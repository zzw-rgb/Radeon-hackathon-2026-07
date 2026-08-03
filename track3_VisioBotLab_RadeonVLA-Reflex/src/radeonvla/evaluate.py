"""Closed-loop evaluation with interruptible commands and recovery retries."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch

from radeonvla.grounding import check_resolved_success, resolve_task
from radeonvla.paths import EVAL_RESULTS_DIR, EVAL_VIDEOS_DIR, PROJECT_ROOT
from radeonvla.protocol import CONTROL_HZ, DATASET_FPS
from radeonvla.randomize import EnvRandomizer, RandomizationConfig
from radeonvla.safety import (
    CommandSession,
    FailureDetector,
    RecoveryPolicy,
    SafetyMonitor,
)
from radeonvla.scene import AppearanceDR, build_scene, init_genesis
from radeonvla.scene_config import FRANKA_QPOS
from radeonvla.tasks import SUITES, get_task, list_task_ids

STATE_KEY = "observation.state"
POST_SUCCESS_SECONDS = 0.6


@dataclass
class PolicyBundle:
    policy: Any
    preprocessor: Any
    postprocessor: Any
    device: torch.device
    fps: int
    image_keys: list[str]
    image_hw: tuple[int, int]
    use_amp: bool = False
    policy_type: str = "unknown"

    def reset(self) -> None:
        self.policy.reset()

    def select_action(self, observation: dict[str, np.ndarray], task: str | None) -> np.ndarray:
        from lerobot.common.control_utils import predict_action

        action = predict_action(
            observation,
            self.policy,
            self.device,
            self.preprocessor,
            self.postprocessor,
            use_amp=self.use_amp,
            task=task,
            robot_type="franka",
        )
        return action.detach().cpu().numpy().reshape(-1).astype(np.float32)


def _load_rename_map(policy_path: str) -> dict:
    path = Path(policy_path) / "train_config.json"
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8")).get("rename_map") or {}
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def load_policy(
    policy_path: str,
    repo_id: str,
    dataset_root: str | None,
    device_str: str,
    *,
    use_amp: bool = False,
    rename_map: dict | None = None,
) -> PolicyBundle:
    from lerobot.configs.policies import PreTrainedConfig
    from lerobot.datasets.lerobot_dataset import LeRobotDatasetMetadata
    from lerobot.policies.factory import make_policy, make_pre_post_processors
    from lerobot.utils.device_utils import get_safe_torch_device

    device = get_safe_torch_device(device_str, log=True)
    # Prefer metadata-only load; training used pyav for ROCm-friendly decoding.
    ds_meta = LeRobotDatasetMetadata(repo_id, root=dataset_root)
    cfg = PreTrainedConfig.from_pretrained(policy_path)
    cfg.pretrained_path = policy_path
    cfg.device = str(device)

    if rename_map is None:
        rename_map = _load_rename_map(policy_path)
    if rename_map:
        print(f"[eval] camera rename_map: {rename_map}")

    policy = make_policy(cfg=cfg, ds_meta=ds_meta, rename_map=rename_map)
    policy.eval()
    preprocessor, postprocessor = make_pre_post_processors(
        policy_cfg=cfg,
        pretrained_path=policy_path,
        preprocessor_overrides={"device_processor": {"device": str(device)}},
    )
    image_keys = [k for k in ds_meta.features if k.startswith("observation.images")]
    if not image_keys:
        raise RuntimeError(f"No image features in dataset {repo_id!r}")
    h, w, _ = ds_meta.features[image_keys[0]]["shape"]
    return PolicyBundle(
        policy=policy,
        preprocessor=preprocessor,
        postprocessor=postprocessor,
        device=device,
        fps=int(ds_meta.fps or DATASET_FPS),
        image_keys=image_keys,
        image_hw=(h, w),
        use_amp=use_amp,
        policy_type=getattr(cfg, "type", "unknown"),
    )


def _to_np(x) -> np.ndarray:
    if hasattr(x, "detach"):
        x = x.detach().cpu().numpy()
    return np.asarray(x)


def _render_camera(cam, size_wh: tuple[int, int]) -> np.ndarray:
    import cv2

    img = _to_np(cam.render(rgb=True)[0])
    w, h = size_wh
    if (img.shape[1], img.shape[0]) != (w, h):
        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    return np.ascontiguousarray(img, dtype=np.uint8)


def build_observation(bundle, pb: PolicyBundle) -> dict[str, np.ndarray]:
    h, w = pb.image_hw
    obs: dict[str, np.ndarray] = {
        STATE_KEY: _to_np(bundle.franka.get_qpos()).reshape(-1).astype(np.float32),
    }
    cam_for_key = {
        "observation.images.world": bundle.world_cam,
        "observation.images.wrist": bundle.wrist_cam,
    }
    for key in pb.image_keys:
        cam = cam_for_key.get(key)
        if cam is None:
            raise RuntimeError(f"Missing camera for feature {key!r}")
        obs[key] = _render_camera(cam, (w, h))
    return obs


def apply_action(bundle, action: np.ndarray | list[float], n_sim_steps: int) -> None:
    action_arr = np.asarray(action, dtype=np.float64).reshape(-1)
    for _ in range(n_sim_steps):
        bundle.franka.control_dofs_position(action_arr)
        bundle.scene.step()
        bundle.update_wrist_cam()


@dataclass
class EpisodeResult:
    episode_id: str
    seed: int
    task_id: str
    instruction: str
    success: bool
    object_correct: bool
    target_correct: bool
    first_attempt_success: bool
    events: list[dict[str, Any]] = field(default_factory=list)
    retry_count: int = 0
    completion_time_s: float = 0.0
    inference_latency_ms: list[float] = field(default_factory=list)
    failure_reason: str | None = None
    video_uri: str | None = None
    tier: str = "L1"
    n_goals: int = 1
    partial_success_rate: float = 0.0
    resolved_goals: list[dict[str, str]] = field(default_factory=list)


def run_episode(
    bundle,
    pb: PolicyBundle,
    *,
    task_id: str,
    seed: int,
    instruction: str | None = None,
    max_steps: int | None = None,
    max_retries: int = 1,
    interrupt_at_step: int | None = None,
    interrupt_task_id: str | None = None,
    save_video: bool = False,
    video_path: Path | None = None,
) -> EpisodeResult:
    task = get_task(task_id)
    max_steps = max_steps or task.max_steps
    instruction = instruction or task.evaluation_instructions[0]
    session = CommandSession(instruction=instruction, task_id=task_id)
    safety = SafetyMonitor()
    recovery = RecoveryPolicy(max_retries=max_retries)

    randomizer = EnvRandomizer(bundle, RandomizationConfig(seed=seed))
    randomizer.reset(seed=seed, task_id=task_id)
    resolved = resolve_task(bundle, task, instruction=instruction, train=False)
    # Failure detector tracks the *current* subgoal fruit (first incomplete goal).
    detector = FailureDetector(task, max_steps=max_steps)
    events: list[dict[str, Any]] = [
        {
            "type": "resolved_goals",
            "tier": resolved.tier,
            "goals": [{"object": g.object_name, "container": g.container} for g in resolved.goals],
        }
    ]

    pb.reset()
    safety.reset()

    n_sim = max(1, int(round(CONTROL_HZ / pb.fps)))
    latencies: list[float] = []
    frames: list[np.ndarray] = []
    retry_count = 0
    first_attempt_success = False
    t0 = time.perf_counter()
    policy_step = 0
    active = True
    last_action = list(FRANKA_QPOS)

    while active and policy_step < max_steps:
        if interrupt_at_step is not None and policy_step == interrupt_at_step and interrupt_task_id:
            new_task = get_task(interrupt_task_id)
            new_instruction = new_task.evaluation_instructions[0]
            session.set_command(instruction=new_instruction, task_id=interrupt_task_id, step=policy_step)
            task = new_task
            max_steps = max(max_steps, task.max_steps)
            resolved = resolve_task(bundle, task, instruction=new_instruction, train=False)
            detector = FailureDetector(task, max_steps=max_steps)
            pb.reset()
            events.append(
                {
                    "type": "interrupt_inject",
                    "step": policy_step,
                    "new_task": interrupt_task_id,
                    "version": session.version,
                    "new_goals": [
                        {"object": g.object_name, "container": g.container} for g in resolved.goals
                    ],
                }
            )

        obs = build_observation(bundle, pb)
        t_inf0 = time.perf_counter()
        raw_action = pb.select_action(obs, session.instruction)
        latencies.append((time.perf_counter() - t_inf0) * 1000.0)

        decision = safety.process(raw_action, command_version=session.version)
        if decision.invalidate_chunk:
            pb.reset()
            events.append({"type": "chunk_invalidated", "step": policy_step, "reason": decision.reason})

        action = np.asarray(decision.action, dtype=np.float64)
        apply_action(bundle, action, n_sim)
        last_action = action.tolist()

        if save_video:
            primary = obs[pb.image_keys[0]]
            h, w = primary.shape[:2]
            panels = [primary]
            if bundle.wrist_cam is not None:
                panels.append(_render_camera(bundle.wrist_cam, (w, h)))
            if bundle.video_cam is not None:
                panels.append(_render_camera(bundle.video_cam, (w, h)))
            frames.append(np.ascontiguousarray(np.hstack(panels) if len(panels) > 1 else primary))

        fail = detector.observe_step(bundle, step=policy_step, action=action, unsafe=not decision.accepted)
        report_now = check_resolved_success(bundle, resolved)
        if report_now["success"]:
            if retry_count == 0:
                first_attempt_success = True
            hold_steps = int(POST_SUCCESS_SECONDS * pb.fps)
            for _ in range(hold_steps):
                apply_action(bundle, last_action, n_sim)
                if save_video:
                    obs_hold = build_observation(bundle, pb)
                    frames.append(obs_hold[pb.image_keys[0]])
            active = False
            break

        if fail is not None and recovery.should_retry(retry_count, fail):
            retry_count += 1
            events.append({"type": "recovery", "step": policy_step, "reason": fail.value, "retry": retry_count})
            recover = np.asarray(recovery.recovery_action(), dtype=np.float64)
            for _ in range(recovery.retreat_steps):
                apply_action(bundle, recover, n_sim)
            pb.reset()
            safety.reset()
            detector = FailureDetector(task, max_steps=max_steps)
            fail = None
        elif fail is not None:
            events.append({"type": "terminal_failure", "step": policy_step, "reason": fail.value})
            active = False
            break

        policy_step += 1

    final_report = check_resolved_success(bundle, resolved)
    diag = detector.finalize(bundle)
    elapsed = time.perf_counter() - t0
    video_uri = None
    if save_video and frames and video_path is not None:
        import imageio.v2 as imageio

        video_path.parent.mkdir(parents=True, exist_ok=True)
        imageio.mimsave(video_path, frames, fps=pb.fps)
        video_uri = str(video_path)

    success = bool(final_report["success"])
    if success and retry_count == 0:
        first_attempt_success = True

    failure_reason = None
    if not success:
        if diag.failure_reason.value != "none":
            failure_reason = diag.failure_reason.value
        elif final_report["n_success"] == 0:
            failure_reason = "no_subgoal_completed"
        else:
            failure_reason = "partial_multi_goal"

    return EpisodeResult(
        episode_id=f"{task_id}_{seed}",
        seed=seed,
        task_id=session.task_id,
        instruction=session.instruction,
        success=success,
        object_correct=bool(final_report["object_correct"]),
        target_correct=bool(final_report["target_correct"]),
        first_attempt_success=first_attempt_success and success,
        events=events + list(session.events) + list(diag.events) + [{"type": "goal_report", **final_report}],
        retry_count=retry_count,
        completion_time_s=elapsed,
        inference_latency_ms=latencies,
        failure_reason=failure_reason,
        video_uri=video_uri,
        tier=resolved.tier,
        n_goals=int(final_report["n_goals"]),
        partial_success_rate=float(final_report["partial_success_rate"]),
        resolved_goals=[{"object": g.object_name, "container": g.container} for g in resolved.goals],
    )


def summarize(episodes: list[EpisodeResult]) -> dict[str, Any]:
    n = max(1, len(episodes))
    by_tier: dict[str, list[EpisodeResult]] = {}
    for e in episodes:
        by_tier.setdefault(e.tier, []).append(e)
    tier_rates = {
        tier: sum(e.success for e in eps) / max(1, len(eps)) for tier, eps in sorted(by_tier.items())
    }
    return {
        "num_episodes": len(episodes),
        "task_success_rate": sum(e.success for e in episodes) / n,
        "object_accuracy": sum(e.object_correct for e in episodes) / n,
        "target_accuracy": sum(e.target_correct for e in episodes) / n,
        "first_attempt_success": sum(e.first_attempt_success for e in episodes) / n,
        "final_success": sum(e.success for e in episodes) / n,
        "mean_partial_success_rate": float(np.mean([e.partial_success_rate for e in episodes])),
        "success_by_tier": tier_rates,
        "recovery_success": (
            sum(e.success and e.retry_count > 0 for e in episodes)
            / max(1, sum(e.retry_count > 0 for e in episodes))
        ),
        "mean_completion_time_s": float(np.mean([e.completion_time_s for e in episodes])),
        "p95_completion_time_s": float(np.percentile([e.completion_time_s for e in episodes], 95)),
        "mean_inference_latency_ms": float(
            np.mean([x for e in episodes for x in e.inference_latency_ms] or [0.0])
        ),
        "p95_inference_latency_ms": float(
            np.percentile([x for e in episodes for x in e.inference_latency_ms] or [0.0], 95)
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "eval.yaml")
    parser.add_argument("--policy-path", required=True)
    parser.add_argument("--repo-id", default="visiobot/radeonvla_reflex")
    parser.add_argument("--dataset-root", default=None)
    parser.add_argument("--episodes", type=int, default=None, help="Total episodes (overrides per-task).")
    parser.add_argument("--episodes-per-task", type=int, default=2)
    parser.add_argument("--tasks", nargs="*", default=None)
    parser.add_argument(
        "--suite",
        default="full",
        choices=sorted(SUITES),
        help="Task suite when --tasks is omitted.",
    )
    parser.add_argument("--seed-start", type=int, default=20000)
    parser.add_argument("--max-retries", type=int, default=1)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--cpu", action="store_true")
    parser.add_argument("--backend", choices=("cpu", "gpu", "amdgpu"), default=None)
    parser.add_argument("--save-video", action="store_true")
    parser.add_argument("--interrupt-demo", action="store_true", help="Inject a mid-episode command change.")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    import subprocess

    args = parse_args(argv)
    backend = args.backend or ("cpu" if args.cpu else "gpu")
    device = "cpu" if args.cpu else args.device
    tasks = args.tasks or list_task_ids(args.suite)

    init_genesis(backend=backend, seed=args.seed_start)
    bundle = build_scene(
        show_viewer=False,
        add_world_cam=True,
        add_wrist_cam=True,
        add_video_cam=args.save_video,
        appearance=AppearanceDR(seed=args.seed_start),
    )
    pb = load_policy(args.policy_path, args.repo_id, args.dataset_root, device)

    results: list[EpisodeResult] = []
    ep_index = 0
    per_task = args.episodes_per_task
    if args.episodes is not None:
        # Distribute total episodes across tasks.
        per_task = max(1, args.episodes // max(1, len(tasks)))

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = EVAL_RESULTS_DIR / f"eval_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    video_dir = EVAL_VIDEOS_DIR / f"eval_{stamp}"

    for task_id in tasks:
        for _ in range(per_task):
            seed = args.seed_start + ep_index
            video_path = video_dir / f"{task_id}_{seed}.mp4" if args.save_video else None
            interrupt_at = 40 if args.interrupt_demo and ep_index == 0 else None
            interrupt_task = None
            if interrupt_at is not None:
                # Prefer flipping a basic L1 side; fall back to a multi-step task.
                if task_id.endswith("_left"):
                    interrupt_task = task_id[:-5] + "_right"
                elif task_id.endswith("_right"):
                    interrupt_task = task_id[:-6] + "_left"
                else:
                    interrupt_task = "banana_right" if task_id != "banana_right" else "plum_left"
                try:
                    get_task(interrupt_task)
                except ValueError:
                    interrupt_task = "banana_left"
            result = run_episode(
                bundle,
                pb,
                task_id=task_id,
                seed=seed,
                max_retries=args.max_retries,
                interrupt_at_step=interrupt_at,
                interrupt_task_id=interrupt_task,
                save_video=args.save_video,
                video_path=video_path,
            )
            results.append(result)
            print(
                f"[eval] {result.episode_id} success={result.success} "
                f"first={result.first_attempt_success} retries={result.retry_count} "
                f"reason={result.failure_reason}"
            )
            ep_index += 1

    summary = summarize(results)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = "0" * 40

    payload = {
        "experiment_id": f"eval_{stamp}",
        "git_commit": commit if len(commit) == 40 else "0" * 40,
        "environment": {
            "gpu": str(pb.device),
            "rocm": str(torch.version.hip),
            "torch": torch.__version__,
            "genesis": "1.1.2",
            "lerobot": "0.6.0",
        },
        "checkpoint": {
            "uri": args.policy_path,
            "sha256": "0" * 64,
        },
        "config": {
            "tasks": tasks,
            "seed_start": args.seed_start,
            "max_retries": args.max_retries,
            "backend": backend,
        },
        "summary": summary,
        "episodes": [asdict(e) for e in results],
    }

    out = args.output or (run_dir / "results.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"[eval] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
