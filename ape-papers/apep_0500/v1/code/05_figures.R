source("code/00_packages.R")  # 加载所需R包 httr, jsonlite, ggplot2 等

# 读取数据和结果对象
panel_data <- readRDS("data/panel_data.rds")
results <- readRDS("data/main_results.rds")

library(ggplot2)
library(dplyr)
library(scales)
library(gridExtra)
library(ggrepel)

# 1. 事件研究图：基于 results$event_study$emp 生成，包含系数及95%置信区间
# 假设results$event_study$emp格式为：data.frame，列包括 event_time, estimate, conf.low, conf.high

event_study_df <- results$event_study$emp %>%
  rename(
    event_time = event_time,
    estimate = estimate,
    conf.low = conf.low,
    conf.high = conf.high
  )

# 事件研究图
p1 <- ggplot(event_study_df, aes(x = event_time, y = estimate)) +
  geom_hline(yintercept = 0, color = "grey50", linetype = "dashed") +  # 零线
  geom_vline(xintercept = 0, color = "red", linetype = "dashed") +    # 事件时点竖线t=0
  geom_point(size = 2) +
  geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width = 0.2) +
  labs(
    title = "事件研究：最低工时保障法对女性劳动参与率影响",
    subtitle = "系数估计及95%置信区间",
    x = "事件时间 (实施政策的年份为0)",
    y = "估计的处理效应 (女性劳动参与率变动)"
  ) +
  theme_bw(base_size = 14)

ggsave("figures/01_event_study.pdf", p1, width = 8, height = 5)

# 2. 平行趋势图
# 按处理组分组绘制女性劳动参与率均值随时间变化的趋势
# 需要构造变量 treatment_status（treated / control）
# 由 panel_data 中，结合最低工时保障法开始年份变量构造

# 增加当年处理状态变量treated: 1=treated已实施，0=未实施
implementation_years <- tibble::tribble(
  ~state, ~start_year,
  "加州", 2016,
  "纽约", 2017,
  "华盛顿州", 2018,
  "新泽西州", 2019,
  "马里兰州", 2020
)

panel_trend <- panel_data %>%
  # 假设有 state, year, female_lfpr 变量
  left_join(implementation_years, by = c("state")) %>%
  mutate(
    treated = case_when(
      is.na(start_year) ~ "未实施",
      year >= start_year ~ "已实施",
      TRUE ~ "未实施"
    )
  )

# 计算每年、每个treated状态的女性劳动参与率均值
trend_summary <- panel_trend %>%
  group_by(year, treated) %>%
  summarise(mean_lfpr = mean(female_lfpr, na.rm = TRUE), .groups = "drop")

p2 <- ggplot(trend_summary, aes(x = year, y = mean_lfpr, color = treated)) +
  geom_line(size = 1) +
  geom_point() +
  labs(
    title = "最低工时保障法实施州女性劳动参与率趋势",
    subtitle = "按处理状态分组的均值变化",
    x = "年份",
    y = "平均女性劳动参与率",
    color = "处理状态"
  ) +
  theme_minimal(base_size = 14) +
  scale_color_manual(values = c("已实施" = "#1B9E77", "未实施" = "#D95F02"))

ggsave("figures/02_parallel_trends.pdf", p2, width = 8, height = 5)

# 3. 处理实施分布图（地图）
# 可视化5个处理州及其实施年份
# 地图数据使用州边界数据，假定使用maps包提供的state数据

library(maps)
library(ggplot2)
library(dplyr)

us_states_map <- map_data("state")

# 处理州名称映射成英文小写（maps中州名均为英文小写）
state_name_map <- tibble::tribble(
  ~chinese, ~english,
  "加州", "california",
  "纽约", "new york",
  "华盛顿州", "washington",
  "新泽西州", "new jersey",
  "马里兰州", "maryland"
)

impl_map <- implementation_years %>%
  left_join(state_name_map, by = c("state" = "chinese")) %>%
  mutate(implemented = TRUE)

map_df <- us_states_map %>%
  left_join(impl_map, by = c("region" = "english")) %>%
  mutate(policy_year = ifelse(is.na(start_year), NA_integer_, start_year))

p3 <- ggplot(map_df, aes(x = long, y = lat, group = group, fill = policy_year)) +
  geom_polygon(color = "black", size = 0.3) +
  scale_fill_gradient(
    na.value = "grey90",
    low = "lightblue",
    high = "darkblue",
    name = "最低工时保障法实施年份"
  ) +
  labs(
    title = "最低工时保障法实施州分布图",
    subtitle = "蓝色越深代表实施年份越晚，灰色为未实施州"
  ) +
  coord_fixed(1.3) +
  theme_minimal(base_size = 14) +
  theme(
    axis.title = element_blank(),
    axis.text = element_blank(),
    axis.ticks = element_blank()
  )

ggsave("figures/03_policy_map.pdf", p3, width = 8, height = 5)

# 4. 跨估计量的系数对比图
# 结合 results$agg_att, results$sunab 等，绘制不同估计量的ATT对比
# 假设results包含不同估计对象及其点估计和置信区间

# 组装数据框用于绘图
coef_df <- bind_rows(
  tibble(
    estimator = "Callaway-Sant'Anna ATT",
    estimate = results$agg_att$estimate,
    conf.low = results$agg_att$conf.low,
    conf.high = results$agg_att$conf.high
  ),
  tibble(
    estimator = "Sun & Abraham ATT",
    estimate = results$sunab$estimate,
    conf.low = results$sunab$conf.low,
    conf.high = results$sunab$conf.high
  )
  # 可根据具体results结构添加更多估计量
)

# 按照估计值排序
coef_df <- coef_df %>%
  mutate(estimator = factor(estimator, levels = estimator))

p4 <- ggplot(coef_df, aes(x = estimator, y = estimate)) +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width = 0.2) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "grey50") +
  labs(
    title = "不同多时期DiD估计量女性劳动参与率影响对比",
    subtitle = "处理效应及95%置信区间",
    x = "估计方法",
    y = "估计的ATT"
  ) +
  theme_bw(base_size = 14)

ggsave("figures/04_att_comparison.pdf", p4, width = 7, height = 5)

# 输出完成提示
message("所有图表已生成并保存至 figures/ 目录。")