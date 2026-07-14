---
family_id: F109
columns:
- benefit_mean_ctx
- benefit_mean_full
- benefit_mean_lg_ctx
- benefit_mean_lg_full
- benefit_mean_lg_ss
- benefit_mean_ss
unit: 双极余弦投影态度分的 bank-year 等权均值 (无量纲, 取值区间 -1 到 1)
formula: "a_j = cos(s_j, p), p = mean(emb(POSITIVE_ANCHORS)) - mean(emb(NEGATIVE_ANCHORS)); benefit_mean[sfx]_[trk] = mean over j in (target_bank, year) of a_j — 每篇等权 (Jha-Liu-Manela 2026 RFS Eq.2 取 c=1 退化为算术均值); sfx 为空=MAIN Qwen3-Embedding-8B / sfx=_lg 为 text-embedding-3-large co-primary; trk 取 full/ctx/ss 三轨"
producer: news_process/pipeline/features/benefit_society.py::compute_benefit_society_panel (panel runner 步骤 7h-benefit; 下游 EB 收缩消费方 = papers/benefit_society/shrinkage.py)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨物化文本 + ctx_is_fallback / ss_is_fallback)
- 40_article_bank_level (df_exploded 文章-银行级展开, 留篇口径与全面板 full-only 门控一致)
- 27_benefit_direction{_lg}.npy + 27_benefit_embeddings{_lg}_{full,ctx,ss}.npy (cache_embeddings=true 时落盘的审计链路中间产物)
citations:
- doi: 10.1093/rfs/hhaf012
  type: journal
  authors: Jha, M., Liu, H., & Manela, A.
  year: 2026
  title: "Does finance benefit society? A language embedding approach"
  venue: Review of Financial Studies
  vol: 39
  issue: 5
  pages_or_artno: 1227-1266
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: 104218
- doi: 10.3386/w33344
  type: wp
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: NBER Working Paper No. 33344
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: "Sustainability or greenwashing: Evidence from the asset market for industrial pollution"
  venue: The Journal of Finance
  vol: 80
  issue: 2
  pages_or_artno: 699-754
- doi: 10.48550/arXiv.2506.05176
  type: arxiv
  authors: Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J.
  year: 2025
  title: "Qwen3 Embedding: Advancing text embedding and reranking through foundation models"
  venue: arXiv
- doi: 10.18653/v1/2025.emnlp-main.179
  type: journal
  authors: Tang, Y., & Yang, Y.
  year: 2025
  title: "FinMTEB: Finance massive text embedding benchmark"
  venue: Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 3620-3638
- doi: 10.3386/w33651
  type: wp
  authors: Gabaix, X., Koijen, R. S. J., Richmond, R. J., & Yogo, M.
  year: 2025
  title: "Asset embeddings"
  venue: NBER Working Paper No. 33651
- doi: 10.1007/s11156-024-01383-0
  type: journal
  authors: Gutknecht, D.
  year: 2025
  title: "Media coverage of corporate social irresponsibility and firm equity risk"
  venue: Review of Quantitative Finance and Accounting
  vol: 65
  issue: 4
  pages_or_artno: 1373-1403
- doi: 10.1016/j.jfineco.2024.103870
  type: journal
  authors: Cookson, J. A., Lu, R., Mullins, W., & Niessner, M.
  year: 2024
  title: "The social signal"
  venue: Journal of Financial Economics
  vol: 158
  pages_or_artno: 103870
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1057/s41599-024-02921-w
  type: journal
  authors: Chen, X., Wan, P., Ma, Z., & Yang, Y.
  year: 2024
  title: "Does corporate digital transformation restrain ESG decoupling? Evidence from China"
  venue: Humanities and Social Sciences Communications
  vol: 11
  issue: 1
  pages_or_artno: Article 407
- doi: 10.1146/annurev-economics-082222-074352
  type: journal
  authors: Ash, E., & Hansen, S.
  year: 2023
  title: "Text algorithms in economics"
  venue: Annual Review of Economics
  vol: 15
  pages_or_artno: 659-688
- doi: 10.1287/stsc.2023.0188
  type: journal
  authors: Westphal, J. D.
  year: 2023
  title: "Systemic symbolic management, corporate social responsibility, and corporate purpose: A cautionary tale"
  venue: Strategy Science
  vol: 8
  issue: 2
  pages_or_artno: 221-232
- doi: 10.1146/annurev-financial-101521-112042
  type: journal
  authors: Berg, T., Fuster, A., & Puri, M.
  year: 2022
  title: "FinTech lending"
  venue: Annual Review of Financial Economics
  vol: 14
  pages_or_artno: 187-207
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: Li, K., Mai, F., Shen, R., & Yan, X.
  year: 2021
  title: "Measuring corporate culture using machine learning"
  venue: The Review of Financial Studies
  vol: 34
  issue: 7
  pages_or_artno: 3265-3315
- doi: 10.1016/j.pacfin.2020.101398
  type: journal
  authors: Cheng, M., & Qu, Y.
  year: 2020
  title: "Does bank FinTech reduce credit risk? Evidence from China"
  venue: Pacific-Basin Finance Journal
  vol: 63
  pages_or_artno: 101398
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1177/0003122419877135
  type: journal
  authors: Kozlowski, A. C., Taddy, M., & Evans, J. A.
  year: 2019
  title: "The geometry of culture: Analyzing the meanings of class through word embeddings"
  venue: American Sociological Review
  vol: 84
  issue: 5
  pages_or_artno: 905-949
