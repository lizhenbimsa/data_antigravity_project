---
family_id: F331
columns:
- hidden_adopt_int_p75
- hidden_adopt_int_p75_ctx
- hidden_adopt_int_p75_ss
unit: 篇均占比 (bank-year 内 Hidden 象限文章数 / 已测量文章数, ∈[0,1] 无量纲比率)
formula: 'groupby(target_bank, year) 上 mean(_is_hidden_int_p75{track}); 逐篇指示
  _is_hidden = (fintech_intensity_score{track} < 年度P75分位) AND (policy_cosine_sim{track}
  >= 年度P75分位), 仅 sim/freq 双双 notna 的文章参与分类, 其余记 NaN 后被 groupby(''mean'')
  自动跳过 (分母 = 该 bank-year 内已测量篇数, 而非全部报道篇数)'
producer: pipeline\panel\runner.py (`_classify_policy_quadrants` + 四象限聚合循环, runner.py:L312-335,
  L1978-2099)
upstream:
- 15_fintech_intensity.parquet (fintech_intensity_score{track}, TF-IDF × SIF 加权金科强度)
- 16_article_policy_alignment.parquet (policy_cosine_sim{track}, 文章-政策文本余弦相似度; Distel
  et al. 2026 方法学定位)
- 24_herd_decay.parquet (verified 域 semi-join, 仅 LLM 核验通过的银行金科报道参与分类)
citations:
- doi: 10.1073/pnas.2203150119
  type: journal
  authors: Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans,
    J., et al.
  year: 2022
  title: Observing many researchers using the same data and hypothesis reveals a
    hidden universe of uncertainty
  venue: Proceedings of the National Academy of Sciences
  vol: '119'
  issue: '44'
  pages_or_artno: e2203150119
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: Text-based sentiment analysis in finance – synthesising the existing literature
    and exploring future directions
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: '31'
  issue: '1'
  pages_or_artno: e1549
- doi: 10.1002/ijfe.3105
  type: journal
  authors: Liu, J., Chen, S., Su, F., & Liu, J.
  year: 2025
  title: Digital transformation disclosure and bank loans – an information heterogeneity
    perspective
  venue: International Journal of Finance & Economics
  vol: '30'
  issue: '4'
  pages_or_artno: 4004-4038
- doi: "10.1016/j.frl.2026.109668"
  type: "journal"
  authors: "Chen, M., Zhang, Z., & Liu, Y."
  year: 2026
  title: "Silence in innovation disclosure: More action-less talk innovation and trade credit financing in China"
  venue: "Finance Research Letters"
  vol: "95"
  pages_or_artno: "109668"
- doi: "10.1016/j.rmal.2025.100272"
  type: "journal"
  authors: "Hemelstrand, S., & Inoue, T."
  year: 2025
  title: "Stop splitting hairs: The problems with dichotomizing continuous data in language research"
  venue: "Research Methods in Applied Linguistics"
  vol: "4"
  issue: "3"
  pages_or_artno: "100272"
new_dois: []
---

## CORE

