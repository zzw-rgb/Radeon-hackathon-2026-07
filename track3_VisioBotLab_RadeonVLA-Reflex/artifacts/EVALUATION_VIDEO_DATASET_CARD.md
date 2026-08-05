---
pretty_name: RadeonVLA-Reflex Evaluation Videos
license: apache-2.0
task_categories:
- robotics
tags:
- robotics
- physical-ai
- vision-language-action
- rocm
- amd-radeon
---

# RadeonVLA-Reflex evaluation videos

This repository is the public video-and-evidence companion for **RadeonVLA-Reflex**, a Track 3 Physical AI submission by VisioBot Lab. It keeps videos beside the machine-readable results and hashes used to describe them.

## Linked releases

- Dataset: [`a3124371940/radeonvla_reflex_physical_2k`](https://huggingface.co/datasets/a3124371940/radeonvla_reflex_physical_2k), revision `2779b7c5566df9072bb9a7c43335d6203ea97887`
- Model: [`a3124371940/radeonvla_reflex_smolvla_2k_200k`](https://huggingface.co/a3124371940/radeonvla_reflex_smolvla_2k_200k), revision `1ea32da3d59ce0905d0f1331bc3c6643e42beb7e`
- Checkpoint tree SHA256: `ad0ec7c1271b73b0ba684180b71a80ae1a9dad22c64a38796ba28f6597991683`

## What is included

| Path | Scope |
|---|---|
| `videos/learned_success/` | Representative 200K learned-policy first-attempt successes for apple, lemon, orange, and plum |
| `videos/reflex/interrupt_recovery_apple_seed61000.mp4` | Apple command-change probe: safe interruption, learned empty grasp, then explicitly labeled strict-physics recovery |
| `videos/reflex/normal_vs_reflex_15s.mp4` | Paired learned-miss and Precision-Reflex comparison |
| `videos/walkthrough/radeonvla_reflex_3min.mp4` | 200-second English project walkthrough with bilingual burned captions |
| `evidence/formal100/` | Formal 100-rollout JSON and CSV evidence |
| `evidence/interrupt_recovery/` | Apple command-change-and-recovery JSON, CSV, and Markdown summary |
| `SHA256SUMS` | Content hashes for every uploaded payload file |

## Formal result boundary

The released 100-rollout benchmark contains 20 tasks × 5 disjoint seeds:

- Learned-policy first-attempt success: **36/100**
- Explicit strict-physics Precision-Reflex contribution: **+55/100**
- Final system success: **91/100**
- P50 / P95 policy inference latency: **4.54 / 37.27 ms**

The representative clips are a replay library, not the benchmark denominator. Aggregate claims are tied to `evidence/formal100/evaluation.json` and its CSV companion.

## Honesty and physics boundary

Precision recovery is invoked only after learned control has failed and is reported separately. Evaluation forbids object pose teleportation, grasp glue, and post-hoc placement correction. The apple interrupt-recovery clip deliberately retains the learned empty grasp before the strict-physics fallback completes the new destination.

## Language

Commands use the exact collected-language instruction source from Physical-2K. The long walkthrough uses English narration and bilingual English/Chinese captions.
