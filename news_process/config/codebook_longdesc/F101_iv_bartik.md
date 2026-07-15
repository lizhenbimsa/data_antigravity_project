---
family_id: F101
columns:
- bartik_attention_iv
- bartik_attention_iv_ctx
- bartik_attention_iv_full
- bartik_attention_iv_ss
- bartik_collab_iv_ctx
- bartik_collab_iv_full
- bartik_collab_iv_ss
- bartik_fintech_lc_iv_ctx
- bartik_fintech_lc_iv_full
- bartik_fintech_lc_iv_ss
- bartik_fintech_lf_iv_ctx
- bartik_fintech_lf_iv_full
- bartik_fintech_lf_iv_ss
- bartik_geoprox_iv_ctx
- bartik_geoprox_iv_full
- bartik_geoprox_iv_ss
- bartik_mauth_iv_ctx
- bartik_mauth_iv_full
- bartik_mauth_iv_ss
- bartik_media_iv_ctx
- bartik_media_iv_full
- bartik_media_iv_ss
- bartik_scale_iv_ctx
- bartik_scale_iv_full
- bartik_scale_iv_ss
- bartik_subst_iv_ctx
- bartik_subst_iv_full
- bartik_subst_iv_ss
- bartik_type_iv_ctx
- bartik_type_iv_ctx_t0
- bartik_type_iv_ctx_t01
- bartik_type_iv_ctx_t1
- bartik_type_iv_full
- bartik_type_iv_full_t0
- bartik_type_iv_full_t01
- bartik_type_iv_full_t1
- bartik_type_iv_ss
- bartik_type_iv_ss_t0
- bartik_type_iv_ss_t01
- bartik_type_iv_ss_t1
- bartik_type_share_private
unit: 工具变量 (与该族 shift 源测度同量纲; share 列为 [0,1] 份额)
formula: "BIV_{i,t} = Σ_g share_{i,g,T0} × shift_{g,t}^{LOO(i)}; share 为基期 T0 冻结份额 (T0 = max(panel.year.min, 2010), 强制 < 2019 政策冲击里程碑), shift 为组 g 内剔除银行 i 自身后其余银行文章级测度的年度均值"
producer: pipeline/panel/iv_did.py::compute_bartik_iv + compute_bartik_iv_fintech (runner 步骤 7e) ; pipeline/panel/iv_extensions.py::compute_bartik_shift_iv (runner 步骤 8z) ; pipeline/panel/runner.py (T0 解析 + _t0/_t1/_t01 基期敏感性编排)
upstream:
- "40_article_bank_level (df_exploded 文章级: target_bank / co_mentioned_banks / year)"
- 21_tone_llms.parquet (llm_vote_score_full/_ctx/_ss; innovation_substantiveness_* / innovation_collab_mode_* / innovation_locus_full/_ctx)
- 15_fintech_intensity.parquet (fintech_intensity_score_full/_ctx/_ss)
- config/bank_addresses.json (NFRA 类型 type_map / 企业规模 scale_map / 注册地省份)
- config/media_classification.json (媒体三方分类 fin/comp/other)
- config/media_weights.json (媒体权威性评分 → high/mid/low 档位)
- config/panel.yaml::panel_building.bartik_base_year + bartik_pre_treatment_cutoff
citations:
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: 181-204
- doi: "10.3390/su172210294"
  type: "journal"
  authors: "Qin, Z., & Jing, Z."
  year: 2025
  title: "Fintech Adoption and Credit Risk Mitigation: Evidence from Chinese Commercial Banks"
  venue: "Sustainability"
- doi: 10.48550/arXiv.2504.05658
  type: arxiv
  authors: Luo, S., Shuai, K., Zhang, Y., Li, W., & He, Y.
  year: 2025
  title: "Identification and estimation of causal peer effects using instrumental variables"
  venue: arXiv
- doi: 10.48550/arXiv.2404.17049
  type: arxiv
  authors: Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W.
  year: 2024
  title: "Overidentification in shift-share designs"
  venue: arXiv
- doi: 10.1093/jrsssa/qnad148
  type: journal
  authors: Apfel, N.
  year: 2024
  title: "Relaxing the exclusion restriction in shift-share instrumental variable estimation"
  venue: "Journal of the Royal Statistical Society Series A: Statistics in Society"
  vol: 187
  issue: 3
  pages_or_artno: 748-771
- doi: 10.1086/728743
  type: journal
  authors: Gabaix, X., & Koijen, R. S. J.
  year: 2024
  title: "Granular instrumental variables"
  venue: Journal of Political Economy
  vol: 132
  issue: 7
  pages_or_artno: 2274-2303
- doi: 10.1016/j.jeconom.2024.105727
  type: journal
  authors: Wang, W., & Zhang, Y.
  year: 2024
  title: "Wild bootstrap inference for instrumental variables regressions with weak and few clusters"
  venue: Journal of Econometrics
  vol: 241
  issue: 1
  pages_or_artno: 105727
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: The Review of Economic Studies
  vol: 89
  issue: 1
  pages_or_artno: 181-213
- doi: 10.1257/aer.20211063
  type: journal
  authors: Lee, D. S., McCrary, J., Moreira, M. J., & Porter, J.
  year: 2022
  title: "Valid t-ratio inference for IV"
  venue: American Economic Review
  vol: 112
  issue: 10
  pages_or_artno: 3260-3290
- doi: 10.2308/JFR-2021-003
  type: journal
  authors: Breuer, M.
  year: 2022
  title: "Bartik instruments: An applied introduction"
  venue: Journal of Financial Reporting
  vol: 7
  issue: 1
  pages_or_artno: 49-67
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1177/1536867X20953572
  type: journal
  authors: Dippel, C., Ferrara, A., & Heblich, S.
  year: 2020
  title: "Causal mediation analysis in instrumental-variables regressions"
  venue: The Stata Journal
  vol: 20
  issue: 3
  pages_or_artno: 613-626
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: "Shift-share designs: Theory and inference"
  venue: The Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 1949-2010
- doi: 10.1146/annurev-economics-080218-025643
  type: journal
  authors: Andrews, I., Stock, J. H., & Sun, L.
  year: 2019
  title: "Weak instruments in instrumental variables regression: Theory and practice"
  venue: Annual Review of Economics
  vol: 11
  pages_or_artno: 727-753
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: The Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: "Media bias in China"
  venue: American Economic Review
  vol: 108
  issue: 9
  pages_or_artno: 2442-2476
- doi: 10.1111/j.1540-6261.2010.01626.x
  type: journal
  authors: Engelberg, J. E., & Parsons, C. A.
  year: 2011
  title: "The causal impact of media in financial markets"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 67-97
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: 10.1017/CBO9780511614491.006
  type: book
  authors: Stock, J. H., & Yogo, M.
  year: 2005
  title: "Testing for weak instruments in linear IV regression"
  venue: "Identification and inference for econometric models: Essays in honor of Thomas Rothenberg (Cambridge University Press)"
  pages_or_artno: 80-108
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: "10.1016/j.iref.2024.01.067"
  type: journal
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: "International Review of Economics & Finance"
- doi: "10.1080/00036846.2025.2475245"
  type: journal
  authors: "Xu, M., He, M., & Tang, X."
  year: 2025
  title: "Bank competition and labor share: evidence from China"
  venue: "Applied Economics"
- doi: "10.1016/j.jcorpfin.2025.102935"
  type: journal
  authors: "Bao, Y., & Goetz, M. R."
  year: 2026
  title: "Local peer effects and corporate investment"
  venue: "Journal of Corporate Finance"
new_dois:
- "10.3390/su172210294"
- "10.1016/j.iref.2024.01.067"
- "10.1080/00036846.2025.2475245"
- "10.1016/j.jcorpfin.2025.102935"
---

## CORE

该文用 Bartik/Nunn 式移位-份额工具变量(1984年邮电业务量×全国互联网普及率交互项)识别金融科技采用对中国商业银行信用风险的因果影响, 与 F101 家族的 Bartik 工具变量构念高度相关。

【构念与来源】
本家族是全仓识别策略的核心工具变量族: 广义 Bartik (shift-share) 工具变量引擎在银行年度面板上的全部落列。研究场景中的根本内生性威胁是, 媒体对某银行金融科技活动的报道语调、注意力强度与属性刻画, 同该银行自身的经营决策与业绩互为因果: 业绩好的银行吸引更多正面报道, 而正面报道又可能改善融资条件与创新投入, 普通最小二乘无法把"舆论冲击对银行的因果效应"从这条反向回路中剥离出来。Bartik 型工具变量的应对思路是把银行 i 在年份 t 受到的舆论暴露分解为两个乘积因子: 一是在处理发生之前的基期 T0 一次性量好、之后永久冻结的银行对各同业组别的暴露份额 (share), 二是组别层面逐年变动、但在构造时刻意剔除银行 i 自身贡献的留一 (leave-one-out, 下称 LOO) 平均冲击 (shift)。两者按组求和即得工具: 该工具与银行 i 当年自身的报道实现值在机械构造上无关, 却通过基期暴露结构预测其所受的组别舆论冲击, 从而为二阶段最小二乘提供一阶段变异。该方法得名于 Bartik 在 1991 年区域经济学著作中提出的就业构成工具, 现代计量基础由 Goldsmith-Pinkham, Sorkin & Swift (2020) 的份额外生性路径与 Borusyak, Hull & Jaravel (2022) 的冲击外生性路径分别奠定; 本家族的识别主张明确走前者 (详见下方识别策略定位)。家族共 41 列, 覆盖十个前缀族 (type, scale, fintech_lf, fintech_lc, media, mauth, geoprox, attention, subst, collab)、三条文本轨 (_full, _ctx, _ss)、三个基期敏感性变体 (_t0, _t1, _t01)、一个契约别名列 (bartik_attention_iv) 与一个基期份额诊断列 (bartik_type_share_private)。从论文组合视角看, 家族承担了主线与衍生论文识别声明的半壁江山: 注意力、实质性、协同、语调与战略差异化五篇论文的主工具或后备工具均取自本家族, 其余前缀族则构成这些声明背后按维度展开的稳健性纵深 — 每个维度回答同一个问题的一个侧面: 银行接收舆论冲击的暴露结构, 究竟由同业类型、体量分层、创新定位、媒体类型、媒体权威还是地理归属刻画。

【方法学与计算】
家族由三台引擎生产, 全部在面板导出 runner 内以 merge-based 方式落列 (显式按 target_bank 与 year 键对齐, 不依赖任何行序假设)。第一台是 iv_did 模块的通用引擎 compute_bartik_iv (runner 步骤 7e), 生产 type 与 scale 两族: share 侧读取文章级 co_mentioned_banks 共现字段, 统计银行 i 在基期文章中与各组别银行的共现次数占比 (组别标签来自 bank_addresses.json 的监管类型六分与企业规模四分映射, 兜底类别 other 从分子与分母同时排除, 保证保留组份额之和为一, 各前缀族之间归一化口径可比); shift 侧对每条轨取组别乘年份单元内 LLM 三家投票情感分 llm_vote_score 的合计与计数, 再减去银行 i 自身在该单元的贡献后求均值, 组内剔除自身后无剩余观测时该单元 shift 置缺失。第二台是同模块的文章属性引擎 compute_bartik_iv_fintech, 生产 fintech_lf, fintech_lc, media, mauth, geoprox 五族: share 不再经共现银行, 而是直接按银行自身基期文章在某个文章级分类列上的类别占比冻结 (创新定位分类、媒体三方类型、媒体权威性档位、媒体省份与银行注册地是否同省), shift 仍为类别乘年份的 LOO 情感均值。第三台是 iv_extensions 模块的广义引擎 compute_bartik_shift_iv (runner 步骤 8z), 生产 attention, subst, collab 三族: share 直接复用步骤 7e 已落面板的 bartik_type_share_ 系列基期共现份额列 (不重复估计, 缺失语义原样继承), shift 则从情感分推广为任意文章级测度 — 注意力族用金融科技强度嵌入分, 实质性族用 LLM 实质性对象征性分类经取值映射转成的零一指示, 协同族用外部协同对自主研发分类的零一指示。基期解析统一为 T0 等于面板最早年份与 2010 中的较晚者 (config 键 bartik_base_year 可显式覆盖), 且强制要求 T0 严格早于 2019 政策冲击里程碑 (数字人民币与监管沙盒试点前夜), 违反即抛错终止而非静默降级。缺失语义经专项修复统一为三条铁则: 基期无文章或基期文章全部落入兜底类别的银行, share 与 IV 保持缺失, 绝不以零填充制造伪零暴露 (零填充曾造成十二至五十个标准差量级的离群伪零直接污染一阶段); share 为正但该组该年 shift 不可计算时, 缺失向工具传播; 面板年份早于基期末年的行, 因份额测自其未来, 工具整行置缺失 (share 前视掩码, share 列本身保留仅供诊断)。数值层面另有一处承重修复: LOO 减除前强制升为双精度浮点, 因为整型窄类型在组内合计与逐行减法链上会静默回绕并翻转 shift 符号。

