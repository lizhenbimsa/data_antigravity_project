---
family_id: F388
columns:
- llm_vote_cont_mw_sum_ctx
- llm_vote_cont_mw_sum_full
- llm_vote_cont_mw_sum_ss
unit: 无量纲加权得分和 (媒体权威性权重 × 置信度加权语调分, 银行-年内逐篇加总)
formula: 'sum_b,y(llm_vote_cont{track} × media_authority_weight), 其中 llm_vote_cont{track}
  = llm_vote_score{track} × llm_agreement_rate{track}, llm_vote_score{track} ∈ {-1,0,1}
  为三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票离散语调, llm_agreement_rate{track}
  为三家投票一致率 (∈[1/3,1]); 分子列, 除以 sum_media_authority_weight{track} 得
  llm_vote_tone_mw{track} (银行-年媒体权威性加权 tone, mean 语义)'
producer: pipeline/panel/encode.py
upstream:
- 21_tone_llms.py
- pipeline/panel/attention_media.py
citations:
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: Chinese fine-grained financial sentiment analysis with large language models
  venue: Neural Computing and Applications
  vol: '37'
  issue: '30'
  pages_or_artno: 24883-24892
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: ChatGPT for textual analysis? How to use generative LLMs in accounting research
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: 'FinBERT: A large language model for extracting information from financial text'
  venue: Contemporary Accounting Research
  vol: '40'
  issue: '2'
  pages_or_artno: 806-841
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority rules: LLM ensemble is a winning approach for content categorization'
  venue: arXiv
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
new_dois: []
---

## CORE

