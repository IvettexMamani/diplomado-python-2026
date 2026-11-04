"""Servidor MCP del BCRP · Tarea 4, Parte 1. Adaptado del proyecto de la Sesión 04 (d2cml-ai/Data-Science-Python).

    uv run pytest -q          # 10 pruebas: las 8 originales de la Sesión 04 y 2 de la herramienta propia
    uv run mcp/server.py      # el servidor, por stdio (Claude Code lo lanza solo gracias a .mcp.json)

Herramientas: buscar_series, serie, resumen y correlacion (la propia). Recurso: bcrp://serie/{codigo}.
Prompt: informe. Las cuentas las hace Python, no el modelo: así cada cifra sale de una llamada que se puede repetir.
"""
import math
import re
import ssl
import time
import unicodedata
from datetime import date
from functools import cache
from pathlib import Path

import httpx
import pandas as pd
import truststore
from fastmcp import FastMCP
from fastmcp.exceptions import ResourceError, ToolError

AQUI = Path(__file__).parent
CATALOGO = AQUI.parent / "datos" / "bcrp" / "catalogo_bcrp.csv"
URL_CATALOGO = "https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata"
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
WEB = "https://estadisticas.bcrp.gob.pe/estadisticas/series"
SOLO_LECTURA = {"readOnlyHint": True, "openWorldHint": True}
TLS = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)  # certificados del sistema: sirve detrás de antivirus o proxies
MAX_PUNTOS = 3000   # más que esto no cabe bien en el contexto del modelo: para eso están resumen y correlacion

# Frecuencias del catálogo y su código de pandas, de la más fina a la más gruesa
FRECUENCIAS = {"Diaria": "D", "Mensual": "M", "Trimestral": "Q", "Anual": "Y"}
NOMBRE_FRECUENCIA = {v: k for k, v in FRECUENCIAS.items()}
ORDEN = {"D": 0, "M": 1, "Q": 2, "Y": 3}
CARPETA_WEB = {"D": "diarias", "M": "mensuales", "Q": "trimestrales", "Y": "anuales"}
MESES = {m: i for i, m in enumerate(
    ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "set", "oct", "nov", "dic"], start=1)} | {"sep": 9}

mcp = FastMCP("bcrp", instructions=(
    "Series oficiales del Banco Central de Reserva del Perú (BCRP). Primero busca el código con buscar_series; "
    "luego usa resumen para variaciones, promedios y extremos, serie para los datos y correlacion para ver si dos "
    "indicadores se mueven juntos. La ficha de cada serie está en el recurso bcrp://serie/{codigo}. No calcules a "
    "mano: cita siempre el código de la serie, el periodo y la fuente (fuente_web), y no presentes una correlación "
    "como si fuera una relación causal."))


def _sin_tildes(s):
    return unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode()


# ------------------------------------------------------------------------------------------------- catálogo
@cache
def catalogo():
    """El catálogo oficial: 17 mil series en unos 7 MB. Se baja una vez y queda en datos/bcrp/ (git lo ignora)."""
    if not CATALOGO.exists():
        CATALOGO.parent.mkdir(parents=True, exist_ok=True)
        r = httpx.get(URL_CATALOGO, timeout=120, verify=TLS)
        r.raise_for_status()
        CATALOGO.write_text(r.content.decode("latin-1"), encoding="utf-8")
    df = pd.read_csv(CATALOGO, sep=";", dtype=str).fillna("")
    df = df.rename(columns={"Código de serie": "codigo", "Categoría de serie": "categoria", "Grupo de serie": "grupo",
                            "Nombre de serie": "nombre", "Frecuencia": "frecuencia",
                            "Fecha de actualización": "actualizada", "Fecha de inicio": "inicio",
                            "Fuente": "fuente_original", "Grupo de publicación": "publicacion",
                            "Área que publica": "area", "Descripción de la serie": "descripcion",
                            "Metodología de la serie": "metodologia"})
    df["texto"] = (df.categoria + " " + df.grupo + " " + df.nombre).map(_sin_tildes)
    return df


