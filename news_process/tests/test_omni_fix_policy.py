"""test_omni_fix_policy — g-policy 组 omni 审计修复回归锁 (2026-06-11).

锁定 5 条 finding 的修复后行为 (mock 外部 API, 合成语料/DataFrame, 不触网):
  - g-policy-01: 权威语料对称清洗 (与新闻侧 normalize 步骤 2.5 同规则删领导人姓名)
  - g-policy-02: vintage-aware 政策锚点 (stage 15 + 26, 前视守卫: 年度 t 只用 ≤t 文档)
  - g-policy-03: stage 15 文章侧 8191-token 预截断 (后于 2026-06-12 选项 B 移除 —
    引擎 chunk+pool 接管, 两侧对称; 本组测试改锁 "无预截断" 行为)
  - g-policy-04: 注释/docstring 漂移修复 (8000 字截断 / 4 种算法 / 0~1 / legacy 标注)
  - g-policy-05: 降级透明 (<3 银行 warning; t2v 稳健轨 raise 不炸 canonical)

# 白话: "政策契合度"是看文章和官方政策文件像不像。这组测试守住: 政策文件和
# 新闻要用同一套清洗规则(领导人姓名两边都删); 算某年文章的契合度只能用该年
# 及更早发布的政策文件(不许拿 2021 年的文件去评 2016 年的文章); 超长文章
# 不再预先砍断, 交给引擎分块平均; 稳健性备用轨失败时只把自己置空, 不连累
# 主结果; 各种跳过和降级都要在日志里讲明。
"""
from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.fast


# ---------------------------------------------------------------------------
# 共用 fixture / helper
# ---------------------------------------------------------------------------

_SYN_CORPUS = """# 说明注释行 (应被剥离)
# [VINTAGE 2015] doc A — 测试标注
DOCA2015 金融科技 政策文本 甲

# [VINTAGE 2021] doc B — 测试标注
DOCB2021 金融科技 政策文本 乙
"""


def _write_corpus(tmp_path, content=_SYN_CORPUS, name='corpus.txt'):
    p = tmp_path / name
    p.write_text(content, encoding='utf-8')
    return str(p)


def _fake_embed_axis(texts, spec, **kwargs):
    """确定性 mock: doc A → e1, doc B → e2, 文章 → e1 (与 doc A 完全对齐)。"""
    out = []
    for t in texts:
        if 'DOCA2015' in t:
            out.append([1.0, 0.0])
        elif 'DOCB2021' in t:
            out.append([0.0, 1.0])
        else:
            out.append([1.0, 0.0])
    return np.array(out, dtype=np.float32)


def _patch_stage15_tokenizers(monkeypatch, pa):
    monkeypatch.setattr(pa, '_count_tokens', lambda t: 10)
    monkeypatch.setattr(pa, '_truncate_to_max_tokens', lambda t, m=None: t)
    monkeypatch.setattr(pa, '_split_into_chunks', lambda t, m=None: [t])


def _toy_articles(years):
    n = len(years)
    return pd.DataFrame({
        '标题': [f't{i}' for i in range(n)],
        '内容': [f'内容 文章 {i}' for i in range(n)],
        'content_ctx': [f'ctx 文章 {i}' for i in range(n)],
        'year': years,
    })


# ---------------------------------------------------------------------------
# g-policy-01: 对称清洗
# ---------------------------------------------------------------------------

def test_loader_strips_leader_names_symmetric_with_news_side(tmp_path):
    """语料侧应用与 preprocess/normalize 步骤 2.5 相同的领导人姓名删除。"""
    from news_process.pipeline.filtering import policy_alignment as pa
    corpus = (
        "# [VINTAGE 2019] doc\n"
        "习近平主席强调 金融科技 健康发展 习近平\n"
    )
    docs = pa.load_policy_corpus_docs(_write_corpus(tmp_path, corpus))
    assert len(docs) == 1
    assert '习近平' not in docs[0]['text'], "语料侧未对称删除领导人姓名"
    # 删除是 replace 级 (残句保留), 与新闻侧 normalize 完全同规则
    assert '主席强调' in docs[0]['text']


