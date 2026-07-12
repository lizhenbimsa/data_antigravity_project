"""v7 W&Z 框架抽查脚本 (R8-K + A 选项)

从 gray_v7_samples.csv 10 行 → 用 v7 unified_cot.txt prompt 调单模型
(gpt-5.4-nano) → 提取 4 个 reason 字段 → 输出 markdown 表供 user BLIND review。

设计原则 (V+W 系列修正):
- AI 永远不输出评分 (anchoring bias 防御; U1/V3)
- Cache hit 优先 (A.0 verified: cache value = raw response 含 reason)
- Z4 prompt injection 防御: input sanitize (将 content 中可能的 prompt
  终止字符 strip; 实际 v7 LLM Rerun 未触发但 audit 工具应 defensive)
- Scope: **internal sanity check, NOT publishable evidence** (W1/W2)
  顶刊 validation 需 n≥500 + 多 raters; 本脚本仅为 v7 commit 信心证明

Execution: 必须从项目根目录运行
    "F:/Anaconda3/python.exe" news_process/scripts/migrate/v7_wz_audit.py

输出: news_process/data/processed/v7_wz_audit_report.md
"""
import asyncio
import json
import os
import re
import sys
from pathlib import Path

# 注入项目父目录到 sys.path (与 prompt_sensitivity.py 一致的 import 习惯)
_HERE = Path(__file__).resolve()
_PROJECT_ROOT = _HERE.parents[3]
sys.path.insert(0, str(_PROJECT_ROOT))

import aiohttp
import pandas as pd

from news_process.core.caching import LLMCache
from news_process.core.config import load_config

CONFIG = load_config()
LLM_CFG = CONFIG.get('tone_llm_processing', {})
PROMPT_TEMPLATE = LLM_CFG.get('prompt_template', '')
PROMPT_VERSION = LLM_CFG.get('prompt_template_version', 'v7-2026-05-14')

# 单模型抽查 (W2: 单 rater 已显式承认, 不作 publishable evidence)
MODEL_ID = 'gpt-5.4-nano'
TEMPERATURE = 0.0

SAMPLES_CSV = 'news_process/data/processed/gray_v7_samples.csv'
REPORT_MD = 'news_process/data/processed/v7_wz_audit_report.md'
CACHE_DB = 'news_process/data/processed/_llm_cache.db'


def sanitize_content(text: str) -> str:
    """Z4: prompt injection 防御 (input sanitization).

    Strip 可能用于 prompt injection 的字符序列。实际 v7 LLM Rerun 未触发
    任何 injection (LLM 输出格式合规), 但 audit 工具应 defensive。
    """
    if not isinstance(text, str):
        return ''
    # 移除可能的 prompt 终止 + 伪造 JSON 模式
    text = re.sub(r'\}\s*,?\s*[\'"][a-z_]+[\'"]\s*:', '', text)
    # 移除连续的 { 或 } (>3 个) 可能用于 JSON 注入
    text = re.sub(r'[\{\}]{3,}', '', text)
    return text.strip()


async def call_llm_with_cache(session: aiohttp.ClientSession, cache: LLMCache,
                              prompt: str) -> tuple[str, bool]:
    """优先用 cache; miss 时调 API。返回 (response_text, cache_hit_bool)。"""
    cached = cache.get(MODEL_ID, prompt,
                       prompt_version=PROMPT_VERSION, temperature=TEMPERATURE)
    if cached:
        return cached, True

    # fix(reaudit-2026-07-12 WP-A3): miss 必须尊重全局离线守卫 — 本脚本经 config 注入
    # 生产 v8 prompt_version, 与 stage 21 同缓存键空间; 无守卫的在线 miss 会绕过
    # "离线=$0" 承诺并把未经生产校验的裸响应预写进生产 _llm_cache.db。
    if os.environ.get('NEWS_PROCESS_LLM_OFFLINE', '').strip().lower() in (
            '1', 'true', 'yes', 'on'):
        # SystemExit ⊂ BaseException ⊄ Exception — 穿透 main() 的逐行 except Exception
        # (镜像 boilerplate SystemExit 穿透先例), 保证离线 miss = 整跑硬失败而非
        # 静默 _error 行 + 误导性 misses:0 汇总。
        raise SystemExit(
            'NEWS_PROCESS_LLM_OFFLINE=1 下缓存 miss — v7_wz_audit 禁止在线付费调用')

    # Cache miss: 调真实 API
    api_key = os.environ.get('YUNWU_API_KEY') or _read_env_key()
    url = 'https://yunwu.ai/v1/chat/completions'
    headers = {'Authorization': f'Bearer {api_key}',
               'Content-Type': 'application/json'}
    payload = {
        'model': MODEL_ID,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': TEMPERATURE,
        'response_format': {'type': 'json_object'},
    }
    async with session.post(url, headers=headers, json=payload,
                            timeout=aiohttp.ClientTimeout(total=60)) as resp:
        data = await resp.json()
        text = data['choices'][0]['message']['content']
        cache.put(MODEL_ID, prompt, text,
                  prompt_version=PROMPT_VERSION, temperature=TEMPERATURE)
        return text, False


