---
family_id: F549
columns:
- target_bank
- year
unit: 标识符 (字符串 target_bank; 整数 year)
formula: 面板主键结构列 (无导出公式, 不参与算术计算)
producer: pipeline\panel\attention_media.py ; pipeline\panel\iv_did.py
upstream: []
citations:
- doi: 10.1093/rfs/hhy083
  type: journal
  authors: Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M.
  year: 2019
  title: "Information, trading, and volatility: Evidence from firm-specific news"
  venue: The Review of Financial Studies
  vol: "32"
  issue: "3"
  pages_or_artno: 992-1033
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: "145"
  issue: "2"
  pages_or_artno: 445-463
- doi: 10.3386/w32026
  type: wp
  authors: van Binsbergen, J. H., Bryzgalova, S., Mukhopadhyay, M., & Sharma, V.
  year: 2024
  title: "(Almost) 200 years of news-based economic sentiment"
  venue: National Bureau of Economic Research Working Paper Series
  vol: ""
  issue: ""
  pages_or_artno: "No. 32026"
new_dois: []
---

## CORE

【构念与来源】
本家族 F549 是全库面板数据的主键结构列组, 由 target_bank (目标银行标识, 字符串) 与 year (观测年份, 整数) 两列构成。二者共同定义面板数据集的行唯一性 (bank-year panel 的行索引单元), 本身不承载任何测度构念 (无正面/负面情感、无强度、无得分), 而是承载"这一行观测属于哪家银行、哪一年"的坐标信息。target_bank 取值来自 config/bank_list.yaml 定义的样本框 (config/银行面板2007-2025年.xlsx 提供的实体标识符骨架, 详见项目 memory 「银行面板xlsx=标识符骨架」), 覆盖国有大行、股份制银行、城商行、农商行等各类持牌金融机构的规范化中文名称; year 取值来自原始新闻发布年份或财务报告年份, 落在样本窗口 2007-2025 (全量语料) 或本机 dev 环境的 2017-2018 (T=2 试跑窗) 之内。两列在全部面板产出文件 (40_panel_yearly.parquet 及其下游 46_stata_export 生成的各 .dta 文件) 中恒定出现于最左侧, 是所有后续 merge、reshape、xtset 操作的锚点。

在 pipeline 内部, target_bank 与 year 并非由单一 producer 一次性生成, 而是在多个阶段的聚合操作中反复以 groupby key 的身份出现并被透传: 上游 stage 11 (news_bank) 在文章级别识别出目标银行实体后写入 target_bank 列; stage 00 (preprocessing) 从原始新闻发布时间解析出 year; 此后 stage 40 (panel_export_main) 以 (target_bank, year) 为唯一分组键, 把文章级 (article-level) 的全部情感/注意力/网络/结构测度聚合为银行-年 (bank-year) 一行。attention_media.py 与 iv_did.py 是本家族 grep 命中的两个高频 producer, 但它们的角色是"消费" (下游 groupby/merge 使用) 而非"生成"这两列的原始语义: attention_media.py 的 detect_defacto_cessation 函数以 (媒体, year) 维度聚合媒体覆盖区间 (first_year/last_year), 需要面板已具备 year 列作为时间轴; iv_did.py 的 Bartik/LOO/DID 各引擎需要按 (银行分组, year) 做经济圈/同组 leave-one-out 均值与政策冲击年份比对, target_bank 与 year 是这些引擎能够正确对齐"谁在哪一年"的前提。