【工程实现与数据契约】
三台引擎在实现层共享一套数据契约, 该契约的每一条都直接决定使用者能否正确解读列值。第一, 行宇宙与留篇门控: 文章级输入 df_exploded 的行宇宙由 full-only 留篇门控决定 — 自二零二六年六月二十九日起, 一篇文章是否被判为银行金融科技报道只看全文轨的大模型确认旗标, ctx 与 ss 轨降为 conditional-on-full 的测度轨, 其列在 full 留篇集的子集上取值; 因此本家族三条轨的工具共享同一篇章分母, 轨间差异纯粹来自测量窗口而非样本构成, 这是三轨可以互为稳健性对照的前提。第二, 双维命名契约: 列名尾缀 _full, _ctx, _ss 一律标注 shift 源测度的文本轨; share 侧的判据信息编码在前缀里 (fintech_lf 对 fintech_lc 的定位分类判据轨、geoprox 的省份判据、mauth 的评分档位), 两个维度独立正交, 任何按尾缀推断份额判据的读法都是错读。第三, 份额归一化跨族可比契约: 全部前缀族统一执行兜底类别双侧排除后归一, 保证保留份额行和为一 — 该口径经专项修复统一 (media 族修复前行和仅约七成), 使跨工具二阶段系数的量级可比。第四, 变量标签契约: 导出层为每列登记英文变量标签, 注明前缀族、份额判据与 shift 轨, 契约别名列与本体列双名登记; Stata 模板按 paper_spec 的 identification.iv 声明名引用, 改名须同步三处 (引擎输出、标签表、模板占位符), 否则模板实例化断链。第五, 日志自证契约: 每次构造在日志中落基期文章数与全量占比、各组份额分布、逐轨有效行数与均值标准差, 以及方法论引用清单, 使任何一次面板生产都能从日志复核工具的构造根据; 这些日志量全部算后即弃, 不参与数值计算, 属 golden-safe 口径。

【文献定位】
方法学谱系上, Goldsmith-Pinkham, Sorkin & Swift (2020) 证明 Bartik 工具在数值上等价于以基期份额为工具的广义矩估计, 并给出 Rotemberg 权重分解以定位哪些份额维度主导识别; 本家族在日志层内置了该诊断的近似实现, 并注明正式论文须以 Stata 的 bartik_weight 官方包复算。Borusyak, Hull & Jaravel (2022) 给出冲击外生性框架下的等价估计与推断; Adão, Kolesár & Morales (2019) 证明 shift-share 设计中残差在份额结构相近的观测间相关, 常规聚类标准误严重低估, 须用其提出的份额感知推断; Borusyak, Hull & Jaravel (2025) 的实践指南则把两条识别路径的核对清单 (不完整份额处理、重归一化选择、基期前定性论证) 系统化, 本家族的实现逐条对表。推断补强侧, Lee, McCrary, Moreira & Porter (2022) 的有效 t 比值临界值、Stock & Yogo (2005) 与 Andrews, Stock & Sun (2019) 的弱工具诊断谱系、Wang & Zhang (2024) 的少簇 wild bootstrap 共同构成模板层的弱工具与少簇防线; 工具族数量达到阈值后主表强制使用 Romano & Wolf (2005) 的逐步降压多重检验校正。构念源头侧, shift 源测度分别锚定 Hassan, Hollander, van Lent & Tahoun (2019) 的公司层文本暴露范式 (注意力族)、媒体经济学关于媒体类型与倾向的证据 (Qin, Strömberg & Wu 2018 提供中国媒体分层的制度事实, 支撑 media 与 mauth 族的份额维度)、以及 Engelberg & Parsons (2011) 用地理媒体覆盖差异分离媒体因果效应的设计 (geoprox 族的直接先例)。Fang, Wang, Wang & Yuan (2024, International Review of Economics & Finance) 用中国银行层面媒体情感指数识别其对系统性风险的因果传导, 为本家族 media/mauth 前缀族的份额判据 (媒体类型与权威性刻画银行舆论暴露异质性) 提供了同类制度背景下的中国银行媒体情感测量先例。Xu, He & Tang (2025, Applied Economics) 利用中国银行业竞争度构造的准工具变量识别策略, 考察银行业竞争对劳动收入份额的因果影响, 与本家族 Bartik/shift-share 工具变量在中国银行业场景下的应用高度相关。Bao & Goetz (2026, Journal of Corporate Finance) 采用留一法 (leave-one-out) 同伴均值构造工具变量识别本地同伴效应对企业投资的因果影响, 方法论上与本家族 LOO/Bartik 工具变量构造直接呼应。同业效应识别的一般理论中, Manski (1993) 的反射问题与 Bramoullé, Djebbari & Fortin (2009) 的网络识别条件解释了为何裸的组均值不能当工具、必须叠加基期冻结份额与 LOO 剔除; Gabaix & Koijen (2024) 的颗粒工具变量与 Luo 等 (2025) 的同伴效应工具化框架是本家族 LOO shift 构造的近缘方法; Breuer (2022) 面向财务与会计实证场景给出的 Bartik 应用入门, 逐项讨论了份额来源选择、基期锚定与工具报告规范, 为本家族在中文银行金融科技新闻场景的移植提供了最贴近的操作对照与陷阱清单。

【识别策略定位】
本家族的识别主张单边押注份额外生性路径: 银行在基期与哪些类型的同业共现、其基期报道落在哪些属性类别, 被论证为先于样本期内政策冲击与结果实现的前定暴露结构。三重护栏在代码层强制执行这一主张。其一, 基期外生性红线: T0 若不早于 2019 里程碑直接抛错, 基期敏感性变体的基期若触线则整列置缺失并告警, 不允许份额测自后处理期。其二, share 前视掩码: 早于基期末年的面板行工具置缺失, 承认份额外生性论证对这些行结构性失效。其三, v6 修剪: 早期版本曾生产二十九个维度族, 经逐维审查后二十八类因份额取自文章特征、编辑事后决策或时间切分等后定属性而被整族删除, 仅保留六类核心维度 (银行类型、银行规模、金融科技定位、媒体三方类型、媒体权威性、地理邻近), 另加步骤 8z 复用 type 份额的三个测度族; 保留族数仍多于单一工具, 故论文主表配 Romano-Wolf 校正压制多工具挑选空间。必须复述的口径铁律: shift 是同组其他银行的内生 LOO 情感或属性均值, 不是准随机外生冲击, 因此 Borusyak-Hull-Jaravel 意义上的冲击外生性路径对本家族不可用, 一切识别重量压在 GPSS 份额路径上, 论文须以基期前定性与 Rotemberg 权重集中度论证支撑; Hahn, Kuersteiner, Santos & Willigrod (2024) 进一步表明 shift-share 设计中的过度识别检验在共同冲击下失效, 这为下述禁混铁律提供计量支撑。份额外生性路径的可检验含义是有限的: 它不允许直接检验排他性, 只允许检验基期份额与银行基期可观测特征的条件独立 (平衡性检验) 与处理前平行趋势, 因此本家族把识别辩护的重量放在两处程序化产物上 — 基期份额分量的落盘 (供平衡性回归) 与 Rotemberg 权重的日志级近似分解 (供识别集中度诊断)。按 Goldsmith-Pinkham, Sorkin & Swift (2020) 的框架, 若某一份额维度承载了绝大部分正的 Rotemberg 权重, 则识别实际由该单一维度驱动, 论文须针对该维度而非全份额向量论证前定性; 若出现显著为负的 Rotemberg 权重, 则不同维度的隐含二阶段估计相互抵消, 提示识别脆弱, 须按 Borusyak, Hull & Jaravel (2025) 实践指南的核对清单逐项复核不完整份额处理与重归一化选择。本家族保留的六类核心维度并非任意挑选: 每一类的份额判据 (监管类型、企业规模、注册地省份、媒体三档、媒体三方类型、创新定位) 均须满足"编纂期或样本期前既定、不随当年报道实现变动"的形式门槛, v6 修剪删去的二十八类恰因份额取自文章事后特征或编辑决策而不满足该门槛, 这条筛选标准本身就是份额外生性路径在维度选择层的具体化。

【与相邻测度的构念区分】
同为面板 IV 列族, 本家族与三类近邻测度须严格区分。第一, leave_one_out_peer_ 与 lpeer_ 前缀的同组 LOO 均值工具 (iv_extensions 第一引擎) 是纯组均值工具, 不含基期份额加权, 其识别直觉是同组舆论溢出; 本家族则把基期暴露结构作为识别核心, 二者是并排的两台引擎, 可作跨族工具组合。第二, outlet_ 前缀的媒体来源构成工具 (iv_extensions 第三引擎) 以基期媒体来源构成乘来源风格暴露, 份额维度是媒体来源而非同业组别或文章类别。第三, zone_leave1out_ 系列经济圈 LOO 工具按地理经济圈分组, 与 geoprox 族的省份同城二分是不同的地理粒度。族内区分同样承重: 列名尾缀 _full, _ctx, _ss 标注的是 shift 源测度的文本轨 (全文、实体窗口、银行与金科同句窗口), 而 fintech_lf 与 fintech_lc 前缀中的 lf 与 lc 标注的是 share 分类判据取自哪条轨的创新定位列 — 份额判据维度与 shift 轨维度相互独立, 阅读列名时不可混淆。三轨口径遵循全仓铁律: full 轨为留篇门控 (二零二六年六月二十九日起门控只看 llm_verified_full) 的主轨, ctx 与 ss 为 conditional-on-full 的测度稳健性轨, 行宇宙是 full 留篇集的子集; ss 轨回退语义镜像 ctx, 文章无银行与金科同句共现时 ss 文本回退为全文并打回退旗标, 共享同一留篇分母。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把同一前缀族的三轨工具拼进同一个 over-identified Hansen J — 同篇文章三个文本窗口承载共同冲击与共同测量误差, 过度识别检验对这类同源工具零功效; 过度识别检验若要做, 只能用跨引擎工具组合 (LOO 乘 Bartik, 或 LOO 乘经济圈 LOO)。同理, _t0, _t1, _t01 基期梯子与十个前缀族之间也各自 just-identified 并排, 禁混同一 Hansen J。第四类近邻区分在方法学谱系而非同仓列族: 本家族的 LOO shift 与 Gabaix & Koijen (2024) 的颗粒工具变量共享"以其他单元的实现值构造工具"的直觉, 但颗粒工具变量按规模加权聚合特质冲击、其外生性来自冲击的特质性, 本家族则以基期份额加权组均值、其外生性来自份额的前定性, 两者是不同的识别哲学, 不可混用其推断公式。同样, Luo 等 (2025) 与 Bramoullé, Djebbari & Fortin (2009) 讨论的同伴效应工具化针对的是"内生效应对外生效应"的分离 (Manski 1993 反射问题), 本家族不主张分离内生与外生同伴效应, 只把组别舆论冲击当作对本行处理变量的外生推手, 因此不受反射问题的完全识别条件约束 — 这一构念边界须在论文方法节写清, 以免审稿人以同伴效应识别的标准误用于本家族。跨引擎组合的合法性也据此界定: 只有当两台引擎的识别变异来源在构造上确不同源 (基期暴露结构对当期组均值、对媒体来源风格暴露) 时, 其工具方可并入同一过度识别检验, 同源变异 (同前缀族三轨、同维度基期梯子) 的 J 检验零功效, 这与 Hahn, Kuersteiner, Santos & Willigrod (2024) 对共同冲击下 overid 失效的论证一致。

