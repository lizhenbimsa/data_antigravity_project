# 基于国际顶刊标准的 News Process 级联架构与计量经济学深度改进报告 (Part 5, 6 & 7)

*本篇为两万字深度诊断报告的最终部分。包含系统健壮性加固、面向最高级别学术审查的可复现性机制，以及具体的实施路线图规划。*

---

## 维度五：系统健壮性、Fail-Fast 机制与容灾恢复（System Robustness）

当前脚本持续运行超过 2.5 小时，这在生产环境和学术大规模计算中是高危状态。一旦在最后 10 分钟发生 API 断连或 Out of Memory (OOM)，所有的计算时间和算力成本都将沉没。

### 5.1 OOM 与计算资源的动态降级策略 (Dynamic Degradation)
*   **当前缺陷**：
    在 `15_article_policy_alignment.py` 或大规模向量计算时，如果显存（VRAM）或内存打满，当前 Python 进程会直接被操作系统（OS）通过 `SIGKILL` 杀死，导致整个 pipeline 瞬间崩溃且无任何现场保留。
*   **重构方案 (防御性内存管理)**：
    *   **内存水位监控与动态 Batch Size**：引入 `psutil` 模块实时监控系统内存（RAM）。当可用内存低于 15% 时，系统不仅要触发 Warning，更要自动将向量处理的 `batch_size` 减半（如从 512 降为 256），实现**动态降级（Graceful Degradation）**而非直接宕机。
    *   **大内存对象主动回收**：在每一轮大体量矩阵运算（如余弦相似度计算）后，强制执行 `del` 操作并显式调用 `gc.collect()` 配合 `torch.cuda.empty_cache()`（如果使用 GPU）。

### 5.2 API 限流（Rate Limiting）的反脆弱设计与智能退避
*   **当前缺陷**：
    虽然有基础的并发限制，但面对不同云厂商（OpenAI, Kimi, 智谱）复杂多变的限流策略（Tokens-per-Minute / Requests-per-Minute 双重限流），当前的重试逻辑相对僵硬，容易触发封号或引发长期阻塞（Deadlock）。
*   **重构方案 (高并发弹性网络)**：
    *   **基于 Token 消耗预测的漏桶算法 (Leaky Bucket / Token Bucket)**：不能仅限制请求次数，必须在上游（请求发出前）预估 Prompt 的 Token 数量，精准控制每分钟发出的 Token 流量。
    *   **Jitter 指数退避与多 Key 轮询 (Key Rotation)**：在发生 `429 Too Many Requests` 时，采用增加随机抖动（Jitter）的指数退避机制，防止“惊群效应（Thundering Herd Problem）”。同时，实现多 API Key 池的无缝热切换（Hot Swap）。

### 5.3 检查点（Checkpoint）的原子性与中间态污染防范
*   **当前缺陷**：
    当程序向 CSV/Pickle 写入时发生崩溃（如断电或强制中止），目标文件将被损坏（只写入了一半），导致下次重新运行（Fail-Fast 恢复）时加载到脏数据，严重污染计量结果。
*   **重构方案 (原子写入)**：
    *   **Write-Ahead Logging (WAL) 与临时文件重命名**：任何数据写入必须先写入 `.tmp` 文件。当且仅当 100% 写入成功并通过 Hash 校验后，再使用操作系统的原子级重命名命令（`os.replace`）将其重命名为最终结果文件（如 `.parquet`）。这确保了 Checkpoint 永远处于**绝对完整（Atomic）**的状态。

---

## 维度六：面向顶刊的可复现性与学术审计（Reproducibility & Academic Audit）

《美国经济评论》（AER）和《金融学杂志》（JF）等顶刊现已强制要求提供所有代码和可运行的数据包以备审计。大模型（LLM）由于其“黑盒”和“在线更新”特性，成为了学术复现的“重灾区”。

