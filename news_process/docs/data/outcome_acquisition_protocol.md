# Banking Outcome Acquisition Protocol (DC2)

> **Status**: M0 协议文档 (2026-05-18)
> **Owner**: 第 10 + 第 11 篇共享 outcome panel
> **修复**: V4 audit DC2 critical, 决定 fallback path α/β/γ

---

## 一、目标

为 500 家中国商业银行 × 18 年 (2007-2024) panel 抓取以下 outcome 字段:

| 字段 | 用途 | Z-score 公式角色 |
|---|---|---|
| `roa` | Z-score 分子 | (ROA + CAR) / σ(ROA) |
| `capital_adequacy_ratio` | Z-score 分子 | 同上 |
| `total_assets` | RWA ratio 分母 | RWA / TA |
| `rwa` | RWA ratio 分子 | 同上 |
| `npl_balance` | NPL formation rate 计算 | NPL_t - NPL_{t-1} |
| `npl_ratio` | 备用 simple risk measure | path γ fallback |
| `total_loans` | NPL formation rate 分母 | / Loan_{t-1} |
| `loan_writeoffs` | NPL formation rate 修正项 | + writeoffs_t |
| `loan_loss_provision` | LLP discretion (第 11 篇) | Bushman-Williams 2012 JAE |

---

## 二、数据源优先级 (per record)

### Source 1: Wind 银行库 (Primary)

- **覆盖率**: 上市行 100%, 非上市股份制 ~80-90%, 非上市城商 ~60-70%, 农商 ~30-40%
- **频率**: 季度数据可得
- **凭证**: WindPy SDK + 商业账号
- **优势**: 字段标准化, API 稳定
- **劣势**: 非上市行覆盖有限, license 费用

### Source 2: 银保监会季报 (Fallback 1)

- **URL**: https://www.cbirc.gov.cn/cn/view/pages/ItemList.html?itemPyCode=tjsj
- **覆盖率**: 行业层面 100%, 单家银行视披露而定 (2018 后非公开比例上升)
- **凭证**: 公开访问 (无需账号)
- **反爬要求**:
  - User-Agent rotation (随机 5-10 个常见浏览器 UA)
  - 请求间隔 ≥ 2 秒
  - 维持 session cookies
  - 必要时手动验证码 (人工 fallback)
- **历史数据可得性**: 2007-2014 大量缺失, 2015-2018 完整, 2019+ 部分回收

### Source 3: 银行年报 PDF (Fallback 2)

- **来源**: 巨潮资讯网 (cninfo.com.cn) + 港交所披露易 (hkexnews.hk) + 各行官网投资者关系页
- **频率**: 年度
- **覆盖率**: 上市行 100%, 非上市约 70% 自主披露
- **提取工具**: tabula-py (Java 依赖) + 关键词 regex + 人工核对
- **挑战**: 各行 PDF 表格 schema 差异巨大 (每家行可能要写 per-bank parser)
- **OCR 兜底**: 早期年报扫描件需 OCR (pytesseract / Adobe Acrobat)

---

## 三、Dry-run 流程

### Step 1: 抓取 2024-Q1 单季度 sample (20 行)

```bash
cd F:\WiseSearch\data_antigravity_project\news_process

# 设置 Wind API key
export WIND_API_KEY="your_wind_token_here"   # Windows: set WIND_API_KEY=...

# 跑 dry-run
python scripts/data_acquisition/banking_outcome_dry_run.py \
    --year-quarter 2024-Q1 \
    --output data/dry_run/2024Q1_outcome.parquet
```

预期输出: `data/dry_run/2024Q1_outcome.parquet` 含 20 行 × 14 列。

### Step 2: Schema validation

```bash
python scripts/data_acquisition/outcome_schema_validator.py \
    --input data/dry_run/2024Q1_outcome.parquet \
    --report data/dry_run/2024Q1_validation_report.json
```

输出 `data/dry_run/2024Q1_validation_report.json` 含:
- `schema_compliance`: true/false
- `per_outcome_stats`: 每字段可得率 + 描述统计
- `feasibility.z_score.joint_availability`: 关键决策依据
- `passes_z_score_feasibility`: ≥ 40% 才 true

### Step 3: Fallback path 决策

```bash
python scripts/data_acquisition/fallback_decision.py \
    --validation-report data/dry_run/2024Q1_validation_report.json \
    --decision-output data/dry_run/2024Q1_path_decision.json
```

输出决策 JSON, 含 `path` (alpha / beta / gamma) + 后续 action items.

