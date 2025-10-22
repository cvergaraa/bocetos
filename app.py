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
st.set_page_config(page_title=' Tablero Inteligente', layout='wide')
st.title('🧠 Tablero Inteligente!')
st.subheader("✏️ Dibuja tu boceto en el panel y presiona **“Analizar imagen”**")

# --- Sidebar de configuración ---
with st.sidebar:
    st.subheader(" Propiedades del Tablero")

    # Dimensiones
    st.write("**Dimensiones del tablero**")
    canvas_width = st.slider("Ancho del tablero", 300, 700, 400, 50)
    canvas_height = st.slider("Alto del tablero", 200, 600, 300, 50)

    # Herramienta de dibujo
    drawing_mode = st.selectbox(
        "Herramienta de dibujo",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point")
    )

    # Ancho