def test_real_corpus_loads_clean_and_fully_dated():
    """真实语料: 6 份文档全部解析出年份, 且加载文本无领导人姓名 (盘上原文含 6 处)。"""
    import os

    from news_process.pipeline.filtering import policy_alignment as pa
    auth_path = pa.CONFIG['paths'].get('authoritative_corpus_file', '')
    if not auth_path or not os.path.exists(auth_path):
        pytest.skip(f"auth corpus 不存在: {auth_path}")
    docs = pa.load_policy_corpus_docs(auth_path)
    assert len(docs) == 6, f"真实语料应切为 6 份文档, 实得 {len(docs)}"
    years = sorted(d['year'] for d in docs)
    assert years == [2015, 2019, 2021, 2022, 2024, 2025], years
    assert not any(d['year_imputed'] for d in docs), "真实语料不应有 impute 年份"
    assert not any('习近平' in d['text'] for d in docs), "对称清洗未生效"


# ---------------------------------------------------------------------------
# g-policy-02: vintage 解析 (标注 / 回退正则 / impute / 全未知)
# ---------------------------------------------------------------------------

def test_loader_fallback_date_line_and_docno(tmp_path):
    """无 VINTAGE 标注时: ≥3 连续空行切分 + 落款日期行 / 文号〔YYYY〕N号 解析。"""
    from news_process.pipeline.filtering import policy_alignment as pa
    corpus = (
        "某政策规划文件甲\n"
        "　　2019 年 8 月\n"
        "正文内容甲\n"
        "\n\n\n\n"
        "某指导意见乙\n"
        "正文内容乙 依据 银发〔2015〕221号 印发\n"
    )
    docs = pa.load_policy_corpus_docs(_write_corpus(tmp_path, corpus))
    assert [d['year'] for d in docs] == [2019, 2015]
    assert not any(d['year_imputed'] for d in docs)


def test_loader_imputes_earliest_year_with_disclosure(tmp_path, monkeypatch):
    """master 设计决定: 解析不出年份的文档默认归最早年 + warning 披露。"""
    from news_process.pipeline.filtering import policy_alignment as pa
    mock_logger = MagicMock()
    monkeypatch.setattr(pa, 'logger', mock_logger)
    corpus = (
        "# [VINTAGE 2021] doc A\n"
        "DOCA 正文\n"
        "\n\n\n\n"
        "无任何年份线索的文档\n"
    )
    docs = pa.load_policy_corpus_docs(_write_corpus(tmp_path, corpus))
    assert [d['year'] for d in docs] == [2021, 2021]
    assert docs[1]['year_imputed'] is True
    warn_msgs = ' '.join(str(c.args[0]) for c in mock_logger.warning.call_args_list)
    assert '无法解析发布年份' in warn_msgs, "缺 impute 披露 warning"


def test_loader_all_years_unknown_returns_none(tmp_path):
    """全语料无任何可解析年份 → year 全 None (消费方降级静态锚点)。"""
    from news_process.pipeline.filtering import policy_alignment as pa
    docs = pa.load_policy_corpus_docs(
        _write_corpus(tmp_path, "无年份文档一\n\n\n\n\n无年份文档二\n"))
    assert len(docs) == 2
    assert all(d['year'] is None for d in docs)


def test_vintage_anchor_text_leq_year_only(tmp_path):
    """vintage_anchor_text: 仅拼接发布年份 ≤ year 的文档; 无可用文档 → None。"""
    from news_process.pipeline.filtering import policy_alignment as pa
    docs = pa.load_policy_corpus_docs(_write_corpus(tmp_path))
    assert pa.vintage_anchor_text(docs, 2014) is None
    a2016 = pa.vintage_anchor_text(docs, 2016)
    assert 'DOCA2015' in a2016 and 'DOCB2021' not in a2016
    a2022 = pa.vintage_anchor_text(docs, 2022)
    assert 'DOCA2015' in a2022 and 'DOCB2021' in a2022


# ---------------------------------------------------------------------------
# g-policy-02: stage 15 前视守卫 (行为级)
# ---------------------------------------------------------------------------

