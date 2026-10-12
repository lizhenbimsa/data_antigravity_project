"""人工标注冻结清单校验 (config/validation.yaml::human_annotation_frozen)。

只读: 逐个比对流水线原件与 human_samples_blind/ 回收副本的 sha256, 任一不符即退出码 1。
可选 --root 指向备份目录 (目录结构同 data/processed/), 用于核验异地备份是否完整。

用法 (repo 根):
    python news_process/scripts/audit/verify_human_annotation_frozen.py
    python news_process/scripts/audit/verify_human_annotation_frozen.py --root D:/备份/processed

白话: 人工标注改不得也删不得, 这个脚本用"指纹"检查每份表是否还是冻结时的样子。
"""
import argparse
import hashlib
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def verify(root: Path) -> int:
    from news_process.core.config import load_config
    cfg = load_config()['human_annotation_frozen']
    archive = root / cfg['archive_dir']
    overrides = cfg.get('archive_sha256_overrides') or {}
    by_name = {p.name: p for p in archive.rglob('*.xlsx')} if archive.exists() else {}
    bad = 0
    for rel, sha in cfg['files'].items():
        checks = [('原件', root / rel, sha)]
        copy = by_name.get(Path(rel).name)
        if copy is None:
            checks.append(('副本', archive / Path(rel).name, sha))
        else:
            ov = overrides.get(copy.relative_to(archive).as_posix())
            checks.append(('副本', copy, ov or sha))
        for kind, path, want in checks:
            if not path.exists():
                status = '缺失'
            elif _sha256(path) != want:
                status = '不符'
            else:
                status = 'OK'
            bad += status != 'OK'
            print(f'[{status}] {kind} {path}')
    print(f'\n共 {len(cfg["files"])} 份冻结表 × (原件 + 副本); 异常 {bad} 项')
    return 1 if bad else 0


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path,
                    default=PROJECT_ROOT / 'news_process' / 'data' / 'processed')
    sys.exit(verify(ap.parse_args().root))
