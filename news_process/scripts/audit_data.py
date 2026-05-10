"""数据版本审计工具。"""

import argparse
from pathlib import Path
from typing import List

from news_process.core.config import load_config
from news_process.core.data_versioning import read_parquet_metadata, verify_data_integrity
from news_process.core.schemas import OUTPUT_REGISTRY


def audit_all_data(output_dir: str | Path | None = None) -> List[dict]:
    """
    审计所有数据文件。

    Args:
        output_dir: 可选的处理数据目录；默认读取配置中的 paths.output_dir。

    Returns:
        审计结果列表
    """
    results = []
    if output_dir is None:
        output_dir = load_config()["paths"]["output_dir"]
    output_dir = Path(output_dir)

    for stage, output_files in OUTPUT_REGISTRY.items():
        for output_file in output_files:
            output_path = output_dir / output_file

            result = {
                "file": output_file,
                "exists": output_path.exists(),
                "has_metadata": False,
                "integrity_ok": False,
                "metadata": None,
            }

            if output_path.exists():
                metadata = read_parquet_metadata(output_path)
                result["has_metadata"] = metadata is not None
                result["metadata"] = metadata

                if metadata:
                    result["integrity_ok"] = verify_data_integrity(output_path)

            results.append(result)

    return results


def print_audit_report(results: List[dict]):
    """打印审计报告。"""
    print("=" * 80)
    print("数据版本审计报告")
    print("=" * 80)
    print()

    total = len(results)
    exists = sum(1 for r in results if r["exists"])
    has_metadata = sum(1 for r in results if r["has_metadata"])
    integrity_ok = sum(1 for r in results if r["integrity_ok"])

    print(f"总文件数: {total}")
    print(f"存在的文件: {exists} ({exists/total*100:.1f}%)")
    print(f"包含元数据: {has_metadata} ({has_metadata/total*100:.1f}%)")
    print(f"完整性验证通过: {integrity_ok} ({integrity_ok/total*100:.1f}%)")
    print()

    print("详细信息:")
    print("-" * 80)

    for result in results:
        status = "✓" if result["integrity_ok"] else "✗"
        print(f"{status} {result['file']}")

        if result["metadata"]:
            metadata = result["metadata"]
            print(f"    Git commit: {metadata.get('git_commit', 'N/A')[:8]}")
            print(f"    Timestamp: {metadata.get('timestamp', 'N/A')}")
            print(f"    Config hash: {metadata.get('config_hash', 'N/A')[:8]}")
        elif result["exists"]:
            print("    ⚠ 缺少版本元数据")
        else:
            print("    ⚠ 文件不存在")

        print()


def main():
    parser = argparse.ArgumentParser(description="审计数据版本和完整性")
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出结果"
    )

    args = parser.parse_args()

    results = audit_all_data()

    if args.json:
        import json
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_audit_report(results)


if __name__ == "__main__":
    main()
