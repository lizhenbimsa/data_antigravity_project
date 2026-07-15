---
family_id: F340
columns:
- indep_frac_cm
- indep_frac_cm_ss
unit: 比率/占比 (proportion, [0,1]; 分子分母同轨 article 计数比, 无量纲)
formula: 'indep_frac_cm = n_articles_indep_cm_ctx / n_articles_llm_valid_ctx (ctx 轨, n_articles_llm_valid_ctx>0 时取值否则 NaN); indep_frac_cm_ss = n_articles_indep_cm_ss / n_articles_llm_valid_ss (ss 轨, 分母同轨独立, 非共享 full 分母)'
producer: pipeline\panel\encode.py (_aggregate_ctx_diagonal + 对角线聚合块 L2035-L2079); pipeline\panel\codebook.py (L1235-L1271 条目登记表, generate_codebook 依 panel.columns 存在性优雅跳过)
upstream:
- "21_tone_llms (LLM 三维度分类之 collab_mode 维: indep/collab 二分类判定, 逐条 article-track)"
- 14_materialize_ctx (content_ctx / content_ss 文本物化, 上游三轨口径)
- 13_cooccurrence_filter (银行-金科硬过滤, 决定进入 LLM 判定的行宇宙)
citations:
- doi: 10.1093/qje/qjx045
  type: journal
  authors: Hansen, S., McMahon, M., & Prat, A.
  year: 2018
  title: 'Transparency and deliberation within the FOMC: a computational linguistics approach'
  venue: The Quarterly Journal of Economics
  vol: '133'
  issue: '2'
  pages_or_artno: 801-870
- doi: 10.1016/j.iref.2018.09.010
  type: journal
  authors: Xia, C., Zhang, X., Cao, C., & Xu, N.
  year: 2019
  title: 'Independent director connectedness in China: An examination of the trade credit financing hypothesis'
  venue: International Review of Economics & Finance
  vol: '63'
  pages_or_artno: 209-225
- doi: 10.1016/j.chieco.2025.102474
  type: journal
  authors: Zheng, Y.
  year: 2025
  title: "Ownership concentration and independent director effectiveness: Governance challenges under China's new company law"
  venue: China Economic Review
  vol: '93'
  pages_or_artno: Article 102474
new_dois: []
---

## CORE

【构念与来源】
本家族刻画银行-金科报道中"创新来源自主性"这一维度的占比测度, 属 P5 (Chesbrough 开放式创新框架) 主线的 collab_mode 分类分支。上游 21_tone_llms 阶段对每篇通过 stage 13 共现硬过滤、进入三轨情感/分类判定的银行-金科报道, 要求 LLM 对文中所述创新活动的组织方式作二分类判定: 自主研发 (Closed/independent, 银行依托内部研发团队独立完成金融科技创新, 不涉及外部合作方) 与外部协同 (Open/collaborative, 银行通过与金科公司、科技厂商、高校院所等外部主体合作、投资、联合实验室等方式获取或共建创新能力)。该二分类判定的理论基础是 Chesbrough (2003) 提出的开放式创新 (open innovation) 范式区分, 即企业既可以选择封闭式内部化研发路径, 也可以选择跨组织边界的协同创新路径, 两者在资源投入结构、知识产权归属、组织学习速度与外部性溢出等维度上存在系统性差异, 因而在实证上需要被区分度量而非合并处理。indep_frac_cm 与 indep_frac_cm_ss 是该二分类判定在银行-年面板层面的聚合占比, 分子取该银行-年内被判定为"自主研发"类的报道篇数, 分母取该银行-年内 LLM 分类判定成功 (verified) 的报道篇数, 二者严格同轨配对: ctx 轨分子配 ctx 轨分母, ss 轨分子配 ss 轨分母, 不存在轨间借用分母的情形。这一"同轨配对"设计源自 metric-audit (2026-06-02) 对早期版本"ctx 分子误配 full 分母导致 frac 越界 >1"问题的订正, 现为本家族及全部 _lc/_sc/_cm 系列对角线聚合列共用的强制守卫。

需要特别说明本家族与家族内 collab_frac_cm / collab_frac_cm_ss (外部协同占比, 未在本家族但属同一 collab_mode 分类下的镜像互补列) 之间的关系: indep_frac 与 collab_frac 理论上互补 (同一篇报道要么判为自主研发要么判为外部协同, 不可兼得), 但二者之和并不严格恒等于 1, 原因是 LLM 对 collab_mode 维度的判定存在部分失败 (NaN) 的情形——既不落入自主研发也不落入外部协同的报道仍计入分母的 n_articles_llm_valid 全集但不计入任一分子。encode.py 采用的恒等式校验已从早期严格版本 `n_articles == n_articles_indep + n_articles_collab` 弱化为逻辑必然性版本 `n_articles >= n_articles_indep + n_articles_collab` (fix omni-g-encode-07, 2026-06-11), 差额由 v3.5.0 D2 `n_articles_cell_NA_full` 兜底跟踪并另行披露, 该弱化避免了在 collab_mode 维度部分失败时触发面板级 assertion 崩溃, 但也意味着 indep_frac_cm 不能被解读为"自主研发占比 = 1 − 外部协同占比"的严格补数, 使用者在做描述统计或回归时应留意这一点。

