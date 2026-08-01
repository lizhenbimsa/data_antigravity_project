---
family_id: F480
columns:
- prov_leave1out_bert_avg_pos_ctx
- prov_leave1out_bert_avg_pos_full
- prov_leave1out_bert_avg_pos_ss
unit: 无量纲比例 (0-1 区间, BERT 正面篇占比的同省同年留一平均)
formula: 'out[i] = (sum_{j in G(i)} bert_pos_share[j] - bert_pos_share[i]) / (|G(i)| - 1), 其中 G(i) = 银行 i 所属 (bank_province, year) 分组; 仅当组内银行数 |G(i)| > 1 时有效, 否则记为缺失'
producer: pipeline\panel\geography.py ; pipeline\panel\export.py
upstream:
- prov_leave1out_tone_full/ctx/ss (同族地理 IV, 情感 LLM 口径孪生列)
- city_leave1out_bert_avg_pos_full/ctx (同构造原语, 城市粒度孪生族, 非本家族列)
- 23_tone_berts (BERT 三模型正面篇占比上游, 经面板聚合为 bert_avg_pos_{track})
citations:
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: 'Firm-Level Political Risk: Measurement and Effects'
  venue: Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 2135-2202
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: 'FinBERT: A Large Language Model for Extracting Information from Financial Text'
  venue: Contemporary Accounting Research
  vol: '40'
  issue: '2'
  pages_or_artno: 806-841
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: 'Bartik Instruments: What, When, Why, and How'
  venue: American Economic Review
  vol: '110'
  issue: '8'
  pages_or_artno: 2586-2624
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: Bank transparency and deposit flows
  venue: Journal of Financial Economics
  vol: '146'
  issue: '2'
  pages_or_artno: 475-501
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: "10.1162/rest.a.263"
  type: "journal"
  authors: "Frandsen, B., Leslie, E., & McIntyre, S."
  year: 2025
  title: "Cluster Jackknife Instrumental Variables Estimation"
  venue: "Review of Economics and Statistics"
  pages_or_artno: "1-19"
- doi: "10.2139/ssrn.4787799"
  type: "wp"
  authors: "Ellis, C., & Jaspersen, J. G."
  year: 2024
  title: "Fixed Effects and the \"Leave-Out'' Instrument"
  venue: "SSRN Electronic Journal"
  pages_or_artno: "4787799"
- doi: "10.1257/aeri.20240184"
  type: "journal"
  authors: "Bobrov, A., Kamdar, R., & Ulate, M."
  year: 2025
  title: "Regional Dissent: Do Local Economic Conditions Influence FOMC Votes?"
  venue: "American Economic Review: Insights"
  vol: "7"
  issue: "2"
  pages_or_artno: "268-284"
new_dois: []
---

## CORE

【构念与来源】
prov_leave1out_bert_avg_pos 家族刻画"同省同年份其他银行的媒体报道 BERT 正面篇占比均值", 在计量上作为目标银行自身 BERT 正面情感测度的排除自身工具变量 (leave-one-out instrument, 简称 LOO-IV)。构念来自地理层面新闻情感的溢出与共振逻辑: 同一省份银行往往共享区域性金融科技政策语境、同批本地财经媒体口径与相近的地方监管沟通渠道, 使得同省同侪银行的新闻正面度在给定年份呈现共同变动, 但该共同变动经排除自身构造后, 与目标银行自身特质冲击 (idiosyncratic shock) 理论上正交, 因此可承担外生工具的识别角色。该家族与情感 LLM 口径的孪生列 `prov_leave1out_tone_full/ctx/ss`、词典口径的孪生列 `prov_leave1out_dict_tone_full/ctx` 共同构成地理层面多测度 leave-one-out IV 矩阵, 其份额构造与排他性论证的方法学谱系可追溯至 Goldsmith-Pinkham, Sorkin & Swift (2020, American Economic Review) 对 shift-share/Bartik 型工具排他性来源的系统性讨论; 三套测度分别锚定 LLM 投票、语言学词典、BERT 分类器三条彼此独立的情感抽取管线, 在同一份地理聚合原语上并排产出, 用于对第一阶段情感内生变量做过度识别 (over-identification) 检验。产生端源码见 `pipeline\panel\geography.py` 的地理 leave-one-out 循环 (在 `bank_province`/`bank_city` 两个粒度上分别跑一遍, 本家族属省粒度), 面板导出层 `pipeline\panel\export.py` 承担列标签映射与 Stata 变量注释, 两文件构成本家族的双 producer 记录。

