"""
23_tone_berts.py — 阶段23：基于 BERT 系列预训练模型的情感分析
===========================================================================

功能：
    使用多个中文金融/通用预训练语言模型，对每篇新闻进行情感分类。

模型列表（由 config.yaml 中 sentiment_analysis.tone_berts.models 配置）：
    1. yiyanghkust/finbert-tone-chinese — FinBERT 中文金融情感
    2. bardsai/finance-sentiment-zh-base — 中文金融短语级情感
    3. IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment — 二郎神 Roberta 情感
    4. hw2942/bert-base-chinese-finetuning-financial-news-sentiment-v2 — 金融新闻情感
    5. FinBERT2-base — 本地微调金融分类模型

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

性能优化（v5 — GPU 全面加速架构）：
    - **FP16 模型权重**：model.half() 将权重永久转为半精度，减半显存带宽
    - **增大 batch size**：128，FP16 下 RTX 3090 显存充裕
    - **动态填充 + 长度排序**：窗口按长度排序分桶，每个 mini-batch 仅填充到
      实际最长序列，减少无效计算
    - **cuDNN benchmark**：自动调优卷积算法
    - **全部模型预加载到 GPU**：消除串行加载/卸载开销
    - **分词结果共享**：相同 max_length 的模型共享同一次批量分词和窗口
    - **pin_memory + non_blocking**：异步 CPU→GPU 数据传输

输入：
    阶段22（词典法情感分析）输出的 Parquet 文件（output_22_words_tone）

输出：
    追加各模型的情感标签和概率列（output_23_bert_tone）
"""

import os
import time
import gc
import pandas as pd
import numpy as np
from collections import Counter
from utils.helpers import load_config, setup_logging, log_memory_usage, log_stage_summary, safe_save_preview_csv

try:
    import torch
    import torch.nn.functional as F
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
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
if DEVICE.type == 'cuda':
    logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    gpu_total_mem = torch.cuda.get_device_properties(0).total_memory
    logger.info(f"GPU 显存: {gpu_total_mem / 1e9:.1f} GB")
    # cuDNN benchmark: 对固定输入尺寸自动选择最快的卷积实现
    torch.backends.cudnn.benchmark = True

# 是否启用 AMP (Automatic Mixed Precision) 加速
USE_AMP = (DEVICE.type == 'cuda' and hasattr(torch, 'amp'))
if USE_AMP:
    logger.info("Mixed Precision (FP16) 推理加速: 已启用")

# 标签映射（从模型输出 id 到中文标签）
DEFAULT_LABEL_MAP = {0: "负面", 1: "中性", 2: "正面"}
DEFAULT_LABEL_MAP_2CLASS = {0: "负面", 1: "正面"}


# ============================================================================
# 2. 模型配置（从 config.yaml 加载，支持 fallback 到内置默认值）
# ============================================================================

def _build_model_configs() -> list:
    """从 config.yaml 的 sentiment_analysis.tone_berts.models 构建模型配置列表。

    label_map 键在 YAML 中为字符串（如 "0"），这里转换为整数。

    Returns:
        list: 模型配置字典列表，每项包含 model_id、short_name、description、
              max_length、label_map（int 键）。
    """
    yaml_models = BERT_PARAMS.get('models', [])
    if not yaml_models:
        # Fallback：内置默认配置
        logger.warning("config.yaml 中未找到 tone_berts.models，使用内置默认配置")
        return [
            {
                "model_id": "yiyanghkust/finbert-tone-chinese",
                "short_name": "finbert_cn",
                "description": "FinBERT 中文情感分析(金融社区中认知度较高)",
                "max_length": 512,
                "label_map": {0: "中性", 1: "正面", 2: "负面"},
            },
            {
                "model_id": "bardsai/finance-sentiment-zh-base",
                "short_name": "fin_sent_zh",
                "description": "中文金融情感分析(基于Financial PhraseBank微调；F1 macro 0.966)",
                "max_length": 512,
                "label_map": {0: "正面", 1: "中性", 2: "负面"},
            },
            {
                "model_id": "IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment",
                "short_name": "erlangshen",
                "description": "二郎神 Roberta 110M 情感分类",
                "max_length": 512,
                "label_map": {0: "负面", 1: "正面"},
            },
            {
                "model_id": "hw2942/bert-base-chinese-finetuning-financial-news-sentiment-v2",
                "short_name": "hw2942",
                "description": "hw2942金融新闻文本的情感分类（训练数据量偏小，泛化能力可能有限）",
                "max_length": 512,
                "label_map": {0: "负面", 1: "中性", 2: "正面"},
            },
            {
                "model_id": "F:/WiseSearch/data_antigravity_project/FinBERT/Fin-labeler/classifier_models/FinBERT2-base_SC_2",
                "short_name": "finbert2",
                "description": "FinBERT2 金融微调分类模型",
                "max_length": 512,
                "label_map": {0: "负面", 1: "正面"},
            },
        ]

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
# v5: 增大到 128，FP16 下 RTX 3090 显存充裕
INFERENCE_BATCH_SIZE = BERT_PARAMS.get('inference_batch_size', 128)