【构念与来源】
本家族三列 (llm_vote_cont_mw_sum_full / _ctx / _ss) 是银行-年面板层面的中间聚合列, 承载"三家 LLM 多数投票语调、经三家一致率加权后再按报道所在媒体的权威性权重加总"的分子和。它不是可直接解释的语调水平, 而是计算 llm_vote_tone_mw{track} (媒体权威性加权语调均值) 时的分子; 分母是同轨的 sum_media_authority_weight{track}。构念源头有两层: 第一层是 stage 21 (21_tone_llms.py) 产出的逐篇三家 LLM 语调投票 (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash 三家独立打分后多数表决), 第二层是 pipeline/panel/encode.py 把逐篇离散投票 llm_vote_score{track} (取值 -1/0/1) 乘以三家一致率 llm_agreement_rate{track} (∈[1/3,1], 三家全票一致时为 1, 二比一多数时约为 2/3) 得到连续编码 llm_vote_cont{track}, 再乘以该篇报道所在媒体的权威性权重 media_authority_weight (来自媒体权重表 media_weights.json, 与 preprocess/dedup.py 里用于抽样阶段的媒体权重同源但用途不同——此处不是抽样去重权重, 而是面板聚合阶段的信源权威性加权), 最后在银行-年内对全部符合条件的报道逐篇求和。之所以要用"连续编码"而非离散投票直接加权, 是因为多数投票的一致程度本身携带信息: 三家 LLM 一致同意"正面"比二比一勉强多数的"正面"更值得信赖, 用一致率对离散投票做连续化处理, 让强共识的报道在加权求和里天然获得更接近满额 ±1 的贡献, 弱共识的报道贡献相应收缩, 这与 Lan et al. (2025, Neural Computing and Applications) 论证中文金融文本细粒度/连续化情感编码优于粗粒度硬分类的思路一致——机器判读的不确定性本身应当被建模而非被舍弃。
【方法学与计算】
媒体权威性加权的动机是: 报道所在媒体的公信力/发行覆盖不同, 一篇来自权威财经媒体的正面报道与一篇来自地方小报的同等正面报道, 对市场参与者信息集的边际贡献理应不同; 用媒体权重加总而非简单等权计数, 是把"信源质量"这一维度显式建模进语调测度, 呼应 You, Zhang & Zhang (2018, RFS)"谁掌握了笔杆子的力量"关于媒体差异化影响力的论证——不同媒体的立场与可信度并非均质, 简单算术平均会抹平这一异质性。计算上, encode.py 先对每篇报道逐轨算出 llm_vote_score{track} (三家投票多数表决的离散语调, 无效/未通过三轨核验的报道记为缺失)、llm_agreement_rate{track} (三家一致率) 与 llm_vote_cont{track} (=score×一致率), 再逐篇乘以 media_authority_weight, 按银行-年分组求和落入本家族三列; 下游把该和除以同轨 sum_media_authority_weight{track} 得到 llm_vote_tone_mw{track} (媒体权威性加权语调均值, mean 语义)。本家族列本身是分子, 单独看无界且随篇数/权重规模变化, 不建议直接作解释变量, 正确用法是与分母列配对算出加权均值, 或在需要"总加权语调质量"而非"均值"的少数场景 (如 herd_decay 相关的规模敏感度检验) 直接使用。
【文献定位】
连续置信度加权语调这一构念设计, 与前述 Lan et al. (2025) 的细粒度/连续化编码论证一脉相承, 二者共同指向"离散硬标签会丢失中文财经文本语义复杂度里的可信度梯度"这一方法学判断; de Kok (2025, Management Science) 系统讨论了在会计与金融研究中使用生成式 LLM 做文本分析时, temperature=0、prompt 版本冻结与缓存复现范式是保证结果可审计、可复现的方法学基线, 本项目 stage 21 的 prompt v8 字节级冻结缓存与 `NEWS_PROCESS_LLM_OFFLINE=1` 离线复现正是循此范式落地。三家 LLM 多数投票本身 (score 的来源) 借鉴 Kamen & Kamen (2025) 关于 LLM 集成投票在内容分类任务上优于单模型的证据——多数投票比依赖单一厂商模型更能抵御个别模型的系统性偏差或幻觉, 一致率则进一步把"投票有多稳"量化为连续权重。Huang, Wang & Yang (2023, Contemporary Accounting Research) 的 FinBERT 研究提示金融文本情感抽取存在领域特异性, 本项目虽以 LLM 而非 BERT 为该家族基座, 但同样的领域特异性考量促使团队保留 BERT 三模型 (finbert_cn/fin_sent_zh/finbert2) 作为互为稳健性的并行轨, 与本 LLM 投票族并排而非合并——这也是为何面板同时存在 llm_vote_* 与 {bert}_* 两条不同技术路线的加权求和族。三轨 (full/ctx/ss) 与媒体权威性加权 (mw) 这两个维度是正交扩展: full/ctx/ss 回答"看多少上下文", mw 回答"报道信源权重该不该均等", 二者独立叠加, 不应混入同一过度识别 (over-identified) 的 Hansen J 检验——full/ctx/ss 各自与 vw (市值加权)/mw (媒体权威性加权)/hw (羊群/herd 加权) 等加权臂都是各自 just-identified、互为稳健性、不分主次的并排测度, 混用会人为制造检验统计量的虚假过度识别约束。留篇门控口径与全库一致: 是否计入某篇报道由 llm_verified_full 决定 (full-only 门控, 2026-06-29 起生效), ctx/ss 轨的行宇宙是 full 留篇集合的子集, 因此 ctx/ss 两轨的样本量恒不大于 full 轨, 三轨报告的是"同一留篇集合下不同上下文窗口"而非"不同样本"的语调差异。

## VAR: llm_vote_cont_mw_sum_ctx

【变体差分】
本列是 ctx 轨 (标题+实体窗口文本) 的 LLM 投票连续编码媒体权威性加权和。文本口径: content_ctx = 标题 + 目标银行/金科实体所在句子的窗口文本 (由 stage 14 ctx_materializer 物化), 与 full 轨 (标题+全文) 相比只保留实体相关上下文, 更贴近"读者只读到与银行/金科高度相关那几句话"的信息暴露场景。若某篇报道没有可识别的银行∧金科实体窗口, 该篇 content_ctx 回退为全文正文并标记 ctx_is_fallback=True, 该回退语义与 ss 轨镜像一致 (两者共享同一套回退规则, 只是窗口宽度不同)。三家 LLM 情感投票、一致率与媒体权威性加权流程与 full/ss 两轨完全相同, 唯一差异是喂给 LLM 的输入文本窗口; 留篇门控仍以 llm_verified_full 为准 (full-only 铁律), 本列的行宇宙是 full 轨留篇集合的子集, 用于检验"缩窄到实体窗口后语调结论是否仍然稳健", 与 full/ss 两轨互为稳健性并排, 不设主次, 不应混入同一过度识别 Hansen J 检验。作为分子列本身无界, 使用时应与同轨分母 sum_media_authority_weight_ctx 配对读出 llm_vote_tone_mw_ctx, 而非直接把本列数值当作语调水平解释; 若只关心方向而非规模, 也可只看本列的符号与同轨等权版 llm_vote_cont_sum_ctx 的相关方向是否一致, 用以粗判媒体权威性加权是否系统性改变了结论方向。ctx 轨常用于检验 full 轨结论是否受"无关正文噪声"污染: 若把阅读范围收窄到实体窗口后, 媒体权威性加权语调依然与 full 轨方向一致, 可为主结论提供一层针对上下文窗口选择的稳健性证据。

