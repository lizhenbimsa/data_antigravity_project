# 03_main_analysis.R
# 本脚本进行最低工时保障法对女性劳动参与率的影响的因果分析
# 使用多时期多组Staggered DiD设计，结合TWFE和Sun-Abraham方法

# ----------------------------
# 1. 载入必要包和数据 ----
source("code/00_packages.R")

# 读取面板数据，panel_data已完整包含treat_year、cohort、post、treated变量
panel_data <- readRDS("data/panel_data.rds")


# ----------------------------
# 2. 样本描述 ----

# 样本量、州数量、年份信息
cat("样本总观测数:", nrow(panel_data), "\n")
cat("包含州数量:", length(unique(panel_data$state_fips)), "\n")
cat("年份区间:", min(panel_data$year), "-", max(panel_data$year), "\n")

# 处理组和对照组观测数
table_treated <- table(panel_data$treated)
cat("处理组观测数:", table_treated["1"], "\n")
cat("对照组观测数:", table_treated["0"], "\n")


# ----------------------------
# 3. 2019年基准描述性统计（按处理状态分组） ----
library(dplyr)
library(broom)

desc_2019 <- panel_data %>%
  filter(year == 2019) %>%
  group_by(treated) %>%
  summarise(
    obs = n(),
    mean_emp_rate = mean(emp_rate, na.rm = TRUE),
    sd_emp_rate = sd(emp_rate, na.rm = TRUE),
    mean_lfp_rate = mean(lfp_rate, na.rm = TRUE),
    sd_lfp_rate = sd(lfp_rate, na.rm = TRUE),
    mean_unemp_rate = mean(unemp_rate, na.rm = TRUE),
    sd_unemp_rate = sd(unemp_rate, na.rm = TRUE)
  )

print(desc_2019)


# ----------------------------
# 4. TWFE 估计（修正双重差分） ----
library(fixest)

# 4.1 emp_rate ~ post, 控制州和年固定效应，州聚类
twfe_emp <- feols(emp_rate ~ post | state_fips + year, cluster = ~state_fips, data = panel_data)

# 4.2 lfp_rate ~ post
twfe_lfp <- feols(lfp_rate ~ post | state_fips + year, cluster = ~state_fips, data = panel_data)

# 4.3 unemp_rate ~ post
twfe_unemp <- feols(unemp_rate ~ post | state_fips + year, cluster = ~state_fips, data = panel_data)


# 打印TWFE回归摘要
cat("\nTWFE 基准回归结果 - emp_rate:\n")
print(summary(twfe_emp))
cat("\nTWFE 基准回归结果 - lfp_rate:\n")
print(summary(twfe_lfp))
cat("\nTWFE 基准回归结果 - unemp_rate:\n")
print(summary(twfe_unemp))


# ----------------------------
# 5. Sun-Abraham 分析（分组-时间特异处理效应） ----

# 5.1 使用 fixest::sunab 构造工具变量
# cohort = 政策实施年份（treat_year），year = 当前年份，ref.p = -1 指定事件时间相差1年前作为基准期

sa_emp <- feols(
  emp_rate ~ sunab(cohort, year, ref.p = -1) | state_fips + year,
  cluster = ~state_fips,
  data = panel_data
)

sa_lfp <- feols(
  lfp_rate ~ sunab(cohort, year, ref.p = -1) | state_fips + year,
  cluster = ~state_fips,
  data = panel_data
)

sa_unemp <- feols(
  unemp_rate ~ sunab(cohort, year, ref.p = -1) | state_fips + year,
  cluster = ~state_fips,
  data = panel_data
)


# 5.2 提取ATT汇总结果 - 使用aggregate聚合，返回fixest对象
agg_att_emp <- aggregate(sa_emp, agg = "ATT")
agg_att_lfp <- aggregate(sa_lfp, agg = "ATT")
agg_att_unemp <- aggregate(sa_unemp, agg = "ATT")