### 6.1 Prompt 漂移检测与 LLM 版本绝对锁定
*   **当前缺陷**：
    调用 `gpt-4o` 或 `kimi-latest` 时，模型服务商会在后台悄悄进行权重微调（Fine-tuning）。这意味着 3 个月前跑出的情感分析结果，与审稿人 3 个月后用你的代码重新跑出的结果可能存在显著差异（Prompt Drift）。
*   **重构方案 (版本固化)**：
    *   **绝对禁止使用指向型指针模型（如 `gpt-4o`）**：在生产代码中，必须硬编码指向具体的冻结快照版本（如 `gpt-4o-2024-05-13`），并在论文中详细声明。
    *   **Prompt MD5 版本控制**：任何对 Prompt 哪怕一个标点符号的修改，都必须导致 Prompt Hash（如 MD5）的改变，并与生成的数据强绑定记录在案，实现“Prompt 即代码 (Prompt-as-Code)”的溯源。

### 6.2 随机种子（Seed）的跨平台确定性传递
*   **重构方案**：
    除了 LLM API 传入 `seed`，本地环境的 `numpy.random.seed`, `torch.manual_seed` 以及 Python 自身的 `PYTHONHASHSEED` 都必须在 pipeline 的入口脚本（如 `run_pipeline_function.py` 的第一行）进行全局锁定，以确保在 Linux (服务器) 和 Windows (当前本地机器) 环境下切分数据集的绝对一致性。

### 6.3 审计日志（Audit Log）的代码化与特征漂移（Data Drift）校验
*   **重构方案**：
    摒弃传统的仅记录 `INFO` 或 `ERROR` 的文本 Log，采用 `MLflow` 或 `Weights & Biases (W&B)` 框架。将每一次 Pipeline 运行的统计量（均值、方差、缺失率）自动上报。一旦修改代码导致最终的“金融洗绿指数（Fintech Washing Index）”均值发生大于 1% 的偏离，立刻发出警报。

---

## 维度七：实施路线图与优先级矩阵（Implementation Roadmap）

基于以上两万字维度的深度剖析，为了不干扰当前的研究进度，建议按照以下三步走（Phases）逐步进行手术式重构：

### 阶段一：抢救性重构（高优先级，低重构成本）
*目标：解决跑得慢、容易崩、难以复现的问题。*
1.  **数据格式迁移**：将所有中间产物从 `.csv` 替换为 `.parquet`，将重度 Pandas `merge` 替换为 `Polars` 引擎。（预期提速 50-100 倍，内存消耗减半）
2.  **原子化 Checkpoint**：落实 `.tmp` 写入重命名机制，彻底告别数据脏写。
3.  **固化 LLM 版本参数**：审查全网的 API 接口调用，将 `model="Kimi-latest"` 替换为特定日期快照，并强制写入 `temperature=0` 和 `seed`。

### 阶段二：计量经济学加固（中优先级，高学术回报）
*目标：应对审稿人的内生性与稳健性挑战。*
1.  **特征颗粒度升级**：实现滑动窗口“Chunk-then-Pool”，废弃直接截断或均值合并。
2.  **RAG 双轨验证**：重写 Fintech Washing 的定义逻辑，采用基于事实（研发、专利）对比的大模型 Agent 流，取代单一的词典法。
3.  **前瞻性偏差修复**：在合并报表与新闻数据时，建立基于交易日历的严格时间滞后匹配逻辑（Rolling Window Lags）。

### 阶段三：工业级调度架构重塑（低优先级，长期基础建设）
*目标：支撑十亿级规模数据与多模态扩展。*
1.  **全面引入 DAG 引擎**：废弃 `run_pipeline_function.py` 的线性 `try-except` 架构，使用 `Prefect` 进行任务的分布式编排。
2.  **工具变量 (IV) / Heckman 第一阶段的前置集成**：构建自动化生成“控制组匹配基准（DTW 距离）”和“被报道概率（IMR）”的基础设施。

---
*（报告全篇完毕。整个深度报告已分阶段拆分并保存至本项目的 docs 目录下，供学术团队审查与架构师评估。）*
