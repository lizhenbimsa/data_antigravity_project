"""news_process.core.caching — LLM 请求级 SQLite 缓存。

源自 Phase 1 mega-module ``utils/llm_cache.py`` 拆分 (Plan-r3 P2-11
头部修正).

功能
-----
对 LLM API 请求进行持久化缓存，避免重复调用相同 prompt 的 API。

缓存键组成 (Plan-r3 P3-17 升级)
-------------------------------
键 = SHA-256 哈希:

    ``f"{SCHEMA_VERSION}|{len(model_id)}:{model_id}|{len(prompt)}:{prompt}|{prompt_version}|{temperature:.4f}"``

各字段含义:

- ``SCHEMA_VERSION`` (常量) — 本模块版本标识. 任何 prompt 模板 / system
  prompt / 响应格式约定层面的修改, 都应 bump 此常量, 让全部历史 cache
  自动失效 (silent miss → 重新调 API). v0 是 round 1+2 历史; v1 是
  Plan-r3 P3-17 引入 prompt_version + temperature 维度的标记.
- ``len(x):x`` 长度前缀 — 防止 ``("a", "b:c")`` 与 ``("a:b", "c")`` 的拼接
  歧义碰撞 (round 1 已有的设计).
- ``prompt_version`` — 调用方显式传入的 prompt 模板版本 (例如
  ``"v6-2026-05-09"``, 与 ``config/prompts/*.txt`` 头部 ``# version: ...``
  对齐). 默认 ``"v0"`` 表示未指定.
- ``temperature`` — LLM 推理温度 (默认 0.0 = 确定性). 0.0 与 0.5 的响应
  分布完全不同, 共用同一缓存键会污染.

设计意图
---------
- silent staleness 防御 — round 1+2 缓存键仅 (model_id, prompt), 当
  prompts/sentiment_cot.txt 改写时, 旧 cache 仍命中, 分析结果不反映新提示词.
  现在 prompt_version 进键, 改一行 prompt → cache miss → 重新调 API.
- BREAKING — Plan-r3 P3-17 把 SCHEMA_VERSION 从 ``"v0"`` 升至 ``"v1"``,
  既有 ``_llm_cache.db`` (236 MiB, 历史快照 @ P3-17 迁移时刻; 现已 ~500MB+
  且随 _ss 轨缓存播种持续增长, 精确值以 CLAUDE.md / 实读磁盘为准)
  全部 silent miss, 下次跑 stage 21 / 15 / 27 会冷启动. 用户已在 plan 中
  explicit 接受此代价.
- 向后兼容 API — ``get/put/put_batch`` 新增的两个参数 ``prompt_version``
  / ``temperature`` 都有默认值 (v0 / 0.0); 旧调用方不修改也能跑, 只是
  键会落到 (v1, v0, 0.0) 命名空间, 与 round 1+2 (v0 命名空间) 完全隔离.

✅ Feature flag 启用状态 (v3.0, 2026-05-13)
------------------------------------------
本模块的 ``prompt_version`` 维度已 **全量接入 6 个生产 callsite**:

- API 层面: ``_make_key/get/put/put_batch`` 实现 ``prompt_version`` 维度,
  由 5 个 invariant test (test_pipeline_robustness.py) 守护正确性.
- 接入机制: ``core/config.py::_inline_external_prompts`` 在加载
  ``config/prompts/*.txt`` 时自动解析首行 ``# version: <token>`` 并写入
  ``<key>_version`` 配置字段; callsite 通过 ``cfg[...]['prompt_template_version']``
  或模块内联常量 ``PEER_PROMPT_VERSION`` / ``EMBEDDING_CONFIG['text_pipeline_version']``
  显式传给 ``LLMCache.get/put``.
- 调用层面 (6 个生产 callsite):

    1. ``pipeline/sentiment/tone_llms.py``        — full/ctx track, PROMPT_VERSION
    2. ``pipeline/panel/llm_peer_iv.py``          — PEER_PROMPT_VERSION (模块内联常量)
    3. ``pipeline/filtering/policy_alignment.py`` — text_pipeline_version (embedding)
    4. ``pipeline/features/benefit_society.py``   — text_pipeline_version (embedding)
    5. ``pipeline/features/strategic_diff.py``    — text_pipeline_version (embedding)
    6. ``pipeline/panel/network_spillover.py``    — text_pipeline_version (embedding)

  注: 共 6 个文件 / 6 处 callsite.
  之前 (Plan-r3 round 3) 注释错记为 "5 个", 漏报 network_spillover.

效果:
- 修改 ``config/prompts/unified_cot.txt`` 时,
  把首行 ``# version: vX-YYYY-MM-DD`` bump 即可触发 cache silent miss,
  确保新提示词重新调 API.
- 修改 ``llm_peer_iv.py::PEER_PROMPT`` 字符串时, 同步 bump
  ``PEER_PROMPT_VERSION`` 模块常量.
- 修改 embedding 模型 / 文本预处理 / 切片策略时, 在 ``config/features.yaml::
  embedding_api.text_pipeline_version`` bump 版本号.

SCHEMA_VERSION 保持 v1 (无需再 bump): 现有 LLMCache 中以 (v1, "v0", 0.0)
为键的历史条目继续命中; 仅当 callsite 传入新版本号时才走新 namespace.

线程安全
---------
sqlite3.connect(db_path, check_same_thread=False) + WAL 日志模式。

查询复杂度与生命周期 (为什么"删光缓存、第一次运行也不会遍历全库")
------------------------------------------------------------------
缓存键 (上文 sha256(...)) 落在 ``cache_key TEXT PRIMARY KEY`` 上。SQLite
对非-INTEGER 主键自动建一棵唯一 B-tree 索引, 因此每次 ``get()`` 都是
``WHERE cache_key = ?`` 的**索引点查 (point lookup)**, 复杂度 ≈ O(log n):
库里有 133,687 条还是 0 条, 单次查找成本同量级 — **从不逐条扫描全表**。

- 全模块无任何 ``SELECT *`` / ``fetchall`` / 游标遍历; 唯一的全表聚合是
  ``size()`` 的 ``COUNT(*)``, 仅供 run 末尾打统计日志, 不在处理热路径。
- ``__init__`` 不把任何行读进内存: 只 ``CREATE TABLE IF NOT EXISTS`` +
  设 WAL。所谓"第一次运行"不存在"先扫一遍全库"的冷启动步骤。
- 删掉 ``_llm_cache.db`` 后第一次运行: 自动新建**空表**, 每条 ``get()``
  都是空表 miss (瞬时返回 None) → 调付费 API → ``put()`` 回填。全程零遍历。

⚠ 删缓存省不掉任何"遍历开销" (本就没有遍历); 真正的代价是 **13 万条全部
miss → 重新付费调 LLM/embedding API 重建**, 且破坏 golden 跨-run 字节级
可复现 (见上文"设计意图"与 CLAUDE.md "勿删 _llm_cache.db 铁律")。

大白话
~~~~~~
把这库想成"带目录索引的字典": 查一个词是拿指纹 (cache_key) 直接翻到那一
页, 不是从第一条往后一条条找。字典里有多少词, 翻这一下都一样快。把字典
全删了再跑, 等于拿到一本空字典 —— 每查必空、秒回, 然后去花钱重新问大模型、
再把答案抄进去。慢和贵都来自"重新调 API", 跟"遍历"没关系。

学术依据
---------
Carlson & Burbano (2026, SMJ §3.3) — LLM 实验可复现性要求确定性缓存.
Plan-r3 P3-17 的 prompt_version 维度直接对应 §3.3.2 "version-aware
provenance" 实践: 任何 prompt 改动必须导致 cache invalidate.

§5 缓存版本门治理规范 (2026-06-25; 新增任何缓存层必遵守)
========================================================
全项目缓存的"改了代码但缓存仍命中旧值 (silent staleness)"是头号风险。提炼现有
5 个版本门 (SCHEMA_VERSION / prompt_version×3 / text_pipeline_version×2 /
PREPROCESS_CODE_VERSION) 的共性, 立 5 条铁律:

- (A) 新缓存键首字段 = SCHEMA_VERSION (沿用 _make_key 模式), 保留全局一键失效能力.
- (B) 凡"改代码语义会改输出但不改键内既有字段"的参数, 要么进键 (如 temperature/seed
      按需进键), 要么绑一个显式 version token, 并在 callsite + config 注释写死 bump 触发条件.
- (C) 嵌入/FP 敏感超参 (model / 切片策略 / dtype / 线程数 等) 必当版本维度对待 — 改语义
      却不进键 (键仅 model_id|chunk文本|text_pipeline_version) → silent staleness; 必同 diff
      bump 对应 text_pipeline_version (例: v3.14.0 MAIN 槽 text-embedding-3-small→
      gemini-embedding-2-preview, 同步 bump config/features.yaml::embedding_api.text_pipeline_version
      → "v3-2026-06-27-gemini"; v3.14.0 起全 API、无本地 batch_size 维度).
- (D) version token 优先放可 lint 扫描的位置: config/prompts/*.txt 首行 > config yaml
      字段 > 模块内联常量. 内联常量是最弱形式, 须配 frozen-hash 单测补强 (反例 + 守卫:
      llm_peer_iv.py::PEER_PROMPT, tests/test_peer_prompt_frozen.py).
- (E) 资源文件 (词典 / anchor / MEDIA_NAME_OVERRIDES 等) 应以内容 sha256 入键, 而非靠
      人工记得 bump (preprocess 已对 noise_patterns / bank_keywords 做).

物理库分治、逻辑接口统一: 本地深度模型推理缓存用独立 sqlite (如 _local_model_cache.db),
验证阶段变体缓存用 _llm_cache_validation.db, 但都复用本模块 LLMCache 类 + 同款键纪律;
生产锚点 _llm_cache.db 勿与它们混库 (避免膨胀 + 稀释 verify 统计).
"""

