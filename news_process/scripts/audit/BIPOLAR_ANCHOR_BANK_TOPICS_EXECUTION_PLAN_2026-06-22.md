# 双极锚点投影 × 银行研究话题 — 执行计划 v3 (每主题专属锚轴)

**日期**: 2026-06-22 (v3; v1→v2→v2.1→v3 演进见 §0.5)
**状态**: **本计划文档** PLAN-ONLY / golden-safe (不触 pipeline/shim/DAG/golden)。⚠ **落地不 golden-safe**:
任一轴上线 (§8 Phase 1+) 经 runner step 7h (`compute_benefit_society_panel` 同族, inline 注入 stage 40 panel,
**不新增 DAG 阶段/schema 注册**) 产新面板列 (每轴 ~24 列 = 3 轨 × {mean/std/pos_frac/neg_frac} × {canonical/_t2v},
12 轴 ≈ 288 列) → **必改 40/46/golden 列哈希 → 触发 stage 45/46 + golden 受控重生** (CLAUDE.md 约束6,
`PYTHONHASHSEED=0`+线程钉死, 排 BLAS-FP 网络列)。成本: stage 21 LLM 投票=$0 (不触发); 锚句+文章嵌入走
embedding API/本地 text2vec (远低于 LLM; 现盘文章嵌入大概率缓存命中, 仅新增 12×~20≈240 条锚句嵌入是真新调用, 极小)
**权威性**: 四轮文档/可行性对抗审计 + 三轮锚句设计+验证工作流 (12 主题 × 10 对, difflib 单词替换全过, 0 假阳; 第二轮 JLM 样式润色, 第三轮新增 JLM 社会主题轴) +
用户 2026-06-22 决策「不考虑成本; 对不同主题用**不同**正/负极锚句做 LLM-Embedding 双极锚点投影」「每个主题独立存在, 不计算彼此间异同」。
**前置铁律**: **各主题独立, 不做轴间判别** (见 §3); 实施任一轴前必过 §4 财务列接入 + 面板深度 T=19 + §3 该轴锚句轴内 margin/符号自检 (advisory)。

---

## 0. v3 架构 — 每主题一条专属双极锚轴

### 0.1 核心决策 (用户 2026-06-22)
**每个研究主题用自己专属的一组正/负极锚句**做 LLM-Embedding 双极锚点投影 (不再共享 benefit_society 的
`benefit_mean`)。机制对每轴相同 (Jha-Liu-Manela 2026 RFS §1.3.2): 正/负极锚句各嵌入 → 方向向量
`p=mean(pos)−mean(neg)` → 文章投影 `a_j=cos(s_j,p)` → bank-year 聚合 → 该主题的**媒体叙事/态度连续指数**
(= treatment)。真实财务量始终作 **outcome** (同源测量误差铁律)。

> **此决策一举解决前四轮评审的两大硬伤**: (a) v2 的 F03「benefit_mean 是金科窄构念被拉去解释一切」——
> 现每轴是为该主题量身定制 (如风险承担轴用风险承担锚句, 直接测「媒体对该行风险承担的叙事」), 传导链天然成立;
> (b) v2 的撞稿/salami——每轴 treatment 现**真正不同**, 与既有 11 篇论文的 treatment 天然区分 (§10), 独立成篇
> 更站得住 (镜像项目内 disagreement/clarity 共 z_score 却独立两篇的先例)。

### 0.2 覆盖范围: 12 主题专属轴
> **用户 2026-06-22 调整**: ① 剔除 **盈利能力 / 经营绩效** (与 benefit_society 已做的"金科态度→ROA/绩效"完全重复, 撞 PAP 锁定的 roa);
> ② **经营效率作单一主题** = **成本效率 + 利润效率合一** (Berger-Mester 1997 JBF cost efficiency + profit efficiency, **不分两轴**);
> ③ **特许权价值保留, 全样本统一 Lerner 口径** (覆盖中国商业银行业**所有银行**含非上市; 文献核实见 §5.11/§9);
> ④ **续删 全要素生产率 + 同群效应** (用户 2026-06-22): 全要素生产率轴整体剔除; 同群效应 (§6 网络空间溢出/peer-LOO IV) 整体删除;
> ⑤ **增 JLM 2026 RFS 社会主题轴** (用户 2026-06-22, 用户原话「完全借鉴 JLM」): 新增 **社会效益 (金融惠及社会) `social_narr`** valence 轴,
> **借鉴 JLM「Does Finance Benefit Society?」社会构念 + KTE 双极投影 + 5 极语义** (firm-year 迁移, 见 §5.12 改编与迁移声明); valence 2→3。→ 14 → 13 → 12 → 11 → **12 轴**。

| 族 | 轴类型 | 主题 (轴) |
|---|---|---|
| **valence 好↔坏轴** (3) | 正极=好/负极=坏 | 经营效率(含成本+利润效率)、特许权价值、社会效益(金融惠及社会; JLM 社会主题) |
| **direction 方向轴** (9, 极性中性) | 多↔少, 不含好坏 | 风险承担、资金成本、流动性创造、流动性囤积、资本缓冲、信贷期限结构、多元化经营、信贷决策、贷款损失准备计提 |

完整锚句库见 **§5** (12 套, 每套 **10 对**, 共 120 对; JLM 样式润色, difflib 单词替换 0 违规)。

### 0.3 关键铁律 (direction 轴专属)
**direction 轴零点不预设好坏**: 「加大风险承担」「拉长信贷期限」「囤积流动性」本身无褒贬 — 投影正不蕴含规范
判断, 好坏交由 outcome 端经济学解释。codebook 须显式声明 direction 轴**无 valence**, 防审稿人误读冒险=坏。
- ⚠ **列名 valence 冲突 (F05)**: 克隆模块机械产 `<前缀>_pos_frac`/`_neg_frac` 列 ((x>center)/(x<center) 占比),
  对 9 条 direction 轴, 列名 pos/neg 字面隐含好坏。处理: codebook valence 声明须**点名 `*_pos_frac`/`*_neg_frac`
  同受零-valence 约束** (pos=投向替换词正向, 非褒贬); 不改列名以保 benefit_society 字节级契约/golden 不破。
- ⚠ **outcome 端叙事护栏 (F15)**: 零-valence 在 treatment 端; **outcome 端论文叙事**同样须 positive-economics 框定
  (报符号+机制, 不下规范判断)。风险承担/信贷决策等敏感轴须显式区分"效率性中介深化"与"过度冒险"两种解读, 引 §9
  的 Laeven-Levine 2009 / Houston 2010 让数据而非作者定性。

---

## 0.5 修订记录 (v1→v2→v2.1→v3)
- **v1**: 每题可能新轴 (含部分新轴草案)。
- **v2/v2.1 (用户「完全复用 benefit_mean」)**: 共享 treatment + swap outcome; 第④轮评审 (19 confirmed/0 假阳)
  暴露 F03 (benefit_mean 是金科窄构念) + 多处撞稿。
- **v3 (用户「不考虑成本, 每主题用不同锚句」)**: 翻转为**每主题专属锚轴**, F03 与撞稿自动消解; 锚句库经设计+
  对抗验证工作流 (14 主题 difflib 单词替换全过)。继承前四轮所有方法论修复 (见各节)。
