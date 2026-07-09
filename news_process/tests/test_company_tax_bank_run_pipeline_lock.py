"""税调 orchestrator 单实例锁 gate (COMPANY_TAX_BANK_COOC_PANEL_EXECUTION_PLAN v4, §3 T-D14)。

镜像 listed lock gate (tests/test_company_bank_run_pipeline_lock.py) 5 项 + 1 锚可读正例 (T-D8) = 6 项。
锁死锁的四条语义: 获取即落 PID / 持有者存活即拒 / 陈旧锁自愈 / 释放即清; +1 正例锁死
run_pipeline._expected_registry_anchor 能从 registry gate 件读出 64-hex 锚 (防锚对比静默降级为"不可读")。

全 mock (LOCK_FILE 重定向 tmp_path), **绝不碰真实 company_tax_bank/logs/ 锁路径** — 防干扰并发运行的
03。本 gate 存在即禁删锁。
⚠ 税调 run_pipeline 与 listed run_pipeline **同名模块** → 必须 spec_from_file_location 按绝对路径
加载并用唯一 sys.modules 名, 避免与 listed lock 测试的 "run_pipeline" 缓存碰撞 (T-D14/R3 P1-3)。
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
_RP_PATH = REPO / "company_tax_bank" / "run_pipeline.py"

# ⚠ 常量镜像 registry gate 件的 EXPECTED_TAX_REGISTRY_SHA256 (正例断言用; 两处同步 bump)
EXPECTED_TAX_REGISTRY_SHA256 = "4f580e3fc458be0c6aac6636f4ed1c3e0936f839c9b815161150e048b6e4c034"


def _load_rp():
    # spec_from_file_location + 唯一模块名: 避免 sys.modules["run_pipeline"] 被 listed lock 测试
    # 先行缓存后返回 listed 模块 (同名碰撞); sys.path 注入仅供该模块内潜在相对定位。
    sys.path.insert(0, str(REPO / "company_tax_bank"))
    spec = importlib.util.spec_from_file_location("company_tax_bank_run_pipeline", _RP_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rp = _load_rp()

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


def test_expected_registry_anchor_is_readable():
    """T-D8 正例: run_pipeline 须能从 tests/test_company_tax_bank_cooc_registry.py 读出
    EXPECTED_TAX_REGISTRY_SHA256 (行首+全名正则) — 不可读会让锚对比静默降级为"未对比", 掩盖漂移。
    本测试依赖 registry gate 件已写好该常量。"""
    anchor = rp._expected_registry_anchor()
    assert anchor is not None, \
        "run_pipeline 无法读出 EXPECTED_TAX_REGISTRY_SHA256 — 锚对比会静默降级为不可读"
    assert anchor == EXPECTED_TAX_REGISTRY_SHA256, "run_pipeline 读出的锚与 registry gate 件不一致"


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
