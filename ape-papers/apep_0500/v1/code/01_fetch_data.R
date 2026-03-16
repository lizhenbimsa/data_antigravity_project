# 01_fetch_data.R
# 从 Census ACS API 获取数据，构建交错 DiD 面板数据集

source("code/00_packages.R")

# ── 常量定义 ──────────────────────────────────────────────────────────────────

YEARS <- 2010:2023
DATA_DIR <- "data"
dir.create(DATA_DIR, showWarnings = FALSE)

# 州 FIPS → 缩写映射（全部 51 个）
FIPS_TO_STATE <- c(
  "01"="AL","02"="AK","04"="AZ","05"="AR","06"="CA","08"="CO","09"="CT",
  "10"="DE","11"="DC","12"="FL","13"="GA","15"="HI","16"="ID","17"="IL",
  "18"="IN","19"="IA","20"="KS","21"="KY","22"="LA","23"="ME","24"="MD",
  "25"="MA","26"="MI","27"="MN","28"="MS","29"="MO","30"="MT","31"="NE",
  "32"="NV","33"="NH","34"="NJ","35"="NM","36"="NY","37"="NC","38"="ND",
  "39"="OH","40"="OK","41"="OR","42"="PA","44"="RI","45"="SC","46"="SD",
  "47"="TN","48"="TX","49"="UT","50"="VT","51"="VA","53"="WA","54"="WV",
  "55"="WI","56"="WY"
)

# 处理组：州 FIPS → 政策实施年份
TREAT_TIMING <- tibble(
  state_fips = c("06", "36", "53", "34", "24"),
  treat_year = c(2016L, 2017L, 2018L, 2019L, 2020L)
)

# ── ACS 变量说明 ───────────────────────────────────────────────────────────────
# B23025_002E: 劳动力人口（16岁以上）
# B23025_003E: 就业人口
# B23025_004E: 受雇人口（civilian employed）
# B23025_005E: 失业人口
# B23025_007E: 不在劳动力中
# B01003_001E: 总人口（用于 2019 年权重）
# B23001_026E: 女性劳动力人口（16岁以上）
# B23001_001E: 总劳动力人口（用于分母）

# ── 单年数据获取函数 ───────────────────────────────────────────────────────────

fetch_acs_year <- function(year) {
  # 女性劳动参与相关变量
  vars <- paste(
    "NAME",
    "B23025_002E",  # 劳动力总人口
    "B23025_003E",  # 就业人口
    "B23025_005E",  # 失业人口
    "B23001_026E",  # 女性劳动力人口（16+）
    "B23001_001E",  # 劳动力年龄总人口（分母）
    "B01003_001E",  # 总人口
    sep = ","
  )

  url <- sprintf(
    "https://api.census.gov/data/%d/acs/acs1?get=%s&for=state:*",
    year, vars
  )

  resp <- tryCatch(GET(url, timeout(30)), error = function(e) NULL)

  if (is.null(resp) || status_code(resp) != 200) {
    warning(sprintf("⚠ %d 年数据获取失败（状态码：%s）",
                    year, if (is.null(resp)) "连接错误" else status_code(resp)))
    return(NULL)
  }

  raw <- fromJSON(content(resp, as = "text", encoding = "UTF-8"))
  df  <- as_tibble(raw[-1, ], .name_repair = "minimal")
  colnames(df) <- raw[1, ]

  df %>%
    rename(
      state_name   = NAME,
      lf_total     = B23025_002E,
      employed     = B23025_003E,
      unemployed   = B23025_005E,
      female_lf    = B23001_026E,
      lf_age_pop   = B23001_001E,
      total_pop    = B01003_001E,
      state_fips   = state
    ) %>%
    mutate(
      year       = year,
      across(c(lf_total, employed, unemployed,
               female_lf, lf_age_pop, total_pop), as.numeric)
    )
}

# ── 循环获取各年数据 ───────────────────────────────────────────────────────────

raw_list <- vector("list", length(YEARS))
names(raw_list) <- as.character(YEARS)

