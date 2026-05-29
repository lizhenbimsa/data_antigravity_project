"""审计修复 (2026-05-30) 的回归守护测试。

集中守护 fix-verification 工作流指出的两个"修复正确但缺回归测试"缺口:
- S7: run_stage 的 Ctrl+C 路径必须终止子进程树并 re-raise (进程组隔离后子进程
  不再随控制台信号终止, 否则中断时成孤儿)。
- B/S10: stage 11/12 的 save 必须把词典文件纳入血缘 input_files, 否则编辑词典
  内容 (路径不变) 后 verify_data_integrity 假阳性 PASS。

放在独立文件以与前序会话的 dual-embedding WIP (test_lineage_input_contract.py
等) 编辑隔离。
"""
from __future__ import annotations

import inspect
import io
import logging
from unittest.mock import MagicMock, patch

import pytest

from news_process.core import stage as stage_mod
from news_process.pipeline.filtering import news_bank, news_fintech


# ---------------------------------------------------------------------------
# S7: run_stage Ctrl+C → 终止进程树 + re-raise
# ---------------------------------------------------------------------------
def test_run_stage_keyboardinterrupt_terminates_tree_and_reraises(tmp_path):
    """audit S7 复核闭环: 用户 Ctrl+C 时, run_stage 必须 (1) 调 _terminate_process_tree
    终止子进程树 (进程组隔离后子进程不再随控制台信号终止), (2) re-raise KeyboardInterrupt
    让 orchestrator 照常停止。删掉 except KeyboardInterrupt 分支 → 子进程中断后成孤儿,
    本测试变红。
    """
    script = tmp_path / "s.py"
    script.write_text("print('x')", encoding="utf-8")
    logger = logging.getLogger("test_s7_ki")

    fake_proc = MagicMock()
    fake_proc.pid = 99999
    # reader 线程对空流 readline 立即得 '' (EOF) → 线程秒退, 不挂起 join
    fake_proc.stdout = io.StringIO("")
    fake_proc.stderr = io.StringIO("")
    fake_proc.poll.return_value = None
    fake_proc.wait.side_effect = KeyboardInterrupt()

    with patch.object(stage_mod.subprocess, "Popen", return_value=fake_proc), \
         patch.object(stage_mod, "_terminate_process_tree") as mock_term:
        with pytest.raises(KeyboardInterrupt):
            stage_mod.run_stage("s.py", "测试中断", logger, base_dir=str(tmp_path))
        assert mock_term.called, (
            "Ctrl+C 路径未调用 _terminate_process_tree — 进程组隔离后子进程会成孤儿"
        )


def test_run_stage_has_keyboardinterrupt_handler():
    """audit S7: 源码层守护 — run_stage 必须显式 except KeyboardInterrupt
    (BaseException 不被 except Exception 捕获)。"""
    src = inspect.getsource(stage_mod.run_stage)
    assert "except KeyboardInterrupt" in src
    # 必须在中断分支内终止进程树 + re-raise。
    # 注: 用真实子句签名 "except Exception as e:" 作分隔, 避免命中本分支注释里
    # 文字提及的 "except Exception" (那里是反引号内的说明文本)。
    ki_block = (src.split("except KeyboardInterrupt", 1)[1]
                   .split("except Exception as e:", 1)[0])
    assert "_terminate_process_tree" in ki_block
    assert "raise" in ki_block


def test_stage_popen_isolation_kwargs_wired_into_popen():
    """audit S7: 隔离 kwargs 必须真接到 Popen (此前为定义却 0 调用的死函数)。"""
    src = inspect.getsource(stage_mod.run_stage)
    assert "_stage_popen_isolation_kwargs()" in src


# ---------------------------------------------------------------------------
# B/S10: stage 11/12 词典文件入血缘 input_files
# ---------------------------------------------------------------------------
def test_news_bank_includes_bank_lexicons_in_lineage():
    """audit B/S10: stage 11 save 必须把 bank_names / bank_name_exclusions 词典
    纳入 input_files (使其内容进 input_hashes), 否则词典篡改对完整性校验失明。"""
    src = inspect.getsource(news_bank.main)
    assert "input_files" in src
    assert "bank_names_file" in src
    assert "bank_name_exclusions_file" in src


def test_news_fintech_includes_fintech_dict_in_lineage():
    """audit B/S10: stage 12 (两处 save) 必须把 fintech_dict 词典纳入 input_files。"""
    src = inspect.getsource(news_fintech.main)
    assert "fintech_dict_file" in src
    assert "input_files" in src
    # 两处 save 都应接入 (full + filtered) — 计数 fintech_dict_file 至少出现 2 次
    assert src.count("fintech_dict_file") >= 2
