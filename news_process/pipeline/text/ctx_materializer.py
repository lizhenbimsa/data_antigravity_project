"""news_process.pipeline.text.ctx_materializer — stage 13 content_ctx 物化.

Plan E P4 A1 (v3.6.0):
    把原 stage 21 (tone_llms._materialize_content_ctx) 中的 content_ctx
    物化逻辑前置到一个独立 stage 13, 让 stage 14 (fintech_intensity)
    和 stage 15 (policy_alignment) 能在 stage 21 之前消费 content_ctx,
    实现真正的双轨化 (B1 + B2 闭合)。

工作流:
    stage 12 (news_fintech) → 12_fintech_news.parquet
    stage 13 (本模块)        → 13_news_with_ctx.parquet  (= 12 + content_ctx 列)
    stage 14 (fintech_intensity) → 读 13, 双轨产 fintech_intensity_score_{full,ctx}
    stage 15 (policy_alignment)  → 读 14, 双轨产 policy_cosine_sim_{full,ctx}
    stage 21 (tone_llms)         → 已物化的 content_ctx 直接复用 (跳过重复物化)

学术依据:
    Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019).
    Firm-level political risk: Measurement and effects. The Quarterly
    Journal of Economics, 134(4), 2135-2202.
    https://doi.org/10.1093/qje/qjz021
    → §III.B "proximity-based attribution" — 实体特异性上下文窗口

向后兼容:
    若 stage 13 未跑, stage 21 仍会自己物化 content_ctx (tone_llms.py:1100
    的 _materialize_content_ctx 不删, 改为 idempotent: 检测列存在则跳过).
    这保证 v3.5.0 既有 pipeline 行为不变。
"""
from __future__ import annotations

import os
import sys
import time

import pandas as pd

# Path injection
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import setup_logging  # noqa: E402
from news_process.core.text.entity_context import (  # noqa: E402
    extract_entity_context,
    get_target_aliases,
)

CONFIG = load_config()
STAGE_NAME = "13_materialize_ctx"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


