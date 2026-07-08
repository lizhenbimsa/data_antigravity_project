"""WP5 gate — 税调企业双替代权源 (城市/县域网点) 构建 + 三权互验测试
(COMPANY_TAX_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-08 v4, §3 T-D14 weight 件)。

母本 = tests/test_company_bank_weight_validation.py, 裁至两 branch scheme
(贷款/银团/董监高/股东各族用例整族剔除), 保留 canon 化全族 + 分支存活/端点/预清洗族,
新增 county 族 (复合键消歧/直筒子 NaN 不回退/空键负例/placeholder 退化恒等/
字面 None 清洗/网点侧占位回退 T-D5c/双锚独立/county_key_ok 单向 + 家数锚/
(i) 类两权恒等) + branch dta 行锚 + 城县两权手算身份锚 integration 测试。

fast 部分全 mock/合成夹具不碰盘 (仅 bank_names.json/registry/税调 yaml 只读);
integration 部分 = dev 真跑锚 (读 config 权源 dta 与 03 双权产物; 读 03 长表用例带
pytest.skip 守卫)。序号前缀模块名 (03_*) 非合法 import 标识符 → spec_from_file_location
防碰撞 (与 listed 03/02 同名空间隔离)。
"""
from __future__ import annotations

import importlib
import importlib.util
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
TAX = REPO / "company_tax_bank"
sys.path.insert(0, str(TAX))  # 使税调 03 内部 importlib 税调 02 + 本文件 import_module 可达

# spec_from_file_location 防与 listed 03/02 同名空间碰撞 (T-D14 常量名/模块名隔离)
_SPEC = importlib.util.spec_from_file_location(
    "03_build_company_tax_bank_weight_validation",
    TAX / "03_build_company_tax_bank_weight_validation.py")
w8 = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = w8
_SPEC.loader.exec_module(w8)

pytestmark = pytest.mark.fast


@pytest.fixture(scope="module")
def canon():
    return w8.BankCanon()


# ---------------------------------------------------------------- DV2 canon 定向锁 (母本照搬)
def test_canon_basic(canon):
    assert canon.canon("中国工商银行股份有限公司上海市分行") == "中国工商银行"  # 分行剥离
    assert canon.canon("工商银行") == "中国工商银行"  # 前缀增删
    assert canon.canon("国家开发银行") is None  # 政策行不在 canonical 宇宙
    assert canon.canon("银行") is None  # 泛称


def test_canon_generic_three_examples(canon):
    """泛称三例 (v33 S1: 第三例是 raw 级 vs head 级的唯一判别器)。"""
    assert canon.canon("银行") is None
    assert canon.canon("银行等金融机构") is None       # ⓪ 闸即死
    assert canon.canon("银行类金融机构") is None       # head=='银行' → head 级黑名单


def test_canon_overseas_gate(canon):
    assert canon.canon("汇丰银行(越南)有限公司") is None       # 不可剥括注禁截断
    assert canon.canon("渣打银行AG") is None                    # 尾缀境外词, head 外 → 照杀
    assert canon.canon("渣打银行商人银行亚洲(投资银行)") is None  # v29 D3 逃逸例
    # 常量清单 ⊇ DV2 v29 最小必含集
    c = w8.DV2_CONSTANTS
    assert set(c["overseas_words"]) >= {"越南", "新加坡", "香港", "澳门", "台湾", "韩国", "日本",
                                        "泰国", "马来西亚", "印尼", "菲律宾", "美国", "英国", "法国",
                                        "德国", "瑞士", "荷兰", "澳大利亚", "加拿大", "亚洲", "欧洲",
                                        "国际", "海外"}
    assert set(c["foreign_suffixes"]) >= {"AG", "N.A.", "Ltd", "LTD", "BRANCH", "PLC", "S.A.",
                                          "N.V.", "Bhd", "Limited"}


def test_canon_v33_structural_pair(canon):
    """v33 S2 结构规则双例: 不可剥括注禁截断 (词表实现必红) + head 内豁免 (无豁免实现必红)。"""
    assert canon.canon("中国工商银行(莫斯科)股份公司") is None
    assert canon.canon("厦门国际银行股份有限公司北京分行") == "厦门国际银行"


def test_canon_affiliate_tail(canon):
    assert canon.canon("上海浦东发展银行村镇银行") is None  # 尾段附属黑名单
    assert canon.canon("中国银行股份有限公司信托咨询公司") is None


def test_canon_former_name_paren(canon):
    """曾用名括注 (v31 R4 救回例): '原*' 括注可剥重试。"""
    assert canon.canon("重庆市商业银行(原重庆银海租赁股份有限公司)") == "重庆银行"