【构念与来源】
本家族属"政策文本对齐四象限"体系 (runner.py `_classify_policy_quadrants`), 用来把每篇银行-金科报道按"金科关键词/强度用得多不多"与"文本和监管政策语义像不像"两条轴, 分到 Token(洗科技)/Hidden(闷声干大事)/Substantive(言行一致)/Irrelevant(不相关) 四个格子里, 再按银行-年聚合成占比。F331 家族对应其中的 Hidden 象限、Track B (int) 词频轴、P75 分位阈值这一组合: hidden_adopt_int_p75 衡量一家银行某年"金科强度测度低于年度 75 分位、但文本与政策语义相似度高于年度 75 分位"的报道占已测量报道的比例。直觉上, 这类报道是银行"做了但没有大肆用金科热词渲染"的报道 — 用词克制、语义却贴近监管政策导向, 与靠堆砌关键词但语义空洞的 Token 象限 (词频高、相似度低) 形成对照, 也与词频和相似度双高的 Substantive 象限区分开。P75 是四象限体系里 {25,50,75} 三档分位阈值梯子中最严格的一档: P50 是项目里通行的中位数分割机制检验基准, P25/P75 是其两翼稳健性检验, 三档阈值下 Hidden 占比的相对排序若一致, 说明"闷声干大事"这一构念不依赖阈值取点 (镜像项目内政治词权重梯度、罕见词频次 cutoff 梯子等阈值敏感性检验的通用写法)。
【方法学与计算】
两条词频轨在 runner.py 里称 Track A (kw, 关键词计数)/Track B (int, 强度加权分数); F331 对应 Track B — 词频侧输入是 stage 15 产出的 fintech_intensity_score (TF-IDF × SIF 加权连续分数, 而非 AC 自动机去重关键词个数), 相似度侧输入是 stage 16 的 policy_cosine_sim (文章嵌入与政策文本嵌入的余弦相似度)。逐篇分类先按年度 (`groupby('year').transform(quantile)`) 分别求 fintech_intensity_score 与 policy_cosine_sim 的 P75 分位阈值 (年度内部计算, 避免跨年通胀/紧缩趋势混入截面比较), 再判定该篇是否"强度低于阈值 且 相似度不低于阈值" — 是则记 1, 否则记 0; 若该篇 sim 或 freq 任一为缺失值 (measured=False, 例如 stage 15/16 优雅早退产生的 NaN), 指示列本身记为 NaN 而非强行归入某一象限, 防止"测量失败"被误读成"低强度"。银行-年聚合用 `groupby(['target_bank','year']).mean()`, pandas 的 mean 默认跳过 NaN, 因此占比的物理分母是该 bank-year 内已测量 (sim、freq 均非 NaN) 的报道篇数, 而非全部留篇报道数; 若某银行某年全部报道都未测量, 该 bank-year 输出 NaN 而不是历史版本曾经出现过的伪零 (v6/F3 修复, 对齐 Allison 2001 关于删除 fillna(0.0) 污染 TWFE 系数的告诫)。分类前还有一道 verified 域 semi-join: 只有经 stage 24 herd_decay (承接 stage 21 三家 LLM 投票核验) 判为"确属银行-金科报道"的文章才进入四象限分类, 与 CLAUDE.md 「留篇门控 = full-only」条款一致 — full 轨的留篇判定 (`llm_verified_full == True`) 决定行宇宙, ctx/ss 轨是该行宇宙子集上的 conditional-on-full 稳健测度, 不单独扩大留篇集合。
【文献定位】
"言行是否一致"这一构念在金融文本分析文献里通常通过对比"关键词曝光度"与"语义/语境贴合度"两个独立维度来刻画: 高词频、低语义贴合常被解读为迎合式的表面化信息披露 (即业界俗称的"洗科技"/cheap talk), 而低词频、高语义贴合则更接近"实质性但低调"的行为模式, 这与文本可读性/语用清晰度文献里区分"表面措辞"与"底层语义"的方法论一脉相承 (Todd, Bowden, & Moshfeghi, 2024, *Intelligent Systems in Accounting, Finance and Management*, 综述文本情感分析方法论时明确区分表层词汇特征与深层语义表征在金融文本上的不同信息含量)。四象限所依托的银行数字化转型文本披露与银行信贷/风险后果之间的关联, 与 Liu, Chen, Su, & Liu (2025, *International Journal of Finance & Economics*) 关于数字化转型披露信息异质性影响银行信贷决策的发现同源 — 该文献强调披露文本本身的"信息含量"而非单纯的词频曝光度才是解释银行行为差异的关键, 呼应本家族用相似度轴而非词频轴单独判定"是否真做了"的设计初衷。分位数阈值敏感性检验的做法, 借鉴了项目内其余梯子构念 (政治词权重敏感性、罕见词频次 cutoff 梯子) 共享的稳健性验证逻辑: 单一截断点选择本身带有研究者自由度, 需要通过多档阈值下结论方向一致来支撑构念有效性, 这与 Breznau et al. (2022, *PNAS*) 关于同一数据、同一假设下不同分析选择会产生隐藏的不确定性宇宙的发现相呼应 — 本家族的三档 P25/P50/P75 梯子正是对这种分析者自由度的显式量化与并列披露, 而非隐藏在单一口径背后。
凡涉及 full/ctx/ss 三轨与 int/kw 两条词频轨、{25,50,75} 三档分位阈值梯子的任何组合, 均遵循「各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J」的项目铁律; 三轨的行宇宙统一锚定在 full 轨的留篇门控判定上 (2026-06-29 起 full-only), ctx/ss 轨是该行宇宙子集上的条件测度, 不构成独立扩大的留篇集合。 就 Hidden 象限本身的构念存在性而言, Chen、Zhang 与 Liu (2026) 专门刻画了中国企业「多行动少言说 (more action-less talk)」的创新披露沉默型态, 即实质投入不低而文本声量偏低的一格, 为本家族把「金科强度低于年度分位、政策语义贴合不低于年度分位」视作可独立测量的采纳型态提供了 2026 年中国语境的前沿存在性证据; 迁移边界须诚实标明: 该文测的是上市公司-年层级的年报创新披露与商业信用融资的关系, 其「沉默」由披露文本与专利/研发投入的落差界定, 与本家族「fintech_intensity_score 低于年度 P75 且 policy_cosine_sim 不低于年度 P75」的双分位判据并非同一操作化, 亦无三轨文本与 P25/P50/P75 阈值梯子。方法学层面的反向告诫则须一并直面: Hemelstrand 与 Inoue (2025) 用三组模拟系统论证了把连续变量二分的代价——二分几乎普遍抬高标准误, 进而使显著性检验失准, 并因信息量削减而压低 R² 等效应量——其明确立场是建议不要二分连续数据。本家族把连续的 fintech_intensity_score 与 policy_cosine_sim 按年度 P75 二值化, 正落在该文所告诫的做法之内, 故此处如实披露这一代价: 象限设计换取的是「言—行两维交叉」的可解释离散型态与跨象限占比的可比性, 而非统计效率。⚠ 须特别申明该锚点的引用边界: 该文并未提出「若必须二分则应做多切点敏感性检验」的补救建议, 因此不得援引其为 P25/P50/P75 三档梯子的正当性依据——阈值梯子系本项目自设的稳健性措施; 且该文领域为应用语言学研究方法而非金融/经济学, 其论证针对单变量二分对回归推断的影响, 未涉及双变量交叉的 2×2 象限、逐年滚动分位阈值, 亦未触及本家族的面板聚合与已测量分母口径。
## VAR: hidden_adopt_int_p75