【已知局限与稳健性梯子】
第一, shift 内生性残留: LOO 剔除消除了自身贡献, 但同组其他银行的情感均值仍可能与组内共同需求冲击相关, 排他性约束不可检验, 论文叙事须以份额路径论证而非双重主张; Apfel (2024) 一类放松排他性约束的部分识别方法是可选的敏感性报告。第二, 基期选择敏感性: type 族显式物化 _t0 (基期 T0)、_t1 (基期 T0 加一年)、_t01 (双年池化) 三臂梯子, 三臂与主列互为稳健性不分主次, 各自 just-identified 并排, 用以证明主结论不被基期落点驱动; _t1 与 _t01 均带基期外生性守卫, 触线即整列缺失。第三, 份额支撑退化: 开发面板仅两个年份时, 基期共现份额大面积退化为单点独热, 组间区分度几乎耗尽, 滞后类衍生量亦仅末年有值, 任何在开发面板上算得的一阶段统计量只承担管道正确性冒烟职能, 相关诊断结论禁止从开发面板外推, 生产十八年全量面板下方可正式评估工具强度与份额集中度。第四, 弱工具与少簇: 模板层配 Kleibergen-Paap 秩 F、Anderson-Rubin 置信区间、有效 t 比值临界值与 wild bootstrap; 中介分解如需在 IV 框架内进行, 走 Dippel, Ferrara & Heblich (2020) 的工具化中介路径。第五, 缺失即诚实: 本家族一切缺失都携带明确语义 (基期无文章、组内无他行、前视掩码、轨源列缺失), 使用者不得以零或均值插补, 插补等价于把工具缺失伪装成零暴露, 恰是专项修复所清除的缺陷。第六, 推断的份额结构依赖: shift-share 设计下回归残差在基期份额结构相近的银行之间相关, 常规按银行聚类的标准误可能显著低估, Adão, Kolesár & Morales (2019) 的份额感知推断或以份额结构定义聚类单元是必要的敏感性报告; 少簇年份维度的推断以 wild bootstrap 补强。第七, 多论文共享工具的解读纪律: 同一工具列可被多篇论文的识别声明收录 (bartik_type_iv_full 同时服务语调与战略差异化两篇), 这在数据层是复用而非依赖 — 每篇论文的二阶段各自独立设定, 工具的有效性论证须在各论文的处理变量构念下分别成立, 不存在一次论证全局通行的捷径; 尤其排他性约束是处理变量特定的: 同组情感浪潮对甲论文结果变量无直接通道, 不自动推出对乙论文亦然。第八, 与结果变量的时序纪律: 部分论文的结果变量为多年前瞻变化量, 工具与处理变量同年、结果跨年, 使用者在动态设定 (加入处理变量滞后项) 中引入本家族工具的滞后时, 须自行保证滞后后的前视掩码语义不被破坏 — 掩码按当年基期关系施加, 手工 shift 列位移不会自动重算掩码。综上, 本家族的一切设计选择服从同一原则: 识别假设写进代码而非只写进论文 — 红线抛错、掩码置缺、缺失传播、程序化三轨清单, 都是把 GPSS 份额路径的论证义务转译为机器可执行守卫的产物; 使用者的义务是不在下游以插补、改名或跨轨拼接破坏这些守卫所保护的语义。第九, 推断层的方法配套须与识别层匹配: 弱工具诊断不采用一阶段 F 大于十的经验法则, 而以 Stock & Yogo (2005) 的临界值表与 Lee, McCrary, Moreira & Porter (2022) 的有效 t 比值临界值为准, 二者在 just-identified 单工具场景下给出比常规 t 检验更保守的拒绝域; 当一阶段疑弱时, 主结论以 Anderson-Rubin 型弱工具稳健置信区间报告, 其对工具强度不敏感, 这一谱系由 Andrews, Stock & Sun (2019) 系统梳理。第十, 部分识别作为排他性放松的补充报告: 当审稿质疑 shift 的 LOO 均值仍可能经组内共同需求冲击违反排他性时, Apfel (2024) 一类放松排他性约束的部分识别方法给出的是识别区间而非点估计, 本家族不默认生产该区间, 但其份额向量与工具列的落盘足以支撑论文在稳健性附录中外接该方法。第十一, 生产规模下的诚实边界: 开发面板两年期的一切一阶段统计量仅承担管道冒烟职能, 家族的工具强度、份额集中度、Rotemberg 权重符号等一切实质诊断结论均须在生产十八年全量面板上重估, 任何把开发面板数值写入论文的行为都属越界, 这条边界与全仓 golden 口径 (开发面板不可外推、数值随生产语料重生) 一致。

## VAR: bartik_attention_iv

【变体差分】
本列为注意力 Bartik 工具的契约别名列, tier 为 core: 在步骤 8z 末尾由 bartik_attention_iv_full 逐位复制而来, 数值与 full 轨列完全相同, 不是第四条独立文本轨。设置该无后缀别名的原因是命名契约: paper_spec 的 identification.iv 字段与根级 Stata 二阶段最小二乘模板按主名无轨后缀的约定引用工具列 (与 llm_peer_iv 族的主名约定一致), 注意力论文 (bank_fintech_attention, 即组合内 P2) 的识别声明以本列名收录为主工具, 复制列保证模板实例化时不因轨后缀改名而断链。经济含义上, 本列工具化的内生处理变量是银行年度注意力指数 attention_index_full — Hassan, Hollander, van Lent & Tahoun (2019) 公司层文本暴露测量范式在中文银行新闻语料上的移植, 其内生性来源是报道注意力与银行金融科技投入决策的双向反馈。构造上, share 侧复用步骤 7e 在 type 维度冻结的基期共现份额 (银行 i 基期文章中与国有大型、股份制、城商、农商、民营、外资六类同业的共现占比, 兜底类别排除后归一), shift 侧取组别乘年份单元内除银行 i 外其余银行文章级金融科技强度分 fintech_intensity_score_full 的年度均值 — 注意 shift 源是嵌入强度测度而非情感分, 这是广义引擎相对步骤 7e 情感 shift 的关键推广: 工具承载的是"同组他行被报道的金融科技强度冲击", 与注意力处理变量的构念通道对齐。缺失语义完整继承: 基期无共现文章的银行整列缺失, 组内仅剩自身的组年单元 shift 缺失并向工具传播, 早于基期末年的面板行前视掩码置缺失。使用口径: 本列与 _ctx, _ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 由于本列与 _full 列数值恒等, 二者绝不可同时入同一回归 (完全共线), 模板按契约名取其一。弱工具诊断与少簇推断按家族通用防线执行, 主表伴随 Romano-Wolf 校正。识别声明的完整语境: 注意力论文的识别工具箱是双引擎并排 — 本列 (Bartik 引擎, 基期共现份额乘同组他行强度冲击) 与 leave_one_out_peer_attention_iv 及其滞后 (LOO 引擎, 同类型年份组内他行注意力指数均值) 各自 just-identified 进各自的二阶段规格, 主规格与后备规格的取舍由论文方法节声明; 若审稿要求过度识别检验, 唯一合法组合是跨引擎的 Bartik 乘 LOO 双工具, 因二者的识别变异来源不同 (基期暴露结构对当期组均值), 同源三轨拼接则被铁律禁止。份额复用的方法学含义值得单独强调: 本列不自建份额而复用 type 维度的基期共现份额, 意味着注意力工具与语调工具 (bartik_type_iv_full) 共享同一份额向量、仅 shift 源不同 — 份额层面的 Rotemberg 权重诊断与平衡性检验做一次即覆盖两族, 这是刻意的设计经济性; 但也因此两族工具在同一论文中不可同时入回归, 其相关性由共享份额机械保证。开发面板注意事项: 两年期下基期共现份额大面积独热退化、组间区分度耗尽, 本列的一阶段 F 统计量在开发面板上仅作管道正确性冒烟、不具任何外推力, 正式的工具强度评估与弱工具结论一律以生产十八年面板的实测为准。shift 源为嵌入强度分而非情感分这一推广, 使本列的排他性论证有其特殊纹理: 同组他行被报道的金融科技强度浪潮, 影响本行注意力指数的合法通道应是竞争性关注的传染, 若该浪潮同时经行业景气度直接改变本行的结果变量 (如金融科技投资规模), 则排他性受威胁; 论文须以结果变量的多年前瞻设定与同期景气度控制封堵旁路, 该论证在 Hassan, Hollander, van Lent & Tahoun (2019) 文本暴露范式的移植中属标准动作。弱工具诊断上, 本列虽为 just-identified 单工具, 仍须报告 Kleibergen-Paap 秩 F 对照 Stock & Yogo (2005) 与 Lee, McCrary, Moreira & Porter (2022) 的临界值, 疑弱时以 Anderson-Rubin 置信区间替代常规 t 检验; 少簇年份维度配 Wang & Zhang (2024) 的 wild bootstrap。作为契约别名列, 本列在导出层与 _full 本体列双名登记, 改任一名须同步引擎输出、变量标签表与模板占位符三处, 否则注意力论文的模板实例化断链; 使用者若在下游脚本按主名与带后缀名分别取列做对照, 须记住二者数值恒等、不可解读为两个独立的稳健性臂。

## VAR: bartik_attention_iv_ctx

【变体差分】
注意力 Bartik 工具的 ctx 实体窗口轨。与家族 canonical (full 轨) 的唯一差分在 shift 源测度的文本轨: 本列的组年 LOO 均值取自文章级 fintech_intensity_score_ctx, 即在标题加实体上下文窗口文本上计算的金融科技强度嵌入分, 而非全文轨的同名分值。ctx 轨文本在 stage 14 物化, 只保留目标银行实体邻近窗口内的语句, 因而强度信号更聚焦于与该银行直接关联的金融科技叙述, 剔除了同篇文章中与目标银行无关的行业泛谈; 相应代价是文本更短、强度估计的抽样噪声更大。share 侧与 canonical 完全相同 (复用 type 维度基期共现份额), 基期解析、前视掩码、缺失传播语义逐条一致, 故本列与 full 轨的数值差异完全由 shift 源的窗口归因差异驱动, 构成对"工具强度信号取自哪个文本粒度"这一测量选择的稳健性检验。口径铁律: ctx 轨是 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集子集; 本列与 full, ss 轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨拼进同一 over-identified Hansen J — 三窗共享同篇文章的共同冲击, 过度识别检验零功效。论文用法为镜像重估: 主表用契约名列, 附表以本列整体替换工具后重跑二阶段最小二乘, 报告系数符号与量级稳定性。

## VAR: bartik_attention_iv_full

【变体差分】
注意力 Bartik 工具的 full 全文轨实名列, 也是该前缀族的 canonical 本体: 契约别名列 bartik_attention_iv 即由本列逐位复制, 两列数值恒等。shift 源为文章级 fintech_intensity_score_full — 在标题前置加全文正文的完整文本上计算的金融科技强度嵌入分, 组别乘年份单元内剔除目标银行自身贡献后取均值。full 轨是全仓留篇门控主轨 (门控只看 llm_verified_full), 文本覆盖最全、单篇强度估计噪声最小, 因而是该工具族一阶段强度的基准臂。share 侧复用 type 维度基期共现份额, 六组归一、兜底排除、基期无文章缺失、前视掩码等语义与家族通用口径逐条一致。本列在面板上与别名列并存的技术原因是导出层双列契约: 变量标签表同时登记两名 (标签均为全文轨注意力 Bartik 工具), 模板走无后缀名, 族内三轨对照走带后缀名, 避免同一列在两种引用场景下语义含混。使用口径: 与 _ctx, _ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与别名列完全共线, 二者取一入回归。诊断上, 本列是 Rotemberg 权重分解与弱工具 F 统计量的默认评估对象, 基期份额集中度的解读以本列为准, 其余轨引用同一份额结构故份额诊断结论跨轨共享。

## VAR: bartik_attention_iv_ss

【变体差分】
注意力 Bartik 工具的 ss 同句共现轨。与 canonical 的差分仍仅在 shift 源文本轨: 组年 LOO 均值取自 fintech_intensity_score_ss, 即在"目标银行与金融科技词出现于同一句 (正负一句窗口)"的最严格判据文本上计算的强度分。ss 轨的构念主张是把强度信号收紧到银行与金融科技被同句直接关联的语句, 归因纯度最高, 是三轨中对"报道确实在谈该银行的金融科技"最保守的测量。回退语义须按全仓铁律复述: 文章不存在银行与金科同句共现时, ss 文本回退为全文正文且 ss_is_fallback 置真, 与 ctx 轨镜像, 共享同一留篇分母 — 因此本列的 shift 源在无同句共现的文章上实际承载全文信号, ss 轨与 full 轨的差异强度取决于语料中同句共现的普及率。stage 21 未产 ss 列时, 引擎的轨源守卫将本列优雅置缺失而非报错。share 侧、基期、前视掩码与缺失传播与家族口径一致。使用铁律: ss 轨为 conditional-on-full 稳健性轨, 与 full, ctx 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 开发面板上 ss 轨源列覆盖稀疏时本列可整列缺失, 属预期退化而非缺陷, 生产语料下方可正式评估其对注意力工具族一阶段强度的边际贡献。

## VAR: bartik_collab_iv_ctx

【变体差分】
协同模式 Bartik 工具的 ctx 轨。该前缀族服务于开放式创新论文 (bank_fintech_collab, 组合内 P5), 内生处理变量为银行金融科技活动中外部协同占比。与 canonical (full 轨) 的差分在 shift 源: 本列取文章级 LLM 分类列 innovation_collab_mode_ctx — 实体窗口轨上三家大模型投票判定的"外部协同对自主研发"分类 — 经取值映射 (外部协同记一、自主研发记零, 映射外取值记缺失且不进分子分母) 转为零一指示后, 在 type 组别乘年份单元内做 LOO 均值。shift 的经济含义是"同组其他银行当年被报道的外部协同倾向", ctx 轨将该判定收紧到目标银行实体邻近窗口, 剔除同篇文章对其他机构协同行为的叙述串扰。share 侧复用 type 维度基期共现份额, 与族内其余轨完全相同, 数值差异全部来自分类判定的窗口归因差异。取值映射的缺失语义值得强调: 分类列取值不在映射表内 (如未分类或低置信) 的文章不参与 shift 分子分母, 与情感 shift 引擎"数值列直接用"的口径不同, 保证指示均值的分母只含有效判定。口径铁律: ctx 为 conditional-on-full 稳健性轨, 与 full, ss 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与 lpeer_collab_iv_ctx (纯组均值 LOO 工具) 是不同引擎的并排工具, 跨引擎组合方可用于过度识别检验。

## VAR: bartik_collab_iv_full

