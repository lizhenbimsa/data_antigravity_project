"""news_process/run_paper.py — 多论文统一调度入口 (Phase 3e).

把 ``papers/<paper_id>/analysis.main()`` 暴露成统一的 CLI 接口, 配合
``papers/_common/paper_config._VALID_PAPER_IDS`` 做严格白名单检查 (防止
任意路径反射攻击 / 拼写错误)。

CLI 用法
--------
    python news_process/run_paper.py <paper_id> [--stage pipeline|tables|figures|all]
                                                [--dry-run]
    python -m news_process.run_paper <paper_id> [...]

可选 paper_id (与 ``papers/<paper_id>/`` 一一对应):
    bank_fintech_tone       — 主线: 银行金融科技语调 → 银行行为
    bank_fintech_attention  — Bank-FinTech 衍生: firm-level attention (Hassan 2019)
    bank_fintech_substance  — Bank-FinTech 衍生: W&Z 实质/象征
    bank_fintech_locus      — Bank-FinTech 衍生: Gomber 底层/应用
    benefit_society         — 衍生 1: 经营效益态度投影 (Jha-Liu-Manela 2026)
    brokerage_network       — 衍生 2: 信息经纪网络 (Han et al. 2024)
    llm_peer                — 衍生 3: LLM 同业 IV (Cao et al. 2025)
    strategic_diff          — 衍生 4: 战略差异度 (Guzman-Li 2023)

    实际白名单以 ``papers/_common/paper_config._VALID_PAPER_IDS`` 为准
    (``--list`` 列出全部白名单 paper_id 及简介, 不执行其它动作)。

设计约束
--------
- *白名单优先*: 只允许 ``papers._common.paper_config._VALID_PAPER_IDS``
   集合中的论文 ID, 阻止误用反射调用任意子模块。
- *零反射动态加载*: 用普通 ``importlib.import_module`` 而非
   ``importlib.util.spec_from_file_location``, 让导入路径完全可静态分析。
- *退出码契约*: 子论文 ``analysis.main()`` 返回 int 直接转 process exit code。

审计日志 (2026-07-06)
--------------------
本入口是整条论文复现链路的**顶层调度点**, 故承载"审查/检查/审核"所需的全量
证据日志。每次调用都会 (经项目 SSOT ``core.logging.setup_logging`` 建的
``run_paper`` logger) 落盘到 ``<log_dir>/run_paper.log`` 并同步打到 console:

- **会话头**: run_id / 主机 / OS 用户 / PID / Python 版本 & 解释器 / 平台 / cwd /
  ``news_process`` 版本 / 调用方式 (脚本 vs ``-m``) 与 sys.path 注入 / 原始 argv。
- **确定性环境快照**: 复现相关的环境变量 (offline 守卫 / ``PYTHONHASHSEED`` /
  BLAS 线程钉 / HF offline / SSL_CERT_FILE 等) —— **故意排除一切 ``*_API_KEY``
  机密**, 审计日志绝不落密钥。
- **论文组合总览 (``--list``)**: 11 篇论文逐篇档案 —— 状态/spec 版本、理论定位、
  处理→结局、识别策略、目标期刊与样本规模 (以上**实时读自 ``paper_registry``
  SSOT**, 零硬编码漂移) + 每篇 2–4 条**理论锚点参考文献 (APA + DOI)**。
- **单篇调度**: 被调论文的完整档案 (spec live + 参考文献) + 全组合一行索引。
- **会话尾**: 退出码及其语义、总耗时; 异常路径完整 traceback 一并入档。

参考文献溯源 (0 臆造铁律)
------------------------
每条参考文献的 DOI **只取自** ``scripts/audit/LITERATURE_ANCHORS_*.md`` 已核验
锚点池, 并经逐条字面回 grep 确认真实存在 (2026-07-06 一次 22-agent workflow 解析 +
对抗核验, 之后作者本机再逐 DOI ``grep -F`` 复核, 0 缺失)。池中查无者只给
作者-年份-出处-标题 (标注 "[无池确认 DOI]"), **绝不凭记忆臆造 DOI** —— 沿项目
"日志学术化富集" 历轮惯例 (见 CLAUDE.md / MEMORY.md litanchor-* 条)。
"""

from __future__ import annotations

import argparse
import getpass
import importlib
import logging
import os
import platform
import sys
import time
from typing import Any, Final, NamedTuple

# ---------------------------------------------------------------------------
# 作为脚本运行 (``python news_process/run_paper.py ...``) 时, 把 news_process/ 的
# 父目录注入 sys.path 头部, 让包导入可解析。是否注入记录进 ``_INJECTED_SYS_PATH``
# 供会话头审计日志展示 (以 ``-m`` / import 方式运行时 __package__ 非 None, 跳过)。
# ---------------------------------------------------------------------------
_INJECTED_SYS_PATH: str | None = None
if __name__ == "__main__" and __package__ is None:
    _project_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _project_parent not in sys.path:
        sys.path.insert(0, _project_parent)
        _INJECTED_SYS_PATH = _project_parent

