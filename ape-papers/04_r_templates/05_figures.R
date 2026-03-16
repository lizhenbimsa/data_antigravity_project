# ============================================================
# APEP 图表生成模板 — 05_figures.R
# 生成论文所需的所有图表
# ============================================================

source("code/00_packages.R")

# ---- 0. 全局主题设置 ----
theme_apep <- theme_minimal(base_size = 12) +
  theme(
    plot.title    = element_text(face = "bold", size = 14),
    plot.subtitle = element_text(color = "grey40"),
    axis.title    = element_text(face = "bold"),
    legend.position = "bottom",
    panel.grid.minor = element_blank()
  )
theme_set(theme_apep)

# 加载数据
panel <- readRDS("output/panel_data.rds")

dir.create("figures", showWarnings = FALSE)

# ---- 1. 平行趋势图 ----
p_trends <- panel %>%
  mutate(group = ifelse(is.infinite(treat_year), "Control", "Treated")) %>%
  group_by(year, group) %>%
  summarise(mean_y = mean(emp_rate, na.rm = TRUE), .groups = "drop") %>%
  ggplot(aes(x = year, y = mean_y, color = group, linetype = group)) +
  geom_line(linewidth = 1.2) +
  geom_point(size = 2) +
  labs(
    title = "Pre-Treatment Parallel Trends",
    x = "Year", y = "Employment Rate",
    color = "Group", linetype = "Group"
  ) +
  scale_color_manual(values = c("Control" = "#2C3E50", "Treated" = "#E74C3C"))

ggsave("figures/parallel_trends.pdf", p_trends, width = 10, height = 6)

# ---- 2. 事件研究图（自定义版本） ----
# 假设已有事件研究系数结果
# est_sa 从 03_main_analysis.R 加载
load("output/rdd_results.RData")  # 或相应结果文件

# 如果使用 fixest 的 sunab:
# coefs <- data.frame(
#   rel_year = ...事件时间...,
#   estimate = ...系数...,
#   ci_low   = ...下界...,
#   ci_high  = ...上界...
# )

# p_event <- ggplot(coefs, aes(x = rel_year, y = estimate)) +
#   geom_point(size = 2.5) +
#   geom_errorbar(aes(ymin = ci_low, ymax = ci_high), width = 0.2) +
#   geom_hline(yintercept = 0, linetype = "dashed", color = "red") +
#   geom_vline(xintercept = -0.5, linetype = "dotted", color = "grey50") +
#   labs(
#     title = "Event Study Estimates",
#     x = "Years Relative to Treatment",
#     y = "Estimated Effect"
#   )
# ggsave("figures/event_study.pdf", p_event, width = 10, height = 6)

# ---- 3. 描述性统计图 ----
p_dist <- panel %>%
  ggplot(aes(x = emp_rate, fill = factor(treated))) +
  geom_density(alpha = 0.5) +
  labs(
    title = "Distribution of Employment Rate",
    x = "Employment Rate", y = "Density",
    fill = "Treated"
  ) +
  scale_fill_manual(values = c("0" = "#3498DB", "1" = "#E74C3C"),
                    labels = c("Control", "Treated"))

ggsave("figures/distribution.pdf", p_dist, width = 10, height = 6)

# ---- 4. 州级热力图 ----
# p_heatmap <- panel %>%
#   ggplot(aes(x = year, y = reorder(state_name, treat_year), fill = emp_rate)) +
#   geom_tile() +
#   scale_fill_gradient2(low = "blue", mid = "white", high = "red",
#                        midpoint = median(panel$emp_rate, na.rm = TRUE)) +
#   labs(title = "State-Year Employment Rate Heatmap",
#        x = "Year", y = "State", fill = "Emp Rate")
# ggsave("figures/heatmap.pdf", p_heatmap, width = 12, height = 15)

cat("✅ 所有图表已保存到 figures/ 目录\n")
