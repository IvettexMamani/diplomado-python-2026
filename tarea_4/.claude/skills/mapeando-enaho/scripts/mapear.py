"""Mapa coroplético de la pobreza monetaria por departamento con la ENAHO 2024. Une indicadores y geometrías por código
(ubigeo[:2] con FIRST_IDDP), nunca por nombre, y compara cada cifra con el archivo de referencia de la Sesión 16.

    uv run .claude/skills/mapeando-enaho/scripts/mapear.py
    uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobre_extremo

Sale mapas/pobreza_departamento.png, salidas/comparacion_mapa.csv y salidas/validacion_mapa.txt. Si la unión no da las
25 unidades, o si una cifra se aleja de la referencia, termina con un error y no guarda el mapa. El mapa de pobreza
extrema tiene su archivo y su validación aparte, sin comparación: la referencia solo cubre la pobreza total.
"""
import argparse
import math
import ssl
import sys
from pathlib import Path

import geopandas as gpd
import httpx
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import truststore  # noqa: E402
from matplotlib.colors import BoundaryNorm, ListedColormap  # noqa: E402
from matplotlib.patheffects import withStroke  # noqa: E402

sys.path.insert(0, str(Path(__file__).parents[2] / "limpiando-enaho" / "scripts"))
from estimar import ANIO, INDICADORES, RAIZ, SALIDAS, cargar, nota_metodo, tabla  # noqa: E402

GEOJSON = RAIZ / "datos" / "peru_departamental_simple.geojson"
URL_GEOJSON = ("https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/"
               "peru_departamental_simple.geojson")
REFERENCIA = Path(__file__).parents[1] / "referencias" / "pobreza_departamento_2024.csv"
MAPAS = RAIZ / "mapas"
LLAVE = "FIRST_IDDP"
UNIDADES = 25
TOLERANCIA = 0.1  # puntos porcentuales, frente a una referencia redondeada a un decimal
CV_REFERENCIAL = 15
SUPERFICIE, TEXTO, TEXTO_2 = "#fcfcfb", "#0b0b0b", "#52514e"
AZULES = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#104281", "#0b2f5e"]
HALO = [withStroke(linewidth=2.4, foreground=SUPERFICIE)]  # la etiqueta se lee sobre cualquier color y cruzando bordes

# Desplazamientos en grados para las etiquetas que no caben en su departamento
AJUSTE = {"Lima": (0.55, -0.25), "La Libertad": (0.1, 0.05), "Amazonas": (0.05, 0.3), "Áncash": (-0.1, 0.0),
          "Huancavelica": (-0.05, 0.1), "Ayacucho": (0.0, -0.25)}
FUERA = {"Tumbes": (-1.25, 0.25), "Lambayeque": (-1.35, -0.2), "Ica": (-1.1, -0.65), "Moquegua": (-2.1, -1.0),
         "Tacna": (-1.25, -1.05)}  # van fuera del polígono, con una línea guía
EN_RECUADRO = {"Callao": (-77.19, -12.12), "Lima": (-76.82, -11.95)}


def coma(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def geometrias():
    """Lee los límites; la llave se lee como texto para conservar el cero de 01 a 09."""
    if not GEOJSON.exists():
        r = httpx.get(URL_GEOJSON, timeout=60, verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT))
        r.raise_for_status()
        GEOJSON.parent.mkdir(parents=True, exist_ok=True)
        GEOJSON.write_bytes(r.content)
    return gpd.read_file(GEOJSON)


def unir(geo, t):
    """Une por código con 1:1 y devuelve (unión, problemas). Un problema aquí detiene el mapa."""
    problemas = []
    llave = geo[LLAVE].astype(str)
    if not llave.str.fullmatch(r"\d{2}").all():
        problemas.append(f"{LLAVE} no es un código de dos dígitos en todas las geometrías: {sorted(llave.unique())[:5]}")
    if len(geo) != UNIDADES or llave.nunique() != UNIDADES:
        problemas.append(f"El GeoJSON tiene {len(geo)} filas y {llave.nunique()} códigos; se esperan {UNIDADES}")
    u = geo.assign(**{LLAVE: llave}).merge(t, left_on=LLAVE, right_on="codigo", how="outer", validate="1:1", indicator=True)
    sin_cifra = u.loc[u["_merge"] == "left_only", LLAVE].tolist()
    sin_forma = u.loc[u["_merge"] == "right_only", "codigo"].tolist()
    if sin_cifra or sin_forma:
        problemas.append(f"Unión incompleta. Geometrías sin cifra: {sin_cifra}. Cifras sin geometría: {sin_forma}")
    if u["pct"].isna().any():
        problemas.append("Hay departamentos sin dato")
    if not {"07", "15"} <= set(u[LLAVE].dropna()):
        problemas.append("Lima (15) y Callao (07) deben aparecer como dos unidades")
    return u.drop(columns="_merge"), problemas


