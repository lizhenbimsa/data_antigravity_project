# Thin Shim 设计模式

`news_process` v2.0 在 26 个数字前缀 root script 上系统应用 **Thin Shim
模式**。本指南讲解此模式的动机、实现规范、变体、与常见反模式。

## 1. 问题陈述

数字前缀文件名（如 `11_news_bank.py`、`38a_temporal_mask_test.py`）有
两个 incompatible properties:

1. **作为 CLI 入口**：orchestrator 通过 `subprocess.run([python,
   "11_news_bank.py"])` 调用；外部 Stata 用户、CI 脚本、shell 脚本可能
   也直接调用，**调用契约必须保留**。
2. **数字前缀不是合法 Python identifier**：`import 11_news_bank`
   语法错误；`from 11_news_bank import main` 同样不合法。

**直接结果**：v1.x 用 `importlib.util.spec_from_file_location("...",
"11_news_bank.py")` 反射 import，但这导致：
* 无法静态分析（pyflakes / pyright / IDE 都不认）
* 文件移动后路径硬编码失效
* 测试 fixture 加载方式与生产代码不一致

## 2. 解决方案：Thin Shim

把 body 全部迁入合法 identifier 的子包模块（`news_process.pipeline.
filtering.news_bank`），数字前缀文件保留为 **≤30 行的 thin shim** 仅
负责 `sys.path` 注入 + delegate。

```{mermaid}
graph LR
    Caller[orchestrator/CLI/Stata] -->|subprocess.run NN_xxx.py| Shim[NN_xxx.py<br/>≤23 行 shim]
    Shim -->|delegate to| Body[news_process.<br/>pipeline.X.module]
    Shim -.->|sys.path 注入| Path[确保 ``news_process.*``<br/>可解析]
```

## 3. 标准 Shim 模板

```python
"""NN_xxx.py — DEPRECATED CLI shim (Phase 7a-N).

Body migrated to ``news_process.pipeline.<sub>.<module>:main`` during
Phase 7a-N. The historical contract ``python NN_xxx.py`` is preserved
by this thin shim; orchestrators continue to invoke it as a subprocess.

External tooling should migrate to:
    python -m news_process.pipeline.<sub>.<module>

Slated for removal in v3.0.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.<sub>.<module> import main
    main()
```

**精确 23 行**（含空行与 docstring）。极度紧凑，零冗余。

## 4. 4 个变体

### 4a. Pipeline 子包变体

```python
from news_process.pipeline.filtering.news_bank import main
from news_process.pipeline.sentiment.tone_llms import main
from news_process.pipeline.audit.stata_audit import main
```

### 4b. Validation 扁平变体

```python
from news_process.validation.text2vec import main
from news_process.validation.prompt_sensitivity import main
```

### 4c. 历史 Phase 1 变体（已有的 4 个）

50/51 用 `pipeline.falsification.controls`，53 用 `pipeline.audit.stats_excel`。

### 4d. 早期 Phase 2 变体（00/15/45）

```python
from news_process.pipeline.preprocess.runner import main
from news_process.pipeline.filtering.policy_alignment import main
from news_process.pipeline.panel.runner import main
```

## 5. 关键约束 ⚠️

### 5a. `sys.path` 注入是必须的

Shim 在 root 层级（`news_process/NN_xxx.py`），需要让 `news_process.X`
可解析。**最简洁**的做法：

```python
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
```

* `__file__` = `/repo/news_process/NN_xxx.py`
* `.parents[0]` = `/repo/news_process`
* `.parents[1]` = `/repo`（注入此目录到 sys.path）
* 然后 `import news_process.X` 解析为 `/repo/news_process/X`

### 5b. `if __name__ == "__main__":` 必须存在

orchestrator 通过 `subprocess.run([python, NN_xxx.py])` 调用，期望脚本
**作为主程序运行**。`if __name__ == "__main__": main()` 是入口。

### 5c. **不要** import 业务依赖到 shim 顶层

```python
# ✗ 错误（v1.x 反模式）
import os
import pandas as pd
from news_process.pipeline.filtering.news_bank import main, BANKS, AC_AUTOMATON

if __name__ == "__main__":
    main()
```

这破坏了 thin shim 的核心目的：**懒加载**。子包 body 加载需要
`load_config()` + AC 自动机构建，耗时数秒；如果 shim 顶层 import 业务依赖，
那么任何对此 shim 的 import（甚至只是为了检查 `if __name__`）都会触发
全部副作用。

正确做法：**仅在 `if __name__ == "__main__":` 内部** import:

```python
# ✓ 正确（v2.0 模式）
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.filtering.news_bank import main  # 懒加载
    main()
```

### 5d. **不要**在 shim 添加业务逻辑