def _fila(codigo):
    codigo = str(codigo).strip().upper()
    fila = catalogo().query("codigo == @codigo")
    if fila.empty:
        raise ToolError(f"No existe el código de serie {codigo!r}. Búsquenlo con buscar_series.")
    return fila.iloc[0]


def _ficha(codigo):
    f = _fila(codigo)
    return {"codigo": f.codigo, "nombre": f"{f.grupo} - {f.nombre}", "categoria": f.categoria,
            "frecuencia": f.frecuencia, "inicio": f.inicio, "actualizada": f.actualizada,
            "fuente_original": f.fuente_original}


@mcp.tool(annotations=SOLO_LECTURA)
def buscar_series(texto: str, frecuencia: str | None = None, limite: int = 10) -> list[dict]:
    """Busca series del BCRP por palabras: todas deben aparecer en la categoría, el grupo o el nombre.

    Ejemplos: "ipc 12 meses", "tipo de cambio interbancario venta", "reservas internacionales netas",
    "tasa de referencia", "cobre precio". frecuencia: "Diaria", "Mensual", "Trimestral" o "Anual".
    Devuelve el código, el nombre completo, la frecuencia y desde cuándo hay datos. Si no hay resultados,
    prueben con menos palabras. También acepta un código, por ejemplo "PN01273PM".
    """
    df = catalogo()
    if re.fullmatch(r"[A-Za-z]{2}\d{5}[A-Za-z]{2}", texto.strip()) and texto.strip().upper() in set(df.codigo):
        return [_ficha(texto)]
    m = pd.Series(True, index=df.index)
    for palabra in _sin_tildes(texto).split():
        m &= df.texto.str.contains(re.escape(palabra))
    if frecuencia:
        m &= df.frecuencia.str.lower() == frecuencia.lower()
    # primero las series vigentes y, entre ellas, las de nombre más corto (las más generales)
    sel = df[m]
    orden = sel.assign(vieja=sel.actualizada < "2025", largo=(sel.grupo + sel.nombre).str.len())
    return [_ficha(c) for c in orden.sort_values(["vieja", "largo"]).head(limite).codigo]


# --------------------------------------------------------------------------------------- fechas y periodos
def _anio(texto):
    """Años de 4 cifras, o de 2 como los que devuelve la API en las series diarias y trimestrales ("26" → 2026)."""
    a = int(texto)
    if len(texto) == 2:
        a += 2000
        if a > pd.Timestamp.today().year + 1:
            a -= 100
    return a


def _periodo_api(nombre, f):
    """Lee un periodo como lo escribe la API: "Ene.2025", "01.Oct.26", "T1.25" o "2025". Setiembre viene "Set" o "Sep"."""
    n = nombre.strip()
    if f == "D" and (m := re.fullmatch(r"(\d{1,2})\.([A-Za-z]{3})\.(\d{2}|\d{4})", n)):
        return pd.Period(year=_anio(m[3]), month=MESES[m[2].lower()], day=int(m[1]), freq="D")
    if f == "M" and (m := re.fullmatch(r"([A-Za-z]{3})\.(\d{2}|\d{4})", n)):
        return pd.Period(year=_anio(m[2]), month=MESES[m[1].lower()], freq="M")
    if f == "Q" and (m := re.fullmatch(r"T([1-4])\.(\d{2}|\d{4})", n)):
        return pd.Period(year=_anio(m[2]), quarter=int(m[1]), freq="Q")
    if f == "Y" and re.fullmatch(r"\d{4}", n):
        return pd.Period(year=int(n), freq="Y")
    raise ValueError(f"periodo de la API que no reconozco: {nombre!r} (frecuencia {f})")


def _frec(p):
    return p.freqstr[0]   # "D", "M", "Q-DEC" → "Q", "Y-DEC" → "Y"


def _texto(p):
    """Un periodo como lo devuelve este servidor: "2026-10-01", "2025-01", "2025-T1" o "2025"."""
    return {"D": lambda: p.strftime("%Y-%m-%d"), "M": lambda: f"{p.year}-{p.month:02d}",
            "Q": lambda: f"{p.year}-T{p.quarter}", "Y": lambda: f"{p.year}"}[_frec(p)]()


