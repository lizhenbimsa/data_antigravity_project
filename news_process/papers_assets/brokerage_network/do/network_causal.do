* =========================================================================
* network_causal.do — 网络因果识别: Network 2SLS + 网络位置异质性
* =========================================================================
*
* 目标:
*   利用面板中已有但尚未被充分利用的网络变量组合,
*   补强两个因果识别维度:
*     (1) Network 2SLS: 二阶溢出作为一阶溢出的排他性工具变量
*     (2) 网络位置 × 政策冲击: 检验 DID 效应的网络位置异质性
*
* 核心学术依据:
*   Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification
*     of peer effects through social networks. Journal of Econometrics,
*     150(1), 41–55. https://doi.org/10.1016/j.jeconom.2008.12.021
*   Manski, C. F. (1993). Identification of endogenous social effects:
*     The reflection problem. The Review of Economic Studies, 60(3),
*     531–542. https://doi.org/10.2307/2298123
*
* 前置依赖 (仅首次安装):
*   ssc install reghdfe, replace
*   ssc install ftools, replace
*   ssc install estout, replace
*   ssc install ivreghdfe, replace
*
* 变量来源:
*   peer_tone_lag1_full      46_network_spillovers.py L255,267
*   peer_tone_2nd_lag1_full  46_network_spillovers.py L258-259,268
*   bank_between_cent        46_network_spillovers.py (逐年计算)
*   bank_constraint          46_network_spillovers.py (逐年计算)
*   brokerage_eigen_cent     47_network_brokerage.py  L253
*   dcep_post / sandbox_post 44_panel_iv_did.py       L529-534
*
* 使用方式:
*   1. 将 Y 替换为实际被解释变量 (如 ROA, Z-score 等)
*   2. 根据研究需要设定 $controls 全局宏
*   3. do stata/network_causal.do
* =========================================================================

clear all
set more off

* ----------------------------------------------------------------------------
* Phase 4a 路径前奏 — papers_assets/<paper>/do/ 自包含调用契约
* 默认假设当前工作目录是本 .do 文件所在目录:
*     news_process/papers_assets/brokerage_network/do/
* 用户可通过 `global panel_dta "..."` / `global out_dir "..."` 显式覆盖。
* 历史注: 原 `use "output/40_panel_data.dta"` 路径已纠正为
*         真实落盘文件 `data_processed/40_panel_yearly.dta`。
* ----------------------------------------------------------------------------
if "$panel_dta" == "" {
    global panel_dta "../../../data_processed/40_panel_yearly.dta"
}
if "$out_dir" == "" {
    global out_dir "../output"
    capture mkdir "$out_dir"
}

* ═══════════════════════════════════════════════════════════════════════════
* 0. 数据加载与面板设定
* ═══════════════════════════════════════════════════════════════════════════

use "$panel_dta", clear

* ── 面板设定 ──
* encode: 将字符串型银行名转换为数值 ID (Stata 面板命令的要求)
encode target_bank, gen(bank_id)
xtset bank_id year

* ── 省份编码 (用于聚类标准误) ──
* 聚类层级选择省份而非银行:
*   (1) 允许省内银行间的误差相关 (更保守)
*   (2) 与本项目 LOO 省级 IV (44_panel_iv_did.py) 的识别逻辑一致
*   参考: Cameron & Miller (2015, J. Human Resources) 关于聚类层级选择
encode bank_province, gen(prov_id)

* ── 用户自定义变量 ──
* 请根据研究需要替换以下占位符:
*   Y:        被解释变量 (如 ROA, NPL_ratio, Z_score 等)
*   controls: 控制变量组 (如 ln_news_coverage, media_hhi, bank_scale_ord)
* global controls "ln_news_coverage media_hhi bank_scale_ord"

* ── 生成滞后中心度变量 ──
* 使用 L. (lag operator) 需要先 xtset, 已在上方完成
* 滞后原因: 避免政策冲击同期改变网络结构导致的反向因果
*   - 如 DCEP 试点可能改变银行间的新闻共现模式
*   - 使用 t-1 期的中心度消除这一内生性来源
*   参考: Angrist & Pischke (2009), Ch. 4 — 前定变量作为工具
gen L_bank_between = L.bank_between_cent
    label var L_bank_between "L1.Co-mention Betweenness"
gen L_bank_constraint = L.bank_constraint
    label var L_bank_constraint "L1.Co-mention Constraint"
gen L_brokerage = L.brokerage_eigen_cent
    label var L_brokerage "L1.Brokerage Eigenvec Cent"


