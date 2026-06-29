"""news_process.pipeline.text.ctx_materializer — stage 13 content_ctx 物化.

Plan E P4 A1 (v3.6.0):
    把原 stage 21 (tone_llms._materialize_content_ctx) 中的 content_ctx
    物化逻辑前置到一个独立 stage 13, 让 stage 14 (fintech_intensity)
    和 stage 15 (policy_alignment) 能在 stage 21 之前消费 content_ctx,
    实现真正的三轨化 (full/ctx/ss; B1 + B2 闭合; ss 见下方 "三轨" 段)。

工作流:
    stage 12 (news_fintech)  → 12_fintech_news.parquet
    stage 12b (cooccurrence) → 13_cooccurrence_filtered.parquet (邻近共现硬过滤后子集; 2026-06-15)
    stage 13 (本模块)        → 14_news_with_ctx.parquet  (= 12b + content_ctx 列)
    stage 14 (fintech_intensity) → 读 13, 三轨产 fintech_intensity_score_{full,ctx,ss}
    stage 15 (policy_alignment)  → 读 14, 三轨产 policy_cosine_sim_{full,ctx,ss}
    stage 21 (tone_llms)         → 已物化的 content_ctx 直接复用 (跳过重复物化)

学术依据:
    Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019).
    Firm-level political risk: Measurement and effects. The Quarterly
    Journal of Economics, 134(4), 2135-2202.
    https://doi.org/10.1093/qje/qjz021
    → §III.B "proximity-based attribution" — 实体特异性上下文窗口

向后兼容:
    若 stage 13 未跑, stage 21 仍会自己物化 content_ctx (tone_llms.py
    的 _materialize_content_ctx 不删, 改为 idempotent: 检测列存在则跳过).
    这保证 v3.5.0 既有 pipeline 行为不变。

三轨 (ss 银行+金科同句, 2026-06-14):
    本阶段额外物化第三条文本轨 content_ss = "标题 + 同一句内同时出现 目标银行
    与 金科词 的那几句话" (extract_bank_fintech_cooccurrence; 锚点=银行∧金科
    同句共现, 排除非金科的银行句), 无共现则按回退公理镜像 ctx 退回全文 body
    并置 ss_is_fallback=True。full / ctx / ss 三轨平价并列, 下游情感/特征阶段
    统一以 ['_full','_ctx','_ss'] 循环消费。

白话:
    这一步给每篇文章额外造三列文本: content_full = "标题 + 整篇正文",
    content_ctx = "标题 + 只跟目标银行相关的那几句话", content_ss = "标题 +
    银行和金融科技出现在同一句的那几句话" (都按位置截窗口, 截不到就退回全文)。
    后面的情感/强度阶段直接读这三列; 原始 '内容' 列原样保留, 不被改动。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 14_materialize_ctx.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: `13_cooccurrence_filtered.parquet` (config 键 output_12b_cooccurrence; 自 2026-06-15 起 = stage 12b 银行×金科邻近共现硬过滤后的邻近相关子集, 上游来自 stage 12 金科子集) 的 '内容'/'标题'/'target_bank' 等列。模块导入时全局加载: 银行否定/短名排除配置 (`load_exclusion_patterns` → NEGATION_AC/SHORT_NAME_EXCLUSIONS/CONTEXT_WINDOW) 与金科 AC 自动机 (`load_fintech_dict` → FINTECH_AC; 加载失败 try/except 兜底为 None → content_ss 全回退)。

**处理步骤** (`main` → `materialize_content_ctx`, idempotent):
1. 幂等短路: 若五列俱全直接返回; 旧 schema (仅有 content_ctx) 走兼容回填路径——补 content_full/ctx_is_fallback, 并以**哨兵**填 content_ss=content_full、ss_is_fallback=True (保幂等, 不重算 ss; 删 content_ctx 可触发全量重算)。
2. 全量路径逐行: 取 body_full='内容', title (缺失显式 pd.isna→空, 不注入字面 'nan'), target_bank。
3. **ctx 轨** = `extract_entity_context(body, 别名, sentence_radius=配置 context_window.sentence_radius 默认1, fallback_char_radius=150, +否定/短名排除)`: 分句→定位银行别名命中句 (经否定/短名排除, has_unexcluded_occurrence)→前后各 radius 句扩窗→O(N log N) 区间合并→' [...] ' 拼接; 无命中回退全文 body (回退公理)。
4. **ss 轨** = `extract_bank_fintech_cooccurrence(body, 别名, FINTECH_AC, sentence_radius=配置 ss_sentence_radius 默认同ctx, fallback_char_radius=150, +否定/短名排除)`: 命中句 = (该句银行别名经排除后仍在) ∧ (含 ≥1 金科词); **不对称口径**——银行侧套否定/短名排除, 金科侧裸 AC (1506 词); 无共现回退全文 body (镜像 ctx); FINTECH_AC=None 时直接全回退。
5. 三轨文本均经 `prepend_title` 注入标题 (body 已以标题开头则不重复; 标题非句末标点则插中文句号)。

**关键公式/算法** (core/text/entity_context.py): 分句 `_split_sentences` 硬边界正则 `[。！？!?；;]` (逗号/顿号不切); 窗口 `_merge_intervals` O(N log N) 区间合并; 短文本(<3 句)退化为字符级窗口 (`_char_level_fallback`, radius=150, ss 路径额外传 fintech_ac 要求同窗共现)。

**输出列** (5 列): `content_full`, `content_ctx`, `content_ss` (三轨文本); `ctx_is_fallback` = (ctx_body == 全文 body) bool; `ss_is_fallback` = (ss_body == 全文 body) bool。两旗标判定都比较'去标题后的 body' (标题前缀对三轨相同, 不影响 entity-miss 语义), 并有 assert 校验列计数与 batch 统计一致。原始 '内容' 列原样保留 (供 doc_length/去重/上下半切分/强度分母/staleness 复用)。

**三轨体现**: 这是 full/ctx/ss 三条文本轨的唯一物化点; v3.6.0 前置 ctx 物化让 stage 14/15 在 stage 21 前即可三轨化, stage 21 直接消费已物化的 content_ctx/ss (tone_llms._materialize_content_ctx 仍存, 保留为幂等向后兼容)。

**外部依赖/确定性**: 纯 CPU (pandas + ahocorasick + 正则分句), **不调 LLM/Embedding/BERT**, 无网络, 逐位可复现。ss 词典加载失败优雅降级 (FINTECH_AC=None → ss 全回退, 不崩管道)。

**DAG 位置**: 上游 stage 12b (邻近共现硬过滤; 其上游为 stage 12 金科子集), 下游 stage 14 (fintech_intensity 三轨)/15 (policy_alignment 三轨)/21 (tone_llms 三轨) 全部消费三列文本。实测 (disk 1170 篇): ss 零共现回退 ~14.27%, 主题漂移 65.76% (银行句仅 34% 同时提金科 → ss 与 ctx 是独立信号)。

■ 白话说明

**这一步在做什么**: 给每篇新闻额外造三段文本, 供后面不同口径地'读'同一篇文章。第一段 content_full = 标题+整篇正文 (全文视角); 第二段 content_ctx = 标题+只跟这家银行有关的那几句话 (聚焦视角); 第三段 content_ss = 标题+'银行和金融科技出现在同一句'的那几句话 (银行×金科共现视角)。打个比方: 同一篇报道, 一份是整页复印, 一份是只把提到'工行'的段落剪下来, 第三份是只把'工行同时谈到移动支付'的句子剪下来——截不到就退回整篇。原始正文一字不动地保留着。

**为什么需要它**: 同一篇文章, '从全文看的态度'和'只看跟这家银行直接相关那几句的态度'可能不同; 而'银行专门在谈金融科技时的态度'又是另一回事 (很多银行新闻其实在讲罚款、坏账, 跟金科无关)。三条轨道让后面的情感/强度分析能从三个角度各算一遍, 互相印证 (这叫'互为稳健性'——结论不依赖某一种截取方式才靠得住)。

**做得好不好的影响**: 这三段文本是后面情感打分、金科强度、政策契合度等核心变量的**直接输入**。如果上下文窗口截得太碎或截错句子, 后面算出来的'银行对金科的态度'就会失真; 实测显示同句共现轨 (ss) 和聚焦轨 (ctx) 有六成多的差异, 说明它确实带来一条独立的新信息, 能支撑论文的稳健性检验。回退旗标 (ctx_is_fallback/ss_is_fallback) 还会告诉后面'这篇有没有截到相关内容', 是判断信号质量的依据, 间接影响银行-年度面板里这些变量的可信度。
========================================================================
"""
from __future__ import annotations

