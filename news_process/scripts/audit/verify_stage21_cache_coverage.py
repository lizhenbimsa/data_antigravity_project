"""验证 stage 21 LLM 缓存对当前语料的覆盖率 — 问题3 (golden 跨-run 确定性) 证明工具。

背景
----
golden snapshot 的可复现性依赖 stage 21 (LLM 双轨投票) 的确定性。stage 21
唯一的不确定性来源是 **缓存 miss → 重新调付费 API → 同一篇文章的投票可能翻转**
(实测: 某边缘文章 idx 在一次重生中 DeepSeek 单模型票 True→False, 致某仅 1 篇
有效文章的边缘银行整行掉出, panel 176→174 行漂移)。

因此确定性的充要条件是: **当前语料 × 全部启用模型 × 三轨 (full/ctx/ss), 在 ``_llm_cache.db``
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

白话
----
LLM 打分结果都存在本地缓存数据库里。只要"每篇文章 × 每个模型 × 每条轨"都能在
缓存里查到, 重跑 stage 21 就一分钱不花、结果和上次一模一样。本脚本就是挨个查
一遍缓存: 全查到 → 放心; 有查不到的 → 重跑会调付费 API, 结果可能变, 先回填缓存。
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

from news_process.core.caching import LLMCache
from news_process.pipeline.sentiment import tone_llms


def _load_stage21_input(input_path: str | None = None) -> tuple[pd.DataFrame, str]:
    """复刻 stage 21 main(): 读 15_fintech_intensity, idempotent 物化 content_ctx。

    fix(2026-06-14 审计 DET-1): 支持 ``input_path`` 覆盖 — 缺省读配置的盘面
    15_fintech_intensity (在裸机上即 T=2 试跑帧), 生产端须传全量 18.2M 语料帧
    以使覆盖率证明对生产规模有效。返回 (df, 实际路径)。
    """
    cfg = tone_llms.CONFIG
    if input_path is None:
        input_14 = cfg['filenames'].get('output_14_fintech_intensity',
                                        '15_fintech_intensity.parquet')
        input_path = os.path.join(cfg['paths']['output_dir'], input_14)
    if not os.path.exists(input_path):
        raise SystemExit(
            f"[verify] stage 21 输入缺失: {input_path} — 请先跑 stage 14, "
            f"或用 --input 指定全量语料帧。")
    df = pd.read_parquet(input_path)
    # 与 main() 同款 idempotent 物化 (stage 13 上游通常已物化, 此处兜底)
    if 'content_ctx' not in df.columns:
        df = tone_llms._materialize_content_ctx(df)
    return df, input_path


def verify_cache_coverage(max_show: int = 10, input_path: str | None = None,
                          min_rows: int = 0) -> int:
    """测量缓存覆盖率, 返回退出码。

    退出码: 0=全覆盖且帧达生产门槛; 2=有缺口; 3=零 miss 但帧行数 < ``min_rows``
    (覆盖率证明仅对该 *子生产* 帧有效, 不足以 bless 全量 golden — DET-1)。

    fix(2026-06-14 审计 DET-1): 新增 ``input_path`` (指定语料帧) 与 ``min_rows``
    (生产规模门槛)。原实现对盘面任意帧报绝对命中, 在 T=2 试跑帧上恒打印
    7020/7020 PASS, 即便 18.2M 生产帧未覆盖 → 确定性证明在生产规模上空洞。
    现要求显式传全量帧并以 ``min_rows`` 把关。
    """
    df, input_path = _load_stage21_input(input_path)
    models = tone_llms.MODELS
    cache_db = os.path.join(tone_llms.CONFIG['paths']['output_dir'], '_llm_cache.db')
    if not os.path.exists(cache_db):
        raise SystemExit(f"[verify] 缓存缺失: {cache_db}")

    n_rows = len(df)
    print(f"[verify] 输入帧: {input_path}")
    print(f"[verify] 语料: {n_rows} 行 × {len(models)} 模型 × 3 轨 (full/ctx/ss) "
          f"= {n_rows * len(models) * 3} 次查找")
    if min_rows > 0 and n_rows < min_rows:
        print(f"[verify] ⚠ 帧行数 {n_rows:,} < 生产门槛 --min-rows={min_rows:,} — "
              f"覆盖率证明仅对此 *子生产* 帧有效, 不足以 bless 全量 T=19 golden。")
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
        if min_rows > 0 and n_rows < min_rows:
            print(f"\n[verify] ⚠ 0 miss 但帧行数 {n_rows:,} < --min-rows={min_rows:,} — "
                  "覆盖率证明仅对该子生产帧有效, **不足以** 在 $0 下确定性复现全量 T=19 "
                  "golden。请对全量 18.2M 语料帧重跑本检查 (--input <全量 15_fintech_intensity>)。")
            return 3
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
    ap.add_argument('--input', type=str, default=None,
                    help="指定语料帧 parquet (缺省=配置的 15_fintech_intensity; "
                         "生产端须传全量 18.2M 语料帧, DET-1)")
    ap.add_argument('--min-rows', type=int, default=0,
                    help="生产规模门槛: 帧行数 < 此值时, 即便 0 miss 也判退出码 3 "
                         "(覆盖率证明不足以 bless 全量 golden, DET-1)")
    args = ap.parse_args()
    sys.exit(verify_cache_coverage(max_show=args.max_show, input_path=args.input,
                                   min_rows=args.min_rows))


if __name__ == '__main__':
    main()
