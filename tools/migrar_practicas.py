#!/usr/bin/env python3
"""Migra las prácticas antiguas (content.es/UD0x/*Practicas.md) al formato de las nuevas páginas
(ficha `practica`, horas por práctica, RA/CE y tabla resumen), con la numeración y el orden
de unidades vigentes (UD5 redes, UD6 perimetral, UD7 alta disponibilidad).

    python3 tools/migrar_practicas.py

Es una herramienta de migración de una sola vez: el resultado se edita ya a mano.
Las horas por práctica suman las horas de prácticas de cada unidad (data/planificacion.json).
"""
import re, pathlib, sys, yaml

R = pathlib.Path(__file__).resolve().parents[1]
C = R / "content.es"
CUR = yaml.safe_load(open(R / "data/curriculo.yaml", encoding="utf8"))

OLD = {
    "UD1": "UD01/UD01 Introduccion Practicas.md",
    "UD3": "UD03/UD3 Criptografía Practicas.md",
    "UD4": "UD04/UD4 Fortificación de Hosts Practicas.md",
    "UD5": "UD06/UD6  Seguridad en Redes Practicas.md",      # redes (antes UD6)
    "UD6": "UD07/UD7 Seguridad Perimetral Practicas.md",     # perímetro (antes UD7)
    "UD6b": "UD06/UD6  Seguridad en Redes Practicas.md",     # SSH, VPN y RADIUS (antes UD6)
    "UD7": "UD05/UD5  Alta Disponibilidad Practicas.md",     # alta disponibilidad (antes UD5)
}
DEST = {"UD1": "ud01-seguridad-informatica", "UD3": "ud03-criptografia", "UD4": "ud04-fortificacion-hosts",
        "UD5": "ud05-seguridad-redes", "UD6": "ud06-seguridad-perimetral", "UD7": "ud07-alta-disponibilidad"}