import os
import platform
import sys
import time

import pandas as pd

# 路径注入: 让 ``news_process.core.*`` 在任意 cwd 下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import pct4, setup_logging, sig4  # noqa: E402
from news_process.core.text.ahocorasick import (  # noqa: E402
    load_exclusion_patterns,
    load_fintech_dict,
)
from news_process.core.text.entity_context import (  # noqa: E402
    extract_bank_fintech_cooccurrence,
    extract_entity_context,
    get_target_aliases,
)

CONFIG = load_config()
STAGE_NAME = "14_materialize_ctx"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# fix(omni-g-entity-03/16, 2026-06-11): ctx 锚定与 stage 11 分类共用同一套
# 否定模式 / 短名歧义排除配置 (单一匹配语义事实源) — 加载路径解析逻辑与
# news_bank.py 完全一致。此前 ctx 提取用裸 `alias in sent` 子串匹配, 被分类层
# 排除的假命中 ('涉农行业'⊂'农行' 等) 在 ctx 物化层重新生效, 把无关句子拖进
# content_ctx。
_EXCLUSION_FILE = CONFIG['paths'].get(
    'bank_name_exclusions_file',
    os.path.join(os.path.dirname(CONFIG['paths'].get('bank_names_file', '')),
                 'bank_name_exclusions.json'),
)
NEGATION_AC, SHORT_NAME_EXCLUSIONS, CONTEXT_WINDOW = load_exclusion_patterns(
    _EXCLUSION_FILE
)

# 三轨 (ss 银行+金科同句共现轨, 2026-06-14): 金科 AC 自动机, 供
# extract_bank_fintech_cooccurrence 锚定"银行∧金科同句"。路径回退解析镜像
# bank_names_file 模式。加载失败 → FINTECH_AC=None: 主物化路径据此把全部
# content_ss 退回全文 body 并置 ss_is_fallback=True (优雅降级, 不崩管道)。
_FINTECH_DICT_FILE = CONFIG['paths'].get(
    'fintech_dict_file',
    os.path.join(os.path.dirname(CONFIG['paths'].get('bank_names_file', '')),
                 'fintech_dict.json'),
)
try:
    _FINTECH_KEYWORDS, FINTECH_AC = load_fintech_dict(_FINTECH_DICT_FILE)
    logger.info(f"  ss 轨金科词典已加载: {len(_FINTECH_KEYWORDS)} 词 "
                f"(from {_FINTECH_DICT_FILE})")
except Exception as e:  # noqa: BLE001 — 任何加载失败均优雅降级, 不阻断管道
    logger.warning(f"  ss 轨金科词典加载失败 ({e}); content_ss 全部回退全文 body, "
                   f"ss_is_fallback=True")
    _FINTECH_KEYWORDS, FINTECH_AC = [], None


