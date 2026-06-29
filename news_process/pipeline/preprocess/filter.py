"""news_process.pipeline.preprocess.filter — DataFrame 初步过滤层.

Phase 4b 从 ``runner.py`` 提取。包含:
- ``_clean_and_filter_dataframe`` — 8 步过滤(地域/类型/黑名单/缺失/广告/银行词/Schema/媒体名称清理)
- ``_ad_keyword_hit_counts`` — 广告过滤词级命中计数 (data appendix 排除统计素材)

依赖:
    filter.py ← _constants.py
    filter.py ← load.py (BANK_KW_AUTOMATON, _ac_contains_any)
"""

from __future__ import annotations

import os
import re

import numpy as np
import pandas as pd

from news_process.core.logging import pct4
from news_process.pipeline.preprocess._constants import (
    AD_KEYWORD_PATTERNS,
    AD_KEYWORD_PATTERNS_TITLE,
    AD_PATTERN,
    AD_PATTERN_TITLE,
    KEY_COLUMNS,
    MEDIA_NAME_OVERRIDES,
    MEDIA_NAMES_TO_EXCLUDE,
    MEDIA_TYPES_INCLUDE_SET,
    REGION_PATTERN,
    logger,
)
from news_process.pipeline.preprocess.load import (
    BANK_KW_AUTOMATON,
    _ac_contains_any,
)

# 进程级守卫: 本模块是 stage 00 预处理 runner 在 ProcessPoolExecutor 中按文件
# 并行调用的 worker 级过滤层 (无独立 main()/run_stage(), 写入共享
# logs/00_preprocessing.log)。依手册 §0.6 (called-by-runner helper): 不重复
# 打 runner 入口的全量 ENV/CONFIG (那由 load.py::_log_worker_banner_once 负责),
# 仅在被调函数首次执行时补一个**过滤方法论子步骤 banner** (load.py 的 banner
# 只覆盖长度过滤的测量可靠性引文, 未覆盖本层的"关键词保留=语料样本选择"与
# "广告词排除=样本选择规则"的学术依据)。用 ``_FILTER_BANNER_EMITTED`` 保证每
# worker 仅打一次 (避免逐文件刷屏)。纯日志, 不改任何产物 (golden-safe)。
_FILTER_BANNER_EMITTED = False


def _log_filter_methodology_once() -> None:
    """每 worker 首次过滤时打印一次"过滤方法论"子步骤 banner (引文逐字取自注册表).

    本层两条核心过滤规则均是**语料样本选择规则** (sample-selection rules),
    写论文 data appendix 时须披露其学术依据:
      · 银行关键词 (Aho-Corasick) 保留过滤 — 词典/关键词法构建主题相关语料,
        是金融文本分析的标准做法 (Loughran & McDonald 词典范式)。
      · 广告关键词排除过滤 — 把付费公告/广告版面剔出语料, 同属样本选择规则,
        其排除与监管事件强度相关, 须在附录如实披露 (词级命中计数见
        ``_ad_keyword_hit_counts``)。
    纯日志, 失败绝不阻断 worker 处理 (golden-safe)。
    """
    global _FILTER_BANNER_EMITTED
    if _FILTER_BANNER_EMITTED:
        return
    _FILTER_BANNER_EMITTED = True
    try:
        logger.info("  🧭 子步骤: stage 00 预处理 · DataFrame 8 步初步过滤 (filter.py)")
        logger.info(f"     · 模块: {os.path.abspath(__file__)} | PID={os.getpid()}")
        # ⚙ 本层过滤配置 (来源 _constants.py; 由 config preprocessing.yaml 驱动)
        _region_on = "启用" if REGION_PATTERN is not None else "未启用"
        _ad_on = "启用" if AD_PATTERN is not None else "未启用"
        _bank_kw_n = len(BANK_KW_AUTOMATON) if BANK_KW_AUTOMATON is not None else 0
        logger.info(
            f"     · ⚙ 配置: 地域过滤={_region_on} | "
            f"保留媒体类型={len(MEDIA_TYPES_INCLUDE_SET):,} 类 | "
            f"媒体黑名单={len(MEDIA_NAMES_TO_EXCLUDE):,} 家 | "
            f"广告过滤={_ad_on} | "
            f"银行关键词 AC 自动机={_bank_kw_n:,} 词 (+繁体/全角括号变体)"
        )
        # 📖 方法论依据 (语料样本选择规则; 逐字取自经核验参考文献注册表)
        logger.info("  📖 方法论依据 (关键词保留=语料样本选择 / 广告词排除=样本选择规则):")
        logger.info(
            "     · Loughran, T., & McDonald, B. (2011). When is a liability not a "
            "liability? Textual analysis, dictionaries, and 10-Ks. The Journal of "
            "Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x"
        )
        logger.info(
            "     · Loughran, T., & McDonald, B. (2016). Textual analysis in "
            "accounting and finance: A survey. Journal of Accounting Research, "
            "54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123"
        )
        logger.info(
            "     · Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based "
            "sentiment analysis in finance: Synthesising the existing literature "
            "and exploring future directions. Intelligent Systems in Accounting, "
            "Finance and Management, 31(1), e1549. "
            "https://doi.org/10.1002/isaf.1549"
        )
        logger.info(
            "       → 词典/关键词法 (Aho-Corasick O(n) 匹配) 是金融文本分析构建"
            "主题相关语料的标准样本选择; 广告版面排除作为附录可披露的样本选择规则。"
            " Todd et al. (2024) 近期综述印证: 词典/关键词法在 2020s 仍是金融文本"
            "语料构建与情感分析的基础层 (与 LLM/嵌入法互补, 而非被取代)。"
        )
    except Exception as e:  # noqa: BLE001  纯日志, 失败绝不阻断 worker 过滤
        logger.warning(f"  filter 方法论 banner 打印失败 (不影响处理): {e}")


