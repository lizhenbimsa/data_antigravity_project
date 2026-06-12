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
import os
from pathlib import Path
from typing import Optional

from .archive import _resolve_archive_root, sha256_of_file

logger = logging.getLogger(__name__)

MANIFEST_FILENAME = 'manifest.json'


def _default_root() -> Path:
    """audit S3 修复 (2026-05-30): 写入与校验共用同一 archive root 解析。

    早期 manifest 三函数 (compute/write/verify) 在 ``root=None`` 时回落
    ``DEFAULT_ARCHIVE_ROOT=Path('data/llm_archive')`` (cwd 相对), 而写入端
    archive.py 走 ``_resolve_archive_root()`` (config 解析的绝对路径)。两者从
    repo 根运行时锚定到不同目录, 致 ``verify_manifest()`` 扫错目录假阴性。
    此处统一改用 ``_resolve_archive_root()``, 保证写/验同源。
    """
    return _resolve_archive_root()


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
    prompt_sha256: Optional[str] = None,
    archive_frozen_date: str = '2026-05-18',
) -> dict:
    """扫描 archive 目录, 生成 manifest dict.

    v3.7.0 (M5 修复): 单次 IO 同时算 sha256 + bytes + line count.

    Args:
        root: archive 根目录 (默认走 _resolve_archive_root, 见 _default_root)。
        prompt_version_anchor: 锚定的 prompt version token (v3.5.1 = "v8").
        prompt_sha256: audit S1 修复 — frozen prompt 的 SHA-256 指纹 (来自
            v3.5.1 sidecar, 比 token 'v8' 更强的复现锚点); None 表示 sidecar 不可读。
        archive_frozen_date: 归档 frozen 日期.

    Returns:
        dict: manifest 内容 (未写入文件).
    """
    root = Path(root) if root else _default_root()
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
        'prompt_sha256': prompt_sha256,  # audit S1: 密码学指纹 (None=sidecar 不可读)
        'files': files,
        'total_records': sum(f['record_count'] for f in files.values()),
        'total_bytes': sum(f['bytes'] for f in files.values()),
    }
    return manifest


def _resolve_sidecar_path() -> Path:
    """fix(omni-g-tonellms-05, 2026-06-11): sidecar 路径经 config 解析为绝对路径。

    仿 ``archive._resolve_archive_root`` (audit S3 写/验同源原则), 解析顺序:
    1. env var ``LLM_ARCHIVE_SIDECAR_PATH`` (CI / 测试 override);
    2. ``load_config()['paths']['output_dir']`` 锚定的绝对路径 — 消除
       cwd-相对路径漂移: 此前从 news_process/ 以外的 cwd (如 CLAUDE.md 规定的
       pytest 仓库父根, 或任意 CI 工作目录) 调 ``write_manifest`` 时, sidecar
       静默找不到 → ``prompt_sha256=None`` 写入 manifest, 密码学指纹锚点无声丢失;
    3. config 不可用时 (纯 unit test 环境) 回落 cwd-相对路径 (历史行为)。
    """
    env_path = os.environ.get('LLM_ARCHIVE_SIDECAR_PATH')
    if env_path:
        return Path(env_path).resolve()
    try:
        from news_process.core.config import load_config
        out_dir = load_config().get('paths', {}).get('output_dir')
        if out_dir:
            return (Path(out_dir) / 'v3_5_1_constants.json').resolve()
    except Exception:
        pass
    return Path('data/processed/v3_5_1_constants.json')


def _read_prompt_sha256_from_sidecar() -> Optional[str]:
    """v3.7.0 (m5) + audit S1 修复 (2026-05-30): 从 v3.5.1 sidecar JSON 读
    frozen prompt 的 SHA-256 指纹。

    早期实现误读两个 *不存在* 的键 (``prompt_v8_sha256_anchor`` /
    ``prompt_version``), 致此函数对真值 sidecar 永远返回 None — 一个永不生效
    的 dead branch (write_manifest 因此永久落回硬编码)。真值 sidecar
    (``data/processed/v3_5_1_constants.json``) 实际存的是 prompt 内容的
    SHA-256 哈希 (键 ``prompt_v8_sha256``), 而非版本 token 字符串。本修复读对
    真值键, 让 manifest 能记录密码学指纹 (比版本 token 'v8' 更强的复现锚点);
    sidecar 缺失 / 损坏时返回 None。

    fix(omni-g-tonellms-05, 2026-06-11): 路径改经 ``_resolve_sidecar_path``
    config 绝对解析 (同批 audit S3 修复在本文件 ``_default_root`` 已做, sidecar
    读取漏改的残留); 缺失/读取失败改 ``logger.warning`` 留痕, 不再静默吞错。
    """
    sidecar = _resolve_sidecar_path()
    if not sidecar.exists():
        logger.warning(
            f"prompt sha256 sidecar 不存在: {sidecar}; "
            "manifest['prompt_sha256'] 将记为 None (密码学指纹锚点缺失)"
        )
        return None
    try:
        with sidecar.open('r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('prompt_v8_sha256')
    except Exception as exc:
        logger.warning(
            f"prompt sha256 sidecar 读取失败 ({sidecar}): {exc!r}; "
            "manifest['prompt_sha256'] 将记为 None"
        )
        return None


# 向后兼容别名: 历史测试 (test_llm_archive.py) 与早期引用按旧名调用。
# audit S1 修复后语义 = 读 prompt 的 SHA256 指纹 (而非不存在的 version token)。
_read_prompt_version_anchor_from_sidecar = _read_prompt_sha256_from_sidecar


def write_manifest(
    root: Optional[Path] = None,
    *,
    prompt_version_anchor: str = 'v8',
    archive_frozen_date: str = '2026-05-18',
) -> Path:
    """生成并写入 manifest.json 到 archive 根目录.

    v3.7.0 (m5) + audit S1/S3 修复 (2026-05-30):
    - root=None 时走 _default_root() (= _resolve_archive_root), 与写入端同源
      (修早期 cwd-相对 DEFAULT_ARCHIVE_ROOT 致 verify 扫错目录的路径漂移)。
    - prompt 的 SHA-256 指纹从 v3.5.1 sidecar 读 (修早期读错 key 的 dead branch),
      记入 manifest['prompt_sha256']; prompt_version_anchor 保留人读 token 'v8'。
    """
    prompt_sha256 = _read_prompt_sha256_from_sidecar()
    root = Path(root) if root else _default_root()
    manifest = compute_manifest(
        root,
        prompt_version_anchor=prompt_version_anchor,
        prompt_sha256=prompt_sha256,
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
    root = Path(root) if root else _default_root()  # audit S3: 与写入同源
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
