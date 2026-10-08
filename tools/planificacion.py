#!/usr/bin/env python3
"""Genera data/planificacion.json: reparto de las 133 h oficiales del módulo 0378 sobre el
calendario escolar 2026/27 a razón de 5 h semanales (1 h cada día lectivo de lunes a viernes).

Uso:  python3 tools/planificacion.py
Si cambia el horario o el calendario, edita HORARIO y NO_LECTIVOS en tools/calendario.py.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from calendario import NO_LECTIVOS, INICIO, FIN, UNIDADES, HORARIO, sesiones
import datetime as dt

HORAS_OFICIALES = 133
assert sum(t + p + e for _, _, t, p, e in UNIDADES) == HORAS_OFICIALES

def main():
    ses = sesiones()
    capacidad = sum(h for _, h in ses)
    horas = []
    for c, _, t, p, e in UNIDADES: horas += [(c, "T")] * t + [(c, "P")] * p + [(c, "E")] * e
    i, dias = 0, []
    uni = {c: {"ini": None, "fin": None} for c, *_ in UNIDADES}
    for d, h in ses:
        if i >= len(horas): break
        trozo = horas[i:i + h]; i += len(trozo)
        c = trozo[0][0]
        u = uni[c]; u["ini"] = u["ini"] or d.isoformat(); u["fin"] = d.isoformat()
        dias.append({"d": d.isoformat(), "k": "lectivo", "u": c, "h": len(trozo), "tp": trozo[0][1], "uu": [c]})
    fin_plan = dias[-1]["d"]
    festivos = [{"d": d.isoformat(), "k": "vacaciones" if "Vacaciones" in m else "festivo", "n": m}
                for d, m in sorted(NO_LECTIVOS.items()) if INICIO <= d <= FIN and d.weekday() < 5]
    unidades = [{"c": c, "n": n, "h": t + p + e, "t": t, "p": p, "e": e, "ini": uni[c]["ini"], "fin": uni[c]["fin"]}
                for c, n, t, p, e in UNIDADES]
    hitos = [{"d": INICIO.isoformat(), "n": "Inicio del curso"}]
    hitos += [{"d": u["fin"], "n": f"Prueba y entrega de la {u['c']}"} for u in unidades]
    hitos.append({"d": FIN.isoformat(), "n": "Fin del curso"})
    out = {"oficial": HORAS_OFICIALES, "semanal": sum(HORARIO.values()), "capacidad": capacidad,
           "reserva": capacidad - HORAS_OFICIALES, "finPlan": fin_plan, "unidades": unidades,
           "dias": sorted(dias + festivos, key=lambda x: x["d"]), "hitos": hitos}
    pathlib.Path(__file__).parent.parent.joinpath("data/planificacion.json").write_text(
        json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Horas disponibles hasta {FIN}: {capacidad} · oficiales: {HORAS_OFICIALES} · reserva: {capacidad - HORAS_OFICIALES}")
    print("Plan completo el", fin_plan)
    for u in unidades: print(u["c"], u["h"], "h", u["ini"], "→", u["fin"])
if __name__ == "__main__": main()