def test_canon_missing_gate(canon):
    """(v32) 输入缺失闸 ⓪₀: 字面 'None' 串 → 落审计、无异常、不入 ⓪/境外闸误判。"""
    assert canon.canon("None") is None
    assert canon.canon("nan") is None
    assert canon.canon("") is None
    assert "<MISSING>" in canon.audit


def test_canon_memo_audit_replay(canon):
    """memo 缓存不吞审计: 同一未映射名两次 canon → audit 频次累计 (replay 补记)。"""
    before = canon.audit.get("国家开发银行", 0)
    canon.canon("国家开发银行")
    canon.canon("国家开发银行")
    assert canon.audit.get("国家开发银行", 0) >= before + 2


# ---------------------------------------------------------------- dtype 通则 (母本照搬)
def test_dtype_norm_recipe():
    """dtype 配方锁 (v29): '10.0'→'10' 非 '1'; 未锚定字面替换实现必红。"""
    s = pd.Series(["10.0", "1.0", "10", "None", np.nan])
    out = w8.norm(s)
    assert out.tolist() == ["10", "1", "10", "None", "nan"]
    assert w8.is_missing(pd.Series(["None", "nan", "", "1"])).tolist() == [True, True, True, False]


# ---------------------------------------------------------------- 税调 DV2 裁剪 + scheme 注册 (税调新增)
def test_dv2_constants_tax_trim():
    """T-D9 裁剪锁: 删 custodian/sanchan (shareholder 侧消费点已裁), 加 city_placeholder_branch_side
    (T-D5c 网点侧占位值集) — 9 键终集使税调 registry 哈希与 listed 永不混淆。"""
    c = w8.DV2_CONSTANTS
    assert "custodian_words" not in c and "custodian_dashes" not in c and "sanchan_words" not in c
    assert "city_placeholder_branch_side" in c
    assert set(c["city_placeholder_branch_side"]) == {"海南省直辖", "海南省直辖县级行政区",
                                                       "省直辖县级行政区划", "省直辖县级行政区"}
    assert set(c) == {"unnameable", "overseas_words", "foreign_suffixes", "generic_heads",
                      "affiliate_tail", "head_exempt_note", "city_overseas", "city_placeholder",
                      "city_placeholder_branch_side"}


def test_schemes_labels_robust_arms():
    """双 scheme 注册锁: 命名推导钉死 (§1); 双 scheme 均无稳健臂 (T-D5b)。"""
    assert w8.SCHEMES == ("branch_city", "branch_county")
    assert w8.SCHEME_LABEL_WORD == {"branch_city": "城市网点", "branch_county": "县域网点"}
    assert w8.ROBUST_ARM_COLS == {"branch_city": [], "branch_county": []}


# ---------------------------------------------------------------- 分支权 mock 夹具 (税调: prepare → yearly_counts → builder)
def branch_mock(rows):
    base = dict(HeadofficeName="中国工商银行", CityName="北京市", CountyName="东城区",
                Status=0.0, ApprovalDate="2000-01-01", QuitDate="", RunawayDate="")
    return pd.DataFrame([{**base, **r} for r in rows])


GEO = pd.DataFrame([
    {"company": "甲公司", "city": "北京", "district": "东城区"},
    {"company": "兵团公司", "city": "自治区直辖县级行政区划", "district": "石河子市"},
    {"company": "省直公司", "city": "省直辖县级行政区划", "district": "济源市"},
    {"company": "缺城公司", "city": "", "district": ""},
])


def _run_branch_city(rows, geo, y0, y1):
    canon = w8.BankCanon()
    b, _ = w8.prepare_branch_frame(branch_mock(rows), canon)
    b_city = b[b["city"] != ""]
    net_city = w8.yearly_counts(b_city[["bank", "city", "ap", "quit", "run", "status"]],
                                ["city"], y0, y1)
    keys = set(b_city["city"])
    return w8.build_weight_branch_city(geo, net_city, keys)


def build_branch_city(rows, geo=GEO, y0=2017, y1=2018):
    out, _cov = _run_branch_city(rows, geo, y0, y1)
    return out


def build_branch_county(rows, geo, y0=2017, y1=2017):
    canon = w8.BankCanon()
    b, _ = w8.prepare_branch_frame(branch_mock(rows), canon)
    b_city = b[b["city"] != ""]
    b_comp = b[(b["city"] != "") & (b["county"] != "")]  # 空键行剔除 (封死空键假匹配)
    net_city = w8.yearly_counts(b_city[["bank", "city", "ap", "quit", "run", "status"]],
                                ["city"], y0, y1)
    net_comp = w8.yearly_counts(b_comp[["bank", "city", "county", "ap", "quit", "run", "status"]],
                                ["city", "county"], y0, y1)
    ckeys = set(b_city["city"])
    compkeys = set(map(tuple, b_comp[["city", "county"]].drop_duplicates().values))
    return w8.build_weight_branch_county(geo, net_city, net_comp, ckeys, compkeys)


