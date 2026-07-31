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

    W5/W6 (2026-06-25): 新增可选 ``inputs`` / ``fingerprint_cols`` 字段 (向后兼容
    默认空, 不破 ``test_dag_consistency``), 作通用 ``--skip-unchanged`` 的声明式依赖
    元数据。⚠ 当前 W5 skip 的安全网是 ``run_pipeline_function`` 主循环的"前缀守卫"
    (任一上游阶段本次真跑过 → 下游一律不跳) + config/资源/input_hashes 三重哈希门,
    **不依赖** ``inputs`` 人工编排的正确性 (规避 CF-7 类误编排); ``inputs`` 仅作文档/未来用。
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
    # W5/W6: 通用 --skip-unchanged 的声明式依赖元数据 (向后兼容默认空; 见类 docstring)。
    inputs: tuple[str, ...] = ()
    fingerprint_cols: tuple[str, ...] = ()


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
        # F19 (2026-07-26): 旧 10000s 对**冷缓存全量重解析**实测 6,708s (111.8 min,
        # 2026-07-24) 只剩 1.49× 余量 —— 热缓存趟本轮 3,785s 看似宽裕是假象。提至 6h。
        timeout=21600,  # 热缓存实测 3,785s / 冷缓存全量重解析实测 6,708s
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
    # 2026-06-15: stage 12b 银行×金科邻近共现硬过滤 (Andreou et al. 2026) — 生产默认只保留
    # 目标银行与 ≥1 金科词在【±1 句窗口】(命中句前后各 1 句) 内邻近共现的文章行
    # (sentence_radius=1 = ±1 句窗口邻近; radius=0 严格同句为最严特例稳健性备选), 降低 stage 12
    # 关键词判定的虚假相关; 下游 stage 13 改读其输出, 三轨情感/强度链天然继承过滤。
    StageSpec(
        name="阶段13: 银行×金科邻近共现预过滤 (Andreou et al. 2026)",
        script="13_cooccurrence_filter.py",
        group="main", kind="filter",
    ),
    # fix(D5, 2026-07-14): 下两条历史注释原写"stage 13 物化"是重编号残留 (12b→13→14
    # 历次重排后串号)——物化动作实际发生在**本 StageSpec (阶段14)**, stage 13 只做
    # 共现硬过滤不物化文本列 (SSOT 见 CLAUDE.md「当前状态铁律」)。
    # v3.6.0 (Plan E P4 A1): 阶段14 物化 content_ctx 列, 让下游 14/15
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
        # fix(2026-07-24): 生产规模语料下本阶段曾被默认 7200s 父端强杀 (九入口编排 ②
        # 于 00:41:30 中断)。当时工况 (logs/15_fintech_intensity.log):
        #   ① 全局 DF: 164.3 万篇唯一文档 jieba 整词分词 = 6509s (~1h48m, 占 90%);
        #   ② IDF×CosSim 权重 + 关键词嵌入 (词表级 607 词, LLMCache 命中即 $0): 秒级;
        #   ③④ 24.2 万篇 × 三轨 × co-primary 双嵌入空间逐文档打分 ≈ 3240s (~54min)。
        # 根因 = jieba.cut 纯 Python 持 GIL, 而分词并行原走 prefer='threads' → 32 核退化
        # 单核 (故 DF 慢到 1h48m)。已双管齐下修复:
        #   (a) fintech_intensity.py §1b: 分词并行改工况自适应后端 — 大工况 (>=16 批,
        #       生产语料) 走 loky 进程后端真并行绕 GIL, 小工况 (测试) 留线程免 spawn 开销;
        #       字节等价经真数据 A/B 实证 (DF/TF/打分 thread==process 逐字节); DF/打分实测
        #       提速数倍~数十倍 → 全阶段 ~2.9h 降到分钟级, 亦覆盖全量普查规模 (约1819万/T=19)。
        #   (b) 本 timeout 显式提至 21600s (6h, 对齐 21/25/26 重阶段档) 作安全上限 —
        #       (a) 后余量已极大, 保留高上限仅为兜底真挂起/宿主极端争用, 非常态需要。
        timeout=21600,
    ),
    StageSpec(
        name="阶段16: 文章级政策语义对齐度",
        script="16_article_policy_alignment.py",
        group="main", kind="filter",
        # F19 (2026-07-26 生产实测校准): 本阶段生产实测 **3659s**, 旧 7200s 仅剩 1.97× 余量。
        # 其耗时主体是「嵌入+余弦 3614s (99.4%)」—— 全命中缓存下仍需逐条取数+JSON 解析
        # 145.2 万次。提至 21600s (6h) 对齐 15/21/25/26 重阶段档。
        timeout=21600,  # 生产实测 3659s; 阶段内含 Embedding API 调用 (全命中亦耗时)
    ),
    # ── 模块三：新闻情感模块 ──
    # 21 (LLM) / 22 (词典) / 23 (BERT) / 24 (跟风衰减) 自 2026-06-13 起全部为无条件
    # always-on (用户决策"全部启用而非条件启用", 对齐 2026-06-12 的 23/24 先例);
    # 不再受 sentiment_analysis.enabled_methods 控制 (见下方注释)。
    # v3.9.0 (2026-06-14): stage 21-24 全部三轨化 (full/ctx/ss) — 第三轨 _ss 读
    # 阶段14 物化的 content_ss (fix(D5, 2026-07-14): 原写"stage 13"是重编号残留,
    # 物化在阶段14非13); LLM prompt v8 字节冻结, 仅 content 实参换 content_ss;
    # ss 为结构性 always-on (无独立 compute 开关), 与 full/ctx 并列第三主轨。
    StageSpec(
        name="阶段21: 统一 LLM 语义精筛与情感分析 (三轨 full/ctx/ss)",
        script="21_tone_llms.py",
        group="main", kind="sentiment",
        # v3 / Fix 1: 6h 子进程硬超时. 已知工况 ~7200s (run_pipeline_function
        # CLI help 自承), 留 3x 安全余量覆盖冷缓存 / 全样本 / 单 yunwu 账户雪崩
        # 后的重试累积耗时 (2026-06-26 起重试为固定 10s 间隔, 非指数退避; 单请求最坏
        # 80×10s=800s). 若全样本冷缓存仍不够, 调高此值即可 (一行修改).
        # 旧值 (StageSpec.timeout=3600 默认) 与已知工况冲突, 会被父端
        # proc.kill() 强杀, 留下 partial parquet.
        timeout=21600,
    ),
    StageSpec(
        name="阶段22: 词典法情感分析",
        script="22_tone_words.py",
        group="main", kind="sentiment",
        # F19 (2026-07-26 生产实测校准): 生产实测 **3744s** (④三轨打分 1880s + ⑤派生
        # 含 boilerplate 1768s), 旧默认 7200s 仅剩 1.92× 余量。⚠ 该值已是**进程并行后**的
        # 耗时 (整改前外推 ≈8h), 若日后回退串行后端会立刻超时。
        timeout=21600,  # 生产实测 3744s (已并行化)
    ),
    # 2026-06-12 用户决策: BERT 文章级情感"全部启用, 不再条件启用" — stage 23
    # 改为无条件 always-on (省略 enabled_when, 取 StageSpec 默认 always_enabled,
    # 同 stage 30a), 不再受 sentiment_analysis.enabled_methods 是否含 'tone_berts'
    # 控制。berts_method_enabled 谓词已从 METHOD_TO_PREDICATE 一并移除。
    StageSpec(
        name="阶段23: BERT模型情感分析",
        script="23_tone_berts.py",
        group="main", kind="sentiment",
        # 🔴 F19 (2026-07-26): **本阶段曾因缺显式 timeout 继承默认 7200s 而在生产首播中被
        # 强杀** —— 实测跑到 140,000/169,811 (82.4%, 19.48 篇/秒) 时触顶, 完成需 ≈8,717s。
        # 与 2026-07-24 stage 15 被强杀**同型同根** (那次只修了 15, 没回头审整张超时表)。
        # 口径: 3 模型 × 3 轨 × 滑窗(stride 0.5, max_length 512), deterministic_mode=
        # cpu_strict 故 GPU 路径**关 AMP** (刻意, 换位级可复现) → 吞吐约 19-20 篇/秒。
        # 🔴 F19b 二次订正 (2026-07-27): 上面那个 8,717s 是**按被杀瞬间的吞吐外推**出来的,
        # 提闸后真跑完实测 **21,400s** —— 外推低估了 2.45×。原因: 吞吐并非常数, 长文/滑窗
        # 分块数随篇长右偏, 被杀前那 82.4% 恰好偏短。⟹ 43200s 对真实需求只有 2.02× 余量,
        # 低于本仓 MIN_MARGIN=3.0 策略。改 72000s (20h) = 实测 21,400s 的 3.36×。
        # ⚠ 通用教训: **「被杀时按已完成比例外推」系统性低估** (stage 23 低估 2.45×,
        # stage 40 同法外推亦须存疑) —— 凡外推值都要在真跑完后回填实测并复核余量。
        timeout=72000,  # 生产实测 21,400s (2026-07-26 ② 全链跑完); 旧 43200 系按 8,717s 低估值所定
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
        # F19/F20 (2026-07-26 二次修正): 首次生产尝试实测 —— 串行下前 50 家银行 (占逐年度
        # 前缀成本模型的 29.75%) 耗时 103 分钟仍未走完 ⟹ 全程外推 **≈5.8 小时**, 撞穿当时
        # 设的 3h 上限。F20 已把逐银行循环改进程并行 (各行独立, 字节等价), 预期降到 ~45 分钟。
        # 留 6h: 覆盖「并行后仍慢于预期」与「小工况回落串行」两种情形。
        # ⚠ 本阶段**无任何缓存/检查点** (纯 CPU, 无 API) → 被超时杀 = 归零重来, 故宁宽勿紧。
        timeout=21600,
    ),

    # ── 模块四c：text2vec 稳健性指标 — 已退役 (2026-05-29 双模型重构) ──
    # legacy (main vs _t2v) by design: 此处"双轨"指 main embedding × text2vec 稳健 twin
    # 这条嵌入模型轴 (strat_diff_t2v / policy_cosine_sim_t2v), 与 full/ctx/ss 文本轨
    # 是两个独立编号空间, 勿混淆; 阶段已退役, 不参与 v3.9.0 三轨化。
    # 原 stage 30 (30_robustness_text2vec) 单独用 text2vec 计算 strat_diff_t2v /
    # policy_cosine_sim_t2v 4 列稳健 twin。改为"主阶段内联双模型计算"后, 这些 _t2v
    # 列由 stage 16 (policy_alignment) + stage 25 (strategic_diff) 在主流程内直接产出
    # (fix(D5, 2026-07-14): 原写"stage 15"是重编号残留, policy_alignment 现为阶段16)
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
        # 🔴 F19b (2026-07-27): **21600s 又一次强杀了本阶段** —— 2026-07-27 07:37:30 跑满
        # 6h 被 kill, 而当时才做到「相邻期连贯性」的第 3 个算子 (全阶段约 6 成)。F19 当初写
        # 「生产规模未实测…提至 6h」本身就是外推, 外推错了。现按**首次完整生产归因**回校:
        #   步骤1-5 载入/编码/聚合 31s · 6b-3 去重敏感性 1,426s · 6c 媒体异质性 281s ·
        #   7~7g/12/13 424s · 7h-net 网络溢出 1,421s · 战略差异度主循环 12,530s (3.48h) ·
        #   相邻期连贯性 ≥5,449s (被杀, 三轨×4 算子外推 ≈5h) ⟹ **真实需求 ≈10-11h**。
        # 并行化 (F24/F25) 后预计降到 ≈2.5h, 但超时闸的职责是**只拦真跑飞**, 不是卡工期。
        # ⚠ 教训: 没有完整实测基线的阶段, 超时闸宁可给到"荒谬地宽"—— 猜一个偏紧的值会在
        # 6 小时后把全部工作烧掉, 严格劣于让它多跑。绝不为了让 gate 变绿而调小分母。
        #
        # 🔵 S8 (2026-07-28) **首次完整实测落地**: 2026-07-27 11:35:46 → 07-28 15:36:04,
        # 父端自计 **100,800s (28.00h)**, EXIT=0。回头看上面那串外推 (≈11h) **低估了 2.55×** ——
        # 这已是同一根因第三次复现 (stage 15 / stage 23 / stage 40): **被杀时按已完成比例
        # 外推会系统性低估**, 因为剩下的往往正是最重的那部分。
        # 按 MIN_MARGIN=3.0 → 100,800 × 3 = **302,400s (84h)**。84h 看着荒谬, 但账要这么算:
        #   · 本阶段**无任何检查点**, 被杀 = 28 小时归零;
        #   · 迄今记录是 3 次误杀 / 0 次跑飞。
        # 分母偏大只烧机时, 分母偏小烧掉的是整整一天的工作 —— 不对称, 故取宽。
        # ⚠ S5 (policy_similarity 逐年并行, 占本阶段 37.8%) 与 S6 落地后本行应凭**新的完整
        #   实测**下调, 而不是凭"预计快多少"下调。
        timeout=302400,  # 生产实测 100,800s (2026-07-28 ② 首次完整跑通) × MIN_MARGIN 3.0
    ),

    # ── v3.2.0 M6 (plan v14 §9.1): Stata 数据导出层 ──
    # parquet → .dta + variable/value labels + codebook .xlsx
    # 依赖 stage 45 (panel parquet) 完成
    StageSpec(
        name="阶段46: Stata 数据导出 (pyreadstat .dta + labels)",
        script="46_stata_export.py",
        group="main", kind="export",
        # 🔴 F19: 旧值 600s 的注释依据是「小面板 (~168 行)」—— 那是 **T=2 dev 面板**。
        # 生产面板由 86 banks × 2 years = 172 行 涨到 bank_list 全量 × 2007-2025,
        # 且最宽 dta 已 3,400+ 列 → pyreadstat 写盘时间不可按 T=2 外推。提至 1h。
        timeout=3600,  # 跨平台 pyreadstat 写 .dta + labels + codebook
    ),

    # ── 模块六：伪造检验 ──
    StageSpec(
        name="阶段51: 伪造检验对照变量构建",
        script="51_falsification_test.py",
        group="main", kind="falsification",
        # F19: 生产规模未实测; T=2 时在默认 7200s 内完成。输入随面板放大 → 提至 3h 留余量。
        timeout=10800,
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
        # 远不够 (生产 stage 00 单遍去重 ~400k 文章即预算 6h)。
        # 🔴 2026-07-30 二次上调 43,200 → 64,800s (18h): 生产 T=19 两趟实测**相差 1.93×**
        #   —— 07-29 上午趟 9,190s (2.55h), 同日下午趟 **17,730s (4.93h)**, 同一代码同一
        #   语料, 差异来自 OS page cache 状态与机器争用 (下午趟前面隔了 28h 的 stage 40)。
        #   按后者算旧闸只剩 2.44× 余量, 已跌破本仓 3.0× 下限 —— 再来一趟冷缓存就是第 5 次
        #   "超时强杀"。新值 = 3.66× × 观测最大值。
        #   ⚠ 教训: **单次实测不能当基线**, 超时表必须存"观测最大值"; 07-29 上午我按首测值
        #   9,190s 回填, 当天下午即被自己的下一趟跑证伪。
        timeout=64800,
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
        # 🔴 2026-07-30 补配显式超时 (此前漏配, 在吃 StageSpec 默认 7200s) —— 由同批新增的
        #   test_no_validation_stage_silently_inherits_default_timeout **当场抓出**,
        #   是继 65 号之后同一形态的第二例。
        #   生产 T=19 两趟实测 259s → 1,056s, **跨趟方差 4.08× 为全表最大**; 按观测最大值
        #   的 10.2× 设闸以吸收该方差 (LLM 三角验证受网关限流/缓存命中率影响大)。
        timeout=10800,
    ),
    StageSpec(
        name="阶段65: 窗口半径敏感性检验",
        script="65_radius_sensitivity.py",
        group="validation", kind="sensitivity",
        # 🔴 2026-07-30 补配显式超时 (此前**漏配, 在吃 StageSpec 默认 7200s**):
        #   生产 T=19 实测 3,170s ⟹ 默认值只剩 2.27× 余量, 已跌破 3.0× 下限。
        #   这正是 stage 15 (2026-07-24) 与 stage 23 (2026-07-26) 两次被父端强杀的**同一
        #   形态**——「重阶段漏配显式超时, 靠默认值兜底」。此前的 gate
        #   test_no_main_stage_silently_inherits_default_timeout 只覆盖 STAGES_MAIN,
        #   验证侧一格没有, 于是本例从那个缺口漏出去 (gate 已同批扩到验证侧)。
        #   14,400s = 4.54× × 实测, 兼顾 radius 梯子未来加档。
        timeout=14400,
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
        # 🔴 S11 (2026-07-29): **本阶段被 10800s 强杀**, 后续 73/74/75 连坐跳过,
        # 整个评估验证管道判 ✗。这是同一根因第 4 次复发 (stage 15 / 23 / 40 / 72):
        # **超时按估算定, 从未按生产规模复核**。
        # 旧注释「N≈40 万标签…单线程约 70 分钟, 64 核 MP 上 n_jobs=16 约 5 分钟
        # (依据 plan §2.2.2 性能估算 + F31 推荐默认值)」两句都不成立:
        #   ① 那是**估算**不是实测 —— 真数据实测 (N=169,811, 比假设的 40 万还小):
        #      bootstrap 单次 754ms → 48 cell × 1000 次 = 10.05h;
        #      permutation 单次 774ms → 48 cell × 1000 次 = 10.32h; **合计 20.4h**,
        #      是「70 分钟」的约 17 倍。
        #   ② 「n_jobs=16 约 5 分钟」指的是一条**代码里根本不存在**的并行路径 ——
        #      模块自身 docstring 也承认「当前实现为 single-thread 串行」。
        # S11 已把它兑现 (上三角镜像 + 逐 cell 进程并行), 单跑实测 8,270s = 2.30h。
        # S12 (2026-07-31) 又动了两处, 净效果是**更快**, 故本闸门不需要放宽:
        #   · 撤销上三角镜像 (前提被真数据证伪) ⟹ bootstrap 格数 24→48, ×2 变慢;
        #   · NMI 标签整数编码 ⟹ 单次调用 902.3ms→49.9ms (真数据实测)。
        #   两者相抵后端到端实测 685.2s→74.5s = **9.2× 更快**, 且**串行兜底路径**
        #   同样受益 (20.4h → 约 1.5h)。
        # ⚠ 但闸门取值**不按期望值定, 按最坏路径定**: `_run_cells` 的 OOM 兜底会
        #   整批回落串行 = 回到 20.4h。取 108000s (30h) = 实测串行需求的 1.47×,
        #   使兜底路径也能跑完。本阶段无检查点, 被杀 = 全部归零 + 下游连坐,
        #   而分母偏大只烧机时 —— 不对称, 故取宽 (同 stage 40 的 S8 裁定)。
        timeout=108000,  # 按 S11 时期的串行兜底需求 20.4h 定; S12 后兜底约 1.5h, 闸门刻意不下调
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
