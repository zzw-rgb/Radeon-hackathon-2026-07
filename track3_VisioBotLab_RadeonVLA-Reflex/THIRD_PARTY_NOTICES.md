# Third-Party Notices

RadeonVLA-Reflex depends on or references the following upstream projects:

| Project | Purpose | Source |
|---|---|---|
| Genesis World | Physics simulation | https://github.com/Genesis-Embodied-AI/genesis-world |
| LeRobot | Dataset, policy training, and SmolVLA | https://github.com/huggingface/lerobot |
| SmolVLA | Vision-language-action base model | https://huggingface.co/lerobot/smolvla_base |
| Franka Fruit-Pick Demo | Track 3 workflow reference | https://github.com/wangxunx/franka_fruit_pick_demo |
| YCB Object Set | Candidate simulation assets | https://www.ycbbenchmarks.com/object-models/ |

Each dependency and asset remains subject to its own license and attribution
requirements.

The Franka Fruit-Pick Demo revision I inspected did not include a top-level license
file. I keep that repository outside this submission tree and use it only as a
workflow reference for Genesis + LeRobot on ROCm. This submission’s source is
written for RadeonVLA-Reflex under VisioBot Lab.

Before redistributing robot or YCB-derived assets, I will record the original source,
exact revision, license, modifications, and required citation in this file.
