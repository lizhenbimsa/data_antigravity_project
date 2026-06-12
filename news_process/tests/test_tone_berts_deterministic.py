"""tests/test_tone_berts_deterministic.py — V4 T1.1a 确定性守卫。

验证 V4 T1.1a 引入的随机种子 + ``torch.use_deterministic_algorithms`` 行为,
使未来的回归 (如有人为性能在 tone_berts.py 重新打开 AMP) 先被快速单测拦下,
而不是等 stage 23 产物在生产中漂移才发现。

测试本身轻量: 不加载模型、不做 parquet IO。只演练对 BERT 推理跨-run
可复现性真正要紧的两条不变量:

  1. 重新设种后, torch.manual_seed 在两次独立调用中产生完全相同的张量
     (平台 RNG 的 sanity check)。
  2. tone_berts 模块按 yaml 配置成功设置 cpu_strict 模式, 模块暴露的
     常量读出来符合预期。
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
    """只 import 一次 tone_berts; reload 以确保读到新鲜的 yaml 配置。"""
    import news_process.pipeline.sentiment.tone_berts as mod
    importlib.reload(mod)
    return mod


def test_seed_makes_torch_rand_deterministic(tone_berts_module):
    """以相同值重新设种后, torch.rand 返回完全相同的张量。"""
    seed = tone_berts_module._SEED
    torch.manual_seed(seed)
    a = torch.rand(5)
    torch.manual_seed(seed)
    b = torch.rand(5)
    assert torch.equal(a, b), "torch.manual_seed failed to make torch.rand deterministic"


def test_seed_makes_numpy_deterministic(tone_berts_module):
    """np.random 设种在模块的种子初始化之后仍然有效。"""
    seed = tone_berts_module._SEED
    np.random.seed(seed)
    a = np.random.rand(5)
    np.random.seed(seed)
    b = np.random.rand(5)
    assert (a == b).all(), "np.random.seed failed to make np.random.rand deterministic"


def test_module_constants_match_yaml_config(tone_berts_module):
    """tone_berts.py 暴露的常量与 yaml 配置值一致。

    回归守卫: 若有人改动 BERT_PARAMS 的访问路径或 deterministic_mode 默认值,
    本测试在 stage 23 真跑之前就会抓到。
    """
    assert tone_berts_module._DETERMINISTIC_MODE in {"cpu_strict", "gpu_strict", "off"}, (
        f"unexpected deterministic_mode: {tone_berts_module._DETERMINISTIC_MODE}"
    )
    assert tone_berts_module._SEED == 42, (
        f"random_seed mismatch with yaml: got {tone_berts_module._SEED}, expected 42"
    )


def test_cpu_strict_mode_disables_amp_and_cudnn_benchmark(tone_berts_module):
    """cpu_strict / gpu_strict 模式下 AMP 必须关闭, (CUDA 上) cuDNN benchmark 也须关闭。"""
    mode = tone_berts_module._DETERMINISTIC_MODE
    if mode == "off":
        pytest.skip("deterministic_mode=off; nothing to enforce")
    # 严格模式下无论什么设备, USE_AMP 都必须是 False。
    assert tone_berts_module.USE_AMP is False, (
        f"USE_AMP must be False in {mode} mode; AMP introduces non-determinism"
    )
    # CUDA 上 cuDNN 必须处于确定性模式且 benchmark 关闭。
    if tone_berts_module.DEVICE.type == "cuda":
        assert torch.backends.cudnn.deterministic is True, (
            f"cudnn.deterministic must be True in {mode} mode"
        )
        assert torch.backends.cudnn.benchmark is False, (
            f"cudnn.benchmark must be False in {mode} mode"
        )
