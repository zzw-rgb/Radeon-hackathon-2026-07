---
license: other
library_name: lerobot
base_model: lerobot/smolvla_base
tags:
  - robotics
  - vision-language-action
  - imitation-learning
  - amd-rocm
  - genesis
---

# RadeonVLA-Reflex SmolVLA-1K Model Card

> Status: draft. Fill measured fields after the final checkpoint is selected.

## Model

- Base model: lerobot/smolvla_base
- Base revision: `c83c3163b8ca9b7e67c509fffd9121e66cb96205`
- Fine-tuned checkpoint: TBD
- Public URL: TBD
- SHA256: TBD
- Training commit: TBD
- Dataset version: TBD

## Intended use

Language-conditioned Franka fruit sorting in the submitted Genesis scene.

## Inputs and outputs

- Image inputs: observation.images.world + observation.images.wrist (320×240 RGB); renamed to camera1/camera2 for SmolVLA
- State shape and ordering: 9-D qpos — panda_joint1..7, panda_finger_joint1..2
- Language input: natural-language task instruction
- Action type, shape, and ordering: 9-D absolute joint positions (same order as state)
- Control frequency: 20 Hz
- Action chunk size: determined by SmolVLA checkpoint config

## Training

| Item | Value |
|---|---|
| Radeon GPU | TBD |
| ROCm | TBD |
| PyTorch | TBD |
| Precision | TBD |
| Batch size | TBD |
| Gradient accumulation | TBD |
| Training steps | TBD |
| Training time | TBD |
| Peak VRAM | TBD |

## Evaluation

I will link this card to the immutable `artifacts/evaluation.json` and
record task/episode counts, first-attempt vs final success, recovery success, inference
latency, and known failure modes after the remote AMD evaluation.

The formal evidence bundle also reports safe-interrupt rate, command-to-invalidation
steps, unprotected post-interrupt action steps, and success under deterministic target
shifts. Baseline runs disable chunk invalidation and automatic retry while retaining the
same checkpoint and held-out seeds.

## Limitations

This model is trained and evaluated in Genesis simulation only; I do not claim real-robot
transfer. Coverage is limited to the registered language/task suite, dual RGB cameras at
320×240, and 9-D absolute joint actions. Observed failure modes will be listed after the
final evaluation run.

## License note

The upstream `lerobot/smolvla_base` repository did not declare license metadata when the
base revision above was frozen. This model card therefore uses Hugging Face's `other`
marker instead of inventing a permissive license. The Physical-1K training dataset is
CC BY 4.0 and its attribution requirements remain applicable to the dataset and rendered
examples. Users must review the upstream base-model terms before redistribution or
commercial use.
