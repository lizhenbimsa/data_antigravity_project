"""验证 stage 21 LLM 缓存对当前语料的覆盖率 — 问题3 (golden 跨-run 确定性) 证明工具。

背景
----
golden snapshot 的可复现性依赖 stage 21 (LLM 双轨投票) 的确定性。stage 21
唯一的不确定性来源是 **缓存 miss → 重新调付费 API → 同一篇文章的投票可能翻转**
(实测: 某边缘文章 idx 在一次重生中 DeepSeek 单模型票 True→False, 致某仅 1 篇
有效文章的边缘银行整行掉出, panel 176→174 行漂移)。

因此确定性的充要条件是: **当前语料 × 全部启用模型 × 双轨, 在 ``_llm_cache.db``
中 0 个 miss**。本脚本即如实测量这一覆盖率, 全程 **纯缓存读, 零网络、零 API、$0**。

判定
----
- ``misses == 0``  → 当前 golden 语料完全被缓存覆盖 → golden 可在 *不调用付费
  API* 的前提下字节级确定性复现。退出码 0。
- ``misses > 0``   → 存在未覆盖的 ``(model, prompt)``; 打印前若干缺口 (model /
  row_idx / track) 供回填。退出码 2。

与 stage 21 的一致性
--------------------
prompt 构造复用 ``tone_llms.iter_article_track_prompts`` (生产同一生成器, 单一
事实源), 缓存键参数 (prompt_version / temperature / random_seed) 复用 stage 21
模块常量 → 本脚本算出的键与 stage 21 实际写入的键字节级一致。若复刻有任何偏差,
将表现为 misses>0 (键不匹配 → 全 miss), 故 ``misses==0`` 反过来也证明复刻无误。

更强的端到端证明 (输出 parquet 字节不变) 见离线确定性模式:
    NEWS_PROCESS_LLM_OFFLINE=1 python -m news_process.21_tone_llms
该模式下任一 miss 直接 raise ``LLMCacheMissError`` 中止, 保证 $0。

用法
----
    python -m news_process.scripts.audit.verify_stage21_cache_coverage
    python news_process/scripts/audit/verify_stage21_cache_coverage.py --max-show 20
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

from news_process.core.caching import LLMCache
from news_process.pipeline.sentiment import tone_llms


def _load_stage21_input() -> pd.DataFrame:
    """复刻 stage 21 main(): 读 14_fintech_intensity, idempotent 物化 content_ctx。"""
    cfg = tone_llms.CONFIG
    input_14 = cfg['filenames'].get('output_14_fintech_intensity',
                                    '14_fintech_intensity.parquet')
    path_14 = os.path.join(cfg['paths']['output_dir'], input_14)
    if not os.path.exists(path_14):
        raise SystemExit(f"[verify] stage 21 输入缺失: {path_14} — 请先跑 stage 14。")
    df = pd.read_parquet(path_14)
    # 与 main() 同款 idempotent 物化 (stage 13 上游通常已物化, 此处兜底)
    if 'content_ctx' not in df.columns:
        df = tone_llms._materialize_content_ctx(df)
    return df


def verify_cache_coverage(max_show: int = 10) -> int:
    """测量缓存覆盖率, 返回退出码 (0=全覆盖, 2=有缺口)。"""
    df = _load_stage21_input()
    models = tone_llms.MODELS
    cache_db = os.path.join(tone_llms.CONFIG['paths']['output_dir'], '_llm_cache.db')
    if not os.path.exists(cache_db):
        raise SystemExit(f"[verify] 缓存缺失: {cache_db}")

    n_rows = len(df)
    print(f"[verify] 语料: {n_rows} 行 × {len(models)} 模型 × 2 轨 "
          f"= {n_rows * len(models) * 2} 次查找")
    print(f"[verify] 缓存: {cache_db}")
    print(f"[verify] 键参数: prompt_version={tone_llms.PROMPT_VERSION!r} "
          f"temperature={tone_llms.TEMPERATURE} random_seed={tone_llms.RANDOM_SEED}")

    hits = 0
    misses = 0
    per_model_miss: dict[str, int] = {m['model_name']: 0 for m in models}
    miss_samples: list[tuple] = []

    with LLMCache(cache_db) as cache:
        for row_idx, track, prompt in tone_llms.iter_article_track_prompts(df):
            for m in models:
                model_id = m['model_name']
                resp = cache.get(
                    model_id, prompt,
                    prompt_version=tone_llms.PROMPT_VERSION,
                    temperature=tone_llms.TEMPERATURE,
                    random_seed=tone_llms.RANDOM_SEED,
                )
                if resp is None:
                    misses += 1
                    per_model_miss[model_id] += 1
                    if len(miss_samples) < max_show:
                        miss_samples.append((model_id, row_idx, track))
                else:
                    hits += 1

    total = hits + misses
    rate = hits / total if total else 0.0
    print(f"\n[verify] 结果: lookups={total} hits={hits} misses={misses} "
          f"hit_rate={rate:.6f}")
    for mid, mc in per_model_miss.items():
        print(f"[verify]   {mid}: misses={mc}")

    if misses == 0:
        print("\n[verify] ✅ 0 miss — golden 语料完全被缓存覆盖, stage 21 可 $0 "
              "确定性复现 (缓存即确定性锚点, 勿删 _llm_cache.db)。")
        return 0

    print(f"\n[verify] ❌ {misses} 个 miss — golden 无法在不调 API 下确定性复现。"
          f" 前 {len(miss_samples)} 个缺口 (model, row_idx, track):")
    for s in miss_samples:
        print(f"[verify]     {s}")
    print("[verify] 修复: 在线跑一次 stage 21 回填缓存, 或检查语料/prompt_version 漂移。")
    return 2


def main() -> None:
    ap = argparse.ArgumentParser(description="验证 stage 21 LLM 缓存覆盖率 (问题3 确定性)")
    ap.add_argument('--max-show', type=int, default=10,
                    help="最多打印多少个 miss 样本 (默认 10)")
    args = ap.parse_args()
    sys.exit(verify_cache_coverage(max_show=args.max_show))


if __name__ == '__main__':
    main()
