# 侧线长文引文体系扩展 — P1 变量清单固化 (2026-07-15)

> 依据 `SIDEPROJECT_LONGDESC_EXTENSION_EXECUTION_PLAN_2026-07-15.md` §6-2 P1 阶段产出。
> 仅做范围盘点与 Layer 1 候选清单固化 + 账本骨架落地, **不含任何长文正文** (P2 工作)。

## 1. 精确清点 (修正 §1 口径不一致)

两侧线源 codebook 均已实读全文 (`company_listed_bank/data/company_bank_cooc_panel_codebook.md`
216 行 / `company_tax_bank/data/company_tax_bank_cooc_panel_codebook.md` 255 行)。按结构类别
精确分类如下 (不再用粗 grep 行数口径):

### company_listed_bank

| 类别 | 数量 | 说明 |
|---|---|---|
| 固定列 (主面板) | 20 | `company_listed_name`/`stock_code`/`year`/`is_bank_company` + 计数/银行数/HHI/覆盖率四组 |
| pair 长表列 | 10 | `_company_bank_cooc_pairs.parquet` schema, 非面板列, 独立命名空间 |
| 加权测度通式 | 1 通式 × N 源列 × 3 轨 × 2 臂(cw/ce) | `cw_X_t`/`ce_X_t`, X 取自银行×年面板任意非缺数值列 (组合爆炸源, 不逐列枚举) |
| 替代权面板数 | 7 | loan/branch/board/supervisor/exec/dsg/shareholder, 同引擎同列名不同权重源 |
| 替代聚合面板数 | 2 | frozenw (基期冻结) / mainbankw (top-1 主办银行) |
| 缩写名↔全名对照表行 | 6 | 说明性表格, 非独立变量 |
| 逐年语料覆盖表行 | 19 (2007–2025) | 说明性诊断表, 非变量 |
| 董监高诊断列 (frozenw/mainbankw 附加) | 5 | `base_year_{track}`/`frozen_n_banks_{track}`/`main_bank_{track}`/`main_bank_share_{track}`/`main_bank_tie_{track}` |

### company_tax_bank

| 类别 | 数量 | 说明 |
|---|---|---|
| 固定列 (主面板) | 20 | 同构 listed_bank, `company_tax_name`/`usci`(18位统一社会信用代码)替代 `stock_code` |
| pair 长表列 | 10 | 同构 listed_bank schema |
| 加权测度通式 | 1 通式 × N 源列 × 3 轨 × 2 臂 | 同构公式, 权重侧由 registry SSOT (`importlib` 只读复用 listed 02 引擎) |
| 替代权面板数 | 2 | branch_city (城市网点) / branch_county (县域网点) |
| 替代聚合面板数 | 2 | frozenw / mainbankw (同构 listed_bank) |
| 双替代权面板固定列 | 4+1 | `rel_n_banks`/`rel_hhi`/`rel_wt_base` + 仅县权面板独有 `county_key_ok` |
| 排除列审计表理由代码行 | 13 | `D15_1_PEER` 等, 说明性表格 (registry excluded 区段汇总, 非变量) |
| 权源逐年关系对数覆盖表行 | 10 (2011–2020) | 说明性诊断表 |
| 已知局限条目 (税调特有 L1–L7 + 继承母本通用局限) | 7 + 12 | 叙述性局限清单条目, 非变量但是长文写作素材 |

⚠ §1 原表"120 个表格行 (grep 口径)"已废弃 — 实际结构与 listed_bank 高度同构 (20 固定列 +
10 pair 列 + 同一 cw/ce 通式), 差异集中在: usci 主键 / 2 替代权(非7) / county_key_ok 缺键语义 /
排除列审计表 / 税调专属已知局限 L1–L7。两项目"变量行数"不可直接横向比较的根因已消除
(此前的差异纯属统计口径不一致, 非规模真实差异)。

## 2. Layer 1 结构性长文候选清单