# 每次调用 engine.run_all_models 的文章批次数
ARTICLES_PER_BATCH = BERT_PARAMS.get('articles_per_batch', 200)


# ============================================================================
# 3. 多模型推理引擎（v5 — FP16 + 动态填充 + 长度排序）
# ============================================================================

class MultiModelSentimentEngine:
    """多模型推理引擎 — AMP 动态混合精度 + 动态填充 + 长度排序。

    v5 架构优化：
      - AMP autocast: 动态混合精度推理，自动选择最优精度
      - 窗口按长度排序分桶，mini-batch 仅填充到实际最长序列
      - 增大 batch size (128) 提升 GPU 吞吐
      - 相同 max_length 的模型共享分词 + 窗口数据

    Attributes:
        models:       已加载的 PyTorch 模型。
        tokenizers:   每个模型对应的 tokenizer。
        model_configs: 模型配置列表。n    """

    def __init__(self, model_configs: list):
        self.model_configs = model_configs
        self.models = {}         # short_name -> PyTorch model (FP16)
        self.tokenizers = {}     # short_name -> tokenizer
        self.loaded_configs = {} # short_name -> config (含实际 num_labels)

        # 按 max_length 分组（用于共享分词）
        self._groups = {}  # max_length -> [short_name, ...]

    def load_all(self) -> list:
        """一次性加载全部模型到 GPU（FP16 权重）。

        Returns:
            list: 成功加载的模型名称列表。
        """
        load_start = time.time()
        loaded_names = []

        for mc in self.model_configs:
            short_name = mc['short_name']
            model_id = mc['model_id']

            try:
                logger.info(f"  正在加载模型: {model_id} ...")

                local_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'models', short_name
                )
                model_path = local_path if os.path.exists(local_path) else model_id

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
                        logger.warning(
                            f"  模型 {short_name} 实际标签数={actual}, 配置={num_labels}。以模型为准。"
                        )
                        num_labels = actual
                        label_map = DEFAULT_LABEL_MAP_2CLASS if actual == 2 else DEFAULT_LABEL_MAP

                self.models[short_name] = model
                self.tokenizers[short_name] = tokenizer
                self.loaded_configs[short_name] = {
                    **mc,
                    'label_map': label_map,
                    'num_labels': num_labels,
                }
                loaded_names.append(short_name)

                # 分组
                ml = mc['max_length']
                self._groups.setdefault(ml, []).append(short_name)

                logger.info(f"  模型 {short_name} 加载成功 (labels={num_labels})")

            except Exception as e:
                logger.error(f"  模型 {model_id} 加载失败: {e}")

        load_elapsed = time.time() - load_start
        logger.info(f"全部模型加载完毕: {len(loaded_names)}/{len(self.model_configs)} "
                     f"(耗时 {load_elapsed:.1f}s)")

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
          - FP16 权重 + AMP autocast 推理
          - 增大 batch size (128)

        Args:
            texts: 文本列表。

        Returns:
            dict: {short_name: list[dict]} 每个模型的逐文章预测结果。
        """
        n_texts = len(texts)
        all_model_results = {}

        # ── 按 max_length 分组共享分词 ──
        for max_length, group_names in self._groups.items():
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

                for bs in range(0, total_windows, INFERENCE_BATCH_SIZE):
                    be = min(bs + INFERENCE_BATCH_SIZE, total_windows)
                    batch_sorted_idx = sorted_indices[bs:be]
                    batch_size = be - bs

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

                    # GPU 推理（FP16 权重 + AMP autocast）
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
        """返回空结果。"""
        cfg = self.loaded_configs.get(short_name)
        if cfg:
            prob_dict = {label: 0.0 for label in cfg['label_map'].values()}
        else:
            prob_dict = {'正面': 0.0, '中性': 0.0, '负面': 0.0}
        return {'label': '中性', 'probabilities': prob_dict, 'num_windows': 0}


# ============================================================================
# 4. 批量处理协调器
# ============================================================================

def process_all_models(df: pd.DataFrame, engine: MultiModelSentimentEngine, content_list: list) -> dict:
    """使用多模型引擎对全部数据进行批量推理。

    Args:
        df:           包含"内容"列的 DataFrame。
        engine:       已加载全部模型的多模型引擎。
        content_list: 预构建的文本列表（全文或上下文片段）。

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

    for batch_start in range(0, total, ARTICLES_PER_BATCH):
        batch_end = min(batch_start + ARTICLES_PER_BATCH, total)
        batch_texts = content_list[batch_start:batch_end]

        # 直接批量推理
        try:
            new_results = engine.run_all_models(batch_texts)
        except Exception as e:
            logger.warning(f"  批次 {batch_start}-{batch_end} 推理异常: {e}")
            new_results = {}
            for sn in loaded_model_names:
                new_results[sn] = [engine._empty_result(sn) for _ in batch_texts]

        for sn in loaded_model_names:
            sn_results = new_results.get(sn, [])
            # 填充可能的长度不足（理论上不应发生）
            while len(sn_results) < len(batch_texts):
                sn_results.append(engine._empty_result(sn))
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

        avg_windows = np.mean([r['num_windows'] for r in results]) if results else 0

        # 输出列
        columns = {f'{sn}_label': labels}
        all_probs = {label: [] for label in label_map.values()}
        for result in results:
            for label_name in label_map.values():
                all_probs[label_name].append(result['probabilities'].get(label_name, 0.0))
        for label_name, probs_list in all_probs.items():
            columns[f'{sn}_{label_name}'] = probs_list

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
    logger.info(f"Mixed Precision: {'FP16' if USE_AMP else '禁用'}")
    logger.info(f"FP16 模型权重: {'已启用' if DEVICE.type == 'cuda' else '禁用'}")
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
        # num_windows=0 表示空文本/推理异常，排除后统计
        valid_nw = nw_arr[nw_arr > 0]
        if len(valid_nw) > 0:
            multi_window = int((valid_nw > 1).sum())
            single_window = int((valid_nw == 1).sum())
            n_valid = len(valid_nw)
            n_excluded = int((nw_arr == 0).sum())
            logger.info("-" * 70)
            logger.info("滑动窗口截断统计 (Sliding Window Truncation Statistics):")
            logger.info(f"  有效文章数: {n_valid:,} (排除 {n_excluded} 篇空文本/异常)")
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