【方法学与计算】
target_bank 与 year 无导出公式, 其"计算"逻辑是实体匹配与时间解析, 而非算术变换: target_bank 依赖银行名称规范化字典 (含总部匹配、别名合并、误配剔除), year 依赖新闻发布日期字段的年份提取 (preprocessing 阶段) 或财务年报口径的年份对齐 (若涉及外部财务面板接入)。二者组合构成面板的唯一主键 (unique key), 即 (target_bank, year) 在最终面板文件中不应有重复行 — 这是 test_dag_consistency.py 与面板可复现性测试隐含检验的不变量之一, 也是 Stata 侧 `xtset target_bank_id year` (或等价的数值化银行 ID) 操作得以成立的必要条件。当财务数据面板接入后 (memory「财务数据将补勿过度强调缺失」), (target_bank, year) 仍将是与外部财务面板 merge 的连接键, 因此其规范化质量 (银行名称唯一性、年份口径一致性) 直接决定下游 merge 的准确率, 任何合并/更名/停业事件若未在银行名称字典中妥善处理, 都会造成同一实体在不同年份被记为不同 target_bank 值, 从而人为制造面板的伪短小 (pseudo-attrition) 或伪进入 (pseudo-entry)。

target_bank 与 year 在识别策略与结构测度语境下还承担另一重角色: 三轨 (full/ctx/ss) 文本口径、co-primary 双轨嵌入 (canonical Qwen3-Embedding-8B 与 `_lg` text-embedding-3-large)、以及各类消融梯度 (词典规则消融、政治词权重 {0.0,0.5,1.0}、罕见词频次 cutoff、BERT 分布阈值梯子等) 全部是在 (target_bank, year) 这一固定坐标系上并列展开的测度族 — 这些梯子彼此互为稳健性、不分主次、各自 just-identified 并排, 禁止混进同一 over-identified Hansen J 检验; 但无论选择哪一条轨道或哪一档参数, 其行索引锚点始终是同一个 (target_bank, year)。这意味着 target_bank/year 本身对三轨/双轨/梯度选择保持中立 (track-agnostic), 是唯一"不能双轨化"的元数据类列 (镜像 memory「双轨=互为稳健性」中关于 track-agnostic 元数据的界定)。留篇门控 (2026-06-29 起 full-only 口径) 同样不改变 target_bank/year 的取值范围或聚合方式, 门控只影响进入聚合分母的文章行数 (n_articles 等下游测度), 不影响主键本身的定义。

【文献定位】
以 (实体, 时间) 为面板数据主键组织非结构化文本信息进行经济学分析, 其方法论基础可追溯到金融文本挖掘对"公司特异性新闻" (firm-specific news) 的系统化处理: Boudoukh, Feldman, Kogan & Richardson (2019, Review of Financial Studies) 论证了将新闻文章按公司与时间两个维度对齐、剥离宏观共同因子后提取信息含量的必要性, 其核心方法学前提正是要求文本数据能够被精确映射到"哪家公司、哪个时间点"这一坐标系 — 这与本家族 target_bank/year 作为主键结构列所扮演的角色高度吻合: 若实体识别或时间解析存在系统性偏误, 后续一切基于新闻的情感/注意力测度都将继承该偏误。Heese, Pérez-Cavazos & Peter (2022, Journal of Financial Economics) 关于地方报纸停刊如何造成公司治理监督真空的研究进一步提示, 面板中媒体覆盖随时间的进入与退出本身携带信息 (并非纯噪声), 因此 target_bank/year 主键的完整性 (是否存在未被识别的覆盖缺口) 需要如 attention_media.py 中 detect_defacto_cessation 那样被显式建模, 而非默认面板是平衡的。van Binsbergen, Bryzgalova, Mukhopadhyay & Sharma (2024, NBER Working Paper No. 32026) 对近两百年新闻文本情感的长时段构建同样表明, 面板类新闻情感研究的稳健性高度依赖底层 (实体, 年份) 主键在跨越长时间窗口时的一致性维护, 这与本项目样本窗口从 2007 延伸至 2025 (全量语料 T=19) 所面临的银行更名、合并、重组等实体识别挑战性质相同。

## VAR: target_bank

