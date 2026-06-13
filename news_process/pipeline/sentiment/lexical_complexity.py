"""news_process.pipeline.sentiment.lexical_complexity — 词汇/句法复杂度 $0 测度族.

2026-06-05 新增 (顶刊文本测度缺口报告批 #2–#6)。一篇文章做**单次** jieba.posseg
词性标注 pass, 派生 6 个互补的"披露质量/可读性"测度, 全部 $0 (jieba 0.42.1 冻结,
无付费 LLM、无新 PyPI 依赖、不触 M0 门、不动 Prompt v8), 真双轨 (_full/_ctx)。

测度与锚点:
  1. rare_word_ratio   低频词率   — You & Zhang (2009) RAS; Gentzkow-Kelly-Taddy
                                     (2019) JEL §2.2 (TF-IDF/词频). 词汇难度维, 补
                                     CPW/TTR 未覆盖的"术语稀有度"。
  2. hard_char_ratio   难字率     — Dale & Chall (1948) familiar-word 思路的中文落地;
                                     丘心颖等 (2016)《经济学(季刊)》15(4):1483-1506.
                                     即英文 Fog "%complex words" 的中文等价 (中文无音节)。
  3. nominalization_ratio 名词化率 — Bonsall-Leone-Miller-Rennekamp (2017) JAE Bog
                                     Index 句法成分之一 (动词憋成抽象名词→官腔/难读)。
  4. function_word_ratio 功能词比率 — LIWC Analytic 维的中文近似 (虚词占比高≈低分析性)。
  5. specificity_index 硬信息密度 — Hope, Hu & Lu (2016) RAS 21(4):1005-1045. 报道
                                     具名实体+数字占比 (reframe: 是"报道"硬信息密度,
                                     非 10-K 自我披露 specificity)。
  6. within_doc_redundancy 文档内冗余 — Dyer-Lang-Stice-Lawrence (2017) JAE; Cazier &
                                     Pfeiffer (2016). 篇内自重复 (与 staleness/herd 的
                                     "跨文章重复"正交: 篇内 vs 篇间)。

诚实限定 (写入论文须披露):
  - jieba.posseg 走 词典+HMM, nr/ns/nt 实体边界与歧义精度低于专用 NER, 属"粗近似/
    上界噪声估计", 措辞应为"以 jieba 词性近似硬信息类别", 勿声称等同 Stanford NER。
  - hard_char 的"常用字集"由 jieba 0.42.1 冻结词典词频派生 (可复现 $0 代理); 官方
    《通用规范汉字表》一级字 3500 可作未来 drop-in 替换 (见 _common_char_set)。
  - within_doc_redundancy 用字符 3-gram 自重复比; 中文新闻篇幅中位 ~800 字、常无段落
    标记, 篇内信号弱于 10-K, 全量下宜另出 bank-year pooled 版互为稳健 (本模块仅篇级)。
  - within_doc_redundancy **强机械长度依赖** (fix(omni-g-numlex-05, 2026-06-11) 披露):
    TTR 族经典缺陷 (Covington & McFall 2010 同构) — 文档越长, 常用 3-gram 重复概率
    机械上升。盘上 1170 篇实测 corr(去空白字符数, redundancy)=0.50 / corr(log 长度)=0.47,
    长度五分位组均值 0.119→0.228 严格单调; full 轨 (中位 ~1553 字) vs ctx 轨 (~725 字)
    的轨间 redundancy 差异首先是长度伪差异。**回归中必须同时控制长度** — 本模块配套
    输出 'redundancy_log_length' (= ln 去空白字符数, 与 redundancy 同定义域) 作控制变量。
  - within_doc_redundancy_han **汉字口径孪生** (fix(hanzi-char-dual, 2026-06-13)): 字符版
    within_doc_redundancy 的 3-gram 含数字/标点/拉丁, 当一篇数字标点占比异常时其"重复"
    部分来自非汉字符号而非中文行文复读。孪生列先抽**纯汉字子序列** (is_cjk 过滤) 再切
    3-gram, 分子(唯一汉字3-gram)/分母(全部汉字3-gram)同为汉字口径。
    ⚠ **定位 (顶刊终审 L1-1, 须如实披露)**: 实测全量 1170 篇 content_full 上
    corr(within_doc_redundancy, within_doc_redundancy_han)=**0.99** (mean char 0.168 vs
    han 0.154, 仅 26.8% 文 |diff|>0.02)。故本列**不是**与字符版互补的第二独立构念, 而是
    "字符口径对非汉字符号扰动的**敏感性诊断**"; 论文报告须披露该 r≈0.99, 且**不**与字符版
    同进一回归 (近完美共线)。注: 这兑现的是用户指令的**「双口径」面 (汉字 vs 字符)**;
    指令的「分子分母口径一致」面由 hard_char_ratio (分子分母同为汉字) 代表 —— 字符版
    within_doc_redundancy 本就分子分母同口径 (字符3-gram), 从不违反一致性, 故 _han 孪生
    并非"修复不一致"。
  - 锚点 Dyer-Lang-Stice-Lawrence (2017) JAE / Cazier-Pfeiffer (2016) 系英文 10-K 文本
    冗余构念; 汉字口径为本项目据该构念之**中文落地** (原文非汉字 operationalization),
    属概念同源, 论文措辞勿声称等同原文做法 (与 hard_char_ratio 的"丘心颖 2016 本土锚"同理)。
    配套 'redundancy_han_log_length' (= ln 汉字数) 作汉字口径长度控制 (同 redundancy_log_length
    之于字符版); 二者均 < 3 个对应单位 → 双 nan。汉字口径纯字符级、零分词器依赖, 对 jieba
    全局注入 byte 级不变, 确定性强于 jieba-based 测度。
  - rare_word 阈值 (RARE_WORD_PERCENTILE=20) 确定性派生, 但低频侧巨量 tie 致实测覆盖约
    57% distinct 词 (非紧致 20% 尾部), 实为"非高频词率"; spec/论文须如实表述。
  - rare_word 分子已排除纯数字/纯拉丁 token (fix(omni-g-numlex-04, 2026-06-11)): 阿拉伯
    数字与英文 token 不在 jieba 中文词典 (OOV freq=0 ≤ cutoff) — 修前实测分子 26.4% 是
    纯数字、3.7% 是拉丁 token, 与词汇难度构念无关且与 num_intensity 机械同源; 分母
    (n_real) 口径不变, 与其余比率一致。
  - specificity 的 m 词性分子已排除模糊量词 (fix(omni-g-numlex-06, 2026-06-11)): jieba
    把 '一些/许多/若干/几十家' 也标 'm', 而 Hope-Hu-Lu (2016 RAS) 的构念是 specific vs
    vague 对立, 模糊量词在 vague 侧; m-token 仅当含实数字字符且非模糊量词时计入。
  - nominalization: f[0]=='n' 亦匹配 nr/ns/nt/nz 专名词性, 故"姓+性/化/度/型/制"型人名
    (如 jieba 把 '赵性' 误标 nr) 会被计入 → 小幅高估, 属上界噪声 (与下方"粗近似"披露一致;
    收紧排除专名会同时漏掉被 jieba 误标 nr 的真名词化如 '安全性', 取舍后选保留 recall)。
  - 本模块全部分词/词性/词频走**独立未注入 jieba Tokenizer 实例** (fix(omni-g-numlex
    jieba-isolation, 2026-06-11), 见 _get_pristine_tokenizer): 不再读全局 jieba.dt —
    任何其它模块对全局分词器的 add_word 注入 (领域词 tag='x' 回退会把 OOV 词当标点
    剔出分母) 都不影响本测度族, 同一文本在注入态/非注入态恒给同一值 (确定性)。
"""
from __future__ import annotations

