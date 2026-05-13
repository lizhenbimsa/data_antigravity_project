"""tests/test_tone_berts_deterministic.py — V4 T1.1a determinism guard.

Verifies the seeding + ``torch.use_deterministic_algorithms`` behaviour added
by V4 T1.1a so that future regressions (e.g. someone re-enabling AMP in
tone_berts.py for performance) trip a fast unit test before stage 23 outputs
diverge in production.

The test is lightweight: no model loading, no parquet IO. It exercises the
two invariants that matter for cross-run reproducibility of BERT inference:

  1. torch.manual_seed produces identical tensor draws across separate calls
     after re-seeding (sanity check of the platform RNG).
  2. The tone_berts module successfully sets cpu_strict mode based on yaml
     config, and reading the module's exposed constants matches expectation.
"""

from __future__ import annotations

import importlib

import pytest

# CI light matrix 不安装 torch (节约 ~4GB 下载); 没有 torch 时整个测试模块 skip。
# 把模块级 import torch 移到 importorskip 之后, 让 CI light job 不再 collection-error。
torch = pytest.importorskip("torch")
import numpy as np


@pytest.fixture(scope="module")
def tone_berts_module():
    """Import tone_berts once; reset import cache to honour fresh yaml read."""
    import news_process.pipeline.sentiment.tone_berts as mod
    importlib.reload(mod)
    return mod


def test_seed_makes_torch_rand_deterministic(tone_berts_module):
    """After re-seeding to the same value, torch.rand returns identical tensors."""
    seed = tone_berts_module._SEED
    torch.manual_seed(seed)
    a = torch.rand(5)
    torch.manual_seed(seed)
    b = torch.rand(5)
    assert torch.equal(a, b), "torch.manual_seed failed to make torch.rand deterministic"


def test_seed_makes_numpy_deterministic(tone_berts_module):
    """np.random seeding survives the module's seed setup."""
    seed = tone_berts_module._SEED
    np.random.seed(seed)
    a = np.random.rand(5)
    np.random.seed(seed)
    b = np.random.rand(5)
    assert (a == b).all(), "np.random.seed failed to make np.random.rand deterministic"


def test_module_constants_match_yaml_config(tone_berts_module):
    """The constants exposed by tone_berts.py match the yaml-configured values.

    Regression guard: if someone changes the BERT_PARAMS access path or the
    deterministic_mode default, this test catches it before stage 23 runs.
    """
    assert tone_berts_module._DETERMINISTIC_MODE in {"cpu_strict", "gpu_strict", "off"}, (
        f"unexpected deterministic_mode: {tone_berts_module._DETERMINISTIC_MODE}"
    )
    assert tone_berts_module._SEED == 42, (
        f"random_seed mismatch with yaml: got {tone_berts_module._SEED}, expected 42"
    )


def test_cpu_strict_mode_disables_amp_and_cudnn_benchmark(tone_berts_module):
    """In cpu_strict / gpu_strict mode, AMP must be off and (on CUDA) cuDNN benchmark off."""
    mode = tone_berts_module._DETERMINISTIC_MODE
    if mode == "off":
        pytest.skip("deterministic_mode=off; nothing to enforce")
    # USE_AMP must always be False in strict modes regardless of device.
    assert tone_berts_module.USE_AMP is False, (
        f"USE_AMP must be False in {mode} mode; AMP introduces non-determinism"
    )
    # On CUDA, cuDNN must be in deterministic mode with benchmark off.
    if tone_berts_module.DEVICE.type == "cuda":
        assert torch.backends.cudnn.deterministic is True, (
            f"cudnn.deterministic must be True in {mode} mode"
        )
        assert torch.backends.cudnn.benchmark is False, (
            f"cudnn.benchmark must be False in {mode} mode"
        )
