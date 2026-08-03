# RadeonVLA-Reflex — AMD ROCm development image (preferable Track 3 deliverable)
# Base: ROCm 7.2.1 + Ubuntu 24.04 (Python 3.12)
#
# Build:
#   docker build -f docker/Dockerfile -t radeonvla-reflex:rocm7.2.1 .
#
# Run (bind-mount the project for assets/datasets/outputs):
#   docker run --rm -it --network=host \
#       --device=/dev/kfd --device=/dev/dri \
#       --group-add video --group-add render \
#       --security-opt seccomp=unconfined \
#       --cap-add=SYS_PTRACE \
#       --ipc=host --shm-size=8g \
#       -v "$PWD":/workspace/radeonvla-reflex \
#       radeonvla-reflex:rocm7.2.1

FROM rocm/dev-ubuntu-24.04:7.2.1-complete

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl wget git \
        libgl1 libglu1-mesa libegl1 libgles2 libglvnd0 libosmesa6 \
        libglib2.0-0 libsm6 libxext6 libxrender1 libx11-6 \
        libxi6 libxrandr2 libxcursor1 libxinerama1 libxfixes3 \
        libvulkan1 vulkan-tools mesa-vulkan-drivers \
        xvfb ffmpeg python3-venv python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -f render && usermod -aG render,video root

WORKDIR /workspace/radeonvla-reflex

# System-site venv so optional image-provided HIP wheels remain visible.
RUN python3 -m venv --system-site-packages /opt/venv
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

# Install ROCm PyTorch wheels when the base image does not already provide HIP torch.
ARG TORCH_WHL=torch-2.9.1+rocm7.2.1.lw.gitff65f5bc-cp312-cp312-linux_x86_64.whl
ARG VISION_WHL=torchvision-0.24.0+rocm7.2.1.gitb919bd0c-cp312-cp312-linux_x86_64.whl
ARG AUDIO_WHL=torchaudio-2.9.0+rocm7.2.1.gite3c6ee2b-cp312-cp312-linux_x86_64.whl
ARG TRITON_WHL=triton-3.5.1+rocm7.2.1.gita272dfa8-cp312-cp312-linux_x86_64.whl
ARG ROCM_WHL_BASE=https://repo.radeon.com/rocm/manylinux/rocm-rel-7.2.1

COPY requirements.remote.txt pyproject.toml README.md ./
COPY src ./src

RUN set -eux; \
    if ! python -c "import torch; assert torch.version.hip is not None"; then \
      mkdir -p /tmp/wheels && cd /tmp/wheels; \
      for w in "$TORCH_WHL" "$VISION_WHL" "$AUDIO_WHL" "$TRITON_WHL"; do \
        url="${ROCM_WHL_BASE}/$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$w")"; \
        wget -q -O "$w" "$url"; \
      done; \
      pip uninstall -y torch torchvision torchaudio triton || true; \
      pip install "$TORCH_WHL" "$VISION_WHL" "$AUDIO_WHL" "$TRITON_WHL"; \
      cd / && rm -rf /tmp/wheels; \
    fi

RUN pip install --no-cache-dir -r requirements.remote.txt \
 && pip install --no-cache-dir -e .

ENV PYOPENGL_PLATFORM=glx \
    HSA_ENABLE_SDMA=0 \
    HIP_VISIBLE_DEVICES=0

RUN python -c "import torch; assert torch.version.hip is not None, 'torch is not a ROCm build'; print(torch.__version__, torch.version.hip)" \
 && python -c "import genesis, lerobot; print('genesis/lerobot ok')"

CMD ["/bin/bash"]
