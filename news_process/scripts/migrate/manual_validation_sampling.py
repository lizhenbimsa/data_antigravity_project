"""人工验证研究 (n≥500) 分层抽样。

输出 (2026-10-10 起, 文件级隔离; 协议 §4 独立性硬条款):
  - manual_validation_samples_blind_{R1,R2,R3}.xlsx — 每名 rater 一份盲表,
    只含文本 + 本人标注列, 零机器列 (不含 stratum / population_weight);
  - manual_validation_reconciliation.xlsx — orig_index 主键 + stratum +
    population_weight + v7ref_ LLM 预测, 不发编码员;
  - manual_validation_samples.xlsx — 仅由 ``merge`` 子命令在三人填毕后装配
    (三盲表 ⋈ 对账表的层/权重), 供 stage 63 (63_news_llms_evaluation) Panel E/F/G 消费, 不发编码员。
含 5 个分层 (strata) + 纯随机层 F, 供 3 名 rater 独立标注。

分层设计 (substantive×symbolic × application×technology 四格 + 拒判格 A;
原 docs/methodology/manual_validation_study_plan.md 已随 docs/ 目录整体删除, commit 1698bda5):
  A: is_bank_fintech_news = False  → 100 篇 (验证拒判正确性)
  B: substantive ∧ application      → 100 篇 (众数基线)
  C: symbolic    ∧ application      → 100 篇 (少数类过采样)
  D: substantive ∧ technology       → 100 篇 (少数类过采样)
  E: symbolic    ∧ technology       → 100 篇 (不足则取全部) — 双重少数类

Stratum E fallback: 若该层不足 100, 取全部 + 把缺额按比例补到 C/D。

运行方式: 从项目根目录运行
    "F:/Anaconda3/python.exe" news_process/scripts/migrate/manual_validation_sampling.py          # 抽样产盲表
    "F:/Anaconda3/python.exe" news_process/scripts/migrate/manual_validation_sampling.py merge    # 三人填毕后装配

白话: 从 LLM 已打标的文章里按"类别组合"分五组抽 500 篇, 给三位真人独立标注,
之后拿真人结果和 LLM 结果对账, 检验 LLM 打标可不可信。少见的类别故意多抽,
不然抽不到几篇没法检验。
"""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================================
# N2 盲表防覆写机制 (2026-07-14; 计划 §10 新挂账 N2, 人工窗口硬前置)
# ----------------------------------------------------------------------------
# fix(N2, 2026-07-14): 此前两处 to_excel (coder_df→OUTPUT_XLSX,
# recon_df→RECONCILIATION_XLSX) 直接写盘无任何检测 — 人工标注 (R1/R2/R3_*
# 列) 启动后若本脚本被误重跑, 会静默覆盖已填写的人工判定且不可逆。现补写出
# 前双保险检测 (同款机制镜像 news_process/validation/llms_human.py
# ``_guard_blind_overwrite``): ① 既有 xlsx 的 R1_/R2_/R3_ 标注列非空计数 >0
# → 拒绝; ② 独立"标注进行中"旗标文件存在 → 拒绝 (覆盖"刚生成尚未填写即被
# 误重跑"窗口)。二者任一命中即 fail-loud raise SystemExit (镜像本文件既有
# ``_resolve_col`` 的 fail-loud 风格), 需显式 --force-regenerate 才可覆盖。
# ============================================================================


def _annotation_flag_path(out_path) -> Path:
    """"发放"旗标文件路径 (fix N2-P1: 发放留痕/警告触发器, 非独立硬闸)。"""
    return Path(str(out_path) + '.annotation_in_progress')


def _count_filled_rater_annotations(path) -> int:
    """读取既有工作台, 统计 R1_/R2_/R3_ 前缀列中非空(非 NaN/非空白/非'nan')值个数。

    读取失败时向上抛出异常, 由调用方保守地当作"有风险"处理。
    """
    existing = pd.read_excel(path)
    rater_cols = [c for c in existing.columns if c.startswith(('R1_', 'R2_', 'R3_'))]
    n_filled = 0
    for c in rater_cols:
        s = existing[c]
        non_null = s.notna()
        non_blank = (s.astype(str).str.strip().str.lower().ne('')
                     & s.astype(str).str.strip().str.lower().ne('nan'))
        n_filled += int((non_null & non_blank).sum())
    return n_filled


