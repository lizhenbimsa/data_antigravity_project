"""
tests/test_llmsdic_judge_reps.py — 盲审三轮 self-consistency + 过半数门槛 专属断言
==================================================================================

背景 (LLMSDIC_JUDGE_TRIPLE_SELFCONSISTENCY_EXECUTION_PLAN_2026-07-21.md §5.3):
2026-07-21 判别协议升级——每家模型每批独立盲审 NUM_JUDGE_REPS=3 轮 (缓存 tag 带轮序号
judge|rep{r}|try{n}, 方案 B 统一命名), 模型内 ≥2/3 轮多数聚成正式票, 模型间入选门槛
回调为严格过半数 (> len(JUDGE_MODELS) * 0.5, 13 家 → ≥7 票)。

守门点 (每条对应一个真实失败模式):
- (a) 缓存 tag 防折叠: 三轮 tag 两两互异且与 legacy tag 互异——否则 temperature=0
  同 prompt 三轮折叠成同一缓存条目, 内部投票沦为假投票 (恒 3:0)。
- (b) 投票函数 2-of-3 边界 (含缺轮保守语义)。
- (c) 门槛表达式为 `> len(JUDGE_MODELS) * 0.5` 严格形态且旧 2/3 表达式不残留。
- (d) manifest v1/v2 双版本: 00 脚本与验钞机须同时认两代 schema (历史核验链不断)。
- (e) 02_analyze_log 判别正则新旧 task_id 双格式命中 (防判别统计静默归零)。
- (f) config 协议常量自洽 (奇数轮 → 永无平票; 多数门由轮数唯一决定)。

⚠ 设计约束 (沿用 test_prompt_audit_s2_s12.py 的既有纪律): 绝不 import
00_LLMs_for_dic.py 本体 (模块顶层建缓存/注册信号处理器)。config.py / llm_cache.py
无此类副作用, 经 importlib 以唯一模块名从磁盘加载做行为断言; 其余用纯文本结构断言。
"""

from __future__ import annotations

import importlib.util
import re
import textwrap
from pathlib import Path

import pytest

pytestmark = pytest.mark.fast

_NEWS_PROCESS_DIR = Path(__file__).resolve().parent.parent
_DIC_DIR = _NEWS_PROCESS_DIR / "LLMs_for_FinTech_dic"
_MAIN_SRC_PATH = _DIC_DIR / "00_LLMs_for_dic.py"
_LOG_SRC_PATH = _DIC_DIR / "02_analyze_log.py"
_CONFIG_SRC_PATH = _DIC_DIR / "config.py"
_CACHE_SRC_PATH = _DIC_DIR / "llm_cache.py"
_VERIFY_SRC_PATH = _DIC_DIR / "verify_judge_cache_coverage.py"


def _read(path: Path) -> str:
    assert path.exists(), f"源文件缺失，断言基础不成立: {path}"
    return path.read_text(encoding="utf-8")


def _load_module(name: str, path: Path):
    """唯一模块名 + 磁盘路径加载，不动 sys.path（防与主项目同名目录/模块冲突）。"""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# (a) 缓存 tag 防折叠
# ---------------------------------------------------------------------------

def test_rep_tags_never_fold_in_cache_key():
    """三轮 tag 与 legacy tag 在 LLMCache.make_key 下四键互异（同模型同 prompt 同温度）。"""
    cache_mod = _load_module("_llmsdic_cache_reps", _CACHE_SRC_PATH)
    make_key = cache_mod.LLMCache.make_key
    prompt = "同一批词的同一判别 prompt"
    keys = [
        make_key("some-model", prompt, "0", tag)
        for tag in ("judge|try0", "judge|rep0|try0", "judge|rep1|try0", "judge|rep2|try0")
    ]
    assert len(set(keys)) == 4, (
        "缓存键折叠: 轮序号未有效区分缓存槽位——三轮会重放同一响应, 内部投票沦为假投票"
    )


def test_judge_batch_has_rep_and_legacy_tag_branches():
    """judge_batch 须同时具备 rep tag (judge|rep{r}) 与 legacy tag (rep=None) 两分支。

    legacy 分支是历史 v1 manifest 冻结重放的 $0 复现锚 (方案 B 下旧缓存条目保留不删)。
    """
    src = _read(_MAIN_SRC_PATH)
    assert '"judge" if rep is None else f"judge|rep{rep}"' in src, (
        "缺 rep/legacy 双分支 tag 选择——要么三轮折叠, 要么 v1 冻结重放失锚"
    )
    # audit 键与真实 cache_tag 必须同构 (同一 _audit_tag 变量喂 make_key 与 cache_tag)
    assert "cache_tag=_audit_tag" in src, (
        "_audit_tag 与 _call_llm_with_retry 的 cache_tag 不同源——manifest 键将与真实缓存键漂移"
    )


