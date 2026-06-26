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


def test_skip_predicate_false_when_recorded_input_deleted(tmp_path, monkeypatch):
    # W5 激活附带的通用安全网: 已记 input_hashes 的文件被删/移动 → 不跳 (旧实现 os.path.exists
    # 为 False 时静默放行, 是 silent-staleness 漏洞)。用 11_news_bank.py 通用路径验证。
    rpf = _orch()
    cfgdir = _seed_skippable(rpf, tmp_path, monkeypatch)
    dep = cfgdir / "upstream.bin"
    dep.write_bytes(b"abc")
    outdir = tmp_path / "out"
    for fn in rpf._get_stage_output_files("11_news_bank.py"):
        dv.save_parquet_with_metadata(
            pd.DataFrame({"x": [1]}), str(outdir / fn), "test", {"k": 1},
            input_files=[str(dep)], config_dir=str(cfgdir),
        )
    assert rpf._stage_skip_unchanged_is_safe("11_news_bank.py")[0] is True   # 基线: 可跳
    dep.unlink()                                                              # 删已记输入
    ok, why = rpf._stage_skip_unchanged_is_safe("11_news_bank.py")
    assert ok is False and "不存在" in why


def test_skip_predicate_false_when_recorded_input_content_changed(tmp_path, monkeypatch):
    # 已记 input_hashes 文件内容变 → 不跳 (内容寻址)。
    rpf = _orch()
    cfgdir = _seed_skippable(rpf, tmp_path, monkeypatch)
    dep = cfgdir / "upstream.bin"
    dep.write_bytes(b"abc")
    outdir = tmp_path / "out"
    for fn in rpf._get_stage_output_files("11_news_bank.py"):
        dv.save_parquet_with_metadata(
            pd.DataFrame({"x": [1]}), str(outdir / fn), "test", {"k": 1},
            input_files=[str(dep)], config_dir=str(cfgdir),
        )
    assert rpf._stage_skip_unchanged_is_safe("11_news_bank.py")[0] is True   # 基线: 可跳
    dep.write_bytes(b"CHANGED")                                              # 改内容
    ok, why = rpf._stage_skip_unchanged_is_safe("11_news_bank.py")
    assert ok is False and "内容已变" in why


# ── W5 激活 (2026-06-26): stage 00 (DAG 根) data_version 元数据 + 原始语料集合门 ──

def _seed_skippable_stage00(rpf, tmp_path, monkeypatch, raw_names=("a.xlsx", "b.xlsx"),
                            code_version=None):
    """造 stage 00 '可跳'基线: tmp config (7 YAML + 资源) + 原始 *.xlsx 语料 + 带 data_version
    元数据 (input_hashes=全量原始 xlsx + code_version) 的产物。返回 (cfgdir, rawdir, outdir)。

    code_version 默认 = 真实 PREPROCESS_CODE_VERSION (使代码版本门通过, 便于测其它门);
    传入 '旧' 值则模拟代码版本漂移。"""
    cfgdir = tmp_path / "config"
    cfgdir.mkdir()
    for fn in dv._SPLIT_YAML_FILES:
        (cfgdir / fn).write_text(f"k_{fn}: v1\n", encoding="utf-8")
    (cfgdir / "dict.json").write_text("[1]", encoding="utf-8")
    rawdir = tmp_path / "raw"
    rawdir.mkdir()
    for nm in raw_names:
        (rawdir / nm).write_bytes(b"xlsx-bytes-" + nm.encode())
    outdir = tmp_path / "out"
    outdir.mkdir()
    monkeypatch.setattr(rpf, "CONFIG_DIR", str(cfgdir))
    monkeypatch.setitem(rpf.CONFIG["paths"], "output_dir", str(outdir))
    monkeypatch.setitem(rpf.CONFIG["paths"], "raw_data_dir", str(rawdir))
    from news_process.pipeline.preprocess._constants import PREPROCESS_CODE_VERSION
    from news_process.pipeline.preprocess.runner import enumerate_raw_xlsx
    cv = code_version if code_version is not None else PREPROCESS_CODE_VERSION
    raw_inputs = enumerate_raw_xlsx(str(rawdir))
    for fn in rpf._get_stage_output_files("00_preprocessing.py"):
        dv.save_parquet_with_metadata(
            pd.DataFrame({"x": [1]}), str(outdir / fn), "00_preprocessing", {"k": 1},
            input_files=raw_inputs, config_dir=str(cfgdir), code_version=cv,
        )
    return cfgdir, rawdir, outdir


def test_stage00_skip_true_when_corpus_unchanged(tmp_path, monkeypatch):
    rpf = _orch()
    _seed_skippable_stage00(rpf, tmp_path, monkeypatch)
    ok, why = rpf._stage_skip_unchanged_is_safe("00_preprocessing.py")
    assert ok is True, why                                  # config/资源/原始语料全未变 → 根阶段可跳


