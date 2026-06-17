"""
news_process.pipeline.sentiment.tone_berts — 阶段23：基于 BERT 系列预训练模型的情感分析
========================================================================================

迁移说明 (Phase 7a-6)：
    本模块由原 root script ``23_tone_berts.py`` body 迁入。
    规范调用方式: ``python -m news_process.pipeline.sentiment.tone_berts``


功能：
    使用多个中文金融/通用预训练语言模型，对每篇新闻进行情感分类。

模型列表（由 config/sentiment.yaml 中 sentiment_analysis.tone_berts.models 配置;
config.yaml 已是 legacy stub, 配置拆分后单一真值在 7 域 split YAML）：
    1. yiyanghkust/finbert-tone-chinese — FinBERT 中文金融情感
    2. bardsai/finance-sentiment-zh-base — 中文金融短语级情感
    3. FinBERT2-base — 本地微调金融分类模型

核心算法：
    滑动窗口文本切片 + 置信度加权池化聚合

    对超过模型 max_length 的长文本，采用滑动窗口切片，
    通过置信度加权池化聚合各窗口的 logits，实现特征无损融合。

    数学原理：
    ─────────
    给定输入文本 T，模型最大 token 长度 L（含特殊 token），
    滑动步长 S = ⌊L × stride_ratio⌋。

    Step 1: Tokenize & Slice
      tokens = tokenizer(T)
      若 len(tokens) ≤ L，单窗口推理；
      否则生成 K 个窗口 W_k = tokens[k·S : k·S + L]

    Step 2: Per-Window Inference
      logits_k = model(W_k).logits ∈ ℝ^C
      confidence_k = softmax(logits_k).max()

    Step 3: Weighted Pooling
      logits* = Σ(confidence_k · logits_k) / Σ(confidence_k)
      probs* = softmax(logits*)
      label* = argmax(probs*)

    白话: BERT 一口最多只能"吃"约 512 个 token, 长文章吃不下。做法是把
    长文切成若干段, 相邻段有一半重叠 (防止关键句正好被切断), 每段各打
    一次分; 最后汇总时, 模型越有把握 (置信度越高) 的段, 话语权越大,
    加权平均出整篇文章的情感判定。

性能优化（v5 — GPU 全面加速架构）：
    - **AMP 动态混合精度**：torch.amp.autocast 自动选择最优数值精度，
      兼顾推理速度与数值稳定性（替代早期 model.half() 永久转换方案）
    - **增大 batch size**：128，AMP 下 RTX 3090 显存充裕
    - **动态填充 + 长度排序**：窗口按长度排序分桶，每个 mini-batch 仅填充到
      实际最长序列，减少无效计算
    - **cuDNN benchmark**：自动调优卷积算法
    - **全部模型预加载到 GPU**：消除串行加载/卸载开销
    - **分词结果共享**：(max_length, 词表指纹) 完全一致的模型才共享同一次批量分词
      和窗口 (fix g-berts-01: 历史按 max_length 分组会把不同词表模型的 token id
      跨词表错配, 词表不同的模型现各自独立分词)
    - **pin_memory + non_blocking**：异步 CPU→GPU 数据传输

输入：
    阶段22（词典法情感分析）输出的 Parquet 文件（output_22_words_tone）

输出：
    追加各模型的情感标签和概率列（output_23_bert_tone）

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 23_tone_berts.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: 读 stage 22 输出 `22_words_tone.parquet` (config 键 output_22_words_tone; 取 `标题`/`内容`/`content_ctx`/`content_ss` 列)。

**处理步骤**: ①`_build_model_configs()` 从 config/sentiment.yaml::sentiment_analysis.tone_berts.models 读 3 个 BERT 模型配置; ②`MultiModelSentimentEngine.load_all()` 一次性加载到 GPU (FP32 权重 + AMP autocast 动态混合精度推理); ③Step 1 用 `prepend_title` 拼三轨文本列表 (full=标题+内容, ctx=标题+content_ctx, ss=标题+content_ss); ④`process_all_models` 对 ctx/full/(ss) 各跑批量推理 (物理隔离防 OOM); ⑤超长文本滑动窗口切片 (`WINDOW_STRIDE_RATIO=0.5` 50% 重叠, 单窗 ≤max_length 512 含特殊 token, 有效正文 ≤510 token) + 置信度加权池化聚合各窗 logits (logits*=Σ(conf_k·logits_k)/Σconf_k); ⑥三轨结果带后缀写回 DataFrame; ⑦写 `bert_num_windows_{track}` (≥1 正常 / 0 空文本 / -1 推理失败哨兵); ⑧保存 parquet, 释放显存, 打三轨分类报告。

**关键算法**: 各模型按自身 tokenizer 分窗 (fix g-berts-01 后词表不同模型不共享分词); argmax 分类 + 置信度加权窗口池化 (高置信窗口更大权重)。批级异常 → 逐篇重试一次 → 仍失败才写失败哨兵 (label=None/概率 NaN/num_windows=-1, 与空文本 num_windows=0 严格区分)。

**输出列**: 每模型 (finbert_cn/fin_sent_zh/finbert2) × 三轨的 `{sn}_label` + 各标签概率列 (含 2-class 模型补 `{sn}_中性`=NaN)、`{sn}_infer_failed_{track}` 哨兵、`bert_num_windows_{full/ctx/ss}`。

**外部依赖与降级**: 3 模型 = (1) yiyanghkust/finbert-tone-chinese (finbert_cn, HF, 3-class 中性/正面/负面), (2) bardsai/finance-sentiment-zh-base (fin_sent_zh, HF, 基于 Financial PhraseBank 微调, 3-class), (3) FinBERT2 (finbert2, 本地私有, 2-class 负面/正面, 经 .env `FINBERT2_MODEL_DIR` 解析; 留空或路径不存在则**优雅跳过该模型**, 另两个 HF 模型照跑)。`strict_models=true` 默认下两个 HF 模型非预期加载失败会 fail-loud raise; FINBERT2_MODEL_DIR 未配是预期 graceful skip。**须 HF_HUB_OFFLINE=1 / TRANSFORMERS_OFFLINE=1** 本地重跑 (两 HF 模型连不上 hf.co 但有本地缓存; 见 memory)。依赖 torch/transformers + GPU; 无 LLM API、无 _llm_cache.db (确定性来自模型权重 + AMP argmax 对分类结果无影响)。

**DAG 位置**: 上游 stage 22 (`22_words_tone.parquet`); 下游 stage 24 (herd_decay 硬依赖 23_bert_tone.parquet)。STAGES_MAIN 阶段23, always-on。

■ 白话说明

这一步是'AI 神经网络版'的情绪打分: 用三个已经在大量金融文本上训练过的小型语言模型 (BERT 系列, 可以理解为'专门读金融新闻的情绪识别器') 给每篇新闻判正面/负面/中性。它和前两步 (大模型、查字典) 是三条独立路线, 各有所长——BERT 不靠关键词硬数, 而是整体理解一段话的语气。新闻太长超出模型一次能读的长度时, 它像翻书一样用滑动窗口分段读, 每段都有 50% 重叠不漏信息, 最后按'读得有多确定'加权合并。为什么需要它: 同样是给媒体语调找旁证, 三种方法 (大模型 + 词典 + BERT) 互相印证, 结论越稳越能上顶刊。其中一个叫 FinBERT2 的模型是项目自己训练的私货, 别人机器上没有也没关系, 程序会自动跳过它、用另外两个公开模型继续跑, 不会卡死。一个实操坑: 本地重跑要先把'离线模式'开关打开, 否则它会去外网下模型结果连不上而失败。这一步同样按全文/银行相关段/银行金科同句段三种范围各推理一遍 (同句段那一路如果上游没准备好就自动只跑前两路)。
========================================================================
"""

import gc
import hashlib
import os
import sys
import time
import warnings
from collections import Counter

import numpy as np
import pandas as pd

# Phase 7a-6: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 pipeline/sentiment/tone_berts.py 出发, 上溯 3 层抵达 news_process/ 的父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import log_memory_usage, log_stage_summary, setup_logging
from news_process.core.reporting import safe_save_preview_csv

warnings.filterwarnings(
    "ignore",
    message=r"Failed to find CUDA\.",
    category=UserWarning,
    module=r"triton\.windows_utils",
)

try:
    import torch
    import torch.nn.functional as F
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
except ImportError:
    raise ImportError(
        "请安装必要依赖：\n"
        "  pip install torch transformers\n"
        "如需 GPU 加速，请安装对应 CUDA 版本的 PyTorch。"
    )


# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "23_tone_berts"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 从配置中获取 BERT 情感分析参数
BERT_PARAMS = CONFIG.get('sentiment_analysis', {}).get('tone_berts', {})

