"""银企共现 orchestrator 单实例锁 gate (2026-07-07 并发双跑事故防复发)。

事故: 两个 run_pipeline 实例相差 46 秒并发全链, 交错覆写同一套日志 (PID 混写/时间戳倒流/
行粘连) 与 ~13GB 产物, company_bank_branchw_panel.dta 留下 688MB 半成品。
本 gate 锁死锁的四条语义: 获取即落 PID / 持有者存活即拒 / 陈旧锁自愈 / 释放即清。
全 mock (LOCK_FILE 重定向 tmp_path), 不碰生产 logs/ 目录。本 gate 存在即禁删锁。
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "company_listed_bank"))

rp = importlib.import_module("run_pipeline")

pytestmark = pytest.mark.fast


@pytest.fixture()
def lock_in_tmp(tmp_path, monkeypatch):
    lock = tmp_path / "_run_pipeline.lock"
    monkeypatch.setattr(rp, "LOCK_FILE", lock)
    return lock


def test_acquire_writes_own_pid_and_release_removes(lock_in_tmp):
    fd = rp._acquire_single_instance_lock()
    try:
        assert lock_in_tmp.exists()
        assert int(lock_in_tmp.read_text(encoding="ascii")) == os.getpid()
    finally:
        rp._release_single_instance_lock(fd)
    assert not lock_in_tmp.exists(), "释放后锁文件必须消失"


def test_second_instance_rejected_while_holder_alive(lock_in_tmp):
    # 持有者 = 本进程 (必然存活) → 第二次获取必须 fail-loud SystemExit(1), 绝不静默排队
    fd = rp._acquire_single_instance_lock()
    try:
        with pytest.raises(SystemExit) as ei:
            rp._acquire_single_instance_lock()
        assert ei.value.code == 1
        assert lock_in_tmp.exists(), "拒绝路径不得动到持有者的锁"
    finally:
        rp._release_single_instance_lock(fd)


def test_stale_lock_from_dead_pid_is_cleared_and_acquired(lock_in_tmp):
    # 陈旧锁 (上次异常退出残留, 持有者已死) → 自愈: 清除后本次获取成功
    psutil = pytest.importorskip("psutil")
    dead = max(psutil.pids()) + 10007
    while psutil.pid_exists(dead):  # 理论碰撞兜底
        dead += 1
    lock_in_tmp.write_text(str(dead), encoding="ascii")
    fd = rp._acquire_single_instance_lock()
    try:
        assert int(lock_in_tmp.read_text(encoding="ascii")) == os.getpid()
    finally:
        rp._release_single_instance_lock(fd)


def test_unreadable_lock_treated_as_stale(lock_in_tmp):
    # 内容不可解析 (半写/损坏) 视为陈旧锁, 不得死锁
    lock_in_tmp.write_text("not-a-pid", encoding="ascii")
    fd = rp._acquire_single_instance_lock()
    try:
        assert int(lock_in_tmp.read_text(encoding="ascii")) == os.getpid()
    finally:
        rp._release_single_instance_lock(fd)


def test_main_dry_run_never_touches_lock(lock_in_tmp):
    # --dry-run 只打印命令: 不获取锁 (只读路径), 也不留残留
    rc = rp.main(["--dry-run"])
    assert rc == 0
    assert not lock_in_tmp.exists()
