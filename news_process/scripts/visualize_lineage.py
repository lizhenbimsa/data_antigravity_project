"""生成数据血缘关系图。"""

import argparse
from pathlib import Path
from typing import Dict, List, Set

from news_process.core.data_versioning import read_parquet_metadata
from news_process.core.schemas import OUTPUT_REGISTRY


def build_lineage_graph() -> Dict[str, List[str]]:
    """
    构建数据血缘关系图。

    Returns:
        字典，键为输出文件，值为输入文件列表
    """
    lineage = {}

    for stage, output_files in OUTPUT_REGISTRY.items():
        for output_file in output_files:
            output_path = Path("data/processed") / output_file

            if output_path.exists():
                metadata = read_parquet_metadata(output_path)
                if metadata:
                    input_files = metadata.get("input_files", [])
                    lineage[output_file] = input_files

    return lineage


def generate_mermaid_diagram(lineage: Dict[str, List[str]]) -> str:
    """
    生成 Mermaid 格式的血缘关系图。

    Args:
        lineage: 血缘关系字典

    Returns:
        Mermaid 图表字符串
    """
    lines = ["graph TD"]

    for output_file, input_files in lineage.items():
        output_node = output_file.replace(".", "_")

        for input_file in input_files:
            input_node = Path(input_file).name.replace(".", "_")
            lines.append(f"    {input_node}[{Path(input_file).name}] --> {output_node}[{output_file}]")

    return "\n".join(lines)


def generate_dot_diagram(lineage: Dict[str, List[str]]) -> str:
    """
    生成 Graphviz DOT 格式的血缘关系图。

    Args:
        lineage: 血缘关系字典

    Returns:
        DOT 图表字符串
    """
    lines = ["digraph lineage {", "    rankdir=LR;", "    node [shape=box];"]

    all_nodes: Set[str] = set()
    for output_file, input_files in lineage.items():
        all_nodes.add(output_file)
        all_nodes.update(Path(f).name for f in input_files)

    for node in sorted(all_nodes):
        node_id = node.replace(".", "_")
        lines.append(f'    {node_id} [label="{node}"];')

    for output_file, input_files in lineage.items():
        output_id = output_file.replace(".", "_")
        for input_file in input_files:
            input_id = Path(input_file).name.replace(".", "_")
            lines.append(f"    {input_id} -> {output_id};")

    lines.append("}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="生成数据血缘关系图")
    parser.add_argument(
        "--format",
        choices=["mermaid", "dot"],
        default="mermaid",
        help="输出格式（mermaid 或 dot）"
    )
    parser.add_argument(
        "--output",
        default="data_lineage.md",
        help="输出文件路径"
    )

    args = parser.parse_args()

    lineage = build_lineage_graph()

    if args.format == "mermaid":
        diagram = generate_mermaid_diagram(lineage)
        content = f"# 数据血缘关系图\n\n```mermaid\n{diagram}\n```\n"
    else:
        diagram = generate_dot_diagram(lineage)
        content = diagram

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✓ 血缘关系图已保存到: {args.output}")
    print(f"  包含 {len(lineage)} 个数据文件")


if __name__ == "__main__":
    main()