【变体差分】
本列是家族的 full 轨、无 anchor 后缀 (vintage 主轨) 变体, 对应象限判定的两条输入均取自 full 轨: 相似度轴用 policy_cosine_sim (标题+正文全文与政策文本的余弦相似度, stage 16 的 vintage 主锚点, 而非 _allv 全语料静态锚点变体), 词频轴用 fintech_intensity_score (stage 15 全文 TF-IDF × SIF 加权强度)。P75 分位阈值同样在 full 轨的 policy_cosine_sim 与 fintech_intensity_score 各自年度分布上求得, 两个阈值互相独立计算 (不是联合分位)。作为三轨与阈值梯子的共同基准, 该列的行宇宙即整个家族的留篇宇宙来源: full 轨 `llm_verified_full == True` 判定哪些文章进入分类环节, ctx/ss 轨在此基础上做条件测度, 不另行扩大留篇集合。该列与家族内 P25/P50 两档阈值变体 (不在本三列家族内、归属同一四象限体系的姊妹列) 互为稳健性并排, 也与 hidden_adopt_kw_p75 (Track A 关键词计数轴) 互为稳健性并排, 三者均不构成对彼此的替代或主次关系。理解本列数值时须注意分母口径: 它衡量的不是"该银行该年全部报道中 Hidden 象限占比", 而是"该银行该年已成功测量出 policy_cosine_sim 与 fintech_intensity_score 两项指标的报道中 Hidden 象限占比"。若某银行某年因文本过短、嵌入调用失败等原因导致大量报道 sim 或 freq 缺失, 分母会相应收窄, 该 bank-year 的占比数值本身仍是对已测量子样本的无偏估计, 但样本代表性可能弱化; 与项目其余"率/均值/相似度"类面板列 (如 article_sim_mean、fintech_intensity_mean) 共享同一"无数据即未测量"契约 — 全未测量的 bank-year 输出 NaN 而非历史版本曾采用过的伪零填充, 使用者不应把该 NaN 误读为"该年 Hidden 占比为零"。作为家族三轨共同基准, 本列在 anchor 维度上也只对应 vintage 主锚点 (空后缀), 与 policy_cosine_sim_allv 全语料静态锚点驱动的姊妹象限占比列 (不在本三列家族内) 是另一组并排稳健性关系, 阈值/文本轨/锚点三个维度互不纠缠、各自独立切换。

## VAR: hidden_adopt_int_p75_ctx

