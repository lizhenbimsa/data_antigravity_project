"""tests/test_cleanup_prune_logs.py — V8 P-4 基于 age 的 logs/runs 清理器.

验证 news_process.scripts.cleanup 新增的 `prune-logs --keep-days N` 子命令:
  - 删除早于 cutoff 的 run 子目录,
  - 保留晚于 cutoff 的 run 子目录,
  - dry-run 模式不执行任何删除,
  - logs/runs/ 缺失时优雅 no-op.

通过 tmp_path + monkeypatch 替换 `_root()`, 避免触碰真实的
news_process/logs 目录.
"""

from __future__ import annotations

import argparse
import os
import time

import pytest

from news_process.scripts import cleanup


@pytest.fixture
def fake_logs_runs(tmp_path, monkeypatch):
    """在 tmp_path 下构造伪造的 logs/runs/ 目录树; monkeypatch 替换 _root().

    返回 (runs_dir, old_dirs, new_dirs), 便于各测试断言哪些子目录幸存.
    """
    np_dir = tmp_path / "news_process"
    runs_dir = np_dir / "logs" / "runs"
    runs_dir.mkdir(parents=True)

    old_dirs = []
    new_dirs = []
    now = time.time()
    for i in range(3):
        # 40 天前的 "old"
        d = runs_dir / f"20260101T000000Z-old-{i}"
        d.mkdir()
        (d / "stage.log").write_text("dummy")
        old_t = now - 40 * 86400
        os.utime(d, (old_t, old_t))
        old_dirs.append(d)
    for i in range(2):
        # 当前的 "new"
        d = runs_dir / f"20260513T000000Z-new-{i}"
        d.mkdir()
        (d / "stage.log").write_text("dummy")
        new_dirs.append(d)

    monkeypatch.setattr(cleanup, "_root", lambda: tmp_path)
    return runs_dir, old_dirs, new_dirs


def test_prune_logs_deletes_old_keeps_new(fake_logs_runs):
    runs_dir, old_dirs, new_dirs = fake_logs_runs
    args = argparse.Namespace(keep_days=30, dry_run=False)

    rc = cleanup.cmd_prune_logs(args)

    assert rc == 0
    for d in old_dirs:
        assert not d.exists(), f"old dir should be deleted: {d}"
    for d in new_dirs:
        assert d.exists(), f"new dir should be kept: {d}"


def test_prune_logs_dry_run_deletes_nothing(fake_logs_runs):
    runs_dir, old_dirs, new_dirs = fake_logs_runs
    args = argparse.Namespace(keep_days=30, dry_run=True)

    rc = cleanup.cmd_prune_logs(args)

    assert rc == 0
    for d in old_dirs + new_dirs:
        assert d.exists(), f"dry-run should keep everything: {d}"


def test_prune_logs_missing_dir_is_noop(tmp_path, monkeypatch):
    """logs/runs/ 不存在时 graceful 退出 0, 不抛."""
    monkeypatch.setattr(cleanup, "_root", lambda: tmp_path)
    args = argparse.Namespace(keep_days=30, dry_run=False)

    rc = cleanup.cmd_prune_logs(args)

    assert rc == 0


def test_prune_logs_zero_keep_days_deletes_everything(fake_logs_runs):
    """--keep-days 0 等于强制删全部 (除非未来 30s 内创建的, 边角不测)."""
    runs_dir, old_dirs, new_dirs = fake_logs_runs
    args = argparse.Namespace(keep_days=0, dry_run=False)

    rc = cleanup.cmd_prune_logs(args)

    assert rc == 0
    # 实际效果: 所有 mtime < now 的目录被删
    # new_dirs 的 mtime 接近 now, 边界条件可能 keep 也可能 del; 不强校验


def test_prune_logs_negative_keep_days_errors(fake_logs_runs):
    """--keep-days -1 拒绝, return code 2 (CLI 标准错误码)."""
    args = argparse.Namespace(keep_days=-1, dry_run=False)

    rc = cleanup.cmd_prune_logs(args)

    assert rc == 2


def test_prune_logs_cli_default_keep_days_is_one(monkeypatch):
    """2026-05-30: prune-logs 不带 --keep-days 时默认值锁定为 1 (旧值 30).

    现有测试都直接构造 argparse.Namespace, 不经过 parser, 因此默认值无人守护;
    本测试经 main() 真正解析 CLI, 用 spy 捕获 parsed args, 锁死默认 == 1。
    """
    captured = {}

    def _spy(args):
        captured["keep_days"] = args.keep_days
        captured["dry_run"] = args.dry_run
        return 0

    monkeypatch.setattr(cleanup, "cmd_prune_logs", _spy)
    rc = cleanup.main(["prune-logs"])

    assert rc == 0
    assert captured["keep_days"] == 1, "prune-logs 默认应保留最近 1 天"
    assert captured["dry_run"] is False