import hashlib
import logging
import os
import sqlite3
import threading
import time

logger = logging.getLogger(__name__)


# Plan-r3 P3-17: 缓存键 schema 版本. 任何键组成或语义层面的破坏性变更
# 都必须 bump 此常量, 让所有历史 cache 静默失效 (重新调 API).
#
# v0 — round 1+2 (key = sha256(len:model_id:prompt))
# v1 — Plan-r3 P3-17 (key = sha256(SCHEMA|len:model_id|len:prompt|pv|temp))
#
# 平滑迁移: ``get()`` 在新键 (v1) miss 时, 自动按旧 (v0) 算法再算一次键
# 做 fallback 读. 这样:
#   - 历史 _llm_cache.db (v0 写入的 236 MiB) 仍能 hit, 测试 / 生产 stage
#     无需等待 API 重调
#   - 调用方传入 prompt_version='v6...' 或非默认 temperature 时, _make_key
#     生成的 v1 键是全新命名空间, fallback v0 必 miss → 正确触发新 API call
#   - put/put_batch 始终用 v1 算法, 老 v0 记录会逐步被新 v1 记录"超越"
#     (相同 prompt 的新写入会建立 v1 key, 之后 get 直接命中 v1)
#   - 用户在 v3.0 准备就绪后可手动 ``DELETE FROM llm_cache WHERE...`` 或
#     直接删 _llm_cache.db 让 v0 命名空间归零.
SCHEMA_VERSION = "v1"

