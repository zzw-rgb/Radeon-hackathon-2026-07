#!/usr/bin/env bash
# Record the three short, judge-facing Reflex demos from an existing checkpoint.
set -euo pipefail
# shellcheck source=lib.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
load_dotenv

export HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES:-0}"
BACKEND="${BACKEND:-amdgpu}"
REPO_ID="${REPO_ID:-visiobot/radeonvla_reflex}"
DATASET_ROOT="${DATASET_ROOT:-datasets/radeonvla_reflex}"
TRAIN_OUTPUT="${TRAIN_OUTPUT:-outputs/train/smolvla_$(basename "$DATASET_ROOT")}"
CKPT="${CKPT:-}"

if [[ -z "$CKPT" ]]; then
  CKPT="$(latest_pretrained_model "$TRAIN_OUTPUT")" \
    || die "No pretrained model found below $TRAIN_OUTPUT/checkpoints"
fi

[[ -d "$CKPT" ]] || die "Checkpoint missing: $CKPT"
[[ -d "$DATASET_ROOT" ]] || die "Dataset missing: $DATASET_ROOT"
CKPT_SHA256="$("${PYTHON[@]}" -m radeonvla.artifact_io "$CKPT" | tail -n 1)"

section "Normal closed-loop demo"
run_py -m radeonvla.evaluate --policy-path "$CKPT" --repo-id "$REPO_ID" \
  --dataset-root "$DATASET_ROOT" --backend "$BACKEND" --tasks banana_white_left \
  --episodes-per-task 1 --checkpoint-sha256 "$CKPT_SHA256" --save-video \
  --output artifacts/demo_normal.json

section "Mid-command interrupt demo"
run_py -m radeonvla.evaluate --policy-path "$CKPT" --repo-id "$REPO_ID" \
  --dataset-root "$DATASET_ROOT" --backend "$BACKEND" --tasks banana_white_left \
  --episodes-per-task 1 --interrupt-demo --checkpoint-sha256 "$CKPT_SHA256" --save-video \
  --output artifacts/demo_interrupt.json

section "Target-shift recovery demo"
run_py -m radeonvla.evaluate --policy-path "$CKPT" --repo-id "$REPO_ID" \
  --dataset-root "$DATASET_ROOT" --backend "$BACKEND" --tasks lemon_blue_right \
  --episodes-per-task 1 --perturbation target_shift --perturb-at-step 30 \
  --checkpoint-sha256 "$CKPT_SHA256" --save-video --output artifacts/demo_recovery.json

ok "Reflex demos complete; videos are under outputs/eval_videos and metrics under artifacts/"
