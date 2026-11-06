---
name: mapeando-enaho
description: Construye el mapa coroplético de la pobreza monetaria por departamento del Perú con la ENAHO 2024 del INEI, con las 25 unidades territoriales y Lima y Callao separados. Úsala cuando pidan un mapa de pobreza, un mapa por departamentos o regiones, o ver en el territorio dónde se concentra la pobreza con la ENAHO.
argument-hint: "[pobreza o pobreza extrema]"
allowed-tools: Bash(uv run *), PowerShell(uv run *), Read
---

# Mapear la pobreza de la ENAHO 2024

## 1. Revisar que exista la base

Si no existe `salidas/hogares_2024.parquet`, usa primero la skill `limpiando-enaho` y vuelve aquí cuando su validación
diga `RESULTADO: APROBADA`. Si la validación falla, detente.

## 2. Generar el mapa

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/mapear.py"
```

Para la pobreza extrema, añade `--indicador pobre_extremo`. El script descarga los límites del repositorio del curso a
`datos/` si faltan. No dibujes con código propio.

## 3. Revisar la validación

Lee `salidas/validacion_mapa.txt`. Para la pobreza extrema, lee `salidas/validacion_mapa_extrema.txt`: comprueba la unión,
pero no hay comparación, porque la referencia de la Sesión 16 solo cubre la pobreza total. Si es ese caso, dilo.

- `RESULTADO: APROBADO`: sigue. `salidas/comparacion_mapa.csv` tiene, por departamento, la cifra calculada, la referencia
  de la Sesión 16, la diferencia y el intervalo de confianza.
- `RESULTADO: RECHAZADO` o error del script: detente y di qué falló. No hay mapa. Nunca copies las cifras de la
  referencia al mapa: solo sirven para comparar.

## 4. Mirar y responder

1. Abre `mapas/pobreza_departamento.png` con Read y comprueba que estén los 25 departamentos sin zonas en blanco.
2. Responde con la ruta, los departamentos con más y menos pobreza, y el resultado de la comparación con la referencia.
3. Advierte que las cifras son muestrales: si dos intervalos se cruzan, el orden entre esos departamentos no es seguro.
   Si una cifra lleva †, avisa que es solo referencial.
4. Describe el patrón territorial sin afirmar causas.

## Reglas del mapa

Todas las aplica el script.

- Une por código: `ubigeo[:2]` con `FIRST_IDDP`, como texto. Nunca por nombre: «APURIMAC» no es «Apurímac».
- Exige 25 unidades con dato. Lima (15) y Callao (07) van separados; el recuadro muestra a los dos.
- Un color de claro a oscuro desde 0, en clases iguales de 10 puntos (5 en pobreza extrema), y la unidad en la leyenda:
  % de personas.
- Usa la base de hogares (`factor07 × mieperho`), la misma de las cifras publicadas y de la referencia.
