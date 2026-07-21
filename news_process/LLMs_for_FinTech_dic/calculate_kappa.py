import pandas as pd
import numpy as np
from pathlib import Path

# 学术化输出支撑（四位有效数字 + 经核验 APA 参考文献；详见 academic.py）
from academic import sig4, cite, references_block

# 本脚本引用文献 handle（Fleiss κ 原始定义 + Landis-Koch / McHugh 双口径分级
# + 一致性系数族：Cohen κ 配对基线 / Krippendorff α 标准测度 / Gwet AC1 对高一致偏态稳健
# + Feinstein-Cicchetti『kappa 悖论』警示——LLM 超多数投票为高一致偏态场景，正切该悖论）
_CITED_KAPPA = ["fleiss_1971", "landis_1977", "mchugh_2012",
                "cohen_1960", "hayes_2007", "gwet_2008", "feinstein_1990"]


def kappa_bands(k: float) -> tuple:
    """返回 Fleiss' κ 在 Landis & Koch (1977) 与 McHugh (2012) 两套口径下的一致性等级。

    Landis-Koch (1977): <0 Poor / 0.00-0.20 Slight / 0.21-0.40 Fair /
      0.41-0.60 Moderate / 0.61-0.80 Substantial / 0.81-1.00 Almost Perfect。
    McHugh (2012, 更严): <0.40 None-to-Minimal(弱) / 0.40-0.59 Weak /
      0.60-0.79 Moderate / 0.80-0.90 Strong / >0.90 Almost Perfect。
    两套口径「不分主次、双重披露」，避免单一分级夸大或低估一致性水平。
    """
    if k < 0:
        lk = "Poor（差）"
    elif k <= 0.20:
        lk = "Slight（轻微）"
    elif k <= 0.40:
        lk = "Fair（尚可）"
    elif k <= 0.60:
        lk = "Moderate（中度）"
    elif k <= 0.80:
        lk = "Substantial（高度）"
    else:
        lk = "Almost Perfect（几近完全）"
    if k < 0.40:
        mh = "None-to-Minimal（无-弱）"
    elif k < 0.60:
        mh = "Weak（弱）"
    elif k < 0.80:
        mh = "Moderate（中度）"
    elif k <= 0.90:
        mh = "Strong（强）"
    else:
        mh = "Almost Perfect（几近完全）"
    return lk, mh


def fleiss_kappa(ratings, n_categories):
    """
    计算 Fleiss' Kappa 系数
    :param ratings: 形状为 (N, k) 的数组，N 是被评估项目的数量，k 是评估者的数量
                    或者形状为 (N, n_categories) 的数组，表示每个项目被评为某个类别的次数
    :param n_categories: 类别的总数
    """
    ratings = np.asarray(ratings)
    # 输入的是原始评分，需要转换为频数矩阵
    N, k = ratings.shape
    freq_matrix = np.zeros((N, n_categories), dtype=int)
    for i in range(N):
        for j in range(k):
            freq_matrix[i, int(ratings[i, j])] += 1
    
    # 计算 p_j (每个类别被分配的整体比例)
    p_j = freq_matrix.sum(axis=0) / (N * k)

    # 计算 P_i (每个项目上评估者达成一致的程度)
    P_i = (np.sum(freq_matrix**2, axis=1) - k) / (k * (k - 1))

    # 计算 P_bar (P_i 的平均值)
    P_bar = np.mean(P_i)

    # 计算 P_e (期望一致性随机发生的一致性)
    P_e = np.sum(p_j**2)

    # 计算 Kappa
    if P_e == 1:
        # fix(D10, 2026-07-14): 原分支返回裸标量 1.0, 与下方正常路径返回
        # (kappa, P_bar, P_e) 三元组不一致 — 调用方 `k, p_bar, p_e = fleiss_kappa(...)`
        # 解包裸 float 会抛 TypeError ('float' object is not iterable)。P_e==1 意味着
        # 全部评估者对每个项目都给出完全相同的单一分类 (期望一致性已饱和), 该退化情形下
        # P_bar 与 P_e 数学上同为 1.0 (自洽), kappa 按惯例记完全一致 = 1.0 (0/0 不定式的
        # 约定取值), 一并以三元组返回保持接口形状恒定。
        return 1.0, 1.0, 1.0
    kappa = (P_bar - P_e) / (1 - P_e)

    return kappa, P_bar, P_e

def _resolve_input(path_arg, sheet_arg):
    """解析输入 xlsx 与 sheet。

    fix(2026-07-21): 原硬编码 v1 冻结件 bank_keywords_20260302_011050.xlsx 已不在盘上
    （历史清理），脚本长期以 Error 收场——改为参数化：--file 指定，缺省取
    data_processed/ 下最新**完整跑**产物；sheet 缺省取全 workbook 通用的
    「5-AI判别结果」（完整跑与 --judge-only 冻结重放产物均含该 sheet）。
    fix(评审C, 2026-07-21): 缺省 glob 收窄为 bank_keywords_2*.xlsx（时间戳前缀）——
    原 bank_keywords_*.xlsx 会把 bank_keywords_judge_replay_* 也纳入且字典序
    'j' > '2' 恒排最后, 缺省永远错选冻结重放件（口径还是 v1 单轮）而非最新完整跑;
    重放件要算 κ 须 --file 显式指定。时间戳文件名字典序即时间序, sorted 末位=最新。
    """
    data_dir = Path(__file__).resolve().parent / 'data_processed'
    path = Path(path_arg) if path_arg else None
    if path is None:
        candidates = sorted(data_dir.glob('bank_keywords_2*.xlsx'))
        if not candidates:
            raise SystemExit("data_processed/ 下无 bank_keywords_2*.xlsx（先跑一次完整流程）")
        path = candidates[-1]
    return path, (sheet_arg or '5-AI判别结果')


