"""scripts/data_acquisition/banking_outcome_dry_run.py
─────────────────────────────────────────────────────────────────────────────
银保监会 + Wind + 银行年报 PDF Bank Outcome Dry-Run 抓取脚本.

V4 audit DC2 deliverable: 验证 Z-score / NPL formation / RWA ratio 三件套
在 500 行 × 18 年 panel 的实际可得率, 决定 fallback path α/β/γ.

Usage
-----
    python scripts/data_acquisition/banking_outcome_dry_run.py \\
        --year-quarter 2024-Q1 \\
        --output data/dry_run/2024Q1_outcome.parquet \\
        --wind-key $WIND_API_KEY

模式
----
- dry_run (默认): 仅 2024-Q1 一季度, 验证 acquisition pipeline 可行性
- full: 2007-Q1 ~ 2024-Q4 全样本 (M1-M2 deliverable)

输出
----
data/dry_run/<period>_outcome.parquet 含 schema:
    target_bank: str       # 银行中文名 (与 panel 主键一致)
    year: int              # 年份
    quarter: int           # 季度 (1-4)
    roa: float             # ROA, 单位 %
    capital_adequacy_ratio: float   # CAR, 单位 %
    total_assets: float    # 总资产, 单位亿元
    rwa: float             # 风险加权资产, 单位亿元
    npl_balance: float     # 不良贷款余额, 单位亿元
    npl_ratio: float       # 不良率, 单位 %
    total_loans: float     # 贷款总额, 单位亿元
    loan_writeoffs: float  # 核销额, 单位亿元 (常 missing)
    loan_loss_provision: float  # 贷款损失准备, 单位亿元
    data_source: str       # 'wind' | 'cbirc' | 'annual_report_pdf'
    acquisition_timestamp: str  # ISO 8601 UTC

数据源优先级 (per record)
-------------------------
1. Wind 银行库 (覆盖率最高, ~80% 非上市行)
2. 银保监会季报 (官方权威, 但 2018 后部分非公开)
3. 银行年报 PDF (兜底, 需 tabula-py OCR)

依赖
----
- WindPy (Wind API, 需用户提供 token)
- requests + BeautifulSoup (银保监会爬虫)
- tabula-py + Java (PDF 表格提取)
- pandas + pyarrow

注意
----
本脚本仅 *scaffolding*; 实际 Wind API 调用 + 银保监会反爬应对需用户填入
真实凭证 + 部分代码 (见 TODO 标记).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import os
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# ─────────────────────────────────────────────────────────────────────────────
# Outcome schema (与 paper_spec.yaml outcome 字段对齐)
# ─────────────────────────────────────────────────────────────────────────────
OUTCOME_SCHEMA = {
    'target_bank': 'string',
    'year': 'int32',
    'quarter': 'int32',
    'roa': 'float32',
    'capital_adequacy_ratio': 'float32',
    'total_assets': 'float64',
    'rwa': 'float64',
    'npl_balance': 'float64',
    'npl_ratio': 'float32',
    'total_loans': 'float64',
    'loan_writeoffs': 'float64',
    'loan_loss_provision': 'float64',
    'data_source': 'string',
    'acquisition_timestamp': 'string',
}

# 500 行 panel 银行清单 (frozen at v3.6.0)
# 实际位置: news_process/config/bank_list.yaml (M1 待生成)
# 这里仅 dry-run 用前 20 家作 demonstration
SAMPLE_BANK_LIST = [
    # 国有 6 大
    '中国工商银行', '中国农业银行', '中国银行', '中国建设银行', '交通银行', '中国邮政储蓄银行',
    # 政策性 3 家
    '国家开发银行', '中国进出口银行', '中国农业发展银行',
    # 系统重要性股份制
    '招商银行', '兴业银行', '浦发银行', '中信银行', '民生银行',
    # 其他股份制
    '光大银行', '华夏银行', '平安银行',
    # 上市城商行 (代表)
    '北京银行', '上海银行', '江苏银行',
]


# ─────────────────────────────────────────────────────────────────────────────
# 数据源 acquisition functions (TODO: 用户填入真实凭证 + API 调用)
# ─────────────────────────────────────────────────────────────────────────────

# v3.7.0 V3 closure B: Wind / CBIRC / PDF 真实实施.
# Wind 字段 code mapping (per Wind 官方 fields documentation 2024).
# 实际跑前用户须先 register Wind license + 启动 WindPy session.
_WIND_FIELD_MAP = {
    # outcome schema field : Wind field code
    'roa': 'roa_avg2',                # 平均总资产回报率 (per Wind)
    'capital_adequacy_ratio': 'capad',  # 资本充足率
    'total_assets': 'wgsd_assets',      # 总资产
    'rwa': 'rwa',                       # 风险加权资产 (银行专用字段)
    'npl_balance': 'npl_amt',           # 不良贷款余额
    'npl_ratio': 'npl_ratio',           # 不良贷款率
    'total_loans': 'loan',               # 贷款总额
    'loan_writeoffs': 'writeoff',       # 贷款核销 (常 missing)
    'loan_loss_provision': 'provision', # 贷款损失准备
}

# Bank name → Wind code mapping (key 列与 bank_list.yaml::target_bank 对齐)
# 用户运行前可扩展到 500 行 (与 bank_list.yaml::banks::wind_code 同步).
_BANK_NAME_TO_WIND_CODE = {
    '中国工商银行': '601398.SH',
    '中国农业银行': '601288.SH',
    '中国银行': '601988.SH',
    '中国建设银行': '601939.SH',
    '交通银行': '601328.SH',
    '中国邮政储蓄银行': '601658.SH',
    '招商银行': '600036.SH',
    '兴业银行': '601166.SH',
    '浦发银行': '600000.SH',
    '中信银行': '601998.SH',
    '民生银行': '600016.SH',
    '中国光大银行': '601818.SH',
    '华夏银行': '600015.SH',
    '平安银行': '000001.SZ',
    '浙商银行': '601916.SH',
    '北京银行': '601169.SH',
    '上海银行': '601229.SH',
    '江苏银行': '600919.SH',
    '南京银行': '601009.SH',
    '宁波银行': '002142.SZ',
    # ... 其余 ~460 行待用户从 bank_list.yaml 同步
}


def fetch_from_wind(
    bank_name: str,
    year: int,
    quarter: int,
    wind_key: Optional[str] = None,
) -> Optional[dict]:
    """v3.7.0 V3 closure B 实施: 从 Wind 银行库抓取单家银行单季度数据.

    使用 WindPy SDK 的 ``w.wsd(code, fields, start_date, end_date)`` 批量字段调用.
    所有字段映射见 ``_WIND_FIELD_MAP``.

    依赖:
        - pip install WindPy (需 Wind 客户端在本机已登录)
        - 环境变量 WIND_API_KEY (或显式传 wind_key 参数; 启动 Wind 客户端会
          自动 OAuth, key 仅用于诊断 / log audit)

    错误处理:
        - WindPy 未安装 → return None (fallback to CBIRC)
        - bank_code 缺失 → return None
        - Wind 调用 ErrorCode != 0 → return None + logger.warning
        - 字段全 NaN → return None

    返回:
        dict OUTCOME_SCHEMA 一条 record, 或 None (Wind 抓取失败).
    """
    if wind_key is None:
        wind_key = os.environ.get('WIND_API_KEY')
    if not wind_key:
        logger.debug(f"WIND_API_KEY 未配置, skip Wind for {bank_name}")
        return None

    bank_code = _BANK_NAME_TO_WIND_CODE.get(bank_name)
    if not bank_code:
        logger.debug(f"Wind code 未映射, skip {bank_name} (扩展 _BANK_NAME_TO_WIND_CODE)")
        return None

    try:
        from WindPy import w  # type: ignore[import-not-found]
    except ImportError:
        logger.warning(
            "WindPy 未安装. 安装: pip install WindPy (需 Wind 客户端 license). "
            "fallback to CBIRC/PDF for %s.", bank_name
        )
        return None

    # 启动 WindPy session (幂等; 已 start 则即时返回)
    start_resp = w.start()
    if start_resp.ErrorCode != 0:
        logger.warning(
            "WindPy w.start() failed (ErrorCode=%s): %s. "
            "确认 Wind 客户端登录 + license 有效.",
            start_resp.ErrorCode, start_resp.Data,
        )
        return None

    # 季度末日期 (Q1=03-31, Q2=06-30, Q3=09-30, Q4=12-31)
    quarter_end_dates = {1: '03-31', 2: '06-30', 3: '09-30', 4: '12-31'}
    end_date = f"{year}-{quarter_end_dates[quarter]}"

    fields_csv = ','.join(_WIND_FIELD_MAP.values())
    # w.wsd 调单点季度数据 (start=end=end_date)
    resp = w.wsd(bank_code, fields_csv, end_date, end_date, "")
    if resp.ErrorCode != 0:
        logger.warning(
            "Wind wsd failed for %s %s-Q%d (ErrorCode=%s): %s",
            bank_name, year, quarter, resp.ErrorCode, resp.Data,
        )
        return None
    if not resp.Data or all(v is None for v in resp.Data[0]):
        logger.debug(f"Wind 返回空数据 {bank_name} {year}-Q{quarter}")
        return None

    # 字段映射: Wind fields 顺序 = _WIND_FIELD_MAP.values() 顺序
    field_names = list(_WIND_FIELD_MAP.keys())
    record = {
        'target_bank': bank_name,
        'year': year,
        'quarter': quarter,
        'data_source': 'wind',
        'acquisition_timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    for i, field in enumerate(field_names):
        # resp.Data 是 list[list], 每个 inner list 是一个 field 的时间序列;
        # 单点查询时 inner list 长度 = 1.
        raw_val = resp.Data[i][0] if resp.Data[i] else None
        record[field] = float(raw_val) if raw_val is not None else None
    return record


def fetch_from_cbirc(bank_name: str, year: int, quarter: int) -> Optional[dict]:
    """v3.7.0 V3 closure B 实施: 银保监会公开季报抓取 (Wind fallback).

    数据源策略 (按 2018-04 银保监合并后 URL 重整):
        Primary: 银保监会金融许可证机构信息 + 季度监管指标公开数据
            https://www.cbirc.gov.cn/cn/view/pages/ItemList.html?itemPyCode=tjsj
            (实际表格通过 itemPyCode=tjsj 进入, 内部 IDV 链接每年异动, 需爬虫
            handle 多级跳转)
        Fallback: 各家上市行 H 股 / A 股自主披露 (季度财务报告 PDF)

    反爬策略 (per CBIRC 公开数据爬取约定):
        - 请求间隔 ≥ 2 秒 (避免 IP 封禁)
        - User-Agent rotation (5-10 个常见浏览器 UA)
        - 维持 session cookies (中途丢 cookies 触发反爬验证码)
        - 必要时人工 fallback (验证码 / Captcha 出现时)

    返回:
        dict OUTCOME_SCHEMA 一条 record, 或 None (CBIRC 无可得数据).

    Note: 由于 CBIRC 单家银行季度数据公开度极低 (大多为行业 aggregates),
    此 fallback 主要服务上市行 (有自主披露); 非上市行需第 3 级 fallback 到
    年报 PDF.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        logger.warning(
            "CBIRC fallback 需要 requests + beautifulsoup4. "
            "pip install requests beautifulsoup4. Skip %s.", bank_name
        )
        return None

    # User-Agent rotation pool
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 '
        '(KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    import random
    import time
    headers = {'User-Agent': random.choice(user_agents)}

    # 主入口 URL (实际数据通过此页跳转到具体季度 IDV)
    cbirc_base = 'https://www.cbirc.gov.cn'
    item_list_url = (
        f'{cbirc_base}/cn/view/pages/ItemList.html?itemPyCode=tjsj'
    )

    try:
        session = requests.Session()
        session.headers.update(headers)
        # 反爬间隔
        time.sleep(2.0 + random.random())
        resp = session.get(item_list_url, timeout=15)
        if resp.status_code != 200:
            logger.warning(
                "CBIRC main list fetch HTTP %s for %s", resp.status_code, bank_name,
            )
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')

        # CBIRC 实际页面结构: 通过 JavaScript 异步加载列表, 静态 HTML 拿不到
        # 完整 link list (此处仅作 scaffold 演示; 用户须用 selenium /
        # playwright 跑动态渲染或直接调 CBIRC 内部 IDV REST endpoint).
        # placeholder: 返回 None, 强制 fallback 到年报 PDF.
        logger.debug(
            "CBIRC 静态 HTML 解析无法获取 %s %s-Q%d 数据 "
            "(动态渲染需 selenium fallback 或内部 IDV API). 转 PDF fallback.",
            bank_name, year, quarter,
        )
        return None

    except Exception as exc:
        logger.warning("CBIRC fetch failed for %s: %r", bank_name, exc)
        return None


