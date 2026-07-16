"""WP0 — 银企共现面板测度注册表对账脚本 (COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN v33).

职责 (计划 §4 WP0):
  1. 读五上游 (40/51/27/16/21_full) 全列名, 按 D15 排除规则 (正则+白名单) 与
     D11 族规则做**全划分** — 每列判 {纳入某基名的源列 | 排除+理由代码}, 残差非零 → SystemExit(1)。
  2. 产出 config/company_bank_cooc_registry.yaml (加权引擎与 schema gate 的唯一 SSOT):
     条目 schema = {basename, family, source, col_by_track, track_agnostic, agg,
                    emit_tracks, short_name, label_elems, emit_panel, cut_code, range_gate}
     + 顶层 bank_company_map (D4 42 家) + excluded (列名→理由代码) + dv2_constants (v33 J2, WP5 常量区段)。
  3. emit 判定从负清单 COMPANY_BANK_COOC_PANEL_CUT_LIST_v23.txt 机械落值 (D17 ②;
     解析规格见计划 WP0-5: 段头全等匹配 / 数据行 = 族\t基名 / 对账前施 *_dcls→*_dm 别名映射 /
     仅锚 CUT 侧 410, 禁 keep==294/domain==704 断言)。
  4. D16 短名: 基名级判定与施加, 全列 ≤32 且全局唯一断言 fail-loud。
  5. 哈希锚 = sha256(canonical JSON, 键排序、剔除易变字段) + 两份名单文件内容哈希 (v20 防呆)。

用法: python company_listed_bank/01_build_company_bank_cooc_registry.py [--panel PATH] [--out PATH]
独立派生数据脚本, 不注册 DAG (镜像 generate_company_listed_names.py 定位)。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
CONFIG = REPO / "config"

logger = logging.getLogger("01_build_company_bank_cooc_registry")
if not logger.handlers:  # console 兜底 (被测试/importlib 导入时); main() 实跑时由 setup_logging 接管
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[WP0] %(levelname)s %(message)s"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)


def _init_stage_logging() -> None:
    """接入主管道日志基建 (core/logging.py::setup_logging): 写 company_listed_bank/logs/<stem>.log,
    格式/每次运行覆盖/50MB rotate 与主管道各阶段日志完全一致。单文件 importlib 加载, 不引入包依赖。"""
    import os
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return  # WP-A: 测试进程绝不接管文件日志 (2026-07-07 审计: 负例测试曾首写截断覆盖生产 02 日志)
    import importlib.util
    spec = importlib.util.spec_from_file_location("_np_core_logging", REPO / "core" / "logging.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.setup_logging(Path(__file__).stem, str(HERE / "logs"))
    # setup_logging 置 propagate=False (主管道防双打惯例); 本脚本进程 root 无 handler,
    # 恢复 True 无双打副作用, 且保 pytest caplog (root handler) 可捕 — 否则负例测试调过
    # main() 后, 同会话后续 caplog 断言静默失捕 (2026-07-07 实弹)
    logging.getLogger(Path(__file__).stem).propagate = True


def _rss_mb() -> float:
    import psutil
    return psutil.Process().memory_info().rss / 1024 / 1024


def _pkg_ver(name: str) -> str:
    """仅日志用途: 读已安装包版本 (importlib.metadata); 缺失/异常一律返回 'n/a', 不影响任何计算。"""
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return "n/a"


def _log_stage_header(panel_path: Path, out_path: Path) -> None:
    """阶段头汇报块 (完全参照主管道 12_news_fintech.log 的内容格式)。"""
    import os
    import platform
    import sys as _sys
    stem = Path(__file__).stem
    logger.info("--- 开始执行阶段: %s ---", stem)
    logger.info("=" * 72)
    logger.info("步骤 01: 银企共现面板测度注册表对账 (WP0; 五上游全划分 + 负清单机械落值 + sha256 哈希锚)")
    logger.info("=" * 72)
    logger.info("【功能】读五上游 (40/51/27/16/21_full) 全部列名, 把 40 面板每一列判定为")
    logger.info("        '纳入某基名的源列' 或 '排除+理由代码' (全划分, 残差非零即崩), 产出")
    logger.info("        config/company_bank_cooc_registry.yaml — 步骤 02/03 加权引擎与 schema gate 的唯一 SSOT。")
    logger.info("【方法】D15 排除正则+白名单 / D11 族规则解析不规则轨后缀; emit 判定从负清单")
    logger.info("        CUT_LIST_v23 机械落值 (仅锚 CUT 侧 410); D16 短名基名级施加 (≤32 且全局唯一);")
    logger.info("        D4 人工对照键经 variant 表解析归一到公司全称 (集合相等断言, 禁计数相等);")
    logger.info("        DV2 常量 import 自步骤 03 落 registry 区段 (双向锁)。")
    logger.info("【判读】40 面板残差 0 列是硬闸 (非 0 → SystemExit); 条目/emit/cut 对账负清单恰等;")
    logger.info("        registry_sha256 变更 = 盘上态漂移信号 → 须 bump 测试锚并级联重跑 02→03。")
    logger.info("【确定性】纯列名读取 + canonical JSON 哈希, 无 LLM/网络/API ($0); 同输入逐字节幂等")
    logger.info("          (2026-07-07 实证: 重跑前后 registry yaml git hash 一致)。")
    logger.info("")
    logger.info("  🧭 项目 / 环境信息")
    logger.info("     · 步骤: %s (WP0 注册表对账, company_listed_bank 流水线 01/03; 不注册主 DAG)", stem)
    logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板), 当前版本 v3.15.0")
    logger.info("     · 流水线定位: 上市公司×年 银企共现媒体报道面板 (105,032 行全谱) 三步生产链之第 1 步")
    logger.info("     · 下游消费者: 02 (WP1 加权引擎, 启动即校验本 registry 哈希锚, 缺则不跑) /")
    logger.info("       03 (WP5 七权互验, 经 dv2_constants 区段与本表双向锁) /")
    logger.info("       gate 测试 tests/test_company_bank_cooc_registry.py (12 用例, 锚死 registry_sha256 与族小计)")
    logger.info("     · 权威计划: scripts/audit/COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-03.md (v34, §4 WP0)")
    logger.info("     · 复现命令: python company_listed_bank/run_pipeline.py --steps 01")
    logger.info("       (或单跑: python company_listed_bank/%s.py [--panel PATH] [--out PATH])", stem)
    logger.info("     · 配置锚: 本流水线不消费 config/*.yaml 运行键 (参数全为脚本内常量 SSOT);")
    logger.info("       输入锚 = 两名单 + 负清单, 三者内容 sha256 落 registry.meta (v20 防呆)")
    logger.info("     · 模块文件: %s", Path(__file__).resolve())
    logger.info("     · 工作目录: %s", os.getcwd())
    logger.info("     · Python:   %s @ %s", platform.python_version(), _sys.executable)
    logger.info("     · 平台:     %s | CPU 逻辑核=%s", platform.platform(), os.cpu_count())
    logger.info("     · 关键库:   pandas=%s | numpy=%s | pyarrow=%s | PyYAML=%s",
                _pkg_ver("pandas"), _pkg_ver("numpy"), _pkg_ver("pyarrow"), _pkg_ver("PyYAML"))
    logger.info("     · 关键库:   psutil=%s | pyreadstat=%s | pyahocorasick=%s (缺失显示 n/a; 仅日志用途)",
                _pkg_ver("psutil"), _pkg_ver("pyreadstat"), _pkg_ver("pyahocorasick"))
    logger.info("     · PID=%s | RUN_ID=%s | 本步骤纯 CPU / 无 LLM·网络·API ($0) / 逐字节幂等",
                os.getpid(), os.environ.get("NEWS_PROCESS_RUN_ID", "standalone"))
    logger.info("  📂 输入 / 输出文件")
    logger.info("     · 输入(40): %s", panel_path)
    logger.info("       ↳ 角色: 主上游 = 银行×年全列面板 (全划分对象); 每列必判 '纳入源列' 或 '排除+理由码',")
    logger.info("         残差非零即 SystemExit(1); 列名经 parquet footer schema 读取, 零数据页 IO")
    logger.info("     · 输入(51/27/16/21_full): %s 下同名 parquet (域外族列名来源)", DATA)
    logger.info("       ↳ 角色: 51=覆盖控制增量 (CTRL 6 基名直读, 与 40 重复列判 DUP_OF_40) |")
    logger.info("         27=社会效益 4 维度六轨 (BD 族, 银行×年直读) | 16=文章级政策对齐 (PA 族, 注册聚合算子 mean) |")
    logger.info("         21_full=verified 留篇宇宙 (KW/FOCUS 族 track-agnostic 自聚合)")
    logger.info("     · 输入(负清单): %s", CUT_LIST_PATH)
    logger.info("       ↳ 角色: emit 判定唯一 SSOT (仅锚 CUT 侧 410 基名; 段头全等匹配, 数据行=族\\t基名,")
    logger.info("         对账前施 _dcls→_dm 别名映射; 禁 keep==294/domain==704 计数锚)")
    logger.info("     · 输入(两名单): %s | %s", CONFIG / "company_listed_names.yaml", CONFIG / "bank_names.json")
    logger.info("       ↳ 角色: D4 对照表构造输入 (机器 variant 交集 + 5 家人工键经 variant 表归一到公司全称)")
    logger.info("     · 输出:     %s (入库 SSOT, 供步骤 02/03 与 gate 测试消费)", out_path)
    logger.info("       ↳ schema: 五区段 {meta, entries, bank_company_map, excluded, dv2_constants}; 条目 12 字段")
    logger.info("         (basename/family/source/col_by_track/track_agnostic/agg/emit_tracks/short_name/")
    logger.info("          label_elems/emit_panel/cut_code/range_gate); 条目顺序 = 下游输出列序 SSOT")
    logger.info("       ↳ 缺失语义: DEFERRED 家族 (boilerplate/rare_word) 缺源列照出全 NaN 列; 其余缺源列"
                "基名默认不产列 (emit_tracks=[], 缺列容错; registry 推导 schema 跨环境恒等);")
    logger.info("         CUT 条目 emit_panel=false 仅留对账痕迹不投影")
    logger.info("  ⚙ 运行配置 (脚本内常量 SSOT)")
    logger.info("     · D16 短名替换表 %d 条 | DCLS→DM 别名 %d 条 | D4 人工对照 %d 家 | DEFERRED 基名 %d 个",
                len(SHORT_NAME_REPLACEMENTS), len(DCLS_ALIAS), len(MANUAL_BANK_COMPANY_MAP),
                len(DEFERRED_BASENAMES))
    logger.info("     · D15 排除规则 %d 条正则 + 强制纳入白名单 %d 项 + 不变式候选 (前缀 %d / 精确 %d / 政策正则 1)",
                len(EXCLUDE_RULES), len(INCLUDE_WHITELIST), len(INVARIANT_CANDIDATES_PREFIX),
                len(INVARIANT_CANDIDATES_EXACT))
    logger.info("  📖 方法论依据 (参考文献, 按主题分节; 每条附白话说明其支撑的具体设计决策)")
    logger.info("   —— A. 构念与效度 (文本测度目录 / 共现构念) ——")
    logger.info("     · Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature,")
    logger.info("       57(3), 535–574. https://doi.org/10.1257/jel.20181020")
    logger.info("       → 白话: 文本变量进计量前须显式声明构造规则与测度目录; 本步骤把 40 面板每列的纳入/排除")
    logger.info("         判定物化为机器可核验的注册表条目 (全划分+理由码), 即该原则的工程落地。")
    logger.info("     · Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey.")
    logger.info("       Journal of Accounting Research, 54(4), 1187–1230. https://doi.org/10.1111/1475-679X.12123")
    logger.info("       → 白话: 文本测度结论对口径选择高度敏感、须全程留痕; excluded 理由码 + 三输入内容 sha256")
    logger.info("         即本脚本给每个口径决策留下的可审计痕迹。")
    logger.info("     · Bybee, L., Kelly, B. T., Manela, A., & Xiu, D. (2024). Business news and business cycles.")
    logger.info("       The Journal of Finance, 79(5), 3105–3147. https://doi.org/10.1111/jofi.13377")
    logger.info("       → 白话: 把海量商业新闻压成结构化面板测度, 前提是字段目录稳定; 本注册表为 700+ 基名冻结")
    logger.info("         族/轨/聚合算子, 保证步骤 02 加权引擎跨重跑产出同一测度集合。")
    logger.info("     · Baker, S. R., Bloom, N., & Davis, S. J. (2016). Measuring economic policy uncertainty.")
    logger.info("       The Quarterly Journal of Economics, 131(4), 1593–1636. https://doi.org/10.1093/qje/qjw024")
    logger.info("       → 白话: 共现计数型文本指标的效度取决于筛选规则透明且固定; D15 排除规则 (10 条正则+不变式三件)+白名单把")
    logger.info("         银企共现测度的列级筛选规则固化, 消除随手改口径的空间。")
    logger.info("     · Lee, C. M. C., Ma, P., & Wang, C. C. Y. (2015). Search-based peer firms: Aggregating investor")
    logger.info("       perceptions through internet co-searches. Journal of Financial Economics, 116(2), 410–431.")
    logger.info("       https://doi.org/10.1016/j.jfineco.2015.02.003")
    logger.info("       → 白话: 该文证明'共同被检索'携带经济关联信息, 为同类'共同被提及'共现构念提供同型前提;")
    logger.info("         D4 对照表在源头剔除上市银行'自我共现'的机械污染。")
    logger.info("     · Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk:")
    logger.info("       Measurement and effects. The Quarterly Journal of Economics, 134(4), 2135–2202.")
    logger.info("       https://doi.org/10.1093/qje/qjz021")
    logger.info("       → 白话: 该文示范了 firm-level 文本测度的系统构造与验证纪律; 本注册表以 range_gate")
    logger.info("         (tone/frac/none) 把每族值域断言机器化以延伸该纪律, 供下游 WP3 gate 逐列复核。")
    logger.info("   —— B. 识别与加权 (份额加权 / 规格全枚举 / 多重检验纪律) ——")
    logger.info("     · Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why,")
    logger.info("       and how. American Economic Review, 110(8), 2586–2624. https://doi.org/10.1257/aer.20181047")
    logger.info("       → 白话: 份额加权测度的可信度取决于权重构成完全透明; 本表冻结进入 02 号 cw/ce 双臂投影的")
    logger.info("         全部源列与轨别, 使'权重×测度'的每一格可回溯到唯一源列。")
    logger.info("     · Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis.")
    logger.info("       Nature Human Behaviour, 4(11), 1208–1214. https://doi.org/10.1038/s41562-020-0912-z")
    logger.info("       → 白话: 规格曲线要求把合理规格全枚举而非只报其一; emit_tracks 三轨 + track-agnostic 判定")
    logger.info("         把每个基名的可用测量臂全部登记, 不留隐藏抽屉。")
    logger.info("     · Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016). Increasing transparency")
    logger.info("       through a multiverse analysis. Perspectives on Psychological Science, 11(5), 702–712.")
    logger.info("       https://doi.org/10.1177/1745691616658637")
    logger.info("       → 白话: 多重宇宙分析主张把数据处理分叉显式化; CUT 410/KEEP 的裁剪来自负清单一次性审定,")
    logger.info("         本脚本仅机械落值, 每个分叉点都留档在 cut_code 字段。")
    logger.info("     · Harvey, C. R., Liu, Y., & Zhu, H. (2016). … and the cross-section of expected returns.")
    logger.info("       The Review of Financial Studies, 29(1), 5–68. https://doi.org/10.1093/rfs/hhv059")
    logger.info("       → 白话: 测度越多假发现风险越高, 须先固定检验域再谈显著性; 本表把 emit 域锚死在负清单之外,")
    logger.info("         是下游多重检验校正的前置纪律。")
    logger.info("   —— C. 数据工程与复现 (分析者自由度 / 复现材料标准) ——")
    logger.info("     · Menkveld, A. J., Dreber, A., Holzmeister, F., Huber, J., Johannesson, M., Kirchler, M.,")
    logger.info("       Razen, M., Weitzel, U., … [百人合著] (2024). Nonstandard errors. The Journal of Finance,")
    logger.info("       79(3), 2339–2390. https://doi.org/10.1111/jofi.13337")
    logger.info("       → 白话: 同一数据不同团队得出不同结果的根源是未记录的口径分叉; registry_sha256 把整个")
    logger.info("         测度目录压成单一指纹, 任何口径漂移都会让 gate 测试即刻翻红。")
    logger.info("     · Chen, A. Y., & Zimmermann, T. (2022). Open source cross-sectional asset pricing.")
    logger.info("       Critical Finance Review, 11(2), 207–264. https://doi.org/10.1561/104.00000112")
    logger.info("       → 白话: 开源资产定价库示范了'变量目录+可复现构造代码'的复现材料范式; 本 yaml 即银企共现")
    logger.info("         面板的入库变量目录, 供审稿人逐条目核对来源与口径。")
    logger.info("     · Brodeur, A., Mikola, D., Cook, N., … [百人合著] (2026). Reproducibility and robustness of")
    logger.info("       economics and political science research. Nature, 652(8108), 151–156.")
    logger.info("       https://doi.org/10.1038/s41586-026-10251-x")
    logger.info("       → 白话: 大规模复现研究显示数据构造不透明是复现失败的常见原因之一; 本步骤 $0、纯列名、逐字节幂等,")
    logger.info("         任何第三方按复现命令重跑应得到相同 registry_sha256。")
    logger.info("     · Dreber, A., & Johannesson, M. (2024). A framework for evaluating reproducibility and")
    logger.info("       replicability in economics. Economic Inquiry, 63(2), 338–356. https://doi.org/10.1111/ecin.13244")
    logger.info("       → 白话: 复现性评估须先界定'同数据同代码'的边界; 哈希锚 + 三输入内容指纹恰好给出该边界 —")
    logger.info("         指纹一致而产物不同即为真缺陷, 而非口径漂移。")
    logger.info("")


CUT_LIST_PATH = REPO / "scripts" / "audit" / "COMPANY_BANK_COOC_PANEL_CUT_LIST_v23.txt"

TRACKS = ("full", "ctx", "ss")

# ---------------------------------------------------------------- D16 短名替换表
# 应用序 = 表序、单遍替换 (计划 D16 + v19 xneg 补丁); 基名级判定与施加 (v20 封口)。
SHORT_NAME_REPLACEMENTS = [
    ("policy_cosine_sim", "polsim"),
    ("avg_fintech_distinct_keywords", "avg_ft_dkw"),
    ("avg_within_doc_redund", "avg_wdred"),
    ("avg_redund_han_log_length", "avg_redhan_ll"),
    ("avg_redund_log_length", "avg_red_ll"),
    ("attention_intensity_density", "attn_int_dens"),
    ("attention_intensity_sd", "attn_int_sd"),
    ("attention_attr_share", "attn_attr_shr"),
    ("washing_ratio_", "wash_"),
    ("washing_asymmetry", "wash_asym"),
    ("washing_tone_shift", "wash_tshift"),
    ("hidden_adopt_", "hid_adopt_"),
    ("assortativity", "assort"),
    ("cross_outlet_tone_variance", "xoutlet_tone_var"),
    ("_cont_mean_", "_cont_"),
    ("xneg_frac_t", "xnegf_t"),
    ("semantic_staleness", "sem_stale"),
    ("semantic_highstale", "sem_histale"),
    ("surface_staleness", "surf_stale"),
    ("surface_highstale", "surf_histale"),
    ("nominalization", "nominaliz"),
    ("_effective_size", "_eff_size"),
    ("coverage_continuity", "cov_contin"),
    ("coverage_active_days", "cov_act_days"),
    ("_net_tone_", "_nt_"),
    ("industry_neg_shock", "ind_neg_shock"),
    ("_target_mention_count", "_tgt_mention_cnt"),
    ("mean_num_intensity_word", "mean_numint_w"),
    ("_within_doc_", "_wd_"),
]

# 负清单 _dcls → _dm 固定别名映射 (恰 6 条, 计划 WP0-5)
DCLS_ALIAS = {f"llm_vote_tone_{d}_dcls": f"llm_vote_tone_{d}_dm"
              for d in ("tech", "app", "sub", "symb", "indep", "collab")}

# D4 人工维护对照表 (5 家逃逸, v18/v23 逐家查定; 与机器 variant 交集并成 42 家)。
# ⚠ 键为证券简称 (计划原文形态), 构建时经 variant 表解析归一到 company_listed_name 全称 —
# 直接当键用会对 own-bank 剔除静默 no-op (结果评审 R3 P0-1 实弹)。
MANUAL_BANK_COMPANY_MAP = {
    "常熟银行": ["江苏常熟农村商业银行"],
    "瑞丰银行": ["浙江绍兴瑞丰农村商业银行"],
    "江阴银行": ["江苏江阴农村商业银行"],
    "张家港行": ["江苏张家港农村商业银行"],
    "青农商行": ["青岛农村商业银行"],
}

# ---------------------------------------------------------------- DV2 常量 (v33 J2: WP0 import WP5 模块常量落 registry 区段, 双向锁)
def _load_dv2_constants() -> dict:
    # 序号前缀模块名 (03_*) 非合法 import 语句标识符 → 走 importlib
    here = str(Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    try:
        import importlib  # noqa: PLC0415
        w8 = importlib.import_module("03_build_company_bank_weight_validation")
        return w8.DV2_CONSTANTS
    except Exception as exc:  # WP5 脚本未就绪时 (WP0 首跑早于 WP5) 用空占位, WP5 落地后重跑 WP0 回填
        logger.warning("导入 03 (WP5) 失败, dv2_constants 落空占位 — WP5 已落地的现状下这属异常, "
                       "须排查 03 模块 import 期错误而非重跑 WP0: %r", exc)
        return {}


# ---------------------------------------------------------------- 哈希锚 canonical 式 (SSOT)
def registry_content_sha256(registry: dict) -> str:
    """哈希锚 = sha256(canonical JSON, 键排序) over 四内容区段 (meta 刻意不入锚, 防自指)。

    本函数是运行时侧唯一实现: 01 写锚 / 02 启动复算校验均调本函数 (02 经 importlib 复用,
    禁第二份实现); gate 测试 test_registry_hash_anchor 保留独立重算式作双实现互证。"""
    anchor_obj = {k: registry[k] for k in ("entries", "bank_company_map", "excluded", "dv2_constants")}
    return hashlib.sha256(
        json.dumps(anchor_obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- 上游列名读取
def read_cols(path: Path) -> list[str]:
    import pyarrow.parquet as pq
    names = pq.ParquetFile(path).schema_arrow.names
    return [n for n in names if n != "__index_level_0__"]


# ---------------------------------------------------------------- 负清单解析 (计划 WP0-5 规格)
def parse_cut_list(path: Path) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()

    def segment(header: str) -> list[tuple[str, str]]:
        try:
            i = lines.index(header)  # 全等段头 (禁前缀匹配)
        except ValueError:
            raise SystemExit(f"负清单缺段头 {header!r}")
        rows: list[tuple[str, str]] = []
        for line in lines[i + 1:]:
            if line.startswith("==="):
                break
            if not line.strip() or line.startswith("#"):
                continue
            fam, base = line.split("\t")
            rows.append((fam, base))
        return rows

    return segment("===[CUT 410]==="), segment("===[KEEP 294]===")


# ---------------------------------------------------------------- 源列解析 (不规则后缀显式映射, 引擎零推断)
# C1/QD/DS 不规则轨后缀 (D11 C1/QD 行 + D11c DS 行)
C1_TRACK_SUFFIX = {
    "tech_frac": ("", "_lc", "_ls"), "app_frac": ("", "_lc", "_ls"),
    "sub_frac": ("", "_sc", "_ss"), "symb_frac": ("", "_sc", "_ss"),
    "indep_frac": ("", "_cm", "_cm_ss"), "collab_frac": ("", "_cm", "_cm_ss"),
}
QD_TRACK_SUFFIX = {
    "n_articles_tech": ("", "_lc_ctx", "_ls_ss"), "n_articles_app": ("", "_lc_ctx", "_ls_ss"),
    "n_articles_sub": ("", "_sc_ctx", "_ss_ss"), "n_articles_symb": ("", "_sc_ctx", "_ss_ss"),
    "n_articles_indep": ("", "_cm_ctx", "_cm_ss"), "n_articles_collab": ("", "_cm_ctx", "_cm_ss"),
}
DS_DM_SUFFIX = {  # _dm 孪生: 无 full 轨 (v23 终审: 源列实存 12 列)
    "llm_vote_tone_tech_dm": ("llm_vote_tone_tech_lc_ctx", "llm_vote_tone_tech_ls_ss"),
    "llm_vote_tone_app_dm": ("llm_vote_tone_app_lc_ctx", "llm_vote_tone_app_ls_ss"),
    "llm_vote_tone_sub_dm": ("llm_vote_tone_sub_sc_ctx", "llm_vote_tone_sub_ss_ss"),
    "llm_vote_tone_symb_dm": ("llm_vote_tone_symb_sc_ctx", "llm_vote_tone_symb_ss_ss"),
    "llm_vote_tone_indep_dm": ("llm_vote_tone_indep_cm_ctx", "llm_vote_tone_indep_cm_ss"),
    "llm_vote_tone_collab_dm": ("llm_vote_tone_collab_cm_ctx", "llm_vote_tone_collab_cm_ss"),
}
# DEFERRED 承诺缺轨全集 (计划 D11b AT 行/v23 判定程序; 缺源列仍照出全 NaN 列)
DEFERRED_BASENAMES = {
    "du_2022_polw00_tone", "du_2022_polw10_tone",
    "gpt54nano_sub_frac", "gpt54nano_tech_frac", "gpt54nano_collab_frac",
    "gemini31_sub_frac", "gemini31_tech_frac", "gemini31_collab_frac",
    "deepseekv4_sub_frac", "deepseekv4_tech_frac", "deepseekv4_collab_frac",
    "avg_boilerplate", "avg_rare_word_c2", "avg_rare_word_c5",
}


def resolve_cols(base: str, colset: set[str]) -> tuple[dict, bool]:
    """基名 → {full/ctx/ss: 源列名或 None}, track_agnostic。不规则后缀全部显式。"""
    # C1 / QD / DS-dm 显式映射
    if base in C1_TRACK_SUFFIX or base in QD_TRACK_SUFFIX:
        sfx = (C1_TRACK_SUFFIX | QD_TRACK_SUFFIX)[base]
        cols = {t: (base + s if base + s in colset else None) for t, s in zip(TRACKS, sfx)}
        return cols, False
    if base in DS_DM_SUFFIX:
        c, s = DS_DM_SUFFIX[base]
        return {"full": None, "ctx": c if c in colset else None, "ss": s if s in colset else None}, False
    # track 后置参数后缀族: herd thr / attention j 梯子 (avg_herd_weight_full_thr25 / attention_index_full_j70w5)
    m = re.match(r"^(.*)_((?:thr|j)\d+(?:w\d+)?)$", base)
    if m:
        stem, sfx = m.groups()
        cols = {t: (f"{stem}_{t}_{sfx}" if f"{stem}_{t}_{sfx}" in colset else None) for t in TRACKS}
        if any(cols.values()):
            return cols, False
    # 嵌入 lg 后置族: semantic_staleness_lg → semantic_staleness_{t}_lg (track 中置)
    if base.endswith("_lg"):
        stem = base[:-3]
        cols = {t: (f"{stem}_{t}_lg" if f"{stem}_{t}_lg" in colset else None) for t in TRACKS}
        if any(cols.values()):
            return cols, False
    # 标准 _{track} 后缀
    std = {t: (f"{base}_{t}" if f"{base}_{t}" in colset else None) for t in TRACKS}
    # full 轨裸名族 (washing_ratio 系/strat 带 N/AS 扩/IN/NW-cogn 等): 裸名在列集且 _full 缺席 → full=裸名
    if std["full"] is None and base in colset:
        if std["ctx"] is not None or std["ss"] is not None:
            std["full"] = base
            return std, False
        # 三轨全无 + 裸名在 → track-agnostic 单列
        return {t: base for t in TRACKS}, True
    if any(std.values()):
        return std, False
    return std, False  # 全 None → DEFERRED 或结构缺席, 调用方判


# ---------------------------------------------------------------- D15 排除规则 (正则+白名单, 全列双评)
# 白名单强制纳入 (排除正则命中但属测度, D15 ⑦ 豁免 + ③ 豁免)
INCLUDE_WHITELIST = {
    "avg_subst_prob_score", "avg_locus_prob_score", "avg_collab_prob_score",  # C1b (D11e)
    "mean_frac_definite", "frac_amb_articles",  # CL (D11f)
    "llm_vote_tone_std",  # DA 分歧构念本体 (D15 ③ 唯一豁免; WP0-6 ③ 核查义务)
    "avg_bank_count", "max_bank_count",  # CS 族, 恰以 _count 结尾
}
# ⑪ 银行不变式候选枚举清单 (作用域定死, v21)
INVARIANT_CANDIDATES_PREFIX = ("net_",)
INVARIANT_CANDIDATES_EXACT = {"stress_period"}
POLICY_INVARIANT_RE = re.compile(r"^(dcep|sandbox|depins)_(treated|post)(_|$)")

TRACK_STRIP_RE = re.compile(r"_(full|ctx|ss)(?=(_|$))")

EXCLUDE_RULES: list[tuple[str, re.Pattern]] = [
    # ① 他行/同组测度 (含 _exc 后缀补丁)
    ("D15_1_PEER", re.compile(r"(_leave1out_|^lpeer_|^leave_one_out_|^exc_|^prox_.*km_|^peer_tone|^emb_peer|^llm_peer_|_exc$)")),
    # ② IV 族
    ("D15_2_IV", re.compile(r"(^bartik_|^outlet_.*_iv|_iv$|_iv_)")),
    # ③ _std/_sum/_count/_skew 伴生 (先剥轨后缀, 双向正则)
    ("D15_3_MOMENT", re.compile(r"_(std|sum|count|skew)(_|$)")),
    # ④ z-score 孪生
    ("D15_4_Z", re.compile(r"_z$")),
    # ⑤ gap 差分
    ("D15_5_GAP", re.compile(r"(^tone_gap_|^attention_gap_|_gap_|_gap$)")),
    # ⑥ 立方胞与交互 + per-BERT-model 维度切片 (D15 ⑥ 收窄条款: ensemble 级 bert_avg_*_{dim} 纳入, per-model 仍除外)
    ("D15_6_INTERACT", re.compile(
        r"(^n_articles_cell_(\d|NA)|^tone_x_|_ddd(_|$)|_x_dcep|_x_sandbox|_x_depins"
        r"|^(finbert_cn|fin_sent_zh|finbert2)_(pos|neg|neu)_(tech|app|sub|symb|indep|collab)$)")),
    # ⑦ 质量诊断
    ("D15_7_DIAG", re.compile(
        r"(_confidence|_prob_|_conf$|_conf_|avg_agreement_rate|_disagree_frac|_freerider_frac|_quietworker_frac"
        r"|^frac_(ctx|ss)_fallback|_bothvalid|_independence|prox_geo_imputed_frac"
        r"|_(disagree|freerider|quietworker)(_frac)?$"
        r"|^has_coverage|^high_coverage|^dummy_no_positive_news|^low_conf_flag|^d4_data_quality_flag)")),
    # ⑧ 别名与纯变换
    ("D15_8_ALIAS", re.compile(
        r"(^ln_|_ln_coverage|^zero_coverage|^fintech_intensity_mean|^n_fintech_articles"
        r"|^du_2022_polw05_tone|^avg_ft_intensity(_lg)?$)")),
    # ⑨ 预烘焙滞后与 event-time 簿记
    ("D15_9_LAG_EVENT", re.compile(
        r"(_lag\d|_lead\d|_lead4plus|_lag4plus|_rel_year|_treat_year|_lag0(_|$))")),
    # ⑩ 环境/规制/静态属性/地理聚合层/分母簿记
    ("D15_10_ENV_STATIC", re.compile(
        r"(^ai_reg_|^bank_(type|scale|zone|province|city|scale_ord)$|^ft_(attn|vol)_(yr|prov|city)"
        r"|^n_articles_llm_valid|^n_words_real|^n_han_real)")),
]


def classify_excluded(col: str) -> str | None:
    """对未被任何基名源列引用的列给排除理由码; 无匹配 → None (残差)。"""
    stripped = TRACK_STRIP_RE.sub("", col)
    # 键列
    if col in {"target_bank", "year"}:
        return "KEY"
    # ⑪ 银行不变式候选清单 (族命中优先于 ⑪ — 本函数只对未纳入列调用, 天然满足)
    if col.startswith(INVARIANT_CANDIDATES_PREFIX) or stripped in INVARIANT_CANDIDATES_EXACT \
            or POLICY_INVARIANT_RE.match(stripped):
        return "D15_11_INVARIANT"
    for code, pat in EXCLUDE_RULES:
        if pat.search(stripped) or pat.search(col):
            return code
    # sum_/min_ 前缀簿记族 (D15 漏网修正)
    if re.match(r"^(sum|min)_", col):
        return "D15_3_MOMENT"
    return None


# ---------------------------------------------------------------- range_gate 判定 (v23: WP3 值域断言载体)
TONE_FAMILIES = {"S1", "S2", "S3", "S4", "S1b", "S5", "DS"}
FRAC_FAMILIES = {"C1", "C2", "S1c", "S6"}


def range_gate_for(base: str, family: str) -> str:
    if family in {"DA", "TD", "CS"}:
        return "none"
    if family in FRAC_FAMILIES:
        return "frac"
    if family in TONE_FAMILIES and ("tone" in base or "_cont" in base or base.endswith("_cont")):
        return "tone"
    if family == "S4" or re.search(r"_net_tone$", base):
        return "tone"
    if family == "S4b" and re.search(r"_(pos|neg|neu)$", base):
        return "frac"
    if re.search(r"_frac$|_frac_", base) and family not in {"DA", "TD", "CS", "MC", "CV"}:
        return "frac"
    return "none"


# ---------------------------------------------------------------- 域外条目 (PA/KW/FOCUS/BD/CTRL, ~25 基名)
def build_offpanel_entries(cols16: set[str], cols27: set[str], cols51: set[str]) -> list[dict]:
    entries: list[dict] = []
    # PA 政策对齐 (16 号文章级, 自聚合 mean; 中缀序 lg 先 allv 后)
    for stem in ("policy_cosine_sim", "policy_cosine_sim_allv",
                 "policy_cosine_sim_lg", "policy_cosine_sim_lg_allv"):
        cols = {t: (f"{stem}_{t}" if f"{stem}_{t}" in cols16 else None) for t in TRACKS}
        entries.append(dict(basename=stem, family="PA", source="16", col_by_track=cols,
                            track_agnostic=False, agg="mean"))
    # KW 金科关键词 (21_full 文章级, track-agnostic 自聚合; 输出基名加 avg_ 前缀)
    kw_map = {
        "avg_fintech_total_count": ("fintech_total_count", "mean"),
        "avg_fintech_upper_count": ("fintech_upper_count", "mean"),
        "avg_fintech_lower_count": ("fintech_lower_count", "mean"),
        "avg_fintech_distinct_keywords": ("fintech_distinct_keywords", "mean"),
        "avg_fintech_in_title": ("fintech_in_title", "share"),
    }
    for out, (src, agg) in kw_map.items():
        entries.append(dict(basename=out, family="KW", source="21", track_agnostic=True,
                            col_by_track={t: src for t in TRACKS}, agg=agg))
    # 聚焦度 (21_full 自聚合, D11e CS 扩; 归 FOCUS 族标签便于对账, 语义属 CS 报道形态)
    for out, src in (("avg_mention_density", "mention_density"),
                     ("avg_target_mention_count", "target_bank_mention_count")):
        entries.append(dict(basename=out, family="FOCUS", source="21", track_agnostic=True,
                            col_by_track={t: src for t in TRACKS}, agg="mean"))
    # BD 社会效益 4 维度 (27 号银行×年, 六轨齐 lg 中置)
    for dim in ("core_op", "growth", "resource", "compliance"):
        for lg in ("", "_lg"):
            stem = f"benefit_{dim}{lg}"
            cols = {t: (f"benefit_{dim}{lg}_{t}" if f"benefit_{dim}{lg}_{t}" in cols27 else None)
                    for t in TRACKS}
            entries.append(dict(basename=stem, family="BD", source="27", col_by_track=cols,
                                track_agnostic=False, agg=None))
    # CTRL 覆盖控制增量 (51 号相对 40 新增 level 量, track-agnostic 直读)
    for stem in ("fintech_share", "nf_n_articles", "all_n_articles",
                 "ft_n_articles_dedup", "nf_headline_frac", "nf_media_breadth"):
        if stem in cols51:
            entries.append(dict(basename=stem, family="CTRL", source="51", track_agnostic=True,
                                col_by_track={t: stem for t in TRACKS}, agg=None))
        else:
            cols = {t: (f"{stem}_{t}" if f"{stem}_{t}" in cols51 else None) for t in TRACKS}
            entries.append(dict(basename=stem, family="CTRL", source="51",
                                track_agnostic=False, col_by_track=cols, agg=None))
    for e in entries:
        e.setdefault("emit_panel", True)
        e.setdefault("cut_code", None)
    return entries


# ---------------------------------------------------------------- D4 42 家对照表
def build_bank_company_map(companies: list[dict], banks: list[dict]) -> dict[str, list[str]]:
    bank_variant_owner: dict[str, set[str]] = {}
    for b in banks:
        for v in b["variants"]:
            bank_variant_owner.setdefault(v, set()).add(b["bank_name"])
    company_variant_owner: dict[str, list[str]] = {}
    for c in companies:
        for v in c["variants"]:
            company_variant_owner.setdefault(v, []).append(c["company_listed_name"])
    mapping: dict[str, set[str]] = {}
    name_flag_set: set[str] = set()
    for c in companies:
        name = c["company_listed_name"]
        hit = set()
        for v in c["variants"]:
            hit |= bank_variant_owner.get(v, set())
        if hit:
            mapping[name] = hit
        if ("银行" in name) or ("农商" in name):
            name_flag_set.add(name)
    n_machine = len(mapping)
    # 人工 5 家: 证券简称经 variant 表解析归一到 company_listed_name 全称 (R3 P0-1 修复)
    for alias, extra in MANUAL_BANK_COMPANY_MAP.items():
        owners = company_variant_owner.get(alias, [])
        if len(owners) != 1:
            raise SystemExit(f"D4 人工对照键 {alias!r} 解析到 {len(owners)} 家公司 (须唯一) — 人工目检")
        mapping.setdefault(owners[0], set()).update(extra)
        logger.info("D4 人工对照解析: 证券简称 %s → 全称 %s (own-bank 对照: %s)",
                    alias, owners[0], "/".join(extra))
    logger.info("D4 对照表构建: 机器 variant 交集 %d 家 + 人工 %d 家解析并入 → 合计 %d 家 "
                "(全称含'银行/农商'公司集 %d 家, 集合相等断言待验)",
                n_machine, len(MANUAL_BANK_COMPANY_MAP), len(mapping), len(name_flag_set))
    # 覆盖性断言 (D4, R3 P0-1 升级为集合相等 — 计数锚对成员错位盲):
    # 对照表键集合 == 全称含银行/农商的公司集合
    if set(mapping) != name_flag_set:
        diff = set(mapping) ^ name_flag_set
        raise SystemExit(
            f"D4 覆盖性断言失败: 对照表键集合 ≠ 全称含银行/农商公司集合, 对称差 {sorted(diff)} — 逐家人工目检")
    return {k: sorted(v) for k, v in sorted(mapping.items())}


# ---------------------------------------------------------------- 短名
def apply_short_name(base: str) -> str:
    s = base
    for old, new in SHORT_NAME_REPLACEMENTS:
        s = s.replace(old, new)
    return s


def finalize_short_names(entries: list[dict]) -> None:
    for e in entries:
        base = e["basename"]
        longest = max(len(f"{arm}_{base}_{t}") for arm in ("cw", "ce") for t in TRACKS)
        if longest <= 32:
            e["short_name"] = base
        else:
            short = apply_short_name(base)
            if max(len(f"{arm}_{short}_{t}") for arm in ("cw", "ce") for t in TRACKS) > 32:
                raise SystemExit(f"D16 短名替换后仍超 32: {base} -> {short}")
            e["short_name"] = short
    # 全局唯一断言 (投影列级)
    seen: dict[str, str] = {}
    for e in entries:
        if not e["emit_panel"]:
            continue
        for arm in ("cw", "ce"):
            for t in e["emit_tracks"]:
                name = f"{arm}_{e['short_name']}_{t}"
                if len(name) > 32:
                    raise SystemExit(f"D16 断言失败: 投影列 {name} 超 32 字符")
                if name in seen:
                    raise SystemExit(f"D16 断言失败: 短名碰撞 {name} ({seen[name]} vs {e['basename']})")
                seen[name] = e["basename"]


# ---------------------------------------------------------------- 主流程
def main(argv=None) -> int:
    _init_stage_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default=str(DATA / "40_panel_yearly.parquet"))
    ap.add_argument("--out", default=str(CONFIG / "company_bank_cooc_registry.yaml"))
    args = ap.parse_args(argv)
    import time
    t_start = time.monotonic()
    _log_stage_header(Path(args.panel), Path(args.out))

    t0 = time.monotonic()
    cols40 = read_cols(Path(args.panel))
    cols51 = read_cols(DATA / "51_panel_with_controls.parquet")
    cols27 = read_cols(DATA / "27_benefit_dimensions_panel.parquet")
    cols16 = read_cols(DATA / "16_article_alignment.parquet")
    cols21 = read_cols(DATA / "21_tone_llms_full.parquet")
    set40, set51, set27, set16, set21 = map(set, (cols40, cols51, cols27, cols16, cols21))
    t_load = time.monotonic() - t0
    logger.info("正在从 %s 加载五上游列名...", DATA)
    logger.info("  📐 输入 schema: 40 面板=%s 列 | 51=%s | 27=%s | 16=%s | 21_full=%s",
                f"{len(cols40):,}", f"{len(cols51):,}", f"{len(cols27):,}",
                f"{len(cols16):,}", f"{len(cols21):,}")
    logger.info("  📐 读取方式: 仅 parquet footer schema (零数据页 IO), __index_level_0__ 簿记列已剥除;")
    logger.info("     列数即行列规模中的'列'维 (本步骤纯 schema 驱动, 不读任何数据行, 与行数/T 无关)")
    logger.info("[Memory] 列名加载后 | RSS: %.4g MB", _rss_mb())

    t0 = time.monotonic()
    cut_rows, keep_rows = parse_cut_list(CUT_LIST_PATH)
    # 对账前施 _dcls→_dm 别名映射 (仅按基名集合)
    cut_bases = [(fam, DCLS_ALIAS.get(b, b)) for fam, b in cut_rows]
    if len({b for _, b in cut_bases}) != 410:
        raise SystemExit(f"负清单 CUT 段物化后应恰 410 基名, 实得 {len({b for _, b in cut_bases})}")
    cut_set = {b for _, b in cut_bases}
    n_alias = sum(1 for _, b in cut_rows if b in DCLS_ALIAS)
    logger.info("负清单 CUT_LIST_v23 解析: CUT 段 %d 行 / KEEP 段 %d 行 | _dcls→_dm 别名映射命中 %d 条"
                " | CUT 物化 %d 基名 (恰 410 硬闸 ✓, 禁 keep/domain 计数锚)",
                len(cut_rows), len(keep_rows), n_alias, len(cut_set))

    # WP0-6 修正: ② lazy 幽灵基名并入标准三轨注册 (KEEP 段 6 条 lazy → 3 真基名)
    keep_bases: list[tuple[str, str]] = []
    seen_keep: set[str] = set()
    for fam, b in keep_rows:
        b2 = re.sub(r"^(lazy_(?:jaccard|overlap|minedit))_full$", r"\1", b)
        if b2 not in seen_keep:
            keep_bases.append((fam, b2))
            seen_keep.add(b2)
    if len(keep_rows) != len(keep_bases):
        logger.info("KEEP 段 lazy 幽灵基名折叠: %d 行 → %d 基名 (lazy_{jaccard,overlap,minedit} 并入"
                    "标准三轨注册, WP0-6 ②)", len(keep_rows), len(keep_bases))
    # WP0-6 ③ llm_vote_tone_std 白名单入 DA 族纳入域 (负清单缺席即保留);
    # 同机制 (v21 干跑被 ⑦ 正则吞掉) 的 C1b 三基名一并核查补注册 — 白名单豁免列须证入纳入域
    for fam, wl in (("DA", "llm_vote_tone_std"), ("C1b", "avg_subst_prob_score"),
                    ("C1b", "avg_locus_prob_score"), ("C1b", "avg_collab_prob_score")):
        if wl not in seen_keep and wl not in cut_set:
            keep_bases.append((fam, wl))
            seen_keep.add(wl)
            logger.warning("白名单豁免基名 %s 不在负清单域, 按 WP0-6 ③ 先例补注册 (族 %s, emit_panel=true)",
                           wl, fam)

    # 40 面板域条目构造 (KEEP + CUT 全在划分域; CUT 打 emit_panel=false)
    entries: list[dict] = []
    domain_rows = [(fam, b, True) for fam, b in keep_bases] + [(fam, b, False) for fam, b in cut_bases]
    unresolved: list[str] = []
    for fam, base, emit in domain_rows:
        cols, ta = resolve_cols(base, set40)
        present = [t for t in TRACKS if cols.get(t)]
        if not present:
            # 注册在案基名盘上缺源列 → 缺列容错 (全缺失列 + loud WARNING, schema 恒等 registry
            # 推导值跨环境不变 — 计划 D11 缺列容错条款; DEFERRED 与共享树 40 面板漂移缺席同待遇)
            cols, ta = {t: None for t in TRACKS}, False
            present = list(TRACKS)
            if base not in DEFERRED_BASENAMES:
                unresolved.append(base)
        if ta:
            emit_tracks = list(TRACKS)  # track-agnostic 按权重轨照出三列
        elif base in DEFERRED_BASENAMES:
            emit_tracks = list(TRACKS)  # DEFERRED 承诺缺轨照出全 NaN
        elif base in DS_DM_SUFFIX:
            emit_tracks = [t for t in TRACKS if cols.get(t)]  # _dm 无 full 结构缺席
        elif base == "avg_boilerplate" or base.startswith("avg_rare_word"):
            emit_tracks = list(TRACKS)  # DEFERRED 家族
        else:
            emit_tracks = [t for t in TRACKS if cols.get(t)]  # 结构性缺席不出列 (AT 等)
        entries.append(dict(
            basename=base, family=fam, source="40", col_by_track=cols, track_agnostic=ta,
            agg=None, emit_tracks=emit_tracks, emit_panel=emit,
            cut_code=("CUT_V23" if not emit else None)))
    if unresolved:
        logger.warning("%d 个注册在案基名盘上缺全部源列 (共享树 40 面板漂移/DEFERRED), 按缺列容错默认不产列"
                       " (emit_tracks=[], 面板无此列族; boilerplate/rare_word DEFERRED 家族例外仍出全 NaN 列):",
                       len(unresolved))
        for b in unresolved:
            logger.warning("    %s", b)
    n_keep_dom = sum(1 for e in entries if e["emit_panel"])
    n_ta = sum(1 for e in entries if e["track_agnostic"])
    n_def = sum(1 for e in entries if e["basename"] in DEFERRED_BASENAMES)
    per_track = {t: sum(1 for e in entries if e["col_by_track"].get(t)) for t in TRACKS}
    logger.info("40 面板域条目构造: %d 条 (KEEP emit=%d / CUT emit_panel=false=%d) | track-agnostic=%d"
                " | DEFERRED 注册=%d (缺源列才容错落全 NaN) | 逐轨源列解析 full=%d / ctx=%d / ss=%d",
                len(entries), n_keep_dom, len(entries) - n_keep_dom, n_ta, n_def,
                per_track["full"], per_track["ctx"], per_track["ss"])

    # 域外条目 (PA/KW/FOCUS/BD/CTRL)
    off = build_offpanel_entries(set16, set27, set51)
    for e in off:
        if e.get("track_agnostic"):
            e["emit_tracks"] = list(TRACKS)
        else:
            e["emit_tracks"] = [t for t in TRACKS if e["col_by_track"].get(t)]
    entries.extend(off)
    off_fams: dict[str, int] = {}
    for e in off:
        off_fams[e["family"]] = off_fams.get(e["family"], 0) + 1
    logger.info("域外条目追加: %d 条 %s — PA=16 号文章级自聚合 mean / KW·FOCUS=21_full verified 宇宙"
                "自聚合 / BD=27 号银行×年直读 (六轨 lg 中置) / CTRL=51 号覆盖控制直读",
                len(off), dict(sorted(off_fams.items())))

    # range_gate 落值
    for e in entries:
        e["range_gate"] = range_gate_for(e["basename"], e["family"])
        if e["family"] == "PA":
            e["range_gate"] = "none"
        e["label_elems"] = {"family": e["family"], "base": e["basename"]}

    # 冲突断言: 基名唯一
    all_bases = [e["basename"] for e in entries]
    if len(all_bases) != len(set(all_bases)):
        dup = sorted({b for b in all_bases if all_bases.count(b) > 1})
        raise SystemExit(f"基名冲突 (一列命中多族/重复注册): {dup}")

    # 穷尽性全划分: 40 面板每列 ∈ 纳入源列 ∪ 排除域
    used40: set[str] = set()
    for e in entries:
        if e["source"] == "40":
            used40.update(c for c in e["col_by_track"].values() if c)
    excluded: dict[str, str] = {}
    residual: list[str] = []
    for col in cols40:
        if col in used40:
            continue
        code = classify_excluded(col)
        if code is None:
            residual.append(col)
        else:
            excluded[col] = code
    if residual:
        logger.error("40 面板残差 %d 列无判定 (穷尽性断言失败):", len(residual))
        for c in residual:
            logger.error("    %s", c)
        raise SystemExit(1)

    # 51 号: CTRL 6 列纳入; 与 40 重复列 DUP_OF_40; 其余走排除
    used51 = {c for e in entries if e["source"] == "51" for c in e["col_by_track"].values() if c}
    residual51 = []
    for col in cols51:
        if col in used51:
            continue
        if col in set40:
            excluded[f"51:{col}"] = "DUP_OF_40"
            continue
        code = classify_excluded(col)
        if code is None:
            residual51.append(col)
        else:
            excluded[f"51:{col}"] = code
    if residual51:
        logger.error("51 号残差 %d 列:", len(residual51))
        for c in residual51:
            logger.error("    %s", c)
        raise SystemExit(1)

    # 27 号: BD 24 轨列纳入 + 键
    used27 = {c for e in entries if e["source"] == "27" for c in e["col_by_track"].values() if c}
    for col in cols27:
        if col in used27:
            continue
        if col in {"target_bank", "year"}:
            excluded[f"27:{col}"] = "KEY"
        else:
            code = classify_excluded(col) or "DIAG"
            excluded[f"27:{col}"] = code

    # 16 号: PA 12 轨列纳入; 2 裸别名 ALIAS; 键; 其余 TEXT (文章级)
    used16 = {c for e in entries if e["source"] == "16" for c in e["col_by_track"].values() if c}
    for col in cols16:
        if col in used16:
            continue
        if col in {"policy_cosine_sim", "policy_cosine_sim_allv"}:
            excluded[f"16:{col}"] = "D15_8_ALIAS"
        elif col in {"docid", "target_bank"}:
            excluded[f"16:{col}"] = "KEY"
        else:
            excluded[f"16:{col}"] = "TEXT"

    # 21_full: KW 5 + 聚焦度 2 纳入; 其余 TEXT
    used21 = {c for e in entries if e["source"] == "21" for c in e["col_by_track"].values() if c}
    for col in cols21:
        if col in used21:
            continue
        excluded[f"21:{col}"] = "KEY" if col in {"docid", "target_bank", "日期"} else "TEXT"

    # 排除域理由代码分布 (D15 十一规则 + KEY/TEXT/DUP_OF_40 簿记码全谱)
    code_counts: dict[str, int] = {}
    for v in excluded.values():
        code_counts[v] = code_counts.get(v, 0) + 1
    logger.info("排除域全划分完成: %d 列判排除 (40 面板域 %d + 51/27/16/21 前缀域 %d), 理由代码分布: %s",
                len(excluded), sum(1 for k in excluded if ":" not in k),
                sum(1 for k in excluded if ":" in k), dict(sorted(code_counts.items())))

    # 白名单核查 (WP0-6 ③): 强制纳入清单每项须在纳入域
    for w in INCLUDE_WHITELIST:
        if not any(e["basename"] == w or w in (e["col_by_track"].get(t) or "" for t in TRACKS)
                   for e in entries):
            hit = [e["basename"] for e in entries
                   if any((e["col_by_track"].get(t) or "").startswith(w) for t in TRACKS)]
            if not hit:
                raise SystemExit(f"白名单豁免列 {w} 未入纳入域 (疑被排除正则吞掉)")

    # 短名
    finalize_short_names(entries)
    n_short = sum(1 for e in entries if e["short_name"] != e["basename"])
    logger.info("D16 短名施加: %d/%d 条目触发缩写替换 (替换表 %d 条单遍表序应用; 投影列全 ≤32 字符"
                "且全局唯一断言 ✓)", n_short, len(entries), len(SHORT_NAME_REPLACEMENTS))

    # 排序: 条目顺序 = 输出列序 SSOT (负清单族/入表序 → 域外族按 PA/KW/FOCUS/BD/CTRL 追加)
    # (domain_rows 构造序 = KEEP→CUT 的负清单原序, off 按构造序 — 已是确定序, 不再重排)

    # 名单内容哈希 (v20 防呆) + registry 哈希
    comp_bytes = (CONFIG / "company_listed_names.yaml").read_bytes()
    bank_bytes = (CONFIG / "bank_names.json").read_bytes()
    cut_bytes = CUT_LIST_PATH.read_bytes()
    companies = yaml.safe_load(comp_bytes.decode("utf-8"))["companies"]
    banks = json.loads(bank_bytes.decode("utf-8"))
    bank_company_map = build_bank_company_map(companies, banks)

    dv2_constants = _load_dv2_constants()

    registry = {
        "meta": {
            "plan": "COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-03 v34",
            "n_entries": len(entries),
            "n_emit": sum(1 for e in entries if e["emit_panel"]),
            "n_cut": sum(1 for e in entries if e["cut_code"] == "CUT_V23"),
            "n_cols_40_panel": len(cols40),
            "company_names_sha256": hashlib.sha256(comp_bytes).hexdigest(),
            "bank_names_sha256": hashlib.sha256(bank_bytes).hexdigest(),
            "cut_list_sha256": hashlib.sha256(cut_bytes).hexdigest(),
        },
        "entries": entries,
        "bank_company_map": bank_company_map,
        "excluded": dict(sorted(excluded.items())),
        "dv2_constants": dv2_constants,
    }
    # 哈希锚 = sha256(canonical JSON, 键排序; 剔除易变字段 — meta 不入锚); canonical 式 SSOT = registry_content_sha256
    anchor = registry_content_sha256(registry)
    registry["meta"]["registry_sha256"] = anchor
    logger.info("输入内容指纹 (v20 防呆): company_names=%s… | bank_names=%s… | cut_list=%s…",
                registry["meta"]["company_names_sha256"][:16],
                registry["meta"]["bank_names_sha256"][:16],
                registry["meta"]["cut_list_sha256"][:16])
    logger.info("DV2 常量区段落值: %d 键 (import 自步骤 03 模块常量, 双向锁载体) — %s",
                len(dv2_constants),
                "/".join(sorted(dv2_constants)) if dv2_constants else "空占位 (WP5 未就绪)")

    t_build = time.monotonic() - t0

    t0 = time.monotonic()
    out = Path(args.out)
    logger.info("正在将注册表写入 %s...", out)
    out.write_text(yaml.safe_dump(registry, allow_unicode=True, sort_keys=False, width=200),
                   encoding="utf-8")
    t_write = time.monotonic() - t0

    # 人读审计表 + 统计报告 (格式参照 12_news_fintech.log)
    fam_counts: dict[str, int] = {}
    for e in entries:
        fam_counts[e["family"]] = fam_counts.get(e["family"], 0) + 1
    n_proj = sum(2 * len(e["emit_tracks"]) for e in entries if e["emit_panel"])
    n_excl40 = sum(1 for k in excluded if ":" not in k)
    logger.info("=" * 70)
    logger.info("===      注册表对账统计报告      ===")
    logger.info("=" * 70)
    logger.info("条目总数: %s (emit %s / cut %s)", f"{len(entries):,}",
                f"{registry['meta']['n_emit']:,}", f"{registry['meta']['n_cut']:,}")
    logger.info("40 面板列数: %s | 纳入源列域外排除: %s | 加权投影列: %s",
                f"{len(cols40):,}", f"{n_excl40:,}", f"{n_proj:,}")
    logger.info("分族小计 (%d 族): %s", len(fam_counts), dict(sorted(fam_counts.items())))
    logger.info("registry_sha256: %s", anchor)
    logger.info("-" * 70)
    logger.info("【结果分析】注册表对账产出指标判读 (逐条附经济学/方法学判读; 越接近预期方向越健康):")
    logger.info("  ① 穷尽性: 40 面板 %s 列全划分残差 0 (硬闸已过) → 无静默漏列 (好)", f"{len(cols40):,}")
    logger.info("     判读: 全划分是测度目录完备性的机器证明 — 上游新增列若未经审计, 本闸即 SystemExit(1);")
    logger.info("     它同时堵'新测度悄悄漏出加权域'与'诊断列误入测度域'两类静默偏误; 闸纯 schema 驱动, 与行数无关。")
    logger.info("  ② 负清单对账: cut=%s 恰等 CUT_LIST_v23 物化 410 基名 → emit 判定机械落值零人工 (好)",
                f"{registry['meta']['n_cut']:,}")
    logger.info("     判读: 裁剪是研究者一次性审定的口径决策 (researcher degrees of freedom 封口), 本脚本只机械执行;")
    logger.info("     若 cut≠410 = 负清单被改动或 _dcls→_dm 别名失配 → 须回计划评审, 禁就地调参凑数。")
    logger.info("  ③ D4 对照: bank_company_map=%d 家全称键 (集合相等断言已过) → own-bank 剔除无错位 (好)",
                len(bank_company_map))
    logger.info("     判读: own-bank 剔除防'上市银行报道自身'机械推高共现分子 (42 家 = A股上市银行全集);")
    logger.info("     新银行 IPO/名单 variant 变化会使集合相等断言翻红 — 翻红是样本框更新信号, 非代码 bug。")
    logger.info("  ④ 哈希锚: %s… — 与 tests/test_company_bank_cooc_registry.py::EXPECTED_REGISTRY_SHA256"
                " 比对; 不一致 = 盘上态漂移, 须 bump 锚并级联 02→03 (关注)", anchor[:16])
    logger.info("     判读: 锚只压 entries/bank_company_map/excluded/dv2_constants 四区段 (meta 剔除, 防自指);")
    logger.info("     有意重跑后锚变属预期; 无改动而锚变 = 输入盘上态漂移, 先取证 (比对三输入 sha256) 再重跑。")
    logger.info("  ⑤ 域外条目: %d 条 (PA/KW/FOCUS/BD/CTRL 五族) — 应恒为 25; 增减 = 16/21/27/51 上游 schema"
                " 漂移信号 (关注)", len(off))
    logger.info("  ⑥ 排除域: %s 列全部持理由码 (码集全枚举, 设计上不存在无码残差); 最大簇为 DUP_OF_40"
                " (51↔40 重复列簿记)", f"{len(excluded):,}")
    logger.info("     与 D15_3_MOMENT (std/sum/count/skew 伴生矩); TEXT/KEY 仅标记文章级与键列, 不构成信息损失。")
    logger.info("  ⑦ 生产 T=19 预期: 本步骤仅依赖列名不依赖行数 → dev(T=2) 与生产(T=19) 的 registry 应逐字节一致;")
    logger.info("     例外仅共享树 40 面板重生增删列 → 表现为残差闸/缺列 WARNING 变化, 均为显式信号而非静默漂移。")
    logger.info("-" * 70)
    logger.info("  ⏱ 各子阶段墙钟耗时与吞吐 (4 位有效数字):")
    logger.info("     · ①读五上游列名: %.4g 秒", t_load)
    logger.info("     · ②解析+全划分+构条目: %.4g 秒", t_build)
    logger.info("     · ③写盘 registry yaml: %.4g 秒", t_write)
    n_cols_all = len(cols40) + len(cols51) + len(cols27) + len(cols16) + len(cols21)  # 仅日志用途
    logger.info("     · 吞吐率: ①列名读取 %.4g 列/秒 | ②全划分 %.4g 列/秒 (按五上游 %s 列与既有墙钟推算)",
                n_cols_all / max(t_load, 1e-9), n_cols_all / max(t_build, 1e-9), f"{n_cols_all:,}")
    t_total = time.monotonic() - t_start
    logger.info("     · 子阶段合计: %.4g 秒 (占总阶段 %.4g%%)",
                t_load + t_build + t_write, 100 * (t_load + t_build + t_write) / max(t_total, 1e-9))
    logger.info("     · 峰值内存说明: 当前 RSS %.4g MB (纯列名/字符串处理, 峰值≈现值; 全程未映射 parquet 数据页)",
                _rss_mb())
    logger.info("═" * 50)
    logger.info("阶段摘要: %s", Path(__file__).stem)
    logger.info("─" * 50)
    logger.info("  耗时:     %.4g 秒 (%.4g 分钟)", t_total, t_total / 60)
    logger.info("  输入:     %s 列 (五上游列名合计)", f"{n_cols_all:,}")
    logger.info("  输出:     %s 条注册条目 → %s", f"{len(entries):,}", out.name)
    logger.info("  内存RSS:  %.4g MB", _rss_mb())
    logger.info("═" * 50)
    logger.info("--- 阶段执行完毕: %s ---", Path(__file__).stem)
    return 0


if __name__ == "__main__":
    sys.exit(main())
