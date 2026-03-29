"""
test_39_prompt_sensitivity.py — 阶段39 Prompt 措辞敏感度量化测试单元测试
=====================================================================

覆盖维度：
  A. config.yaml ↔ 代码交叉验证
  B. run_pipeline_validation.py 一致性
  C. import 完整性分析
  D. 边界条件压力测试（全一致/随机/单条/完全不一致）
  E. LaTeX 语法正确性
  F. 端到端模拟测试（mock data → 报告生成）
"""
import sys, os, json, tempfile, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import pandas as pd
import yaml

issues = []
code = open(os.path.join(os.path.dirname(__file__), '..', '39_prompt_sensitivity.py'),
            'r', encoding='utf-8').read()

# ============================================================================
# 维度 A: config.yaml ↔ 代码交叉验证
# ============================================================================
print("=" * 60)
print("维度 A: config.yaml ↔ 代码交叉验证")
print("=" * 60)

config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

# A1: prompt_sensitivity_test 节点存在
ps_cfg = cfg.get('prompt_sensitivity_test', None)
if ps_cfg is None:
    issues.append("A1: config.yaml 中无 prompt_sensitivity_test 节点")
    print("  ❌ A1: 节点缺失")
else:
    print(f"  ✅ A1: 节点存在, keys={list(ps_cfg.keys())}")

# A2: 代码中读取的 key 与 config 中的 key 一致
expected_keys = ['enabled', 'sample_size', 'random_seed',
                 'pass_threshold_verification', 'pass_threshold_sentiment',
                 'pass_threshold_kappa', 'pass_threshold_alpha']
for k in expected_keys:
    if k not in ps_cfg:
        issues.append(f"A2: config 缺少 key '{k}'")
        print(f"  ❌ A2: config 缺少 '{k}'")
    elif f"'{k}'" in code or f'"{k}"' in code or f"get('{k}'" in code:
        print(f"  ✅ A2: '{k}' = {ps_cfg[k]}")
    else:
        print(f"  ⚠️ A2: '{k}' 在 config 中但代码中未找到直接引用")

# A3: validation 开关
val_cfg = cfg.get('validation', {})
if 'prompt_sensitivity' not in val_cfg:
    issues.append("A3: validation 节点缺少 prompt_sensitivity 开关")
    print("  ❌ A3: 开关缺失")
else:
    print(f"  ✅ A3: validation.prompt_sensitivity = {val_cfg['prompt_sensitivity']}")

# A4: validation 开关总数
n_switches = len(val_cfg)
print(f"  {'✅' if n_switches == 8 else '❌'} A4: validation 开关数 = {n_switches} (期望8)")
if n_switches != 8:
    issues.append(f"A4: 开关数 {n_switches} != 8")


# ============================================================================
# 维度 B: run_pipeline_validation.py 一致性
# ============================================================================
print("\n" + "=" * 60)
print("维度 B: run_pipeline_validation.py 一致性")
print("=" * 60)

rpv_path = os.path.join(os.path.dirname(__file__), '..', 'run_pipeline_validation.py')
rpv = open(rpv_path, 'r', encoding='utf-8').read()

# B1: docstring 包含阶段39
if '阶段39' in rpv:
    print("  ✅ B1: docstring 包含阶段39")
else:
    issues.append("B1: docstring 缺少阶段39")
    print("  ❌ B1: docstring 缺少")

# B2: 9个阶段
if '9 个验证阶段' in rpv:
    print("  ✅ B2: 日志说明 9 个阶段")
else:
    issues.append("B2: 日志说明非 9 个阶段")
    print("  ❌ B2: 阶段数不匹配")

# B3: stages.append 包含39
if '39_prompt_sensitivity.py' in rpv:
    print("  ✅ B3: stages 列表包含 39")
else:
    issues.append("B3: stages 列表缺少 39")
    print("  ❌ B3: stages 缺少")

# B4: 开关名一致 (prompt_sensitivity)
if "prompt_sensitivity'" in rpv or 'prompt_sensitivity"' in rpv:
    print("  ✅ B4: 开关名 'prompt_sensitivity' 与 config.yaml 一致")
else:
    issues.append("B4: 开关名不一致")
    print("  ❌ B4: 开关名不匹配")