import functools
import math
import re
import threading

import jieba
import jieba.posseg as pseg

# fix(hanzi-char-dual, 2026-06-13): 汉字判定走 cn_text_utils 单一事实源原语 (is_cjk),
# 取代本模块历史散落的 `'一' <= ch <= '鿿'` 内联谓词 —— 字节等价纯重构, 不改任何
# 已落盘值; 同时新增的汉字口径篇内冗余 within_doc_redundancy_han 也据此与字符口径
# within_doc_redundancy 互为"字符 vs 汉字"双口径稳健性 (双轨纪律)。
from news_process.core.text.cn_text_utils import is_cjk

# ── 常量 (spec 固定) ─────────────────────────────────────────────────────────
# 低频词阈值: jieba 冻结词典正词频分布的第 P 百分位 (确定性、可复现)。
# ⚠ 因低频侧巨量并列 (freq=2 约 4 万词、freq=3 约 16 万词), 第 20 百分位 cutoff 实测=3.0,
# 用 <= 谓词会把 freq<=3 的词全计入 → rare_word_ratio 实际覆盖约 57% distinct 词 (含
# OOV freq=0 升至约 70%), 即度量"非高频词率"而非紧致的最稀有 20% 尾部。论文/spec 须如实
# 表述, 勿声称"低频 20% 阈值" (审核 2026-06-05 P2)。
RARE_WORD_PERCENTILE = 20
# 常用字覆盖率: 累计到该比例的字频质量定义"常用字" (越大常用字集越大、难字率越低)
COMMON_CHAR_COVERAGE = 0.995
# 难字率分母最小 Han 字数 (过短文本难字率不稳, 低于此返回 nan)
_MIN_HAN_CHARS = 5

