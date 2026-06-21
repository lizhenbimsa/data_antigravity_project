"""经验性验证: 注入金科词到 _jieba_tokenizer 的真实影响 (ground-truth blast radius)。

直接调用 strategic_diff 的**真实** _build_tfidf_sim_matrix / _build_lda_jsd_matrix,
在**真实**银行-年聚合文本上对比"当前裸 jieba" vs "注入金科词"两种分词器, 实测:
  C1 char 相似度矩阵: 注入前后是否字节一致 (证 char 轨免疫)
  C2 word 相似度矩阵: 注入前后是否变化 (证注入生效)
  C3 word 矩阵注入态两跑: 是否一致 (证确定性)
  C4 LDA: 注入前后是否跑通且变化 (证 LDA 受影响且不崩)
  C5 tokenizer 隔离: 注入实例出整词, 全局 jieba 仍切碎 (证全局纯净)
  C6 NaN/退化: 注入后是否无 NaN 爆增
不写盘任何产物, 不触 panel/golden。$0, 纯 CPU, 离线。
"""
from __future__ import annotations

import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 离线/确定性护栏 (本探针不调 API, 仅防 import 副作用)
os.environ.setdefault("NEWS_PROCESS_LLM_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import jieba  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import news_process.pipeline.features.strategic_diff as sd  # noqa: E402
from news_process.core.config import load_config  # noqa: E402
from news_process.core.text.ahocorasick import load_fintech_dict  # noqa: E402

CFG = load_config()
ROOT = r"F:\WiseSearch\data_antigravity_project\news_process"

# ── 1. 载入金科词 (单一事实源, 与计划 D2 一致) ──
dict_path = CFG["paths"].get("fintech_dict_file") or os.path.join(ROOT, "config", "fintech_dict.json")
FINTECH_KEYWORDS, _ = load_fintech_dict(dict_path)
print(f"金科词典: {len(FINTECH_KEYWORDS)} 词  (from {dict_path})")

# ── 2. 构造"注入态独立 tokenizer"原型 (镜像计划 §D1/§4) ──
_inj_tk = jieba.Tokenizer()
for _kw in FINTECH_KEYWORDS:
    _inj_tk.add_word(_kw)


def _injected_jieba_tokenizer(text: str) -> list[str]:
    """计划提议的新 _jieba_tokenizer: 独立注入实例 + 同样的 len>=2 + 停用词过滤。"""
    return [w for w in _inj_tk.cut(text) if len(w) >= 2 and w not in sd._STOPWORDS]


# 保存原始引用
_orig_tokenizer = sd._jieba_tokenizer

# ── C5: tokenizer 隔离实测 ──
print("\n=== C5: tokenizer 隔离 (注入实例 vs 全局) ===")
probe_words = ["金融科技", "区块链", "第三方支付", "数字普惠金融", "大数据风控"]
for w in probe_words:
    inj = list(_inj_tk.cut(w))
    glob = list(jieba.cut(w))
    print(f"  {w:<10} 注入实例={'/'.join(inj):<14} 全局jieba={'/'.join(glob):<14} "
          f"{'✅整词+全局仍碎(隔离OK)' if inj == [w] and glob != [w] else '⚠检查'}")

# ── 3. 载入真实文章级数据并用 strategic_diff 真实聚合 ──
art_path = os.path.join(ROOT, "data", "processed", "40_article_bank_level.parquet")
df = pd.read_parquet(art_path)
# 该 parquet 已含 year; full 轨文本列
text_col = "content_full" if "content_full" in df.columns else "内容"
print(f"\n真实文章数据: {art_path}  rows={len(df)}  text_col={text_col}")

agg = sd._aggregate_bank_year_texts(df, text_col=text_col)
# 选银行数最多的年份
yr = agg.groupby("year").size().idxmax()
dy = agg[agg["year"] == yr]
texts = dy["agg_text"].tolist()
banks = dy["target_bank"].tolist()
print(f"选定年份={yr}  银行数={len(texts)}  (用真实聚合文本跑真实 _build_* 函数)")


def _summ(mat):
    if mat is None:
        return "None"
    a = np.asarray(mat, dtype=float)
    off = a[~np.eye(a.shape[0], dtype=bool)]
    return (f"shape={a.shape} mean_offdiag={np.nanmean(off):.6f} "
            f"nan%={100*np.isnan(a).mean():.2f}% sha={hash(a.tobytes())&0xffffffff:08x}")


# ── C1: char 矩阵 (不经 jieba, 应与分词器无关) ──
print("\n=== C1: char 相似度矩阵 (注入前后应字节一致 → char 轨免疫) ===")
sd._jieba_tokenizer = _orig_tokenizer
char_a, _ = sd._build_tfidf_sim_matrix(texts, "char")
sd._jieba_tokenizer = _injected_jieba_tokenizer
char_b, _ = sd._build_tfidf_sim_matrix(texts, "char")
print(f"  char(当前)  : {_summ(char_a)}")
print(f"  char(注入)  : {_summ(char_b)}")
print(f"  → char 注入前后 array_equal = {np.array_equal(np.nan_to_num(char_a), np.nan_to_num(char_b))} "
      f"{'✅免疫' if np.array_equal(np.nan_to_num(char_a), np.nan_to_num(char_b)) else '❌意外变化'}")

# ── C2 + C3: word 矩阵 当前 vs 注入 vs 注入重跑 ──
print("\n=== C2/C3: word 相似度矩阵 (当前 vs 注入 vs 注入重跑) ===")
sd._jieba_tokenizer = _orig_tokenizer
word_cur, _ = sd._build_tfidf_sim_matrix(texts, "word")
sd._jieba_tokenizer = _injected_jieba_tokenizer
word_inj1, _ = sd._build_tfidf_sim_matrix(texts, "word")
word_inj2, _ = sd._build_tfidf_sim_matrix(texts, "word")
print(f"  word(当前)    : {_summ(word_cur)}")
print(f"  word(注入#1)  : {_summ(word_inj1)}")
print(f"  word(注入#2)  : {_summ(word_inj2)}")
chg = not np.array_equal(np.nan_to_num(word_cur), np.nan_to_num(word_inj1))
det = np.array_equal(np.nan_to_num(word_inj1), np.nan_to_num(word_inj2))
_maxd = float(np.nanmax(np.abs(np.nan_to_num(word_cur) - np.nan_to_num(word_inj1))))
print(f"  → C2 注入改变 word 矩阵 = {chg} (max|Δ|={_maxd:.6f}) {'✅注入生效' if chg else '⚠无变化'}")
print(f"  → C3 注入态两跑一致 = {det} {'✅确定性' if det else '❌非确定'}")

# ── C4: LDA 当前 vs 注入 (跑通 + 变化) ──
print("\n=== C4: LDA+JSD 矩阵 (注入前后跑通且变化) ===")
try:
    sd._jieba_tokenizer = _orig_tokenizer
    lda_cur, _ = sd._build_lda_jsd_matrix(texts, len(texts))
    sd._jieba_tokenizer = _injected_jieba_tokenizer
    lda_inj1, _ = sd._build_lda_jsd_matrix(texts, len(texts))
    lda_inj2, _ = sd._build_lda_jsd_matrix(texts, len(texts))
    print(f"  LDA(当前)   : {_summ(lda_cur)}")
    print(f"  LDA(注入#1) : {_summ(lda_inj1)}")
    print(f"  LDA(注入#2) : {_summ(lda_inj2)}")
    lchg = not np.array_equal(np.nan_to_num(lda_cur), np.nan_to_num(lda_inj1))
    ldet = np.array_equal(np.nan_to_num(lda_inj1), np.nan_to_num(lda_inj2))
    print(f"  → C4 注入改变 LDA = {lchg} ; 注入态两跑一致 = {ldet} "
          f"{'✅受影响且确定' if lchg and ldet else '⚠检查(LDA确定性依赖BLAS线程钉死)'}")
except Exception as e:  # noqa: BLE001
    print(f"  ❌ LDA 跑崩: {type(e).__name__}: {e}")

# ── C6: NaN 退化检查 ──
print("\n=== C6: NaN/退化 ===")
for nm, m in [("word当前", word_cur), ("word注入", word_inj1)]:
    a = np.asarray(m, dtype=float)
    print(f"  {nm}: nan%={100*np.isnan(a).mean():.2f}%  全1对角?={np.allclose(np.diag(a),1.0)}")

sd._jieba_tokenizer = _orig_tokenizer  # 还原
print("\nDONE.")
