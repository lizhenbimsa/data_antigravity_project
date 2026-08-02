"""定向回填 stage 21 LLM 缓存缺口 — 让 ``NEWS_PROCESS_LLM_OFFLINE=1`` 离线复现重新可达。

背景
----
stage 21 在离线确定性模式下, 缓存 miss 会在 ``tone_llms.fetch_llm_async`` 直接
``raise LLMCacheMissError`` 并一路冒泡到进程顶层 —— **是崩溃不是降级** (见
``scripts/audit/STAGE21_LOG_DEFECT_AUDIT_AND_REMEDIATION_PLAN_2026-07-25.md`` D1
的调用链终验)。缺口的成因是**弃票不入缓存**: 200 响应为空 / 不可解析 / 缺
``is_bank_fintech_news`` 键时按可重试瞬时失败处理, 重试耗尽后返回 ``None`` 而
**绝不 ``cache.put``** (该闸门是承重设计, 本脚本零妥协、不触碰)。结果是这些
(model, prompt) 格永久缺条目, 下一跑离线必崩。

本脚本做且只做一件事: **把缺口格逐个在线重取一次, 好响应写回主缓存**。

为什么不直接"在线跑一次 stage 21"
--------------------------------
在线模式会额外启用**平局重试** (``sentiment_tie_retry_rounds``), 它以
``force_refresh=True`` 绕缓存重调并以 ``INSERT OR REPLACE`` **覆写既有条目** →
少数边界篇的投票可在两跑间翻转 (D1-3/D2 机理)。为回填 0.005% 的缺口而让
99.99% 已冻结的确定性锚点面临覆写风险, 代价不成比例。本脚本只碰 miss 格,
**一条既有缓存条目都不覆写** (miss 格按定义在库中不存在)。

与生产的一致性
--------------
- prompt 构造复用 ``tone_llms.iter_article_track_prompts`` (与生产、与
  ``verify_stage21_cache_coverage.py`` 同一事实源) → 缓存键字节级一致。
- 实际请求复用 ``tone_llms.fetch_llm_async`` 本体 → 归档 (``llm_archive``) →
  ``_is_cacheable_llm_response`` 闸门 → ``cache.put`` 的整条写入路径与生产逐字
  相同, 不存在"回填出来的条目与生产写的不同款"的可能。
- 缓存键四维 (model_id + prompt + prompt_version + temperature) 全部取自
  ``tone_llms`` 模块常量, 不在本脚本重新定义。

``--max-retries`` 为何默认 5 而非生产的 80
------------------------------------------
缺口的主体成因是「模型稳定返空」这一**确定性**失败 (D5: 264/267 弃票为
gemini31, 其中 263 次原因即 200 空响应), 对它重试 80 次 × 10s ≈ 800s/格 是纯
空转。重试次数**不进缓存键**, 故调小它对写入内容零影响, 只影响墙钟。若某格
确因瞬时网络故障而失败, 重跑本脚本即可 (幂等: 已命中的格自动跳过)。

用法
----
    # ① 只看缺口, 零网络零成本 (默认)
    python -m news_process.scripts.audit.backfill_stage21_cache_misses

    # ② 真回填 (在线, 付费; 仅对缺口格调 API)
    python -m news_process.scripts.audit.backfill_stage21_cache_misses --execute

    # ③ 回填后复验
    python -m news_process.scripts.audit.verify_stage21_cache_coverage

退出码: 0=无缺口 (或回填后已补齐); 2=仍有缺口; 3=dry-run 探到缺口 (未回填)。

白话
----
LLM 打分结果存在本地"账本"里, 重跑时查得到就不用花钱、结果也永远一样。上次跑
的时候有 120 个格子模型死活没给出合格答案, 按设计这种坏答案不许进账本, 于是账
本就永久缺了这 120 格; 下次开"只准查账本、不准花钱"的离线模式一跑, 一查不到就
直接崩。本脚本就是专门把这 120 格重新问一遍、把合格答案补进账本, 别的格子一个
都不动。
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

import aiohttp
import pandas as pd

from news_process.core.caching import LLMCache
from news_process.pipeline.sentiment import tone_llms

# 回填并发上限 — 缺口量级为百, 无需生产的 250/500; 保守取值避免触发网关限流,
# 且让失败日志可读。可经 --concurrency 覆盖。
_DEFAULT_CONCURRENCY = 16
# 见模块 docstring「--max-retries 为何默认 5」。
_DEFAULT_MAX_RETRIES = 5


def _load_stage21_input(input_path: str | None = None) -> tuple[pd.DataFrame, str]:
    """读 stage 21 输入帧 — 与 verify_stage21_cache_coverage 同款 (含 ctx 兜底物化)。"""
    cfg = tone_llms.CONFIG
    if input_path is None:
        input_15 = cfg['filenames'].get('output_14_fintech_intensity',
                                        '15_fintech_intensity.parquet')
        input_path = os.path.join(cfg['paths']['output_dir'], input_15)
    if not os.path.exists(input_path):
        raise SystemExit(
            f"[backfill] stage 21 输入缺失: {input_path} — 请先跑 stage 15, "
            f"或用 --input 指定语料帧。")
    df = pd.read_parquet(input_path)
    if 'content_ctx' not in df.columns:
        df = tone_llms._materialize_content_ctx(df)
    return df, input_path


def _subset_rows(df: pd.DataFrame, rows: list[int] | None) -> pd.DataFrame:
    """按 row_idx 白名单裁剪语料帧 — 定向重试用。

    全量扫描要遍历 242,000 × 3 轨 × 3 模型 = 218 万次缓存查找 (约 25 分钟)。
    对「首轮回填后只剩个位数格待重试」的场景, 逐次全量扫描是纯浪费。本函数按
    ``df.index`` 取子集, 使 ``iter_article_track_prompts`` 只对目标行构造 prompt
    —— prompt 内容只依赖行自身字段, 与是否被裁剪无关, 故缓存键**逐字节不变**。
    """
    if not rows:
        return df
    missing = [r for r in rows if r not in df.index]
    if missing:
        raise SystemExit(f"[backfill] --rows 指定的行不在语料帧中: {missing}")
    return df.loc[rows]


def _scan_misses(df: pd.DataFrame, cache: LLMCache,
                 include_registered: bool = False) -> tuple[list[tuple], list[tuple]]:
    """扫描当前语料 × 全部模型 × 三轨的缓存缺口。

    Args:
        include_registered: 是否把已登记为**永久弃票**的格也当作待回填 (默认否)。
            这些格模型已证实拒绝出票, 重试是纯空转 (实测 gemini 单格 30 次要空转
            6.6 分钟), 且离线路径已能按缺票放行, 无需回填。置 True 只在怀疑模型侧
            已修复 (换网关 / 换模型版本) 时用于复查。

    Returns:
        (todo, registered):
        · todo       — list of (model_cfg, row_idx, track, prompt), 待回填;
        · registered — list of (model_id, row_idx, track, failure_kind), 已登记弃票。
        顺序稳定 (行 → 轨 → 模型), 与 ``iter_article_track_prompts`` 遍历序一致。
    """
    todo: list[tuple] = []
    registered: list[tuple] = []
    for row_idx, track, prompt in tone_llms.iter_article_track_prompts(df):
        for m in tone_llms.MODELS:
            key_kw = dict(prompt_version=tone_llms.PROMPT_VERSION,
                          temperature=tone_llms.TEMPERATURE,
                          random_seed=tone_llms.RANDOM_SEED)
            if cache.get(m['model_name'], prompt, **key_kw) is not None:
                continue
            dropped = cache.get_dropped_vote(m['model_name'], prompt, **key_kw)
            if dropped is not None:
                registered.append(
                    (m['model_name'], row_idx, track, dropped['failure_kind']))
                if not include_registered:
                    continue
            todo.append((m, row_idx, track, prompt))
    return todo, registered


async def _backfill_async(misses: list[tuple], cache: LLMCache,
                          concurrency: int, max_retries: int) -> dict:
    """对缺口格逐个走生产同源的 fetch_llm_async 重取, 好响应由其内部写回缓存。

    Returns:
        dict: {(model_id, row_idx, track): bool}  True=本次拿到可缓存响应。
    """
    semaphore = asyncio.Semaphore(concurrency)
    connector = tone_llms.build_llm_connector(concurrency)
    pacers = tone_llms.build_model_pacers(
        tone_llms.MODELS, tone_llms.LLM_CONFIG.get('request_spacing_seconds', 0.0))
    availability = tone_llms.AsyncModelAvailability()

    outcomes: dict = {}
    async with aiohttp.ClientSession(connector=connector,
                                     timeout=tone_llms.build_llm_timeout()) as session:
        # preflight 探活: 与生产在线路径一致, 提前发现鉴权/模型不可用 (迁移
        # OpenLux 后尤其值得先探, 免得 120 格各自空转 max_retries 次)。
        await tone_llms.preflight_model_availability(session, tone_llms.MODELS, availability)

        tasks = [
            tone_llms.fetch_llm_async(
                session, semaphore, prompt, m, row_idx, track, cache=cache,
                request_pacer=pacers.get(m['model_name']),
                model_availability=availability,
                max_retries=max_retries,
                prompt_version=tone_llms.PROMPT_VERSION,
            )
            for (m, row_idx, track, prompt) in misses
        ]
        total = len(tasks)
        done = 0
        print(f"[backfill] 📡 开始回填 {total} 个缺口格 "
              f"(并发={concurrency}, max_retries={max_retries})")
        for coro in asyncio.as_completed(tasks):
            row_idx, model_id, res_text, track = await coro
            outcomes[(model_id, row_idx, track)] = res_text is not None
            done += 1
            if done % max(1, total // 10) == 0 or done == total:
                ok = sum(1 for v in outcomes.values() if v)
                print(f"[backfill]   进度 {done}/{total} — 已取得响应 {ok}")
    return outcomes


def backfill(execute: bool = False, input_path: str | None = None,
             concurrency: int = _DEFAULT_CONCURRENCY,
             max_retries: int = _DEFAULT_MAX_RETRIES,
             max_show: int = 200, rows: list[int] | None = None,
             retry_registered: bool = False) -> int:
    """扫描缺口 → (可选) 在线回填 → 复验。返回退出码。"""
    if execute and tone_llms.LLM_OFFLINE:
        raise SystemExit(
            "[backfill] ❌ 拒绝执行: NEWS_PROCESS_LLM_OFFLINE 已开启, 而回填必须在线。"
            " 请在**未设**该变量的 shell 中重跑 --execute。")

    df, input_path = _load_stage21_input(input_path)
    df = _subset_rows(df, rows)
    cache_db = os.path.join(tone_llms.CONFIG['paths']['output_dir'], '_llm_cache.db')
    if not os.path.exists(cache_db):
        raise SystemExit(f"[backfill] 缓存缺失: {cache_db}")

    print(f"[backfill] 输入帧: {input_path}")
    if rows:
        print(f"[backfill] ⚠ --rows 定向模式: 只扫描 {len(rows)} 个指定行 "
              f"(缓存键与全量扫描逐字节一致; 但本次**不构成**全语料覆盖率证明)")
    print(f"[backfill] 语料: {len(df):,d} 行 × {len(tone_llms.MODELS)} 模型 × 3 轨")
    print(f"[backfill] 缓存: {cache_db}")
    print(f"[backfill] 键参数: prompt_version={tone_llms.PROMPT_VERSION!r} "
          f"temperature={tone_llms.TEMPERATURE} random_seed={tone_llms.RANDOM_SEED}")
    print(f"[backfill] 模式: {'EXECUTE (在线, 付费)' if execute else 'DRY-RUN (零网络, $0)'}")

    with LLMCache(cache_db) as cache:
        misses, registered = _scan_misses(df, cache,
                                          include_registered=retry_registered)
        n_miss = len(misses)
        print(f"\n[backfill] 扫描完成: {n_miss} 个待回填缺口格")
        if registered:
            print(f"[backfill] ℹ 另有 {len(registered)} 格已登记为**永久弃票** "
                  f"({'本次一并重试' if retry_registered else '已跳过'}; 模型侧永久拒绝出票, "
                  f"离线复现按缺票放行, 不阻塞):")
            for s in registered[:max_show]:
                print(f"[backfill]     {s}")
        if n_miss == 0:
            print("[backfill] ✅ 无待回填缺口 — stage 21 已可 "
                  "NEWS_PROCESS_LLM_OFFLINE=1 离线 $0 复现。")
            return 0

        per_model: dict[str, int] = {}
        for (m, _row, _track, _p) in misses:
            per_model[m['model_name']] = per_model.get(m['model_name'], 0) + 1
        for mid, cnt in sorted(per_model.items(), key=lambda kv: -kv[1]):
            print(f"[backfill]   {mid}: {cnt}")
        print(f"[backfill] 前 {min(max_show, n_miss)} 个缺口 (model, row_idx, track):")
        for (m, row_idx, track, _p) in misses[:max_show]:
            print(f"[backfill]     ({m['model_name']!r}, {row_idx}, {track!r})")

        if not execute:
            print("\n[backfill] ⏸ DRY-RUN 结束 — 未调用任何 API, 未写入任何条目。"
                  " 确认无误后加 --execute 真回填。")
            return 3

        # 返回值仅用于进度显示; 是否补齐一律以下方重查缓存为准 (库里有没有才是判据)。
        asyncio.run(_backfill_async(misses, cache, concurrency, max_retries))

        # 复验: 直接重查缓存 (而非信 fetch 的返回值) — 唯一可信判据是"库里有没有"。
        # 仍缺的格再分两类: 已被 fetch_llm_async 自动登记为永久弃票 (可接受, 离线
        # 会按缺票放行) vs 真仍缺 (瞬时故障未登记, 下次离线仍会 hard-fail)。
        newly_registered: list[tuple] = []
        still: list[tuple] = []
        for (m, row_idx, track, prompt) in misses:
            key_kw = dict(prompt_version=tone_llms.PROMPT_VERSION,
                          temperature=tone_llms.TEMPERATURE,
                          random_seed=tone_llms.RANDOM_SEED)
            if cache.get(m['model_name'], prompt, **key_kw) is not None:
                continue
            dropped = cache.get_dropped_vote(m['model_name'], prompt, **key_kw)
            if dropped is not None:
                newly_registered.append(
                    (m['model_name'], row_idx, track, dropped['failure_kind']))
            else:
                still.append((m['model_name'], row_idx, track))

    filled = n_miss - len(newly_registered) - len(still)
    print(f"\n[backfill] 回填结果: {filled}/{n_miss} 已写入缓存; "
          f"登记为永久弃票 {len(newly_registered)}; 真仍缺 {len(still)}")
    if newly_registered:
        print("[backfill] ℹ 以下格已登记为**永久弃票** (模型侧拒绝出票, 重试无解; "
              "离线复现将按缺票放行, 与在线路径行为一致 — 不阻塞):")
        for s in newly_registered[:max_show]:
            print(f"[backfill]     {s}")
    if still:
        print("[backfill] ❌ 真仍缺的格 (失败型判为**瞬时**故障, 未登记 — 下次离线跑"
              "仍会 hard-fail):")
        for s in still[:max_show]:
            print(f"[backfill]     {s}")
        print("[backfill] 后续: 排查网络/限流后重跑本脚本 (幂等, 已命中的格自动跳过)。")
        return 2

    print("[backfill] ✅ 无真缺口 — stage 21 可重新 NEWS_PROCESS_LLM_OFFLINE=1 "
          "离线 $0 复现。建议再跑 verify_stage21_cache_coverage 独立复核。")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(
        description="定向回填 stage 21 LLM 缓存缺口 (只碰 miss 格, 不覆写任何既有条目)")
    ap.add_argument('--execute', action='store_true',
                    help="真调 API 回填 (在线, 付费); 缺省为 dry-run 只扫描")
    ap.add_argument('--input', type=str, default=None,
                    help="指定语料帧 parquet (缺省=配置的 15_fintech_intensity)")
    ap.add_argument('--concurrency', type=int, default=_DEFAULT_CONCURRENCY,
                    help=f"回填并发 (默认 {_DEFAULT_CONCURRENCY})")
    ap.add_argument('--max-retries', type=int, default=_DEFAULT_MAX_RETRIES,
                    help=f"单格重试上限 (默认 {_DEFAULT_MAX_RETRIES}; 见 docstring 说明, "
                         f"不进缓存键故对写入内容零影响)")
    ap.add_argument('--max-show', type=int, default=200,
                    help="最多打印多少个缺口 (默认 200)")
    ap.add_argument('--rows', type=str, default=None,
                    help="只处理指定 row_idx (逗号分隔), 跳过 218 万次全量扫描 — "
                         "首轮回填后定向重试个别顽固格用。⚠ 定向模式下的 0 miss "
                         "**不**构成全语料覆盖率证明, 收尾须跑 verify_stage21_cache_coverage。")
    ap.add_argument('--retry-registered', action='store_true',
                    help="连已登记为永久弃票的格也重试 (默认跳过)。仅在模型侧可能已"
                         "修复时用 (换网关/换模型版本); 否则是纯空转。")
    args = ap.parse_args()
    rows = [int(x) for x in args.rows.split(',') if x.strip()] if args.rows else None
    sys.exit(backfill(execute=args.execute, input_path=args.input,
                      concurrency=args.concurrency, max_retries=args.max_retries,
                      max_show=args.max_show, rows=rows,
                      retry_registered=args.retry_registered))


if __name__ == '__main__':
    main()
