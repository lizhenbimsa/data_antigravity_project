# APEP 复现 — 环境配置指南

## 1. R 语言环境

### 1.1 安装 R（≥ 4.3.0）
```bash
# Windows: 从 https://cran.r-project.org/ 下载安装
# macOS:
brew install r
# Linux (Ubuntu):
sudo apt-get install r-base r-base-dev
```

### 1.2 安装 RStudio（推荐）
从 https://posit.co/downloads/ 下载 RStudio Desktop

### 1.3 核心 R 包安装
```r
# 00_packages.R — 在每个论文项目中首先运行

# 计量经济学相关
install.packages(c(
  "fixest",        # 固定效应回归 + 交错 DiD
  "did",           # Callaway-Sant'Anna DiD 估计
  "did2s",         # Gardner (2021) 两步 DiD
  "rdrobust",      # 断点回归（RDD）稳健估计
  "rddensity",     # RDD 密度检验
  "modelsummary",  # 回归结果表格
  "sandwich",      # 稳健标准误
  "lmtest"         # 假设检验
))

# 数据获取
install.packages(c(
  "tidycensus",    # Census API 数据
  "censusapi",     # Census API（替代方案）
  "fredr",         # FRED 联储经济数据
  "blsAPI",        # BLS 劳工统计局数据
  "httr",          # HTTP 请求
  "jsonlite"       # JSON 解析
))

# 数据处理与可视化
install.packages(c(
  "tidyverse",     # dplyr, ggplot2, tidyr, readr 等
  "data.table",    # 高性能数据操作
  "haven",         # 读写 Stata/SPSS/SAS
  "arrow",         # Parquet 读写
  "ggthemes",      # ggplot2 主题扩展
  "patchwork",     # 图表拼接
  "scales",        # 坐标轴标签格式化
  "kableExtra",    # 表格格式化
  "stargazer"      # 回归表格输出
))
```

## 2. API 密钥配置

### 2.1 Census API Key
1. 前往 https://api.census.gov/data/key_signup.html 注册
2. 在 R 中配置：
```r
# 方法一：在 .Renviron 中设置
# 打开 .Renviron:
usethis::edit_r_environ()
# 添加：
# CENSUS_API_KEY=your_key_here

# 方法二：在脚本中直接设置
census_api_key("your_key_here", install = TRUE)
```

### 2.2 FRED API Key
1. 前往 https://fred.stlouisfed.org/docs/api/api_key.html 注册
2. 在 R 中配置：
```r
fredr_set_key("your_fred_key_here")
```

### 2.3 BLS API Key
1. 前往 https://registrationbls.gov/registrationEngine/ 注册
2. 在请求中包含 key 参数即可

## 3. LaTeX 环境

### 3.1 安装 TeX Live / MiKTeX
```bash
# Windows: 下载 MiKTeX https://miktex.org/download
# macOS:
brew install --cask mactex
# Linux:
sudo apt-get install texlive-full
```

### 3.2 必需的 LaTeX 包
大多数 TeX 发行版已包含，如缺少可手动安装：
- `amsmath`, `amssymb` — 数学公式
- `booktabs` — 专业表格
- `graphicx` — 图片插入
- `hyperref` — 超链接
- `natbib` / `biblatex` — 参考文献
- `geometry` — 页面设置
- `setspace` — 行距
- `float` — 浮动体控制

## 4. LLM API 配置

### 4.1 所需 LLM 服务
用于论文撰写和评审的模型：

| 模型                   | 用途                        | API 来源      |
| ---------------------- | --------------------------- | ------------- |
| Claude claude-opus-4-5 | 论文撰写（authoring_model） | Anthropic API |
| GPT-5-mini             | 评审模型                    | OpenAI API    |
| Grok-4.1-Fast          | 评审模型                    | xAI API       |
| Gemini-3-Flash         | 评审模型                    | Google AI API |
| Codex-Mini             | 评审模型                    | OpenAI API    |

### 4.2 API Key 环境变量
```bash
# 在 .env 或系统环境变量中配置
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export XAI_API_KEY="xai-..."
export GOOGLE_AI_API_KEY="AIza..."
```

## 5. Python 环境（辅助）

部分论文使用 Python 进行数据预处理：
```bash
pip install requests pandas numpy census us
```

## 6. 目录结构初始化

```bash
# 为新论文创建标准目录结构
mkdir -p apep_XXXX/v1/{code,data,figures,tables}
```

## 7. 验证安装

```r
# 运行以下代码验证所有依赖是否正确安装
packages <- c("fixest", "did", "did2s", "rdrobust", "tidycensus",
              "fredr", "tidyverse", "modelsummary")

for (pkg in packages) {
  if (require(pkg, character.only = TRUE, quietly = TRUE)) {
    cat(sprintf("✅ %s v%s\n", pkg, packageVersion(pkg)))
  } else {
    cat(sprintf("❌ %s 未安装\n", pkg))
  }
}
```
