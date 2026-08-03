"""One-command pipeline stages for local smoke and remote full runs.

Stages
------
assets   -> setup_assets
env      -> check_env
scene    -> scene smoke
expert   -> scripted expert episodes
record   -> collect LeRobot demos
validate -> dataset checks
train    -> lerobot-train wrapper (optional dry-run)
eval     -> closed-loop evaluation (needs checkpoint)
benchmark-> sim throughput
all-smoke-> assets + env + scene + expert(1) + record(1) + validate
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from radeonvla.paths import PROJECT_ROOT


def _run(cmd: list[str]) -> int:
    print("[pipeline]", " ".join(cmd), flush=True)
    return subprocess.call(cmd)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage",
        choices=(
            "assets",
            "env",
            "scene",
            "expert",
            "record",
            "validate",
            "train",
            "eval",
            "benchmark",
            "all-smoke",
        ),
    )
    parser.add_argument("--backend", choices=("cpu", "gpu", "amdgpu"), default="cpu")
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--task", default="banana_left")
    parser.add_argument("--repo-id", default="visiobot/radeonvla_reflex_smoke")
    parser.add_argument("--dataset-root", default="datasets/radeonvla_reflex_smoke")
    parser.add_argument("--steps-train", type=int, default=100)
    parser.add_argument("--policy-path", default=None)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--dry-run-train", action="store_true")
    parser.add_argument("--require-amd", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    py = sys.executable
    root = PROJECT_ROOT
    dataset_path = Path(args.dataset_root)
    if not dataset_path.is_absolute():
        dataset_path = (root / dataset_path).resolve()
    dataset_root = str(dataset_path)

    def stage_assets() -> int:
        return _run([py, "-m", "radeonvla.setup_assets"])

    def stage_env() -> int:
        cmd = [py, "-m", "radeonvla.check_env"]
        if args.require_amd:
            cmd += ["--require-amd", "--init-genesis"]
        return _run(cmd)

    def stage_scene() -> int:
        return _run([py, "-m", "radeonvla.scene", "--backend", args.backend, "--steps", "30", "--save-frames"])

    def stage_expert() -> int:
        return _run(
            [
                py,
                "-m",
                "radeonvla.expert",
                "--backend",
                args.backend,
                "--task",
                args.task,
                "--episodes",
                str(args.episodes),
            ]
        )

    def stage_record() -> int:
        return _run(
            [
                py,
                "-m",
                "radeonvla.record_dataset",
                "--backend",
                args.backend,
                "--task",
                args.task,
                "--episodes",
                str(args.episodes),
                "--repo-id",
                args.repo_id,
                "--dataset-root",
                dataset_root,
                "--overwrite",
            ]
        )

    def stage_validate() -> int:
        return _run(
            [
                py,
                "-m",
                "radeonvla.validate_dataset",
                "--repo-id",
                args.repo_id,
                "--dataset-root",
                dataset_root,
            ]
        )

    def stage_train() -> int:
        cmd = [
            py,
            "-m",
            "radeonvla.train_policy",
            "smolvla",
            "--repo-id",
            args.repo_id,
            "--dataset-root",
            dataset_root,
            "--steps",
            str(args.steps_train),
            "--device",
            args.device,
            "--batch-size",
            "1",
            "--num-workers",
            "0",
        ]
        if args.dry_run_train:
            cmd.append("--dry-run")
        return _run(cmd)

    def stage_eval() -> int:
        if not args.policy_path:
            print("[pipeline] --policy-path is required for eval")
            return 2
        cmd = [
            py,
            "-m",
            "radeonvla.evaluate",
            "--policy-path",
            args.policy_path,
            "--repo-id",
            args.repo_id,
            "--dataset-root",
            dataset_root,
            "--backend",
            args.backend,
            "--tasks",
            args.task,
            "--episodes-per-task",
            str(max(1, args.episodes)),
        ]
        if args.backend == "cpu":
            cmd.append("--cpu")
        return _run(cmd)

    def stage_benchmark() -> int:
        return _run([py, "-m", "radeonvla.benchmark", "--backend", args.backend, "--steps", "100"])

    stages = {
        "assets": stage_assets,
        "env": stage_env,
        "scene": stage_scene,
        "expert": stage_expert,
        "record": stage_record,
        "validate": stage_validate,
        "train": stage_train,
        "eval": stage_eval,
        "benchmark": stage_benchmark,
    }

    if args.stage == "all-smoke":
        for name in ("assets", "env", "scene", "expert", "record", "validate"):
            # expert/record use 1 episode by default for smoke
            code = stages[name]()
            if code != 0:
                print(f"[pipeline] stage {name} failed with code {code}")
                return code
        # train dry-run only in smoke (full train is expensive / may need GPU)
        code = _run(
            [
                py,
                "-m",
                "radeonvla.train_policy",
                "smolvla",
                "--repo-id",
                args.repo_id,
                "--dataset-root",
                dataset_root,
                "--steps",
                str(args.steps_train),
                "--device",
                args.device,
                "--dry-run",
            ]
        )
        return code

    # Filter empty tokens for eval cpu flag
    if args.stage == "eval":
        cmd_code = stage_eval()
        return cmd_code

    return stages[args.stage]()


if __name__ == "__main__":
    raise SystemExit(main())
