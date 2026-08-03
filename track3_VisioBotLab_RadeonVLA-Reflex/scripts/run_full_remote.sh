#!/usr/bin/env bash
# Full remote AMD workflow (record -> train -> eval). Override env vars as needed.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES:-0}"
BACKEND="${BACKEND:-amdgpu}"
EPISODES="${EPISODES:-100}"
TRAIN_STEPS="${TRAIN_STEPS:-10000}"
REPO_ID="${REPO_ID:-visiobot/radeonvla_reflex}"
DATASET_ROOT="${DATASET_ROOT:-datasets/radeonvla_reflex}"
DEVICE="${DEVICE:-cuda}"

python -m radeonvla.check_env --require-amd --init-genesis --json docs/environment.remote.json
python -m radeonvla.setup_assets
python -m radeonvla.scene --backend "$BACKEND" --steps 50 --save-frames
python -m radeonvla.expert --backend "$BACKEND" --task banana_left --episodes 3

python -m radeonvla.record_dataset \
  --backend "$BACKEND" \
  --episodes "$EPISODES" \
  --repo-id "$REPO_ID" \
  --dataset-root "$DATASET_ROOT" \
  --overwrite \
  --dr-appearance --dr-object-color --dr-runtime

python -m radeonvla.validate_dataset --repo-id "$REPO_ID" --dataset-root "$DATASET_ROOT"

python -m radeonvla.train_policy smolvla \
  --repo-id "$REPO_ID" \
  --dataset-root "$DATASET_ROOT" \
  --steps "$TRAIN_STEPS" \
  --device "$DEVICE" \
  --batch-size 4

CKPT="${CKPT:-outputs/train/smolvla_$(basename "$DATASET_ROOT")/checkpoints/last/pretrained_model}"
python -m radeonvla.evaluate \
  --policy-path "$CKPT" \
  --repo-id "$REPO_ID" \
  --dataset-root "$DATASET_ROOT" \
  --backend "$BACKEND" \
  --episodes-per-task 5 \
  --save-video

python -m radeonvla.benchmark --backend "$BACKEND" --steps 300 --policy-path "$CKPT" \
  --repo-id "$REPO_ID" --dataset-root "$DATASET_ROOT"
