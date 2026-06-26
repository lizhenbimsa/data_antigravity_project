"""W11: Stata run_do 内容寻址跳过的键/路径逻辑 (纯 CPU, 不启 Stata)。"""
from pathlib import Path

from news_process.papers._common import stata_runner as sr


def test_rundo_log_path_strips_do_ext():
    # CF-3: Stata /b do foo.do 写的是 foo.log (去 .do), 不是 foo.do.log。
    assert sr._rundo_log_path(Path("/x/foo.do")).name == "foo.log"


def test_rundo_sidecar_location():
    p = sr._rundo_sidecar(Path("/x/foo.do"))
    assert p.parent.name == "_rundo_cache"   # 落 _rundo_cache/ 不污染模板源树
    assert p.name == "foo.skipstamp.json"


def test_rundo_skip_key_deterministic_and_sensitive(tmp_path):
    do = tmp_path / "t.do"
    do.write_text("di 1\n", encoding="utf-8")
    dta = tmp_path / "d.dta"
    dta.write_text("data1", encoding="utf-8")
    k1 = sr._rundo_skip_key(do, [str(dta)], "Stata.exe")
    assert k1 == sr._rundo_skip_key(do, [str(dta)], "Stata.exe")        # 确定性
    dta.write_text("data2", encoding="utf-8")
    assert sr._rundo_skip_key(do, [str(dta)], "Stata.exe") != k1        # .dta 变 → 键变
    dta.write_text("data1", encoding="utf-8")
    do.write_text("di 2\n", encoding="utf-8")
    assert sr._rundo_skip_key(do, [str(dta)], "Stata.exe") != k1        # .do 变 → 键变


def test_rundo_skip_key_includes_args(tmp_path):
    # F9/TQ-1: args 入键 — 同 do+dta 但不同 args (do 内经 `args` 宏读取) 不应误命中跳过;
    # args=None 与 [] 同键 (无 args 等价)。若回退 F9 (从键删 args) 本测试必红。
    do = tmp_path / "t.do"
    do.write_text("di 1\n", encoding="utf-8")
    dta = tmp_path / "d.dta"
    dta.write_text("data", encoding="utf-8")
    base = sr._rundo_skip_key(do, [str(dta)], "Stata.exe", None)
    assert base == sr._rundo_skip_key(do, [str(dta)], "Stata.exe", [])          # None ≡ [] 无 args
    assert base != sr._rundo_skip_key(do, [str(dta)], "Stata.exe", ["2020"])     # 有 args → 键变
    assert (sr._rundo_skip_key(do, [str(dta)], "Stata.exe", ["2020"])
            != sr._rundo_skip_key(do, [str(dta)], "Stata.exe", ["2021"]))        # 不同 args → 不同键
