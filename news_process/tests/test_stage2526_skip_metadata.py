"""tests/test_stage2526_skip_metadata.py — F22 gate: stage 25/26 的 --skip-unchanged 元数据。

**为何需要 (2026-07-26/27 生产实弹, 两次)**: stage 40 两次失败重试, 每次 orchestrator 都把
stage 25 (2,645s) + stage 26 (6,766s) **整个重跑一遍** —— 合计 2.6 小时纯浪费。根因不是
判据太保守, 而是这两个阶段用裸 ``df.to_parquet()`` 写盘, 产物**根本没有 data_version
schema metadata** ⟹ ``_stage_skip_unchanged_is_safe`` 读不到 input_hashes/config 指纹
⟹ 结构性判定"不可跳过", 与内容是否真的变了无关。

不变量:
  ① stage 25/26 的**全部**登记产物 (OUTPUT_REGISTRY) 都经 save_parquet_with_metadata 写;
  ② 版本号常量住在**零副作用叶模块** —— orchestrator 父进程要 import 它取版本, 若指向
     article_sbert/article_staleness 本体, 父进程 import 会执行 setup_logging 而**截断该
     阶段的生产日志** (2026-07-26 实弹: A/B 脚本 import herd_decay 抹掉了 stage 24 日志);
  ③ stage 25 的输入构造开关 INPUT_STRATEGY 必须**编进**其 code_version —— 否则把开关回退
     到 'bybee400_v1' 再配 --skip-unchanged 会静默沿用 v2 旧产物 (silent staleness);
  ④ INPUT_STRATEGY 单一 SSOT (article_sbert 只 re-export, 不另立字面量)。
"""
from __future__ import annotations

import ast
import importlib
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PKG = os.path.dirname(_HERE)
_PROJECT_PARENT = os.path.dirname(_PKG)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.schemas import OUTPUT_REGISTRY  # noqa: E402

_LEAF = os.path.join(_PKG, 'pipeline', 'text', '_constants.py')
_STAGE_SRC = {
    '25_article_sbert.py': os.path.join(_PKG, 'pipeline', 'text', 'article_sbert.py'),
    '26_article_staleness.py': os.path.join(_PKG, 'pipeline', 'text', 'article_staleness.py'),
}


def _src(path: str) -> str:
    with open(path, encoding='utf-8') as fh:
        return fh.read()


# ── ① 登记产物全部走带元数据的写盘 ──

@pytest.mark.parametrize('script', sorted(_STAGE_SRC))
def test_stage_writes_metadata_for_every_registered_output(script):
    src = _src(_STAGE_SRC[script])
    n_outputs = len(OUTPUT_REGISTRY[script])
    n_calls = src.count('save_parquet_with_metadata(')
    # 减去 import 行本身不计: import 用 `from ... import save_parquet_with_metadata` 无括号
    assert n_calls >= n_outputs, (
        f'{script} 登记了 {n_outputs} 个产物, 但只有 {n_calls} 处 save_parquet_with_metadata 调用 —— '
        f'任一产物缺 data_version 元数据, --skip-unchanged 即整阶段判不可跳, '
        f'每次下游失败重试都会白跑本阶段 (2026-07-26/27 实弹 2.6h/次)。')


@pytest.mark.parametrize('script', sorted(_STAGE_SRC))
def test_no_bare_to_parquet_left_on_registered_outputs(script):
    """裸 to_parquet 不得再出现在写登记产物的位置 (防回退)。"""
    src = _src(_STAGE_SRC[script])
    offenders = [ln.strip() for ln in src.splitlines()
                 if '.to_parquet(' in ln and not ln.strip().startswith('#')]
    assert not offenders, (
        f'{script} 仍有裸 to_parquet 写盘: {offenders} —— 登记产物必须走 '
        f'save_parquet_with_metadata, 否则 --skip-unchanged 失效。')


# ── ② 叶模块零副作用 (父进程 import 安全) ──

