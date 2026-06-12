"""Plan E P4 G3 batch migration: 9 paper_spec.yaml main treatment → _ctx.

用法 (user-run):
    F:\\Anaconda3\\python.exe news_process/scripts/migrate/plan_e_g3_paper_spec_ctx_switch.py [--dry-run]

工作:
    对 9 个 paper_spec.yaml 自动:
    1. 把 treatment.primary 的 _full 后缀替换为 _ctx
    2. 把原 _full 主变量加入 treatment.alternative (保留 robustness 路径)
    3. 输出 diff + 备份 (.bak)
    4. 不修改的项: alternative 已含 _ctx 变体的 paper 视为已迁移

学术依据: Tetlock 2007 JF / Loughran-McDonald 2016 JAR 现代标准。
治理: 单作者 + No SSRN preprint + 数据授权 → main treatment 切换不违反 pre-reg。

⚠ 重要: 切换后所有现有 Stata 表格数字会变。建议运行后:
    1. 重跑 stage 13/14/15 → 21 → 45 → 46 完整 pipeline
    2. 重生成 9 paper Stata 输出 (papers/_common/stata_runner.py build-replication)
    3. 跑 ATT 漂移监控 (att_drift_simulation.py)
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys

# Round 2 M4 修: 用 ruamel.yaml round-trip 保留 comment + 处理 inline/block 通用
# 替代脆弱的 regex 替换. ruamel.yaml 0.18+ 已在项目依赖中.
from ruamel.yaml import YAML

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

PAPERS_DIR = os.path.join(_PROJECT_PARENT, 'news_process', 'papers')

# 已在 P4 G3 手动迁移的 paper (跳过自动处理)
ALREADY_MIGRATED = {'bank_fintech_tone'}


def _is_full_suffix_var(name: str) -> bool:
    return isinstance(name, str) and name.endswith('_full')


def _to_ctx(name: str) -> str:
    if not _is_full_suffix_var(name):
        return name
    return name[:-len('_full')] + '_ctx'


def migrate_one(spec_path: str, dry_run: bool = False) -> tuple[bool, str]:
    """对单 paper spec 做 G3 迁移 (Round 2 M4 修: ruamel.yaml round-trip).

    用 ruamel.yaml round-trip 保留 comment + 处理 inline / block / mixed 通用,
    替代 v1 的脆弱 regex 替换 (在 inline list 上 silent fail).
    """
    yaml_rt = YAML()
    yaml_rt.preserve_quotes = True
    yaml_rt.indent(mapping=2, sequence=4, offset=2)

    with open(spec_path, 'r', encoding='utf-8') as f:
        spec = yaml_rt.load(f)

    if not spec or 'treatment' not in spec:
        return False, "  [skip] no 'treatment' section"

    paper_id = spec.get('paper_id', os.path.basename(os.path.dirname(spec_path)))
    if paper_id in ALREADY_MIGRATED:
        return False, f"  [skip] {paper_id} already migrated (manual)"

    tx = spec['treatment']
    primary = tx.get('primary')
    if not _is_full_suffix_var(primary):
        return False, f"  [skip] primary='{primary}' has no _full suffix"

    new_primary = _to_ctx(primary)
    alt = tx.get('alternative', [])
    if not isinstance(alt, list):
        alt = [alt]

    # Round 2 M4 修: 用对象层操作 + ruamel round-trip dump (保留 comment)
    # 1) 旧 primary 进 alternative (若不已在)
    # 2) 所有 _full 变体的 _ctx 镜像加入 alternative (若不已在)
    existing_set = {str(a) for a in alt}
    to_append: list[str] = []
    # alternative 中 _full 变体的 _ctx 镜像
    for a in list(alt):
        if _is_full_suffix_var(a):
            ctx = _to_ctx(a)
            if ctx not in existing_set and ctx != new_primary:
                to_append.append(ctx)
                existing_set.add(ctx)
    # old primary 作 robustness 路径
    if primary not in existing_set and primary != new_primary:
        to_append.append(primary)
        existing_set.add(primary)

    # Round 2 m5 修: .bak 带时间戳, 避免二次 --apply 覆盖丢失中间态
    import datetime as _dt
    _ts = _dt.datetime.now().strftime('%Y%m%d-%H%M%S')

    if dry_run:
        return True, (f"  [dry] {paper_id}: primary {primary!r} -> {new_primary!r}; "
                      f"alternative will add {to_append}")

    # 备份带时间戳 (m5 修)
    bak_path = f"{spec_path}.bak.{_ts}"
    shutil.copy2(spec_path, bak_path)

    # 改 primary
    tx['primary'] = new_primary
    # 追加 alternative 条目 (保留原 list 类型 — ruamel CommentedSeq)
    # Round 5 m12 修: setdefault 提到 loop 外避免冗余调用
    if to_append:
        tx.setdefault('alternative', [])
        for item in to_append:
            tx['alternative'].append(item)

    with open(spec_path, 'w', encoding='utf-8') as f:
        yaml_rt.dump(spec, f)

    return True, (f"  [done] {paper_id}: primary={new_primary} "
                  f"(+{len(to_append)} alternative items: {to_append}; "
                  f"backup: {os.path.basename(bak_path)})")


def main():
    ap = argparse.ArgumentParser(
        description="Plan E P4 G3 batch migration. 默认 DRY-RUN, 需 --apply 才实写."
    )
    # F-E 修 (审核): 默认 dry-run, 用户必须显式 --apply 才实写
    # 防止误执行污染 9 paper spec
    ap.add_argument('--apply', action='store_true',
                    help='实际写入 yaml (默认 dry-run); 先跑 dry-run 看 diff 再加此 flag')
    args = ap.parse_args()
    dry_run = not args.apply

    print("=" * 60)
    print(f"Plan E P4 G3 — paper_spec.yaml main treatment → _ctx 批量迁移")
    print(f"PAPERS_DIR: {PAPERS_DIR}")
    print(f"Mode: {'DRY-RUN (默认, 加 --apply 实写)' if dry_run else 'APPLY (实写, 含 .bak 备份)'}")
    print("=" * 60)

    paper_dirs = sorted(
        os.path.join(PAPERS_DIR, d) for d in os.listdir(PAPERS_DIR)
        if os.path.isdir(os.path.join(PAPERS_DIR, d))
        and not d.startswith('_')
    )
    n_changed = 0
    for pdir in paper_dirs:
        spec_path = os.path.join(pdir, 'paper_spec.yaml')
        if not os.path.exists(spec_path):
            continue
        changed, msg = migrate_one(spec_path, dry_run=dry_run)
        print(msg)
        if changed:
            n_changed += 1

    print("=" * 60)
    print(f"Migration complete: {n_changed} paper(s) {'would be ' if dry_run else ''}updated.")
    if not dry_run and n_changed > 0:
        print(f"⚠ NEXT: 重跑 pipeline + Stata 模板 + ATT 漂移检验.")
        print(f"  备份文件: papers/*/paper_spec.yaml.bak (可 git revert 或手动 restore)")


if __name__ == '__main__':
    main()