【变体差分】
协同模式 Bartik 工具的 full 轨, tier 为 core: 开放式创新论文 (bank_fintech_collab, 组合内 P5) 在 paper_spec 的 identification.iv 声明中收录本列为识别策略主工具, 二阶段最小二乘模板按本列名实例化。被工具化的内生处理变量是银行年度外部协同占比 collab_frac 族测度 — Chesbrough 开放式创新框架下"银行金融科技推进依赖外部合作还是自主研发"的媒体测量。构造全链: share 侧复用步骤 7e 冻结的 type 维度基期共现份额 (银行 i 基期文章与六类监管类型同业的共现占比, 兜底类别双侧排除后份额和为一, 基期无共现文章者整列缺失); shift 侧取文章级 innovation_collab_mode_full — 全文轨三家大模型投票的协同模式分类 — 经外部协同记一、自主研发记零的取值映射转为指示后, 在组别乘年份单元内剔除银行 i 自身贡献求均值, 组内仅剩自身时缺失并向工具传播; 早于基期末年的面板行前视掩码置缺失。工具的识别直觉: 银行 i 基期的同业暴露结构决定其接收"同组他行协同浪潮"的强度, 而该浪潮由其他银行的报道实现驱动, 与银行 i 自身当年的协同决策在构造上无关; 识别重量押在 GPSS 份额外生性路径, shift 为内生 LOO 分类均值, 冲击外生性路径不可用, 论文须报告基期前定性论证与 Rotemberg 权重集中度。分类 shift 相对情感 shift 的额外考量: 指示均值的方差随组年有效判定篇数收缩, 小组别年份的 shift 抽样噪声更大, 弱工具诊断 (Kleibergen-Paap 秩 F 对照有效 t 比值临界值) 在本列上尤其不可省略; 少簇场景配 wild bootstrap 推断。使用铁律: 与 _ctx, _ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 三轨同源于同篇文章的分类判定, 共同测量误差使过度识别检验零功效, 如需 overid 须与 LOO 引擎工具跨族组合 (leave_one_out_peer_collab_iv 及其滞后是指定搭档, 其识别变异来自当期组均值而非基期暴露结构)。full 轨为留篇门控主轨, 行宇宙即 full 留篇集, 分类判定的置信过滤在 encode 层完成 — 分类共识并非文章存档层的裸多数票, 而是经确认旗标门控与清票规则后的口径, 使用者不得绕过面板列自行从文章级分类重新聚合。主表伴随 Romano-Wolf 多重检验校正, 因保留工具族数多于单一工具。构念区分注意: 本列与实质性族 (bartik_subst_iv_full) 结构完全平行 — 同一份额向量、同为零一分类 shift — 但两个分类维度在构念上正交 (协同问的是创新组织方式、实质性问的是创新真实程度), 论文层各服务一篇、互不替代; 与注意力族的差分则在 shift 量纲 (指示占比对连续强度分)。份额复用契约与注意力族条目所述一致: 本列复用 type 份额, 份额层诊断跨族共享, 但与 type 情感工具不可同回归并入。开发面板两年期下, 组年单元的有效协同判定篇数稀少、指示均值方差大, 本列一阶段强度不具外推力, 弱工具结论以生产面板为准; 分类 shift 对大模型判定分布的依赖也意味着换模型属改测度类改动, 须走受控重生流程。协同维度的排他性论证有其构念特殊性: 同组他行的外部协同浪潮影响本行开放式创新决策的合法通道是竞争性模仿与生态位挤压 (Chesbrough 开放式创新框架下的同群压力), 若该浪潮同时经并购市场热度或政策补贴直接改变本行结果变量, 排他性即受威胁, 论文须以结果变量时序与政策窗口控制封堵旁路。指示均值 shift 相对连续情感 shift 的一个额外脆弱点在推断: 当组年有效判定篇数少时, 零一指示的 LOO 均值只能取有限个离散值, 其对二阶段的解释力受份额向量与该离散 shift 的交互支撑, Rotemberg 权重可能高度集中于少数组别年份, 论文报告权重集中度时须对协同族单独审视, 不能沿用情感 shift 族的诊断结论。与 lpeer_collab_iv 跨引擎组合是本列唯一合法的过度识别检验搭档, 因 LOO 引擎的识别变异来自当期组均值、与本列基期暴露结构变异确不同源。

## VAR: bartik_collab_iv_ss

【变体差分】
协同模式 Bartik 工具的 ss 同句轨。差分仅在 shift 源: 取 innovation_collab_mode_ss — 银行与金科同句窗口文本上的协同模式 LLM 分类 — 经外部协同记一、自主研发记零映射后做 type 组年 LOO 均值。ss 轨把协同判定收紧到银行与金融科技被同句直接关联的语句, 是"报道确实在谈该银行自身协同行为"的最保守归因判据, 纯度最高而文本支撑最薄。回退语义按全仓铁律: 无同句共现的文章 ss 文本回退为全文且回退旗标置真 (镜像 ctx), 共享 full 留篇分母, 故本列 shift 在回退文章上实际承载全文判定信号; stage 21 未产 ss 分类列时轨源守卫将本列优雅置缺失。share 侧复用 type 基期份额, 基期、前视掩码、映射外取值不进分子分母等语义与族内其余轨逐条一致。使用口径: ss 为 conditional-on-full 稳健性轨, 与 full, ctx 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。开发面板上同句判定覆盖稀疏导致本列大面积缺失属预期退化而非缺陷; 生产语料下, 本列与 full 轨系数的稳定对照是"协同测量不被窗口选择驱动"稳健性叙事的关键一环, 与 lpeer_collab_iv_ss 跨引擎组合方可支撑合法的过度识别检验。

## VAR: bartik_fintech_lc_iv_ctx

【变体差分】
金融科技定位 Bartik 工具, 份额判据取 ctx 轨 (lc), shift 取 ctx 情感轨。本族由文章属性引擎生产, 与 type 族的根本差分在 share 来源: 不经共现银行, 而是按银行 i 基期文章在 innovation_locus_ctx 分类列 (实体窗口轨 LLM 判定的"底层技术对应用场景"创新定位) 上的类别占比冻结份额, 类别仅两维 (tech 与 app), 未映射与兜底取值从分子分母双侧排除后归一, 基期文章全部未映射的银行份额保持缺失。shift 侧为类别乘年份单元内其他银行 llm_vote_score_ctx (实体窗口轨三家投票情感分) 的 LOO 年度均值。列名双维须严格区读: 前缀中的 lc 标注份额分类判据取自 ctx 轨定位列, 尾缀 _ctx 标注 shift 情感的文本轨 — 本列是两维皆 ctx 的对角组合, 份额判据与冲击测量在同一窗口粒度上对齐。识别直觉: 基期偏向底层技术叙事的银行, 后续更多暴露于技术类报道的情感冲击。份额判据由 LLM 分类决定, 属须配合论证的维度 (v6 审查明确要求论文对 LLM 分类份额的前定性单独辩护)。口径铁律: 本列与族内 full, ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; lc 与 lf 两个份额判据臂同样并排不交叉, 论文主规格取其一, 另一作稳健性。

## VAR: bartik_fintech_lc_iv_full

【变体差分】
金融科技定位 Bartik 工具, 份额判据 ctx 轨 (lc), shift 取 full 情感轨。share 侧与 lc 族其余轨完全相同: 银行 i 基期文章按 innovation_locus_ctx (实体窗口轨 LLM 创新定位分类, Hassan 式实体邻近归因框架) 的 tech 对 app 两类占比冻结, 未映射双侧排除, 基期全未映射者缺失。差分在 shift: 本列取类别乘年份单元内其他银行 llm_vote_score_full (全文轨情感分) 的 LOO 均值, 即份额判据用窗口归因、冲击测量用全文信号的交叉组合。这一组合的方法学价值在于拆解两个测量自由度: 与 bartik_fintech_lc_iv_ctx 对照隔离 shift 轨的影响 (份额同、冲击窗口异), 与 bartik_fintech_lf_iv_full 对照隔离份额判据轨的影响 (冲击同、份额判据异), 使"工具不被任一窗口选择驱动"的稳健性主张可以按维度归因。full 情感轨是留篇门控主轨, 组年单元有效篇数最多, shift 抽样噪声最小, 故本列通常是 lc 份额臂内一阶段强度最高的组合。缺失语义、基期解析 (T0 与 2019 红线)、前视掩码与家族口径逐条一致。使用铁律: 与族内 ctx, ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; lc 对 lf 两份额臂并排不交叉; 份额由 LLM 分类决定, 论文须单独论证其基期前定性, 并以 Rotemberg 权重报告两类别的识别贡献集中度。

## VAR: bartik_fintech_lc_iv_ss

【变体差分】
金融科技定位 Bartik 工具, 份额判据 ctx 轨 (lc), shift 取 ss 同句情感轨。share 侧同 lc 臂: 基期文章按实体窗口轨创新定位分类的 tech 对 app 占比冻结份额。shift 侧取类别乘年份单元内其他银行 llm_vote_score_ss — 银行与金科同句窗口文本上的三家投票情感分 — 的 LOO 年度均值。本列把冲击测量收紧到最严格的同句归因判据, 与 lc 份额的窗口归因判据形成"份额中等严格、冲击最严格"的阶梯组合。ss 轨回退语义按全仓铁律复述: 无银行金科同句共现的文章, ss 文本回退为全文且回退旗标置真 (镜像 ctx), 共享 full 留篇分母, 故回退文章上的情感判定实际承载全文信号; stage 21 未产 ss 情感列时, 引擎守卫将本列优雅置缺失而非报错。其余语义 (基期解析与红线、未映射双侧排除、组内仅剩自身缺失传播、前视掩码) 与家族口径逐条一致。使用口径: ss 为 conditional-on-full 稳健性轨, 与族内 full, ctx 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 同句情感在小类别年份单元内有效篇数最少, shift 抽样噪声在族内最大, 弱工具诊断在本列上不可省略, 开发面板上整列缺失属预期退化而非缺陷, 结论以生产面板为准。

## VAR: bartik_fintech_lf_iv_ctx

【变体差分】
金融科技定位 Bartik 工具, 份额判据取 full 轨 (lf), shift 取 ctx 情感轨。与 lc 臂的唯一差分在份额分类判据来源: 本臂按银行 i 基期文章在 innovation_locus_full (全文轨 LLM 创新定位分类) 上的 tech 对 app 占比冻结份额 — 全文判定覆盖每篇留篇文章, 分类支撑最厚, 但可能把同篇文章中与目标银行无关的技术叙事也计入其定位画像; lc 臂则以窗口归因换取归因纯度。两臂在 paper_spec 层的约定是主规格取其一、另一作稳健性, 属于并排不分主次的份额判据梯子, 各自 just-identified, 禁混同一 over-identified Hansen J。本列 shift 取类别乘年份单元内其他银行 llm_vote_score_ctx (实体窗口情感分) 的 LOO 均值, 与 bartik_fintech_lf_iv_full 对照可隔离冲击窗口的影响, 与 bartik_fintech_lc_iv_ctx 对照可隔离份额判据的影响。缺失语义与家族口径一致: 基期无文章或基期文章全部未映射的银行份额与工具保持缺失, 类别年份单元内剔除自身后无剩余判定时 shift 缺失传播, 早于基期末年的行前视掩码。份额由 LLM 分类决定, 论文须按 v6 审查要求单独论证该分类在基期的前定性, 并报告 Rotemberg 权重集中度; 类别仅两维时识别实际由单一有效份额维度驱动, 解读时须注意。

## VAR: bartik_fintech_lf_iv_full

【变体差分】
金融科技定位 Bartik 工具, 份额判据 full 轨 (lf), shift 取 full 情感轨, 即两维皆全文的对角组合, 是 lf 份额臂的基准列。share 侧: 银行 i 基期文章按 innovation_locus_full 分类的底层技术对应用场景两类占比冻结, 该分类由三家大模型投票产生并在 encode 层经置信门控, 未映射与兜底取值双侧排除后份额和为一; 基期文章全部未映射者份额保持缺失, 不以零填充制造伪零暴露。shift 侧: 类别乘年份单元内其他银行全文轨情感分的 LOO 均值, 全文情感为留篇门控主轨, 单元有效篇数最多, shift 估计最稳。识别直觉与 lc 臂相同: 基期定位画像决定银行接收技术类对应用类报道情感冲击的相对暴露; 与 type 族的差分在于份额维度是文章属性而非同业共现结构, 二者提供互补的暴露通道, 跨族组合可用于过度识别检验 (族内三轨则严禁)。历史口径注记: 该族源自 v3.2.0 双套独立设计, lf 臂对应全文框架、lc 臂对应实体邻近框架, 两臂列族完全平行。缺失语义、基期解析与红线、前视掩码逐条继承家族口径。使用铁律: 与族内 ctx, ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; lf 对 lc 份额臂并排取一为主; LLM 分类份额的前定性论证与弱工具诊断为论文必答项。

## VAR: bartik_fintech_lf_iv_ss

【变体差分】
金融科技定位 Bartik 工具, 份额判据 full 轨 (lf), shift 取 ss 同句情感轨。share 侧与 lf 臂其余轨相同: 基期文章按全文轨创新定位分类的 tech 对 app 占比冻结份额, 未映射双侧排除, 基期全未映射者缺失。shift 侧取类别乘年份单元内其他银行 llm_vote_score_ss 的 LOO 年度均值, 把冲击测量收紧到银行与金融科技同句共现的最严格归因窗口, 与 lf 份额的全文判据形成"份额最宽、冲击最窄"的极端交叉组合 — 该组合与 bartik_fintech_lc_iv_full (份额窗口归因、冲击全文) 恰成镜像, 两列对照可完整刻画两个测量自由度的交互影响。ss 轨回退语义按铁律复述: 无同句共现的文章 ss 文本回退为全文、回退旗标置真、镜像 ctx、共享 full 留篇分母; ss 情感列缺席时守卫优雅置缺失。基期解析 (T0 取面板最早年与 2010 较晚者、强制早于 2019 里程碑)、组内仅剩自身缺失传播、前视掩码与家族口径一致。使用口径: ss 为 conditional-on-full 稳健性轨, 与族内 full, ctx 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 同句单元有效篇数最少使本列一阶段强度先验最弱, 报告时以弱工具稳健的 Anderson-Rubin 置信区间替代常规 t 检验为宜, 开发面板整列缺失属预期退化。

