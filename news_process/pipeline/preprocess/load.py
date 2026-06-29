"""news_process.pipeline.preprocess.load — 加载层 (AC 自动机 + 单文件并行入口).

Phase 4b 从 ``runner.py`` 提取。包含:
- ``_build_ac_automaton`` / ``_ac_contains_any`` — AC 多模式匹配 helper
- ``BANK_KW_AUTOMATON`` — 模块级单例, 在 import 时一次性构建
- ``_process_single_file`` — ProcessPoolExecutor 工作进程入口, 处理单个 XLSX

依赖关系:
    load.py ← _constants.py
    load.py ← filter.py (Python 子模块, 间接调用)
    load.py ← normalize.py (clean_text_batch)

为打破"_process_single_file 调 filter.py 调 load.py" 的潜在循环, 我们让
filter.py *不再* 在模块顶部 import load.py, 而是改成 lazy import。这样
load.py 仅依赖 _constants 与 normalize, 形成单向 DAG。
"""

from __future__ import annotations

import os
import warnings

import ahocorasick
import numpy as np
import pandas as pd

from news_process.core.logging import pct4
from news_process.pipeline.preprocess._constants import (
    BANK_KEYWORDS,
    CHINESE_CHAR_PATTERN,
    PARAMS,
    REQUIRED_COLUMNS,
    SHEET_NAME,
    logger,
)

# 富集日志一次性开关 (per-worker 进程级, 仅服务日志; ProcessPoolExecutor spawn 的每个
# worker 各自一份 False → 每进程仅在首个文件打印一次方法论引文与配置 banner, 避免逐文件刷屏)。
# 纯日志状态, 不入任何产物 / schema / 控制流 (golden-safe)。
_WORKER_BANNER_EMITTED = False

# ── 经核验参考文献 (VERIFIED_REFERENCES 注册表, 逐字照抄 APA-7 + DOI; 仅日志用) ──
# 白话: 本模块的核心机器就是 Aho-Corasick 多模式匹配自动机 (_build_ac_automaton /
# _ac_contains_any / BANK_KW_AUTOMATON 单例) —— 把数百个银行关键词预编成一张"查词地图",
# 文章只读一遍就同时知道命中了哪些词。此处登记该算法的**原始出处**文献, 运行期随
# 自动机构建与 worker banner 落日志 (溯源到方法本源, 非装饰性"相邻"引用; 纯日志, golden-safe)。
_REFERENCES = {
    # Aho-Corasick 多模式匹配自动机原始算法文献 (本模块 _build_ac_automaton /
    # _ac_contains_any / BANK_KW_AUTOMATON 即其直接实现): 一次 O(n) 线性扫描同时匹配全部模式串。
    'aho_corasick': (
        "Aho, A. V., & Corasick, M. J. (1975). Efficient string matching: "
        "An aid to bibliographic search. Communications of the ACM, 18(6), "
        "333-340. https://doi.org/10.1145/360825.360855"
    ),
}

# ============================================================================
# 1. Aho-Corasick 自动机 (多模式匹配, O(n) 时间复杂度)
# ============================================================================
# 技术原理: AC 自动机在文本上的一次线性扫描中同时匹配所有关键词,
# 时间复杂度 O(文本长度 + 匹配数), 相比逐关键词正则匹配的
# O(文本长度 × 关键词数) 有数量级提升。
# 白话: 把几百个银行关键词预先编成一张"查词地图", 文章从头到尾只读一遍,
# 就能同时知道哪些关键词出现过 — 不用拿每个关键词分别把文章搜一遍。


def _build_ac_automaton(keywords):
    """构建 Aho-Corasick 自动机, 用于 O(n) 时间同时匹配所有关键词.

    Args:
        keywords: 关键词列表。

    Returns:
        ahocorasick.Automaton: 构建好的自动机实例。
    """
    A = ahocorasick.Automaton()
    for kw in keywords:
        A.add_word(kw.lower(), kw)
    A.make_automaton()
    return A


def _ac_contains_any(text: str, automaton) -> bool:
    """O(n) 时间检查文本是否包含自动机中的任一关键词.

    Args:
        text:      待检查的文本。
        automaton: 已构建的 AC 自动机。

    Returns:
        bool: 文本中是否包含至少一个关键词。
    """
    for _ in automaton.iter(text.lower()):
        return True
    return False