def _texto_api(p):
    """Un periodo como lo pide la API: 2025-01-15 (diaria), 2025-1 (mensual, y trimestre 1 en las trimestrales), 2025."""
    return {"D": lambda: p.strftime("%Y-%m-%d"), "M": lambda: f"{p.year}-{p.month}",
            "Q": lambda: f"{p.year}-{p.quarter}", "Y": lambda: f"{p.year}"}[_frec(p)]()


def _instante(texto, inicio):
    """Convierte "2025", "2025-T1", "2025-03" o "2025-03-15" en el primer (inicio=True) o el último instante de ese
    periodo. Así "2025" sirve igual para una serie diaria, mensual, trimestral o anual. Sin texto: hoy."""
    if texto is None or str(texto).strip() == "":
        return pd.Timestamp.today()
    t = str(texto).strip().upper().replace("/", "-").replace(".", "-")
    try:
        if m := re.fullmatch(r"(\d{4})", t):
            p = pd.Period(year=int(m[1]), freq="Y")
        elif (m := re.fullmatch(r"(\d{4})-?[TQ]([1-4])", t)) or (m := re.fullmatch(r"[TQ]([1-4])-(\d{4})", t)):
            anio, trim = (m[1], m[2]) if len(m[1]) == 4 else (m[2], m[1])
            p = pd.Period(year=int(anio), quarter=int(trim), freq="Q")
        elif m := re.fullmatch(r"(\d{4})-(\d{1,2})", t):
            date(int(m[1]), int(m[2]), 1)             # pandas acepta el mes 13 y lo pasa al año siguiente: aquí no
            p = pd.Period(year=int(m[1]), month=int(m[2]), freq="M")
        elif m := re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", t):
            date(int(m[1]), int(m[2]), int(m[3]))
            p = pd.Period(year=int(m[1]), month=int(m[2]), day=int(m[3]), freq="D")
        else:
            raise ValueError
    except ValueError:
        raise ToolError(f"No entiendo la fecha {texto!r}. Usen 2025 (año), 2025-T1 (trimestre), 2025-03 (mes) "
                        "o 2025-03-15 (día).") from None
    return p.start_time if inicio else p.end_time


# ------------------------------------------------------------------------------------------------ descarga
@cache
def _bajar(url):
    """Pide una URL de la API y la guarda en caché. Si el BCRP responde una página HTML en vez de JSON (lo hace
    cuando recibe muchos pedidos seguidos), espera y reintenta: 2, 4, 8 y 16 segundos."""
    espera = 2
    for intento in range(5):
        try:
            return httpx.get(url, timeout=60, verify=TLS, follow_redirects=True).json()
        except (ValueError, httpx.TransportError):
            if intento < 4:
                time.sleep(espera)
                espera *= 2
    raise ToolError(f"El BCRP no respondió con datos en {url}. Esperen unos segundos y reintenten.")


