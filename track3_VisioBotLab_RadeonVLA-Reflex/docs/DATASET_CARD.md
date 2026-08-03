# RadeonVLA-Reflex Dataset Card

> Status: template. Replace every TBD before release.

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

| Task | Training episodes | Validation episodes | Test episodes |
|---|---:|---:|---:|
| banana_left | TBD | TBD | TBD |
| banana_right | TBD | TBD | TBD |
| lemon_left | TBD | TBD | TBD |
| lemon_right | TBD | TBD | TBD |
| plum_left | TBD | TBD | TBD |
| plum_right | TBD | TBD | TBD |

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

Describe:

1. scripted expert states;
2. success criteria;
3. randomization ranges;
4. recording frequency;
5. filtering and rejection;
6. dataset validation;
7. visual replay audit.

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

List every redistributed robot, fruit, container, texture, and mesh source with its
license and modification history. State known task imbalance, simulation bias, and
coverage limitations.
