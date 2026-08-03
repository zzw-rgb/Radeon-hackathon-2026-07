# RadeonVLA-Reflex Model Card

> Status: draft. Fill measured fields after the final checkpoint is selected.

## Model

- Base model: lerobot/smolvla_base
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

I will link this card to the immutable evaluation JSON under `outputs/eval_results/` and
record task/episode counts, first-attempt vs final success, recovery success, inference
latency, and known failure modes after the remote AMD evaluation.

## Limitations

This model is trained and evaluated in Genesis simulation only; I do not claim real-robot
transfer. Coverage is limited to the registered language/task suite, dual RGB cameras at
320×240, and 9-D absolute joint actions. Observed failure modes will be listed after the
final evaluation run.
