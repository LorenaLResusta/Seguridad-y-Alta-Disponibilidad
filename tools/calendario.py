#!/usr/bin/env python3
"""Calcula la temporalización del módulo 0378 sobre el calendario escolar 2026/27.

Uso:  python3 tools/calendario.py            -> imprime la tabla Markdown
      python3 tools/calendario.py --json     -> imprime los datos en JSON

Parámetros (editables): horario semanal, inicio y fin de curso y días no lectivos.
Fuentes del calendario: Generalitat Valenciana (curso 2026/27: 9/09/2026 – 18/06/2027) y
calendario provisional del IES San Vicente (festivos locales y días no lectivos propuestos).
"""
import datetime as dt, json, sys

INICIO, FIN = dt.date(2026, 9, 9), dt.date(2027, 6, 18)
# Horario semanal supuesto: {día de la semana (0 = lunes): horas}. AJUSTAR al horario real del grupo.
HORARIO = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1}   # 1 h cada día lectivo de lunes a viernes = 5 h/semana

NO_LECTIVOS = {                    # fecha -> motivo
    dt.date(2026, 10, 9): "Día de la Comunitat Valenciana",
    dt.date(2026, 10, 12): "Fiesta Nacional de España",
    dt.date(2026, 12, 7): "No lectivo (propuesta del Consejo Escolar Municipal)",
    dt.date(2026, 12, 8): "Inmaculada Concepción",
    dt.date(2027, 3, 19): "San José",
    dt.date(2027, 4, 5): "Fiesta patronal de San Vicente",
    dt.date(2027, 4, 6): "Fiesta patronal de San Vicente",
    dt.date(2027, 4, 7): "No lectivo (propuesta del Consejo Escolar Municipal)",
    dt.date(2027, 4, 8): "No lectivo (propuesta del Consejo Escolar Municipal)",
    dt.date(2027, 4, 9): "No lectivo (propuesta del Consejo Escolar Municipal)",
}
def rango(a, b, motivo):
    d = a
    while d <= b:
        NO_LECTIVOS.setdefault(d, motivo); d += dt.timedelta(days=1)
rango(dt.date(2026, 12, 22), dt.date(2027, 1, 6), "Vacaciones de Navidad")
rango(dt.date(2027, 3, 25), dt.date(2027, 4, 5), "Vacaciones de Pascua")

UNIDADES = [  # (código, título, h teoría, h práctica, h evaluación)
    ("UD1", "Introducción a la seguridad, riesgos y marco legal", 7, 5, 2),
    ("UD2", "Seguridad pasiva: almacenamiento y copias de seguridad", 7, 9, 2),
    ("UD3", "Criptografía y aplicaciones criptográficas", 7, 9, 2),
    ("UD4", "Fortificación de hosts y seguridad activa", 8, 12, 2),
    ("UD5", "Seguridad en redes: monitorización, detección y respuesta", 7, 9, 2),
    ("UD6", "Seguridad perimetral: cortafuegos, proxy, VPN y acceso remoto", 9, 14, 2),
    ("UD7", "Alta disponibilidad, virtualización y continuidad de negocio", 7, 9, 2),
]
TOTAL = sum(t + p + e for _, _, t, p, e in UNIDADES)
assert TOTAL == 133, TOTAL

def sesiones():
    d, out = INICIO, []
    while d <= FIN:
        if d.weekday() in HORARIO and d not in NO_LECTIVOS:
            out.append((d, HORARIO[d.weekday()]))
        d += dt.timedelta(days=1)
    return out

def plan():
    ses, acum, fin_ud, k = sesiones(), 0, [], 0
    limites = []
    for c, *_ , t, p, e in [(u[0], 0, u[2], u[3], u[4]) for u in UNIDADES]:
        k += t + p + e; limites.append((c, k))
    filas, h = [], 0
    for d, hs in ses:
        if h >= TOTAL: break
        usa = min(hs, TOTAL - h)
        ud0 = next(c for c, lim in limites if h < lim)
        ud1 = next(c for c, lim in limites if h + usa <= lim)
        filas.append({"fecha": d.isoformat(), "horas": usa, "h_ini": h + 1, "h_fin": h + usa,
                      "ud": ud0 if ud0 == ud1 else f"{ud0}/{ud1}"})
        h += usa
    return filas, h, ses

if __name__ == "__main__":
    filas, h, ses = plan()
    if "--json" in sys.argv:
        print(json.dumps({"filas": filas, "total": h}, ensure_ascii=False, indent=1)); sys.exit()
    print(f"Sesiones disponibles hasta el {FIN}: {len(ses)} · horas disponibles: {sum(x for _, x in ses)}")
    print(f"Horas asignadas: {h} · última sesión: {filas[-1]['fecha']}")
    por_ud = {}
    for f in filas:
        for u in f['ud'].split('/'): por_ud.setdefault(u, []).append(f['fecha'])
    for c, t, *_ in UNIDADES: print(c, por_ud[c][0], '→', por_ud[c][-1])
