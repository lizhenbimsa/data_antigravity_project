"""W5: 通用 --skip-unchanged 的 producer 侧内容寻址哈希 + parquet 元数据往返。

测 core/data_versioning 的 compute_config_file_hashes / compute_resource_hashes /
save_parquet_with_metadata 新增字段。纯 CPU / 无 network / 不触生产数据。
编排器侧判据 (_stage_skip_unchanged_is_safe) 由 test_dag_consistency 的洁净加载 +
本文件验证的 helper + 默认关 (不改生产首跑) 共同覆盖。
"""
import pandas as pd

from news_process.core import data_versioning as dv


def test_config_file_hashes_deterministic_and_detect_change(tmp_path):
    cdir = tmp_path / "config"
    cdir.mkdir()
    (cdir / "filtering.yaml").write_text("a: 1\n", encoding="utf-8")
    (cdir / "paths.yaml").write_text("p: x\n", encoding="utf-8")
    h1 = dv.compute_config_file_hashes(cdir)
    assert set(h1) == {"filtering.yaml", "paths.yaml"}
    assert dv.compute_config_file_hashes(cdir) == h1  # 确定性
    (cdir / "filtering.yaml").write_text("a: 2\n", encoding="utf-8")  # 改内容
    h2 = dv.compute_config_file_hashes(cdir)
    assert h2["filtering.yaml"] != h1["filtering.yaml"]  # 变了的检测到
    assert h2["paths.yaml"] == h1["paths.yaml"]  # 未动的不变


def test_resource_hashes_covers_json_txt_not_yaml(tmp_path):
    cdir = tmp_path / "config"
    (cdir / "prompts").mkdir(parents=True)
    (cdir / "bank_keywords.json").write_text('["a"]', encoding="utf-8")
    (cdir / "prompts" / "p.txt").write_text("v", encoding="utf-8")
    (cdir / "filtering.yaml").write_text("a: 1\n", encoding="utf-8")
    res = dv.compute_resource_hashes(cdir)
    assert "bank_keywords.json" in res          # 词典进资源门
    assert "prompts/p.txt" in res               # prompt 进资源门 (POSIX 风格相对路径)
    assert "filtering.yaml" not in res          # YAML 由 config_file_hashes 另管, 不重复
    before = res["bank_keywords.json"]
    (cdir / "bank_keywords.json").write_text('["a","b"]', encoding="utf-8")  # 改词典
    assert dv.compute_resource_hashes(cdir)["bank_keywords.json"] != before  # 资源变检测到


def test_metadata_roundtrip_has_new_fields(tmp_path):
    cdir = tmp_path / "config"
    cdir.mkdir()
    for fn in dv._SPLIT_YAML_FILES:
        (cdir / fn).write_text(f"k_{fn}: v\n", encoding="utf-8")
    (cdir / "dict.json").write_text("[1]", encoding="utf-8")
    out = tmp_path / "stageX.parquet"
    dv.save_parquet_with_metadata(
        pd.DataFrame({"x": [1, 2]}), str(out), "stageX", {"cfg": 1},
        input_files=[], config_dir=str(cdir),
    )
    meta = dv.read_parquet_metadata(out)
    assert meta is not None
    # W5 新字段写进 schema metadata (非数据列 → golden-safe) 并能读回
    assert "config_file_hashes" in meta and "resource_hashes" in meta
    assert set(meta["config_file_hashes"]) == set(dv._SPLIT_YAML_FILES)
    assert meta["resource_hashes"].get("dict.json")


# ── F5 (2026-06-26): consumer 侧判据 _stage_skip_unchanged_is_safe + CLI + 前缀守卫覆盖 ──
# (验证报告 F5: 此前只测 producer helper, 误跳防护逻辑零覆盖)。run_pipeline_function 是根级
# 脚本 (非包模块), 用 importlib 加载 (同 tests/integration/test_dag_consistency.py 手法)。
import importlib.util  # noqa: E402
import os  # noqa: E402

_ORCH = None


