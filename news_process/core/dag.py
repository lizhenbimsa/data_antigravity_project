"""news_process.core.dag — 声明式流水线 DAG.

Phase 1 交付物: ``StageSpec`` 数据类 + ``STAGES_MAIN`` / ``STAGES_VALIDATION``
列表。这两份列表是 "哪些阶段存在 / 何时运行" 的 **单源真值**;
``run_pipeline_function.py`` (主流水线执行器) 与
``run_pipeline_validation.py`` (验证执行器) 都从此处 import 自己的
``STAGES`` 常量, 并由 ``tests/integration/test_dag_consistency.py``
通过 ``is`` 身份比对验证两端绑定一致。

命名纪律: ``StageSpec`` 是 DAG 中使用的 *声明式* 记录 (frozen dataclass);
刻意与未来某 phase 将在 ``core/stage.py`` 引入的 *运行时* ``Stage``
抽象基类区分开, 以避免命名冲突。

``enabled_when`` 谓词机制保留供未来扩展, 但自 2026-06-13 起 **所有 StageSpec 均使用
默认 ``always_enabled``** (用户决策"全部启用而非条件启用": stage 21/22/23/24/18 与全部
14 个验证阶段均无条件常开, 对齐 2026-06-12 的 stage 23/24 先例)。各谓词函数保留为纯函数
仅供测试 / config 一致性提示复用。谓词必须是模块级 Python callable, 这样在多个 import
站点之间 ``is`` 身份比对才有意义 — DAG 一致性测试依赖这一点。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

# ----------------------------------------------------------------------------
# enabled_when 谓词集。声明在模块作用域, 以使 ``is`` 身份比对跨 import 站点
# 仍然成立 — DAG 一致性测试依赖此性质来确认两个 orchestrator 复用同一个
# 谓词对象。
# ----------------------------------------------------------------------------


def always_enabled(_cfg: dict[str, Any]) -> bool:
    """``enabled_when`` 谓词：始终启用（无配置依赖）。"""
    return True


def llm_method_enabled(cfg: dict[str, Any]) -> bool:
    """谓词：``sentiment_analysis.enabled_methods`` 是否含 ``tone_llms``。

    2026-06-13: stage 21 已改为无条件 always-on (用户决策: 全部启用而非条件启用,
    同 23/24 先例), 本谓词不再挂在任何 ``StageSpec.enabled_when`` 上, 也已从
    ``METHOD_TO_PREDICATE`` 移除; 保留为纯函数, 仅供测试与 config 一致性提示复用。
    """
    methods = (
        cfg.get('sentiment_analysis', {}).get('enabled_methods', []) or []
    )
    return 'tone_llms' in methods


def words_method_enabled(cfg: dict[str, Any]) -> bool:
    """谓词：``sentiment_analysis.enabled_methods`` 是否含 ``tone_words``。

    2026-06-13: stage 22 已改为无条件 always-on (用户决策: 全部启用而非条件启用,
    同 23/24 先例), 本谓词不再挂在任何 ``StageSpec.enabled_when`` 上, 也已从
    ``METHOD_TO_PREDICATE`` 移除; 保留为纯函数, 仅供测试与 config 一致性提示复用。
    """
    methods = (
        cfg.get('sentiment_analysis', {}).get('enabled_methods', []) or []
    )
    return 'tone_words' in methods


def berts_method_enabled(cfg: dict[str, Any]) -> bool:
    """谓词：``sentiment_analysis.enabled_methods`` 是否含 ``tone_berts``。

    2026-06-12 变更: stage 23 (BERT 文章级情感) 与硬依赖它的 stage 24 已改为
    **无条件 always-on** (用户决策: 全部启用, 不再条件启用)。本谓词因此不再挂在
    任何 ``StageSpec.enabled_when`` 上, 也已从 ``METHOD_TO_PREDICATE`` 移除;
    保留为纯函数, 仅供测试与 config 一致性提示复用。
    """
    methods = (
        cfg.get('sentiment_analysis', {}).get('enabled_methods', []) or []
    )
    return 'tone_berts' in methods


def _validation_flag(key: str, default: bool = True
                     ) -> Callable[[dict[str, Any]], bool]:
    """返回一个读取 ``cfg['validation'][key]`` 的谓词 (默认值 True)。"""
    def predicate(cfg: dict[str, Any]) -> bool:
        return cfg.get('validation', {}).get(key, default)
    predicate.__name__ = f"validation_{key}_enabled"
    return predicate


def article_staleness_enabled(cfg: dict[str, Any]) -> bool:
    """谓词：``article_staleness.enabled`` (历史 opt-in flag, 默认 False)。

    历史 (O2 sample-run finding 2026-05-25): stage 18 (semantic Faiss + surface
    MinHash 双指标) 依赖 faiss-cpu + datasketch 两个前置包, 曾以 config flag 显式
    opt-in (默认 disabled) 避免缺前置包时阻塞 pipeline; 依赖已于 2026-06-01 pip
    安装到位。

    2026-06-13: stage 18 已改为无条件 always-on (用户决策: 全部启用而非条件启用),
    本谓词不再挂在 ``StageSpec.enabled_when`` 上, 保留为纯函数仅供测试复用。
    ⚠ always-on 后若 faiss-cpu / datasketch 缺失, stage 18 会真崩 (不再优雅跳过) —
    运行环境须确保两包已安装。
    """
    return cfg.get('article_staleness', {}).get('enabled', False)


# 验证模块谓词句柄集 — 仅在模块作用域声明一次, 以使 `is` 身份比对跨 import 站点成立。
# 2026-06-13: 全部 14 个验证阶段已改为无条件 always-on (用户决策: 全部启用而非条件启用),
# 这些句柄不再挂在任何 StageSpec.enabled_when 上, 保留为纯机械件仅供测试 / config 一致性复用。
_VALIDATION_PREDS: dict[str, Callable[[dict[str, Any]], bool]] = {
    'threshold_sensitivity': _validation_flag('threshold_sensitivity'),
    'dedup_sensitivity': _validation_flag('dedup_sensitivity'),
    'classification_eval': _validation_flag('classification_eval'),
    'sentiment_validation': _validation_flag('sentiment_validation'),
    'radius_sensitivity': _validation_flag('radius_sensitivity'),
    'entity_masking': _validation_flag('entity_masking'),
    'dict_coverage_audit': _validation_flag('dict_coverage_audit'),
    'media_diversity': _validation_flag('media_diversity'),
    'prompt_sensitivity': _validation_flag('prompt_sensitivity'),
    'inter_track_kappa': _validation_flag('inter_track_kappa'),
    'construct_orthogonality': _validation_flag('construct_orthogonality'),  # v3.5.0 D3 stage 39c
    'lexical_discriminant_validity': _validation_flag('lexical_discriminant_validity'),  # v3.5.1 stage 39d
    'lm_discriminant_validity': _validation_flag('lm_discriminant_validity'),  # v3.5.2 PR #4 stage 39e (LM 6 子词典 HTMT)
    'cross_media_alpha': _validation_flag('cross_media_alpha'),  # v3.7.0 PR #12 stage 39f (Krippendorff α + variance)
}


# ----------------------------------------------------------------------------
# StageSpec — 声明式 DAG 记录。
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class StageSpec:
    """单个流水线阶段的声明式描述符。

    Attributes:
        name:         人类可读的阶段标签 (用于日志、摘要)。
        script:       相对于项目根的文件名 (``"00_preprocessing.py"``)。
        group:        ``"main"`` | ``"validation"`` | ``"feature"``。
        kind:         自由格式的类别标签。
        timeout:      子进程超时秒数。
        enabled_when: 谓词 ``(cfg) -> bool``, 决定运行时是否纳入该阶段;
                      无条件运行的阶段使用 ``always_enabled``。

    Phase 1 刻意不填充 ``inputs`` / ``outputs`` 字段;
    Phase 2d 将通过 ``core.schemas.OUTPUT_REGISTRY`` 串接二者。
    """

    name: str
    script: str
    group: str
    kind: str = "stage"
    # P-072 修复 (v3.7.1): 默认 3600s 在长 stage (22/23/24/51 全语料) 上会被父端 SIGKILL,
    # 留下 partial parquet (见旧 stage 21 注释 L208-212 自承). 提至 7200s 给非 LLM 类
    # stage 留 buffer; LLM/embedding 类继续显式设 21600.
    timeout: int = 7200
    enabled_when: Callable[[dict[str, Any]], bool] = always_enabled


# ----------------------------------------------------------------------------
# STAGES_MAIN — 生产流水线 DAG (run_pipeline_function)。
# 镜像 run_pipeline_function.py:run_pipeline() 的 stages 列表;
# 配置驱动的条件分支通过 enabled_when 谓词捕获。
# ----------------------------------------------------------------------------


STAGES_MAIN: list[StageSpec] = [
    # ── 模块一：新闻预处理模块 ──
    StageSpec(
        name="阶段00: 数据预处理",
        script="00_preprocessing.py",
        group="main", kind="preprocess",
        timeout=10000,
    ),

    # ── 模块二：新闻筛选模块 ──
    StageSpec(
        name="阶段11: 银行新闻判断",
        script="11_news_bank.py",
        group="main", kind="filter",
    ),
    StageSpec(
        name="阶段12: 金融科技新闻判断 + 全量分类结果",
        script="12_news_fintech.py",
        group="main", kind="filter",
    ),
    # 2026-06-15: stage 12b 银行×金科邻近共现硬过滤 (Andreou et al. 2026) — 只保留
    # 目标银行与 ≥1 金科词在 ±sentence_radius 句窗口内邻近共现的文章行, 降低 stage 12
    # 关键词判定的虚假相关; 下游 stage 13 改读其输出, 三轨情感/强度链天然继承过滤。
    StageSpec(
        name="阶段13: 银行×金科邻近共现预过滤 (Andreou et al. 2026)",
        script="13_cooccurrence_filter.py",
        group="main", kind="filter",
    ),
    # v3.6.0 (Plan E P4 A1): stage 13 物化 content_ctx 列, 让下游 14/15
    # 在 stage 21 之前即可消费 ctx, 实现真双轨化 (B1 + B2 闭合; 后于 v3.9.0 扩为三轨)。
    # v3.9.0 (2026-06-14): 同一阶段再物化第三轨 content_ss (银行+金科同句共现轨)
    # + ss_is_fallback 旗标 — 取"标题 + 含目标银行∧金科词同句 ±N 句窗"; 无共现→
    # 镜像 ctx 回退公理写全文 body。下游 14/15 自此消费 full/ctx/ss 三轨。
    StageSpec(
        name="阶段14: 实体特异性上下文物化 (content_ctx / content_ss 三轨)",
        script="14_materialize_ctx.py",
        group="main", kind="filter",
    ),
    StageSpec(
        name="阶段15: 金融科技技术重度评分 (TF-IDF, 三轨 full/ctx/ss)",
        script="15_fintech_intensity.py",
        group="main", kind="filter",
    ),
    StageSpec(
        name="阶段16: 文章级政策语义对齐度",
        script="16_article_policy_alignment.py",
        group="main", kind="filter",
        timeout=7200,  # 阶段内含 Embedding API 调用
    ),
    # ── 模块三：新闻情感模块 ──
    # 21 (LLM) / 22 (词典) / 23 (BERT) / 24 (跟风衰减) 自 2026-06-13 起全部为无条件
    # always-on (用户决策"全部启用而非条件启用", 对齐 2026-06-12 的 23/24 先例);
    # 不再受 sentiment_analysis.enabled_methods 控制 (见下方注释)。
    # v3.9.0 (2026-06-14): stage 21-24 全部三轨化 (full/ctx/ss) — 第三轨 _ss 读
    # stage 13 物化的 content_ss; LLM prompt v8 字节冻结, 仅 content 实参换 content_ss;
    # ss 为结构性 always-on (无独立 compute 开关), 与 full/ctx 并列第三主轨。
    StageSpec(
        name="阶段21: 统一 LLM 语义精筛与情感分析 (三轨 full/ctx/ss)",
        script="21_tone_llms.py",
        group="main", kind="sentiment",
        # v3 / Fix 1: 6h 子进程硬超时. 已知工况 ~7200s (run_pipeline_function
        # CLI help 自承), 留 3x 安全余量覆盖冷缓存 / 全样本 / 单 yunwu 账户雪崩
        # 后的指数退避. 若全样本冷缓存仍不够, 调高此值即可 (一行修改).
        # 旧值 (StageSpec.timeout=3600 默认) 与已知工况冲突, 会被父端
        # proc.kill() 强杀, 留下 partial parquet.
        timeout=21600,
    ),
    StageSpec(
        name="阶段22: 词典法情感分析",
        script="22_tone_words.py",
        group="main", kind="sentiment",
    ),
    # 2026-06-12 用户决策: BERT 文章级情感"全部启用, 不再条件启用" — stage 23
    # 改为无条件 always-on (省略 enabled_when, 取 StageSpec 默认 always_enabled,
    # 同 stage 30a), 不再受 sentiment_analysis.enabled_methods 是否含 'tone_berts'
    # 控制。berts_method_enabled 谓词已从 METHOD_TO_PREDICATE 一并移除。
    StageSpec(
        name="阶段23: BERT模型情感分析",
        script="23_tone_berts.py",
        group="main", kind="sentiment",
    ),

    # ── 模块四b：跟风衰减权重 (硬依赖 stage 23 BERT 输出) ──
    # stage 24 内部硬编码读 23_bert_tone.parquet (见 pipeline/sentiment/herd_decay.py
    # main(): input_filename=filenames.get('output_23_bert_tone', '23_bert_tone.parquet');
    # 输入契约 docstring L59/L86)。因 stage 23 自 2026-06-12 起
    # 已是无条件 always-on, 其硬依赖者 stage 24 同样改为 always-on — 二者构成
    # 结构性 always-on 链, 不再随 enabled_methods 启停。
    #
    # 设计意义: stage 45 panel runner 亦硬依赖 24_herd_decay.parquet (见
    # pipeline/panel/runner.py 的 main(): 读 24_herd_decay.parquet, 缺文件即 sys.exit(1))。把 23/24 提升为 always-on 后, 无论
    # enabled_methods 如何配置, 该输入始终生成, stage 45 不会再因缺输入而
    # sys.exit(1) — 这正是本次"全部启用而非条件启用"决策消除的脆弱耦合
    # (此前由 berts_method_enabled 谓词条件启停时存在该崩溃路径)。
    StageSpec(
        name="阶段24: 跟风衰减权重",
        script="24_herd_decay_processor.py",
        group="main", kind="sentiment",
    ),

    # ── 模块四c：text2vec 稳健性指标 — 已退役 (2026-05-29 双模型重构) ──
    # legacy (main vs _t2v) by design: 此处"双轨"指 main embedding × text2vec 稳健 twin
    # 这条嵌入模型轴 (strat_diff_t2v / policy_cosine_sim_t2v), 与 full/ctx/ss 文本轨
    # 是两个独立编号空间, 勿混淆; 阶段已退役, 不参与 v3.9.0 三轨化。
    # 原 stage 30 (30_robustness_text2vec) 单独用 text2vec 计算 strat_diff_t2v /
    # policy_cosine_sim_t2v 4 列稳健 twin。改为"主阶段内联双模型计算"后, 这些 _t2v
    # 列由 stage 15 (policy_alignment) + stage 25 (strategic_diff) 在主流程内直接产出
    # (main=text-embedding-3-small / robustness=text2vec 同源同算法), stage 30 因此
    # 完全冗余而退役。详见 config/features.yaml embedding_robustness + runner.py 8e 段。
    # v3.7.0 PR #9 (D 组前置): article-level SBERT 持久化.
    # 把 stage 30 内部计算后即丢的 article embeddings 持久化, 让 D1/D2/D3
    # 三 stage 直接复用 (节省 ~12-15 h 计算).
    StageSpec(
        name="阶段25: Article-level SBERT 持久化 (D 组前置)",
        script="25_article_sbert.py",
        group="main", kind="robustness",
        timeout=21600,  # 40 万文章: GPU 约 4-6 小时, CPU 约 12-24 小时
    ),
    # v3.7.0 PR #11+#11.5 (D2.a + D2.b): article staleness 双指标.
    # 学术依据: Tetlock (2011) RFS 24(5):1481-1512; Gentzkow-Kelly-Taddy (2019) JEL.
    # 2026-06-13: 改为无条件 always-on (用户决策: 全部启用而非条件启用); 历史 opt-in flag
    # article_staleness.enabled 仅作记录。⚠ 依赖 faiss-cpu + datasketch (已于 2026-06-01
    # pip 安装到位); always-on 后若缺包会真崩, 运行环境须确保两包已安装。
    StageSpec(
        name="阶段26: Article-level staleness 双指标 (surface MinHash + semantic Faiss)",
        script="26_article_staleness.py",
        group="main", kind="robustness",
        timeout=21600,  # MinHash + Faiss 在 400k 文章上 4 h
    ),

    # ── 模块五：面板数据构建 (单文件入口, 内部串行执行 7 个子步) ──
    # Plan P1-6 (保守版): StageSpec.name 显式列出 panel runner 内部
    # 41 → 42 → 43 → 44 → 46 → 47 → 45 子步语义, 让日志/摘要可读;
    # 文件名维持单文件入口 ``40_panel_export_main.py`` (重编号后外部 CLI 契约即 ``python 40_*``).
    # 真正拆分为 7 个独立 stage (子进程隔离 + OUTPUT_REGISTRY 重整) 留待 v3.0
    # 与 thin shim 退役同期完成 (Plan 选项 B).
    StageSpec(
        name=(
            "阶段40 (内含 41+42+43+44+46+47): "
            "Bank-Year 面板编排器 — 41 编码聚合 → 42 媒体注意力 → "
            "43 地理缓冲 → 44 Bartik IV/DID → 46 网络溢出 → "
            "47 经纪网络 → 45 诊断与多格式导出"
        ),
        script="40_panel_export_main.py",
        group="main", kind="panel",
        timeout=7200,  # 阶段内含 Stage 25/26/27 Embedding 计算
    ),

    # ── v3.2.0 M6 (plan v14 §9.1): Stata 数据导出层 ──
    # parquet → .dta + variable/value labels + codebook .xlsx
    # 依赖 stage 45 (panel parquet) 完成
    StageSpec(
        name="阶段46: Stata 数据导出 (pyreadstat .dta + labels)",
        script="46_stata_export.py",
        group="main", kind="export",
        timeout=600,  # 跨平台 pyreadstat 写 .dta, 小面板 (~168 行) < 1 分钟
    ),

    # ── 模块六：伪造检验 ──
    StageSpec(
        name="阶段51: 伪造检验对照变量构建",
        script="51_falsification_test.py",
        group="main", kind="falsification",
    ),
]


# ----------------------------------------------------------------------------
# STAGES_VALIDATION — 稳健性/验证执行器 (run_pipeline_validation)。
# 2026-06-13: 全部 16 个验证阶段均为无条件 always-on (用户决策: 全部启用而非条件启用);
# 此前 14 个由 _VALIDATION_PREDS 谓词条件启停的阶段已全部省略 enabled_when, 取 StageSpec
# 默认 always_enabled (另 32 / 38b 本就无 flag)。_VALIDATION_PREDS 句柄保留为纯机械件供
# 测试复用, 不再挂在任何 StageSpec 上。
# ----------------------------------------------------------------------------


STAGES_VALIDATION: list[StageSpec] = [
    StageSpec(
        name="阶段60: 阈值敏感性分析",
        script="60_bank_fintech_threshold.py",
        group="validation", kind="sensitivity",
    ),
    StageSpec(
        name="阶段61: 人工抽样验证样本生成",
        script="61_news_llms_human.py",
        group="validation", kind="human",
        # always_enabled — 历史 runner 对 stage 32 没有专门的 flag
    ),
    StageSpec(
        name="阶段62: 去重阈值敏感性分析",
        script="62_dedup_threshold_sensitivity.py",
        group="validation", kind="sensitivity",
        # 全量语料 (去重前 _cache, ~数百万行) 上对 5 个阈值 (0.70/0.75/0.80/0.85/0.90)
        # 各做一次精确+近似去重;
        # MinHash 签名已优化为 5 阈值共用一次 (validation/dedup_threshold.py), 但 LSH
        # 构建 + 查询时间窗口仍逐阈值跑一遍, 全量下单遍即 ~1-1.5h → 默认 7200s (2h)
        # 远不够 (生产 stage 00 单遍去重 ~400k 文章即预算 6h)。提到 12h 安全上限,
        # 与最大长跑阶段对齐; 这是硬超时上限 (跑完即退), 非期望运行时长。
        timeout=43200,
    ),
    StageSpec(
        name="阶段63: 分类有效性评估",
        script="63_news_llms_evaluation.py",
        group="validation", kind="evaluation",
    ),
    StageSpec(
        name="阶段64: 情感三角验证",
        script="64_tone_validation.py",
        group="validation", kind="evaluation",
    ),
    StageSpec(
        name="阶段65: 窗口半径敏感性检验",
        script="65_radius_sensitivity.py",
        group="validation", kind="sensitivity",
    ),
    StageSpec(
        name="阶段66: Entity Masking 稳健性测试",
        script="66_entity_masking_test.py",
        group="validation", kind="robustness",
        # 三轨 (full/ctx/ss) 掩码复判最多 1,000 × 3 × 3 = 9,000 次 LLM 请求
        # (v3.9.0: entity_masking TRACKS 由 full/ctx 扩为 full/ctx/ss)。
        # 冷缓存 + 网关限流下会超过默认 3,600s, 必须显式放宽。
        timeout=21600,
    ),
    StageSpec(
        name="阶段67: 金融科技词典覆盖率审计",
        script="67_dict_coverage_audit.py",
        group="validation", kind="audit",
    ),
    StageSpec(
        name="阶段68: 媒体名称与地域多样性审计",
        script="68_media_diversity.py",
        group="validation", kind="audit",
    ),
    StageSpec(
        name="阶段69: 距离衰减权重敏感性检验",
        script="69_decay_sensitivity.py",
        group="validation", kind="sensitivity",
        # always_enabled — 历史 runner 对 38b 没有专门的 flag
    ),
    StageSpec(
        name="阶段70: Prompt措辞敏感度测试",
        script="70_prompt_sensitivity.py",
        group="validation", kind="robustness",
        # 4 个 prompt 变体 × 1,000 样本 × 3 模型 × 3 轨道 (full/ctx/ss) = 36,000
        # 次请求 (v3.9.0: prompt_sensitivity 由 2 轨扩为三轨)。该阶段有增量 LLM
        # 缓存, 但冷缓存完整跑通需要长超时。
        timeout=43200,
    ),
    StageSpec(
        name="阶段71: Inter-track Cohen's κ for innovation dimensions",
        script="71_inter_track_kappa.py",
        group="validation", kind="audit",
        # 仅 article-level κ + bootstrap CI; 一秒级运行
    ),
    StageSpec(
        name="阶段72: NMI 三 construct 正交性测度 + permutation null (v3.5.0 D3)",
        script="72_construct_orthogonality.py",
        group="validation", kind="audit",
        # 在 N≈40 万标签上做 bootstrap 1000 次 + permutation 1000 次;
        # 单线程约 70 分钟, 64 核 MP 上 n_jobs=16 约 5 分钟
        # (依据 plan §2.2.2 性能估算 + F31 推荐默认值)。
        timeout=10800,  # 3 小时上限 — 覆盖最坏情况并留余量
    ),
    StageSpec(
        name="阶段73: A1/A3 lexical discriminant validity (HTMT + AVE + κ + α; v3.5.1)",
        script="73_lexical_discriminant_validity.py",
        group="validation", kind="audit",
        # 在 N≈9000 个 bank-year 面板观测上做成对 on-disk HTMT;
        # 单线程 < 1 分钟的轻量任务 (依据 plan v0.3 §2.3 修 R7-H3 + R8-H3)。
        # Permutation 1000 次, seed=42 (修 R9-H3)。
        timeout=900,  # 15 分钟上限
    ),
    # v3.5.2 PR #4: LM 6 子词典 (uncert/litig/constr/modal_strong/modal_weak/complexity) HTMT.
    # Henseler-Ringle-Sarstedt (2015) JAMS 43(1) 双 cutoff 0.85/0.90.
    StageSpec(
        name="阶段74: LM 6 子词典 discriminant validity (HTMT + Cronbach α + permutation)",
        script="74_lm_discriminant_validity.py",
        group="validation", kind="audit",
        timeout=900,  # 15 分钟上限, 仿 39d
    ),
    # v3.7.0 PR #12 (D3): Cross-media tone variance + Krippendorff α.
    # ⚠ 与第 10 篇 bank_media_disagreement 重叠; 同时输出 variance (main 候选)
    # + α (robustness), 启用前对齐 spec.
    StageSpec(
        name="阶段75: Cross-media tone variance + Krippendorff α (v3.7.0 D3)",
        script="75_cross_media_alpha.py",
        group="validation", kind="audit",
        timeout=3600,  # 60 分钟上限, 含事件检测 + 媒体源聚合
    ),
]


# ----------------------------------------------------------------------------
# 供 orchestrator / 测试使用的便捷工具函数。
# ----------------------------------------------------------------------------


def filter_enabled(stages: list[StageSpec],
                   config: dict[str, Any]) -> list[StageSpec]:
    """返回 ``stages`` 中 ``enabled_when(config)`` 为 True 的子集。"""
    return [s for s in stages if s.enabled_when(config)]


# ----------------------------------------------------------------------------
# v3 / Fix 2: METHOD_TO_PREDICATE 单一真源化
# ----------------------------------------------------------------------------
# 历史上 ``run_pipeline_function.py`` 持有一份本地的
# ``_sentiment_method_to_script`` 字典 (line 214-218), 与 dag.py 中已有的
# ``llm_method_enabled / words_method_enabled / berts_method_enabled`` 三个
# 谓词构成"第三份事实来源" — 任一处漂移都会让"未启用阶段陈旧文件清理"
# 与"DAG 阶段筛选"的语义不一致。
#
# Fix 2 把 method ↔ predicate 映射收回 dag.py (对称于已有的
# ``_VALIDATION_PREDS``), 并通过 ``get_script_for_method()`` 公共函数把
# script 名反查也封装在 dag.py 内部 — orchestrator 仅消费, 不再维护。
#
# 2026-06-12: ``tone_berts`` 从本映射移除 — stage 23/24 已改为无条件 always-on
# (结构性阶段, 不再是可由 enabled_methods 切换的 method), 故不参与 orchestrator
# 的"未启用 method 陈旧文件清理"循环。
#
# 2026-06-13: ``tone_llms`` / ``tone_words`` 亦一并移除 — stage 21/22 已改为
# 无条件 always-on (用户决策"全部启用而非条件启用", 对齐 23/24 先例), 不再受
# sentiment_analysis.enabled_methods 控制。三种情感方法现全部为结构性 always-on,
# 本映射因此为空 {}; ``get_script_for_method`` 恒返回 None, orchestrator 的
# "未启用 method 陈旧文件清理"循环已随 run_pipeline_function.py 一并退役。
# 白话: LLM / 词典 / BERT 三种情感方法现在都"焊死常开", 配置清单关不掉它们,
#       这个映射就空了 — 没有"被关掉的方法"需要清理残留文件。
METHOD_TO_PREDICATE: dict[str, Callable[[dict[str, Any]], bool]] = {}


def get_script_for_method(method: str) -> Optional[str]:
    """根据 sentiment method 名反查 STAGES_MAIN 中对应 stage 的 script.

    2026-06-13: ``METHOD_TO_PREDICATE`` 已为空 (三种情感方法全部 always-on),
    故本函数当前恒返回 None; 保留供未来扩展与测试复用。

    依赖性质: ``StageSpec.enabled_when`` 必须是 ``METHOD_TO_PREDICATE``
    中登记的某个模块级谓词 (``is`` 身份比对); 这一性质由
    ``tests/integration/test_dag_consistency.py::
    test_predicate_identity_module_scope`` 强制守护。

    Returns:
        - 找到对应 stage 时返回其 script 文件名 (例如 ``'21_tone_llms.py'``).
        - method 名未在 ``METHOD_TO_PREDICATE`` 登记 → ``None``
          (调用方应视为配置错误).
        - method 已登记但 STAGES_MAIN 中找不到对应谓词的 stage → ``None``
          (理论上不应发生; 由 ``test_method_to_predicate_covers_sentiment_specs``
          强制守护).
    """
    pred = METHOD_TO_PREDICATE.get(method)
    if pred is None:
        return None
    for spec in STAGES_MAIN:
        if spec.enabled_when is pred:
            return spec.script
    return None
