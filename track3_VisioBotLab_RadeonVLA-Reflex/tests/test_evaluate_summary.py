from dataclasses import asdict
from pathlib import Path

from radeonvla.artifact_io import validate_evaluation_payload
from radeonvla.evaluate import EpisodeResult, summarize

ROOT = Path(__file__).resolve().parents[1]


def episode(**overrides) -> EpisodeResult:
    values = {
        "episode_id": "banana_white_left_1",
        "seed": 1,
        "task_id": "banana_white_left",
        "instruction": "Pick the banana.",
        "success": True,
        "object_correct": True,
        "target_correct": True,
        "first_attempt_success": True,
        "inference_latency_ms": [10.0, 20.0],
    }
    values.update(overrides)
    return EpisodeResult(**values)


def test_summary_reports_reflex_and_scenario_metrics() -> None:
    results = [
        episode(
            interrupted=True,
            safe_interrupt=True,
            interrupt_response_steps=0,
            scenario="interrupt",
        ),
        episode(
            episode_id="banana_white_left_2",
            seed=2,
            success=False,
            object_correct=False,
            target_correct=False,
            first_attempt_success=False,
            retry_count=1,
            scenario="target_shift",
        ),
    ]
    summary = summarize(results)
    assert summary["final_success"] == 0.5
    assert summary["safe_interrupt_rate"] == 1.0
    assert summary["mean_interrupt_response_steps"] == 0.0
    assert summary["success_by_task"]["banana_white_left"] == 0.5
    assert summary["success_by_scenario"] == {"interrupt": 1.0, "target_shift": 0.0}
    assert summary["p50_inference_latency_ms"] == 15.0


def test_episode_result_and_summary_match_formal_schema() -> None:
    result = episode()
    payload = {
        "experiment_id": "schema_test",
        "git_commit": "a" * 40,
        "environment": {
            "gpu": "cpu",
            "rocm": "none",
            "torch": "test",
            "genesis": "test",
            "lerobot": "test",
        },
        "checkpoint": {"uri": "test", "sha256": "b" * 64},
        "config": {},
        "summary": summarize([result]),
        "episodes": [asdict(result)],
    }
    validate_evaluation_payload(payload, ROOT / "artifacts" / "evaluation.schema.json")