- doi: 10.1287/orsc.2014.0949
  type: journal
  authors: Kim, E.-H., & Lyon, T. P.
  year: 2015
  title: "Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure"
  venue: Organization Science
  vol: 26
  issue: 3
  pages_or_artno: 705-723
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: "10.1057/s41283-026-00203-0"
  title: "Multidimensional digital transformation and bank performance in china"
  authors: "Yang, L., & Yang, P."
  year: 2026
  venue: "Risk Management"
  type: "journal"
  one_sentence_zh: "用多维度指标测量中国银行的数字化转型程度并检验其对银行经营绩效的影响, 呼应本家族关于金融科技对银行经营净效应存在正反两读的文献定位。"
- doi: "10.2139/ssrn.5201335"
  title: "Word2Prices: Embedding Central Bank Communications for Inflation Prediction"
  authors: "Araujo, D., Bokan, N., Comazzi, F., & Lenza, M."
  year: 2025
  venue: "SSRN Electronic Journal"
  type: "wp"
  one_sentence_zh: "用词嵌入表征央行沟通文本并证明其预测力优于词典法与情感指标, 为本家族嵌入投影方法优于词典/情感测度的方法论选择提供跨领域佐证。"
new_dois:
- 10.3386/w33344
- 10.1177/0003122419877135
- "10.1057/s41283-026-00203-0"
- "10.2139/ssrn.5201335"
---

## CORE

【构念与来源】
本家族测量的构念是媒体报道对银行金融科技经营效益的态度, 即一年之内, 媒体在报道某家银行的金融科技或数字化转型活动时, 整体上把这些活动描述为利好该银行自身经营 (提升效率、降低成本、改善风控、拓展客源), 还是损害其经营 (加剧风险、抬高投入、冲击既有业务、引发合规问题)。它回答的不是这家银行被报道了多少 (注意力维度) 或报道语气是否正面 (通用情感维度), 而是一个更窄也更贴近理论的问题: 在媒体叙事中, 金融科技对这家银行到底是资产还是负债。方法论直接移植 Jha, Liu & Manela (2026) 发表于 Review of Financial Studies 的双极锚点语言嵌入框架。该文为回答金融是否有益社会这一问题, 用两组语义上严格对立的锚点句在嵌入空间中差分出一条金融利好社会到金融损害社会的连续语义轴, 再把大规模文本投影到该轴上得到连续态度分。本项目做了一次构念替换: 把社会效益维度换成银行自身经营效益维度, 锚点句改为围绕金融科技对银行经营影响的正负对偶陈述, 其余数学结构逐式保留 (文章级投影对应其第 1.3.2 节式一, bank-year 聚合对应式二)。更上游的方法论先例是 Kozlowski, Taddy & Evans (2019) 的文化几何学: 任何语义维度都可以由成对反义锚点的嵌入差分向量在向量空间中定义, 文本沿该向量的投影即其在该维度上的取态。数据来源是本项目的中文银行金融科技新闻语料: 经 stage 13 银行与金科词邻近共现硬过滤后的文章集, 在 panel runner 中展开为文章-银行级 df_exploded, 三轨文本 (content_full, content_ctx, content_ss) 由 stage 14 ctx_materializer 统一物化。行宇宙的留篇口径与全面板一致, 即 2026-06-29 切换后的 full-only 门控: 一篇文章是否算作银行金科报道只看 llm_verified_full, ctx 与 ss 是 conditional-on-full 的测度轨与稳健轨, 其行宇宙是 full 留篇集的子集。家族六列 = 三轨乘双嵌入模型, 其中 benefit_mean_full 是 benefit_society 论文 paper_spec 的 treatment 主列, benefit_mean_lg_full 是其 co-primary 嵌入对偶, 两者同为 core 列。

