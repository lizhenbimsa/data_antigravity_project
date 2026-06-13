# 长度过滤区间的顶刊方法论辩护与披露方案

**日期**: 2026-06-13
**对象**: `config/preprocessing.yaml::title_min_length=2 / content_min_length=100 / content_max_length=10000`
**性质**: 零行为变更 — 阈值一字不动, 仅补辩护注释 + 诊断日志 + 本文档
**接线**: `pipeline/preprocess/load.py::_log_length_filter_diagnostics` (stage 00 逐文件 log-only)

---

## 1. 结论

顶刊不存在"标准长度区间"; 认可的是一套流程: **下限给测量可靠性论证, 上限给
文体噪声排除论证, data appendix 做分布披露 + 截断敏感性**。本方案把这三件事的
供数与披露义务固化进代码与配置注释。三阈值的合规性**不可一概而论**:
- **下限 100 字** — 有直接顶刊先例 (TSM 2008 词数过滤), 合规性强。
- **上限 10000 字** — 无数值长度上限的直接先例 (TSM 不设上限); 其**动机** (排除
  公司发布/公告类整版转载) 在中文新闻顶刊有文体排除先例 (You et al. 2018 RFS,
  §2.4), 但本项目以**数值阈值**操作化该动机属项目特异, 须靠披露 + 截断敏感性补强,
  **不可搭下限先例的便车**。
- **标题 ≥2 字** — 数据完整性过滤, 须由删除构成数据 (§4 标题诊断) 坐实非样本选择。

## 2. 文献锚点 (已逐字核验原文, 勿凭记忆转引)

### 2.1 下限的直接锚点 — Tetlock, Saar-Tsechansky & Macskassy (2008, *Journal of Finance*)

原文 p.9 (Columbia working-paper 版, 2026-06-13 核验):

> "we require that each story contains **at least 50 words in total**, and at
> least five words that are either 'Positive' or 'Negative,' where at least
> three of the five must be unique. We impose these three word count filters
> **to eliminate stories that contain only tables or lists** with company names
> and quantitative information, **and to limit the influence of outliers** on
> the negative words measure described below." (p.9; 句尾 "described below"
> 指向其 §II 的标准化定义, 完整引文止于此)

要点:
- 下限 = 全文 ≥50 英文词; 信息量换算 ≈ 75–100 汉字 (英→中扩张系数 ~1.5–2.0
  字/词; 50 词 × 1.5–2.0 ≈ 75–100) → 本项目 100 字同量级。
- 理由是功能性的: 语调 = 命中词/总词比值, 分母过小 → 抽样方差爆炸;
  超短文多为表格/列表残片 (本项目报纸语料同构: 行情表/中缝快讯)。
- **TSM 2008 不设长度上限**。对比值型语调离群的处理是 (a) 上述三个**词数下限**
  过滤本身 + (b) 语调按上一年均值/标准差**标准化** (原文 p.10 eq.1–2)。
  ⚠ 勿混淆: 原文 p.12 的 "winsorize ... at the 1% level" 对象是 **SUE 与
  分析师预测变量** (结果变量, 压制估计误差), 与文章长度/语调无关 — 本辩护
  不以 winsorize 作为"长文处理机制"。
- 引用: Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S. (2008). More
  than words: Quantifying language to measure firms' fundamentals.
  *The Journal of Finance*, 63(3), 1437–1467.
  https://doi.org/10.1111/j.1540-6261.2008.01362.x

### 2.2 长度归一化路线 — Loughran & McDonald (2011, *Journal of Finance*)

LM 2011 处理文档长度差异的方式是比例化 + tf-idf 加权, 同样不靠上限截断。
本项目 `tone_words` 词典轨的 valid-token 分母 (2026-06-10 修复) 已是同一路线。
引用: Loughran, T., & McDonald, B. (2011). When is a liability not a
liability? Textual analysis, dictionaries, and 10-Ks. *The Journal of
Finance*, 66(1), 35–65. https://doi.org/10.1111/j.1540-6261.2010.01625.x

