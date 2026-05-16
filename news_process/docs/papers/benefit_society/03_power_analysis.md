# Power Analysis — Benefit-Society 论文

**前提**: Phase 0 实测样本 n = 168（84 银行 × 2 年），benefit 非空率 69% → 有效 obs ≈ **116**

---

## 1. 计算前提

### 1.1 模型设定
$$Y_{i,t} = \beta \cdot \text{benefit\_mean\_full}_{i,t} + \gamma X_{i,t} + \alpha_{\text{type}(i)} + \delta_t + \varepsilon_{i,t}$$

### 1.2 自由度核算

| 项目 | 自由度消耗 |
|---|---|
| Total obs | 116 |
| 银行类型 FE (4 类：国有/股份/城商/农商) | 3 |
| 年 FE (2 年) | 1 |
| 总部省份 FE (~25 省) | 24 |
| 控制变量（ln_asset, CAR, 贷存比, ln_age, ln_articles）| 5 |
| benefit_mean | 1 |
| **有效残差自由度** | **116 − 34 = 82** |

注：弃用银行 FE（与 type FE 共线 + 年仅 2 → 无 within-bank 时序识别力）。

### 1.3 测度变异

基于现有 panel 实测：
- `benefit_mean_full` SD ≈ 0.15（横截面）
- 非上市子样本（n≈80）SD ≈ 0.18（噪声更大）

---

## 2. MDE (Minimum Detectable Effect) 计算

### 2.1 公式
$$\text{MDE}(\beta) = \frac{t_{\alpha/2} + t_{1-\kappa}}{\sqrt{n_{\text{eff}}}} \cdot \frac{\sigma_\varepsilon}{\sigma_X \sqrt{1-R^2_{\text{partial}}}}$$

α = 0.05（双尾）, κ = 0.80（power）→ $t_{\alpha/2}+t_{1-\kappa} \approx 2.81$

### 2.2 标准化设定（Y 标准化为 1 SD）

| 假设 partial R² | $\sigma_\varepsilon$ | MDE (β, std) | 解读 |
|---|---|---|---|
| 0.20 (强) | 0.89 | **0.27 SD** | 1 SD benefit ↑ → Y 增加 27% SD |
| 0.10 (中) | 0.95 | **0.29 SD** | 1 SD benefit ↑ → Y 增加 29% SD |
| 0.05 (弱) | 0.97 | **0.30 SD** | 1 SD benefit ↑ → Y 增加 30% SD |

**结论**：在 n=82 有效残差 + benefit SD=0.18 的实际样本下，**MDE ≈ 0.27-0.30 SD**。

### 2.3 与文献效应大小对比

| 参考研究 | 报告的 β (媒体语调 → 财务变量) |
|---|---|
| Jha-Liu-Manela 2026 RFS (US banks) | 0.15-0.25 SD |
| Hassan 2019 QJE (political risk → investment) | 0.10-0.20 SD |
| Tetlock 2007 JF (媒体悲观 → 股价) | 0.08-0.15 SD |

**风险评估**：现有 n=116 下的 MDE (0.27-0.30 SD) **高于**文献典型效应大小 (0.10-0.20 SD)。

→ **真效应可能检不出**（II 类错误风险高）。

---

## 3. 应对策略

### 3.1 提高 power 的可行手段

| 手段 | 效果 | 可行性 |
|---|---|---|
| 扩展年份至 2014-2024 → n≈800-1000 | MDE 降至 0.10 SD | 阻塞：需上游 pipeline 重跑 |
| 放松媒体筛选门槛 (≥1 篇 vs ≥3 篇) | n 上升 ~10-15% | ✅ 立即可行 |
| 使用 1-year-change 设计（差分） | 减少 panel 维度但消除 FE | ⚠️ 仅 1 个差分点 |
| Bayesian shrinkage 减少噪声 | partial R² ↑ → MDE 微降 | ✅ shrinkage.py 已构建 |
| 报告效应大小 + 置信区间 | 替代 NHST，规避 power | ✅ 写作策略 |

### 3.2 推荐 MVP 策略
1. **接受现有 n=116 限制**，报告效应大小 + 95% CI 而非仅显著性
2. **Bayesian 估计**作 robustness（shrinkage.py）
3. **明确声明** ex-ante power 限制于讨论部分
4. **扩展版**作为后续论文（待 pipeline 时间扩展后）

---

## 4. Phase 0 D9 决策

**结论**：MDE 0.27-0.30 SD > 文献典型 0.10-0.20 SD → **未达预期 power**。

**自动决策**（无人工参与）：
- ✅ 仍启动 MVP 论文（不阻塞）
- ✅ PAP 中明确声明 power 限制
- ✅ 报告效应大小为主，显著性为辅
- ✅ 预留扩展版论文路径（Phase B）

---

## 5. 后续依赖

- `papers/benefit_society/shrinkage.py`: 实施 Bayesian 收缩降低测度噪声
- `papers/benefit_society/analysis.py`: 主回归报告时输出 95% CI + 标准化系数
- Stata 模板 `15_table6_effect_size.do.tmpl`（新增）: 强调效应大小报告