【方法学与计算】
计算分三步, 全部实现于 pipeline/features/benefit_society.py 的 compute_benefit_society_panel (panel runner 步骤 7h-benefit)。第一步是锚点轴构建。项目手工定义十对正负极锚点句, 每对正负极遵守单词替换对偶纪律 (例如金融科技提升经营效率对金融科技降低经营效率), 镜像 Jha, Liu & Manela (2026) 表二的构造原则, 目的是让差分轴只编码效益方向而不混入题材、句式或长度差异。全部锚点句经统一嵌入引擎 embed_texts 编码后, 方向向量 p 等于正极句嵌入均值减负极句嵌入均值; 未归一的原始差分向量落盘为 27_benefit_direction (含 sidecar, 记录 model_id、维度与锚点对数), 供 27c alt-anchor 与 placebo 审计链路在同一嵌入空间复算。构建时执行锚点质量自诊断: 每个锚点句在归一化轴上的自投影方向须与其极性一致 (符号容差 anchor_sign_tolerance 默认 0.03), 每对正负极自投影的间隔须超过 anchor_pair_min_margin 默认 0.02, 违例逐条 loud 告警并在日志给出轴锐利度判定, 防止一条不锐利的轴静默进入生产。第二步是文章级投影。每篇文章的轨内文本经同一引擎编码为向量 s_j, 得分 a_j 等于 s_j 与归一化方向向量的余弦相似度, 取值区间负一到一, 正值表示该篇叙事偏向利好经营, 负值表示偏向损害经营。空文本行不送引擎、得分记 NaN; 长文不做 8191 token 预截断, 由引擎自带的朴素分段加 token 加权 mean pooling 覆盖全文 (omni-g-benefit-04 修复, 兑现 full 轨完整语义信号的声称, 长文尾部不再被静默丢弃)。cache_embeddings 开启时, 全长文章嵌入按模型与轨分别落盘 npy 加 sidecar, 行序与 df_exploded 一一对应。第三步是 bank-year 聚合。文章级得分按 target_bank 与 year 分组取等权算术均值得到本家族的 benefit_mean 列; Jha, Liu & Manela (2026) 式二本是覆盖权重加权和, 本项目每篇文章权重相等, 加权和退化为算术均值。同一分组还伴生三个姊妹测度 (均不属本家族): benefit_std 为组内得分标准差 (单观测 bank-year 记 NaN 而非填零, 因只有一篇报道与多篇完全一致在统计上不可区分), benefit_pos_frac 与 benefit_neg_frac 为正负态度文章占比, 其阈值中心采用冻结 sidecar 的首跑全样本 pooled median 而非逐 run 现算; 须强调连续均值列不经过该中心化, 冻结中心只影响占比列。嵌入层面是 co-primary 双轨: canonical 无后缀槽为 Qwen3-Embedding-8B (硅基流动 API, 4096 维; 技术报告见 Zhang et al. 2025), _lg 槽为 text-embedding-3-large (3072 维); 两个 spec 各自独立编码锚点、独立计算方向向量与投影, 维度由嵌入矩阵形状驱动, 全程维度无关。列名规则为 lg 中置: 模型后缀插在基名与轨后缀之间, 即 benefit_mean 加可选 _lg 加轨名, 例如 benefit_mean_lg_ctx 而非 benefit_mean_ctx_lg。co-primary parity 守卫执行 both-or-neither 铁律: 任一侧某轨全体无效时, 同族两侧该轨列一并建列并同置 NaN, 绝不留单边孤儿列; _lg 侧 API 致命错走软降级 (返回全 NaN 得分并告警), MAIN canonical 侧 fail-fast 照常上抛, 不吞离线闸异常。三轨语义: full 轨读 content_full, 即 stage 14 prepend_title 拼接的标题加全文正文, 与词典轨、BERT 轨同源; ctx 轨读 content_ctx, 即标题加目标银行实体窗口文本, 消除同篇内非目标实体的情感污染; ss 轨读 content_ss, 即仅保留同句内同时含目标银行与金科词的句子加减一句窗口, 金科归因最严。ss 回退语义镜像 ctx: 无银行金科同句共现时 content_ss 回退为全文 body 且 ss_is_fallback 置真, 与其余轨共享 n_articles 分母。ctx 与 ss 轨在 content 列缺失时优雅跳过并留日志, 兼容旧 schema。工程确定性口径: 文章文本与锚点句的编码走统一嵌入引擎, token 切块按 cl100k 词表以 8191 上限分段; 嵌入请求受项目级离线守卫约束, 离线环境变量置真时缓存 miss 直接抛错而不付费调 API, 全命中时整条链路可零成本字节级复现; 每个模型乘每条轨的文章嵌入缓存路径彼此独立, 互不覆写。聚合完成后按模型中缀加轨后缀重命名并 merge 回面板, 面板端再跑一次 parity 巡检, 对违例轨两侧列族统一置 NaN 并 loud 告警。

【白话说明】
用大白话讲, 这个指标做的事是: 先写好十对意思针锋相对的句子, 一半说金融科技让银行经营变好, 一半说让银行经营变坏; 把这两组句子都变成高维数字向量, 相减得到一根指向利好经营方向的箭头; 再把每篇新闻也变成向量, 看它跟这根箭头的夹角——夹角小 (余弦大) 说明这篇新闻的说法偏向利好, 夹角大说明偏向损害; 最后把一家银行一年里所有新闻的分数取平均, 就是这家银行这一年在媒体眼中金融科技帮不帮它赚钱的总印象分。之所以要做两套模型 (国产 Qwen 与 OpenAI 各算一遍) 和三种读法 (读全文、只读提到这家银行的段落、只读银行和金融科技出现在同一句里的话), 是为了证明结论不是某一个模型或某一种读法碰巧算出来的。

【文献定位】
本家族处在三支文献的交点上。第一支是经济学文本方法文献: Gentzkow, Kelly & Taddy (2019) 确立了文本即数据的通用框架, Ash & Hansen (2023) 系统评述了嵌入表征相对词袋与词典方法在捕捉语义方向上的优势; 在金融应用侧, Li, Mai, Shen & Yan (2021) 用词嵌入从盈余电话会议文本中测量企业文化, Gabaix, Koijen, Richmond & Yogo (2025) 把嵌入表征推广到资产层面, 而 Jha, Liu & Manela (2026) 的双极锚点投影是其中与本测度数学结构完全同构的直接母锚; Kozlowski, Taddy & Evans (2019) 则提供了差分向量定义语义维度的社会科学理论基础。嵌入模型选择上, Tang & Yang (2025) 的金融文本嵌入基准 FinMTEB 说明通用嵌入在金融域的表现存在系统差异, 这正是本项目坚持双嵌入模型 co-primary 并行而非单模型独断的文献理由; Zhang et al. (2025) 是 canonical 槽 Qwen3 嵌入模型的技术报告。第二支是媒体与银行文献: Cookson, Lu, Mullins & Niessner (2024) 证明媒体信号中注意力与情感是可分离的两个维度, 支持本项目把态度测度 (本家族) 与覆盖强度测度 (fintech_intensity 族) 并行产出而非合并; Cookson, Fox, Gil-Bazo, Imbet & Schiller (2026) 证明媒体与社交叙事能实质性驱动银行挤兑, Fang, Wang, Wang & Yuan (2024) 在中国场景下证明媒体情感影响存款稳定性与银行系统性风险, 共同确立媒体态度对银行经营后果的因果相关性。第三支是金融科技与银行经营文献: Berg, Fuster & Puri (2022) 综述了金融科技信贷的效率与风险两面性, Cheng & Qu (2020) 用中国银行数据检验银行金科投入对信用风险的影响, 说明金融科技对银行经营的净效应在文献中本就存在正反两读, 这正是需要一条连续双极态度轴而非二值分类的原因。Yang & Yang (2026, Risk Management) 用多维度指标测量中国银行的数字化转型程度并检验其对银行经营绩效的影响, 呼应本家族关于金融科技对银行经营净效应存在正反两读的文献定位。Araujo, Bokan, Comazzi & Lenza (2025, SSRN Electronic Journal) 用词嵌入表征央行沟通文本并证明其预测力优于词典法与情感指标, 为本家族嵌入投影方法优于词典/情感测度的方法论选择提供跨领域佐证。此外, 符号管理与脱耦文献 (Westphal 2023; Duchin, Gao & Xu 2025; Chen, Wan & Ma 等 2024; Gutknecht 2025) 提示媒体叙事的效益宣称可能与实质行动脱节, 为把本测度与实质性投入测度对照使用提供理论动机。

