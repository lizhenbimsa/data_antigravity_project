"""取回 + 校验 LLM 复现性归档 (decision A: Zenodo 外部仓库交付, 2026-05-30)。

设计: git 仓库只存索引 ``data/llm_archive/manifest.json`` (每文件 SHA-256 + 记录数
+ 字节数); 归档实体 (~332MB→25GB 的每日 ``responses/*.jsonl``, LLM 原始响应,
顶刊 V4 F-P2.1 复现硬约束) 托管在 Zenodo, 凭 DOI 下载 —— 避免 git LFS 的存储/带宽
成本, 且数据永久可引用。

用法 (repo 根运行):
    python news_process/scripts/data_acquisition/fetch_llm_archive.py
        # 校验已下载到 data/llm_archive/responses/ 的归档 (对照 git 内 manifest)
    python news_process/scripts/data_acquisition/fetch_llm_archive.py --doi <DOI>
        # 用指定 DOI 打印下载指引

退出码: 0=校验通过 / 1=实体未就位(给下载指引) / 2=缺 manifest / 3=校验不一致。

⚠ 作者上传 Zenodo 后, 把下方 ``ZENODO_DOI`` 与 data/llm_archive/README.md 的 DOI
  填成真实值 (如 '10.5281/zenodo.1234567')。
"""
from __future__ import annotations

import argparse
import sys

# Zenodo record "Bank FinTech" (Open access / CC-BY-4.0); 实体归档 responses.zip 托管于此 DOI。
# 下载 responses.zip 后解压到 data/llm_archive/ (zip 内含 responses/ 子目录, 勿解压到
# responses/ 否则嵌套成 responses/responses/)。
# 2026-05-30 实测: zip 内 5 个 jsonl 与 manifest SHA-256 byte-for-byte 一致 (复现性成立)。
ZENODO_DOI = "10.5281/zenodo.20453766"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="取回 + 校验 LLM 复现归档 (Zenodo 交付)"
    )
    parser.add_argument(
        "--doi", default=None,
        help="覆盖内置 ZENODO_DOI (仅用于打印下载指引)",
    )
    args = parser.parse_args()

    from news_process.pipeline.llm_archive import verify_manifest
    from news_process.pipeline.llm_archive.archive import _resolve_archive_root

    root = _resolve_archive_root()
    responses = root / "responses"
    manifest = root / "manifest.json"

    if not manifest.exists():
        print(f"[ERR] 缺 manifest: {manifest}")
        print("      manifest.json 应随 git 仓库 clone 到位; 请确认在 repo 根运行。")
        return 2

    n_jsonl = len(list(responses.glob("*.jsonl"))) if responses.exists() else 0
    if n_jsonl == 0:
        doi = args.doi or ZENODO_DOI
        print("=" * 64)
        print("归档实体未就位 (data/llm_archive/responses/ 为空 / 不存在)。")
        print(f"请从 Zenodo 下载 responses.zip, 解压到: {root}")
        print("  (zip 内已含 responses/ 子目录, 勿解压到 responses/ 否则嵌套)")
        print(f"  DOI : {doi}")
        print(f"  URL : https://doi.org/{doi}")
        print("解压后重跑本脚本以校验 SHA-256 完整性。")
        print("=" * 64)
        return 1

    ok, errors = verify_manifest(root)
    if ok:
        print(f"[OK] 归档完整性校验通过: {n_jsonl} 个 jsonl 与 manifest SHA-256 一致。")
        return 0
    print(f"[FAIL] 校验未通过, {len(errors)} 处不一致:")
    for err in errors[:10]:
        print("  -", err)
    if len(errors) > 10:
        print(f"  ... 另有 {len(errors) - 10} 处")
    return 3


if __name__ == "__main__":
    sys.exit(main())
