"""apply_stata_notes_helper — apply_stata_notes.ps1 的 Python 侧配套 (WP2, 计划 §3b)。

子命令 (全部只读 dta, 除 sidecar 文件写入外零副作用):
    snapshot        注入前/后快照落盘 (列数/dtype/var labels + 内容哈希; 供 WP5 读回全等断言)
    expected        打印某 dta 的 notes 对账期望数 = |dta 实际列 ∩ manifest 短名集| (§3b 对账层)
    sidecar-update  注入成功后逐 dta 键局部更新 _notes_applied_fingerprint.json (§3b 失败处置)
    sidecar-remove  注入失败时移除该 dta 键 (键缺失 = doctor [7/7] loud WARN)

从 repo 根运行: python -m news_process.scripts.apply_stata_notes_helper <cmd> ...
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

from news_process.pipeline.panel.stata_export import (
    NOTES_MANIFEST_FILENAME,
    STATA_NOTES_DTA_TARGETS,
    compute_expected_notes_count,
)

SIDECAR_FILENAME = '_notes_applied_fingerprint.json'


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _read_dta_meta(path: str):
    import pyreadstat
    _, meta = pyreadstat.read_dta(path, metadataonly=True)
    return meta


def _load_manifest(data_dir: str) -> dict:
    p = os.path.join(data_dir, NOTES_MANIFEST_FILENAME)
    if not os.path.exists(p):
        raise SystemExit(f'[helper] manifest 不存在: {p} — 先跑 stage 46 (write_notes_do_file)')
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def cmd_snapshot(args) -> int:
    """列数/dtype/var labels/sha256 快照 (§3b: ps1 开头自动落盘, 供 WP5 全等断言)。"""
    snap = {'taken_at': datetime.now(timezone.utc).isoformat(), 'dtas': {}}
    for key, fn in STATA_NOTES_DTA_TARGETS.items():
        p = os.path.join(args.data_dir, fn)
        if not os.path.exists(p):
            snap['dtas'][key] = {'file': fn, 'missing': True}
            continue
        meta = _read_dta_meta(p)
        snap['dtas'][key] = {
            'file': fn,
            'sha256': _sha256_file(p),
            'n_cols': int(meta.number_columns),
            'n_rows': int(meta.number_rows),
            'columns': list(meta.column_names),
            'dtypes': dict(meta.readstat_variable_types),
            'var_labels': dict(meta.column_names_to_labels),
        }
    out = os.path.join(args.data_dir, args.out)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(snap, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f'SNAPSHOT_WRITTEN={out}')
    return 0


def cmd_expected(args) -> int:
    """打印期望注入数 (仅数字, 供 ps1 捕获对账)。"""
    manifest = _load_manifest(args.data_dir)
    p = os.path.join(args.data_dir, args.dta)
    if not os.path.exists(p):
        raise SystemExit(f'[helper] dta 不存在: {p}')
    meta = _read_dta_meta(p)
    print(compute_expected_notes_count(meta.column_names, manifest['columns_short']))
    return 0


def _load_sidecar(data_dir: str) -> dict:
    p = os.path.join(data_dir, SIDECAR_FILENAME)
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    return {}


def _write_sidecar(data_dir: str, sidecar: dict) -> str:
    p = os.path.join(data_dir, SIDECAR_FILENAME)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(sidecar, f, ensure_ascii=False, indent=2, sort_keys=True)
    return p


def cmd_sidecar_update(args) -> int:
    """逐 dta 键局部更新 (其余键原样保留 — §3b 失败处置: 任一 dta 失败=该键缺失)。"""
    manifest = _load_manifest(args.data_dir)
    fn = manifest['dta_targets'].get(args.key)
    if not fn:
        raise SystemExit(f'[helper] manifest 无 dta key: {args.key}')
    p = os.path.join(args.data_dir, fn)
    if not os.path.exists(p):
        raise SystemExit(f'[helper] dta 不存在: {p}')
    sidecar = _load_sidecar(args.data_dir)
    sidecar[args.key] = {
        'dta': fn,
        'sha256': _sha256_file(p),  # 注入后 (save, replace 之后) 的内容哈希
        'n_notes_applied': int(args.n_applied),
        'applied_at': datetime.now(timezone.utc).isoformat(),
    }
    out = _write_sidecar(args.data_dir, sidecar)
    print(f'SIDECAR_UPDATED key={args.key} file={out}')
    return 0


def cmd_sidecar_remove(args) -> int:
    sidecar = _load_sidecar(args.data_dir)
    if args.key in sidecar:
        del sidecar[args.key]
        _write_sidecar(args.data_dir, sidecar)
        print(f'SIDECAR_KEY_REMOVED key={args.key}')
    else:
        print(f'SIDECAR_KEY_ABSENT key={args.key}')
    return 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(prog='python -m news_process.scripts.apply_stata_notes_helper')
    sub = ap.add_subparsers(dest='cmd', required=True)

    sp = sub.add_parser('snapshot')
    sp.add_argument('--data-dir', required=True)
    sp.add_argument('--out', default='_notes_preinject_snapshot.json')
    sp.set_defaults(func=cmd_snapshot)

    sp = sub.add_parser('expected')
    sp.add_argument('--data-dir', required=True)
    sp.add_argument('--dta', required=True, help='dta 文件名 (相对 data-dir)')
    sp.set_defaults(func=cmd_expected)

    sp = sub.add_parser('sidecar-update')
    sp.add_argument('--data-dir', required=True)
    sp.add_argument('--key', required=True, choices=sorted(STATA_NOTES_DTA_TARGETS))
    sp.add_argument('--n-applied', required=True, type=int)
    sp.set_defaults(func=cmd_sidecar_update)

    sp = sub.add_parser('sidecar-remove')
    sp.add_argument('--data-dir', required=True)
    sp.add_argument('--key', required=True)
    sp.set_defaults(func=cmd_sidecar_remove)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())
