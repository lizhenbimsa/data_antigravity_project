---
family_id: F429
columns:
  - low_conf_flag
unit: 二值哑变量 (0/1, 无量纲)
formula: "low_conf_flag = 1{avg_category_confidence < 0.5}; avg_category_confidence 列缺失(全 NaN)时该行仍按 NaN<0.5→False 规则置 0, 而非留空"
producer: news_process/pipeline/panel/export.py::_materialize_low_conf_flag (导出前无条件物化); 源统计量 avg_category_confidence 由 news_process/pipeline/panel/encode.py 从 category_confidence_full/_ctx (tone_llms.py 产出) 按 target_bank×year 均值聚合
upstream:
  - 21_tone_llms.parquet (category_confidence_full / category_confidence_ctx)
  - 40_panel_export_main (encode.py 聚合 avg_category_confidence)
citations:
- doi: 10.1257/aer.20200374
  type: journal
  authors: Aguirregabiria, V., Clark, R., & Wang, H.
  year: 2025
  title: "The geographic flow of bank funding and access to credit: Branch networks, synergies, and local competition"
  venue: American Economic Review
  vol: 115
  issue: 6
  pages_or_artno: 1818-1856
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: "Bank transparency and deposit flows"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 475-501
- doi: 10.18653/v1/2024.naacl-long.366
  type: wp
  authors: Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I.
  year: 2024
  title: "A survey of confidence estimation and calibration in large language models"
  venue: "Proceedings of NAACL-HLT 2024"
  pages_or_artno: 6577-6595
- doi: 10.1145/1102351.1102430
  type: wp
  authors: Niculescu-Mizil, A., & Caruana, R.
  year: 2005
  title: "Predicting good probabilities with supervised learning"
  venue: "Proceedings of the 22nd International Conference on Machine Learning (ICML)"
  pages_or_artno: 625-632
- doi: 10.1177/0956797611417632
  type: journal
  authors: Simmons, J. P., Nelson, L. D., & Simonsohn, U.
  year: 2011
  title: "False-positive psychology: Undisclosed flexibility in data collection and analysis allows presenting anything as significant"
  venue: Psychological Science
  vol: 22
  issue: 11
  pages_or_artno: 1359-1366
- doi: "10.1162/tacl_a_00754"
  type: "journal"
  authors: "Wen, B., Yao, J., Feng, S., Xu, C., Tsvetkov, Y., Howe, B., & Wang, L. L."
  year: 2025
  title: "Know Your Limits: A Survey of Abstention in Large Language Models"
  venue: "Transactions of the Association for Computational Linguistics"
  vol: "13"
  pages_or_artno: "529-556"
- doi: "10.18653/v1/2025.naacl-long.179"
  type: "journal"
  authors: "Gligoric, K., Zrnic, T., Lee, C., Candes, E., & Jurafsky, D."
  year: 2025
  title: "Can Unconfident LLM Annotations Be Used for Confident Conclusions?"
  venue: "Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)"
  pages_or_artno: "3514-3533"
new_dois: []
---

## CORE

【构念与来源】

low_conf_flag 是一个纯诊断性的银行-年度层级二值哑变量, 用来标记某个 bank×year 观测在 LLM 分类维度(底层技术 vs. 应用场景, Gomber 等 2018 意义上的 locus 二分)上的平均置信度是否处于"偏低、结果慎用"区间。它不是任何构念的测度本身, 而是对上游 LLM 分类信号质量的元信息 (meta-information)封装: 当一年内某银行的相关报道整体上让三家大模型难以在"底层技术"与"应用场景"之间给出高置信度归类时, 该行的 tech_frac / app_frac 等基于该分类衍生的比例型指标就更可能混入分类噪声, 论文使用者应当对这些行的回归结果保持审慎, 或者在稳健性检验中将其剔除、加权降低或单独分组比较。