def test_branch_alive_boundary():
    """分支存续边界锁: Approval==t 在、Quit==t 不在。"""
    out = build_branch_city([dict(ApprovalDate="2017-06-01"),
                             dict(ApprovalDate="2000-01-01", Status=2.0, QuitDate="2017-03-01")],
                            y0=2017, y1=2017)
    m = out[(out["company"] == "甲公司") & (out["year"] == 2017)]
    assert m["w"].iloc[0] == 1  # 第二网点 quit_yr≤t 不在


def test_branch_runaway_channel():
    """失控通道锁: Status=1 ∧ runaway_yr≤t 不计存续。"""
    out = build_branch_city([dict(Status=1.0, RunawayDate="2016-01-01")], y0=2017, y1=2017)
    assert out.empty or out[out["company"] == "甲公司"].empty


def test_branch_endpoint_parse_failure_means_not_happened():
    """端点解析失败锁 (v29): QuitDate 解析失败 ∧ Status=2 → 按仍存续非剔行。
    (掺 30 行正常退出行稀释失败率至 <5%, 免触发端点失败率闸 — 闸有独立测试)"""
    rows = [dict(Status=2.0, QuitDate="不可解析", CityName="北京市")]
    rows += [dict(Status=2.0, QuitDate="2005-01-01", CityName="上海市") for _ in range(30)]
    out = build_branch_city(rows, y0=2017, y1=2017)
    assert out[(out["company"] == "甲公司")]["w"].iloc[0] == 1  # 解析失败行按"未退出"存续


def test_branch_endpoint_failure_gate():
    """端点失败率闸 (单点读表段, 城县共享): >5% → SystemExit。"""
    with pytest.raises(SystemExit):
        build_branch_city([dict(Status=2.0, QuitDate="不可解析")], y0=2017, y1=2017)


def test_branch_city_bilateral_strip():
    """城市双侧对称锁: 公司 city='北京' ∧ 分支 CityName='北京市' → 对齐。"""
    out = build_branch_city([dict(CityName="北京市")], y0=2017, y1=2017)
    assert not out[(out["company"] == "甲公司") & (out["w"] > 0)].empty


def test_branch_single_strip_regex():
    """城市单次去尾锁 (v28): '津市市'→'津市' 非 '津'; 自治州原样。"""
    geo = pd.DataFrame([{"company": "津市公司", "city": "津市市", "district": ""},
                        {"company": "湘西公司", "city": "湘西土家族苗族自治州", "district": ""}])
    out = build_branch_city([dict(CityName="津市市"), dict(CityName="湘西土家族苗族自治州")],
                            geo=geo, y0=2017, y1=2017)
    assert out[(out["company"] == "津市公司")]["w"].iloc[0] == 1
    assert out[(out["company"] == "湘西公司")]["w"].iloc[0] == 1


def test_branch_bingtuan_district_fallback():
    """兵团 district 回退锁 (v31 双串): 自治区串→石河子; 省直辖串→济源。"""
    out = build_branch_city([dict(CityName="石河子市"), dict(CityName="济源市")], y0=2017, y1=2017)
    assert out[(out["company"] == "兵团公司")]["w"].iloc[0] == 1
    assert out[(out["company"] == "省直公司")]["w"].iloc[0] == 1


def test_branch_missing_city_audit():
    """缺城市公司锁 (v29 三例): 真缺失/空串/占位∧district 缺失 → 分支权全缺失不崩。"""
    geo = pd.DataFrame([{"company": "缺1", "city": "", "district": ""},
                        {"company": "缺2", "city": "大开曼", "district": ""},
                        {"company": "缺3", "city": "省直辖县级行政区划", "district": ""}])
    out = build_branch_city([dict(CityName="北京市")], geo=geo, y0=2017, y1=2017)
    assert out.empty  # 三家全走审计通道, 无行


def test_branch_cityname_precleaning():
    """CityName 预清洗锁 (v29): 括注剥离对齐; 'null' 按缺失。"""
    geo = pd.DataFrame([{"company": "伊犁公司", "city": "伊犁哈萨克自治州", "district": ""}])
    out = build_branch_city([dict(CityName="伊犁哈萨克自治州(注:直辖)"), dict(CityName="null")],
                            geo=geo, y0=2017, y1=2017)
    assert out[(out["company"] == "伊犁公司")]["w"].iloc[0] == 1  # 'null' 行不计