from news_process.core.logging import setup_logging, sig4  # noqa: E402
from news_process.core.run_id import generate_run_id  # noqa: E402
from news_process.papers._common.paper_config import (  # noqa: E402
    _VALID_PAPER_IDS,
    is_valid_paper_id,
)
from news_process.papers._common.paper_registry import (  # noqa: E402
    PAPER_IDS_EXISTING,
    PAPER_IDS_NEW,
    PAPER_IDS_PROVISIONAL,
)

_LOGGER = logging.getLogger('run_paper')


# paper_id → 一行简介 (供 --list 展示)
_PAPER_SUMMARIES: Final[dict[str, str]] = {
    'bank_fintech_tone':
        '主线: 媒体银行金融科技语调 → 银行行为 (整条 pipeline 的产品化封装)',
    'bank_fintech_attention':
        'Bank-FinTech 衍生: firm-level fintech 曝光强度 (Hassan et al. 2019 QJE)',
    'bank_fintech_substance':
        'Bank-FinTech 衍生: W&Z 实质/象征二元属性 (W&Z 1994/1998 ASQ)',
    'bank_fintech_locus':
        'Bank-FinTech 衍生: 底层/应用 locus 二元属性 (Gomber 2018 JMIS)',
    'benefit_society':
        '衍生 1: 经营效益态度投影 (Jha, Liu & Manela 2026, RFS §1.3.2)',
    'brokerage_network':
        '衍生 2: 信息经纪网络与企业表现 (Han, Kim & Nanda 2024)',
    'llm_peer':
        '衍生 3: LLM 生成同业竞争 IV (Cao, Chen, Tucker & Wan 2025, RAS)',
    'strategic_diff':
        '衍生 4: 银行金融科技战略差异度 (Guzman-Li 2023; Hoberg-Phillips 2016)',
    # Provisional (2026-06-01 wiring): 可调度但 tables/figures 为 Phase-3 契约占位骨架,
    # 完整 B-route 交付物 (manuscript/refs.bib/Stata 全集) 待 P5 / M5 / M7 onboarding。
    'bank_fintech_collab':
        '衍生/P5 (provisional): 自主研发 vs 外部协同 (Chesbrough 2003; 表/图占位待 M5/M6)',
    'bank_media_disagreement':
        '第10篇 (provisional): 跨媒体语调分歧 → 风险承担 (Cookson-Niessner 2020 JF; 待 M5)',
    'bank_news_clarity':
        '第11篇 (provisional): 新闻清晰度 → 外部信息环境质量 (Bushman-Williams 2012 JAE; 待 M7)',
}


# 退出码 → 语义 (会话尾审计行). analysis.main() 亦可返回任意 int, 未登记者归"未分类"。
_EXIT_CODE_MEANINGS: Final[dict[int, str]] = {
    0: '成功',
    1: '导入失败 / 缺少 main() 入口 / 论文 analysis.main() 返回 1',
    2: '未知 paper_id (白名单校验失败)',
}

# 审计快照只记录**复现/行为相关**的环境变量; 严禁纳入任何机密。
# ⚠ 绝不加入 YUNWU_API_KEY / DEEPSEEK_API_KEY / SILICONFLOW_API_KEY / EMBEDDING_API_KEY
#   等 ``*_API_KEY`` (审计日志会落盘, 密钥入档即泄露)。此处为显式 allow-list, 非 deny-list。
_AUDIT_ENV_KEYS: Final[tuple[str, ...]] = (
    'NEWS_PROCESS_RUN_ID',       # 本次运行关联 ID (与下游 stage 日志对齐)
    'NEWS_PROCESS_LLM_OFFLINE',  # 离线守卫: 命中缓存则 $0 复现, miss 即 raise
    'PYTHONHASHSEED',            # golden 重生确定性前置 (须 =0)
    'MKL_NUM_THREADS',           # BLAS 线程钉死 (=1) — 消除 FP 非确定
    'OPENBLAS_NUM_THREADS',
    'NUMEXPR_NUM_THREADS',
    'OMP_NUM_THREADS',
    'HF_HUB_OFFLINE',            # stage 23 BERT 离线重跑
    'TRANSFORMERS_OFFLINE',
    'NO_COLOR',                  # console 着色开关 (审计口径)
    'SSL_CERT_FILE',             # 裸环境嵌入 SSL 修复 (certifi)
)


# ---------------------------------------------------------------------------
# 论文理论定位 + 理论锚点参考文献 (供组合总览 / 单篇档案的学术化富集)
#
# ▶ 结构字段 (处理/结局/识别/目标/样本) **不在此硬编码** —— 运行时实时读自
#   ``paper_registry.get_spec(pid)`` (SSOT, 零漂移); 此处只放两类无法机读的元数据:
#   ① 一句话理论定位 tagline; ② 理论锚点参考文献。
# ▶ 参考文献 DOI **全部取自** ``scripts/audit/LITERATURE_ANCHORS_*.md`` 已核验池并
#   逐条字面复核存在 (0 臆造); 池中查无者 doi=None (仍给作者-年份-出处-标题)。
#   provenance 详见模块 docstring "参考文献溯源" 段。
# ---------------------------------------------------------------------------


