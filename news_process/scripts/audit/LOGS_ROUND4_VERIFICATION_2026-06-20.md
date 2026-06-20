# 第四轮日志审计 — 收敛验证 + 真缺陷修复 (2026-06-20)

> 续 round 1-3 (`LOG_FILES_ENRICH_AUDIT_` / `LOG_FIXES_REAUDIT_` / `LOGS_FINAL_AUDIT_VERDICT_` / `DEFERRED_ITEMS_COMPLETION_`)。
> 方法: 41-agent 第四轮收敛验证工作流 (39 日志终扫 + 终极批判 + 收敛裁决) → 主控亲验真缺陷 → 修 4 项 → 实证。
> 工件: `_logaudit_20260620/{r4_findings,r4_critic,r4_verdict,logs_snapshot_round4}` · 工作流 wf_a7184a71-2bc。

---

## 0. 总裁决

**第四轮证明"尚未完全收敛"是对的 —— 它抓出 1 个前三轮全漏的【真算法 bug】+ 1 个【结构性日志缺陷的生产侧未修分支】, 两者均已亲验并修复。** 诚信维度持续 0 造假 (4 轮)。修复后: 我方累计 **28 文件 golden-safe 修复**, ruff 全绿, 定向测试 0 失败, 真缺陷已闭环。

**关键认识 (诚实)**: 同形多轮审计对"造假"边际价值已≈0 (4 轮全 0), 但对"声明-实现缺口"类真 bug 仍有非平凡边际 —— 第四轮的 stage 18 argsort 正是前三轮把注意力压在日志取证层而漏掉的算法 bug。**此后边际递减**: 建议以"修复+提交"收口, 而非再跑第五轮同形审计。

---

## 1. 第四轮抓出并已修复的真缺陷 (4 项, 全亲验)

### ① stage 18 `article_staleness.py` argsort/NaT 整列错位 (真算法 P1, 前三轮全漏)
- **实证**: `pd.Series.argsort()` 对 NaT 返回 **-1** (实测 pandas 2.2.3: `[d,d,NaT,d,NaT].argsort()=[1,2,-1,0,-1]`) → `df.iloc[-1]` 把 NaT 行错配成末行 + 丢失真行 (`rowid [1,2,4,0,4]`, 行 3 丢、行 4 重)。逆置换 `np.argsort(_sort_idx)` 也随之失效。
- **影响**: surface (L165) + semantic (L284) 两轨同 bug; 当前 T=2 盘面若日期全可解析则不显形, 但生产 17M 必有不可解析日期 → NaT → staleness 列错位。
- **修复**: 两处改 `np.argsort(pd.to_datetime(...).values, kind='stable')` (NaT 稳定排末尾、合法置换, 与逆置换自洽)。订正"semantic 轨一致"的错误注释。
- **golden 影响**: staleness 列当前因代际守卫未并入面板 (round-1 R11), 故 golden-safe; 生产 staleness 接入时即正确。

### ② R1 结构根因的【生产侧】未修分支 — 模块级 setup_logging import 即截断 (结构 P1)
- **round-3 的 conftest R1 fix 只覆盖 pytest**; 生产/standalone import (并行会话 panel build 经 runner→llm_peer_iv→tone_llms import) 仍触发 `tone_llms.py` 模块级 `logger.info` (L200/L498) → `setup_logging(delay=True)` 首写截断 `logs/21_tone_llms.log` → 覆写成 2 行 import banner (掩盖真实 stage 21 运行)。同理 `llm_peer_iv.py:131` 截断 48 日志。
- **修复**: 把 tone_llms (L200/498) 与 llm_peer_iv (L131) 的模块级参数回显 emit **移入各自 main()/compute_llm_peer_iv()**。delay=True 下"setup 不 emit = 不开文件 = 不截断"; 仅真实运行时回显。
- **实证**: 在【非 pytest】fresh python 中 `import llm_peer_iv` (→import tone_llms) 后, `logs/21` + `logs/48` md5 **逐位不变** (323fa577 / 59064b10)。生产 import-clobber 消除。结合 conftest fix, R1 在 test + 生产两条 import 路径均闭环。

### ③ stage 52 `stata_audit.py` DiD 可识别性退化守卫 (验证诚信 P1)
- **问题**: T=2 盘面 `dcep_post/sandbox_post` 全 0 (无政策后期窗口) → "treated-post 逻辑" / "event-study 互斥" 报 16 行 **all-PASS**, 但这些 PASS 是**空集恒真 (vacuous)**, 掩盖 DiD 结构不可识别。referee 会误读为"DiD 设计成立"。
- **修复**: 加 5b-2 退化守卫: `post`/`treated` 无变异 (nunique≤1) 时 record loud `WARN '... DiD 结构不可识别, 下方 PASS 为空集恒真...生产 T=18 方可识别'`。不删既有 PASS (技术上为真), 仅加披露。golden-safe (validation 诊断)。

### ④ filtering.yaml SIF→IDF 跨源一致性 (P3 文案)
- config 注释 (L25/33/38) 仍写 "TF-IDF + SIF 词向量质心" / "SIF 质心" / "各向异性校准 (Ethayarajh)", 与 LOG + `fintech_intensity.py` docstring 已订正的 "非 SIF, IDF 加权普通质心" (fix omni-g-fintech-02) 矛盾。订正为 "IDF 加权普通质心 (非 SIF)" + Ethayarajh 降为"现象动机参考, 非校准方法"。

