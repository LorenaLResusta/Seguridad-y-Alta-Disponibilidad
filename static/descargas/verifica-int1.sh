#!/usr/bin/env bash
# verifica-int1.sh · Comprobaciones automáticas de la práctica integradora INT-1 (UD01 a UD04)
# Módulo 0378 Seguridad y alta disponibilidad · 2.º ASIR · curso 2026/27
#
# Uso (en la máquina virtual srv-clinica, Debian 13):   sudo ./verifica-int1.sh APELLIDO
#
# Una práctica por unidad: UD01 matriz de riesgos, UD02 copias con restic, UD03 CA y HTTPS, UD04 SSH.
#
# Este script SOLO LEE el estado del sistema: no instala ni cambia nada. Solo crea una
# carpeta temporal en /var/tmp para la restauración de prueba y la borra al terminar
# (restic se ejecuta con --no-lock, así que tampoco escribe en el repositorio).
# Cada comprobación vale 0,8 puntos (10 comprobaciones = 8,0 puntos).
# Genera el fichero  evidencias-INT1-APELLIDO.txt  en el directorio actual.
set -u
export LC_ALL=C

[ "$(id -u)" -eq 0 ] || { echo "Ejecútalo con sudo:  sudo $0 APELLIDO"; exit 2; }
APELLIDO="${1:-}"
[[ "$APELLIDO" =~ ^[A-Za-z][A-Za-z0-9_-]{1,30}$ ]] || { echo "Uso:  sudo $0 APELLIDO   (solo letras, números, - o _)"; exit 2; }

