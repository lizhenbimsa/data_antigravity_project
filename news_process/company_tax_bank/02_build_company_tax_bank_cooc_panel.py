"""WP1 — 税调企业×年 银企共现媒体报道面板 (COMPANY_TAX_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-08 v7).

产出 (T-D1/T-D12, 默认落 company_tax_bank/data/, 不入库):
  company_tax_bank/data/company_tax_bank_cooc_panel.dta        主面板 (447,710 行 = 44,771 家 × 10 年 2011–2020, 20 固定列 + 加权列)
  company_tax_bank/data/company_tax_bank_cooc_panel.parquet    伴生 (未缩写全名)
  company_tax_bank/data/company_tax_bank_cooc_panel_codebook.md
  company_tax_bank/data/_company_tax_bank_cooc_pairs.parquet   pair 长表 10 列 (被删加权列唯一重构载体)

跨管道复用边界 (T-D10, 禁第二份实现):
  加权引擎全部公司无关件经 importlib 复用 listed 02 (build_measure_library /
  compute_weighted_panel / _compute_weighted_panel_percol 参照臂 / default_paths /
  load_input21 / compute_wt_base / _sparse_equivalence_check); 本文件只持有公司相关本地件
  (load_name_assets / usci_map / scan_hits·build_pair_table·build_counts·add_hhi /
  write_outputs+FIXED_LABELS / run_gates)。税调 03 复用本模块 write_outputs (管道内禁重抄)。

独立派生数据脚本, 不注册 DAG; $0 纯字符串匹配, 无 API 无随机。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[1]
LISTED_DIR = REPO / "company_listed_bank"  # 跨管道引擎所在 (只读 import, T-D18 零字节改动)
DATA = REPO / "data" / "processed"         # 上游输入 (只读, 主管道产物)
OUT_DATA = HERE / "data"                   # 本流水线产物 (面板/pair/codebook, 不入库)
CONFIG = REPO / "config"
TRACKS = ("full", "ctx", "ss")
# 绝对合法域 = 新闻语料真实发表年域 (T-D4; 数据质检器, 与母本 listed 同 2007–2025)。
# ⚠ 铁律: **不随税调面板窗收窄** — 窗外 (2007–2010 / 2021–2025) 报道是"合法但窗外", 由
# build_pair_table/build_counts 的年窗过滤丢入 n_outwin 诊断 (INFO), 绝非"坏年"。若误把此域也收成
# 面板窗 2011–2020 → 生产全量下 2007–2010/2021–2025 共 9 年报道被判合法域外坏年、占比远超 0.1% 阈
# → build_year_map SystemExit。
ABS_YEAR_MIN, ABS_YEAR_MAX = 2007, 2025
# 面板年窗 = 税调企业数据可得域 (2011–2020; 税调调查仅覆盖此十年)。与 ABS 域 / listed 面板窗**刻意分叉**
# (listed 二者恰重合于 2007–2025; 税调则 ABS=语料域、PANEL=数据可得域两概念真正分离)。argparse 默认值锚此。
PANEL_YEAR_MIN, PANEL_YEAR_MAX = 2011, 2020

logger = logging.getLogger("02_build_company_tax_bank_cooc_panel")
if not logger.handlers:  # console 兜底 (被测试/importlib 导入时); main() 实跑时由 setup_logging 接管
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[tax_cooc_panel] %(levelname)s %(message)s"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)


# ---------------------------------------------------------------- 跨管道引擎载入 (T-D10)
_ENGINE = None


def engine():
    """listed 02 加权引擎模块 (importlib 惰性单例; 公司无关纯函数集, 只读复用)。

    模块名与本管道含 `_tax_` 区分, sys.path 双目录无遮蔽 (计划 T-D12 已核验)。
    引擎演进 → 本管道 gate (手算锚+bitwise) 翻红 = 故意的漂移探测器 (T-D10 耦合披露)。
    """
    global _ENGINE
    if _ENGINE is None:
        if str(LISTED_DIR) not in sys.path:
            sys.path.insert(0, str(LISTED_DIR))
        import importlib
        _ENGINE = importlib.import_module("02_build_company_bank_cooc_panel")
        _attach_engine_logging()
    return _ENGINE


class _EngineLogRename(logging.Filter):
    """把借用的 listed 加权引擎 logger 记录改名为本税调阶段名 — 真正兑现 redirect_module_logger
    语义。attach 只接管 handler 不改名, 会让引擎自身 emit 的 budget/双法等价断言等行携带 listed
    引擎阶段名混入税调日志 (按阶段名 grep 排障会漏归, 且步骤号错标)。改写 record.name 使这些行归
    到宿主税调阶段 (纯 cosmetic, 零数据/确定性影响; R1/T-D10)。"""

    def __init__(self, stage_name: str) -> None:
        super().__init__()
        self._stage = stage_name

    def filter(self, record: logging.LogRecord) -> bool:
        record.name = self._stage
        return True


def _attach_engine_logging() -> None:
    """跨管道引擎日志接管 (T-D10, 镜像主仓 redirect_module_logger 语义): 把本阶段文件 handler
    attach 到引擎 logger + 挂改名 Filter, 使 budget 生效值与 chunk 收缩 WARNING 以本税调阶段名落
    税调日志文件 (否则只上 console 且携带 listed 阶段名, 生产日志失载/错归)。测试进程不接管
    (与 _init_stage_logging 对称)。"""
    import os
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return
    eng_logger = logging.getLogger("02_build_company_bank_cooc_panel")
    if not any(isinstance(f, _EngineLogRename) for f in eng_logger.filters):
        eng_logger.addFilter(_EngineLogRename(Path(__file__).stem))  # R1: 改名兑现真 redirect
    for h in logger.handlers:
        if h not in eng_logger.handlers:
            eng_logger.addHandler(h)
    eng_logger.setLevel(logging.INFO)


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


def log(msg: str, warn: bool = False) -> None:
    (logger.warning if warn else logger.info)(msg)


def _rss_mb() -> float:
    import psutil
    return psutil.Process().memory_info().rss / 1024 / 1024


def _pkg_ver(name: str) -> str:
    """关键库版本 (importlib.metadata; 仅日志用途, 取不到一律 'n/a', 绝不影响计算)。"""
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return "n/a"


# ---------------------------------------------------------------- 税调名单载入 (T-D1 本地件)
_TAX_COMPANIES: list[dict] | None = None
_USCI_MAP: dict[str, str] | None = None


def tax_companies() -> list[dict]:
    """税调企业名单 SSOT = config/company_tax_names.yaml (44,771 家); 模块级缓存,
    load_name_assets / usci_map / 税调 03 共用一次读盘。"""
    global _TAX_COMPANIES
    if _TAX_COMPANIES is None:
        _TAX_COMPANIES = yaml.safe_load(
            (CONFIG / "company_tax_names.yaml").read_text(encoding="utf-8"))["companies"]
    return _TAX_COMPANIES


def usci_map() -> dict[str, str]:
    """company_tax_name → 18 位统一社会信用代码 (F1: 全填全唯一; 恒字符串)。
    面板与外部数据 merge 的核心接入键 (usci × year); write_outputs 单点注入消费。"""
    global _USCI_MAP
    if _USCI_MAP is None:
        _USCI_MAP = {c["company_tax_name"]: str(c["usci"]) for c in tax_companies()}
    return _USCI_MAP


def _log_stage_header(dp: dict, registry_path: Path, out_dta: Path,
                      year_min: int, year_max: int) -> None:
    """阶段头汇报块 (完全参照母本 02 / 主管道 12_news_fintech.log 内容格式; 纯日志, 无计算副作用)。"""
    import os
    import platform
    import sys as _sys
    stem = Path(__file__).stem
    logger.info("--- 开始执行阶段: %s ---", stem)
    logger.info("=" * 72)
    logger.info("步骤 02: 税调企业×年 银企共现媒体报道面板构建 (WP1; AC 三轨扫描 + 加权引擎 + pair 长表)")
    logger.info("=" * 72)
    logger.info("【功能】在 21_full 留篇宇宙 (行=报道×目标银行) 上, 用 44,771 家税调企业名 variant 做")
    logger.info("        Aho-Corasick 三轨 (full/ctx/ss) 扫描, 判定'该报道同时谈及目标银行与该税调企业',")
    logger.info("        聚成 企业×年 面板 (20 固定列 [含 usci str18] + registry 全部 emit 测度的 cw/ce")
    logger.info("        加权投影列), 另产 pair 长表 (企业×银行×年×轨, 被删加权列的唯一重构载体) 与 codebook。")
    logger.info("【方法】名单 SSOT=company_tax_names.yaml (v1.0.0); D4 own-bank 剔除 (280 家银行系税调企业")
    logger.info("        vs 自家银行, T-D3 五通道) + D4b 子串自共现作废 (语义照搬牡丹江先例);")
    logger.info("        归年=docid 全局 min(日期); 跨年去重键不含 year; 加权引擎 cw=Σ(w·X)/Σw (X 缺失不")
    logger.info("        摊薄) 与 ce=等权均值 — 引擎经 importlib 只读复用 listed 02 (T-D10 禁第二份实现)。")
    logger.info("【判读】命中率与 k^c 分位适中为佳 (过高=短名误配噪声, 过低=名单覆盖不足);")
    logger.info("        verified 严格分化 (_v ≤ canonical) 与 40 面板漂移闸是硬闸; gate 全过才落盘。")
    logger.info("【确定性】纯 CPU 字符串匹配 (ahocorasick/pandas), 无 LLM/网络/API ($0); mergesort 稳定")
    logger.info("          排序 + sorted 遍历, 同输入重跑列内容哈希一致 (T-D16 确定性验收域含本面板)。")
    logger.info("")
    logger.info("  🧭 项目 / 环境信息")
    logger.info("     · 步骤: %s (WP1 面板构建, company_tax_bank 流水线 02/03; 不注册主 DAG)", stem)
    logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板), 当前版本 v3.15.0")
    logger.info("     · 模块文件: %s", Path(__file__).resolve())
    logger.info("     · 工作目录: %s", os.getcwd())
    logger.info("     · Python:   %s @ %s", platform.python_version(), _sys.executable)
    logger.info("     · 平台:     %s | CPU 逻辑核=%s", platform.platform(), os.cpu_count())
    logger.info("     · PID=%s | RUN_ID=%s | 本步骤纯 CPU / 无 LLM·网络·API ($0) / 确定性可复现",
                os.getpid(), os.environ.get("NEWS_PROCESS_RUN_ID", "standalone"))
    logger.info("     · 关键库版本: pandas=%s | numpy=%s | pyarrow=%s | pyahocorasick=%s",
                _pkg_ver("pandas"), _pkg_ver("numpy"), _pkg_ver("pyarrow"), _pkg_ver("pyahocorasick"))
    logger.info("       pyreadstat=%s | scipy=%s | PyYAML=%s | psutil=%s (importlib.metadata, 仅日志用途)",
                _pkg_ver("pyreadstat"), _pkg_ver("scipy"), _pkg_ver("PyYAML"), _pkg_ver("psutil"))
    logger.info("  🧬 流水线定位 / 上下游消费者 / 复现命令")
    logger.info("     · 定位: company_tax_bank 独立派生流水线 01→02→03 的第 2 步 (WP1);")
    logger.info("       不注册主 DAG, 但上游全依赖主管道 data/processed 产物 (只读)")
    logger.info("     · 上游硬依赖: 步骤 01 的 registry yaml (加权引擎唯一 SSOT, 缺则本步骤拒跑)")
    logger.info("     · 跨管道复用: 加权引擎 = listed 02 公司无关件 (importlib 只读; listed 管线零改动铁律)")
    logger.info("     · 下游消费者: ① 步骤 03 双替代权 (城市/县域网点) 互验 (import 本模块 write_outputs +")
    logger.info("       读 pair 长表锚, 缺 pair 即 SystemExit '无锚即无互验'); ② Stata 分析端 (dta 短名+")
    logger.info("       中文标签, merge 键 usci×year); ③ 论文数据附录 (codebook 独立覆盖本流水线全部产物)")
    logger.info("     · 复现命令: python company_tax_bank/02_build_company_tax_bank_cooc_panel.py")
    logger.info("       (或 run_pipeline.py --steps 02; WP-orch 期建立)")
    logger.info("     · 关键 config 键: paths.yaml::output_21_tone_llms_full / output_40_panel_yearly /")
    logger.info("       output_15_article_alignment / output_51_panel_controls (27 号无键, 引擎内常量)")
    logger.info("     · 名单 SSOT: config/company_tax_names.yaml (企业, v1.0.0) + config/bank_names.json (银行);")
    logger.info("       gate 测试 = tests/test_company_tax_bank_cooc_panel.py (pytest 收集 61 项)")
    logger.info("  📂 输入 / 输出文件")
    logger.info("     · 输入(21_full): %s (留篇宇宙, 行=报道×目标银行)", dp["input"])
    logger.info("     · 输入(40 面板): %s (银行×年测度库主源)", dp["panel"])
    logger.info("     · 输入(16/27/51): %s | %s | %s (域外族, 任一缺失→对应族全缺失列)",
                dp["alignment"], dp["benefit"], dp["controls"])
    logger.info("     · 输入(registry): %s (步骤 01 产出, 唯一 SSOT)", registry_path)
    logger.info("     · 输出(主面板): %s (+同名 .parquet 伴生, 未缩写全名)", out_dta)
    logger.info("     · 输出(pair 长表): %s (metadata 含 registry_sha256 + 输入指纹)",
                out_dta.parent / "_company_tax_bank_cooc_pairs.parquet")
    logger.info("     · 输出(codebook): %s (含双替代权面板章占位区块, 03 幂等 upsert)",
                out_dta.parent / "company_tax_bank_cooc_panel_codebook.md")
    logger.info("     · 输出 schema 概述: 主面板 = 企业×年满骨架 (无缺格, %s 家 × %d 年 = %s 行)",
                "44,771", year_max - year_min + 1, f"{44_771 * (year_max - year_min + 1):,}")
    logger.info("       × [20 固定列 (标识/计数/HHI/覆盖诊断) + registry 全部 emit 测度的 cw/ce×三轨投影列];")
    logger.info("       pair 长表 = 企业×银行×年×轨 10 列")
    logger.info("     · 指纹/校验语义: pair 长表 parquet metadata 内嵌 registry_sha256 +")
    logger.info("       input_fingerprint=sha256(输入文件字节数|行数); 步骤 03 启动双向校验, stale 即 SystemExit")
    logger.info("     · 两套缺失语义: 计数列无命中=0 (真零); cw/ce 加权列无共现或无可用银行=NaN")
    logger.info("       (Stata '.', 绝非 0) — gate⑧ 强制互斥, 消费端不可混用")
    logger.info("  ⚙ 运行配置")
    logger.info("     · 三轨 = %s | 绝对合法域 = [%d, %d] | 面板年窗 = [%d, %d] | 固定列 %d 个",
                "/".join(TRACKS), ABS_YEAR_MIN, ABS_YEAR_MAX, year_min, year_max, len(FIXED_ORDER))
    logger.info("     · 加权双臂: cw=共现份额加权 (share×shift 结构) / ce=等权均值 — 互为稳健性、不分主次,")
    logger.info("       各自 just-identified 并排, 禁混同一 over-identified Hansen J (项目铁律)")
    logger.info("  📖 方法论依据 (参考文献 15 条, 按主题分节; 逐字引自项目已核验文献池, DOI 未改动)")
    logger.info("   ─── [A] 构念与效度: 新闻共现作为银企关联测度 ───")
    logger.info("     A1. Ge, S., Li, S., & Zheng, H. (2025). Diamond cuts diamond: News co-mention momentum")
    logger.info("         spillover prevails in China. Journal of Banking & Finance, 171, Article 107356.")
    logger.info("         https://doi.org/10.1016/j.jbankfin.2024.107356")
    logger.info("       → 白话: 中文财经新闻里两家机构被同篇报道共同提及, 是可检验的经济关联信号;")
    logger.info("         本步骤以'目标银行×税调企业同篇共现'构建关联强度, 与其效度前提同构。")
    logger.info("     A2. Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns.")
    logger.info("         The Journal of Finance, 64(5), 2023–2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x")
    logger.info("       → 白话: 媒体覆盖量本身就是有定价含义的公司特征; 本面板的 n_cooc_{full,ctx,ss} 计数列")
    logger.info("         即企业层'涉银报道覆盖量'测度, 无命中填 0 (真零) 是该构念的一部分。")
    logger.info("     A3. Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media in financial")
    logger.info("         markets. The Journal of Finance, 66(1), 67–97. https://doi.org/10.1111/j.1540-6261.2010.01626.x")
    logger.info("       → 白话: 把'报道行为'与'事件本身'分离并证明报道有独立因果作用; 支撑本脚本把报道级")
    logger.info("         共现做成面板处理变量, 而非仅当底层业务关系的被动代理。")
    logger.info("     A4. Lee, C. M. C., Ma, P., & Wang, C. C. Y. (2015). Search-based peer firms: Aggregating")
    logger.info("         investor perceptions through internet co-searches. Journal of Financial Economics,")
    logger.info("         116(2), 410–431. https://doi.org/10.1016/j.jfineco.2015.02.003")
    logger.info("       → 白话: 用'共同被检索'聚合公众感知来定义公司间关联, 与本脚本'共同被报道'同构;")
    logger.info("         其共现→关联的聚合思路即 pair 长表 (企业×银行×年×轨) 的设计原型。")
    logger.info("   ─── [B] 识别与加权: shift-share 结构 / W 矩阵选择 ───")
    logger.info("     B1. Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share")
    logger.info("         instruments. Journal of Economic Perspectives, 39(1), 181–204.")
    logger.info("         https://doi.org/10.1257/jep.20231370")
    logger.info("       → 白话: cw 加权列 = 共现份额(share)×银行测度(shift) 的 shift-share 结构; 分母只计")
    logger.info("         该测度非缺失银行的权重 (incomplete shares 的正面处理), 依该检查表落地。")
    logger.info("     B2. Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when,")
    logger.info("         why, and how. American Economic Review, 110(8), 2586–2624.")
    logger.info("         https://doi.org/10.1257/aer.20181047")
    logger.info("       → 白话: shift-share 设计的识别力来自份额的外生性; 本脚本把份额 (pair 长表 n_docs 系)")
    logger.info("         与银行测度库分离落盘, 使份额可被分析端单独审查、检验与替换。")
    logger.info("     B3. Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference.")
    logger.info("         The Quarterly Journal of Economics, 134(4), 1949–2010. https://doi.org/10.1093/qje/qjz025")
    logger.info("       → 白话: 共享同一银行 shift 的企业间残差相关, 常规聚类 SE 会失真; codebook 使用要点")
    logger.info("         已把 exposure-robust SE 列为 cw 列回归的分析端义务, 本日志同步提示。")
    logger.info("     B4. Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in")
    logger.info("         corporate financial policies. Journal of Financial Economics, 144(1), 247–272.")
    logger.info("         https://doi.org/10.1016/j.jfineco.2021.05.060")
    logger.info("       → 白话: 用哪种关系矩阵 W 加权本身就是识别假设; 故步骤 03 另备城市/县域两层级银行")
    logger.info("         网点替代权源互验, 证结论不被'媒体共现'这一种 W 的选择驱动。")
    logger.info("     B5. Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy?")
    logger.info("         The Journal of Finance, 69(1), 139–178. https://doi.org/10.1111/jofi.12094")
    logger.info("       → 白话: 关联组均值特征作解释变量是公司金融标准范式; ce 臂即'共现银行等权均值',")
    logger.info("         与 cw 共现加权臂并排互为稳健、不分主次。")
    logger.info("   ─── [C] 共现计数的统计性质: 分数计数 / 零模型 / 集中度 (HHI) ───")
    logger.info("     C1. Neal, Z. P., Domagalski, R., & Sagan, B. (2021). Comparing alternatives to the fixed")
    logger.info("         degree sequence model for extracting the backbone of bipartite projections. Scientific")
    logger.info("         Reports, 11(1), Article 23929. https://doi.org/10.1038/s41598-021-03238-3")
    logger.info("       → 白话: 二部投影的原始共现计数被两侧度分布机械驱动, 须对照零模型判读; 本步骤的")
    logger.info("         k^c 分位诊断与 frac (1/k 分摊) 即为此设; 步骤 03 富集度双基准是其正式检验。")
    logger.info("     C2. Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022). A better index for")
    logger.info("         analysis of co-occurrence and similarity. Science Advances, 8(4), Article eabj9204.")
    logger.info("         https://doi.org/10.1126/sciadv.abj9204")
    logger.info("       → 白话: 传统共现指数受边际频次污染, 跨单元比较会系统性误导; 本脚本同时物化")
    logger.info("         n_docs/frac/longhit/strict 多口径, 并保 pair 长表供任意替代指数事后重构。")
    logger.info("     C3. Hoberg, G., & Phillips, G. M. (2025). Scope, scale, and concentration: The 21st-century")
    logger.info("         firm. The Journal of Finance, 80(1), 415–466. https://doi.org/10.1111/jofi.13400")
    logger.info("       → 白话: 以文本测度刻画企业'组合集中度'的顶刊范式; cooc_hhi_{track} 用共现份额平方和")
    logger.info("         度量企业的银行组合集中度 (单银行格≡1, 零共现=NaN, gate③ 三锁)。")
    logger.info("   ─── [D] 数据工程与复现 ───")
    logger.info("     D1. Silcock, E., D'Amico-Wong, L., Yang, J., & Dell, M. (2022). Noise-robust de-duplication")
    logger.info("         at scale (NBER Working Paper No. 30726). https://doi.org/10.3386/w30726")
    logger.info("       → 白话: 大规模新闻语料的重复稿是文本测度的主要噪声源; 本脚本对 (docid,target_bank)")
    logger.info("         去重并断言重复行三轨文本一致, 不一致即 fail-loud 拒跑 (确定性失锚)。")
    logger.info("     D2. Menkveld, A. J., Dreber, A., Holzmeister, F., Huber, J., Johannesson, M., Kirchler, M.,")
    logger.info("         Razen, M., Weitzel, U., … [百人合著] (2024). Nonstandard errors. The Journal of Finance,")
    logger.info("         79(3), 2339–2390. https://doi.org/10.1111/jofi.13337")
    logger.info("       → 白话: 同一数据不同团队的管道决策会产生系统性'非标准误'; 本脚本把 cw/ce、三轨、")
    logger.info("         frac/longhit/strict 等构造决策全部并排物化, 把管道方差显性化供读者复算。")
    logger.info("     D3. Brodeur, A., Mikola, D., Cook, N., … [百人合著] (2026). Reproducibility and robustness")
    logger.info("         of economics and political science research. Nature, 652(8108), 151–156.")
    logger.info("         https://doi.org/10.1038/s41586-026-10251-x")
    logger.info("       → 白话: 大样本复现评估表明材料完备性直接决定可复现率; 本日志按复现材料标准记录")
    logger.info("         环境/库版本/输入指纹/复现命令, dta+parquet+codebook+pair 四件产物自足。")
    logger.info("")


# ---------------------------------------------------------------- 名单载入 + AC 自动机 + D4/D4b
def load_name_assets(registry: dict):
    """税调名单 (company_tax_names.yaml) + 银行名单 → AC 自动机 / D4b 子串索引 / D4 own-bank 对照。

    D4b 索引化加速 (T-D10 授权, 语义等价): 母本双循环 (每银行 variant × 全部公司 variant 的
    `cv in vb` 判定) 对 124,366 公司 variants 达 ~1e9 次 in, 分钟到十分钟级 — 改为对每个
    银行 variant 枚举其全部长度 < len(vb) 的连续子串、查公司 variant 集合。等价性由子串
    定义保证: `cv != vb and cv in vb` ⇔ cv 是 vb 的某个真子串 (长度必 < len(vb))。
    T-P0-5 普查清单 (92 对) 作参照臂: 运行时报 (公司 variant, 银行 variant) 真子串对数。
    """
    companies = tax_companies()
    banks = yaml.safe_load((CONFIG / "bank_names.json").read_text(encoding="utf-8"))
    company_names = [c["company_tax_name"] for c in companies]

    import ahocorasick
    A = ahocorasick.Automaton()
    variant_owner: dict[str, list[str]] = {}
    for c in companies:
        for v in c["variants"]:
            if not v or not v.strip():
                raise SystemExit(f"variant 空串守卫: 企业 {c['company_tax_name']} 含空/纯空白 variant")
            variant_owner.setdefault(v, []).append(c["company_tax_name"])
    for v, owners in variant_owner.items():
        A.add_word(v, (v, owners))
    A.make_automaton()

    bank_canonical = {b["bank_name"] for b in banks}
    # D4b: bank_name → 其全部 variants 的公司-variant 真子串集 (索引化: 子串枚举 + set 查询)
    company_variants = set(variant_owner)
    max_cv_len = max((len(v) for v in company_variants), default=0)
    bank_substr: dict[str, frozenset[str]] = {}
    pair_set: set[tuple[str, str]] = set()  # (公司 variant, 银行 variant) 真子串对 (T-P0-5 参照臂口径)
    for b in banks:
        sub = set()
        for vb in b["variants"]:
            L = len(vb)
            max_l = min(max_cv_len, L - 1)  # 真子串: 长度必 < len(vb) (cv==vb 排除由此内含)
            for length in range(1, max_l + 1):
                for i in range(L - length + 1):
                    cv = vb[i:i + length]
                    if cv in company_variants:
                        sub.add(cv)
                        pair_set.add((cv, vb))
        if sub:
            bank_substr[b["bank_name"]] = frozenset(sub)
    logger.info("D4b 子串索引构建 (索引化加速, 语义=公司 variant ⊊ 银行 variant 真子串): "
                "(公司 variant, 银行 variant) 真子串对 %d 对 (T-P0-5 全量普查参照臂 = 92 对; "
                "名单换代时该数漂移属预期, 与参照臂分叉须重审 §7-L7)", len(pair_set))
    # D4 own-bank 对照 (registry SSOT; T-D3: 值可为 [] 空列表 — scan 的 in 判定天然 no-op)
    own_map = {comp: set(bs) for comp, bs in registry["bank_company_map"].items()}
    bank_company_set = set(own_map)
    return A, variant_owner, bank_canonical, bank_substr, own_map, bank_company_set, company_names


# ---------------------------------------------------------------- 三轨 AC 扫描 (T-D4 零新口径)
def scan_hits(df: pd.DataFrame, A, bank_substr, own_map) -> pd.DataFrame:
    """逐行三轨 AC 扫描, D4/D4b 内联作废 → 命中明细 (company, bank, year_raw, docid, track,
    verified, ss_fallback, min_variant_len, max_variant_len)。构造口径逐条照搬母本 (T-D4)。"""
    records: list[tuple] = []
    n_d4 = n_d4b = 0  # 内联作废计数 (审计留痕: D4=own-bank 自共现 / D4b=子串自共现)
    it = df[["docid", "_year", "target_bank", "content_full", "content_ctx", "content_ss",
             "ss_is_fallback", "_verified"]].itertuples(index=False, name=None)
    for docid, year, bank, c_full, c_ctx, c_ss, ss_fb, verified in it:
        sub = bank_substr.get(bank)
        for track, text in (("full", c_full), ("ctx", c_ctx), ("ss", c_ss)):
            if not text:
                continue
            per_company: dict[str, list[str]] = {}
            for _, (variant, owners) in A.iter(text):
                for comp in owners:  # D5 跨公司重复 variant: 全部归属企业各计 (T-P0-4: 67 个)
                    per_company.setdefault(comp, []).append(variant)
            for comp, vars_hit in per_company.items():
                if bank in own_map.get(comp, ()):  # D4 own-bank 跳过 (银行系税调企业自共现)
                    n_d4 += 1
                    continue
                if sub and all(v in sub for v in vars_hit):  # D4b 逐轨: 全部命中 ⊂ 子串集 → 作废
                    n_d4b += 1
                    continue
                lens = [len(v) for v in vars_hit]
                records.append((comp, bank, year, docid, track, verified, bool(ss_fb),
                                min(lens), max(lens)))
    hits = pd.DataFrame(records, columns=["company", "bank", "year_raw", "docid", "track",
                                          "verified", "ss_fallback", "min_vlen", "max_vlen"])
    if len(hits):
        per_track = hits["track"].value_counts().to_dict()
        n_ver = int(hits["verified"].sum())
        logger.info("AC 三轨扫描完成: 命中明细 %s 行 (full=%s / ctx=%s / ss=%s) | verified 行 %s (%.4g%%)",
                    f"{len(hits):,}", f"{per_track.get('full', 0):,}", f"{per_track.get('ctx', 0):,}",
                    f"{per_track.get('ss', 0):,}", f"{n_ver:,}", 100 * n_ver / len(hits))
        logger.info("内联作废留痕: D4 own-bank 自共现跳过 %s 次 | D4b 子串自共现作废 %s 次 "
                    "(语义照搬牡丹江先例; 全部命中 variant ⊂ 银行名子串集才作废, 混合命中保留)",
                    f"{n_d4:,}", f"{n_d4b:,}")
        vlen = hits["max_vlen"]
        logger.info("命中 variant 长度谱 (max_vlen, 精度分层依据: 母本 dev 抽样 ≥4 字层 precision≈0.92): "
                    "≤2 字=%s | 3 字=%s | ≥4 字=%s (%.4g%%)",
                    f"{int((vlen <= 2).sum()):,}", f"{int((vlen == 3).sum()):,}",
                    f"{int((vlen >= 4).sum()):,}", 100 * float((vlen >= 4).mean()))
    return hits


# ---------------------------------------------------------------- 归年映射与年窗 (T-D4)
def build_year_map(hits: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """绝对合法域剔除 → 全局 docid→min(年) 映射 (窗口裁剪之前建立, 母本 v20 顺序封口)。"""
    bad = ((hits["year_raw"] < ABS_YEAR_MIN) | (hits["year_raw"] > ABS_YEAR_MAX)
           | hits["year_raw"].isna())  # L2: null 日期→NaT→NaN year, 显式计脏年 (否则 NaN 比较恒
    #                                    False 绕过脏年 SystemExit 闸 → 窗口过滤静默丢行, fail-open)
    n_bad = int(bad.sum())
    if n_bad:
        frac = n_bad / len(hits)
        log(f"绝对合法域外年份行剔除 {n_bad} ({100 * frac:.4g}%)", warn=True)
        if frac > 0.001:
            raise SystemExit(f"合法域外年份占比 {frac:.3%} > 0.1%")
        hits = hits.loc[~bad]
    year_map = hits.groupby("docid")["year_raw"].min()
    n_multi = int((hits.groupby("docid")["year_raw"].nunique() > 1).sum())
    if n_multi:
        log(f"同 docid 跨年 {n_multi} 篇 → min(日期) 归年", warn=True)
    hits = hits.assign(year=hits["docid"].map(year_map))
    if len(year_map):
        logger.info("归年映射建立 (T-D4: 窗口裁剪之前, 全局 docid→min(年)): %s 篇 | 年域 [%d, %d]",
                    f"{len(year_map):,}", int(year_map.min()), int(year_map.max()))
    return year_map, hits


# ---------------------------------------------------------------- pair 长表 (T-D4, 10 列)
def build_pair_table(hits: pd.DataFrame, year_min: int, year_max: int) -> pd.DataFrame:
    h = hits[(hits["year"] >= year_min) & (hits["year"] <= year_max)].copy()
    # k / k_v: 该 docid 该企业逐轨的去重有效银行数 (作废后; verified 版限 verified 行)
    dk = h.drop_duplicates(["company", "track", "docid", "bank"]).copy()
    key3 = pd.MultiIndex.from_frame(dk[["company", "track", "docid"]])
    key4 = pd.MultiIndex.from_frame(dk[["company", "bank", "track", "docid"]])
    k = dk.groupby(["company", "track", "docid"])["bank"].nunique()
    kv = dk[dk["verified"]].groupby(["company", "track", "docid"])["bank"].nunique()
    d = dk
    d["k"] = key3.map(k)
    d["k_v"] = key3.map(kv) if len(kv) else np.nan
    d["frac"] = 1.0 / d["k"]
    d["frac_v"] = np.where(d["verified"], 1.0 / d["k_v"], 0.0)
    # longhit: 该 (company,bank,docid,track) 存在任一 ≥4 字 variant 命中即计 (混合命中语义)
    lh = h.groupby(["company", "bank", "track", "docid"])["max_vlen"].max() >= 4
    d["longhit"] = key4.map(lh)
    # strict (仅 ss 轨语义): 剔 ss_fallback 行; full/ctx 恒等填充
    strict_docs = h.groupby(["company", "bank", "track", "docid"])["ss_fallback"].agg(lambda s: not s.all())
    d["nonfb"] = key4.map(strict_docs)
    d["ver_any"] = key4.map(h.groupby(["company", "bank", "track", "docid"])["verified"].any())
    d = d.sort_values(["company", "bank", "track", "docid"], kind="mergesort")  # 稳定排序后 sum
    g = d.groupby(["company", "bank", "year", "track"], sort=True)
    pair = pd.DataFrame({
        "n_docs": g["docid"].nunique(),
        "n_docs_v": g.apply(lambda x: x.loc[x["ver_any"], "docid"].nunique(), include_groups=False),
        "n_docs_strict": g.apply(lambda x: x.loc[x["nonfb"], "docid"].nunique(), include_groups=False),
        "n_docs_frac": g["frac"].sum(),
        "n_docs_frac_v": g["frac_v"].sum(),
        "n_docs_longhit": g.apply(lambda x: x.loc[x["longhit"], "docid"].nunique(), include_groups=False),
    }).reset_index()
    # full/ctx 轨 n_docs_strict = n_docs 恒等填充 (fallback 概念仅 ss 轨有, schema 注明)
    m = pair["track"].isin(["full", "ctx"])
    pair.loc[m, "n_docs_strict"] = pair.loc[m, "n_docs"]
    for c in ("n_docs", "n_docs_v", "n_docs_strict", "n_docs_longhit"):
        pair[c] = pair[c].astype("int32")
    return pair


# ---------------------------------------------------------------- 计数聚合 (T-D11)
def build_counts(hits: pd.DataFrame, companies: list[str], year_min: int, year_max: int,
                 bank_company_set: set[str]) -> pd.DataFrame:
    h = hits[(hits["year"] >= year_min) & (hits["year"] <= year_max)]
    # 全局去重键 = (company, track, docid) 不含 year (T-D4); year 由映射赋值
    dd = h.drop_duplicates(["company", "track", "docid"])
    out: dict[str, pd.Series] = {}
    for t in TRACKS:
        s = dd[dd["track"] == t]
        out[f"n_cooc_{t}"] = s.groupby(["company", "year"])["docid"].nunique()
        sv = h[(h["track"] == t) & h["verified"]].drop_duplicates(["company", "docid"])
        out[f"n_cooc_{t}_v"] = sv.groupby(["company", "year"])["docid"].nunique()
        out[f"n_banks_{t}"] = h[h["track"] == t].groupby(["company", "year"])["bank"].nunique()
    # ss_strict: 剔除该 docid 全部 ss 行均 fallback 的报道
    ss = h[h["track"] == "ss"].copy()
    if len(ss):
        nonfb_doc = ss.groupby(["company", "docid"])["ss_fallback"].agg(lambda s: not s.all())
        ss["nonfb"] = pd.MultiIndex.from_frame(ss[["company", "docid"]]).map(nonfb_doc)
        out["n_cooc_ss_strict"] = (ss[ss["nonfb"]].drop_duplicates(["company", "docid"])
                                   .groupby(["company", "year"])["docid"].nunique())
    else:
        out["n_cooc_ss_strict"] = pd.Series(dtype="float64")
    years = list(range(year_min, year_max + 1))
    idx = pd.MultiIndex.from_product([companies, years], names=["company_tax_name", "year"])
    panel = pd.DataFrame(index=idx)
    for name, s in out.items():
        if len(s) == 0:  # 空轨/空组: groupby 空 df 产单层索引, 换成空双层
            s = pd.Series(dtype="float64", index=pd.MultiIndex.from_arrays(
                [[], []], names=["company_tax_name", "year"]))
        else:
            s.index.names = ["company_tax_name", "year"]
        panel[name] = s
    panel = panel.fillna(0).astype("int32").reset_index()
    panel["year"] = panel["year"].astype("int16")
    panel["is_bank_company"] = panel["company_tax_name"].isin(bank_company_set).astype("int8")
    return panel


def add_hhi(panel: pd.DataFrame, pair: pd.DataFrame) -> pd.DataFrame:
    """cooc_hhi_{track}: canonical n_docs 份额平方和; 单银行≡1; 零共现 NaN (母本 D8b 照搬)。"""
    for t in TRACKS:
        p = pair[pair["track"] == t]
        tot = p.groupby(["company", "year"])["n_docs"].transform("sum")
        share2 = (p["n_docs"] / tot) ** 2
        hhi = share2.groupby([p["company"], p["year"]]).sum()
        hhi.index.names = ["company_tax_name", "year"]
        panel = panel.merge(hhi.rename(f"cooc_hhi_{t}"), how="left",
                            left_on=["company_tax_name", "year"], right_index=True)
    return panel


# ---------------------------------------------------------------- 标签 (照搬母本, T-D11 双闸)
FAMILY_LABEL = {
    "Q": "数量", "F": "金科强度", "S1": "情感LLM", "S1b": "情感LLM连续", "S1c": "情感正负份额",
    "S2": "情感词典", "S2b": "词典零规则", "S3": "词典均值", "S4": "情感BERT", "S4b": "BERT份额",
    "S5": "加权情感", "S6": "LM扩展", "S7": "情感切片", "C1": "分类共识", "C1b": "分类概率",
    "C2": "分类per-model", "QD": "分维度数量", "F2": "数字强度", "W": "洗白", "B": "社会效益",
    "ST": "陈旧度", "BP": "模板化", "RW": "罕见词", "AD": "采纳", "FE": "金科暴露", "CO": "语义凝聚",
    "AS": "权威相似", "AC": "算法迎合", "HD": "羊群", "SD": "战略差异化", "MC": "媒体构成",
    "NW": "网络", "CV": "媒体覆盖", "AT": "注意力", "PC": "同伴竞争", "IN": "行业冲击",
    "DA": "媒体分歧", "CS": "报道形态", "DS": "维度情感", "CL": "清晰度", "DP": "词典正负比",
    "TD": "情感动态", "CT": "迎合", "PE": "政策暴露", "PA": "政策对齐", "BD": "效益维度",
    "CTRL": "覆盖控制", "KW": "金科关键词", "FOCUS": "聚焦度", "MISC": "杂项",
    "GAP_UNPLANNED": "补遗", "S5_GAP": "加权情感补漏",
}


def make_label(arm: str, base: str, track: str, family: str, scheme_word: str = "共现") -> str:
    arm_word = f"{scheme_word}加权" if arm == "cw" else "等权均值"
    lbl = f"{arm_word}-{FAMILY_LABEL.get(family, family)}-{base}-{track}轨"
    lbl = lbl[:80]  # 截断单位 = 字符 (母本 v20 封口); 字节闸只作断言
    assert len(lbl.encode("utf-8")) <= 320
    return lbl


# ---------------------------------------------------------------- dta 写出 (usci 单点注入, T-D1)
def write_outputs(panel: pd.DataFrame, registry: dict, out_dta: Path, scheme_word: str = "共现",
                  fixed_labels: dict[str, str] | None = None, emit_dta: bool = True) -> None:
    """emit_dta=False (WP-S3 --no-emit-dta dev 快速模式): 只写 parquet 伴生, 跳过 pyreadstat.write_dta
    (省 ~330s/面板; dev 产物本不可回归)。默认 True → 生产照出 dta, 零行为变化。本函数对入参 panel
    非破坏 (usci 缺则先 .copy(); rename 建新 dta), 故可安全放后台线程 (WP-S2)。"""
    import pyreadstat
    # usci 兜底注入 (紧随 company_tax_name; 主面板已在 main 显式插入则跳过) —
    # 税调 03 双替代权面板经此单点获得同列, 禁在 03 第二份实现 (T-D1)
    if "usci" not in panel.columns:
        panel = panel.copy()
        panel.insert(panel.columns.get_loc("company_tax_name") + 1, "usci",
                     panel["company_tax_name"].map(usci_map()))
    assert panel["usci"].notna().all(), "usci 映射缺失 (税调名单 SSOT 应全覆盖 44,771 家)"
    assert (panel["usci"].str.len() == 18).all(), "usci 长度 ≠ 18 (str18 契约破; F1: 18 位全填全唯一)"
    emit = {e["basename"]: e for e in registry["entries"] if e["emit_panel"]}
    rename: dict[str, str] = {}
    labels: dict[str, str] = dict(fixed_labels or {})
    labels.setdefault("usci", "统一社会信用代码 (18 位)")
    for col in panel.columns:
        m = None
        for arm in ("cw", "ce"):
            if col.startswith(arm + "_"):
                rest = col[len(arm) + 1:]
                for t in TRACKS:
                    if rest.endswith("_" + t):
                        base = rest[: -(len(t) + 1)]
                        if base in emit:
                            m = (arm, base, t)
                        break
                break
        if m:
            arm, base, t = m
            e = emit[base]
            short = f"{arm}_{e['short_name']}_{t}"
            rename[col] = short
            labels[short] = make_label(arm, base, t, e["family"], scheme_word)
    # 三结构断言前置于任何写盘 (rename 非破坏 inplace=False, 元数据操作成本可忽略) → 恢复"全过才落盘"原子性
    dta = panel.rename(columns=rename)
    assert all(len(c) <= 32 for c in dta.columns), "dta 变量名超 32"
    assert len(set(dta.columns)) == len(dta.columns), "dta 变量名碰撞"
    assert all(len(v) <= 80 for v in labels.values()), "dta 变量标签超 80 字符"
    # F8 (2026-07-10 crash-safe): 先写 .tmp 再 Path.replace 原子改名 (同目录原子 rename) — 长跑 03 被 kill/
    # 崩于写盘中途时最终路径不留半写 dta/parquet 供 Stata 误读。最终字节与就地写等价 → golden 中性
    # (dta 头本含时间戳, golden gate 走 registry sha/列内容哈希, 非 dta 字节)。
    _pq = out_dta.with_suffix(".parquet")
    _pq_tmp = _pq.with_name(_pq.name + ".tmp")
    panel.to_parquet(_pq_tmp)  # 伴生用未缩写全名 (parquet 恒出)
    _pq_tmp.replace(_pq)
    if emit_dta:  # WP-S3: --no-emit-dta (dev 快速模式) 跳过 dta 落盘; 默认 True → 生产照出
        # 2026-07-15 审计防呆: labels.get(c, c) 静默兜底会把未登记标签的列以列名充当 label 落盘 —
        # 写盘前 loud 披露未命中清单 (当前实测 0 命中, 对现有列集 no-op; 保守 warning 级不硬崩)。
        _unlabeled = [c for c in dta.columns if c not in labels]
        if _unlabeled:
            logger.warning("write_outputs: %d 列未命中 labels, 以列名充当 dta label: %s",
                           len(_unlabeled), _unlabeled)
        _dta_tmp = out_dta.with_name(out_dta.name + ".tmp")
        pyreadstat.write_dta(dta, str(_dta_tmp), column_labels=[labels.get(c, c) for c in dta.columns])
        _dta_tmp.replace(out_dta)
    else:  # 删陈旧 dta (+ 残留 .tmp): 防外部 Stata 静默读到与新 parquet 版本错配的旧 dta (评审 no-emit-dta-stale)
        out_dta.unlink(missing_ok=True)
        out_dta.with_name(out_dta.name + ".tmp").unlink(missing_ok=True)


FIXED_LABELS = {
    "company_tax_name": "税调企业名称 (全称)",
    "usci": "统一社会信用代码 (18 位)",
    "year": "报道发表年",
    "is_bank_company": "银行系税调企业 (D4, 280 家)",
    "n_cooc_full": "银企共现报道数-full轨",
    "n_cooc_ctx": "银企共现报道数-ctx轨",
    "n_cooc_ss": "银企共现报道数-ss轨",
    "n_cooc_full_v": "同full轨, 限LLM验证通过报道",
    "n_cooc_ctx_v": "同ctx轨, 限LLM验证通过报道",
    "n_cooc_ss_v": "同ss轨, 限LLM验证通过报道",
    "n_cooc_ss_strict": "同ss轨, 剔除ss回退报道",
    "n_banks_full": "full轨共现去重银行家数",
    "n_banks_ctx": "ctx轨共现去重银行家数",
    "n_banks_ss": "ss轨共现去重银行家数",
    "cooc_hhi_full": "full轨共现权重集中度HHI",
    "cooc_hhi_ctx": "ctx轨共现权重集中度HHI",
    "cooc_hhi_ss": "ss轨共现权重集中度HHI",
    "cooc_wt_base_full": "full轨共现落在银行面板的比例",
    "cooc_wt_base_ctx": "ctx轨共现落在银行面板的比例",
    "cooc_wt_base_ss": "ss轨共现落在银行面板的比例",
}

FIXED_ORDER = list(FIXED_LABELS)

# codebook 双替代权面板章标记 (§1 命名规则钉死, 成对字面量; 03 幂等 section-upsert)
CODEBOOK_ALT_BEGIN = "<!-- BEGIN 双替代权面板章 (03 生成, 勿手改) -->"
CODEBOOK_ALT_END = "<!-- END 双替代权面板章 -->"


# ---------------------------------------------------------------- codebook (T-D19 ①–⑦)
def write_codebook(path: Path, registry: dict, panel: pd.DataFrame, input21: pd.DataFrame,
                   year_min: int, year_max: int) -> None:
    emit = [e for e in registry["entries"] if e["emit_panel"]]
    yearly = input21.groupby("_year").size()
    from collections import Counter
    excl_codes = Counter(registry["excluded"].values())
    lines = [
        "# 税调企业银企共现面板 (company_tax_bank) — codebook",
        "",
        "> 本 codebook 独立覆盖 company_tax_bank 流水线的**全部**产物 (与 news_process 主项目",
        "> codebook 相互独立, 互不交叉引用维护); 机器可读 emit 子集 SSOT = ",
        f"> `config/company_tax_bank_cooc_registry.yaml` (registry_sha256 "
        f"{registry['meta']['registry_sha256'][:16]}…); 按全谱表找列请先查该清单 (CUT 裁剪在案)。",
        "> 禁写生成时间戳 (T-D16 确定性验收域: 同输入两跑本文件 sha256 恒等)。",
        "",
        "## 产物总览 (整个功能, 全部落 company_tax_bank/data/)",
        "| 产物 | 生产步骤 | 说明 |", "|---|---|---|",
        "| `company_tax_bank_cooc_panel.dta`/`.parquet` | 02 | 主面板 (媒体共现权): 企业×年, 20 固定列 + 加权列 |",
        "| `_company_tax_bank_cooc_pairs.parquet` | 02 | pair 长表 (企业×银行×年×轨), 被删加权列唯一重构载体 |",
        "| `company_tax_bank_cooc_panel_codebook.md` | 02 (双权章由 03 upsert) | 本文件 |",
        "| `_company_tax_bank_altweights_{scheme}.parquet` ×2 | 03 | 双替代权长表 (branch_city 城市网点 / branch_county 县域网点) |",
        "| `company_tax_bank_{scheme}w_panel.dta`/`.parquet` ×2 | 03 | 双替代权真实面板 (与主面板并成三权) |",
        "| `_company_tax_bank_weight_validation.md` | 03 | 三权互验报告 (富集度双基准/份额 Spearman/均值差 等 DV5 件套) |",
        "",
        "执行顺序与硬依赖见 `company_tax_bank/README.md` (WP-orch 期建立); 唯一不落 data/ 的产物 = "
        "registry yaml (入库 SSOT, 落 `config/`)。",
        "",
        "## ① 数据谱系 (T-D19①)",
        "原始媒体语料 → stage 00–14 (银行·金科实体识别 → stage 13 银∧金科邻近共现硬过滤 → 三轨文本物化) "
        "→ stage 21 三家 LLM 情感/验证 (21_tone_llms_full.parquet 全宇宙, 行=报道×目标银行) "
        "→ 本脚本对三轨文本做**税调企业名 AC 匹配** (名单 SSOT = `config/company_tax_names.yaml` v1.0.0, "
        "44,771 家, 124,366 个 variants; 派生自税调企业名称批次 xlsx) → pair 长表 → 加权引擎 "
        "(registry SSOT, 经 importlib 只读复用 listed 02 引擎) → 企业×年面板。"
        "权源侧 (03): `config/银行业金融机构基本信息表.dta` (603,907 行商业数据, 不入库) → BankCanon "
        "规范化 → 城市/县域两层级网点权。计数的语料宇宙是\"银行金融科技报道\", 不是全部新闻。",
        "",
        "**谱系与许可披露 (T-D20)**: 税调名单是政府调查数据, 保密性/再分发地位比商业名单更尖锐 — "
        "派生聚合面板可分发; 名单/行级长表按需申请 (降级路径)。权源 dta 谱系七字段 (数据商·数据库名/"
        "表编号·版本·获取日期·提取过滤条件·许可条款·第三方获取路径) 核定 DEFERRED 至生产机轮 (§6)。"
        "外部不可得的税调名单与权源 dta 使完整重生不可复现, 复现包附 pair 长表+双权长表代偿。",
        "",
        "## ② 逐变量说明 (T-D19②)",
        "",
        "### pair 长表 schema (10 列逐列)",
        "| 列 | 含义 |", "|---|---|",
        "| `company` | 税调企业全称 (company_tax_names.yaml SSOT) |",
        "| `bank` | 目标银行 canonical 名 (bank_names.json SSOT) |",
        "| `year` | 归年 = 该 docid 全局 min(日期) 年 (跨年去重键不含 year) |",
        "| `track` | 文本轨 full/ctx/ss |",
        "| `n_docs` | 该 (企业,银行,年,轨) 去重共现篇数 (canonical 不门控) |",
        "| `n_docs_v` | verified 门控篇数 (llm_verified_full==True 行级) |",
        "| `n_docs_strict` | ss 轨剔 fallback 行的严格同句篇数 (非 ss 轨恒等填充 ≡ n_docs) |",
        "| `n_docs_frac` | 分数计数 Σ(1/k), k=该篇该企业该轨去重有效银行数 (同篇多银行按 1/k 分摊) |",
        "| `n_docs_frac_v` | verified 口径分数计数 (unverified 行计 0) |",
        "| `n_docs_longhit` | 存在任一 ≥4 字 variant 命中的篇数 (混合命中语义, 精度稳健臂) |",
        "",
        f"### 固定列 ({len(FIXED_LABELS)})",
        "| 变量 | 标签 |", "|---|---|",
    ]
    lines += [f"| `{k}` | {v} |" for k, v in FIXED_LABELS.items()]
    lines += [
        "",
        "`usci` = 18 位统一社会信用代码 (F1: 全填全唯一) — 面板与外部数据 merge 的首选键 "
        "(`usci × year`; `company_tax_name × year` 为等价备用键)。"
        "`is_bank_company` = 名称含 {银行, 农商} 两 token 的税调企业 (T-D3①, 280 家); own-bank 剔除后"
        "其行保留 (与自家银行的共现不计), 剔样本归分析端 (§7-L6)。",
        "",
        "### 加权测度列",
        "构造通式: `cw_X_t(i,yr) = Σ_b [n_cooc_t(b,i,yr)/Σ_b' n_cooc_t(b',i,yr)] × X_t(b,yr)` "
        "(分母限该测度该年非缺失共现银行并重归一); `ce_X_t` 等权算术平均稳健臂。"
        "权重与测度同轨; track-agnostic 源列以权重轨为准。列序 = registry SSOT 条目序→轨→臂。",
        "",
        "## 两套缺失语义",
        "计数列无命中填 0 (面板基底语义); 加权测度列无共现/无可用银行置缺失 (Stata `.`), 绝非 0。",
        "",
        "## 门控双宇宙",
        "权重 = canonical 不门控计数 (21_full 全宇宙); 测度侧统一为 verified 宇宙 "
        "(40 面板沿上游门控, 自聚合族 = verified 子集 semi-join)。两宇宙刻意不同属设计。",
        "",
        "## ③ 使用要点 (分析端义务, T-D19③)",
        "- **exposure-robust SE**: cw 列 = 共现份额×银行测度的 shift-share 结构, 共享同一银行 shift 的",
        "  企业间残差相关 — 推断须用 exposure-robust SE (Adão-Kolesár-Morales 2019 QJE / ",
        "  Borusyak-Hull-Jaravel 2022 型), 常规按企业聚类会失真。",
        "- **⚠ cluster(bank) 无定义警示**: 本面板行键是企业×年, 每行的 cw/ce 混合多家银行的贡献 — ",
        "  企业级回归里 `cluster(bank)` 无定义; 银行维聚类须回 pair 长表重构成 企业×银行×年 长表再做。",
        "- **计数列建模**: n_cooc 族右偏重零 — 建议 `ln(1+x)` 或 PPML (泊松伪极大似然), 勿直接 OLS 原值。",
        "- **三轨禁单调断言**: full/ctx/ss 三轨互为稳健性、不分主次, 轨间无单调包含关系 (ss 有回退语义),",
        "  禁作 n_cooc_ss ≤ n_cooc_ctx ≤ n_cooc_full 类断言; 三轨禁混同一 over-identified Hansen J。",
        "- **cooc_wt_base 上界语义**: 该值是 cw 列有效覆盖的上界 (共现落在银行面板的比例) — 走低时",
        "  加权测度只代表部分共现宇宙, 分析端按覆盖率做样本限制稳健。",
        "- **权重内生性**: 媒体共现权重与被加权测度可能同源于报道行为本身 (共源反射通道) — 03 的",
        "  城市/县域网点权即其对照臂; 预声明 primary 权重后三权并排, 禁挑臂单报。",
        "- **满骨架截断**: 面板本体不裁行 (裁行会破坏计数列 fillna(0) 真零语义); 99%+ 全零行在回归端",
        "  属\"无共现企业-年\", 样本裁剪归分析端 (Stata 示例见下)。",
        "",
        "## ④ D17 三义务段 (T-D19④)",
        "- allv 锚点构念由 PA 族单载体承载 (auth_sim/AD allv 交叉臂已裁, pair 表可重构)。",
        "- `bert_avg_neu ≡ 1 − bert_avg_pos − bert_avg_neg` 恒等 (残差 ≤1e-4; finbert2 无 neu 致 "
        "ensemble 层混 2/3 模型宇宙, 禁加和断言)。",
        "- 被删 410 基名 ×6 臂列研究地位不降: 全部可由 pair 长表 + 银行×年面板 (46/40 dta 全列) 按 "
        "D12 公式一行 merge 精确重构 (isclose 级; 负清单与 listed 同一份, 义务原封适用)。重构代码段:",
        "",
        "```python",
        "import pandas as pd",
        "pair = pd.read_parquet('_company_tax_bank_cooc_pairs.parquet')",
        "bank = pd.read_parquet('40_panel_yearly.parquet')  # 或 46 dta 全列",
        "t, X = 'full', '<被删源列名>'",
        "p = pair[pair.track == t].merge(bank[['target_bank', 'year', X]],",
        "        left_on=['bank', 'year'], right_on=['target_bank', 'year'])",
        "p = p[p[X].notna()]",
        "w = p.n_docs / p.groupby(['company', 'year']).n_docs.transform('sum')",
        "cw = (w * p[X]).groupby([p.company, p.year]).sum()  # cw_<X>_full",
        "ce = p.groupby(['company', 'year'])[X].mean()       # ce_<X>_full",
        "```",
        "",
        "### 消融预答 (D17 黄牌)",
        "词典规则消融变体与 canonical 相关 0.998–0.999 (主仓 audit MATH-1 在案), 完整梯子经 pair 表可复现。",
        "",
        "## ⑤ 逐年上游语料覆盖表 (T-D19⑤; 计数 0 可判真零 vs 无语料假零)",
        "| 年 | 输入报道行数 |", "|---|---|",
    ]
    for y in range(year_min, year_max + 1):
        lines.append(f"| {y} | {int(yearly.get(y, 0))} |")
    lines += [
        "",
        "面板年窗 2011–2020 (税调企业数据可得域) 完整内嵌于新闻语料域 2007–2025, 故生产全量下"
        "每个窗内年均有语料; dev T=2 (2017–2018) 下其余窗内年整年 0 属预期而非缺失。",
        "",
        "## ⑥ 附录 (T-D19⑥)",
        "",
        "### 排除列审计表 (registry excluded 区段按理由代码汇总)",
        "| 理由代码 | 列数 |", "|---|---|",
    ]
    lines += [f"| {code} | {n} |" for code, n in sorted(excl_codes.items())]
    lines += [
        "",
        f"(逐列明细共 {sum(excl_codes.values())} 条, 见 registry yaml `excluded` 区段; "
        "emit/CUT 判定负清单与 listed 管线共用同一份 CUT_LIST v23。)",
        "",
        "### 缩写名↔全名对照表",
        "| 全名基名 | dta 短名 |", "|---|---|",
    ]
    lines += [f"| {e['basename']} | {e['short_name']} |" for e in emit
              if e["short_name"] != e["basename"]]
    lines += [
        "",
        "### Stata merge 示例 (merge 键 = usci × year)",
        "```stata",
        "use company_tax_bank_cooc_panel.dta, clear",
        "merge 1:1 usci year using firm_admin_panel.dta   // usci = 18 位统一社会信用代码",
        "* 满骨架截断示例 (L2 口径): 名单为批次快照无逐年存续, 满骨架铺 0;",
        "* 按需以外部工商注册年裁样本, 剔除注册前年份的机械真零行",
        "keep if year<=2024 & year>=reg_year",
        "xtset, clear",
        "```",
        "",
        "### 匹配精度分层抽样 (T-P0-7 dev 一轮; 生产机第二轮 DEFERRED)",
        "2 字 variants 32 条全量人工过目: 含 `科技`/`电脑`/`空中`/`商检` 等高泛用 token (源自简称列, "
        "挂在个别企业) — 维持不裁剪口径 (与 listed 一致), 分析端可按 usci 剔除受污企业行; 3 字 21 条"
        "无同级风险。母本 dev 分层抽样参照: ≤2 字层 precision ≈0.71 / 3 字层 ≈0.76 / ≥4 字层 ≈0.92 — "
        "短名假阳性通道实证 → pair 长表 `n_docs_longhit` (≥4 字 variant 命中计数臂) 是唯一可执行稳健工具。",
        "",
        "### 已知局限 (计划 §7 全量)",
        "**税调特有**: L1 短简称假阳性 (≤4 字 variants 1,353 条, 2 字 32 / 3 字 21; 44,771 家名录密度下"
        "命中密度上升; 不裁剪只披露, 稳健工具 = n_docs_longhit) / L2 税调名单时点性 (批次快照无逐年存续 → "
        "满骨架铺 0, 与 listed \"上市前年份\"同型; 以 usci 关联外部工商注册年截断) / L3 县权结构性缺失 "
        "~2.2% (922 家直筒子·零星缺失 + 开发区/高新区等非民政区划残差; 精确家数以 ① county_key_ok 附录"
        "运行时实数为单一数字源, 县权回归样本 = 有真县级区划企业子集; 144 家省直辖占位企业城县两权恒等点名) / "
        "L4 县改区·区划变更错位 (权源快照 vs 税调批次两时点, 计入 B 锚缺口"
        "披露, 不建别名表) / L5 分支权构念 (网点数≈本地银行供给暴露, shift-share 型; 构念差异非质量差异) / "
        "L6 280 家银行系企业 (own-bank 剔除后面板行保留 is_bank_company=1, 剔样本归分析端) / "
        "L7 own-bank 子串映射残余风险 (支配规则+人工过目后仍属批次快照, bank_names.json 扩充须重审, "
        "gate 翻红机制兜底)。",
        "",
        "**继承母本 §7 通用局限 (对税调面板同构成立, 显式声明继承而非默认)**: 公司侧名录/通稿灌水 "
        "(k^c 分位诊断入日志, 刻意不设剔除阈值) / variant 子串重叠双计 (T-P0-4 跨企业重复 variant 67 个 "
        "[最大 8 归属] · T-P0-5 银企子串对 92 对, 保守口径) / 拉丁字母大小写敏感 / full 轨联播稿权重放大 + "
        "联播稿 HHI=1/k 假分散 / D4b 残余第三方假阳性 / 企业侧覆盖自选择 (Heckman/扩展边际提示) / "
        "variant 快照无逐年生效 / 21_full 行宇宙 = stage 13 共现硬过滤后口径 / 加权测度银行覆盖缺口 "
        "(共现银行全集 vs 40 面板银行数; cooc_wt_base 诊断) / dev 缺源列基名 / 分类份额小分母噪声 / "
        "多重检验负担 ~1,900 列 / 共现关系类型异质 (Hilt & Schwenkler) / LLM lookahead bias。",
        "",
        "三轨/嵌入双轨/LLM 三家/词典梯子/BERT 三模型/加权-等权两臂/三权重 (媒体共现·城市网点·县域网点): "
        "互为稳健、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。",
        "",
        "pair 长表 `n_docs_strict` 语义注: 仅 ss 轨剔 `ss_is_fallback` 报道; full/ctx 轨恒等",
        "`n_docs` 填充 (fallback 概念仅 ss 轨有, 勿按 ctx_is_fallback 重算)。",
        "",
    ]
    text = "\n".join(lines)
    # ⑦ 双替代权面板章 section-upsert 区块 (T-D19⑦): 02 预留占位区块; 03 幂等 replace。
    # 整文件重写不清掉既有章 (镜像 listed 02 的保留逻辑)。
    block = "\n\n(占位: 双替代权面板章由步骤 03 生成后幂等 upsert 于此。)\n\n"
    if path.exists():
        old = path.read_text(encoding="utf-8")
        if CODEBOOK_ALT_BEGIN in old and CODEBOOK_ALT_END in old:
            block = old.split(CODEBOOK_ALT_BEGIN)[1].split(CODEBOOK_ALT_END)[0]
    text = text.rstrip("\n") + "\n\n" + CODEBOOK_ALT_BEGIN + block + CODEBOOK_ALT_END + "\n"
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- gates (八组内联, fail-loud)
def run_gates(panel: pd.DataFrame, pair: pd.DataFrame, registry: dict,
              n_rows_expect: int) -> None:
    assert len(panel) == n_rows_expect, f"行数 {len(panel)} ≠ {n_rows_expect}"
    log(f"  gate① 行数不变量: {len(panel):,} 行 == 企业数×年数 预期 {n_rows_expect:,} ✓ (满骨架完备无缺格)")
    for t in TRACKS:
        assert (panel[f"n_cooc_{t}_v"] <= panel[f"n_cooc_{t}"]).all()
        nb, nc = panel[f"n_banks_{t}"], panel[f"n_cooc_{t}"]
        assert ((nb >= 1) == (nc >= 1)).all()
        hhi = panel[f"cooc_hhi_{t}"].dropna()
        assert ((hhi > 0) & (hhi <= 1)).all(), f"HHI 值域违例 {t}"
        sub = panel.loc[panel[f"cooc_hhi_{t}"].notna()]
        assert (sub[f"cooc_hhi_{t}"] >= 1 / sub[f"n_banks_{t}"] - 1e-12).all()
        single = sub[sub[f"n_banks_{t}"] == 1]
        assert (single[f"cooc_hhi_{t}"] == 1.0).all(), "单银行格 HHI 须无容差 ==1.0"
        wb = panel[f"cooc_wt_base_{t}"].dropna()
        assert ((wb >= 0) & (wb <= 1)).all()
    assert (panel["n_cooc_ss_strict"] <= panel["n_cooc_ss"]).all()
    log("  gate② 计数序 (三轨): n_cooc_v ≤ n_cooc / n_banks≥1 ⇔ n_cooc≥1 / ss_strict ≤ ss ✓")
    log("  gate③ HHI 三锁 (三轨): 值域 (0,1] / HHI ≥ 1/n_banks / 单银行格无容差 ==1.0 ✓; "
        "cooc_wt_base ∈ [0,1] ✓")
    # verified 严格分化 (Σ==0 独立诊断文案, T-P0-6): Σ n_cooc_*_v < Σ n_cooc_* 全轨
    for t in TRACKS:
        tot, tot_v = int(panel[f"n_cooc_{t}"].sum()), int(panel[f"n_cooc_{t}_v"].sum())
        if tot == 0:
            raise AssertionError(
                f"{t} 轨 Σn_cooc==0 — 全轨零命中: 独立诊断 (非 verified 分化问题), 先查税调名单 "
                f"variants/AC 自动机/该轨文本是否为空, 再查 21_full 语料覆盖")
        assert tot_v < tot, f"{t} 轨 verified 未分化 (21_full 应含 unverified 行)"
    log("  gate④ verified 严格分化: " + " / ".join(
        f"{t} Σv={int(panel[f'n_cooc_{t}_v'].sum()):,}<Σ={int(panel[f'n_cooc_{t}'].sum()):,}"
        for t in TRACKS) + " ✓ (门控双宇宙真实分化, 非恒等复制)")
    # pair 恒等式: Σ_b n_docs_frac == n_cooc 全格三轨 isclose (禁精确相等)
    for t in TRACKS:
        p = pair[pair["track"] == t]
        s = p.groupby(["company", "year"])["n_docs_frac"].sum()
        s_v = p.groupby(["company", "year"])["n_docs_frac_v"].sum()
        s.index.names = s_v.index.names = ["company_tax_name", "year"]
        lhs = panel.set_index(["company_tax_name", "year"])[f"n_cooc_{t}"]
        lhs_v = panel.set_index(["company_tax_name", "year"])[f"n_cooc_{t}_v"]
        joined = pd.DataFrame({"frac": s}).join(lhs.rename("n"), how="left")
        assert joined["n"].notna().all(), f"pair 表 (company,year) 落在面板骨架外 ({t})"
        assert np.isclose(joined["frac"], joined["n"]).all(), f"Σ n_docs_frac ≠ n_cooc ({t})"
        joined_v = pd.DataFrame({"frac": s_v}).join(lhs_v.rename("n"), how="left")
        assert np.isclose(joined_v["frac"], joined_v["n"]).all(), f"Σ n_docs_frac_v ≠ n_cooc_v ({t})"
        assert (p["n_docs_longhit"] <= p["n_docs"]).all()
    log("  gate⑤ pair frac 恒等 (三轨): Σ_b n_docs_frac == n_cooc 且 Σ_b n_docs_frac_v == n_cooc_v "
        "全格 isclose ✓ (分数计数分摊无泄漏); longhit ≤ n_docs ✓")
    # 单银行企业×年格 cw == ce (N=1 短路后精确; 双方同 NaN 亦过) — 抽 registry 前 20 emit 列
    emit_entries = [e for e in registry["entries"] if e["emit_panel"]][:20]
    single_mask = panel["n_banks_full"] == 1
    n_cwce_checked = 0
    for e in emit_entries:
        if "full" not in e["emit_tracks"]:
            continue
        cwc, cec = f"cw_{e['basename']}_full", f"ce_{e['basename']}_full"
        if cwc in panel.columns:
            a, b = panel.loc[single_mask, cwc], panel.loc[single_mask, cec]
            ok = (a.isna() & b.isna()) | np.isclose(a, b, equal_nan=True)
            assert ok.all(), f"单银行格 cw≠ce: {cwc}"
            n_cwce_checked += 1
    log(f"  gate⑥ 单银行格 cw==ce (N=1 短路精确性): 抽 registry 前 20 emit 条目实检 "
        f"{n_cwce_checked} 列 × {int(single_mask.sum()):,} 格 ✓")
    # 值域 gate: registry range_gate 字段展开 (禁列名圈定)
    n_range_cols = 0
    for e in registry["entries"]:
        if not e["emit_panel"] or e["range_gate"] == "none":
            continue
        lo, hi = (-1.0, 1.0) if e["range_gate"] == "tone" else (0.0, 1.0)
        for t in e["emit_tracks"]:
            for arm in ("cw", "ce"):
                col = f"{arm}_{e['basename']}_{t}"
                if col not in panel.columns:
                    continue
                v = panel[col].dropna()
                if len(v):
                    assert (v >= lo - 1e-9).all() and (v <= hi + 1e-9).all(), f"值域违例 {col}"
                n_range_cols += 1
    log(f"  gate⑦ 值域 (registry range_gate 展开, 禁列名圈定): tone∈[-1,1] / frac∈[0,1] "
        f"共检 {n_range_cols:,} 列 ✓")
    # 缺失语义互斥: n_cooc_t==0 ⇒ 该轨全部 cw/ce 缺失
    cw_cols_by_track = {t: [c for c in panel.columns
                            if (c.startswith("cw_") or c.startswith("ce_")) and c.endswith("_" + t)
                            and not c.startswith("cooc_")] for t in TRACKS}
    for t in TRACKS:
        zero = panel[f"n_cooc_{t}"] == 0
        if cw_cols_by_track[t]:
            assert panel.loc[zero, cw_cols_by_track[t]].isna().all().all(), \
                f"零共现格出现非缺失加权值 ({t})"
    log("  gate⑧ 两套缺失语义互斥: n_cooc==0 格 ⇒ 该轨全部 cw/ce 缺失 (计数真零 vs 测度缺失"
        "绝不混淆) 三轨全过 ✓")
    log("WP1 内联 gate 全过 (八组硬闸, 任一失败 = AssertionError 拒绝落盘)")


# ---------------------------------------------------------------- main
def build_upstream_snapshot(p_input: Path | None, p_panel: Path | None,
                            p_align: Path | None, p_benefit: Path | None,
                            p_controls: Path | None) -> dict:
    """G2a/F17 (八入口审计计划 2026-07-10): 五上游代际快照 — 记录层锚 + 新鲜度哨兵。

    刻意不并入 input_fingerprint 本体 (03/04 双向锁语义不变, 锁不翻); 仅供审计取证。
    schema: 键=resolve 句柄名, 值={file,size,mtime_ns,sha256_16}, 缺席上游=null。
    哨兵 (保守超集 max(panel, input)): 27 号由 paper 侧独立生产, 陈旧在 dev 常态 —
    **警不崩, 照并旧值** (语义与主管道 runner F2 mtime 守卫相反: 那边=陈旧跳过 merge)。
    与 listed 侧 02 逐字同构 (pair metadata 写段是两处独立副本, 双改同步)。
    """
    def _snap(path: Path | None) -> dict | None:
        if path is None:
            return None
        st = path.stat()
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return {"file": path.name, "size": st.st_size,
                "mtime_ns": st.st_mtime_ns, "sha256_16": h.hexdigest()[:16]}

    snapshot = {name: _snap(p) for name, p in (
        ("input", p_input), ("panel", p_panel), ("alignment", p_align),
        ("benefit", p_benefit), ("controls", p_controls))}
    for name, ent in snapshot.items():
        logger.info("  [upstream_snapshot] %-9s = %s", name,
                    "缺席 (null)" if ent is None else
                    f"{ent['file']} | {ent['size']:,d} B | mtime_ns={ent['mtime_ns']}"
                    f" | sha256_16={ent['sha256_16']}")
    if (p_benefit is not None and p_input is not None and p_panel is not None
            and p_benefit.stat().st_mtime_ns < max(
                p_panel.stat().st_mtime_ns, p_input.stat().st_mtime_ns)):
        logger.warning(
            "27_benefit_dimensions_panel 早于本轮主管道产物 (代际陈旧), benefit 48 列取值属旧代 — "
            "重生入口 = 从 repo 根跑 python -m news_process.papers.benefit_society.dimension_analysis "
            "--track all --include-lg --df-exploded news_process/data/processed/40_article_bank_level.parquet "
            "(缺 --df-exploded 则 anchors-only 不落面板; 若 27 号确已同步重生, 本警告为保守误报, "
            "以 upstream_snapshot 内 benefit 的 sha256_16 为准)")
    return snapshot


def main(argv=None) -> int:
    if sys.flags.optimize:  # 本脚本 fail-fast 闸为 assert, -O/PYTHONOPTIMIZE 下会静默失效并照常落盘
        raise SystemExit("禁以 -O/PYTHONOPTIMIZE 运行 (assert 闸失效 → 无防线静默落盘)")
    _init_stage_logging()
    eng = engine()  # 跨管道引擎 (T-D10; import 即 attach 本阶段日志 handler)
    dp = eng.default_paths()
    ap = argparse.ArgumentParser()
    ap.add_argument("--input"); ap.add_argument("--panel"); ap.add_argument("--alignment")
    ap.add_argument("--benefit"); ap.add_argument("--controls")
    ap.add_argument("--registry", default=str(CONFIG / "company_tax_bank_cooc_registry.yaml"))
    ap.add_argument("--output", default=str(OUT_DATA / "company_tax_bank_cooc_panel.dta"))
    ap.add_argument("--year-min", type=int, default=PANEL_YEAR_MIN)
    ap.add_argument("--year-max", type=int, default=PANEL_YEAR_MAX)
    ap.add_argument("--no-emit-dta", action="store_true",
                    help="WP-S3 dev 快速模式: 跳过 dta 落盘只写 parquet (dev 产物不可回归; 生产勿用)")
    args = ap.parse_args(argv)
    if args.year_min > args.year_max:
        raise SystemExit(2)

    def resolve(name: str, required: bool = False) -> Path | None:
        given = getattr(args, name)
        if given:  # 显式传参: 缺失 → SystemExit
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

    import time
    t_start = time.monotonic()
    _log_stage_header(dp, Path(args.registry), Path(args.output), args.year_min, args.year_max)

    t0 = time.monotonic()
    reg_path = Path(args.registry)
    if not reg_path.exists():  # 显式 SystemExit (兑现"缺则不跑"文案; 裸 FileNotFoundError 无排障指引)
        raise SystemExit(f"registry 缺失: {reg_path} — 先跑 WP0 (01_build_company_tax_bank_cooc_registry.py)")
    registry = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    # 启动自校验 (T-D8): 哈希锚复算 + registry 基名数 + 40 面板实读列集 ⊆ 已判定全集
    if registry["meta"]["n_entries"] < 600:
        raise SystemExit("registry 基名数 < 600 — 疑损坏")
    # 哈希锚复算: canonical 式经 importlib 复用税调 01 的 SSOT 函数 registry_content_sha256
    # (01→02→run_pipeline→gate 四方同一实现, 禁第二份; gate 测试另存独立重算式作双实现互证)
    import importlib
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    wp0 = importlib.import_module("01_build_company_tax_bank_cooc_registry")
    recalc_sha = wp0.registry_content_sha256(registry)
    if recalc_sha != registry["meta"]["registry_sha256"]:
        raise SystemExit("registry 内容与 meta.registry_sha256 不自洽 (手改/半写/损坏) — 重跑 WP0")
    logger.info("registry 哈希锚启动复算通过: 内容 sha256=%s… == meta.registry_sha256 (canonical 式"
                "复用 01 SSOT 函数)", recalc_sha[:16])
    p_input = resolve("input", required=True)
    p_panel = resolve("panel", required=True)
    p_align, p_benefit, p_controls = resolve("alignment"), resolve("benefit"), resolve("controls")

    import pyarrow.parquet as pq
    cols40_live = {n for n in pq.ParquetFile(p_panel).schema_arrow.names if n != "__index_level_0__"}
    judged = {c for e in registry["entries"] if e["source"] == "40"
              for c in e["col_by_track"].values() if c}
    judged |= {k for k in registry["excluded"] if ":" not in k}
    drift = cols40_live - judged
    if drift:
        raise SystemExit(f"40 面板出现 registry 未判定新列 (WP0 后漂移; 处置协议 T-D9: 先跑 listed 01 "
                         f"对照确认漂移同源, 禁就地加 EXCLUDE 正则): {sorted(drift)[:10]}")

    upstream_snapshot = build_upstream_snapshot(
        p_input, p_panel, p_align, p_benefit, p_controls)

    A, variant_owner, bank_canonical, bank_substr, own_map, bank_company_set, company_names = \
        load_name_assets(registry)
    logger.info("正在从 %s 加载数据...", p_input)
    input21 = eng.load_input21(p_input, bank_canonical)
    logger.info("已加载 %s 行数据。", f"{len(input21):,}")
    logger.info("  📐 输入 schema: 行数=%s | 列数=%d | 税调企业名单=%s 家 (variant %s 个) | 银行 canonical=%d 家",
                f"{len(input21):,}", len(input21.columns), f"{len(company_names):,}",
                f"{len(variant_owner):,}", len(bank_canonical))
    n_ver_rows = int(input21["_verified"].sum())
    logger.info("留篇宇宙细目 (21_full, 行=报道×目标银行): docid 去重 %s 篇 | 目标银行 %d 家 | "
                "年域 [%d, %d] | llm_verified_full==True 行 %s (%.4g%%; 门控双宇宙 — "
                "权重侧 canonical 不门控, 测度侧 verified 宇宙)",
                f"{input21['docid'].nunique():,}", input21["target_bank"].nunique(),
                int(input21["_year"].min()), int(input21["_year"].max()),
                f"{n_ver_rows:,}", 100 * n_ver_rows / len(input21))
    n_multi_owner = sum(1 for v in variant_owner.values() if len(v) > 1)
    n_own_empty = sum(1 for bs in own_map.values() if not bs)
    logger.info("D4b 子串自共现索引: %d 家银行建有公司-variant 真子串集 (子串对合计 %s) | "
                "跨企业重复 variant %d 个 (D5: 全部归属企业各计; T-P0-4 参照臂=67) | "
                "D4 own-bank 对照 %d 家 (T-D3 恰 280; 其中空列表值 %d 家 = 无 canonical 对应, "
                "no-op 但 is_bank_company 仍=1)",
                len(bank_substr), f"{sum(len(s) for s in bank_substr.values()):,}",
                n_multi_owner, len(own_map), n_own_empty)
    logger.info("[Memory] 数据加载后 | RSS: %.4g MB (psutil 驻留集读数, 非峰值)", _rss_mb())
    t_load = time.monotonic() - t0

    t0 = time.monotonic()
    logger.info("开始三轨 Aho-Corasick 扫描 (D4/D4b 内联作废)...")
    hits = scan_hits(input21, A, bank_substr, own_map)
    if hits.empty:
        raise SystemExit(1)  # 全表零命中不可能 (44,771 家对生产语料)
    year_map, hits = build_year_map(hits)
    # 合法域内、窗外 → INFO 裁剪 (第二层)
    n_outwin = int(((hits["year"] < args.year_min) | (hits["year"] > args.year_max)).sum())
    if n_outwin:
        log(f"INFO: 窗口外年份行裁剪 {n_outwin} (属预期)")

    pair = build_pair_table(hits, args.year_min, args.year_max)
    pt_counts = pair["track"].value_counts().to_dict()
    logger.info("pair 长表构建 (企业×银行×年×轨, 10 列; 被删 410 基名×6 臂加权列的唯一重构载体): "
                "%s 行 (full=%s / ctx=%s / ss=%s)", f"{len(pair):,}",
                f"{pt_counts.get('full', 0):,}", f"{pt_counts.get('ctx', 0):,}",
                f"{pt_counts.get('ss', 0):,}")
    for t in TRACKS:
        p = pair[pair["track"] == t]
        if not len(p):
            continue
        n_docs_sum, frac_sum = int(p["n_docs"].sum()), float(p["n_docs_frac"].sum())
        lh_share = float(p["n_docs_longhit"].sum()) / max(n_docs_sum, 1)
        msg = (f"  pair[{t}]: Σn_docs={n_docs_sum:,} | Σn_docs_v={int(p['n_docs_v'].sum()):,} "
               f"(verified 门控) | Σn_docs_frac={frac_sum:,.4g} (Σ(1/k) 同篇多银行分摊) | "
               f"longhit 篇占比={100 * lh_share:.4g}% (≥4 字 variant 精度稳健臂)")
        if t == "ss":
            n_fb = int((p["n_docs"] - p["n_docs_strict"]).sum())
            msg += f" | strict 剔 ss 回退 {n_fb:,} 篇计数"
        logger.info(msg)
    panel = build_counts(hits, company_names, args.year_min, args.year_max, bank_company_set)
    # usci 紧随 company_tax_name (FIXED_ORDER 第 2 固定列; 18 位字符串, T-D1 单点注入)
    panel.insert(1, "usci", panel["company_tax_name"].map(usci_map()))
    assert panel["usci"].notna().all(), "usci 映射缺失 (税调名单 SSOT 应全覆盖 44,771 家)"
    panel = add_hhi(panel, pair)
    for t in TRACKS:
        nz = panel[panel[f"n_cooc_{t}"] > 0]
        n_single = int((nz[f"n_banks_{t}"] == 1).sum())
        logger.info("  计数聚合[%s]: 有共现企业×年格 %s | 共现总篇计 %s | 单银行格 %s (HHI≡1.0) | "
                    "HHI 非缺失 %s 格", t, f"{len(nz):,}", f"{int(nz[f'n_cooc_{t}'].sum()):,}",
                    f"{n_single:,}", f"{int(panel[f'cooc_hhi_{t}'].notna().sum()):,}")
    logger.info("is_bank_company 标记: %d 家银行系税调企业 (D4, own-bank 剔除后其行保留但自家银行不计共现)",
                int(panel.drop_duplicates('company_tax_name')['is_bank_company'].sum()))

    panel40 = pd.read_parquet(p_panel)
    align = pd.read_parquet(p_align) if p_align else None
    benefit = pd.read_parquet(p_benefit) if p_benefit else None
    controls = pd.read_parquet(p_controls) if p_controls else None
    measures = eng.build_measure_library(input21, panel40, align, benefit, controls, registry)
    del panel40, align, benefit, controls  # T-D13: merge/写盘间显式释放
    n_agg16 = sum(1 for c in measures.columns if str(c).startswith("__agg16__"))
    n_agg21 = sum(1 for c in measures.columns if str(c).startswith("__agg21__"))
    logger.info("银行×年测度库构建 (五上游统一, 引擎消费面; T-D10 跨管道复用 listed 02): "
                "%s 银行×年键 × %s 列 (40/51/27 直读=%d | 16 号 PA 自聚合=%d | 21 号 KW·FOCUS 自聚合=%d)",
                f"{len(measures):,}", f"{len(measures.columns):,}",
                len(measures.columns) - n_agg16 - n_agg21, n_agg16, n_agg21)

    wt_base = eng.compute_wt_base(pair, measures)
    panel = panel.merge(wt_base, how="left", left_on=["company_tax_name", "year"], right_index=True)
    for t in TRACKS:
        wb = wt_base[f"cooc_wt_base_{t}"].dropna()
        if len(wb):
            logger.info("  cooc_wt_base[%s] (共现落在银行面板的比例, 加权测度覆盖诊断): "
                        "均值 %.4g | p10 %.4g | 全 1.0 格占比 %.4g%%",
                        t, float(wb.mean()), float(wb.quantile(0.1)), 100 * float((wb == 1.0).mean()))

    # 媒体权重长表 (canonical n_docs, 逐轨)
    weights = pair.rename(columns={"n_docs": "w"})[["company", "bank", "year", "track", "w"]]
    logger.info("媒体权重长表 (canonical n_docs 不门控, 逐轨三矩阵): %s 行 → 加权引擎 "
                "(cw=Σ(w·X)/Σw 缺失不摊薄 + ce=等权均值; N=1 格短路 cw:=X 防浮点漂移)",
                f"{len(weights.dropna(subset=['w'])):,}")
    weighted = eng.compute_weighted_panel(weights, measures, registry)
    n_cw = sum(1 for c in weighted.columns if c.startswith("cw_"))
    n_ce = sum(1 for c in weighted.columns if c.startswith("ce_"))
    n_all_nan = int(weighted.isna().all().sum()) if len(weighted.columns) else 0
    logger.info("加权投影完成: %s 列 (cw=%s + ce=%s, 列序=registry SSOT 条目序→轨→臂) | "
                "全 NaN 列 %s 个", f"{len(weighted.columns):,}", f"{n_cw:,}", f"{n_ce:,}",
                f"{n_all_nan:,}")
    if n_all_nan:
        log(f"{n_all_nan} 个加权列全 NaN (主因 BERT nt_iyvol/iytrend 需 T≥3 + _ss 稀疏的 dev T=2 退化→T=19 恢复; 非 cross_media, 后者 emit_tracks=[] 产 0 列, 详见 ⑥ 判读 / 计划 F2/F3)", warn=True)
    panel = panel.merge(weighted, how="left", left_on=["company_tax_name", "year"], right_index=True)

    # 列序: 固定 20 列 + 加权列 (registry SSOT 序, weighted 已排)
    ordered = FIXED_ORDER + [c for c in panel.columns if c not in FIXED_ORDER]
    panel = panel[ordered]

    n_expect = len(company_names) * (args.year_max - args.year_min + 1)  # 乘式, 禁写死 (T-D1)
    run_gates(panel, pair, registry, n_expect)
    eng._sparse_equivalence_check(weights, measures, registry, weighted)
    del weighted, measures  # T-D13: 写盘前显式释放 (峰值控制)
    t_build = time.monotonic() - t0
    logger.info("[Memory] 聚合+加权+gate 后 | RSS: %.4g MB (psutil 驻留集读数, 非峰值)", _rss_mb())

    t0 = time.monotonic()
    out_dta = Path(args.output)
    out_dta.parent.mkdir(parents=True, exist_ok=True)
    logger.info("正在将主面板/pair 长表/codebook 写入 %s...", out_dta.parent)
    # pair 长表落盘 (含 registry 哈希 + 输入指纹 metadata); 与主面板同目录 (跟随 --output)
    import pyarrow as pa
    import pyarrow.parquet as pqw
    tbl = pa.Table.from_pandas(pair, preserve_index=False)
    fingerprint = hashlib.sha256(f"{p_input.stat().st_size}|{len(input21)}".encode()).hexdigest()
    tbl = tbl.replace_schema_metadata({**(tbl.schema.metadata or {}),
                                       b"registry_sha256": registry["meta"]["registry_sha256"].encode(),
                                       b"input_fingerprint": fingerprint.encode(),
                                       b"upstream_snapshot": json.dumps(
                                           upstream_snapshot, ensure_ascii=False,
                                           sort_keys=True).encode()})
    pqw.write_table(tbl, out_dta.parent / "_company_tax_bank_cooc_pairs.parquet")
    logger.info("pair 长表落盘: metadata 内嵌 registry_sha256=%s… + input_fingerprint=%s… "
                "(步骤 03 启动时校验, stale 即 SystemExit)",
                registry["meta"]["registry_sha256"][:16], fingerprint[:16])

    write_outputs(panel, registry, out_dta, fixed_labels=FIXED_LABELS, emit_dta=not args.no_emit_dta)
    logger.info("主面板落盘: %s (短名 + 中文变量标签 ≤80 字符; usci str18 三联闸过) + 同名 .parquet "
                "伴生 (未缩写全名, 程序端首选)", out_dta.name)
    cb_path = out_dta.parent / "company_tax_bank_cooc_panel_codebook.md"
    write_codebook(cb_path, registry, panel, input21, args.year_min, args.year_max)
    logger.info("codebook 落盘: %s (%d 行; T-D19 ①–⑥ 全骨架 + ⑦ 双替代权面板章占位区块, "
                "步骤 03 幂等 upsert 保留)", cb_path.name,
                len(cb_path.read_text(encoding="utf-8").splitlines()))
    t_write = time.monotonic() - t0

    # 统计报告 + 结果分析 (格式参照母本 02 / 12_news_fintech.log)
    logger.info("=" * 70)
    logger.info("===      税调企业银企共现面板构建统计报告      ===")
    logger.info("=" * 70)
    logger.info("输入宇宙: %s 行 (报道×目标银行) | 命中明细: %s 行", f"{len(input21):,}", f"{len(hits):,}")
    logger.info("主面板: %s 行 × %s 列 (企业 %s × 年 %d)", f"{len(panel):,}", f"{len(panel.columns):,}",
                f"{len(company_names):,}", args.year_max - args.year_min + 1)
    logger.info("pair 长表: %s 行 × %d 列", f"{len(pair):,}", len(pair.columns))
    # 逐年命中篇数分布 (真零 vs 无语料假零 可判)
    hit_by_year = hits.drop_duplicates("docid").groupby("year").size()
    logger.info("逐年命中篇数 (docid 去重): %s",
                {int(y): int(n) for y, n in hit_by_year.sort_index().items()})
    # 头部企业 (full 轨窗口总篇数 top-5; 灌水诊断辅助, 刻意不设剔除阈值)
    top5 = (panel.groupby("company_tax_name")["n_cooc_full"].sum()
            .sort_values(ascending=False).head(5))
    logger.info("full 轨共现篇数 top-5 企业: %s", {k: int(v) for k, v in top5.items()})
    # B1: 单企业占比畸高 = 短名/通用子串 variant 误配灌水信号 (设计刻意不剔除, 仅 surface —
    # 阈值属分析端自由度; 对冲工具 = n_docs_longhit ≥4字臂 + codebook §7 L1)。运行时 loud 告警,
    # 使该数据态在生产日志即被点名, 而非仅靠 top-5/k^c 留痕人工发现。
    _tot_full = int(panel["n_cooc_full"].sum())
    if _tot_full and len(top5):
        _t1_share = int(top5.iloc[0]) / _tot_full
        if _t1_share > 0.30:
            log(f"单企业共现占比畸高: {top5.index[0]} 占 full 轨共现总篇计 {_t1_share:.1%} "
                f"({int(top5.iloc[0]):,}/{_tot_full:,}) — 疑短名/通用子串 variant 误配灌水; 核该"
                f"企业 variant 长度谱 + 用 n_docs_longhit (≥4字臂) 稳健复核 (刻意不剔除, §7 L1)",
                warn=True)
    # k^c 分位诊断 (§7, 无剔除阈值)
    for t in TRACKS:
        ht = hits[hits["track"] == t].drop_duplicates(["company", "docid"])
        kc = ht.groupby("docid")["company"].nunique()
        if len(kc):
            q = kc.quantile([0.5, 0.9, 0.99]).tolist()
            log(f"k^c {t}: p50={q[0]:.4g} p90={q[1]:.4g} p99={q[2]:.4g} max={kc.max()}"
                f" | top docid: {kc.nlargest(3).to_dict()}")
    logger.info("-" * 70)
    n_docs_hit = hits.drop_duplicates("docid").shape[0]
    n_comp_hit = panel.loc[panel["n_cooc_full"] > 0, "company_tax_name"].nunique()
    logger.info("【结果分析】面板构建产出指标判读 (逐条附经济学/方法学解读与健康区间):")
    logger.info("  ① 行数不变量: %s 行 == %s 企业 × %d 年 → 满骨架完备无缺格 (好)",
                f"{len(panel):,}", f"{len(company_names):,}", args.year_max - args.year_min + 1)
    logger.info("     判读: 行数只由名单×年窗决定, 与语料规模无关 — 缺格意味着 reindex/merge 静默丢行,")
    logger.info("     任何偏离都是代码缺陷而非数据态; 平衡骨架也是 Stata xtset 与真零/假零判别的前提。")
    logger.info("  ② 共现覆盖: %s/%s 篇报道命中 ≥1 家税调企业 (%.4g%%); %s 家企业 full 轨有共现"
                " → 有可消费信号 (好)", f"{n_docs_hit:,}", f"{input21['docid'].nunique():,}",
                100 * n_docs_hit / max(input21["docid"].nunique(), 1), f"{n_comp_hit:,}")
    logger.info("     判读: 语料宇宙是 stage 13 过滤后的'银行金融科技报道', 命中率高于一般新闻属预期;")
    logger.info("     44,771 家名录密度下命中率还会高于 listed 5,528 家 (§7-L1); 过高 (>90%%) 提示短名")
    logger.info("     误配灌水, 过低 (<10%%) 提示名单覆盖不足或轨文本为空 — 两个方向都应先查 variant")
    logger.info("     长度谱与 k^c 右尾, 而非直接采信计数列。")
    logger.info("  ③ 内联 gate: frac 恒等/HHI 三锁/值域/单银行 cw==ce/缺失互斥/verified 分化 全过;"
                " 双法 (分块 join vs 稀疏矩阵) 抽样等价已证 → 加权引擎无静默错位 (好)")
    logger.info("     判读: 八闸全为恒等式/序关系/值域约束, 与样本规模无关 — 生产 T=19 上任何一闸翻红")
    logger.info("     都指向构造缺陷 (如权重错轨/分母摊薄/缺失被填 0), 属拒绝落盘级错误, 不可当告警忽略。")
    logger.info("  ④ pair 长表 metadata 带 registry_sha256=%s… + 输入指纹 → 步骤 03 双向锁可核 (好)",
                registry["meta"]["registry_sha256"][:16])
    logger.info("     判读: 指纹链保证 03 的双权互验与本面板同源同输入 — 复现包审查者可据此排除")
    logger.info("     '面板与权重来自不同数据快照'这一常见不可复现根因。")
    logger.info("  ⑤ k^c 右尾判读 (上表分位): p50 低而 max 高 = 少数名录/盘点稿贡献大量弱关联共现;")
    logger.info("     frac 列 (1/k 分摊) 与 longhit 臂即其对冲, 刻意不设剔除阈值 (阈值属分析端自由度,")
    logger.info("     预注册后在回归端做样本限制稳健, 避免本步骤引入 researcher df)。")
    logger.info("  ⑥ 全 NaN 加权列 %s 个 (共 %s 列): 两独立成因 (F3 拆分, 勿混为'缺源列一因') —",
                f"{n_all_nan:,}", f"{n_cw + n_ce:,}")
    logger.info("     (a) BERT nt_iyvol/iytrend (需 T≥3 且 ≥6 有效月) + _ss 轨 substance/washing 稀疏 = dev T=2 时间深度退化,")
    logger.info("         生产 T=19 上游全列重生后自然填充 (与'缺源列'无关, 勿盲查 40/51/27 覆盖);")
    logger.info("     (b) cross_media 三基名 (cross_media_alpha/cross_outlet_tone_variance/n_events) registry emit_tracks=[] → 产 0 列 (非此处 NaN);")
    logger.info("         若主面板整体缺 cross_media, 属 main↔validation 顺序耦合 (stage75 恒晚于 stage40) 非 T=19 覆盖问题 — 见 README/计划 F2。")
    logger.info("  ⑦ cooc_wt_base (上文三轨统计): 该值是 cw 列有效覆盖的上界 — 越接近 1, 加权测度")
    logger.info("     对共现宇宙的代表性越强 (>0.9 视为健康); 生产上若走低属数据态而非 bug,")
    logger.info("     分析端按覆盖率做样本限制稳健 (codebook 使用要点义务)。")
    logger.info("  ⑧ 与生产 T=19 的预期差异: 本次输入为 dev 语料 (约全量 0.05%%); 计数/覆盖/k^c 分位")
    logger.info("     将随语料放大数量级, 但 gate 判据 (恒等/值域/序) 与骨架行数公式均规模无关,")
    logger.info("     可直接作为生产运行的判读基线; 面板窗 2011–2020 全内嵌语料域 2007–2025, 生产各窗内年")
    logger.info("     均有语料, dev T=2 仅 2017–2018 有语料、其余窗内年整年 0 属预期非缺失;")
    logger.info("     dev 产物不可用于任何回归 (T-D13 禁令)。")
    logger.info("-" * 70)
    logger.info("  ⏱ 各子阶段墙钟耗时与吞吐率 (4 位有效数字; 吞吐率=既有计数/墙钟, 无新增重计算):")
    logger.info("     · ①加载 registry+名单+21_full: %.4g 秒 (吞吐 %.4g 输入行/秒)",
                t_load, len(input21) / max(t_load, 1e-9))
    logger.info("     · ②AC 扫描+聚合+加权+gate: %.4g 秒 (吞吐 %.4g 输入行/秒 | %.4g 命中明细行/秒)",
                t_build, len(input21) / max(t_build, 1e-9), len(hits) / max(t_build, 1e-9))
    logger.info("     · ③写盘 dta/parquet/pair/codebook: %.4g 秒 (吞吐 %.4g 面板单元格/秒; "
                "dta 全表序列化为该段主项)",
                t_write, len(panel) * len(panel.columns) / max(t_write, 1e-9))
    t_total = time.monotonic() - t_start
    logger.info("     · 子阶段合计: %.4g 秒 (占总阶段 %.4g%%; 余量=argparse/头部日志等常数开销)",
                t_load + t_build + t_write, 100 * (t_load + t_build + t_write) / max(t_total, 1e-9))
    logger.info("     · 判读: 生产 T=19 下 ② 随语料行数近线性放大 (AC 扫描对文本长度线性), ③ 随")
    logger.info("       面板行×列放大; RSS 峰值主项 = 写盘期 dta 全表驻留 (447,710 行 × ~1,900 列")
    logger.info("       ≈7GB float64 单帧, T-D13 预算内; merge/写盘间已显式 del 释放)。")
    logger.info("═" * 50)
    logger.info("阶段摘要: %s", Path(__file__).stem)
    logger.info("─" * 50)
    logger.info("  耗时:     %.4g 秒 (%.4g 分钟)", t_total, t_total / 60)
    logger.info("  输入:     %s 行 (21_full 报道×目标银行)", f"{len(input21):,}")
    logger.info("  输出:     %s 行 × %s 列 → %s", f"{len(panel):,}", f"{len(panel.columns):,}", out_dta.name)
    logger.info("  内存RSS:  %.4g MB (进程当前驻留集, 非运行期峰值)", _rss_mb())
    logger.info("═" * 50)
    logger.info("--- 阶段执行完毕: %s ---", Path(__file__).stem)
    return 0


if __name__ == "__main__":
    sys.exit(main())
