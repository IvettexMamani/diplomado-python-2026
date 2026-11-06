"""Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO 2024, los une y valida el resultado.

    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py

Entra: datos/enaho/966-Modulo34.zip y 966-Modulo02.zip (se descargan del INEI si faltan).
Sale, en salidas/: personas_2024.parquet, hogares_2024.parquet, indicadores.csv y validacion.txt.

Las cifras de referencia solo se comparan: nada del proceso las usa para ajustar un resultado. Si falla una validación
esencial, validacion.txt lo dice, no queda ninguna base procesada y el proceso termina con un error.
"""
import argparse
import hashlib
import io
import re
import ssl
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import httpx
import numpy as np
import pandas as pd
import truststore

sys.path.insert(0, str(Path(__file__).parent))
from estimar import ANIO, INDICADORES, RAIZ, SALIDAS, fila, tabla  # noqa: E402

DATOS = RAIZ / "datos" / "enaho"
URL = "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo{}.zip"
SUMARIA = re.compile(r"/sumaria-2024\.dta$", re.I)  # no sumaria-2024-12g.dta, la versión con 12 grupos de gasto
MIEMBROS = re.compile(r"/enaho01-2024-200\.dta$", re.I)  # no las tablas de ocupaciones que trae el mismo zip

LLAVES = {"conglome": 6, "vivienda": 3, "hogar": 2}
COLUMNAS_HOGAR = ["conglome", "vivienda", "hogar", "ubigeo", "dominio", "estrato", "mes", "mieperho", "factor07",
                  "pobreza", "linea", "linpe", "gashog2d", "inghog1d"]
COLUMNAS_PERSONA = ["conglome", "vivienda", "hogar", "codperso", "ubigeo", "estrato", "p203", "p204", "p205", "p206",
                    "p207", "p208a", "facpob07"]
DEPARTAMENTOS = {"01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho",
                 "06": "Cajamarca", "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco", "11": "Ica",
                 "12": "Junín", "13": "La Libertad", "14": "Lambayeque", "15": "Lima", "16": "Loreto",
                 "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura", "21": "Puno",
                 "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali"}
DOMINIOS = {1: "Costa norte", 2: "Costa centro", 3: "Costa sur", 4: "Sierra norte", 5: "Sierra centro",
            6: "Sierra sur", 7: "Selva", 8: "Lima Metropolitana"}
EDADES = ([0, 15, 30, 45, 60, 130], ["0-14", "15-29", "30-44", "45-59", "60 y más"])

# De la Tarea 4, la Sesión 16 y la Ficha Técnica de la ENAHO 2024. Solo se comparan con lo calculado.
REFERENCIA = {"hogares": 33_691, "filas_modulo_02": 117_721, "residentes": 108_664, "upm": 5_359, "pobreza": 27.6,
              "urbana": 24.8, "rural": 39.3, "extrema": 5.5, "lima_metropolitana": 28.2}
TOLERANCIA = 0.1  # puntos porcentuales
POBLACION = (33e6, 36e6)  # orden de magnitud de la población del Perú: delata un factor mal aplicado


class Validacion:
    """Lleva las comprobaciones. Con esencial=True, un incumplimiento rechaza la base; con False, solo avisa."""

    def __init__(self):
        self.lineas = []
        self.aprobadas = self.fallas = self.avisos = 0

    def comprobar(self, cumple, texto, esencial=True):
        cumple = bool(cumple)
        marca = "OK" if cumple else ("FALLA" if esencial else "AVISO")
        self.lineas.append(f"[{marca:5}] {texto}")
        self.aprobadas += cumple
        self.fallas += (not cumple) and esencial
        self.avisos += (not cumple) and not esencial

    def seccion(self, texto):
        self.lineas += ["", texto]

    def informar(self, texto):
        self.lineas.append(f"        {texto}")


def bajar(modulo, datos):
    """Descarga el zip del INEI si no está. Si el portal no responde, explica cómo conseguirlo a mano."""
    ruta = datos / f"966-Modulo{modulo}.zip"
    if ruta.exists():
        return ruta
    url = URL.format(modulo)
    print(f"Descargando {url}")
    try:
        r = httpx.get(url, timeout=300, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"},
                      verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT))
        r.raise_for_status()
        zipfile.ZipFile(io.BytesIO(r.content))
    except (httpx.HTTPError, zipfile.BadZipFile) as e:
        raise SystemExit(f"No se pudo descargar {url} ({e}). Bájalo desde el navegador y guárdalo en {ruta}.")
    datos.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(r.content)
    return ruta