def _datos(codigo, inicio, fin):
    """Los datos de una serie entre dos instantes, como pd.Series con índice de periodos, más sus fuentes."""
    ficha = _ficha(codigo)
    f = FRECUENCIAS.get(ficha["frecuencia"])
    if f is None:
        raise ToolError(f"La serie {ficha['codigo']} tiene una frecuencia que no manejo: {ficha['frecuencia']!r}.")
    p0, p1 = pd.Period(inicio, freq=f), pd.Period(fin, freq=f)
    if p0 > p1:
        raise ToolError(f"El periodo está al revés: desde ({_texto(p0)}) es posterior a hasta ({_texto(p1)}).")
    valores = {}
    for per in _bajar(f"{API}/{ficha['codigo']}/json/{_texto_api(p0)}/{_texto_api(p1)}").get("periods", []):
        try:
            x = float(per["values"][0])          # "n.d." y vacíos no son números: se saltan
        except (IndexError, KeyError, TypeError, ValueError):
            continue
        if not math.isnan(x):
            valores[_periodo_api(per["name"], f)] = x
    s = pd.Series(list(valores.values()), index=pd.PeriodIndex(list(valores), freq=f), dtype=float).sort_index()
    s = s[(s.index >= p0) & (s.index <= p1)]
    if s.empty:
        raise ToolError(f"La serie {ficha['codigo']} no tiene datos entre {_texto(p0)} y {_texto(p1)}. "
                        f"Hay datos desde {ficha['inicio']} y se actualizó el {ficha['actualizada']}.")
    # Las fuentes citan el rango de los datos devueltos, no el pedido: abiertas después, muestran las mismas cifras
    rango = f"{_texto_api(s.index[0])}/{_texto_api(s.index[-1])}"
    url = f"{API}/{ficha['codigo']}/json/{rango}"
    web = f"{WEB}/{CARPETA_WEB[f]}/resultados/{ficha['codigo']}/html/{rango}/"
    return ficha, s, url, web


def _r(x, cifras=4):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), cifras)


def _punto(s, p):
    return {"periodo": _texto(p), "valor": _r(s[p], 6)}


def _cabecera(ficha, s, url, web):
    return {"codigo": ficha["codigo"], "nombre": ficha["nombre"], "frecuencia": ficha["frecuencia"],
            "periodo": {"desde": _texto(s.index[0]), "hasta": _texto(s.index[-1])}, "n": len(s),
            "fuente": url, "fuente_web": web, "fuente_original": ficha["fuente_original"] or "BCRP"}


# ------------------------------------------------------------------------------------------------- serie
@mcp.tool(annotations=SOLO_LECTURA)
def serie(codigo: str, desde: str, hasta: str | None = None) -> dict:
    """Descarga los datos de una serie del BCRP entre dos fechas, ambas incluidas.

    codigo: el que da buscar_series, por ejemplo "PN01273PM". desde y hasta: "2025" (año), "2025-T1" (trimestre),
    "2025-03" (mes) o "2025-03-15" (día); se adaptan a la frecuencia de la serie, así que "2025" en una serie
    mensual va de 2025-01 a 2025-12. Sin hasta, llega hasta el último dato publicado.
    Devuelve "datos" como [{"periodo", "valor"}] con periodos "2025-01" (mensual), "2026-10-01" (diaria),
    "2025-T1" (trimestral) o "2025" (anual), sin los valores "n.d.". "fuente" es la URL de la API y "fuente_web" la
    tabla en la web del BCRP para comprobar la cifra. Para variaciones, promedios o extremos usen resumen.
    """
    ficha, s, url, web = _datos(codigo, _instante(desde, True), _instante(hasta, False))
    if len(s) > MAX_PUNTOS:
        raise ToolError(f"La serie {ficha['codigo']} tiene {len(s)} datos en ese periodo. Acórtenlo o usen resumen "
                        "o correlacion, que calculan sin devolver todos los datos.")
    return _cabecera(ficha, s, url, web) | {"datos": [_punto(s, p) for p in s.index]}


# ----------------------------------------------------------------------------------------------- resumen
@mcp.tool(annotations=SOLO_LECTURA)
def resumen(codigo: str, desde: str, hasta: str | None = None) -> dict:
    """Resume una serie del BCRP en un periodo: primer y último dato, cambio, variación %, promedio, desviación
    estándar, máximo y mínimo (cada extremo con su periodo).

    Úsenla siempre que haya que decir cuánto subió o bajó un indicador, cuál fue su promedio o cuándo tocó su pico:
    el modelo no debe hacer esas cuentas a mano. Mismos argumentos que serie, por ejemplo
    codigo="PN01273PM", desde="2025-12", hasta="2026-09". cambio = último − primero (en la unidad de la serie);
    variacion_pct = cambio / |primero| × 100. Si la serie ya es una tasa en %, el dato a reportar es cambio, en
    puntos porcentuales.
    """
    ficha, s, url, web = _datos(codigo, _instante(desde, True), _instante(hasta, False))
    primero, ultimo = s.iloc[0], s.iloc[-1]
    r = _cabecera(ficha, s, url, web) | {
        "primero": _punto(s, s.index[0]), "ultimo": _punto(s, s.index[-1]),
        "cambio": _r(ultimo - primero),
        "variacion_pct": _r((ultimo - primero) / abs(primero) * 100) if primero else None,
        "promedio": _r(s.mean()), "desviacion_estandar": _r(s.std()) if len(s) > 1 else None,
        "maximo": _punto(s, s.idxmax()), "minimo": _punto(s, s.idxmin())}
    if re.search(r"%|var\b|variaci|tasa", _sin_tildes(ficha["nombre"])):
        r["nota"] = ("La serie ya es una tasa o variación en %: «cambio» está en puntos porcentuales y «variacion_pct» "
                     "es el cambio relativo de esa tasa, que casi nunca es lo que se quiere reportar.")
    return r


