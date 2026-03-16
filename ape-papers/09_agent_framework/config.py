# -*- coding: utf-8 -*-
"""
APEP 生产基础设施 — 全局配置
==========================================
管理所有模型、API 密钥、路径和运行时参数。
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Optional
from pathlib import Path


# ============================================================
# 1. 统一 API 配置（所有模型通过 yunwu.ai 代理）
# ============================================================

UNIFIED_API_BASE_URL = "https://yunwu.ai/v1"
UNIFIED_API_KEY = "sk-bxKmTvBf5WrJwZ0r474eBfC2De404a38931216Ed79548f05"


@dataclass
class ModelConfig:
    """单个 LLM 模型的完整配置"""
    name: str                              # 人类可读名称
    provider: str                          # 统一使用 openai 兼容格式
    model_id: str                          # API 模型标识符
    api_key_env: str = "APEP_API_KEY"      # 环境变量（备用）
    api_base_url: Optional[str] = None     # 自定义 API 端点
    max_tokens: int = 16384                # 最大输出 tokens
    temperature: float = 0.7               # 采样温度
    timeout: int = 300                     # 请求超时（秒）
    max_retries: int = 3                   # 最大重试次数
    retry_delay: float = 5.0               # 重试间隔（秒）
    rate_limit_rpm: int = 60               # 速率限制（每分钟请求数）

    @property
    def api_key(self) -> str:
        """优先使用统一 API Key，其次从环境变量读取"""
        return UNIFIED_API_KEY or os.environ.get(self.api_key_env, "")

    @property
    def base_url(self) -> str:
        """优先使用统一 API Base URL"""
        return self.api_base_url or UNIFIED_API_BASE_URL


# ---- 撰写模型（Authoring Models）----
AUTHORING_MODELS: Dict[str, ModelConfig] = {
    "gemini-write": ModelConfig(
        name="Gemini 3.1 Pro",
        provider="openai",
        model_id="gemini-3.1-pro-preview",
        api_base_url=UNIFIED_API_BASE_URL,
        max_tokens=16384,
        temperature=0.7,
    ),
    "gpt-write": ModelConfig(
        name="GPT-5.2",
        provider="openai",
        model_id="gpt-5.2",
        api_base_url=UNIFIED_API_BASE_URL,
        max_tokens=16384,
        temperature=0.7,
    ),
    "claude-write": ModelConfig(
        name="Claude Sonnet 4.6",
        provider="openai",
        model_id="claude-sonnet-4-6",
        api_base_url=UNIFIED_API_BASE_URL,
        max_tokens=16384,
        temperature=0.7,
    ),
    "grok-write": ModelConfig(
        name="Grok 4.1",
        provider="openai",
        model_id="grok-4.1",
        api_base_url=UNIFIED_API_BASE_URL,
        max_tokens=16384,
        temperature=0.7,
    ),
    "deepseek-write": ModelConfig(
        name="DeepSeek V3.2",
        provider="openai",
        model_id="deepseek-v3.2",
        api_base_url=UNIFIED_API_BASE_URL,
        max_tokens=16384,
        temperature=0.7,
    ),
}

# ---- 评审模型（Review Models）----
REVIEW_MODELS: Dict[str, ModelConfig] = {
    "gpt-review": ModelConfig(
        name="GPT-5 Mini",
        provider="openai",
        model_id="gpt-5-mini",
        api_base_url=UNIFIED_API_BASE_URL,
        max_tokens=8192,
        temperature=0.3,
    ),
    "grok-review": ModelConfig(
        name="Grok 4.1 Fast",
        provider="openai",
        model_id="grok-4-1-fast-non-reasoning",
        api_base_url=UNIFIED_API_BASE_URL,
        max_tokens=8192,
        temperature=0.3,
    ),
    "deepseek-review": ModelConfig(
        name="DeepSeek V3.2 Fast",
        provider="openai",
        model_id="deepseek-v3.2-fast",
        api_base_url=UNIFIED_API_BASE_URL,
        max_tokens=8192,
        temperature=0.3,
    ),
    "gemini-review": ModelConfig(
        name="Gemini 3 Flash",
        provider="openai",
        model_id="gemini-3-flash-preview",
        api_base_url=UNIFIED_API_BASE_URL,
        max_tokens=8192,
        temperature=0.3,
    ),
}

# ---- 裁判模型（Tournament Judge）----
JUDGE_MODELS: Dict[str, ModelConfig] = {
    "gemini-judge": ModelConfig(
        name="Gemini 3.1 Pro (Judge)",
        provider="openai",
        model_id="gemini-3.1-pro-preview",
        api_base_url=UNIFIED_API_BASE_URL,
        max_tokens=4096,
        temperature=0.1,
    ),
    "gpt-judge": ModelConfig(
        name="GPT-5.2 (Judge)",
        provider="openai",
        model_id="gpt-5.2",
        api_base_url=UNIFIED_API_BASE_URL,
        max_tokens=4096,
        temperature=0.1,
    ),
}


# ============================================================
# 2. 路径配置
# ============================================================

@dataclass
class PathConfig:
    """项目路径配置"""
    # 根目录（可通过环境变量覆盖）
    project_root: Path = field(
        default_factory=lambda: Path(
            os.environ.get("APEP_ROOT", Path(__file__).parent.parent)
        )
    )

    @property
    def papers_dir(self) -> Path:
        """论文存储目录"""
        return self.project_root

    @property
    def templates_dir(self) -> Path:
        """模板目录"""
        return self.project_root / "08_config_templates"

    @property
    def r_templates_dir(self) -> Path:
        """R 代码模板目录"""
        return self.project_root / "04_r_templates"

    @property
    def latex_templates_dir(self) -> Path:
        """LaTeX 模板目录"""
        return self.project_root / "05_paper_template"

    @property
    def logs_dir(self) -> Path:
        """日志目录"""
        d = self.project_root / "logs"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def paper_dir(self, paper_id: str, version: int = 1) -> Path:
        """获取单篇论文的版本目录"""
        return self.papers_dir / paper_id / f"v{version}"


PATHS = PathConfig()


# ============================================================
# 3. 流水线阶段配置
# ============================================================

@dataclass
class StageConfig:
    """单个流水线阶段的配置"""
    name: str                   # 阶段名称
    order: int                  # 执行顺序
    model_key: str              # 使用的模型 key（引用 AUTHORING_MODELS）
    required_inputs: list       # 本阶段需要的输入文件
    expected_outputs: list      # 本阶段应产出的文件
    max_attempts: int = 3       # 最大重试次数
    timeout_minutes: int = 30   # 超时（分钟）
    can_skip: bool = False      # 是否可跳过


PIPELINE_STAGES: Dict[str, StageConfig] = {
    "ideas": StageConfig(
        name="创意生成",
        order=1,
        model_key="claude-write",
        required_inputs=[],
        expected_outputs=["ideas.md", "ideas_ranked.json"],
    ),
    "plan": StageConfig(
        name="研究计划",
        order=2,
        model_key="claude-write",
        required_inputs=["ideas_ranked.json"],
        expected_outputs=["initial_plan.md", "research_plan.md"],
    ),
    "data": StageConfig(
        name="数据获取",
        order=3,
        model_key="claude-write",
        required_inputs=["research_plan.md"],
        expected_outputs=["code/01_fetch_data.R"],
        timeout_minutes=60,
    ),
    "analysis": StageConfig(
        name="计量分析",
        order=4,
        model_key="claude-write",
        required_inputs=["research_plan.md", "code/01_fetch_data.R"],
        expected_outputs=["code/03_main_analysis.R", "code/05_figures.R"],
        timeout_minutes=60,
    ),
    "paper": StageConfig(
        name="论文撰写",
        order=5,
        model_key="claude-write",
        required_inputs=["research_plan.md", "code/03_main_analysis.R"],
        expected_outputs=["paper.tex"],
        timeout_minutes=45,
    ),
    "review": StageConfig(
        name="同行评审",
        order=6,
        model_key="claude-write",  # 评审使用 REVIEW_MODELS，此处为 fallback
        required_inputs=["paper.tex"],
        expected_outputs=["review_gpt_1.md", "review_cc_1.md"],
    ),
    "revision": StageConfig(
        name="修订",
        order=7,
        model_key="claude-write",
        required_inputs=["paper.tex", "review_gpt_1.md"],
        expected_outputs=["revision_plan_1.md", "reply_to_reviewers_1.md"],
        can_skip=True,
    ),
    "publish": StageConfig(
        name="发布",
        order=8,
        model_key="claude-write",
        required_inputs=["paper.tex", "metadata.json"],
        expected_outputs=["paper.pdf", "REPLICATION.md", "scan_report.json"],
    ),
}


# ============================================================
# 4. 评审决策阈值
# ============================================================

@dataclass
class ReviewThresholds:
    """评审决策阈值"""
    accept_threshold: float = 7.5       # 综合评分 >= 此值：接受
    minor_revision_threshold: float = 6.0  # >= 此值且 < accept：小修
    major_revision_threshold: float = 4.5  # >= 此值且 < minor：大修
    # < major_revision_threshold: 拒稿
    max_revision_rounds: int = 3        # 最大修订轮数
    min_reviewers: int = 3              # 最少评审人数

REVIEW_THRESHOLDS = ReviewThresholds()


# ============================================================
# 5. ELO 竞赛参数
# ============================================================

@dataclass
class TournamentConfig:
    """竞赛系统参数"""
    initial_elo: float = 1500.0
    k_factor: float = 32.0              # ELO K 因子
    min_matches: int = 5                # 最少比赛场次
    confidence_threshold: float = 0.95   # 统计显著性阈值
    judges_per_match: int = 3           # 每场比赛的裁判数
    max_rounds: int = 10                # 最大轮次

TOURNAMENT_CONFIG = TournamentConfig()


# ============================================================
# 6. 日志配置
# ============================================================

import logging

def setup_logging(name: str = "apep", level: int = logging.INFO) -> logging.Logger:
    """配置结构化日志"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # 控制台输出
        console = logging.StreamHandler()
        console.setLevel(level)
        fmt = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console.setFormatter(fmt)
        logger.addHandler(console)

        # 文件输出
        log_file = PATHS.logs_dir / f"{name}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    return logger