---

## 四、Full acquisition 流程 (M1-M2, sample dry-run 通过后)

### Bank list 准备

1. 创建 `news_process/config/bank_list.yaml` 含 500 行 banks
2. 来源: 银保监会银行业金融机构法人名单 (按月更新)
3. 字段:
   ```yaml
   - target_bank: 中国工商银行
     bank_type_id: 1
     is_soe: true
     implicit_guarantee_tier: 5
     wind_code: "601398.SH"
     pdf_dir: data/annual_reports/工商银行/
   - ...
   ```

### Full panel 抓取

```bash
python scripts/data_acquisition/banking_outcome_dry_run.py \
    --year-quarter 2007-Q1 \
    --output data/processed/47_outcomes/2007Q1.parquet \
    --full-bank-list

# 重复 2007-Q1 ~ 2024-Q4 共 72 个 quarter
# 或写 Python wrapper 一次跑全 (M1 deliverable)
```

### 合并 + Stage 47 注册

1. 合并 72 个 parquet → `data/processed/47_risk_taking_outcomes.parquet`
2. 注册 `core/dag.py::STAGES_MAIN` 加 stage 47
3. 加 `core/schemas.py::OUTPUT_REGISTRY` 字段
4. 创建 thin shim `news_process/47_risk_taking_outcomes.py`
5. 更新 `tests/integration/test_dag_consistency.py` 14 → 15 stage
6. Regenerate golden baseline + 跑全测试套件

---

## 五、Path α/β/γ 决策含义

### Path α (≥ 70% joint availability)

- ✅ 全 outcome 设计可行
- 主回归: Z-score 主 + NPL formation + RWA ratio secondary
- 第 11 篇 LLP discretion direct match Bushman-Williams 2012 JAE 可用
- KPI: 维持 48 月 1.5-2.2 篇接收预期

### Path β (40-70%)

- ⚠️ RWA / LLP 缺失较多
- 主回归: Z-score 主 + NPL formation, RWA 退化为 partial-sample robustness
- 第 11 篇 anchor 转向 Bushee 2010 JAR 框架 (减少对 Bushman-Williams direct match 依赖)
- KPI: 接收预期维持 1.2-1.8 篇

### Path γ (< 40%)

- ❌ Z-score 不可算
- 退回 ROA + NPL ratio simple measure
- **与 P1 bank_fintech_tone 主 outcome 重叠** → 需重新评估两篇是否值得继续
- 考虑转向 V4 推荐的 #18 (policy alignment) / #19 (media breadth) candidate
- KPI: 严重下调至 0.5-1.0 篇

---

## 六、Time budget

| Step | Duration | Owner |
|---|---|---|
| 配置 Wind API key + 测试 SDK | 1 天 | 用户 |
| Dry-run sample 20 行 | 0.5 天 | 用户运行脚本 |
| Validation + fallback decision | 即时 (自动) | 脚本 |
| 用户审 decision + go/pivot | 1 天 | 用户 |
| Bank list 准备 (500 行) | 3 天 | 用户 + 银保监 list 整理 |
| Full panel 抓取 (72 quarters × 500 banks) | 1-2 周 | 自动 (Wind) + 人工 (年报 PDF) |
| Stage 47 注册 + 测试更新 | 1 周 | 自动 |
| **总计** | **3-4 周** | **M0-M2** |

---

## 七、风险登记

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| Wind API license 限额超出 | 中 | 中 | 分批抓取 + 延迟 |
| 银保监会反爬升级 | 高 | 中 | 人工兜底 + 历史快照 |
| 历史 PDF OCR 准确率低 | 高 | 中 | 人工核对关键字段 |
| 非上市行 RWA 大面积缺失 | 高 | 高 | 触发 path β |
| Bank list 与项目 panel 主键不一致 | 中 | 高 | 严格基于现有 panel target_bank field |

---

## 八、Definition of Done

- [x] 抓取脚本骨架 (banking_outcome_dry_run.py)
- [x] Schema validator
- [x] Fallback decision logic
- [x] 本协议文档
- [ ] Wind API 调用代码填入 (TODO 标记, 用户实施)
- [ ] 银保监会爬虫代码填入 (TODO 标记, 用户实施)
- [ ] Annual report PDF parser (per-bank, 用户实施)
- [ ] Bank list 500 行 frozen (M1 deliverable)
- [ ] Dry-run 2024-Q1 实际运行 (用户执行)
- [ ] Path α/β/γ 决策 + spec amendment (用户决策)
