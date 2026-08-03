"""Record scripted dual-bowl sorting demonstrations into a LeRobot dataset."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np

from radeonvla.expert import run_pick_place
from radeonvla.paths import DATASETS_DIR, PROJECT_ROOT
from radeonvla.protocol import CONTROL_HZ, DATASET_FPS, JOINT_NAMES, dataset_features
from radeonvla.randomize import EnvRandomizer, RandomizationConfig, RuntimeDR
from radeonvla.scene import AppearanceDR, build_scene, init_genesis
from radeonvla.tasks import TASKS, get_task


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
        if (img.shape[1], img.shape[0]) != (self.img_w, self.img_h):
            img = cv2.resize(img, (self.img_w, self.img_h), interpolation=cv2.INTER_AREA)
        return np.ascontiguousarray(img, dtype=np.uint8)

    def on_step(self, action) -> None:
        self._accum += 1.0
        if self._accum < self.steps_per_frame:
            return
        self._accum -= self.steps_per_frame

        state = self._to_np(self.bundle.franka.get_qpos()).reshape(-1).astype(np.float32)
        action_arr = self._to_np(action).reshape(-1).astype(np.float32)
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
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--task", default=None, help="Single task id; default cycles all tasks.")
    parser.add_argument("--repo-id", default="visiobot/radeonvla_reflex")
    parser.add_argument("--dataset-root", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--fps", type=int, default=DATASET_FPS)
    parser.add_argument("--img-width", type=int, default=320)
    parser.add_argument("--img-height", type=int, default=240)
    parser.add_argument("--cpu", action="store_true")
    parser.add_argument("--backend", choices=("cpu", "gpu", "amdgpu"), default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dr-appearance", action="store_true")
    parser.add_argument("--dr-object-color", action="store_true")
    parser.add_argument("--dr-table-jitter", type=float, default=0.15)
    parser.add_argument("--dr-fov-jitter", type=float, default=0.0)
    parser.add_argument("--dr-rebuild-every", type=int, default=0, help="Rebuild scene every N successes.")
    parser.add_argument("--dr-runtime", action="store_true")
    parser.add_argument("--dr-friction", type=float, nargs=2, default=[0.7, 1.3])
    parser.add_argument("--dr-mass", type=float, nargs=2, default=[0.8, 1.2])
    parser.add_argument("--keep-failures", action="store_true", help="Also keep failed episodes.")
    return parser.parse_args(argv)


def _instruction_for(task_id: str, *, train: bool = True) -> str:
    task = get_task(task_id)
    pool = task.training_instructions if train else task.evaluation_instructions
    return pool[0]


def main(argv: list[str] | None = None) -> int:
    from lerobot.configs.video import RGBEncoderConfig
    from lerobot.datasets.lerobot_dataset import LeRobotDataset

    args = parse_args(argv)
    backend = args.backend or ("cpu" if args.cpu else "gpu")
    dataset_root = args.dataset_root or (DATASETS_DIR / args.repo_id.split("/")[-1])
    dataset_root = Path(dataset_root)

    if dataset_root.exists():
        if not args.overwrite:
            raise FileExistsError(f"{dataset_root} exists; pass --overwrite to replace it.")
        shutil.rmtree(dataset_root)

    task_cycle = [args.task] if args.task else sorted(TASKS)
    features = dataset_features(args.img_height, args.img_width)

    init_genesis(backend=backend, seed=args.seed)

    def _make_bundle(domain: int):
        appearance = AppearanceDR(
            enabled=args.dr_appearance,
            table_color_jitter=args.dr_table_jitter,
            randomize_object_color=args.dr_object_color,
            fov_jitter_deg=args.dr_fov_jitter,
            seed=args.seed + domain,
        )
        return build_scene(
            show_viewer=False,
            add_world_cam=True,
            add_wrist_cam=True,
            appearance=appearance,
        )

    domain = 0
    bundle = _make_bundle(domain)
    runtime = RuntimeDR(
        enabled=args.dr_runtime,
        friction_ratio_range=tuple(args.dr_friction),
        mass_ratio_range=tuple(args.dr_mass),
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
        video_encoding_batch_size=0,
        encoder_cfg=RGBEncoderConfig(),
    )

    successes = 0
    attempts = 0
    ep = 0
    while successes < args.episodes:
        task_id = task_cycle[ep % len(task_cycle)]
        task = randomizer.reset(seed=args.seed + attempts, task_id=task_id)
        instruction = _instruction_for(task.task_id, train=True)
        recorder.reset()
        ok, _ = run_pick_place(bundle, task, recorder=recorder.on_step)
        attempts += 1
        if ok or args.keep_failures:
            if len(recorder) == 0:
                print(f"[record] warning: empty episode for {task.task_id}, retrying")
                continue
            recorder.flush_to(dataset, instruction)
            if ok:
                successes += 1
                ep += 1
                print(f"[record] saved success {successes}/{args.episodes} task={task.task_id} frames={len(recorder)}")
                if args.dr_rebuild_every and successes % args.dr_rebuild_every == 0 and successes < args.episodes:
                    domain += 1
                    bundle = _make_bundle(domain)
                    randomizer = EnvRandomizer(
                        bundle,
                        RandomizationConfig(seed=args.seed + attempts, runtime_dr=runtime, task_ids=tuple(task_cycle)),
                    )
                    recorder = EpisodeRecorder(bundle, fps=args.fps, img_wh=(args.img_width, args.img_height))
            else:
                print(f"[record] saved failure task={task.task_id} frames={len(recorder)}")
        else:
            print(f"[record] discarded failure task={task.task_id}")

    print(f"[record] done: {successes} successes in {attempts} attempts -> {dataset_root}")
    print(f"[record] joint schema: {JOINT_NAMES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
