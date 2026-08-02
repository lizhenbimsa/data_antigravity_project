---
family_id: F170
columns:
- deepseekv4_cont_mw_sum_ctx
- deepseekv4_cont_mw_sum_full
- deepseekv4_cont_mw_sum_ss
- gemini31_cont_mw_sum_ctx
- gemini31_cont_mw_sum_full
- gemini31_cont_mw_sum_ss
- gpt54nano_cont_mw_sum_ctx
- gpt54nano_cont_mw_sum_full
- gpt54nano_cont_mw_sum_ss
unit: 媒体权威性加权连续语调的银行-年累加和 (无量纲, 未归一化分子)
formula: "{short}_cont_mw_sum{track} = Σ_{a∈bank-year} [ score_a × confidence_a × media_authority_weight_a ]; 其中 score_a∈{-1,0,+1} 为单模型该轨判定映射, confidence_a 为该模型自报置信度, {short}∈{gpt54nano, gemini31, deepseekv4}, {track}∈{_full,_ctx,_ss}; 本列是未归一化的连续语调分子, 当前面板不为其物化对应的 per-model 归一化输出列 (仅共识轨 llm_vote_cont_mw{track} 被归一化; per-model 归一化只存在于离散 score 分支 {short}_tone_mw{track} = {short}_score_mw_sum{track} / sum_wd_mw_{short}{track}, 分子取离散 sibling 列而非本连续列, 分母取 per-model verified 掩码媒体权威权重和 sum_wd_mw_{short}{track}, 缺列时回退物理和 sum_media_authority_weight{track})"
producer: "news_process/pipeline/panel/runner.py (步骤 3c: 逐模型 _cont × media_authority_weight → _cont_mw) ; news_process/pipeline/panel/encode.py::_build_panel_aggregations (groupby sum → _cont_mw_sum) ; news_process/pipeline/sentiment/tone_llms.py (stage 21 三家 LLM 逐条判定与置信度源)"
upstream:
- 21_tone_llms.parquet (三家 LLM 逐轨 sentiment/confidence/verified)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss)
- runner 步骤 3c media_authority_weight (Holzman-式媒体权威权重)
citations:
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.1287/mnsc.2024.05417
  type: journal
  authors: Siano, F.
  year: 2025
  title: "The news in earnings announcement disclosures: Capturing word context using LLM methods"
  venue: Management Science
  vol: 71
  issue: 11
  pages_or_artno: 9831-9855
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: "Majority rules: LLM ensemble is a winning approach for content categorization"
  venue: arXiv
- doi: 10.48550/arXiv.2502.18036
  type: arxiv
  authors: Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., ... Yu, P. S.
  year: 2025
  title: "Harnessing multiple large language models: A survey on LLM ensemble"
  venue: arXiv
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: arXiv
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是单一大语言模型 (LLM) 在银行-年层面的、经媒体权威性加权的连续语调累加和, 即最终归一化情感度量的未除权分子。列名骨架为 {short}_cont_mw_sum{track}, 其中模型短名 {short} 取 gpt54nano (对应 GPT-5.4-nano)、gemini31 (对应 Gemini-3.1-flash-lite) 与 deepseekv4 (对应 DeepSeek-V4-flash, 直连 api.deepseek.com, 非早期误标的 xAI Grok), 文本轨 {track} 取 full、ctx、ss 三条。九列即三家模型与三条文本轨的笛卡尔积。此处 cont 指连续型语调 (continuous), 与离散型 score 相区别: 前者在离散极性标签之上再乘以模型自报的置信度, 使得同为"负面"的两篇报道能按模型对自身判断的确定程度分出强弱; mw 指媒体权威性加权 (media-authority weighted), 即每篇报道的连续语调再乘以该报道所属媒体来源的权威性权重, 让权威大报的语调在银行-年汇总中获得更高话语权; sum 指该银行-年内所有留篇报道上述加权连续语调的算术累加, 是一个尚未除以权重总和的分子, 而非可直接横向比较的均值。构念的数据来源是阶段 21 (tone_llms) 三家 LLM 对每篇报道逐条、逐轨的独立判定: 每条新闻在同一思维链 Prompt 内一次性返回真伪精筛与情感极性, 模型另给出自报置信度; 三家模型并发请求、各自独立留痕, 既服务于下游多数投票共识, 也在本家族里作为逐模型 (per-model) 的跨厂商稳健性并排轨保留下来。媒体权威性权重则由银行-年面板构建阶段 (runner 步骤 3c) 依据媒体来源属性计算, 呼应媒体报道的显著性与传播力在资本市场定价中的非对称作用这一实证传统, Fang 与 Peress (2009) 以及 Tetlock (2007) 均记录了媒体覆盖的显著性与语调对股票横截面与投资者情绪的实质影响, 为按媒体权威加权提供了理论依据。

