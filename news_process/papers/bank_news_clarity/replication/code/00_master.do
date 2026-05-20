* news_process v3.7.0 — 第 11 篇 bank_news_clarity Master orchestrator
*
* 设计依据: V4 audit reframe (clarity = external info env quality, Bushee 2010 JAR)
* DC1 path C: No-SSRN + _ctx G3 严谨路线.
* Stata 版本要求: ≥ 19. 必需包: reghdfe estout coefplot asdoc ivreg2.

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

do "news_process/papers/bank_news_clarity/replication/code/00_install_packages.do"
do "news_process/papers/bank_news_clarity/replication/code/01_data_prep.do"

* === Tables ===
do "news_process/papers/bank_news_clarity/replication/code/11_table2_main_clarity_risk.do"
do "news_process/papers/bank_news_clarity/replication/code/13_table4_heterogeneity.do"

display ""
display "=========================================="
display "第 11 篇 bank_news_clarity 全部 .do 跑完"
display "  输出: papers/bank_news_clarity/output/"
display "=========================================="