【识别策略定位】
benefit_mean_full 是 benefit_society 论文 paper_spec 声明的 treatment 主列 (正文级主处理变量), 其成果变量为银行盈利能力 roa (外部财务面板接入时构造)。识别框架上, 本测度是嵌入派生的生成式回归量 (generated regressor): Ludwig, Mullainathan & Rambachan (2025) 的应用计量框架指出, 由机器学习模型生成的测度进入回归右侧时须正视其测度误差与模型依赖, 本项目的对齐方式是三条。其一, 回归以 bank 与 year 双固定效应吸收投影得分的任何固定水平偏移, 使识别只依赖组内变异, 锚点集或嵌入空间的整体平移不进入估计; 其二, 缺失得分行 listwise 处理, 不以零或均值填补, 避免把无信号伪装成中性态度; 其三, 模型依赖以 co-primary 双嵌入与 27c 替代锚点与 placebo 审计正面暴露而非掩盖。面板级 IV 扩展 (同组 leave-one-out 均值、广义 Bartik、媒体来源 house-style 暴露三引擎) 为处理变量内生性提供工具变量族, 三引擎分别针对三类内生性威胁: leave-one-out 同组均值利用同类银行媒体态度的共同成分作外生变异源, 其构造刻意剔除自身观测以规避 Manski (1993) 反射问题中被解释者与解释者同集合导致的机械相关; 广义 Bartik 工具沿 Goldsmith-Pinkham, Sorkin & Swift (2020) 的份额乘漂移逻辑, 以银行既定的媒体来源结构份额与来源层面态度漂移的乘积作预测变异, 其识别假设 (份额外生) 须在论文正文按该文的诊断清单披露; 媒体来源 house-style 暴露则利用不同媒体机构文风与立场的持久差异 (媒体报道立场影响资产价格的经典证据链自 Tetlock 2007 起确立), 银行被哪些媒体覆盖的历史构成对其当年态度得分形成与银行自身基本面正交的暴露。三 IV 与 OLS 主规格同样服从并排纪律: 每个工具各自 just-identified 单独入 2SLS, 不把多个工具堆进同一条过度识别方程去做联合 Hansen J, 这既是全项目铁律, 也因三工具的排除约束各自成立与否是三个独立的经济学论断, 联合检验的拒绝无法归因。口径铁律必须在此复述: 三轨 full, ctx, ss 之间、canonical 与 _lg 两个 co-primary 嵌入之间, 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨或不同嵌入模型的同构念测度混进同一个 over-identified 的 Hansen J 检验; 每条轨每个模型各进各的回归, 结论以跨规格符号与显著性的一致性呈现, 而不是以联合过度识别检验呈现。跨嵌入模型比较系数时须做标准化 (两个嵌入空间的余弦投影原始尺度不可比), 只比标准化 beta 不比原始水平。推断层面的配套约定: 面板回归按银行聚类稳健标准误, 深度受限的开发面板 (T 为二) 不用于任何推断结论; 多规格并排产生的多重检验问题不靠事后挑选处理, 而是在跨模型稳健性附表框架下用 Romano & Wolf (2005) 逐步降压族错误率程序控制 (该程序以自举重采样保留检验统计量间的相依结构, 比 Bonferroni 类校正在高度相关的同构念规格族上功效损失小得多, 恰合本家族六列高相关的情形), 与项目内其他同构念替代测量族的做法一致。另须区分处理变量与成果变量两套体系: 本家族全部六列都属处理变量测度体系, 成果变量 (roa 等财务指标) 是外部财务面板的哨兵列, 两套体系在 paper_spec 中各自声明, 不可互换角色。