## VAR: bartik_geoprox_iv_ctx

【变体差分】
地理邻近 Bartik 工具的 ctx 情感轨。该族的份额维度是报道的地理归属二分: 以 bank_addresses.json 的银行注册地省份对照文章的媒体省份字段, 同省记 local、异省记 nonlocal, 银行 i 基期文章在两类上的占比即冻结份额。识别直觉承接 Engelberg & Parsons (2011) 的经典设计 — 本地媒体与异地媒体对同一事件的覆盖差异提供与银行自身决策无关的暴露变异; 银行注册地在样本期前既定, 媒体省份是文章属性, 两者交叉的二分类别满足份额基期前定的论证要求, 故该维度在 v6 修剪中被保留。shift 侧为类别乘年份单元内其他银行 llm_vote_score_ctx (实体窗口轨情感分) 的 LOO 年度均值, 即"同为本地报道或同为异地报道的其他银行当年情感冲击"。与 canonical (full 情感轨) 的唯一差分在 shift 情感的文本轨: 实体窗口归因剔除同篇文章与目标银行无关段落的情感串扰, 换取更大的抽样噪声。缺失语义与家族口径一致: 基期无文章者缺失、单元内剔除自身无剩余时 shift 缺失传播、早于基期末年前视掩码; 媒体省份字段缺失的文章不参与分类。使用铁律: 与族内 full, ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 二分份额下识别由单一有效维度驱动, Rotemberg 权重解读须注意。

## VAR: bartik_geoprox_iv_full

【变体差分】
地理邻近 Bartik 工具的 full 情感轨, 该族 canonical 本体。share 侧: 银行注册地省份 (bank_addresses.json, 样本期前既定的机构属性) 与文章媒体省份同异判定的 local 对 nonlocal 二分, 按银行 i 基期文章占比冻结; 该份额维度的前定性论证在全家族中最直接 — 注册地不随报道实现变动, 媒体省份由媒体机构属地决定, 两者均不受银行当年决策影响, 这正是 v6 审查保留本族的理由, 学术先例为 Engelberg & Parsons (2011) 以地理覆盖差异分离媒体因果效应的设计。shift 侧: 类别乘年份单元内其他银行 llm_vote_score_full (全文轨三家投票情感分) 的 LOO 年度均值, 全文轨为留篇门控主轨, 单元篇数最多、估计最稳。工具语义: 基期以本地报道为主的银行, 持续暴露于本地媒体报道情感的年度波动; 基期以异地全国性报道为主的银行则暴露于异地媒体情感波动 — 两类媒体的情感生成机制差异 (属地宣传激励对市场化选题) 提供识别变异, Qin, Strömberg & Wu (2018) 刻画的中国媒体分层制度事实是该差异的经验支撑。缺失语义、基期解析与红线、前视掩码逐条继承家族口径; 媒体省份字段不存在时整族跳过。使用铁律: 与 _ctx, _ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与 zone_leave1out_ 经济圈工具是不同地理粒度的并排族, 跨族组合方可做过度识别检验。

## VAR: bartik_geoprox_iv_ss

【变体差分】
地理邻近 Bartik 工具的 ss 同句情感轨。share 侧与族内其余轨完全相同: 银行注册地省份对文章媒体省份的 local 对 nonlocal 二分, 基期占比冻结, 前定性论证同 full 轨条目。差分仅在 shift 情感的文本轨: 类别乘年份单元内其他银行 llm_vote_score_ss — 银行与金融科技同句窗口文本上的情感分 — 的 LOO 年度均值, 把"本地对异地报道情感冲击"的测量收紧到确实在同句谈论银行金融科技的语句。ss 轨回退语义按全仓铁律复述: 文章无银行金科同句共现时 ss 文本回退为全文、回退旗标置真、与 ctx 镜像、共享 full 留篇分母, 回退文章上的情感判定实际承载全文信号; stage 21 未产 ss 情感列时引擎守卫将本列优雅置缺失而非中断。基期解析 (T0 红线)、单元内剔除自身无剩余时缺失传播、前视掩码等语义逐条继承。方法学定位: 本列检验地理暴露工具是否被情感测量的窗口选择驱动 — 若 full 与 ss 轨给出同号同量级的二阶段系数, 则地理通道的识别叙事不依赖任一窗口判据。使用口径: ss 为 conditional-on-full 稳健性轨, 与族内 full, ctx 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 同句单元篇数最少, 弱工具诊断必报, 开发面板整列缺失属预期退化。

## VAR: bartik_mauth_iv_ctx

【变体差分】
媒体权威性 Bartik 工具的 ctx 情感轨。该族份额维度是媒体权威性三档: 以 media_weights.json 的媒体评分把文章来源划为 high (评分不低于八十)、mid (不低于六十)、low 三档, 未收录媒体按低分兜底落 low 档, 银行 i 基期文章在三档上的占比即冻结份额。档位阈值与媒体评分在样本期前给定, 权威媒体名录属机构层前定属性, 故 v6 审查保留该维度; 学术依据是会计与金融文献中媒体权威性影响信息传导强度的证据链, 中国场景下官方层级媒体与市场化媒体的报道激励差异 (Qin, Strömberg & Wu 2018) 为档位间情感生成差异提供制度基础。shift 侧为档位乘年份单元内其他银行 llm_vote_score_ctx (实体窗口轨情感分) 的 LOO 年度均值。与 canonical (full 情感轨) 的唯一差分在 shift 文本轨: 实体窗口归因收紧情感的银行指向性。识别直觉: 基期被高权威媒体密集覆盖的银行, 持续暴露于高权威媒体报道情感的年度波动, 该波动由同档位内其他银行的报道实现驱动, 与银行 i 自身当年表现在构造上无关。缺失语义、基期解析与红线、前视掩码继承家族口径。使用铁律: 与族内 full, ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与 media 三方分类族的份额维度高度相关, 二族并排不叠加, 禁在同一规格同时入工具。

## VAR: bartik_mauth_iv_full

【变体差分】
媒体权威性 Bartik 工具的 full 情感轨, 该族 canonical 本体。share 侧: media_weights.json 媒体评分驱动的 high, mid, low 三档 (阈值八十与六十, 未收录媒体兜底 low), 银行 i 基期文章的档位占比冻结为份额; 三档全保留、无排除类别, 份额和为一。评分与档位映射为编纂期前定的媒体机构属性, 不随单篇报道实现变动, 满足 GPSS 份额前定性论证的形式要求, 但论文仍须讨论"基期被何种权威档媒体覆盖"与银行不可观测质量的潜在相关 — 这是本族相对 geoprox 族 (注册地纯外生) 更弱的一环, 建议以基期特征平衡检验补强。shift 侧: 档位乘年份单元内其他银行 llm_vote_score_full 的 LOO 年度均值, 全文轨为留篇门控主轨, 单元篇数最多。工具语义: 高权威媒体的情感波动 (如政策导向的行业定调) 对基期高权威暴露银行构成更强的舆论冲击, 识别变异来自档位间情感生成机制的分化。缺失语义与家族口径逐条一致: 基期无文章者份额与工具缺失, 档位年份单元剔除自身无剩余时 shift 缺失传播, 早于基期末年前视掩码; media_weights.json 缺失时整族跳过并告警。使用铁律: 与 _ctx, _ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 三档份额下 Rotemberg 权重通常集中于 high 档, 报告集中度以支撑识别叙事。

## VAR: bartik_mauth_iv_ss

【变体差分】
媒体权威性 Bartik 工具的 ss 同句情感轨。share 侧与族内其余轨相同: media_weights.json 评分三档 (high 不低于八十、mid 不低于六十、low 兜底) 的基期文章占比冻结份额。差分仅在 shift 情感文本轨: 档位乘年份单元内其他银行 llm_vote_score_ss — 银行与金融科技同句窗口情感分 — 的 LOO 年度均值, 把权威档位情感冲击的测量收紧到确实同句谈论银行金融科技的语句, 剔除高权威媒体长篇政经报道中与银行金融科技无关段落的情感串扰 — 该串扰在权威媒体上先验最强 (篇幅长、议题广), 故 ss 收紧对本族的测量净化价值高于多数前缀族。ss 回退语义按全仓铁律复述: 无同句共现的文章 ss 文本回退为全文、回退旗标置真、镜像 ctx、共享 full 留篇分母; ss 情感列缺席时守卫优雅置缺失。基期解析与 2019 红线、单元剔除自身无剩余缺失传播、前视掩码逐条继承家族口径。使用口径: ss 为 conditional-on-full 稳健性轨, 与族内 full, ctx 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与 media 族并排不叠加。同句单元在 mid 与 low 档的年份篇数最稀, 本列缺失面与弱工具风险先验最高, 报告 Anderson-Rubin 置信区间为宜; 开发面板整列缺失属预期退化。

## VAR: bartik_media_iv_ctx

【变体差分】
媒体三方分类 Bartik 工具的 ctx 情感轨。该族份额维度是媒体类型三分: 以 media_classification.json 的名录把文章来源划为财经类 (fin)、综合类 (comp) 与其他 (other), 银行 i 基期文章在保留类别上的占比冻结为份额。口径要点: other 为兜底类别, 按家族统一修复从份额分子与分母双侧排除后重归一 — 修复前 other 计入分母不进分子曾致本族份额和仅约七成、与 type 族份额和为一的归一化口径不可比、跨工具系数失真, 修复后两族可比。媒体类型属机构层前定属性, 财经媒体与综合媒体的选题与情感生成机制差异 (市场化财经报道对泛新闻报道) 提供识别变异, v6 审查仅保留此三方分类、删除八个高相关二分变体以避免多重检验膨胀。shift 侧为类型乘年份单元内其他银行 llm_vote_score_ctx (实体窗口情感分) 的 LOO 年度均值; 与 canonical 的唯一差分在 shift 文本轨。缺失语义: 基期无文章或基期文章全落 other 的银行份额与工具缺失, 单元剔除自身无剩余时 shift 缺失传播, 前视掩码同家族口径; media_classification.json 缺失时整族跳过。使用铁律: 与族内 full, ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与 mauth 权威档位族份额高度相关, 二族并排取一, 禁同规格叠加。

## VAR: bartik_media_iv_full

【变体差分】
媒体三方分类 Bartik 工具的 full 情感轨, 该族 canonical 本体。share 侧: media_classification.json 名录驱动的 fin 对 comp 二维保留份额 (other 兜底类别双侧排除后归一), 按银行 i 基期文章类型占比冻结。识别叙事: 基期被财经媒体密集覆盖的银行与被综合媒体覆盖的银行, 接收的是两套情感生成机制不同的报道流 — 财经媒体紧跟市场与监管议题、情感波动与行业周期同步, 综合媒体则受属地与社会议题驱动; 基期类型构成决定银行对两套报道流年度情感波动的相对暴露, 而该波动由同类型媒体对其他银行的报道实现驱动。中国媒体市场的商业化分层 (Qin, Strömberg & Wu 2018) 为类型间机制差异提供制度证据。shift 侧: 类型乘年份单元内其他银行 llm_vote_score_full 的 LOO 年度均值, 全文轨为留篇门控主轨。缺失语义逐条继承家族口径: 基期无文章或全落 other 者缺失且不以零填充, 单元剔除自身无剩余时缺失传播, 早于基期末年前视掩码, 分类名录缺失整族跳过并告警。方法学注记: 保留类别仅两维时, 份额向量退化为单自由度 (fin 占比与 comp 占比之和为一), 识别实际由单一维度驱动, Rotemberg 权重分解在本族信息量有限, 弱工具诊断相应更承重。使用铁律: 与 _ctx, _ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与 mauth 族并排取一。

## VAR: bartik_media_iv_ss

【变体差分】
媒体三方分类 Bartik 工具的 ss 同句情感轨。share 侧与族内其余轨相同: fin 对 comp 保留类别的基期文章占比 (other 双侧排除后归一) 冻结份额。差分仅在 shift 情感文本轨: 类型乘年份单元内其他银行 llm_vote_score_ss — 银行与金融科技同句窗口情感分 — 的 LOO 年度均值。同句收紧对本族的针对性价值: 综合类媒体报道中银行金融科技往往只是长篇社会经济叙事的一个段落, 全文情感大量承载无关议题的情绪, ss 判据把 comp 类单元的情感测量净化到直接谈论银行金融科技的语句, 使两类媒体的 shift 在构念上更可比。ss 回退语义按全仓铁律复述: 无银行金科同句共现的文章 ss 文本回退为全文、回退旗标置真、镜像 ctx、共享 full 留篇分母, 回退占比高的类型单元其净化效果相应打折; stage 21 未产 ss 情感列时守卫优雅置缺失。基期解析与红线、缺失传播、前视掩码逐条继承。使用口径: ss 为 conditional-on-full 稳健性轨, 与族内 full, ctx 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与 mauth 族并排取一。同句判定在综合类媒体上覆盖最稀, 本列该维度 shift 的有效篇数先验最少, 弱工具诊断必报; 开发面板整列缺失属预期退化。