* ═══════════════════════════════════════════════════════════════════════════
* A. Network 2SLS — 同行情感溢出的因果估计
* ═══════════════════════════════════════════════════════════════════════════
*
* 核心问题: Manski (1993) 反射问题
*   OLS 回归 Y_i = α·(W×tone)_i + X_i·β + ε_i 中,
*   W×tone 内生——因为同一组银行既影响 i 也被 i 影响。
*   即使使用了 Lag(t-1), 仍可能存在关联效应 (correlated effects):
*   同省/同类型银行面临相似的宏观冲击, 导致 W×tone 与 ε 相关。
*
* 识别策略: Bramoullé et al. (2009, JoE, Proposition 1)
*   利用网络的非传递性结构 (intransitive triads) 作为排他性约束:
*     - 银行 A 的邻居 B 的邻居 C, 但 C 不是 A 的邻居
*     - C 的情感 (二阶溢出) 仅通过 B (一阶邻居) 间接影响 A
*     - 因此 W²×tone 满足排他性: 与 A 的结果无直接关联
*   本项目设定的优势:
*     使用 Lag(t-1) 的情感 (前定变量), 进一步消除同期反向因果,
*     使排他性约束更容易被满足 (相比 Bramoullé 的同期设定)
*
* 内生变量: peer_tone_lag1_full    = W_{t-1} × tone_{t-1}  (一阶溢出)
* 工具变量: peer_tone_2nd_lag1_full = W²_{t-1} × tone_{t-1} (二阶溢出)
* ═══════════════════════════════════════════════════════════════════════════

* ────────────────────────────────────────────────────────────────
* A1. OLS 基准 (不处理内生性, 作为 2SLS 的对照)
*     用途: 与 A2 比较系数大小和方向
*           若 2SLS 系数 > OLS, 提示 OLS 存在衰减偏误 (attenuation bias)
*           若 2SLS 系数方向反转, 提示弱 IV 或排他性违背
* ────────────────────────────────────────────────────────────────
reghdfe Y peer_tone_lag1_full $controls, ///
    absorb(bank_id year) vce(cluster prov_id)
eststo ols_baseline

* ────────────────────────────────────────────────────────────────
* A2. Network 2SLS (核心回归)
*     内生变量: peer_tone_lag1_full  (W × tone, 一阶同行溢出)
*     工具变量: peer_tone_2nd_lag1_full (W² × tone, 二阶溢出)
*     排他性: Bramoullé et al. (2009, JoE, Proposition 1)
*       — 二阶邻居的滞后情感仅通过一阶邻居间接影响银行 i
*     聚类层级: 省份 (允许省内银行间误差相关)
*     注意: 恰好识别 (1 IV for 1 endog), 无过度识别检验
* ────────────────────────────────────────────────────────────────
ivreghdfe Y (peer_tone_lag1_full = peer_tone_2nd_lag1_full) ///
    $controls, absorb(bank_id year) cluster(prov_id) ffirst
eststo iv_net2sls

* 弱 IV 诊断 (由 ffirst 选项自动报告):
*   Kleibergen-Paap rk Wald F > 10 → IV 足够强
*   若 F < 10 → 论文中将 Network 2SLS 降级为补充分析
*   参考: Stock & Yogo (2005), Kleibergen & Paap (2006)
*   注意: ivreghdfe 底层基于 ivreg2, 不支持 estat firststage
*         应使用 ffirst 选项 (已加入上方命令)


* ═══════════════════════════════════════════════════════════════════════════
* B. 网络位置 × DCEP 政策冲击交互
* ═══════════════════════════════════════════════════════════════════════════
*
* 经济学假设:
*   处于信息网络枢纽位置的银行 (高 betweenness centrality),
*   能更快获取和传播金融科技政策信息,
*   因此可能更强地响应数字人民币 (DCEP) 试点政策。
*
* 交互项规范:
*   Brambor, T., Clark, W. R., & Golder, M. (2006). Understanding
*   interaction models. Political Analysis, 14(1), 63–82.
*   https://doi.org/10.1093/pan/mpi014
*   → 必须同时包含交互项和所有低阶构成项 (主效应)
*
* 内生性处理:
*   使用滞后一期中心度 (L.bank_between_cent), 而非同期值
*   原因: 政策冲击可能同期改变银行的新闻共现模式 (反向因果)
*
* 技术说明:
*   - bank_between_cent 是时变变量 (46 逐年构建邻接矩阵)
*   - L.bank_between_cent 不会被 absorb(bank_id) 吸收 (因为它逐年变化)
*   - dcep_post 是 bank-specific 时变变量 (不同银行 treat_year 不同)
*     不会被 absorb(bank_id year) 吸收
*   - 首年观测因 L. 操作符结构性缺失, 减少约 N 个观测, 不影响一致性
* ═══════════════════════════════════════════════════════════════════════════