【与相邻测度的构念区分】
第一, 与政策对齐族 (stage 15 与 26 的 authoritative similarity 类测度) 的区别: 后者的锚点是单一政策文本, 测的是像不像政策的单极相似度, 没有方向性; 本家族的锚点是双极对偶句集, 测的是利好还是损害的有向连续轴, 零点有实质语义。第二, 与通用情感族 (词典 tone, LLM 三家投票 tone, BERT tone) 的区别: 通用情感沿 Tetlock (2007) 以降的媒体语气文献传统, 测整篇文本的正负语气, 不锁定金融科技对经营的因果指向; 一篇语气积极但内容与金科经营效益无关的报道, 在通用情感上得高分, 在本轴上投影接近零。方法层面差异同样实质: 词典法计数固定词表命中, 对否定、隐喻与新造词失灵; LLM 投票法输出离散三分类, 丢失强度信息; 本家族的嵌入投影输出连续分, 且语义由锚点句整句定义而非单词表, 能捕捉降本增效这类词典未收录的行业表达。三类测度在面板中并存不冗余: 通用情感是本家族的构念上位近邻, 两者的差值本身携带信息 (语气好但效益归因弱, 提示报道属公关通稿而非实质效益报道)。第三, 与 benefit 四维度分解族 (dimension_analysis 产出的四个子维度乘六轨列族) 的区别: 该族把 benefit 构念分解为多个子维度方向轴, 列名规则同为 lg 中置但属另一家族另一 SSOT; 本家族是单一总效益轴。第四, 与 fintech_intensity 族的区别: 后者测报道与金科语义的贴近强度, 属注意力与暴露维度, 与本家族的态度维度正交 (呼应 Cookson et al. 2024 的注意力情感可分离证据)。第五, 与 EB 收缩变体的区别: papers/benefit_society/shrinkage.py 以分层经验贝叶斯把稀疏 bank-year 单元的均值向同年同省同类型群组均值收缩, 收缩权重为单元抽样方差与先验方差之比的 Morris 闭式矩估计, 群组定义含 year 以杜绝未来信息泄入 (omni-g-benefit-06 修复), 先验方差估计做了单成员组剔除、N 减 k 自由度与抽样噪声扣除三重修正 (omni-g-benefit-03, 07, 09 修复); 本家族是未收缩的原始均值列, 同时是收缩列的直接输入, 两者在回归中作主规格与稳健臂并排使用。

【已知局限与稳健性梯子】
已知局限有五。其一, 锚点句是研究者设计的, 十对锚点的措辞选择构成研究者自由度; 对策是 27c 审计链路在落盘的同一嵌入空间上跑替代锚点与 placebo 轴, 检验结论对锚点措辞的敏感性, 且锚点自诊断闸 (符号容差与对偶间隔) 在每次构轴时机械执行。其二, 余弦投影的原始尺度依赖嵌入空间, canonical 与 _lg 两列的水平不可直接比较, 跨模型只比标准化系数; 换嵌入模型属换测度空间的大改, 须走执行计划并同步删除盘上冻结阈值 sidecar (该 sidecar 记录 model_id, 跨空间误用会 fail-loud 崩 stage 40, 这是刻意的防呆而非缺陷), 但再次强调冻结中心只影响占比姊妹列, 不影响本家族均值列。其三, 稀疏单元噪声: 仅有一至三篇报道的 bank-year 均值抽样方差大, 稳健对策是 EB 收缩臂; 收缩实现的披露事项 (文章级方差缺失时以截面总方差除以篇数作回退代理会系统性低估方差, n_obs 默认取 cell 内全部篇数而非有效得分篇数导致精度高估, ctx 轨差异更大) 已在源码显式声明。其四, 生成式回归量的测度误差与模型漂移: 以固定效应吸收水平项、以双模型并排暴露模型依赖, 并在 manuscript 披露嵌入厂商切换的数值副作用。其五, dev 环境退化: 本机 T=2 开发面板行数极少, ctx 与 ss 轨部分单元退化属预期, 生产口径以 T=18 全量语料为准。稳健性梯子的完整结构是: 双嵌入模型乘三轨共六列互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 纵向再加 EB 收缩臂、std 与正负占比姊妹族、27c 替代锚点与 placebo 审计, 以及面板级三引擎 IV 族。梯子之间正交不交叉, 不做组合爆炸。最后一条须向数据使用者显式声明的语义边界: 本测度是媒体叙事层面的态度, 不是银行金融科技投入的实测经营回报; 媒体宣称与实质行动可能脱耦 (符号管理文献的核心告诫), 且脱耦是双向的: Kim & Lyon (2015) 证明企业披露既有夸大其绿 (greenwash) 也有刻意藏拙 (brownwash) 两个方向, 移植到本语境即媒体叙事既可能高估也可能低估金科的真实经营效益, 测度误差的符号先验上不确定, 不能按单向偏误做机械校正; 因此把本列系数解读为金融科技真实效益的证据是过度解读, 正确的解读是媒体叙事中的效益归因与银行后续财务表现之间的联系; 若研究问题恰是宣称与实质的裂隙, 应把本家族与实质性投入类测度并列建模而非替换使用。同理, 本测度也不应被当作银行披露质量或媒体客观性的度量: 它刻画的是叙事方向的均值, 对叙事真伪保持沉默, 真伪层面的检验属于下游论文的研究设计而非本列的定义。

## VAR: benefit_mean_full