def test_stage15_vintage_lookahead_guard(tmp_path, monkeypatch):
    """年度 t 只与 ≤t 锚点算余弦: 2016→cos=1 (仅 doc A); 2022→cos=1/√2 (A+B 池化);
    2014 (早于全部文档) 与年份未知 → NaN; 全程不因 NaN 崩值域断言。"""
    from news_process.pipeline.filtering import policy_alignment as pa
    monkeypatch.setitem(pa.CONFIG['paths'], 'authoritative_corpus_file',
                        _write_corpus(tmp_path))
    monkeypatch.setattr(pa._eng, 'embed_texts', _fake_embed_axis)
    _patch_stage15_tokenizers(monkeypatch, pa)

    out = pa.compute_article_policy_alignment(
        _toy_articles([2016, 2022, 2014, np.nan]))
    got = out['policy_cosine_sim_full'].tolist()
    assert got[0] == pytest.approx(1.0, abs=1e-6), "2016 应只对 2015 文档锚点"
    assert got[1] == pytest.approx(1 / np.sqrt(2), abs=1e-6), \
        "2022 应对 2015+2021 池化锚点"
    assert np.isnan(got[2]), "2014 早于全部政策文档应 NaN (前视守卫)"
    assert np.isnan(got[3]), "年份未知应 NaN (前视守卫)"
    # t2v 轨同步 vintage (mock 对两 spec 同返回)
    assert out['policy_cosine_sim_t2v_full'].iloc[0] == pytest.approx(1.0, abs=1e-6)
    assert np.isnan(out['policy_cosine_sim_t2v_full'].iloc[2])
    # legacy alias 仍 = _full
    assert out['policy_cosine_sim'].equals(out['policy_cosine_sim_full'])


def test_stage15_year_derived_from_date_column(tmp_path, monkeypatch):
    """无 'year' 列时从 '日期' 派生文章年份 (与 panel/encode 同口径)。"""
    from news_process.pipeline.filtering import policy_alignment as pa
    monkeypatch.setitem(pa.CONFIG['paths'], 'authoritative_corpus_file',
                        _write_corpus(tmp_path))
    monkeypatch.setattr(pa._eng, 'embed_texts', _fake_embed_axis)
    _patch_stage15_tokenizers(monkeypatch, pa)

    df = _toy_articles([2016, 2022]).drop(columns=['year'])
    df['日期'] = ['2016-03-01', '2014-05-02']
    out = pa.compute_article_policy_alignment(df)
    assert out['policy_cosine_sim_full'].iloc[0] == pytest.approx(1.0, abs=1e-6)
    assert np.isnan(out['policy_cosine_sim_full'].iloc[1]), \
        "日期派生 2014 应触发前视守卫 NaN"


def test_stage15_no_year_info_degrades_to_static_with_disclosure(
        tmp_path, monkeypatch):
    """输入缺 year/日期 → 降级静态全语料锚点 (旧行为) 且 warning 显式披露。"""
    from news_process.pipeline.filtering import policy_alignment as pa
    monkeypatch.setitem(pa.CONFIG['paths'], 'authoritative_corpus_file',
                        _write_corpus(tmp_path))
    monkeypatch.setattr(pa._eng, 'embed_texts', _fake_embed_axis)
    _patch_stage15_tokenizers(monkeypatch, pa)
    mock_logger = MagicMock()
    monkeypatch.setattr(pa, 'logger', mock_logger)

    df = _toy_articles([2016, 2022]).drop(columns=['year'])
    out = pa.compute_article_policy_alignment(df)
    # 静态锚点 = (e1+e2)/2 归一 → 所有文章 cos = 1/√2, 无 NaN
    assert out['policy_cosine_sim_full'].notna().all()
    assert np.allclose(out['policy_cosine_sim_full'].to_numpy(),
                       1 / np.sqrt(2), atol=1e-6)
    warn_msgs = ' '.join(str(c.args[0]) for c in mock_logger.warning.call_args_list)
    assert '前视披露' in warn_msgs, "静态降级必须显式披露"


def test_stage15_vintage_optout_uses_static_anchor(tmp_path, monkeypatch):
    """article_alignment.vintage_aware=false → 静态锚点 (稳健性 opt-out) + 披露。"""
    from news_process.pipeline.filtering import policy_alignment as pa
    monkeypatch.setitem(pa.CONFIG['paths'], 'authoritative_corpus_file',
                        _write_corpus(tmp_path))
    monkeypatch.setitem(pa.CONFIG.setdefault('article_alignment', {}),
                        'vintage_aware', False)
    monkeypatch.setattr(pa._eng, 'embed_texts', _fake_embed_axis)
    _patch_stage15_tokenizers(monkeypatch, pa)

    out = pa.compute_article_policy_alignment(_toy_articles([2014]))
    # opt-out 后 2014 不再 NaN (静态锚点含全部文档)
    assert out['policy_cosine_sim_full'].iloc[0] == pytest.approx(
        1 / np.sqrt(2), abs=1e-6)


# ---------------------------------------------------------------------------
# g-policy-05 (b): t2v 稳健轨 raise 不炸 canonical
# ---------------------------------------------------------------------------