def _expand_keyword_variants(keywords) -> list:
    """为银行关键词注入繁体 (OpenCC s2t) + 全角括号变体.

    fix(omni-g-preprocess-07, 2026-06-11): 银行关键词保留过滤 (决定样本存留,
    淘汰 30-50%) 在文本规范化 (ftfy / OpenCC t2s / 全角→半角) **之前** 对原始
    文本执行 (见 _process_single_file: 先 _clean_and_filter_dataframe 再
    clean_text_batch), 而 bank_keywords.json 全部为简体+半角括号 — 繁体源 /
    全角括号源文章会在规范化修复之前被静默丢弃 (latent, 全量 2007-2024 语料)。
    经裁决采纳廉价修法: 构建 AC 自动机时同时加入 s2t 繁体变体与全角括号变体,
    过滤顺序保持不变 (避免对 60-70% 将被地域/类型过滤淘汰的行先做昂贵规范化)。
    OpenCC 不可用时优雅降级 (仅原始关键词 + 全角括号变体, log warning)。

    Args:
        keywords: 原始 (简体) 关键词列表。

    Returns:
        list: 去重排序后的关键词 + 变体列表。
    """
    variants = set(keywords)
    # 全角括号变体 (如 '联合银行(中国)' → '联合银行（中国）')
    variants |= {
        kw.replace('(', '（').replace(')', '）')
        for kw in variants if '(' in kw or ')' in kw
    }
    try:
        import opencc
        _cc_s2t = opencc.OpenCC('s2t')
        variants |= {_cc_s2t.convert(kw) for kw in variants}
        # 繁体变体再补全角括号形态 (组合覆盖: 繁体 × 全角括号)
        variants |= {
            kw.replace('(', '（').replace(')', '）')
            for kw in variants if '(' in kw or ')' in kw
        }
    except Exception as e:  # 防御性回退: opencc 缺失/初始化失败不阻断加载
        logger.warning(f"OpenCC s2t 关键词变体生成失败, AC 自动机不含繁体变体: {e}")
    return sorted(variants)


BANK_KW_AUTOMATON = (
    _build_ac_automaton(_expand_keyword_variants(BANK_KEYWORDS))
    if BANK_KEYWORDS else None
)
if BANK_KW_AUTOMATON is not None:
    logger.info(
        f"Aho-Corasick 自动机构建完成({len(BANK_KEYWORDS)} 个关键词 "
        f"+ 繁体/全角括号变体, fix omni-g-preprocess-07)"
    )
    # 📖 算法本源 (本模块核心匹配机器的原始文献): O(n) 多模式匹配自动机
    logger.info(f"  📖 {_REFERENCES['aho_corasick']}")


# ============================================================================
# 2. 单文件处理 (并行工作进程入口)
# ============================================================================


