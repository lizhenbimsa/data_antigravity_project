"""LLM Archive 核心模块 — append-only 归档 LLM raw response.

v3.7.0 关键不变量:
1. Append-only: 一旦写入不可修改 (反向追溯保证)
2. 按日切分文件 (data/llm_archive/responses/YYYY-MM-DD.jsonl)
3. 每条 record 自带 cache_key (与 core.caching.LLMCache 反向 lookup)
4. model_version 与 model_id 分离 (model_id 是配置名, model_version 是 API 返回的实际版本)
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import logging
import os
import threading
import uuid
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _resolve_archive_root() -> Path:
    """v3.7.0 (M3 修复): archive 根目录解析顺序.

    1. env var LLM_ARCHIVE_ROOT (CI / 测试 override)
    2. core.config.load_config()['paths']['llm_archive'] (项目惯例)
    3. fallback: <data_processed parent>/llm_archive (与 data/processed/ 平级)

    返回绝对路径, 避免 cwd 依赖.
    """
    env_path = os.environ.get('LLM_ARCHIVE_ROOT')
    if env_path:
        return Path(env_path).resolve()

    try:
        from news_process.core.config import load_config
        cfg = load_config()
        archive_path = cfg.get('paths', {}).get('llm_archive')
        if archive_path:
            return Path(archive_path).resolve()
        # fallback: data_processed parent / llm_archive
        data_processed = cfg.get('paths', {}).get('data_processed')
        if data_processed:
            return Path(data_processed).resolve().parent / 'llm_archive'
    except Exception:
        # config 不可用时 (如纯 unit test 环境), 用相对路径
        pass

    # 最终 fallback: 相对项目 root (脚本通常从 repo root 跑)
    return Path('data/llm_archive').resolve()


# 默认归档目录 (lazy resolved, 见 _get_default_archive)
DEFAULT_ARCHIVE_ROOT = Path('data/llm_archive')  # 兼容旧 import; runtime 用 _resolve_archive_root
DEFAULT_RESPONSES_DIR = DEFAULT_ARCHIVE_ROOT / 'responses'

# JSONL record 必填字段 (V4 F-P2.1 reproducibility 强约束).
# v3.7.0 (m1 修复): 区分 caller-required vs auto-filled.
CALLER_REQUIRED_FIELDS = frozenset({
    'cache_key',
    'model_id',
    'model_version',   # API 返回的实际 version, 与 model_id (配置名) 分离
    'prompt_version',
    'temperature',
    'prompt',
    'response_raw',
    'api_endpoint',
})
AUTO_FILLED_FIELDS = frozenset({'request_id', 'timestamp_utc'})
REQUIRED_FIELDS = CALLER_REQUIRED_FIELDS | AUTO_FILLED_FIELDS  # 兼容旧引用


class LLMArchive:
    """LLM raw response 永久归档.

    Append-only 写入, 不修改不删除. 与 core.caching.LLMCache 通过 cache_key
    互联 (LLMCache 是 prompt → response 加速 cache, LLMArchive 是 reproducibility ledger).

    Thread-safe via internal lock.

    Usage:
        archive = LLMArchive()  # 使用默认 data/llm_archive/
        archive.append({
            'cache_key': '...',
            'model_id': 'gpt-5.4-nano',
            'model_version': 'gpt-5.4-nano-2026-01',
            ...
        })
    """

    def __init__(self, root: Optional[Path] = None):
        """初始化归档.

        Args:
            root: 归档根目录. 默认走 _resolve_archive_root()
                (= config paths.llm_archive 解析后的 repo-root data/llm_archive,
                绝对路径, CWD 无关)。
        """
        # audit A 评审修复 (2026-05-30): 默认 root 走 _resolve_archive_root() 而非
        # cwd 相对的 DEFAULT_ARCHIVE_ROOT — 后者会让从 news_process/ 子目录直接
        # new LLMArchive() 时落到被 .gitignore 排除的旧位置 (路径漂移残留)。
        self.root = Path(root) if root else _resolve_archive_root()
        self.responses_dir = self.root / 'responses'
        self.responses_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        # 进程级计数器 (与 LLMCache 风格一致)
        self._writes = 0
        self._bytes_written = 0

    def _current_file(self) -> Path:
        """当前应写入的 JSONL 文件 (按 UTC 日切分).

        v3.7.0 (M2 修复): 跨午夜竞态保护 — 进入 critical section 后再次确认
        日期, 避免 thread A 在 23:59:59 取日期, thread B 在 00:00:00 同时取
        不同日期, 然后并发写不同文件让 manifest 漏文件的边界 bug.

        本方法 *本身* 不持锁; 调用方必须先持 self._lock.
        """
        today = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')
        return self.responses_dir / f'{today}.jsonl'

    def _prepare_record(self, record: dict) -> tuple[dict, str]:
        """填充 request_id / timestamp_utc + 校验必填. 返回 (record, line)."""
        if 'request_id' not in record:
            record['request_id'] = str(uuid.uuid4())
        if 'timestamp_utc' not in record:
            record['timestamp_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()

        missing = REQUIRED_FIELDS - set(record.keys())
        if missing:
            raise ValueError(
                f"LLMArchive.append 缺必填字段: {missing}. "
                f"V4 F-P2.1 reproducibility 强约束要求完整 metadata."
            )
        line = json.dumps(record, ensure_ascii=False, sort_keys=True) + '\n'
        return record, line

    def append(self, record: dict) -> str:
        """Append 单条 record 到归档.

        Args:
            record: caller 必填 8 字段 (cache_key / model_id / model_version /
                    prompt_version / temperature / prompt / response_raw /
                    api_endpoint). request_id 与 timestamp_utc 自动填充.

        Returns:
            str: request_id (UUID v4)

        Raises:
            ValueError: 若 record 缺必填字段.
        """
        record, line = self._prepare_record(record)
        # JSONL append (小于 PIPE_BUF 的小写入在 OS 层面是原子的)
        # _current_file() 在 lock 内调用以避免跨午夜 race (M2 修复)
        with self._lock:
            fp = self._current_file()
            with fp.open('a', encoding='utf-8') as f:
                f.write(line)
            self._writes += 1
            self._bytes_written += len(line.encode('utf-8'))
        return record['request_id']

    def append_batch(self, records: list[dict]) -> list[str]:
        """v3.7.0 (M15 修复): 批量 append, 单次 lock + 单次 file open.

        embedding API 一次 batch N 个 (N up to 100) → 这是性能关键路径.
        与 append() 行为一致, 仅消除 N 次 lock contention.

        Args:
            records: list of records (每条必含 REQUIRED_FIELDS).

        Returns:
            list[str]: 各 record 的 request_id (顺序与 input 一致).
        """
        if not records:
            return []
        prepared = [self._prepare_record(r) for r in records]
        rids = [r['request_id'] for r, _ in prepared]
        lines = ''.join(line for _, line in prepared)
        bytes_total = len(lines.encode('utf-8'))

        with self._lock:
            fp = self._current_file()
            with fp.open('a', encoding='utf-8') as f:
                f.write(lines)
            self._writes += len(records)
            self._bytes_written += bytes_total
        return rids

    def stats(self) -> dict:
        """返回进程级写入统计.

        Note: ``current_file`` 字段是 *调用瞬间* 的 UTC 日切分文件; 跨午夜
        后续 append 会切到新文件. 仅用于诊断, 不要把此值作为永久 anchor.
        """
        with self._lock:
            current = str(self._current_file())
            return {
                'writes': self._writes,
                'bytes_written': self._bytes_written,
                'current_file': current,
            }


def archive_record(
    *,
    cache_key: str,
    model_id: str,
    model_version: str,
    prompt: str,
    response_raw: str,
    prompt_version: str = 'v0',
    temperature: float = 0.0,
    api_endpoint: str = '',
    http_status: int = 200,
    http_headers: Optional[dict] = None,
    archive: Optional[LLMArchive] = None,
) -> str:
    """便捷函数 — 归档单条 record.

    设计为现有 LLM 调用 callsite 一行接入:
        from news_process.pipeline.llm_archive import archive_record

        response = client.chat.completions.create(...)
        archive_record(
            cache_key=cache_key,
            model_id='gpt-5.4-nano',
            model_version=response.model,          # API 返回的实际 version!
            prompt=prompt,
            response_raw=response.model_dump_json(),
            prompt_version='v8',
        )

    Args:
        cache_key: 与 core.caching.LLMCache._make_key 一致, 用于反向 lookup.
        model_id: 配置名 (例 "gpt-5.4-nano").
        model_version: API 返回的实际 version (例 "gpt-5.4-nano-2026-01").
        prompt: 完整 prompt 文本.
        response_raw: API 返回的完整 JSON (不仅是 content).
        prompt_version: prompt 模板版本 (v3.5.1 frozen = "v8").
        temperature: LLM 温度 (默认 0.0).
        api_endpoint: API 完整 URL.
        http_status: HTTP 响应码.
        http_headers: HTTP headers (optional, default None 表示不归档 headers).
        archive: LLMArchive 实例 (None 时用默认 singleton).

    Returns:
        str: request_id (UUID v4)
    """
    if archive is None:
        archive = _get_default_archive()
    record = {
        'cache_key': cache_key,
        'model_id': model_id,
        'model_version': model_version,
        'prompt_version': prompt_version,
        'temperature': temperature,
        'prompt': prompt,
        'response_raw': response_raw,
        'api_endpoint': api_endpoint,
        'http_status': http_status,
    }
    if http_headers is not None:
        record['http_headers'] = http_headers
    return archive.append(record)


# Singleton lazy-init.
# v3.7.0 (m4 简化): Python GIL 保证 dict 赋值原子, 单 lock 已足够.
# v3.7.0 (M3 修复): 用 _resolve_archive_root() 计算实际路径, 而非 DEFAULT_ARCHIVE_ROOT 字符串.
_DEFAULT_ARCHIVE: Optional[LLMArchive] = None
_DEFAULT_LOCK = threading.Lock()


def _get_default_archive() -> LLMArchive:
    """获取默认 LLMArchive singleton (lazy init via config-resolved path)."""
    global _DEFAULT_ARCHIVE
    if _DEFAULT_ARCHIVE is not None:
        return _DEFAULT_ARCHIVE
    with _DEFAULT_LOCK:
        if _DEFAULT_ARCHIVE is None:
            _DEFAULT_ARCHIVE = LLMArchive(root=_resolve_archive_root())
    return _DEFAULT_ARCHIVE


def sha256_of_file(path: Path) -> str:
    """计算单个文件 SHA-256 hex digest.

    v3.7.0 (m2 修复): 显式 error handling — file disappeared / permission
    denied 时 raise 含上下文的 OSError (而非 cryptic bytes-read exception).
    """
    h = hashlib.sha256()
    p = Path(path)
    try:
        with p.open('rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
    except FileNotFoundError as exc:
        raise OSError(f"sha256_of_file: 文件不存在 {p}") from exc
    except PermissionError as exc:
        raise OSError(f"sha256_of_file: 权限拒绝 {p}") from exc
    return h.hexdigest()
