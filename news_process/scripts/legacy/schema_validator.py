"""
schema_validator.py — DataFrame Schema验证工具
================================================

功能：
    验证DataFrame是否符合预定义的Schema，防止列缺失导致的KeyError。

使用方法（archive only — 此模块已被 Phase 1 弃用, 仅作历史归档）：
    # 历史用法 (utils/ 在 Phase 6b 被删除前可用):
    #     from utils.schema_validator import validate_schema, load_schemas
    # 后续替代方案: news_process.core.quality.* 与 news_process.core.schemas
    schemas = load_schemas()
    if not validate_schema(df, 'stage_14_output', schemas, logger):
        raise ValueError("输入数据Schema不匹配")
"""

import os
import yaml
import pandas as pd


def load_schemas(config_dir: str = None) -> dict:
    """加载Schema定义文件。

    Args:
        config_dir: 配置目录路径，默认为当前脚本所在目录的config子目录

    Returns:
        dict: Schema定义字典
    """
    if config_dir is None:
        config_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config'
        )

    schema_file = os.path.join(config_dir, 'schemas.yaml')

    if not os.path.exists(schema_file):
        return {}

    with open(schema_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def validate_schema(df: pd.DataFrame, stage_name: str,
                    schemas: dict, logger) -> bool:
    """验证DataFrame是否符合阶段Schema定义。

    Args:
        df: 待验证的DataFrame
        stage_name: 阶段名称（如 'stage_14_output'）
        schemas: Schema定义字典
        logger: 日志对象

    Returns:
        bool: 验证是否通过
    """
    schema = schemas.get(stage_name)

    if not schema:
        logger.debug(f"未定义Schema: {stage_name}，跳过验证")
        return True

    required = schema.get('required_columns', [])
    missing = [col for col in required if col not in df.columns]

    if missing:
        logger.error(f"Schema验证失败: 缺失列 {missing}")
        logger.error(f"期望列: {required}")
        logger.error(f"实际列: {df.columns.tolist()}")
        return False

    logger.debug(f"Schema验证通过: {stage_name}")
    return True


def load_with_fallback(primary_path: str, fallback_paths: list,
                      logger) -> pd.DataFrame:
    """通用回退加载函数。

    Args:
        primary_path: 主输入文件路径
        fallback_paths: 回退文件路径列表
        logger: 日志对象

    Returns:
        pd.DataFrame: 加载的数据

    Raises:
        FileNotFoundError: 所有路径均不存在时抛出
    """
    if os.path.exists(primary_path):
        logger.info(f"使用主输入: {os.path.basename(primary_path)}")
        return pd.read_parquet(primary_path)

    for fallback in fallback_paths:
        if os.path.exists(fallback):
            logger.warning(f"主输入不存在，使用回退: {os.path.basename(fallback)}")
            return pd.read_parquet(fallback)

    all_paths = [primary_path] + fallback_paths
    raise FileNotFoundError(f"所有输入均未找到: {[os.path.basename(p) for p in all_paths]}")