def _ad_keyword_hit_counts(removed_values: pd.Series, kw_patterns) -> str:
    """对被广告过滤删除的字段值做 per-keyword 命中计数, 返回日志摘要串.

    仅在被删子集上计数 (淘汰率 ~1-3%, 开销可忽略)。一行可命中多个关键词,
    故词级计数之和 ≥ 被删行数 (计数有重叠, 用于定位主力词而非精确分账)。
    白话: 删完后回头数一数每个词各杀了多少行, 哪个词杀得多一目了然 —
    既是论文 data appendix 排除统计表的素材, 也是"某词过度排除"的预警器。

    Args:
        removed_values: 被删行的字段值 (str Series)。
        kw_patterns: [(关键词, compiled pattern)] 词级 pattern 表。

    Returns:
        str: 形如 '公告=12, 通知=3' 的摘要 (按命中数降序, 零命中词省略)。
    """
    counts = []
    for kw, kw_pat in kw_patterns:
        n = int(removed_values.str.contains(kw_pat, na=False, regex=True).sum())
        if n:
            counts.append((kw, n))
    counts.sort(key=lambda item: (-item[1], item[0]))
    return ', '.join(f'{kw}={n}' for kw, n in counts)


def _clean_and_filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """对单个 DataFrame 执行全部初始过滤操作.

    过滤顺序经过精心设计, 按数据淘汰率从高到低排列,
    确保高淘汰率的过滤先执行, 最大化减少后续步骤的数据量:
      1. 媒体地域过滤 (淘汰率最高, ~60-70%)
      2. 媒体类型过滤 (~5-10%)
      3. 媒体名称黑名单过滤 (排除剪报服务等非原始新闻来源)
      4. 缺失值过滤 (~2-5%)
      5. 广告关键词过滤 (~1-3%; 标题字段高误伤词行尾锚定, fix omni-g-preprocess-05)
      6. 银行关键词保留过滤 (Aho-Corasick, ~30-50%; 自动机含繁体/全角括号变体
         以兼容规范化前的原始文本, fix omni-g-preprocess-07)
      7. Schema 统一 (object → string, 不改变行数)
      8. 媒体名称清理 (去除报纸名称修饰后缀/版面/无效字符, 不改变行数)

    Args:
        df: 从 Excel 文件读取的原始 DataFrame。

    Returns:
        pd.DataFrame: 过滤和标准化后的 DataFrame。
    """
    if df.empty:
        return df

    # 子步骤 banner (每 worker 仅一次): 过滤层方法论引文 + 本层配置
    _log_filter_methodology_once()

    # 本层输入行数 (仅服务于末尾保留率结果判读的局部变量; 不入任何产物)
    _rows_in = len(df)
    # 纯日志局部累加器: [(步骤标签, 该步移除行数, 该步后剩余行数)] — 仅供末尾
    # "逐步淘汰构成" 汇总日志消费, 绝不入任何产物/返回/控制流 (golden-safe)。
    _step_removed = []

    # 1. 媒体地域过滤: 仅保留中国大陆地区的媒体
    if REGION_PATTERN is not None:
        rows_before = len(df)
        region_cleaned = df['国家地区/省份'].astype(str).str.replace(r'\s+', '', regex=True)
        df = df[region_cleaned.str.contains(REGION_PATTERN, na=False, regex=True)]
        logger.info(f"  [1/8 地域过滤] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")
        _step_removed.append(('地域', rows_before - len(df), len(df)))

    # 2. 媒体类型过滤: 仅保留指定类型(如"报纸")
    rows_before = len(df)
    df = df[df['媒体类型(中文)'].isin(MEDIA_TYPES_INCLUDE_SET)]
    logger.info(f"  [2/8 类型过滤] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")
    _step_removed.append(('类型', rows_before - len(df), len(df)))

    # 3. 媒体名称黑名单过滤: 排除剪报服务机构等非原始新闻来源
    if MEDIA_NAMES_TO_EXCLUDE:
        rows_before = len(df)
        df = df[~df['媒体(中文)'].astype(str).isin(MEDIA_NAMES_TO_EXCLUDE)]
        if rows_before - len(df) > 0:
            logger.info(f"  [3/8 媒体名称黑名单] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")
            _step_removed.append(('黑名单', rows_before - len(df), len(df)))

    # 4. 关键字段缺失值过滤(标题、内容、媒体名、日期任一为空则移除)
    rows_before = len(df)
    df = df.dropna(subset=KEY_COLUMNS)
    # R1-R5 audit fix A8 (2026-05-27): 修 R4-A8 finding —— dropna 仅 drop None/NaN,
    # 不 drop literal empty string ''. OCR / Wisers 数据库 NULL → '' 映射时关键
    # 字段保留, 导致 pd.to_datetime 后 NaT silent 进 panel. 此处对每个关键列做
    # ne('') strip 过滤.
    for _col in KEY_COLUMNS:
        if _col in df.columns:
            df = df[df[_col].astype(str).str.strip() != '']
    logger.info(f"  [4/8 缺失值过滤] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")
    _step_removed.append(('缺失', rows_before - len(df), len(df)))

    # 5. 广告关键词过滤(检查标题、版面、栏名三个字段)
    # fix(omni-g-preprocess-05, 2026-06-11): 标题字段改用 AD_PATTERN_TITLE —
    # 高误伤词 (ad_keywords_title_anchored, 2026-06-13 三批扩 6→27 词) 对标题
    # 要求行尾锚定, 不再把 '央行公告下调存准率' / '上市银行三季度报告显示…' /
    # 'XX银行收到行政处罚事先告知书 拟被罚没…' 等监管/财经新闻整篇误删;
    # 版面/栏名仍用无锚定 AD_PATTERN (付费公告版面全量排除, 行为不变)。
    # 数据附录披露: 标题命中广告关键词 (高误伤词须行尾锚定) 或 版面/栏名含
    # 任一广告关键词的记录被排除出语料 — 该排除与监管事件强度相关, 属语料
    # 构建的样本选择规则, 写论文 data appendix 时须披露; 词级命中计数随
    # 日志输出 (见 _ad_keyword_hit_counts), 即附录排除统计表的直接素材。
    for field_name, col_name, _pattern, _kw_patterns in [
        ('标题', '标题', AD_PATTERN_TITLE, AD_KEYWORD_PATTERNS_TITLE),
        ('版面', '版面', AD_PATTERN, AD_KEYWORD_PATTERNS),
        ('栏名', '栏名', AD_PATTERN, AD_KEYWORD_PATTERNS),
    ]:
        if _pattern is None:
            continue
        rows_before = len(df)
        col_values = df[col_name].astype(str)
        hit_mask = col_values.str.contains(_pattern, na=False, regex=True)
        if hit_mask.any():
            kw_detail = _ad_keyword_hit_counts(col_values[hit_mask], _kw_patterns)
            df = df[~hit_mask]
            logger.info(
                f"  [5/8 广告过滤-{field_name}] "
                f"移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,} "
                f"(词级命中, 可重叠: {kw_detail})"
            )
            _step_removed.append((f'广告·{field_name}', rows_before - len(df), len(df)))

    # 6. 银行关键词保留过滤(Aho-Corasick O(n) 复杂度)
    # 只保留内容中提及至少一个银行关键词的新闻
    if BANK_KW_AUTOMATON is not None:
        rows_before = len(df)
        content_values = df['内容'].astype(str).values
        # 向量化版本: 使用 numpy 布尔数组避免 Python 级别循环开销
        mask = np.fromiter(
            (_ac_contains_any(t, BANK_KW_AUTOMATON) for t in content_values),
            dtype=bool,
            count=len(content_values)
        )
        df = df[mask]
        logger.info(f"  [6/8 银行关键词过滤] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")
        _step_removed.append(('银行词', rows_before - len(df), len(df)))

    # 7. Schema 统一: object 列 → string, 确保后续 Parquet 序列化安全
    # 📊 schema-boundary breadcrumb (io_provenance; 纯日志, try/except 守卫, 结果即弃,
    # golden-safe): 在归一循环 *之前* 数一下有多少 object-dtype 列将被强制
    # fillna('').astype(str), 作为 Parquet 序列化边界的可复现性面包屑。
    # 白话: 记录这一步把几列"杂类型 (object)"统一成了字符串, 方便复现时核对 schema 边界。
    try:
        _n_obj_cols = len([c for c in df.columns if df[c].dtype == 'object'])
        if _n_obj_cols:
            logger.info(
                f"  [7/8 Schema 统一] object→string 归一 {_n_obj_cols:,} 列 "
                f"(Parquet 序列化安全边界, 不改行数)"
            )
    except Exception as e:  # noqa: BLE001  纯日志, 失败绝不阻断过滤
        logger.warning(f"  Schema 统一统计打印失败 (不影响处理): {e}")
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('').astype(str)

    # 8. 媒体名称清理: 去除报纸名称中的各类修饰后缀、附加版面及无效字符
    # 白话: 把 "人民日报·海外版 since 2008" 这类带修饰的报名逐步裁剪回母报名
    # ("人民日报"), 让同一家报纸在数据里只剩一个统一名字; 裁过头变成空串时
    # 回退到只去掉换行符的原名, 不会把媒体名洗丢。
    if '媒体(中文)' in df.columns:
        orig_media = df['媒体(中文)'].astype(str)
        # (0) 基础预清理: 剔除换行/制表符等不可见格式字符, 作为最安全的基底名称
        s_base = orig_media.str.replace(r'[\r\n\t]+', ' ', regex=True).str.strip()
        s = s_base.copy()

        # (1) 括号内内容清除
        s = s.str.replace(r'[\(（\[【].*?[\)）\]】]', '', regex=True)
        # (2) 数字报及固定短语清除
        s = s.str.replace('数字报', '', regex=False)
        # (3) 日期及 since 清除
        s = s.str.replace(r'\s*-\s*since\s+.*', '', flags=re.IGNORECASE, regex=True)
        s = s.str.replace(r'\s*-\s*\d{8}\s*-\s*\d{8}.*', '', regex=True)
        s = s.str.replace(r'\s+\d{8}-\d{8}.*', '', regex=True)
        # (4) 点号及中圆点后缀清除
        s = s.str.replace(r'^(.*?[\u4e00-\u9fa5][^·\.]*)[·\.].*', r'\1', regex=True)
        # (5) 特定地域及版面清除
        s = s.str.replace(
            r'\s*-?\s*(英文版|中文版|东莞版|加东版|加西版|美西版|粤东版|台湾版|网络版|电子版|手机版|华南版|华东版|西北版|纽约免费报|东九龙|西九龙).*',
            '', regex=True
        )
        # (6) 删除末尾纯英文字符串
        s = s.str.replace(r'(.*[\u4e00-\u9fa5].*?)\s+[a-zA-Z\s]+$', r'\1', regex=True)

        cleaned_media = s.str.strip()

        # 防御性回退: 如果清洗后变为空(如纯括号组成), 则保留预清理后的原名称
        s_final = cleaned_media.where(cleaned_media != '', s_base)

        # (7) 重点特例覆盖
        for k, v in MEDIA_NAME_OVERRIDES.items():
            s_final = s_final.where(s_base != k, v)

        df['媒体(中文)'] = s_final

        # 📊 媒体名称规范化产出统计 (outlet-identity canonicalization yield;
        # result_distribution; 纯日志, try/except 守卫, 结果即弃, golden-safe)。
        # 媒体名是下游媒体多样性 (HHI) 与 outlet 固定效应的实体键 —— 同一报纸若残留
        # 多个变体名会虚增 outlet 计数、稀释固定效应; 故规范化命中率是论文 data
        # appendix 的实体清洗 (outlet-identity normalization rate) provenance 统计。
        # 白话: 这一步把 "人民日报·海外版"/"人民日报 since 2008" 收敛回 "人民日报",
        # 这里数一数改写了多少行、把多少个不同报名合并掉、几条特例规则真的命中。
        try:
            if len(df) > 0:
                _n_changed = int((s_final != orig_media).sum())
                _uniq_before = int(orig_media.nunique())
                _uniq_after = int(s_final.nunique())
                _n_override_fired = sum(
                    1 for _k in MEDIA_NAME_OVERRIDES if bool((s_base == _k).any())
                )
                logger.info(
                    f"  📊 [8/8 媒体名称规范化] 改写 {_n_changed:,} 行 "
                    f"({pct4(_n_changed / len(df))}) | "
                    f"去重后唯一报名 {_uniq_before:,} → {_uniq_after:,} 家 | "
                    f"特例覆盖规则命中 {_n_override_fired:,}/{len(MEDIA_NAME_OVERRIDES):,} 条"
                )
        except Exception as e:  # noqa: BLE001  纯日志, 失败绝不阻断过滤返回
            logger.warning(f"  媒体名称规范化统计打印失败 (不影响处理): {e}")

    # 📊 结果判读 (本文件块整体保留率; pct4 四位有效数字, 纯日志):
    # 8 步过滤是高淘汰链 (地域 ~60-70% + 银行词 ~30-50% 为主力), 单文件整体保留
    # 率通常落在 5-25%。给一个粗判读门槛, 偏离时提示语料/词典/媒体口径异常。
    try:
        _rows_out = len(df)
        if _rows_in > 0:
            _keep = _rows_out / _rows_in
            if _rows_out == 0:
                _verdict = "❌ 零存留 (本文件被全删, 检查是否地域/类型口径过严或源 schema 异常)"
            elif _keep < 0.01:
                _verdict = "⚠ 极低保留 (临界, 多为主题外/外地媒体为主的源文件, 属预期)"
            elif _keep > 0.60:
                _verdict = "⚠ 异常高保留 (临界, 检查地域/银行词过滤是否未生效)"
            else:
                _verdict = "✅ 保留率落在预期高淘汰链区间"
            logger.info(
                f"  📊 [本文件块过滤汇总] {_rows_in:,} → {_rows_out:,} 行, "
                f"整体保留率={pct4(_keep)} — {_verdict}"
            )
            # 逐步淘汰构成 (各步移除占原始行数; 主力通常=地域 ~60-70% + 银行词
            # ~30-50%, 其余为卫生型过滤), 供论文 data appendix 排除瀑布表素材。
            if _step_removed:
                _breakdown = ', '.join(
                    f"{lbl} -{rmv:,} ({pct4(rmv / _rows_in)})"
                    for lbl, rmv, _rem in _step_removed
                )
                logger.info(
                    f"  📊 [逐步淘汰构成 占原始 {_rows_in:,} 行] {_breakdown}"
                )
    except Exception as e:  # noqa: BLE001  纯日志, 失败绝不阻断过滤返回
        logger.warning(f"  过滤汇总判读打印失败 (不影响处理): {e}")

    return df


__all__ = ['_clean_and_filter_dataframe']