def _orch():
    global _ORCH
    if _ORCH is None:
        import news_process
        root = os.path.dirname(os.path.dirname(os.path.abspath(news_process.__file__)))
        path = os.path.join(root, "news_process", "run_pipeline_function.py")
        spec = importlib.util.spec_from_file_location("_w5test_rpf", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _ORCH = mod
    return _ORCH


def test_skip_unchanged_cli_default_false():
    rpf = _orch()
    assert rpf._parse_cli_args([]).skip_unchanged is False          # 默认关
    assert rpf._parse_cli_args(["--skip-unchanged"]).skip_unchanged is True


def test_run_pipeline_default_namespace_has_skip_unchanged():
    # CF-2: args=None 默认 Namespace 必含 skip_unchanged=False (否则 10+ 无参 run_pipeline 调用方 AttributeError)。
    import inspect
    import re
    src = inspect.getsource(_orch().run_pipeline)
    # V2-1: 容空格的正则 + 锚定在 argparse.Namespace(...) 构造段 (比裸子串匹配鲁棒, 不易假通过)。
    assert re.search(r"argparse\.Namespace\([^)]*skip_unchanged\s*=\s*False", src), \
        "run_pipeline 的 args is None 默认 Namespace 必含 skip_unchanged=False (CF-2)"


def test_skip_predicate_false_when_output_missing(tmp_path, monkeypatch):
    rpf = _orch()
    monkeypatch.setitem(rpf.CONFIG["paths"], "output_dir", str(tmp_path))   # 空目录 → 产物不存在
    ok, _ = rpf._stage_skip_unchanged_is_safe("11_news_bank.py")
    assert ok is False                                              # 保守: 产物缺失不跳


def test_skip_predicate_false_for_no_output_stage(tmp_path, monkeypatch):
    from news_process.core.schemas import EXPECTED_NO_OUTPUT_STAGES
    rpf = _orch()
    monkeypatch.setitem(rpf.CONFIG["paths"], "output_dir", str(tmp_path))
    no_out = next(iter(EXPECTED_NO_OUTPUT_STAGES))   # 任一无 parquet 产物的 validation/audit 阶段
    ok, _ = rpf._stage_skip_unchanged_is_safe(no_out)
    assert ok is False                               # 无登记产物 → 不参与跳过 (保守)


def test_skip_predicate_false_when_metadata_lacks_hashes(tmp_path, monkeypatch):
    # 产物存在但裸 parquet (无 data_version) → 保守不跳 (= F1 现状 stage00 bare write 的情形)。
    import pyarrow as pa
    import pyarrow.parquet as pq
    rpf = _orch()
    outdir = tmp_path / "out"
    outdir.mkdir()
    monkeypatch.setitem(rpf.CONFIG["paths"], "output_dir", str(outdir))
    outs = rpf._get_stage_output_files("11_news_bank.py")
    assert outs
    for fn in outs:
        pq.write_table(pa.table({"x": [1]}), str(outdir / fn))     # 裸写, 无元数据
    ok, _ = rpf._stage_skip_unchanged_is_safe("11_news_bank.py")
    assert ok is False                                             # 无 config_file_hashes → 保守不跳


def test_skip_predicate_true_when_unchanged(tmp_path, monkeypatch):
    # 正路径: 产物带元数据 + config/资源未变 + 无上游输入 → 可跳。
    rpf = _orch()
    outdir = tmp_path / "out"
    outdir.mkdir()
    monkeypatch.setitem(rpf.CONFIG["paths"], "output_dir", str(outdir))
    outs = rpf._get_stage_output_files("11_news_bank.py")
    for fn in outs:
        dv.save_parquet_with_metadata(
            pd.DataFrame({"x": [1]}), str(outdir / fn), "test", {"k": 1},
            input_files=[], config_dir=rpf.CONFIG_DIR,
        )
    ok, why = rpf._stage_skip_unchanged_is_safe("11_news_bank.py")
    assert ok is True, why                                         # config/资源/无上游输入 均未变 → 可跳


def _seed_skippable(rpf, tmp_path, monkeypatch):
    """造一个'可跳'基线: tmp config 目录 (7 YAML + 1 资源) + 带元数据的产物 (config_dir=tmp)。返回 cfgdir。"""
    cfgdir = tmp_path / "config"
    cfgdir.mkdir()
    for fn in dv._SPLIT_YAML_FILES:
        (cfgdir / fn).write_text(f"k_{fn}: v1\n", encoding="utf-8")
    (cfgdir / "dict.json").write_text("[1]", encoding="utf-8")
    outdir = tmp_path / "out"
    outdir.mkdir()
    monkeypatch.setattr(rpf, "CONFIG_DIR", str(cfgdir))
    monkeypatch.setitem(rpf.CONFIG["paths"], "output_dir", str(outdir))
    for fn in rpf._get_stage_output_files("11_news_bank.py"):
        dv.save_parquet_with_metadata(
            pd.DataFrame({"x": [1]}), str(outdir / fn), "test", {"k": 1},
            input_files=[], config_dir=str(cfgdir),
        )
    return cfgdir


def test_skip_predicate_false_when_config_yaml_changed(tmp_path, monkeypatch):
    # F5/TQ-2 最关键 consumer 负路径: 元数据齐全但 stage 相关 split YAML 内容变 → 不跳。
    rpf = _orch()
    cfgdir = _seed_skippable(rpf, tmp_path, monkeypatch)
    assert rpf._stage_skip_unchanged_is_safe("11_news_bank.py")[0] is True   # 基线: 可跳
    # filtering.yaml ∈ STAGE_CONFIG_FILES['11_news_bank.py'] → 改它必使判据失配
    (cfgdir / "filtering.yaml").write_text("k_filtering.yaml: CHANGED\n", encoding="utf-8")
    ok, why = rpf._stage_skip_unchanged_is_safe("11_news_bank.py")
    assert ok is False and "config" in why                                   # config 文件变 → 不跳


def test_skip_predicate_false_when_resource_changed(tmp_path, monkeypatch):
    # F5/TQ-2: 资源门 — config/ 下资源 (词典/anchor) 内容变 → 不跳 (防"改词典却被错跳")。
    rpf = _orch()
    cfgdir = _seed_skippable(rpf, tmp_path, monkeypatch)
    assert rpf._stage_skip_unchanged_is_safe("11_news_bank.py")[0] is True   # 基线: 可跳
    (cfgdir / "dict.json").write_text("[1,2,3]", encoding="utf-8")            # 改资源内容
    ok, why = rpf._stage_skip_unchanged_is_safe("11_news_bank.py")
    assert ok is False and "资源" in why                                      # 资源变 → 不跳
