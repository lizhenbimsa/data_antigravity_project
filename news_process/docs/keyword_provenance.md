# 金融科技关键词词典来源文档 (G-04)

> 本文档系统记录 `fintech_dict.json` 中 1,506 个金融科技关键词的构建方法论、
> 生产流程、质量验证及学术引用，满足顶级期刊审稿人对"关键词选择透明性"的要求。

---

## 一、词典构建方法论

### 1.1 方法论概述

本词典采用 **基于大语言模型群体智能 (Swarm Intelligence of LLMs) 的全自动化构建方法**，
而非传统的人工先验或无监督扩展路径。完整方法论详见项目技术论文：

> **《基于大语言模型群体智能的金融科技词典构建：多模型生成与交叉盲审机制》**
> 位于: `LLMs_for_FinTech_dic/FinTech_Dictionary_LLMs_Paper_Final.md`

该方法克服了传统词典构建的三重系统性约束 (Siano, 2025; Wang et al., 2024)：
1. **选择性偏差** — 人工标注受研究者既有知识结构的限制
2. **时效性困境** — 静态词典无法追踪新兴领域的动态术语演化  
3. **假阳性噪音** — 无监督方法 (LDA/Word2Vec) 因纯语境共现引入非领域词汇

### 1.2 三阶段流水线

| 阶段 | 名称 | 输入 | 输出 | 温度设置 |
|------|------|------|------|---------|
| **Phase 1** | 零样本并发生成 (Zero-shot Concurrency Generation) | 结构化 Prompt × 8 模型 × 100 次/模型 | 82,356 个原始词条 | 模型默认温度 (多样性优先) |
| **Phase 2** | 集合迭代精简 (Set-based Evolutionary Reduction) | 82,356 → NFKC 去重 → 超子串降幂 | 4,004 唯一实体 → **2,814 正交词根** | — |
| **Phase 3** | 专家交叉盲审 (Cross-Blind Peer Review) | 2,814 词根 × 8 模型 LLM-as-a-Judge | **1,506 个多数投票通过词** | **T=0** (确定性贪心解码) |

### 1.3 关键数据流

```
82,356 原始词条
    ↓ Unicode NFKC 规范化 + Hash 去重 [O(1)]
4,004 唯一实体
    ↓ 超子串降幂约束算子 [O(N²)]
2,814 正交词根
    ↓ 8 模型交叉盲审 (Batch=100, T=0)
    ↓ 简单多数投票截断 (total_score ≥ 5)
1,506 最终词典 ← fintech_dict.json
```

---

## 二、LLM 模型矩阵

### 2.1 模型配置

依据 **2026 年 2 月 27 日 SuperCLUE 通用大模型榜** (总分 > 60) 筛选，
8 款异构模型覆盖不同参数架构、训练语料及对齐策略，构成多智能体决策网络：

| 编号 | 模型 | 开发机构 | 架构特征 | 系统角色 |
|------|------|---------|---------|---------|
| 01 | Claude-Opus-4.6 | Anthropic | 逻辑对齐特化，安全性约束强 | 高质生成锚点 / 严密交叉复审 |
| 02 | Gemini-3.1-Pro-Preview | Google | 超长检索窗口，知识图谱丰富 | 长尾概念提取 / 交叉前瞻盲审 |
| 03 | Doubao-Seed-2.0-pro-260215 | 字节跳动 | 高并发流量模型底座 | 基础生成节点 / 防偏见兜底 |
| 04 | Claude-Opus-4.5 (20251101) | Anthropic | 上代 Opus 稳定版基座 | 逻辑验证校验池补充 |
| 05 | Gemini-3-Pro-Preview | Google | 通用型 Gemini 分析底座 | 评判算力支撑 |
| 06 | GPT-5.2 | OpenAI | MoE 架构 | 基座生成锚点 / 核心盲审判决 |
| 07 | Kimi-k2.5 | Moonshot | 中文基座优化，长上下文支持 | 中文经济学语料图谱挖掘 |
| 08 | Gemini-3-Flash-Preview | Google | 响应延迟低，高并发吞吐 | 高频生成衍生词特征空间 |

### 2.2 Prompt 工程

**生成阶段 Prompt** (Phase 1)：

