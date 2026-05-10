# Stata Do文件审查报告

## 审查日期
2026-05-10

## 审查范围
- 16个Stata do文件
- 1个Python转换脚本
- 面板数据结构验证

---

## 一、审查结果总览

### ✅ 已完成项

1. **文件创建完整**
   - 主控文件: 1个 (`99_master.do`)
   - 变量标签文件: 14个 (`01-14_label_*.do`)
   - 辅助文件: 1个 (`00_load_panel_data.do`)
   - 总计: 16个do文件，1439行代码

2. **面板数据结构验证**
   - 数据维度: 4,608行 × 1,725列 ✓
   - 唯一银行数: 288个 ✓
   - 年份范围: 2008-2023 (16年) ✓
   - 关键列完整: target_bank, year 无缺失值 ✓

3. **指标分类统计**
   - LLM情感指标: 394个
   - 词典情感指标: 390个
   - BERT情感指标: 298个
   - 媒体相关指标: 74个
   - 地理相关指标: 80个
   - 网络相关指标: 59个

4. **轨道分布**
   - _full轨道: 511个指标
   - _ctx轨道: 531个指标
   - _title轨道: 388个指标

5. **加权指标**
   - VW (Value-Weighted): 49个
   - MW (Media Authority): 174个
   - HW (Herd-Weighted): 210个
   - 标准化指标(_z): 51个

6. **Python转换脚本**
   - 脚本创建成功 ✓
   - 编码问题已修复 ✓
   - 可正常执行转换 ✓

---

## 二、发现的问题

### ⚠️ 问题1: 变量标签覆盖率不足

**严重程度**: 高

**问题描述**:
- 数据集总变量数: 1,725个
- 已标注变量数: 698个
- **覆盖率: 40.5%**
- 未标注变量: 1,027个

**未标注变量分类**:
1. LLM相关: 256个
2. 词典相关: 298个
3. BERT相关: 186个
4. 其他: 287个

**典型未标注变量示例**:
```
- avg_gemini3_conf_ctx
- avg_gpt5nano_conf_title
- avg_bian_2021_neg_ratio_full
- bert_avg_neg_app_ctx
- avg_cpw_ctx
- avg_msent_ctx
```

**原因分析**:
1. 部分衍生指标未包含在标签脚本中
2. 上下文(_ctx)和标题(_title)轨道的部分指标遗漏
3. 聚合统计指标(avg_*, sum_*)未完全覆盖

### ⚠️ 问题2: Stata变量名长度限制

**严重程度**: 中

**问题描述**:
8个变量名超过Stata的32字符限制，已被自动截断：

```
jiang_2021_idf_score_hw_sum_title   -> jiang_2021_idf_score_hw_sum_titl
jiang_2021_idf_score_mw_sum_title   -> jiang_2021_idf_score_mw_sum_titl
prov_leave1out_dict_avg_tone_full   -> prov_leave1out_dict_avg_tone_ful
prov_leave1out_dict_avg_tone_title  -> prov_leave1out_dict_avg_tone_tit
city_leave1out_dict_avg_tone_full   -> city_leave1out_dict_avg_tone_ful
city_leave1out_dict_avg_tone_title  -> city_leave1out_dict_avg_tone_tit
prov_leave1out_bert_avg_pos_title   -> prov_leave1out_bert_avg_pos_titl
city_leave1out_bert_avg_pos_title   -> city_leave1out_bert_avg_pos_titl
```

**影响**:
- 变量名被截断可能导致混淆
- 需要在do文件中使用截断后的变量名

### ⚠️ 问题3: Python脚本警告

**严重程度**: 低

**问题描述**:
1. FutureWarning: `errors='ignore'` 已弃用
2. InvalidColumnName: 8个变量名被自动重命名

**影响**: 不影响功能，但需要注意未来兼容性

---

## 三、改进建议

### 🔧 建议1: 补充缺失的变量标签（优先级：高）

**方案A: 创建补充标签文件**
创建 `15_label_supplementary.do` 包含所有遗漏的变量标签

**方案B: 扩展现有文件**
在现有14个标签文件中补充遗漏的变量

**推荐**: 方案A，便于维护和审查

### 🔧 建议2: 处理变量名长度问题（优先级：中）

**方案A: 在Python转换时重命名**
在 `convert_parquet_to_stata.py` 中预先重命名超长变量

**方案B: 在Stata中重命名**
在主控文件中添加 `rename` 命令

**推荐**: 方案B，保持原始数据不变

### 🔧 建议3: 优化Python脚本（优先级：低）

1. 修复 FutureWarning
2. 添加变量名长度检查和自动缩短功能
3. 改进错误处理

---

## 四、质量评估

### 代码质量: ⭐⭐⭐⭐☆ (4/5)

**优点**:
- ✅ 模块化设计，14个独立标签文件
- ✅ 主控文件自动化程度高
- ✅ 注释清晰，结构合理
- ✅ 变量标签中文化，便于理解

