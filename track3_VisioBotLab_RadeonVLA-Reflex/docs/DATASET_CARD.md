# RadeonVLA-Reflex Dataset Card

> Status: draft. Fill measured fields after the demonstration dataset is finalized.

## Overview

- Dataset name: RadeonVLA-Reflex Demonstrations
- Version: TBD
- Generator commit: TBD
- Genesis version: 1.1.2
- LeRobot version: 0.6.0
- License: TBD after asset-license review
- Public URL: TBD
- SHA256 or dataset revision: TBD

## Task coverage

The primary L1 dataset has 20 variations: five fruits × four bowl positions.

| Fruit | Bowl positions | Planned training minimum | Validation | Held-out evaluation |
|---|---|---:|---:|---:|
| banana | white-left, blue-left, white-right, blue-right | 10 each | 5 each | 10 each |
| lemon | white-left, blue-left, white-right, blue-right | 10 each | 5 each | 10 each |
| plum | white-left, blue-left, white-right, blue-right | 10 each | 5 each | 10 each |
| apple | white-left, blue-left, white-right, blue-right | 10 each | 5 each | 10 each |
| orange | white-left, blue-left, white-right, blue-right | 10 each | 5 each | 10 each |

The release table will replace planned counts with the immutable dataset manifest. L2–L4
data are reported separately and are not implied by the primary L1 total.

## Frame schema

| Field | Shape/type | Description |
|---|---|---|
| observation.images.world | (240, 320, 3) uint8 | World RGB camera |
| observation.images.wrist | (240, 320, 3) uint8 | Wrist RGB camera |
| observation.state | (9,) float32 | Ordered robot and gripper qpos |
| action | (9,) float32 | Absolute joint-position target |
| task | string | Natural-language instruction |
| timestamp | float | Episode time (dataset metadata) |
| episode_index | integer | Episode identifier |
| frame_index | integer | Frame within episode |
| seed | integer | Reset seed (logged externally) |
| success | boolean | Independent success judgement (filter at record time) |

## Action protocol

- Action type: absolute_joint_position
- Joint names and order: panda_joint1..7, panda_finger_joint1..2
- Dimension: 9
- Joint unit: radians (arm), meters (fingers)
- Gripper convention and range: [0.0, 0.04], open=0.04, closed=0.0
- Control frequency: 20 Hz dataset (sim 100 Hz, decimated)

## Data generation

I collect data with the scripted multi-goal expert (`python -m radeonvla.record_dataset`):

1. expert states follow resolved L1–L4 goals after scene randomization;
2. success requires all subgoals inside the commanded bowl rim;
3. pose jitter is non-overlapping; optional appearance/physics DR flags are supported;
4. recording rate is 20 Hz (sim 100 Hz, decimated);
5. failed episodes are discarded by default (`--keep-failures` optional);
6. `validate_dataset` checks schema, non-finite values, and image statistics;
7. I spot-check camera videos under `datasets/*/videos/` before training.
8. Recording happens under `.inprogress`; the target path is replaced only after finalize,
   coverage checks, and a successful LeRobot reopen.

## Split policy

- Training seeds: 0–9999
- Validation seeds: 10000–10999
- Formal evaluation seeds: 20000–29999
- Interruption/recovery seeds: 30000–30999

No seed may occur in more than one split.

## Quality checks

- no black or corrupt images;
- state and action match the frozen schema;
- no NaN or infinity;
- task, object, and container agree;
- episode success is independently verified;
- random replay videos were manually inspected.

## Assets and limitations

Robot and YCB meshes are populated via `setup_assets` (see `assets/README.md` and
`THIRD_PARTY_NOTICES.md`). This dataset is simulation-only; object and language coverage
are limited to the registered fruit/bowl suite. Final episode counts and any class
imbalance will be written into the tables above when the release revision is frozen.