【方法学与计算】
计算原语是标准的 leave-one-out 组内均值: 先按 (bank_province, year) 分组, 对组内 BERT 正面篇占比列 (即面板层 `bert_avg_pos_{track}`, 上游来自 stage 23 三家 BERT 模型输出正面篇占比后在面板聚合层求均值的派生列) 求组内求和 `grp_sum` 与组内计数 `grp_cnt`, 随后对每个银行-年观测取 `(grp_sum − 自身值) / (grp_cnt − 1)`。此构造保证目标银行自身的贡献被严格剔除, 区别于普通同省均值 (后者会把自身值也计入分母分子, 引入机械正相关, 破坏 IV 排除性)。有效性判据为组内银行数 `grp_cnt > 1`——若某省某年只有该行一家银行上榜 (或该省样本量 < 5 提前 `continue` 跳过), 则该行该年的 leave-one-out 值记为缺失 (NaN), 而非误填 0 或组均值本身。产生端在完成全部地理列合并后, 会记录一段判读日志: 统计全部 leave-one-out 列的平均有效占比, 若均值 < 0.5 则显式提示"单一银行组多 → 弱工具风险", 提醒该列仅适宜作证伪/稳健性用途而非唯一识别策略——这一点在早期试跑 T=2 (2017-2018) 该面板上尤为突出, 省级分组天然稀疏, 实测有效占比常低于全量 T=19 生产面板的预期水平。产生端日志同时给出示例 Stata 命令 `ivreghdfe Y (llm_vote_tone_full = prov_leave1out_tone_full prov_leave1out_dict_tone_full prov_leave1out_bert_avg_pos_full), absorb(target_bank year) cluster(target_bank)` 搭配 `estat overid` 做 Hansen J 检验, 说明本列在实际用法上是作为多工具矩阵中的一支, 与词典口径、LLM 口径同时纳入同一超定 (over-identified) 回归。历史上曾发生列名压缩事故 (fix omni-g-panel-export-04, 2026-06-11): 原始 `prov_leave1out_dict_avg_tone_full` 因超出 Stata 32 字符变量名上限被单侧截断, 导致 `.dta` 内 full/ctx 两轨词干不对称, 后续已改为规范化词干 `prov_leave1out_dict_tone_full` 并同步 Stata 命令引用; 本家族 `bert_avg_pos` 词干本身在 32 字符上限内未受此问题波及, 但记录该修复史是理解相邻列命名规范的必要背景。