def materialize_content_ctx(df: pd.DataFrame) -> pd.DataFrame:
    """物化 content_ctx 列 (idempotent).

    若 'content_ctx' 已在 df.columns, 直接返回 — 避免重复计算。
    否则按 config 中 context_window 节读取 sentence_radius 和
    fallback_char_radius, 对每个 (文章, target_bank) 对调用
    extract_entity_context()。

    Args:
        df: 含 '内容' 和 'target_bank' 列。

    Returns:
        df: 新增 'content_ctx' 列 (若已存在则不变)。

    Note:
        fix(omni-g-misc-04, 2026-06-11): 主物化路径的缺失标题 (np.nan/pd.NA/None)
        统一按空标题处理 (不再注入字面 'nan' 前缀 / 不再 TypeError), 与旧 schema
        分支的 fillna('') 口径一致。
        fix(omni-g-entity-03/16, 2026-06-11): ctx 锚定套用 stage 11 同款否定/
        短名排除 — 全部 alias 出现均被排除的文章 ctx 退回全文 body (回退公理)。
    """
    # remove-title-track: 三轨文本 (full/ctx/ss) 均需"包含标题"。content_full
    # (= 标题 + 内容) / content_ctx (= 标题 + 实体窗口) / content_ss (= 标题 +
    # 银行∧金科同句窗口) 都经 prepend_title 注入标题。原始 '内容' 列保持不变 (仍供
    # doc_length / 去重 / 上下半切分 / fintech 强度分母 / staleness 等非情感
    # 复用)。下游 full 轨情感消费者改读 content_full。
    from news_process.core.text.entity_context import prepend_title

    if ('content_full' in df.columns and 'content_ctx' in df.columns
            and 'ctx_is_fallback' in df.columns
            and 'content_ss' in df.columns and 'ss_is_fallback' in df.columns):
        logger.info("  content_full/content_ctx/content_ss + ctx_is_fallback/"
                    "ss_is_fallback 五列已存在, 跳过物化 (idempotent)")
        return df

    # 旧 schema 兼容 (remove-title-track): content_ctx 已被上游物化, 但缺
    # content_full / ctx_is_fallback。**不重算 content_ctx** (尊重既有物化值),
    # 仅补算缺列: content_full = 标题 + 内容; ctx_is_fallback = (content_ctx ≡ 内容)。
    # content_ctx 此处保持原值不再注入标题 (上游已定; 与 prepend_title 的 startswith
    # 去重不冲突)。
    # 三轨 (ss, 2026-06-14): 旧数据缺 content_ss/ss_is_fallback → 按 plan §8.3
    # 回填策略以**哨兵**填充 (content_ss=全文 = content_full, ss_is_fallback=True)
    # 并告警, **不在回填路径重算 ss** (保幂等: 旧 schema 重跑行为不变, 不引入新
    # 提取漂移)。如需真 ss 列, 删 content_ctx 触发下方全量重算路径。
    if 'content_ctx' in df.columns and not (
            'content_full' in df.columns and 'ctx_is_fallback' in df.columns
            and 'content_ss' in df.columns and 'ss_is_fallback' in df.columns):
        df = df.copy()
        # fix(three-track-verify 2026-06-18): 与主物化路径 body_full / _bodies 同口径 pd.isna→''
        # (NaN 正文不被 astype(str) 变 'nan'), 保 legacy 幂等分支 ctx_is_fallback/content_full 一致。
        _bodies_old = ['' if pd.isna(v) else str(v) for v in df['内容'].tolist()]
        # 与 _bodies_old 同口径 pd.isna→'' (content_ctx 由本模块恒写为字符串、当前无 NaN producer,
        # 此处纯对称防御: 保 ctx_is_fallback 的 _ctx_old==_bodies_old 比较两侧口径一致)。
        _ctx_old = ['' if pd.isna(v) else str(v) for v in df['content_ctx'].tolist()]
        if 'ctx_is_fallback' not in df.columns:
            df['ctx_is_fallback'] = pd.Series(
                [c == b for c, b in zip(_ctx_old, _bodies_old)],
                index=df.index,
            ).astype('bool')
        if 'content_full' in df.columns:
            pass
        elif '标题' in df.columns:
            _titles_old = df['标题'].fillna('').astype(str).tolist()
            df['content_full'] = [prepend_title(t, b)
                                  for t, b in zip(_titles_old, _bodies_old)]
        else:
            df['content_full'] = _bodies_old
        _ss_backfilled = False
        if 'content_ss' not in df.columns:
            # content_ss 哨兵 = content_full (= 标题+全文, 即 ss_body 回退全文 body
            # 经 prepend_title 后的结果), 与回退公理一致。
            df['content_ss'] = df['content_full'].astype(str).tolist()
            _ss_backfilled = True
        if 'ss_is_fallback' not in df.columns:
            df['ss_is_fallback'] = pd.Series(
                [True] * len(df), index=df.index).astype('bool')
            _ss_backfilled = True
        logger.info(f"  旧 schema: content_ctx 已存在, 补算 content_full + "
                    f"ctx_is_fallback ({int(df['ctx_is_fallback'].sum())}/{len(df)} True)")
        if _ss_backfilled:
            logger.warning("  旧 schema 缺 content_ss/ss_is_fallback: 按回退策略哨兵填充 "
                           "(content_ss=全文, ss_is_fallback=True, 不重算); 如需真 ss 列"
                           "请删 content_ctx 触发全量重算")
        return df

    _ctx_cfg = CONFIG.get('context_window', {})
    _sentence_radius = _ctx_cfg.get('sentence_radius', 1)
    _fallback_char_radius = _ctx_cfg.get('fallback_char_radius', 150)
    # 三轨 ss: 命中句扩窗半径, 默认同 ctx 的 sentence_radius。
    _ss_sentence_radius = _ctx_cfg.get('ss_sentence_radius', _sentence_radius)

    logger.info(f"物化 content_full + content_ctx + content_ss 列 (含标题注入) — "
                f"sentence_radius={_sentence_radius}, "
                f"ss_sentence_radius={_ss_sentence_radius}, "
                f"fallback_char_radius={_fallback_char_radius}, "
                f"fintech_ac={'已加载' if FINTECH_AC is not None else 'None(ss全回退)'}")
    _bnf = CONFIG['paths'].get('bank_names_file', '')
    _alias_cache: dict = {}

    full_list = []       # full 轨: 标题 + 内容
    ctx_list = []        # ctx 轨: 标题 + 实体窗口 (或 fallback)
    ctx_body_list = []   # ctx 的纯 body 部分 (无标题前缀), 仅用于 fallback 判定
    ss_list = []         # ss 轨: 标题 + 银行∧金科同句窗口 (或 fallback)
    ss_body_list = []    # ss 的纯 body 部分 (无标题前缀), 仅用于 fallback 判定
    # 回退归因 (2026-06-28): 把"回退至全文"拆成两类本质不同的来源, 让日志自解释
    # (此前日志只报合并计数, 易被误读为"X% 文章没找到银行")。逐行记录"抽取是否真
    # 返回空"作 tri-state 标记: True = 抽取真返回空 (全文无目标银行 / 正文为空 / 被否定·
    # 短名排除全部弹掉) → 真·实体未命中 (真信号缺失); False = 抽取已命中非空 (若该行仍判
    # 回退, 则属【巧合性全覆盖】= 抽取文与全文逐字相等: ≥3 句文走命中句 ±radius 句窗口
    # 合并盖满全篇, 或 <3 句短文走字符级 ±fallback_char_radius 回退盖满全文 → 短文 / 命中
    # 密集的几何假象, 非信号缺失); None = 无有效 target_bank (三轨退化为全文=全文);
    # 'nodict' = 金科词典缺失 (仅 ss 轨)。供下方日志据此细分回退原因。纯统计, 不改产物/列/控制流。
    ctx_raw_empty_list = []
    ss_raw_empty_list = []
    # perf(accel-stage13-01): iterrows → 列式 tolist/zip, 去 per-row Series 物化开销。
    # 逐位等价: 仅访问 str 列 (内容/标题/target_bank) 且统一 str() 包裹, 不受 iterrows
    # 跨列 dtype 上溯影响; pd.isna 标题守卫原样保留 (omni-g-misc-04)。主成本仍是下方
    # extract_* 抽取 (后续可 loky 并行, 见加速计划 §②)。
    _contents = df['内容'].tolist() if '内容' in df.columns else [''] * len(df)
    _titles = df['标题'].tolist() if '标题' in df.columns else [''] * len(df)
    _banks = df['target_bank'].tolist() if 'target_bank' in df.columns else [''] * len(df)
    for body_raw, _t, bank_raw in zip(_contents, _titles, _banks):
        # fix(omni-g-misc-04, 2026-06-11; 扩展 three-track-verify 2026-06-18 覆盖正文):
        # 缺失正文/标题均显式 pd.isna 判空, 与 L98 旧 schema 路径 fillna('') 口径对齐 —
        # 原 `str(body_raw)`: np.nan (truthy float) 漏网被 str() 成字面 'nan' 前缀静默注入
        # 三轨 (full/ctx/ss) 情感/embedding 文本; pd.NA 在 `or` 布尔语境直接 TypeError。
        # 上游 stage 00 KEY_COLUMNS 过滤守卫是 config 驱动 (默认可为空), 不可依赖。
        body_full = '' if pd.isna(body_raw) else str(body_raw)
        title = '' if pd.isna(_t) else str(_t)
        target_bank = str(bank_raw)
        if target_bank and target_bank not in ('nan', 'None'):
            if target_bank not in _alias_cache:
                _alias_cache[target_bank] = get_target_aliases(target_bank, _bnf)
            _aliases = _alias_cache[target_bank]
            # fix(omni-g-entity-03/16, 2026-06-11): 传入 stage 11 同款排除配置,
            # 锚定与分类两层共用同一匹配语义。
            ctx_body = extract_entity_context(
                body_full, _aliases,
                sentence_radius=_sentence_radius,
                fallback_char_radius=_fallback_char_radius,
                negation_ac=NEGATION_AC,
                short_name_exclusions=SHORT_NAME_EXCLUSIONS,
                context_window=CONTEXT_WINDOW,
            )
            # 回退归因: 先记"抽取是否真返回空" (= 实体未命中信号); 再据下方
            # ctx_body 是否 ≡ 全文区分 miss(真空) / fullcov(命中但盖满全篇)。
            ctx_raw_empty_list.append(not ctx_body)
            if not ctx_body:
                ctx_body = body_full  # 回退公理: 无匹配时保留全文 body
            # 三轨 ss: 银行∧金科同句窗口。FINTECH_AC=None (词典加载失败) 时直接
            # 回退全文 body → ss_is_fallback 全 True (与模块级降级契约一致)。
            if FINTECH_AC is not None:
                ss_body = extract_bank_fintech_cooccurrence(
                    body_full, _aliases, FINTECH_AC,
                    sentence_radius=_ss_sentence_radius,
                    fallback_char_radius=_fallback_char_radius,
                    negation_ac=NEGATION_AC,
                    short_name_exclusions=SHORT_NAME_EXCLUSIONS,
                    context_window=CONTEXT_WINDOW,
                )
                ss_raw_empty_list.append(not ss_body)
                if not ss_body:
                    ss_body = body_full  # 回退公理 (镜像 ctx): 无共现→全文 body
            else:
                ss_body = body_full
                ss_raw_empty_list.append('nodict')  # 词典缺失→全回退 (非真未命中)
        else:
            ctx_body = body_full
            ss_body = body_full
            ctx_raw_empty_list.append(None)  # 无有效 target_bank
            ss_raw_empty_list.append(None)
        ctx_body_list.append(ctx_body)
        ss_body_list.append(ss_body)
        full_list.append(prepend_title(title, body_full))
        ctx_list.append(prepend_title(title, ctx_body))
        ss_list.append(prepend_title(title, ss_body))

    df = df.copy()
    df['content_full'] = full_list
    df['content_ctx'] = ctx_list
    df['content_ss'] = ss_list
    # v3.7.2 R8-H1 全管道延伸: ctx_is_fallback 暴露 entity-miss 信号。
    # remove-title-track: 因三轨 (full/ctx/ss) 都前置了同一标题, 判定改为比较"去标题
    # 后的 body" (ctx_body / ss_body vs 全文 body), 标题前缀对三轨同样, 不影响
    # entity-miss 语义。
    # 锚定: lexical_discriminant_validity.py:20 (R8-H1 audit anchor)
    # 三轨 ss (2026-06-14): ss_is_fallback = (ss_body == 全文 body), 镜像
    # ctx_is_fallback 语义 (无银行∧金科同句共现 → 回退全文 → True)。
    # fix(three-track-verify, 2026-06-18): 与 body_full 同口径 pd.isna→'' (而非 astype(str)
    # 把 NaN 变 'nan'), 保 is_fallback 比较两侧一致 (NaN 正文行: body_full='' vs _bodies='')。
    _bodies = ['' if pd.isna(v) else str(v) for v in df['内容'].tolist()]
    ctx_fb_flags = [cb == fb for cb, fb in zip(ctx_body_list, _bodies)]
    ss_fb_flags = [sb == fb for sb, fb in zip(ss_body_list, _bodies)]
    df['ctx_is_fallback'] = pd.Series(ctx_fb_flags, index=df.index).astype('bool')
    df['ss_is_fallback'] = pd.Series(ss_fb_flags, index=df.index).astype('bool')
    n_fallback = sum(ctx_fb_flags)
    n_ss_fallback = sum(ss_fb_flags)

    # 健壮性 (评审 defense-in-depth): zip 对长度不一会【静默截断】→ 下方按类求和的
    # assert 反而抓不到 list 失同步。先硬断言两 raw_empty 列与 *_fb_flags 等长 (==len df),
    # 让未来若误加 continue/break 漏一次 append 立即暴露, 而非静默错算回退归因。
    assert len(ctx_raw_empty_list) == len(ctx_fb_flags) == len(df), \
        (f"ctx_raw_empty_list 长度 ({len(ctx_raw_empty_list)}) 与 "
         f"ctx_fb_flags/df ({len(ctx_fb_flags)}/{len(df)}) 失同步")
    assert len(ss_raw_empty_list) == len(ss_fb_flags) == len(df), \
        (f"ss_raw_empty_list 长度 ({len(ss_raw_empty_list)}) 与 "
         f"ss_fb_flags/df ({len(ss_fb_flags)}/{len(df)}) 失同步")

    # ── 回退归因细分 (2026-06-28): 把"回退至全文"拆成本质不同的来源 ──
    # *_is_fallback 标志 = (抽取文 ≡ 全文 内容), 它把两类合并计数, 易被误读:
    #   · miss    (真·实体未命中) = 抽取真返回空被全文兜底 (含空正文) → **真信号缺失** (须警惕);
    #   · fullcov (巧合性全覆盖)  = 抽取已命中, 但抽取文与全文逐字相等 (≥3 句文走句窗
    #                               盖满 / <3 句短文走字符回退盖满) → **非**信号缺失;
    #   · nobank  = 该行无有效 target_bank (三轨退化为全文); nodict = 金科词典缺失 (仅 ss)。
    # 三/四类之和恒 == n_fallback (无有效 bank 行 ctx/ss 同时回退)。纯统计, 不改产物。
    # 据 ctx_raw_empty_list (tri-state) × ctx_fb_flags 归类: 仅对判回退的行细分。
    n_ctx_miss = n_ctx_cov = n_ctx_nobank = 0
    for _fb, _re in zip(ctx_fb_flags, ctx_raw_empty_list):
        if not _fb:
            continue
        if _re is None:
            n_ctx_nobank += 1
        elif _re:
            n_ctx_miss += 1
        else:
            n_ctx_cov += 1
    n_ss_miss = n_ss_cov = n_ss_nobank = n_ss_nodict = 0
    for _fb, _re in zip(ss_fb_flags, ss_raw_empty_list):
        if not _fb:
            continue
        if _re is None:
            n_ss_nobank += 1
        elif _re == 'nodict':
            n_ss_nodict += 1
        elif _re:
            n_ss_miss += 1
        else:
            n_ss_cov += 1
    assert int(df['ctx_is_fallback'].sum()) == n_fallback, \
        f"ctx_is_fallback 列计数 ({int(df['ctx_is_fallback'].sum())}) " \
        f"与 batch 统计 ({n_fallback}) 不一致"
    assert int(df['ss_is_fallback'].sum()) == n_ss_fallback, \
        f"ss_is_fallback 列计数 ({int(df['ss_is_fallback'].sum())}) " \
        f"与 batch 统计 ({n_ss_fallback}) 不一致"
    # 回退归因细分须穷尽划分 n_fallback (miss ⊎ fullcov ⊎ nobank / +nodict), 否则
    # 漏归类会让日志原因数对不上总数 → 硬断言守护 (与上方两条列计数 assert 同级)。
    assert n_ctx_miss + n_ctx_cov + n_ctx_nobank == n_fallback, \
        f"ctx 回退归因之和 ({n_ctx_miss}+{n_ctx_cov}+{n_ctx_nobank}) ≠ n_fallback ({n_fallback})"
    assert n_ss_miss + n_ss_cov + n_ss_nobank + n_ss_nodict == n_ss_fallback, \
        f"ss 回退归因之和 ({n_ss_miss}+{n_ss_cov}+{n_ss_nobank}+{n_ss_nodict}) ≠ n_ss_fallback ({n_ss_fallback})"
    _bank_strs = df['target_bank'].astype(str).str.strip()
    n_with_bank = ((_bank_strs != '') & (_bank_strs != 'nan') &
                   (_bank_strs != 'None')).sum()
    logger.info(f"  content_ctx 物化完成: {len(df)} 行, "
                f"回退至全文: {n_fallback}/{n_with_bank} 条 "
                f"({pct4(n_fallback / max(n_with_bank, 1))})")
    # 回退归因 (让"回退至全文"一行不被误读为"X 条没找到银行"): 拆真未命中 vs 巧合全覆盖。
    logger.info(f"    └─ 回退归因: 真·实体未命中 {n_ctx_miss} 条 (全文无目标银行 / 正文为空 / "
                f"被否定·短名排除全部弹掉 → 真信号缺失) | 巧合性全覆盖 {n_ctx_cov} 条 (银行已命中, "
                f"但抽取文与全文逐字相等: ≥3 句文走命中句 ±{_sentence_radius} 句窗口盖满 / <3 句短文"
                f"走字符级回退盖满 → 短文或命中密集的几何假象, 非信号缺失) | 无有效 target_bank "
                f"{n_ctx_nobank} 条")
    logger.info(f"       (占带 bank 行 {n_with_bank} 之比, 4 位有效数字: 真·未命中 "
                f"{pct4(n_ctx_miss / max(n_with_bank, 1))} | 巧合全覆盖 "
                f"{pct4(n_ctx_cov / max(n_with_bank, 1))} | 无有效 bank "
                f"{pct4(n_ctx_nobank / max(n_with_bank, 1))} — 判读以'真·未命中率'为准, "
                f"巧合全覆盖系几何假象非信号缺失)")
    logger.info(f"  ctx_is_fallback 列已写入 (bool): "
                f"{int(df['ctx_is_fallback'].sum())}/{len(df)} True")
    logger.info(f"  content_ss 物化完成 (银行+金科同句): {len(df)} 行, "
                f"回退至全文: {n_ss_fallback}/{n_with_bank} 条 "
                f"({pct4(n_ss_fallback / max(n_with_bank, 1))})")
    logger.info(f"    └─ 回退归因: 真·无同句共现 {n_ss_miss} 条 (银行与金科从不在同一句 / 正文为空 → "
                f"真信号缺失) | 巧合性全覆盖 {n_ss_cov} 条 (已命中, 但抽取文与全文逐字相等: ±"
                f"{_ss_sentence_radius} 句窗口或字符回退盖满全文 → 短文几何假象) | 无有效 target_bank "
                f"{n_ss_nobank} 条 | 金科词典缺失 {n_ss_nodict} 条")
    logger.info(f"       (占带 bank 行 {n_with_bank} 之比, 4 位有效数字: 真·无共现 "
                f"{pct4(n_ss_miss / max(n_with_bank, 1))} | 巧合全覆盖 "
                f"{pct4(n_ss_cov / max(n_with_bank, 1))} | 无有效 bank "
                f"{pct4(n_ss_nobank / max(n_with_bank, 1))} | 词典缺失 "
                f"{pct4(n_ss_nodict / max(n_with_bank, 1))})")
    logger.info(f"  ss_is_fallback 列已写入 (bool): "
                f"{int(df['ss_is_fallback'].sum())}/{len(df)} True")

    # ── 结果分析 (写入 <stage>.log, 让日志自带"这批数据物化得好不好"的解读) ──
    # crash-guard (硬化 A): 整块"读数据算指标 + 打印"包进 try/except。本块在最终
    # 写盘 (save_dataset, main() L429) 之前执行 → 若任何统计计算抛异常 (空列表
    # 除零已 max(...,1) 守住, 但仍防御未预期的 KeyError/TypeError/数值异常), 必须
    # 降级为 WARNING 跳过, 绝不连带崩掉整个 stage 13 丢失产物 (否则证伪 golden-safe)。
    # 本块纯读 in-memory 列表/已算好的标量 (full_list/ctx_list/ss_list/n_fallback…),
    # 不回写 df、不改返回值、不改写盘内容 → 纯日志, golden-safe。
    try:
        # 三轨平均字符数 + 压缩比: 体现 ctx/ss 窗口相对全文截掉了多少 (越小 = 越聚焦)。
        # 注: full_list/ctx_list/ss_list 元素均为 prepend_title 产出的 str (非 NaN),
        # len() 恒有效; 各比率分母均 max(...,1) 守零 → 无 NaN/除零方向误判风险 (硬化 B
        # 在本块不适用: 此处统计的是字符串列表长度, 非含 NaN 的数值 Series)。
        _mean_full = sum(len(x) for x in full_list) / max(len(full_list), 1)
        _mean_ctx = sum(len(x) for x in ctx_list) / max(len(ctx_list), 1)
        _mean_ss = sum(len(x) for x in ss_list) / max(len(ss_list), 1)
        # ctx↔ss 分歧率: 两轨截到的 body 不同的占比 (高 = ss 是独立信号, 非 ctx 的冗余
        # 复制; 无 bank 行两轨同为全文 body, 恒相等不计入, 故分母取 n_with_bank)。
        n_div = sum(1 for sb, cb in zip(ss_body_list, ctx_body_list) if sb != cb)
        _ctx_hit = n_with_bank - n_fallback    # ctx 真正截到银行相关句的条数
        _ss_hit = n_with_bank - n_ss_fallback  # ss 真正截到"银行∧金科同句"的条数
        _ctx_fb_rate = n_fallback / max(n_with_bank, 1)
        _ss_fb_rate = n_ss_fallback / max(n_with_bank, 1)
        _div_rate = n_div / max(n_with_bank, 1)
        logger.info("-" * 72)
        logger.info("【结果分析】三轨文本物化质量解读:")
        logger.info(f"  样本: {len(df):,} 行, 其中 {n_with_bank:,} 行带有效 target_bank "
                    f"(ctx/ss 窗口仅对这些行生效, 其余直接用全文)")
        if n_with_bank == 0:
            # 全样本无有效 target_bank: 三轨退化为'全文=全文=全文', 回退/分歧率分母为 0
            # (已 max(...,1) 兜底为 100%/0%), 此时方向判读无意义, 走专门分支不落数值档。
            logger.info("  本批无任何带有效 target_bank 的行: ctx/ss 三轨全部退化为全文 body, "
                        "回退率/分歧率不适用 (核查上游 target_bank 是否全空)")
        else:
            logger.info(f"  平均文本长度: full={sig4(_mean_full)} 字 | "
                        f"ctx={sig4(_mean_ctx)} 字 ({pct4(_mean_ctx / max(_mean_full, 1))} of full) | "
                        f"ss={sig4(_mean_ss)} 字 ({pct4(_mean_ss / max(_mean_full, 1))} of full)")
            logger.info(f"  ctx 轨: {_ctx_hit:,}/{n_with_bank:,} 条截到银行相关句 (窗口窄于全文), "
                        f"{n_fallback:,} 条 ctx≡全文 (回退率 {pct4(_ctx_fb_rate)}); 拆解 = 真·未命中 "
                        f"{n_ctx_miss:,} + 巧合全覆盖 {n_ctx_cov:,} + 无 bank {n_ctx_nobank:,}")
            # 判读须按"真·未命中率"而非合并回退率: 巧合全覆盖是短文窗口盖满全篇的几何假象,
            # 银行其实已命中, 不代表 ctx 信号弱。把判读门槛从 _ctx_fb_rate 改为 _ctx_miss_rate。
            _ctx_miss_rate = n_ctx_miss / max(n_with_bank, 1)
            logger.info("    → " + ("真·未命中率低, 绝大多数文章都能定位到目标银行 "
                                    "(回退多由短文/命中密集致窗口盖满全篇所致, 属几何假象, ctx 信号有效)"
                                    if _ctx_miss_rate < 0.30 else
                                    "真·实体未命中率偏高, 较多文章全文无目标银行/被否定·短名"
                                    "排除弹掉 (核查别名表/分句口径/语料是否离题)"))
            # P2 fix: ss 轨命中判读 + ctx↔ss 分歧判读必须置于 FINTECH_AC is not None 守卫下。
            # 词典缺失时 ss 全回退全文 (回退率=100%、分歧率≡ctx 回退率), 此时打"ss 回退率天然
            # 高于 ctx 属预期 / 分歧明显支撑三轨稳健性"会与紧随其后的 loud warning (词典未加载、
            # ss 不可用) 相邻矛盾, 且诱导读者据全回退假象误判三轨稳健性。故守卫内才走方向判读;
            # 守卫外只打原始计数并明示分歧全部来自 ss 退化为全文 body, 非 ss 独立信号。
            if FINTECH_AC is not None:
                logger.info(f"  ss 轨: {_ss_hit:,}/{n_with_bank:,} 条截到'银行∧金科同句', "
                            f"{n_ss_fallback:,} 条 ss≡全文 (回退率 {pct4(_ss_fb_rate)}); 拆解 = 真·无同句"
                            f"共现 {n_ss_miss:,} + 巧合全覆盖 {n_ss_cov:,} + 无 bank {n_ss_nobank:,}")
                # 注 (2026-06-29 修正): stage 12b 邻近共现硬过滤生产默认 radius=1 (±1 句窗口邻近)。
                # keep 集 ⊆ ss 同句共现集【仅当 12b radius=0 严格同句【且 match_in_title=False】时严格
                # 成立】(ss 命中判据恒严格同句, 与 ss_sentence_radius 无关——后者只控输出扩窗; 又因 ss
                # 提取只读正文 body, title=true 时"标题同句、正文跨句"行会被 12b 留下却落 ss 回退 → 已破
                # 子集, 即下文三态②); radius=1 时 keep 集 ⊋ ss 同句集 →
                # 存活行新增"仅邻句非同句"行 (正文无银行∧金科同句) → 这些行 ss 真·无共现回退 → ss
                # 真·未命中【不坍缩】, frac_ss_fallback∈(0,1) (在 match_in_title=true 部分恢复基础上
                # 进一步恢复)。又因 ss 命中句 ⊆ ctx 命中句 (ss 须银行∧金科同句, ctx 只须银行) → 同
                # radius 下 ss 全覆盖必致 ctx 全覆盖 → ss 合并回退计数 ≤ ctx (本批 56 ≤ 162; 机制可证)。
                logger.info("    → ss 回退按镜像 ctx 的公理退回全文 body; stage 12b 邻近共现过滤 "
                            "(生产 radius=1) 后存活含非同句邻句行 → ss 真·无共现回退恢复 ∈(0,1), 另有"
                            "短文/字符回退全覆盖几何假象 (非 ss 信号缺失)")
                logger.info(f"  ctx↔ss 分歧率: {n_div:,}/{n_with_bank:,} ({pct4(_div_rate)}) 两轨截到不同句子")
                logger.info("    → " + ("分歧明显, ss 带来独立于 ctx 的新信息, 支撑三轨稳健性设计"
                                        if _div_rate > 0.40 else
                                        "分歧较小, ss 与 ctx 高度重叠, 作为独立信号的增量有限 (论文须如实披露)"))
                # ── 回退原因详解 (短文几何假象的句数实证): 让日志自带"为何会出现回退至全文"的
                # 答案。巧合全覆盖行普遍是短文 (命中句 ±radius 句窗口必然盖满全篇), 用正文句数
                # 均值/短文占比印证。仅读 in-memory 列表, 纯日志, golden-safe。
                try:
                    from news_process.core.text.entity_context import (
                        _split_sentences,
                    )
                    _cov_sc = [len(_split_sentences(_bodies[i]))
                               for i, (_fb, _re) in enumerate(
                                   zip(ctx_fb_flags, ctx_raw_empty_list))
                               if _fb and _re is False]
                    logger.info("  ── 回退原因详解 (核心: 回退≠没找到银行) ──")
                    logger.info("    · *_is_fallback 标志 = (抽取文 ≡ 全文 内容), 混合两类来源: "
                                "真·未命中 (信号缺失) + 巧合全覆盖 (句窗或字符回退盖满全文, 非缺失)")
                    if _cov_sc:
                        _mean_sc = sum(_cov_sc) / len(_cov_sc)
                        # 按机制分三档: <3 句走【字符级回退】(±fallback_char_radius 字, 与 sentence_radius
                        # 无关); 3-6 句多为单/少命中句即可盖满的短文 (句窗); >6 句须命中密集才能 merged
                        # ==[0,n-1]。≤6 仅是经验性短文界, 非句窗盖满的机制临界 (临界 = 命中句密度)。
                        _n = len(_cov_sc)
                        _lt3 = sum(1 for s in _cov_sc if s < 3)
                        _s36 = sum(1 for s in _cov_sc if 3 <= s <= 6)
                        _gt6 = sum(1 for s in _cov_sc if s > 6)
                        logger.info(f"    · ctx 巧合全覆盖 {_n:,} 条正文句数: 均值 {sig4(_mean_sc)} 句; "
                                    f"按机制分档 <3 句(字符回退) {_lt3:,} ({pct4(_lt3 / _n)}) | "
                                    f"3-6 句(短文句窗) {_s36:,} ({pct4(_s36 / _n)}) | "
                                    f">6 句(命中密集) {_gt6:,} ({pct4(_gt6 / _n)})")
                        logger.info("    · 解读: <3 / 3-6 档是'短文几何假象'; >6 档是'银行高频出现→命中"
                                    "句密集→合并窗口盖满全篇', 二者均非信号缺失 (银行已命中)")
                    logger.info(f"    · 据此: 本批真正的信号缺失 = 真·未命中 (ctx {n_ctx_miss:,} / "
                                f"ss {n_ss_miss:,} 条); 其余回退为几何假象, 银行/共现均已命中")
                    logger.info("    · ss 全覆盖 ≤ ctx 全覆盖 (机制可证, 非经验外推): ss 命中句 ⊆ ctx "
                                "命中句 (ss 须银行∧金科同句, ctx 只须银行), 同 radius 下 ss 覆盖全文必致 "
                                f"ctx 也覆盖 → ss fullcov {n_ss_cov:,} ≤ ctx fullcov {n_ctx_cov:,}")
                except Exception as _e2:  # noqa: BLE001 — 句数证据仅辅助, 失败不阻断主日志
                    logger.debug(f"    · (回退句数证据计算失败, 跳过此块: {_e2})")
            else:
                # FINTECH_AC is None: ss 全回退全文 → _ss_hit=0、回退率=100%、分歧率纯由 ss
                # 退化为全文 body 与 ctx 不同所致, 与"ss 独立信号"无关。只打原始计数 + 明确禁判读。
                logger.info(f"  ss 轨: 0/{n_with_bank:,} 条截到'银行∧金科同句', "
                            f"全部 {n_ss_fallback:,} 条回退全文 (回退率 {pct4(1.0)}, 因金科词典未加载)")
                logger.info(f"  ctx↔ss 分歧={pct4(_div_rate)} ({n_div:,}/{n_with_bank:,}) 全部来自 ss "
                            "退化为全文 body (词典缺失), 非 ss 独立信号, 请勿据此判读三轨稳健性")
        if FINTECH_AC is None:
            logger.warning("  ⚠ 金科词典未加载 (FINTECH_AC=None): content_ss 已全部回退全文, "
                           "ss 轨此次不可用 (优雅降级, 不阻断管道; 修复词典路径后重跑可恢复)")
        if n_with_bank < 5000:
            logger.info(f"  ⚠ 带 target_bank 的行数偏少 ({n_with_bank:,}), 多为盘面小样本 (如 T=2), "
                        "上述回退/分歧率仅供管道正确性验证, 全量结论以 17M/T=18 实测为准")
        logger.info("-" * 72)
    except Exception as _e:  # noqa: BLE001 — 仅日志诊断, 绝不阻断写盘
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")
    return df


