"""benefit_society_audit_combined (P1.6 + 27c thin shim) 测试。

V2.0 J-L-M 稳健性对齐计划 §3 Phase 1 P1.9 (P1.6 部分)。
仅测 validate-only 路径; 完整 projection 需要 sentence_transformers
(标记为 integration)。
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.features import benefit_society_audit_combined

# ============================================================================
# CLI validate-only
# ============================================================================


class TestCLIValidate:
    def test_validate_only_exits_clean(self) -> None:
        rc = benefit_society_audit_combined.main(["--validate-only"])
        assert rc == 0

    def test_no_args_warns_and_exits_clean(self) -> None:
        """不带输入参数时仅校验 yaml schema; CLI 发警告并退出码 0。"""
        rc = benefit_society_audit_combined.main([])
        assert rc == 0


# ============================================================================
# build_audit_panel (mock embedding 路径) — 纯 Python, 不依赖 sentence_transformers
# ============================================================================


class TestBuildAuditPanelMock:
    def test_length_mismatch_raises(self) -> None:
        df = pd.DataFrame(
            {
                "target_bank": ["a"],
                "year": [2017],
                "标题": ["x"],
                "内容": ["y"],
            }
        )
        emb = np.zeros((3, 8))  # 长度不匹配
        direction = np.zeros(8)
        with pytest.raises(ValueError, match="length mismatch"):
            benefit_society_audit_combined.build_audit_panel(df, emb, direction)


# ============================================================================
# 27c thin shim — 脚本调用形态
# ============================================================================


class TestThinShim:
    def test_27c_shim_is_short(self) -> None:
        """按 CLAUDE.md 不变量, shim 应 ≤30 行。"""
        path = Path(__file__).resolve().parents[1] / "27c_placebo_and_alt_anchor.py"
        # 实际在 news_process 根目录而非 tests 根 — 此处做路径调整
        shim_path = (
            Path(__file__).resolve().parents[1] / "27c_placebo_and_alt_anchor.py"
        )
        if not shim_path.exists():
            # tests 在 news_process/tests/ 下; shim 在 news_process/ 根
            shim_path = Path(__file__).resolve().parent.parent / "27c_placebo_and_alt_anchor.py"
        assert shim_path.exists(), f"shim not found: {shim_path}"
        # CLAUDE.md 硬上限: ≤30 行
        with open(shim_path, encoding="utf-8") as f:
            nlines = sum(1 for _ in f)
        assert nlines <= 30, f"27c shim has {nlines} lines > 30 cap"

    def test_27c_shim_imports_main_only(self) -> None:
        """shim 应仅含"导入并转发"模式 (无业务逻辑)。"""
        shim_path = (
            Path(__file__).resolve().parent.parent / "27c_placebo_and_alt_anchor.py"
        )
        text = shim_path.read_text(encoding="utf-8")
        # 必须从 pipeline.features.benefit_society_audit_combined 导入 main
        assert (
            "from news_process.pipeline.features.benefit_society_audit_combined import main"
            in text
        )
        # 必须在 __main__ guard 下调用 sys.exit(main())
        assert "sys.exit(main())" in text


# ============================================================================
# write_sidecar_json
# ============================================================================


class TestSidecarJSON:
    def test_sidecar_json_written(self, tmp_path) -> None:
        panel_path = tmp_path / "audit_panel.parquet"
        # 不实际写 parquet; 只验证 sidecar.json
        meta = {
            "alt_anchor_yaml_sha256": "abc",
            "placebo_keyword_yaml_sha256": "def",
            "placebo_match_counts": {"housing": 100},
        }
        sidecar = benefit_society_audit_combined.write_sidecar_json(panel_path, meta)
        assert sidecar.exists()
        assert sidecar.name == "audit_panel.sidecar.json"
        import json

        loaded = json.loads(sidecar.read_text(encoding="utf-8"))
        assert loaded["alt_anchor_yaml_sha256"] == "abc"
        assert loaded["placebo_match_counts"]["housing"] == 100


# ============================================================================
# quality-hardening Round 50 (2026-05-27): coverage 61.19% → ≥90%
# 补 _repo_root (line 56) + build_audit_panel happy path (92-134) +
# main() 全输入路径 (213-231) — mock sentence_transformers 重依赖
# ============================================================================


def test_repo_root_returns_news_process_parent():
    """_repo_root 返回 parents[3] = repo 根目录 (line 56)."""
    from news_process.pipeline.features.benefit_society_audit_combined import _repo_root
    root = _repo_root()
    # _repo_root 是 Path(__file__).resolve().parents[3]
    # benefit_society_audit_combined.py 在 news_process/pipeline/features/
    # parents[0]=features, [1]=pipeline, [2]=news_process, [3]=repo root
    # 因此返回的应该是 repo 根 (含 news_process 子目录)
    assert (root / 'news_process').is_dir() or (root / 'pyproject.toml').exists()


def test_build_audit_panel_happy_path_mocked(tmp_path, monkeypatch):
    """build_audit_panel mock 重依赖跑通完整流程 (lines 92-134)."""
    from unittest.mock import MagicMock, patch

    import news_process.pipeline.features.benefit_society_audit_combined as mod

    # 合成 3 行 article-bank
    df = pd.DataFrame({
        'target_bank': ['A', 'A', 'B'],
        'year': [2018, 2019, 2018],
        '标题': ['n1', 'n2', 'n3'],
        '内容': ['x', 'y', 'z'],
    })
    n = 3
    emb_dim = 8
    text_embeddings = np.random.RandomState(42).randn(n, emb_dim).astype(np.float32)
    main_direction = np.random.RandomState(43).randn(emb_dim).astype(np.float32)

    # Mock SentenceTransformer 构造器 + encode
    fake_st = MagicMock()
    fake_st.encode = lambda texts, show_progress_bar=False: np.zeros(
        (len(texts), emb_dim), dtype=np.float32)
    with patch('sentence_transformers.SentenceTransformer',
               return_value=fake_st):
        # Mock 各 helper 以跳过 yaml IO (使用伪造锚点/关键词)
        fake_pos = ['pos1', 'pos2']
        fake_neg = ['neg1', 'neg2']
        fake_alt_meta = {'yaml_sha256': 'fakealtanchor'}
        with patch.object(mod, 'load_jlm_zh_anchors',
                           return_value=(fake_pos, fake_neg, fake_alt_meta)):
            # _alt_direction 返回单位向量
            with patch.object(mod, '_alt_direction',
                               return_value=np.ones(emb_dim, dtype=np.float32)):
                # _alt_project 返回得分数组
                with patch.object(mod, '_alt_project',
                                   return_value=np.array([0.1, 0.2, 0.3])):
                    # _alt_aggregate 返回最小 panel
                    alt_panel = pd.DataFrame({
                        'target_bank': ['A', 'B'],
                        'year': [2018, 2018],
                        'benefit_jlm_zh_mean': [0.1, 0.3],
                    })
                    with patch.object(mod, '_alt_aggregate',
                                       return_value=alt_panel):
                        # placebo 相关 helper
                        fake_placebo_meta = {'yaml_sha256': 'fakeplacebo'}
                        with patch.object(
                                mod, 'load_placebo_keywords',
                                return_value=({'housing': ['kw1']},
                                              {'neutral': ['kw2']},
                                              fake_placebo_meta)):
                            placebo_panel = pd.DataFrame({
                                'target_bank': ['A', 'B'],
                                'year': [2018, 2018],
                                'benefit_placebo_housing_mean': [0.5, 0.6],
                            })
                            with patch.object(
                                    mod, 'compute_placebo_projection',
                                    return_value=(placebo_panel,
                                                  {'housing': 10})):
                                combined, meta = mod.build_audit_panel(
                                    df, text_embeddings, main_direction)
    assert isinstance(combined, pd.DataFrame)
    assert 'benefit_jlm_zh_mean' in combined.columns
    assert 'benefit_placebo_housing_mean' in combined.columns
    assert meta['alt_anchor_yaml_sha256'] == 'fakealtanchor'
    assert meta['placebo_keyword_yaml_sha256'] == 'fakeplacebo'
    assert meta['n_articles_total'] == n
    assert meta['embedding_dim'] == emb_dim


def _write_emb_with_sidecar(path, emb, model_id='text-embedding-3-small'):
    """fix(omni-g-benefit-01, 2026-06-11): 测试 helper — 写 .npy + 必备 sidecar."""
    import json
    np.save(path, emb)
    with open(f"{path}.sidecar.json", 'w', encoding='utf-8') as f:
        json.dump({
            'model_id': model_id,
            'n_rows': int(emb.shape[0]),
            'dim': int(emb.shape[1]),
        }, f)


def test_main_full_args_writes_panel_and_sidecar(tmp_path, monkeypatch):
    """main() 带全部输入参数 → 跑通到 write parquet + sidecar。

    旧行为断言更新注明 (fix(omni-g-benefit-01, 2026-06-11)): 输入 .npy 现要求
    sibling .sidecar.json (model_id/n_rows) — 无 sidecar 的陈旧 npy fail-loud;
    fixture 据此补 sidecar。
    """
    from unittest.mock import patch

    import news_process.pipeline.features.benefit_society_audit_combined as mod

    # 写 fixture files (.npy + sidecar)
    emb = np.zeros((2, 8), dtype=np.float32)
    df_exp = pd.DataFrame({
        'target_bank': ['A', 'B'],
        'year': [2018, 2018],
        '标题': ['x', 'y'],
        '内容': ['x', 'y'],
    })
    direction = np.zeros(8, dtype=np.float32)
    emb_path = tmp_path / 'emb.npy'
    df_path = tmp_path / 'df.parquet'
    dir_path = tmp_path / 'dir.npy'
    out_path = tmp_path / 'out' / 'panel.parquet'
    _write_emb_with_sidecar(emb_path, emb)
    df_exp.to_parquet(df_path)
    np.save(dir_path, direction)

    # mock build_audit_panel 返回 (panel, meta)
    fake_panel = pd.DataFrame({
        'target_bank': ['A', 'B'],
        'year': [2018, 2018],
        'metric': [0.1, 0.2],
    })
    fake_meta = {'alt_anchor_yaml_sha256': 'abc',
                  'placebo_keyword_yaml_sha256': 'def',
                  'placebo_match_counts': {},
                  'n_articles_total': 2}
    with patch.object(mod, 'build_audit_panel',
                       return_value=(fake_panel, fake_meta)):
        rc = mod.main([
            '--text-embeddings-full', str(emb_path),
            '--df-exploded', str(df_path),
            '--main-direction-npy', str(dir_path),
            '--output', str(out_path),
        ])
    assert rc == 0
    assert out_path.exists()
    sidecar = out_path.with_suffix('.sidecar.json')
    assert sidecar.exists()
