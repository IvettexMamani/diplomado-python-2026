# /// script
# requires-python = ">=3.10"
# dependencies = ["truststore"]
# ///
"""Descarga la ENAHO anual del portal de microdatos del INEI y la descomprime en datos/originales/.

Adaptado de la skill «descargando-enaho» (carpeta Skills ENAHO del curso): solo cambia la carpeta
de destino. Para esta tarea se bajan los módulos 05 (empleo e ingresos) y 34 (sumaria):

    uv run scripts/obtener_datos.py --anio 2025 --modulos 05 34 --raiz .
    # años usados: 2017 (validación) y 2019 a 2025

Queda así (código 1031 = 2025):
    datos/originales/1031-Modulo05/enaho01a-2025-500.dta
    datos/originales/1031-Modulo34/sumaria-2025.dta

La serie de la EPE de Lima Metropolitana no la baja este script: se descargó a mano de
https://www.gob.pe/institucion/inei/informes-publicaciones/3211214-series-de-empleo-lima-metropolitana
(archivo «Series de Empleo Lima Metropolitana», actualizado al trimestre jul-ago-set 2026) y
está en datos/originales/inei_epe_lima/series_empleo_lima_metropolitana.xlsx.

El código de cada año sale de CODIGOS (verificados) o, si no está, del portal del INEI.
Nunca prueba números en la URL: si el INEI no publica el año, lo dice y termina.
"""
from __future__ import annotations

import argparse
import http.cookiejar
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

try:  # usa los certificados del sistema (antivirus o proxy que inspeccionan HTTPS)
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

PORTAL = "https://proyectos.inei.gob.pe/microdatos"
DESCARGA = "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/{formato}/{codigo}-Modulo{modulo}.zip"
ENCUESTA = "Condiciones de Vida y Pobreza - ENAHO"   # ENAHO, metodología actualizada
METODOLOGIA = "2"
PERIODO_ANUAL = "55"                                  # «Anual - (Ene-Dic)» en el portal

# Códigos del INEI ya verificados (la URL de los módulos 34 y 02 responde 200).
CODIGOS = {2017: 603, 2019: 687, 2020: 737, 2021: 759, 2022: 784, 2023: 906, 2024: 966, 2025: 1031}

# Archivo principal de cada módulo, para avisar si no vino en el zip.
PRINCIPAL = {"34": "sumaria-{anio}.dta", "02": "enaho01-{anio}-200.dta"}
CABECERAS = {"User-Agent": "Mozilla/5.0 (descargando-enaho)"}


class NoPublicado(Exception):
    pass


def abridor():
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def consultar_codigo(anio: int) -> int:
    """Pide al portal la tabla de módulos del año (período anual) y lee el código."""
    op = abridor()

    def post(pagina: str, datos: dict) -> str:
        cuerpo = urllib.parse.urlencode({"bandera": "1", **datos}).encode()
        req = urllib.request.Request(f"{PORTAL}/{pagina}", data=cuerpo, headers=CABECERAS)
        with op.open(req, timeout=60) as r:
            return r.read().decode("latin-1")

    op.open(urllib.request.Request(f"{PORTAL}/Consulta_por_Encuesta.asp?CU=19558",
                                   headers=CABECERAS), timeout=60).read()
    anios = post("CambiaEnc.asp", {"_cmbEncuesta": ENCUESTA, "_cmbEncuesta0": METODOLOGIA})
    if f'value="{anio}"' not in anios:
        raise NoPublicado(f"el INEI no tiene la ENAHO {anio} en su portal")
    periodos = post("CambiaAnio.asp", {"_cmbEncuesta": ENCUESTA, "_cmbAnno": str(anio),
                                       "_cmbEncuesta0": METODOLOGIA})
    if f'value="{PERIODO_ANUAL}"' not in periodos:
        raise NoPublicado(f"el INEI todavía no publica la ENAHO anual de {anio} "
                          f"(solo hay trimestres)")
    tabla = post("cambiaPeriodo.asp", {"_cmbEncuesta": ENCUESTA, "_cmbAnno": str(anio),
                                       "_cmbTrimestre": PERIODO_ANUAL})
    codigos = set(re.findall(r"descarga/STATA/(\d+)-Modulo\d+\.zip", tabla))
    if len(codigos) != 1:
        raise RuntimeError(f"no pude leer el código de {anio} en el portal: {sorted(codigos)}")
    return int(codigos.pop())