# ------------------------------------------------------------------------------- herramienta propia: correlacion
def _fisher(r, n):
    """Intervalo de confianza al 95 % y p-valor aproximados con la transformación z de Fisher."""
    if n <= 3:
        return None, None
    if abs(r) >= 1 - 1e-12:
        return [_r(r), _r(r)], 0.0
    z, se = math.atanh(r), 1 / math.sqrt(n - 3)
    return [_r(math.tanh(z - 1.96 * se)), _r(math.tanh(z + 1.96 * se))], _r(math.erfc(abs(z) / se / math.sqrt(2)), 6)


def _fuerza(r):
    a = abs(r)
    nivel = "prácticamente nula" if a < 0.1 else "débil" if a < 0.3 else "moderada" if a < 0.7 else "fuerte"
    return nivel if a < 0.1 else f"{nivel} {'positiva' if r > 0 else 'negativa'}"


@mcp.tool(annotations=SOLO_LECTURA)
def correlacion(codigo_a: str, codigo_b: str, desde: str, hasta: str | None = None, rezago: int = 0) -> dict:
    """Correlación entre dos series del BCRP, calculada en Python con los periodos alineados.

    Úsenla para preguntas como «¿se mueven juntos el tipo de cambio y la inflación?» o «¿el precio del cobre se
    anticipa al PBI?». Por ejemplo: codigo_a="PN01273PM", codigo_b="PD04638PD", desde="2023-01", hasta="2025-12".
    Qué hace, en orden:
    1. Si las frecuencias difieren, lleva la más fina a la más gruesa con el promedio de cada periodo
       (diaria → mensual, mensual → trimestral...). Los periodos se devuelven en esa frecuencia común.
    2. Empareja periodo con periodo y descarta los que no tienen dato en alguna de las dos ("n.d." o sin
       publicar), y dice cuántos descartó de cada serie.
    3. rezago=k compara A en t con B en t−k, en periodos de la frecuencia común: con k > 0 se pregunta si B se
       anticipa a A. Baja B desde k periodos antes para no perder pares. Va de −36 a 36.
    Devuelve n, Pearson con su intervalo de confianza al 95 % y su p-valor aproximados (Fisher), Spearman (por
    rangos, menos sensible a valores extremos), la correlación de las variaciones periodo a periodo (si la de los
    niveles es alta pero esta no, puede ser solo que ambas series tienen tendencia), advertencias, la fuente de
    cada serie y, si hay 120 pares o menos, los datos emparejados. Una correlación describe una asociación: no
    prueba causalidad, y en series de tiempo el p-valor suele ser optimista.
    """
    if abs(rezago) > 36:
        raise ToolError("El rezago debe estar entre −36 y 36 periodos.")
    fichas = {"a": _ficha(codigo_a), "b": _ficha(codigo_b)}
    frec = {k: FRECUENCIAS.get(v["frecuencia"]) for k, v in fichas.items()}
    if None in frec.values():
        raise ToolError("Una de las series tiene una frecuencia que no manejo.")
    comun = max(frec.values(), key=ORDEN.get)
    p0 = pd.Period(_instante(desde, True), freq=comun)
    p1 = pd.Period(_instante(hasta, False), freq=comun)
    if p0 > p1:
        raise ToolError(f"El periodo está al revés: desde ({_texto(p0)}) es posterior a hasta ({_texto(p1)}).")

    # A en [p0, p1]; B en [p0 − k, p1 − k], para que con rezago también haya un par por periodo
    _, sa, url_a, web_a = _datos(codigo_a, p0.start_time, p1.end_time)
    _, sb, url_b, web_b = _datos(codigo_b, (p0 - rezago).start_time, (p1 - rezago).end_time)
    a = sa.groupby(sa.index.asfreq(comun)).mean()
    b = sb.groupby(sb.index.asfreq(comun)).mean()
    b.index = b.index + rezago                      # el valor de B en t−k queda rotulado en t
    indice = pd.period_range(p0, p1, freq=comun)
    tabla = pd.DataFrame({"a": a.reindex(indice), "b": b.reindex(indice)})
    pares = tabla.dropna()
    n = len(pares)
    if n < 4:
        raise ToolError(f"Solo hay {n} periodos con dato en las dos series entre {_texto(p0)} y {_texto(p1)}; "
                        "hacen falta al menos 4. Amplíen el periodo.")
    if pares.a.std() == 0 or pares.b.std() == 0:
        raise ToolError("Una de las series no cambia en el periodo: la correlación no está definida.")

    r = float(pares.a.corr(pares.b))
    rho = float(pares.a.rank().corr(pares.b.rank()))
    intervalo, p_valor = _fisher(r, n)
    variaciones = tabla.diff().dropna()             # solo periodos consecutivos con dato en ambas
    r_var = float(variaciones.a.corr(variaciones.b)) if len(variaciones) >= 4 else None

    descartados = {"sin_dato_en_a": int((tabla.a.isna() & tabla.b.notna()).sum()),
                   "sin_dato_en_b": int((tabla.b.isna() & tabla.a.notna()).sum())}
    advertencias = []
    for k, s in (("a", sa), ("b", sb)):
        if frec[k] != comun:
            advertencias.append(f"La serie {fichas[k]['codigo']} es {fichas[k]['frecuencia'].lower()}: se usó el "
                                f"promedio de cada periodo {NOMBRE_FRECUENCIA[comun].lower()} "
                                f"({len(s)} datos en {s.index.asfreq(comun).nunique()} periodos).")
    if sum(descartados.values()):
        advertencias.append(f"Se descartaron {sum(descartados.values())} periodos sin dato en una de las series.")
    if n < 12:
        advertencias.append(f"Con {n} pares la correlación es poco estable: tómenla como indicio.")
    if r_var is not None and abs(r) >= 0.5 and abs(r_var) < 0.3:
        advertencias.append("Los niveles están muy correlacionados pero sus variaciones no: puede ser que ambas series "
                            "solo compartan una tendencia (correlación espuria).")
    advertencias.append("Correlación no implica causalidad; el p-valor supone datos independientes y en series de "
                        "tiempo suele ser optimista.")

    def lado(ficha, url, web, s):
        return {"codigo": ficha["codigo"], "nombre": ficha["nombre"], "frecuencia": ficha["frecuencia"],
                "observaciones": len(s), "fuente": url, "fuente_web": web,
                "fuente_original": ficha["fuente_original"] or "BCRP"}

    resultado = {
        "serie_a": lado(fichas["a"], url_a, web_a, sa),
        "serie_b": lado(fichas["b"], url_b, web_b, sb) | {"rezago": rezago},
        "frecuencia_comun": NOMBRE_FRECUENCIA[comun],
        "periodo": {"desde": _texto(pares.index[0]), "hasta": _texto(pares.index[-1])},
        "n": n, "descartados": descartados,
        "pearson": _r(r), "intervalo_95": intervalo, "p_valor_aprox": p_valor, "spearman": _r(rho),
        "fuerza": _fuerza(r),
        "pearson_variaciones": _r(r_var), "n_variaciones": len(variaciones),
        "advertencias": advertencias,
    }
    if rezago:
        resultado["interpretacion_rezago"] = (f"Cada valor de {fichas['a']['codigo']} en t se compara con el de "
                                              f"{fichas['b']['codigo']} en t{-rezago:+d} ({NOMBRE_FRECUENCIA[comun].lower()}).")
    if n <= 120:
        resultado["datos"] = [{"periodo": _texto(p), "a": _r(fila.a, 6), "b": _r(fila.b, 6)}
                              for p, fila in pares.iterrows()]
    return resultado


