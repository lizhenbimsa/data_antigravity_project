---
family_id: F306
columns:
- fin_sent_zh_正面_mw_sum_ctx
- fin_sent_zh_正面_mw_sum_full
- fin_sent_zh_正面_mw_sum_ss
- finbert2_正面_mw_sum_ctx
- finbert2_正面_mw_sum_full
- finbert2_正面_mw_sum_ss
- finbert_cn_正面_mw_sum_ctx
- finbert_cn_正面_mw_sum_full
- finbert_cn_正面_mw_sum_ss
unit: 无量纲加权概率总和 (媒体权重 × 概率, bank-year 层面求和)
formula: 媒体加权正面概率总和 = Σ_i (media_weight_i × P_model(正面 | article_i)), 逐模型逐轨在 bank-year 单元内对该行所有留篇文章求和
producer: pipeline\sentiment\tone_berts.py (文章级 BERT 三模型三轨正面概率); pipeline\panel\encode.py (`build_aggregation_dict` 内 `agg[f'{b}_正面_mw_sum{track}'] = (f'{b}_正面_mw{track}', 'sum')` 做媒体加权求和聚合); pipeline\panel\codebook.py (`_bert_model_match` 仅用于 codebook 元数据标签生成, 不参与本列数值计算)
upstream:
- 22_words_tone.parquet
- 23_bert_tone.parquet
citations:
- doi: "10.1111/1911-3846.12832"
  type: journal
  authors: "Huang, A. H., Wang, H., & Yang, Y."
  year: 2023
  title: "FinBERT: A Large Language Model for Extracting Information from Financial Text"
  venue: "Contemporary Accounting Research"
  vol: "40"
  issue: "2"
  pages_or_artno: "806-841"
- doi: "10.1145/3711896.3737219"
  type: wp
  authors: "Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z."
  year: 2025
  title: "FinBERT2: A Specialized Bidirectional Encoder for Bridging the Gap in Finance-Specific Deployment of Large Language Models"
  venue: "Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)"
  pages_or_artno: "5117-5128"
- doi: "10.18653/v1/N19-1423"
  type: wp
  authors: "Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K."
  year: 2019
  title: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"
  venue: "Proceedings of NAACL-HLT 2019"
  pages_or_artno: "4171-4186"
- doi: "10.24963/ijcai.2020/622"
  type: wp
  authors: "Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J."
  year: 2020
  title: "FinBERT: A Pre-trained Financial Language Representation Model for Financial Text Mining"
  venue: "Proceedings of IJCAI-20"
  pages_or_artno: "4513-4519"
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure Sentiment: Machine Learning vs. Dictionary Methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
new_dois: []
---

## CORE

