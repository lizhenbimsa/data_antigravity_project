# Sentiment Management: AI-based Evidence from Earnings Guidance
## 基于参考论文的项目分析诊断报告与执行计划

> **参考论文**: Berkovitch, J., Israeli, D., & Kasznik, R. (2025). *Sentiment Management: AI-based Evidence from Earnings Guidance*. Stanford GSB Working Paper.
>
> **项目**: `F:\WiseSearch\data_antigravity_project\news_process`
>
> **生成日期**: 2026-04-06

---

# 第一部分：基于参考论文的项目分析与诊断报告

## 1. 范式映射与盲区诊断

### 1.1 论文核心机制提炼

Berkovitch et al. (2025) 的核心贡献是揭示了企业在自愿性披露（earnings guidance）中的**情感管理（Sentiment Management）**行为——即企业战略性地在披露的不同结构部位（标题 vs. 正文、正文前段 vs. 后段）嵌入差异化的情感信号，以利用投资者的有限注意力和信息处理成本来操控市场预期。

**四个核心发现**：

| 编号 | 核心发现 | 论文依据 |
|------|----------|----------|
| F1 | **标题情感放大**：即使正文整体情感为负，企业仍在标题中保持正面情感（TI_SENT > 0 when TXT_SENT < 0） | Table 1 Panel B：当 TXT_SENT = -0.216 时，TI_SENT = 0.031（仍为正） |
| F2 | **正文情感递减**：正面情感集中在正文前段，随段落推进而稳步下降（"前置加载"策略） | Figure 1 & Table 2：SENT_P1 与 SENT_P10 之差可达 0.399 |
| F3 | **标题情感增量信息含量**：标题情感对异常股价收益率（CAR）和交易量有增量解释力 | Table 6：TI_SENT 系数 = 0.022（t = 10.62），控制 TXT_SENT 后仍显著 |
| F4 | **情感管理的截面异质性**：miss analyst forecasts 和低分析师跟踪的企业情感管理更强 | Table 4：Miss 组 TXT_NEG × I(TXT_SENT_NEG) = 0.332（t = 2.598） |

**核心方法论特征**：

1. **FinBERT 分域情感度量**：使用金融领域预训练的 BERT 模型，对标题和正文分别生成 positive/negative/neutral 三维概率，情感得分 = POS - NEG ∈ [-1, 1]
2. **文本分段分析**：将正文按 250 词切割为最多 10 个 portions，逐段计算情感，分析情感梯度
3. **Within-disclosure 研究设计**：在同一篇披露内部比较标题 vs. 正文的情感差异，消除了跨企业/跨时间的混杂因素
4. **ChatGPT-4o 对照实验**：生成 AI 标题作为反事实基准，证明人工标题的情感偏差并非语言学的自然属性

### 1.2 当前项目与论文范式的落差诊断

| 维度 | 论文范式 | 当前项目现状 | 落差严重度 |
|------|----------|-------------|-----------|
| **文本结构粒度** | 标题独立分析 + 正文分 10 段分析，形成 12 个情感得分 | 标题仅用于规则筛选（ad_keywords），不参与情感分析；全文作为一个整体输入模型 | 🔴 **高** |
| **情感度量的分离性** | 独立输出 POS, NEG, NEU 三维概率，情感 = POS - NEG | LLM 输出三分类标签（正面/中性/负面）+ 置信度；BERT 输出三维概率但未按结构位置分析 | 🟡 **中** |
| **披露结构内情感管理检测** | 核心创新：标题 vs. 正文的情感偏差检测，以及正文内部的情感梯度估计 | 完全缺失——项目无任何机制检测"同一篇文章不同位置的情感差异" | 🔴 **高** |
| **投资者反应关联** | 情感得分 → CAR[-1,1] / ATVol 的回归检验 | 项目输出 Bank-Year 面板情感指标，尚未直接输出"标题情感"作为独立变量 | 🟡 **中** |
| **AI 基准对照** | ChatGPT-4o 生成"中性标题"，证明企业标题的情感偏差非自然语言属性 | 项目已有 LLM 三角验证（gpt5nano, gemini3, claude4h），但用于真伪精筛和情感分类，而非用于生成基准标题 | 🟢 **低** |
| **FinBERT 分域模型** | 使用 Araci (2019) 的 FinBERT 模型，输出三维概率 | 项目 `23_tone_berts.py` 已集成 5 个 BERT 模型含 FinBERT 中文版，架构兼容 | 🟢 **低** |

