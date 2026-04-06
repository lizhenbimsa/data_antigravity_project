"""
test_39_prompt_sensitivity.py — 阶段39 Prompt 措辞敏感度量化 单元测试
=====================================================================

覆盖维度：
  A. config.yaml ↔ 代码交叉验证
  B. run_pipeline_validation.py 一致性
  C. import 完整性分析
  D. 边界条件压力测试（全一致/随机/单条/完全不一致）
  E. LaTeX 语法正确性
  F. 端到端模拟测试（mock data → 报告生成）
  G. 深层逻辑验证
"""
import os
import json
import tempfile
import shutil

import pytest
import numpy as np
import pandas as pd
import yaml

# ── 导入被测模块 ──
# conftest.py 已确保 news_process 目录在 sys.path 中
_MOD39_PATH = os.path.join(os.path.dirname(__file__), '..', '39_prompt_sensitivity.py')


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope='module')
def mod39():
    """延迟导入 39_prompt_sensitivity 模块，避免模块级副作用。"""
    return __import__('39_prompt_sensitivity')


@pytest.fixture(scope='module')
def source_code():
    """读取 39_prompt_sensitivity.py 源代码文本。"""
    with open(_MOD39_PATH, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture(scope='module')
def config():
    """加载 config.yaml。"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope='module')
def rpv_code():
    """读取 run_pipeline_validation.py 源代码文本。"""
    rpv_path = os.path.join(os.path.dirname(__file__), '..', 'run_pipeline_validation.py')
    with open(rpv_path, 'r', encoding='utf-8') as f:
        return f.read()


# ============================================================================
# 维度 A: config.yaml ↔ 代码交叉验证
# ============================================================================

class TestConfigCodeCrossValidation:
    """维度 A: config.yaml 与代码的交叉验证。"""

    def test_a1_prompt_sensitivity_node_exists(self, config):
        """A1: prompt_sensitivity_test 节点存在"""
        assert 'prompt_sensitivity_test' in config, \
            "config.yaml 中无 prompt_sensitivity_test 节点"

    def test_a2_config_keys_match_code(self, config, source_code):
        """A2: 代码中读取的 key 与 config 中的 key 一致"""
        ps_cfg = config.get('prompt_sensitivity_test', {})
        expected_keys = [
            'enabled', 'sample_size', 'random_seed',
            'pass_threshold_verification', 'pass_threshold_sentiment',
            'pass_threshold_kappa', 'pass_threshold_alpha',
        ]
        for k in expected_keys:
            assert k in ps_cfg, f"config 缺少 key '{k}'"

    def test_a3_validation_switch_exists(self, config):
        """A3: validation 开关包含 prompt_sensitivity"""
        val_cfg = config.get('validation', {})
        assert 'prompt_sensitivity' in val_cfg, \
            "validation 节点缺少 prompt_sensitivity 开关"

    def test_a4_validation_switch_count(self, config):
        """A4: validation 开关总数 == 8"""
        val_cfg = config.get('validation', {})
        n_switches = len(val_cfg)
        # 注: 实际开关数如有新增，应同步更新此处期望值
        assert n_switches >= 8, \
            f"validation 开关数 {n_switches} < 8 (期望 ≥ 8)"


# ============================================================================
# 维度 B: run_pipeline_validation.py 一致性
# ============================================================================

class TestPipelineValidationConsistency:
    """维度 B: run_pipeline_validation.py 一致性。"""

    def test_b1_docstring_includes_stage39(self, rpv_code):
        """B1: docstring 包含阶段39"""
        assert '阶段39' in rpv_code, "docstring 缺少阶段39"

    def test_b2_nine_stages(self, rpv_code):
        """B2: 日志说明 9 个阶段"""
        assert '9 个验证阶段' in rpv_code, "日志说明非 9 个阶段"

    def test_b3_stages_list_includes_39(self, rpv_code):
        """B3: stages 列表包含 39_prompt_sensitivity.py"""
        assert '39_prompt_sensitivity.py' in rpv_code, \
            "stages 列表缺少 39"

    def test_b4_switch_name_consistent(self, rpv_code):
        """B4: 开关名 prompt_sensitivity 与 config.yaml 一致"""
        assert "prompt_sensitivity'" in rpv_code or \
               'prompt_sensitivity"' in rpv_code, \
            "开关名不一致"

    def test_b5_stage39_after_37(self, rpv_code):
        """B5: 阶段39在阶段37之后"""
        pos_37 = rpv_code.find('37_dict_coverage_audit')
        pos_39 = rpv_code.find('39_prompt_sensitivity')
        assert pos_37 < pos_39, "阶段39顺序错误，应在37之后"


# ============================================================================
# 维度 C: import 完整性分析
# ============================================================================

class TestImportCompleteness:
    """维度 C: import 完整性分析。"""

    def test_c_imports_used(self, source_code):
        """C: 所有导入的模块确实在代码主体中被使用"""
        imports_to_check = {
            'os': ('os.path', 'os.makedirs', 'os.path.join'),
            'time': ('time.time',),
            'json': ('json.dump',),
            'asyncio': ('asyncio.Semaphore', 'asyncio.run', 'asyncio.as_completed'),
            'aiohttp': ('aiohttp.ClientSession', 'aiohttp.TCPConnector'),
            'numpy': ('np.',),
            'pandas': ('pd.',),
            'matplotlib': ('matplotlib.use', 'plt.'),
            'font_manager': ('font_manager.',),
            'import_module': ('import_module',),
        }

        body = source_code[source_code.find('CONFIG = load_config()'):]
        for mod_name, usage_patterns in imports_to_check.items():
            found = any(p in body for p in usage_patterns)
            assert found, f"未使用的 import: {mod_name}"

    def test_c_no_redundant_imports(self, source_code):
        """C: 冗余导入已清理"""
        cleaned = [
            'import sys', 'import logging',
            'from collections import Counter',
            'from utils.entity_context import',
        ]
        for ci in cleaned:
            assert ci not in source_code, f"冗余导入未清理: {ci}"


# ============================================================================
# 维度 D: 边界条件压力测试
# ============================================================================

class TestBoundaryConditions:
    """维度 D: 边界条件压力测试。"""

    def test_d0_variant_prompts_format_safe(self, mod39):
        """D0: 所有 VARIANT_PROMPTS 的 format() 调用安全"""
        test_kwargs = {
            'target_bank': '工商银行',
            'co_mentioned_banks': '建设银行; 农业银行',
            'title': '测试标题',
            'content': '测试内容',
        }
        for vk, prompt in mod39.VARIANT_PROMPTS.items():
            result = prompt.format(**test_kwargs)
            assert '工商银行' in result, f"{vk}: 占位符替换失败"
            assert '"is_bank_fintech_news"' in result, \
                f"{vk}: JSON schema 缺失"

    def test_d1_variant_labels_coverage(self, mod39):
        """D1: VARIANT_LABELS 覆盖所有 VARIANT_PROMPTS"""
        for vk in mod39.VARIANT_PROMPTS:
            assert vk in mod39.VARIANT_LABELS, \
                f"Missing label for {vk}"

    def test_d2_build_fleiss_matrix(self, mod39):
        """D2: _build_fleiss_matrix 正确性"""
        labels = np.array([[0, 1, 0], [0, 1, 1]])
        count = mod39._build_fleiss_matrix(labels)
        expected = np.array([[2, 0], [0, 2], [1, 1]])
        np.testing.assert_array_equal(count, expected)

    def test_d3_fleiss_standard_validation(self, mod39):
        """D3: Fleiss (1971) Table 3 标准验证"""
        m = np.array([
            [0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6],
            [0, 3, 9, 2, 0], [2, 2, 8, 1, 1], [7, 7, 0, 0, 0],
            [3, 2, 6, 3, 0], [2, 5, 3, 2, 2], [6, 5, 2, 1, 0],
            [0, 2, 2, 3, 7],
        ])
        fk = mod39.compute_fleiss_kappa(m)
        assert abs(fk - 0.2099) < 0.001, \
            f"Fleiss kappa={fk:.4f}, expected ~0.2099"

    def test_d4_full_agreement(self, mod39):
        """D4: 全一致 (N=100, 5 coders all 1) → kappa=1.0"""
        cm = mod39._build_fleiss_matrix(np.ones((5, 100), dtype=int))
        fk = mod39.compute_fleiss_kappa(cm)
        assert abs(fk - 1.0) < 0.001, f"全一致 Fleiss={fk}"

    def test_d5_empty_matrix(self, mod39):
        """D5: 空矩阵 → kappa=0.0"""
        fk = mod39.compute_fleiss_kappa(np.array([]).reshape(0, 2))
        assert fk == 0.0, f"空矩阵 Fleiss={fk}"

    def test_d6_random_labels(self, mod39):
        """D6: 随机标注 (N=50, 5 coders) → kappa 接近 0"""
        np.random.seed(42)
        cm = mod39._build_fleiss_matrix(
            np.random.randint(0, 2, size=(5, 50))
        )
        fk = mod39.compute_fleiss_kappa(cm)
        assert abs(fk) < 0.5, f"随机标注 Fleiss={fk}, 应接近 0"

    def test_d7_pairwise_full_agreement(self, mod39):
        """D7: Pairwise 全一致"""
        df = pd.DataFrame({
            'V0_baseline_verified_full': [True] * 10,
            'V0_baseline_sentiment_full': ['正面'] * 10,
            'test_verified_full': [True] * 10,
            'test_sentiment_full': ['正面'] * 10,
        })
        r = mod39.compute_pairwise_consistency(df, 'test', '_full')
        assert r['verification_agreement'] == 1.0
        assert r['cohens_kappa_verification'] == 1.0

    def test_d8_pairwise_full_disagreement(self, mod39):
        """D8: Pairwise 完全不一致"""
        df = pd.DataFrame({
            'V0_baseline_verified_full': [True] * 5 + [False] * 5,
            'V0_baseline_sentiment_full': ['正面'] * 5 + ['负面'] * 5,
            'test2_verified_full': [False] * 5 + [True] * 5,
            'test2_sentiment_full': ['负面'] * 5 + ['正面'] * 5,
        })
        r = mod39.compute_pairwise_consistency(df, 'test2', '_full')
        assert r['verification_agreement'] == 0.0


# ============================================================================
# 维度 E: LaTeX 语法正确性
# ============================================================================

class TestLatexCorrectness:
    """维度 E: LaTeX 语法正确性。"""

    def test_e_latex_balanced_envs(self, mod39):
        """E: LaTeX 环境 begin/end 配对 + 无占位符残留"""
        mock_pairwise = {
            '_full': {vk: {
                'verification_agreement': 0.92,
                'sentiment_agreement': 0.88,
                'cohens_kappa_verification': 0.84,
            } for vk in mod39.VARIANT_PROMPTS},
            '_ctx': {vk: {
                'verification_agreement': 0.90,
                'sentiment_agreement': 0.85,
                'cohens_kappa_verification': 0.80,
            } for vk in mod39.VARIANT_PROMPTS},
        }
        mock_multi = {
            '_full': {'krippendorffs_alpha': 0.87, 'fleiss_kappa': 0.85},
            '_ctx': {'krippendorffs_alpha': 0.83, 'fleiss_kappa': 0.81},
        }
        mock_variance = {
            '_full': {'true_rate_std': 0.012},
            '_ctx': {'true_rate_std': 0.018},
        }

        tmp_dir = tempfile.mkdtemp()
        try:
            mod39._generate_latex_table(
                mock_pairwise, mock_multi, mock_variance,
                list(mod39.VARIANT_PROMPTS.keys()), 1000, tmp_dir,
            )
            tex_path = os.path.join(tmp_dir, 'prompt_sensitivity_table.tex')
            with open(tex_path, 'r', encoding='utf-8') as f:
                tex = f.read()

            for env in ['table', 'tabular']:
                opens = tex.count(f'\\begin{{{env}}}')
                closes = tex.count(f'\\end{{{env}}}')
                assert opens == closes, \
                    f"LaTeX {env} 不配对: {opens} opens vs {closes} closes"

            assert 'tablenotes' not in tex, "tablenotes 依赖应已移除"
            assert 'x.xxxx' not in tex, "LaTeX 中残留占位符"
        finally:
            shutil.rmtree(tmp_dir)


# ============================================================================
# 维度 F: 端到端模拟测试
# ============================================================================

class TestEndToEndSimulation:
    """维度 F: 端到端模拟测试（mock data → 报告生成）。"""

    @pytest.fixture
    def mock_data(self, mod39):
        """生成 mock DataFrame 并填充变体列。"""
        n_mock = 20
        np.random.seed(42)
        df = pd.DataFrame({
            '内容': [f'测试内容{i}' for i in range(n_mock)],
            'content_ctx': [f'上下文{i}' for i in range(n_mock)],
            'target_bank': ['工商银行'] * n_mock,
            'co_mentioned_banks': ['建设银行'] * n_mock,
            '标题': [f'标题{i}' for i in range(n_mock)],
            'llm_verified_full': np.random.choice(
                [True, False], n_mock, p=[0.7, 0.3]),
            'llm_verified_ctx': np.random.choice(
                [True, False], n_mock, p=[0.6, 0.4]),
            'llm_sentiment_full': np.random.choice(
                ['正面', '中性', '负面'], n_mock),
            'llm_sentiment_ctx': np.random.choice(
                ['正面', '中性', '负面'], n_mock),
        })

        # 提取基线
        df = mod39.extract_baseline(df)

        # 填充变体列
        for vk in mod39.VARIANT_PROMPTS:
            for track in ['_full', '_ctx']:
                df[f'{vk}_verified{track}'] = np.random.choice(
                    [True, False], n_mock, p=[0.65, 0.35])
                df[f'{vk}_sentiment{track}'] = np.random.choice(
                    ['正面', '中性', '负面'], n_mock)

        return df

    def test_f1_extract_baseline(self, mock_data):
        """F1: extract_baseline 列生成"""
        assert 'V0_baseline_verified_full' in mock_data.columns
        assert 'V0_baseline_sentiment_ctx' in mock_data.columns

    def test_f3_metric_computation(self, mod39, mock_data):
        """F3: 全套指标计算无异常"""
        variant_keys = list(mod39.VARIANT_PROMPTS.keys())
        for track in ['_full', '_ctx']:
            for vk in variant_keys:
                r = mod39.compute_pairwise_consistency(mock_data, vk, track)
                assert 'verification_agreement' in r
            multi = mod39.compute_multivariant_consistency(
                mock_data, variant_keys, track)
            assert 'krippendorffs_alpha' in multi
            var = mod39.compute_cross_variant_variance(
                mock_data, variant_keys, track)
            assert 'true_rate_std' in var

    def test_f4_report_generation(self, mod39, mock_data):
        """F4: 报告文件生成 + 最小尺寸验证"""
        variant_keys = list(mod39.VARIANT_PROMPTS.keys())
        pairwise_results = {}
        multi_results = {}
        variance_results = {}
        for track in ['_full', '_ctx']:
            pw = {}
            for vk in variant_keys:
                pw[vk] = mod39.compute_pairwise_consistency(
                    mock_data, vk, track)
            pairwise_results[track] = pw
            multi_results[track] = mod39.compute_multivariant_consistency(
                mock_data, variant_keys, track)
            variance_results[track] = mod39.compute_cross_variant_variance(
                mock_data, variant_keys, track)

        tmp_report = tempfile.mkdtemp()
        try:
            mod39.generate_reports(
                mock_data, variant_keys, pairwise_results,
                multi_results, variance_results, True, tmp_report,
            )
            expected_files = {
                'prompt_sensitivity_results.json': 1000,
                'prompt_sensitivity_detail.csv': 1000,
                'prompt_sensitivity_table.tex': 500,
                'prompt_sensitivity_heatmap.png': 10000,
            }
            for fname, min_size in expected_files.items():
                fpath = os.path.join(tmp_report, fname)
                assert os.path.exists(fpath), f"{fname} 不存在"
                size = os.path.getsize(fpath)
                assert size >= min_size, \
                    f"{fname} 过小: {size} < {min_size}"
        finally:
            shutil.rmtree(tmp_report)

    def test_f5_json_structure(self, mod39, mock_data):
        """F5: JSON 报告结构完整性"""
        variant_keys = list(mod39.VARIANT_PROMPTS.keys())
        pairwise_results = {}
        multi_results = {}
        variance_results = {}
        for track in ['_full', '_ctx']:
            pw = {}
            for vk in variant_keys:
                pw[vk] = mod39.compute_pairwise_consistency(
                    mock_data, vk, track)
            pairwise_results[track] = pw
            multi_results[track] = mod39.compute_multivariant_consistency(
                mock_data, variant_keys, track)
            variance_results[track] = mod39.compute_cross_variant_variance(
                mock_data, variant_keys, track)

        tmp_report = tempfile.mkdtemp()
        try:
            mod39.generate_reports(
                mock_data, variant_keys, pairwise_results,
                multi_results, variance_results, True, tmp_report,
            )
            json_path = os.path.join(
                tmp_report, 'prompt_sensitivity_results.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                rpt = json.load(f)
            required = [
                'stage', 'methodology', 'sample_size', 'passed',
                'full_track', 'ctx_track', 'thresholds',
            ]
            missing = [k for k in required if k not in rpt]
            assert not missing, f"JSON 缺少 keys: {missing}"
        finally:
            shutil.rmtree(tmp_report)


# ============================================================================
# 维度 G: 深层逻辑验证
# ============================================================================

class TestDeepLogic:
    """维度 G: 深层逻辑验证。"""

    def test_g1_numpy_json_serialization(self, source_code):
        """G1: numpy → JSON 序列化保护 (round(float(...)) 调用)"""
        float_casts = source_code.count('round(float(')
        assert float_casts >= 10, \
            f"numpy → JSON 保护不足 ({float_casts} 处, 期望 ≥ 10)"

    def test_g2_prompt_variant_semantic_diff(self, mod39):
        """G2: 各 Prompt 变体与 V0 语义差异验证"""
        v0 = mod39.PROMPT_TEMPLATE
        for vk, prompt in mod39.VARIANT_PROMPTS.items():
            assert prompt != v0, f"{vk} 与 V0 完全相同!"
            placeholders = [
                '{target_bank}', '{co_mentioned_banks}',
                '{title}', '{content}',
            ]
            missing_ph = [p for p in placeholders if p not in prompt]
            assert not missing_ph, f"{vk} 缺少占位符 {missing_ph}"
            schema_keys = [
                '"is_bank_fintech_news"', '"sentiment"',
                '"sentiment_confidence"',
            ]
            missing_sk = [k for k in schema_keys if k not in prompt]
            assert not missing_sk, f"{vk} JSON schema 缺少 {missing_sk}"

    def test_g3_heatmap_diagonal_symmetry(self, mod39):
        """G3: heatmap Kappa 矩阵: 对角线 == 1.0 且矩阵对称"""
        n_hm = 30
        np.random.seed(42)
        hm_df = pd.DataFrame()
        all_hm_keys = ['V0_baseline'] + list(mod39.VARIANT_PROMPTS.keys())
        for key in all_hm_keys:
            for trk in ['_full', '_ctx']:
                hm_df[f'{key}_verified{trk}'] = np.random.choice(
                    [True, False], n_hm)

        for trk in ['_full', '_ctx']:
            km = np.ones((len(all_hm_keys), len(all_hm_keys)))
            for i in range(len(all_hm_keys)):
                for j in range(len(all_hm_keys)):
                    if i == j:
                        continue
                    a_i = hm_df[
                        f'{all_hm_keys[i]}_verified{trk}'
                    ].astype(int).values
                    a_j = hm_df[
                        f'{all_hm_keys[j]}_verified{trk}'
                    ].astype(int).values
                    km[i, j] = mod39.compute_cohens_kappa(a_i, a_j)['kappa']

            # 对角线全为 1.0
            for idx in range(len(all_hm_keys)):
                assert km[idx, idx] == 1.0, \
                    f"{trk} 对角线 [{idx}] 非 1.0"
            # 矩阵对称
            assert np.allclose(km, km.T, atol=1e-10), \
                f"{trk} 矩阵不对称"

    def test_g4_run_validation_docstring(self, rpv_code):
        """G4: run_validation() docstring 包含阶段39"""
        func_doc_start = rpv_code.find('def run_validation')
        func_doc = rpv_code[func_doc_start:func_doc_start + 800]
        assert '阶段39' in func_doc, \
            "run_validation() docstring 缺少阶段39"