### 2.3 下限的统计学表述 (论文可直接使用)

词典命中率 p、文章 n 个有效 token 时, frac 型语调的抽样标准误
≈ √(p(1−p)/n)。给定可容忍标准误反解最小 n — 把"为什么是 100 字"从
约定俗成变成测量误差量级论证。100 汉字分词后约 60–70 token, 与词典语调
测量误差可控的量级一致 (order-of-magnitude check), 为 100 字下限提供测量
误差量级的正面支撑。

⚠ 两点诚实限定 (投稿前须保留, 否则 referee 一眼看穿):
- **独立性假设**: √(p(1−p)/n) 把每个 token 视作独立 Bernoulli 命中, 但文本中
  情感词成簇、同根词重复、句内自相关 → 真实方差被设计效应 (design effect,
  deff > 1) 放大, 故该公式给出的是**乐观下界**, 实际所需 n 只多不少 (Gentzkow,
  Kelly & Taddy 2019 JEL 即强调文本计数的非独立性)。诚实标注后此论据反而更稳:
  它说明 100 字是**保守而非冒进**。用作量级直觉, 非精确反解。
- **量级而非定下界**: 此处未设定具体可容忍 SE 阈、未代入 p 经验值反解出精确 n*,
  故只主张"量级一致", 不主张"恰好踩在可测下界"。若投稿需要, 补一行示例反解
  (设 p、设 SE 阈 → 解 n*) 即可升级为定量论据。

### 2.4 中文语境锚点 — You, Zhang & Zhang (2018, *Review of Financial Studies*)

针对"中文上市公司报纸新闻"的顶刊研究, 与本项目语料最直接可比。其样本构建对
**公司发布内容**做文体型排除 (工作论文版原文逐字核验, 2026-06-13):

> "When collecting the news reports in the state-controlled newspapers, we only
> focus on news reports written by journalists, and we **exclude media releases
> from firms because they are rebroadcasts and do not contain any new
> information**."

这为本项目排除"公司发布/公告类整版转载" (年报/招股书/法定公告) 的**动机**提供
了中文新闻顶刊先例 — 即上限 10000 字 + `ad_keywords` 共同针对的那类内容。

⚠ **诚实边界 (须在论文讲清, 不可越界)**:
1. You et al. 用**文体/来源类型**排除 (排除公司发布稿), **不设数值长度过滤** —
   其 "number of words in an article" (`ArticleWord`) 仅作**研究变量** (考察报道
   详尽度), 非样本过滤器。故本项目仍**无**"≥100 字 / ≤10000 字"数值口径的直接
   先例; 数值阈值是对该文体排除动机的合理**操作化**。
