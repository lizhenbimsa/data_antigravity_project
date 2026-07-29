"""tests/test_media_name_override_in_dedup.py — 媒体名归一化必须对**所有**去重入口生效。

**事故 (2026-07-29 入口③ 阶段 62)**:
    未匹配媒体 10 个 (162,487 行回退默认权重), 高频未匹配:
    {'21世界经济报道': 155319, '羊城晚报深圳版': 2655, '河南法制报': 1951, ...}

而这 10 个名字**全部**早已在 `MEDIA_NAME_OVERRIDES` 里 —— 规则不缺, 是**没被执行到**:

    filter.py:297      对新 xlsx 应用 override → 写 _cache/<file>.parquet
                       ⚠ 增量缓存命中时整段跳过 ⟹ 缓存里留的是原始名
    runner.py:699      全量读回后再兜底 replace  ⟹ stage 00 生产去重 ✅ 正确
    _load_pre_dedup_corpus (stage 62)  直读 _cache/*.parquet 拼接就用
                       ❌ 绕过那层兜底 ⟹ 权重全落默认 10

`runner.py:695-697` 的注释本就写明兜底存在的理由是「确保映射**始终**作用于全量数据」——
第二条路径漏掉它是疏忽, 不是设计。

**修法**: 下沉到 `ArticleDeduplicator._prepare_dataframe`, 由 fail-open 改为 fail-safe ——
任何喂给去重器的语料都自动归一, 而不是每个调用方各自记得做。**刻意不选**"在 62 号补一次
replace": 那会是第 3 处副本, 下一个新增的 _cache 消费者仍会再踩一遍。

**幂等性是 golden 安全的前提**: stage 00 的 runner 已先 replace 过一遍, 再走去重器内这一层
必须是 no-op, 否则去重输入变化 → golden 漂移。已实证: 唯一"value 同时是 key"的条目是自映射
`'读者文摘 - 中文版'` (刻意, 防被正则误洗), 无链式改写。

⚠ **严重性边界 (勿夸大)**: 媒体权重在近似去重里**只是同日 tiebreak** (`dedup.py:276` docstring
明载「媒体权重仅作同日 tiebreak」), 簇内排序主键是日期。同日文章彼此距离 0、必然同落时间窗,
故无论谁排第一都只活一条 ⟹ **保留条数与权重无关**, 权重只改"活下来的是哪一条"。
本 gate 因此**分开断言计数与身份**, 不把二者混为一谈。
"""
from __future__ import annotations

import inspect
import os
import sys

import pandas as pd
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.preprocess import dedup as dd  # noqa: E402
from news_process.pipeline.preprocess._constants import (  # noqa: E402
    MEDIA_NAME_OVERRIDES as M,
)

#: 2026-07-29 阶段 62 实际报出的 10 个未匹配名 (逐字节取自生产日志) —— 全部必须可归一。
PRODUCTION_UNMATCHED = [
    '21世界经济报道', '羊城晚报深圳版', '河南法制报', '羊城晚报佛山版', '中国工商报',
    '人民邮电报', '中国保险报', '羊城晚报顺德版', '四川法制报', '新民晚报社区版家庭周刊',
]


class _NullLogger:
    def __getattr__(self, _):
        return lambda *a, **k: None


def _cfg():
    from news_process.core.config import load_config
    return load_config()


def _frame(media_names):
    n = len(media_names)
    return pd.DataFrame({
        'docid': [str(1000 + i) for i in range(n)],
        '标题': [f'标题{i}' for i in range(n)],
        '内容': [f'内容内容内容{i}' for i in range(n)],
        '日期': [f'2020-01-0{i % 9 + 1}' for i in range(n)],
        '媒体(中文)': list(media_names),
    })


# ── ① 10 个生产未匹配名必须全部在 override 表里 ──

@pytest.mark.parametrize('name', PRODUCTION_UNMATCHED)
def test_production_unmatched_name_is_covered_by_overrides(name):
    assert name in M, (
        f'{name!r} 不在 MEDIA_NAME_OVERRIDES —— 2026-07-29 阶段 62 报的 10 个未匹配名'
        f'当时全部已在表内, 若此条消失说明归一规则被删。')


def test_override_targets_exist_in_weight_table():
    """归一目标必须在 media_weights.json 里有权重, 否则归一了照样回退默认权重。"""
    import json

    from news_process.core.config import load_config
    wpath = load_config()['paths']['media_weights_file']
    with open(wpath, encoding='utf-8') as f:
        weights = json.load(f)
    missing = sorted({M[n] for n in PRODUCTION_UNMATCHED if M[n] not in weights})
    assert not missing, (
        f'以下归一目标在 media_weights.json 中无条目: {missing} —— '
        f'归一后仍会回退默认权重, 等于没修。')


