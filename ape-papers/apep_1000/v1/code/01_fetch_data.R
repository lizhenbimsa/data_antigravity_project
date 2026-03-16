# 01_fetch_data.R
# 本脚本从Census ACS REST API获取2010-2023年州层面劳动力相关数据，
# 处理成适合did包面板数据格式，并保存面板数据及描述性统计。

source("code/00_packages.R")  # 加载必要包，假设已配置好 httr, jsonlite, dplyr, tibble 等

library(httr)
library(jsonlite)
library(dplyr)
library(tibble)

# -------------------------------------------
# 1. 定义州FIPS与州缩写完整映射表 (51个州包括DC)
# -------------------------------------------
state_map <- tibble::tribble(
  ~state_fips, ~state_abbr,
  "01", "AL",  "02", "AK", "04", "AZ", "05", "AR", "06", "CA",
  "08", "CO",  "09", "CT", "10", "DE", "11", "DC", "12", "FL",
  "13", "GA",  "15", "HI", "16", "ID", "17", "IL", "18", "IN",
  "19", "IA",  "20", "KS", "21", "KY", "22", "LA", "23", "ME",
  "24", "MD",  "25", "MA", "26", "MI", "27", "MN", "28", "MS",
  "29", "MO",  "30", "MT", "31", "NE", "32", "NV", "33", "NH",
  "34", "NJ",  "35", "NM", "36", "NY", "37", "NC", "38", "ND",
  "39", "OH",  "40", "OK", "41", "OR", "42", "PA", "44", "RI",
  "45", "SC",  "46", "SD", "47", "TN", "48", "TX", "49", "UT",
  "50", "VT",  "51", "VA", "53", "WA", "54", "WV", "55", "WI",
  "56", "WY"
) %>% mutate(state_fips = sprintf("%02s", state_fips))  # 保证两位格式

# -------------------------------------------
# 2. 定义要抓取的变量及说明
# ACS变量说明（ACS1年数据）：
# B23025_004E - employed 
# B23025_005E - unemployed
# B23025_003E - labor force (B23025_004E + B23025_005E)
# B23025_002E - population 16 years and over (有劳动力适龄人口)
# B01003_001E - total population
# 计算：
# emp_rate = employed / population 16+
# lfp_rate = labor force / population 16+
# unemp_rate = unemployed / labor force
# -------------------------------------------
varcodes <- c(
  employed = "B23025_004E",
  unemployed = "B23025_005E",
  labor_force = "B23025_003E",
  pop_16_over = "B23025_002E",
  total_pop = "B01003_001E"
)

years <- 2010:2023

# -------------------------------------------
# 3. 初始化空列表存储每年数据
# -------------------------------------------
data_list <- list()

# -------------------------------------------
# 4. 定义获取单年州数据的函数
# -------------------------------------------
fetch_year_state_data <- function(year) {
  # 构造API地址，获取所有州全部目标变量
  url <- sprintf(
    "https://api.census.gov/data/%d/acs/acs1?get=NAME,%s&for=state:*",
    year,
    paste(varcodes, collapse = ",")
  )
  resp <- GET(url)
  # 检查响应状态
  if (status_code(resp) != 200) {
    warning(sprintf("警告：%d年数据获取失败，状态码%d，跳过此年", year, status_code(resp)))
    return(NULL)
  }
  # 解析内容
  content_json <- fromJSON(content(resp, as = "text", encoding = "UTF-8"))
  if (length(content_json) < 2) {
    warning(sprintf("警告：%d年API返回数据非预期格式，跳过此年", year))
    return(NULL)
  }
  df <- as_tibble(content_json[-1, ], .name_repair = "minimal")
  colnames(df) <- content_json[1, ]
  
  # 重命名变量方便后续处理
  df <- df %>%
    rename(
      state_name = NAME,
      employed = !!varcodes["employed"],
      unemployed = !!varcodes["unemployed"],
      labor_force = !!varcodes["labor_force"],
      pop_16_over = !!varcodes["pop_16_over"],
      total_pop = !!varcodes["total_pop"],
      state_fips = state
    ) %>%
    # 转换变量类型为数值
    mutate(across(c(employed, unemployed, labor_force, pop_16_over, total_pop), as.numeric),
           state_fips = sprintf("%02s", state_fips))  # 保持2位格式
  
  # 丢弃无效数据行：pop_16_over <= 0情况
  df <- df %>% filter(pop_16_over > 0)
  
  # 计算比率变量
  df <- df %>%
    mutate(
      emp_rate = employed / pop_16_over,
      lfp_rate = labor_force / pop_16_over,
      unemp_rate = ifelse(labor_force > 0, unemployed / labor_force, NA_real_),
      year = year
    )
  
  # 加州缩写，便于后续合并
  df <- df %>%
    left_join(state_map, by = "state_fips")
  
  return(df)
}

# -------------------------------------------
# 5. 循环抓取各年数据，拼接
# -------------------------------------------
for (yr in years) {
  df_year <- tryCatch(fetch_year_state_data(yr),
                      error = function(e) {
                        warning(sprintf("错误：%d年数据加载异常：%s，跳过此年", yr, e$message))
                        NULL
                      })
  if (is.null(df_year)) {
    next  # 跳过失败年份
  }
  data_list[[as.character(yr)]] <- df_year
  cat(sprintf("成功获取%d年数据，行数%d\n", yr, nrow(df_year)))
}

