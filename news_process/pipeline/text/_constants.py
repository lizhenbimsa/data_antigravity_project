"""stage 25/26 的叶常量模块 (leaf constants, **零 import / 零副作用**)。

⚠ **为何必须单列一个叶模块** (镜像 ``pipeline/preprocess/_constants.py``):
orchestrator 的 ``--skip-unchanged`` 代码版本门
(``run_pipeline_function.STAGE_CODE_VERSION``) 会在**父进程**里
``importlib.import_module(...)`` 本模块以取当前版本号。若把这些常量留在
``article_sbert`` / ``article_staleness`` 里, 父进程的 import 会连带执行:

  ① ``setup_logging(STAGE_NAME, ...)`` —— ``_DelayedTruncatingRotatingHandler``
     按**进程首写**截断, 父进程一写就把该阶段的**生产日志清空** (2026-07-26 实弹:
     我的 A/B 脚本 import ``herd_decay`` 就抹掉了 stage 24 的生产日志);
  ② ``load_config()`` + ``embedding_engine`` import —— 纯无谓开销。

故本模块**只准放字面常量, 严禁任何 import 与任何模块级副作用**。

版本号语义 (供 ``--skip-unchanged`` 判据):
  改动这两个常量 ⟹ 已落盘产物的 ``data_version.code_version`` 与当前值失配
  ⟹ orchestrator reject skip ⟹ 该阶段重跑。凡**改变输出数值**的代码改动都应 bump。
"""
from __future__ import annotations

# ── stage 25 输入构造策略 (SSOT; article_sbert 从此处 import, 勿在别处再定义) ──
# 'whole_text_v2' (现行, 2026-07-26): 整篇 content_{track}, 与 stage 16 逐字节同构。
# 'bybee400_v1'   (退役参照, 一键回退用): 标题(≤100)+首段(≤300) 截断。
INPUT_STRATEGY = 'whole_text_v2'
VALID_STRATEGIES = frozenset({'whole_text_v2', 'bybee400_v1'})

# ⚠ 把策略开关**编进**版本号 —— 二者结构上不可分离: 回退 INPUT_STRATEGY 到
# 'bybee400_v1' 会自动使 code_version 失配 → skip 失效 → 强制重跑。若两者分离,
# 「翻开关 + --skip-unchanged」会静默沿用 v2 旧产物 (silent staleness)。
SBERT_CODE_VERSION = f'sbert-v2:{INPUT_STRATEGY}'

# stage 26 无策略开关; 纯语义版本号, 改测度/改列时手工 bump。
STALENESS_CODE_VERSION = 'staleness-v1'