def _log_worker_banner_once() -> None:
    """每个 worker 进程首个文件时打印一次子步骤 banner (环境/配置/方法论引文).

    本模块是 stage 00 预处理 runner 在 ProcessPoolExecutor 中按文件并行调用的
    worker 级 loader, 无独立 main()/run_stage(), 写入共享 logs/00_preprocessing.log。
    依手册 §0.6 (called-by-runner helper): 不重复打 runner 入口的全量 ENV/CONFIG,
    仅在被调函数起始处打一个子步骤 banner —— 步骤名 + 方法依据引文 + 关键配置。
    用进程级 ``_WORKER_BANNER_EMITTED`` 守卫保证每 worker 仅打一次 (避免逐文件刷屏)。
    纯日志, 不改任何产物 (golden-safe)。
    """
    global _WORKER_BANNER_EMITTED
    if _WORKER_BANNER_EMITTED:
        return
    _WORKER_BANNER_EMITTED = True
    try:
        import platform
        import sys

        logger.info("  🧭 子步骤: stage 00 预处理 · 单文件加载-清洗-长度过滤 (worker 进程入口)")
        logger.info(f"     · 模块: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:  {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:    {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · PID={os.getpid()} | 本步纯 CPU / 无 LLM·网络·API ($0, 确定性)")

        # ⚙ 配置块: 本 worker 实际生效的长度过滤阈值 (来源 config preprocessing.yaml::PARAMS)
        _title_min = PARAMS.get('title_min_length', 2)
        _content_min = PARAMS.get('content_min_length', 100)
        _content_max = PARAMS.get('content_max_length', 10000)
        logger.info(
            f"  ⚙ 长度过滤阈值: 标题汉字≥{_title_min:,} | "
            f"内容汉字 {_content_min:,}~{_content_max:,} | "
            f"银行关键词={len(BANK_KEYWORDS):,} (+繁体/全角括号变体, AC 自动机 O(n) 匹配)"
        )

        # 📖 方法论依据 (长度过滤下限的测量可靠性论证; 逐字取自经核验参考文献注册表)
        logger.info("  📖 方法论依据 (长度过滤下限):")
        logger.info(
            "     · Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S. (2008). "
            "More than words: Quantifying language to measure firms' fundamentals. "
            "The Journal of Finance, 63(3), 1437-1467. "
            "https://doi.org/10.1111/j.1540-6261.2008.01362.x"
        )
        logger.info(
            "       → 每篇 ≥50 词以保证语调测度可靠 (排除表格/列表残片); "
            "本阶段以汉字数近似 (50 词≈75-100 字), 取 100 汉字为更宽松边界"
        )
        logger.info(
            "       → 标题 ≥2 汉字属**数据完整性过滤** (剔空/损坏标题), 非样本选择: "
            "被删项以 0 字 (空/损坏) 为主而非 1 字真标题 (删除构成诊断见 "
            "_log_title_filter_diagnostics); 内容上限 10000 汉字排除超长文体噪声, "
            "长文语调影响由按年标准化压制 (TSM 2008 实际不设上限, 故上限仅作稳健性边界)。"
        )

        # 📖 方法论依据 (多模式匹配机器): 银行关键词保留过滤由 Aho-Corasick 自动机驱动
        logger.info("  📖 方法论依据 (多模式匹配自动机):")
        logger.info(f"     · {_REFERENCES['aho_corasick']}")
        logger.info(
            "       → 一次 O(n) 线性扫描同时匹配全部银行关键词 (含繁体/全角括号变体), "
            "取代逐关键词 O(n×k) 正则; 本模块 _build_ac_automaton / _ac_contains_any 即其直接实现"
        )
    except Exception as e:  # noqa: BLE001  纯日志, 失败绝不阻断 worker 处理
        logger.warning(f"  worker banner 打印失败 (不影响处理): {e}")


# ============================================================================
# 长度过滤诊断 (log-only, 零行为变更)
# ============================================================================
# 动机 (2026-06-13 长度区间顶刊合规化): 顶刊对长度过滤的要求不是某个标准数字,
# 而是 (a) 下限的测量可靠性论证 + (b) 上限的文体噪声排除论证 + (c) data appendix
# 分布披露与截断敏感性。本诊断为 (c) 供数: 每个源文件记录内容长度分布分位数 +
# 替代阈值矩阵下的保留行数, 论文附录直接从生产 run 日志汇总, 无需重跑语料。
# 文献锚点: Tetlock/Saar-Tsechansky/Macskassy 2008 JF 要求每篇 ≥50 词 (引文出自
# 其 Columbia 工作论文版 p.9, 非刊印版页码; 排除表格/列表残片 + 限制比值型语调
# 指标的离群影响), 且**不设上限** (长文影响靠语调按年标准化压制; 其 1% winsorize
# 的对象是 SUE/分析师预测等结果变量, 非语调) —
# 详见 scripts/audit/LENGTH_FILTER_JUSTIFICATION_2026-06-13.md。
# ⚠ 供数前提: stage 00 增量缓存命中时 worker 被跳过, 不产生本诊断日志;
# [长度诊断] 行仅在冷缓存/重算路径出现 (全量生产 run 为新语料 → 天然冷缓存)。
# 白话: 不动现有的 100~10000 字门槛, 只在日志里多记一笔"如果门槛换成别的数,
# 会留下多少篇" — 将来论文附录要做"门槛换了结果也不变"的检验时, 数据现成。

