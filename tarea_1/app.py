"""Dashboard de la Tarea 1: clasificador de titulares de El Comercio.

Ejecutar desde la carpeta tarea_1/:  streamlit run app.py
"""
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

RAIZ = Path(__file__).parent
DATOS, MODELO = RAIZ / "datos", RAIZ / "modelo"
ETIQUETAS = ["politica", "economia", "deportes", "ciencia_tecnologia"]
NOMBRES = {"politica": "Política", "economia": "Economía", "deportes": "Deportes",
           "ciencia_tecnologia": "Ciencia y tecnología"}

st.set_page_config(page_title="Clasificador de titulares peruanos", page_icon="📰", layout="wide")


@st.cache_data
def cargar_datos():
    df = pd.read_csv(DATOS / "noticias.csv", parse_dates=["fecha"]).fillna({"bajada": ""})
    llm = pd.read_csv(DATOS / "etiquetas_llm.csv")[["url", "etiqueta_llm", "confianza"]]
    return df.merge(llm, on="url", how="left")


@st.cache_data
def cargar_metricas():
    return json.loads((MODELO / "metricas.json").read_text(encoding="utf-8"))


df = cargar_datos()
metricas = cargar_metricas()
fechas = df["fecha"]

# ------------------------------------------------------------------ encabezado
st.title("¿Se pueden convertir titulares peruanos en un clasificador de noticias?")
st.markdown(
    f"**{len(df)} titulares de El Comercio** publicados entre el {fechas.min():%d/%m} y el "
    f"{fechas.max():%d/%m/%Y}, clasificados en 4 categorías: política, economía, deportes y "
    "ciencia y tecnología. Un modelo DistilBERT ajustado con solo ~260 titulares los clasifica en "
    "milisegundos. Pruébalo al final de la página."
)
with st.expander("Resumen metodológico"):
    st.markdown(f"""
1. **Recolección** (`01_recoleccion.ipynb`): sitemaps oficiales de 4 secciones declarados en
   `robots.txt` y HTML de cada nota, con pausas de 1.5 s. Cada sección del diario se mapea a una
   de las 4 categorías; las columnas de opinión y las secciones que no encajan se descartan.
2. **Línea base zero-shot**: `Recognai/bert-base-spanish-wwm-cased-xnli`, sin entrenamiento
   (F1 macro {metricas['zero_shot_f1_40']:.2f} en 40 titulares).
3. **Supervisión débil con LLM**: `{metricas['modelo_llm']}` etiqueta las {metricas['n_noticias']}
   noticias con un prompt estructurado; una auditoría humana a ciegas de 20 casos mide su acuerdo.
4. **Fine-tuning**: `{metricas['modelo_base']}` con `Trainer` (3 épocas, batch 16, F1 macro),
   split estratificado 70/15/15 y evaluación final en {metricas['n_test']} titulares de test
   nunca vistos.
""")

# ------------------------------------------------------------------ filtros
st.sidebar.header("Filtros")
medios = sorted(df["medio"].unique())
sel_medios = st.sidebar.multiselect("Medio", medios, default=medios)
sel_categorias = st.sidebar.multiselect("Categoría", ETIQUETAS, default=ETIQUETAS, format_func=NOMBRES.get)
filtrado = df[df["medio"].isin(sel_medios) & df["etiqueta"].isin(sel_categorias)]
st.sidebar.caption(f"{len(filtrado)} de {len(df)} noticias con los filtros actuales.")

# ------------------------------------------------------------------ indicadores
zero_shot_test = next(c["f1_macro"] for c in metricas["comparativa"] if c["enfoque"].startswith("Zero-shot"))
acuerdo = metricas["acuerdo_llm_humano"]
c1, c2, c3 = st.columns(3)
c1.metric("Noticias recolectadas", f"{len(df)}", delta=f"{len(filtrado)} con los filtros", delta_color="off")
c2.metric("F1 macro en test (DistilBERT)", f"{metricas['f1_macro_test']:.2f}",
          delta=f"{metricas['f1_macro_test'] - zero_shot_test:+.2f} vs. zero-shot en el mismo test",
          help=f"Calculado sobre {metricas['n_test']} titulares de test reservados, nunca usados para entrenar.")
c3.metric("Acuerdo LLM vs. auditoría humana", f"{acuerdo / 20:.0%}" if acuerdo is not None else "pendiente",
          delta=f"{acuerdo}/20 casos revisados a ciegas" if acuerdo is not None else None, delta_color="off")

# ------------------------------------------------------------------ exploración
st.subheader("Exploración de las noticias")
if filtrado.empty:
    st.info("No hay noticias con los filtros seleccionados.")
else:
    conteo = (filtrado["etiqueta"].value_counts().reindex(sel_categorias).dropna().astype(int)
                .rename_axis("etiqueta").reset_index(name="noticias"))
    conteo["categoria"] = conteo["etiqueta"].map(NOMBRES)
    conteo["porcentaje"] = conteo["noticias"] / conteo["noticias"].sum()
    mayor, menor = conteo.loc[conteo["noticias"].idxmax()], conteo.loc[conteo["noticias"].idxmin()]
    if len(conteo) == 1:
        titulo = f"{len(filtrado)} noticias de {mayor['categoria']} con los filtros actuales"
    elif mayor["noticias"] - menor["noticias"] <= 0.15 * mayor["noticias"]:
        titulo = (f"Las {len(conteo)} categorías están casi balanceadas: entre {menor['noticias']} "
                  f"y {mayor['noticias']} noticias")
    else:
        titulo = (f"{mayor['categoria']} concentra más noticias ({mayor['noticias']}) "
                  f"que {menor['categoria']} ({menor['noticias']})")

    fig = px.bar(conteo, x="categoria", y="noticias", text="noticias",
                 custom_data=["porcentaje"], labels={"categoria": "Categoría", "noticias": "Noticias"})
    fig.update_traces(marker_color="#2a78d6", textposition="outside", width=0.55,
                      hovertemplate="%{x}<br>%{y} noticias (%{customdata[0]:.0%})<extra></extra>")
    fig.update_layout(title=titulo, barcornerradius=4, height=380,
                      yaxis_range=[0, conteo["noticias"].max() * 1.18], margin=dict(t=60, b=10))
    st.plotly_chart(fig, width="stretch")

    COLUMNAS = ["fecha", "etiqueta", "titular", "bajada", "medio", "seccion_original",
                "etiqueta_llm", "confianza", "url"]
    tabla = filtrado.sort_values("fecha", ascending=False)[COLUMNAS]
    st.dataframe(
        tabla, hide_index=True, width="stretch", height=360,
        column_config={
            "fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
            "etiqueta": "Categoría",
            "titular": st.column_config.TextColumn("Titular", width="large"),
            "bajada": st.column_config.TextColumn("Bajada", width="medium"),
            "medio": "Medio",
            "seccion_original": "Sección original",
            "etiqueta_llm": "Etiqueta del LLM",
            "confianza": st.column_config.NumberColumn("Confianza LLM", format="%.2f"),
            "url": st.column_config.LinkColumn("Enlace", display_text="Abrir"),
        },
    )
    st.download_button("Descargar CSV con los filtros actuales", type="secondary",
                       data=tabla.to_csv(index=False).encode("utf-8-sig"),
                       file_name="noticias_filtradas.csv", mime="text/csv")