class _Ref(NamedTuple):
    """一条理论锚点参考文献。doi=None 表示池中无 DOI (专著/未收录), 非臆造缺口。"""
    cite: str    # 作者 (年份), 如 "Hassan, Hollander, van Lent & Tahoun (2019)"
    venue: str   # 期刊/出版物
    title: str
    doi: str | None  # 仅当在锚点池字面确认存在时非 None


_PAPER_THEORY: Final[dict[str, str]] = {
    'bank_fintech_tone':
        "用 text-as-data 情感分析度量媒体对银行金融科技报道的语调方向, "
        "经储户/市场纪律渠道传导至银行资金成本等行为与绩效。",
    'bank_fintech_attention':
        "以新闻媒体曝光强度 (Fang-Peress extensive 覆盖构念的 intensity 加权扩展) "
        "度量银行对 fintech 的关注度, 沿 Hassan (2019) '测度→企业响应' 范式识别对银行 "
        "fintech 投入的因果影响。",
    'bank_fintech_substance':
        "以 Westphal-Zajac 实质/象征 (substantive/symbolic) 脱耦框架度量银行金融科技宣告"
        "属性, 检验实质性宣告对成本收入比前向改善的因果效应。",
    'bank_fintech_locus':
        "以 Gomber (2018) fintech 框架把银行金科话语切成 '底层技术 vs 应用场景' 二元 locus, "
        "用同业 LOO IV 检验对引用加权专利等技术创新产出的差异化因果效应。",
    'benefit_society':
        "用 LLM-Embedding 双极锚点投影 (a_j=cos(s_j, pos-neg)) 测度银行金融科技报道的 "
        "'经营效益态度', 检验其对银行绩效 (ROA) 的影响; 承 Jha-Liu-Manela 语言嵌入范式。",
    'brokerage_network':
        "信息经纪网络位置 (介数/结构洞) 驱动同业语调溢出对银行绩效的因果传染, "
        "二阶网络 W^2·tone 作工具变量破解 Manski 反射问题。",
    'llm_peer':
        "用 LLM 语义同业 (非 SIC 行业码) 构造 leave-one-out 语调 IV, 绕开 Manski 反射问题, "
        "识别同业语调溢出对银行真实经营结局的因果效应。",
    'strategic_diff':
        "用多文本表征 (TF-IDF/LDA-JSD/Embedding) 测银行金融科技战略差异度 (N-邻文本距离), "
        "检验差异化→产品市场势力→特许权价值 (tobin_q), Bartik IV 识别。",
    'bank_fintech_collab':
        "以 Chesbrough 开放式创新框架, 把银行金科公告编码为 '自主研发 vs 外部协同' 二元"
        "属性, 检验外部协同主导是否驱动更多 fintech 并购。",
    'bank_media_disagreement':
        "承 Cookson-Niessner 投资者分歧测度谱系, 度量跨媒体语调分歧 (cross-outlet variance) "
        "→ 银行风险承担 (Z-score/NPL/RWA) 的双向因果, 以 outlet house-style 暴露作 IV。",
    'bank_news_clarity':
        "用 You (2018) 清晰度词典把媒体报道的外部信息环境质量量化为 treatment, 检验其对银行"
        "风险承担 (Z-score) 的因果效应, 方向由分样本揭示; 直接锚 Bushman-Williams (2012) JAE。",
}