```
请生成一个包含约100个中文专业词汇的银行"金融科技"词典。
参考词汇：{金融科技、数字金融、开放银行、监管科技、人工智能、大数据、区块链、云计算、物联网等}
要求：每个词汇应确保简洁、准确且意义明确，涵盖银行"金融科技"的所有关键领域和新兴方向。
格式：必须严格返回一个JSON对象，Key为"keywords"，Value为列表。
```

**盲审阶段 Prompt** (Phase 3)：

```
请逐一判断以下50个词汇是否属于银行"金融科技"领域的专业词汇。
要求：判定属于返回1，不属于返回0。对每个词汇的判定要给出理由，理由字数不多于20字。
格式：严格返回JSON对象，包含'results'数组，每个对象有'keyword'、'score'、'reason'三个键。
```

**设计原理**：
- **定量约束 ("约100个")** — 控制模型发散，引导经验图谱提取
- **结构化 JSON 输出** — 消除自然语言冗余，满足高并发解析
- **凝缩型 CoT ("理由不多于20字")** — 激活因果逻辑链，减少 Lazy Output Defaults
- **伯努利分布转换 ("返回1或0")** — 规避语境模糊，结构化为二元分类矩阵

---

## 三、质量验证

### 3.1 多评估者一致性: Fleiss' Kappa

**Fleiss' Kappa 检验结果** (N=2,814, n=8, k=2)：

| 统计量 | 数值 | 含义 |
|--------|------|------|
| $\bar{P}$ (实际观测一致性) | **0.7596** | 随机抽取一词两模型，75.96% 概率判定一致 |
| $P_e$ (偶然预期一致性) | 0.5176 | 纯随机猜测下的巧合基准线 |
| **Fleiss' κ** | **0.5017** | 位于 Landis & Koch (1977) 中度至实质一致性区间 |
| Z 检验统计量 | > 5.0 | p < 0.0001，拒绝随机共现原假设 |

**解读**：依据 Landis & Koch (1977) 的标尺 (0.41-0.60 = Moderate Agreement)，
κ = 0.5017 在包含海量生僻术语的超高难度纯文本分类中，
**证明了多数投票截断机制能有效分离统计伪特征与弱共识噪音**。

### 3.2 投票分布与分层质量

| 层级 | 得票 | 词数 | 占通过词汇比 | 质量描述 |
|------|------|------|-------------|---------|
| **S层** (核心) | 8票全票共识 | 870 | 57.8% | 最高置信度基础元素 |
| **A层** (高置信) | 6-7票 | 495 | 32.8% | 优质核心 + 可靠派生词汇 |
| **B层** (准入边界) | 5票 | 141 | 9.4% | 多数投票准入边界 |
| *争议区* (剔除) | 0-4票 | 1,308 | — | 未获超半数认可，判定为噪音 |
| **合计通过** | ≥ 5票 | **1,506** | **100%** | — |

### 3.3 梯队质量切片验证

| 层级 | 随机抽取样本 | 模型盲审逻辑反馈 | 结论 |
|------|------------|----------------|------|
| S级 (8票) | 同态加密、隐私计算、联邦学习、分布式账本 | "隐私计算为商业银行安全开放数据孤岛之底层防护架构" | 准确刻画核心属性 |
| A/B级 (5-7票) | 手机终端营运平台、多通道催收、信贷审批RPA | "符合数字技术融入信贷及审核操作边界的营运工具概念" | 反映具体场景应用 |
| 剔除区 (0-1票) | 核心处理器主板调配、C++并行服务器 | "仅属基础IT设施代名，未特指金融垂直业务改良特征" | 通用噪音被有效过滤 |

---

## 四、下游应用中的分类体系

### 4.1 二级分类

词典在 `news_process` 流水线中通过 `utils/canonicalization.py` 的 `canonicalize_topic`
函数进行二级分类 (底层技术 / 应用场景)，用于面板变量 `tech_frac` 的计算。

### 4.2 管道验证模块

