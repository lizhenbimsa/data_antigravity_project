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

local project_root "F:/WiseSearch/data_antigravity_project"
cd "`project_root'"

do "papers/bank_news_clarity/replication/code/00_install_packages.do"
do "papers/bank_news_clarity/replication/code/01_data_prep.do"

* === Tables ===
do "papers/bank_news_clarity/replication/code/11_table2_main_clarity_risk.do"
do "papers/bank_news_clarity/replication/code/13_table4_heterogeneity.do"

display ""
display "=========================================="
display "第 11 篇 bank_news_clarity 全部 .do 跑完"
display "  输出: papers/bank_news_clarity/output/"
display "=========================================="