# 设备选择
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"推理设备: {DEVICE}")

# ===== V4 T1.1a: 严格确定性 (CPU 优先, GPU 走 backlog T1.1b) =====
# 模式:
#   cpu_strict — 在 CPU 上启用 use_deterministic_algorithms(warn_only=True);
#                若也跑 GPU, 同时关 cuDNN benchmark + 关 AMP (保证位级一致).
#   gpu_strict — 仅 GPU 严格; 与 cpu_strict 区别在保留 GPU 路径配置 hook
#                (warn_only=False 在某些 op 上会抛错, 须 user 自行评估).
#   off        — 历史行为, 含 AMP + cuDNN benchmark (性能优先, 不保证可重现).
_DETERMINISTIC_MODE = BERT_PARAMS.get('deterministic_mode', 'cpu_strict')
_SEED = int(BERT_PARAMS.get('random_seed', 42))

# 设种子: 覆盖 random / numpy / torch / transformers 四个独立随机源
import random as _stdlib_random

_stdlib_random.seed(_SEED)
np.random.seed(_SEED)
torch.manual_seed(_SEED)
try:
    from transformers import set_seed as _hf_set_seed
    _hf_set_seed(_SEED)
except ImportError:
    # transformers 旧版没有 set_seed; torch.manual_seed 已覆盖其大部分内部 RNG
    pass
if DEVICE.type == 'cuda':
    torch.cuda.manual_seed_all(_SEED)

logger.info(f"随机种子: {_SEED}; 确定性模式: {_DETERMINISTIC_MODE}")

# 确定性算法 + cuDNN 策略
if _DETERMINISTIC_MODE in ('cpu_strict', 'gpu_strict'):
    # warn_only=True: CPU 上几乎不会抛错; GPU 上某些 op (如 scatter_add_, atomic_add)
    # 会输出 warning 但继续运行. T1.1b backlog 评估是否升级 warn_only=False.
    torch.use_deterministic_algorithms(True, warn_only=True)

if DEVICE.type == 'cuda':
    logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    gpu_total_mem = torch.cuda.get_device_properties(0).total_memory
    logger.info(f"GPU 显存: {gpu_total_mem / 1e9:.1f} GB")
    if _DETERMINISTIC_MODE in ('cpu_strict', 'gpu_strict'):
        # cuDNN deterministic + 关 benchmark: 牺牲 ~10-30% 推理速度换位级一致
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        logger.info("cuDNN: deterministic=True, benchmark=False (严格模式)")
    else:
        torch.backends.cudnn.benchmark = True
        logger.info("cuDNN: benchmark=True (性能模式, 未启用确定性)")

# 是否启用 AMP (Automatic Mixed Precision) 加速
# 严格模式下关 AMP: fp16 mixed precision 在 reduction 时存在非确定性 (Nvidia docs).
USE_AMP = (
    DEVICE.type == 'cuda'
    and hasattr(torch, 'amp')
    and _DETERMINISTIC_MODE not in ('cpu_strict', 'gpu_strict')
)
if USE_AMP:
    logger.info("Mixed Precision (AMP) 推理加速: 已启用")
elif DEVICE.type == 'cuda':
    logger.info("Mixed Precision (AMP): 已禁用 (严格模式)")

# 标签映射（从模型输出 id 到中文标签）— 项目侧极性索引*约定*文档
# fix(omni-g-berts-03, 2026-06-11): 这两个常量不再作为 num_labels 不匹配时的盲目
# 回退映射 (在产两个 hub checkpoint 的真实 id2label 顺序与此约定均为 0↔2 极性翻转,
# 盲回退 = tone 符号整体翻转)。回退路径现优先从 checkpoint id2label 经极性归一推导,
# 推导失败则 fail-loud raise。常量保留作为项目极性顺序约定的参照与测试锚点。
DEFAULT_LABEL_MAP = {0: "负面", 1: "中性", 2: "正面"}
DEFAULT_LABEL_MAP_2CLASS = {0: "负面", 1: "正面"}

# 极性同义词分组（用于 checkpoint id2label 顺序校验）。
# checkpoint 的标签文本可能是中/英文任意写法, 这里把它们归一到
# {neg, neu, pos} 三类, 只比较"哪个索引落在哪个极性"这一顺序契约,
# 不要求标签文本字面相等。
_POLARITY_SYNONYMS = {
    'neg': {'负面', '消极', '负向', 'negative', 'neg', 'bad', 'label_0'},
    'neu': {'中性', '中立', 'neutral', 'neu', 'none'},
    'pos': {'正面', '积极', '正向', 'positive', 'pos', 'good'},
}


def _polarity_of(label_text) -> str | None:
    """把任意 checkpoint 标签文本归一为 'neg'/'neu'/'pos'/None。"""
    if label_text is None:
        return None
    s = str(label_text).strip().lower()
    for pol, names in _POLARITY_SYNONYMS.items():
        if s in {n.lower() for n in names}:
            return pol
    return None


def _label_order_consistent(ckpt_id2label: dict, expected_label_map: dict) -> bool:
    """校验 checkpoint 的 id2label 极性顺序是否与项目预期一致。

    仅对那些两边都能归一到已知极性 (neg/neu/pos) 的索引做比较;
    无法识别的标签文本视为"无法判定"而跳过 (返回 True 不误报),
    因为本守卫的目的是抓"正负静默对调", 而非强制标签文本统一。

    Returns:
        True  — 顺序一致 (或无法判定, 保守不告警);
        False — 至少一个索引两边都可识别但极性相反/错位。
    """
    for idx, expected_name in expected_label_map.items():
        exp_pol = _polarity_of(expected_name)
        ckpt_pol = _polarity_of(ckpt_id2label.get(idx))
        if exp_pol is None or ckpt_pol is None:
            continue  # 任一侧无法识别极性 → 不判定
        if exp_pol != ckpt_pol:
            return False
    return True


# 极性 → 项目中文标签 (用于从 checkpoint id2label 推导项目侧 label_map)
_POLARITY_TO_CN = {'neg': '负面', 'neu': '中性', 'pos': '正面'}


def _derive_label_map_from_checkpoint(model_config, num_labels: int) -> dict | None:
    """从 checkpoint 自带 id2label 推导项目中文 label_map。

    fix(omni-g-berts-03, 2026-06-11): num_labels 与配置不匹配时, 以 checkpoint
    自身声明的类别顺序为准 — 每个索引的标签文本经 _polarity_of 归一到
    neg/neu/pos 再映射为项目中文标签, 保证极性顺序忠实于 checkpoint。

    Returns:
        dict | None: 推导成功返回 {idx: 中文标签}; 任一索引标签无法归一极性、
            极性重复、或 id2label 缺失/条数不符 → 返回 None (调用方须 fail-loud,
            不得回退项目侧 DEFAULT 顺序出数)。
    """
    id2label = getattr(model_config, 'id2label', None)
    if not isinstance(id2label, dict) or len(id2label) != num_labels:
        return None
    derived = {}
    seen_polarities = set()
    for raw_idx, raw_label in id2label.items():
        try:
            idx = int(raw_idx)  # HF config.json 原始键可能是字符串
        except (TypeError, ValueError):
            return None
        pol = _polarity_of(raw_label)
        if pol is None or pol in seen_polarities:
            return None  # 无法归一 (如 LABEL_1) 或极性重复 → 不可推导
        seen_polarities.add(pol)
        derived[idx] = _POLARITY_TO_CN[pol]
    return derived


def _tokenizer_fingerprint(tokenizer) -> str:
    """计算 tokenizer 词表身份指纹 (vocab fingerprint)。

    fix(omni-g-berts-01, 2026-06-11): 共享分词的分组键由 max_length 升级为
    (max_length, 本指纹) — 仅词表 (含 added_tokens)、大小写策略、特殊 token id
    完全一致的模型才允许共享同一次批量分词。历史按 max_length 分组曾让
    finbert2 (词增强 vocab 34,932) 全程吃 finbert_cn (bert-base-chinese,
    vocab 21,128) 的 token id — 逐 id 跨词表错位即乱码输入。

    Returns:
        str: sha256 hex digest; 无 get_vocab 的异类 tokenizer 退化为按对象身份
            生成的唯一指纹 (保守: 永不与他人共享分词)。

    白话: 不同模型各有一本"字典"(词表), 同一个编号在两本字典里可能对应
    完全不同的字。为了省时间让多个模型共用一次分词结果, 必须先确认它们
    的字典一模一样 —— 这里把整本字典内容哈希成一个指纹, 指纹相同才共享,
    否则各分各的, 防止把 A 模型的编号喂给 B 模型变成乱码。
    """
    h = hashlib.sha256()
    try:
        vocab = tokenizer.get_vocab()  # 含 added_tokens (HF 契约)
    except Exception:
        # 无法取词表 → 不可证明等价 → 按对象身份隔离, 永不共享
        return f"no-vocab:{type(tokenizer).__name__}:{id(tokenizer)}"
    for token, idx in sorted(vocab.items()):
        h.update(f"{token}\t{idx}\n".encode())
    do_lower = getattr(tokenizer, 'do_lower_case', None)
    if do_lower is None:
        do_lower = getattr(tokenizer, 'init_kwargs', {}).get('do_lower_case')
    special_ids = (
        getattr(tokenizer, 'cls_token_id', None),
        getattr(tokenizer, 'sep_token_id', None),
        getattr(tokenizer, 'pad_token_id', None),
        getattr(tokenizer, 'unk_token_id', None),
    )
    h.update(f"|do_lower_case={do_lower}|special={special_ids}".encode())
    return h.hexdigest()