【构念与来源】
本家族衡量三个中文金融 BERT 分类器 (finbert_cn/fin_sent_zh/finbert2) 各自输出的"正面"概率, 在 bank-year 单元内按媒体权重加总后的强度指标, 记作 `{model}_正面_mw_sum_{track}`。它属于 CLAUDE.md「LLM 三家/BERT 三模型互为稳健性」体系里 BERT 一支的 per-model 加权总和臂: 三个模型各自跑一遍同样的加权求和口径, 彼此 co-equal、互为稳健性、不分主次, 用来证明"银行-金融科技报道整体偏正面"这一结论不依赖任一具体 BERT 模型的判断习惯。与 P1 主线的 LLM 投票语调 (`llm_vote_tone`) 不同, BERT 支路没有跨模型 ensemble headline——三个模型各自独立留存, 任一模型 (尤其是私有部署的 finbert2) 缺席只掉自身族列, 不连坐另外两个。数据来源是 stage 23 (`tone_berts.py`) 对 stage 22 词典法情感处理后的语料, 用三个预训练/微调 BERT 分类器对每篇文章做正面/负面/(中性) 概率打分; 这批文章级概率随后在 stage 40 面板导出阶段, 按每篇文章所属媒体的报道量权重 (media weight, `mw`) 在 bank-year 内加总, 得到本家族的 9 个面板列。
【方法学与计算】
三个 BERT 模型的技术路线彼此独立: finbert_cn (yiyanghkust/finbert-tone-chinese) 是三分类 (负面/中性/正面) 的中文金融领域微调模型; fin_sent_zh (bardsai/finance-sentiment-zh-base) 基于 Financial PhraseBank 思路微调、同为三分类; finbert2 是项目自建的私有二分类模型 (仅负面/正面, 无中性), 经 `.env` 的 `FINBERT2_MODEL_DIR` 解析本地权重, 未配置时优雅跳过 (另两个 HuggingFace 模型照常运行, 不受影响)。文章级推理阶段 (stage 23) 对超过模型单窗上限 (有效正文 ≤510 token) 的长文本用滑动窗口切片 (`WINDOW_STRIDE_RATIO=0.5`, 50% 重叠) 并按各窗置信度加权池化 logits 后 argmax 得到正面概率 `{model}_正面_{track}` (以及三轨各自的 `bert_num_windows_{track}` 空文本/失败哨兵)。三轨 full/ctx/ss 分别对应"标题+全文"/"标题+银行实体窗口"/"标题+银行∧金科同句窗口"三种不同范围的输入文本 (`prepend_title` 拼接), 各自独立推理、独立产出正面概率列, 各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J——三轨反映的是"测度范围"这一维度的稳健性, 不是同一构念的三个替代工具变量, 不可同时塞进一个过度识别方程。ss 轨的回退语义镜像 ctx: 若某篇文章没有银行∧金科词在同一句共现, 则 `content_ss` 退化为全文 body、`ss_is_fallback=True`, 与 `n_articles` 共享同一分母口径; `FINTECH_AC=None` 时 `*_is_fallback` 全 True, 整条 ss 轨优雅降级为等同 full 的口径而不报错。文章级正面概率进入面板阶段后, 由 `pipeline\panel\encode.py::build_aggregation_dict` 在 `agg[f'{b}_正面_mw_sum{track}'] = (f'{b}_正面_mw{track}', 'sum')` 一行归入媒体权威性加权 (`mw`) 求和臂 (`_bert_model_match` 正则只匹配英文 metric 名如 net_tone/pos_sum/pos_std, 不覆盖本家族的中文列名, 仅供 codebook 元数据标签生成使用, 与本列的实际数值计算无关): 对 bank-year 单元内该银行∧金科留篇文章集合, 用每篇文章所属媒体的权重乘以该模型该轨正面概率后逐篇求和, 得到 `{model}_正面_mw_sum_{track}`。这里的媒体权重 (`mw`) 来自 `pipeline\panel\runner.py::compute_media_authority_weights` (`3c` 步骤) 载入 `media_weights.json` 的静态媒体权威性评分 (量级 10-100, 参照 Holzman, Miller & Twedt 2023 *The Accounting Review* 的 Outlet Impact Media Sent 做简化替代), 是按媒体名称匹配到的预定义权威打分, 与该媒体在本语料库内实际出现的报道频次或篇数无关, 不是频次驱动的动态权重。它与羊群加权 `hw` (`herd_weight`, 三轨独立权重) 是并列而非嵌套的加权支路; 同一 `runner.py` 步骤 3b 还预计算了另一条并列支路 `vw`, 其权重取自 `mention_density` (提及密度, Hassan et al. 2019 *Quarterly Journal of Economics* 的 Value-weighted Exposure 构造思路)——即该银行实体在文章中被提及的密度, 而非市值 (market capitalization); 全仓不存在任何市值/市值加权字段参与该支路的构造, `vw` 之"value"指的是文本层面的提及强度权重, 不应理解为财务市值意义上的"价值加权"。本家族列名后缀为 `mw`, 因此三条支路里只有媒体权威性这一条与本家族直接相关, `hw`/`vw` 仅在此处作为并列支路的背景说明提及, 不参与本家族列的计算。加权求和口径 (`_mw_sum`) 与未加权均值口径 (无权重后缀的 `{model}_正面_{track}` 家族) 是并列的稳健性梯子, 而非同一列的不同表示——媒体权重回答"报道声量大的媒体是否驱动了正面判断"这一稳健性问题, 未加权口径回答"平均而言这家银行的报道有多正面"。留篇门控遵循全仓 full-only 铁律 (2026-06-29): 是否算作一篇有效的"银行-金科报道"只看 `llm_verified_full == True` (由 LLM 三家投票判定), ctx/ss 轨的行宇宙是 full 留篇集的子集, 三轨各自在这个共同行宇宙内独立计算, 不额外扩大或收缩样本。
【文献定位】
以 BERT 系列神经网络模型度量金融文本情感语调的做法, 方法学根基是 Devlin et al. (2019) 提出的双向 Transformer 预训练范式, 以及此后一系列面向金融领域的领域适配微调工作: Liu et al. (2020) 提出的 FinBERT 变体确立了"通用预训练+金融语料微调"的标准路径, Huang, Wang & Yang (2023) 在 *Contemporary Accounting Research* 进一步展示了大语言模型/BERT 类模型从财务文本中抽取信息的系统性优势——该文发表于会计学顶级期刊, 是本家族"用预训练神经网络模型而非纯词典规则度量语调"这一方法学选择的顶刊锚点。finbert2 模型本身出自 Xu et al. (2025) 在 KDD '25 提出的双向编码器架构, 该文明确将其定位为弥合大语言模型在金融领域专业化部署缺口的工具, 支撑本项目采用私有微调 finbert2 而非仅依赖通用 FinBERT 变体的设计选择。三模型 co-equal 并排、互不设定 ensemble headline 的稳健性设计, 呼应"多种独立测量工具对同一构念的结论一致性, 比单一工具更能排除结论由某个模型特异性判断习惯驱动"这一多方法互证思路——这与 stage 21 大语言模型三家投票、stage 22 词典法三条路线各自独立、互不设定单一权威口径的总体设计原则是同一逻辑在 BERT 支路的体现, 而非借助外部方法论文献确立。BERT 支路与 stage 21 的大语言模型三家投票、stage 22 的词典法三条路线并列, 构成本项目"大模型+词典+BERT"三条独立度量语调的总体设计, 三条路线互不隶属, 结论的稳健性建立在三者方向一致而非任一路线的绝对精度上。BERT 深层模型相较词典法在情感判定质量上的优势, 另有 Frankel, Jennings & Lee (2022, Management Science) 的直接顶刊证据支撑: 该文系统比较机器学习分类器与词典法在披露文本情感抽取上的表现, 证明经监督学习/微调的分类模型在识别语义层面的情感信号上显著优于关键词计数式词典法, 为本项目以 BERT 深层模型 (而非词典) 承担情感分类主力提供了顶刊层级的方法学背书。

