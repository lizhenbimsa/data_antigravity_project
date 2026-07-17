---
family_id: F538
columns:
- sum_wd_mw_gpt54nano_ctx
- sum_wd_mw_gpt54nano_full
- sum_wd_mw_gpt54nano_ss
unit: 无量纲权重和 (media_authority_weight 均值归一化后逐篇权重之和, 非货币/非计数单位)
formula: 'sum_wd_mw_gpt54nano{track} = Σ_{i∈bank-year} media_authority_weight_i · 1{gpt54nano_score_i{track} 非缺失}, track∈{_full,_ctx,_ss}; 源自 runner._build_llm_valid_masked_weights(frame, mw_weight, "mw") 产出的篇章级列 _wd_mw_gpt54nano{track} 在 encode.py 聚合入口按 bank-year 分组 sum 得到'
producer: pipeline/panel/runner.py::_build_llm_valid_masked_weights (调用于步骤3c 媒体权威加权段, 约 runner.py:832) 产篇章级 _wd_mw_gpt54nano{track}; pipeline/panel/encode.py 步骤5 聚合入口 (约 encode.py:1203) 按 agg[f'sum_wd_mw_gpt54nano{track}'] = (f'_wd_mw_gpt54nano{track}', 'sum') 聚合为 bank-year 面板列; 消费方 encode.py:2242 用作 gpt54nano_tone_mw{track} 的匹配分母 (经 _llm_denom 兜底)
upstream:
- 21_tone_llms.parquet (gpt54nano_score_full/_ctx/_ss 三轨逐篇有效性掩码)
- media_authority_weight (媒体权威性加权源, encode.py 3c 段, 匹配 config/media_weights.json 均值归一化后的媒体权重)
citations:
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT outperforms crowd workers for text-annotation tasks
  venue: Proceedings of the National Academy of Sciences
  vol: '120'
  issue: '30'
  pages_or_artno: e2305016120
- doi: 10.1126/sciadv.adp1528
  type: journal
  authors: Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E.
  year: 2024
  title: Wisdom of the silicon crowd — LLM ensemble prediction capabilities rival human crowd accuracy
  venue: Science Advances
  vol: '10'
  issue: '45'
  pages_or_artno: eadp1528
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: The validity of sentiment analysis — comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms
  venue: Communication Methods and Measures
  vol: '15'
  issue: '2'
  pages_or_artno: 121-140
- doi: 10.1017/pan.2021.33
  type: journal
  authors: Ying, L., Montgomery, J. M., & Stewart, B. M.
  year: 2022
  title: Topics, concepts, and measurement — a crowdsourced procedure for validating topics as measures
  venue: Political Analysis
  vol: '30'
  issue: '4'
  pages_or_artno: 570-589
- doi: "10.1080/19312458.2024.2378690"
  type: "journal"
  authors: "Laurer, M., van Atteveldt, W., Casas, A., & Welbers, K."
  year: 2025
  title: "On Measurement Validity and Language Models: Increasing Validity and Decreasing Bias with Instructions"
  venue: "Communication Methods and Measures"
  vol: "19"
  issue: "1"
  pages_or_artno: "46-62"
new_dois: []
---

## CORE

【构念与来源】
F538 家族的三列 (sum_wd_mw_gpt54nano_full / _ctx / _ss) 不是情感测度本身, 而是一族"配套分母"辅助列: 它们承载的构念是"在媒体权威性加权 (MW) 口径下, gpt54nano 这一家 LLM 在某银行-某年份实际给出有效语调判断的报道所占的权重总和", 服务于 encode.py 里 `{short}_tone_mw{track}` (本族即 `gpt54nano_tone_mw{track}`) 的构造。项目情感测度体系采用三家 LLM 多数投票 (`gpt-5.4-nano`/gpt54nano、`gemini-3.1-flash-lite`/gemini31 两家走 yunwu、`deepseek-v4-flash`/deepseekv4 直连 api.deepseek.com) 互为跨厂商稳健性并排, 三家各自的 per-model 子测度是"co-equal 不分主次"的稳健性轨, 而非以投票共识为主、单模型为辅的层级关系。MW (Media-Authority-Weighted) 加权口径源自媒体权威性分级思想 (Holzman et al. 2023, TAR), 用报道所在媒体的权威性权重对篇章级语调加权聚合, 与等权 (EW)、发文量加权 (VW, mention_density)、跟风衰减加权 (HW, herd_weight) 并列为四套聚合权重方案之一; 四套权重各自反映不同的"哪些报道该被赋予更大发言权"假设, 互为稳健性并排, 不设主次。