【变体差分】
本列是家族 canonical 主列, 也是 benefit_society 论文 paper_spec 声明的 treatment 主列 (正文级主处理变量), tier 为 core。它在家族六列坐标系中的位置由两个维度共同锁定: 嵌入模型维度取 canonical 无后缀槽, 即 Qwen3-Embedding-8B (硅基流动 API, 4096 维), 列名不带模型中缀; 文本轨道维度取 full 轨, 读 stage 14 物化的 content_full 列, 即 prepend_title 拼接的标题加全文正文, 与词典轨、BERT 轨的 full 文本严格同源 (metric-audit 病根 A 修复后不再用裸空格拼接, 缺列时回退内联 prepend_title 构建)。full 轨的语义定位是完整语义信号: 不裁剪实体窗口、不限定共现句, 把整篇报道的叙事整体投影到经营效益轴上, 因而对文章级主题漂移最包容, 也最接近 Jha, Liu & Manela (2026) 原方法对全文的处理方式。长文经引擎朴素分段加 token 加权 mean pooling 全文覆盖, 无预截断。该列同时承担全家族的门控基准角色: 2026-06-29 起留篇门控为 full-only, 一篇文章是否进入报道宇宙只看 llm_verified_full, 因此本列的行宇宙就是面板的报道宇宙本身, ctx 与 ss 两轨是其子集上的条件测度。作为 treatment 主列, 它是下游一系列构件的锚: EB 收缩变体以它为输入, 27c 替代锚点与 placebo 审计以它的嵌入落盘为输入, 面板 IV 扩展三引擎围绕它构造工具, 论文回归表的主规格列以它为处理变量、以 roa 为成果变量。与家族内其余五列的关系遵守口径铁律: 它与 benefit_mean_lg_full 是 co-primary 关系, 同为主测度、互为稳健性、不分主次, 无后缀是历史命名产物而非等级标记; 它与 ctx, ss 轨列是主轨与条件稳健轨关系; 上述任何配对都各自 just-identified 并排进各自的回归, 严禁混进同一个 over-identified Hansen J。数值语义上, 取值区间负一到一, 正值表示该银行该年的金科报道叙事整体偏利好经营, 数值大小是嵌入空间余弦投影的均值, 只有序数与组内变异意义, 水平本身不跨嵌入空间可比; 该 bank-year 无任何有效得分文章时为 NaN, 下游 listwise 处理不填补。为什么由 full 轨而非归因更严的 ss 轨担任 canonical 主列, 有三层理由: 第一, 忠实性——母锚方法 (Jha, Liu & Manela 2026) 的投影对象就是整篇文档, full 轨与母锚逐式可比, 便于把本项目结果放回该文献坐标系; 第二, 覆盖率——ctx 与 ss 轨的窗口化会产生更多空文本与回退, full 轨在全部留篇上都有非空文本, 均值的有效支撑篇数最大、抽样方差最小; 第三, 研究者自由度最小——窗口半径、实体判定与回退规则都是额外的研究者选择, full 轨不引入任何一个, 把这些选择留给稳健臂去承担。姊妹列关系上, 本列与同分组同轨的 benefit_std_full, benefit_pos_frac_full, benefit_neg_frac_full 共享同一批文章级得分, 分别刻画态度分布的一阶矩、离散度与两尾占比, 属不同家族但常在同一张描述统计表并列; 与 EB 收缩列的关系是原始臂对收缩臂, 收缩臂以本列与 benefit_std_full 为输入, 稀疏单元的回归建议两臂并报。推断口径上, 以本列为处理变量的主规格按银行聚类稳健标准误, 跨规格附表的多重检验由逐步降压族错误率程序 (Romano & Wolf 2005) 统一控制; 三引擎 IV 规格中本列是被工具的内生变量, 每个工具各自 just-identified 单独入方程。白话说一句: 这一列就是全项目回答金融科技在媒体嘴里帮不帮银行赚钱这个问题时, 排在第一位被引用的那一列, 其余五列存在的意义都是证明这一列的答案不是碰巧算出来的, 换个模型换种读法答案依旧。

## VAR: benefit_mean_lg_full

【变体差分】
本列是 canonical 主列 benefit_mean_full 的 _lg co-primary 嵌入对偶, tier 为 core, core 依据是 benefit 家族 treatment 主列的 co-primary 双轨铁律: 两个嵌入槽同为主测度、互为稳健性、严格 parity, 主列进 core 则其对偶必进 core。与 canonical 列的唯一差分维度是嵌入模型: 本列用 text-embedding-3-large (OpenAI 系, 经 yunwu 端点, 3072 维) 编码锚点句与文章文本, 方向向量、投影、聚合的全部数学步骤与 canonical 逐式相同, 由同一段代码在 spec 循环的 _lg 分支执行, 维度由嵌入矩阵形状驱动, 全程维度无关。列名遵守 lg 中置规则: 模型中缀插在基名与轨后缀之间, 即 benefit_mean_lg_full 而非 benefit_mean_full_lg, 这一命名规则与 benefit 维度分解族一致, 检索或改码时不可按尾缀猜列名。parity 守卫是本列语义的一部分: 列的存在性与 canonical 列 both-or-neither, 任一侧 full 轨全体无效时两侧列一并建列并同置 NaN, 不允许单边孤儿; 降级行为却是不对称的, _lg 侧 API 致命错走软降级返回全 NaN 并告警 (防连带炸掉整个 stage), canonical 侧 fail-fast 照常上抛, 离线守卫 NEWS_PROCESS_LLM_OFFLINE 下嵌入缓存 miss 会直接 raise 而不付费调 API。方法论定位上, 双模型并行的理由是金融域嵌入表现的模型间系统差异 (Tang & Yang 2025 的基准证据): 若两条完全独立的嵌入空间在同一锚点构造下给出符号与显著性一致的估计, 结论对嵌入模型选择的依赖即被证伪性检验覆盖; 这也是对 Ludwig, Mullainathan & Rambachan (2025) 生成式回归量告诫的工程化回应, 模型依赖被并排暴露而非藏进单一模型。使用纪律与 canonical 列镜像: 本列与 benefit_mean_full 各自 just-identified 进各自的回归, 严禁两列同时作工具或同时入一条 over-identified Hansen J 检验; 跨模型比较只比标准化系数, 因为两个嵌入空间的余弦投影原始尺度不可比, 水平差异 (含均值平移与方差差异) 是空间几何性质而非信息差异, 回归中由固定效应与标准化共同中和。方向向量与文章嵌入按 _lg 后缀独立落盘, 27c 审计链路可在 _lg 空间独立复算替代锚点与 placebo。两个嵌入空间的差异是实质性的而非形式性的: canonical 槽是在以中文为核心语料之一的开源基座上训练的嵌入模型, _lg 槽是英文为主的商用嵌入模型, 两者的训练语料、对齐目标与维度都不同, 对中文金融语句中隐喻、政策话语与行业黑话的向量化方式可能系统性不同; 若两个空间给出的锚点轴在各自空间内都锐利 (对偶间隔诊断通过) 且投影结论一致, 这一致就跨越了模型谱系的一次真实洗牌, 证据强度远高于同谱系模型间的复算。工程细节上, 本列的锚点句、方向向量与文章嵌入在 _lg 空间从零独立计算并按 _lg 后缀独立落盘缓存, 与 canonical 缓存零共享; token 切块口径与 canonical 一致 (cl100k 词表, 8191 上限, 分段后 token 加权 mean pooling), 离线守卫同样生效, 缓存 miss 在离线态直接抛错。厂商维度须在 manuscript 披露: 项目嵌入历史上经历过厂商切换, canonical 与 _lg 的当前组合是国产与海外双厂商刻意并置, 本列因此兼任厂商稳健性披露的载体。附表呈现约定: 本列与 canonical 主列在跨模型稳健性附表中并排各占一列, 报标准化系数与聚类稳健标准误, 多重检验按逐步降压族错误率程序统一控制; 若两列符号相反, 结论按更保守方向陈述并把分歧本身作为发现披露, 不做事后择优。白话说一句: 这一列是用另一家公司的另一套模型把主列的整个计算从头再做一遍, 两遍答案一致, 主列的结论才算站得住。