# 名词化后缀 (动词/形容词 → 抽象名词: 数字化/安全性/合规度/中心型/股份制)
_NOMINAL_SUFFIX = frozenset({'性', '化', '度', '型', '制'})
# 名词化词性: vn(名动词) / an(名形词)
_NOMINAL_FLAGS = frozenset({'vn', 'an'})

# 功能词词性前缀 (LIWC function words 的中文映射): u 助词 / p 介词 / c 连词 / r 代词 /
# y 语气词 / e 叹词. 不含 d 副词 (副词偏内容, 保守排除)。
_FUNCTION_FLAG_PREFIXES = ('u', 'p', 'c', 'r', 'y', 'e')

# 具名实体词性 (硬信息): nr 人名 / ns 地名 / nt 机构 / nz 其他专名
_ENTITY_FLAGS = frozenset({'nr', 'ns', 'nt', 'nz'})

# fix(omni-g-numlex-04, 2026-06-11): rare_word 分子排除谓词 — 纯数字/纯拉丁 token
# (含 '3.5%'/'2017'/'ABC'/'Q3' 类) 是 OOV (freq=0 ≤ cutoff) 但与词汇难度构念无关。
_NON_LEXICAL_TOKEN_RE = re.compile(r'^[0-9A-Za-z.,%％‰．\-]+$')

# fix(omni-g-numlex-06, 2026-06-11): jieba 标 'm' 的模糊量词 (vague quantifier) —
# Hope-Hu-Lu (2016 RAS) specificity 构念中应在 vague 侧, 不得计入硬信息分子。
# 另: 以 几/数 开头的不定量 ('几十家'/'数百') 同属 vague (见 _is_hard_m_token)。
_VAGUE_M_TOKENS = frozenset({
    '一些', '许多', '若干', '大量', '不少', '部分', '少量', '少许', '一点', '一定',
})
# m-token 须含实数字字符 (阿拉伯/全角/中文数字) 才算硬信息
_M_REAL_NUM_CHAR_RE = re.compile(r'[0-9０-９零一二两三四五六七八九十百千万亿]')


