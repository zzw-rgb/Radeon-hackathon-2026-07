# RadeonVLA-Reflex

## Technical Report — Track 3 Physical AI Challenge

**Team:** VisioBot Lab
**Team Member:** Zhenwei Zhou
**Affiliation:** Nanjing University of Science and Technology
**Date:** TBD
**Submitted Commit:** TBD

## 1. Executive Summary

RadeonVLA-Reflex is my language-guided Franka dual-bowl fruit-sorting system for
Track 3 of the AMD AI DevMaster Hackathon (VisioBot Lab). I fine-tune SmolVLA with
LeRobot on demonstrations collected in Genesis, and wrap closed-loop execution with
interruptible command handling and failure-aware recovery. The formal task suite
covers a primary L1 benchmark of five fruits × four language-addressable bowl positions,
plus L2–L4 extensions for spatial grounding, multi-step sequences, and attribute rules.

> I will fill quantitative success rates, GPU model, ROCm build, and wall-clock
> numbers after remote AMD runs. Until those runs finish, this section does not
> report measured performance.

## 2. Target Application

The application is flexible robotic sorting for food handling, laboratory automation,
and small-batch logistics. An operator issues a natural-language command that names a
fruit and a destination container. The robot must observe RGB images and proprioception,
execute continuous joint-space actions, accept mid-task command changes safely, and
recover from empty grasps or timeouts with at most one retry. Practical value comes from
combining VLA generalization with deterministic execution safety.

## 3. Task Definition and Success Criteria

- Fruits: banana, lemon, plum, apple, orange. Containers: white/blue bowls on the left/right.
- **Tiered suite (L1–L4)** used in this project:
  - **L1 Basic** — named fruit × color/side bowl (20 tasks).
  - **L2 Spatial** — leftmost / rightmost / nearest-to-robot / farthest (resolved after randomization).
  - **L3 Multi-step** — ordered multi-object sequences in one episode (2–3 subgoals).
  - **L4 Rules** — attribute sorting (yellow→left, purple→right; curved→left, round→right).
- Training and evaluation use disjoint natural-language templates (see `tasks.py`).
- Spatial/rule goals are grounded by `grounding.resolve_task` after each reset.
- Episode reset randomizes object xy within non-overlap slot jitter and small yaw noise.
- Action: 9-D absolute joint positions (7 arm + 2 fingers) at 20 Hz.
- Success: **all** subgoals satisfied (object bottom inside commanded bowl rim); partial rate is reported.
- Max episode length: 600–1800 policy steps by tier; max recovery retries: 1.

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

I use Genesis 1.1.2 with a Franka Emika Panda MJCF, five YCB fruits (banana / lemon /
plum / apple / orange), and four fixed upright bowl instances (white/blue on each side). World and wrist RGB cameras feed
the policy at 320×240; an optional third camera is for evaluation video only. Simulation
runs at 100 Hz control with dataset capture at 20 Hz. Pose resets use non-overlapping
slot jitter. Full asset notes live in `docs/DATASET_CARD.md` and `assets/README.md`.

Remote AMD runs use the Genesis AMD backend after `radeonvla.check_env --require-amd`.
Local development may use CPU Genesis for imports and unit tests only.

## 6. Demonstration Dataset

I generate demonstrations with the scripted multi-goal expert (`record_dataset`) into a
LeRobot 0.6 dataset. Frames store world/wrist RGB, 9-D state/action, and a natural-language
task string. Training and evaluation instructions are disjoint per task. Seed ranges:

Collection uses two-phase publication. Episodes are written to a hidden `.inprogress`
directory with an atomic progress manifest. Only a finalized dataset that reaches the
requested success count, passes the task-coverage gate, and can be reopened by LeRobot
replaces the previous published dataset.

| Split | Seeds |
|---|---|
| Training | 0–9999 |
| Validation | 10000–10999 |
| Formal evaluation | 20000–29999 |
| Interrupt / recovery probes | 30000–30999 |

Detailed schema and episode counts are maintained in `docs/DATASET_CARD.md` and will be
updated when the final dataset revision is frozen.

## 7. Model and Training

I fine-tune `lerobot/smolvla_base` through the project train wrapper
(`python -m radeonvla.train_policy smolvla`). Dataset camera keys `world` / `wrist` map to
SmolVLA’s `camera1` / `camera2` via `rename_map`. Video decoding defaults to `pyav`.

| Item | Value |
|---|---|
| GPU | pending remote log |
| ROCm | pending remote log |
| PyTorch | pending remote log |
| Precision | bfloat16 (planned) |
| Batch size | 4 (default config) |
| Steps | 10000 (default config) |
| Training time | pending |
| Throughput | pending |
| Peak VRAM | pending |

## 8. Interruptible Command Execution

I implement command versioning in `CommandSession`. When the language instruction changes
mid-episode, the version increments; `SafetyMonitor` opens the gripper, holds the arm, and
invalidates the stale action chunk so the policy is reset. Evaluation can inject a mid-rollout
command change with `--interrupt-demo`. I will report whether online correction succeeds or
only safe cancellation is reliable after remote measurements.

