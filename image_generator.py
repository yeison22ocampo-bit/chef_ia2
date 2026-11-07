"""Genera la imagen del plato con un modelo de imagen de NVIDIA."""
import base64

import config
from nvidia_client import NvidiaError, post_json


def generate_dish_image(image_prompt: str, api_key: str) -> bytes:
    """Devuelve bytes de la imagen (JPEG/PNG) del plato."""
    prompt = f"Professional food photography, {image_prompt}, natural light, appetizing, 4k"
    data = post_json(config.IMAGE_URL, api_key, {"prompt": prompt, **config.IMAGE_PARAMS})
    # Maneja formas comunes de respuesta base64
    b64 = None
    if isinstance(data.get("artifacts"), list) and data["artifacts"]:
        b64 = data["artifacts"][0].get("base64")
    b64 = b64 or data.get("image") or data.get("b64_json") or (
        data.get("data", [{}])[0].get("b64_json") if data.get("data") else None)
    if not b64:
        raise NvidiaError("El servicio no devolvió una imagen.")
    try:
        return base64.b64decode(b64, validate=True)
    except ValueError as exc:
        raise NvidiaError("Imagen recibida con formato inválido.") from exc


if __name__ == "__main__":
    import os
    open("plato.jpg", "wb").write(generate_dish_image("a bowl of tomato soup", os.environ["NVIDIA_API_KEY"]))