## VAR: bartik_scale_iv_ctx

【变体差分】
银行规模 Bartik 工具的 ctx 情感轨。该族由通用引擎生产, 与 type 族同机制而分组维度不同: 组别标签取 bank_addresses.json 的企业规模四分 (L 大型、M 中型、S 小型、XS 微型, 未映射落 other 且双侧排除), share 为银行 i 基期文章中经 co_mentioned_banks 共现字段统计的跨规模组暴露占比 — 即基期与哪些规模档的同业在同篇报道中共同出现。规模是监管报表层面的前定机构属性, 满足份额前定性的形式要求; 识别直觉是共现网络的规模结构: 基期常与大型银行同篇出现的银行, 持续暴露于大型银行群体的报道情感波动。shift 侧为规模组乘年份单元内其他银行 llm_vote_score_ctx (实体窗口情感分) 的 LOO 年度均值; 与 canonical 的唯一差分在 shift 文本轨。基期无共现文章但自身规模组可识别的银行, 份额按自身组独热兜底; 自身组落 other 者保持缺失 (伪零修复口径)。其余语义 (T0 解析与 2019 红线、单元剔除自身无剩余缺失传播、前视掩码、整型升双精度防回绕) 逐条继承家族口径。使用铁律: 与族内 full, ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与 type 族是同引擎不同分组维度的并排族, 论文以 type 为主规格、本族作稳健性, 跨族组合方可做过度识别检验。

## VAR: bartik_scale_iv_full

【变体差分】
银行规模 Bartik 工具的 full 情感轨, 该族 canonical 本体, 在 runner 步骤 7e 中作为 type 主规格之后的第一稳健性族显式生产。share 侧: 企业规模四分组 (L, M, S, XS) 的基期共现份额, 经 co_mentioned_banks 字段按分号切分共现银行名单、映射到规模组、剔除 other 后计数归一; 基期无共现的银行按自身组独热兜底 (自身组不可识别者缺失), 该兜底承认"无共现记录的银行至少暴露于自身规模组"的最小信息假设。shift 侧: 规模组乘年份单元内其他银行 llm_vote_score_full (全文轨三家投票情感分) 的 LOO 年度均值, 全文轨为留篇门控主轨。识别叙事: 银行业报道存在按规模分层的行业叙事 (大行政策定调、中小行风险专题), 基期共现结构决定银行对各层叙事情感波动的暴露强度; 与 type 族的监管类型分层相比, 规模分层捕获的是体量维度的行业冲击, 两族份额相关但不重合, 构成识别通道的三角验证。数值防线注记: 本族与 type 族共享通用引擎的整型升双精度修复 — LOO 减除链在窄整型上会静默回绕并翻转 shift 符号, 修复后全链双精度。缺失语义、基期解析与红线、前视掩码逐条继承家族口径。使用铁律: 与 _ctx, _ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与 type 族并排、主规格取 type, 本族入稳健性附表; 四维份额的 Rotemberg 权重集中度随样本共现结构报告。

## VAR: bartik_scale_iv_ss

【变体差分】
银行规模 Bartik 工具的 ss 同句情感轨。share 侧与族内其余轨完全相同: 企业规模四分组的基期共现份额 (co_mentioned_banks 驱动, other 双侧排除, 无共现者自身组独热兜底)。差分仅在 shift 情感文本轨: 规模组乘年份单元内其他银行 llm_vote_score_ss — 银行与金融科技同句窗口情感分 — 的 LOO 年度均值, 把规模分层叙事的情感冲击收紧到确实同句谈论银行金融科技的语句。ss 回退语义按全仓铁律复述: 无同句共现的文章 ss 文本回退为全文、回退旗标置真、镜像 ctx、共享 full 留篇分母; stage 21 未产 ss 情感列时引擎守卫将本列优雅置缺失而非中断整个步骤。基期解析 (T0 取面板最早年与 2010 较晚者、强制早于 2019 政策里程碑)、单元剔除自身无剩余时缺失传播、早于基期末年前视掩码、整型升双精度防回绕等语义逐条继承家族口径。方法学定位: 本列与 full, ctx 轨的系数对照检验规模通道识别是否被情感测量窗口驱动, 三轨同号同量级则该通道稳健。使用口径: ss 为 conditional-on-full 稳健性轨, 与族内 full, ctx 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与 type 族并排。小规模组的同句单元篇数最稀, 弱工具诊断必报; 开发面板整列缺失属预期退化, 生产十八年面板下方可评估。

## VAR: bartik_subst_iv_ctx

【变体差分】
实质性 Bartik 工具的 ctx 轨。该前缀族服务于实质性对象征性论文 (bank_fintech_substance, 组合内 P3), 内生处理变量为银行金融科技报道中实质性占比 sub_frac 族测度。本列与 canonical (full 轨) 的差分在 shift 源: 取文章级 LLM 分类列 innovation_substantiveness_ctx — 实体窗口轨上三家大模型投票判定的"实质性对象征性"创新属性 — 经取值映射 (实质性记一、象征性记零, 映射外取值缺失且不进分子分母) 转为零一指示后, 在 type 组别乘年份单元内做 LOO 均值。shift 的经济含义是"同组其他银行当年被报道的金融科技实质性倾向", 实体窗口归因把该判定收紧到目标银行邻近语境, 剔除同篇文章对其他机构实质性行为叙述的串扰。share 侧复用步骤 7e 冻结的 type 维度基期共现份额, 与族内其余轨完全相同, 数值差异全部来自分类判定的窗口归因差异。取值映射的分母纪律与 collab 族一致: 只有有效判定进入 shift 分子分母, 未分类文章不稀释指示均值。缺失语义、基期解析与红线、前视掩码逐条继承家族口径。使用铁律: ctx 为 conditional-on-full 稳健性轨, 与族内 full, ss 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与 lpeer_subst_iv_ctx (LOO 引擎) 跨引擎组合方可做过度识别检验。

## VAR: bartik_subst_iv_full

【变体差分】
实质性 Bartik 工具的 full 轨, tier 为 core: 实质性对象征性论文 (bank_fintech_substance, 组合内 P3) 在 paper_spec 的 identification.iv 声明中收录本列为识别策略主工具, 根级与论文级二阶段最小二乘模板按本列名实例化。构念背景: 该论文检验银行金融科技活动的实质性 (真实技术投入与业务落地) 对象征性 (公关叙事与跟风表态) 之别对长期成本效率的差异化影响, 处理变量为媒体报道经 LLM 判定的实质性占比, 其内生性来源是经营质量同时驱动实质性行为与媒体刻画。构造全链: share 侧复用步骤 7e 冻结的 type 维度基期共现份额 (六类监管类型同业的基期共现占比, 兜底双侧排除归一, 基期无共现文章者整列缺失, 不以零填充制造伪零暴露); shift 侧取文章级 innovation_substantiveness_full — 全文轨三家大模型投票的实质性分类 — 经实质性记一、象征性记零的取值映射转为指示后, 在组别乘年份单元内剔除银行 i 自身贡献求均值, 组内仅剩自身时缺失传播; 早于基期末年的面板行前视掩码置缺失。识别直觉: 银行 i 基期的同业暴露结构决定其接收"同组他行实质性叙事浪潮"的强度, 该浪潮由其他银行的报道实现驱动, 与银行 i 自身当年的实质性决策在构造上无关; 识别重量押在 GPSS 份额外生性路径, shift 为内生 LOO 分类均值, 冲击外生性路径不可用, 论文须报告基期前定性论证与 Rotemberg 权重集中度, 过度识别检验只能以本列与 LOO 引擎工具 (leave_one_out_peer_subst_iv 族) 跨引擎组合进行。分类 shift 的弱工具考量与 collab 族同: 指示均值方差随组年有效判定篇数收缩, Kleibergen-Paap 秩 F 对照有效 t 比值临界值必报, 少簇场景配 wild bootstrap。使用铁律: 与 _ctx, _ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; full 轨为留篇门控主轨, 主表伴随 Romano-Wolf 多重检验校正。构念区分与排他性叙事: 实质性维度的排他性论证有其特殊性 — 同组他行的实质性叙事浪潮影响本行成本效率的合法通道只能经由本行的实质性行为响应 (竞争压力驱动的真实投入), 若浪潮同时直接改变本行的市场估值或监管态度, 排他性即受威胁; 论文须以时序结构 (结果变量为多年前瞻变化) 与控制变量集 (同期估值与监管代理) 封堵旁路, 这一论证义务比注意力族更重, 因实质性构念与经营质量的先验相关更强。与协同族 (bartik_collab_iv_full) 的平行结构对照见该列条目, 两个分类维度构念正交、各服务一篇论文。取值映射的分母纪律再强调一次: 只有被大模型有效判定为实质性或象征性的文章进入 shift 分子分母, 未分类文章不稀释指示均值, 该口径与情感 shift 引擎的数值列直用口径不同, 复算时最易在此处出错。开发面板两年期下组年有效判定稀少, 一阶段结论不得外推到生产面板; 换大模型属改测度类改动, 分类分布漂移会直接传导到本列, 须走受控重生流程并在论文数据附录披露。推断层配套须与实质性论文的多年前瞻结果变量设定匹配: 工具与处理变量同年、结果跨年, 使用者在动态设定中引入本列滞后时须自行保证前视掩码语义不被手工位移破坏 (掩码按当年基期关系施加, 手工 shift 不重算掩码)。弱工具诊断上, 本列为 just-identified 单工具但分类 shift 方差随组年有效篇数收缩, 疑弱风险高于情感 shift 族, Kleibergen-Paap 秩 F 对照 Stock & Yogo (2005) 与 Lee, McCrary, Moreira & Porter (2022) 临界值必报, 主结论以 Anderson-Rubin 弱工具稳健区间为宜, 少簇配 Wang & Zhang (2024) wild bootstrap; 保留工具族多于单一工具, 主表伴随 Romano & Wolf (2005) 逐步降压多重检验校正以压制跨维度挑选空间。Rotemberg 权重的类型维度集中度须在本列上按 Goldsmith-Pinkham, Sorkin & Swift (2020) 分解报告, 民营等小组别的权重解读尤须谨慎。

## VAR: bartik_subst_iv_ss

【变体差分】
实质性 Bartik 工具的 ss 同句轨。差分仅在 shift 源: 取 innovation_substantiveness_ss — 银行与金科同句窗口文本上的实质性对象征性 LLM 分类 — 经实质性记一、象征性记零映射后做 type 组年 LOO 均值。同句判据对本族的构念针对性: 实质性判定高度依赖具体行为证据语句 (投资金额、系统上线、合作签约), 这类语句往往正是银行名与金融科技词同句出现之处, 故 ss 收紧在理论上保留了实质性判定的证据核心、剔除的是外围修辞段落 — ss 轨与 full 轨系数的稳定对照因此构成"实质性测量不靠修辞驱动"的针对性稳健证据。回退语义按全仓铁律复述: 无同句共现的文章 ss 文本回退为全文且回退旗标置真 (镜像 ctx), 共享 full 留篇分母, 回退文章上的分类实际承载全文判定; stage 21 未产 ss 分类列时轨源守卫将本列优雅置缺失。share 侧复用 type 基期共现份额, 映射外取值不进分子分母、基期解析与红线、单元剔除自身无剩余缺失传播、前视掩码逐条继承家族口径。使用口径: ss 为 conditional-on-full 稳健性轨, 与族内 full, ctx 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 开发面板同句分类覆盖稀疏致本列大面积缺失属预期退化, 生产语料下与 lpeer_subst_iv_ss 跨引擎组合可支撑过度识别检验。

## VAR: bartik_type_iv_ctx