## VAR: fin_sent_zh_正面_mw_sum_ctx

【变体差分】
本列取模型 fin_sent_zh (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的三分类中文金融情感模型), 轨道为 ctx (标题+银行实体窗口文本), 聚合为媒体加权 (mw) 正面概率总和。ctx 轨只把与目标银行实体相邻的文本片段喂给模型, 而非全文, 用意是让判断聚焦在"该银行"相关的语境上, 排除文章中与该银行无关段落带来的稀释或噪声。它与 full 轨 (同模型同权重、标题+全文) 及 ss 轨 (同模型同权重、标题+银行∧金科同句窗口) 是三条并排的稳健性测量, 三者对同一 bank-year 单元给出可能不同的正面强度总和, 差异本身即反映"文本范围选择"对度量结果的敏感性; 三轨结论方向一致才被视为稳健, 禁止把三轨同时作为工具或解释变量塞进同一个过度识别的 Hansen J 检验。媒体加权 (mw) 意味着本列不是简单的算术求和, 而是按各篇报道所属媒体的权重加权后求和, 与同模型同轨但无权重后缀的未加权求和列构成加权/未加权的并排稳健性对照, 二者互不替代。fin_sent_zh 与 finbert_cn 同为三分类结构 (负面/中性/正面), 二者在 ctx 轨上的对照构成"同架构不同训练来源"这一稳健性维度, 用以检验结论是否依赖某个特定模型的训练语料或微调细节; 而与 finbert2 的对照则额外引入"二分类 vs 三分类"这一架构维度。两条维度均归入 CLAUDE.md 所述的 per-model 互为稳健性铁律, 三模型各自 just-identified, 不构成联合过度识别方程的组成部分。

## VAR: fin_sent_zh_正面_mw_sum_full

