"""Genera una receta estructurada (JSON) con DeepSeek."""
import config
from nvidia_client import chat
from utils import safe_json_loads

SCHEMA = (
    '{"nombre": str, "descripcion": str, "tiempo_total": str, "dificultad": str, '
    '"porciones": int, "ingredientes_usados": [{"nombre": str, "cantidad": str}], '
    '"ingredientes_despensa": [str], "pasos": [{"numero": int, "instruccion": str, '
    '"tiempo": str}], "consejos": [str], "image_prompt": "descripción en INGLÉS de la '
    'foto gastronómica del plato terminado"}'
)


def generate_recipe(ingredients: list[str], api_key: str, servings: int = 2,
                    restrictions: str = "", max_minutes: int = 45) -> dict:
    """Devuelve la receta como dict validado."""
    if not ingredients:
        raise ValueError("Se necesita al menos un ingrediente.")
    prompt = (
        f"Eres un chef. Crea UNA receta viable en {config.LANGUAGE} usando principalmente "
        f"estos ingredientes: {', '.join(ingredients)}. Puedes añadir básicos de despensa "
        f"(sal, aceite, agua, pimienta) listándolos aparte. Porciones: {servings}. "
        f"Restricciones dietéticas: {restrictions or 'ninguna'}. Tiempo máximo: "
        f"{max_minutes} min. Responde SOLO JSON estricto con este esquema: {SCHEMA}")
    for attempt in range(2):
        raw = chat(api_key, config.LLM_MODEL, [{"role": "user", "content": prompt}],
                   temperature=0.5, max_tokens=3000)
        try:
            r = safe_json_loads(raw)
            if r.get("nombre") and r.get("pasos") and r.get("image_prompt"):
                return r
            raise ValueError("Receta incompleta.")
        except (ValueError, AttributeError):
            if attempt == 1:
                raise ValueError("No se pudo generar una receta válida. Inténtalo de nuevo.")
    return {}


if __name__ == "__main__":
    import os, json
    print(json.dumps(generate_recipe(["huevos", "tomate"], os.environ["NVIDIA_API_KEY"]),
                     ensure_ascii=False, indent=2))
