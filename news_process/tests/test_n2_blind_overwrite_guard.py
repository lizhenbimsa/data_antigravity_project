"""tests/test_n2_blind_overwrite_guard.py — N2 盲表防覆写机制回归锁。

对应计划: scripts/audit/PROMPT_ASSETS_AUDIT_EXECUTION_PLAN_2026-07-12.md
§10 新挂账 N2（盲表防覆写机制，人工窗口硬前置）。

覆盖两个写出口（各 ≥2 条用例：已填盲表被拒绝覆写 / 空盲表正常重生）：
  1. ``news_process/validation/llms_human.py::_write_blind_workbook``
     （61 工作台 blind_A/B 写出口, :183-196 附近）。
  2. ``news_process/scripts/migrate/manual_validation_sampling.py::
     _guard_blind_overwrite``（工作台 + 对账表两处 to_excel 写出口, :228,230）。

全程只用 tmp_path 隔离产物，绝不触碰真实 data/processed/ 或 eval_reports/。
"""
import os
import sys

import pandas as pd
import pytest

_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.scripts.migrate import manual_validation_sampling as mvs
from news_process.validation import llms_human

# ============================================================================
# 1. llms_human.py — _write_blind_workbook 写出口
# ============================================================================

def _sample_df_61(n=6):
    return pd.DataFrame({
        '_row_uid': range(n),
        'docid': range(n),
        '日期': ['2017-01-01'] * n,
        '媒体类型(中文)': ['报纸'] * n,
        '标题': [f't{i}' for i in range(n)],
        '内容': ['c'] * n,
        'target_bank': ['工商银行'] * n,
        '编码者A_验证': [''] * n,
        '编码者B_验证': [''] * n,
        '编码者A_情感': [''] * n,
        '编码者B_情感': [''] * n,
    })