【变体差分】
银行类型 Bartik 工具的 ctx 情感轨, tier 为 core: 战略差异化论文 (strategic_diff) 在 paper_spec 的 identification.iv 声明中收录本列为识别策略主工具之一 — 该论文的主测度族以实体窗口轨为主轨 (战略文本区分度构念要求把叙事归因到目标银行自身), 故其工具亦对齐 ctx 轨, 与多数论文以 full 轨为主的口径刻意不同。构造: share 侧为 type 维度基期共现份额 — 银行 i 基期文章经 co_mentioned_banks 字段统计的与六类监管类型同业 (国有大型 soe、股份制 joint、城商 city、农商 rural、民营 private、外资 foreign) 的共现占比, 兜底类别 other 双侧排除后归一, 基期无共现者按自身组独热兜底、自身组不可识别者缺失; shift 侧为类型组乘年份单元内其他银行 llm_vote_score_ctx (实体窗口轨三家投票情感分) 的 LOO 年度均值。识别直觉: 监管类型是银行业最根本的制度分层, 类型组内共享监管冲击与行业叙事, 基期共现结构决定银行对各类型组情感波动的暴露; 实体窗口情感把该波动的测量收紧到与被报道银行直接关联的语境。数值防线 (整型升双精度防 LOO 回绕)、缺失语义 (伪零修复、单元剔除自身无剩余缺失传播)、基期解析与 2019 红线、前视掩码逐条继承家族口径。使用铁律: 与族内 full, ss 轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 本列另有 _t0, _t01, _t1 三个基期敏感性变体 (仅 type 族物化), 梯子各臂同样并排禁混; 与 lpeer 族跨引擎组合方可做过度识别检验, 主表伴随 Romano-Wolf 校正。作为 core 列, 本列是 strategic_diff 二阶段模板的一阶段工具, 弱工具诊断 (Kleibergen-Paap 秩 F、有效 t 比值临界值、Anderson-Rubin 置信区间) 与少簇 wild bootstrap 为必报项。为何战略差异化论文的主工具取 ctx 轨而非家族惯例的 full 轨, 值得展开: 该论文的处理变量是银行金融科技叙事相对同业的文本区分度, 其测量在实体窗口轨上构造 — 区分度构念要求比较的是各银行被如何刻画, 全文轨会把同篇文章中其他机构的叙事混入目标银行画像, 直接稀释区分度信号; 处理变量在 ctx 轨, 工具的 shift 情感也对齐 ctx 轨, 保证工具与处理变量的测量窗口一致, 避免窗口错配引入的衰减偏误。这一对齐原则是家族层的一般规则: 工具的 shift 轨应与被工具化处理变量的主轨一致, 其余轨作稳健性。与 full 轨核心列 (bartik_type_iv_full) 的关系: 两列共享同一份额向量, 仅 shift 情感窗口不同, 在战略差异化论文内 full 轨列充当本列的稳健性对照臂 (该论文识别声明同时收录两列, 各自 just-identified 分规格并排), 绝不同时入同一回归。ss 轨与本列的对照则检验更严格的同句归因下结论是否存续。基期梯子注记: type 族是家族内唯一物化 _t0, _t01, _t1 三臂基期梯子的前缀族, 本列的三个变体与本列互为稳健性不分主次, 各臂固定 ctx 轨仅变基期口径, 与三轨维度正交不交叉。开发面板两年期下基期共现份额独热退化、组间区分度耗尽, 本列一阶段统计量仅作管道冒烟不得外推, 正式弱工具评估以生产十八年面板为准。战略差异化论文的排他性论证在 ctx 轨上有对齐红利也有独立义务: 工具 shift 与处理变量同取实体窗口轨, 消除了窗口错配的衰减偏误, 但同组他行的实体窗口情感浪潮影响本行战略文本区分度的合法通道 (竞争性叙事分化) 须与直接经市场估值旁路的可能性分离, 论文以结果变量时序 (Tobin q 等前瞻量) 与同期估值控制封堵。份额层诊断与 full 轨核心列共享: 两列同一 type 份额向量, Rotemberg 权重分解与基期平衡性检验按 Goldsmith-Pinkham, Sorkin & Swift (2020) 在 type 维度做一次即覆盖两轨, 民营组份额分量单独落盘供复算。弱工具与少簇防线 (Stock & Yogo 2005 与 Lee, McCrary, Moreira & Porter 2022 临界值、Anderson-Rubin 区间、Wang & Zhang 2024 wild bootstrap) 与 Romano & Wolf (2005) 主表校正为必报项; 推断的份额结构依赖 (Adão, Kolesár & Morales 2019) 要求以份额感知聚类补强常规按银行聚类的标准误。

## VAR: bartik_type_iv_ctx_t0

【变体差分】
bartik_type_iv_ctx 的基期敏感性变体, 基期显式固定为 T0 (与主列相同的解析基期, 即面板最早年与 2010 的较晚者)。本列的方法学角色是基期梯子的参照臂: 三臂梯子 (_t0 基期 T0、_t1 基期 T0 加一年、_t01 双年池化) 用以证明工具与二阶段结论不被基期落点选择驱动, 而 _t0 臂给出与主列同基期但经独立重算路径 (runner 以精简面板骨架重新调用通用引擎后按银行与年份键 merge 回主面板) 生产的对照值 — 在实现无缺陷时应与主列逐位一致, 因此同时充当基期梯子的锚点与构造路径的自检哨兵。shift 侧与主列相同: 类型组乘年份单元内其他银行实体窗口情感分的 LOO 年度均值; share 侧为 T0 单年冻结的六类监管类型共现份额。外生性守卫: 变体构造循环内显式检查基期是否触及 2019 政策里程碑, 触线则三轨整列置缺失并告警而非静默生产违反前定性公理的工具。工程史注记: 该族曾有 merge 回选清单遗漏 ss 轨致其变体列被静默丢弃的缺陷, 已修复为程序化三轨列表; 本列的 merge 对齐全程键驱动不依赖行序。使用口径: 基期梯子三臂与主列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 梯子与三轨两个维度正交, 本列固定 ctx 轨仅变基期。

## VAR: bartik_type_iv_ctx_t01

【变体差分】
bartik_type_iv_ctx 的双年池化基期变体: share 在基期年集合 {T0, T0 加一年} 上池化冻结 — 两年文章合并后统计跨类型组共现占比, 相当于以更厚的基期样本平滑单年共现结构的偶然波动, 是基期梯子中方差最小的份额估计臂。池化语义有明确的工程勘误史: 旧实现曾把两年子集当全量文章传入而引擎内部仍只取单年份额, 池化从未发生, 该变体与 _t0 臂字节级相同 (幻影变体), 且 shift 聚合域被截断到基期两年、其余年份经零填充制成精确伪零; 修复后改为传全量文章加显式基期年集合参数, 引擎内真池化, shift 聚合域覆盖全部年份。前视掩码按池化口径收紧: 早于基期集合末年 (T0 加一年) 的面板行工具置缺失, 比单年臂多掩一年。外生性守卫同样按池化口径: 基期集合含 T0 加一年, 若其触及 2019 政策里程碑则三轨整列缺失并告警。shift 侧与主列相同 (ctx 轨情感的类型组年 LOO 均值), 差异全部来自份额的基期口径。使用铁律: 基期梯子三臂 (_t0, _t1, _t01) 与主列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 本列固定 ctx 轨仅变基期, 梯子与三轨维度正交不交叉。开发面板仅两年时池化基期即覆盖全样本, 该臂退化属预期, 解读以生产十八年面板为准。

## VAR: bartik_type_iv_ctx_t1

【变体差分】
bartik_type_iv_ctx 的后移基期变体: share 在 T0 加一年的单年上冻结, 检验主结论对基期整体后移一年的敏感性。该臂的独特承重在外生性守卫: 主列的红线只检查 T0 早于 2019 政策里程碑, 而本臂基期为 T0 加一年, 可能恰好落入后处理区间 (例如面板起始于二零一八年时本臂基期落到二零一九年, 绕过主列红线) — 专项修复后变体构造循环对每个臂的实际基期单独检查, 触线则三轨整列置缺失并告警, 绝不静默生产份额测自政策后区间、违反 GPSS 前定性公理的工具。前视掩码同步后移: 早于本臂基期的面板行 (含 T0 当年) 工具置缺失, 因其份额测自这些行的未来。构造路径与 _t0 臂相同: 精简面板骨架重调引擎、按键 merge 回主面板、程序化三轨回选清单 (含 ss 轨补齐修复)。shift 侧与主列一致 (ctx 轨情感的类型组年 LOO 均值), 数值差异来自基期年文章构成的变化 — 若两个相邻基期给出的工具在二阶段产生同号同量级系数, 则基期落点不驱动结论。使用口径: 基期梯子三臂与主列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 本列固定 ctx 轨仅变基期, 与三轨维度正交。开发面板上本臂基期为末年, 前视掩码掩去首年, 有效行进一步收缩属预期退化。

## VAR: bartik_type_iv_full

【变体差分】
银行类型 Bartik 工具的 full 情感轨, tier 为 core, 且是全家族识别载荷最重的单列: 同时被两篇论文的 paper_spec identification.iv 声明收录 — 声誉语调论文 (bank_fintech_tone, 组合内 P1, 处理变量为三家投票语调 llm_vote_tone_full) 与战略差异化论文 (strategic_diff) — 二阶段最小二乘模板按本列名双处实例化。构造全链: share 侧为 type 维度基期共现份额, 经 co_mentioned_banks 字段按分号切分共现银行名单、映射到 bank_addresses.json 的监管类型六分 (国有大型、股份制、城商、农商、民营、外资), 兜底 other 双侧排除后计数归一; 基期无共现文章的银行按自身类型组独热兜底, 自身组不可识别者保持缺失 — 伪零修复的直接受益列, 修复前零填充曾制造十二至五十个标准差量级的伪零暴露直接污染一阶段。shift 侧为类型组乘年份单元内其他银行 llm_vote_score_full (全文轨三家大模型投票情感分, 留篇门控主轨) 的 LOO 年度均值, LOO 减除链全程双精度 (整型回绕修复), 组内剔除自身后无剩余观测的单元缺失并向工具传播。识别叙事: 监管类型是中国银行业最根本的制度分层, 同类型银行共享监管政策冲击、准入约束与行业叙事框架; 银行 i 基期在报道中与各类型同业的共现结构, 刻画其在行业舆论网络中的位置, 决定各类型组情感浪潮向其传导的强度 — 该浪潮由其他银行的报道实现驱动, 与银行 i 自身当年表现在构造上无关。识别重量押在 GPSS 份额外生性路径; shift 为内生 LOO 情感均值而非准随机冲击, 冲击外生性路径不可用, 论文须报告基期共现结构的前定性论证、Rotemberg 权重的类型维度集中度、以及份额感知的推断修正。本列另有 _t0, _t01, _t1 三个基期敏感性变体 (仅 type 族物化此梯子, 因其识别载荷最重), 三臂与本列互为稳健性不分主次、各自 just-identified 并排、禁混同一 over-identified Hansen J; 三轨维度同禁: 本列与 _ctx, _ss 轨严禁拼进同一过度识别检验, 同篇三窗共同冲击使 J 检验零功效, overid 须与 LOO 引擎或经济圈引擎工具跨族组合。弱工具与少簇防线 (Kleibergen-Paap 秩 F、有效 t 比值、Anderson-Rubin 置信区间、wild bootstrap) 与 Romano-Wolf 主表校正为两篇论文模板的共同必报项。基期解析 T0 取面板最早年与 2010 较晚者且强制早于 2019 里程碑, 早于基期末年的面板行前视掩码置缺失。双论文共享的解读纪律: 语调论文与战略差异化论文各自独立设定二阶段, 本列在两处的排他性论证互不通用 — 同组情感浪潮对融资成本无直接通道的论证, 不能移植为对市场估值无直接通道; 每篇论文须在自身处理变量与结果变量的构念下重新论证工具有效性, 数据层的列复用只是构造经济性, 不构成识别论证的复用。份额诊断的归属: 本列的份额向量是全家族被复用最广的一套 (attention, subst, collab 三族直接引用), Rotemberg 权重分解与基期平衡性检验以本列所属的 type 维度为准做一次、结论跨引用族共享; 民营组份额分量单独落盘 (bartik_type_share_private) 供该诊断与审稿复算。开发面板注意: 两年期下共现份额独热退化、shift 的组年单元稀疏, 本列在开发面板上的任何一阶段统计量仅作管道正确性冒烟, 不得写入论文; 生产十八年面板下, 前视掩码将实际作用于 T0 之前的年份行 (二零零七至二零零九), 使用者应预期这些行工具整列缺失并在样本声明中如实报告。作为家族识别载荷最重的单列, 本列的诊断规范也最严: Rotemberg 权重若集中于国有大型或股份制等大组, 论文须针对该主导维度而非全份额向量论证前定性 (Goldsmith-Pinkham, Sorkin & Swift 2020); 若出现负权重, 提示不同类型维度的隐含二阶段相互抵消、识别脆弱, 须按 Borusyak, Hull & Jaravel (2025) 核对清单复核不完整份额与重归一化。推断以份额感知修正 (Adão, Kolesár & Morales 2019) 与弱工具稳健区间 (Andrews, Stock & Sun 2019) 双重补强, 主表配 Romano & Wolf (2005) 校正。

## VAR: bartik_type_iv_full_t0

【变体差分】
bartik_type_iv_full 的基期参照臂: 基期显式固定为主列同款 T0, 经独立重算路径生产。runner 在变体循环中以仅含银行与年份两列的精简面板骨架重新调用通用引擎, 对全量文章重算 T0 单年冻结份额与全年份 LOO shift, 再把结果列改名加 _t0 尾缀后按银行与年份键 merge 回主面板 — 与主列在无实现缺陷时逐位一致, 故本臂兼具基期梯子锚点与构造路径自检哨兵的双重角色: 若本臂与主列出现数值分歧, 指向 merge 对齐或状态泄漏缺陷而非经济内容差异。shift 侧为类型组乘年份单元内其他银行全文轨情感分 (留篇门控主轨) 的 LOO 年度均值; share 为六类监管类型的 T0 单年共现份额, 兜底双侧排除、独热兜底与缺失语义同主列。外生性守卫在变体循环内逐臂执行: 基期触及 2019 政策里程碑则三轨整列缺失并告警。工程史注记: merge 回选清单曾遗漏 ss 轨 (v3.9.0 引入 ss 时漏改), 造成该轨变体死计算后被丢弃, 已修复为程序化三轨列表, 本臂三轨齐全。使用口径: 基期梯子三臂 (_t0, _t1, _t01) 与主列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 本列固定 full 轨仅变基期构造路径, 梯子与三轨维度正交不交叉。

## VAR: bartik_type_iv_full_t01