【文献定位】
本家族方法学谱系上承 Hassan et al. (2019, QJE) 关于企业层面文本测度构造与工具识别的一般性讨论——该文虽针对政治风险文本测度, 但其"从共同暴露中剥离出可作为工具的外生成分"的构造逻辑与本家族的地理留一平均高度同构。BERT 正面篇占比的上游测度方法论直接源自 Huang, Wang & Yang (2023, Contemporary Accounting Research) 提出的金融领域微调 BERT 分类器范式 (FinBERT), 本项目 stage 23 的三家 BERT 模型 (finbert_cn/fin_sent_zh/finbert2) 均沿此范式对中文财经文本做三分类情感判别, 正面篇占比即该分类器输出在文章层面聚合后的比例统计量。工具变量的构造哲学参照 Goldsmith-Pinkham, Sorkin & Swift (2020, American Economic Review) 对 Bartik/shift-share 型工具的系统性方法论综述, 该文强调工具的可信度取决于份额分配的外生性来源可追溯、可检验, 这与本家族"排除自身+地理分组"的显式可核验构造原则一致。地理层面情感共振的实证先例可见 Chen, Goldstein, Huang & Vashishtha (2022, JFE) 对银行透明度与存款流动的研究, 以及 Fang, Wang, Wang & Yuan (2024, IREF) 对中国银行媒体情感与系统性风险关系的实证, 二者均支持"同区域银行新闻情感存在可观测共同成分"这一构念前提, 为本家族地理留一工具的经济学合理性提供实证支撑。 晚近文献进一步在方法学与构念前提两个层面补强了这一构造。Frandsen、Leslie 与 McIntyre (2025) 提出并推导 cluster jackknife (按簇留出) 工具变量估计量, 证明在簇内含多工具与多固定效应的设定下按簇留出可消除标准 2SLS 的偏误, 其按簇留出的思路与本家族按 (bank_province, year) 分组、从组内均值中排除自身的构造同族; 该文为纯计量方法论文 (估计量推导 + 蒙特卡洛 + 一例美国司法/法官指派数据应用), 其留出单位是法官簇, 本家族的留出单位则是同组的单个银行且分组键为地理×年份, 本项目仅借其对留一构造的偏误校正逻辑作方法参照, 并未实施 cluster jackknife 估计。Ellis 与 Jaspersen (2024) 分析留一同侪均值工具在含固定效应模型中的行为, 指出组内留一均值与固定效应同时使用时估计量会出现机械性偏误, 构成本家族构造法的方法学警示文献; 该文为 SSRN 工作论文而非同行评审终稿, 讨论对象是一般线性面板的留一 IV 估计量, 未涉及本项目的 bank-year 层级、亦未涉及被聚合的 BERT 正面篇占比这一底层原子值, 更未讨论本项目 (省份,年份) / (城市,年份) / 经济圈 三种分组键与 min_group_size 守卫, 且本家族的留一列在部分设定中仅作同侪暴露控制变量而非工具, 故须按上述范围节制引用。Bobrov、Kamdar 与 Ulate (2025) 检验区域经济状况是否影响按地区指派的决策者的投票行为, 为“主体所属地理区域的状况会系统性影响其可观测行为”提供了顶刊层面的近期证据, 与前述银行透明度与媒体情感两条实证一同支撑本家族按省份分组构造同侪暴露的经济学前提; 该文主体为美联储地区联储主席、行为为货币政策投票, 与中国银行的媒体报道情感无直接对应, 其地理分组是既定的联储辖区而本项目需自建 (省份,年) 键, 且该文不做留一均值构造、也未把同组他成员的行为作为解释变量, 因此仅锚定“地理分组承载实质经济含义”这一前提, 不锚定 leave-one-out 算子本身。
【与相邻测度的构念区分】
本家族与同目录下 `prov_leave1out_tone_{full,ctx,ss}` (情感 LLM 口径)、`prov_leave1out_dict_tone_{full,ctx}` (语言学词典口径) 共享完全相同的地理留一构造原语, 唯一区别在于被聚合的底层情感测度来源不同——本家族聚合的是 stage 23 三家 BERT 分类器的正面篇占比, 而非 stage 21 三家 LLM 投票共识或 stage 22 词典打分。三条口径在方法学谱系上互不隶属、互为独立测量误差来源, 因此在计量上应各自作为 just-identified 工具并排使用、互为稳健性、不分主次——CLAUDE.md「当前状态铁律」明确要求禁止将 LLM/词典/BERT 三条情感测量管线各自产生的地理留一工具混入同一个 over-identified Hansen J 检验框架, 以免不同测量误差结构相互污染过度识别检验的解释力。本家族与"城市粒度"孪生族 `city_leave1out_bert_avg_pos_{full,ctx}` 的区别仅在于地理分组粒度 (省 vs 市), 后者分组更细、组内银行数更少、有效占比通常更低, 二者亦互为稳健性并排, 不应混同为同一识别策略下的替代工具。

