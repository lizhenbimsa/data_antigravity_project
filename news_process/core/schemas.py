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
"""

from __future__ import annotations

from typing import Mapping


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


def get_stage_outputs(stage_script: str) -> list[str]:
    """返回某个阶段脚本产出的 parquet 文件名列表 (无登记返回空列表)。"""
    return list(OUTPUT_REGISTRY.get(stage_script, []))


__all__ = ["OUTPUT_REGISTRY", "get_stage_outputs"]