# 替代阈值矩阵: min 50 = TSM 2008 ≥50 词的字面数字 (注: 此处比较的是汉字数,
# 50 词信息量约对应 75-100 字, 故 50-汉字是比 TSM 更宽松的下限, 取作敏感性边界);
# 200 = 加倍保守; max 包围生产值 10000; None = 不设上限 (TSM 2008 实际做法)。
_DIAG_MIN_CUTOFFS = (50, 100, 200)
_DIAG_MAX_CUTOFFS = (5000, 10000, 20000, None)


def _length_filter_diagnostics(content_len: pd.Series) -> dict:
    """计算内容汉字数分布与替代截断阈值下的保留行数 (纯诊断, 不过滤).

    Args:
        content_len: 每行内容的汉字计数 Series (调用方已算好, 此处零额外扫描)。

    Returns:
        dict: ``{'n', 'pctiles', 'min', 'max', 'kept'}``;
        ``kept`` 键为 ``(min_cutoff, max_cutoff)`` 元组 (max=None 表示不设上限),
        值为该组合下保留的行数。空 Series 或全 NaN 时仅含 ``{'n': 0}``。
    """
    # 全 NaN 守卫: 生产路径 (filter.py dropna + normalize.py fillna) 下 content_len
    # 恒为 int64 无 NaN, 此守卫为 no-op; 仅防御病理性全 NaN 输入致 int(min())=int(NaN)
    # 崩溃 (与改前一致: 该文件本就会被过滤为空 → 返回 None, 此处仅免去 ERROR traceback)。
    n = len(content_len)
    if n == 0 or content_len.notna().sum() == 0:
        return {'n': 0}
    pct = content_len.quantile([0.01, 0.05, 0.50, 0.95, 0.99])
    kept = {}
    for lo in _DIAG_MIN_CUTOFFS:
        for hi in _DIAG_MAX_CUTOFFS:
            mask = content_len >= lo
            if hi is not None:
                mask &= content_len <= hi
            kept[(lo, hi)] = int(mask.sum())
    return {
        'n': n,
        'pctiles': {float(p): int(v) for p, v in pct.items()},
        'min': int(content_len.min()),
        'max': int(content_len.max()),
        'kept': kept,
    }


def _log_length_filter_diagnostics(content_len: pd.Series) -> None:
    """将 ``_length_filter_diagnostics`` 结果格式化为紧凑日志 (含保留率判读)."""
    diag = _length_filter_diagnostics(content_len)
    if diag['n'] == 0:
        return
    p = diag['pctiles']
    logger.info(
        f"  [长度诊断] 内容汉字数分布 (n={diag['n']:,}): "
        f"min={diag['min']} p1={p[0.01]} p5={p[0.05]} p50={p[0.5]} "
        f"p95={p[0.95]} p99={p[0.99]} max={diag['max']}"
    )
    kept_str = ' | '.join(
        f"≥{lo}~{'∞' if hi is None else hi}:{cnt:,}"
        for (lo, hi), cnt in diag['kept'].items()
    )
    logger.info(f"  [长度诊断] 替代阈值保留行数: {kept_str}")
    # 📊 关键指标解读 (运行结果信息): 生产阈值 (100~10000 汉字) 下的保留率 + 阈值敏感性判读
    try:
        n = diag['n']
        lo_prod = PARAMS.get('content_min_length', 100)
        hi_prod = PARAMS.get('content_max_length', 10000)
        kept_prod = diag['kept'].get((lo_prod, hi_prod))
        if kept_prod is not None and n > 0:
            keep_frac = kept_prod / n
            # 与"不设上限"对照: TSM 2008 实际做法不设上限 → 上限剔除应仅占极小比例
            kept_noupper = diag['kept'].get((lo_prod, None))
            upper_drop = (
                (kept_noupper - kept_prod) / n
                if kept_noupper is not None else float('nan')
            )
            verdict = (
                '✅ 主体保留, 长度过滤温和' if keep_frac >= 0.70
                else '⚠ 保留率偏低, 截断敏感性需复核' if keep_frac >= 0.40
                else '❌ 过滤过激, 多数行被剔除 (须核查阈值/语料)'
            )
            logger.info(
                f"  [长度诊断] 生产阈值 {lo_prod:,}~{hi_prod:,} 保留率="
                f"{pct4(keep_frac)} (其中上限剔除占 {pct4(upper_drop)}) → {verdict}"
            )
            # 判读阈值显式化 (审计可见性): 保留率判读门槛随结果落日志, 免回查源码。
            logger.info(
                f"  [长度诊断] 保留率判读阈值: ≥{pct4(0.70)} 温和 | "
                f"≥{pct4(0.40)} 临界 | <{pct4(0.40)} 过激 (须核查阈值/语料)"
            )
    except Exception as e:  # noqa: BLE001  纯日志, 失败绝不阻断处理
        logger.warning(f"  [长度诊断] 保留率判读失败 (不影响处理): {e}")