## VAR: prov_leave1out_bert_avg_pos_ctx

【变体差分】
本列聚合的底层情感测度是三轨中的 ctx 轨——即 stage 14 物化的 `content_ctx` (标题 + 银行/金科实体窗口文本) 经 stage 23 三家 BERT 模型分类后聚合得到的 `bert_avg_pos_ctx` 面板列, 再按 (bank_province, year) 做排除自身留一平均。ctx 轨相较 full 轨的核心差异在于输入文本范围更窄, 仅保留实体附近的上下文窗口而非全文, 理论上降低无关段落噪声、但也可能丢失全篇语境线索; 当某篇文章不满足银行∧金科实体窗口条件时, `content_ctx` 按既定回退语义退化为全文, 对应 `ctx_is_fallback` 标记为真。本列在识别策略中与 `prov_leave1out_bert_avg_pos_full` 互为稳健性并排使用, 二者各自 just-identified, 不应同时纳入同一 over-identified Hansen J 检验; ctx 轨作为稳健性轨用于验证 full-only 留篇门控 (2026-06-29 起生效) 之外的条件性测度是否得出一致结论, 但样本行宇宙仍以 full 轨的 `llm_verified_full == True` 留篇集为准, ctx 轨列在该子集之外的行不作为独立留篇口径存在。就地理留一构造本身而言, ctx 轨的分组均值与 full 轨共用同一套 (bank_province, year) 分组键与同一份组内计数有效性判据 (组内银行数须大于 1 才输出非缺失值), 二者差异完全来自被聚合的底层 BERT 正面篇占比列本身的文本输入范围不同, 而非留一算法本身有别。实践上, 若某省某年多数银行的报道恰好触发 ctx 回退 (即绝大多数文章不满足实体窗口条件而退化为全文), 则该省年份组的 ctx 轨留一均值会在数值上高度贴近 full 轨对应值, 这属于回退语义下的预期一致性, 不代表两轨测度冗余, 因为二者仍是各自独立计算、各自可能在不同子样本上出现分歧的并排稳健性轨。

## VAR: prov_leave1out_bert_avg_pos_full

【变体差分】
本列是家族的 canonical 主轨, 聚合的底层情感测度是 full 轨——即 stage 23 三家 BERT 模型对 `content_full` (标题 + 全文正文) 分类后聚合得到的 `bert_avg_pos_full` 面板列, 按 (bank_province, year) 排除自身留一平均。留篇门控口径 (2026-06-29 起) 明确以 full 轨的 `llm_verified_full == True` 作为"是否判定为一篇银行金科报道"的唯一依据, 因此本列所依赖的分母 (同省同年有效 BERT 正面测度银行数) 与行宇宙均以 full 轨留篇集为基准, ctx/ss 两个孪生列则是在该行宇宙子集之上的条件性测度、并非独立留篇口径。在此类地理留一多工具 IV 回归框架中, `prov_leave1out_bert_avg_pos_full` 通常与 `prov_leave1out_tone_full`、`prov_leave1out_dict_tone_full` 并列进入同一超定回归的工具集合, 三者共同承担对 `llm_vote_tone_full` 等主处理变量的过度识别检验, 但按照 CLAUDE.md 铁律, 该"三工具同时进入一个 Hansen J"属于三条测量管线之间的合法并排 (不同 producer 各自独立测量), 与"同一测量管线的多轨/多梯子混入同一 Hansen J"这一被禁止的情形不同——判定标准是工具的独立测量误差来源, 而非表面上是否同属"地理留一"构造族。作为 canonical 主轨, 本列也是产生端判读日志重点关注的对象: 日志在完成全部地理留一列合并后, 会统计包括本列在内的全部 leave-one-out 列的平均有效占比, 若低于 0.5 则给出"单一银行组多 → 弱工具风险"的警示, 提示使用者本列 (以及同族其余轨) 在样本地理分布过度集中时仅适宜作为证伪或稳健性佐证, 不宜作为唯一识别策略的主工具; 该判读对早期试跑 T=2 面板尤为关键, 省级分组样本量有限使有效占比天然偏低, 生产 T=19 全量语料上因银行覆盖更广、省份组内样本更充分, 预期有效占比会显著提升。

