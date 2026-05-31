"""Non-destructive smoke harness for run_pipeline_function.py.

不触发 run_pipeline() (那会预清理删除 parquet)。仅执行编排器实际依赖的
代码路径: 模块级 config/DAG 导入 + 阶段规划 + OUTPUT_REGISTRY 一致性 +
CLI 解析。任意环节抛错即非零退出, 复现编排器的真实错误。
"""
import sys
import traceback


def main() -> int:
    try:
        # 1) 导入编排器模块: 执行其模块级代码 (load_config / setup_logging /
        #    generate_run_id / 从 core.dag 导入 STAGES)。run_pipeline 在
        #    __main__ 守卫下, 导入不会触发它 → 非破坏性。
        import run_pipeline_function as orch

        # 2) 阶段规划: 复现编排器 run_pipeline() 里构建 stages 的逻辑。
        from news_process.core.dag import filter_enabled
        active = filter_enabled(orch.STAGES, orch.CONFIG)
        stages = [(s.script, s.name, s.timeout) for s in active]
        print(f"[smoke] 主管道规划阶段数 = {len(stages)}")
        for i, (script, name, _to) in enumerate(stages, 1):
            print(f"[smoke]   {i:>2}. {name} ({script})")

        # 3) OUTPUT_REGISTRY 一致性: 编排器对每个 active stage 调用
        #    _get_stage_output_files; 任一未登记会 raise RuntimeError。
        total_outputs = 0
        for script, _name, _to in stages:
            files = orch._get_stage_output_files(script)
            total_outputs += len(files)
        print(f"[smoke] 全部 active stage 通过 OUTPUT_REGISTRY 一致性校验; "
              f"登记输出文件累计 = {total_outputs}")

        # 4) CLI 解析两条路径。
        ns_default = orch._parse_cli_args([])
        ns_skip = orch._parse_cli_args(["--skip-21-if-exists"])
        assert ns_default.skip_21_if_exists is False
        assert ns_skip.skip_21_if_exists is True
        print("[smoke] CLI 解析 (默认 / --skip-21-if-exists) 正常")

        # 5) 编排器引用的 schemas 符号可解析。
        from news_process.core.schemas import (  # noqa: F401
            EXPECTED_NO_OUTPUT_STAGES,
            OUTPUT_REGISTRY,
        )
        print(f"[smoke] OUTPUT_REGISTRY={len(OUTPUT_REGISTRY)} 项, "
              f"EXPECTED_NO_OUTPUT_STAGES={len(EXPECTED_NO_OUTPUT_STAGES)} 项")

        print("[smoke] run_pipeline_function.py 代码层验证通过 (非破坏性)")
        return 0
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
