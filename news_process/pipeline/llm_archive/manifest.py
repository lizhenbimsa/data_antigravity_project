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
import platform
import sys
import time
from pathlib import Path
from typing import Optional

from news_process.core.logging import pct4, sig4

from .archive import _resolve_archive_root, sha256_of_file

logger = logging.getLogger(__name__)

MANIFEST_FILENAME = 'manifest.json'

# ── 经核验参考文献 (逐字照抄 APA-7 + DOI; 仅运行期日志用, 让 .log 自证方法学锚点) ──
# 白话: 本模块给冻结归档的每个 jsonl 文件算 SHA-256 + 把 frozen prompt 的哈希指纹
# 钉进 manifest.json (内容寻址 content-addressed 复现锚点)。Sandve 等 (2013) 的
# "可复现计算研究十条简单规则" 第 4-6 条 (记录所有中间结果 / 版本 / 精确出处) 正是
# 这套 per-file SHA-256 + prompt 指纹完整性清单的方法学依据 (同一 DOI 亦锚定姊妹的
# 内容寻址/SHA-256 模块 core/data_versioning.py, 见 LITERATURE_ANCHORS_SUPPLEMENT_IV)。
_MANIFEST_REFERENCES = {
    "reproducible_research": (
        "Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten "
        "simple rules for reproducible computational research. PLoS "
        "Computational Biology, 9(10), e1003285. "
        "https://doi.org/10.1371/journal.pcbi.1003285"
    ),
}


