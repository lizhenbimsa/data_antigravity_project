"""
news_process.validation.llms_human — 阶段32：生成人工“金标准”双任务联合验证包

迁移说明 (Phase 7b)：
    本模块由原 root script ``61_news_llms_human.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.llms_human``

========================================================================

功能：
    从 `21_tone_llms.parquet` 或后续处理文件中进行简单随机抽样（默认 500 条），
    生成带有数据校验(Data Validation)的 Excel 文件，包含人类判定真伪（Verification）
    和人类判定情感（Sentiment）的双重联合标注列。
    
输出：
    一站式标注工作台 Excel 文件：`61_human_samples.xlsx`

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 61_news_llms_human.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**职责**: stage 21 LLM 投票结果的人工"金标准"采样器 —— 抽一批文章给人类编码员复核, 产出可直接填写的 Excel 工作台, 是 stage 33/34 效标效度评估的上游。

**输入 (三级回退, 取第一个存在者)**: ① `21_tone_llms_full.parquet` (config.filenames.output_21_tone_llms_full) → ② `23_bert_tone.parquet` (output_23_bert_tone) → ③ `21_tone_llms.parquet` (output_21_tone_llms)。三者皆缺则 logger.error 并 return (不抛异常)。

**处理步骤** (`main()`):
- `load_config()` 读 `human_validation.sample_size` (默认 500) / `random_seed` (默认 42)。
- 简单随机抽样 `df.sample(n=min(SAMPLE_SIZE,len(df)), random_state=RANDOM_SEED)`; 行数 ≤ 目标量则全选 (`df.copy()`)。确定性由固定 seed 保证。
- 追加 4 个空标注列: `编码者A_验证`/`编码者B_验证` (取值 1/0 = 真/伪) + `编码者A_情感`/`编码者B_情感` (正面/中性/负面)。初值均为空字符串 `''`。
- 列重排: 把 4 个标注列 + 关键展示列 (日期/媒体类型(中文)/标题/内容/target_bank/co_mentioned_banks/fintech_keyword_details, 取存在者) 提到最前。
- 用 `xlsxwriter` 写 Excel (sheet 名 `验证数据`), 并经 `set_excel_data_validation()` 对验证列下拉锁定为 {'1','0'}、情感列锁定为 {正面,中性,负面} (动态范围 行2:行10000); 引擎不可用/写盘异常时回退普通 `to_excel`。

**合并函数 `merge_annotations()`** (编码完成后手动调用): 读回填好的 xlsx, 逐行比对两编码者 —— 验证/情感各自: 两人皆有效且一致 → 写共识 `最终_验证`/`最终_情感`; 分歧 → 写哨兵 (`最终_验证`=-1, `最终_情感`='待仲裁'); 另加空 `裁定备注` 列; 输出 `*_merged.xlsx` + 一致率/分歧数/待仲裁数日志。这些哨兵正是 stage 33 评估时要剔除的 attrition。⚠ **该 merge 子命令仅经模块入口可达** —— `python -m news_process.validation.llms_human merge [in.xlsx] [out.xlsx]` (模块 `__main__` 解析 argv[1]=='merge'); 根 shim `61_news_llms_human.py` 的 `__main__` 只调 `main()` 且不透传 argv, 故 `python 61_news_llms_human.py merge` **不会** 触发合并 (只会跑抽样)。

**关键算法/公式**: 无统计计算, 核心是确定性随机抽样 (pandas `df.sample` + 固定 random_state) + Excel 数据校验下拉规则。

**外部依赖**: pandas / numpy / xlsxwriter (写校验下拉) / openpyxl (回退路径与 merge 读 xlsx)。无 LLM/Embedding API 调用, 无 _llm_cache.db, 无网络, $0。

**DAG 位置**: 验证支线 stage 32, 上游 = stage 21 (LLM) / 23 (BERT) 的文章级产出; 下游 = stage 33 (`llms_evaluation.main` 读 32 产出的填好 Excel 算 precision/recall/κ)。shim 仅 `sys.path` 注入后 `from ...llms_human import main; main()`, 零业务逻辑。

■ 白话说明

这一步是"出考卷": 从全部新闻里随机抽 500 篇 (固定随机种子, 每次抽的都一样), 做成一张 Excel 表 (默认文件名 61_human_samples.xlsx) 发给两位人工编码员, 让他们逐篇判断 ①这条新闻是不是真的银行金融科技新闻 ②它的语气是正面/中性/负面。表格里的判断列被锁成下拉菜单, 防止有人手滑填错格式。

为什么需要它: 流水线主要靠 AI 大模型 (LLM) 给每篇新闻打标签, 但我们必须证明"机器打的标签跟人判断的一致", 否则审稿人不信。这张人工答卷就是后面给机器打分用的"标准答案"。编码员填完后, 还有个合并环节把两人的答案对齐 (一致就采纳, 吵架就标"待仲裁")—— 注意这个合并要用模块入口 `python -m news_process.validation.llms_human merge` 触发, 直接跑根脚本带 merge 参数是无效的。

对最终结果的影响: 它本身不直接进银行-年度面板, 也不改任何论文数字。但它的抽样质量决定了 stage 33/34 算出的"机器准确率/κ 一致性"可不可信 —— 抽得有代表性, 验证结论才站得住; 抽偏了 (比如全抽到容易判的), 会高估机器水平。
========================================================================
"""

import os
import platform
import sys
import time

import numpy as np
import pandas as pd

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/llms_human.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import (
    log_memory_usage,
    log_stage_summary,
    pct4,
    setup_logging,
    sig4,
)

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "61_news_llms_human"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 读取配置
HUMAN_VAL_CONFIG = CONFIG.get('human_validation', {})
SAMPLE_SIZE = HUMAN_VAL_CONFIG.get('sample_size', 500)
RANDOM_SEED = HUMAN_VAL_CONFIG.get('random_seed', 42)