def _guard_blind_overwrite(out_path, force_regenerate: bool) -> None:
    """N2 盲表防覆写守卫: 写出前检测, 有风险则 fail-loud 拒绝覆写。"""
    out_path = Path(out_path)
    flag_path = _annotation_flag_path(out_path)
    flag_exists = flag_path.exists()
    n_filled = 0
    read_failed = False
    if out_path.exists():
        try:
            n_filled = _count_filled_rater_annotations(out_path)
        except Exception as e:
            print(f"覆写检测: 读取既有工作台 {out_path} 失败 ({e}) — 保守判定为有风险, 拒绝覆写")
            read_failed = True

    if force_regenerate:
        if n_filled > 0 or flag_exists or read_failed:
            print(
                f"⚠ --force-regenerate 显式越权覆写 {out_path} (检测到 {n_filled} 个非空标注"
                f"{'/读取失败按有风险处理' if read_failed else ''}"
                f"{'/存在标注进行中旗标' if flag_exists else ''}) — "
                "现有人工标注 (如有) 将被覆盖/作废。"
            )
        return

    if n_filled > 0 or read_failed:
        msg = (
            f"检测到 {out_path} 已有 {n_filled} 个非空标注"
            + ("（读取异常, 保守视为有标注）" if read_failed else "")
            + ("（且存在'发放'旗标文件）" if flag_exists else "")
            + " → 拒绝重生 (N2 盲表防覆写机制)。如确需重新生成 (将作废现有人工标注), "
              "请显式传 --force-regenerate。"
        )
        print(msg)
        raise SystemExit(
            f"N2 盲表防覆写守卫拦截: {out_path} 已有 {n_filled} 个非空人工标注"
            f"{'（含读取异常）' if read_failed else ''}, "
            "拒绝覆写；需 --force-regenerate 显式越权。"
        )

    # fix(N2-P1, 2026-07-14): 旗标单独在位 (零标注且可读) → 放行 + LOUD 警告,
    # 与 llms_human._guard_blind_overwrite 同款语义 (旗标=发放记录, 非独立硬闸;
    # 抽样确定性保证重生内容可再现, 空表无人工成果可丢; 防守卫死锁重跑路径)。
    if flag_exists:
        print(
            f"⚠ 检测到'已发放'旗标 {flag_path} 但工作台零标注 — 按确定性重生放行。"
            "若编码员正于外部副本作业, 请先收回核对。"
        )


