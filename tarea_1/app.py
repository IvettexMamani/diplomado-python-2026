"""Dashboard Streamlit – Tarea 1: ¿Pueden convertir titulares peruanos en un clasificador de noticias?

Ejecutar desde la carpeta tarea_1/:  streamlit run app.py
"""
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).parent
DATOS = BASE / "datos"
MODELO = BASE / "modelo"
ETIQUETAS = ["politica", "economia", "deportes", "ciencia_tecnologia"]
NOMBRES = {"politica": "Política", "economia": "Economía", "deportes": "Deportes",
           "ciencia_tecnologia": "Ciencia y tecnología"}

st.set_page_config(page_title="Clasificador de noticias peruanas", page_icon="🗞️", layout="wide")


@st.cache_data
def cargar_noticias():
    df = pd.read_csv(DATOS / "noticias.csv").fillna({"bajada": ""})
    llm = pd.read_csv(DATOS / "etiquetas_llm.csv")[["url", "etiqueta_llm", "confianza"]]
    return df.merge(llm, on="url", how="left")


@st.cache_data
def cargar_metricas():
    return json.loads((MODELO / "metricas.json").read_text(encoding="utf-8"))


@st.cache_resource
def cargar_clasificador():
    from transformers import pipeline
    return pipeline("text-classification", model=str(MODELO), top_k=None, device=-1)


df = cargar_noticias()
metricas = cargar_metricas()

# ------------------------------------------------------------------ encabezado
st.title("🗞️ ¿Pueden convertir titulares peruanos en un clasificador de noticias?")
st.markdown(
    f"""
**Sí.** A partir de **{len(df)} noticias de El Comercio** (descargadas el {df['fecha'].max()}) se entrenó un
clasificador que asigna cada titular a una de 4 categorías: política, economía, deportes o ciencia y tecnología.

**Metodología:**
1. Recolección desde los sitemaps oficiales del diario, respetando `robots.txt` y con pausas entre solicitudes.
2. La etiqueta de referencia sale de la sección del diario.
3. Línea base zero-shot (BETO-XNLI).
4. Etiquetado débil con un LLM local (Qwen2.5-1.5B) y auditoría humana de 20 casos.
5. Fine-tuning de **DistilBERT multilingüe** con un split estratificado 70/15/15, evaluado en un test reservado.
"""
)

# ------------------------------------------------------------------ filtros
st.sidebar.header("Filtros")
medios = sorted(df["medio"].unique())
sel_medios = st.sidebar.multiselect("Medio", medios, default=medios)
sel_categorias = st.sidebar.multiselect("Categoría", ETIQUETAS, default=ETIQUETAS, format_func=NOMBRES.get)
filtrado = df[df["medio"].isin(sel_medios) & df["etiqueta"].isin(sel_categorias)]
st.sidebar.caption(f"{len(filtrado)} de {len(df)} noticias en el filtro actual.")

# ------------------------------------------------------------------ indicadores
c1, c2, c3 = st.columns(3)
c1.metric("Noticias recolectadas", f"{len(df)}", help="Total del dataset limpio (datos/noticias.csv).")
c2.metric("F1 macro en test", f"{metricas['f1_macro_test']:.2f}",
          delta=f"{metricas['f1_macro_test'] - metricas['zero_shot_f1_40']:+.2f} vs. zero-shot",
          help=f"DistilBERT fine-tuned, evaluado en {metricas['n_test']} titulares nunca vistos en el entrenamiento.")
acuerdo = metricas.get("acuerdo_llm_humano")
c3.metric("Acuerdo LLM vs. auditoría humana", f"{acuerdo / 20:.0%}" if acuerdo is not None else "pendiente",
          help=f"{acuerdo}/20 predicciones del LLM confirmadas por revisión manual." if acuerdo is not None else None)

# ------------------------------------------------------------------ gráfico y tabla
st.subheader("Distribución de categorías")
if filtrado.empty:
    st.info("No hay noticias con los filtros seleccionados.")
else:
    conteo = (filtrado["etiqueta"].value_counts().reindex(sel_categorias).fillna(0).astype(int)
              .rename_axis("etiqueta").reset_index(name="noticias"))
    conteo["categoría"] = conteo["etiqueta"].map(NOMBRES)
    mayor = conteo.loc[conteo["noticias"].idxmax()]
    fig = px.bar(conteo, x="categoría", y="noticias", text="noticias", color="categoría",
                 title=f"{mayor['categoría']} concentra {mayor['noticias'] / conteo['noticias'].sum():.0%} "
                       f"de las {conteo['noticias'].sum()} noticias filtradas")
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Noticias")
    st.plotly_chart(fig, width="stretch")

st.subheader("Explorar noticias")
columnas = ["titular", "bajada", "etiqueta", "etiqueta_llm", "seccion_original", "fecha", "url"]
st.dataframe(filtrado[columnas], width="stretch", hide_index=True,
             column_config={"url": st.column_config.LinkColumn("url")})
st.download_button("⬇️ Descargar CSV filtrado", filtrado[columnas].to_csv(index=False).encode("utf-8"),
                   file_name="noticias_filtradas.csv", mime="text/csv")

# ------------------------------------------------------------------ probador en vivo
st.subheader("🔮 Probador en vivo")
st.caption("Escribe o pega un titular peruano y el modelo DistilBERT fine-tuned predice su categoría.")
if not (MODELO / "model.safetensors").exists():
    st.warning("No se encontraron los pesos del modelo (`modelo/model.safetensors`). "
               "Ejecuta `02_clasificacion.ipynb` para entrenarlo y guardarlo antes de usar el probador.")
else:
    titular = st.text_input("Titular", placeholder="Ej.: Congreso aprueba nuevo retiro de fondos de AFP")
    if st.button("Clasificar", type="primary"):
        if not titular.strip():
            st.error("Escribe un titular primero.")
        else:
            with st.spinner("Clasificando…"):
                salida = cargar_clasificador()(titular.strip())[0]
            probas = (pd.DataFrame(salida).assign(categoría=lambda d: d["label"].map(NOMBRES))
                      .sort_values("score", ascending=False))
            top = probas.iloc[0]
            st.success(f"**Categoría predicha: {top['categoría']}** — probabilidad {top['score']:.1%}")
            fig_p = px.bar(probas.sort_values("score"), x="score", y="categoría", orientation="h",
                           text=probas.sort_values("score")["score"].map("{:.1%}".format),
                           title=f"El modelo asigna {top['score']:.0%} de probabilidad a {top['categoría']}")
            fig_p.update_layout(xaxis_range=[0, 1], xaxis_title="Probabilidad", yaxis_title="")
            st.plotly_chart(fig_p, width="stretch")