for (yr in YEARS) {
  cat(sprintf("正在获取 %d 年数据...\n", yr))
  result <- fetch_acs_year(yr)
  if (is.null(result)) next
  raw_list[[as.character(yr)]] <- result
  Sys.sleep(0.3)  # 避免 API 限速
}

raw_panel <- bind_rows(raw_list)
cat(sprintf("✓ 原始面板：%d 行，覆盖年份：%s\n",
            nrow(raw_panel),
            paste(sort(unique(raw_panel$year)), collapse = ", ")))

# ── 构建分析面板 ───────────────────────────────────────────────────────────────

# 提取 2019 年人口权重
pop_2019 <- raw_panel %>%
  filter(year == 2019) %>%
  select(state_fips, state_pop = total_pop)

panel_data <- raw_panel %>%
  # 添加州缩写
  mutate(state_abbr = FIPS_TO_STATE[state_fips]) %>%
  # 合并处理时间
  left_join(TREAT_TIMING, by = "state_fips") %>%
  # cohort：从未处理州设为 Inf
  mutate(
    cohort     = if_else(is.na(treat_year), Inf, as.numeric(treat_year)),
    treated    = !is.na(treat_year),
    post       = if_else(treated, year >= treat_year, FALSE),
    rel_time   = if_else(treated, as.integer(year - treat_year), NA_integer_)
  ) %>%
  # 计算比率
  mutate(
    emp_rate   = employed   / lf_age_pop,   # 就业率
    lfp_rate   = lf_total   / lf_age_pop,   # 劳动参与率
    unemp_rate = unemployed / lf_total,     # 失业率
    female_lfp_rate = female_lf / lf_age_pop  # 女性劳动参与率（核心结果变量）
  ) %>%
  # 合并人口权重
  left_join(pop_2019, by = "state_fips") %>%
  # 仅保留有效观测
  filter(!is.na(state_abbr), lf_age_pop > 0)

# ── 数据质量检查 ───────────────────────────────────────────────────────────────

cat("\n── 数据质量检查 ──────────────────────────────────────\n")
cat(sprintf("总观测数：%d\n", nrow(panel_data)))
cat(sprintf("州数量：%d\n", n_distinct(panel_data$state_fips)))
cat(sprintf("年份范围：%d–%d\n", min(panel_data$year), max(panel_data$year)))
cat(sprintf("处理州数量：%d\n", n_distinct(filter(panel_data, treated)$state_fips)))
cat(sprintf("从未处理州数量：%d\n", n_distinct(filter(panel_data, !treated)$state_fips)))
cat(sprintf("female_lfp_rate 缺失值：%d\n", sum(is.na(panel_data$female_lfp_rate))))
cat(sprintf("female_lfp_rate 范围：[%.4f, %.4f]\n",
            min(panel_data$female_lfp_rate, na.rm = TRUE),
            max(panel_data$female_lfp_rate, na.rm = TRUE)))

# 处理组 cohort 分布
cat("\n处理组 cohort 分布：\n")
panel_data %>%
  filter(treated) %>%
  distinct(state_abbr, cohort) %>%
  arrange(cohort) %>%
  print()

# ── 描述性统计 ────────────────────────────────────────────────────────────────

desc_stats <- panel_data %>%
  group_by(treated, year) %>%
  summarise(
    n_states          = n_distinct(state_fips),
    mean_female_lfp   = mean(female_lfp_rate, na.rm = TRUE),
    sd_female_lfp     = sd(female_lfp_rate,   na.rm = TRUE),
    mean_lfp_rate     = mean(lfp_rate,         na.rm = TRUE),
    mean_unemp_rate   = mean(unemp_rate,       na.rm = TRUE),
    .groups = "drop"
  )

write_csv(desc_stats, file.path(DATA_DIR, "descriptive_stats.csv"))
cat(sprintf("\n✓ 描述性统计已保存至 %s\n", file.path(DATA_DIR, "descriptive_stats.csv")))

# ── 保存面板数据 ───────────────────────────────────────────────────────────────

saveRDS(panel_data, file.path(DATA_DIR, "panel_data.rds"))
cat(sprintf("✓ 面板数据已保存至 %s\n", file.path(DATA_DIR, "panel_data.rds")))