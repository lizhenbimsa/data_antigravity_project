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

# fix(omni-g-preprocess-04, 2026-06-11): 清洗代码版本号 — 纳入 per-file 增量缓存键
# (见 runner.py::compute_preprocess_cache_key)。任何改变 per-file 清洗/过滤语义的
# 代码变更 (正则/过滤顺序/资源处理) 都必须 bump 此常量, 使 production run 时
# 旧缓存自动失效重算, 防止盘上语料成为不同清洗规则的混合体。
PREPROCESS_CODE_VERSION = 'v2-2026-06-11-omni'


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

# fix(omni-g-preprocess-03, 2026-06-11): 网页互动计数 noise 族 (_category_11:
# view/like/comment/share/collect/count_suffix) 与 pagination 的裸 `\d+/\d+` 支
# 设计目标是删网页互动计数, 但在报纸正文 (本语料媒体类型=报纸, 无互动计数) 中
# 无锚定地命中实质内容 ('专家推荐30只银行股'→'专家只银行股', '不良率从3/4季度
# 开始下降'→'不良率从季度开始下降')。
# 2026-06-13: 本项目不含网页/APP 语料, 故这些模式 **永久排除** — 删去历史 config 开关
# preprocessing.interaction_noise_patterns_enabled (及常量 INTERACTION_NOISE_ENABLED),
# filter_noise_patterns 无条件剔除互动计数族 + 摘 pagination 裸分数支 (等价旧 false 路径)。
# 白话: 这些"点赞/评论/分页"清洗规则只对网页有用; 本项目全是报纸, 用不上且会误删
#       正文数字, 所以直接固定关掉, 不再留开关。
INTERACTION_NOISE_KEYS = frozenset({
    'view_count', 'count_suffix', 'comment_count',
    'like_count', 'collect_count', 'share_count',
})
# pagination 中匹配任意 `数字/数字` 的裸分数支 (如 '3/4季度') — 与互动计数族一并永久排除
_PAGINATION_BARE_FRACTION_BRANCH = r'|\d+\s*/\s*\d+'


def filter_noise_patterns(noise_data: dict) -> list:
    """从 noise_patterns.json 数据中选取生效的噪声模式 (跳过 ``_`` 注释键).

    fix(omni-g-preprocess-03, 2026-06-11): 整键剔除网页互动计数族
    (INTERACTION_NOISE_KEYS) 并从 pagination 模式中摘除裸 ``\\d+/\\d+`` 支,
    防止报纸正文实质内容被误删。
    2026-06-13: 本项目无网页语料, 该剔除已由历史 config 开关改为无条件执行
    (等价于旧 ``interaction_enabled=False`` 路径, 行为不变)。
    """
    patterns = []
    for k, v in noise_data.items():
        if k.startswith('_'):
            continue
        if k in INTERACTION_NOISE_KEYS:
            continue
        if k == 'pagination':
            stripped = v.replace(_PAGINATION_BARE_FRACTION_BRANCH, '')
            if stripped == v:
                logger.warning(
                    "pagination 模式中未找到预期的裸 \\d+/\\d+ 支 "
                    "(noise_patterns.json 已变更?), 保留原模式"
                )
            v = stripped
        patterns.append(v)
    return patterns


# 噪声模式正则(从 JSON 文件加载, 支持热更新而无需改代码)
try:
    with open(CONFIG['paths']['noise_patterns_file'], 'r', encoding='utf-8') as f:
        noise_data = json.load(f)
        noise_patterns_list = filter_noise_patterns(noise_data)
        logger.info(
            f"已加载 {len(noise_patterns_list):,d} 个噪声模式 "
            f"(网页互动计数族已永久排除 — 报纸语料)"
        )
except Exception as e:
    logger.error(f"无法加载噪声模式文件: {e}")
    noise_patterns_list = []

