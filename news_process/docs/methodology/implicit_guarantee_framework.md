# Implicit Guarantee 框架在中国 Banking Risk-Taking 研究中的应用

> **Status**: M0 立项文档 (2026-05-18)
> **Owner**: 第 10 篇 (bank_media_disagreement) + 第 11 篇 (bank_news_clarity) 共享理论框架
> **修复**: V4 audit F-P1.1 critical, 中国 setting Z-score 解释必须

---

## 一、为什么必须引入 implicit guarantee 框架

### V4 audit 暴露的致命问题

国际顶刊 banking risk-taking 文献 (Laeven-Levine 2009 JFE 为代表) 的 Z-score 框架建立在 **市场化银行 + 显性破产风险** 假设上:

- Z-score = (ROA + CAR) / σ(ROA)
- 解释: Z-score 越低 → 银行离倒闭越近 → risk-taking 越激进
- **Implicit 假设**: 银行真的会倒闭, 储户真的会损失

### 中国 banking 现实

中国商业银行系统受 **政府隐性担保** 主导:

- **央行 LOLR 承诺**: 系统重要性银行 + 国有大行不允许倒闭
- **财政部 implicit guarantee**: 历史先例 (2019 包商接管, 储户 100% 兑付, 与 FDIC 美式 250k cap 不同)
- **地方政府担保**: 城商行 / 农商行多有地方政府隐性背书
- **存款保险**: 2015 才建立, 50 万元 cap, 但 *从未真正违约赔付* (包商案例直接 100% 兑付)

### 后果: Z-score 在中国失去 standard interpretation

若直接套用 Laeven-Levine 2009 框架, **顶刊 reviewer 一审必拒**:
- 国有大行 Z-score 低不代表 risk-taking 激进 (因为有 LOLR, σ(ROA) 在 implicit guarantee 下被压缩)
- 城商 / 农商行 Z-score 不可与上市股份制行直接比较
- 跨 SOE / non-SOE 子样本的 Z-score 系数解读完全不同

---

## 二、Acharya-Anginer-Warburton 框架

### 主要锚定文献

**Acharya, Anginer & Warburton (2016, RFS working paper)**:
"The End of Market Discipline? Investor Expectations of Implicit Government Guarantees"

- **核心 finding**: TBTF (too big to fail) 银行的 bond spread 显著低于其 fundamentals 暗示的水平
- **测量**: implicit guarantee value = TBTF spread discount = (fair spread - actual spread)
- **机制**: market discipline 弱化 → moral hazard → risk-taking 上升

### 延伸到中国 setting

| 维度 | Acharya 2016 美国 | 中国对应 |
|---|---|---|
| TBTF 边界 | top 10 银行 + 资产 > $250B | 国有 6 大行 + 部分系统重要性股份制 (招商 / 兴业 / 浦发 / 中信) |
| Implicit guarantee 强度 | top 10 高, 中型行中等 | 国有 > 股份制 > 上市城商 > 非上市城商 > 农商 > 村镇 (递减) |
| Bond spread 数据 | TRACE secondary market | CFETS 银行间债券 (有限) + 二级资本债发行利差 |
| Market discipline 弱化标志 | spread / fundamentals 弹性 ↓ | NPL / ROA 对存款流出的弹性 ↓ |

### 关键 quote (作 introduction citation)

> "These findings suggest that investors expect the government to use public funds to back the bondholders of major financial institutions, which weakens market discipline and may foster excessive risk-taking" (Acharya, Anginer & Warburton 2016, working paper §1).

---

## 三、SOE 银行分类 spec

### 计算字段定义

```yaml
is_soe:
  type: binary
  values: [0, 1]
  definition: 银行是否受国务院 / 财政部 / 地方政府直接 / 间接控制 (持股 > 50% 或一致行动人)

bank_type_id:
  type: categorical
  values:
    1: 国有大行 (state_owned)
    2: 股份制商业银行 (joint_stock)
    3: 城市商业银行 (city_commercial)
    4: 农村商业银行 (rural_commercial)
    5: 民营银行 / 互联网银行 (private_internet)
    6: 外资银行 (foreign_owned)
    7: 政策性银行 (policy_bank)
    8: 其他 / 待分类 (other)

implicit_guarantee_tier:
  type: ordinal
  values: [1, 2, 3, 4, 5]
  definition: implicit guarantee 强度排名
  values_detail:
    5: 国有大行 + 政策性银行 (绝对 TBTF)
    4: 系统重要性股份制 (D-SIB list, 招商/兴业/浦发/中信/民生)
    3: 其他股份制 + 上市城商行
    2: 非上市城商行 (有地方政府背书)
    1: 农商行 + 民营 + 互联网 + 外资
```

### 国有 6 大行清单 (is_soe = 1, bank_type_id = 1, tier = 5)

| 中文名 | 上市状态 | 资产规模 (2024Q4 估) | 实控人 |
|---|---|---|---|
| 中国工商银行 | A+H | ~50 万亿 | 财政部 + 中央汇金 |
| 中国农业银行 | A+H | ~42 万亿 | 财政部 + 中央汇金 |
| 中国银行 | A+H | ~37 万亿 | 财政部 + 中央汇金 |
| 中国建设银行 | A+H | ~43 万亿 | 中央汇金 |
| 交通银行 | A+H | ~14 万亿 | 财政部 |
| 中国邮政储蓄银行 | A+H | ~17 万亿 | 邮政集团 + 财政部 |

### 政策性银行清单 (is_soe = 1, bank_type_id = 7, tier = 5)

