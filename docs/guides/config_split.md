# 配置 7 域拆分指南

v2.0 的 `config/` 由 7 个领域 YAML + 外部 prompt 模板组成，避免单一巨石
配置文件。本指南讲解每个域的职责、新增配置项的步骤、以及 deep-merge 的
行为细节。

## 1. 7 域概览

| 文件 | 行数（参考） | 主要内容 |
|---|---|---|
| `paths.yaml` | ~70 | `paths`（路径） + `filenames`（输出文件名） + `parallel`（并行） |
| `preprocessing.yaml` | ~60 | `preprocessing`（阶段 00 参数） + `normalization` + `deduplication` |
| `filtering.yaml` | ~80 | `bank_news_classification` + `fintech_news_classification` + `article_alignment` + `fintech_intensity` |
| `sentiment.yaml` | ~100 | `tone_llm_processing` + `sentiment_analysis` + `tone_word_processing` + `tone_bert_processing` + `herd_detection` |
| `features.yaml` | ~30 | `embedding_api` + `benefit_society` + `strategic_differentiation` |
| `panel.yaml` | ~30 | `panel_building` + `temporal_mask_test` |
| `validation.yaml` | ~50 | `human_validation` + `validation` + 各 `*_test` |
| `prompts/unified_cot.txt` | ~50 | 阶段 21 LLM Chain-of-Thought 模板 |
| `prompts/title_sentiment.txt` | ~30 | 标题轨道情感分析模板 |

外加 `config.yaml` 是历史 stub（仅含 split-mode 检测说明），不再有实际内容。

## 2. 加载流程（deep-merge + 内联）

```{mermaid}
graph LR
    Start[load_config 调用]
    Start --> Detect{config/ 含 7 域 YAML?}
    Detect -->|是| Split[Split-mode 路径]
    Detect -->|否| Mono[Legacy monolithic]

    Split --> Load1[paths.yaml]
    Load1 --> Load2[preprocessing.yaml]
    Load2 --> Load3[filtering.yaml]
    Load3 --> Load4[sentiment.yaml]
    Load4 --> Load5[features.yaml]
    Load5 --> Load6[panel.yaml]
    Load6 --> Load7[validation.yaml]
    Load7 --> Merge[递归 deep-merge<br/>顺序优先级]

    Merge --> Resolve[路径解析<br/>./xxx → 绝对路径]
    Resolve --> Inline[Prompt 内联<br/>config/prompts/*.txt → string]
    Inline --> Done[返回单一 cfg dict]

    Mono --> Direct[直接 yaml.safe_load]
    Direct --> Resolve
```

`load_config()` 实现细节：

* **detect**：检查 `config/` 下是否存在 `paths.yaml`、`preprocessing.yaml`等 7 个文件，全部存在 → split-mode。
* **deep-merge**：递归合并字典 / 列表追加；后加载的 YAML 覆盖前面同 key。
* **路径解析**：所有以 `./` 开头的相对路径解析为基于 `news_process/` 的绝对路径。
* **prompt inline**：扫描 cfg dict 找到 `prompt_template_file: ./config/prompts/xxx.txt`字段，自动 `read_text()` 后改写为 `prompt_template: <文件内容>`。

```{tip}
对消费方代码 100% **API 兼容** —— 旧代码读 `cfg['tone_llm_processing']['prompt_template']`
依然得到 prompt 字符串内容；只是配置维护方现在编辑外部文件而非 YAML 内嵌字符串。
```

## 3. 新增配置项（典型场景）

### 3a. 新增简单 scalar / dict

例：在 sentiment.yaml 中加 `tone_llm_processing.title_sentiment_prompt_template_file`：

```yaml
# news_process/config/sentiment.yaml
tone_llm_processing:
  # ... 已有 ...
  title_sentiment_prompt_template_file: ./config/prompts/title_sentiment.txt
```

写对应的 prompt 文件：

```bash
echo "你是金融情感分析师..." > news_process/config/prompts/title_sentiment.txt
```

代码消费：

```python
from news_process.core.config import load_config
cfg = load_config()
template = cfg['tone_llm_processing']['title_sentiment_prompt_template']  # 已自动内联
```

### 3b. 新增整个域

如果新增的配置量大，应该开**新域 YAML**：

