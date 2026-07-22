"""scripts/audit/innovation_proxy_triangulation.py
====================================================

WP-R3「创新维度三角化」—— substance/locus/collab 三个创新维度各构造一条
**方法独立的 $0 proxy 测度**（正则/词典/AC 自动机，零 LLM、零 API 调用），
与既有 LLM 标签、（未来的）人工标签三边互证，回答"三维创新测度的效度证据
是否只来自单一方法（LLM）"这一 review-critical 问题。

背景
----
`MEASUREMENT_VALIDITY_PARITY_EXECUTION_PLAN_2026-06-22.md` 注³ (F10) 指出：
substance/locus/collab 三个创新维度全部依赖单一方法（LLM 标注），结构上
不存在方法独立的第二测量机理，收敛效度 (convergent validity) 构念性不适用。
本脚本是对该缺口的**三角化闭环**回应：不是给三维再造一个"更准的"测量
（那仍是同方法的变体），而是给每维构造一条**方法学上完全独立**（正则匹配 /
词典二分 / AC 实体共现，而非任何 LLM 调用）的 proxy 测度，与 LLM 标签、
以及 WP-R2（人工标注，另一 WP，尚未收口）三者互证，形成三角闭环设计
（human-LLM / human-proxy / LLM-proxy 三边）。**proxy 本身不追求"测得更准"，
只追求"测量机理与 LLM 完全独立"** —— 这正是三角化范式的核心：不同方法的
共同局限彼此正交，一致的结论比单一方法更可信。

构造（三条 proxy，逐条见下方常量与函数）
--------------------------------------
1. **subst proxy**（对应 innovation_substantiveness/"实质性 vs 象征性"）：
   具体投入信号 regex 组 —— 金额+单位 / 人力规模 / 系统上线 / 专利 / 资质
   获批。W&Z (1994/1998) 的 substantive vs symbolic 区分本质是"是否有可
   验证的具体投入证据"，故用这组 regex 直接抓文本里的"硬证据"密度。
2. **locus proxy**（对应 innovation_locus/"底层技术 vs 应用场景"）：
   `config/fintech_locus_split.yaml`（WP-R3 双编码+仲裁产物 v2-2026-07-22，607 词
   (2026-07-21 词典换血) 按 Gomber et al. 2018 框架二分为 tech/func/unassigned）驱动的 AC 自动机，
   在 tech∪func 论域上算 tech 占比。
3. **collab proxy**（对应 innovation_collab_mode/"自主研发 vs 外部协同"）：
   协作动词表 × 非银实体（上市公司/税调企业/手工金科名单）AC 共现 ——
   Chesbrough (2003) open innovation 的操作化外部信号是"文本中出现协作
   语言 + 具体外部主体"两者同现。

设计
----
- 全程纯 CPU：正则 + pyahocorasick AC 自动机 + 词典二分表，**零 LLM 调用、
  零网络请求、零外部 API、$0**（与 stage 21 LLM 三家投票完全解耦）。
- 三边分析骨架（`analyze_triangulation`）：human-LLM / human-proxy /
  LLM-proxy。当前人工标签（WP-R2）尚未收口，human 边留接口 (`--human-labels`)，
  未提供路径时返回 `status="pending_wp_r2_human_labels"` 占位，**不假装
  算出一个数**；LLM-proxy 边基于 `21_tone_llms_full.parquet` 的
  `avg_{dim}_prob_score_full` 连续概率与本脚本 proxy 连续分数直接可算。
- 主报连续测度的 Spearman / point-biserial（不依赖阈值二值化）；二值 φ 系数
  / Cohen's κ 在阈值梯子 `{0.3, 0.5, 0.7}` 上作次要展示（梯子各点并排、
  不进任何联合检验 —— 镜像政治词权重/规则消融梯度先例）。

防误用铁律（写死于本脚本与每份产物 md/JSON 头部, 勿删）
--------------------------------------------------------
- **三 proxy 是「互为稳健性证据」的旁证轨，不是面板测度**：不产生任何
  面板 dta 列，不注册 DAG/OUTPUT_REGISTRY，无 thin shim；产物只落
  `validation/eval_reports/`。
- **`config/fintech_locus_split.yaml` 只读消费，`config/fintech_dict.json`
  本体零字节触碰**（后者是生产管道血缘锚点，见该 yaml 头注）。
- **铁律 note**（固定文案，逐份报告打印）：
  "co-equal validity evidence; never pooled into one over-identified
  Hansen J; not a panel measure, not an instrument"。
- proxy 精度天花板明确：这是**近似**测度（正则/词典/共现，非语义理解），
  弱相关不构成"LLM 测量失败"的证据，只构成"该维度尚缺独立支撑"的披露
  （见 WP-R3 §3 预登记弱边定位规则）。

白话
----
LLM 判"这篇报道是不是真金白银投入 / 底层技术还是业务场景 / 自己研发还是
找外援"，这个判断准不准，光靠 LLM 自己说了不算数。本脚本换一套完全不用
AI、只靠"抓关键词/抓具体数字/抓协作动词+公司名"的笨办法，独立算一遍
类似的分数，然后拿这个笨办法的分数去跟 LLM 的判断对一下——如果两者大体
方向一致，说明 LLM 的判断不是空穴来风；如果对不上，也不能说 LLM 错了，
只能说这个维度还缺一个独立的"第二证人"。真正说了算的"人工标注"这个
第二证人还没到位（另一个工作项 WP-R2），本脚本先把"笨办法"这个旁证
拿出来。

用法
----
    python -m news_process.scripts.audit.innovation_proxy_triangulation --dry-run
    python news_process/scripts/audit/innovation_proxy_triangulation.py --dry-run
    python news_process/scripts/audit/innovation_proxy_triangulation.py \
        --input <全量 21_tone_llms_full.parquet> --min-rows 5000

退出码
------
    0 = 成功写出报告 (三 proxy 构造 + LLM-proxy 边分析)。
    2 = 输入 parquet / fintech_locus_split.yaml 缺失。
    3 = 帧行数 < --min-rows 且未传 --dry-run (非生产规模, 拒绝无声当生产结果用)。
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# 路径注入: 让 news_process.* 在任意 cwd 可解析 (镜像
# measure_bank_fintech_cooccurrence.py 的既有范式)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402

logger = logging.getLogger("innovation_proxy_triangulation")
if not logger.handlers:
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[WP-R3] %(levelname)s %(message)s"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)

REPO = Path(_PROJECT_PARENT) / "news_process"
CONFIG_DIR = REPO / "config"
EVAL_REPORTS_DIR = REPO / "validation" / "eval_reports"

IRON_RULE_NOTE = (
    "co-equal validity evidence; never pooled into one over-identified Hansen J; "
    "not a panel measure, not an instrument"
)

# ============================================================================
# 1. subst proxy — 具体投入信号 regex 组
#    (W&Z 1994/1998 substantive vs symbolic: 是否有可验证的"硬证据"投入)
# ============================================================================
SUBST_SIGNAL_PATTERNS: dict[str, tuple[re.Pattern, str]] = {
    # 金额+单位: 具体投入规模的货币化信号 (如"投入5000万元"/"斥资2亿元")
    "amount": (
        re.compile(r"\d+(?:\.\d+)?\s*(?:万元|亿元|千万元|百万元|万美元|亿美元|美元|人民币)"),
        "金额+单位: 具体投入规模的货币化信号",
    ),
    # 人力规模: 具体投入的人力规模信号 (如"组建200人研发团队"/"引入50名工程师")
    "headcount": (
        re.compile(r"\d+\s*(?:名|多名|余名|位)?\s*(?:研发人员|工程师|技术人员|技术团队|研发团队|员工)"),
        "人数规模: 具体投入的人力规模信号",
    ),
    # 系统/平台上线: 具体技术交付里程碑信号 (如"核心系统正式上线"/"平台已投产")
    "system_launch": (
        re.compile(r"(?:系统|平台|产品|项目)(?:已|正式|全面)?\s*(?:上线|投产|发布|落地|投入使用)"),
        "系统上线: 具体技术交付里程碑信号",
    ),
    # 专利: 具体知识产权产出信号 (如"获得发明专利"/"专利号ZL...")
    "patent": (
        re.compile(r"专利号|发明专利|实用新型专利|(?:获得|申请|授权|拥有)\S{0,6}专利"),
        "专利/专利号: 具体知识产权产出信号",
    ),
    # 资质/牌照获批: 具体监管许可信号 (如"获批消费金融牌照"/"取得支付业务许可证")
    "license": (
        re.compile(r"(?:获批|获得|取得|拿到)\S{0,10}(?:牌照|许可证|资质|批复|执照)"),
        "资质获批: 具体监管许可信号",
    ),
}


def subst_proxy_score(text: str) -> tuple[int, list[str]]:
    """具体投入信号密度 = 命中的信号类别数 (0-5, 非累计出现次数 —— 一类信号
    出现 3 次和 1 次同记 1, 避免单类信号重复堆叠掩盖类别多样性)。

    Returns:
        (n_categories_hit, hit_category_names)
    """
    if not isinstance(text, str) or not text:
        return 0, []
    hits = [name for name, (pat, _doc) in SUBST_SIGNAL_PATTERNS.items() if pat.search(text)]
    return len(hits), hits


# ============================================================================
# 2. locus proxy — fintech_locus_split.yaml 驱动的 AC 自动机
# ============================================================================
def load_locus_split() -> dict:
    path = CONFIG_DIR / "fintech_locus_split.yaml"
    if not path.exists():
        raise SystemExit(
            f"[WP-R3] fintech_locus_split.yaml 缺失: {path} — 先跑双编码+仲裁流程产出该文件"
            " (见文件头注构造方法)。"
        )
    with open(path, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    for bucket in ("tech", "func", "unassigned"):
        if bucket not in doc:
            raise SystemExit(f"[WP-R3] fintech_locus_split.yaml 缺 '{bucket}' 桶")
    return doc


def build_ac(words: list[str]):
    """通用 AC 自动机构建 (pyahocorasick 原生 API; 范式抄
    company_listed_bank/02_build_company_bank_cooc_panel.py:264-274 与
    core/text/ahocorasick.py 的既有用法 —— add_word(pattern, value) + make_automaton())。
    """
    import ahocorasick
    A = ahocorasick.Automaton()
    for w in words:
        w = w.strip()
        if w:
            A.add_word(w, w)
    A.make_automaton()
    return A


def locus_proxy_ratio(text: str, tech_ac, func_ac) -> tuple[float, int, int]:
    """tech 占比 = distinct tech 命中词数 / (distinct tech + distinct func 命中词数)。

    unassigned 桶词不参与自动机 (词表构建时已剔出), 分子分母天然只在
    tech∪func 论域上计算 (WP-R3 §2 "unassigned 剔出分子分母" 约定)。

    Returns:
        (tech_ratio (NaN if tech+func==0), n_tech_distinct, n_func_distinct)
    """
    if not isinstance(text, str) or not text:
        return float("nan"), 0, 0
    tech_hits = {kw for _end, kw in tech_ac.iter(text)}
    func_hits = {kw for _end, kw in func_ac.iter(text)}
    n_tech, n_func = len(tech_hits), len(func_hits)
    denom = n_tech + n_func
    ratio = (n_tech / denom) if denom > 0 else float("nan")
    return ratio, n_tech, n_func


# ============================================================================
# 3. collab proxy — 协作动词表 × 非银实体共现
# ============================================================================
# ~20 个中文协作动词/短语 (Chesbrough 2003 open innovation 的外部协同语言信号;
# 每词附语义角色注释)。
COLLAB_VERBS: list[tuple[str, str]] = [
    ("合作", "通用合作动词, 覆盖面最广的协同信号"),
    ("联手", "并列主体共同行动, 强调对等协作"),
    ("携手", "同'联手', 常见于新闻标题化表达"),
    ("牵手", "非正式协作惯用语, 常见于财经报道标题"),
    ("签约", "正式合同签署, 隐含协议约束的外部协作"),
    ("战略合作", "正式命名的长期协作关系(名词短语)"),
    ("战略协议", "正式合作文书信号"),
    ("战略协作", "同战略合作, 措辞变体"),
    ("结盟", "联盟关系形成, 强协作强度信号"),
    ("共建", "联合建设(平台/实验室/系统), 具体协作产出导向"),
    ("共同打造", "联合产出导向表述"),
    ("联合开发", "具体研发协作(产品/系统层面)"),
    ("联合研发", "同联合开发, 研发协作变体"),
    ("合作研发", "同上, 措辞变体"),
    ("技术合作", "限定为技术层面的外部协作"),
    ("授权合作", "许可/授权型协作(如技术授权)"),
    ("深化合作", "既有合作关系的强化表述"),
    ("达成合作", "合作关系新近达成的时点性表述"),
    ("战略投资", "股权/资本层面的外部协作信号"),
    ("战略入股", "同战略投资, 强调入股行为"),
    ("引入战略投资者", "引入外部资本方的协作信号"),
]


def _load_bank_exclusion_names() -> set[str]:
    path = CONFIG_DIR / "bank_list.yaml"
    with open(path, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    return {b["target_bank"] for b in doc["banks"]}


def _is_bank_like(name: str, bank_names: set[str]) -> bool:
    """银行剔除判据: 精确命中 bank_list.yaml 全称, 或名称含'银行'字样
    (bank_list.yaml 实测 1767 家全称无一例外含'银行', 故此启发式与精确匹配
    等价且更稳健, 覆盖上市公司/税调企业清单里未逐字对齐 bank_list 拼写的边缘banks)。"""
    return name in bank_names or "银行" in name


# ~20 词头部非上市金科手工名单 (非 A 股上市 → 不在 company_listed_names.yaml;
# 非银行持牌机构 → 不应与 bank_list.yaml 冲突; 逐词注释注明排除/纳入依据)。
MANUAL_FINTECH_ENTITIES: list[tuple[str, str]] = [
    ("蚂蚁集团", "Ant Group, 非上市 (A股) 金科巨头, 非银行牌照主体"),
    ("蚂蚁金服", "蚂蚁集团曾用名, 历史报道高频出现"),
    ("京东科技", "京东集团金融科技板块, 非上市非银行"),
    ("京东数科", "京东科技曾用名(京东数字科技)"),
    ("度小满", "百度系金融科技公司, 非上市非银行"),
    ("度小满金融", "度小满曾用名/全称变体"),
    ("苏宁金融", "苏宁系金融科技板块, 非上市非银行"),
    ("陆金所控股", "陆金所在美股上市(非 A 股), 不在 company_listed_names.yaml 覆盖范围"),
    ("同盾科技", "风控科技独角兽, 未上市"),
    ("百融云创", "港股上市(非 A 股), 金融科技公司"),
    ("腾讯金融科技", "腾讯集团金融科技业务群(FiT), 非独立上市主体"),
    ("财付通", "腾讯旗下非银行支付牌照主体(微信支付底层)"),
    ("支付宝", "蚂蚁集团旗下非银行支付品牌"),
    ("宜信", "宜信普惠, 早期财富科技/P2P 代表企业, 未上市"),
    ("宜信普惠", "宜信旗下业务品牌"),
    ("挖财", "个人财务管理 App 代表企业, 未上市"),
    ("排排网", "第三方基金销售/财富科技平台, 未上市"),
    ("360数科", "360 数字科技(原360金融), 中概股上市(非 A 股)"),
    ("乐信", "乐信集团, 中概股上市(非 A 股), 消费金融科技公司"),
    ("信也科技", "信也科技(拍拍贷更名), 中概股上市(非 A 股)"),
]
# ⚠ 刻意排除 (非"非银"): 微众银行/网商银行/新网银行 —— 三者虽品牌互联网化,
# 但均持有银行牌照, 按 _is_bank_like 的"银行"字样规则天然排除, 此处显式
# 备注防止误加入手工名单。

# 泛机构后缀正则 (兜底捕获手工名单/官方清单外的长尾金科企业; 命中后仍需
# 排除含"银行"字样, 由调用方统一过滤)。
GENERIC_INSTITUTION_SUFFIX_RE = re.compile(
    r"[一-龥]{2,20}(?:金融科技|科技金融|数字科技|网络科技|信息科技|"
    r"大数据|云计算)(?:有限公司|股份有限公司)?"
)


def build_entity_assets() -> tuple:
    """构建非银实体锚点: 上市公司 + 税调企业 (剔除银行) + 手工金科名单。

    Returns:
        (entity_ac, bank_names_excluded_count, n_entities_total)
    """
    bank_names = _load_bank_exclusion_names()

    variants: set[str] = set()
    n_excluded = 0

    listed_path = CONFIG_DIR / "company_listed_names.yaml"
    with open(listed_path, encoding="utf-8") as f:
        listed_doc = yaml.safe_load(f)
    for c in listed_doc["companies"]:
        if _is_bank_like(c["company_listed_name"], bank_names):
            n_excluded += 1
            continue
        for v in c.get("variants", []):
            if v and v.strip():
                variants.add(v.strip())

    tax_path = CONFIG_DIR / "company_tax_names.yaml"
    with open(tax_path, encoding="utf-8") as f:
        tax_doc = yaml.safe_load(f)
    for c in tax_doc["companies"]:
        if _is_bank_like(c["company_tax_name"], bank_names):
            n_excluded += 1
            continue
        for v in c.get("variants", []):
            if v and v.strip():
                variants.add(v.strip())

    for name, _note in MANUAL_FINTECH_ENTITIES:
        variants.add(name)

    entity_ac = build_ac(sorted(variants))
    return entity_ac, n_excluded, len(variants)


def collab_proxy_indicator(text: str, verb_ac, entity_ac) -> tuple[bool, int, int]:
    """协作信号 = 协作动词命中 AND (已知非银实体命中 OR 泛机构后缀正则命中)。

    文档级 (whole-article) 共现, 非句级/窗口级 —— proxy 定位是"廉价旁证",
    非production 精度的共现判据 (production 判据见 stage 13
    `entity_context.has_bank_fintech_cooccurrence_within_radius`, 本脚本
    刻意不复用生产判据以保持"方法独立"的三角化前提)。

    Returns:
        (is_collab_signal, n_verb_hits, n_entity_hits)
    """
    if not isinstance(text, str) or not text:
        return False, 0, 0
    verb_hits = sum(1 for _end, _v in verb_ac.iter(text))
    entity_hits = {v for _end, v in entity_ac.iter(text)}
    n_entity = len(entity_hits)
    if n_entity == 0 and GENERIC_INSTITUTION_SUFFIX_RE.search(text):
        n_entity = 1  # 正则兜底命中记 1 (非可数命名实体, 只记"是否出现")
    return (verb_hits > 0 and n_entity > 0), verb_hits, n_entity


# ============================================================================
# 三角分析: human-LLM / human-proxy / LLM-proxy
# ============================================================================
THRESHOLD_LADDER = (0.3, 0.5, 0.7)


def _spearman(x: pd.Series, y: pd.Series) -> float:
    m = x.notna() & y.notna()
    if m.sum() < 3:
        return float("nan")
    return float(x[m].corr(y[m], method="spearman"))


def _point_biserial(binary: pd.Series, cont: pd.Series) -> float:
    """point-biserial = Pearson r(binary(0/1), continuous) —— 数学等价, 无需
    专门实现 (标准心理测量学结论, 见 Tate 1954)。"""
    m = binary.notna() & cont.notna()
    if m.sum() < 3:
        return float("nan")
    return float(binary[m].astype(float).corr(cont[m], method="pearson"))


def _phi_kappa(bin_a: pd.Series, bin_b: pd.Series) -> dict:
    m = bin_a.notna() & bin_b.notna()
    a, b = bin_a[m].astype(int), bin_b[m].astype(int)
    n = len(a)
    if n < 3:
        return {"n": int(n), "phi": float("nan"), "kappa": float("nan")}
    po = float((a == b).mean())
    # phi = Pearson r on 0/1 indicators
    phi = float(a.corr(b, method="pearson")) if a.std() > 0 and b.std() > 0 else float("nan")
    pa1, pb1 = a.mean(), b.mean()
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    kappa = (po - pe) / (1 - pe) if pe < 1 else float("nan")
    return {"n": int(n), "phi": phi, "kappa": float(kappa), "po": po}


def compute_llm_proxy_edge(df: pd.DataFrame) -> dict:
    """LLM-proxy 边: 本脚本 proxy 连续分数 vs `21_tone_llms_full.parquet` 的
    `avg_{dim}_prob_score_full` 连续概率 (仅在 `llm_verified_full==True` 子集
    上算, 与面板聚合的 verified 门控口径一致)。"""
    edge: dict = {}
    verified = df["llm_verified_full"].fillna(False).astype(bool) if "llm_verified_full" in df.columns else pd.Series(True, index=df.index)
    sub = df[verified].copy()

    # --- subst ---
    llm_subst = sub.get("avg_subst_prob_score_full")
    proxy_subst = sub["subst_proxy_n_categories"] / 5.0  # 归一化到 [0,1]
    edge["subst"] = {
        "n": int(verified.sum()),
        "spearman": _spearman(proxy_subst, llm_subst) if llm_subst is not None else float("nan"),
        "threshold_ladder": {},
    }
    if llm_subst is not None:
        for t in THRESHOLD_LADDER:
            edge["subst"]["threshold_ladder"][str(t)] = _phi_kappa(
                (proxy_subst >= t), (llm_subst >= 0.5))

    # --- locus ---
    llm_locus = sub.get("avg_locus_prob_score_full")
    proxy_locus = sub["locus_proxy_tech_ratio"]
    edge["locus"] = {
        "n": int(proxy_locus.notna().sum()),
        "spearman": _spearman(proxy_locus, llm_locus) if llm_locus is not None else float("nan"),
        "threshold_ladder": {},
    }
    if llm_locus is not None:
        for t in THRESHOLD_LADDER:
            edge["locus"]["threshold_ladder"][str(t)] = _phi_kappa(
                (proxy_locus >= t), (llm_locus >= 0.5))

    # --- collab ---
    llm_collab = sub.get("avg_collab_prob_score_full")
    proxy_collab_cont = sub["collab_proxy_n_verb_hits"].clip(upper=5) / 5.0
    proxy_collab_bin = sub["collab_proxy_is_signal"]
    edge["collab"] = {
        "n": int(verified.sum()),
        "spearman": _spearman(proxy_collab_cont, llm_collab) if llm_collab is not None else float("nan"),
        "point_biserial_binary_proxy": _point_biserial(proxy_collab_bin, llm_collab) if llm_collab is not None else float("nan"),
        "threshold_ladder": {},
    }
    if llm_collab is not None:
        for t in THRESHOLD_LADDER:
            edge["collab"]["threshold_ladder"][str(t)] = _phi_kappa(
                proxy_collab_bin, (llm_collab >= t))

    return edge


def compute_human_edges_stub(human_labels_path: str | None) -> dict:
    """human-LLM / human-proxy 两边留接口 —— WP-R2 人工标签尚未收口
    (MVP-0622 通道待生产语料人工填写, 见 CLAUDE.md 稳健性缺口闭环)。

    人工标签就绪后, 传 `--human-labels <path>` (schema: docid, subst_human,
    locus_human, collab_human), 本函数会自动补齐两边真实数值; 就绪前
    显式返回 pending 状态, **不伪造一个数字**。"""
    if not human_labels_path or not os.path.exists(human_labels_path):
        return {
            "status": "pending_wp_r2_human_labels",
            "note": "待 WP-R2 人工标签收口 (MVP-0622 通道人工填写完成后, 传 "
                    "--human-labels <path> 即可自动补齐 human-LLM / human-proxy 两边)",
        }
    # 人工标签就绪后的计算路径 (schema 契约见 docstring); 目前分支未触达。
    human_df = pd.read_parquet(human_labels_path) if human_labels_path.endswith(".parquet") \
        else pd.read_csv(human_labels_path)
    return {"status": "computed", "n_human_labels": int(len(human_df))}


def analyze_triangulation(df: pd.DataFrame, human_labels_path: str | None) -> dict:
    return {
        "iron_rule_note": IRON_RULE_NOTE,
        "llm_proxy_edge": compute_llm_proxy_edge(df),
        "human_llm_edge": compute_human_edges_stub(human_labels_path),
        "human_proxy_edge": compute_human_edges_stub(human_labels_path),
        "weak_edge_rule": (
            "预登记弱边定位规则 (WP-R3 §3): human-LLM 高 + human-proxy 低 → "
            "proxy 弱、LLM 效度由人工边独立支撑; human-LLM 低 → 问题在 LLM 或"
            "构念本身 (回 WP-R2.5); 三边俱低 → 操作化整体存疑, 入限界披露。"
            "当前 human 边 pending, 本轮仅可报 LLM-proxy 边, 弱边定位待 WP-R2 收口。"
        ),
    }


# ============================================================================
# 主流程
# ============================================================================
def _load_input(input_path: str | None) -> tuple[pd.DataFrame, str]:
    if input_path is None:
        cfg = load_config()
        input_path = os.path.join(
            cfg["paths"]["output_dir"],
            cfg["paths"].get("output_21_tone_llms_full", "21_tone_llms_full.parquet"),
        )
    if not os.path.exists(input_path):
        raise SystemExit(f"[WP-R3] 输入缺失: {input_path} — 请先跑 stage 21 或指定 --input。")
    df = pd.read_parquet(input_path)
    return df, input_path


def build_proxies(df: pd.DataFrame) -> pd.DataFrame:
    """对全帧逐行构造三 proxy 列 (纯 CPU, $0)。"""
    locus_doc = load_locus_split()
    tech_ac = build_ac(locus_doc["tech"])
    func_ac = build_ac(locus_doc["func"])
    entity_ac, n_excluded, n_entities = build_entity_assets()
    verb_ac = build_ac([v for v, _note in COLLAB_VERBS])
    logger.info("locus 词表: tech=%d / func=%d / unassigned=%d (fintech_locus_split.yaml v%s)",
                len(locus_doc["tech"]), len(locus_doc["func"]), len(locus_doc["unassigned"]),
                locus_doc["metadata"]["version"])
    logger.info("collab 实体锚点: %d 个非银实体变体 (剔除银行样式名称 %d 个) + %d 词协作动词表",
                n_entities, n_excluded, len(COLLAB_VERBS))

    text_col = "content_full" if "content_full" in df.columns else None
    if text_col is None:
        raise SystemExit("[WP-R3] 输入帧缺 content_full 列 (proxy 全部在 full 轨全文上算)。")

    n_cat, cat_names = [], []
    tech_r, n_tech_l, n_func_l = [], [], []
    is_sig, n_verb, n_ent = [], [], []
    for text in df[text_col]:
        c, names = subst_proxy_score(text)
        n_cat.append(c)
        cat_names.append(",".join(names))
        r, nt, nf = locus_proxy_ratio(text, tech_ac, func_ac)
        tech_r.append(r)
        n_tech_l.append(nt)
        n_func_l.append(nf)
        sig, nv, ne = collab_proxy_indicator(text, verb_ac, entity_ac)
        is_sig.append(sig)
        n_verb.append(nv)
        n_ent.append(ne)

    out = df.copy()
    out["subst_proxy_n_categories"] = n_cat
    out["subst_proxy_categories"] = cat_names
    out["locus_proxy_tech_ratio"] = tech_r
    out["locus_proxy_n_tech"] = n_tech_l
    out["locus_proxy_n_func"] = n_func_l
    out["collab_proxy_is_signal"] = is_sig
    out["collab_proxy_n_verb_hits"] = n_verb
    out["collab_proxy_n_entity_hits"] = n_ent
    return out


def write_reports(df_with_proxies: pd.DataFrame, edges: dict, tag: str) -> list[str]:
    EVAL_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    written = []

    detail_cols = [
        "docid", "target_bank", "subst_proxy_n_categories", "subst_proxy_categories",
        "locus_proxy_tech_ratio", "locus_proxy_n_tech", "locus_proxy_n_func",
        "collab_proxy_is_signal", "collab_proxy_n_verb_hits", "collab_proxy_n_entity_hits",
    ]
    detail_cols = [c for c in detail_cols if c in df_with_proxies.columns]
    detail_path = EVAL_REPORTS_DIR / f"innovation_proxy_triangulation_detail{tag}.csv"
    df_with_proxies[detail_cols].to_csv(detail_path, index=False, encoding="utf-8-sig")
    written.append(str(detail_path))

    results_path = EVAL_REPORTS_DIR / f"innovation_proxy_triangulation_results{tag}.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(edges, f, ensure_ascii=False, indent=2, default=lambda o: None if isinstance(o, float) and np.isnan(o) else o)
    written.append(str(results_path))

    md_path = EVAL_REPORTS_DIR / f"innovation_proxy_triangulation_summary{tag}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# WP-R3 创新维度三角化 — proxy 构造报告\n\n")
        f.write(f"> **铁律**: {IRON_RULE_NOTE}\n\n")
        f.write("## LLM-proxy 边 (Spearman / point-biserial 主报; φ/κ 阈值梯子次要展示)\n\n")
        for dim, d in edges["llm_proxy_edge"].items():
            f.write(f"### {dim}\n\n- n = {d.get('n')}\n- Spearman ρ = {d.get('spearman')}\n")
            if "point_biserial_binary_proxy" in d:
                f.write(f"- point-biserial r = {d.get('point_biserial_binary_proxy')}\n")
            f.write("- 阈值梯子 (φ / κ, 次要展示):\n\n")
            for t, v in d.get("threshold_ladder", {}).items():
                f.write(f"  - threshold={t}: n={v.get('n')} φ={v.get('phi')} κ={v.get('kappa')}\n")
            f.write("\n")
        f.write("## human 边\n\n")
        f.write(f"- human-LLM: {edges['human_llm_edge']}\n")
        f.write(f"- human-proxy: {edges['human_proxy_edge']}\n\n")
        f.write(f"## 弱边定位规则\n\n{edges['weak_edge_rule']}\n")
    written.append(str(md_path))
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="WP-R3 创新维度三角化 — $0 proxy 构造 + LLM-proxy 边分析")
    ap.add_argument("--input", type=str, default=None,
                    help="21_tone_llms_full.parquet 路径 (缺省=配置默认路径)")
    ap.add_argument("--human-labels", type=str, default=None,
                    help="WP-R2 人工标签文件 (parquet/csv, 尚未收口时留空)")
    ap.add_argument("--min-rows", type=int, default=5000,
                    help="非 --dry-run 模式下的生产规模门槛 (帧行数 < 此值且未传 --dry-run 时拒绝跑, 退出码 3)")
    ap.add_argument("--dry-run", action="store_true",
                    help="T=2 dev 规模验证跑通模式: 跳过 --min-rows 门槛, 产物文件名加 _dryrun 后缀")
    args = ap.parse_args(argv)

    df, input_path = _load_input(args.input)
    n_rows = len(df)
    logger.info("输入帧: %s (%d 行)", input_path, n_rows)

    if not args.dry_run and n_rows < args.min_rows:
        logger.error(
            "帧行数 %d < --min-rows=%d 且未传 --dry-run — 拒绝把 dev 规模结果当生产结果用。"
            " 加 --dry-run 显式确认这是验证跑, 或指定全量语料帧。",
            n_rows, args.min_rows)
        return 3

    df_proxies = build_proxies(df)
    edges = analyze_triangulation(df_proxies, args.human_labels)

    tag = "_dryrun" if args.dry_run else ""
    written = write_reports(df_proxies, edges, tag)
    for p in written:
        logger.info("已写出: %s", p)
    logger.info("[OK] WP-R3 proxy 三角化报告完成 (%s模式)。%s",
                "dry-run" if args.dry_run else "生产", IRON_RULE_NOTE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