def comparar(u, ruta=REFERENCIA):
    """Tabla calculado frente a referencia. La referencia nunca entra al mapa."""
    ref = pd.read_csv(ruta, dtype={"ccdd": str}).rename(columns={"ccdd": "codigo", "pobreza_pct": "referencia"})
    c = pd.DataFrame(u.drop(columns="geometry")).merge(ref[["codigo", "referencia"]], on="codigo", how="outer",
                                                       validate="1:1")
    c["diferencia"] = c["pct"].round(2) - c["referencia"]
    columnas = ["codigo", "categoria", "pct", "referencia", "diferencia", "ic95_inf", "ic95_sup", "cv_pct", "n_muestra"]
    return c[columnas].sort_values("codigo").round(2)


def rotulo(fila):
    marca = " †" if fila.cv_pct > CV_REFERENCIAL else ""
    return f"{fila.categoria}\n{coma(fila.pct)}{marca}"


def dibujar(u, y, ruta):
    paso = 10 if u["pct"].max() > 25 else 5  # con 10 puntos, la pobreza extrema quedaría en solo dos clases
    tope = math.ceil(u["pct"].max() / paso) * paso
    limites = list(range(0, tope + 1, paso))
    colores = ListedColormap(AZULES[:len(limites) - 1])
    norma = BoundaryNorm(limites, colores.N)
    fig, ax = plt.subplots(figsize=(8.6, 10.6), facecolor=SUPERFICIE)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.9, bottom=0.07)
    u.plot(column="pct", cmap=colores, norm=norma, edgecolor=SUPERFICIE, linewidth=0.7, ax=ax)
    ax.set_axis_off()
    ax.set_xlim(-83.6, -67.6)
    ax.set_ylim(-19.2, 0.5)

    for fila, punto in zip(u.itertuples(), u.geometry.representative_point()):
        if fila.categoria == "Callao":
            continue  # se rotula en el recuadro
        if fila.categoria in FUERA:
            dx, dy = FUERA[fila.categoria]
            ax.annotate(rotulo(fila), xy=(punto.x, punto.y), xytext=(punto.x + dx, punto.y + dy), ha="center", va="center",
                        fontsize=7.5, color=TEXTO, arrowprops={"arrowstyle": "-", "color": TEXTO_2, "linewidth": 0.6})
        else:
            dx, dy = AJUSTE.get(fila.categoria, (0, 0))
            ax.text(punto.x + dx, punto.y + dy, rotulo(fila), ha="center", va="center", fontsize=7.5, color=TEXTO,
                    path_effects=HALO)

    # Recuadro con Lima y Callao, que en la escala nacional casi no se separan
    zoom = ax.inset_axes([0.02, 0.05, 0.25, 0.25], facecolor=SUPERFICIE)
    u.plot(column="pct", cmap=colores, norm=norma, edgecolor=SUPERFICIE, linewidth=1, ax=zoom)
    zoom.set_xlim(-77.35, -76.55)
    zoom.set_ylim(-12.35, -11.55)
    zoom.set_xticks([])
    zoom.set_yticks([])
    zoom.set_xlabel("")
    zoom.set_ylabel("")
    for fila in u.itertuples():
        if fila.categoria in EN_RECUADRO:
            zoom.text(*EN_RECUADRO[fila.categoria], rotulo(fila), ha="center", va="center", fontsize=7.5, color=TEXTO,
                      path_effects=HALO)
    zoom.set_title("Lima y Callao son dos unidades", fontsize=8, color=TEXTO_2, pad=4)
    ax.indicate_inset_zoom(zoom, edgecolor=TEXTO_2, alpha=0.8, linewidth=0.7)

    barra = fig.add_axes([0.06, 0.81, 0.27, 0.016])
    escala = fig.colorbar(plt.cm.ScalarMappable(norm=norma, cmap=colores), cax=barra, orientation="horizontal",
                          ticks=limites, drawedges=True)
    escala.dividers.set_color(SUPERFICIE)
    barra.set_title(f"{INDICADORES[y]} (% de personas)", fontsize=9, color=TEXTO_2, loc="left", pad=6)
    barra.tick_params(labelsize=9, colors=TEXTO_2, length=0)
    for lado in barra.spines.values():
        lado.set_visible(False)

    orden = u.sort_values("pct", ascending=False)
    a, b, z = orden.iloc[0], orden.iloc[1], orden.iloc[-1]
    sujeto = "pobreza extrema" if y == "pobre_extremo" else "pobreza"
    fig.text(0.03, 0.975, f"{a.categoria} ({coma(a.pct)} %) y {b.categoria} ({coma(b.pct)} %) tienen la mayor {sujeto};\n"
                          f"{z.categoria} ({coma(z.pct)} %), la menor", fontsize=14, fontweight="bold", color=TEXTO,
             va="top", linespacing=1.3)
    fig.text(0.03, 0.915, f"{INDICADORES[y]} por departamento, {ANIO}, % de personas. Lima no incluye Callao.",
             fontsize=10, color=TEXTO_2, va="top")
    notas = [f"Fuente: INEI, ENAHO {ANIO} (módulo 34), ponderado: {nota_metodo('hogares')}.",
             "Límites: repositorio del curso, unidos por código (ubigeo[:2] = FIRST_IDDP). Elaboración propia."]
    if (u["cv_pct"] > CV_REFERENCIAL).any():
        notas.append(f"† Coeficiente de variación mayor a {CV_REFERENCIAL} %: cifra solo referencial.")
    fig.text(0.03, 0.015, "\n".join(notas), fontsize=7.5, color=TEXTO_2, va="bottom", linespacing=1.4)
    ruta.parent.mkdir(exist_ok=True)
    fig.savefig(ruta, dpi=200, facecolor=SUPERFICIE)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--indicador", default="pobre", choices=list(INDICADORES))
    a = p.parse_args()
    t = tabla(cargar("hogares"), "departamento", a.indicador)  # la sumaria: el método de las cifras publicadas
    u, problemas = unir(geometrias(), t)
    lineas = [f"Validación del mapa, ENAHO {ANIO}: {INDICADORES[a.indicador]}", ""]
    lineas.append(f"[{'OK' if not problemas else 'FALLA':5}] Unión por código {LLAVE} = ubigeo[:2]: "
                  f"{int(u['pct'].notna().sum())} de {UNIDADES} unidades con geometría y dato")
    lineas += [f"[FALLA] {x}" for x in problemas]
    if a.indicador == "pobre" and not problemas:
        c = comparar(u)
        c.to_csv(SALIDAS / "comparacion_mapa.csv", index=False, encoding="utf-8")
        mayor = c.loc[c["diferencia"].abs().idxmax()]
        cumple = c["diferencia"].abs().max() <= TOLERANCIA
        lineas.append(f"[{'OK' if cumple else 'FALLA':5}] Frente a la referencia de la Sesión 16: diferencia máxima "
                      f"{abs(mayor.diferencia):.2f} pp ({mayor.categoria}), tolerancia {TOLERANCIA} pp")
        if not cumple:
            problemas.append(f"La cifra de {mayor.categoria} se aleja {abs(mayor.diferencia):.2f} pp de la referencia")
    elif a.indicador != "pobre":
        lineas.append("[AVISO] Sin comparación: la referencia de la Sesión 16 solo cubre la pobreza monetaria total")
    oficial = a.indicador == "pobre"
    ruta = MAPAS / ("pobreza_departamento.png" if oficial else "pobreza_extrema_departamento.png")
    lineas += ["", f"RESULTADO: {'RECHAZADO' if problemas else 'APROBADO'}", ""]
    informe = "validacion_mapa.txt" if oficial else "validacion_mapa_extrema.txt"  # cada mapa conserva su validación
    (SALIDAS / informe).write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas))
    if problemas:
        raise SystemExit("El mapa no se generó: " + "; ".join(problemas))
    dibujar(u, a.indicador, ruta)
    print(f"Guardado: {ruta.relative_to(RAIZ).as_posix()}")
    print(pd.DataFrame(u.drop(columns="geometry")).sort_values("pct", ascending=False)[
        ["codigo", "categoria", "pct", "ic95_inf", "ic95_sup", "cv_pct"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