命名规则 (不复用主项目 `F0xx`): **company_listed_bank → `LB0xx`**, **company_tax_bank →
`TB0xx`**, 三位数字顺序编号, 各自独立编号空间, 互不冲突, 未来扩容留有余量 (当前候选止于
`LB018`/`TB017`, 后续批次可续号)。tier 映射依据计划 §4 推定映射 (standard ≥1000汉字 / core
≥5000汉字; 2026-07-15 二次修订对齐主项目门槛, 旧"≥100/≥1000字"口径作废): 固定列骨架 / 加权通式本身 / 双替代权总纲等"结构性主干"定为 core, 其余定为 standard。

### company_listed_bank (18 篇候选)

| ID | tier | 覆盖内容 |
|---|---|---|
| LB001 | core | 主面板固定列骨架 (20 固定列: 计数/银行数/HHI/覆盖率四组, D7 门控双宇宙) |
| LB002 | standard | pair 长表 schema (10 列, n_docs 系列变体语义) |
| LB003 | core | `cw_X_t`/`ce_X_t` 加权测度构造通式 (D12/D13, 分母限非缺共现银行重归一) |
| LB004 | standard | D17 三义务段与消融预答 (bert_avg_neu 恒等/词典消融相关性/pair 表重构通道) |
| LB005 | standard | 匹配精度分层抽样方法论 (WP3 R3-2, variant 长度×k^c 分层, precision 0.71/0.76/0.92) |
| LB006 | standard | 已知局限清单 (§7 摘要: 短简称误匹配/名录灌水/variant 双计/LLM 前瞻偏差等) |
| LB007 | core | 七替代权面板总纲 (D18, 禁横向 merge/禁混 Hansen J, track 双语义) |
| LB008 | standard | 贷款权 (loanw) 构造与披露 (DV4a, MaxLoan 恒额代理/银团 1/k/左截断) |
| LB009 | standard | 网点权 (branchw) 构造 (城市代理网点数/rel_hhi 稠密结构) |
| LB010 | standard | 董监高四臂治理权 (board/supervisor/exec/dsg, D18 四臂不可加, 左端缺口 v32) |
| LB011 | standard | 股东权 (shareholderw) 构造与快照口径 (DV4g, 最晚可观测报告期 + S0304a 折叠) |
| LB012 | core | frozenw 基期冻结替代聚合面板构造 (D2, GPSS initial-share 逐年重归一) |
| LB013 | standard | frozenw 发表义务五句 (D10, exposure-robust SE/共同样本对齐义务) |
| LB014 | core | mainbankw 主办银行替代聚合面板构造 (D3, 当年 argmax + 三级确定性平票) |
| LB015 | standard | mainbankw 诊断列与缺失语义 (D4, main_bank_share/tie, 顺延内生性禁令) |
| LB016 | standard | 替代聚合面板刻意不做清单 (GIV/LOO/关系衰减权重/frozen×mainbank 交叉禁) |
| LB017 | standard | 缩写名↔全名对照与命名规则 (D16) |
| LB018 | standard | 数据谱系与许可披露 (D9/DV5⑥, 商业数据库谱系七字段/再分发降级路径) |

### company_tax_bank (17 篇候选)

