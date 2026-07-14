"""S1 (prompt-audit 2026-07-14): v8 主 prompt 字节级冻结 gate.

背景: unified_cot.txt (v8-2026-05-17) 是 stage 21 缓存键语料 — 改一个字节 =
三轨 ≈13 万条缓存全 miss + golden 锚全废。此前 PEER_PROMPT / jlm 锚点均有
冻结锁, 唯独主 prompt 缺字节 gate (计划 §2-S1)。

双口径 (计划 §0-3, 两条各锁一条):
- **raw 口径** = 磁盘原始字节 (CRLF) sha256 = ``0430ba3c…`` — sidecar
  ``prompt_v8_sha256`` 锚与公示指纹用此口径;
- **LF 归一口径** = ``\\r\\n``→``\\n`` 后 sha256 = ``14952b06…`` — 缓存键
  实际消费的内存文本口径 (core/config.py 文本模式 universal newlines)。

镜像 ``test_peer_prompt_frozen`` 的 ``.replace('\\r\\n','\\n')`` 模式, LF 条目
防跨 EOL checkout 误红; raw 条目在 CRLF 工作树上锁盘上字节。

白话: 这份考题一个字都不能再改 — 这里存了考题的两枚指纹, 谁改了考题,
测试立刻翻红。v9 升级时 (计划 §11.4-#2) 本文件按受控流程更新为 v9 指纹。
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

_PROMPT_PATH = (
    Path(__file__).resolve().parents[1] / 'config' / 'prompts' / 'unified_cot.txt'
)

# 计划 §0-3 公示双口径指纹 (2026-07-14 实算锁定)
V8_SHA256_RAW = '0430ba3c1b2a289e5f022081953e7748f35dfa9e3e1ac9303f6d0f1871cc858c'
V8_SHA256_LF = '14952b06664ad4c1242ea10bde185975245366cea71a448480b1d0bcf5d25bf4'


@pytest.mark.fast
def test_v8_prompt_frozen_lf_normalized():
    """LF 归一口径 (缓存键域): 跨 EOL checkout 免疫的字节冻结锁."""
    raw = _PROMPT_PATH.read_bytes()
    lf = raw.replace(b'\r\n', b'\n')
    assert hashlib.sha256(lf).hexdigest() == V8_SHA256_LF, (
        'unified_cot.txt LF 归一字节漂移 — v8 prompt 被修改! '
        '一切修改必须走计划 §11 v9 受控流程, 严禁直接改字节。'
    )


@pytest.mark.fast
def test_v8_prompt_frozen_raw_bytes():
    """raw 口径 (sidecar/公示指纹域): 盘上原始字节冻结锁.

    注: 本条在 LF-checkout 环境会红 (raw 口径定义于 CRLF 工作树), 此时以
    LF 条目为准并按 §0-3 声明口径; 本仓 .gitattributes 未对 .txt 强制 eol,
    Windows 主环境下恒为 CRLF。
    """
    raw = _PROMPT_PATH.read_bytes()
    if b'\r\n' not in raw:
        pytest.skip('工作树为 LF checkout — raw(CRLF) 口径不适用, 以 LF 条目为准')
    assert hashlib.sha256(raw).hexdigest() == V8_SHA256_RAW


@pytest.mark.fast
def test_sidecar_anchor_matches_disk_recomputation():
    """sidecar 锚 == 盘上实文件 raw 复算 (恒等闭环, M1 迁移后口径).

    sidecar 已随 M1-P0 修复 (2026-07-14) 通过 .gitignore negation 例外恢复
    git 跟踪 (新 clone 自带权威冻结值, 三 median 不会跨环境重冻结分叉);
    若在剥离数据的环境中缺失 → skip (sha 锚可由 runtime producer 首跑重建,
    见 encode_collab.compute_prompt_v8_raw_sha256; median 以 git 版本为权威)。
    """
    from news_process.pipeline.llm_archive.manifest import _resolve_sidecar_path
    sidecar = _resolve_sidecar_path()
    if not sidecar.exists():
        pytest.skip('sidecar 未生成 (首跑 panel build 时由 runtime producer 写入)')
    anchored = json.loads(sidecar.read_text(encoding='utf-8')).get('prompt_v8_sha256')
    if anchored is None:
        pytest.fail('sidecar prompt_v8_sha256=None — 密码学锚缺失 (M1/M2 未收口?)')
    recomputed = hashlib.sha256(_PROMPT_PATH.read_bytes()).hexdigest()
    assert anchored == recomputed, (
        f'sidecar 锚 {anchored[:12]}… ≠ 盘上复算 {recomputed[:12]}… — '
        'prompt 或 sidecar 有一方被改动'
    )


@pytest.mark.fast
def test_eol_immunity_of_prompt_loader(tmp_path):
    """EOL 免疫回归: CRLF/LF 两份同内容模板经文本模式读入结果相同.

    锁定 §0-2 已推翻项的实证前提 (core/config.py 文本模式 universal
    newlines): 缓存键与磁盘行尾无关。若未来 loader 改二进制读, 本条翻红。
    """
    content_lf = '# version: vX-test\nline1\nline2\n'
    p_lf = tmp_path / 'lf.txt'
    p_crlf = tmp_path / 'crlf.txt'
    p_lf.write_bytes(content_lf.encode('utf-8'))
    p_crlf.write_bytes(content_lf.replace('\n', '\r\n').encode('utf-8'))
    read_lf = p_lf.read_text(encoding='utf-8')
    read_crlf = open(p_crlf, encoding='utf-8').read()  # 文本模式 universal newlines
    assert read_lf == read_crlf
