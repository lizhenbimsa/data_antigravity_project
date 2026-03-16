# ============================================================
# APEP RDD 分析代码模板 — 03_main_analysis_rdd.R
# 断点回归设计（Regression Discontinuity Design）
# ============================================================

source("code/00_packages.R")
library(rdrobust)
library(rddensity)

# ---- 1. 加载数据 ----
df <- readRDS("output/analysis_data.rds")

# 定义变量（根据研究修改）
Y_VAR     <- "outcome"        # 结果变量
X_VAR     <- "running_var"    # 运行变量（如年龄、收入、分数等）
CUTOFF    <- 65               # 断点值（如 65 岁）

Y <- df[[Y_VAR]]
X <- df[[X_VAR]]

# ---- 2. 主要 RDD 估计 ----
cat("=== 2. 主要 RDD 估计（MSE 最优带宽） ===\n")
rd_main <- rdrobust(Y, X, c = CUTOFF)
summary(rd_main)

# ---- 3. RD 散点图 ----
cat("\n=== 3. RD 散点图 ===\n")
pdf("figures/rd_plot.pdf", width = 10, height = 6)
rdplot(Y, X, c = CUTOFF,
       title  = "RD Plot",
       x.label = "Running Variable",
       y.label = "Outcome Variable")
dev.off()

# ---- 4. McCrary 密度检验 ----
cat("\n=== 4. 操纵检验（密度检验） ===\n")
dens_test <- rddensity(X, c = CUTOFF)
summary(dens_test)

pdf("figures/density_test.pdf", width = 10, height = 6)
rdplotdensity(dens_test, X,
              title = "McCrary Density Test at Cutoff")
dev.off()

# ---- 5. 带宽敏感性分析 ----
cat("\n=== 5. 带宽敏感性分析 ===\n")
bw_optimal <- rd_main$bws[1, 1]
bw_factors <- c(0.5, 0.75, 1.0, 1.25, 1.5, 2.0)

bw_results <- data.frame()
for (f in bw_factors) {
  rd_bw <- rdrobust(Y, X, c = CUTOFF, h = bw_optimal * f)
  bw_results <- rbind(bw_results, data.frame(
    bandwidth  = bw_optimal * f,
    factor     = f,
    estimate   = rd_bw$coef[1],
    se         = rd_bw$se[3],  # robust SE
    pvalue     = rd_bw$pv[3],
    ci_lower   = rd_bw$ci[3, 1],
    ci_upper   = rd_bw$ci[3, 2],
    n_left     = rd_bw$N_h[1],
    n_right    = rd_bw$N_h[2]
  ))
}
print(bw_results)

# 可视化带宽敏感性
p_bw <- ggplot(bw_results, aes(x = factor, y = estimate)) +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = ci_lower, ymax = ci_upper), width = 0.1) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "red") +
  geom_vline(xintercept = 1, linetype = "dotted", color = "blue") +
  labs(title = "Bandwidth Sensitivity Analysis",
       x = "Bandwidth multiplier",
       y = "RD Estimate") +
  theme_minimal()
ggsave("figures/bandwidth_sensitivity.pdf", p_bw, width = 10, height = 6)

# ---- 6. 协变量平衡检验 ----
cat("\n=== 6. 协变量平衡检验 ===\n")
covariates <- c("covar1", "covar2", "covar3")  # 替换实际协变量名

cov_results <- data.frame()
for (cov in covariates) {
  if (cov %in% names(df)) {
    rd_cov <- rdrobust(df[[cov]], X, c = CUTOFF)
    cov_results <- rbind(cov_results, data.frame(
      covariate = cov,
      estimate  = rd_cov$coef[1],
      se        = rd_cov$se[3],
      pvalue    = rd_cov$pv[3]
    ))
  }
}
if (nrow(cov_results) > 0) {
  cat("协变量在断点处的连续性检验:\n")
  print(cov_results)
}

# ---- 7. 安慰剂断点检验 ----
cat("\n=== 7. 安慰剂断点检验 ===\n")
placebo_cutoffs <- c(CUTOFF - 5, CUTOFF - 3, CUTOFF + 3, CUTOFF + 5)

placebo_results <- data.frame()
for (pc in placebo_cutoffs) {
  rd_placebo <- rdrobust(Y, X, c = pc)
  placebo_results <- rbind(placebo_results, data.frame(
    cutoff   = pc,
    estimate = rd_placebo$coef[1],
    se       = rd_placebo$se[3],
    pvalue   = rd_placebo$pv[3]
  ))
}
cat("安慰剂断点结果:\n")
print(placebo_results)

# ---- 8. 不同多项式阶数 ----
cat("\n=== 8. 多项式阶数敏感性 ===\n")
for (p in 1:3) {
  rd_p <- rdrobust(Y, X, c = CUTOFF, p = p)
  cat(sprintf("p = %d: 估计 = %.4f, SE = %.4f, p值 = %.4f\n",
              p, rd_p$coef[1], rd_p$se[3], rd_p$pv[3]))
}

# ---- 9. 保存结果 ----
dir.create("tables", showWarnings = FALSE)
save(rd_main, bw_results, cov_results, placebo_results,
     file = "output/rdd_results.RData")

cat("\n✅ RDD 分析完成\n")