# ------------------------------------------------------------------------------------------------- recurso
@mcp.resource("bcrp://serie/{codigo}", mime_type="application/json")
def ficha_serie(codigo: str) -> dict:
    """Ficha descriptiva de una serie del BCRP: nombre, categoría, frecuencia, fuente original, quién la publica,
    desde cuándo hay datos, cuándo se actualizó y los enlaces a la API y a su tabla en la web."""
    try:
        f = _fila(codigo)
    except ToolError as e:
        raise ResourceError(str(e)) from None
    frec = FRECUENCIAS.get(f.frecuencia)
    return {
        "codigo": f.codigo, "nombre": f"{f.grupo} - {f.nombre}", "categoria": f.categoria,
        "grupo_de_serie": f.grupo, "nombre_de_serie": f.nombre, "descripcion": f.descripcion or None,
        "metodologia": f.metodologia or None,
        "frecuencia": f.frecuencia, "datos_desde": f.inicio, "actualizada": f.actualizada,
        "fuente_original": f.fuente_original or "BCRP", "grupo_de_publicacion": f.publicacion, "area_que_publica": f.area,
        "tabla_web": f"{WEB}/{CARPETA_WEB[frec]}/resultados/{f.codigo}/html" if frec else None,
        "api": f"{API}/{f.codigo}/json/{{desde}}/{{hasta}}",
        "como_citar": f"Banco Central de Reserva del Perú, serie {f.codigo} «{f.grupo} - {f.nombre}» "
                      f"(fuente original: {f.fuente_original or 'BCRP'}). https://estadisticas.bcrp.gob.pe",
    }