### 1.3 核心盲区总结

> **盲区一（致命级）**：项目将新闻视为"单一整体"进行情感分析，**完全忽略了标题与正文之间的情感差异**——而这正是 Berkovitch et al. (2025) 的核心识别策略。这意味着项目无法捕捉到企业/媒体通过标题"情感放大"来操控读者注意力的行为，从而可能遗漏了情感指标中一个具有显著增量信息含量的维度。

> **盲区二（重要级）**：项目未按正文位置（前段/后段）分析情感梯度。Berkovitch et al. 证明只有前 4 段的情感显著预测股价反应（Table 7 Column 11），后段情感对投资者几乎无影响。这意味着项目的"全文情感"可能被正文后段的低质量信息所稀释。

---

## 2. 实质性改进项（宁缺毋滥）

### 改进 A：标题情感独立度量 → 情感管理指数构建

- **具体修改建议**：在现有 BERT 情感分析流程（`23_tone_berts.py`）中增加对"标题"列的独立情感推理，生成 `TI_POS`, `TI_NEG`, `TI_SENT` 三个指标；在面板聚合阶段（`41_panel_encode_aggregate.py`）新增 `ti_sent_mean`, `ti_sent_std` 等 Bank-Year 级变量。
- **论文依据**：Table 6 Column 3 证明 TI_SENT 系数 = 0.022（t = 10.62），控制 TXT_SENT 后仍显著正相关于 CAR[-1,1]。标题情感的增量信息含量约为正文情感的 30.14%。
- **预期边际贡献**：
  - 构建 `sentiment_management_index = TI_SENT - TXT_SENT`，量化每篇新闻的"情感管理强度"
  - 该指数可作为一个具有理论基础的新控制变量或调节变量——当情感管理强度高时，原始 TXT_SENT 的信息含量可能被"注水"
  - 为下游回归提供一个内生性诊断工具：如果银行金融科技新闻也存在类似的"标题放大"模式，则纯情感指标可能存在系统性偏误

### 改进 B：正文分段情感梯度分析 → 情感前置加载检测

- **具体修改建议**：在 `23_tone_berts.py` 的滑动窗口推理中，额外记录每个窗口的独立情感得分（目前窗口得分已在推理中计算，但仅用于置信度加权池化后丢弃），以"前 N 段均值 vs. 后 N 段均值"构建情感梯度指标。
- **论文依据**：Figure 1 和 Table 2 Panel A 显示，企业 earnings guidance 的情感在正文前段最高，逐段下降至第 10 段时累计降幅可达 0.399。Table 7 Column 11 证明，当所有 10 段情感同时入回归，仅 P1、P2、P4 显著，说明投资者主要处理前段信息。
- **预期边际贡献**：
  - 构建 `tone_gradient = SENT_front_half - SENT_back_half`，检测新闻是否存在"前正后负"的情感前置加载模式
  - 与论文 WSJ 对照组（Figure 2）类似，可用媒体新闻与银行自有公告进行对比，验证情感梯度是否为媒体自有行为

### 改进 C：标题凸显度（Salience）控制变量

- **具体修改建议**：借鉴 Huang, Nekrasov & Teoh (2018) 的标题凸显度指标（标题中数字的数量，截断为 3），在 `22_tone_words.py` 或 `41_panel_encode_aggregate.py` 中新增 `headline_salience` 变量。
- **论文依据**：Table 10 证明，在控制 TI_SENT 后，headline salience 不再显著（Column 3: TI_Salience 系数不显著），说明 FinBERT 情感度量支配了凸显度度量。但在不控制 TI_SENT 时，salience 仍显著（Column 1），因此作为稳健性检验的控制变量仍有价值。
- **预期边际贡献**：提供一个低成本的稳健性对照——如果项目的标题情感指标在控制 salience 后仍显著，则说明情感度量确实超越了简单的"标题含数字量"。

---

## 3. 冗余剥离

经诊断，当前项目**不存在需要因本论文而剔除的模块**。理由如下：

- 项目的三层情感分析架构（LLM + 词典 + BERT）符合学术三角验证标准，论文并未否定词典法的价值
- 项目的双轨模式（全文 _full + 上下文片段 _ctx）与论文的"分段分析"思路互补而非冲突
- BERT 滑动窗口机制（`23_tone_berts.py`）已为实施改进 B 提供了技术基础设施，无需推翻重建

