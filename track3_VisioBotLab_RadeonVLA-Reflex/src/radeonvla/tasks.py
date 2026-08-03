"""Language-conditioned task registry for RadeonVLA-Reflex.

Task tiers
----------
L1 Basic        — name a fruit + left/right bowl (single goal)
L2 Spatial      — grounding by spatial relation (leftmost / rightmost / nearest)
L3 Multi-step   — ordered multi-object sequences in one episode
L4 Rule-based   — attribute rules (e.g. yellow→left, purple→right)

The scripted expert and closed-loop policy execute a resolved goal list from
``radeonvla.grounding.resolve_task`` after each scene randomization.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Grounding = Literal["named", "leftmost", "rightmost", "nearest_robot", "farthest_robot"]
Tier = Literal["L1", "L2", "L3", "L4"]


@dataclass(frozen=True, slots=True)
class SubGoalSpec:
    """One pick-and-place goal, possibly with deferred spatial grounding."""

    container: str  # left_bowl | right_bowl
    object_name: str | None = None  # concrete fruit when grounding == named
    grounding: Grounding = "named"
    # For rule-based expansion (L4): attribute filters applied at resolve time.
    attribute: str | None = None  # yellow | purple | curved | round


@dataclass(frozen=True, slots=True)
class TaskSpec:
    task_id: str
    tier: Tier
    goals: tuple[SubGoalSpec, ...]
    training_instructions: tuple[str, ...]
    evaluation_instructions: tuple[str, ...]
    max_steps: int = 600
    max_retries: int = 1
    description: str = ""

    @property
    def target_object(self) -> str:
        """Backward-compatible primary object (first named goal or placeholder)."""
        g0 = self.goals[0]
        if g0.object_name is not None:
            return g0.object_name
        return f"@{g0.grounding}"

    @property
    def target_container(self) -> str:
        return self.goals[0].container

    @property
    def is_multi_step(self) -> bool:
        return len(self.goals) > 1 or self.tier in {"L3", "L4"}

    @property
    def n_goals(self) -> int:
        # L4 attribute rules expand at resolve time; upper bound used for logging.
        if self.tier == "L4":
            return 3
        return len(self.goals)


def _l1(fruit: str, side: str, training: tuple[str, ...], evaluation: tuple[str, ...]) -> TaskSpec:
    return TaskSpec(
        task_id=f"{fruit}_{side}",
        tier="L1",
        goals=(SubGoalSpec(object_name=fruit, container=f"{side}_bowl", grounding="named"),),
        training_instructions=training,
        evaluation_instructions=evaluation,
        max_steps=600,
        description=f"Pick {fruit} into {side} bowl.",
    )


def _l2(
    task_id: str,
    grounding: Grounding,
    side: str,
    training: tuple[str, ...],
    evaluation: tuple[str, ...],
) -> TaskSpec:
    return TaskSpec(
        task_id=task_id,
        tier="L2",
        goals=(SubGoalSpec(object_name=None, container=f"{side}_bowl", grounding=grounding),),
        training_instructions=training,
        evaluation_instructions=evaluation,
        max_steps=700,
        description=f"Ground {grounding} fruit into {side} bowl.",
    )


def _l3(
    task_id: str,
    goals: tuple[SubGoalSpec, ...],
    training: tuple[str, ...],
    evaluation: tuple[str, ...],
) -> TaskSpec:
    return TaskSpec(
        task_id=task_id,
        tier="L3",
        goals=goals,
        training_instructions=training,
        evaluation_instructions=evaluation,
        max_steps=1400,
        description="Ordered multi-object sort.",
    )


def _l4(
    task_id: str,
    goals: tuple[SubGoalSpec, ...],
    training: tuple[str, ...],
    evaluation: tuple[str, ...],
) -> TaskSpec:
    return TaskSpec(
        task_id=task_id,
        tier="L4",
        goals=goals,
        training_instructions=training,
        evaluation_instructions=evaluation,
        max_steps=1800,
        description="Attribute rule-based multi-object sort.",
    )


# ---------------------------------------------------------------------------
# L1 — basic named fruit × bowl (baseline, still required)
# ---------------------------------------------------------------------------
L1_TASKS: dict[str, TaskSpec] = {
    "banana_left": _l1(
        "banana",
        "left",
        ("Pick the banana and place it in the left bowl.", "Sort the banana into the left container."),
        (
            "Move the yellow curved fruit to the container on the left.",
            "Put the banana into the bowl on the left side.",
        ),
    ),
    "banana_right": _l1(
        "banana",
        "right",
        ("Pick the banana and place it in the right bowl.", "Sort the banana into the right container."),
        (
            "Move the yellow curved fruit to the container on the right.",
            "Put the banana into the bowl on the right side.",
        ),
    ),
    "lemon_left": _l1(
        "lemon",
        "left",
        ("Pick the lemon and place it in the left bowl.", "Sort the lemon into the left container."),
        ("Put the yellow round fruit into the container on the left.", "Move the lemon to the left bowl."),
    ),
    "lemon_right": _l1(
        "lemon",
        "right",
        ("Pick the lemon and place it in the right bowl.", "Sort the lemon into the right container."),
        ("Put the yellow round fruit into the container on the right.", "Move the lemon to the right bowl."),
    ),
    "plum_left": _l1(
        "plum",
        "left",
        ("Pick the plum and place it in the left bowl.", "Sort the plum into the left container."),
        ("Move the purple fruit to the container on the left.", "Put the plum into the left bowl."),
    ),
    "plum_right": _l1(
        "plum",
        "right",
        ("Pick the plum and place it in the right bowl.", "Sort the plum into the right container."),
        ("Move the purple fruit to the container on the right.", "Put the plum into the right bowl."),
    ),
}

# ---------------------------------------------------------------------------
# L2 — spatial grounding (must look at relative layout after randomization)
# ---------------------------------------------------------------------------
L2_TASKS: dict[str, TaskSpec] = {
    "leftmost_to_left": _l2(
        "leftmost_to_left",
        "leftmost",
        "left",
        (
            "Pick the leftmost fruit on the table and put it in the left bowl.",
            "Sort the fruit that is farthest to the left into the left container.",
        ),
        (
            "Move the fruit closest to the left edge into the left bowl.",
            "Place whichever fruit sits most to the left into the left container.",
        ),
    ),
    "rightmost_to_right": _l2(
        "rightmost_to_right",
        "rightmost",
        "right",
        (
            "Pick the rightmost fruit on the table and put it in the right bowl.",
            "Sort the fruit that is farthest to the right into the right container.",
        ),
        (
            "Move the fruit closest to the right edge into the right bowl.",
            "Place whichever fruit sits most to the right into the right container.",
        ),
    ),
    "nearest_to_left": _l2(
        "nearest_to_left",
        "nearest_robot",
        "left",
        (
            "Pick the fruit nearest to the robot base and place it in the left bowl.",
            "Sort the closest fruit to the arm into the left container.",
        ),
        (
            "Move the fruit that is nearest the manipulator into the left bowl.",
            "Place the closest reachable fruit into the left container.",
        ),
    ),
    "farthest_to_right": _l2(
        "farthest_to_right",
        "farthest_robot",
        "right",
        (
            "Pick the fruit farthest from the robot and place it in the right bowl.",
            "Sort the most distant fruit into the right container.",
        ),
        (
            "Move the fruit that is farthest from the manipulator into the right bowl.",
            "Place the farthest fruit into the right container.",
        ),
    ),
}

# ---------------------------------------------------------------------------
# L3 — ordered multi-object sequences (long horizon)
# ---------------------------------------------------------------------------
L3_TASKS: dict[str, TaskSpec] = {
    "seq_banana_left_lemon_right": _l3(
        "seq_banana_left_lemon_right",
        (
            SubGoalSpec(object_name="banana", container="left_bowl"),
            SubGoalSpec(object_name="lemon", container="right_bowl"),
        ),
        (
            "First put the banana in the left bowl, then put the lemon in the right bowl.",
            "Sort the banana left and the lemon right, in that order.",
        ),
        (
            "Place the curved yellow fruit into the left container, then the round yellow fruit into the right.",
            "Banana goes left, lemon goes right — complete both steps.",
        ),
    ),
    "seq_plum_right_banana_left": _l3(
        "seq_plum_right_banana_left",
        (
            SubGoalSpec(object_name="plum", container="right_bowl"),
            SubGoalSpec(object_name="banana", container="left_bowl"),
        ),
        (
            "First put the plum in the right bowl, then put the banana in the left bowl.",
            "Sort the plum right and the banana left, in that order.",
        ),
        (
            "Purple fruit to the right container, then the curved yellow fruit to the left.",
            "Complete both placements: plum right, banana left.",
        ),
    ),
    "seq_lemon_left_plum_left": _l3(
        "seq_lemon_left_plum_left",
        (
            SubGoalSpec(object_name="lemon", container="left_bowl"),
            SubGoalSpec(object_name="plum", container="left_bowl"),
        ),
        (
            "Put the lemon and then the plum into the left bowl.",
            "Sort both the lemon and the plum into the left container, lemon first.",
        ),
        (
            "Move the round yellow fruit and then the purple fruit into the left bowl.",
            "Both lemon and plum should end in the left container.",
        ),
    ),
    "seq_triple_sort": _l3(
        "seq_triple_sort",
        (
            SubGoalSpec(object_name="banana", container="left_bowl"),
            SubGoalSpec(object_name="lemon", container="left_bowl"),
            SubGoalSpec(object_name="plum", container="right_bowl"),
        ),
        (
            "Put the banana and the lemon into the left bowl, and the plum into the right bowl.",
            "Left bowl: banana then lemon. Right bowl: plum.",
        ),
        (
            "Yellow fruits go left; the purple fruit goes right. Handle banana, lemon, then plum.",
            "Complete the three-way sort: banana left, lemon left, plum right.",
        ),
    ),
}

# ---------------------------------------------------------------------------
# L4 — attribute / rule-based sorting (expanded at resolve time)
# ---------------------------------------------------------------------------
L4_TASKS: dict[str, TaskSpec] = {
    "rule_yellow_left_purple_right": _l4(
        "rule_yellow_left_purple_right",
        (
            # attribute markers; grounding expands to concrete fruits in order
            SubGoalSpec(container="left_bowl", grounding="named", attribute="yellow"),
            SubGoalSpec(container="right_bowl", grounding="named", attribute="purple"),
        ),
        (
            "Put all yellow fruits into the left bowl and the purple fruit into the right bowl.",
            "Sort by color: yellow to the left container, purple to the right.",
        ),
        (
            "Move every yellow item left and the purple item right.",
            "Color rule: yellow→left, purple→right.",
        ),
    ),
    "rule_round_right_curved_left": _l4(
        "rule_round_right_curved_left",
        (
            SubGoalSpec(container="left_bowl", grounding="named", attribute="curved"),
            SubGoalSpec(container="right_bowl", grounding="named", attribute="round"),
        ),
        (
            "Put the curved fruit into the left bowl and the round fruits into the right bowl.",
            "Shape rule: curved→left, round→right.",
        ),
        (
            "Banana-like curved item left; spherical items right.",
            "Sort by shape: curved left, round right.",
        ),
    ),
}

# Full registry (union). Suites select subsets.
TASKS: dict[str, TaskSpec] = {**L1_TASKS, **L2_TASKS, **L3_TASKS, **L4_TASKS}

SUITES: dict[str, tuple[str, ...]] = {
    # Baseline only (starter-comparable single-goal)
    "basic": tuple(sorted(L1_TASKS)),
    # Spatial + multi-step differentiators
    "advanced": tuple(sorted({*L2_TASKS, *L3_TASKS, *L4_TASKS})),
    # Competition default: mix for coverage and difficulty
    "full": tuple(sorted(TASKS)),
    # Long-horizon only (demo of hardness)
    "multistep": tuple(sorted(L3_TASKS)),
    "spatial": tuple(sorted(L2_TASKS)),
    "rules": tuple(sorted(L4_TASKS)),
}


def get_task(task_id: str) -> TaskSpec:
    try:
        return TASKS[task_id]
    except KeyError as exc:
        choices = ", ".join(sorted(TASKS))
        raise ValueError(f"Unknown task {task_id!r}. Expected one of: {choices}") from exc


def list_task_ids(suite: str | None = None) -> list[str]:
    if suite is None:
        return sorted(TASKS)
    if suite not in SUITES:
        raise ValueError(f"Unknown suite {suite!r}. Expected one of: {sorted(SUITES)}")
    return list(SUITES[suite])


def tasks_for_suite(suite: str = "full") -> dict[str, TaskSpec]:
    return {tid: TASKS[tid] for tid in list_task_ids(suite)}
