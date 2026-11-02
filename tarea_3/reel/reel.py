"""Pasos 2 a 4: guion.json -> voz clonada -> reel vertical con gráficos, música y créditos.

Adaptado de sessions/15-texto-a-reel/reel.py del curso (d2cml-ai/Data-Science-Python, licencia MIT).
Cambios para la Tarea 3: cada escena puede traer una «imagen» (gráfico o mapa de 900 × 570 px)
debajo de su cifra, el video mezcla una pista de música por debajo de la voz (-32 LUFS frente a
-14 LUFS de la narración), la última escena muestra los créditos y vista_previa() dibuja un cuadro
por escena sin generar la voz, para revisar el diseño.

    Voz           Qwen3-TTS clona tu voz con 10 a 20 s de audio y narra cada escena
    VozExpresiva  VoxCPM2 clona tu voz y además acepta un estilo por escena (locutor, urgente, cálido)
    subtitulos()  Whisper transcribe la narración: subtítulos palabra por palabra y control de calidad
    video()       reel 1080x1920 con cifras, subtítulos y aviso de voz generada con IA

El paso 1 (texto largo -> guion.json) está en guion.py.
"""
import re
import subprocess
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).parent
FUENTES = AQUI / "fuentes"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

TTS = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
ASR = "large-v3-turbo"

ANCHO, ALTO, FPS = 1080, 1920, 30
MARGEN = 90
FONDO, TEXTO, SUAVE, ACENTO, CAJA = "#1C1A17", "#F7F3EC", "#B8AE9F", "#F08A4B", "#2A2723"
PAUSA, INICIO, FINAL = 0.35, 0.3, 0.8   # segundos de silencio entre escenas, al inicio y al final
# Estilos de VoxCPM2 por defecto; en inglés funcionan mejor que en español. Una escena puede traer su "estilo" en guion.json
ESTILOS = {"inicio": "urgent, dramatic news anchor, strong emphasis",
           "medio": "confident news anchor, energetic, clear emphasis on the numbers",
           "cierre": "warm, friendly, inviting tone"}


def _reloj(msg, t):
    print(f"[{time.time() - t:5.1f}s] {msg}", flush=True)


# Voz clonada ---------------------------------------------------------------

def cargar_audio(ruta, sr=16000):
    """Cualquier audio (wav, m4a, ogg de WhatsApp, mp3) a mono float32 con ffmpeg."""
    crudo = subprocess.run([FFMPEG, "-v", "error", "-i", str(ruta), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                           capture_output=True, check=True).stdout
    return np.frombuffer(crudo, np.float32)


class Voz:
    """Clona una voz a partir de 10 a 20 segundos de audio y su transcripción (la hace Whisper)."""

    def __init__(self, referencia, modelo=TTS, device="cpu"):
        import torch
        from qwen_tts import Qwen3TTSModel

        self.referencia = cargar_audio(referencia)
        self.texto_ref = _transcribir(self.referencia)
        self.tts = Qwen3TTSModel.from_pretrained(modelo, device_map=device, dtype=torch.float32)
        self.prompt = self.tts.create_voice_clone_prompt(ref_audio=(self.referencia, 16000), ref_text=self.texto_ref)

    def decir(self, frases, estilos=None):   # Qwen3-TTS no acepta estilo al clonar
        wavs, self.sr = self.tts.generate_voice_clone(text=frases, language=["Spanish"] * len(frases),
                                                      voice_clone_prompt=self.prompt)
        return wavs


class VozExpresiva:
    """VoxCPM2 (OpenBMB, Apache 2.0): clona la voz y sigue un estilo escrito entre paréntesis antes de la frase."""

    def __init__(self, referencia, device="cpu", con_estilo=True):
        import tempfile

        import soundfile as sf
        from voxcpm import VoxCPM

        audio = cargar_audio(referencia)
        self.ref = Path(tempfile.mkdtemp()) / "referencia.wav"
        sf.write(self.ref, audio, 16000)
        self.texto_ref = _transcribir(audio)
        self.con_estilo = con_estilo
        self.tts = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, optimize=False, device=device)
        self.sr = self.tts.tts_model.sample_rate

    def decir(self, frases, estilos=None):
        estilos = estilos if self.con_estilo and estilos else [None] * len(frases)
        return [self.tts.generate(text=f"({e}){f}" if e else f, reference_wav_path=str(self.ref),
                                  cfg_value=2.0, inference_timesteps=10)
                for f, e in zip(frases, estilos)]


