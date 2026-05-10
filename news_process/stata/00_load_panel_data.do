/*==============================================================================
  文件: 00_load_panel_data.do
  目的: 加载并标注所有媒体报道文本生成的指标
  作者: Claude Code
  日期: 2026-05-10

  说明:
  本do文件加载 40_panel_yearly.parquet 面板数据，包含所有从媒体报道文本
  生成的指标，涵盖：
  - LLM情感分析指标 (阶段21)
  - 词典情感分析指标 (阶段22)
  - BERT情感分析指标 (阶段23)
  - 金融科技强度指标 (阶段14)
  - 政策对齐度指标 (阶段15)
  - 媒体注意力指标 (阶段42)
  - 地理缓冲指标 (阶段43)
  - 网络指标 (阶段46-47)
  - 战略差异度指标 (阶段30)
  - 其他衍生指标
==============================================================================*/

clear all
set more off
set maxvar 32767

* 设置工作目录
cd "F:\WiseSearch\data_antigravity_project\news_process"

* 加载面板数据 (需要先安装 parquet 读取工具)
* 方法1: 使用 Python 转换为 dta 格式
* 方法2: 使用 readstat13 或其他工具

* 这里假设已经转换为 dta 格式
use "data/processed/40_panel_yearly.dta", clear

* 或者使用 Python 脚本转换
* python script
* import pandas as pd
* df = pd.read_parquet('data/processed/40_panel_yearly.parquet')
* df.to_stata('data/processed/40_panel_yearly.dta', write_index=False)
* end

display "数据加载完成"
describe, short
summarize