_PAPER_LIT_ANCHORS: Final[dict[str, tuple[_Ref, ...]]] = {
    'bank_fintech_tone': (
        _Ref("Tetlock (2007)", "The Journal of Finance",
             "Giving content to investor sentiment: The role of media in the stock market",
             "10.1111/j.1540-6261.2007.01232.x"),
        _Ref("Loughran & McDonald (2011)", "The Journal of Finance",
             "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks",
             "10.1111/j.1540-6261.2010.01625.x"),
        _Ref("Martinez Peria & Schmukler (2001)", "The Journal of Finance",
             "Do depositors punish banks for bad behavior? Market discipline, "
             "deposit insurance, and banking crises", None),
        _Ref("Iyer & Puri (2012)", "American Economic Review",
             "Understanding bank runs: The importance of depositor-bank "
             "relationships and networks", None),
    ),
    'bank_fintech_attention': (
        _Ref("Fang & Peress (2009)", "The Journal of Finance",
             "Media coverage and the cross-section of stock returns",
             "10.1111/j.1540-6261.2009.01493.x"),
        _Ref("Hassan, Hollander, van Lent & Tahoun (2019)",
             "The Quarterly Journal of Economics",
             "Firm-level political risk: Measurement and effects",
             "10.1093/qje/qjz021"),
        _Ref("Manski (1993)", "The Review of Economic Studies",
             "Identification of endogenous social effects: The reflection problem",
             "10.2307/2298123"),
        _Ref("Goldsmith-Pinkham, Sorkin & Swift (2020)", "American Economic Review",
             "Bartik instruments: What, when, why, and how",
             "10.1257/aer.20181047"),
    ),
    'bank_fintech_substance': (
        _Ref("Westphal & Zajac (1994)", "Administrative Science Quarterly",
             "Substance and symbolism in CEOs' long-term incentive plans",
             "10.2307/2393295"),
        _Ref("Westphal & Zajac (1998)", "Administrative Science Quarterly",
             "The symbolic management of stockholders: Corporate governance "
             "reforms and shareholder reactions", "10.2307/2393593"),
        _Ref("Leary & Roberts (2014)", "The Journal of Finance",
             "Do peer firms affect corporate financial policy?",
             "10.1111/jofi.12094"),
        _Ref("Goldsmith-Pinkham, Sorkin & Swift (2020)", "American Economic Review",
             "Bartik instruments: What, when, why, and how",
             "10.1257/aer.20181047"),
    ),
    'bank_fintech_locus': (
        _Ref("Gomber, Kauffman, Parker & Weber (2018)",
             "Journal of Management Information Systems",
             "On the fintech revolution: Interpreting the forces of innovation, "
             "disruption, and transformation in financial services",
             "10.1080/07421222.2018.1440766"),
        _Ref("Leary & Roberts (2014)", "The Journal of Finance",
             "Do peer firms affect corporate financial policy?",
             "10.1111/jofi.12094"),
        _Ref("Kogan, Papanikolaou, Seru & Stoffman (2017)",
             "The Quarterly Journal of Economics",
             "Technological innovation, resource allocation, and growth", None),
        _Ref("Goldstein, Jiang & Karolyi (2019)", "The Review of Financial Studies",
             "To FinTech and beyond", None),
    ),
    'benefit_society': (
        _Ref("Jha, Liu & Manela (2026)", "The Review of Financial Studies",
             "Does finance benefit society? A language embedding approach",
             "10.1093/rfs/hhaf012"),
        _Ref("Leary & Roberts (2014)", "The Journal of Finance",
             "Do peer firms affect corporate financial policy?",
             "10.1111/jofi.12094"),
        _Ref("Westphal & Zajac (2001)", "Administrative Science Quarterly",
             "Decoupling policy from practice: The case of stock repurchase programs",
             None),
    ),
    'brokerage_network': (
        _Ref("Han, Kim & Nanda (2024)", "The Review of Financial Studies",
             "Institutional brokerage networks: Facilitating liquidity provision",
             "10.1093/rfs/hhae026"),
        _Ref("Bramoullé, Djebbari & Fortin (2009)", "Journal of Econometrics",
             "Identification of peer effects through social networks",
             "10.1016/j.jeconom.2008.12.021"),
        _Ref("Manski (1993)", "The Review of Economic Studies",
             "Identification of endogenous social effects: The reflection problem",
             "10.2307/2298123"),
        _Ref("Burt (1992)", "Harvard University Press (专著)",
             "Structural holes: The social structure of competition", None),
    ),
    'llm_peer': (
        _Ref("Cao, Chen, Tucker & Wan (2025)", "Review of Accounting Studies",
             "Large language model-identified peer firms", None),
        _Ref("Manski (1993)", "The Review of Economic Studies",
             "Identification of endogenous social effects: The reflection problem",
             "10.2307/2298123"),
        _Ref("Leary & Roberts (2014)", "The Journal of Finance",
             "Do peer firms affect corporate financial policy?",
             "10.1111/jofi.12094"),
    ),
    'strategic_diff': (
        _Ref("Guzman & Li (2023)", "Management Science",
             "Measuring founding strategy", "10.1287/mnsc.2022.4369"),
        _Ref("Hoberg & Phillips (2016)", "Journal of Political Economy",
             "Text-based network industries and endogenous product differentiation",
             "10.1086/688176"),
        _Ref("Hoberg, Phillips & Prabhala (2014)", "The Journal of Finance",
             "Product market threats, payouts, and financial flexibility",
             "10.1111/jofi.12050"),
        _Ref("Keeley (1990)", "American Economic Review",
             "Deposit insurance, risk, and market power in banking", None),
    ),
    'bank_fintech_collab': (
        _Ref("Chesbrough (2003)", "Harvard Business School Press (专著)",
             "Open innovation: The new imperative for creating and profiting "
             "from technology", None),
        _Ref("Laursen & Salter (2006)", "Strategic Management Journal",
             "Open for innovation: The role of openness in explaining innovation "
             "performance among U.K. manufacturing firms", "10.1002/smj.507"),
        _Ref("Hagedoorn (2002)", "Research Policy",
             "Inter-firm R&D partnerships: An overview of major trends and "
             "patterns since 1960", "10.1016/S0048-7333(01)00120-2"),
        _Ref("Cohen & Levinthal (1990)", "Administrative Science Quarterly",
             "Absorptive capacity: A new perspective on learning and innovation",
             None),
    ),
    'bank_media_disagreement': (
        _Ref("Cookson & Niessner (2020)", "The Journal of Finance",
             "Why don't we agree? Evidence from a social network of investors",
             "10.1111/jofi.12852"),
        _Ref("Antweiler & Frank (2004)", "The Journal of Finance",
             "Is all that talk just noise? The information content of internet "
             "stock message boards", "10.1111/j.1540-6261.2004.00662.x"),
        _Ref("Diether, Malloy & Scherbina (2002)", "The Journal of Finance",
             "Differences of opinion and the cross section of stock returns", None),
        _Ref("Bushman & Williams (2012)", "Journal of Accounting and Economics",
             "Accounting discretion, loan loss provisioning, and discipline of "
             "banks' risk-taking", None),
    ),
    'bank_news_clarity': (
        _Ref("You, Zhang & Zhang (2018)", "The Review of Financial Studies",
             "Who captures the power of the pen?", "10.1093/rfs/hhx055"),
        _Ref("Loughran & McDonald (2014)", "The Journal of Finance",
             "Measuring readability in financial disclosures",
             "10.1111/jofi.12162"),
        _Ref("Bushman & Williams (2012)", "Journal of Accounting and Economics",
             "Accounting discretion, loan loss provisioning, and discipline of "
             "banks' risk-taking", None),
        _Ref("Bushee, Core, Guay & Hamm (2010)", "Journal of Accounting Research",
             "The role of the business press as an information intermediary", None),
    ),
}


