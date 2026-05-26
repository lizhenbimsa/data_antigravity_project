"""tests/test_llm_archive.py — v3.7.0 LLM Archive 单元测试.

V4 audit V6 verification 必修, 验证 reproducibility 强约束:
1. Append-only 写入正确
2. Manifest sha256 + byte count 准确
3. verify_manifest 正确检测篡改
4. 必填字段缺失 raise ValueError
"""
from __future__ import annotations

import json

import pytest

from news_process.pipeline.llm_archive import (
    LLMArchive,
    archive_record,
    compute_manifest,
    verify_manifest,
)
from news_process.pipeline.llm_archive.archive import sha256_of_file
from news_process.pipeline.llm_archive.manifest import write_manifest


@pytest.fixture
def tmp_archive(tmp_path):
    """每个 test 一个独立 archive 根目录."""
    return LLMArchive(root=tmp_path / 'llm_archive')


def _valid_record() -> dict:
    """构造一条合法 record (V4 F-P2.1 全字段)."""
    return {
        'cache_key': 'abc123' * 10,
        'model_id': 'gpt-5.4-nano',
        'model_version': 'gpt-5.4-nano-2026-01',
        'prompt_version': 'v8',
        'temperature': 0.0,
        'prompt': '这家银行的金融科技投入如何?',
        'response_raw': '{"choices":[{"message":{"content":"正面"}}]}',
        'api_endpoint': 'https://api.yunwu.ai/v1/chat/completions',
        'http_status': 200,
    }


class TestAppendOnly:
    """LLMArchive append-only 写入正确性."""

    def test_append_returns_request_id(self, tmp_archive):
        rid = tmp_archive.append(_valid_record())
        assert isinstance(rid, str)
        assert len(rid) == 36  # UUID v4 length

    def test_append_creates_jsonl(self, tmp_archive):
        tmp_archive.append(_valid_record())
        files = list(tmp_archive.responses_dir.glob('*.jsonl'))
        assert len(files) == 1

    def test_multiple_appends_one_file(self, tmp_archive):
        """同日多次 append → 单文件 (按日切分)."""
        for _ in range(5):
            tmp_archive.append(_valid_record())
        files = list(tmp_archive.responses_dir.glob('*.jsonl'))
        assert len(files) == 1
        with files[0].open(encoding='utf-8') as f:
            lines = f.readlines()
        assert len(lines) == 5

    def test_records_are_unique_uuid(self, tmp_archive):
        rids = [tmp_archive.append(_valid_record()) for _ in range(10)]
        assert len(set(rids)) == 10

    def test_missing_required_field_raises(self, tmp_archive):
        rec = _valid_record()
        del rec['model_version']  # V4 critical 字段
        with pytest.raises(ValueError, match='缺必填字段'):
            tmp_archive.append(rec)


class TestArchiveRecord:
    """archive_record 便捷函数."""

    def test_basic_call(self, tmp_archive):
        rid = archive_record(
            cache_key='key1',
            model_id='gpt-5.4-nano',
            model_version='gpt-5.4-nano-2026-01',
            prompt='hi',
            response_raw='{}',
            archive=tmp_archive,
        )
        assert isinstance(rid, str)

    def test_http_headers_optional(self, tmp_archive):
        """默认 http_headers=None 不写入字段."""
        rid = archive_record(
            cache_key='key1',
            model_id='m',
            model_version='v',
            prompt='p',
            response_raw='r',
            archive=tmp_archive,
        )
        files = list(tmp_archive.responses_dir.glob('*.jsonl'))
        with files[0].open(encoding='utf-8') as f:
            rec = json.loads(f.readline())
        assert 'http_headers' not in rec

    def test_http_headers_included(self, tmp_archive):
        rid = archive_record(
            cache_key='key1',
            model_id='m',
            model_version='v',
            prompt='p',
            response_raw='r',
            http_headers={'x-request-id': 'foo'},
            archive=tmp_archive,
        )
        files = list(tmp_archive.responses_dir.glob('*.jsonl'))
        with files[0].open(encoding='utf-8') as f:
            rec = json.loads(f.readline())
        assert rec['http_headers']['x-request-id'] == 'foo'