TITULO = {
    "UD1": ("Introducción a la seguridad, riesgos y marco legal", 5, 14),
    "UD3": ("Criptografía y aplicaciones criptográficas", 9, 18),
    "UD4": ("Fortificación de hosts y seguridad activa", 12, 22),
    "UD5": ("Seguridad en redes: monitorización, detección y respuesta", 9, 18),
    "UD6": ("Seguridad perimetral: cortafuegos, proxy, VPN y acceso remoto", 14, 25),
    "UD7": ("Alta disponibilidad, virtualización y continuidad de negocio", 9, 18),
}
G, A, RT, P = "Guiada", "Autónoma", "Reto", "Proyecto"
# unidad -> lista de (origen, nº antiguo de la práctica o "T" para la tarea evaluable, tipo, horas, nivel, CE, entrega)
PLAN = {
 "UD1": [("UD1", 0, G, 1, 1, "RA1: a, b", "capturas del laboratorio operativo"),
         ("UD1", 1, G, 1, 1, "RA1: c; RA2: h", "inventario en la carpeta de evidencias"),
         ("UD1", 2, G, 1, 2, "RA1: a, g", "línea base y registro de la detección"),
         ("UD1", 3, G, 1, 2, "RA1: e", "política de contraseñas y registro del ataque"),
         ("UD1", 4, A, 0, 1, "RA1: d", "informe de análisis del correo"),
         ("UD1", 5, A, 0, 2, "RA1: c; RA2: b", "informe de vulnerabilidades"),
         ("UD1", 6, RT, 0, 3, "RA1: i", "informe forense con cadena de custodia"),
         ("UD1", 7, P, 1, 3, "RA1: a, c; RA7: f", "plan de gestión de riesgos")],
 "UD3": [("UD3", 1, G, 1, 1, "RA1: g", "salidas de las órdenes"),
         ("UD3", 2, G, 1, 2, "RA1: g", "capturas y análisis del modo ECB"),
         ("UD3", 3, G, 1, 2, "RA2: f", "claves, mensaje cifrado y firma verificada"),
         ("UD3", 4, G, 1, 2, "RA1: e, g", "comparativa de costes y sales"),
         ("UD3", 5, G, 2, 3, "RA2: f; RA3: c", "CA propia y certificados emitidos"),
         ("UD3", 6, G, 2, 2, "RA2: f; RA3: c", "servidor HTTPS verificado"),
         ("UD3", 7, A, 0, 2, "RA3: c", "informe de la configuración TLS"),
         ("UD3", 8, G, 1, 2, "RA2: f", "CRL y comprobación de la revocación")],
 "UD4": [("UD4", 1, G, 1, 1, "RA1: c; RA2: h", "inventario y línea base"),
         ("UD4", 2, G, 2, 2, "RA1: e", "usuarios, sudo y política de contraseñas"),
         ("UD4", 3, G, 2, 2, "RA2: c", "SSH por clave y registro de Fail2ban"),
         ("UD4", 4, G, 1, 2, "RA2: c, h", "reglas del cortafuegos y escaneo"),
         ("UD4", 5, G, 1, 2, "RA1: g; RA2: f", "volumen cifrado y prueba de apertura"),
         ("UD4", 6, G, 1, 3, "RA2: c", "perfil de control de acceso y denegación"),
         ("UD4", 7, G, 1, 2, "RA2: d, e; RA1: i", "reglas de auditoría y análisis antimalware"),
         ("UD4", 8, G, 1, 2, "RA2: b", "informe de Lynis antes y después"),
         ("UD4", 9, G, 1, 3, "RA2: e, i", "agente enrolado y alerta recibida"),
         ("UD4", 10, A, 0, 3, "RA2: c", "informe comparativo con Linux"),
         ("UD4", "T", P, 1, 3, "RA1: e, f, i; RA2: a-e", "informe antes/después")],
 "UD5": [("UD5", 1, G, 2, 2, "RA2: c, d", "capturas de la anomalía ARP/DHCP"),
         ("UD5", 2, G, 2, 3, "RA2: c", "configuración VLAN/ACL y pruebas"),
         ("UD5", 6, G, 2, 3, "RA2: i, c", "regla propia y alerta de Suricata"),
         ("UD5", 7, A, 1, 2, "RA2: d, h", "captura filtrada y análisis"),
         ("UD5", "T", P, 2, 3, "RA2: c, d, h, i", "informe de red segura")],
 "UD6": [("UD6", 1, G, 1, 1, "RA1: h; RA3: a, b", "esquema de zonas y matriz de flujos"),
         ("UD6", 2, G, 2, 3, "RA4: b, c, d", "conjunto de reglas nftables y pruebas"),
         ("UD6", 3, G, 1, 2, "RA4: c, d", "servicio publicado y comprobación desde fuera"),
         ("UD6", 4, A, 0, 2, "RA4: e, g", "registro y diagnóstico"),
         ("UD6", 5, G, 2, 2, "RA5: b, c, d, e, g", "Squid con autenticación y restricciones"),
         ("UD6", 6, G, 1, 3, "RA5: a, f", "proxy inverso con TLS"),
         ("UD6", 7, A, 0, 2, "RA4: f", "informe comparativo de cortafuegos"),
         ("UD6", 8, G, 1, 3, "RA4: g", "prueba de fallo del perímetro"),
         ("UD6b", 3, G, 1, 2, "RA3: c, f", "configuración SSH y pruebas"),
         ("UD6b", 4, G, 2, 3, "RA3: d, e", "túnel WireGuard operativo"),
         ("UD6b", 5, G, 1, 3, "RA3: f, g", "autenticación RADIUS comprobada"),
         ("UD6b", 8, A, 0, 3, "RA3: d", "túnel IPsec sitio a sitio"),
         ("UD6", "T", P, 2, 3, "RA1: h; RA3; RA4; RA5", "informe técnico del perímetro")],
 "UD7": [("UD7", 1, G, 1, 1, "RA6: a, h", "cálculo de disponibilidad y SPOF"),
         ("UD7", 2, G, 1, 2, "RA6: b, f", "RAID 1 con fallo y reconstrucción"),
         ("UD7", 3, G, 1, 2, "RA6: c, d", "servicio de dos nodos operativo"),
         ("UD7", 4, G, 1, 2, "RA6: e", "HAProxy con retirada del nodo caído"),
         ("UD7", 5, G, 1, 3, "RA6: d", "IP virtual y conmutación medida"),
         ("UD7", 6, G, 1, 3, "RA6: d, f", "réplica promocionada"),
         ("UD7", 7, G, 1, 3, "RA6: g", "tabla de interrupción bajo carga"),
         ("UD7", 8, A, 0, 3, "RA6: g", "informe del clúster"),
         ("UD7", 9, A, 0, 3, "RA6: c, g", "informe de HA en Proxmox"),
         ("UD7", "T", P, 2, 3, "RA6: a-i", "informe de arquitectura de alta disponibilidad")],
}

def split_blocks(text):
    """Divide en bloques por encabezados «## » fuera de bloques de código."""
    lines, blocks, cur, fence = text.split("\n"), [], None, False
    pre = []
    for ln in lines:
        if ln.startswith("```"): fence = not fence
        if not fence and ln.startswith("## "):
            cur = [ln]; blocks.append(cur)
        elif cur is None: pre.append(ln)
        else: cur.append(ln)
    return "\n".join(pre), ["\n".join(b).rstrip() for b in blocks]

