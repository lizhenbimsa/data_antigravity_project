# 指标审计 — 终审核查闭合 (META-VERIFY, 2026-06-10)

> 对 `METRIC_AUDIT_TOPTIER_2026-06-09.md`(38 条 confirmed)做最高标准独立核查:**第二批更挑剔的 skeptic 逐条重新证伪 37 条 + 同型兄弟扫描 + 覆盖盲区扫描 + 复核 2 个"清白"单元**,再由主控亲验/web 核对所有重校准与新发现。本文是核查闭合,记录裁决变更、新增、以及对核查本身的纠错。

**核查日期**: 2026-06-10
**方法**: 元核查工作流 (**47 agents / 3.8M tokens / ~14min**) = 37 独立重证伪 + 10 覆盖扫描 → **主控亲验 7/7 + web 核对 1 个 + 数据核对 2 个**。
**总裁决**: 原 37 条 → **33 upheld / 2 downgraded / 1 upgraded / 1 false-positive**;**122 同型兄弟站点**;**23 覆盖新发现**;主控又**纠正核查自身 2 处过度声称**。

---

## 0. 核查可信度结论

原审计的元层**推翻率仅 2.7%(1/37)**,远低于本项目历史 15–20% —— 印证原审计(每条已配 2 个 verifier + 主控 7/7 亲验)定级稳健。但**核查层自身并非无误**:主控用 web/数据核对逮出核查工作流的 **2 处过度声称**(见 §3 纠错)。核心教训重申:**无单一自动层足够;主控经验/web 核对是终裁。**

主控独立复核(与工作流并行,7/7 + 3 额外):
| 发现 | 主控独立证据 | 与工作流裁决 |
|---|---|---|
| lmfls-01 未落地 | git log:`lm_non_sentiment.py` 仅 docs/创建提交,无分母修复 | 一致(工作流降 P3) |
| embedding L2 | `normalize_embeddings` 全仓 0 命中;encode_local 未归一 | 一致 upheld |
| network-04 docstring | 当前 L301-303 仍含"打破反射效应, 满足排他性约束" | 一致 upheld |
| ivdid-05 | 盘上 present-row rowsum: type/scale/mauth/geoprox=**1.0000**, media=**0.7273** | 一致 upheld(**主控加细:仅 media 受影响**,mauth/geoprox 无 other 故 =1) |
| toneberts-03 | `bert_num_windows` 在 panel 0 消费 | 一致 upheld |
| ctx-fallback | pandas 3.0.3 `astype(str)` 对 NaN 返 float nan,逐行 `str()` 返 'nan'/'None' | 一致 upheld |
| Distel 引文 | **web 核实:论文真实存在**(RP 55(3):105426, 2026-02-02 online) | **推翻工作流"likely fabricated"** |
| 区域 phantom | 盘上 bank_province ''=0/NaN=0(全匹配)→ 无 phantom 组 | **降 P1→P3-latent** |
| Int8 stata_audit 加法 | `pos_count(Int8)+neg_count(Int8)` 实测 `98+60=-98` 回绕 | upheld(**修正主控原"无其他站点"声称**) |

---

## 1. 对原 37 条的裁决变更(4 条)

### ⬆ 升级 P2→P1 · `tonellms-prob-score-skips-verified-filter`
连续 `avg_llm_prob_score` 是 falsification/稳健性主 DV(`falsification_template.do.tmpl` "用连续替换离散, β 须同号同强度"),却比离散 DV 多纳入 verified=False 模型的情感 → **两个 DV 算在不同模型子集上 → falsification 检验结构性失效**(非 label nit,是 valid-vs-physical 域不匹配)。盘上实测:1010/3507(28.8%)情感票来自 verified=False 模型;328/1170(28%)文章 final_v=False 却全部带非 NaN prob_score 进均值;verified-gated 重算在 195 篇上不同(mean|Δ|≈0.08/max 0.63)。且经 encode.py:809 + 加权变体(vw/mw/hw)一并传播。git 证 ff33e879 起从未门控(tone_llms-02,2026-06-02 即标)。**升 P1,与 P1 族并列。**

### ⬇ 降级 P2→P3 · `lmfls-01-denominator-not-fixed`
事实全 upheld(分母含标点+数字,字节级等同 V3 标记,git 证从未修)。但**唯一分析敏感消费者** `lm_discriminant_validity.py:122` 用 **Pearson 相关**(尺度不变,分母统一缩放不改相关)→ 判别效度统计不受影响;受影响的只是 frac 的绝对水平。**若 frac 作 level 进 Stata 回归则仍 P2(衰减)**,否则 P3。保守按 P3 + 该 caveat。

