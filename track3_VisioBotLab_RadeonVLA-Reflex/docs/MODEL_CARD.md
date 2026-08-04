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

> Release status: trained checkpoint. The Physical-1K data and checkpoint are published;
> formal closed-loop evaluation of this checkpoint is still in progress and no final success
> rate is claimed in this revision.

## Model

- Base model: lerobot/smolvla_base
- Base revision: `c83c3163b8ca9b7e67c509fffd9121e66cb96205`
- Fine-tuned checkpoint: `020000/pretrained_model`
- Public URL: https://huggingface.co/a3124371940/radeonvla_reflex_smolvla_1k
- Local checkpoint tree SHA256: `47911b0faf672905107dd7daf18b5a99eaf199a01dcc579f62253fc4a3016308`
- Training pipeline commit: `be62f684c7e916e8600cf37b8644883f8b75a7dd`
- Dataset: https://huggingface.co/datasets/a3124371940/radeonvla_reflex_physical_1k
- Dataset revision: `b0f72c60e9100739fd82bd498c8f3d9bed7b75af`

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
| Radeon GPU | AMD Radeon Graphics, `gfx1100`, 51.5 GB VRAM |
| ROCm | 7.2.1 / HIP runtime 7.2.53211 |
| PyTorch | 2.9.1+rocm7.2.1 |
| Precision | FP32 (`use_amp=false`) |
| Batch size | 4 |
| Gradient accumulation | Not configured; one optimizer update per batch |
| Training steps | 20,000 (80,000 sampled frames) |
| Training time | 45m 34s |
| Peak training memory reported by LeRobot | 2.22 GB |
| Final logged minibatch loss | 0.091 |

## Evaluation

The final 20-task held-out evaluation has not yet been completed for this Physical-1K
checkpoint. This release therefore does not claim a closed-loop success rate. The
checkpoint has passed a forced-offline `SmolVLAPolicy.from_pretrained` load test after
vendoring its VLM tokenizer and processor assets. A later revision will bind the formal
evaluation JSON, Normal-vs-Reflex comparison, inference latency, and observed failure
modes without replacing the immutable training metadata above.

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
