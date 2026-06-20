"""news_process.pipeline.panel.verified_universe — stage-21 verified 域门控 helper.

提供 ``restrict_to_verified``: 把"文章×银行"粒度的帧按 ``(docid, target_bank)``
inner-join 收敛到 stage-21 LLM 语义精筛后的 verified 集 (``24_herd_decay.parquet``),
让 attention / dedup-sensitivity 等"直读 pre-21 文件 (15_fintech_intensity /
12_fintech_news_full) 再聚合"的处理变量与面板其余文本测度共享同一聚合域。

背景 (panel-universe-consistency-audit 2026-06-13, ATT-1/DEDUP-1): stage 14 的规则
预筛候选集含约 26.8% 被 stage 21 判伪 (非真实银行-金融科技报道) 的文章。面板的政策
对齐族已由 ``runner.py::_filter_to_verified_universe`` 在聚合前 semi-join 收敛到
verified 集; attention 处理变量族 (及其去重敏感性镜像) 此前漏覆盖, 本 helper 统一该
门控。刻意与 runner 的同名内部函数解耦 (runner 反向 import attention_media / dedup,
不可循环), 故另置本中性模块。

⚠ 仅门控**分子** (fintech 强度/计数/HHI 源帧); **分母与全集脊柱** (全部银行新闻
``n_all`` / ``universe``) 必须保持 12_full 全集不变 (Fang-Peress 关注度分母; 非
fintech 银行新闻行从不经 stage 21 验证, 物理上不可门控), 否则破坏 NaN-vs-0 契约与
份额语义 (attention_pct = 已验证 fintech / 全部银行新闻 才是干净的议程份额)。

三轨 (full/ctx/ss) 自动继承 (2026-06-14): 本 helper 按 ``(docid, target_bank)``
inner-join 门控, 是 **track-agnostic** 的行级语义过滤 — 它只决定"哪些 (文章, 银行)
对幸存", 与情感轨后缀 (_full/_ctx/_ss) 无关。故新增的 ss 轨 (银行+金科同句共现:
fintech_intensity_score_ss / llm_vote_tone_ss 等) 在本模块**零改自动进 verified 门**,
无需任何 _ss 分支; 上游调用方 (attention_media / dedup_sensitivity) 各自的 ss 列
随其 full/ctx 兄弟一同经此 semi-join 收敛到同一聚合域。

自包含读盘说明 (审计计划 D1/C4): 本 helper 直接读 ``24_herd_decay.parquet`` 作
verified 脊柱。这在 stage-45 runner 内成立, 因 runner 从同一文件载入 df (runner.py:~535, df_exploded 别名 :~993)
且在调用 attention/dedup 前 (compute_fintech_attention_index /
compute_attention_treatments / compute_dedup_sensitivity_treatments,
~L1015-1027) 仅按列追加、不删行 →
盘面 ≡ 内存。若未来在 attention 调用前对 df_exploded 加行级过滤, 应改为把 verified
keyset 显式传入而非读盘。
"""
from __future__ import annotations

import logging
import os

import pandas as pd

_MODULE_LOGGER = logging.getLogger(__name__)

# fail-open 时的统一响亮告警 (%s 占位: label / 原因)。门控被跳过即意味着该测度
# 退回含约 26.8% stage-21 判伪文章的 pre-21 全集, 非出版级 — 必须 loud。
_SKIP_MSG = (
    "VERIFIED 域门控跳过 [%s]: %s — 返回**未门控**全集 (含约 26.8%% 被 stage-21 "
    "判伪文章, 非出版级; 仅应出现于旧 schema / 合成帧 / 缺 24_herd_decay 时)"
)


def restrict_to_verified(
    df: pd.DataFrame,
    output_dir: str,
    filenames: dict,
    *,
    keys=('docid', 'target_bank'),
    logger=None,
    label: str = '',
) -> pd.DataFrame:
    """按 ``keys`` inner-join 把 ``df`` 收敛到 stage-21 verified 集 (24_herd_decay)。

    Graceful fail-open (镜像 runner.py::_filter_to_verified_universe): 当
    (a) ``df`` 缺 ``keys`` 列, (b) ``24_herd_decay`` 文件缺失, 或 (c) verified 帧
    读键失败 时, 发出响亮 warning 并**原样返回未门控 ``df``** (保旧 schema / 合成
    测试帧不崩)。生产 schema 恒含 docid → 必走门控路径。

    verified keyset 经 ``drop_duplicates`` → 即便 ``df`` 在 ``keys`` 上有重复行,
    inner-join 也不会放大行数 (每行至多匹配一条 verified 键)。

    Args:
        df:          文章×银行粒度帧 (须含 ``keys`` 列方能门控)。
        output_dir:  data/processed 目录 (定位 24_herd_decay)。
        filenames:   ``CONFIG['filenames']`` 风格 dict (取 ``output_24_herd_decay``)。
        keys:        join 键; 默认 ``(docid, target_bank)`` (验证是 article×bank 级,
                     同 docid 可对 A 行判真、对 B 行判伪 → 不可用 docid 单键)。
        logger:      调用方 logger (None → 模块 logger)。
        label:       日志标识 (如 ``'attention.s14'``)。

    Returns:
        门控后子集 (行数 ≤ len(df)); 或 fail-open 时原 ``df``。
    """
    log = logger if logger is not None else _MODULE_LOGGER
    keys = list(keys)

    missing_in = [k for k in keys if k not in df.columns]
    if missing_in:
        log.warning(_SKIP_MSG, label, f"输入帧缺键 {missing_in}")
        return df

    herd_path = os.path.join(
        output_dir, filenames.get('output_24_herd_decay', '24_herd_decay.parquet'))
    if not os.path.exists(herd_path):
        log.warning(_SKIP_MSG, label, f"24_herd_decay 缺失 ({herd_path})")
        return df

    try:
        verified = pd.read_parquet(herd_path, columns=keys).drop_duplicates()
    except Exception as exc:  # noqa: BLE001 — verified 帧缺键/读错均 fail-open
        log.warning(_SKIP_MSG, label, f"读 24_herd_decay 键失败 ({exc})")
        return df

    n_before = len(df)
    out = df.merge(verified, on=keys, how='inner')
    log.info("  verified 域门控 [%s]: %d → %d 行 (semi-join 24_herd_decay on %s)",
             label, n_before, len(out), keys)
    return out


def parquet_has_columns(path: str, cols) -> bool:
    """探 parquet schema 判断 ``cols`` 是否全部存在 (不读数据列)。

    用于"列可选"读取: 避免 ``pd.read_parquet(path, columns=[...缺失列...])`` 抛
    ArrowInvalid (例如合成测试帧不含 docid)。pyarrow 不可用时保守返回 False
    (调用方据此走"不含该列"路径, 后续 ``restrict_to_verified`` 再 fail-open)。
    """
    try:
        import pyarrow.parquet as pq
        avail = set(pq.ParquetFile(path).schema.names)
        return all(c in avail for c in cols)
    except Exception:  # noqa: BLE001
        return False