### ⬇ 降级 P2→P3 · `stratdiff-centroid-emb-clip-hides-high-tail`
数学声称对(嵌入 1-cos 可达 ~1.95),但 `strategic_diff.py:1580-1586` 有 assert 把所有 centroid 列界定在 [0,1+ε] → clip 是为通过该 assert 的防御;影响仅"高分化尾部被压到 1.0"(信息损失),非数值崩溃。**P3(尾部信息损失),修法=embedding 轨 clip 到 [0,2] 并改 assert。**

### ✗ 假阳性(非 bug,env-conditional)· `stata-export46-no-nullable-coercion-fallback`
工作流推翻:**pandas 3.0.3 `to_stata` 原生处理 nullable 扩展类型**(Int8/Float64+pd.NA),fallback 路径不崩。**但**原发现明确限定"pandas 2.x minimal-install"(生产 pin `>=2.2,<3.0`,lock 2.3.3),工作流只在 3.0.3 验证。**裁决:当前/3.0 env 非 bug;保留 P3-latent 备注(生产 2.x pin 未实测,且见 §2 pyreadstat byte 真实导出隐患)。**

**其余 33 条 upheld**(含 4 个 P1:fintech_share / VW-MW-HW / peer_tone 伪零 / BW2012 裸比率;及全部 P2/P3 公式-引文-聚合-双轨-确定性族)。

---

## 2. 覆盖扫描新发现(23,经主控adjudication)

### 真实且重要(纳入清单)
- **【P1 族】clarity 加权均值 valid/physical 域不匹配** `encode_collab.py:528-557` — `mean_clarity_score`/`mean_frac_definite`(media-auth×herd 加权)分子限 clarity-valid、分母 Σw 全物理 → 系统下偏。**VW/MW/HW(P1-2)的未标记同型兄弟**;同处 `aggregate_num_intensity_panel` 624-655 NaN-分母同病。
- **【P1-leakage】clarity 二值化用 in-sample pooled median** `encode_collab.py:501-507` — `median_amb_d0` sidecar 存在但**未接线进二值化**(每跑现算 in-sample)。benefit `_center` 同型兄弟。
- **【P1-leakage】benefit_pos/neg_frac in-sample median**(原 benefit 发现的再确认,benefit_society.py:631)。
- **【P1-domain】geography `compute_regional_imitation_pressure` 在"清白"单元再审中发现**:无 matched-row 守卫 → 理论上把 geo 未匹配行并入 phantom `('',year)` 组。**主控数据核对:盘上 0 未匹配 → 当前不触发,降 P3-latent**(全量新增银行若填 '' 而非 NaN 才触发)。
- **【P2 citation】Tetlock (2011) 误标 JF,实为 RFS 24(5):1481-1512** — 横跨 `herd_decay.py:22`/`dag.py:268`/`encode.py`/`geography.py`/`export.py`/`runner.py`/`article_staleness.py` 8 处。**⚠ 本审计上一版报告也沿用了"Tetlock 2011 JF",一并更正。** Tetlock 2007=JF;2008(More Than Words)=JF;2011(All the News…)=**RFS**。
- **【P2】tone_words IDF 的 DF 在裸 `内容`(无标题)上算,却应用于 title-prepended 打分文本** `tone_words.py:558,584,1297` — 违 Gentzkow-Kelly-Taddy(2019)TF-IDF 同语料要求(IDF 语料 ≠ TF 语料)。
- **【P2】cross_media_alpha 事件检测 `>= p90` 对零方差 bank 判 100% 天为 shock** `cross_media_alpha.py:97-100` — 退化(改 `>` 或加方差守卫)。
- **【P2 dual-track】benefit_society alt_anchor + audit_combined 仅 full 轨** — 验证 ctx 主处理的稳健性锚却无 ctx 轨。
- **【P2-latent】Int8+Int8 裸加法 `stata_audit.py:357-361`** `pos_count.fillna(0)+neg_count.fillna(0)` 静默回绕(实测 98+60=-98)→ **讽刺地击穿了它自己要查的 pos+neg>n 双重计数审计**。**修正主控原报告"全仓无其他裸算术站点"声称**(原扫描漏了 `pipeline/audit/`)。当前 T=2 max 100 不触发,T=19 latent。
- **【P3-latent】pyreadstat 把 [101,126] 的 Int8 计数写成 Stata 扩展缺失(.a–.z)** `stata_export.py:550-557` — `gpt54nano_tone_sum_full` T=2 已=100,T=19 必越界 → 静默变 Stata 缺失。生产 pyreadstat 路径(to_stata fallback 会安全 upcast)。**与 §1 stata-export46 合并为"导出层 Int8/byte 隐患"。**
- **【P2 citation】benefit 阈值把 median-centering 归因 Mu-Viswanath/Ethayarajh 各向异性校正** `benefit_society.py:621-639` — 该操作不实现这两篇方法,过度归因。
- **【P3】forward_looking FLS 多字词标记 jieba 不整词切出** `forward_looking.py:86-99` — clarity/LM jieba 注入同型兄弟。
- **【P1-doc / 主控独立同源】codebook 复现包硬伤再确认**:94.2% 空引用 + 94% 占位描述 + `year` 范围 [2013,2023] 实 2017-2018 + **24 列未登记/9 幻影列 + `avg_locus_prob_score_std` 范围 [0,0.5] 实际越界**(schema 陈旧)。

