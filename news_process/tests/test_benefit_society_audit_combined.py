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

    def test_no_args_warns_and_exits_clean(self, tmp_path, monkeypatch) -> None:
        """不带输入参数 + 上游产物缺失时: 自动接线后存在性检查发现缺失 → 仅校验 yaml,
        CLI 发警告并退出码 0 (warn 回退路径)。

        fix(2026-06-29): main() 现默认经 _resolve_default_inputs 从 config 自动接线
        stage 27/40 规范输入。故 no-args 的 warn 回退须在"上游产物不存在"的隔离环境下
        验证 (否则会接到真实 data/processed 产物并尝试付费嵌入 + 写真实面板)。
        monkeypatch load_config 使 output_dir/log_dir 指向空 tmp 目录 → 解析后文件不存在
        → 命中 warn 回退。
        """
        import news_process.core.config as _cfg

        fake_cfg = {
            "paths": {"output_dir": str(tmp_path), "log_dir": str(tmp_path)},
            "filenames": {},
        }
        monkeypatch.setattr(_cfg, "load_config", lambda *a, **k: fake_cfg)
        rc = benefit_society_audit_combined.main([])
        assert rc == 0


# ============================================================================
# build_audit_panel (mock embedding 路径) — 纯 Python, 不依赖 sentence_transformers
# ============================================================================


# ============================================================================
# _resolve_default_inputs — fix(2026-06-29) 自动接线 stage 27/40 规范输入
# ============================================================================


