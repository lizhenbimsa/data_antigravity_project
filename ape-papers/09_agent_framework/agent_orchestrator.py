# -*- coding: utf-8 -*-
"""
APEP 生产基础设施 — 主编排器（Agent Orchestrator）
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
from r_executor import RExecutor, STANDARD_R_PIPELINE

logger = setup_logging("apep.orchestrator")


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
    def build_ideas_prompt(policy_domain: str = "labor economics") -> tuple[str, str]:
        """生成创意生成阶段的提示词（含 DiD/RDD 可行性评估表）"""
        system = (
            "你是一位专注于政策评估的资深计量经济学家。"
            "你提出的研究创意须符合最高因果识别标准，适合发表于顶级经济学期刊（AER/AEJ 级别）。"
            "你始终包含具体的可行性评估。请用中文回复所有内容。"
        )
        prompt = f"""请为以下政策评估领域生成 5 个自主政策评估研究创意：{policy_domain}。

每个创意须满足：
1. 使用双重差分法（DiD，交错州级实施）或断点回归（RDD，年龄/收入/分数阈值）
2. 数据须可从公共 API 免费获取（Census ACS REST API、BLS、FRED）
3. 因果识别策略须具有可信度
4. 包含具体可行性评估表

每个创意须严格遵循以下结构：

## 创意 N：[标题]
**政策：**[政策名称及实施时间]

各州实施时间（列出所有州及年份）。

**结果变量：**[具体结果变量及 API 变量代码]

**识别策略：**[DiD/RDD 策略及详细论证]

**创新性：**[2-3 句说明文献空白]

**可行性检验：**
- 变异性：[处理州数量 N，对照州数量 N]
- 数据可访问性：[确认 API 端点有效]
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

请避免：最低工资对就业的基本效果、ACA 对保险覆盖的基本效果、基础枪支管制研究。
请确保每个创意都有明确定义的处理组和对照组。"""
        return system, prompt

    @staticmethod
    def build_ranking_prompt(ideas_content: str) -> tuple[str, str]:
        """生成创意排名提示词"""
        system = "你是一位正在评估研究提案的经济学期刊编辑。请用中文填写所有文本字段，仅输出合法 JSON。"
        prompt = f"""请对以下研究创意进行排名和评分。仅输出合法 JSON，不要添加任何其他文本。

{ideas_content}