def test_stage15_t2v_raise_keeps_canonical(tmp_path, monkeypatch):
    """ROBUSTNESS spec 嵌入 raise (如 embedding_robustness 缺配 → RuntimeError):
    stage 不崩, canonical 列照常产出, 仅 _t2v 置 NaN (契约: 失败不破坏 canonical)。"""
    from news_process.pipeline.filtering import policy_alignment as pa
    monkeypatch.setitem(pa.CONFIG['paths'], 'authoritative_corpus_file',
                        _write_corpus(tmp_path))
    _patch_stage15_tokenizers(monkeypatch, pa)

    def _embed_raise_on_t2v(texts, spec, **kwargs):
        if 'text2vec' in str((spec or {}).get('model', '')):
            raise RuntimeError("Embedding API spec missing base_url or api_key")
        return _fake_embed_axis(texts, spec, **kwargs)

    monkeypatch.setattr(pa._eng, 'embed_texts', _embed_raise_on_t2v)
    out = pa.compute_article_policy_alignment(_toy_articles([2016, 2022]))
    assert out['policy_cosine_sim_full'].notna().all(), "canonical 被稳健轨失败误伤"
    assert out['policy_cosine_sim_t2v_full'].isna().all()
    assert out['policy_cosine_sim_t2v_ctx'].isna().all()


# ---------------------------------------------------------------------------
# stage 26: vintage 锚点 + <3 银行 warning + t2v raise 守卫
# ---------------------------------------------------------------------------

def _toy_df_exploded(years, banks_per_year=3):
    bank_pool = ['工商银行', '建设银行', '中国银行', '农业银行']
    rows = []
    for year in years:
        for i, b in enumerate(bank_pool[:banks_per_year]):
            rows.append({
                'target_bank': b,
                'year': year,
                '标题': f'{b} 金融科技 标题 {year}-{i}',
                '内容': f'{b} 区块链 移动支付 智能风控 数字化转型 {year}-{i} ' * 3,
                'content_ctx': f'{b} 实体上下文 金融科技 段落 {year}-{i} ' * 2,
            })
    return pd.DataFrame(rows)


def _toy_panel(years, banks_per_year=3):
    bank_pool = ['工商银行', '建设银行', '中国银行', '农业银行']
    rows = [{'target_bank': b, 'year': y}
            for y in years for b in bank_pool[:banks_per_year]]
    return pd.DataFrame(rows)


def _fake_embed_rand(texts, spec, **kwargs):
    items = list(texts)
    if not items:
        return None
    rng = np.random.RandomState(42)
    return rng.rand(len(items), 8).astype(np.float32)


def test_stage26_vintage_anchor_per_year_and_lookahead_skip(tmp_path, monkeypatch):
    """stage 26: 各年度幽灵锚点 = vintage_anchor_text(docs, year); 早于全部文档的
    年份整年跳过 (auth_sim_* 经 left-merge 后 NaN) 且 warning 披露。"""
    from news_process.pipeline.features import policy_similarity as ps
    monkeypatch.setitem(ps.CONFIG['paths'], 'authoritative_corpus_file',
                        _write_corpus(tmp_path))
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts', _fake_embed_rand)
    mock_logger = MagicMock()
    monkeypatch.setattr(ps, 'logger', mock_logger)

    anchors_seen = {}
    orig_tfidf = ps._build_tfidf

    def _spy_tfidf(texts, mode):
        # 锚点是 texts_with_auth 最后一个元素; 按其内容归档
        anchors_seen.setdefault(texts[-1], set())
        return orig_tfidf(texts, mode)

    monkeypatch.setattr(ps, '_build_tfidf', _spy_tfidf)

    panel = ps.compute_authoritative_similarity(
        _toy_df_exploded([2014, 2016, 2022]), _toy_panel([2014, 2016, 2022]))

    # 2014: 无 ≤2014 文档 → 跳过 + 披露
    warn_msgs = ' '.join(str(c.args[0]) for c in mock_logger.warning.call_args_list)
    assert '前视守卫' in warn_msgs and '2014' in warn_msgs
    y2014 = panel[panel['year'] == 2014]
    assert y2014['auth_sim_tfidf_c_full'].isna().all(), "2014 应整年 NaN"
    # 2016/2022: 有值
    assert panel[panel['year'] == 2016]['auth_sim_tfidf_c_full'].notna().all()
    assert panel[panel['year'] == 2022]['auth_sim_tfidf_c_full'].notna().all()
    # 锚点逐年不同: 2016 锚仅 doc A; 2022 锚含 A+B
    anchor_texts = list(anchors_seen)
    assert any('DOCA2015' in a and 'DOCB2021' not in a for a in anchor_texts), \
        "缺 2016 年的 ≤2016 锚点 (仅 doc A)"
    assert any('DOCA2015' in a and 'DOCB2021' in a for a in anchor_texts), \
        "缺 2022 年的 ≤2022 锚点 (A+B)"


