#!/usr/bin/env bash
# Full AMD Radeon workflow: check -> record (suite) -> train -> evaluate -> benchmark
#
# Usage:
#   bash scripts/run_full_remote.sh
#   EPISODES=50 TRAIN_STEPS=5000 SUITE=full bash scripts/run_full_remote.sh
#   SKIP_TRAIN=1 CKPT=path/to/pretrained_model bash scripts/run_full_remote.sh
set -euo pipefail
# shellcheck source=lib.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
load_dotenv

export HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES:-0}"
BACKEND="${BACKEND:-amdgpu}"
EPISODES="${EPISODES:-100}"
TRAIN_STEPS="${TRAIN_STEPS:-10000}"
SUITE="${SUITE:-full}"
REPO_ID="${REPO_ID:-visiobot/radeonvla_reflex}"
DATASET_ROOT="${DATASET_ROOT:-datasets/radeonvla_reflex}"
DEVICE="${DEVICE:-cuda}"
BATCH_SIZE="${BATCH_SIZE:-4}"
EVAL_PER_TASK="${EVAL_PER_TASK:-5}"
SKIP_TRAIN="${SKIP_TRAIN:-0}"
DR="${DR:-1}"

START=$(date +%s)
section "Full remote pipeline"
log "HIP_VISIBLE_DEVICES=$HIP_VISIBLE_DEVICES BACKEND=$BACKEND SUITE=$SUITE EPISODES=$EPISODES"

section "1 env (strict AMD)"
run_py -m radeonvla.check_env --require-amd --init-genesis --json docs/environment.remote.json

section "2 assets + scene + expert smoke"
run_py -m radeonvla.setup_assets
run_py -m radeonvla.scene --backend "$BACKEND" --steps 50 --save-frames
run_py -m radeonvla.expert --backend "$BACKEND" --task banana_white_left --episodes 2
run_py -m radeonvla.expert --backend "$BACKEND" --task seq_banana_white_left_lemon_white_right --episodes 1

section "3 record ($EPISODES successes, suite=$SUITE)"
RECORD_ARGS=(
  -m radeonvla.record_dataset
  --backend "$BACKEND"
  --episodes "$EPISODES"
  --suite "$SUITE"
  --repo-id "$REPO_ID"
  --dataset-root "$DATASET_ROOT"
  --overwrite
)
if [[ "$DR" == "1" ]]; then
  RECORD_ARGS+=(--dr-appearance --dr-object-color --dr-runtime)
fi
run_py "${RECORD_ARGS[@]}"
run_py -m radeonvla.validate_dataset --repo-id "$REPO_ID" --dataset-root "$DATASET_ROOT"

CKPT="${CKPT:-outputs/train/smolvla_$(basename "$DATASET_ROOT")/checkpoints/last/pretrained_model}"
if [[ "$SKIP_TRAIN" != "1" ]]; then
  section "4 train SmolVLA ($TRAIN_STEPS steps)"
  run_py -m radeonvla.train_policy smolvla \
    --repo-id "$REPO_ID" \
    --dataset-root "$DATASET_ROOT" \
    --steps "$TRAIN_STEPS" \
    --device "$DEVICE" \
    --batch-size "$BATCH_SIZE"
else
  section "4 train skipped (SKIP_TRAIN=1)"
  [[ -d "$CKPT" ]] || die "CKPT not found: $CKPT"
fi

section "5 evaluate"
[[ -d "$CKPT" ]] || die "Checkpoint missing: $CKPT (set CKPT=... or disable SKIP_TRAIN)"
run_py -m radeonvla.evaluate \
  --policy-path "$CKPT" \
  --repo-id "$REPO_ID" \
  --dataset-root "$DATASET_ROOT" \
  --backend "$BACKEND" \
  --suite "$SUITE" \
  --episodes-per-task "$EVAL_PER_TASK" \
  --save-video

section "6 interrupt demo + benchmark"
run_py -m radeonvla.evaluate \
  --policy-path "$CKPT" \
  --repo-id "$REPO_ID" \
  --dataset-root "$DATASET_ROOT" \
  --backend "$BACKEND" \
  --tasks banana_white_left \
  --episodes-per-task 1 \
  --interrupt-demo \
  --save-video || log "WARN: interrupt demo returned non-zero"

run_py -m radeonvla.benchmark --backend "$BACKEND" --steps 300 \
  --policy-path "$CKPT" --repo-id "$REPO_ID" --dataset-root "$DATASET_ROOT"

ok "Full remote pipeline finished in $(elapsed "$START")s"
log "Checkpoint: $CKPT"
log "Eval outputs under: $ROOT/outputs/eval_results"