【方法学与计算】
计算链路分三级严格上溯。第一级在阶段 21 与编码环节 (encode) 逐模型物化文章级连续语调: 单模型的离散极性 {short}_score 由该模型返回的情感标签经 SENTIMENT_MAP 映射到 {-1, 0, +1}, 且当该模型自身对该篇的 verified 为假时把自身 score 置为缺失 (per-model 独立降级, 不牵连他模型); 随后 {short}_cont = {short}_score × 该模型自报置信度, 落入 [-1, +1], 缺失沿 NaN 语义自然传播。第二级在 runner 步骤 3c 施加媒体权威性权重: {short}_cont_mw = {short}_cont × media_authority_weight, 权重缺失时回退为 1.0。第三级在面板聚合把文章级 {short}_cont_mw 按银行-年 groupby 求和, 得到本家族的 {short}_cont_mw_sum。本列是分子, 且须辨明一个易错点: 当前面板并不为本连续列物化一条 per-model 归一化输出。真正被物化的 per-model 归一化度量 {short}_tone_mw{track} 取自离散的 sibling 列 {short}_score_mw_sum{track} 而非本连续列, 即 {short}_tone_mw{track} = {short}_score_mw_sum{track} ÷ sum_wd_mw_{short}{track}, 其分母是仅计入该模型成功打分 (verified) 文章权重的 per-model 掩码媒体权威权重和 sum_wd_mw_{short}{track} (该掩码列缺失时才回退物理和 sum_media_authority_weight{track}, 权重和为 0 时置 NaN 防除零); 之所以对 LLM 族用掩码分母, 是因为单模型打分失败行的 score 为缺失, 分子只累加成功行, 分母若用全物理权重和会系统性把语调压向 0。连续型的归一化目前只在三家共识轨上物化为 llm_vote_cont_mw{track} = llm_vote_cont_mw_sum{track} ÷ sum_wd_mw_llm{track}, per-model 连续轨则止于本累加分子。因此在 Stata 侧本家族一般不直接进回归, 而是作为可复算的中间存档量: 若研究者需要 per-model 连续归一化语调, 可镜像共识轨做法, 以本列除以同模型同轨的掩码权重和 sum_wd_mw_{short}{track} (缺列回退 sum_media_authority_weight{track}) 复算; 本列的首要用途是供审计逐轨追溯加权语调分子与其配套分母是否成对生成, 并支撑替代归一化方案。留篇门控遵循 2026-06-29 起的 full-only 口径: 一篇报道是否被判为"一篇银行金科报道"只看 llm_verified_full, 因此三轨共享同一 full 留篇集所定义的行宇宙, ctx 与 ss 轨是 conditional-on-full 的子集测度, 各 per-track 列在该子集上照常逐轨计算; ss 轨在无银行与金科同句共现时镜像 ctx 回退到全文正文并置 ss_is_fallback 为真, 缺 content_ss 列时优雅回退 content_full。确定性由 Prompt v8 字节级冻结与 temperature=0 推理锚定, 缓存命中即可离线零字节复现, 这一"提示冻结加缓存"的可复现范式与 de Kok (2025) 对生成式 LLM 用于会计研究的操作规范一致。⚠ 铁律: 三条文本轨 full、ctx、ss 各自 just-identified 并排, 三家模型 gpt54nano、gemini31、deepseekv4 互为稳健性、不分主次, 二者均严禁把不同轨或不同模型混进同一 over-identified 的 Hansen J 过度识别检验; 每条轨、每家模型各自单独进入 just-identified 设定并排比较, 逐模型子测度是跨厂商三角验证的稳健性轨而非可加合并的分量。

