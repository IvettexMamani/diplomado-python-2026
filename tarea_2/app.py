"""App de la Tarea 2: documentos (OCR) y audios (ASR) con extracción por LLM.

Ejecutar desde la carpeta tarea_2/:  streamlit run app.py
"""
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).parent
DATOS, MODELOS = RAIZ / "datos", RAIZ / "modelos"

st.set_page_config(page_title="Tarea 2 – OCR y transcripción", page_icon="📄", layout="wide")

st.title("Tarea 2 – OCR y transcripción")
st.info("En construcción.")