# ---------------------------------------------------------------------------
# 审计辅助 (纯日志/取证, 不参与任何产物计算 → golden-safe)
# ---------------------------------------------------------------------------


def _safe_getuser() -> str:
    """尽力拿到 OS 登录用户名 (取证用), 任何失败都优雅降级, 绝不抛异常。"""
    try:
        return getpass.getuser()
    except Exception:  # 无 pwd / 环境残缺等
        return os.environ.get('USERNAME') or os.environ.get('USER') or '<unknown>'


def _get_package_version() -> str:
    """读取 ``news_process.__version__`` (代码版本溯源), 失败降级为 <unknown>。"""
    try:
        import news_process
        return getattr(news_process, '__version__', '<unknown>')
    except Exception:
        return '<unknown>'


def _resolve_log_dir() -> str:
    """解析审计日志目录。

    优先项目 config 的 ``paths.log_dir`` (与 ``run_pipeline_function`` 同源);
    config 加载失败时回退到 ``<news_process>/logs``, 保证 ``--list`` / ``-h`` 等
    无需 config 的路径也一定能落审计日志 (审计覆盖优先于严格一致)。
    """
    try:
        from news_process.core.config import load_config
        log_dir = load_config().get('paths', {}).get('log_dir')
        if log_dir:
            return log_dir
    except Exception:
        pass
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')


def _configure_audit_logger() -> logging.Logger:
    """建立 ``run_paper`` 审计 logger (文件 + console 双通道)。

    复用项目 SSOT ``core.logging.setup_logging`` (PID 戳 / rotating / 无色落盘);
    ``file_mode='a'`` 追加累积历次调度记录 (RotatingFileHandler 按 50MB 有界滚动) ——
    审计要历史轨迹, 与 stage 默认的 ``'w'``(只留最新) 刻意相反。文件 handler 无法
    创建时 (如 log_dir 只读) 降级为 console-only, 确保 CLI 永不因日志基建而挂。
    """
    log_dir = _resolve_log_dir()
    try:
        return setup_logging('run_paper', log_dir, file_mode='a')
    except Exception:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - PID:%(process)d - %(levelname)s - %(message)s',
        )
        lg = logging.getLogger('run_paper')
        lg.warning("无法创建审计文件日志 (log_dir=%s); 已降级为 console-only。",
                   log_dir, exc_info=True)
        return lg


def _log_runtime_context(logger: logging.Logger, run_id: str,
                         argv: list[str] | None) -> None:
    """会话头: 记录调用者身份、运行环境与原始命令行 (取证锚点)。"""
    logger.info("═" * 68)
    logger.info("run_paper 调度会话开始 | run_id=%s", run_id)
    logger.info("─" * 68)
    logger.info("主机 host:        %s", platform.node())
    logger.info("OS 用户 user:     %s", _safe_getuser())
    logger.info("进程 PID:         %d", os.getpid())
    logger.info("Python:           %s", sys.version.replace('\n', ' '))
    logger.info("解释器 executable: %s", sys.executable)
    logger.info("平台 platform:    %s", platform.platform())
    logger.info("工作目录 cwd:     %s", os.getcwd())
    logger.info("news_process 版本: %s", _get_package_version())
    logger.info("调用方式:         %s",
                "脚本 (python run_paper.py)" if _INJECTED_SYS_PATH
                else "模块 (-m news_process.run_paper / import)")
    if _INJECTED_SYS_PATH:
        logger.info("  ↳ 已注入 sys.path[0]: %s", _INJECTED_SYS_PATH)
    logger.info("原始命令行 sys.argv: %s", sys.argv)
    logger.info("有效 argv (传入 main): %s",
                "None → 使用 sys.argv[1:]" if argv is None else argv)
    logger.info("run_id 已导出 NEWS_PROCESS_RUN_ID → 下游各 stage 子进程继承, 便于跨日志对齐。")


def _log_env_snapshot(logger: logging.Logger) -> None:
    """确定性/行为相关环境变量快照 (显式 allow-list, 严禁纳入任何 *_API_KEY 机密)。"""
    logger.info("─" * 68)
    logger.info("确定性/行为环境快照 (故意排除全部 *_API_KEY 机密):")
    for key in _AUDIT_ENV_KEYS:
        val = os.environ.get(key)
        logger.info("  %-22s = %s", key, val if val is not None else "<未设置>")


