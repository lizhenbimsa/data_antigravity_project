"""_gen_manuscripts.py — Generate remaining 4 derivative-paper manuscripts.

P4.2 helper (plan-r3 derivative-paper extension, 2026-05-15)

This script writes:
- 4 papers × 2 langs × {manuscript.tex, refs.bib} = 16 files

Run with: ``python -m news_process.papers._p_plan._gen_manuscripts``

The main paper (bank_fintech_tone) is hand-written separately for higher
quality content; derivative papers share a templated structure.

After running once, this file can be removed (P-plan cleanup).
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

REPO_ROOT = Path(__file__).resolve().parents[3]

# ============================================================================
# Per-paper metadata for substitution
# ============================================================================

PAPERS: dict[str, dict[str, str]] = {
    'benefit_society': {
        'title_en': 'Operating-Benefit Attitude in Bank Media Coverage:\\\\'
                    'A Bipolar Anchor Projection Approach',
        'title_zh': '银行媒体报道中的经营效益态度：\\\\双极锚点投影法',
        'method_en': 'bipolar anchor projection (Jha--Liu--Manela 2026, RFS)',
        'method_zh': '双极锚点投影 (Jha--Liu--Manela 2026 RFS)',
        'main_dv_var_en': 'operating-benefit attitude (\\code{benefit\\_mean\\_full})',
        'main_dv_var_zh': '经营效益态度 (\\code{benefit\\_mean\\_full})',
        'lit_en': 'Three strands: (1)~bipolar anchor projection '
                  '(Jha--Liu--Manela 2026 \\emph{RFS}); '
                  '(2)~symbolic/substantive adoption (Westphal--Zajac 2001 '
                  '\\emph{ASQ}); (3)~text-based corporate-finance measures '
                  '(Hoberg--Phillips 2016 \\emph{JPE}).',
        'lit_zh': '三条主线: (1)~双极锚点投影 (Jha--Liu--Manela 2026 \\emph{RFS}); '
                  '(2)~象征--实质采用 (Westphal--Zajac 2001 \\emph{ASQ}); '
                  '(3)~公司金融文本测度 (Hoberg--Phillips 2016 \\emph{JPE})。',
        'bib_extra': [
            '@article{jha2026benefit,'
            '\n  title={Does Finance Benefit Society? A Language Embedding Approach},'
            '\n  author={Jha, Manish and Liu, Hongyu and Manela, Asaf},'
            '\n  journal={Review of Financial Studies},'
            '\n  volume={39},\n  number={5},\n  pages={1227--1266},'
            '\n  year={2026},\n  doi={10.1093/rfs/hhaf012}\n}',
            '@article{distel2026evidence,'
            '\n  title={From Evidence to Impact: Token vs.\\ Hidden Adoption '
            'in Innovation Research},'
            '\n  author={Distel, Andreas P. and Grimpe, Christoph and Poetz, Marion},'
            '\n  journal={Research Policy},'
            '\n  volume={55},\n  number={3},\n  pages={105426},'
            '\n  year={2026},\n  doi={10.1016/j.respol.2026.105426}\n}',
        ],
    },
    'brokerage_network': {
        'title_en': 'Network Brokerage and Bank Performance:\\\\'
                    'Causal Identification via Second-Order Peer Tone',
        'title_zh': '网络经纪与银行绩效：\\\\基于二阶同业语调的因果识别',
        'method_en': 'network 2SLS (Bramoull\\\'e--Djebbari--Fortin 2009)',
        'method_zh': '网络 2SLS (Bramoull\\\'e--Djebbari--Fortin 2009)',
        'main_dv_var_en': 'first-order peer tone (\\code{peer\\_tone\\_lag1\\_full}) '
                          'instrumented by second-order peer tone',
        'main_dv_var_zh': '一阶同业语调 (\\code{peer\\_tone\\_lag1\\_full}), '
                          '以二阶同业语调作为工具变量',
        'lit_en': '(1)~peer effects identification (Manski 1993 \\emph{RES}); '
                  '(2)~network 2SLS via intransitive triads (Bramoull\\\'e '
                  '\\emph{et~al.}\\ 2009 \\emph{JoE}); (3)~institutional '
                  'brokerage networks (Han \\emph{et~al.}\\ 2024 \\emph{RFS}).',
        'lit_zh': '(1)~同业效应识别 (Manski 1993 \\emph{RES}); '
                  '(2)~利用非传递三元组的网络 2SLS (Bramoull\\\'e \\emph{et~al.}\\ '
                  '2009 \\emph{JoE}); (3)~机构经纪网络 (Han \\emph{et~al.}\\ '
                  '2024 \\emph{RFS})。',
        'bib_extra': [
            '@article{bramoulle2009identification,'
            '\n  title={Identification of Peer Effects through Social Networks},'
            '\n  author={Bramoull\\\'e, Yann and Djebbari, Habiba and Fortin, Bernard},'
            '\n  journal={Journal of Econometrics},'
            '\n  volume={150},\n  number={1},\n  pages={41--55},'
            '\n  year={2009},\n  doi={10.1016/j.jeconom.2008.12.021}\n}',
            '@article{manski1993reflection,'
            '\n  title={Identification of Endogenous Social Effects: The Reflection Problem},'
            '\n  author={Manski, Charles F.},'
            '\n  journal={Review of Economic Studies},'
            '\n  volume={60},\n  number={3},\n  pages={531--542},'
            '\n  year={1993},\n  doi={10.2307/2298123}\n}',
            '@article{han2024brokerage,'
            '\n  title={Institutional Brokerage Networks: Facilitating Liquidity Provision},'
            '\n  author={Han, Ming and Kim, Sang Hyun and Nanda, Vikram and Ramadorai, Tarun},'
            '\n  journal={Review of Financial Studies},'
            '\n  volume={37},\n  number={9},\n  pages={2903--2935},'
            '\n  year={2024},\n  doi={10.1093/rfs/hhae026}\n}',
        ],
    },
    'strategic_diff': {
        'title_en': 'Strategic Differentiation in Bank FinTech Coverage:\\\\'
                    'Multi-Method Text Measures and Their Empirical Performance',
        'title_zh': '银行金融科技报道中的战略差异度：\\\\多方法文本测度及其实证表现',
        'method_en': 'N-nearest-neighbor TF-IDF (Guzman--Li 2023) + product-market '
                     'fluidity (Hoberg--Phillips 2016)',
        'method_zh': 'N-最近邻 TF-IDF (Guzman--Li 2023) + 产品市场流动性 '
                     '(Hoberg--Phillips 2016)',
        'main_dv_var_en': 'strategic differentiation score '
                          '(\\code{strat\\_diff\\_n5})',
        'main_dv_var_zh': '战略差异度分数 (\\code{strat\\_diff\\_n5})',
        'lit_en': '(1)~founding strategy differentiation (Guzman--Li 2023 \\emph{MS}); '
                  '(2)~text-based product-market industries (Hoberg--Phillips 2016 '
                  '\\emph{JPE}); (3)~product-market fluidity (Hoberg--Phillips--Prabhala '
                  '2014 \\emph{JF}); (4)~industry-centroid distance '
                  '(Xie--Fan--Lin 2025 \\emph{Economic Research}).',
        'lit_zh': '(1)~创业战略差异度 (Guzman--Li 2023 \\emph{MS}); '
                  '(2)~文本驱动产品市场行业 (Hoberg--Phillips 2016 \\emph{JPE}); '
                  '(3)~产品市场流动性 (Hoberg--Phillips--Prabhala 2014 \\emph{JF}); '
                  '(4)~行业重心法 (谢佳松--樊嘉诚--林建浩 2025 \\emph{经济研究})。',
        'bib_extra': [
            '@article{guzman2023strategy,'
            '\n  title={Measuring Founding Strategy},'
            '\n  author={Guzman, Jorge and Li, Aishen},'
            '\n  journal={Management Science},'
            '\n  volume={69},\n  number={1},\n  pages={101--118},'
            '\n  year={2023},\n  doi={10.1287/mnsc.2022.4369}\n}',
            '@article{hoberg2016tnic,'
            '\n  title={Text-Based Network Industries and Endogenous Product Differentiation},'
            '\n  author={Hoberg, Gerard and Phillips, Gordon},'
            '\n  journal={Journal of Political Economy},'
            '\n  volume={124},\n  number={5},\n  pages={1423--1465},'
            '\n  year={2016},\n  doi={10.1086/688176}\n}',
        ],
    },
    'llm_peer': {
        'title_en': 'LLM-Generated Peer Identification and Causal Inference '
                    'for Bank FinTech Strategy',
        'title_zh': 'LLM 生成的同业识别与银行金融科技战略的因果推断',
        'method_en': 'LLM-defined peer set (Cao \\emph{et~al.}\\ 2025) + '
                     'leave-one-out instrumental variable',
        'method_zh': 'LLM 定义的同业集 (Cao \\emph{et~al.}\\ 2025) + 留一法工具变量',
        'main_dv_var_en': 'LLM-peer leave-one-out tone IV '
                          '(\\code{llm\\_peer\\_tone\\_iv\\_full})',
        'main_dv_var_zh': 'LLM 同业留一法语调 IV '
                          '(\\code{llm\\_peer\\_tone\\_iv\\_full})',
        'lit_en': '(1)~LLM-based peer identification (Cao \\emph{et~al.}\\ 2025 '
                  '\\emph{RAS}); (2)~Stock--Yogo (2005) weak-instrument testing; '
                  '(3)~Kleibergen--Paap (2006) rank-based identification.',
        'lit_zh': '(1)~基于 LLM 的同业识别 (Cao \\emph{et~al.}\\ 2025 \\emph{RAS}); '
                  '(2)~Stock--Yogo (2005) 弱工具检验; '
                  '(3)~Kleibergen--Paap (2006) 秩识别。',
        'bib_extra': [
            '@article{cao2025genai,'
            '\n  title={Can Generative AI Help Identify Peer Firms?},'
            '\n  author={Cao, Zhiyu and Li, Wei and Wang, Yang and Zhao, Yu},'
            '\n  journal={Review of Asset Studies},'
            '\n  year={2025},\n  note={Forthcoming}\n}',
            '@incollection{stock2005weak,'
            '\n  title={Testing for Weak Instruments in Linear IV Regression},'
            '\n  author={Stock, James H. and Yogo, Motohiro},'
            '\n  booktitle={Identification and Inference for Econometric Models},'
            '\n  pages={80--108},\n  publisher={Cambridge University Press},'
            '\n  year={2005},\n  doi={10.1017/CBO9780511614491.006}\n}',
        ],
    },
}

# ============================================================================
# Templates
# ============================================================================

TEMPLATE_EN = dedent(r"""
    % {paper_id}/drafts/en/manuscript.tex
    % P4.2 manuscript skeleton (plan-r3 derivative-paper extension, 2026-05-15)
    % Compile: xelatex + biber + xelatex × 2

    \input{{../../../_shared/preamble_en.tex}}

    \addbibresource{{refs.bib}}

    \title{{{title_en}}}
    \author{{\NoteThis{{Author names}}}}
    \date{{\today}}

    \begin{{document}}
    \maketitle

    \begin{{abstract}}
    \NoteThis{{Final abstract pending.}}
    Using bank-year media coverage of FinTech and {method_en}, we measure
    {main_dv_var_en} for Chinese listed banks. We find \NoteThis{{key result}}\@.
    \end{{abstract}}

    \section{{Introduction}}\label{{sec:intro}}
    \NoteThis{{Motivate the research question and contribution.}}

    \section{{Literature Review}}\label{{sec:lit}}
    {lit_en}

    \section{{Methodology}}\label{{sec:method}}
    \subsection{{Sample and Data}}
    The bank--year panel covers approximately 164 bank--years
    (2017--2018). All bank--year observations are processed by the
    \code{{news\_process}} pipeline (Phase 9b baseline; see
    \code{{papers\_assets/V6\_METHODOLOGY\_CHANGES.md}}).

    \subsection{{Tone Annotation (F1: Three-Family LLM Validation)}}
    We employ three independent LLM families for sentiment annotation:
    \code{{gpt-5.4-nano}} (OpenAI), \code{{gemini-3.1-flash-lite-preview}}
    (Google), and \code{{deepseek-v4-flash}} (DeepSeek\,/\,Grok). All three
    routed through yunwu.ai (\code{{/v1/chat/completions}}, OpenAI-compatible),
    \code{{temperature=0}}, \code{{seed=42}}. Inter-family agreement reported as
    Cohen's $\kappa$ and Krippendorff's $\alpha$; majority vote with ties marked
    \code{{undefined}} (not \code{{neutral}}).

    \subsection{{Article-Level Coding (F2: Decontamination)}}
    Articles where all three families fail or split three ways are coded
    \emph{{missing}}, not \code{{neutral}}. Bank--FinTech relevance failing
    majority verification is also missing. This eliminates the 81.7\,\%
    contamination in pre-v6 ``neutral'' labels.

    \subsection{{Zero-Observation Semantics (F3: NaN Main Path)}}
    For bank--years with \code{{n\_articles=0}}, similarity-based features
    (\code{{auth\_sim\_*}}, \code{{benefit\_*}}, \code{{article\_sim\_*}}),
    ratios (\code{{token\_adopt\_*}}, \code{{hidden\_adopt\_*}},
    \code{{subst\_adopt\_*}}), and \code{{fintech\_intensity\_mean}} are coded
    as \code{{NaN}}. Counts remain at 0. Listwise deletion follows Allison
    (2001) / Heckman (1979).

    \subsection{{Bartik IV Pruning (F4)}}
    Of approximately 30 candidate Bartik instruments, 28 are removed in v6
    for violating Goldsmith-Pinkham \emph{{et~al.}}\ (2020, \emph{{AER}})
    exogeneity. Retained: \code{{bartik\_type\_iv\_full}} and
    \code{{prov\_leave1out\_tone\_full}}.

    \section{{Data}}\label{{sec:data}}
    \NoteThis{{Descriptive statistics in Table 1 (see \code{{papers/{paper_id}/tables.py:build\_table1}}).}}

    \section{{Main Results}}\label{{sec:main}}
    \NoteThis{{Table 2 from \code{{output/tables/table2\_*.csv}}; Figure 2 coefplot.}}

    \section{{Mechanism}}\label{{sec:mech}}
    \NoteThis{{Table 3 from \code{{output/tables/table3\_*.csv}}; Figure 3.}}

    \section{{Heterogeneity}}\label{{sec:het}}
    \NoteThis{{Table 4 (SOE × paper-specific interactions) from
    \code{{output/tables/table4\_heterogeneity.csv}}.}}

    \section{{Robustness}}\label{{sec:robust}}
    \NoteThis{{Table 5 (paper-specific robustness battery) from
    \code{{output/tables/table5\_*.csv}}.}}

    \section{{Conclusion}}\label{{sec:concl}}
    \NoteThis{{Final discussion and policy implications.}}

    \printbibliography

    \end{{document}}