def _touch_annotation_flag(out_path) -> None:
    """写出成功后落"发放"旗标 (fix N2-P1: 语义=发放记录/重生警告触发器,
    单独在位不硬拦空表重生; 非空标注由主检硬拦)。旗标写失败不影响工作台本身。"""
    import time
    try:
        with open(_annotation_flag_path(out_path), 'w', encoding='utf-8') as f:
            f.write(
                "N2 盲表发放旗标 — "
                f"由 manual_validation_sampling.main 于 {time.strftime('%Y-%m-%d %H:%M:%S')} 生成。\n"
                f"存在表示 {out_path} 已发放给编码员; 零标注时重跑仅警告放行, "
                "检出非空人工标注则硬拦 (须 --force-regenerate 越权)。\n"
            )
    except Exception as e:
        print(f"落地发放旗标文件失败 (不影响工作台本身): {e}")


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_PARQUET = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / '21_tone_llms.parquet'
INPUT_FULL_PARQUET = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / '21_tone_llms_full.parquet'
OUTPUT_XLSX = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / 'manual_validation_samples.xlsx'
# 反锚定对账表 (R-0/F1): LLM 预测 (v7ref_*), 仅在编码完成+共识冻结后解锁
RECONCILIATION_XLSX = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / 'manual_validation_reconciliation.xlsx'
RATERS = ('R1', 'R2', 'R3')
# 每名 rater 的盲表 (文件级隔离): 旧版三人同表分列 → 后填者可见先填者判定, 破独立性。
BLIND_XLSX = {r: OUTPUT_XLSX.with_name(f'manual_validation_samples_blind_{r}.xlsx') for r in RATERS}
BLIND_SHEET = '验证数据'
# stratum 由 LLM 预测定义 (如 C_symbolic_app), population_weight 与层一一对应可反推层
# → 二者只进对账表, 绝不进盲表。
RECON_ONLY_COLS = ['stratum', 'population_weight']
# 仲裁表 (2026-10-12): 两人编码互相矛盾的条目交 C 裁决; merge 时把 C_ 列并入装配表。
ADJ_XLSX = OUTPUT_XLSX.with_name('manual_validation_pending_adjudication.xlsx')
_ADJ_DIMS = {  # 维度 → (R 列后缀, 仲裁列, 下拉取值)
    'substantiveness': ('stage3a_substantiveness', 'C_stage3a_substantiveness', ['substantive', 'symbolic']),
    'locus': ('stage3b_locus', 'C_stage3b_locus', ['technology', 'application']),
    'collab': ('stage3c_collab', 'C_stage3c_collab', ['self_developed', 'collaborative']),
}
# 分类标注列的合法取值 (盲表内锁下拉; 拼写错误会被 normalize_rater_value 静默丢成 None)。
_RATER_DROPDOWNS = {
    'stage1_relevant': ['yes', 'no'],
    'stage1_conf': ['low', 'med', 'high'],
    'stage2_sentiment': ['positive', 'neutral', 'negative'],
    'stage2_conf': ['low', 'med', 'high'],
    'stage3a_substantiveness': ['substantive', 'symbolic'],
    'stage3a_conf': ['low', 'med', 'high'],
    'stage3b_locus': ['technology', 'application'],
    'stage3b_conf': ['low', 'med', 'high'],
    'stage3c_collab': ['self_developed', 'collaborative'],
    'stage3c_conf': ['low', 'med', 'high'],
}


def _write_rater_blind(blind_df: pd.DataFrame, rater: str, path: Path) -> None:
    """写单名 rater 的盲表: 验证数据 (锁下拉) + 编码指南。"""
    guide = pd.DataFrame(
        [('任务', f'独立填写 {rater}_ 前缀各列; 判断依据 = 标题 + 内容全文, 仅针对 target_bank 目标银行。'),
         ('stage1_relevant', 'yes / no — 该文是否确为目标银行的金融科技相关新闻'),
         ('stage2_sentiment', 'positive / neutral / negative — 对目标银行金科活动的情感倾向'),
         ('stage3a_substantiveness', 'substantive (实质性举措) / symbolic (象征性表态)'),
         ('stage3b_locus', 'technology (底层技术) / application (应用场景)'),
         ('stage3c_collab', 'self_developed (自主研发) / collaborative (外部协同)'),
         ('*_conf', 'low / med / high — 本人对该判定的把握'),
         ('*_rationale', '自由文本, 简述判定理由'),
         ('total_time_sec', '本篇用时 (秒)'),
         ('独立性', '禁止与其他编码员交流; 按行序标注; 不得改动其余列。'),
         ('完整协议', 'scripts/audit/HUMAN_ANNOTATION_PROTOCOL_2026-07-03.md')],
        columns=['项目', '说明'])
    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        blind_df.to_excel(writer, sheet_name=BLIND_SHEET, index=False)
        guide.to_excel(writer, sheet_name='编码指南', index=False)
        ws = writer.sheets[BLIND_SHEET]
        for suffix, choices in _RATER_DROPDOWNS.items():
            col = f'{rater}_{suffix}'
            if col in blind_df.columns:
                ci = list(blind_df.columns).index(col)
                ws.data_validation(1, ci, len(blind_df), ci,
                                   {'validate': 'list', 'source': choices})


