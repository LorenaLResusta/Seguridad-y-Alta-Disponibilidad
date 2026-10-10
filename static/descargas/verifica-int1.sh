#!/usr/bin/env bash
# verifica-int1.sh · Comprobaciones automáticas de la práctica integradora INT-1 (UD01 a UD04)
# Módulo 0378 Seguridad y alta disponibilidad · 2.º ASIR · curso 2026/27
#
# Uso (en la máquina virtual srv-clinica, Debian 13):   sudo ./verifica-int1.sh APELLIDO
#
# Este script SOLO LEE el estado del sistema: no instala ni cambia nada (salvo ficheros
# temporales en /tmp que borra al terminar). Cada comprobación vale 0,5 puntos.
# Genera el fichero  evidencias-INT1-APELLIDO.txt  en el directorio actual.
set -u
export LC_ALL=C

[ "$(id -u)" -eq 0 ] || { echo "Ejecútalo con sudo:  sudo $0 APELLIDO"; exit 2; }
APELLIDO="${1:-}"
[[ "$APELLIDO" =~ ^[A-Za-z][A-Za-z0-9_-]{1,30}$ ]] || { echo "Uso:  sudo $0 APELLIDO   (solo letras, números, - o _)"; exit 2; }

# Rutas y nombres que fija el enunciado de la práctica
DIR_INT=/srv/int1                    # documentos de la práctica
DATOS=/srv/datos                     # volumen RAID 5
REPO=/backup/repo                    # repositorio de restic
PASS_RESTIC=/root/.restic-pass        # fichero con la contraseña del repositorio
CA_DIR=/etc/ssl/clinica              # ca.crt y servidor.crt
FQDN=intranet.clinica.lan            # nombre del servicio HTTPS
SALIDA="evidencias-INT1-${APELLIDO}.txt"

TMP=$(mktemp); trap 'rm -f "$TMP"' EXIT
say() { printf '%s\n' "$*" >> "$TMP"; }
OK=0; TOTAL=0

# chk ID "qué se comprueba" "pista si falla" función
chk() {
  local id="$1" desc="$2" hint="$3"; shift 3
  TOTAL=$((TOTAL + 1))
  if "$@" >/dev/null 2>&1; then OK=$((OK + 1)); say "[OK]     $id  $desc"
  else say "[FALLA]  $id  $desc   -> $hint"; fi
}

