"""WP5 — 税调企业双替代权源构建 + 三权互验 (COMPANY_TAX_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-08 v7).

三层产物 (均不入库, 默认落 company_tax_bank/data/):
  ① 双替代权长表 _company_tax_bank_altweights_{branch_city,branch_county}.parquet
     (统一 schema company/bank/year/w, 无稳健臂 — ROBUST_ARM_COLS 两 scheme 均 [])
  ② 双替代权真实面板 company_tax_bank_{scheme}w_panel.{dta,parquet} ×2
     (与媒体共现权主面板并成三权, 引擎/列名/标签同源; 县权面板另 +county_key_ok int8)
  ③ 三权互验报告 _company_tax_bank_weight_validation.md (T-D7 全件套 + 顶刊披露包 +
     未映射审计附录; 禁时间戳) + codebook「双替代权面板章」幂等 upsert (T-D19⑦)

权源: config/银行业金融机构基本信息表.dta 单一 dta, 拆城市/县域两层级 (T-D5)。
银行名 canonical 化 = BankCanon (DV2 判定序零改动, 本模块本地裁剪版, §8-N5)。
DV2_CONSTANTS 由 WP0 序列化入 registry `dv2_constants` 区段 (双向锁, T-D8)。

T-D9 裁剪口径 (相对 listed 03 的 DV2_CONSTANTS):
  - 保留 8 键 (值逐字节照抄 listed): unnameable / overseas_words / foreign_suffixes /
    generic_heads / affiliate_tail / head_exempt_note / city_overseas / city_placeholder
    (BankCanon 与分支权消费, listed 03:292 最小集断言勿裁);
  - 删除 custodian_words / custodian_dashes / sanchan_words (消费点在 shareholder
    builder [listed 03:729-739], 税调裁掉 loan+shareholder+董监高权源后无消费者;
    裁剪同时使税调 registry 哈希与 listed 永不混淆);
  - 新增 city_placeholder_branch_side (T-D5c 网点侧 CityName 占位回退值集, T-P0-2 实测全集)。

⚠ 铁律: DV2_CONSTANTS 字面量禁改 (registry sha 已一次定终, 改动即 sha 换代须整链重跑,
gate 哈希锚兜底)。约束: 顶层仅轻 import — pandas/numpy/yaml/pyreadstat/scipy 等重依赖
全部后置到函数体内 (01 经 importlib 读本模块常量, 不得被拖入重依赖)。
独立派生数据脚本, 不注册 DAG; $0 纯 pandas, 无 LLM/网络/API。
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # 仅类型标注; 运行时重依赖全部函数内延迟 import (WP5-stub 轻顶层约束)
    import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"   # 上游输入 (只读, 主管道产物)
OUT_DATA = HERE / "data"             # 本流水线产物 (双权长表/面板/互验报告, 不入库)
CONFIG = REPO / "config"
TRACKS = ("full", "ctx", "ss")
# 面板年窗 = 税调企业数据可得域 (2011–2020; 与 02 同源锚, 见 02 ABS/PANEL 分叉铁律)。argparse 默认锚此。
# ⚠ 03 第一层脏年域 = 网点审批/退出日期合理域 [1990, 2035] (可早于 2007, 与面板窗**无关**, 勿混改);
# 第二层 outwin 才用本窗裁网点存续年格。
PANEL_YEAR_MIN, PANEL_YEAR_MAX = 2011, 2020

logger = logging.getLogger("03_build_company_tax_bank_weight_validation")
if not logger.handlers:  # console 兜底 (被测试/importlib 导入时); main() 实跑时由 setup_logging 接管
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[tax_w8] %(levelname)s %(message)s"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)


# ================================================================ DV2 常量 (T-D9 终集; WP0 import 落 registry, 双向锁载体)
DV2_CONSTANTS: dict = {
    # ⓪ 不可名指闸词表 (v27 + v33 扩四词; 值逐字节照抄 listed 03)
    "unnameable": ["银团", "牵头", "等金融机构", "等银行", "或非银行",
                   "参团", "包括但不限于", "在内的多家", "多家银行"],
    # 境外闸最小必含清单 (v29; 国家/地区词段 + 法人尾缀段)
    "overseas_words": ["越南", "新加坡", "香港", "澳门", "台湾", "韩国", "日本", "泰国",
                       "马来西亚", "印尼", "菲律宾", "美国", "英国", "法国", "德国", "瑞士",
                       "荷兰", "澳大利亚", "加拿大", "亚洲", "欧洲", "国际", "海外"],
    "foreign_suffixes": ["AG", "N.A.", "Ltd", "LTD", "BRANCH", "PLC", "S.A.", "N.V.",
                         "Bhd", "Limited"],
    # 泛称黑名单 (head 级施加, v27)
    "generic_heads": ["银行"],
    # 尾段附属实体黑名单 (v29)
    "affiliate_tail": ["村镇", "信托", "证券", "培训", "工会", "劳动服务", "劳司",
                       "房地产", "咨询", "技协", "租赁", "基金", "保险", "服务公司", "服务部",
                       "协会", "委员会", "监督管理"],  # (R2 P2-1) 银行业协会/银监会类穿透封死
    # head 内豁免家族 (v33 S2-P1: 境内法人行 canonical 自含境外词者, 8 家)
    "head_exempt_note": "厦门国际银行/中信银行国际(中国)/法国兴业银行(中国)/法国巴黎银行(中国)/"
                        "摩根士丹利国际银行(中国)/澳大利亚和新西兰银行(中国)/瑞士银行(中国)/宁波通商银行",
    # 公司缺 city 境外占位 (DV4b ③)
    "city_overseas": ["大开曼", "香港特别行政区"],
    "city_placeholder": ["省直辖县级行政区划", "自治区直辖县级行政区划"],
    # T-D5c 网点侧 CityName 占位值集 (税调净新增键; T-P0-2 实测全集恰 225 行:
    # 海南省直辖 128 / 海南省直辖县级行政区 93 / 省直辖县级行政区划 3 / 省直辖县级行政区 1)
    "city_placeholder_branch_side": ["海南省直辖", "海南省直辖县级行政区",
                                     "省直辖县级行政区划", "省直辖县级行政区"],
}


def _init_stage_logging() -> None:
    """接入主管道日志基建 (core/logging.py::setup_logging): 写 company_tax_bank/logs/<stem>.log,
    格式/每次运行覆盖/50MB rotate 与主管道各阶段日志完全一致。单文件 importlib 加载, 不引入包依赖。"""
    import os
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return  # WP-A: 测试进程绝不接管文件日志 (2026-07-07 审计: 负例测试曾首写截断覆盖生产日志)
    import importlib.util
    spec = importlib.util.spec_from_file_location("_np_core_logging", REPO / "core" / "logging.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.setup_logging(Path(__file__).stem, str(HERE / "logs"))
    # setup_logging 置 propagate=False (主管道防双打惯例); 本脚本进程 root 无 handler,
    # 恢复 True 无双打副作用, 且保 pytest caplog (root handler) 可捕 — 否则负例测试调过
    # main() 后, 同会话后续 caplog 断言静默失捕 (2026-07-07 实弹)
    logging.getLogger(Path(__file__).stem).propagate = True


class _EngineLogRename(logging.Filter):
    """把借用的 listed 加权引擎 logger 记录改名为本税调阶段名 — 真正兑现 redirect_module_logger
    语义。attach 只接管 handler 不改名, 会让引擎自身 emit 的 budget/chunk 收缩等行携带 listed
    引擎阶段名混入税调 03 日志 (按阶段名 grep 排障会漏归, 且步骤号错标为 02)。改写 record.name
    使这些行归到宿主税调阶段 (纯 cosmetic, 零数据/确定性影响; R1/T-D10)。"""

    def __init__(self, stage_name: str) -> None:
        super().__init__()
        self._stage = stage_name

    def filter(self, record: logging.LogRecord) -> bool:
        record.name = self._stage
        return True


def _attach_engine_logging() -> None:
    """跨管道引擎日志接管 (T-D10, 镜像主仓 redirect_module_logger 语义): 把本阶段文件
    handler attach 到 listed 02 引擎 logger + 挂改名 Filter, 使 budget 生效值与 chunk 收缩
    WARNING 以本税调阶段名落税调 03 日志文件 (否则只上 console 且携带 listed 阶段名, 生产日志
    失载/错归)。仅 attach 文件 handler (console 由税调 02 的 engine() attach 兜底, 避免 console
    双打)。测试进程不接管。"""
    import os
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return
    # 白名单字面量 ① (T-D8): listed 02 引擎 logger 名, 跨管道 importlib 目标串
    eng_logger = logging.getLogger("02_build_company_bank_cooc_panel")
    if not any(isinstance(f, _EngineLogRename) for f in eng_logger.filters):
        eng_logger.addFilter(_EngineLogRename(Path(__file__).stem))  # R1: 改名兑现真 redirect
    for h in logger.handlers:
        if isinstance(h, logging.FileHandler) and h not in eng_logger.handlers:
            eng_logger.addHandler(h)
    eng_logger.setLevel(logging.INFO)


def log(msg: str, warn: bool = False) -> None:
    (logger.warning if warn else logger.info)(msg)


def _rss_mb() -> float:
    import psutil
    return psutil.Process().memory_info().rss / 1024 / 1024


def _lib_ver(name: str) -> str:
    """关键库版本 (仅日志用途; 未安装/无发行元数据 → 'n/a', 不影响任何计算)。"""
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return "n/a"


def _log_stage_header(pairs_path: Path, registry_path: Path, dta_path: Path, outdir: Path,
                      year_min: int, year_max: int) -> None:
    """阶段头汇报块 (完全参照主管道 12_news_fintech.log 的内容格式, 税调化)。"""
    import os
    import platform
    import sys as _sys
    stem = Path(__file__).stem
    logger.info("--- 开始执行阶段: %s ---", stem)
    logger.info("=" * 72)
    logger.info("步骤 03: 双替代权源构建 (城市/县域网点两层级) + 双权面板批量生产 + 三权互验 (WP5)")
    logger.info("=" * 72)
    logger.info("【功能】从 config/银行业金融机构基本信息表.dta 构建城市层级 (branch_city) 与县域层级")
    logger.info("        (branch_county) 两套 税调企业×银行×年 网点存续权长表, 复用步骤 02 的 SSOT 加权")
    logger.info("        引擎批量生产两套真实面板 (与媒体共现权面板并成三权), 并产三权互验报告")
    logger.info("        (富集度双基准/份额 Spearman/均值差/Top-1/支撑对比 等 T-D7 件套)。")
    logger.info("【方法】银行名 canonical 化 = DV2 判定序 (缺失闸→不可名指→境外闸+head 内豁免→泛称/")
    logger.info("        尾段黑名单→审计); 单点读表+公共规范化段 (剥括注/T-D5c 网点侧占位城名回退/字面")
    logger.info("        'None' 清洗/端点闸一次) 后城县两 builder 分臂; 县域复合键 (city,county) 精确")
    logger.info("        匹配, 三条例外机器规则 ((i) 占位退化键/(ii) 直筒子 NaN/(iii) 无匹配审计);")
    logger.info("        own-bank 剔除在长表落盘前施加; DV2 常量双向锁 + pair 长表 registry 指纹校验。")
    logger.info("【判读】富集度 (有网点关系对的共现命中率 vs 零模型基准) > 1 支持'共现代理真实关系';")
    logger.info("        叙事以边际保持基准为准 (机械边际集中已扣除), gate 按均匀基准 1.5×; 城县两权")
    logger.info("        方向一致 > 单点数值; 覆盖锚 城 A≥90%∧B≥99.5% / 县 A≥85%∧B≥99.5% 是硬闸")
    logger.info("        (T-D6 探针实证终值; 翻红=数据商改版信号, 先查改版而非放松阈值)。")
    logger.info("【确定性】纯 pandas ($0), 无 LLM/网络/API; sorted 遍历 + 闭式聚合, 同输入可复现;")
    logger.info("          报告与 codebook 禁写生成时间戳 (T-D16 确定性验收域); 未映射名称全量落审计。")
    logger.info("")
    logger.info("  🧭 项目 / 环境信息")
    logger.info("     · 步骤: %s (WP5 双权互验, company_tax_bank 流水线 03/03; 不注册主 DAG)", stem)
    logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板), 当前版本 v3.16.0")
    logger.info("     · 权威执行计划: scripts/audit/COMPANY_TAX_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-08.md (v7)")
    logger.info("     · 模块文件: %s", Path(__file__).resolve())
    logger.info("     · 工作目录: %s", os.getcwd())
    logger.info("     · Python:   %s @ %s", platform.python_version(), _sys.executable)
    logger.info("     · 平台:     %s | CPU 逻辑核=%s", platform.platform(), os.cpu_count())
    logger.info("     · 关键库:   pandas=%s | numpy=%s | pyarrow=%s | pyreadstat=%s | scipy=%s",
                _lib_ver("pandas"), _lib_ver("numpy"), _lib_ver("pyarrow"),
                _lib_ver("pyreadstat"), _lib_ver("scipy"))
    logger.info("     · 关键库②: PyYAML=%s | psutil=%s (importlib.metadata 读数, 仅日志用途)",
                _lib_ver("PyYAML"), _lib_ver("psutil"))
    logger.info("     · PID=%s | RUN_ID=%s | 本步骤纯 CPU / 无 LLM·网络·API ($0) / 确定性可复现",
                os.getpid(), os.environ.get("NEWS_PROCESS_RUN_ID", "standalone"))
    logger.info("     · 内存预算: NEWS_PROCESS_COOC_BUDGET_CELLS=%s (T-D13: 分支长表 ~千万行级; "
                "orchestrator 注入默认 1.0B [WP-S1 提速 v2, 见 run_pipeline.py/README], "
                "手工 export 勿低于此值防 chunk 收缩)",
                os.environ.get("NEWS_PROCESS_COOC_BUDGET_CELLS", "未设→引擎默认"))
    logger.info("  🔗 流水线定位 / 上下游 / 复现")
    logger.info("     · 上游: 01 registry yaml (启动双向锁+哈希指纹, 缺/stale 即 SystemExit) + 02 pair 长表")
    logger.info("       (互验媒体锚, '无锚即无互验') + 02 的 SSOT 加权引擎与 write_outputs")
    logger.info("       (importlib.import_module 复用, 管道内禁第二份实现, T-D1/T-D10)")
    logger.info("     · 下游消费者: Stata 分析端三权 specification-curve 森林图 (primary 权重预先声明,")
    logger.info("       禁挑臂单报) + gate 测试 tests/test_company_tax_bank_weight_validation.py (47 用例)")
    logger.info("     · 复现命令: python company_tax_bank/run_pipeline.py --steps 03 (WP-orch 期建立); 或")
    logger.info("       直接 python company_tax_bank/03_build_company_tax_bank_weight_validation.py")
    logger.info("     · 关键 config 键: registry `dv2_constants` (DV2 双向锁) / `bank_company_map` (own-bank")
    logger.info("       剔除) / `entries[].range_gate` (面板值域 gate) / `meta.registry_sha256` (pair 指纹锚)")
    logger.info("  📂 输入 / 输出文件")
    logger.info("     · 输入(pair 长表): %s", pairs_path)
    logger.info("       角色=互验媒体锚 (步骤 02 产出; canonical (company,bank) 对×轨×篇数;")
    logger.info("       内嵌 registry_sha256 指纹, 与当前 registry 不一致即 SystemExit)")
    logger.info("     · 输入(registry): %s", registry_path)
    logger.info("       角色=加权引擎 SSOT (DV2 常量双向锁 + own-bank 映射 + 测度 range_gate 值域档案)")
    logger.info("     · 输入(权源 dta): %s (商业许可, 恒不入库; 603,907 行锚由 gate 测试锚死,", dta_path)
    logger.info("       翻红=数据商改版信号; 城县两权同源一表, 单点读一次分臂)")
    logger.info("     · 输出(双权长表): %s (_company_tax_bank_altweights_{scheme}.parquet ×2)", outdir)
    logger.info("       统一 schema company/bank/year/w (无稳健臂); own-bank 已剔")
    logger.info("     · 输出(双权面板): %s (company_tax_bank_{scheme}w_panel.{dta,parquet} ×2)", outdir)
    logger.info("       与媒体主面板同引擎同列名 (cw_/ce_ 列族); 缺失语义: rel_n_banks=0 行 cw/ce 全 NaN 非 0")
    logger.info("       ('无网点关系'≠'测度为零'); 县权面板另 +county_key_ok int8 (缺键 vs 真零机器可判);")
    logger.info("       禁三面板横向 merge / 禁混同一 Hansen J")
    logger.info("     · 输出(互验报告): %s", outdir / "_company_tax_bank_weight_validation.md")
    logger.info("       T-D7 件套 (覆盖/城县支撑对比/Spearman 三行/富集度双基准+均值差/Top-1) + ⑥ 顶刊")
    logger.info("       披露包 + 反向证据三件套逐权点名 + 未映射审计附录 (top-50 频次全量留痕)")
    logger.info("     · 输出(codebook 双权章): %s (幂等 section-upsert, 标记字面量 SSOT=步骤 02)",
                outdir / "company_tax_bank_cooc_panel_codebook.md")
    logger.info("  ⚙ 运行配置")
    logger.info("     · 权源层级 = %s (%s) | DV2 常量键 %d 个 | 三轨 = %s",
                "/".join(SCHEMES), "/".join(SCHEME_LABEL_WORD[s] for s in SCHEMES),
                len(DV2_CONSTANTS), "/".join(TRACKS))
    logger.info("     · 年窗 = %d–%d (CLI --year-min/--year-max) | 输出目录 = %s (--output-dir, 整目录不入库)",
                year_min, year_max, outdir)
    logger.info("     · 通则: ⓑ 年窗两层 (脏年 >0.5% SystemExit / 窗外 INFO 裁剪) | ⓒ w 非缺失必 >0 |")
    logger.info("       双面板串行生产 + merge/写盘间显式 del (T-D13 峰值控制, 禁同持两面板)")
    logger.info("  📖 方法论依据 (参考文献 43 条, 逐字引自项目已核验 DOI 池; 按主题九小节 [A]–[I], "
                "每条附锚定白话说明 + 迁移边界)")
    logger.info("   [A] 构念与效度 — 共现→关系的收敛效度 / 富集度零模型 (8 条)")
    logger.info("     · 共现代理关系的效度先例: Lee, C. M. C., Ma, P., & Wang, C. C. Y. (2015). Search-based")
    logger.info("       peer firms: Aggregating investor perceptions through internet co-searches. Journal of")
    logger.info("       Financial Economics, 116(2), 410–431. https://doi.org/10.1016/j.jfineco.2015.02.003")
    logger.info("       → 白话: 共同被检索能聚合出真实同侪关系; 本步骤把'媒体共现对是否富集于城市/县域")
    logger.info("         网点暴露关系'做成同构的收敛效度检验 (T-D7 ④), 逻辑与该文一致。")
    logger.info("     · 共现指数的边际污染: Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022).")
    logger.info("       A better index for analysis of co-occurrence and similarity. Science Advances, 8(4),")
    logger.info("       Article eabj9204. https://doi.org/10.1126/sciadv.abj9204")
    logger.info("       → 白话: 传统共现指数被两侧流行度机械抬高; 本步骤富集度因此设'边际保持'第二基准")
    logger.info("         (Σ m_b·a_b 解析式), 叙事只认扣除大银行机械重合后的倍数, 不引均匀基准夸大。")
    logger.info("     · 固定度序列零模型: Neal, Z. P., Domagalski, R., & Sagan, B. (2021). Comparing")
    logger.info("       alternatives to the fixed degree sequence model for extracting the backbone of")
    logger.info("       bipartite projections. Scientific Reports, 11(1), Article 23929.")
    logger.info("       https://doi.org/10.1038/s41598-021-03238-3")
    logger.info("       → 白话: 二部投影里'共同出现'大半由度序列机械决定; 边际保持基准即固定边际零模型的")
    logger.info("         闭式实现 (零随机、sorted 遍历), 同输入重跑逐字节一致。")
    logger.info("     · 零模型选择须元验证: Cimini, G., Carra, A., Didomenicantonio, L., & Zaccaria, A. (2022).")
    logger.info("       Meta-validation of bipartite network projections. Communications Physics, 5(1),")
    logger.info("       Article 76. https://doi.org/10.1038/s42005-022-00856-9")
    logger.info("       → 白话: 不同零模型判出的'显著关系'不同, 单一基准会误导; 本步骤双基准并报 (gate 按")
    logger.info("         均匀 1.5×, 叙事按边际保持), 两基准的差值本身即'大银行机械重合'的量化披露。")
    logger.info("     · MTMM 收敛/区分效度框架: Campbell, D. T., & Fiske, D. W. (1959). Convergent and")
    logger.info("       discriminant validation by the multitrait-multimethod matrix. Psychological")
    logger.info("       Bulletin, 56(2), 81–105. https://doi.org/10.1037/h0046016")
    logger.info("       → 白话: 同一构念多方法测量的相关矩阵是效度检验的原型; 互验 ③ Spearman (收敛) 与")
    logger.info("         ⑤ Top-1 低同银行率 (构念区分) 就是三权版 MTMM — 迁移边界: 只作描述性效度证据,")
    logger.info("         不当因果识别用 (⑥(b) 推断地位钉死)。")
    logger.info("     · 二部系统统计验证网络: Tumminello, M., Miccichè, S., Lillo, F., Piilo, J., &")
    logger.info("       Mantegna, R. N. (2011). Statistically validated networks in bipartite complex")
    logger.info("       systems. PLoS ONE, 6(3), Article e17994. https://doi.org/10.1371/journal.pone.0017994")
    logger.info("       → 白话: 二部共现须对随机零假设校验后才配称'关系'; 本步骤富集度 gate (均匀基准")
    logger.info("         1.5×) 即该思想的全局闭式版 — 迁移边界: 不做逐边 p 值过滤, 只报全局倍数")
    logger.info("         (长表保留全部 w>0 对, 不因'不显著'删边)。")
    logger.info("     · 边约束缺失误判骨架: Neal, Z. P., & Neal, J. W. (2024). Illustrating the importance")
    logger.info("       of edge constraints in backbones of bipartite projections. PLOS ONE, 19(5),")
    logger.info("       e0302973. https://doi.org/10.1371/journal.pone.0302973")
    logger.info("       → 白话: 忽略两侧度约束的零模型会系统性误判显著边; 边际保持基准把媒体/网点两侧")
    logger.info("         边际 (Σ m_b·a_b) 同时固定, 正是这一告诫在解析式富集度上的落地。")
    logger.info("     · 传统共现指数系统性纠偏: Mainali, K. P., & Slud, E. (2025). CooccurrenceAffinity:")
    logger.info("       An R package for computing a novel metric of affinity in co-occurrence data that")
    logger.info("       corrects for pervasive errors in traditional indices. PLOS ONE, 20(1),")
    logger.info("       Article e0316650. https://doi.org/10.1371/journal.pone.0316650")
    logger.info("       → 白话: Jaccard/支撑重合类指数受两侧边际机械驱动已是方法学共识; 互验 ② 支撑对比")
    logger.info("         因此明标'稠密语义、不作收敛效度证据' — 迁移边界: 本步骤只用双基准倍数叙事,")
    logger.info("         不搬其 MLE affinity 估计量 (零随机闭式可复现优先)。")
    logger.info("   [B] 网点密度 = 金融可达性 / 信贷通道 — 权源构念的经济学依据 (8 条)")
    logger.info("     · 银企关系谱系奠基: Petersen, M. A., & Rajan, R. G. (1994). The benefits of lending")
    logger.info("       relationships: Evidence from small business data. The Journal of Finance, 49(1), 3–37.")
    logger.info("       https://doi.org/10.1111/j.1540-6261.1994.tb04418.x")
    logger.info("       → 白话: 银行对企业的影响经由'关系'传导是银企实证的奠基前提 — 且其样本正是小企业;")
    logger.info("         税调企业以非上市中小企业为主, 本地网点暴露是其银企关系最可观测的载体。")
    logger.info("     · 地理邻近信息通道: Kang, B. U., & Nam, J. S. (2025). Do local newspapers matter to")
    logger.info("       institutional investors? Contemporary Accounting Research, 42(3), 1713–1743.")
    logger.info("       https://doi.org/10.1111/1911-3846.13049")
    logger.info("       → 白话: 信息与关系有地理边界; 城市/县域网点权用'企业注册地内该行存续网点数'做地理")
    logger.info("         暴露代理, 县域层级把地理边界收得比城市更紧 (同一权源的粒度梯子)。")
    logger.info("     · 网点渠道宏观奠基: Jayaratne, J., & Strahan, P. E. (1996). The finance-growth")
    logger.info("       nexus: Evidence from bank branch deregulation. The Quarterly Journal of Economics,")
    logger.info("       111(3), 639–670. https://doi.org/10.2307/2946668")
    logger.info("       → 白话: 分支管制放松→本地增长, 确立'网点布局是真实信贷供给通道'的奠基证据 —")
    logger.info("         本步骤以存续网点数为权正是把这条通道测度化; 迁移边界: 该文是州级准实验,")
    logger.info("         本处只借构念不借识别。")
    logger.info("     · 距离/关系借贷微观机制: Degryse, H., & Ongena, S. (2005). Distance, lending")
    logger.info("       relationships, and competition. The Journal of Finance, 60(1), 231–266.")
    logger.info("       https://doi.org/10.1111/j.1540-6261.2005.00729.x")
    logger.info("       → 白话: 银企距离直接进入贷款定价与竞争结构 — 注册地辖区内网点存续数是距离暴露的")
    logger.info("         行政区划粒度代理 (权源 dta 无坐标, 连续距离不可得, 该文划出本权源的测度上界)。")
    logger.info("     · 本地金融发展横截面: Guiso, L., Sapienza, P., & Zingales, L. (2004). Does local")
    logger.info("       financial development matter? The Quarterly Journal of Economics, 119(3), 929–969.")
    logger.info("       https://doi.org/10.1162/0033553041502162")
    logger.info("       → 白话: 一体化金融市场内'本地'金融发展仍显著影响企业 — 支持以企业注册地行政区为")
    logger.info("         暴露单元的设计选择 (城市/县域两级即该文'本地'边界的粒度梯子)。")
    logger.info("     · 网点扩张结构模型: Ji, Y., Teng, S., & Townsend, R. M. (2023). Dynamic bank")
    logger.info("       expansion: Spatial growth, financial access, and inequality. Journal of Political")
    logger.info("       Economy, 131(8), 2209–2275. https://doi.org/10.1086/724112")
    logger.info("       → 白话: 银行网点的空间扩张动态直接决定金融可达性分布 — '逐年重算存续网点数'的")
    logger.info("         时变权重设计 (yearly_counts 逐 t 重算 alive) 与该文的动态视角同构。")
    logger.info("     · 距离因果证据: Herpfer, C., Mjøs, A., & Schmidt, C. (2023). The causal impact of")
    logger.info("       distance on bank lending. Management Science, 69(2), 723–740.")
    logger.info("       https://doi.org/10.1287/mnsc.2022.4346")
    logger.info("       → 白话: 距离对放贷的影响有因果证据且随距离衰减 — 县域键比城市键更紧的粒度收缩")
    logger.info("         有经济学回报, 城县两权不是冗余而是暴露强度梯子。")
    logger.info("     · 分支网络旗舰新证: Aguirregabiria, V., Clark, R., & Wang, H. (2025). The geographic")
    logger.info("       flow of bank funding and access to credit: Branch networks, synergies, and local")
    logger.info("       competition. American Economic Review, 115(6), 1818–1856.")
    logger.info("       https://doi.org/10.1257/aer.20200374")
    logger.info("       → 白话: 分支网络结构决定资金地理流向与本地信贷可得的最新旗舰证据 — 网点存续权")
    logger.info("         作为暴露测度在顶刊语境下的当代合法性锚。")
    logger.info("   [C] 网点退出 (branch closures) — 存续判定端点的经济意义 (5 条)")
    logger.info("     · 关闭→本地信贷收缩: Nguyen, H.-L. Q. (2019). Are credit markets still local?")
    logger.info("       Evidence from bank branch closings. American Economic Journal: Applied Economics,")
    logger.info("       11(1), 1–32. https://doi.org/10.1257/app.20170543")
    logger.info("       → 白话: 网点关闭令本地小企业信贷持续收缩 — 存续判定必须扣掉退出网点 (Status=2 ∧")
    logger.info("         quit≤t 即出局), 否则权重把已断的通道当活的计。")
    logger.info("     · 关闭后定价/信息不对称: Bonfim, D., Nogueira, G., & Ongena, S. (2021). \"Sorry,")
    logger.info("       we're closed\": Bank branch closures, loan pricing, and information asymmetries.")
    logger.info("       Review of Finance, 25(4), 1211–1259. https://doi.org/10.1093/rof/rfaa036")
    logger.info("       → 白话: 关闭改变的不止数量还有定价与软信息 — 支持逐年重算存续 (而非期初固定快照)")
    logger.info("         的时变权重口径; 端点解析失败按'未发生'保守处理 (失败率 0% 单点闸)。")
    logger.info("     · 信贷冲击→实体经济: Greenstone, M., Mas, A., & Nguyen, H.-L. (2020). Do credit")
    logger.info("       market shocks affect the real economy? Quasi-experimental evidence from the Great")
    logger.info("       Recession and \"normal\" economic times. American Economic Journal: Economic")
    logger.info("       Policy, 12(1), 200–225. https://doi.org/10.1257/pol.20160005")
    logger.info("       → 白话: 县级信贷供给变动传导到实体经济的准实验传统 — 县域层级聚合 (而非只做城市)")
    logger.info("         的实证价值出处; 迁移边界: 本步骤只产暴露权, 结果端效应留给分析侧。")
    logger.info("     · 关闭抑制企业创建: Cardamone, P., & Trivieri, F. (2024). Out of sight, out of mind!")
    logger.info("       Bank branch closures and new firm creation in Italy. Regional Studies, Regional")
    logger.info("       Science, 11(1), 122–152. https://doi.org/10.1080/21681376.2024.2315187")
    logger.info("       → 白话: 网点消失连'新企业出生'都受抑 — 税调样本以中小企业为主, 网点存续权对该")
    logger.info("         人群是一阶暴露而非二阶噪音。")
    logger.info("     · 分支体系长期衰退: Keil, J., & Ongena, S. (2024). The demise of branch banking –")
    logger.info("       Technology, consolidation, bank fragility. Journal of Banking & Finance, 158,")
    logger.info("       Article 107038. https://doi.org/10.1016/j.jbankfin.2023.107038")
    logger.info("       → 白话: 技术与并购驱动网点体系收缩是趋势性事实 — 年窗内网点进入/退出提供时间")
    logger.info("         变异, 呼应 codebook 'FE 后识别变异仅网点进入退出'的共线性警示。")
    logger.info("   [D] 县域金融与中国网点证据 — 县级层级的独立价值 (6 条)")
    logger.info("     · 农村银行奠基实验: Burgess, R., & Pande, R. (2005). Do rural banks matter? Evidence")
    logger.info("       from the Indian social banking experiment. American Economic Review, 95(3),")
    logger.info("       780–795. https://doi.org/10.1257/0002828054201242")
    logger.info("       → 白话: 农村/县域网点扩张有独立于城市体系的实体效应 — 县域权不是城市权的降采样,")
    logger.info("         而是不同暴露人群的测度 (branch_county 支撑 = 有真县级区划企业子集)。")
    logger.info("     · 中国城商行本地发展: Chen, Z., Poncet, S., & Xiong, R. (2020). Local financial")
    logger.info("       development and constraints on domestic private-firm exports: Evidence from city")
    logger.info("       commercial banks in China. Journal of Comparative Economics, 48(1), 56–75.")
    logger.info("       https://doi.org/10.1016/j.jce.2019.09.005")
    logger.info("       → 白话: 城商行布局度量中国本地金融发展的先例 — 城市层级键 (city_key 去市尾) 与")
    logger.info("         中国场景的适配性锚点。")
    logger.info("     · 中国网点地理×企业: Lai, S., Chen, L., Wang, Q. S., & Anderson, H. D. (2023). Bank")
    logger.info("       competition and corporate employment: Evidence from the geographic distribution of")
    logger.info("       bank branches in China. Journal of Banking & Finance, 154, Article 106964.")
    logger.info("       https://doi.org/10.1016/j.jbankfin.2023.106964")
    logger.info("       → 白话: '网点×地理×企业'同构数据形态在中国的顶刊先例 — 本步骤权源 dta 的字段")
    logger.info("         语义 (HeadofficeName/CityName/CountyName/存续端点) 即该文所用测度族。")
    logger.info("     · branch density 测度选择: Gama, P. M., Sol Murta, F., & Vieira, E. S. (2024). Local")
    logger.info("       banking development and SME conservative financing policy. Does bank branch")
    logger.info("       density matter? Small Business Economics, 63(4), 1747–1765.")
    logger.info("       https://doi.org/10.1007/s11187-024-00910-6")
    logger.info("       → 白话: 对 SME 起作用的是网点'密度'而非有无 dummy — w=存续网点计数 (非 0/1) 的")
    logger.info("         测度选择依据; 单银行企业 rel_hhi≡1 由 gate 断言锚死。")
    logger.info("     · 中国县域网点扩张: Qiao, L., Guo, D., Wu, C., & Wang, H. (2025). Exploring common")
    logger.info("       prosperity in China's counties: From the perspective of bank branch expansion.")
    logger.info("       Cities, 158, Article 105724. https://doi.org/10.1016/j.cities.2025.105724")
    logger.info("       → 白话: 县级网点扩张的中国当代证据 — branch_county 权源年窗 (2011–2020) 恰落其")
    logger.info("         记录的县域扩张高峰期, 权重时间变异非空转。")
    logger.info("     · 金科×网点交互: Zhang, X., & Li, Z. (2026). FinTech and branch network expansion:")
    logger.info("       Evidence from China's banking industry. Applied Economics, 58(12), 2321–2336.")
    logger.info("       https://doi.org/10.1080/00036846.2025.2476213")
    logger.info("       → 白话: 金科发展与网点扩张互动 — 本管道用网点权聚合的正是银行金科测度 (cw_ 列族),")
    logger.info("         该文提示两者相关是实质现象而非本设计的工件; 分析端解释系数时须记住这层内生。")
    logger.info("   [E] MAUP 与区划键 — 城/县双层级与县改区错位 (3 条)")
    logger.info("     · MAUP 经典: Fotheringham, A. S., & Wong, D. W. S. (1991). The modifiable areal unit")
    logger.info("       problem in multivariate statistical analysis. Environment and Planning A: Economy")
    logger.info("       and Space, 23(7), 1025–1044. https://doi.org/10.1068/a231025")
    logger.info("       → 白话: 多元统计结论可随空间聚合单元改变 — 城/县两级并排本身就是 MAUP 敏感性")
    logger.info("         检验的直接落地 (同一权源换聚合单元, 结论应方向一致); 迁移边界: 权源无坐标,")
    logger.info("         无法做连续距离/网格加密的完整 MAUP 谱。")
    logger.info("     · 县改区经济效应: Zhao, B., & Xi, X. (2022). Economic effects of conversion from")
    logger.info("       county (or county-level city) to municipal district in China. PLOS ONE, 17(9),")
    logger.info("       Article e0272267. https://doi.org/10.1371/journal.pone.0272267")
    logger.info("       → 白话: 县改区在样本期是高频行政区划事件 — 权源快照 (2026 现址) 与税调批次两时点")
    logger.info("         的键错位由此产生, 计入 B 锚缺口诚实披露而非建别名表硬对齐 (L4/§8-N6)。")
    logger.info("     · 县改区驱动因素: Tan, P., & Wang, R. (2026). Local drivers of municipal")
    logger.info("       consolidation: County-to-district conversion in China. Land, 15(4), Article 672.")
    logger.info("       https://doi.org/10.3390/land15040672")
    logger.info("       → 白话: 县改区决策与本地经济状态相关 (非随机) — 若建别名表强行回填, 等于把内生的")
    logger.info("         区划变更混进权重构造; '不建表、留缺口'是识别上更保守的选择。")
    logger.info("   [F] own-bank 剔除 — related lending 文献依据 (3 条)")
    logger.info("     · 关联贷款奠基: La Porta, R., Lopez-de-Silanes, F., & Zamarripa, G. (2003). Related")
    logger.info("       lending. The Quarterly Journal of Economics, 118(1), 231–268.")
    logger.info("       https://doi.org/10.1162/00335530360535199")
    logger.info("       → 白话: 银行对关联企业的放贷条件系统性异于市场交易 — 银行系税调企业×自家银行的")
    logger.info("         '关系'是内部人通道非本构念, own-bank 对在长表落盘前剔除的直接文献依据。")
    logger.info("     · 关联租金证据: Khwaja, A. I., & Mian, A. (2005). Do lenders favor politically")
    logger.info("       connected firms? Rent provision in an emerging financial market. The Quarterly")
    logger.info("       Journal of Economics, 120(4), 1371–1411. https://doi.org/10.1162/003355305775097524")
    logger.info("       → 白话: 关联/政治连接放贷含租金转移 — 不剔 own-bank 会同时虚增双权并令互验富集度")
    logger.info("         向上偏 (机械对角线命中), 剔除是效度检验自身的防污染要求。")
    logger.info("     · 所有权网络信息作用: Gao, H., Ru, H., & Yang, X. (2022). The informational role of")
    logger.info("       ownership networks in bank lending. Journal of Financial and Quantitative Analysis,")
    logger.info("       57(8), 2993–3017. https://doi.org/10.1017/S0022109021000788")
    logger.info("       → 白话: 中国银行放贷沿所有权网络传导信息 — own-bank 剔除集以股权归属界定")
    logger.info("         (registry bank_company_map, 280 家) 的口径依据; 迁移边界: 只剔直接自家对,")
    logger.info("         不剔间接股权链 (该扩展属分析端稳健臂)。")
    logger.info("   [G] 名称匹配 (record linkage) — DV2 canonical 化的方法学地位 (5 条)")
    logger.info("     · 记录链接理论奠基: Fellegi, I. P., & Sunter, A. B. (1969). A theory for record")
    logger.info("       linkage. Journal of the American Statistical Association, 64(328), 1183–1210.")
    logger.info("       https://doi.org/10.1080/01621459.1969.10501049")
    logger.info("       → 白话: 链接判定 = 显式规则下的分类问题 (method-origin); DV2 判定序 (缺失闸→不可")
    logger.info("         名指→境外闸→黑名单→截断查表) 是其确定性 rule-based 特例, 全规则可枚举可审计。")
    logger.info("     · 自动链接偏误评估: Bailey, M. J., Cole, C., Henderson, M., & Massey, C. (2020). How")
    logger.info("       well do automated linking methods perform? Lessons from US historical data.")
    logger.info("       Journal of Economic Literature, 58(4), 997–1044. https://doi.org/10.1257/jel.20191526")
    logger.info("       → 白话: 假阳性链接比假阴性对下游估计更毒 — DV2 '精确失败即落审计、绝不模糊截断'")
    logger.info("         (不可剥括注禁入截断) 的保守序即按此权衡设计。")
    logger.info("     · 自动链接实务基准: Abramitzky, R., Boustan, L., Eriksson, K., Feigenbaum, J., &")
    logger.info("       Pérez, S. (2021). Automated linking of historical data. Journal of Economic")
    logger.info("       Literature, 59(3), 865–918. https://doi.org/10.1257/jel.20201599")
    logger.info("       → 白话: 链接质量必须以可复核方式披露 — 互验报告'未映射审计附录 (top-50 频次全量")
    logger.info("         留痕)'即其推荐的链接透明度实践。")
    logger.info("     · entity resolution 全景: Binette, O., & Steorts, R. C. (2022). (Almost) all of")
    logger.info("       entity resolution. Science Advances, 8(12), Article eabi8021.")
    logger.info("       https://doi.org/10.1126/sciadv.abi8021")
    logger.info("       → 白话: 实体消解的规范流程 = 规范化→阻塞→判定→审计; BankCanon 的 memo 缓存 +")
    logger.info("         audit 重放记账即该流程的单机确定性实现 (同名输入恒同输出)。")
    logger.info("     · 链接数据=缺失数据视角: Kamat, G., & Gutman, R. (2026). Analysis of linked files:")
    logger.info("       A missing data perspective. Statistical Science, 41(1). https://doi.org/10.1214/24-STS939")
    logger.info("       → 白话: 未链接单元应按缺失机制建模而非静默丢弃 — 县权缺键走 NaN 通道 +")
    logger.info("         county_key_ok 指示列 (缺键≠真零机器可判), 正是该视角在面板端的落地。")
    logger.info("   [H] 份额识别与暴露推断 — shift-share 谱系 (2 条)")
    logger.info("     · 份额外生性诊断: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik")
    logger.info("       instruments: What, when, why, and how. American Economic Review, 110(8), 2586–2624.")
    logger.info("       https://doi.org/10.1257/aer.20181047")
    logger.info("       → 白话: share×shift 设计的识别落在'份额'上; 用媒体共现/城市网点/县域网点三套彼此")
    logger.info("         独立来源的份额互验 (Spearman/富集度), 正是对'哪一种份额驱动结论'的直接诊断。")
    logger.info("     · 暴露相关稳健推断: Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs:")
    logger.info("       Theory and inference. The Quarterly Journal of Economics, 134(4), 1949–2010.")
    logger.info("       https://doi.org/10.1093/qje/qjz025")
    logger.info("       → 白话: 份额结构相似的企业残差相关, 常规 SE 失真; 互验报告 ⑥(c) 逐权内生性处方中")
    logger.info("         的 exposure-robust SE (AKM 2019) 即出自此文。")
    logger.info("   [I] 多重规格与复现 — 三权并排的方法学地位 (3 条)")
    logger.info("     · 规格曲线: Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve")
    logger.info("       analysis. Nature Human Behaviour, 4(11), 1208–1214.")
    logger.info("       https://doi.org/10.1038/s41562-020-0912-z")
    logger.info("       → 白话: 所有合理规格一次报全而非挑好看的报; 三权面板把'权重构造'物化成规格维度 —")
    logger.info("         同一 (测度,DV) 报三权系数森林图, 禁挑臂单报 (互验报告 ⑥(b) 落地)。")
    logger.info("     · 研究者自由度方差: Menkveld, A. J., Dreber, A., Holzmeister, F., Huber, J.,")
    logger.info("       Johannesson, M., Kirchler, M., Razen, M., Weitzel, U., … [百人合著] (2024).")
    logger.info("       Nonstandard errors. The Journal of Finance, 79(3), 2339–2390.")
    logger.info("       https://doi.org/10.1111/jofi.13337")
    logger.info("       → 白话: 同一数据不同团队结果的方差主要来自研究者自由度; 三权把权重构造这一自由度")
    logger.info("         显式暴露为可并排检验的对象, 而非藏进未披露的取舍。")
    logger.info("     · 复现性大样本证据: Brodeur, A., Mikola, D., Cook, N., … [百人合著] (2026).")
    logger.info("       Reproducibility and robustness of economics and political science research. Nature,")
    logger.info("       652(8108), 151–156. https://doi.org/10.1038/s41586-026-10251-x")
    logger.info("       → 白话: 大规模复现研究凸显了机器可核验复现材料的价值; 本步骤覆盖锚/双向锁/parquet")
    logger.info("         指纹全部 fail-loud, 同输入重跑字节级一致, 即此类可核验证据的工程落地。")
    logger.info("")


MISSING_SET = {"None", "nan", ""}
COMPANY_SUFFIX_RE = re.compile(r"(股份有限公司|有限责任公司|有限公司|股份公司)$")
PAREN_RE = re.compile(r"[（(]([^（）()]*)[)）]")


def norm(s: pd.Series) -> pd.Series:
    """DV4 通则 ⓐ: dtype 规范化 (v29 配方锚定 r'\\.0$' 正则)。"""
    return s.astype(str).str.replace(r"\.0$", "", regex=True)


def is_missing(s: pd.Series) -> pd.Series:
    return norm(s).isin(MISSING_SET)


# ================================================================ DV2 canonical 化 (母本单函数照搬, 本地裁剪版 §8-N5)
class BankCanon:
    def __init__(self):
        import yaml
        banks = yaml.safe_load((CONFIG / "bank_names.json").read_text(encoding="utf-8"))
        self.variant_to_canon: dict[str, str] = {}
        for b in banks:
            for v in b["variants"]:
                self.variant_to_canon.setdefault(v, b["bank_name"])
        self.canonicals = {b["bank_name"] for b in banks}
        self.audit: dict[str, int] = {}  # 未映射审计 (名称 → 频次)
        self._memo: dict[str, str | None] = {}
        c = DV2_CONSTANTS
        assert set(c["overseas_words"]) >= {"越南", "新加坡", "亚洲", "国际"}  # DV6 常量 ⊇ 最小集 (03:292 断言保留)
        self._overseas = c["overseas_words"]
        self._fsuffix = c["foreign_suffixes"]
        self._unname = c["unnameable"]
        self._tail = c["affiliate_tail"]

    def _audit_add(self, name: str) -> None:
        self.audit[name] = self.audit.get(name, 0) + 1

    def _strip_paren(self, name: str):
        """返回 (剥括注后名称, 括注列表)。"""
        parens = PAREN_RE.findall(name)
        return PAREN_RE.sub("", name), parens

    def _overseas_hits(self, name: str) -> list[str]:
        hits = [w for w in self._overseas if w in name]
        hits += [sfx for sfx in self._fsuffix if sfx in name]
        return hits

    def canon(self, raw) -> str | None:
        """DV2 判定序: ⓪₀ → ⓪ → ① (原名/剥公司后缀精确查表, 括注规则) → ② (截断+闸) → ③ 审计。"""
        name = str(raw).strip() if raw is not None else ""
        cached = self._memo.get(name, "\x00")
        if cached != "\x00":
            self._audit_replay(name, cached)
            return cached
        result = self._canon_uncached(name)
        self._memo[name] = result
        self._audit_replay(name, result)
        return result

    def _audit_replay(self, name: str, result) -> None:
        if result is None:
            self._audit_add(name if name not in MISSING_SET else "<MISSING>")

    def _canon_uncached(self, name: str) -> str | None:
        V = self.variant_to_canon
        # ⓪₀ 输入缺失闸 (v32)
        if name in MISSING_SET:
            return None
        # ⓪ 不可名指闸
        if any(w in name for w in self._unname):
            return None
        # ① 原名/剥公司后缀精确查表
        if name in V:
            return V[name]
        base = COMPANY_SUFFIX_RE.sub("", name)
        if base in V:
            return V[base]
        # 括注规则: 仅 '中国' 或 '原*' 可剥 (剥后重试); 其余 = 不可剥括注 → 禁入 ② (v33 S2-P0)
        stripped, parens = self._strip_paren(base)
        if parens:
            if all(p == "中国" or p.startswith("原") for p in parens):
                if stripped in V:
                    return V[stripped]
                sb = COMPANY_SUFFIX_RE.sub("", stripped)
                if sb in V:
                    return V[sb]
                base = sb  # 剥后进入后续判定 (含境外闸/截断)
            else:
                return None  # 不可剥括注 → 精确失败即落审计, 绝不截断
        # 境外主体闸 (v27/v29) + head 内豁免 (v33 S2-P1)
        has_bank = "银行" in base
        head = (base.split("银行", 1)[0] + "银行") if has_bank else base
        tail = base.split("银行", 1)[1] if has_bank else ""
        os_hits = self._overseas_hits(base)
        if os_hits:
            exempt = head in V and all(w in head for w in os_hits)
            if not exempt:
                return None
        if not has_bank:
            return None  # ③
        # ② 泛称黑名单 head 级 (v27): head=="银行" → None (含"银行等金融机构"类复合泛称)
        if head == "银行":
            return None
        # ② 尾段附属实体黑名单 (v29): 截断后尾段非空 ∧ 含黑名单词 → None
        if tail and any(w in tail for w in self._tail):
            return None
        # ② 截至首个"银行"剥分支行再查 (含"中国"前缀增删双向)
        for cand in (head, head[2:] if head.startswith("中国") else "中国" + head):
            if cand in V:
                return V[cand]
        return None  # ③ 未映射审计 (canon() 外壳记账)


# ================================================================ 通则 ⓑ 年窗两层
def year_two_layer(years: pd.Series, year_min: int, year_max: int, tag: str,
                   sys_exit_frac: float = 0.005) -> pd.Series:
    """返回 keep mask; 第一层 (解析失败 ∨ ∉[1990,2035]) 剔+WARNING (>0.5%→SystemExit);
    第二层 (窗外真实年) 剔+INFO。"""
    bad = years.isna() | (years < 1990) | (years > 2035)
    n_bad = int(bad.sum())
    if n_bad:
        frac = n_bad / len(years)
        log(f"{tag}: 第一层脏年剔除 {n_bad} ({100 * frac:.4g}%)", warn=True)
        if frac > sys_exit_frac:
            raise SystemExit(f"{tag} 第一层脏年占比 {100 * frac:.4g}% > {100 * sys_exit_frac:.4g}%")
    outwin = ~bad & ((years < year_min) | (years > year_max))
    if outwin.any():
        log(f"{tag}: 第二层窗外年裁剪 {int(outwin.sum())} (INFO, 属预期)")
    return ~bad & ~outwin


def parse_year(s: pd.Series) -> pd.Series:
    import pandas as pd
    return pd.to_datetime(s.astype(str), errors="coerce").dt.year


# ================================================================ 公司键 (税调名单; T-D1 名单 SSOT)
def load_companies() -> tuple[list[str], pd.DataFrame]:
    """税调名单 → (企业全称 sorted 列表, geo 三列 DataFrame)。geo.company=company_tax_name。"""
    import pandas as pd
    import yaml
    comp = yaml.safe_load((CONFIG / "company_tax_names.yaml").read_text(encoding="utf-8"))["companies"]
    names = sorted(c["company_tax_name"] for c in comp)
    geo = pd.DataFrame([{"company": c["company_tax_name"],
                         "city": str(c.get("city") or ""), "district": str(c.get("district") or "")}
                        for c in comp])
    return names, geo


# ================================================================ provider 注册 (双 scheme, T-D5/§1)
SCHEMES = ("branch_city", "branch_county")
SCHEME_LABEL_WORD = {"branch_city": "城市网点", "branch_county": "县域网点"}
ROBUST_ARM_COLS = {"branch_city": [], "branch_county": []}  # 双 scheme 均无稳健臂 (T-D5b)

BRANCH_DTA = CONFIG / "银行业金融机构基本信息表.dta"
DTA_USECOLS = ["HeadofficeName", "CityName", "CountyName", "Status",
               "ApprovalDate", "QuitDate", "RunawayDate"]  # listed 六列 + CountyName (T-D5)


# ================================================================ 单点读表 + 公共规范化段 (T-D5/T-D5c)
def prepare_branch_frame(raw_df: pd.DataFrame, canon: BankCanon) -> tuple[pd.DataFrame, dict]:
    """单点规范化 (城县两 builder 分臂前共享, R3 走查 P1-2):
    ① HeadofficeName → canonical (映射率入日志);
    ② CountyName 剥括注 + 字面 "None"/缺失归空 (F3);
    ③ CityName 剥括注 + 缺失归空;
    ④ T-D5c: CityName ∈ city_placeholder_branch_side → CityName := (已清洗) CountyName 回退
       (网点侧占位对偶, 施加在剥括注后、分臂之前 — 城县两 builder 同受益);
    ⑤ city_key = 去市尾 (正则 市$ 单次); county_key 不去尾 (T-D5b 去尾豁免);
    ⑥ 端点失败率闸单点算一次 (分母 = Status∈{1,2} 行; >5% SystemExit / >1% WARNING)。
    返回 (b 六列帧 [bank/city/county/ap/quit/run/status], prep 统计 dict)。"""
    import numpy as np
    import pandas as pd
    df = raw_df.copy()
    uniq = {u: canon.canon(u) for u in df["HeadofficeName"].unique()}
    n_mapped_names = sum(1 for v in uniq.values() if v)
    n_all = len(df)
    df["bank"] = df["HeadofficeName"].map(uniq)
    df = df.dropna(subset=["bank"])
    logger.info("分支漏斗: 网点记录 %s 行 | 总行名 %s 种 → DV2 canonical 成功 %s 种 (%.4g%%) | "
                "映射后保留 %s 行 (%.4g%%; 未映射=境外/村镇/非银机构落审计)",
                f"{n_all:,}", f"{len(uniq):,}", f"{n_mapped_names:,}",
                100 * n_mapped_names / max(len(uniq), 1), f"{len(df):,}",
                100 * len(df) / max(n_all, 1))
    # ② CountyName 预清洗 (F3: 缺失形态是字面字符串 "None", 照搬 isna 判空会漏)
    county = df["CountyName"].astype(str).str.replace(PAREN_RE, "", regex=True).str.strip()
    county = county.where(~county.isin(["null", "None", "nan", ""]), "")
    # ③ CityName 预清洗三则 (剥括注 / 'null'+空串按缺失 / 未对齐落审计)
    city = df["CityName"].astype(str).str.replace(PAREN_RE, "", regex=True).str.strip()
    city = city.where(~city.isin(["null", "None", "nan", ""]), "")
    # ④ T-D5c 网点侧占位城名回退 (T-P0-2 源 dta 实测 225 行: 琼中/屯昌/定安等县死键漏计封堵;
    #    注: 225 是映射前原始占位行, 回退发生在 dropna(bank) 之后, 故实回退 = 已映射 canonical 银行的子集)
    n_ph_raw = int(raw_df["CityName"].astype(str).str.replace(PAREN_RE, "", regex=True).str.strip()
                   .isin(DV2_CONSTANTS["city_placeholder_branch_side"]).sum())
    ph_side = city.isin(DV2_CONSTANTS["city_placeholder_branch_side"])
    n_ph_side = int(ph_side.sum())
    city = city.where(~ph_side, county)
    if n_ph_side or n_ph_raw:
        logger.info("T-D5c 网点侧 CityName 占位回退: 已回退 %s 行 (= 源 dta 占位 %s 行 − 未映射 canonical "
                    "银行 %s 行经 dropna(bank) 剔除; 未映射行本无权重贡献故剔除无损) | CityName∈%s → "
                    "回退 CityName:=CountyName (公共规范化段施加, 城县两 builder 同受益)",
                    f"{n_ph_side:,}", f"{n_ph_raw:,}", f"{n_ph_raw - n_ph_side:,}",
                    DV2_CONSTANTS["city_placeholder_branch_side"])
    df["city"] = city.str.replace(r"市$", "", regex=True)  # ⑤ 正则 市$ 单次, 禁 rstrip
    df["county"] = county  # 去尾豁免 (直匹 97.53%, 剥尾制造 通州区↔通州市 歧义)
    status = norm(df["Status"])
    ap_y = parse_year(df["ApprovalDate"])
    quit_y = parse_year(df["QuitDate"])
    run_y = parse_year(df["RunawayDate"])
    # ⑥ 端点失败率闸 (单点一次; 分母 = Status∈{1,2}, T-D5 计量 P2-1 更正口径)
    exit_mask = status.isin(["2", "1"])
    fail = (status == "2") & quit_y.isna() | (status == "1") & run_y.isna()
    frac_fail = fail.sum() / max(int(exit_mask.sum()), 1)
    if frac_fail > 0.05:
        raise SystemExit(f"分支端点失败率 {100 * frac_fail:.4g}% > 5%")
    if frac_fail > 0.01:
        log(f"分支端点失败率 {100 * frac_fail:.4g}% > 1%", warn=True)
    logger.info("分支存续判定要素 (单点闸, 城县共享): Status 退出 %s / 失控 %s 行 | 端点日期解析"
                "失败率 %.4g%% (≤1%% 健康; 失败=按'未发生'保守处理) | 城市键 %s 种 | 县域键 %s 种 "
                "(空键行城 %s / 县 %s — 各 builder 侧剔除, 封死空键假匹配)",
                f"{int((status == '2').sum()):,}", f"{int((status == '1').sum()):,}",
                100 * frac_fail, f"{df['city'].replace('', np.nan).nunique():,}",
                f"{df['county'].replace('', np.nan).nunique():,}",
                f"{int((df['city'] == '').sum()):,}", f"{int((df['county'] == '').sum()):,}")
    b = pd.DataFrame({"bank": df["bank"], "city": df["city"], "county": df["county"],
                      "ap": ap_y, "quit": quit_y, "run": run_y, "status": status})
    stats = {"n_rows_raw": n_all, "n_rows_mapped": len(df), "n_headoffice_names": len(uniq),
             "n_mapped_names": n_mapped_names, "endpoint_fail_frac": float(frac_fail),
             "n_ph_side_fallback": n_ph_side}
    return b, stats


def yearly_counts(b: pd.DataFrame, keys: list[str], year_min: int, year_max: int) -> pd.DataFrame:
    """逐年存续网点计数 (母本 alive 式零改动): 存续 = approval≤t ∧ 非(退出∧quit≤t) ∧
    非(失控∧run≤t); 端点解析失败 = '未发生' 保守处理。返回 keys+bank+year+w 长表。"""
    import pandas as pd
    rows = []
    for t in range(year_min, year_max + 1):
        alive = (b["ap"].notna() & (b["ap"] <= t)
                 & ~((b["status"] == "2") & b["quit"].notna() & (b["quit"] <= t))
                 & ~((b["status"] == "1") & b["run"].notna() & (b["run"] <= t)))
        cnt = b[alive].groupby(keys + ["bank"]).size().rename("w").reset_index()
        cnt["year"] = t
        rows.append(cnt)
    return pd.concat(rows, ignore_index=True)


# ================================================================ T-D5a 城市层 branch_city
def build_weight_branch_city(geo: pd.DataFrame, net_city: pd.DataFrame,
                             branch_city_keys: set) -> tuple[pd.DataFrame, dict]:
    """公司键 = city (placeholder 退 district) 去市尾; 境外/缺失剔除; w = 城内该行当年存续
    网点数, w>0 才落长表。覆盖锚要素显式返回值 (不用 out.attrs — copy/merge 易丢, R3 P2-4)。"""
    import numpy as np
    g = geo.copy()
    placeholder = g["city"].isin(DV2_CONSTANTS["city_placeholder"])
    g["key"] = np.where(placeholder, g["district"], g["city"])
    # 键规范化与 net_city (dta 侧, PAREN 剥离) 及县权 deg_key 对称: 剥括注 + strip + 去市尾
    # (使 (i) 退化键两权恒等不依赖"税调 geo 无括注"外部前提, 非仅靠运行时 assert 事后兜底; R1 P2-3)
    g["key"] = (g["key"].str.replace(PAREN_RE, "", regex=True).str.strip()
                .str.replace(r"市$", "", regex=True))
    overseas_or_missing = (g["key"] == "") | g["city"].isin(DV2_CONSTANTS["city_overseas"])
    g_ok = g[~overseas_or_missing]
    n_audit = int(overseas_or_missing.sum())
    if n_audit:
        log(f"branch_city: 缺 city/境外审计通道企业 {n_audit} 家 (城权全缺失)")
    out = g_ok.merge(net_city, left_on="key", right_on="city")[["company", "bank", "year", "w"]]
    out = out[out["w"] > 0]
    cov = {"keyed_companies": set(g_ok["company"]),
           "n_keyed": len(g_ok),
           "n_overseas_missing": n_audit,
           "n_placeholder": int(placeholder.sum()),
           "hit_rate": float(g_ok["key"].isin(branch_city_keys).mean())}
    return out, cov


# ================================================================ T-D5b 县域层 branch_county (税调新 builder)
def build_weight_branch_county(geo: pd.DataFrame, net_city: pd.DataFrame,
                               net_comp: pd.DataFrame, branch_city_keys: set,
                               branch_comp_keys: set) -> tuple[pd.DataFrame, dict, dict]:
    """复合键 (city_key, county_key) 精确匹配 (同名区县跨市 310 个 — 复合键消歧)。
    三条例外 (全机器规则):
      (i)  city ∈ city_placeholder (占位 144 家): 绕过复合键, 公司键 = district 去市尾,
           网点计数走 city-level 折叠 (与 branch_city 同一 net_city 表同式 merge) —
           由构造保证城/县两权对这些企业逐 (bank,year) 数值恒等 (gate 锚死);
      (ii) district == '-' (直筒子 922 家): 县权长表无行 (NaN 通道), 不回退城市层;
      (iii) 复合键无匹配残差 (开发区等): 长表无行 + 审计计数。
    返回 (长表, 覆盖锚要素 dict, company→county_key_ok 映射 dict)。"""
    import pandas as pd
    g = geo.copy()
    placeholder = g["city"].isin(DV2_CONSTANTS["city_placeholder"])
    overseas = g["city"].isin(DV2_CONSTANTS["city_overseas"])  # 防御性空集 (F1 四地理零缺失)
    dash = (g["district"] == "-") & ~placeholder & ~overseas   # (ii) 显式 NaN 通道, 禁清洗归空
    # 公司侧复合键: city_key 去市尾; district_norm = 剥括注 + 脏值集清洗 两步 (去尾豁免)
    # city_key 与 net_comp.city (dta 侧) 及城权 key/deg_key 全对称 (三处均 PAREN_RE+strip+市$)
    # (defense-in-depth: 不依赖税调 geo 无括注/空白外部前提; 当前批 0 括注字节等价; R2 补齐)
    g["city_key"] = (g["city"].str.replace(PAREN_RE, "", regex=True).str.strip()
                     .str.replace(r"市$", "", regex=True))
    dn = g["district"].str.replace(PAREN_RE, "", regex=True).str.strip()
    dn = dn.where(~dn.isin(["null", "None", "nan"]), "")
    g["district_norm"] = dn
    empty_key = ~placeholder & ~overseas & ~dash & ((dn == "") | (g["city_key"] == ""))  # 防御性空集
    eligible = ~placeholder & ~overseas & ~dash & ~empty_key
    comp_probe = pd.MultiIndex.from_frame(g.loc[eligible, ["city_key", "district_norm"]])
    matched = pd.Series(False, index=g.index)
    matched.loc[eligible[eligible].index] = comp_probe.isin(branch_comp_keys)
    miss = eligible & ~matched  # (iii)
    # (i) 退化键: district 去市尾, 对 net_city 折叠计数 (与城权同表同式 → 恒等由构造保证)
    g["deg_key"] = g["district"].str.replace(PAREN_RE, "", regex=True).str.strip() \
                                .str.replace(r"市$", "", regex=True)
    ph_hit = placeholder & g["deg_key"].isin(branch_city_keys)  # (i) 的 B 锚判定 = city 层口径
    out_comp = g[eligible & matched].merge(
        net_comp, left_on=["city_key", "district_norm"], right_on=["city", "county"]
    )[["company", "bank", "year", "w"]]
    out_ph = g[placeholder].merge(net_city, left_on="deg_key",
                                  right_on="city")[["company", "bank", "year", "w"]]
    out = pd.concat([out_comp, out_ph], ignore_index=True)
    out = out[out["w"] > 0]
    # county_key_ok (T-D5b, int8): 1 = 有效复合键 (匹配) 或 (i) 退化键命中; 0 = (ii)/(iii)/境外缺键
    ok = (matched | ph_hit)
    key_ok = {c: int(v) for c, v in zip(g["company"], ok)}
    # (ii) 企业清单落审计日志 (全量留痕; 918 直筒子 + 4 零星)
    dash_by_city = g.loc[dash, "city"].value_counts().to_dict()
    logger.info("branch_county (ii) 直筒子/零星缺失通道: district=='-' 企业 %s 家 (县权全缺失 NaN, "
                "不回退城市层 — 回退会让县权复制城权污染互稳独立性) | 按市分布: %s",
                f"{int(dash.sum()):,}", dash_by_city)
    logger.info("branch_county (ii) 企业全量清单 (审计留痕): %s", "/".join(sorted(g.loc[dash, "company"])))
    if miss.any():
        logger.info("branch_county (iii) 复合键无匹配残差: %s 家 (开发区/高新区等非民政区划为主, 县权"
                    "全缺失, 诚实计入 B 锚缺口) | 全量清单: %s", f"{int(miss.sum()):,}",
                    "/".join(sorted(g.loc[miss, "company"])))
    cov = {"n_total": len(g),
           "n_dash": int(dash.sum()),
           "n_overseas": int(overseas.sum()),
           "n_empty_key": int(empty_key.sum()),
           "n_placeholder": int(placeholder.sum()),
           "n_placeholder_hit": int(ph_hit.sum()),
           "n_eligible": int(eligible.sum()),
           "n_matched": int(matched.sum()),
           "keyed_companies": set(g.loc[eligible | placeholder, "company"]),
           "placeholder_companies": set(g.loc[placeholder, "company"])}
    cov["n_keyed"] = len(cov["keyed_companies"])
    cov["hit_rate"] = (cov["n_matched"] + cov["n_placeholder_hit"]) / max(cov["n_keyed"], 1)
    return out, cov, key_ok


# ================================================================ own-bank 剔除 (D4 继承; T-D10 矢量化授权)
def drop_own_bank(longtab: pd.DataFrame, registry: dict, tag: str = "") -> pd.DataFrame:
    """own-bank 对在长表构建时剔除、长表落盘即已剔。矢量化 (own_map 仅 280 家 → isin 预过滤 +
    (company,bank) 对集合判定, 免千万行逐行 apply; 语义与母本逐行版恒等)。"""
    import pandas as pd
    own = {c: bs for c, bs in registry["bank_company_map"].items() if bs}  # 空列表值天然 no-op
    if not len(longtab) or not own:
        return longtab
    cand = longtab["company"].isin(own.keys())
    if not cand.any():
        return longtab
    pair_set = {(c, b) for c, bs in own.items() for b in bs}
    sub_hit = pd.MultiIndex.from_frame(longtab.loc[cand, ["company", "bank"]]).isin(pair_set)
    mask = pd.Series(False, index=longtab.index)
    mask.loc[longtab.index[cand][sub_hit]] = True
    n = int(mask.sum())
    if n:
        log(f"{tag or '?'} 权源: own-bank 对剔除 {n} 行 (D4 继承, 银行系税调企业 vs 自家银行零泄漏)")
        return longtab[~mask]
    return longtab


# ================================================================ 固定列 (引擎边界外调用方计算)
def fixed_cols_for(longtab: pd.DataFrame, measures: pd.DataFrame,
                   skeleton: pd.MultiIndex) -> pd.DataFrame:
    """rel_n_banks / rel_hhi / rel_wt_base (母本 D18 ② 同式; index 位置式赋值, T-D8)。"""
    import pandas as pd
    lt = longtab.dropna(subset=["w"])
    g = lt.groupby(["company", "year"])
    n_banks = g["bank"].nunique()
    tot = g["w"].sum()
    sh2 = (lt["w"] / lt.set_index(["company", "year"]).index.map(tot).values) ** 2
    hhi = sh2.groupby([lt["company"], lt["year"]]).sum()
    in_panel = pd.MultiIndex.from_frame(lt[["bank", "year"]]).isin(set(measures.index))
    wq = (lt["w"] * in_panel).groupby([lt["company"], lt["year"]]).sum() / tot
    out = pd.DataFrame({"rel_n_banks": n_banks, "rel_hhi": hhi, "rel_wt_base": wq})
    out.index.names = ["company_tax_name", "year"]  # 位置式赋值 (禁旧名字面量参与逻辑)
    out = out.reindex(skeleton)
    out["rel_n_banks"] = out["rel_n_banks"].fillna(0).astype("int32")
    return out


# ================================================================ 互验 (T-D7; 统计原语照搬母本)
def _fold_pairs(w: pd.DataFrame) -> set[tuple[str, str]]:
    return set(map(tuple, w.dropna(subset=["w"])[["company", "bank"]].drop_duplicates().values))


def _shares(w: pd.DataFrame) -> pd.Series:
    """份额 s(c,b) = Σ_t w / Σ_{b',t} w (先窗口求和再算份额, 禁逐年份额取均值 — v33 公式铁律)。"""
    ws = w.dropna(subset=["w"]).groupby(["company", "bank"])["w"].sum()
    tot = ws.groupby(level=0).sum()
    return ws / ws.index.get_level_values(0).map(tot)


def enrichment(pairs_m: set, pairs_alt: set) -> dict:
    """④ 富集度双基准 (均匀 + 边际保持解析式 Σ_b m_b·a_b/(|C|·|pairs_m|), 零随机禁置换)。
    B_m = pair 当窗 distinct bank 全集 (不限共同公司集, 母本 P0-1 修正后口径)。"""
    C = {c for c, _ in pairs_m} & {c for c, _ in pairs_alt}
    pm = {(c, b) for c, b in pairs_m if c in C}
    pa = {(c, b) for c, b in pairs_alt if c in C}
    B_m = {b for _, b in pairs_m}
    if not pm or not pa or not C:
        return {"n/a": True}
    hit = len(pm & pa) / len(pm)
    base_uniform = len(pa & {(c, b) for c in C for b in B_m}) / (len(C) * len(B_m))
    mb: dict[str, int] = {}
    ab: dict[str, int] = {}
    for c, b in pm:
        mb[b] = mb.get(b, 0) + 1
    for c, b in pa:
        ab[b] = ab.get(b, 0) + 1
    base_marg = sum(mb.get(b, 0) * ab.get(b, 0)
                    for b in sorted(set(mb) | set(ab))) / (len(C) * len(pm))  # sorted: HASHSEED 免疫
    return {"n_common_companies": len(C), "n_pairs_m": len(pm), "n_pairs_alt": len(pa),
            "hit_rate": hit, "base_uniform": base_uniform,
            "enrich_uniform": hit / base_uniform if base_uniform > 0 else float("nan"),
            "base_marginal": base_marg,
            "enrich_marginal": hit / base_marg if base_marg > 0 else float("nan")}


def spearman_common(sa: pd.Series, sb: pd.Series) -> tuple[float | None, int]:
    """③ 份额 Spearman — 仅共同支撑口径, 禁 union 补 0。

    返回 None 的两种情形均按 n/a 呈报: ① n<10 (小样本闸); ② ρ 数学未定义
    (任一份额向量在共同支撑上为常数, 如全单银行企业 share≡1 → spearmanr 出 nan;
    透传 nan 会在报告打出 '+nan' 且被 ρ<0 反向证据点名静默漏计)。"""
    import pandas as pd
    common = sa.index.intersection(sb.index)
    if len(common) < 10:
        return None, len(common)
    import warnings

    from scipy.stats import ConstantInputWarning, spearmanr
    with warnings.catch_warnings():
        # ρ 未定义在下方显式归 None (n/a), 常数输入警告为冗余噪音, 定向收掉不遮蔽其它警告
        warnings.simplefilter("ignore", ConstantInputWarning)
        rho, _ = spearmanr(sa.loc[common], sb.loc[common])
    if pd.isna(rho):
        return None, len(common)
    return float(rho), len(common)


def top1_stats(sa: pd.Series, sb: pd.Series) -> dict:
    """⑤ Top-1 同银行率 + 包含率 (argmax, 并列取字典序首)。"""
    def top1(s: pd.Series) -> dict[str, str]:
        d: dict[str, tuple] = {}
        for (c, b), v in s.items():
            cur = d.get(c)
            if cur is None or v > cur[0] or (v == cur[0] and b < cur[1]):
                d[c] = (v, b)
        return {c: b for c, (v, b) in d.items()}
    ta, tb = top1(sa), top1(sb)
    C = set(ta) & set(tb)
    if not C:
        return {"same": None, "n": 0}
    same = sum(ta[c] == tb[c] for c in C) / len(C)
    supp_b = {}
    for c, b in sb.index:
        supp_b.setdefault(c, set()).add(b)
    incl = sum(ta[c] in supp_b.get(c, set()) for c in C) / len(C)
    return {"same": same, "incl_a_in_b": incl, "n": len(C)}


# ================================================================ codebook 双权章 (幂等 section-replace; 标记 SSOT = 税调 02)
def upsert_codebook_section(codebook_path: Path, section_md: str,
                            begin: str, end: str) -> None:
    block = f"{begin}\n{section_md}\n{end}"
    if codebook_path.exists():
        text = codebook_path.read_text(encoding="utf-8")
        if begin in text and end in text:
            pre = text.split(begin)[0]
            post = text.split(end, 1)[1]
            text = pre + block + post
        else:
            text = text.rstrip("\n") + "\n\n" + block + "\n"
    else:
        text = block + "\n"
    codebook_path.write_text(text, encoding="utf-8")


def build_codebook_section(coverage: dict[str, pd.Series], cov_county: dict,
                           n_keyok0: int) -> str:
    lines = [
        "",
        "## 双替代权面板 (T-D5/T-D19⑦, 步骤 03 生成)",
        "",
        "双替代权面板 `company_tax_bank_{branch_city,branch_county}w_panel.{dta,parquet}`",
        "与媒体主面板同引擎同列名 (`cw_/ce_{短名}_{track}`, 同一短名表), scheme 身份由文件名承载",
        "(branch_city=城市网点 / branch_county=县域网点)。",
        "**禁三面板横向 merge 成单文件; 三权 (媒体共现·城市网点·县域网点) 互为稳健性、不分主次,",
        "各自 just-identified 并排, 禁混同一 over-identified Hansen J、禁同一回归 RHS 并置多权重",
        "版本的同名测度**。城/县两权是同一权源 dta 的粒度梯子, 论文端预声明 primary 层级。",
        "",
        "### track 双语义",
        "媒体主面板: 权重逐轨三矩阵。双替代面板: 权重 track-less, `cw_X_{track}` 的 track 含义 =",
        "**测度 X 自身的轨**, 权重恒同一; track-agnostic 测度在替代面板三轨列逐字节恒等",
        "(结构冗余非 bug, 分析端任取一列)。",
        "",
        "### 固定列 (双面板)",
        "| 变量 | 标签 |", "|---|---|",
        "| `company_tax_name` | 税调企业名称 (全称) |",
        "| `usci` | 统一社会信用代码 (18 位; merge 首选键 usci×year) |",
        "| `year` | 年 |",
        "| `is_bank_company` | 银行系税调企业 (D4, 280 家) |",
        "| `rel_n_banks` | {城市/县域}网点权当年支撑银行数 (0 = 无关系, 该行 cw/ce 全缺失) |",
        "| `rel_hhi` | 网点权重集中度 HHI |",
        "| `rel_wt_base` | 网点权重落在银行面板的比例 |",
        "| `county_key_ok` | **仅县权面板**: 1=有效复合键或 (i) 退化键, 0=(ii)/(iii)/境外缺键 |",
        "",
        f"`county_key_ok==0` 共 {n_keyok0:,} 家 (直筒子/零星缺失 {cov_county['n_dash']:,} + "
        f"复合键无匹配 {cov_county['n_eligible'] - cov_county['n_matched']:,} + 境外/空键 "
        f"{cov_county['n_overseas'] + cov_county['n_empty_key']:,} + (i)placeholder退化键落空 "
        f"{cov_county['n_placeholder'] - cov_county['n_placeholder_hit']:,}); 其县权全缺失是**缺键**而非"
        "真零 — 与 `rel_n_banks=0` 的\"城里真无网点\"真零形态在面板端签名相同, 必须以本列区分",
        "(税调名单不可再分发, 复现包使用者无法自行重构该子集, T-D5b)。`county_key_ok==1` 且县权",
        "全缺失 = 合法真零形态 (如全部网点 2011 前退出), 见互验报告 ① 真零企业披露行。",
        "",
        "### 构念与 rel_hhi 披露 (L5)",
        "w = 企业注册地 (城市层=city, placeholder 退 district; 县域层=(city,district) 复合键) 内",
        "该行当年**存续网点数** (存量暴露, shift-share 型本地银行供给代理; 构念差异非质量差异)。",
        "城市层稠密 (母本 rel_hhi≈0.05–0.10 参照), cw_branch_city 近似城市层银行构成均值, 企业 FE",
        "后识别变异仅网点进入退出 (与城市/企业 FE 共线性警示); 县域层键更细、预期更集中 (生产值",
        "以互验报告为准)。存续窗口: ApprovalDate≤t ∧ 非(退出∧QuitDate≤t) ∧ 非(失控∧RunawayDate≤t)。",
        "",
        "### (i) 类城县恒等说明 (T-D5b(i))",
        f"省/自治区直辖县级占位企业 {cov_county['n_placeholder']:,} 家 (石河子/仙桃/潜江等):",
        "分支侧把这些县级市直接记在 CityName、CountyName 为镇/街道级 → 县权对其绕过复合键、走",
        "城市层同款退化键 (公司键=district), **由构造保证城/县两权对这些企业逐 (bank,year) 数值",
        "恒等** (行政区划本身无更细层级, 非 bug; 互验 city×county Spearman 已按企业整体剔除)。",
        "",
        "### 县权结构性缺失 (L3/L4)",
        f"(ii) district=`-` {cov_county['n_dash']:,} 家 (东莞/中山/嘉峪关直筒子为主 + 零星缺失):",
        "县名不可对齐 (分支侧为镇/街道级), 县权全缺失 NaN, **不回退城市层** (回退会让县权复制城权",
        f"污染互稳独立性); (iii) 复合键无匹配 {cov_county['n_eligible'] - cov_county['n_matched']:,} 家",
        "(开发区/高新区等非民政区划为主)。县权回归样本 = \"有真县级区划企业\"子集。县改区/区划变更",
        "错位 (权源快照 vs 税调批次两时点) 计入 B 锚缺口披露, 不建别名表 (L4/§8-N6)。",
        "",
        "### 权源逐年关系对数覆盖表 (真无关系 vs 权源覆盖假零)",
        "| 年 | " + " | ".join(SCHEMES) + " |",
        "|---|" + "---|" * len(SCHEMES),
    ]
    years = sorted({y for s in coverage.values() for y in s.index})
    for y in years:
        lines.append(f"| {y} | " + " | ".join(str(int(coverage[s].get(y, 0))) for s in SCHEMES) + " |")
    lines += [
        "",
        "### 数据谱系 (T-D20 承接; 字段终值生产机轮回填 §6)",
        "权源 = `config/银行业金融机构基本信息表.dta` (603,907 行商业数据, 恒不入库); 谱系七字段",
        "(数据商·数据库名/表编号·版本·获取日期·提取过滤条件·许可条款·第三方获取路径) 核定 DEFERRED。",
        "税调名单 (政府调查数据) 与权源 dta 外部不可得 → 完整重生不可复现, 复现包附 pair 长表 +",
        "双权长表代偿 (派生聚合面板可分发、名单/行级长表按需申请的降级路径)。",
    ]
    return "\n".join(lines)


# ================================================================ WP-S2 后台写盘 join (可测助手)
def _join_background_writes(bg: dict, exc_active: bool, log_err) -> list:
    """join WP-S2 后台 dta 写 future。fail-loud 语义:
    - exc_active=False (主序正常结束) → 任一 bg 写异常直接**上抛** (fail-loud, 不静默吞)。
    - exc_active=True (主序已因先前异常退出, 如 county gate 断言先抛) → bg 写异常仅 log_err **记录不上抛**,
      使**原异常优先**呈现 (防 finally 异常掩盖 root cause; 镜像评审 R2 建议)。
    返回 [(scheme, 后台写秒)] (成功者)。bg 值 = future (须有 .result())。"""
    done = []
    for scheme, fut in bg.items():
        try:
            done.append((scheme, fut.result()))
        except Exception as e:  # noqa: BLE001 — 蓄意宽捕以在复合失败下保原异常优先
            if not exc_active:
                raise
            log_err(f"[WP-S2] {scheme} 后台 dta 写盘失败, 但主序已因先前异常退出 → 原异常优先: {e!r}")
    return done


# ================================================================ 主流程
def main(argv=None) -> int:
    if sys.flags.optimize:  # 本脚本 fail-fast 闸为 assert, -O/PYTHONOPTIMIZE 下会静默失效
        raise SystemExit("禁以 -O/PYTHONOPTIMIZE 运行 (assert 闸失效 → 无防线静默落盘)")
    _init_stage_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch-dta")
    ap.add_argument("--pairs", default=str(OUT_DATA / "_company_tax_bank_cooc_pairs.parquet"))
    ap.add_argument("--input"); ap.add_argument("--panel"); ap.add_argument("--alignment")
    ap.add_argument("--benefit"); ap.add_argument("--controls")
    ap.add_argument("--registry", default=str(CONFIG / "company_tax_bank_cooc_registry.yaml"))
    ap.add_argument("--output-dir", default=str(OUT_DATA))
    ap.add_argument("--year-min", type=int, default=PANEL_YEAR_MIN)
    ap.add_argument("--year-max", type=int, default=PANEL_YEAR_MAX)
    ap.add_argument("--no-emit-dta", action="store_true",
                    help="WP-S3 dev 快速模式: 两 branch 面板跳过 dta 落盘只写 parquet (dev 不可回归; 生产勿用)")
    args = ap.parse_args(argv)
    if args.year_min > args.year_max:
        raise SystemExit(2)
    y0, y1 = args.year_min, args.year_max
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    import time
    t_start = time.monotonic()
    dta_path = Path(args.branch_dta) if args.branch_dta else BRANCH_DTA
    _log_stage_header(Path(args.pairs), Path(args.registry), dta_path, outdir, y0, y1)
    t0 = time.monotonic()

    # SSOT 复用 (T-D1/T-D10, 管道内禁第二份实现); 序号前缀模块名非法 import 标识符 → 走 importlib
    import importlib

    import numpy as np
    import pandas as pd
    import yaml
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    wp1 = importlib.import_module("02_build_company_tax_bank_cooc_panel")
    eng = wp1.engine()  # 跨管道引擎 (listed 02 公司无关件; 只读复用)
    _attach_engine_logging()  # 引擎 budget/chunk WARNING 落本阶段文件日志 (T-D10)

    reg_path = Path(args.registry)
    if not reg_path.exists():  # 显式 SystemExit (兑现头部"缺/stale 即 SystemExit"文案)
        raise SystemExit(f"registry 缺失: {reg_path} — 先跑 WP0 (01_build_company_tax_bank_cooc_registry.py)")
    registry = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    # DV2 常量双向锁 (T-D8): 启动断言自身常量 == registry 区段 (缺/空/不等同为 fail-closed)
    reg_dv2 = registry.get("dv2_constants")
    if not reg_dv2:
        raise SystemExit("registry 缺 dv2_constants 区段 (旧版/空占位 WP0 产物) — 重跑 WP0")
    if reg_dv2 != DV2_CONSTANTS:
        raise SystemExit("DV2_CONSTANTS 与 registry dv2_constants 区段不一致 — 重跑 WP0")
    logger.info("DV2 常量双向锁校验通过: 模块常量 == registry dv2_constants 区段 (%d 键: %s)",
                len(DV2_CONSTANTS), "/".join(sorted(DV2_CONSTANTS)))

    pairs_path = Path(args.pairs)
    if not pairs_path.exists():
        raise SystemExit(f"pair 长表缺失: {pairs_path} (互验以媒体为锚, 无锚即无互验)")
    import pyarrow.parquet as pq
    meta = pq.ParquetFile(pairs_path).schema_arrow.metadata or {}
    reg_sha = (meta.get(b"registry_sha256") or b"").decode()
    if not reg_sha:  # fail-closed: 缺指纹=非 02 正规产物 (02 恒内嵌), 放行即指纹校验形同虚设
        raise SystemExit("pair 长表 metadata 缺 registry_sha256 (被外部工具重写/非 02 产物?) — 先重跑 WP1")
    if reg_sha != registry["meta"]["registry_sha256"]:
        raise SystemExit("pair 长表 registry 指纹与当前 registry 不一致 (stale, 先重跑 WP1)")
    # D8 第二把锁读点 (2026-07-18, 镜像 04 双向锁; 与 listed 03 对称): 21_full 重生而
    # registry sha 不变时, 单锁放行会让 03 静默用旧媒体锚 × 新测度库混代产互验报告。
    pair_fp = (meta.get(b"input_fingerprint") or b"").decode()
    if not pair_fp:  # fail-closed: 02 恒内嵌; 缺失 = 非 02 正规产物
        raise SystemExit("pair 长表 metadata 缺 input_fingerprint (被外部工具重写/非 02 产物?) — 先重跑 02")
    pair = pd.read_parquet(pairs_path)
    logger.info("已加载 pair 长表 %s 行 (registry 指纹校验通过: 内嵌 registry_sha256=%s… == 当前"
                " registry, 媒体锚与测度注册表同代)。", f"{len(pair):,}", reg_sha[:16])
    logger.info("pair 长表 schema: %d 列 = %s (互验仅用 track=='full' 的 canonical n_docs 作媒体锚)",
                len(pair.columns), "/".join(map(str, pair.columns)))
    logger.info("[Memory] 数据加载后 | RSS: %.4g MB", _rss_mb())
    t_load = time.monotonic() - t0
    t0 = time.monotonic()

    canon = BankCanon()
    companies_all, geo = load_companies()
    logger.info("DV2 canonical 化器就绪: variant→canonical 映射 %s 条 | canonical 银行 %s 家 | "
                "判定序 = ⓪₀缺失闸 → ⓪不可名指(%d 词) → ①精确查表(原名/剥公司后缀/括注规则) → "
                "境外闸(%d 国家地区词+%d 法人尾缀, head 内豁免 8 家) → ②泛称(%d 词)/尾段黑名单(%d 词) → "
                "截断剥分支行 → ③未映射审计 (memo 缓存)",
                f"{len(canon.variant_to_canon):,}", f"{len(canon.canonicals):,}",
                len(DV2_CONSTANTS["unnameable"]), len(DV2_CONSTANTS["overseas_words"]),
                len(DV2_CONSTANTS["foreign_suffixes"]), len(DV2_CONSTANTS["generic_heads"]),
                len(DV2_CONSTANTS["affiliate_tail"]))
    logger.info("税调企业名单载入 (T-D1 SSOT): %s 家 | 地理键 (city/district) 全填 | 规模锚 = "
                "%s × %d 年 = %s 面板行", f"{len(companies_all):,}", f"{len(companies_all):,}",
                y1 - y0 + 1, f"{len(companies_all) * (y1 - y0 + 1):,}")

    # ---- 单点读表 + 公共规范化 + 分臂 (T-D5)
    if not dta_path.exists():
        raise SystemExit(f"权源 dta 缺失: {dta_path} (税调唯一权源, 缺则双权全无 — 不可优雅跳过)")
    import pyreadstat
    logger.info("―― 权源构建: 单点读表 %s (usecols=%d 列) → 公共规范化段 → 城县两 builder 分臂 ――",
                dta_path.name, len(DTA_USECOLS))
    _ts = time.monotonic()
    raw_df, _ = pyreadstat.read_dta(str(dta_path), usecols=DTA_USECOLS)
    b, prep_stats = prepare_branch_frame(raw_df, canon)
    del raw_df
    # 逐年存续计数表: 城 (city×bank×year) 与 县 (city×county×bank×year) 共用同一 b/alive 式;
    # (i) 类企业的县权走 net_city 同表同式 merge → 城县恒等由构造保证 (T-D5b(i))
    b_city = b[b["city"] != ""]
    b_comp = b[(b["city"] != "") & (b["county"] != "")]  # 空键行剔除 (封死空键假匹配, 计量 P1-4)
    net_city = yearly_counts(b_city[["bank", "city", "ap", "quit", "run", "status"]],
                             ["city"], y0, y1)
    net_comp = yearly_counts(b_comp[["bank", "city", "county", "ap", "quit", "run", "status"]],
                             ["city", "county"], y0, y1)
    branch_city_keys = set(b_city["city"])
    branch_comp_keys = set(map(tuple, b_comp[["city", "county"]].drop_duplicates().values))
    logger.info("分支逐年存续网点计数: 城市×银行×年 %s 格 | (城,县)×银行×年 %s 格 (年窗 %d–%d "
                "逐年重算存续: approval≤t ∧ 非(退出∧quit≤t) ∧ 非(失控∧run≤t)) | 网点侧键集: "
                "城 %s 种 / (城,县) 复合 %s 种",
                f"{len(net_city):,}", f"{len(net_comp):,}", y0, y1,
                f"{len(branch_city_keys):,}", f"{len(branch_comp_keys):,}")

    longtabs: dict[str, pd.DataFrame] = {}
    longtabs["branch_city"], cov_city = build_weight_branch_city(geo, net_city, branch_city_keys)
    logger.info("branch_city 长表构建完成 (%.4g 秒累计含读表): %s 行", time.monotonic() - _ts,
                f"{len(longtabs['branch_city']):,}")
    longtabs["branch_county"], cov_county, county_key_ok = build_weight_branch_county(
        geo, net_city, net_comp, branch_city_keys, branch_comp_keys)
    logger.info("branch_county 长表构建完成: %s 行 (复合键匹配 %s 家 + (i) 退化键 %s 家; "
                "(ii) %s / (iii) %s 家无行)", f"{len(longtabs['branch_county']):,}",
                f"{cov_county['n_matched']:,}", f"{cov_county['n_placeholder']:,}",
                f"{cov_county['n_dash']:,}", f"{cov_county['n_eligible'] - cov_county['n_matched']:,}")
    del net_comp

    # own-bank 长表落盘即已剔 (D4 继承)
    for k in list(longtabs):
        longtabs[k] = drop_own_bank(longtabs[k], registry, tag=k)
        assert len(longtabs[k]) > 0, f"{k} 权长表为空 (SystemExit 级锚)"
        longtabs[k].to_parquet(outdir / f"_company_tax_bank_altweights_{k}.parquet")
        logger.info("%s 长表落盘: %s 行 (企业 %s × 银行 %s) → _company_tax_bank_altweights_%s.parquet"
                    " | 稳健臂列: 无 (单臂权源, ROBUST_ARM_COLS=[])", k, f"{len(longtabs[k]):,}",
                    f"{longtabs[k]['company'].nunique():,}", f"{longtabs[k]['bank'].nunique():,}", k)

    # (i) 类两权逐 (bank,year) 恒等自检 (T-D5b(i) 构造保证的运行时证据; own-bank 剔除后口径)
    ph_set = cov_county["placeholder_companies"]
    a_ph = (longtabs["branch_city"][longtabs["branch_city"]["company"].isin(ph_set)]
            .sort_values(["company", "bank", "year"]).reset_index(drop=True))
    c_ph = (longtabs["branch_county"][longtabs["branch_county"]["company"].isin(ph_set)]
            .sort_values(["company", "bank", "year"]).reset_index(drop=True))
    assert a_ph[["company", "bank", "year", "w"]].equals(c_ph[["company", "bank", "year", "w"]]), \
        "(i) 类占位企业城/县两权长表不恒等 (T-D5b(i) 构造保证破)"
    logger.info("(i) 类恒等自检通过: %s 家占位企业城/县两权长表逐 (company,bank,year,w) 精确相等 "
                "(%s 行; net_city 同表同式 merge 构造保证)", f"{len(ph_set):,}", f"{len(a_ph):,}")

    # ---- 覆盖锚 (T-D6, 城县分设 SystemExit 级; A/B 共用 keyed 分母)
    nz_city = longtabs["branch_city"]["company"].nunique() / max(cov_city["n_keyed"], 1)
    if nz_city < 0.90:
        raise SystemExit(f"branch_city 覆盖锚 A: 非零权企业占比 {100 * nz_city:.4g}% < 90%")
    if cov_city["hit_rate"] < 0.995:
        raise SystemExit(f"branch_city 覆盖锚 B: 城市键命中率 {100 * cov_city['hit_rate']:.4g}% "
                         f"< 99.5% (双侧去市尾/T-D5c 回退疑失效)")
    logger.info("branch_city 覆盖锚 A∧B 实测: A 非零权企业占比 %.4g%% (≥90%% ✓) | B 城市键命中率 "
                "%.4g%% (≥99.5%% ✓, T-P0-2 参照=100.0000%%) | keyed 分母 %s 家 (剔境外/空键 %s)",
                100 * nz_city, 100 * cov_city["hit_rate"], f"{cov_city['n_keyed']:,}",
                f"{cov_city['n_overseas_missing']:,}")
    nz_county = longtabs["branch_county"]["company"].nunique() / max(cov_county["n_keyed"], 1)
    if nz_county < 0.85:
        raise SystemExit(f"branch_county 覆盖锚 A: 非零权企业占比 {100 * nz_county:.4g}% < 85%")
    if cov_county["hit_rate"] < 0.995:
        raise SystemExit(f"branch_county 覆盖锚 B: 复合键命中率 {100 * cov_county['hit_rate']:.4g}% "
                         f"< 99.5% (T-P0-2 参照=99.9042%)")
    logger.info("branch_county 覆盖锚 A∧B 实测: A 非零权企业占比 %.4g%% (≥85%% ✓) | B 复合键命中率 "
                "%.4g%% (≥99.5%% ✓; 命中 = 复合键 %s + (i) 退化键 %s, 缺口 = (iii) %s 家) | "
                "keyed 分母 %s 家 (= 全量 %s − (ii) %s − 境外/空键 %s; (iii) 留分母诚实计缺口)",
                100 * nz_county, 100 * cov_county["hit_rate"], f"{cov_county['n_matched']:,}",
                f"{cov_county['n_placeholder_hit']:,}",
                f"{cov_county['n_eligible'] - cov_county['n_matched']:,}",
                f"{cov_county['n_keyed']:,}", f"{cov_county['n_total']:,}",
                f"{cov_county['n_dash']:,}",
                f"{cov_county['n_overseas'] + cov_county['n_empty_key']:,}")
    n_keyok0 = sum(1 for v in county_key_ok.values() if v == 0)
    _iii = cov_county["n_eligible"] - cov_county["n_matched"]
    _ph_miss = cov_county["n_placeholder"] - cov_county["n_placeholder_hit"]  # (i) placeholder 退化键落空
    _oe = cov_county["n_overseas"] + cov_county["n_empty_key"]
    # 穷尽互斥 5 桶 (county_key_ok = matched | ph_hit; key_ok==0 = 非 matched ∧ 非 ph_hit):
    #   (ii)dash + (iii)eligible未匹配 + 境外+空键 + (i)placeholder退化键落空 (R2 补第 4 桶 + fail-loud)
    assert n_keyok0 == cov_county["n_dash"] + _iii + _oe + _ph_miss, (
        f"county_key_ok==0 分解不闭合: {n_keyok0} != dash {cov_county['n_dash']} + (iii) {_iii} "
        f"+ 境外/空键 {_oe} + placeholder落空 {_ph_miss} — 分区非穷尽或有重复")
    logger.info("county_key_ok 家数 (运行时实数, 禁硬锚): key_ok==0 共 %s 家 (运行时分解 = (ii) %s "
                "+ (iii) %s + 境外/空键 %s + (i)placeholder退化键落空 %s) | key_ok==1 共 %s 家",
                f"{n_keyok0:,}", f"{cov_county['n_dash']:,}", f"{_iii:,}", f"{_oe:,}",
                f"{_ph_miss:,}", f"{len(county_key_ok) - n_keyok0:,}")

    # ---- 测度库一次构建双面板复用 (T-D10 单引擎)
    dp = eng.default_paths()

    def resolve(name: str, required: bool = False) -> Path | None:
        given = getattr(args, name)
        if given:
            path = Path(given)
            if not path.exists():
                raise SystemExit(f"显式传参 --{name} 路径不存在: {path}")
            return path
        path = dp[name]
        if not path.exists():
            if required:
                raise SystemExit(f"必需上游缺失: {path}")
            log(f"默认路径缺失 {path.name} → 对应族全缺失列", warn=True)
            return None
        return path

    p_input = resolve("input", required=True)
    p_panel = resolve("panel", required=True)
    p_align, p_benefit, p_controls = resolve("alignment"), resolve("benefit"), resolve("controls")
    input21 = eng.load_input21(p_input, canon.canonicals)
    # D8 第二把锁复算 (2026-07-18): size 取 03 实际载入的 p_input (resolve 支持 --input
    # 覆盖); rows 取本次 len(input21)。⚠ 必须在下方 del input21 之前完成 (T-D13 释放)。
    import hashlib as _hashlib
    _fp_now = _hashlib.sha256(f"{p_input.stat().st_size}|{len(input21)}".encode()).hexdigest()
    if pair_fp != _fp_now:
        raise SystemExit(f"pair 长表 input_fingerprint ({pair_fp[:16]}…) 与现场 21_full "
                         f"({_fp_now[:16]}…) 不同代 — 先重跑 02 (禁旧媒体锚×新测度混代)")
    logger.info("pair 双向锁通过 (03): registry sha 同代 ✓ + input_fingerprint 同代 ✓ (%s…)",
                _fp_now[:16])
    panel40 = pd.read_parquet(p_panel)
    align = pd.read_parquet(p_align) if p_align else None
    benefit = pd.read_parquet(p_benefit) if p_benefit else None
    controls = pd.read_parquet(p_controls) if p_controls else None
    measures = eng.build_measure_library(input21, panel40, align, benefit, controls, registry)
    del panel40, align, benefit, controls, input21  # T-D13: merge/写盘间显式释放
    logger.info("银行×年测度库一次构建 (单引擎多权源, 双面板共用禁重复实现): %s 键 × %s 列 "
                "(SSOT 函数 import 自税调 02 → listed 02 引擎)",
                f"{len(measures):,}", f"{len(measures.columns):,}")

    skeleton = pd.MultiIndex.from_product([companies_all, range(y0, y1 + 1)],
                                          names=["company_tax_name", "year"])
    bank_company_set = set(registry["bank_company_map"])

    # ---- 双面板批量生产 (WP-S2: branch_city 写盘后台线程与 branch_county 引擎部分重叠; 禁同持两面板)
    from concurrent.futures import ThreadPoolExecutor
    emit_dta = not args.no_emit_dta
    wp1.usci_map()  # WP-S2 预热: 单线程首建 usci 惰性全局, 防 city 后台线程与 county 主线程并发双建 (无锁全局)
    coverage: dict[str, pd.Series] = {}
    panel_shapes: dict[str, tuple] = {}
    _write_pool = ThreadPoolExecutor(max_workers=1)
    _bg_writes: dict[str, object] = {}  # scheme -> future (仅 branch_city; panel 经闭包默认参存活至 join)
    try:
        for scheme in SCHEMES:
            _tp = time.monotonic()
            lt = longtabs[scheme]
            coverage[scheme] = lt.dropna(subset=["w"]).groupby("year").size()
            weights = lt[["company", "bank", "year", "w"]]  # 引擎入口四列 (track-less → 三轨广播)
            weighted = eng.compute_weighted_panel(weights, measures, registry)
            fixed = fixed_cols_for(lt, measures, skeleton)
            panel = fixed.reset_index()
            panel["is_bank_company"] = panel["company_tax_name"].isin(bank_company_set).astype("int8")
            panel["year"] = panel["year"].astype("int16")
            cols = ["company_tax_name", "year", "is_bank_company",
                    "rel_n_banks", "rel_hhi", "rel_wt_base"]
            fixed_labels = {
                "company_tax_name": "税调企业名称 (全称)", "year": "年",
                "is_bank_company": "银行系税调企业 (D4, 280 家)",
                "rel_n_banks": f"{SCHEME_LABEL_WORD[scheme]}权当年支撑银行数",
                "rel_hhi": f"{SCHEME_LABEL_WORD[scheme]}权重集中度HHI",
                "rel_wt_base": f"{SCHEME_LABEL_WORD[scheme]}权重落在银行面板比例"}
            if scheme == "branch_county":
                panel["county_key_ok"] = (panel["company_tax_name"].map(county_key_ok)
                                          .fillna(0).astype("int8"))
                cols.append("county_key_ok")
                fixed_labels["county_key_ok"] = "县级键有效性 (1=有效复合键或退化键; 0=缺键, 县权缺失非真零)"
            panel = panel[cols]
            panel = panel.merge(weighted, how="left", left_on=["company_tax_name", "year"],
                                right_index=True)
            _t_engine = time.monotonic()
            # 面板批量 gate (母本 DV6 末段 + 县权 T-D5b 单向 gate)
            assert len(panel) == len(skeleton), f"{scheme} 面板行数 ≠ 骨架 (乘式 {len(skeleton):,})"
            cwce = [c for c in panel.columns if c.startswith(("cw_", "ce_"))]
            zero = panel["rel_n_banks"] == 0
            assert panel.loc[zero, cwce].isna().all().all(), f"{scheme}: rel_n_banks=0 行出现非缺失 cw/ce"
            assert panel[cwce].notna().any().any(), f"{scheme} 面板全缺失 (SystemExit 级锚)"
            hhi = panel["rel_hhi"].dropna()
            assert ((hhi > 0) & (hhi <= 1 + 1e-12)).all(), f"{scheme}: rel_hhi 值域违例"
            single = panel[(panel["rel_n_banks"] == 1) & panel["rel_hhi"].notna()]
            assert np.isclose(single["rel_hhi"], 1.0).all(), f"{scheme}: 单银行 rel_hhi ≠ 1"
            for e in registry["entries"]:
                if not e["emit_panel"] or e["range_gate"] == "none":
                    continue
                lo, hi = (-1.0, 1.0) if e["range_gate"] == "tone" else (0.0, 1.0)
                for t in e["emit_tracks"]:
                    col = f"cw_{e['basename']}_{t}"
                    if col in panel.columns:
                        v = panel[col].dropna()
                        if len(v):
                            assert (v >= lo - 1e-9).all() and (v <= hi + 1e-9).all(), \
                                f"{scheme}: 值域违例 {col}"
            if scheme == "branch_county":
                # county_key_ok 单向 gate (T-D5b; 禁双向 — key_ok==1 且全缺失是合法真零形态)
                bad_rows = panel.loc[panel["county_key_ok"] == 0, "rel_n_banks"]
                assert (bad_rows == 0).all(), "county_key_ok==0 企业出现非零县权 (单向 gate 破)"
                log(f"  gate(县) county_key_ok 单向断言: ==0 的 {n_keyok0:,} 家企业县权全缺失 "
                    f"(rel_n_banks≡0 ⇒ cw/ce 全 NaN) ✓; ==1 且全缺失者归真零披露 (互验①)")
            _t_gate = time.monotonic()
            out_dta = outdir / f"company_tax_bank_{scheme}w_panel.dta"
            n_nonzero = int((panel["rel_n_banks"] > 0).sum())
            panel_shapes[scheme] = (len(panel), len(panel.columns) + 1)  # +1 = write_outputs usci 注入
            _gatetail = ("骨架行数/零关系全缺失/全缺失锚/rel_hhi 值域+单银行==1/registry 值域"
                         + ("/county_key_ok 单向" if scheme == "branch_county" else "") + " 全过")
            _head = (f"{scheme} 面板: {len(panel):,} 行 × {len(panel.columns) + 1} 列 (含 usci 单点注入) "
                     f"→ {out_dta.name}")
            _cov = (f" | 有关系企业×年格 {n_nonzero:,} ({100 * n_nonzero / len(panel):.4g}%) "
                    f"| 批量 gate: {_gatetail}")
            if scheme == "branch_city":  # WP-S2: 后台写盘, 与 branch_county 引擎部分重叠 (write_dta 持 GIL,
                # 靠主线程 county 引擎 pandas/numpy 释放 GIL 实现部分重叠; panel 经闭包默认参存活至 join)
                def _timed_write(_p=panel, _od=out_dta, _sw=SCHEME_LABEL_WORD[scheme],
                                 _fl=fixed_labels, _emit=emit_dta):
                    _t0 = time.monotonic()
                    wp1.write_outputs(_p, registry, _od, scheme_word=_sw, fixed_labels=_fl, emit_dta=_emit)
                    return time.monotonic() - _t0
                _bg_writes[scheme] = _write_pool.submit(_timed_write)
                log(f"{_head} (引擎加权 {_t_engine - _tp:.4g}s + 批量 gate {_t_gate - _t_engine:.4g}s "
                    f"+ dta 写盘→后台线程 [WP-S2, 与 branch_county 引擎重叠]){_cov}")
                del weighted, fixed  # panel 经闭包存活至 join; weighted(~6.4GB 宽帧)/fixed 立即释放
            else:  # branch_county: 同步写盘 (其后仅互验 ~14s, 无可重叠对象)
                wp1.write_outputs(panel, registry, out_dta, scheme_word=SCHEME_LABEL_WORD[scheme],
                                  fixed_labels=fixed_labels, emit_dta=emit_dta)
                _elp = time.monotonic() - _tp
                log(f"{_head} ({_elp:.4g} 秒 = 引擎加权 {_t_engine - _tp:.4g} + 批量 gate "
                    f"{_t_gate - _t_engine:.4g} + dta 写盘 {time.monotonic() - _t_gate:.4g}, 吞吐 "
                    f"{len(panel) / max(_elp, 1e-9):.4g} 行/秒){_cov}")
                del panel, weighted, fixed  # T-D13 串行释放
                logger.info("[Memory] %s 面板落盘后 | RSS: %.4g MB", scheme, _rss_mb())
    finally:
        # WP-S2 join: 主序正常结束→bg 写异常 fail-loud 上抛; 主序已异常→bg 异常记录不掩盖原异常。
        # shutdown 先于 join 循环 (wait=True 阻塞等 city 写完), 确保 join 上抛时线程池仍被清理 (WP-S2-f)。
        _exc_active = sys.exc_info()[0] is not None
        _write_pool.shutdown(wait=True)
        for _sc, _wsec in _join_background_writes(_bg_writes, _exc_active, logger.error):
            logger.info("[WP-S2] %s dta 后台写盘完成: %.4g 秒 (与 branch_county 引擎重叠) | RSS: %.4g MB",
                        _sc, _wsec, _rss_mb())
        logger.info("[Memory] 双面板全部落盘/join 完成 | RSS: %.4g MB", _rss_mb())

    # ---- 三权互验报告 (T-D7)
    mp = pair[pair["track"] == "full"].rename(columns={"n_docs": "w"})
    media_pairs = _fold_pairs(mp)
    media_shares = _shares(mp)
    media_yearly = mp.dropna(subset=["w"]).groupby("year").size()
    alt_pairs = {k: _fold_pairs(v) for k, v in longtabs.items()}
    alt_shares = {k: _shares(v) for k, v in longtabs.items()}
    # (i) 类整体剔除后的份额 (city×county 跨粒度收敛效度专用, T-D7③)
    shares_noph = {k: _shares(v[~v["company"].isin(ph_set)]) for k, v in longtabs.items()}
    logger.info("―― 互验 T-D7 件套计算 (媒体锚 = pair 长表 canonical n_docs full 轨: "
                "%s (c,b) 对 / %s 企业 / %s 银行) ――", f"{len(media_pairs):,}",
                f"{len({c for c, _ in media_pairs}):,}", f"{len({b for _, b in media_pairs}):,}")

    # 真零企业披露 (T-D5b: key_ok==1 且县权全缺失 = 合法真零, 与缺键区分)
    n_truezero_county = len({c for c, v in county_key_ok.items() if v == 1}
                            - set(longtabs["branch_county"]["company"].unique()))
    rl = ["# 三权互验报告 (WP5 / T-D7)", "",
          f"窗口 {y0}–{y1}; 媒体锚 = pair 长表 canonical n_docs full 轨 (刻意不用 _v — verified "
          "门控属测度层, 互验锚取存档全量口径)。三权 = 媒体共现 (media) / 城市网点 (branch_city) / "
          "县域网点 (branch_county), 互为稳健性、不分主次, 各自 just-identified 并排, "
          "禁混同一 over-identified Hansen J。", "",
          "## ① 覆盖概览", "| 权源 | 企业数 | 银行数 | (c,b) 对数 |", "|---|---|---|---|"]
    for k, ps in [("media", media_pairs)] + [(s, alt_pairs[s]) for s in SCHEMES]:
        rl.append(f"| {k} | {len({c for c, _ in ps})} | {len({b for _, b in ps})} | {len(ps)} |")
    rl += ["", "### 逐年关系对数表 (rel_n_banks=0 可判\"真无关系 vs 权源覆盖假零\")",
           "| 年 | media | " + " | ".join(SCHEMES) + " |",
           "|---|---|" + "---|" * len(SCHEMES)]
    for y in range(y0, y1 + 1):
        rl.append(f"| {y} | {int(media_yearly.get(y, 0))} | "
                  + " | ".join(str(int(coverage[s].get(y, 0))) for s in SCHEMES) + " |")
    rl += ["",
           f"真零企业披露行: 县权 `county_key_ok==1` 且窗口内县权全缺失的企业 **{n_truezero_county} 家**"
           " (有效键但辖区内无任何 canonical 银行存续网点 — 合法真零形态, 非缺键; 缺键企业见 "
           f"`county_key_ok==0` 共 {n_keyok0} 家)。"]
    logger.info("互验① 覆盖概览: media %s 对 | branch_city %s 对 | branch_county %s 对 | "
                "县权真零企业 %s 家 (key_ok==1 且全缺失) / 缺键 %s 家 (key_ok==0)",
                f"{len(media_pairs):,}", f"{len(alt_pairs['branch_city']):,}",
                f"{len(alt_pairs['branch_county']):,}", f"{n_truezero_county:,}", f"{n_keyok0:,}")

    # ② city×county 支撑对比 (两替代权皆稠密 → 整段替换母本稀疏权两两件, 标注稠密语义)
    Cc = {c for c, _ in alt_pairs["branch_city"]} & {c for c, _ in alt_pairs["branch_county"]}
    pa_ = {(c, x) for c, x in alt_pairs["branch_city"] if c in Cc}
    pb_ = {(c, x) for c, x in alt_pairs["branch_county"] if c in Cc}
    rl += ["", "## ② 城×县支撑对比 (双稠密权; 母本稀疏权两两重合件整段替换, T-D7②)",
           "| 对比 | P(∈县|∈城) | Jaccard | 共见企业 |", "|---|---|---|---|"]
    if pa_ and pb_:
        rl.append(f"| branch_city×branch_county | {len(pa_ & pb_) / len(pa_):.3f} | "
                  f"{len(pa_ & pb_) / len(pa_ | pb_):.3f} | {len(Cc)} |")
        logger.info("互验② 城×县支撑对比: P(∈县|∈城)=%.4g | Jaccard=%.4g | 共见企业 %s 家",
                    len(pa_ & pb_) / len(pa_), len(pa_ & pb_) / len(pa_ | pb_), f"{len(Cc):,}")
    rl += ["",
           "稠密语义标注: 两权皆由网点存续机械展开 (非稀疏注册关系), 支撑重合高属构造预期 — 县⊂城的"
           "包含率反映粒度收紧的信息增量 (P(∈县|∈城) 越低于 1, 县级键的区分度越高), 不作收敛效度证据; "
           "收敛效度以 ③④⑤ 对媒体锚为准。"]

    # ③ 份额 Spearman 三行 (共同支撑, 禁 union 补零; 份额=先窗口求和; ρ 未定义归 n/a)
    rl += ["", "## ③ 份额 Spearman (共同支撑口径, 禁 union 补 0; 份额 = 先窗口求和再算)",
           "| 对 | ρ | n 共同对 |", "|---|---|---|"]
    spearman_neg = []
    sp_rows = [("media×branch_city", media_shares, alt_shares["branch_city"]),
               ("media×branch_county", media_shares, alt_shares["branch_county"]),
               ("branch_city×branch_county", shares_noph["branch_city"],
                shares_noph["branch_county"])]
    for tag, sa, sb in sp_rows:
        rho, n = spearman_common(sa, sb)
        rl.append(f"| {tag} | {'n/a' if rho is None else f'{rho:+.3f}'} | {n} |")
        logger.info("互验③ 份额 Spearman %s: ρ=%s (共同支撑 n=%d 对)", tag,
                    "n/a (n<10 或 ρ 未定义)" if rho is None else f"{rho:+.4g}", n)
        if rho is not None and rho < 0:
            spearman_neg.append(f"{tag} (ρ={rho:+.4g}, n={n})")
    rl += ["",
           f"city×county 行为跨粒度收敛效度; **(i) 类省直辖占位企业 {len(ph_set)} 家已按企业整体"
           "剔除** (其两权向量逐格恒等, 按对剔无意义 — 剔除数点名披露, T-D7③)。"]
    if spearman_neg:
        rl.append("")
        rl.append(f"⚠ 反向证据点名: {'; '.join(spearman_neg)} — 份额 Spearman 为负 "
                  "(dev 共同支撑对数小, 方向定谳以生产复跑为准)。")

    # ④ 富集度双基准 media→{city,county} (+反向方向并报; gate 按均匀基准 1.5× 前向)
    rl += ["", "## ④ 富集度 (双基准; 叙事以边际保持版为准, gate 按均匀基准 1.5×)",
           "(富集倍数按未舍入底数计算, 用表内 4 位小数机械复算存在尾差属预期)",
           "| 方向 | 命中率 | 均匀基准 | 富集(均匀) | 边际保持基准 | 富集(边际保持) |",
           "|---|---|---|---|---|---|"]
    warn_schemes = []
    marg_below = []
    for s in SCHEMES:
        fwd = enrichment(media_pairs, alt_pairs[s])
        rev = enrichment(alt_pairs[s], media_pairs)
        for tag, e in ((f"media→{s}", fwd), (f"{s}→media", rev)):
            if e.get("n/a"):
                rl.append(f"| {tag} | n/a | | | | |")
                logger.info("互验④ 富集度 %s: n/a (共见宇宙空)", tag)
                continue
            rl.append(f"| {tag} | {e['hit_rate']:.3f} | {e['base_uniform']:.4f} | "
                      f"{e['enrich_uniform']:.2f}× | {e['base_marginal']:.4f} | "
                      f"{e['enrich_marginal']:.2f}× |")
            logger.info("互验④ 富集度 %s: 命中率 %.4g | 均匀基准 %.4g → %.4g× | "
                        "边际保持基准 %.4g → %.4g× (叙事以边际保持为准; 共见企业 %d)",
                        tag, e["hit_rate"], e["base_uniform"], e["enrich_uniform"],
                        e["base_marginal"], e["enrich_marginal"], e["n_common_companies"])
            if e["enrich_marginal"] < 1.0:  # nan 比较恒 False, 自动排除
                marg_below.append(tag)
        if not fwd.get("n/a") and fwd["enrich_uniform"] < 1.5:
            warn_schemes.append(s)
    if warn_schemes:
        rl.append("")
        rl.append(f"⚠ WARNING: {warn_schemes} 均匀基准富集度 <1.5× — 待生产复审 (dev 不判失败)。")
        for s in warn_schemes:
            log(f"富集度方向锚 <1.5× (均匀口径): {s} — 待生产复审", warn=True)
    if marg_below:
        rl.append("")
        rl.append(f"⚠ 反向证据点名: {'/'.join(marg_below)} — 边际保持富集 <1× "
                  "(叙事判据的反向证据; dev 共同支撑极小, 方向定谳以生产复跑为准)。")

    # ④b 媒体对篇数按有无权源关系分组均值差 (收敛效度第三件)
    rl += ["", "## ④b 媒体对篇数按有无权源关系分组均值差 (收敛效度第三件)",
           "| 权源 | 有关系媒体对均值 n_docs | 无关系媒体对均值 | 比值 | 有关系对数 |",
           "|---|---|---|---|---|"]
    media_ndocs = mp.groupby(["company", "bank"])["w"].sum()
    meandiff_below = []
    for s in SCHEMES:
        in_rel = media_ndocs.index.isin(alt_pairs[s])
        if in_rel.any() and (~in_rel).any():
            a_mean, b_mean = media_ndocs[in_rel].mean(), media_ndocs[~in_rel].mean()
            ratio = a_mean / b_mean
            rl.append(f"| {s} | {a_mean:.4g} | {b_mean:.4g} | {ratio:.4g}× | {int(in_rel.sum())} |")
            logger.info("互验④b 篇数均值差 %s: 有权源关系媒体对均值 %.4g vs 无关系 %.4g = %.4g× "
                        "(有关系对 %d)", s, a_mean, b_mean, ratio, int(in_rel.sum()))
            if ratio < 1.0:
                meandiff_below.append(f"{s} ({ratio:.4g}×, 有关系对 {int(in_rel.sum())})")
    if meandiff_below:
        rl.append("")
        rl.append(f"⚠ 反向证据点名: {'; '.join(meandiff_below)} — 有权源关系媒体对篇数均值低于无关系对 "
                  "(dev 有关系对数小, 方向定谳以生产复跑为准)。")

    # ⑤ Top-1 同银行率 / 包含率
    rl += ["", "## ⑤ Top-1 同银行率 / 包含率",
           "| media×权源 | 同银行率 | media Top1 ∈ 权源支撑 | n |", "|---|---|---|---|"]
    for s in SCHEMES:
        st = top1_stats(media_shares, alt_shares[s])
        if st["n"]:
            rl.append(f"| media×{s} | {st['same']:.3f} | {st['incl_a_in_b']:.3f} | {st['n']} |")
            logger.info("互验⑤ Top-1 media×%s: 同银行率 %.4g | media Top1 ∈ 权源支撑 %.4g (n=%d; "
                        "低同银行率 = 三权测不同构念的实证)", s, st["same"], st["incl_a_in_b"], st["n"])

    # ⑥ 顶刊披露包 (a)–(e) + 反向证据三件套逐权
    rl += [
        "", "## ⑥ 顶刊效度证据与披露包",
        "(a) 富集度 = 收敛效度证据 (信号存在性), **禁写 \"validated against credit relationships\"**;",
        "措辞钉死 = \"captures real relationships at N× random baseline while measuring a distinct",
        "construct\"; 必并报 {均匀值, 边际保持值, precision 绝对水平} 三件, 叙事以边际保持基准为准",
        "(机械边际集中已扣除)。",
        "(b) 推断地位钉死: 三权 specification-curve 属**描述性**证据; 假设检验以预声明 primary 单臂",
        "为准, 禁挑臂单报; 三权免 FWER 的归类依据 = 规格稳健性并排 (三权测量不同关系构念上的暴露,",
        "非同构念替代 headline 测量, Top-1 低同银行率为实证), 落字于此。城/县两权是同一权源的粒度",
        "梯子, 论文端预声明 primary 层级。",
        "(c)❶ 媒体权共源反射通道 (cw 权重与被加权测度同源语料机械相关) 处方 = 重叠占比",
        "n_cooc/n_articles 分位披露 + leave-company-out 扩展臂提示; ❷ 分支稠密权 + 企业 FE 后识别",
        "变异 = 网点进入退出 (与城市/企业 FE 共线性警示); 双权全部内生 — frozen-share 基期份额/",
        "等权 ce 臂 (仅对冲规模假设)/企业与年 FE/exposure-robust SE (AKM 2019) 逐条适用。",
        "(d) 存量/流量构念差异: 网点权 = 存续网点数的**存量暴露** (2026 快照区划键, 历史迁址按现址",
        "计); 媒体共现权 = 报道流量覆盖。县权另有结构性缺失 (§7-L3: (ii) 直筒子 + (iii) 开发区) 与",
        "县改区错位 (L4, 计入 B 锚缺口不建别名表)。",
        "(e) 数据谱系: 权源 dta 谱系七字段 + 税调名单许可地位 (政府调查数据, 名单/行级长表按需申请、",
        "派生聚合面板可分发的降级路径) — 终值生产机轮回填 (§6 DEFERRED); 第三方获取路径以 codebook",
        "谱系段为准。",
        "",
        "### 反向证据三件套 (逐权点名; 与富集度 <1× 同标准)",
        f"- 份额 Spearman ρ<0: {'; '.join(spearman_neg) if spearman_neg else '无'}",
        f"- 边际保持富集 <1×: {'/'.join(marg_below) if marg_below else '无'}",
        f"- 篇数均值差 <1×: {'; '.join(meandiff_below) if meandiff_below else '无'}",
        "", "## 未映射审计附录 (top-50 频次)",
        "| 名称 | 频次 |", "|---|---|"]
    for name, cnt in sorted(canon.audit.items(), key=lambda kv: -kv[1])[:50]:
        rl.append(f"| {name} | {cnt} |")
    top10 = sorted(canon.audit.items(), key=lambda kv: -kv[1])[:10]
    logger.info("DV2 未映射审计: %s 种名称 (合计 %s 次; 全量留痕无静默丢弃) | top-10: %s",
                f"{len(canon.audit):,}", f"{sum(canon.audit.values()):,}",
                {k: v for k, v in top10})
    t_build = time.monotonic() - t0
    t0 = time.monotonic()
    logger.info("正在将互验报告与 codebook 双权章写入 %s...", outdir)
    (outdir / "_company_tax_bank_weight_validation.md").write_text("\n".join(rl) + "\n",
                                                                   encoding="utf-8")
    # codebook 双权章 (幂等 section-replace; 成对标记字面量 SSOT = 税调 02, 禁第二份拼法)
    upsert_codebook_section(outdir / "company_tax_bank_cooc_panel_codebook.md",
                            build_codebook_section(coverage, cov_county, n_keyok0),
                            wp1.CODEBOOK_ALT_BEGIN, wp1.CODEBOOK_ALT_END)
    t_write = time.monotonic() - t0

    # 统计报告 + 结果分析 (格式参照 12_news_fintech.log)
    logger.info("=" * 70)
    logger.info("===      双替代权源构建与三权互验统计报告      ===")
    logger.info("=" * 70)
    for k in longtabs:
        logger.info("权源 %-13s: 长表 %s 行 | 企业 %s 家 | 银行 %s 家", k,
                    f"{len(longtabs[k]):,}", f"{longtabs[k]['company'].nunique():,}",
                    f"{longtabs[k]['bank'].nunique():,}")
    for k, (nr, nc) in panel_shapes.items():
        logger.info("面板 %-13s: %s 行 × %s 列 (含 usci)", k, f"{nr:,}", f"{nc:,}")
    logger.info("-" * 70)
    logger.info("【结果分析】双权源产出指标判读 (越接近预期方向越健康):")
    logger.info("  ① 双权长表: 2/2 权源就绪, 全部非空 (空长表 SystemExit 级锚已过) (好)")
    logger.info("     判读: 城/县两权同源一表拆粒度 — 支撑差异全部来自县级键可对齐性 ((ii)/(iii) 通道),")
    logger.info("     属结构性缺失而非质量差异; 分析端预声明 primary 层级 (T-D7 铁律)。")
    logger.info("  ② own-bank 剔除: 长表落盘前已施加 (280 家银行系税调企业 vs 自家银行零泄漏) (好)")
    logger.info("     判读: 银行分支法人与其总行的对角线'关系'是机械恒真而非经济关系, 不剔会同时虚增")
    logger.info("     双权并令互验富集度向上偏; 落盘前剔除保证长表任何下游消费者都拿不到泄漏行。")
    logger.info("  ③ 覆盖锚: 城 A≥90%∧B≥99.5% / 县 A≥85%∧B≥99.5% 四 SystemExit 闸已过 (好)")
    logger.info("     判读: A 翻红 = '存续判定全错→网点全零'剧本; B 翻红 = 键清洗/T-D5c 回退失效或数据商")
    logger.info("     字段改码。生产 T=19 复跑若翻红, 先查数据商改版而非放松阈值 (T-D6 铁律)。")
    logger.info("  ④ (i) 类恒等 + county_key_ok: 占位 %s 家两权逐格恒等 ✓ | 缺键 %s 家单向 gate ✓ (好)",
                f"{len(ph_set):,}", f"{n_keyok0:,}")
    logger.info("     判读: 恒等是构造保证的运行时证据 (同一 net_city 表同式 merge); county_key_ok 把")
    logger.info("     '缺键'与'真零'在面板端机器可分 — 复现包使用者无需税调名单即可重构县权样本子集。")
    logger.info("  ⑤ DV2 未映射名称: %s 种 (全量落互验报告审计附录 top-50, 无静默丢弃) — 生产复跑时"
                "复核映射率 (关注)", f"{len(canon.audit):,}")
    logger.info("     判读: 未映射名 freq 结构性恒 1 (distinct 名集, 无频次梯度 — 'top 频次'非有效概念);")
    logger.info("     top-50 实以农商行/境外行为主, 另含少数城商行 (大同/洛阳/晋城) 因不在 bank_names.json")
    logger.info("     canonical 宇宙 (1,767 家) 而落审计 — 属 SSOT 枚举缺口 (非'政策性银行刻意排除', top-50")
    logger.info("     零命中进出口/农发/国开)。⚠ 覆盖锚 A/B 系 conditional-on-in-universe (测企业侧键命中率),")
    logger.info("     不认证银行宇宙本身完备性; 生产须另核 SSOT 是否漏收真实营业城商行 (codebook §7 L7 已挂账)。")
    logger.info("  ⑥ 互验件套 (富集度双基准/份额 Spearman 三行/均值差/Top-1/城县支撑对比) 已写入报告,"
                " 判读以报告为准: %s", outdir / "_company_tax_bank_weight_validation.md")
    logger.info("     判读: 健康形态 = 边际保持富集 >1× 且城县方向一致 + Spearman 以正为主 + 有关系媒体")
    logger.info("     对篇数均值高于无关系对 (收敛效度) + Top-1 同银行率低 (不同构念实证)。")
    logger.info("  ⑦ 富集度方向锚 (gate 口径 = 均匀基准 1.5×): 未达标权源 %d 个%s (dev 不判失败, loud "
                "WARNING 待生产复审)", len(warn_schemes),
                f" ({'/'.join(warn_schemes)})" if warn_schemes else "")
    logger.info("     边际保持口径 <1× 方向 (反向证据, 点名披露): %d 个%s — dev 共同支撑极小, "
                "方向定谳以生产复跑为准", len(marg_below),
                f" ({'/'.join(marg_below)})" if marg_below else "")
    logger.info("     份额 Spearman ρ<0 对 (反向证据, 点名披露): %d 个%s — 同上以生产复跑定谳",
                len(spearman_neg), f" ({'; '.join(spearman_neg)})" if spearman_neg else "")
    logger.info("     ④b 篇数均值差 <1× 权源 (反向证据, 点名披露): %d 个%s — 同上以生产复跑定谳",
                len(meandiff_below), f" ({'; '.join(meandiff_below)})" if meandiff_below else "")
    logger.info("  ⑧ dev vs 生产 T=19 预期差异: 媒体锚出自 dev 语料, 共同支撑对数偏小 (Spearman 可现")
    logger.info("     n/a, 小样本 ρ 波动大属预期); 生产 约1,819万 篇/T=19 下共同支撑将数量级增厚, 互验数值以")
    logger.info("     生产复跑为准; 权源 dta 侧锚 (行数/覆盖/端点闸) 不随语料变, 翻红另查数据商改版;")
    logger.info("     dev 产物不可用于任何回归 (T-D13 禁令)。")
    logger.info("-" * 70)
    logger.info("  ⏱ 各子阶段墙钟耗时 (秒, 4 位有效数字):")
    logger.info("     · ①加载 registry+pair 长表: %.4g 秒", t_load)
    logger.info("     · ②双权构建+双面板+互验计算: %.4g 秒", t_build)
    logger.info("     · ③写盘 报告+codebook: %.4g 秒", t_write)
    t_total = time.monotonic() - t_start
    logger.info("     · 子阶段合计: %.4g 秒 (占总阶段 %.4g%%)",
                t_load + t_build + t_write, 100 * (t_load + t_build + t_write) / max(t_total, 1e-9))
    logger.info("═" * 50)
    logger.info("阶段摘要: %s", Path(__file__).stem)
    logger.info("─" * 50)
    logger.info("  耗时:     %.4g 秒 (%.4g 分钟)", t_total, t_total / 60)
    logger.info("  输入:     pair 长表 %s 行 + 权源 dta %s 行 (映射后)",
                f"{len(pair):,}", f"{prep_stats['n_rows_mapped']:,}")
    logger.info("  输出:     双权长表 ×2 + 双权面板 ×2 + 互验报告 + codebook 双权章 → %s", outdir)
    logger.info("  内存RSS:  %.4g MB (psutil 终态读数, 峰值出现在面板引擎/写盘段, 以此为下界)", _rss_mb())
    logger.info("═" * 50)
    logger.info("--- 阶段执行完毕: %s ---", Path(__file__).stem)
    return 0


if __name__ == "__main__":
    sys.exit(main())