def _is_hard_m_token(w: str) -> bool:
    """m 词性 token 是否为"硬"数量信息 (fix(omni-g-numlex-06, 2026-06-11)).

    排除: 模糊量词表命中 / 几|数 开头的不定量 / 不含实数字字符的 token。
    保留: '100' / '亿元' / '三十' / '5家' 等真定量。
    """
    if w in _VAGUE_M_TOKENS or w.startswith(('几', '数')):
        return False
    return bool(_M_REAL_NUM_CHAR_RE.search(w))

# 逆接/转折连词【独立词表】—— 刻意不复用 config/sentiment.yaml 的 adversative_words
# (那张表驱动情感 boost; 复用会让本 RHS 与情感轨机械同源、污染度量纯度, 见缺口报告 G5)。
# 锚: Ding-Liu-Yu (2008) WSDM; 徐巍-姚振晔-陈冬华 (2021)《会计研究》(3):28-44 (副词连词占比)。
_ADVERSATIVE_WORDS = frozenset({
    '但', '但是', '然而', '却', '可是', '不过', '尽管', '虽然', '虽',
    '反而', '相反', '只是', '反倒', '岂料', '殊不知', '竟然', '不料',
    '尽管如此', '话虽如此', '即便', '即使', '纵然', '哪怕',
})

_PUNCT_FLAG = 'x'  # jieba.posseg 标点/未知词性

# ── 独立未注入 jieba Tokenizer (fix(omni-g-numlex jieba-isolation, 2026-06-11)) ──
# 旧实现读全局 jieba.dt / 模块级 pseg.cut → 结果依赖全局分词器的注入态: 任何
# 模块 add_word 都会改写 FREQ (动 _rare_word_cutoff/_common_char_set 派生) 并把
# OOV 领域词以 tag='x' 回退当标点剔出分母 — 同一文本在注入前/后给两套值, 破坏
# 确定性。修复: 本模块全部分词/词性/词频走从不暴露注入入口的私有 Tokenizer 实例
# (DCL 懒加载单例; tone_words 的领域词注入只进它自己的 _TONE_TOKENIZER, 见
# omni-g-tonewords-10/-11 — 两端隔离后全局 jieba 即使被第三方污染也不影响本族)。
# RLock (非 Lock): _get_pristine_posseg 持锁期间嵌套调用 _get_pristine_tokenizer,
# 非重入锁会自死锁。
# 白话: 全局共享的分词器像公共白板, 别的模块可能往上面加自定义词, 一加,
# 这里算出来的"难词率"等数值就会跟着变, 同一篇文章前后两次算出不同结果。
# 解决办法是自己私藏一块干净白板 (私有 Tokenizer), 谁也写不到它上面,
# 保证结果永远可复现。
_PRISTINE_LOCK = threading.RLock()
_PRISTINE_TOKENIZER: jieba.Tokenizer | None = None
_PRISTINE_POSSEG: pseg.POSTokenizer | None = None


def _get_pristine_tokenizer() -> jieba.Tokenizer:
    """返回本模块专用的独立未注入 jieba.Tokenizer (lazy 单例, DCL 锁)."""
    global _PRISTINE_TOKENIZER
    if _PRISTINE_TOKENIZER is None:
        with _PRISTINE_LOCK:
            if _PRISTINE_TOKENIZER is None:
                tk = jieba.Tokenizer()
                tk.initialize()  # 立即加载冻结词典 (FREQ 确定性来源)
                _PRISTINE_TOKENIZER = tk
    return _PRISTINE_TOKENIZER


def _get_pristine_posseg() -> pseg.POSTokenizer:
    """返回绑定独立 Tokenizer 的 posseg 实例 (lazy 单例, DCL 锁)."""
    global _PRISTINE_POSSEG
    if _PRISTINE_POSSEG is None:
        with _PRISTINE_LOCK:
            if _PRISTINE_POSSEG is None:
                _PRISTINE_POSSEG = pseg.POSTokenizer(tokenizer=_get_pristine_tokenizer())
    return _PRISTINE_POSSEG