def normalizar(nombre):
    """Nombres en minúscula; el año llega como aÑo y queda anio."""
    return nombre.strip().lower().replace("ñ", "ni")


def leer(ruta, patron):
    """Lee el .dta del zip sin convertir etiquetas: los códigos siguen siendo números y las llaves, texto."""
    with zipfile.ZipFile(ruta) as z:
        nombres = [n for n in z.namelist() if patron.search(n)]
        if len(nombres) != 1:
            raise SystemExit(f"Esperaba un archivo {patron.pattern} en {ruta} y hay {len(nombres)}.")
        d = pd.read_stata(io.BytesIO(z.read(nombres[0])), convert_categoricals=False)
    d.columns = [normalizar(c) for c in d.columns]
    return d


def ancho_fijo(serie, ancho):
    """Una llave es texto de ancho fijo: si llegó como número, ya perdió sus ceros iniciales."""
    return pd.api.types.is_string_dtype(serie) and serie.astype(str).str.fullmatch(rf"\d{{{ancho}}}").all()


def residentes(m):
    """El filtro de la sesión: miembros presentes, y no miembros que llevan 30 días o más en el hogar."""
    return m[((m["p204"] == 1) & (m["p205"] == 2)) | ((m["p204"] == 2) & (m["p206"] == 1))]


def territorio(d):
    """Departamento, área, dominio y pobreza. Iguales en las dos bases, para que un corte no dependa de cuál se usa."""
    d["departamento"] = d["ubigeo"].str[:2]
    d["nombre_departamento"] = d["departamento"].map(DEPARTAMENTOS)
    d["urbano"] = d["estrato"] <= 5
    d["area"] = np.where(d["urbano"], "Urbana", "Rural")
    d["nombre_dominio"] = d["dominio"].map(DOMINIOS)
    d["estrato_diseno"] = d["departamento"] + "-" + d["estrato"].astype(str)
    d["pobre"] = (d["pobreza"] <= 2).astype("int8")
    d["pobre_extremo"] = (d["pobreza"] == 1).astype("int8")
    return d


def construir(sumaria, miembros):
    """Devuelve (hogares, personas). El merge con validate='m:1' lanza MergeError si un hogar está repetido."""
    h = territorio(sumaria[COLUMNAS_HOGAR].copy())
    miembros_hogar = h["mieperho"].astype(float)  # llega en int8: 12 × mieperho se desborda con 11 miembros o más
    h["peso"] = h["factor07"].astype(float) * miembros_hogar
    h["gasto_mensual_pc"] = h["gashog2d"] / (12 * miembros_hogar)
    columnas = ["conglome", "vivienda", "hogar", "ubigeo", "estrato", "dominio", "mes", "mieperho", "factor07",
                "pobreza", "linea", "linpe", "gasto_mensual_pc"]
    p = residentes(miembros[COLUMNAS_PERSONA]).merge(h[columnas], on=list(LLAVES), how="left", validate="m:1",
                                                     suffixes=("", "_hogar"), indicator=True)
    p = territorio(p)
    p["peso"] = p["facpob07"].astype(float)
    p["sexo"] = p["p207"].map({1: "Hombre", 2: "Mujer"})
    p["edad"] = p["p208a"]
    p["grupo_edad"] = pd.cut(p["edad"], bins=EDADES[0], labels=EDADES[1], right=False).astype(str)
    return h, p