# None 输入哨兵 (final recode F2 修复 + round-3 review R8 改为纯 ASCII):
#
# 旧版用 ``'\x00<None>\x00'`` (含 null byte) — 虽然 hashlib.sha256 输出不含
# null byte (永远是 hex 字符), 但 round-3 review R8 指出: 万一未来代码 path
# 把 m_id / p_str 直接 print 到 log 或写到非-hash 字段, 含 \x00 的字符串在
# 部分终端 / sqlite3 实现下行为不可预测 (Python 3.11+ sqlite3 实测可存可读,
# 但跨版本不保证).
#
# 新版用纯 ASCII ``'<<NULL_SENTINEL>>'`` — 字面量极不可能与合法 model_id /
# prompt / prompt_version 碰撞 (生产 yaml 不会出现这种字符串). 把哨兵长度
# 通过 ``f"{len(m_id)}:{m_id}"`` 长度前缀绑定, 确保即使用户传入字面量
# ``'<<NULL_SENTINEL>>'`` 也与 None 区分 (两者长度不同 → key 不同).
#
# 注意: 这是 round-3 内的 SCHEMA-compatible 改动 — 既有的所有 v1 cache 写
# 入都不传 None (生产 model_id / prompt 永远是非空字符串), 所以更换哨兵
# 字面量不会让任何现有 v1 cache 失效. 仅理论上"曾用 None 输入"的合成测试
# cache 失效, 但合成测试用 tmp_path 隔离, 也无 production cache 影响.
_NONE_SENTINEL = '<<NULL_SENTINEL>>'