数据来源链条: 该列的直接上游是 avg_category_confidence, 由 pipeline/panel/encode.py 在 bank-year 聚合阶段从 article×bank 级 category_confidence_full(优先) 或历史 legacy 裸名 category_confidence 按 (target_bank, year) 分组取均值得到; 而 category_confidence_full/_ctx 本身则是 stage 21 tone_llms.py 在做底层技术/应用场景(locus)分类判定时, 由 LLM×关键词混合 (hybrid LLM×keyword) 判据产出的逐篇分类置信度评分。这条链路属于 P4 (Gomber locus) paper 的辅助诊断轨, 与 P4 主线 treatment 变量(如 sub_frac/tech_frac/collab_frac 等分类维度衍生比例)共享同一批底层置信度信号, 但 low_conf_flag 本身并不进入任何论文的主回归设定, 它是一个纯粹的样本质量筛查/稳健性工具列。

【方法学与计算】

计算规则极其简明: 只要面板中存在 avg_category_confidence 这一列, 就无条件按阈值 0.5 做二分类映射: avg_category_confidence < 0.5 记 1(低置信度), 否则记 0(含置信度缺失/NaN 的情形, 因为 NaN < 0.5 在 pandas 布尔比较语义下恒为 False, 从而被映射为 0 而非保留缺失)。这一"NaN→0"的处理是有意为之的工程选择而非疏漏: 早期实现曾把该列的创建嵌在 log_diagnostics 函数内部一个 `if len(valid_conf) > 0` 条件分支中, 导致 avg_category_confidence 全为 NaN(例如本机试跑样本量小、分类置信度尚未就位)的情况下该列干脆不存在, panel schema 随数据内容而非代码路径漂移, 且隐式依赖 runner 必须先调用 log_diagnostics 再调用 export_panel 的调用顺序契约, 是一处脆弱的副作用式设计。修复后, log_diagnostics 被收紧为纯只读函数(不再变异 panel), 列的物化改为 export_panel 内部通过 _materialize_low_conf_flag 无条件执行: 只要 avg_category_confidence 列在 panel 中存在(不论其取值是否全为 NaN), 就会生成 low_conf_flag, 语义与修复前"NaN<0.5→False→0"逐位一致, 但 schema 稳定性不再依赖数据内容, 也不再依赖调用顺序。dtype 固定为 int(0/1 两值), 而非布尔或浮点, 便于直接进 Stata `.dta` 作为二值控制/交互变量或分组变量使用。

阈值 0.5 是研究者的固定判读切点而非估计量, 与 export.py 内部另一处仅供人工日志读取、不落盘的判读带(mean<0.50 判"置信度偏低"、0.50–0.70 判"中等"、≥0.70 判"较高")共用同一 0.5 分割点语义, 但 low_conf_flag 只保留了"低于 0.5"这一个粗粒度切面, 更细的三档判读只出现在运行日志文本里, 不会物化为面板列。需要强调的是, 该列不是任何三轨(full/ctx/ss)测度族的一员, 也不参与 co-primary 双轨嵌入或消融梯子体系, 是单一无后缀的诊断标量, 不存在"互为稳健性、就 identified 并排"的多变体口径问题; 使用者若想追问不同轨道下分类置信度的差异, 应转向 avg_category_confidence_full / avg_category_confidence_ctx 这两个上游列本身(它们各自锚定于 full 全文轨与 ctx 实体窗口轨, 是两个独立聚合口径, 而非该家族的一部分)。

【文献定位】

分类器输出的置信度分数是否真实反映其正确概率, 是机器学习校准(calibration)文献的核心问题。Niculescu-Mizil & Caruana (2005) 系统比较了多种监督学习方法输出概率的校准质量, 指出很多"看似高置信度"的判别式模型分数并不天然对应真实后验概率, 需要额外的校准步骤(如 Platt scaling、等张回归)才能被当作可靠的置信度使用; 这一发现为本列"不能默认 LLM 吐出的置信度分数就是可信概率, 必须设阈值做粗粒度质量分层"的工程实践提供了方法学背景。更晚近地, Geng 等 (2024) 对大语言模型的置信度估计与校准做了系统综述, 指出 LLM 生成式判别任务(包括分类式 prompting)中的置信度信号存在系统性偏差与厂商/模型异质性, 呼应了本项目采用三家 LLM 投票、并对置信度均值设定阈值筛查而非直接信任单一模型置信度分数的做法。