【文献定位】
本家族坐落在"以 LLM 做金融文本情感标注、并以多模型三角验证换取可信度"的方法学脉络上。Gilardi、Alizadeh 与 Kubli (2023) 在顶刊系统证据中显示 ChatGPT 在文本标注任务上可超过众包工人, 为以 LLM 替代人工情感编码提供了效度基础; Siano (2025) 与 Frankel、Jennings 与 Lee (2022) 分别论证了 LLM 方法与机器学习方法在捕捉词语语境、超越纯词典法上的增量, 支持本项目在词典与 BERT 之外并置 LLM 连续语调轨; Huang、Wang 与 Yang (2023) 的 FinBERT 是金融文本大模型抽取的经典参照, 界定了本家族与 BERT 族在测度构念上的分工。多模型共识与集成的合理性由 Kamen 与 Kamen (2025) 的多数投票集成实证, 以及 Chen 等 (2025) 的 LLM 集成综述共同支撑, 二者均说明并排保留逐模型子测度、再在上层以多数投票聚合, 相较任一单模型能降低方差与系统性偏误, 是有充分方法学根据的稳健设计, 也正当化了本家族在共识轨之外额外留存三家逐模型子测度作跨厂商三角验证的做法。Carlson 与 Burbano (2026) 与 Ludwig、Mullainathan 与 Rambachan (2025) 则从管理学标注规范与应用计量框架两侧, 提示以 LLM 标注变量入回归时须防范测量误差与提示敏感性, 这正是本家族保留未归一化分子以便审计、并坚持三轨三模型各自 just-identified 并排的动机所在。

## VAR: deepseekv4_cont_mw_sum_ctx

【变体差分】
本列是 DeepSeek-V4-flash 模型在 ctx (上下文片段) 轨上的媒体权威性加权连续语调银行-年累加和。模型维度上, 它取自直连 api.deepseek.com 的第三家 LLM, 与走 OpenLux 网关的 gpt54nano、gemini31 属不同厂商、不同 API 源, 三家在本家族里互为稳健性、不分主次; 该列的 verified 门控与 score 置缺失均以 DeepSeek 自身对该篇的判定为准, 其缺席只掉自身族列而不牵连另两家 (per-model 独立降级)。文本轨维度上, ctx 轨的输入是 content_ctx, 即标题 prepend 后再取含目标银行别名命中句前后各配置窗口 (context_window.sentence_radius, 默认 1 句) 扩展合并的实体邻近片段, 短文本退化为字符级窗口; 它相对 full 轨聚焦于银行实体周边语境, 削弱与银行无关的段落噪声, 使模型判定更集中于目标银行周边的实体邻近语境。作为分子须澄清一处易错口径: 面板并不为本连续列物化对应的 per-model 归一化输出, 已物化的 deepseekv4_tone_mw_ctx 取自离散的 sibling 列 deepseekv4_score_mw_sum_ctx, 即 deepseekv4_score_mw_sum_ctx ÷ sum_wd_mw_deepseekv4_ctx (分母是仅计入 DeepSeek verified 篇权重的掩码媒体权威权重和, 缺该掩码列时才回退物理和 sum_media_authority_weight_ctx), 与本连续列无关。本连续列止于未归一化分子, 若需 per-model 连续归一化, 可镜像共识轨 llm_vote_cont_mw 做法以本列除以同模型同轨掩码权重和 sum_wd_mw_deepseekv4_ctx (缺列回退 sum_media_authority_weight_ctx) 复算。留篇门控仍是 full-only: 行宇宙由 llm_verified_full 定义, ctx 轨在该 full 留篇子集上按 conditional-on-full 口径逐轨计算, 因此本列度量的是"已被判定为银行金科报道的样本中, DeepSeek 在实体邻近语境下所感知的、经媒体权威加权的连续语调总量"。作为未归一化分子, 本列在实证中主要供审计核对权重分子与分母是否逐轨配对, 以及支撑替代归一化方案, 一般不单独直接进入主回归。⚠ 铁律: 本列与同家族的 full、ss 两轨, 以及 gpt54nano、gemini31 两家模型的对应列, 各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: deepseekv4_cont_mw_sum_full