The evaluator records safe-interrupt rate, command-to-invalidation steps, and the number
of unprotected post-interrupt action steps. Demo videos overlay command version, runtime
state, retry count, scenario, and live inference latency.

## 9. Failure Detection and Recovery

`FailureDetector` watches empty-grasp heuristics (closed gripper while the target fruit
stays near the table), timeouts, and invalid actions. `RecoveryPolicy` allows one retreat
to a home-like open-gripper pose and a retry. I report first-attempt success and final
success separately in evaluation JSON.

## 10. AMD Radeon GPU and ROCm Integration

I target a single visible Radeon GPU (`HIP_VISIBLE_DEVICES=0`) with a matching ROCm PyTorch
HIP build. The project never pins a generic CPU torch wheel in `pyproject.toml`. Remote setup
and validation steps are in `docs/REMOTE_ROCM_SETUP.md` and `scripts/check_remote_amd.sh`.
I will attach measured latency, throughput, and peak VRAM from the final Radeon instance.

## 11. Experimental Protocol

- Fixed git commit for the submitted revision;
- dataset and checkpoint checksums recorded in artifacts;
- held-out evaluation language (not training phrasings);
- seed ranges as in Section 6;
- suite `basic` by default for the primary 20-task benchmark; advanced tiers are explicit;
- primary award benchmark: 20 L1 tasks × 10 held-out episodes;
- deterministic target/container shifts for robustness stress tests;
- baseline-vs-Reflex ablation by disabling invalidation and retry;
- success = all resolved subgoals placed correctly;
- keep failure episodes in raw JSON;
- latency measured after short warm-up with device synchronization when CUDA/HIP is available.

## 12. Quantitative Results

| Method | Tasks | Episodes | First-attempt success | Final success | P95 latency | Peak VRAM |
|---|---:|---:|---:|---:|---:|---:|
| Scripted expert | pending | pending | pending | pending | N/A | pending |
| SmolVLA baseline | pending | pending | pending | pending | pending | pending |
| SmolVLA + Reflex | pending | pending | pending | pending | pending | pending |

I will publish per-task and per-tier tables from immutable `artifacts/evaluation.json`
after remote evaluation.

## 13. Failure Analysis

After evaluation, I will attach representative episode IDs for observed modes only (wrong
object, wrong target, empty grasp, slip, timeout, partial multi-goal, interrupt failure).
I will not invent failure modes that were not logged.

## 14. Innovation and Technical Contributions

Contributions I implemented in this submission:

1. Dual-bowl language sorting with L1–L4 task tiers and runtime grounding;
2. Interruptible command sessions with stale-chunk invalidation;
3. Failure detection and one-shot recovery around a SmolVLA joint-position policy;
4. Deterministic target/container perturbations and baseline-vs-Reflex robustness evaluation;
5. Crash-safe dataset publication with continuous progress manifests and coverage gates;
6. A full ROCm-oriented pipeline: assets → record → validate → train → evaluate → benchmark;
7. Reviewable JSON/CSV/Markdown evidence with real checkpoint hashing and video telemetry.

Learned control (SmolVLA) is separate from deterministic safety/recovery logic.

## 15. Deliverables

| Deliverable | Public URL | SHA256 or revision |
|---|---|---|
| Source repository | pending push URL | pending commit |
| Model | pending | pending |
| Dataset/documentation | `docs/DATASET_CARD.md` | pending |
| Raw evaluation | `artifacts/evaluation.json` + CSV/summary | pending |
| Demo video | pending | pending |
| Technical report | this document / PDF export | pending |

## 16. Reproducibility

Reproduction follows `README.md` inside `track3_VisioBotLab_RadeonVLA-Reflex/`:

1. create the ROCm Python environment and install `requirements.remote.txt`;
2. `python -m radeonvla.setup_assets`;
3. `python -m radeonvla.check_env --require-amd --init-genesis`;
4. record or download the dataset, then train or load the checkpoint;
5. run `python -m radeonvla.evaluate` and compare JSON against this report.

## 17. Team Member and Contribution

**Zhenwei Zhou:** system design, implementation, data generation, model training,
evaluation, documentation, and submission (VisioBot Lab, Nanjing University of Science
and Technology).

## 18. Limitations and Future Work

Current work is **simulation-only** (Genesis). Language and object coverage are limited to
the registered fruit/bowl suite. Real-robot transfer is out of scope for this submission.
Recovery is capped at one retry and is rule-based, not learned. After remote training I will
list empirical failure modes and any features that remain unmeasured.

## 19. References

- Genesis World
- Hugging Face LeRobot and SmolVLA
- AMD ROCm / Radeon developer documentation
- YCB Object and Model Set
- AMD Track 3 contest repository and Radeon Cloud user guide
- Track 3 Franka fruit-pick demo (workflow reference only)