def test_leaf_constants_module_has_no_imports_or_side_effects():
    tree = ast.parse(_src(_LEAF))
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == '__future__':
            continue
        assert not isinstance(node, (ast.Import, ast.ImportFrom)), (
            f'_constants.py 出现 import ({ast.dump(node)[:80]}) —— 本模块由 orchestrator '
            f'**父进程** import 取 code_version; 任何连带 import 都可能触发 setup_logging '
            f'而截断该阶段的生产日志, 或白付 load_config/嵌入引擎的开销。')
        assert isinstance(node, (ast.Assign, ast.AnnAssign, ast.Expr)), (
            f'_constants.py 只准放字面常量赋值, 出现了 {type(node).__name__} —— '
            f'任何函数/类/语句都是潜在副作用。')


def test_leaf_constants_import_is_truly_isolated():
    """真 import 一次, 断言没有连带拉起 article_* / core 模块。"""
    for m in [k for k in list(sys.modules) if k.startswith('news_process.pipeline.text')]:
        del sys.modules[m]
    before = set(sys.modules)
    importlib.import_module('news_process.pipeline.text._constants')
    pulled = {m for m in set(sys.modules) - before
              if m.startswith('news_process.') and not m.endswith('_constants')}
    # 允许包 __init__ (news_process.pipeline.text 等命名空间), 不允许实体模块
    heavy = {m for m in pulled if m.rsplit('.', 1)[-1] not in
             ('news_process', 'pipeline', 'text', 'core')}
    assert not heavy, f'import 叶模块连带拉起了实体模块: {sorted(heavy)}'


# ── ③④ 版本号编进开关 + SSOT 唯一 ──

def test_sbert_code_version_embeds_input_strategy():
    c = importlib.import_module('news_process.pipeline.text._constants')
    assert c.INPUT_STRATEGY in c.SBERT_CODE_VERSION, (
        f'SBERT_CODE_VERSION={c.SBERT_CODE_VERSION!r} 未包含 INPUT_STRATEGY='
        f'{c.INPUT_STRATEGY!r} —— 二者一旦可分离, 「回退开关 + --skip-unchanged」'
        f'就会静默沿用旧口径产物 (silent staleness)。')
    assert c.INPUT_STRATEGY in c.VALID_STRATEGIES


def test_input_strategy_has_single_literal_source():
    """article_sbert 不得再自立 INPUT_STRATEGY 字面量 (只准 re-export 叶模块)。"""
    src = _src(_STAGE_SRC['25_article_sbert.py'])
    bad = [ln.strip() for ln in src.splitlines()
           if ln.startswith('INPUT_STRATEGY') and ('"' in ln or "'" in ln)
           and '_CONST' not in ln]
    assert not bad, (
        f'article_sbert.py 出现字面量 INPUT_STRATEGY 定义: {bad} —— '
        f'SSOT 在 pipeline/text/_constants.py, 此处只准 re-export。')


def test_orchestrator_registers_both_stages_in_code_version_gate():
    from news_process.run_pipeline_function import (
        STAGE_CODE_VERSION,
        STAGE_CONFIG_FILES,
    )
    for script in _STAGE_SRC:
        assert script in STAGE_CONFIG_FILES, f'{script} 未登记 STAGE_CONFIG_FILES → 永不跳过'
        assert script in STAGE_CODE_VERSION, (
            f'{script} 未登记 STAGE_CODE_VERSION → 纯代码逻辑变更不会失效跳过')
        mod, attr = STAGE_CODE_VERSION[script]
        assert mod.endswith('_constants'), (
            f'{script} 的 code_version 指向 {mod} —— 必须指向零副作用叶模块, '
            f'否则 orchestrator 父进程 import 会截断该阶段生产日志。')
        assert getattr(importlib.import_module(mod), attr, None), (
            f'{mod}.{attr} 解析不到值 → orchestrator 会保守重跑, 整改失效')