【变体差分】
本列是 DeepSeek-V4-flash 模型在 full (全文) 轨上的媒体权威性加权连续语调银行-年累加和, 是三条轨中的 canonical 留篇轨。文本轨维度上, full 轨输入为 content_full, 即标题 prepend 后拼接的整篇正文, 覆盖信息最完整、样本噪声也最高, 是留篇门控的判定基准: 一篇报道是否算作银行金科报道, 完全取决于 llm_verified_full 是否为真, 因而 full 轨既定义行宇宙又充当自身的一条度量轨。模型维度上, 本列取 DeepSeek 单家、直连 api.deepseek.com 的第三方判定, 与另两家跨厂商并排作三角验证; DeepSeek 自身 verified 为假时其 score 置缺失, 独立降级不连坐。计算上, 每篇 full 轨连续语调 = DeepSeek 离散极性 × 自报置信度, 再乘媒体权威性权重, 银行-年求和即得本列; 须澄清面板不为本连续列物化 per-model 归一化输出, 已物化的 deepseekv4_tone_mw_full 取自离散 sibling 列 deepseekv4_score_mw_sum_full ÷ sum_wd_mw_deepseekv4_full (分母为仅计 DeepSeek verified 篇权重的掩码和, 缺列回退物理和 sum_media_authority_weight_full), 而非本连续列; 本列若要连续归一化须镜像共识轨以本列除以同轨掩码权重和 sum_wd_mw_deepseekv4_full 复算。相对 ctx 与 ss 两条稳健性轨, full 轨语义最宽、构念最贴近"整篇报道对该银行金科议题的总体语调倾向", 在与另两家模型的 full 轨列并排时构成逐模型跨厂商稳健性比较的主锚。值得强调的是, full 轨信息最全也意味着最易吸纳与银行金科议题无关的段落, 因此本列的语调总量在解释上偏"整篇总体印象", 需与 ctx、ss 两条更聚焦的稳健性轨对照阅读, 三轨读数一致方能说明结论不被单一取文范围驱动。⚠ 铁律: full、ctx、ss 三轨与三家模型各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J。本列为未归一化分子, 供审计追溯与替代归一化, 一般不直接单独入主回归。

## VAR: deepseekv4_cont_mw_sum_ss

【变体差分】
本列是 DeepSeek-V4-flash 模型在 ss (银行与金科同句共现) 轨上的媒体权威性加权连续语调银行-年累加和。文本轨维度上, ss 轨输入为 content_ss, 即标题 prepend 后仅保留同一句内同时出现目标银行别名与金科词的句子并按窗口扩展的最严片段, 判据比 ctx 更紧, 用以隔离出银行与金融科技真正被并置讨论的语境; 其回退语义镜像 ctx: 当整篇无银行与金科同句共现时, content_ss 回退全文正文并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母口径, 缺 content_ss 列时进一步优雅回退 content_full。模型维度上, 本列仍取 DeepSeek 单家判定, 与 gpt54nano、gemini31 跨厂商并排互为稳健性, DeepSeek 自身 verified 为假仅掉自身族列。作为分子须澄清: 面板不为本连续列物化 per-model 归一化输出, 已物化的 deepseekv4_tone_mw_ss 取自离散 sibling 列 deepseekv4_score_mw_sum_ss ÷ sum_wd_mw_deepseekv4_ss (分母为仅计 DeepSeek verified 篇权重的掩码媒体权威权重和, 缺列回退物理和 sum_media_authority_weight_ss), 而非本连续列; 本连续列若要归一化须镜像共识轨以本列除以同轨掩码权重和 sum_wd_mw_deepseekv4_ss 复算。留篇门控仍是 full-only, ss 轨是 conditional-on-full 的最严子集测度: 在 full 留篇集内, 度量 DeepSeek 于"银行与金科同句共现"这一最贴近研究构念的语境下、经媒体权威加权感知到的连续语调总量。因判据最严, 早期试跑 T=2 小样本上该轨可能出现较多回退与零方差退化, 属预期行为, 生产期长面板恢复正常。由于回退行会把全文正文重新纳入, 解释本列时须结合 ss_is_fallback 的占比判断该轨在多大程度上真正体现了同句共现语境, 而非退化为 ctx 的近似。⚠ 铁律: ss 与 full、ctx 两轨及三家模型各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: gemini31_cont_mw_sum_ctx

