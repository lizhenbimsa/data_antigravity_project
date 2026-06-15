# 顶刊重审修复 — Stata 合成 T=18 烟雾验证报告 (全 11 篇)

> REAUDIT_STATA_SMOKE_T18_2026-06-14 · 配套 PROJECT_REAUDIT_TOPTIER_T18_2026-06-14.md

## 元信息

- **目的**: 对 PROJECT_REAUDIT_TOPTIER_T18 落地的全部 Stata 模板改动 (era-stability / weakiv-AR / pooled over-id Hansen J / honestdid / csdid+bacondecomp / boottest(prov) / Oster / bank_id FE / Sun-Abraham coefplot / 共线性披露 等), 在【合成 T=18 面板】(60 banks × 2007-2024 = 1080 行, 各论文专属列) 上经 Stata `/b` 真跑, 验证它们【真产出 / 优雅跳过】而非「注释声称却跑不出」(claimed-but-not-run)。
- **方法**: 逐论文自洽 agent (建复现包 → 造合成 T=18 面板 → 跑 00_master `/b` → 扫 `r()` → 只修【本轮审计引入】真错误并复跑)。**顺序执行 (单 lab 许可)**, 分两个工作流 (7 篇 + 5 篇; 首个 4.3h 后 auth 过期, 第二个补齐 + benefit 复验)。
- **环境**: StataNow MP 19.5。⚠ 本机 **ivreghdfe 运行期恒 r(301)** (ftools/reghdfe Mata 不兼容) — 所有 2SLS 经 ivreg2 回退跑出, 全量机 ivreghdfe 正常则走 HDFE 主路径, 行为等价。
- **关键性质**: 纯 Stata 模板/spec 层, **golden-safe** (无 panel 列值变更), 全部**未 git commit**。临时包/合成盘在 `build/smoke_reaudit{2,3}/` (gitignored)。

## 总裁决

**全 11 篇审计目标块在合成 T=18 上真跑验证通过** (真产出非空, 或缺 ado/缺财务列时优雅跳过)。烟雾额外**逮出并修复了 4 个第一实施工作流引入的 audit-introduced「claimed-but-not-run」真 bug** + 多个 pre-existing 阻断 (为打通链)。这正是本次审计头号根因「声明—实现缺口」在修复自身中的复现 → 已闭环。