---

## 2. 第四轮其余 finding 分类 (12 P1 / 23 P2 / 47 P3 → 去重后)

| 类别 | 说明 | 处置 |
|---|---|---|
| **真缺陷 (本轮修)** | ①stage18 argsort ②R1 生产侧 ③stage52 DiD ④SIF | **已修 (见 §1)** |
| **fixed-in-source (我方修复已在源码, 部分已反映进重生日志)** | 34 _ss 标签/热力图后缀/Δα/众数; 22 verdict (重生日志已无 "符合预期 0.998"); 47 fire_sale 零方差 (重生日志已含); 39e conftest 验证 | 已闭环 (源码), 日志随生产重生自愈 |
| **复核为非缺陷** | 39a κ∈[0.50,0.70] 甜区内部一致 (round-3 已定); 引用 (Carlson/Andreou/Distel/SSRN, round-3 已核验) | 不改 |
| **测度退化 (T=18 deferred, 如实披露)** | 23 finbert2 labels=2 ~98%正面/0%中性; 34 ECE conf=0; 51/52 弱IV/confirmatory | 生产门控, manuscript 披露 |
| **取证身份污染 (integrity_ok=false 5 处, 非造假)** | 12b/22/23/37/40 canonical 日志现为 pytest/probe 残片; 真值 parquet 完好 (12b meta sha=55a82159 等) | 根因=R1 生产侧 (本轮②已修); 日志随生产重生自愈 |
| **并行 loughran 会话责任** | decay_sensitivity:896 "15→18"; export.py:109 漏 'b' | 转告该会话 (见 §4) |
| **生产门控** | golden 重生 T=18 / 真实生产日志重生 | data/raw 空 + M0 付费 (SOP 见 DEFERRED 报告) |

诚信: **0 造假, 0 数据腐败** (第四轮亲验: 12b parquet 1125行/113银行完好; 21/23/39e 真跑另存 _runcheck/snapshot; 所有日志内部数字与源码逐位自洽)。

---

## 3. 验证

- 我方累计 **28 文件** (round1-3 的 24 + round4 的 article_staleness / tone_llms / stata_audit / filtering.yaml; llm_peer_iv 已在 24 内), **+208/−82**, 全 golden-safe (validation/log/doc/comment, 零 panel-producer 逻辑改)。
- ruff 全绿; py_compile/YAML/JSON 通过; 定向测试 (含 stage18/21/48/52 链) **0 失败** (179 + 202 junit 实测)。
- R1 生产侧修复**实证**: 非 pytest import 不再截断 21/48 日志 (md5 逐位不变)。
- manifest: `_logaudit_20260620/FIXES_20260620.diff` (28 文件)。

---

## 4. ⚠ 并行会话已大幅扩张 (提交强约束)

并行 **loughran 第6词典会话** 自 round-3 起从 7 文件扩张到 **~21 文件** (广度 6th-dict 集成): `attention_media.py`/`export.py`/`stata_export.py`/`decay_sensitivity.py`/`radius_sensitivity.py`/`encode.py`/`sentiment.yaml`/`pipeline_v34_rerun.yaml`/`paper_spec.yaml`/`golden_panel_v0.json`/`test_omni_fix_attention.py`/`stata/*_label_*.do` ×6/`generate_*labels.py`/`test_34/test_45/test_dual_track/test_fintech_indicators/test_iss_llm_score_subset/test_omni_fix_tonellms/test_stage3_dual_track` 等。
- **实证零文件交集**: 我方 28 文件与并行 ~21 文件**无任何同文件双改** (逐文件 grep: 我的文件 0 loughran 签名; 我未碰它们的文件)。故按名可干净隔离。
- **提交铁律**: 若提交, by-name 只 `git add` 我方 28 文件 (见 manifest), 排除全部并行文件 + `_regen_backup_20260620/` + `dicts_excel/.../_work/`。**勿 `git add -A`** (会误推并行未定稿的 6th-dict 集成 + 误 bless 其 T=2 golden)。
- **未提交** (一致于前三轮; 并行会话仍活跃, 由用户在其收口后统一 reconcile)。

---

## 5. 给用户的诚实结论

**4 轮审计已逼近收口, 但"收敛"取决于执行而非再审:**
1. **诚信维度已收口** — 4 轮 0 造假/0 数据腐败, 再跑同形审计抓造假边际≈0。
2. **缺陷维度本轮仍净增 1 真 P1 (stage18)** 并已修 → 证明多轮审计对"声明-实现缺口"类 bug 仍有递减但非零边际; 预期第五轮再发现新 P1 概率显著下降。
3. **真正的剩余是"提交 + 生产重生", 非"再审"**:
   - 28 文件修复**未提交** (用户决策 + 并行会话活跃)。
   - 全部"日志=测试/import 残片"的最终自愈需一次干净生产 run (18/21/30a/31/38/40/52 重生) + golden 受控重生 (OMP_NUM_THREADS=1 排 3 BLAS-FP 网络列), 受 data/raw 空 + M0 付费门控。
   - 并行 loughran 会话的 2 项 (decay_sensitivity:896 / export.py:109) 由该会话顺修。
4. **建议**: 收口路径 = (a) 用户决定是否提交我方 28 文件 (按名隔离已验证可行); (b) 待并行会话结束 + T=18 数据/M0 就位后一次性生产重生; (c) 而非再跑第五轮同形日志审计。