## VAR: llm_vote_cont_mw_sum_full

【变体差分】
本列是 full 轨 (标题+全文正文) 的 LLM 投票连续编码媒体权威性加权和, 是本家族三轨中的门控轨: 是否把某篇报道计入"一篇关于目标银行的金科相关报道"这一判定, 完全依据 llm_verified_full == True (2026-06-29 起的 full-only 留篇门控铁律), ctx/ss 两轨的样本集合都是本轨留篇集合的子集。full 轨给 LLM 的输入文本是标题+全文原始正文 (prepend_title 拼接, 未做实体窗口截断), 因此最贴近"读者完整阅读整篇报道"的信息暴露口径, 是 P1 (bank_fintech_tone) 主线论文的 canonical treatment 轨 (`treatment.primary` 对应 llm_vote_tone_full 一族)。作为分子列, 本列与 sum_media_authority_weight_full 配对可算出 llm_vote_tone_mw_full (媒体权威性加权语调均值), 是与等权版 llm_vote_tone_full、市值加权版 llm_vote_tone_vw_full、羊群加权版 llm_vote_tone_hw_full 并排的媒体质量加权稳健性臂, 四种加权口径 (等权/vw/mw/hw) 互为稳健性、不分主次, 各自 just-identified, 不应混入同一过度识别 Hansen J 检验。由于本列是门控轨的分子, 它同时决定 ctx/ss 两轨的样本量上界: 若某银行-年在 full 轨下几乎没有留篇 (llm_verified_full 全部为假), 三轨本列都会同步趋近于零或缺失, 这是设计使然而非数据缺陷, 使用时不应将三轨的规模差异误读为"内容窗口越窄语调越弱"。full 轨还是唯一一条同时被 P1 主线论文当作 treatment 且被稳健性梯子 (等权/vw/mw/hw 四种加权、以及规则消融梯度、政治词权重三档) 共同消费的轨道, 理解本列须以此为参照系: 它是"整篇正文语调 × 三家一致率 × 媒体权威性"三重信息压缩后的规模量, 分母配对后才具备横截面可比性。

## VAR: llm_vote_cont_mw_sum_ss

【变体差分】
本列是 ss 轨 (标题+银行∧金科同句±N窗) 的 LLM 投票连续编码媒体权威性加权和, 判定原语为 extract_bank_fintech_cooccurrence, 窗口半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制 (默认1句, 与 stage 13 硬过滤所用的 cooccurrence_filter.sentence_radius 是两个不同的配置键, 不可混用)。ss 轨要求银行与金科词汇在严格同句 (±N句窗) 内共同出现, 比 ctx 轨的实体窗口更苛刻, 是三轨中信息暴露范围最窄的一支, 用来检验"只有当银行与金科在同一句话里被直接关联提及"时语调结论是否依然成立。若报道内不存在这种同句共现, content_ss 回退为全文正文并标记 ss_is_fallback=True, 该回退语义镜像 ctx 轨 (两者共享同一份 n_articles 分母口径与回退处理逻辑)。留篇门控同样以 llm_verified_full 为准, 本列行宇宙是 full 轨留篇集合的子集; 三家 LLM 投票、一致率与媒体权威性加权流程与 full/ctx 两轨完全相同, 差异只在输入文本窗口, 与 full/ctx 两轨互为稳健性并排、不分主次, 不应混入同一过度识别 Hansen J 检验。ss 轨的媒体权威性加权和常常小于 ctx/full 两轨 (同句共现门槛更高, 符合条件的报道更少甚至更容易触发回退), 这一规模差异属于窗口构念本身的预期特征, 不构成异常; 与 ctx 轨类似, 正确用法是配对同轨分母 sum_media_authority_weight_ss 得到 llm_vote_tone_mw_ss 再做解释, 单独的求和列只用于规模/覆盖度诊断。

<!-- rendered-citations:begin -->
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
<!-- rendered-citations:end -->
