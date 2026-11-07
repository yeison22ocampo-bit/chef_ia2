"""Configuración central. VERIFICA estos valores en https://build.nvidia.com/."""

# LLM de texto (receta y pasos). Ajusta el ID exacto según el catálogo.
LLM_MODEL = "deepseek-ai/deepseek-v4.1-flash"
# Modelo de visión (DeepSeek Flash es solo texto): detecta ingredientes.
VISION_MODEL = "meta/llama-3.2-90b-vision-instruct"
CHAT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# Generación de imagen (FLUX.1-schnell del catálogo NVIDIA). Cambia modelo/URL si lo deseas.
IMAGE_URL = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-schnell"
IMAGE_PARAMS = {"width": 1024, "height": 1024, "steps": 4, "seed": 0}

# Video opcional (Cosmos text2video)
VIDEO_URL = "https://ai.api.nvidia.com/v1/cosmos/nvidia/cosmos3-nano"
VIDEO_PARAMS = {"model_mode": "text2video", "resolution": "480_16_9",
                "num_frames": 25, "num_inference_steps": 35, "fps": 24, "seed": 42}

TIMEOUT = 120          # segundos por petición
RETRIES = 2            # reintentos en 429/5xx
MAX_IMAGE_SIDE = 1024  # px, lado máximo al enviar la foto
MAX_IMAGE_MB = 8
JPEG_QUALITY = 85
LANGUAGE = "español"
