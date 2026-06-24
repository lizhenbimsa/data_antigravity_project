"""news_process.pipeline.filtering.cooccurrence_filter — stage 12b 银行×金科邻近共现预过滤.

在 stage 12 (news_fintech) 与 stage 13 (materialize_ctx) 之间插入一道【硬过滤】:
**只保留 "目标银行与 ≥1 金融科技词在 ±sentence_radius 句窗口内邻近共现" 的文章行,
丢弃其余** —— 压降 stage 12 "出现金科词即判金科" 造成的虚假相关 (False Positives)。

学术依据:
    Andreou et al. (2026). Research Policy. core-contextual word-pairing within a
    span —— 邻近配对作为主题相关性归因过滤。本实现是其【句级窗口】操作化
    (银行锚句 ±sentence_radius 句; 比 10-lexical-token span 更宽, 详见 manuscript 披露)。
    Hassan, T. A., et al. (2019). QJE 134(4), 2135-2202. §III.B proximity-based attribution。

工作流:
    stage 12 (news_fintech)  → 12_fintech_news.parquet      (is_fintech_news==True 关键词金科)
    stage 12b (本模块)       → 13_cooccurrence_filtered.parquet (= 12 的近邻相关子集, 丢行)
    stage 13 (materialize_ctx) → 读 12b 输出 (ctx_materializer.py main 的 in_name=output_12b_cooccurrence 重指针)

口径 (与 stage 13 _ss 轨【不同】, 见 entity_context.has_bank_fintech_cooccurrence_within_radius):
    - 保留判据 = 窗口邻近 (银行锚句 i ∧ 金科∈[i±radius] 邻句); 严格同句 (_ss) 是其子集。
    - 不对称匹配: 银行侧否定/短名排除 (has_unexcluded_occurrence); 金科侧裸 AC (1506 词)。

路线 A (纯接受-披露, 四轮审计定稿): 12b 仅丢行, 下游 controls.py/encode.py 零改动;
    n_articles/fintech_share/attention 族①(firm-level, 经 14→verified 门控)/NF 对照组的
    统计宇宙统一平移为 "近邻相关金科" 口径 (⚠ 地理 attention 族 ft_attn_*/ft_vol_* 直读
    12_fintech_news_full、不经 12b → 仍原始关键词口径, pre-existing 未门控, 与 12b 正交),
    在 manuscript/codebook 披露 (fintech_share 分母经 "望远镜式坍缩" 恒不变, 不受 12b 影响)。

安全 (铁律):
    - FINTECH_AC=None (词典加载失败) → **保留全部行 + loud WARNING** (绝不静默清空整库)。
    - keep 率低于 cooccurrence_filter.min_keep_frac (或 0 行) → SystemExit(1) + loud。

规范调用:
    python -m news_process.pipeline.filtering.cooccurrence_filter
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time

import pandas as pd

# 路径注入: 让 ``news_process.core.*`` 在任意 cwd 下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import (  # noqa: E402
    log_stage_summary,
    pct4,
    setup_logging,
    sig4,
)
from news_process.core.text.ahocorasick import (  # noqa: E402
    load_exclusion_patterns,
    load_fintech_dict,
)
from news_process.core.text.entity_context import (  # noqa: E402
    get_target_aliases,
    has_bank_fintech_cooccurrence_within_radius,
)

CONFIG = load_config()
STAGE_NAME = "13_cooccurrence_filter"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 模块级加载 (镜像 ctx_materializer.py:106-136, 单一匹配语义事实源):
#   - 银行否定/短名排除配置 (与 stage 11/13 同口径)
#   - 金科 AC 自动机 (加载失败 → FINTECH_AC=None → SAFE-1 保留全部行)
_EXCLUSION_FILE = CONFIG['paths'].get(
    'bank_name_exclusions_file',
    os.path.join(os.path.dirname(CONFIG['paths'].get('bank_names_file', '')),
                 'bank_name_exclusions.json'),
)
NEGATION_AC, SHORT_NAME_EXCLUSIONS, CONTEXT_WINDOW = load_exclusion_patterns(
    _EXCLUSION_FILE
)

_FINTECH_DICT_FILE = CONFIG['paths'].get(
    'fintech_dict_file',
    os.path.join(os.path.dirname(CONFIG['paths'].get('bank_names_file', '')),
                 'fintech_dict.json'),
)
try:
    _FINTECH_KEYWORDS, FINTECH_AC = load_fintech_dict(_FINTECH_DICT_FILE)
    logger.info(f"  12b 金科词典已加载: {len(_FINTECH_KEYWORDS)} 词 "
                f"(from {_FINTECH_DICT_FILE})")
except Exception as e:  # noqa: BLE001 — 任何加载失败均优雅降级, 不阻断管道
    logger.warning(f"  12b 金科词典加载失败 ({e}); SAFE-1: 保留全部行 (不过滤)")
    _FINTECH_KEYWORDS, FINTECH_AC = [], None


def _is_valid_bank(target_bank: str) -> bool:
    """非空且非空值哨兵的 target_bank 才可锚定 (否则丢弃)。

    哨兵集覆盖 np.nan→'nan' / None→'None' / pd.NA→'<NA>' / pd.NaT→'NaT'
    的 str() 形态 (CF-03 防御性封闭; 误判方向恒为安全丢弃)。
    """
    s = str(target_bank).strip()
    return bool(s) and s not in ('nan', 'None', '<NA>', 'NaT')


def filter_cooccurrence(df: pd.DataFrame) -> pd.DataFrame:
    """对每个 (文章, target_bank) 行判定窗口邻近共现, 保留命中行 (稳定布尔掩码)。

    SAFE-1: FINTECH_AC=None → 保留全部行 (绝不静默清空)。
    """
    if FINTECH_AC is None:
        logger.warning(
            "  ⚠ SAFE-1: FINTECH_AC=None (词典缺失), 12b 不过滤, 原样保留 "
            f"{len(df)} 行"
        )
        return df.reset_index(drop=True)

    _cfg = CONFIG.get('cooccurrence_filter', {})
    _sentence_radius = _cfg.get('sentence_radius', 1)
    _fallback_char_radius = CONFIG.get('context_window', {}).get(
        'fallback_char_radius', 150
    )
    _bnf = CONFIG['paths'].get('bank_names_file', '')
    _alias_cache: dict = {}

    logger.info(
        f"  12b 窗口邻近共现过滤: sentence_radius={_sentence_radius}, "
        f"fallback_char_radius={_fallback_char_radius}, "
        f"金科词典={len(_FINTECH_KEYWORDS)} 词"
    )

    # 性能 (CF-01): 先 tolist 取出两列再纯 Python 列表 zip 循环, 避开 df.iterrows()
    # 每行构造 Series 的开销 (全量 17M 语料下显著); 语义与逐行等价 (同序、同 mask)。
    _banks = (
        df['target_bank'].tolist() if 'target_bank' in df.columns
        else [None] * len(df)
    )
    _bodies = (
        df['内容'].astype(str).tolist() if '内容' in df.columns
        else [''] * len(df)
    )
    keep = []
    for target_bank, body_full in zip(_banks, _bodies):
        if not _is_valid_bank(target_bank):
            keep.append(False)
            continue
        tb = str(target_bank).strip()
        if tb not in _alias_cache:
            _alias_cache[tb] = get_target_aliases(tb, _bnf)
        keep.append(
            has_bank_fintech_cooccurrence_within_radius(
                body_full, _alias_cache[tb], FINTECH_AC,
                sentence_radius=_sentence_radius,
                negation_ac=NEGATION_AC,
                short_name_exclusions=SHORT_NAME_EXCLUSIONS,
                context_window=CONTEXT_WINDOW,
                fallback_char_radius=_fallback_char_radius,
            )
        )

    mask = pd.Series(keep, index=df.index)
    # 稳定布尔掩码: 保留 stage 12 原序, 刻意不 sort_values。
    return df[mask].reset_index(drop=True)


def _write_sidecar_meta(out_path: str, n_in: int, n_out: int) -> None:
    """落盘 provenance sidecar (判据元数据), 供审稿复算追溯丢行依据。

    写前 unlink 保幂等; 刻意不含 wall-clock 时间戳 (保确定性)。
    """
    _cfg = CONFIG.get('cooccurrence_filter', {})
    criterion = (
        f"windowed_cooccurrence|radius={_cfg.get('sentence_radius', 1)}"
        f"|fallback_char_radius="
        f"{CONFIG.get('context_window', {}).get('fallback_char_radius', 150)}"
        f"|fintech_dict={os.path.basename(_FINTECH_DICT_FILE)}"
        f"|n_keywords={len(_FINTECH_KEYWORDS)}"
    )
    meta = {
        "stage": STAGE_NAME,
        "criterion": criterion,
        "criterion_sha256": hashlib.sha256(criterion.encode("utf-8")).hexdigest(),
        "sentence_radius": _cfg.get('sentence_radius', 1),
        "fintech_dict_file": _FINTECH_DICT_FILE,
        "n_fintech_keywords": len(_FINTECH_KEYWORDS),
        "fintech_ac_loaded": FINTECH_AC is not None,
        "n_rows_in": int(n_in),
        "n_rows_out": int(n_out),
        "n_dropped": int(n_in - n_out),
    }
    meta_path = os.path.splitext(out_path)[0] + ".meta.json"
    if os.path.exists(meta_path):
        os.remove(meta_path)
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2, sort_keys=True)
    logger.info(f"  provenance sidecar 已写出: {meta_path}")


def _log_environment_and_config(in_path: str, out_path: str) -> None:
    """打印 ①项目/环境 ②输入/输出 ③运行配置 ④方法论依据 四块 (日志富集 2026-06-24)。

    对齐 tone_words.py 黄金范式: 把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调
    参数、依据哪些学术方法"一次性落进日志, 便于复现核对 / 审计 / 排错。纯日志, 不改
    任何产物 / schema / 控制流 (golden-safe)。失败仅 WARNING, 绝不阻断阶段。
    """
    try:
        _cfg = CONFIG.get('cooccurrence_filter', {})
        _sentence_radius = _cfg.get('sentence_radius', 1)
        _min_keep_frac = _cfg.get('min_keep_frac', 0.001)
        _fallback_char_radius = CONFIG.get('context_window', {}).get(
            'fallback_char_radius', 150
        )
        _bank_file = CONFIG['paths'].get('bank_names_file', '(默认)')
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')

        # ① 🧭 项目 / 环境信息
        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (stage 12b 银行×金科邻近共现硬过滤, "
                    "STAGES_MAIN)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) "
                    "| 版本 v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段纯 CPU (ahocorasick + 正则分句) / 无 LLM·Embedding·网络·API "
                    "($0); 逐位可复现")

        # ② 📂 输入 / 输出文件
        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入:   {in_path} (stage 12 关键词金科子集)")
        logger.info(f"     · 输出:   {out_path} (= stage 12 的近邻相关子集, 丢行)")
        logger.info(f"     · sidecar: {os.path.splitext(out_path)[0]}.meta.json "
                    "(判据 + criterion_sha256 + 行数对账)")
        logger.info(f"     · 金科词典: {_FINTECH_DICT_FILE}")
        logger.info(f"     · 银行排除: {_EXCLUSION_FILE}")
        logger.info(f"     · 银行别名: {_bank_file}")

        # ③ ⚙ 运行配置 (config/filtering.yaml::cooccurrence_filter 等)
        logger.info("  ⚙ 运行配置 (config/filtering.yaml::cooccurrence_filter 等)")
        logger.info(f"     · sentence_radius={_sentence_radius:,d} 句 (银行锚句 ±radius "
                    "邻句窗口; radius=0 退化为严格同句 _ss 子集)")
        logger.info(f"     · min_keep_frac={sig4(_min_keep_frac)} (keep 率下界; 低于即 "
                    "SystemExit(1) 防全库误删)")
        logger.info(f"     · fallback_char_radius={_fallback_char_radius:,d} 字 "
                    "(无法分句时的字符窗回退)")
        logger.info(f"     · 金科 AC 词数: {len(_FINTECH_KEYWORDS):,d} | FINTECH_AC "
                    f"{'已加载' if FINTECH_AC is not None else 'None → SAFE-1 全保留'}")
        logger.info("     · 不对称匹配口径: 银行侧否定/短名排除 (has_unexcluded_occurrence) "
                    "| 金科侧裸 AC")

        # ④ 📖 方法论依据 (参考文献 emit 进日志; 仅引经核验注册表条目)
        logger.info("  📖 方法论依据")
        logger.info("     · 邻近配对归因过滤: Andreou et al. (2026). Research Policy. "
                    "core-contextual word-pairing within a span (DOI 待核验, 不作已证事实)")
        logger.info("       → 银行与金科词若仅各说各的、隔太远共现, 则主题相关性弱, 删之降"
                    "虚假相关; 本实现是其【句级窗口】操作化")
        logger.info("     · 邻近归因 (proximity-based attribution): Hassan, T. A., "
                    "Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level "
                    "political risk: Measurement and effects. The Quarterly Journal of "
                    "Economics, 134(4), 2135-2202. "
                    "https://doi.org/10.1093/qje/qjz021")
        logger.info("       → §III.B 以「距实体的邻近度」加权归因, 本阶段借其思路把"
                    "「距银行」近邻的金科共现作为主题相关性判据")
    except Exception as e:  # noqa: BLE001 — 环境/配置/方法块日志失败绝不阻断阶段
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def main():
    """Stage 12b 入口: 读 12_fintech_news.parquet → 写 13_cooccurrence_filtered.parquet."""
    stage_start = time.time()
    # 功能说明 banner — 替换旧 "--- 开始执行阶段 ---" 短 banner (对齐 39c 黄金范式:
    # 单 banner 替换而非叠加; 末尾 log_stage_summary 仍负责收尾摘要)。
    logger.info("=" * 72)
    logger.info("阶段 12b: 银行×金科邻近共现硬过滤 (Andreou et al. 2026 Research Policy)")
    logger.info("=" * 72)
    logger.info(
        "【功能】在 stage 12 (关键词金科) 与 stage 13 (物化 ctx) 之间插一道更严的"
        "硬过滤: 只保留 '目标银行与 ≥1 金科词在 ±sentence_radius 句窗口内邻近共现' 的"
        "文章行, 丢弃 '银行与金科隔太远、各说各的' 稿件 → 压降 stage 12 关键词判定的"
        "虚假相关 (False Positives)。产出 = stage 12 的近邻相关子集 parquet + provenance "
        "sidecar (判据 + criterion_sha256 + 行数对账)。"
    )
    logger.info(
        "【方法】逐 (文章, target_bank) 行调 has_bank_fintech_cooccurrence_within_radius: "
        "银行锚句 i (经否定/短名排除) ∧ 金科∈[i±radius] 邻句 (金科侧裸 AC, 不对称口径) → "
        "命中保留。严格同句 (_ss 轨, radius=0) 是本口径子集, 禁互相复用。稳定布尔掩码保留 "
        "stage 12 原序, 不 sort。"
    )
    logger.info(
        "【判读】keep 率越高 = 删得越少 (stage 12 关键词判定本就近邻相关, 噪声少); "
        "keep 率越低 = 剔除的虚假相关越多。⚠ keep 率低于 min_keep_frac 或 0 行 → "
        "SystemExit(1) 报警 (疑似全库误删)。"
    )
    logger.info(
        "【确定性】纯 CPU (ahocorasick + 正则分句), 无 LLM/Embedding/网络, 逐位可复现; "
        "sidecar 刻意不含 wall-clock 时间戳。"
    )
    output_dir = CONFIG['paths']['output_dir']
    filenames = CONFIG.get('filenames', {})
    in_name = filenames.get('output_12_fintech_news', '12_fintech_news.parquet')
    out_name = filenames.get(
        'output_12b_cooccurrence', '13_cooccurrence_filtered.parquet'
    )
    in_path = os.path.join(output_dir, in_name)
    out_path = os.path.join(output_dir, out_name)

    # ①-④ 项目/环境/输入输出/运行配置/方法论依据 块 (日志富集 2026-06-24)
    _log_environment_and_config(in_path, out_path)

    # 运行期各子阶段墙钟耗时累计 (末尾 ⏱ 汇总; 数字一律 sig4 秒)
    phase_durations: dict[str, float] = {}

    if not os.path.exists(in_path):
        logger.error(f"输入未找到: {in_path}")
        raise SystemExit(1)

    _t = time.time()
    df = pd.read_parquet(in_path)
    n_in = len(df)
    n_banks_in = (
        df['target_bank'].astype(str).str.strip().loc[
            lambda s: s.map(lambda x: x not in ('', 'nan', 'None'))
        ].nunique()
        if 'target_bank' in df.columns else 0
    )
    phase_durations['①读盘'] = time.time() - _t
    logger.info(f"加载 stage 12 输出: {n_in:,d} 行, {n_banks_in:,d} 家银行 "
                f"(读盘耗时 {sig4(phase_durations['①读盘'])} 秒)")

    _t = time.time()
    df_kept = filter_cooccurrence(df)
    phase_durations['②邻近共现过滤'] = time.time() - _t
    n_out = len(df_kept)
    n_banks_out = (
        df_kept['target_bank'].astype(str).str.strip().loc[
            lambda s: s.map(lambda x: x not in ('', 'nan', 'None'))
        ].nunique()
        if 'target_bank' in df_kept.columns else 0
    )
    keep_frac = (n_out / n_in) if n_in else 0.0
    logger.info(
        f"  邻近共现过滤: 保留 {n_out:,d}/{n_in:,d} 行 (keep={sig4(keep_frac)} = "
        f"{pct4(keep_frac)}), 丢弃 {n_in - n_out:,d} 行; 银行 {n_banks_in:,d}→"
        f"{n_banks_out:,d} (过滤耗时 {sig4(phase_durations['②邻近共现过滤'])} 秒)"
    )

    # min-N 守卫: 仅当 FINTECH_AC 实际生效 (非 SAFE-1 全保留) 才校验, 防止真实
    # 零共现把整库清空 (词典缺失走 SAFE-1, keep==1.0, 不触发)。
    if FINTECH_AC is not None:
        min_keep_frac = CONFIG.get('cooccurrence_filter', {}).get(
            'min_keep_frac', 0.001
        )
        if n_out == 0 or keep_frac < min_keep_frac:
            logger.error(
                f"  ✗ keep 率 {sig4(keep_frac)} 低于 min_keep_frac="
                f"{sig4(min_keep_frac)} (或 0 行): 疑似全库误删, 中止以防污染下游。请"
                f"核对金科词典/语料/sentence_radius。"
            )
            raise SystemExit(1)

    # --- 结果分析 (纯增量日志; 下列局部变量仅服务于日志打印, 不回写 df / 不入产物) ---
    # crash-guard: 整个 "读数据算指标" 分析块包 try/except, 任何诊断异常只 WARNING 跳过,
    # 绝不阻断后续 save_dataset 写盘 (golden-safe: 日志诊断永不拖垮产物)。
    logger.info("-" * 72)
    logger.info("【结果分析】banner-as-spec: 逐项解读本次硬过滤的产出指标与方向判读")
    _t = time.time()
    try:
        _n_dropped = n_in - n_out
        _drop_frac = (_n_dropped / n_in) if n_in else 0.0
        if FINTECH_AC is None:
            # SAFE-1 生效: 词典缺失 → 原样全保留, keep 必为 1.0
            logger.warning(
                f"  [SAFE-1 优雅降级] FINTECH_AC=None (金科词典加载失败), 12b 未执行任何"
                f"过滤, 原样保留全部 {n_out:,d} 行 (keep={pct4(1.0)})。下游沿用 stage 12 "
                f"原始关键词口径, 近邻共现硬过滤【未生效】, 请核对金科词典 "
                f"{os.path.basename(_FINTECH_DICT_FILE)} 后重跑以激活过滤。"
            )
        elif n_in == 0:
            # 空输入: keep_frac 已被 (if n_in else 0.0) 兜底为 0, 不落数值方向判读分支
            logger.warning(
                "  [空输入] stage 12 输出 0 行, 无可分析的 keep 率/银行覆盖; "
                "请核对上游 stage 12 是否产出。"
            )
        else:
            logger.info(
                f"  [keep_frac] 保留 {n_out:,d}/{n_in:,d} 行, keep={sig4(keep_frac)} "
                f"({pct4(keep_frac)}) (丢弃 {_n_dropped:,d} 行 / drop={pct4(_drop_frac)})。"
            )
            # 方向判读: keep 率对照 min_keep_frac 下界 + 严格同句 (radius=0) 14.27% 零共现上界。
            # 注: 14.27% 是【严格同句零共现率】上界 → 窗口 (radius≥1) 实际丢行率应更低,
            # 即 keep 率应高于 (1-0.1427)=0.8573 这一保守下界 (见 CLAUDE.md v3.10.0 披露)。
            _min_keep = CONFIG.get('cooccurrence_filter', {}).get(
                'min_keep_frac', 0.001
            )
            _ss_zero_cooc_upper = 0.1427  # 严格同句 radius=0 零共现率上界 (disk 1170 篇实测)
            _keep_lower = 1.0 - _ss_zero_cooc_upper  # 保守 keep 率下界 ≈0.8573
            if keep_frac >= _keep_lower:
                logger.info(
                    f"  [判读: 好] keep={sig4(keep_frac)} ({pct4(keep_frac)}) ≥ 保守下界 "
                    f"{sig4(_keep_lower)} (=1−严格同句零共现上界 "
                    f"{pct4(_ss_zero_cooc_upper)}); 窗口邻近 (radius≥1) 删行少于严格同句, "
                    f"符合预期方向 (窗口比同句更宽)。"
                )
            elif keep_frac >= 0.5:
                logger.warning(
                    f"  [判读: 临界] keep={sig4(keep_frac)} ({pct4(keep_frac)}) 低于保守"
                    f"下界 {sig4(_keep_lower)} 但仍 ≥0.5; 删行偏多, 请核对 "
                    f"sentence_radius / 金科词典覆盖是否过严。"
                )
            else:
                logger.warning(
                    f"  [判读: 坏] keep={sig4(keep_frac)} ({pct4(keep_frac)}) <0.5 (删掉"
                    f"过半行) 但未触发 min_keep_frac={sig4(_min_keep)} 中止; 远低于严格同句"
                    f"口径预期, 强烈怀疑词典/语料/radius 配置异常, 请人工复核后再放行下游。"
                )
        # 银行覆盖判读: 过滤后若有银行整家掉出 → 该银行无任何近邻共现稿件, 面板会少一格
        _n_banks_lost = n_banks_in - n_banks_out
        if _n_banks_lost > 0:
            logger.warning(
                f"  [银行覆盖] 过滤后银行数 {n_banks_in:,d}→{n_banks_out:,d} "
                f"(掉出 {_n_banks_lost:,d} 家): 这些银行无任何 '与金科近邻共现' 稿件, "
                f"将不进入下游 bank-year 面板的金科口径。"
            )
        else:
            logger.info(
                f"  [银行覆盖: 好] 银行数 {n_banks_in:,d}→{n_banks_out:,d} (无银行整家掉出), "
                f"面板银行维度无收缩。"
            )
        # 守恒/口径披露 (路线 A): 12b 仅丢行, fintech_share 分母望远镜式坍缩恒不变
        logger.info(
            "  [口径披露] 路线 A 纯接受-披露: 12b 仅丢行, 下游 controls.py/encode.py "
            "零改动; 被丢的中间集从 ft 端移到 nf 端代数和守恒 → fintech_share 分母恒不变, "
            "仅分子(近邻相关金科篇数) 随过滤变小, 已在 manuscript/codebook 如实披露。"
        )
        # 小样本警告 (盘面 T=2)
        if n_banks_out <= 2 or n_in < 5000:
            logger.warning(
                f"  [小样本警告] 当前为盘面小样本 (过滤前 {n_in:,d} 行 / {n_banks_in:,d} 家 → "
                f"过滤后 {n_out:,d} 行 / {n_banks_out:,d} 家, 疑似 T=2 验证盘): 上述 keep 率/"
                f"银行覆盖仅用于验证管道正确性, 全量结论以 17M/T=18 实测为准。"
            )
    except Exception as _e:  # noqa: BLE001 — 诊断日志绝不阻断产物落盘
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")
    phase_durations['③结果分析'] = time.time() - _t
    logger.info("-" * 72)

    _t = time.time()
    from news_process.core.reporting import save_dataset
    _lineage = [
        p for p in (in_path, _FINTECH_DICT_FILE, _EXCLUSION_FILE,
                    CONFIG['paths'].get('bank_names_file', ''))
        if p and os.path.exists(p)
    ]
    save_dataset(df=df_kept, output_path=out_path, logger=logger,
                 stage_name=STAGE_NAME, config=CONFIG, input_files=_lineage)

    # CF-02: parquet 成功落盘【之后】再写 provenance sidecar, 保证 sidecar 永远
    # 描述一个真实存在且最新的 parquet (save_dataset 若抛错则不留陈旧 sidecar)。
    _write_sidecar_meta(out_path, n_in, n_out)
    phase_durations['④写盘+sidecar'] = time.time() - _t

    # ⏱ 各子阶段墙钟耗时汇总 (纯日志; 数字 sig4 秒)
    try:
        logger.info("  ⏱ 各子阶段墙钟耗时 (秒)")
        for _name, _dur in phase_durations.items():
            logger.info(f"     · {_name}: {sig4(_dur)} 秒")
        _total = sum(phase_durations.values())
        logger.info(f"     · 子阶段合计: {sig4(_total)} 秒 (不含 banner/收尾)")
    except Exception as _te:  # noqa: BLE001 — 计时汇总日志绝不阻断阶段
        logger.warning(f"  ⏱ 计时汇总打印失败 (不影响处理): {_te}")

    log_stage_summary(logger, STAGE_NAME, stage_start, n_in, n_out)
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