def materialize_content_ctx(df: pd.DataFrame) -> pd.DataFrame:
    """物化 content_ctx 列 (idempotent).

    若 'content_ctx' 已在 df.columns, 直接返回 — 避免重复计算。
    否则按 config 中 context_window 节读取 sentence_radius 和
    fallback_char_radius, 对每个 (文章, target_bank) 对调用
    extract_entity_context()。

    Args:
        df: 含 '内容' 和 'target_bank' 列。

    Returns:
        df: 新增 'content_ctx' 列 (若已存在则不变)。
    """
    # remove-title-track: 两轨文本均需"包含标题"。content_full (= 标题 + 内容)
    # 与 content_ctx (= 标题 + 实体窗口) 都经 prepend_title 注入标题。原始 '内容'
    # 列保持不变 (仍供 doc_length / 去重 / 上下半切分 / fintech 强度分母 / topic /
    # staleness 等非情感复用)。下游 full 轨情感消费者改读 content_full。
    from news_process.core.text.entity_context import prepend_title

    if ('content_full' in df.columns and 'content_ctx' in df.columns
            and 'ctx_is_fallback' in df.columns):
        logger.info("  'content_full' + 'content_ctx' + 'ctx_is_fallback' 已存在, "
                    "跳过物化 (idempotent)")
        return df

    # 旧 schema 兼容 (remove-title-track): content_ctx 已被上游物化, 但缺
    # content_full / ctx_is_fallback。**不重算 content_ctx** (尊重既有物化值),
    # 仅补算缺列: content_full = 标题 + 内容; ctx_is_fallback = (content_ctx ≡ 内容)。
    # content_ctx 此处保持原值不再注入标题 (上游已定; 与 prepend_title 的 startswith
    # 去重不冲突)。
    if 'content_ctx' in df.columns and not (
            'content_full' in df.columns and 'ctx_is_fallback' in df.columns):
        df = df.copy()
        _bodies_old = df['内容'].astype(str).tolist()
        _ctx_old = df['content_ctx'].astype(str).tolist()
        if 'ctx_is_fallback' not in df.columns:
            df['ctx_is_fallback'] = pd.Series(
                [c == b for c, b in zip(_ctx_old, _bodies_old)],
                index=df.index,
            ).astype('bool')
        if 'content_full' in df.columns:
            pass
        elif '标题' in df.columns:
            _titles_old = df['标题'].fillna('').astype(str).tolist()
            df['content_full'] = [prepend_title(t, b)
                                  for t, b in zip(_titles_old, _bodies_old)]
        else:
            df['content_full'] = _bodies_old
        logger.info(f"  旧 schema: content_ctx 已存在, 补算 content_full + "
                    f"ctx_is_fallback ({int(df['ctx_is_fallback'].sum())}/{len(df)} True)")
        return df

    _ctx_cfg = CONFIG.get('context_window', {})
    _sentence_radius = _ctx_cfg.get('sentence_radius', 1)
    _fallback_char_radius = _ctx_cfg.get('fallback_char_radius', 150)

    logger.info(f"物化 content_full + content_ctx 列 (含标题注入) — "
                f"sentence_radius={_sentence_radius}, "
                f"fallback_char_radius={_fallback_char_radius}")
    _bnf = CONFIG['paths'].get('bank_names_file', '')
    _alias_cache: dict = {}

    full_list = []       # full 轨: 标题 + 内容
    ctx_list = []        # ctx 轨: 标题 + 实体窗口 (或 fallback)
    ctx_body_list = []   # ctx 的纯 body 部分 (无标题前缀), 仅用于 fallback 判定
    for _, row in df.iterrows():
        body_full = str(row.get('内容', ''))
        title = str(row.get('标题', '') or '')
        target_bank = str(row.get('target_bank', ''))
        if target_bank and target_bank not in ('nan', 'None'):
            if target_bank not in _alias_cache:
                _alias_cache[target_bank] = get_target_aliases(target_bank, _bnf)
            ctx_body = extract_entity_context(
                body_full, _alias_cache[target_bank],
                sentence_radius=_sentence_radius,
                fallback_char_radius=_fallback_char_radius,
            )
            if not ctx_body:
                ctx_body = body_full  # 回退公理: 无匹配时保留全文 body
        else:
            ctx_body = body_full
        ctx_body_list.append(ctx_body)
        full_list.append(prepend_title(title, body_full))
        ctx_list.append(prepend_title(title, ctx_body))

    df = df.copy()
    df['content_full'] = full_list
    df['content_ctx'] = ctx_list
    # v3.7.2 R8-H1 全管道延伸: ctx_is_fallback 暴露 entity-miss 信号。
    # remove-title-track: 因两轨都前置了同一标题, 判定改为比较"去标题后的 body"
    # (ctx_body vs 全文 body), 标题前缀对两轨同样, 不影响 entity-miss 语义。
    # 锚定: lexical_discriminant_validity.py:20 (R8-H1 audit anchor)
    _bodies = df['内容'].astype(str).tolist()
    df['ctx_is_fallback'] = pd.Series(
        [cb == fb for cb, fb in zip(ctx_body_list, _bodies)],
        index=df.index,
    ).astype('bool')
    n_fallback = sum(1 for cb, fb in zip(ctx_body_list, _bodies) if cb == fb)
    assert int(df['ctx_is_fallback'].sum()) == n_fallback, \
        f"ctx_is_fallback 列计数 ({int(df['ctx_is_fallback'].sum())}) " \
        f"与 batch 统计 ({n_fallback}) 不一致"
    _bank_strs = df['target_bank'].astype(str).str.strip()
    n_with_bank = ((_bank_strs != '') & (_bank_strs != 'nan') &
                   (_bank_strs != 'None')).sum()
    logger.info(f"  content_ctx 物化完成: {len(df)} 行, "
                f"回退至全文: {n_fallback}/{n_with_bank} 条 "
                f"({n_fallback/max(n_with_bank,1)*100:.1f}%)")
    logger.info(f"  ctx_is_fallback 列已写入 (bool): "
                f"{int(df['ctx_is_fallback'].sum())}/{len(df)} True")
    return df


def main():
    """Stage 13 入口: 读 12_fintech_news.parquet → 写 13_news_with_ctx.parquet."""
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")
    output_dir = CONFIG['paths']['output_dir']
    filenames = CONFIG.get('filenames', {})
    in_name = filenames.get('output_12_fintech_news', '12_fintech_news.parquet')
    out_name = filenames.get('output_13_news_with_ctx', '13_news_with_ctx.parquet')
    in_path = os.path.join(output_dir, in_name)
    out_path = os.path.join(output_dir, out_name)

    if not os.path.exists(in_path):
        logger.error(f"输入未找到: {in_path}")
        raise SystemExit(1)

    df = pd.read_parquet(in_path)
    logger.info(f"加载 stage 12 输出: {len(df)} 行")
    df = materialize_content_ctx(df)
    assert 'content_full' in df.columns
    assert 'content_ctx' in df.columns

    from news_process.core.reporting import save_dataset
    save_dataset(df=df, output_path=out_path, logger=logger,
                 stage_name=STAGE_NAME, config=CONFIG, input_files=[in_path])

    from news_process.core.logging import log_stage_summary
    log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