@functools.lru_cache(maxsize=1)
def _common_char_set() -> frozenset[str]:
    """从 jieba 0.42.1 冻结词典词频派生"常用字"集 (可复现 $0 代理).

    做法: 遍历独立 Tokenizer 的 FREQ 所有词条 (fix(omni-g-numlex jieba-isolation):
    不再读可被注入污染的全局 jieba.dt.FREQ), 把词频累加到其每个汉字上得到字频;
    按字频降序累计到 COMMON_CHAR_COVERAGE 比例的汉字即"常用字"。
    jieba 词典冻结 → 结果确定性。

    未来可替换为官方《通用规范汉字表》一级字 3500 (drop-in, 改本函数返回值即可)。
    """
    char_freq: dict[str, int] = {}
    for word, freq in _get_pristine_tokenizer().FREQ.items():
        if not freq:
            continue
        for ch in word:
            if is_cjk(ch):  # CJK 统一表意文字 (SSOT 原语, 字节等价旧 '一'<=ch<='鿿')
                char_freq[ch] = char_freq.get(ch, 0) + freq
    if not char_freq:
        return frozenset()
    total = sum(char_freq.values())
    common: set[str] = set()
    cum = 0
    for ch, f in sorted(char_freq.items(), key=lambda kv: kv[1], reverse=True):
        common.add(ch)
        cum += f
        if cum / total >= COMMON_CHAR_COVERAGE:
            break
    return frozenset(common)


@functools.lru_cache(maxsize=1)
def _rare_word_cutoff() -> float:
    """低频词频率阈值 = jieba 冻结词典正词频的第 RARE_WORD_PERCENTILE 百分位.

    词 w 视为"低频/难词" iff FREQ.get(w, 0) <= cutoff (OOV freq=0 → 低频; FREQ 读
    独立 Tokenizer, fix(omni-g-numlex jieba-isolation): 注入词不再漂移百分位)。
    ⚠ 见上方 RARE_WORD_PERCENTILE 注释: 低频侧巨量 tie 使实测 cutoff=3.0、覆盖约 57%
    distinct 词; 该指标实为"非高频词率", 论文表述勿声称紧致 20% 尾部 (审核 2026-06-05 P2)。
    """
    freqs = sorted(f for f in _get_pristine_tokenizer().FREQ.values() if f and f > 0)
    if not freqs:
        return 0.0
    idx = max(0, min(len(freqs) - 1, int(len(freqs) * RARE_WORD_PERCENTILE / 100)))
    return float(freqs[idx])


def _safe_div(num: float, den: float) -> float:
    """分母 > 0 时返回比值 (round 6), 否则 nan (避免 0 分母伪 0)。"""
    return round(num / den, 6) if den > 0 else float('nan')


def _empty_result() -> dict[str, float]:
    """空/无效文本的统一返回 (所有键 → nan, 保证跨行 dict 结构一致)。"""
    return {
        'rare_word_ratio': float('nan'),
        'hard_char_ratio': float('nan'),
        'nominalization_ratio': float('nan'),
        'function_word_ratio': float('nan'),
        'specificity_index': float('nan'),
        'within_doc_redundancy': float('nan'),
        'redundancy_log_length': float('nan'),
        'within_doc_redundancy_han': float('nan'),
        'redundancy_han_log_length': float('nan'),
        'adversative_ratio': float('nan'),
        'n_words_real': float('nan'),
        'n_han_real': float('nan'),
    }