def test_stage26_lt3_banks_warning(tmp_path, monkeypatch):
    """<3 银行年份: 裸 continue → 显式 warning (镜像 stage 25 同守卫)。"""
    from news_process.pipeline.features import policy_similarity as ps
    monkeypatch.setitem(ps.CONFIG['paths'], 'authoritative_corpus_file',
                        _write_corpus(tmp_path))
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts', _fake_embed_rand)
    mock_logger = MagicMock()
    monkeypatch.setattr(ps, 'logger', mock_logger)

    panel = ps.compute_authoritative_similarity(
        _toy_df_exploded([2020], banks_per_year=2), _toy_panel([2020], 2))
    warn_msgs = ' '.join(str(c.args[0]) for c in mock_logger.warning.call_args_list)
    assert '最低要求 3' in warn_msgs, "稀疏年份跳过必须有日志披露"
    assert 'auth_sim_tfidf_c_full' not in panel.columns or \
        panel['auth_sim_tfidf_c_full'].isna().all()


def test_stage26_t2v_build_emb_raise_guard(tmp_path, monkeypatch):
    """稳健轨 _build_emb raise → 整 stage 不崩; canonical auth_sim_emb_full 有值,
    auth_sim_emb_t2v_full 置 NaN (g-policy-05 契约)。"""
    from news_process.pipeline.features import policy_similarity as ps
    monkeypatch.setitem(ps.CONFIG['paths'], 'authoritative_corpus_file',
                        _write_corpus(tmp_path))
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts', _fake_embed_rand)

    orig_emb = ps._build_emb

    def _emb_raise_on_spec(texts, spec=None):
        if spec is not None:
            raise RuntimeError("Embedding API spec missing base_url or api_key")
        return orig_emb(texts)

    monkeypatch.setattr(ps, '_build_emb', _emb_raise_on_spec)
    panel = ps.compute_authoritative_similarity(
        _toy_df_exploded([2020]), _toy_panel([2020]))
    assert panel['auth_sim_emb_full'].notna().all(), "canonical 被 t2v 失败误伤"
    assert panel['auth_sim_emb_t2v_full'].isna().all(), "t2v 失败应置 NaN"


# ---------------------------------------------------------------------------
# g-policy-03 / 04: 截断披露 + 注释漂移修复 (源码级回归锁, 防静默 revert)
# ---------------------------------------------------------------------------

def test_article_pretruncation_removed_engine_chunkpools():
    """stage 15 (选项 B, 2026-06-12): 文章侧 8191-token 预截断已移除 — 统一引擎
    embed_texts 的朴素分段 (naive chunking) + Mean Pooling 接管超长文章, 两侧 (文章/锚点)
    对称 (镜像 stage 27 omni-g-benefit-04)。源码级回归锁: 防静默 revert 回预截断。"""
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    src = inspect.getsource(pa.compute_article_policy_alignment)
    # 主流程不得再调用预截断 (注释里提及 'omni-g-policy-03'/'选项 B' 等字样不算)
    body = src.replace('omni-g-policy-03', '').replace('选项 B', '')
    assert '_truncate_to_max_tokens(' not in body, \
        "文章侧不得恢复 8191-token 预截断 (选项 B: 引擎 chunk+pool 接管)"
    # 全文直送引擎 (传 full_texts / ctx_texts, 非预截断版本)
    assert 'full_texts, ctx_texts' in src, \
        "应把全文 full_texts/ctx_texts 直送 _cosine_for_spec (两侧对称)"
    # 口径变更披露在位 (显式 supersede 旧的 omni-g-policy-03 截断决定)
    assert 'omni-g-policy-03' in src, "缺 supersede omni-g-policy-03 的口径变更披露"
    assert 'supersede' in src.lower(), "口径变更应显式标 supersede (防误读为新增)"
    assert 't[:8000]' not in src, "陈旧的 stage 25 字符级截断表述应已移除"