try:
    import argparse
    import sys

    # zh-CN Windows 控制台默认 GBK，防非 GBK 字符崩溃（镜像 llm_cache.py CLI 处理）
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")

    _parser = argparse.ArgumentParser(description="Fleiss' Kappa 评分者间一致性（独立离线计算）")
    _parser.add_argument("--file", type=str, default=None, help="判别结果 xlsx（缺省=最新）")
    _parser.add_argument("--sheet", type=str, default=None, help="sheet 名（缺省=5-AI判别结果）")
    _args = _parser.parse_args()

    _xlsx, _sheet = _resolve_input(_args.file, _args.sheet)
    print(f"输入: {_xlsx.name} / sheet={_sheet}")
    df = pd.read_excel(_xlsx, sheet_name=_sheet)

    # 评分列选择（2026-07-21 三轮 self-consistency 改造后双口径兼容）：
    # 优先 {key}_vote（13 家正式票 = 各模型三轮盲审的内部多数，κ 衡量正式票间一致性）；
    # 无 _vote 列（v1 单轮产物）回退 {key}_score（13 次单判）。
    vote_cols = [col for col in df.columns if col.endswith('_vote')]
    legacy_cols = [col for col in df.columns if col.endswith('_score') and col != 'total_score']
    if vote_cols:
        score_cols = vote_cols
        print(f"口径: 三轮 self-consistency 正式票 (_vote 列, 与 v1 单判口径的 κ 不可直接比较)")
    else:
        score_cols = legacy_cols
        print("口径: v1 单轮判别 (_score 列)")
    print(f"找到的评分列 ({len(score_cols)} 个):")
    for col in score_cols:
        print(f"  - {col}")

    # 轮内一致率（仅三轮产物有 _score_r* 列时输出）：3:0 全同 vs 2:1 分歧的占比，
    # 作为模型内 self-consistency 的描述统计（不进 κ）
    r1_cols = [c for c in df.columns if c.endswith('_score_r1')]
    if r1_cols:
        n_rows = len(df)
        print(f"\n模型内三轮一致率 (unanimous 3:0 占比 | split 2:1 占比, N={n_rows}):")
        for c1 in r1_cols:
            base = c1[: -len('_score_r1')]
            c2, c3 = f"{base}_score_r2", f"{base}_score_r3"
            if c2 in df.columns and c3 in df.columns and n_rows:
                same = ((df[c1] == df[c2]) & (df[c2] == df[c3])).mean()
                print(f"  - {base}: {sig4(same * 100)}% | {sig4((1 - same) * 100)}%")

    # 构造评分矩阵 ratings 形状为 (N, k)
    # N = 词语数量, k = 模型数量
    # 取值为 0 或 1，表示类别总数为 2 (0=非银行金融科技, 1=银行金融科技)
    ratings = df[score_cols].values
    
    # 保证所有的值都在 0, 1 之间且没有缺失值
    ratings = np.nan_to_num(ratings, 0)
    ratings = np.clip(ratings, 0, 1)

    k, p_bar, p_e = fleiss_kappa(ratings, n_categories=2)
    lk_band, mh_band = kappa_bands(k)
    print("\n--- Fleiss' Kappa 评分者间一致性检验 (Inter-rater Reliability) ---")
    print(f"方法：多评分者名义量表一致性 {cite('fleiss_1971')}；类别数 = 2 (0=非金融科技, 1=金融科技)。")
    print(f"N (词语总数): {ratings.shape[0]}")
    print(f"k (模型数量/评分者): {ratings.shape[1]}")
    # 所有非整数一律四位有效数字 (sig4)
    print(f"P_bar (实际观测一致性): {sig4(p_bar)}")
    print(f"P_e (偶然预期一致性): {sig4(p_e)}")
    print(f"Fleiss' Kappa 系数 κ: {sig4(k)}")
    print("一致性分级（双口径披露，不分主次）：")
    print(f"  · Landis & Koch (1977): {lk_band}")
    print(f"  · McHugh (2012, 更严):  {mh_band}")
    print(f"  {cite('landis_1977', 'mchugh_2012')}")
    print("一致性系数族与稳健性佐证（不分主次）：")
    print("  · 配对基线 Cohen κ；标准测度 Krippendorff α；对高一致偏态稳健的 Gwet AC1。")
    print("  · ⚠ kappa 悖论：高观测一致 + 偏态边缘分布下 κ 可能偏低（LLM 超多数投票即此场景），宜并观 AC1。")
    print(f"  {cite('cohen_1960', 'hayes_2007', 'gwet_2008', 'feinstein_1990')}")
    print("\n--- 参考文献 (References, APA) ---")
    for ref_line in references_block(_CITED_KAPPA, title="参考文献 (References, APA)"):
        print(ref_line)

except Exception as e:
    print(f"Error: {e}")