【变体差分】
bartik_type_iv_full 的双年池化基期臂: share 在 {T0, T0 加一年} 两年文章的合并样本上统计跨类型组共现占比后冻结, 以更厚的基期支撑平滑单年共现结构的偶然波动 — 对基期恰逢个别银行重大事件 (共现结构被单一事件扭曲) 的场景, 池化臂给出更稳的份额估计, 是梯子中份额方差最小的一臂。真池化语义有承重勘误史: 旧实现传入两年子集文章而引擎内部仍只取单年, 池化从未发生, 本臂与 _t0 臂字节级相同 (幻影变体), 且 shift 聚合域被截断到基期两年、其余年份的 shift 缺失经旧零填充制成工具精确伪零; 修复后改传全量文章加显式基期年集合参数, 引擎内以年份集合过滤真池化, shift 聚合域覆盖全部年份, 零填充同批清除。前视掩码按池化口径收紧到基期集合末年: 早于 T0 加一年的面板行 (含 T0 当年) 工具置缺失。外生性守卫按池化口径: 集合含 T0 加一年, 触及 2019 里程碑则三轨整列缺失并告警。shift 侧与主列一致 (全文轨情感的类型组年 LOO 均值)。使用铁律: 梯子三臂与主列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 本列固定 full 轨仅变基期口径, 与三轨维度正交。开发面板两年时池化基期覆盖全样本属预期退化, 解读以生产面板为准。

## VAR: bartik_type_iv_full_t1

【变体差分】
bartik_type_iv_full 的后移基期臂: share 在 T0 加一年的单年文章上冻结, 与主列 (基期 T0) 对照检验识别结论对基期落点整体后移一年的敏感性 — 若相邻两个基期测得的共现结构给出同号同量级的二阶段系数, 则"基期恰好选在哪一年"不驱动结论, 这是 GPSS 框架下份额前定性叙事的标准补强证据。本臂的独特守卫承重: 主列红线只约束 T0 本身早于 2019 政策里程碑, 后移臂的实际基期 T0 加一年可能恰好触线 (面板起始二零一八年时本臂基期为二零一九年, 若不单检即绕过红线、份额测自数字人民币与沙盒试点后的区间); 专项修复后变体循环对每臂实际基期单独执行守卫, 触线则三轨整列置缺失并告警, 拒绝静默生产违反前定性公理的工具。前视掩码同步后移: T0 当年的面板行因份额测自其未来而置缺失, 本臂有效行天然比主列少一年。构造路径同 _t0 臂: 精简骨架重调引擎、键 merge 回面板、程序化三轨回选 (ss 轨补齐修复后三轨齐全)。shift 侧与主列一致: 类型组乘年份单元内其他银行全文轨情感分的 LOO 年度均值。使用口径: 梯子三臂与主列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 本列固定 full 轨仅变基期, 与三轨维度正交不交叉。

## VAR: bartik_type_iv_ss

【变体差分】
银行类型 Bartik 工具的 ss 同句情感轨。share 侧与 type 族其余轨完全相同: 六类监管类型的基期共现份额 (co_mentioned_banks 驱动, other 双侧排除, 无共现者自身组独热兜底, 自身组不可识别者缺失)。差分仅在 shift 情感文本轨: 类型组乘年份单元内其他银行 llm_vote_score_ss — 银行与金融科技同句窗口文本上的三家投票情感分 — 的 LOO 年度均值, 把类型分层行业叙事的情感冲击收紧到确实同句谈论银行金融科技的语句, 剔除长篇行业综述中与金融科技无关段落的情感串扰。ss 回退语义按全仓铁律复述: 文章无银行金科同句共现时 ss 文本回退为全文正文且回退旗标置真, 与 ctx 轨镜像, 共享 full 留篇分母 — 回退占比高的类型组年单元, 其 shift 实际承载全文信号, ss 与 full 轨的差异强度由同句共现普及率决定; stage 21 未产 ss 情感列时引擎守卫将本列优雅置缺失。数值防线 (双精度 LOO)、缺失语义、基期解析与 2019 红线、前视掩码逐条继承家族口径。本列同样物化 _t0, _t01, _t1 基期梯子 (梯子构造循环程序化覆盖三轨, ss 轨曾因 merge 回选遗漏被丢弃、已修复补齐)。使用铁律: ss 为 conditional-on-full 稳健性轨, 与族内 full, ctx 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 基期梯子与三轨维度正交, 各臂同禁。开发面板同句覆盖稀疏致本列缺失面大属预期退化, 生产面板下方可评估其一阶段贡献。

## VAR: bartik_type_iv_ss_t0

【变体差分】
bartik_type_iv_ss 的基期参照臂: 基期显式固定为主解析 T0, 经变体循环的独立重算路径生产, 与 ss 主列在无实现缺陷时逐位一致, 兼具基期梯子锚点与构造自检哨兵双角色。shift 侧为类型组乘年份单元内其他银行同句窗口情感分的 LOO 年度均值 (ss 回退语义随源列继承: 无同句共现文章的情感判定实际承载全文信号); share 为六类监管类型的 T0 单年共现份额。本列的存在本身携带一段承重工程史: v3.9.0 引入 ss 轨时, 基期变体的 merge 回选清单未同步扩到三轨, ss 变体列在临时面板上被改名造出后即遭丢弃 — 死计算加三轨平价破坏; 二零二六年六月二十五日的 merge 平价修复把回选清单改为按三轨元组程序化生成, 本列自此真实落盘。该史实的方法学教益是三轨平价须由程序化清单而非手写列名保障, 后续所有三轨扩列均沿此口径。外生性守卫逐臂执行: 基期触及 2019 政策里程碑则整列缺失并告警; 前视掩码、缺失传播、双精度 LOO 逐条继承家族口径。使用口径: 基期梯子三臂与 ss 主列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 本列固定 ss 轨仅变基期构造路径, 梯子、三轨两维正交不交叉; ss 为 conditional-on-full 稳健性轨, 开发面板缺失面大属预期。

## VAR: bartik_type_iv_ss_t01

【变体差分】
bartik_type_iv_ss 的双年池化基期臂: share 在 {T0, T0 加一年} 合并文章样本上统计六类监管类型共现占比后冻结, shift 为类型组年单元内其他银行同句窗口情感分的 LOO 年度均值。池化臂在 ss 轨上的针对性价值: 同句共现文章本就稀疏, 单年基期的共现份额在 ss 语料结构下更易被个别文章扭曲, 双年池化以更厚的基期支撑压低份额估计方差 — 尽管份额本身统计自全部基期文章而非仅同句文章 (share 与 shift 的文本判据独立: 份额由共现字段驱动、不分轨, shift 才分轨), 该臂仍是 ss 轨基期稳健性的标准对照。真池化勘误史与 full 轨条目所述相同: 旧实现的幻影池化 (与 _t0 字节级相同) 加 shift 聚合域截断伪零已被修复, 现为全量文章加显式基期集合的引擎内真池化。前视掩码收紧到池化集合末年, 早于 T0 加一年的行置缺失; 外生性守卫按集合末年执行, 触及 2019 里程碑则整列缺失告警。merge 回选的程序化三轨清单保证本列真实落盘 (ss 轨补齐修复)。使用铁律: 梯子三臂与 ss 主列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 本列固定 ss 轨仅变基期口径, 与三轨维度正交; ss 为 conditional-on-full 稳健性轨, ss 回退语义 (无同句共现回退全文、旗标置真、镜像 ctx、共享 full 分母) 随 shift 源列继承。

## VAR: bartik_type_iv_ss_t1

【变体差分】
bartik_type_iv_ss 的后移基期臂: share 在 T0 加一年单年冻结, shift 为类型组年单元内其他银行同句窗口情感分的 LOO 年度均值。与 ss 主列对照检验同句轨工具对基期落点后移一年的敏感性, 与 full, ctx 轨的同名臂共同构成基期乘文本轨的九格对照面 — 九格系数的符号与量级稳定性是"识别既不被基期选择也不被窗口判据驱动"这一双重稳健主张的完整证据体。守卫承重与 full 轨 _t1 条目相同且对本列同样生效: 后移基期 T0 加一年可能触及 2019 政策里程碑而绕过主列红线, 变体循环逐臂单检, 触线则三轨整列置缺失并告警, 拒绝生产份额测自政策后区间的工具; 前视掩码同步后移, T0 当年面板行置缺失, 本臂有效行比主列少一年。ss 回退语义随 shift 源列继承: 无银行金科同句共现的文章其情感判定回退承载全文信号、旗标置真、镜像 ctx、共享 full 留篇分母。构造路径为精简骨架重调引擎加键 merge 回面板, 程序化三轨回选清单保证 ss 变体真实落盘 (merge 平价修复)。缺失传播、双精度 LOO、兜底双侧排除逐条继承家族口径。使用口径: 基期梯子三臂与 ss 主列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; ss 为 conditional-on-full 稳健性轨, 本列固定 ss 轨仅变基期, 梯子与三轨维度正交不交叉; 开发面板上本臂受同句稀疏与基期后移双重收缩, 缺失面最大属预期退化。

## VAR: bartik_type_share_private

【变体差分】
本列不是工具变量本体, 而是 type 维度基期份额向量中民营银行 (private) 组的份额分量: 银行 i 基期文章经 co_mentioned_banks 共现字段统计, 与民营银行类同业共现的次数占其全部非兜底共现次数的比例, 取值域为零到一, 在基期 T0 一次性冻结后跨年恒定 (面板逐年重复同一银行级数值)。该列与其余五类份额分量 (国有大型、股份制、城商、农商、外资) 共同构成 GPSS 框架的份额向量, 六者对有共现记录的银行按行加总为一。落盘本列的三重用途: 其一, Rotemberg 权重诊断 — GPSS 分解须以份额列与工具列联合计算各维度对识别的贡献权重, 面板内置日志级近似诊断并注明正式论文以 Stata 官方包复算, 民营组因组内银行数少、情感波动大, 其权重解读须格外谨慎; 其二, 平衡性检验 — 份额前定性叙事的标准补强是检验基期份额与银行基期特征的条件相关, 本列是该检验的直接回归元; 其三, 一阶段透明性 — 审稿人可据份额列手工复算工具值核对构造链。缺失语义与工具列同源: 基期无共现文章且自身组不可识别的银行本列缺失 (伪零修复口径, 绝不以零填充把工具缺失伪装成零暴露); 前视掩码不作用于本列 — 工具列在早于基期末年的行被掩码置缺失, 份额列刻意保留原值, 注释明示仅供诊断, 使用者不得把早期行的份额值当作该行可用的暴露测度。本列与任何工具列的关系是构造中间量对成品, 不入二阶段回归右侧, 不参与三轨与基期梯子的并排口径; 若论文按 GPSS 等价性直接以份额向量为工具做 GMM, 则须整组六列同入并遵循份额路径的全部诊断义务, 单列入回归无识别含义。

<!-- rendered-citations:begin -->
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Qin, Z., & Jing, Z. (2025). Fintech Adoption and Credit Risk Mitigation: Evidence from Chinese Commercial Banks. Sustainability. https://doi.org/10.3390/su172210294
Luo, S., Shuai, K., Zhang, Y., Li, W., & He, Y. (2025). Identification and estimation of causal peer effects using instrumental variables. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.05658
Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W. (2024). Overidentification in shift-share designs. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.17049
Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. Journal of the Royal Statistical Society Series A: Statistics in Society, 187(3), 748-771. https://doi.org/10.1093/jrsssa/qnad148
Gabaix, X., & Koijen, R. S. J. (2024). Granular instrumental variables. Journal of Political Economy, 132(7), 2274-2303. https://doi.org/10.1086/728743
Wang, W., & Zhang, Y. (2024). Wild bootstrap inference for instrumental variables regressions with weak and few clusters. Journal of Econometrics, 241(1), 105727. https://doi.org/10.1016/j.jeconom.2024.105727
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. The Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Lee, D. S., McCrary, J., Moreira, M. J., & Porter, J. (2022). Valid t-ratio inference for IV. American Economic Review, 112(10), 3260-3290. https://doi.org/10.1257/aer.20211063
Breuer, M. (2022). Bartik instruments: An applied introduction. Journal of Financial Reporting, 7(1), 49-67. https://doi.org/10.2308/JFR-2021-003
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Dippel, C., Ferrara, A., & Heblich, S. (2020). Causal mediation analysis in instrumental-variables regressions. The Stata Journal, 20(3), 613-626. https://doi.org/10.1177/1536867X20953572
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. The Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Andrews, I., Stock, J. H., & Sun, L. (2019). Weak instruments in instrumental variables regression: Theory and practice. Annual Review of Economics, 11, 727-753. https://doi.org/10.1146/annurev-economics-080218-025643
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media in financial markets. The Journal of Finance, 66(1), 67-97. https://doi.org/10.1111/j.1540-6261.2010.01626.x
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Stock, J. H., & Yogo, M. (2005). Testing for weak instruments in linear IV regression. Identification and inference for econometric models: Essays in honor of Thomas Rothenberg (Cambridge University Press). https://doi.org/10.1017/CBO9780511614491.006
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2024.01.067
Xu, M., He, M., & Tang, X. (2025). Bank competition and labor share: evidence from China. Applied Economics. https://doi.org/10.1080/00036846.2025.2475245
Bao, Y., & Goetz, M. R. (2026). Local peer effects and corporate investment. Journal of Corporate Finance. https://doi.org/10.1016/j.jcorpfin.2025.102935
<!-- rendered-citations:end -->