shim 是**纯 delegate**。所有业务（参数解析、IO、计算）都在 body 里。
如果你想给 stage 加一个 `--debug` flag，加在 body 的 `main()` 里用
argparse。

## 6. 子包 body 端的对应模式

子包 body 文件需要在顶部做 sys.path 注入（**3 级**或 **2 级**，取决于
文件深度）：

### Pipeline 子包（3 级）

```python
# news_process/pipeline/<sub>/<module>.py
_HERE = os.path.dirname(os.path.abspath(__file__))
# pipeline/<sub>/<module>.py → pipeline/<sub>/ → pipeline/ → news_process/ → repo/
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)
```

### Validation 扁平（2 级）

```python
# news_process/validation/<module>.py
_HERE = os.path.dirname(os.path.abspath(__file__))
# validation/<module>.py → validation/ → news_process/ → repo/
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)
```

理由：`subprocess.run([python, "/abs/path/to/news_process/<sub>/<mod>.py"])`
不会自动把 `news_process/` 父目录加入 sys.path，需要 body 显式注入。
反正这是 belt-and-suspenders（实际 `python -m` 调用时已正确解析），
但成本是 5 行注释 + 4 行代码，远低于潜在故障率。

## 7. 测试 fixture 端的对应模式

测试**不**应通过 shim 加载 module（shim 只暴露 `main()`，不 expose 内部
函数 / 模块级常量）。规范模式：

```python
# news_process/tests/test_NN_xxx.py
@pytest.fixture
def my_module():
    """Phase 7a-N: body 已迁至子包，规范包路径加载."""
    import os, sys
    _PROJECT_PARENT = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    if _PROJECT_PARENT not in sys.path:
        sys.path.insert(0, _PROJECT_PARENT)
    from news_process.pipeline.<sub> import <module>
    return <module>
```

**禁用**模式：

```python
# ✗ 反模式 1：importlib 反射加载 shim
my_module = importlib.import_module('NN_xxx')   # 现在只返回 23 行 shim

# ✗ 反模式 2：spec_from_file_location
spec = importlib.util.spec_from_file_location("name", "NN_xxx.py")
my_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(my_module)
```

## 8. 反模式：what NOT to do

### 8a. ❌ 在 shim 里加 logger / setup_logging

```python
# ✗ 错误：让 shim 拥有 logger 是把业务逻辑从 body 漏到 shim
import pathlib, sys
sys.path.insert(0, ...)

import logging
logger = logging.getLogger("11_news_bank_shim")
logger.info("Starting...")  # 这种 log 只是噪音
```

### 8b. ❌ 在 shim 做参数解析

```python
# ✗ 错误：argparse 应该在 body 的 main() 里
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--debug")
args = parser.parse_args()

if __name__ == "__main__":
    from news_process.pipeline.filtering.news_bank import main
    main(debug=args.debug)
```

### 8c. ❌ 多个 import 路径

```python
# ✗ 错误：if-else 分支
try:
    from news_process.pipeline.filtering.news_bank import main
except ImportError:
    from utils.helpers import news_bank_main as main   # 旧路径回退
```

v2.0 起 `utils/` 已删除（Phase 6b），任何对它的 fallback 都是 dead code。

### 8d. ❌ 在 shim 暴露内部函数

```python
# ✗ 错误：尝试让 shim 像旧 root script 一样 expose 全部
import pathlib, sys
sys.path.insert(0, ...)

from news_process.pipeline.filtering.news_bank import (
    main, BANKS, AC_AUTOMATON, classify_batch, _analyze_single_article,
    log_classification_report, merge_stats,
    SPLIT_RATIO, MIN_UPPER, MIN_LOWER, MIN_NAME_OCCURRENCES,
)

if __name__ == "__main__":
    main()
```

这等于把 shim 变回一个完整 module，丧失 thin 的本意。**只 import `main`**。
其他符号让消费方走规范包路径：`from news_process.pipeline.filtering.news_bank
import classify_batch`。

## 9. 历史背景

26 个 thin shim 是分两批完成的：

* **Phase 1.4b - Phase 2c**（5 个 pilot）: `00`, `15`, `45`, `51`, `53`
* **Phase 7a**（8 个 pipeline）: `11`, `12`, `14`, `21`, `22`, `23`, `24`, `52`
* **Phase 7b**（13 个 validation）: `30`, `31`, `32`, `32a`, `33`, `34`,
  `35`, `36`, `37`, `38`, `38a`, `38b`, `39`

每批的 commit / tag 见 [CHANGELOG](../changelog.md)。

## 10. 见也

* [新增 Stage 指南](adding_stage.md) — 创建新 stage 时正确应用此模式
* [`core.dag.StageSpec` 参考](../reference/dag.md)
* CHANGELOG 中 Phase 7a / 7b 章节
