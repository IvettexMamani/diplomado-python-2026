"""Limpia la ENAHO 2019-2025 y clasifica a cada trabajador según su nivel de empleo.

Lee el módulo 05 (empleo e ingresos, una fila por persona de 14 años a más) y el módulo 34
(sumaria, una fila por hogar) que deja `obtener_datos.py` en datos/originales/, y escribe
datos/procesados/pea_2019_2025.parquet: una fila por persona de la PEA (ocupada o desocupada).

Definición (la del INEI para los niveles de empleo):
  - Subempleo por horas: ocupado que trabaja menos de 35 horas a la semana, quiere trabajar
    más horas (p521 = 1) y está disponible para hacerlo (p521a = 1).
  - Subempleo por ingresos: ocupado que no está subempleado por horas y cuyo ingreso laboral
    mensual (monetario, de la ocupación principal y las secundarias) es menor al ingreso
    mínimo referencial (IMR).
  - IMR: costo de la canasta mínima de consumo familiar (línea de pobreza total × miembros del
    hogar) dividido entre el número promedio de perceptores (ocupados) por hogar. Se calcula
    por dominio geográfico y área (15 grupos), con los hogares ponderados por factor07.
  - Adecuadamente empleado: el resto de los ocupados.
  - PEA: ocupados más desocupados abiertos (ocu500 = 1 o 2), de 14 años a más.

Validación: con la ENAHO 2017 el script reproduce la PEA (17 215,7 mil) y los ocupados
(16 511,0 mil) del INEI, el subempleo por horas (460 mil frente a 462 mil) y el subempleo por
ingresos con 1,3 puntos menos (40,7 % frente a 42,0 % de la PEA). Ver validacion_2017.txt.

Uso:
    python scripts/procesar_datos.py            # desde tarea_3/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

RAIZ = Path(__file__).resolve().parents[1]
ORIGINALES = RAIZ / "datos" / "originales"
PROCESADOS = RAIZ / "datos" / "procesados"

VALIDACION = {2017: 603}   # año con cifras oficiales del INEI para comparar
CODIGOS = {2019: 687, 2020: 737, 2021: 759, 2022: 784, 2023: 906, 2024: 966, 2025: 1031}

LLAVES = ["conglome", "vivienda", "hogar"]
COLS_500 = LLAVES + [
    "codperso", "ubigeo", "dominio", "estrato", "p204", "p205", "p206", "p207", "p208a",
    "p301a", "ocu500", "fac500a", "p507", "p506r4", "p513t", "p518", "p519", "p520",
    "p521", "p521a",
    # ingreso laboral anual: dependiente e independiente, en dinero y en especie,
    # en la ocupación principal y en las secundarias, más los ingresos extraordinarios
    "i524a1", "d529t", "i530a", "d536", "i538a1", "d540t", "i541a", "d543", "d544t",
]
# Ingreso laboral monetario: dependiente (i524a1, i538a1) e independiente (i530a, i541a),
# de la ocupación principal y de las secundarias. Montos anuales: se dividen entre 12.
INGRESOS = ["i524a1", "i530a", "i538a1", "i541a"]
# Sensibilidad: solo la ocupación principal, o sumando pagos en especie y autoconsumo
INGRESOS_PRINCIPAL = ["i524a1", "i530a"]
INGRESOS_AMPLIO = INGRESOS + ["d529t", "d536", "d540t", "d543"]
COLS_SUMARIA = LLAVES + ["dominio", "estrato", "linea", "mieperho", "factor07"]

DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho",
    "06": "Cajamarca", "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco",
    "11": "Ica", "12": "Junín", "13": "La Libertad", "14": "Lambayeque", "15": "Lima",
    "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura",
    "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}
DOMINIOS = {1: "Costa norte", 2: "Costa centro", 3: "Costa sur", 4: "Sierra norte",
            5: "Sierra centro", 6: "Sierra sur", 7: "Selva", 8: "Lima Metropolitana"}


def leer_dta(ruta: Path, columnas: list[str]) -> pd.DataFrame:
    """Lee solo las columnas pedidas; los nombres cambian de mayúsculas entre años."""
    _, meta = pyreadstat.read_dta(str(ruta), metadataonly=True)
    reales = {c.lower(): c for c in meta.column_names}
    faltan = [c for c in columnas if c not in reales]
    usar = [reales[c] for c in columnas if c in reales]
    df, _ = pyreadstat.read_dta(str(ruta), usecols=usar, apply_value_formats=False)
    df.columns = [c.lower() for c in df.columns]
    for c in faltan:          # p506r4 no existe en algún año: queda vacía
        df[c] = np.nan
    return df


def texto(serie: pd.Series, ancho: int) -> pd.Series:
    """Llaves como texto con ceros a la izquierda (015009, 010101)."""
    return serie.astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(ancho)


def sector(ciiu: pd.Series) -> pd.Series:
    """Agrupa la CIIU rev. 4 (4 dígitos) en 8 sectores; los 2 primeros dígitos son la división."""
    div = pd.to_numeric(texto(ciiu.fillna(-1).astype(int), 4).str[:2], errors="coerce")
    cortes = [(1, 3, "Agropecuario y pesca"), (5, 9, "Minería"), (10, 33, "Manufactura"),
              (41, 43, "Construcción"), (45, 47, "Comercio"), (49, 53, "Transporte"),
              (55, 56, "Restaurantes y hoteles"), (35, 99, "Otros servicios")]
    salida = pd.Series("Sin dato", index=ciiu.index)
    for ini, fin, nombre in reversed(cortes):
        salida[(div >= ini) & (div <= fin)] = nombre
    return salida


def educacion(p301a: pd.Series) -> pd.Series:
    mapa = {1: "Primaria o menos", 2: "Primaria o menos", 3: "Primaria o menos",
            4: "Primaria o menos", 12: "Primaria o menos", 5: "Secundaria", 6: "Secundaria",
            7: "Superior no universitaria", 8: "Superior no universitaria",
            9: "Universitaria", 10: "Universitaria", 11: "Universitaria"}
    return p301a.map(mapa).fillna("Sin dato")


def procesar(anio: int) -> tuple[pd.DataFrame, dict]:
    cod = {**VALIDACION, **CODIGOS}[anio]
    m5 = leer_dta(ORIGINALES / f"{cod}-Modulo05" / f"enaho01a-{anio}-500.dta", COLS_500)
    su = leer_dta(ORIGINALES / f"{cod}-Modulo34" / f"sumaria-{anio}.dta", COLS_SUMARIA)
    filas_leidas = len(m5)

    for c in LLAVES:
        m5[c] = texto(m5[c], {"conglome": 6, "vivienda": 3, "hogar": 2}[c])
        su[c] = texto(su[c], {"conglome": 6, "vivienda": 3, "hogar": 2}[c])
    m5["codperso"] = texto(m5["codperso"], 2)
    m5["ubigeo"] = texto(m5["ubigeo"], 6)

    duplicados = int(m5.duplicated(LLAVES + ["codperso"]).sum())
    m5 = m5.drop_duplicates(LLAVES + ["codperso"])

    # Residentes habituales (criterio del INEI) de 14 años a más
    residente = ((m5.p204 == 1) & (m5.p205 == 2)) | ((m5.p204 == 2) & (m5.p206 == 1))
    m5 = m5[residente & (m5.p208a >= 14)].copy()
    filas_residentes = len(m5)

    # PEA: ocupados (1) y desocupados abiertos (2); sin factor no se puede expandir
    m5 = m5[m5.ocu500.isin([1, 2]) & m5.fac500a.notna() & (m5.fac500a > 0)].copy()
    ocupado = m5.ocu500 == 1

    # IMR por dominio y área: canasta media del hogar / ocupados medios por hogar,
    # sobre todos los hogares de la sumaria ponderados por factor07
    n_ocup = m5[ocupado].groupby(LLAVES).size().rename("n_ocup")
    su = su.merge(n_ocup, on=LLAVES, how="left", validate="1:1")
    su["n_ocup"] = su.n_ocup.fillna(0)
    su["canasta"] = su.linea * su.mieperho
    su["urbano"] = su.estrato <= 5
    g = su[su.factor07 > 0].groupby(["dominio", "urbano"])
    imr = (g.apply(lambda d: np.average(d.canasta, weights=d.factor07), include_groups=False)
           / g.apply(lambda d: np.average(d.n_ocup, weights=d.factor07), include_groups=False))
    imr = imr.rename("imr").reset_index()

    sin_sumaria = int((~m5.set_index(LLAVES).index.isin(su.set_index(LLAVES).index)).sum())
    m5["urbano"] = m5.estrato <= 5
    m5 = m5.merge(imr, on=["dominio", "urbano"], how="left", validate="m:1")
    ocupado = m5.ocu500 == 1

    ingresos = {}
    for nombre, cols in [("base", INGRESOS), ("principal", INGRESOS_PRINCIPAL),
                         ("amplio", INGRESOS_AMPLIO)]:
        ingresos[nombre] = m5[cols].fillna(0).sum(axis=1) / 12
    m5["ingreso_mensual"] = ingresos["base"]
    # Horas: las de la semana pasada (principal + secundarias); si no fue una semana
    # normal (p519 = 2), las que trabaja normalmente (p520)
    horas_semana = m5.p513t.fillna(0) + m5.p518.fillna(0)
    m5["horas"] = np.where((m5.p519 == 2) & m5.p520.notna(), m5.p520, horas_semana)

    m5["ocupado"] = ocupado
    m5["sub_horas"] = ocupado & (m5.horas < 35) & (m5.p521 == 1) & (m5.p521a == 1)
    no_horas = ocupado & ~m5.sub_horas
    m5["sub_ingresos"] = no_horas & (ingresos["base"] < m5.imr)
    m5["adecuado"] = no_horas & ~m5.sub_ingresos
    m5["sub_ingresos_principal"] = no_horas & (ingresos["principal"] < m5.imr)
    m5["sub_ingresos_amplio"] = no_horas & (ingresos["amplio"] < m5.imr)

    salida = pd.DataFrame({
        "anio": anio,
        "conglome": m5.conglome, "vivienda": m5.vivienda, "hogar": m5.hogar,
        "codperso": m5.codperso, "ubigeo": m5.ubigeo,
        "departamento": m5.ubigeo.str[:2],
        "nombre_departamento": m5.ubigeo.str[:2].map(DEPARTAMENTOS),
        "dominio": m5.dominio.map(DOMINIOS),
        "area": np.where(m5.urbano, "Urbana", "Rural"),
        "sexo": m5.p207.map({1: "Hombre", 2: "Mujer"}),
        "edad": m5.p208a.astype(int),
        "grupo_edad": pd.cut(m5.p208a, [13, 24, 44, 64, 200],
                             labels=["14-24", "25-44", "45-64", "65+"]).astype(str),
        "educacion": educacion(m5.p301a),
        "sector": sector(m5.p506r4),
        "ocupado": m5.ocupado, "horas": m5.horas.round(1),
        "ingreso_mensual": m5.ingreso_mensual.round(2), "imr": m5.imr.round(2),
        "sub_horas": m5.sub_horas, "sub_ingresos": m5.sub_ingresos,
        "adecuado": m5.adecuado, "sub_ingresos_principal": m5.sub_ingresos_principal,
        "sub_ingresos_amplio": m5.sub_ingresos_amplio,
        "fac500a": m5.fac500a,
    })
    salida.loc[~salida.ocupado, "sector"] = "Desocupado"

    control = {
        "anio": anio, "filas_modulo05": filas_leidas, "duplicados": duplicados,
        "residentes_14_mas": filas_residentes, "pea": len(salida),
        "ocupados": int(salida.ocupado.sum()), "sin_sumaria": sin_sumaria,
        "departamentos": salida.departamento.nunique(),
        "imr_lima_metropolitana": float(imr.loc[imr.dominio == 8, "imr"].iloc[0]),
    }
    return salida, control


# Cifras oficiales del INEI con la ENAHO 2017 (miles de personas y % de la PEA), de
# «Perú: Evolución de los indicadores de empleo e ingresos por departamento, 2007-2017»,
# cuadros 3.1 y 3.2: https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1537/cap03.pdf
OFICIAL_2017 = {"pea": 17215.7, "ocupados": 16511.0, "adecuado": 8815.9, "sub_horas": 461.7,
                "sub_ingresos": 7233.4, "tasa_sub_ingresos": 42.0,
                "tasa_sub_ingresos_urbana": 33.0, "tasa_sub_ingresos_rural": 73.6}


def validar() -> bool:
    """Compara la ENAHO 2017 procesada con las cifras publicadas por el INEI."""
    df, _ = procesar(2017)
    w = df.fac500a

    def miles(m):
        return w[m].sum() / 1e3

    def tasa(m, filtro=None):
        f = filtro if filtro is not None else pd.Series(True, index=df.index)
        return w[m & f].sum() / w[f].sum() * 100

    urb = df.area == "Urbana"
    propio = {"pea": miles(df.index == df.index), "ocupados": miles(df.ocupado),
              "adecuado": miles(df.adecuado), "sub_horas": miles(df.sub_horas),
              "sub_ingresos": miles(df.sub_ingresos), "tasa_sub_ingresos": tasa(df.sub_ingresos),
              "tasa_sub_ingresos_urbana": tasa(df.sub_ingresos, urb),
              "tasa_sub_ingresos_rural": tasa(df.sub_ingresos, ~urb)}
    lineas = ["Validación con la ENAHO 2017 (cifras oficiales del INEI, Lib1537 cap. 3)",
              f"{'indicador':28s} {'INEI':>10s} {'este script':>12s} {'diferencia':>11s}"]
    ok = True
    for k, oficial in OFICIAL_2017.items():
        dif = propio[k] - oficial
        rel = dif / oficial * 100
        # tolerancia: 0,5 % en PEA y ocupados; 5 % en los niveles de empleo
        tol = 0.5 if k in ("pea", "ocupados") else 6.0
        estado = "OK" if abs(rel) <= tol else "REVISAR"
        ok &= estado == "OK"
        lineas.append(f"{k:28s} {oficial:10.1f} {propio[k]:12.1f} {dif:+10.1f}  {estado}")
    lineas.append("RESULTADO: " + ("OK" if ok else "REVISAR"))
    texto_ = "\n".join(lineas)
    (PROCESADOS / "validacion_2017.txt").write_text(texto_ + "\n", encoding="utf-8")
    print(texto_)
    return ok


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    PROCESADOS.mkdir(parents=True, exist_ok=True)
    if not validar():
        print("La validación con 2017 no cuadra: revisar antes de usar la base.")
        return 1
    partes, controles = [], []
    for anio in CODIGOS:
        df, ctl = procesar(anio)
        partes.append(df)
        controles.append(ctl)
        assert ctl["departamentos"] == 25, f"{anio}: faltan departamentos"
        assert ctl["sin_sumaria"] == 0, f"{anio}: personas sin hogar en la sumaria"
        print(f"{anio}: {ctl['pea']:,} personas de la PEA ({ctl['ocupados']:,} ocupadas); "
              f"IMR Lima Metropolitana S/ {ctl['imr_lima_metropolitana']:,.0f}")
    base = pd.concat(partes, ignore_index=True)
    base.to_parquet(PROCESADOS / "pea_2019_2025.parquet", index=False)
    pd.DataFrame(controles).to_csv(PROCESADOS / "control_limpieza.csv", index=False)
    print(f"Listo: datos/procesados/pea_2019_2025.parquet ({len(base):,} filas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
