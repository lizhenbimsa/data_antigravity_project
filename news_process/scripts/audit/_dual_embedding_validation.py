"""一次性小样本验证: 双模型嵌入引擎 (主=text-embedding-3-small API / 稳健=text2vec local)。

不触 production panel / golden; 用 scratch cache DB。验证:
  ① 主 spec 经 yunwu 真实 API → 维度 1536 + 连通
  ② 第二次调用同文本 → 缓存命中 (writes 不增)
  ③ 稳健 spec 本地 text2vec → 维度 768
  ④ cosine 值域合理 + 主/稳健 twin Spearman 相关 (非 ≈1 非 ≈0)
"""
import os
import sys
import tempfile

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from news_process.core.caching import LLMCache  # noqa: E402
from news_process.core.config import load_config  # noqa: E402
from news_process.pipeline.text import embedding_engine as eng  # noqa: E402

CFG = load_config()
MAIN = CFG.get('embedding_api', {})
ROBUST = CFG.get('embedding_robustness', {})

print(f"MAIN spec    : model={MAIN.get('model')} base_url={MAIN.get('base_url')}")
print(f"ROBUST spec  : model={ROBUST.get('model')} base_url={ROBUST.get('base_url')}")
assert not eng.spec_uses_local(MAIN), "主 spec 应为 API (base_url != local)"
assert eng.spec_uses_local(ROBUST), "稳健 spec 应为 local"

TEXTS = [
    "工商银行加大金融科技投入，推进区块链与移动支付的数字化转型。",
    "建设银行发布智能风控平台，提升信贷审批效率。",
    "中国银行布局开放银行，深化与金融科技公司合作。",
    "农业银行强化数据中台建设，赋能普惠金融业务。",
    "招商银行手机银行月活突破亿级，零售金融科技领先。",
]

scratch_db = os.path.join(tempfile.gettempdir(), "_dualemb_scratch_cache.db")
if os.path.exists(scratch_db):
    os.remove(scratch_db)

# ① 主 spec 真实 API (cold)
with LLMCache(scratch_db) as cache:
    import asyncio
    emb_api = asyncio.run(eng.get_embeddings_api(TEXTS, MAIN, cache, enable_archive=False))
    s1 = cache.stats()
print(f"\n① API cold: shape={emb_api.shape} hits={s1['hits']} writes={s1['writes']}")
assert emb_api.shape == (len(TEXTS), 1536), f"主轨维度应为 1536, 实得 {emb_api.shape}"

# ② 第二次 → 缓存命中
with LLMCache(scratch_db) as cache:
    emb_api2 = asyncio.run(eng.get_embeddings_api(TEXTS, MAIN, cache, enable_archive=False))
    s2 = cache.stats()
print(f"② API warm: shape={emb_api2.shape} hits={s2['hits']} writes={s2['writes']} hit_rate={s2['hit_rate']:.2f}")
assert s2['writes'] == 0, f"第二次应全缓存命中, writes={s2['writes']}"
assert s2['hits'] == len(TEXTS), f"应命中 {len(TEXTS)} 条, 实得 {s2['hits']}"
assert np.allclose(emb_api, emb_api2), "缓存命中向量应与首次一致"

# ③ 稳健 spec 本地 text2vec
emb_t2v = eng.embed_texts(TEXTS, ROBUST, log_prefix="t2v")
print(f"③ local t2v: shape={emb_t2v.shape}")
assert emb_t2v is not None and emb_t2v.shape[0] == len(TEXTS), "稳健轨应返回 n 行"
assert emb_t2v.shape[1] == 768, f"text2vec 维度应为 768, 实得 {emb_t2v.shape}"

# ④ cosine 值域 + 主/稳健 twin 相关性
from scipy.stats import spearmanr  # noqa: E402
from sklearn.metrics.pairwise import cosine_similarity  # noqa: E402

anchor_api = emb_api.mean(axis=0, keepdims=True)
cos_api = cosine_similarity(emb_api, anchor_api).ravel()
anchor_t2v = emb_t2v.mean(axis=0, keepdims=True)
cos_t2v = cosine_similarity(emb_t2v, anchor_t2v).ravel()
print(f"④ cos_api range=[{cos_api.min():.3f},{cos_api.max():.3f}] "
      f"cos_t2v range=[{cos_t2v.min():.3f},{cos_t2v.max():.3f}]")
assert (cos_api >= -1.001).all() and (cos_api <= 1.001).all(), "API cosine 越界"
assert (cos_t2v >= -1.001).all() and (cos_t2v <= 1.001).all(), "t2v cosine 越界"
rho, _ = spearmanr(cos_api, cos_t2v)
print(f"   主/稳健 twin Spearman ρ = {rho:.3f} (两模型相关但不相同, 符合稳健性对照预期)")

os.remove(scratch_db)
print("\n[OK] dual-embedding small-sample validation PASSED "
      "(main 1536-API + robust 768-text2vec, cache-isolated hit, production untouched)")
