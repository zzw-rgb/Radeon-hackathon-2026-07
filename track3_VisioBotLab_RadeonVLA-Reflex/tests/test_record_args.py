from radeonvla.record_dataset import _instruction_for, _missing_task_coverage, _task_cycle, parse_args
from radeonvla.tasks import get_task


def test_parse_record_defaults() -> None:
    args = parse_args(["--episodes", "3", "--overwrite"])
    assert args.episodes == 3
    assert args.overwrite is True
    assert args.repo_id == "visiobot/radeonvla_reflex"


def test_task_cycle_single_and_suite() -> None:
    args = parse_args(["--task", "banana_white_left"])
    assert _task_cycle(args) == ["banana_white_left"]
    args = parse_args(["--suite", "basic"])
    basic = set(_task_cycle(args))
    assert len(basic) == 20
    assert "banana_white_left" in basic and "apple_blue_left" in basic and "orange_blue_right" in basic
    args = parse_args(["--suite", "multistep"])
    assert "seq_triple_sort" in _task_cycle(args)
    assert "seq_apple_blue_left_orange_blue_right" in _task_cycle(args)


def test_training_instruction_comes_from_registry() -> None:
    task = get_task("lemon_white_right")
    text = _instruction_for("lemon_white_right", train=True)
    assert text in task.training_instructions
    assert text not in task.evaluation_instructions


def test_required_coverage_reports_missing_tasks() -> None:
    selected = ["apple_blue_left", "banana_white_left"]
    counts = {"apple_blue_left": 1, "banana_white_left": 0}
    assert _missing_task_coverage(selected, counts) == ["banana_white_left"]
    counts["banana_white_left"] = 1
    assert _missing_task_coverage(selected, counts) == []