# ---------------------------------------------------------------------------
# (b) 模型内投票函数 2-of-3 边界
# ---------------------------------------------------------------------------

def _extract_rep_vote() -> callable:
    """从 00 源码截取 _rep_vote 函数体, 在沙盒内 exec (majority 为显式参数, 评审A 修复后)。"""
    src = _read(_MAIN_SRC_PATH)
    m = re.search(r"def _rep_vote\(scores.*?\n(?:    .*\n|\n)*?    return [^\n]+\n", src)
    assert m is not None, "未找到 _rep_vote 函数定义，源码结构已变化"
    func_src = textwrap.dedent(m.group(0))
    func_src = re.sub(
        r"def _rep_vote\([^)]*\)\s*->\s*int:", "def _rep_vote(scores, majority):",
        func_src, count=1,
    )
    namespace: dict = {}
    exec(compile(func_src, "<rep_vote_block>", "exec"), namespace)  # noqa: S102
    return namespace["_rep_vote"]


def test_rep_vote_two_of_three_boundaries():
    """2-of-3 多数边界: 2/3 票=1、1/3 票=0、全同显然; 缺轮按 0 计 (保守方向)。"""
    vote = _extract_rep_vote()
    assert vote([1, 1, 1], 2) == 1
    assert vote([1, 1, 0], 2) == 1, "2/3 多数应成票"
    assert vote([1, 0, 0], 2) == 0, "1/3 少数不应成票"
    assert vote([0, 0, 0], 2) == 0
    # 缺轮语义 (该轮 hard_fail/聚合缺格 → 少一个元素): 只剩 1 票时绝不能过 2 票门
    assert vote([1, 1], 2) == 1, "两轮全 1 (第三轮缺) 已达多数门, 应成票"
    assert vote([1], 2) == 0, "单轮 1 (两轮缺) 不足多数门, 缺轮不得把词投成 1"
    assert vote([], 2) == 0
    # 冻结门穿透语义 (评审A): 同一轮分在不同 majority 下结果不同 → 门必须显式传入
    assert vote([1, 1, 0], 3) == 0, "门=3 (五轮协议) 时 2:1 不应成票"
    assert vote([1, 1, 1], 3) == 1


def test_replay_freezes_rep_majority_from_manifest():
    """评审A 修复锚: v2 冻结重放必须消费 manifest 的 rep_majority (写而不读=复现假证书)。"""
    src = _read(_MAIN_SRC_PATH)
    assert 'manifest.get("rep_majority"' in src, (
        "冻结重放未读取 manifest.rep_majority——config 轮数协议演进后, 历史 v2 manifest "
        "重放的投票门将静默漂移且判决照旧盖「可复现」(评审A major)"
    )
    assert "rep_majority=frozen_majority" in src, (
        "frozen_majority 未穿透到 _build_judge_dataframe/_write_judge_manifest——"
        "重放投票门仍用活体 config 或重放 manifest 落盘自相矛盾协议存根"
    )


def test_judge_score_domain_enforced():
    """评审B 修复锚: 解析处须有 0/1 域强制 (越界整数按坏项跳过, 不得进 result_map)。"""
    src = _read(_MAIN_SRC_PATH)
    assert re.search(r"if sc not in \(0, 1\):", src), (
        "判别 score 解析缺 0/1 域强制——越界整数 (如字段错置的 3) 会经 sum 过门"
        "伪造/否决模型内多数 (评审B)"
    )


# ---------------------------------------------------------------------------
# (c) 入选门槛: 严格过半数形态
# ---------------------------------------------------------------------------

def test_threshold_is_strict_half_and_no_two_thirds_residue():
    """门槛须为 `> len(JUDGE_MODELS) * 0.5` (13 家 → ≥7 票); 旧 2/3 可执行表达式零残留。"""
    src = _read(_MAIN_SRC_PATH)
    assert re.search(
        r'df_final\["total_score"\]\s*>\s*len\(JUDGE_MODELS\)\s*\*\s*0\.5', src
    ), "入选门槛不是严格过半数 `> len(JUDGE_MODELS) * 0.5` 形态 (2026-07-21 用户裁定)"
    assert not re.search(
        r'total_score"\]\s*>\s*len\(JUDGE_MODELS\)\s*\*\s*2\s*/\s*3', src
    ), "旧 2/3 门槛表达式仍残留 (只允许注释台账保留历史记述)"
    # _min_pass 须为过半数口径 (len // 2 + 1), 不得残留 2/3 口径 (len * 2 // 3 + 1)
    assert "len(JUDGE_MODELS) // 2 + 1" in src, "_min_pass 未切过半数口径"
    assert "len(JUDGE_MODELS) * 2 // 3 + 1" not in src, "_min_pass 残留 2/3 口径"


