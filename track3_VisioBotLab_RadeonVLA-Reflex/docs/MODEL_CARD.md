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

> Release status: pre-release. Publication metadata is bound by the validated release workflow.

## Model

- Base model: lerobot/smolvla_base
- Base revision: `c83c3163b8ca9b7e67c509fffd9121e66cb96205`
- Fine-tuned checkpoint: Selected from the validated release run
- Public URL: Published by release workflow
- SHA256: Computed at release
- Training commit: Bound from the dataset manifest at release
- Dataset version: Bound from the validated dataset at release

## Intended use

Language-conditioned Franka fruit sorting in the project Genesis scene.

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
| Radeon GPU | Recorded from release artifacts |
| ROCm | Recorded from release artifacts |
| PyTorch | Recorded from release artifacts |
| Precision | Recorded from training configuration |
| Batch size | Recorded from training configuration |
| Gradient accumulation | Recorded from training configuration |
| Training steps | Recorded from training summary |
| Training time | Recorded from training summary |
| Peak VRAM | Recorded from release artifacts |

## Evaluation

The published card links to immutable `artifacts/evaluation.json` and records
task and episode counts, first-attempt and final success, recovery success, inference
latency, and observed failure modes from the remote AMD evaluation.

The formal evidence bundle also reports safe-interrupt rate, command-to-invalidation
steps, unprotected post-interrupt action steps, and success under deterministic target
shifts. Baseline runs disable chunk invalidation and automatic retry while retaining the
same checkpoint and held-out seeds.

## Limitations

Training and evaluation are limited to Genesis simulation. Coverage includes the
registered language and task suite, dual RGB cameras at 320×240, and 9-D absolute joint
actions. Real-robot transfer is outside the current evaluation scope. The published card
lists failure modes observed in the final evaluation run.

## License note

The upstream `lerobot/smolvla_base` repository did not declare license metadata when the
base revision above was frozen. This model card therefore uses Hugging Face's `other`
marker instead of inventing a permissive license. The Physical-1K training dataset is
CC BY 4.0 and its attribution requirements remain applicable to the dataset and rendered
examples. Users must review the upstream base-model terms before redistribution or
commercial use.