【变体差分】
target_bank 是本家族内唯一的实体标识列, 取值为规范化后的中文银行名称字符串, 来自 config/bank_list.yaml 定义的样本框与 config/银行面板2007-2025年.xlsx 提供的标识符骨架 (该 xlsx 仅含 4 列身份标识信息、无财务列, 其价值在于提供实体匹配字典与样本框定义, 被下游 40 号及后续多个阶段引用, 不可删除)。该列在 stage 11 (news_bank) 完成文章级银行实体识别后写入, 随后在 stage 40 (panel_export_main) 的聚合环节作为 groupby 主键之一被保留到面板输出。与本家族内的 year 列不同, target_bank 承载的是横截面维度 (cross-sectional dimension) 的身份信息, 不随时间推移改变取值范围 (除非涉及银行更名/合并/新设/退出样本, 这类事件需要在银行名称规范化字典中显式处理, 否则会造成同一实体因名称漂移而被误判为多个不同的 target_bank)。target_bank 与三轨文本口径、co-primary 双轨嵌入、各类消融梯度均保持正交: 无论下游哪一条测度轨道被激活, target_bank 的取值本身不发生变化, 它只是被用作聚合与合并的键, 而非被测度的对象。在 attention_media.py 的停刊代理检测逻辑中, target_bank 与"媒体(中文)"是两个不同维度的实体标识 (前者是银行, 后者是新闻媒体来源), 二者不可混淆; 在 iv_did.py 的 Bartik/LOO 引擎中, target_bank 进一步被映射到银行分组 (group, 如按银行类型或经济圈划分), 用于计算同组内 leave-one-out 均值, 但这一分组映射是 target_bank 的下游衍生使用, 并不改变 target_bank 列本身的定义或取值。

## VAR: year

【变体差分】
year 是本家族内唯一的时间标识列, 取值为整数型观测年份, 定义面板的纵向 (longitudinal) 维度。该列在 stage 00 (preprocessing) 阶段从原始新闻发布时间字段解析得出, 随后贯穿全部下游阶段, 在 stage 40 的聚合环节与 target_bank 共同构成面板主键。本机 dev 环境样本窗口为 2017-2018 (T=2, 176 行, 110 家银行 × 2 年); 真实全量语料样本窗口为 2007-2025 (T=19, 约 1,819 万条新闻经过滤后聚合)。year 与本家族内 target_bank 的核心差异在于: year 是全部纵向分析 (滞后项 L./F./D.、年度固定效应、DiD 处理时点比对、面板固定效应模型 xtset 的时间维声明) 的锚点, 而 target_bank 是横截面维的锚点。在 iv_did.py 的 DID 政策冲击变量合并 (merge_policy_shocks) 逻辑中, year 被用于比对银行所在城市/省份的政策试点 (如 DCEP、监管沙盒) 生效年份, 从而生成处理指示变量; 由于本机 dev 面板样本窗口 (2017-2018) 早于多数政策处理年份 (≥2019), 该比对在 T=2 开发环境下产生退化 (处理指示恒为 0, 不可识别), 这是样本窗口过短导致的预期表现, 并非 year 列本身的构造缺陷, 全量语料 T=19 窗口下该比对将正常产生跨时间的处理前后变异。year 与三轨文本口径、co-primary 双轨嵌入、消融梯度同样保持正交, 任何测度轨道或参数梯度的选择都不改变 year 列的取值范围或聚合口径, year 只决定该行观测属于纵向哪一个时间切片。

<!-- rendered-citations:begin -->
Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M. (2019). Information, trading, and volatility: Evidence from firm-specific news. The Review of Financial Studies, 32(3), 992-1033. https://doi.org/10.1093/rfs/hhy083
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
van Binsbergen, J. H., Bryzgalova, S., Mukhopadhyay, M., & Sharma, V. (2024). (Almost) 200 years of news-based economic sentiment. National Bureau of Economic Research Working Paper Series No. No. 32026 [Working Paper]. https://doi.org/10.3386/w32026
<!-- rendered-citations:end -->
