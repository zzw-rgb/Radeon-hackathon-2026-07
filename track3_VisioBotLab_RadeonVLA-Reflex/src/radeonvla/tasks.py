"""Canonical task registry for language-guided dual-bowl fruit sorting."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaskSpec:
    task_id: str
    target_object: str
    target_container: str
    training_instructions: tuple[str, ...]
    evaluation_instructions: tuple[str, ...]
    max_steps: int = 600
    max_retries: int = 1


def _task(
    fruit: str,
    side: str,
    training: tuple[str, ...],
    evaluation: tuple[str, ...],
) -> TaskSpec:
    return TaskSpec(
        task_id=f"{fruit}_{side}",
        target_object=fruit,
        target_container=f"{side}_bowl",
        training_instructions=training,
        evaluation_instructions=evaluation,
    )


TASKS: dict[str, TaskSpec] = {
    "banana_left": _task(
        "banana",
        "left",
        (
            "Pick the banana and place it in the left bowl.",
            "Sort the banana into the left container.",
        ),
        (
            "Move the yellow curved fruit to the container on the left.",
            "Put the banana into the bowl on the left side.",
        ),
    ),
    "banana_right": _task(
        "banana",
        "right",
        (
            "Pick the banana and place it in the right bowl.",
            "Sort the banana into the right container.",
        ),
        (
            "Move the yellow curved fruit to the container on the right.",
            "Put the banana into the bowl on the right side.",
        ),
    ),
    "lemon_left": _task(
        "lemon",
        "left",
        (
            "Pick the lemon and place it in the left bowl.",
            "Sort the lemon into the left container.",
        ),
        (
            "Put the yellow round fruit into the container on the left.",
            "Move the lemon to the left bowl.",
        ),
    ),
    "lemon_right": _task(
        "lemon",
        "right",
        (
            "Pick the lemon and place it in the right bowl.",
            "Sort the lemon into the right container.",
        ),
        (
            "Put the yellow round fruit into the container on the right.",
            "Move the lemon to the right bowl.",
        ),
    ),
    "plum_left": _task(
        "plum",
        "left",
        (
            "Pick the plum and place it in the left bowl.",
            "Sort the plum into the left container.",
        ),
        (
            "Move the purple fruit to the container on the left.",
            "Put the plum into the left bowl.",
        ),
    ),
    "plum_right": _task(
        "plum",
        "right",
        (
            "Pick the plum and place it in the right bowl.",
            "Sort the plum into the right container.",
        ),
        (
            "Move the purple fruit to the container on the right.",
            "Put the plum into the right bowl.",
        ),
    ),
}


def get_task(task_id: str) -> TaskSpec:
    try:
        return TASKS[task_id]
    except KeyError as exc:
        choices = ", ".join(sorted(TASKS))
        raise ValueError(f"Unknown task {task_id!r}. Expected one of: {choices}") from exc


def list_task_ids() -> list[str]:
    return sorted(TASKS)