def fetch_from_annual_report_pdf(
    bank_name: str,
    year: int,
    pdf_dir: Path = Path('data/annual_reports'),
) -> Optional[dict]:
    """v3.7.0 V3 closure B 实施: 银行年报 PDF 提取年度数据 (CBIRC fallback).

    PDF 来源 (按可得性优先级):
        1. 巨潮资讯网 (cninfo.com.cn): A 股全部上市行年报 PDF
        2. 港交所披露易 (hkexnews.hk): H 股上市行 PDF
        3. 各行官网投资者关系页: 非上市但自愿披露的城商 / 农商
        4. 银保监会年度公开报告: 兜底, 仅含 aggregate 数据

    提取策略:
        - **tabula-py 表格提取** (Java 依赖): 主资产负债表 + 利润表
        - **pdfplumber** (纯 Python fallback): 表格 extract_tables
        - **关键词 regex**: 提取 "资本充足率", "不良贷款率", "总资产" 等附近的数值
        - **per-bank parser**: 各行 PDF 表格 schema 差异巨大, 需要 per-bank
          ``_PARSERS[bank_name]`` 字典 dispatch (M1 用户实施时按需扩展)

    PDF 路径约定:
        data/annual_reports/<bank_name>/<year>.pdf
        (用户须先批量下载, 文件名严格年份格式)

    返回:
        dict OUTCOME_SCHEMA 一条 record (年度, quarter=4), 或 None.
    """
    pdf_path = pdf_dir / bank_name / f'{year}.pdf'
    if not pdf_path.exists():
        logger.debug(f"PDF 年报不存在: {pdf_path}; skip")
        return None

    # 优先 tabula-py (Java + JVM, 表格提取最准)
    tables: Optional[list] = None
    try:
        import tabula  # type: ignore[import-untyped]
        tables = tabula.read_pdf(
            str(pdf_path),
            pages='all',
            multiple_tables=True,
            lattice=True,  # 主资产负债表通常有 visible borders
            silent=True,
        )
    except ImportError:
        logger.debug("tabula-py 不可用, 尝试 pdfplumber fallback")
        try:
            import pdfplumber  # type: ignore[import-untyped]
            tables = []
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_tables()
                    if extracted:
                        for t in extracted:
                            if len(t) > 1:
                                # 转换为 DataFrame
                                import pandas as pd_local
                                df = pd_local.DataFrame(t[1:], columns=t[0])
                                tables.append(df)
        except ImportError:
            logger.warning(
                "PDF 提取需要 tabula-py 或 pdfplumber. "
                "pip install tabula-py pdfplumber. Skip %s/%s.pdf.",
                bank_name, year,
            )
            return None
        except Exception as exc:
            logger.warning(f"pdfplumber 读取失败 {pdf_path}: {exc!r}")
            return None
    except Exception as exc:
        logger.warning(f"tabula 读取失败 {pdf_path}: {exc!r}")
        return None

    if not tables:
        logger.debug(f"PDF {pdf_path} 未提取到表格")
        return None

    # 字段提取 via regex on table cells
    # 各行年报表格关键词约定 (per 上市行通用 IFRS 报表):
    field_keywords = {
        'roa': ['平均总资产回报率', '总资产收益率', 'ROA'],
        'capital_adequacy_ratio': ['资本充足率', '资本充足率（核心）'],
        'total_assets': ['资产总计', '总资产'],
        'rwa': ['风险加权资产', '风险加权资产合计'],
        'npl_balance': ['不良贷款', '不良贷款余额'],
        'npl_ratio': ['不良贷款率'],
        'total_loans': ['贷款总额', '客户贷款'],
        'loan_loss_provision': ['贷款损失准备', '贷款减值准备'],
    }
    extracted_values = {}
    for field, keywords in field_keywords.items():
        for table in tables:
            try:
                # tabula DataFrame 或 pdfplumber DataFrame
                table_str = table.to_string() if hasattr(table, 'to_string') else str(table)
                for kw in keywords:
                    if kw in table_str:
                        # 提取 keyword 之后第一个数值 (可能含千分位逗号)
                        import re
                        # 匹配 "关键词...12,345.67" 或 "关键词...12345.67%"
                        pattern = rf'{kw}[^0-9]*([\d,]+\.?\d*)\s*%?'
                        match = re.search(pattern, table_str)
                        if match:
                            try:
                                val = float(match.group(1).replace(',', ''))
                                extracted_values[field] = val
                                break
                            except ValueError:
                                continue
                if field in extracted_values:
                    break
            except Exception:
                continue

    if not extracted_values:
        logger.debug(f"PDF {pdf_path} 未提取到任何 outcome 字段")
        return None

    record = {
        'target_bank': bank_name,
        'year': year,
        'quarter': 4,                       # 年报数据归 Q4
        'data_source': 'annual_report_pdf',
        'acquisition_timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    record.update(extracted_values)
    # 补 None 给 schema 中未提取到的字段
    for col in OUTCOME_SCHEMA:
        record.setdefault(col, None)
    return record


# ─────────────────────────────────────────────────────────────────────────────
# Orchestration
# ─────────────────────────────────────────────────────────────────────────────

def acquire_one_bank_period(
    bank_name: str,
    year: int,
    quarter: int,
    wind_key: Optional[str] = None,
) -> Optional[dict]:
    """级联尝试: Wind → 银保监会 → 年报 PDF.

    返回首个成功的 record, 全失败返回 None.
    """
    # Wind first (覆盖最高)
    rec = fetch_from_wind(bank_name, year, quarter, wind_key)
    if rec is not None:
        return rec

    # 银保监会 fallback
    rec = fetch_from_cbirc(bank_name, year, quarter)
    if rec is not None:
        return rec

    # 年报 PDF 兜底 (仅 Q4 才有年度数据)
    if quarter == 4:
        rec = fetch_from_annual_report_pdf(bank_name, year)
        if rec is not None:
            return rec

    return None


def dry_run(
    year_quarter: str,
    bank_list: list[str] = SAMPLE_BANK_LIST,
    output_path: Optional[Path] = None,
    wind_key: Optional[str] = None,
) -> pd.DataFrame:
    """dry-run 主入口: 单季度 × 全 bank list 实际可得率测试.

    Args:
        year_quarter: '2024-Q1' 格式
        bank_list: 银行清单 (默认 SAMPLE 20 家; 实际 500 行)
        output_path: 输出 parquet 路径
        wind_key: Wind API key (None 时从 env WIND_API_KEY 读)

    Returns:
        pd.DataFrame 含 OUTCOME_SCHEMA 字段, 缺失行 data_source='missing'
    """
    year, q_str = year_quarter.split('-')
    year = int(year)
    quarter = int(q_str.replace('Q', ''))

    records = []
    for bank in bank_list:
        rec = acquire_one_bank_period(bank, year, quarter, wind_key)
        if rec is None:
            # missing placeholder
            rec = {col: None for col in OUTCOME_SCHEMA}
            rec['target_bank'] = bank
            rec['year'] = year
            rec['quarter'] = quarter
            rec['data_source'] = 'missing'
            rec['acquisition_timestamp'] = dt.datetime.now(dt.timezone.utc).isoformat()
        records.append(rec)
        logger.info(f"  {bank} {year}-Q{quarter}: {rec['data_source']}")

    df = pd.DataFrame(records)
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, engine='pyarrow')
        logger.info(f"Dry-run output: {output_path} ({len(df)} rows)")

    return df


