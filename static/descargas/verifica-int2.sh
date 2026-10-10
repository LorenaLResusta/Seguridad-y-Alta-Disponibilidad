#!/usr/bin/env bash
# verifica-int2.sh · Comprobaciones automáticas de la práctica integradora INT-2 (UD05 a UD07)
# Módulo 0378 Seguridad y alta disponibilidad · 2.º ASIR · curso 2026/27
#
# Uso (como root, en cada máquina que corresponda):
#   sudo ./verifica-int2.sh fw APELLIDO     # en fw01  (UD05 y UD06: Suricata, nftables, WireGuard)
#   sudo ./verifica-int2.sh lb APELLIDO     # en lb01  (UD07: HAProxy, balanceo y prueba de fallo)
#
# Este script SOLO LEE el estado del sistema: no instala ni cambia nada. Cada comprobación
# vale 0,5 puntos (fw: 10 comprobaciones; lb: 6). Genera  evidencias-INT2-ROL-APELLIDO.txt
set -u
export LC_ALL=C

[ "$(id -u)" -eq 0 ] || { echo "Ejecútalo con sudo:  sudo $0 fw|lb APELLIDO"; exit 2; }
ROL="${1:-}"; APELLIDO="${2:-}"
[[ "$ROL" == fw || "$ROL" == lb ]] || { echo "Uso:  sudo $0 fw|lb APELLIDO"; exit 2; }
[[ "$APELLIDO" =~ ^[A-Za-z][A-Za-z0-9_-]{1,30}$ ]] || { echo "Uso:  sudo $0 $ROL APELLIDO   (solo letras, números, - o _)"; exit 2; }

DIR_INT=/srv/int2                    # documentos de la práctica (prueba-fallo.csv)
RTO_MAX=300                          # RTO exigido: 5 minutos = 300 s
SALIDA="evidencias-INT2-${ROL}-${APELLIDO}.txt"

TMP=$(mktemp); trap 'rm -f "$TMP"' EXIT
say() { printf '%s\n' "$*" >> "$TMP"; }
OK=0; TOTAL=0
chk() {  # chk ID "qué se comprueba" "pista si falla" función
  local id="$1" desc="$2" hint="$3"; shift 3
  TOTAL=$((TOTAL + 1))
  if "$@" >/dev/null 2>&1; then OK=$((OK + 1)); say "[OK]     $id  $desc"
  else say "[FALLA]  $id  $desc   -> $hint"; fi
}

