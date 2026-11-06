# Referencia de la ENAHO 2024

Léela cuando una pregunta use una variable o un corte que no aparece en `SKILL.md`.

## Archivos

| Archivo | Una fila por | Filas | Llaves | Factor |
|---|---|---|---|---|
| `966-Modulo34.zip` → `sumaria-2024.dta` | hogar | 33,691 | `conglome`, `vivienda`, `hogar` | `factor07` |
| `966-Modulo02.zip` → `enaho01-2024-200.dta` | persona | 117,721 | las tres + `codperso` | `facpob07` |

Los zip traen otros archivos que no se usan: `sumaria-2024-12g.dta` tiene el gasto en 12 grupos (misma pobreza y mismo
factor), y `enaho_tabla_ciuo_88.dta` y `enaho_tabla_cno_2015.dta` son tablas de ocupaciones. También traen la
documentación: `Diccionario2024.pdf`, `FichaTecnica.pdf`, `Sumaria-2024.pdf` y `CED-01-200-2024.pdf`.

## Columnas de las bases procesadas

`salidas/hogares_2024.parquet` y `salidas/personas_2024.parquet` comparten estas columnas:

| Columna | Significado |
|---|---|
| `conglome`, `vivienda`, `hogar` | Llaves, como texto con sus ceros iniciales. `conglome` es la UPM |
| `ubigeo`, `departamento`, `nombre_departamento` | Ubigeo de 6 dígitos, `ubigeo[:2]` y su nombre. 25 unidades: Lima (15) y Callao (07) van separados |
| `estrato`, `urbano`, `area` | Estrato de 1 a 8. `urbano = estrato <= 5`. `area` es `Urbana` o `Rural` |
| `dominio`, `nombre_dominio` | 1 Costa norte, 2 Costa centro, 3 Costa sur, 4 Sierra norte, 5 Sierra centro, 6 Sierra sur, 7 Selva, 8 Lima Metropolitana |
| `mes` | Mes de la encuesta, como texto |
| `pobreza` | 1 pobre extremo, 2 pobre no extremo, 3 no pobre |
| `pobre`, `pobre_extremo` | `pobreza <= 2` y `pobreza == 1`, como 0 o 1 |
| `linea`, `linpe` | Línea de pobreza total y alimentaria, en soles por persona al mes |
| `gasto_mensual_pc` | `gashog2d / (12 × mieperho)`, gasto por persona al mes |
| `mieperho` | Miembros del hogar. Coincide con quienes tienen `p204 == 1` |
| `factor07` | Factor de expansión anual del hogar |
| `estrato_diseno` | `departamento-estrato`, estrato para el error de muestreo |
| `peso` | El peso que corresponde a cada base; ver abajo |

Solo en `hogares_2024.parquet`: `gashog2d` (gasto anual bruto) e `inghog1d` (ingreso anual bruto).

Solo en `personas_2024.parquet`: `codperso`, `facpob07`, `sexo` (`Hombre`, `Mujer`), `edad` y `grupo_edad` (`0-14`,
`15-29`, `30-44`, `45-59`, `60 y más`).

## Unidad de análisis y factor

| Pregunta | Base | Peso |
|---|---|---|
| Pobreza de Perú, área, dominio o departamento | hogares | `factor07 × mieperho`, método del INEI |
| Pobreza por sexo o edad | personas | `facpob07`, sobre residentes habituales |
| Una característica del hogar como unidad | hogares | `factor07`, sin `mieperho`, con un cálculo propio y dicho expresamente |

Usar `factor07` solo responde otra pregunta: qué porcentaje de hogares es pobre, no de personas. `validacion.txt` muestra
cuánto cambia la cifra con cada error.

## Residentes habituales

```python
((p204 == 1) & (p205 == 2)) | ((p204 == 2) & (p206 == 1))
```

- `p204`: ¿es miembro del hogar? 1 sí, 2 no.
- `p205`: ¿se encuentra ausente del hogar 30 días o más? 1 sí, 2 no.
- `p206`: ¿está presente en el hogar 30 días o más? 1 sí, 2 no.
- Las 3,966 filas con `p203 == 0` son registros del panel, sin datos en `p204`, y no pasan el filtro.

`mieperho` no aplica ese filtro: por eso las dos bases cubren poblaciones algo distintas.

## Error de muestreo

La Ficha Técnica describe una muestra «probabilística, de áreas, estratificada, bietápica e independiente en cada
departamento». `estimar.py` usa `conglome` como UPM y `departamento × estrato` como estrato, y linealiza la razón
ponderada. Un control con jackknife de UPM dio el mismo error estándar con 2 o más cifras significativas.

- Un subgrupo se marca como dominio, sin borrar filas: borrarlas subestima el error.
- Para comparar dos grupos usa `diferencia()`, que considera que comparten hogares y conglomerados.
- `cv_pct > 15` se marca como cifra referencial. Es una regla práctica de este proyecto, no una cifra publicada por el
  INEI en estos archivos.

## Qué no está en la base

Educación (módulo 03), salud (04), empleo (05) y programas sociales (37) no se descargan: la tarea pide los módulos 34 y
02. Tampoco hay otros años. Una pregunta sobre esos temas no se puede responder con esta skill.

La sumaria tiene más variables de gasto e ingreso que no pasan a la base. Para sumarlas, añádelas a `COLUMNAS_HOGAR` en
`scripts/limpiar.py`, con su significado tomado de `Sumaria-2024.pdf`, y corre la limpieza de nuevo.
