"""Cliente HTTP genérico para la API de NVIDIA (build.nvidia.com)."""
import time
from typing import Any

import requests

import config


class NvidiaError(Exception):
    """Error amigable (en español) al llamar a la API de NVIDIA."""


_MESSAGES = {
    401: "API key inválida o ausente. Revisa tu clave de build.nvidia.com.",
    403: "Acceso denegado: tu clave no tiene permiso para este modelo.",
    404: "Modelo o endpoint no encontrado. Verifica los IDs en config.py.",
    429: "Límite de uso alcanzado. Espera un momento e inténtalo de nuevo.",
}


def post_json(url: str, api_key: str, payload: dict, timeout: int = config.TIMEOUT,
              retries: int = config.RETRIES) -> dict[str, Any]:
    """POST JSON con reintentos (429/5xx). Nunca incluye la API key en errores."""
    if not api_key:
        raise NvidiaError(_MESSAGES[401])
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json",
               "Content-Type": "application/json"}
    last = "Error desconocido."
    for attempt in range(retries + 1):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.Timeout:
            last = "Tiempo de espera agotado."
        except requests.RequestException:
            last = "No se pudo conectar con el servicio de NVIDIA."
        else:
            if r.ok:
                try:
                    return r.json()
                except ValueError as exc:
                    raise NvidiaError("Respuesta no válida del servicio.") from exc
            if r.status_code in _MESSAGES and r.status_code != 429:
                raise NvidiaError(_MESSAGES[r.status_code])
            last = _MESSAGES.get(r.status_code) or (
                f"Error del servidor ({r.status_code})." if r.status_code >= 500
                else f"Solicitud rechazada ({r.status_code}): {r.text[:200]}")
            if r.status_code < 500 and r.status_code != 429:
                raise NvidiaError(last)
        if attempt < retries:
            time.sleep(2 ** attempt)
    raise NvidiaError(last)


def chat(api_key: str, model: str, messages: list[dict], temperature: float = 0.3,
         max_tokens: int = 2048) -> str:
    """Llamada a chat/completions (formato OpenAI). Devuelve el texto."""
    data = post_json(config.CHAT_URL, api_key, {
        "model": model, "messages": messages, "temperature": temperature,
        "max_tokens": max_tokens, "stream": False})
    try:
        return data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError) as exc:
        raise NvidiaError("Respuesta inesperada del modelo.") from exc


if __name__ == "__main__":
    import os
    print(chat(os.environ["NVIDIA_API_KEY"], config.LLM_MODEL,
               [{"role": "user", "content": "Di hola en una palabra"}]))
