"""news_process.pipeline.sentiment.executive_ner — stage 19 LLM CEO NER.

v3.7.0 PR #13 (D4) — 用 yunwu LLM zero-shot 抽取银行高管 (CEO / 董事长 /
总裁 / 行长) 提及, panel 新增高管聚焦度指标.

学术依据
--------
Kaustia, M., & Rantapuska, E. (2016). Does mood affect trading behavior?
Journal of Financial Markets, 29, 1-26.
→ CEO 媒体提及与 CEO 个人声誉、股价的关联

Bushee, B. J., Gow, I. D., & Taylor, D. J. (2018). Linguistic complexity
in firm disclosures: Obfuscation or information? Journal of Accounting
Research, 56(1), 85-121.
→ NER 抽 firm-level vs CEO-level disclosure

Malmendier, U., & Tate, G. (2009). Superstar CEOs. Quarterly Journal of
Economics, 124(4), 1593-1638.

设计
----
1. zero-shot prompt: 复用 stage 21 LLM client (yunwu) + 缓存层
2. DC3 LLM archive 接入 (v3.7.0 顶刊 reproducibility 硬约束)
3. 双轨: content_full + content_ctx 各跑一次
4. 输出 article-level: n_ceo_mentions, n_unique_execs, exec_hhi
5. bank-year 聚合

成本估算
--------
~$6-12 yunwu API (400k × 0.3K tokens × $0.5/1M, 100% miss 估算).
$15 预算上限 (v2.3 G-D4.1 准入门控).

DC3 LLM archive 接入
-------------------
每次 LLM 调用通过 ``archive_record(...)`` 写入 append-only JSONL +
SHA-256 manifest, 即使 GPT-5.4→5.5 升级仍可复现 (v3.7.0 V4 F-P2.1
critical 修复).

panel 新增列
-----------
``n_ceo_mentions_{full,ctx}``       高管提及总次数 (bank-year = 篇级总次数的 mean)
``n_unique_execs_{full,ctx}``       去重高管数 (bank-year = 篇级 distinct 数的 mean)
``exec_hhi_{full,ctx}``             mention 在 executives 上的 HHI (聚焦度)

⚠ 诚实度声明 (口径限制):
  1. **无跨银行 / 跨文章高管去歧义** (no cross-bank disambiguation): 每篇文章
     的高管名单由 LLM 独立抽取, 同名高管在不同银行 / 不同文章间不做实体对齐;
     ``n_unique_execs`` 是 *篇内* distinct 名字数, 不是 bank-year 池化后的真实
     去重高管数。重名 / 别名 / 简称在文章间会被重复计数。
  2. **bank-year HHI 是 mean(篇级 HHI), 非加权 pooled HHI** (mean-of-per-article
     HHI, NOT a mention-weighted pooled HHI): 聚合在 ``main()`` 用 ``'mean'``
     对篇级 ``exec_hhi`` 取等权简单平均 (每篇文章权重相同, 与文章篇幅 / 提及
     次数无关), 而非把所有文章的提及汇总到 bank-year 后再算单一 HHI。两者在
     文章数不均或单篇主导时会显著不同; 任何"该银行年度高管聚焦度"的解读须
     按此等权 mean-of-fractions 口径理解。

stub 说明
---------
本模块代码完整, 实际跑需要:
    1. yunwu YUNWU_API_KEY 配置 (现有 stage 21 已用)
    2. ~$12 预算 + 12-24 h wall clock
    3. 200 篇人工 gold standard 标注 → precision ≥ 0.85, recall ≥ 0.75
"""

from __future__ import annotations

import json
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

CONFIG = load_config()
STAGE_NAME = "19_executive_ner"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# P-006 修复 (v3.7.1): LLMCache API 对齐 — 使用与 stage 21 / benefit_society
# / policy_alignment 同款 db_path 模式 (不是 namespace=...).
CACHE_DB_PATH = CONFIG['paths'].get(
    'llm_cache_db',
    os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db'),
)

# P-022 修复 (v3.7.1): retry/backoff 参数 (从 sentiment.yaml::executive_ner 读取).
_NER_CONFIG = CONFIG.get('executive_ner', {})
MAX_RETRIES = int(_NER_CONFIG.get('max_retries', 5))
TIMEOUT_PER_REQUEST = int(_NER_CONFIG.get('timeout_per_request', 60))
RETRY_DELAY = 2.0       # 起始 sleep 秒
RETRY_BACKOFF_CAP = 60  # 单次 sleep 上限