【变体差分】
本列取模型 fin_sent_zh, 轨道为 full (标题+全文, 无实体窗口或同句限制的完整正文), 聚合为媒体加权正面概率总和。full 轨是三轨中信息量最完整的一支, 模型看到文章的全部内容 (通过滑动窗口切片处理超长文本并加权池化多窗结果), 因此其正面判断也最容易受到与目标银行无关段落 (如文章中同时报道其他机构、宏观背景介绍等) 的影响而产生稀释。它与 ctx/ss 两条更聚焦的轨道并排、互为稳健性, 不设何者为"更优"; 若三轨方向一致, 表明模型对该银行-金科报道的正面判断不依赖于文本截取范围。作为留篇门控的口径锚, full 轨的 `llm_verified_full` 判定同时决定了 ctx/ss 轨的行宇宙边界 (2026-06-29 full-only 铁律), 但这一门控作用于文章是否入选样本, 与本列的媒体加权求和计算本身是两个独立环节。full 轨的滑动窗口切片 (`WINDOW_STRIDE_RATIO=0.5`, 50% 重叠) 对长文章尤为重要, fin_sent_zh 与 finbert_cn 两个三分类模型在此机制上完全对称, 差异只体现在各自的训练语料与微调目标, 因此本列与 finbert_cn 同轨列的比较可视为对"三分类模型选择"这一具体维度的稳健性检验, 而与 finbert2 同轨列的比较则同时叠加了架构维度的差异。

## VAR: fin_sent_zh_正面_mw_sum_ss

【变体差分】
本列取模型 fin_sent_zh, 轨道为 ss (标题+银行与金融科技词在同一句共现的窗口文本), 聚合为媒体加权正面概率总和。ss 轨是三轨中范围最窄、判据最严的一支: 只有当目标银行实体与金融科技相关词汇在同一个句子内共现时, 该句才被纳入喂给模型的文本; 若某篇留篇文章没有这种同句共现 (`FINTECH_AC` 词表未命中或架构未就绪), 该篇的 `content_ss` 回退为全文 body、`ss_is_fallback=True`, 与 ctx 轨的回退语义镜像一致, 且与 `n_articles` 共享同一分母, 不额外剔除或扩样。这一设计保证 ss 轨永远有值可算, 不会因严格判据落空而产生系统性缺失。ss 轨与 ctx/full 两轨并排、互为稳健性, 是三者中对"银行-金科强关联语境"刻画最精确、但也最依赖上游共现检测质量的一支。ss 轨判据的构造 (银行∧金科同句共现) 与三轨文本后缀本身是两套不同的分类体系: 前者关乎"进入模型的句子是否满足特定语义邻近条件", 后者关乎"喂给模型的文本范围有多大", 二者名义上都用 ss 标记但含义不同, 阅读本列时应以 CLAUDE.md「三轨 full/ctx/ss」条目的定义为准, 不与网络指标族的判据后缀 (`_win1`/`_sent`) 混淆。

## VAR: finbert2_正面_mw_sum_ctx

【变体差分】
本列取模型 finbert2 (项目自建私有二分类 BERT, 仅正面/负面两类、无中性档位), 轨道为 ctx, 聚合为媒体加权正面概率总和。finbert2 由于是二分类模型, 其"正面概率"在数值分布上与另两个三分类模型 (finbert_cn、fin_sent_zh, 概率质量在正/负/中性三档间分摊) 不完全可比——finbert2 的正面概率天然更集中在两极, 因此跨模型比较时应关注方向一致性与标准化后的效应量, 而非概率水平本身的绝对大小。finbert2 依赖 `.env` 中 `FINBERT2_MODEL_DIR` 指向的本地私有权重; 该环境变量未配置或路径失效时, finbert2 全族 (含本列) 优雅跳过, 仅此模型的三轨列整体缺失, 不影响 finbert_cn/fin_sent_zh 两个 HuggingFace 模型的族继续产出 (per-model 独立降级, 非 co-primary 嵌入式的 both-or-neither)。本列与 ctx 轨的另两个模型列、以及 finbert2 自身的 full/ss 两轨列并排, 互为稳健性。由于 finbert2 是二分类而非三分类, ctx 轨在实体窗口文本较短时更容易产生接近极值 (接近 0 或接近 1) 的判断, 这与三分类模型因中性档位分流概率质量而呈现出的较平缓分布形成对照; 这一架构差异是解读跨模型比较结果时应纳入考量的背景, 而非需要修正的偏差。本列的媒体加权求和口径继承了家族层面对 mw/vw/hw 三支加权臂并列不隶属的一般设计。

## VAR: finbert2_正面_mw_sum_full