【方法学与计算】
indep_frac_cm 属于 ctx 轨 (实体窗口文本, 标题+银行/金科实体邻近窗口), 是本家族的 canonical 列; indep_frac_cm_ss 属于 ss 轨 (标题+银行∧金科同句共现窗口, `config/filtering.yaml::context_window.ss_sentence_radius` 默认 ±1 句)。两轨与本家族之外仍存在的 full 轨 indep_frac (标题+全文正文) 共同构成三轨并排测度, 三轨在计算上完全独立: 各轨有各自的 LLM 分类判定输入文本 (content_full / content_ctx / content_ss, 均由 stage 14 ctx_materializer 物化, prepend_title 拼接), 各自的分类结果计数列 (n_articles_indep / n_articles_indep_cm_ctx / n_articles_indep_cm_ss), 各自的分母 (n_articles_llm_valid / n_articles_llm_valid_ctx / n_articles_llm_valid_ss)。按项目口径铁律, 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁将三轨混入同一 over-identified 的 Hansen J 检验中同时使用——这是因为三轨共享同一底层文章样本, 强行合并会人为制造工具冗余与内生相关, 破坏过度识别检验的统计前提。

ss 轨的回退语义镜像 ctx 轨: 当某篇报道中银行与金科关键词未出现在同一句 (无法满足严格同句共现窗口条件) 时, content_ss 退化为全文 body, 对应 ss_is_fallback 标记为 True, 此时该篇报道仍计入 n_articles (共享分母口径), 但其 collab_mode 判定文本实质上与 full 轨趋同, 在回退比例较高的样本中 ss 轨与 full 轨的相关性会相应上升, 这是设计内的优雅降级而非缺陷。此外, 项目整体已确立"留篇门控 = full-only" (2026-06-29): 一篇报道是否被认定为"有效的银行金科报道"这一准入判定只看 full 轨的 `llm_verified_full == True`, ctx/ss 两轨降格为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 轨留篇集合的子集; indep_frac_cm 与 indep_frac_cm_ss 的分母 n_articles_llm_valid_ctx / n_articles_llm_valid_ss 因此天然是 n_articles_llm_valid (full 轨分母) 的子集口径, 而非独立抽样的另一组文章, 使用者在跨轨比较占比水平时应注意样本基数已内生收缩。

分母为 0 (该银行-年在对应轨上无 LLM 分类成功的报道) 时两列均按 `np.where` 规则置 NaN, 而非 0, 以避免"无样本"与"样本存在但自主研发占比恰为 0"两种语义混淆; encode.py 亦为 n_articles_llm_valid_ctx/_ss 缺失整列的极端情形 (上游阶段未产出该轨分类列) 提供 else 分支, 整列置 NaN 并记录 WARNING 日志, 保证下游面板合并不因列缺失而中断。indep_frac_cm_ss 的落盘依赖上游 innovation_collab_mode_ss 分类列的存在性, generate_codebook 仅按 panel.columns 实际存在与否决定是否发射该条目, 缺列时优雅跳过而非报错, 这一模式与家族内其余 _ls/_ss 系列 (locus、substantiveness 维度的 ss 轨对角线) 完全一致。

【文献定位】
本家族分类判定的理论根基是 Chesbrough (2003) 的开放式创新框架, 该框架区分封闭式 (closed/proprietary) 与开放式 (open/collaborative) 两种创新组织模式, 是管理学与创新经济学文献中区分企业创新来源自主性的经典二元分类依据; Laursen & Salter (2006, SMJ) 进一步以"开放度" (openness) 的搜索广度/深度双维刻画企业外部知识获取行为, 为本家族"自主研发 vs. 外部协同"二分类在实证操作化上提供了先例, 即用离散的信息来源计数或占比来代理企业在创新组织维度上的位置, 而非依赖不可观测的内部研发投入数据。将该分类判定建立在文本挖掘而非问卷/专利数据基础之上, 方法论上借鉴了 Hansen, McMahon & Prat (2018, *Quarterly Journal of Economics*) 用计算语言学方法从会议文本中提取央行决策透明度与审议模式的做法——二者共同的方法论前提是: 组织行为的某些结构性特征 (审议模式、创新组织方式) 可以通过对相关文本的系统性、规则化分类来间接测度, 且该测度可在大样本、跨期面板上规模化复制, 优于依赖问卷或档案数据的传统方法。就"自主性"这一构念本身而言, 公司治理文献中关于独立董事 (independent director) 的研究提供了平行参照: Xia, Zhang, Cao & Xu (2019, *International Review of Economics & Finance*) 与 Zheng (2025, *China Economic Review*) 均在中国资本市场情境下考察治理主体的独立性/自主性如何影响企业行为与合同安排结果, 二者虽考察的是治理结构而非创新组织模式, 但共享"自主性程度可作为可观测占比变量嵌入面板回归"这一实证策略, 为本家族占比型测度在因果识别设计中的使用提供了同类文献支撑。

