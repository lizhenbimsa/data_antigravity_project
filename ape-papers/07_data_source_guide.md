# APEP 复现 — 公共数据源参考指南

## 概述

APEP 项目严格使用**公开可获取的数据**，确保所有研究可复现。主要数据来源包括美国联邦政府的公共统计 API。

---

## 1. US Census Bureau — 美国人口普查局

### 1.1 American Community Survey (ACS)

| 属性         | 值                                            |
| ------------ | --------------------------------------------- |
| **API 端点** | `https://api.census.gov/data/{year}/acs/acs1` |
| **R 包**     | `tidycensus`                                  |
| **时间覆盖** | 2005-2023（1年制）/ 2009-2023（5年制）        |
| **地理级别** | 州、县、Census tract、Block group             |
| **频率**     | 年度                                          |
| **API Key**  | https://api.census.gov/data/key_signup.html   |

#### 常用变量

```r
# 劳动力相关
"B23025_001" = "16岁以上人口"
"B23025_002" = "劳动力"
"B23025_003" = "民用劳动力"
"B23025_004" = "就业人口"
"B23025_005" = "失业人口"
"B23025_007" = "非劳动力"

# 收入相关
"B19013_001" = "家庭收入中位数"
"B19001_001" = "家庭收入分布总数"
"B20004_001" = "个人收入中位数"

# 人口特征
"B01003_001" = "总人口"
"B01001_002" = "男性人口"
"B01001_026" = "女性人口"
"B02001_002" = "白人人口"
"B02001_003" = "黑人/非裔人口"
"B03001_003" = "西班牙裔/拉丁裔人口"

# 教育
"B15003_022" = "学士学位"
"B15003_023" = "硕士学位"
"B15003_025" = "博士学位"

# 住房
"B25077_001" = "房屋价值中位数"
"B25064_001" = "租金中位数"
"B25003_001" = "住房权属总数"

# 健康保险
"B27001_001" = "健康保险总人口"
"B27010_001" = "健康保险覆盖类型"
```

#### R 代码示例
```r
library(tidycensus)
census_api_key("YOUR_KEY")

# 获取 2022 年各州就业数据
data <- get_acs(
  geography = "state",
  variables = c(employed = "B23025_004", labor_force = "B23025_002"),
  year = 2022,
  survey = "acs1"
)
```

### 1.2 Current Population Survey (CPS)

| 属性         | 值                                               |
| ------------ | ------------------------------------------------ |
| **网站**     | https://www.census.gov/programs-surveys/cps.html |
| **R 包**     | `cpsR` / `ipumsr`（需 IPUMS 账号）               |
| **时间覆盖** | 1968-至今                                        |
| **特点**     | 月度劳动力调查，个人级微观数据                   |

### 1.3 PUMS（公共使用微观数据样本）

| 属性         | 值                                                 |
| ------------ | -------------------------------------------------- |
| **API 端点** | `https://api.census.gov/data/{year}/acs/acs1/pums` |
| **R 包**     | `tidycensus::get_pums()`                           |
| **特点**     | 个人/家庭级微观数据，可做子样本分析                |

---

## 2. Bureau of Labor Statistics (BLS) — 劳工统计局

| 属性         | 值                                                  |
| ------------ | --------------------------------------------------- |
| **API 端点** | `https://api.bls.gov/publicAPI/v2/timeseries/data/` |
| **R 包**     | `blsAPI`                                            |
| **时间覆盖** | 1939-至今（部分系列）                               |
| **频率**     | 月度/季度/年度                                      |
| **API Key**  | https://registrationbls.gov/registrationEngine/     |

### 常用数据系列

| 系列 ID 前缀 | 数据名称     | 地理级别    |
| ------------ | ------------ | ----------- |
| LAUS         | 地区失业统计 | 州、县、MSA |
| CE           | 当前就业统计 | 全国、州    |
| CW           | 县级工资数据 | 县          |
| OE           | 职业就业统计 | 州、MSA     |

#### R 代码示例
```r
library(blsAPI)
# 获取加州月度失业率
payload <- list(
  'seriesid' = list("LASST060000000000003"),
  'startyear' = "2010",
  'endyear' = "2023",
  'registrationkey' = "YOUR_BLS_KEY"
)
response <- blsAPI(payload, api_version = 2, return_data_frame = TRUE)
```

---

## 3. Federal Reserve (FRED) — 联储经济数据

| 属性           | 值                                                |
| -------------- | ------------------------------------------------- |
| **网站**       | https://fred.stlouisfed.org/                      |
| **API 端点**   | `https://api.stlouisfed.org/fred/`                |
| **R 包**       | `fredr`                                           |
| **数据系列数** | 800,000+                                          |
| **API Key**    | https://fred.stlouisfed.org/docs/api/api_key.html |

### 常用系列

| 系列 ID   | 描述                  |
| --------- | --------------------- |
| UNRATE    | 全国失业率            |
| GDP       | 国内生产总值          |
| CPIAUCSL  | 消费者价格指数        |
| FEDFUNDS  | 联邦基金利率          |
| {STATE}UR | 各州失业率（如 TXUR） |
| MSPUS     | 房屋销售价格中位数    |

#### R 代码示例
```r
library(fredr)
fredr_set_key("YOUR_FRED_KEY")

# 获取全国失业率
unrate <- fredr(
  series_id = "UNRATE",
  observation_start = as.Date("2010-01-01"),
  observation_end = as.Date("2023-12-31"),
  frequency = "a"  # 年度
)
```

---

## 4. 其他数据源

### 4.1 IPUMS
- **网站**: https://ipums.org/
- **内容**: CPS、ACS 等的统一接口
- **R 包**: `ipumsr`
- **需要**: 注册账号

### 4.2 CDC WONDER
- **网站**: https://wonder.cdc.gov/
- **内容**: 死亡率、出生率等健康数据
- **特点**: 县级公共健康数据

### 4.3 FBI UCR
- **网站**: https://crime-data-explorer.fr.cloud.gov/
- **内容**: 犯罪统计数据
- **R 包**: 需手动下载或使用 API

### 4.4 National Center for Education Statistics (NCES)
- **网站**: https://nces.ed.gov/
- **内容**: 教育相关数据
- **特点**: 学区级数据

---

## 5. 政策数据编码

### 政策实施时间表
许多 APEP 论文需要**手动编码**各州的政策实施年份。常用参考来源：

| 来源               | 网址                  | 内容                   |
| ------------------ | --------------------- | ---------------------- |
| NCSL               | https://www.ncsl.org/ | 全国各州立法数据库     |
| LegiScan           | https://legiscan.com/ | 法案追踪               |
| Westlaw/LexisNexis | —                     | 法律数据库（学术访问） |

### 编码格式
```r
# 标准政策编码向量
treatment_years <- c(
  "California" = 2020,
  "New York"   = 2021,
  "Texas"      = Inf,  # 从未实施 = 对照组
  ...
)
```

---

## 6. API 使用注意事项

> [!WARNING]
> 1. **速率限制**: Census API 每日调用有上限，建议批量获取后缓存
> 2. **数据版本**: ACS 数据每年修订，注意使用一致的年份版本
> 3. **缺失值**: 小人口州/县可能因隐私保护被抑制（suppressed）
> 4. **MOE**: ACS 数据自带 Margin of Error，应在分析中考虑
> 5. **地理编码**: FIPS 代码可能随年份变化（如弗吉尼亚州的独立市）