def merge() -> None:
    """三人填毕后装配 manual_validation_samples.xlsx (stage 63 (63_news_llms_evaluation) Panel E/F/G 的输入)。

    三盲表按 orig_index 对齐取各自标注列, 再从对账表并回 stratum / population_weight;
    v7ref_ LLM 预测不并入 (stage 63 的机器预测另从 21_tone_llms.parquet 经 docid 取)。
    """
    for p in list(BLIND_XLSX.values()) + [RECONCILIATION_XLSX]:
        if not p.exists():
            raise SystemExit(f'[FATAL] 缺文件: {p} — 先跑抽样')
    frames = {r: pd.read_excel(p, sheet_name=BLIND_SHEET) for r, p in BLIND_XLSX.items()}
    recon = pd.read_excel(RECONCILIATION_XLSX)
    keys = set(recon['orig_index'])
    for r, d in frames.items():
        if d['orig_index'].duplicated().any() or set(d['orig_index']) != keys:
            raise SystemExit(f'[FATAL] 盲表 {r} 与对账表 orig_index 不一致, 拒绝装配')
    merged = frames['R1'].copy()
    for r in RATERS[1:]:
        rcols = [c for c in frames[r].columns if c.startswith(f'{r}_')]
        merged = merged.merge(frames[r][['orig_index'] + rcols], on='orig_index',
                              how='left', validate='one_to_one')
    wcols = [c for c in RECON_ONLY_COLS if c in recon.columns]
    merged = merged.merge(recon[['orig_index'] + wcols], on='orig_index',
                          how='left', validate='one_to_one')
    if ADJ_XLSX.exists():
        adj = pd.read_excel(ADJ_XLSX, sheet_name=BLIND_SHEET)
        ccols = [c for c in adj.columns if c.startswith('C_')]
        merged = merged.merge(adj[['orig_index'] + ccols], on='orig_index',
                              how='left', validate='one_to_one')
        print(f'  并入仲裁列 {ccols} ({int(adj[ccols].notna().sum().sum())} 个 C 裁决)')
    merged.to_excel(OUTPUT_XLSX, index=False)
    for r in RATERS:
        n = _count_filled_rater_annotations(BLIND_XLSX[r])
        print(f'  {r}: {n} 个非空标注单元格')
    print(f'[装配] {len(merged)} 行 → {OUTPUT_XLSX} (不发编码员)')


def adjudicate() -> None:
    """两人打平的条目 → 仲裁表 (C 填)。读装配表, 只列需裁维度的三人原判 + 空白 C 列。"""
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from news_process.validation.manual_validation_schema import R_COLUMNS_BY_RATER, needs_adjudication
    if not OUTPUT_XLSX.exists():
        raise SystemExit(f'[FATAL] 缺装配表 {OUTPUT_XLSX} — 先跑 merge')
    if ADJ_XLSX.exists():
        old = pd.read_excel(ADJ_XLSX, sheet_name=BLIND_SHEET)
        if old[[c for c in old.columns if c.startswith('C_')]].notna().any().any():
            raise SystemExit(f'[FATAL] 既有仲裁表已含 C 判定, 拒绝覆盖: {ADJ_XLSX}')
    mv = pd.read_excel(OUTPUT_XLSX)
    need = pd.DataFrame({d: mv.apply(lambda r, d=d: needs_adjudication(r, R_COLUMNS_BY_RATER[d]), axis=1)
                         for d in _ADJ_DIMS})
    rows = need.any(axis=1)
    out = mv.loc[rows, ['orig_index', 'docid', 'target_bank', '标题', '内容']].copy()
    for d, (suf, ccol, _) in _ADJ_DIMS.items():
        out[f'需裁_{d}'] = need.loc[rows, d].map({True: '是', False: ''})
        for r in RATERS:
            out[f'{r}_{suf}'] = mv.loc[rows, f'{r}_{suf}']
        out[ccol] = ''
    with pd.ExcelWriter(ADJ_XLSX, engine='xlsxwriter') as writer:
        out.to_excel(writer, sheet_name=BLIND_SHEET, index=False)
        ws = writer.sheets[BLIND_SHEET]
        for _, (_, ccol, choices) in _ADJ_DIMS.items():
            ci = list(out.columns).index(ccol)
            ws.data_validation(1, ci, len(out), ci, {'validate': 'list', 'source': choices})
    print(f'[仲裁] {ADJ_XLSX}: {len(out)} 行; 各维需裁 {need.sum().to_dict()} (零机器判定列)')