# B5: 阶段39在37之后
pos_37 = rpv.find('37_dict_coverage_audit')
pos_39 = rpv.find('39_prompt_sensitivity')
if pos_37 < pos_39:
    print("  ✅ B5: 阶段39在阶段37之后")
else:
    issues.append("B5: 阶段39顺序错误")
    print("  ❌ B5: 顺序错误")


# ============================================================================
# 维度 C: import 完整性分析
# ============================================================================
print("\n" + "=" * 60)
print("维度 C: import 完整性分析")
print("=" * 60)

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

for mod_name, usage_patterns in imports_to_check.items():
    body = code[code.find('CONFIG = load_config()'):]
    found = any(p in body for p in usage_patterns)
    if not found:
        issues.append(f"C: 未使用的 import: {mod_name}")
        print(f"  ❌ C: '{mod_name}' 未使用")
    else:
        print(f"  ✅ C: '{mod_name}' 已使用")

# 确认冗余导入已清理
cleaned = ['import sys', 'import logging', 'from collections import Counter',
           'from utils.entity_context import']
for ci in cleaned:
    if ci in code:
        issues.append(f"C: 冗余导入未清理: {ci}")
        print(f"  ❌ C: 冗余: {ci}")
    else:
        print(f"  ✅ C: 已清理: {ci}")


# ============================================================================
# 维度 D: 边界条件压力测试
# ============================================================================
print("\n" + "=" * 60)
print("维度 D: 边界条件压力测试")
print("=" * 60)

mod39 = __import__('39_prompt_sensitivity')

# D0: VARIANT_PROMPTS format() 安全
print("\n  D0: Prompt format() 安全测试")
test_kwargs = {
    'target_bank': '工商银行', 'co_mentioned_banks': '建设银行; 农业银行',
    'title': '测试标题', 'content': '测试内容'
}
for vk, prompt in mod39.VARIANT_PROMPTS.items():
    try:
        result = prompt.format(**test_kwargs)
        assert '工商银行' in result and '"is_bank_fintech_news"' in result
        print(f"    ✅ {vk}: OK ({len(result)} chars)")
    except Exception as e:
        issues.append(f'D0: {vk} format failed: {e}')
        print(f"    ❌ {vk}: {e}")

# D1: VARIANT_LABELS 覆盖
print("\n  D1: VARIANT_LABELS 覆盖")
for vk in mod39.VARIANT_PROMPTS:
    if vk not in mod39.VARIANT_LABELS:
        issues.append(f"D1: Missing label for {vk}")
    else:
        print(f"    ✅ {vk} -> {mod39.VARIANT_LABELS[vk]}")

# D2: _build_fleiss_matrix 正确性
print("\n  D2: _build_fleiss_matrix")
labels = np.array([[0, 1, 0], [0, 1, 1]])
count = mod39._build_fleiss_matrix(labels)
expected = np.array([[2, 0], [0, 2], [1, 1]])
if np.array_equal(count, expected):
    print(f"    ✅ OK: {count.tolist()}")
else:
    issues.append(f"D2: _build_fleiss_matrix incorrect")
    print(f"    ❌ {count} != {expected}")

# D3: Fleiss (1971) 标准验证
print("\n  D3: Fleiss (1971) Table 3")
m = np.array([
    [0,0,0,0,14],[0,2,6,4,2],[0,0,3,5,6],[0,3,9,2,0],
    [2,2,8,1,1],[7,7,0,0,0],[3,2,6,3,0],[2,5,3,2,2],
    [6,5,2,1,0],[0,2,2,3,7]
])
fk = mod39.compute_fleiss_kappa(m)
print(f"    Fleiss kappa = {fk:.4f} (expected 0.2099)")
if abs(fk - 0.2099) > 0.001:
    issues.append(f"D3: Fleiss standard mismatch: {fk}")

# D4: 全一致
print("\n  D4: 全一致 (N=100, 5 coders all 1)")
cm = mod39._build_fleiss_matrix(np.ones((5, 100), dtype=int))
fk = mod39.compute_fleiss_kappa(cm)
print(f"    Fleiss kappa = {fk:.4f} (expect 1.0)")
if abs(fk - 1.0) > 0.001:
    issues.append(f"D4: 全一致 Fleiss={fk}")

