from radeonvla.record_dataset import _instruction_for, _task_cycle, parse_args
from radeonvla.tasks import get_task


def test_parse_record_defaults() -> None:
    args = parse_args(["--episodes", "3", "--overwrite"])
    assert args.episodes == 3
    assert args.overwrite is True
    assert args.repo_id == "visiobot/radeonvla_reflex"


def test_task_cycle_single_and_suite() -> None:
    args = parse_args(["--task", "banana_left"])
    assert _task_cycle(args) == ["banana_left"]
    args = parse_args(["--suite", "basic"])
    assert set(_task_cycle(args)) == {
        "banana_left",
        "banana_right",
        "lemon_left",
        "lemon_right",
        "plum_left",
        "plum_right",
    }
    args = parse_args(["--suite", "multistep"])
    assert "seq_triple_sort" in _task_cycle(args)


def test_training_instruction_comes_from_registry() -> None:
    task = get_task("lemon_right")
    text = _instruction_for("lemon_right", train=True)
    assert text in task.training_instructions
    assert text not in task.evaluation_instructions