# ── ② 去重器内部必须应用归一 (fail-safe by construction) ──

def test_prepare_dataframe_normalizes_media_names():
    d = dd.ArticleDeduplicator(config=_cfg(), logger_instance=_NullLogger())
    out = d._prepare_dataframe(_frame(PRODUCTION_UNMATCHED))
    still_raw = [n for n in out['媒体(中文)'] if n in M and M[n] != n]
    assert not still_raw, (
        f'_prepare_dataframe 后仍有未归一的原始名: {sorted(set(still_raw))} —— '
        f'归一化必须在去重器内部兜底, 否则直读 _cache/*.parquet 的路径 (阶段 62) 又会漏。')


def test_no_default_weight_fallback_for_covered_media():
    """归一后这 10 家不得再落默认权重 —— 这正是生产日志里那 162,487 行的成因。"""
    d = dd.ArticleDeduplicator(config=_cfg(), logger_instance=_NullLogger())
    out = d._prepare_dataframe(_frame(PRODUCTION_UNMATCHED))
    fell_back = out[out[d.COL_WEIGHT] == d.default_weight]['媒体(中文)'].tolist()
    assert not fell_back, (
        f'以下媒体归一后仍回退默认权重 {d.default_weight}: {sorted(set(fell_back))}')


def test_source_applies_overrides_inside_prepare():
    src = inspect.getsource(dd.ArticleDeduplicator._prepare_dataframe)
    assert 'MEDIA_NAME_OVERRIDES' in src, (
        '_prepare_dataframe 不再应用 MEDIA_NAME_OVERRIDES —— 修复被回退。'
        '勿改成"在 62 号补一次 replace": 那是第 3 处副本, 下一个 _cache 消费者仍会踩。')


# ── ③ 幂等 (golden 安全前提) ──

def test_overrides_have_no_chained_mapping():
    """value 不得同时是 key (自映射除外), 否则二次 replace 会继续改写, 破坏幂等。"""
    chained = {v: M[v] for v in set(M.values()) if v in M and M[v] != v}
    assert not chained, (
        f'出现链式映射 {chained} —— replace 应用两次的结果将不同于一次, '
        f'stage 00 (runner 已 replace 过) 再经去重器就会二次改写 ⟹ golden 漂移。')


def test_double_application_is_noop():
    """实证幂等: 对已归一数据再跑一遍 _prepare_dataframe, 媒体名与权重逐格不变。"""
    cfg = _cfg()
    d1 = dd.ArticleDeduplicator(config=cfg, logger_instance=_NullLogger())
    once = d1._prepare_dataframe(_frame(PRODUCTION_UNMATCHED))
    d2 = dd.ArticleDeduplicator(config=cfg, logger_instance=_NullLogger())
    twice = d2._prepare_dataframe(once.copy())
    assert list(once['媒体(中文)']) == list(twice['媒体(中文)']), '二次归一改动了媒体名'
    assert list(once[d1.COL_WEIGHT]) == list(twice[d2.COL_WEIGHT]), '二次归一改动了权重'


def test_already_normalized_names_untouched():
    """已是正名的行不得被改动 (含刻意的自映射条目)。"""
    canonical = ['21世纪经济报道', '羊城晚报', '读者文摘 - 中文版', '人民日报']
    d = dd.ArticleDeduplicator(config=_cfg(), logger_instance=_NullLogger())
    out = d._prepare_dataframe(_frame(canonical))
    assert list(out['媒体(中文)']) == canonical, '正名被误改'


# ── ④ 阶段 62 的加载路径 ──

def test_stage62_loader_does_not_reapply_overrides_itself():
    """62 号不该自己补 replace —— 归一由去重器统一负责, 避免第 3 处副本漂移。

    (若将来确实要在 62 号内做, 请连同本用例一起改, 并说明为何两处都要。)
    """
    from news_process.validation import dedup_threshold as dt
    src = inspect.getsource(dt._load_pre_dedup_corpus)
    assert 'MEDIA_NAME_OVERRIDES' not in src, (
        '_load_pre_dedup_corpus 自行应用了 override —— 现在归一由 '
        'ArticleDeduplicator._prepare_dataframe 统一兜底, 两处并存会各自漂移。')
