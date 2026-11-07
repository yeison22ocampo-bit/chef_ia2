"""Utilidades: imágenes (Pillow), base64 y parseo JSON seguro."""
import base64
import io
import json
import re
from typing import Any

from PIL import Image, UnidentifiedImageError


def prepare_image(data: bytes, max_side: int = 1024, max_mb: int = 8, quality: int = 85) -> bytes:
    """Valida, corrige orientación, redimensiona y devuelve JPEG en bytes."""
    if not data:
        raise ValueError("La imagen está vacía.")
    if len(data) > max_mb * 1024 * 1024:
        raise ValueError(f"La imagen supera {max_mb} MB.")
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("El archivo no es una imagen válida.") from exc
    from PIL import ImageOps
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


def to_data_url(jpeg: bytes) -> str:
    """Convierte bytes JPEG a data URL base64."""
    return "data:image/jpeg;base64," + base64.b64encode(jpeg).decode()


def safe_json_loads(text: str) -> Any:
    """Extrae y parsea el primer objeto/arreglo JSON de un texto (tolera ```json)."""
    if not text:
        raise ValueError("Respuesta vacía.")
    text = re.sub(r"```(?:json)?", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for open_c, close_c in (("{", "}"), ("[", "]")):
        s, e = text.find(open_c), text.rfind(close_c)
        if s != -1 and e > s:
            try:
                return json.loads(text[s:e + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("No se pudo interpretar la respuesta como JSON.")


if __name__ == "__main__":
    print(safe_json_loads('```json\n{"a": 1}\n```'))
    im = io.BytesIO()
    Image.new("RGB", (2000, 1000), "red").save(im, "PNG")
    print(Image.open(io.BytesIO(prepare_image(im.getvalue()))).size)