# 模块导出的指标键 (供 tone_words new_metric_cols 登记 + encode 聚合引用)
# fix(omni-g-numlex-05, 2026-06-11): 新增 'redundancy_log_length' (ln 去空白字符数,
# 与 within_doc_redundancy 同定义域) — redundancy 强机械长度依赖 (corr=0.50, 五分位
# 均值 0.119→0.228 严格单调, 见模块 docstring 诚实限定段), 回归用 redundancy 时必须
# 同时控制该列。⚠ 非 [0,1] 比率列 (是 log 字符数), 下游聚合/检验勿按比率断言。
# fix(hanzi-char-dual, 2026-06-13): 新增 'within_doc_redundancy_han' (汉字口径篇内冗余,
# 与字符口径 within_doc_redundancy 互为双口径) + 'redundancy_han_log_length' (ln 汉字数,
# 汉字口径长度控制, 同样非 [0,1] 比率列)。两键经 LEXICAL_COMPLEXITY_KEYS 自动物化为
# *_full/*_ctx 文章列 (tone_words), within_doc_redundancy_han 再由 encode 聚合到面板。
LEXICAL_COMPLEXITY_KEYS = (
    'rare_word_ratio', 'hard_char_ratio', 'nominalization_ratio',
    'function_word_ratio', 'specificity_index', 'within_doc_redundancy',
    'redundancy_log_length', 'within_doc_redundancy_han',
    'redundancy_han_log_length', 'adversative_ratio',
)

# 词级文章长度原始计数 (非比率): mean 聚合后由 geography 做 ln 变换得 ln_word_count
# (Li 2008 JAE 真 MLENGTH 词口径, 补 avg_article_length 的字符口径; 批 #7)。
WORD_COUNT_KEY = 'n_words_real'

# fix(hanzi-char-dual, 2026-06-13): 汉字级文章长度原始计数 (非比率) = 该文 CJK 汉字数
# (= is_cjk 过滤计数, 与 hard_char 的 n_han 同源同值)。mean 聚合 (encode → avg_han_count)
# 后由 geography 做 ln 变换得 ln_han_count —— 补齐文章长度族的**第三口径**: 字符口径
# avg_article_length / 词口径 ln_word_count / 汉字口径 ln_han_count 三者并存, 兑现用户
# "既要考虑汉字也要考虑字符"指令 (中文场景字符含数字标点拉丁, 汉字口径剔除之, 更纯)。
HAN_COUNT_KEY = 'n_han_real'


def _char_trigram_redundancy(content: str) -> tuple[float, float]:
    """篇内冗余: 返回 (redundancy, log_length)。

    redundancy = 1 − (唯一字符3-gram数 / 全部字符3-gram数);
    越高 = 重复 3-gram 越多 = 越啰嗦/套话/复读。短文本 (<3 字) → 双 nan。
    用字符 3-gram 而非 gzip: 避免短文本压缩头部开销主导, 更可解释。

    fix(omni-g-numlex-05, 2026-06-11): 同时返回 log_length = ln(去空白字符数) —
    redundancy 是 TTR 族测度, 对长度强机械依赖 (盘上实测 corr=0.50, 长度五分位
    均值严格单调 0.119→0.228; Covington & McFall 2010 对 TTR 的批评同构), 截面/
    轨间差异大半由长度驱动 → 输出同定义域的 log-length 控制变体列, 回归必控。

    白话: 把文章切成连续 3 个字一组的小片段, 数一数有多少片段是重复出现的,
    重复越多说明越啰嗦。但文章越长, 撞出重复片段的概率天然越高 —— 长文
    显得"更啰嗦"很多时候只是因为它长。所以这里顺手把文章长度 (取对数) 也
    输出一列, 做回归时把它放进去当控制变量, 才能分清"真啰嗦"和"只是长"。
    """
    s = re.sub(r'\s+', '', content)
    if len(s) < 3:
        return (float('nan'), float('nan'))
    grams = [s[i:i + 3] for i in range(len(s) - 2)]
    total = len(grams)
    uniq = len(set(grams))
    redundancy = round(1.0 - uniq / total, 6) if total > 0 else float('nan')
    return (redundancy, round(math.log(len(s)), 6))