def validar(sumaria, miembros, h, p):
    v, ref = Validacion(), REFERENCIA
    todos_h, todos_p = pd.Series(True, index=h.index), pd.Series(True, index=p.index)

    v.seccion("Lectura y llaves")
    v.comprobar(len(sumaria) == ref["hogares"], f"Hogares en la sumaria: {len(sumaria):,} (esperado {ref['hogares']:,})")
    v.comprobar(len(miembros) == ref["filas_modulo_02"],
                f"Filas del módulo 02: {len(miembros):,} (esperado {ref['filas_modulo_02']:,})")
    for nombre, d in (("sumaria", sumaria), ("módulo 02", miembros)):
        v.comprobar(all(ancho_fijo(d[c], n) for c, n in LLAVES.items()) and ancho_fijo(d["ubigeo"], 6),
                    f"Llaves y ubigeo como texto de ancho fijo, con sus ceros iniciales ({nombre})")
    v.comprobar(not sumaria.duplicated(list(LLAVES)).any(), "Sin hogares repetidos en la sumaria")
    v.comprobar(not miembros.duplicated([*LLAVES, "codperso"]).any(), "Sin personas repetidas en el módulo 02")

    v.seccion("Residentes habituales y unión")
    antes = len(residentes(miembros))
    v.comprobar(antes == ref["residentes"],
                f"Residentes habituales: {antes:,} de {len(miembros):,} filas (esperado {ref['residentes']:,})")
    sin_hogar = int((p["_merge"] != "both").sum())
    v.comprobar(sin_hogar == 0, f"Unión validate='m:1': {sin_hogar} residentes sin hogar")
    v.comprobar(len(p) == antes and not p.duplicated([*LLAVES, "codperso"]).any(),
                f"La unión no pierde ni duplica personas: {antes:,} antes y {len(p):,} después")
    iguales = (p["ubigeo"] == p["ubigeo_hogar"]) & (p["estrato"] == p["estrato_hogar"])
    v.comprobar(iguales.all(), f"Ubigeo y estrato coinciden entre módulos en {iguales.mean():.1%} de los residentes")
    unidos = len(p.drop_duplicates(list(LLAVES)))
    v.comprobar(unidos == len(h), f"Hogares con al menos un residente: {unidos:,} de {len(h):,}", esencial=False)

    v.seccion("Territorio")
    v.comprobar(set(h["departamento"]) == set(p["departamento"]) == set(DEPARTAMENTOS),
                f"Códigos territoriales: {h['departamento'].nunique()} en hogares y {p['departamento'].nunique()} en "
                "personas, del 01 al 25, con Lima (15) y Callao (07) separados")
    v.comprobar(h["conglome"].nunique() == ref["upm"],
                f"Conglomerados: {h['conglome'].nunique():,} (Ficha Técnica: {ref['upm']:,})", esencial=False)

    v.seccion("Factores de expansión")
    sin_peso = int((~(h["factor07"] > 0)).sum() + (~(h["mieperho"] > 0)).sum() + (~(p["facpob07"] > 0)).sum())
    v.comprobar(sin_peso == 0, f"Pesos faltantes o no positivos: {sin_peso}")
    pob_h, pob_p = h["peso"].sum(), p["peso"].sum()
    v.comprobar(POBLACION[0] < pob_h < POBLACION[1] and POBLACION[0] < pob_p < POBLACION[1],
                f"Población expandida: {pob_h:,.0f} con factor07 × mieperho y {pob_p:,.0f} con facpob07")
    iguales = np.isclose(p["facpob07"], p["factor07"])
    v.comprobar(iguales.all(), f"facpob07 es el factor del hogar en {iguales.mean():.1%} de los residentes")

    v.seccion("Pobreza")
    v.comprobar(h["pobreza"].isin([1, 2, 3]).all(), "pobreza solo toma los valores 1, 2 y 3, sin faltantes")
    bajo_linea = h["gasto_mensual_pc"] < h["linea"]
    v.comprobar((bajo_linea == (h["pobre"] == 1)).all(), "La variable pobreza se reproduce con gasto mensual por "
                f"persona < línea en {(bajo_linea == (h['pobre'] == 1)).mean():.2%} de los hogares")
    nacional = fila(h, "pobre", todos_h)["pct"]
    por_personas = fila(p, "pobre", todos_p)["pct"]
    for texto, valor in (("sumaria, factor07 × mieperho", nacional), ("residentes, facpob07", por_personas)):
        v.comprobar(abs(valor - ref["pobreza"]) <= TOLERANCIA, f"Pobreza nacional ({texto}): {valor:.2f} % "
                    f"(referencia {ref['pobreza']} %, tolerancia ±{TOLERANCIA} pp)")
    for texto, dentro, y, clave in (("Pobreza urbana", h["urbano"], "pobre", "urbana"),
                                    ("Pobreza rural", ~h["urbano"], "pobre", "rural"),
                                    ("Pobreza extrema", todos_h, "pobre_extremo", "extrema"),
                                    ("Lima Metropolitana", h["dominio"] == 8, "pobre", "lima_metropolitana")):
        valor = fila(h, y, dentro)["pct"]
        v.comprobar(abs(valor - ref[clave]) <= TOLERANCIA, f"{texto}: {valor:.2f} % (referencia {ref[clave]} %)",
                    esencial=False)

    v.seccion("Por qué importa ponderar (solo para comparar)")
    simple_h, simple_p = h["pobre"].mean() * 100, p["pobre"].mean() * 100
    v.informar(f"Promedio simple de hogares: {simple_h:.2f} %. De personas: {simple_p:.2f} %. "
               f"Hogares con factor07, sin mieperho: {np.average(h['pobre'], weights=h['factor07']) * 100:.2f} %.")
    v.comprobar(abs(nacional - simple_h) > 1 and abs(por_personas - simple_p) > 1,
                "Las cifras ponderadas difieren de los promedios simples")
    v.informar(f"{nacional:.2f} frente a {por_personas:.2f}: mieperho cuenta a los "
               f"{int((miembros['p204'] == 1).sum()):,} miembros del hogar (p204 = 1) y los residentes habituales son "
               f"{antes:,}: son dos poblaciones distintas.")
    return v


