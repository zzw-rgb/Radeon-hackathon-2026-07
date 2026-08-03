# RadeonVLA-Reflex

## Technical Report — Track 3 Physical AI Challenge

**Team:** VisioBot Lab
**Team Member:** Zhenwei Zhou
**Affiliation:** Nanjing University of Science and Technology
**Date:** TBD
**Submitted Commit:** TBD

## 1. Executive Summary

RadeonVLA-Reflex is a language-guided Franka dual-bowl fruit-sorting system built for
Track 3 of the AMD AI DevMaster Hackathon. The policy stack is SmolVLA fine-tuned with
LeRobot on demonstrations collected in Genesis; the control stack adds interruptible
command execution and failure-aware recovery around the learned action chunks. Six
tasks (banana/lemon/plum × left/right bowl) form the formal task registry.

> Quantitative success rates, GPU model, ROCm build, and wall-clock numbers will be
> filled after remote AMD runs. Until then, this section must not claim measured
> performance.

## 2. Target Application

The application is flexible robotic sorting for food handling, laboratory automation,
and small-batch logistics. An operator issues a natural-language command that names a
fruit and a destination container. The robot must observe RGB images and proprioception,
execute continuous joint-space actions, accept mid-task command changes safely, and
recover from empty grasps or timeouts with at most one retry. Practical value comes from
combining VLA generalization with deterministic execution safety.

## 3. Task Definition and Success Criteria

- Fruits: banana, lemon, plum. Containers: left_bowl, right_bowl (six tasks).
- Training and evaluation use disjoint natural-language templates (see `tasks.py`).
- Episode reset randomizes object xy within non-overlap slot jitter and small yaw noise.
- Action: 9-D absolute joint positions (7 arm + 2 fingers) at 20 Hz.
- Success: target fruit bottom is inside the commanded bowl rim footprint and below rim.
- Max episode length: 600 policy steps; max recovery retries: 1.

## 4. System Architecture

```text
Language command ──┐
World RGB ─────────┤
Wrist RGB ─────────┤──► SmolVLA ──► action ──► SafetyMonitor ──► Genesis
Proprioception ────┘                              │
                                      CommandSession (version)
                                      FailureDetector + RecoveryPolicy
```

1. Inputs: natural-language instruction, world/wrist RGB, 9-D qpos.
2. SmolVLA (LeRobot) produces absolute joint-position actions / chunks.
3. SafetyMonitor clamps joints, rate-limits large jumps, and on command-version change
   opens the gripper and invalidates the stale chunk (policy reset).
4. FailureDetector flags empty grasp / timeout; RecoveryPolicy allows one home retreat
   and retry.
5. Genesis steps the Franka dual-bowl scene and returns the next observation.

The learned controller is **end-to-end** joint-position VLA. Interrupt invalidation and
recovery are **deterministic outer layers**, not a second learned high-level planner.

## 5. Genesis Simulation Environment

Document:

- Genesis version and backend;
- Franka model and asset source;
- fruit and container assets;
- camera configuration;
- physics and control frequency;
- headless rendering;
- deterministic reset limitations.

## 6. Demonstration Dataset

Use docs/DATASET_CARD.md as the source of truth. Include:

- generation method;
- task and episode distribution;
- frame schema;
- action and state ordering;
- seed splits;
- filtering and audit;
- license and redistribution constraints.

## 7. Model and Training

Describe SmolVLA base model, feature mapping, normalization, action chunks, optimizer,
precision, batch, steps, checkpoint selection, and training time.

| Item | Value |
|---|---|
| GPU | TBD |
| ROCm | TBD |
| PyTorch | TBD |
| Precision | TBD |
| Batch size | TBD |
| Effective batch size | TBD |
| Steps | TBD |
| Training time | TBD |
| Throughput | TBD |
| Peak VRAM | TBD |

## 8. Interruptible Command Execution

Describe the fixed command-change injection point, command versioning, old chunk
invalidation, safety transition, replanning behavior, and evaluation protocol.

If only safe cancellation is verified, state that limitation and do not claim successful
online correction.

## 9. Failure Detection and Recovery

Describe the event definition, evidence window, false-trigger control, recovery
sequence, retry limit, and evaluation.

Report first-attempt and final success separately.

## 10. AMD Radeon GPU and ROCm Integration

Include:

- Radeon model and architecture;
- ROCm and driver;
- matching PyTorch HIP build;
- single-GPU restriction;
- Genesis AMD backend evidence;
- simulation, data generation, training, inference, and evaluation use;
- latency, throughput, temperature/power if available, and peak VRAM methodology.

## 11. Experimental Protocol

State:

- immutable submitted commit;
- dataset and checkpoint checksum;
- held-out tasks and instructions;
- exact seed ranges;
- episode count by task;
- success and failure definitions;
- latency measurement warm-up and synchronization;
- retained failure episodes.

## 12. Quantitative Results

| Method | Tasks | Episodes | First-attempt success | Final success | P95 latency | Peak VRAM |
|---|---:|---:|---:|---:|---:|---:|
| Scripted expert | TBD | TBD | TBD | TBD | N/A | TBD |
| SmolVLA | TBD | TBD | TBD | TBD | TBD | TBD |
| SmolVLA + recovery | TBD | TBD | TBD | TBD | TBD | TBD |

Remove baselines that were not actually run.

Provide per-task results and link to immutable raw JSON/CSV.

## 13. Failure Analysis

Show representative failures with episode IDs. Discuss wrong object, wrong target,
empty grasp, slip, timeout, unstable placement, action invalidity, and distribution
shift only when observed.

## 14. Innovation and Technical Contributions

Explain verified contributions, separating learned-policy capability from deterministic
safety and recovery logic.

## 15. Deliverables

| Deliverable | Public URL | SHA256 or revision |
|---|---|---|
| Source repository | TBD | TBD |
| Model | TBD | TBD |
| Dataset/documentation | TBD | TBD |
| Raw evaluation | TBD | TBD |
| Demo video | TBD | TBD |
| Technical report | This PDF | TBD |

## 16. Reproducibility

Summarize the exact README path, environment creation, model and asset download,
strict AMD validation, smoke test, single rollout, and quick evaluation.

Report the clean-environment audit duration and every known platform assumption.

## 17. Team Member and Contribution

**Zhenwei Zhou:** system design, implementation, data generation, model training,
evaluation, documentation, and submission.

## 18. Limitations and Future Work

State simulation-only scope, task coverage, language coverage, real-robot transfer
limits, model failures, recovery limits, and unimplemented planned features.

## 19. References

Include Genesis, LeRobot, SmolVLA, ROCm, YCB, the official Track 3 repository, and any
other source actually used.