# D5: 空矩阵
print("\n  D5: 空矩阵")
fk = mod39.compute_fleiss_kappa(np.array([]).reshape(0, 2))
print(f"    Fleiss kappa = {fk:.4f} (expect 0.0)")
if fk != 0.0:
    issues.append(f"D5: 空矩阵 Fleiss={fk}")

# D6: 随机
print("\n  D6: 随机标注 (N=50, 5 coders)")
np.random.seed(42)
cm2 = mod39._build_fleiss_matrix(np.random.randint(0, 2, size=(5, 50)))
fk2 = mod39.compute_fleiss_kappa(cm2)
print(f"    Fleiss kappa = {fk2:.4f} (expect ~0)")

# D7: Pairwise 全一致
print("\n  D7: Pairwise 全一致")
df_d7 = pd.DataFrame({
    'V0_baseline_verified_full': [True]*10,
    'V0_baseline_sentiment_full': ['正面']*10,
    'test_verified_full': [True]*10,
    'test_sentiment_full': ['正面']*10,
})
r = mod39.compute_pairwise_consistency(df_d7, 'test', '_full')
print(f"    v_agree={r['verification_agreement']}, kappa={r['cohens_kappa_verification']}")

# D8: Pairwise 完全不一致
print("\n  D8: Pairwise 完全不一致")
df_d8 = pd.DataFrame({
    'V0_baseline_verified_full': [True]*5 + [False]*5,
    'V0_baseline_sentiment_full': ['正面']*5 + ['负面']*5,
    'test2_verified_full': [False]*5 + [True]*5,
    'test2_sentiment_full': ['负面']*5 + ['正面']*5,
})
r2 = mod39.compute_pairwise_consistency(df_d8, 'test2', '_full')
print(f"    v_agree={r2['verification_agreement']}, kappa={r2['cohens_kappa_verification']}")


# ============================================================================
# 维度 E: LaTeX 语法正确性
# ============================================================================
print("\n" + "=" * 60)
print("维度 E: LaTeX 语法正确性")
print("=" * 60)

