# 媒体报道文本指标聚合到Stata面板数据 - 完成总结

> **⚠ 历史快照（Stale Snapshot, 2026-05-10 / v1.0 epoch）** — 描述初代 Stata 集成: 16 .do / 1725 indicators / 4,608 rows / 288 banks。v3.x 已迁移到 stage 46 (`pipeline/panel/stata_export.py`)；当前 panel 2,033 列、84×2 实际/目标 500×18。
> **当前权威**：[`STATA_INDICATORS_CATALOG.md`](STATA_INDICATORS_CATALOG.md)（v1.5 / 3,085 行 / 5 轮评审终版，2026-05-19 起为 Stata 列指标穷尽分类说明）。
> **保留原因**：[`项目说明书_简明版.md`](项目说明书_简明版.md) L486 endorse；记录初代 16 .do 实施过程与命名约定来源。

## 项目概述

已成功创建完整的Stata do文件体系，将所有1725个利用媒体报道文本生成计算的指标聚合到Stata面板数据中。

## 创建的文件清单

### 1. Stata Do文件（16个）

**主控文件**
- `stata/99_master.do` - 主控文件，自动执行所有步骤

**变量标签文件**（按指标类型分类）
- `stata/01_label_variables.do` - 基础变量和LLM情感指标
- `stata/02_label_dict_bert.do` - 词典法和BERT情感指标
- `stata/03_label_features.do` - 文本特征和衍生指标
- `stata/04_label_media.do` - 媒体注意力和异质性指标
- `stata/05_label_advanced.do` - 高级文本分析指标
- `stata/06_label_geography.do` - 地理缓冲和区域指标
- `stata/07_label_iv_did.do` - Bartik IV和DID指标
- `stata/08_label_network.do` - 网络指标
- `stata/09_label_strategic.do` - 战略差异度和政策对齐度指标
- `stata/10_label_benefit_token.do` - 社会效益和代币采纳指标
- `stata/11_label_washing_disag.do` - 洗绿和分歧度指标
- `stata/12_label_cater_misc.do` - 迎合指标和其他衍生指标
- `stata/13_label_standardized.do` - 标准化指标
- `stata/14_label_jf_exc.do` - JF系数和排除性指标

**文档**
- `stata/README.md` - 完整使用说明文档

### 2. Python转换脚本

- `scripts/convert_parquet_to_stata.py` - Parquet到Stata格式转换工具

## 涵盖的指标体系

### 核心情感分析指标（约500个）

**LLM情感分析**（阶段21）
- 3个模型：GPT5nano、Gemini3、Grok4.1
- 3个轨道：全文(_full)、上下文(_ctx)、标题(_title)
- 指标类型：离散情感、连续情感、置信度、一致率

**词典情感分析**（阶段22）
- 5本词典：江2021、姚2021、卞2021、杜2022、尤2018
- 包含IDF加权版本

**BERT情感分析**（阶段23）
- 5个模型：FinBERT-CN、FinSent-ZH、Erlangshen、HW2942、FinBERT2
- 输出：正面/负面/中性概率

### 文本特征指标（约100个）

- 句子长度、词汇丰富度(TTR)、每词字符数
- 情感强度、情感标准差
- LLM置信度和一致性指标

### 金融科技指标（约50个）

- 金融科技词汇占比
- 金融科技强度(TF-IDF)
- 技术类vs应用类新闻分类

### 媒体异质性指标（约200个）

- 媒体类型（金融vs综合）
- 媒体层级（中央vs地方）
- 媒体性质（官方vs非官方）
- 市场化程度
- 地理邻近性（本省vs外省、本市vs外市）
- 媒体广度和集中度

### 地理缓冲指标（约80个）

- 4个缓冲区：50km、100km、150km、200km
- AI模仿渗透率
- Leave-One-Out情感指标

### 工具变量和DID指标（约100个）

- Bartik IV（银行类型、规模、金融科技、媒体类型等）
- DID政策冲击（DCEP、监管沙盒、存款保险）
- 事件研究设计

### 网络指标（约150个）

- 银行网络中心度（22个指标）
- 同行网络溢出
- 经纪网络
- LLM同行IV（多个阈值）

### 战略差异度指标（约100个）

- TF-IDF（字符级、词级）
- LDA主题模型
- Sentence Embedding
- Text2Vec稳健性
- 文本连贯性

### 政策对齐度指标（约30个）

- 权威政策相似度（多种方法）
- 政策余弦相似度

### 高级衍生指标（约400个）

- 洗绿指标（多模型）
- 分歧度指标
- 迎合指标
- JF系数
- 排除性指标
- 情感反转
- 社会效益
- 代币采纳

