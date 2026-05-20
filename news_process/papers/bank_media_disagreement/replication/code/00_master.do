* news_process v3.7.0 — 第 10 篇 bank_media_disagreement Master orchestrator
*
* 设计依据: V4 audit reframe + DC1 path B (SSRN + _full main).
* Stata 版本要求: ≥ 19 (项目策略 2026-05-16: Stata 19+ only)
* 必需包: ssc install reghdfe estout coefplot asdoc

version 19
clear all
set maxvar 32767
set linesize 120
set more off

* Project root: 默认相对当前工作目录 (cwd); 外部协作者无需改路径,
* 只需 cd 到 data_antigravity_project 根再运行 do code/00_master.do.
* (P-017 修复: 不再硬编码本机绝对路径.)
local project_root "`c(pwd)'"
di as txt "Project root: `project_root'"

* 检查必要包安装
do "news_process/papers/bank_media_disagreement/replication/code/00_install_packages.do"

* 数据准备
do "news_process/papers/bank_media_disagreement/replication/code/01_data_prep.do"

* === Tables (论文主体) ===
do "news_process/papers/bank_media_disagreement/replication/code/11_table2_main_disagreement_risk.do"
do "news_process/papers/bank_media_disagreement/replication/code/13_table4_heterogeneity.do"

display ""
display "=========================================="
display "第 10 篇 bank_media_disagreement 全部 .do 跑完"
display "  输出: papers/bank_media_disagreement/output/"
display "=========================================="
