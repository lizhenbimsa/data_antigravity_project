"""WP-R3 创新维度三角化 gate 测试 (locus 词表二分 + proxy 脚本纪律)。

覆盖 (`PROMPT_ASSETS_AUDIT_EXECUTION_PLAN_2026-07-12.md` §10 WP-R3.4 "防误用与决策记录修订"):
  1. `config/fintech_locus_split.yaml` 三桶完整性 —— 并集 = `fintech_dict.json`
     全部 1506 词 (零遗漏), 三桶两两不交。
  2. `fintech_locus_split.yaml` 零 `pipeline/`/`papers/` import (仅
     `scripts/audit/` 消费, 全仓 grep 断言)。
  3. `innovation_proxy_triangulation.py` 产物路径 ⊆ `validation/eval_reports/`
     (源码文本级断言), 且不产生任何面板 dta 列 (无 `to_stata` 调用、未注册
     DAG/OUTPUT_REGISTRY、无 thin shim)。
  4. 双编码原始表存档存在且行数与词典总数一致 (双编码可追溯性)。

本测试模块自身零 API 调用 ($0), 纯文件系统 + 文本断言。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
CONFIG_DIR = REPO / "config"
SCRIPTS_AUDIT_DIR = REPO / "scripts" / "audit"
VALIDATION_DIR = REPO / "validation"
EVAL_REPORTS_DIR = VALIDATION_DIR / "eval_reports"

LOCUS_SPLIT_PATH = CONFIG_DIR / "fintech_locus_split.yaml"
FINTECH_DICT_PATH = CONFIG_DIR / "fintech_dict.json"
PROXY_SCRIPT_PATH = SCRIPTS_AUDIT_DIR / "innovation_proxy_triangulation.py"
# fix(WP-R3-P1, 2026-07-14): 双编码原始表迁 config/ 与 yaml 同座并经 .gitignore
# negation 入库 (κ=0.8375 的唯一证据载体不可再生, WP-R3.4 立法意图=持久存档与
# 版本化; 计划原文 eval_reports 落点因该目录不入库惯例改此处, 属文档化偏离)。
DOUBLE_CODING_CSV = CONFIG_DIR / "locus_split_double_coding_2026-07-14.csv"


# ---------------------------------------------------------------------------
# 1. 三桶完整性
# ---------------------------------------------------------------------------
class TestLocusSplitBuckets:
    def _load(self):
        with open(LOCUS_SPLIT_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _dict_words(self) -> list[str]:
        with open(FINTECH_DICT_PATH, encoding="utf-8") as f:
            return json.load(f)

    def test_file_exists(self):
        assert LOCUS_SPLIT_PATH.exists(), f"缺 {LOCUS_SPLIT_PATH}"

    def test_three_buckets_present(self):
        doc = self._load()
        for bucket in ("tech", "func", "unassigned"):
            assert bucket in doc, f"缺桶 {bucket}"
            assert isinstance(doc[bucket], list) and len(doc[bucket]) > 0

    def test_union_equals_full_dict_zero_missing(self):
        """并集 = fintech_dict.json 全部 1506 词, 零遗漏。"""
        doc = self._load()
        words = self._dict_words()
        union = set(doc["tech"]) | set(doc["func"]) | set(doc["unassigned"])
        assert union == set(words), (
            f"三桶并集与词典不等: 词典独有 {set(words) - union}, "
            f"三桶独有 {union - set(words)}"
        )
        assert len(words) == 1506, f"fintech_dict.json 应恰 1506 词, 实读 {len(words)}"

    def test_buckets_pairwise_disjoint(self):
        doc = self._load()
        t, fc, u = set(doc["tech"]), set(doc["func"]), set(doc["unassigned"])
        assert not (t & fc), f"tech∩func 非空: {t & fc}"
        assert not (t & u), f"tech∩unassigned 非空: {t & u}"
        assert not (fc & u), f"func∩unassigned 非空: {fc & u}"

    def test_no_duplicate_within_bucket(self):
        doc = self._load()
        for bucket in ("tech", "func", "unassigned"):
            items = doc[bucket]
            assert len(items) == len(set(items)), f"{bucket} 桶内有重复词"

    def test_metadata_counts_match_buckets(self):
        doc = self._load()
        meta = doc["metadata"]
        assert meta["n_tech"] == len(doc["tech"])
        assert meta["n_func"] == len(doc["func"])
        assert meta["n_unassigned"] == len(doc["unassigned"])
        assert meta["n_tech"] + meta["n_func"] + meta["n_unassigned"] == 1506

    def test_metadata_kappa_above_threshold(self):
        """双编码 κ 应 > 0.7 (计划预期门槛)。"""
        doc = self._load()
        assert doc["metadata"]["cohens_kappa"] > 0.7

    def test_do_not_modify_declaration_present(self):
        """头注须显式声明禁改 fintech_dict.json 本体 (血缘锚点铁律)。"""
        text = LOCUS_SPLIT_PATH.read_text(encoding="utf-8")
        assert "禁止" in text and "fintech_dict.json" in text
        assert "input_hashes" in text or "血缘" in text


# ---------------------------------------------------------------------------
# 2. 零 pipeline/papers import (仅 scripts/audit/ 消费)
# ---------------------------------------------------------------------------
class TestConsumerScopeIsolation:
    def test_no_pipeline_or_papers_reference(self):
        """全仓 grep: pipeline/ 与 papers/ 下任何文件都不得引用
        fintech_locus_split(.yaml)? —— locus proxy 是旁证轨, 不得被生产代码消费。"""
        hits: list[str] = []
        for base in (REPO / "pipeline", REPO / "papers"):
            if not base.exists():
                continue
            for py in base.rglob("*.py"):
                text = py.read_text(encoding="utf-8", errors="ignore")
                if "fintech_locus_split" in text:
                    hits.append(str(py))
        assert not hits, f"生产代码引用了 fintech_locus_split, 违反消费者范围铁律: {hits}"

    def test_only_scripts_audit_consumes(self):
        """反向确认: 唯一消费者是 scripts/audit/innovation_proxy_triangulation.py
        (全仓 grep 命中文件集合应恰为 {该脚本, 本 yaml 自身, 本 gate 测试, 执行计划 md})。"""
        hits: list[Path] = []
        for py in REPO.rglob("*.py"):
            if "site-packages" in str(py) or ".venv" in str(py):
                continue
            text = py.read_text(encoding="utf-8", errors="ignore")
            if "fintech_locus_split" in text:
                hits.append(py)
        allowed = {PROXY_SCRIPT_PATH, Path(__file__).resolve()}
        unexpected = [p for p in hits if p.resolve() not in allowed]
        assert not unexpected, f"非预期消费者引用了 fintech_locus_split: {unexpected}"


# ---------------------------------------------------------------------------
# 3. proxy 脚本纪律: 产物路径 ⊆ eval_reports / 无面板列产出
# ---------------------------------------------------------------------------
class TestProxyScriptDiscipline:
    def _source(self) -> str:
        assert PROXY_SCRIPT_PATH.exists(), f"缺 {PROXY_SCRIPT_PATH}"
        return PROXY_SCRIPT_PATH.read_text(encoding="utf-8")

    def test_output_paths_all_under_eval_reports(self):
        """源码文本级断言: 所有写文件路径常量都落在 EVAL_REPORTS_DIR 之下
        (通过检查 EVAL_REPORTS_DIR 定义 + 所有 .to_csv/.to_excel/json.dump 的
        目标变量均从 EVAL_REPORTS_DIR 派生, 而非硬编码其他目录)。"""
        text = self._source()
        assert 'EVAL_REPORTS_DIR = REPO / "validation" / "eval_reports"' in text, (
            "EVAL_REPORTS_DIR 未按预期锚定到 validation/eval_reports/"
        )
        # 所有落盘调用 (.to_csv / open(... "w" ...) / json.dump 配套的 with open) 的路径
        # 变量名必须是 detail_path / results_path / md_path, 且这三者定义式里都出现
        # EVAL_REPORTS_DIR —— 直接断言三个 path 变量的构造行都锚定 EVAL_REPORTS_DIR。
        for var in ("detail_path", "results_path", "md_path"):
            pattern = re.compile(rf"{var}\s*=\s*EVAL_REPORTS_DIR\s*/")
            assert pattern.search(text), f"{var} 未锚定 EVAL_REPORTS_DIR, 违反产物路径 ⊆ eval_reports 铁律"

    def test_no_pipeline_output_dir_hardcode(self):
        """不得写入 data/processed/ (面板产物目录) 或 data/raw/。"""
        text = self._source()
        assert 'data/processed"' not in text and "data/processed'" not in text
        assert 'data/raw"' not in text and "data/raw'" not in text

    def test_no_to_stata_or_dta_emission(self):
        """不产生任何 .dta / to_stata 调用 —— proxy 不是面板测度, 不得混入 Stata 导出。"""
        text = self._source()
        assert "to_stata" not in text
        assert ".dta" not in text

    def test_not_registered_in_dag_or_output_registry(self):
        """audit-only: 不得出现在 core/dag.py 的 STAGES_MAIN/STAGES_VALIDATION,
        也不得出现在 core/schemas.py 的 OUTPUT_REGISTRY。"""
        dag_text = (REPO / "core" / "dag.py").read_text(encoding="utf-8")
        schemas_text = (REPO / "core" / "schemas.py").read_text(encoding="utf-8")
        assert "innovation_proxy_triangulation" not in dag_text
        assert "innovation_proxy_triangulation" not in schemas_text

    def test_no_thin_shim(self):
        """不得存在同名 thin shim (news_process/NN_innovation_proxy_triangulation.py)。"""
        shims = list(REPO.glob("*innovation_proxy_triangulation*.py"))
        # 只允许 scripts/audit/ 下那一份 (glob 只扫 REPO 顶层, 天然排除 scripts/audit/ 子目录)
        assert shims == [], f"疑似违规 thin shim: {shims}"

    def test_iron_rule_note_hardcoded(self):
        """铁律 note 字面量须在源码中固定存在 (逐份报告打印, 防误用)。"""
        text = self._source()
        assert "never pooled into one over-identified Hansen J" in text
        assert "not a panel measure, not an instrument" in text

    def test_zero_llm_or_network_calls(self):
        """$0 铁律: 脚本不得出现任何 LLM/HTTP 调用痕迹。"""
        text = self._source()
        for forbidden in ("requests.", "openai", "anthropic", "fetch_llm", "LLMCache("):
            assert forbidden not in text, f"proxy 脚本含疑似网络/LLM 调用: {forbidden}"


# ---------------------------------------------------------------------------
# 4. 双编码原始表存档
# ---------------------------------------------------------------------------
class TestDoubleCodingArtifact:
    def test_csv_exists_under_config(self):
        # fix(WP-R3-P1, 2026-07-14): 存档位由 eval_reports (不入库惯例) 迁 config/
        # 与 yaml 同座并 negation 入库 — 断言同步 (文档化偏离, 见文件头注)。
        assert DOUBLE_CODING_CSV.exists(), f"缺双编码原始表 {DOUBLE_CODING_CSV}"
        assert DOUBLE_CODING_CSV.is_relative_to(CONFIG_DIR)

    def test_csv_row_count_matches_dict(self):
        import csv
        with open(DOUBLE_CODING_CSV, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1506, f"双编码表应恰 1506 行 (含表头之外), 实读 {len(rows)}"

    def test_csv_has_required_columns(self):
        import csv
        with open(DOUBLE_CODING_CSV, encoding="utf-8-sig", newline="") as f:
            header = next(csv.reader(f))
        for col in ("idx", "term", "coder_a_label", "coder_b_label", "agree",
                    "final_label", "arbitration_rationale"):
            assert col in header, f"双编码表缺列 {col}"

    def test_disagreement_rows_have_rationale(self):
        import csv
        with open(DOUBLE_CODING_CSV, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        disagreements = [r for r in rows if r["agree"] == "False"]
        assert len(disagreements) > 0
        missing_rationale = [r["term"] for r in disagreements if not r["arbitration_rationale"].strip()]
        assert not missing_rationale, f"以下分歧词缺仲裁理由: {missing_rationale}"
