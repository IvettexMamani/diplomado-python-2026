"""Imágenes de las escenas del reel (900 × 570 px, fondo oscuro del video), hechas con los datos procesados.

Entradas: datos/procesados/*.csv (de analizar_datos.py), los límites departamentales y una
captura del dashboard (reel/recursos/captura_dashboard.png, opcional).
Salida: reel/recursos/escena{1..6}_*.png, que reel/guion.json usa en el campo «imagen».

Uso:
    python scripts/graficos_reel.py            # desde tarea_3/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Circle, Polygon  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "datos" / "procesados"
REC = RAIZ / "reel" / "recursos"
GEO = RAIZ / "datos" / "originales" / "peru_departamental_simple.geojson"

# Colores del video (los mismos de reel.py) y de la paleta del dashboard en modo oscuro
FONDO, TEXTO, SUAVE, ACENTO = "#1C1A17", "#F7F3EC", "#B8AE9F", "#F08A4B"
AZUL, ROJO, GRIS, REJILLA, MEDIO = "#3987e5", "#e66767", "#5b574f", "#34312c", "#46423b"
ANCHO_PX, ALTO_PX, DPI = 900, 570, 100


def estilo() -> None:
    # Public Sans es una fuente variable y matplotlib solo lee su peso más delgado:
    # se usa DejaVu Sans (viene con matplotlib y trae negrita)
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 17, "font.weight": "bold",
        "figure.facecolor": FONDO, "axes.facecolor": FONDO, "savefig.facecolor": FONDO,
        "text.color": TEXTO, "axes.labelcolor": SUAVE, "xtick.color": SUAVE, "ytick.color": SUAVE,
        "axes.edgecolor": REJILLA, "axes.grid": True, "grid.color": REJILLA, "grid.linewidth": 1,
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "axes.formatter.use_locale": False,
    })


def figura():
    return plt.figure(figsize=(ANCHO_PX / DPI, ALTO_PX / DPI), dpi=DPI)


def coma(x: float, dec: int = 1) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def guardar(fig, nombre: str) -> Path:
    ruta = REC / nombre
    fig.savefig(ruta, dpi=DPI)
    plt.close(fig)
    print(f"  {ruta.relative_to(RAIZ).as_posix()}")
    return ruta


def escena1_pictograma(lima: pd.DataFrame) -> None:
    """27,5 de cada 100: la tasa del último trimestre en Lima, como 100 puntos."""
    tasa = float(lima.iloc[-1].tasa_sub_ingresos)
    fig = figura()
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_xlim(-0.6, 19.6), ax.set_ylim(-1.6, 5.6), ax.axis("off"), ax.set_aspect("equal")
    llenos = int(tasa)
    parcial = tasa - llenos
    for k in range(100):
        fila, col = divmod(k, 20)
        x, y = col, 4 - fila
        ax.add_patch(Circle((x, y), 0.36, color=GRIS, lw=0))
        if k < llenos:
            ax.add_patch(Circle((x, y), 0.36, color=ACENTO, lw=0))
        elif k == llenos and parcial > 0:   # medio punto para el 0,5
            ax.add_patch(matplotlib.patches.Wedge((x, y), 0.36, 90, 90 + 360 * parcial, color=ACENTO, lw=0))
    ax.text(-0.4, -1.1, f"{coma(tasa)} de cada 100 personas de la fuerza laboral de Lima",
            fontsize=19, color=TEXTO, va="center")
    guardar(fig, "escena1_pictograma.png")


def escena2_lima(lima: pd.DataFrame) -> None:
    d = lima[lima.index >= "2023-01"]
    x = pd.to_datetime(d.index + "-01")
    v = d.var_interanual_pct.to_numpy()
    fig = figura()
    ax = fig.add_axes([0.13, 0.12, 0.80, 0.80])
    ax.bar(x, v, width=22, color=[ROJO if y > 0 else AZUL for y in v])
    ax.axhline(0, color=SUAVE, lw=1)
    ax.yaxis.set_major_formatter(lambda y, _: f"{y:+.0f} %".replace("+0", "0"))
    ax.set_ylim(min(v) - 3, max(v) + 5)
    ax.tick_params(length=0)
    ax.grid(axis="x", visible=False)
    ax.set_xticks(pd.to_datetime(["2023-01-01", "2024-01-01", "2025-01-01", "2026-01-01"]))
    ax.set_xticklabels(["2023", "2024", "2025", "2026"])
    ax.annotate(f"+{coma(v[-1])} %", (x[-1], v[-1]), xytext=(8, 4), textcoords="offset points",
                ha="right", va="bottom", fontsize=24, fontweight="bold", color=TEXTO)
    ax.text(-0.12, 1.03, "Variación interanual de los subempleados por ingresos, Lima (EPE)",
            transform=ax.transAxes, fontsize=15, color=SUAVE)
    guardar(fig, "escena2_lima_variacion.png")


def escena3_peru(nac: pd.DataFrame) -> None:
    fig = figura()
    ax = fig.add_axes([0.12, 0.12, 0.84, 0.78])
    ax.plot(nac.anio, nac.tasa_sub_ingresos, color=AZUL, lw=4, marker="o", ms=11,
            markeredgecolor=FONDO, markeredgewidth=2.5)
    ax.axvspan(2019.5, 2020.5, color=MEDIO, alpha=0.5, lw=0)
    ax.text(2020, 26, "Pandemia", ha="center", fontsize=14, color=SUAVE)
    for anio, dy in [(2020, 12), (2024, 14), (2025, -34)]:
        y = float(nac.loc[nac.anio == anio, "tasa_sub_ingresos"].iloc[0])
        ax.annotate(f"{coma(y)} %", (anio, y), xytext=(0, dy), textcoords="offset points", ha="center",
                    fontsize=22 if anio == 2025 else 18, fontweight="bold", color=TEXTO)
    ax.set_ylim(25, 58), ax.set_xlim(2018.6, 2025.5)
    ax.set_xticks(nac.anio)
    ax.yaxis.set_major_formatter(lambda y, _: f"{y:.0f} %")
    ax.tick_params(length=0)
    ax.grid(axis="x", visible=False)
    ax.text(-0.11, 1.04, "Perú: subempleo por ingresos, % de la fuerza laboral (ENAHO)",
            transform=ax.transAxes, fontsize=15, color=SUAVE)
    guardar(fig, "escena3_peru_tendencia.png")


def escena4_mapa(cambio: pd.DataFrame) -> None:
    geo = json.loads(GEO.read_text(encoding="utf-8"))
    dif = cambio.set_index(cambio.departamento.astype(str).str.zfill(2)).cambio_pp
    lim = float(np.ceil(dif.abs().max()))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("div", [AZUL, MEDIO, ROJO])
    norma = matplotlib.colors.TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim)
    fig = figura()
    ax = fig.add_axes([0.0, 0.0, 0.62, 1.0])
    ax.set_aspect("equal"), ax.axis("off")
    centros = {}
    for f in geo["features"]:
        cod = f["properties"]["FIRST_IDDP"]
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        mayor = None
        for p in polys:
            anillo = np.array(p[0])
            ax.add_patch(Polygon(anillo, closed=True, fc=cmap(norma(dif.get(cod, 0))), ec=FONDO, lw=0.8))
            if mayor is None or len(anillo) > len(mayor):
                mayor = anillo
        centros[cod] = mayor.mean(axis=0)
    ax.autoscale_view()
    # Etiqueta para Tumbes, el único departamento con alza significativa
    sube = cambio[cambio.significativo & (cambio.cambio_pp > 0)]
    for r in sube.itertuples():
        cx, cy = centros[str(r.departamento).zfill(2)]
        ax.annotate(f"{r.nombre}\n+{coma(r.cambio_pp)} pp", (cx, cy), xytext=(cx + 2.2, cy + 0.6),
                    fontsize=18, fontweight="bold", color=TEXTO,
                    arrowprops=dict(arrowstyle="-", color=TEXTO, lw=1.5))
    # Leyenda a la derecha
    ax2 = fig.add_axes([0.64, 0.10, 0.34, 0.80])
    ax2.axis("off")
    bajan = int((cambio.cambio_pp < 0).sum())
    ax2.text(0, 0.92, "Cambio 2024-2025", fontsize=17, color=SUAVE)
    ax2.text(0, 0.78, f"{bajan} de 25", fontsize=34, fontweight="bold", color=AZUL)
    ax2.text(0, 0.70, "departamentos bajaron", fontsize=16, color=TEXTO)
    ax2.text(0, 0.52, f"{len(sube)}", fontsize=34, fontweight="bold", color=ROJO)
    ax2.text(0, 0.44, "subió con un cambio\nsignificativo", fontsize=16, color=TEXTO, va="top")
    cb = fig.add_axes([0.66, 0.12, 0.28, 0.035])
    matplotlib.colorbar.ColorbarBase(cb, cmap=cmap, norm=norma, orientation="horizontal")
    cb.tick_params(colors=SUAVE, labelsize=12, length=0)
    cb.set_xticks([-lim, 0, lim], [f"−{lim:.0f} pp", "0", f"+{lim:.0f} pp"])
    for s in cb.spines.values():
        s.set_visible(False)
    guardar(fig, "escena4_mapa_cambio.png")


def escena5_brecha(grupos: pd.DataFrame) -> None:
    g = grupos[grupos.anio == 2025].set_index(["variable", "grupo"]).tasa
    filas = [("Mujeres", g["sexo", "Mujer"], ACENTO), ("Hombres", g["sexo", "Hombre"], GRIS),
             ("Rural", g["area", "Rural"], ACENTO), ("Urbana", g["area", "Urbana"], GRIS)]
    fig = figura()
    ax = fig.add_axes([0.22, 0.08, 0.72, 0.82])
    y = [3.6, 2.8, 1.0, 0.2]
    ax.barh(y, [f[1] for f in filas], height=0.62, color=[f[2] for f in filas])
    for yy, (nombre, val, _) in zip(y, filas):
        ax.text(-1.5, yy, nombre, ha="right", va="center", fontsize=20, color=TEXTO)
        ax.text(val + 1, yy, f"{coma(val)} %", va="center", fontsize=22, fontweight="bold", color=TEXTO)
    ax.text(0, 4.35, "Por sexo", fontsize=15, color=SUAVE)
    ax.text(0, 1.75, "Por área", fontsize=15, color=SUAVE)
    ax.set_xlim(0, 70), ax.set_ylim(-0.4, 4.7)
    ax.axis("off")
    guardar(fig, "escena5_brecha.png")


def escena6_dashboard() -> None:
    """Recorte de la captura del dashboard, con borde redondeado; si no hay captura, se omite."""
    origen = REC / "captura_dashboard.png"
    if not origen.exists():
        print("  (sin reel/recursos/captura_dashboard.png: la escena 6 se arma sin imagen)")
        return
    from PIL import Image, ImageDraw
    img = Image.open(origen).convert("RGB")
    img.thumbnail((ANCHO_PX, ALTO_PX))
    lienzo = Image.new("RGB", (ANCHO_PX, ALTO_PX), FONDO)
    mascara = Image.new("L", img.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, *img.size), radius=22, fill=255)
    lienzo.paste(img, ((ANCHO_PX - img.width) // 2, (ALTO_PX - img.height) // 2), mascara)
    lienzo.save(REC / "escena6_dashboard.png")
    print("  reel/recursos/escena6_dashboard.png")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    REC.mkdir(parents=True, exist_ok=True)
    estilo()
    lima = pd.read_csv(PROC / "serie_lima_epe.csv", index_col=0)
    nac = pd.read_csv(PROC / "serie_nacional.csv")
    cambio = pd.read_csv(PROC / "cambio_departamento_2024_2025.csv", dtype={"departamento": str})
    grupos = pd.read_csv(PROC / "tasas_grupos.csv")
    print("Imágenes del reel:")
    escena1_pictograma(lima)
    escena2_lima(lima)
    escena3_peru(nac)
    escena4_mapa(cambio)
    escena5_brecha(grupos)
    escena6_dashboard()
    return 0


if __name__ == "__main__":
    sys.exit(main())