# 银行关键词(用于内容预过滤, 只保留提及银行的新闻)
try:
    with open(CONFIG['paths']['bank_keywords_file'], 'r', encoding='utf-8') as f:
        BANK_KEYWORDS = json.load(f)
        logger.info(f"已加载 {len(BANK_KEYWORDS):,d} 个银行关键词")
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
# fix(omni-g-preprocess-02, 2026-06-11): 两支均加 (?<!\d)/(?!\d) 数字边界锚 —
# 旧模式无锚定, 会匹配更长数字串内部的 10-12 位子串并部分截删, 残留尾部数字
# 拼出全新错误数值 (如 '总资产138000000000元'→'总资产0元')。锚定后长数字串
# (>12 位) 完全不动; 恰为 10-12 位的独立数字串仍整体命中 (与真实电话格式
# 不可区分, 已知保守行为), 但不再产生部分截删的拼接残值。
# 白话: 旧规则会把一长串数字中间"长得像电话号"的 10-12 位剪掉, 剩下的数字
# 头尾一拼变成全新的错误金额 (138000000000 元 → 0 元); 现在要求号码两边不能
# 紧挨着其他数字, 长数字串就完全不会被碰了。
phone_pattern = re.compile(
    r'(?<!\d)(?:\+?86)?1[3-9]\d{9}(?!\d)'   # 手机号 (可带 +86/86 前缀)
    r'|(?<!\d)\d{3,4}[-\s]?\d{7,8}(?!\d)'   # 座机号 (区号 + 可选分隔符)
)
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
# fix(omni-g-preprocess-01, 2026-06-11): 重复压缩支排除数字 [^0-9] — 旧 `(.)\1{2,}`
# 对任意字符 (含数字) 的 ≥3 连续重复一律压缩为 2 个, 把金融文本中圆整金额/年份/
# 指数/股票代码的连零量级吞掉 (1000亿→100亿, 2000年→200年, 600000→600),
# 且事后不可逆。标点/空白两支保持不变。
TAIL_CLEANUP_PATTERN = re.compile(
    r'([^0-9])\1{2,}'                   # 重复字符 (排除数字; 如 'aaaaa' → 'aa')
    r'|([,，.。!！?？;；:：、])\2+'     # 冗余标点 (如 '。。。' → '。')
    r'|\s+'                              # 空白字符序列 → 单个空格
)

# 广告关键词模式: 支持字符间插入空白的弹性匹配(如"广 告"也能匹配"广告")
# fix(omni-g-preprocess-05, 2026-06-11): 高误伤词 (config:
# preprocessing.ad_keywords_title_anchored) 在标题字段改为 **行尾锚定** 匹配
# (如 '……公告$' 才删) — 旧无锚定子串匹配把货币政策公告报道 ('央行公告下调
# 存准率')、监管风险提示新闻、年报解读等真监管新闻整篇删除, 与监管事件强度
# 强相关 → 非随机样本选择。版面/栏名字段保持无锚定 (付费公告版面仍全量排除,
# 行为不变)。披露: 该排除规则见 filter.py 步骤 5 docstring。
# 扩充(2026-06-13, 广告排除过度性复查, 三批): 锚定清单 6→12→22→27 词, 补入
# 同构误伤模式的词 — 一批: 季度报告/半年度报告/业绩预告/信息披露/公示/通告;
# 二批(终审对抗复核 P1): 广告/特别提示/专项报告/核查意见/权益变动报告书/
# 事先告知书/事先告知函/事先催告书/倡议书/挂失 (如 'XX银行收到行政处罚事先
# 告知书 拟被罚没2.6亿元' / '整治银行理财虚假广告乱象' 此前被中段命中整篇误删);
# 三批(二批复核净裁决): 遗失 (防共现句式击杀'挂失'救活)/股票预案/年报摘要+
# 半年报摘要 (子串关系须成对锚定)/转债行情。
# ⚠ 拼写错误孪生词 '半年度度报告' 与 招募说明书族 刻意不锚定 (详见
# preprocessing.yaml 注释)。
# 白话: 以前标题里只要出现"公告/通知"这类词整篇就被当广告删掉, 把"央行公告
# 降准"这种正经新闻也误伤了; 现在只有标题以这些词【结尾】(如"××银行配股
# 公告") 才删, 报道类标题保得住。
_AD_KEYWORDS_TITLE_ANCHORED_DEFAULT = [
    '公告', '通知', '声明', '通报', '风险提示', '年度报告',
    '季度报告', '半年度报告', '业绩预告', '信息披露', '公示', '通告',
    '广告', '特别提示', '专项报告', '核查意见', '权益变动报告书',
    '事先告知书', '事先告知函', '事先催告书', '倡议书', '挂失',
    '遗失', '股票预案', '年报摘要', '半年报摘要', '转债行情',
]
AD_KEYWORDS_TITLE_ANCHORED = PARAMS.get(
    'ad_keywords_title_anchored', _AD_KEYWORDS_TITLE_ANCHORED_DEFAULT
)


