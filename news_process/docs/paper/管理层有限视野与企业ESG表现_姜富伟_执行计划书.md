# 管理层有限视野与企业ESG表现 — 项目分析与执行计划书

> **参考论文**: 姜富伟、张芷宁、丁慧 (2024). 管理层有限视野与企业ESG表现. *金融研究*, 2024(09), 134-152.
>
> **项目路径**: `F:\WiseSearch\data_antigravity_project\news_process`
>
> **生成时间**: 2026-04-06

---

## 📋 目录

- [第一部分：基于参考论文的项目分析与诊断报告](#第一部分基于参考论文的项目分析与诊断报告)
  - [1. 范式映射与盲区诊断](#1-范式映射与盲区诊断)
  - [2. 实质性改进项](#2-实质性改进项)
  - [3. 冗余剥离](#3-冗余剥离)
- [第二部分：项目重构与优化执行计划书](#第二部分项目重构与优化执行计划书)
  - [1. 优先级排布](#1-优先级排布)
  - [2. 阶段化执行指令 (SOP)](#2-阶段化执行指令-sop)
  - [3. 风险预案 (Plan B)](#3-风险预案-plan-b)

---

# 第一部分：基于参考论文的项目分析与诊断报告

> **功能**: 学术与逻辑诊断。侧重 Why & What。

---

## 1. 范式映射与盲区诊断

### 1.1 论文核心机制提炼

| 维度 | 姜富伟等 (2024) 的核心范式 | 当前项目对标情况 |
|:---|:---|:---|
| **理论内核** | 动态契约模型：有限视野（高贴现率 γ）→ 管理层操纵短期现金流 → 信息披露质量下降 + 长期资金吸引力降低 → ESG 投入不足 | 项目无理论模型层, 纯实证管道; **不构成落差** — 项目定位为数据工程管道而非理论推演 |
| **核心解释变量** | **Myopia**: 基于 MD&A 文本中"短视词"词频占比 (胡楠等 2021 词库), 辅以中文金融情感词典 (姜富伟等 2021) 和 BERT 模型控制语言情绪干扰 | 项目已部署: ① 姜富伟等 (2021) 中文金融情感词典 (`jiang_2021`); ② 多 BERT 模型 (含 FinBERT-CN); ③ 多 LLM 三角验证. **情感度量维度完整, 但缺少"短视性"维度** |
| **文本分析方法** | 词典法词频统计 + 情绪控制（两步法: 先提取有限视野语义, 再正交化情绪噪声） | 项目将情感和语义集成在同一 CoT prompt 中, **一步到位**; 论文的分步正交化策略是一种可借鉴的稳健性设计 |
| **内生性处理** | IV-2SLS (综合份额移动模拟法); 模糊断点回归 (未预期盈余断点); PSM 1:1 最近邻匹配; 熵平衡 | 项目已有: 29套 Bartik Shift-Share IV + 省/市/经济圈 LOO IV + 交错 DID (DCEP/Sandbox). **IV 储备远超论文**, 无落差 |
| **传导机制** | 信息操纵渠道 (信息披露质量评分 ↓) + 长期资金吸引力渠道 (稳定型机构投资者持仓占比 ↓) | 项目面板中无信息披露质量代理变量、无机构投资者持仓数据. **但这是数据层面的限制, 非管道设计缺陷** |
| **调节效应** | 短期激励 (PPS) 加剧 + 长期激励 (股权) 缓解; 经营压力 (融资约束/行业竞争/EPU) 放大 | 项目面板中已有 DID 政策冲击变量, 但缺少公司治理调节变量. **维持原状 — 属于下游 Stata 回归的变量选择问题, 而非管道设计问题** |

### 1.2 真实落差判定

> [!IMPORTANT]
> **核心诊断结论**: 本项目与论文的核心差异不在于管道架构（项目管道远优于论文单一词频法），而在于**特征维度拓展**和**情感度量的信号分离方法**层面可借鉴论文的两个关键思路。

**落差 A — 前瞻性/短视性语义维度缺少独立指标**

论文使用"短视词库"（胡楠等 2021）从 MD&A 中提取 Myopia 指标，核心洞察是：**"短视性"是独立于"情感极性"的语义维度**。项目当前的情感分析管道（LLM + 词典 + BERT）聚焦情感极性（正面/中性/负面），但已内置前瞻性陈述词汇集（`forward_looking_words`, Li 2010, JAR），并已计算 `forward_looking_ratio` 和 `forward_looking_count`。项目隐含地捕捉了"时间取向"维度，但尚未构建其**对偶指标**——"短视性/回顾性"词频比。

**落差 B — 情感-语义正交化**

论文的一个方法论亮点是：先提取 Myopia 指标（纯语义），然后控制情绪影响（使用姜富伟 2021 词典和 BERT），验证 Myopia 指标在控制情绪后仍显著。这种"正交化"设计为识别策略提供了额外的稳健性。项目当前的 LLM+词典+BERT 三角验证体系已实现了多方法交叉校验, 但可以**借鉴此"信号分离"思想，将情感置信度作为调节变量显式纳入回归**。

---

## 2. 实质性改进项

> **原则**: 宁缺毋滥。仅列出对当前项目有明确边际贡献的改进。

---

### 改进 A：构建"回顾性陈述"对偶词频指标

| 项 | 内容 |
|:---|:---|
| **具体修改** | 在 `config.yaml` 的 `tone_words` 段中新增 `backward_looking_words` 词汇集（与已有 `forward_looking_words` 对偶），并在 `22_tone_words.py` 中计算 `backward_looking_ratio` 和 `backward_looking_count`，最终在面板中生成 `fl_bl_ratio = forward_looking_ratio / (forward_looking_ratio + backward_looking_ratio)` 作为"时间取向指数" |
| **论文依据** | 姜富伟等 (2024) 表2第(5)列: Myopia 系数 -0.29***（1%显著）。论文使用胡楠等 (2021) 短视词库（包含"当前""短期""季度"等回顾/短期词汇）。Li (2010, JAR) Table 1 同时列出了 forward-looking 和 backward-looking 词表 |
| **边际贡献** | ① 为面板增加一个**独立于情感极性的语义维度**，可作为异质性分持变量（"高前瞻性新闻环境下，金融科技情感对银行行为的影响是否更强？"）; ② 与现有 `forward_looking_ratio` 构成闭合的时间取向衡量体系; ③ 实施成本极低（仅需增加词库 + 复用现有计算框架） |

---

### 改进 B：LLM 置信度作为"信号清晰度"调节变量的显式标准化

| 项 | 内容 |
|:---|:---|
| **具体修改** | 在 `43_panel_indicators_geography.py` 的 `standardize_panel_variables()` 中，将已有的 `avg_llm_conf_full/ctx` 纳入 Fama-MacBeth 年度截面 Z-score 标准化，生成 `avg_llm_conf_full_z` / `avg_llm_conf_ctx_z`，并在 Stata 变量标签中明确注释其用途（"Signal Clarity Moderator, c.f. Shapiro et al. 2022, JoE; 姜富伟等 2024 情绪正交化"） |
| **论文依据** | 姜富伟等 (2024) 第四部分(二): "借助中文情感词典和金融大语言模型拓展文本指标，把语言情绪纳入考量范围...在考虑了情绪对于语义的干扰后，Myopia 指标仍然具有信息含量"。Shapiro, Sudhof & Wilson (2022, JoE): 情感度量噪声导致回归系数衰减偏误 (attenuation bias) |
| **边际贡献** | ① 项目已计算 `avg_llm_conf_full/ctx` 但未做截面标准化, 导致该变量在 Fama-MacBeth 框架下直接比较困难; ② 标准化后可直接作为交互项 `Tone × Conf_z` 进入回归, 检验"高置信度样本中情感效应是否更强", 对应论文"情绪正交化"思想的现代化实现; ③ 边际实施成本几乎为零（仅需在现有标准化列表中追加两个变量名） |

---

## 3. 冗余剥离

> [!NOTE]
> **结论: 无冗余模块需要剔除。**
>
> 经逐项审查, 当前项目管道的所有模块均有明确的学术锚定和功能必要性:
> - 29 套 Bartik IV → 过度识别稳健性（远超论文的单一 IV）
> - DID 双政策冲击 (DCEP + Sandbox) → 自然实验识别策略
> - 三角验证 (LLM × 3 + 词典 × 5 + BERT × 5) → 测量误差控制
> - 距离衰减敏感性 (38b) → Sautner et al. (2023, JF) 方法论稳健性
> - Entity Masking (36) + Prompt Sensitivity (39) → LLM 方法论审计
>
> 以上均为顶刊级别的方法论标配, **维持原状**。

---

# 第二部分：项目重构与优化执行计划书

> **功能**: 工程落地指南。侧重 How。

---

## 1. 优先级排布

| 优先级 | 改进项 | 类型 | 实施成本 | 预期收益 | 涉及文件 |
|:---:|:---|:---|:---:|:---:|:---|
| 🟢 P0 | **B. LLM 置信度截面标准化** | 速赢项 | ⭐ | ⭐⭐⭐ | `43_panel_indicators_geography.py` |
| 🟡 P1 | **A. 回顾性陈述词频指标** | 核心攻坚项 | ⭐⭐ | ⭐⭐⭐⭐ | `config.yaml`, `22_tone_words.py`, `41_panel_encode_aggregate.py` |

---

## 2. 阶段化执行指令 (SOP)

### 阶段一：速赢项 — LLM 置信度截面标准化

> **预计工时**: < 30 分钟 | **风险等级**: 🟢 低

#### 动作 1.1: 修改 `43_panel_indicators_geography.py`

在 `standardize_panel_variables()` 函数的标准化变量列表中追加:

```python
# 追加到 vars_to_standardize 列表:
'avg_llm_conf_full',
'avg_llm_conf_ctx',
```

#### 动作 1.2: 修改 `45_panel_export_main.py` 的 Stata 标签

```python
# 追加到 STATA_LABELS 字典:
'avg_llm_conf_full_z':  'LLM Confidence Z-score (Full, Signal Clarity)',
'avg_llm_conf_ctx_z':   'LLM Confidence Z-score (Ctx, Signal Clarity)',
```

#### 交付物标准

- [ ] `avg_llm_conf_full_z` 和 `avg_llm_conf_ctx_z` 出现在最终面板的 `.dta` 文件中
- [ ] 两个变量的年度截面均值 ≈ 0, 标准差 ≈ 1
- [ ] Stata 变量标签正确显示

---

### 阶段二：核心攻坚项 — 回顾性陈述词频指标

> **预计工时**: 2-3 小时 | **风险等级**: 🟡 中

#### 动作 2.1: 构建 `backward_looking_words` 词汇集

在 `config.yaml` → `sentiment_analysis.tone_words` 段中新增:

```yaml
# ── 回顾性陈述词汇集 (Backward-Looking Statement Dictionary) ──
#
# 学术依据:
#   胡楠、薛付婧、王昊楠 (2021). 管理者短视主义影响企业长期投资吗？
#   管理世界, (5), 139-156.
#   → 短视词库中包含大量回顾性/短期性词汇
#
#   Li, F. (2010). Journal of Accounting Research, 48(5), 1049-1102.
#   DOI: 10.1111/j.1475-679X.2010.00382.x
#   → Table 1 同时定义了 forward-looking 和 backward/historical 词表
#
# 对偶设计:
#   与 forward_looking_words 构成闭合的"时间取向"衡量体系:
#   fl_bl_ratio = FL / (FL + BL), ∈ [0, 1]
#   → 0 = 纯回顾, 1 = 纯前瞻, 0.5 = 均衡
backward_looking_words:
  # A. 过去/已完成类
  - "已"
  - "已经"
  - "曾"
  - "曾经"
  - "此前"
  - "过去"
  - "以往"
  - "历史"
  - "历来"
  - "之前"
  - "早前"
  - "既往"
  - "近年来"
  - "近期"
  - "近日"
  - "日前"
  # B. 当前/短期类 (对应胡楠等 2021 短视词库)
  - "当前"
  - "目前"
  - "眼下"
  - "现阶段"
  - "短期"
  - "暂时"
  - "临时"
  - "一时"
  - "当下"
  - "即时"
  # C. 回顾/总结类
  - "回顾"
  - "总结"
  - "盘点"
  - "梳理"
  - "复盘"
  - "上年"
  - "去年"
  - "上一年"
  - "同期"
  - "上季度"
  - "上半年"
  # D. 完成体标记
  - "完成了"
  - "实现了"
  - "达到了"
  - "取得了"
  - "录得"
```

#### 动作 2.2: 修改 `22_tone_words.py`

**2.2a** 在全局常量区（约 L152 附近）追加:

```python
BACKWARD_LOOKING_WORDS: frozenset[str] = frozenset(
    SENTIMENT_PARAMS.get('backward_looking_words', [])
)
```

**2.2b** 新增计算函数:

```python
def _compute_backward_looking_ratio(tokens: list[str]) -> tuple[float, int]:
    """计算回顾性词汇比率 (与 forward_looking_ratio 构成对偶指标)."""
    if not tokens:
        return 0.0, 0
    bl_count = sum(1 for t in tokens if t in BACKWARD_LOOKING_WORDS)
    return bl_count / len(tokens), bl_count
```

**2.2c** 在 `_analyze_single_article()` 函数中, 紧接 `forward_looking_ratio` 计算之后追加:

```python
bl_ratio, bl_count = _compute_backward_looking_ratio(tokens)
result['backward_looking_ratio'] = round(bl_ratio, 6)
result['backward_looking_count'] = bl_count
```

**2.2d** 在 `_inject_custom_dicts_to_jieba()` 中注入多字回顾性词汇:

```python
for word in BACKWARD_LOOKING_WORDS:
    if len(word) > 1:
        jieba.add_word(word)
```

#### 动作 2.3: 修改 `41_panel_encode_aggregate.py`

在 `build_aggregation_dict()` 函数的前瞻性陈述聚合块后追加:

```python
# --- G2. 回顾性陈述 + 时间取向指数
#     (姜富伟等 2024 短视性概念的操作化) ---
agg[f'avg_bl_ratio{track}'] = (f'backward_looking_ratio{track}', 'mean')
agg[f'avg_bl_ratio_std{track}'] = (f'backward_looking_ratio{track}', 'std')
agg[f'sum_bl_count{track}'] = (f'backward_looking_count{track}', 'sum')
```

#### 动作 2.4: 在面板层计算时间取向指数

在 `45_panel_export_main.py` 的综合指标计算步骤中追加:

```python

```

#### 动作 2.5: Stata 标签

```python
'avg_bl_ratio_full':       'Backward-Looking Ratio EW Mean (Full)',
'avg_bl_ratio_ctx':        'Backward-Looking Ratio EW Mean (Ctx)',
```

#### 交付物标准

- [ ] `backward_looking_ratio` 在文章级数据中与 `forward_looking_ratio` 共存
- [ ] Stata `.dta` 文件中新增面板级变量

---

### 阶段三：结论验证与文档更新

> **预计工时**: 1 小时 | **风险等级**: 🟢 低

#### 动作 3.1: 运行管道验证

```bash
# 仅运行词典法模块 + 面板构建
python 22_tone_words.py
python 45_panel_export_main.py
```

#### 动作 3.2: 描述性统计校验

使用 Stata 或 Python 验证新增变量:

```stata
* 描述性统计
sum avg_fl_ratio_full avg_bl_ratio_full, d
```

**验收标准**:
- `avg_llm_conf_full_z` 年度截面均值 ≈ 0

#### 动作 3.3: 更新技术文档

在 `docs/Project_Technical_Manual.md` 中追加新增变量的说明。

---

## 3. 风险预案 (Plan B)

### 风险 1: 回顾性词汇覆盖率过低

| 维度 | 描述 |
|:---|:---|
| **触发条件** | `backward_looking_ratio` 在 > 50% 文章中为 0 |
| **根因分析** | 金融科技新闻天然偏向前瞻性话语, 回顾性表述出现频率低 |
| **Plan B** | ① 放宽词库: 将 "上涨""下跌""增长""下降" 等带有时间暗示的结果性动词纳入; ② 替代指标: 使用 LLM 在 CoT 第二阶段新增一个布尔值 `is_forward_looking`, 直接由模型判断文章时间取向; ③ 最终保底: 仅保留 `forward_looking_ratio` 作为异质性分组变量, 放弃对偶设计 |

### 风险 3: Stata 列名超限

| 维度 | 描述 |
|:---|:---|
| **触发条件** | 新增变量名超过 Stata 32 字符限制 |
| **根因分析** | `backward_looking_ratio` 等列名较长 |
| **Plan B** | 使用缩写: `bl_ratio_full`, `bl_ratio_ctx` |

---

## 附录: 论文方法论与项目对照矩阵

| 论文方法论组件 | 论文实现 | 项目已有等价物 | 是否需要修改 |
|:---|:---|:---|:---:|
| MD&A 文本分析 | 胡楠等 (2021) 短视词库 + 词频统计 | `22_tone_words.py` 词典法引擎 | 词库拓展 |
| 情绪控制 | 姜富伟等 (2021) 词典 + BERT | `jiang_2021` + 5 BERT 模型 + 3 LLM | ✅ **维持原状** |
| 工具变量 | 综合份额移动模拟法 + 模糊 RDD | 29 套 Bartik IV + LOO IV | ✅ **维持原状 (优于论文)** |
| PSM 匹配 | 1:1 最近邻 + 熵平衡 | 未实现 (非管道职责) | ⚪ Stata 端实现 |
| 传导机制 | 信息披露质量 + 长期资金占比 | 无 (数据不可得) | ⚪ 不适用 |
| 调节效应 | PPS 短期激励 / 股权长期激励 | DID 政策冲击 (DCEP/Sandbox) | ✅ **维持原状** |
| 差异性分析 | 融资约束 / 行业竞争 / EPU | 多维 Bartik IV 异质性 | ✅ **维持原状** |
| 前瞻性陈述 | 未涉及 | `forward_looking_ratio` (Li 2010) | 新增对偶指标 |
| LLM 置信度 | 未涉及 | `avg_llm_conf_full/ctx` (Shapiro 2022) | 截面标准化 |

---

> [!CAUTION]
> **严禁在未获得授权的情况下执行本计划中的任何代码修改。** 本计划书仅作为分析诊断和技术方案文档，所有改动须经审批后方可实施。