# ============================================================
# 7. 验证与诊断
# ============================================================

def validate_environment() -> tuple[bool, list[str]]:
    """验证当前环境配置是否完整"""
    missing = []

    # 检查统一 API 配置
    if not UNIFIED_API_KEY:
        missing.append("UNIFIED_API_KEY (config.py 中未配置)")

    # 检查 R 环境
    import shutil
    if not shutil.which("Rscript"):
        missing.append("Rscript (R 语言环境)")

    return (len(missing) == 0, missing)


if __name__ == "__main__":
    print("=" * 60)
    print("APEP 环境诊断报告")
    print("=" * 60)

    env_ok, missing = validate_environment()

    if env_ok:
        print("\n✅ 所有检查通过！")
    else:
        print("\n❌ 缺失项:")
        for m in missing:
            print(f"   - {m}")

    print(f"\n📁 项目根目录: {PATHS.project_root}")
    print(f"📝 日志目录:   {PATHS.logs_dir}")
    print(f"🌐 API 入口:   {UNIFIED_API_BASE_URL}")
    print(f"🔑 API Key:    {UNIFIED_API_KEY[:12]}...{UNIFIED_API_KEY[-4:]}")
    print(f"🤖 撰写模型:   {', '.join(AUTHORING_MODELS.keys())}")
    print(f"📋 评审模型:   {', '.join(REVIEW_MODELS.keys())}")
    print(f"⚖️  裁判模型:   {', '.join(JUDGE_MODELS.keys())}")