def test_prepare_branch_frame_stats():
    """单点读表段: HeadofficeName→canonical 映射 + 未映射剔除 + 统计 dict 字段。"""
    canon = w8.BankCanon()
    b, stats = w8.prepare_branch_frame(branch_mock([
        dict(HeadofficeName="中国工商银行"),
        dict(HeadofficeName="国家开发银行"),      # 政策行不在 canonical → 剔
        dict(HeadofficeName="某村镇银行"),         # 尾段附属 → 剔
    ]), canon)
    assert len(b) == 1 and b["bank"].iloc[0] == "中国工商银行"
    assert stats["n_rows_raw"] == 3 and stats["n_rows_mapped"] == 1
    assert set(b.columns) == {"bank", "city", "county", "ap", "quit", "run", "status"}


# ---------------------------------------------------------------- T-D5c 网点侧占位回退 (对 listed 净新增)
def test_branch_side_city_placeholder_fallback():
    """T-D5c: 网点侧 CityName ∈ 占位值集 → 回退 CityName:=CountyName (琼中/屯昌/定安死键漏计封堵)。"""
    canon = w8.BankCanon()
    b, stats = w8.prepare_branch_frame(branch_mock([
        dict(CityName="海南省直辖", CountyName="琼中黎族苗族自治县")]), canon)
    assert stats["n_ph_side_fallback"] == 1
    assert b["city"].iloc[0] == "琼中黎族苗族自治县"   # 回退后去市尾无 '市' → 原样
    assert b["county"].iloc[0] == "琼中黎族苗族自治县"


# ---------------------------------------------------------------- 县域层 branch_county 族 (税调新增, T-D5b)
def test_county_composite_key_disambiguation():
    """复合键消歧锁: 同名区县跨市不串 (district 单键会误匹, 复合键必须消歧)。"""
    geo = pd.DataFrame([{"company": "北京朝阳公司", "city": "北京", "district": "朝阳区"},
                        {"company": "长春朝阳公司", "city": "长春", "district": "朝阳区"}])
    out, cov, key_ok = build_branch_county([dict(CityName="北京市", CountyName="朝阳区")], geo)
    assert out[out["company"] == "北京朝阳公司"]["w"].iloc[0] == 1
    assert out[out["company"] == "长春朝阳公司"].empty  # 长春朝阳区无网点 → 不因同名串到北京
    assert key_ok["北京朝阳公司"] == 1 and key_ok["长春朝阳公司"] == 0


def test_county_dash_no_city_fallback():
    """直筒子 NaN 不回退锁 (ii): district=='-' → 县权全缺失 (无行), 即便城市层有网点也不回退。"""
    geo = pd.DataFrame([{"company": "东莞公司", "city": "东莞", "district": "-"}])
    out, cov, key_ok = build_branch_county([dict(CityName="东莞市", CountyName="虎门镇")], geo)
    assert out.empty  # 城市层有 东莞 网点, 但 (ii) 通道不回退
    assert key_ok["东莞公司"] == 0 and cov["n_dash"] == 1


def test_county_empty_key_no_false_match():
    """空键互不匹配负例 (P1-4): 公司侧脏 district 清洗归空 + 网点侧 county 清洗归空 → 两侧空键禁假匹配。"""
    geo = pd.DataFrame([{"company": "空区公司", "city": "北京", "district": "None"}])
    out, cov, key_ok = build_branch_county([dict(CityName="北京市", CountyName="None")], geo)
    assert out.empty  # 空 district_norm → 不 eligible; 网点 county 清洗后被 b_comp 剔
    assert key_ok["空区公司"] == 0 and cov["n_empty_key"] == 1


def test_county_placeholder_degenerate_key_identity():
    """placeholder 键退化恒等锁 (i): city∈占位 → 走 city-level 退化键, 城/县两权对该企业逐格恒等。"""
    geo = pd.DataFrame([{"company": "省直公司", "city": "省直辖县级行政区划", "district": "济源市"}])
    rows = [dict(CityName="济源市", CountyName="济源")]
    out_city = build_branch_city(rows, geo, 2017, 2017)
    out_county, cov, key_ok = build_branch_county(rows, geo, 2017, 2017)
    a = out_city[out_city["company"] == "省直公司"].sort_values(["bank", "year"]).reset_index(drop=True)
    c = out_county[out_county["company"] == "省直公司"].sort_values(["bank", "year"]).reset_index(drop=True)
    assert not a.empty
    assert a[["company", "bank", "year", "w"]].equals(c[["company", "bank", "year", "w"]])
    assert key_ok["省直公司"] == 1
    assert cov["n_placeholder"] == 1 and cov["n_placeholder_hit"] == 1


