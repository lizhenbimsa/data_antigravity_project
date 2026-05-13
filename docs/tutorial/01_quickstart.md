# 快速上手（5 分钟）

本教程帮助你在 5 分钟内：装好环境、加载配置、跑一次 import smoke test，
确认 v2.1.0 包可以正常工作。**不会**实际跑流水线（那需要 22 GB 数据 +
LLM API 配额，见 [主流水线教程](02_main_pipeline.md)）。

## 1. 系统要求

| 维度 | 要求 |
|---|---|
| OS | Windows 10/11、Linux、macOS（pytest 中 3 个 lock test 在 Win 上 skip，无功能影响） |
| Python | {{min_python}}+（推荐 3.13） |
| 内存 | 推荐 16 GB+（流水线峰值阶段 00 占用 ~10 GB） |
| 磁盘 | 至少 50 GB 空闲（22 GB 数据 + 模型缓存 + 日志） |

## 2. 克隆 + 装环境

```bash
# 克隆仓库（路径由你决定）
cd /path/to/your/workspace

# 创建 isolated venv（避免 Conda site-package 泄漏 — requirements.txt 顶部有专门的注释）
python -m venv .venv
.venv/Scripts/python.exe -m pip install --upgrade pip   # Windows
# .venv/bin/pip install --upgrade pip                   # macOS/Linux

# 装运行时依赖
.venv/Scripts/python.exe -m pip install -r news_process/requirements.txt
```

## 3. 配置 .env

```bash
cp news_process/.env.example news_process/.env
```

编辑 `news_process/.env`：

```bash
# LLM API 密钥（阶段 21 / 32 / 33 / 36 / 39 需要；其他 stage 不需要）
GPT5NANO_API_KEY=sk-xxxxxx
GEMINI3_API_KEY=AIzaSyXXX
CLAUDE4H_API_KEY=sk-ant-xxxxxx

# Embedding API（阶段 15 / 25-27 需要）
EMBEDDING_API_KEY=sk-xxxxxx
```

```{tip}
仅做 import smoke test 时，密钥可以填**任意非空值** — `load_config()`
不会真的发起 API 请求。
```

## 4. 验证安装

跑 5 个最关键的 smoke check：

```python
# 在 repo root 跑：python smoke.py
import news_process
print(f"news_process version: {news_process.__version__}")  # 期望: 2.0.0

# Check 1: config 可加载
from news_process.core.config import load_config
cfg = load_config()
print(f"output_dir: {cfg['paths']['output_dir']}")
print(f"配置域: {sorted(cfg.keys())[:5]}...")

# Check 2: DAG 可枚举
from news_process.core.dag import STAGES_MAIN, STAGES_VALIDATION
print(f"主线 DAG: {len(STAGES_MAIN)} stages")
print(f"验证 DAG: {len(STAGES_VALIDATION)} stages")

# Check 3: 全部 pipeline + validation 子包可 import
from news_process.pipeline.filtering import news_bank, news_fintech, fintech_intensity
from news_process.pipeline.sentiment import tone_llms, tone_words, tone_berts, herd_decay
from news_process.pipeline.audit import stata_audit, stats_excel
from news_process.validation import (
    text2vec, threshold, llms_human, dedup_threshold, llms_evaluation,
    tone_validation, radius_sensitivity, entity_masking, dict_coverage,
    media_diversity, temporal_mask, decay_sensitivity, prompt_sensitivity,
)
print("All canonical imports OK.")

# Check 4: 5 个 paper 包可 import
from news_process.papers import (
    bank_fintech_tone, benefit_society, brokerage_network, llm_peer, strategic_diff,
)
print(f"Papers loaded: {[p.PAPER_ID for p in [bank_fintech_tone, benefit_society, brokerage_network, llm_peer, strategic_diff]]}")

# Check 5: pytest 套件
# 在 shell 里跑：python -m pytest news_process/tests/ -q --co  # 仅 collect
```

期望输出：

```
news_process version: 2.0.0
output_dir: F:/.../news_process/data/processed
配置域: ['article_alignment', 'bank_news_classification', 'benefit_society', ...]
主线 DAG: 11 stages
验证 DAG: 12 stages
All canonical imports OK.
Papers loaded: ['bank_fintech_tone', 'benefit_society', 'brokerage_network', 'llm_peer', 'strategic_diff']
```

## 5. 跑全套测试（可选，~4 min）

```bash
.venv/Scripts/python.exe -m pytest news_process/tests/
```

期望（post-Wave 0/1 + Batch P0 + V8 + Wave 2 batch 1, 2026-05-13）：

```
891 passed, 2 skipped, 33 warnings in ~33s   # HEAD baseline (jieba warm cache, cold start ~75s)
                                             # 演进: v2.1.0=772 -> round 3 review=814 -> Wave 1 (+ BERT determinism)=855
                                             #      -> Batch P0 (+ cache stats + BERT invariant)=863
                                             #      -> V8 (+ log-prune + main-paper smoke)=879
                                             #      -> Wave 2 b1 (+ iv_did paper-critical math)=891
```

```{warning}
2 skipped 是平台天然差异（1 个 Unix-only fcntl test + 1 个 Win 空字符串路径），
不再像旧 baseline (6 skipped) 那样混入 Windows 文件锁测试 — Plan-r2 P1-5
sidecar 化已让那 4 个原本的 Win SKIP 转为 PASS。

历史对比 (v2.0.0 baseline): 778 passed / 7 skipped. v2.1.0 后 -16 测试
(Phase 9a 整删 ``test_papers_dag_consistency.py`` 的 16 个 0-差异守护测试)
+ 1 测试 (Phase 9d 新增 ``test_stages_main_all_registered_in_output_registry``
一致性守护) 净 -15. 对应实测 baseline 在 v2.0.0 之上还有 +9 (3 个 release-
follow-up fix commit 各自带新测试), 故最终 772.
```

## 6. 下一步

* [主流水线教程](02_main_pipeline.md) — 用真实 22 GB 数据跑生产流水线
* [验证模块教程](03_validation.md) — 跑稳健性检验矩阵
* [多论文工作流](04_multi_paper.md) — 同时驱动 5 个研究产品
* [新增 Stage 指南](../guides/adding_stage.md) — 添加自己的处理阶段