在应用金融文献层面, Chen 等 (2022, Journal of Financial Economics) 关于银行信息透明度与存款流的研究提醒我们: 当测度构造依赖对定性文本信号的分类判定时, 分类噪声本身可能与银行特征(规模、上市地位、信息环境)系统相关, 从而产生测度误差的非随机性, 这正是本列存在的意义——它不假设分类噪声是均匀分布的白噪声, 而是把"哪些银行-年份的分类结果更值得怀疑"显式标记出来供研究者事后检验或分组。Aguirregabiria 等 (2025, American Economic Review) 在银行分支网络与信贷可得性的研究中广泛使用了多重稳健性分组与样本质量筛查设计, 这类"先标记可疑观测、再做敏感性对比"的研究规范与 low_conf_flag 的用途高度一致。此外, Simmons 等 (2011) 关于"未披露的灵活性"如何制造虚假显著性的方法学警示, 从更宏观的角度支持了本项目在面板层面显式披露分类置信度诊断列、而非把分类噪声悄悄吞掉的设计哲学: 任何依赖 tech_frac/app_frac 等分类衍生比例做因果推断的下游分析, 都应当把 low_conf_flag 作为敏感性检验的候选分组变量或控制变量, 以证明主结论不是被少数分类噪声较大的银行-年份观测所驱动。 在方法学邻近文献中, Wen 等 (2025) 对大语言模型的弃答 (abstention) 研究做了系统综述, 从 query、model 与 human values 三个视角归纳了识别并特殊处理低把握输出的方法谱系、基准与评估指标; 须说明的是本项目并不实施弃答——模型始终作答, low_conf_flag 只是在面板导出层对事后置信度取固定阈值的哑变量, 故该综述仅作为"低置信输出应被显式识别与特殊处理而非静默采纳"这一一般性思路的背景参考, 并非本列做法的方法学出处, 阈值 0.5 亦系研究者选择而非原文推荐值, 而缺失行按 NaN<0.5 判否置 0 的语义更在原文覆盖范围之外。Gligoric、Zrnic、Lee、Candes 与 Jurafsky (2025) 提出 confidence-driven inference, 以 LLM 自报置信度决定哪些样本值得付费人工复标, 并给出统计有效的点估计与置信区间, 实证表明低置信 LLM 标注在恰当处理下仍可支撑可信结论; 该文支撑的是"把逐篇置信度当作可用统计信息而非一律丢弃"这一层, 但其有效推断依赖配套的人工标注子样本作为 ground truth, 本项目并无此人工回路, 置信度仅用于打分与阈值标记, 且本项目的 confidence 已经三家投票的一致/分歧调整 (一致时上调、分歧时折减), 与原文的单模型置信度口径不同, 故不得据以宣称本列具备该文的推断有效性。
## VAR: low_conf_flag

【变体差分】

本家族仅含单一列 low_conf_flag, 不存在同家族内的轨道/模型/权重/滞后差分对象, 因此本节聚焦阐明该列与相邻测度族之间的构念边界, 以及使用该列时需要注意的口径细节。

首先要明确它与 avg_category_confidence 及其分轨版本 avg_category_confidence_full/avg_category_confidence_ctx 的关系: 后三者是连续型(理论区间 [0,1])的置信度均值统计量, 由 encode.py 在面板聚合阶段对 article×bank 层级的 category_confidence_full/category_confidence_ctx 按 (target_bank, year) 取算术平均得到; 而 low_conf_flag 是对无后缀口径 avg_category_confidence(优先取 avg_category_confidence_full 别名, 缺失时回退兼容 legacy 裸名 category_confidence 聚合结果)应用 0.5 阈值后的二值化衍生列, 属于典型的"连续测度→诊断哑变量"降维操作, 信息量严格弱于原连续列, 使用时若不需要二值分组、只需要连续置信度水平作解释变量或控制变量, 应直接使用 avg_category_confidence 或其分轨版本, 而非本列。

