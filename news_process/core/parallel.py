"""news_process.core.parallel — 基于 joblib 的 DataFrame 批次并行工具。

由历史 ``utils/helpers.py:524-590`` 拆分而来。
保留的公开 API: ``parallelize_dataframe``。
"""

from __future__ import annotations

import pandas as pd
import psutil
from joblib import Parallel, delayed


def parallelize_dataframe(df, func, n_jobs=-1, batch_size=10000,
                          logger=None, desc=None):
    """将 ``func`` 按行批次应用到 ``df``, 跨 ``n_jobs`` 个 worker 进程并行执行。

    Args:
        df:         输入 DataFrame。
        func:       callable, 签名为 ``(df_batch) -> df_result``。
        n_jobs:     并行 worker 数量; -1 表示 "全部 CPU - 1"。
        batch_size: 每批次行数 (默认 10000)。
        logger:     可选 logger, 用于进度上报。
        desc:       可选进度标签。

    Returns:
        pd.DataFrame: 各批次结果纵向拼接后的整张 DataFrame。
    """
    if n_jobs == -1:
        n_jobs = max(1, psutil.cpu_count(logical=True) - 1)

    num_batches = max(1, (len(df) - 1) // batch_size + 1)
    df_batches = [
        df.iloc[i * batch_size:(i + 1) * batch_size]
        for i in range(num_batches)
    ]

    task_desc = desc or "批次处理"
    if logger:
        logger.info(
            f"{task_desc}: 共 {num_batches} 个批次，"
            f"每批次 {batch_size} 行，使用 {n_jobs} 个并行进程"
        )

    results = []
    completed = 0
    for result in Parallel(n_jobs=n_jobs, return_as="generator")(
        delayed(func)(batch) for batch in df_batches
    ):
        results.append(result)
        completed += 1
        if logger and (completed % max(1, num_batches // 10) == 0
                       or completed == num_batches):
            progress_pct = (completed / num_batches) * 100
            logger.info(
                f"{task_desc}: 进度 {completed}/{num_batches} "
                f"({progress_pct:.1f}%)"
            )

    return pd.concat(results)