- **反向假阳 (锁定)**: JLM 2026 RFS **39(5):1227-1266 已正式见刊** (Editor's Choice, DOI 10.1093/rfs/hhaf012);
  勿再判编造。
- **引用订正** (设计工作流捕获): Berger-Kim-Ma 2024 CAR 标题=「Bank sentiment and liquidity hoarding」
  41(3):1513-1542; Pagan 1984 是生成 **RHS**, 生成 LHS 残差 (DELR/Lerner/SFA) 用**整链 block-bootstrap by bank**
  (Murphy-Topel 1985 是两步估计量方差修正, 不直接覆盖 LHS-生成; 最稳健用整链 bootstrap)。
- **第⑥轮 v3 文档评审 (GO_WITH_FIXES; 33 原始 → 25 去重 → 14 confirmed + 11 partial + 0 假阳; 架构本身确认站得住)**,
  5 must-fix + 7 should-fix (+ P3 精修) 已并入:
  - **F01**: §3 订正 — stage 72 (文章级离散 NMI) 对 bank-year 连续投影**范畴不适用** (移出判别门); stage 73
    硬编码 3 indicator 须**实质重构** (非"扩 run 入口"); 新增门 A (vs benefit_mean) / 门 B (N×N; 第⑥轮 14 轴态, 后续多轮重构 (现态轴数见 §0.2); §3 轴间判别门已整体退役)。
  - **F02**: §3.1 回退订正 — benefit_society **无子维度** (仅单一 benefit_mean), 虚构的"benefit 子维度/扩展表"落点
    改为可操作 (改窄锚重测 / 并入既有论文 horse-race / 作 benefit_mean 稳健对照)。
  - **F06+F07**: §5.8 拨备轴锚句去价值词 (审慎/充分↔宽松/不足 违 direction 零-valence) + 修第5对长度不等, 改纯时点/力度方向。
  - **F08**: §3.1 判别三档补特许权价值入 medium → 求和 7+4+3=14 (第⑥轮 14 轴态; 剔盈利/绩效后 13 轴态; 判别三档与 §3.1 后均整体退役)。
  - **F03/F04/F05/F09/F10/F11/F13 (should-fix)**: 头部 golden-safe 限定 (落地必触 golden 重生); §3.2 轴存活情景表;
    §7 监管断点 depins 同步全国 vs dcep/sandbox 分批; §3.0b 全轴单因子 (PC1/partial-out) 前置诊断; §4.3 接入两级 +
    roe/nim 未登记守卫; §9 JLM 粒度迁移声明。
  - **P3 锚句精修 (F16/F21/F22/F23/F24)**: 列前缀 `_attn`→`_narr` (避与 attention 撞名 + 语义对) + 命名守卫;
    §5.1 风险承担去价值词 (助长/激进/投机性); §5.6 经营效率第5/9对对称化; §5.7 TFP 补足 10 对。
  - **接受/已注 P3**: F12(v34 liquidity_creation 已补登记)/F14(路径前缀)/F17(GMM 工程分流, §7 已注)/F18($0 精确化,
    头部已注)/F19(批量裁决, §3.1 已加)/F20(sigma_roa 登记)/F25(流动性创造长锚 margin, §5.4 上线实测)。
  - **反向假阳 (锁定)**: JLM 2026 RFS 39(5):1227-1266 已见刊, 评审 0 假阳, 全程未误判其编造。
- **第⑦轮 v3 最终终审 (GO_WITH_FIXES; 28 原始 → 16 去重 → 15 confirmed + 1 partial + 0 假阳; 架构再确认站得住)**,
  收口 2 must-fix (均第⑥轮 fix-propagation 残留) + 9 should-fix 已并入:
  - **F01 (must-fix)**: §3.1 high 档"流动性创造→先在 benefit_society 建流动性子轴"是循环规避 + 把 outcome 列当 treatment
    子维度 (违铁律#1) → 改可操作回退 (改窄锚/benefit_mean 稳健对照/treatment-side horse-race)。
  - **F02 (must-fix)**: 头部 L12 + Phase 2 仍写"stage 72/73 HTMT" (stage 72 产 NMI 非 HTMT 已移出) → 改 stage 73。
  - **should-fix (已并入)**: F03 逐对自检标 advisory 非 gate; F04 confirmatory primary 唯一钉死 + outcome 共线门;
    F05 direction 轴 `*_pos/neg_frac` 列名 valence 声明; F06 horse-race 回退仅 exploratory 不替宿主 PAP; F07 投影列
    归 runner step 7h (非 stage 15); F08 z_score CAR-变体披露; F09 partial-out 双向风险 (under-reject); F12 ss 轨
    退化 + 双嵌入投影稳定性上线门; F15 outcome 端叙事护栏; F10 术语/计数精度 (门 A |corr| / high档<4 / 计数)。
  - **接受 P3**: F11(§5.1 动词/pair6 留 T=19 实测)/F13(门 B descriptive 已注)/F14(附录路径前缀)/F16(§5.11 催生↔裁撤 边际)。
  - **结论**: 架构 (每主题专属锚轴) 经 7 轮确认站得住; 文档层达顶刊可执行标准。**仅余实施期前置门** (T=19 实测
    stage 73 HTMT / stage 73 须实质重构 / 财务接入 + golden 受控重生 / ss·t2v 投影稳定性上线实测) — 非文档可闭合。
    *(注: stage 73 HTMT/重构 二项已被后文「各主题独立, 不做轴间判别」决策整体退役, 见 §3; 此为第⑦轮时序快照)*
- **用户 2026-06-22 轴集调整 (14 轴 → 13 轴)**:
  - **① 剔除 盈利能力 `profit_narr` + 经营绩效 `perf_narr`**: 二者本质即 benefit_society 已做的"金科态度→ROA/绩效"
    (撞 benefit_mean→roa PAP 锁定 + strategic_diff tobin_q), 不另立。→ §2/§5/§3.1/§10 同步删。
  - **② 经营效率 `cir_narr` 拆为 成本效率 `costeff_narr` + 利润效率 `profiteff_narr`** (锚 **Berger-Mester 1997 JBF**
    银行 cost efficiency vs standard/alternative profit efficiency 二分): 成本效率保留原成本侧锚句 (outcome=CIR_change_3yr);
    利润效率新建 profit-frontier 锚句 (outcome=SFA 利润效率 或 PPOP/资产 代理), 区别于已剔的盈利水平。
  - **③ 特许权价值 `moat_narr` 保留** (经文献核实, §9): 非上市银行**可用会计型 Lerner 指数** (价格-边际成本加成) 测
    特许权价值/市场势力 (Berger-Klapper-Turk-Ariss 2009 JFSR / Jiménez-Lopez-Saurina 2013 J.Fin.Stab. 明确把 Lerner 当 franchise
    value 直接代理; 理论 Keeley 1990/Marcus 1984/Hellmann-Murdock-Stiglitz 2000)。主 outcome=Lerner (全样本含非上市);
    上市子样本另算 Tobin Q 作代理有效性对照。
  - **计数更新**: valence 5→4 (成本效率/利润效率/TFP/特许权), direction 9 不变; 总 14→13; 判别 high 7→6 (剔盈利/绩效,
    经营效率→成本效率, +利润效率), medium 4 / low 3 不变。§0.2/§2/§3.x/§4/§5/§9/§10 全量对齐。
- **第⑧轮 13轴重构后终审 (GO_WITH_FIXES; 25→9→8 confirmed + 1 partial + 0 假阳; 重构主体一致, §2↔§5 100% 对齐)**,
  3 must-fix + 6 should/P3 已并入 (均纯文档 fix-propagation 残留, golden-safe):
  - **F01**: §8 Phase 2 残留"high 档 7 轴" → 6 (唯一残留旧计数)。
  - **F02**: §7 F04 / §4.3 / §8 Phase 0a 仍以已剔的盈利#2/绩效#13 + 无消费方 roe 作多-outcome 锁主范例 → 改现役轴
    (风险承担锁 Z-score / 特许权锁 Lerner); roe 降 horse-race 备列, nim 改挂特许权稳健代理。
  - **F03**: §7 生成-LHS 整链 bootstrap 条款补全 — Lerner (translog 估 MC) + SFA 利润/成本效率 (复合残差) 同属生成量,
    并入 block-bootstrap; 显式区分 PPOP/CIR/Tobin_q 纯观测量不触发。
  - **F04**: §4.2 Lerner 从"纯会计 0a"移到"估计步骤 0b" (须 translog 投入价格, 仍不需股价适用非上市, 但非纯 merge)。
  - **F05**: §7 outcome 共线门簇示例 ROA/ROE/NIM → 现役**三效率轴簇** (CIR/PPOP-SFA利润效率/TFP), 与 treatment 端对称。
  - **P3/补强**: F06 §3.1 特许权共线对象改 benefit_mean/strategic_diff (删盈利/绩效孤儿轴); F07 §5.13/§9 "Lerner 直接代理"
    软化为"市场势力代理/franchise-value hypothesis 检验量"; F08 §9 Tetlock 改通用方法学锚; F09 §0.5 历史快照加限定;
    + 新增 Lerner↔Tobin Q **可证伪对照判据** (符号一致+|corr|阈, 发散则改报市场势力非 franchise value)。
  - **结论**: 13 轴重构经第⑧轮确认一致无残留 (high 计数 100% 对齐, 0 残留旧轴号); 文档层达"万无一失"。
- **用户 2026-06-22 二次调整 (13 轴 → 12 轴)**:
  - **① 经营效率合一**: 撤销上一轮的"成本效率/利润效率拆两轴", 按用户令**合为单一"经营效率"主题 `effic_narr`** (含成本效率
    + 利润效率两维, Berger-Mester 1997)。新锚句 10 对覆盖成本侧(2/3/6/7)+利润侧(4/8)+整体前沿(1/5/9/10); outcome = 成本效率
    (CIR/SFA cost) + 利润效率 (SFA profit/PPOP) 作同一论文两维, 单一 confirmatory primary 二选一。→ valence 4→3, 总 13→12,
    high 6→5。此举顺带消解上一轮评审 F05 的"三效率轴 outcome 簇"共线 (现降为经营效率内部成本↔利润维)。
  - **② 特许权价值全样本统一 Lerner 口径**: 按用户令"覆盖中国商业银行业所有银行", 明确 **Lerner 指数为全样本(大型/股份/
    城商/农商/民营, 含上市非上市)单一 outcome 口径**; Tobin Q 仅上市子样本验证 Lerner 代理有效性, 非上市行独立 outcome。
  - **全量对齐**: §0.2(valence 3)/§2(12 行)/§5(5.1-5.12)/§3.0-3.2(12 轴/high 5/5×5)/§4.2/§7/§9/§10 + golden 288 列 已扫。
- **用户 2026-06-22 三次调整 (各主题独立 + JLM 锚句润色)**:
  - **① 各主题独立, 不做轴间判别**: 按用户令「每个主题都是独立存在的, 不需要计算彼此之间的异同」, **整体退役原 §3 轴间判别硬门**
    (stage 73 HTMT / 门 A vs benefit_mean / 门 B N×N / 全轴单因子 PC1 诊断 / 判别风险三档 / 批量裁决 / 轴存活情景) +
    §2 删"判别风险"列 + §7 删轴间 outcome 共线门 (N×N 相关矩阵 / 经营效率↔TFP 跨轴护栏) + §8 Phase 2 改纯轴内 margin/符号
    自检 + 删 Phase 6 high 档回退收尾 + §10 删"须证判别/high 风险"门语。**保留** (与轴间互比无关): 各轴锚句轴内 margin/符号
    自检 (advisory) + 单篇内单一 confirmatory primary (p-hacking 控制) + §10 与既有 11 篇论文的共享-outcome 交叉引用披露
    (publication ethics, 非 12 轴互比)。
  - **② 12 套锚句按 JLM 样式润色统一形式**: 按用户令「根据 JLM 2026 RFS 锚句样式, 对 12 套锚句润色修改, 确保形式一致」,
    以 `config/jlm2026_chinese_anchors.yaml` 官方 5 对中文锚 (金融服务有益↔损害社会 / 金融对世界产生积极↔消极影响 等) 为样式
    权威, 二轮工作流 (12 polish + 12 verify 全 pass + harmonize) 统一: 主语标准化 (金融科技/银行数字化转型/数字金融服务/金融
    科技应用 固定小集合)、句长收敛 14-18 字、去技术性长从句、严格 single-word-change + 正负极等长、valence/direction 极性词
    类型匹配。§5.1-§5.12 全量替换。
  - **全量对齐**: §0(权威性两轮锚句工作流)/§2(删判别风险列+独立声明)/§3(轴内自检)/§5(润色锚句+删轴间 HTMT 剔除 caveat)/
    §7(删轴间共线门)/§8(Phase 2/4/6)/§10(共享 outcome 披露) + 附录(六轮工作流)。
- **用户 2026-06-22 四次调整 (删 全要素生产率 + 同群效应; 12 → 11 轴; 仍 PLAN-ONLY 未提交)**:
  - **① 删全要素生产率轴** (原 #6 `tfp_narr`, valence): §2 删行并将 #7–#12 重编为 #6–#11; §5 删 §5.6 TFP 锚句套并将 §5.7–§5.12
    重编为 §5.6–§5.11; valence 3→2 (仅 经营效率/特许权价值), direction 9 不变; 锚句 120→**110 对** (11×10); golden 列 288→**264**
    (11×24)。连带删: §4.3 估计步骤的 TFP(LP/OP/ACF)、§7/§8 生成-LHS 的 "TFP 残差/Levinsohn-Petrin/ACF"、§9 删 Levinsohn-Petrin
    2003 + Ackerberg-Caves-Frazer 2015 (TFP 生产函数专用; 保留 Berger-Mester 经营效率 + Pagan/Murphy-Topel 生成回归量)。
  - **② 删同群效应** (原 §6 网络空间溢出): §6 改信息性墓碑 (保留节号避免 §7–§10 连锁重编); 删 §0.2 方法行 + §8 Phase 5 (同群效应叠加)。
    **识别后果**: 各轴 IV 从 peer-LOO (`leave_one_out_peer_<topic>_iv`, Leary-Roberts) **切换为 zone-LOO 地理暴露主 + 广义 Bartik 作 over-id**
    (⚠ 四次调整初定"Bartik 主", 后经 P1-b 按代码现实订正为"zone-LOO 可立即落地主 + Bartik 须先构造文章级 shift 作 over-id、未构造则 just-identified", 见 §7);
    §9 删 Manski 1993 / Leary-Roberts 2014 / Bramoullé 2009 (peer-effect 专用), 补 Bartik 1991 /
    GPSS 2020 AER; 附录删 `network_spillover.py` 代码锚点 + GLMY path-homology 评估随之退役。
  - **机械校验**: §5 锚句从文档反解 11 套 / 110 对 difflib 单词替换+等长 **0 违规**; 全文 12→11 / 120→110 / 288→264 / valence 3→2
    计数全量对齐; §5.x 与 §2 # 序号一一对应; 多智能体顶刊复审 (见附录 ⑦)。
- **用户 2026-06-22 五次调整 (增 JLM 2026 RFS 社会主题轴; 11 → 12 轴; 仍 PLAN-ONLY 未提交)**:
  - **增「社会效益 (金融惠及社会)」轴 `social_narr`** (#12, valence): 用户令「完全借鉴 JLM 2026 RFS, 增加 JLM 社会主题」。落实 = **借鉴
    JLM「Does Finance Benefit Society?」社会构念 + KTE 双极投影方法 + 5 极语义 (firm-year 迁移)** (JLM 2026 RFS 39(5):1227-1266; Zingales 2015 JF 70(4):1327-1363 同名命题;
    KTE 2019 geometry of culture)。新 §5.12 锚句 10 对**回声 JLM 官方 5 极语义维度** (官方 yaml 逐字 = 有益↔损害/好↔**不好**/很好↔**邪恶**/
    积极↔消极/帮助↔**有害**; §5.12 为 valence 对仗+等长**改编**其负极, 仅 #1损害/#3消极 逐字重合, 余 8 处改编见 §5.12 披露), 经 7-agent 设计+对抗
    验证工作流 (3 候选→验证→harmonize) + 独立 difflib **0 违规** (10 对单词替换+等长 15–18 字+主语标准化)。outcome = 普惠金融 `inclusive_loan_growth` (v34:159)。
  - **关键区分 (codebook 须披露)**: 本轴 ≠ 项目既有 `benefit_society` 模块 —— benefit_society (名义"社会"实测**银行自身经营效益**
    business benefit, 宾语=经营效率/盈利/风控/合规); 本轴测对**社会**的 benefit (societal benefit, 10 对宾语 0/10 命中银行内部指标,
    全落 社会/民生/实体/公众/世界)。共方法异构念, 0 锚句重复; 填补项目内 JLM 真社会构念空缺。
  - **计数迁移**: 11→**12 轴**; valence 2→**3** (经营效率/特许权价值/社会效益); direction 9; 锚句 110→**120 对**; golden 列 264→**288**
    (12×24); 嵌入 ~220→~240。全文对齐: 头部/§0.2/§2(加#12行)/§3(轴数12)/§4.2+§4.3(Phase 0a 加普惠)/§5(加§5.12)/§7(轴数12+反向因果社会轴专款)/
    §8(Phase1/2)/§9(加 JLM社会+Zingales)/§10(加 social_narr 行)/附录(⑧)。**§5 从文档反解 12 套/120 对 difflib 0 违规 + 与 verified set 0 mismatch**;
    最终 19-agent 复审 GO_WITH_FIXES (0 P0/3 P1/4 P2/3 P3) 全部已修: §3+§7 stale 计数 11→12 / JLM 官方 5 极改编诚实披露 (仅 #1/#3 逐字重合, 余 8 处横跨①②③④⑤, 见 §5.12) / social_narr↔benefit_mean
    唯一同母本对描述性 |corr| 例外 + 职能划界(防 salami) / §7 社会轴反向因果专款 / "完全借鉴"→"借鉴+firm-year迁移" / §4.2+§9 outcome 接线。

---

## 1. 四条铁律 (代码已成文)
1. **投影 ≠ outcome**: treatment=媒体叙事投影, outcome=真实财务/监管报表量, 物理隔离 (同源测量误差)。
2. **三轨 full×ctx×ss 各自 just-identified 并排, 禁混进同一 over-identified Hansen J** (`iv_extensions.py:516-523`);
   跨族 over-id = 单轨内 广义Bartik×zone-LOO (须 Hansen J + KP rk F; **Bartik 须先构造文章级投影 shift, 见 §7; 未构造则 just-identified**)。
3. **vintage 前视守卫** (outcome/政策锚取各年 ≤t)。
4. **锚句 single-word-change** (正/负极仅替换一个核心词, difflib 单 replace span, 正负极等长, 其余字 100% 相同)。
   ⊕ **direction 轴零点无 valence** (§0.3)。

---

## 2. 12 主题专属锚轴总览

| # | 主题 (列前缀建议) | 轴 | 构念 (媒体叙事指数) | 配对 outcome |
|---|---|---|---|---|
| 1 | 风险承担 `risktaking_narr` | dir | 金科推升↔收敛 风险承担水平/敞口 | Z-score(主, CAR变体†)/RWA密度/NPL |
| 2 | 资金成本 `fundcost_narr` | dir | 金科压低↔抬高 计息负债成本 | funding_cost |
| 3 | 流动性创造 `liqcreate_narr` | dir | 金科放大↔收缩 cat-fat 中介转换 | cat-fat LC |
| 4 | 流动性囤积 `liqhoard_narr` | dir | 金科冲击→囤积↔释放 流动性 | LH 三分量比率 |
| 5 | 经营效率 `effic_narr` | val | 金科提升↔拉低 **经营效率 (含成本效率 + 利润效率)**; Berger-Mester 1997 cost & profit efficiency | 成本效率(CIR_change_3yr / SFA cost eff) + 利润效率(SFA profit eff / PPOP) |
| 6 | 贷款损失准备计提 `provtiming_narr` | dir | 金科→拨备 时点前后/力度多少 (中性方向) | DELR 残差(主, 限时点子维) + 拨备覆盖率变动/拨贷比(secondary, 力度子维) |
| 7 | 资本缓冲行为 `capbuf_narr` | dir | 金科增厚↔削薄 超额资本缓冲 | capital_buffer |
| 8 | 信贷期限结构 `maturity_narr` | dir | 金科拉长↔缩短 信贷期限/久期 | 贷款加权久期/中长期占比 |
| 9 | 多元化经营 `diverse_narr` | dir | 金科多元化扩张↔专业化聚焦 | 非息收入占比/revenue_hhi |
| 10 | 信贷决策 `creditstance_narr` | dir | 金科放宽↔收紧 信贷标准/额度 | 贷款增速 + 滞后 NPL 生成 |
| 11 | 特许权价值 `moat_narr` | val | 金科巩固↔削弱 护城河/特许权价值 | **Lerner 指数(主, 中国商业银行业全样本: 大型/股份/城商/农商/民营, 含上市与非上市, 统一口径)**; Tobin_q/market-to-book 仅上市子样本验证 Lerner 代理有效性 |
| 12 | 社会效益(金融惠及社会) `social_narr` | val | 金科有益↔损害 社会/公众/实体经济 (**JLM「Does Finance Benefit Society?」社会金融情感**, 借鉴 + firm-year 迁移) | **普惠金融 `inclusive_loan_growth`(主, 银行对社会真实贡献; v34:159 已登记)**; 涉农/小微贷款占比 作代理 |

> **各主题独立 (用户 2026-06-22)**: 12 轴各为独立研究主题, **不计算彼此间判别/异同** (原"判别风险"列已删, 见 §3); 轴 val/dir 计数 = valence 3 (经营效率/特许权价值/社会效益) + direction 9。**全要素生产率轴 (原 #6) + 同群效应 (原 §6) 已删; 社会效益 (#12, JLM 社会主题) 已增** (均用户 2026-06-22 决策)。

> 列命名是**新轴产物** (与 benefit_society 的 `benefit_mean_*` 并列, 各轴产 `_full/_ctx/_ss` + `_t2v` twin)。
> † z_score = CAR-based Z-score 变体 (Basel CAR/RWA 加权资本项), 非 Laeven-Levine 2009 原版 (账面 equity/TA), 投稿须标注 (§7)。
> ⚠ **轴集调整 (用户 2026-06-22)**: ① 剔除 盈利能力 `profit_narr` + 经营绩效 `perf_narr` (本质=benefit_society benefit_mean→roa
> 已做, roa 经 PAP v1.0-final 锁死); ② 成本效率 + 利润效率**合为单一"经营效率"轴 `effic_narr`** (用户令不分开, 作一个经营效率
> 主题, 含两个效率维度 outcome); ③ 特许权价值**全样本统一 Lerner 口径** (覆盖中国商业银行业所有银行); ④ **续删 全要素生产率 + 同群效应**; ⑤ **增 JLM 社会主题轴 社会效益 `social_narr`** (借鉴 JLM 2026 RFS, firm-year 迁移)。→ 14 → 13 → 12 → 11 → **12 轴**。

---

## 3. 锚句质量自检 (轴内; 用户 2026-06-22: 各主题独立, 不做轴间判别)

> **用户决策**: 12 个主题**各自独立存在, 不计算彼此之间 (及与 benefit_mean) 的判别效度/异同**。各轴构念/outcome/文献
> 本就不同 (见 §2/§9/§10), 区分性由**构念层**论证 (不同研究主题), **不靠 HTMT 实证**。故原 §3 的轴间判别硬门
> (stage 73 HTMT / 门 A vs benefit_mean / 门 B N×N 矩阵 / 全轴单因子诊断 / 判别风险三档 / 批量裁决 / 轴存活情景)
> **整体退役**; §2 不再设"判别风险"列, 各轴一律作独立研究主题落地。

**唯一保留 = 各轴锚句的轴内自检** (与轴间判别无关): 每轴投影前过 `benefit_society.py:129-130` 的 `anchor_pair_min_margin`
(0.02) / `anchor_sign_tolerance` (0.03) 逐对 margin+符号检验 (正极投正/负极投负), 确保该套锚句方向向量纯净。
> ⚠ 此自检是 **advisory 日志诊断** (`benefit_society.py:452-486` 纯 warning, 不剔锚不拦轴; F03); direction 轴低频反义词
> (抑低/压降) margin 偏小时人工读 warning 校准; 若要 gate 语义须 §8 落地为 direction 轴增 fail→drop 工作项。
> ⚠ **stage 72/73 留痕**: 原拟 stage 73 HTMT 作判别门, 但 (a) 用户决定各主题独立不做轴间比较; (b) stage 73 现码 `:103-109`
> 硬编码 3 indicator 仅服务创新/清晰度族, stage 72 (`construct_orthogonality.py`) 产 NMI 对连续投影范畴不适用 → 二者**不再作本计划判别门**。

<!-- §3 轴间判别硬门 (门 A/B/单因子/三档/批量裁决/存活情景) 已按用户独立性决策整体退役 -->

---


## 4. 财务列接入清单 (步骤 0, 阻断性)

### 4.1 现状 + 接入门
`config/银行面板2007-2025年.xlsx` 仅 4 列名册, 财务列全哨兵; 接入门 `run_production_regen.py:30`
`_FINANCIAL_OUTCOME_COLS` (`:64-71` 缺列报错→SOP 步骤0; ⚠ **不含 level `cost_income_ratio`** — #5 用
`cost_income_ratio_change_3yr` 避盲点)。「有财务数据」≠「已 merge」, 步骤 0 须确认真实列落盘。

### 4.2 各轴 outcome 数据需求
| 数据维度 | 轴 (outcome) |
|---|---|
| 纯会计 (利润表+资产负债表, 直接 merge) | 经营效率(成本侧 CIR_change_3yr / 利润侧 PPOP-资产 会计代理)·资金成本(funding_cost)·拨备(拨备覆盖率变动/拨贷比 力度子维; DELR 时点子维属生成残差见估计步骤行)·多元化(非息占比/revenue_hhi)·信贷决策(贷款增速)·社会效益(普惠 inclusive_loan_growth / 涉农·小微贷款占比) |
| +监管资本/RWA | 风险承担(Z-score/RWA)·资本缓冲(capital_buffer) |
| +表外明细 | 流动性创造(cat-fat)·流动性囤积(LH 三分量) |
| +市值 (仅上市子样本) | 特许权价值 对照(Tobin_q/market-to-book, Keeley 原版, 仅验证 Lerner 代理有效性, 非独立 outcome) |
| +投入/产出价格 + 估计步骤 (F04: 非纯 merge) | **拨备(DELR 残差: LLP ~ ΔNPL+L.NPL+贷款增速+盈余前指标 基本面回归取残差, 生成-LHS 非纯 merge)**·经营效率(SFA cost frontier + profit frontier, 与会计 CIR/PPOP 互为稳健)·**特许权价值(Lerner: translog 成本函数估 MC; 投入价格=会计比率 (利息支出/存款·人力费用/资产等) → 不需股价, 全样本含非上市可算, 但属估计步骤非纯 0a merge)** |
| +贷款期限分项 | 信贷期限(久期/中长期占比) |
| v34 已登记 | `capital_buffer`(v34:156 第11篇 sec)/`liquidity_hoarding_share`(v34:155 第10篇 mech)/`liquidity_creation`(v34:158 benefit_society exploratory)/`inclusive_loan_growth`(v34:159) |

### 4.3 接入分两级 + 关键守卫 (F10/F11)
现 `_FINANCIAL_OUTCOME_COLS` 仅 7 列 (roa/funding_cost/cost_income_ratio_change_3yr/citation_weighted_patent/
m_and_a_fintech/tobin_q/z_score), 远不覆盖 12 轴 outcome 全集 → **步骤 0 拆两级**:
- **Phase 0a (纯会计 merge, 较快)**: 利润表+资产负债表 → 解锁 拨备(拨备覆盖率变动/拨贷比 力度子维, 随会计 merge 入 `_FINANCIAL_OUTCOME_COLS`; DELR 时点子维属 0b 生成残差)/多元化/信贷决策/资金成本/经营效率(CIR+PPOP 代理)/社会效益(普惠 `inclusive_loan_growth` + 涉农/小微贷款占比) 等会计型轴。
- **Phase 0b (外部数据/估计步骤, 重型子项目)**: 监管资本/RWA + 表外明细(cat-fat) + 市值 + 贷款期限 + 投入价格/数量 +
  生成残差/估计工程 (DELR 残差 / 流动性创造 Berger-Bouwman 三步分类 cat-fat; **特许权 Lerner 须 translog 成本函数估 MC**;
  经营效率 SFA cost+profit frontier) → 风险承担/资本缓冲/流动性创造/特许权/经营效率(SFA口径)/拨备(DELR 时点子维) 依赖此级 (远非"纯会计列 merge")。
- ⚠ **roe 未登记 (F11 订正)**: 盈利/绩效轴已剔除 → `roe` **既不在 `_FINANCIAL_OUTCOME_COLS` 也不在 derived_columns**
  (config/ 零命中) 且**无现役轴消费**, 仅作 horse-race 探索备列, **非任何轴 confirmatory primary** (不必强制补登记)。
  `nim` 现挂**特许权价值轴的稳健代理** (§5.11: Lerner 的可观测对应, NIM 由市场势力驱动 Ho-Saunders) → 须随 Lerner 接入时
  一并登记 nim。注: 现 `_FINANCIAL_OUTCOME_COLS` 7 列无 roe/nim, 接入 nim 时加入即可。

---

## 5. 锚句库 (12 套专属正/负极锚句; v3 核心交付物)

> **JLM 2026 RFS 样式 (2026-06-22 二/三轮工作流, 形式统一; 120 对 difflib 机械校验 0 违规)**: 每套 **10 对**, 严格
> **single-word-change** (正/负极仅替换一个核心词, difflib 单 replace span 逐对验, 正负极**等长**, 其余字 100% 相同),
> 句长 **15–18 字**, 一般现在时, 平实陈述; 主语标准化为固定小集合 **{金融科技应用 / 数字金融服务 / 银行数字化转型 / 金融科技}**,
> 句式 = `[金科主语]+[核心词]+[银行+维度宾语]` (对齐 `config/jlm2026_chinese_anchors.yaml` 官方 5 对中文锚: 金融服务有益↔损害
> 社会 / 金融对世界产生积极↔消极影响 等)。
> **极性词 = 轴类型**: valence 轴 (经营效率/特许权价值/社会效益) 用好坏词 (提升↔拉低 / 改善↔恶化 / 巩固↔削弱 / 有益↔损害); direction
> 轴 (其余 9) 用方向中性词 (加大↔抑制 / 拉长↔缩短 / 囤积↔释放 / 放宽↔收紧), **零 valence** (codebook 须声明该轴无好坏)。
> 落地 = 各套建一个 benefit_society-式投影模块 (POSITIVE/NEGATIVE_ANCHORS), 产 `<前缀>_{full/ctx/ss}(_t2v)` 列。
> **各主题独立, 不做轴间判别** (§3): 各套仅过轴内 margin/符号自检, 不与其它套/benefit_mean 互比 HTMT。

### 5.1 风险承担 [direction] — `加大↔抑制`
1. 金融科技应用**加大**银行风险承担水平 ↔ **抑制** | 2. 数字金融服务**推升**银行信贷扩张力度 ↔ **压低**
3. 银行数字化转型**放大**银行风险敞口 ↔ **压缩** | 4. 金融科技应用**放大**银行杠杆久期错配 ↔ **收窄**
5. 数字金融服务**增加**银行长尾客群授信 ↔ **减少** | 6. 金融科技**抬升**银行行业资产集中度 ↔ **压低**
7. 金融科技应用**加重**银行同业资金依赖 ↔ **减轻** | 8. 数字金融服务**扩大**银行交易性业务规模 ↔ **收缩**
9. 银行数字化转型**加大**风险加权资产密度 ↔ **压降** | 10. 金融科技**推升**银行批发性融资敞口规模 ↔ **收敛**
> ⚠ **direction 零-valence**: 全 10 对方向中性词 (加大↔抑制 等), 不含好坏价值词; codebook 须声明本轴无 valence。低频反义词 margin 上线实测。

### 5.2 资金成本 [direction] — `压低↔抬高`
1. 金融科技应用**压低**银行整体资金成本水平 ↔ **抬高** | 2. 银行数字化转型**压降**银行存款付息成本 ↔ **抬高**
3. 数字金融服务**收窄**银行存贷利差成本 ↔ **扩大** | 4. 金融科技应用**压缩**银行批发融资利率 ↔ **抬高**
5. 数字金融服务**压低**银行同业拆借资金价格 ↔ **抬升** | 6. 银行数字化转型**减轻**银行计息负债利息 ↔ **加重**
7. 数字金融服务**下调**银行储蓄存款定价 ↔ **上调** | 8. 金融科技应用**压低**银行债务融资利率 ↔ **推高**
9. 数字金融服务**压低**银行客户资金获取成本 ↔ **抬高** | 10. 金融科技应用**平抑**银行存款利率竞争强度 ↔ **推升**

### 5.3 流动性创造 [direction] — Berger-Bouwman cat-fat
1. 金融科技应用**扩大**银行流动性创造规模 ↔ **收缩** | 2. 银行数字化转型**增强**银行存贷期限转换 ↔ **削弱**
3. 数字金融服务**扩张**银行信贷中介规模 ↔ **压缩** | 4. 金融科技应用**延展**银行表外授信供给 ↔ **收紧**
5. 数字金融服务**扩张**银行实体经济融资规模 ↔ **收缩** | 6. 银行数字化转型**抬升**银行期限转换强度 ↔ **压低**
7. 金融科技应用**拓宽**银行小微流动性供给 ↔ **收窄** | 8. 数字金融服务**延长**银行存贷期限错配 ↔ **缩短**
9. 金融科技应用**增加**银行表外流动性承诺 ↔ **削减** | 10. 数字金融服务**扩展**银行流动性中介职能 ↔ **收缩**

### 5.4 流动性囤积 [direction] — `囤积↔释放`
1. 金融科技推动银行**囤积**高流动性资产 ↔ **释放** | 2. 银行数字化转型促银行**收缩**信贷投放 ↔ **扩张**
3. 数字金融服务促银行**累积**超额准备金 ↔ **动用** | 4. 金融科技应用促银行**留存**闲置资金 ↔ **投放**
5. 金融科技推动银行**抬高**现金持有比例 ↔ **压低** | 6. 银行数字化转型促银行**增持**短债头寸 ↔ **减持**
7. 数字金融服务促银行**积聚**预防性缓冲 ↔ **消耗** | 8. 金融科技应用促银行**收紧**流动性承诺 ↔ **放开**
9. 金融科技推动银行**沉淀**同业拆借资金 ↔ **拆出** | 10. 银行数字化转型促银行**储备**变现资产 ↔ **处置**

### 5.5 经营效率 [valence] — 含成本效率 + 利润效率 (Berger-Mester 1997; 用户令合为单一经营效率主题)
1. 金融科技应用**提升**银行整体经营效率 ↔ **拉低** | 2. 银行数字化转型**改善**银行单位运营成本 ↔ **恶化**
3. 数字金融服务**优化**银行成本收入比率 ↔ **恶化** | 4. 数字金融服务**提高**银行利润转化效率 ↔ **降低**
5. 金融科技应用拉**近**银行成本利润前沿 ↔ 拉**远** | 6. 银行数字化转型**压低**银行后台费用开支 ↔ **抬高**
7. 金融科技应用**压缩**银行人力成本占比 ↔ **抬高** | 8. 数字金融服务**强**化银行利润获取效率 ↔ **弱**化
9. 金融科技应用**增强**银行要素配置效能 ↔ **削减** | 10. 银行数字化转型**缩小**银行效率前沿差距 ↔ **拉大**
> **构念 = 经营效率, 含两维** (Berger-Mester 1997 JBF cost & (standard/alternative) profit efficiency): **成本效率** (锚句
> 2/3/6/7: 单位成本/成本收入比/费用开支/人力成本占比) + **利润效率** (锚句 4/8: 利润转化/利润获取效率) + 整体/双前沿 (1/5/9/10)。
> **不分两轴**——作同一"经营效率"主题, outcome 取**成本效率** (`cost_income_ratio_change_3yr` 主 / SFA cost efficiency) +
> **利润效率** (SFA profit efficiency / `PPOP`-资产 代理) 两个效率维度: 单一 confirmatory primary 须二选一 (建议 CIR), 余作
> secondary 受单篇内 FWER; SFA 口径作 outcome 时触发生成-LHS bootstrap (§7), CIR/PPOP 纯观测不触发。

### 5.6 贷款损失准备计提 [direction] — 计提时点/力度/方式/类别 (纯方向中性, 逐对等长)
1. 金融科技应用**前**移银行贷款损失计提 ↔ **后**移 | 2. 金融科技应用**组合**计提银行信用损失 ↔ **单笔**
3. 数字金融服务**加大**银行减值准备计提 ↔ **压减** | 4. 银行数字化转型**多**提银行贷款损失准备 ↔ **少**提
5. 金融科技应用**逐期**计提银行减值准备 ↔ **集中** | 6. 金融科技应用**提早**确认银行预期信用损失 ↔ **延后**
7. 数字金融服务**上调**银行拨备计提力度 ↔ **下调** | 8. 银行数字化转型**增强**银行减值计提力度 ↔ **减弱**
9. 金融科技应用**动态**计提银行贷款拨备 ↔ **静态** | 10. 数字金融服务计提银行**一般**损失准备 ↔ **专项**
> ⚠ **direction 零-valence**: 4 子维度全方向中性 —— 时点(前移↔后移/提早↔延后) · 力度(加大↔压减/多↔少/上调↔下调/增强↔减弱) · 方式(组合↔单笔/逐期↔集中/动态↔静态) · 类别(一般↔专项), 正负极逐对等长, 不含价值词。
> 计提力度↑的福利符号两面性 (Bushman-Williams 2012 JAE) 交由 outcome/DELR 残差解释, 不在锚轴预设。
> ⚠ **复合构念 + 多 outcome 分维 (F-new)**: 本轴 = 拨备行为综合方向复合构念 (时点+力度+方式+类别 4 子维正交, 投影向量为各子维均值)。
> 配对 primary outcome **DELR (Beatty-Liao 2014 延迟确认) 仅映射时点子维**; codebook/§7 须声明: treatment→DELR 因果**限定时点子维** +
> 报子维 heterogeneity; 力度子维另配 secondary outcome (拨备覆盖率变动/拨贷比); 方式/类别子维为描述性 treatment-side。**不以单一 DELR 主张全复合构念因果**。
> ⚠ **正交→margin 风险 (落地实测裁决)**: 4 子维近正交 → 单一平均方向向量**轴内 margin 预期偏低**, §3 逐对 margin/符号自检须重点监控本轴; 若多对 margin<0.02, 上线时考虑**时点子维专属窄锚单独投影** + 力度/方式/类别子维另建独立投影列 (拆分本复合轴)。

### 5.7 资本缓冲行为 [direction] — `增厚↔削薄`
1. 金融科技应用**增厚**银行超额资本缓冲 ↔ **削薄** | 2. 银行数字化转型**抬升**银行资本充足率 ↔ **压低**
3. 数字金融服务**加厚**银行核心资本垫层 ↔ **削薄** | 4. 金融科技应用**增持**银行监管资本盈余 ↔ **减持**
5. 金融科技应用**扩大**银行资本安全边际 ↔ **收窄** | 6. 银行数字化转型**累积**银行资本储备规模 ↔ **消耗**
7. 数字金融服务**抬升**银行资本留存比例 ↔ **压低** | 8. 金融科技应用**增配**银行超额资本头寸 ↔ **减配**
9. 金融科技应用**抬高**银行资本缓冲水平 ↔ **压低** | 10. 银行数字化转型**加快**银行内源资本补充 ↔ **放缓**

### 5.8 信贷期限结构 [direction] — `拉长↔缩短`
1. 金融科技应用**拉长**银行信贷期限结构 ↔ **缩短** | 2. 银行数字化转型**延长**银行贷款平均久期 ↔ **缩短**
3. 数字金融服务**增配**银行中长期贷款规模 ↔ **削减** | 4. 金融科技应用**抬升**银行信贷期限重心 ↔ **下移**
5. 金融科技应用**推升**银行贷款加权久期 ↔ **压低** | 6. 银行数字化转型**延展**银行贷款到期期限 ↔ **缩短**
7. 数字金融服务**拉大**银行长短贷款期限差 ↔ **收窄** | 8. 金融科技应用**拓宽**银行长期信贷占比 ↔ **压缩**
9. 金融科技应用**增持**银行长久期信贷资产 ↔ **减持** | 10. 银行数字化转型**增发**银行长周期信贷 ↔ **压减**

### 5.9 多元化经营 [direction] — `拓展↔收缩` (valence-neutral)
1. 金融科技应用推动银行**拓展**多元化经营 ↔ **收缩** | 2. 数字金融服务推动银行**扩张**非息收入格局 ↔ **收缩**
3. 数字金融服务推动银行**分散**主营业务结构 ↔ **集中** | 4. 金融科技应用引导银行**拓宽**跨业经营边界 ↔ **收窄**
5. 金融科技应用推动银行**扩张**多元收入来源 ↔ **压缩** | 6. 金融科技应用引导银行**进入**多元业务板块 ↔ **退出**
7. 数字金融服务推动银行**延伸**跨业务线经营 ↔ **回撤** | 8. 金融科技应用推动银行**增设**异地经营网点 ↔ **撤并**
9. 金融科技应用推动银行**延展**综合金融服务 ↔ **收拢** | 10. 数字金融服务推动银行**扩展**中间业务收入 ↔ **收缩**
> ⚠ **direction 零-valence**: 句式 [金科主语]+推动/引导+银行+[方向词]+[宾语], 全 10 对方向中性词 (拓展↔收缩/扩张↔收缩/分散↔集中/拓宽↔收窄/扩张↔压缩/进入↔退出/延伸↔回撤/增设↔撤并/延展↔收拢/扩展↔收缩), 正负极逐对等长, 不含好坏 (#8 异地网点=地域多元化, 区别于 #2/#5 收入多元化)。

### 5.10 信贷决策 [direction] — `放宽↔收紧`
1. 金融科技应用**放宽**银行信贷审批标准 ↔ **收紧** | 2. 银行数字化转型**扩大**银行贷款准入范围 ↔ **收窄**
3. 数字金融服务**扩大**银行小微企业授信 ↔ **压缩** | 4. 金融科技应用**放松**银行信贷投放条件 ↔ **收紧**
5. 银行数字化转型**加快**银行信贷审批速度 ↔ **放缓** | 6. 数字金融服务**上调**银行单户授信上限 ↔ **下调**
7. 金融科技应用**调高**银行信贷风险容忍度 ↔ **调低** | 8. 数字金融服务**增加**银行长尾客群信贷 ↔ **削减**
9. 金融科技应用**放宽**银行抵押担保要求 ↔ **收紧** | 10. 数字金融服务**下调**银行信贷审批利率 ↔ **上调**
> ⚠ **direction 零-valence + 极性一致**: 全 10 对核心词 2字, 正负极逐对严格单词替换且等长 (放宽/收紧·扩大/收窄·扩大/压缩·放松/收紧·加快/放缓·上调/下调·调高/调低·增加/削减·放宽/收紧·下调/上调), **正极同向"更宽松/更便利信贷"** (9 对=放松准入/审批/授信/风险容忍 + 第 5 对=审批提速(时效维, 同向更顺畅信贷)), 负极统一"收紧/放缓"。与轴内方向词同为零-valence。语义守恒 = 信贷决策的松紧/准入/风险偏好/时效方向, 福利符号两面交由 outcome 解释。

### 5.11 特许权价值 [valence] — Keeley franchise (全样本统一 Lerner 指数, 覆盖中国商业银行业**所有银行**)
1. 金融科技应用**巩固**银行的特许权价值 ↔ **削弱** | 2. 银行数字化转型**加宽**银行业务护城河 ↔ **收窄**
3. 数字金融服务**抬高**银行业进入壁垒高度 ↔ **压低** | 4. 金融科技应用**增强**银行客户黏性水平 ↔ **削弱**
5. 金融科技应用**扩大**银行市场势力定价权 ↔ **缩小** | 6. 银行数字化转型**巩固**银行特许经营租金 ↔ **动摇**
7. 数字金融服务**厚植**银行存款专营特许权 ↔ **瓦解** | 8. 金融科技应用**抬升**银行市净率估值溢价 ↔ **压低**
9. 银行数字化转型**筑牢**银行长期竞争壁垒 ↔ **瓦解** | 10. 金融科技应用**巩固**银行特许权护城河 ↔ **侵蚀**
> **outcome — 覆盖中国商业银行业全样本 (经文献核实, §9)**: 经典 charter value (Keeley 1990 = 市值账面比/Tobin Q) 需股价 →
> **仅上市行可算, 不能覆盖全样本**。但顶刊将**市场势力 = 特许权价值的来源** (Keeley 1990 → Marcus 1984 → Hellmann-Murdock-Stiglitz
> 2000), 故 **以会计型 Lerner 指数 (价格-边际成本加成, 超对数成本函数估 MC) 统一测全样本特许权价值/市场势力** —— **主 outcome =
> Lerner 指数, 对中国商业银行业【所有银行】单一口径计算** (大型国有/股份制/城商/农商/民营; 含上市与非上市), 纯会计·监管数据可算、
> 不需股价 (Berger-Klapper-Turk-Ariss 2009 JFSR / Jiménez-Lopez-Saurina 2013 J.Fin.Stab.: 市场势力是 franchise value 主要来源, Lerner 作
> franchise-value hypothesis 核心检验量/市场势力代理, 经 Keeley 机制映射, 非 Lerner≡Tobin Q 等同, F07; Turk-Ariss 2010 JBF
> 发展中国家样本; Maudos-Fernández 2004 JBF)。稳健 = NIM / 会计型超额利润现值 (Demsetz-Saidenberg-Strahan 1996 going-concern,
> 披露为代理); 市场层 HHI/Boone 仅作工具/控制非 outcome; **上市子样本另算 Tobin Q/market-to-book (Keeley 原版) 仅作 Lerner
> 代理有效性的验证, 不作上市行的独立 outcome — 保持全样本单一测度**。⚠ 论文须明示"以 Lerner 操作化全样本特许权价值"避免
> "Lerner 冒充 Tobin Q"的构念偷换批评。
> **可证伪对照判据 (上线门)**: 上市子样本上 treatment→Lerner 与 treatment→Tobin Q 须 **(a) 系数符号一致 + (b) Lerner 与
> Tobin Q 的 bank-year |corr| 超阈 (如 >0.3)** 方判 Lerner 代理有效; **若符号相反/相关弱 → 改报"市场势力"构念 (非 franchise
> value), 不冒称特许权价值**。预设发散情景处置, 避免事后合理化。

### 5.12 社会效益 (金融惠及社会) [valence] — 借鉴 JLM 2026 RFS「Does Finance Benefit Society?」社会金融情感 (firm-year 迁移)
1. 金融科技应用**有益**国家实体经济发展 ↔ **损害** | 2. 数字金融服务**造福**社会大众日常生活 ↔ **祸害**
3. 银行数字化转型对社会民生产生**积极**影响 ↔ **消极** | 4. 金融科技应用**帮助**实体经济稳健运行 ↔ **危害**
5. 数字金融服务对社会民生产生**好**作用 ↔ **坏** | 6. 银行数字化转型**惠及**社会公众金融需求 ↔ **侵害**
7. 金融科技对实体经济的社会作用是**正面**的 ↔ **负面** | 8. 数字金融服务**助力**社会实体经济繁荣 ↔ **损害**
9. 金融科技对社会公众与实体经济贡献**良好** ↔ **恶劣** | 10. 金融科技应用**改善**社会公众福利水平 ↔ **恶化**
> **构念 = JLM 社会构念** (Jha-Liu-Manela 2026 RFS «Does Finance Benefit Society?» 39(5):1227-1266; Zingales 2015 JF 70(4):1327-1363
> 同名命题; KTE 2019 geometry of culture): 媒体叙事中 银行金融科技/数字金融 是否**有益于 社会/公众/实体经济/民生/世界**。10 对**回声 JLM
> 5 极语义维度** (分配 ①3(1/2/6) ②2(5/10) ③1(9) ④2(3/7) ⑤2(4/8))。**全 valence 好坏词** (codebook 声明本轴有社会褒贬, 区别于 9 个 direction 零-valence 轴)。
> ⚠ **官方原文 vs 本轴改编 (诚实披露)**: JLM 官方 5 极逐字 (`config/jlm2026_chinese_anchors.yaml`) = 有益↔**损害** / 好↔**不好** / 很好↔**邪恶** /
> 积极↔**消极** / 帮助↔**有害** (⑤负极含逐字保留的附录笔误「金融系统有害金融」, V2.E37)。本 §5.12 **10 对负极中仅 #1(损害, 维①) 与 #3(消极, 维④)
> 与官方对应维度逐字重合**; 其余 **8 对为 valence 对仗 + single-word-change + 等长 的设计改编**: 维① #2祸害/#6侵害 (官方 损害→) · 维② #5坏/#10恶化
> (官方 不好→) · 维③ #9恶劣 (官方 邪恶→, 兼 system-level 人格→社会贡献迁移) · 维④ #7负面 (官方 消极→) · 维⑤ #4危害/#8损害 (官方 有害→)。
> **codebook 须如实披露此全部 8 处改编** (非仅 ②③⑤)。
> ⚠ **≠ benefit_society 模块 (构念物理隔离)**: benefit_society (`pipeline/features/benefit_society.py:158-209`) 测银行**自身经营效益**
> (business benefit, 宾语=经营效率/盈利/风控/合规 等 firm 内部指标); 本轴测对**社会的 benefit** (societal benefit, 本套 10 对宾语 **0/10**
> 命中银行内部指标, 全落 社会/民生/实体/公众/世界 — 与 benefit_society 主模块 (business-object 锚) 靠**宾语层**分离)。共方法 (KTE 双极投影) 异构念。
> ⚠ **与 yaml 官方 5 锚关系 (P3 避误读)**: yaml 官方 5 锚**多为 societal-object** (社会/世界/经济; 官方 #3 good_corrupt 宾语为"财务专业人员"人格层, 见维③迁移), 故与 social_narr 10 锚在**锚-宾语层有重叠**;
> 二者分离**不靠锚宾语, 而靠下述「职能划界」的 3 个代码隔离器** (outcome / 落盘 / 角色)。前文「0 锚句重复」仅指 **verbatim 字符串非重叠** (无逐字相同句), **非构念分离论证**。
> outcome = 普惠金融 `inclusive_loan_growth` (银行对社会真实贡献, v34:159; §10 披露与 benefit_society exploratory 的共享 outcome)。
> ⚠ **职能划界 (防 salami)**: `pipeline/features/benefit_society_alt_anchor.py` 已用 **yaml 官方 5 锚**作 benefit_society 的"替代锚点族"
> 稳健臂 (`benefit_jlm_zh_*`, 检验其 **business-benefit** 主结论换广义金融锚后是否存活, outcome 仍=经营量)。本 `social_narr` (新 10 锚,
> outcome=inclusive_loan_growth) **职能不同**: 前者=business 构念的锚-稳健性, 后者=独立 societal-benefit 测度。benefit_society 的 yaml 锚臂
> 保留其 business 稳健职能, 但**不得**再被解读为"社会效益测度"(该职能由 social_narr 独占)。
> ⚠ **唯一同母本对的判别例外 (F-new; 不违独立性决策)**: `social_narr`↔`benefit_mean` 是全文档**唯一**同撞 JLM/Zingales 母本 + KTE 方法 +
> 主 outcome (inclusive_loan_growth) 的轴对。仅对此**单对**开 codebook **描述性披露** (advisory 非 gate, 镜像 §5.11 Lerner↔Tobin Q 判据):
> 报 `social_narr` vs `benefit_mean` 的 bank-year |corr|; 预设处置 **|corr|>0.7 → 披露高相关、social_narr 作 benefit_society 的 societal-side
> 扩展而非独立构念主张**。**不恢复全局 HTMT 硬门** (仅此一对, 尊重各主题独立)。
> ⚠ **粒度迁移声明** (镜像 F13): JLM 实证对象 = country-year 广义金融社会情感, 本轴迁至 firm-year 银行金科媒体叙事; 借鉴 = **JLM 社会构念 +
> KTE 双极投影方法 + 5 极语义**, **非** JLM 直接背书 firm-level (须以 benefit_society firm-year 先例锚定)。
> ⚠ **反向因果 (社会轴最强)**: outcome `inclusive_loan_growth` 即银行真实普惠行为, 「真实普惠投放→正面社会叙事」反向通道最强 → §7 排他性加社会轴专款。

---

## 6. 同群效应 (已按用户 2026-06-22 决策整体删除)
> 原「同群效应 — 网络空间溢出机制 (非锚轴)」整体删除: 含 (a) 空间滞后 `W·proj_k` 作机制变量检验同业主题叙事对本行
> outcome 的溢出, (b) 同组 leave-one-out 同业均值 `leave_one_out_peer_<topic>_iv` 作 IV。**各轴识别改用 §7 的广义
> zone-LOO 地理暴露为主 + 广义 Bartik (须先构造文章级 shift, 见 §7) 作 over-id 第二工具**, 不再依赖同业 peer 叙事溢出 (zone-LOO 是地理空间暴露非同群); 相关 Manski 反射 / Leary-Roberts /
> Bramoullé / GLMY path-homology 评估随之退役 (§9 引用同步删)。
> ⚠ **识别强度后果 (上线门, 诚实披露)**: 退役同业 peer-LOO 后, **zone-LOO 地理暴露**作可立即落地主工具, 但其对内生「媒体叙事投影」
> treatment 的 first-stage 相关性**不可假定与原 peer-LOO 等强**; 须逐轴实测 **KP rk F** 满足 Stock-Yogo 临界 (GPSS rho 仅在广义 Bartik 文章级 shift 构造后、作 shift-share over-id 工具时适用, 见 §7)。广义 Bartik 须先完成
> 文章级 shift 工程方可作 over-id 第二工具; **未完成前各轴 just-identified (仅 zone-LOO, 无 Hansen J, 见 §7 设计)**。T=19 生产盘逐轴裁决, 弱则降稳健性。

---

## 7. 研究设计与推断协议 (每轴)
- **设计**: treatment = 本轴投影 `<前缀>_{full/ctx/ss}` → outcome = 真实财务量 → IV = **zone-LOO 地理暴露**
  主 (`iv_extensions.py::compute_peer_loo_iv` 取 `group_col=bank_zone`: 本行所在地理区 leave-one-out 投影均值作**空间暴露**工具,
  **非同业 peer 叙事溢出** = 与已删同群效应口径不同) + **广义 Bartik (shift-share) 作 over-id 第二工具 (须先构造文章级投影 shift, 见下 ⚠)**。
  bank+year 双向 FE + 规模/资本/前期 outcome 控制。
  > ⚠ **Bartik 可操作化前置 (P1-b 订正, 代码坐实)**: `compute_bartik_shift_iv` 须**文章级 shift 列** (`shift_col_by_track→df_exploded[src]`),
  > 而各新轴 treatment 是 bank-year 聚合双极投影; 既有同类投影轴 `benefit_mean` 的 IV (`iv_extensions.py:593-624`) 亦**仅用 LOO (peer/zone)、
  > 0 次 Bartik**。故 Bartik **非"复用现有引擎即得各轴主工具"**: §8 Phase 1 须**新增工程** = 构造文章级双极投影 shift `a_j=cos(s_j,p)` (不聚合到
  > bank-year) 喂 `shift_col_by_track`。**Bartik 未构造前各轴单轨内仅 zone-LOO 主工具 → just-identified, 无 Bartik×zone-LOO over-id、
  > Hansen J 不可计算** (须如实披露, 不可声称已 over-identified)。
- **排他性 outcome-specific**: 每轴枚举该 outcome 的潜在直接渠道 (审计师跨行学习/监管同侪窗口指导/共同流动性
  冲击), 论证被 FE+控制吸收; 最脆弱者优先 zone-LOO 主工具 + (Bartik 文章级 shift 构造后) Bartik×zone-LOO Hansen J + KP rk F + GPSS rho; Bartik 未构造则仅 KP rk F (just-identified)。
  > ⚠ **社会效益轴 (#12 social_narr) 专属反向因果条款 (F-new, 12 轴中反向最强)**: 其 outcome `inclusive_loan_growth` 本身即银行
  > **真实普惠行为**, 存在「真实普惠投放 → 正面社会叙事」反向通道。须额外: (a) 主工具 **zone-LOO 须满足 LOO 排他** (本行 outcome 不进 IV) +
  > Bartik (若构造) shift 取**纯外生金科冲击** (与本行后续普惠决策无关); (b) 控**前期 `inclusive_loan_growth` 滞后项** + vintage≤t 守卫;
  > (c) 论文报 **reverse-Granger / lead-outcome 安慰剂**。衔接 §7 "最脆弱者优先 zone-LOO 主工具 (+ Bartik 文章级 shift 构造后作 over-id)", 无需新增阶段。
- **生成-LHS outcome (DELR/Lerner/SFA 效率; F03 补全)**: 凡 outcome 是**一阶段估计量** (DELR 残差 [拨备#6 primary, **treatment→DELR 因果限定时点子维, 报子维 heterogeneity, 见 §5.6 复合构念**] /
  **特许权价值 Lerner — MC 由 translog 成本函数估** / **经营效率的 SFA cost & profit 复合残差 E[u|ε]**), 作 LHS 时第二阶段 SE 须
  **block-bootstrap by bank 覆盖【一阶段估计 + 二阶段回归】整链** (非 Pagan; SFA 须 Simar-Wilson 式 bootstrap)。⚠ **纯观测量不触发**: 经营效率会计
  outcome `cost_income_ratio_change_3yr` / `PPOP/资产`、特许权对照 `Tobin_q` 是观测值, 走常规推断。
- **GMM (资本缓冲)**: system-GMM 部分调整**不 clone 静态 2SLS 骨架**, 单列工程路径; 引 Nickell 1981; 内部滞后矩工具 (本身即 over-id, diff-in-Hansen 不依赖 Bartik) +
  zone-LOO 外部工具 (+ 广义 Bartik 须先构造文章级 shift, 同 §7/§8 Phase 1b) 时报 difference-in-Hansen + collapse + AR(2) (Roodman 2009)。
- **推断**: 单一 confirmatory 主假设 + PAP (每轴锁定主 outcome); bank + bank×year 双向聚类; small-G wild cluster
  bootstrap; **单篇内** FWER (Romano-Wolf, applies_to exploratory; ⚠ 跨独立论文 family-wise 不成立)。
- **监管断点 (拨备/资本/风险) — F05 订正**: 若引断点须建**真 event-study** (相对事件时间 dummies + pre-trend
  联合检验 + 安慰剂断点), **不可**声称复用 `33_tableA9`(lead-placebo)/`34_tableA11`(时代子样本); 否则按 benefit_society
  `event_studies:[]` 立场声明纯横截面。⚠ **交错变异区分**: 仅**分批/分地区试点** (DCEP 数字人民币分批、沙盒分批
  准入) 有交错 timing → 方可用 **Sun-Abraham/Callaway-Sant'Anna**; **同步全国断点** (`depins_post` 存款保险 2015-05-01
  全国同步、资管新规) **无 never-treated 对照 → staggered-DiD 退化**, 只能退 **pre/post DiD + 平行趋势图 + 安慰剂**,
  不可冒称 staggered-DiD。⚠ **T=2 盘面断点设计一律 N/A, 仅 T=19 生产盘可跑**。
- **confirmatory primary 唯一钉死 (F04/F05; 单篇内 p-hacking 控制, 现役轴举例)**: 多 outcome 轴须**唯一锁一列**作 confirmatory
  primary 写入各 `paper_spec.yaml` 的 `confirmatory_family`, 余列降 secondary 受单篇内 FWER, 防事后挑显著 (p-hacking)。
  现役多-outcome 轴: **风险承担(#1)** 从 Z-score/RWA密度/NPL **锁 Z-score** (CAR 变体); **特许权价值(#11)** 从 Lerner/Tobin_q
  **锁 Lerner** (全样本; Tobin_q 仅上市子样本验证非 primary); **经营效率(#5)** 含**成本效率 + 利润效率两维**, 须从
  `cost_income_ratio_change_3yr` / SFA cost / SFA profit / `PPOP` 中**锁一个 primary** (建议 CIR), 余作 secondary 受单篇内 FWER; **拨备(#6)** 锁 **DELR(时点子维) primary**, 拨备覆盖率变动/拨贷比(力度子维) secondary 受单篇内 FWER (见 §5.6 复合构念分维)。
> ⚠ **轴间 outcome 共线门已删 (用户独立性决策 2026-06-22)**: 各主题独立, **不再**要求 12 轴 primary outcome 的 N×N 相关矩阵
> 或任何跨轴护栏。上述"唯一锁一列"纯为**单篇内**多 outcome 的 p-hacking 控制 (含经营效率轴内成本/利润两维择一作
> primary), 属轴内事务, 与轴间判别/比较无关。
- **z_score CAR-变体披露 (F08)**: 风险承担轴若复用项目现有 `z_score` 列, 须沿用 disagreement/clarity 的 **CAR-based
  Z-score 变体**披露 (资本项=Basel CAR/RWA 加权, **非** Laeven-Levine 2009 JFE 原版的账面 equity/TA), 不可误称 L-L 原版;
  或 Phase 0b 构造 L-L 原版 Z-score 时显式区分。
- **ss 轨退化 + 双嵌入投影稳定性上线门 (F12, $0 golden-safe)**: (a) 每轴报 `ss_is_fallback` 率 + `_ss` vs `_ctx`
  投影相关 — `content_ss` 窄窗 (同句含 银行∧金科) 实测主题漂移 65.76%, 测具体银行行为的 direction 轴 (信贷期限/拨备
  时点/资本缓冲) 主题命中可能更低 → 大量回退全文; 命中过低则披露 ss 仅作稳健性而非平价主轨。(b) 报每轴 canonical
  投影 vs `_t2v` 投影的 bank-year 相关 (双极投影对嵌入几何各向异性敏感, skew≈−1.23), 主结论须双模型方向一致方采纳。

---

## 8. 落地路线图
- **Phase 0 — 财务列接入 (阻断, F10 拆两级)**: **0a** 纯会计列 merge (利润表+资产负债表, 补 `cost_income_ratio` +
  `PPOP/资产` 进 `_FINANCIAL_OUTCOME_COLS`; 解锁会计型轴; `nim` 随 Lerner 接入时一并补, `roe` 仅 horse-race 备列) → **0b**
  外部数据/估计 (监管资本/RWA + 表外 cat-fat + 市值 + 贷款期限 + 投入价格/数量) + 生成残差/估计工程 (DELR / Lerner-translog /
  SFA 利润·成本效率)。v34 对账; `roa` 小写。
- **Phase 1 — 锚轴投影列落盘 (F07 订正阶段归属)**: 12 套锚句各建 benefit_society-式模块 (POSITIVE/NEGATIVE_ANCHORS,
  落 `pipeline/features/`), 在 **runner step 7h** (stage 45 panel 构造内, 非 stage 15) 自行调 `embedding_engine` 嵌入
  锚句+文章 (复用现有嵌入缓存; **stage 21 LLM 投票=$0** 不触发) → inline 注入 stage 40 panel 产 `<前缀>_{full/ctx/ss}(_t2v)` 列。
  先落 **3 轴** (流动性囤积/拨备/信贷期限) 验管线 (T=2 即可验 treatment 端; 各轴独立, 任选即可)。
  > ⚠ **Phase 1b — Bartik over-id 工程 (P1-b, 可选/IV 增强)**: 若需广义 Bartik 作 over-id 第二工具 (§7), 须额外构造**文章级双极投影 shift**
  > `a_j=cos(s_j,p)` (各轴不聚合到 bank-year 的文章级投影列) 喂 `iv_extensions.py::compute_bartik_shift_iv` 的 `shift_col_by_track`;
  > **非复用现有引擎** (既有 `benefit_mean` 仅用 LOO, 0 Bartik)。**不做此工程则各轴仅 zone-LOO just-identified** (无 Hansen J), 仍可识别但无 over-id 检验。
- **Phase 2 — 各轴锚句轴内自检 (advisory, 非阻断)**: 全 12 轴逐对 margin/符号自检 (正极投正/负极投负, 见 §3) 校验
  方向向量纯净; **不做轴间 HTMT/判别** (各主题独立, 用户 2026-06-22 决策)。direction 轴低频反义词 (抑低/压降) margin 偏小时人工读 warning。
- **Phase 3 — T=19 生产重生**: 财务 outcome 接入 + 锚轴列落盘 → 重跑 stage 15/45/46 + golden 受控重生
  (`PYTHONHASHSEED=0` + 线程钉死 1, 排 BLAS-FP 网络中心度列)。
- **Phase 4 — 独立论文** (每轴一篇): clone benefit_society 三件套, 换 treatment 列 (本轴投影) + outcome + §7 推断协议;
  非静态-2SLS 题 (资本缓冲 GMM / DELR 残差) 分流单列工程路径。可优先落 3 轴 → 监管/表外/市值数据到位后扩展其余。
  IV 走 §7 的 zone-LOO 地理暴露主工具 (+ Bartik 文章级 shift 构造后作 over-id; 同群效应已删, 无同业 peer-LOO 叠加)。

---

## 9. 引用
- **Jha-Liu-Manela 2026 RFS 39(5):1227-1266** (DOI 10.1093/rfs/hhaf012, 已见刊, 投影法 §1.3.2 Table 2); 勿判编造。
  ⚠ **粒度迁移声明 (F13, 镜像 Berger-Kim-Ma 非 drop-in)**: JLM 实证对象是 **Google Books Ngram 跨 8 国 (1870-2009)
  的 country-year 社会层面广义金融情感**, **非** firm-level/bank-year 媒体文章投影。本计划借用其 Kozlowski-Taddy-Evans
  双极投影**方法**迁移到 bank-year 金科媒体文章, 属 construct/粒度迁移 (与 benefit_society 同), 论文方法部分须明示,
  并以 benefit_society (firm-year 金科) 为项目内先例锚定, 不可暗示 JLM 直接背书 firm-year 媒体叙事投影。
- **Kozlowski-Taddy-Evans 2019 ASR 84(5):905-949** (geometry of culture, 方法上游)。
- 社会效益 (JLM 社会主题轴 §5.12, 借鉴 + firm-year 迁移): **Jha-Liu-Manela 2026 RFS 39(5):1227-1266** «Does Finance Benefit
  Society?» (社会金融情感双极投影 = 本轴 **treatment 构念**直接母本) / **Zingales 2015 JF 70(4):1327-1363** (AFA Presidential
  Address «Does Finance Benefit Society?», JLM 命题同名母题)。**outcome 端**: `inclusive_loan_growth` 沿用既有 benefit_society
  模块的构造口径/provenance (§10 共享数据基础设施 v34:159, 防双口径漂移); 中国普惠金融/小微信贷实证测度顶刊锚**待独立单核后补引**
  (勿凭记忆落引); Phase 4 阻断清单登记此条为 **outcome-端 identification 前置门**。
- 风险承担: **Laeven-Levine 2009 JFE 93(2):259-275** / **Houston-Lin-Lin-Ma 2010 JFE 96(3):485-512**。
- 方法学 (全族通用; F08: 原挂已剔的盈利/绩效轴, 现归通用): **Tetlock 2007 JF 62(3):1139-1168** (媒体语调→真实后果范式)。
- 资金成本: **Martinez Peria-Schmukler 2001 JF 56(3):1029-1051** / **Iyer-Puri 2012 AER 102(4):1414-1445**。
- 流动性: **Berger-Bouwman 2009 RFS 22(9):3779-3837** (cat-fat) / **Berger-Guedhami-Kim-Li 2022 JFI 49:100893**
  (LH 三分量) / **Berger-Kim-Ma 2024 CAR 41(3):1513-1542** DOI 10.1111/1911-3846.12949 (10-K 自披露非媒体, 须点明非 drop-in)。
- 效率 + 生成回归量: **Berger-Mester 1997 JBF 21(7):895-947** (银行 **cost efficiency + (standard/alternative) profit efficiency**;
  支撑 §5.5 经营效率轴**含成本与利润两个效率维度**); 生成-LHS 残差 (DELR/Lerner/SFA) 作 LHS 的整链 bootstrap 参考
  **Pagan 1984 IER 25(1):221-247** (RHS) / **Murphy-Topel 1985 JBES 3(4):370-379** (两步估计量)。
- 拨备: **Beatty-Liao 2014 JAE 58(2-3):339-383** / **Bushman-Williams 2012 JAE 54(1):1-18**。
- 资本缓冲: **Jokipii-Milne 2008 JBF 32(8):1440-1451** / **Ayuso-Pérez-Saurina 2004 JFI 13(2):249-264** /
  **Nickell 1981 Econometrica 49(6):1417-1426** / **Roodman 2009** (Stata Journal 9(1):86-136 + OBES 71(1):135-158)。
- 期限: **Diamond 1991 QJE 106(3):709-737** / **Flannery 1986 JF 41(1):19-37**。
- 多元化: **Laeven-Levine 2007 JFE 85(2):331-367** / **Stiroh 2004 JMCB 36(5):853-882**。
- 信贷决策: **Lown-Morgan 2006 JMCB 38(6):1575-1597** / **Bassett-Chosak-Driscoll-Zakrajšek 2014 JME 62:23-40**。
- 特许权 (非上市行 Lerner 口径, 均 WebSearch 核实): 理论 **Keeley 1990 AER 80(5):1183-1200** / **Marcus 1984 JBF 8:557-565** /
  **Hellmann-Murdock-Stiglitz 2000 AER 90(1):147-165** (市场势力→准租→franchise value); Lerner 测度 **Maudos-Fernández de
  Guevara 2004 JBF 28(9):2259-2281** / **Turk-Ariss 2010 JBF 34(4):765-775** (发展中国家); **Lerner 作 franchise value 的市场势力代理**:
  **Berger-Klapper-Turk-Ariss 2009 JFSR 35(2):99-118** / **Jiménez-Lopez-Saurina 2013 J.Fin.Stab. 9(2):185-195** (二文将 Lerner 作
franchise-value hypothesis 核心检验量/市场势力代理, 非 Lerner≡franchise value 直接等同, F07);
  **Demsetz-Saidenberg-Strahan 1996 FRBNY EPR 2(2):1-14** (going-concern franchise value 定义, 注: Fed 政策刊非顶刊, 作并列);
  竞争度 **Boone 2008 Econ.J. 118(531):1245-1261** (作工具/控制非 outcome)。⚠ 不就具体中国 Lerner 论文落引用 (须另行单核)。
- IV/识别 (Bartik shift-share + 弱工具/FWER; 同群/peer-LOO 引用随 §6 同群效应删除): **Bartik 1991** (Who Benefits from State
  and Local Economic Development Policies?, W.E. Upjohn Institute) / **Goldsmith-Pinkham-Sorkin-Swift 2020 AER 110(8):2586-2624**
  (Bartik instruments 识别诊断, GPSS rho); **Sanderson-Windmeijer 2016 J. Econometrics 190(2):212-221** (弱工具) /
  **Romano-Wolf 2005** (FWER)。

---

## 10. 与既有 11 篇论文 outcome 重叠披露 (treatment 现天然区分)
v3 下每轴 treatment 是**专属投影** (与既有论文 treatment 不同) → outcome 重叠由 treatment 差异化解决 (镜像项目内
disagreement/clarity 共 z_score 独立两篇先例)。须披露 + 交叉引用 + 共享 outcome 数据基础设施声明:
> **穷尽性方法 (F-new, 防漏)**: 本表须对 §2/§4.2 全 12 轴的 primary + secondary + (含 DELR 时点子维) outcome **逐列 grep `papers/*/paper_spec.yaml`** 查重, 命中即列行; §0.5 机械校验加 "§10 行数 ≥ 被占用 outcome 数" 反解校验 (防后续轴增删再漏)。本轮已补 direction 轴遗漏 3 行 (拨备#6 DELR primary / 多元化#9 非息占比 / 信贷决策#10 贷款增速)。
| 本轴 outcome | 既有占用 (treatment) | 处理 |
|---|---|---|
| roa | benefit_society/brokerage/llm_peer primary | **盈利能力/经营绩效轴已剔除** (本质=benefit_society benefit_mean→roa 已做; roa 经 PAP 锁死) |
| tobin_q | strategic_diff primary / P1·llm_peer sec | 仅特许权价值轴**上市子样本对照**用 (主测度 Lerner; treatment=moat_narr ≠ strat_diff_n5) |
| Lerner 指数 (特许权价值主 outcome) | **无既有论文占用** | 特许权价值轴独立 (全样本会计型市场势力=franchise value 代理, 中国商业银行业所有银行); 见 §5.11/§9 |
| cost_income_ratio_change_3yr | substance primary (sub_frac) | 经营效率轴成本侧 (treatment=`effic_narr` ≠ sub_frac) → 独立+交叉引用 |
| 利润效率(SFA)/PPOP | **无既有论文占用** | 经营效率轴利润侧 (Berger-Mester profit efficiency, ≠ 已剔除的盈利水平 ROA/ROE) |
| funding_cost | P1 primary (llm_vote_tone) + strategic_diff sec + disagreement mech | 资金成本轴 (treatment=fundcost_narr, ≠ P1 tone) → 独立+交叉引用+共享 funding_cost outcome 披露 |
| z_score | disagreement/clarity primary (variance/clarity) | 风险承担轴 (treatment=risktaking_narr, 不同构念) → 独立+交叉引用+共享 z_score 披露 |
| capital_buffer | clarity secondary (mean_clarity) | 资本缓冲轴 (treatment=capbuf_narr) → 独立+披露 |
| liquidity_creation | benefit_society exploratory_extension (benefit_mean) | 流动性创造轴 (treatment=liqcreate_narr ≠ benefit_mean) → 独立+交叉引用+共享 outcome 数据披露 |
| inclusive_loan_growth (社会效益主 outcome) | benefit_society exploratory_extension (benefit_mean, v34:159) | 社会效益轴 #12 (treatment=`social_narr` ≠ benefit_mean; **JLM 真社会构念 ≠ benefit_society 经营效益构念**) → 独立+交叉引用+共享 outcome 数据披露 |
| liquidity_hoarding_share | disagreement secondary (variance) | 流动性囤积轴 → 独立+口径区隔披露 |
| npl_formation/rwa | disagreement/clarity confirmatory | (信贷决策/风险承担 secondary outcome) → 披露 |
| sigma_roa_5y_rolling | brokerage secondary | (风险承担 secondary) → 披露 |
| level cost_income_ratio | bank_fintech_attention(P2) secondary | 经营效率轴成本侧**避用 level**, 用 change_3yr |
| 拨备覆盖率变动/拨贷比 | **无既有论文占用** | 拨备轴 #6 力度子维 secondary outcome (DELR 时点子维=primary) → 独立+披露 |
| loan_loss_provision_discretion / DELR 残差 (拨备#6 primary 时点子维) | **bank_news_clarity confirmatory** (paper_spec L71/L79: 路线(b) BW2012 残差式 discretion 升"与 z_score 并列核心通道") | 拨备轴 #6 (treatment=`provtiming_narr` ≠ clarity `mean_clarity`, 不同构念) → 独立+交叉引用+**共享 DELR 残差构造/provenance 披露**(防双口径漂移) |
| noninterest_income_share (非息收入占比, 多元化#9 outcome) | bank_fintech_attention(P2)/locus(P4)/strategic_diff secondary | 多元化轴 #9 (treatment=`diverse_narr` ≠ 三者 treatment) → 独立+交叉引用+共享 outcome 披露 |
| loan_growth (贷款增速, 信贷决策#10 primary) | bank_fintech_tone(P1) secondary + brokerage_network secondary | 信贷决策轴 #10 (treatment=`creditstance_narr` ≠ P1 tone/brokerage 网络) → 独立+交叉引用+共享 outcome 披露 |

---

## 附录 — 核验出处
- 八轮工作流: ① feasibility / ② with-financials / ③ v1 评审 / ④ v2 评审 (19 confirmed/0 假阳) / ⑤ 锚句设计+验证
  (difflib 单词替换全过) / ⑥ 锚句按 JLM 样式润色+对抗验证 (12 主题 × 10 对, 全 pass, 形式统一) / ⑦ 删 全要素生产率 + 同群效应
  (用户 2026-06-22) → 11 轴 / 110 对, 多智能体顶刊复审 (GO_WITH_FIXES, 9 真缺陷全修) / ⑧ **增 JLM 社会主题轴 社会效益**
  (用户 2026-06-22, 7-agent 设计+对抗验证工作流, 10 对 difflib 0 违规, 回声 JLM 官方 5 极) → **12 轴 / 120 对**, 多智能体顶刊复审。
- 代码锚点 (逐字核; F14 = 全用包内路径: benefit_society→`pipeline/features/`, iv_extensions→`pipeline/panel/`,
  run_production_regen→`scripts/migrate/`):
  `pipeline/features/benefit_society.py:158-209` (10 对含金科锚句/投影机制/`anchor_pair_min_margin` 0.02/
  `anchor_sign_tolerance` 0.03); `iv_extensions.py:516-523,593-603` (三轨/跨族 over-id/广义 Bartik shift-share IV);
  `run_production_regen.py:30,64-71` (接入门); `config/pipeline_v34_rerun.yaml:154-159` (财务列登记)。
- 文献 (WebSearch): JLM 2026 RFS 39(5):1227-1266 已见刊; Pagan 1984=生成 RHS; Berger-Kim-Ma 2024 CAR 41(3):1513-1542。
