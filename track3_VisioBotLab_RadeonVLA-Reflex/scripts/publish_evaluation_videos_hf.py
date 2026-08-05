#!/usr/bin/env python3
"""Publish the checked RadeonVLA-Reflex evaluation-video evidence bundle."""

from __future__ import annotations

import hashlib
import io
from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ID = "a3124371940/radeonvla_reflex_evaluation_videos"

FILES = {
    "README.md": PROJECT_ROOT / "artifacts" / "EVALUATION_VIDEO_DATASET_CARD.md",
    "videos/learned_success/apple_blue_left_seed50020.mp4": PROJECT_ROOT
    / "website/public/videos/eval-apple-blue-left.mp4",
    "videos/learned_success/lemon_blue_right_seed50022.mp4": PROJECT_ROOT
    / "website/public/videos/eval-lemon-blue-right.mp4",
    "videos/learned_success/orange_white_right_seed50023.mp4": PROJECT_ROOT
    / "website/public/videos/eval-orange-white-right.mp4",
    "videos/learned_success/plum_white_left_seed50024.mp4": PROJECT_ROOT
    / "website/public/videos/eval-plum-white-left.mp4",
    "videos/reflex/interrupt_recovery_apple_seed61000.mp4": PROJECT_ROOT
    / "website/public/videos/interrupt-recovery-apple.mp4",
    "videos/reflex/normal_vs_reflex_15s.mp4": PROJECT_ROOT
    / "website/public/videos/normal-vs-reflex-15s.mp4",
    "videos/walkthrough/radeonvla_reflex_3min.mp4": PROJECT_ROOT
    / "website/public/videos/radeonvla-reflex-3min.mp4",
    "videos/walkthrough/radeonvla_reflex_3min.vtt": PROJECT_ROOT
    / "website/public/videos/radeonvla-reflex-3min.vtt",
    "evidence/formal100/evaluation.json": PROJECT_ROOT / "artifacts/evaluation.json",
    "evidence/formal100/evaluation.csv": PROJECT_ROOT / "artifacts/evaluation.csv",
    "evidence/formal100/evaluation.schema.json": PROJECT_ROOT / "artifacts/evaluation.schema.json",
    "evidence/interrupt_recovery/evaluation.json": PROJECT_ROOT
    / "artifacts/interrupt_recovery_evaluation_apple.json",
    "evidence/interrupt_recovery/evaluation.csv": PROJECT_ROOT
    / "artifacts/interrupt_recovery_evaluation_apple.csv",
    "evidence/interrupt_recovery/evaluation.summary.md": PROJECT_ROOT
    / "artifacts/interrupt_recovery_evaluation_apple.summary.md",
}


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> None:
    missing = [str(path) for path in FILES.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing release inputs:\n" + "\n".join(missing))

    sums = "".join(f"{digest(path)}  {repo_path}\n" for repo_path, path in sorted(FILES.items()))
    operations = [
        CommitOperationAdd(path_in_repo=repo_path, path_or_fileobj=path)
        for repo_path, path in FILES.items()
    ]
    operations.append(
        CommitOperationAdd(path_in_repo="SHA256SUMS", path_or_fileobj=io.BytesIO(sums.encode("utf-8")))
    )

    api = HfApi()
    api.create_repo(REPO_ID, repo_type="dataset", private=False, exist_ok=True)
    commit = api.create_commit(
        repo_id=REPO_ID,
        repo_type="dataset",
        operations=operations,
        commit_message="Publish evaluation videos, formal evidence, and checksums",
    )
    info = api.repo_info(REPO_ID, repo_type="dataset")
    print(f"repo=https://huggingface.co/datasets/{REPO_ID}")
    print(f"commit={commit.oid}")
    print(f"revision={info.sha}")
    print(f"files={len(api.list_repo_files(REPO_ID, repo_type='dataset', revision=info.sha))}")


if __name__ == "__main__":
    main()