# ============================================================================
# 2. 模型配置（仅从 config/sentiment.yaml 加载, 单一真值; Plan P0-2 删除内置 fallback 列表）
# ============================================================================

def _build_model_configs() -> list:
    """从 config/sentiment.yaml 的 sentiment_analysis.tone_berts.models 构建模型配置列表。

    label_map 键在 YAML 中为字符串（如 "0"），这里转换为整数。

    Plan P0-2 (合并 #2 + #8) 修订:
        删除原 80 行内置 fallback 列表 — 它与 config/sentiment.yaml 的
        models 段形成"双源真值", 任一处增删模型都需手动同步, 极易漂移;
        且 fallback 中包含某台开发机的 Windows 绝对路径, 让任何非该机器
        的用户在 fallback 路径下立即失败.
        现在 sentiment.yaml 缺失或 models 段为空时直接 raise, 提示明确.
        finbert2 这类本地私有模型通过 ${FINBERT2_MODEL_DIR} env var 解析,
        缺该 env 时 sentiment.yaml 解析为空字符串, load_all 在 try 之外显式判定为
        "预期 graceful skip" (fix g-berts-04), 不影响其它 2 个 huggingface 模型
        (finbert_cn / fin_sent_zh); 后者的非预期加载失败默认 fail-loud raise.

    Returns:
        list: 模型配置字典列表，每项包含 model_id、short_name、description、
              max_length、label_map（int 键）。

    Raises:
        RuntimeError: 当 config 中 sentiment_analysis.tone_berts.models 段
            缺失或为空时. (历史 fallback 用过期硬编码列表掩盖此配置错误,
            导致用户在 config 损坏时仍貌似正常运行, 但用的是项目维护者上次
            release 时的过期模型清单. )
    """
    yaml_models = BERT_PARAMS.get('models', [])
    if not yaml_models:
        raise RuntimeError(
            "config/sentiment.yaml::sentiment_analysis.tone_berts.models "
            "段缺失或为空. 该段是 stage 23 BERT 情感分析的模型清单单一真值, "
            "请按既有格式补齐 (参考当前 3 模型配置 (finbert_cn / fin_sent_zh / finbert2)). "
            "Plan P0-2 已删除代码内 fallback 双源以避免静默漂移."
        )

    configs = []
    for m in yaml_models:
        raw_label_map = m.get('label_map', {})
        # YAML 中键为字符串，转为 int
        label_map = {int(k): v for k, v in raw_label_map.items()}
        configs.append({
            "model_id":    m.get('model_id', ''),
            "short_name":  m.get('short_name', ''),
            "description": m.get('description', ''),
            "max_length":  int(m.get('max_length', 512)),
            "label_map":   label_map,
        })
    return configs


MODEL_CONFIGS = _build_model_configs()

# 滑动窗口参数
WINDOW_STRIDE_RATIO = BERT_PARAMS.get('window_stride_ratio', 0.5)

# ── 推理 batch size ──
# v5: 增大到 128，AMP 下 RTX 3090 显存充裕
INFERENCE_BATCH_SIZE = BERT_PARAMS.get('inference_batch_size', 128)

# 每次调用 engine.run_all_models 的文章批次数
ARTICLES_PER_BATCH = BERT_PARAMS.get('articles_per_batch', 200)


# ============================================================================
# 3. 多模型推理引擎（v5 — AMP 动态混合精度 + 动态填充 + 长度排序）
# ============================================================================

