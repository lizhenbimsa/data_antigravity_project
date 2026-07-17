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


# ⚠ 常量镜像 registry gate 件的主锚/激活代副锚 (正例断言用; RR3-Z-MAJ-1: 禁裸姐妹
# import — tests/ 目录不在 sys.path, 单跑本文件会 ModuleNotFoundError 假红; 两处
# 同步 bump; G9 收口后随姊妹件回归单值时一并收拢)
_MIRROR_REGISTRY_SHA256 = "023cdc9158ec52ba60f148f59b520a9195a02a3086da95b641db93c5d082dd30"
_MIRROR_REGISTRY_SHA256_ACTIVATED = "4a2f79fd932974b090db338a1441ea95934e6ff22a5cb61b0ed8c5f29871d4e1"


def test_expected_registry_anchor_and_activated_are_readable():
    """D-4fix (2026-07-18): 主锚+激活代副锚双提取器均须能从 registry gate 件读出 64-hex —
    副锚不可读 = 激活代判读静默 fail-open (「勿 bump 主锚」保护永不生效, 重演 D-1 拉锯)。"""
    assert rp._expected_registry_anchor() == _MIRROR_REGISTRY_SHA256
    activated = rp._expected_registry_anchor_activated()
    assert activated is not None and len(activated) == 64, \
        "run_pipeline 无法读出 EXPECTED_REGISTRY_SHA256_ACTIVATED (副锚正则 fail-open)"
    assert activated == _MIRROR_REGISTRY_SHA256_ACTIVATED


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


# ── 五入口诊断整改 gate (2026-07-09): A5 锁 try/finally 边界 + A9 os.write fd 清理 ──

def test_init_logging_exception_still_releases_lock(lock_in_tmp, monkeypatch):
    """A5: _init_stage_logging() 抛异常时 main() 的 try/finally 仍释放锁 —— 原实现 acquire+_init
    在 try 外, _init 异常则 finally 不执行 → fd + 锁残留。修复后异常路径也释放锁。"""
    def _boom():
        raise RuntimeError("simulated _init_stage_logging failure")
    monkeypatch.setattr(rp, "_init_stage_logging", _boom)
    with pytest.raises(RuntimeError, match="simulated _init_stage_logging failure"):
        rp.main(["--steps", "01"])
    assert not lock_in_tmp.exists(), "A5: _init_stage_logging 异常后锁必须被 finally 释放"


def test_os_write_failure_cleans_fd_and_lock(lock_in_tmp, monkeypatch):
    """A9: os.write 失败(如 ENOSPC)时清理 fd + 删 0 字节锁再抛 —— 原实现绕过 except FileExistsError
    上抛且 fd 未 close → fd 泄漏 + 0 字节残锁。仅对本进程 PID 写入抛, 不干扰其它 os.write。"""
    real_write = os.write
    def _boom(fd, data):
        if data == str(os.getpid()).encode("ascii"):
            raise OSError(28, "No space left on device")
        return real_write(fd, data)
    monkeypatch.setattr(rp.os, "write", _boom)
    with pytest.raises(OSError):
        rp._acquire_single_instance_lock()
    assert not lock_in_tmp.exists(), "A9: os.write 失败后 0 字节锁文件必须被清理"