# 标题长度替代阈值: 1/2/3 字, 用于支撑"≥2 删的是损坏行而非真标题"的披露主张。
_DIAG_TITLE_CUTOFFS = (1, 2, 3)


def _title_filter_diagnostics(title_len: pd.Series) -> dict:
    """计算标题汉字数过滤的删除构成 (纯诊断, 不过滤).

    动机 (2026-06-13 第三轮终审): 标题 ≥2 字被定性为"数据完整性过滤, 非样本选择",
    但该定性须由删除构成数据支撑 — 须证明被 ≥2 删除的标题以 0 字 (空/损坏) 为主、
    而非大量 1 字真标题。本诊断按 ≥1/≥2/≥3 替代阈值记保留行数 + 拆出被 ≥2 删除者
    中 0 字 / 1 字各几行, 供 data appendix 坐实"无样本选择风险"。

    Args:
        title_len: 每行标题的汉字计数 Series (调用方已算好, 零额外扫描)。

    Returns:
        dict: ``{'n', 'kept', 'removed_lt2', 'n_zero', 'n_one'}``;
        ``kept`` 键为阈值 (1/2/3) → 保留行数。空 Series 或全 NaN 时仅含 ``{'n': 0}``。
    """
    n = len(title_len)
    if n == 0 or title_len.notna().sum() == 0:
        return {'n': 0}
    kept = {c: int((title_len >= c).sum()) for c in _DIAG_TITLE_CUTOFFS}
    return {
        'n': n,
        'kept': kept,
        'removed_lt2': n - kept[2],
        'n_zero': int((title_len == 0).sum()),
        'n_one': int((title_len == 1).sum()),
    }


def _log_title_filter_diagnostics(title_len: pd.Series) -> None:
    """将 ``_title_filter_diagnostics`` 结果格式化为紧凑日志 (含样本选择风险判读)."""
    d = _title_filter_diagnostics(title_len)
    if d['n'] == 0:
        return
    k = d['kept']
    logger.info(
        f"  [长度诊断] 标题汉字数 (n={d['n']:,}): "
        f"保留 ≥1:{k[1]:,} ≥2:{k[2]:,} ≥3:{k[3]:,} | "
        f"被≥2删除 {d['removed_lt2']:,} (其中 0字:{d['n_zero']:,} 1字:{d['n_one']:,})"
    )
    # 📊 关键指标解读: 被 ≥2 删除者中 0 字 (空/损坏) 占比越高 → 越坐实"数据完整性过滤, 非样本选择"
    try:
        removed = d['removed_lt2']
        if removed > 0:
            zero_share = d['n_zero'] / removed
            verdict = (
                '✅ 删除项以 0 字(空/损坏)为主 → 数据完整性过滤, 非样本选择' if zero_share >= 0.80
                else '⚠ 含较多 1 字真标题, 样本选择风险需附录披露' if zero_share >= 0.50
                else '❌ 多为 1 字真标题, 存在样本选择风险'
            )
            logger.info(
                f"  [长度诊断] 标题 ≥2 删除构成: 0字占 {pct4(zero_share)} → {verdict}"
            )
            # 判读阈值显式化 (审计可见性): 把硬编码门槛随结果一并落日志, 便于
            # 复核"本批 0 字占比落在哪一档"而无需回查源码常量 (纯日志, 不改判读)。
            logger.info(
                f"  [长度诊断] 0字占比判读阈值: ≥{pct4(0.80)} 数据完整性过滤 | "
                f"≥{pct4(0.50)} 临界(含 1 字真标题) | <{pct4(0.50)} 样本选择风险"
            )
    except Exception as e:  # noqa: BLE001  纯日志, 失败绝不阻断处理
        logger.warning(f"  [长度诊断] 标题删除构成判读失败 (不影响处理): {e}")