class TestLlmsHumanN2Guard:
    def test_empty_blind_table_regenerates_normally(self, tmp_path):
        """空盲表 (从未存在) 正常写出, 且写出后落"标注进行中"旗标。"""
        sdf = _sample_df_61()
        p = str(tmp_path / 'blind_A.xlsx')
        llms_human._write_blind_workbook(sdf, 'A', p)
        assert os.path.exists(p)
        flag = llms_human._annotation_flag_path(p)
        assert os.path.exists(flag), 'N2 双保险第二层: 写出后必须落旗标文件'

    def test_filled_blind_table_rejected_without_force(self, tmp_path):
        """已填盲表 (人工判定_情感/_row_uid 等价列非空) 再次写出必须被拒绝。"""
        sdf = _sample_df_61()
        p = str(tmp_path / 'blind_A.xlsx')
        llms_human._write_blind_workbook(sdf, 'A', p)
        # 模拟人工已填写: 回填第一行的 编码者A_情感
        filled = pd.read_excel(p, sheet_name='验证数据')
        filled['编码者A_情感'] = filled['编码者A_情感'].astype(object)
        filled.loc[0, '编码者A_情感'] = '正面'
        with pd.ExcelWriter(p, engine='xlsxwriter') as w:
            filled.to_excel(w, sheet_name='验证数据', index=False)
        # 移除旗标, 单独验证"标注列非空"这一条检测路径本身也能拦截
        flag = llms_human._annotation_flag_path(p)
        if os.path.exists(flag):
            os.remove(flag)
        with pytest.raises(SystemExit):
            llms_human._write_blind_workbook(sdf, 'A', p)

    def test_flag_alone_warns_but_allows_regen(self, tmp_path, caplog):
        """fix(N2-P1, 2026-07-14): 旗标单独在位 (零标注) → 放行 + LOUD 警告。

        原语义"旗标单独硬拦"会死锁编排器 (shim 零参调用无越权通道, 首跑落旗标
        后每次验证管道在 stage 61 硬中止并连坐跳过后续阶段 — R2-A 实跑确证)。
        放行安全: 抽样 seed 恒定 → 重生内容可再现, 空表无人工成果可丢。
        """
        sdf = _sample_df_61()
        p = str(tmp_path / 'blind_A.xlsx')
        llms_human._write_blind_workbook(sdf, 'A', p)  # 首次写出 → 旗标落地
        assert os.path.exists(llms_human._annotation_flag_path(p))
        # 标注列仍全空 + 旗标在位 → 第二次调用放行 (编排器重跑场景), 且带警告。
        # 模块 logger 经 setup_logging propagate=False → caplog 收不到, 须直挂
        # handler (先例: test_v9_pre1_skip_version_guard 同款绕法)。
        llms_human.logger.addHandler(caplog.handler)
        try:
            llms_human._write_blind_workbook(sdf, 'A', p)  # 不得 raise
        finally:
            llms_human.logger.removeHandler(caplog.handler)
        assert any('放行' in m for m in caplog.messages), 'N2-P1: 放行必须带 LOUD 警告'

    def test_flag_plus_filled_annotations_still_blocks(self, tmp_path):
        """旗标 + 非空标注同现 → 主检仍硬拦 (N2-P1 只放行零标注情形)。"""
        sdf = _sample_df_61()
        p = str(tmp_path / 'blind_A.xlsx')
        llms_human._write_blind_workbook(sdf, 'A', p)
        filled = pd.read_excel(p, sheet_name='验证数据')
        filled['编码者A_情感'] = filled['编码者A_情感'].astype(object)
        filled.loc[0, '编码者A_情感'] = '正面'
        filled.to_excel(p, sheet_name='验证数据', index=False)
        assert os.path.exists(llms_human._annotation_flag_path(p))
        with pytest.raises(SystemExit):
            llms_human._write_blind_workbook(sdf, 'A', p)

    def test_force_regenerate_overrides_guard(self, tmp_path):
        """显式 force_regenerate=True 越权覆写, 已填标注/旗标均不再拦截。"""
        sdf = _sample_df_61()
        p = str(tmp_path / 'blind_A.xlsx')
        llms_human._write_blind_workbook(sdf, 'A', p)
        filled = pd.read_excel(p, sheet_name='验证数据')
        filled['编码者A_情感'] = filled['编码者A_情感'].astype(object)
        filled.loc[0, '编码者A_情感'] = '正面'
        with pd.ExcelWriter(p, engine='xlsxwriter') as w:
            filled.to_excel(w, sheet_name='验证数据', index=False)
        # 未越权应拒绝
        with pytest.raises(SystemExit):
            llms_human._write_blind_workbook(sdf, 'A', p)
        # 显式越权应放行
        llms_human._write_blind_workbook(sdf, 'A', p, force_regenerate=True)
        assert os.path.exists(p)


# ============================================================================
# 2. manual_validation_sampling.py — 两处 to_excel 写出口 (共用同一守卫函数)
# ============================================================================