# -------------------------------------------------------------------------------------------------- prompt
@mcp.prompt
def informe(tema: str, desde: str = "2024-01", hasta: str = "") -> str:
    """Informe breve sobre un tema macroeconómico del Perú con series oficiales del BCRP, en el que cada cifra lleva
    su código de serie, su periodo y su fuente. Ejemplos de tema: «inflación», «tipo de cambio y precios»,
    «actividad económica»."""
    hasta_txt = hasta or "el último dato publicado"
    return f"""Prepara un informe breve sobre «{tema}» en el Perú con series oficiales del BCRP, desde {desde} hasta {hasta_txt}.

1. Con buscar_series identifica de 2 a 4 series pertinentes. Si hay varias parecidas, elige las vigentes y di por qué
   (frecuencia, cobertura, quién la produce). Su ficha está en el recurso bcrp://serie/{{codigo}}.
2. Para cada serie llama a resumen en el periodo. Usa serie solo si necesitas ver la trayectoria.
3. Si el tema relaciona dos indicadores, usa correlacion (con rezago si tiene sentido económico) y repórtala como una
   asociación descriptiva, nunca como una causa. Menciona n y la correlación de las variaciones.
4. No hagas cuentas a mano: cada cifra del informe debe salir de una herramienta. Si una cifra no está, dilo.
5. Entrega, en español:
   - Contexto en un párrafo.
   - Una tabla con: indicador, código de serie, periodo, cifra y unidad.
   - Tres hallazgos, cada uno con su cifra, el código de la serie y el periodo.
   - Limitaciones (frecuencia, revisiones, lo que las series no dicen).
   - Fuentes: el enlace fuente_web de cada serie y «Banco Central de Reserva del Perú, Estadísticas», con la fecha
     de consulta.
"""


if __name__ == "__main__":
    mcp.run(show_banner=False)
