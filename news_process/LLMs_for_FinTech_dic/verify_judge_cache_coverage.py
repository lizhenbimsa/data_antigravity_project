"""
盲审缓存覆盖验证器（P3, 2026-07-21 执行计划）——镜像主项目 verify_stage21_cache_coverage 语义。

职责：拿盲审 manifest（复现存根）逐任务重建 prompt → 重算缓存键 → 与 manifest 记录键
互验（防 config 字面漂移）→ 逐键查 _llm_cache.db（只读）。全部命中且零降级 →
盖章「✅ 认证可离线 $0 复现」；否则逐条列缺失并 exit 1。

纯只读、$0、不依赖网络；生成阶段零触碰（只消费判别 manifest 与判别缓存键）。

用法（cwd = LLMs_for_FinTech_dic/）：
    python verify_judge_cache_coverage.py                       # 取最新 manifest
    python verify_judge_cache_coverage.py --manifest <path>     # 指定 manifest
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from config import CACHE_DB_FILE, DATA_DIR, build_judge_prompt
from llm_cache import LLMCache


def _latest_manifest() -> Path:
    candidates = sorted(DATA_DIR.glob("judge_manifest_*.json"))
    if not candidates:
        raise SystemExit("data_processed/ 下无 judge_manifest_*.json（先跑一次完整流程产出存根）")
    return candidates[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description="盲审缓存覆盖验证器（只读, $0）")
    parser.add_argument("--manifest", type=str, default=None, help="manifest 路径（默认最新）")
    parser.add_argument("--db", type=str, default=str(CACHE_DB_FILE), help="缓存库路径")
    args = parser.parse_args()

    manifest_path = Path(args.manifest) if args.manifest else _latest_manifest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "llmsdic-judge-manifest/v1":
        print(f"✗ 无法识别的 manifest schema: {manifest.get('schema')!r}")
        return 1

    kw_list = list(manifest["wordlist"])
    bsize = int(manifest["judge_batch_size"])
    models = list(manifest["judge_models"])
    batches = [kw_list[i:i + bsize] for i in range(0, len(kw_list), bsize)]
    tasks = manifest.get("tasks", {})

    print(f"manifest: {manifest_path.name}")
    print(f"口径: {len(kw_list)} 词 / {len(batches)} 批 / {len(models)} 模型 "
          f"= {len(batches) * len(models)} 任务; 首跑判决 reproducible="
          f"{manifest.get('verdict', {}).get('reproducible')}")

    # 只读打开缓存库（mode=ro：绝不写入、绝不建库）
    db_path = Path(args.db)
    if not db_path.exists():
        print(f"✗ 缓存库不存在: {db_path}")
        return 1
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)

    def _in_db(key: str) -> bool:
        return conn.execute(
            "SELECT 1 FROM llm_cache WHERE key = ?", (key,)
        ).fetchone() is not None

    n_checked = 0
    misses = []          # (model, batch, try, key) 缓存缺条目
    drifts = []          # manifest 键 ≠ 现算键（config prompt 字面漂移）
    absent_tasks = []    # manifest 里整个任务缺席（判别未覆盖该格）
    degraded = []        # 首跑非可重放终局（hard_fail/health_skip/shutdown/offline_miss/无响应 try）

    for model in models:
        for bi, batch in enumerate(batches):
            task = tasks.get(f"{model}|batch{bi}")
            if task is None:
                absent_tasks.append(f"{model}/批次{bi + 1}")
                continue
            outcome = task.get("outcome")
            if outcome not in {"full", "partial_adopt"}:
                degraded.append(f"{model}/批次{bi + 1}: outcome={outcome}")
            prompt = build_judge_prompt(batch)
            for att in task.get("attempts", []):
                n = int(att["try"])
                key_calc = LLMCache.make_key(model, prompt, "0", f"judge|try{n}")
                n_checked += 1
                if att.get("key") and att["key"] != key_calc:
                    drifts.append(f"{model}/批次{bi + 1}/try{n}")
                    continue  # 键已漂移，查库无意义
                if not att.get("got_response", False):
                    degraded.append(f"{model}/批次{bi + 1}/try{n}: 首跑无响应（缓存空洞）")
                    continue
                if not _in_db(key_calc):
                    misses.append(f"{model}/批次{bi + 1}/try{n}: {key_calc[:16]}...")

    conn.close()

    print(f"共核验 {n_checked} 个 (model, batch, try) 缓存键")
    ok = not (misses or drifts or absent_tasks or degraded)
    if ok:
        print("✅ 认证：盲审全量缓存覆盖 0 miss、0 键漂移、0 降级 —— 可离线 $0 逐字节复现"
              "（LLMS_DIC_OFFLINE=1 重放安全）")
        return 0
    for label, items in (
        ("缓存缺条目", misses),
        ("键漂移（config prompt 字面已变，重放≠首跑口径）", drifts),
        ("manifest 缺任务（判别未覆盖）", absent_tasks),
        ("首跑降级（不可复现终局）", degraded),
    ):
        if items:
            print(f"✗ {label} × {len(items)}:")
            for item in items[:30]:
                print(f"    - {item}")
            if len(items) > 30:
                print(f"    ...（另 {len(items) - 30} 条从略）")
    return 1


if __name__ == "__main__":
    sys.exit(main())