【变体差分】
本列是 Gemini-3.1-flash-lite 模型在 ctx (上下文片段) 轨上的媒体权威性加权连续语调银行-年累加和。模型维度上, 它取自经 OpenLux 网关调用的 Gemini-3.1-flash-lite, 与同走 OpenLux 的 gpt54nano 及直连的 deepseekv4 并排, 三家跨厂商互为稳健性、不分主次; 本列的极性与置信度均来自 Gemini 对该篇该轨的独立判定, 其 verified 为假时仅本模型族列置缺失, 独立降级不连坐另两家。文本轨维度上, ctx 轨输入 content_ctx 聚焦目标银行别名命中句前后各默认 1 句的实体邻近窗口, 相对 full 轨压缩无关噪声、相对 ss 轨放宽共现约束, 处于三轨严苛度的中间档。计算路径与家族一致: 每篇 ctx 连续语调 = Gemini 离散极性 × 自报置信度, 乘媒体权威性权重后银行-年求和即得本列。须澄清: 面板不为本连续列物化 per-model 归一化输出, 已物化的 gemini31_tone_mw_ctx 取自离散 sibling 列 gemini31_score_mw_sum_ctx ÷ sum_wd_mw_gemini31_ctx (分母为仅计 Gemini verified 篇权重的掩码媒体权威权重和, 缺列回退物理和 sum_media_authority_weight_ctx), 而非本连续列。留篇门控为 full-only, 本列在 full 留篇子集上按 conditional-on-full 逐轨计算, 度量的是"已判为银行金科报道的样本中, Gemini 在实体邻近语境下经媒体权威加权感知的连续语调总量"。与 deepseekv4、gpt54nano 的同轨列并排, 可检验主结论是否随 LLM 厂商更换而稳健。作为未归一化分子, 本列一般不单列入主回归, 而是供审计核对权重分子与分母是否逐轨配对; 若需 per-model 连续归一化, 须镜像共识轨以本列除以同轨掩码权重和 sum_wd_mw_gemini31_ctx 复算, 而不能误认本列本身即某归一化度量的分子。⚠ 铁律: 本列与 full、ss 两轨及另两家模型各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: gemini31_cont_mw_sum_full

【变体差分】
本列是 Gemini-3.1-flash-lite 模型在 full (全文) 轨上的媒体权威性加权连续语调银行-年累加和, 为该模型三轨中的 canonical 留篇轨。文本轨维度上, full 轨输入 content_full 为标题 prepend 后的整篇正文, 信息最全、噪声也最高, 并且是全项目留篇门控的判定基准 (llm_verified_full); 尽管门控由 full 轨定义, 本列本身仍是 Gemini 单家在 full 轨上的一条独立度量轨。模型维度上, 本列取经 OpenLux 调用的 Gemini-3.1-flash-lite 单家判定, 与 gpt54nano、deepseekv4 跨厂商并排三角验证; Gemini 自身 verified 为假时其 score 置缺失, per-model 独立降级。计算上, 每篇 full 连续语调 = Gemini 离散极性 × 自报置信度, 乘媒体权威性权重, 银行-年求和得本列。须澄清面板不为本连续列物化 per-model 归一化输出, 已物化的 gemini31_tone_mw_full 取自离散 sibling 列 gemini31_score_mw_sum_full ÷ sum_wd_mw_gemini31_full (分母为仅计 Gemini verified 篇权重的掩码和, 缺列回退物理和 sum_media_authority_weight_full), 而非本连续列; 本列若要连续归一化须镜像共识轨以本列除以同轨掩码权重和 sum_wd_mw_gemini31_full 复算。与 deepseekv4_cont_mw_sum_full、gpt54nano_cont_mw_sum_full 并排, 本列构成"同一 full 轨、换厂商模型"的逐模型稳健性主锚, 是检验语调主结论是否被单一模型驱动的关键并排轨。需要提示的是, Gemini 与 GPT 均经 OpenLux 网关调用而 DeepSeek 直连其官方 API, 这一路由差异不改变逐模型并排的稳健性地位, 但在生产首播播种缓存时须确保三家的键与凭据齐备, 缺任一家只导致该家族列独立缺席而不影响另两家。⚠ 铁律: full、ctx、ss 三轨与三家模型各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J。本列为未归一化分子, 供审计与替代归一化, 一般不单独直接入主回归。

## VAR: gemini31_cont_mw_sum_ss

