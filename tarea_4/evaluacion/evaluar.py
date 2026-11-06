"""Compara a Claude Code sin y con los componentes del proyecto, con las mismas 10 preguntas y sesiones independientes.

    uv run evaluacion/evaluar.py --preparar             # crea los dos espacios de trabajo aislados
    uv run evaluacion/evaluar.py --modo A --minutos 8   # corre lo que falte de ese modo, hasta ese tiempo
    uv run evaluacion/evaluar.py --modo B --minutos 8
    uv run evaluacion/evaluar.py --resumir              # califica y escribe resultados.csv y comparacion.md

Modo A: una carpeta vacía fuera del repositorio, solo con búsqueda web. Sin archivos ni terminal, así no puede llegar a
las respuestas guardadas en el proyecto.
Modo B: lo mismo, más el servidor MCP, las Skills y lo que necesitan para correr (Read y Bash limitado a `uv run`), en una
copia del proyecto sin evaluacion/, informes/, evidencias_ia/ ni README.md, que contienen las respuestas.
En ambos, GitHub está bloqueado, porque el repositorio público tiene las respuestas.

Las reglas de calificación están aquí y se publicaron antes de la primera corrida. Cada corrida queda en
evidencias_ia/evaluacion/ y se salta si ya existe, así que una interrupción no obliga a repetir nada.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).parent.parent
sys.path.insert(0, str(RAIZ / "mcp"))
from demo_claude import _limpiar, legible  # noqa: E402

AQUI = Path(__file__).parent
EVIDENCIAS = RAIZ / "evidencias_ia" / "evaluacion"
TRABAJO = Path(os.environ.get("TEMP", "/tmp")) / "t4eval"
MODELO = "sonnet"
LIMITE = 420  # segundos por pregunta
INSTRUCCION = ("Responde con datos verificados. En «valores» pon los números que pide la pregunta, en el orden en que los "
               "pide y en la unidad indicada; usa null para el dato que no puedas obtener con tus herramientas: no estimes. "
               "En «texto» pon el nombre que pida la pregunta, si pide alguno. En «fuente» di de dónde sale cada cifra y su "
               "periodo. En «interpretacion», si la pregunta pide una conclusión, respóndela en una o dos frases.\n\n")
ESQUEMA = {"type": "object", "required": ["valores", "texto", "fuente", "interpretacion"],
           "properties": {"valores": {"type": "array", "items": {"type": ["number", "null"]}}, "texto": {"type": "string"},
                          "fuente": {"type": "string"}, "interpretacion": {"type": "string"}}}
RECURSOS = "ListMcpResourcesTool,ReadMcpResourceTool"
BLOQUEO = "WebFetch(domain:github.com),WebFetch(domain:raw.githubusercontent.com),WebFetch(domain:api.github.com)"
MODOS = {"A": ["--tools", "WebSearch,WebFetch", "--allowedTools", "WebSearch,WebFetch", "--disable-slash-commands"],
         "B": ["--tools", f"WebSearch,WebFetch,Skill,Read,Bash,{RECURSOS}", "--mcp-config", ".mcp.json",
               "--allowedTools", f"WebSearch,WebFetch,Skill,Read,Bash(uv run *),mcp__bcrp,{RECURSOS}"]}
# Si una herramienta toca alguno de estos textos, la corrida se marca: no debería poder pasar
PROHIBIDO = re.compile(r"diplomado-python-2026|evaluacion|informes/|informe_final|IvettexMamani", re.I)
NIEGA = re.compile(r"\bno\b[^.]{0,80}(prueba|permite|se puede|puede concluir|demuestra|basta|alcanza|suficiente|concluir)", re.I)
MOTIVO = re.compile(r"causal|causa\b|asociaci|correlaci|años? distint|distintos años|diferentes años|un solo|una sola|"
                    r"otros factores|factores|un dato|dos datos|una observaci|2022[^.]{0,60}2024", re.I)


def preparar():
    """Dos carpetas nuevas: A vacía; B con el código, los datos y las bases, sin nada que contenga las respuestas."""
    shutil.rmtree(TRABAJO, ignore_errors=True)
    a, b = TRABAJO / "A", TRABAJO / "B"
    a.mkdir(parents=True)
    (b / "mcp").mkdir(parents=True)
    (b / "salidas").mkdir()
    shutil.copytree(RAIZ / ".claude", b / ".claude", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(RAIZ / "datos", b / "datos")
    for nombre in (".mcp.json", "pyproject.toml", "uv.lock", "mcp/server.py"):
        shutil.copy(RAIZ / nombre, b / nombre)
    for nombre in ("personas_2024.parquet", "hogares_2024.parquet", "validacion.txt", "indicadores.csv"):
        shutil.copy(RAIZ / "salidas" / nombre, b / "salidas" / nombre)
    print(f"Listo: {a} (vacía) y {b} ({sum(1 for p in b.rglob('*') if p.is_file())} archivos)")


def correr(q, modo):
    prompt = INSTRUCCION + q.pregunta
    cmd = ["claude", "-p", prompt, "--model", MODELO, "--output-format", "stream-json", "--verbose",
           "--no-session-persistence", "--strict-mcp-config", "--json-schema", json.dumps(ESQUEMA, ensure_ascii=False),
           *MODOS[modo], "--disallowedTools", BLOQUEO]
    entorno = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    entorno |= {"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "UV_PROJECT_ENVIRONMENT": str(RAIZ / ".venv"), "PYTHONUTF8": "1"}
    t = time.time()
    error = ""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=LIMITE, cwd=TRABAJO / modo, env=entorno)
        salida, avisos = p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        salida = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        avisos, error = "", f"Superó el límite de {LIMITE} s"
    eventos = []
    for linea in salida.splitlines():
        if linea.strip().startswith("{"):
            try:
                eventos.append(json.loads(linea))
            except json.JSONDecodeError:
                pass
    final = next((e for e in reversed(eventos) if e.get("type") == "result"), {})
    if not eventos:
        error = error or f"Sin eventos: {avisos[-300:]}"
    llamadas = [c for e in eventos if e.get("type") == "assistant" for c in e.get("message", {}).get("content", [])
                if c.get("type") == "tool_use"]
    return {"id": q.id, "modo": modo, "respuesta": final.get("structured_output"), "texto_final": final.get("result", ""),
            "segundos": round(time.time() - t, 1), "turnos": final.get("num_turns"), "costo_usd": final.get("total_cost_usd"),
            "error": error or (final.get("result", "") if final.get("is_error") else ""),
            "herramientas": [c["name"] for c in llamadas],
            "skills": [c["input"].get("skill", "") for c in llamadas if c["name"] == "Skill"],
            "contaminacion": sorted({m.group(0) for c in llamadas for m in PROHIBIDO.finditer(json.dumps(c["input"], ensure_ascii=False))
                                     if c["name"] != "StructuredOutput"})}, cmd, eventos, prompt


def guardar(resumen, cmd, eventos, prompt):
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    nombre = f"{resumen['modo']}_{resumen['id']}"
    limpios = _limpiar(eventos)
    (EVIDENCIAS / f"{nombre}.jsonl").write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in limpios), encoding="utf-8")
    (EVIDENCIAS / f"{nombre}.md").write_text(legible(prompt, MODELO, cmd, limpios, resumen["segundos"]), encoding="utf-8")
    (EVIDENCIAS / f"{nombre}.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")


def lanzar(modo, minutos):
    preguntas = pd.read_csv(AQUI / "preguntas.csv", keep_default_na=False)
    inicio = time.time()
    for q in preguntas.itertuples():
        if (EVIDENCIAS / f"{modo}_{q.id}.json").exists():
            continue
        if time.time() - inicio > minutos * 60:
            print("Se acabó el tiempo de esta tanda; vuelve a correr el comando para seguir.")
            return
        resumen, cmd, eventos, prompt = correr(q, modo)
        guardar(resumen, cmd, eventos, prompt)
        r = resumen["respuesta"] or {}
        print(f"{modo} {q.id}: {resumen['segundos']} s, {len(resumen['herramientas'])} llamadas, valores {r.get('valores')}, "
              f"contaminación {resumen['contaminacion']}, error {resumen['error'][:80]!r}", flush=True)
    print(f"Modo {modo} completo.")


def calificar(q, resumen):
    """Devuelve (resultado, datos_correctos, interpretacion_correcta). Las reglas se fijaron antes de correr."""
    r = resumen.get("respuesta")
    if resumen.get("error") and not r:
        return "error", False, None
    if not r:
        return "sin_respuesta", False, None
    esperados, tolerancias = json.loads(q.valores), json.loads(q.tolerancias)
    valores = (r.get("valores") or []) + [None] * len(esperados)
    aciertos = [v is not None and abs(v - e) <= t for v, e, t in zip(valores, esperados, tolerancias)]
    vacios = all(v is None for v in valores[:len(esperados)])
    texto_bien = not q.texto or q.texto.casefold() in (r.get("texto") or "").casefold()
    datos = all(aciertos) and texto_bien
    if q.tipo != "Combinada":
        if datos:
            return "correcta", True, None
        if vacios:
            return "sin_respuesta", False, None
        return ("parcial" if any(aciertos) else "incorrecta"), False, None
    lectura = r.get("interpretacion") or ""
    interpretacion = bool(NIEGA.search(lectura) and MOTIVO.search(lectura))
    if datos and interpretacion:
        return "correcta", True, True
    if vacios and not texto_bien and not interpretacion:
        return "sin_respuesta", False, False
    if datos or interpretacion or any(aciertos):
        return "parcial", datos, interpretacion
    return "incorrecta", False, False


def resumir():
    preguntas = pd.read_csv(AQUI / "preguntas.csv", keep_default_na=False)
    ruta_revision = AQUI / "revision_manual.csv"
    revision = pd.read_csv(ruta_revision, keep_default_na=False) if ruta_revision.exists() else pd.DataFrame(columns=["id", "modo", "resultado", "motivo"])
    filas = []
    for q in preguntas.itertuples():
        for modo in MODOS:
            ruta = EVIDENCIAS / f"{modo}_{q.id}.json"
            if not ruta.exists():
                continue
            s = json.loads(ruta.read_text(encoding="utf-8"))
            automatico, datos, interpretacion = calificar(q, s)
            cambio = revision[(revision["id"] == q.id) & (revision["modo"] == modo)]
            r = s.get("respuesta") or {}
            generada = ", ".join(filter(None, [r.get("texto", ""), *[str(v) for v in r.get("valores", [])]]))
            filas.append({"id": q.id, "tipo": q.tipo, "modo": modo, "pregunta": q.pregunta, "respuesta_esperada": q.respuesta_esperada,
                          "respuesta_generada": generada, "interpretacion_generada": r.get("interpretacion", ""),
                          "fuente_utilizada": r.get("fuente", ""), "herramientas_utilizadas": " ".join(sorted(set(s["herramientas"]))) or "ninguna",
                          "skills_utilizadas": " ".join(dict.fromkeys(s["skills"])), "llamadas": len(s["herramientas"]),
                          "resultado": cambio["resultado"].iloc[0] if len(cambio) else automatico,
                          "resultado_automatico": automatico, "datos_correctos": datos, "interpretacion_correcta": interpretacion,
                          "revision_manual": cambio["motivo"].iloc[0] if len(cambio) else "", "segundos": s["segundos"],
                          "turnos": s["turnos"], "costo_usd": round(s["costo_usd"] or 0, 4), "error": s["error"],
                          "contaminacion": " ".join(s["contaminacion"])})
    t = pd.DataFrame(filas)
    t.to_csv(AQUI / "resultados.csv", index=False, encoding="utf-8")
    print(t.pivot(index="id", columns="modo", values="resultado").to_string())
    print(t.groupby("modo")["resultado"].value_counts().unstack(fill_value=0).to_string())
    print(t.groupby("modo")[["segundos", "costo_usd"]].agg(["mean", "sum"]).round(3).to_string())
    return t


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--preparar", action="store_true")
    p.add_argument("--modo", choices=list(MODOS))
    p.add_argument("--minutos", type=float, default=8)
    p.add_argument("--resumir", action="store_true")
    a = p.parse_args()
    if a.preparar:
        preparar()
    if a.modo:
        lanzar(a.modo, a.minutos)
    if a.resumir:
        resumir()