def _process_single_file(file_path: str) -> pd.DataFrame | None:
    """读取并清洗单个 XLSX 文件.

    设计为在 ``ProcessPoolExecutor`` 的工作进程中运行(spawn 模式)。
    每个文件独立处理, 进程间无共享状态。

    处理流程: Excel 读取 → 过滤 → 文本标准化 → 长度过滤

    Args:
        file_path: XLSX 文件的绝对路径。

    Returns:
        pd.DataFrame | None: 处理后的 DataFrame, 或 None(处理失败/数据为空)。
    """
    # lazy import, 避免模块加载期循环依赖:
    # - filter.py 从本模块 import BANK_KW_AUTOMATON
    # - normalize.py 是仅依赖 _constants 的 sibling 模块
    from news_process.pipeline.preprocess.filter import _clean_and_filter_dataframe
    from news_process.pipeline.preprocess.normalize import clean_text_batch

    file_name = os.path.basename(file_path)
    try:
        # 每 worker 进程首个文件时打印一次子步骤 banner (环境/配置/方法论引文)
        _log_worker_banner_once()
        logger.info(f"--- 开始处理: {file_name} ---")

        # 使用 calamine 引擎(基于 Rust, 比 openpyxl 快 5-10x)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            df_chunk = pd.read_excel(
                file_path, sheet_name=SHEET_NAME,
                engine="calamine", usecols=REQUIRED_COLUMNS
            )

        logger.info(f"  加载 {len(df_chunk):,} 行, 开始过滤...")
        # 📥 输入溯源 (I/O provenance): 实读 sheet / 列 schema / 列数 / 绝对路径 —
        # 给审计一条 "输入文件 → 行×列 → schema" 完整入口痕迹 (纯日志, 失败绝不阻断)。
        try:
            _cols = list(df_chunk.columns)
            logger.info(
                f"     📥 输入: sheet='{SHEET_NAME}' | "
                f"{len(df_chunk):,} 行 × {len(_cols):,} 列 | "
                f"列 schema={_cols} | usecols 要求列={list(REQUIRED_COLUMNS)}"
            )
            logger.info(f"     📂 源文件绝对路径: {os.path.abspath(file_path)}")
        except Exception as _e_io:  # noqa: BLE001  纯日志, 失败绝不阻断 worker 处理
            logger.warning(f"     输入溯源日志失败 (不影响处理): {_e_io}")

        # ── 初步过滤 ──
        df_cleaned = _clean_and_filter_dataframe(df_chunk)
        n_loaded = len(df_chunk)  # log-only: 入口装载行数 (供完成时整体保留率, 不参与任何计算)
        del df_chunk  # 及早释放原始数据内存

        if df_cleaned.empty:
            logger.warning(f"  {file_name}: 过滤后无有效数据, 跳过")
            return None

        # ── 文本标准化 ──
        logger.info(f"  开始文本标准化({len(df_cleaned):,} 行)...")
        df_cleaned = clean_text_batch(df_cleaned)

        # 统计疑似代码/结构化文档(仅记录, 不过滤)
        if 'suspected_code_doc' in df_cleaned.columns:
            suspect_count = df_cleaned['suspected_code_doc'].sum()
            if suspect_count > 0:
                # 占比 (result statistic): 给裸计数补上分母 → 数据质量份额 (纯日志, 失败回退裸计数)
                try:
                    _suspect_share = suspect_count / len(df_cleaned)
                    logger.info(
                        f"  疑似代码/结构化文档: {suspect_count:,} 条 "
                        f"(占清洗后 {len(df_cleaned):,} 行的 {pct4(_suspect_share)})"
                    )
                except Exception as _e_sc:  # noqa: BLE001  纯日志, 失败不阻断
                    logger.info(f"  疑似代码/结构化文档: {suspect_count:,} 条")
            df_cleaned.drop(columns=['suspected_code_doc'], inplace=True)

        if df_cleaned.empty:
            logger.warning(f"  {file_name}: 标准化后无有效数据, 跳过")
            return None

        # ── 长度过滤 ──
        TITLE_MIN_LEN = PARAMS.get('title_min_length', 2)
        CONTENT_MIN_LEN = PARAMS.get('content_min_length', 100)
        CONTENT_MAX_LEN = PARAMS.get('content_max_length', 10000)

        # 标题汉字数过滤
        rows_before = len(df_cleaned)
        title_chinese_len = df_cleaned['标题'].astype(str).str.count(CHINESE_CHAR_PATTERN)
        # 过滤前记标题删除构成诊断 (log-only; 支撑"≥2 删的是损坏行"披露)
        _log_title_filter_diagnostics(title_chinese_len)
        df_cleaned = df_cleaned[title_chinese_len >= TITLE_MIN_LEN]
        logger.info(
            f"  [标题长度≥{TITLE_MIN_LEN}] "
            f"移除 {rows_before - len(df_cleaned):,} 行 → 剩余 {len(df_cleaned):,}"
        )

        # 内容汉字数过滤(上下限合并为一次计算, 避免创建两个中间布尔 Series)
        rows_before = len(df_cleaned)
        content_chinese_len = df_cleaned['内容'].astype(str).str.count(CHINESE_CHAR_PATTERN)
        # 过滤前先记分布与替代阈值诊断 (log-only; data appendix 截断敏感性供数)
        _log_length_filter_diagnostics(content_chinese_len)
        df_cleaned = df_cleaned[
            (content_chinese_len >= CONTENT_MIN_LEN) & (content_chinese_len <= CONTENT_MAX_LEN)
        ]
        logger.info(
            f"  [内容长度 {CONTENT_MIN_LEN}~{CONTENT_MAX_LEN}] "
            f"移除 {rows_before - len(df_cleaned):,} 行 → 剩余 {len(df_cleaned):,}"
        )

        # Schema 安全检查: 确保所有 object 列转为 string
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == 'object':
                df_cleaned[col] = df_cleaned[col].fillna('').astype(str)

        if df_cleaned.empty:
            logger.warning(f"  {file_name}: 长度过滤后无有效数据, 跳过")
            return None

        logger.info(f"--- 完成: {file_name} → 保留 {len(df_cleaned):,} 行 ---")
        # 📊 端到端保留率 (result statistic): 出口保留行 / 入口装载行 = 单文件全链净留存
        # (Excel 装载 → 初步过滤 → 文本标准化 → 长度过滤); 纯日志, 失败绝不阻断。
        try:
            if n_loaded > 0:
                logger.info(
                    f"  📊 端到端保留率: {len(df_cleaned):,}/{n_loaded:,} "
                    f"= {pct4(len(df_cleaned) / n_loaded)} "
                    f"(Excel 装载 → 过滤·标准化·长度过滤 全链净留存)"
                )
        except Exception as _e_ret:  # noqa: BLE001  纯日志, 失败不阻断
            logger.warning(f"  端到端保留率日志失败 (不影响处理): {_e_ret}")
        return df_cleaned

    except Exception as e:
        logger.error(f"处理文件 {file_name} 时出错: {e}", exc_info=True)
        return None


# numpy 由 _clean_and_filter_dataframe 的 AC mask 使用; 此处也 import 一次,
# 确保 ProcessPoolExecutor spawn 出的 worker 进程重新导入时它已就位
# (对微妙的 import 顺序时序问题做防御)。
_ = np  # 消除 "imported but unused" 告警


__all__ = [
    '_build_ac_automaton',
    '_ac_contains_any',
    '_expand_keyword_variants',
    'BANK_KW_AUTOMATON',
    '_length_filter_diagnostics',
    '_log_length_filter_diagnostics',
    '_log_title_filter_diagnostics',
    '_title_filter_diagnostics',
    '_process_single_file',
]
