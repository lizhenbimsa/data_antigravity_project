"""tests/test_omni_fix_codebook.py — omni 审计修复回归锁 (g-codebook 组, 2026-06-11).

锁定 pipeline/panel/codebook.py + scripts/generate_codebook.py 的修复行为:

  g-codebook-02/-09  LLM 投票阵容 notes 从 config 动态拼接 (Grok-4.1 幻影阵容清除)
  g-codebook-03      attention_index 锚点更正传播到 codebook (Fang & Peress 主锚)
  g-codebook-04/-11  source_stage 错置修正 (attn→Stage 40, network/cent→Stage 40)
  g-codebook-05      track 字段统一 full/ctx 枚举 + 生成期断言
  g-codebook-06/-14  target_bank 取值范围生成时动态 nunique (取代硬编码 '42家')
  g-codebook-01/-08  year 取值范围生成时动态 min–max (取代硬编码 '[2013, 2023]')
  g-codebook-07      scripts/generate_codebook.py 优先读 51_panel_with_controls
  g-codebook-10      13 个 article 级死条目迁出主字典 + 12 个真实 frac 列注册
  g-codebook-12      xlsx 列宽 get_column_letter (chr(64+idx) 26 列上限 latent 崩溃)
  g-codebook-13      *_prob_score_std 取值范围 [0, 0.5] → [0, 1/√2]

全部用合成 DataFrame, 不依赖盘上大数据, 不调外部 API。

# 白话: codebook 是给变量做"说明书"的模块。这组测试确保说明书里不再出现
# 编造的模型名、错误的来源阶段、写死的银行家数/年份范围等错误信息——
# 该动态实测的就动态实测, 对不上的宁可报错也不输出错误文档。
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

from news_process.pipeline.panel import codebook as cb  # noqa: E402

# ============================================================================
# fixtures
# ============================================================================

@pytest.fixture()
def synthetic_panel() -> pd.DataFrame:
    """3 银行 × 2 年合成面板, 含主键 + 一个数值列 + 一个 ctx 列。"""
    banks = ['银行A', '银行B', '银行C']
    rows = []
    for b in banks:
        for y in (2017, 2018):
            rows.append({
                'target_bank': b,
                'year': y,
                'llm_vote_tone_full': 0.1,
                'llm_vote_tone_ctx': -0.2,
            })
    return pd.DataFrame(rows)


# ============================================================================
# g-codebook-02 / -09: LLM 阵容 notes 动态化, Grok 幻影清除
# ============================================================================

class TestLLMLineupNotes:
    def test_no_grok_anywhere_in_metadata(self):
        """全部 curated 元数据任何字段不得再出现幻影模型名。"""
        meta = cb.get_variable_metadata_dict()
        for var, m in meta.items():
            blob = ' '.join(str(v) for v in m.to_dict().values())
            assert 'Grok' not in blob, f'{var} 仍含幻影模型 Grok'
            assert 'GPT-5-nano' not in blob, f'{var} 仍含错误版本名 GPT-5-nano'

    def test_lineup_built_from_config_single_source(self):
        """notes 与 config/sentiment.yaml::tone_llm_processing.models 同源。"""
        meta = cb.get_variable_metadata_dict()
        notes_full = meta['llm_vote_tone_full'].notes
        cfg_models = cb.CONFIG.get('tone_llm_processing', {}).get('models', [])
        if cfg_models:
            for m in cfg_models:
                name = m.get('model_name', m.get('short_name', ''))
                assert name in notes_full, (
                    f'config 模型 {name!r} 未出现在 llm_vote_tone_full notes: {notes_full!r}'
                )
        else:
            # config 缺失时 fallback 必须是真实历史阵容
            for name in ('gpt-5.4-nano', 'gemini-3.1-flash-lite', 'deepseek-v4-flash'):
                assert name in notes_full

    def test_ctx_notes_also_documents_lineup(self):
        meta = cb.get_variable_metadata_dict()
        assert 'deepseek' in meta['llm_vote_tone_ctx'].notes.lower()


# ============================================================================
# g-codebook-03: attention_index 锚点更正 (extensive ≠ Hassan intensive)
# ============================================================================

class TestAttentionAnchor:
    def test_attention_index_reference_leads_with_fang_peress(self):
        meta = cb.get_variable_metadata_dict()
        for col in ('attention_index_full', 'attention_index_ctx'):
            ref = meta[col].reference
            assert ref.startswith('Fang & Peress'), (
                f'{col} reference 应以 Fang & Peress 开头 (extensive 主锚), got {ref!r}'
            )
            assert 'cf. Hassan' in ref, f'{col} 应将 Hassan 降为 cf. 对照: {ref!r}'

    def test_attention_index_notes_disclose_extensive(self):
        meta = cb.get_variable_metadata_dict()
        for col in ('attention_index_full', 'attention_index_ctx'):
            assert 'extensive' in meta[col].description, (
                f'{col} description 应披露 extensive 构念'
            )

    def test_attention_index_ctx_no_hassan_proximity_claim(self):
        """ctx 描述不再以 'Hassan proximity' 锚定 (改为 entity-context 窗口归因)。"""
        meta = cb.get_variable_metadata_dict()
        assert 'Hassan proximity' not in meta['attention_index_ctx'].description

    def test_family_reference_kept_for_intensive_columns(self):
        """pct/density 等 intensive 口径列保留 Hassan 族级首引 (不矫枉过正)。"""
        meta = cb.get_variable_metadata_dict()
        assert meta['attention_pct_full'].reference.startswith('Hassan')


# ============================================================================
# g-codebook-04 / -11: source_stage 错置修正
# ============================================================================

class TestSourceStage:
    def test_infer_attn_no_longer_stage_24(self):
        for col in ('ft_attn_prov', 'ft_attn_city'):
            src = cb._infer_source_stage(col)
            assert src != 'Stage 24', f'{col} 仍错标 Stage 24 (herd_decay)'
            assert 'Stage 40' in src, f'{col} 应标 Stage 40, got {src!r}'

    def test_infer_network_cent_no_longer_stage_46(self):
        for col in ('bank_between_cent', 'network_density'):
            src = cb._infer_source_stage(col)
            assert src != 'Stage 46', f'{col} 仍错标 Stage 46 (现 DAG=stata_export)'
            assert 'Stage 40' in src and 'network_spillover' in src

    def test_bank_degree_cent_curated_stage(self):
        meta = cb.get_variable_metadata_dict()
        src = meta['bank_degree_cent'].source_stage
        assert src != 'Stage 46'
        assert 'Stage 40' in src

    def test_other_infer_mappings_untouched(self):
        """非 attn/network 分支不受影响 (回归保护)。"""
        assert cb._infer_source_stage('llm_foo') == 'Stage 21'
        assert cb._infer_source_stage('bert_foo') == 'Stage 23'
        assert cb._infer_source_stage('jiang_foo') == 'Stage 22'
        assert cb._infer_source_stage('strat_foo') == 'Stage 25'
        assert cb._infer_source_stage('zzz') == '未知'


# ============================================================================
# g-codebook-05: track 编码统一枚举
# ============================================================================

class TestTrackEnum:
    def test_all_curated_tracks_in_allowed_enum(self):
        # v3.9.0 三轨: 直接读 codebook._ALLOWED_TRACKS (含 'ss') 而非硬编码,
        # 让本断言随 _ALLOWED_TRACKS 自维护 (新增 _ss 元数据不再误判为混编)。
        allowed = cb._ALLOWED_TRACKS
        meta = cb.get_variable_metadata_dict()
        bad = {k: v.track for k, v in meta.items()
               if v.track not in allowed}
        assert not bad, f'track 编码混编仍在: {bad}'

    def test_prob_score_entries_use_standard_track(self):
        """prob_score 条目用标准 track 枚举 (原 8 误用中文 '全文'/'上下文')。

        三维对称补全 (2026-06-14): collab 维同 subst/locus 一并断言。"""
        meta = cb.get_variable_metadata_dict()
        assert meta['avg_subst_prob_score_full'].track == 'full'
        assert meta['avg_subst_prob_score_std_full'].track == 'full'
        assert meta['avg_locus_prob_score_ctx'].track == 'ctx'
        assert meta['avg_locus_prob_score_std_ctx'].track == 'ctx'
        assert meta['avg_collab_prob_score_full'].track == 'full'
        assert meta['avg_collab_prob_score_std_ctx'].track == 'ctx'

    def test_single_text_specs_use_empty_not_dash(self):
        """_SINGLE_TEXT_SPECS 的 track-agnostic 空值统一 '' (原 '—')。"""
        meta = cb.get_variable_metadata_dict()
        for col in ('frac_front_page', 'wire_frac', 'coverage_continuity'):
            assert meta[col].track == '', f'{col} track 应为空串, got {meta[col].track!r}'

    def test_generate_codebook_raises_on_illegal_track(self, tmp_path, monkeypatch,
                                                       synthetic_panel):
        """生成期断言: 非法 track 值 fail-loud 而非静默进产物。"""
        bad_meta = {'llm_vote_tone_full': cb.VariableMetadata(
            var_name='llm_vote_tone_full', label='x', track='全文')}
        monkeypatch.setattr(cb, 'get_variable_metadata_dict', lambda: bad_meta)
        with pytest.raises(ValueError, match='track 编码非法'):
            cb.generate_codebook(synthetic_panel, str(tmp_path), formats=['json'])


# ============================================================================
# g-codebook-06 / -14 / -01 / -08: 主键取值范围动态实测
# ============================================================================

class TestDynamicKeyRanges:
    def test_static_fallback_no_hardcoded_42(self):
        meta = cb.get_variable_metadata_dict()
        assert '42家' not in meta['target_bank'].value_range
        assert '[2013, 2023]' not in meta['year'].value_range

    def test_generated_codebook_uses_actual_nunique_and_year_span(
            self, tmp_path, synthetic_panel):
        out = cb.generate_codebook(synthetic_panel, str(tmp_path), formats=['json'])
        rows = json.loads(Path(out['json']).read_text(encoding='utf-8'))
        by_name = {r['变量名']: r for r in rows}
        assert by_name['target_bank']['取值范围'].startswith('3家商业银行'), (
            f"target_bank 取值范围未动态实测: {by_name['target_bank']['取值范围']!r}"
        )
        assert by_name['year']['取值范围'].startswith('[2017, 2018]'), (
            f"year 取值范围未动态实测: {by_name['year']['取值范围']!r}"
        )

    def test_dynamic_range_tracks_panel_changes(self, tmp_path, synthetic_panel):
        """换一个 5 银行 / 2019–2021 的 panel → 取值范围跟着变 (非缓存/硬编码)。"""
        panel = pd.DataFrame({
            'target_bank': [f'行{i}' for i in range(5) for _ in (0, 1, 2)],
            'year': [2019, 2020, 2021] * 5,
        })
        out = cb.generate_codebook(panel, str(tmp_path), formats=['json'])
        rows = json.loads(Path(out['json']).read_text(encoding='utf-8'))
        by_name = {r['变量名']: r for r in rows}
        assert by_name['target_bank']['取值范围'].startswith('5家商业银行')
        assert by_name['year']['取值范围'].startswith('[2019, 2021]')


# ============================================================================
# g-codebook-10: 13 个 article 级死条目迁出 + 真实 frac 列注册
# ============================================================================

_ARTICLE_LEVEL_13 = [
    'innovation_locus_full', 'innovation_locus_ctx',
    'innovation_substantiveness_full', 'innovation_substantiveness_ctx',
    'innovation_collab_mode_full', 'innovation_collab_mode_ctx',
    'innovation_collab_mode_confidence_full', 'innovation_collab_mode_confidence_ctx',
    'category_confidence_full', 'category_confidence_ctx',
    'llm_verified_dual_full_only', 'llm_verified_dual_ctx_only',
    'llm_verified_dual_both',
]

_REAL_FRAC_12 = [
    'tech_frac', 'app_frac', 'tech_frac_lc', 'app_frac_lc',
    'sub_frac', 'symb_frac', 'sub_frac_sc', 'symb_frac_sc',
    'indep_frac', 'collab_frac', 'indep_frac_cm', 'collab_frac_cm',
]


class TestArticleLevelSplit:
    def test_13_dead_entries_moved_out_of_panel_dict(self):
        panel_meta = cb.get_variable_metadata_dict()
        for col in _ARTICLE_LEVEL_13:
            assert col not in panel_meta, (
                f'{col} 是 article 级列名 (永不进 panel codebook), 不应留在主字典'
            )

    def test_article_level_dict_preserves_all_13(self):
        art = cb.get_article_level_metadata_dict()
        assert sorted(art) == sorted(_ARTICLE_LEVEL_13)

    def test_article_label_value_range_is_string_enum_not_01(self):
        """article 级 parquet 实存中文标签字符串, 0/1 编码仅发生在 stata_export 下游。"""
        art = cb.get_article_level_metadata_dict()
        vr = art['innovation_locus_full'].value_range
        assert '底层技术' in vr and '应用场景' in vr
        assert not vr.startswith('0 ('), f'仍声称 0|1 编码: {vr!r}'
        vr_sub = art['innovation_substantiveness_ctx'].value_range
        assert '实质性' in vr_sub and '象征性' in vr_sub

    def test_real_panel_frac_columns_registered(self):
        panel_meta = cb.get_variable_metadata_dict()
        for col in _REAL_FRAC_12:
            assert col in panel_meta, f'panel 真实聚合列 {col} 未注册 curated 条目'
            m = panel_meta[col]
            assert m.value_range == '[0, 1] ∪ NaN'
            assert m.track in ('full', 'ctx')
            assert m.reference, f'{col} 引文为空'

    def test_frac_denominator_track_consistent(self):
        """ctx 对角线 frac 必须用 ctx 分母 (metric-audit 2026-06-02 final 行为)。"""
        panel_meta = cb.get_variable_metadata_dict()
        for col in ('tech_frac_lc', 'sub_frac_sc', 'indep_frac_cm'):
            assert 'n_articles_llm_valid_ctx' in panel_meta[col].formula
        for col in ('tech_frac', 'sub_frac', 'indep_frac'):
            f = panel_meta[col].formula
            assert 'n_articles_llm_valid' in f and '_ctx' not in f


# ============================================================================
# g-codebook-12: xlsx 列宽 >26 列不崩 (get_column_letter)
# ============================================================================

class TestExcelColumnLetter:
    def test_excel_export_survives_more_than_26_columns(self, tmp_path, monkeypatch,
                                                        synthetic_panel):
        """伪造 20 个额外统计字段 → codebook_df 32 列 > 26;
        旧 chr(64+idx) 在 idx=27 产生非法列名 '[' 崩溃, 修后必须成功。"""
        real_stats = cb.extract_variable_stats

        def fat_stats(panel, var_name):
            stats = real_stats(panel, var_name)
            stats.update({f'extra_stat_{i:02d}': float(i) for i in range(20)})
            return stats

        monkeypatch.setattr(cb, 'extract_variable_stats', fat_stats)
        out = cb.generate_codebook(synthetic_panel, str(tmp_path), formats=['excel'])
        assert Path(out['excel']).exists()
        # 读回验证列数确实越过 26 边界 (确认本测试真的踩到了旧 bug 的触发面)
        df = pd.read_excel(out['excel'])
        assert len(df.columns) > 26


# ============================================================================
# g-codebook-13: prob_score_std 取值范围上界
# ============================================================================

class TestProbScoreStdRange:
    def test_range_no_longer_claims_half(self):
        meta = cb.get_variable_metadata_dict()
        for col in ('avg_subst_prob_score_std_full', 'avg_subst_prob_score_std_ctx',
                    'avg_locus_prob_score_std_full', 'avg_locus_prob_score_std_ctx',
                    'avg_collab_prob_score_std_full', 'avg_collab_prob_score_std_ctx'):
            vr = meta[col].value_range
            assert vr != '[0, 0.5]', f'{col} 仍声称越界旧范围 [0, 0.5]'
            assert '0.7071' in vr or '1/√2' in vr, (
                f'{col} 应声称 ddof=1 样本 SD 上确界 1/√2: {vr!r}'
            )

    def test_observed_overflow_value_within_new_bound(self):
        """盘上实测 0.5292 必须落在新声称范围内 (旧范围 0.5 已被实测推翻)。"""
        assert 0.5292 <= 2 ** -0.5 + 1e-12

    def test_notes_disclose_ddof1_sup(self):
        meta = cb.get_variable_metadata_dict()
        assert 'ddof=1' in meta['avg_locus_prob_score_std_full'].notes


# ============================================================================
# g-codebook-07: scripts/generate_codebook.py 面板源 51 优先 / 40 回退
# ============================================================================

class TestScriptPanelSource:
    @staticmethod
    def _write_panels(tmp_path: Path, with_51: bool) -> None:
        panel40 = pd.DataFrame({
            'target_bank': ['银行A', '银行B'],
            'year': [2017, 2018],
        })
        panel40.to_parquet(tmp_path / '40_panel_yearly.parquet')
        if with_51:
            panel51 = panel40.copy()
            panel51['only_in_51_controls'] = 1.0
            panel51.to_parquet(tmp_path / '51_panel_with_controls.parquet')

    @staticmethod
    def _patch_config(monkeypatch, mod, tmp_path: Path) -> None:
        cfg_paths = dict(mod.CONFIG.get('paths', {}))
        cfg_paths['output_dir'] = str(tmp_path)
        monkeypatch.setitem(mod.CONFIG, 'paths', cfg_paths)
        monkeypatch.setitem(mod.CONFIG, 'filenames', {
            'output_51_panel_controls': '51_panel_with_controls.parquet',
            'output_40_panel_yearly': '40_panel_yearly.parquet',
        })

    def _load_script_module(self):
        import importlib
        return importlib.import_module('news_process.scripts.generate_codebook')

    def test_prefers_51_panel_when_present(self, tmp_path, monkeypatch):
        mod = self._load_script_module()
        self._write_panels(tmp_path, with_51=True)
        self._patch_config(monkeypatch, mod, tmp_path)
        assert mod.main() == 0
        rows = json.loads(
            (tmp_path / 'variable_codebook.json').read_text(encoding='utf-8'))
        names = {r['变量名'] for r in rows}
        assert 'only_in_51_controls' in names, (
            '存在 51 面板时应以其为源 (codebook 须含 51-only 列)'
        )

    def test_falls_back_to_40_panel(self, tmp_path, monkeypatch):
        mod = self._load_script_module()
        self._write_panels(tmp_path, with_51=False)
        self._patch_config(monkeypatch, mod, tmp_path)
        assert mod.main() == 0
        rows = json.loads(
            (tmp_path / 'variable_codebook.json').read_text(encoding='utf-8'))
        names = {r['变量名'] for r in rows}
        assert 'only_in_51_controls' not in names
        assert 'target_bank' in names

    def test_errors_when_no_panel_exists(self, tmp_path, monkeypatch):
        mod = self._load_script_module()
        self._patch_config(monkeypatch, mod, tmp_path)
        assert mod.main() == 1


# ============================================================================
# 端到端 sanity: 全 4 格式生成不崩 + 行数 = panel 列数
# ============================================================================

def test_generate_codebook_all_formats_end_to_end(tmp_path, synthetic_panel):
    out = cb.generate_codebook(synthetic_panel, str(tmp_path))
    assert set(out) == {'excel', 'csv', 'markdown', 'json'}
    for p in out.values():
        assert Path(p).exists()
    rows = json.loads(Path(out['json']).read_text(encoding='utf-8'))
    # 每个 panel 列恰好一行 — 无幻影行 (列不在 panel 则不发射) 的结构性保证
    assert len(rows) == len(synthetic_panel.columns)


# ============================================================================
# toptier-audit D4-1 / F5 (2026-06-13): attention_attr_share 公式 codebook 端锁
# ============================================================================

def test_attr_share_formula_synced_to_live_estimator():
    """codebook attention_attr_share 公式须为撤回 clip 后的有界 share
    Σctx/(Σctx+Σfull), 防 codebook 端静默回退旧 clip 删失版 (源端
    attention_media 已有锁, codebook 端此前无锁 → F5 补)。"""
    meta = cb.get_variable_metadata_dict()['attention_attr_share']
    f = meta.formula
    assert 'Σ_d ctx + Σ_d full' in f, \
        f'attr_share 公式应为 Σctx/(Σctx+Σfull) 有界 share, got: {f!r}'
    # 撤回的 clip 删失版不得作为活公式 (仅可出现在解释性注释, 不在 formula 字段)
    assert 'clip(' not in f, f'attr_share formula 不得含已撤回的 clip 删失构造: {f!r}'
    assert meta.value_range == '[0, 1]'
