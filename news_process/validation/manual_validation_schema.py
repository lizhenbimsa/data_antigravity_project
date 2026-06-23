"""manual_validation_samples.xlsx schema 的单一事实源 (single source of truth)。

Plan v1.37 P0 §3.3.1 (R23A-01 — 抽样脚本的 v3.2.0 迁移由独立的前置
ticket 跟踪; 本模块只固化下游评估所期望的 schema)。

使用方:
  - news_process/validation/llms_evaluation.py (P0 4 任务扩展)
  - news_process/tests/test_63_evaluation.py (test_r_column_schema_coupling)

抽样脚本 news_process/scripts/migrate/manual_validation_sampling.py 用
f-string 模板生成编码者列名
(`f'{rater}_stage3a_substantiveness'`, rater 取 ['R1','R2','R3']);
本模块把这些模板镜像为具体常量。
"""
import pandas as pd

# 3 编码者共识设计 (plan v1.37 §3.3.1)
R_COLUMNS_BY_RATER = {
    'substantiveness': [
        'R1_stage3a_substantiveness',
        'R2_stage3a_substantiveness',
        'R3_stage3a_substantiveness',
    ],
    'locus': [
        'R1_stage3b_locus',
        'R2_stage3b_locus',
        'R3_stage3b_locus',
    ],
    # WS-A (G3): collab 编码者间 schema (自研/协同, Chesbrough 2003 / L&S 2006)。
    # ⚠ 维度键裸名 'collab' (对齐 substantiveness/locus); task/pred/metrics
    #   层用 innovation_collab_mode 前缀 (见 llms_evaluation.py)。
    'collab': [
        'R1_stage3c_collab',
        'R2_stage3c_collab',
        'R3_stage3c_collab',
    ],
}


# 编码者单元格的取值可能是英文 (见抽样脚本 L130-144);
# LLM 预测 + Stata 编码用中文。下游比较前先归一化 (R3C-01 + R5C-01)。
_RATER_VALUE_TO_CANONICAL_LABEL_RAW = {
    'substantive': '实质性',
    'symbolic':    '象征性',
    'technology':  '底层技术',
    'application': '应用场景',
    # WS-A: collab 取值 (自研/协同)
    'self_developed': '自主研发',
    'collaborative':  '外部协同',
    # 已是中文的原样透传
    '实质性': '实质性',
    '象征性': '象征性',
    '底层技术': '底层技术',
    '应用场景': '应用场景',
    '自主研发': '自主研发',
    '外部协同': '外部协同',
}


def normalize_rater_value(raw):
    """把编码者单元格取值归一化为规范中文标签, 无法识别时返回 None。

    规则 (plan v1.37 §3.3.1 + R4A-02 + R5C-01):
      - None / pandas.isna(raw) / 空字符串 → None (静默)。
      - 通过了 isna() 的 bool / int / float → None (静默;
        openpyxl 自动类型推断的产物)。
      - 字符串先 .strip(); 英文键经 .lower() 大小写折叠匹配;
        中文键 (CJK 不受大小写折叠影响) 直接匹配。
      - 未知字符串 (如拼写错误 'subtantive') → None。
    """
    try:
        if raw is None or pd.isna(raw):
            return None
    except (TypeError, ValueError):
        pass
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if not s:
        return None
    return (_RATER_VALUE_TO_CANONICAL_LABEL_RAW.get(s)
            or _RATER_VALUE_TO_CANONICAL_LABEL_RAW.get(s.lower()))


def merge_three_rater_majority(row, rater_columns):
    """单行的 3 编码者多数票共识 (majority-vote consensus)。

    返回规范中文标签或 None。

    规则 (plan v1.37 §3.3.1):
      1. 3 个单元格经 normalize_rater_value 归一化; 丢弃 None。
      2. 0 个有效单元格 → None (不进 gold)。
      3. 恰好 1 个有效 → None (缺乏编码者间确认; R3C-13)。
      4. ≥2 个有效且 ≥2 个一致 → 多数标签。
      5. 恰好 2 个有效且互不一致 (第 3 个缺失) → None (平局)。

    白话: 三个人投票, 至少要有两票相同才算数; 只有一个人填了、或两个
    人意见相反, 都不能当金标准用。
    """
    values = [normalize_rater_value(row.get(c)) for c in rater_columns]
    values = [v for v in values if v is not None]
    if len(values) == 0:
        return None
    if len(values) == 1:
        return None  # 缺乏编码者间确认
    # 计票
    from collections import Counter
    counts = Counter(values)
    most_common = counts.most_common(2)
    if most_common[0][1] >= 2:
        return most_common[0][0]
    return None  # 1-1 平局 (第 3 票缺失), 或 1-1-1 (二分类下不可能)