def test_long_article_reaches_engine_untruncated(monkeypatch):
    """行为级回归锁 (选项 B): 一篇 >8191 cl100k token 的文章, 送入统一引擎
    embed_texts 前**逐字不得被截断** (chunk+pool 由引擎负责)。

    补强源码级锁 test_article_pretruncation_removed_engine_chunkpools 的盲区:
    源码字符串匹配挡不住"换写法重新截断"(改函数名 / 内联 decode(encode[:N]) /
    新 helper) 的假阴性 — 本测试捕获**真实送入引擎的文本**, 任何形式的预截断都会
    使长文本变短而被逮到。镜像 stage 27 test_omni_fix_benefit.TestNoPretruncation。"""
    import os

    from news_process.pipeline.filtering import policy_alignment as pa

    auth_path = pa.CONFIG['paths'].get('authoritative_corpus_file', '')
    if not os.path.exists(auth_path):
        pytest.skip(f"auth corpus not found: {auth_path}")

    long_text = '银行金融科技数字化转型' * 1500  # 远超 8191 cl100k tokens
    df = pd.DataFrame({
        '标题': ['标题'],
        '内容': [long_text],
        'content_ctx': ['工行 ctx'],
        'year': [2017],
    })

    calls: list[list[str]] = []

    def _capture_embed(texts, spec, **kwargs):
        texts = list(texts)
        calls.append(texts)
        return np.array([[1.0] + [0.0] * 1535] * len(texts), dtype=np.float32)

    # 捕获所有送入引擎的文本 (full / ctx / auth 各轨 × MAIN/ROBUSTNESS spec)
    monkeypatch.setattr(pa._eng, 'embed_texts', _capture_embed)

    pa.compute_article_policy_alignment(df)

    flat = [t for call in calls for t in call]
    article_texts = [t for t in flat if '银行金融科技数字化转型' in t]
    assert article_texts, "未捕获到 full 轨文章文本送入引擎 (调用链异常)"
    # 整篇 long_text 必须逐字出现在送入引擎的文本中 (预截断会让它变短/截尾)
    assert any(long_text in t for t in article_texts), \
        "长文章送引擎前被截断 (选项 B 违规: 预截断复活, 含任意换写法绕过)"


def test_legacy_embeddings_fn_marked_test_only():
    """_get_embeddings_api_dynamic 应显式标注为 legacy/test-only (生产 0 调用)。"""
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    doc = inspect.getdoc(pa._get_embeddings_api_dynamic) or ''
    assert 'LEGACY' in doc and 'test' in doc.lower(), \
        "_get_embeddings_api_dynamic 缺 legacy test-only 标注"
    # 生产主路径不调用它
    src = inspect.getsource(pa.compute_article_policy_alignment)
    assert '_get_embeddings_api_dynamic' not in src
    src_spec = inspect.getsource(pa._cosine_for_spec)
    assert '_get_embeddings_api_dynamic' not in src_spec
    assert '_eng.embed_texts' in src_spec


def test_policy_similarity_docstring_drift_fixed():
    """stage 26 模块 docstring: '4 种算法' → 5 指标; '相同的 8000 字截断' 事实陈述
    已被 token 分段+池化口径替换; vintage 语义已写入。"""
    from news_process.pipeline.features import policy_similarity as ps
    doc = ps.__doc__ or ''
    assert '4 种算法' not in doc, "'4 种算法' 与实产 5 指标不符, 应已修"
    assert '5 个相似度指标' in doc
    assert 'token 分段' in doc, "应描述现行 token 分段+均值池化口径"
    assert 'vintage' in doc.lower() or '发布年份' in doc


def test_stage15_cosine_range_wording_fixed():
    """stage 15 白话段值域表述: 理论值域 [-1, 1] (旧 '0~1 的分数' 已纠偏)。"""
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    doc = inspect.getdoc(pa.compute_article_policy_alignment) or ''
    assert '[-1, 1]' in doc
    assert '打一个 0~1 的分数' not in doc


def test_stage15_value_assertions_nan_safe():
    """vintage NaN 合法值不应触发值域断言假崩 (nanmin/nanmax + 全 NaN continue)。"""
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    src = inspect.getsource(pa.compute_article_policy_alignment)
    assert 'np.nanmin' in src and 'np.nanmax' in src, \
        "值域断言必须 NaN-安全 (vintage 守卫产生合法 NaN)"