## VAR: benefit_mean_ctx

【变体差分】
本列与 canonical 主列的唯一差分维度是文本轨道: 嵌入模型同为无后缀 canonical 槽 Qwen3-Embedding-8B, 但投影文本从 content_full 换成 content_ctx, 即标题加目标银行实体上下文窗口文本 (stage 14 物化, prepend_title 已内嵌标题)。ctx 轨的构念动机是消除实体归因污染: 一篇同时报道多家银行的文章, 其全文投影会把其他银行的金科叙事情感记到目标银行头上, ctx 轨只保留目标银行实体附近的文本窗口, 使态度得分更可归因于目标银行本身。代价是文本变短、上下文变窄, 长篇叙事中远离实体提及处的效益论述会被裁掉, 得分方差通常更大。行宇宙口径: full-only 门控 (2026-06-29) 下本列是 conditional-on-full 的测度轨, 行宇宙为 full 留篇集的子集, content_ctx 列缺失时该轨整体优雅跳过并留日志。源码披露的一个已知精度事项与本列直接相关: 下游 EB 收缩用的 n_obs 默认取 cell 内全部篇数而非该轨有效得分篇数, ctx 轨因窗口化空文本更多, 精度高估在本轨更明显。使用纪律: 本列与 full, ss 轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 论文叙事中它是主轨结论的归因稳健臂, 检验利好经营的叙事信号是否在剥离非目标实体文本后仍然存在。

## VAR: benefit_mean_lg_ctx

【变体差分】
本列在家族坐标系中同时偏离 canonical 两个维度: 嵌入模型取 _lg 槽 text-embedding-3-large (3072 维, lg 中置命名), 文本轨道取 ctx 轨 content_ctx (标题加目标银行实体窗口)。它的语义是两条稳健梯子的交点格: 对 benefit_mean_ctx 而言它是换嵌入空间的 co-primary 对偶, 对 benefit_mean_lg_full 而言它是换文本轨的归因稳健臂。parity 守卫按轨执行: 本列与 benefit_mean_ctx 在 ctx 轨上 both-or-neither, 任一侧全体无效则两侧同建同置 NaN; _lg 侧 API 致命错软降级为全 NaN, 不连带 canonical 侧。方向向量在 _lg 空间独立构轴, 文章 ctx 文本在 _lg 空间独立编码, 与 canonical 空间零共享, 因此本列与 benefit_mean_ctx 的一致性是真正跨空间的独立复验而非同源改算。需要说明的口径边界: 双嵌入与三轨是两条正交梯子, 本列作为交点格存在是因为 co-primary parity 铁律要求每条轨都有双模型孪生 (列名双射), 而非鼓励在回归中做模型乘轨道的交互解读; 使用时它与家族内任何其他列都各自 just-identified 并排、互为稳健性、不分主次, 严禁与任何同构念列混进同一 over-identified Hansen J, 跨模型比较只比标准化系数。典型用法是出现在附表的规格矩阵中, 与其余五列并排呈现符号与显著性的一致性; 若主列结论在本格翻转, 优先怀疑的是 ctx 窗口化在 _lg 空间放大了短文本噪声, 而非构念本身失效, 应对照该格的有效篇数与回退占比再下判断。

## VAR: benefit_mean_lg_ss