def set_excel_data_validation(writer, sheet_name, df, start_row=1):
    """
    为生成的 Excel 文件设置 Data Validation，避免人类标注重格式随意。
    """
    try:
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # 定义验证格式
        validate_verif = {
            'validate': 'list',
            'source': ['1', '0'] # 1=真, 0=伪
        }
        
        validate_senti = {
            'validate': 'list',
            'source': ['正面', '中性', '负面']
        }
        
        # 寻找对应的列索引
        col_names = list(df.columns)
        
        # 获取字母列号 (A, B, C...)
        def get_col_letter(idx):
            res = ""
            while idx >= 0:
                res = chr((idx % 26) + 65) + res
                idx = (idx // 26) - 1
            return res
            
        for name in ['编码者A_验证', '编码者B_验证']:
            if name in col_names:
                idx = col_names.index(name)
                col_letter = get_col_letter(idx)
                # 对整列动态范围 (表头除外) 应用数据校验
                worksheet.data_validation(f'{col_letter}2:{col_letter}10000', validate_verif)
        
        for name in ['编码者A_情感', '编码者B_情感']:
            if name in col_names:
                idx = col_names.index(name)
                col_letter = get_col_letter(idx)
                worksheet.data_validation(f'{col_letter}2:{col_letter}10000', validate_senti)
                
    except Exception as e:
        logger.warning(f"设置 Excel 数据验证失败，但不影响结果生成: {e}")


# ============================================================================
# 盲标双文件协议 (WP-A1, 2026-07-03; 协议=scripts/audit/HUMAN_ANNOTATION_PROTOCOL_2026-07-03.md)
# 盲表 (编码员表, 零机器判定列) 与 reconciliation (对账表, 全列) 分离, 防锚定偏差;
# join 键 = 合成行键 _row_uid (docid 为 文章×银行 粒度非唯一, 仅作展示/溯源列)。
# ============================================================================

#: 盲表允许的上下文列 (白名单): 键/元数据/原文 + target_bank (任务定义所需 —
#: 编码员须知道"目标银行"是谁才能判 T1; 它是实体匹配产物非模型预测, 不构成锚定)
_BLIND_CONTEXT_COLS = ['_row_uid', 'docid', '日期', '媒体类型(中文)', '标题', '内容', 'target_bank']

#: 4 个人工标注列 (A/B 各 2 列; 保留 编码者{A,B}_ 前缀命名 —
#: set_excel_data_validation 按该命名定位下拉, 各盲表天然只命中本编码员两列)
_ANNOTATION_COLS = ['编码者A_验证', '编码者B_验证', '编码者A_情感', '编码者B_情感']


def derive_blind_paths(output_path: str) -> dict:
    """从 config 单键 base (61_human_samples.xlsx) 派生盲标协议四文件路径
    (镜像 merge_annotations 的 `_merged` 派生法, 不新增 config 键)。"""
    base, ext = os.path.splitext(output_path)
    return {
        'blind_A': f"{base}_blind_A{ext}",
        'blind_B': f"{base}_blind_B{ext}",
        'reconciliation': f"{base}_reconciliation{ext}",
        'pending': f"{base}_pending_adjudication{ext}",
    }


def _build_coder_guide(coder: str) -> pd.DataFrame:
    """盲表内嵌编码指南 sheet (WP-E; 摘自协议文档的编码员可见部分)。"""
    rows = [
        ('任务', f'编码者{coder} 独立完成两列: 编码者{coder}_验证 ∈ {{1,0}} — 1=该文确为目标银行'
                 '(target_bank 列) 的金融科技相关新闻, 0=不是; '
                 f'编码者{coder}_情感 ∈ {{正面,中性,负面}} — 基于标题+内容整体语调。'),
        ('判断依据', '阅读"标题"+"内容"全文判断; 客观描述标中性; 标题计入判断但以正文为主。'),
        ('独立性', '禁止与另一位编码员就任何篇目交流; 禁止使用任何 LLM/翻译/摘要工具辅助判定; '
                   '按表内行序标注, 不得自选顺序。'),
        ('边界规则', '混合情感按主导语调、势均力敌标中性; 引用他行负面不传染; 目标银行被处罚/通报=负面, '
                     '银行主动风险提示/合规声明默认中性; 文本异常(乱码/截断)时 验证=0、情感=中性。'),
        ('完整协议', 'scripts/audit/HUMAN_ANNOTATION_PROTOCOL_2026-07-03.md '
                     '(试标资格门 κ≥0.667 / 仲裁规则 / 全部边界先例见该文档)'),
    ]
    return pd.DataFrame(rows, columns=['项目', '说明'])


def _write_blind_workbook(sample_df: pd.DataFrame, coder: str, out_path: str) -> pd.DataFrame:
    """写单编码员盲表: 本编码员 2 标注列前置 + 白名单上下文列, 零机器判定列。"""
    ann_cols = [f'编码者{coder}_验证', f'编码者{coder}_情感']
    cols = [c for c in ann_cols + _BLIND_CONTEXT_COLS if c in sample_df.columns]
    blind_df = sample_df[cols].copy()
    try:
        with pd.ExcelWriter(out_path, engine='xlsxwriter') as writer:
            blind_df.to_excel(writer, sheet_name='验证数据', index=False)
            set_excel_data_validation(writer, '验证数据', blind_df)
            _build_coder_guide(coder).to_excel(writer, sheet_name='编码指南', index=False)
    except Exception as e:
        logger.warning(f"写入盲表 {out_path} (xlsxwriter) 失败 ({e}), 回退普通写入")
        blind_df.to_excel(out_path, index=False)
    return blind_df


def _write_reconciliation(sample_df: pd.DataFrame, out_path: str) -> None:
    """写对账表: 全部机器/上下文列 + _row_uid, 剔除人工标注列; 共识冻结后才解锁对账, 不发编码员。"""
    recon_df = sample_df.drop(
        columns=[c for c in _ANNOTATION_COLS if c in sample_df.columns])
    recon_df.to_excel(out_path, sheet_name='验证数据', index=False)


def main():
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39c)。
    logger.info("=" * 72)
    logger.info("阶段 61: LLM×人工金标准采样器 (人工抽样验证样本生成; criterion validity 上游)")
    logger.info("=" * 72)
    logger.info(f"【功能】从全部新闻里随机抽一批文章 (本次 SAMPLE_SIZE={SAMPLE_SIZE} 篇, 受 config 控制), 做成可直接")
    logger.info("        填写的 Excel 标注工作台 (sheet=验证数据), 发给两位人工编码员逐篇判定")
    logger.info("        ①是否真银行金科新闻 (验证 1/0) ②语气 (正面/中性/负面)。")
    logger.info("        产出 = 人工'标准答案'考卷, 是 stage 33/34 评 LLM 精度/κ 的上游 (本阶段不进面板)。")
    logger.info(
        f"【方法】简单随机抽样 df.sample(n=min({SAMPLE_SIZE},N), random_state={RANDOM_SEED}); "
        "固定种子保证逐位可复现。"
    )
    logger.info("        追加 4 空标注列 + 关键展示列提到最前; xlsxwriter 写下拉数据校验 (验证锁{1,0}/")
    logger.info("        情感锁{正面,中性,负面}), 引擎不可用时回退普通 to_excel。无统计计算。")
    logger.info("【判读】抽样代表性是 stage 33/34 结论可信度的前提: 抽偏 (全抽易判篇) 会高估机器水平;")
    logger.info("        抽样率应≈目标量/总量, 全选 (N≤目标量) 时下游金标准覆盖度受限须披露。")
    logger.info("【确定性】纯 CPU, 无 LLM/Embedding/网络调用, $0; 固定 random_state → 逐位可复现。")

    # 🧭 项目 / 环境信息 + ⚙ 运行配置 + 📖 方法论依据 (日志富集 2026-06-24, 纯日志 golden-safe)
    # crash-guard: 整块 try/except 包住, 日志渲染异常绝不冒泡崩阶段 (铁律: 日志块不得让阶段挂)。
    try:
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info("  🧭 项目 / 环境信息")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板); 版本 v3.15.0")
        logger.info(f"     · 阶段: {STAGE_NAME} (人工金标准采样器, 验证支线 stage 61; criterion validity 上游)")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段纯 CPU / 无 LLM·网络·API ($0) / 固定 random_state → 逐位可复现")

        logger.info("  ⚙ 运行配置 (config::human_validation)")
        logger.info(f"     · 目标抽样量 SAMPLE_SIZE={SAMPLE_SIZE:,} | 随机种子 RANDOM_SEED={RANDOM_SEED}")
        logger.info("     · 抽样法: 简单随机抽样 df.sample(n=min(SAMPLE_SIZE,N), random_state=RANDOM_SEED)")
        logger.info("     · 标注列: 编码者A/B_验证 (锁下拉 {1,0}) + 编码者A/B_情感 (锁下拉 {正面,中性,负面})")
        logger.info("     · 写盘引擎: xlsxwriter (带数据校验下拉) → 失败回退普通 to_excel")

        logger.info("  📖 方法论依据 (人工金标准 / 双编码者一致性 / LLM-vs-人工效标效度)")
        logger.info("     · LLM 标注 vs 人工编码 (效标效度): Gilardi, F., Alizadeh, M., & Kubli, M. (2023). "
                    "ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National "
                    "Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120")
        logger.info("       → 本阶段抽样产'人工标准答案', 用于 stage 33/34 检验 LLM 投票与人工判定是否一致。")
        logger.info("     · 多编码者三角验证: Denzin, N. K. (2017). The research act: A theoretical introduction "
                    "to sociological methods. Routledge. https://doi.org/10.4324/9781315134543")
        logger.info("       → 两位独立编码员交叉复核 (一致采纳 / 分歧标'待仲裁') = 调查者三角化以提升测度可信度。")
        logger.info("     · LLM 标注的方法学纪律 (误分类偏置 / prompt 敏感性 / 可复现性): Carlson, N. A., & "
                    "Burbano, V. (2026). The use of LLMs to annotate data in management research: "
                    "Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. "
                    "https://doi.org/10.1002/smj.70023")
        logger.info("       → 凡用 LLM 给文本贴标签均须以人工金标准校准误分类偏置, 正是本阶段抽样产'标准答案'的动因。")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法论信息打印失败 (不影响结果生成): {_e}")

    # 优先使用全量 LLM 结果
    input_filename = CONFIG.get('filenames', {}).get('output_21_tone_llms_full', '21_tone_llms_full.parquet')
    input_path = os.path.join(CONFIG["paths"]["output_dir"], input_filename)
    
    # 退回到已过滤版本
    if not os.path.exists(input_path):
        input_filename = CONFIG.get('filenames', {}).get('output_23_bert_tone', '23_bert_tone.parquet')
        input_path = os.path.join(CONFIG["paths"]["output_dir"], input_filename)
    
    # 再退回到 tone_llms
    if not os.path.exists(input_path):
        input_filename = CONFIG.get('filenames', {}).get('output_21_tone_llms', '21_tone_llms.parquet')
        input_path = os.path.join(CONFIG["paths"]["output_dir"], input_filename)
        
    if not os.path.exists(input_path):
        logger.error(f"无法找到可作为抽样源的 parquet 文件: {input_path}")
        return
        
    logger.info(f"加载数据以供抽样: {input_path}")
    df = pd.read_parquet(input_path)
    logger.info(f"总数据量: {len(df)}")
    log_memory_usage(logger, "数据加载后")
    
    # 抽样
    target_sample_size = min(SAMPLE_SIZE, len(df))
    logger.info(f"计划抽样数量: {target_sample_size} (基于随机种子 {RANDOM_SEED})")
    
    if len(df) <= target_sample_size:
        sample_df = df.copy()
        logger.info("数据量少于或等于目标抽样量，直接全选。")
    else:
        # 全样本简单随机抽样
        logger.info("执行简单随机抽样")
        sample_df = df.sample(n=target_sample_size, random_state=RANDOM_SEED)

    # 追加人工标注“一站式”作业台的四列
    # 新规定：用 1/0 代表真假，直接用中文表示情感
    col_names = list(_ANNOTATION_COLS)
    sample_df = sample_df.copy()
    # WP-A1: 抽样后一次 shuffle (镜像 manual_validation_sampling.py 防层界锚定;
    # A/B 盲表与对账表共用同一行序) + 铸造合成行键 _row_uid (R4 实证 docid 为
    # 文章×银行 粒度非唯一 1331u/1544 → 全部 join/断言用 _row_uid, docid 仅展示)。
    sample_df = sample_df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    sample_df['_row_uid'] = range(len(sample_df))
    for col in col_names:
        sample_df[col] = ''
    
    # 重排列表将验证列放在标题与内容之前，让标注者第一眼就能填
    desired_front = col_names + ['_row_uid', 'docid', '日期', '媒体类型(中文)', '标题', '内容', 'target_bank', 'co_mentioned_banks', 'fintech_keyword_details']
    front_cols = [c for c in desired_front if c in sample_df.columns]
    other_cols = [c for c in sample_df.columns if c not in front_cols]
    sample_df = sample_df[front_cols + other_cols]
    
    # 导出
    output_filename = CONFIG.get('filenames', {}).get('output_32_human_sample', '61_human_samples.xlsx')
    output_path = os.path.join(CONFIG["paths"]["output_dir"], output_filename)
        
    # WP-A1 盲标双文件协议: 不再产出旧单文件工作台 (机器列+人工列同帧 = 反盲标);
    # 产物 = 盲表A + 盲表B (零机器列, per-coder 独立副本) + reconciliation (全列对账)。
    blind_paths = derive_blind_paths(output_path)
    logger.info(f"正在保存盲标双文件协议产物 (base = {output_path}):")
    for coder in ('A', 'B'):
        bp = blind_paths[f'blind_{coder}']
        _write_blind_workbook(sample_df, coder, bp)
        logger.info(f"  盲表{coder} = {bp} (仅键/元数据/原文/target_bank + 编码者{coder} 两标注列, 已锁下拉)")
    _write_reconciliation(sample_df, blind_paths['reconciliation'])
    logger.info(f"  对账表 = {blind_paths['reconciliation']} (全部机器列, 共识冻结后解锁, 不发编码员)")
    if os.path.exists(output_path):
        logger.warning(
            f"  ⚠ 检测到旧版单文件工作台 {output_path} (含机器判定列, 反盲标) — "
            "已弃用, 绝不可发编码员; 确认无已填标注后可手动删除。")

    # 结果分析 — 写入日志: 抽样源/抽样率/标注列就绪情况 + 判读 (仿 39c)。
    # crash-guard: 本块仅"读数据算计数+打日志", 不写盘/不改产物 (Excel 已于上方落盘);
    # 但仍整体包 try/except, 防未来取数异常 (如缺列/空 Series) 冒泡崩掉阶段、误伤 golden-safe 性质。
    try:
        n_total = len(df)
        n_sample = len(sample_df)
        sample_frac = (n_sample / n_total * 100) if n_total > 0 else 0.0
        full_select = n_total <= target_sample_size  # 全选 (未真正抽样) 标记
        # 展示列就绪度: desired_front 里真正落入 Excel 的关键列 (供编码员判读用)
        display_present = [c for c in front_cols if c not in col_names]
        n_display = len(display_present)
        n_display_expected = 9  # _row_uid/docid/日期/媒体类型(中文)/标题/内容/target_bank/co_mentioned_banks/fintech_keyword_details

        logger.info("-" * 72)
        logger.info("【结果分析】人工金标准考卷已生成 (抽样代表性 → 下游 stage 33/34 结论可信度):")
        logger.info(
            f"  抽样源 = {input_filename} (三级回退取第一存在者: 21_full → 23_bert → 21_tone_llms)"
        )
        # 📥 IO provenance (此前仅记行数, 无 schema 宽度 / 工作台维度): 输入 parquet 全宽列数 +
        # 抽样工作台 (含 +4 空标注列) 最终维度, 让 .log 自证"抽样前后的数据形状"。整数 :,d 无须 sig4。
        logger.info(
            f"  源 schema = {n_total:,} 行 × {df.shape[1]:,} 列 (parquet 全宽); "
            f"输出工作台 = {n_sample:,} 行 × {sample_df.shape[1]:,} 列 (Excel, 已并入 4 空标注列 + 关键展示列前置)"
        )
        logger.info(
            f"  总语料 N = {n_total:,} 篇; 目标抽样量 = {target_sample_size} (config SAMPLE_SIZE={SAMPLE_SIZE})"
        )
        if n_total == 0:
            # NaN/空数据 guard: 空语料时不落进抽样率方向判读 (否则除零/恒为 0 误判)
            logger.warning("  ⚠ 总语料 N=0 (无有效数据): 无样本可抽, 跳过抽样率判读; 请检查抽样源是否为空。")
        elif full_select:
            logger.warning(
                f"  ⚠ 全选: N({n_total:,}) ≤ 目标量({target_sample_size}), 未真正随机抽样 → "
                "抽样率=100%; 盘面 T=2 小语料下属预期, 全量 17M 不会触发。"
            )
        else:
            logger.info(
                f"  实际抽样 = {n_sample:,} 篇, 抽样率 = {pct4(sample_frac, fraction=False)} "
                f"(简单随机, random_state={RANDOM_SEED}, 逐位可复现)"
            )
            # 仅作记录: 抽样率 = 实际抽样量/总量, 由 .sample(n=target) 构造保证抽样量恒等于目标量
            # (故抽样率与目标占比恒相等, 非代表性检验)。⚠ 本行不下'无偏'结论 —— 抽样量等于请求量
            # 是构造性事实, 并未检验样本在银行/年份/媒体维度上是否代表总体; 代表性须 stage 33/34 实测。
            logger.info(
                "    判读: 抽样量=配置目标量 (由 df.sample(n=) 构造保证); "
                "此处仅记录抽样规模, 维度代表性 (银行/年份/媒体) 不在本阶段检验。"
            )
        logger.info(
            f"  标注列 = {len(col_names)}/4 就绪 ({', '.join(col_names)}, 初值空待人工回填)"
        )
        if n_display < n_display_expected:
            logger.warning(
                f"  ⚠ 展示列 {n_display}/{n_display_expected} 就绪 (实有: {display_present}); "
                "缺列会降低编码员判读上下文, 但不影响抽样确定性。"
            )
        else:
            logger.info(
                f"  展示列 {n_display}/{n_display_expected} 就绪 ({display_present}) → 编码员上下文充分。"
            )
        logger.info(
            f"  产出 = 盲表A/B + 对账表 (base={output_path}; sheet=验证数据, 标注列已锁下拉; "
            "join 键=_row_uid; 不进面板, golden 无关)")
        logger.info(
            "  ⚠ 本阶段只产'考卷'不算指标: 精度/κ 在 stage 33 评; 抽样若偏 (全抽易判篇) 会高估机器水平。"
        )
        if n_sample < 50:
            logger.warning(
                f"  ⚠ 样本仅 {n_sample} 篇 (盘面 T=2 小样本): 仅验证管道正确性, "
                "criterion validity 结论以全量 17M/T=18 实测为准。"
            )
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    # 抽样代表性 sanity 自检 (log-only, golden-safe) — 在抽到的 sample_df 上看
    # 媒体类型/年份 的边际分布, 实证上文已披露的"抽偏 (全抽易判篇/单一来源) 会高估机器水平"
    # 识别威胁 (substantiate-at-runtime)。⚠ 仅边际分布诊断, **非**正式代表性检验: 样本对总体
    # 在银行/年份/媒体维度的代表性仍由 stage 33/34 实测; 本块全部计算只喂 logger 即抛弃,
    # 绝不回流下游 (铁律: log-only, 单独 try/except 包住, 异常绝不冒泡崩阶段)。
    try:
        logger.info("-" * 72)
        logger.info("【抽样代表性自检 (诊断, 非正式检验; 代表性正式判定见 stage 33/34)】")
        n_drawn = len(sample_df)
        # (a) 媒体类型(中文) top-k 份额: 单一媒体占比过高 → 抽样向某来源倾斜 (against 代表性)
        media_col = '媒体类型(中文)'
        if media_col in sample_df.columns:
            vc_media = sample_df[media_col].value_counts(dropna=True)
            n_outlet = int(vc_media.shape[0])
            n_media_valid = int(vc_media.sum())
            if n_media_valid > 0:
                topk = vc_media.head(5)
                shares = ", ".join(
                    f"{name}={pct4(cnt / n_media_valid * 100, fraction=False)}"
                    for name, cnt in topk.items()
                )
                logger.info(
                    f"  媒体类型覆盖 = {n_outlet:,} 类 (有效 {n_media_valid:,} 篇); "
                    f"top-{len(topk)} 份额: {shares}"
                )
                top1_share = vc_media.iloc[0] / n_media_valid * 100
                if top1_share > 50:
                    logger.warning(
                        f"  ⚠ 最大媒体单类占比 {pct4(top1_share, fraction=False)} (>50%): "
                        "抽样向单一来源倾斜, 须在 stage 33/34 代表性检验中如实披露。"
                    )
            else:
                logger.info(f"  ({media_col} 列全缺失, 跳过媒体类型代表性自检)")
        else:
            logger.info(f"  (无 {media_col} 列, 跳过媒体类型代表性自检)")
        # (b) 年份覆盖/跨度: 优先 year 数值列, 退回 日期 派生; 抽样若塌缩到单一年度 → T 维不代表性
        year_series = None
        if 'year' in sample_df.columns:
            year_series = pd.to_numeric(sample_df['year'], errors='coerce').dropna()
        elif '日期' in sample_df.columns:
            year_series = pd.to_datetime(sample_df['日期'], errors='coerce').dt.year.dropna()
        if year_series is not None and len(year_series) > 0:
            y_min, y_max = int(year_series.min()), int(year_series.max())
            n_years = int(year_series.nunique())
            logger.info(
                f"  年份覆盖 = {n_years:,} 个年度 (跨度 {y_min}–{y_max}); "
                f"年份可解析 {len(year_series):,}/{n_drawn:,} 篇"
            )
            if n_years <= 1:
                logger.warning(
                    "  ⚠ 抽样仅覆盖 ≤1 个年度: 盘面 T=2 小样本下属预期, "
                    "全量 17M/T=18 须确认逐年覆盖均衡 (代表性以 stage 33/34 为准)。"
                )
        else:
            logger.info("  (无 year/日期 可派生年份, 跳过年份覆盖代表性自检)")
        logger.info("  判读: 上述仅边际分布诊断, 正式代表性 (银行/年份/媒体对总体) 仍是 stage 33 之责。")
        logger.info("-" * 72)
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"[抽样代表性自检] 诊断计算异常, 跳过(不影响产物): {_e}")

    log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(sample_df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


# ============================================================================
# 3. 人工标注合并（编码完成后使用）
# ============================================================================

def merge_annotations(input_path: str = None, output_path: str = None,
                      with_adjudication: bool = False):
    """合并两位编码者的人工判定，生成黄金标准列。

    合并规则：
      - 一致：取共识值写入 ``最终_验证`` / ``最终_情感``
      - 分歧：标记为 ``待仲裁``（验证列写 -1，情感列写 "待仲裁"）

    同时生成合并统计摘要（一致率、分歧条目数），供研究者参考。

    Args:
        input_path:  已标注的 Excel 文件路径。默认自动从配置读取。
        output_path: 合并后的输出文件路径。默认在同目录生成 ``_merged`` 后缀文件。
    """
    merge_start = time.time()
    logger.info("--- 开始人工标注合并 ---")

    # 📖 子步骤 banner: 双编码者一致性合并 = 调查者三角化 (日志富集 2026-06-24, 纯日志 golden-safe)
    try:
        logger.info("  步骤: 双编码者人工判定合并 (一致采纳共识 / 分歧标'待仲裁'剔除)")
        logger.info("     方法依据: Denzin, N. K. (2017). The research act: A theoretical introduction "
                    "to sociological methods. Routledge. https://doi.org/10.4324/9781315134543")
        logger.info("     判读: 一致率越高 → 标注任务越客观、金标准越可信; 待仲裁条目正是 stage 33 须剔除的 attrition。")
        logger.info("     编码者间信度 (多类别 / 层级一致性): Moons, F., & Vandervieren, E. (2025). Measuring "
                    "agreement among several raters classifying subjects into one or more (hierarchical) "
                    "categories: A generalization of Fleiss' kappa. Behavior Research Methods, 57(10), "
                    "Article 287. https://doi.org/10.3758/s13428-025-02746-8")
        logger.info("       → 情感三分类 (正面/中性/负面) 的双编码者一致正是 Fleiss κ 家族度量对象; 本步算一致率, κ 在 stage 33/34。")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  合并方法论 banner 打印失败 (不影响合并): {_e}")

    # 解析路径
    if input_path is None:
        input_filename = CONFIG.get('filenames', {}).get(
            'output_32_human_sample', '61_human_samples.xlsx'
        )
        input_path = os.path.join(CONFIG["paths"]["output_dir"], input_filename)

    # WP-A1: base 单文件与双盲表任一存在即可继续 (盲标协议下 base 本体不再产出,
    # 存在性判定须覆盖派生盲表, 否则新协议恒被此处提前拦截)
    _bp_probe = derive_blind_paths(input_path)
    if not (os.path.exists(input_path)
            or (os.path.exists(_bp_probe['blind_A']) and os.path.exists(_bp_probe['blind_B']))):
        logger.error(f"标注文件未找到 (单文件与双盲表均缺): {input_path}")
        return

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_merged{ext}"

    # 读取已标注数据 — WP-A1 盲标协议: 优先双盲表 (blind_A + blind_B, 按 _row_uid 合并);
    # 旧单文件路径保留为 fallback (loud WARNING, 兼容历史工作台)。
    blind_paths = derive_blind_paths(input_path)
    ba_path, bb_path = blind_paths['blind_A'], blind_paths['blind_B']
    if os.path.exists(ba_path) and os.path.exists(bb_path):
        logger.info(f"读取双盲表标注: {ba_path} + {bb_path}")
        try:
            with pd.ExcelFile(ba_path) as xa:
                df_a = pd.read_excel(xa, sheet_name='验证数据')
            with pd.ExcelFile(bb_path) as xb:
                df_b = pd.read_excel(xb, sheet_name='验证数据')
        except Exception as e:
            logger.error(f"读取盲表失败: {e}")
            return
        # fail-loud 键断言: 行数 + _row_uid 集合双侧一致 (docid 非唯一, 禁作键)
        if '_row_uid' not in df_a.columns or '_row_uid' not in df_b.columns:
            logger.error("盲表缺 _row_uid 键列 — 请用新版生成端重生盲表")
            return
        if len(df_a) != len(df_b) or set(df_a['_row_uid']) != set(df_b['_row_uid']):
            logger.error(
                f"双盲表 _row_uid 不一致 (A={len(df_a)} 行 / B={len(df_b)} 行) — "
                "行被增删或来自不同批次, 拒绝合并")
            return
        b_cols = ['_row_uid'] + [c for c in ('编码者B_验证', '编码者B_情感') if c in df_b.columns]
        df = df_a.merge(df_b[b_cols], on='_row_uid', how='inner', validate='one_to_one')
        if len(df) != len(df_a):
            logger.error(f"盲表合并后行数漂移 ({len(df_a)}→{len(df)}), 拒绝继续")
            return
    else:
        logger.warning(
            f"⚠ 未找到双盲表 ({ba_path}), 回退旧版单文件路径 {input_path} — "
            "单文件工作台机器列与人工列同帧 (反盲标), 仅供历史数据兼容")
        try:
            # fix(2026-06-19 run-check F5 兄弟泄漏): with 上下文确保 ExcelFile 句柄关闭 (消除 ResourceWarning)
            with pd.ExcelFile(input_path) as xl:
                sheet_name = '验证数据' if '验证数据' in xl.sheet_names else xl.sheet_names[0]
                df = pd.read_excel(xl, sheet_name=sheet_name)
        except Exception as e:
            logger.error(f"读取标注文件失败: {e}")
            return

    logger.info(f"共 {len(df)} 条标注记录")

    # --- 合并验证判定 ---
    ver_a_col, ver_b_col = '编码者A_验证', '编码者B_验证'
    final_ver_col = '最终_验证'

    if ver_a_col in df.columns and ver_b_col in df.columns:
        df[ver_a_col] = pd.to_numeric(df[ver_a_col], errors='coerce')
        df[ver_b_col] = pd.to_numeric(df[ver_b_col], errors='coerce')

        both_valid = df[ver_a_col].notna() & df[ver_b_col].notna()
        agree_mask = both_valid & (df[ver_a_col] == df[ver_b_col])
        disagree_mask = both_valid & (df[ver_a_col] != df[ver_b_col])

        df[final_ver_col] = np.nan
        df.loc[agree_mask, final_ver_col] = df.loc[agree_mask, ver_a_col]
        df.loc[disagree_mask, final_ver_col] = -1  # 待仲裁标记

        n_agree_ver = int(agree_mask.sum())
        n_disagree_ver = int(disagree_mask.sum())
        n_total_ver = int(both_valid.sum())
        agree_rate_ver = n_agree_ver / n_total_ver * 100 if n_total_ver > 0 else 0

        logger.info(f"[验证] 合并完成: 一致={n_agree_ver:,}, 分歧={n_disagree_ver:,}, "
                     f"一致率={pct4(agree_rate_ver, fraction=False)}")
        # log-only: 有效双标注覆盖率 = 两位编码者均给出有效验证判定的占比 (缺失/未填越多覆盖率越低)
        cover_ver = (n_total_ver / len(df) * 100) if len(df) > 0 else 0.0
        logger.info(f"[验证] 有效双标注覆盖率 = {pct4(cover_ver, fraction=False)} "
                     f"({n_total_ver:,}/{len(df):,} 条两位编码者均有效); 覆盖率偏低须披露 attrition 来源。")
    else:
        logger.warning(f"未找到验证判定列（{ver_a_col}, {ver_b_col}），跳过验证合并")

    # --- 合并情感判定 ---
    sen_a_col, sen_b_col = '编码者A_情感', '编码者B_情感'
    final_sen_col = '最终_情感'

    if sen_a_col in df.columns and sen_b_col in df.columns:
        df[sen_a_col] = df[sen_a_col].astype(str).str.strip()
        df[sen_b_col] = df[sen_b_col].astype(str).str.strip()

        # 将空字符串和 'nan' 视为缺失
        for col in [sen_a_col, sen_b_col]:
            df.loc[df[col].isin(['', 'nan', 'None']), col] = np.nan

        both_valid_sen = df[sen_a_col].notna() & df[sen_b_col].notna()
        agree_mask_sen = both_valid_sen & (df[sen_a_col] == df[sen_b_col])
        disagree_mask_sen = both_valid_sen & (df[sen_a_col] != df[sen_b_col])

        df[final_sen_col] = pd.array([pd.NA] * len(df), dtype='object')
        df.loc[agree_mask_sen, final_sen_col] = df.loc[agree_mask_sen, sen_a_col]
        df.loc[disagree_mask_sen, final_sen_col] = '待仲裁'

        n_agree_sen = int(agree_mask_sen.sum())
        n_disagree_sen = int(disagree_mask_sen.sum())
        n_total_sen = int(both_valid_sen.sum())
        agree_rate_sen = n_agree_sen / n_total_sen * 100 if n_total_sen > 0 else 0

        logger.info(f"[情感] 合并完成: 一致={n_agree_sen:,}, 分歧={n_disagree_sen:,}, "
                     f"一致率={pct4(agree_rate_sen, fraction=False)}")
        # log-only: 有效双标注覆盖率 = 两位编码者均给出有效情感判定 (非空/非 nan) 的占比
        cover_sen = (n_total_sen / len(df) * 100) if len(df) > 0 else 0.0
        logger.info(f"[情感] 有效双标注覆盖率 = {pct4(cover_sen, fraction=False)} "
                     f"({n_total_sen:,}/{len(df):,} 条两位编码者均有效); 三分类一致率随类别基率漂移须谨慎解读。")
    else:
        logger.warning(f"未找到情感判定列（{sen_a_col}, {sen_b_col}），跳过情感合并")

    # --- WP-C 仲裁工作流 (双口径, 2026-07-03) ---
    # strict 口径 = 剔除分歧 (原行为) 永远保留为 *_strict 列; 主口径 最终_* 在
    # --with-adjudication 且第三编码员 C 已填时被 C 裁决覆盖 (A=B→共识;
    # A≠B∧C 有值→C; A≠B∧C 空→保持哨兵 -1/'待仲裁' = 下限回退, stage 63 语义不变)。
    if final_ver_col in df.columns:
        df['最终_验证_strict'] = df[final_ver_col]
    if final_sen_col in df.columns:
        df['最终_情感_strict'] = df[final_sen_col]

    pending_path = derive_blind_paths(input_path)['pending']
    if with_adjudication:
        if not os.path.exists(pending_path):
            logger.warning(f"--with-adjudication 指定但仲裁工作台不存在: {pending_path}, 跳过仲裁")
        elif '_row_uid' not in df.columns:
            logger.warning("--with-adjudication 需要 _row_uid 键 (旧版单文件工作台不支持仲裁), 跳过")
        else:
            adj = pd.read_excel(pending_path, sheet_name=0)
            n_adj_ver = n_adj_sen = 0
            if '_row_uid' in adj.columns:
                if final_ver_col in df.columns and '编码者C_验证' in adj.columns:
                    c_ver = pd.to_numeric(adj['编码者C_验证'], errors='coerce')
                    ver_map = dict(zip(adj['_row_uid'], c_ver))
                    mapped = df['_row_uid'].map(ver_map)
                    m = df[final_ver_col].eq(-1).fillna(False) & mapped.isin([0, 1])
                    df.loc[m, final_ver_col] = mapped[m]
                    n_adj_ver = int(m.sum())
                if final_sen_col in df.columns and '编码者C_情感' in adj.columns:
                    c_sen = adj['编码者C_情感'].astype(str).str.strip()
                    sen_map = dict(zip(adj['_row_uid'], c_sen))
                    mapped = df['_row_uid'].map(sen_map)
                    m = df[final_sen_col].eq('待仲裁').fillna(False) & mapped.isin(['正面', '中性', '负面'])
                    df.loc[m, final_sen_col] = mapped[m]
                    n_adj_sen = int(m.sum())
                logger.info(f"[仲裁] C 裁决已并入主口径: 验证 {n_adj_ver} 条 / 情感 {n_adj_sen} 条 "
                            "(strict 剔除口径保留于 最终_*_strict 供并排报告)")
            else:
                logger.warning(f"仲裁工作台缺 _row_uid 列, 跳过仲裁: {pending_path}")

    # 剩余未决分歧 → 仲裁工作台 (仅键/文本/A-B 判定, 不含机器列; 编码员 C 填 编码者C_* 两列)
    dis_mask = pd.Series(False, index=df.index)
    if final_ver_col in df.columns:
        dis_mask |= df[final_ver_col].eq(-1).fillna(False)
    if final_sen_col in df.columns:
        dis_mask |= df[final_sen_col].eq('待仲裁').fillna(False)
    if int(dis_mask.sum()) > 0:
        _skip_pending = False
        if os.path.exists(pending_path):
            try:
                old_adj = pd.read_excel(pending_path, sheet_name=0)
                for c in ('编码者C_验证', '编码者C_情感'):
                    if c in old_adj.columns and old_adj[c].notna().any():
                        logger.warning(
                            f"⚠ 既有仲裁工作台已含 C 判定 ({pending_path}), 拒绝覆盖 — "
                            "先跑 --with-adjudication 并入后再重生")
                        _skip_pending = True
                        break
            except Exception as e:
                logger.warning(f"读取既有仲裁工作台失败 ({e}), 为安全起见不覆盖: {pending_path}")
                _skip_pending = True
        if not _skip_pending:
            pend_cols = [c for c in ('_row_uid', 'docid', '标题', '内容',
                                     ver_a_col, ver_b_col, sen_a_col, sen_b_col)
                         if c in df.columns]
            pending_df = df.loc[dis_mask, pend_cols].copy()
            pending_df['编码者C_验证'] = ''
            pending_df['编码者C_情感'] = ''
            try:
                with pd.ExcelWriter(pending_path, engine='xlsxwriter') as writer:
                    pending_df.to_excel(writer, sheet_name='验证数据', index=False)
                    # C 列下拉直接按列号施加 (勿走 set_excel_data_validation 的
                    # 编码者A/B 命名定位 — 表内已有同名 A/B 原判定列, 会命中错列)
                    ws = writer.sheets['验证数据']
                    cols = list(pending_df.columns)
                    civ = cols.index('编码者C_验证')
                    cis = cols.index('编码者C_情感')
                    n = len(pending_df)
                    ws.data_validation(1, civ, n, civ, {'validate': 'list', 'source': ['1', '0']})
                    ws.data_validation(1, cis, n, cis, {'validate': 'list', 'source': ['正面', '中性', '负面']})
            except Exception:
                pending_df.to_excel(pending_path, index=False)
            logger.info(f"[仲裁] 待仲裁工作台已生成: {pending_path} ({len(pending_df)} 行, "
                        "仲裁人不见机器列; 填毕后 merge --with-adjudication 二次合并)")

    # --- 添加裁定备注列（如不存在） ---
    if '裁定备注' not in df.columns:
        df['裁定备注'] = ''

    # --- 输出 ---
    try:
        df.to_excel(output_path, index=False)
        logger.info(f"合并结果已保存: {output_path}")
    except Exception as e:
        logger.error(f"保存合并结果失败: {e}")
        return

    # 统计摘要
    logger.info("--- 合并统计摘要 ---")
    if final_ver_col in df.columns:
        pending_ver = int((df[final_ver_col] == -1).sum())
        logger.info(f"  验证: 待仲裁 {pending_ver:,} 条 (stage 33 须剔除的 attrition)")
    if final_sen_col in df.columns:
        pending_sen = int((df[final_sen_col] == '待仲裁').sum())
        logger.info(f"  情感: 待仲裁 {pending_sen:,} 条 (stage 33 须剔除的 attrition)")

    elapsed = time.time() - merge_start
    logger.info(f"--- 标注合并完毕 (耗时 {sig4(elapsed)}s) ---")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'merge':
        # 用法: python 61_news_llms_human.py merge [input.xlsx] [output.xlsx] [--with-adjudication]
        args = [a for a in sys.argv[2:] if a != '--with-adjudication']
        adj = '--with-adjudication' in sys.argv[2:]
        inp = args[0] if len(args) > 0 else None
        out = args[1] if len(args) > 1 else None
        merge_annotations(inp, out, with_adjudication=adj)
    else:
        main()
