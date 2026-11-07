"""Chef Visión IA - interfaz Streamlit que orquesta los módulos."""
import streamlit as st

import config
from image_generator import generate_dish_image
from ingredient_detector import detect_ingredients
from nvidia_client import NvidiaError
from recipe_generator import generate_recipe
from video_generator import generate_dish_video

st.set_page_config(page_title="Chef Visión IA", page_icon="🍳", layout="wide")
ss = st.session_state
for k, v in {"ingredients": [], "recipe": None, "dish_img": None, "video": None}.items():
    ss.setdefault(k, v)

# ---------- Barra lateral: API key ----------
with st.sidebar:
    st.header("🔑 Configuración")
    default = st.secrets.get("NVIDIA_API_KEY", "") if hasattr(st, "secrets") else ""
    try:
        default = st.secrets.get("NVIDIA_API_KEY", "")
    except Exception:
        default = ""
    ss["api_key"] = st.text_input("API key de NVIDIA", value=ss.get("api_key", default),
                                  type="password",
                                  help="Gratis en https://build.nvidia.com/")
    st.markdown("[Obtener API key](https://build.nvidia.com/)")
    servings = st.number_input("Porciones", 1, 12, 2)
    restrictions = st.text_input("Restricciones dietéticas", placeholder="vegetariano, sin gluten…")
    max_min = st.slider("Tiempo disponible (min)", 10, 120, 45, 5)
    want_video = st.checkbox("🎬 Generar video (opcional, lento)", value=False)

st.title("🍳 Chef Visión IA")
st.caption("Fotografía tus ingredientes y obtén una receta, su imagen y el paso a paso.")

if not ss["api_key"]:
    st.info("👋 Ingresa tu API key de NVIDIA en la barra lateral para comenzar.")
    st.stop()

# ---------- Entrada de imagen ----------
tab_cam, tab_up = st.tabs(["📷 Cámara", "🖼️ Subir imagen"])
with tab_cam:
    cam = st.camera_input("Toma una foto de tus ingredientes")
with tab_up:
    up = st.file_uploader("Carga una imagen", type=["jpg", "jpeg", "png", "webp"])
source = cam or up
if source:
    st.image(source, caption="Imagen a analizar", use_container_width=True)

try:
    if source and st.button("🔍 Identificar ingredientes", type="primary", use_container_width=True):
        with st.spinner("Analizando la imagen…"):
            found = detect_ingredients(source.getvalue(), ss["api_key"])
        ss.update(ingredients=found, recipe=None, dish_img=None, video=None)
        if not found:
            st.warning("No encontré alimentos en la imagen. Prueba con otra foto.")
except (NvidiaError, ValueError) as exc:
    st.error(str(exc))

# ---------- Ingredientes editables ----------
if ss["ingredients"]:
    st.subheader("🥕 Ingredientes detectados")
    edited = st.data_editor(ss["ingredients"], num_rows="dynamic", use_container_width=True,
                            key="ing_editor")
    names = [r["nombre"] for r in edited if r.get("nombre")]
    if st.button("👨‍🍳 Crear receta", type="primary", use_container_width=True):
        try:
            with st.spinner("Creando receta…"):
                ss["recipe"] = generate_recipe(names, ss["api_key"], int(servings),
                                               restrictions, max_min)
            with st.spinner("Generando imagen del plato…"):
                ss["dish_img"] = generate_dish_image(ss["recipe"]["image_prompt"], ss["api_key"])
            if want_video:
                with st.spinner("Generando video (puede tardar minutos)…"):
                    ss["video"] = generate_dish_video(ss["recipe"]["image_prompt"], ss["api_key"])
        except (NvidiaError, ValueError) as exc:
            st.error(str(exc))

# ---------- Resultados ----------
r = ss["recipe"]
if r:
    t1, t2, t3 = st.tabs(["📋 Receta", "🖼️ Imagen", "👣 Paso a paso"])
    with t1:
        st.header(r["nombre"])
        st.write(r.get("descripcion", ""))
        c = st.columns(3)
        c[0].metric("Tiempo", r.get("tiempo_total", "-"))
        c[1].metric("Dificultad", r.get("dificultad", "-"))
        c[2].metric("Porciones", r.get("porciones", "-"))
        st.subheader("Ingredientes")
        for i in r.get("ingredientes_usados", []):
            st.markdown(f"- {i.get('cantidad', '')} {i.get('nombre', '')}")
        if r.get("ingredientes_despensa"):
            st.markdown("**De la despensa:** " + ", ".join(r["ingredientes_despensa"]))
    with t2:
        if ss["dish_img"]:
            st.image(ss["dish_img"], caption=r["nombre"], use_container_width=True)
        if ss["video"]:
            st.video(ss["video"])
    with t3:
        for p in r["pasos"]:
            st.markdown(f"**{p.get('numero', '')}.** {p.get('instruccion', '')}"
                        + (f" _(⏱ {p['tiempo']})_" if p.get("tiempo") else ""))
        for tip in r.get("consejos", []):
            st.info(f"💡 {tip}")
