"""news_process.pipeline.preprocess._constants — 预处理模块级常量与资源初始化.

Phase 4b 从 ``pipeline/preprocess/runner.py`` 提取, 让 sub-module 拆分 (load/
normalize/filter/dedup) 不必互相 import 状态。本模块:
- 不依赖任何 preprocess sibling 模块
- 在 import 时一次性完成 CONFIG / logger / 噪声/银行关键词加载与正则编译
- ProcessPoolExecutor spawn 模式下每 worker 重新 import → 同样一次性完成
   (与 Phase 4b 之前的 runner.py 模块级初始化语义完全等价)

约定: 所有"硬编码字典/常量/已编译正则"放在此处; 函数/类放在专属 sub-module。
"""

from __future__ import annotations

import json
import os
import re

import sys

# Phase 4b: 解析 ``news_process.core.*`` 需要项目根 (news_process/ 的父目录)
# 在 sys.path 中。脚本调用 / 包模式 / pytest fixture 等多种入口都安全。
_project_parent = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if _project_parent not in sys.path:
    sys.path.insert(0, _project_parent)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging


# ============================================================================
# 1. 配置 + logger
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "00_preprocessing"
PARAMS = CONFIG['preprocessing']

# 子进程(ProcessPoolExecutor spawn 模式)重新导入本模块时,
# 使用 console_only 模式避免多进程并发写同一日志文件导致损坏。
_is_subprocess = (__name__ != "__main__")
logger = setup_logging(STAGE_NAME, CONFIG['paths']['log_dir'], console_only=_is_subprocess)

# 去重相关配置
DEDUP_PARAMS = CONFIG.get('deduplication', {})
nb_workers = DEDUP_PARAMS.get("parallel_workers", os.cpu_count() or 1)


# ============================================================================
# 2. 从 PARAMS 提取常量(模块加载时执行一次, 避免运行时重复查找)
# ============================================================================

KEY_COLUMNS = PARAMS.get('key_columns_for_na_check', [])
MEDIA_TYPES_TO_INCLUDE = PARAMS.get('media_types_to_include', [])
REQUIRED_COLUMNS = PARAMS.get('required_columns', [])
SHEET_NAME = PARAMS.get('sheet_name', 'Sheet1')
MAINLAND_CHINA_REGIONS = PARAMS.get('mainland_china_regions', [])
AD_KEYWORDS = PARAMS.get('ad_keywords', [])
MEDIA_NAMES_TO_EXCLUDE = frozenset(PARAMS.get('media_names_to_exclude', []))

# 媒体名称映射表: 将地方版/子版名称统一合并到母报。
# 在两处应用:
#   ① _clean_and_filter_dataframe() (filter.py) → 新文件处理时即时清洗
#   ② main()                         (runner.py) → 读取合并数据后全局兜底
MEDIA_NAME_OVERRIDES = {
    # 保留原名的特殊媒体 (防止被正则步骤误清洗)
    '读者文摘 - 中文版': '读者文摘 - 中文版',
    '中国服装·鞋帮': '中国服装报',
    # ── 地方版 / 子版名称 → 母报名称 ──
    '太行日报晚报版': '太行日报',
    '安徽日报农村版': '安徽日报',
    '人民日报市场版': '人民日报',
    '羊城晚报深圳版': '羊城晚报',
    '羊城晚报佛山版': '羊城晚报',
    '羊城晚报珠中江地方版': '羊城晚报',
    '羊城晚报顺德版': '羊城晚报',
    '生活报七台河版': '生活报',
    '新民晚报社区版家庭周刊': '新民晚报社区版',
    '武汉科技报少年科普周刊': '武汉科技报',
    '新闻晨报社区版': '新闻晨报',
}

# 文本标准化配置
NORMALIZATION_PARAMS = CONFIG.get('normalization', {})


# ============================================================================
# 3. 预编译翻译表 (一次构建, 全局复用)
# ============================================================================
# 技术原理: str.translate() 使用 C 级别的字符映射表,
# 单次调用可同时完成全角→半角和引号标准化, 比分步 str.replace() 快 3-5x。

_FULL_CHARS = (
    '０１２３４５６７８９'
    'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
    'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
    '－（）～！＠＃￥％︿＆＊＋＝＼｜，．？＜＞｛｝【】；：　'
)
_HALF_CHARS = (
    '0123456789'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    "-()~!@#$%^&*+=\\|,.?<>{}[];: "
)
_full_to_half_table = str.maketrans(_FULL_CHARS, _HALF_CHARS)

# 中文引号 → ASCII 直引号
_quote_table = {
    0x201C: '"',  0x201D: '"',         # 左右双弯引号
    ord('「'): '"', ord('」'): '"',    # 日文引号
    ord('『'): '"', ord('』'): '"',    # 日文书名号
}

# 合并为单个翻译表
COMBINED_TRANS = {**_full_to_half_table, **_quote_table}

TEXT_COLUMNS = ['标题', '内容']


# ============================================================================
# 4. 加载外部资源 (噪声 / 银行关键词)
# ============================================================================

