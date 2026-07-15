---
family_id: LB006
columns:
- known_limitations_summary_conceptual
unit: 概念性说明, 无独立数值量纲
formula: "无公式; 十二条局限逐条为观察性陈述, 部分附带稳健工具指引(如短简称误匹配对应 n_docs_longhit 稳健列)"
producer: company_listed_bank/data/company_bank_cooc_panel_codebook.md 第七章(手工维护, 随各阶段实测更新)
upstream:
- WP3_R3-2 分层抽样核验结果 (短简称误匹配比例来源)
- news_process stage 13 共现硬过滤日志 (语料宇宙边界来源)
citations:
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: "Media bias in China"
  venue: American Economic Review
  vol: 108
  issue: 9
  pages_or_artno: 2442-2476
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: 53
  issue: 2
  pages_or_artno: 405-459
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: "What drives media slant? Evidence from U.S. daily newspapers"
  venue: Econometrica
  vol: 78
  issue: 1
  pages_or_artno: 35-71
- doi: 10.1214/24-STS939
  type: journal
  authors: Kamat, G., & Gutman, R.
  year: 2026
  title: "Analysis of linked files: A missing data perspective"
  venue: Statistical Science
  vol: 41
  issue: 1
  pages_or_artno: ""
---

## CORE

本家族是主面板已知局限清单的独立展开长文, 覆盖十二条观察性陈述背后的方法论根据与应对建议, 目的是让使用者在解读面板结果前充分理解数据构造过程中不可完全消除的系统性偏差来源。这些局限并非本项目实施缺陷, 而是大规模自动化文本挖掘与实体匹配任务的结构性特征, 在媒体与文本数据的实证研究文献中普遍存在。

短简称误匹配与名录稿灌水两条局限共同指向语料噪声问题: 短字符公司简称容易与其他实体或常见词语发生字面重合造成假阳性, 而部分报道属于批量刊发的企业名录稿而非实质性新闻, 会造成计数虚高。本项目对前者提供了基于变体长度的稳健计数列作为应对工具, 对后者则刻意不设强制剔除阈值, 而是把富集度诊断信息写入日志供使用者自行判断, 这一处理方式呼应了媒体偏差研究中对样本选择透明度的要求, 即报告诊断信息而非隐藏式地单方面裁剪样本。variant 子串双计与拉丁字母大小写敏感两条局限属于匹配算法本身的保守设计选择, 前者是为了不遗漏任何可能的真实提及而接受适度的重复计数风险, 后者则反映出中文语境下英文缩写大小写规范不统一的现实。语料宇宙边界的局限提醒使用者, 全部计数均建立在银行金融科技报道这一经过硬过滤的子语料之上, 而非全部新闻的无条件全集, 这一边界设定本身即是一种样本选择, 与政治敏感信息披露研究中强调的样本框架界定同理, 需要在解读前明确声明。权重内生性与前瞻偏差两条局限则提示使用者在做因果推断时须格外谨慎, 权重来源于观测到的关系强度而非随机分配, 语言模型标注也存在训练语料的时间边界, 这类问题的一般性应对框架可参照缺失数据与链接偏差文献中反复强调的敏感性分析原则, 通过词典与传统机器学习方法构造弱信号对照通道来交叉验证语言模型标注的稳健性。

十二条局限清单的另一重价值在于为使用者提供了一份优先级排序参考, 而非要求对每一条局限都投入同等的稳健性检验精力。以受影响样本占比与对最终结论方向性偏误的潜在幅度两个维度做粗略排序, 语料宇宙边界与权重内生性两条通常应放在最优先审视的位置, 因为二者直接关系到因果解释的有效性边界, 而非仅仅是测量精度层面的噪声问题; 短简称误匹配与 variant 子串双计两条虽然影响样本量, 但由于稳健计数列已提供直接的应对工具, 边际审视成本较低。局限清单的存在本身也反映出本项目在方法论披露上采取的一种保守立场, 即宁可在文档层面主动罗列尚未完全解决的问题, 也不倾向于通过隐藏或淡化处理制造数据完美无瑕的错觉, 这一立场与近年实证社会科学领域对研究透明度日益提高的期待相一致, 越来越多的期刊与审稿流程要求作者明确区分测量误差、样本选择与识别假设三个层次的局限, 而非笼统地在结论部分做一句"存在局限"的免责声明。使用者在引用本面板做实证研究时, 建议至少针对与自身研究问题最相关的两到三条局限做专门的稳健性附录说明, 例如若研究问题涉及金融科技渗透率的时间趋势, 则应重点交代语料宇宙边界与前瞻偏差两条局限对趋势估计可能带来的影响方向。

<!-- rendered-citations:begin -->
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Kamat, G., & Gutman, R. (2026). Analysis of linked files: A missing data perspective. Statistical Science, 41(1). https://doi.org/10.1214/24-STS939
<!-- rendered-citations:end -->