# 合并所有年份数据
panel_data_raw <- bind_rows(data_list)

# -------------------------------------------
# 6. 读取treatment信息（state_fips 和 reform_year），假设有此表
# 这里模拟构造示例 treatment_year 数据，实际研究中请替换为真实数据文件读取或手工定义
# 由于问题没给treatment年份数据来源，以下示意：
# -------------------------------------------
# 假设 reform_year 是每州的改革年份，未改革州设为NA或Inf
# 此处演示模拟一个列表，实际请替换
# 格式例：
# treatment_df <- tibble(state_fips = c("01","02",...),
#                        reform_year = c(2015, Inf, ...))
# 
# 强制要求：
# 从未处理的 cohort 设为 Inf
# -------------------------------------------

# 下面演示构造示例，务必替换为实际数据
treatment_df <- state_map %>%
  mutate(reform_year = NA_integer_)

# 随机模拟部分州的改革年份（2012-2018），其余为未处理
set.seed(123)
treated_states <- sample(state_map$state_fips, 20)
treatment_df <- treatment_df %>%
  mutate(reform_year = ifelse(state_fips %in% treated_states,
                              sample(2012:2018, length(treated_states), replace = TRUE),
                              Inf))

# 检查treatment_df结构
cat("Treatment cohort（reform_year）分布情况预览：\n")
print(table(treatment_df$reform_year, useNA = "ifany"))

# -------------------------------------------
# 7. 构建面板数据，含cohort、post、treated、rel_time变量
# -------------------------------------------

panel_data <- panel_data_raw %>%
  # 加入treatment年份
  left_join(treatment_df, by = "state_fips") %>%
  # cohort变量：reform_year
  mutate(cohort = reform_year) %>%
  # 如果reform_year为NA，转Inf代表未处理
  mutate(cohort = ifelse(is.na(cohort), Inf, cohort)) %>%
  # post表示是否处于处理后时期
  mutate(post = ifelse(year >= cohort, 1, 0)) %>%
  # treated 表示个体是否为处理组（cohort不是Inf）
  mutate(treated = ifelse(cohort == Inf, 0, 1)) %>%
  # rel_time = 当前年份-改革年份，未处理为NA（可改为NA_real_）
  mutate(rel_time = ifelse(cohort == Inf, NA_real_, year - cohort)) %>%
  select(state_fips, state_abbr, year, cohort, post, treated, rel_time,
         emp_rate, lfp_rate, unemp_rate, employed, unemployed, labor_force, pop_16_over, total_pop)

# -------------------------------------------
# 8. 加入2019年人口权重 state_pop
# -------------------------------------------

pop_2019 <- data_list[["2019"]] %>%
  select(state_fips, total_pop) %>%
  rename(state_pop = total_pop)

panel_data <- panel_data %>%
  left_join(pop_2019, by = "state_fips")

cat("2019年人口权重加入完成，部分示例数据如下:\n")
print(head(panel_data %>% select(state_fips, state_abbr, year, state_pop)))

# -------------------------------------------
# 9. 数据质量检查，打印关键统计信息
# -------------------------------------------

cat("数据质量检查信息:\n")
cat(sprintf("总行数%d\n", nrow(panel_data)))
cat(sprintf("涉及州数%d\n", length(unique(panel_data$state_fips))))
cat(sprintf("时间跨度 %d 到 %d\n", min(panel_data$year), max(panel_data$year)))

# 检查 emp_rate, lfp_rate, unemp_rate 是否存在异常
summary_emp_rate <- summary(panel_data$emp_rate)
summary_lfp_rate <- summary(panel_data$lfp_rate)
summary_unemp_rate <- summary(panel_data$unemp_rate)

cat("emp_rate 简要统计:\n"); print(summary_emp_rate)
cat("lfp_rate 简要统计:\n"); print(summary_lfp_rate)
cat("unemp_rate 简要统计:\n"); print(summary_unemp_rate)

# -------------------------------------------
# 10. 保存面板数据
# -------------------------------------------
if (!dir.exists("data")) dir.create("data")
saveRDS(panel_data, file = "data/panel_data.rds")
cat("面板数据已保存到 data/panel_data.rds\n")

# -------------------------------------------
# 11. 计算并保存描述性统计
# -------------------------------------------

# 选择数值变量计算均值、中位数、标准差等描述
desc_stats <- panel_data %>%
  select(emp_rate, lfp_rate, unemp_rate, employed, unemployed, labor_force, pop_16_over, total_pop, state_pop) %>%
  summarise_all(list(
    mean = ~mean(., na.rm = TRUE),
    median = ~median(., na.rm = TRUE),
    sd = ~sd(., na.rm = TRUE),
    min = ~min(., na.rm = TRUE),
    max = ~max(., na.rm = TRUE),
    n_nonmiss = ~sum(!is.na(.))
  )) %>%
  tidyr::pivot_longer(everything(),
                      names_to = c("variable","statistic"),
                      names_sep = "_",
                      values_to = "value") %>%
  tidyr::pivot_wider(names_from = statistic, values_from = value) %>%
  arrange(variable)

write.csv(desc_stats, file = "data/descriptive_stats.csv", row.names = FALSE)
cat("描述性统计已保存到 data/descriptive_stats.csv\n")