def tamano_remoto(url: str) -> int | None:
    req = urllib.request.Request(url, method="HEAD", headers=CABECERAS)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return int(r.headers.get("Content-Length") or 0) or None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def bajar(url: str, destino: Path) -> None:
    esperado = tamano_remoto(url)
    if esperado is None:
        raise FileNotFoundError(f"el INEI no tiene {url}")
    if destino.exists() and destino.stat().st_size == esperado and zipfile.is_zipfile(destino):
        print(f"Ya estaba: {destino.name} ({esperado / 1e6:.1f} MB)")
        return
    parcial = destino.with_suffix(".zip.part")
    print(f"Bajando {destino.name} ({esperado / 1e6:.1f} MB)...", flush=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=CABECERAS), timeout=300) as r, \
            open(parcial, "wb") as f:
        shutil.copyfileobj(r, f, length=1 << 20)
    if parcial.stat().st_size != esperado or not zipfile.is_zipfile(parcial):
        parcial.unlink()
        raise RuntimeError(f"{destino.name} llegó incompleto o no es un zip; vuelve a correr")
    parcial.replace(destino)


def descomprimir(zip_: Path, carpeta: Path) -> list[Path]:
    """Extrae todo en datos/<código>-ModuloNN/, sin subcarpetas ni rutas del zip."""
    carpeta.mkdir(exist_ok=True)
    salida = []
    with zipfile.ZipFile(zip_) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            nombre = Path(info.filename.replace("\\", "/")).name
            destino = carpeta / nombre
            if not (destino.exists() and destino.stat().st_size == info.file_size):
                with zf.open(info) as src, open(destino, "wb") as dst:
                    shutil.copyfileobj(src, dst, length=1 << 20)
            salida.append(destino)
    return salida


def buscar_raiz(inicio: Path) -> Path:
    """El proyecto es la primera carpeta, desde aquí hacia arriba, con datos/ o .claude/."""
    for carpeta in [inicio, *inicio.parents]:
        if (carpeta / "datos").is_dir() or (carpeta / ".claude").is_dir():
            return carpeta
    return inicio


def main() -> int:
    for flujo in (sys.stdout, sys.stderr):    # tildes legibles en la consola de Windows
        flujo.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--modulos", nargs="+", default=["34", "02"], help="por defecto: 34 02")
    ap.add_argument("--formato", default="STATA", choices=["STATA", "SPSS", "CSV"])
    ap.add_argument("--raiz", type=Path, default=None, help="carpeta del proyecto")
    args = ap.parse_args()
    anio = args.anio
    modulos = [m.zfill(2) for m in args.modulos]
    raiz = (args.raiz or buscar_raiz(Path.cwd())).resolve()
    datos = raiz / "datos" / "originales"
    datos.mkdir(parents=True, exist_ok=True)

    try:
        if anio in CODIGOS:
            codigo = CODIGOS[anio]
            print(f"ENAHO {anio}: código {codigo} (tabla verificada)")
        else:
            codigo = consultar_codigo(anio)
            print(f"ENAHO {anio}: código {codigo} (consultado al portal del INEI)")
    except NoPublicado as e:
        print(f"NO PUBLICADO: {e}.")
        return 2

    listos = []
    for m in modulos:
        url = DESCARGA.format(formato=args.formato, codigo=codigo, modulo=m)
        zip_ = datos / f"{codigo}-Modulo{m}.zip"
        try:
            bajar(url, zip_)
        except FileNotFoundError as e:
            print(f"ERROR: {e}. Ese módulo no existe para {anio}.")
            return 1
        archivos = descomprimir(zip_, datos / f"{codigo}-Modulo{m}")
        principal = PRINCIPAL.get(m, "").format(anio=anio).lower()
        if args.formato == "STATA" and principal:
            hallado = [a for a in archivos if a.name.lower() == principal]
            if not hallado:
                dta = [a.name for a in archivos if a.suffix.lower() == ".dta"]
                print(f"AVISO: el zip {zip_.name} no trae {principal}; trae {dta}")
                listos.append(zip_.with_suffix(""))
            else:
                listos.append(hallado[0])
        else:
            listos.append(zip_.with_suffix(""))

    print()
    for ruta in listos:
        print(f"Listo: {ruta.relative_to(raiz).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
