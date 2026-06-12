"""benefit_society_alt_anchor (A2 备择锚点族) 测试。

V2.0 J-L-M 稳健性对齐计划 §3 Phase 1 P1.9 (A2 部分)。
使用 MOCK embedding 函数 — 不加载 shibing624 模型 (CI 安全)。
"""

from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.features.benefit_society_alt_anchor import (
    aggregate_to_bank_year,
    compute_direction_vector,
    load_jlm_zh_anchors,
    project_texts,
)

# ============================================================================
# load_jlm_zh_anchors
# ============================================================================


class TestLoadAnchors:
    def test_default_yaml_loads_with_5_pairs(self) -> None:
        """默认路径加载 yaml, 严格 5 对 (J-L-M canonical)."""
        pos, neg, meta = load_jlm_zh_anchors()
        assert len(pos) == 5
        assert len(neg) == 5
        assert meta["n_pairs"] == 5
        assert meta["anchor_family"] == "jlm_zh_v1"

    def test_first_pair_is_jlm_canonical(self) -> None:
        """第 1 对 = J-L-M Appendix A 原文 verbatim."""
        pos, neg, _ = load_jlm_zh_anchors()
        assert pos[0] == "金融服务有益社会"
        assert neg[0] == "金融服务损害社会"

    def test_pair5_preserves_appendix_typo(self) -> None:
        """V2.E37: pair 5 负面句保留 Appendix typo '金融' (本应 '经济')."""
        pos, neg, _ = load_jlm_zh_anchors()
        assert pos[4] == "金融系统帮助经济"
        # 按可复现性要求, 刻意不纠正 Appendix 原文 typo
        assert neg[4] == "金融系统有害金融"

    def test_sha256_stable(self) -> None:
        """SHA-256 hash 与 yaml 字节内容绑定; 测试时锁定值."""
        _, _, meta = load_jlm_zh_anchors()
        sha = meta["yaml_sha256"]
        assert isinstance(sha, str)
        assert len(sha) == 64  # SHA-256 hex
        # 若有意修改 yaml 内容, 需同步更新此期望 hash
        # Round 9 V2.E37 修正版: yaml comments 重写 (澄清"不同研究问题"非"项目扩展")
        # 2026-06-12 注释审计: yaml 注释英译中 (锚点句/键值逐位未动, safe_load 与改前
        # 递归相等), 按上行指引同步更新期望 hash。
        assert sha == "0e35d996917c8910bd9f6293cf920e2898438bd0fd225ab5957ad3f1acb57c4d"

    def test_missing_yaml_raises(self, tmp_path) -> None:
        """yaml 不存在 → FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="UA-3"):
            load_jlm_zh_anchors(tmp_path / "nonexistent.yaml")

    def test_invalid_n_pairs_raises(self, tmp_path) -> None:
        """n_pairs != 5 → ValueError (违反 J-L-M 规范方法论的锚点对数)。"""
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text(
            "schema_version: '1.0'\n"
            "anchor_family: 'bad'\n"
            "n_pairs: 3\n"
            "pairs:\n"
            "  - {id: 1, positive: 'a', negative: 'b'}\n"
            "  - {id: 2, positive: 'c', negative: 'd'}\n"
            "  - {id: 3, positive: 'e', negative: 'f'}\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="5 anchor pairs"):
            load_jlm_zh_anchors(bad_yaml)


# ============================================================================
# compute_direction_vector
# ============================================================================


def _mock_embedding_fn(d: int = 16):
    """返回确定性 mock embedding 函数 (基于 hash), 仅供测试。"""

    def fn(texts):
        # 基于 hash 的伪确定性 embedding (非真实语义)
        n = len(texts)
        out = np.empty((n, d), dtype=np.float32)
        for i, t in enumerate(texts):
            h = hashlib.sha256(t.encode("utf-8")).digest()
            out[i] = np.frombuffer(h, dtype=np.uint8)[:d].astype(np.float32) / 255.0
        return out

    return fn


class TestComputeDirection:
    def test_direction_is_unit_norm(self) -> None:
        fn = _mock_embedding_fn(d=16)
        pos = ["pos1", "pos2", "pos3"]
        neg = ["neg1", "neg2", "neg3"]
        direction = compute_direction_vector(pos, neg, fn)
        assert direction.shape == (16,)
        assert np.linalg.norm(direction) == pytest.approx(1.0, abs=1e-5)

    def test_anchor_count_mismatch_raises(self) -> None:
        fn = _mock_embedding_fn(d=8)
        with pytest.raises(ValueError, match="Anchor count mismatch"):
            compute_direction_vector(["a", "b"], ["c"], fn)

    def test_degenerate_direction_raises(self) -> None:
        """全部锚点相同 → 退化 (零) 方向向量 → 抛异常。"""

        def constant_fn(texts):
            return np.ones((len(texts), 8), dtype=np.float32)

        with pytest.raises(ValueError, match="Degenerate"):
            compute_direction_vector(["a", "b"], ["c", "d"], constant_fn)

    def test_pair_wise_diff_equivalent_to_mean_then_diff(self) -> None:
        """验证 N4 撤回: 逐对差均值 == 先均值再差 (线性代数恒等)。"""
        fn = _mock_embedding_fn(d=8)
        pos = ["p1", "p2", "p3", "p4", "p5"]
        neg = ["n1", "n2", "n3", "n4", "n5"]
        # 方法 A: mean(pos) - mean(neg) 后归一化 (代码库实现)
        d_a = compute_direction_vector(pos, neg, fn)
        # 方法 B: 逐对差的均值后归一化 (J-L-M 原文表述)
        embeddings = fn(pos + neg)
        n = len(pos)
        pair_diffs = embeddings[:n] - embeddings[n:]
        d_b_raw = pair_diffs.mean(axis=0)
        d_b = d_b_raw / np.linalg.norm(d_b_raw)
        # 两者在浮点误差内应一致
        assert np.allclose(d_a, d_b, atol=1e-6)


# ============================================================================
# project_texts
# ============================================================================


class TestProjectTexts:
    def test_projection_in_cosine_range(self) -> None:
        rng = np.random.default_rng(42)
        embeddings = rng.standard_normal((20, 16)).astype(np.float32)
        direction = rng.standard_normal(16).astype(np.float32)
        direction = direction / np.linalg.norm(direction)
        scores = project_texts(embeddings, direction)
        assert scores.shape == (20,)
        assert scores.dtype == np.float32
        assert np.all(scores >= -1.0 - 1e-5)
        assert np.all(scores <= 1.0 + 1e-5)

    def test_handles_zero_embedding(self) -> None:
        """零范数 embedding → cosine = 0 (而非 NaN)。"""
        embeddings = np.zeros((3, 8), dtype=np.float32)
        embeddings[1] = 1.0  # 一行非零
        direction = np.zeros(8, dtype=np.float32)
        direction[0] = 1.0
        scores = project_texts(embeddings, direction)
        assert not np.isnan(scores).any()

    def test_dimension_mismatch_raises(self) -> None:
        embeddings = np.zeros((3, 8))
        direction = np.zeros(16)
        with pytest.raises(ValueError, match="Dimension mismatch"):
            project_texts(embeddings, direction)


# ============================================================================
# aggregate_to_bank_year
# ============================================================================


class TestAggregateBankYear:
    def test_basic_aggregation(self) -> None:
        df = pd.DataFrame(
            {
                "target_bank": ["bank_a", "bank_a", "bank_b", "bank_b"],
                "year": [2017, 2017, 2017, 2018],
            }
        )
        scores = np.array([0.5, -0.3, 0.8, 0.0], dtype=np.float32)
        agg = aggregate_to_bank_year(df, scores)
        assert len(agg) == 3  # (a, 2017), (b, 2017), (b, 2018)
        a_2017 = agg[(agg["target_bank"] == "bank_a") & (agg["year"] == 2017)].iloc[0]
        assert a_2017["benefit_jlm_zh_mean"] == pytest.approx(0.1, abs=1e-5)
        assert a_2017["benefit_jlm_zh_pos_frac"] == pytest.approx(0.5)
        assert a_2017["benefit_jlm_zh_neg_frac"] == pytest.approx(0.5)

    def test_singleton_std_is_nan(self) -> None:
        """单观测组 std 保持 NaN (fix(omni-g-benefit-05, 2026-06-11)).

        旧行为断言更新注明: 原断言 std==0.0 锁定的是 fillna(0) 缺陷 — 填 0 令
        '只有 1 篇报道'与'多篇完全一致(真实零分歧)'不可区分, 与核心 tone std
        族 (保持 NaN) 口径冲突, 已按组级裁决移除。
        """
        df = pd.DataFrame({"target_bank": ["bank_a"], "year": [2018]})
        scores = np.array([0.5], dtype=np.float32)
        agg = aggregate_to_bank_year(df, scores)
        assert len(agg) == 1
        assert np.isnan(agg.iloc[0]["benefit_jlm_zh_std"])

    def test_length_mismatch_raises(self) -> None:
        df = pd.DataFrame({"target_bank": ["a"], "year": [2017]})
        scores = np.array([0.5, 0.3])
        with pytest.raises(ValueError, match="length mismatch"):
            aggregate_to_bank_year(df, scores)

    def test_nan_scores_dropped(self) -> None:
        df = pd.DataFrame(
            {
                "target_bank": ["a", "a", "a"],
                "year": [2017, 2017, 2017],
            }
        )
        scores = np.array([0.5, np.nan, -0.3], dtype=np.float32)
        agg = aggregate_to_bank_year(df, scores)
        assert len(agg) == 1
        # [0.5, -0.3] 的均值 = 0.1
        assert agg.iloc[0]["benefit_jlm_zh_mean"] == pytest.approx(0.1, abs=1e-5)


# ============================================================================
# CLI 冒烟测试 (validate-only 路径; 不触碰 sentence_transformers)
# ============================================================================


class TestCLIValidate:
    def test_validate_only_exits_clean(self) -> None:
        """--validate-only 不加载模型且退出码 0。"""
        from news_process.pipeline.features import benefit_society_alt_anchor

        rc = benefit_society_alt_anchor.main(["--validate-only"])
        assert rc == 0


# ============================================================================
# quality-hardening Round 52 (2026-05-27): alt_anchor 73.21% → ≥90%
# 补 yaml validation 边界 (82/85/90) + embedding shape (137) + project 2D (167) +
# write_sidecar_json (227-243) + main() full projection branch (307-343)
# ============================================================================


class TestLoadAnchorsValidation:
    def test_pairs_count_not_5_raises(self, tmp_path):
        """pairs 实际长度 != 5 但 n_pairs==5 仍触发 line 82."""
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text(
            "schema_version: '1.0'\nanchor_family: 'bad'\nn_pairs: 5\n"
            "pairs:\n"
            "  - {id: 1, positive: 'a', negative: 'b'}\n"
            "  - {id: 2, positive: 'c', negative: 'd'}\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="Expected 5 pairs"):
            load_jlm_zh_anchors(bad_yaml)

    def test_duplicate_ids_raise(self, tmp_path):
        """重复 id → ValueError (line 85)."""
        bad_yaml = tmp_path / "dup.yaml"
        bad_yaml.write_text(
            "schema_version: '1.0'\nanchor_family: 'bad'\nn_pairs: 5\n"
            "pairs:\n"
            "  - {id: 1, positive: 'a', negative: 'b'}\n"
            "  - {id: 1, positive: 'c', negative: 'd'}\n"
            "  - {id: 3, positive: 'e', negative: 'f'}\n"
            "  - {id: 4, positive: 'g', negative: 'h'}\n"
            "  - {id: 5, positive: 'i', negative: 'j'}\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="Duplicate pair ids"):
            load_jlm_zh_anchors(bad_yaml)

    def test_empty_sentence_raises(self, tmp_path):
        """positive 或 negative 为空 → ValueError (line 90)."""
        bad_yaml = tmp_path / "empty.yaml"
        bad_yaml.write_text(
            "schema_version: '1.0'\nanchor_family: 'bad'\nn_pairs: 5\n"
            "pairs:\n"
            "  - {id: 1, positive: 'a', negative: ''}\n"  # negative 为空
            "  - {id: 2, positive: 'c', negative: 'd'}\n"
            "  - {id: 3, positive: 'e', negative: 'f'}\n"
            "  - {id: 4, positive: 'g', negative: 'h'}\n"
            "  - {id: 5, positive: 'i', negative: 'j'}\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="Empty sentence"):
            load_jlm_zh_anchors(bad_yaml)


def test_compute_direction_embedding_shape_mismatch_raises():
    """embedding_fn 返回错形 shape → ValueError (line 137-139)."""
    def bad_fn(texts):
        # 返回 1D 数组而非 2D
        return np.zeros(len(texts))
    with pytest.raises(ValueError, match="returned shape"):
        compute_direction_vector(["a", "b"], ["c", "d"], bad_fn)


def test_project_texts_requires_2d_embeddings():
    """text_embeddings 是 1D → ValueError (line 167-168)."""
    embeddings = np.zeros(10)  # 1D
    direction = np.zeros(8)
    with pytest.raises(ValueError, match="must be 2D"):
        project_texts(embeddings, direction)


def test_write_sidecar_json(tmp_path):
    """write_sidecar_json 写完整 sidecar (lines 227-243)."""
    from news_process.pipeline.features.benefit_society_alt_anchor import (
        write_sidecar_json,
    )
    panel_path = tmp_path / 'panel.parquet'
    fake_meta = {'yaml_sha256': 'abc', 'anchor_family': 'jlm_zh_v1'}
    out = write_sidecar_json(
        panel_path, fake_meta,
        direction_sha='dir_sha_xyz',
        n_articles=100,
        n_bank_years=50,
    )
    assert out.exists()
    assert out.name == 'panel.sidecar.json'
    import json
    data = json.loads(out.read_text(encoding='utf-8'))
    assert data['anchor_metadata']['yaml_sha256'] == 'abc'
    assert data['direction_vector_sha256'] == 'dir_sha_xyz'
    assert data['n_articles_scored'] == 100
    assert data['n_bank_year_obs'] == 50
    assert data['embedding_dim'] == 768


def test_main_missing_inputs_warns_and_exits_clean():
    """main() 仅有部分 input → warn + return 0 (lines 307-312)."""
    from news_process.pipeline.features import benefit_society_alt_anchor as mod
    # 既没传 text-embeddings 也没传 df-exploded → warning branch
    rc = mod.main([])
    assert rc == 0


def _write_emb_with_sidecar(path, emb, model_id='text-embedding-3-small'):
    """fix(omni-g-benefit-01, 2026-06-11): 测试 helper — 写 .npy + 必备 sidecar."""
    import json
    np.save(path, emb)
    sidecar = {
        'model_id': model_id,
        'n_rows': int(emb.shape[0]),
        'dim': int(emb.shape[1]),
    }
    with open(f"{path}.sidecar.json", 'w', encoding='utf-8') as f:
        json.dump(sidecar, f)


def test_main_full_projection_path(tmp_path, monkeypatch):
    """main() 全输入路径: mock 统一引擎闭包 + 走完整 projection (含 ctx 轨)。

    旧行为断言更新注明 (fix(omni-g-benefit-01, 2026-06-11)): 原测试 mock
    SentenceTransformer("shibing624/...") 直调且 .npy 无 sidecar — 该链路
    已按组级裁决重接线: 锚点经统一引擎 (spec 由 sidecar model_id 反查),
    无 sidecar 的陈旧 .npy fail-loud。
    """
    from unittest.mock import patch

    from news_process.pipeline.features import benefit_society_alt_anchor as mod

    # 准备 fixture 文件 (.npy + sidecar; 维度任意 — 由 sidecar 自描述)
    n = 4
    emb_dim = 16
    emb = np.random.RandomState(0).randn(n, emb_dim).astype(np.float32)
    emb_ctx = np.random.RandomState(2).randn(n, emb_dim).astype(np.float32)
    df = pd.DataFrame({
        'target_bank': ['A'] * n,
        'year': [2018] * n,
    })
    emb_path = tmp_path / 'emb.npy'
    ctx_path = tmp_path / 'emb_ctx.npy'
    df_path = tmp_path / 'df.parquet'
    output_path = tmp_path / 'out' / 'panel.parquet'
    _write_emb_with_sidecar(emb_path, emb)
    _write_emb_with_sidecar(ctx_path, emb_ctx)
    df.to_parquet(df_path)

    # mock 引擎闭包工厂 (不触网、不读 config): 返回确定性锚点嵌入
    def fake_make_fn(spec, **kwargs):
        return lambda texts: np.random.RandomState(1).randn(
            len(list(texts)), emb_dim).astype(np.float32)

    with patch.object(mod, 'resolve_embedding_spec', return_value={'model': 'x'}), \
         patch.object(mod, 'make_anchor_embedding_fn', side_effect=fake_make_fn):
        rc = mod.main([
            '--text-embeddings-full', str(emb_path),
            '--text-embeddings-ctx', str(ctx_path),
            '--df-exploded', str(df_path),
            '--output', str(output_path),
        ])
    assert rc == 0
    assert output_path.exists()
    out = pd.read_parquet(output_path)
    # ctx 轨列 (fix(omni-g-benefit-01): 补 ctx 轨)
    assert 'benefit_jlm_zh_mean' in out.columns
    assert 'benefit_jlm_zh_mean_ctx' in out.columns
    sidecar = output_path.with_suffix('.sidecar.json')
    assert sidecar.exists()
    import json
    meta = json.loads(sidecar.read_text(encoding='utf-8'))
    # sidecar 不再硬编码 shibing624/768 — 反映实际输入
    assert meta['embedding_model'] == 'text-embedding-3-small'
    assert meta['embedding_dim'] == emb_dim
    assert meta['tracks'] == ['full', 'ctx']


def test_main_stale_npy_without_sidecar_fails_loud(tmp_path):
    """无 sidecar 的 .npy (2026-05-09 陈旧产物形态) → fail-loud, 不静默消费
    (fix(omni-g-benefit-01, 2026-06-11))."""
    from news_process.pipeline.features import benefit_society_alt_anchor as mod

    emb_path = tmp_path / 'stale.npy'
    np.save(emb_path, np.zeros((3, 8), dtype=np.float32))  # 故意不写 sidecar
    df_path = tmp_path / 'df.parquet'
    pd.DataFrame({'target_bank': ['A'] * 3, 'year': [2018] * 3}).to_parquet(df_path)

    with pytest.raises(FileNotFoundError, match="sidecar"):
        mod.main([
            '--text-embeddings-full', str(emb_path),
            '--df-exploded', str(df_path),
            '--output', str(tmp_path / 'out.parquet'),
        ])
