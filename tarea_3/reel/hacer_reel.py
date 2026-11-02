"""guion.json -> voz clonada -> reel vertical con gráficos, subtítulos, música y créditos.

Adaptado de sessions/15-texto-a-reel/hacer_reel.py del curso (licencia MIT). Uso, desde tarea_3/reel/:

    # 0. Revisar el diseño sin generar la voz (solo necesita Pillow y numpy)
    python hacer_reel.py --vista-previa

    # 1. Reel completo con tu voz de referencia (15 a 25 s) y la música
    python hacer_reel.py --voz voz/mi_voz.m4a --tts Qwen/Qwen3-TTS-12Hz-0.6B-Base

Guarda en salidas/: reel.mp4, reel.wav, reel.srt, portada.png, posts.md y guion.json con el WER
por escena. Con --vista-previa guarda en vista_previa/: un PNG por escena, storyboard.png y
subtitulos_borrador.srt (tiempos estimados).
"""
import argparse
import json
import shutil
import time
from pathlib import Path

try:  # certificados del sistema: necesario si un antivirus o proxy inspecciona HTTPS (Avast)
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import reel

AQUI = Path(__file__).parent
MUSICA = AQUI / "recursos" / "musica" / "musica_generada.mp3"
FUENTE = "INEI: ENAHO 2019-2025 y EPE Lima Metropolitana (jul-set 2026)"
AUTORA = "Ivette Carolina Mamani Flores"

p = argparse.ArgumentParser()
p.add_argument("--voz", help="15 a 25 s de tu voz: wav, m4a, ogg o mp3 (no se sube a GitHub)")
p.add_argument("--autor", default=AUTORA)
p.add_argument("--fuente", default=FUENTE, help="fuente de los datos, aparece en todo el video")
p.add_argument("--musica", default=str(MUSICA), help="pista de fondo con licencia de uso; 'ninguna' para omitirla")
p.add_argument("--device", default="cpu", help="cpu, mps (Mac) o cuda")
p.add_argument("--motor", default="qwen", choices=["qwen", "voxcpm"], help="voxcpm acepta estilo de locutor por escena")
p.add_argument("--tts", default="Qwen/Qwen3-TTS-12Hz-0.6B-Base", help="con --motor qwen; el 0.6B es el más liviano para CPU")
p.add_argument("--sin-estilo", action="store_true", help="con --motor voxcpm: clona sin indicar estilo")
p.add_argument("--velocidad", type=float, default=1.0, help="1.08 = 8 %% más rápido, sin cambiar el tono")
p.add_argument("--salidas", default=str(AQUI / "salidas"))
p.add_argument("--vista-previa", action="store_true", help="solo cuadros de prueba, sin voz")
a = p.parse_args()

guion = json.loads((AQUI / "guion.json").read_text(encoding="utf-8"))
palabras = sum(len(e["frase"].split()) for e in guion["escenas"])
print(f"Guion: {len(guion['escenas'])} escenas, {palabras} palabras "
      f"(~{palabras / 2.5:.0f} s a 2,5 palabras/s, más pausas)")
for e in guion["escenas"]:
    print(f"   {'ok ' if e.get('cifra_en_texto') else '¡¡ '} {e['cifra'] or '-':>16} | {e['frase']}")

if a.vista_previa:
    dur = reel.vista_previa(guion, AQUI / "vista_previa", a.fuente, a.autor)
    print(f"Vista previa lista en vista_previa/ (duración estimada: {dur:.0f} s)")
    raise SystemExit(0)

if not a.voz:
    p.error("falta --voz (tu grabación de 15 a 25 s); para revisar el diseño usa --vista-previa")

t0 = time.time()
salidas = Path(a.salidas)
salidas.mkdir(exist_ok=True)
shutil.copy(AQUI / "guion.json", salidas / "guion.json")
musica = None if a.musica.lower() == "ninguna" else Path(a.musica)
if musica and not musica.exists():
    print(f"   No encuentro la música en {musica}: corre primero python generar_musica.py o pasa --musica")
    raise SystemExit(1)

if a.motor == "voxcpm":
    voz = reel.VozExpresiva(a.voz, device=a.device, con_estilo=not a.sin_estilo)
else:
    voz = reel.Voz(a.voz, modelo=a.tts, device=a.device)
reel._reloj(f"voz cargada; referencia: «{voz.texto_ref}»", t0)
narracion = reel.narrar(voz, guion, velocidad=a.velocidad)
(salidas / "guion.json").write_text(json.dumps(guion, ensure_ascii=False, indent=2), encoding="utf-8")
reel._reloj(f"narración: {narracion.duracion:.1f} s; WER por escena: "
            + ", ".join(f"{e['wer']:.2f}" for e in guion["escenas"]), t0)
if not 45 <= narracion.duracion <= 75:
    print(f"   ¡Ojo! La tarea pide 45 a 75 s y salieron {narracion.duracion:.0f} s: ajusta --velocidad o el guion.")

reel.subtitulos(narracion, guion)
reel.a_srt(narracion, salidas / "reel.srt")
reel._reloj(f"subtítulos: {len(narracion.palabras)} palabras", t0)

reel.portada(guion, narracion, salidas / "portada.png", a.fuente, a.autor)
reel.video(guion, narracion, salidas / "reel.mp4", a.fuente, a.autor, musica=musica)
reel.posts(guion, salidas / "posts.md")
reel._reloj(f"listo: {salidas / 'reel.mp4'}", t0)
