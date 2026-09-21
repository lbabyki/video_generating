FROM nvidia/cuda:12.8.1-cudnn-runtime-ubuntu24.04@sha256:ac55d124da4882b497f732d8dfd9a702d5447a5f29d08d56da6f64f0a1eb34bc

ARG COMFYUI_COMMIT=b0f4b7b294ce482a2e071d9d762c133d38c7aa07
ARG PYTORCH_VERSION=2.11.0+cu128
ARG TORCHVISION_VERSION=0.26.0+cu128
ARG TORCHAUDIO_VERSION=2.11.0+cu128
ARG APP_UID=1001
ARG APP_GID=1001

ENV DEBIAN_FRONTEND=noninteractive VIRTUAL_ENV=/opt/venv PATH=/opt/venv/bin:$PATH PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates git python3 python3-venv \
    && rm -rf /var/lib/apt/lists/* && python3 -m venv "$VIRTUAL_ENV" \
    && pip install --no-cache-dir pip==25.0.1 setuptools==75.8.2 wheel==0.45.1

RUN git clone https://github.com/comfyanonymous/ComfyUI.git /opt/ComfyUI \
    && cd /opt/ComfyUI && git checkout --detach "$COMFYUI_COMMIT" \
    && test "$(git rev-parse HEAD)" = "$COMFYUI_COMMIT"

COPY docker/comfyui/requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir --only-binary=:all: --index-url https://pypi.org/simple --extra-index-url https://download.pytorch.org/whl/cu128 -r /tmp/requirements.lock \
    && python -c "import torch, torchaudio, torchvision; assert torch.__version__ == '${PYTORCH_VERSION}'; assert torchaudio.__version__ == '${TORCHAUDIO_VERSION}'; assert torchvision.__version__ == '${TORCHVISION_VERSION}'"

RUN groupadd --gid "$APP_GID" comfyui && useradd --uid "$APP_UID" --gid "$APP_GID" --create-home --shell /usr/sbin/nologin comfyui \
    && mkdir -p /opt/ComfyUI/models/{checkpoints,loras,vae,controlnet,clip_vision} /opt/ComfyUI/{input,output,user} \
    && chown -R comfyui:comfyui /opt/ComfyUI /opt/venv

WORKDIR /opt/ComfyUI
USER comfyui
EXPOSE 8188
CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