def test_stage00_skip_false_when_corpus_file_added(tmp_path, monkeypatch):
    # 根阶段无上游 → 前缀守卫无从保护; "新增 xlsx" 由集合门检出 (通用 input_hashes 循环看不见新文件)。
    rpf = _orch()
    _, rawdir, _ = _seed_skippable_stage00(rpf, tmp_path, monkeypatch)
    assert rpf._stage_skip_unchanged_is_safe("00_preprocessing.py")[0] is True
    (rawdir / "c.xlsx").write_bytes(b"new-corpus-file")
    ok, why = rpf._stage_skip_unchanged_is_safe("00_preprocessing.py")
    assert ok is False and "新增" in why


def test_stage00_skip_false_when_corpus_file_deleted(tmp_path, monkeypatch):
    rpf = _orch()
    _, rawdir, _ = _seed_skippable_stage00(rpf, tmp_path, monkeypatch)
    assert rpf._stage_skip_unchanged_is_safe("00_preprocessing.py")[0] is True
    next(iter(sorted(rawdir.glob("*.xlsx")))).unlink()       # 删一个已记原始文件
    ok, why = rpf._stage_skip_unchanged_is_safe("00_preprocessing.py")
    assert ok is False and "不存在" in why


def test_stage00_skip_false_when_corpus_content_changed(tmp_path, monkeypatch):
    rpf = _orch()
    _, rawdir, _ = _seed_skippable_stage00(rpf, tmp_path, monkeypatch)
    assert rpf._stage_skip_unchanged_is_safe("00_preprocessing.py")[0] is True
    next(iter(sorted(rawdir.glob("*.xlsx")))).write_bytes(b"CHANGED-CORPUS")  # 改原始文件内容
    ok, why = rpf._stage_skip_unchanged_is_safe("00_preprocessing.py")
    assert ok is False and "内容已变" in why


def test_stage00_raw_input_glob_registry_matches_runner():
    # 漂移守卫: 编排器集合门口径 ((raw_data_dir, *.xlsx)) 与 runner.enumerate_raw_xlsx 一致。
    rpf = _orch()
    assert rpf.STAGE_RAW_INPUT_GLOBS.get("00_preprocessing.py") == ("raw_data_dir", "*.xlsx")
    from news_process.pipeline.preprocess import runner
    assert callable(runner.enumerate_raw_xlsx)


def test_enumerate_raw_xlsx_sorted_abspath_xlsx_only(tmp_path):
    from news_process.pipeline.preprocess.runner import enumerate_raw_xlsx
    (tmp_path / "b.xlsx").write_bytes(b"1")
    (tmp_path / "a.xlsx").write_bytes(b"2")
    (tmp_path / "c.txt").write_bytes(b"3")          # 非 xlsx 不计
    got = enumerate_raw_xlsx(str(tmp_path))
    assert got == sorted(got)                        # 排序 (口径稳定)
    assert all(os.path.isabs(p) for p in got)        # 绝对路径
    assert [os.path.basename(p) for p in got] == ["a.xlsx", "b.xlsx"]


# ── W5 激活的 golden 安全性: 数据列字节不变, 仅多 data_version schema metadata ──

