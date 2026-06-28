"""omni 修复组 g-zscore-papers 回归锁 (fix omni, 2026-06-11).

锁定 4 个 finding 的修复后行为 (仅 papers/bank_media_disagreement +
papers/bank_news_clarity 两目录, 按主控组级裁决):

- 01: z_score 直引 Laeven-Levine 的 13 处全部改为 CAR-based 变体更正口径
      (spec / 两 11_table2 模板头注+esttab 表注 / 两 tables.py / 两 replication
      README + code 副本)。
- 02: cross_outlet_tone_variance 同名异构 — disagreement spec 加 39f 实现口径
      披露 + Step 3 矩统一 std→var(ddof=1); BW2012 模板 "direct match" 措辞改与
      clarity spec:71 披露一致 (裸 LLP/贷款比率, 非残差式 discretion)。
- 03: clarity spec tA8 悬空模板 (全仓不存在) 补 "待设计" 诚实标注。
- 04: 论文 10/11 主回归模板 (11_table2 / 13_table4 × 模板+replication code 副本)
      加 fail-loud 守卫: capture confirm variable + 可读报错, 不再 M1 直接 r(111);
      clarity Panel B 的幻影列 listed 单独守卫 (缺失跳过该 panel)。

纯文本/YAML 断言, 不跑 Stata, 不依赖盘上大数据, 不调外部 API。

# 白话: 两篇 provisional 论文的模板里, z_score 的算法其实是用监管资本充足率
# (CAR) 拼的变体, 不是 Laeven-Levine 原版 — 这组测试确保所有引用该文献的地方
# 都老实写明"CAR 变体"; 同名但算法不同的指标要披露差异; 引用了全仓不存在的
# 模板要标"待设计"; 回归用到的列缺失时要给可读报错, 不能让 Stata 抛裸 r(111)。
# (注: stage 49 风险结果三件套已于 2026-06-12 整体移除, z_score 等名称仅作为
# 这两篇论文 spec/模板中的指标占位保留, 与本文件断言不冲突。)
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

PAPERS_DIR = Path(__file__).resolve().parents[1] / 'papers'
DISAGREEMENT = PAPERS_DIR / 'bank_media_disagreement'
CLARITY = PAPERS_DIR / 'bank_news_clarity'

# 修复涉及的全部 Stata 文件 (模板 + replication code 副本须内容同步)
TABLE2_FILES = [
    DISAGREEMENT / 'stata_templates' / '11_table2_main_disagreement_risk.do.tmpl',
    DISAGREEMENT / 'replication' / 'code' / '11_table2_main_disagreement_risk.do',
    CLARITY / 'stata_templates' / '11_table2_main_clarity_risk.do.tmpl',
    CLARITY / 'replication' / 'code' / '11_table2_main_clarity_risk.do',
]
TABLE4_FILES = [
    DISAGREEMENT / 'stata_templates' / '13_table4_heterogeneity.do.tmpl',
    DISAGREEMENT / 'replication' / 'code' / '13_table4_heterogeneity.do',
    CLARITY / 'stata_templates' / '13_table4_heterogeneity.do.tmpl',
    CLARITY / 'replication' / 'code' / '13_table4_heterogeneity.do',
]
CLARITY_TABLE2_FILES = [p for p in TABLE2_FILES if 'clarity' in p.name]
CLARITY_TABLE4_FILES = [
    CLARITY / 'stata_templates' / '13_table4_heterogeneity.do.tmpl',
    CLARITY / 'replication' / 'code' / '13_table4_heterogeneity.do',
]


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


# ============================================================================
# Finding 01 — z_score Laeven-Levine 直引全部加 CAR 变体更正
# ============================================================================


def test_no_undisclosed_laeven_citation_in_both_paper_dirs() -> None:
    """两 paper 目录内任何含 'Laeven' 的源文件行必须同行带 CAR 变体披露标记.

    (排除 __pycache__ 二进制; 防止未来再引入无披露直引 — 这正是本次
    FIX-REGRESSION 的根因: 上轮只修了 1/13 处。)
    """
    markers = ('CAR', '变体', 'variant')
    offenders: list[str] = []
    for base in (DISAGREEMENT, CLARITY):
        for path in sorted(base.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            if path.suffix not in {'.py', '.yaml', '.md', '.do'} and not path.name.endswith('.do.tmpl'):
                continue
            for lineno, line in enumerate(_read(path).splitlines(), start=1):
                if 'Laeven' in line and not any(m in line for m in markers):
                    offenders.append(f'{path}:{lineno}: {line.strip()}')
    assert not offenders, (
        '发现无 CAR 变体披露的 Laeven-Levine 直引 (fix omni-g-zscore-papers-01):\n'
        + '\n'.join(offenders)
    )


def test_disagreement_spec_outcome_has_car_variant_correction() -> None:
    raw = _read(DISAGREEMENT / 'paper_spec.yaml')
    assert 'CAR-based Z-score 变体' in raw
    # primary_formula 行须注明资本项口径
    assert '监管 CAR' in raw
    # YAML 仍可解析且 primary 值不变 (修复仅注释层)
    spec = yaml.safe_load(raw)
    assert spec['outcome']['primary'] == 'z_score'


@pytest.mark.parametrize('path', TABLE2_FILES, ids=lambda p: p.name + ('/tmpl' if p.suffix == '.tmpl' else '/code'))
def test_table2_header_citation_corrected(path: Path) -> None:
    text = _read(path)
    assert 'CAR-based Z-score 变体' in text, f'{path} 头注缺 CAR 变体更正'
    # 旧的无披露 esttab 表注 (直接渲染进发表表格脚注) 必须消失
    assert 'Z-score per Laeven-Levine 2009 JFE.' not in text
    # 新表注: 渲染进 .tex 的脚注必须写明 CAR 变体
    assert 'CAR-based variant (capital term = regulatory CAR' in text


# ============================================================================
# Finding 02 — cross_outlet_tone_variance 同名异构披露 + BW2012 措辞
# ============================================================================


def test_disagreement_spec_discloses_39f_homonym_construction() -> None:
    raw = _read(DISAGREEMENT / 'paper_spec.yaml')
    # 披露注释: 盘上同名列 = 39f 事件窗条件估计量, 与 spec 无条件口径不同
    # (权重描述措辞由 g-audit-family 组并行维护, 此处只锁披露存在性, 不锁字面)
    assert '同名异构' in raw
    assert 'cross_media_alpha.py' in raw
    assert '加权平均到 bank-year' in raw
    spec = yaml.safe_load(raw)
    pc = spec['treatment']['primary_construction']
    # Step 3 矩统一: 列名含 variance → var (ddof=1), 不再是 std 自相矛盾
    assert 'var(outlet_tone[b,t,*], ddof=1)' in pc
    assert 'std(outlet_tone' not in pc
    # treatment.primary 值本身不变 (列名重命名属 M2-M3, 不在本次修复范围)
    assert spec['treatment']['primary'] == 'cross_outlet_tone_variance_full'


@pytest.mark.parametrize('path', CLARITY_TABLE2_FILES, ids=lambda p: p.suffix)
def test_bw2012_direct_match_wording_aligned_with_spec_disclosure(path: Path) -> None:
    """BW2012 'direct match' 措辞须与 clarity spec:71 披露一致.

    当前 loan_loss_provision_discretion 实为裸 LLP/贷款比率, 非 BW2012 残差式
    discretion — 模板注释/列标题/表注均不得再冒充 direct match。
    """
    text = _read(path)
    assert 'direct match' not in text
    assert '"BW2012 LLP"' not in text          # 旧 mtitle
    assert 'LLP Discretion' not in text        # 旧 title
    assert '裸 LLP/贷款' in text                # 头注披露
    assert 'raw LLP/loans ratio' in text       # 渲染进 .tex 的表注披露
    assert '"LLP Ratio"' in text               # 新 mtitle


# ============================================================================
# Finding 03 — clarity spec tA8 悬空模板补 "待设计" 标注
# ============================================================================


def test_clarity_ta8_dangling_template_honestly_annotated() -> None:
    raw = _read(CLARITY / 'paper_spec.yaml')
    assert '模板待设计' in raw
    # 标注必须落在 tA8 块附近 (含模板名的注释披露)
    assert '19_bnc_num_intensity_complementary' in raw
    spec = yaml.safe_load(raw)
    # template 值保持原名 (仅加注释, 不改 spec 数据 → schema 测试不受影响)
    assert spec['tables']['tA8']['template'] == '19_bnc_num_intensity_complementary'
    # 全仓确实不存在该模板 (若未来补齐, 此断言提醒同步移除 "待设计" 标注)
    repo_root = PAPERS_DIR.parent
    hits = list(repo_root.rglob('19_bnc_num_intensity_complementary*'))
    assert hits == [], f'模板已补齐, 请移除 tA8 待设计标注: {hits}'


# ============================================================================
# Finding 04 — fail-loud 守卫: capture confirm + 可读报错 (不再 M1 r(111))
# ============================================================================


@pytest.mark.parametrize('path', TABLE2_FILES + TABLE4_FILES, ids=lambda p: str(p.relative_to(PAPERS_DIR)))
def test_main_regression_guard_before_first_eststo(path: Path) -> None:
    text = _read(path)
    guard_pos = text.find('capture confirm variable')
    eststo_pos = text.find('eststo')
    assert guard_pos != -1, f'{path} 缺 fail-loud 守卫 (capture confirm variable)'
    assert eststo_pos != -1
    assert guard_pos < eststo_pos, f'{path} 守卫必须在第一条回归之前'
    # 可读报错: 指明数据装配点 (01_data_prep + working dataset) 并以 error 111 终止
    assert 'error 111' in text
    assert '01_data_prep' in text
    assert '_paper10_working.dta' in text or '_paper11_working.dta' in text
    assert 'fix(omni-g-zscore-papers-04, 2026-06-11)' in text


@pytest.mark.parametrize('path', TABLE2_FILES, ids=lambda p: str(p.relative_to(PAPERS_DIR)))
def test_table2_required_vars_cover_treatment_controls_and_soe(path: Path) -> None:
    text = _read(path)
    required_line = next(
        (ln for ln in text.splitlines() if ln.startswith('local REQUIRED_VARS')), None,
    )
    assert required_line is not None, f'{path} 缺 REQUIRED_VARS 清单'
    # DV/TX/CTRL_B/CTRL_Y 经 local 展开覆盖; is_soe 是 M6 交互必需
    for token in ("`DV'", "`TX'", "`CTRL_B'", "`CTRL_Y'", 'is_soe'):
        assert token in required_line, f'{path} REQUIRED_VARS 缺 {token}'


@pytest.mark.parametrize('path', CLARITY_TABLE2_FILES, ids=lambda p: p.suffix)
def test_clarity_table2_guards_phantom_external_columns(path: Path) -> None:
    """clarity 的 credit_rating / term_spread / listed 幻影列须有诚实披露.

    credit_rating (外部评级) 与 term_spread (国债曲线) 在 CTRL 里 → 主守卫覆盖,
    报错信息须点名外部数据需求; M_BW 的 loan_loss_provision_discretion 进
    REQUIRED_VARS。
    """
    text = _read(path)
    required_line = next(
        ln for ln in text.splitlines() if ln.startswith('local REQUIRED_VARS')
    )
    assert 'loan_loss_provision_discretion' in required_line
    assert 'credit_rating' in text and '外部评级' in text
    assert 'term_spread' in text and '国债收益率曲线' in text


@pytest.mark.parametrize('path', TABLE4_FILES, ids=lambda p: str(p.relative_to(PAPERS_DIR)))
def test_table4_required_vars_cover_tier_split(path: Path) -> None:
    text = _read(path)
    required_line = next(
        (ln for ln in text.splitlines() if ln.startswith('local REQUIRED_VARS')), None,
    )
    assert required_line is not None, f'{path} 缺 REQUIRED_VARS 清单'
    assert 'implicit_guarantee_tier' in required_line, (
        f'{path} Panel A/D 分组列 implicit_guarantee_tier 未进守卫'
    )


@pytest.mark.parametrize('path', CLARITY_TABLE4_FILES, ids=lambda p: p.suffix)
def test_clarity_table4_panel_b_listed_guard_skips_not_crashes(path: Path) -> None:
    """幻影列 listed: Panel B 单独守卫, 缺失时跳过该 panel 而非崩整个 do-file."""
    text = _read(path)
    listed_guard = text.find('capture confirm variable listed')
    panel_b = text.find('eststo B_listed')
    assert listed_guard != -1, f'{path} 缺 listed 守卫'
    assert panel_b != -1
    assert listed_guard < panel_b, f'{path} listed 守卫必须在 Panel B 回归之前'
    assert 'Panel B 跳过' in text
    # Panel B 回归必须落在 else 块内 (守卫与回归之间存在 else)
    else_pos = text.find('else {', listed_guard)
    assert else_pos != -1 and else_pos < panel_b, f'{path} Panel B 未包进 else 块'


# ============================================================================
# 整体一致性 — 模板与 replication code 副本内容同步 (忽略 EOL 差异)
# ============================================================================


@pytest.mark.parametrize(
    ('tmpl', 'code'),
    [
        (TABLE2_FILES[0], TABLE2_FILES[1]),
        (TABLE2_FILES[2], TABLE2_FILES[3]),
        (TABLE4_FILES[0], TABLE4_FILES[1]),
        (TABLE4_FILES[2], TABLE4_FILES[3]),
    ],
    ids=['t2-disagreement', 't2-clarity', 't4-disagreement', 't4-clarity'],
)
def test_template_and_replication_code_copy_in_sync(tmpl: Path, code: Path) -> None:
    """模板与 replication/code 实例化副本须逐行同内容 (CRLF/LF 差异除外)."""
    t = _read(tmpl).replace('\r\n', '\n')
    c = _read(code).replace('\r\n', '\n')
    assert t == c, f'{tmpl.name} 与 replication code 副本内容漂移'


def test_all_11_specs_still_load_via_registry() -> None:
    """spec 注释/literal-block 修改不得破坏 paper_registry 加载 (schema 完整性)."""
    from news_process.papers._common.paper_registry import load_all_specs

    specs = load_all_specs()
    assert len(specs) == 11
    assert specs['bank_media_disagreement'].raw['treatment']['primary'] == (
        'cross_outlet_tone_variance_full'
    )
    assert specs['bank_news_clarity'].raw['treatment']['primary'] == (
        'mean_clarity_score_full'  # full-only gating (2026-06-29): main_track _ctx→_full
    )