* ────────────────────────────────────────────────────────────────
* B1. Betweenness Centrality × DCEP
*     betweenness: 银行在共现网络中的"桥梁"地位 (Freeman 1979)
*     预期: 正系数 → 信息桥梁银行从 DCEP 试点中获益更多
* ────────────────────────────────────────────────────────────────
gen dcep_x_L_between = dcep_post * L_bank_between
    label var dcep_x_L_between "DCEP Post × L1.Betweenness"
reghdfe Y dcep_x_L_between dcep_post L_bank_between $controls, ///
    absorb(bank_id year) vce(cluster prov_id)
eststo b1

* ────────────────────────────────────────────────────────────────
* B2. Structural Constraint × DCEP
*     constraint: 银行的网络受限程度 (Burt 1992)
*     高 constraint = 结构洞少 = 信息来源单一
*     预期: 负系数 → 网络受限银行从 DCEP 中获益更少
*     参考: Burt, R. S. (1992). Structural holes: The social
*       structure of competition. Harvard University Press.
*       ISBN: 978-0-674-84372-1.
* ────────────────────────────────────────────────────────────────
gen dcep_x_L_constraint = dcep_post * L_bank_constraint
    label var dcep_x_L_constraint "DCEP Post × L1.Constraint"
reghdfe Y dcep_x_L_constraint dcep_post L_bank_constraint $controls, ///
    absorb(bank_id year) vce(cluster prov_id)
eststo b2

* ────────────────────────────────────────────────────────────────
* B3. 信息经纪中心度 × DCEP
*     brokerage_eigen_cent: 媒体-银行二分图的特征向量中心度
*     衡量银行在信息分发网络中的枢纽地位
*     高值 = 通过更多异质媒体渠道传播/接收信息
*     学术依据: Han, M., Kim, S. H., Nanda, V., & Ramadorai, T.
*       (2024). Institutional brokerage networks: Facilitating
*       liquidity provision. The Review of Financial Studies,
*       37(9), 2903–2935. https://doi.org/10.1093/rfs/hhae026
* ────────────────────────────────────────────────────────────────
gen dcep_x_L_brokerage = dcep_post * L_brokerage
    label var dcep_x_L_brokerage "DCEP Post × L1.Brokerage"
reghdfe Y dcep_x_L_brokerage dcep_post L_brokerage $controls, ///
    absorb(bank_id year) vce(cluster prov_id)
eststo b3


* ═══════════════════════════════════════════════════════════════════════════
* C. 网络位置 × Sandbox 政策冲击交互
* ═══════════════════════════════════════════════════════════════════════════
*
* 与模块 B 结构完全对称, 替换 dcep_post → sandbox_post
* 目的: 验证网络位置异质性是否在不同政策冲击中一致成立
*       若 DCEP 和 Sandbox 的交互效应方向一致 → 结论稳健
*       若方向不一致 → 需在论文中讨论政策差异性
* ═══════════════════════════════════════════════════════════════════════════

* C1. Betweenness × Sandbox
gen sandbox_x_L_between = sandbox_post * L_bank_between
    label var sandbox_x_L_between "Sandbox Post × L1.Betweenness"
reghdfe Y sandbox_x_L_between sandbox_post L_bank_between $controls, ///
    absorb(bank_id year) vce(cluster prov_id)
eststo c1

* C2. Constraint × Sandbox
gen sandbox_x_L_constraint = sandbox_post * L_bank_constraint
    label var sandbox_x_L_constraint "Sandbox Post × L1.Constraint"
reghdfe Y sandbox_x_L_constraint sandbox_post L_bank_constraint $controls, ///
    absorb(bank_id year) vce(cluster prov_id)
eststo c2

* C3. Brokerage × Sandbox
gen sandbox_x_L_brokerage = sandbox_post * L_brokerage
    label var sandbox_x_L_brokerage "Sandbox Post × L1.Brokerage"
reghdfe Y sandbox_x_L_brokerage sandbox_post L_brokerage $controls, ///
    absorb(bank_id year) vce(cluster prov_id)
eststo c3


* ═══════════════════════════════════════════════════════════════════════════
* D. Ctx 轨道稳健性
* ═══════════════════════════════════════════════════════════════════════════
*
* Ctx 轨道: 情感分析时剔除了共提银行的上下文窗口
*   (详见 21_tone_llms.py 中的 ctx_window 设定)
* 目的: 验证 Network 2SLS 结果对情感度量方式的稳健性
*   若 Full 和 Ctx 轨道系数方向一致 → 结果不受上下文窗口影响
* ═══════════════════════════════════════════════════════════════════════════