""").lstrip()


TEMPLATE_ZH = dedent(r"""
    % {paper_id}/drafts/zh/manuscript.tex
    % P4.2 中文 manuscript 骨架 (plan-r3 衍生论文扩展, 2026-05-15)
    % 编译: xelatex + biber + xelatex × 2

    \input{{../../../_shared/preamble_zh.tex}}

    \addbibresource{{refs.bib}}

    \title{{{title_zh}}}
    \author{{\NoteThis{{作者姓名}}}}
    \date{{\today}}

    \begin{{document}}
    \maketitle

    \begin{{abstract}}
    \NoteThis{{最终摘要待定。}}
    本文基于银行—年度金融科技媒体报道, 采用{method_zh},
    度量中国上市银行的{main_dv_var_zh}。我们发现 \NoteThis{{核心结论}}\@。
    \end{{abstract}}

    \section{{引言}}\label{{sec:intro}}
    \NoteThis{{阐释研究问题与贡献。}}

    \section{{文献综述}}\label{{sec:lit}}
    {lit_zh}

    \section{{方法}}\label{{sec:method}}
    \subsection{{样本与数据}}
    银行—年度面板覆盖约 164 个银行—年观测 (2017--2018)。
    所有数据由 \code{{news\_process}} 管线 (Phase 9b 基线) 处理,
    详见 \code{{papers\_assets/V6\_METHODOLOGY\_CHANGES.md}}。

    \subsection{{语调标注 (F1: 三家族 LLM 真三角验证)}}
    采用三个独立 LLM 家族: \code{{gpt-5.4-nano}} (OpenAI)、
    \code{{gemini-3.1-flash-lite-preview}} (Google)、\code{{deepseek-v4-flash}}
    (DeepSeek\,/\,Grok)。统一通过 yunwu.ai (\code{{/v1/chat/completions}},
    OpenAI 兼容) 调用, \code{{temperature=0}}, \code{{seed=42}}。
    家族间一致性以 Cohen's $\kappa$ 与 Krippendorff's $\alpha$ 报告;
    多数投票得最终标签, 平局标 \code{{undefined}} (非 \code{{neutral}})。

    \subsection{{篇章级编码 (F2: 去污染)}}
    三家族全部失败 / 三方分裂者编为\emph{{缺失}} (非 \code{{neutral}});
    银行--金融科技相关性未通过多数验证者亦视为缺失。
    此举消除了 v6 之前 81.7\,\% ``中性'' 标签的污染。

    \subsection{{零观测语义 (F3: NaN 主路径)}}
    对 \code{{n\_articles=0}} 的银行—年, 相似度类特征
    (\code{{auth\_sim\_*}}、\code{{benefit\_*}}、\code{{article\_sim\_*}})、
    比例类 (\code{{token\_adopt\_*}}、\code{{hidden\_adopt\_*}}、
    \code{{subst\_adopt\_*}})、\code{{fintech\_intensity\_mean}} 均编为
    \code{{NaN}}; 计数类保持 0。回归采用列删除 (Allison 2001 / Heckman 1979)。

    \subsection{{Bartik IV 修剪 (F4)}}
    约 30 个候选 Bartik 工具变量中, 28 个在 v6 中因违反
    Goldsmith-Pinkham \emph{{et~al.}}\ (2020, \emph{{AER}}) 外生性被删除。
    保留: \code{{bartik\_type\_iv\_full}} 与 \code{{prov\_leave1out\_tone\_full}}。

    \section{{数据描述}}\label{{sec:data}}
    \NoteThis{{Table 1 描述统计参见 \code{{papers/{paper_id}/tables.py:build\_table1}}。}}

    \section{{基准回归}}\label{{sec:main}}
    \NoteThis{{Table 2 源自 \code{{output/tables/table2\_*.csv}}; Figure 2 系数图。}}

    \section{{机制检验}}\label{{sec:mech}}
    \NoteThis{{Table 3 源自 \code{{output/tables/table3\_*.csv}}; Figure 3。}}

    \section{{异质性}}\label{{sec:het}}
    \NoteThis{{Table 4 (SOE × 论文专属交互) 源自
    \code{{output/tables/table4\_heterogeneity.csv}}。}}

    \section{{稳健性}}\label{{sec:robust}}
    \NoteThis{{Table 5 (论文专属稳健性矩阵) 源自
    \code{{output/tables/table5\_*.csv}}。}}

    \section{{结论}}\label{{sec:concl}}
    \NoteThis{{最终讨论与政策含义。}}

    \printbibliography

    \end{{document}}