| 模块 | 功能 | 验证内容 |
|------|------|---------|
| `31_bank_fintech_threshold.py` | 阈值网格搜索 | MIN_DISTINCT_KEYWORDS 1-10 级敏感性分析 |
| `37_dict_coverage_audit.py` | 词典覆盖率审计 | 五词典逐词匹配率 + 零匹配文章占比 |
| `32_news_llms_human.py` | 人工验证抽样 | 分层随机抽样生成编码任务 |
| `33_news_llms_evaluation.py` | 评估框架 | Cohen's κ + Krippendorff's α + McNemar 检验 |

---

## 五、实施代码与产出文件

### 5.1 核心代码

| 文件 | 功能 |
|------|------|
| `LLMs_for_FinTech_dic/00_LLMs_for_dic.py` | 主脚本：生成 → 精简 → 盲审 → Excel 导出 |
| `LLMs_for_FinTech_dic/config.py` | 模型列表、Prompt 模板、任务参数 |
| `LLMs_for_FinTech_dic/calculate_kappa.py` | Fleiss' Kappa 独立验证计算 |

### 5.2 产出数据

| 文件 | 说明 |
|------|------|
| `LLMs_for_FinTech_dic/data_processed/bank_keywords_20260302_011050.xlsx` | 含"判别-金融科技"Sheet，记录 2,814 词 × 8 模型完整评分矩阵 |
| `news_process/config/fintech_dict.json` | 最终 1,506 词词典 (total_score ≥ 5 截断后) |

---

## 六、参考文献

> 以下文献严格引用自 `LLMs_for_FinTech_dic/FinTech_Dictionary_LLMs_Paper_Final.md`(§6)
> 和 `FinTech_Dictionary_Fleiss_Kappa_Methodology.md`，仅保留与词典构建方法直接相关的核心引用。

### A. 一致性检验方法论基石

1. **Fleiss, J. L. (1971).** "Measuring nominal scale agreement among many raters." *Psychological Bulletin*, 76(5), 378–382. https://doi.org/10.1037/h0031619
   — Fleiss' Kappa 开山之作，多评估者名义尺度一致性的理论基础

2. **Landis, J. R., & Koch, G. G. (1977).** "The measurement of observer agreement for categorical data." *Biometrics*, 33(1), 159-174. https://doi.org/10.2307/2529310
   — Kappa 系数解释标尺 (0.41-0.60 = Moderate Agreement)

3. **Krippendorff, K. (2004).** "Reliability in Content Analysis: Some Common Misconceptions and Recommendations." *Human Communication Research*, 30(3), 411-433. https://doi.org/10.1111/j.1468-2958.2004.tb00738.x
   — 多评议者内容分析中一致性检验的规范框架

### B. LLM-as-a-Judge 科学性

4. **Gilardi, F., Alizadeh, M., & Kubli, M. (2023).** "ChatGPT outperforms crowd-workers for text-annotation tasks." *Proceedings of the National Academy of Sciences (PNAS)*, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
   — LLM 零样本分类准确率超越人类外包工，赋予模型"合法裁判权"

5. **Zheng, L., Chiang, W. L., et al. (2024).** "Judging LLM-as-a-judge with MT-Bench and Chatbot Arena." *Advances in Neural Information Processing Systems (NeurIPS)*, 36. https://doi.org/10.48550/arXiv.2306.05685
   — LLM-as-a-Judge 范式的稳健性实证，跨模型交叉评分能逼近人类专家共识

6. **Brown, T., et al. (2020).** "Language models are few-shot learners." *Advances in Neural Information Processing Systems*, 33, 1877-1901. https://doi.org/10.48550/arXiv.2005.14165
   — GPT-3 零样本泛化能力的基石论文，论证 Prompt 驱动的垂直文本分类合理性

7. **Wei, J., et al. (2022).** "Chain-of-thought prompting elicits reasoning in large language models." *Advances in Neural Information Processing Systems*, 35, 24824-24837. https://doi.org/10.48550/arXiv.2201.11903
   — CoT 提示激活深层因果推理，支撑盲审阶段"理由约束"的有效性

### C. 金融文本分析与词典构建

8. **Loughran, T., & McDonald, B. (2011).** "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks." *The Journal of Finance*, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
   — 金融文本分析领域奠基之作，论证通用词典在金融语境中的严重语义错位

9. **Loughran, T., & McDonald, B. (2016).** "Textual analysis in accounting and finance: A survey." *Journal of Accounting Research*, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
   — 以自建词库为基础的金融文本分析方法学综述