【变体差分】
本列取模型 finbert2, 轨道为 full, 聚合为媒体加权正面概率总和。作为三模型中唯一的私有二分类架构, finbert2 在 full 轨上直接对标题+全文做正面/负面二选一判断, 概率解释为"该文本被判为正面而非负面的置信度", 与三分类模型把部分概率质量分给中性类别的机制不同。本列与 fin_sent_zh_正面_mw_sum_full、finbert_cn_正面_mw_sum_full 构成 full 轨下的三模型并排稳健性对照, 三者共同验证"银行-金科报道整体偏正面"结论是否稳健于具体模型架构 (二分类 vs 三分类、私有微调 vs 公开预训练) 的选择。finbert2 缺席时本列整列缺失, 不影响另两模型的 full 轨列。full 轨给 finbert2 提供了最完整的输入文本量, 有助于滑动窗口机制在多个窗口间充分平均、降低单窗噪声对最终判断的影响; 但也意味着与 ctx/ss 两条更聚焦的轨道相比, full 轨的判断更容易被文章中与目标银行无关的段落 (背景介绍、其他机构报道等) 稀释, 这是三轨并排设计要检验的核心稳健性问题之一, 本列作为 finbert2 支路里信息量最完整的一格承担了这一检验的基准角色。由于 finbert2 是本项目自建的私有模型, 其训练语料与微调目标未必与公开发布的 finbert_cn/fin_sent_zh 完全一致, full 轨作为覆盖信息最全的一支, 是判断 finbert2 与另两个公开模型在同一段完整文本上是否给出方向一致判断的首要对照格; 若三模型在 full 轨上方向一致, 即可初步排除"finbert2 私有训练细节导致系统性偏离"这一担忧, 但仍需结合 ctx/ss 两轨的一致性做完整判断。

## VAR: finbert2_正面_mw_sum_ss

【变体差分】
本列取模型 finbert2, 轨道为 ss, 聚合为媒体加权正面概率总和, 是本家族里判据最严 (银行∧金科同句共现) 且模型架构最特殊 (私有二分类) 的一个组合。ss 轨的回退语义 (无同句共现则退化为全文、`ss_is_fallback=True`, 分母与 `n_articles` 共享) 与 fin_sent_zh/finbert_cn 两模型的 ss 轨完全一致——回退逻辑是轨道层面的属性, 与具体用哪个 BERT 模型打分无关。本列若因 `FINBERT2_MODEL_DIR` 未配置而缺失, 属于 per-model 降级而非 ss 轨本身失效, ss 轨在另两模型上照常产出。ss 轨判据的严格性 (银行∧金科同句共现) 叠加 finbert2 二分类架构对短文本更容易给出极值判断的特性, 使得本列在共现命中的少数文章上可能呈现比 full/ctx 两轨更强的正面或负面倾向, 解读时应结合 `ss_is_fallback` 指示列区分"真实同句共现打分"与"回退到全文打分"两种情形, 不可笼统混同。finbert2 缺席场景下本列与 ctx/full 两轨同步整族缺失, 而三模型的 ss 轨回退语义 (镜像 ctx, 分母共享 `n_articles`) 对存活模型完全不受影响, 因此即便 finbert2 支路整体不可用, fin_sent_zh 与 finbert_cn 两模型的 ss 轨稳健性检验依然可以独立完成, 不因单一模型缺席而失去论证力。本列数值应始终与 `bert_num_windows_ss` 哨兵列联合读取: 若某篇文章的窗口数为 0 (空文本) 或 -1 (推理失败), 该篇不应计入本列的加权求和, 与正常推理成功的篇目严格区分, 避免把哨兵值误当作真实的低正面概率纳入统计。

## VAR: finbert_cn_正面_mw_sum_ctx

【变体差分】
本列取模型 finbert_cn (yiyanghkust/finbert-tone-chinese, 公开发布的三分类中文金融领域微调 BERT), 轨道为 ctx, 聚合为媒体加权正面概率总和。finbert_cn 是三个 BERT 模型中最早被学界广泛采用、公开可复现程度最高的一个, 其三分类输出 (负面/中性/正面) 结构与 fin_sent_zh 相同, 二者互为同构模型的跨厂商/跨训练语料稳健性对照, 而 finbert2 的二分类结构则是架构层面的第三种独立视角。本列在 ctx 轨上聚焦银行实体窗口文本, 与同模型 full/ss 两轨、以及 ctx 轨下另两个模型列共同构成本家族的稳健性网格, 各格并排、不设主次。由于 finbert_cn 在多篇既有实证会计/金融文献中被反复使用, 本列常被研究者当作跨论文比较的锚点; 但在本项目自身的稳健性论证里, 它与 finbert2/fin_sent_zh 两模型是完全对等的三分之一, 不因"更常被引用"而获得优先解释权。读取本列数值时须同时参照 `finbert_cn_正面_mw_sum_full` 与 `finbert_cn_正面_mw_sum_ss` 两个同模型异轨列, 以及未加权口径的对照列, 综合判断结论是否稳健。finbert_cn 训练所依据的公开语料与 fin_sent_zh 的 Financial PhraseBank 微调路线在覆盖范围上存在差异, 两者在 ctx 轨上对同一批银行实体窗口文本可能给出不完全相同的正面强度总和, 这类差异属于预期内的跨模型测量误差, 只要三模型三轨的方向大体一致即视为结论稳健, 不需要也不应当以某一模型的数值为基准去校准另一模型。