> **结论：维持现状**——当前架构无需裁剪，仅需**增量扩展**标题维度和分段维度的输出。

---

# 第二部分：项目重构与优化执行计划书

## 1. 优先级排布

| 改进项 | 实施成本 | 预期收益 | 分类 |
|--------|----------|----------|------|
| **A. 标题情感独立度量** | 🟢 低（BERT 引擎已就绪，仅需复用推理对标题列单独跑一轮） | 🔴 高（增量信息含量约 30%，论文 Table 6 强证据） | **速赢项 (Quick Win)** |
| **C. 标题凸显度控制变量** | 🟢 极低（纯 regex 数字计数，~10 行代码） | 🟡 中（Huang et al. 2018 对照用） | **速赢项 (Quick Win)** |
| **B. 正文分段情感梯度** | 🟡 中（需修改 BERT 引擎返回逐窗口得分，修改聚合逻辑） | 🟡 中（仅当研究方向涉及"who writes the news"时高价值） | **核心攻坚项** |

---

## 2. 阶段化执行指令 (SOP)

### 阶段一：标题情感独立度量 + 凸显度变量（速赢项）

#### 任务 1.1：`23_tone_berts.py` 新增标题轨道推理

**核心动作**：

1. 在 `main()` 函数中，除现有的 `content_full_list` 和 `content_ctx_list` 外，新增第三条轨道 `title_list`：
   ```python
   title_list = df['标题'].fillna('').astype(str).tolist()
   ```

2. 调用已有的 `process_all_models(df, engine, title_list)` 生成 `output_title`

3. 将标题推理结果以 `_title` 后缀写入 DataFrame：
   ```python
   for mc in MODEL_CONFIGS:
       sn = mc['short_name']
       if sn in output_title:
           for col_name, col_data in output_title[sn]['columns'].items():
               df[f"{col_name}_title"] = col_data
   ```

**交付物标准**：
- 输出 Parquet 包含 `{model}_正面_title`, `{model}_负面_title`, `{model}_label_title` 列
- 日志输出标题轨道的情感分布统计

#### 任务 1.2：篇章级情感管理指数计算

**核心动作**：

在 `41_panel_encode_aggregate.py` 的 `encode_sentiment()` 函数中新增：

```python
# --- 标题情感管理指数 (Berkovitch et al. 2025) ---
for bert_model in BERT_MODELS:
    pos_title = f'{bert_model}_正面_title'
    neg_title = f'{bert_model}_负面_title'
    pos_full = f'{bert_model}_正面_full'
    neg_full = f'{bert_model}_负面_full'
    
    if all(c in df.columns for c in [pos_title, neg_title, pos_full, neg_full]):
        # TI_SENT = TI_POS - TI_NEG
        df[f'{bert_model}_ti_sent'] = df[pos_title] - df[neg_title]
        # TXT_SENT = TXT_POS - TXT_NEG (全文)
        df[f'{bert_model}_txt_sent'] = df[pos_full] - df[neg_full]
        # Sentiment Management Index = TI_SENT - TXT_SENT
        df[f'{bert_model}_sent_mgmt'] = (
            df[f'{bert_model}_ti_sent'] - df[f'{bert_model}_txt_sent']
        )
```

**交付物标准**：
- 篇章级包含 `{model}_ti_sent`, `{model}_txt_sent`, `{model}_sent_mgmt` 列
- `sent_mgmt > 0` 表示标题情感高于正文（"情感放大"）
- `sent_mgmt < 0` 表示标题情感低于正文（"情感压制"或客观标题）

#### 任务 1.3：标题凸显度变量

**核心动作**：

在 `22_tone_words.py` 的 `_analyze_single_article()` 函数（或新建一个标题分析函数中）新增：

```python
import re

def compute_headline_salience(title: str) -> int:
    """标题凸显度: 标题中数字的数量, 截断为 3。
    
    学术依据:
      Huang, X., Nekrasov, A., & Teoh, S.H. (2018).
      Headline salience, managerial opportunism, and over-
      and under-reactions to earnings.
      The Accounting Review, 93(6), 231-255.
    """
    if not isinstance(title, str):
        return 0
    # 匹配连续数字序列（含小数、百分比中的数字）
    numbers = re.findall(r'\d+\.?\d*', title)
    return min(len(numbers), 3)
```