【方法学与计算】
构造分两步。第一步在 pipeline/panel/runner.py 步骤3c (媒体权威加权段) 通过 `_build_llm_valid_masked_weights(frame, mw_weight, 'mw')` 在篇章级产出中间列 `_wd_mw_gpt54nano{track}`: 对每一轨 track ∈ {_full, _ctx, _ss}, 取该篇报道所属媒体的权威性权重 `media_authority_weight` (由媒体中文名精确/归一化匹配 `config/media_weights.json` 得原始权重, 再全样本均值归一化, 使权重均值 ≈1、std 反映权威性区分度), 再用 `.where(gpt54nano_score{track}.notna())` 做有效性掩码: 若 gpt54nano 在该轨对该篇报道给出了有效的语调判断 (score 非缺失), 该篇的媒体权威权重被保留; 若 gpt54nano 该轨判断缺失 (如 LLM 调用失败、留篇门控未通过等), 该篇权重被置为缺失, 不计入求和。第二步在 pipeline/panel/encode.py 步骤5聚合入口 (`agg[f'sum_wd_mw_gpt54nano{track}'] = (f'_wd_mw_gpt54nano{track}', 'sum')`) 按 bank-year 分组求和, pandas 的 groupby-sum 天然跳过 NaN, 于是聚合结果恰为"该 bank-year 内 gpt54nano 该轨给出有效判断的所有报道的媒体权威权重之和"。零新闻的 bank-year 单元事后由计数/和列零填契约统一填 0 (而非留 NaN), 与 `sum_mention_density` 等兄弟列的处理一致。这一构造存在的动因是一处已修复的分母失配缺陷: 若直接用"全部报道的物理媒体权重和"作 `gpt54nano_tone_mw{track}` 的分母, 分子 (Σ weight·score, 对无效行天然 NA-skip) 与分母 (Σ weight over all) 的统计域不一致——分子只数了 gpt54nano 有判断的报道, 分母却把没判断的报道也算了进去, 等价于把"gpt54nano 未给出判断"的报道隐式当作语调为 0, 使加权语调随 LLM 判断缺失比例的上升而系统性向 0 偏移。`sum_wd_mw_gpt54nano{track}` 正是为纠正这一偏差而设的"同域匹配分母": encode.py 消费端 `gpt54nano_tone_mw{track} = gpt54nano_score_mw_sum{track} / sum_wd_mw_gpt54nano{track}` (经 `_llm_denom` 函数按列存在性在 valid-mask 分母与物理分母间兜底选择, 缺 valid-mask 列时退回物理域分母以兼容旧 parquet), 分子分母同数"gpt54nano 该轨判断有效"的这批报道, 消除了向零衰减偏差。需要强调: 该修正专属 LLM 族 (`llm`/各 per-model short/`prob` 三类分组), 因其 score 结构性可能因模型调用失败等原因产生缺失; 词典族因 stage 13 硬过滤后存活行必含真实 token、空文本分支不可达, score 结构性无 NaN, 分子分母天然同域, 不建此类 valid-mask 分母列; BERT 族存在推理失败哨兵 NaN, 该修正对 BERT 族的对称补齐已列入 M0/golden 重生窗口的待办, 现行防线是观测闸监控失败率是否为 0, 本族三列与 BERT 族无关。
三轨语义遵循项目统一口径: full=标题+正文全文, ctx=标题+银行/金科实体窗口, ss=标题+银行∧金科同句 (或窗口±N) 共现片段, 三者在 stage 14 `ctx_materializer` 统一物化; ss 轨若某篇报道不存在银行∧金科同句共现, 按镜像 ctx 的回退语义退化为使用全文正文 (`content_ss`=全文 body, `ss_is_fallback`=True), 该回退不影响本族分母构造本身——分母只关心 gpt54nano 在该轨的 score 是否非缺失, 与该轨文本是否走了回退通道是两个独立判据。三轨各自 just-identified 并排、互为稳健性、不分主次, 项目铁律要求三轨结果禁止混入同一个 over-identified 的 Hansen J 过度识别检验中联合估计; 留篇门控口径 (是否判定为"一篇银行金科报道") 自 2026-06-29 起统一为 full-only, 即仅由 `llm_verified_full` 决定, ctx/ss 两轨降为 full 留篇集合之上的 conditional-on-full 测度/稳健性轨, 本族 ctx/ss 两列的行宇宙同样是该 full 留篇子集, 而非独立留篇标准下的报道全集。

