# Third-Party Notices

RadeonVLA-Reflex depends on or references the following upstream projects:

| Project | Purpose | Source |
|---|---|---|
| Genesis World | Physics simulation | https://github.com/Genesis-Embodied-AI/Genesis |
| LeRobot | Dataset, policy training, and SmolVLA | https://github.com/huggingface/lerobot |
| SmolVLA | Vision-language-action base model | https://huggingface.co/lerobot/smolvla_base |
| Franka Fruit-Pick Demo | Track 3 workflow reference | https://github.com/wangxunx/franka_fruit_pick_demo |
| YCB Object Set | Candidate simulation assets | https://www.ycbbenchmarks.com/object-models/ |

Each dependency and asset remains subject to its own license and attribution
requirements.

The Franka Fruit-Pick Demo is used only as a workflow reference for Genesis + LeRobot
on ROCm and is not vendored as source code in this tree.

### Bundled simulation assets under `assets/`

| Asset | Bundled path | Upstream |
|---|---|---|
| Franka Emika Panda MJCF | `assets/robots/franka/` | Genesis World package assets |
| YCB banana / apple / lemon / orange / plum / bowl | `assets/ycb/<id>/` | [YCB Object and Model Set](https://www.ycbbenchmarks.com/object-models/) |

YCB project pages:

- https://www.ycbbenchmarks.com/object-models/
- http://ycb-benchmarks.s3-website-us-east-1.amazonaws.com/

Integrity: `assets/SHA256SUMS` and `python -m radeonvla.setup_assets --verify`.
Blue bowl appearance is applied in scene code (entity surface color), not by editing
the upstream YCB texture files.