**交付物标准**：
- 篇章级包含 `headline_salience ∈ {0, 1, 2, 3}` 列
- Bank-Year 面板包含 `avg_headline_salience` 聚合列

#### 任务 1.4：面板聚合扩展

**核心动作**：

在 `41_panel_encode_aggregate.py` 的 `build_aggregation_dict()` 中新增：

```python
# --- K. 标题情感 & 情感管理指数 (Berkovitch et al. 2025) ---
for bert_model in BERT_MODELS:
    agg[f'{bert_model}_ti_sent_mean'] = (f'{bert_model}_ti_sent', 'mean')
    agg[f'{bert_model}_ti_sent_std'] = (f'{bert_model}_ti_sent', 'std')
    agg[f'{bert_model}_sent_mgmt_mean'] = (f'{bert_model}_sent_mgmt', 'mean')
    agg[f'{bert_model}_sent_mgmt_std'] = (f'{bert_model}_sent_mgmt', 'std')

# --- L. 标题凸显度 (Huang et al. 2018) ---
agg['avg_headline_salience'] = ('headline_salience', 'mean')
```

**交付物标准**：
- Bank-Year 面板包含 BERT 模型级的标题情感均值/标准差
- Bank-Year 面板包含情感管理指数均值/标准差

---

### 阶段二：正文分段情感梯度分析（核心攻坚项）

#### 任务 2.1：BERT 引擎返回逐窗口情感得分

**核心动作**：

修改 `MultiModelSentimentEngine.run_all_models()` 的返回结构，在现有的 `label`, `probabilities`, `num_windows` 之外，新增 `per_window_probs` 字段：

```python
results.append({
    'label': label_map.get(predicted_idx, f"类别{predicted_idx}"),
    'probabilities': {...},
    'num_windows': e - s,
    'per_window_probs': [  # 新增：每个窗口的独立概率
        {ln: round(probs_per_window[w][idx].item(), 4)
         for idx, ln in label_map.items()}
        for w in range(e - s)
    ],
})
```

**交付物标准**：
- `per_window_probs` 为列表，长度 = num_windows
- 每个元素为 `{'正面': float, '负面': float, '中性': float}`

#### 任务 2.2：情感梯度指标计算

**核心动作**：

在 `process_all_models()` 返回结果后，在 `main()` 中计算前后半段情感差：

```python
def compute_tone_gradient(per_window_probs: list) -> float:
    """正文情感梯度 = 前半段情感均值 - 后半段情感均值。
    
    正值表示"前正后负"(前置加载)，负值表示"前负后正"。
    """
    n = len(per_window_probs)
    if n < 2:
        return 0.0
    mid = n // 2
    front_sents = [p.get('正面', 0) - p.get('负面', 0) for p in per_window_probs[:mid]]
    back_sents = [p.get('正面', 0) - p.get('负面', 0) for p in per_window_probs[mid:]]
    return np.mean(front_sents) - np.mean(back_sents)
```

**交付物标准**：
- 篇章级包含 `tone_gradient_full`, `tone_gradient_ctx` 列
- 正值 > 0 表示企业/媒体"前置加载"正面信息
- Bank-Year 面板包含 `avg_tone_gradient`, `tone_gradient_std`

#### 任务 2.3：稳健性检验—与媒体类型交叉

**核心动作**：

利用现有的 `媒体类型(中文)` 字段，将新闻按来源类型分组（如"报纸"/"网络"/"通讯社"），比较不同媒体类型的情感梯度模式。参照论文对 WSJ 文章的分析（Figure 2），验证情感前置加载是否为特定来源独有。

**交付物标准**：
- 面板增加按媒体类型分层的情感梯度指标
- 日志输出各媒体类型的平均情感梯度对比

---

### 阶段三：结论重构

#### 任务 3.1：变量文档更新

**核心动作**：

在 `docs/Project_Technical_Manual.md` 和面板数据字典中新增以下变量定义：

| 变量名 | 定义 | 学术依据 |
|--------|------|----------|
| `{model}_ti_sent` | 标题情感得分 = 标题正面概率 - 标题负面概率 | Berkovitch et al. (2025), Eq. (1) |
| `{model}_txt_sent` | 全文情感得分 = 全文正面概率 - 全文负面概率 | Berkovitch et al. (2025), Eq. (3) |
| `{model}_sent_mgmt` | 情感管理指数 = TI_SENT - TXT_SENT | Berkovitch et al. (2025), §4-5 |
| `headline_salience` | 标题凸显度 = min(标题中数字序列数, 3) | Huang et al. (2018, TAR) |
| `tone_gradient` | 情感梯度 = 前半段情感均值 - 后半段情感均值 | Berkovitch et al. (2025), Figure 1 |

