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
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from news_process.core.logging import pct4

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


# ── W5 通用 --skip-unchanged: config/资源内容寻址哈希 (2026-06-25) ──
# golden-safe: 只读 config/ 下文件内容算 sha256, 不产数据列; 写进 parquet schema
# metadata (非数据列), 供编排器在 spawn 前比对决定是否跳过"输入未变"的阶段。
_SPLIT_YAML_FILES = (
    "paths.yaml", "preprocessing.yaml", "filtering.yaml", "sentiment.yaml",
    "features.yaml", "panel.yaml", "validation.yaml",
)


def _default_config_dir() -> Path:
    """core/data_versioning.py → core/ → news_process/ → config/ (与 core/config.py 同源定位)。"""
    return Path(__file__).resolve().parent.parent / "config"


def compute_config_file_hashes(config_dir: str | Path | None = None) -> dict[str, str]:
    """对 7 个 split YAML 各算内容 sha256。改任一 YAML 内容 → 对应消费它的 stage 失效。"""
    cdir = Path(config_dir) if config_dir is not None else _default_config_dir()
    out: dict[str, str] = {}
    for fn in _SPLIT_YAML_FILES:
        p = cdir / fn
        if p.exists():
            out[fn] = compute_file_hash(p)
    return out


def compute_resource_hashes(config_dir: str | Path | None = None) -> dict[str, str]:
    """对 config/ 下全部载荷资源 (词典/anchor/prompt 等 .json/.txt) 各算内容 sha256。

    W5 通用 skip 的**保守资源门**: 任一资源变 → 不跳过任何阶段, 防"改词典/anchor 却被
    错跳" (news_bank.py 自承 input_hashes 不含词典内容会致 verify 失明)。
    """
    cdir = Path(config_dir) if config_dir is not None else _default_config_dir()
    out: dict[str, str] = {}
    if cdir.exists():
        for p in sorted(cdir.rglob("*")):
            if p.is_file() and p.suffix.lower() in (".json", ".txt"):
                rel = str(p.relative_to(cdir)).replace("\\", "/")
                out[rel] = compute_file_hash(p)
    return out