# 5.3 构造汇总表，强制转换为data.frame，避免直接使用did包内部特殊字段
get_summary_df <- function(agg_result, outcome_name) {
  df <- as.data.frame(coeftable(agg_result))
  # 注意coeftable列名一般为 Estimate、Std. Error、t value、Pr(>|t|)
  # 还需要事件时间信息，从rownames或term中提取
  df$term <- rownames(df)

  # 从term字符串提取相对事件时间，此处term格式一般为 "group-time" 或 "_(year::X)"
  # fixest包Sun-Abraham aggregate结果中term格式通常是 e.g. "att.group 2016"
  # 参考term中数字，我们用正则匹配第一组数字作为event_time
  library(stringr)
  # 如果term中含有"year::"格式，提取后缀数字作为rel_time
  rel_time <- str_extract(df$term, "-?\\d+")
  df$rel_time <- as.integer(rel_time)

  df$outcome <- outcome_name
  df <- dplyr::select(df, outcome, term, rel_time, Estimate, `Std. Error`, `Pr(>|t|)`)

  # 计算95%置信区间
  df <- df %>%
    mutate(
      ci_lower = Estimate - 1.96 * `Std. Error`,
      ci_upper = Estimate + 1.96 * `Std. Error`,
      sig = ifelse(`Pr(>|t|)` < 0.05, TRUE, FALSE)
    )
  return(df)
}

summary_emp <- get_summary_df(agg_att_emp, "emp_rate")
summary_lfp <- get_summary_df(agg_att_lfp, "lfp_rate")
summary_unemp <- get_summary_df(agg_att_unemp, "unemp_rate")

# 合并所有结果
summary_table <- bind_rows(summary_emp, summary_lfp, summary_unemp)

# ----------------------------
# 6. 事件研究系数提取 ----

extract_event_coeffs <- function(fe_model, outcome_name) {
  ct <- as.data.frame(coeftable(fe_model))
  ct$term <- rownames(ct)

  # 只保留事件时间相关的系数，匹配字符串中包含"year::"
  event_rows <- grepl("year::", ct$term)

  df <- ct[event_rows, ]
  # 提取事件时间，形式如 "sunab::year::+2" 或 "year::-1"
  library(stringr)
  df$estimate <- df$Estimate
  df$se <- df$`Std. Error`
  df$pval <- df$`Pr(>|t|)`
  df$rel_time <- as.integer(str_extract(df$term, "-?\\d+"))
  df$outcome <- outcome_name
  
  df <- dplyr::select(df, outcome, term, rel_time, estimate, se, pval)
  return(df)
}

event_study_emp <- extract_event_coeffs(sa_emp, "emp_rate")
event_study_lfp <- extract_event_coeffs(sa_lfp, "lfp_rate")
event_study_unemp <- extract_event_coeffs(sa_unemp, "unemp_rate")


# ----------------------------
# 7. 预趋势检验 ----

# 预趋势关注rel_time < 0的系数, 检查显著数量

pre_trend_count <- function(event_df) {
  pre_periods <- event_df %>% filter(rel_time < 0)
  num_signif <- sum(pre_periods$pval < 0.05, na.rm = TRUE)
  total_pre <- nrow(pre_periods)
  cat(sprintf("%s 预趋势期显著系数数量：%d / %d\n",
              unique(event_df$outcome), num_signif, total_pre))
  return(list(num_signif = num_signif, total_pre = total_pre))
}

pretrend_emp <- pre_trend_count(event_study_emp)
pretrend_lfp <- pre_trend_count(event_study_lfp)
pretrend_unemp <- pre_trend_count(event_study_unemp)


# ----------------------------
# 8. 保存结果 ----
results <- list(
  twfe = list(emp = twfe_emp, lfp = twfe_lfp, unemp = twfe_unemp),
  sunab = list(emp = sa_emp, lfp = sa_lfp, unemp = sa_unemp),
  agg_att = list(emp = agg_att_emp, lfp = agg_att_lfp, unemp = agg_att_unemp),
  summary_table = summary_table,
  event_study_coefs = list(emp = event_study_emp, lfp = event_study_lfp, unemp = event_study_unemp),
  pretrend_test = list(emp = pretrend_emp, lfp = pretrend_lfp, unemp = pretrend_unemp)
)

saveRDS(results, "data/main_results.rds")

# 写出汇总表为CSV（包含ATT估计值、标准误、置信区间、显著性）
library(readr)
write_csv(summary_table, "data/main_results_summary.csv")

cat("分析完成，结果已保存至 data/main_results.rds 和 data/main_results_summary.csv\n")