【变体差分】
本列是 Gemini-3.1-flash-lite 模型在 ss (银行与金科同句共现) 轨上的媒体权威性加权连续语调银行-年累加和。文本轨维度上, ss 轨输入 content_ss 仅保留同句内同时含目标银行别名与金科词的最严片段并按窗口扩展, 判据比 ctx 更紧, 用以精准隔离银行与金融科技被真正并置讨论的语境; 回退语义镜像 ctx, 无同句共现时回退全文正文并置 ss_is_fallback 为真, 共享 n_articles 分母, 缺列再优雅回退 content_full。模型维度上, 本列取 Gemini 单家判定, 经 OpenLux 调用, 与 gpt54nano、deepseekv4 跨厂商并排互为稳健性; Gemini 自身 verified 为假仅掉本模型族列。作为分子须澄清: 面板不为本连续列物化 per-model 归一化输出, 已物化的 gemini31_tone_mw_ss 取自离散 sibling 列 gemini31_score_mw_sum_ss ÷ sum_wd_mw_gemini31_ss (分母为仅计 Gemini verified 篇权重的掩码媒体权威权重和, 缺列回退物理和 sum_media_authority_weight_ss), 而非本连续列; 本列若要连续归一化须镜像共识轨以本列除以同轨掩码权重和 sum_wd_mw_gemini31_ss 复算。留篇门控 full-only, 本列是 conditional-on-full 的最严子集测度, 度量 Gemini 在最贴近研究构念的"银行金科同句共现"语境下、经媒体权威加权的连续语调总量。因判据最严, 小样本开发期该轨易出现较多回退与零方差退化, 属预期; 生产期长面板恢复正常。与另两家模型的 ss 列并排, 可在最严语境下检验厂商稳健性。作为未归一化分子, 本列须除以同轨权重总和后方可横向比较, 单独读取其绝对量意义有限; 其价值在于让审计能逐轨追溯 Gemini 在最严共现语境下的加权语调分子是否与分母配套生成。⚠ 铁律: ss 与 full、ctx 两轨及三家模型各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: gpt54nano_cont_mw_sum_ctx

【变体差分】
本列是 GPT-5.4-nano 模型在 ctx (上下文片段) 轨上的媒体权威性加权连续语调银行-年累加和。模型维度上, 它取自经 OpenLux 网关调用的 GPT-5.4-nano, 与同走 OpenLux 的 gemini31 及直连 api.deepseek.com 的 deepseekv4 三家跨厂商并排, 互为稳健性、不分主次; 本列的极性与置信度取自 GPT 对该篇该轨的独立判定, 其 verified 为假时仅本模型族列置缺失, 独立降级不连坐。文本轨维度上, ctx 轨输入 content_ctx 聚焦目标银行别名命中句前后各默认 1 句的实体邻近窗口, 严苛度居 full 与 ss 之间, 在压缩无关噪声与保留足够语境之间取平衡。计算与家族一致: 每篇 ctx 连续语调 = GPT 离散极性 × 自报置信度, 乘媒体权威性权重后银行-年求和即本列。须澄清: 面板不为本连续列物化 per-model 归一化输出, 已物化的 gpt54nano_tone_mw_ctx 取自离散 sibling 列 gpt54nano_score_mw_sum_ctx ÷ sum_wd_mw_gpt54nano_ctx (分母为仅计 GPT verified 篇权重的掩码媒体权威权重和, 缺列回退物理和 sum_media_authority_weight_ctx), 而非本连续列; 本列若要连续归一化须镜像共识轨以本列除以同轨掩码权重和 sum_wd_mw_gpt54nano_ctx 复算。留篇门控 full-only, 本列在 full 留篇子集上按 conditional-on-full 逐轨计算。与 deepseekv4、gemini31 的同轨列并排, 检验语调主结论在更换 LLM 厂商时的稳健性。GPT-5.4-nano 作为轻量级模型在成本与吞吐上具备优势, 但其自报置信度的标定尺度可能与另两家不同, 因而本列的绝对量不宜与他家跨模型直接比水平, 只宜在各自 just-identified 并排设定内比较标准化后的系数方向与显著性。⚠ 铁律: 本列与 full、ss 两轨及另两家模型各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J。本列为未归一化分子, 服务审计追溯而非直接单列入回归。

## VAR: gpt54nano_cont_mw_sum_full

