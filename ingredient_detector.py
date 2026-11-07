"""Detecta ingredientes en una foto usando un modelo de visión de NVIDIA."""
import config
from nvidia_client import chat
from utils import prepare_image, safe_json_loads, to_data_url

PROMPT = (
    "Analiza la imagen e identifica SOLO alimentos/ingredientes visibles. "
    "Si no hay alimentos, devuelve es_comida=false y lista vacía. No inventes. "
    'Responde SOLO JSON estricto: {"es_comida": bool, "ingredientes": '
    '[{"nombre": str, "cantidad": str, "confianza": número 0-1}]}. '
    f"Nombres en {config.LANGUAGE}."
)


def detect_ingredients(image_bytes: bytes, api_key: str) -> list[dict]:
    """Devuelve lista de ingredientes; lista vacía si no hay comida."""
    url = to_data_url(prepare_image(image_bytes, config.MAX_IMAGE_SIDE,
                                    config.MAX_IMAGE_MB, config.JPEG_QUALITY))
    messages = [{"role": "user", "content": [
        {"type": "text", "text": PROMPT},
        {"type": "image_url", "image_url": {"url": url}}]}]
    for attempt in range(2):  # reintenta una vez si el JSON es inválido
        raw = chat(api_key, config.VISION_MODEL, messages, temperature=0.1)
        try:
            data = safe_json_loads(raw)
            if not data.get("es_comida", True):
                return []
            items = [i for i in data.get("ingredientes", []) if i.get("nombre")]
            return [{"nombre": str(i["nombre"]).strip(),
                     "cantidad": str(i.get("cantidad", "")),
                     "confianza": float(i.get("confianza", 0) or 0)} for i in items]
        except (ValueError, AttributeError, TypeError):
            if attempt == 1:
                raise ValueError("No se pudo interpretar la respuesta del detector.")
    return []


if __name__ == "__main__":
    import os, sys
    print(detect_ingredients(open(sys.argv[1], "rb").read(), os.environ["NVIDIA_API_KEY"]))
