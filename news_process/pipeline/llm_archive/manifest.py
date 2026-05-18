"""LLM Archive Manifest — 生成 / 验证 manifest.json.

v3.7.0 Manifest 格式 (per-file SHA-256 + 全局 metadata):

::

    {
      "schema_version": "v1",
      "archive_frozen_date": "2026-05-18",
      "generated_at_utc": "2026-05-18T13:45:00+00:00",
      "prompt_version_anchor": "v8",
      "files": {
        "2026-05-18.jsonl": {
          "sha256": "abc123...",
          "bytes": 1234567,
          "record_count": 1234
        },
        ...
      },
      "total_records": 12345,
      "total_bytes": 5678901
    }
"""
from __future__ import annotations

import datetime as dt
import json
import logging
from pathlib import Path
from typing import Optional

from .archive import DEFAULT_ARCHIVE_ROOT, sha256_of_file

logger = logging.getLogger(__name__)

MANIFEST_FILENAME = 'manifest.json'


def _sha_and_count_in_one_pass(path: Path) -> tuple[str, int, int]:
    """v3.7.0 (M5 修复): 单次 IO 同时算 sha256 + bytes + line count.

    Returns:
        (sha256_hex, byte_count, line_count)
    """
    import hashlib
    h = hashlib.sha256()
    byte_count = 0
    line_count = 0
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
            byte_count += len(chunk)
            line_count += chunk.count(b'\n')
    return h.hexdigest(), byte_count, line_count


def compute_manifest(
    root: Optional[Path] = None,
    *,
    prompt_version_anchor: str = 'v8',
    archive_frozen_date: str = '2026-05-18',
) -> dict:
    """扫描 archive 目录, 生成 manifest dict.

    v3.7.0 (M5 修复): 单次 IO 同时算 sha256 + bytes + line count.

    Args:
        root: archive 根目录 (默认 data/llm_archive/).
        prompt_version_anchor: 锚定的 prompt version (v3.5.1 = "v8").
        archive_frozen_date: 归档 frozen 日期.

    Returns:
        dict: manifest 内容 (未写入文件).
    """
    root = Path(root) if root else DEFAULT_ARCHIVE_ROOT
    responses_dir = root / 'responses'
    if not responses_dir.exists():
        logger.warning(f"responses dir 不存在: {responses_dir}")
        files = {}
    else:
        files = {}
        for jsonl_path in sorted(responses_dir.glob('*.jsonl')):
            sha, byte_count, line_count = _sha_and_count_in_one_pass(jsonl_path)
            files[jsonl_path.name] = {
                'sha256': sha,
                'bytes': byte_count,
                'record_count': line_count,
            }

    manifest = {
        'schema_version': 'v1',
        'archive_frozen_date': archive_frozen_date,
        'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'prompt_version_anchor': prompt_version_anchor,
        'files': files,
        'total_records': sum(f['record_count'] for f in files.values()),
        'total_bytes': sum(f['bytes'] for f in files.values()),
    }
    return manifest


def _read_prompt_version_anchor_from_sidecar() -> Optional[str]:
    """v3.7.0 (m5 修复): 从 v3.5.1 sidecar JSON 读 frozen prompt version.

    避免 hardcoded 'v8' 在 sidecar 升级时漂移.
    """
    sidecar = Path('data/processed/v3_5_1_constants.json')
    if not sidecar.exists():
        return None
    try:
        with sidecar.open('r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('prompt_v8_sha256_anchor') or data.get('prompt_version')
    except Exception:
        return None


def write_manifest(
    root: Optional[Path] = None,
    *,
    prompt_version_anchor: Optional[str] = None,
    archive_frozen_date: str = '2026-05-18',
) -> Path:
    """生成并写入 manifest.json 到 archive 根目录.

    v3.7.0 (m5 修复): prompt_version_anchor=None 时从 sidecar JSON 读 (避免硬编码).
    """
    if prompt_version_anchor is None:
        anchor_from_sidecar = _read_prompt_version_anchor_from_sidecar()
        prompt_version_anchor = anchor_from_sidecar or 'v8'
    root = Path(root) if root else DEFAULT_ARCHIVE_ROOT
    manifest = compute_manifest(
        root,
        prompt_version_anchor=prompt_version_anchor,
        archive_frozen_date=archive_frozen_date,
    )
    manifest_path = root / MANIFEST_FILENAME
    with manifest_path.open('w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
    logger.info(
        f"Manifest written: {manifest_path} "
        f"({manifest['total_records']} records, {manifest['total_bytes']} bytes)"
    )
    return manifest_path


def verify_manifest(root: Optional[Path] = None) -> tuple[bool, list[str]]:
    """验证 archive 与 manifest 一致.

    v3.7.0 (M4 修复): 双向 cross-check —
    1. manifest 中的每个文件必须存在且 sha256/bytes 匹配
    2. responses_dir 中不能有 manifest *未登记* 的 jsonl 文件
       (防止恶意 / 误操作偷加新 jsonl 而 verify 漏报)

    Returns:
        (ok, errors): ok=True 表示完整一致.
                      errors 列出每个不一致 / 多余文件的诊断.
    """
    root = Path(root) if root else DEFAULT_ARCHIVE_ROOT
    manifest_path = root / MANIFEST_FILENAME
    if not manifest_path.exists():
        return False, [f"manifest 不存在: {manifest_path}"]

    with manifest_path.open('r', encoding='utf-8') as f:
        manifest = json.load(f)

    errors = []
    responses_dir = root / 'responses'
    manifest_files = manifest.get('files', {})

    # (1) 正向: manifest 列出的文件必须 match
    for filename, expected in manifest_files.items():
        fp = responses_dir / filename
        if not fp.exists():
            errors.append(f"文件缺失: {filename}")
            continue
        actual_sha = sha256_of_file(fp)
        if actual_sha != expected['sha256']:
            errors.append(
                f"SHA-256 mismatch {filename}: "
                f"expected {expected['sha256'][:16]}... got {actual_sha[:16]}..."
            )
        actual_bytes = fp.stat().st_size
        if actual_bytes != expected['bytes']:
            errors.append(
                f"Byte count mismatch {filename}: "
                f"expected {expected['bytes']} got {actual_bytes}"
            )

    # (2) v3.7.0 (M4 修复) 反向 cross-check: 不允许 manifest 外的 jsonl
    if responses_dir.exists():
        actual_files = {p.name for p in responses_dir.glob('*.jsonl')}
        unregistered = actual_files - set(manifest_files.keys())
        for name in sorted(unregistered):
            errors.append(
                f"未登记文件 (manifest 外): {name} — "
                f"可能是恶意篡改或忘 update manifest. 跑 write_manifest() 重新生成."
            )

    return len(errors) == 0, errors