def _read_env_key() -> str:
    env_path = _PROJECT_ROOT / 'news_process' / '.env'
    if env_path.exists():
        for line in env_path.read_text(encoding='utf-8').splitlines():
            if line.startswith('YUNWU_API_KEY='):
                return line.split('=', 1)[1].strip().strip('"').strip("'")
    raise RuntimeError('YUNWU_API_KEY 未设置 (env 或 .env)')


def build_prompt(row: pd.Series) -> str:
    """组装 v7 prompt: PROMPT_TEMPLATE.format() 填充 4 placeholder。"""
    return PROMPT_TEMPLATE.format(
        target_bank=row['target_bank'],
        co_mentioned_banks='',  # gray_v7_samples 未含此列, 用空串
        title=sanitize_content(str(row.get('标题', ''))),
        content=sanitize_content(str(row.get('内容', ''))[:2000]),  # 截断防过长
    )


async def main():
    print(f'[v7 W&Z audit] prompt_version: {PROMPT_VERSION}')
    print(f'[v7 W&Z audit] model: {MODEL_ID}')

    df = pd.read_csv(SAMPLES_CSV, encoding='utf-8-sig')
    print(f'[v7 W&Z audit] loaded {len(df)} samples from {SAMPLES_CSV}')

    cache = LLMCache(CACHE_DB)
    n_hits, n_misses = 0, 0
    rows_out = []

    async with aiohttp.ClientSession() as session:
        for idx, row in df.iterrows():
            prompt = build_prompt(row)
            try:
                resp, hit = await call_llm_with_cache(session, cache, prompt)
                n_hits += int(hit)
                n_misses += int(not hit)
                parsed = json.loads(resp)
            except Exception as e:
                print(f'  [row {idx}] error: {e}')
                rows_out.append({**row.to_dict(), '_error': str(e),
                                 '_cache_hit': False})
                continue

            rows_out.append({
                'idx': idx,
                'group': row.get('group', ''),
                'target_bank': row.get('target_bank', ''),
                'title': row.get('标题', '')[:80],
                'v6_text_type': row.get('text_type', ''),
                'v7_innovation_substantiveness': parsed.get('innovation_substantiveness', ''),
                'v7_innovation_locus': parsed.get('innovation_locus', ''),
                'verification_reason': parsed.get('verification_reason', ''),
                'sentiment_reason': parsed.get('sentiment_reason', ''),
                'innovation_substantiveness_reason': parsed.get(
                    'innovation_substantiveness_reason', ''),
                'innovation_locus_reason': parsed.get('innovation_locus_reason', ''),
                'cache_hit': hit,
            })

    print(f'[v7 W&Z audit] cache hits: {n_hits}/{len(df)}, misses: {n_misses}')

    # 输出 markdown 报告
    md = ['# v7 W&Z Framework Audit Report\n',
          f'**Scope**: Internal sanity check (NOT publishable evidence).\n',
          f'**Sample**: n={len(rows_out)} (R8-K 5+3+2 distribution).\n',
          f'**Model**: {MODEL_ID} single-shot.\n',
          f'**Cache hits**: {n_hits}/{len(rows_out)} (v7 LLM Rerun cache reuse).\n',
          '\n## W&Z Concept Checklist (for BLIND user review)\n',
          '审 each row\'s `innovation_substantiveness_reason` against:\n',
          '(a) 实质经济后果 / 实际后果 / 可验证后果\n',
          '(b) 合法性 / legitimacy / 印象管理\n',
          '(c) 脱钩 / decoupling\n',
          '(d) 信号 / signaling\n',
          '(e) 公关包装 / 营销包装 / 表演性\n',
          '(f) 实质投入 / 资源投入\n',
          '\n通过判据: **≥7/10 行 reason 含 ≥1 个 (a)-(f) 关键概念**\n',
          '\n## Samples\n']
    for r in rows_out:
        if '_error' in r:
            md.append(f'\n### Row {r.get("idx", "?")} — ERROR: {r["_error"]}\n')
            continue
        md.append(f'\n### Row {r["idx"]} | group={r["group"]} | bank={r["target_bank"]} | cache_hit={r["cache_hit"]}\n')
        md.append(f'**标题**: {r["title"]}...\n\n')
        md.append(f'- v6 text_type: `{r["v6_text_type"]}`\n')
        md.append(f'- v7 innovation_substantiveness: `{r["v7_innovation_substantiveness"]}`\n')
        md.append(f'- v7 innovation_locus: `{r["v7_innovation_locus"]}`\n\n')
        md.append(f'**verification_reason**: {r["verification_reason"]}\n\n')
        md.append(f'**sentiment_reason**: {r["sentiment_reason"]}\n\n')
        md.append(f'**innovation_substantiveness_reason** (focus for W&Z audit):\n')
        md.append(f'> {r["innovation_substantiveness_reason"]}\n\n')
        md.append(f'**innovation_locus_reason**:\n')
        md.append(f'> {r["innovation_locus_reason"]}\n\n')
        md.append('---\n')

    Path(REPORT_MD).write_text(''.join(md), encoding='utf-8')
    print(f'[v7 W&Z audit] report saved: {REPORT_MD}')


if __name__ == '__main__':
    asyncio.run(main())