def _log_archive_env_and_config(
    action: str,
    root: Path,
    *,
    prompt_version_anchor: str = 'v8',
    archive_frozen_date: str = '2026-05-18',
    sidecar: Optional[Path] = None,
) -> None:
    """日志富集 (2026-06-24, 纯日志 golden-safe): LLM archive manifest 子步骤 banner。

    本模块是 *基础设施* 库 helper (无独立 stage main()/run_stage(), 共享调用方日志),
    生成 / 校验 ``manifest.json`` (per-file SHA-256 + 全局 metadata), 服务于 stage 21
    LLM 投票归档的密码学复现锚点 (CLAUDE.md: '勿删 _llm_cache.db' 同源思想 —
    manifest 把冻结归档的每文件 SHA-256 与 frozen prompt 指纹钉死, 保证 golden 可复现)。

    按富集手册 §0.5: called-by-runner / 无自有 main 的 helper 不重复 ENV/CONFIG 全块
    (那是 runner 入口职责), 只在被调函数起始处打一个**子步骤 banner**: 项目/环境指纹 +
    本步读写路径 + 可调锚点。基础设施虽非编号 stage, 但 per-file SHA-256 + frozen prompt
    指纹的内容寻址完整性清单本身即一项可引用的可复现方法 (Sandve et al. 2013 规则 4-6),
    故运行期附 📖 方法学引文 (见 _MANIFEST_REFERENCES)。失败 try/except 吞掉, 绝不让日志块
    崩调用阶段。
    """
    try:
        logger.info("  🧭 LLM Archive Manifest — %s", action)
        logger.info("     · 模块: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) | %s",
                    "LLM 投票归档完整性 (基础设施, 非编号 stage)")
        logger.info("     · 模块文件: %s", os.path.abspath(__file__))
        logger.info("     · 工作目录: %s", os.getcwd())
        logger.info("     · Python:   %s @ %s", sys.version.split()[0], sys.executable)
        logger.info("     · 平台:     %s | CPU 逻辑核=%s", platform.platform(), os.cpu_count())
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info("     · PID=%d | RUN_ID=%s | 纯 IO/哈希, 无 LLM·网络·API ($0, 确定性)",
                    os.getpid(), _run_id or '(未设置)')

        logger.info("  ⚙ 运行配置 (manifest 锚点)")
        logger.info("     · archive 根:      %s", root)
        logger.info("     · responses 目录:  %s", root / 'responses')
        logger.info("     · manifest 输出:   %s", root / MANIFEST_FILENAME)
        if sidecar is not None:
            logger.info("     · prompt 指纹 sidecar: %s", sidecar)
        logger.info("     · prompt_version_anchor=%s | archive_frozen_date=%s | schema_version=v1",
                    prompt_version_anchor, archive_frozen_date)
        logger.info("     · 完整性算法: per-file SHA-256 + 字节计数 + 行数(record_count) 单次 IO")
        # 📖 方法学依据 (运行期 emit, 让 .log 自证锚点): 可复现计算研究规则 4-6 (记录
        # 所有中间结果/版本/精确出处) 正是 per-file SHA-256 + prompt 指纹完整性清单的依据
        logger.info("  📖 完整性清单方法学依据:")
        logger.info("     📖 %s", _MANIFEST_REFERENCES["reproducible_research"])
    except Exception as e:  # noqa: BLE001
        logger.warning("  环境/配置信息打印失败 (不影响处理): %r", e)


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
    _t0 = time.time()
    prompt_sha256 = _read_prompt_sha256_from_sidecar()
    root = Path(root) if root else _default_root()
    # 子步骤 banner (日志富集 2026-06-24, golden-safe): 项目/环境指纹 + 读写路径 + 锚点
    _log_archive_env_and_config(
        'write_manifest',
        root,
        prompt_version_anchor=prompt_version_anchor,
        archive_frozen_date=archive_frozen_date,
        sidecar=_resolve_sidecar_path(),
    )
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
        f"({manifest['total_records']:,d} records, {manifest['total_bytes']:,d} bytes)"
    )
    # 📊 关键指标解读 (日志富集 2026-06-24): 对照阈值给好/临界/坏判读 — 纯日志
    try:
        n_files = len(manifest.get('files', {}))
        total_records = manifest['total_records']
        total_bytes = manifest['total_bytes']
        logger.info("  📊 归档完整性快照")
        logger.info("     · 归档 jsonl 文件数=%s | 总记录=%s | 总字节=%s",
                    f"{n_files:,d}", f"{total_records:,d}", f"{total_bytes:,d}")
        if prompt_sha256:
            logger.info("     · prompt_sha256 密码学指纹: %s… (复现锚点已钉死 ✅)",
                        prompt_sha256[:16])
        else:
            logger.warning("     · prompt_sha256=None ⚠ (sidecar 不可读, 复现锚点降级为人读 token "
                           "'%s'; 仅 'v8' 锚点弱于哈希指纹)", prompt_version_anchor)
        if n_files == 0:
            logger.warning("     · ⚠ responses 目录为空 — manifest 登记 0 文件 (归档尚未播种?)")
        elif total_records > 0:
            avg_rec = total_records / n_files
            avg_kb = (total_bytes / n_files) / 1024.0
            logger.info("     · 每文件均值: 记录=%s 条 | 体积=%s KB (越均匀=按日切分越规整 ✅)",
                        sig4(avg_rec), sig4(avg_kb))
            # 📊 每文件五数概括 (日志富集 2026-06-29, 纯日志 golden-safe): record_count 与
            # 字节体积本已逐文件存于 manifest['files'], 此处只读不改 — min/Q1/中位/Q3/max
            # 揭示按日切分的离散度, 用以发现异常巨大或近空 (空 jsonl) 的归档文件 (均值线看不出)。
            # 结果仅喂 logger, 绝不回流下游, 失败被内层 try/except 吞掉。
            try:
                import statistics as _stats
                _recs = sorted(f['record_count'] for f in manifest['files'].values())
                _kbs = sorted((f['bytes'] / 1024.0) for f in manifest['files'].values())
                if len(_recs) >= 2:
                    _rq = _stats.quantiles(_recs, n=4, method='inclusive')  # [Q1, 中位, Q3]
                    _kq = _stats.quantiles(_kbs, n=4, method='inclusive')
                    logger.info("     · 每文件记录分布: min=%s | Q1=%s | 中位=%s | Q3=%s | max=%s 条",
                                f"{_recs[0]:,d}", sig4(_rq[0]), sig4(_rq[1]), sig4(_rq[2]),
                                f"{_recs[-1]:,d}")
                    logger.info("     · 每文件体积分布: min=%s | Q1=%s | 中位=%s | Q3=%s | max=%s KB",
                                sig4(_kbs[0]), sig4(_kq[0]), sig4(_kq[1]), sig4(_kq[2]),
                                sig4(_kbs[-1]))
                    if _recs[0] == 0:
                        logger.warning("     · ⚠ 存在 record_count=0 的空 jsonl — 请核查该日归档是否漏播种")
                else:
                    logger.info("     · 每文件分布: 仅 %s 个文件, 五数概括从略 (n<2)", f"{n_files:,d}")
            except Exception as _de:  # noqa: BLE001
                logger.warning("     · 每文件分布打印失败 (不影响处理): %r", _de)
        else:
            logger.warning("     · ⚠ 文件数=%s 但总记录=0 — 可能存在空 jsonl, 请核查", f"{n_files:,d}")
        logger.info("  ⏱ write_manifest 墙钟耗时: %s 秒", sig4(time.time() - _t0))
    except Exception as e:  # noqa: BLE001
        logger.warning("  完整性快照打印失败 (不影响处理): %r", e)
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
    _t0 = time.time()
    root = Path(root) if root else _default_root()  # audit S3: 与写入同源
    # 子步骤 banner (日志富集 2026-06-24, golden-safe): 校验入口环境/路径指纹
    _log_archive_env_and_config('verify_manifest', root)
    manifest_path = root / MANIFEST_FILENAME
    if not manifest_path.exists():
        logger.warning("  ❌ manifest 不存在: %s — 校验直接判失败", manifest_path)
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

    # 📊 关键指标解读 (日志富集 2026-06-24): 双向 cross-check 通过率 + verdict — 纯日志
    try:
        n_registered = len(manifest_files)
        n_errors = len(errors)
        ok = n_errors == 0
        # 通过率 = (已登记文件数 − 错误数) / 已登记文件数; 分母为 0 时记 100% (空归档无可校验项)
        pass_rate = 1.0 if n_registered == 0 else max(0.0, (n_registered - n_errors)) / n_registered
        logger.info("  📊 manifest 双向 cross-check 结果")
        logger.info("     · 登记文件=%s | 不一致/多余项=%s | 正向通过率≈%s",
                    f"{n_registered:,d}", f"{n_errors:,d}", pct4(pass_rate))
        if ok:
            logger.info("     · ✅ 完整一致: SHA-256/字节/行数全部 match 且无 manifest 外 jsonl "
                        "(归档冻结完整, 复现锚点可信)")
        else:
            logger.error("     · ❌ 校验失败: %s 项不一致 — 归档被改动或 manifest 过期, 须跑 "
                         "write_manifest() 重生", f"{n_errors:,d}")
            for _e in errors[:10]:
                logger.error("       - %s", _e)
        logger.info("  ⏱ verify_manifest 墙钟耗时: %s 秒", sig4(time.time() - _t0))
    except Exception as e:  # noqa: BLE001
        logger.warning("  校验结果解读打印失败 (不影响处理): %r", e)
    return len(errors) == 0, errors