# Rutas y nombres que fija el enunciado de la práctica
DIR_INT=/srv/int1                    # documentos de la práctica
DATOS=/srv/datos                     # datos clínicos ficticios que se copian
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
  local f="$DIR_INT/matriz-riesgos.csv" h; [ -f "$f" ] || return 1
  h=$(head -n1 "$f" | sed '1s/^\xEF\xBB\xBF//' | tr -d '\r')          # tolera BOM de UTF-8 y fin de línea de Windows
  if [[ "$h" == *';'* ]]; then say "AVISO:    matriz-riesgos.csv usa ';' como separador (Excel en español): debe usar comas"; fi
  [ "$h" = 'activo,amenaza,probabilidad,impacto,riesgo,tratamiento' ] || return 1
  tail -n +2 "$f" | tr -d '\r' | awk -F, '
    NF > 0 { n++ }
    NF >= 6 && $3 >= 1 && $3 <= 5 && $4 >= 1 && $4 <= 5 && $5 == $3 * $4 { ok++ }
    END { exit !(n >= 8 && ok == n) }'
}
f_A2() {  # integridad: SHA256SUMS incluye la matriz y todos los hashes coinciden
  ( cd "$DIR_INT" && [ -f SHA256SUMS ] && grep -q 'matriz-riesgos.csv' SHA256SUMS && sha256sum -c --quiet SHA256SUMS )
}
# ---------- UD02 · Protección de los datos ----------
f_B1() {  # al menos 5 ficheros en /srv/datos y repositorio restic íntegro (sin bloqueo: no escribe en el repositorio)
  [ "$(find "$DATOS" -type f 2>/dev/null | wc -l)" -ge 5 ] || return 1
  RESTIC_PASSWORD_FILE="$PASS_RESTIC" restic -r "$REPO" --no-lock check
}
f_B2() {  # restauración en una ruta distinta idéntica a los datos actuales
  local t r; t=$(mktemp -d /var/tmp/int1-rest.XXXXXX) || return 1
  if RESTIC_PASSWORD_FILE="$PASS_RESTIC" restic -r "$REPO" --no-lock restore latest --include "$DATOS" --target "$t"; then
    diff -r "$DATOS" "$t$DATOS"; r=$?
  else r=1; fi
  rm -rf "$t"; return $r
}
f_B3() {  # copias programadas: temporizador de systemd activo que lanza restic al menos cada 4 horas
  local timer svc exe expr t0 t1 t2 gap
  while read -r timer _; do
    [ -n "$timer" ] || continue
    systemctl is-active --quiet "$timer" || continue
    svc=$(systemctl show -p Unit --value "$timer" 2>/dev/null); [ -n "$svc" ] || continue
    # el servicio debe lanzar restic (directamente o mediante un script que lo contenga)
    exe=$(systemctl show -p ExecStart --value "$svc" 2>/dev/null | sed -nE 's/.*path=([^ ;]+).*/\1/p' | head -n1)
    { systemctl cat "$svc" 2>/dev/null | grep -q 'restic backup'; } || { [ -r "$exe" ] && grep -q 'restic' "$exe"; } || continue
    # frecuencia: el mayor intervalo entre ejecuciones consecutivas de cada OnCalendar no supera 4 h
    while IFS= read -r expr; do
      [ -n "$expr" ] || continue
      mapfile -t T < <(systemd-analyze calendar --iterations=48 "$expr" 2>/dev/null | awk '
        /\(in UTC\):/ { u[++nu] = $0 }
        /^ *(Next elapse|Iteration #[0-9]+):/ { l[++nl] = $0 }
        END { if (nu > 0) for (i = 1; i <= nu; i++) print u[i]; else for (i = 1; i <= nl; i++) print l[i] }' \
        | sed -E 's/^[^:]*: +//')
      [ "${#T[@]}" -ge 2 ] || continue
      gap=0; t0=""
      for t1 in "${T[@]}"; do
        t1=$(date -d "$t1" +%s 2>/dev/null) || { gap=999999; break; }
        [ -n "$t0" ] && [ $((t1 - t0)) -gt "$gap" ] && gap=$((t1 - t0))
        t0=$t1
      done
      [ "$gap" -gt 0 ] && [ "$gap" -le 14400 ] && return 0
    done < <(systemctl show -p TimersCalendar --value "$timer" 2>/dev/null | grep -oE 'OnCalendar=[^;}]*' | sed -E 's/^OnCalendar=//; s/ +$//')
  done < <(systemctl list-unit-files --type=timer --state=enabled --no-legend 2>/dev/null)
  return 1
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
# ---------- UD04 · Fortificación ----------
f_D1() {  # SSH solo con clave y sin acceso directo de root
  local c; c=$(sshd -T 2>/dev/null) || return 1
  grep -qx 'passwordauthentication no' <<<"$c" && grep -qx 'pubkeyauthentication yes' <<<"$c" && grep -qx 'permitrootlogin no' <<<"$c"
}
f_D2() {  # Fail2ban activo con la cárcel (jail) sshd y maxretry <= 3 (valor por defecto: 5)
  local m; systemctl is-active --quiet fail2ban || return 1
  m=$(fail2ban-client get sshd maxretry 2>/dev/null) || return 1
  [[ "$m" =~ ^[0-9]+$ ]] && [ "$m" -le 3 ]
}

# ---------- Informe ----------
say "PRACTICA: INT-1 (UD01-UD04) · modulo 0378 · curso 2026/27"
say "ALUMNO:   $APELLIDO"
say "MAQUINA:  $(hostname) · $(. /etc/os-release && echo "$PRETTY_NAME") · kernel $(uname -r)"
say "ID-VM:    $(sha256sum /etc/machine-id | cut -c1-12)"
say "FECHA:    $(date -Is)"
say ""
for h in restic openssl sshd fail2ban-client systemd-analyze; do
  command -v "$h" >/dev/null 2>&1 || say "AVISO:    falta la orden '$h' (la comprobación asociada fallará)"
done
say "--- UD01 Diagnostico (matriz de riesgos)"
chk A1 "Matriz de riesgos valida (>= 8 filas, riesgo = prob x impacto)" "revisa $DIR_INT/matriz-riesgos.csv" f_A1
chk A2 "SHA256SUMS verifica la matriz de riesgos"                       "genera el fichero con sha256sum en $DIR_INT" f_A2
say "--- UD02 Copias de seguridad (restic)"
chk B1 "Datos en /srv/datos (>= 5 ficheros) y repositorio restic integro" "restic -r $REPO check"                    f_B1
chk B2 "Restauracion en otra ruta identica a /srv/datos"                "haz una copia NUEVA tras el ultimo cambio"  f_B2
chk B3 "Copias programadas: temporizador con restic cada 4 h o menos"   "systemctl list-timers; OnCalendar con intervalo <= 4 h" f_B3
say "--- UD03 PKI y HTTPS"
chk C1 "CA propia con CN=CA-$APELLIDO"                                  "openssl x509 -in $CA_DIR/ca.crt -noout -subject" f_C1
chk C2 "Certificado firmado por la CA y con SAN $FQDN"                  "openssl verify y -ext subjectAltName"       f_C2
chk C3 "HTTPS en 443 con TLS 1.3 y cadena verificada"                   "openssl s_client -tls1_3 -CAfile ca.crt"    f_C3
say "--- UD04 Fortificacion (SSH y Fail2ban)"
chk D1 "SSH solo con clave y sin root (sshd -T)"                        "PasswordAuthentication no; PermitRootLogin no" f_D1
chk D2 "Fail2ban activo con jail sshd y maxretry <= 3"                  "jail.local: maxretry = 3 y reinicia fail2ban" f_D2
say ""
say "PUNTOS_AUTO: $OK/$TOTAL  (cada comprobacion = 0,8 -> $(awk -v o="$OK" 'BEGIN { printf "%.1f", o * 0.8 }') de 8,0 puntos)"

tee "$SALIDA" < "$TMP"
printf 'FIRMA: %s\n' "$(sha256sum "$TMP" | cut -d' ' -f1)" | tee -a "$SALIDA"
echo "Fichero generado: $(pwd)/$SALIDA"