def _log_parsed_args(logger: logging.Logger, args: argparse.Namespace,
                     unknown: list[str]) -> None:
    """记录 argparse 解析结果与将透传给子论文的未知参数。"""
    logger.info("─" * 68)
    logger.info("解析后的参数:")
    logger.info("  paper_id  = %r", args.paper_id)
    logger.info("  --list    = %s", args.list_papers)
    logger.info("  --stage   = %s", args.stage)
    logger.info("  --dry-run = %s", args.dry_run)
    logger.info("  透传/未知 argv (原样转发给 analysis.main()) = %s", unknown)


# ---------------------------------------------------------------------------
# 论文组合总览 / 单篇档案 (结构字段 live 读 SSOT + 学术锚点参考文献)
# ---------------------------------------------------------------------------


def _portfolio_tier(pid: str) -> str:
    """论文组合层级 (与 spec.status 互补: provisional 在 spec 里 status 仍为 new)。"""
    if pid in PAPER_IDS_PROVISIONAL:
        return 'provisional (可调度; 表/图为占位骨架)'
    if pid in PAPER_IDS_NEW:
        return 'new (B-route 全交付)'
    if pid in PAPER_IDS_EXISTING:
        return 'existing (已建)'
    return 'unknown-tier'


def _load_spec_safe(pid: str) -> Any | None:
    """加载单篇 PaperSpec (paper_registry SSOT); 任何失败降级为 None (不致命)。"""
    try:
        from news_process.papers._common.paper_registry import get_spec
        return get_spec(pid)
    except Exception:
        return None


def _spec_snapshot(spec: Any | None) -> dict[str, Any]:
    """从 PaperSpec 提取供审计展示的结构字段 (全部实时读自 spec, 零硬编码漂移)。"""
    if spec is None:
        return {}
    raw = getattr(spec, 'raw', {}) or {}

    def _dig(d: Any, *keys: str) -> Any:
        cur = d
        for k in keys:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(k)
        return cur

    tx = _dig(raw, 'treatment', 'primary')
    if tx is None:
        # locus 等以 treatment pair (2D) 表达, 无单一 primary 标量。
        t = raw.get('treatment')
        if isinstance(t, dict):
            for k in ('treatment_pair', 'pair', 'primary_layer', 'layer'):
                if t.get(k):
                    tx = t.get(k)
                    break
        if tx is None:
            tx = '(2D treatment pair — 见 spec)'
    diff = (getattr(spec, 'differentiation_claim', '') or '').strip()
    diff_line = diff.splitlines()[0].strip() if diff else ''
    if len(diff_line) > 96:
        diff_line = diff_line[:96] + '…'
    return {
        'status': getattr(spec, 'status', '?'),
        'spec_version': getattr(spec, 'spec_version', '?'),
        'treatment': tx,
        'outcome': _dig(raw, 'outcome', 'primary'),
        'outcome_secondary': _dig(raw, 'outcome', 'secondary'),
        'baseline': _dig(raw, 'identification', 'baseline'),
        'iv': _dig(raw, 'identification', 'iv', 'primary'),
        'primary_outlet': getattr(spec, 'primary_outlet', '')
        or _dig(raw, 'targets', 'primary_outlet'),
        'ambitious_outlet': _dig(raw, 'targets', 'ambitious_outlet'),
        't_year': _dig(raw, 'sample', 't_year'),
        'n_bank_min': _dig(raw, 'sample', 'n_bank_min'),
        'obs_target_min': _dig(raw, 'sample', 'obs_target_min'),
        'diff_claim': diff_line,
    }


def _format_ref(ref: _Ref) -> str:
    """把一条锚点渲染为 APA 风格审计行 (DOI 仅在池确认时给, 否则显式标注无 DOI)。"""
    base = f"{ref.cite}. {ref.title}. {ref.venue}."
    if ref.doi:
        return f"{base} https://doi.org/{ref.doi}"
    return f"{base} [无池确认 DOI]"


def _log_paper_block(logger: logging.Logger, pid: str,
                     index: int | None = None, *, with_refs: bool = True) -> None:
    """记录单篇论文档案: 结构字段 (live spec) + 理论定位 + 参考文献。"""
    snap = _spec_snapshot(_load_spec_safe(pid))
    head = f"【{index:02d}/{len(_VALID_PAPER_IDS)}】" if index is not None else "▶ "
    logger.info("%s%-24s  [%s · spec %s · %s]",
                head, pid, snap.get('status', '?'),
                snap.get('spec_version', '?'), _portfolio_tier(pid))
    logger.info("     理论定位: %s", _PAPER_THEORY.get(pid, '(无)'))
    logger.info("     一行简介: %s", _PAPER_SUMMARIES.get(pid, '(no summary)'))
    if snap:
        sec = snap.get('outcome_secondary')
        sec_txt = f" (+次要 {sec})" if sec else ""
        logger.info("     处理 → 结局: %s  →  %s%s",
                    snap.get('treatment'), snap.get('outcome'), sec_txt)
        logger.info("     识别策略: baseline=%s | IV=%s",
                    snap.get('baseline'), snap.get('iv'))
        logger.info("     目标: 首选期刊=%s | 进取=%s | 样本 T=%s · N≥%s · obs≥%s",
                    snap.get('primary_outlet'), snap.get('ambitious_outlet'),
                    snap.get('t_year'), snap.get('n_bank_min'),
                    snap.get('obs_target_min'))
        if snap.get('diff_claim'):
            logger.info("     差异化主张: %s", snap['diff_claim'])
    else:
        logger.info("     ⚠ 无法读取 paper_spec.yaml (spec 缺失/解析失败); 仅展示静态元数据。")
    if with_refs:
        refs = _PAPER_LIT_ANCHORS.get(pid, ())
        n_doi = sum(1 for r in refs if r.doi)
        logger.info("     理论锚点参考文献 (%d 条; %d 条附池确认 DOI):", len(refs), n_doi)
        for r in refs:
            logger.info("       · %s", _format_ref(r))