```bash
touch news_process/config/my_new_domain.yaml
```

然后编辑 `core/config.py` 的 `_SPLIT_DOMAINS`（注意：当前实现是 7 域硬
编码；扩容到第 8 域需要改 `_SPLIT_DOMAINS` 列表）。

```python
_SPLIT_DOMAINS = (
    "paths", "preprocessing", "filtering", "sentiment",
    "features", "panel", "validation",
    "my_new_domain",   # ← 新加
)
```

并把 `_detect_split_mode()` 期望的文件清单同步更新。

### 3c. 新增 prompt 模板

```bash
echo "你是 ..." > news_process/config/prompts/my_new_template.txt
```

在合适的域 YAML 引用：

```yaml
# news_process/config/<domain>.yaml
my_feature:
  prompt_template_file: ./config/prompts/my_new_template.txt
```

`load_config()` 的 `_inline_external_prompts()` 自动识别 `*_template_file`
后缀的 key，读取文件后改写为对应的 `*_template` key。

## 4. 测试配置变更

```bash
# 单元测试：deep-merge / detect / inline 逻辑
.venv/Scripts/python.exe -m pytest news_process/tests/integration/test_config_split_equivalence.py

# 系统测试：split-mode 加载结果与单一 config.yaml 应**递归相等**
# (该测试 fixture 临时回滚到 monolithic config.yaml + 比对)
```

## 5. 关键约定 ⚠️

### 5a. **不要**修改 stub `config.yaml`

`news_process/config/config.yaml` 是 Phase 4d 留下的 stub，**仅含**说明
注释。如果你真的修改了它（误以为是配置主入口），后果是：

* split-mode 仍优先（其余 7 个 YAML 存在 → 检测为 split-mode）
* 但你的 stub 改动被 silently ignored（这正是 stub 的设计）

要修改配置，去对应域 YAML。

### 5b. **不要**用 `~` 或 `$HOME`

YAML 中所有路径用 `./` 开头的相对路径（基于 news_process/ 目录解析），
**不要**用 `~/...` 或 `$HOME` —— `_resolve_paths()` 不展开。

### 5c. 加载顺序 = `_SPLIT_DOMAINS` tuple 顺序

deep-merge 后加载的会覆盖前面的同 key。如果你有意让某个 YAML 后于其他
覆盖，调整 `_SPLIT_DOMAINS` 顺序。但**请慎重** — 当前顺序是经过 Phase 4d
review 后选定的最自然顺序（paths → preprocess → filter → ...），改动会
影响所有人的配置预期。

### 5d. 域之间不应该有循环引用

YAML 是声明式数据，不能写表达式 / 引用其他域的值。如果你需要"`paths` 域
里某个路径基于 `preprocessing` 域的某个值"，把这个值挪到 `paths` 域。

### 5e. 敏感信息走 `.env` 而非 YAML

API 密钥、数据库密码等**必须**走环境变量，不入 YAML。`load_config()`
会自动 `python-dotenv` 加载 `news_process/.env` 并解析 YAML 中
`${VAR_NAME}` 占位符。

```yaml
# news_process/config/sentiment.yaml
tone_llm_processing:
  models:
    - model_name: gpt-5-nano
      api_key: ${GPT5NANO_API_KEY}   # ← 自动从 .env 替换
```

## 6. 调试 config 加载

```python
from news_process.core.config import load_config
cfg = load_config()

# 看完整 loaded config
import json
print(json.dumps(cfg, indent=2, default=str, ensure_ascii=False)[:3000])

# 验证某个 key 解析正确
print(cfg['paths']['output_dir'])  # 应是绝对路径，且存在
print(len(cfg['tone_llm_processing']['prompt_template']))  # 应是非零长度（已内联）
```

## 7. DoD 验收

* ✓ `load_config()` 不抛异常
* ✓ 关键 key 都能取到（`paths.output_dir`, `tone_llm_processing.models` 等）
* ✓ 路径都是绝对路径
* ✓ Prompt 都是字符串而非 dict（内联成功）
* ✓ `test_config_split_equivalence` 通过

## 8. 见也

* [`core.config.load_config` API](../api/core.md)
* [新增 Stage 指南](adding_stage.md)
* `news_process/config/SPLIT_PLAN.md`（Phase 2f 拆分计划文档，原始决策记录）
