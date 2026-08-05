# Track 3, VisioBot Lab, RadeonVLA-Reflex

RadeonVLA-Reflex is an interruptible and recoverable execution layer around SmolVLA for
language-guided Franka fruit sorting. It runs the full simulation, data collection, training,
and evaluation path on one AMD Radeon GPU with ROCm.

## 60-second evaluator path

1. Open the [live bilingual showcase](https://zzw-rgb.github.io/Radeon-hackathon-2026-07/).
2. Play the [200-second English narrated demo](https://zzw-rgb.github.io/Radeon-hackathon-2026-07/videos/radeonvla-reflex-3min.mp4).
3. Review the [five-page technical report](https://github.com/zzw-rgb/Radeon-hackathon-2026-07/blob/submission/track3-visiobotlab-radeonvla-reflex/track3_VisioBotLab_RadeonVLA-Reflex/reports/RadeonVLA-Reflex-Technical-Report.pdf).
4. Inspect the public [Physical-2K dataset](https://huggingface.co/datasets/a3124371940/radeonvla_reflex_physical_2k)
   and [200K checkpoint](https://huggingface.co/a3124371940/radeonvla_reflex_smolvla_2k_200k).
5. Reproduce the repository checks and evaluation using the [English README](https://github.com/zzw-rgb/Radeon-hackathon-2026-07/blob/submission/track3-visiobotlab-radeonvla-reflex/track3_VisioBotLab_RadeonVLA-Reflex/README.md).

## Final measured results

The primary benchmark freezes one 200K checkpoint, the exact collected language, all 20 basic
fruit × destination tasks, five disjoint seeds per task, and no learned-policy retries.

| Metric | Result |
|---|---:|
| Learned SmolVLA first attempt | 36/100 |
| Strict-physics precision recoveries | 55/63 |
| Final system success | 91/100 |
| Wilson 95% interval | 83.8–95.2% |
| Inference latency P50 / P95 | 4.54 / 37.27 ms |
| Retained failures | 9/100 |

All 100 episodes are retained in [`artifacts/evaluation.json`](https://github.com/zzw-rgb/Radeon-hackathon-2026-07/blob/submission/track3-visiobotlab-radeonvla-reflex/track3_VisioBotLab_RadeonVLA-Reflex/artifacts/evaluation.json).
Precision recovery remains opt-in and is reported separately; it executes with rigid pose writes,
object teleport, kinematic grasp glue, and placement nudges disabled.

An independent seed-60000 command-change probe switches `banana→white-left` to
`banana→blue-right` at control step 40. It records safe interrupt 1/1, zero additional response
steps, zero unprotected old-command actions, and final new-target success 1/1 in
[`artifacts/interrupt_evaluation.json`](https://github.com/zzw-rgb/Radeon-hackathon-2026-07/blob/submission/track3-visiobotlab-radeonvla-reflex/track3_VisioBotLab_RadeonVLA-Reflex/artifacts/interrupt_evaluation.json).

## AMD Radeon / ROCm path

- AMD Radeon Graphics (`gfx1100`), one visible GPU;
- ROCm runtime `7.2.53211-e1a6bc5663`;
- PyTorch `2.9.1+rocm7.2.1.gitff65f5bc`;
- Genesis 1.1.2 and LeRobot 0.6.0;
- Physical-2K continuation: 100,000 steps in 3h45m32s, 30 samples/s;
- measured peak training memory: 2.22 GB.

## Immutable public artifacts

| Artifact | Revision / digest |
|---|---|
| Physical-2K dataset | `2779b7c5566df9072bb9a7c43335d6203ea97887` |
| Cumulative-200K model | `1ea32da3d59ce0905d0f1331bc3c6643e42beb7e` |
| Policy tree SHA256 | `ad0ec7c1271b73b0ba684180b71a80ae1a9dad22c64a38796ba28f6597991683` |
| Formal evaluation implementation | `c5c37576d4b80f056205ef7920a5f1ebfa614f86` |

The dataset contains 2,000 strict-physics successes, 468,889 frames, exact 20×100 task
coverage, 2,000 certificates, and zero validator errors or warnings. Final checksums for the
compact release bundle are in [`artifacts/SHA256SUMS`](https://github.com/zzw-rgb/Radeon-hackathon-2026-07/blob/submission/track3-visiobotlab-radeonvla-reflex/track3_VisioBotLab_RadeonVLA-Reflex/artifacts/SHA256SUMS).

## Claims boundary

This submission evaluates Genesis simulation only and makes no real-robot or sim-to-real claim.
The learned first attempt and deterministic recovery are intentionally not collapsed into one
opaque learned-policy score. Advanced L2–L4 task definitions are implemented, while the reported
91/100 primary result covers the registered L1 20-task suite.
