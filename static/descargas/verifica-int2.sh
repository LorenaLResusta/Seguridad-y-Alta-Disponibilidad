#!/usr/bin/env bash
# verifica-int2.sh · Comprobaciones automáticas de la práctica integradora INT-2 (UD05 a UD07)
# Módulo 0378 Seguridad y alta disponibilidad · 2.º ASIR · curso 2026/27
#
# Uso (como root, en la máquina fw01 de la práctica, Debian 13):   sudo ./verifica-int2.sh APELLIDO
#
# Este script SOLO LEE el estado del sistema: no instala ni cambia nada. Se ejecuta en UNA sola
# máquina (fw01) y genera UN solo fichero:  evidencias-INT2-APELLIDO.txt
# Son 10 comprobaciones de 0,8 puntos (10 x 0,8 = 8,0 puntos).
set -u
export LC_ALL=C

[ "$(id -u)" -eq 0 ] || { echo "Ejecútalo con sudo:  sudo $0 APELLIDO"; exit 2; }
APELLIDO="${1:-}"
[[ "$APELLIDO" =~ ^[A-Za-z][A-Za-z0-9_-]{1,30}$ ]] || { echo "Uso:  sudo $0 APELLIDO   (solo letras, números, - o _)"; exit 2; }

# Rutas y nombres que fija el enunciado de la práctica
DIR_INT=/srv/int2                                  # documentos de la práctica (prueba-fallo.csv)
RULES=/var/lib/suricata/rules/local.rules          # reglas propias de Suricata
SURI_YAML=/etc/suricata/suricata.yaml
FASTLOG=/var/log/suricata/fast.log
CFG=/etc/haproxy/haproxy.cfg
SOCK=/run/haproxy/admin.sock                       # socket de administración de HAProxy
RTO_MAX=300                                        # RTO exigido: 5 minutos = 300 s
PUNTOS=0,8                                         # valor de cada comprobación
SALIDA="evidencias-INT2-${APELLIDO}.txt"

TMP=$(mktemp); trap 'rm -f "$TMP"' EXIT
say() { printf '%s\n' "$*" >> "$TMP"; }
OK=0; TOTAL=0
chk() {  # chk ID "qué se comprueba" "pista si falla" función
  local id="$1" desc="$2" hint="$3"; shift 3
  TOTAL=$((TOTAL + 1))
  if "$@" >/dev/null 2>&1; then OK=$((OK + 1)); say "[OK]     $id  $desc"
  else say "[FALLA]  $id  $desc   -> $hint"; fi
}

