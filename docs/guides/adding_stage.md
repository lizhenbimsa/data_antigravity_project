# 新增 Stage（流水线阶段）开发指南

本指南演示如何为 v3.7.x 主流水线 / 验证矩阵添加一个新的处理阶段（v2.1.0 起的 thin shim + 声明式 DAG 契约不变）。

## 1. 决策树：放在哪？

```{mermaid}
graph TD
    Q1{新阶段属于哪类业务？}
    Q1 -->|核心 pipeline| P[news_process/pipeline/&lt;sub&gt;/]
    Q1 -->|稳健性 / 验证| V[news_process/validation/]
    Q1 -->|纯审计 / 一次性| A[news_process/scripts/audit/]

    P -->|是哪个子包| P1[preprocess / filtering / text / sentiment /<br/>features / panel / falsification / audit / external / llm_archive]
    V -->|是否需要 enabled_when 谓词| Vy[加 _VALIDATION_PREDS 键]
    V -->|总是跑| Vn[直接 always_enabled]
```

**经验法则**：
* **主线生产**（产出是下游所有 stage 的输入或论文需要的核心变量）→ `pipeline/`
* **方法论检验 / 稳健性**（不进主流水线，仅为论文 Appendix 服务）→ `validation/`
* **一次性审计 / 数据探索**（不希望 pytest 扫到，可能含 `sys.exit`）→ `scripts/audit/`

## 2. 标准开发流程（10 步）

### Step 1: 选择阶段编号

阶段编号有约定俗成的业务前缀：

| 前缀 | 含义 | 已用 |
|---|---|---|
| `00` | 预处理 | 00 |
| `1x` | 筛选 | 11, 12, 14, 15 |
| `2x` | 情感 | 21, 22, 23, 24 |
| `3x` | 验证 | 30-39, 32a, 38a, 38b |
| `4x` | 面板组装 | 40-48 |
| `5x` | 衍生（伪造检验、审计） | 51, 52, 53 |

新阶段尽量复用前缀（如新加一个情感方法用 `25_xxx`），保持命名一致。

### Step 2: 在子包写 body

例：在 `pipeline/sentiment/` 加 `aspect_based.py`（aspect-based sentiment）。

```python
# news_process/pipeline/sentiment/aspect_based.py
"""阶段 25: Aspect-Based Sentiment Analysis."""

import os
import sys
import time

# 子包模式：上溯 3 层抵达 news_process/ 的父目录
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging, log_stage_summary
from news_process.core.reporting import save_dataset

CONFIG = load_config()
STAGE_NAME = "25_aspect_based"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


def main():
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

    # ... 业务逻辑

    save_dataset(result_df, output_path, logger)
    log_stage_summary(logger, STAGE_NAME, stage_start, n_in, n_out)
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
```

### Step 3: 写 root thin shim

```python
# news_process/25_aspect_based.py — 23 行 thin shim
"""25_aspect_based.py — DEPRECATED CLI shim (v2.0+)."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.sentiment.aspect_based import main
    main()
```

### Step 4: 在 DAG 注册

编辑 `news_process/core/dag.py`：

```python
STAGES_MAIN: list[StageSpec] = [
    # ... 已有阶段 ...

    StageSpec(
        name="阶段25: Aspect-Based 情感分析",
        script="25_aspect_based.py",
        group="main", kind="sentiment",
        timeout=3600,
        # 如果只在某种 enabled_methods 启用，定义谓词；否则用默认 always_enabled
        enabled_when=aspect_method_enabled,  # 自定义模块级 callable
    ),
]


# 模块级谓词（保证 `is` identity）
def aspect_method_enabled(cfg: dict) -> bool:
    methods = cfg.get('sentiment_analysis', {}).get('enabled_methods', []) or []
    return 'aspect_based' in methods
```

### Step 5: （可选）在 OUTPUT_REGISTRY 注册输出

编辑 `news_process/core/schemas.py`：

```python
OUTPUT_REGISTRY: dict[str, list[str]] = {
    # ... 已有 ...
    '25_aspect_based.py': ['25_aspect_based.parquet'],
}
```

这让 orchestrator 在每次启动新 stage 前预清理陈旧输出。

### Step 6: （可选）添加 config

如果新 stage 有可调参数，在合适的域 YAML 里加：

```yaml
# news_process/config/sentiment.yaml
aspect_based_sentiment:
  enabled: true
  aspect_keywords_file: ./config/aspect_keywords.json
  threshold: 0.6
```

可访问：

```python
ASPECT_CFG = CONFIG.get('aspect_based_sentiment', {})
threshold = ASPECT_CFG.get('threshold', 0.6)
```

### Step 7: 写单元测试

