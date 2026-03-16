# 复现指南模板 — REPLICATION.md

# Replication Guide for paper_XXXX

## Paper Information
- **Title**: {论文标题}
- **Paper ID**: paper_XXXX_vN
- **Method**: {DiD / RDD}
- **Author Model**: {LLM 模型名}
- **Date**: {发布日期}

## System Requirements

### Software
- Stata >= 15.0

### Stata Packages
```stata
do code/00_packages.do
```
Key packages: `reghdfe`, `ppmlhdfe`, `estout`, `coefplot`, `psmatch2`, `bdiff`, `winsor2`, `ivreg2`, `xtabond2`, `xtscc`, `rdrobust`

### Data
- 本项目使用本地 `data/data.dta` 数据库，无需外部 API 密钥
- 所有银行变量均已预先整合至该文件

## Replication Steps

### Step 1: Set up environment
```bash
# Create output directories
mkdir -p output data figures tables logs
```

### Step 2: Install Stata dependencies
```bash
stata-mp -e do code/00_packages.do
```

### Step 3: Load and preprocess bank data
```bash
stata-mp -e do code/01_fetch_data.do
```
**Expected output**: `data/clean_data.dta`（银行面板数据，含 bankid, year, 控制变量, DID 处理变量）
**Estimated time**: ~2 minutes

### Step 4: Descriptive statistics
```bash
stata-mp -e do code/02_descriptive_stats.do
```
**Expected output**: 描述性统计输出（tabstat, 相关系数, VIF）

### Step 5: Run main analysis
```bash
stata-mp -e do code/03_main_analysis.do
```
**Expected output**:
- `data/main_results_summary.csv` — 基准回归结果
- 控制台输出：reghdfe / ppmlhdfe / xtabond2 结果

### Step 6: Robustness checks
```bash
stata-mp -e do code/04_robustness.do
```
**Expected output**: PSM-DID, 安慰剂, IV, 系统GMM 等稳健性检验结果

### Step 7: Generate figures
```bash
stata-mp -e do code/05_figures.do
```
**Expected output**: `figures/*.png` — 平行趋势图、安慰剂核密度图、银行类型趋势图等

### Step 8: Heterogeneity analysis
```bash
stata-mp -e do code/06_heterogeneity.do
```
**Expected output**: 分组回归 + bdiff 组间差异检验结果

### Step 9: Mechanism analysis
```bash
stata-mp -e do code/07_mechanism.do
```
**Expected output**: 机制渠道回归结果（风险管理/信贷配置/金融创新）

### Step 10: Further analysis
```bash
stata-mp -e do code/08_further_analysis.do
```
**Expected output**: 调节效应、前瞻经济后果、同业溢出效应结果

## Expected Results Summary

| Estimate       | Value | SE   | p-value |
| -------------- | ----- | ---- | ------- |
| TWFE (reghdfe) | {β}   | {SE} | {p}     |
| ppmlhdfe       | {β}   | {SE} | {p}     |
| System GMM     | {β}   | {SE} | {p}     |
| Driscoll-Kraay | {β}   | {SE} | {p}     |

## File Manifest

```
paper_XXXX/vN/
├── paper.md                # Markdown 论文源码
├── metadata.json           # 论文元数据
├── initial_plan.md         # 预注册研究计划
├── research_plan.md        # 演进版研究计划
├── REPLICATION.md          # 本文件
├── code/
│   ├── 00_packages.do      # 包安装
│   ├── 01_fetch_data.do    # 数据加载与清洗
│   ├── 02_descriptive_stats.do  # 描述性统计
│   ├── 03_main_analysis.do # 基准回归
│   ├── 04_robustness.do    # 稳健性检验
│   ├── 05_figures.do       # 图表生成
│   ├── 06_heterogeneity.do # 异质性分析
│   ├── 07_mechanism.do     # 机制分析
│   └── 08_further_analysis.do  # 进一步研究
├── data/
│   ├── clean_data.dta      # 清洗后的银行面板数据
│   └── main_results_summary.csv
├── figures/
│   ├── parallel_trends.png
│   ├── placebo_density.png
│   ├── trend_by_banktype.png
│   └── ...
├── tables/
│   └── ...
└── logs/
    └── ...
```

## Known Issues
- {已知问题1}
- {已知问题2}

## Contact
For replication questions, please open an issue at:
#
