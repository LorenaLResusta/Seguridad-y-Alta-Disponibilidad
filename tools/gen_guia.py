#!/usr/bin/env python3
"""Genera las páginas de la guía que dependen de datos: RA/CE y temporalización.

    python3 tools/gen_guia.py

Lee tools/matriz_ra_ce.json, data/curriculo.yaml y tools/calendario.py.
Escribe content.es/guia/ra-ce.md y content.es/guia/temporalizacion.md.
"""
import json, datetime as dt, pathlib, sys, yaml
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import calendario as cal

R = pathlib.Path(__file__).resolve().parents[1]
cur = yaml.safe_load(open(R / "data/curriculo.yaml", encoding="utf8"))
mat = json.load(open(R / "tools/matriz_ra_ce.json", encoding="utf8"))
SLUG = {"UD1": "ud01-seguridad-informatica", "UD2": "ud02-seguridad-pasiva", "UD3": "ud03-criptografia",
        "UD4": "ud04", "UD5": "ud05-seguridad-redes", "UD6": "ud06-seguridad-perimetral",
        "UD7": "ud07-alta-disponibilidad"}
UDS = [u[0] for u in cal.UNIDADES]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MES = ["", "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
def f(d): return f"{d.day} {MES[d.month]}"

def link(u): return f"[{u}](/{SLUG[u]}/)"

# ---------------- RA / CE ----------------
out = ["""---
title: "Resultados de aprendizaje y criterios de evaluación"
weight: 1
---

# Resultados de aprendizaje y criterios de evaluación

El módulo **0378. Seguridad y alta disponibilidad** pertenece al título de **Técnico Superior en Administración de Sistemas Informáticos en Red** y se imparte en **2.º curso**. Sus resultados de aprendizaje (RA) y criterios de evaluación (CE) proceden de las enseñanzas mínimas del **Real Decreto 1629/2009, de 30 de octubre**, modificado por el **Real Decreto 500/2024, de 21 de mayo**. El currículo autonómico vigente es el del **Decreto 114/2025, de 29 de julio, del Consell**, que fija **133 horas** (4 horas semanales).

> [!IMPORTANT]
> Un **resultado de aprendizaje** describe lo que sabrás hacer al terminar el módulo. Un **criterio de evaluación** es una evidencia concreta de que lo has conseguido. Cada unidad, práctica y actividad de estos apuntes indica qué CE trabaja.

> [!NOTE]
> El orden de las unidades no sigue el de los RA. El currículo describe *qué* hay que conseguir, no *en qué orden* se enseña: primero se estudia qué proteger y cómo cifrarlo (UD1 a UD4), después la red y su perímetro (UD5 y UD6) y, al final, cómo garantizar que el servicio no se detiene (UD7), porque la alta disponibilidad reutiliza lo aprendido antes.

## Mapa de contribución

```mermaid
flowchart LR
    RA1["RA1 · Pautas seguras"] --- U1[UD1] & U2[UD2] & U3[UD3] & U4[UD4]
    RA2["RA2 · Seguridad activa"] --- U3 & U4 & U5
    RA3["RA3 · Acceso remoto"] --- U3 & U6
    RA4["RA4 · Cortafuegos"] --- U6
    RA5["RA5 · Proxy"] --- U6
    RA6["RA6 · Alta disponibilidad"] --- U2 & U7
    RA7["RA7 · Legislación"] --- U1
```

● contribución principal · ○ contribución complementaria. Los textos de los criterios son **literales** del Real Decreto 1629/2009.
"""]
for ra, d in cur.items():
    out.append(f"\n## {ra}. {d['titulo']}\n")
    out.append("| CE | Criterio de evaluación | Unidades |\n|---|---|---|")
    for k, txt in d["ce"].items():
        cols = mat[f"{ra}.{k}"]
        us = ", ".join(f"{link(u)}{' ○' if c == '○' else ''}" for u, c in zip(UDS, cols) if c)
        out.append(f"| {ra}.{k} | {txt} | {us} |")
(R / "content.es/guia/ra-ce.md").write_text("\n".join(out) + "\n", encoding="utf8")

# ---------------- Temporalización ----------------
filas, tot, ses = cal.plan()
t = ["""---
title: "Temporalización y calendario"
weight: 2
bookToc: true
---

# Temporalización y calendario

## Horas oficiales del módulo

| Dato | Valor | Fuente |
|---|---|---|
| Módulo | 0378. Seguridad y alta disponibilidad | RD 1629/2009 |
| Curso | 2.º ASIR | Decreto 114/2025 |
| **Duración** | **133 horas** | Decreto 114/2025, de 29 de julio, del Consell (Anexo de distribución horaria) |
| **Carga semanal** | **4 horas** (oficial) · **5 horas** en esta planificación | Decreto 114/2025 · horario del grupo |
| Duración mínima estatal | 55 horas · 6 ECTS | RD 1629/2009 (enseñanzas mínimas) |

> [!WARNING]
> **No uses la Orden 36/2012.** La orden anterior fijaba 100 horas (5 semanales) en la Comunitat Valenciana. Para el curso 2026/27 el currículo vigente es el del **Decreto 114/2025**: 133 horas en total. Esta planificación reparte esas 133 horas a **5 horas semanales** (una hora cada día lectivo); el total oficial no cambia.

Estos apuntes cuentan **horas lectivas** (las del horario oficial del grupo). Cada unidad reparte sus horas en tres bloques: **teoría** (explicación y ejemplos), **prácticas** (laboratorio guiado y autónomo) y **evaluación** (prueba teórico-práctica y entrega de la tarea de la unidad).

## Distribución por unidades

| UD | Unidad | Teoría | Prácticas | Evaluación | Total | % | RA principales |
|---|---|--:|--:|--:|--:|--:|---|"""]
sumT = sumP = sumE = 0
for c, tit, a, b, e in cal.UNIDADES:
    tt = a + b + e; sumT += a; sumP += b; sumE += e
    ras = sorted({k.split(".")[0] for k, v in mat.items() if v[UDS.index(c)] == "●"})
    t.append(f"| {c} | [{tit}](/{SLUG[c]}/) | {a} h | {b} h | {e} h | **{tt} h** | {round(tt*100/133)} % | {', '.join(ras)} |")
t.append(f"| | **Total** | **{sumT} h** | **{sumP} h** | **{sumE} h** | **133 h** | 100 % | RA1 a RA7 |")
t.append(f"""> [!NOTE]
> El **{round(sumP*100/133)} %** de las horas son de laboratorio. Esa proporción es intencionada: en seguridad y alta disponibilidad se aprende configurando, atacando en un entorno aislado, comprobando y recuperando.

## Calendario escolar de referencia 2026/27

| Hito | Fecha |
|---|---|
| Inicio del curso | miércoles 9 de septiembre de 2026 |
| Vacaciones de Navidad | del 22 de diciembre de 2026 al 6 de enero de 2027 |
| Vacaciones de Pascua | del 25 de marzo al 5 de abril de 2027 |
| Fin del curso | viernes 18 de junio de 2027 |
| Días lectivos del curso | 179 |

Festivos y días no lectivos que afectan a la planificación (calendario **provisional** del IES San Vicente; los marcados «propuesta» deben ser aprobados por el Consejo Escolar Municipal):

| Fecha | Motivo |
|---|---|""")
for d in sorted(k for k in cal.NO_LECTIVOS if not cal.NO_LECTIVOS[k].startswith("Vacaciones")):
    t.append(f"| {DIAS[d.weekday()]} {f(d)} {d.year} | {cal.NO_LECTIVOS[d]} |")
t.append(f"""
> [!CAUTION]
> **Calendario provisional.** Comprueba las fechas con la versión definitiva que publique el centro. Si cambia algún festivo, vuelve a ejecutar `tools/gen_guia.py` para regenerar esta tabla.
""")
t.append(f"""## Propuesta de calendario

**Horario supuesto:** 5 horas semanales, una hora cada día lectivo de lunes a viernes. Si el grupo tiene otro horario, edita `HORARIO` en `tools/calendario.py` y regenera con `python3 tools/planificacion.py` y `python3 tools/gen_guia.py`.

Hasta el 18 de junio hay **{len(ses)} horas** posibles. Se necesitan 133: el plan termina el **{filas[-1]['fecha']}** y quedan **{len(ses)-133} horas de margen** para imprevistos, repasos, recuperaciones y la evaluación final.

> [!NOTE]
> El **calendario interactivo** (pulsa un día para ver qué toca) está en la [portada](/). La tabla resume el mismo plan por semanas.

| Semana | Del | Al | Horas | Unidad(es) | Horas acumuladas |
|--:|---|---|--:|---|---|""")
sem = {}
for r in filas:
    d = dt.date.fromisoformat(r["fecha"]); k = d - dt.timedelta(days=d.weekday())
    sem.setdefault(k, []).append((d, r))
for n, (k, rs) in enumerate(sem.items(), 1):
    uds = []
    for _, r in rs:
        for u in r["ud"].split("/"):
            if u not in uds: uds.append(u)
    t.append(f"| {n} | {DIAS[rs[0][0].weekday()][:3]} {f(rs[0][0])} | {DIAS[rs[-1][0].weekday()][:3]} {f(rs[-1][0])} | {sum(r['horas'] for _, r in rs)} | {' / '.join(uds)} | {rs[0][1]['h_ini']}–{rs[-1][1]['h_fin']} |")
t.append("""
## Cómo está pensado el ritmo de cada unidad

1. **Primeras sesiones: teoría y demostración.** Se presentan los conceptos con el ciclo *amenaza → vulnerabilidad → ataque → detección → mitigación → comprobación*.
2. **Sesiones centrales: prácticas guiadas.** Se reproduce el procedimiento paso a paso en el laboratorio y se anota qué ocurre en cada comprobación.
3. **Sesiones finales: práctica autónoma, tarea del proyecto y evaluación.** La última sesión de cada unidad es la prueba; la tarea del proyecto se entrega en esa semana.

> [!TIP]
> En las unidades de red, perímetro y alta disponibilidad conviene dejar las **instantáneas** de las máquinas virtuales preparadas al final de cada sesión: la siguiente práctica parte del estado en que terminó la anterior.
""")
t += ["", "## Entregas obligatorias", "", "| Práctica | Unidades | Fecha |", "|---|---|---|", "| INT-1 | UD1–UD3 | 27/11/2026 |", "| INT-2 | UD4–UD6 | 22/03/2027 (propuesta) |", "| INT-3 | UD7 | 30/04/2027 (propuesta) |", "", "Detalle en [Prácticas integradoras](/guia/practicas-integradoras/)."]
(R / "content.es/guia/temporalizacion.md").write_text("\n".join(t), encoding="utf8")
print("OK")
