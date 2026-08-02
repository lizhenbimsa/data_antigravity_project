# 环境变量参考

`news_process` v2.0 使用环境变量（通过 `python-dotenv` 从 `.env` 加载）
注入：(a) 敏感凭证（API 密钥）；(b) 跨进程协调信号（run_id）。

## 1. 总览

| 变量 | 必需？ | 主消费者 | 说明 |
|---|---|---|---|
| `GPT5NANO_API_KEY` | 仅 21/32/33/36/39 | 阶段 21 LLM 调用 | OpenAI / GPT-5-nano API 密钥 |
| `GEMINI3_API_KEY` | 仅 21/32/33/36/39 | 阶段 21 LLM 调用 | Google AI Studio / Gemini 3 API 密钥 |
| `CLAUDE4H_API_KEY` | 仅 21/32/33/36/39 | 阶段 21 LLM 调用 | Anthropic / Claude 4 Haiku API 密钥 |
| `EMBEDDING_API_KEY` | 仅 15/25-27 | Embedding 调用 | 用于文档级语义对齐与 SIF 词向量质心 |
| `NEWS_PROCESS_RUN_ID` | 自动生成 | orchestrator + stage 子进程 | 单次运行的唯一 ID，用于日志聚合 |
| `STATA_PATH` | 仅用 `StataRunner` 时 | `papers/_common/stata_runner.py` | Stata 二进制绝对路径覆盖 |
| `PYTHONIOENCODING` | Windows 推荐 | 任何向 console 输出 Unicode 的脚本 | 设为 `utf-8` 避免 GBK 编码报错 |

## 2. API 密钥（4 个）

### 2a. 配置方法

复制模板：

```bash
cp news_process/.env.example news_process/.env
```

编辑 `news_process/.env`：

```bash
GPT5NANO_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXX
GEMINI3_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXX
CLAUDE4H_API_KEY=sk-ant-XXXXXXXXXXXXXXXXXXXXXXXX
EMBEDDING_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXX
```

### 2b. 在 YAML 中引用

`config/sentiment.yaml`:

```yaml
tone_llm_processing:
  # v6: 真三家族 (OpenAI + Google + xAI), 全部走 OpenLux 聚合代理
  models:
    - model_name: gpt-5-nano-2025-08-07
      short_name: gpt5nano
      base_url: https://api.openlux.ai/v1
      api_key: ${OPENLUX_API_KEY}    # ← 自动从 .env 替换
    - model_name: gemini-3-flash-preview-nothinking
      short_name: gemini3
      base_url: https://api.openlux.ai/v1
      api_key: ${OPENLUX_API_KEY}
    - model_name: grok-4-1-fast-non-reasoning
      short_name: grok41
      base_url: https://api.openlux.ai/v1
      api_key: ${OPENLUX_API_KEY}
```

`load_config()` 会用 `string.Template` 风格替换 `${VAR_NAME}` 占位符。
未定义的变量会保持字面量 `${UNDEFINED}` 不替换 — 此时 LLM 请求阶段
会因 invalid API key 失败，而不是 silent 跑通。

### 2c. 安全注意 ⚠️

* `.env` 已 gitignored（`.gitignore` 第 27-31 行）
* `.env.example` 是 tracked 模板，**只含变量名，无值**（whitelist 规则
  让它免于 ignore）
* **绝对不要**把真实密钥提交到 git
* CI/CD 环境通过环境变量注入，不创建 `.env` 文件

## 3. `NEWS_PROCESS_RUN_ID`

### 3a. 用途

orchestrator 启动时生成全局唯一 ID，所有子进程通过环境变量继承同一值，
让本次运行的所有 stage 日志聚合到同一目录：

```
news_process/logs/runs/<NEWS_PROCESS_RUN_ID>/
├── 00_preprocessing.log
├── 11_news_bank.log
├── 12_news_fintech.log
└── ...
```

### 3b. 自动生成格式

`run_pipeline_function.py:_generate_run_id()`:

```python
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
host = socket.gethostname().split(".")[0][:24]
rid = f"{ts}-{host}-{os.getpid()}"
# e.g. "20260504T080000Z-DESKTOP-12345"
```

### 3c. 父进程注入子进程的机制

orchestrator 启动时把 `NEWS_PROCESS_RUN_ID` 写入 `os.environ`：

```python
os.environ["NEWS_PROCESS_RUN_ID"] = rid
```

`subprocess.run()` 默认继承全部 `os.environ`，子进程的 `setup_logging()`
读取此变量并解析日志路径：

```python
# news_process/core/logging.py:setup_logging()
run_id = os.environ.get("NEWS_PROCESS_RUN_ID")
if run_id:
    log_dir = base_log_dir / "runs" / run_id
else:
    log_dir = base_log_dir   # legacy 单文件模式
log_dir.mkdir(parents=True, exist_ok=True)
```

### 3d. 手动覆盖

如果 CI 想用自己的 ID（例如 `gh-action-${RUN_NUMBER}`），先 export 即可：

```bash
export NEWS_PROCESS_RUN_ID="gh-action-${RUN_NUMBER}"
.venv/Scripts/python.exe news_process/run_pipeline_function.py
```

orchestrator 检测到已存在则保留，不覆盖。

## 4. `STATA_PATH`

### 4a. 用途

`papers/_common/stata_runner.py` 默认按操作系统探测 Stata 二进制：

* Windows: `C:/Program Files/Stata18/StataMP-64.exe`（优先 MP > SE > IC）
* macOS: `/Applications/Stata/Stata.app/Contents/MacOS/stata-mp`
* Linux: `/usr/local/stata18/stata-mp`

如果探测失败或你想用非默认路径：

```bash
export STATA_PATH="/path/to/stata-mp"
```

### 4b. 编程式覆盖

```python
from news_process.papers._common.stata_runner import StataRunner

# 优先级：构造参数 > STATA_PATH 环境变量 > 自动探测
runner = StataRunner(stata_path="/custom/path/stata-mp")
runner = StataRunner()  # 走环境变量或自动探测
```

## 5. `PYTHONIOENCODING`（Windows 强烈推荐）

Windows 默认 `cp936` (GBK) console 编码，向 stdout 打印中文 Unicode 时
**会**报 `UnicodeEncodeError`：

```bash
# Windows PowerShell — 推荐永久设置
[Environment]::SetEnvironmentVariable("PYTHONIOENCODING", "utf-8", "User")
```

或仅本次会话：

```bash
# Windows cmd
set PYTHONIOENCODING=utf-8

# Windows PowerShell
$env:PYTHONIOENCODING = "utf-8"

# Linux/macOS
export PYTHONIOENCODING=utf-8
```

Phase 4d 的 `split_config_yaml.py` 在 Windows 上首次运行时遇到此问题
（中文 ✓ checkmark 字符），现已被诊断并加入 troubleshooting list。

## 6. 验证环境变量已正确加载

```python
import os
from news_process.core.config import load_config

# .env 应已被 load_config 自动加载
cfg = load_config()

print("Run ID:", os.environ.get("NEWS_PROCESS_RUN_ID", "(not yet set)"))
print("API keys present:")
for key in ["GPT5NANO_API_KEY", "GEMINI3_API_KEY",
            "CLAUDE4H_API_KEY", "EMBEDDING_API_KEY"]:
    val = os.environ.get(key, "")
    print(f"  {key}: {'<present>' if val and not val.startswith('${') else '<MISSING>'}")
```

## 7. 见也

* `news_process/.env.example` — 模板文件
* [`core.config.load_config` API](../api/core.md)
* [`core.logging.setup_logging` API](../api/core.md)
* [配置拆分指南](../guides/config_split.md)