对每个创意在四个维度上评分（0-10）：
- originality：是否填补了文献空白？
- feasibility：数据是否真实可获取？API 是否稳定？
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
    def build_plan_prompt(selected_idea: str) -> tuple[str, str]:
        """生成研究计划提示词（含完整 R 代码规范和效应量推理）"""
        system = (
            "你是一位正在撰写预分析计划的资深计量经济学家。"
            "你的计划须足够详细，以便其他研究者无需额外指导即可复现该研究。"
            "请包含完整的 R 代码规范和效应量推理。请用中文回复所有内容。"
        )
        prompt = f"""请为以下研究创意撰写详细的初始研究计划（initial_plan.md）：

{selected_idea}

计划须包含以下所有部分：

## 研究问题
[清晰、可检验的因果命题]

## 背景
[政策详情、时间线，列出所有实施州及年份]

## 识别策略
**设计：**[交错 DiD / 精确 RDD]
**处理：**[精确定义]
**对照：**[精确定义]
**估计量：**Callaway-Sant'Anna（2021）组-时间 ATT 估计量
**平行趋势假设：**[为什么可信——至少 3 个论点]

## 预期效应与机制
**主要机制：**[政策如何影响结果变量]
**预期效应：**
- [结果变量 1 的方向与幅度，例如约 0.5-2 个百分点]
- [结果变量 2]
**效应量推理：**
- [受影响的人口比例是多少？]
- [先前文献的基准效应是多少？]
- [为什么总体效应会被稀释？]

## 主要规格说明
请包含完整 R 代码块：
```r
library(did)
att_gt <- att_gt(
  yname = "outcome_var",
  tname = "year",
  idname = "state_fips",
  gname = "treat_year",
  data = panel_data,
  control_group = "nevertreated",
  anticipation = 0,
  base_period = "universal"
)
att_overall <- aggte(att_gt, type = "simple")
att_event <- aggte(att_gt, type = "dynamic")
```

## 结果变量
**主要变量：**[附 Census ACS 变量代码，如 B23025_004E]
**辅助变量：**[其他结果变量]

## 数据来源
1. Census ACS 1-Year：https://api.census.gov/data/YEAR/acs/acs1
   [列出具体变量代码]
2. [如有其他来源，请列出]

## 计划中的稳健性检验
1. 替代估计量（Sun-Abraham via fixest::sunab，did2s）
2. 平行趋势敏感性分析（HonestDiD 界）
3. 安慰剂检验（虚假处理时间）
4. 替代对照组（未被处理组）
5. 子组分析

## 时间线
[潜在问题及缓解策略]"""
        return system, prompt

    @staticmethod
    def build_code_prompt(plan_content: str, code_type: str = "fetch") -> tuple[str, str]:
        """生成 R 代码撰写提示词（与原始 ape-papers 格式一致）"""
        system = (
            "你是一位专精于计量经济学分析的 R 编程专家。"
            "请编写生产级质量的 R 代码，遵循 ape-papers 项目的既有模式。"
            "API 调用使用 httr + jsonlite。所有路径须相对于论文目录。"
            "代码注释请用中文撰写。"
        )
        if code_type == "fetch":
            prompt = f"""请根据以下研究计划编写完整的 R 脚本（01_fetch_data.R）：

{plan_content}

关键要求：
1. 使用 httr::GET() + jsonlite::fromJSON() 直接调用 Census ACS REST API
   （不要使用 tidycensus，使用原始 API 调用，代码样例如下：
    url <- sprintf("https://api.census.gov/data/%d/acs/acs1?get=NAME,B23025_004E&for=state:*", year)
    resp <- GET(url)
    content_json <- fromJSON(content(resp, as="text", encoding="UTF-8"))
    df <- as_tibble(content_json[-1, ], .name_repair="minimal")
    colnames(df) <- content_json[1, ]
    # 务必先重命名所需的列，然后再进行 as.numeric 类型转换！例如：
    # df <- df %>% rename(employed = B23025_004E, state_fips = state) %>% mutate(across(c(employed), as.numeric))
   ）
2. 循环获取 2010-2023 年的数据，每年单独获取（若某年数据获取失败或状态码不为200，请发出警告并严格使用 next 跳过，绝不能使用 stop() 中断整个程序）
3. 包含完整的州 FIPS 到州缩写映射（全部 51 个）
4. 将处理时间定义为包含 state_fips 和 treat_year 的 tibble
5. 构建包含以下变量的面板数据：cohort（从未处理的 cohort 请设为 Inf，切勿使用不存在的 Inf_real_）、post、treated、rel_time
6. 计算比率：emp_rate、lfp_rate、unemp_rate
7. 添加 2019 年人口权重（state_pop）
8. 使用 cat() 信息进行数据质量检查
9. 保存到 data/panel_data.rds
10. 保存描述性统计到 data/descriptive_stats.csv
11. 脚本以 source("code/00_packages.R") 开头

脚本须自包含，无需任何 API 密钥即可运行。所有注释用中文撰写。"""
        elif code_type == "analysis":
            prompt = f"""请编写完整的 R 分析脚本（03_main_analysis.R）：

{plan_content}

严格遵循以下结构：
1. source("code/00_packages.R")
2. panel_data <- readRDS("data/panel_data.rds")
   （非常重要：绝对不要在此脚本中再次构造政策生效年份表或进行 left_join！panel_data中已经有完整的 treat_year、cohort、post 和 treated 变量，直接使用即可。否则会引发变量名冲突和找不到变量的报错！）
3. 打印样本描述（州、年份、观测数、处理情况汇总）
4. 打印基准描述性统计（2019 年，按处理状态分组）

5. TWFE 估计（fixest::feols）：
   - emp_rate ~ post | state_fips + year, cluster = ~state_fips
   - lfp_rate ~ post | state_fips + year

6. Sun-Abraham 估计（fixest::sunab）：
   - emp_rate ~ sunab(cohort, year, ref.p = -1) | state_fips + year
   - lfp_rate、unemp_rate 类似
   - 获取 ATT：使用 agg_attX <- aggregate(sa_emp, agg = "ATT")
   - （极其重要：在提取 ATT 汇总结果构造 summary_table 时，提取估计值和标准误请强行转化为 data.frame 然后使用 df$Estimate 和 df$`Std. Error` 或类似常见列名，绝对禁止使用 $att.egt, $se.egt 等 `did` 包的特有字段名字来截取！）

7. 事件研究系数提取：
   - agg_att_emp <- aggregate(sa_emp, agg = "ATT")
   - lfp 和 unemp 同理

8. 事件研究系数：
   - 通过 coeftable() + filter(grepl("year::", term)) 提取
   - 重命名列：estimate、se、pval
   - 从 term 名称计算 rel_time

9. 预趋势检验：
   - 筛选 rel_time < 0，统计显著的处理前期系数数量

10. 保存结果：
    - saveRDS(results, "data/main_results.rds")
    - 包含 ATT、SE、95% CI、显著性的汇总表
    - write_csv(summary_table, "data/main_results_summary.csv")

所有回归使用州级聚类标准误。所有注释用中文撰写。"""
        else:
            prompt = f"""请编写 R 图表生成代码（05_figures.R）：

{plan_content}

生成以下发表级质量图表：
1. 事件研究图（ggplot2）：系数及 95% CI，t=0 处加竖线
2. 平行趋势图：按处理状态分组的结果变量均值随时间变化
3. 处理实施分布图或地图
4. 跨估计量的系数对比图

务必首先读取此前保存的数据分析结果和基础面板数据：
```r
panel_data <- readRDS("data/panel_data.rds")
results <- readRDS("data/main_results.rds")
```
使用 `results` 中对应的对象（如 `results$event_study$emp`，`results$agg_att`，`results$sunab`等）提取系数，以及 `panel_data` 中的数据作图。不要假设环境变量自动存在。

所有图表保存为 PDF 到 figures/ 目录，例如 figures/01_event_study.pdf。
使用 theme_minimal() 或 theme_bw()，字号 >= 12pt。
以 source("code/00_packages.R") 开头。所有注释用中文撰写。只输出可执行代码，不要包含任何 markdown 代码块标识。"""

        return system, prompt

    @staticmethod
    def build_paper_prompt(
        plan_content: str,
        analysis_results: str = "",
    ) -> tuple[str, str]:
        """生成论文撰写提示词"""
        system = (
            "你是一位为顶级学术期刊撰写论文的经济学教授。"
            "请输出完整的中文学术论文（LaTeX 格式），使用 ctexart 文档类以支持中文，"
            "12pt 字体，双倍行距，booktabs 表格。全文须用中文撰写。"
        )
        prompt = f"""请以 LaTeX 格式撰写一篇完整的中文学术论文。

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

LaTeX 文档头部须使用：
\\documentclass[UTF8,12pt,notitlepage]{{ctexart}}
\\usepackage{{setspace}}
\\doublespacing

写作风格：参考 AER/AEJ 期刊水平，使用被动语态，数字精确到小数点后三位。
全文（含标题、摘要、各章节、图表说明）须用中文撰写。
特别注意：严禁第一页出现空白页！请确保 \\maketitle 和 \\begin{{abstract}} 之间不要使用 \\newpage 或 \\clearpage 等强制换页符。"""
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
        policy_domain: str = "labor economics",
    ):
        self.paper_id = paper_id
        self.version = version
        self.model_key = model_key
        self.contributor = contributor
        self.policy_domain = policy_domain

        self.paper_dir = PATHS.paper_dir(paper_id, version)
        self.paper_dir.mkdir(parents=True, exist_ok=True)

        # 创建标准子目录
        for subdir in ["code", "data", "figures", "tables", "output"]:
            (self.paper_dir / subdir).mkdir(exist_ok=True)

        self.state = PipelineState(self.paper_dir)
        self.r_executor = RExecutor()
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
        # 生成创意
        system, prompt = self.prompt_engine.build_ideas_prompt(self.policy_domain)
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

        # 生成初始研究计划
        system, prompt = self.prompt_engine.build_plan_prompt(selected_idea)
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

        # 生成 R 代码
        system, prompt = self.prompt_engine.build_code_prompt(plan, "fetch")
        generate_to_file(
            self.model_key, prompt,
            self.paper_dir / "code" / "01_fetch_data.R",
            system=system,
        )

        # 复制 packages 模板
        pkg_template = PATHS.r_templates_dir / "00_packages.R"
        if pkg_template.exists():
            shutil.copy2(pkg_template, self.paper_dir / "code" / "00_packages.R")

        # 执行 R 脚本
        result = self.r_executor.execute(
            "code/01_fetch_data.R",
            self.paper_dir,
            timeout_minutes=config.timeout_minutes,
        )
        if not result.success:
            if self.r_executor.available:
                logger.error("❌ 数据获取 R 脚本执行失败。")
                return False
            else:
                logger.warning("⚠️ 数据获取 R 脚本未执行（R 不可用），但代码已生成。")

        return True

    def _stage_analysis(self, config: StageConfig) -> bool:
        """阶段 4: 生成分析代码并执行"""
        plan = (self.paper_dir / "research_plan.md").read_text(encoding="utf-8")

        # 生成分析代码
        system, prompt = self.prompt_engine.build_code_prompt(plan, "analysis")
        generate_to_file(
            self.model_key, prompt,
            self.paper_dir / "code" / "03_main_analysis.R",
            system=system,
        )

        # 生成图表代码
        system, prompt = self.prompt_engine.build_code_prompt(plan, "figures")
        generate_to_file(
            self.model_key, prompt,
            self.paper_dir / "code" / "05_figures.R",
            system=system,
        )

        # 执行 R 脚本
        result = self.r_executor.execute(
            "code/03_main_analysis.R",
            self.paper_dir,
            timeout_minutes=config.timeout_minutes,
        )
        if not result.success:
            if self.r_executor.available:
                logger.error("❌ 分析 R 脚本执行失败。")
                return False
            else:
                logger.warning("⚠️ 分析 R 脚本未执行（R 不可用），但代码已生成。")

        # 执行图表生成
        fig_result = self.r_executor.execute(
            "code/05_figures.R",
            self.paper_dir,
            timeout_minutes=15,
        )
        if not fig_result.success:
            if self.r_executor.available:
                logger.error("❌ 图表 R 脚本执行失败。")
                return False
            else:
                logger.warning("⚠️ 图表 R 脚本未执行，但代码已生成。")

        return True

    def _stage_paper(self, config: StageConfig) -> bool:
        """阶段 5: 撰写论文"""
        plan = (self.paper_dir / "research_plan.md").read_text(encoding="utf-8")

        # 收集分析结果（CSV 汇总表 + RDS 描述 + 控制台日志）
        analysis_results = ""

        # 读取 CSV 汇总表
        for csv_file in (self.paper_dir / "data").glob("*.csv"):
            try:
                content = csv_file.read_text(encoding="utf-8", errors="ignore")
                analysis_results += f"\n=== {csv_file.name} ===\n{content}\n"
            except Exception:
                pass

        # 读取 output/ 中的任何文本文件
        for txt_file in (self.paper_dir / "output").glob("*"):
            if txt_file.suffix in (".txt", ".csv", ".log"):
                try:
                    content = txt_file.read_text(encoding="utf-8", errors="ignore")
                    analysis_results += f"\n=== {txt_file.name} ===\n{content}\n"
                except Exception:
                    pass

        # 列出可用的 RDS 数据文件
        rds_files = list((self.paper_dir / "data").glob("*.rds"))
        if rds_files:
            analysis_results += "\n=== Available RDS Data Files ===\n"
            for f in rds_files:
                analysis_results += f"- {f.name} ({f.stat().st_size / 1024:.1f} KB)\n"

        # 列出可用的图表
        fig_files = list((self.paper_dir / "figures").glob("*"))
        if fig_files:
            analysis_results += "\n=== Available Figures ===\n"
            for f in fig_files:
                analysis_results += f"- {f.name}\n"

        system, prompt = self.prompt_engine.build_paper_prompt(plan, analysis_results)
        generate_to_file(
            self.model_key, prompt,
            self.paper_dir / "paper.tex",
            system=system,
            max_tokens=32768,
        )
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
        for review_file in self.paper_dir.glob("review_*.md"):
            reviews.append(review_file.read_text(encoding="utf-8"))

        if not reviews:
            logger.info("ℹ️  无评审意见，跳过修订阶段")
            return True

        combined_reviews = "\n\n---\n\n".join(reviews)
        paper_content = (self.paper_dir / "paper.tex").read_text(encoding="utf-8")

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
            self.paper_dir / f"revision_plan_{round_num}.md",
            system=system,
        )

        # Step 2: 生成评审回复
        generate_to_file(
            self.model_key,
            f"请根据以下评审意见撰写正式的逐条回复（用中文）：\n{combined_reviews}",
            self.paper_dir / f"reply_to_reviewers_{round_num}.md",
            system="你正在为学术审稿人撰写逐条回复。请用中文回复所有内容。",
        )

        # Step 3: 重写论文（关键修复：原始项目评审后会更新 paper.tex）
        revision_plan = (self.paper_dir / f"revision_plan_{round_num}.md").read_text(encoding="utf-8")
        system = (
            "你是一位根据审稿人意见修订论文的经济学教授。"
            "请输出完整的修订后 LaTeX 文档，全文用中文撰写，使用 ctexart 文档类。"
        )
        prompt = f"""请根据评审反馈和修订计划对本论文进行修订。

原始论文：
{paper_content}

修订计划：
{revision_plan}

请输出完整的修订后 paper.tex，纳入所有修改。
在 LaTeX 中用 %% 修订 注释标记重大改动。"""

        generate_to_file(
            self.model_key, prompt,
            self.paper_dir / "paper.tex",
            system=system,
            max_tokens=32768,
        )

        self.state.increment_revision()
        logger.info(f"✅ 修订完成 (Round {round_num}): paper.tex 已更新")
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
            f"with R code files in code/ directory.",
            self.paper_dir / "REPLICATION.md",
            system="Generate a replication guide in markdown format.",
        )

        # 编译 PDF（尝试）
        self._compile_latex()

        # 运行质量扫描
        self._quality_scan()

        logger.info(f"📦 论文已发布: {self.paper_id} v{self.version}")
        return True

    # ---- 辅助方法 ----

    def _extract_title(self) -> str:
        """从 paper.tex 提取标题"""
        tex_file = self.paper_dir / "paper.tex"
        if tex_file.exists():
            content = tex_file.read_text(encoding="utf-8")
            import re
            match = re.search(r"\\title\{([^}]+)\}", content)
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

    def _find_xelatex(self) -> str:
        """自动探测 xelatex 可执行文件路径"""
        import shutil

        # 1. 优先从当前 PATH 查找
        found = shutil.which("xelatex")
        if found:
            return found

        # 2. 扫描 Windows 常见安装目录（MiKTeX / TeX Live）
        import os, glob
        candidate_patterns = [
            r"C:\Users\*\AppData\Local\Programs\MiKTeX*\miktex\bin\x64\xelatex.exe",
            r"C:\Users\*\AppData\Local\Programs\MiKTeX*\miktex\bin\xelatex.exe",
            r"C:\Program Files\MiKTeX*\miktex\bin\x64\xelatex.exe",
            r"C:\Program Files\MiKTeX*\miktex\bin\xelatex.exe",
            r"C:\texlive\*\bin\win32\xelatex.exe",
            r"C:\texlive\*\bin\windows\xelatex.exe",
        ]
        for pattern in candidate_patterns:
            matches = glob.glob(pattern)
            if matches:
                logger.info(f"🔍 找到 xelatex: {matches[0]}")
                return matches[0]

        return "xelatex"  # 回退，让 subprocess 自己报错

    def _compile_latex(self):
        """尝试编译 LaTeX"""
        import subprocess
        import re

        tex_file = self.paper_dir / "paper.tex"
        if not tex_file.exists():
            return

        # ---- 图片缺失保护机制 ----
        content = tex_file.read_text(encoding="utf-8")
        # 匹配 \includegraphics[可选]{文件名} 或 \includegraphics{文件名}
        # 并在文件不存在时注释掉该命令以免 pdf 编译 Fatal Error
        def img_replacer(match):
            full_match = match.group(0)
            img_filename = match.group(1)
            # 解决如果有引号或者空格包裹的情况
            clean_filename = img_filename.strip().strip('"\'')
            img_path = self.paper_dir / clean_filename
            if not img_path.exists():
                logger.warning(f"⚠️ 屏蔽缺失的图片引用: {clean_filename}")
                return f"% [Missing Figure: {clean_filename}]\n% {full_match}"
            return full_match

        new_content = re.sub(r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}', img_replacer, content)

        # ---- 空白页清理机制 ----
        # 1. 强制在 ctexart 类中添加 notitlepage
        new_content = re.sub(r'\\documentclass\[(.*?)\]\{ctexart\}', 
                             lambda m: f'\\documentclass[{m.group(1)},notitlepage]{{ctexart}}' if 'notitlepage' not in m.group(1) else m.group(0), 
                             new_content)
        # 2. 移除 \maketitle 到第一个 \section 之间的 \newpage 和 \clearpage
        mt_idx = new_content.find(r'\maketitle')
        sec_idx = new_content.find(r'\section', mt_idx) if mt_idx != -1 else -1
        if mt_idx != -1 and sec_idx != -1:
            prefix = new_content[:mt_idx]
            middle = new_content[mt_idx:sec_idx]
            suffix = new_content[sec_idx:]
            middle = re.sub(r'\\(newpage|clearpage)\b', '', middle)
            new_content = prefix + middle + suffix

        if new_content != content:
            tex_file.write_text(new_content, encoding="utf-8")
        # --------------------------

        xelatex_cmd = self._find_xelatex()
        logger.info(f"📄 使用 xelatex: {xelatex_cmd}")

        try:
            for i in range(2):  # 两轮编译解决交叉引用
                result = subprocess.run(
                    [xelatex_cmd, "-interaction=nonstopmode", "paper.tex"],
                    cwd=str(self.paper_dir),
                    capture_output=True, timeout=180,
                )
                logger.debug(f"xelatex 第{i+1}轮 returncode={result.returncode}")

            if (self.paper_dir / "paper.pdf").exists():
                size_kb = (self.paper_dir / "paper.pdf").stat().st_size // 1024
                logger.info(f"✅ LaTeX 编译成功: paper.pdf ({size_kb} KB)")
            else:
                # 打印 xelatex 的错误输出帮助诊断
                stderr_text = result.stderr.decode("utf-8", errors="ignore")[-500:]
                logger.warning(f"⚠️ LaTeX 编译未生成 PDF\n{stderr_text}")
        except FileNotFoundError:
            logger.warning("⚠️ LaTeX 编译跳过: 未找到 xelatex，请安装 MiKTeX 或 TeX Live")
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ LaTeX 编译超时（>180s）")

    def _quality_scan(self):
        """运行质量扫描"""
        required_files = [
            "paper.tex", "metadata.json", "initial_plan.md",
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
        code_files = list((self.paper_dir / "code").glob("*.R"))
        scan["checks"]["code_scripts"] = len(code_files)
        scan["checks"]["has_fetch_data"] = (self.paper_dir / "code" / "01_fetch_data.R").exists()
        scan["checks"]["has_analysis"] = (self.paper_dir / "code" / "03_main_analysis.R").exists()

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
    parser = argparse.ArgumentParser(description="APEP 论文流水线编排器")
    parser.add_argument("paper_num", type=int, help="论文编号（如 500）")
    parser.add_argument("--version", type=int, default=1, help="版本号")
    parser.add_argument("--model", default="claude-write", help="撰写模型 key")
    parser.add_argument("--contributor", default="anonymous", help="贡献者")
    parser.add_argument("--domain", default="labor economics", help="政策领域")
    parser.add_argument("--resume-from", default=None, help="从指定阶段恢复")

    args = parser.parse_args()

    paper_id = f"apep_{args.paper_num:04d}"

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