def clean_title(h):
    t = h[3:].strip()
    t = re.sub(r"^\d+\.\s+", "", t)
    return t

def body_of(block):
    return "\n".join(block.split("\n")[1:]).strip("\n")

def slug(t):
    return re.sub(r"[^\w\- ]", "", t.lower()).replace(" ", "-")

def demote(body):
    """### n.m. Título -> #### Título (fuera de bloques de código); quita separadores finales."""
    out, fence = [], False
    for ln in body.split("\n"):
        if ln.startswith("```"): fence = not fence
        if not fence and ln.startswith("### "):
            ln = "#### " + re.sub(r"^\d+\.\d+\.?\s+", "", ln[4:])
        out.append(ln)
    s = "\n".join(out).rstrip()
    s = re.sub(r"\n+---\s*$", "", s).rstrip()
    return s

def renumber(body, mapa):
    def rep(m):
        k = int(m.group(2))
        return f"{m.group(1)}{mapa[k]}" if k in mapa else m.group(0)
    return re.sub(r"(\b[Pp]ráctica )(\d+)\b(?![.\d])", rep, body)

def ra_union(items):
    d = {}
    for it in items:
        for part in it[5].split(";"):
            m = re.match(r"\s*(RA\d)(?::\s*(.*))?$", part)
            ra, ces = m.group(1), m.group(2)
            if not ces or ces in ("a-e", "a-i"): d[ra] = None
            elif d.get(ra, set()) is not None: d.setdefault(ra, set()).update(c.strip() for c in ces.split(","))
    return " ".join(f'"{ra}"' if d[ra] is None else f'"{ra}:{",".join(sorted(d[ra]))}"' for ra in sorted(d))

def ra_attr(s):
    out = []
    for part in s.split(";"):
        m = re.match(r"\s*(RA\d)(?::\s*(.*))?$", part)
        ra, ces = m.group(1), m.group(2)
        if ces in ("a-e", "a-i"): ces = None
        out.append(f"{ra}:{ces.replace(' ', '')}" if ces else ra)
    return ";".join(out)

def hs(h): return f"{h} h" if h else "0 h · trabajo autónomo"