## VAR: prov_leave1out_bert_avg_pos_ss

【变体差分】
本列聚合的底层情感测度是三轨中的 ss 轨——即 stage 14 物化的 `content_ss` (标题 + 银行∧金科同句 ±N 窗口文本, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 经 stage 23 三家 BERT 模型分类后聚合得到的 `bert_avg_pos_ss` 面板列, 再按 (bank_province, year) 做排除自身留一平均。ss 轨回退语义镜像 ctx 轨: 当某篇文章不存在银行与金科词的同句共现时, `content_ss` 退化为全文 body 且 `ss_is_fallback` 标记为真, 该回退分支与 ctx 轨共享同一份 `n_articles` 分母口径, 二者判定不对称——银行侧采用否定词过滤加短名过滤, 金科侧采用裸 Aho-Corasick 607 词表匹配, 与 stage 13 硬过滤阶段的共现判据 (±1 句窗口、标题+正文匹配) 是两个不同判据、不可混用。本列同样以 full 轨留篇集为行宇宙基准, 与 `prov_leave1out_bert_avg_pos_full`、`prov_leave1out_bert_avg_pos_ctx` 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 检验; 由于 ss 轨判据比 ctx 轨更严格 (要求同句而非同窗), 满足条件的文章占比通常更低, 该省年份组内的有效样本银行数亦相应更小, 在稀疏地理分组 (如开发面板早期试跑 T=2) 上留一有效占比可能进一步走低, 使用时应结合产生端判读日志给出的平均有效占比一并解读, 不宜孤立看待单一年份的取值。需特别注意 ss 轨判据 (银行与金科词严格同句共现, 原语 `extract_bank_fintech_cooccurrence`) 与 stage 13 共现硬过滤阶段所用的 ±1 句窗口判据 (原语 `has_bank_fintech_cooccurrence_within_radius`) 是两个刻意区分、禁止互相复用的判据: 前者用于决定文章是否进入本家族 ss 轨聚合口径, 后者用于决定文章是否在最上游就被硬过滤丢弃, 二者口径不一致属既定设计, 不应视为逻辑不一致或待修复的缺陷。本列与 `prov_leave1out_bert_avg_pos_full`、`prov_leave1out_bert_avg_pos_ctx` 三者在下游 IV 回归中若同时出现, 应各自作为独立的稳健性检验分别报告估计系数, 而非拼装进同一张过度识别表格内联合检验。

<!-- rendered-citations:begin -->
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A Large Language Model for Extracting Information from Financial Text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik Instruments: What, When, Why, and How. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Frandsen, B., Leslie, E., & McIntyre, S. (2025). Cluster Jackknife Instrumental Variables Estimation. Review of Economics and Statistics, 1-19. https://doi.org/10.1162/rest.a.263
Ellis, C., & Jaspersen, J. G. (2024). Fixed Effects and the "Leave-Out'' Instrument. SSRN Electronic Journal No. 4787799 [Working Paper]. https://doi.org/10.2139/ssrn.4787799
Bobrov, A., Kamdar, R., & Ulate, M. (2025). Regional Dissent: Do Local Economic Conditions Influence FOMC Votes? American Economic Review: Insights, 7(2), 268-284. https://doi.org/10.1257/aeri.20240184
<!-- rendered-citations:end -->
