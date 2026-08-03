# Remote ROCm Setup

This document deliberately separates environment detection from installation. Never
install a wheel set before checking the remote instance.

## Step 1: Record the untouched environment

~~~bash
python3 --version
rocminfo | head -n 100
amd-smi
rocm-smi

python3 - <<'PY'
try:
    import torch
except Exception as exc:
    print("torch_import_error:", repr(exc))
else:
    print("torch:", torch.__version__)
    print("hip:", torch.version.hip)
    print("available:", torch.cuda.is_available())
    print("count:", torch.cuda.device_count())
PY
~~~

If torch.version.hip is non-null and the Radeon device is available, preserve that build.

## Step 2: Install a matching build only when needed

The Track 3 starter revision inspected on 2026-08-03 documents the following combination:

~~~text
Python 3.12
ROCm 7.2.1
torch 2.9.1 ROCm wheel
torchvision 0.24.0 ROCm wheel
torchaudio 2.9.0 ROCm wheel
triton 3.5.1 ROCm wheel
~~~

Use the exact commands from the official starter README only when the instance reports
that same ROCm and Python combination:

https://github.com/wangxunx/franka_fruit_pick_demo

For any other ROCm version, select the matching build from official AMD ROCm
documentation or the contest image instructions.

## Step 3: Protect the validated build

After installing the remaining dependencies:

~~~bash
python -m pip check
python - <<'PY'
import torch
assert torch.version.hip is not None
assert torch.cuda.is_available()
print(torch.__version__)
print(torch.version.hip)
print(torch.cuda.get_device_name(0))
PY
~~~

Then capture a package snapshot:

~~~bash
python -m pip freeze > docs/requirements.remote.freeze.txt
~~~

Do not use the local CPU requirements as the remote PyTorch installation source.
