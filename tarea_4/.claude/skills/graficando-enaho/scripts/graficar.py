"""Gráficos de pobreza monetaria de la ENAHO 2024: barras ponderadas con su intervalo de confianza y un título que dice
qué muestran las cifras. El título, las notas y los valores se calculan aquí; ninguno se escribe a mano.

    uv run .claude/skills/graficando-enaho/scripts/graficar.py --por area
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --por sexo --solo departamento=Puno
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --por departamento --indicador pobre_extremo

Sale figuras/<nombre>.png a 200 dpi, e imprime la tabla con las cifras del gráfico.
"""
import argparse
import re
import sys
import textwrap
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patheffects import withStroke  # noqa: E402

sys.path.insert(0, str(Path(__file__).parents[2] / "limpiando-enaho" / "scripts"))
from estimar import (ANIO, ETIQUETA, INDICADORES, RAIZ, SALIDAS, base_para, diferencia, filtrar, nota_metodo,  # noqa: E402
                     separar_filtros, tabla)

FIGURAS = RAIZ / "figuras"
SUPERFICIE, TEXTO, TEXTO_2, REJILLA = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e0"
INTENSO, SUAVE = "#2a78d6", "#9ec5f4"
CV_REFERENCIAL = 15
PLURAL = {"Mujer": "las mujeres", "Hombre": "los hombres"}


def coma(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def _lugar(fila, por):
    """Cómo se nombra una categoría dentro de la frase del título."""
    return f"el grupo de {fila.categoria} años" if por == "grupo_edad" else fila.categoria


def titulo(por, t, dif, sujeto):
    """La frase principal del gráfico, según lo que dicen las cifras."""
    alta, baja = t.loc[t["pct"].idxmax()], t.loc[t["pct"].idxmin()]
    x, y, d = coma(alta.pct), coma(baja.pct), coma(alta.pct - baja.pct)
    if dif is None:
        return f"{sujeto} es más alta en {_lugar(alta, por)} ({x} %) y más baja en {_lugar(baja, por)} ({y} %)"
    if por == "area":
        if dif["distinguible"]:
            return (f"{sujeto} {alta.categoria.lower()} ({x} %) supera a la {baja.categoria.lower()} ({y} %) "
                    f"en {d} puntos porcentuales")
        return f"{sujeto} urbana y la rural no se distinguen: {alta.categoria.lower()} {x} %, {baja.categoria.lower()} {y} %"
    if dif["distinguible"]:
        return f"{sujeto} afecta más a {PLURAL[alta.categoria]} ({x} %) que a {PLURAL[baja.categoria]} ({y} %), por {d} puntos"
    return f"{sujeto} casi no cambia por sexo: {alta.categoria.lower()} {x} %, {baja.categoria.lower()} {y} %"


def lectura(t, total, dif):
    """Una línea que separa las diferencias reales del error de muestreo."""
    if dif is not None:
        rango = f"Diferencia con 95 % de confianza: de {coma(dif['ic95_inf'])} a {coma(dif['ic95_sup'])} puntos."
        return rango + ("" if dif["distinguible"] else " Incluye el cero: no se distingue del error de muestreo.")
    return (f"Respecto de {total}: {int((t['frente_total'] == 1).sum())} por encima, "
            f"{int((t['frente_total'] == -1).sum())} por debajo y {int((t['frente_total'] == 0).sum())} sin diferencia "
            "distinguible con 95 % de confianza (color suave).")


def comparar_con_total(df, y, por, t, dentro):
    """1, -1 o 0 si la categoría está por encima, por debajo o no se distingue del total de su dominio."""
    claves = df[por].astype(str)
    salida = []
    for codigo in t["codigo"]:
        d = diferencia(df, y, dentro & (claves == codigo), dentro)
        salida.append(0 if not d["distinguible"] else (1 if d["dif"] > 0 else -1))
    return salida


def dibujar(t, total, nombre_total, por, encabezado, subtitulo, pie, ruta, comparar):
    encabezado = textwrap.fill(encabezado, 78)
    lineas_titulo = encabezado.count("\n") + 1
    cabeza = 0.2 + 0.27 * lineas_titulo + 0.72  # todas las medidas en pulgadas
    base_pie = 0.14 + 0.16 * (pie.count("\n") + 1)
    alto = cabeza + 0.2 + 0.36 * len(t) + 0.56 + base_pie
    fig, ax = plt.subplots(figsize=(9, alto), facecolor=SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)
    t = t.iloc[::-1].reset_index(drop=True)  # barh dibuja de abajo hacia arriba
    colores = [INTENSO if (not comparar or f != 0) else SUAVE for f in t["frente_total"]]
    ax.barh(t.index, t["pct"], height=0.62, color=colores, zorder=2)
    ax.hlines(t.index, t["ic95_inf"], t["ic95_sup"], color=TEXTO_2, linewidth=1.1, zorder=3)
    ax.vlines(total, -0.6, len(t) - 0.5, color=TEXTO_2, linewidth=1, linestyle=(0, (4, 3)), zorder=4)
    tope = t["ic95_sup"].max()
    halo = [withStroke(linewidth=3, foreground=SUPERFICIE)]  # la línea del total no tapa las cifras
    for i, f in t.iterrows():
        marca = " †" if f["cv_pct"] > CV_REFERENCIAL else ""
        ax.text(f["ic95_sup"] + tope * 0.012, i, f"{coma(f['pct'])}{marca}", va="center", fontsize=9.5, color=TEXTO,
                path_effects=halo, zorder=5)
    ax.text(total, len(t) - 0.46, f"{nombre_total}: {coma(total)} %", ha="center", va="bottom", fontsize=9, color=TEXTO_2)
    ax.set_yticks(t.index, t["categoria"], fontsize=10, color=TEXTO)
    ax.set_xlim(0, tope * 1.1)
    ax.set_ylim(-0.6, len(t) - 0.1)
    ax.set_xlabel("% de personas", fontsize=9.5, color=TEXTO_2)
    ax.tick_params(axis="x", colors=TEXTO_2, labelsize=9, length=0)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=REJILLA, linewidth=0.7, zorder=0)
    for lado in ("top", "right", "left", "bottom"):
        ax.spines[lado].set_visible(False)
    fig.subplots_adjust(left=0.2 if por in ("departamento", "dominio") else 0.13, right=0.97, top=1 - cabeza / alto,
                        bottom=(base_pie + 0.56) / alto)
    izquierda = 0.02
    fig.text(izquierda, 1 - 0.2 / alto, encabezado, fontsize=13, fontweight="bold", color=TEXTO, va="top")
    fig.text(izquierda, 1 - (0.2 + 0.27 * lineas_titulo + 0.08) / alto, subtitulo, fontsize=9.5, color=TEXTO_2, va="top",
             linespacing=1.4)
    fig.text(izquierda, 0.1 / alto, pie, fontsize=7.5, color=TEXTO_2, va="bottom", linespacing=1.4)
    FIGURAS.mkdir(exist_ok=True)
    fig.savefig(ruta, dpi=200, facecolor=SUPERFICIE)
    plt.close(fig)


def sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", texto.lower()) if not unicodedata.combining(c))


def nombre_archivo(por, y, filtros):
    partes = ["pobreza_extrema" if y == "pobre_extremo" else "pobreza", por]
    partes += [re.sub(r"[^a-z0-9]+", "-", sin_tildes(f"{k}-{v}")) for k, v in filtros.items()]
    return "_".join(partes) + ".png"


def nombre_dominio(df, filtros):
    """Cómo se llama el dominio en el gráfico: Puno, Rural o Perú."""
    if not filtros:
        return "Perú"
    nombres = []
    for columna, valor in filtros.items():
        marca = filtrar(df, {columna: valor})
        nombres.append(str(df.loc[marca, ETIQUETA.get(columna, columna)].iloc[0]))
    return " · ".join(nombres)


def graficar(por, y="pobre", filtros=None, salidas=SALIDAS):
    filtros = filtros or {}
    if por in filtros:
        raise SystemExit(f"No se puede agrupar por {por} y filtrar por {por} a la vez.")
    df, unidad = base_para(por, filtros, salidas)
    dentro = filtrar(df, filtros)
    t = tabla(df, por, y, dentro)
    if len(t) < 2:
        raise SystemExit(f"Con ese filtro solo queda {len(t)} categoría de {por}: un gráfico de barras no aporta nada.")
    total = tabla(df, None, y, dentro)["pct"].iloc[0]
    comparar = len(t) > 2
    t["frente_total"] = comparar_con_total(df, y, por, t, dentro) if comparar else 1
    dif = None
    if not comparar:
        alta, baja = t.loc[t["pct"].idxmax(), "codigo"], t.loc[t["pct"].idxmin(), "codigo"]
        claves = df[por].astype(str)
        dif = diferencia(df, y, dentro & (claves == alta), dentro & (claves == baja))
    sujeto = "La pobreza extrema" if y == "pobre_extremo" else "La pobreza"
    lugar = nombre_dominio(df, filtros)
    subtitulo = (f"{INDICADORES[y]}, % de personas. {lugar}, {ANIO}. La línea fina es el intervalo de confianza de 95 %.\n"
                 + lectura(t, lugar, dif))
    notas = [f"Fuente: INEI, ENAHO {ANIO} ({'módulo 34' if unidad == 'hogares' else 'módulos 34 y 02'}). "
             f"Estimación ponderada: {nota_metodo(unidad)}. Elaboración propia."]
    if (t["cv_pct"] > CV_REFERENCIAL).any():
        notas.append(f"† Coeficiente de variación mayor a {CV_REFERENCIAL} %: cifra solo referencial.")
    ruta = FIGURAS / nombre_archivo(por, y, filtros)
    encabezado = titulo(por, t, dif, sujeto)
    dibujar(t, total, lugar, por, encabezado, subtitulo, "\n".join(notas), ruta, comparar)
    return ruta, encabezado, t, total, dif


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--por", required=True, choices=["area", "dominio", "departamento", "sexo", "grupo_edad"])
    p.add_argument("--indicador", default="pobre", choices=list(INDICADORES))
    p.add_argument("--solo", action="append", metavar="COLUMNA=VALOR", help="restringe el dominio; se puede repetir")
    a = p.parse_args()
    ruta, encabezado, t, total, dif = graficar(a.por, a.indicador, separar_filtros(a.solo))
    print(f"Guardado: {ruta.relative_to(RAIZ).as_posix()}")
    print(f"Título: {encabezado}")
    columnas = ["categoria", "pct", "ic95_inf", "ic95_sup", "cv_pct", "n_muestra"]
    print(pd.DataFrame(t[columnas]).round(2).to_string(index=False))
    print(f"Total del dominio: {total:.2f} %")
    if dif:
        print(f"Diferencia: {dif['dif']:.2f} pp, IC 95 % de {dif['ic95_inf']:.2f} a {dif['ic95_sup']:.2f}; "
              f"{'distinguible' if dif['distinguible'] else 'no distinguible'} del error de muestreo")


if __name__ == "__main__":
    main()