def summarize_acquisition(df: pd.DataFrame) -> dict:
    """计算 dry-run 关键指标供 fallback 决策."""
    n_total = len(df)
    n_missing = (df['data_source'] == 'missing').sum()
    by_source = df['data_source'].value_counts().to_dict()

    # outcome 字段可得率 (非 NaN 占比)
    outcome_cols = ['roa', 'capital_adequacy_ratio', 'rwa', 'npl_balance',
                    'total_loans', 'loan_writeoffs', 'loan_loss_provision']
    availability = {
        col: float(df[col].notna().mean()) for col in outcome_cols if col in df.columns
    }

    return {
        'n_total_bank_period': n_total,
        'n_missing': int(n_missing),
        'overall_acquisition_rate': float((n_total - n_missing) / n_total),
        'by_source': by_source,
        'per_outcome_availability': availability,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Banking outcome dry-run acquisition')
    parser.add_argument('--year-quarter', default='2024-Q1',
                        help='YYYY-Qn format, default 2024-Q1')
    parser.add_argument('--output', default='data/dry_run/2024Q1_outcome.parquet',
                        type=Path)
    parser.add_argument('--wind-key', default=None,
                        help='Wind API key (or set WIND_API_KEY env var)')
    parser.add_argument('--full-bank-list', action='store_true',
                        help='Use full 500 bank list (M1+ only)')
    args = parser.parse_args()

    bank_list = SAMPLE_BANK_LIST
    if args.full_bank_list:
        # TODO: 加载 news_process/config/bank_list.yaml (M1 deliverable)
        logger.warning("full bank list 未实施, fallback to sample 20 banks")

    df = dry_run(
        year_quarter=args.year_quarter,
        bank_list=bank_list,
        output_path=args.output,
        wind_key=args.wind_key,
    )

    summary = summarize_acquisition(df)
    print("\n" + "=" * 60)
    print("DRY-RUN SUMMARY")
    print("=" * 60)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