# ---------- UD01 · Diagnóstico ----------
f_A1() {  # matriz de riesgos: cabecera exacta, al menos 8 filas y riesgo = probabilidad x impacto (1 a 5)
  local f="$DIR_INT/matriz-riesgos.csv"; [ -f "$f" ] || return 1
  head -n1 "$f" | tr -d '\r' | grep -qx 'activo,amenaza,probabilidad,impacto,riesgo,tratamiento' || return 1
  tail -n +2 "$f" | tr -d '\r' | awk -F, '
    NF > 0 { n++ }
    NF >= 6 && $3 >= 1 && $3 <= 5 && $4 >= 1 && $4 <= 5 && $5 == $3 * $4 { ok++ }
    END { exit !(n >= 8 && ok == n) }'
}
f_A3() {  # política de contraseñas: longitud mínima de 12 o más en pwquality
  cat /etc/security/pwquality.conf /etc/security/pwquality.conf.d/*.conf 2>/dev/null \
    | grep -E '^[[:space:]]*minlen[[:space:]]*=' | tail -n1 \
    | awk -F= '{ v = $2 + 0 } END { exit !(NR > 0 && v >= 12) }'
}
f_A4() {  # integridad: SHA256SUMS incluye la matriz y todos los hashes coinciden
  ( cd "$DIR_INT" && [ -f SHA256SUMS ] && grep -q 'matriz-riesgos.csv' SHA256SUMS && sha256sum -c --quiet SHA256SUMS )
}
# ---------- UD02 · Protección de los datos ----------
f_B1() {  # RAID 5 con 3 discos activos y 1 de reserva
  local d; d=$(mdadm --detail /dev/md0 2>/dev/null) || return 1
  grep -q 'Raid Level : raid5' <<<"$d" && grep -q 'Active Devices : 3' <<<"$d" && grep -q 'Spare Devices : 1' <<<"$d"
}
f_B2() {  # /srv/datos montado desde md0 y persistente en fstab, con datos
  [ "$(findmnt -n -o SOURCE "$DATOS" 2>/dev/null)" = "/dev/md0" ] || return 1
  grep -qE "^[^#]*[[:space:]]$DATOS[[:space:]]" /etc/fstab || return 1
  [ "$(find "$DATOS" -type f 2>/dev/null | wc -l)" -ge 5 ]
}
f_B3() {  # repositorio restic íntegro
  RESTIC_PASSWORD_FILE="$PASS_RESTIC" restic -r "$REPO" check
}
f_B4() {  # restauración en una ruta distinta idéntica a los datos actuales
  local t r; t=$(mktemp -d /tmp/int1-rest.XXXXXX) || return 1
  if RESTIC_PASSWORD_FILE="$PASS_RESTIC" restic -r "$REPO" restore latest --target "$t"; then
    diff -r "$DATOS" "$t$DATOS"; r=$?
  else r=1; fi
  rm -rf "$t"; return $r
}
# ---------- UD03 · PKI y HTTPS ----------
f_C1() {  # CA propia cuyo nombre incluye tu apellido
  openssl x509 -in "$CA_DIR/ca.crt" -noout -subject | grep -qiE "CN ?= ?CA-${APELLIDO}( |,|$)"
}
f_C2() {  # certificado del servidor firmado por esa CA y con el nombre en subjectAltName
  openssl verify -CAfile "$CA_DIR/ca.crt" "$CA_DIR/servidor.crt" | grep -q ': OK' &&
  openssl x509 -in "$CA_DIR/servidor.crt" -noout -ext subjectAltName | grep -q "DNS:$FQDN"
}
f_C3() {  # Nginx responde en 443 con TLS 1.3 y la cadena se verifica contra la CA propia
  echo | timeout 10 openssl s_client -connect 127.0.0.1:443 -servername "$FQDN" -tls1_3 \
    -CAfile "$CA_DIR/ca.crt" -verify_hostname "$FQDN" 2>&1 | grep -q 'Verification: OK'
}
f_C4() {  # Nginx solo admite TLS 1.2 y 1.3 (ni TLSv1 ni TLSv1.1)
  local p; p=$(nginx -T 2>/dev/null | grep -E '^[[:space:]]*ssl_protocols' | head -n1)
  [ -n "$p" ] || return 1
  ! grep -qE 'TLSv1([[:space:];]|\.1)' <<<"$p" && grep -q 'TLSv1.3' <<<"$p"
}
# ---------- UD04 · Fortificación ----------
f_D1() {  # SSH solo con clave y sin acceso directo de root
  local c; c=$(sshd -T 2>/dev/null) || return 1
  grep -qx 'passwordauthentication no' <<<"$c" && grep -qx 'pubkeyauthentication yes' <<<"$c" && grep -qx 'permitrootlogin no' <<<"$c"
}
f_D2() {  # UFW activo, entrada denegada por defecto y solo SSH y HTTPS permitidos explícitamente
  local s; s=$(ufw status verbose 2>/dev/null) || return 1
  grep -q 'Status: active' <<<"$s" && grep -q 'Default: deny (incoming)' <<<"$s" &&
  grep -E '^(22|OpenSSH)([^0-9]|$)' <<<"$s" | grep -q ALLOW &&
  grep -E '^443([^0-9]|$)' <<<"$s" | grep -q ALLOW
}
f_D3() {  # Fail2ban activo con la cárcel (jail) sshd
  systemctl is-active --quiet fail2ban && fail2ban-client status sshd
}
f_D4() {  # auditd activo con una regla de vigilancia sobre /etc/passwd o /etc/shadow
  systemctl is-active --quiet auditd && auditctl -l | grep -qE '/etc/(passwd|shadow)'
}
f_D5() {  # Lynis: el índice de fortificación mejora al menos 10 puntos
  local a d
  a=$(grep -m1 '^hardening_index=' "$DIR_INT/lynis-antes.dat" 2>/dev/null | cut -d= -f2)
  d=$(grep -m1 '^hardening_index=' "$DIR_INT/lynis-despues.dat" 2>/dev/null | cut -d= -f2)
  [[ "$a" =~ ^[0-9]+$ && "$d" =~ ^[0-9]+$ ]] && [ $((d - a)) -ge 10 ]
}

# ---------- Informe ----------
say "PRACTICA: INT-1 (UD01-UD04) · modulo 0378 · curso 2026/27"
say "ALUMNO:   $APELLIDO"
say "MAQUINA:  $(hostname) · $(. /etc/os-release && echo "$PRETTY_NAME") · kernel $(uname -r)"
say "ID-VM:    $(sha256sum /etc/machine-id | cut -c1-12)"
say "FECHA:    $(date -Is)"
say ""
for h in mdadm restic openssl nginx sshd ufw fail2ban-client auditctl; do
  command -v "$h" >/dev/null 2>&1 || say "AVISO:    falta la orden '$h' (la comprobación asociada fallará)"
done
say "--- UD01 Diagnostico"
chk A1 "Matriz de riesgos valida (>= 8 filas, riesgo = prob x impacto)" "revisa $DIR_INT/matriz-riesgos.csv" f_A1
chk A3 "Politica de contrasenas: minlen >= 12 en pwquality"            "edita /etc/security/pwquality.conf"        f_A3
chk A4 "SHA256SUMS verifica la matriz de riesgos"                       "genera el fichero con sha256sum en $DIR_INT" f_A4
say "--- UD02 Proteccion de los datos"
chk B1 "RAID 5 con 3 discos activos + 1 de reserva (md0)"               "mdadm --detail /dev/md0"                    f_B1
chk B2 "/srv/datos montado desde md0, en fstab y con datos"             "findmnt /srv/datos; revisa /etc/fstab"      f_B2
chk B3 "Repositorio restic integro (restic check)"                      "restic -r $REPO check"                      f_B3
chk B4 "Restauracion en otra ruta identica a /srv/datos"                "haz una copia NUEVA tras el ultimo cambio"  f_B4
say "--- UD03 PKI y HTTPS"
chk C1 "CA propia con CN=CA-$APELLIDO"                                  "openssl x509 -in $CA_DIR/ca.crt -noout -subject" f_C1
chk C2 "Certificado firmado por la CA y con SAN $FQDN"                  "openssl verify y -ext subjectAltName"       f_C2
chk C3 "HTTPS en 443 con TLS 1.3 y cadena verificada"                   "openssl s_client -tls1_3 -CAfile ca.crt"    f_C3
chk C4 "Nginx solo con TLS 1.2 y 1.3"                                   "ssl_protocols TLSv1.2 TLSv1.3;"             f_C4
say "--- UD04 Fortificacion"
chk D1 "SSH solo con clave y sin root (sshd -T)"                        "PasswordAuthentication no; PermitRootLogin no" f_D1
chk D2 "UFW activo, deny incoming y permitidos 22 y 443"                "ufw status verbose"                         f_D2
chk D3 "Fail2ban activo con jail sshd"                                  "systemctl status fail2ban"                  f_D3
chk D4 "auditd activo con regla sobre /etc/passwd o /etc/shadow"        "auditctl -l"                                f_D4
chk D5 "Lynis: mejora de al menos 10 puntos"                            "guarda lynis-antes.dat y lynis-despues.dat"  f_D5
say ""
say "PUNTOS_AUTO: $OK/$TOTAL  (cada comprobacion = 0,5 -> $(awk -v o="$OK" 'BEGIN { printf "%.1f", o * 0.5 }') de 8,0 puntos)"

tee "$SALIDA" < "$TMP"
printf 'FIRMA: %s\n' "$(sha256sum "$TMP" | cut -d' ' -f1)" | tee -a "$SALIDA"
echo "Fichero generado: $(pwd)/$SALIDA"
