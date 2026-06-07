import os
from unittest.mock import patch

from nanopilot.metrics import (
    _provider_profile,
    run_context_ablation_v2,
    run_memory_ablation_v2,
    run_recovery_ablation_v2,
    run_resume_context_ablation_v2,
    run_resume_memory_ablation_v2,
    run_resume_recovery_ablation_v2,
    run_resume_security_regression_v2,
    write_resume_expanded_report,
    write_benchmark_core_report,
)


def test_run_context_ablation_v2_writes_expected_artifact(tmp_path):
    artifact_path = tmp_path / "artifacts" / "context-ablation-v2.json"

    artifact = run_context_ablation_v2(
        artifact_path=artifact_path,
        repetitions=1,
    )

    assert artifact_path.exists()
    assert artifact["artifact_type"] == "context-ablation-v2"
    assert artifact["config_count"] == 12
    assert len(artifact["configs"]) == 12
    assert "current_request_preserved_rate" in artifact["summary"]


def test_provider_profile_loads_project_env_before_reading_deepseek_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "\n".join(
            [
                "NANOPILOT_DEEPSEEK_API_KEY=sk-project-deepseek",
                "NANOPILOT_DEEPSEEK_MODEL=deepseek-v4-pro",
                "NANOPILOT_DEEPSEEK_API_BASE=https://api.deepseek.com/anthropic",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with patch.dict(
        os.environ,
        {
            "DEEPSEEK_API_KEY": "sk-legacy-deepseek",
            "DEEPSEEK_MODEL": "legacy-deepseek-model",
            "DEEPSEEK_API_BASE": "https://legacy.deepseek.example/anthropic",
        },
        clear=True,
    ):
        profile = _provider_profile("deepseek")

    assert profile["status"] == "ready"
    assert profile["api_key"] == "sk-project-deepseek"
    assert profile["model"] == "deepseek-v4-pro"
    assert profile["base_url"] == "https://api.deepseek.com/anthropic"


def test_run_memory_ablation_v2_writes_expected_artifact(tmp_path):
    artifact_path = tmp_path / "artifacts" / "memory-ablation-v2.json"

    artifact = run_memory_ablation_v2(
        artifact_path=artifact_path,
        repetitions=1,
    )

    assert artifact_path.exists()
    assert artifact["artifact_type"] == "memory-ablation-v2"
    assert artifact["task_count"] == 12
    assert set(artifact["variants"]) == {"memory_on", "memory_off", "memory_irrelevant"}
    assert "memory_hit_rate" in artifact["variants"]["memory_on"]


def test_run_recovery_ablation_v2_writes_expected_artifact(tmp_path):
    artifact_path = tmp_path / "artifacts" / "recovery-ablation-v2.json"

    artifact = run_recovery_ablation_v2(
        artifact_path=artifact_path,
        repetitions=1,
    )

    assert artifact_path.exists()
    assert artifact["artifact_type"] == "recovery-ablation-v2"
    assert artifact["task_count"] == 10
    assert set(artifact["variants"]) == {"resume_enabled", "resume_disabled"}
    assert set(artifact["variants"]["resume_enabled"]["summary"]) >= {
        "resume_success_rate",
        "stale_reanchor_rate",
        "workspace_drift_detection_rate",
        "resume_false_accept_rate",
    }


def test_resume_expanded_artifacts_use_resume_matrix_sizes(tmp_path):
    context_path = tmp_path / "artifacts" / "resume-context-ablation-v2.json"
    memory_path = tmp_path / "artifacts" / "resume-memory-ablation-v2.json"
    recovery_path = tmp_path / "artifacts" / "resume-recovery-ablation-v2.json"
    security_path = tmp_path / "artifacts" / "resume-security-regression-v2.json"

    context = run_resume_context_ablation_v2(context_path, repetitions=1)
    memory = run_resume_memory_ablation_v2(memory_path, repetitions=1)
    recovery = run_resume_recovery_ablation_v2(recovery_path, repetitions=1)
    security = run_resume_security_regression_v2(security_path, repetitions=1)

    assert context["artifact_type"] == "resume-context-ablation-v2"
    assert context["config_count"] == 24
    assert context["runs"] == 24
    assert memory["artifact_type"] == "resume-memory-ablation-v2"
    assert memory["task_count"] == 18
    assert memory["total_variant_runs"] == 54
    assert recovery["artifact_type"] == "resume-recovery-ablation-v2"
    assert recovery["task_count"] == 14
    assert recovery["total_variant_runs"] == 28
    assert security["artifact_type"] == "resume-security-regression-v2"
    assert security["scenario_count"] == 14
    assert security["runs"] == 14


def test_write_resume_expanded_report_includes_resume_safe_numbers(tmp_path):
    context_path = tmp_path / "artifacts" / "resume-context-ablation-v2.json"
    memory_path = tmp_path / "artifacts" / "resume-memory-ablation-v2.json"
    recovery_path = tmp_path / "artifacts" / "resume-recovery-ablation-v2.json"
    security_path = tmp_path / "artifacts" / "resume-security-regression-v2.json"
    harness_path = tmp_path / "artifacts" / "harness-regression-v2.json"
    harness_path.parent.mkdir(parents=True, exist_ok=True)
    harness_path.write_text(
        '{"summary":{"total_tasks":12,"pass_rate":1.0,"within_budget_rate":1.0,"verifier_pass_rate":1.0}}',
        encoding="utf-8",
    )
    run_resume_context_ablation_v2(context_path, repetitions=1)
    run_resume_memory_ablation_v2(memory_path, repetitions=1)
    run_resume_recovery_ablation_v2(recovery_path, repetitions=1)
    run_resume_security_regression_v2(security_path, repetitions=1)

    report_path = tmp_path / "docs" / "metrics" / "nanopilot-resume-expanded-report.md"
    report_text = write_resume_expanded_report(
        report_path=report_path,
        harness_artifact_path=harness_path,
        context_artifact_path=context_path,
        memory_artifact_path=memory_path,
        recovery_artifact_path=recovery_path,
        security_artifact_path=security_path,
    )

    assert report_path.exists()
    assert "Resume Context Ablation" in report_text
    assert "configs: 24" in report_text
    assert "tasks: 18" in report_text
    assert "scenarios: 14" in report_text


def test_write_benchmark_core_report_marks_resume_safe_metrics(tmp_path):
    run_context_ablation_v2(tmp_path / "artifacts" / "context-ablation-v2.json", repetitions=1)
    run_memory_ablation_v2(tmp_path / "artifacts" / "memory-ablation-v2.json", repetitions=1)
    run_recovery_ablation_v2(tmp_path / "artifacts" / "recovery-ablation-v2.json", repetitions=1)
    harness_artifact_path = tmp_path / "artifacts" / "harness-regression-v2.json"
    harness_artifact_path.write_text(
        '{"summary":{"total_tasks":12,"pass_rate":1.0,"within_budget_rate":1.0,"verifier_pass_rate":1.0},"failure_category_counts":{}}',
        encoding="utf-8",
    )

    report_path = tmp_path / "docs" / "metrics" / "nanopilot-benchmark-core-report.md"
    report_text = write_benchmark_core_report(
        report_path=report_path,
        harness_artifact_path=harness_artifact_path,
        context_artifact_path=tmp_path / "artifacts" / "context-ablation-v2.json",
        memory_artifact_path=tmp_path / "artifacts" / "memory-ablation-v2.json",
        recovery_artifact_path=tmp_path / "artifacts" / "recovery-ablation-v2.json",
    )

    assert report_path.exists()
    assert "可以安全写进简历的指标" in report_text
    assert "只适合放文档/面试展开的指标" in report_text
    assert "resume_success_rate" in report_text
    assert "memory_hit_rate" in report_text
