# AutoPaper 复现 — 环境配置指南

## 1. Stata 环境

### 1.1 确认 Stata（≥ 15.0）
确保系统中已安装 Stata，并且可执行文件路径已添加到操作系统的 PATH 环境变量中。

可以通过以下命令验证：
```bash
StataMP-64 -q -e display "Stata runs"
# 或者对于 Windows 中的批处理/命令行环境
stata -q -e display "Stata runs"
```

### 1.2 核心 Stata 包安装
```stata
* 00_packages.do — 在每个论文项目中首先运行

* ---- 基础回归与高维固定效应 ----
ssc install reghdfe, replace
ssc install ftools, replace
ssc install ppmlhdfe, replace       // 泊松伪极大似然（计数因变量）
ssc install hdfe, replace

* ---- 结果输出格式化 ----
ssc install estout, replace
ssc install outreg2, replace
ssc install asdoc, replace

* ---- 数据预处理 ----
ssc install winsor2, replace        // 缩尾处理

* ---- 匹配与因果推断 ----
ssc install psmatch2, replace       // 倾向得分匹配 (PSM)
ssc install rdrobust, replace       // 断点回归 (RDD)
ssc install rddensity, replace      // McCrary 密度检验
ssc install ivreg2, replace         // 工具变量两阶段
ssc install ranktest, replace       // ivreg2 依赖

* ---- DID 前沿方法 ----
ssc install eventstudyinteract, replace
ssc install did_multiplegt, replace
ssc install csdid, replace
ssc install drdid, replace

* ---- 图形与可视化 ----
ssc install coefplot, replace
ssc install binscatter, replace

* ---- 异质性与检验 ----
ssc install bdiff, replace          // 组间系数差异 Bootstrap 检验

* ---- 银行面板诊断 ----
ssc install xtabond2, replace       // 系统 GMM（动态面板）
ssc install xtscc, replace          // Driscoll-Kraay 标准误
ssc install xtcsd, replace          // 截面相关 Pesaran CD 检验
```

## 2. LLM API 配置

### 2.1 所需 LLM 服务
用于论文撰写和评审的模型：

| 模型                   | 用途                        | API 来源      |
| ---------------------- | --------------------------- | ------------- |
| Claude claude-opus-4-5 | 论文撰写（authoring_model） | Anthropic API |
| GPT-5-mini             | 评审模型                    | OpenAI API    |
| Grok-4.1-Fast          | 评审模型                    | xAI API       |
| Gemini-3-Flash         | 评审模型                    | Google AI API |
| Codex-Mini             | 评审模型                    | OpenAI API    |

### 2.2 API Key 环境变量
```bash
# 在 .env 或系统环境变量中配置
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export XAI_API_KEY="xai-..."
export GOOGLE_AI_API_KEY="AIza..."
```

## 3. Python 环境（辅助）

部分论文使用 Python 进行数据预处理：
```bash
pip install requests pandas numpy openpyxl httpx
```

## 4. 目录结构初始化

```bash
# 为新论文创建标准目录结构
mkdir -p paper_XXXX/v1/{code,data,figures,tables,output}
```

## 5. 验证安装

```stata
* 运行以下代码验证所有核心包是否正确安装
local packages "reghdfe ftools ppmlhdfe estout outreg2 coefplot rdrobust psmatch2 bdiff winsor2 ivreg2 xtabond2"

foreach pkg in `packages' {
    capture which `pkg'
    if _rc == 0 {
        display "✅ `pkg' 已安装"
    }
    else {
        display "❌ `pkg' 未安装"
    }
}
```