【文献定位】
本族三列服务的多 LLM 多数投票 + 跨厂商稳健性设计, 方法学根基是"用多个独立评分者的判断汇聚以逼近真值"这一测量学传统在 LLM 时代的延伸。Gilardi, Alizadeh & Kubli (2023, PNAS) 证明 ChatGPT 类模型在文本标注任务上准确率可超越众包工人, 为用 LLM 替代/补充人工标注建立了实证基础; Schoenegger et al. (2024, Science Advances) 进一步论证多个 LLM 组成的"硅基群体"预测能力可比拟人类群体智慧, 为本项目采用三家异构 LLM (而非单家) 投票聚合提供了方法学支撑——多家模型各自独立打分、再加权/投票聚合的思路正是"群体智慧"范式在情感分类任务上的具体落地。van Atteveldt, van der Velden & Boukes (2021, Communication Methods and Measures) 系统比较了人工标注、众包编码、词典法与机器学习算法在情感分析效度上的差异, 说明不同测量路径 (对应本项目的 LLM/词典/BERT 三法并排) 各有效度剖面, 支持项目"多法互为稳健性、不设单一权威测度"的整体设计哲学。Ying, Montgomery & Stewart (2022, Political Analysis) 探讨了众包验证程序在概念测量中的应用, 呼应本族分母构造中"有效性掩码"这一核心动作的方法学关切: 当某个评分来源 (无论是人类标注者还是本项目情境下的某家 LLM) 对特定样本未能给出判断时, 聚合统计量的构造必须显式处理这种缺失, 否则会引入系统性偏差, 这正是 `sum_wd_mw_gpt54nano{track}` 存在的方法学正当性所在。 晚近测量方法学文献进一步夯实了本族掩码的效度前提。Laurer、Casas 与 Welbers (2025) 以对照实验系统检验语言模型作为测量工具的效度, 证明指令/提示设计会实质改变效度与偏误; 本族三列以 gpt54nano 在该轨是否给出有效判断界定分母求和域, 该掩码本身即模型效度的函数, 故该文锚定的正是本族 (以及 mw/vw/hw 各权重口径下全部 per-model 分母姊妹族) 赖以成立的效度前提。迁移边界须诚实标明: 原文对象为英文传播学文本分类任务与开源指令微调模型, 本项目则是中文新闻加三家商用 API 模型; 原文结论支持"加指令可提效度", 而本项目情感提示词 v8 已字节冻结、嵌入侧刻意零 instruct 前缀, 二者设计取向不同, 不可直接迁移; 原文亦不涉及任何权重加权分母口径, 更未处理银行-年面板层的聚合。
## VAR: sum_wd_mw_gpt54nano_full

【变体差分】
本列是 full 轨 (标题+正文全文) 上的 MW valid-mask 分母, 分组条件为 `gpt54nano_score_full` 非缺失。full 轨是项目留篇门控的口径来源: `llm_verified_full == True` 决定某篇报道是否被认定为"一篇银行金科报道", 因此本列所对应的分母行宇宙即为该门控下的留篇集合本身 (而非 ctx/ss 轨在留篇集合之上的条件子集)。在三家 LLM 投票机制下, gpt54nano 是否在 full 轨对某篇报道给出有效判断, 取决于该篇是否通过留篇门控且 gpt54nano 单模型调用未失败; 与 gemini31_score_full、deepseekv4_score_full 各自的有效性彼此独立, 三家各自构造并排的 `sum_wd_mw_{model}_full` 分母列, 不共享同一掩码, 互为跨厂商稳健性、不分主次。本列与 `gpt54nano_score_mw_sum_full` 搭配构成 `gpt54nano_tone_mw_full` 的分子分母对, 是该篇章-模型-权重组合在 full 轨上"媒体权威加权语调"的核心配套统计量。就读数直觉而言, 本列数值越大, 说明该银行-年份内 gpt54nano 成功给出有效判断且报道又集中在权威性权重较高媒体的篇幅越多; 若某 bank-year 恰好零新闻或 gpt54nano 在该单元全部判断缺失, 本列依"计数/和"列零填契约填 0 而非留 NaN, 与 `sum_mention_density`、其余 `sum_wd_*` 兄弟列口径一致, 消费端 `_llm_denom` 遇 0 会经 `replace(0, np.nan)` 兜底防止除零。作为 full 轨专属的辅助分母, 本列不直接进入任何回归设定的解释变量或结果变量, 其唯一角色是撑起 `gpt54nano_tone_mw_full` 这一 per-model MW 稳健性测度的分母正确性; 与该测度并列的还有等权、VW (发文量加权)、HW (跟风衰减加权) 三套权重下 gpt54nano 各自的匹配分母, 四套权重口径彼此正交、互为稳健性、不设权重上的主次。

## VAR: sum_wd_mw_gpt54nano_ctx