class LLMCache:
    """LLM 请求级 SQLite 缓存。

    缓存键: sha256(SCHEMA_VERSION|len:model_id|len:prompt|prompt_version|temperature).
    缓存值: API 原始响应文本 + 模型标识 + 时间戳.

    Attributes:
        db_path: SQLite 数据库文件路径。
    """

    def __init__(self, db_path: str):
        """初始化 LLM 缓存。

        Args:
            db_path: SQLite 数据库文件路径。若不存在则自动创建。
        """
        self.db_path = db_path
        self._lock = threading.Lock()
        # T0.0a: 进程级运行时计数器 (不落盘, 每次 LLMCache 实例化重置).
        # 用于 stage 21 / embedding stage 结束时打 hit-rate 摘要, 帮助
        # 诊断"为什么这次 run 比上次慢" / "新 prompt_version 让缓存全 miss"
        # 之类问题. 多线程下 get()/put() 都已经持 self._lock, 计数器与 DB
        # 读写在同一临界区内增改, 无额外同步开销.
        self._hits = 0       # v1 命中
        self._v0_hits = 0    # v0 fallback 命中 (老 cache 兼容路径)
        self._misses = 0     # 两条路径都 miss
        self._writes = 0     # put + put_batch 累计写入条数
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        # WAL 模式: 支持并发读，写入不阻塞读取
        self._conn.execute("PRAGMA journal_mode=WAL")
        # cache_key 为 TEXT PRIMARY KEY → SQLite 自动建唯一 B-tree 索引, 故
        # get() 的 ``WHERE cache_key = ?`` 是索引点查 (O(log n)), 不随库增大
        # 而变慢、永不全表扫描 (详见模块 docstring "查询复杂度与生命周期")。
        # __init__ 仅建表 + 设 WAL, 不读取任何行入内存 — "第一次运行"无冷启动
        # 全库遍历; 即便删库重建, 新空表的逐条 get() 也是瞬时 miss, 不遍历。
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS llm_cache (
                cache_key   TEXT PRIMARY KEY,
                model_id    TEXT NOT NULL,
                response    TEXT NOT NULL,
                created_at  REAL NOT NULL
            )
        """)
        self._conn.commit()

    @staticmethod
    def _make_key(model_id: str, prompt: str,
                  *, prompt_version: str = "v0",
                  temperature: float = 0.0,
                  random_seed: int | None = None) -> str:
        """生成缓存键 (Plan-r3 P3-17 升级版).

        Args:
            model_id:        模型标识符 (例如 "gpt-5.4-nano").
            prompt:          请求的 prompt 文本.
            prompt_version:  prompt 模板版本字符串 (例如 "v6-2026-05-09").
                             默认 "v0" 表示调用方未指定 — 与新 prompt 改动后
                             的 cache 自然分离.
            temperature:     LLM 推理温度 (默认 0.0 = 确定性).

        Returns:
            str: 64 字符的十六进制 SHA-256 哈希值。

        Note:
            键格式见模块 docstring "缓存键组成". 任何破坏性变更必须 bump
            模块级 ``SCHEMA_VERSION`` 常量.
        """
        # ⚠ final recode 审查发现: model_id=None 与 model_id="" 不能共用 namespace
        # (旧实现 ``str(x) if x is not None else ""`` 让 None ≡ ""). 用纯 ASCII 哨兵
        # ``_NONE_SENTINEL`` ('<<NULL_SENTINEL>>') 区分, 并经 ``f"{len(m_id)}:{m_id}"``
        # 长度前缀绑定, 即便用户传入字面量 '<<NULL_SENTINEL>>' 也与 None 长度不同而区分
        # (详见模块 docstring 141-157, round-3 review R8 已弃用旧 null-byte 方案).
        # 生产 code path 不传 None (yaml 配置必有值), 但作为公开 API 接口契约必须严格.
        m_id = _NONE_SENTINEL if model_id is None else str(model_id)
        p_str = _NONE_SENTINEL if prompt is None else str(prompt)
        pv = _NONE_SENTINEL if prompt_version is None else str(prompt_version)
        # ⚠ recode 审查发现: 用 .4f 格式化会让 1e-30 与 0.0 都格式化为 "0.0000"
        # 引发键碰撞 (recode/test_cache_temperature_precision). 改用 repr() 保证
        # Python 浮点的 "shortest unambiguous representation":
        #   repr(0.0) == '0.0'    repr(1e-30) == '1e-30'  (区分)
        #   repr(0.5) == '0.5'    repr(0.05)  == '0.05'
        # 同时长度前缀让 prompt_version 含 '|' 也不引发碰撞.
        # 边角说明 (final recode 审查通过):
        #   - nan: repr(nan)='nan', 两次 nan 调用键相等 (避免 cache 无穷失效); 生产不传
        #   - -0.0: repr(-0.0)='-0.0' 与 0.0 区分; 生产不传; 严格学术正确
        temp_str = repr(float(temperature))
        # audit S2 修复 (2026-05-30): seed 维度按需进键, 避免静默 stale-hit。
        # 设计: seed 仅在 temperature != 0.0 时拼入 key。理由 —
        #   (1) temperature=0.0 (贪心解码) 下 random_seed 对 LLM 输出无影响,
        #       省略它使 key 与历史 P3-17 schema (无 seed 维度) 字节级一致 →
        #       零缓存失效, 无需 bump SCHEMA_VERSION (现存 _llm_cache.db 全命中)。
        #   (2) temperature>0 时 seed 决定采样路径, 必须进 key, 让温度/种子
        #       稳健性扫描得到正确的 cache miss, 而非静默命中按 temp=0.0 算出
        #       的旧响应 (后者会污染稳健性表)。
        seed_part = (
            f"|seed:{int(random_seed)}"
            if (random_seed is not None and float(temperature) != 0.0)
            else ""
        )
        # SCHEMA|len:model|len:prompt|len:pv|temp_repr[|seed:N]
        raw = (
            f"{SCHEMA_VERSION}|"
            f"{len(m_id)}:{m_id}|"
            f"{len(p_str)}:{p_str}|"
            f"{len(pv)}:{pv}|{temp_str}{seed_part}"
        )
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    # v3.7.0 (C3 修复): 公开 API alias 供 pipeline.llm_archive 反向 lookup 使用.
    # 与 _make_key 完全等价, 但名字无下划线表示公开 contract — 未来 LLMCache 重构
    # 时必须保持此别名行为不变 (顶刊 reproducibility 强约束, V4 F-P2.1).
    @staticmethod
    def make_key(model_id: str, prompt: str,
                 *, prompt_version: str = "v0",
                 temperature: float = 0.0,
                 random_seed: int | None = None) -> str:
        """``_make_key`` 的公开别名 (v3.7.0+, 稳定 API)。

        ``pipeline/llm_archive/`` 各调用点应使用本方法, 以在 LLMCache
        schema 迁移过程中保持反向 lookup 兼容性。
        """
        return LLMCache._make_key(model_id, prompt,
                                  prompt_version=prompt_version,
                                  temperature=temperature,
                                  random_seed=random_seed)

    @staticmethod
    def _make_key_v0(model_id: str, prompt: str) -> str:
        """生成 v0 旧 schema 键 (Plan-r3 P3-17 平滑迁移用).

        仅 ``get`` 在 v1 miss 时调用做 fallback 读. ``put`` 不再写 v0.
        """
        m_id = str(model_id) if model_id is not None else ""
        p_str = str(prompt) if prompt is not None else ""
        raw = f"{len(m_id)}:{m_id}:{p_str}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def get(self, model_id: str, prompt: str,
            *, prompt_version: str = "v0",
            temperature: float = 0.0,
            random_seed: int | None = None) -> str | None:
        """查询缓存 (Plan-r3 P3-17: 加 prompt_version + temperature 维度)。

        平滑迁移: 新键 (v1) miss 后, 当 ``prompt_version='v0'`` 且
        ``temperature=0.0`` (即调用方未传 P3-17 新参数时), 自动用旧 v0
        算法再查一次, 让历史 _llm_cache.db 中的 v0 记录仍能被新代码命中.

        Args:
            model_id:        模型标识符.
            prompt:          请求的 prompt 文本.
            prompt_version:  prompt 模板版本 (默认 "v0", 与历史无关键值兼容).
            temperature:     推理温度 (默认 0.0).

        Returns:
            str | None: 缓存的响应文本, 未命中返回 None.
        """
        key = self._make_key(model_id, prompt,
                             prompt_version=prompt_version,
                             temperature=temperature,
                             random_seed=random_seed)
        # 索引点查 (point lookup): 按 cache_key 主键 B-tree 直达, 非全表扫描;
        # 命中与否成本 ≈ O(log n), 与库中总条目数 (13 万 vs 0) 几乎无关。
        with self._lock:
            cursor = self._conn.execute(
                "SELECT response FROM llm_cache WHERE cache_key = ?", (key,)
            )
            row = cursor.fetchone()
            if row:
                # T0.0a: v1 命中, 在锁内增计数避免竞争
                self._hits += 1
                return row[0]
        # v1 miss → 仅当调用方未指定新维度时, 尝试 v0 fallback
        if prompt_version == "v0" and temperature == 0.0:
            v0_key = self._make_key_v0(model_id, prompt)
            with self._lock:
                cursor = self._conn.execute(
                    "SELECT response FROM llm_cache WHERE cache_key = ?", (v0_key,)
                )
                row = cursor.fetchone()
                if row:
                    # T0.0a: v0 fallback 命中
                    self._v0_hits += 1
                    return row[0]
                self._misses += 1
                return None
        with self._lock:
            self._misses += 1
        return None

    def put(self, model_id: str, prompt: str, response: str,
            *, prompt_version: str = "v0",
            temperature: float = 0.0,
            random_seed: int | None = None) -> None:
        """写入缓存 (Plan-r3 P3-17: 加 prompt_version + temperature 维度)。

        仅在 HTTP 200 成功响应时调用. 使用 INSERT OR REPLACE 确保幂等性.

        Args:
            model_id:        模型标识符.
            prompt:          请求的 prompt 文本.
            response:        API 返回的原始响应文本.
            prompt_version:  prompt 模板版本.
            temperature:     推理温度.
        """
        key = self._make_key(model_id, prompt,
                             prompt_version=prompt_version,
                             temperature=temperature,
                             random_seed=random_seed)
        m_id = str(model_id) if model_id is not None else ""
        r_str = str(response) if response is not None else ""
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO llm_cache (cache_key, model_id, response, created_at) "
                "VALUES (?, ?, ?, ?)",
                (key, m_id, r_str, time.time())
            )
            self._conn.commit()
            self._writes += 1  # T0.0a

    def put_batch(self, model_id: str, prompts: list[str], responses: list[str],
                  *, prompt_version: str = "v0",
                  temperature: float = 0.0,
                  random_seed: int | None = None) -> None:
        """批量原子写入缓存 (Plan-r3 P3-17: 加 prompt_version + temperature 维度)。

        使用 executemany 配合事务大幅提升高并发环境下的写入吞吐量。
        在处理 Batch Embedding (每批数千条) 时可避免频繁的 I/O 锁抢占。

        Args:
            model_id:        模型标识符.
            prompts:         请求的 prompt 列表.
            responses:       API 对应的响应文本列表.
            prompt_version:  prompt 模板版本.
            temperature:     推理温度.
        """
        if not prompts or not responses or len(prompts) != len(responses):
            return

        now = time.time()
        rows = []
        m_id = str(model_id) if model_id is not None else ""
        for p, r in zip(prompts, responses):
            key = self._make_key(model_id, p,
                                 prompt_version=prompt_version,
                                 temperature=temperature,
                                 random_seed=random_seed)
            r_str = str(r) if r is not None else ""
            rows.append((key, m_id, r_str, now))

        with self._lock:
            self._conn.executemany(
                "INSERT OR REPLACE INTO llm_cache (cache_key, model_id, response, created_at) "
                "VALUES (?, ?, ?, ?)",
                rows
            )
            self._conn.commit()
            self._writes += len(rows)  # T0.0a

    def delete(self, model_id: str, prompt: str,
               *, prompt_version: str = "v0",
               temperature: float = 0.0,
               random_seed: int | None = None) -> int:
        """删除指定 (model_id, prompt, ...) 的缓存条目 (v1 + 适用时 v0 fallback)。

        用于**读取侧自愈** (2026-06-23): 当 ``get()`` 命中的响应经上层校验为
        坏条目 (空 / 不可解析 / 缺验证键) 时, 上层 (stage 21 ``fetch_llm_async``
        在线模式) 删除该条目并重新调 API 重取, 让坏缓存自我修复。

        ⚠ 这是对确定性锚点 ``_llm_cache.db`` 的**写 (删) 操作** — 仅应在
        在线重跑、明确要求自愈坏缓存时调用; **离线确定性模式
        (``NEWS_PROCESS_LLM_OFFLINE=1``) 严禁调用本方法** (离线须严格只读,
        保证字节级复现)。删坏条目后, 下次该 (model, prompt) 会 cache miss →
        重新付费调 API → 重写好响应; 这会改变受影响篇目的聚合结果, 须随后
        受控重生 golden (与项目"勿删整库"铁律不冲突: 此处只精准清除坏条目)。

        与 ``get()`` 的 v0 fallback 对称: 当 ``prompt_version == 'v0'`` 且
        ``temperature == 0.0`` 时一并删除 v0 旧 schema 键, 防坏条目藏在 v0
        命名空间躲过删除后又被 ``get`` 的 fallback 命中。

        Args:
            model_id:        模型标识符.
            prompt:          请求的 prompt 文本.
            prompt_version:  prompt 模板版本 (须与写入时一致才能命中删除).
            temperature:     推理温度.
            random_seed:     随机种子 (仅 temperature>0 时进键).

        Returns:
            int: 实际删除的行数 (0 = 未命中任何键, 1 = 删 v1, 最多 2 = v1+v0)。
        """
        keys = [self._make_key(model_id, prompt,
                               prompt_version=prompt_version,
                               temperature=temperature,
                               random_seed=random_seed)]
        if prompt_version == "v0" and temperature == 0.0:
            keys.append(self._make_key_v0(model_id, prompt))
        deleted = 0
        with self._lock:
            for k in keys:
                cursor = self._conn.execute(
                    "DELETE FROM llm_cache WHERE cache_key = ?", (k,)
                )
                if cursor.rowcount and cursor.rowcount > 0:
                    deleted += cursor.rowcount
            self._conn.commit()
        return deleted

    def stats(self) -> dict:
        """返回运行时 hit/miss/write 计数 + 推导的 hit_rate (T0.0a).

        Returns:
            dict: 字段:
                - hits:     v1 schema 命中数 (主路径)
                - v0_hits:  v0 fallback 命中数 (老 cache 兼容路径)
                - misses:   两条路径都 miss 的查询数
                - writes:   put + put_batch 累计写入条数
                - lookups:  hits + v0_hits + misses (所有 get 调用数)
                - hit_rate: (hits + v0_hits) / lookups, 0.0 if lookups==0

        计数器是 process-local in-memory, **不持久化**到 SQLite. 用途是
        每次 run 末尾打一行摘要日志, 帮助定位"为什么这次比上次慢"等问题.
        DB 总条数请用 size().
        """
        with self._lock:
            hits = self._hits
            v0_hits = self._v0_hits
            misses = self._misses
            writes = self._writes
        lookups = hits + v0_hits + misses
        hit_rate = (hits + v0_hits) / lookups if lookups else 0.0
        return {
            'hits': hits,
            'v0_hits': v0_hits,
            'misses': misses,
            'writes': writes,
            'lookups': lookups,
            'hit_rate': hit_rate,
        }

    def size(self) -> int:
        """返回缓存中的总条目数。

        Returns:
            int: 缓存条目数。

        Note:
            这是本模块**唯一**的全表聚合 (``COUNT(*)``), 仅用于 run 末尾打
            统计日志, **不在 get()/put() 热路径上**。情感/embedding 处理逐条
            走主键索引点查, 不依赖本方法, 也不会因库增大而变慢 (见模块
            docstring "查询复杂度与生命周期")。
        """
        with self._lock:
            cursor = self._conn.execute("SELECT COUNT(*) FROM llm_cache")
            return cursor.fetchone()[0]

    def close(self) -> None:
        """关闭数据库连接。"""
        with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None

    def __enter__(self):
        """上下文管理器入口。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出，自动关闭连接。"""
        self.close()
        return False