| ID | tier | 覆盖内容 |
|---|---|---|
| TB001 | core | 主面板固定列骨架 (20 固定列, usci 18位统一社会信用代码主键, is_bank_company 280家) |
| TB002 | standard | pair 长表 schema (10 列, 同构 listed_bank) |
| TB003 | core | `cw_X_t`/`ce_X_t` 加权测度构造通式 (企业侧同构公式, registry importlib 复用引擎) |
| TB004 | standard | D17 三义务段与消融预答 (税调面板同构继承 listed_bank) |
| TB005 | standard | 使用要点五条 (exposure-robust SE/cluster(bank)无定义/PPML建议/三轨禁单调/权重内生性) |
| TB006 | standard | 匹配精度分层抽样 (税调专属 2字/3字 variant 全量人工过目) |
| TB007 | standard | 已知局限-税调特有 L1–L7 (短简称/时点性/县权缺失/县改区错位/构念/银行系企业/子串映射残余) |
| TB008 | standard | 已知局限-继承母本通用局限 (显式声明继承而非默认, 与 listed_bank §7 对照) |
| TB009 | core | 双替代权面板总纲 (T-D5/T-D19⑦, 三权并排禁 merge, 城/县两权是同权源粒度梯子) |
| TB010 | standard | 城市网点权 (branch_cityw) 构造 (存续网点数/rel_hhi 稠密结构) |
| TB011 | standard | 县域网点权 (branch_countyw) 构造与 `county_key_ok` 缺键语义 (L3/L4) |
| TB012 | standard | (i) 类城县恒等说明 (T-D5b(i), 144家省直辖县级占位企业逐 bank×year 恒等) |
| TB013 | standard | 权源逐年关系对数覆盖表方法论 (真无关系 vs 权源覆盖假零判定) |
| TB014 | standard | 排除列审计表方法论 (registry excluded 区段理由代码 D15_1..D15_11/DUP_OF_40/KEY/TEXT) |
| TB015 | standard | 数据谱系与许可披露 (T-D20, 政府调查数据保密性/再分发降级路径) |
| TB016 | standard | 缩写名↔全名对照与命名规则 (同构 listed_bank) |
| TB017 | standard | Stata merge 与满骨架截断使用规范 (usci×year 主键, L2 时点性裁剪示例) |

**合计 35 篇** (core 8 篇 / standard 27 篇), 落在计划 §2 "30-50 篇" 区间内。逐篇对应"一种构造
逻辑家族", 具体 (X, track, 权重) 实例仍留在两份现有表格型 codebook 内, 通过"本列属于 XX 构造
通式, 见长文 LBxxx/TBxxx"的方式指回本清单 (第二层继承引用, P2/P3 工作)。

## 3. 独立账本骨架 (P0 隔离风险项落地)

严格镜像主项目 `config/codebook_longdesc/_new_dois_ledger.json` / `_index.json` 的顶层字段
schema (`entries`/`no_doi_acks`; `tier_signoff`/`structural_whitelist`/`families`), 内容为空骨架:

- `company_listed_bank/data/codebook_longdesc/_new_dois_ledger.json` — `{"entries": [], "no_doi_acks": []}`
- `company_listed_bank/data/codebook_longdesc/_index.json` — `families: {}`, `tier_signoff.user_ack=false` (未签收占位), `structural_whitelist: [company_listed_name, stock_code, year]`
- `company_tax_bank/data/codebook_longdesc/_new_dois_ledger.json` — `{"entries": [], "no_doi_acks": []}`
- `company_tax_bank/data/codebook_longdesc/_index.json` — `families: {}`, `tier_signoff.user_ack=false`, `structural_whitelist: [company_tax_name, usci, year]`

与主项目 `config/codebook_longdesc/_new_dois_ledger.json`(4175 行, 主项目新颖度闸 50.02% 压线通过)
**零交集、零耦合** — 未写入、未读取、未 import 该文件。

## 4. 脚本空跑验证 (P1-4)

```
"/f/Anaconda3/python.exe" scripts/audit/check_longdesc_whitelist.py --longdesc-dir company_listed_bank/data/codebook_longdesc
"/f/Anaconda3/python.exe" scripts/audit/check_longdesc_whitelist.py --longdesc-dir company_tax_bank/data/codebook_longdesc
```

两次均 `EXIT=0`, 报告 `n_families=0 / n_whitelist=874 (主项目白名单, 只读复用) / n_ledger=0 /
0 致命项 / 0 告警`。控制台中文乱码为 Windows GBK 终端渲染 UTF-8 输出的显示问题 (非脚本报错,
退出码与字段值均正确)。空骨架态下脚本未走"库为空→提示 exit 0"分支 (因 `_index.json` 已存在),
而是正常进入 `run_checks` 主路径并以 0 家族收尾 — 证明脚本对"已建账本骨架、待写入长文"的
过渡态兼容, 为 P2 批量写入长文后复跑同一命令做好衔接。