# 噪声模式正则(从 JSON 文件加载, 支持热更新而无需改代码)
try:
    with open(CONFIG['paths']['noise_patterns_file'], 'r', encoding='utf-8') as f:
        noise_data = json.load(f)
        # 跳过以 '_' 开头的注释键
        noise_patterns_list = [v for k, v in noise_data.items() if not k.startswith('_')]
        logger.info(f"已加载 {len(noise_patterns_list)} 个噪声模式")
except Exception as e:
    logger.error(f"无法加载噪声模式文件: {e}")
    noise_patterns_list = []

# 银行关键词(用于内容预过滤, 只保留提及银行的新闻)
try:
    with open(CONFIG['paths']['bank_keywords_file'], 'r', encoding='utf-8') as f:
        BANK_KEYWORDS = json.load(f)
        logger.info(f"已加载 {len(BANK_KEYWORDS)} 个银行关键词")
except Exception as e:
    logger.error(f"无法加载银行关键词文件: {e}")
    BANK_KEYWORDS = []


# ============================================================================
# 5. 预编译正则表达式 (避免每个文件/每行重复编译)
# ============================================================================

# 各类噪声文本的匹配模式
control_char_pattern_str = r'[\x00-\x1f\x7f-\x9f]'
url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
phone_pattern = re.compile(r'(?:\+?86)?1[3-9]\d{9}|\d{3,4}[-\s]?\d{7,8}')
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF"
    "\U00002700-\U000027BF\U00002600-\U000026FF\U0001F1E6-\U0001F1FF"
    "]+", flags=re.UNICODE
)

# 噪声模式合并为单个正则(减少 re.sub 调用次数)
all_removal_patterns = noise_patterns_list + [control_char_pattern_str]
try:
    combined_removal_pattern = (
        re.compile('|'.join(all_removal_patterns))
        if all_removal_patterns
        else re.compile(r'\b\B')  # 永远不匹配的空模式
    )
    logger.info("噪声模式正则编译成功")
except re.error as e:
    logger.error(f"噪声模式正则编译失败: {e}")
    combined_removal_pattern = re.compile(control_char_pattern_str)

# 统一去除正则: URL + Email + 电话 + Emoji + 噪声 + 控制字符
# 合并为单个正则, 一次 re.sub 调用完成所有清除
try:
    UNIFIED_CLEANUP_PATTERN = re.compile(
        '|'.join([url_pattern.pattern, email_pattern.pattern,
                  phone_pattern.pattern, emoji_pattern.pattern])
        + '|' + combined_removal_pattern.pattern
    )
    logger.info("统一清除正则编译成功")
except re.error as e:
    logger.error(f"统一清除正则编译失败, 将回退到分步模式: {e}")
    UNIFIED_CLEANUP_PATTERN = None

# 尾部清理: 重复字符 + 冗余标点 + 空白序列, 合并为单个正则
TAIL_CLEANUP_PATTERN = re.compile(
    r'(.)\1{2,}'                        # 重复字符 (如 'aaaaa' → 'aa')
    r'|([,，.。!！?？;；:：、])\2+'     # 冗余标点 (如 '。。。' → '。')
    r'|\s+'                              # 空白字符序列 → 单个空格
)

# 广告关键词模式: 支持字符间插入空白的弹性匹配(如"广 告"也能匹配"广告")
AD_PATTERN = None
if AD_KEYWORDS:
    flexible_patterns = [r'\s*'.join(list(kw)) for kw in AD_KEYWORDS]
    AD_PATTERN = re.compile('|'.join(flexible_patterns), re.IGNORECASE)

# 中国大陆地区名匹配
REGION_PATTERN = (
    re.compile('|'.join(MAINLAND_CHINA_REGIONS))
    if MAINLAND_CHINA_REGIONS else None
)

# 汉字字符匹配(用于统计标题/内容中的汉字数量)
CHINESE_CHAR_PATTERN = re.compile(r'[\u4e00-\u9fff]')

# 媒体类型保留集 (frozenset 的 __contains__ 比 list 快 O(1) vs O(n))
MEDIA_TYPES_INCLUDE_SET = frozenset(MEDIA_TYPES_TO_INCLUDE)


__all__ = [
    # config + logger
    'CONFIG', 'STAGE_NAME', 'PARAMS', 'NORMALIZATION_PARAMS', 'DEDUP_PARAMS',
    'logger', 'nb_workers',
    # data constants
    'KEY_COLUMNS', 'MEDIA_TYPES_TO_INCLUDE', 'REQUIRED_COLUMNS', 'SHEET_NAME',
    'MAINLAND_CHINA_REGIONS', 'AD_KEYWORDS', 'MEDIA_NAMES_TO_EXCLUDE',
    'MEDIA_NAME_OVERRIDES', 'TEXT_COLUMNS',
    # raw resource lists
    'noise_patterns_list', 'BANK_KEYWORDS',
    # translation table
    'COMBINED_TRANS',
    # compiled regexes
    'url_pattern', 'email_pattern', 'phone_pattern', 'emoji_pattern',
    'combined_removal_pattern', 'UNIFIED_CLEANUP_PATTERN',
    'TAIL_CLEANUP_PATTERN', 'AD_PATTERN', 'REGION_PATTERN',
    'CHINESE_CHAR_PATTERN', 'MEDIA_TYPES_INCLUDE_SET',
]