PROMPT_VERSION = 'd4_v0_20260518'  # 与 prompt 内容绑定; 改 PROMPT_TEMPLATE 必须 bump

# v3.7.0 V4 P2.1: DC3 LLM archive 接入
try:
    from news_process.pipeline.llm_archive.archive import archive_record  # noqa: E402
    HAS_ARCHIVE = True
except ImportError:
    logger.warning("  pipeline.llm_archive 未就绪 (v3.7.0 PR DC3); D4 archive 跳过")
    HAS_ARCHIVE = False
    archive_record = None  # type: ignore


PROMPT_TEMPLATE = """请从以下中文银行 / 金融科技新闻文章中识别提到的银行高管姓名。
关注职位: CEO / 董事长 / 总裁 / 行长 / 副行长 / 副总裁 / 首席执行官 / 首席风险官 / 首席信息官。

仅返回 JSON 数组, 格式如下 (无任何额外文字):
[
  {{"name": "姓名", "title": "职位", "mention_count": 提及次数}},
  ...
]

若无任何高管提及, 返回空数组 [].

文章 (银行: {bank_name}):
{content}

JSON 输出:"""


def _yunwu_chat_sync(
    prompt: str,
    model: str,
    *,
    timeout: int = TIMEOUT_PER_REQUEST,
    max_retries: int = MAX_RETRIES,
) -> tuple[str, dict]:
    """同步 yunwu API 调用 (与 tone_llms._build_llm_request 同源 schema).

    Yunwu 兼容 OpenAI Chat Completions API.

    P-022 修复 (v3.7.1): 加 retry + 指数退避; 旧版单次 POST 任何 429/5xx
    都静默 return '' → 系统性 NER 数据丢失. 现在 max_retries 内重试,
    最终失败才返空.

    Returns:
        (content, meta): content 是 message content (空串=失败); meta 含
        ``http_status`` / ``model_version`` / ``api_endpoint`` / ``response_raw``
        / ``attempts`` 供 archive_record 调用 (P-007).
    """
    meta = {
        'http_status': 0, 'model_version': model,
        'api_endpoint': '', 'response_raw': '', 'attempts': 0,
    }
    try:
        import requests  # noqa: E402 (lazy import 避免 light test 拉重依赖)
    except ImportError:
        logger.error("requests 未装; D4 LLM 调用失败")
        return '', meta

    api_key = os.environ.get('YUNWU_API_KEY', '')
    if not api_key:
        logger.warning("YUNWU_API_KEY 环境变量未设置; D4 跳过 LLM 调用")
        return '', meta
    base_url = os.environ.get('YUNWU_BASE_URL', 'https://yunwu.ai/v1')
    endpoint = f'{base_url}/chat/completions'
    meta['api_endpoint'] = endpoint

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.0,  # NER 任务 deterministic
        'seed': 42,
        'response_format': {'type': 'json_object'},
    }
    delay = RETRY_DELAY
    for attempt in range(max_retries):
        meta['attempts'] = attempt + 1
        try:
            resp = requests.post(endpoint, headers=headers, json=payload,
                                 timeout=timeout)
            meta['http_status'] = resp.status_code
            if resp.status_code == 200:
                try:
                    data = resp.json()
                except Exception:
                    data = {}
                meta['response_raw'] = resp.text
                meta['model_version'] = data.get('model', model)
                try:
                    return data['choices'][0]['message']['content'] or '', meta
                except (KeyError, IndexError, TypeError):
                    return '', meta
            if resp.status_code in (429, 500, 502, 503, 504):
                if attempt < max_retries - 1:
                    logger.warning(
                        f"  LLM HTTP {resp.status_code} attempt "
                        f"{attempt + 1}/{max_retries}, sleep {delay:.1f}s"
                    )
                    time.sleep(delay)
                    delay = min(delay * 2, RETRY_BACKOFF_CAP)
                    continue
            # 非 retry 类 4xx (e.g. 400/401/404) 立即放弃
            logger.warning(f"  LLM HTTP {resp.status_code} (non-retry); abort")
            meta['response_raw'] = resp.text[:500]
            return '', meta
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"  LLM RequestException {type(e).__name__} attempt "
                    f"{attempt + 1}/{max_retries}, sleep {delay:.1f}s"
                )
                time.sleep(delay)
                delay = min(delay * 2, RETRY_BACKOFF_CAP)
                continue
            logger.warning(f"  LLM 重试耗尽: {type(e).__name__}: {str(e)[:120]}")
            return '', meta
        except Exception as e:
            logger.warning(f"  LLM unexpected: {type(e).__name__}: {str(e)[:120]}")
            return '', meta
    return '', meta


