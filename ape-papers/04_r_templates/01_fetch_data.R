# ==============================================================================
# APEP — 数据获取模板 (httr + jsonlite 版)
# ==============================================================================
# 与原始 ape-papers 项目完全一致的 Census ACS API 调用方式。
# 不需要 Census API Key，直接通过 REST API 获取公开数据。
#
# 用法:
#   source("code/00_packages.R")  # 先加载依赖
#   source("code/01_fetch_data.R")
# ==============================================================================

library(httr)
library(jsonlite)
library(tidycensus)
library(fredr)
library(blsAPI)

# 在脚本初始化时配置 FRED
fredr_set_key("44234648faf7e5225d76b53b7282d934")

# 直接在脚本中设置 Census，设置 install=TRUE 会将其保存到您的 .Renviron 中，以后就不用每次都写了
census_api_key("e987afbb572afbebe2ead1d3cb302a242fb73ae5", install = TRUE)

# 注：BLS API 密钥将直接在下方的第 3.5 节正式请求中使用。


cat("========================================\n")
cat("FETCHING DATA: Census ACS\n")
cat("========================================\n\n")

# ==============================================================================
# 1. Census ACS 数据获取函数
# ==============================================================================

cat("Fetching Census ACS data (2010-2023)...\n")

# 核心函数：从 Census API 获取单年度数据
fetch_acs_year <- function(year) {
  base_url <- sprintf("https://api.census.gov/data/%d/acs/acs1", year)

  # ---- 🔧 变量列表（根据研究课题修改） ----
  vars <- c(
    "NAME",
    "B23025_002E", # In labor force
    "B23025_003E", # Civilian labor force
    "B23025_004E", # Employed (civilian)
    "B23025_005E", # Unemployed
    "B23025_007E", # Not in labor force
    "B01003_001E" # Total population
  )

  url <- paste0(
    base_url,
    "?get=", paste(vars, collapse = ","),
    "&for=state:*"
  )

  response <- tryCatch(
    GET(url, timeout(30)),
    error = function(e) NULL
  )

  if (is.null(response) || status_code(response) != 200) {
    warning(sprintf("Failed to fetch ACS data for %d", year))
    return(NULL)
  }

  data <- fromJSON(content(response, "text"))

  # 第一行是变量名
  df <- as_tibble(data[-1, ], .name_repair = "minimal")
  names(df) <- data[1, ]

  df <- df %>%
    mutate(
      year = year,
      across(c(B23025_002E:B01003_001E), as.numeric)
    ) %>%
    rename(state_fips = state)

  return(df)
}

# 循环获取所有年份
acs_data <- list()
for (year in 2010:2023) {
  cat(sprintf("  Fetching ACS %d...", year))
  acs_year <- fetch_acs_year(year)
  if (!is.null(acs_year)) {
    acs_data[[as.character(year)]] <- acs_year
    cat(" done\n")
  } else {
    cat(" FAILED\n")
  }
  Sys.sleep(0.5) # 避免请求过快
}

acs_all <- bind_rows(acs_data)

# ==============================================================================
# 2. 变量重命名与计算
# ==============================================================================

acs_clean <- acs_all %>%
  rename(
    state_name = NAME,
    in_labor_force = B23025_002E,
    civilian_labor_force = B23025_003E,
    employed_civilian = B23025_004E,
    unemployed = B23025_005E,
    not_in_labor_force = B23025_007E,
    total_pop = B01003_001E
  ) %>%
  mutate(
    # 计算关键比率
    working_age_pop = in_labor_force + not_in_labor_force,
    lfp_rate = in_labor_force / working_age_pop * 100,
    emp_rate = employed_civilian / working_age_pop * 100,
    unemp_rate = unemployed / civilian_labor_force * 100
  )

cat(sprintf("\nFetched ACS data for %d state-years\n", nrow(acs_clean)))

# ==============================================================================
# 3. 州 FIPS 编码与缩写映射
# ==============================================================================

state_abbr <- tibble(
  state_fips = c(
    "01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13",
    "15", "16", "17", "18", "19", "20", "21", "22", "23", "24",
    "25", "26", "27", "28", "29", "30", "31", "32", "33", "34",
    "35", "36", "37", "38", "39", "40", "41", "42", "44", "45",
    "46", "47", "48", "49", "50", "51", "53", "54", "55", "56"
  ),
  state_abbr = c(
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
  )
)

# ==============================================================================
# 3.5 BLS LAUS 数据获取 (州级失业率)
# ==============================================================================

cat("\n========================================\n")
cat("FETCHING DATA: BLS LAUS (State Unemployment)\n")
cat("========================================\n\n")

bls_key <- "e40eea7ae13d4da79c2953dd1667e5bf"

# LAUS 州级年度失业率系列 ID: LASST + 2位FIPS + 0000000000003
series_ids <- paste0("LASST", state_abbr$state_fips, "0000000000003")
# BLS API 限制每次最多 50 个 series，这里有 51 个状态(含DC)，分成两批请求
batch1 <- series_ids[1:40]
batch2 <- series_ids[41:length(series_ids)]

fetch_bls_batch <- function(series_batch, start_year, end_year) {
  payload <- list(
    "seriesid" = series_batch,
    "startyear" = as.character(start_year),
    "endyear" = as.character(end_year),
    "registrationkey" = bls_key,
    "calculations" = FALSE,
    "annualaverage" = TRUE
  )

  response_json <- blsAPI(payload, 2)
  if (is.null(response_json)) {
    return(NULL)
  }

  data <- fromJSON(response_json)
  if (data$status != "REQUEST_SUCCEEDED") {
    warning(paste("BLS Error:", paste(data$message, collapse = "; ")))
    return(NULL)
  }

  parsed_list <- lapply(data$Results$series, function(s) {
    if (length(s$data) == 0) {
      return(NULL)
    }
    # 取年度平均数据 (M13)
    s$data %>%
      as_tibble() %>%
      filter(period == "M13") %>%
      select(year, value) %>%
      mutate(
        state_fips = substr(s$seriesID, 6, 7),
        bls_unemp_rate = as.numeric(value)
      ) %>%
      select(state_fips, year, bls_unemp_rate)
  })
  bind_rows(parsed_list)
}

