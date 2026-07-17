"""tests/test_orchestrator_guards.py — WP-A 守卫层单测 (八入口第六轮审计 A-6, 2026-07-18)。

覆盖三条仅在错误路径触发的守卫逻辑 (fast sweep 与入口正常复跑均走不到, 故必须单测):
  ① D1: --skip-unchanged 判据的 config/资源哈希不可读 → 保守返 (False, 含「保守重跑」),
     绝不让 OSError 冒顶 abort 整条 pipeline。patch 目标 =
     news_process.core.data_versioning.compute_config_file_hashes (run_pipeline_function
     内为函数级 import, rpf 模块无该属性可 patch)。
  ② N1: 预清理失败记录 + 成功后新鲜度复核 (三子场景: 记录成功→mtime 未变判 stale /
     mtime 已变不判 / 记录侧 stat 亦抛 [TOCTOU 消失] → 不记录、守卫不冲出)。
  ③ N3: PipelineLock._cleanup 的 sidecar 属主校验 (首行他人 PID → 保留; 本人 PID → 删除)。
"""
from __future__ import annotations

import logging
import os

import pytest

pytestmark = pytest.mark.fast

_LOG = logging.getLogger("test_orchestrator_guards")


# ---------------------------------------------------------------------------
# ① D1: config/资源哈希 OSError → 保守重跑 (不冒顶)
# ---------------------------------------------------------------------------

def test_skip_unchanged_config_hash_oserror_is_conservative(monkeypatch):
    import news_process.core.data_versioning as dv
    import news_process.run_pipeline_function as rpf

    def _boom(_dir):
        raise PermissionError("simulated: config yaml locked by AV/OneDrive")

    monkeypatch.setattr(dv, "compute_config_file_hashes", _boom)
    ok, reason = rpf._stage_skip_unchanged_is_safe("00_preprocessing.py")
    assert ok is False, "哈希不可读必须保守不跳, 而非抛异常/放行"
    assert "保守重跑" in reason and "PermissionError" in reason


# ---------------------------------------------------------------------------
# ② N1: 预清理失败记录 + 新鲜度复核 (三子场景)
# ---------------------------------------------------------------------------

def test_precleanup_pending_and_stale_unchanged_mtime(tmp_path, monkeypatch):
    """(a) remove 抛 OSError + stat 正常 → 记录; 复核 mtime 未变 → 判 stale。"""
    import news_process.run_pipeline_function as rpf

    f = tmp_path / "out.parquet"
    f.write_bytes(b"old-bytes")

    def _deny(_path):
        raise PermissionError("simulated: file held open")

    monkeypatch.setattr(os, "remove", _deny)
    pending = rpf._precleanup_stage_outputs(["out.parquet"], str(tmp_path), _LOG)
    assert list(pending) == [os.path.join(str(tmp_path), "out.parquet")]
    monkeypatch.undo()

    stale = rpf._stale_outputs_after_success(pending)
    assert stale == ["out.parquet"], "预清理失败且 mtime 未变的残留必须被判 stale"


def test_precleanup_stale_cleared_when_mtime_changes(tmp_path, monkeypatch):
    """(b) 同 (a) 但复核前文件被重写 (mtime 变) → 不判 stale。"""
    import news_process.run_pipeline_function as rpf

    f = tmp_path / "out.parquet"
    f.write_bytes(b"old-bytes")

    def _deny(_path):
        raise PermissionError("simulated: file held open")

    monkeypatch.setattr(os, "remove", _deny)
    pending = rpf._precleanup_stage_outputs(["out.parquet"], str(tmp_path), _LOG)
    monkeypatch.undo()
    assert pending, "前提: 已记录 pending"

    old_ns = next(iter(pending.values()))
    os.utime(f, ns=(old_ns + 10**9, old_ns + 10**9))  # 模拟子进程重写 (mtime 前移 1s)
    assert rpf._stale_outputs_after_success(pending) == []


def test_precleanup_toctou_vanish_records_nothing(tmp_path, monkeypatch):
    """(c) remove 报错但文件旋即消失 (TOCTOU) → stat 失败 → 不记录、不冲出循环。"""
    import news_process.run_pipeline_function as rpf

    f = tmp_path / "out.parquet"
    f.write_bytes(b"old-bytes")
    real_remove = os.remove

    def _remove_then_report_failure(path):
        real_remove(path)  # 文件真的消失了
        raise PermissionError("simulated: race — reported failure after vanish")

    monkeypatch.setattr(os, "remove", _remove_then_report_failure)
    pending = rpf._precleanup_stage_outputs(["out.parquet"], str(tmp_path), _LOG)
    assert pending == {}, "文件已消失等效已清理, 不得记录, 守卫不得抛异常"
    assert rpf._stale_outputs_after_success(pending) == []


# ---------------------------------------------------------------------------
# ③ N3: sidecar 属主校验
# ---------------------------------------------------------------------------

def test_sidecar_foreign_owner_is_preserved(tmp_path):
    from news_process.core.locking import PipelineLock

    lock = PipelineLock(_LOG, lock_dir=str(tmp_path))
    with lock:
        sidecar = lock.sidecar_path
        assert os.path.exists(sidecar)
        # 模拟窄竞态: 新持锁者已重写 sidecar (首行=他人 PID)
        with open(sidecar, "w", encoding="utf-8") as sf:
            sf.write("999999999\n2026-07-18 00:00:00\n")
    assert os.path.exists(sidecar), "他人所有的 sidecar 不得被旧实例删除 (N3)"
    os.remove(sidecar)  # 测试自清理


def test_sidecar_own_owner_is_removed(tmp_path):
    from news_process.core.locking import PipelineLock

    lock = PipelineLock(_LOG, lock_dir=str(tmp_path))
    with lock:
        sidecar = lock.sidecar_path
        assert os.path.exists(sidecar)
    assert not os.path.exists(sidecar), "本实例自己的 sidecar 释放时应正常删除"
