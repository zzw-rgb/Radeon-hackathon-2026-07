import pytest

from radeonvla.tasks import TASKS, get_task


def test_registry_contains_all_six_tasks() -> None:
    assert set(TASKS) == {
        "banana_left",
        "banana_right",
        "lemon_left",
        "lemon_right",
        "plum_left",
        "plum_right",
    }


def test_training_and_evaluation_language_are_separate() -> None:
    for task in TASKS.values():
        assert task.training_instructions
        assert task.evaluation_instructions
        assert set(task.training_instructions).isdisjoint(task.evaluation_instructions)


def test_unknown_task_fails_clearly() -> None:
    with pytest.raises(ValueError, match="Unknown task"):
        get_task("apple_left")