# ---------------------------------------------------------------------------
# (d) manifest 双版本
# ---------------------------------------------------------------------------

def test_manifest_dual_schema_everywhere():
    """00 脚本与验钞机均须同时认 v1/v2 两代 schema; v2 协议冻结字段齐全。"""
    for path in (_MAIN_SRC_PATH, _VERIFY_SRC_PATH):
        src = _read(path)
        assert "llmsdic-judge-manifest/v1" in src, f"{path.name} 丢失 v1 schema 兼容 (历史核验链断)"
        assert "llmsdic-judge-manifest/v2" in src, f"{path.name} 缺 v2 schema 支持"
    main_src = _read(_MAIN_SRC_PATH)
    for field in ('"n_judge_reps"', '"rep_majority"', '"final_vote_threshold"'):
        assert field in main_src, f"manifest v2 缺协议冻结字段 {field}"


# ---------------------------------------------------------------------------
# (e) 02_analyze_log 判别正则双格式命中
# ---------------------------------------------------------------------------

def _extract_regexes(varnames: list[str]) -> dict[str, re.Pattern]:
    src = _read(_LOG_SRC_PATH)
    out: dict[str, re.Pattern] = {}
    for name in varnames:
        m = re.search(rf'{name}\s*=\s*re\.search\(\s*\n?\s*r"([^"]+)"', src)
        assert m is not None, f"未找到 {name} 正则定义，02_analyze_log.py 结构已变化"
        out[name] = re.compile(m.group(1))
    return out


def test_analyze_log_judge_regexes_match_old_and_new_task_ids():
    """三条判别正则须命中旧 (无轮) 与新 (带 /轮R) 两代 task_id——失配即判别统计静默归零。"""
    regexes = _extract_regexes(["m_judge_success", "m_judge_fail", "m_judge_retry"])
    samples = {
        "m_judge_success": (
            "[2026-07-21 10:00:00] [INFO]   [判别-glm-5.2/批次3] 成功判别 100/100 个词",
            "[2026-07-21 10:00:00] [INFO]   [判别-glm-5.2/批次3/轮2] 成功判别 100/100 个词",
        ),
        "m_judge_fail": (
            "[2026-07-21 10:00:01] [ERROR]   [判别-glm-5.2/批次3] 失败，全部标记为0",
            "[2026-07-21 10:00:01] [ERROR]   [判别-glm-5.2/批次3/轮2] 失败，全部标记为0",
        ),
        "m_judge_retry": (
            "[2026-07-21 10:00:02] [WARNING]   [判别-glm-5.2/批次3] 重试 1/100: timeout",
            "[2026-07-21 10:00:02] [WARNING]   [判别-glm-5.2/批次3/轮2] 重试 1/100: timeout",
        ),
    }
    for name, (old_line, new_line) in samples.items():
        pat = regexes[name]
        m_old, m_new = pat.search(old_line), pat.search(new_line)
        assert m_old is not None, f"{name} 丢失旧格式兼容 (历史日志将统计归零)"
        assert m_new is not None, f"{name} 未命中带 /轮R 的新 task_id (新日志将统计归零)"
        assert m_old.group(1) == m_new.group(1) == "glm-5.2", (
            f"{name} 模型名捕获组被 /轮 后缀污染: {m_old.group(1)!r} vs {m_new.group(1)!r}"
        )


# ---------------------------------------------------------------------------
# (f) config 协议常量自洽
# ---------------------------------------------------------------------------

def test_config_rep_constants_consistent():
    """NUM_JUDGE_REPS=3 (奇数→模型内永无平票); JUDGE_REP_MAJORITY 由轮数唯一决定 (=2)。"""
    cfg = _load_module("_llmsdic_config_reps", _CONFIG_SRC_PATH)
    assert cfg.NUM_JUDGE_REPS == 3, "轮数偏离 2026-07-21 用户裁定的 3 轮协议"
    assert cfg.NUM_JUDGE_REPS % 2 == 1, "轮数必须为奇数, 否则模型内 0/1 投票存在平票"
    assert cfg.JUDGE_REP_MAJORITY == cfg.NUM_JUDGE_REPS // 2 + 1 == 2, (
        "内部多数门须由轮数唯一决定 (// 2 + 1), 不得手改脱钩"
    )
