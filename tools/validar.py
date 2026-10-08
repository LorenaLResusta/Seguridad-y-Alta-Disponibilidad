#!/usr/bin/env python3
"""Validador de contenido (sustituye a una compilación de Hugo cuando no está disponible).

    python3 tools/validar.py                       # todo content.es
    python3 tools/validar.py content.es/ud04-*     # solo algunas rutas

Comprueba: cabecera YAML, shortcodes ra/practica/quiz/figura/steps/details/tabs, CE existentes
en data/curriculo.yaml, imágenes, enlaces internos y suma de horas de las prácticas.
"""
import re, sys, glob, pathlib, yaml
R = pathlib.Path(__file__).resolve().parents[1]
CUR = yaml.safe_load(open(R / "data/curriculo.yaml", encoding="utf8"))
CE = {f"{ra}.{k}" for ra, d in CUR.items() for k in d["ce"]}
TIPOS = {"Guiada", "Autónoma", "Reto", "Proyecto"}
errs, warns = [], []

def e(f, m): errs.append(f"{f}: {m}")
def w(f, m): warns.append(f"{f}: {m}")

def check_ra_token(f, tok):
    tok = tok.strip()
    m = re.fullmatch(r"(RA\d)(?::\s*([a-i](?:\s*,\s*[a-i])*)?)?", tok)
    if not m: return e(f, f"referencia RA mal formada: {tok!r}")
    ra, ces = m.group(1), m.group(2)
    if ra not in CUR: return e(f, f"RA inexistente: {ra}")
    for c in re.split(r"\s*,\s*", ces or ""):
        if c and f"{ra}.{c}" not in CE: e(f, f"CE inexistente: {ra}.{c}")

def link_ok(target):
    t = target.split("#")[0].split("?")[0].strip("/")
    if not t: return True
    base = R / "content.es" / t
    return any(p.exists() for p in (base.with_suffix(".md"), base / "_index.md", base.parent / (base.name + ".md")))

def check(path):
    f = str(pathlib.Path(path).relative_to(R)); txt = pathlib.Path(path).read_text(encoding="utf8")
    m = re.match(r"---\n(.*?)\n---\n", txt, re.S)
    if not m: return e(f, "falta la cabecera YAML")
    try:
        fm = yaml.safe_load(m.group(1)); assert "title" in fm and "weight" in fm
    except Exception as ex: e(f, f"cabecera YAML no válida ({ex})")
    body = txt[m.end():]
    # sin código: los ejemplos de shortcodes dentro de bloques ``` no cuentan
    plain = re.sub(r"```.*?```", "", body, flags=re.S)
    for m in re.finditer(r"\{\{<\s*ra\s+(.*?)\s*>\}\}", plain):
        for tok in re.findall(r'"([^"]+)"', m.group(1)): check_ra_token(f, tok)
    horas = 0
    for m in re.finditer(r"\{\{<\s*practica\s+(.*?)\s*>\}\}", plain, re.S):
        a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        for k in ("num", "tipo", "duracion", "nivel", "ra"):
            if k not in a: e(f, f"practica sin '{k}': {m.group(1)[:60]}")
        if a.get("tipo") not in TIPOS: e(f, f"tipo de práctica no válido: {a.get('tipo')}")
        if a.get("nivel") not in {"1", "2", "3"}: e(f, f"nivel no válido: {a.get('nivel')}")
        mh = re.fullmatch(r"(\d+(?:[.,]\d+)?)\s*h(?:\s*·\s*trabajo autónomo)?", a.get("duracion", ""))
        if mh: horas += float(mh.group(1).replace(",", "."))
        else: e(f, f"duración debe expresarse en horas (p. ej. '2 h'): {a.get('duracion')!r}")
        for tok in re.split(r";\s*", a.get("ra", "")): 
            if tok.strip(): check_ra_token(f, tok.replace(" ", "", 1) if ":" in tok else tok)
    for m in re.finditer(r"\{\{<\s*quiz\s*>\}\}(.*?)\{\{<\s*/quiz\s*>\}\}", body, re.S):
        try:
            q = yaml.safe_load(m.group(1))
            for i, it in enumerate(q, 1):
                assert {"q", "options", "answer", "explain"} <= set(it), f"pregunta {i}: faltan campos"
                assert isinstance(it["answer"], int) and 0 <= it["answer"] < len(it["options"]), f"pregunta {i}: answer fuera de rango"
        except Exception as ex: e(f, f"quiz no válido: {ex}")
    for m in re.finditer(r"\{\{<\s*figura\s+(.*?)\s*>\}\}", plain):
        s = re.search(r'src="([^"]+)"', m.group(1))
        if not s or not (R / "assets/images" / s.group(1)).exists(): e(f, f"figura inexistente: {s and s.group(1)}")
    for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)", plain):
        u = m.group(1)
        if u.startswith("http"): continue
        cand = [R / "static" / u.lstrip("/"), R / "assets" / u.lstrip("/"), R / "assets/images" / u.removeprefix("images/"), pathlib.Path(path).parent / u]
        if not any(c.exists() for c in cand): e(f, f"imagen inexistente: {u}")
    for tag in ("steps", "details", "tabs", "tab"):
        o = len(re.findall(r"\{\{%\s*" + tag + r"[\s%]", plain)) + len(re.findall(r"\{\{<\s*" + tag + r"[\s>]", plain))
        c = len(re.findall(r"\{\{%\s*/" + tag + r"\s*%\}\}", plain)) + len(re.findall(r"\{\{<\s*/" + tag + r"\s*>\}\}", plain))
        if o != c: e(f, f"shortcode '{tag}' desbalanceado ({o} aperturas, {c} cierres)")
    for m in re.finditer(r"\]\((/[^)\s]*)\)", plain):
        if not link_ok(m.group(1)): e(f, f"enlace interno roto: {m.group(1)}")
    if re.search(r"\{\{<\s*(sgbd)\b", plain): e(f, "usa el shortcode 'sgbd' (usa 'sw')")
    return f, horas

if __name__ == "__main__":
    args = sys.argv[1:] or [str(R / "content.es")]
    files = []
    for a in args:
        for p in glob.glob(a):
            pp = pathlib.Path(p)
            files += sorted(pp.rglob("*.md")) if pp.is_dir() else [pp]
    for p in files:
        r = check(str(pathlib.Path(p).resolve()))
        if r and r[1]: print(f"  horas de prácticas en {r[0]}: {r[1]:g} h")
    errs[:] = list(dict.fromkeys(errs)); warns[:] = list(dict.fromkeys(warns))
    for x in warns: print("AVISO", x)
    for x in errs: print("ERROR", x)
    print(f"{len(files)} ficheros · {len(errs)} errores · {len(warns)} avisos")
    sys.exit(1 if errs else 0)
