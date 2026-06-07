#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nanopilot.evaluator import run_harness_regression_v2  # noqa: E402
from nanopilot.metrics import (  # noqa: E402
    DEFAULT_HARNESS_REGRESSION_V2_PATH,
    DEFAULT_RESUME_CONTEXT_ABLATION_V2_PATH,
    DEFAULT_RESUME_EXPANDED_REPORT_PATH,
    DEFAULT_RESUME_MEMORY_ABLATION_V2_PATH,
    DEFAULT_RESUME_RECOVERY_ABLATION_V2_PATH,
    DEFAULT_RESUME_SECURITY_REGRESSION_V2_PATH,
    run_resume_context_ablation_v2,
    run_resume_memory_ablation_v2,
    run_resume_recovery_ablation_v2,
    run_resume_security_regression_v2,
    write_resume_expanded_report,
)


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Run resume-focused expanded NanoPilot evaluation artifacts.")
    parser.add_argument("--benchmark-path", default="benchmarks/coding_tasks.json")
    parser.add_argument("--harness-artifact", default=str(DEFAULT_HARNESS_REGRESSION_V2_PATH))
    parser.add_argument("--harness-workspace-root", default="artifacts/harness-workspaces")
    parser.add_argument("--context-artifact", default=str(DEFAULT_RESUME_CONTEXT_ABLATION_V2_PATH))
    parser.add_argument("--memory-artifact", default=str(DEFAULT_RESUME_MEMORY_ABLATION_V2_PATH))
    parser.add_argument("--recovery-artifact", default=str(DEFAULT_RESUME_RECOVERY_ABLATION_V2_PATH))
    parser.add_argument("--security-artifact", default=str(DEFAULT_RESUME_SECURITY_REGRESSION_V2_PATH))
    parser.add_argument("--report", default=str(DEFAULT_RESUME_EXPANDED_REPORT_PATH))
    parser.add_argument("--context-repetitions", type=int, default=5)
    parser.add_argument("--memory-repetitions", type=int, default=5)
    parser.add_argument("--recovery-repetitions", type=int, default=3)
    parser.add_argument("--security-repetitions", type=int, default=3)
    return parser


def main(argv=None):
    args = build_arg_parser().parse_args(argv)

    run_harness_regression_v2(
        benchmark_path=args.benchmark_path,
        artifact_path=args.harness_artifact,
        workspace_root=args.harness_workspace_root,
    )
    run_resume_context_ablation_v2(
        artifact_path=args.context_artifact,
        repetitions=args.context_repetitions,
    )
    run_resume_memory_ablation_v2(
        artifact_path=args.memory_artifact,
        repetitions=args.memory_repetitions,
    )
    run_resume_recovery_ablation_v2(
        artifact_path=args.recovery_artifact,
        repetitions=args.recovery_repetitions,
    )
    run_resume_security_regression_v2(
        artifact_path=args.security_artifact,
        repetitions=args.security_repetitions,
    )
    write_resume_expanded_report(
        report_path=args.report,
        harness_artifact_path=args.harness_artifact,
        context_artifact_path=args.context_artifact,
        memory_artifact_path=args.memory_artifact,
        recovery_artifact_path=args.recovery_artifact,
        security_artifact_path=args.security_artifact,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