SEED = 42
TARGET_TOTAL = 500
PER_STRATUM = 100


def main(force_regenerate: bool = False):
    """分层抽样主入口。

    Args:
        force_regenerate: fix(N2, 2026-07-14) 显式越权覆写既有工作台的人工
            标注 (CLI: ``--force-regenerate``)。默认 False —— 若既有 xlsx 已
            有非空 R1_/R2_/R3_ 标注或"标注进行中"旗标存在, 拒绝覆写并 fail-loud。
    """
    # 加载: 21_tone_llms_full.parquet 含全部 1,170 篇文章 (包括 verified=False)
    if INPUT_FULL_PARQUET.exists():
        df = pd.read_parquet(INPUT_FULL_PARQUET)
        print(f'Loaded full parquet: {len(df)} rows × {len(df.columns)} cols')
    else:
        df = pd.read_parquet(INPUT_PARQUET)
        print(f'Loaded verified-only parquet: {len(df)} rows × {len(df.columns)} cols')

    # WS-D F7 先决修复 (R6-P2-2): 分层列改读 _full 主轨 + loud 守卫。
    # 现盘 21_tone_llms*.parquet 只有 innovation_substantiveness_{full,ctx,ss}
    # (带后缀), 无裸名 innovation_substantiveness/_locus → 裸名直接 KeyError 崩。
    # 与 :53 已用的 llm_verified_full 主轨一致。
    def _resolve_col(df_, candidates, what):
        for c in candidates:
            if c in df_.columns:
                return c
        innov = [c for c in df_.columns if c.startswith('innovation_')]
        raise SystemExit(
            f'抽样阻塞: 缺 {what} 分层列 (尝试 {candidates}); '
            f'现有 innovation_* 列: {innov}'
        )

    SUBST_COL = _resolve_col(
        df, ['innovation_substantiveness_full', 'innovation_substantiveness'],
        'innovation_substantiveness')
    LOCUS_COL = _resolve_col(
        df, ['innovation_locus_full', 'innovation_locus'], 'innovation_locus')
    # collab 列仅用于 v7ref 参考 + stage3c_collab 标注, 不进分层 (8 格早期试跑 T=2 枯竭)
    COLLAB_COL = next(
        (c for c in ['innovation_collab_mode_full', 'innovation_collab_mode']
         if c in df.columns), None)

    # 分层
    strata = {}

    # Stratum A: 非银行金融科技新闻 (验证拒判)
    pool_a = df[df.get('llm_verified_full', True) == False]
    strata['A_not_relevant'] = pool_a

    # Stratum B-E: verified=True, 按 innovation_* 维度分层
    verified = df[df.get('llm_verified_full', True) == True].copy()
    print(f'\nVerified subset: {len(verified)}')
    print(f'  {SUBST_COL} distribution:')
    print(verified[SUBST_COL].value_counts(dropna=False).to_string())
    print(f'  {LOCUS_COL} distribution:')
    print(verified[LOCUS_COL].value_counts(dropna=False).to_string())

    # B: 实质性 ∧ 应用场景 (众数格)
    strata['B_substantive_app'] = verified[
        (verified[SUBST_COL] == '实质性') &
        (verified[LOCUS_COL] == '应用场景')
    ]

    # C: 象征性 (symbolic, W&Z 1998 ASQ) ∧ 应用场景
    strata['C_symbolic_app'] = verified[
        (verified[SUBST_COL] == '象征性') &
        (verified[LOCUS_COL] == '应用场景')
    ]

    # D: 实质性 ∧ 底层技术
    strata['D_substantive_tech'] = verified[
        (verified[SUBST_COL] == '实质性') &
        (verified[LOCUS_COL] == '底层技术')
    ]

    # E: 象征性 ∧ 底层技术 (双重少数类)
    strata['E_symbolic_tech'] = verified[
        (verified[SUBST_COL] == '象征性') &
        (verified[LOCUS_COL] == '底层技术')
    ]

    # 抽样 (带不足额回退)
    print(f'\nStratum populations:')
    samples = {}
    backfill_needed = 0
    for name, pool in strata.items():
        avail = len(pool)
        target = PER_STRATUM
        n = min(avail, target)
        if avail < target:
            shortfall = target - avail
            backfill_needed += shortfall
            print(f'  {name}: {avail} avail, taking ALL {n} (shortfall {shortfall} → backfill)')
        else:
            print(f'  {name}: {avail} avail, sampling {n}')
        samples[name] = pool.sample(n=n, random_state=SEED).assign(stratum=name)

    # 若 E (或其他层) 不足额 — 缺额重新分配到 C/D (次稀有的两类)
    if backfill_needed > 0:
        print(f'\nBackfill needed: {backfill_needed} → distributing to C + D')
        # 优先补 C (E 之后最稀有), 再补 D
        for backfill_target in ['C_symbolic_app', 'D_substantive_tech']:
            if backfill_needed <= 0:
                break
            pool = strata[backfill_target]
            already_sampled_ids = set(samples[backfill_target].index)
            remaining = pool.loc[~pool.index.isin(already_sampled_ids)]
            add_n = min(backfill_needed, len(remaining))
            if add_n > 0:
                extra = remaining.sample(n=add_n, random_state=SEED + 1).assign(stratum=backfill_target + '_extra')
                samples[backfill_target] = pd.concat([samples[backfill_target], extra])
                print(f'  {backfill_target}: +{add_n} (now {len(samples[backfill_target])})')
                backfill_needed -= add_n

    # 合并各层样本
    out = pd.concat(samples.values(), ignore_index=False).reset_index(drop=False)
    out = out.rename(columns={'index': 'orig_index'})

    # 追加后置分层加权列
    # population_weight = (该层总体数) / (该层样本数)
    # 白话: 少数类被故意多抽了, 算总体指标时要用这个权重"还原"回真实占比。
    for name in samples.keys():
        clean_name = name.replace('_extra', '')
        pop_size = len(strata[clean_name])
        sample_size = sum(1 for s in out['stratum'] if s.startswith(clean_name))
        weight = pop_size / sample_size if sample_size > 0 else 0.0
        out.loc[out['stratum'].str.startswith(clean_name), 'population_weight'] = weight

    # 标注表单列 (初始为空, 留给 rater 填写)
    # WS-D: 新增 stage3c_collab (自研/协同, Chesbrough 2003 / L&S 2006);
    # 取值 self_developed / collaborative (与 _RATER_VALUE_TO_CANONICAL_LABEL_RAW 对齐)。
    for rater in ['R1', 'R2', 'R3']:
        for stage_col in [
            f'{rater}_stage1_relevant',         # yes / no
            f'{rater}_stage1_conf',              # low / med / high
            f'{rater}_stage2_sentiment',         # positive / neutral / negative
            f'{rater}_stage2_conf',
            f'{rater}_stage3a_substantiveness',  # substantive / symbolic
            f'{rater}_stage3a_conf',
            f'{rater}_stage3a_rationale',        # 自由文本
            f'{rater}_stage3b_locus',            # technology / application
            f'{rater}_stage3b_conf',
            f'{rater}_stage3b_rationale',
            f'{rater}_stage3c_collab',           # self_developed / collaborative
            f'{rater}_stage3c_conf',
            f'{rater}_stage3c_rationale',
            f'{rater}_total_time_sec',           # 用于注意力检查
        ]:
            out[stage_col] = ''

    # WS-D 纯随机层 (R4-P2-05): 10-20% 不按任何 LLM 标签随机抽,
    # 供无偏估计 LLM 漏判率 (分层抽样按 LLM 标签定义 frame 无法估漏判)。
    # ⚠ 早期试跑 T=2/N≈400 下仅作 face-validity 哨兵, 漏判率点估计不附推断 CI,
    #   真值 deferred-T18 全样本。
    already = set(out['orig_index'])
    pure_pool = df.loc[~df.index.isin(already)]
    pure_n = min(len(pure_pool), max(1, round(0.15 * len(out))))
    if pure_n > 0:
        pure = (pure_pool.sample(n=pure_n, random_state=SEED + 2)
                .assign(stratum='F_pure_random')
                .reset_index().rename(columns={'index': 'orig_index'}))
        pure['population_weight'] = len(df) / pure_n if pure_n else 0.0
        # 给纯随机层补齐 rater 标注列 (空) 与其余 out 列
        for c in out.columns:
            if c not in pure.columns:
                pure[c] = '' if c.startswith(('R1_', 'R2_', 'R3_')) else pd.NA
        out = pd.concat([out, pure[out.columns]], ignore_index=True)

    # ── 反锚定 (R-0/F1): 每名 rater 独立盲表零 LLM 标签 + 对账表后解锁 ──
    # 窗口文本列 (F13/R-P1-3): 供 deferred 窗口级金标准 (各轨独立窗口判标签)
    metadata_cols = ['orig_index', 'docid', 'target_bank', '标题', '内容',
                     'content_ctx', 'content_ss']
    metadata_cols = [c for c in metadata_cols if c in out.columns]

    # v7ref LLM 预测 (含 collab): 仅进对账表, 绝不进编码者盲表 (anchoring)
    v7_ref_cols_orig = [c for c in ['llm_verified_full', 'llm_sentiment_full',
                                    SUBST_COL, LOCUS_COL, COLLAB_COL]
                        if c and c in out.columns]
    rename_map = {c: f'v7ref_{c}' for c in v7_ref_cols_orig}

    # D5 修复: random shuffle 避免 rater 在 stratum boundary anchoring bias
    out = out.sample(frac=1, random_state=43).reset_index(drop=True)

    # (a) reconciliation 对账表: orig_index 主键 + 层/权重 + 全部 v7ref_ LLM 预测,
    #     编码完成+共识冻结后才解锁对账
    recon_df = out[['orig_index'] + RECON_ONLY_COLS + v7_ref_cols_orig].rename(columns=rename_map)

    print(f'\nFinal sample size: {len(out)}')
    print('Stratum breakdown:')
    print(out['stratum'].value_counts().to_string())
    # (b) 每名 rater 一份盲表: 元数据 + 本人空白标注列, 同内容同行序。
    # fix(N2, 2026-07-14): 写出前 N2 防覆写守卫 — 既有盲表若已有非空标注,
    # 拒绝覆写 (需 force_regenerate=True 显式越权)。三份先全部过守卫再落盘, 防半写。
    print()
    for rater in RATERS:
        _guard_blind_overwrite(BLIND_XLSX[rater], force_regenerate)
    _guard_blind_overwrite(RECONCILIATION_XLSX, force_regenerate)
    for rater in RATERS:
        own_cols = [c for c in out.columns if c.startswith(f'{rater}_')]
        _write_rater_blind(out[metadata_cols + own_cols], rater, BLIND_XLSX[rater])
        _touch_annotation_flag(BLIND_XLSX[rater])
        print(f'[盲表{rater}] 零机器列, 仅本人标注列 → {BLIND_XLSX[rater]}')
    print(f'[对账表] reconciliation (层/权重/LLM 预测, 编码后解锁) → {RECONCILIATION_XLSX}')
    recon_df.to_excel(RECONCILIATION_XLSX, index=False)
    _touch_annotation_flag(RECONCILIATION_XLSX)
    print('Done.')


if __name__ == '__main__':
    # fix(N2, 2026-07-14): --force-regenerate 显式越权覆写既有人工标注
    # 用法: python manual_validation_sampling.py [--force-regenerate]
    #       python manual_validation_sampling.py merge   (三人填毕后装配)
    #       python manual_validation_sampling.py adjudicate   (两人打平条目 → 仲裁表)
    if 'merge' in sys.argv[1:]:
        merge()
    elif 'adjudicate' in sys.argv[1:]:
        adjudicate()
    else:
        main(force_regenerate='--force-regenerate' in sys.argv[1:])