def test_stage00_write_data_bytes_unchanged_only_metadata_added(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq
    cfgdir = tmp_path / "config"
    cfgdir.mkdir()
    for fn in dv._SPLIT_YAML_FILES:
        (cfgdir / fn).write_text("k: v\n", encoding="utf-8")
    df = pd.DataFrame({
        "docid": [1, 2, 3],
        "标题": ["甲", "乙", "丙"],
        "内容": ["x" * 50, "y" * 60, "z" * 70],
        "媒体(中文)": ["人民日报", "新华社", "人民日报"],
        "score": [0.1, float("nan"), 0.3],
    })
    old = tmp_path / "old.parquet"
    new = tmp_path / "new.parquet"
    # OLD = 历史 stage00 裸写 (preserve_index=False + 同款列存参数, 无元数据)
    pq.write_table(
        pa.Table.from_pandas(df, preserve_index=False), str(old),
        compression="snappy", row_group_size=100_000, use_dictionary=True, write_statistics=True,
    )
    # NEW = 经 save_parquet_with_metadata (同款 write 参数 + preserve_index=False)
    dv.save_parquet_with_metadata(
        df, str(new), "00_preprocessing", {"k": 1}, input_files=[], config_dir=str(cfgdir),
        preserve_index=False, compression="snappy", row_group_size=100_000,
        use_dictionary=True, write_statistics=True,
    )
    df_old = pd.read_parquet(old)
    df_new = pd.read_parquet(new)
    pd.testing.assert_frame_equal(df_old, df_new)                  # 数据字节级一致 (含 dtype/NaN)
    for col in df_old.columns:                                     # golden 口径: 逐列内容哈希一致
        h_old = pd.util.hash_pandas_object(df_old[col], index=False).values.tobytes()
        h_new = pd.util.hash_pandas_object(df_new[col], index=False).values.tobytes()
        assert h_old == h_new, col
    assert dv.read_parquet_metadata(old) is None                  # 旧裸写: 无 data_version
    meta = dv.read_parquet_metadata(new)                          # 新写: 多了 data_version
    assert meta and "config_file_hashes" in meta and "resource_hashes" in meta


def test_save_parquet_default_params_backward_compatible(tmp_path):
    # 既有调用方 (不传新 write kwargs) 产物数据字节不变 (默认值 == pyarrow 默认)。
    import pyarrow as pa
    import pyarrow.parquet as pq
    cfgdir = tmp_path / "config"
    cfgdir.mkdir()
    (cfgdir / "paths.yaml").write_text("p: x\n", encoding="utf-8")
    df = pd.DataFrame({"a": [1, 2], "b": ["甲", "乙"], "c": [0.5, float("nan")]})
    ref = tmp_path / "ref.parquet"
    new = tmp_path / "new.parquet"
    pq.write_table(pa.Table.from_pandas(df), str(ref))            # 旧内部行为: from_pandas(df)+裸 write
    dv.save_parquet_with_metadata(                               # 新默认参数调用
        df, str(new), "s", {"k": 1}, input_files=[], config_dir=str(cfgdir),
    )
    pd.testing.assert_frame_equal(pd.read_parquet(ref), pd.read_parquet(new))


# ── 终审 P2 修复: 跳过判据不可读输入 → 保守 (不 abort pipeline) + stage00 代码版本门 ──

def test_skip_predicate_false_when_input_unreadable_not_abort(tmp_path, monkeypatch):
    # P2 (locked-file): 已记输入存在但 compute_file_hash 抛 OSError (Windows 文件被锁) → 判据
    # 必须保守返 False (不跳), 而非让异常冒泡 abort 整条 pipeline。
    rpf = _orch()
    cfgdir = _seed_skippable(rpf, tmp_path, monkeypatch)
    dep = cfgdir / "upstream.bin"
    dep.write_bytes(b"abc")
    outdir = tmp_path / "out"
    for fn in rpf._get_stage_output_files("11_news_bank.py"):
        dv.save_parquet_with_metadata(
            pd.DataFrame({"x": [1]}), str(outdir / fn), "test", {"k": 1},
            input_files=[str(dep)], config_dir=str(cfgdir),
        )
    assert rpf._stage_skip_unchanged_is_safe("11_news_bank.py")[0] is True   # 基线可跳
    real = dv.compute_file_hash
    def _raiser(p):                                              # 只对该 dep 抛, 不影响 config/资源哈希
        if str(p).endswith("upstream.bin"):
            raise PermissionError("locked by Excel/OneDrive")
        return real(p)
    monkeypatch.setattr(dv, "compute_file_hash", _raiser)
    ok, why = rpf._stage_skip_unchanged_is_safe("11_news_bank.py")  # 不得抛异常
    assert ok is False and "无法读取核验" in why


def test_stage00_code_version_recorded_in_metadata(tmp_path, monkeypatch):
    from news_process.pipeline.preprocess._constants import PREPROCESS_CODE_VERSION as CUR
    rpf = _orch()
    _, _, outdir = _seed_skippable_stage00(rpf, tmp_path, monkeypatch)
    for fn in rpf._get_stage_output_files("00_preprocessing.py"):
        meta = dv.read_parquet_metadata(str(outdir / fn))
        assert meta and meta.get("code_version") == CUR          # 元数据落了真实代码版本号


def test_stage00_skip_false_when_code_version_changed(tmp_path, monkeypatch):
    # 改预处理代码逻辑 + bump PREPROCESS_CODE_VERSION 后, 即便 config/语料未变也必须失效根阶段跳过。
    rpf = _orch()
    _seed_skippable_stage00(rpf, tmp_path, monkeypatch, code_version="v0-STALE-CODE")
    ok, why = rpf._stage_skip_unchanged_is_safe("00_preprocessing.py")
    assert ok is False and "代码版本变" in why


def test_stage00_code_version_registry_points_at_real_constant():
    # 漂移守卫: 注册表指向真实存在的 PREPROCESS_CODE_VERSION 常量。
    rpf = _orch()
    spec = rpf.STAGE_CODE_VERSION.get("00_preprocessing.py")
    assert spec == ("news_process.pipeline.preprocess._constants", "PREPROCESS_CODE_VERSION")
    import importlib
    mod = importlib.import_module(spec[0])
    assert isinstance(getattr(mod, spec[1], None), str)          # 常量存在且为字符串