class TestManifest:
    """Manifest 生成 / 验证."""

    def test_compute_empty_archive(self, tmp_archive):
        manifest = compute_manifest(tmp_archive.root)
        assert manifest['total_records'] == 0
        assert manifest['files'] == {}

    def test_compute_with_records(self, tmp_archive):
        for _ in range(3):
            tmp_archive.append(_valid_record())
        manifest = compute_manifest(tmp_archive.root)
        assert manifest['total_records'] == 3
        assert len(manifest['files']) == 1
        first_file = list(manifest['files'].values())[0]
        assert first_file['record_count'] == 3
        assert len(first_file['sha256']) == 64

    def test_write_and_verify_round_trip(self, tmp_archive):
        for _ in range(2):
            tmp_archive.append(_valid_record())
        write_manifest(tmp_archive.root)
        ok, errors = verify_manifest(tmp_archive.root)
        assert ok, f"verify failed: {errors}"

    def test_verify_detects_tampering(self, tmp_archive):
        """篡改 jsonl 后 verify 必须 fail."""
        tmp_archive.append(_valid_record())
        write_manifest(tmp_archive.root)

        # 篡改: append 一行 (sha256 + bytes 都变)
        files = list(tmp_archive.responses_dir.glob('*.jsonl'))
        with files[0].open('a', encoding='utf-8') as f:
            f.write('{"tampered":true}\n')

        ok, errors = verify_manifest(tmp_archive.root)
        assert not ok
        assert any('SHA-256 mismatch' in e or 'Byte count mismatch' in e for e in errors)

    def test_verify_detects_missing_file(self, tmp_archive):
        tmp_archive.append(_valid_record())
        write_manifest(tmp_archive.root)
        files = list(tmp_archive.responses_dir.glob('*.jsonl'))
        files[0].unlink()
        ok, errors = verify_manifest(tmp_archive.root)
        assert not ok
        assert any('文件缺失' in e for e in errors)

    # quality-hardening Round 4 (2026-05-27): manifest.py 91.25% -> ~100%
    # missing 78-79 / 109 / 114-115 / 162 / 195
    def test_compute_when_responses_dir_missing_returns_empty_files(self, tmp_path, caplog):
        """compute_manifest 在 root/responses 不存在时 → files={} + warning (lines 78-79)."""
        from news_process.pipeline.llm_archive.manifest import compute_manifest
        root = tmp_path / 'archive_no_resp'
        root.mkdir()  # root 存在但 responses 子目录不存在
        import logging
        caplog.set_level(logging.WARNING, logger='news_process.pipeline.llm_archive.manifest')
        m = compute_manifest(root)
        assert m['files'] == {}
        assert m['total_records'] == 0

    def test_read_prompt_version_anchor_sidecar_missing_returns_none(self, tmp_path, monkeypatch):
        """sidecar 不存在 → None (manifest.py:109)."""
        from news_process.pipeline.llm_archive import manifest as M
        monkeypatch.chdir(tmp_path)  # cwd 切到无 data/processed/v3_5_1_constants.json 的临时目录
        assert M._read_prompt_version_anchor_from_sidecar() is None

    def test_read_prompt_version_anchor_corrupt_json_returns_none(self, tmp_path, monkeypatch):
        """sidecar JSON 损坏 → except → None (manifest.py:114-115)."""
        from news_process.pipeline.llm_archive import manifest as M
        sidecar_dir = tmp_path / 'data' / 'processed'
        sidecar_dir.mkdir(parents=True)
        (sidecar_dir / 'v3_5_1_constants.json').write_text(
            'NOT JSON {{{{', encoding='utf-8')
        monkeypatch.chdir(tmp_path)
        assert M._read_prompt_version_anchor_from_sidecar() is None

    def test_verify_manifest_missing_returns_false(self, tmp_path):
        """manifest.json 本身不存在 → False + 单条错误 (manifest.py:162)."""
        from news_process.pipeline.llm_archive.manifest import verify_manifest
        root = tmp_path / 'archive_no_manifest'
        root.mkdir()
        ok, errors = verify_manifest(root)
        assert ok is False
        assert len(errors) == 1
        assert 'manifest 不存在' in errors[0]

    def test_verify_detects_unregistered_extra_jsonl(self, tmp_archive):
        """manifest 外的 jsonl 文件 → 报错 '未登记文件' (manifest.py:195)."""
        from news_process.pipeline.llm_archive.manifest import verify_manifest
        tmp_archive.append(_valid_record())
        write_manifest(tmp_archive.root)
        # 注入一个 manifest 外的 rogue jsonl
        rogue = tmp_archive.responses_dir / 'rogue_2099-12-31.jsonl'
        rogue.write_text('{"rogue":true}\n', encoding='utf-8')
        ok, errors = verify_manifest(tmp_archive.root)
        assert not ok
        assert any('未登记文件' in e for e in errors)


class TestSha256OfFile:
    """sha256_of_file 工具函数."""

    def test_deterministic(self, tmp_path):
        fp = tmp_path / 'foo.txt'
        fp.write_text('hello world', encoding='utf-8')
        h1 = sha256_of_file(fp)
        h2 = sha256_of_file(fp)
        assert h1 == h2
        # SHA-256("hello world") 已知值
        assert h1 == 'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'


# pytest 标记 (CI light tier, 与 v3.5.1 测试矩阵兼容)
pytestmark = [pytest.mark.fast]