【变体差分】
本列是 GPT-5.4-nano 模型在 full (全文) 轨上的媒体权威性加权连续语调银行-年累加和, 为该模型三轨中的 canonical 留篇轨。文本轨维度上, full 轨输入 content_full 为标题 prepend 后的整篇正文, 信息最完整, 且是全项目留篇门控的判定基准 (llm_verified_full 决定一篇报道是否算作银行金科报道); 门控虽由 full 轨定义, 本列本身仍是 GPT 单家在 full 轨的一条独立度量轨。模型维度上, 本列取经 OpenLux 调用的 GPT-5.4-nano 单家判定, 与 gemini31、deepseekv4 跨厂商并排三角验证; GPT 自身 verified 为假时 score 置缺失, per-model 独立降级不连坐。计算上, 每篇 full 连续语调 = GPT 离散极性 × 自报置信度, 乘媒体权威性权重, 银行-年求和得本列。须澄清面板不为本连续列物化 per-model 归一化输出, 已物化的 gpt54nano_tone_mw_full 取自离散 sibling 列 gpt54nano_score_mw_sum_full ÷ sum_wd_mw_gpt54nano_full (分母为仅计 GPT verified 篇权重的掩码和, 缺列回退物理和 sum_media_authority_weight_full), 而非本连续列; 本列若要连续归一化须镜像共识轨以本列除以同轨掩码权重和 sum_wd_mw_gpt54nano_full 复算。与 gemini31_cont_mw_sum_full、deepseekv4_cont_mw_sum_full 并排, 本列构成"同一 full 轨、换厂商模型"的逐模型稳健性主锚, 是判断语调主结论是否被单一模型驱动的关键并排轨。在三家模型的 full 轨列都可得时, 研究者可对三列各自归一化后作跨模型一致性 (如 Krippendorff α 与 Cohen κ) 校核, 但这属于 full-only 门控与逐模型并排框架内的稳健性练习, 与本列作为分子的审计用途相互独立。⚠ 铁律: full、ctx、ss 三轨与三家模型各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J。本列为未归一化分子, 供审计与替代归一化, 一般不单独直接入主回归。

## VAR: gpt54nano_cont_mw_sum_ss

【变体差分】
本列是 GPT-5.4-nano 模型在 ss (银行与金科同句共现) 轨上的媒体权威性加权连续语调银行-年累加和。文本轨维度上, ss 轨输入 content_ss 仅保留同句内同时含目标银行别名与金科词的最严片段并按窗口扩展, 判据比 ctx 更紧, 用以精准隔离银行与金融科技真正被并置讨论的语境; 回退语义镜像 ctx, 无同句共现时回退全文正文并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母口径, 缺 content_ss 列时优雅回退 content_full。模型维度上, 本列取经 OpenLux 调用的 GPT-5.4-nano 单家判定, 与 gemini31、deepseekv4 跨厂商并排互为稳健性; GPT 自身 verified 为假仅掉本模型族列, 独立降级。作为分子须澄清: 面板不为本连续列物化 per-model 归一化输出, 已物化的 gpt54nano_tone_mw_ss 取自离散 sibling 列 gpt54nano_score_mw_sum_ss ÷ sum_wd_mw_gpt54nano_ss (分母为仅计 GPT verified 篇权重的掩码媒体权威权重和, 缺列回退物理和 sum_media_authority_weight_ss), 而非本连续列; 本列若要连续归一化须镜像共识轨以本列除以同轨掩码权重和 sum_wd_mw_gpt54nano_ss 复算。留篇门控 full-only, 本列是 conditional-on-full 的最严子集测度, 度量 GPT 在最贴近研究构念的"银行金科同句共现"语境下、经媒体权威加权的连续语调总量。因判据最严, 开发期小样本上该轨易出现较多回退与零方差退化, 属预期行为, 生产期长面板恢复正常。与另两家模型的 ss 列并排, 可在最严语境下检验厂商稳健性。同时须注意, ss 判据最严意味着 GPT 在该轨可参与判定的有效篇数通常少于 ctx 与 full, 银行-年累加和的分母 sum_media_authority_weight_ss 也相应更小, 因此本列在稀疏格上更易出现较大波动, 解释时应结合有效篇数与回退占比一并审视。⚠ 铁律: ss 与 full、ctx 两轨及三家模型各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Siano, F. (2025). The news in earnings announcement disclosures: Capturing word context using LLM methods. Management Science, 71(11), 9831-9855. https://doi.org/10.1287/mnsc.2024.05417
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., ... Yu, P. S. (2025). Harnessing multiple large language models: A survey on LLM ensemble. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2502.18036
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
