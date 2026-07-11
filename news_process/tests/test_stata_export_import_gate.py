"""test_stata_export_import_gate — §0 铁律 AST 级防线: 导出路径不 import/调用组装器.

P1 整改 (2026-07-11): 旧 regex gate (test_codebook_longdesc.py::
test_export_paths_do_not_import_composer) 对 repo 惯用形态双层可绕 (评审探针实证):
    ① import 面: `from news_process.pipeline.panel import codebook_longdesc`
       (codebook.py 自身即此写法) 三个行首锚定分支全 miss;
    ② 调用面: 只查带下划线 '_compose_long_description(' 子串, 而叶模块公开函数名
       是无下划线的 compose_long_description → `codebook_longdesc.compose_long_description(...)`
       不含该子串。
本 gate 改 **AST 级**: ast.parse 提取全部 Import/ImportFrom/Name/Attribute/Call,
任何形态引用 codebook_longdesc 模块或 compose_long_description /
_compose_long_description 函数均 fail; 注释/docstring 的声明性提及天然豁免
(注释不进 AST, docstring 是 Constant 不是 Name/Attribute)。含反例自测
(checker 对全部已知绕过形态必须报警) — 防线自身的防线。

违规后果 (评审复核确认): 组装器 SystemExit ⊄ Exception → stata_export.py 的
except Exception 捕不到, stage 40/46/51 全崩 (§0 铁律的存在理由)。
"""
from __future__ import annotations

import ast
import os
from typing import List

import pytest

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

#: 三条导出链 (与旧 regex gate 同域): stage 46 / 40 / 51 的 dta 写路径
_EXPORT_PATH_FILES = (
    os.path.join(_REPO, 'pipeline', 'panel', 'stata_export.py'),
    os.path.join(_REPO, 'pipeline', 'panel', 'export.py'),
    os.path.join(_REPO, 'pipeline', 'falsification', 'controls.py'),
)

_FORBIDDEN_MODULE = 'codebook_longdesc'
_FORBIDDEN_FUNCS = frozenset({'compose_long_description', '_compose_long_description'})


def find_composer_references(source: str) -> List[str]:
    """返回 source 中对组装器 (模块/函数) 的全部真实引用 (import + 调用面).

    AST 级 → 注释天然豁免; docstring 是 ast.Constant, 不会被 Name/Attribute/
    Import 检查误伤。额外覆盖字符串动态 import 通道: Call 实参中的字符串常量
    含模块名即报 (importlib.import_module / __import__ 形态)。
    """
    tree = ast.parse(source)
    hits: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if _FORBIDDEN_MODULE in a.name.split('.'):
                    hits.append(f'L{node.lineno}: import {a.name}')
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ''
            if _FORBIDDEN_MODULE in mod.split('.'):
                hits.append(f'L{node.lineno}: from {mod} import ...')
            for a in node.names:
                if a.name == _FORBIDDEN_MODULE or a.name in _FORBIDDEN_FUNCS:
                    hits.append(f'L{node.lineno}: from {mod or "."} import {a.name}')
        elif isinstance(node, ast.Attribute):
            if node.attr in _FORBIDDEN_FUNCS or node.attr == _FORBIDDEN_MODULE:
                hits.append(f'L{node.lineno}: 属性引用 .{node.attr}')
        elif isinstance(node, ast.Name):
            if node.id in _FORBIDDEN_FUNCS or node.id == _FORBIDDEN_MODULE:
                hits.append(f'L{node.lineno}: 名字引用 {node.id}')
        elif isinstance(node, ast.Call):
            # 动态 import 通道: importlib.import_module('…codebook_longdesc') / __import__
            for arg in list(node.args) + [kw.value for kw in node.keywords]:
                if (isinstance(arg, ast.Constant) and isinstance(arg.value, str)
                        and _FORBIDDEN_MODULE in arg.value):
                    hits.append(f'L{node.lineno}: 调用实参字符串含 {_FORBIDDEN_MODULE!r}')
    return hits


class TestExportPathsAstGate:
    @pytest.mark.parametrize('path', _EXPORT_PATH_FILES,
                             ids=[os.path.basename(p) for p in _EXPORT_PATH_FILES])
    def test_export_path_file_free_of_composer(self, path):
        src = open(path, encoding='utf-8').read()
        hits = find_composer_references(src)
        assert not hits, (
            f'{os.path.basename(path)}: 导出路径引用了组装器 (§0 铁律; SystemExit '
            f'⊄ Exception, 会把 stage 40/46/51 打崩): {hits[:10]}')


class TestCheckerCatchesKnownBypasses:
    """反例自测: 旧 regex gate 漏掉的全部形态, AST checker 必须逐一报警."""

    @pytest.mark.parametrize('snippet', [
        # ① 旧 gate 实证漏掉的 repo 惯用形态 (codebook.py 自身写法)
        'from news_process.pipeline.panel import codebook_longdesc\n',
        'from news_process.pipeline.panel import codebook_longdesc as cl\n',
        'from . import codebook_longdesc\n',
        # ② 公开函数名 (无下划线) 的 from-import 与调用
        'from news_process.pipeline.panel.codebook_longdesc import compose_long_description\n',
        'x = codebook_longdesc.compose_long_description(col, panel, lib)\n',
        'y = compose_long_description(col)\n',
        # ③ 旧 gate 能抓的形态 (回归保底)
        'import news_process.pipeline.panel.codebook_longdesc as cl\n',
        'from .codebook import _compose_long_description\n',
        'z = mod._compose_long_description(col)\n',
        # ④ 动态 import 通道
        "import importlib\nm = importlib.import_module('news_process.pipeline.panel.codebook_longdesc')\n",
        "m = __import__('news_process.pipeline.panel.codebook_longdesc')\n",
    ])
    def test_violation_snippet_flagged(self, snippet):
        assert find_composer_references(snippet), f'checker 漏报: {snippet!r}'

    @pytest.mark.parametrize('snippet', [
        # 声明性提及豁免: 注释与 docstring 不构成引用
        '# 刻意不 import codebook_longdesc._compose_long_description (铁律)\nx = 1\n',
        '"""§0: 导出路径不 import 组装器 (_compose_long_description), 经 json 消费。"""\n',
        # 近邻合法 import 不误伤
        'from news_process.pipeline.panel import codebook\n',
        'from news_process.pipeline.panel.codebook import get_variable_metadata_dict\n',
        'label = compose_something_else(col)\n',
    ])
    def test_legit_snippet_not_flagged(self, snippet):
        assert find_composer_references(snippet) == [], f'checker 误报: {snippet!r}'


if __name__ == '__main__':
    raise SystemExit(pytest.main([__file__, '-v']))
