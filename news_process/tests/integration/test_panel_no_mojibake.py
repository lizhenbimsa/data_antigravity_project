"""tests/integration/test_panel_no_mojibake.py — v3.7.3 Plan A v1.0 (v1.0.2 更正)。

NEW-B1 状态: **2026-05-26 执行期内已更正为假警报**。

最初的疑虑 (已被推翻)
==========================
Plan A 初验时, 通过 PowerShell 查看 ``data/processed/40_panel_yearly.parquet``
的列名, 看似含 ``����`` 乱码序列 (如 ``finbert_cn_����_w_sum_full``),
当时被误判为 GBK/UTF-8 双重编码污染。

实际结论 (经 Unicode 码位扫描验证)
====================================================
这些列名包含的是**合法 UTF-8 中文字符** (不是 U+FFFD 替换字符)。
码位扫描结果:
    0x6b63 = 正 (zhèng, "positive")
    0x9762 = 面 (miàn, "side")
    0x8d1f = 负 (fù, "negative")

即真实列名是 ``finbert_cn_正面_w_sum_full`` / ``finbert_cn_负面_w_sum_full``
等。PowerShell 默认 GBK 代码页无法渲染这些 UTF-8 中文字符, 才显示成
``����``。这是**终端渲染假象, 不是数据污染**。

本测试自带的 ``_detect_mojibake_columns`` helper 防的是未来**真正的**
U+FFFD 乱码; 这与中文列名是两回事 — 中文列名是合法 UTF-8, 且下游 .dta
导出由 ``stata_export.py`` 的 rename 层 (v3.5.2+) 正确处理。

本测试验证:
1. panel 没有任何 U+FFFD 乱码列 (即最初的怀疑点)。
2. 中文字符列存在 (信息性检查; 不算失败)。
3. 模式与 v3.5.2 LM 4 子词典 sentiment label 编码一致。

白话: 当年以为列名乱码了, 其实只是终端显示不了中文。这个测试留着,
是为了万一以后真出现乱码字符 (U+FFFD) 能第一时间报警。
"""
from __future__ import annotations

from pathlib import Path

import pytest

pd = pytest.importorskip("pandas", reason="pandas required for panel scan")

# 待扫描的 panel 文件 (相对仓库根)。stage 45 / stage 51 的全部已知 parquet
# 产物。磁盘上存在的逐个独立扫描; 文件缺失不算错误 (CI 可能无磁盘 panel)。
PANEL_FILES = [
    "data/processed/40_panel_yearly.parquet",
    "data/processed/51_panel_with_controls.parquet",
]


def _detect_mojibake_columns(panel: pd.DataFrame) -> list[str]:
    """返回含 U+FFFD 或 ``����`` 序列的列名。"""
    return [c for c in panel.columns
            if "�" in c or "����" in c]


@pytest.fixture(scope="module")
def panel_columns_by_file() -> dict[str, list[str]]:
    """每个 panel 文件只加载一次, 返回各文件的乱码列名列表。

    不存在的文件跳过 (允许 CI 环境无 panel 磁盘产物)。
    """
    results = {}
    for rel_path in PANEL_FILES:
        path = Path(rel_path)
        if not path.exists():
            continue
        try:
            panel = pd.read_parquet(path)
        except Exception as e:
            pytest.skip(f"cannot read {rel_path}: {e}")
        results[rel_path] = _detect_mojibake_columns(panel)
    return results


def test_at_least_one_panel_file_exists(panel_columns_by_file):
    """sanity 检查: 至少扫到 1 个 panel 文件 (否则本测试无数据可验)。"""
    if not panel_columns_by_file:
        pytest.skip("no panel files found — CI without disk artifacts")
    assert len(panel_columns_by_file) >= 1


def test_panel_columns_have_no_mojibake(panel_columns_by_file):
    """严格检查: 任何 panel 列名都不得含 U+FFFD 替换字符。

    NEW-B1 v1.0.2 更正: 已验证 panel 中 U+FFFD 乱码为 0; 最初在
    PowerShell 输出里看到的 ``����`` 是合法 UTF-8 中文字符的
    终端渲染假象。
    """
    all_mojibake = {}
    for file_path, mojibake_cols in panel_columns_by_file.items():
        if mojibake_cols:
            all_mojibake[file_path] = mojibake_cols

    assert not all_mojibake, (
        f"NEW (post-v1.0.2): panel files have REAL U+FFFD mojibake columns: "
        f"{ {k: len(v) for k, v in all_mojibake.items()} }; "
        f"first 5 examples per file: "
        f"{ {k: v[:5] for k, v in all_mojibake.items()} }; "
        f"this is a regression — investigate stage 22/23 encoding output."
    )


def test_panel_has_expected_chinese_columns(panel_columns_by_file):
    """诊断性检查 (信息性): panel 含约 100+ 个中文字符列
    (v3.5.2+ LM 4 子词典 sentiment labels)。这不是乱码;
    是合法 UTF-8 中文词典标签 (正面/负面 等)。

    已验证码位: 0x6b63 (正) / 0x9762 (面) / 0x8d1f (负)。

    .dta 导出时的中文→ASCII rename 由 stata_export.py 负责
    (规避 Stata 变量名约束); 本测试只验证 panel 侧中文列
    按预期存在。
    """
    for file_path, _ in panel_columns_by_file.items():
        path = Path(file_path)
        panel = pd.read_parquet(path)
        chinese_cols = [c for c in panel.columns
                        if any(0x4e00 <= ord(ch) <= 0x9fff for ch in c)]
        # 预期 ≥ 50 (v3.5.2+ LM 4 子词典 × 多种权重 × 多轨)
        assert len(chinese_cols) >= 50 or len(chinese_cols) == 0, (
            f"{file_path}: unexpected Chinese column count {len(chinese_cols)}; "
            f"v3.5.2+ baseline is ≥ 50 (or 0 if pre-v3.5.2 panel). "
            f"Sample: {chinese_cols[:3]}"
        )
