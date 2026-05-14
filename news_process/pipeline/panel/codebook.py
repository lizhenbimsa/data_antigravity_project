"""news_process.pipeline.panel.codebook — 变量代码手册自动生成模块

功能：
1. 自动生成完整的变量代码手册（Variable Codebook）
2. 包含变量名、标签、注释、数据类型、取值范围、计算公式等完整属性
3. 支持导出为 Excel、CSV、Markdown、JSON 等多种格式
4. 自动从面板数据中提取变量统计信息

v7 schema 升级 (2026-05-14):
    prompt v7 把 text_type → innovation_substantiveness (W&Z 1994/1998 ASQ
    substantive-vs-symbolic 框架); fintech_category → innovation_locus (Gomber
    et al. 2018 JMIS enabling-technology vs business-function 框架)。

    panel 层为保持 v6 列名兼容 (Stata + papers/ 模块 + golden baseline),
    采用 tone_llms.py 内联翻译层: LLM 输出 '象征性' 在落 parquet 前映射为 '描述性'。
    因此变量名后缀 _desc/_sub/_tech/_app 在 v7 起的语义解读如下:

      _desc -> 象征性 (symbolic)   ← Westphal & Zajac 1994 ASQ symbolic management
      _sub  -> 实质性 (substantive)
      _tech -> 底层技术 (enabling technology, Gomber 2018)
      _app  -> 应用场景 (business function, Gomber 2018)

    论文 replication 包中所有 _desc 命名变量应按 W&Z (1994) symbolic 解释。
    详见 docs/methodology/prompt_terminology_mapping.md。

作者: Claude Opus 4.7
日期: 2026-05-10 (v6) / 2026-05-14 (v7 schema upgrade)
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List

import pandas as pd

from news_process.core.config import load_config

# 初始化配置和日志
CONFIG = load_config()
logger = logging.getLogger(__name__)


# ============================================================================
# 1. 变量元数据定义（Variable Metadata Schema）
# ============================================================================

class VariableMetadata:
    """变量元数据类，包含变量的完整属性"""

    def __init__(
        self,
        var_name: str,
        label: str,
        description: str = "",
        data_type: str = "",
        unit: str = "",
        value_range: str = "",
        formula: str = "",
        source_stage: str = "",
        reference: str = "",
        notes: str = "",
        category: str = "",
        track: str = "",
    ):
        """初始化变量元数据

        Args:
            var_name: 变量名
            label: 变量标签（简短描述）
            description: 详细描述/注释
            data_type: 数据类型（float, int, str, bool等）
            unit: 单位（如：元、%、分等）
            value_range: 取值范围（如：[0, 1]、[-1, 1]等）
            formula: 计算公式
            source_stage: 来源阶段（如：Stage 21, Stage 46等）
            reference: 学术文献引用
            notes: 额外说明
            category: 变量类别（如：情感指标、网络指标等）
            track: 文本轨道（full/ctx/title）
        """
        self.var_name = var_name
        self.label = label
        self.description = description
        self.data_type = data_type
        self.unit = unit
        self.value_range = value_range
        self.formula = formula
        self.source_stage = source_stage
        self.reference = reference
        self.notes = notes
        self.category = category
        self.track = track

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {
            '变量名': self.var_name,
            '标签': self.label,
            '描述': self.description,
            '数据类型': self.data_type,
            '单位': self.unit,
            '取值范围': self.value_range,
            '计算公式': self.formula,
            '来源阶段': self.source_stage,
            '学术引用': self.reference,
            '备注': self.notes,
            '变量类别': self.category,
            '文本轨道': self.track,
        }


# ============================================================================
# 2. 变量元数据字典（完整版）
# ============================================================================

def get_variable_metadata_dict() -> Dict[str, VariableMetadata]:
    """获取完整的变量元数据字典

    包含所有变量的详细属性：
    - 变量名、标签、描述
    - 数据类型、单位、取值范围
    - 计算公式、来源阶段、学术引用
    """
    metadata = {}

    # ═══ 主键变量 ═══
    metadata['target_bank'] = VariableMetadata(
        var_name='target_bank',
        label='Target Bank',
        description='目标银行名称（标准化后的银行全称）',
        data_type='str',
        unit='',
        value_range='42家商业银行',
        formula='',
        source_stage='Stage 11',
        reference='',
        notes='面板数据的银行维度主键',
        category='主键',
        track='',
    )

    metadata['year'] = VariableMetadata(
        var_name='year',
        label='Year',
        description='年份',
        data_type='int',
        unit='年',
        value_range='[2013, 2023]',
        formula='',
        source_stage='Stage 11',
        reference='',
        notes='面板数据的时间维度主键',
        category='主键',
        track='',
    )

    # ═══ 注意力指数 ═══
    metadata['ft_attn_yr'] = VariableMetadata(
        var_name='ft_attn_yr',
        label='Fintech Attention Index (Year)',
        description='年度金融科技注意力指数，基于新闻报道频率和媒体覆盖度计算',
        data_type='float',
        unit='指数值',
        value_range='[0, +∞)',
        formula='ln(1 + n_articles) × exp(-distance_decay)',
        source_stage='Stage 24',
        reference='Da et al. (2011, JF); Fang & Peress (2009, JF)',
        notes='使用指数距离衰减权重，反映媒体注意力的空间扩散效应',
        category='注意力指数',
        track='',
    )

    # ═══ LLM 情感指标 ═══
    metadata['llm_vote_tone_full'] = VariableMetadata(
        var_name='llm_vote_tone_full',
        label='LLM Vote Tone (Full-text)',
        description='LLM投票情感指数（全文轨道），基于多个大语言模型的投票结果',
        data_type='float',
        unit='情感值',
        value_range='[-1, 1]',
        formula='(n_pos - n_neg) / (n_pos + n_neg + n_neu)',
        source_stage='Stage 21',
        reference='Cao et al. (2025, Working Paper)',
        notes='使用GPT-5-nano、Gemini-3、Grok-4.1三个模型的多数投票结果',
        category='情感指标',
        track='full',
    )

    metadata['llm_vote_tone_ctx'] = VariableMetadata(
        var_name='llm_vote_tone_ctx',
        label='LLM Vote Tone (Context)',
        description='LLM投票情感指数（上下文轨道），仅分析包含目标银行的句子及其前后文',
        data_type='float',
        unit='情感值',
        value_range='[-1, 1]',
        formula='(n_pos - n_neg) / (n_pos + n_neg + n_neu)',
        source_stage='Stage 21',
        reference='Cao et al. (2025, Working Paper)',
        notes='上下文轨道可以减少噪音，提高情感识别的精确度',
        category='情感指标',
        track='ctx',
    )

    # ═══ 网络中心度指标 ═══
    metadata['bank_degree_cent'] = VariableMetadata(
        var_name='bank_degree_cent',
        label='Co-mention Degree Centrality',
        description='银行共现网络的度中心度，衡量银行在媒体报道中的连接数量',
        data_type='float',
        unit='中心度',
        value_range='[0, 1]',
        formula='degree(i) / (n - 1)',
        source_stage='Stage 46',
        reference='Freeman (1979, Social Networks)',
        notes='度中心度越高，表示该银行与其他银行共同出现在新闻中的频率越高',
        category='网络指标',
        track='',
    )

    return metadata


# ============================================================================
# 3. 自动提取变量统计信息
# ============================================================================

def extract_variable_stats(
    panel: pd.DataFrame,
    var_name: str
) -> Dict[str, Any]:
    """从面板数据中自动提取变量的统计信息

    Args:
        panel: 面板数据
        var_name: 变量名

    Returns:
        包含统计信息的字典
    """
    if var_name not in panel.columns:
        return {}

    series = panel[var_name]
    stats = {
        '观测数': len(series),
        '缺失数': series.isna().sum(),
        '缺失率': f"{series.isna().mean():.2%}",
    }

    # 数值型变量的统计
    if pd.api.types.is_numeric_dtype(series):
        valid = series.dropna()
        if len(valid) > 0:
            stats.update({
                '均值': f"{valid.mean():.4f}",
                '标准差': f"{valid.std():.4f}",
                '最小值': f"{valid.min():.4f}",
                '25分位': f"{valid.quantile(0.25):.4f}",
                '中位数': f"{valid.median():.4f}",
                '75分位': f"{valid.quantile(0.75):.4f}",
                '最大值': f"{valid.max():.4f}",
            })

    # 分类变量的统计
    elif pd.api.types.is_string_dtype(series) or pd.api.types.is_categorical_dtype(series):
        valid = series.dropna()
        if len(valid) > 0:
            value_counts = valid.value_counts()
            stats.update({
                '唯一值数': len(value_counts),
                '最常见值': value_counts.index[0] if len(value_counts) > 0 else '',
                '最常见值频数': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            })

    return stats


# ============================================================================
# 4. 生成完整的变量代码手册
# ============================================================================

_DEFAULT_CODEBOOK_FORMATS: tuple[str, ...] = ('excel', 'csv', 'markdown', 'json')


def generate_codebook(
    panel: pd.DataFrame,
    output_dir: str,
    formats: List[str] | None = None,
) -> Dict[str, str]:
    """生成完整的变量代码手册

    Args:
        panel: 面板数据
        output_dir: 输出目录
        formats: 输出格式列表，可选：'excel', 'csv', 'markdown', 'json'.
            None 时取 _DEFAULT_CODEBOOK_FORMATS 全 4 格式.

    Returns:
        生成的文件路径字典
    """
    if formats is None:
        formats = list(_DEFAULT_CODEBOOK_FORMATS)
    logger.info("=" * 70)
    logger.info("生成变量代码手册（Variable Codebook）")
    logger.info("=" * 70)

    # 获取变量元数据字典
    metadata_dict = get_variable_metadata_dict()

    # 构建完整的代码手册数据
    codebook_data = []
    for col in panel.columns:
        # 获取预定义的元数据
        if col in metadata_dict:
            meta = metadata_dict[col]
            row = meta.to_dict()
        else:
            # 自动推断元数据
            row = {
                '变量名': col,
                '标签': _infer_label(col),
                '描述': _infer_description(col),
                '数据类型': str(panel[col].dtype),
                '单位': '',
                '取值范围': '',
                '计算公式': '',
                '来源阶段': _infer_source_stage(col),
                '学术引用': '',
                '备注': '自动推断的元数据，需要人工审核',
                '变量类别': _infer_category(col),
                '文本轨道': _infer_track(col),
            }

        # 添加统计信息
        stats = extract_variable_stats(panel, col)
        row.update(stats)

        codebook_data.append(row)

    # 转换为 DataFrame
    codebook_df = pd.DataFrame(codebook_data)

    # 生成输出文件
    output_files = {}
    os.makedirs(output_dir, exist_ok=True)

    # Excel 格式
    if 'excel' in formats:
        excel_path = os.path.join(output_dir, 'variable_codebook.xlsx')
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            codebook_df.to_excel(writer, sheet_name='Codebook', index=False)
            # 调整列宽
            worksheet = writer.sheets['Codebook']
            for idx, col in enumerate(codebook_df.columns, 1):
                max_length = max(
                    codebook_df[col].astype(str).map(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(64 + idx)].width = min(max_length + 2, 50)
        output_files['excel'] = excel_path
        logger.info(f"  ✓ Excel 格式: {excel_path}")

    # CSV 格式
    if 'csv' in formats:
        csv_path = os.path.join(output_dir, 'variable_codebook.csv')
        codebook_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        output_files['csv'] = csv_path
        logger.info(f"  ✓ CSV 格式: {csv_path}")

    # Markdown 格式
    if 'markdown' in formats:
        md_path = os.path.join(output_dir, 'variable_codebook.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# 变量代码手册（Variable Codebook）\n\n")
            f.write(f"**生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**变量总数**: {len(codebook_df)}\n\n")
            f.write(f"**面板维度**: {len(panel)} 行 × {len(panel.columns)} 列\n\n")
            f.write("---\n\n")
            f.write(codebook_df.to_markdown(index=False))
        output_files['markdown'] = md_path
        logger.info(f"  ✓ Markdown 格式: {md_path}")

    # JSON 格式
    if 'json' in formats:
        json_path = os.path.join(output_dir, 'variable_codebook.json')
        codebook_dict = codebook_df.to_dict(orient='records')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(codebook_dict, f, ensure_ascii=False, indent=2)
        output_files['json'] = json_path
        logger.info(f"  ✓ JSON 格式: {json_path}")

    logger.info(f"\n变量代码手册生成完成！共 {len(codebook_df)} 个变量")
    return output_files


# ============================================================================
# 5. 辅助函数：自动推断变量属性
# ============================================================================

def _infer_label(var_name: str) -> str:
    """自动推断变量标签"""
    # 轨道映射
    track_suffix = ''
    if var_name.endswith('_full'):
        track_suffix = ' (Full)'
    elif var_name.endswith('_ctx'):
        track_suffix = ' (Ctx)'
    elif var_name.endswith('_title'):
        track_suffix = ' (Title)'

    # 基础标签推断
    if 'tone' in var_name:
        return f'Sentiment Tone{track_suffix}'
    elif 'attn' in var_name:
        return f'Attention Index{track_suffix}'
    elif 'cent' in var_name:
        return f'Network Centrality{track_suffix}'
    elif 'media' in var_name:
        return f'Media Indicator{track_suffix}'
    else:
        return var_name.replace('_', ' ').title()


def _infer_description(var_name: str) -> str:
    """自动推断变量描述"""
    return f'变量 {var_name} 的详细描述（需要人工补充）'


def _infer_source_stage(var_name: str) -> str:
    """自动推断来源阶段"""
    if 'llm' in var_name or 'gpt' in var_name or 'gemini' in var_name:
        return 'Stage 21'
    elif 'bert' in var_name:
        return 'Stage 23'
    elif 'dict' in var_name or 'jiang' in var_name or 'yao' in var_name:
        return 'Stage 22'
    elif 'attn' in var_name:
        return 'Stage 24'
    elif 'network' in var_name or 'cent' in var_name:
        return 'Stage 46'
    elif 'strat' in var_name:
        return 'Stage 25'
    else:
        return '未知'


def _infer_category(var_name: str) -> str:
    """自动推断变量类别"""
    if var_name in ['target_bank', 'year']:
        return '主键'
    elif 'tone' in var_name or 'sent' in var_name:
        return '情感指标'
    elif 'attn' in var_name:
        return '注意力指数'
    elif 'cent' in var_name or 'network' in var_name:
        return '网络指标'
    elif 'media' in var_name:
        return '媒体指标'
    elif 'strat' in var_name:
        return '战略差异'
    else:
        return '其他'


def _infer_track(var_name: str) -> str:
    """自动推断文本轨道"""
    if var_name.endswith('_full'):
        return 'full'
    elif var_name.endswith('_ctx'):
        return 'ctx'
    elif var_name.endswith('_title'):
        return 'title'
    else:
        return ''