【变体差分】
本列同时取 _lg 嵌入槽 (text-embedding-3-large, 3072 维, lg 中置命名) 与 ss 轨文本 content_ss, 是家族中归因口径最严且嵌入空间独立于 canonical 的一格。ss 轨文本仅保留同句内同时含目标银行与金科词的句子加减一句窗口 (半径由 config filtering 的 ss_sentence_radius 控制, 默认一句; 注意该键与 stage 13 共现过滤的 sentence_radius 是两个不同键), 银行侧判定带否定与短名过滤, 金科侧为裸 AC 词表命中, 判定不对称属刻意口径。回退语义必须精确复述: 无银行金科同句共现时 content_ss 回退为全文 body 且 ss_is_fallback 置真, 镜像 ctx 的回退设计, 与其余轨共享 n_articles 分母, 因此本列在回退占比高的单元上语义趋近 full 轨而非缺失。本列与 benefit_mean_ss 构成 ss 轨上的 co-primary 对偶, parity 守卫 both-or-neither 按轨执行, _lg 侧 API 致命错软降级全 NaN 不连坐 canonical。方法论角色: 若利好经营的态度信号在最严归因窗口且换一条独立嵌入空间后仍保持符号一致, 则结论同时对归因污染与嵌入模型选择免疫, 这是家族六格矩阵中证伪力最强的一格, 也因文本最短而噪声最大。使用纪律与全家族一致: 各自 just-identified 并排、互为稳健性不分主次, 严禁混同一 over-identified Hansen J, 跨模型只比标准化系数; 解读本格时应同时报告 ss 轨回退占比, 回退占比高的年份格其信息含量实质接近 full 轨, 不宜当作严归因证据单独引用。

## VAR: benefit_mean_ss

【变体差分】
本列与 canonical 主列的唯一差分维度是文本轨道取 ss 轨: 嵌入模型仍为无后缀 canonical 槽 Qwen3-Embedding-8B (4096 维), 投影文本换为 content_ss, 即仅保留同句内同时含目标银行与金科词的句子加减一句窗口的拼接文本 (stage 14 物化, prepend_title 已含标题)。ss 轨是三轨中金科归因最严的一轨: full 轨包容整篇叙事, ctx 轨锁定目标银行附近, ss 轨进一步要求银行与金科在同一句内共现, 把态度得分钉在银行乘金科的最小语义单元上, 最大限度排除同篇内与金科无关的银行叙事及与目标银行无关的金科叙事。回退语义是本列不可省略的口径: 无共现时 content_ss 回退全文 body 且 ss_is_fallback 置真 (镜像 ctx 回退), 共享 n_articles 分母; 金科词表不可用 (FINTECH_AC 为 None) 时回退标志全真, 属优雅降级而非错误。行宇宙为 full-only 门控下 full 留篇集的子集, content_ss 缺列时该轨优雅跳过。dev T=2 环境下本轨部分单元退化属预期, 生产结论以 T=18 全量为准。使用纪律: 与 full, ctx 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 论文中它是归因最严格的稳健臂, 用于回应审稿人关于全文投影混入无关叙事的质疑; 与 ctx 轨相比, 它的窗口判据从实体邻近收紧到同句共现, 是三轨梯子上语义最窄的一级, 得分方差与回退占比也相应最高。

<!-- rendered-citations:begin -->
Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? A language embedding approach. Review of Financial Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. NBER Working Paper No. 33344 [Working Paper]. https://doi.org/10.3386/w33344
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance, 80(2), 699-754. https://doi.org/10.1111/jofi.13412
Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J. (2025). Qwen3 Embedding: Advancing text embedding and reranking through foundation models. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2506.05176
Tang, Y., & Yang, Y. (2025). FinMTEB: Finance massive text embedding benchmark. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 3620-3638. https://doi.org/10.18653/v1/2025.emnlp-main.179
Gabaix, X., Koijen, R. S. J., Richmond, R. J., & Yogo, M. (2025). Asset embeddings. NBER Working Paper No. 33651 [Working Paper]. https://doi.org/10.3386/w33651
Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. Review of Quantitative Finance and Accounting, 65(4), 1373-1403. https://doi.org/10.1007/s11156-024-01383-0
Cookson, J. A., Lu, R., Mullins, W., & Niessner, M. (2024). The social signal. Journal of Financial Economics, 158, 103870. https://doi.org/10.1016/j.jfineco.2024.103870
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Chen, X., Wan, P., Ma, Z., & Yang, Y. (2024). Does corporate digital transformation restrain ESG decoupling? Evidence from China. Humanities and Social Sciences Communications, 11(1), Article 407. https://doi.org/10.1057/s41599-024-02921-w
Ash, E., & Hansen, S. (2023). Text algorithms in economics. Annual Review of Economics, 15, 659-688. https://doi.org/10.1146/annurev-economics-082222-074352
Westphal, J. D. (2023). Systemic symbolic management, corporate social responsibility, and corporate purpose: A cautionary tale. Strategy Science, 8(2), 221-232. https://doi.org/10.1287/stsc.2023.0188
Berg, T., Fuster, A., & Puri, M. (2022). FinTech lending. Annual Review of Financial Economics, 14, 187-207. https://doi.org/10.1146/annurev-financial-101521-112042
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. The Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Cheng, M., & Qu, Y. (2020). Does bank FinTech reduce credit risk? Evidence from China. Pacific-Basin Finance Journal, 63, 101398. https://doi.org/10.1016/j.pacfin.2020.101398
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Kozlowski, A. C., Taddy, M., & Evans, J. A. (2019). The geometry of culture: Analyzing the meanings of class through word embeddings. American Sociological Review, 84(5), 905-949. https://doi.org/10.1177/0003122419877135
Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure. Organization Science, 26(3), 705-723. https://doi.org/10.1287/orsc.2014.0949
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Yang, L., & Yang, P. (2026). Multidimensional digital transformation and bank performance in china. Risk Management. https://doi.org/10.1057/s41283-026-00203-0
Araujo, D., Bokan, N., Comazzi, F., & Lenza, M. (2025). Word2Prices: Embedding Central Bank Communications for Inflation Prediction. SSRN Electronic Journal [Working Paper]. https://doi.org/10.2139/ssrn.5201335
<!-- rendered-citations:end -->
