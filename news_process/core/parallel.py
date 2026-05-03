"""news_process.core.parallel — joblib-based DataFrame batch parallelism.

Split from legacy ``utils/helpers.py:524-590``.
Public API preserved: ``parallelize_dataframe``.
"""

from __future__ import annotations

import pandas as pd
import psutil
from joblib import Parallel, delayed


def parallelize_dataframe(df, func, n_jobs=-1, batch_size=10000,
                          logger=None, desc=None):
    """Apply ``func`` to ``df`` in row-batches across ``n_jobs`` worker processes.

    Args:
        df:         input DataFrame.
        func:       callable ``(df_batch) -> df_result``.
        n_jobs:     parallel worker count; -1 = all CPUs minus 1.
        batch_size: rows per batch (default 10k).
        logger:     optional logger for progress reporting.
        desc:       optional progress label.

    Returns:
        pd.DataFrame: vertically concatenated result.
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