def call_llm_for_ner(
    content: str,
    bank_name: str,
    *,
    model: str = 'gpt-5.4-nano',
    cache_namespace: str = 'd4_ceo_ner',
    return_status: bool = False,
    cache=None,
):
    """zero-shot LLM NER call; 缓存 by (model, content hash, namespace).

    Args:
        content: 文章正文.
        bank_name: target_bank (供 prompt context).
        model: yunwu 模型 ID.
        cache_namespace: cache key 前缀 (与 stage 21 ``''`` 隔离).

    Returns:
        list of {name, title, mention_count}; 空列表表示无高管提及.

    Note:
        v3.7.0 DC3 archive 自动接入: 每次调用 archive_record(...)
        失败不阻塞 (try/except), 与 tone_llms.py 同款.
    """
    # audit-fixes 2026-05-29 (M4): return_status=True 时返回 (execs, call_failed);
    # call_failed 仅在 LLM 调用真失败 (空响应/无 key/重试耗尽) 时为 True, 与
    # "确无高管" (有响应但 execs 为空) 区分, 供 main() 把失败行置 NaN 而非 0,
    # 并在失败率过高时 abort, 避免静默产出全零面板。默认 False → 返回 list
    # (向后兼容既有调用方/测试)。
    def _ret(execs, call_failed):
        return (execs, call_failed) if return_status else execs

    if not content or not content.strip():
        return _ret([], False)  # 空输入 — 非调用失败

    prompt = PROMPT_TEMPLATE.format(
        bank_name=bank_name or '未知银行',
        content=content[:2000],  # 截断防超 token limit
    )

    # P-006 修复 (v3.7.1): LLMCache 真 API 是 `LLMCache(db_path)` 不是
    # `LLMCache(namespace=)`; cache.get/put 也是 (model_id, prompt, prompt_version=)
    # 不是单参版本. 旧实现 TypeError 被宽 except 吞掉 → 永不命中 cache.
    # 现在使用与 tone_llms / benefit_society / policy_alignment 一致的 API.
    # P-007 修复 (v3.7.1): archive_record 真签名是 keyword-only
    # (cache_key, model_id, model_version, prompt, response_raw, prompt_version,
    #  temperature, api_endpoint, http_status, ...) — 不是 (stage=, model=, response=, metadata=).
    raw = ''
    meta: dict = {
        'http_status': 0, 'model_version': model,
        'api_endpoint': '', 'response_raw': '', 'attempts': 0,
    }
    cache_obj = None
    cache_key = ''
    try:
        from news_process.core.caching import LLMCache  # noqa: E402
        # audit S11 修复 (2026-05-30): 优先复用调用方传入的共享 cache; 仅在未传入
        # 时 (向后兼容既有调用方/测试) 本地新建。main() 现传入单一共享 cache, 消除
        # 此前每篇文章 ×双轨 = 2N 次新建 SQLite 连接 (production 40 万规模 = 80 万次
        # 开关 + WAL 句柄, Windows 易触句柄上限) 的连接 churn。
        cache_obj = cache if cache is not None else LLMCache(CACHE_DB_PATH)
        cache_key = LLMCache.make_key(
            model, prompt, prompt_version=PROMPT_VERSION, temperature=0.0,
        )
        cached = cache_obj.get(
            model, prompt, prompt_version=PROMPT_VERSION, temperature=0.0,
        )
        if cached is not None:
            raw = cached
            meta['http_status'] = 200
            meta['response_raw'] = cached
    except ImportError:
        # core.caching 不可用 → 直调 (无缓存)
        pass
    except Exception as e:
        logger.warning(f"  LLM cache layer fail: {type(e).__name__}: {e}; "
                       "fallback to direct call")
        cache_obj = None

    cache_hit = bool(raw)
    if not raw:
        raw, meta = _yunwu_chat_sync(prompt, model)
        if raw and cache_obj is not None:
            try:
                cache_obj.put(
                    model, prompt, raw,
                    prompt_version=PROMPT_VERSION, temperature=0.0,
                )
            except Exception as e:
                logger.debug(f"  LLM cache put fail: {e}")

    # DC3 archive (v3.7.0 reproducibility 硬约束) — P-007 修复: 正确 kwargs
    # + cache-hit 也归档 (P-045-relevant), 让 archive 真正成为 source of truth.
    if HAS_ARCHIVE and archive_record and raw:
        try:
            if not cache_key:
                # cache 路径不可用时仍生成 key (与 tone_llms.py 一致)
                from news_process.core.caching import LLMCache  # noqa: E402
                cache_key = LLMCache.make_key(
                    model, prompt, prompt_version=PROMPT_VERSION, temperature=0.0,
                )
            archive_record(
                cache_key=cache_key,
                model_id=model,
                model_version=meta.get('model_version') or model,
                prompt=prompt,
                response_raw=meta.get('response_raw') or raw,
                prompt_version=PROMPT_VERSION,
                temperature=0.0,
                api_endpoint=meta.get('api_endpoint', ''),
                http_status=meta.get('http_status') or (200 if cache_hit else 0),
            )
        except Exception as e:
            logger.debug(f"  archive_record fail: {type(e).__name__}: {e}")

    # JSON 解析鲁棒
    # audit-fixes 2026-05-29 (M4): 空 raw = LLM 调用失败 (无响应/无 key/重试
    # 耗尽) → call_failed=True; 有响应但解析为空 = 确无高管 → call_failed=False.
    call_failed = not raw
    if not raw:
        return _ret([], call_failed)
    try:
        execs = json.loads(raw)
        # 兼容两种返回: list of dict 直接 / {"executives": [...]}
        if isinstance(execs, dict):
            for k in ('executives', 'result', 'data', 'items'):
                if k in execs and isinstance(execs[k], list):
                    execs = execs[k]
                    break
            else:
                # dict 但无嵌套 list, 尝试取 values
                execs = [v for v in execs.values() if isinstance(v, list)]
                if execs:
                    execs = execs[0]
                else:
                    return _ret([], call_failed)
        if not isinstance(execs, list):
            return _ret([], call_failed)
        return _ret([e for e in execs if isinstance(e, dict) and 'name' in e], call_failed)
    except (json.JSONDecodeError, TypeError, KeyError):
        return _ret([], call_failed)


