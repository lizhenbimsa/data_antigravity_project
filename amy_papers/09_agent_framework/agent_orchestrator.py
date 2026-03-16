# -*- coding: utf-8 -*-
"""
AutoPaper 生产基础设施 — 主编排器（Agent Orchestrator）
==========================================
驱动单篇论文从创意到发布的完整 8 阶段流水线。
包含状态机管理、断点续传和完整的错误恢复。
"""

import json
import time
import shutil
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Optional

from config import (
    PATHS, PIPELINE_STAGES, AUTHORING_MODELS,
    REVIEW_THRESHOLDS, StageConfig, setup_logging
)
from llm_client import generate_to_file, generate_with_model, get_global_tracker
from stata_executor import StataExecutor, STANDARD_STATA_PIPELINE

logger = setup_logging("paper.orchestrator")


# ============================================================
# 1. 流水线状态
# ============================================================

class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineState:
    """流水线状态持久化管理器"""

    def __init__(self, paper_dir: Path):
        self.state_file = paper_dir / ".pipeline_state.json"
        self.paper_dir = paper_dir
        self._state = self._load()

    def _load(self) -> dict:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        return {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "current_stage": "ideas",
            "stages": {
                name: {"status": StageStatus.PENDING, "attempts": 0, "error": None}
                for name in PIPELINE_STAGES
            },
            "revision_round": 0,
        }

    def save(self):
        self._state["updated_at"] = datetime.now().isoformat()
        self.state_file.write_text(
            json.dumps(self._state, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def get_stage_status(self, stage: str) -> str:
        return self._state["stages"][stage]["status"]

    def set_stage_status(self, stage: str, status: StageStatus, error: str = None):
        self._state["stages"][stage]["status"] = status
        if status == StageStatus.RUNNING:
            self._state["stages"][stage]["attempts"] += 1
        if error:
            self._state["stages"][stage]["error"] = error
        self._state["current_stage"] = stage
        self.save()

    @property
    def current_stage(self) -> str:
        return self._state["current_stage"]

    @property
    def revision_round(self) -> int:
        return self._state["revision_round"]

    def increment_revision(self):
        self._state["revision_round"] += 1
        self.save()

    def get_attempts(self, stage: str) -> int:
        return self._state["stages"][stage]["attempts"]


# ============================================================
# 2. 提示词引擎
# ============================================================

class PromptEngine:
    """
    动态提示词构建器。
    根据当前阶段和上下文文件自动生成 LLM 提示词。
    """

    @staticmethod
    def build_ideas_prompt(policy_domain: str = "Commercial Banking", schema_text: str = "") -> tuple[str, str]:
        """生成创意生成阶段的提示词（含 DiD/RDD 可行性评估表）"""
        system = (
            "你是一位专注于商业银行与金融监管研究的资深计量经济学家。"
            "你提出的研究创意须符合最高因果识别标准，适合发表于顶级金融学期刊。"
            "你始终包含具体的可行性评估。请用中文回复所有内容。"
        )
        prompt = f"""请为以下政策评估领域生成 5 个自主政策评估研究创意：{policy_domain}。

每个创意须满足：
1. 使用双重差分法（DiD，不同银行/银行类型在不同时间受到政策冲击的交错实施）或断点回归（RDD，基于银行监管指标阈值如资本充足率、不良贷款率、资产规模等存在明确断点）
2. **绝对指令：数据必须且只能使用本项目提供的以下变量清单中的现有变量组合，严禁编造任何不存在的变量。以下是可用的变量列表（来自 data_schema.txt）：**
```
{schema_text}
```
3. 因果识别策略须具有可信度
4. 包含具体可行性评估表

每个创意须严格遵循以下结构：

## 创意 N：[标题]
**政策：**[政策名称及实施时间]

各州实施时间（列出所有州及年份）。

**结果变量：**[具体结果变量及它在本地 data.dta 中的对应列名与标签]

**识别策略：**[DiD/RDD 策略及详细论证]

**创新性：**[2-3 句说明文献空白]

**可行性检验：**
- 变异性：[处理主体数量 N，对照主体数量 N]
- 数据可访问性：[确认变量真实存在于本项目的 data_schema.txt 中]
- 未被过度研究：[说明创新性]

**DiD 早期可行性评估：**

| 标准 | 评估 | 说明 |
|------|------|------|
| 处理前期数量 | 强/一般/弱 | [解释] |
| 进入处理的选择性 | 强/一般/弱 | [解释] |
| 对照组质量 | 强/一般/弱 | [解释] |
| 处理集群 | 强/一般/弱 | [处理州数量 N] |
| 并行政策 | 强/一般/弱 | [混淆因素] |

**主要关切：**[如有重大问题，请说明]

---

列出 5 个创意后，提供：
## 综合排名
| 排名 | 创意 | 识别策略 | 可行性 | 创新性 |
|------|------|---------|--------|--------|
| 1 | ... | 强 | 高 | 高 |

请避免：常规存贷款利率对利润的基础影响分析、基础的资本充足率合规研究、简单的规模与盈利正相关关系。
请确保每个创意都有明确定义的处理组和对照组银行。"""
        return system, prompt

    @staticmethod
    def build_ranking_prompt(ideas_content: str) -> tuple[str, str]:
        """生成创意排名提示词"""
        system = "你是一位正在评估研究提案的经济学期刊编辑。请用中文填写所有文本字段，仅输出合法 JSON。"
        prompt = f"""请对以下研究创意进行排名和评分。仅输出合法 JSON，不要添加任何其他文本。

{ideas_content}

对每个创意在四个维度上评分（0-10）：
- originality：是否填补了文献空白？
- feasibility：所需的变量是否在提供的 data_schema.txt 数据字典中真实存在？
- causal_credibility：识别策略是否能说服 AER 编辑？
- policy_relevance：对政策制定者是否有价值？

输出 JSON 格式（title 和 ranking_rationale 请用中文填写）：
{{
  "rankings": [
    {{"idea_id": 1, "title": "...", "originality": X, "feasibility": X,
      "causal_credibility": X, "policy_relevance": X, "total": X,
      "ranking_rationale": "..."}}
  ],
  "recommended": 1,
  "recommendation_rationale": "..."
}}"""
        return system, prompt

    @staticmethod
    def build_plan_prompt(selected_idea: str, schema_content: str = "") -> tuple[str, str]:
        """生成研究计划提示词（含完整 Stata 代码规范和效应量推理）"""
        system = (
            "你是一位专精于商业银行与金融监管研究的资深计量经济学家。"
            "你的计划须足够详细，以便其他研究者无需额外指导即可复现该研究。"
            "请包含完整的 Stata 代码规范和效应量推理。请用中文回复所有内容。"
        )
        prompt = f"""请为以下研究创意撰写详细的初始研究计划（initial_plan.md）：

{selected_idea}

计划须包含以下所有部分："""
        if schema_content:
            prompt += f"\n\n=======================\n附：可用数据字典 data_schema.txt：\n{schema_content}\n=======================\n请严格遵守字典里的变量名称，切勿使用外部或未定义的变量进行设计！\n\n"

        prompt += """
## 研究问题
[清晰、可检验的因果命题，聚焦于商业银行]

## 背景
[银行业监管政策详情、时间线，列出所有受影响的银行类型/批次及年份]

## 识别策略
**设计：**[交错 DiD / 精确 RDD]
**处理：**[精确定义处理组银行]
**对照：**[精确定义对照组银行]
**估计量：**建议使用 reghdfe 双向固定效应 + xtabond2 系统GMM + xtscc Driscoll-Kraay标准误
**平行趋势假设：**[为什么可信——至少 3 个论点]

## 预期效应与机制
**主要机制：**[监管政策如何影响银行行为和绩效]
**预期效应：**
- [结果变量 1 的方向与幅度，例如不良贷款率下降约 0.5-2 个百分点]
- [结果变量 2]
**效应量推理：**
- [受影响的银行比例是多少？]
- [先前银行业文献的基准效应是多少？]
- [为什么总体效应可能被稀释（如银行提前调整行为）？]

## 主要规格说明
请包含完整 Stata 代码块示例（必须）：
```stata
reghdfe outcome_var $Controls DID, absorb(bankid year) vce(cluster bankid)
```

## 结果变量
**主要变量：**[附 data.dta 中的具体列名]
**辅助变量：**[其他结果变量]

## 数据来源
1. 本地的祖父目录 DTA 数据库文件：[../../data/data.dta]
   [列出具体所需的列名]
2. [如有其他本地来源，请列出]

## 计划中的稳健性检验
1. PSM-DID 倾向得分匹配
2. 安慰剂检验（随机置换处理组）
3. 工具变量两阶段回归 (ivreg2)
4. 系统 GMM 动态面板 (xtabond2)
5. Driscoll-Kraay 标准误 (xtscc)
6. 排除竞争性银行监管政策
7. 排除特定银行样本（五大行、金融危机年份）
8. 替代度量检验

## 异质性与机制分析
**异质性：**按银行类型/规模/产权/上市状态/地区的分组分析
**机制：**风险管理渠道/信贷配置渠道/金融创新渠道

## 时间线
[潜在问题及缓解策略]"""
        return system, prompt

    @staticmethod
    def build_code_prompt(plan_content: str, code_type: str = "fetch", schema_content: str = "") -> tuple[str, str]:
        """生成 Stata 代码撰写提示词（与原始 AutoPaper 格式一致）"""
        system = (
        "你是一位专精于计量经济学分析的 Stata 编程专家。\n"
        "请编写生产级质量的 Stata 代码（.do），遵循 AutoPaper 项目的既有模式。\n"
        "【🔴 致命警告 🔴】所有脚本的正文最开头必须强制加上 `set varabbrev off` 并且独立一行！Stata 的默认变量名缩写会造成诸如 `cap drop NPL` 意外将原始数据中的 `NPLRatio` 删除引发全盘崩溃！绝不能漏掉这一句！\n"
        "代码中必须用 /* 注释 */ 或 * 注释 的形式进行中文说明。"
    )
        if code_type == "fetch":
            prompt = f"""请根据以下商业银行研究计划编写完整的 Stata 脚本（01_fetch_data.do）：

数据要求：直接从项目自带的祖父本地目录 DTA 数据库（../../data/data.dta）读取，不要爬取数据。所有路径须相对于论文目录。
{plan_content}

"""
            if schema_content:
                prompt += f"注意：请绝对严格地使用以下数据字典中提供的可用变量！严禁编造诸如 cityid 等不在字典里的列名。\n\n可用字典:\n{schema_content}\n\n"
            
            prompt += """关键要求：
0. 【🔴 致命警告 🔴】严格遵守 Stata 语法：由于我们提供的 `data.dta` 面板数据已经是包含大量成品字段的库，不要盲目 `gen` 字典里已经有的变量！如果你要构建的政策处理变量（例如 DID、Post、Treat、虚拟变量等）或者控制变量在数据字典的英文列中**已经存在**，绝对不要试图去 `gen` 它们，直接原样使用即可！如果你非要重新计算并覆盖，必须在 `gen` 之前加上 `capture drop 变量名`（比如 `cap drop DID` 然后再 `gen DID = ...`），否则立刻引发 `already defined r(110)` 导致全盘挂掉！【绝对禁令】：任何情况下使用 `cap drop`，后面只能跟**一个**变量名！绝对不允许在一行写多个变量（例如 `cap drop A B` 是违法的！必须写成 `cap drop A` 然后换行 `cap drop B`），否则只要其中一个不存在就会导致全盘删除失败！另外，处理字符串截取时必须使用 `substr()`，绝对禁止使用不存在的 `substring()` 函数引发 r(133) 崩溃！
0.5 【🔴 致命警告 🔴】绝对不允许在脚本内出现任何带有 `log using` 的代码（如 `log using "log/01...", text`），Python 会自动托管日志！擅自使用会导致 r(603) 无法打开文件的崩溃！
1. 必须使用 `use "../../data/data.dta", clear` 读取数据（因你的运行目录为论文版本级，真数据在两层父目录下）。
2. 切勿使用任何网络请求读取远程 API，所有变量需从本地提取。
3. 面板标识符应编码为 bankid（银行个体标识）和 year，使用 `xtset bankid year` 设定面板。
4. 构建银行特征控制变量：Ln_Assets（银行规模对数）、CAR（资本充足率）、NPL（不良贷款率）、ROA（总资产收益率）、NIM（净利差）、CIR（成本收入比）、LDR（存贷比）等。使用 winsor2 进行 1%/99% 缩尾处理。
4.5 【🔴 致命警告 🔴】`winsor2` 的正确语法是 `winsor2 varlist, suffix(_w) cuts(1 99)` ！绝对禁止使用 `gen()` 选项（会引发 `option gen() not allowed r(198)` 崩溃）！绝对禁止使用 `p()` 选项（正确的是 `cuts()`）！缩尾后的变量名会自动加上 `_w` 后缀（如 `lnTotalAssets_w`），然后你再用 `gen` 赋值给最终变量名即可。脚本末尾也绝对不准写 `exit 0` 或 `exit`，Stata 跑完会自动退出。
5. 构建 DID 处理变量（Treat, Post, DID = Treat * Post），如前所述，如果要生成已有名称的变量请务必先逐个 `cap drop`。
6. 构建银行分组变量：银行类型虚拟变量（国有大行/股份制/城商行/农商行）、规模分组（LargeBank）、产权分组（SOE）、上市状态（listed）。
6.5 【🔴 致命警告 🔴】Stata 严格区分大小写！数据表里的年份变量全称为小写的 `year`！严禁擅自写成首字母大写的 `Year` 或者是中文 `年` 或者是其他变体，否则立刻引发 `variable not found r(111)` 挂掉全盘！
7. 必须保存清洗后的面板数据到 `data/clean_data.dta` ( `save "data/clean_data.dta", replace` ) 。
6. 【极度重要警告】对于描述性统计文件的保存，由于你经常会擅自发明不存在的 Stata `collapse` 语法或使用 `preserve` 导致灾难性执行崩溃（如 r(198) 与 r(622) 错误）。因此现做如下绝对强制规定：
   - 绝对禁止使用 `collapse` 或任何其他复杂统计命令来生成汇总。
   - 绝对禁止使用 `preserve` 和 `restore`。
   - 你只需在数据清理完成后，不做任何加工，直接原样使用并**仅使用**这一条指令：`export delimited using "data/descriptive_stats.csv", replace`。
   - 严禁在该命令后添加 `delimiter(comma)` 、 `varnames(1)` 或其他多此一举参数。
7. 禁止在脚本末尾进行诸如“保留某一期”等自作聪明的面板结构检验，防止误 drop 或 keep 数据。
8. 脚本自包含，切勿包含 markdown 块符号如 ```stata。"""
        elif code_type == "analysis":
            prompt = f"""你的任务是：**严格按照 `04_stata_templates` 目录中已有的 Stata 分析模板**，
仅对指定变量占位符进行替换，生成可直接运行的 `03_main_analysis.do` 脚本。

以下是本研究的研究计划，你需要从中提取变量信息：
{plan_content}

"""
            if schema_content:
                prompt += f"""以下是项目数据字典，你**必须且只能**从中提取真实存在的变量名：
```
{schema_content}
```

"""
            prompt += """# 【核心任务：仅替换以下五类变量占位符，其余代码一字不改】

根据研究计划与数据字典，识别并填写以下五类变量，然后将其替换到模板对应位置：

| 变量类型 | 模板占位符 | 说明 |
|---------|-----------|------|
| **被解释变量** | `Y1`、`Y2`、`Y3` | 主因变量及备用结果变量，必须来自数据字典 |
| **核心解释变量 / 驱动变量** | `DID`（DiD 模板）或 `X`（RDD 模板） | DID 中的交乘项，或 RDD 中的连续型驱动变量，必须来自数据字典 |
| **控制变量** | `$Controls` 宏所引用的变量列表 | 全部替换为数据字典中真实存在的控制变量名，以空格分隔 |
| **中间变量（机制检验）** | 机制回归中的结果变量 | 用于检验传导渠道的中间变量，必须来自数据字典 |
| **异质性分析变量** | 按组回归中的分组变量 | 用于异质性分样本的分组标识变量，必须来自数据字典 |

---

# 【绝对禁止事项 — 违者视为任务失败】

> **🚨 最高铁律：除上述五类变量名之外，模板中的所有代码结构、命令语法、固定效应设定、输出格式等一字不得修改，也不得向模板外追加任何 Stata 语句。**

1. **禁止修改代码结构**：不得增删回归命令、`esttab` 参数、`estimates store` 格式、固定效应吸收项（`absorb(bankid year)`）、聚类标准误（`vce(cluster bankid)`）等任何非变量名部分。
2. **禁止生成模板外代码**：严禁添加模板中不存在的回归模型、稳健性检验、事件研究、`graph`/`coefplot`/`twoway` 等绘图命令、`log using` 日志命令。
3. **禁止捏造变量名**：所替换的变量名必须**逐字节**出现在上方数据字典的英文列名中；凡字典中查无此名的变量，一律不得使用，后果是 `variable not found r(111)` 全盘崩溃。
4. **禁止在 `global Controls` 或 `local controls` 宏定义列表末尾添加中文注释**：Stata 会将中文字符作为变量名吞入，导致后续回归立刻崩溃。
5. **模型名称长度**：`estimates store` 的模型名称不得超过 27 个字符（Stata 内部加前缀后总长 32）。
6. **数据加载语句唯一合法格式**：`use "data/clean_data.dta", clear`，不得使用宏路径拼接或添加 `../../`。

---

# 【输出规范】

- **只输出可直接运行的纯 Stata 代码**，不含任何 Markdown 代码块标识（如 ` ```stata `）。
- **不得输出任何解释性文字**，仅输出脚本本身。
- **必须取消注释**：模板中以 `*` 开头的回归指令（如 `* reghdfe ...`）在替换变量后，**必须去掉行首的注释符 `*`**，确保代码能被执行。
- 保留所有原模板中的中文注释，变量替换处可补充简短中文注释说明替换理由。"""
        else:
            prompt = f"""请编写 Stata 图表生成代码（05_figures.do）：
"""
            if schema_content:
                prompt += f"注意：请绝对严格地使用以下数据字典中提供的可用因变量和自变量！严禁自作主张编造诸如 green_credit、CityGDP等不在字典纯英文列名里的变量！如果你不知道因变量叫什么，请从下方的真实字典里挑！\n\n可用字典:\n{schema_content}\n\n"
            
            prompt += f"""【🔴 最高优先级红线警告 🔴】
1. 你的代码加载数据这步必须也仅仅只能写 `use "data/clean_data.dta", clear` 这一句！绝对、永远禁止擅自添加 `../` 或 `../../` 这些相对路径前缀，因为 Python 后台执行目录早就在根目录下了！
2. 绝对不允许在脚本内出现任何带有 `log using` 的代码，Python 会自动托管日志！
3. 【极度重要警告】Stata 严格区分大小写！数据表里的年份变量全称为小写的 `year`！严禁擅自写成首字母大写的 `Year` 或者是其他变体，否则立刻引发 `variable Year not found r(111)` 挂掉全盘！
4. 【极度重要警告】Stata 的多行代码换行续行符必须且只能是 `///` ，绝对、完全禁止使用单独的 `\` （反斜杠）来换行！！！使用 `\` 来续行会直接导致 `r(199) unrecognized command` 全盘崩溃！
以上红线一旦触碰直接导致致命崩溃！

根据以下研究计划：
{plan_content}

0. 【极度重要警告】严格遵守 Stata 语法：绝对禁止使用 `set graphics fontface` 这种根本不存在的语法！这会直接引发 r(198) 崩溃。绘图时请保持默认全局配置，切勿画蛇添足地修改字体、主题！
1. 强制、绝对、只能使用 `use "data/clean_data.dta", clear` 读取本地数据（严禁自己拼凑相对路径）。
2. 【毁灭级警告】由于本地数据不支持，上游的分析脚本绝对不可能做过任何“事件研究”，你也绝对不可能找到类似 `data/event_study_coefs.dta` 这种包含系数的中间文件！因此，图表阶段你必须、绝对、完全放弃所有的【事件研究图】！绝对不允许读取不存在的 coef 文件！如果有任何此类违规，脚本立刻枪毙！
3. 请只生成以下发表级质量图表（直接基于 `data/clean_data.dta` 绘制）：
   - 平行趋势图（原始均值趋势）：按处理状态分组的结果变量均值随时间变化的折线图（用 `preserve` 之后，`collapse (mean) Y变量, by(year 处理变量)` 汇总后用 `twoway connected` 画图，画完后记得 `restore`）。【血红警告】：这里的 `Y变量` 和 `处理变量` 必须是你从上方真实数据字典中一个字母不差地直接复制下来的！比如字典里如果有 `Wind绿色信贷余额百万元` 你就原样用它，绝不准自己发明 `green_loan` 这种占位符骗自己！
   - 描述性统计图表或变量间的核密度图、散点图拟合等。
4. 【毁灭级警告】与分析脚本相同，绝对不准使用任何 `log using` 会导致立刻崩溃。
5. 【绝对致命警告】图表脚本里千万、绝对不要使用 `program define` 或者自定义高级命令函数来循环画图！这种语法极易引发变量作用域和传递出错导致 `r(100) varlist required` 崩溃！请用最原始、最普通的平铺直叙方式，针对每一个因变量，老老实实地顺序写出代码即可！不要炫技！
6. 所有图表导出为图像到 figures/ 目录，例如：
`graph export "figures/01_parallel_trend.pdf", as(pdf) replace` 或 `.png`。
设置合适的 scheme（如 scheme(s2color)），字号适中。
只输出可执行代码，不要包含任何 markdown 代码块标识。"""

        return system, prompt

    @staticmethod
    def build_paper_prompt(
        plan_content: str,
        analysis_results: str = "",
    ) -> tuple[str, str]:
        """生成论文撰写提示词"""
        system = (
            "你是一位为顶级学术期刊撰写论文的经济学教授。"
            "请输出完整的中文学术论文（Markdown 格式），"
            "全文须用中文撰写。"
        )
        prompt = f"""请以 Markdown 格式撰写一篇完整的中文学术论文。

研究计划：
{plan_content}

{f'分析结果：{analysis_results}' if analysis_results else ''}

必须包含以下章节：
1. 标题与摘要（≤300 字）
2. 引言（研究动机、贡献声明、结构预览）
3. 制度背景
4. 数据（来源、变量定义、描述性统计）
5. 实证策略（模型设定、识别假设论证）
6. 主要结果（核心发现、事件研究图解读）
7. 稳健性检验（安慰剂检验、替代规格、子组分析）
8. 讨论（机制探讨、局限性）
9. 结论（总结与政策建议）
10. 参考文献

写作风格：参考 AER/AEJ 期刊水平，使用被动语态，数字精确到小数点后三位。
全文（含标题、摘要、各章节、图表说明）须用中文撰写。
【🔴 极度重要警告 🔴】对于上面“分析结果”中提供的图表，请务必在正文的合适位置（例如“主要结果”章节）使用提供的精确 Markdown 语法嵌入相关图表。不可遗漏！"""
        return system, prompt

    @staticmethod
    def build_metadata(
        paper_id: str, title: str, method: str, version: int,
        contributor: str, model: str,
    ) -> dict:
        """生成 metadata.json"""
        return {
            "paper_id": f"{paper_id}_v{version}",
            "title": title,
            "method": method,
            "policy_id": None,
            "contributor": contributor,
            "authoring_model": model,
            "published_at": datetime.now().isoformat(),
            "paper_family_id": paper_id,
            "version": version,
        }


# ============================================================
# 3. 主编排器
# ============================================================

class PaperPipeline:
    """
    单篇论文的完整生命周期编排器。

    管理从创意生成到最终发布的全部 8 个阶段，
    支持断点续传和自动错误恢复。
    """

    def __init__(
        self,
        paper_id: str,
        version: int = 1,
        model_key: str = "claude-write",
        contributor: str = "anonymous",
        policy_domain: str = "Commercial Banking",
    ):
        self.paper_id = paper_id
        self.version = version
        self.model_key = model_key
        self.contributor = contributor
        self.policy_domain = policy_domain

        self.paper_dir = PATHS.paper_dir(paper_id, version)
        self.paper_dir.mkdir(parents=True, exist_ok=True)

        # 创建标准子目录
        for subdir in ["code", "data", "figures", "tables", "output", "log", "review"]:
            (self.paper_dir / subdir).mkdir(exist_ok=True)

        self.state = PipelineState(self.paper_dir)
        self.stata_executor = StataExecutor()
        self.prompt_engine = PromptEngine()

        logger.info(f"📝 论文流水线初始化: {paper_id} v{version}")
        logger.info(f"   目录: {self.paper_dir}")
        logger.info(f"   模型: {model_key}")

    def run(self, start_from: Optional[str] = None) -> bool:
        """
        运行完整流水线。

        Args:
            start_from: 从指定阶段开始（断点续传）

        Returns:
            True if 所有阶段成功
        """
        stages = sorted(PIPELINE_STAGES.items(), key=lambda x: x[1].order)
        started = start_from is None

        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 启动论文流水线: {self.paper_id}")
        logger.info(f"{'='*60}")

        for stage_name, stage_config in stages:
            if not started:
                if stage_name == start_from:
                    started = True
                else:
                    continue

            # 检查是否已完成
            if self.state.get_stage_status(stage_name) == StageStatus.COMPLETED:
                logger.info(f"⏭️  跳过已完成阶段: {stage_config.name}")
                continue

            # 检查是否可跳过
            if stage_config.can_skip and self.state.get_stage_status(stage_name) == StageStatus.SKIPPED:
                logger.info(f"⏭️  跳过可选阶段: {stage_config.name}")
                continue

            # 检查重试次数
            if self.state.get_attempts(stage_name) >= stage_config.max_attempts:
                logger.error(
                    f"🛑 阶段 {stage_config.name} 已达最大重试次数 "
                    f"({stage_config.max_attempts})"
                )
                return False

            # 执行阶段
            logger.info(f"\n{'─'*40}")
            logger.info(f"📌 阶段 {stage_config.order}/8: {stage_config.name}")
            logger.info(f"{'─'*40}")

            self.state.set_stage_status(stage_name, StageStatus.RUNNING)

            try:
                success = self._execute_stage(stage_name, stage_config)
                if success:
                    self.state.set_stage_status(stage_name, StageStatus.COMPLETED)
                    logger.info(f"✅ 阶段完成: {stage_config.name}")
                else:
                    self.state.set_stage_status(
                        stage_name, StageStatus.FAILED,
                        error="阶段执行返回失败"
                    )
                    logger.error(f"❌ 阶段失败: {stage_config.name}")
                    return False

            except Exception as e:
                self.state.set_stage_status(
                    stage_name, StageStatus.FAILED, error=str(e)
                )
                logger.error(f"❌ 阶段异常: {stage_config.name} — {e}")
                return False

        logger.info(f"\n{'='*60}")
        logger.info(f"🎉 论文流水线完成: {self.paper_id}")
        logger.info(f"   Token 使用: {get_global_tracker().summary()}")
        logger.info(f"{'='*60}")
        return True

    def _execute_stage(self, stage_name: str, config: StageConfig) -> bool:
        """分派执行单个阶段"""
        dispatch = {
            "ideas": self._stage_ideas,
            "plan": self._stage_plan,
            "data": self._stage_data,
            "analysis": self._stage_analysis,
            "paper": self._stage_paper,
            "review": self._stage_review,
            "revision": self._stage_revision,
            "publish": self._stage_publish,
        }
        handler = dispatch.get(stage_name)
        if handler is None:
            raise ValueError(f"未知阶段: {stage_name}")
        return handler(config)

    # ---- 阶段实现 ----

    def _stage_ideas(self, config: StageConfig) -> bool:
        """阶段 1: 生成研究创意"""
        # 读取本地 data_schema.txt
        schema_path = PATHS.project_root / "data_schema.txt"
        if schema_path.exists():
            schema_text = schema_path.read_text(encoding="utf-8")
        else:
            logger.warning("未能找到 data_schema.txt，将仅使用基础提示词。")
            schema_text = ""

        # 生成创意
        system, prompt = self.prompt_engine.build_ideas_prompt(self.policy_domain, schema_text)
        generate_to_file(
            self.model_key, prompt,
            self.paper_dir / "ideas.md",
            system=system,
        )

        # 排名创意
        ideas_content = (self.paper_dir / "ideas.md").read_text(encoding="utf-8")
        system, prompt = self.prompt_engine.build_ranking_prompt(ideas_content)
        generate_to_file(
            self.model_key, prompt,
            self.paper_dir / "ideas_ranked.json",
            system=system,
            json_mode=True,
        )
        return True

    def _stage_plan(self, config: StageConfig) -> bool:
        """阶段 2: 制定研究计划"""
        import re
        raw_json_text = (self.paper_dir / "ideas_ranked.json").read_text(encoding="utf-8")
        raw_json_text = re.sub(r"^```[a-z]*\s*\n", "", raw_json_text.strip(), flags=re.IGNORECASE)
        raw_json_text = re.sub(r"\n```\s*$", "", raw_json_text.strip()).strip()

        ranked = json.loads(raw_json_text)
        ideas_content = (self.paper_dir / "ideas.md").read_text(encoding="utf-8")

        recommended_id = ranked.get("recommended", 1)
        selected_idea = f"Recommended Idea #{recommended_id}:\n{ideas_content}"

        # 读取全局 Schema
        schema_path = PATHS.project_root / "data_schema.txt"
        schema_text = schema_path.read_text(encoding="utf-8") if schema_path.exists() else ""

        # 生成初始研究计划
        system, prompt = self.prompt_engine.build_plan_prompt(selected_idea, schema_text)
        generate_to_file(
            self.model_key, prompt,
            self.paper_dir / "initial_plan.md",
            system=system,
        )

        # 复制为 research_plan.md（可演进版本）
        shutil.copy2(
            self.paper_dir / "initial_plan.md",
            self.paper_dir / "research_plan.md",
        )
        return True

    def _stage_data(self, config: StageConfig) -> bool:
        """阶段 3: 生成数据获取代码并执行"""
        plan = (self.paper_dir / "research_plan.md").read_text(encoding="utf-8")

        # 读取全局 Schema
        schema_path = PATHS.project_root / "data_schema.txt"
        schema_text = schema_path.read_text(encoding="utf-8") if schema_path.exists() else ""

        # 生成 Stata 代码（如果已存在则跳过，以支持手动修复后恢复运行）
        fetch_code_path = self.paper_dir / "code" / "01_fetch_data.do"
        if fetch_code_path.exists() and fetch_code_path.stat().st_size > 0:
            logger.info("⏭️  数据获取脚本已存在，跳过重新生成: 01_fetch_data.do")
        else:
            system, prompt = self.prompt_engine.build_code_prompt(plan, "fetch", schema_text)
            generate_to_file(
                self.model_key, prompt,
                fetch_code_path,
                system=system,
            )

        # 复制 packages 模板
        pkg_template = PATHS.stata_templates_dir / "00_packages.do"
        if pkg_template.exists():
            shutil.copy2(pkg_template, self.paper_dir / "code" / "00_packages.do")

        # 执行 Stata 脚本
        result = self.stata_executor.execute(
            "code/01_fetch_data.do",
            self.paper_dir,
            timeout_minutes=config.timeout_minutes,
        )
        if not result.success:
            if self.stata_executor.available:
                logger.error("❌ 数据获取 Stata 脚本执行失败。")
                return False
            else:
                logger.warning("⚠️ 数据获取 Stata 脚本未执行（Stata 不可用），但代码已生成。")

        return True

    def _stage_analysis(self, config: StageConfig) -> bool:
        """阶段 4: 生成分析代码并执行"""
        plan = (self.paper_dir / "research_plan.md").read_text(encoding="utf-8")

        # 读取全局 Schema
        schema_path = PATHS.project_root / "data_schema.txt"
        schema_text = schema_path.read_text(encoding="utf-8") if schema_path.exists() else ""

        # 读取 method 模板
        import json
        metadata_file = self.paper_dir / "metadata.json"
        method = "did"
        if metadata_file.exists():
            method_str = json.loads(metadata_file.read_text(encoding="utf-8")).get("method", "did").lower()
            if "did" in method_str: method = "did"
            elif "rdd" in method_str: method = "rdd"
            elif "iv" in method_str: method = "iv"
            elif "synth" in method_str: method = "synth"
            else: method = "did"
        template_file = PATHS.stata_templates_dir / f"03_main_analysis_{method}.do"
        template_text = template_file.read_text(encoding="utf-8") if template_file.exists() else ""
        plan_with_template = f"{plan}\n\n==== Stata 分析模板 ====\n{template_text}"

        # 生成分析代码（如果已存在则跳过，以支持手动修复后恢复运行）
        analysis_code_path = self.paper_dir / "code" / "03_main_analysis.do"
        if analysis_code_path.exists() and analysis_code_path.stat().st_size > 0:
            logger.info("⏭️  分析脚本已存在，跳过重新生成: 03_main_analysis.do")
        else:
            system, prompt = self.prompt_engine.build_code_prompt(plan_with_template, "analysis", schema_text)
            generate_to_file(
                self.model_key, prompt,
                analysis_code_path,
                system=system,
            )

        # 生成图表代码（如果已存在则跳过）
        figures_code_path = self.paper_dir / "code" / "05_figures.do"
        if figures_code_path.exists() and figures_code_path.stat().st_size > 0:
            logger.info("⏭️  图表脚本已存在，跳过重新生成: 05_figures.do")
        else:
            system, prompt = self.prompt_engine.build_code_prompt(plan, "figures")
            generate_to_file(
                self.model_key, prompt,
                figures_code_path,
                system=system,
            )

        # 执行 Stata 脚本
        result = self.stata_executor.execute(
            "code/03_main_analysis.do",
            self.paper_dir,
            timeout_minutes=config.timeout_minutes,
        )
        if not result.success:
            if self.stata_executor.available:
                logger.error("❌ 分析 Stata 脚本执行失败。")
                return False
            else:
                logger.warning("⚠️ 分析 Stata 脚本未执行（Stata 不可用），但代码已生成。")

        # 执行图表生成
        fig_result = self.stata_executor.execute(
            "code/05_figures.do",
            self.paper_dir,
            timeout_minutes=15,
        )
        if not fig_result.success:
            if self.stata_executor.available:
                logger.error("❌ 图表 Stata 脚本执行失败。")
                return False
            else:
                logger.warning("⚠️ 图表 Stata 脚本未执行，但代码已生成。")

        return True

    def _stage_paper(self, config: StageConfig) -> bool:
        """阶段 5: 撰写论文"""
        plan = (self.paper_dir / "research_plan.md").read_text(encoding="utf-8")

        # 收集分析结果（CSV 汇总表 + RDS 描述 + 控制台日志）
        analysis_results = ""

        # 读取 CSV 汇总表 (存放在 tables 中)
        for csv_file in (self.paper_dir / "tables").glob("*.csv"):
            try:
                content = csv_file.read_text(encoding="utf-8", errors="ignore")
                if len(content) > 5000:
                    content = content[:5000] + "\n... (Content truncated due to length) ..."
                analysis_results += f"\n=== {csv_file.name} ===\n{content}\n"
            except Exception:
                pass

        # 读取 output/ 中的任何文本文件
        for txt_file in (self.paper_dir / "output").glob("*"):
            if txt_file.suffix in (".txt", ".csv", ".log"):
                try:
                    content = txt_file.read_text(encoding="utf-8", errors="ignore")
                    if len(content) > 5000:
                        content = content[:5000] + "\n... (Content truncated due to length) ..."
                    analysis_results += f"\n=== {txt_file.name} ===\n{content}\n"
                except Exception:
                    pass

        # 列出可用的 dta 数据文件
        dta_files = list((self.paper_dir / "data").glob("*.dta"))
        if dta_files:
            analysis_results += "\n=== Available Data Files ===\n"
            for f in dta_files:
                analysis_results += f"- {f.name} ({f.stat().st_size / 1024:.1f} KB)\n"
        elif not self.stata_executor.available:
            analysis_results += "\n⚠️ 注意：尚未执行分析代码（缺少 Stata），未能获取真实结果。请根据常识和预期的理论方向撰写正文内容的占位符。\n"

        # 列出可用的图表
        fig_files = list((self.paper_dir / "figures").glob("*"))
        if fig_files:
            analysis_results += "\n=== Available Figures ===\n"
            for f in fig_files:
                img_md = f"![{f.stem}](figures/{f.name})"
                analysis_results += f"- {f.name} (请使用此确切的Markdown引用代码: `{img_md}`)\n"

        system, prompt = self.prompt_engine.build_paper_prompt(plan, analysis_results)
        generate_to_file(
            self.model_key, prompt,
            self.paper_dir / "paper.md",
            system=system,
            max_tokens=32768,
        )

        # 补全丢失的图表 (自动兜底)
        self._ensure_figures_in_paper(self.paper_dir / "paper.md")
        return True

    def _stage_review(self, config: StageConfig) -> bool:
        """阶段 6: 多模型同行评审（委托给 review_pipeline）"""
        # 动态导入以避免循环依赖
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "10_review_pipeline"))
        from review_pipeline import ReviewPipeline

        pipeline = ReviewPipeline(self.paper_dir)
        result = pipeline.run_review()
        return result.get("status") != "error"

    def _stage_revision(self, config: StageConfig) -> bool:
        """阶段 7: 根据评审意见修订论文"""
        round_num = self.state.revision_round + 1

        # 收集所有评审文件
        reviews = []
        for review_file in (self.paper_dir / "review").glob("review_*.md"):
            reviews.append(review_file.read_text(encoding="utf-8"))

        if not reviews:
            logger.info("ℹ️  无评审意见，跳过修订阶段")
            return True

        combined_reviews = "\n\n---\n\n".join(reviews)
        paper_content = (self.paper_dir / "paper.md").read_text(encoding="utf-8")

        # Step 1: 生成修订计划
        system = "你是一位正在制定系统修订计划的资深经济学家。请用中文回复所有内容。"
        prompt = f"""请根据以下评审意见制定系统修订计划。

评审意见：
{combined_reviews}

论文（前 4000 字）：
{paper_content[:4000]}

输出 revision_plan_{round_num}.md，包含：
1. 每位评审人主要关切的汇总
2. 行动项目表（| 编号 | 评审人 | 问题 | 优先级 | 建议修改 |）
3. 需要新增的分析清单
4. 评审回复草稿"""

        generate_to_file(
            self.model_key, prompt,
            self.paper_dir / "review" / f"revision_plan_{round_num}.md",
            system=system,
        )

        generate_to_file(
            self.model_key,
            f"请根据以下评审意见撰写正式的逐条回复（用中文）：\n{combined_reviews}",
            self.paper_dir / "review" / f"reply_to_reviewers_{round_num}.md",
            system="你正在为学术审稿人撰写逐条回复。请用中文回复所有内容。",
        )

        # Step 3: 重写论文（关键修复：原始项目评审后会更新 paper.md）
        revision_plan = (self.paper_dir / "review" / f"revision_plan_{round_num}.md").read_text(encoding="utf-8")
        system = (
            "你是一位根据审稿人意见修订论文的经济学教授。"
            "请输出完整的修订后 Markdown 文档，全文用中文撰写。"
        )
        prompt = f"""请根据评审反馈和修订计划对本论文进行修订。

原始论文：
{paper_content}

修订计划：
{revision_plan}

请输出完整的修订后 paper.md，纳入所有修改。
在 Markdown 中用 <!-- 修订 --> 注释标记重大改动。
【🔴 极度重要警告 🔴】在修订过程中，务必保留原版论文中的所有 Markdown 图片嵌入链接（如 `![...](figures/...)`），绝对不可删减图表！"""

        generate_to_file(
            self.model_key, prompt,
            self.paper_dir / "paper.md",
            system=system,
            max_tokens=32768,
        )

        import shutil
        shutil.copy2(
            self.paper_dir / "paper.md",
            self.paper_dir / "review" / f"paper_revised_{round_num}.md"
        )

        # 补全丢失的图表 (兜底大模型幻觉删减)
        self._ensure_figures_in_paper(self.paper_dir / "paper.md")
        self._ensure_figures_in_paper(self.paper_dir / "review" / f"paper_revised_{round_num}.md")

        self.state.increment_revision()
        logger.info(f"✅ 修订完成 (Round {round_num}): paper.md 已更新")
        return True

    def _stage_publish(self, config: StageConfig) -> bool:
        """阶段 8: 发布"""
        # 生成 metadata.json
        title = self._extract_title()
        method = self._detect_method()

        metadata = self.prompt_engine.build_metadata(
            paper_id=self.paper_id,
            title=title,
            method=method,
            version=self.version,
            contributor=self.contributor,
            model=AUTHORING_MODELS[self.model_key].model_id,
        )
        (self.paper_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        # 生成 REPLICATION.md
        generate_to_file(
            self.model_key,
            f"Generate REPLICATION.md for paper {self.paper_id} "
            f"with Stata code files (00_packages.do through 08_further_analysis.do) in code/ directory. "
            f"This is a commercial banking research paper using bank-level panel data.",
            self.paper_dir / "REPLICATION.md",
            system="Generate a replication guide in markdown format for a commercial banking research paper using Stata.",
        )

        # 运行质量扫描
        self._quality_scan()

        logger.info(f"📦 论文已发布: {self.paper_id} v{self.version}")
        return True

    def _ensure_figures_in_paper(self, paper_path: Path):
        """自动巡检并补全 paper.md 中遗漏的图表（后处理兜底）"""
        if not paper_path.exists():
            return
        
        figures_dir = self.paper_dir / "figures"
        if not figures_dir.exists():
            return
            
        fig_files = list(figures_dir.glob("*"))
        if not fig_files:
            return
            
        content = paper_path.read_text(encoding="utf-8", errors="ignore")
        missing_figs = []
        for f in fig_files:
            # 简单检查引用，不论是确切的相对路径还是仅文件名
            if f.name not in content:
                md_code = f"![{f.stem}](figures/{f.name})"
                missing_figs.append(md_code)
                
        if missing_figs:
            logger.warning(f"⚠️ 发现 {paper_path.name} 遗漏了 {len(missing_figs)} 个图表，正在文末自动追加。")
            append_content = "\n\n## 附录：图表\n\n" + "\n\n".join(missing_figs) + "\n"
            
            with open(paper_path, "a", encoding="utf-8") as f:
                f.write(append_content)

    # ---- 辅助方法 ----

    def _extract_title(self) -> str:
        """从 paper.md 提取标题"""
        md_file = self.paper_dir / "paper.md"
        if md_file.exists():
            content = md_file.read_text(encoding="utf-8")
            import re
            match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
            if match:
                return match.group(1).replace("\n", " ").strip()
        return "Untitled"

    def _detect_method(self) -> str:
        """检测使用的研究方法"""
        plan_file = self.paper_dir / "research_plan.md"
        if plan_file.exists():
            content = plan_file.read_text(encoding="utf-8").lower()
            if "difference-in-differences" in content or "did" in content:
                return "DiD"
            elif "regression discontinuity" in content or "rdd" in content:
                return "RDD"
            elif "doubly robust" in content:
                return "DR"
        return "Unknown"



    def _quality_scan(self):
        """运行质量扫描"""
        required_files = [
            "paper.md", "metadata.json", "initial_plan.md",
            "research_plan.md", "ideas.md",
        ]
        scan = {
            "paper_id": self.paper_id,
            "version": self.version,
            "scanned_at": datetime.now().isoformat(),
            "checks": {},
            "overall": "pass",
        }

        for f in required_files:
            exists = (self.paper_dir / f).exists()
            scan["checks"][f] = "pass" if exists else "fail"
            if not exists:
                scan["overall"] = "fail"

        # 检查代码目录
        code_files = list((self.paper_dir / "code").glob("*.do"))
        scan["checks"]["code_scripts"] = len(code_files)
        scan["checks"]["has_fetch_data"] = (self.paper_dir / "code" / "01_fetch_data.do").exists()
        scan["checks"]["has_analysis"] = (self.paper_dir / "code" / "03_main_analysis.do").exists()

        # 检查图表
        figures = list((self.paper_dir / "figures").glob("*"))
        scan["checks"]["figure_count"] = len(figures)

        (self.paper_dir / "scan_report.json").write_text(
            json.dumps(scan, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        logger.info(f"📊 质量扫描: {scan['overall'].upper()}")


# ============================================================
# 4. CLI 入口
# ============================================================

def main():
    """命令行入口"""
    import argparse
    parser = argparse.ArgumentParser(description="AutoPaper 论文流水线编排器")
    parser.add_argument("paper_num", type=int, help="论文编号（如 500）")
    parser.add_argument("--version", type=int, default=1, help="版本号")
    parser.add_argument("--model", default="claude-write", help="撰写模型 key")
    parser.add_argument("--contributor", default="anonymous", help="贡献者")
    parser.add_argument("--domain", default="Commercial Banking", help="政策领域")
    parser.add_argument("--resume-from", default=None, help="从指定阶段恢复")

    args = parser.parse_args()

    paper_id = f"paper_{args.paper_num:04d}"

    pipeline = PaperPipeline(
        paper_id=paper_id,
        version=args.version,
        model_key=args.model,
        contributor=args.contributor,
        policy_domain=args.domain,
    )

    success = pipeline.run(start_from=args.resume_from)
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