10. **Gentzkow, M., Kelly, B., & Taddy, M. (2019).** "Text as data." *Journal of Economic Literature*, 57(3), 536-567. https://doi.org/10.1257/jel.20181020
    — "Text as Data" 规范化框架，文本分类与阈值敏感性的方法论标准

11. **Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019).** "Firm-level political risk: Measurement and effects." *The Quarterly Journal of Economics*, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
    — 词频统计作为企业级风险暴露测度的 QJE 范例

### D. 金融科技定义与测度

12. **Thakor, A. V. (2020).** "Fintech and banking: What do we know?" *Journal of Financial Intermediation*, 41, 100833. https://doi.org/10.1016/j.jfi.2019.100833
    — 银行业 FinTech 的学术定义框架，本词典的概念边界标准

13. **Gomber, P., et al. (2018).** "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services." *Journal of Management Information Systems*, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
    — 金融科技创新分类体系

14. **Cheng, M., & Qu, Y. (2020).** "Does bank FinTech reduce credit risk? Evidence from China." *Pacific-Basin Finance Journal*, 63, 101398. https://doi.org/10.1016/j.pacfin.2020.101398
    — 中国银行业金融科技关键词频测度的先行研究，本词典为其方法论的代际升维

### E. 文本挖掘与无监督方法局限

15. **Hanley, K. W., & Hoberg, G. (2019).** "Dynamic interpretation of emerging risks in the financial sector." *The Review of Financial Studies*, 32(12), 4543-4603. https://doi.org/10.1093/rfs/hhz057
    — 词嵌入在金融文本特征提取中的应用及过度映射问题

16. **Hoberg, G., & Phillips, G. (2016).** "Text-based network industries and endogenous product differentiation." *Journal of Political Economy*, 124(5), 1423-1465. https://doi.org/10.1086/688176
    — 基于文本的行业分类动态边界划定，支撑自下而上重构词典边界的合理性

17. **Siano, F. (2025).** "The News in Earnings Announcement Disclosures: Capturing Word Context Using LLM Methods." *Management Science*, 71(11). https://doi.org/10.1287/mnsc.2023.0134
    — 静态词表难以应对动态特征词库更新的局限性论证

### F. LLM 在金融分析中的应用

18. **Lopez-Lira, A., & Tang, Y. (2023).** "Can ChatGPT forecast stock price movements? Return predictability and large language models." *Available at SSRN 4412788*. https://doi.org/10.2139/ssrn.4412788
    — LLM 在金融文本情感解读中的预见性实证

19. **Huang, A. H., Wang, H., & Yang, Y. (2023).** "FinBERT: A large language model for extracting information from financial text." *Contemporary Accounting Research*, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
    — 金融专用语言模型的分类优势

20. **de Kok, T. (2025).** "ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research." *Management Science*, (Forthcoming). https://doi.org/10.1287/mnsc.2024.0321
    — 生成式 LLM 在会计研究文本分析中的方法论规范

21. **Gopal, R. D., et al. (2025).** "Inventing with Machines: Generative AI and the Evolving Landscape of IS Research." *Information Systems Research*, 36(4), 1949-1967. https://doi.org/10.1287/isre.2024.0412
    — 多智能体系统统计验证协议控制偏见与假阳性的理论基础

---

## 七、论文表述建议

在论文方法论章节中，可使用以下表述：

> "We construct the FinTech keyword dictionary using a Swarm Intelligence of LLMs
> framework. Eight heterogeneous foundation models (GPT-5.2, Claude Opus 4.6,
> Gemini 3.1 Pro, Kimi-k2.5, etc.) independently generated 82,356 candidate
> terms via zero-shot concurrent sampling. After Unicode normalization, hash
> deduplication, and super-substring inclusive elimination, 2,814 orthogonal
> roots were submitted to a machine cross-blind peer review at temperature T=0.
> Applying a simple majority voting threshold (total_score ≥ 5 out of 8 models),
> we obtain a final dictionary of 1,506 terms with Fleiss' κ = 0.5017
> (Moderate Agreement per Landis & Koch, 1977; Z > 5.0, p < 0.0001),
> of which 870 terms (57.8%) achieved unanimous consensus across all models."