# ---------- fw01 · UD05 detección ----------
RULES=/var/lib/suricata/rules/local.rules
f_S1() {  # regla propia de Suricata (sid 1000000-1999999) activa, no comentada
  grep -E '^(alert|drop)[[:space:]].*sid:[[:space:]]*1[0-9]{6}[[:space:]]*;' "$RULES" | grep -q .
}
f_S2() {  # Suricata en marcha y configuración válida
  systemctl is-active --quiet suricata && suricata -T -c /etc/suricata/suricata.yaml
}
f_S3() {  # alguna regla propia ha generado una alerta registrada en fast.log
  local s
  for s in $(grep -hoE '^(alert|drop)[[:space:]].*sid:[[:space:]]*1[0-9]{6}' "$RULES" | grep -oE '1[0-9]{6}$'); do
    grep -qE "\[1:${s}:[0-9]+\]" /var/log/suricata/fast.log && return 0
  done
  return 1
}
# ---------- fw01 · UD06 perímetro ----------
f_F1() { nft list ruleset | grep -qE 'hook input .*policy drop'; }
f_F2() { nft list ruleset | grep -qE 'hook forward .*policy drop'; }
f_F3() { nft list ruleset | grep -q 'dnat to'; }
f_F4() { nft list ruleset | grep -qE 'masquerade|snat to'; }
f_F5() {  # túnel WireGuard con al menos un apretón de manos (handshake) con un par
  wg show all latest-handshakes | awk '$3 > 0 { f = 1 } END { exit !f }'
}
f_F6() {  # endurecimiento TCP/IP: reenvío activo, syncookies y rp_filter
  [ "$(sysctl -n net.ipv4.ip_forward)" = 1 ] && [ "$(sysctl -n net.ipv4.tcp_syncookies)" = 1 ] &&
  [ "$(sysctl -n net.ipv4.conf.all.rp_filter)" != 0 ]
}
f_F7() { nft list ruleset | grep -qE '(^|[[:space:]])log([[:space:]]|$)'; }   # alguna regla registra (log)
# ---------- lb01 · UD07 alta disponibilidad ----------
CFG=/etc/haproxy/haproxy.cfg
f_H1() { systemctl is-active --quiet haproxy && haproxy -c -f "$CFG"; }
f_H2() { [ "$(grep -cE '^[[:space:]]*server[[:space:]].*[[:space:]]check' "$CFG")" -ge 2 ]; }
f_H3() {  # los dos servidores del backend están UP en este momento (requiere socat y stats socket)
  echo "show stat" | socat stdio /run/haproxy/admin.sock \
    | awk -F, '$2 != "FRONTEND" && $2 != "BACKEND" && $18 == "UP" { n++ } END { exit !(n >= 2) }'
}
f_H4() {  # prueba-fallo.csv: >= 2 fallos medidos y todos recuperados dentro del RTO
  tr -d '\r' < "$DIR_INT/prueba-fallo.csv" | awk -F, -v max="$RTO_MAX" '
    NR == 1 { next }
    NF >= 4 { n++; if ($4 + 0 > 0 && $4 + 0 <= max) ok++ }
    END { exit !(n >= 2 && ok == n) }'
}
f_H5() {  # el reparto funciona: en 20 peticiones responden los dos servidores web
  local n; n=$(for _ in $(seq 20); do curl -s --max-time 3 http://127.0.0.1/; done | grep -oE 'web0[12]' | sort -u | wc -l)
  [ "$n" -eq 2 ]
}
f_H6() {  # el balanceador publica HTTPS (certificado servido en 443)
  echo | timeout 10 openssl s_client -connect 127.0.0.1:443 2>/dev/null | grep -q 'BEGIN CERTIFICATE'
}

say "PRACTICA: INT-2 (UD05-UD07) · rol $ROL · modulo 0378 · curso 2026/27"
say "ALUMNO:   $APELLIDO"
say "MAQUINA:  $(hostname) · $(. /etc/os-release && echo "$PRETTY_NAME") · kernel $(uname -r)"
say "ID-VM:    $(sha256sum /etc/machine-id | cut -c1-12)"
say "FECHA:    $(date -Is)"
say ""
if [ "$ROL" = fw ]; then
  for h in nft wg suricata sysctl; do command -v "$h" >/dev/null 2>&1 || say "AVISO:    falta la orden '$h'"; done
  say "--- UD05 Deteccion"
  chk S1 "Regla propia de Suricata (sid 1000000-1999999)"        "edita $RULES"                          f_S1
  chk S2 "Suricata activo y configuracion valida (suricata -T)"  "sudo suricata -T -c /etc/suricata/suricata.yaml" f_S2
  chk S3 "Alerta de una regla propia en fast.log"                "genera trafico que la dispare"         f_S3
  say "--- UD06 Perimetro"
  chk F1 "nftables: cadena input con policy drop"                "type filter hook input ... policy drop;"   f_F1
  chk F2 "nftables: cadena forward con policy drop"              "type filter hook forward ... policy drop;" f_F2
  chk F3 "Publicacion de un servicio con DNAT"                   "regla dnat to <ip:puerto>"             f_F3
  chk F4 "Salida a Internet con masquerade o snat"               "regla masquerade en postrouting"       f_F4
  chk F5 "WireGuard con handshake de un par"                     "sudo wg show; conecta un cliente"      f_F5
  chk F6 "ip_forward=1, tcp_syncookies=1 y rp_filter activo"     "sysctl en /etc/sysctl.d/"              f_F6
  chk F7 "Alguna regla del cortafuegos registra con log"         "drop con log prefix"                   f_F7
else
  for h in haproxy socat curl openssl; do command -v "$h" >/dev/null 2>&1 || say "AVISO:    falta la orden '$h'"; done
  say "--- UD07 Alta disponibilidad"
  chk H1 "HAProxy activo y configuracion valida"                 "haproxy -c -f $CFG"                    f_H1
  chk H2 "Al menos 2 servidores con 'check' (comprobacion de salud)" "server webXX ... check"            f_H2
  chk H3 "Los 2 servidores del backend estan UP ahora"           "socat + stats socket; arranca web01 y web02" f_H3
  chk H4 "prueba-fallo.csv: >= 2 fallos recuperados en <= ${RTO_MAX} s" "completa $DIR_INT/prueba-fallo.csv" f_H4
  chk H5 "Reparto: en 20 peticiones responden web01 y web02"     "cada web debe mostrar su nombre"       f_H5
  chk H6 "El balanceador sirve HTTPS en 443"                     "bind :443 ssl crt ..."                 f_H6
fi
say ""
say "PUNTOS_AUTO: $OK/$TOTAL  (cada comprobacion = 0,5 -> $(awk -v o="$OK" 'BEGIN { printf "%.1f", o * 0.5 }') puntos en esta maquina)"

tee "$SALIDA" < "$TMP"
printf 'FIRMA: %s\n' "$(sha256sum "$TMP" | cut -d' ' -f1)" | tee -a "$SALIDA"
echo "Fichero generado: $(pwd)/$SALIDA"
