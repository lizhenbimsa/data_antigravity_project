"""news_process.pipeline.preprocess.filter — DataFrame 初步过滤层.

Phase 4b 从 ``runner.py`` 提取。包含:
- ``_clean_and_filter_dataframe`` — 8 步过滤(地域/类型/黑名单/缺失/广告/银行词/Schema/媒体名称清理)

依赖:
    filter.py ← _constants.py
    filter.py ← load.py (BANK_KW_AUTOMATON, _ac_contains_any)
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from news_process.pipeline.preprocess._constants import (
    AD_PATTERN,
    AD_PATTERN_TITLE,
    KEY_COLUMNS,
    MEDIA_NAME_OVERRIDES,
    MEDIA_NAMES_TO_EXCLUDE,
    MEDIA_TYPES_INCLUDE_SET,
    REGION_PATTERN,
    logger,
)
from news_process.pipeline.preprocess.load import (
    BANK_KW_AUTOMATON,
    _ac_contains_any,
)


def _clean_and_filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """对单个 DataFrame 执行全部初始过滤操作.

    过滤顺序经过精心设计, 按数据淘汰率从高到低排列,
    确保高淘汰率的过滤先执行, 最大化减少后续步骤的数据量:
      1. 媒体地域过滤 (淘汰率最高, ~60-70%)
      2. 媒体类型过滤 (~5-10%)
      3. 媒体名称黑名单过滤 (排除剪报服务等非原始新闻来源)
      4. 缺失值过滤 (~2-5%)
      5. 广告关键词过滤 (~1-3%; 标题字段高误伤词行尾锚定, fix omni-g-preprocess-05)
      6. 银行关键词保留过滤 (Aho-Corasick, ~30-50%; 自动机含繁体/全角括号变体
         以兼容规范化前的原始文本, fix omni-g-preprocess-07)
      7. Schema 统一 (object → string, 不改变行数)
      8. 媒体名称清理 (去除报纸名称修饰后缀/版面/无效字符, 不改变行数)

    Args:
        df: 从 Excel 文件读取的原始 DataFrame。

    Returns:
        pd.DataFrame: 过滤和标准化后的 DataFrame。
    """
    if df.empty:
        return df

    # 1. 媒体地域过滤: 仅保留中国大陆地区的媒体
    if REGION_PATTERN is not None:
        rows_before = len(df)
        region_cleaned = df['国家地区/省份'].astype(str).str.replace(r'\s+', '', regex=True)
        df = df[region_cleaned.str.contains(REGION_PATTERN, na=False, regex=True)]
        logger.info(f"  [1/8 地域过滤] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")

    # 2. 媒体类型过滤: 仅保留指定类型(如"报纸")
    rows_before = len(df)
    df = df[df['媒体类型(中文)'].isin(MEDIA_TYPES_INCLUDE_SET)]
    logger.info(f"  [2/8 类型过滤] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")

    # 3. 媒体名称黑名单过滤: 排除剪报服务机构等非原始新闻来源
    if MEDIA_NAMES_TO_EXCLUDE:
        rows_before = len(df)
        df = df[~df['媒体(中文)'].astype(str).isin(MEDIA_NAMES_TO_EXCLUDE)]
        if rows_before - len(df) > 0:
            logger.info(f"  [3/8 媒体名称黑名单] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")

    # 4. 关键字段缺失值过滤(标题、内容、媒体名、日期任一为空则移除)
    rows_before = len(df)
    df = df.dropna(subset=KEY_COLUMNS)
    # R1-R5 audit fix A8 (2026-05-27): 修 R4-A8 finding —— dropna 仅 drop None/NaN,
    # 不 drop literal empty string ''. OCR / Wisers 数据库 NULL → '' 映射时关键
    # 字段保留, 导致 pd.to_datetime 后 NaT silent 进 panel. 此处对每个关键列做
    # ne('') strip 过滤.
    for _col in KEY_COLUMNS:
        if _col in df.columns:
            df = df[df[_col].astype(str).str.strip() != '']
    logger.info(f"  [4/8 缺失值过滤] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")

    # 5. 广告关键词过滤(检查标题、版面、栏名三个字段)
    # fix(omni-g-preprocess-05, 2026-06-11): 标题字段改用 AD_PATTERN_TITLE —
    # 高误伤词 (公告/通知/声明/通报/风险提示/年度报告) 对标题要求行尾锚定,
    # 不再把 '央行公告下调存准率' / '上市银行年度报告显示…' 等监管新闻整篇
    # 误删; 版面/栏名仍用无锚定 AD_PATTERN (付费公告版面全量排除, 行为不变)。
    # 数据附录披露: 标题命中广告关键词 (高误伤词须行尾锚定) 或 版面/栏名含
    # 任一广告关键词的记录被排除出语料 — 该排除与监管事件强度相关, 属语料
    # 构建的样本选择规则, 写论文 data appendix 时须披露。
    for field_name, col_name, _pattern in [
        ('标题', '标题', AD_PATTERN_TITLE),
        ('版面', '版面', AD_PATTERN),
        ('栏名', '栏名', AD_PATTERN),
    ]:
        if _pattern is None:
            continue
        rows_before = len(df)
        df = df[~df[col_name].astype(str).str.contains(_pattern, na=False, regex=True)]
        if rows_before - len(df) > 0:
            logger.info(
                f"  [5/8 广告过滤-{field_name}] "
                f"移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}"
            )

    # 6. 银行关键词保留过滤(Aho-Corasick O(n) 复杂度)
    # 只保留内容中提及至少一个银行关键词的新闻
    if BANK_KW_AUTOMATON is not None:
        rows_before = len(df)
        content_values = df['内容'].astype(str).values
        # 向量化版本: 使用 numpy 布尔数组避免 Python 级别循环开销
        mask = np.fromiter(
            (_ac_contains_any(t, BANK_KW_AUTOMATON) for t in content_values),
            dtype=bool,
            count=len(content_values)
        )
        df = df[mask]
        logger.info(f"  [6/8 银行关键词过滤] 移除 {rows_before - len(df):,} 行 → 剩余 {len(df):,}")

    # 7. Schema 统一: object 列 → string, 确保后续 Parquet 序列化安全
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('').astype(str)

    # 8. 媒体名称清理: 去除报纸名称中的各类修饰后缀、附加版面及无效字符
    # 白话: 把 "人民日报·海外版 since 2008" 这类带修饰的报名逐步裁剪回母报名
    # ("人民日报"), 让同一家报纸在数据里只剩一个统一名字; 裁过头变成空串时
    # 回退到只去掉换行符的原名, 不会把媒体名洗丢。
    if '媒体(中文)' in df.columns:
        orig_media = df['媒体(中文)'].astype(str)
        # (0) 基础预清理: 剔除换行/制表符等不可见格式字符, 作为最安全的基底名称
        s_base = orig_media.str.replace(r'[\r\n\t]+', ' ', regex=True).str.strip()
        s = s_base.copy()

        # (1) 括号内内容清除
        s = s.str.replace(r'[\(（\[【].*?[\)）\]】]', '', regex=True)
        # (2) 数字报及固定短语清除
        s = s.str.replace('数字报', '', regex=False)
        # (3) 日期及 since 清除
        s = s.str.replace(r'\s*-\s*since\s+.*', '', flags=re.IGNORECASE, regex=True)
        s = s.str.replace(r'\s*-\s*\d{8}\s*-\s*\d{8}.*', '', regex=True)
        s = s.str.replace(r'\s+\d{8}-\d{8}.*', '', regex=True)
        # (4) 点号及中圆点后缀清除
        s = s.str.replace(r'^(.*?[\u4e00-\u9fa5][^·\.]*)[·\.].*', r'\1', regex=True)
        # (5) 特定地域及版面清除
        s = s.str.replace(
            r'\s*-?\s*(英文版|中文版|东莞版|加东版|加西版|美西版|粤东版|台湾版|网络版|电子版|手机版|华南版|华东版|西北版|纽约免费报|东九龙|西九龙).*',
            '', regex=True
        )
        # (6) 删除末尾纯英文字符串
        s = s.str.replace(r'(.*[\u4e00-\u9fa5].*?)\s+[a-zA-Z\s]+$', r'\1', regex=True)

        cleaned_media = s.str.strip()

        # 防御性回退: 如果清洗后变为空(如纯括号组成), 则保留预清理后的原名称
        s_final = cleaned_media.where(cleaned_media != '', s_base)

        # (7) 重点特例覆盖
        for k, v in MEDIA_NAME_OVERRIDES.items():
            s_final = s_final.where(s_base != k, v)

        df['媒体(中文)'] = s_final

    return df


__all__ = ['_clean_and_filter_dataframe']