def extract_ner_features(execs: list[dict]) -> dict[str, float]:
    """从 LLM NER 输出抽取 panel 列指标.

    Returns:
        {'n_ceo_mentions': int, 'n_unique_execs': int, 'exec_hhi': float}.
    """
    if not execs:
        return {
            'n_ceo_mentions': 0,
            'n_unique_execs': 0,
            'exec_hhi': float('nan'),
        }
    counts = [int(e.get('mention_count', 1) or 1) for e in execs]
    total = sum(counts)
    if total == 0:
        return {
            'n_ceo_mentions': 0,
            'n_unique_execs': len(execs),
            'exec_hhi': float('nan'),
        }
    fracs = [c / total for c in counts]
    hhi = sum(f * f for f in fracs)
    return {
        'n_ceo_mentions': total,
        'n_unique_execs': len(execs),
        'exec_hhi': hhi,
    }


def main():
    stage_start = time.time()
    logger.info("=" * 60)
    logger.info("阶段 19: LLM CEO/Chairman NER (v3.7.0 PR #13, D4)")
    logger.info(f"  DC3 archive: {'ENABLED' if HAS_ARCHIVE else 'SKIPPED (未集成)'}")
    logger.info("=" * 60)

    output_dir = CONFIG['paths']['output_dir']
    src_path = os.path.join(output_dir, '13_news_with_ctx.parquet')
    if not os.path.exists(src_path):
        logger.error(f"  stage 13 未跑: {src_path}")
        sys.exit(1)

    df = pd.read_parquet(src_path)
    logger.info(f"  article-level: {len(df)} 行")

    # P0 修复 (metric-audit 2026-06-02): 13_news_with_ctx 仅有 str 型 '日期',
    # 无 'year' 列; 此前 line ~467 直接 groupby(['target_bank','year']) →
    # KeyError: 'year' (active crash, stage 19 自 2026-06-01 已 enabled). 镜像
    # runner.py:1094-1100 / attention_media.py:255-257 的 year 派生.
    if 'year' not in df.columns:
        if '日期' not in df.columns:
            logger.error("  缺 'year' 与 '日期' 列, 无法做 bank-year 聚合")
            sys.exit(1)
        df['year'] = pd.to_datetime(df['日期'], errors='coerce').dt.year

    # audit S11 修复 (2026-05-30): 全 run 共用单一 LLMCache 连接, 传入每次
    # call_llm_for_ner, 替代此前每篇文章 ×双轨 = 2N 次新建连接不关闭 (production
    # 40 万规模 = 80 万次 SQLite/WAL 句柄开关, Windows 易触上限)。正常路径在末尾
    # 显式 close; sys.exit 路径由进程退出回收 (单一连接, 不累积)。
    try:
        from news_process.core.caching import LLMCache
        _ner_cache = LLMCache(CACHE_DB_PATH)
    except Exception:
        _ner_cache = None

    # 双轨 LLM 调用 (cost: ~$6 each)
    # P1 修复 (metric-audit 2026-06-02, 病根A 标题不对称): full 轨改读 content_full
    # (=标题+正文, stage 13 物化), 与 ctx 轨 (content_ctx 含标题) 对称; 缺列回退 '内容'.
    _full_col = 'content_full' if 'content_full' in df.columns else '内容'
    for suffix, content_col in (('full', _full_col), ('ctx', 'content_ctx')):
        if content_col not in df.columns:
            continue
        logger.info(f"  ── 轨道 {suffix} ──")
        records = []
        n_failed = 0
        for idx, row in df.iterrows():
            execs, call_failed = call_llm_for_ner(
                content=row[content_col],
                bank_name=row.get('target_bank', ''),
                cache_namespace=f'd4_ceo_ner_{suffix}',
                return_status=True,
                cache=_ner_cache,  # audit S11: 复用共享连接, 不每篇新建
            )
            if call_failed:
                # audit-fixes 2026-05-29 (M4): LLM 调用失败 → NaN (不当作 0 高管)
                n_failed += 1
                feats = {'n_ceo_mentions': float('nan'),
                         'n_unique_execs': float('nan'),
                         'exec_hhi': float('nan')}
            else:
                feats = extract_ner_features(execs)
            records.append({
                'article_id': idx,
                f'n_ceo_mentions_{suffix}': feats['n_ceo_mentions'],
                f'n_unique_execs_{suffix}': feats['n_unique_execs'],
                f'exec_hhi_{suffix}': feats['exec_hhi'],
            })
        # audit-fixes 2026-05-29 (M4): 失败率 > 50% = LLM 整体宕机, 拒绝写出
        # 退化面板 (此前 100% 失败会静默产出全零面板并 exit 0, 与"确无高管"不可
        # 区分)。与 tone_llms 的 call_failure→NaN 约定一致。
        if len(df) > 0 and n_failed / len(df) > 0.5:
            logger.error(
                f"  轨道 {suffix}: LLM NER 调用失败率 {n_failed}/{len(df)} "
                f"({100 * n_failed / len(df):.0f}%) > 50%, 疑似 API 整体宕机; "
                f"拒绝写出退化面板。请检查 YUNWU_API_KEY / 网络后重跑。"
            )
            sys.exit(1)
        ner_df = pd.DataFrame(records)
        for col in ner_df.columns:
            if col != 'article_id':
                df[col] = ner_df.set_index('article_id').loc[df.index, col].values

    # ── bank-year 聚合 ──
    # 诚实度: 三列均用等权 'mean' 对篇级值简单平均 —— exec_hhi 是 mean(篇级 HHI)
    # 而非 mention-weighted pooled HHI; n_unique_execs 是篇级 distinct 数的 mean
    # 而非跨文章池化去重 (无跨银行/跨文章实体去歧义)。详见模块 docstring 口径声明。
    agg_cols = {}
    for c in df.columns:
        if any(c.startswith(p) for p in ('n_ceo_mentions_', 'n_unique_execs_', 'exec_hhi_')):
            agg_cols[c] = 'mean'

    if not agg_cols:
        logger.error("  无 NER 列输出; D4 LLM 调用 stub 未实施 (G-D4.1 待启用)")
        sys.exit(0)

    panel = df.groupby(['target_bank', 'year'], as_index=False).agg(agg_cols)
    out_path = os.path.join(output_dir, '19_executive_ner_panel.parquet')
    panel.to_parquet(out_path, index=False)
    logger.info(f"  bank-year panel → {out_path} ({len(panel)} 行)")
    logger.info(f"  耗时: {time.time() - stage_start:.1f} s")
    # audit S11 修复: 正常路径显式关闭共享 cache 连接。
    if _ner_cache is not None:
        _ner_cache.close()


if __name__ == '__main__':
    main()