def _log_paper_catalog(logger: logging.Logger) -> None:
    """论文组合总览: 11 篇逐篇完整档案 (--list / 无参数时的全局态势)。"""
    ids = sorted(_VALID_PAPER_IDS)
    logger.info("═" * 68)
    logger.info("论文组合总览 (共 %d 篇 | existing %d + new %d + provisional %d)",
                len(ids), len(PAPER_IDS_EXISTING), len(PAPER_IDS_NEW),
                len(PAPER_IDS_PROVISIONAL))
    logger.info("结构字段实时读自 paper_registry (SSOT, 零硬编码漂移); "
                "参考文献 DOI 取自已核验 LITERATURE_ANCHORS 池 (0 臆造, 见模块 docstring)。")
    for i, pid in enumerate(ids, 1):
        logger.info("─" * 68)
        try:
            _log_paper_block(logger, pid, index=i, with_refs=True)
        except Exception:
            logger.warning("论文 %s 档案渲染失败 (非致命, 跳过):", pid, exc_info=True)
    logger.info("═" * 68)


def _log_portfolio_index(logger: logging.Logger, current_pid: str) -> None:
    """一行式组合索引, ★ 标出本次调度所在的论文 (单篇调度时的态势感知)。"""
    logger.info("─" * 68)
    logger.info("组合定位索引 (★ = 本次调度 %s):", current_pid)
    for pid in sorted(_VALID_PAPER_IDS):
        mark = "★" if pid == current_pid else "·"
        logger.info("   %s %-24s %s", mark, pid,
                    _PAPER_SUMMARIES.get(pid, '(no summary)'))


def _log_paper_config(logger: logging.Logger, paper_id: str) -> None:
    """记录该论文的本地化落盘路径 (PaperConfig) —— 产物位置可追溯。非致命。"""
    try:
        from news_process.papers._common.paper_config import get_paper_config
        pc = get_paper_config(paper_id)
        logger.info("论文本地化配置 (PaperConfig, 产物落盘位置):")
        logger.info("  project_root = %s", pc.project_root)
        logger.info("  panel_dir    = %s", pc.panel_dir)
        logger.info("  output_dir   = %s", pc.output_dir)
        logger.info("  do_dir       = %s", pc.do_dir)
        logger.info("  drafts_dir   = %s", pc.drafts_dir)
    except Exception:
        logger.warning("解析 %s 的 PaperConfig 失败 (非致命, 继续调度):",
                       paper_id, exc_info=True)


def _log_session_end(logger: logging.Logger, run_id: str,
                     outcome: dict[str, Any], session_start: float) -> None:
    """会话尾: 记录退出码语义 + 总耗时 (异常路径标注为未捕获异常)。"""
    elapsed = time.time() - session_start
    logger.info("─" * 68)
    if outcome.get('exc'):
        logger.info("会话结束 | run_id=%s | 结果: 未捕获异常 (见上方 traceback) | 总耗时: %ss",
                    run_id, sig4(elapsed))
    else:
        code = outcome.get('code')
        meaning = _EXIT_CODE_MEANINGS.get(code, '论文 analysis.main() 返回值 / 未分类')
        logger.info("会话结束 | run_id=%s | 退出码: %s (%s) | 总耗时: %ss",
                    run_id, code, meaning, sig4(elapsed))
    logger.info("═" * 68)