【变体差分】
本列切至 ctx 轨: 相似度轴改用 policy_cosine_sim_ctx (标题+实体窗口文本与政策文本的余弦相似度), 词频轴优先取 fintech_intensity_score_ctx (若 stage 15 已产出该轨强度分数的同轨变体; 若缺列则代码按 track-agnostic 元数据规则回退复用 full 轨列并在日志披露, 但强度分数本身是逐轨独立计算的连续测度, 生产口径下通常存在同轨变体)。P75 阈值仍在 ctx 轨各自的年度分布上重新求分位, 与 full 轨阈值数值不同、互不通用。ctx 轨的留篇行宇宙由 full 轨门控判定继承 (conditional-on-full), 即参与本列分类的文章集合是 full 轨已判定为"银行-金科报道"的子集, 而非 ctx 轨自身独立判定的留篇集合; ss 回退语义 (无银行∧金科同句共现 → content_ss 退化为全文 body) 与本列无关, 本列只涉及 full/ctx 两轨之间的对照。本列与 full 轨、ss 轨版本互为稳健性并排检验同一 Hidden 象限构念在不同文本窗口下是否保持一致, 三者禁止混入同一 over-identified 模型设定。ctx 轨的实体窗口截取比 full 轨全文更聚焦银行实体周边语境, 理论上应削弱与银行无关的段落对相似度/强度测量的稀释效应; 若 ctx 轨与 full 轨的 Hidden 占比排序在跨银行截面上高度一致, 可视为该构念对文本窗口选择不敏感的证据, 反之若排序显著漂移, 则提示相似度/强度测量本身对窗口截取方式敏感, 应结合 ss 轨三方比对再下结论, 单一文本窗口的结果不构成独立可发表证据。

## VAR: hidden_adopt_int_p75_ss

【变体差分】
本列切至 ss 轨: 相似度轴改用 policy_cosine_sim_ss (标题+银行∧金科同句共现窗口文本与政策文本的余弦相似度), 词频轴优先取同轨变体 fintech_intensity_score_ss (缺列则回退复用 full 轨列, 逻辑与 ctx 轨对称)。ss 轨遵循项目通行的回退语义, 镜像 ctx 轨: 当某篇文章不存在银行与金科词汇的同句共现时, 其 content_ss 退化为全文 body (`ss_is_fallback=True`), 该退化发生在上游 stage 14 文本物化环节, 本列只是消费 stage 15/16 基于该 ss 文本算出的强度分数与相似度, 不改变 fallback 判定本身。P75 阈值同样在 ss 轨年度分布上独立求分位, 数值与 full/ctx 两轨不同。行宇宙同样继承 full 轨的留篇门控判定 (conditional-on-full), ss 轨不单独扩大或收缩留篇集合。本列与 full、ctx 两轨互为稳健性并排, 共同构成 Track B (int) P75 阈值下 Hidden 象限占比的三轨检验组; 三轨、两条词频轨、三档阈值梯子的任意交叉组合均不得混入同一 over-identified Hansen J 设定。ss 轨是三轨中判定标准最严格的一支: 只有银行实体与金科词汇在同一句内共现的文章才会用真正的"同句窗口"文本重新计算相似度与强度, 其余文章一律回退为全文 body (回退语义镜像 ctx 轨的缺列回退, 但触发条件不同 — ctx 缺列回退发生在词频侧无同轨变体时, ss 回退发生在逐篇同句共现判定失败时), 因此 ss 轨的 Hidden 占比样本中相当一部分文章实际消费的是与 full 轨等价的全文测量, 只有同句共现子样本才提供真正独立于 full 轨的增量信息, 解读 ss 轨与 full 轨差异时应留意这一混合样本结构。

<!-- rendered-citations:begin -->
Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al. (2022). Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty. Proceedings of the National Academy of Sciences, 119(44), e2203150119. https://doi.org/10.1073/pnas.2203150119
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance – synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Liu, J., Chen, S., Su, F., & Liu, J. (2025). Digital transformation disclosure and bank loans – an information heterogeneity perspective. International Journal of Finance & Economics, 30(4), 4004-4038. https://doi.org/10.1002/ijfe.3105
Chen, M., Zhang, Z., & Liu, Y. (2026). Silence in innovation disclosure: More action-less talk innovation and trade credit financing in China. Finance Research Letters, 95, 109668. https://doi.org/10.1016/j.frl.2026.109668
Hemelstrand, S., & Inoue, T. (2025). Stop splitting hairs: The problems with dichotomizing continuous data in language research. Research Methods in Applied Linguistics, 4(3), 100272. https://doi.org/10.1016/j.rmal.2025.100272
<!-- rendered-citations:end -->