def main():
    """Stage 13 入口: 读 13_cooccurrence_filtered.parquet → 写 14_news_with_ctx.parquet.

    输入自 2026-06-15 起改为 stage 12b (银行×金科邻近共现硬过滤) 的输出, 而非
    stage 12 直出 —— 下游三轨情感/强度链由此天然继承 12b 过滤 (路线 A; 见
    cooccurrence_filter.py)。回滚 = 把 in_name 改回 output_12_fintech_news + 全量重跑。
    """
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39c/39d/39e)。
    logger.info("=" * 72)
    logger.info("阶段 14: 三轨文本物化 (content_full / content_ctx / content_ss; v3.6.0 + v3.9.0)")
    logger.info("=" * 72)
    logger.info("【功能】给每篇新闻造三段可供下游'分别阅读'同一篇文章的文本, 供 stage 14/15/21")
    logger.info("        在三个口径下各算一遍情感/金科强度/政策契合度, 互相印证 (互为稳健性)。")
    logger.info("          · content_full = 标题 + 整篇正文              (全文视角)")
    logger.info("          · content_ctx  = 标题 + 只跟目标银行相关的句子 (实体聚焦视角)")
    logger.info("          · content_ss   = 标题 + 银行与金科同句出现的句子 (银行×金科共现视角)")
    logger.info("【方法】分句(硬边界 。！？；)→定位银行别名命中句(套否定/短名排除)→前后各扩 N 句→")
    logger.info("        O(N log N) 区间合并; ss 额外要求同句含 ≥1 金科词(裸 AC 词典, 不对称口径)。")
    logger.info("        截不到相关句则按'回退公理'退回全文 body 并置 *_is_fallback=True。")
    logger.info("【判读】回退率越低 = 越多文章截到了相关上下文(信号越聚焦); ctx 与 ss 分歧越大")
    logger.info("        = ss 带来越独立的新信息(支撑论文三轨稳健性, 而非 ctx 的冗余复制)。")
    logger.info("【确定性】纯 CPU(pandas + 正则分句 + ahocorasick), 不调 LLM/Embedding, 逐位可复现。")

    output_dir = CONFIG['paths']['output_dir']
    filenames = CONFIG.get('filenames', {})
    in_name = filenames.get(
        'output_12b_cooccurrence', '13_cooccurrence_filtered.parquet'
    )
    out_name = filenames.get('output_13_news_with_ctx', '14_news_with_ctx.parquet')
    in_path = os.path.join(output_dir, in_name)
    out_path = os.path.join(output_dir, out_name)

    # ── 🧭 项目 / 环境信息 + 📂 输入输出 + ⚙ 运行配置 + 📖 方法论依据 (日志富集, 2026-06-24) ──
    # 目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息、运行结果信息"):
    # 把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、依据哪篇文献"一次性落进日志,
    # 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 / schema / 控制流 (golden-safe)。
    try:
        _ctx_cfg_banner = CONFIG.get('context_window', {})
        _sr = _ctx_cfg_banner.get('sentence_radius', 1)
        _ssr = _ctx_cfg_banner.get('ss_sentence_radius', _sr)
        _fcr = _ctx_cfg_banner.get('fallback_char_radius', 150)
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')

        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (stage 14 三轨文本物化; STAGES_MAIN)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) "
                    "| 版本 v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段纯 CPU / 无 LLM·Embedding·网络·API ($0) / 逐位可复现")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入:   {in_path} (config 键 output_12b_cooccurrence)")
        logger.info(f"     · 输出:   {out_path} (config 键 output_13_news_with_ctx)")
        logger.info(f"     · 银行别名: {CONFIG['paths'].get('bank_names_file', '(默认)')}")
        logger.info(f"     · 银行排除: {_EXCLUSION_FILE}")
        logger.info(f"     · 金科词典: {_FINTECH_DICT_FILE} "
                    f"({len(_FINTECH_KEYWORDS):,d} 词, "
                    f"FINTECH_AC={'已加载' if FINTECH_AC is not None else 'None(ss 全回退)'})")

        logger.info("  ⚙ 运行配置 (config\\filtering.yaml::context_window)")
        logger.info(f"     · ctx 扩窗半径 sentence_radius={_sr:,d} 句 "
                    f"| ss 扩窗半径 ss_sentence_radius={_ssr:,d} 句")
        logger.info(f"     · 短文本字符级回退半径 fallback_char_radius={_fcr:,d} 字")
        logger.info(f"     · 银行侧匹配: 否定模式 NEGATION_AC + 短名歧义排除 "
                    f"({len(SHORT_NAME_EXCLUSIONS):,d} 条) | 金科侧: 裸 AC (不对称口径)")
        logger.info("     · 三轨: ['_full','_ctx','_ss'] 平价并列; 回退公理=无命中→退回全文 body")

        logger.info("  📖 方法论依据 (运行期 emit, 非仅注释)")
        logger.info("     · 实体特异性上下文窗口 (proximity-based attribution, §III.B):")
        logger.info("       Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. "
                    "(2019). Firm-level political risk: Measurement and effects. "
                    "The Quarterly Journal of Economics, 134(4), 2135-2202. "
                    "https://doi.org/10.1093/qje/qjz021")
        logger.info("       (白话: 只把'离目标实体最近的那几句'剪出来, 比整篇正文更精准地"
                    "捕捉对该实体的态度, 是 ctx/ss 两轨的方法学锚点)")
        logger.info("     · 关键词/二元组命中识别新兴技术关注 (ss 轨金科词锚定):")
        logger.info("       Kalyani, A., Bloom, N., Carvalho, M., Hassan, T. A., "
                    "Lerner, J., & Tahoun, A. (2025). The diffusion of new "
                    "technologies. The Quarterly Journal of Economics, 140(2), "
                    "1299-1365. https://doi.org/10.1093/qje/qjaf002")
        logger.info("       (白话: 用文本中的技术词/二元组命中来追踪新技术扩散; 与本阶段"
                    "ss 轨'同句含 ≥1 金科词 (FINTECH_AC 命中)'锚定金科关注同一范式)")
        logger.info("     · 关键词词表构建 firm-level 文本暴露 (金科词典构造标准模板):")
        logger.info("       Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. "
                    "(2023). Firm-level climate change exposure. The Journal of "
                    "Finance, 78(3), 1449-1498. https://doi.org/10.1111/jofi.13219")
        logger.info("       (白话: 用机器学习发现关键词 + 二元组命中构造企业层面文本暴露度, "
                    "是 FINTECH_AC 金科词典构造 + 同句命中计数的标准方法学模板)")
        logger.info("     · 三轨 = 同一银行-报道的多重'处理'测度 (multiple treatments 计量动因):")
        logger.info("       de Chaisemartin, C., & D'Haultfœuille, X. (2023). "
                    "Two-way fixed effects and differences-in-differences estimators "
                    "with several treatments. Journal of Econometrics, 236(2), 105480. "
                    "https://doi.org/10.1016/j.jeconom.2023.105480")
        logger.info("       (白话: 把 full/ctx/ss 视作同一银行-报道的三种并列'处理'定义; "
                    "据'多重处理须各自识别、不可混入同一过度识别式'之诫, 三轨各自 just-identified "
                    "并排互证, 严禁混进同一 over-identified Hansen J — 此即本阶段产三轨而非单轨的计量动因)")
    except Exception as _e:  # noqa: BLE001 — 仅日志诊断, 绝不阻断处理
        logger.warning(f"[环境/配置/方法论] 日志 banner 打印失败 (不影响处理): {_e}")

    if not os.path.exists(in_path):
        logger.error(f"输入未找到: {in_path}")
        raise SystemExit(1)

    _t_load = time.time()
    df = pd.read_parquet(in_path)
    _load_elapsed = time.time() - _t_load
    logger.info(f"加载 stage 12b 输出 (邻近共现过滤后): {len(df)} 行 "
                f"(⏱ 读盘 {sig4(_load_elapsed)} 秒)")

    _t_mat = time.time()
    df = materialize_content_ctx(df)
    _mat_elapsed = time.time() - _t_mat
    logger.info(f"  ⏱ 三轨物化耗时: {sig4(_mat_elapsed)} 秒 "
                f"({sig4(len(df) / max(_mat_elapsed, 1e-9))} 行/秒)")
    assert 'content_full' in df.columns
    assert 'content_ctx' in df.columns
    assert 'content_ss' in df.columns
    assert 'ss_is_fallback' in df.columns

    from news_process.core.reporting import save_dataset
    _t_save = time.time()
    save_dataset(df=df, output_path=out_path, logger=logger,
                 stage_name=STAGE_NAME, config=CONFIG, input_files=[in_path])
    _save_elapsed = time.time() - _t_save
    logger.info(f"  ⏱ 写盘耗时: {sig4(_save_elapsed)} 秒")

    # ⏱ 阶段计时汇总 (各子阶段墙钟): 读盘 / 物化 / 写盘 + 全阶段总耗时。
    try:
        _total = time.time() - stage_start
        logger.info("  ⏱ 阶段计时汇总 (墙钟秒, 4 位有效数字):")
        logger.info(f"     · 读盘   = {sig4(_load_elapsed)} 秒 "
                    f"({pct4(_load_elapsed / max(_total, 1e-9))})")
        logger.info(f"     · 三轨物化 = {sig4(_mat_elapsed)} 秒 "
                    f"({pct4(_mat_elapsed / max(_total, 1e-9))})")
        logger.info(f"     · 写盘   = {sig4(_save_elapsed)} 秒 "
                    f"({pct4(_save_elapsed / max(_total, 1e-9))})")
        logger.info(f"     · 全阶段 = {sig4(_total)} 秒")
    except Exception as _e:  # noqa: BLE001 — 仅日志诊断, 绝不阻断收尾
        logger.warning(f"[阶段计时汇总] 打印失败 (不影响产物): {_e}")

    from news_process.core.logging import log_stage_summary
    log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