def get_python_version() -> str:
    """获取 Python 版本。"""
    import sys
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_key_dependencies() -> dict[str, str]:
    """获取关键依赖的版本。"""
    try:
        warnings.filterwarnings(
            "ignore",
            message=r"Failed to find CUDA\.",
            category=UserWarning,
            module=r"triton\.windows_utils",
        )
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
        config_dir: str | Path | None = None,
        code_version: str | None = None,
    ):
        self.stage_name = stage_name
        self.config = config
        self.input_files = input_files or []
        # W5 (2026-06-26): 该阶段"代码语义版本号" (如 stage 00 的 PREPROCESS_CODE_VERSION)。
        #   写进 schema metadata (非数据列 → golden-safe), 供 --skip-unchanged 在改了预处理
        #   代码逻辑 (dedup/normalize/filter) 时失效该阶段的跳过判据 (config/语料未变也重跑)。
        self.code_version = code_version

        # 收集版本信息
        self.git_commit = get_git_commit_hash()
        self.git_branch = get_git_branch()
        self.config_hash = compute_config_hash(config)
        # W5 通用 --skip-unchanged: config/资源内容寻址哈希 (写进 schema metadata, golden-safe)。
        self.config_file_hashes = compute_config_file_hashes(config_dir)
        self.resource_hashes = compute_resource_hashes(config_dir)
        # F-15 (2026-05-16): 带时区的 UTC 时间戳, 保证跨服务器血缘记录可比。
        # naive datetime 的时区歧义是 F-15 全项目唯一命中点 (R25 扫描);
        # core/run_id.py:27 的同类代码用同一写法。
        self.timestamp = datetime.now(timezone.utc).isoformat()
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
            "code_version": self.code_version,
            "config_file_hashes": self.config_file_hashes,
            "resource_hashes": self.resource_hashes,
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
    config_dir: str | Path | None = None,
    *,
    code_version: str | None = None,
    preserve_index: bool | None = None,
    compression: str = "snappy",
    row_group_size: int | None = None,
    use_dictionary: bool = True,
    write_statistics: bool = True,
):
    """
    保存 DataFrame 到 parquet 文件，并附加版本元数据。

    Args:
        df: 要保存的 DataFrame
        output_path: 输出文件路径
        stage_name: 阶段名称
        config: 配置字典
        input_files: 依赖的输入文件列表
        config_dir: split YAML / 资源目录 (默认从 core/config 同源定位)
        code_version: 该阶段代码语义版本号 (如 PREPROCESS_CODE_VERSION); 入 schema metadata,
            供 --skip-unchanged 在预处理代码逻辑变化时失效跳过 (默认 None = 不记录, 不参与门控)
        preserve_index: 透传给 ``pa.Table.from_pandas`` (默认 None = pyarrow 默认行为)
        compression / row_group_size / use_dictionary / write_statistics:
            透传给 ``pq.write_table`` 的列存布局参数。

    ⚠ W5 (2026-06-26): ``preserve_index`` 与四个 write 参数的默认值与
    ``pa.Table.from_pandas`` / ``pq.write_table`` 的 pyarrow 默认**逐位一致** —— 既有调用方
    (不传这些 kwargs) 产物字节不变。stage 00 (``pipeline/preprocess/runner.py``) 用它们
    复刻历史 ``pq.write_table(..., row_group_size=100_000, ...)`` 的列存布局, 仅额外多写
    ``b'data_version'`` schema metadata (非数据列 → golden 只哈希数据列 → golden-safe),
    以激活通用 ``--skip-unchanged`` 的根阶段内容寻址判据。
    """
    metadata = DataVersionMetadata(
        stage_name, config, input_files, config_dir=config_dir, code_version=code_version
    )

    table = pa.Table.from_pandas(df, preserve_index=preserve_index)

    existing_metadata = table.schema.metadata or {}
    custom_metadata = {
        b"data_version": metadata.to_json().encode("utf-8"),
    }
    merged_metadata = {**existing_metadata, **custom_metadata}

    new_schema = table.schema.with_metadata(merged_metadata)
    table = table.cast(new_schema)

    pq.write_table(
        table,
        output_path,
        compression=compression,
        row_group_size=row_group_size,
        use_dictionary=use_dictionary,
        write_statistics=write_statistics,
    )

    # ── 纯日志统计 (log-only, 不参与任何产物计算; 仅喂给下方 logger) ──
    n_rows, n_cols = df.shape  # df.shape 只读, 不改产物
    n_input_decl = len(metadata.input_files)        # 声明的依赖输入文件数 (整数)
    n_input_hashed = len(metadata.input_hashes)     # 实际找到并已记 SHA-256 的输入数
    n_input_missing = n_input_decl - n_input_hashed  # 声明但盘上缺失 (未记 hash) 的输入数
    # 输入文件 hash 覆盖率 (盘上找到 / 声明), 0 声明时无意义 → 标注 N/A。
    hash_cov_str = (
        pct4(n_input_hashed / n_input_decl) if n_input_decl > 0 else "N/A (无声明输入)"
    )
    n_config_yaml = len(metadata.config_file_hashes)  # W5 内容寻址: 已记 split YAML 数
    n_resources = len(metadata.resource_hashes)       # W5 内容寻址: 已记载荷资源 (.json/.txt) 数
    n_deps = len(metadata.dependencies)               # 已记关键依赖版本数

    logger.info(
        f"已保存 {output_path} (附数据血缘元数据 data_version):\n"
        f"  Git commit (前 8 位): {metadata.git_commit[:8]}\n"
        f"  Git branch:         {metadata.git_branch}\n"
        f"  Config hash (前 8 位): {metadata.config_hash[:8]}\n"
        f"  Python:             {metadata.python_version}\n"
        f"  输入文件数:          {n_input_hashed:,} 个 (已记 SHA-256)\n"
        f"  Timestamp (UTC):    {metadata.timestamp}"
    )
    logger.info(
        "📊 运行期参数 (data_versioning · 内容寻址血缘):\n"
        f"  · 阶段 stage_name      : {metadata.stage_name}\n"
        f"  · 产物 DataFrame 规模  : {n_rows:,} 行 × {n_cols:,} 列\n"
        f"  · 声明依赖输入文件     : {n_input_decl:,} 个 (盘上找到 {n_input_hashed:,} / 缺失 {n_input_missing:,})\n"
        f"  · split YAML 内容哈希  : {n_config_yaml:,} 份 (W5 --skip-unchanged 门控)\n"
        f"  · 载荷资源内容哈希     : {n_resources:,} 份 (.json/.txt; 保守资源门)\n"
        f"  · 关键依赖版本记录     : {n_deps:,} 个 ({', '.join(metadata.dependencies) or '空'})"
    )
    logger.info(
        "📈 结果统计 (血缘元数据完整性):\n"
        f"  · 输入文件 SHA-256 覆盖率 : {hash_cov_str} ({n_input_hashed:,}/{n_input_decl:,})\n"
        f"  · config_hash (全局配置)  : {metadata.config_hash[:12]}…\n"
        f"  · 元数据键总数            : {len(metadata.to_dict()):,} 个顶层字段\n"
        f"  · 写入 parquet schema metadata key: b'data_version' (非数据列, golden-safe)"
    )
    # 📖 方法论依据 (内容寻址 / 可复现计算血缘): 记录 git commit + config hash +
    #    输入文件 SHA-256 + 依赖版本, 使每个 parquet 产物可溯源、可复现校验。
    #    候选文献中的计量估计方法 (qreg/PPML/Oster/randomization inference) 与本模块
    #    "数据版本/出处追踪" 无方法学锚定关系, 故不 emit; 仅 emit 两条真锚定的"可复现"
    #    方法学文献 —— Sandve 2013 (通用可复现计算) + Cheng 2024 (LLM 标注可复现, 对应
    #    本模块为 stage 21 等 LLM 标注 parquet 记录 code_version / config_hash 的机制)。
    logger.info(
        "📖 方法论依据 (可复现计算研究 · 出处与版本追踪):\n"
        "  Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten simple "
        "rules for reproducible computational research. PLoS Computational Biology, "
        "9(10), e1003285. https://doi.org/10.1371/journal.pcbi.1003285\n"
        "  (白话: 可复现计算研究的十条准则; 本模块落实其规则 4-6——记录所有中间结果、"
        "版本与精确出处, 让每个 parquet 产物都能溯源到 git commit / config / 输入哈希。)\n"
        "  Cheng, X., Mayya, R., & Sedoc, J. (2024). To err is human; to annotate, "
        "SILICON? Toward robust reproducibility in LLM annotation (arXiv:2412.14461). "
        "arXiv. https://doi.org/10.48550/arXiv.2412.14461\n"
        "       → 本模块把 code_version (如 PREPROCESS_CODE_VERSION) 与 config_hash "
        "(含 prompt_version) 一并写入 schema metadata, 正是该文倡导的'记录 prompt/配置/"
        "代码版本以使 LLM 标注产物可复现'纪律在数据版本层的落地。"
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