class MultiModelSentimentEngine:
    """多模型推理引擎 — AMP 动态混合精度 + 动态填充 + 长度排序。

    v5 架构优化：
      - AMP autocast: 动态混合精度推理，自动选择最优精度
      - 窗口按长度排序分桶，mini-batch 仅填充到实际最长序列
      - 增大 batch size (128) 提升 GPU 吞吐
      - (max_length, 词表指纹) 一致的模型共享分词 + 窗口数据
        (fix g-berts-01: 词表不同的模型独立分词, 防 token id 跨词表错配)

    Attributes:
        models:          已加载的 PyTorch 模型。
        tokenizers:      每个模型对应的 tokenizer。
        model_configs:   模型配置列表。
        skipped_expected: 预期 graceful skip 的模型名 (如 FINBERT2_MODEL_DIR 未配)。
        failed_models:    非预期加载失败的模型名 (strict_models=false 时才可能非空)。
    """

    def __init__(self, model_configs: list):
        self.model_configs = model_configs
        self.models = {}         # short_name -> PyTorch model (FP32, AMP推理)
        self.tokenizers = {}     # short_name -> tokenizer
        self.loaded_configs = {} # short_name -> config (含实际 num_labels)

        # fix(omni-g-berts-04, 2026-06-11): 显式记录跳过/失败清单, 供 stage summary
        # 与 gate 校验 loaded/expected 计数
        self.skipped_expected = []  # 预期跳过 (本地私有模型未配置)
        self.failed_models = []     # 非预期加载失败

        # fix(omni-g-berts-01, 2026-06-11): 分组键 max_length → (max_length, 词表指纹)
        self._groups = {}  # (max_length, vocab_fingerprint) -> [short_name, ...]

    def load_all(self) -> list:
        """一次性加载全部模型到 GPU（FP32 权重, AMP 推理）。

        fix(omni-g-berts-04, 2026-06-11) 降级透明化: 预期 graceful skip 仅限
        "本地私有模型未配置" (model_id 为空 = FINBERT2_MODEL_DIR 未设, 或解析为
        本地绝对路径但不存在); 其余模型 (hub 模型瞬态故障等) 加载失败默认 raise
        (config 开关 sentiment_analysis.tone_berts.strict_models=false 可放宽,
        放宽时失败记入 failed_models 供 gate 校验)。
        fix(omni-g-berts-03, 2026-06-11): num_labels 不匹配时不再盲回退
        DEFAULT_LABEL_MAP 顺序, 改从 checkpoint id2label 极性归一推导, 推导失败
        raise; 极性顺序守卫由 warning-only 升级为 fail-loud。

        Returns:
            list: 成功加载的模型名称列表。
        """
        load_start = time.time()
        loaded_names = []
        strict_models = bool(BERT_PARAMS.get('strict_models', True))

        for mc in self.model_configs:
            short_name = mc['short_name']
            model_id = str(mc['model_id'] or '')

            local_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'models', short_name
            )

            # fix(omni-g-berts-04, 2026-06-11): 预期跳过判定提前到 try 之外,
            # 与"非预期加载失败"严格分流。预期跳过 = 本地私有模型未配置:
            #   (a) model_id 为空 (FINBERT2_MODEL_DIR 未设 → yaml 解析为空串);
            #   (b) model_id 是本地路径 (绝对路径或含反斜杠, hub id 不可能) 但不存在。
            # 两种情况均需本地 models/<short_name> 副本也不存在才跳过。
            _looks_local = os.path.isabs(model_id) or ('\\' in model_id)
            if not os.path.exists(local_path) and (
                not model_id.strip() or (_looks_local and not os.path.exists(model_id))
            ):
                logger.warning(
                    f"  模型 {short_name} 本地路径未配置或不存在 "
                    f"(model_id={model_id!r}, 如 FINBERT2_MODEL_DIR 未设) — "
                    f"预期 graceful skip, 其余模型继续。"
                )
                self.skipped_expected.append(short_name)
                continue

            model_path = local_path if os.path.exists(local_path) else model_id

            try:
                logger.info(f"  正在加载模型: {model_id} ...")

                # 加载 tokenizer
                tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

                # 加载模型
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_path, trust_remote_code=True
                )
                model.to(DEVICE)
                model.eval()

                # v5: 使用 AMP autocast 动态混合精度推理
                # 不再使用 model.half() 永久转换权重，避免与 autocast 语义冲突

                # 标签映射
                label_map = mc['label_map'].copy()
                num_labels = len(label_map)
                if hasattr(model.config, 'num_labels'):
                    actual = model.config.num_labels
                    if actual != num_labels:
                        # fix(omni-g-berts-03, 2026-06-11): 历史此处盲回退
                        # DEFAULT_LABEL_MAP{,_2CLASS} — 其索引顺序对在产两个 hub
                        # checkpoint 均为 0↔2 极性翻转 (tone 符号整体翻转)。
                        # 改为: 从 checkpoint 自带 id2label 极性归一推导; 推导
                        # 失败 fail-loud, 不得以项目侧约定顺序冒充 checkpoint 顺序。
                        derived = _derive_label_map_from_checkpoint(model.config, actual)
                        if derived is None:
                            raise RuntimeError(
                                f"模型 {short_name} 实际标签数={actual} 与配置 "
                                f"label_map 条目数={num_labels} 不匹配, 且无法从 "
                                f"checkpoint id2label="
                                f"{getattr(model.config, 'id2label', None)!r} "
                                f"推导极性映射 — 拒绝盲回退默认顺序 (极性翻转风险)。"
                                f"请修正 config/sentiment.yaml 该模型的 label_map。"
                            )
                        logger.warning(
                            f"  模型 {short_name} 实际标签数={actual}, 配置={num_labels}。"
                            f"以 checkpoint id2label 极性推导为准: {derived}"
                        )
                        num_labels = actual
                        label_map = derived

                # 防御性校验: checkpoint 的 id2label *顺序* 与项目预期极性顺序
                # 是否一致 (抓"正负静默对调")。
                # fix(omni-g-berts-03, 2026-06-11): 由 warning-only 升级为
                # fail-loud — 极性对调若放行, 该模型 tone 符号整体翻转且下游
                # 无任何可见信号; 不得继续以可疑映射出数。
                _ckpt_id2label = getattr(model.config, 'id2label', None)
                if isinstance(_ckpt_id2label, dict) and _ckpt_id2label:
                    if not _label_order_consistent(_ckpt_id2label, label_map):
                        raise RuntimeError(
                            f"模型 {short_name} checkpoint id2label={_ckpt_id2label} "
                            f"的极性顺序与项目 label_map={label_map} 不一致 — "
                            f"上游 checkpoint 可能重排了类别索引, 正负情感存在静默"
                            f"对调风险。请核对并修正 config/sentiment.yaml 的 "
                            f"label_map 后重跑 (本步骤拒绝以可疑映射出数)。"
                        )

                self.models[short_name] = model
                self.tokenizers[short_name] = tokenizer
                self.loaded_configs[short_name] = {
                    **mc,
                    'label_map': label_map,
                    'num_labels': num_labels,
                }
                loaded_names.append(short_name)

                # 分组 — fix(omni-g-berts-01, 2026-06-11): 组键 max_length →
                # (max_length, 词表指纹); 词表/大小写/特殊 token 任一不同的模型
                # 不再共享分词 (finbert2 用自己的 tokenizer, 含其 added_tokens)
                group_key = (mc['max_length'], _tokenizer_fingerprint(tokenizer))
                self._groups.setdefault(group_key, []).append(short_name)

                logger.info(f"  模型 {short_name} 加载成功 (labels={num_labels})")

            except Exception as e:
                # fix(omni-g-berts-04, 2026-06-11): 非预期加载失败不再静默吞掉 —
                # strict_models=true (默认) 直接 raise, 防止该模型三轨列 (full/
                # ctx/ss) 从输出 parquet 整体消失而阶段仍 SUCCESS (下游按列存在性
                # 静默跳过)。
                self.failed_models.append(short_name)
                logger.error(f"  模型 {model_id} 加载失败: {e}")
                if strict_models:
                    logger.error(
                        "    strict_models=true (默认): 非预期模型加载失败 fail-loud。"
                        "如确需容忍缺席, 在 config/sentiment.yaml 设 "
                        "sentiment_analysis.tone_berts.strict_models: false"
                    )
                    raise

        load_elapsed = time.time() - load_start
        # fix(omni-g-berts-04): stage summary 显式记录 loaded/expected/skipped/failed
        logger.info(
            f"全部模型加载完毕: {len(loaded_names)}/{len(self.model_configs)} "
            f"(预期跳过 {len(self.skipped_expected)}: {self.skipped_expected}; "
            f"意外失败 {len(self.failed_models)}: {self.failed_models}) "
            f"(耗时 {load_elapsed:.1f}s)"
        )

        if DEVICE.type == 'cuda':
            allocated = torch.cuda.memory_allocated() / 1e9
            reserved = torch.cuda.memory_reserved() / 1e9
            logger.info(f"GPU 显存: 所有模型已分配 {allocated:.2f} GB, "
                        f"已保留 {reserved:.2f} GB")

        return loaded_names

    def unload_all(self):
        """释放全部模型和 GPU 显存。"""
        self.models.clear()
        self.tokenizers.clear()
        self.loaded_configs.clear()
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    @torch.no_grad()
    def run_all_models(self, texts: list) -> dict:
        """对一批文本执行全部模型的推理。

        v5 核心优化：
          - 共享分词 + 窗口构造
          - 按窗口长度排序 → 动态填充到 mini-batch 内最长序列
          - AMP autocast 动态混合精度推理
          - 增大 batch size (128)

        Args:
            texts: 文本列表。

        Returns:
            dict: {short_name: list[dict]} 每个模型的逐文章预测结果。
        """
        n_texts = len(texts)
        all_model_results = {}

        # ── 按 (max_length, 词表指纹) 分组共享分词 ──
        # fix(omni-g-berts-01, 2026-06-11): 组键含词表指纹, 组内 tokenizer 等价,
        # representative 的分词结果对全组每个模型都是其自身词表下的合法 token id
        for (max_length, _vocab_fp), group_names in self._groups.items():
            # 取该组中第一个已加载模型的 tokenizer
            representative = None
            for gn in group_names:
                if gn in self.tokenizers:
                    representative = gn
                    break
            if representative is None:
                continue

            tokenizer = self.tokenizers[representative]
            eff_len = max_length - 2
            stride = max(1, int(eff_len * WINDOW_STRIDE_RATIO))

            cls_id = tokenizer.cls_token_id or tokenizer.bos_token_id or 101
            sep_id = tokenizer.sep_token_id or tokenizer.eos_token_id or 102
            pad_id = tokenizer.pad_token_id or 0

            # ── Step 1: 批量分词（共享，只做一次） ──
            valid_indices = []
            valid_texts = []
            for i, t in enumerate(texts):
                if isinstance(t, str) and t.strip():
                    valid_indices.append(i)
                    valid_texts.append(t)

            batch_token_ids = []
            if valid_texts:
                encoded = tokenizer(
                    valid_texts,
                    add_special_tokens=False,
                    return_attention_mask=False,
                    return_token_type_ids=False,
                    verbose=False,
                )
                batch_token_ids = encoded['input_ids']

            # ── Step 2: 滑动窗口构造 + 记录每个窗口的实际长度 ──
            windows_data = []  # [(token_ids_with_special, seq_len), ...]
            spans_by_idx = {}  # valid_idx -> (start, end) in windows_data

            for j, token_ids in enumerate(batch_token_ids):
                span_start = len(windows_data)
                total_tokens = len(token_ids)

                if total_tokens <= eff_len:
                    win_ids = [cls_id] + token_ids + [sep_id]
                    windows_data.append((win_ids, len(win_ids)))
                else:
                    start = 0
                    while start < total_tokens:
                        end = min(start + eff_len, total_tokens)
                        window_ids = token_ids[start:end]
                        win_ids = [cls_id] + window_ids + [sep_id]
                        windows_data.append((win_ids, len(win_ids)))
                        if end >= total_tokens:
                            break
                        start += stride

                spans_by_idx[valid_indices[j]] = (span_start, len(windows_data))

            # 构建完整 article_spans
            article_spans = [spans_by_idx.get(i, (0, 0)) for i in range(n_texts)]
            total_windows = len(windows_data)

            if total_windows == 0:
                for short_name in group_names:
                    all_model_results[short_name] = [self._empty_result(short_name)
                                                     for _ in range(n_texts)]
                continue

            # ── Step 3: 按长度排序（使同一个 mini-batch 内序列长度相近） ──
            sorted_indices = sorted(range(total_windows),
                                    key=lambda k: windows_data[k][1])

            # ── Step 4: 同组内每个模型依次推理（共享窗口数据） ──
            for short_name in group_names:
                if short_name not in self.models:
                    all_model_results[short_name] = [self._empty_result(short_name)
                                                     for _ in range(n_texts)]
                    continue

                model = self.models[short_name]
                cfg = self.loaded_configs[short_name]
                num_labels = cfg['num_labels']
                label_map = cfg['label_map']

                # 收集所有窗口的 logits（按原始顺序）
                all_logits = torch.zeros(total_windows, num_labels,
                                         device=DEVICE if DEVICE.type == 'cuda' else 'cpu')

                batch_counter = 0
                for bs in range(0, total_windows, INFERENCE_BATCH_SIZE):
                    be = min(bs + INFERENCE_BATCH_SIZE, total_windows)
                    batch_sorted_idx = sorted_indices[bs:be]
                    batch_size = be - bs
                    batch_counter += 1

                    # 动态填充：仅填充到该 mini-batch 内的最长序列
                    max_seq_in_batch = max(windows_data[k][1] for k in batch_sorted_idx)

                    # 构造 numpy 数组 → tensor（动态宽度）
                    input_ids_np = np.full((batch_size, max_seq_in_batch), pad_id, dtype=np.int64)
                    attn_mask_np = np.zeros((batch_size, max_seq_in_batch), dtype=np.int64)

                    for local_i, global_i in enumerate(batch_sorted_idx):
                        win_ids, seq_len = windows_data[global_i]
                        input_ids_np[local_i, :seq_len] = win_ids
                        attn_mask_np[local_i, :seq_len] = 1

                    input_ids_t = torch.from_numpy(input_ids_np)
                    attn_mask_t = torch.from_numpy(attn_mask_np)
                    if DEVICE.type == 'cuda':
                        input_ids_t = input_ids_t.pin_memory()
                        attn_mask_t = attn_mask_t.pin_memory()

                    # GPU 推理（AMP autocast 动态混合精度）
                    inputs = {
                        'input_ids': input_ids_t.to(DEVICE, non_blocking=True),
                        'attention_mask': attn_mask_t.to(DEVICE, non_blocking=True),
                    }
                    with torch.amp.autocast(DEVICE.type, enabled=USE_AMP):
                        outputs = model(**inputs)

                    # 将 logits 还原到原始索引位置（在 GPU 上收集）
                    batch_logits = outputs.logits.float()
                    for local_i, global_i in enumerate(batch_sorted_idx):
                        all_logits[global_i] = batch_logits[local_i]

                    # GPU 内存管理：每10批清理一次缓存，防止碎片累积
                    if DEVICE.type == 'cuda' and batch_counter % 10 == 0:
                        torch.cuda.empty_cache()

                # 一次性回传 CPU 做聚合
                all_logits_cpu = all_logits.cpu()

                # ── Step 5: 按文章聚合 ──
                results = []
                for i in range(n_texts):
                    s, e = article_spans[i]
                    if s == e:
                        results.append(self._empty_result(short_name))
                        continue

                    article_logits = all_logits_cpu[s:e]
                    probs_per_window = F.softmax(article_logits, dim=-1)
                    confidences = probs_per_window.max(dim=-1).values
                    weight_sum = confidences.sum()
                    weights = (confidences / weight_sum) if weight_sum > 0 else (
                        torch.ones(e - s) / (e - s))

                    final_probs = F.softmax(weights @ article_logits, dim=-1)
                    predicted_idx = final_probs.argmax().item()

                    results.append({
                        'label': label_map.get(predicted_idx, f"类别{predicted_idx}"),
                        'probabilities': {
                            ln: round(final_probs[idx].item(), 4)
                            for idx, ln in label_map.items() if idx < len(final_probs)
                        },
                        'num_windows': e - s,
                    })

                all_model_results[short_name] = results

        return all_model_results

    def _empty_result(self, short_name: str) -> dict:
        """返回空文本结果 (num_windows=0)。

        仅用于"输入文本为空/空白"这一语义; 推理失败请用 _failure_result
        (num_windows=-1), 两者在 num_windows 上严格区分 (fix g-berts-02)。
        """
        cfg = self.loaded_configs.get(short_name)
        if cfg:
            prob_dict = {label: 0.0 for label in cfg['label_map'].values()}
        else:
            prob_dict = {'正面': 0.0, '中性': 0.0, '负面': 0.0}
        return {'label': '中性', 'probabilities': prob_dict, 'num_windows': 0}

    def _failure_result(self, short_name: str) -> dict:
        """返回推理失败哨兵结果 (num_windows=-1)。

        fix(omni-g-berts-02, 2026-06-11): 与空文本 (_empty_result, num_windows=0)
        严格区分的失败哨兵:
          - num_windows = -1 — 失败标志 (空文本=0, 正常推理 ≥1);
          - label = None — 不冒充 '中性' (对 2-class 模型 '中性' 是标签空间外
            类别, 对 3-class 模型则与真实中性预测不可区分);
          - 概率 = NaN (而非 0.0) — pandas mean/sum 聚合自动跳过, 与 LLM 族
            v6/F2 "测量失败 → pd.NA 与真实中性严格区分" 契约对齐。
        """
        cfg = self.loaded_configs.get(short_name)
        if cfg:
            prob_dict = {label: float('nan') for label in cfg['label_map'].values()}
        else:
            prob_dict = {'正面': float('nan'), '中性': float('nan'), '负面': float('nan')}
        return {'label': None, 'probabilities': prob_dict, 'num_windows': -1}


