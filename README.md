# 🍳 Chef Visión IA

Foto de ingredientes → detección → receta → imagen del plato → paso a paso.

## Decisión de arquitectura
`deepseek-v4.1-flash` es un modelo de **texto**; por eso los ingredientes se detectan con un
modelo de **visión** de NVIDIA (`VISION_MODEL`) y DeepSeek genera receta y pasos.
La imagen del plato usa FLUX (opcional: video con Cosmos). Todo con una sola API key.

## Local
```bash
pip install -r requirements.txt
streamlit run app.py
```
API key gratis: https://build.nvidia.com/ (pégala en la barra lateral).
Prueba por módulo: `NVIDIA_API_KEY=... python recipe_generator.py`

## Despliegue en Streamlit Community Cloud
1. Sube el proyecto a GitHub (sin `secrets.toml`).
2. En https://streamlit.io → New app → elige repo, rama y `app.py`.
3. (Opcional) Settings → Secrets: `NVIDIA_API_KEY = "nvapi-..."`.

## Estructura
`app.py` UI · `config.py` constantes · `utils.py` imágenes/JSON · `nvidia_client.py` HTTP ·
`ingredient_detector.py` · `recipe_generator.py` · `image_generator.py` · `video_generator.py`

## Límites conocidos
- Verifica IDs de modelos y endpoints en `config.py`; el catálogo cambia.
- El video es lento y puede agotar el tiempo/cuota.
- La detección depende de la calidad de la foto.
