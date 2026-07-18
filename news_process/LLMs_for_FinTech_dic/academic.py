"""
学术化日志支撑模块 (academic logging support)
==================================================

本模块为 LLMs_for_FinTech_dic 子管道的日志输出提供两类学术化基础设施：

1. ``REFERENCES``：经核验的 APA 参考文献注册表 (Single Source of Truth), 共 **121 条**，
   逐条对应本目录手稿 ``FinTech_Dictionary_LLMs_Paper_Final.md`` §6 参考文献书目
   (:265 起, 现为单一字母序合并列表 **146 条**; lockstep: 本注册表 121 条均在其中)。
   ⚠ **严禁自我生成参考文献**：其中 **41 条**取自原核心书目 (文本量化 / 特征字典 /
   大模型验证 / Fleiss κ) 之子集; 另 **80 条**为 2020-2026 重点 (尤重 2024-2026) 的方法学
   锚点补编, 覆盖七类"做法" (群体智能·集成投票 / LLM-as-annotator / 生成式 AI 金融实证 /
   LLM 基座评价 / 金融科技测度 / 词典构建 / 评分者一致性)。该 80 条最初按"做法"分组为
   §6.1 补编, 后由并发整合并入合并后的 §6 字母序书目 (分组结构已被合并取代, 数据不变)。
   **DOI 逐字保留** 且**全部 121 条经 crossref (期刊/SSRN/NBER/会议) 或 DataCite (arXiv)
   实访核验 (121/121 可解析且题名吻合)**；题名/作者列表/标点/大小写按 **APA 7** 规范化校订
   ——曾据此同步修正手稿 §6 中 5 处 APA 笔误 (Thakor "know?." → "know?"、Devlin "Bert" →
   "BERT"、Bubeck "gpt-4" → "GPT-4"、McHugh 副标题 "the" → "The"、Vaswani 由省略号补全
   8 位作者); 补编阶段另修正 widmann 卷期页 (31(2),187-205→31(4),626-641)、bybee 首字母
   (J.L.→L.)、vives DOI (改用可解析的 …100719-120854)。**handle 去冲突**: 提示词综述
   Liu et al. (2023) 与既有 G-Eval ``liu_2023`` 同名, 故改用 handle ``pfliu_2023``。
   任何新增/修改引文，须先在该手稿书目中确有其目、再经 crossref/DataCite 实访核验 DOI
   可解析且题名吻合，方可入册。

2. ``sig4()`` 等格式化工具：所有**非整数**数值在日志中一律保留**四位有效数字**
   (``%.4g``，沿用主项目 news_process 的 ``%.4g`` 惯例)；整数原样输出。

该模块为**纯标准库叶模块**（零第三方依赖、零反向 import），供 00/01/02/
calculate_kappa 等脚本安全 ``from academic import ...``（镜像 ``config`` 的共享模块
定位）。
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List

# ════════════════════════════════════════════════════════════════
# 一、经核验的参考文献注册表 (verbatim from manuscript §6, DO NOT fabricate)
# ════════════════════════════════════════════════════════════════
# 每条: handle -> {year, intext(APA 括注式作者-年), apa(全 APA 含 DOI), doi(裸 DOI
# 供实访核验; 非 DOI 稳定链接者置 None 并在 apa 内保留原链接)}。
# handle 命名 = 首作者姓_年 (多作者取首author)；in-text 遵循 APA 7 (三作者及以上用
# "et al.")。分组注释标注该引文在本管道中的方法学锚定位置。

REFERENCES: Dict[str, Dict] = {
    # ── A. 文本即数据 / 金融文本量化的方法学根基 ──────────────────────
    "gentzkow_2019": {
        "year": 2019,
        "intext": "Gentzkow et al., 2019",
        "apa": "Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020",
        "doi": "10.1257/jel.20181020",
    },
    "kearney_2014": {
        "year": 2014,
        "intext": "Kearney & Liu, 2014",
        "apa": "Kearney, C., & Liu, S. (2014). Textual sentiment in finance: A survey of methods and models. International Review of Financial Analysis, 33, 171-185. https://doi.org/10.1016/j.irfa.2014.02.006",
        "doi": "10.1016/j.irfa.2014.02.006",
    },
    "loughran_2011": {
        "year": 2011,
        "intext": "Loughran & McDonald, 2011",
        "apa": "Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x",
        "doi": "10.1111/j.1540-6261.2010.01625.x",
    },
    "tetlock_2007": {
        "year": 2007,
        "intext": "Tetlock, 2007",
        "apa": "Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x",
        "doi": "10.1111/j.1540-6261.2007.01232.x",
    },
    "tetlock_2008": {
        "year": 2008,
        "intext": "Tetlock et al., 2008",
        "apa": "Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S. (2008). More than words: Quantifying language to measure firms' fundamentals. The Journal of Finance, 63(3), 1437-1467. https://doi.org/10.1111/j.1540-6261.2008.01362.x",
        "doi": "10.1111/j.1540-6261.2008.01362.x",
    },
    "garcia_2023": {
        "year": 2023,
        "intext": "García et al., 2023",
        "apa": "García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006",
        "doi": "10.1016/j.jfineco.2022.11.006",
    },
    # ── B. 专家先验种子词典 / 主题词频测度的先例与局限 ────────────────
    "baker_2006": {
        "year": 2006,
        "intext": "Baker & Wurgler, 2006",
        "apa": "Baker, M., & Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns. The Journal of Finance, 61(4), 1645-1680. https://doi.org/10.1111/j.1540-6261.2006.00885.x",
        "doi": "10.1111/j.1540-6261.2006.00885.x",
    },
    "baker_2016": {
        "year": 2016,
        "intext": "Baker et al., 2016",
        "apa": "Baker, S. R., Bloom, N., & Davis, S. J. (2016). Measuring economic policy uncertainty. The Quarterly Journal of Economics, 131(4), 1593-1636. https://doi.org/10.1093/qje/qjw024",
        "doi": "10.1093/qje/qjw024",
    },
    "hassan_2019": {
        "year": 2019,
        "intext": "Hassan et al., 2019",
        "apa": "Hassan, T. A., Hollander, S., Van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021",
        "doi": "10.1093/qje/qjz021",
    },
    # ── C. 无监督扩容的过度映射 / 假阳性问题 ─────────────────────────
    "blei_2003": {
        "year": 2003,
        "intext": "Blei et al., 2003",
        "apa": "Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet allocation. Journal of Machine Learning Research, 3, 993-1022. https://jmlr.org/papers/v3/blei03a.html",
        "doi": None,
    },
    "hanley_2019": {
        "year": 2019,
        "intext": "Hanley & Hoberg, 2019",
        "apa": "Hanley, K. W., & Hoberg, G. (2019). Dynamic interpretation of emerging risks in the financial sector. The Review of Financial Studies, 32(12), 4543-4603. https://doi.org/10.1093/rfs/hhz023",
        "doi": "10.1093/rfs/hhz023",
    },
    "li_2021": {
        "year": 2021,
        "intext": "Li et al., 2021",
        "apa": "Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. The Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079",
        "doi": "10.1093/rfs/hhaa079",
    },
    # ── D. 金融科技领域界定与银行数字化测度 ──────────────────────────
    "gomber_2018": {
        "year": 2018,
        "intext": "Gomber et al., 2018",
        "apa": "Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766",
        "doi": "10.1080/07421222.2018.1440766",
    },
    "thakor_2020": {
        "year": 2020,
        "intext": "Thakor, 2020",
        "apa": "Thakor, A. V. (2020). Fintech and banking: What do we know? Journal of Financial Intermediation, 41, 100833. https://doi.org/10.1016/j.jfi.2019.100833",
        "doi": "10.1016/j.jfi.2019.100833",
    },
    "philippon_2019": {
        "year": 2019,
        "intext": "Philippon, 2019",
        "apa": "Philippon, T. (2019). On fintech and financial inclusion. National Bureau of Economic Research (No. w26330). https://doi.org/10.3386/w26330",
        "doi": "10.3386/w26330",
    },
    "cheng_2020": {
        "year": 2020,
        "intext": "Cheng & Qu, 2020",
        "apa": "Cheng, M., & Qu, Y. (2020). Does bank FinTech reduce credit risk? Evidence from China. Pacific-Basin Finance Journal, 63, 101398. https://doi.org/10.1016/j.pacfin.2020.101398",
        "doi": "10.1016/j.pacfin.2020.101398",
    },
    "goldstein_2021": {
        "year": 2021,
        "intext": "Goldstein et al., 2021",
        "apa": "Goldstein, I., Spatt, C. S., & Ye, M. (2021). Big data in finance. The Review of Financial Studies, 34(7), 3213-3225. https://doi.org/10.1093/rfs/hhab038",
        "doi": "10.1093/rfs/hhab038",
    },
    # ── E. 大语言模型架构与对齐基石 ─────────────────────────────────
    "vaswani_2017": {
        "year": 2017,
        "intext": "Vaswani et al., 2017",
        "apa": "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. Advances in Neural Information Processing Systems, 30. https://doi.org/10.48550/arXiv.1706.03762",
        "doi": "10.48550/arXiv.1706.03762",
    },
    "devlin_2018": {
        "year": 2018,
        "intext": "Devlin et al., 2018",
        "apa": "Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2018). BERT: Pre-training of deep bidirectional transformers for language understanding. arXiv preprint arXiv:1810.04805. https://doi.org/10.48550/arXiv.1810.04805",
        "doi": "10.48550/arXiv.1810.04805",
    },
    "brown_2020": {
        "year": 2020,
        "intext": "Brown et al., 2020",
        "apa": "Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J. D., ... & Amodei, D. (2020). Language models are few-shot learners. Advances in Neural Information Processing Systems, 33, 1877-1901. https://doi.org/10.48550/arXiv.2005.14165",
        "doi": "10.48550/arXiv.2005.14165",
    },
    "wei_2022": {
        "year": 2022,
        "intext": "Wei et al., 2022",
        "apa": "Wei, J., Wang, X., Schuurmans, D., Bosma, M., Xia, F., ... & Zhou, D. (2022). Chain-of-thought prompting elicits reasoning in large language models. Advances in Neural Information Processing Systems, 35, 24824-24837. https://doi.org/10.48550/arXiv.2201.11903",
        "doi": "10.48550/arXiv.2201.11903",
    },
    "ouyang_2022": {
        "year": 2022,
        "intext": "Ouyang et al., 2022",
        "apa": "Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., ... & Lowe, R. (2022). Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems, 35, 27730-27744. https://doi.org/10.48550/arXiv.2203.02155",
        "doi": "10.48550/arXiv.2203.02155",
    },
    "zhao_2023": {
        "year": 2023,
        "intext": "Zhao et al., 2023",
        "apa": "Zhao, W. X., Zhou, K., Li, J., Tang, T., Wang, X., Hou, Y., ... & Wen, J. R. (2023). A survey of large language models. arXiv preprint arXiv:2303.18223. https://doi.org/10.48550/arXiv.2303.18223",
        "doi": "10.48550/arXiv.2303.18223",
    },
    "bubeck_2023": {
        "year": 2023,
        "intext": "Bubeck et al., 2023",
        "apa": "Bubeck, S., Chandrasekaran, V., Eldan, R., Gehrke, J., Horvitz, E., Kamar, E., ... & Zhang, Y. (2023). Sparks of artificial general intelligence: Early experiments with GPT-4. arXiv preprint arXiv:2303.12712. https://doi.org/10.48550/arXiv.2303.12712",
        "doi": "10.48550/arXiv.2303.12712",
    },
    # ── F. LLM-as-a-Judge / 生成式评价一致性 (本机制的直接理论锚) ──────
    "zheng_2023": {
        "year": 2023,
        "intext": "Zheng et al., 2023",
        "apa": "Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E., & Stoica, I. (2023). Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. Advances in Neural Information Processing Systems, 36. https://doi.org/10.48550/arXiv.2306.05685",
        "doi": "10.48550/arXiv.2306.05685",
    },
    "liu_2023": {
        "year": 2023,
        "intext": "Liu et al., 2023",
        "apa": "Liu, Y., Iter, D., Xu, Y., Wang, S., Xu, R., & Zhu, C. (2023). G-Eval: NLG evaluation using GPT-4 with better human alignment. arXiv. https://doi.org/10.48550/arXiv.2303.16634",
        "doi": "10.48550/arXiv.2303.16634",
    },
    # ── G. 生成式 AI 用于金融 / 会计实证测度 (2020–2026 前沿) ─────────
    "huang_2023": {
        "year": 2023,
        "intext": "Huang et al., 2023",
        "apa": "Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832",
        "doi": "10.1111/1911-3846.12832",
    },
    "wu_2023": {
        "year": 2023,
        "intext": "Wu et al., 2023",
        "apa": "Wu, S., Irsoy, O., Lu, S., Dabravolski, V., Dredze, M., Gehrmann, S., ... & Mann, G. (2023). BloombergGPT: A large language model for finance. arXiv preprint arXiv:2303.17564. https://doi.org/10.48550/arXiv.2303.17564",
        "doi": "10.48550/arXiv.2303.17564",
    },
    "yang_2020": {
        "year": 2020,
        "intext": "Yang et al., 2020",
        "apa": "Yang, Y., Uy, M. C., & Huang, A. (2020). FinBERT: A pretrained language model for financial communications. arXiv preprint arXiv:2006.08097. https://doi.org/10.48550/arXiv.2006.08097",
        "doi": "10.48550/arXiv.2006.08097",
    },
    "dekok_2025": {
        "year": 2025,
        "intext": "de Kok, 2025",
        "apa": "de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253",
        "doi": "10.1287/mnsc.2023.03253",
    },
    "siano_2025": {
        "year": 2025,
        "intext": "Siano, 2025",
        "apa": "Siano, F. (2025). The news in earnings announcement disclosures: Capturing word context using LLM methods. Management Science, 71(11), 9831-9855. https://doi.org/10.1287/mnsc.2024.05417",
        "doi": "10.1287/mnsc.2024.05417",
    },
    "bernard_2026": {
        "year": 2026,
        "intext": "Bernard et al., 2026",
        "apa": "Bernard, D., Blankespoor, E., de Kok, T., & Toynbee, S. (2026). Using GPT to measure business complexity. The Accounting Review, 101(3), 67-102. https://doi.org/10.2308/tar-2023-0716",
        "doi": "10.2308/tar-2023-0716",
    },
    "cao_2024": {
        "year": 2024,
        "intext": "Cao et al., 2024",
        "apa": "Cao, S., Jiang, W., Wang, J., & Yang, B. (2024). From man vs. machine to man + machine: The art and AI of stock analyses. Journal of Financial Economics, 160, 103910. https://doi.org/10.1016/j.jfineco.2024.103910",
        "doi": "10.1016/j.jfineco.2024.103910",
    },
    "lopezlira_2023": {
        "year": 2023,
        "intext": "Lopez-Lira & Tang, 2023",
        "apa": "Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price movements? Return predictability and large language models. Available at SSRN 4412788. https://doi.org/10.2139/ssrn.4412788",
        "doi": "10.2139/ssrn.4412788",
    },
    "fatouros_2023": {
        "year": 2023,
        "intext": "Fatouros et al., 2023",
        "apa": "Fatouros, G., Soldatos, J., Kouroumali, K., Makridis, G., & Kyriazis, D. (2023). Transforming sentiment analysis in the financial domain with ChatGPT. Machine Learning with Applications, 14, 100508. https://doi.org/10.1016/j.mlwa.2023.100508",
        "doi": "10.1016/j.mlwa.2023.100508",
    },
    "kiciman_2023": {
        "year": 2023,
        "intext": "Kıcıman et al., 2023",
        "apa": "Kıcıman, E., Ness, R., Sharma, A., & Tan, C. (2023). Causal reasoning and large language models: Opening a new frontier for causality. arXiv. https://doi.org/10.48550/arXiv.2305.00050",
        "doi": "10.48550/arXiv.2305.00050",
    },
    "gopal_2025": {
        "year": 2025,
        "intext": "Gopal et al., 2025",
        "apa": "Gopal, R. D., Li, J., Riemer, K., Sarker, S., Singh, P. V., Susarla, A., Bichler, M., & Thatcher, J. B. (2025). Inventing with machines: Generative AI and the evolving landscape of IS research. Information Systems Research, 36(4), 1949-1967. https://doi.org/10.1287/isre.2025.editorial.v36.n4",
        "doi": "10.1287/isre.2025.editorial.v36.n4",
    },
    "ye_2024": {
        "year": 2024,
        "intext": "Ye et al., 2024",
        "apa": "Ye, Z., Yoganarasimhan, H., & Zheng, Y. (2024). LOLA: LLM-assisted online learning algorithm for content experiments. SSRN. https://doi.org/10.2139/ssrn.4851778",
        "doi": "10.2139/ssrn.4851778",
    },
    # ── H. 评分者间一致性 / Fleiss' Kappa 统计测度 (§4.2 双口径披露锚) ──
    "fleiss_1971": {
        "year": 1971,
        "intext": "Fleiss, 1971",
        "apa": "Fleiss, J. L. (1971). Measuring nominal scale agreement among many raters. Psychological Bulletin, 76(5), 378-382. https://doi.org/10.1037/h0031619",
        "doi": "10.1037/h0031619",
    },
    "landis_1977": {
        "year": 1977,
        "intext": "Landis & Koch, 1977",
        "apa": "Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159-174. https://doi.org/10.2307/2529310",
        "doi": "10.2307/2529310",
    },
    "mchugh_2012": {
        "year": 2012,
        "intext": "McHugh, 2012",
        "apa": "McHugh, M. L. (2012). Interrater reliability: The kappa statistic. Biochemia Medica, 22(3), 276-282. https://doi.org/10.11613/bm.2012.031",
        "doi": "10.11613/bm.2012.031",
    },

    # ════════════════════════════════════════════════════════════════
    # §6.1 方法学锚点补编 (2020-2026 重点; 全部经 crossref/DataCite 实访核验,
    # 逐条对应手稿 §6.1 补编书目; 严禁自造)。按七类"做法"归组。
    # ════════════════════════════════════════════════════════════════

    # ── A. 群体智能 / 集成学习 / 多智能体投票 (核心机制锚) ────────────────
    "galton_1907": {
        "year": 1907,
        "intext": "Galton, 1907",
        "apa": "Galton, F. (1907). Vox populi. Nature, 75(1949), 450-451. https://doi.org/10.1038/075450a0",
        "doi": "10.1038/075450a0",
    },
    "hong_2004": {
        "year": 2004,
        "intext": "Hong & Page, 2004",
        "apa": "Hong, L., & Page, S. E. (2004). Groups of diverse problem solvers can outperform groups of high-ability problem solvers. Proceedings of the National Academy of Sciences, 101(46), 16385-16389. https://doi.org/10.1073/pnas.0403723101",
        "doi": "10.1073/pnas.0403723101",
    },
    "wolpert_1992": {
        "year": 1992,
        "intext": "Wolpert, 1992",
        "apa": "Wolpert, D. H. (1992). Stacked generalization. Neural Networks, 5(2), 241-259. https://doi.org/10.1016/S0893-6080(05)80023-1",
        "doi": "10.1016/S0893-6080(05)80023-1",
    },
    "breiman_1996": {
        "year": 1996,
        "intext": "Breiman, 1996",
        "apa": "Breiman, L. (1996). Bagging predictors. Machine Learning, 24(2), 123-140. https://doi.org/10.1007/BF00058655",
        "doi": "10.1007/BF00058655",
    },
    "breiman_2001": {
        "year": 2001,
        "intext": "Breiman, 2001",
        "apa": "Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5-32. https://doi.org/10.1023/A:1010933404324",
        "doi": "10.1023/A:1010933404324",
    },
    "dietterich_2000": {
        "year": 2000,
        "intext": "Dietterich, 2000",
        "apa": "Dietterich, T. G. (2000). Ensemble methods in machine learning. In Multiple classifier systems (Lecture Notes in Computer Science, Vol. 1857, pp. 1-15). Springer. https://doi.org/10.1007/3-540-45014-9_1",
        "doi": "10.1007/3-540-45014-9_1",
    },
    "wang_2022": {
        "year": 2022,
        "intext": "Wang et al., 2022",
        "apa": "Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S., Chowdhery, A., & Zhou, D. (2022). Self-consistency improves chain of thought reasoning in language models. arXiv preprint arXiv:2203.11171. https://doi.org/10.48550/arXiv.2203.11171",
        "doi": "10.48550/arXiv.2203.11171",
    },
    "du_2023": {
        "year": 2023,
        "intext": "Du et al., 2023",
        "apa": "Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., & Mordatch, I. (2023). Improving factuality and reasoning in language models through multiagent debate. arXiv preprint arXiv:2305.14325. https://doi.org/10.48550/arXiv.2305.14325",
        "doi": "10.48550/arXiv.2305.14325",
    },
    "liang_2023": {
        "year": 2023,
        "intext": "Liang et al., 2023",
        "apa": "Liang, T., He, Z., Jiao, W., Wang, X., Wang, Y., Wang, R., Yang, Y., Tu, Z., & Shi, S. (2023). Encouraging divergent thinking in large language models through multi-agent debate. arXiv preprint arXiv:2305.19118. https://doi.org/10.48550/arXiv.2305.19118",
        "doi": "10.48550/arXiv.2305.19118",
    },
    "chan_2023": {
        "year": 2023,
        "intext": "Chan et al., 2023",
        "apa": "Chan, C.-M., Chen, W., Su, Y., Yu, J., Xue, W., Zhang, S., Fu, J., & Liu, Z. (2023). ChatEval: Towards better LLM-based evaluators through multi-agent debate. arXiv preprint arXiv:2308.07201. https://doi.org/10.48550/arXiv.2308.07201",
        "doi": "10.48550/arXiv.2308.07201",
    },
    "jiang_2023": {
        "year": 2023,
        "intext": "Jiang et al., 2023",
        "apa": "Jiang, D., Ren, X., & Lin, B. Y. (2023). LLM-Blender: Ensembling large language models with pairwise ranking and generative fusion. arXiv preprint arXiv:2306.02561. https://doi.org/10.48550/arXiv.2306.02561",
        "doi": "10.48550/arXiv.2306.02561",
    },
    "chen_2023": {
        "year": 2023,
        "intext": "Chen et al., 2023",
        "apa": "Chen, J. C.-Y., Saha, S., & Bansal, M. (2023). ReConcile: Round-table conference improves reasoning via consensus among diverse LLMs. arXiv preprint arXiv:2309.13007. https://doi.org/10.48550/arXiv.2309.13007",
        "doi": "10.48550/arXiv.2309.13007",
    },
    "li_2024": {
        "year": 2024,
        "intext": "Li et al., 2024",
        "apa": "Li, J., Zhang, Q., Yu, Y., Fu, Q., & Ye, D. (2024). More agents is all you need. arXiv preprint arXiv:2402.05120. https://doi.org/10.48550/arXiv.2402.05120",
        "doi": "10.48550/arXiv.2402.05120",
    },
    "wang_2024": {
        "year": 2024,
        "intext": "Wang et al., 2024",
        "apa": "Wang, J., Wang, J., Athiwaratkun, B., Zhang, C., & Zou, J. (2024). Mixture-of-agents enhances large language model capabilities. arXiv preprint arXiv:2406.04692. https://doi.org/10.48550/arXiv.2406.04692",
        "doi": "10.48550/arXiv.2406.04692",
    },

    # ── B. LLM-as-annotator / 计算社会科学文本标注 (判别阶段直接锚) ────────
    "gilardi_2023": {
        "year": 2023,
        "intext": "Gilardi et al., 2023",
        "apa": "Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120",
        "doi": "10.1073/pnas.2305016120",
    },
    "ziems_2024": {
        "year": 2024,
        "intext": "Ziems et al., 2024",
        "apa": "Ziems, C., Held, W., Shaikh, O., Chen, J., Zhang, Z., & Yang, D. (2024). Can large language models transform computational social science? Computational Linguistics, 50(1), 237-291. https://doi.org/10.1162/coli_a_00502",
        "doi": "10.1162/coli_a_00502",
    },
    "argyle_2023": {
        "year": 2023,
        "intext": "Argyle et al., 2023",
        "apa": "Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). Out of one, many: Using language models to simulate human samples. Political Analysis, 31(3), 337-351. https://doi.org/10.1017/pan.2023.2",
        "doi": "10.1017/pan.2023.2",
    },
    "rathje_2024": {
        "year": 2024,
        "intext": "Rathje et al., 2024",
        "apa": "Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C. E., & Van Bavel, J. J. (2024). GPT is an effective tool for multilingual psychological text analysis. Proceedings of the National Academy of Sciences, 121(34), e2308950121. https://doi.org/10.1073/pnas.2308950121",
        "doi": "10.1073/pnas.2308950121",
    },
    "grossmann_2023": {
        "year": 2023,
        "intext": "Grossmann et al., 2023",
        "apa": "Grossmann, I., Feinberg, M., Parker, D. C., Christakis, N. A., Tetlock, P. E., & Cunningham, W. A. (2023). AI and the transformation of social science research. Science, 380(6650), 1108-1109. https://doi.org/10.1126/science.adi1778",
        "doi": "10.1126/science.adi1778",
    },
    "bail_2024": {
        "year": 2024,
        "intext": "Bail, 2024",
        "apa": "Bail, C. A. (2024). Can generative AI improve social science? Proceedings of the National Academy of Sciences, 121(21), e2314021121. https://doi.org/10.1073/pnas.2314021121",
        "doi": "10.1073/pnas.2314021121",
    },
    "mellon_2024": {
        "year": 2024,
        "intext": "Mellon et al., 2024",
        "apa": "Mellon, J., Bailey, J., Scott, R., Breckwoldt, J., Miori, M., & Schmedeman, P. (2024). Do AIs know what the most important issue is? Using language models to code open-text social survey responses at scale. Research & Politics, 11(1). https://doi.org/10.1177/20531680241231468",
        "doi": "10.1177/20531680241231468",
    },
    "chae_2025": {
        "year": 2025,
        "intext": "Chae & Davidson, 2025",
        "apa": "Chae, Y., & Davidson, T. (2025). Large language models for text classification: From zero-shot learning to instruction-tuning. Sociological Methods & Research. Advance online publication. https://doi.org/10.1177/00491241251325243",
        "doi": "10.1177/00491241251325243",
    },
    "tornberg_2023": {
        "year": 2023,
        "intext": "Törnberg, 2023",
        "apa": "Törnberg, P. (2023). ChatGPT-4 outperforms experts and crowd workers in annotating political Twitter messages with zero-shot learning. arXiv preprint arXiv:2304.06588. https://doi.org/10.48550/arXiv.2304.06588",
        "doi": "10.48550/arXiv.2304.06588",
    },
    "pangakis_2023": {
        "year": 2023,
        "intext": "Pangakis et al., 2023",
        "apa": "Pangakis, N., Wolken, S., & Fasching, N. (2023). Automated annotation with generative AI requires validation. arXiv preprint arXiv:2306.00176. https://doi.org/10.48550/arXiv.2306.00176",
        "doi": "10.48550/arXiv.2306.00176",
    },
    "he_2024": {
        "year": 2024,
        "intext": "He et al., 2024",
        "apa": "He, X., Lin, Z., Gong, Y., Jin, A.-L., Zhang, H., Lin, C., Jiao, J., Yiu, S. M., Duan, N., & Chen, W. (2024). AnnoLLM: Making large language models to be better crowdsourced annotators. In Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 6: Industry Track) (pp. 165-190). Association for Computational Linguistics. https://doi.org/10.18653/v1/2024.naacl-industry.15",
        "doi": "10.18653/v1/2024.naacl-industry.15",
    },

    # ── C. 生成式 AI 用于金融/会计实证测度 (2024-2026 前沿) ────────────────
    # ⚠ kim_2024 (Financial Statement Analysis) 之 arXiv 版被作者撤回; 此处引 SSRN
    #    工作论文版 (DOI 可解析)。若顶刊投稿避免引用撤回稿, 可改用 kim_2023 替代。
    "kim_2024": {
        "year": 2024,
        "intext": "Kim et al., 2024",
        "apa": "Kim, A. G., Muhn, M., & Nikolaev, V. V. (2024). Financial statement analysis with large language models. SSRN Electronic Journal. https://doi.org/10.2139/ssrn.4835311",
        "doi": "10.2139/ssrn.4835311",
    },
    "jha_2024a": {
        "year": 2024,
        "intext": "Jha et al., 2024a",
        "apa": "Jha, M., Qian, J., Weber, M., & Yang, B. (2024a). ChatGPT and corporate policies. National Bureau of Economic Research (No. w32161). https://doi.org/10.3386/w32161",
        "doi": "10.3386/w32161",
    },
    "eisfeldt_2023": {
        "year": 2023,
        "intext": "Eisfeldt et al., 2023",
        "apa": "Eisfeldt, A. L., Schubert, G., & Zhang, M. B. (2023). Generative AI and firm values. National Bureau of Economic Research (No. w31222). https://doi.org/10.3386/w31222",
        "doi": "10.3386/w31222",
    },
    "hansen_2023": {
        "year": 2023,
        "intext": "Hansen & Kazinnik, 2023",
        "apa": "Hansen, A. L., & Kazinnik, S. (2023). Can ChatGPT decipher Fedspeak? SSRN Electronic Journal. https://doi.org/10.2139/ssrn.4399406",
        "doi": "10.2139/ssrn.4399406",
    },
    "glasserman_2023": {
        "year": 2023,
        "intext": "Glasserman & Lin, 2023",
        "apa": "Glasserman, P., & Lin, C. (2023). Assessing look-ahead bias in stock return predictions generated by GPT sentiment analysis. arXiv preprint arXiv:2309.17322. https://doi.org/10.48550/arXiv.2309.17322",
        "doi": "10.48550/arXiv.2309.17322",
    },
    "bybee_2023": {
        "year": 2023,
        "intext": "Bybee, 2023",
        "apa": "Bybee, L. (2023). Surveying generative AI's economic expectations. arXiv preprint arXiv:2305.02823. https://doi.org/10.48550/arXiv.2305.02823",
        "doi": "10.48550/arXiv.2305.02823",
    },
    "kirtac_2024": {
        "year": 2024,
        "intext": "Kirtac & Germano, 2024",
        "apa": "Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227",
        "doi": "10.1016/j.frl.2024.105227",
    },
    "jha_2024b": {
        "year": 2024,
        "intext": "Jha et al., 2024b",
        "apa": "Jha, M., Qian, J., Weber, M., & Yang, B. (2024b). Harnessing generative AI for economic insights. SSRN Electronic Journal. https://doi.org/10.2139/ssrn.4976759",
        "doi": "10.2139/ssrn.4976759",
    },
    "kim_2023": {
        "year": 2023,
        "intext": "Kim et al., 2023",
        "apa": "Kim, A. G., Muhn, M., & Nikolaev, V. V. (2023). Bloated disclosures: Can ChatGPT help investors process information? SSRN Electronic Journal. https://doi.org/10.2139/ssrn.4425527",
        "doi": "10.2139/ssrn.4425527",
    },

    # ── D. LLM 基座/评价/提示工程/解码 方法学 ──────────────────────────────
    "ji_2023": {
        "year": 2023,
        "intext": "Ji et al., 2023",
        "apa": "Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., Ishii, E., Bang, Y. J., Madotto, A., & Fung, P. (2023). Survey of hallucination in natural language generation. ACM Computing Surveys, 55(12), 1-38. https://doi.org/10.1145/3571730",
        "doi": "10.1145/3571730",
    },
    "huang_2025": {
        "year": 2025,
        "intext": "Huang et al., 2025",
        "apa": "Huang, L., Yu, W., Ma, W., Zhong, W., Feng, Z., Wang, H., Chen, Q., Peng, W., Feng, X., Qin, B., & Liu, T. (2025). A survey on hallucination in large language models: Principles, taxonomy, challenges, and open questions. ACM Transactions on Information Systems, 43(2), 1-55. https://doi.org/10.1145/3703155",
        "doi": "10.1145/3703155",
    },
    "chang_2024": {
        "year": 2024,
        "intext": "Chang et al., 2024",
        "apa": "Chang, Y., Wang, X., Wang, J., Wu, Y., Yang, L., Zhu, K., Chen, H., Yi, X., Wang, C., Wang, Y., Ye, W., Zhang, Y., Chang, Y., Yu, P. S., Yang, Q., & Xie, X. (2024). A survey on evaluation of large language models. ACM Transactions on Intelligent Systems and Technology, 15(3), 1-45. https://doi.org/10.1145/3641289",
        "doi": "10.1145/3641289",
    },
    "pfliu_2023": {
        "year": 2023,
        "intext": "Liu, Yuan, et al., 2023",
        "apa": "Liu, P., Yuan, W., Fu, J., Jiang, Z., Hayashi, H., & Neubig, G. (2023). Pre-train, prompt, and predict: A systematic survey of prompting methods in natural language processing. ACM Computing Surveys, 55(9), 1-35. https://doi.org/10.1145/3560815",
        "doi": "10.1145/3560815",
    },
    "kojima_2022": {
        "year": 2022,
        "intext": "Kojima et al., 2022",
        "apa": "Kojima, T., Gu, S. S., Reid, M., Matsuo, Y., & Iwasawa, Y. (2022). Large language models are zero-shot reasoners. arXiv preprint arXiv:2205.11916. https://doi.org/10.48550/arXiv.2205.11916",
        "doi": "10.48550/arXiv.2205.11916",
    },
    "holtzman_2019": {
        "year": 2019,
        "intext": "Holtzman et al., 2019",
        "apa": "Holtzman, A., Buys, J., Du, L., Forbes, M., & Choi, Y. (2019). The curious case of neural text degeneration. arXiv preprint arXiv:1904.09751. https://doi.org/10.48550/arXiv.1904.09751",
        "doi": "10.48550/arXiv.1904.09751",
    },
    "minaee_2024": {
        "year": 2024,
        "intext": "Minaee et al., 2024",
        "apa": "Minaee, S., Mikolov, T., Nikzad, N., Chenaghlu, M., Socher, R., Amatriain, X., & Gao, J. (2024). Large language models: A survey. arXiv preprint arXiv:2402.06196. https://doi.org/10.48550/arXiv.2402.06196",
        "doi": "10.48550/arXiv.2402.06196",
    },
    "naveed_2023": {
        "year": 2023,
        "intext": "Naveed et al., 2023",
        "apa": "Naveed, H., Khan, A. U., Qiu, S., Saqib, M., Anwar, S., Usman, M., Akhtar, N., Barnes, N., & Mian, A. (2023). A comprehensive overview of large language models. arXiv preprint arXiv:2307.06435. https://doi.org/10.48550/arXiv.2307.06435",
        "doi": "10.48550/arXiv.2307.06435",
    },
    "dong_2023": {
        "year": 2023,
        "intext": "Dong et al., 2023",
        "apa": "Dong, Q., Li, L., Dai, D., Zheng, C., Ma, J., Li, R., Xia, H., Xu, J., Wu, Z., Chang, B., Sun, X., Li, L., & Sui, Z. (2023). A survey on in-context learning. arXiv preprint arXiv:2301.00234. https://doi.org/10.48550/arXiv.2301.00234",
        "doi": "10.48550/arXiv.2301.00234",
    },
    "gu_2024": {
        "year": 2024,
        "intext": "Gu et al., 2024",
        "apa": "Gu, J., Jiang, X., Shi, Z., Tan, H., Zhai, X., Xu, C., Li, W., Shen, Y., Ma, S., Liu, H., Wang, Y., & Guo, J. (2024). A survey on LLM-as-a-judge. arXiv preprint arXiv:2411.15594. https://doi.org/10.48550/arXiv.2411.15594",
        "doi": "10.48550/arXiv.2411.15594",
    },

    # ── E. 金融科技 / 银行数字化测度 (含中国) ──────────────────────────────
    "berg_2020": {
        "year": 2020,
        "intext": "Berg et al., 2020",
        "apa": "Berg, T., Burg, V., Gombović, A., & Puri, M. (2020). On the rise of FinTechs: Credit scoring using digital footprints. The Review of Financial Studies, 33(7), 2845-2897. https://doi.org/10.1093/rfs/hhz099",
        "doi": "10.1093/rfs/hhz099",
    },
    "fuster_2019": {
        "year": 2019,
        "intext": "Fuster et al., 2019",
        "apa": "Fuster, A., Plosser, M., Schnabl, P., & Vickery, J. (2019). The role of technology in mortgage lending. The Review of Financial Studies, 32(5), 1854-1899. https://doi.org/10.1093/rfs/hhz018",
        "doi": "10.1093/rfs/hhz018",
    },
    "chen_2019": {
        "year": 2019,
        "intext": "Chen et al., 2019",
        "apa": "Chen, M. A., Wu, Q., & Yang, B. (2019). How valuable is FinTech innovation? The Review of Financial Studies, 32(5), 2062-2106. https://doi.org/10.1093/rfs/hhy130",
        "doi": "10.1093/rfs/hhy130",
    },
    "buchak_2018": {
        "year": 2018,
        "intext": "Buchak et al., 2018",
        "apa": "Buchak, G., Matvos, G., Piskorski, T., & Seru, A. (2018). Fintech, regulatory arbitrage, and the rise of shadow banks. Journal of Financial Economics, 130(3), 453-483. https://doi.org/10.1016/j.jfineco.2018.03.011",
        "doi": "10.1016/j.jfineco.2018.03.011",
    },
    "dacunto_2019": {
        "year": 2019,
        "intext": "D'Acunto et al., 2019",
        "apa": "D'Acunto, F., Prabhala, N., & Rossi, A. G. (2019). The promises and pitfalls of robo-advising. The Review of Financial Studies, 32(5), 1983-2020. https://doi.org/10.1093/rfs/hhz014",
        "doi": "10.1093/rfs/hhz014",
    },
    "stulz_2019": {
        "year": 2019,
        "intext": "Stulz, 2019",
        "apa": "Stulz, R. M. (2019). FinTech, BigTech, and the future of banks. Journal of Applied Corporate Finance, 31(4), 86-97. https://doi.org/10.1111/jacf.12378",
        "doi": "10.1111/jacf.12378",
    },
    "vives_2019": {
        "year": 2019,
        "intext": "Vives, 2019",
        "apa": "Vives, X. (2019). Digital disruption in banking. Annual Review of Financial Economics, 11, 243-272. https://doi.org/10.1146/annurev-financial-100719-120854",
        "doi": "10.1146/annurev-financial-100719-120854",
    },
    "boot_2021": {
        "year": 2021,
        "intext": "Boot et al., 2021",
        "apa": "Boot, A., Hoffmann, P., Laeven, L., & Ratnovski, L. (2021). Fintech: What's old, what's new? Journal of Financial Stability, 53, 100836. https://doi.org/10.1016/j.jfs.2020.100836",
        "doi": "10.1016/j.jfs.2020.100836",
    },
    "frost_2019": {
        "year": 2019,
        "intext": "Frost et al., 2019",
        "apa": "Frost, J., Gambacorta, L., Huang, Y., Shin, H. S., & Zbinden, P. (2019). BigTech and the changing structure of financial intermediation. Economic Policy, 34(100), 761-799. https://doi.org/10.1093/epolic/eiaa003",
        "doi": "10.1093/epolic/eiaa003",
    },
    "guo_2022": {
        "year": 2022,
        "intext": "Guo & Wang, 2022",
        "apa": "Guo, F., & Wang, J. (2022). Quantifying digital financial inclusion in China. In The digital financial revolution in China. Brookings Institution Press. https://doi.org/10.5040/9780815750420.ch-002",
        "doi": "10.5040/9780815750420.ch-002",
    },
    "cornelli_2023": {
        "year": 2023,
        "intext": "Cornelli et al., 2023",
        "apa": "Cornelli, G., Frost, J., Gambacorta, L., Rau, P. R., Wardrop, R., & Ziegler, T. (2023). Fintech and big tech credit: Drivers of the growth of digital lending. Journal of Banking & Finance, 148, 106742. https://doi.org/10.1016/j.jbankfin.2022.106742",
        "doi": "10.1016/j.jbankfin.2022.106742",
    },
    "xie_2023": {
        "year": 2023,
        "intext": "Xie & Wang, 2023",
        "apa": "Xie, X., & Wang, S. (2023). Digital transformation of commercial banks in China: Measurement, progress and impact. China Economic Quarterly International, 3(1), 35-45. https://doi.org/10.1016/j.ceqi.2023.03.002",
        "doi": "10.1016/j.ceqi.2023.03.002",
    },
    "berg_2022": {
        "year": 2022,
        "intext": "Berg et al., 2022",
        "apa": "Berg, T., Fuster, A., & Puri, M. (2022). FinTech lending. Annual Review of Financial Economics, 14, 187-207. https://doi.org/10.1146/annurev-financial-101521-112042",
        "doi": "10.1146/annurev-financial-101521-112042",
    },
    "babina_2025": {
        "year": 2025,
        "intext": "Babina et al., 2025",
        "apa": "Babina, T., Bahaj, S., Buchak, G., De Marco, F., Foulis, A., Gornall, W., Mazzola, F., & Yu, T. (2025). Customer data access and fintech entry: Early evidence from open banking. Journal of Financial Economics, 169, 103950. https://doi.org/10.1016/j.jfineco.2024.103950",
        "doi": "10.1016/j.jfineco.2024.103950",
    },

    # ── F. 领域词典/词表构建方法学 & 文本即数据综述 ────────────────────────
    "loughran_2016": {
        "year": 2016,
        "intext": "Loughran & McDonald, 2016",
        "apa": "Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123",
        "doi": "10.1111/1475-679X.12123",
    },
    "loughran_2020": {
        "year": 2020,
        "intext": "Loughran & McDonald, 2020",
        "apa": "Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12, 357-375. https://doi.org/10.1146/annurev-financial-012820-032249",
        "doi": "10.1146/annurev-financial-012820-032249",
    },
    "ash_2023": {
        "year": 2023,
        "intext": "Ash & Hansen, 2023",
        "apa": "Ash, E., & Hansen, S. (2023). Text algorithms in economics. Annual Review of Economics, 15, 659-688. https://doi.org/10.1146/annurev-economics-082222-074352",
        "doi": "10.1146/annurev-economics-082222-074352",
    },
    "bodnaruk_2015": {
        "year": 2015,
        "intext": "Bodnaruk et al., 2015",
        "apa": "Bodnaruk, A., Loughran, T., & McDonald, B. (2015). Using 10-K text to gauge financial constraints. Journal of Financial and Quantitative Analysis, 50(4), 623-646. https://doi.org/10.1017/S0022109015000411",
        "doi": "10.1017/S0022109015000411",
    },
    "jegadeesh_2013": {
        "year": 2013,
        "intext": "Jegadeesh & Wu, 2013",
        "apa": "Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018",
        "doi": "10.1016/j.jfineco.2013.08.018",
    },
    "king_2017": {
        "year": 2017,
        "intext": "King et al., 2017",
        "apa": "King, G., Lam, P., & Roberts, M. E. (2017). Computer-assisted keyword and document set discovery from unstructured text. American Journal of Political Science, 61(4), 971-988. https://doi.org/10.1111/ajps.12291",
        "doi": "10.1111/ajps.12291",
    },
    "sautner_2023": {
        "year": 2023,
        "intext": "Sautner et al., 2023",
        "apa": "Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). Firm-level climate change exposure. The Journal of Finance, 78(3), 1449-1498. https://doi.org/10.1111/jofi.13219",
        "doi": "10.1111/jofi.13219",
    },
    "hassan_2023": {
        "year": 2023,
        "intext": "Hassan et al., 2023",
        "apa": "Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1. The Review of Financial Studies, 36(12), 4919-4964. https://doi.org/10.1093/rfs/hhad044",
        "doi": "10.1093/rfs/hhad044",
    },
    "elhaj_2019": {
        "year": 2019,
        "intext": "El-Haj et al., 2019",
        "apa": "El-Haj, M., Rayson, P., Walker, M., Young, S., & Simaki, V. (2019). In search of meaning: Lessons, resources and next steps for computational analysis of financial discourse. Journal of Business Finance & Accounting, 46(3-4), 265-306. https://doi.org/10.1111/jbfa.12378",
        "doi": "10.1111/jbfa.12378",
    },
    "grennan_2021": {
        "year": 2021,
        "intext": "Grennan & Michaely, 2021",
        "apa": "Grennan, J., & Michaely, R. (2021). FinTechs and the market for financial analysis. Journal of Financial and Quantitative Analysis, 56(6), 1877-1907. https://doi.org/10.1017/S0022109020000721",
        "doi": "10.1017/S0022109020000721",
    },
    "rodriguez_2022": {
        "year": 2022,
        "intext": "Rodriguez & Spirling, 2022",
        "apa": "Rodriguez, P. L., & Spirling, A. (2022). Word embeddings: What works, what doesn't, and how to tell the difference for applied research. The Journal of Politics, 84(1), 101-115. https://doi.org/10.1086/715162",
        "doi": "10.1086/715162",
    },
    "widmann_2023": {
        "year": 2023,
        "intext": "Widmann & Wich, 2023",
        "apa": "Widmann, T., & Wich, M. (2023). Creating and comparing dictionary, word embedding, and transformer-based models to measure discrete emotions in German political text. Political Analysis, 31(4), 626-641. https://doi.org/10.1017/pan.2022.15",
        "doi": "10.1017/pan.2022.15",
    },

    # ── G. 评分者间一致性 / 信度统计 (深化 §4.2 kappa) ────────────────────
    "scott_1955": {
        "year": 1955,
        "intext": "Scott, 1955",
        "apa": "Scott, W. A. (1955). Reliability of content analysis: The case of nominal scale coding. Public Opinion Quarterly, 19(3), 321-325. https://doi.org/10.1086/266577",
        "doi": "10.1086/266577",
    },
    "cohen_1960": {
        "year": 1960,
        "intext": "Cohen, 1960",
        "apa": "Cohen, J. (1960). A coefficient of agreement for nominal scales. Educational and Psychological Measurement, 20(1), 37-46. https://doi.org/10.1177/001316446002000104",
        "doi": "10.1177/001316446002000104",
    },
    "feinstein_1990": {
        "year": 1990,
        "intext": "Feinstein & Cicchetti, 1990",
        "apa": "Feinstein, A. R., & Cicchetti, D. V. (1990). High agreement but low kappa: I. The problems of two paradoxes. Journal of Clinical Epidemiology, 43(6), 543-549. https://doi.org/10.1016/0895-4356(90)90158-L",
        "doi": "10.1016/0895-4356(90)90158-L",
    },
    "krippendorff_2004": {
        "year": 2004,
        "intext": "Krippendorff, 2004",
        "apa": "Krippendorff, K. (2004). Reliability in content analysis: Some common misconceptions and recommendations. Human Communication Research, 30(3), 411-433. https://doi.org/10.1111/j.1468-2958.2004.tb00738.x",
        "doi": "10.1111/j.1468-2958.2004.tb00738.x",
    },
    "hayes_2007": {
        "year": 2007,
        "intext": "Hayes & Krippendorff, 2007",
        "apa": "Hayes, A. F., & Krippendorff, K. (2007). Answering the call for a standard reliability measure for coding data. Communication Methods and Measures, 1(1), 77-89. https://doi.org/10.1080/19312450709336664",
        "doi": "10.1080/19312450709336664",
    },
    "gwet_2008": {
        "year": 2008,
        "intext": "Gwet, 2008",
        "apa": "Gwet, K. L. (2008). Computing inter-rater reliability and its variance in the presence of high agreement. British Journal of Mathematical and Statistical Psychology, 61(1), 29-48. https://doi.org/10.1348/000711006X126600",
        "doi": "10.1348/000711006X126600",
    },
    "artstein_2008": {
        "year": 2008,
        "intext": "Artstein & Poesio, 2008",
        "apa": "Artstein, R., & Poesio, M. (2008). Inter-coder agreement for computational linguistics. Computational Linguistics, 34(4), 555-596. https://doi.org/10.1162/coli.07-034-R2",
        "doi": "10.1162/coli.07-034-R2",
    },
    "krippendorff_2011": {
        "year": 2011,
        "intext": "Krippendorff, 2011",
        "apa": "Krippendorff, K. (2011). Agreement and information in the reliability of coding. Communication Methods and Measures, 5(2), 93-112. https://doi.org/10.1080/19312458.2011.568376",
        "doi": "10.1080/19312458.2011.568376",
    },
    "zapf_2016": {
        "year": 2016,
        "intext": "Zapf et al., 2016",
        "apa": "Zapf, A., Castell, S., Morawietz, L., & Karch, A. (2016). Measuring inter-rater reliability for nominal data—which coefficients and confidence intervals are appropriate? BMC Medical Research Methodology, 16, Article 93. https://doi.org/10.1186/s12874-016-0200-9",
        "doi": "10.1186/s12874-016-0200-9",
    },
    "passonneau_2014": {
        "year": 2014,
        "intext": "Passonneau & Carpenter, 2014",
        "apa": "Passonneau, R. J., & Carpenter, B. (2014). The benefits of a model of annotation. Transactions of the Association for Computational Linguistics, 2, 311-326. https://doi.org/10.1162/tacl_a_00185",
        "doi": "10.1162/tacl_a_00185",
    },
}


# ════════════════════════════════════════════════════════════════
# 二、四位有效数字格式化 (所有非整数数值统一口径)
# ════════════════════════════════════════════════════════════════

def sig4(x: object) -> str:
    """将数值格式化为**四位有效数字** (%.4g)；整数值原样输出；None/NaN/Inf → 'NA'。

    口径：用户规范"所有非整数数字均要保留四位有效数字"。整数（含整数值的
    float，如 12.0）按整数显示；其余走 ``%.4g`` (4 significant figures，
    与主项目 news_process 日志的 %.4g 惯例一致)。
    """
    if x is None:
        return "NA"
    if isinstance(x, bool):  # bool 是 int 子类，单列避免 True→'1'
        return str(x)
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return str(x)
    if math.isnan(xf) or math.isinf(xf):
        return "NA"
    if xf.is_integer():
        return str(int(xf))
    return f"{xf:.4g}"


def pct4(numer: float, denom: float) -> str:
    """百分比 (numer/denom*100)，四位有效数字，附 '%'；分母为 0 → 'NA'。"""
    if not denom:
        return "NA"
    return f"{sig4(numer / denom * 100.0)}%"


# ════════════════════════════════════════════════════════════════
# 三、引文块生成器 (in-text 括注 + 尾部 APA 全表)
# ════════════════════════════════════════════════════════════════

def cite(*handles: str) -> str:
    """返回 APA 括注式 in-text 引用，如 '(Zheng et al., 2023; Liu et al., 2023)'。

    未知 handle 会抛 KeyError（fail-loud，防止悄悄引用不存在的文献）。
    """
    parts = [REFERENCES[h]["intext"] for h in handles]
    return "(" + "; ".join(parts) + ")"


def apa_of(handle: str) -> str:
    """返回单条 handle 的全 APA 字符串。"""
    return REFERENCES[handle]["apa"]


def references_block(handles: Iterable[str], title: str = "本轮日志引用文献 (References cited)") -> List[str]:
    """把一组 handle 渲染为可逐行 logger.info 的 APA 参考文献块（按作者字母序编号）。

    去重 + 按 APA 字符串字母序排序（≈ 按首作者姓氏），返回行列表：标题行 +
    分隔线 + 逐条 "1. <APA>"。所有 DOI/链接均来自 REFERENCES（经核验），
    不在此处新造任何文献。
    """
    seen: Dict[str, str] = {}
    for h in handles:
        if h not in REFERENCES:
            raise KeyError(f"references_block: 未知文献 handle '{h}' (不在 REFERENCES 注册表)")
        seen[h] = REFERENCES[h]["apa"]
    ordered = sorted(seen.values())
    lines = [title, "-" * 72]
    for i, apa in enumerate(ordered, 1):
        lines.append(f"  [{i}] {apa}")
    return lines


def all_dois() -> List[str]:
    """返回全部非空 DOI（供 DOI 核验脚本/工作流实访核对）。"""
    return [v["doi"] for v in REFERENCES.values() if v.get("doi")]