def _han_trigram_redundancy(content: str) -> tuple[float, float]:
    """汉字口径篇内冗余: 返回 (redundancy_han, han_log_length)。

    fix(hanzi-char-dual, 2026-06-13): 字符口径 _char_trigram_redundancy 的孪生版。
    先抽取**纯汉字子序列** (is_cjk 过滤掉数字/标点/拉丁/空白) 再切字符 3-gram ——
    分子(唯一汉字3-gram)与分母(全部汉字3-gram)同为汉字口径, 满足"分子分母口径
    一致" (与 hard_char_ratio 同范式)。与字符版互为"字符 vs 汉字"双口径稳健性
    (双轨纪律: 不以相关性取舍, 两版各自进回归)。

    redundancy_han = 1 − (唯一汉字3-gram / 全部汉字3-gram); 汉字数 < 3 → 双 nan。
    han_log_length = ln(汉字数); 与 redundancy_han 同定义域, 作汉字口径长度控制
    (篇内冗余 TTR 族对长度强机械依赖, 见模块 docstring; 回归用 redundancy_han 时
    须同时控制本列, 同 redundancy_log_length 之于字符版)。

    白话: 和字符版冗余一个意思 (数重复的小片段, 越多越啰嗦), 区别是这版只盯方块
    汉字, 把数字标点英文全扔掉再数 —— 这样"分子分母都是汉字", 口径干净, 也不会
    被一篇里塞满数字/符号撑出来的假重复带偏; 两版一起看互相印证。
    """
    han_str = ''.join(ch for ch in content if is_cjk(ch))
    n_han = len(han_str)
    if n_han < 3:
        return (float('nan'), float('nan'))
    grams = [han_str[i:i + 3] for i in range(n_han - 2)]
    total = len(grams)
    uniq = len(set(grams))
    redundancy = round(1.0 - uniq / total, 6) if total > 0 else float('nan')
    return (redundancy, round(math.log(n_han), 6))


