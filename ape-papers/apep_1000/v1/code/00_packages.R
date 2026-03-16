# ============================================================
# APEP DiD 分析代码模板 — 00_packages.R
# 安装和加载所有必需的 R 包
# ============================================================

options(repos = c(CRAN = "https://cloud.r-project.org"))

# --- 计量经济学包 ---
if (!require("fixest")) install.packages("fixest") # 固定效应 + 交错 DiD
if (!require("did")) install.packages("did") # Callaway-Sant'Anna
if (!require("did2s")) install.packages("did2s") # Gardner 两步 DiD
if (!require("modelsummary")) install.packages("modelsummary") # 回归表格
if (!require("sandwich")) install.packages("sandwich") # 稳健标准误
if (!require("lmtest")) install.packages("lmtest") # 假设检验

# --- 数据获取包 ---
if (!require("tidycensus")) install.packages("tidycensus") # Census API
if (!require("fredr")) install.packages("fredr") # FRED API
if (!require("httr")) install.packages("httr") # HTTP 请求
if (!require("jsonlite")) install.packages("jsonlite") # JSON 解析
if (!require("blsAPI")) install.packages("blsAPI") # BLS API

# --- 数据处理与可视化 ---
if (!require("tidyverse")) install.packages("tidyverse") # 数据工具集
if (!require("data.table")) install.packages("data.table") # 高性能数据操作
if (!require("haven")) install.packages("haven") # Stata 格式
if (!require("ggthemes")) install.packages("ggthemes") # ggplot 主题
if (!require("patchwork")) install.packages("patchwork") # 图表拼接
if (!require("scales")) install.packages("scales") # 坐标轴格式
if (!require("kableExtra")) install.packages("kableExtra") # 表格美化
if (!require("stargazer")) install.packages("stargazer") # 回归表格

# 加载所有包
library(fixest)
library(did)
library(did2s)
library(modelsummary)
library(tidycensus)
library(tidyverse)
library(data.table)
library(patchwork)
library(scales)

cat("✅ 所有依赖包加载完成\n")