INTRO = {
 "UD5": "Observación y detección de amenazas de capa 2 y 3, segmentación con VLAN y ACL, detección de intrusiones con Suricata y captura y análisis de tráfico en un laboratorio aislado.",
 "UD6": "Perímetro con WAN, LAN y DMZ en un cortafuegos Linux (nftables), NAT y publicación, proxy directo e inverso, y acceso remoto seguro con SSH, WireGuard y RADIUS, con prueba de fallo del perímetro.",
}
OBJ = {
 "UD5": """- Observar el funcionamiento normal de ARP y DHCP y detectar anomalías con herramientas defensivas.
- Segmentar con VLAN 802.1Q en Linux y aplicar ACL entre segmentos con nftables.
- Desplegar Suricata con reglas propias y comprobar sus alertas.
- Capturar y analizar tráfico con `tcpdump` y Wireshark.""",
}
def build(ud):
    titulo, horasP, horasT = TITULO[ud]
    num = ud[2:]
    items = PLAN[ud]
    assert sum(i[3] for i in items) == horasP, (ud, sum(i[3] for i in items), horasP)
    cache = {}
    def get(src):
        if src not in cache:
            pre, bl = split_blocks((C / OLD[src]).read_text(encoding="utf8"))
            cache[src] = (pre, bl)
        return cache[src]
    pre, blocks = get(ud)
    # intro (cita inicial del documento antiguo)
    intro = INTRO.get(ud) or next((l[2:].strip() for l in pre.split("\n") if l.startswith("> ")), "")
    sect = {}
    for b in blocks:
        t = clean_title(b.split("\n")[0])
        sect[t.split(" ")[0] + (" " + t.split(" ")[1] if t.startswith("Práctica") else "")] = b
    out = [f'---\ntitle: "UD{num} · Prácticas"\nweight: 2\nbookToc: true\n---\n', f"# UD{num} · Prácticas\n"]
    out.append("{{< ra " + ra_union(items) + " >}}\n")
    out.append(intro + "\n" if intro else "")
    # tabla resumen
    out.append("| Práctica | Tipo | Nivel | Horas | CE principales |\n|---|---|---|--:|---|")
    rows = []
    for k, (src, n, tipo, h, niv, ra, ent) in enumerate(items, 1):
        sp, sb = get(src)
        if n == "T":
            b = next(x for x in sb if clean_title(x.split("\n")[0]).startswith("Tarea evaluable"))
            tit = clean_title(b.split("\n")[0])
            tit = re.sub(r"^Tarea evaluable\s*[:\-–]\s*", "", tit); tit = tit[0].upper() + tit[1:]
            head = f"Tarea del proyecto · {tit}"
        else:
            b = next(x for x in sb if re.match(rf"\d+\. Práctica {n}\b", x.split("\n")[0][3:]))
            tit = re.sub(rf"^Práctica {n}\s*[·\-–]\s*", "", clean_title(b.split("\n")[0]))
            head = f"Práctica {num}.{k} · {tit}"
        rows.append((src, n, tipo, h, niv, ra, ent, b, tit, head, k))
        niv_s = "●" * niv + "○" * (3 - niv)
        out.append(f"| [{num}.{k} {tit}](#{slug(head)}) | {tipo} | {niv_s} | {h if h else '—'} | {ra.replace(';', ' ·')} |")
    out.append(f"| **Total** | | | **{horasP} h** | |\n")
    out.append(f"> [!NOTE]\n> Las prácticas con **—** horas son **trabajo autónomo** (fuera del horario) u opcionales: amplían la unidad, pero no restan tiempo a las {horasP} h de prácticas oficiales de la unidad. El resto se realiza en el laboratorio, en las horas indicadas.\n")
    # objetivos / normas / preparación (del documento principal)
    for key in ("Objetivos", "Normas", "Preparación"):
        b = next((v for k2, v in sect.items() if k2.startswith(key)), None)
        if b:
            t = clean_title(b.split("\n")[0])
            cuerpo = OBJ[ud] + "\n\n" + "\n".join(l for l in demote(body_of(b)).split("\n") if l.startswith("> ")) if (key == "Objetivos" and ud in OBJ) else demote(body_of(b))
            if key == "Objetivos" and ud == "UD6": cuerpo = cuerpo.replace("\n\n> [!", "\n- Configurar acceso remoto seguro: SSH avanzado, VPN con WireGuard y autenticación centralizada con RADIUS.\n\n> [!", 1)
            out.append(f"## {t}\n\n{cuerpo}\n")
    if ud == "UD6":
        out.append("> [!NOTE]\n> Las prácticas **6.9 a 6.12** (SSH, WireGuard, RADIUS e IPsec) reutilizan las máquinas y redes de laboratorio de la [UD5](/ud05-seguridad-redes/ud05-practicas/#preparación-del-laboratorio). Si no las tienes, prepáralas primero.\n")
    # prácticas
    for src, n, tipo, h, niv, ra, ent, b, tit, head, k in rows:
        mapa = {}
        for kk, it in enumerate(items, 1):
            if it[0] == src and it[1] != "T": mapa[it[1]] = f"{num}.{kk}"
        body = demote(body_of(b))
        body = re.sub(r"^(\s*\n)+", "", body)
        body = renumber(body, mapa)
        etq = ' etiqueta="Tarea"' if n == "T" else ""
        numv = f"{num}.{k}"
        entorno = "Debian 13 · VirtualBox 7"
        out.append("---\n")
        out.append(f"## {head}\n\n" + "{{< practica" + etq + f' num="{numv}" tipo="{tipo}" duracion="{hs(h)}" nivel="{niv}" ra="{ra_attr(ra)}" entorno="{entorno}" entrega="{ent}" >}}}}\n\n' + body + "\n")
    out.append("---\n")
    # secciones finales
    claves = [("Problemas", "Problemas habituales"), ("Buenas", "Buenas prácticas de seguridad aplicadas"),
                     ("Actividades", "Actividades"), ("Autoevaluación", "Preguntas de autoevaluación"),
                     ("Resumen", "Resumen"), ("Referencias", "Referencias y documentación oficial"), ("Recursos", "Referencias y documentación oficial")]
    if not any(i[1] == "T" for i in items): claves.insert(4, ("Tarea", "Tarea evaluable de la unidad"))
    for key, new in claves:
        b = next((v for k2, v in sect.items() if k2.startswith(key)), None)
        if b and not (key == "Recursos" and any("Referencias" in x for x in out)):
            out.append(f"## {new}\n\n{demote(body_of(b))}\n")
    dest = C / DEST[ud] / f"ud0{num}-practicas.md"
    dest.parent.mkdir(exist_ok=True)
    txt = re.sub(r"\n{3,}", "\n\n", "\n".join(out))
    dest.write_text(txt, encoding="utf8")
    print(ud, "->", dest.relative_to(R), len(txt.splitlines()), "líneas")

if __name__ == "__main__":
    for ud in (sys.argv[1:] or ["UD1", "UD3", "UD4", "UD5", "UD6", "UD7"]):
        build(ud)