def indicadores(h, p):
    """La tabla que consultan el agente y el informe. Cada corte indica de qué base sale."""
    cortes = (("Perú", None, h, "hogares"), ("Área", "area", h, "hogares"), ("Dominio", "dominio", h, "hogares"),
              ("Departamento", "departamento", h, "hogares"), ("Perú", None, p, "personas"),
              ("Área", "area", p, "personas"), ("Sexo", "sexo", p, "personas"),
              ("Grupo de edad", "grupo_edad", p, "personas"))
    filas = []
    for y, nombre in INDICADORES.items():
        for grupo, por, base, unidad in cortes:
            filas.append(tabla(base, por, y).assign(indicador=nombre, grupo=grupo, base=unidad))
    t = pd.concat(filas, ignore_index=True)
    t = t[["indicador", "grupo", "base", *[c for c in t if c not in ("indicador", "grupo", "base")]]]
    return t.round({"pct": 2, "ee": 3, "ic95_inf": 2, "ic95_sup": 2, "cv_pct": 2, "poblacion": 0})


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()[:16]


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--anio", type=int, default=ANIO)
    a.add_argument("--datos", type=Path, default=DATOS)
    a.add_argument("--salidas", type=Path, default=SALIDAS)
    args = a.parse_args()
    if args.anio != ANIO:
        raise SystemExit(f"Esta Skill solo cubre la ENAHO {ANIO} (código 966 del INEI): sus validaciones son de ese año "
                         f"y no hay cifras de referencia para {args.anio}.")
    args.salidas.mkdir(parents=True, exist_ok=True)
    bases = {u: args.salidas / f"{u}_{ANIO}.parquet" for u in ("personas", "hogares")}
    for base in bases.values():  # una corrida fallida no debe dejar una base anterior que parezca válida
        base.unlink(missing_ok=True)

    z34, z02 = bajar("34", args.datos), bajar("02", args.datos)
    sumaria, miembros = leer(z34, SUMARIA), leer(z02, MIEMBROS)
    cabecera = [f"Validación de la ENAHO {ANIO}. Generado por limpiar.py el {datetime.now():%Y-%m-%d %H:%M}.",
                f"Archivos: {z34.name} (sha256 {huella(z34)}), {z02.name} (sha256 {huella(z02)})."]
    informe = args.salidas / "validacion.txt"
    try:
        h, p = construir(sumaria, miembros)
    except pd.errors.MergeError as e:
        informe.write_text("\n".join([*cabecera, "", f"[FALLA] La unión m:1 no es válida: {e}", "", "RESULTADO: RECHAZADA", ""]),
                           encoding="utf-8")
        raise SystemExit(f"Validación esencial fallida: la unión de personas y hogares no es m:1 ({e}).")
    v = validar(sumaria, miembros, h, p)
    pie = ["", f"Aprobadas: {v.aprobadas}. Fallidas: {v.fallas}. Avisos: {v.avisos}.",
           f"RESULTADO: {'RECHAZADA' if v.fallas else 'APROBADA'}"]
    informe.write_text("\n".join([*cabecera, *v.lineas, *pie, ""]), encoding="utf-8")
    print("\n".join(v.lineas + pie))
    if v.fallas:
        raise SystemExit(f"Validaciones esenciales fallidas: {v.fallas}. No se guardó ninguna base. Revisa {informe}.")

    p = p.drop(columns=["_merge", "ubigeo_hogar", "estrato_hogar", "p203", "p204", "p205", "p206", "p207", "p208a"])
    h.to_parquet(bases["hogares"], index=False)
    p.to_parquet(bases["personas"], index=False)
    indicadores(h, p).to_csv(args.salidas / "indicadores.csv", index=False, encoding="utf-8")
    print(f"Guardados {bases['personas'].name} ({len(p):,} personas), {bases['hogares'].name} ({len(h):,} hogares) "
          "e indicadores.csv")


if __name__ == "__main__":
    main()
