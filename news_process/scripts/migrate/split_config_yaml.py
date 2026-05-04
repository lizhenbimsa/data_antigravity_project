"""scripts/migrate/split_config_yaml.py — Phase 4d 配置拆分迁移脚本.

用法:
    python news_process/scripts/migrate/split_config_yaml.py

效果:
- 读取 ``news_process/config/config.yaml``
- 按 SPLIT_PLAN.md 的领域映射拆为 7 个 YAML
- 提取 2 个 prompt 模板到 ``news_process/config/prompts/*.txt``
- 把原 ``config.yaml`` 改写为说明性 stub (loader 会自动检测 split 模式)
- 全程使用 ``ruamel.yaml``, 尽量保留注释 / key 顺序

幂等性:
- 检测到 split YAMLs 已存在时, 直接 abort (避免覆盖手工修改的 split 文件)
- 用 ``--force`` 强制覆盖
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ruamel.yaml import YAML


# ----------------------------------------------------------------------------
# 原 config 顶层节 → 拆分后领域 YAML 的映射
# ----------------------------------------------------------------------------

SECTION_TO_DOMAIN: dict[str, str] = {
    # paths.yaml
    'paths': 'paths',
    'filenames': 'paths',
    'parallel': 'paths',
    # preprocessing.yaml
    'preprocessing': 'preprocessing',
    'normalization': 'preprocessing',
    'deduplication': 'preprocessing',
    # filtering.yaml
    'bank_news_classification': 'filtering',
    'fintech_news_classification': 'filtering',
    'fintech_intensity': 'filtering',
    'article_alignment': 'filtering',
    'context_window': 'filtering',
    # sentiment.yaml
    'tone_llm_processing': 'sentiment',
    'sentiment_analysis': 'sentiment',
    'herd_detection': 'sentiment',
    # features.yaml
    'embedding_api': 'features',
    'benefit_society': 'features',
    # panel.yaml
    'panel_building': 'panel',
    'temporal_mask_test': 'panel',
    # validation.yaml
    'human_validation': 'validation',
    'validation': 'validation',
    'entity_masking_test': 'validation',
    'prompt_sensitivity_test': 'validation',
    'threshold_sensitivity': 'validation',
}

DOMAINS = ('paths', 'preprocessing', 'filtering', 'sentiment',
           'features', 'panel', 'validation')

# Prompt template fields to externalize:
#   key path (within the parsed dict) → output filename under config/prompts/
PROMPT_EXTRACTIONS: dict[tuple[str, str], str] = {
    ('tone_llm_processing', 'prompt_template'): 'unified_cot.txt',
    ('tone_llm_processing', 'title_sentiment_prompt_template'): 'title_sentiment.txt',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--force', action='store_true',
                        help='Overwrite split YAMLs / prompt files if they already exist.')
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    config_dir = project_root / 'config'
    legacy_yaml = config_dir / 'config.yaml'
    prompts_dir = config_dir / 'prompts'

    if not legacy_yaml.exists():
        print(f"ERROR: {legacy_yaml} not found", file=sys.stderr)
        return 2

    # 检查 split YAMLs 是否已存在
    targets = {d: config_dir / f"{d}.yaml" for d in DOMAINS}
    existing_targets = [str(p) for p in targets.values() if p.exists()]
    if existing_targets and not args.force:
        print(f"ERROR: split YAMLs already exist: {existing_targets}",
              file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        return 2

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096  # Don't wrap long strings

    print(f"Loading {legacy_yaml}...")
    with open(legacy_yaml, 'r', encoding='utf-8') as f:
        cfg = yaml.load(f)

    print(f"Top-level keys: {list(cfg.keys())}")

    # 1) Extract prompt templates
    prompts_dir.mkdir(parents=True, exist_ok=True)
    for (section, key), filename in PROMPT_EXTRACTIONS.items():
        if section not in cfg or key not in cfg[section]:
            print(f"WARN: prompt key {section}.{key} not found, skipping")
            continue
        content = cfg[section][key]
        out_path = prompts_dir / filename
        out_path.write_text(content, encoding='utf-8', newline='\n')
        print(f"  ✓ Extracted prompt: {section}.{key} → {out_path.name} "
              f"({len(content)} chars)")
        # Replace inline content with file reference
        del cfg[section][key]
        # New key name: <key>_file → relative path
        cfg[section][f'{key}_file'] = f'./config/prompts/{filename}'

    # 2) Split top-level into 7 domain dicts
    split_dicts: dict[str, dict] = {d: {} for d in DOMAINS}
    unmapped_sections: list[str] = []
    for section in cfg:
        domain = SECTION_TO_DOMAIN.get(section)
        if domain is None:
            unmapped_sections.append(section)
            continue
        split_dicts[domain][section] = cfg[section]

    if unmapped_sections:
        print(f"ERROR: unmapped sections: {unmapped_sections}", file=sys.stderr)
        return 2

    # 3) Write split YAMLs
    for domain in DOMAINS:
        out_path = targets[domain]
        sub_cfg = split_dicts[domain]
        if not sub_cfg:
            print(f"  (skip) {domain}.yaml — empty after split")
            continue
        with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(f"# Phase 4d split — {domain} domain\n"
                    f"# Generated by scripts/migrate/split_config_yaml.py\n"
                    f"# Original section ownership preserved; comments may have"
                    f" been re-flowed during round-trip.\n\n")
            yaml.dump(sub_cfg, f)
        size_kb = out_path.stat().st_size / 1024
        print(f"  ✓ Wrote {out_path.name} ({size_kb:.1f}KB, "
              f"{len(sub_cfg)} top-level keys)")

    # 4) Replace legacy config.yaml with stub
    stub = """# news_process configuration — split into 7 domain YAMLs (Phase 4d)
# =====================================================================
#
# This file is intentionally empty. The configuration is now distributed
# across 7 domain-specific YAML files in this directory:
#
#     paths.yaml          — paths + filenames + parallel
#     preprocessing.yaml  — preprocessing + normalization + deduplication
#     filtering.yaml      — bank/fintech_news_classification + fintech_intensity
#                           + article_alignment + context_window
#     sentiment.yaml      — tone_llm_processing + sentiment_analysis + herd_detection
#     features.yaml       — embedding_api + benefit_society
#     panel.yaml          — panel_building + temporal_mask_test
#     validation.yaml     — human_validation + validation + *_test + *_sensitivity
#
# And 2 prompt templates externalized to:
#
#     prompts/unified_cot.txt        — tone_llm_processing.prompt_template
#     prompts/title_sentiment.txt    — tone_llm_processing.title_sentiment_prompt_template
#
# news_process.core.config.load_config() detects the split-mode setup and
# deep-merges all 7 YAMLs into a single dict semantically equivalent to the
# pre-Phase-4d monolithic config.yaml.
#
# Backward compatibility: if any of the 7 split YAMLs is missing, the
# loader falls back to reading this file as a monolithic legacy config.
# Therefore the loader treats THIS file as authoritative when split YAMLs
# are absent, but uses the 7-file layout when they are present.
"""
    legacy_yaml.write_text(stub, encoding='utf-8', newline='\n')
    print(f"  ✓ Replaced {legacy_yaml.name} with stub")

    print("\nDone. Verify by running:")
    print("  pytest news_process/tests/integration/test_config_split_equivalence.py")
    return 0


if __name__ == '__main__':
    sys.exit(main())