【变体差分】
本列是 ctx 轨 (标题+银行/金科实体窗口) 上的 MW valid-mask 分母, 分组条件为 `gpt54nano_score_ctx` 非缺失。ctx 轨自 full-only 留篇门控切换后属 conditional-on-full 的稳健性/robustness 测度轨, 其行宇宙是 full 轨留篇集合的子集, 本列继承这一行宇宙约束——若某篇报道未通过 full 轨留篇门控, 即便其 ctx 轨文本本身存在, 该篇也不进入本列的求和范围。在此子集内, gpt54nano 是否在 ctx 轨给出有效判断仍由该模型对 ctx 窗口文本的独立调用结果决定, 与 full/ss 两轨的有效性各自独立判定, 三轨分母各自 just-identified、互为稳健性并排, 禁止混入同一 over-identified Hansen J 联合估计。本列服务于 `gpt54nano_tone_mw_ctx` 的构造, 用于检验 gpt54nano 情感测度是否对"截取到实体窗口附近文本"这一文本口径变化保持稳健。与 full 轨同名分母相比, 本列的求和范围通常不大于 full 轨对应值——凡进入本列求和的报道必先满足 full 轨留篇门控, 再叠加 ctx 轨自身 gpt54nano 判断非缺失这一条件, 两层筛选是先后关系而非并列关系。数值上若本列显著小于 full 轨同 bank-year 单元的值, 说明相当一部分在 full 轨判断有效的报道在 ctx 轨未能得到 gpt54nano 的有效判断 (例如实体窗口截取后文本过短、上下文信息不足以支撑模型给出判断), 这本身即是三轨稳健性比较的一项诊断信号, 而非数据缺陷。本列同样遵循计数/和列零填契约, 零新闻或该轨判断全缺失的 bank-year 单元填 0。

## VAR: sum_wd_mw_gpt54nano_ss

【变体差分】
本列是 ss 轨 (标题+银行∧金科同句/近邻窗口共现片段) 上的 MW valid-mask 分母, 分组条件为 `gpt54nano_score_ss` 非缺失。ss 轨语义镜像 ctx 轨: 若某篇报道不存在银行与金科词汇的同句 (或按 `context_window.ss_sentence_radius` 配置的窗口半径内) 共现, 该篇的 `content_ss` 按回退语义退化为使用全文正文, 并以 `ss_is_fallback=True` 标记, 但这一回退发生在文本物化阶段 (stage 14), 与本列所依赖的"gpt54nano 在 ss 轨的 score 是否非缺失"这一判据相互独立——回退只改变喂给 gpt54nano 的输入文本内容, 不直接决定该轨判断是否有效。与 ctx 轨一致, ss 轨同样是 full 留篇门控之上的条件子集, 本列继承该行宇宙约束。ss 轨相对 ctx 轨的差异在于聚焦更严格的"同句共现"证据窗口, 用于检验 gpt54nano 情感判断是否依赖更宽的上下文信息还是仅凭银行与金科词汇紧邻共现的局部文本即可稳定给出。ss/ctx/full 三轨分母各自并排、互为稳健性、不分主次, 三者禁止混入同一 over-identified Hansen J 检验。本列服务于 `gpt54nano_tone_mw_ss` 的构造, 与 ctx 轨类似, 其求和范围继承 full 轨留篇门控子集, 再叠加 ss 轨 gpt54nano 判断非缺失这一条件。由于 ss 轨在无同句共现时回退为全文正文, 实际喂给 gpt54nano 的输入文本在"真同句片段"与"回退全文"两种情形下差异很大, 但本列本身不区分这两种情形——只要 gpt54nano 在该轨给出了非缺失判断 (无论输入是真片段还是回退全文), 该篇的媒体权威权重即计入本列。若需要单独考察回退子样本对分母的贡献, 须结合 `ss_is_fallback` 标记在篇章级另行切分, 本列的 bank-year 汇总值本身不携带这一区分信息。同样遵循计数/和列零填契约, 零新闻或该轨判断全缺失时填 0, 消费端除法经 `_llm_denom` 的零值兜底防护。

<!-- rendered-citations:begin -->
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd — LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), eadp1528. https://doi.org/10.1126/sciadv.adp1528
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis — comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Ying, L., Montgomery, J. M., & Stewart, B. M. (2022). Topics, concepts, and measurement — a crowdsourced procedure for validating topics as measures. Political Analysis, 30(4), 570-589. https://doi.org/10.1017/pan.2021.33
Laurer, M., van Atteveldt, W., Casas, A., & Welbers, K. (2025). On Measurement Validity and Language Models: Increasing Validity and Decreasing Bias with Instructions. Communication Methods and Measures, 19(1), 46-62. https://doi.org/10.1080/19312458.2024.2378690
<!-- rendered-citations:end -->
