"""tests/test_prompt_audit_s3_s10_s13.py — PROMPT_ASSETS_AUDIT 计划批次 D 专属断言
(2026-07-14)。

对应 ``scripts/audit/PROMPT_ASSETS_AUDIT_EXECUTION_PLAN_2026-07-12.md`` §2 表:

  S3  benefit_society.py 冻结 center sidecar 守卫加固 (:521-579 附近)
      —— model_id/anchor_sha256/text_pipeline_version 三字段各自「双方都存在
      且不匹配 → fail-loud」、旧条目缺字段 →「warning + 回填不改 center 值」。
  S10 benefit_society.py `_get_embeddings` (:235-292 附近) 离线闸穿透
      —— NEWS_PROCESS_LLM_OFFLINE 真值时, `_lg` twin 的 except 分支必须
      re-raise (不降级为 None); 在线模式行为不变 (降级+warning)。
  S13 config/benefit_society_placebo_keywords.yaml 「智能柜员机」与
      fintech_dict.json 精确交集裁定 (保留+披露, §4 明确不修清单 #4)
      —— gate 断言交集 ⊆ {'智能柜员机'}, 防词典更新后再漂移而未察觉。

全部 fast / $0 / mock 外部依赖, 不触真实 data/processed 副作用
(OUTPUT_DIR 经 monkeypatch 重定向到 tmp_path; embedding 引擎经 monkeypatch mock)。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.pipeline.features import benefit_society as bs  # noqa: E402

pytestmark = pytest.mark.fast

_REPO = Path(__file__).resolve().parents[1]  # news_process/


# ============================================================================
# S3 — 冻结 center sidecar 守卫三分支
# ============================================================================


class TestS3CenterSidecarGuard:
    """_get_frozen_center: model_id/anchor_sha256/text_pipeline_version 三字段
    各自「双方都存在且不匹配 → fail-loud」+ 旧条目缺字段的「warning + 回填」分支。"""

    @staticmethod
    def _write_sidecar(tmp_path: Path, entry: dict, score_key: str = 'benefit_score_full') -> Path:
        path = tmp_path / '_benefit_center_sidecar.json'
        path.write_text(json.dumps({score_key: entry}, ensure_ascii=False), encoding='utf-8')
        return path

    # ---- (a) 三字段全部匹配 → 正常通过, 返回冻结 center ----
    def test_all_three_fields_match_passes(self, monkeypatch, tmp_path):
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        self._write_sidecar(tmp_path, {
            'center': 0.42,
            'model_id': 'Qwen/Qwen3-Embedding-8B',
            'anchor_sha256': 'sha-abc',
            'text_pipeline_version': 'v1-2026-06-27',
        })
        c = bs._get_frozen_center(
            'benefit_score_full', pd.Series([0.0, 1.0]), 'Qwen/Qwen3-Embedding-8B',
            anchor_sha256='sha-abc', text_pipeline_version='v1-2026-06-27',
        )
        assert c == pytest.approx(0.42)

    # ---- (b) 不匹配 → fail-loud (raise) ----
    def test_anchor_sha256_mismatch_raises(self, monkeypatch, tmp_path):
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        self._write_sidecar(tmp_path, {
            'center': 0.42,
            'model_id': 'm1',
            'anchor_sha256': 'sha-old',
            'text_pipeline_version': 'v1',
        })
        with pytest.raises(ValueError, match='锚点句'):
            bs._get_frozen_center(
                'benefit_score_full', pd.Series([0.0, 1.0]), 'm1',
                anchor_sha256='sha-new', text_pipeline_version='v1',
            )

    def test_text_pipeline_version_mismatch_raises(self, monkeypatch, tmp_path):
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        self._write_sidecar(tmp_path, {
            'center': 0.42,
            'model_id': 'm1',
            'anchor_sha256': 'sha-abc',
            'text_pipeline_version': 'v1-old',
        })
        with pytest.raises(ValueError, match='文本处理管线'):
            bs._get_frozen_center(
                'benefit_score_full', pd.Series([0.0, 1.0]), 'm1',
                anchor_sha256='sha-abc', text_pipeline_version='v2-new',
            )

    def test_model_id_mismatch_still_raises(self, monkeypatch, tmp_path):
        """既有 model_id 分支不因新增两字段而退化。"""
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        self._write_sidecar(tmp_path, {
            'center': 0.42,
            'model_id': 'm-old',
            'anchor_sha256': 'sha-abc',
            'text_pipeline_version': 'v1',
        })
        with pytest.raises(ValueError, match='模型换代'):
            bs._get_frozen_center(
                'benefit_score_full', pd.Series([0.0, 1.0]), 'm-new',
                anchor_sha256='sha-abc', text_pipeline_version='v1',
            )

    # ---- (c) 旧条目缺字段 → warning + 回填, 绝不改 center 值 ----
    def test_legacy_entry_missing_fields_backfills_without_changing_center(
            self, monkeypatch, tmp_path, caplog):
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        sidecar_path = self._write_sidecar(tmp_path, {
            'center': 0.777,
            'model_id': 'm1',
            # 无 anchor_sha256 / text_pipeline_version — 模拟 S3 升级前冻结的旧条目
        })
        import logging
        # bs.logger (= encode.py 的 stage logger) 经 core.logging.setup_logging 设
        # propagate=False (每阶段独立日志文件, 不冒泡到 root) —— caplog 默认挂在 root
        # 上, 故须临时打开 propagate 让本条 WARNING 冒泡到 caplog 的捕获 handler。
        monkeypatch.setattr(bs.logger, 'propagate', True)
        with caplog.at_level(logging.WARNING, logger=bs.logger.name):
            c = bs._get_frozen_center(
                'benefit_score_full', pd.Series([9.0, 9.0]), 'm1',
                anchor_sha256='sha-new', text_pipeline_version='v-new',
            )
        # center 值绝不被改动 (不是按新 scores 重算, 也不是被 fail-loud 崩掉)
        assert c == pytest.approx(0.777)
        assert any('回填' in r.getMessage() for r in caplog.records)
        # 磁盘 sidecar 被原地回填两字段, center 数值原样保留
        reloaded = json.loads(sidecar_path.read_text(encoding='utf-8'))
        entry = reloaded['benefit_score_full']
        assert entry['center'] == pytest.approx(0.777)
        assert entry['anchor_sha256'] == 'sha-new'
        assert entry['text_pipeline_version'] == 'v-new'

    def test_legacy_entry_missing_fields_no_raise_even_if_new_value_given(
            self, monkeypatch, tmp_path):
        """旧条目缺字段场景下, 即使当前调用带了不同的新值, 也只回填不 fail-loud
        (回填分支优先于「双方都存在」比较 — 缺失方视为"尚不可比较", 非"不匹配")。"""
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        self._write_sidecar(tmp_path, {'center': 1.5, 'model_id': 'm1'})
        c = bs._get_frozen_center(
            'benefit_score_full', pd.Series([0.0, 1.0]), 'm1',
            anchor_sha256='sha-anything', text_pipeline_version='v-anything',
        )
        assert c == pytest.approx(1.5)


# ============================================================================
# S10 — 离线闸 RuntimeError 必须穿透 re-raise
# ============================================================================


class TestS10OfflineGateReraise:
    """_get_embeddings: `_lg` twin (API 非 MAIN canonical) 的 except 分支,
    NEWS_PROCESS_LLM_OFFLINE 真值时必须 re-raise, 而非降级为 None。"""

    @staticmethod
    def _fake_lg_spec() -> dict:
        # 非 MAIN canonical (对象身份与 EMBEDDING_CONFIG 不同) 且 base_url 非本地
        # (spec_uses_local 恒 False) —— 确保命中 _get_embeddings 的 try/except 分支
        # 而非 fail-fast 裸路径分支。
        return {'model': 'text-embedding-3-large-test', 'base_url': 'https://example.invalid/v1'}

    def test_offline_env_true_reraises(self, monkeypatch):
        monkeypatch.setenv('NEWS_PROCESS_LLM_OFFLINE', '1')

        def _raise_runtime_error(*args, **kwargs):
            raise RuntimeError("离线确定性模式嵌入缓存 miss (模拟)")

        monkeypatch.setattr(bs._eng, 'embed_texts', _raise_runtime_error)
        with pytest.raises(RuntimeError, match='离线'):
            bs._get_embeddings(['t1'], spec=self._fake_lg_spec())

    def test_offline_env_false_swallows_and_downgrades(self, monkeypatch):
        monkeypatch.delenv('NEWS_PROCESS_LLM_OFFLINE', raising=False)

        def _raise_auth_error(*args, **kwargs):
            raise RuntimeError("401 unauthorized (模拟在线鉴权致命错)")

        monkeypatch.setattr(bs._eng, 'embed_texts', _raise_auth_error)
        result = bs._get_embeddings(['t1'], spec=self._fake_lg_spec())
        assert result is None  # 在线致命错仍走既有降级语义, 不受本次改动影响

    @pytest.mark.parametrize('truthy_val', ['true', 'YES', 'on', '1'])
    def test_offline_env_truthy_variants_reraise(self, monkeypatch, truthy_val):
        monkeypatch.setenv('NEWS_PROCESS_LLM_OFFLINE', truthy_val)

        def _raise_runtime_error(*args, **kwargs):
            raise RuntimeError("离线缓存 miss (模拟)")

        monkeypatch.setattr(bs._eng, 'embed_texts', _raise_runtime_error)
        with pytest.raises(RuntimeError):
            bs._get_embeddings(['t1'], spec=self._fake_lg_spec())


# ============================================================================
# S13 — placebo ∩ fintech_dict 白名单 gate
# ============================================================================


class TestS13PlaceboFintechIntersection:
    """placebo 关键词与 fintech_dict.json 的交集须 ⊆ {'自助银行'} —— 防词典
    /placebo 词表任一方后续更新扩大交集而未被察觉。S13-v2 (2026-07-22, 词典 607 换血
    + 用户授权全项目 607 化): 交集由 {智能柜员机} (已随换血出局) 换为 {自助银行}
    (607 新入词); 裁定镜像 2026-07-14 先例 — 保留交集词 + yaml 头注披露, 不再反复;
    若交集再扩大则须重新走 §2 S13 审计。"""

    _ALLOWED_INTERSECTION = {'自助银行'}

    @staticmethod
    def _load_placebo_keywords() -> set[str]:
        import yaml
        yaml_path = _REPO / 'config' / 'benefit_society_placebo_keywords.yaml'
        with open(yaml_path, encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        kws: set[str] = set()
        for section in ('business_lines', 'neutral_baseline'):
            for bl in (cfg.get(section) or {}).values():
                kws.update(bl.get('keywords') or [])
        return kws

    @staticmethod
    def _load_fintech_dict() -> set[str]:
        dict_path = _REPO / 'config' / 'fintech_dict.json'
        with open(dict_path, encoding='utf-8') as f:
            words = json.load(f)
        return set(words)

    def test_intersection_is_within_whitelist(self):
        placebo_kws = self._load_placebo_keywords()
        fintech_kws = self._load_fintech_dict()
        intersection = placebo_kws & fintech_kws
        assert intersection <= self._ALLOWED_INTERSECTION, (
            f"placebo 关键词与 fintech_dict 交集超出白名单 {self._ALLOWED_INTERSECTION}: "
            f"{intersection - self._ALLOWED_INTERSECTION} — 需重新走 PROMPT_ASSETS_AUDIT "
            "计划 §2 S13 审计 (placebo 方向性可能被污染)。"
        )

    def test_self_service_bank_is_the_documented_single_overlap(self):
        """锁定当前实测交集恰为 1 词 (S13-v2, 2026-07-22: 「自助银行」, 与 yaml 头注
        披露一致); 若变为 0 (词被删) 或新增其他重叠词, 本测试会先于上一条泛化 gate
        精确报警。(旧名 test_smart_teller_machine_*, 随 607 换血更名。)"""
        placebo_kws = self._load_placebo_keywords()
        fintech_kws = self._load_fintech_dict()
        intersection = placebo_kws & fintech_kws
        assert intersection == {'自助银行'}