def test_prepare_county_literal_none_and_paren_cleaning():
    """字面 'None' 清洗锁 (F3: 缺失形态是字面串 'None' 非 NaN) + 括注剥离。"""
    canon = w8.BankCanon()
    b, _ = w8.prepare_branch_frame(branch_mock([
        dict(CountyName="None"), dict(CountyName="东城区（注：X）"), dict(CountyName="")]), canon)
    assert int((b["county"] == "").sum()) == 2       # 'None' 与 '' → 空
    assert int((b["county"] == "东城区").sum()) == 1  # 剥括注 → 东城区


def test_coverage_anchor_inputs_independent_per_scheme():
    """城县双锚独立锁 (T-D6): 城市键命中 ≠ 复合键命中 → 城/县两 SystemExit 闸各读自身 hit_rate。"""
    geo = pd.DataFrame([{"company": "甲公司", "city": "北京", "district": "东城区"}])
    rows = [dict(CityName="北京市", CountyName="海淀区")]  # 城命中(北京), 县脱靶(东城区≠海淀区)
    _oc, cov_city = _run_branch_city(rows, geo, 2017, 2017)
    _oq, cov_county, _k = build_branch_county(rows, geo, 2017, 2017)
    assert cov_city["hit_rate"] == pytest.approx(1.0)     # 城市键命中 → 城锚 B 不触发
    assert cov_county["hit_rate"] == pytest.approx(0.0)   # 复合键脱靶 → 县锚 B 独立触发 (<99.5% SystemExit)


# ---------------------------------------------------------------- DV5 互验锁 (统计原语照搬母本)
def test_enrichment_hand_calc():
    """富集度小例手算 + (v33 ④) 边际保持解析式锁 (零随机)。"""
    pm = {("c1", "A"), ("c1", "B"), ("c2", "A")}
    pa = {("c1", "A"), ("c2", "A"), ("c2", "B")}
    e = w8.enrichment(pm, pa)
    # C={c1,c2}, B_m={A,B}; hit = |{(c1,A),(c2,A)}|/3 = 2/3
    assert e["hit_rate"] == pytest.approx(2 / 3)
    assert e["base_uniform"] == pytest.approx(3 / 4)
    # m_A=2,m_B=1; a_A=2,a_B=1 → Σ=2*2+1*1=5; /(|C|*|pm|)=5/6
    assert e["base_marginal"] == pytest.approx(5 / 6)
    assert e["enrich_marginal"] == pytest.approx((2 / 3) / (5 / 6))


def test_spearman_common_support_no_union_zero():
    """补 0 伪影负例: 两套零重合稀疏权 → ρ 输出 n/a (None) 而非负数。"""
    sa = pd.Series({("c1", "A"): 1.0, ("c1", "B"): 0.5})
    sb = pd.Series({("c2", "C"): 1.0})
    rho, n = w8.spearman_common(sa, sb)
    assert rho is None and n == 0


def test_spearman_undefined_rho_is_na():
    """共同支撑上任一份额向量为常数 → ρ 数学未定义, 归 None (报告呈 n/a),
    不透传 nan (透传会打出 '+nan' 且被 ρ<0 反向证据点名静默漏计)。"""
    const = pd.Series([1.0] * 12, index=range(12))
    ranked = pd.Series(np.arange(12, dtype=float), index=range(12))
    rho, n = w8.spearman_common(const, ranked)
    assert rho is None and n == 12
    rho2, n2 = w8.spearman_common(ranked, ranked)  # 正例对照: 定义良好时照常出值
    assert rho2 == pytest.approx(1.0) and n2 == 12


def test_fold_pairs_and_shares():
    """折叠对集 + 份额锁: _shares = 先窗口求和再算份额 (禁逐年份额取均值, v33 公式铁律)。"""
    w = pd.DataFrame({"company": ["c1", "c1", "c1"], "bank": ["A", "A", "B"],
                      "year": [2017, 2018, 2017], "w": [3.0, 1.0, 4.0]})
    assert w8._fold_pairs(w) == {("c1", "A"), ("c1", "B")}
    sh = w8._shares(w)
    # A: (3+1)=4, B: 4 → 各占 0.5 (先跨年求和)
    assert sh[("c1", "A")] == pytest.approx(0.5) and sh[("c1", "B")] == pytest.approx(0.5)


