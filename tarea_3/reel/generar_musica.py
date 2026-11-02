"""Pista de fondo para el reel, sintetizada con numpy: sin derechos de terceros (dominio público).

Acordes La menor - Fa - Do - Sol (4 s cada uno, 80 s en total) con un colchón suave, un bajo
y un arpegio tenue, más una reverberación simple. La mezcla final la baja a -32 LUFS por debajo
de la voz (reel.video), así que aquí solo se normaliza el pico.

Uso, desde tarea_3/reel/:
    python generar_musica.py        # -> recursos/musica/musica_generada.mp3

Si prefieren una pista hecha por músicos, usen una con licencia que permita el uso (por ejemplo,
la Pixabay Content License o CC BY con atribución), guárdenla en recursos/musica/ y pásenla con
--musica; actualicen el campo «creditos» de guion.json.
"""
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

AQUI = Path(__file__).parent
SALIDA = AQUI / "recursos" / "musica" / "musica_generada.mp3"
SR = 44100
DUR_ACORDE = 4.0
REPETICIONES = 5            # 4 acordes × 4 s × 5 = 80 s
rng = np.random.default_rng(42)


def nota(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


# Acordes en notación MIDI (raíz grave + tríada en el registro medio)
ACORDES = [
    (45, [57, 60, 64]),   # La menor
    (41, [57, 60, 65]),   # Fa
    (48, [55, 60, 64]),   # Do
    (43, [55, 59, 62]),   # Sol
]


def envolvente(n: int, ataque: float, salida: float) -> np.ndarray:
    t = np.arange(n) / SR
    env = np.minimum(1.0, t / ataque) * np.minimum(1.0, (n / SR - t) / salida)
    return np.clip(env, 0, 1)


def colchon(freqs, dur):
    """Ondas senoidales con un leve desafinado (efecto coro) y armónicos suaves."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for desaf in (-0.12, 0.0, 0.12):
            ff = f * 2 ** (desaf / 12)
            fase = rng.uniform(0, 2 * np.pi)
            s += np.sin(2 * np.pi * ff * t + fase) + 0.25 * np.sin(4 * np.pi * ff * t + fase)
    return s * envolvente(n, 1.2, 1.2) / (len(freqs) * 3)


def bajo(f, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * envolvente(n, 0.05, 1.5) * 0.6


def arpegio(freqs, dur):
    """Notas cortas y tenues (corcheas a 60 ppm) que dan movimiento."""
    n = int(dur * SR)
    s = np.zeros(n)
    paso = 0.5
    orden = [0, 1, 2, 1, 2, 1, 0, 1]
    for k, i in enumerate(orden):
        ini = int(k * paso * SR)
        m = int(1.2 * SR)
        t = np.arange(m) / SR
        f = freqs[i] * 2
        g = np.sin(2 * np.pi * f * t) * np.exp(-t * 4.0) * 0.18
        fin = min(n, ini + m)
        s[ini:fin] += g[: fin - ini]
    return s


def reverb(x, segundos=2.2, mezcla=0.25):
    m = int(segundos * SR)
    impulso = rng.standard_normal(m) * np.exp(-np.arange(m) / SR * 3.0)
    impulso /= np.sqrt((impulso ** 2).sum())
    largo = len(x) + m - 1
    nfft = 1 << (largo - 1).bit_length()
    humedo = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(impulso, nfft), nfft)[: len(x)]
    return (1 - mezcla) * x + mezcla * humedo


def main() -> None:
    n_acorde = int(DUR_ACORDE * SR)
    cola = int(1.2 * SR)        # los acordes se superponen 1,2 s para que no haya cortes
    total = n_acorde * len(ACORDES) * REPETICIONES + cola
    pista = np.zeros(total)
    k = 0
    for _ in range(REPETICIONES):
        for raiz, triada in ACORDES:
            ini = k * n_acorde
            dur = DUR_ACORDE + cola / SR
            freqs = [nota(m) for m in triada]
            seg = colchon(freqs, dur) + bajo(nota(raiz), dur) + arpegio(freqs, dur)
            pista[ini:ini + len(seg)] += seg
            k += 1
    pista = reverb(pista)
    pista *= envolvente(len(pista), 2.0, 3.0)
    pista = pista / np.abs(pista).max() * 0.7
    estereo = np.stack([pista, np.roll(pista, int(0.012 * SR))], axis=1).astype(np.float32)

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ffmpeg, "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "libmp3lame", "-b:a", "128k", str(SALIDA)],
                   input=estereo.tobytes(), check=True)
    print(f"Listo: {SALIDA.relative_to(AQUI).as_posix()} ({len(pista) / SR:.0f} s)")


if __name__ == "__main__":
    main()