## VAR: finbert_cn_正面_mw_sum_full

【变体差分】
本列取模型 finbert_cn, 轨道为 full, 聚合为媒体加权正面概率总和, 是本家族里覆盖信息量最完整 (标题+全文) 且模型公开可复现程度最高的一格, 常被用作跨模型比较时的方法学参照点。它与 fin_sent_zh_正面_mw_sum_full (同轨、同为三分类) 以及 finbert2_正面_mw_sum_full (同轨、二分类) 并排, 三者共同承担"结论是否依赖具体 BERT 模型选择"这一稳健性论证; 与 finbert_cn 自身的 ctx/ss 两轨并排, 承担"结论是否依赖文本截取范围"这一稳健性论证。两条稳健性维度 (跨模型/跨轨) 正交, 互不交叉, 均不设 over-identified 联合检验。full 轨在门控口径上还承担一个额外角色: 是否把某篇文章计入 bank-year 分母 (`n_articles`) 的判定完全由 full 轨的 `llm_verified_full` 决定, ctx/ss 两轨只在这个既定行宇宙内独立计算各自的加权总和, 不反过来影响样本纳入与否; 因此本列在解读上兼具"三模型稳健性锚"与"留篇门控参照轨"的双重含义, 但这两层含义须分开理解, 不可混为一谈。finbert_cn 作为学界最广泛使用的中文金融 BERT 变体之一, 其 full 轨判断常被用来与其他研究团队的公开结果做粗略参照, 但在本项目内部, 这种"外部知名度"不应转化为"内部权重更高"——三模型 co-equal 的设计初衷正是要避免因某个模型更常被引用就默认其判断更可信, 而是要求三者方向一致才共同支持结论。

## VAR: finbert_cn_正面_mw_sum_ss

【变体差分】
本列取模型 finbert_cn, 轨道为 ss, 聚合为媒体加权正面概率总和, 是 finbert_cn 三轨中判据最严的一支——只对银行与金融科技词同句共现的句子打分, 无共现的留篇文章回退为全文 (`ss_is_fallback=True`, 与 `n_articles` 共享分母)。本列与同模型 ctx/full 两轨、以及 ss 轨下另两模型列 (fin_sent_zh、finbert2) 并排, 分别对应"文本范围敏感性"与"模型架构敏感性"两条互不交叉的稳健性检验维度, 三模型三轨共 9 列构成本家族完整的稳健性网格, 任一单列的缺失或异常不应被解读为家族整体结论的推翻, 而应结合网格内其余 8 列的方向一致性综合判断。finbert_cn 的三分类结构在 ss 轨这种文本量较小的严格判据场景下, 中性档位吸收概率质量的效应可能比 full 轨更明显 (短句文本比长文更容易被判为中性), 这是解读本列与同模型其他轨道数值差异时需要留意的一个机制性因素, 而非模型出错的信号。本列与 fin_sent_zh_正面_mw_sum_ss、finbert2_正面_mw_sum_ss 共同构成 ss 判据下的三模型对照组, 三者共享同一套回退语义与分母口径, 差异只来自各自的分类架构与训练来源, 是本家族里检验"严格判据下结论是否依赖模型选择"这一具体稳健性问题的完整对照集。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A Large Language Model for Extracting Information from Financial Text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A Specialized Bidirectional Encoder for Bridging the Gap in Finance-Specific Deployment of Large Language Models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25) No. 5117-5128 [Working Paper]. https://doi.org/10.1145/3711896.3737219
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. Proceedings of NAACL-HLT 2019 No. 4171-4186 [Working Paper]. https://doi.org/10.18653/v1/N19-1423
Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A Pre-trained Financial Language Representation Model for Financial Text Mining. Proceedings of IJCAI-20 No. 4513-4519 [Working Paper]. https://doi.org/10.24963/ijcai.2020/622
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
<!-- rendered-citations:end -->