```python
# news_process/tests/test_25_aspect_based.py
"""tests/test_25_aspect_based.py — 阶段 25 白盒测试."""

import os
import sys
import pytest
import pandas as pd

# 注入项目父目录
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)


@pytest.fixture
def aspect_module():
    """规范包导入（不要走 importlib.import_module('25_aspect_based')）."""
    from news_process.pipeline.sentiment import aspect_based
    return aspect_based


class TestAspectBased:
    def test_some_helper(self, aspect_module):
        result = aspect_module.compute_aspect_score("...", aspects=["AI"])
        assert 0 <= result <= 1
```

### Step 8: 跑测试

```bash
.venv/Scripts/python.exe -m pytest news_process/tests/test_25_aspect_based.py -v
```

### Step 9: 跑 DAG 一致性测试

```bash
.venv/Scripts/python.exe -m pytest news_process/tests/integration/test_dag_consistency.py -v
```

确保新 stage 加入后 orchestrator 仍能正确消费 DAG。

### Step 10: 跑全套测试 + commit

```bash
.venv/Scripts/python.exe -m pytest news_process/tests/
git add news_process/pipeline/sentiment/aspect_based.py \
        news_process/25_aspect_based.py \
        news_process/core/dag.py \
        news_process/core/schemas.py \
        news_process/config/sentiment.yaml \
        news_process/tests/test_25_aspect_based.py
git commit -m "feat(news_process): add stage 25 aspect-based sentiment analysis"
```

## 3. 关键约定 ⚠️

### 3a. **不要**用 `importlib.import_module('25_aspect_based')`

旧代码用反射 import 数字前缀文件，v2.0 起**禁止**。规范包路径：

```python
# ✗ 错误（v1.x 模式）
import importlib
mod = importlib.import_module('25_aspect_based')

# ✓ 正确（v2.0 模式）
from news_process.pipeline.sentiment import aspect_based as mod
```

### 3b. body 中的 `sys.path` 注入是 belt-and-suspenders

子包 body 中包含 sys.path 注入是为了在以下情况下工作：

* 模块作为子进程启动：`subprocess.run([python, "25_aspect_based.py"])`
* 模块直接调用：`python -m news_process.pipeline.sentiment.aspect_based`
* 测试 fixture 加载：`from news_process.pipeline.sentiment import aspect_based`

不要删除 sys.path 注入块。

### 3c. **不要**在模块级别 `sys.exit()`

`pipeline/` 与 `validation/` 模块会被 pytest collect → import，模块级
`sys.exit(1)` 会导致 pytest collection 失败。如果有"必须退出"的 fatal
error，放在 `main()` 内部。

`scripts/audit/` 不受此约束（pytest 不扫这个目录）。

### 3d. 谓词必须是模块级 callable

`enabled_when=` 参数必须是**模块级**函数，不能是 lambda 或局部 closure。
理由：`test_dag_consistency.py` 用 `is` 检测谓词身份相等，要求两个
import site 共享同一个 callable 对象。

```python
# ✗ 错误：lambda 在每次 import 时是新对象
StageSpec(..., enabled_when=lambda cfg: cfg['x']['y'])

# ✗ 错误：内联函数同样问题
def define_specs():
    def my_pred(cfg):
        return cfg['x']['y']
    return [StageSpec(..., enabled_when=my_pred)]

# ✓ 正确：模块级 def
def my_pred(cfg):  # 模块作用域
    return cfg['x']['y']

STAGES_MAIN = [
    StageSpec(..., enabled_when=my_pred),
]
```

## 4. 添加 validation 阶段

仅 step 1-2 略有不同：

* 放在 `news_process/validation/` 而非 `pipeline/<sub>/`
* `sys.path` 注入是 **2 级**（`os.path.dirname × 2`）而非 3 级
* 在 `core/dag.py:STAGES_VALIDATION` 注册（不是 `STAGES_MAIN`）
* 谓词放在 `_VALIDATION_PREDS` dict 里 + 用 `_validation_flag()` 工厂

例：

```python
# news_process/core/dag.py 添加：
_VALIDATION_PREDS['my_new_check'] = _validation_flag('my_new_check')

# STAGES_VALIDATION 添加：
StageSpec(
    name="阶段40: 我的新稳健性检验",
    script="40_my_new_check.py",
    group="validation", kind="robustness",
    enabled_when=_VALIDATION_PREDS['my_new_check'],
),
```

config 加开关：

```yaml
# news_process/config/validation.yaml
validation:
  my_new_check: true   # 默认开
```

## 5. DoD 验收

* ✓ 子包 body 文件存在且可 import (`python -c "from news_process.pipeline.X.Y import main"`)
* ✓ root thin shim 存在且可执行 (`python news_process/NN_xxx.py --help` 不崩)
* ✓ DAG 中已注册（grep `core/dag.py`）
* ✓ pytest 通过（unit + integration 都跑）
* ✓ orchestrator 干跑（dry-run）能列出新 stage：`python run_pipeline_function.py` 看输出

## 6. 见也

* [`StageSpec` 参考](../reference/dag.md)
* [Thin shim 设计模式](thin_shim_pattern.md)
* [配置拆分指南](config_split.md)
