"""(Opcional) Clip de presentación con Cosmos text2video."""
import base64

import config
from nvidia_client import NvidiaError, post_json


def generate_dish_video(prompt: str, api_key: str) -> bytes:
    """Devuelve bytes mp4."""
    data = post_json(config.VIDEO_URL, api_key, {"prompt": prompt, **config.VIDEO_PARAMS},
                     timeout=600)
    if "b64_video" not in data:
        raise NvidiaError("El servicio no devolvió un video.")
    try:
        return base64.b64decode(data["b64_video"], validate=True)
    except ValueError as exc:
        raise NvidiaError("Video recibido con formato inválido.") from exc


if __name__ == "__main__":
    import os
    open("output.mp4", "wb").write(generate_dish_video("A steaming plate of pasta, cinematic", os.environ["NVIDIA_API_KEY"]))