class TestManualValidationSamplingN2Guard:
    def test_no_existing_file_passes(self, tmp_path):
        """目标路径尚不存在 (首次生成) → 守卫放行, 无异常。"""
        p = tmp_path / 'manual_validation_samples.xlsx'
        mvs._guard_blind_overwrite(p, force_regenerate=False)  # 不应抛异常

    def test_filled_rater_annotations_rejected_without_force(self, tmp_path):
        """既有工作台 R1_/R2_/R3_ 列已有非空标注 → 拒绝覆写。"""
        p = tmp_path / 'manual_validation_samples.xlsx'
        df = pd.DataFrame({
            'orig_index': [0, 1],
            'R1_stage1_relevant': ['yes', ''],  # 一个非空标注
            'R2_stage1_relevant': ['', ''],
            'R3_stage1_relevant': ['', ''],
        })
        df.to_excel(p, index=False)
        with pytest.raises(SystemExit):
            mvs._guard_blind_overwrite(p, force_regenerate=False)

    def test_empty_rater_columns_pass(self, tmp_path):
        """既有工作台存在但 R1_/R2_/R3_ 列全空 (且无进行中旗标) → 正常放行重生。"""
        p = tmp_path / 'manual_validation_samples.xlsx'
        df = pd.DataFrame({
            'orig_index': [0, 1],
            'R1_stage1_relevant': ['', ''],
            'R2_stage1_relevant': ['', ''],
            'R3_stage1_relevant': ['', ''],
        })
        df.to_excel(p, index=False)
        mvs._guard_blind_overwrite(p, force_regenerate=False)  # 不应抛异常

    def test_flag_alone_warns_but_allows_regen(self, tmp_path, capsys):
        """fix(N2-P1, 2026-07-14): 旗标单独在位 (R 列全空) → 放行 + 警告
        (与 llms_human 同款语义; 旗标=发放记录非独立硬闸)。"""
        p = tmp_path / 'manual_validation_samples.xlsx'
        df = pd.DataFrame({
            'orig_index': [0, 1],
            'R1_stage1_relevant': ['', ''],
        })
        df.to_excel(p, index=False)
        mvs._touch_annotation_flag(p)
        mvs._guard_blind_overwrite(p, force_regenerate=False)  # 不得 raise
        assert '放行' in capsys.readouterr().out

    def test_flag_plus_filled_still_blocks(self, tmp_path):
        """旗标 + 非空 R 列同现 → 主检仍硬拦。"""
        p = tmp_path / 'manual_validation_samples.xlsx'
        pd.DataFrame({
            'orig_index': [0],
            'R1_stage1_relevant': ['是'],
        }).to_excel(p, index=False)
        mvs._touch_annotation_flag(p)
        with pytest.raises(SystemExit):
            mvs._guard_blind_overwrite(p, force_regenerate=False)

    def test_force_regenerate_overrides_guard(self, tmp_path):
        """显式 force_regenerate=True 时, 已填标注/旗标均不拦截。"""
        p = tmp_path / 'manual_validation_samples.xlsx'
        df = pd.DataFrame({
            'orig_index': [0, 1],
            'R1_stage1_relevant': ['yes', ''],
        })
        df.to_excel(p, index=False)
        mvs._touch_annotation_flag(p)
        mvs._guard_blind_overwrite(p, force_regenerate=True)  # 不应抛异常

    def test_reconciliation_path_also_guarded(self, tmp_path, capsys):
        """对账表写出口 (无 R1_/R2_/R3_ 列本身) 仍走同一守卫。

        fix(N2-P1, 2026-07-14): 旗标单独在位 → 放行 + 警告 (非硬拦);
        对账表无标注列 → 主检恒零标注 → 重生恒放行 (其内容为机器产物,
        确定性可再现, 拦它只会死锁重跑)。守卫接线本身由警告输出证明。"""
        p = tmp_path / 'manual_validation_reconciliation.xlsx'
        df = pd.DataFrame({'orig_index': [0, 1], 'v7ref_llm_verified_full': [True, False]})
        df.to_excel(p, index=False)
        mvs._touch_annotation_flag(p)
        mvs._guard_blind_overwrite(p, force_regenerate=False)  # 不得 raise
        assert '放行' in capsys.readouterr().out  # 守卫确实在该出口生效


# ============================================================================
# 3. main() 端到端 force_regenerate 透传 (llms_human 侧; $0, tmp_path 隔离)
# ============================================================================

class TestLlmsHumanMainForceRegenerateWiring:
    def test_main_signature_accepts_force_regenerate(self):
        """main() 必须接受 force_regenerate 关键字参数 (CLI --force-regenerate
        透传口), 防止未来重构漏接线。"""
        import inspect
        sig = inspect.signature(llms_human.main)
        assert 'force_regenerate' in sig.parameters
        assert sig.parameters['force_regenerate'].default is False