### 主控推翻核查的过度声称(诚实纠错,2 处)
1. **"Distel-Grimpe-Poetz (2026, Research Policy) likely fabricated" → 推翻**:web 核实论文**真实存在**(RP 55(3):105426,2026-02-02 online;hidden/token citation 的 NLP 方法,与代码"显性引用 vs 文本级语义实质借鉴"概念契合)。**严禁把"伪造引文"写入报告 —— 那是对用户研究诚信的不实指控。** 仅余软提示:确认 §3.2.1 是否确含逐文余弦(概念锚已成立)。
2. **"regional phantom = P1 active" → 降 P3-latent**:覆盖 agent 从代码(无守卫)推断,未核数据;盘上 0 未匹配行 → 不触发。

---

## 3. 对核查本身的元纠错(meta-meta)
本次核查的**自动层(工作流)亦有 ≥2 处过度声称**,全部由主控 web/数据核对逮出:(a) Distel 引文误判"伪造"(实存);(b) regional phantom 误判 P1(数据 0 触发)。**这正是分层验证的价值:对抗 verifier 抓 plausible-but-wrong,主控经验/web/数据抓 verifier 自身的过度声称。** 计入"诚实边界"。

---

## 4. 最终校准清单(并入 METRIC_AUDIT_TOPTIER_2026-06-09)

**P1(实质,进发表)= 5 → 6**:原 4(fintech_share / VW-MW-HW / peer_tone 伪零 / BW2012)+ **tonellms prob-score(升级)** + **clarity 加权均值族(新,VW/MW/HW 同型,含 in-sample median 二值化 leakage)**。

**P2 ≈ 20 → ~24**:原族基本 upheld,新增 Tetlock-RFS 误引(8 处)、tone_words IDF 语料错配、cross_media_alpha p90、benefit alt_anchor 单轨、benefit median 归因、Int8 stata_audit 加法(latent)。lmfls-01/stratdiff-centroid 降出 P2。

**P3 ≈ 6 → ~10**:+ lmfls-01、stratdiff-centroid、regional phantom(latent)、pyreadstat byte、forward_looking FLS jieba。

**清白背书加强**:encode_collab 的 D2 cell_id/D4 残差核验 clean(仅 clarity 加权均值族有缺陷);geography haversine/z-score/LOO/coval-moskowitz 引文 clean(仅 regional phantom latent);benefit_mean、herd O(N·window)、policy cosine(Distel 引文真实)、Bartik 代数(media 除外)等核心算法仍 clean。

**假阳性最终(并入原 6 → 8)**:+ stata-export46(env-conditional)、Distel"伪造"(web 推翻)。

---

## 5. 结论
原审计经最高标准元核查 **96% 站得住**(33/37 upheld 含 4 P1),仅 1 升级、2 降级、1 env-conditional 假阳性;覆盖扫描补出 ~10 条真实新发现(尤以 **clarity 加权均值族 P1 同型兄弟** 与 **tonellms prob-score 升 P1** 最重要),并修正主控原报告 2 处(Int8 站点不完整、Tetlock 误引)。核查自身 2 处过度声称由主控 web/数据逮出。**最终清单:~6 P1 / ~24 P2 / ~10 P3 / 8 假阳性。修复路线图(阶段 0 纯文档+引文+codebook、阶段 1 $0 本地重算+golden 重生)不变,新增项归入对应阶段。** 报告与代码现状一致;未改代码,待 user 拍板落地。

## 附:核查产物
- 本文 `METRIC_AUDIT_METAVERIFY_CLOSURE_2026-06-10.md`(核查闭合,权威)
- `_metaverify_parsed.md`(37 重证伪 + 23 覆盖新发现全文)· `_meta_verify_input.json`(核查输入)
- 工作流脚本 `scripts/audit/_meta_workflow.js`(可复跑)
- 上游 `METRIC_AUDIT_TOPTIER_2026-06-09.md`(被核查的原报告)· `_wf_findings_parsed.md`