| 中文名 | 主要业务 |
|---|---|
| 国家开发银行 | 国家开发性金融 |
| 中国进出口银行 | 进出口贸易融资 |
| 中国农业发展银行 | 农业政策性金融 |

### 系统重要性股份制 (is_soe = 0, bank_type_id = 2, tier = 4)

按银保监会 D-SIB list (2024):
- 招商银行 / 兴业银行 / 浦发银行 / 中信银行 / 民生银行
- (部分名单可能因银保监会评估变化, 项目以 2024 Q4 list 为 baseline frozen)

### 其他股份制 (is_soe = 0, bank_type_id = 2, tier = 3)

光大 / 华夏 / 广发 / 平安 / 恒丰 / 渤海 / 浙商

---

## 四、Spec 在第 10/11 篇主回归的应用

### 主回归 spec (两篇通用)

```stata
* Baseline (无 implicit guarantee 校准)
reghdfe z_score treatment_var bank_controls year_controls, ///
    absorb(bank_id year province) cluster(bank_id year)

* V4 F-P1.1 修复: 加入 implicit guarantee 交互
reghdfe z_score c.treatment_var##i.is_soe bank_controls year_controls, ///
    absorb(bank_id year province) cluster(bank_id year)

* 三 tier 异质性
reghdfe z_score c.treatment_var##i.implicit_guarantee_tier bank_controls year_controls, ///
    absorb(bank_id year province) cluster(bank_id year)
```

### 解读

- 系数 `treatment × is_soe` 显著 → channel 在 SOE / non-SOE 间异质 (符合 Acharya 框架预测)
- `treatment × implicit_guarantee_tier` 单调下降 → channel 随 implicit guarantee 强度系统变化

### Heterogeneity table 必含

| 子样本 | 预期 |
|---|---|
| Tier 5 (国有 6 大 + 政策性) | treatment 效应弱 (LOLR 主导, market discipline 失效) |
| Tier 4 (D-SIB 股份制) | treatment 效应中等 |
| Tier 3-2 (普通股份制 + 上市城商) | treatment 效应中强 |
| Tier 1 (农商 + 民营 + 互联网) | treatment 效应强 (无 implicit guarantee, market discipline 起作用) |

---

## 五、数据来源

### is_soe 计算来源

| 信息 | 数据源 |
|---|---|
| 实控人结构 | Wind 银行库 → 股权穿透模块 |
| 国资委 / 财政部持股 | 银保监会年度披露 |
| 中央汇金持股 | 中央汇金公司公开信息 |
| 地方政府控股 | 地方国资委公开信息 |

### bank_type_id 计算来源

| 信息 | 数据源 |
|---|---|
| 银保监会银行分类 | 银保监会官网 → 银行业金融机构法人名单 (按月更新) |
| 上市状态 | 沪深交易所 / 港交所 / 美股 |
| 资产规模 | 银保监会季报 + Wind 银行库 |

### implicit_guarantee_tier 校准来源

- 银保监会 D-SIB list (年度更新)
- Wind 银行库 → 信用评级 (AAA / AA+ / AA ...)
- Acharya 2016 RFS methodology (TBTF spread discount 量化, 若 CFETS 数据可得则计算)

---

## 六、与 V4 audit 其他 finding 的对应

| V4 finding | 本框架修复 |
|---|---|
| F-P1.1 [CRITICAL] Risk-taking 中国 setting fundamentally 不同 | ✅ 引入 Acharya 2016 框架 |
| F-P1.2 [CRITICAL] 国有大行 6 家主导 panel power | ✅ tier 5 sample split + drop top 6 robustness |
| F-P1.3 [MAJOR] non-listed bank 子类型细分 | ✅ tier 1-4 细分 |
| F2.2 [MAJOR] boundary condition 缺失 | ✅ 5 tier heterogeneity 即 boundary 论证 |
| F-Adv.4 [MAJOR] "Why not LLM 直接预测" | ✅ tier 异质性是 mechanism approach 不可替代的价值 |

---

## 七、Definition of Done

- [x] 本框架文档 (M0 已完成)
- [ ] `is_soe` / `bank_type_id` / `implicit_guarantee_tier` 数据字段加入 outcome panel (M1-M2)
- [ ] 500 行实控人结构数据收集 (M1, 与 DC2 dry-run 共享)
- [ ] D-SIB list frozen at 2024-Q4 (M1)
- [ ] paper_spec.yaml 中 heterogeneity 字段已含 SOE / tier 维度 (✅ 已完成, 见两份 spec)
- [ ] Stata heterogeneity .do 模板 (M5-M7, 第 10/11 篇 baseline 阶段)

---

## 八、Definition of Done — 引用清单

### Tier 1 (必引)
- Acharya, V. V., Anginer, D., & Warburton, A. J. (2016). The End of Market Discipline? Working paper, NYU Stern.
- Laeven, L., & Levine, R. (2009). Bank governance, regulation and risk taking. *Journal of Financial Economics*, 93(2), 259-275.

### Tier 2 (引)
- Demirgüç-Kunt, A., & Huizinga, H. (2010). Bank activity and funding strategies. *Journal of Financial Economics*, 98(3), 626-650.
- Dell'Ariccia, G., Laeven, L., & Suarez, G. A. (2017). Bank leverage and monetary policy's risk-taking channel. *Journal of Finance*, 72(2), 613-654.

### Tier 3 (背景引)
- Allen, F., Qian, J., Shan, S. C., & Zhao, M. (2019). The IPO of Industrial and Commercial Bank of China. *Review of Financial Studies*, 32(2), 421-465.
- Berger, A. N., Hasan, I., & Zhou, M. (2009). Bank ownership and efficiency in China. *Journal of Banking & Finance*, 33(1), 113-130.
