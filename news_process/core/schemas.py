"""news_process.core.schemas — 列契约 + ``OUTPUT_REGISTRY`` (Phase 2d)。

Phase 2d 交付的单源 ``OUTPUT_REGISTRY`` 把每个阶段脚本名映射到它产出的
parquet 文件列表。orchestrator (用于陈旧数据预清理) 与 stage runner
(用于写入路径解析) 共同消费此字典。

Phase 1 时 orchestrator 内部持有一份私有的 ``_get_stage_output_files``
硬编码, 而各 stage 又独立从 ``CONFIG['filenames']['output_XX_*']``
读取文件名 — 教科书级 "双源真值" 风险。Phase 2d 通过本注册表消除这一
分歧。

注册表逐字保留历史 parquet 文件名契约, 确保 ``data/processed/`` 下既有
文件在新抽象下仍可访问。

Phase 9 (plan m2): 在 ``OUTPUT_REGISTRY`` (默认文件名) 之外引入
``_FILENAME_KEYS`` (filename_key 间接索引层), 并让 ``get_stage_outputs``
接受可选 ``config`` 参数。当 ``config`` 提供时, 优先读
``config['filenames'][filename_key]`` 解析实际文件名, 否则 fallback 到
默认文件名。这样用户在 ``paths.yaml::filenames`` 中改文件名后, 预清理
逻辑能自动跟进, 不再有 "stage 写到 X / 预清理删 Y" 的双源真值漂移。

注册表设计原则:
- ``OUTPUT_REGISTRY[script] = list[默认文件名]`` 保持 ``list[str]`` 公开
  类型, 既有调用方 (例如 ``panel_loader.list_available_panels``) 无需改动。
- ``_FILENAME_KEYS[script] = list[filename_key | None]`` 与 OUTPUT_REGISTRY
  下标一一对应; ``None`` 表示该输出是 stage 内部副产物, 在 paths.yaml 的
  ``filenames`` 节中无对应 key, 永远使用默认文件名。
"""

from __future__ import annotations

from typing import Mapping, Optional


# 阶段脚本名 (历史 root 文件名, 保留以做向后兼容) → 该阶段产出的 parquet
# 文件名列表。runner main() 不写 parquet 的阶段 (例如只产 eval_reports/*.csv
# 的验证类 runner) 故意不在此处登记; orchestrator 把缺失视为 "无需做预
# 清理"。
OUTPUT_REGISTRY: Mapping[str, list[str]] = {
    # 模块一: preprocess
    "00_preprocessing.py": ["00_preprocessing.parquet"],
    # 模块二: filtering
    "11_news_bank.py": ["11_bank_news.parquet"],
    "12_news_fintech.py": [
        "12_fintech_news.parquet",
        "12_fintech_news_full.parquet",
    ],
    "14_fintech_intensity.py": ["14_fintech_intensity.parquet"],
    "15_article_policy_alignment.py": ["15_article_alignment.parquet"],
    # 模块三: sentiment
    "21_tone_llms.py": [
        "21_tone_llms.parquet",
        "21_tone_llms_full.parquet",
    ],
    "22_tone_words.py": ["22_words_tone.parquet"],
    "23_tone_berts.py": ["23_bert_tone.parquet"],
    "24_herd_decay_processor.py": ["24_herd_decay.parquet"],
    # 模块五: panel construction (阶段 45 产出 bank-year + article-bank 两类面板)
    "45_panel_export_main.py": [
        "40_panel_yearly.parquet",
        "40_article_bank_level.parquet",
        "40_attn_index_year.parquet",
        "40_attn_index_province_year.parquet",
        "40_attn_index_city_year.parquet",
    ],
    # 模块六: falsification
    "51_falsification_test.py": ["51_panel_with_controls.parquet"],
}


# plan m2: filename_key 间接索引层。下标与 OUTPUT_REGISTRY 一一对应:
# - str  → 在 paths.yaml::filenames 中存在该 key, get_stage_outputs(config=...)
#          调用时将优先读 config['filenames'][key] 取实际文件名。
# - None → 该输出是 stage 内部副产物, paths.yaml::filenames 中无对应 key,
#          永远使用 OUTPUT_REGISTRY 中的默认文件名 (用户不可在 config 改名)。
_FILENAME_KEYS: Mapping[str, list[Optional[str]]] = {
    "00_preprocessing.py": ["output_00_preprocessing"],
    "11_news_bank.py": ["output_11_bank_news"],
    "12_news_fintech.py": [
        "output_12_fintech_news",
        "output_12_fintech_full",
    ],
    "14_fintech_intensity.py": ["output_14_fintech_intensity"],
    "15_article_policy_alignment.py": ["output_15_article_alignment"],
    "21_tone_llms.py": [
        "output_21_tone_llms",
        "output_21_tone_llms_full",
    ],
    "22_tone_words.py": ["output_22_words_tone"],
    "23_tone_berts.py": ["output_23_bert_tone"],
    "24_herd_decay_processor.py": ["output_24_herd_decay"],
    "45_panel_export_main.py": [
        "output_40_panel_yearly",
        "output_40_article_bank",
        None,  # 40_attn_index_year — 内部副输出, 无 config key
        None,  # 40_attn_index_province_year
        None,  # 40_attn_index_city_year
    ],
    "51_falsification_test.py": ["output_51_panel_controls"],
}


def get_stage_outputs(stage_script: str,
                      config: Optional[Mapping] = None) -> list[str]:
    """返回阶段脚本产出的 parquet 文件名列表 (无登记返回空列表)。

    Args:
        stage_script: 阶段脚本名 (例如 ``'00_preprocessing.py'``)。
        config: 可选; 当提供时, 函数会先尝试从
            ``config['filenames'][filename_key]`` 解析实际文件名,
            未配置或键缺失时 fallback 到 OUTPUT_REGISTRY 默认文件名。
            ``None`` 时返回 OUTPUT_REGISTRY 默认文件名 (向后兼容)。

    Returns:
        文件名列表 (顺序与 OUTPUT_REGISTRY 一致)。
    """
    defaults = OUTPUT_REGISTRY.get(stage_script, [])
    if not defaults:
        return []
    if config is None:
        return list(defaults)

    keys = _FILENAME_KEYS.get(stage_script, [None] * len(defaults))
    filenames_cfg = config.get('filenames', {}) or {}

    out: list[str] = []
    for i, default_filename in enumerate(defaults):
        key = keys[i] if i < len(keys) else None
        if key is not None and key in filenames_cfg:
            out.append(filenames_cfg[key])
        else:
            out.append(default_filename)
    return out


__all__ = ["OUTPUT_REGISTRY", "get_stage_outputs"]
