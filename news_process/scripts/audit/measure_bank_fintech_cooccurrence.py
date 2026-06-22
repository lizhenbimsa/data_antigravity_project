"""scripts/audit/measure_bank_fintech_cooccurrence.py
=======================================================

零成本盘面实测: 量化"句级 银行+金科 共现"覆盖率, 当初**催生**了
一条"银行+金科同句/邻近共现"情感轨 (topic-localization track) 的决策。

注 (2026-06 后续): 该决策已落地 —— _ss 银行+金科同句轨已作并列第三主轨上线
(v3.9.0), stage 12b 邻近共现硬过滤亦已上线 (v3.10.0)。本脚本现为冻结的
一次性度量 (口径仍准确), 不再是活的设计裁决输入。

背景 (见 2026-06 双轨/三轨讨论):
  - 现有 _ctx 轨只锚【银行别名】(extract_entity_context 不碰金科词),
    度量的是"金科文章里、围绕该银行的泛情感", 含罚款/坏账等非金科句。
  - 语料已被 stage 12 硬过滤 (每篇都是 fintech 文章, ≥2 个不同金科词),
    这一步替 ctx 买下了"主题相关"的大部分。
  - 待量化的唯一活的不确定量 = 文章内"主题漂移率":
    在【含目标银行的句子】里, 有多大比例【也含金科词】?
    高 → ctx 已基本主题定位 → 同句轨冗余 → optional;
    低 → 多数银行句不谈金科 → 真漂移 → strongly-recommended。

口径 (全程复用 pipeline 自己的匹配函数, 不另写一套):
  - 分句:        core.text.entity_context._split_sentences (同一 _SENT_SPLIT_RE)
  - 银行句判定:  core.text.ahocorasick.has_unexcluded_occurrence
                 (含 stage 11/13 同款否定模式 + 短名歧义排除) — 与 ctx 锚定同口径
  - 金科句判定:  core.text.ahocorasick.load_fintech_dict 的 AC 自动机,
                 句内出现 ≥1 个金科词即记为金科句 (= 提议轨的"句含金科"定义)
  - 别名:        core.text.entity_context.get_target_aliases (同 ctx 物化)
  - ctx 窗口复刻: 命中句 ± sentence_radius(=1) 邻句, 区间并集 — 与 extract_entity_context 一致

度量:
  A 文章级共现覆盖率 = 含 ≥1 个"银行∧金科"同句的文章占比。
      100%-A = 严格同句轨下会变空文本→NaN→掉行的文章占比 (样本萎缩估计)。
  B 银行句的金科率 (核心漂移指标) = 在所有银行句中, 同时含金科词的占比。
      1-B = 文章内主题漂移率。pooled (按句汇总) 与 per-article 平均各报一遍。
  C ctx 窗口稀释率 = 在实际进入 ctx 窗口的句子 (银行句 ±1 邻句) 中, 含金科词占比。
      预计 < B (±1 邻句进一步稀释)。
  附: 每文"银行∧金科"同句数分布 (0/1/2/≥3), 衡量严格轨保留多少文本。

输出: 控制台报告 + scripts/audit/cooccurrence_measurement.json
运行: python -m news_process.scripts.audit.measure_bank_fintech_cooccurrence
"""
from __future__ import annotations

import json
import os
import statistics
import sys

import pandas as pd

# 路径注入: 让 news_process.* 在任意 cwd 可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.text.ahocorasick import (  # noqa: E402
    has_unexcluded_occurrence,
    load_exclusion_patterns,
    load_fintech_dict,
)
from news_process.core.text.entity_context import (  # noqa: E402
    _split_sentences,
    get_target_aliases,
)

BODY_COL = "内容"
TITLE_COL = "标题"


def _pct(num: int, den: int) -> float:
    return (num / den * 100.0) if den else 0.0