### 加权指标（约200个）

- VW (Value-Weighted): 提及密度加权
- MW (Media Authority-Weighted): 媒体权威性加权
- HW (Herd-Weighted): 跟风衰减加权

### 标准化指标（约100个）

- 所有核心情感指标的Z-score标准化版本

## 使用方法

### 快速开始

```stata
cd "F:\WiseSearch\data_antigravity_project\news_process"
do stata/99_master.do
```

这将自动：
1. 转换parquet为dta格式
2. 加载面板数据
3. 添加所有变量标签
4. 保存为 `40_panel_yearly_labeled.dta`
5. 生成摘要报告

### 手动转换（如果需要）

```bash
# 使用Python脚本转换
python scripts/convert_parquet_to_stata.py
```

然后在Stata中：
```stata
use "data/processed/40_panel_yearly.dta", clear
do stata/01_label_variables.do
do stata/02_label_dict_bert.do
* ... 依次执行其他脚本
```

## 数据结构

- **观测单位**: 银行-年份（bank-year）
- **数据维度**: 4608行 × 1725列
- **面板类型**: 非平衡面板
- **关键变量**: `target_bank`, `year`

## 变量命名规则

### 轨道后缀
- `_full`: 全文轨道
- `_ctx`: 上下文轨道
- `_title`: 标题轨道

### 加权后缀
- `_w` / `_vw`: Value-Weighted
- `_mw`: Media Authority-Weighted
- `_hw`: Herd-Weighted

### 聚合后缀
- `_sum`: 总和
- `_mean` / 无后缀: 均值
- `_std`: 标准差
- `_frac`: 占比
- `_count`: 计数
- `_z`: 标准化

## 使用示例

### 基础回归
```stata
reghdfe outcome llm_vote_tone_full controls, ///
    absorb(target_bank year) cluster(target_bank)
```

### 工具变量
```stata
ivregress 2sls outcome (llm_vote_tone_full = bartik_type_iv_full) ///
    controls, cluster(target_bank)
```

### DID分析
```stata
reghdfe outcome c.dcep_post##c.llm_vote_tone_full controls, ///
    absorb(target_bank year) cluster(target_bank)
```

## 技术特点

1. **完整性**: 涵盖所有1725个文本生成指标
2. **模块化**: 14个独立的标签脚本，便于维护
3. **自动化**: 主控文件一键执行所有步骤
4. **文档化**: 每个变量都有中文标签说明
5. **兼容性**: 支持Stata 14/15/16格式

## 指标来源

所有指标均来自以下pipeline阶段：
- 阶段14: 金融科技强度评分
- 阶段15: 文章级政策语义对齐度
- 阶段21: 统一LLM语义精筛与情感分析
- 阶段22: 词典法情感分析
- 阶段23: BERT模型情感分析
- 阶段24: 跟风衰减权重
- 阶段30: text2vec双轨稳健性指标
- 阶段42: 金融科技注意力 + 媒体异质性
- 阶段43: 地理缓冲 + AI模仿
- 阶段44: Bartik IV + DID
- 阶段46: 网络溢出
- 阶段47: 经纪网络
- 阶段48: LLM同行IV

## 学术参考

本数据集的构建方法参考了以下文献：
- Hassan et al. (2019, QJE) - 企业层面政治风险测量
- Gentzkow, Kelly & Taddy (2019, JEL) - 文本作为数据
- Holzman et al. (2023, TAR) - 媒体语调与股票回报
- Tetlock et al. (2008, JF) - 量化语言测量企业基本面

## 下一步建议

1. **运行主控文件**: `do stata/99_master.do`
2. **检查数据**: 查看生成的 `40_panel_yearly_labeled.dta`
3. **探索性分析**: 使用 `describe` 和 `summarize` 命令
4. **开始回归分析**: 根据研究问题选择合适的指标

## 注意事项

1. 部分指标可能存在缺失值（如某些银行某年无新闻覆盖）
2. 同类指标可能高度相关，避免同时放入回归
3. 建议在银行层面聚类标准误
4. 使用标准化指标（`_z`后缀）便于比较系数大小

## 文件位置

所有文件已保存在：
- Stata do文件: `F:\WiseSearch\data_antigravity_project\news_process\stata\`
- Python脚本: `F:\WiseSearch\data_antigravity_project\news_process\scripts\`
- 数据文件: `F:\WiseSearch\data_antigravity_project\news_process\data\processed\`

---

**创建日期**: 2026-05-10  
**作者**: Claude Code  
**版本**: v1.0
