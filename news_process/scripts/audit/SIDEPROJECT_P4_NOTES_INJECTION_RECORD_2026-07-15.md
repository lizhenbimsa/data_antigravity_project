# 侧线 P4 · 15 份 dta 数据集级 notes 注入映射与执行记录 (2026-07-15)

> 计划 = `SIDEPROJECT_LONGDESC_EXTENSION_EXECUTION_PLAN_2026-07-15.md` P4 (P0 决策定案第 2 条, 用户 2026-07-15 授权)。
> 方案 = **数据集级 notes** (`notes _dta:`), 因 LB007/LB012 等家族的 `columns` 字段是面板文件名/概念名而非真实列名, 逐列 notes 不可行。
> 文本中和 = 复用 `pipeline/panel/stata_export.py::_stata_notes_text` (换行归一/`\`/反引号/`$`宏面/`{}`/`//`/`/*`/marker 全套) + `_split_note_segments` 按 UTF-8 字节预算切段, 每段一条 `notes _dta:`。
> 每家族注入头 = `【<家族ID> · <md 文件名>】` + frontmatter 之后全文正文 (含渲染引文尾节, 剥 HTML 注释 marker)。

## 家族 → dta 映射表 (SSOT, 对账以此为准)

### company_listed_bank (10 份 dta, 通用篇 = LB003/LB004/LB005/LB006/LB016/LB017/LB018)

| dta | 注入家族 (升序) | 家族数 |
|---|---|---|
| company_bank_cooc_panel.dta | LB001, LB002, LB003, LB004, LB005, LB006, LB016, LB017, LB018 | 9 |
| company_bank_loanw_panel.dta | LB003–LB008, LB016, LB017, LB018 (通用7 + LB007, LB008) | 9 |
| company_bank_branchw_panel.dta | 通用7 + LB007, LB009 | 9 |
| company_bank_boardw_panel.dta | 通用7 + LB007, LB010 | 9 |
| company_bank_supervisorw_panel.dta | 通用7 + LB007, LB010 | 9 |
| company_bank_execw_panel.dta | 通用7 + LB007, LB010 | 9 |
| company_bank_dsgw_panel.dta | 通用7 + LB007, LB010 | 9 |
| company_bank_shareholderw_panel.dta | 通用7 + LB007, LB011 | 9 |
| company_bank_frozenw_panel.dta | 通用7 + LB012, LB013 | 9 |
| company_bank_mainbankw_panel.dta | 通用7 + LB014, LB015 | 9 |

### company_tax_bank (5 份 dta, 通用篇 = TB003–TB008, TB013–TB017 共 11 篇)

| dta | 注入家族 (升序) | 家族数 |
|---|---|---|
| company_tax_bank_cooc_panel.dta | TB001, TB002 + 通用11 | 13 |
| company_tax_bank_branch_cityw_panel.dta | 通用11 + TB009, TB010, TB012 | 14 |
| company_tax_bank_branch_countyw_panel.dta | 通用11 + TB009, TB011, TB012 | 14 |
| company_tax_bank_frozenw_panel.dta | 通用11 | 11 |
| company_tax_bank_mainbankw_panel.dta | 通用11 | 11 |

映射依据: LB001/LB002、TB001/TB002 = 主面板骨架/长表 schema → 仅各自 cooc 主面板; LB007 = 七替代权总览 → 7 个 altweight 面板; LB008→loanw, LB009→branchw, LB010→治理四臂 (board/supervisor/exec/dsg), LB011→shareholderw, LB012/013→frozenw, LB014/015→mainbankw; TB009 = 双网点权总览 → city/county 两面板, TB010→cityw, TB011→countyw, TB012 (城县恒等说明)→city+county 双面板; 骨架/公式/局限/命名/谱系/义务类通用篇注入全部相关 dta。TB 侧 frozenw/mainbankw 无专属家族 (TB 库未设), 仅通用篇 — 如需专文属后续扩展。

## 注入产物与对账

- 注入前快照: `company_listed_bank/data/_notes_preinject_snapshot.json`、`company_tax_bank/data/_notes_preinject_snapshot.json` (行数/列数/值哈希/label 表哈希/既有 notes)。
- 注入 .do: `company_listed_bank/data/_notes_inject_<dta名>.do` 等, 每 dta 一个, `version 19` + `use` + `capture notes drop _dta` + 逐段 `notes _dta:` + `save, replace` + `exit, clear`; 一律 StataMP-64 `/b` 批处理; 跑完扫同名 .log 的 r(###)。
- 期望 notes 条数 = 逐家族切段数之和 (由生成脚本计算并写入 `_notes_applied_fingerprint.json`), 对账 = pyreadstat 复读 notes 条数与之相等 + 行/列/值哈希/label 哈希与注入前逐一相等。
- 对账结果见本文件末尾"执行结果"节 (执行后回填)。

## 执行结果 (2026-07-15 回填)

- **15/15 全部注入成功且对账 PASS**: 全部 .do 经 StataMP-64 `/b` 批处理跑完, 15 份 .log 逐一扫描 `r(###)` = 0 条; 每份 log 末尾 `NOTES_DTA_DONE=<n>` 与期望切段数逐一相等 (LB 10 份各 24 条; TB cityw/countyw 各 32、cooc 30、frozenw/mainbankw 各 23; 合计 244 条 notes)。
- **注入前后对账**: 逐 dta 行数/列数/值哈希 (pd.util.hash_pandas_object 全表)/label 全表哈希 四项逐一相等 (LB 10 份 105,032 行; TB 5 份 447,710 行); 唯一差异 = notes + 文件时间戳/尺寸, 符合预期。pyreadstat 复读 notes 条数 = 期望+1 (多出的 1 条为 Stata `note0` 条数计数标记本身, 属 dta 格式固有)。
- **执行插曲 (无数据后果)**: ① 第二批首个 do (shareholderw) 完整跑完 (`exit, clear` 已回显、dta 已保存) 后 Stata 进程僵死不退, `-Wait` 卡死 → 手工击杀僵尸并停掉旧批任务, 改用「起进程→轮询 log DONE 标记→兜底击杀」策略跑完剩余 6 份; ② supervisorw 存在理论上的双跑竞态窗口, 已由值哈希对账证实无损 (PASS)。
- sidecar 指纹: 两侧线 `data/_notes_applied_fingerprint.json` 已写 (逐 dta sha256/行列/值哈希/label 哈希/notes 条数/家族清单/PASS)。
- 主项目零污染实证 (计划 §6-P4 附加项): `check_longdesc_whitelist.py --longdesc-dir config/codebook_longdesc` 复跑 EXIT=0, novelty 2536/5070 = 50.0% 不变。

## 终审补记 (2026-07-15, 终审 P2 整改后收口)

### (a) LB017 弱化重注事件与对账结果

终审 P2 整改将 `LB017_abbreviation_naming_convention.md` 的 Fišar 2024 引申句弱化 (删除"变量命名的随意性正是复现失败的高发源头之一"这一超出原文粒度的断言, 改为"构件标准化/可追溯性"层面表述; 弱化后 1262 汉字 ≥1000, LB 两门禁复跑 EXIT=0), 导致 10 份 LB dta 内已注入的 LB017 notes 段与 md 出现一句漂移。处置 = 对 10 份 `company_listed_bank/data/*.dta` 按首轮同款工具链**幂等重注** (TB 5 份不含 LB017, 不动):

- 基于弱化后 md 全文重切段、重新生成 10 个 `_notes_inject_*.do` (保留 `capture notes drop _dta` 幂等头 + `version 19` + `save, replace` + `exit, clear`), StataMP-64 一律 `/b`; 注入前快照按 round2 重打 (`_notes_preinject_snapshot.json` 各条目标记 `round=reinject-LB017-2026-07-15`)。
- 10/10 log 扫描 `r(###)` = 0 条, `NOTES_DTA_DONE=24` 与期望切段数逐一相等。
- 对账 **10/10 ALL_PASS**: 行 (105,032)/列/值哈希/label 哈希与重注前逐位相等; notes 条数 = 24+1 (note0 计数标记); **段级精确对账** = 用同一 `_stata_notes_text`+`_split_note_segments` 重算全部期望段, strip 归一后与 `meta.notes` 多重集全等 (LB017 弱化后新句在场由段级全等蕴含); 旧句"高发源头"全部 10 份 dta notes 0 命中。
- `company_listed_bank/data/_notes_applied_fingerprint.json` 已刷新 (逐 dta sha256/notes_count, method 标注"LB017 弱化后幂等重注"); TB 侧指纹不动。

### (b) 终审三条 P3 观察 (对账口径铁律, 后续复用须知)

1. **Stata 会 trim note 段首尾空白** → 逐字节对账须先做首尾空白归一 (本轮段级对账即 `seg.strip()` vs `note.strip()`)。
2. **pyreadstat `meta.notes` 是 characteristics 存储序, 非 note 编号序** → 不能按列表顺序拼接重建全文, 跨段句子会被打散 (本轮"新句 substring 直查"曾因此假红一次); 正确姿态 = 期望段集合 vs 实际段集合的多重集比对 (排序后全等)。
3. **注入流程会触碰 md 的 mtime** (重切段读取/渲染物化) → 以 mtime 判"文档未变"不可靠, 一律以内容哈希为准。

### (c) 主项目 51 号指纹失锚

主项目 51 号 dta 指纹失锚问题已由主会话重算回写收口, 不属本侧线范围, 此处仅存目备查。
