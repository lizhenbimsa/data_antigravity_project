"""一次性探针: 实测 jieba 对中文金融新闻文本的分词有效性。
- 报 jieba 版本
- 裸 jieba 分词 vs 注入领域词后分词 (域复合词是否被切碎)
- cn_tokenize (core/text) 行为 + 停用词过滤
- tone_words 独立 tokenizer 注入态
- 单字 / 纯英文 / 数字 / 标点 边界
不写盘任何产物 (仅 stdout)。$0, 纯 CPU。
"""
from __future__ import annotations

import io
import sys

# 强制 UTF-8 stdout (Windows GBK 控制台防乱码)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import jieba  # noqa: E402

print("=" * 70)
print(f"jieba.__version__ = {getattr(jieba, '__version__', '<none>')}")
print("=" * 70)

# 代表性中文金融科技新闻样本 (含领域复合词、银行名、英文混排、数字)
SAMPLES = [
    "招商银行联合蚂蚁金服推出基于区块链的供应链金融科技平台。",
    "工商银行的金融科技子公司加大对人工智能与大数据风控的投入。",
    "央行强调要防范互联网金融的系统性风险，规范第三方支付与网络借贷。",
    "该行数字普惠金融业务的不良贷款率较去年同期显著下降。",
    "平安银行2023年净利润同比增长12%，金融科技战略转型成效明显。",
]

print("\n### 1. 裸 jieba.cut (默认词典, 无领域注入) ###")
for s in SAMPLES:
    toks = list(jieba.cut(s))
    print(f"  原文: {s}")
    print(f"  分词: {' / '.join(toks)}")
    print()

# 关注的领域复合词是否被默认词典切碎
DOMAIN_WORDS = [
    "金融科技", "区块链", "供应链金融", "人工智能", "大数据风控",
    "互联网金融", "第三方支付", "网络借贷", "数字普惠金融", "不良贷款率",
    "蚂蚁金服", "招商银行", "工商银行", "平安银行",
]
print("### 2. 领域复合词: 裸 jieba 能否整词切出 (cut(w)==[w]) ###")
for w in DOMAIN_WORDS:
    cut = list(jieba.cut(w))
    ok = "✅整词" if cut == [w] else "❌被切碎"
    print(f"  {w:<10} -> {' / '.join(cut):<20} {ok}")

print("\n### 3. add_word 注入后 (独立 Tokenizer 实例) ###")
tk = jieba.Tokenizer()
for w in DOMAIN_WORDS:
    tk.add_word(w)
for w in DOMAIN_WORDS:
    cut = list(tk.cut(w))
    ok = "✅整词" if cut == [w] else "❌仍碎"
    print(f"  {w:<10} -> {' / '.join(cut):<20} {ok}")

print("\n### 4. 注入后整句分词 (域词应整体出现) ###")
for s in SAMPLES:
    toks = list(tk.cut(s))
    print(f"  {s}")
    print(f"  -> {' / '.join(toks)}")
    print()

# 项目通用 tokenizer
print("### 5. core.text.cn_text_utils.cn_tokenize (停用词过滤 + 单字/英文/数字剔除) ###")
try:
    from news_process.core.text.cn_text_utils import CN_FIN_STOPWORDS, cn_tokenize
    print(f"  停用词表大小: {len(CN_FIN_STOPWORDS)}")
    for s in SAMPLES:
        toks = cn_tokenize(s)
        print(f"  {s}")
        print(f"  -> {' / '.join(toks)}")
        print()
except Exception as e:  # noqa: BLE001
    print(f"  [cn_tokenize import 失败] {type(e).__name__}: {e}")

print("### 6. 边界: 单字真词 / 纯英文 / 数字 / 标点 在 cn_tokenize 下被丢弃? ###")
try:
    from news_process.core.text.cn_text_utils import cn_tokenize
    edge = "钱 是 fintech AI 2023 ， 。 龙 虎"
    print(f"  原文: {edge}")
    print(f"  cn_tokenize -> {cn_tokenize(edge)}")
    print("  (注: 单字'钱/龙/虎'/纯英文'fintech'/'AI'/数字'2023' 是否被 <2 / 纯英文 / 数字 规则丢弃)")
except Exception as e:  # noqa: BLE001
    print(f"  [skip] {e}")

print("\nDONE.")
