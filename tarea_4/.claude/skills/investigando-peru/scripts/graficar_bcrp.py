"""Gráfico anual de series del BCRP guardadas con la herramienta MCP guardar_series. Suma los meses de cada año, apila
las series y calcula el título. Ninguna cifra se escribe a mano.

    uv run .claude/skills/investigando-peru/scripts/graficar_bcrp.py --datos salidas/bcrp/agroexportaciones_nacional.csv \
        --desde 2020 --hasta 2024 --tema agroexportaciones --unidad "millones de US$" \
        --etiqueta PN38744BM="No tradicionales agropecuarias" --etiqueta PN38740BM="Tradicionales agrícolas"

Sale figuras/<tema>_bcrp.png y salidas/<tema>_anual.csv. Un año incompleto se rechaza: sumaría menos meses que los demás.
"""
import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).parents[4]
SUPERFICIE, TEXTO, TEXTO_2, REJILLA = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e0"
COLORES = ["#2a78d6", "#eb6834", "#1baf7a"]  # posiciones fijas de la paleta categórica validada
DATOS_POR_ANIO = {"Anual": 1, "Trimestral": 4, "Mensual": 12}


def coma(x, d=0):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


def anual(d, desde, hasta):
    """Suma cada serie por año y devuelve una tabla con años en filas y códigos en columnas."""
    d = d.assign(anio=d["periodo"].astype(str).str[:4].astype(int))
    d = d[d["anio"].between(desde, hasta)]
    if d.empty:
        raise SystemExit(f"El archivo no tiene datos entre {desde} y {hasta}.")
    conteo = d.groupby(["codigo", "anio"]).size()
    esperado = d.groupby("codigo")["frecuencia"].first().map(DATOS_POR_ANIO)
    incompletos = [f"{c} {a} ({n} de {esperado[c]})" for (c, a), n in conteo.items() if n != esperado[c]]
    faltan = pd.MultiIndex.from_product([esperado.index, range(desde, hasta + 1)]).difference(conteo.index)
    if incompletos or len(faltan):
        raise SystemExit(f"Años incompletos, no se pueden sumar: {incompletos + [f'{c} {a} (0)' for c, a in faltan]}")
    return d.pivot_table(index="anio", columns="codigo", values="valor", aggfunc="sum")


def dibujar(t, etiquetas, tema, unidad, ruta):
    total = t.sum(axis=1)
    a, b = t.index[0], t.index[-1]
    variacion = (total[b] / total[a] - 1) * 100
    verbo = "crecieron" if variacion >= 0 else "cayeron"
    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)
    base = pd.Series(0.0, index=t.index)
    for i, codigo in enumerate(t.columns):
        ax.bar(t.index, t[codigo], bottom=base, width=0.56, color=COLORES[i], edgecolor=SUPERFICIE, linewidth=1.5,
               label=etiquetas.get(codigo, codigo), zorder=2)
        base = base + t[codigo]
    for anio, valor in total.items():
        ax.text(anio, valor * 1.012, coma(valor), ha="center", va="bottom", fontsize=10, color=TEXTO)
    ax.set_xticks(t.index, [str(x) for x in t.index], fontsize=10, color=TEXTO)
    ax.set_ylim(0, total.max() * 1.12)
    ax.set_ylabel(unidad, fontsize=9.5, color=TEXTO_2)
    ax.yaxis.set_major_formatter(lambda v, _: coma(v))
    ax.tick_params(axis="y", colors=TEXTO_2, labelsize=9, length=0)
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="y", color=REJILLA, linewidth=0.7, zorder=0)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(REJILLA)
    ax.legend(frameon=False, loc="upper left", fontsize=9.5, labelcolor=TEXTO)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.82, bottom=0.14)
    fig.text(0.02, 0.965, f"Las {tema} {verbo} {coma(abs(variacion))} % entre {a} y {b}", fontsize=13, fontweight="bold",
             color=TEXTO, va="top")
    fig.text(0.02, 0.905, f"Suma anual, {unidad} corrientes: de {coma(total[a])} en {a} a {coma(total[b])} en {b}.",
             fontsize=9.5, color=TEXTO_2, va="top")
    fig.text(0.02, 0.02, f"Fuente: BCRP, series {', '.join(t.columns)}. Valores FOB, sin ajustar por precios. "
                         "Elaboración propia.", fontsize=7.5, color=TEXTO_2, va="bottom")
    ruta.parent.mkdir(exist_ok=True)
    fig.savefig(ruta, dpi=200, facecolor=SUPERFICIE)
    plt.close(fig)
    return variacion


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--datos", type=Path, required=True, help="CSV de guardar_series")
    p.add_argument("--desde", type=int, required=True)
    p.add_argument("--hasta", type=int, required=True)
    p.add_argument("--tema", required=True, help="una palabra para el título y los archivos")
    p.add_argument("--unidad", required=True)
    p.add_argument("--etiqueta", action="append", default=[], metavar="CODIGO=TEXTO")
    a = p.parse_args()
    if not a.datos.exists():
        raise SystemExit(f"No existe {a.datos}. Guarda antes las series con la herramienta MCP guardar_series.")
    t = anual(pd.read_csv(a.datos), a.desde, a.hasta)
    if t.shape[1] > len(COLORES):
        sys.exit(f"Son {t.shape[1]} series y el gráfico apilado admite {len(COLORES)}.")
    etiquetas = dict(x.split("=", 1) for x in a.etiqueta)
    ruta = RAIZ / "figuras" / f"{a.tema}_bcrp.png"
    variacion = dibujar(t, etiquetas, a.tema, a.unidad, ruta)
    salida = t.assign(total=t.sum(axis=1)).round(2)
    salida.to_csv(RAIZ / "salidas" / f"{a.tema}_anual.csv", encoding="utf-8")
    print(f"Guardado: {ruta.relative_to(RAIZ).as_posix()} y salidas/{a.tema}_anual.csv")
    print(salida.to_string())
    print(f"Variación del total entre {a.desde} y {a.hasta}: {variacion:.2f} %")


if __name__ == "__main__":
    main()