cat("Fetching BLS LAUS data batch 1...\n")
bls_data1 <- fetch_bls_batch(batch1, 2010, 2023)
cat("Fetching BLS LAUS data batch 2...\n")
bls_data2 <- fetch_bls_batch(batch2, 2010, 2023)

bls_all <- bind_rows(bls_data1, bls_data2) %>%
  mutate(year = as.numeric(year))

cat(sprintf("Fetched BLS data for %d state-years\n", nrow(bls_all)))


# ==============================================================================
# 4. 政策处理变量定义
# ==============================================================================

# ---- 🔧 处理时间（根据研究课题修改） ----
# 示例：Clean Slate Laws 各州实施年份
clean_slate_dates <- tibble(
  state_fips = c("42", "49", "34", "26", "09", "10", "51", "40", "08", "06", "27", "36"),
  state_name_treat = c(
    "Pennsylvania", "Utah", "New Jersey", "Michigan", "Connecticut",
    "Delaware", "Virginia", "Oklahoma", "Colorado", "California",
    "Minnesota", "New York"
  ),
  treat_year_analysis = c(2018, 2019, 2019, 2020, 2021, 2021, 2021, 2022, 2022, 2022, 2023, 2024)
)

# ==============================================================================
# 5. 构建面板数据
# ==============================================================================

panel_data <- acs_clean %>%
  # 添加州缩写
  left_join(state_abbr, by = "state_fips") %>%
  # 合并 BLS 失业率数据
  left_join(bls_all, by = c("state_fips", "year")) %>%
  # 添加处理信息
  left_join(
    clean_slate_dates %>% select(state_fips, treat_year = treat_year_analysis),
    by = "state_fips"
  ) %>%
  mutate(
    # 未处理州 treat_year = 0
    treat_year = replace_na(treat_year, 0),
    # Sun-Abraham 的 cohort（未处理 = Inf）
    cohort = ifelse(treat_year == 0, Inf, treat_year),
    # 处理后指示变量
    post = as.integer(year >= treat_year & treat_year > 0),
    # 曾经处理指示变量
    treated = as.integer(treat_year > 0 & treat_year <= 2024),
    # 相对处理时间
    rel_time = ifelse(treat_year > 0, year - treat_year, NA_integer_)
  ) %>%
  # 创建州数值 ID
  mutate(state_id = as.integer(factor(state_fips)))

# 州人口权重（2019 年基线）
state_pop <- acs_clean %>%
  filter(year == 2019) %>%
  select(state_fips, pop_2019 = total_pop)

panel_data <- panel_data %>%
  left_join(state_pop, by = "state_fips")

# ==============================================================================
# 6. 数据质量检查
# ==============================================================================

cat("\n========================================\n")
cat("DATA QUALITY CHECKS\n")
cat("========================================\n\n")

cat(sprintf("Total observations: %d\n", nrow(panel_data)))
cat(sprintf("States: %d\n", n_distinct(panel_data$state_fips)))
cat(sprintf("Years: %d - %d\n", min(panel_data$year), max(panel_data$year)))
cat(sprintf("Treated states: %d\n", sum(panel_data$treated[panel_data$year == 2023])))
cat(sprintf("Control states: %d\n", sum(!panel_data$treated[panel_data$year == 2023])))

# 缺失值检查
cat(sprintf("\nMissing values:\n"))
cat(sprintf("  emp_rate: %d\n", sum(is.na(panel_data$emp_rate))))
cat(sprintf("  lfp_rate: %d\n", sum(is.na(panel_data$lfp_rate))))
cat(sprintf("  unemp_rate: %d\n", sum(is.na(panel_data$unemp_rate))))
cat(sprintf("  bls_unemp_rate: %d\n", sum(is.na(panel_data$bls_unemp_rate))))


# ==============================================================================
# 7. 保存数据
# ==============================================================================

dir.create("data", showWarnings = FALSE, recursive = TRUE)
saveRDS(panel_data, "data/panel_data.rds")

cat(sprintf("\n✅ Panel data saved: data/panel_data.rds (%d rows)\n", nrow(panel_data)))

# 保存描述性统计
desc_stats <- panel_data %>%
  filter(year == 2019) %>%
  group_by(treated) %>%
  summarize(
    n = n(),
    emp_rate_mean = mean(emp_rate, na.rm = TRUE),
    emp_rate_sd = sd(emp_rate, na.rm = TRUE),
    lfp_rate_mean = mean(lfp_rate, na.rm = TRUE),
    lfp_rate_sd = sd(lfp_rate, na.rm = TRUE),
    unemp_rate_mean = mean(unemp_rate, na.rm = TRUE),
    unemp_rate_sd = sd(unemp_rate, na.rm = TRUE),
    bls_unemp_rate_mean = mean(bls_unemp_rate, na.rm = TRUE),
    bls_unemp_rate_sd = sd(bls_unemp_rate, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(treated = ifelse(treated == 1, "Treated", "Control"))

write.csv(desc_stats, "data/descriptive_stats.csv", row.names = FALSE)
cat("✅ Descriptive statistics saved: data/descriptive_stats.csv\n")