def compute_lexical_complexity(content: str) -> dict[str, float]:
    """对单一文本计算 6+1 个词汇/句法复杂度测度 (单次 posseg pass)。

    Args:
        content: 任意单一文本 (典型 content_full 或 content_ctx)。

    Returns:
        dict: LEXICAL_COMPLEXITY_KEYS 各键 → float (无效/空文本 → nan)。
    """
    if not isinstance(content, str) or not content.strip():
        return _empty_result()
    # 拦截 pandas astype(str) 字符串化 NaN 哨兵 (与 numerical_intensity 同款保护)
    if content.strip() in ('nan', 'NaN', 'None', '<NA>', 'NaT'):
        return _empty_result()

    # ── 单次词性标注 pass (posseg 比 jieba.cut 慢 ~2-3x, 是新测度的必要成本) ──
    # fix(omni-g-numlex jieba-isolation, 2026-06-11): 走独立未注入 posseg 实例,
    # 不再受全局 jieba 注入态影响 (add_word 的 tag='x' 回退会把领域词剔出分母)。
    pairs = [(w, f) for w, f in _get_pristine_posseg().cut(content) if w.strip()]
    real_pairs = [(w, f) for w, f in pairs if f != _PUNCT_FLAG]
    n_real = len(real_pairs)
    if n_real == 0:
        return _empty_result()

    cutoff = _rare_word_cutoff()
    common_chars = _common_char_set()
    freq = _get_pristine_tokenizer().FREQ  # fix(omni-g-numlex jieba-isolation)

    n_rare = 0          # 低频/难词数
    n_nominal = 0       # 名词化 token 数
    n_function = 0      # 功能词 token 数
    n_entity = 0        # 具名实体 + 数词 token 数 (specificity 分子)
    n_adversative = 0   # 逆接连词 token 数
    for w, f in real_pairs:
        # 1) rare_word: 词频 <= cutoff (OOV freq=0 也命中)
        # fix(omni-g-numlex-04, 2026-06-11): 纯数字/纯拉丁 token 不计入分子 —
        # 修前实测分子 26.4% 纯数字 + 3.7% 拉丁, 与词汇难度构念无关 (分母不变)。
        if freq.get(w, 0) <= cutoff and not _NON_LEXICAL_TOKEN_RE.fullmatch(w):
            n_rare += 1
        # 3) nominalization: vn/an 词性 或 名词且以名词化后缀结尾
        if f in _NOMINAL_FLAGS or (f and f[0] == 'n' and w[-1] in _NOMINAL_SUFFIX):
            n_nominal += 1
        # 4) function word: u/p/c/r/y/e 词性前缀
        if f and f[0] in _FUNCTION_FLAG_PREFIXES:
            n_function += 1
        # 5) specificity: 具名实体 (nr/ns/nt/nz) 或"硬"数词
        # fix(omni-g-numlex-06, 2026-06-11): m 词性须过 _is_hard_m_token (排除
        # 一些/许多/若干/几X/数X 等模糊量词 — 构念上属 vague 侧, 不是硬信息)。
        if f in _ENTITY_FLAGS or (f and f[0] == 'm' and _is_hard_m_token(w)):
            n_entity += 1
        # 7) adversative: 命中独立逆接词表
        if w in _ADVERSATIVE_WORDS:
            n_adversative += 1

    # 2) hard_char: 非常用 Han 字 / 全部 Han 字 (分子分母同为汉字口径, is_cjk SSOT)
    han = [ch for ch in content if is_cjk(ch)]
    n_han = len(han)
    if n_han >= _MIN_HAN_CHARS:
        n_hard = sum(1 for ch in han if ch not in common_chars)
        hard_char_ratio = round(n_hard / n_han, 6)
    else:
        hard_char_ratio = float('nan')

    redundancy, redundancy_log_len = _char_trigram_redundancy(content)
    # fix(hanzi-char-dual, 2026-06-13): 汉字口径篇内冗余孪生 (与字符版双口径)
    redundancy_han, redundancy_han_log_len = _han_trigram_redundancy(content)

    return {
        'rare_word_ratio': _safe_div(n_rare, n_real),
        'hard_char_ratio': hard_char_ratio,
        'nominalization_ratio': _safe_div(n_nominal, n_real),
        'function_word_ratio': _safe_div(n_function, n_real),
        'specificity_index': _safe_div(n_entity, n_real),
        'within_doc_redundancy': redundancy,
        # fix(omni-g-numlex-05): redundancy 的 log-length 控制变体 (非比率列)
        'redundancy_log_length': redundancy_log_len,
        # fix(hanzi-char-dual, 2026-06-13): 汉字口径冗余 + 其 log-length 控制 (非比率列)
        'within_doc_redundancy_han': redundancy_han,
        'redundancy_han_log_length': redundancy_han_log_len,
        'adversative_ratio': _safe_div(n_adversative, n_real),
        'n_words_real': float(n_real),  # 词级文章长度 (批 #7, 供 ln_word_count)
        # fix(hanzi-char-dual, 2026-06-13): 汉字级文章长度 (供 ln_han_count); 复用上方
        # hard_char 已算的 n_han (= is_cjk 过滤计数, 定义上 == cn_han_count(content)),
        # 不重复扫描。无标题/正文均 prepend 标题轨, 与 n_words_real 同口径文本。
        # fix(hanzi-char-dual final-audit, 2026-06-13): n_han==0 (零汉字文章, 如纯数字/
        # 拉丁残片) → nan 而非 0.0 —— 否则该文在 avg_han_count 被当有效 0 长度计入分母,
        # 而同文在 avg_within_doc_redund_han 是 nan 被跳过, 造成汉字口径族 bank-year
        # 聚合的零汉字边界 NaN 语义不对称 (顶刊终审 Gap#4)。"无汉字 → 汉字长度不适用"。
        'n_han_real': float(n_han) if n_han > 0 else float('nan'),
    }