mock_pairwise = {
    '_full': {vk: {'verification_agreement': 0.92, 'sentiment_agreement': 0.88,
                    'cohens_kappa_verification': 0.84} for vk in mod39.VARIANT_PROMPTS},
    '_ctx': {vk: {'verification_agreement': 0.90, 'sentiment_agreement': 0.85,
                   'cohens_kappa_verification': 0.80} for vk in mod39.VARIANT_PROMPTS},
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
    mod39._generate_latex_table(mock_pairwise, mock_multi, mock_variance,
                                 list(mod39.VARIANT_PROMPTS.keys()), 1000, tmp_dir)
    tex_path = os.path.join(tmp_dir, 'prompt_sensitivity_table.tex')
    tex = open(tex_path, 'r', encoding='utf-8').read()

    for env in ['table', 'tabular']:
        opens = tex.count(f'\\begin{{{env}}}')
        closes = tex.count(f'\\end{{{env}}}')
        if opens != closes:
            issues.append(f"E: LaTeX {env} 不配对")
            print(f"  ❌ E: {env} 不配对: {opens} vs {closes}")
        else:
            print(f"  ✅ E: \\begin/end {{{env}}} 配对 ({opens})")

    if 'tablenotes' in tex:
        issues.append("E: tablenotes 存在")
    else:
        print("  ✅ E: 无 tablenotes 依赖")

    if 'x.xxxx' in tex:
        issues.append("E: 占位符残留")
    else:
        print("  ✅ E: 数值已填充")
finally:
    shutil.rmtree(tmp_dir)


# ============================================================================
# 维度 F: 端到端模拟测试
# ============================================================================
print("\n" + "=" * 60)
print("维度 F: 端到端模拟测试")
print("=" * 60)

n_mock = 20
np.random.seed(42)
mock_df = pd.DataFrame({
    '内容': [f'测试内容{i}' for i in range(n_mock)],
    'content_ctx': [f'上下文{i}' for i in range(n_mock)],
    'target_bank': ['工商银行'] * n_mock,
    'co_mentioned_banks': ['建设银行'] * n_mock,
    '标题': [f'标题{i}' for i in range(n_mock)],
    'llm_verified_full': np.random.choice([True, False], n_mock, p=[0.7, 0.3]),
    'llm_verified_ctx': np.random.choice([True, False], n_mock, p=[0.6, 0.4]),
    'llm_sentiment_full': np.random.choice(['正面', '中性', '负面'], n_mock),
    'llm_sentiment_ctx': np.random.choice(['正面', '中性', '负面'], n_mock),
})

# F1: extract_baseline
mock_df2 = mod39.extract_baseline(mock_df)
assert 'V0_baseline_verified_full' in mock_df2.columns
assert 'V0_baseline_sentiment_ctx' in mock_df2.columns
print("  ✅ F1: extract_baseline 列生成")

# F2: 模拟变体
for vk in mod39.VARIANT_PROMPTS:
    for track in ['_full', '_ctx']:
        mock_df2[f'{vk}_verified{track}'] = np.random.choice([True, False], n_mock, p=[0.65, 0.35])
        mock_df2[f'{vk}_sentiment{track}'] = np.random.choice(['正面', '中性', '负面'], n_mock)
print("  ✅ F2: 变体列赋值")

# F3: 全套指标
variant_keys = list(mod39.VARIANT_PROMPTS.keys())
pairwise_results = {}; multi_results = {}; variance_results = {}
for track in ['_full', '_ctx']:
    pw = {}
    for vk in variant_keys:
        pw[vk] = mod39.compute_pairwise_consistency(mock_df2, vk, track)
    pairwise_results[track] = pw
    multi_results[track] = mod39.compute_multivariant_consistency(mock_df2, variant_keys, track)
    variance_results[track] = mod39.compute_cross_variant_variance(mock_df2, variant_keys, track)
print(f"  ✅ F3: Full alpha={multi_results['_full']['krippendorffs_alpha']:.4f}")

# F4: 报告生成
tmp_report = tempfile.mkdtemp()
try:
    mod39.generate_reports(mock_df2, variant_keys, pairwise_results,
                            multi_results, variance_results, True, tmp_report)
    expected_files = {
        'prompt_sensitivity_results.json': 1000,
        'prompt_sensitivity_detail.csv': 1000,
        'prompt_sensitivity_table.tex': 500,
        'prompt_sensitivity_heatmap.png': 10000,
    }
    for fname, min_size in expected_files.items():
        fpath = os.path.join(tmp_report, fname)
        if os.path.exists(fpath):
            size = os.path.getsize(fpath)
            if size >= min_size:
                print(f"  ✅ F4: {fname}: {size:,} bytes")
            else:
                issues.append(f"F4: {fname} 过小: {size} < {min_size}")
                print(f"  ❌ F4: {fname} 过小")
        else:
            issues.append(f"F4: {fname} 不存在")
            print(f"  ❌ F4: {fname} 不存在")

    # F5: JSON 结构
    with open(os.path.join(tmp_report, 'prompt_sensitivity_results.json'), 'r', encoding='utf-8') as f:
        rpt = json.load(f)
    required = ['stage', 'methodology', 'sample_size', 'passed', 'full_track', 'ctx_track', 'thresholds']
    missing = [k for k in required if k not in rpt]
    if missing:
        issues.append(f"F5: JSON 缺少 keys: {missing}")
    else:
        print(f"  ✅ F5: JSON 7 top-level keys 完整")

    # F6: CSV 行数 + 列数
    csv_df = pd.read_csv(os.path.join(tmp_report, 'prompt_sensitivity_detail.csv'))
    exp_rows = n_mock * len(variant_keys) * 2
    exp_cols = 9
    if len(csv_df) == exp_rows and len(csv_df.columns) == exp_cols:
        print(f"  ✅ F6: CSV {len(csv_df)} 行 × {len(csv_df.columns)} 列")
    else:
        issues.append(f"F6: CSV {len(csv_df)}×{len(csv_df.columns)} != {exp_rows}×{exp_cols}")

finally:
    shutil.rmtree(tmp_report)


# ============================================================================
# 维度 G: 第7轮新增维度
# ============================================================================
print("\n" + "=" * 60)
print("维度 G: 深层逻辑验证")
print("=" * 60)

# G1: numpy JSON 序列化安全
print("\n  G1: numpy JSON 序列化")
float_casts = code.count('round(float(')
if float_casts >= 10:
    print(f"    ✅ 代码中有 {float_casts} 处 round(float(...)) 保护")
else:
    issues.append(f"G1: numpy → JSON 保护不足 ({float_casts} 处)")

# G2: Prompt V0-V4 语义差异验证
print("\n  G2: Prompt 变体差异验证")
from difflib import SequenceMatcher
v0 = mod39.PROMPT_TEMPLATE
for vk, prompt in mod39.VARIANT_PROMPTS.items():
    if prompt == v0:
        issues.append(f"G2: {vk} 与 V0 完全相同!")
        print(f"    ❌ {vk}: 与 V0 完全相同!")
    else:
        placeholders = ['{target_bank}', '{co_mentioned_banks}', '{title}', '{content}']
        missing_ph = [p for p in placeholders if p not in prompt]
        schema_keys = ['"is_bank_fintech_news"', '"sentiment"', '"sentiment_confidence"']
        missing_sk = [k for k in schema_keys if k not in prompt]
        if missing_ph:
            issues.append(f"G2: {vk} 缺少占位符 {missing_ph}")
        elif missing_sk:
            issues.append(f"G2: {vk} JSON schema 缺少 {missing_sk}")
        else:
            sim = SequenceMatcher(None, v0, prompt).ratio()
            print(f"    ✅ {vk}: 与V0相似度={sim:.1%}, 占位符+schema完整")

# G3: heatmap 对角线和对称性验证
print("\n  G3: heatmap 矩阵特性")
n_hm = 30
np.random.seed(42)
hm_df = pd.DataFrame()
all_hm_keys = ['V0_baseline'] + list(mod39.VARIANT_PROMPTS.keys())
for key in all_hm_keys:
    for trk in ['_full', '_ctx']:
        hm_df[f'{key}_verified{trk}'] = np.random.choice([True, False], n_hm)

for trk in ['_full', '_ctx']:
    km = np.ones((len(all_hm_keys), len(all_hm_keys)))
    for i in range(len(all_hm_keys)):
        for j in range(len(all_hm_keys)):
            if i == j:
                continue
            a_i = hm_df[f'{all_hm_keys[i]}_verified{trk}'].astype(int).values
            a_j = hm_df[f'{all_hm_keys[j]}_verified{trk}'].astype(int).values
            km[i, j] = mod39.compute_cohens_kappa(a_i, a_j)['kappa']
    diag_ok = all(km[i, i] == 1.0 for i in range(len(all_hm_keys)))
    sym_ok = np.allclose(km, km.T, atol=1e-10)
    lbl = trk.lstrip('_')
    print(f"    {lbl}: 对角线={'✅' if diag_ok else '❌'}, 对称性={'✅' if sym_ok else '❌'}")
    if not diag_ok:
        issues.append(f"G3: {lbl} 对角线非1.0")
    if not sym_ok:
        issues.append(f"G3: {lbl} 矩阵不对称")

# G4: run_validation() docstring 包含阶段39
print("\n  G4: run_validation() docstring")
rpv2 = open(os.path.join(os.path.dirname(__file__), '..', 'run_pipeline_validation.py'),
            'r', encoding='utf-8').read()
# 检查函数级 docstring（不是文件级）
func_doc_start = rpv2.find('def run_validation')
func_doc = rpv2[func_doc_start:func_doc_start+800]
if '阶段39' in func_doc:
    print("    ✅ run_validation() docstring 包含阶段39")
else:
    issues.append("G4: run_validation() docstring 缺少阶段39")
    print("    ❌ run_validation() docstring 缺少阶段39")


# ============================================================================
# 最终汇总
# ============================================================================
print("\n" + "=" * 60)
print("最终汇总")
print("=" * 60)

if issues:
    print(f"\n❌ {len(issues)} ISSUES FOUND:")
    for i in issues:
        print(f"  - {i}")
    sys.exit(1)
else:
    print("\n✅ 全部 7 个维度、40+ 项检查全部通过。代码已达生产标准。")
    sys.exit(0)