def _transcribir(audio16k):
    return " ".join(s.text.strip() for s in _whisper().transcribe(audio16k, language="es")[0])


def _acelerar(w, sr, factor):
    """Cambia el ritmo sin cambiar el tono (atempo de ffmpeg)."""
    crudo = subprocess.run([FFMPEG, "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-",
                            "-af", f"atempo={factor}", "-f", "f32le", "-"],
                           input=np.asarray(w, np.float32).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(crudo, np.float32)


# Subtítulos y control de calidad --------------------------------------------

_ASR = None


def _whisper():
    global _ASR
    if _ASR is None:
        from faster_whisper import WhisperModel
        _ASR = WhisperModel(ASR, device="cpu", compute_type="int8")
    return _ASR


@dataclass
class Narracion:
    audio: np.ndarray
    sr: int
    escenas: list            # (inicio, fin) en segundos de cada escena
    palabras: list = field(default_factory=list)   # (inicio, fin, palabra) de Whisper

    @property
    def duracion(self):
        return len(self.audio) / self.sr


def narrar(voz, guion, max_wer=0.25, reintentos=1, velocidad=1.0):
    """Narra cada escena; si Whisper no entiende bien una escena (WER alto), la vuelve a generar."""
    frases = [e["frase"] for e in guion["escenas"]]
    n = len(frases)
    estilos = [e.get("estilo") or ESTILOS["inicio" if i == 0 else "cierre" if i == n - 1 else "medio"]
               for i, e in enumerate(guion["escenas"])]
    wavs = voz.decir(frases, estilos)
    if velocidad != 1:
        wavs = [_acelerar(w, voz.sr, velocidad) for w in wavs]
    for intento in range(reintentos + 1):
        for e, w in zip(guion["escenas"], wavs):
            e["wer"] = _wer(e["frase"], _a16k(w, voz.sr))
        malas = [i for i, e in enumerate(guion["escenas"]) if e["wer"] > max_wer]
        if not malas or intento == reintentos:
            break
        for i, w in zip(malas, voz.decir([frases[i] for i in malas], [estilos[i] for i in malas])):
            wavs[i] = _acelerar(w, voz.sr, velocidad) if velocidad != 1 else w

    sr, partes, escenas, t = voz.sr, [np.zeros(int(INICIO * voz.sr), np.float32)], [], INICIO
    for w in wavs:
        w = np.asarray(w, np.float32)
        escenas.append((t, t + len(w) / sr))
        partes += [w, np.zeros(int(PAUSA * sr), np.float32)]
        t += len(w) / sr + PAUSA
    partes.append(np.zeros(int(FINAL * sr), np.float32))
    return Narracion(np.concatenate(partes), sr, escenas)


def _a16k(w, sr):
    w = np.asarray(w, np.float32)
    return np.interp(np.arange(0, len(w), sr / 16000), np.arange(len(w)), w).astype(np.float32)


def _normalizar(s):
    """Para comparar lo escrito con lo que oyó Whisper: números en palabras, sin tildes ni puntuación."""
    from num2words import num2words
    s = s.lower().replace("%", " por ciento")
    s = re.sub(r"(?<=\d)[,.](?=\d{3}\b)", "", s)
    s = re.sub(r"\d+", lambda m: num2words(int(m.group()), lang="es"), s)
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^\w\s]", " ", s).split())


def _wer(referencia, audio16k):
    import jiwer
    oido = " ".join(s.text for s in _whisper().transcribe(audio16k, language="es")[0])
    return jiwer.wer(_normalizar(referencia), _normalizar(oido)) if _normalizar(oido) else 1.0


def subtitulos(narracion, guion):
    """Palabras con tiempo; el guion va como contexto para que Whisper escriba bien los nombres propios."""
    contexto = " ".join(e["frase"] for e in guion["escenas"])
    segs, _ = _whisper().transcribe(_a16k(narracion.audio, narracion.sr), language="es",
                                    word_timestamps=True, initial_prompt=contexto)
    palabras = []
    for w in (w for s in segs for w in s.words if w.word.strip()):
        # Whisper a veces parte "8.7" o "126%" en dos palabras: se pegan a la anterior
        if palabras and re.match(r"^[.,%]", w.word.strip()):
            ini, _, prev = palabras.pop()
            palabras.append((ini, w.end, prev + w.word.strip()))
        else:
            palabras.append((w.start, w.end, w.word.strip()))
    palabras = corregir(palabras, guion.get("correcciones_subtitulos", {}))
    narracion.palabras = palabras
    return palabras


