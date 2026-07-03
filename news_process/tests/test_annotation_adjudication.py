"""G-2 gate — 双编码合并 + 第三编码员仲裁工作流回归锁 (WP-C, 2026-07-03)。

锁定四象限合并真值表与哨兵语义:
  A=B (双合法)      → 共识值
  A≠B ∧ C 有值      → C 裁决 (仅 --with-adjudication; 主口径)
  A≠B ∧ C 空        → 哨兵 -1 / '待仲裁' 保持 (下限回退, stage 63 语义不变)
  任一缺失          → NaN (不判)
strict 剔除口径永远保留于 最终_*_strict; 已填 C 的仲裁工作台不得被覆盖。
"""
import pandas as pd

from news_process.validation import llms_human


def _write_blind_pair(tmp_path):
    """8 行四象限样例: 行3=验证分歧, 行4=A缺失, 行5=情感分歧, 行7=情感双缺。"""
    base = str(tmp_path / '61_human_samples.xlsx')
    paths = llms_human.derive_blind_paths(base)
    n = 8
    ctx = {'_row_uid': list(range(n)), 'docid': [i // 2 for i in range(n)],
           '标题': [f't{i}' for i in range(n)], '内容': ['c'] * n}
    pd.DataFrame({**ctx,
                  '编码者A_验证': [1, 1, 0, 1, None, 1, 1, 1],
                  '编码者A_情感': ['正面', '中性', '中性', '正面', '正面', '正面', '中性', None],
                  }).to_excel(paths['blind_A'], sheet_name='验证数据', index=False)
    pd.DataFrame({**ctx,
                  '编码者B_验证': [1, 1, 0, 0, 1, 1, 1, 1],
                  '编码者B_情感': ['正面', '中性', '中性', '正面', '正面', '负面', '中性', None],
                  }).to_excel(paths['blind_B'], sheet_name='验证数据', index=False)
    return base, paths


def _merged(path):
    return pd.read_excel(path).sort_values('_row_uid').reset_index(drop=True)


class TestMergeQuadrants:
    def test_consensus_sentinel_strict_and_pending(self, tmp_path):
        base, paths = _write_blind_pair(tmp_path)
        out = str(tmp_path / 'merged.xlsx')
        llms_human.merge_annotations(base, out)
        m = _merged(out)
        # 象限 1: A=B → 共识
        assert m.loc[0, '最终_验证'] == 1
        assert m.loc[2, '最终_验证'] == 0
        assert m.loc[0, '最终_情感'] == '正面'
        # 象限 2: 分歧 → 哨兵
        assert m.loc[3, '最终_验证'] == -1
        assert m.loc[5, '最终_情感'] == '待仲裁'
        # 象限 3: 任一缺失 → 不判
        assert pd.isna(m.loc[4, '最终_验证'])
        assert pd.isna(m.loc[7, '最终_情感'])
        # strict 口径镜像 (仲裁前恒等)
        assert m.loc[3, '最终_验证_strict'] == -1
        assert m.loc[5, '最终_情感_strict'] == '待仲裁'
        assert m.loc[0, '最终_验证_strict'] == 1
        # 待仲裁工作台: 仅分歧行, 含 C 两列, 零机器列
        pend = pd.read_excel(paths['pending'])
        assert set(pend['_row_uid']) == {3, 5}
        assert '编码者C_验证' in pend.columns and '编码者C_情感' in pend.columns
        assert not any('LLM' in str(c) or '词典' in str(c) for c in pend.columns)

    def test_adjudication_overrides_primary_keeps_strict(self, tmp_path):
        base, paths = _write_blind_pair(tmp_path)
        out = str(tmp_path / 'merged.xlsx')
        llms_human.merge_annotations(base, out)
        # 仲裁人裁决行3 验证=1; 行5 情感刻意留空 (→ 保持哨兵)
        pend = pd.read_excel(paths['pending'])
        pend.loc[pend['_row_uid'] == 3, '编码者C_验证'] = 1
        pend.to_excel(paths['pending'], index=False)
        llms_human.merge_annotations(base, out, with_adjudication=True)
        m = _merged(out)
        assert m.loc[3, '最终_验证'] == 1, 'C 裁决须并入主口径'
        assert m.loc[3, '最终_验证_strict'] == -1, 'strict 剔除口径不得被仲裁污染'
        assert m.loc[5, '最终_情感'] == '待仲裁', 'C 空 → 下限回退哨兵'
        assert m.loc[5, '最终_情感_strict'] == '待仲裁'

    def test_pending_with_c_values_not_overwritten(self, tmp_path):
        base, paths = _write_blind_pair(tmp_path)
        out = str(tmp_path / 'merged.xlsx')
        llms_human.merge_annotations(base, out)
        pend = pd.read_excel(paths['pending'])
        pend.loc[pend['_row_uid'] == 3, '编码者C_验证'] = 1
        pend.to_excel(paths['pending'], index=False)
        # 再跑默认 merge — 已填 C 的仲裁台必须原样保留 (人工劳动不可再生)
        llms_human.merge_annotations(base, out)
        pend2 = pd.read_excel(paths['pending'])
        filled = pd.to_numeric(
            pend2.loc[pend2['_row_uid'] == 3, '编码者C_验证'], errors='coerce')
        assert (filled == 1).all(), '已填 C 判定被覆盖销毁'

    def test_row_uid_mismatch_refuses_merge(self, tmp_path):
        base, paths = _write_blind_pair(tmp_path)
        db = pd.read_excel(paths['blind_B'], sheet_name='验证数据').iloc[:-1]
        db.to_excel(paths['blind_B'], sheet_name='验证数据', index=False)
        out = str(tmp_path / 'merged.xlsx')
        llms_human.merge_annotations(base, out)
        import os
        assert not os.path.exists(out), '_row_uid 漂移时必须拒绝合并 (fail-loud)'
