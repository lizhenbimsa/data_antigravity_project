"""B 完成后解析 results.json 并输出 markdown summary

Execution: 必须从项目根目录运行
    "F:/Anaconda3/python.exe" news_process/scripts/migrate/summarize_v7_sensitivity_results.py
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULTS_JSON = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / 'eval_reports' / 'prompt_sensitivity_results.json'
OUT_MD = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / 'v7_sensitivity_summary.md'


def main():
    if not RESULTS_JSON.exists():
        print(f'NOT FOUND: {RESULTS_JSON}')
        sys.exit(1)

    data = json.loads(RESULTS_JSON.read_text(encoding='utf-8'))

    md = ['# v7 Prompt Sensitivity Audit Summary\n',
          f'**Methodology**: {data.get("methodology", "")}\n',
          f'**Sample size**: {data.get("sample_size", "?")}, seed: {data.get("random_seed", "?")}\n',
          f'**Variants**: {data.get("n_variants", "?")} + V0 baseline\n',
          f'**Models**: {data.get("n_models", "?")}\n',
          f'**Tracks**: {data.get("tracks", [])}\n',
          f'**Overall PASS**: {"✅" if data.get("passed") else "❌"}\n\n',
          '## Thresholds\n']
    for k, v in data.get('thresholds', {}).items():
        md.append(f'- `{k}`: {v}\n')

    for track_key in ['full_track', 'ctx_track']:
        track_info = data.get(track_key, {})
        md.append(f'\n## {track_key}\n\n')
        md.append('### Pairwise (variant vs V0)\n\n')
        md.append('| Variant | v_agree | s_agree | κ_verif | iss_agree | κ_iss (W&Z) | il_agree | κ_il (Gomber) |\n')
        md.append('|---|---|---|---|---|---|---|---|\n')
        for vk, pw in track_info.get('pairwise', {}).items():
            md.append(f'| {vk} | {pw.get("verification_agreement","?"):.4f} | '
                     f'{pw.get("sentiment_agreement","?"):.4f} | '
                     f'{pw.get("cohens_kappa_verification","?"):.4f} | '
                     f'{pw.get("innovation_substantiveness_agreement","?")} | '
                     f'{pw.get("cohens_kappa_innovation_substantiveness","?")} | '
                     f'{pw.get("innovation_locus_agreement","?")} | '
                     f'{pw.get("cohens_kappa_innovation_locus","?")} |\n')
        multi = track_info.get('multi_variant', {})
        md.append(f'\n### Multi-variant: α={multi.get("krippendorffs_alpha","?")}, '
                 f"Fleiss' κ={multi.get('fleiss_kappa','?')}\n")

    OUT_MD.write_text(''.join(md), encoding='utf-8')
    print(f'Summary written: {OUT_MD}')


if __name__ == '__main__':
    main()