## VAR: indep_frac_cm

【变体差分】
本列是家族的 ctx 轨 canonical 列, 全称"自主研发占比 (ctx 轨)"。区别于同一 collab_mode 分类维度下的 full 轨 indep_frac (不在本家族, 分子分母均取 full 轨全文文本对应的计数列) 与 ss 轨 indep_frac_cm_ss (本家族第二列), indep_frac_cm 的分类判定输入文本是 content_ctx (标题+银行/金科实体邻近窗口, stage 14 物化, prepend_title 拼接), 分子取 n_articles_indep_cm_ctx (ctx 轨下被 LLM 判定为"自主研发"类的报道计数), 分母取 n_articles_llm_valid_ctx (ctx 轨下 LLM 分类判定成功的报道总数, 该分母是 full 轨留篇集合 n_articles_llm_valid 的子集口径, 因留篇门控已切换为 full-only)。当 n_articles_llm_valid_ctx 为 0 或该列本身缺失时, indep_frac_cm 置 NaN。该列命名中的 "_cm" 后缀标记其所属分类维度为 collab_mode (创新属性三维度之一, 另两维为 locus 底层技术/应用场景、substantiveness 实质性/象征性), 区别于同样带 ctx 标记但属于其他维度的 _lc (locus-ctx) 与 _sc (substantiveness-ctx) 系列列, 三者虽同为 ctx 轨对角线聚合产物, 但分类语义互不相关, 不可混用或相加。本列与家族外的 collab_frac_cm (外部协同占比, ctx 轨) 互补但不严格求和为 1 (差额为该轨 collab_mode 判定失败的报道占比, 由 n_articles_cell_NA 系列列另行披露), 亦与 tone_gap_indep_collab_cm_ctx (自主研发类报道与外部协同类报道之间的情感落差, 受 min-n≥5 双侧样本量守门) 共用同一上游对角线聚合结果但服务于不同分析目的, 前者是构成比例、后者是条件情感差异, 不应互相替代。

## VAR: indep_frac_cm_ss

【变体差分】
本列是家族第三轨 (ss 轨) 变体, 全称"自主研发占比 (ss 轨, 银行∧金科同句共现窗口)"。区别于 indep_frac_cm (ctx 轨, 实体邻近窗口) 与家族外 indep_frac (full 轨, 全文正文), 本列的分类判定输入文本是 content_ss——仅当银行关键词与金科关键词出现在同一自然句 (`config/filtering.yaml::context_window.ss_sentence_radius` 控制的窗口半径, 默认 ±1 句) 时才采用该同句片段, 否则回退为全文 body 并置 ss_is_fallback=True (回退语义镜像 ctx 轨的降级处理, 保证共享 n_articles 分母口径, 不因窗口条件不满足而丢弃样本)。本列的分母是 n_articles_llm_valid_ss, 该列由 encode.py 独立产出并使用, 与 ctx 轨分母 n_articles_llm_valid_ctx 是两个互不共享的独立计数列: 二者计算口径相同 (均取该轨 LLM 分类判定成功的报道计数) 但取值来源不同, 各自反映该轨自身的 LLM 分类成功率, 不存在跨轨借用或共享同一底层计数列的情形。indep_frac_cm_ss 的分子 n_articles_indep_cm_ss 来自 encode.py 对 innovation_collab_mode_ss 分类列的对角线聚合 (镜像 ctx 轨 _aggregate_ctx_diagonal 调用, 以 track='_ss' 参数区分), 若上游该 ss 轨分类列不存在, generate_codebook 依 panel.columns 存在性判断自动跳过本列的发射, 不产生占位空列。按三轨并排口径, indep_frac_cm_ss 与 indep_frac_cm 及 full 轨 indep_frac 三者互为稳健性测度、各自 just-identified、不分主次, 严禁混入同一 over-identified Hansen J 检验; 在实证解读上, 由于同句共现窗口比实体邻近窗口更严格, indep_frac_cm_ss 的回退比例通常高于 ctx 轨(对应窗口条件更难满足), 使用者在比较三轨系数差异时应结合各轨回退占比一并披露, 以避免将"窗口口径差异导致的样本构成差异"误读为"自主性构念本身在不同文本窗口下的实质差异"。

<!-- rendered-citations:begin -->
Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: a computational linguistics approach. The Quarterly Journal of Economics, 133(2), 801-870. https://doi.org/10.1093/qje/qjx045
Xia, C., Zhang, X., Cao, C., & Xu, N. (2019). Independent director connectedness in China: An examination of the trade credit financing hypothesis. International Review of Economics & Finance, 63, 209-225. https://doi.org/10.1016/j.iref.2018.09.010
Zheng, Y. (2025). Ownership concentration and independent director effectiveness: Governance challenges under China's new company law. China Economic Review, 93, Article 102474. https://doi.org/10.1016/j.chieco.2025.102474
<!-- rendered-citations:end -->