def main() -> None:
    cfg = load_config()
    paths = cfg["paths"]
    out_dir = paths["output_dir"]

    corpus_path = os.path.join(out_dir, "14_news_with_ctx.parquet")
    if not os.path.exists(corpus_path):
        corpus_path = os.path.join(out_dir, "12_fintech_news.parquet")
    df = pd.read_parquet(corpus_path)

    bank_names_file = paths.get("bank_names_file", "")
    fintech_dict_file = paths.get("fintech_dict_file", "")
    excl_file = paths.get(
        "bank_name_exclusions_file",
        os.path.join(os.path.dirname(bank_names_file), "bank_name_exclusions.json"),
    )

    fintech_keywords, fintech_ac = load_fintech_dict(fintech_dict_file)
    neg_ac, short_excl, ctx_win = load_exclusion_patterns(excl_file)
    sentence_radius = cfg.get("context_window", {}).get("sentence_radius", 1)

    def sent_has_fintech(sent: str) -> bool:
        if fintech_ac is None or not sent:
            return False
        for _ in fintech_ac.iter(sent):
            return True
        return False

    def sent_has_bank(sent: str, aliases) -> bool:
        return any(
            has_unexcluded_occurrence(sent, a, neg_ac, short_excl, ctx_win)
            for a in aliases
        )

    # 累加器
    n_rows = len(df)
    n_rows_with_bank = 0          # 有有效 target_bank 的行
    n_short_text = 0             # < 3 句 (ctx 走字符级回退)

    pooled_bank_sents = 0       # 全部银行句 (跨文)
    pooled_bank_and_ft = 0      # 全部 银行∧金科 同句
    pooled_ctx_window_sents = 0  # 进入 ctx 窗口的句子总数
    pooled_ctx_window_ft = 0     # ctx 窗口句中含金科的

    per_article_bank_ft_rate = []   # 每文 B (银行句中金科率), 仅当该文有银行句
    n_articles_have_cooccur = 0     # 至少 1 个 银行∧金科 同句的文章
    cooccur_count_hist = {0: 0, 1: 0, 2: 0, "3+": 0}
    bank_and_ft_per_article = []    # 每文 银行∧金科 同句数

    ctx_contains_ft_article = 0     # content_ctx 文本本身含金科词的文章 (粗 proxy)

    _alias_cache: dict = {}

    for _, row in df.iterrows():
        body = str(row.get(BODY_COL, "") or "")
        target_bank = str(row.get("target_bank", "") or "").strip()
        has_bank = target_bank not in ("", "nan", "None")
        if has_bank:
            n_rows_with_bank += 1
            if target_bank not in _alias_cache:
                _alias_cache[target_bank] = get_target_aliases(
                    target_bank, bank_names_file
                )
            aliases = _alias_cache[target_bank]
        else:
            aliases = []

        # content_ctx proxy: 实际 ctx 输入文本里有没有金科词
        ctx_text = str(row.get("content_ctx", "") or "")
        if sent_has_fintech(ctx_text):
            ctx_contains_ft_article += 1

        sentences = _split_sentences(body)
        n = len(sentences)
        if n < 3:
            n_short_text += 1

        # 逐句标注
        bank_flags = [has_bank and sent_has_bank(s, aliases) for s in sentences]
        ft_flags = [sent_has_fintech(s) for s in sentences]

        bank_idx = [i for i, b in enumerate(bank_flags) if b]
        n_bank_sent = len(bank_idx)
        n_bank_and_ft = sum(1 for i in bank_idx if ft_flags[i])

        pooled_bank_sents += n_bank_sent
        pooled_bank_and_ft += n_bank_and_ft

        if n_bank_sent > 0:
            per_article_bank_ft_rate.append(n_bank_and_ft / n_bank_sent)

        bank_and_ft_per_article.append(n_bank_and_ft)
        if n_bank_and_ft >= 1:
            n_articles_have_cooccur += 1
        if n_bank_and_ft == 0:
            cooccur_count_hist[0] += 1
        elif n_bank_and_ft == 1:
            cooccur_count_hist[1] += 1
        elif n_bank_and_ft == 2:
            cooccur_count_hist[2] += 1
        else:
            cooccur_count_hist["3+"] += 1

        # ctx 窗口复刻 (仅非回退: >=3 句且有银行命中)
        if n >= 3 and bank_idx:
            window = set()
            for i in bank_idx:
                for j in range(max(0, i - sentence_radius),
                               min(n - 1, i + sentence_radius) + 1):
                    window.add(j)
            pooled_ctx_window_sents += len(window)
            pooled_ctx_window_ft += sum(1 for j in window if ft_flags[j])

    # ---- 报告 ----
    A = _pct(n_articles_have_cooccur, n_rows)
    B_pooled = _pct(pooled_bank_and_ft, pooled_bank_sents)
    B_article = (statistics.mean(per_article_bank_ft_rate) * 100.0
                 if per_article_bank_ft_rate else 0.0)
    C = _pct(pooled_ctx_window_ft, pooled_ctx_window_sents)
    ctx_ft_cov = _pct(ctx_contains_ft_article, n_rows)
    mean_cooccur = (statistics.mean(bank_and_ft_per_article)
                    if bank_and_ft_per_article else 0.0)
    median_cooccur = (statistics.median(bank_and_ft_per_article)
                      if bank_and_ft_per_article else 0.0)

    report = {
        "corpus": os.path.basename(corpus_path),
        "n_rows": n_rows,
        "n_rows_with_target_bank": n_rows_with_bank,
        "n_short_text_lt3_sentences": n_short_text,
        "fintech_dict_size": len(fintech_keywords),
        "pooled_bank_sentences": pooled_bank_sents,
        "pooled_bank_and_fintech_sentences": pooled_bank_and_ft,
        "pooled_ctx_window_sentences": pooled_ctx_window_sents,
        "pooled_ctx_window_fintech_sentences": pooled_ctx_window_ft,
        "metric_A_article_cooccur_coverage_pct": round(A, 2),
        "metric_A_articles_zero_cooccur_pct": round(100.0 - A, 2),
        "metric_B_bank_sentence_fintech_rate_pooled_pct": round(B_pooled, 2),
        "metric_B_bank_sentence_fintech_rate_article_avg_pct": round(B_article, 2),
        "metric_B_topic_drift_rate_pooled_pct": round(100.0 - B_pooled, 2),
        "metric_C_ctx_window_fintech_rate_pct": round(C, 2),
        "proxy_content_ctx_contains_fintech_pct": round(ctx_ft_cov, 2),
        "mean_bank_and_ft_sentences_per_article": round(mean_cooccur, 2),
        "median_bank_and_ft_sentences_per_article": median_cooccur,
        "cooccur_count_histogram": cooccur_count_hist,
    }

    print("=" * 72)
    print("  句级 银行+金科 共现 实测报告")
    print("=" * 72)
    print(f"语料: {report['corpus']}  行数(=文章×目标银行对): {n_rows}")
    print(f"  其中有有效 target_bank: {n_rows_with_bank}  "
          f"| <3句(ctx字符级回退): {n_short_text}")
    print(f"金科词典规模: {len(fintech_keywords)} 词")
    print("-" * 72)
    print(f"[A] 文章级共现覆盖率 = {A:.1f}%  "
          f"(含≥1个'银行∧金科'同句的文章: {n_articles_have_cooccur}/{n_rows})")
    print(f"    → 严格同句轨下会变空→掉行的文章: {100.0-A:.1f}%  (样本萎缩估计)")
    print(f"[B] 银行句的金科率 (核心漂移指标):")
    print(f"      pooled(按句)      = {B_pooled:.1f}%   "
          f"({pooled_bank_and_ft}/{pooled_bank_sents} 银行句也含金科)")
    print(f"      per-article(按文均) = {B_article:.1f}%")
    print(f"    → 文章内主题漂移率 (1-B, pooled) = {100.0-B_pooled:.1f}%")
    print(f"[C] ctx窗口(银行句±{sentence_radius}邻句)的金科率 = {C:.1f}%   "
          f"({pooled_ctx_window_ft}/{pooled_ctx_window_sents})")
    print(f"    proxy: content_ctx 文本本身含金科词的文章 = {ctx_ft_cov:.1f}%")
    print("-" * 72)
    print(f"每文 '银行∧金科' 同句数: 均值={mean_cooccur:.2f} 中位={median_cooccur}")
    print(f"  分布  0句: {cooccur_count_hist[0]}  1句: {cooccur_count_hist[1]}  "
          f"2句: {cooccur_count_hist[2]}  ≥3句: {cooccur_count_hist['3+']}")
    print("=" * 72)

    out_json = os.path.join(_HERE, "cooccurrence_measurement.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"已写出: {out_json}")


if __name__ == "__main__":
    main()