def _print_paper_list() -> None:
    """打印所有可调度论文 (面向人类的干净 stdout, 无时间戳)。"""
    print("可调度论文列表:\n")
    for pid in sorted(_VALID_PAPER_IDS):
        summary = _PAPER_SUMMARIES.get(pid, '(no summary)')
        print(f"  {pid:24s}  {summary}")
    print()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='python -m news_process.run_paper',
        description='多论文统一调度器 — 调用指定论文子包的 analysis CLI。',
    )
    parser.add_argument(
        'paper_id', nargs='?',
        help='论文标识 (与 papers/<paper_id>/ 一一对应)。',
    )
    parser.add_argument(
        '--list', action='store_true', dest='list_papers',
        help='列出全部白名单 paper_id (含组合总览 + 参考文献), 不执行其它动作。',
    )
    parser.add_argument(
        '--stage', choices=['pipeline', 'tables', 'figures', 'all'],
        default='all',
        help='转发给论文 analysis.main() 的 --stage 参数 (默认 all)。',
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='转发给论文 analysis.main() 的 --dry-run。',
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    session_start = time.time()

    # run_id 先行生成并导出 (下游 stage 子进程经 NEWS_PROCESS_RUN_ID 继承同一 ID),
    # 再建审计 logger —— 使会话头/尾都带 run_id, 且整条链路日志可交叉对齐。
    run_id = generate_run_id()
    logger = _configure_audit_logger()

    _log_runtime_context(logger, run_id, argv)
    _log_env_snapshot(logger)

    outcome: dict[str, Any] = {'code': None, 'exc': False}
    try:
        parser = _build_parser()
        # parse_known_args: 未知参数透传给子论文; -h / 参数错误会 raise SystemExit,
        # 被下方 except 捕获入档后原样透传 (连 --help 请求也留审计痕迹)。
        args, unknown = parser.parse_known_args(argv)
        _log_parsed_args(logger, args, unknown)

        # --list 或无 paper_id: 输出全组合总览 (逐篇档案 + 参考文献), 不调度。
        if args.list_papers or args.paper_id is None:
            reason = "--list" if args.list_papers else "无 paper_id 位置参数"
            logger.info("动作: 论文组合总览 (触发原因: %s), 不执行调度。", reason)
            _log_paper_catalog(logger)
            _print_paper_list()  # 面向人类的干净 stdout 快速索引
            outcome['code'] = 0
            return 0

        # 白名单校验 (设计约束: 白名单优先, 阻止反射调用任意子模块)。
        whitelist = sorted(_VALID_PAPER_IDS)
        logger.info("─" * 68)
        logger.info("白名单 (SSOT=papers._common.paper_registry.PAPER_IDS_ALL, 共 %d 项): %s",
                    len(whitelist), whitelist)
        if not is_valid_paper_id(args.paper_id):
            logger.error("paper_id=%r 不在白名单 → 拒绝调度 (退出码 2)。", args.paper_id)
            print(
                f"ERROR: 未知 paper_id={args.paper_id!r}. "
                f"白名单: {whitelist}\n请用 --list 查看可选值。",
                file=sys.stderr,
            )
            outcome['code'] = 2
            return 2
        logger.info("paper_id=%r 通过白名单校验。", args.paper_id)

        # 被调论文的完整档案 (结构字段 live + 理论定位 + 参考文献) + 组合定位索引。
        logger.info("═" * 68)
        logger.info("本次调度论文档案:")
        _log_paper_block(logger, args.paper_id, index=None, with_refs=True)
        _log_portfolio_index(logger, args.paper_id)

        # 记录该论文的落盘路径 (产物可追溯; 非致命)。
        logger.info("─" * 68)
        _log_paper_config(logger, args.paper_id)

        # 零反射动态加载: importlib.import_module, 导入路径完全可静态分析。
        module_path = f"news_process.papers.{args.paper_id}.analysis"
        logger.info("─" * 68)
        logger.info("解析目标模块 (零反射 importlib.import_module): %s", module_path)
        import_start = time.time()
        try:
            analysis_mod = importlib.import_module(module_path)
        except ImportError:
            logger.error("导入失败 %s → 退出码 1 (完整 traceback 如下):",
                         module_path, exc_info=True)
            outcome['code'] = 1
            return 1
        logger.info("模块导入成功 | 耗时: %ss | 源文件: %s",
                    sig4(time.time() - import_start),
                    getattr(analysis_mod, '__file__', '<unknown>'))

        if not hasattr(analysis_mod, 'main'):
            logger.error("%s 缺少 main() 入口; 不符合 Phase 3 契约 → 退出码 1。",
                         module_path)
            outcome['code'] = 1
            return 1

        # 组装转发参数 (退出码契约: 子论文返回 int 直接转 process exit code)。
        forwarded: list[str] = ['--stage', args.stage]
        if args.dry_run:
            forwarded.append('--dry-run')
        forwarded.extend(unknown)

        logger.info("═" * 68)
        logger.info("转发给 %s.main() 的参数: %s", module_path, forwarded)
        logger.info("开始调用 analysis.main() ...")
        call_start = time.time()
        rc = int(analysis_mod.main(forwarded) or 0)
        logger.info("analysis.main() 正常返回 | 返回码=%d | 调用耗时: %ss",
                    rc, sig4(time.time() - call_start))
        outcome['code'] = rc
        return rc

    except SystemExit as se:
        # argparse (-h / 参数错误) 或子论文内部 sys.exit —— 入档后原样透传退出码。
        outcome['code'] = se.code if isinstance(se.code, int) else (
            0 if se.code is None else 1)
        logger.info("捕获 SystemExit(code=%r) — 见上方 usage/help 或 traceback, 原样透传。",
                    se.code)
        raise
    except BaseException:
        # 未预期异常 (含 KeyboardInterrupt): 完整 traceback 入档后原样抛出, 便于取证。
        outcome['exc'] = True
        logger.error("run_paper 调度过程未捕获异常 (完整 traceback 如下):", exc_info=True)
        raise
    finally:
        _log_session_end(logger, run_id, outcome, session_start)


if __name__ == '__main__':
    sys.exit(main())
