# RadeonVLA-Reflex Model Card

> Status: template. Replace every TBD after selecting the final checkpoint.

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

Link the model to the immutable raw evaluation revision and report:

- tasks and episode counts;
- first-attempt success;
- final success;
- recovery success;
- inference latency;
- known failure modes.

## Limitations

Do not claim real-robot transfer. Describe simulation-only scope, language coverage,
object coverage, camera assumptions, action-space limitations, and observed failures.