""").lstrip()


BIB_SHARED = dedent("""
    % papers_assets/<paper_id>/drafts/<lang>/refs.bib
    % P4.2 (plan-r3 derivative-paper extension, 2026-05-15)
    % Shared foundational references; paper-specific entries appended below.

    @article{hassan2019firm,
      title={Firm-Level Political Risk: Measurement and Effects},
      author={Hassan, Tarek A. and Hollander, Stephan and {van Lent}, Laurence and Tahoun, Ahmed},
      journal={Quarterly Journal of Economics},
      volume={134}, number={4}, pages={2135--2202}, year={2019},
      doi={10.1093/qje/qjz021}
    }

    @article{goldsmith2020bartik,
      title={Bartik Instruments: What, When, Why, and How},
      author={Goldsmith-Pinkham, Paul and Sorkin, Isaac and Swift, Henry},
      journal={American Economic Review},
      volume={110}, number={8}, pages={2586--2624}, year={2020},
      doi={10.1257/aer.20181047}
    }

    @article{brambor2006understanding,
      title={Understanding Interaction Models: Improving Empirical Analyses},
      author={Brambor, Thomas and Clark, William R. and Golder, Matt},
      journal={Political Analysis},
      volume={14}, number={1}, pages={63--82}, year={2006},
      doi={10.1093/pan/mpi014}
    }

    @article{cameron2015practitioner,
      title={A Practitioner's Guide to Cluster-Robust Inference},
      author={Cameron, A. Colin and Miller, Douglas L.},
      journal={Journal of Human Resources},
      volume={50}, number={2}, pages={317--372}, year={2015},
      doi={10.3368/jhr.50.2.317}
    }
""").lstrip()


# ============================================================================
# Generator
# ============================================================================

def generate_one(paper_id: str, meta: dict[str, str], dry_run: bool = False) -> list[Path]:
    """Generate manuscript.tex + refs.bib for both en and zh of one paper."""
    paper_root = REPO_ROOT / 'news_process' / 'papers_assets' / paper_id
    written: list[Path] = []

    for lang, template in (('en', TEMPLATE_EN), ('zh', TEMPLATE_ZH)):
        lang_dir = paper_root / 'drafts' / lang
        lang_dir.mkdir(parents=True, exist_ok=True)

        # Manuscript
        body = template.format(paper_id=paper_id, **meta)
        ms_path = lang_dir / 'manuscript.tex'
        if not dry_run:
            ms_path.write_text(body, encoding='utf-8')
        written.append(ms_path)

        # Bibliography
        bib_body = BIB_SHARED + '\n' + '\n\n'.join(meta['bib_extra']) + '\n'
        bib_path = lang_dir / 'refs.bib'
        if not dry_run:
            bib_path.write_text(bib_body, encoding='utf-8')
        written.append(bib_path)

    return written


def main(dry_run: bool = False) -> int:
    total = 0
    for paper_id, meta in PAPERS.items():
        written = generate_one(paper_id, meta, dry_run=dry_run)
        total += len(written)
        for p in written:
            mark = '[plan]' if dry_run else '[OK]'
            print(f'{mark} {p.relative_to(REPO_ROOT)}')
    print(f'\nGenerated {total} files for {len(PAPERS)} papers.')
    return 0


if __name__ == '__main__':
    import sys
    main(dry_run=('--dry-run' in sys.argv))
