"""规则消融梯度 golden 重生 — drift 验证 (new vs backup golden)。

用法: python news_process/scripts/audit/_regen_ablation/diff_golden.py <backup_golden.json> <new_golden.json>

对每个 stage parquet 比对 new vs backup 的 column_hashes:
  · ADDED  = new 有 / backup 无 (期望 = 规则消融梯度新列, 22 级 108 / 40 级 108 / 51 级 108)
  · REMOVED= backup 有 / new 无 (期望 = 0)
  · DRIFT  = 两边都有但 hash 不同 (期望 = 0; 若 ⊆ 已知 ~4 BLAS-FP 网络列则可外科还原)

退出码 0 = 仅 ADDED 为消融列且 REMOVED=0 且 DRIFT⊆已知BLAS; 否则 1 (须人工裁决)。
"""
import json
import re
import sys

# 已知 BLAS-FP 非确定网络/嵌入列 (golden-regen-omp-determinism memory): 全 canonical env 下应 0 漂移,
# 若仅这些漂移可外科还原 backup 值 (不 bless 漂移)。
_KNOWN_BLAS_RE = re.compile(
    r'(bank_eigen_cent|harmonic_cent|cfbetween_cent|clustering|coh_lda|auth_sim_emb|emb_peer)')
# 规则消融梯度列模式 (article {d}_score_{sfx}{trk} / panel {d}_{sfx}_tone{trk})
_NEW_VARIANTS = ('raw', 'degonly', 'advonly', 'negdeg', 'negadv', 'degadv')
_ABL_RE = re.compile(
    r'^(jiang_2021|yao_2021|bian_2021|du_2022|you_2018|loughran)_'
    r'(?:score_)?(' + '|'.join(_NEW_VARIANTS) + r')(?:_tone)?(?:_(?:full|ctx|ss))?$')


def _hashes(g, stage):
    return (g.get('stages', {}).get(stage, {}) or {}).get('column_hashes', {}) or {}


def main(backup_path, new_path):
    backup = json.load(open(backup_path, encoding='utf-8'))
    new = json.load(open(new_path, encoding='utf-8'))
    stages = sorted(set(backup.get('stages', {})) | set(new.get('stages', {})))
    ok = True
    for st in stages:
        bh, nh = _hashes(backup, st), _hashes(new, st)
        if not bh and not nh:
            continue
        added = [c for c in nh if c not in bh]
        removed = [c for c in bh if c not in nh]
        drift = [c for c in nh if c in bh and nh[c] != bh[c]]
        if not (added or removed or drift):
            continue
        non_abl_added = [c for c in added if not _ABL_RE.match(c)]
        blas_drift = [c for c in drift if _KNOWN_BLAS_RE.search(c)]
        real_drift = [c for c in drift if not _KNOWN_BLAS_RE.search(c)]
        print(f"\n=== {st} ===")
        print(f"  ADDED={len(added)} (ablation={len(added)-len(non_abl_added)}, NON-ablation={len(non_abl_added)})")
        print(f"  REMOVED={len(removed)}  DRIFT={len(drift)} (known-BLAS={len(blas_drift)}, REAL={len(real_drift)})")
        if non_abl_added:
            print(f"  ⚠ NON-ablation ADDED (unexpected): {non_abl_added[:10]}")
            ok = False
        if removed:
            print(f"  ⚠ REMOVED (unexpected): {removed[:10]}")
            ok = False
        if real_drift:
            print(f"  ⚠ REAL DRIFT (NOT known BLAS — must investigate): {real_drift[:15]}")
            ok = False
        if blas_drift:
            print(f"  ℹ known-BLAS drift (可外科还原 backup): {blas_drift}")
    print("\n" + ("VALIDATION PASS — 仅消融新列 + (可能)已知 BLAS 漂移" if ok
                  else "VALIDATION FAIL — 见上方 ⚠ (须人工裁决, 勿 bless)"))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