**不足**:
- ❌ 变量标签覆盖率仅40.5%
- ⚠️ 部分变量名超长

### 文档质量: ⭐⭐⭐⭐⭐ (5/5)

**优点**:
- ✅ README.md 详细完整
- ✅ 使用示例丰富
- ✅ 变量命名规则清晰
- ✅ 学术参考文献完整

### 可用性: ⭐⭐⭐☆☆ (3/5)

**优点**:
- ✅ 主控文件一键执行
- ✅ Python转换脚本可用

**不足**:
- ❌ 需要补充1027个变量标签才能完全可用
- ⚠️ 变量名截断可能导致混淆

---

## 五、后续行动计划

### 立即执行（优先级：高）

1. **补充缺失的变量标签**
   - 创建 `15_label_supplementary.do`
   - 覆盖所有1027个未标注变量
   - 预计工作量: 2-3小时

2. **更新主控文件**
   - 添加 `15_label_supplementary.do` 的执行
   - 添加变量名重命名逻辑

### 短期优化（优先级：中）

3. **处理变量名长度问题**
   - 在主控文件中添加 `rename` 命令
   - 更新相关标签文件

4. **优化Python脚本**
   - 修复 FutureWarning
   - 改进变量名处理

### 长期改进（优先级：低）

5. **添加数据验证**
   - 检查变量标签完整性
   - 验证数据类型一致性

6. **创建测试脚本**
   - 自动化测试do文件语法
   - 验证变量标签覆盖率

---

## 六、结论

### 总体评价: ✅ 基本可用，需要补充

当前创建的Stata do文件体系**结构完整、设计合理**，但**变量标签覆盖率不足**是主要问题。

### 可用性状态

- **当前状态**: 40.5%变量已标注，可以部分使用
- **完全可用**: 需要补充1027个变量标签
- **预计完成时间**: 补充标签后即可达到100%覆盖率

### 推荐使用方式

**方案1: 立即使用（部分功能）**
```stata
do stata/99_master.do
* 使用已标注的698个变量进行分析
```

**方案2: 等待补充后使用（完整功能）**
```stata
* 等待创建 15_label_supplementary.do
* 然后执行完整的主控文件
```

---

## 附录A: 文件清单

### Stata Do文件（16个）

| 文件名 | 行数 | 大小 | 标签数 | 说明 |
|--------|------|------|--------|------|
| 00_load_panel_data.do | 46 | 1.4KB | 0 | 数据加载说明 |
| 01_label_variables.do | 59 | 3.0KB | 34 | 基础变量和LLM指标 |
| 02_label_dict_bert.do | 77 | 4.2KB | 45 | 词典和BERT指标 |
| 03_label_features.do | 76 | 3.8KB | 41 | 文本特征指标 |
| 04_label_media.do | 80 | 4.0KB | 47 | 媒体异质性指标 |
| 05_label_advanced.do | 77 | 3.8KB | 36 | 高级分析指标 |
| 06_label_geography.do | 89 | 4.3KB | 50 | 地理缓冲指标 |
| 07_label_iv_did.do | 101 | 4.7KB | 66 | Bartik IV和DID |
| 08_label_network.do | 102 | 5.0KB | 59 | 网络指标 |
| 09_label_strategic.do | 94 | 4.9KB | 54 | 战略差异度指标 |
| 10_label_benefit_token.do | 60 | 2.8KB | 28 | 社会效益指标 |
| 11_label_washing_disag.do | 111 | 5.7KB | 72 | 洗绿和分歧度 |
| 12_label_cater_misc.do | 114 | 5.7KB | 60 | 迎合指标 |
| 13_label_standardized.do | 79 | 4.4KB | 51 | 标准化指标 |
| 14_label_jf_exc.do | 87 | 4.7KB | 55 | JF系数和排除性 |
| 99_master.do | 187 | 6.2KB | 0 | 主控文件 |
| **总计** | **1,439** | **64.6KB** | **698** | |

### 辅助文件

- `scripts/convert_parquet_to_stata.py` - Python转换脚本
- `stata/README.md` - 使用说明文档
- `STATA_INTEGRATION_SUMMARY.md` - 项目总结

---

## 附录B: 未标注变量统计

### 按类型分类

| 类型 | 数量 | 占比 |
|------|------|------|
| LLM相关 | 256 | 24.9% |
| 词典相关 | 298 | 29.0% |
| BERT相关 | 186 | 18.1% |
| 其他 | 287 | 27.9% |
| **总计** | **1,027** | **100%** |

### 按轨道分类

| 轨道 | 未标注数量 |
|------|-----------|
| _full | ~340 |
| _ctx | ~350 |
| _title | ~250 |
| 其他 | ~87 |

---

**审查人**: Claude Code  
**审查日期**: 2026-05-10  
**版本**: v1.0
