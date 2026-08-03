"""Record scripted dual-bowl sorting demonstrations into a LeRobot dataset.

End-to-end data collection for SmolVLA training:

1. Build the Genesis dual-bowl Franka scene.
2. Reset with pose (and optional physics) randomization.
3. Run the scripted expert for a language-conditioned task.
4. Decimate 100 Hz control to dataset FPS and write successful episodes.

Example::

    python -m radeonvla.record_dataset --episodes 20 --backend cpu --overwrite
    python -m radeonvla.record_dataset --episodes 100 --backend amdgpu \\
        --dr-appearance --dr-object-color --dr-runtime --overwrite
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np

from radeonvla.expert import run_resolved_task
from radeonvla.grounding import resolve_task
from radeonvla.paths import DATASETS_DIR, PROJECT_ROOT
from radeonvla.protocol import CONTROL_HZ, DATASET_FPS, JOINT_NAMES, dataset_features
from radeonvla.randomize import EnvRandomizer, RandomizationConfig, RuntimeDR
from radeonvla.scene import AppearanceDR, build_scene, init_genesis
from radeonvla.tasks import SUITES, get_task, list_task_ids


class EpisodeRecorder:
    """Decimate 100 Hz control steps to dataset FPS and buffer one episode."""

    def __init__(self, bundle, *, fps: int = DATASET_FPS, img_wh: tuple[int, int] = (320, 240)):
        self.bundle = bundle
        self.fps = fps
        self.img_w, self.img_h = img_wh
        self.steps_per_frame = CONTROL_HZ / fps
        self.reset()

    def reset(self) -> None:
        self.states: list[np.ndarray] = []
        self.actions: list[np.ndarray] = []
        self.world_imgs: list[np.ndarray] = []
        self.wrist_imgs: list[np.ndarray] = []
        # Capture the first control step of the episode.
        self._accum = self.steps_per_frame

    def __len__(self) -> int:
        return len(self.states)

    @staticmethod
    def _to_np(x) -> np.ndarray:
        if hasattr(x, "detach"):
            x = x.detach().cpu().numpy()
        return np.asarray(x)

    def _resize(self, img) -> np.ndarray:
        import cv2

        img = self._to_np(img)
        if img.ndim == 3 and img.shape[-1] > 3:
            img = img[..., :3]
        if (img.shape[1], img.shape[0]) != (self.img_w, self.img_h):
            img = cv2.resize(img, (self.img_w, self.img_h), interpolation=cv2.INTER_AREA)
        if img.dtype != np.uint8:
            img = np.clip(img, 0, 255).astype(np.uint8)
        return np.ascontiguousarray(img, dtype=np.uint8)

    def on_step(self, action) -> None:
        self._accum += 1.0
        if self._accum < self.steps_per_frame:
            return
        self._accum -= self.steps_per_frame

        if self.bundle.world_cam is None or self.bundle.wrist_cam is None:
            raise RuntimeError("Recording requires world and wrist cameras.")

        state = self._to_np(self.bundle.franka.get_qpos()).reshape(-1).astype(np.float32)
        action_arr = self._to_np(action).reshape(-1).astype(np.float32)
        if state.shape[0] != len(JOINT_NAMES) or action_arr.shape[0] != len(JOINT_NAMES):
            raise RuntimeError(
                f"Expected {len(JOINT_NAMES)}-D state/action, got state={state.shape} action={action_arr.shape}"
            )
        world = self._resize(self.bundle.world_cam.render(rgb=True)[0])
        wrist = self._resize(self.bundle.wrist_cam.render(rgb=True)[0])
        self.states.append(state)
        self.actions.append(action_arr)
        self.world_imgs.append(world)
        self.wrist_imgs.append(wrist)

    def flush_to(self, dataset, task: str) -> None:
        for state, action, world, wrist in zip(
            self.states, self.actions, self.world_imgs, self.wrist_imgs, strict=True
        ):
            dataset.add_frame(
                {
                    "observation.state": state,
                    "action": action,
                    "observation.images.world": world,
                    "observation.images.wrist": wrist,
                    "task": task,
                }
            )
        dataset.save_episode()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "base.yaml")
    parser.add_argument("--episodes", type=int, default=20, help="Number of successful episodes to keep.")
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=0,
        help="Max expert rollouts (0 => 5x episodes). Stops early if successes reached.",
    )
    parser.add_argument("--task", default=None, help="Single task id.")
    parser.add_argument("--tasks", nargs="*", default=None, help="Optional explicit task id list.")
    parser.add_argument(
        "--suite",
        default="full",
        choices=sorted(SUITES),
        help="Task suite when --task/--tasks omitted (default: full advanced set).",
    )
    parser.add_argument("--repo-id", default="visiobot/radeonvla_reflex")
    parser.add_argument("--dataset-root", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--fps", type=int, default=DATASET_FPS)
    parser.add_argument("--img-width", type=int, default=320)
    parser.add_argument("--img-height", type=int, default=240)
    parser.add_argument("--cpu", action="store_true")
    parser.add_argument("--backend", choices=("cpu", "gpu", "amdgpu"), default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--vcodec", default="libsvtav1", help="RGB video codec for LeRobot.")
    parser.add_argument("--dr-appearance", action="store_true")
    parser.add_argument("--dr-object-color", action="store_true")
    parser.add_argument("--dr-table-jitter", type=float, default=0.15)
    parser.add_argument("--dr-fov-jitter", type=float, default=0.0)
    parser.add_argument("--dr-rebuild-every", type=int, default=0, help="Rebuild scene every N successes (0=off).")
    parser.add_argument("--dr-runtime", action="store_true")
    parser.add_argument("--dr-friction", type=float, nargs=2, default=[0.7, 1.3])
    parser.add_argument("--dr-mass", type=float, nargs=2, default=[0.8, 1.2])
    parser.add_argument("--dr-cam-pos", type=float, default=0.0)
    parser.add_argument("--dr-cam-lookat", type=float, default=0.0)
    parser.add_argument("--keep-failures", action="store_true", help="Also keep failed episodes.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Write a JSON manifest next to the dataset (default: <root>/recording_manifest.json).",
    )
    return parser.parse_args(argv)


def _instruction_for(task_id: str, *, train: bool = True) -> str:
    task = get_task(task_id)
    pool = task.training_instructions if train else task.evaluation_instructions
    return pool[0]


def _task_cycle(args: argparse.Namespace) -> list[str]:
    if args.task:
        get_task(args.task)
        return [args.task]
    if args.tasks:
        for task_id in args.tasks:
            get_task(task_id)  # validate
        return list(args.tasks)
    return list_task_ids(args.suite)


def _rebuild_scene(backend: str, seed: int, domain: int, args: argparse.Namespace):
    """Rebuild Genesis for a new appearance domain (Layer-A DR)."""
    import genesis as gs

    if hasattr(gs, "destroy"):
        try:
            gs.destroy()
        except Exception:
            pass
    init_genesis(backend=backend, seed=seed + domain)
    appearance = AppearanceDR(
        enabled=args.dr_appearance,
        table_color_jitter=args.dr_table_jitter,
        randomize_object_color=args.dr_object_color,
        fov_jitter_deg=args.dr_fov_jitter,
        seed=seed + domain,
    )
    return build_scene(
        show_viewer=False,
        add_world_cam=True,
        add_wrist_cam=True,
        appearance=appearance,
    )


def main(argv: list[str] | None = None) -> int:
    from lerobot.configs.video import RGBEncoderConfig
    from lerobot.datasets.lerobot_dataset import LeRobotDataset

    args = parse_args(argv)
    backend = args.backend or ("cpu" if args.cpu else "gpu")
    dataset_root = Path(args.dataset_root or (DATASETS_DIR / args.repo_id.split("/")[-1]))
    if not dataset_root.is_absolute():
        dataset_root = (PROJECT_ROOT / dataset_root).resolve()
    max_attempts = args.max_attempts if args.max_attempts > 0 else max(args.episodes * 5, args.episodes)

    if dataset_root.exists():
        if not args.overwrite:
            raise FileExistsError(f"{dataset_root} exists; pass --overwrite to replace it.")
        shutil.rmtree(dataset_root)
    dataset_root.parent.mkdir(parents=True, exist_ok=True)

    task_cycle = _task_cycle(args)
    features = dataset_features(args.img_height, args.img_width)

    init_genesis(backend=backend, seed=args.seed)
    domain = 0
    bundle = _rebuild_scene(backend, args.seed, domain, args) if args.dr_appearance else build_scene(
        show_viewer=False,
        add_world_cam=True,
        add_wrist_cam=True,
        appearance=AppearanceDR(
            enabled=args.dr_appearance,
            table_color_jitter=args.dr_table_jitter,
            randomize_object_color=args.dr_object_color,
            fov_jitter_deg=args.dr_fov_jitter,
            seed=args.seed,
        ),
    )

    runtime = RuntimeDR(
        enabled=args.dr_runtime,
        friction_ratio_range=tuple(args.dr_friction),
        mass_ratio_range=tuple(args.dr_mass),
        cam_pos_jitter=args.dr_cam_pos,
        cam_lookat_jitter=args.dr_cam_lookat,
    )
    randomizer = EnvRandomizer(
        bundle,
        RandomizationConfig(seed=args.seed, runtime_dr=runtime, task_ids=tuple(task_cycle)),
    )
    recorder = EpisodeRecorder(bundle, fps=args.fps, img_wh=(args.img_width, args.img_height))

    dataset = LeRobotDataset.create(
        repo_id=args.repo_id,
        fps=args.fps,
        root=str(dataset_root),
        robot_type="franka",
        features=features,
        use_videos=True,
        image_writer_threads=4,
        batch_encoding_size=1,
        rgb_encoder=RGBEncoderConfig(vcodec=args.vcodec),
    )

    successes = 0
    failures_saved = 0
    attempts = 0
    ep = 0
    per_task: dict[str, int] = {t: 0 for t in task_cycle}

    while successes < args.episodes and attempts < max_attempts:
        if args.dr_rebuild_every and args.dr_appearance and successes > 0:
            target_domain = successes // args.dr_rebuild_every
            if target_domain != domain:
                domain = target_domain
                bundle = _rebuild_scene(backend, args.seed, domain, args)
                randomizer = EnvRandomizer(
                    bundle,
                    RandomizationConfig(
                        seed=args.seed + attempts,
                        runtime_dr=runtime,
                        task_ids=tuple(task_cycle),
                    ),
                )
                recorder = EpisodeRecorder(bundle, fps=args.fps, img_wh=(args.img_width, args.img_height))
                print(f"[record] rebuilt appearance domain {domain}")

        task_id = task_cycle[ep % len(task_cycle)]
        task = randomizer.reset(seed=args.seed + attempts, task_id=task_id)
        instruction = _instruction_for(task.task_id, train=True)
        resolved = resolve_task(bundle, task, instruction=instruction, train=True)
        recorder.reset()
        ok, _, report = run_resolved_task(bundle, resolved, recorder=recorder.on_step)
        attempts += 1
        goals_str = ",".join(f"{g.object_name}->{g.container}" for g in resolved.goals)

        if ok and len(recorder) > 0:
            recorder.flush_to(dataset, instruction)
            successes += 1
            per_task[task.task_id] = per_task.get(task.task_id, 0) + 1
            ep += 1
            print(
                f"[record] success {successes}/{args.episodes} "
                f"task={task.task_id} tier={task.tier} goals=[{goals_str}] "
                f"frames={len(recorder)} attempt={attempts}"
            )
        elif args.keep_failures and len(recorder) > 0:
            recorder.flush_to(dataset, "FAILED: " + instruction)
            failures_saved += 1
            print(
                f"[record] failure saved task={task.task_id} tier={task.tier} "
                f"partial={report.get('partial_success_rate', 0):.2f} frames={len(recorder)}"
            )
        else:
            reason = "empty" if len(recorder) == 0 else "failed"
            print(
                f"[record] discarded ({reason}) task={task.task_id} tier={task.tier} "
                f"partial={report.get('partial_success_rate', 0):.2f} attempt={attempts}"
            )

    dataset.finalize()

    manifest = {
        "repo_id": args.repo_id,
        "dataset_root": str(dataset_root),
        "fps": args.fps,
        "image_size": [args.img_height, args.img_width],
        "joint_names": list(JOINT_NAMES),
        "features": features,
        "successes": successes,
        "failures_saved": failures_saved,
        "attempts": attempts,
        "per_task_successes": per_task,
        "task_cycle": task_cycle,
        "suite": args.suite,
        "seed": args.seed,
        "backend": backend,
        "dr_appearance": args.dr_appearance,
        "dr_runtime": args.dr_runtime,
    }
    manifest_path = args.manifest or (dataset_root / "recording_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"[record] done: {successes} successes (+{failures_saved} failures saved) in {attempts} attempts")
    print(f"[record] dataset -> {dataset_root}")
    print(f"[record] manifest -> {manifest_path}")
    if successes < args.episodes:
        print(f"[record] WARNING: only {successes}/{args.episodes} successes before max_attempts={max_attempts}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