def _clave(w):
    return re.sub(r"[^\w]", "", unicodedata.normalize("NFD", w.lower()).encode("ascii", "ignore").decode())


def corregir(palabras, correcciones):
    """Reemplaza en los subtítulos lo que Whisper oyó mal (p. ej. siglas) por el texto del guion.

    correcciones = {"de el enlace": "del INEI: el enlace"}; el tramo conserva sus tiempos y las
    palabras nuevas se reparten en partes iguales.
    """
    for mal, bien in correcciones.items():
        objetivo = [_clave(w) for w in mal.split()]
        n = len(objetivo)
        i = 0
        while i + n <= len(palabras):
            if [_clave(p[2]) for p in palabras[i:i + n]] == objetivo:
                ini, fin = palabras[i][0], palabras[i + n - 1][1]
                nuevas = bien.split()
                paso = (fin - ini) / len(nuevas)
                palabras[i:i + n] = [(ini + k * paso, ini + (k + 1) * paso, w) for k, w in enumerate(nuevas)]
                i += len(nuevas)
            else:
                i += 1
    return palabras


def escenas_por_palabras(palabras, guion, duracion):
    """Inicio y fin de cada escena buscando sus dos primeras palabras en lo que transcribió Whisper."""
    claves = [_clave(p[2]) for p in palabras]
    inicios, desde = [], 0
    for e in guion["escenas"]:
        primeras = [_clave(w) for w in e["frase"].split()[:2]]
        k = next((j for j in range(desde, len(claves) - 1) if claves[j:j + 2] == primeras), None)
        if k is None:
            raise ValueError(f"no encuentro el inicio de la escena «{e['frase'][:40]}…» en la transcripción")
        inicios.append(max(palabras[k][0] - 0.1, 0.0))
        desde = k + 1
    finales = [ini - PAUSA for ini in inicios[1:]] + [min(palabras[-1][1] + 0.2, duracion)]
    return list(zip(inicios, finales))


def _bloques(palabras, max_palabras=4, max_letras=24):
    """Agrupa palabras en bloques cortos para leer en el celular; corta en signos de puntuación."""
    bloques, actual = [], []
    for p in palabras:
        actual.append(p)
        largo = sum(len(x[2]) + 1 for x in actual)
        if len(actual) >= max_palabras or largo >= max_letras or p[2][-1] in ".,;:?!":
            bloques.append(actual)
            actual = []
    if actual:
        bloques.append(actual)
    return bloques


def a_srt(narracion, ruta):
    def hms(t):
        return f"{int(t // 3600):02}:{int(t % 3600 // 60):02}:{int(t % 60):02},{int(t % 1 * 1000):03}"
    lineas = []
    for i, b in enumerate(_bloques(narracion.palabras), 1):
        lineas += [str(i), f"{hms(b[0][0])} --> {hms(b[-1][1])}", " ".join(p[2] for p in b), ""]
    Path(ruta).write_text("\n".join(lineas), encoding="utf-8")


# Video ---------------------------------------------------------------------

def _fuente(nombre, tam, peso):
    ruta = FUENTES / f"{nombre}.ttf"
    if not ruta.exists():   # Oswald y Public Sans, de Google Fonts (licencia OFL)
        import urllib.request
        FUENTES.mkdir(exist_ok=True)
        urllib.request.urlretrieve(f"https://github.com/google/fonts/raw/main/ofl/{nombre.lower()}/{nombre}%5Bwght%5D.ttf", ruta)
    f = ImageFont.truetype(str(ruta), tam)
    f.set_variation_by_axes([peso])
    return f


def _envolver(draw, texto, fuente, ancho):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if draw.textlength(prueba, font=fuente) <= ancho:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    return lineas + [actual]


def _ajustar(draw, texto, nombre, peso, ancho, maximo, minimo=80):
    for tam in range(maximo, minimo, -10):
        f = _fuente(nombre, tam, peso)
        if draw.textlength(texto, font=f) <= ancho:
            return f
    return _fuente(nombre, minimo, peso)


