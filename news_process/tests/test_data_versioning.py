import pandas as pd

from news_process.core.data_versioning import (
    DataVersionMetadata,
    compute_file_hash,
    read_parquet_metadata,
    save_parquet_with_metadata,
    verify_data_integrity,
)


def test_data_version_metadata():
    """测试版本元数据创建"""
    config = {"test": "config"}
    metadata = DataVersionMetadata("test_stage", config)

    assert metadata.stage_name == "test_stage"
    assert metadata.config_hash is not None
    assert metadata.git_commit is not None
    assert metadata.timestamp is not None


def test_save_and_read_metadata(tmp_path):
    """测试保存和读取元数据"""
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    output_path = tmp_path / "test.parquet"
    config = {"test": "config"}

    save_parquet_with_metadata(
        df=df,
        output_path=output_path,
        stage_name="test_stage",
        config=config,
    )

    metadata = read_parquet_metadata(output_path)
    assert metadata is not None
    assert metadata["stage_name"] == "test_stage"
    assert "git_commit" in metadata
    assert "config_hash" in metadata


def test_verify_data_integrity(tmp_path):
    """测试数据完整性验证"""
    input_file = tmp_path / "input.txt"
    input_file.write_text("test data")

    df = pd.DataFrame({"a": [1, 2, 3]})
    output_path = tmp_path / "output.parquet"
    config = {"test": "config"}

    save_parquet_with_metadata(
        df=df,
        output_path=output_path,
        stage_name="test_stage",
        config=config,
        input_files=[str(input_file)],
    )

    assert verify_data_integrity(output_path) is True

    input_file.write_text("modified data")

    assert verify_data_integrity(output_path) is False


def test_compute_file_hash(tmp_path):
    """测试文件 hash 计算"""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    hash1 = compute_file_hash(test_file)
    hash2 = compute_file_hash(test_file)

    assert hash1 == hash2

    test_file.write_text("different content")
    hash3 = compute_file_hash(test_file)

    assert hash1 != hash3


# ---------------------------------------------------------------------------
# quality-hardening Round 3 (2026-05-27): 补缺失分支覆盖
# data_versioning.py 84.76% -> ~100% (lines 39-41 / 54-55 / 103-105 /
# 215-218 / 237-238 / 242-243)
# ---------------------------------------------------------------------------

import subprocess
from unittest.mock import patch

from news_process.core import data_versioning as dv


def test_get_git_commit_hash_returns_unknown_on_called_process_error():
    """subprocess CalledProcessError → 'unknown' (data_versioning.py:39-41)."""
    with patch.object(
        dv.subprocess, 'run',
        side_effect=subprocess.CalledProcessError(returncode=128, cmd='git')):
        assert dv.get_git_commit_hash() == 'unknown'


def test_get_git_branch_returns_unknown_on_called_process_error():
    """subprocess CalledProcessError → 'unknown' (data_versioning.py:54-55)."""
    with patch.object(
        dv.subprocess, 'run',
        side_effect=subprocess.CalledProcessError(returncode=128, cmd='git')):
        assert dv.get_git_branch() == 'unknown'


def test_get_key_dependencies_returns_empty_on_import_error(monkeypatch):
    """关键依赖 ImportError → {} (data_versioning.py:103-105)."""
    import builtins
    orig_import = builtins.__import__

    def fake_import(name, *a, **kw):
        if name in ('numpy', 'pandas', 'torch', 'transformers'):
            raise ImportError(f"fake missing: {name}")
        return orig_import(name, *a, **kw)

    monkeypatch.setattr(builtins, '__import__', fake_import)
    assert dv.get_key_dependencies() == {}


def test_read_parquet_metadata_handles_no_data_version_key(tmp_path):
    """parquet 含 schema 但 metadata 无 'data_version' key → None (line 215)."""
    pd_local = __import__('pandas')
    df = pd_local.DataFrame({'a': [1, 2]})
    p = tmp_path / 'plain.parquet'
    df.to_parquet(p)  # 无 save_parquet_with_metadata 包装 → 无 data_version
    assert dv.read_parquet_metadata(p) is None


def test_read_parquet_metadata_handles_read_failure(tmp_path):
    """parquet 损坏/不可读 → logger.warning + None (line 216-218)."""
    bad = tmp_path / 'corrupt.parquet'
    bad.write_bytes(b'NOT A PARQUET FILE')
    assert dv.read_parquet_metadata(bad) is None


def test_verify_data_integrity_returns_false_on_missing_file(tmp_path):
    """文件不存在 → False (data_versioning.py:237-238)."""
    p = tmp_path / 'missing.parquet'
    assert dv.verify_data_integrity(p) is False


def test_verify_data_integrity_returns_false_when_metadata_missing(tmp_path):
    """parquet 存在但无版本元数据 → False (data_versioning.py:242-243)."""
    pd_local = __import__('pandas')
    df = pd_local.DataFrame({'a': [1, 2]})
    p = tmp_path / 'plain.parquet'
    df.to_parquet(p)  # 同上 — 无元数据
    assert dv.verify_data_integrity(p) is False