其次要明确该列与情感/态度类测度族的边界: low_conf_flag 反映的是 LLM 在"底层技术 vs. 应用场景"这一分类维度(locus, 呼应 P4 paper 的 Gomber (2018) 理论框架)上的判定置信度, 与情感极性(tone, 呼应 P1 paper)、实质性(substantiveness, 呼应 P3 paper 的 W&Z 框架)、协作模式(collab_mode, 呼应 P5 paper 的 Chesbrough 开放式创新框架)等其他分类/情感维度的置信度是彼此独立的量, 不应混淆或相加。当前面板中只有 locus 维度的置信度诊断被物化为面板级哑变量, 其余维度若有类似质量诊断需求, 需在各自维度的专属分析中另行构造, 不由本列代理。

再者, 因为该列 NaN 值在阈值比较后被无条件映射为 0, 使用者在解读"low_conf_flag=0"时必须区分两种截然不同的底层情形: 一是该 bank-year 确实拥有足够多篇报道且分类置信度均值确实 ≥0.5(真正的"高置信度"); 二是该 bank-year 完全没有可用的分类置信度输入(avg_category_confidence 本身为 NaN, 通常对应该银行该年零报道或零 LLM 有效分类样本), 此时 low_conf_flag=0 只是数值比较的技术性副产品, 并不代表分类质量真的可靠。研究者若要严谨区分这两种情形, 应联合参照 n_articles_llm_valid(该行是否有正的报道计数)或直接检查 avg_category_confidence 是否为缺失值, 而不能单独依赖 low_conf_flag=0 就断定分类质量良好; 这一"0 值二义性"是使用该哑变量时最容易被忽视的陷阱, 也是本列被定位为粗粒度诊断/稳健性筛查工具、而非精确构念测度的核心原因。

最后从口径演进角度看, 该列的物化时点被刻意从"诊断阶段(log_diagnostics)有条件创建"改为"导出阶段(export_panel)无条件创建", 目的是保证面板 schema(列集合)不随具体一次运行的数据内容(比如某次试跑样本中置信度全为 NaN)而变化, 只取决于代码路径本身。这意味着即便在开发/测试环境的小样本(如早期试跑 T=2 数据)下 avg_category_confidence 大面积缺失, low_conf_flag 列依然会稳定出现在导出的 parquet/dta 中(全部或几乎全部取值为 0), 这是预期的 by-design 行为而非缺陷; 生产全量语料(T=19, 覆盖 2007–2025 年)下随着分类置信度信号更充分地就位, 该列的 1/0 分布会更真实地反映跨银行-年度的分类不确定性差异。
<!-- rendered-citations:begin -->
Aguirregabiria, V., Clark, R., & Wang, H. (2025). The geographic flow of bank funding and access to credit: Branch networks, synergies, and local competition. American Economic Review, 115(6), 1818-1856. https://doi.org/10.1257/aer.20200374
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I. (2024). A survey of confidence estimation and calibration in large language models. Proceedings of NAACL-HLT 2024 No. 6577-6595 [Working Paper]. https://doi.org/10.18653/v1/2024.naacl-long.366
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML) No. 625-632 [Working Paper]. https://doi.org/10.1145/1102351.1102430
Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). False-positive psychology: Undisclosed flexibility in data collection and analysis allows presenting anything as significant. Psychological Science, 22(11), 1359-1366. https://doi.org/10.1177/0956797611417632
Wen, B., Yao, J., Feng, S., Xu, C., Tsvetkov, Y., Howe, B., & Wang, L. L. (2025). Know Your Limits: A Survey of Abstention in Large Language Models. Transactions of the Association for Computational Linguistics, 13, 529-556. https://doi.org/10.1162/tacl_a_00754
Gligoric, K., Zrnic, T., Lee, C., Candes, E., & Jurafsky, D. (2025). Can Unconfident LLM Annotations Be Used for Confident Conclusions? Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), 3514-3533. https://doi.org/10.18653/v1/2025.naacl-long.179
<!-- rendered-citations:end -->
