"""DV6 — 七替代权源 gate + 测试 (COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN v34)。

fast 部分全 mock 不碰盘 (仅 bank_names.json/registry 只读); integration 部分 = dev 真跑锚
(行数锚/身份实弹锚, 读 config dta 与 company_listed_bank/data 产物)。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "company_listed_bank"))

# 序号前缀模块名 (03_*) 非合法 import 语句标识符 → 走 importlib
import importlib  # noqa: E402

w8 = importlib.import_module("03_build_company_bank_weight_validation")

pytestmark = pytest.mark.fast


@pytest.fixture(scope="module")
def canon():
    return w8.BankCanon()


# ---------------------------------------------------------------- DV2 canon 定向锁
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


# ---------------------------------------------------------------- dtype 通则
def test_dtype_norm_recipe():
    """dtype 配方锁 (v29): '10.0'→'10' 非 '1'; 未锚定字面替换实现必红。"""
    s = pd.Series(["10.0", "1.0", "10", "None", np.nan])
    out = w8.norm(s)
    assert out.tolist() == ["10", "1", "10", "None", "nan"]
    assert w8.is_missing(pd.Series(["None", "nan", "", "1"])).tolist() == [True, True, True, False]


# ---------------------------------------------------------------- 贷款权 mock 锁
def loan_mock(rows: list[dict]) -> pd.DataFrame:
    base = dict(Symbol="000001", EventID=None, RelateToLoanCompanyCode="P7514", IsBankGroup="0",
                LoanBank="中国工商银行", IsSign="1", IsTermination="0", SignDate="",
                CurrencyCode="CNY", MaxLoan=100.0, LoanTerm=np.nan, LoanStarDate="2010-01-01",
                LoanEndDate="", DeclareDate="", LoanProcess="5")
    out = []
    for i, r in enumerate(rows):
        d = dict(base)
        d.update(r)
        d["EventID"] = i
        out.append(d)
    return pd.DataFrame(out)


COMPANIES = {"000001": "甲公司", "000002": "乙公司"}


def build_loan(rows, y0=2007, y1=2025):
    canon = w8.BankCanon()
    return w8.build_weight_loan(loan_mock(rows), canon, COMPANIES, y0, y1, check_anchors=False), canon


def test_loan_duration_expansion():
    """存续展开锁 (v28): y0=2010, LoanTerm=3 → 恰闭区间 {2010..2013} 4 年 (单位=年方向)。"""
    out, _ = build_loan([dict(LoanStarDate="2010-06-01", LoanTerm=3.0)])
    assert sorted(out["year"]) == [2010, 2011, 2012, 2013]
    assert (out["w"] == 100.0).all()


def test_loan_y1_guard():
    """y1 守卫锁: LoanEndDate < 起始年 → y1:=y0 单年。"""
    out, _ = build_loan([dict(LoanStarDate="2015-01-01", LoanEndDate="2010-01-01")])
    assert sorted(out["year"]) == [2015]


def test_loan_end_date_empty_fallback():
    """LoanEndDate 空串锁: 走 LoanTerm 回退而非解析异常。"""
    out, _ = build_loan([dict(LoanStarDate="2012-01-01", LoanEndDate="", LoanTerm=1.0)])
    assert sorted(out["year"]) == [2012, 2013]


def test_loan_date_three_level_fallback():
    """借款日期三级回退锁: LoanStar 缺 → Sign 缺 → DeclareDate。"""
    out, _ = build_loan([dict(LoanStarDate="", SignDate="", DeclareDate="2014-05-01", LoanTerm=0.5)])
    assert 2014 in set(out["year"])


def test_loan_p7501_excluded():
    """关系代码锁: P7501 母公司行不计。"""
    out, _ = build_loan([dict(RelateToLoanCompanyCode="P7501")])
    assert len(out) == 0


def test_loan_w_own_semantics():
    """w_own 语义锁 (v28/v33): 同组 P7514+P7502 → w=和, w_own=仅 P7514; 全 P7502 → w_own==0;
    组内含缺 MaxLoan 的 P7514 → w_own=NaN。"""
    out, _ = build_loan([
        dict(RelateToLoanCompanyCode="P7514", MaxLoan=100.0, LoanBank="中国工商银行"),
        dict(RelateToLoanCompanyCode="P7502", MaxLoan=50.0, LoanBank="中国工商银行"),
        dict(RelateToLoanCompanyCode="P7502", MaxLoan=70.0, LoanBank="中国建设银行"),
        dict(RelateToLoanCompanyCode="P7514", MaxLoan=np.nan, LoanBank="中国农业银行"),
    ])
    icbc = out[out["bank"] == "中国工商银行"].iloc[0]
    assert icbc["w"] == 150.0 and icbc["w_own"] == 100.0
    ccb = out[out["bank"] == "中国建设银行"].iloc[0]
    assert ccb["w_own"] == 0.0  # 无 P7514 → 真零, 行保留
    abc = out[out["bank"] == "中国农业银行"].iloc[0]
    assert np.isnan(abc["w_own"]) and np.isnan(abc["w"])  # 有 P7514 但金额缺 → NaN


def test_loan_group_all_missing_amount():
    """金额臂组级全缺锁 (v31): 长表行在·w=NaN·w_cnt 有值。"""
    out, _ = build_loan([dict(MaxLoan=np.nan)])
    assert len(out) == 1
    assert np.isnan(out["w"].iloc[0]) and out["w_cnt"].iloc[0] == 1.0


def test_loan_non_cny_excluded_from_amount():
    """canonical 金额臂限 CNY; 计数臂全币种。"""
    out, _ = build_loan([dict(CurrencyCode="USD", MaxLoan=100.0)])
    assert np.isnan(out["w"].iloc[0]) and out["w_cnt"].iloc[0] == 1.0


def test_loan_w_dur_arm():
    """w_dur 第四臂 (v33 J1): 仅期限可观测事件入; 单年回退事件 NaN。"""
    out, _ = build_loan([dict(LoanStarDate="2010-01-01", LoanEndDate="", LoanTerm=np.nan,
                              SignDate="", DeclareDate="2010-01-01")])
    assert np.isnan(out["w_dur"].iloc[0]) and out["w"].iloc[0] == 100.0
    out2, _ = build_loan([dict(LoanStarDate="2010-01-01", LoanTerm=1.0)])
    assert (out2["w_dur"] == 100.0).all()


def test_loan_cross_window_expansion():
    """跨窗展开锁 (v31): y0=2024·Term=3 → 窗内 2024–2025 保留、2026–2027 INFO 裁剪。"""
    out, _ = build_loan([dict(LoanStarDate="2024-01-01", LoanTerm=3.0)])
    assert sorted(out["year"]) == [2024, 2025]


# ---------------------------------------------------------------- 银团锁批
def test_syndicate_split_two():
    """v29 三 mock: 拆 2 行金额各半 / 列举尾缀剥后 k=2 / 剥牵头 k=2。"""
    out, _ = build_loan([dict(IsBankGroup="1", LoanBank="中国工商银行、中国建设银行", MaxLoan=100.0)])
    assert len(out) == 2 and np.isclose(out["w"], 50.0).all()
    out2, _ = build_loan([dict(IsBankGroup="1", LoanBank="中国工商银行、中国建设银行等金融机构",
                               MaxLoan=100.0)])
    assert len(out2) == 2 and np.isclose(out2["w"], 50.0).all()
    out3, _ = build_loan([dict(IsBankGroup="1", LoanBank="中国工商银行牵头,中国建设银行",
                               MaxLoan=100.0)])
    assert len(out3) == 2


def test_syndicate_no_delim_dropped():
    """无分隔符 '…牵头的银团' → 整笔 ⓪ 剔除。"""
    out, canon = build_loan([dict(IsBankGroup="1", LoanBank="工商银行牵头的银团", MaxLoan=100.0)])
    assert len(out) == 0


def test_syndicate_k0_audit_no_zerodiv():
    """(v30) k=0 mock: 成员全部映射失败 → 整笔落审计、无除零异常。"""
    out, canon = build_loan([dict(IsBankGroup="1", LoanBank="花旗东京、汇丰伦敦分社", MaxLoan=100.0)])
    assert len(out) == 0
    assert any("k=0" in x for x in getattr(canon, "audit_extra", []))


def test_syndicate_paren_balance_k3():
    """(v33 ①) 括注平衡 mock → k=3 (v31 字面先拆实现必红; v34 第四则剥 其中/为)。"""
    out, _ = build_loan([dict(IsBankGroup="1", MaxLoan=90.0,
                              LoanBank="银团(其中中国工商银行为牵头行,中国建设银行,昆仑银行)")])
    assert set(out["bank"]) == {"中国工商银行", "中国建设银行", "昆仑银行"}
    assert np.isclose(out["w"], 30.0).all()


def test_syndicate_duplicate_member_k2():
    """(v33 ②) 重复成员 mock → k=2、金额各半 (canonical 去重锁)。"""
    out, _ = build_loan([dict(IsBankGroup="1", MaxLoan=100.0,
                              LoanBank="中国工商银行、中国工商银行、中国建设银行")])
    assert len(out) == 2 and np.isclose(out["w"], 50.0).all()


def test_syndicate_conjunction_audit():
    """(v33 ③) 连接词 mock: 单成员串双行名 → 落审计非静默单映射。"""
    out, canon = build_loan([dict(IsBankGroup="1", MaxLoan=100.0,
                                  LoanBank="交通银行、外星银行和未知银行")])
    assert any("连接词" in x for x in getattr(canon, "audit_extra", []))


def test_syndicate_w_own():
    """w_own 银团锁 (v29): P7514 银团行 MaxLoan/k 计入 w_own; 全 P7502 银团组 w_own==0。"""
    out, _ = build_loan([dict(IsBankGroup="1", RelateToLoanCompanyCode="P7514",
                              LoanBank="中国工商银行、中国建设银行", MaxLoan=100.0)])
    assert np.isclose(out["w_own"], 50.0).all()
    out2, _ = build_loan([dict(IsBankGroup="1", RelateToLoanCompanyCode="P7502",
                               LoanBank="中国工商银行、中国建设银行", MaxLoan=100.0)])
    assert (out2["w_own"] == 0.0).all()


def test_syndicate_lead_flag():
    """ⓕ (v33 J1) 牵头行 lead 身份在拆分层被记录 (剥'牵头'前)。"""
    members = w8._syndicate_split("银团(其中中国工商银行为牵头行,中国建设银行)")
    d = dict(members)
    assert d.get("中国工商银行") is True
    assert d.get("中国建设银行") is False


# ---------------------------------------------------------------- 分支权 mock 锁
def branch_mock(rows):
    base = dict(HeadofficeName="中国工商银行", CityName="北京市", Status=0.0,
                ApprovalDate="2000-01-01", QuitDate="", RunawayDate="")
    return pd.DataFrame([{**base, **r} for r in rows])


GEO = pd.DataFrame([
    {"company": "甲公司", "city": "北京", "district": "东城区"},
    {"company": "兵团公司", "city": "自治区直辖县级行政区划", "district": "石河子市"},
    {"company": "省直公司", "city": "省直辖县级行政区划", "district": "济源市"},
    {"company": "缺城公司", "city": "", "district": ""},
])


def build_branch(rows, geo=GEO, y0=2017, y1=2018):
    canon = w8.BankCanon()
    return w8.build_weight_branch(branch_mock(rows), canon, geo, y0, y1)


def test_branch_alive_boundary():
    """分支存续边界锁: Approval==t 在、Quit==t 不在。"""
    out = build_branch([dict(ApprovalDate="2017-06-01"),
                        dict(ApprovalDate="2000-01-01", Status=2.0, QuitDate="2017-03-01")],
                       y0=2017, y1=2017)
    m = out[(out["company"] == "甲公司") & (out["year"] == 2017)]
    assert m["w"].iloc[0] == 1  # 第二网点 quit_yr≤t 不在


def test_branch_runaway_channel():
    """失控通道锁: Status=1 ∧ runaway_yr≤t 不计存续。"""
    out = build_branch([dict(Status=1.0, RunawayDate="2016-01-01")], y0=2017, y1=2017)
    assert out.empty or out[out["company"] == "甲公司"].empty


def test_branch_endpoint_parse_failure_means_not_happened():
    """端点解析失败锁 (v29): QuitDate 解析失败 ∧ Status=2 → 按仍存续非剔行。
    (掺 30 行正常退出行稀释失败率至 <5%, 免触发 v33 J2 端点失败率闸 — 闸有独立测试)"""
    rows = [dict(Status=2.0, QuitDate="不可解析", CityName="北京市")]
    rows += [dict(Status=2.0, QuitDate="2005-01-01", CityName="上海市") for _ in range(30)]
    out = build_branch(rows, y0=2017, y1=2017)
    assert out[(out["company"] == "甲公司")]["w"].iloc[0] == 1  # 解析失败行按"未退出"存续


def test_branch_endpoint_failure_gate():
    """(v33 J2) 端点失败率闸: >5% → SystemExit。"""
    with pytest.raises(SystemExit):
        build_branch([dict(Status=2.0, QuitDate="不可解析")], y0=2017, y1=2017)


def test_branch_city_bilateral_strip():
    """城市双侧对称锁: 公司 city='北京' ∧ 分支 CityName='北京市' → 对齐。"""
    out = build_branch([dict(CityName="北京市")], y0=2017, y1=2017)
    assert not out[(out["company"] == "甲公司") & (out["w"] > 0)].empty


def test_branch_single_strip_regex():
    """城市单次去尾锁 (v28): '津市市'→'津市' 非 '津'; 自治州原样。"""
    geo = pd.DataFrame([{"company": "津市公司", "city": "津市市", "district": ""},
                        {"company": "湘西公司", "city": "湘西土家族苗族自治州", "district": ""}])
    out = build_branch([dict(CityName="津市市"), dict(CityName="湘西土家族苗族自治州")],
                       geo=geo, y0=2017, y1=2017)
    assert out[(out["company"] == "津市公司")]["w"].iloc[0] == 1
    assert out[(out["company"] == "湘西公司")]["w"].iloc[0] == 1


def test_branch_bingtuan_district_fallback():
    """兵团 district 回退锁 (v31 双串): 自治区串→石河子; 省直辖串→济源。"""
    out = build_branch([dict(CityName="石河子市"), dict(CityName="济源市")], y0=2017, y1=2017)
    assert out[(out["company"] == "兵团公司")]["w"].iloc[0] == 1
    assert out[(out["company"] == "省直公司")]["w"].iloc[0] == 1


def test_branch_missing_city_audit():
    """缺城市公司锁 (v29 三例): 真缺失/空串/占位∧district 缺失 → 分支权全缺失不崩。"""
    geo = pd.DataFrame([{"company": "缺1", "city": "", "district": ""},
                        {"company": "缺2", "city": "大开曼", "district": ""},
                        {"company": "缺3", "city": "省直辖县级行政区划", "district": ""}])
    out = build_branch([dict(CityName="北京市")], geo=geo, y0=2017, y1=2017)
    assert out.empty  # 三家全走审计通道, 无行


def test_branch_cityname_precleaning():
    """CityName 预清洗锁 (v29): 括注剥离对齐; 'null' 按缺失。"""
    geo = pd.DataFrame([{"company": "伊犁公司", "city": "伊犁哈萨克自治州", "district": ""}])
    out = build_branch([dict(CityName="伊犁哈萨克自治州(注:直辖)"), dict(CityName="null")],
                       geo=geo, y0=2017, y1=2017)
    assert out[(out["company"] == "伊犁公司")]["w"].iloc[0] == 1  # 'null' 行不计


# ---------------------------------------------------------------- 董监高 mock 锁
def board_mock(rows):
    base = dict(Symbol="000001", EndDate="2017-12-31", PersonID="P1", SpecificPosition="董事",
                IsExsacutive="0", ServInstitution="中国工商银行", FinInstitutionTypeCode="S8003",
                ServiceStatus=1.0)
    return pd.DataFrame([{**base, **r} for r in rows])


def build_board(rows, y0=2007, y1=2025):
    canon = w8.BankCanon()
    return w8.build_board_family(board_mock(rows), canon, COMPANIES, y0, y1, check_anchors=False)


def test_position_three_way():
    """职务三分类锁: 董事长→董事臂; 职工监事→监事臂; 双含→监事臂。"""
    fam = build_board([dict(SpecificPosition="董事长", PersonID="A"),
                       dict(SpecificPosition="职工监事", PersonID="B"),
                       dict(SpecificPosition="董事兼监事", PersonID="C")])
    assert fam["board"]["w"].sum() == 1   # 仅 A
    assert fam["supervisor"]["w"].sum() == 2  # B + C
    assert fam["dsg"]["w"].sum() == 3


def test_personid_dedup():
    """PersonID 去重锁 (v31): 同人同年同机构双职务两行 → w=1 (size 误代 nunique 必红)。"""
    fam = build_board([dict(PersonID="X", SpecificPosition="董事"),
                       dict(PersonID="X", SpecificPosition="董事长")])
    assert fam["board"]["w"].iloc[0] == 1.0


def test_canonical_arm_no_servicestatus_filter():
    """canonical 臂不过滤锁 (v29): ServiceStatus=NaN 与 '3' 行 → canonical 计入、strict 不计。"""
    fam = build_board([dict(PersonID="A", ServiceStatus=np.nan),
                       dict(PersonID="B", ServiceStatus=3.0),
                       dict(PersonID="C", ServiceStatus=1.0)])
    b = fam["board"]
    assert b["w"].iloc[0] == 3.0
    assert b["w_strict"].iloc[0] == 1.0


def test_servinstitution_source_col():
    """ServInstitution 源列锁 (v28): FullName 塞银行名、ServInstitution 塞非银名 → 不入权。"""
    df = board_mock([dict(ServInstitution="某某科技公司")])
    df["FullName"] = "中国工商银行"
    canon = w8.BankCanon()
    fam = w8.build_board_family(df, canon, COMPANIES, 2007, 2025, check_anchors=False)
    assert fam["dsg"].empty


def test_strict_arm_carrier_all_four():
    """稳健臂载体锁 (v33): 四张董监高长表各有 w_strict; 贷款有 w_cnt/w_own/w_dur。"""
    fam = build_board([dict()])
    for k in ("board", "supervisor", "exec", "dsg"):
        assert "w_strict" in fam[k].columns
    out, _ = build_loan([dict()])
    for c in ("w_cnt", "w_own", "w_dur"):
        assert c in out.columns


# ---------------------------------------------------------------- 股东 mock 锁
def sh_mock(rows):
    base = dict(Stkcd="000001", Reptdt="2017-12-31", S0301a="中国工商银行",
                S0304a=5.0, CategoryID="P2202")
    return pd.DataFrame([{**base, **r} for r in rows])


def build_sh(rows, y0=2007, y1=2025):
    canon = w8.BankCanon()
    return w8.build_weight_shareholder(sh_mock(rows), canon, COMPANIES, y0, y1,
                                       check_anchors=False)


def test_shareholder_custodian_gate():
    """托管剔除锁: 'X基金-Y银行-Z计划' 不入股东权。"""
    out = build_sh([dict(S0301a="华夏基金-工商银行-理财计划", CategoryID="P2239")])
    assert out.empty


def test_shareholder_snapshot_latest():
    """股东年末快照锁 (v29 双 mock + v31 第三 mock 两宇宙判别)。"""
    # mock1: 同年两报告期同一银行 → 取最晚 Reptdt 份额
    out = build_sh([dict(Reptdt="2017-06-30", S0304a=9.0), dict(Reptdt="2017-12-31", S0304a=5.0)])
    assert out["w"].iloc[0] == 5.0
    # mock2: 银行只在较早期、缺席最晚期 → 不纳
    out2 = build_sh([dict(Reptdt="2017-06-30", S0304a=9.0),
                     dict(Reptdt="2017-12-31", S0301a="某某实业公司", S0304a=3.0, CategoryID="P2239")])
    assert out2.empty
    # mock3 (v31 R4 唯一判别器): 12-31 期存在但只含非银行行 → 该 (c,t) 不纳
    out3 = build_sh([dict(Reptdt="2017-06-30", S0304a=9.0, CategoryID="P2202"),
                     dict(Reptdt="2017-12-31", S0301a="自然人张三", S0304a=3.0, CategoryID="P2239")])
    assert out3.empty


def test_shareholder_third_channel_bidirectional():
    """股东第三通道锁 (v29 双向): P2239+可映射真银行→纳; 工会三产→不纳; P2201→不纳。"""
    out = build_sh([dict(S0301a="兴业银行深圳分行", CategoryID="P2239", S0304a=2.0)])
    assert len(out) == 1 and out["bank"].iloc[0] == "兴业银行"
    out2 = build_sh([dict(S0301a="中国农业银行上海分行机关工会委员会", CategoryID="P2239")])
    assert out2.empty
    out3 = build_sh([dict(S0301a="花旗银行", CategoryID="P2201")])
    assert out3.empty


def test_shareholder_canonical_fold_sum():
    """(v33 ①) 折叠锁: 同 (c,t) 最晚期 'X银行A分行' 3% + 'X银行' 5% → w=8 (sum 算子)。"""
    out = build_sh([dict(S0301a="中国工商银行北京分行", S0304a=3.0),
                    dict(S0301a="中国工商银行", S0304a=5.0)])
    assert len(out) == 1
    assert out["w"].iloc[0] == pytest.approx(8.0)


# ---------------------------------------------------------------- DV5 互验锁
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


def test_codebook_idempotent(tmp_path):
    """(v33 ③) codebook 幂等锁: 两次 section-replace 字节级一致。"""
    p = tmp_path / "cb.md"
    p.write_text("# codebook\n\n正文\n", encoding="utf-8")
    w8.upsert_codebook_section(p, "## 七权章\n内容 A")
    once = p.read_bytes()
    w8.upsert_codebook_section(p, "## 七权章\n内容 A")
    assert p.read_bytes() == once
    w8.upsert_codebook_section(p, "## 七权章\n内容 B")
    assert b"\xe5\x86\x85\xe5\xae\xb9 B" in p.read_bytes()
    assert p.read_text(encoding="utf-8").count("BEGIN") == 1


def test_label_scheme_word():
    """标签改写锁: 贷款面板变量标签不含'共现'字样。"""
    wp1 = importlib.import_module("02_build_company_bank_cooc_panel")
    lbl = wp1.make_label("cw", "n_articles", "full", "Q", scheme_word="贷款")
    assert "共现" not in lbl and "贷款加权" in lbl


# ---------------------------------------------------------------- integration: dev 真跑锚
@pytest.mark.integration
def test_row_anchors_real_dta():
    """行数锚 (v27/v29/v30/v31, 精确等值, 翻红即数据商改版信号)。"""
    import pyreadstat
    loan, _ = pyreadstat.read_dta(str(w8.DTA_FILES["loan"]),
                                  usecols=["IsSign", "IsTermination", "RelateToLoanCompanyCode",
                                           "CurrencyCode", "EventID"])
    assert len(loan) == 263015 and loan["EventID"].nunique() == 263015
    assert int((w8.norm(loan["IsSign"]) == "1").sum()) == 14929
    f = loan[w8.norm(loan["IsSign"]) == "1"]
    f = f[w8.norm(f["IsTermination"]) != "1"]
    f = f[f["RelateToLoanCompanyCode"].isin(["P7514", "P7502"])]
    assert int((w8.norm(f["CurrencyCode"]) == "CNY").sum()) == 14127
    board, _ = pyreadstat.read_dta(str(w8.DTA_FILES["board"]),
                                   usecols=["FinInstitutionTypeCode", "IsExsacutive", "ServiceStatus"])
    b = board[board["FinInstitutionTypeCode"].isin(["S8002", "S8003"])]
    assert len(b) == 139753
    assert int((w8.norm(b["IsExsacutive"]) == "1").sum()) == 64263
    assert int((w8.norm(b["ServiceStatus"]) == "1").sum()) == 27974
    sh, _ = pyreadstat.read_dta(str(w8.DTA_FILES["shareholder"]), usecols=["CategoryID"])
    assert len(sh) == 2442278
    assert int((sh["CategoryID"] == "P2202").sum()) == 4822


@pytest.mark.integration
def test_identity_anchors_seven_panels():
    """(v33 ④) 七面板身份实弹锚: 每权源从原始 dta 手算已知 (c,b,t) 的 w, 断言恰落对应文件名
    的长表中 (同构 schema 批量 zip 错绑时唯身份锚必红)。"""
    got = {}
    for scheme in w8.SCHEMES:
        p = w8.OUT_DATA / f"_company_bank_altweights_{scheme}.parquet"
        if not p.exists():
            pytest.skip("WP5 长表未落盘 (先跑 company_listed_bank/03_build_company_bank_weight_validation.py)")
        got[scheme] = pd.read_parquet(p)
    # 贷款: 从原始 dta 手算首个 CNY 非银团可映射事件
    canon = w8.BankCanon()
    import pyreadstat
    loan, _ = pyreadstat.read_dta(str(w8.DTA_FILES["loan"]), usecols=w8.DTA_USECOLS["loan"])
    lt = w8.build_weight_loan(loan, canon, dict(_load_code_map()), 2007, 2025)
    probe = lt.dropna(subset=["w"]).iloc[0]
    m = got["loan"]
    hit = m[(m["company"] == probe["company"]) & (m["bank"] == probe["bank"])
            & (m["year"] == probe["year"])]
    assert len(hit) == 1 and np.isclose(hit["w"].iloc[0], probe["w"]), "贷款身份锚失配 (疑错绑)"
    # 各权源 schema 载体区分 (身份互斥的快速证据): 稳健臂列集不同
    assert {"w_cnt", "w_own", "w_dur"} <= set(got["loan"].columns)
    assert "w_strict" in got["dsg"].columns and "w_strict" not in got["branch"].columns
    assert set(got["shareholder"].columns) == {"company", "bank", "year", "w"}


def _load_code_map():
    import yaml
    comp = yaml.safe_load((w8.CONFIG / "company_listed_names.yaml").read_text(encoding="utf-8"))
    return {str(c["stock_code"]).zfill(6): c["company_listed_name"] for c in comp["companies"]}


# ---------------------------------------------------------------- 启动双锁 fail-closed + ③ ρ 未定义口径 (2026-07-07)
def test_missing_dv2_section_systemexit(tmp_path):
    """registry 缺 dv2_constants 区段 (旧版/空占位 WP0 产物) → fail-closed
    (此前 `if reg_dv2 and ...` 静默放行, 与头部日志"缺/stale 即 SystemExit"承诺相悖)。"""
    p = tmp_path / "no_dv2.yaml"
    p.write_text("meta:\n  registry_sha256: 'x'\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="缺 dv2_constants"):
        w8.main(["--registry", str(p)])


def test_pair_missing_metadata_systemexit(tmp_path):
    """pair parquet 无内嵌 registry_sha256 metadata (非 02 正规产物) → fail-closed。"""
    pair = tmp_path / "pairs_nometa.parquet"
    pd.DataFrame({"company": ["甲"], "bank": ["A"], "year": [2017],
                  "track": ["full"], "n_docs": [1]}).to_parquet(pair)
    with pytest.raises(SystemExit, match="缺 registry_sha256"):
        w8.main(["--pairs", str(pair)])


def test_spearman_undefined_rho_is_na():
    """共同支撑上任一份额向量为常数 → ρ 数学未定义, 归 None (报告呈 n/a),
    不透传 nan (透传会打出 '+nan' 且被 ρ<0 反向证据点名静默漏计)。"""
    const = pd.Series([1.0] * 12, index=range(12))
    ranked = pd.Series(np.arange(12, dtype=float), index=range(12))
    rho, n = w8.spearman_common(const, ranked)
    assert rho is None and n == 12
    rho2, n2 = w8.spearman_common(ranked, ranked)  # 正例对照: 定义良好时照常出值
    assert rho2 == pytest.approx(1.0) and n2 == 12


def test_registry_missing_systemexit(tmp_path):
    """registry 文件缺失 → 显式 SystemExit 带排障指引 (非裸 FileNotFoundError)。"""
    with pytest.raises(SystemExit, match="registry 缺失"):
        w8.main(["--registry", str(tmp_path / "nonexistent.yaml")])


@pytest.mark.fast
def test_03_input_fingerprint_second_lock_readpoint_present():
    """D8 第二把锁读点 (2026-07-18 第六轮审计): listed 03 必须含 pair metadata 的
    input_fingerprint 读取与复算比对 — 删除即回退到「registry sha 单锁」, 21_full 重生
    而 sha 不变时 03 会静默用旧媒体锚×新测度库混代产互验报告。"""
    src = (REPO / "company_listed_bank" /
           "03_build_company_bank_weight_validation.py").read_text(encoding="utf-8")
    assert 'input_fingerprint' in src, "D8 第二把锁读点缺失 — 删除即回退 (2026-07-18)"
    assert src.count("input_fingerprint") >= 2, "须同时含 metadata 读点与复算比对两处"
