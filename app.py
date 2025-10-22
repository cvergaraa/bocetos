import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

# --- Función para codificar imagen a base64 ---
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# --- Configuración de la app ---
st.set_page_config(page_title='🧠 Tablero Inteligente', layout='wide')
st.title('🧠 Tablero Inteligente')
st.subheader("✏️ Dibuja tu boceto en el panel y presiona **“Analizar imagen”**")

# --- Sidebar de configuración ---
with st.sidebar:
    st.subheader("⚙️ Propiedades del Tablero")

    # Dimensiones
    st.write("**Dimensiones del tablero**")
    canvas_width = st.slider("Ancho del tablero", 300, 700, 400, 50)
    canvas_height = st.slider("Alto del tablero", 200, 600, 300, 50)

    # Herramienta de dibujo
    drawing_mode = st.selectbox(
        "Herramienta de dibujo",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point")
    )

    # Ancho del trazo
    stroke_width = st.slider("Ancho de línea", 1, 30, 5)

    # Colores
    stroke_color = st.color_picker("Color del trazo", "#000000")
    bg_color = st.color_picker("Color de fondo", "#FFFFFF")

    st.markdown("---")
    st.info("💡 Consejo: Usa fondo blanco y trazo negro para mejores resultados visuales.")

    # Clave API
    ke = st.text_input('🔑 Ingresa tu clave de OpenAI', type="password")
    os.environ['OPENAI_API_KEY'] = ke

# --- Inicialización del cliente ---
api_key = os.environ.get('OPENAI_API_KEY', None)
client = None
if api_key:
    client = OpenAI(api_key=api_key)

# --- Lienzo principal ---
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # color semitransparente para relleno
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=canvas_height,
    width=canvas_width,
    drawing_mode=drawing_mode,
    key=f"canvas_{canvas_width}_{canvas_height}",
)

# --- Botón de análisis ---
analyze_button = st.button("🔍 Analizar imagen", type="secondary")

# --- Procesamiento ---
if analyze_button:
    if not api_key:
        st.warning("⚠️ Por favor ingresa tu clave API en la barra lateral.")
    elif canvas_result.image_data is None:
        st.warning("⚠️ Dibuja un boceto en el tablero antes de analizar.")
    else:
        with st.spinner("🧠 Analizando tu imagen..."):
            try:
                # Guardar y convertir imagen
                input_numpy_array = np.array(canvas_result.image_data)
                input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
                input_image.save('img.png')

                # Codificar imagen
                base64_image = encode_image_to_base64("img.png")

                prompt_text = "Describe brevemente en español la imagen proporcionada."

                # Mensaje para el modelo
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": f"data:image/png;base64,{base64_image}",
                            },
                        ],
                    }
                ]

                # Llamada a la API de OpenAI
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=500,
                )

                # Mostrar respuesta
                if response.choices[0].message.content:
                    st.success("✅ Análisis completado:")
                    st.markdown(response.choices[0].message.content)

                    if Expert == profile_imgenh:
                        st.session_state.mi_respuesta = response.choices[0].message.content

            except Exception as e:
                st.error(f"Ocurrió un error durante el análisis: {e}")

# --- Sección informativa ---
st.sidebar.markdown("---")
st.sidebar.title("📘 Acerca de:")
st.sidebar.write("""
Esta aplicación permite dibujar un boceto y enviarlo a un modelo de IA 
para obtener una descripción generada automáticamente.

🧩 Combina visión computacional con modelos de lenguaje.
Desarrollado con **Streamlit** y **OpenAI API**.
""")