def test_top1_stats_hand():
    """⑤ Top-1 同银行率 / 包含率锁 (argmax, 并列取字典序首)。"""
    sa = pd.Series({("c1", "A"): 0.7, ("c1", "B"): 0.3, ("c2", "A"): 0.6, ("c2", "C"): 0.4})
    sb = pd.Series({("c1", "A"): 0.9, ("c1", "B"): 0.1, ("c2", "B"): 1.0})
    st = w8.top1_stats(sa, sb)
    # Top1: sa c1→A, c2→A; sb c1→A, c2→B; 共同 {c1,c2}; 同银行 c1 → 1/2
    assert st["n"] == 2 and st["same"] == pytest.approx(0.5)
    # 包含率: sa c1 Top1=A ∈ sb.c1 支撑{A,B} ✓; sa c2 Top1=A ∉ sb.c2 支撑{B} ✗ → 1/2
    assert st["incl_a_in_b"] == pytest.approx(0.5)


def test_codebook_idempotent(tmp_path):
    """codebook 幂等锁: 两次 section-replace 字节级一致 (成对标记显式传入, 用合成文本)。"""
    p = tmp_path / "cb.md"
    p.write_text("# codebook\n\n正文\n", encoding="utf-8")
    begin, end = "<!-- B -->", "<!-- E -->"
    w8.upsert_codebook_section(p, "## 双权章\n内容 A", begin, end)
    once = p.read_bytes()
    w8.upsert_codebook_section(p, "## 双权章\n内容 A", begin, end)
    assert p.read_bytes() == once
    w8.upsert_codebook_section(p, "## 双权章\n内容 B", begin, end)
    assert "内容 B".encode() in p.read_bytes()
    assert p.read_text(encoding="utf-8").count(begin) == 1


def test_label_scheme_word():
    """标签改写锁: 双权面板变量标签 scheme_word 驱动, 不含'共现'字样。"""
    wp1 = importlib.import_module("02_build_company_tax_bank_cooc_panel")
    lbl = wp1.make_label("cw", "n_articles", "full", "Q", scheme_word="城市网点")
    assert "共现" not in lbl and "城市网点加权" in lbl


