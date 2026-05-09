import pytest
import pandas as pd
from pathlib import Path
from news_process.core.data_versioning import (
    DataVersionMetadata,
    save_parquet_with_metadata,
    read_parquet_metadata,
    verify_data_integrity,
    compute_file_hash,
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