# Lee "show stat" del socket de HAProxy (socat o, si no está, nc -U)
hap_stat() {
  if command -v socat >/dev/null 2>&1; then echo "show stat" | socat stdio "$SOCK"
  else echo "show stat" | nc -U -w2 "$SOCK"; fi
}
# Cuenta los servidores (no FRONTEND/BACKEND) que cumplen una condición sobre una columna por NOMBRE
# (la cabecera de "show stat" empieza por "# pxname,svname,..."): evita depender de la posición.
#   hap_servers status UP      -> servidores con status UP
#   hap_servers chkdown 1      -> servidores con chkdown >= 1 (veces que han pasado de UP a DOWN)
hap_servers() {
  local col="$1" val="$2"
  hap_stat | awk -F, -v col="$col" -v val="$val" '
    NR == 1 { sub(/^# */, "", $1); for (i = 1; i <= NF; i++) if ($i == col) c = i; next }
    c && $2 != "FRONTEND" && $2 != "BACKEND" && NF > 1 {
      if (col == "status" ? $c == val : ($c + 0) >= (val + 0)) n++
    }
    END { print n + 0 }'
}

# ---------- UD05 · Detección (Suricata) ----------
f_S1() {  # regla propia (sid 1000000-1999999) activa, no comentada, y cargada desde suricata.yaml
  grep -E '^(alert|drop)[[:space:]].*sid:[[:space:]]*1[0-9]{6}[[:space:]]*;' "$RULES" | grep -q . &&
  grep -Eq '^[[:space:]]*-[[:space:]]*local\.rules' "$SURI_YAML"
}
f_S2() {  # Suricata en marcha y una regla propia ha generado una alerta registrada en fast.log
  local s
  systemctl is-active --quiet suricata || return 1
  for s in $(grep -hoE '^(alert|drop)[[:space:]].*sid:[[:space:]]*1[0-9]{6}' "$RULES" | grep -oE '1[0-9]{6}$'); do
    grep -qE "\[1:${s}:[0-9]+\]" "$FASTLOG" && return 0
  done
  return 1
}
# ---------- UD06 · Perímetro (nftables) ----------
f_F1() { nft list ruleset | grep -qE 'hook input .*policy drop'; }
f_F2() { nft list ruleset | grep -qE 'hook forward .*policy drop'; }
# En tablas "inet" nft escribe "dnat ip to"; en tablas "ip", "dnat to". "redirect" es un DNAT hacia la propia máquina.
f_F3() { nft list ruleset | grep -qE 'dnat( ip6?)? to|redirect( to)?'; }
f_F4() { nft list ruleset | grep -qE 'masquerade|snat( ip6?)? to'; }
# ---------- UD07 · Alta disponibilidad (HAProxy) ----------
f_H1() {  # HAProxy activo, configuración válida y al menos 2 servidores con comprobación de salud
  systemctl is-active --quiet haproxy && haproxy -c -f "$CFG" &&
  [ "$(grep -cE '^[[:space:]]*server[[:space:]].*[[:space:]]check' "$CFG")" -ge 2 ]
}
f_H2() { [ "$(hap_servers status UP)" -ge 2 ]; }   # los dos servidores están UP ahora mismo
f_H3() {  # el reparto funciona: en 20 peticiones responden los dos servidores web
  local n; n=$(for _ in $(seq 20); do curl -s --max-time 3 http://127.0.0.1/; done | grep -oE 'web0[12]' | sort -u | wc -l)
  [ "$n" -eq 2 ]
}
f_H4() {  # prueba de fallo: CSV correcto (web01 y web02, <= RTO) y HAProxy ha visto caer a los dos servidores
  tr -d '\r' < "$DIR_INT/prueba-fallo.csv" | awk -F, -v max="$RTO_MAX" '
    NR == 1 { next }
    NF >= 4 { n++; if ($4 + 0 > 0 && $4 + 0 <= max) ok++; if ($1 == "web01") a = 1; if ($1 == "web02") b = 1 }
    END { exit !(n >= 2 && ok == n && a && b) }' &&
  [ "$(hap_servers chkdown 1)" -ge 2 ]
}

# ---------- Informe ----------
say "PRACTICA: INT-2 (UD05-UD07) · modulo 0378 · curso 2026/27"
say "ALUMNO:   $APELLIDO"
say "MAQUINA:  $(hostname) · $(. /etc/os-release && echo "$PRETTY_NAME") · kernel $(uname -r)"
say "ID-VM:    $(sha256sum /etc/machine-id | cut -c1-12)"
say "FECHA:    $(date -Is)"
say ""
for h in nft suricata haproxy curl; do command -v "$h" >/dev/null 2>&1 || say "AVISO:    falta la orden '$h' (la comprobacion asociada fallara)"; done
command -v socat >/dev/null 2>&1 || command -v nc >/dev/null 2>&1 || say "AVISO:    falta 'socat' (sudo apt install socat): H2 y H4 lo necesitan"
say "--- UD05 Deteccion"
chk S1 "Regla propia de Suricata (sid 1000000-1999999) cargada"      "edita $RULES y anade '- local.rules' en rule-files" f_S1
chk S2 "Suricata activo y con una alerta de tu regla en fast.log"    "genera trafico que dispare tu regla"      f_S2
say "--- UD06 Perimetro"
chk F1 "nftables: cadena input con policy drop"                      "type filter hook input ... policy drop;"   f_F1
chk F2 "nftables: cadena forward con policy drop"                    "type filter hook forward ... policy drop;" f_F2
chk F3 "Publicacion de la web con DNAT (o redirect)"                 "regla dnat to / redirect to en prerouting"  f_F3
chk F4 "Salida de la DMZ con masquerade o snat"                      "regla masquerade en postrouting"           f_F4
say "--- UD07 Alta disponibilidad"
chk H1 "HAProxy activo, configuracion valida y 2 servidores con check" "haproxy -c -f $CFG; server webXX ... check" f_H1
chk H2 "Los 2 servidores del backend estan UP ahora"                 "arranca web01 y web02; revisa $SOCK"        f_H2
chk H3 "Reparto: en 20 peticiones responden web01 y web02"           "balance roundrobin y cada web muestra su nombre" f_H3
chk H4 "prueba-fallo.csv de web01 y web02 (<= ${RTO_MAX} s) y caida vista por HAProxy" "completa el CSV y NO recargues HAProxy despues de la prueba" f_H4
say ""
# Dato informativo para la correccion de la pregunta P3: el peor tiempo de recuperacion medido
RTO_PEOR=$(tr -d '\r' < "$DIR_INT/prueba-fallo.csv" 2>/dev/null | awk -F, 'NR > 1 && ($4 + 0) > m { m = $4 + 0 } END { print m + 0 }')
say "RTO_PEOR_MEDIDO: ${RTO_PEOR} s (objetivo: <= ${RTO_MAX} s)"
say "PUNTOS_AUTO: $OK/$TOTAL  (cada comprobacion = $PUNTOS -> $(awk -v o="$OK" 'BEGIN { printf "%.1f", o * 0.8 }') de 8,0 puntos)"

tee "$SALIDA" < "$TMP"
printf 'FIRMA: %s\n' "$(sha256sum "$TMP" | cut -d' ' -f1)" | tee -a "$SALIDA"
echo "Fichero generado: $(pwd)/$SALIDA"
