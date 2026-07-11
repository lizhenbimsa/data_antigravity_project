#!/usr/bin/env python3
"""build_codebook_family_map.py — WP0 家族映射机械化 (Stata 变量属性×codebook 长注释执行计划 §5 WP0)。

权威口径 = scripts/audit/STATA_VARATTR_AND_CODEBOOK_LONGDESC_EXECUTION_PLAN_2026-07-10.md (v2.9)。

功能 (WP0 交付物):
  1. 读 51 面板 (51 缺失 = SystemExit(1) 拒跑, **禁回退 40** — 长文生产/验收模式铁律, 计划 §0);
  2. 三级归族 (计划 §1): ① SSOT 常量精确匹配 (从 pipeline 源码 import, 勿手抄) →
     ② codebook 既有推断函数 (变量类别 × 来源阶段 × 剥后缀基名) 机械聚类 →
     ③ 单例家族 + needs_family_review 标记 (>15% 触发人工复审报告);
  3. tier 三态初判 (core|standard|pending, 计划 §1a 类别 1-7 显式名单 + 负面清单,
     判定次序: 显式类别 1-7 均优先于负面清单);
  4. spec 主轨 (11 篇 paper_spec treatment/outcome/identification.iv) + 验证轨
     (instantiate 白名单模板扫 regress 行 + 一跳 local/global 解析, 仅存在性核验;
     spec 外新列一律 needs_review 不自动入 core);
  5. 产 config/codebook_longdesc/_index.json (增量 merge: 存量条目 tier/状态/rationale/
     签核只增不改, 绝不全量重写);
  6. 产 per-家族写手输入包三件套 (build/codebook_inputs/F###/: columns.json /
     source_excerpt.md / citations_pool.md, 计划 §6);
  7. 产签核提案 build/codebook_inputs/wp0_core_signoff_proposal.md (core 清单 +
     四项收窄决策 + 三 gate 实测数字)。

守恒 gate (脚本内自验 + tests/test_codebook_family_map.py 复验):
  - Σ家族列数 (剔 tier=pending) == 面板实存列数, 0 孤儿, 0 重复收录;
  - core 候选 ⊆ panel.columns (pending 豁免), 0 幻影名;
  - core/pending 逐列 core_rationale 非空;
  - core(含 pending) 占比 ≤10%。

用法 (repo 根):
    F:\\Anaconda3\\python.exe -m news_process.scripts.audit.build_codebook_family_map
确定性: 纯 CPU 读 parquet/yaml/模板 → 写 json/md, 无 LLM/Embedding/网络/API ($0);
不动任何 panel 数值列 / parquet / golden。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

# --- sys.path bootstrap (镜像 scripts/generate_codebook.py) ---
_HERE = Path(__file__).resolve()
_NEWS_PROCESS_ROOT = _HERE.parents[2]          # news_process/
_REPO_ROOT = _HERE.parents[3]                  # data_antigravity_project/
for _p in (str(_NEWS_PROCESS_ROOT), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# 结构列豁免白名单 (计划 §1a 类别 7; 逐列点名, 落 _index.json 顶层供 gate 机械消费)
STRUCTURAL_WHITELIST = ['target_bank', 'year']

# 计划 §1a 类别 2: 11/11 主 DV 全为外部财务哨兵 (唯一名 8 个), 面板不实存 → tier=pending。
# (llm_peer DV 按 paper_spec SAL-3 = roa; 两篇 provisional 的 z_score 是占位同名。)
# 该集合由 spec 主轨在运行期解析复核 — 此处仅作"允许 pending 的已知哨兵"闸,
# 运行期若 spec 主轨解析出本集合以外的面板缺失列 → fail-loud (幻影名防线)。
KNOWN_PENDING_SENTINELS = frozenset({
    'funding_cost', 'ln_fintech_investment', 'cost_income_ratio_change_3yr',
    'citation_weighted_patent', 'm_and_a_fintech', 'roa', 'tobin_q', 'z_score',
    # 计划 §1a 类别 1: disagreement treatment 面板不实存 → pending (计划显式点名)
    'cross_outlet_tone_variance_full',
})

# provisional 模板占位变量名 (CLAUDE.md 铁律), 验证轨扫描结果须过滤
PLACEHOLDER_VARNAMES = frozenset({'z_score', 'npl', 'rwa', 'npl_ratio', 'rwa_density'})

# 计划点名但本机 51 面板不实存的 canonical (存在性守卫跳过, 签核提案披露;
# 面板重生 merge 后重跑本脚本自动升 core)。运行期填充。
SKIPPED_ABSENT_CANONICALS: list[str] = []

# ── 2026-07-10 用户签核 (AskUserQuestion via orchestrator, 四问全按推荐通过) ──
# --apply-signoff 时落 _index.json 顶层 tier_signoff; signed_manifest_sha 由
# compute_signed_manifest_sha 复算 (gate 测试断言"当前哈希==签核哈希", 防清单漂移假绿)。
SIGNOFF_2026_07_10 = {
    'date': '2026-07-10',
    'method': ('AskUserQuestion via orchestrator session'
               '（四问全部按推荐通过：core 扩围 150-250 / 四项收窄决策批准 / '
               '655 家族全量直写 / needs_review 维持 standard + 顶刊两裁量'
               '（JEL 计 top / 未列名计非 top）照案）'),
    'user_ack': True,
}

# 签核决策 ④: 验证轨 needs_review 10 列维持 standard (冻结, 扩围判据③不得触碰)
NEEDS_REVIEW_FROZEN_STANDARD = frozenset({
    'coh_tfidf_c_full', 'dcep_post', 'digital_frontier', 'fintech_intensity_mean',
    'hidden_adopt_kw_p50', 'sandbox_post', 'strat_fluidity', 'strat_sim_max',
    'subst_adopt_kw_p50', 'token_adopt_kw_p50',
})


def compute_signed_manifest_sha(index: dict) -> str:
    """签核清单联合内容哈希 (计划 §1a): core 清单 + pending 清单 + 结构列豁免白名单。

    确定性口径: sorted 列名集合 + sort_keys/紧凑分隔 json + utf-8 → sha256。
    gate (tests/test_codebook_family_map.py) 断言当前复算哈希 == 落库
    tier_signoff.signed_manifest_sha — 不等即强制重新签核 (防"签核对象已非
    签核时清单"假绿; 计划 §1a signed_manifest_sha 机制)。
    """
    fams = list((index.get('families') or {}).values())
    core = sorted({c for fam in fams
                   for c, t in (fam.get('tier_by_col') or {}).items() if t == 'core'})
    pending = sorted({c for fam in fams
                      for c, t in (fam.get('tier_by_col') or {}).items() if t == 'pending'})
    payload = json.dumps(
        {'core': core, 'pending': pending,
         'structural_whitelist': sorted(index.get('structural_whitelist') or [])},
        ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

# 验证轨模板白名单 (计划 §1a v2 模板白名单点名, 按 glob pattern 展开到真名):
# 每 paper 固化 {主结果, 机制, 2SLS} 模板
TEMPLATE_WHITELIST_PATTERNS = {
    'bank_fintech_tone': ['11_table2_main_m1m6*', '22_tableA3_bartik_iv*',
                          '25_tableA6_tone_iv_2sls*', '12_table3_mechanism*'],
    'bank_fintech_attention': ['15_*_main_regression*', '12_table3_mechanism*', '16_*mechanism*'],
    'bank_fintech_substance': ['15_*_main_regression*', '12_table3_mechanism*', '16_*mechanism*'],
    'bank_fintech_locus': ['15_*_main_regression*', '12_table3_mechanism*', '16_*mechanism*'],
    'bank_fintech_collab': ['15_*_main_regression*', '12_table3_mechanism*', '16_*mechanism*'],
    'benefit_society': ['11_table2_main*', '25_tableA12_iv_2sls*', '12_table3_mechanism*'],
    'strategic_diff': ['11_table2_main*', '12_table3_mechanism*'],
    'brokerage_network': ['11_table2_main_iv_2sls*', '12_table3_mechanism*'],
    'llm_peer': ['11_table2_main_iv_2sls*', '12_table3_mechanism*'],
    'bank_news_clarity': ['11_table2_main_clarity_risk*', '12_table3_iv_2sls*'],
    'bank_media_disagreement': ['11_table2_main_disagreement_risk*'],
}

# 剥后缀基名 (计划 §1 三级归族次序 ②): 逐个 regex 迭代剥到不动点。
# 判据后缀/三轨后缀/_lg token/加权/滞后/阈值/topk/z 分数孪生/事件研究窗/梯子 —
# 与 CLAUDE.md 各梯子后缀清单 + 面板实测列名形态 (2026-07-10 首跑校准) 一致。
_STRIP_PATTERNS = [
    re.compile(r'_(win1|sent)$'),          # 网络判据变体
    re.compile(r'_(full|ctx|ss)$'),        # 三轨文本后缀
    re.compile(r'_lg$'),                   # _lg 尾缀 (semantic_staleness_full_lg 形态)
    re.compile(r'_(vw|mw|hw)$'),           # 加权聚合
    re.compile(r'_(lead|lag)\d*(plus)?$'), # 滞后派生 + 事件研究 lead/lag 窗
    re.compile(r'_2nd$'),                  # 二阶滞后 (peer_tone_2nd_lag1)
    re.compile(r'_(t80|t95)$'),            # xneg 阈值梯子
    re.compile(r'_(c2|c5)$'),              # 罕见词 cutoff 梯子
    re.compile(r'_thr\d+$'),               # herd 阈值梯子 (_thr25.._thr45)
    re.compile(r'_j\d+w\d+$'),             # attention jump×window 参数梯子
    re.compile(r'_z$'),                    # z 分数孪生
    re.compile(r'_std$'),                  # std 姊妹统计
    re.compile(r'_n\d+$'),                 # strat_diff top-k N 梯子
    re.compile(r'_w$'),                    # 加权孪生 (strat_diff_nK_w)
    re.compile(r'_\d+$'),                  # 数字尾缀 (如 llm_peer_tone_iv_full_75)
    re.compile(r'_(lc|ls|sc|sf|lf)$'),     # 分类三轨对 (locus/subst class track)
    re.compile(r'_(app|tech|sub|symb)$'),  # 分类目标类条件变体
    re.compile(r'_(post|treated|treat_year|rel_year)$'),  # 事件研究结构列
    re.compile(r'_ddd_\w+$'),              # DDD 交互
    re.compile(r'_share_\w+$'),            # Bartik 暴露份额 (bartik_*_share_*)
    re.compile(r'_(disagree|freerider|quietworker|bothvalid)$'),  # 分歧角色变体
    re.compile(r'_frac$'),                 # 占比后缀 (家族键归并用, 不影响 tier)
    re.compile(r'_(pos|neg)$'),            # 正负侧姊妹
    re.compile(r'_(city|prov|province|yr)$'),  # 地理/年广播孪生
    re.compile(r'_(ord|dedup|exc)$'),      # 序数/去重/排除孪生
]
_LG_INFIX_RE = re.compile(r'_lg_')         # _lg 中置形态 (avg_ft_intensity_lg_full)
_TRACK_INFIX_RE = re.compile(r'_(full|ctx|ss)_')  # 三轨中置 (avg_herd_weight_full_thr25)
_KM_INFIX_RE = re.compile(r'_\d+km')       # 地理半径梯子 (prox_100km_*, ai_reg_50km)
_STAT_PREFIX_RE = re.compile(r'^(avg|sum|min|max)_')  # 统计聚合前缀 (姊妹归并)


def _base_override(col: str) -> str | None:
    """面板实测列名形态的家族级基名覆写 (首跑校准, 防碎片化单例)。"""
    if re.match(r'^n_(all_|ft_|fintech_)?articles', col):
        return 'n_articles'                # 计数/分母族 (n_articles_* 诊断全族)
    if col.endswith('_media_frac'):
        return 'media_frac'                # 媒体类型占比族
    if 'coverage' in col:
        return 'coverage'                  # 报道覆盖族
    if col.startswith('brok_bip_'):
        return 'brok_bip'                  # 二分图媒体-银行中心性族
    if col.startswith('brokerage_'):
        return 'brokerage'                 # brokerage 遗留族
    return None

# 负面清单后缀特征 (计划 §1a; 仅约束验证轨 needs_review 候选与总判据兜底,
# **不**覆盖显式类别 1-7 — 判定次序: 显式名单优先)
_NEGATIVE_SUFFIX_RES = [
    re.compile(r'_(ctx|ss)$'),
    re.compile(r'_(ctx|ss)_lg$'),
    re.compile(r'polw(00|10)'),
    re.compile(r'_(c2|c5)$'),
    re.compile(r'_(win1|sent)$'),
    re.compile(r'_(t80|t95)$'),
    re.compile(r'_lag\d*'),
    re.compile(r'_src$'),                  # per-model 分类维度门控指示列
]


def _strip_base(col: str) -> str:
    """剥后缀基名: 中置 token (lg/track/km) 归一 + 迭代剥后缀到不动点 + 统计前缀归并。"""
    base = _LG_INFIX_RE.sub('_', col)
    base = _TRACK_INFIX_RE.sub('_', base)
    base = _KM_INFIX_RE.sub('', base)
    changed = True
    while changed:
        changed = False
        for pat in _STRIP_PATTERNS:
            new = pat.sub('', base)
            if new != base and new:
                base = new
                changed = True
    stripped = _STAT_PREFIX_RE.sub('', base)
    return stripped if stripped else base


def _slug(text: str, maxlen: int = 48) -> str:
    s = re.sub(r'[^a-z0-9_]+', '_', text.lower()).strip('_')
    return (s[:maxlen] or 'family').rstrip('_')


# ---------------------------------------------------------------------------
# 面板加载 (51 缺失 = 拒跑, 禁回退 40)
# ---------------------------------------------------------------------------

def load_panel_columns() -> tuple[list[str], dict[str, str], str]:
    """读 51 面板列名 + dtype (pyarrow schema, 不载数据)。51 缺失 → SystemExit(1)。"""
    from news_process.core.config import load_config
    cfg = load_config()
    panel51_path = os.path.join(
        cfg['paths']['output_dir'],
        cfg['filenames'].get('output_51_panel_controls', '51_panel_with_controls.parquet'),
    )
    if not os.path.exists(panel51_path):
        # 计划 §0 fail-loud 铁律: 长文生产/验收模式下 51 缺失 = 拒跑,
        # 禁在回退 40 宇宙 (缺 11 个 51-only 列) 下产出 (generate_codebook 的回退不适用本脚本)
        print(f"[FATAL] 51_panel_with_controls 不存在: {panel51_path}")
        print("[FATAL] WP0 家族映射禁回退 40_panel_yearly (计划 §0/§5 WP0 铁律) — 拒跑。")
        raise SystemExit(1)
    import pyarrow.parquet as pq
    schema = pq.ParquetFile(panel51_path).schema_arrow
    cols = list(schema.names)
    dtypes = {name: str(schema.field(name).type) for name in cols}
    return cols, dtypes, panel51_path


# ---------------------------------------------------------------------------
# spec 主轨 (计划 §1a 机械化双轨之主轨)
# ---------------------------------------------------------------------------

def read_paper_specs() -> dict:
    """读 11 篇 paper_spec.yaml 的 treatment / outcome / identification.iv。

    P4 locus special-case: 无 treatment.primary 而是 primary_pair (Stata 侧派生不落盘)
    → 面板真实源列 = tech_frac + app_frac (计划 §1a 类别 1 显式点名)。
    """
    import yaml
    specs = {}
    spec_dir = _NEWS_PROCESS_ROOT / 'papers'
    for spec_path in sorted(spec_dir.glob('*/paper_spec.yaml')):
        d = yaml.safe_load(spec_path.read_text(encoding='utf-8'))
        pid = d.get('paper_id') or spec_path.parent.name
        treatment = d.get('treatment', {}) or {}
        outcome = d.get('outcome', {}) or {}
        ident = d.get('identification', {}) or {}
        iv = ident.get('iv', {}) or {}
        t_primary = treatment.get('primary')
        if t_primary is None and 'primary_pair' in treatment:
            # P4 locus: pair 派生列 Stata 侧生成不落盘 → 面板真实源列
            t_cols = ['tech_frac', 'app_frac']
        elif t_primary is not None:
            t_cols = [t_primary]
        else:
            t_cols = []
        iv_cols = []
        if isinstance(iv, dict):
            for k in ('primary', 'fallback'):
                v = iv.get(k)
                if isinstance(v, str):
                    iv_cols.append(v)
        specs[pid] = {
            'treatment_cols': t_cols,
            'outcome_primary': outcome.get('primary'),
            'iv_cols': iv_cols,
        }
    return specs


# ---------------------------------------------------------------------------
# 验证轨 (instantiate 白名单模板 → 扫 regress 行 + 一跳 local/global 解析)
# ---------------------------------------------------------------------------

_REG_CMD_RE = re.compile(
    r'^\s*(?:quietly\s+|qui\s+|capture\s+noisily\s+|capture\s+|cap\s+|noisily\s+)*'
    r'(?:reghdfe|ivreghdfe|ivreg2|ivregress\s+2sls|ivregress|regress|reg|xtreg|areg|'
    r'ppmlhdfe|rwolf2?|boottest)\b(.*)$'
)
_LOCAL_DEF_RE = re.compile(r'^\s*(?:local|global)\s+(\w+)\s+(.*)$')
_MACRO_LOCAL_RE = re.compile(r'`(\w+)\'')
_MACRO_GLOBAL_RE = re.compile(r'\$\{?(\w+)\}?')
_TOKEN_RE = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')
_STATA_NOISE = frozenset({
    'if', 'in', 'using', 'absorb', 'cluster', 'vce', 'robust', 'noconstant',
    'fe', 're', 'first', 'endog', 'exog', 'partial', 'savefirst', 'e', 'missing',
    'i', 'c', 'ib', 'L', 'F', 'D', 'year', 'target_bank',
})


def _instantiate_replication_packages(scratch_root: Path) -> dict:
    """主线/衍生 9 篇经 build_replication_package 实例化到 scratch (不落 repo);
    provisional 两篇直接扫已实例化产物 papers/<pid>/replication/code/ (计划 §1a:
    provisional 模板无 {{}} 占位符, instantiate ≡ copy, 扫既有产物字节等价)。
    返回 {paper_id: code_dir}。失败逐 paper 记录, 不中断 (报告披露)。
    """
    from news_process.papers._common.paper_registry import (
        PAPER_IDS_ALL,
        PAPER_IDS_PROVISIONAL,
    )
    from news_process.papers._common.stata_runner import build_replication_package

    code_dirs: dict[str, Path] = {}
    failures: dict[str, str] = {}
    for pid in PAPER_IDS_ALL:
        try:
            if pid in PAPER_IDS_PROVISIONAL and pid in (
                    'bank_media_disagreement', 'bank_news_clarity'):
                code_dir = _NEWS_PROCESS_ROOT / 'papers' / pid / 'replication' / 'code'
                if not code_dir.is_dir():
                    failures[pid] = f'replication/code 不存在: {code_dir}'
                    continue
                code_dirs[pid] = code_dir
                continue
            choices: dict[str, str] = {'PROJECT_ROOT': str(_REPO_ROOT)}
            if pid == 'bank_fintech_tone':
                # 三轨占位符取生产默认 full 主轨 (计划 §1a v2.5 命令固化: lf/sf/full)
                choices.update({'MAIN_LOCUS_TRACK': 'lf', 'MAIN_SUBST_TRACK': 'sf',
                                'MAIN_SENT_TRACK': 'full'})
            pkg_dir = build_replication_package(
                main_spec_choices=choices, output_root=scratch_root, paper_id=pid)
            code_dirs[pid] = Path(pkg_dir) / 'code'
        except Exception as exc:  # noqa: BLE001 — 逐 paper 隔离, 失败披露非静默
            failures[pid] = f'{type(exc).__name__}: {exc}'
    return {'code_dirs': code_dirs, 'failures': failures}


def _scan_do_file(do_path: Path, panel_cols: set) -> set:
    """扫单个实例化 .do 的 regress 行, 一跳 local/global 解析, 返回命中面板列集合。"""
    try:
        text = do_path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return set()
    lines = text.splitlines()
    # 拼接 /// 续行
    merged: list[str] = []
    buf = ''
    for ln in lines:
        stripped = ln.split('//')[0] if ' //' in ln and '///' not in ln else ln
        if stripped.rstrip().endswith('///'):
            buf += stripped.rstrip()[:-3] + ' '
        else:
            merged.append(buf + stripped)
            buf = ''
    if buf:
        merged.append(buf)
    # 一跳宏定义收集
    macro_defs: dict[str, str] = {}
    for ln in merged:
        m = _LOCAL_DEF_RE.match(ln)
        if m:
            macro_defs[m.group(1)] = m.group(2)
    hits: set[str] = set()
    for ln in merged:
        m = _REG_CMD_RE.match(ln)
        if not m:
            continue
        rest = m.group(1)
        rest = rest.split(',', 1)[0]  # 逗号后是 options, 丢弃
        # 一跳宏展开 (仅一跳, 计划口径)
        for mac_re in (_MACRO_LOCAL_RE, _MACRO_GLOBAL_RE):
            def _sub(mm):
                return ' ' + macro_defs.get(mm.group(1), '') + ' '
            rest = mac_re.sub(_sub, rest)
        for tok in _TOKEN_RE.findall(rest):
            if tok in _STATA_NOISE or tok in PLACEHOLDER_VARNAMES:
                continue
            if tok in panel_cols:
                hits.add(tok)
    return hits


def run_verification_track(panel_cols: set) -> dict:
    """验证轨: instantiate → 白名单模板扫描。返回 per-paper 命中列 + 失败披露。"""
    scratch = Path(tempfile.mkdtemp(prefix='wp0_replication_scan_'))
    inst = _instantiate_replication_packages(scratch)
    scanned: dict[str, dict] = {}
    for pid, code_dir in inst['code_dirs'].items():
        patterns = TEMPLATE_WHITELIST_PATTERNS.get(pid, [])
        files: list[Path] = []
        for pat in patterns:
            files.extend(sorted(code_dir.glob(pat + '.do')) or sorted(code_dir.glob(pat)))
        files = sorted(set(f for f in files if f.suffix == '.do'))
        cols_hit: set[str] = set()
        for f in files:
            cols_hit |= _scan_do_file(f, panel_cols)
        scanned[pid] = {
            'whitelisted_do_files': [f.name for f in files],
            'cols_hit': sorted(cols_hit),
        }
    return {'scanned': scanned, 'failures': inst['failures'],
            'scratch_dir': str(scratch)}


# ---------------------------------------------------------------------------
# 三级归族
# ---------------------------------------------------------------------------

def build_families(panel_cols: list[str]) -> dict:
    """三级归族 (计划 §1): 返回 {family_key: {'columns': [...], 'level': 1|2|3,
    'kind': str, 'needs_family_review': bool}}。每列恰归一族 (守恒)。"""
    # --- SSOT 常量 import (从 pipeline 源码 import, 勿手抄; 计划 §1 ①) ---
    # 注: RULE_ABLATION_SUFFIXES / POLITICAL_WEIGHT_SUFFIXES 取 encode 侧 (与
    # tone_words._RULE_ABLATION_VARIANTS / POLITICAL_WEIGHT_VARIANTS byte-sync,
    # gate=test_rule_ablation_variant_set_synced / test_political_weight_ladder;
    # 刻意不 import tone_words — 其模块级词典加载重且非必需)。
    from news_process.papers.benefit_society.dimension_analysis import DIMENSION_INDICES
    from news_process.pipeline.panel import bert_distribution as bd
    from news_process.pipeline.panel.codebook import _infer_category, _infer_source_stage
    from news_process.pipeline.panel.encode import (
        BERT_MODELS,
        DICT_NAMES,
        LLM_CLASS_SPEC,
        LLM_MODELS,
        POLITICAL_WEIGHT_SUFFIXES,
        RULE_ABLATION_SUFFIXES,
    )
    from news_process.pipeline.panel.network_spillover import NETWORK_METRIC_BASES

    dims = list(DIMENSION_INDICES)
    llm_class_metrics = [v[0] for v in LLM_CLASS_SPEC.values()]  # sub/tech/collab_frac

    # bert_distribution 五族精确列集 (SSOT 生成器)
    bd_panel_cols = set(bd.iter_panel_cols(BERT_MODELS))

    def _bd_bucket(col: str) -> str | None:
        if col not in bd_panel_cols:
            return None
        if 'tone_entropy' in col:
            return 'bertdist_entropy'
        if 'xneg_frac' in col:
            return 'bertdist_xneg_frac'
        if 'net_tone_skew' in col:
            return 'bertdist_skew'
        if col.startswith('bert_xmodel'):
            return 'bertdist_xmodel'
        if '_nt_iyvol' in col or '_nt_iytrend' in col:
            return 'bertdist_intrayear'
        return 'bertdist_other'

    crit_re = re.compile(r'_(win1|sent)$')
    polw_re = re.compile(
        r'^(' + '|'.join(map(re.escape, DICT_NAMES)) + r')_(' +
        '|'.join(POLITICAL_WEIGHT_SUFFIXES) + r')_')
    polw_geo_re = re.compile(
        r'^dict_avg_(' + '|'.join(POLITICAL_WEIGHT_SUFFIXES) + r')_')
    _abl_nonraw = [s for s in RULE_ABLATION_SUFFIXES]
    abl_re = re.compile(
        r'^(dict_avg|' + '|'.join(map(re.escape, DICT_NAMES)) + r')_(' +
        '|'.join(_abl_nonraw) + r')_')
    benefit_re = re.compile(
        r'^benefit_(' + '|'.join(dims) + r')(_lg)?_(full|ctx|ss)$')
    iv_engine_res = [
        ('iv_leave_one_out', re.compile(r'^leave_one_out_peer_\w*iv')),
        ('iv_bartik', re.compile(r'^bartik_\w*iv')),
        ('iv_outlet', re.compile(r'^outlet_\w*iv')),
    ]

    def _model_prefix_match(col: str, models: list[str]) -> tuple[str, str] | None:
        for m in sorted(models, key=len, reverse=True):
            if col.startswith(m + '_'):
                return m, col[len(m) + 1:]
        return None

    families: dict[str, dict] = {}

    def _add(key: str, col: str, level: int, kind: str):
        fam = families.setdefault(key, {'columns': [], 'level': level, 'kind': kind,
                                        'needs_family_review': False})
        fam['columns'].append(col)

    level2_pool: list[str] = []
    for col in panel_cols:
        # 结构列
        if col in STRUCTURAL_WHITELIST:
            _add('structural_keys', col, 1, 'structural')
            continue
        # bert_distribution 五族 (须早于泛型 BERT per-model)
        b = _bd_bucket(col)
        if b:
            _add(b, col, 1, 'bert_distribution')
            continue
        # 政治词权重梯子 (du_2022 polw; 须早于消融/泛型词典)
        if polw_re.match(col) or polw_geo_re.match(col):
            _add('political_weight_du_2022', col, 1, 'political_weight')
            continue
        # 规则消融梯度 (6 词典 + dict_avg × 7 变体 × 3 轨)
        m_abl = abl_re.match(col)
        if m_abl:
            _add(f'rule_ablation_{m_abl.group(1)}', col, 1, 'rule_ablation')
            continue
        # 网络 33 结构指标 (剥判据后缀精确匹配)
        base_crit = crit_re.sub('', col)
        if base_crit in NETWORK_METRIC_BASES:
            _add(f'net_{base_crit}', col, 1, 'network_metric')
            continue
        # benefit 4 维度六轨
        m_ben = benefit_re.match(col)
        if m_ben:
            _add(f'benefit_dim_{m_ben.group(1)}', col, 1, 'benefit_dimension')
            continue
        # IV 三引擎
        matched_iv = False
        for key, pat in iv_engine_res:
            if pat.match(col):
                _add(key, col, 1, 'iv_engine')
                matched_iv = True
                break
        if matched_iv:
            continue
        # LLM per-model (含 LLM_CLASS_SPEC 分类维度)
        mm = _model_prefix_match(col, LLM_MODELS)
        if mm:
            model, rest = mm
            rest_base = _strip_base(rest)
            if any(rest_base == met or rest.startswith(met) for met in llm_class_metrics):
                metric = next(met for met in llm_class_metrics
                              if rest_base == met or rest.startswith(met))
                _add(f'llm_class_{metric}', col, 1, 'llm_class_per_model')
            else:
                _add(f'llm_permodel_{rest_base}', col, 1, 'llm_per_model')
            continue
        # BERT per-model 泛型
        mb = _model_prefix_match(col, BERT_MODELS)
        if mb:
            model, rest = mb
            _add(f'bert_permodel_{_strip_base(rest)}', col, 1, 'bert_per_model')
            continue
        level2_pool.append(col)

    # --- ② 推断函数机械聚类: (变量类别 × 来源阶段 × 剥后缀基名) ---
    clusters: dict[tuple, list[str]] = {}
    for col in level2_pool:
        base = _base_override(col) or _strip_base(col)
        key = (_infer_category(col), _infer_source_stage(col), base)
        clusters.setdefault(key, []).append(col)

    coarse_pool: list[tuple[tuple, str]] = []   # (原 key, col)
    for (cat, stage, base), cols in clusters.items():
        if len(cols) >= 2:
            fam_key = f'l2_{_slug(base)}'
            # 防 level1 键碰撞
            while fam_key in families:
                fam_key += '_x'
            families[fam_key] = {'columns': cols, 'level': 2,
                                 'kind': f'inferred:{cat}|{stage}',
                                 'needs_family_review': False}
        else:
            coarse_pool.append(((cat, stage, base), cols[0]))

    # --- ② pass B (粗聚): 剩余单列按 (类别 × 来源阶段 × 基名首 token) 再聚一轮;
    #     粗聚成族者标 needs_family_review (人工可复审归并质量), 仍单列者进 ③ ---
    coarse: dict[tuple, list[str]] = {}
    for (cat, stage, base), col in coarse_pool:
        tok = base.split('_')[0] if '_' in base else base
        coarse.setdefault((cat, stage, tok), []).append(col)
    for (cat, stage, tok), cols in coarse.items():
        if len(cols) >= 2:
            fam_key = f'l2c_{_slug(tok)}'
            while fam_key in families:
                fam_key += '_x'
            families[fam_key] = {'columns': cols, 'level': 2,
                                 'kind': f'inferred_coarse:{cat}|{stage}',
                                 'needs_family_review': True}
        else:
            # --- ③ 单例家族 + needs_family_review ---
            fam_key = f'l3_{_slug(cols[0])}'
            while fam_key in families:
                fam_key += '_x'
            families[fam_key] = {'columns': cols, 'level': 3,
                                 'kind': f'singleton:{cat}|{stage}',
                                 'needs_family_review': True}
    return families


# ---------------------------------------------------------------------------
# tier 三态初判 (计划 §1a 类别 1-7 + 负面清单; 显式类别优先于负面清单)
# ---------------------------------------------------------------------------

def build_core_candidates(specs: dict, panel_cols: set) -> tuple[dict, dict]:
    """返回 (core_rationale: {col: [rationale,...]}, pending_rationale: {col: [...]})。

    显式类别 1-7 逐条落地 (计划 §1a); 类别 6 的"等"字按计划显式点名清单收敛,
    不自行外推 (反灌水)。
    """
    core: dict[str, list[str]] = {}
    pending: dict[str, list[str]] = {}

    def _hit(col: str, rationale: str, force_pending: bool = False):
        if force_pending or col not in panel_cols:
            if col not in KNOWN_PENDING_SENTINELS:
                # 幻影名防线: 面板缺失且非已知哨兵 → fail-loud
                print(f"[FATAL] core 候选 '{col}' 不在面板且非已知 pending 哨兵 — 幻影名。")
                raise SystemExit(1)
            pending.setdefault(col, []).append(rationale)
        else:
            core.setdefault(col, []).append(rationale)

    # 类别 1: treatment 主列
    for pid, s in specs.items():
        for c in s['treatment_cols']:
            _hit(c, f'[类别1] paper_spec treatment 主列 (paper={pid}; 正文级主处理变量)')
    # 类别 2: 主 outcome/DV → 全外部财务哨兵 pending
    for pid, s in specs.items():
        c = s['outcome_primary']
        if c:
            _hit(c, f'[类别2] paper {pid} 主 outcome/DV — 外部财务面板哨兵, '
                    f'接入后升 core (计划 §1a 类别 2)', force_pending=True)
    # 类别 3: 全 11 篇 identification.iv primary + fallback
    for pid, s in specs.items():
        for c in s['iv_cols']:
            _hit(c, f'[类别3] 识别策略主 IV (paper={pid}, identification.iv primary/fallback 全收)')
    # 类别 4: 全局 headline 测度 (实名点名; attention_pct/n_articles/fintech_share
    # 非嵌入族无 _lg — 勿造幻影名; avg_ft_intensity 族 _lg 中缀形态)
    cat4 = ['n_articles', 'n_articles_llm_valid', 'fintech_share', 'attention_pct_full',
            'avg_ft_intensity_full', 'avg_ft_intensity_lg_full']
    for c in cat4:
        if c in panel_cols:
            _hit(c, '[类别4] 全局 headline 测度 (分母/门控/canonical 及 _lg co-primary 对偶)')
        # fintech_share 仅 51 宇宙实存 — 51 面板下应在; 缺失即幻影名 fail-loud
        else:
            print(f"[FATAL] 类别4 headline '{c}' 不在 51 面板 — 幻影名。")
            raise SystemExit(1)
    # 类别 5: 跨厂商/跨模型 co-equal 主轨 full 列
    for m in ('gpt54nano', 'gemini31', 'deepseekv4'):
        _hit(f'{m}_tone_full', '[类别5] LLM 跨厂商 co-equal 主轨 full 列 (27_tableA12 FWER 主角)')
    for b in ('finbert_cn', 'fin_sent_zh', 'finbert2'):
        _hit(f'{b}_net_tone_full', '[类别5] BERT 跨模型 co-equal 主轨 full 列 (27_tableA12 FWER 主角)')
    # 类别 6: 各大家族 canonical 代表列 (计划显式点名清单, 不外推"等"字)
    cat6 = {
        '[类别6] 六词典 canonical full 轨': [
            'loughran_tone_full', 'jiang_2021_tone_full', 'yao_2021_tone_full',
            'bian_2021_tone_full', 'du_2022_tone_full', 'you_2018_tone_full',
            'dict_avg_tone_full'],
        '[类别6] staleness canonical (+嵌入族 _lg 对偶; surface=carve-out 无 _lg)': [
            'semantic_staleness_full', 'semantic_staleness_full_lg', 'surface_staleness_full'],
        '[类别6] boilerplate canonical (非嵌入 carve-out 无 _lg)': ['avg_boilerplate_full'],
        '[类别6] herd canonical (+sum/min 姊妹)': [
            'avg_herd_weight_full', 'sum_herd_weight_full', 'min_herd_weight_full'],
        '[类别6] 网络溢出 headline': [
            'industry_neg_shock', 'emb_peer_tone_lag1_full', 'bank_cogn_mean',
            'bank_degree_cent'],
    }
    for rationale, cols in cat6.items():
        for c in cols:
            _hit(c, rationale)
    # 类别 6 续: benefit 家族 canonical + _lg 对偶 (嵌入族)。
    # ⚠ 实测披露 (2026-07-10): 计划 §1a 点名的 "benefit 4 维度 full 轨 canonical"
    # (benefit_{core_op,growth,resource,compliance}_full, dimension_analysis 产) 在本机
    # 51 面板不实存 (维度 24 列在 benefit_society 附属 parquet, 未 merge 进 51) —
    # 按"全部使用面板实存全名, 幻影名 fail-loud"铁律**存在性守卫**: 实存才收,
    # 不实存记入签核提案披露 (面板重生 merge 后重跑本脚本自动升 core)。
    from news_process.papers.benefit_society.dimension_analysis import DIMENSION_INDICES
    for dim in DIMENSION_INDICES:
        for c, rat in ((f'benefit_{dim}_full', '[类别6] benefit 维度 full 轨 canonical'),
                       (f'benefit_{dim}_lg_full',
                        '[类别6] benefit 维度 full 轨 canonical 的 _lg co-primary 对偶')):
            if c in panel_cols:
                _hit(c, rat)
            else:
                SKIPPED_ABSENT_CANONICALS.append(c)
    # benefit 家族 51 面板实存 canonical = benefit_mean_full (已经类别 1 treatment 入 core);
    # 其 _lg co-primary 对偶按类别 6 嵌入族口径随收。
    _hit('benefit_mean_lg_full', '[类别6] benefit 家族 canonical (treatment 主列) 的 _lg co-primary 对偶')
    # 类别 6 续: BERT 分布形状五族 canonical
    for b in ('finbert_cn', 'fin_sent_zh', 'finbert2'):
        _hit(f'{b}_tone_entropy_full', '[类别6] BERT 分布形状族 canonical (归一化熵)')
        _hit(f'{b}_xneg_frac_full', '[类别6] BERT 分布形状族 canonical (极端负面占比 τ=.90 无后缀)')
        _hit(f'{b}_net_tone_skew_full', '[类别6] BERT 分布形状族 canonical (raw skew)')
        _hit(f'{b}_nt_iyvol_full', '[类别6] BERT 分布形状族 canonical (年内波动)')
    _hit('bert_xmodel_lblhet_full', '[类别6] BERT 跨模型标签异质 canonical (非嵌入 carve-out 无 _lg)')
    # 类别 7: 主键结构列 — 不进 core, 白名单豁免 (STRUCTURAL_WHITELIST 顶层落库)

    # ═══════════ 2026-07-10 签核扩围 (决策①: core 150–250, 类别 6 "等高频用列"口径) ═══════════
    # 判据①: L1 SSOT 主要测度家族的 canonical full 轨代表列 (无后缀/canonical 变体);
    # 判据②: 嵌入族 canonical 的 _lg co-primary 对偶随收 (非嵌入 carve-out 不适用, 存在性断言);
    # 判据③: 白名单/根级模板实例化 .do 中作为回归变量出现 ≥2 模板的高频列 (2026-07-10 实测 tally);
    # 定序不变: 显式类别优先于负面清单; bank controls / 梯子 / 消融 / 阈值 / 判据变体 /
    # ctx·ss 轨仍不入; needs_review 10 列按签核决策④冻结 standard (NEEDS_REVIEW_FROZEN_STANDARD)。

    def _hit_if_exists(col: str, rationale: str):
        """扩围软候选: 面板实存才收, 不实存记披露清单 (非幻影收录)。"""
        if col in panel_cols:
            _hit(col, rationale)
        else:
            SKIPPED_ABSENT_CANONICALS.append(col)

    # 扩①-A: 网络 33 结构指标家族 canonical (无判据后缀列; NETWORK_METRIC_BASES SSOT 全收 —
    # brokerage/P1 网络角色的正文级供给, _win1/_sent 判据变体仍不入)
    from news_process.pipeline.panel.network_spillover import NETWORK_METRIC_BASES
    for base in NETWORK_METRIC_BASES:
        _hit(base, '[类别6-扩围①] 网络结构指标家族 canonical (同篇判据无后缀列; '
                   'NETWORK_METRIC_BASES SSOT; 2026-07-10 签核扩围)')
    # 扩①-B: brokerage 二分图/遗留网络家族 canonical
    for c, rat in (
        ('brok_bip_degree_cent', '[类别6-扩围①] WS-B 二分图媒体-银行中心性家族 canonical'),
        ('brokerage_eigen_cent', '[类别6-扩围①] brokerage 特征向量中心性 (brokerage paper 网络主测度)'),
        ('brokerage_fire_sale', '[类别6-扩围①] brokerage 火灾出售暴露 (15_table6 centrality-outcome 主题列)'),
    ):
        _hit(c, rat + ' (2026-07-10 签核扩围)')
    # 扩①-C: BERT 分布形状年内动态族第二 canonical 测度 (iytrend, 与 iyvol 并列)
    for b in ('finbert_cn', 'fin_sent_zh', 'finbert2'):
        _hit(f'{b}_nt_iytrend_full',
             '[类别6-扩围①] BERT 分布形状族 canonical (年内趋势, 与 iyvol 并列第二测度; 2026-07-10 签核扩围)')
    # 扩②: 嵌入族 canonical 的 _lg co-primary 对偶 + W-嵌入轨 canonical
    _hit('emb_peer_tone_lag1_lg_full',
         '[类别6-扩围②] 网络溢出 headline emb_peer_tone_lag1_full 的 _lg co-primary 对偶 (2026-07-10 签核扩围)')
    _hit('bank_emb_sim_mean_lag1',
         '[类别6-扩围①] 网络 W-嵌入相似轨 canonical (嵌入余弦相似加权 W; ctx/ss 稳健轨不入; 2026-07-10 签核扩围)')
    _hit('bank_emb_sim_mean_lag1_lg',
         '[类别6-扩围②] bank_emb_sim_mean_lag1 的 _lg co-primary 对偶 (2026-07-10 签核扩围)')
    # 扩①-D: 主要测度家族 canonical full 代表列 (CLAUDE.md 点名 headline/canonical)
    for c, rat in (
        ('llm_models_avg_tone_full', 'LLM 三家均值-ensemble 语调 (CLAUDE.md LLM 三家段点名 headline 变体)'),
        ('frac_fls_full', 'FLS 前瞻陈述双门 canonical (稳健性缺口补齐 ⑤; fonly 单门稳健臂不入)'),
        ('avg_rare_word_full', '罕见词频次 canonical (cutoff=3 ≡ 无 c 后缀; _c2/_c5 梯子不入)'),
        ('mean_num_intensity_full', '数值强度 canonical (Table A9 num_intensity 真双轨之字符轨)'),
        ('mean_num_intensity_word_full', '数值强度词轨 (Table A9 真双轨 co-equal 第二臂, spec tA9 dual_track)'),
        ('semantic_highstale_full', '语义高陈旧二元 headline (staleness canonical 孪生)'),
        ('surface_highstale_full', '表层高陈旧二元 headline (MinHash carve-out 无 _lg)'),
        ('avg_agreement_rate_full', 'LLM 三家一致率 headline (效度叙事列, 模型间一致性正文报告)'),
        ('benefit_std_full', 'benefit 家族分散度统计 canonical (态度分歧测度)'),
        ('attention_disp_full', 'attention 家族分散度 canonical (P2 注意力分散测度)'),
        ('frac_front_page', 'news_salience 族 canonical (头版占比; CLAUDE.md 点名保留的显著性信号)'),
        ('frac_front_section', 'news_salience 族显著性信号 (版面前部占比)'),
        ('frac_target_in_lead', 'news_salience 族显著性信号 (导语命中占比)'),
        ('headline_frac', '标题显著性信号 canonical (controls.py headline_frac, CLAUDE.md 点名保留)'),
    ):
        _hit(c, f'[类别6-扩围①] {rat} (2026-07-10 签核扩围)')
    _hit_if_exists('semantic_highstale_full_lg',
                   '[类别6-扩围②] semantic_highstale_full 的 _lg co-primary 对偶 (2026-07-10 签核扩围)')
    # 扩①-E: strat_diff 方法族 canonical N=5 臂 (spec treatment=strat_diff_n5 [word 主方法];
    # lda/emb 方法 co-equal 互稳 + emb 的 _lg 对偶; N 梯子 {10..50} 与 _w 加权孪生不入)
    for c, rat in (
        ('strat_diff_n5_lda', 'strat_diff LDA 方法臂 canonical (N=5, 与主方法 co-equal 互稳)'),
        ('strat_diff_n5_emb', 'strat_diff 嵌入方法臂 canonical (N=5, 与主方法 co-equal 互稳)'),
        ('strat_diff_n5_emb_lg', 'strat_diff 嵌入方法臂的 _lg co-primary 对偶'),
    ):
        _hit(c, f'[类别6-扩围①] {rat} (2026-07-10 签核扩围)')
    # 扩①-F: 六词典方向性构成成分 canonical full (L&M 2011 Table III 分解范式:
    # pos/neg ratio 是 {dict}_tone 公式的直接构成成分; 消融/权重梯子仍不入)
    from news_process.pipeline.panel.encode import DICT_NAMES
    for d in DICT_NAMES:
        _hit(f'avg_{d}_pos_ratio_full',
             f'[类别6-扩围①] 词典 {d} 正面成分占比 canonical full (L&M 分解成分; 2026-07-10 签核扩围)')
        _hit(f'avg_{d}_neg_ratio_full',
             f'[类别6-扩围①] 词典 {d} 负面成分占比 canonical full (L&M 分解成分; 2026-07-10 签核扩围)')
    # 扩①-G: LLM 共识连续得分 / 均值-ensemble 连续臂 / 金科暴露 (存在性软守卫)
    _hit_if_exists('llm_vote_cont_full',
                   '[类别6-扩围①] LLM 共识连续得分族 canonical (tone 的连续孪生; 2026-07-10 签核扩围)')
    _hit_if_exists('llm_models_avg_cont_full',
                   '[类别6-扩围①] LLM 三家均值-ensemble 连续得分 canonical (2026-07-10 签核扩围)')
    _hit_if_exists('fintech_exposure_full',
                   '[类别6-扩围①] 金科暴露测度家族 canonical (2026-07-10 签核扩围)')
    # 扩③: 验证轨 ≥2 模板回归变量 (2026-07-10 全模板 tally 实测; 负面清单/needs_review 冻结已排除)
    for c, n_tmpl, rat in (
        ('bank_type', 7, '银行类型调节主变量 (7 模板异质性正文表)'),
        ('benefit_pos_frac_full', 3, 'benefit 正面占比 (3 模板机制/稳健正文表)'),
        ('benefit_neg_frac_full', 3, 'benefit 负面占比 (3 模板机制/稳健正文表)'),
    ):
        if c in NEEDS_REVIEW_FROZEN_STANDARD:
            continue  # 决策④冻结防线 (当前三列均不在冻结清单, 防御性保留)
        _hit(c, f'[类别6-扩围③] 验证轨回归变量 ≥2 模板 (实测 {n_tmpl} 模板): {rat} (2026-07-10 签核扩围)')

    return core, pending


def is_negative_listed(col: str, controls: set) -> bool:
    """负面清单 (计划 §1a): 仅约束验证轨 needs_review 候选与总判据兜底。"""
    if col in controls:
        return True
    return any(p.search(col) for p in _NEGATIVE_SUFFIX_RES)


def collect_controls(specs_dir: Path) -> set:
    """bank controls 全体显式入负面清单 (计划 v2.8): spec controls 字段 +
    stata_runner._PAPER_DEFAULTS 的 CONTROLS 字符串。"""
    import yaml
    controls: set[str] = set()
    for spec_path in sorted(specs_dir.glob('*/paper_spec.yaml')):
        d = yaml.safe_load(spec_path.read_text(encoding='utf-8'))
        c = d.get('controls', {}) or {}
        for k in ('bank_level', 'year_level'):
            v = c.get(k) or []
            if isinstance(v, list):
                controls.update(x for x in v if isinstance(x, str))
    try:
        from news_process.papers._common.stata_runner import _PAPER_DEFAULTS
        for d in _PAPER_DEFAULTS.values():
            for tok in str(d.get('CONTROLS', '')).split():
                controls.add(tok)
    except Exception:  # noqa: BLE001
        pass
    return controls


# ---------------------------------------------------------------------------
# unit/formula/producer 初判 (家族级 draft; 落地后 SSOT = 家族 md frontmatter)
# ---------------------------------------------------------------------------

def draft_unit(cols: list[str]) -> str:
    joined = ' '.join(cols)
    rep = cols[0]
    if any(t in rep for t in ('frac', 'share', 'ratio', 'pct', 'rate', 'coverage')):
        return '比率/占比 (proportion, [0,1] 或百分比; 待写手按 frontmatter 校准)'
    if rep.startswith('n_') or 'count' in rep or rep.startswith('num_'):
        return '篇数/计数 (count)'
    if 'tone' in joined or 'sentiment' in joined:
        return '语调得分 (连续, 约 [-1,1]; 聚合后 bank-year 均值)'
    if '_iv' in rep or rep.endswith('_iv'):
        return '工具变量 (与被工具化内生变量同量纲)'
    if 'entropy' in rep:
        return '归一化熵 [0,1]'
    if 'staleness' in rep or 'boilerplate' in rep or 'sim' in rep:
        return '相似度/比率 [0,1]'
    if any(t in rep for t in ('cent', 'clustering', 'coreness', 'constraint', 'density')):
        return '网络结构指标 (无量纲)'
    if rep in ('target_bank',):
        return '标识符 (字符串)'
    if rep in ('year',):
        return '年份'
    return '无量纲得分/指标 (WP0 初判待写手校对)'


def draft_formula(fam: dict) -> str:
    kind = fam['kind']
    mapping = {
        'network_metric': '年度银行共现网络 (networkx) 上的结构指标; 判据变体 {同篇/±1句 _win1/同句 _sent}',
        'rule_ablation': '状态机 Σ|final| 自归一化词典语调 (指定语言学规则子集) → bank-year 均值',
        'political_weight': 'du_2022 词典语调, political_positive 权重 ∈{0.0,0.5,1.0} → bank-year 均值',
        'llm_per_model': '单一 LLM 模型文章级语调/得分 → bank-year 聚合 (verified 门控)',
        'llm_class_per_model': '单一 LLM 模型分类维度占比 = 该模型判为目标类篇数 / 该模型 verified 篇数',
        'bert_per_model': '单一 BERT 模型文章级概率/符号语调 → bank-year 聚合',
        'bert_distribution': 'BERT 概率列 $0 后处理分布形状测度 (熵/极端占比/偏度/跨模型/年内动态)',
        'benefit_dimension': '嵌入方向向量投影得分 (维度锚点) → bank-year 均值; 六轨 {full,ctx,ss}×{MAIN,_lg}',
        'iv_engine': 'IV 引擎构造 (同组 LOO 均值 / 广义 Bartik / 媒体 house-style 暴露)',
        'structural': '主键结构列 (无导出公式)',
    }
    return mapping.get(kind, '(WP0 初判占位 — 以家族 md frontmatter formula: 为准, 写手对源码校对)')


# ---------------------------------------------------------------------------
# _index.json 组装 + 增量 merge
# ---------------------------------------------------------------------------

INDEX_FAMILY_REQUIRED_KEYS = ('file', 'columns', 'tier_by_col', 'core_rationale_by_col',
                              'status', 'batch', 'unit_draft', 'formula_draft',
                              'producer_draft')


def merge_index(existing: dict | None, fresh: dict) -> dict:
    """增量 merge (计划 §1a): 面板列变/重跑时新列 → 新条目 draft; 存量条目的
    tier/状态/rationale/签核**只增不改**, 绝不全量重写。

    键 = 家族 file 名 (slug 稳定)。纯函数 (供 gate 测试直接调用)。
    """
    if not existing or not existing.get('families'):
        return fresh
    merged = {
        # 顶层签核/白名单以存量为准 (只增不改)
        'tier_signoff': existing.get('tier_signoff', fresh.get('tier_signoff', {})),
        'structural_whitelist': existing.get('structural_whitelist',
                                             fresh.get('structural_whitelist', [])),
        'families': {},
    }
    old_by_file = {fam['file']: (fid, fam) for fid, fam in existing['families'].items()}
    new_by_file = {fam['file']: (fid, fam) for fid, fam in fresh['families'].items()}
    used_ids: set[str] = set(existing['families'].keys())

    # 1) 存量家族全部原样保留; 若 fresh 同 file 家族有新列 → 仅追加
    for file_key, (old_fid, old_fam) in old_by_file.items():
        fam = json.loads(json.dumps(old_fam))  # deep copy, 不动原对象
        if file_key in new_by_file:
            _, new_fam = new_by_file[file_key]
            for col in new_fam['columns']:
                if col not in fam['columns']:
                    fam['columns'].append(col)
                    fam['tier_by_col'][col] = new_fam['tier_by_col'].get(col, 'standard')
                    r = new_fam['core_rationale_by_col'].get(col)
                    if r:
                        fam['core_rationale_by_col'][col] = r
        merged['families'][old_fid] = fam

    # 2) 全新家族: 续号追加 (只追加不重排)
    max_num = max((int(fid[1:]) for fid in used_ids), default=0)
    for file_key, (new_fid, new_fam) in sorted(
            new_by_file.items(), key=lambda kv: min(kv[1][1]['columns'])):
        if file_key in old_by_file:
            continue
        max_num += 1
        merged['families'][f'F{max_num:03d}'] = new_fam
    return merged


# ---------------------------------------------------------------------------
# 写手输入包三件套 (计划 §6)
# ---------------------------------------------------------------------------

_KW_EXPANSION = {
    'tone': ['tone', 'sentiment'], 'cent': ['centrality', 'network'],
    'herd': ['herd', 'herding'], 'staleness': ['stale', 'staleness', 'novelty'],
    'boilerplate': ['boilerplate', 'template'], 'bartik': ['bartik', 'shift-share'],
    'iv': ['instrument', 'instrumental'], 'entropy': ['entropy', 'disagreement'],
    'skew': ['skew', 'skewness', 'crash'], 'clarity': ['clarity', 'readability'],
    'attention': ['attention', 'coverage'], 'benefit': ['csr', 'social', 'benefit'],
    'strat': ['differentiation', 'strategic', 'distinctive'],
    'collab': ['collaboration', 'open innovation', 'alliance'],
    'subst': ['substantive', 'symbolic'], 'sub': ['substantive', 'symbolic'],
    'tech': ['technology', 'innovation'], 'llm': ['llm', 'gpt', 'language model'],
    'bert': ['bert', 'transformer'], 'dict': ['dictionary', 'lexicon'],
    'peer': ['peer', 'spillover'], 'shock': ['shock', 'contagion', 'spillover'],
    'cogn': ['cognitive', 'similarity'], 'emb': ['embedding', 'semantic'],
    'staleness_full': ['staleness'], 'media': ['media', 'newspaper'],
    'fintech': ['fintech', 'digital'], 'polw': ['political', 'state media'],
    'net': ['network'], 'brok': ['brokerage', 'broker'], 'gf': ['brokerage', 'gould'],
    'salience': ['salience'], 'clarity_score': ['readability'],
    'rare': ['rare word', 'readability', 'complexity'],
    # P2-⑧ (2026-07-11) 词典基名 → dictionary/构成性锚映射: 组件/衍生家族 (如
    # du_2022_neg_count) 的关键词此前只剩噪声 token, 检索段漏掉该词典的构成性锚。
    # 锚 token = 池渲染行内实存的 DOI/题名子串 (逐条对 874 白名单池核验, 零臆造):
    #   du_2022   → Du et al. (2022, RoF, 10.1093/rof/rfab036) 'rfab036'
    #   loughran  → L&M (2011, JF, 10.1111/j.1540-6261.2010.01625.x) 'when is a liability'
    #   jiang_2021→ 姜富伟等 (2021, 经济学(季刊), 10.13821/j.cnki.ceq.2021.04.10) 'ceq.2021.04.10'
    #   bian_2021 → Bian et al. (2021, SSRN, 10.2139/ssrn.3446388) 'ssrn.3446388'
    #   you_2018  → You, Zhang & Zhang (2018, RFS, 10.1093/rfs/hhx055) 'power of the pen'
    #   yao_2021  → 池内未检得独立锚 (2026-07-11 探测), 仅给 dictionary/lexicon 泛化词
    'du': ['dictionary', 'lexicon', 'rfab036'],
    'loughran': ['dictionary', 'lexicon', 'when is a liability'],
    'jiang': ['dictionary', 'lexicon', 'ceq.2021.04.10'],
    'bian': ['dictionary', 'lexicon', 'ssrn.3446388'],
    'you': ['dictionary', 'lexicon', 'power of the pen'],
    'yao': ['dictionary', 'lexicon'],
}
# P2-⑧/NIT (2026-07-11): +sent/win1 (网络判据后缀切词成 'sent' 会把无关 sentiment
# 文献顶到网络家族池首位) + l2/l2c/l3 (归族层级前缀, 纯机械噪声)
_KW_STOP = frozenset({'full', 'ctx', 'ss', 'lg', 'avg', 'mean', 'sum', 'min', 'max',
                      'yr', 'n', 'the', 'of', 'frac', 'score', 'is', 'in', 'bank',
                      '2021', '2022', '2018', 'zh', 'cn',
                      'sent', 'win1', 'l2', 'l2c', 'l3'})


def family_keywords(fam_key: str, cols: list[str]) -> list[str]:
    toks: set[str] = set()
    for src in [fam_key] + cols[:6]:
        for t in re.split(r'[_\W]+', src.lower()):
            if not t or t in _KW_STOP or t.isdigit() or len(t) <= 1:
                continue
            toks.add(t)
            for kw in _KW_EXPANSION.get(t, []):
                toks.add(kw)
    return sorted(toks)


def load_citation_pool() -> list[tuple[str, str, str]]:
    """白名单引文候选池: audit_dois.FILES 全量 extract_refs → [(doi, 渲染行, 源文件)]。"""
    sys.path.insert(0, str(_HERE.parent))
    import audit_dois  # noqa: E402  (同目录脚本; import 不触网络)
    pool: dict[str, tuple[str, str]] = {}
    for f in audit_dois.FILES:
        if not os.path.exists(f):
            continue
        for doi, (line, short) in audit_dois.extract_refs(f).items():
            if doi not in pool or len(line) > len(pool[doi][0]):
                pool[doi] = (line, short)
    return [(doi, line, short) for doi, (line, short) in sorted(pool.items())]


# 家族 → 所属论文 (manuscript refs 检索用) 的关键词映射
_PAPER_KEYWORD_MAP = [
    (re.compile(r'attention|attn|ft_vol'), 'bank_fintech_attention'),
    (re.compile(r'sub_frac|subst'), 'bank_fintech_substance'),
    (re.compile(r'tech_frac|app_frac|locus'), 'bank_fintech_locus'),
    (re.compile(r'collab'), 'bank_fintech_collab'),
    (re.compile(r'benefit'), 'benefit_society'),
    (re.compile(r'brok|gf_|net_|cent|clustering|coreness|constraint|neg_shock|cogn|emb_peer'),
     'brokerage_network'),
    (re.compile(r'strat'), 'strategic_diff'),
    (re.compile(r'clarity|readab|rare_word'), 'bank_news_clarity'),
    (re.compile(r'disagree|cross_outlet'), 'bank_media_disagreement'),
    (re.compile(r'llm_peer'), 'llm_peer'),
    (re.compile(r'tone|sentiment|llm|bert|dict|polw'), 'bank_fintech_tone'),
]


def paper_for_family(fam_key: str, cols: list[str]) -> str | None:
    text = fam_key + ' ' + ' '.join(cols[:5])
    for pat, pid in _PAPER_KEYWORD_MAP:
        if pat.search(text):
            return pid
    return None


def manuscript_refs_text(pid: str) -> str:
    """该家族所属论文 manuscript 的参考文献段全量 (refs.bib 优先, collab 用 md 节)。"""
    assets = _NEWS_PROCESS_ROOT / 'papers_assets' / pid
    bib = assets / 'drafts' / 'zh' / 'refs.bib'
    if bib.exists():
        return f'(来源: {bib.relative_to(_NEWS_PROCESS_ROOT)})\n\n```bibtex\n' + \
            bib.read_text(encoding='utf-8') + '\n```\n'
    md = assets / 'manuscript_zh.md'
    if md.exists():
        txt = md.read_text(encoding='utf-8')
        m = re.search(r'^##\s*参考文献\s*$(.*?)(?=^##\s|\Z)', txt, re.M | re.S)
        if m:
            return f'(来源: {md.relative_to(_NEWS_PROCESS_ROOT)} 参考文献节)\n' + m.group(1)
    return f'(paper={pid} 无 papers_assets manuscript refs — 以白名单检索段为准)\n'


def preload_sources() -> dict[str, str]:
    texts: dict[str, str] = {}
    for sub in ('pipeline', 'papers', 'core'):
        for p in sorted((_NEWS_PROCESS_ROOT / sub).rglob('*.py')):
            if 'stata_templates' in str(p) or '__pycache__' in str(p):
                continue
            try:
                texts[str(p.relative_to(_NEWS_PROCESS_ROOT))] = p.read_text(
                    encoding='utf-8', errors='replace')
            except OSError:
                continue
    return texts


def _fallback_prefix_bases(bases: list[str]) -> list[str]:
    """P2-⑦ (2026-07-11) 渐进前缀兜底基名: 程序化拼名列族 (f-string 组装列名, 如
    du_2022_neg_count) 的完整基名在源码中结构性零命中 — 逐级剥尾 token 后再 grep
    (du_2022_neg_count → du_2022_neg → du_2022), 命中的是真实 SSOT 常量/模块
    (词典基名/族前缀), 保证兜底摘录仍以实际源码为据 (零手抄)。
    单 token 短前缀 (<5 字符且无 '_') 停止, 防 'du'/'n' 级噪声全仓乱命中
    (阈值 5: 'cater'/'disag' 族前缀实测命中真实 producer runner.py, 2026-07-11 校准)。
    """
    out: list[str] = []
    for b in bases:
        parts = b.split('_')
        for k in range(len(parts) - 1, 0, -1):
            cand = '_'.join(parts[:k])
            if '_' not in cand and len(cand) < 5:
                break
            if cand not in out:
                out.append(cand)
    return out


def _grep_excerpt(bases: list[str], sources: dict[str, str], radius: int,
                  max_files: int, note: str = '') -> tuple[list[str], list[str]]:
    """按基名列表 grep 打分 → top 文件 ±radius 行摘录。返回 (parts, producers)。"""
    scored: dict[str, int] = {}
    for path, text in sources.items():
        n = sum(text.count(b) for b in bases)
        if n > 0:
            scored[path] = n
    top = sorted(scored.items(), key=lambda kv: -kv[1])[:max_files]
    parts: list[str] = []
    producers: list[str] = []
    for path, n in top:
        producers.append(path)
        lines = sources[path].splitlines()
        # 首个命中行
        hit_line = None
        for i, ln in enumerate(lines):
            if any(b in ln for b in bases):
                hit_line = i
                break
        if hit_line is None:
            continue
        lo, hi = max(0, hit_line - radius), min(len(lines), hit_line + radius + 1)
        snippet = '\n'.join(f'{j + 1:6d}\t{lines[j]}' for j in range(lo, hi))
        parts.append(f'### {path} (命中 {n} 次{note}; 摘录 L{lo + 1}-L{hi})\n\n```python\n'
                     f'{snippet}\n```\n')
    return parts, producers


def source_excerpt_for(cols: list[str], sources: dict[str, str],
                       radius: int = 30, max_files: int = 2) -> tuple[str, list[str]]:
    """producer 模块按基名 grep 自动截取相关函数 ±radius 行 (计划 §6 ②)。
    返回 (excerpt_md, producer_paths)。

    P2-⑦ (2026-07-11): 完整基名零命中时启用渐进前缀兜底 (_fallback_prefix_bases) —
    程序化拼名列族至少给出 producer 模块与相关常量/函数摘录, 不再把 44% 家族的
    producer 定位成本整体转嫁写手; 兜底摘录在标头显式标注, 写手仍须校对。
    """
    bases: list[str] = []
    for c in cols[:4]:
        b = _strip_base(c)
        if b not in bases:
            bases.append(b)
    parts, producers = _grep_excerpt(bases, sources, radius, max_files)
    if not parts:
        fb = _fallback_prefix_bases(bases)
        if fb:
            parts, producers = _grep_excerpt(
                fb, sources, radius, max_files,
                note=f'; SSOT 前缀兜底 {fb[:3]}')
        if parts:
            parts.insert(0, '(完整基名零命中 — 以下为渐进前缀 SSOT 兜底摘录, '
                            'P2-⑦; 写手须按摘录校对 producer 归属)\n')
    if not parts:
        parts.append('(未在 pipeline/papers/core 源码中按基名命中 — 写手须人工定位 producer)\n')
    return '\n'.join(parts), producers


# ---------------------------------------------------------------------------
# 家族 md 骨架生成 (格式与 WP1 引擎 parse_family_md/load_library 严格兼容)
# ---------------------------------------------------------------------------

def emit_family_skeletons(merged: dict, longdesc_dir: Path) -> tuple[int, int]:
    """逐家族写 F###_<slug>.md 骨架。**只写缺失文件, 绝不覆盖已有** (写手成果保护)。

    格式契约 (WP1 codebook_longdesc.parse_family_md / _TEMPLATE_family.md):
    - frontmatter YAML (--- 定界): family_id/columns/unit/formula/producer/upstream/
      citations: []/new_dois: [] — columns 严格 == _index.json 该家族 columns
      (列集合三处全等 gate); frontmatter 存在后 _index 的 *_draft 不再被消费 (防双头);
    - "## CORE" 节 + 逐列 "## VAR: <panel 实名>" 节 (骨架占位中文短文, status=draft
      → 字数闸为告警不崩);
    - 段首小标题契约 (P1-1 裁决 2026-07-11): CORE 节以【构念与来源】开头、VAR 节以
      【变体差分】开头 — 内联小标题归骨架/写手正文, 组装器不再前置这两个标题
      (只加机械段标题), 双侧同注即触发组装器 _DOUBLE_SEG_TITLE_RE fail-loud;
    - 人工区禁 markdown 结构语法 (行首 #/成对 **/行首 |/fence) 与 {word:...} 占位符形态;
      正文禁 doi.org;
    - 尾部空渲染尾节 (rendered-citations fence, citations=[] → 渲染段空 == 集合空,
      渲染物化一致性断言②恒真, materialize 幂等 no-op)。
    Returns: (新写文件数, 已存在跳过数)。
    """
    import yaml

    from news_process.pipeline.panel.codebook_longdesc import RENDERED_BEGIN, RENDERED_END

    n_new = n_exist = 0
    for fid, fam in merged['families'].items():
        path = longdesc_dir / fam['file']
        if path.exists():
            n_exist += 1
            continue
        fm = {
            'family_id': fid,
            'columns': list(fam['columns']),
            'unit': fam.get('unit_draft', ''),
            'formula': fam.get('formula_draft', ''),
            'producer': fam.get('producer_draft', ''),
            'upstream': [],
            'citations': [],
            'new_dois': [],
        }
        fm_yaml = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False,
                                 width=10000, default_flow_style=False)
        lines = [
            '---',
            fm_yaml.rstrip('\n'),
            '---',
            '',
            '## CORE',
            '',
            '【构念与来源】',
            f'骨架占位 — 本节为家族核心长文, 待 WP4 写手按写手输入包三件套 '
            f'(build/codebook_inputs/{fid}/ 下 columns.json、source_excerpt.md、'
            f'citations_pool.md) 撰写。本骨架由 build_codebook_family_map 机械生成, '
            f'家族 status=draft, 字数闸与引文闸在 draft 态降级为告警计数。'
            f'单位初判: {fam.get("unit_draft", "")}。公式初判见 frontmatter formula 字段, '
            f'写手须对 producer 源码逐条校对后改写。',
            '',
        ]
        for c in fam['columns']:
            tier = fam['tier_by_col'].get(c, 'standard')
            lines += [
                f'## VAR: {c}',
                '',
                '【变体差分】',
                f'骨架占位 — 本列 tier={tier}, 待写手写清该列区别于家族 canonical 的'
                f'精确差分语义 (轨道、模型、阈值、判据、权重、滞后)。',
                '',
            ]
        lines += [RENDERED_BEGIN, '', RENDERED_END, '']
        path.write_text('\n'.join(lines), encoding='utf-8', newline='\n')
        n_new += 1
    return n_new, n_exist


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description='WP0 家族映射机械化 (计划 §5 WP0)')
    ap.add_argument('--skip-verification', action='store_true',
                    help='跳过 instantiate 验证轨 (退化为 spec 主轨; 报告披露)')
    ap.add_argument('--skip-input-packs', action='store_true',
                    help='只产 _index.json + 签核提案 (调试用)')
    ap.add_argument('--apply-signoff', action='store_true',
                    help='把 2026-07-10 用户签核记录 (SIGNOFF_2026_07_10 + 复算 '
                         'signed_manifest_sha) 落 _index.json 顶层 tier_signoff')
    ap.add_argument('--emit-skeletons', action='store_true',
                    help='逐家族生成 config/codebook_longdesc/F*.md 骨架 (只写缺失, 绝不覆盖)')
    args = ap.parse_args(argv)

    index_path = _NEWS_PROCESS_ROOT / 'config' / 'codebook_longdesc' / '_index.json'
    inputs_dir = _NEWS_PROCESS_ROOT / 'build' / 'codebook_inputs'
    inputs_dir.mkdir(parents=True, exist_ok=True)
    index_path.parent.mkdir(parents=True, exist_ok=True)

    print('[1/7] 读 51 面板 (缺失=拒跑, 禁回退 40) ...')
    panel_cols, dtypes, panel_path = load_panel_columns()
    panel_set = set(panel_cols)
    print(f'      面板: {panel_path}')
    print(f'      列数: {len(panel_cols)}')

    print('[2/7] spec 主轨: 读 11 篇 paper_spec ...')
    specs = read_paper_specs()
    print(f'      specs: {len(specs)} 篇')
    if len(specs) != 11:
        print(f'[FATAL] paper_spec 数 {len(specs)} != 11 — 宇宙漂移, 拒跑。')
        raise SystemExit(1)

    print('[3/7] tier 三态初判 (类别 1-7 显式名单; 幻影名 fail-loud) ...')
    core_rat, pending_rat = build_core_candidates(specs, panel_set)
    controls = collect_controls(_NEWS_PROCESS_ROOT / 'papers')

    verification: dict = {'scanned': {}, 'failures': {}, 'skipped': args.skip_verification}
    if not args.skip_verification:
        print('[4/7] 验证轨: instantiate 白名单模板 → 扫 regress 行 ...')
        verification.update(run_verification_track(panel_set))
    else:
        print('[4/7] 验证轨: --skip-verification (退化为 spec 主轨, 报告披露)')

    # 验证轨裁决 (计划 v2.8): 仅存在性核验主轨候选; spec 外新列 → needs_review
    scanned_all: set[str] = set()
    for pid, info in verification.get('scanned', {}).items():
        scanned_all |= set(info['cols_hit'])
    core_verified = {c: (c in scanned_all) for c in core_rat}
    needs_review_cols = sorted(
        c for c in scanned_all
        if c not in core_rat and c not in STRUCTURAL_WHITELIST
        and not is_negative_listed(c, controls))

    print('[5/7] 三级归族 ...')
    families_raw = build_families(panel_cols)
    # pending 哨兵家族 (面板不实存, 长文照写入库, 守恒/notes 对账显式排除)
    dv_sentinels = sorted(c for c in pending_rat if c != 'cross_outlet_tone_variance_full')
    families_raw['pending_external_financial_dvs'] = {
        'columns': dv_sentinels, 'level': 1, 'kind': 'pending_sentinel',
        'needs_family_review': False}
    if 'cross_outlet_tone_variance_full' in pending_rat:
        families_raw['pending_disagreement_treatment'] = {
            'columns': ['cross_outlet_tone_variance_full'], 'level': 1,
            'kind': 'pending_sentinel', 'needs_family_review': False}

    # 组装 fresh index (family_id 按家族首列字典序一次性分配三位号)
    fam_items = sorted(families_raw.items(), key=lambda kv: min(kv[1]['columns']))
    fresh: dict = {'tier_signoff': {}, 'structural_whitelist': list(STRUCTURAL_WHITELIST),
                   'families': {}}
    sources = {} if args.skip_input_packs else preload_sources()
    fam_meta: dict[str, dict] = {}
    for i, (fam_key, fam) in enumerate(fam_items, start=1):
        fid = f'F{i:03d}'
        cols = sorted(fam['columns'])
        tier_by_col: dict[str, str] = {}
        rationale_by_col: dict[str, str] = {}
        for c in cols:
            if c in pending_rat:
                tier_by_col[c] = 'pending'
                rationale_by_col[c] = ' / '.join(pending_rat[c])
            elif c in core_rat:
                tier_by_col[c] = 'core'
                rationale_by_col[c] = ' / '.join(core_rat[c])
            else:
                tier_by_col[c] = 'standard'
        excerpt, producers = ('', [])
        if not args.skip_input_packs:
            excerpt, producers = source_excerpt_for(cols, sources)
        entry = {
            'file': f'{fid}_{_slug(fam_key)}.md',
            'columns': cols,
            'tier_by_col': tier_by_col,
            'core_rationale_by_col': rationale_by_col,
            'status': 'draft',
            'batch': None,
            'unit_draft': draft_unit(cols),
            'formula_draft': draft_formula(fam),
            'producer_draft': ' ; '.join(producers) if producers else '(待 WP4 写手定位)',
        }
        if fam['needs_family_review']:
            entry['needs_family_review'] = True
        fam_nr = sorted(set(cols) & set(needs_review_cols))
        if fam_nr:
            entry['needs_review_cols'] = fam_nr
        fresh['families'][fid] = entry
        fam_meta[fid] = {'key': fam_key, 'level': fam['level'], 'kind': fam['kind'],
                         'excerpt': excerpt}

    # 增量 merge (存量条目只增不改)
    existing = None
    if index_path.exists():
        existing = json.loads(index_path.read_text(encoding='utf-8'))
    merged = merge_index(existing, fresh)

    # ---- 守恒 gate (脚本内自验, fail-loud) ----
    print('[6/7] 守恒 gate 自验 ...')
    all_nonpending: list[str] = []
    all_listed = 0
    for fid, fam in merged['families'].items():
        nonp = [c for c in fam['columns'] if fam['tier_by_col'].get(c) != 'pending']
        all_nonpending.extend(nonp)
        all_listed += len(fam['columns'])
    nonpending_set = set(all_nonpending)
    if len(all_nonpending) != len(nonpending_set):
        print('[FATAL] 守恒 gate: 同列被多家族重复收录。')
        raise SystemExit(1)
    if nonpending_set != panel_set:
        orphan = panel_set - nonpending_set
        phantom = nonpending_set - panel_set
        print(f'[FATAL] 守恒 gate: 孤儿列 {len(orphan)} / 幻影列 {len(phantom)}')
        for c in sorted(orphan)[:20]:
            print('  orphan:', c)
        for c in sorted(phantom)[:20]:
            print('  phantom:', c)
        raise SystemExit(1)
    n_core = sum(1 for fid, fam in merged['families'].items()
                 for c, t in fam['tier_by_col'].items() if t == 'core')
    n_pending = sum(1 for fid, fam in merged['families'].items()
                    for c, t in fam['tier_by_col'].items() if t == 'pending')
    ratio = (n_core + n_pending) / len(panel_cols)
    if ratio > 0.10:
        print(f'[FATAL] 反灌水闸: core+pending 占比 {ratio:.2%} > 10%。')
        raise SystemExit(1)
    for fid, fam in merged['families'].items():
        for c, t in fam['tier_by_col'].items():
            if t in ('core', 'pending') and not fam['core_rationale_by_col'].get(c):
                print(f'[FATAL] rationale 闸: {c} (tier={t}) 无 core_rationale。')
                raise SystemExit(1)

    # ---- 签核落库 (--apply-signoff; signed_manifest_sha = 复算联合哈希) ----
    if args.apply_signoff:
        old_ts = merged.get('tier_signoff') or {}
        new_sha = compute_signed_manifest_sha(merged)
        if old_ts.get('signed_manifest_sha') and old_ts['signed_manifest_sha'] != new_sha:
            print('[WARN] 既有签核哈希与当前清单不一致 — 按 --apply-signoff 显式重签。')
        merged['tier_signoff'] = dict(SIGNOFF_2026_07_10,
                                      signed_manifest_sha=new_sha)
        print(f'      tier_signoff 落库: signed_manifest_sha={new_sha}')

    # 落盘 _index.json
    index_path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'      _index.json -> {index_path}')

    # ---- 家族 md 骨架 (--emit-skeletons; 只写缺失绝不覆盖) ----
    if args.emit_skeletons:
        n_new, n_exist = emit_family_skeletons(merged, index_path.parent)
        print(f'      骨架 md: 新写 {n_new} / 已存在跳过 {n_exist} -> {index_path.parent}')

    # ---- 写手输入包三件套 ----
    # 单例 = 恰 1 列且 needs_family_review (粗聚 pass B 家族 ≥2 列, 不计单例)
    n_singleton = sum(1 for fam in merged['families'].values()
                      if fam.get('needs_family_review') and len(fam['columns']) == 1)
    n_coarse = sum(1 for fam in merged['families'].values()
                   if fam.get('needs_family_review') and len(fam['columns']) >= 2)
    n_fam = len(merged['families'])
    if not args.skip_input_packs:
        print('[7/7] 写手输入包三件套 ...')
        pool = load_citation_pool()
        for fid, fam in merged['families'].items():
            fam_dir = inputs_dir / fid
            fam_dir.mkdir(parents=True, exist_ok=True)
            meta = fam_meta.get(fid, {})
            cols = fam['columns']
            # ① columns.json (列清单 + tier + 差分维度提示)
            col_entries = []
            for c in cols:
                hints = []
                if re.search(r'_(full|ctx|ss)($|_lg$)', c):
                    hints.append('三轨 full/ctx/ss')
                if '_lg' in c:
                    hints.append('_lg co-primary 对偶 (text-embedding-3-large)')
                if re.search(r'_(win1|sent)$', c):
                    hints.append('网络判据变体 (银行∧银行)')
                if re.search(r'_lag\d*', c):
                    hints.append('滞后派生')
                if re.search(r'_(vw|mw|hw)$', c):
                    hints.append('加权聚合变体')
                if re.search(r'polw(00|05|10)', c):
                    hints.append('政治词权重梯子')
                if re.search(r'_(t80|t95)$', c):
                    hints.append('极端占比阈值梯子')
                if re.search(r'_(c2|c5)$', c):
                    hints.append('罕见词 cutoff 梯子')
                if re.search(r'_n\d+($|_)', c):
                    hints.append('top-k N 梯子')
                col_entries.append({
                    'name': c,
                    'tier': fam['tier_by_col'].get(c, 'standard'),
                    'dtype': dtypes.get(c, '(pending — 面板不实存)'),
                    'core_rationale': fam['core_rationale_by_col'].get(c, ''),
                    'diff_dimension_hints': hints,
                    'needs_review': c in fam.get('needs_review_cols', []),
                })
            (fam_dir / 'columns.json').write_text(
                json.dumps({
                    'family_id': fid, 'file': fam['file'], 'status': fam['status'],
                    'family_key': meta.get('key', ''), 'level': meta.get('level'),
                    'kind': meta.get('kind', ''),
                    'unit_draft': fam['unit_draft'],
                    'formula_draft': fam['formula_draft'],
                    'producer_draft': fam['producer_draft'],
                    'needs_family_review': fam.get('needs_family_review', False),
                    'columns': col_entries,
                }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            # ② source_excerpt.md
            (fam_dir / 'source_excerpt.md').write_text(
                f'# {fid} producer 源码摘录 (机械 grep ±30 行; WP0 初判, 写手校对)\n\n'
                + (meta.get('excerpt') or '(略)') + '\n', encoding='utf-8')
            # ③ citations_pool.md (白名单 874 渲染行按关键词 top-30 + manuscript refs 全量)
            kws = family_keywords(meta.get('key', fid), cols)
            scored = []
            for doi, line, short in pool:
                s = sum(1 for kw in kws if kw in line.lower())
                if s > 0:
                    scored.append((s, doi, line, short))
            scored.sort(key=lambda t: (-t[0], t[1]))
            top30 = scored[:30]
            pid = paper_for_family(meta.get('key', ''), cols)
            lines_md = [
                f'# {fid} 引文候选池 (白名单内检索; 铁律: 只准引用本文件内 DOI, '
                f'新 DOI 须走 new_dois 台账三关)\n',
                f'家族关键词: {", ".join(kws)}\n',
                f'\n## 白名单检索 top-{len(top30)} (874-DOI 池)\n',
            ]
            for s, doi, line, short in top30:
                lines_md.append(f'- [score={s}] ({short}) {line}')
            if not top30:
                lines_md.append('- (关键词零命中 — 写手从所属论文 refs 段选锚或走 new_dois 流程)')
            lines_md.append('\n## 所属论文 manuscript 参考文献段全量\n')
            if pid:
                lines_md.append(f'所属论文 (机械关键词映射): {pid}\n')
                lines_md.append(manuscript_refs_text(pid))
            else:
                lines_md.append('(未映射到具体论文 — pipeline 级家族; 以白名单检索段为准)')
            (fam_dir / 'citations_pool.md').write_text(
                '\n'.join(lines_md) + '\n', encoding='utf-8')
        print(f'      输入包: {n_fam} 家族 × 3 件套 -> {inputs_dir}')
    else:
        print('[7/7] --skip-input-packs: 跳过输入包')

    # ---- 签核提案 ----
    _write_signoff_proposal(
        inputs_dir / 'wp0_core_signoff_proposal.md',
        merged, panel_cols, core_rat, pending_rat, core_verified,
        needs_review_cols, verification, n_fam, n_singleton, ratio)

    print('')
    print('===== WP0 完成 =====')
    print(f'面板列数           : {len(panel_cols)}')
    print(f'家族总数           : {n_fam}')
    print(f'  L1 SSOT 精确匹配 : {sum(1 for m in fam_meta.values() if m["level"] == 1)}')
    print(f'  L2 推断聚类      : {sum(1 for m in fam_meta.values() if m["level"] == 2)}'
          f' (含粗聚 needs_review {n_coarse})')
    print(f'  L3 单例          : {n_singleton} ({n_singleton / max(n_fam, 1):.1%} 家族口径'
          f'{" — >15% 触发人工复审归并" if n_singleton / max(n_fam, 1) > 0.15 else ""})')
    print(f'core 列数          : {n_core} ({n_core / len(panel_cols):.2%})')
    print(f'pending 列数       : {n_pending}')
    print(f'core+pending 占比  : {ratio:.2%} (闸 <=10%)')
    print(f'needs_review 列数  : {len(needs_review_cols)}')
    print(f'验证轨失败 paper   : {list(verification.get("failures", {}).keys()) or "无"}')
    return 0


def _write_signoff_proposal(path: Path, merged: dict, panel_cols: list[str],
                            core_rat: dict, pending_rat: dict, core_verified: dict,
                            needs_review_cols: list[str], verification: dict,
                            n_fam: int, n_singleton: int, ratio: float) -> None:
    n_core = len(core_rat)
    n_pending = len(pending_rat)
    by_cat: dict[str, list[tuple[str, str]]] = {}
    for col, rats in sorted(core_rat.items()):
        cat = rats[0].split(']')[0] + ']'
        by_cat.setdefault(cat, []).append((col, ' / '.join(rats)))
    lines = [
        '# WP0 core 清单签核提案 (tier 三态机械初判 → 用户签核)',
        '',
        f'- 日期: 2026-07-10 | 面板: 51_panel_with_controls ({len(panel_cols)} 列, 生成期实读)',
        '- 权威口径: scripts/audit/STATA_VARATTR_AND_CODEBOOK_LONGDESC_EXECUTION_PLAN_2026-07-10.md (v2.9) §1/§1a',
        '- 签核后落 `_index.json` 顶层 `tier_signoff` (signed_manifest_sha = core 清单 + 结构列豁免白名单联合哈希)。',
        '',
        '## 一、三 gate 实测数字',
        '',
        f'| gate | 实测 | 闸 |',
        f'|---|---|---|',
        f'| 守恒 (非 pending 家族列 == 面板列) | {len(panel_cols)} == {len(panel_cols)}, 0 孤儿 0 重复 | 全等 |',
        f'| core 候选 ⊆ panel.columns (pending 豁免) | 0 幻影名 (fail-loud 通过) | 0 |',
        f'| core(含 pending) 占比 | {n_core}+{n_pending} = {n_core + n_pending} / {len(panel_cols)} = {ratio:.2%} | <=10% |',
        '',
        f'家族总数 {n_fam}; 单例家族 {n_singleton} ({n_singleton / max(n_fam, 1):.1%})'
        f'{" — **>15% 触发人工复审归并 (计划 §1 ③)**" if n_singleton / max(n_fam, 1) > 0.15 else " (<=15%, 不触发复审)"}。',
        '',
        '## 二、四项收窄决策 (对用户字面要求的收窄, 请逐项确认; 计划 §1a v2.5 忠实性披露)',
        '',
        '1. **结构列豁免**: `target_bank`/`year` 豁免 >=1000 汉字闸, 仅须 12 字段完整 + 短描述, 不进 core;',
        '2. **pending 哨兵列暂不注 notes**: 主 DV 外部财务哨兵列不在 dta 中 (事实约束), 长文照写入 codebook 附录"待接入变量"章, 财务面板接入后自动升 core 并回补;',
        '3. **顶刊闸允许 field 领域刊 <=30%**: 引文顶刊计分三分类 top/field/wp-preprint, (top+field 内) 非 top 占比 >30% 打回;',
        '4. **wp/preprint 不计入"非顶刊"分母**: 与 arXiv 方法学补充锚地位一致。',
        '',
        '## 三、core 清单 (按类别分组, 逐列 rationale)',
        '',
    ]
    for cat in sorted(by_cat):
        lines.append(f'### {cat} ({len(by_cat[cat])} 列)')
        lines.append('')
        for col, rat in by_cat[cat]:
            v = '' if core_verified.get(col) else ' ⚠未在白名单模板扫描命中(spec 主轨兜底, 存在性=面板实存)'
            lines.append(f'- `{col}` — {rat}{v}')
        lines.append('')
    lines += ['### pending (tier=pending, 排除在守恒/字数/notes 对账之外)', '']
    for col, rats in sorted(pending_rat.items()):
        lines.append(f'- `{col}` — {" / ".join(rats)}')
    lines += [
        '',
        '## 四、验证轨披露',
        '',
        f'- instantiate 方式: 主线/衍生 9 篇 build_replication_package → 临时目录'
        f' ({verification.get("scratch_dir", "(skipped)")}); provisional 两篇扫既有'
        ' papers/<pid>/replication/code/ 已实例化产物 (模板无 {{}} 占位符, instantiate ≡ copy, 字节等价)。',
        f'- 实例化失败 paper: {json.dumps(verification.get("failures", {}), ensure_ascii=False)}',
        f'- 扫描裁决 (计划 v2.8): 仅存在性核验主轨候选; spec 外新列一律 needs_review 不自动入 core;'
        ' bank controls 全体 + 负面清单后缀 (ctx/ss/polw00·10/_c2·_c5/_win1·_sent/_t80·_t95/lag/_src) 已排除。',
        f'- needs_review 列 ({len(needs_review_cols)}): '
        + (', '.join(f'`{c}`' for c in needs_review_cols) if needs_review_cols else '(无)'),
        '',
        '## 四bis、计划点名但 51 面板不实存的 canonical (存在性守卫跳过, 非幻影收录)',
        '',
        ('- ' + '\n- '.join(f'`{c}`' for c in SKIPPED_ABSENT_CANONICALS)
         if SKIPPED_ABSENT_CANONICALS else '- (无)'),
        '- 上述列 (benefit 4 维度六轨 canonical) 由 dimension_analysis 产于 benefit_society 附属'
        ' parquet, 本机 51 面板未 merge → 按"core 全部使用面板实存全名"铁律跳过并披露;'
        ' 面板重生 merge 后重跑 build_codebook_family_map 自动收录。',
        '',
        '## 五、per-paper 白名单模板扫描明细',
        '',
    ]
    for pid, info in sorted(verification.get('scanned', {}).items()):
        lines.append(f'- **{pid}**: 模板 {info["whitelisted_do_files"]} → 命中面板列 '
                     f'{len(info["cols_hit"])} 个')
    ts = merged.get('tier_signoff') or {}
    if ts:
        lines += [
            '',
            '## 六、签核结果 (2026-07-10, 已落库 `_index.json` 顶层 `tier_signoff`)',
            '',
            f'- 日期: {ts.get("date")}',
            f'- 方式: {ts.get("method")}',
            f'- user_ack: {ts.get("user_ack")}',
            f'- signed_manifest_sha: `{ts.get("signed_manifest_sha")}`'
            ' (= core 清单 + pending 清单 + structural_whitelist 联合内容 sha256,'
            ' 复算函数 = build_codebook_family_map.compute_signed_manifest_sha,'
            ' gate = tests/test_codebook_family_map.py::test_tier_signoff_matches_manifest)',
            '- 四问结论: ① core 扩围 150–250 (类别 6-扩围①②③ 已落实, 本文档 §三 为扩围后终版清单);'
            ' ② 四项收窄决策 (§二) 全部批准; ③ 家族粒度保持全量直写;'
            ' ④ needs_review 10 列维持 standard, 顶刊两裁量 (JEL 计 top / 未列名计非 top) 照案。',
            f'- 扩围后 core 终数: {n_core} 列 / pending {n_pending} 列'
            f' / core+pending 占比 {ratio:.2%} (硬闸 <=10% 不变)。',
        ]
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'      签核提案 -> {path}')


if __name__ == '__main__':
    raise SystemExit(main())
