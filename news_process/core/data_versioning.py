"""news_process.core.data_versioning — 数据版本控制和血缘追踪。

在 parquet 文件元数据中记录：
- Git commit hash
- 配置文件 hash
- 生成时间戳
- 依赖的输入文件 hash
- Python 版本和关键依赖版本
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

logger = logging.getLogger(__name__)


def get_git_commit_hash() -> str:
    """获取当前 Git commit hash。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        logger.warning("无法获取 Git commit hash，可能不在 Git 仓库中")
        return "unknown"


def get_git_branch() -> str:
    """获取当前 Git 分支名。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def compute_file_hash(file_path: str | Path) -> str:
    """计算文件的 SHA256 hash。"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_config_hash(config: dict) -> str:
    """计算配置字典的 hash (SHA-256)。

    ``default=str`` 兜底: 若字典含 datetime/Path 等非 JSON 原生类型,
    转为字符串表示, 避免 TypeError。
    """
    config_str = json.dumps(config, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(config_str.encode()).hexdigest()


def get_python_version() -> str:
    """获取 Python 版本。"""
    import sys
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_key_dependencies() -> dict[str, str]:
    """获取关键依赖的版本。"""
    try:
        import numpy
        import pandas
        import torch
        import transformers

        return {
            "pandas": pandas.__version__,
            "numpy": numpy.__version__,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
        }
    except ImportError as e:
        logger.warning(f"无法获取依赖版本: {e}")
        return {}


class DataVersionMetadata:
    """数据版本元数据。"""

    def __init__(
        self,
        stage_name: str,
        config: dict,
        input_files: Optional[list[str]] = None,
    ):
        self.stage_name = stage_name
        self.config = config
        self.input_files = input_files or []

        # 收集版本信息
        self.git_commit = get_git_commit_hash()
        self.git_branch = get_git_branch()
        self.config_hash = compute_config_hash(config)
        self.timestamp = datetime.now().isoformat()
        self.python_version = get_python_version()
        self.dependencies = get_key_dependencies()

        # 计算输入文件 hash
        self.input_hashes = {}
        for input_file in self.input_files:
            if Path(input_file).exists():
                self.input_hashes[input_file] = compute_file_hash(input_file)

    def to_dict(self) -> dict:
        """转换为字典。"""
        return {
            "stage_name": self.stage_name,
            "git_commit": self.git_commit,
            "git_branch": self.git_branch,
            "config_hash": self.config_hash,
            "timestamp": self.timestamp,
            "python_version": self.python_version,
            "dependencies": self.dependencies,
            "input_files": self.input_files,
            "input_hashes": self.input_hashes,
        }

    def to_json(self) -> str:
        """转换为 JSON 字符串。"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


def save_parquet_with_metadata(
    df: pd.DataFrame,
    output_path: str | Path,
    stage_name: str,
    config: dict,
    input_files: Optional[list[str]] = None,
):
    """
    保存 DataFrame 到 parquet 文件，并附加版本元数据。

    Args:
        df: 要保存的 DataFrame
        output_path: 输出文件路径
        stage_name: 阶段名称
        config: 配置字典
        input_files: 依赖的输入文件列表
    """
    metadata = DataVersionMetadata(stage_name, config, input_files)

    table = pa.Table.from_pandas(df)

    existing_metadata = table.schema.metadata or {}
    custom_metadata = {
        b"data_version": metadata.to_json().encode("utf-8"),
    }
    merged_metadata = {**existing_metadata, **custom_metadata}

    new_schema = table.schema.with_metadata(merged_metadata)
    table = table.cast(new_schema)

    pq.write_table(table, output_path)

    logger.info(
        f"已保存 {output_path} with metadata:\n"
        f"  Git commit: {metadata.git_commit[:8]}\n"
        f"  Config hash: {metadata.config_hash[:8]}\n"
        f"  Timestamp: {metadata.timestamp}"
    )


def read_parquet_metadata(file_path: str | Path) -> Optional[dict]:
    """
    读取 parquet 文件的版本元数据。

    Args:
        file_path: parquet 文件路径

    Returns:
        版本元数据字典，如果不存在则返回 None
    """
    try:
        parquet_file = pq.ParquetFile(file_path)
        metadata = parquet_file.schema_arrow.metadata

        if metadata and b"data_version" in metadata:
            version_json = metadata[b"data_version"].decode("utf-8")
            return json.loads(version_json)

        return None
    except Exception as e:
        logger.warning(f"无法读取 {file_path} 的元数据: {e}")
        return None


def verify_data_integrity(file_path: str | Path) -> bool:
    """
    验证数据完整性。

    检查：
    1. 文件是否存在
    2. 元数据是否存在
    3. 输入文件 hash 是否匹配（如果输入文件仍存在）

    Args:
        file_path: parquet 文件路径

    Returns:
        True 如果数据完整，False 如果存在问题
    """
    if not Path(file_path).exists():
        logger.error(f"文件不存在: {file_path}")
        return False

    metadata = read_parquet_metadata(file_path)
    if metadata is None:
        logger.warning(f"文件缺少版本元数据: {file_path}")
        return False

    for input_file, expected_hash in metadata.get("input_hashes", {}).items():
        if Path(input_file).exists():
            actual_hash = compute_file_hash(input_file)
            if actual_hash != expected_hash:
                logger.error(
                    f"输入文件 hash 不匹配: {input_file}\n"
                    f"  期望: {expected_hash[:8]}...\n"
                    f"  实际: {actual_hash[:8]}..."
                )
                return False

    logger.info(f"数据完整性验证通过: {file_path}")
    return True