ivreghdfe Y (peer_tone_lag1_ctx = peer_tone_2nd_lag1_ctx) ///
    $controls, absorb(bank_id year) cluster(prov_id) ffirst
eststo iv_ctx


* ═══════════════════════════════════════════════════════════════════════════
* E. 输出汇总表
* ═══════════════════════════════════════════════════════════════════════════

esttab ols_baseline iv_net2sls b1 b2 b3 c1 c2 c3 iv_ctx ///
    using "$out_dir/network_causal.tex", ///
    star(* .10 ** .05 *** .01) se replace ///
    title("Network Causal Identification: 2SLS and Heterogeneous Effects") ///
    mtitles("OLS" "Net-2SLS" ///
            "DCEP{$\times$}Betw" "DCEP{$\times$}Constr" "DCEP{$\times$}Broker" ///
            "SB{$\times$}Betw" "SB{$\times$}Constr" "SB{$\times$}Broker" ///
            "Net-2SLS Ctx") ///
    note("All regressions include bank and year FE. " ///
         "Clustered SE at province level. " ///
         "Network centrality measures use L1 (lagged one period). " ///
         "2SLS IV: W{$^2$} tone (Bramoulle et al. 2009, JoE).")

* ── 屏幕输出 (快速查看) ──
esttab ols_baseline iv_net2sls b1 b2 b3 c1 c2 c3 iv_ctx, ///
    star(* .10 ** .05 *** .01) se ///
    mtitles("OLS" "2SLS" "D×Bt" "D×Co" "D×Br" "S×Bt" "S×Co" "S×Br" "Ctx")


* ═══════════════════════════════════════════════════════════════════════════
* 参考文献 (完整 APA 格式, DOI 已在线验证)
* ═══════════════════════════════════════════════════════════════════════════
*
* [1] Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification
*     of peer effects through social networks. Journal of Econometrics,
*     150(1), 41–55. https://doi.org/10.1016/j.jeconom.2008.12.021
*
* [2] Manski, C. F. (1993). Identification of endogenous social effects:
*     The reflection problem. The Review of Economic Studies, 60(3),
*     531–542. https://doi.org/10.2307/2298123
*
* [3] Lee, L.-F. (2007). Identification and estimation of econometric
*     models with group interactions, contextual factors and fixed
*     effects. Journal of Econometrics, 140(2), 333–374.
*     https://doi.org/10.1016/j.jeconom.2006.07.001
*
* [4] De Giorgi, G., Pellizzari, M., & Redaelli, S. (2010). Identification
*     of social interactions through partially overlapping peer groups.
*     American Economic Journal: Applied Economics, 2(2), 241–275.
*     https://doi.org/10.1257/app.2.2.241
*
* [5] Brambor, T., Clark, W. R., & Golder, M. (2006). Understanding
*     interaction models: Improving empirical analyses. Political
*     Analysis, 14(1), 63–82. https://doi.org/10.1093/pan/mpi014
*
* [6] Han, M., Kim, S. H., Nanda, V., & Ramadorai, T. (2024).
*     Institutional brokerage networks: Facilitating liquidity provision.
*     The Review of Financial Studies, 37(9), 2903–2935.
*     https://doi.org/10.1093/rfs/hhae026
*
* [7] Burt, R. S. (1992). Structural holes: The social structure of
*     competition. Harvard University Press. ISBN: 978-0-674-84372-1.
*
* [8] LeSage, J. P., & Pace, R. K. (2009). Introduction to spatial
*     econometrics. Chapman and Hall/CRC. ISBN: 978-1-4200-6424-7.
*
* [9] Angrist, J. D., & Pischke, J.-S. (2009). Mostly harmless
*     econometrics: An empiricist's companion. Princeton University
*     Press. ISBN: 978-0-691-12034-8.
*
* [10] Cameron, A. C., & Miller, D. L. (2015). A practitioner's guide
*      to cluster-robust inference. Journal of Human Resources, 50(2),
*      317–372. https://doi.org/10.3368/jhr.50.2.317
*
* [11] Stock, J. H., & Yogo, M. (2005). Testing for weak instruments
*      in linear IV regression. In D. W. K. Andrews & J. H. Stock
*      (Eds.), Identification and inference for econometric models:
*      Essays in honor of Thomas Rothenberg (pp. 80–108). Cambridge
*      University Press. https://doi.org/10.1017/CBO9780511614491.006
*
* [12] Kleibergen, F., & Paap, R. (2006). Generalized reduced rank
*      tests using the singular value decomposition. Journal of
*      Econometrics, 133(1), 97–126.
*      https://doi.org/10.1016/j.jeconom.2005.02.011
* =========================================================================
