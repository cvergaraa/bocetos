import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
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

# --- Sidebar con propiedades del tablero ---
with st.sidebar:
    st.subheader("⚙️ Propiedades del Tablero")

    # Dimensiones del tablero
    st.subheader("Dimensiones del Tablero")
    canvas_width = st.slider("Ancho del tablero", 300, 700, 500, 50)
    canvas_height = st.slider("Alto del tablero", 200, 600, 300, 50)

    # Herramienta de dibujo
    drawing_mode = st.selectbox(
        "Herramienta de Dibujo:",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point")
    )

    # Ancho de trazo
    stroke_width = st.slider("Selecciona el ancho de línea", 1, 30, 10)

    # Color del trazo
    stroke_color = st.color_picker("Color del trazo", "#000000")

    # Color de fondo
    bg_color = st.color_picker("Color de fondo", "#FFFFFF")

    st.markdown("---")
    st.info("💡 Consejo: Fondo blanco y trazo negro dan mejor contraste.")

    # Clave API
    ke = st.text_input('🔑 Ingresa tu Clave de OpenAI', type="password")
    os.environ['OPENAI_API_KEY'] = ke


# --- Inicialización del cliente ---
api_key = os.environ.get('OPENAI_API_KEY', None)
client = None
if api_key:
    client = OpenAI(api_key=api_key)

# --- Crear el lienzo con las propiedades configuradas ---
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
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

# --- Procesamiento del dibujo ---
if analyze_button:
    if not api_key:
        st.warning("⚠️ Por favor ingresa tu clave de OpenAI en la barra lateral.")
    elif canvas_result.image_data is None:
        st.warning("⚠️ Dibuja algo en el tablero antes de analizar.")
    else:
        with st.spinner("🧠 Analizando tu imagen..."):
            try:
                # Convertir y guardar la imagen
                input_numpy_array = np.array(canvas_result.image_data)
                input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
                input_image.save('img.png')

                # Codificar imagen a base64
                base64_image = encode_image_to_base64("img.png")

                # Prompt para la IA
                prompt_text = "Describe brevemente en español lo que se observa en la imagen."

                # Construcción del mensaje
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

                # Petición al modelo
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
Esta aplicación demuestra cómo una IA puede analizar un boceto dibujado a mano.  
Combina un **canvas interactivo** con la **API de OpenAI** para generar descripciones automáticas.
""")