# ============================================================================
# 4. 批量处理协调器
# ============================================================================

def process_all_models(df: pd.DataFrame, engine: MultiModelSentimentEngine, content_list: list) -> dict:
    """使用多模型引擎对全部数据进行批量推理。

    fix(omni-g-berts-02, 2026-06-11) 批级异常兜底重写: 历史 except 把整批
    (200 篇 × 全部模型) 静默写成 '中性'+全 0 概率哨兵 (与空文本不可区分,
    哨兵 0.0 直进下游 mean/sum 聚合)。现改为: 批级异常 → 逐篇单独重试一次
    (隔离坏文章/瞬态 GPU 故障), 仍失败的文章才写失败哨兵 (_failure_result:
    label=None / 概率 NaN / num_windows=-1), 并输出每篇 {sn}_infer_failed
    标志列; 末尾统计总失败篇数。

    Args:
        df:           仅用于确定总行数 (len(df)) 的 DataFrame; 文本不从此读取
                      (历史注释称"包含'内容'列", 与实现不符, 已修正)。
        engine:       已加载全部模型的多模型引擎。
        content_list: 预构建的文本列表 (content_full / content_ctx / content_ss
                      三轨之一, 均含 prepend 标题)。

    Returns:
        dict: {short_name: {'columns': {...}, 'stats': {...}}}
    """
    total = len(df)

    # 初始化收集器
    model_results_all = {}
    loaded_model_names = []
    for mc in engine.model_configs:
        sn = mc['short_name']
        if sn in engine.models:
            model_results_all[sn] = []
            loaded_model_names.append(sn)

    inference_start = time.time()
    n_failed_articles = 0  # fix(omni-g-berts-02): 重试后仍失败的文章总数

    for batch_start in range(0, total, ARTICLES_PER_BATCH):
        batch_end = min(batch_start + ARTICLES_PER_BATCH, total)
        batch_texts = content_list[batch_start:batch_end]

        # 直接批量推理
        try:
            new_results = engine.run_all_models(batch_texts)
        except Exception as e:
            # fix(omni-g-berts-02, 2026-06-11): 批级异常不再整批置哨兵 —
            # 逐篇单独重试一次, 仍失败的文章才写失败哨兵 (num_windows=-1,
            # 概率 NaN, label=None, 与空文本 num_windows=0 严格区分)。
            logger.warning(
                f"  批次 {batch_start}-{batch_end} 推理异常, 逐篇重试一次: {e}"
            )
            new_results = {sn: [] for sn in loaded_model_names}
            for art_offset, text in enumerate(batch_texts):
                try:
                    single = engine.run_all_models([text])
                    for sn in loaded_model_names:
                        sn_single = single.get(sn) or [engine._failure_result(sn)]
                        new_results[sn].append(sn_single[0])
                except Exception as retry_e:
                    n_failed_articles += 1
                    logger.warning(
                        f"    文章 idx={batch_start + art_offset} 单篇重试仍失败, "
                        f"写失败哨兵: {retry_e}"
                    )
                    for sn in loaded_model_names:
                        new_results[sn].append(engine._failure_result(sn))

        for sn in loaded_model_names:
            sn_results = new_results.get(sn, [])
            # 填充可能的长度不足（理论上不应发生; 缺位 = 结果缺失而非空文本,
            # fix(omni-g-berts-02): 改用失败哨兵而非空文本哨兵）
            while len(sn_results) < len(batch_texts):
                sn_results.append(engine._failure_result(sn))
            model_results_all[sn].extend(sn_results)

        # 进度日志
        processed = batch_end
        if processed % 500 == 0 or processed == total:
            elapsed = time.time() - inference_start
            speed = processed / elapsed if elapsed > 0 else 0
            logger.info(f"  [全部模型] 进度: {processed}/{total} "
                        f"({speed:.1f} 文章/秒)")

    total_elapsed = time.time() - inference_start
    logger.info(f"  全部模型推理完成。总耗时: {total_elapsed:.1f}s, "
                f"速度: {total / total_elapsed:.1f} 文章/秒 (×{len(model_results_all)}模型)")

    # fix(omni-g-berts-02): 末尾统计重试后仍失败的文章数 (失败哨兵已写入,
    # 下游可由 {sn}_infer_failed 标志列 / num_windows=-1 过滤)
    if n_failed_articles:
        logger.error(
            f"  ⚠ {n_failed_articles}/{total} 篇文章批级+单篇重试均失败, "
            f"已写失败哨兵 (label=None, 概率=NaN, num_windows=-1); "
            f"请检查 GPU/驱动日志后考虑重跑本阶段。"
        )

    # GPU 显存日志
    if DEVICE.type == 'cuda':
        allocated = torch.cuda.memory_allocated() / 1e9
        reserved = torch.cuda.memory_reserved() / 1e9
        logger.info(f"  GPU 显存: 已分配 {allocated:.2f} GB, 已保留 {reserved:.2f} GB")

    # ── 构建输出 ──
    output = {}
    for sn, results in model_results_all.items():
        cfg = engine.loaded_configs[sn]
        label_map = cfg['label_map']

        # 标签列
        labels = [r['label'] for r in results]
        label_counts = Counter(labels)

        stats = {}
        for label_name in label_map.values():
            stats[f'{sn}_{label_name}'] = label_counts.get(label_name, 0)

        # fix(omni-g-berts-02): avg_windows 排除失败哨兵 (-1), 不让其拉低均值
        _nw_valid = [r['num_windows'] for r in results if r['num_windows'] >= 0]
        avg_windows = np.mean(_nw_valid) if _nw_valid else 0

        # 输出列
        columns = {f'{sn}_label': labels}
        all_probs = {label: [] for label in label_map.values()}
        for result in results:
            for label_name in label_map.values():
                all_probs[label_name].append(result['probabilities'].get(label_name, 0.0))
        for label_name, probs_list in all_probs.items():
            columns[f'{sn}_{label_name}'] = probs_list

        # fix(omni-g-berts-02, 2026-06-11): 2-class 模型 (如 finbert2) 输出端补
        # 中性=NaN 列 (而非 0) — 下游 2-class/3-class 混均时 pandas mean/sum 自动
        # 跳过 NaN, 不再把"该模型无中性维度"冒充为"中性概率恒 0"。
        # 跨文件聚合接口注明: pipeline/panel/encode.py 的 THREE_CLASS_MODELS 守卫
        # 仍按 config label_map 判定 (本列存在与否不改其现行行为); 若 panel 组
        # 决定统一口径, 可将 encode.py:535 守卫改为列存在性 + NaN-aware 聚合。
        if not any(_polarity_of(v) == 'neu' for v in label_map.values()):
            columns[f'{sn}_中性'] = [float('nan')] * len(results)

        # fix(omni-g-berts-02): 每篇 failure 标志列 (失败哨兵 num_windows=-1);
        # 主函数追加轨道后缀 → {sn}_infer_failed_full / _ctx / _ss (三轨)
        columns[f'{sn}_infer_failed'] = [r['num_windows'] == -1 for r in results]

        num_windows_list = [r['num_windows'] for r in results]
        output[sn] = {'columns': columns, 'stats': stats, 'avg_windows': avg_windows,
                      'num_windows_list': num_windows_list}

    return output