2. You et al. 明确**不依赖正负词计数**构造语调 (原文: "We do not rely on the
   count of positive or negative words"), 与 TSM 2008 / 本项目词典轨方法不同 —
   引它是为锚定**样本构建惯例**, 非语调方法。
- 引用: You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the
  pen? *The Review of Financial Studies*, 31(1), 43–96.
  https://doi.org/10.1093/rfs/hhx055

> 旁证 (供预防审稿质疑): 媒体语调正典多数**不**做逐文长度过滤 —— Tetlock (2007,
> JF) 用单一每日 WSJ 专栏、Garcia (2013, JF) 用固定 NYT 专栏、Engelberg & Parsons
> (2011, JF) 用地理覆盖变异识别。逐文长度过滤特属"公司层面新闻聚合" (TSM 2008) 与
> "中文新闻文体排除" (You et al. 2018) 两类设计, 本项目属此两类, 故沿用其过滤惯例。

## 3. 三阈值的定性 (审稿人视角)

| 阈值 | 定性 | 辩护路线 | 风险 |
|---|---|---|---|
| 标题 ≥2 字 | 数据完整性过滤 | 剔除损坏行 (须由 §4 标题诊断坐实删除以 0 字为主, 非真标题) | 低 (待数据确认) |
| 正文 ≥100 字 | 样本选择项 | TSM 2008 直接锚点 + 测量可靠性 | 低 (有先例) |
| 正文 ≤10000 字 | 样本选择项 | `ad_keywords` 公告排除的**长度兜底** (抓漏过关键词的整版转载); 动机有 You et al. 2018 RFS 文体排除先例, 但**无数值上限直接先例** | 中 → 须敏感性 + 增量披露 |

⚠ 选择非随机性自查 (上限是全文最弱环, 须直面三个 referee 必问):
1. **相对 ad_keywords 的增量**: 上限只该抓**漏过关键词的**整版转载。须报告"上限相对
   ad_keywords 的增量删除量" — 即仅因 >10000 字被删、但未被任何 ad_keyword 命中的
   行数及其占比。若该增量极小, 说明上限只是冗余兜底, 风险可忽略。
2. **被删样本实测构成 (承诺报告, 不以预期代替证据)**: 生产 run 后抽样人工查验
   >10000 字被删样本的文体构成, **报告实测占比** (而非断言"预期年报占多数")。
3. **选择非随机性**: 危机/处罚类银行报道往往更长, 若上限系统性删事件期深度报道,
   与广告锚定审计"被删类与监管事件强度相关"同构 (selection-on-outcome)。
若 (2) 发现真深度报道占比可感 → 改走 TSM 路线 (取消上限, 改对长文语调离群用标准化/
对语调度量本身缩尾), 但这是语料变更 → stage 21 付费重跑, 须过 M0 gate。

⚠ **§6 的上限=∞ 回归级敏感性从"deferred"升级为投稿前必交** — 这正是 referee
会指定的 robustness, 不能只停留在诊断计数。

## 4. 已落地的供数机制 (本次, $0)

**内容** — `load.py::_log_length_filter_diagnostics`, stage 00 逐源文件过滤前记录:
1. 内容汉字数分布: min / p1 / p5 / p50 / p95 / p99 / max;
2. 替代阈值矩阵保留行数: min ∈ {50, 100, 200} × max ∈ {5000, 10000, 20000, ∞}。

**标题** — `load.py::_log_title_filter_diagnostics`, 过滤前记录: ≥1/≥2/≥3 字各保留
行数 + 被 ≥2 删除者中 **0 字 (空/损坏) 与 1 字各几行**。这是 §3 标题行"数据完整性
非样本选择"定性的**直接证据源**: 若被删者绝大多数是 0 字, 则"删的是损坏行而非真
标题"坐实; 若 1 字真标题占比可感, 则须如实降级为样本选择项。

生产 run 后从 `logs/runs/<run_id>/00_preprocessing.log` 汇总 `[长度诊断]` 行
即得 data appendix 的内容分布表 + 各阈值删除量 + 标题删除构成, 无需重跑语料。

⚠ 供数前提 (审计 2026-06-13 逮出): 该日志行仅在 **冷缓存/重算路径** 出现 —
stage 00 增量缓存命中时 worker 被跳过 (`_process_single_file` 不执行) →
暖缓存 run 日志中无任何 `[长度诊断]` 行。全量生产 run 处理新语料为天然冷缓存,
故首跑必有诊断; 若仅对已缓存语料重跑取数, 须先 bump `PREPROCESS_CODE_VERSION`
或改用独立脚本扫 `00_preprocessing.parquet` 重算分布。

## 5. Data appendix 模板文本

⚠ 模板的稳健性句为**待检验命题**, 非既成结论 (§6 回归级敏感性尚未跑)。措辞已用
"检验是否稳健 / 报告替代阈值下的系数", **不得**改回"显示...稳定 / shows ... are
stable" — 除非检验跑出且方向确为稳健, 否则即报告不存在的结果 (学术诚信红线)。

**中文**:
> 我们要求标题含至少 2 个汉字 (剔除字段损坏记录), 正文含 100–10,000 个汉字。
> 下限沿袭 Tetlock, Saar-Tsechansky and Macskassy (2008) 对公司相关新闻报道 ≥50 词
> 的过滤 (排除仅含表格或列表的条目, 并限制比值型语调指标的离群影响); 上限用于
> 排除整版转载的年报、招股书与法定公告正文 (与关键词类公告过滤互为兜底), 排除
> 公司发布内容的做法亦见 You, Zhang and Zhang (2018) 对中文上市公司新闻的样本构建。
> 该过滤删除 X.X% 的原始条目; 附图 AX 报告正文长度分布; 附表 AX 报告在替代阈值
> (下限 50/200 字、上限 5,000/20,000 字或不设上限) 下重估的主回归系数, 用于检验
> 主结果对长度过滤的稳健性。

**English**:
> We require headlines to contain at least 2 Chinese characters (removing
> corrupted records) and article bodies to contain between 100 and 10,000
> Chinese characters. The lower bound follows Tetlock, Saar-Tsechansky, and
> Macskassy (2008), who discard firm-specific news stories shorter than 50 words
> to eliminate table- or list-only items and to limit the influence of outliers
> on ratio-based tone measures; the upper bound removes full-page reprints of
> annual reports, prospectuses, and statutory announcements, complementing our
> keyword-based announcement filter (excluding firm-issued content similarly
> follows You, Zhang, and Zhang's (2018) sample construction for Chinese
> listed-firm news). These filters remove X.X% of raw items. Figure AX reports
> the length distribution; in the Internet Appendix we examine whether our main
> coefficients are robust to setting the lower bound to 50 or 200 characters and
> the upper bound to 5,000, 20,000, or removing it entirely, with Table AX
> reporting the coefficients under these alternative thresholds.

## 6. 截断敏感性检验 — 刻意 deferred (⚠ 付费红线)

替代阈值下的**回归级**敏感性 (非诊断计数) 需要按新阈值重建语料 →
新增/移出文章 → stage 21 LLM 缓存 miss → 付费。故:
- 本次只落地诊断计数 (第 4 节, $0);
- 回归级敏感性与全量生产 run 合并执行 (一次付费窗口内顺带跑 4 个替代语料
  的轻量版: 词典轨 $0 可先行, LLM 轨仅对 delta 文章付费);
- 在那之前, 论文文本用第 5 节模板 + 诊断计数表即可支撑 data appendix。

⚠ **投稿前必交项 (非可选)**: 上限=∞ 的回归级敏感性是 referee 必指定的 robustness
(见 §3), 不得停在诊断计数; 须在合并生产 run 时跑出并入 Internet Appendix。"deferred"
仅指执行**时点** (等付费窗口), 非可省略。

## 7. 改动清单 (2026-06-13)

| 文件 | 改动 | 行为影响 |
|---|---|---|
| `pipeline/preprocess/load.py` | +内容诊断 (`_length_filter_diagnostics`/`_log_length_filter_diagnostics`, 含全 NaN 守卫) +标题诊断 (`_title_filter_diagnostics`/`_log_title_filter_diagnostics`) + 两调用点 + `__all__` 四项 | log-only, 语料零变更 |
| `config/preprocessing.yaml` | 长度段注释: 锚点/定性/披露义务/付费红线/白话 | 注释 only, 参数值不动 (2/100/10000) |
| `tests/test_length_filter_diagnostics.py` (新建) | 14 测试 (内容计数/分位/不可变/空与全NaN/生产阈值耦合/调用点接线 + 标题构成/接线) | — |
| 本文档 | 权威辩护 + 中英 appendix 模板 + You et al. 2018 RFS 锚点 + √ 独立性限定 | — |