def _flex_kw(kw: str) -> str:
    """关键词 → 字符间可插空白的弹性正则片段 (如 '广告' → '广\\s*告')."""
    return r'\s*'.join(list(kw))


AD_PATTERN = None         # 版面/栏名用: 全部关键词, 无锚定 (行为不变)
AD_PATTERN_TITLE = None   # 标题用: 高误伤词要求行尾锚定
# 词级 pattern 表 (2026-06-13): 供 filter.py 步骤 5 对被删行做 per-keyword
# 命中计数日志, 为 data appendix 排除统计表与"过度排除"监测提供素材。
# 白话: 除了"一锅煮"的大正则, 再给每个词单独留一个小正则, 删完后回头数一数
# 每个词各杀了多少行, 写进日志, 方便论文附录披露和发现哪个词杀错人。
AD_KEYWORD_PATTERNS = []        # 版面/栏名用: [(关键词, 无锚定 pattern)]
AD_KEYWORD_PATTERNS_TITLE = []  # 标题用: [(关键词, 高误伤词行尾锚定 pattern)]
if AD_KEYWORDS:
    AD_PATTERN = re.compile(
        '|'.join(_flex_kw(kw) for kw in AD_KEYWORDS), re.IGNORECASE
    )
    _anchored_set = set(AD_KEYWORDS_TITLE_ANCHORED)
    _title_parts = (
        [_flex_kw(kw) for kw in AD_KEYWORDS if kw not in _anchored_set]
        + [_flex_kw(kw) + r'\s*$' for kw in AD_KEYWORDS if kw in _anchored_set]
    )
    AD_PATTERN_TITLE = re.compile('|'.join(_title_parts), re.IGNORECASE)
    for _kw in AD_KEYWORDS:
        _flex = _flex_kw(_kw)
        AD_KEYWORD_PATTERNS.append((_kw, re.compile(_flex, re.IGNORECASE)))
        AD_KEYWORD_PATTERNS_TITLE.append((
            _kw,
            re.compile(
                _flex + r'\s*$' if _kw in _anchored_set else _flex,
                re.IGNORECASE,
            ),
        ))
    del _kw, _flex  # 防模块命名空间泄漏 (循环变量仅构表用)

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
    'MAINLAND_CHINA_REGIONS', 'AD_KEYWORDS', 'AD_KEYWORDS_TITLE_ANCHORED',
    'MEDIA_NAMES_TO_EXCLUDE', 'MEDIA_NAME_OVERRIDES', 'TEXT_COLUMNS',
    'PREPROCESS_CODE_VERSION',
    # raw resource lists
    'noise_patterns_list', 'BANK_KEYWORDS',
    # noise gating (fix omni-g-preprocess-03; interaction 族 2026-06-13 改永久排除)
    'INTERACTION_NOISE_KEYS', 'filter_noise_patterns',
    # translation table
    'COMBINED_TRANS',
    # compiled regexes
    'url_pattern', 'email_pattern', 'phone_pattern', 'emoji_pattern',
    'combined_removal_pattern', 'UNIFIED_CLEANUP_PATTERN',
    'TAIL_CLEANUP_PATTERN', 'AD_PATTERN', 'AD_PATTERN_TITLE',
    'AD_KEYWORD_PATTERNS', 'AD_KEYWORD_PATTERNS_TITLE', 'REGION_PATTERN',
    'CHINESE_CHAR_PATTERN', 'MEDIA_TYPES_INCLUDE_SET',
]