#### 任务 3.2：诊断脚本——情感管理模式检测

**核心动作**：

新建 `34b_sentiment_management_audit.py`（或并入现有 `34_tone_validation.py`），实现以下诊断：

1. **标题放大检测**：统计 `TI_SENT > 0 AND TXT_SENT < 0` 的比例（论文: Panel B 显示负面信息中标题仍为正面）
2. **情感梯度分布**：绘制 `tone_gradient` 的直方图，与论文 Figure 1 对标
3. **截面异质性**：按银行规模/分析师跟踪分组，检验情感管理强度的差异

---

## 3. 风险预案 (Plan B)

### 风险 1：标题文本过短导致 BERT 推理不稳定

**预判**：中文新闻标题通常 10-30 字（约 15-50 tokens），远低于 BERT 的 512 token 上限。FinBERT 在极短文本上的情感概率分布可能高度集中于 neutral。

**替代方案**：
- 方案 A（首选）：使用 LLM 对标题单独进行情感分析。在 `21_tone_llms.py` 的 Prompt 中增加一个独立的"标题情感"字段——成本极低，因为标题文本极短
- 方案 B：将标题与正文第一句拼接（约 50-100 字）再送入 BERT，模拟论文中投资者"先读标题再扫前文"的信息处理行为

### 风险 2：分段分析时窗口划分与论文不一致

**预判**：论文按 250 英文词切割（对应 512 tokens），项目处理中文文本，jieba 分词后的 token 数与英文不同。现有滑动窗口按 `max_length - 2 = 510 tokens` 切割，步长 50%。

**替代方案**：
- 维持现有滑动窗口机制不变（项目已按 token 级别切割）
- 在计算情感梯度时，直接使用滑动窗口的索引顺序（第 1 个窗口 = 前段，最后一个窗口 = 后段），无需严格对齐英文 250 词的切割方式
- 论文的核心洞察是**相对位置的情感差异**（前段 vs. 后段），而非绝对的 250 词粒度

### 风险 3：中国新闻标题与美国 earnings guidance 标题的结构差异

**预判**：论文研究的是企业自行发布的 press release 标题（企业有完全控制权），而本项目的新闻标题由媒体撰写，企业对标题的控制力较弱。这可能导致"情感管理"的agent不同（企业 vs. 媒体）。

**替代方案**：
- 将本项目的"情感管理指数"重新解读为**"媒体情感框架效应"**而非"企业情感管理"——媒体通过标题框架影响读者（投资者）对金融科技新闻的第一印象
- 这一视角同样具有学术贡献——Huang et al. (2018, TAR) 的"headline salience"假说正是基于媒体标题的投资者反应
- 在论文写作时，可将发现表述为："与 Berkovitch et al. (2025) 发现企业管理 press release 标题情感一致，我们发现中国金融媒体在银行金融科技新闻标题中也存在类似的情感放大模式"

---

## 附录：关键参考文献

1. Berkovitch, J., Israeli, D., & Kasznik, R. (2025). Sentiment Management: AI-based Evidence from Earnings Guidance. Stanford GSB Working Paper.
2. Araci, D. (2019). FinBERT: Financial Sentiment Analysis with Pre-trained Language Models. arXiv:1908.10063.
3. Huang, A.H., Wang, H., & Yang, Y. (2023). FinBERT: A Large Language Model for Extracting Information from Financial Text. *Contemporary Accounting Research*, 40(2), 806-841.
4. Huang, X., Nekrasov, A., & Teoh, S.H. (2018). Headline Salience, Managerial Opportunism, and Over- and Under-reactions to Earnings. *The Accounting Review*, 93(6), 231-255.
5. Loughran, T. & McDonald, B. (2011). When is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. *The Journal of Finance*, 66(1), 35-65.
6. Cao, S., Jiang, W., Yang, B., & Zhang, A.L. (2023). How to Talk When a Machine is Listening: Corporate Disclosure in the Age of AI. *The Review of Financial Studies*, 36(9), 3603-3642.