def _base(titulo, fuente_datos, autor):
    """Lo que no cambia en todo el video: título, aviso de IA y fuente."""
    img = Image.new("RGB", (ANCHO, ALTO), FONDO)
    d = ImageDraw.Draw(img)
    d.text((MARGEN, 250), titulo.upper(), font=_fuente("PublicSans", 40, 800), fill=ACENTO)
    aviso = "VOZ GENERADA CON IA"
    f = _fuente("PublicSans", 28, 700)
    x1 = MARGEN + d.textlength(aviso, font=f) + 36
    d.rounded_rectangle((MARGEN, 315, x1, 365), radius=25, outline=SUAVE, width=2)
    d.text((MARGEN + 18, 340), aviso, font=f, fill=SUAVE, anchor="lm")
    pie = _fuente("PublicSans", 30, 500)
    for i, linea in enumerate(_envolver(d, f"{autor} · Fuente: {fuente_datos}", pie, ANCHO - 2 * MARGEN)):
        d.text((MARGEN, 1480 + i * 42), linea, font=pie, fill=SUAVE)
    return img


def _escena(e, creditos=None):
    """Capa transparente: cifra grande, etiqueta y, si la escena la trae, la imagen (gráfico o mapa)."""
    capa = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    ancho = ANCHO - 2 * MARGEN
    def alto(texto, f):   # altura sobre la línea base
        return -d.textbbox((0, 0), texto, font=f, anchor="ls")[1]

    imagen = None
    if e.get("imagen"):
        imagen = Image.open(AQUI / e["imagen"]).convert("RGBA")
        imagen.thumbnail((ancho, 570))
    # Con imagen, la cifra es más chica para que quepan las dos entre el aviso de IA y los subtítulos
    max_cifra = 150 if imagen else 300
    lineas = []
    if e.get("cifra"):
        f = _ajustar(d, e["cifra"], "Oswald", 700, ancho, max_cifra, minimo=70)
        lineas.append((e["cifra"], f, TEXTO, alto(e["cifra"], f), 34 if imagen else 70))
        fe, color = _fuente("PublicSans", 40 if imagen else 58, 600), SUAVE
    else:
        fe, color = _fuente("Oswald", 64 if imagen else 104, 600), TEXTO
    lineas += [(x, fe, color, alto("H", fe), int(fe.size * 0.4)) for x in _envolver(d, e["etiqueta"], fe, ancho)]
    if imagen:
        y = 400
    else:
        y = (420 + 1220 - sum(h + g for *_, h, g in lineas) + lineas[-1][4]) / 2
    for texto, f, color, h, g in lineas:
        y += h
        d.text((MARGEN, y), texto, font=f, fill=color, anchor="ls")
        y += g
    if imagen:
        y_img = int(max(y + 20, 1240 - imagen.height))
        capa.paste(imagen, (MARGEN + (ancho - imagen.width) // 2, y_img), imagen)
    if creditos:
        fc = _fuente("PublicSans", 26, 500)
        for i, linea in enumerate(_envolver(d, creditos, fc, ancho)):
            d.text((MARGEN, 1600 + i * 36), linea, font=fc, fill=SUAVE)
    return capa


def _cuadro(base, capas, narracion, t, bloques, fuente_sub):
    img = base.copy()
    # escena actual, con una entrada suave (aparece y sube) en sus primeros 0.35 s
    i = max([k for k, (ini, _) in enumerate(narracion.escenas) if ini - PAUSA <= t] or [0])
    a = min(1.0, max(0.0, (t - narracion.escenas[i][0] + PAUSA) / 0.35))
    capa = capas[i]
    if a < 1:
        capa = capa.copy()
        capa.putalpha(capa.getchannel("A").point(lambda v: int(v * a)))
    img.paste(capa, (0, int(40 * (1 - a))), capa)

    d = ImageDraw.Draw(img)
    # barra de avance arriba, como en las historias
    d.rounded_rectangle((MARGEN, 180, ANCHO - MARGEN, 188), radius=4, fill=CAJA)
    d.rounded_rectangle((MARGEN, 180, MARGEN + (ANCHO - 2 * MARGEN) * t / narracion.duracion, 188), radius=4, fill=ACENTO)

    # subtítulo: el bloque que se está diciendo, con la palabra actual resaltada
    b = next((b for b in bloques if b[0][0] - 0.1 <= t <= b[-1][1] + 0.25), None)
    if b:
        texto = " ".join(p[2] for p in b)
        w = d.textlength(texto, font=fuente_sub)
        x, y = (ANCHO - w) / 2, 1300
        d.rounded_rectangle((x - 36, y - 26, x + w + 36, y + fuente_sub.size + 34), radius=28, fill=CAJA)
        for ini, fin, palabra in b:
            d.text((x, y), palabra, font=fuente_sub, fill=ACENTO if ini <= t <= fin + 0.05 else TEXTO)
            x += d.textlength(palabra + " ", font=fuente_sub)
    return img


def _capas(guion):
    n = len(guion["escenas"])
    return [_escena(e, guion.get("creditos") if i == n - 1 else None) for i, e in enumerate(guion["escenas"])]


def video(guion, narracion, ruta, fuente_datos, autor, musica=None):
    """Dibuja cada cuadro con Pillow y se los pasa a ffmpeg con la narración (-14 LUFS) y la música (-32 LUFS)."""
    import soundfile as sf

    ruta = Path(ruta)
    wav = ruta.with_suffix(".wav")
    sf.write(wav, narracion.audio, narracion.sr)
    base = _base(guion["titulo"], fuente_datos, autor)
    capas = _capas(guion)
    bloques = _bloques(narracion.palabras)
    fuente_sub = _fuente("PublicSans", 62, 800)
    entradas = ["-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ANCHO}x{ALTO}", "-r", str(FPS), "-i", "-",
                "-i", str(wav)]
    voz = "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-14:TP=-1.5:LRA=11"
    if musica:
        dur = narracion.duracion
        entradas += ["-stream_loop", "-1", "-i", str(musica)]
        filtro = (f"{voz}[voz];[2:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                  f"loudnorm=I=-32:TP=-3:LRA=11,atrim=0:{dur:.2f},afade=t=in:d=1.5,"
                  f"afade=t=out:st={max(dur - 2.5, 0):.2f}:d=2.5[mus];"
                  f"[voz][mus]amix=inputs=2:duration=first:normalize=0[a]")
    else:
        filtro = f"{voz}[a]"
    cmd = [FFMPEG, "-y", "-v", "error", *entradas, "-filter_complex", filtro, "-map", "0:v", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
           "-shortest", "-movflags", "+faststart", str(ruta)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(int(narracion.duracion * FPS)):
        proc.stdin.write(_cuadro(base, capas, narracion, k / FPS, bloques, fuente_sub).tobytes())
    proc.stdin.close()
    proc.wait()
    return ruta


def portada(guion, narracion, ruta, fuente_datos, autor, escena=1):
    """Un cuadro fijo para revisar el diseño o usar como miniatura."""
    t = narracion.escenas[escena][0] + 1.0
    img = _cuadro(_base(guion["titulo"], fuente_datos, autor), _capas(guion),
                  narracion, t, _bloques(narracion.palabras), _fuente("PublicSans", 62, 800))
    img.save(ruta)
    return ruta


# Vista previa sin voz ------------------------------------------------------

def narracion_estimada(guion, palabras_por_segundo=2.5, sr=16000):
    """Tiempos aproximados (2,5 palabras/s, el ritmo medido con Qwen3-TTS) para revisar el diseño."""
    t, escenas, palabras = INICIO, [], []
    for e in guion["escenas"]:
        texto = e["frase"].split()
        dur = len(texto) / palabras_por_segundo
        paso = dur / len(texto)
        palabras += [(t + i * paso, t + (i + 1) * paso, w) for i, w in enumerate(texto)]
        escenas.append((t, t + dur))
        t += dur + PAUSA
    audio = np.zeros(int((t + FINAL) * sr), np.float32)
    return Narracion(audio, sr, escenas, palabras)


def vista_previa(guion, carpeta, fuente_datos, autor):
    """Un cuadro por escena, una hoja de contacto y subtítulos de borrador, sin TTS ni Whisper."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    narracion = narracion_estimada(guion)
    base = _base(guion["titulo"], fuente_datos, autor)
    capas = _capas(guion)
    bloques = _bloques(narracion.palabras)
    fuente_sub = _fuente("PublicSans", 62, 800)
    cuadros = []
    for i, (ini, fin) in enumerate(narracion.escenas, 1):
        img = _cuadro(base, capas, narracion, min(ini + 1.2, fin), bloques, fuente_sub)
        img.save(carpeta / f"escena_{i}.png")
        cuadros.append(img)
    hoja = Image.new("RGB", (ANCHO // 3 * len(cuadros), ALTO // 3), FONDO)
    for i, c in enumerate(cuadros):
        hoja.paste(c.resize((ANCHO // 3, ALTO // 3)), (i * ANCHO // 3, 0))
    hoja.save(carpeta / "storyboard.png")
    a_srt(narracion, carpeta / "subtitulos_borrador.srt")
    return narracion.duracion