# ============================================================================
# 5. 统计报告
# ============================================================================

def log_classification_report(output: dict, total: int):
    """输出 BERT 情感分析统计报告。

    Args:
        output: process_all_models 返回的结果字典。
        total:  总记录数。
    """
    logger.info("=" * 70)
    logger.info("===      BERT 模型情感分析统计报告      ===")
    logger.info("=" * 70)
    logger.info(f"总记录数: {total:,}")
    logger.info(f"推理设备: {DEVICE}")
    logger.info(f"Mixed Precision: {'AMP' if USE_AMP else '禁用'}")
    logger.info(f"模型权重精度: {'FP32 (AMP推理时动态转换)' if DEVICE.type == 'cuda' else 'FP32'}")
    logger.info(f"滑动窗口步长比例: {WINDOW_STRIDE_RATIO}")
    logger.info(f"推理 batch 大小: {INFERENCE_BATCH_SIZE}")
    logger.info(f"动态填充 + 长度排序: 已启用")
    logger.info(f"多模型并行加载: 已启用 (共享分词)")

    logger.info("-" * 70)
    logger.info(f"{'模型':<20} {'正面':>8} {'中性':>8} {'负面':>8} "
                f"{'正面占比':>10} {'中性占比':>10} {'负面占比':>10}")
    logger.info("-" * 70)

    for mc in MODEL_CONFIGS:
        sn = mc['short_name']
        if sn not in output:
            continue
        stats = output[sn]['stats']
        pos = stats.get(f'{sn}_正面', 0)
        neu = stats.get(f'{sn}_中性', 0)
        neg = stats.get(f'{sn}_负面', 0)
        pos_pct = f"{pos / total * 100:.1f}%" if total > 0 else "N/A"
        neu_pct = f"{neu / total * 100:.1f}%" if total > 0 else "N/A"
        neg_pct = f"{neg / total * 100:.1f}%" if total > 0 else "N/A"
        logger.info(f"  {sn:<20} {pos:>8,} {neu:>8,} {neg:>8,} "
                    f"{pos_pct:>10} {neu_pct:>10} {neg_pct:>10}")

    # ── 滑动窗口截断统计 ──
    _first_key = next(iter(output), None)
    if _first_key and 'num_windows_list' in output[_first_key]:
        nw_list = output[_first_key]['num_windows_list']
        nw_arr = np.array(nw_list)
        # num_windows=0 表示空文本, -1 表示推理失败哨兵 (fix g-berts-02), 排除后统计
        valid_nw = nw_arr[nw_arr > 0]
        if len(valid_nw) > 0:
            multi_window = int((valid_nw > 1).sum())
            single_window = int((valid_nw == 1).sum())
            n_valid = len(valid_nw)
            n_empty = int((nw_arr == 0).sum())
            n_failed = int((nw_arr == -1).sum())
            logger.info("-" * 70)
            logger.info("滑动窗口截断统计 (Sliding Window Truncation Statistics):")
            logger.info(f"  有效文章数: {n_valid:,} "
                        f"(排除 {n_empty} 篇空文本, {n_failed} 篇推理失败哨兵)")
            logger.info(f"  单窗口文章: {single_window:,} 篇 ({single_window / n_valid * 100:.1f}%)")
            logger.info(f"  多窗口文章: {multi_window:,} 篇 ({multi_window / n_valid * 100:.1f}%)")
            logger.info(f"  窗口数统计: mean={valid_nw.mean():.2f}, "
                        f"median={float(np.median(valid_nw)):.0f}, "
                        f"max={int(valid_nw.max())}, std={valid_nw.std():.2f}")
            nw_dist = sorted(Counter(valid_nw.tolist()).items())
            dist_str = ", ".join(f"{int(k)}窗口:{v}篇" for k, v in nw_dist[:8])
            if len(nw_dist) > 8:
                dist_str += f", ... (共{len(nw_dist)}种)"
            logger.info(f"  窗口数分布: {dist_str}")

    logger.info("=" * 70)


def _track_polarity_shares(out_dict: dict, total: int) -> dict:
    """从单轨 output 提取各模型 正面/中性/负面 占比与失败篇数 (仅供【结果分析】日志)。

    纯只读聚合, 不回写任何 df/产物。返回:
        {short_name: {'pos_pct':.., 'neu_pct':.., 'neg_pct':.., 'n_failed':..,
                      'avg_windows':..}}
    """
    summary = {}
    for sn, blob in out_dict.items():
        stats = blob.get('stats', {})
        pos = stats.get(f'{sn}_正面', 0)
        neu = stats.get(f'{sn}_中性', 0)
        neg = stats.get(f'{sn}_负面', 0)
        nw_list = blob.get('num_windows_list', [])
        n_failed = sum(1 for nw in nw_list if nw == -1)
        summary[sn] = {
            'pos_pct': (pos / total * 100) if total > 0 else float('nan'),
            'neu_pct': (neu / total * 100) if total > 0 else float('nan'),
            'neg_pct': (neg / total * 100) if total > 0 else float('nan'),
            'n_failed': n_failed,
            'avg_windows': blob.get('avg_windows', 0),
        }
    return summary


