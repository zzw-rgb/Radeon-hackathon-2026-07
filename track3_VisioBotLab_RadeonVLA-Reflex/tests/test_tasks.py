import numpy as np
import pytest

from radeonvla.grounding import ATTRIBUTES, _expand_attribute_goals, _select_spatial
from radeonvla.tasks import L1_TASKS, L2_TASKS, L3_TASKS, L4_TASKS, SUITES, TASKS, get_task, list_task_ids


def test_registry_contains_all_tiers() -> None:
    assert set(L1_TASKS).issubset(TASKS)
    assert set(L2_TASKS).issubset(TASKS)
    assert set(L3_TASKS).issubset(TASKS)
    assert set(L4_TASKS).issubset(TASKS)
    assert len(TASKS) >= 16


def test_suites_partition_is_consistent() -> None:
    assert set(SUITES["basic"]) == set(L1_TASKS)
    assert set(SUITES["full"]) == set(TASKS)
    assert set(SUITES["advanced"]).isdisjoint(set())  # non-empty advanced set
    assert len(SUITES["advanced"]) >= 8


def test_training_and_evaluation_language_are_separate() -> None:
    for task in TASKS.values():
        assert task.training_instructions
        assert task.evaluation_instructions
        assert set(task.training_instructions).isdisjoint(task.evaluation_instructions)


def test_l3_is_multi_step() -> None:
    task = get_task("seq_banana_left_lemon_right")
    assert task.tier == "L3"
    assert task.is_multi_step
    assert len(task.goals) == 2


def test_l4_attribute_expansion() -> None:
    task = get_task("rule_yellow_left_purple_right")
    expanded = _expand_attribute_goals(task.goals)
    names = [g.object_name for g in expanded]
    assert "banana" in names and "lemon" in names and "plum" in names
    assert ATTRIBUTES["yellow"] == frozenset({"banana", "lemon"})


def test_spatial_grounding_uses_table_axes() -> None:
    positions = {
        "banana": np.array([0.3, 0.2, 0.8]),
        "lemon": np.array([0.4, -0.1, 0.8]),
        "plum": np.array([0.5, 0.0, 0.8]),
    }
    assert _select_spatial(positions, "leftmost") == "banana"
    assert _select_spatial(positions, "rightmost") == "lemon"
    assert _select_spatial(positions, "nearest_robot") == "banana"
    assert _select_spatial(positions, "farthest_robot") == "plum"


def test_unknown_task_fails_clearly() -> None:
    with pytest.raises(ValueError, match="Unknown task"):
        get_task("apple_left")


def test_list_task_ids_suite() -> None:
    ids = list_task_ids("multistep")
    assert all(tid in L3_TASKS for tid in ids)
