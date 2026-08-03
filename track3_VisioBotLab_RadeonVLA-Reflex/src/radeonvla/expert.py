"""Scripted dual-bowl pick-and-place expert for demonstration collection.

The expert follows a resolved task: pick the target fruit and place it into the
commanded left or right bowl. Multi-step tasks run subgoals in order. Motion uses
IK with velocity-limited transport while grasping.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from radeonvla.paths import FRAMES_DIR, PROJECT_ROOT
from radeonvla.protocol import GRIPPER_CLOSED, GRIPPER_OPEN
from radeonvla.safety import check_placement_success, entity_aabb, entity_pos
from radeonvla.scene import AppearanceDR, build_scene, init_genesis
from radeonvla.scene_config import FRANKA_QPOS, TABLE_TOP_Z

PREGRASP_CLEARANCE = 0.18
LIFT_HAND_Z = TABLE_TOP_Z + 0.30
RETREAT_HAND_Z = TABLE_TOP_Z + 0.35
PLACE_HAND_Z_ABOVE = 0.16
HAND_TO_FINGERTIP = 0.105
GRASP_CENTER_DROP_FRAC = 0.45
PALM_CLEARANCE = 0.02
MOVE_MAX_DQ = 0.006
MOVE_MIN_STEPS = 40
MOVE_SETTLE_STEPS = 15

MOTORS_DOF = np.arange(7)
FINGERS_DOF = np.arange(7, 9)

RecorderFn = Callable[[np.ndarray], None]


@dataclass(frozen=True)
class GraspProfile:
    yaw_offset: float = 90.0
    grasp_hand_z: float = TABLE_TOP_Z + 0.105
    close_force: float = -10.0
    center_align: bool = False


PROFILES: dict[str, GraspProfile] = {
    "banana": GraspProfile(yaw_offset=90.0, grasp_hand_z=TABLE_TOP_Z + 0.105, close_force=-10.0),
    "lemon": GraspProfile(yaw_offset=0.0, close_force=-12.0, center_align=True),
    "plum": GraspProfile(yaw_offset=0.0, close_force=-12.0, center_align=True),
}


def _to_np(x) -> np.ndarray:
    if hasattr(x, "detach"):
        x = x.detach().cpu().numpy()
    return np.asarray(x).reshape(-1)


def _topdown_quat(yaw_deg: float) -> np.ndarray:
    from genesis.utils.geom import euler_to_quat

    return euler_to_quat(np.array([180.0, 0.0, yaw_deg]))


def _obj_xy_yaw(entity) -> tuple[np.ndarray, float]:
    from genesis.utils.geom import quat_to_xyz

    pos = entity_pos(entity)
    quat = _to_np(entity.get_quat())
    yaw = float(quat_to_xyz(quat, degrees=True)[2])
    return pos, yaw


def _grasp_hand_z(entity, profile: GraspProfile) -> float:
    if not profile.center_align:
        return profile.grasp_hand_z
    aabb = entity_aabb(entity)
    z_min, z_max = float(aabb[0, 2]), float(aabb[1, 2])
    center_z = 0.5 * (z_min + z_max)
    half_height = 0.5 * (z_max - z_min)
    fingertip_z = center_z - GRASP_CENTER_DROP_FRAC * half_height
    z_jaw = fingertip_z + HAND_TO_FINGERTIP
    z_top = z_max + PALM_CLEARANCE
    return max(z_jaw, z_top)


def _ik(bundle, pos: np.ndarray, quat: np.ndarray) -> np.ndarray:
    hand = bundle.franka.get_link("hand")
    return bundle.franka.inverse_kinematics(link=hand, pos=pos, quat=quat)


def _record(recorder: RecorderFn | None, action) -> None:
    if recorder is not None:
        recorder(np.asarray(action, dtype=np.float32).reshape(-1))


def _settle(bundle, steps: int, recorder: RecorderFn | None = None) -> None:
    hold = np.array(FRANKA_QPOS)
    for _ in range(steps):
        _record(recorder, hold)
        bundle.franka.control_dofs_position(hold)
        bundle.scene.step()
        bundle.update_wrist_cam()


def _goto_plan(bundle, pos, quat, *, finger, num_waypoints=150, settle=20, recorder=None):
    qpos = _ik(bundle, pos, quat)
    qpos = _to_np(qpos)
    qpos[-2:] = finger
    path = bundle.franka.plan_path(qpos_goal=qpos, num_waypoints=num_waypoints)
    for wp in path:
        wp = _to_np(wp)
        _record(recorder, wp)
        bundle.franka.control_dofs_position(wp)
        bundle.scene.step()
        bundle.update_wrist_cam()
    for _ in range(settle):
        _record(recorder, qpos)
        bundle.franka.control_dofs_position(qpos)
        bundle.scene.step()
        bundle.update_wrist_cam()
    return qpos


def _goto_direct(bundle, pos, quat, *, finger_cmd, steps=120, close_force=None, recorder=None):
    qpos = _to_np(_ik(bundle, pos, quat))
    finger_target = GRIPPER_CLOSED if close_force is not None else finger_cmd
    arm = qpos[:-2]
    action = np.concatenate([arm, [finger_target, finger_target]])
    for _ in range(steps):
        _record(recorder, action)
        bundle.franka.control_dofs_position(qpos[:-2], MOTORS_DOF)
        if close_force is not None:
            bundle.franka.control_dofs_force(np.array([close_force, close_force]), FINGERS_DOF)
        else:
            bundle.franka.control_dofs_position(np.array([finger_cmd, finger_cmd]), FINGERS_DOF)
        bundle.scene.step()
        bundle.update_wrist_cam()
    return qpos


def _goto_interp(bundle, pos, quat, *, finger_cmd, close_force=None, recorder=None):
    q_goal = _to_np(_ik(bundle, pos, quat))
    arm_goal = q_goal[:-2]
    arm_start = _to_np(bundle.franka.get_dofs_position(MOTORS_DOF))
    dist = float(np.max(np.abs(arm_goal - arm_start))) if arm_goal.size else 0.0
    n = max(MOVE_MIN_STEPS, int(np.ceil(dist / MOVE_MAX_DQ))) if dist > 1e-9 else MOVE_MIN_STEPS
    finger_target = GRIPPER_CLOSED if close_force is not None else finger_cmd

    def _cmd(arm):
        action = np.concatenate([arm, [finger_target, finger_target]])
        _record(recorder, action)
        bundle.franka.control_dofs_position(arm, MOTORS_DOF)
        if close_force is not None:
            bundle.franka.control_dofs_force(np.array([close_force, close_force]), FINGERS_DOF)
        else:
            bundle.franka.control_dofs_position(np.array([finger_cmd, finger_cmd]), FINGERS_DOF)
        bundle.scene.step()
        bundle.update_wrist_cam()

    for i in range(1, n + 1):
        _cmd(arm_start + (arm_goal - arm_start) * (i / n))
    for _ in range(MOVE_SETTLE_STEPS):
        _cmd(arm_goal)
    return q_goal


def _descend_vertical(bundle, xy, z_from, z_to, quat, *, finger, steps=80, settle=15, recorder=None):
    qpos = None
    for z in np.linspace(z_from, z_to, steps):
        qpos = _to_np(_ik(bundle, np.array([xy[0], xy[1], z]), quat))
        qpos[-2:] = finger
        _record(recorder, qpos)
        bundle.franka.control_dofs_position(qpos)
        bundle.scene.step()
        bundle.update_wrist_cam()
    for _ in range(settle):
        _record(recorder, qpos)
        bundle.franka.control_dofs_position(qpos)
        bundle.scene.step()
        bundle.update_wrist_cam()
    return qpos


def run_pick_place(
    bundle,
    task,
    *,
    recorder: RecorderFn | None = None,
    save_frames: bool = False,
    settle_steps: int = 60,
    fruit: str | None = None,
    container: str | None = None,
) -> tuple[bool, list[tuple[str, Any]]]:
    """Execute a single pick-and-place for one (fruit, container) goal.

    ``task`` may be a ``TaskSpec``, ``ResolvedTask``, or any object exposing
    ``target_object`` / ``target_container``. Explicit ``fruit`` / ``container``
    override those fields (used for multi-step sequences).
    """
    fruit = fruit or task.target_object
    container = container or task.target_container
    if fruit.startswith("@"):
        raise ValueError(
            f"Unresolved spatial target {fruit!r}. Call resolve_task() before run_pick_place()."
        )
    pick_entity = bundle.objects[fruit]
    place_entity = bundle.objects[container]
    profile = PROFILES.get(fruit, GraspProfile())

    frames: list[tuple[str, Any]] = []

    def snap(tag: str) -> None:
        if save_frames and bundle.world_cam is not None:
            frames.append((tag, bundle.world_cam.render(rgb=True)[0]))

    _settle(bundle, settle_steps)
    snap("00_start")

    obj_pos, obj_yaw = _obj_xy_yaw(pick_entity)
    grasp_quat = _topdown_quat(obj_yaw + profile.yaw_offset)

    pregrasp = np.array([obj_pos[0], obj_pos[1], obj_pos[2] + PREGRASP_CLEARANCE])
    _goto_plan(bundle, pregrasp, grasp_quat, finger=GRIPPER_OPEN, recorder=recorder)
    snap("01_pregrasp")

    grasp_z = _grasp_hand_z(pick_entity, profile)
    _descend_vertical(
        bundle,
        (obj_pos[0], obj_pos[1]),
        pregrasp[2],
        grasp_z,
        grasp_quat,
        finger=GRIPPER_OPEN,
        recorder=recorder,
    )
    grasp = np.array([obj_pos[0], obj_pos[1], grasp_z])
    snap("02_reach")

    _goto_direct(
        bundle,
        grasp,
        grasp_quat,
        finger_cmd=GRIPPER_CLOSED,
        steps=100,
        close_force=profile.close_force,
        recorder=recorder,
    )
    snap("03_grasp")

    lift = np.array([grasp[0], grasp[1], LIFT_HAND_Z])
    _goto_interp(
        bundle,
        lift,
        grasp_quat,
        finger_cmd=GRIPPER_CLOSED,
        close_force=profile.close_force,
        recorder=recorder,
    )
    snap("04_lift")

    place_pos = entity_pos(place_entity)
    above = np.array([place_pos[0], place_pos[1], place_pos[2] + PLACE_HAND_Z_ABOVE])
    _goto_interp(
        bundle,
        above,
        grasp_quat,
        finger_cmd=GRIPPER_CLOSED,
        close_force=profile.close_force,
        recorder=recorder,
    )
    snap("05_above_target")

    _goto_direct(bundle, above, grasp_quat, finger_cmd=GRIPPER_OPEN, steps=80, recorder=recorder)
    snap("06_release")

    retreat = np.array([place_pos[0], place_pos[1], RETREAT_HAND_Z])
    _goto_direct(bundle, retreat, grasp_quat, finger_cmd=GRIPPER_OPEN, steps=80, recorder=recorder)
    _settle(bundle, settle_steps, recorder=recorder)
    snap("07_done")

    # Single-goal success (multi-step uses check_resolved_success at a higher level).
    from radeonvla.tasks import SubGoalSpec, TaskSpec

    synthetic = TaskSpec(
        task_id=f"_single_{fruit}_{container}",
        tier="L1",
        goals=(SubGoalSpec(object_name=fruit, container=container),),
        training_instructions=("",),
        evaluation_instructions=("",),
    )
    success, _, _ = check_placement_success(bundle, synthetic)
    return success, frames


def run_resolved_task(
    bundle,
    resolved,
    *,
    recorder: RecorderFn | None = None,
    save_frames: bool = False,
    settle_steps: int = 60,
    home_between_goals: bool = True,
) -> tuple[bool, list[tuple[str, Any]], dict]:
    """Execute all subgoals of a ``ResolvedTask`` in order (supports L2–L4)."""
    from radeonvla.grounding import check_resolved_success

    all_frames: list[tuple[str, Any]] = []
    for idx, goal in enumerate(resolved.goals):
        if idx > 0 and home_between_goals:
            # Return toward a safe home pose between subgoals so the second grasp
            # is not disturbed by residual arm motion over the bowls.
            _settle(bundle, 40, recorder=recorder)
            home = np.array(FRANKA_QPOS)
            for _ in range(80):
                if recorder is not None:
                    recorder(home.astype(np.float32))
                bundle.franka.control_dofs_position(home)
                bundle.scene.step()
                bundle.update_wrist_cam()
            _settle(bundle, 40, recorder=recorder)

        ok, frames = run_pick_place(
            bundle,
            resolved,
            recorder=recorder,
            save_frames=save_frames and idx == 0,
            settle_steps=settle_steps if idx == 0 else 40,
            fruit=goal.object_name,
            container=goal.container,
        )
        for tag, img in frames:
            all_frames.append((f"g{idx}_{tag}", img))
        if not ok:
            report = check_resolved_success(bundle, resolved)
            report["stopped_at_goal"] = idx
            return False, all_frames, report

    report = check_resolved_success(bundle, resolved)
    return bool(report["success"]), all_frames, report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the scripted dual-bowl sorting expert.")
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "base.yaml")
    parser.add_argument("--task", default=None, help="Single task id (default: cycle --suite).")
    parser.add_argument(
        "--suite",
        default="basic",
        choices=("basic", "advanced", "full", "multistep", "spatial", "rules"),
        help="Task suite to cycle when --task is omitted.",
    )
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--cpu", action="store_true")
    parser.add_argument("--backend", choices=("cpu", "gpu", "amdgpu"), default=None)
    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--save-frames", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    from radeonvla.grounding import resolve_task
    from radeonvla.randomize import EnvRandomizer, RandomizationConfig
    from radeonvla.tasks import list_task_ids

    args = parse_args(argv)
    backend = args.backend or ("cpu" if args.cpu else "gpu")
    init_genesis(backend=backend, seed=args.seed)
    bundle = build_scene(
        show_viewer=args.vis,
        add_world_cam=True,
        add_wrist_cam=True,
        appearance=AppearanceDR(seed=args.seed),
    )
    task_ids = [args.task] if args.task else list_task_ids(args.suite)
    randomizer = EnvRandomizer(
        bundle,
        RandomizationConfig(seed=args.seed, task_ids=tuple(task_ids)),
    )

    successes = 0
    for ep in range(args.episodes):
        task_id = task_ids[ep % len(task_ids)]
        task = randomizer.reset(seed=args.seed + ep, task_id=task_id)
        resolved = resolve_task(bundle, task, train=True)
        ok, frames, report = run_resolved_task(
            bundle,
            resolved,
            save_frames=args.save_frames and ep == 0,
        )
        successes += int(ok)
        goals_str = " -> ".join(f"{g.object_name}:{g.container}" for g in resolved.goals)
        print(
            f"[expert] ep={ep} task={task.task_id} tier={task.tier} "
            f"goals=[{goals_str}] success={ok} partial={report.get('partial_success_rate', 0):.2f}"
        )
        if frames:
            import imageio.v2 as imageio

            FRAMES_DIR.mkdir(parents=True, exist_ok=True)
            for tag, img in frames:
                imageio.imwrite(FRAMES_DIR / f"{tag}.png", img)
            print(f"[expert] saved {len(frames)} frames to {FRAMES_DIR}")

    print(f"[expert] success rate: {successes}/{args.episodes}")
    return 0 if successes == args.episodes else 1


if __name__ == "__main__":
    raise SystemExit(main())