# ============================================================================
# 6. 主函数
# ============================================================================

def main():
    """BERT 情感分析阶段主入口（v5 GPU 全面加速架构）。

    流程：
      1. 加载输入数据（阶段22词典法输出）
      2. 预加载全部模型到 GPU (FP32, AMP推理)
      3. 批量推理（分批调用 process_all_models）
      4. 写回各模型预测列，保存输出 Parquet
      5. 释放模型显存，生成统计报告和预览 CSV
    """
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")
    logger.info("=" * 72)
    logger.info("阶段 23: BERT 情感分析 (三轨/优雅降级; finbert_cn / fin_sent_zh / finbert2)")
    logger.info("=" * 72)
    logger.info("【功能】用 3 个金融领域预训练 BERT 模型对每篇新闻判正面/中性/负面, 与")
    logger.info("        stage 21(LLM)、stage 22(词典) 构成三条独立情感测度路线互相印证;")
    logger.info("        按全文(_full)/银行相关段(_ctx)/银行金科同句段(_ss)各推理一遍, 产")
    logger.info("        出 {模型}_label + 各标签概率列 (供下游 stage 45 panel/encode 聚合 BERT 极性) +")
    logger.info("        bert_num_windows_{轨} (仅供可选验证阶段 tone_validation 窗口数分层; production panel 不消费)。")
    logger.info("        stage 24 herd_decay 硬依赖本阶段整个 23_bert_tone.parquet 文件 (缺文件即 SystemExit(1)), 但只读 content/标识列。")
    logger.info(f"【方法】超长文本滑动窗口切片 (WINDOW_STRIDE_RATIO={WINDOW_STRIDE_RATIO:.2f}, "
                "相邻窗 50% 重叠, 单窗 ≤")
    logger.info("        max_length 512 含特殊 token) + 置信度加权池化 logits*=Σ(conf_k·logits_k)/Σconf_k;")
    logger.info("        各模型按自身 tokenizer 分窗 (fix g-berts-01 词表不同不共享分词); argmax 分类。")
    logger.info("【判读】三模型全语料聚合极性占比相近 (边际分布一致), 若模型间占比差 >15pp 需在")
    logger.info("        三角验证中重点关注。num_windows: ≥1 正常 / 0 空文本 / -1 推理失败哨兵。")
    logger.info("        (注: 此处仅比对全语料聚合极性占比; 文章级一致性/收敛效度须看 stage 39a")
    logger.info("        pipeline/audit/inter_track_kappa.py 的跨模型 kappa。)")
    logger.info("【确定性】纯本地 torch/transformers 推理, 无 LLM API、无 _llm_cache.db; 确定性来自模型")
    logger.info(f"          权重 + argmax (deterministic_mode={_DETERMINISTIC_MODE}; "
                "AMP 对 argmax 分类结果无影响)。")
    logger.info("=" * 72)
    logger.info(f"配置的模型数量: {len(MODEL_CONFIGS)}")
    logger.info(f"推理 batch 大小: {INFERENCE_BATCH_SIZE}")
    logger.info(f"每次处理文章数: {ARTICLES_PER_BATCH}")
    for mc in MODEL_CONFIGS:
        logger.info(f"  - {mc['short_name']}: {mc['model_id']} ({mc['description']})")

    # ── 定义输入输出路径 ──
    input_path = os.path.join(
        CONFIG['paths']['output_dir'],
        CONFIG['filenames'].get('output_22_words_tone', '22_words_tone.parquet')
    )
    output_path = os.path.join(
        CONFIG['paths']['output_dir'],
        CONFIG['filenames'].get('output_23_bert_tone', '23_bert_tone.parquet')
    )

    if not os.path.exists(input_path):
        logger.error(f"输入文件未找到: {input_path}")
        raise SystemExit(1)

    logger.info(f"正在从 {input_path} 加载数据...")
    df = pd.read_parquet(input_path)
    input_rows = len(df)
    logger.info(f"已加载 {input_rows:,} 行数据。")
    log_memory_usage(logger, "数据加载后")

    # ── Step 1: 一次性加载全部模型到 GPU (FP32, AMP推理) ──
    logger.info("=" * 50)
    logger.info("正在预加载全部模型到 GPU (FP32, AMP推理)...")
    engine = MultiModelSentimentEngine(MODEL_CONFIGS)
    loaded_names = engine.load_all()
    if not loaded_names:
        logger.error("没有模型加载成功，退出阶段")
        raise SystemExit(1)
    log_memory_usage(logger, "全部模型加载后")

    # ── Step 1b: 构建三轨文本列表 (full / ctx / ss) ──
    # full 轨 = 标题 + 内容; ctx 轨 = 标题 + 实体窗口; ss 轨 = 标题 + 银行∧金科
    # 同句共现窗口 (content_ss 由 stage 13 ctx_materializer 物化, 无共现→镜像 ctx
    # 回退全文 body)。标题轨已取消; 三轨文本均经 prepend_title 注入标题
    # (与 stage 13 / 词典法对齐)。
    from news_process.core.text.entity_context import prepend_title
    _titles = (df['标题'].fillna('').astype(str).tolist()
               if '标题' in df.columns else [''] * len(df))
    _bodies = df['内容'].fillna('').astype(str).tolist()
    _ctx_bodies = df['content_ctx'].fillna(df['内容']).astype(str).tolist()
    content_full_list = [prepend_title(t, b) for t, b in zip(_titles, _bodies)]
    content_ctx_list = [prepend_title(t, c) for t, c in zip(_titles, _ctx_bodies)]

    # ss 轨优雅跳过: content_ss 由 stage 13 物化 (v3.9.0 三轨); 旧 schema 缺列时
    # 跳过 ss 推理 (镜像 ctx 守卫风格), 不影响 full/ctx 两路产出。
    _has_ss = 'content_ss' in df.columns
    content_ss_list = None
    if _has_ss:
        _ss_bodies = df['content_ss'].fillna(df['内容']).astype(str).tolist()
        content_ss_list = [prepend_title(t, s) for t, s in zip(_titles, _ss_bodies)]
        logger.info(
            f"三轨文本列表构建完成 (含标题注入): full={len(content_full_list)}, "
            f"ctx={len(content_ctx_list)}, ss={len(content_ss_list)}"
        )
    else:
        logger.warning(
            "  content_ss 列缺失 (旧 schema) — ss 轨 (银行+金科同句) 优雅跳过, "
            "仅产出 full/ctx 两路。"
        )
        logger.info(
            f"文本列表构建完成 (含标题注入): full={len(content_full_list)}, "
            f"ctx={len(content_ctx_list)}, ss=跳过"
        )

    # ── Step 2: 三轨批量推理（物理隔离，防止 OOM） ──
    logger.info("=" * 50)
    logger.info("开始多模型三轨批量推理...")

    logger.info("启动 [_ctx] 轨道推理...")
    output_ctx = process_all_models(df, engine, content_ctx_list)

    logger.info("启动 [_full] 轨道推理...")
    output_full = process_all_models(df, engine, content_full_list)

    # ss 轨 (银行+金科同句): content_ss 缺列时 output_ss=None, 下游写回/统计跳过。
    output_ss = None
    if _has_ss:
        logger.info("启动 [_ss] 轨道推理 (银行+金科同句)...")
        output_ss = process_all_models(df, engine, content_ss_list)

    # ── Step 3: 将三轨结果写回 DataFrame（带后缀） ──
    # 镜像 ctx 守卫风格: ss 轨缺列 (output_ss is None) 时 (output, suffix) 对自动
    # 被过滤掉, 不写任何 *_ss 列 (优雅跳过)。
    _track_outputs = [(output_ctx, '_ctx'), (output_full, '_full')]
    if output_ss is not None:
        _track_outputs.append((output_ss, '_ss'))
    for out_dict, suffix in _track_outputs:
        for mc in MODEL_CONFIGS:
            sn = mc['short_name']
            if sn in out_dict:
                for col_name, col_data in out_dict[sn]['columns'].items():
                    df[f"{col_name}{suffix}"] = col_data

    # ── Step 3b: 写入 BERT 窗口数列（三轨，供下游分层分析使用） ──
    # 语义说明: num_windows ≥1 正常推理; 0 = 空文本; -1 = 推理失败哨兵
    # (fix g-berts-02)。fix g-berts-01 后各模型按自身 tokenizer 分词, 窗口数
    # 是 tokenizer 特异的; 本列取首个模型的计数 (日志注明基于哪个模型)。
    # ss 轨 (银行+金科同句) 缺列 (output_ss is None) 时 bert_num_windows_ss 不写。
    _first_sn = next((mc['short_name'] for mc in MODEL_CONFIGS
                      if mc['short_name'] in output_full), None)
    if _first_sn:
        if _first_sn in output_ctx and 'num_windows_list' in output_ctx[_first_sn]:
            df['bert_num_windows_ctx'] = output_ctx[_first_sn]['num_windows_list']
            logger.info(f"  已写入 bert_num_windows_ctx 列 (基于模型: {_first_sn})")
        if _first_sn in output_full and 'num_windows_list' in output_full[_first_sn]:
            df['bert_num_windows_full'] = output_full[_first_sn]['num_windows_list']
            logger.info(f"  已写入 bert_num_windows_full 列 (基于模型: {_first_sn})")
        if (output_ss is not None and _first_sn in output_ss
                and 'num_windows_list' in output_ss[_first_sn]):
            df['bert_num_windows_ss'] = output_ss[_first_sn]['num_windows_list']
            logger.info(f"  已写入 bert_num_windows_ss 列 (基于模型: {_first_sn})")

    # ── Step 4: 保存输出 ──
    # 使用数据版本控制保存
    from news_process.core.data_versioning import save_parquet_with_metadata
    save_parquet_with_metadata(
        df=df,
        output_path=output_path,
        stage_name="23_tone_berts",
        config=CONFIG,
        input_files=[input_path],
    )
    logger.info(f"已保存输出文件: {output_path} ({len(df):,} 行)")

    # ── Step 5: 释放全部模型 ──
    engine.unload_all()
    log_memory_usage(logger, "模型释放后")

    # ── 打印统计报告（三轨分别打印; ss 缺列时跳过第三份） ──
    logger.info("=== [_ctx] 轨道统计 ===")
    log_classification_report(output_ctx, len(df))
    logger.info("=== [_full] 轨道统计 ===")
    log_classification_report(output_full, len(df))
    if output_ss is not None:
        logger.info("=== [_ss] 轨道统计 (银行+金科同句) ===")
        log_classification_report(output_ss, len(df))

    # ── 生成预览 CSV ──
    preview_path = output_path.replace('.parquet', '.csv')
    safe_save_preview_csv(df, preview_path, logger)

    # ── 【结果分析】: 对真实产出指标对照阈值/预期方向给判读 ──
    # 整块只读聚合, 不回写 df/产物。已在最终写盘 (save_parquet_with_metadata) 之后,
    # 仍统一包 try/except 防边缘崩溃 (如空 Series.max()) 中断阶段收尾 (crash-guard, golden-safe)。
    try:
        _total = len(df)
        logger.info("-" * 72)
        logger.info("【结果分析】BERT 三轨情感分类产出解读 (对照阈值/预期方向):")

        # ① 模型加载/降级状态
        n_expected = len(MODEL_CONFIGS)
        n_loaded = len(loaded_names)
        logger.info(f"  · 模型加载: {n_loaded}/{n_expected} 成功 "
                    f"(预期跳过 {len(engine.skipped_expected)}: {engine.skipped_expected or '无'}; "
                    f"意外失败 {len(engine.failed_models)}: {engine.failed_models or '无'})。")
        if 'finbert2' in engine.skipped_expected:
            logger.warning(
                "    ⚠ finbert2 (本地私有 2-class 模型) 优雅跳过 — FINBERT2_MODEL_DIR 未配置或"
                "路径不存在; 另 2 个 HF 模型 (finbert_cn/fin_sent_zh) 照跑, 输出缺 finbert2_* 列属预期。"
            )
        if engine.failed_models:
            logger.warning(
                f"    ⚠ {engine.failed_models} 为非预期加载失败 (strict_models=false 才会走到此)，"
                "其三轨情感列将整体缺失, 下游 stage 24/45 按列存在性静默跳过 — 请核查 HF 离线缓存/驱动。"
            )

        # ② 三轨极性占比 — 跨模型边际分布同向性 (仅全语料聚合占比, 非文章级收敛效度; 后者看 stage 39a)
        _AGREE_THRESHOLD_PP = 15.0  # 模型间占比差阈值, 取自 banner【判读】/逐行注释
        for out_dict, track_name in [(output_full, '_full'), (output_ctx, '_ctx'),
                                     (output_ss, '_ss (银行+金科同句)')]:
            if out_dict is None:
                logger.info(f"  · 轨道 {track_name}: 优雅跳过 (content_ss 列缺失, 旧 schema)。")
                continue
            if _total <= 0:
                logger.info(f"  · 轨道 {track_name}: 无有效数据 (df 0 行), 跳过占比判读。")
                continue
            shares = _track_polarity_shares(out_dict, _total)
            pos_list = [v['pos_pct'] for v in shares.values()]
            neg_list = [v['neg_pct'] for v in shares.values()]
            for sn, v in shares.items():
                logger.info(
                    f"  · 轨道 {track_name} 模型 {sn}: 正面 {v['pos_pct']:.1f}% / "
                    f"中性 {v['neu_pct']:.1f}% / 负面 {v['neg_pct']:.1f}%, "
                    f"平均窗口数 {v['avg_windows']:.2f}, 推理失败 {v['n_failed']} 篇。"
                )
                if v['n_failed'] > 0:
                    logger.warning(
                        f"    ⚠ {sn}{track_name} 有 {v['n_failed']} 篇推理失败哨兵 "
                        f"(num_windows=-1, 概率 NaN); 下游聚合自动跳过, 但失败率高需重跑本阶段。"
                    )
            # NaN-guard: 任一占比为 NaN (理论上 total<=0 已先跳过, 防御性兜底) 时不做方向判读,
            # 否则 max/min 含 nan 的比较恒 False 会误落到"边际占比相近"档。
            _valid_pn = [p for p in (pos_list + neg_list) if not (isinstance(p, float) and np.isnan(p))]
            if len(_valid_pn) != len(pos_list) + len(neg_list):
                logger.info(
                    f"    {track_name} 占比含 NaN (无有效情感数据), 跳过跨模型同向性判读。"
                )
            elif len(pos_list) >= 2:
                pos_spread = max(pos_list) - min(pos_list)
                neg_spread = max(neg_list) - min(neg_list)
                _verdict = ("边际占比相近" if max(pos_spread, neg_spread) <= _AGREE_THRESHOLD_PP
                            else "边际占比发散(需关注)")
                logger.info(
                    f"    模型间占比极差: 正面 {pos_spread:.1f}pp / 负面 {neg_spread:.1f}pp "
                    f"→ {_verdict} (阈值 {_AGREE_THRESHOLD_PP:.0f}pp; ≤阈值=三模型全语料聚合极性"
                    f"占比相近(边际分布一致), 非逐文章一致性; >阈值=三角验证重点关注; "
                    f"文章级 concordance/收敛效度须看 stage 39a inter_track_kappa.py)。"
                )
            else:
                logger.info(
                    f"    {track_name} 仅 {len(pos_list)} 个模型成功 → 无法做跨模型同向性判读 "
                    f"(finbert2 跳过时只剩 2 个 HF 模型)。"
                )

        # ③ 滑动窗口截断 — 取 full 轨首个模型, 判读长文占比
        _first_sn = next((mc['short_name'] for mc in MODEL_CONFIGS
                          if mc['short_name'] in output_full), None)
        if _first_sn and 'num_windows_list' in output_full.get(_first_sn, {}):
            _nw = np.array(output_full[_first_sn]['num_windows_list'])
            _valid = _nw[_nw > 0]
            if len(_valid) > 0:
                _multi = int((_valid > 1).sum())
                _multi_pct = _multi / len(_valid) * 100
                _empty = int((_nw == 0).sum())
                _maxw = int(_valid.max())
                logger.info(
                    f"  · 滑动窗口 (基于 {_first_sn}, _full 轨): 多窗口长文 {_multi} 篇 "
                    f"({_multi_pct:.1f}%), 最大窗口数 {_maxw}, 空文本 {_empty} 篇。"
                )
                if _maxw > 10:
                    logger.info(
                        f"    注: 最大窗口数 {_maxw}>10, 存在超长文本; 置信度加权池化已无损融合各窗, 无截断丢失。"
                    )

        # ④ 小样本/盘面规模警告
        if _total <= 2000:
            logger.info(
                f"  · 样本规模 {_total:,} 行 (盘面 T=2 小样本): 本次仅验证三轨推理管道正确性 "
                "(无 NameError/列对齐/降级路径); 占比与同向性的实证结论以 17M/T=18 全量重跑为准。"
            )
        logger.info("-" * 72)
    except Exception as _e:  # noqa: BLE001  仅日志诊断, 绝不影响已落盘产物
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=input_rows, output_rows=len(df))
    _track_mode = "三轨模式" if output_ss is not None else "双轨模式 (ss 缺列跳过)"
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ({_track_mode}) ---")


if __name__ == "__main__":
    main()