class TestResolveDefaultInputs:
    def _bare_args(self):
        import argparse

        return argparse.Namespace(
            text_embeddings_full=None,
            text_embeddings_ctx=None,
            text_embeddings_ss=None,
            df_exploded=None,
            main_direction_npy=None,
        )

    def test_fills_required_canonical_paths(self, tmp_path) -> None:
        """必需三件套 (full/df/direction) 无条件接线到 config output_dir 下规范文件名。"""
        import os

        args = self._bare_args()
        cfg = {"paths": {"output_dir": str(tmp_path)}, "filenames": {}}
        benefit_society_audit_combined._resolve_default_inputs(args, cfg)
        assert args.text_embeddings_full == os.path.join(
            str(tmp_path), "27_benefit_embeddings_full.npy"
        )
        assert args.main_direction_npy == os.path.join(
            str(tmp_path), "27_benefit_direction.npy"
        )
        assert args.df_exploded == os.path.join(
            str(tmp_path), "40_article_bank_level.parquet"
        )

    def test_optional_twins_wired_only_when_present(self, tmp_path) -> None:
        """ctx/ss 可选 twin: 默认路径文件存在才接线; 不存在则保持 None。"""
        import os

        # 只造 ctx 默认文件, 不造 ss
        (tmp_path / "27_benefit_embeddings_ctx.npy").write_bytes(b"x")
        args = self._bare_args()
        cfg = {"paths": {"output_dir": str(tmp_path)}, "filenames": {}}
        benefit_society_audit_combined._resolve_default_inputs(args, cfg)
        assert args.text_embeddings_ctx == os.path.join(
            str(tmp_path), "27_benefit_embeddings_ctx.npy"
        )
        assert args.text_embeddings_ss is None  # ss 默认文件不存在 → 不接线

    def test_explicit_paths_preserved(self, tmp_path) -> None:
        """显式传入的 CLI 路径 (非 None) 一律保留, 不被默认值覆盖。"""
        args = self._bare_args()
        args.text_embeddings_full = "EXPLICIT_full.npy"
        args.df_exploded = "EXPLICIT_df.parquet"
        args.main_direction_npy = "EXPLICIT_dir.npy"
        cfg = {"paths": {"output_dir": str(tmp_path)}, "filenames": {}}
        benefit_society_audit_combined._resolve_default_inputs(args, cfg)
        assert args.text_embeddings_full == "EXPLICIT_full.npy"
        assert args.df_exploded == "EXPLICIT_df.parquet"
        assert args.main_direction_npy == "EXPLICIT_dir.npy"

    def test_respects_config_filename_overrides(self, tmp_path) -> None:
        """嵌入基名/df 文件名从 config filenames 派生 (非硬编码)。"""
        import os

        args = self._bare_args()
        cfg = {
            "paths": {"output_dir": str(tmp_path)},
            "filenames": {
                "output_27_benefit_cache": "CUSTOM_emb.npy",
                "output_40_article_bank": "CUSTOM_df.parquet",
            },
        }
        benefit_society_audit_combined._resolve_default_inputs(args, cfg)
        assert args.text_embeddings_full == os.path.join(
            str(tmp_path), "CUSTOM_emb_full.npy"
        )
        assert args.df_exploded == os.path.join(str(tmp_path), "CUSTOM_df.parquet")


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
        path = Path(__file__).resolve().parents[1] / "80_placebo_and_alt_anchor.py"
        # 实际在 news_process 根目录而非 tests 根 — 此处做路径调整
        shim_path = (
            Path(__file__).resolve().parents[1] / "80_placebo_and_alt_anchor.py"
        )
        if not shim_path.exists():
            # tests 在 news_process/tests/ 下; shim 在 news_process/ 根
            shim_path = Path(__file__).resolve().parent.parent / "80_placebo_and_alt_anchor.py"
        assert shim_path.exists(), f"shim not found: {shim_path}"
        # CLAUDE.md 硬上限: ≤30 行
        with open(shim_path, encoding="utf-8") as f:
            nlines = sum(1 for _ in f)
        assert nlines <= 30, f"27c shim has {nlines} lines > 30 cap"

    def test_27c_shim_imports_main_only(self) -> None:
        """shim 应仅含"导入并转发"模式 (无业务逻辑)。"""
        shim_path = (
            Path(__file__).resolve().parent.parent / "80_placebo_and_alt_anchor.py"
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
    from unittest.mock import patch

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

    # v3.14.0 (2026-06-27, all-API): 锚点嵌入改走统一引擎 make_anchor_embedding_fn
    # (embed_texts API 路径), 不再 mock 本地 SentenceTransformer。此处 mock 闭包工厂
    # 返回确定性锚点嵌入闭包 (不触网/不读 config), 并 mock resolve_embedding_spec
    # 避开 config 反查 (与 _alt_direction patch 联用, 闭包实际不被调用)。
    fake_anchor_fn = lambda texts: np.zeros((len(list(texts)), emb_dim), dtype=np.float32)  # noqa: E731
    with patch.object(mod, 'resolve_embedding_spec', return_value={'model': 'x'}), \
         patch.object(mod, 'make_anchor_embedding_fn', return_value=fake_anchor_fn):
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


def _write_emb_with_sidecar(path, emb, model_id='Qwen/Qwen3-Embedding-8B'):
    """fix(omni-g-benefit-01, 2026-06-11): 测试 helper — 写 .npy + 必备 sidecar.

    v3.14.0 (2026-06-27): 默认 model_id 改为 MAIN co-primary Qwen/Qwen3-Embedding-8B
    (旧本地/小模型已整体移除)。
    """
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

    import news_process.core.config as _cfg
    import news_process.pipeline.features.benefit_society_audit_combined as mod

    # fix(2026-06-29): main() 现无条件调 _resolve_default_inputs(args, config) 自动接线省略输入。
    # 本测试只显式传 full/df/direction, 把 ctx/ss 留 None → 若 config.output_dir 指向真实
    # data/processed (含生产 27_benefit_embeddings_ctx/ss.npy), resolver 会接到那两个真实文件,
    # 令测试经 model_id 巧合 green、换模即伪失败 (非 hermetic)。monkeypatch load_config 使
    # output_dir/log_dir 指向 tmp_path (无 canonical ctx/ss 文件) → ctx/ss 保持 None → 恢复隔离。
    monkeypatch.setattr(
        _cfg, "load_config",
        lambda *a, **k: {"paths": {"output_dir": str(tmp_path), "log_dir": str(tmp_path)}, "filenames": {}},
    )

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


def test_no_args_auto_wires_canonical_inputs_and_writes_panel(tmp_path, monkeypatch):
    """fix(2026-06-29) success-path 回归锁: 裸跑 main([]) 在 config output_dir 下
    canonical 输入就绪时, 经 _resolve_default_inputs 自动接线 → 进入投影分支 → 写出
    默认输出面板 (而非命中 warn 回退)。

    这是本次修复的核心行为 (堵住"裸跑空转 warn-exit"原 bug); 隔离地放在 tmp output_dir
    里放 canonical full/df/direction fixture, mock build_audit_panel, 断言裸跑产面板。
    若未来有人写反存在性判据或改坏 resolver, 本锁会失败 (而 warn-回退单测仍绿)。
    """
    from unittest.mock import patch

    import news_process.core.config as _cfg
    import news_process.pipeline.features.benefit_society_audit_combined as mod

    monkeypatch.setattr(
        _cfg, "load_config",
        lambda *a, **k: {"paths": {"output_dir": str(tmp_path), "log_dir": str(tmp_path)}, "filenames": {}},
    )

    # canonical 文件名 (镜像 _resolve_default_inputs 默认): 只放必需三件套, 不放 ctx/ss
    _write_emb_with_sidecar(tmp_path / "27_benefit_embeddings_full.npy", np.zeros((2, 8), dtype=np.float32))
    pd.DataFrame({
        "target_bank": ["A", "B"], "year": [2018, 2018],
        "标题": ["x", "y"], "内容": ["x", "y"],
    }).to_parquet(tmp_path / "40_article_bank_level.parquet")
    np.save(tmp_path / "27_benefit_direction.npy", np.zeros(8, dtype=np.float32))

    fake_panel = pd.DataFrame({"target_bank": ["A"], "year": [2018], "metric": [0.1]})
    fake_meta = {"alt_anchor_yaml_sha256": "a", "placebo_keyword_yaml_sha256": "b",
                 "placebo_match_counts": {}, "n_articles_total": 2}
    with patch.object(mod, "build_audit_panel", return_value=(fake_panel, fake_meta)):
        rc = mod.main([])  # 裸跑 — 无任何 CLI 输入路径

    assert rc == 0
    # 默认输出 = <output_dir>/80_alt_anchor_and_placebo_panel.parquet (未命中 warn 回退)
    default_out = tmp_path / "80_alt_anchor_and_placebo_panel.parquet"
    assert default_out.exists(), "裸跑应自动接线 canonical 输入并写出面板, 而非 warn 空转"
    assert default_out.with_suffix(".sidecar.json").exists()


def test_no_args_auto_wires_ctx_ss_twins_passed_through(tmp_path, monkeypatch):
    """fix(2026-06-29) ctx/ss 端到端锁: canonical full+ctx+ss (同 model_id) 就绪时, 裸跑
    main([]) 经 _resolve_default_inputs 接线三轨 → load_article_embeddings 校验同空间 →
    build_audit_panel 收到**非 None 的 ctx/ss ndarray** (三轨 twin 真端到端透传, 非仅 full)。

    补 Pass-1 评审建议: 此前 ctx/ss 自动接线仅在 _resolve_default_inputs 单测 (路径级) 覆盖,
    main()→load→透传 整条链未锁。
    """
    from unittest.mock import patch

    import news_process.core.config as _cfg
    import news_process.pipeline.features.benefit_society_audit_combined as mod

    monkeypatch.setattr(
        _cfg, "load_config",
        lambda *a, **k: {"paths": {"output_dir": str(tmp_path), "log_dir": str(tmp_path)}, "filenames": {}},
    )

    emb = np.zeros((2, 8), dtype=np.float32)
    # 三轨 fixture 同 model_id (默认 Qwen) → 通过 main() 的同空间校验
    _write_emb_with_sidecar(tmp_path / "27_benefit_embeddings_full.npy", emb)
    _write_emb_with_sidecar(tmp_path / "27_benefit_embeddings_ctx.npy", emb)
    _write_emb_with_sidecar(tmp_path / "27_benefit_embeddings_ss.npy", emb)
    pd.DataFrame({
        "target_bank": ["A", "B"], "year": [2018, 2018],
        "标题": ["x", "y"], "内容": ["x", "y"],
    }).to_parquet(tmp_path / "40_article_bank_level.parquet")
    np.save(tmp_path / "27_benefit_direction.npy", np.zeros(8, dtype=np.float32))

    captured = {}

    def _recording_build(df_exploded, text_embeddings, main_direction, **kwargs):
        captured["ctx"] = kwargs.get("text_embeddings_ctx")
        captured["ss"] = kwargs.get("text_embeddings_ss")
        return (
            pd.DataFrame({"target_bank": ["A"], "year": [2018], "m": [0.1]}),
            {"alt_anchor_yaml_sha256": "a", "placebo_keyword_yaml_sha256": "b",
             "placebo_match_counts": {}, "n_articles_total": 2},
        )

    with patch.object(mod, "build_audit_panel", side_effect=_recording_build):
        rc = mod.main([])

    assert rc == 0
    assert captured["ctx"] is not None and captured["ctx"].shape == (2, 8), "ctx twin 未端到端透传"
    assert captured["ss"] is not None and captured["ss"].shape == (2, 8), "ss twin 未端到端透传"


def test_auto_wired_ctx_model_mismatch_raises(tmp_path, monkeypatch):
    """fix(2026-06-29) 负例锁: auto-wired ctx 轨 model_id 与 full 轨不一致 → main() fail-loud
    ValueError (三轨须同嵌入空间; 镜像 stage 27 落盘陈旧 twin 的半迁移态防护)。"""
    import news_process.core.config as _cfg
    import news_process.pipeline.features.benefit_society_audit_combined as mod

    monkeypatch.setattr(
        _cfg, "load_config",
        lambda *a, **k: {"paths": {"output_dir": str(tmp_path), "log_dir": str(tmp_path)}, "filenames": {}},
    )

    emb = np.zeros((2, 8), dtype=np.float32)
    _write_emb_with_sidecar(tmp_path / "27_benefit_embeddings_full.npy", emb, model_id="Qwen/Qwen3-Embedding-8B")
    _write_emb_with_sidecar(tmp_path / "27_benefit_embeddings_ctx.npy", emb, model_id="STALE-OTHER-MODEL")
    pd.DataFrame({
        "target_bank": ["A", "B"], "year": [2018, 2018],
        "标题": ["x", "y"], "内容": ["x", "y"],
    }).to_parquet(tmp_path / "40_article_bank_level.parquet")
    np.save(tmp_path / "27_benefit_direction.npy", np.zeros(8, dtype=np.float32))

    with pytest.raises(ValueError, match="ctx embeddings model"):
        mod.main([])