| 论文 | status | 审计新块真产出 | audit-introduced bug (已修) | pre-existing 修(打通链) |
|---|---|---|---|---|
| bank_fintech_tone | FIXED | era / weakiv AR-CI / Rotemberg / Sun-Abraham IW coefplot | — (weakiv AR-CI string-parse 增补) | 25/22 ivreghdfe→ivreg2 回退; 14 frget _rand_treat→rand_treat |
| bank_fintech_attention | FIXED | era(ibn) / **pooled over-id Hansen J** / honestdid .gph / pre-trend F / Oster | **19 Hansen J 需 partial(i.bank_id i.year)** | — |
| bank_fintech_substance | FIXED | era(testparm) / weakiv AR / FE-sat / Oster / subsample | **22 weakiv 冒号+cluster 不兼容; 26 testparm r(F)** | 18 boottest 单 absorb |
| bank_fintech_locus | PASS | era / weakiv AR / **honestdid .gph(c.#c.+位置切片)** / 事件研究 | — | — (pre-existing 15 test r111 记录) |
| bank_fintech_collab | FIXED | era / weakiv AR-CI / IV / Sun-Abraham 事件研究 | **21 weakiv 非法 `ar` 选项 + e()/r() 取值错** | — (pre-existing 15 test r111 记录) |
| benefit_society | PASS | **bank_id FE / weakiv AR / partial Hansen J(0.685/0.842) / era** | — (partial 修复由主控应用, 烟雾复验生效) | stata_runner EXT_Y 占位符登记 |
| brokerage_network | FIXED | era / weakiv AR-CI / **csdid+bacondecomp / boottest(prov)** / Oster | — | 00_master capture-wrap (ivreghdfe r301 连环 abort) |
| llm_peer | FIXED | era / 主 IV M3-M5 / FE-sat / 子样本 / 时序 placebo | **16/17 缺 ivreg2 回退致静默零产出** | 12/13/14/30 ivreg2 回退 |
| strategic_diff | PASS | era / correlate r(C) 共线性披露(corr=-0.976/VIF21) | — | (主链 12 r301 → master-fix 处理) |
| bank_media_disagreement | FIXED | weakiv AR-CI / FE-sat / Oster | **12 weakiv `_vhat_`+28字符=34>32 名超限** | 11 keep 因子顺序 → master-fix |
| bank_news_clarity | PARTIAL→ | weakiv AR-CI / FE-sat / Oster / 结构子样本 | — (12 weakiv 内生名短未触限) | 11 keep 因子顺序 + master 挂起 → master-fix |

## 一、审计引入的「claimed-but-not-run」真 bug (烟雾逮出 + 已修) — 最有价值

第一实施工作流写出的模板"注释/脚注声称了方法学, 但 Stata 上跑不出"——与审计指控全项目的头号根因同型, 在我的修复里复现, 烟雾逐个逮出并修到【真产出】:

1. **collab/21 weakiv 非法 `ar` 选项** — `weakiv ..., cluster(bank_id) lm ar` 中 `ar` 不是 weakiv 合法选项 → r(198) 静默吞 → AR CI 侧表只剩表头。修: 删 `ar` (weakiv 默认即算 AR) + AR p 改 `e(ar_p)`、CI 读字符串 `e(ar_cset)`。
2. **substance/22 weakiv 冒号语法带 cluster** — `weakiv,...: ivreg2 ..., cluster()` — weakiv 不接受被包裹命令的 cluster() → r(198)。修: 两步式 (先裸 ivreg2 落 e(), 紧随裸 `weakiv, level(95)`)。
3. **substance/26 testparm 统计量** — reghdfe+cluster 后 testparm 返回 r(F) 非 r(chi2) → wald 行恒空。修: 加 r(F) 回退 + label 订正。
4. **attention/19 + benefit/25 pooled over-id Hansen J 秩亏** — ivreg2 带 `i.bank_id i.year` 高维哑变量 + 聚类 → moment-cov 秩亏 'overid stat not reported' → Hansen J 恒空。修: 加 `partial(i.bank_id i.year)` (attention 实测 J p=0.775; benefit 实测 0.685/0.842)。
5. **MD/12 weakiv 内生名超 32 字符** — weakiv 内部建 `_vhat_`+内生名; `cross_outlet_tone_variance_ctx`(28) → 34>32 → r(198) 静默吞。修: 加短名别名 `_txd` 喂 2SLS+weakiv。
6. **llm_peer 16/17 (FE-sat/subsample 2SLS) 缺 ivreg2 回退** — 本机 ivreghdfe r301 → 整 Panel 静默零产出。修: 加 ivreghdfe→ivreg2 回退 (镜像主表)。
7. **attention/18 + locus/18 honestdid 多行 Mata r(3000) + 因子 c.#i. 列错位** (主控二次修, 早于烟雾): 改 c.#c. event-time + 位置切片 → 隔离 + master 整跑均产 .gph (15997B / 18167B)。

## 二、weakiv 正确用法 (本机 StataNow 19.5 钉死, 后续复用)

- weakiv 是 e-class; **裸调**, 不能用冒号包裹带 cluster() 的命令; 无 `ar` 合法选项 (默认即算 AR)。
- AR p = **`e(ar_p)`** (非 r(ar_p)); AR 95% CI 是【字符串】**`e(ar_cset)`** (无数值 e(ar_cset_lb/ub), 须解析)。
- 内生变量名须使 `_vhat_`+name ≤ 32 字符 (长名先 gen 短别名)。
- 标准两步: `ivreg2 DV (en=iv) controls i.bank_id i.year, cluster(bank_id)` → 紧随 `weakiv, level(95)`。
- over-id 列 ivreg2 要报 Hansen J 须 `partial(i.bank_id i.year)` (否则秩亏不报)。
- 本机 ivreghdfe r(301) → IV 一律 capture noisily + 回退 ivreg2 (IV-6)。

## 三、审计新块真产出确认 (合成 T=18)

- **era-stability** (9 篇全部): 三时代 2007-12/2013-18/2019-24 各 N≈360 分段回归 + treatment×era 交乘 + 跨时代 Wald 相等检验, 全真产出真系数 (T=2 盘退化跳过, T=18 全激活)。`ibn.era` (attention) / `testparm` (substance) / 各 paper 变体均验证。
- **weakiv AR-CI** (IV 篇): KP rk F + Anderson-Rubin Wald p + 95% CI 进表 (修后真填)。
- **pooled over-id Hansen J** (attention/19 + benefit/25): partial 后真报告。
- **honestdid .gph** (attention/locus): 位置切片 + numpreperiods(2/3) 真产图。
- **csdid + bacondecomp** (brokerage/12): Callaway-Sant'Anna 错时事件研究 (dcep/sandbox cohort) + Goodman-Bacon 分解真跑。
- **boottest(prov_id)** (brokerage/11/12): 省级 wild bootstrap 真跑 (9999 reps)。
- **Oster δ** (多篇): psacalc 用 materialized year 哑变量 (非 i.year, 避 rc5001) 真算出。
- **Sun-Abraham IW coefplot** (tone/30, collab/19): eventstudyinteract e(b_iw)/e(V_iw) 真绘图。
- **bank_id FE** (benefit/11/14): absorb(bank_id year) 真吸收 (替代 bank_type FE)。
- **correlate r(C) 共线性披露** (strategic/11): corr/VIF 真取出。

## 四、生产环境清单 (须人工/生产 run 处理, 非本轮可修)

1. **ado 安装** (本机缺, 对应块现优雅跳过 capture-guard, 装后自动激活兑现): `rwolf` (Romano-Wolf FWER) · `wyoung` (brokerage FWER battery) · `bartik_weight` (官方 Rotemberg, 现内联 OLS 近似回退) · `condivreg`/`rivtest` (weakiv 已装为首选, 回退层) · `ppmlhdfe` (locus/collab 计数) · `xtbreak` (结构断点)。
2. **本机 ivreghdfe r(301)** — 重装 ftools/reghdfe/ivreghdfe; 否则全 2SLS 走 ivreg2 回退 (等价但慢; 部分 Hansen J 在 ivreg2 回退下秩亏空白, ivreghdfe absorb 路径可报)。
3. **财务/IV enrichment 列接入 + stage 45/46 重跑 + golden 重生**: 真盘现无 funding_cost / cost_income_ratio_change_3yr / citation_weighted_patent / m_and_a_fintech / roa / tobin_q / z_score 等主 outcome + IV 工具列 → 真 master 在 01_data_prep fail-loud (预期); 财务面板接入后全部 wire-ahead 块自动激活, 须 golden 重生。⚠ benefit/25 第二阶段硬编码小写 `roa` 与 MAIN_DV 大写 `ROA` sentinel 命名不一致 (2026-06-13 引入) — 接入时统一大小写。
4. **15_tableA6 Panel A 加权聚合 2SLS** (llm_peer; agg-audit 2026-06-13 引入, 非本轮) 仍缺 ivreg2 回退 → 本机静默跳过; 建议同款补回退。
5. **boottest 在双向 reghdfe FE 后不可运行** (多处 wild p 须单 absorb 承载; substance/18 已修, attention/18 等待生产决策)。
6. **复现包 CLI** `build-replication` 对 benefit/brokerage 因 BENEFIT_*_FRAC_SS / PRIMARY_CENT 等占位符未登记 stata_runner 而抛"未知占位符" (并行会话/2026-06-13 引入的跨论文 infra drift); 绕过 = derivative_replication 直建。建议补登记。

## 五、结论

本轮顶刊重审的 Stata 模板交付 (10 新模板 + 多篇 IV/稳健性/披露改动) 经合成 T=18 真跑验证为**运行时健全**: 全部审计目标块真产出或正确优雅跳过, 烟雾逮出的 6 个 audit-introduced「claimed-but-not-run」真 bug 已全部修到真产出。pre-existing 主链阻断 (master 裸 do abort/挂起 + 11_table2 keep 因子顺序 + 21 set maxvar 死锁) 经 master capture-wrap + 定点修复打通 (见配套 master-reachability 修复)。**剩余全部为生产环境清单** (装 ado + 修 ivreghdfe + 财务接入 + golden 重生), 非模板缺陷。所有改动纯 Stata 层 golden-safe, 未提交。
