/*==============================================================================
  文件: 99_master.do
  目的: 主控文件 - 加载数据并执行所有标签脚本
  作者: Claude Code
  日期: 2026-05-10

  使用说明:
  1. 首先需要将 parquet 文件转换为 dta 格式
  2. 运行本文件将自动加载数据并添加所有变量标签
  3. 所有文本生成的指标都将被正确标注
==============================================================================*/

clear all
set more off
set maxvar 32767

* 设置工作目录
cd "F:\WiseSearch\data_antigravity_project\news_process"

* ============================================================================
* 步骤1: 转换 parquet 为 dta 格式 (如果尚未转换)
* ============================================================================

capture confirm file "data/processed/40_panel_yearly.dta"
if _rc != 0 {
    display as error "未找到 40_panel_yearly.dta 文件"
    display as text "正在使用 Python 转换 parquet 文件..."

    python script
import pandas as pd
import sys

try:
    # 读取 parquet 文件
    df = pd.read_parquet('data/processed/40_panel_yearly.parquet')

    # 转换为 Stata dta 格式
    df.to_stata('data/processed/40_panel_yearly.dta',
                write_index=False,
                version=118)  # Stata 14/15/16 格式

    print("转换成功: 40_panel_yearly.parquet -> 40_panel_yearly.dta")
    print(f"数据维度: {df.shape[0]} 行 × {df.shape[1]} 列")

except Exception as e:
    print(f"转换失败: {str(e)}", file=sys.stderr)
    sys.exit(1)
    end
}

* ============================================================================
* 步骤2: 加载面板数据
* ============================================================================

use "data/processed/40_panel_yearly.dta", clear

display as text _newline(2)
display as result "=" * 70
display as result "数据加载成功"
display as result "=" * 70
describe, short
summarize target_bank year, detail

* ============================================================================
* 步骤3: 执行所有变量标签脚本
* ============================================================================

display as text _newline(2)
display as result "=" * 70
display as result "开始添加变量标签..."
display as result "=" * 70

* 01. 基础变量和LLM情感指标
display as text "正在执行: 01_label_variables.do"
do "stata/01_label_variables.do"

* 02. 词典和BERT情感指标
display as text "正在执行: 02_label_dict_bert.do"
do "stata/02_label_dict_bert.do"

* 03. 文本特征和衍生指标
display as text "正在执行: 03_label_features.do"
do "stata/03_label_features.do"

* 04. 媒体注意力和异质性指标
display as text "正在执行: 04_label_media.do"
do "stata/04_label_media.do"

* 05. 高级文本分析指标
display as text "正在执行: 05_label_advanced.do"
do "stata/05_label_advanced.do"

* 06. 地理缓冲和区域指标
display as text "正在执行: 06_label_geography.do"
do "stata/06_label_geography.do"

* 07. Bartik IV和DID指标
display as text "正在执行: 07_label_iv_did.do"
do "stata/07_label_iv_did.do"

* 08. 网络指标
display as text "正在执行: 08_label_network.do"
do "stata/08_label_network.do"

* 09. 战略差异度和政策对齐度指标
display as text "正在执行: 09_label_strategic.do"
do "stata/09_label_strategic.do"

* 10. 社会效益和代币采纳指标
display as text "正在执行: 10_label_benefit_token.do"
do "stata/10_label_benefit_token.do"

* 11. 洗绿和分歧度指标
display as text "正在执行: 11_label_washing_disag.do"
do "stata/11_label_washing_disag.do"

* 12. 迎合指标和其他衍生指标
display as text "正在执行: 12_label_cater_misc.do"
do "stata/12_label_cater_misc.do"

* 13. 标准化指标
display as text "正在执行: 13_label_standardized.do"
do "stata/13_label_standardized.do"

* 14. JF系数和排除性指标
display as text "正在执行: 14_label_jf_exc.do"
do "stata/14_label_jf_exc.do"

* 15. 补充标签（遗漏的变量）
display as text "正在执行: 15_label_supplementary.do"
do "stata/15_label_supplementary.do"

* ============================================================================
* 步骤3.5: 处理超长变量名（Stata 32字符限制）
* ============================================================================

display as text _newline(2)
display as result "=" * 70
display as result "处理超长变量名..."
display as result "=" * 70

* 重命名8个超过32字符的变量名
capture rename jiang_2021_idf_score_hw_sum_titl jiang_21_idf_hw_sum_title
capture rename jiang_2021_idf_score_mw_sum_titl jiang_21_idf_mw_sum_title
capture rename prov_leave1out_dict_avg_tone_ful prov_loo_dict_avg_tone_full
capture rename prov_leave1out_dict_avg_tone_tit prov_loo_dict_avg_tone_title
capture rename city_leave1out_dict_avg_tone_ful city_loo_dict_avg_tone_full
capture rename city_leave1out_dict_avg_tone_tit city_loo_dict_avg_tone_title
capture rename prov_leave1out_bert_avg_pos_titl prov_loo_bert_avg_pos_title
capture rename city_leave1out_bert_avg_pos_titl city_loo_bert_avg_pos_title

display as text "已重命名8个超长变量名"

* ============================================================================
* 步骤4: 保存带标签的数据
* ============================================================================

display as text _newline(2)
display as result "=" * 70
display as result "保存带标签的数据..."
display as result "=" * 70

save "data/processed/40_panel_yearly_labeled.dta", replace

display as text _newline(2)
display as result "=" * 70
display as result "完成! 所有变量标签已添加"
display as result "=" * 70
display as text "输出文件: data/processed/40_panel_yearly_labeled.dta"
display as text "总变量数: " as result c(k)
display as text "总观测数: " as result c(N)

* ============================================================================
* 步骤5: 生成变量标签摘要报告
* ============================================================================

display as text _newline(2)
display as result "=" * 70
display as result "变量标签摘要"
display as result "=" * 70

* 统计各类指标数量
local llm_vars = 0
local dict_vars = 0
local bert_vars = 0
local media_vars = 0
local geo_vars = 0
local network_vars = 0
local strategic_vars = 0

foreach var of varlist * {
    local lab : variable label `var'
    if regexm("`lab'", "LLM|GPT|Gemini|Grok") local ++llm_vars
    if regexm("`lab'", "词典|江|姚|卞|杜|尤") local ++dict_vars
    if regexm("`lab'", "BERT|FinBERT|FinSent") local ++bert_vars
    if regexm("`lab'", "媒体|Media") local ++media_vars
    if regexm("`lab'", "地理|缓冲|LOO|km") local ++geo_vars
    if regexm("`lab'", "网络|同行|中心度|Peer") local ++network_vars
    if regexm("`lab'", "战略|差异|政策|对齐") local ++strategic_vars
}

display as text "LLM情感分析指标: " as result `llm_vars'
display as text "词典情感分析指标: " as result `dict_vars'
display as text "BERT情感分析指标: " as result `bert_vars'
display as text "媒体注意力指标: " as result `media_vars'
display as text "地理缓冲指标: " as result `geo_vars'
display as text "网络指标: " as result `network_vars'
display as text "战略差异度指标: " as result `strategic_vars'

display as text _newline(2)
display as result "所有文本生成的指标已成功聚合到Stata面板数据中!"