# ---------------------------------------------------------------- 启动双锁 fail-closed (母本 SystemExit 族照搬)
def test_missing_dv2_section_systemexit(tmp_path):
    """registry 缺 dv2_constants 区段 (旧版/空占位 WP0 产物) → fail-closed SystemExit。"""
    p = tmp_path / "no_dv2.yaml"
    p.write_text("meta:\n  registry_sha256: 'x'\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="缺 dv2_constants"):
        w8.main(["--registry", str(p)])


def test_pair_missing_metadata_systemexit(tmp_path):
    """pair parquet 无内嵌 registry_sha256 metadata (非 02 正规产物) → fail-closed SystemExit。"""
    pair = tmp_path / "pairs_nometa.parquet"
    pd.DataFrame({"company": ["甲"], "bank": ["A"], "year": [2017],
                  "track": ["full"], "n_docs": [1]}).to_parquet(pair)
    with pytest.raises(SystemExit, match="缺 registry_sha256"):
        w8.main(["--pairs", str(pair)])


def test_registry_missing_systemexit(tmp_path):
    """registry 文件缺失 → 显式 SystemExit 带排障指引 (非裸 FileNotFoundError)。"""
    with pytest.raises(SystemExit, match="registry 缺失"):
        w8.main(["--registry", str(tmp_path / "nonexistent.yaml")])


def test_year_min_gt_max_systemexit():
    """年窗非法 (min>max) → SystemExit (argparse 层后置守卫)。"""
    with pytest.raises(SystemExit):
        w8.main(["--year-min", "2020", "--year-max", "2007"])


def test_weight_year_window_2011_2020():
    """v7 口径修正守卫: 03 面板年窗默认 = 税调数据可得域 2011–2020 (与 02 PANEL_YEAR 同源锚);
    argparse --year-min/--year-max 默认锚模块常量, 防未来静默回退窗口。⚠ 03 第一层脏年域
    [1990, 2035] (网点审批/退出日期合理域, 可早于 2011) 与面板年窗**无关、独立**, 不随之变。"""
    assert (w8.PANEL_YEAR_MIN, w8.PANEL_YEAR_MAX) == (2011, 2020), "03 面板年窗须 = 2011–2020"
    assert w8.PANEL_YEAR_MAX - w8.PANEL_YEAR_MIN + 1 == 10


# ---------------------------------------------------------------- integration: dev 真跑锚
@pytest.mark.integration
def test_branch_dta_row_anchors():
    """branch 权源 dta 行锚 (税调唯一权源不可零锚; 翻红即数据商改版信号, 先查改版而非放松)。"""
    import pyreadstat
    raw, _ = pyreadstat.read_dta(str(w8.BRANCH_DTA), usecols=["Status", "CountyName"])
    assert len(raw) == 603907
    st = w8.norm(raw["Status"])
    assert {k: int((st == k).sum()) for k in ("0", "2", "1")} == {"0": 550359, "2": 51185, "1": 2363}
    # F3: CountyName 缺失形态是字面字符串 'None' (非 NaN) — 照搬 isna 判空会漏
    assert int((raw["CountyName"].astype(str) == "None").sum()) == 3168


def _skip_if_no_altweights():
    for scheme in w8.SCHEMES:
        if not (w8.OUT_DATA / f"_company_tax_bank_altweights_{scheme}.parquet").exists():
            pytest.skip("WP5 双权长表未落盘 (先跑 company_tax_bank/03_*)")


@pytest.mark.integration
def test_city_county_hand_calc_identity_anchors():
    """城县两权手算身份锚各一 (镜像 listed test:527): 从权源 dta 手算某 (company,bank,year)
    的存续网点数, 与双权长表对应格 isclose (同构 schema 错绑时唯身份锚必红)。"""
    _skip_if_no_altweights()
    import pyreadstat
    canon = w8.BankCanon()
    _, geo = w8.load_companies()
    geo_by = geo.set_index("company")
    raw, _ = pyreadstat.read_dta(str(w8.BRANCH_DTA), usecols=w8.DTA_USECOLS)
    b, _ = w8.prepare_branch_frame(raw, canon)

    def alive_at(sub, t):
        return (sub["ap"].notna() & (sub["ap"] <= t)
                & ~((sub["status"] == "2") & sub["quit"].notna() & (sub["quit"] <= t))
                & ~((sub["status"] == "1") & sub["run"].notna() & (sub["run"] <= t)))

    ph = set(geo[geo["city"].isin(w8.DV2_CONSTANTS["city_placeholder"])]["company"])

    # 城权身份锚: city 长表确定性首行 → 手算 (city_key, bank) 存续网点数
    city_lt = (pd.read_parquet(w8.OUT_DATA / "_company_tax_bank_altweights_branch_city.parquet")
               .sort_values(["company", "bank", "year"]).reset_index(drop=True))
    pc = city_lt.iloc[0]
    grow = geo_by.loc[pc["company"]]
    ck = grow["district"] if grow["city"] in w8.DV2_CONSTANTS["city_placeholder"] else grow["city"]
    ck = re.sub(r"市$", "", ck)
    sub = b[(b["bank"] == pc["bank"]) & (b["city"] == ck)]
    assert int(alive_at(sub, int(pc["year"])).sum()) == pc["w"], "城权身份锚失配 (疑错绑/存续判定漂移)"

    # 县权身份锚: county 长表首个非占位企业 → 手算 (city_key, county_norm, bank) 存续网点数
    county_lt = (pd.read_parquet(w8.OUT_DATA / "_company_tax_bank_altweights_branch_county.parquet")
                 .sort_values(["company", "bank", "year"]).reset_index(drop=True))
    normal = county_lt[~county_lt["company"].isin(ph)]
    pk = normal.iloc[0]
    grow2 = geo_by.loc[pk["company"]]
    ck2 = re.sub(r"市$", "", grow2["city"])
    dn2 = w8.PAREN_RE.sub("", grow2["district"]).strip()
    sub2 = b[(b["bank"] == pk["bank"]) & (b["city"] == ck2) & (b["county"] == dn2)]
    assert int(alive_at(sub2, int(pk["year"])).sum()) == pk["w"], "县权身份锚失配 (复合键存续判定漂移)"


@pytest.mark.integration
def test_placeholder_companies_city_county_identity():
    """(i) 类两权长表逐 (bank,year) 恒等: 144 家省直辖占位企业城/县两权向量逐格精确相等
    (T-D5b(i) 构造保证 — net_city 同表同式 merge; city×county Spearman 因此按企业整体剔除)。"""
    _skip_if_no_altweights()
    _, geo = w8.load_companies()
    ph = set(geo[geo["city"].isin(w8.DV2_CONSTANTS["city_placeholder"])]["company"])
    assert len(ph) == 144  # F4② 占位企业 (省/自治区直辖县级行政区划)
    city_lt = pd.read_parquet(w8.OUT_DATA / "_company_tax_bank_altweights_branch_city.parquet")
    county_lt = pd.read_parquet(w8.OUT_DATA / "_company_tax_bank_altweights_branch_county.parquet")
    a = (city_lt[city_lt["company"].isin(ph)]
         .sort_values(["company", "bank", "year"]).reset_index(drop=True))
    c = (county_lt[county_lt["company"].isin(ph)]
         .sort_values(["company", "bank", "year"]).reset_index(drop=True))
    assert not a.empty
    assert a[["company", "bank", "year", "w"]].equals(c[["company", "bank", "year", "w"]])


@pytest.mark.integration
def test_county_key_ok_unidirectional_and_count():
    """county_key_ok 单向断言 (T-D5b, 禁双向): key_ok==0 ⇒ 县权全缺失 (rel_n_banks≡0);
    + key_ok==0 家数运行时锚 (实测 971 = 直筒子/零星 922 + 开发区等残差)。"""
    p = w8.OUT_DATA / "company_tax_bank_branch_countyw_panel.parquet"
    if not p.exists():
        pytest.skip("WP5 县权面板未落盘 (先跑 company_tax_bank/03_*)")
    df = pd.read_parquet(p, columns=["company_tax_name", "county_key_ok", "rel_n_banks"])
    # 单向: ==0 ⇒ 县权全缺失 (但 ==1 且全缺失是合法真零形态, 禁反向断言)
    assert (df.loc[df["county_key_ok"] == 0, "rel_n_banks"] == 0).all()
    assert df[df["county_key_ok"] == 0]["company_tax_name"].nunique() == 971


@pytest.mark.integration
def test_city_county_spearman_excludes_identity():
    """city×county 份额 Spearman 剔恒等企业: 占位 144 家两权向量逐格恒等 (ρ 抬高伪影),
    按企业整体剔除后 ρ 仍高 (跨粒度收敛效度真信号)。锚 = 互验报告 ③ 行 (+0.899 / n=945447)。

    ⚠ v7 窗口修正 (2011–2020) 相关: n/ρ 是 `_shares` 跨窗内年求和产物 → **随年窗收窄而变**;
    当前锚 (945447 / 0.899) 读的是**旧 19 年窗盘上产物**, 与陈旧 on-disk 一致故此刻正确。
    03 按 2011–2020 重跑双权长表后须同步 bump 此二 assert + 上行 docstring 数字 (计划 §9 v7
    DEFERRED 已登记)。同族 :537 `county_key_ok==0 nunique==971` 是**企业级、窗无关, 勿误 bump**。"""
    _skip_if_no_altweights()
    _, geo = w8.load_companies()
    ph = set(geo[geo["city"].isin(w8.DV2_CONSTANTS["city_placeholder"])]["company"])
    city_lt = pd.read_parquet(w8.OUT_DATA / "_company_tax_bank_altweights_branch_city.parquet")
    county_lt = pd.read_parquet(w8.OUT_DATA / "_company_tax_bank_altweights_branch_county.parquet")
    sc = w8._shares(city_lt[~city_lt["company"].isin(ph)])
    sq = w8._shares(county_lt[~county_lt["company"].isin(ph)])
    rho, n = w8.spearman_common(sc, sq)
    assert n == 945447
    assert rho == pytest.approx(0.899, abs=0.01)


@pytest.mark.integration
def test_usci_output_dtype_str18_in_products():
    """T-D14 输出侧 usci str18 契约 (计划 §T-D14 'dta 读回 dtype 仍字符串'; R1 P2-5 补覆盖缺口):
    产物面板 usci 列须为字符串 dtype、逐值 len==18 非空 — 防写盘回归把含尾字母 usci 静默转数值
    致 usci×year 主键损坏而 gate 全绿 (输入 yaml SSOT 完好)。读产物, 缺则 skip。"""
    pq = w8.OUT_DATA / "company_tax_bank_cooc_panel.parquet"
    dta = w8.OUT_DATA / "company_tax_bank_cooc_panel.dta"
    if not pq.exists():
        pytest.skip("WP1 主面板未落盘 (先跑 company_tax_bank/02_*)")
    s = pd.read_parquet(pq, columns=["usci"])["usci"]
    assert s.dtype == object, f"parquet usci dtype 应为 object(字符串), 实为 {s.dtype} — 疑写盘静默转数值"
    assert s.notna().all() and (s.astype(str).str.len() == 18).all(), "usci 须全非空且逐值 18 位"
    if dta.exists():
        import pyreadstat
        _, meta = pyreadstat.read_dta(str(dta), metadataonly=True)
        vt = meta.readstat_variable_types.get("usci")
        assert vt == "string", f"dta 读回 usci 类型应为 string, 实为 {vt} — 防 str18 主键被强转数值"