# ============================================================================
# 6. 主函数
# ============================================================================

def main():
    """BERT 情感分析阶段主入口（v5 GPU 全面加速架构）。

    流程：
      1. 加载输入数据（阶段22词典法输出）
      2. 预加载全部模型到 GPU (FP16)
      3. 批量推理（分批调用 process_all_models）
      4. 写回各模型预测列，保存输出 Parquet
      5. 释放模型显存，生成统计报告和预览 CSV
    """
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")
    logger.info("")
    logger.info("  📌 阶段目的")
    logger.info("     使用 5 个 BERT 系列预训练模型对每篇新闻进行情感分类。")
    logger.info("     采用双轨模式: 全文(_full)和上下文片段(_ctx)分别推理。")
    logger.info("     超长文本使用滑动窗口切片 + 置信度加权池化聚合。")
    logger.info("")
    logger.info("  📖 方法论依据")
    logger.info("     · 滑动窗口: 步长比例 0.5, 确保相邻窗口有 50% 重叠, 减少边界信息丢失")
    logger.info("     · 置信度加权池化: 高置信度窗口获得更大权重, 避免噪声窗口拉偏结果")
    logger.info("     · AMP 动态混合精度: 自动选择 FP16/FP32, 对 argmax 分类结果无影响")
    logger.info("")
    logger.info("  📊 关键指标解读")
    logger.info("     · 单窗口文章: 内容 ≤ 510 tokens, 无截断风险")
    logger.info("     · 多窗口文章: 需关注窗口数分布, 若 max>10 说明有超长文本")
    logger.info("     · 各模型正/负面占比: 若模型间差异 >15pp, 需在三角验证中重点关注")
    logger.info("")
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
        return

    logger.info(f"正在从 {input_path} 加载数据...")
    df = pd.read_parquet(input_path)
    input_rows = len(df)
    logger.info(f"已加载 {input_rows:,} 行数据。")
    log_memory_usage(logger, "数据加载后")

    # ── Step 1: 一次性加载全部模型到 GPU (FP16) ──
    logger.info("=" * 50)
    logger.info("正在预加载全部模型到 GPU (FP16)...")
    engine = MultiModelSentimentEngine(MODEL_CONFIGS)
    loaded_names = engine.load_all()
    if not loaded_names:
        logger.error("没有模型加载成功，退出阶段")
        return
    log_memory_usage(logger, "全部模型加载后")

    # ── Step 1b: 构建双轨文本列表 ──
    # content_ctx 由阶段 21 预计算并物化为列，直接读取以确保三种方法输入一致
    content_full_list = df['内容'].fillna('').astype(str).tolist()
    content_ctx_list = df['content_ctx'].fillna(df['内容']).astype(str).tolist()

    logger.info(f"双轨文本列表构建完成: full={len(content_full_list)}, ctx={len(content_ctx_list)}")

    # ── Step 2: 双轨批量推理（物理隔离，防止 OOM） ──
    logger.info("=" * 50)
    logger.info("开始多模型双轨批量推理...")

    logger.info("启动 [_ctx] 轨道推理...")
    output_ctx = process_all_models(df, engine, content_ctx_list)

    logger.info("启动 [_full] 轨道推理...")
    output_full = process_all_models(df, engine, content_full_list)

    # ── Step 3: 将双轨结果写回 DataFrame（带后缀） ──
    for out_dict, suffix in [(output_ctx, '_ctx'), (output_full, '_full')]:
        for mc in MODEL_CONFIGS:
            sn = mc['short_name']
            if sn in out_dict:
                for col_name, col_data in out_dict[sn]['columns'].items():
                    df[f"{col_name}{suffix}"] = col_data

    # ── Step 3b: 写入 BERT 窗口数列（双轨，供下游分层分析使用） ──
    _first_sn = next((mc['short_name'] for mc in MODEL_CONFIGS
                      if mc['short_name'] in output_full), None)
    if _first_sn:
        if _first_sn in output_ctx and 'num_windows_list' in output_ctx[_first_sn]:
            df['bert_num_windows_ctx'] = output_ctx[_first_sn]['num_windows_list']
            logger.info(f"  已写入 bert_num_windows_ctx 列 (基于模型: {_first_sn})")
        if _first_sn in output_full and 'num_windows_list' in output_full[_first_sn]:
            df['bert_num_windows_full'] = output_full[_first_sn]['num_windows_list']
            logger.info(f"  已写入 bert_num_windows_full 列 (基于模型: {_first_sn})")

    # ── Step 4: 保存输出 ──
    df.to_parquet(output_path, index=False)
    logger.info(f"已保存输出文件: {output_path} ({len(df):,} 行)")

    # ── Step 5: 释放全部模型 ──
    engine.unload_all()
    log_memory_usage(logger, "模型释放后")

    # ── 打印统计报告（双轨分别打印） ──
    logger.info("=== [_ctx] 轨道统计 ===")
    log_classification_report(output_ctx, len(df))
    logger.info("=== [_full] 轨道统计 ===")
    log_classification_report(output_full, len(df))

    # ── 生成预览 CSV ──
    preview_path = output_path.replace('.parquet', '.csv')
    safe_save_preview_csv(df, preview_path, logger)

    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=input_rows, output_rows=len(df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} (双轨模式) ---")


if __name__ == "__main__":
    main()
