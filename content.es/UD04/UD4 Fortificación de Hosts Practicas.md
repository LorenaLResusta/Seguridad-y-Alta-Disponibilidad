---
title: "Prácticas"
slug: "practicas"
weight: 2
---

# UD4. Prácticas: fortificación de hosts

> Inventario, usuarios y sudo, contraseñas, SSH con claves y Fail2ban, cortafuegos, cifrado LUKS, control de acceso obligatorio, auditoría, integridad, antimalware, Lynis y Wazuh sobre máquinas virtuales propias.

| Datos de las prácticas | Información |
| --- | --- |
| Módulo | 0378. Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR |
| Duración estimada | 10 horas |
| Entorno | Red `SAD-NAT` (192.168.100.0/24): `sad-web` (.30) como servidor a fortificar y `sad-cli` (.10) como cliente |
| Sistemas | Debian 13 (principal) y AlmaLinux 10 (donde se indica) |
| Teoría asociada | [Teoría de la UD4](../teoria/) |

---

## 1. Objetivos

- Inventariar servicios, puertos, usuarios y permisos de un host Linux y guardarlo como línea base.
- Aplicar mínimo privilegio con usuarios, `sudo` y ACL, y una política de contraseñas con PAM.
- Configurar SSH con claves, comprobar que se rechazan las contraseñas y bloquear IP abusivas con Fail2ban.
- Configurar un cortafuegos local con política de denegación por defecto y verificarlo con Nmap.
- Crear y usar un volumen cifrado LUKS (en un entorno de pruebas).
- Diagnosticar un bloqueo de control de acceso obligatorio (SELinux) y revisar AppArmor.
- Auditar cambios con `auditd`, AIDE y detectar malware de prueba con ClamAV.
- Medir la fortificación con Lynis (antes y después) y monitorizar con Wazuh.

> [!IMPORTANT]
> **Alcance ético y legal.** Todas las pruebas se hacen **solo** sobre tus máquinas virtuales de `SAD-NAT`. No escanees, ataques ni pruebes credenciales en equipos de terceros, ni en la red del centro. Los «intentos fallidos» de estas prácticas son pocos y controlados, contra tus propias cuentas, para comprobar que las defensas funcionan.

---

## 2. Preparación

### 2.1. Máquinas y *snapshots*

1. `sad-web` (Debian 13) y `sad-cli` (Debian 13 o AlmaLinux 10), con IP fijas en `SAD-NAT` (UD1).
2. Crea una *snapshot* de cada máquina llamada `ud4-inicio`. Si algo sale mal, vuelves al estado inicial.
3. Abre **dos terminales** contra `sad-web`: una para trabajar y otra de seguridad (para corregir errores sin perder el acceso). La consola de VirtualBox también sirve como acceso de emergencia.

### 2.2. Directorio de evidencias

En `sad-web`:

```bash
mkdir -p ~/ud4-evidencias            # carpeta para guardar la salida de los comandos
chmod 700 ~/ud4-evidencias           # solo tu usuario puede entrar
date | tee ~/ud4-evidencias/00-fecha.txt
```

`tee` muestra la salida en pantalla **y** la guarda en el fichero: así documentas sin repetir el comando.

### 2.3. Paquetes

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y openssh-server nmap lynis cryptsetup acl libpam-pwquality libpwquality-tools \
  fail2ban python3-systemd auditd aide clamav clamav-freshclam apparmor-utils ufw htop curl
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo dnf upgrade -y
sudo dnf install -y epel-release
sudo dnf install -y openssh-server nmap lynis cryptsetup acl libpwquality \
  fail2ban fail2ban-firewalld audit aide clamav clamav-update \
  policycoreutils-python-utils setroubleshoot-server httpd htop curl
```
{{% /tab %}}
{{< /tabs >}}

> [!NOTE]
> En Debian el cortafuegos de las prácticas es **UFW** (o nftables) y en AlmaLinux **firewalld**. No instales ni actives los tres.

---

## 3. Práctica 1 · Inventario y línea base

**Objetivo:** documentar el estado inicial (y medir la superficie de ataque) antes de cambiar nada.

### 3.1. Inventario local (en `sad-web`)

```bash
{ hostnamectl; echo ---; ip -br a; echo ---; uname -r; } | tee ~/ud4-evidencias/01-sistema.txt
sudo ss -tulpn | tee ~/ud4-evidencias/01-puertos-local.txt
systemctl list-unit-files --state=enabled --type=service | tee ~/ud4-evidencias/01-servicios.txt
getent passwd | awk -F: '$3>=1000 && $3<65000 {print $1, $3, $7}' | tee ~/ud4-evidencias/01-usuarios.txt
sudo find / -xdev -perm -4000 -type f 2>/dev/null | tee ~/ud4-evidencias/01-suid.txt
```

### 3.2. Inventario desde el exterior (en `sad-cli`)

```bash
nmap -sV -p- 192.168.100.30 | tee ~/nmap-antes.txt
```

Copia el resultado a `sad-web` o consérvalo para el informe. `-sV` intenta identificar el servicio y su versión; `-p-` explora los 65 535 puertos.

### 3.3. Análisis

Rellena esta tabla en tu informe:

| Puerto | Servicio | ¿Es necesario? | ¿Debe estar accesible desde toda la red? | Decisión |
| --- | --- | --- | --- | --- |
| 22/tcp | sshd | Sí | Solo desde `SAD-NAT` | Restringir |
| … | … | … | … | … |

> [!TIP]
> Si no hay más servicios, instala uno para practicar: `sudo apt install -y nginx` (Debian) o `sudo dnf install -y nginx` (AlmaLinux).

---

## 4. Práctica 2 · Usuarios, sudo, ACL y contraseñas

**Objetivo:** aplicar mínimo privilegio y una política de contraseñas.

### 4.1. Usuarios y grupo de administración web

```bash
sudo groupadd webadmins
sudo useradd -m -s /bin/bash -G webadmins ana        # administradora web
sudo useradd -m -s /bin/bash luis                    # usuario sin privilegios
sudo passwd ana                                      # usa una contraseña de laboratorio
sudo passwd luis
id ana; id luis | tee ~/ud4-evidencias/02-usuarios.txt
```

### 4.2. sudo restringido

```bash
sudo visudo -f /etc/sudoers.d/10-webadmins
```

Escribe una única línea y guarda:

```text
%webadmins ALL=(root) /usr/bin/systemctl restart nginx, /usr/bin/systemctl status nginx
```

Comprobaciones:

```bash
sudo visudo -c                              # esperado: "parsed OK" en todos los ficheros
sudo -l -U ana                              # ana solo puede esas dos órdenes
su - ana -c 'sudo systemctl status nginx'   # funciona
su - ana -c 'sudo cat /etc/shadow'          # debe fallar: "no está autorizado" / "not allowed"
su - luis -c 'sudo -l'                      # luis no tiene permisos sudo
```

Revisa el registro: `sudo journalctl _COMM=sudo --since "10 min ago"`. Los intentos fallidos quedan anotados.

### 4.3. ACL

```bash
sudo mkdir -p /srv/proyecto
sudo setfacl -m u:ana:rwx /srv/proyecto
sudo setfacl -m u:luis:rx /srv/proyecto
getfacl /srv/proyecto | tee ~/ud4-evidencias/02-acl.txt
su - luis -c 'touch /srv/proyecto/prueba'      # esperado: Permission denied (luis solo puede leer)
su - ana  -c 'touch /srv/proyecto/prueba && echo "ana escribe"'
```

### 4.4. Política de contraseñas (pwquality)

Haz una copia y edita el fichero:

```bash
sudo cp /etc/security/pwquality.conf /etc/security/pwquality.conf.bak
sudoedit /etc/security/pwquality.conf
```

Descomenta o añade:

```ini
minlen = 12
minclass = 3
maxrepeat = 3
usercheck = 1
```

Comprobación con la utilidad de puntuación y con un cambio real:

```bash
echo 'abc123'                  | pwscore     # debe rechazarse
echo 'Cuatro-Nubes-Rojas-84!'  | pwscore     # puntuación alta
sudo passwd luis                              # prueba con 'abc123': debe rechazarla; luego con una frase larga
```

Registra el resultado en `~/ud4-evidencias/02-pwquality.txt`.

### 4.5. Bloqueo por intentos fallidos (opcional, con precaución)

Sigue el apartado 4.3 de la teoría (AlmaLinux: `authselect enable-feature with-faillock`; Debian: edición de `common-auth`). **Mantén abierta una sesión de `root`** durante la prueba.

```bash
for i in 1 2 3 4 5 6; do su - luis -c true <<< "contraseña_incorrecta" ; done 2>/dev/null
sudo faillock --user luis                      # intentos registrados
sudo faillock --user luis --reset              # desbloquear
```

> [!WARNING]
> Si la configuración PAM falla y no puedes iniciar sesión, restaura desde la consola: `cp /etc/pam.d/common-auth.bak /etc/pam.d/common-auth` (Debian) o `authselect disable-feature with-faillock` (AlmaLinux).

---

## 5. Práctica 3 · SSH seguro y Fail2ban

**Objetivo:** cerrar la puerta más usada. Ciclo: amenaza (acceso remoto) → vulnerabilidad (contraseñas y `root`) → ataque (intentos repetidos) → detección (registros) → mitigación (claves y Fail2ban) → comprobación.

### 5.1. Claves en el cliente

En `sad-cli`:

```bash
ssh-keygen -t ed25519 -C "ana@sad-cli"                       # acepta la ruta por defecto y pon una passphrase
ssh-copy-id -i ~/.ssh/id_ed25519.pub ana@192.168.100.30      # copia la clave pública al servidor
ssh ana@192.168.100.30 'hostname; id'                        # entra con la clave
```

> [!IMPORTANT]
> `ssh-copy-id` necesita que, en ese momento, el servidor aún acepte contraseña. Hazlo **antes** de desactivarla.

### 5.2. Configuración endurecida (en `sad-web`)

Con la sesión de seguridad abierta:

```bash
sudo mkdir -p /etc/ssh/sshd_config.d
sudoedit /etc/ssh/sshd_config.d/10-hardening.conf
```

```text
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
AllowUsers ana
MaxAuthTries 3
LoginGraceTime 30
X11Forwarding no
AllowTcpForwarding no
ClientAliveInterval 300
ClientAliveCountMax 2
```

Valida y recarga:

```bash
sudo sshd -t && echo "Sintaxis correcta"                         # si hay error, NO recargues
sudo sshd -T | grep -Ei 'permitrootlogin|passwordauthentication|allowusers' | tee ~/ud4-evidencias/03-sshd-efectivo.txt
sudo systemctl reload ssh        # Debian   ·   AlmaLinux: sudo systemctl reload sshd
```

### 5.3. Comprobación (desde `sad-cli`)

```bash
ssh ana@192.168.100.30 'echo acceso con clave OK'                      # debe funcionar
ssh -o PubkeyAuthentication=no ana@192.168.100.30                      # Permission denied (publickey)
ssh luis@192.168.100.30                                                # rechazado: no está en AllowUsers
ssh root@192.168.100.30                                                # rechazado
```

Revisa el registro en `sad-web`:

```bash
sudo journalctl -u ssh --since "10 min ago" --no-pager | tail -20     # AlmaLinux: -u sshd
```

### 5.4. Fail2ban

En `sad-web`, crea `/etc/fail2ban/jail.local`:

```bash
sudoedit /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime  = 10m
findtime = 10m
maxretry = 3
backend  = systemd
ignoreip = 127.0.0.1/8
# AlmaLinux: banaction = firewallcmd-rich-rules

[sshd]
enabled = true
mode    = aggressive
```

`mode = aggressive` hace que Fail2ban cuente también las conexiones que se cierran sin autenticarse (lo que ocurre cuando un cliente ofrece una clave no válida o un usuario no permitido).

```bash
sudo systemctl enable --now fail2ban
sudo fail2ban-client status sshd                   # debe mostrar el jail activo
```

> [!NOTE]
> `ignoreip` no incluye a `sad-cli` a propósito: para poder probar el bloqueo. Cuando termines, **desbloquea** tu IP y valora añadirla.

**Prueba controlada**, desde `sad-cli` (tu propia máquina contra tu propio servidor), 5 intentos con un usuario inexistente:

```bash
for i in 1 2 3 4 5; do ssh -o BatchMode=yes usuariofalso@192.168.100.30 true; done
ssh ana@192.168.100.30 true        # esperado: Connection refused / timed out (IP bloqueada)
```

En `sad-web`:

```bash
sudo fail2ban-client status sshd | tee ~/ud4-evidencias/03-fail2ban.txt     # "Banned IP list: 192.168.100.10"
sudo fail2ban-client set sshd unbanip 192.168.100.10                        # desbloquear
```

Tras desbloquear, vuelve a entrar desde `sad-cli` para comprobar la recuperación.

### 5.5. Solución de problemas

| Problema | Qué mirar |
| --- | --- |
| Tras recargar no puedo entrar | En la sesión de seguridad: `sudo rm /etc/ssh/sshd_config.d/10-hardening.conf && sudo systemctl reload ssh` |
| `Permission denied (publickey)` con tu usuario | Permisos: `~/.ssh` 700 y `authorized_keys` 600; `AllowUsers` correcto; `journalctl -u ssh` |
| Fail2ban no bloquea | `sudo fail2ban-client status sshd`; comprueba `backend = systemd` y `python3-systemd`; `sudo fail2ban-regex systemd-journal sshd` |

---

## 6. Práctica 4 · Cortafuegos local y verificación con Nmap

**Objetivo:** que el servidor solo ofrezca los puertos imprescindibles y comprobarlo desde fuera.

### 6.1. Red de seguridad

Programa un «deshacer» por si te quedas sin acceso:

```bash
sudo systemd-run --on-active=180 --unit=deshacer-fw systemctl stop ufw        # Debian con UFW
# AlmaLinux:  sudo systemd-run --on-active=180 --unit=deshacer-fw systemctl stop firewalld
```

### 6.2. Reglas

{{< tabs >}}
{{% tab "Debian / Ubuntu (UFW)" %}}
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.100.0/24 to any port 22 proto tcp comment 'SSH laboratorio'
sudo ufw allow 80/tcp comment 'HTTP'          # solo si has instalado nginx
sudo ufw enable
sudo ufw status verbose | tee ~/ud4-evidencias/04-ufw.txt
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky (firewalld)" %}}
```bash
sudo systemctl enable --now firewalld
sudo firewall-cmd --permanent --remove-service=ssh
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.100.0/24" service name="ssh" accept'
sudo firewall-cmd --permanent --add-service=http         # solo si hay servidor web
sudo firewall-cmd --reload
sudo firewall-cmd --list-all | tee ~/ud4-evidencias/04-firewalld.txt
```
{{% /tab %}}
{{< /tabs >}}

### 6.3. Comprobación

Desde `sad-cli`:

```bash
nmap -sV -p- 192.168.100.30 | tee ~/nmap-despues.txt
diff <(grep -E '^[0-9]+/' ~/nmap-antes.txt) <(grep -E '^[0-9]+/' ~/nmap-despues.txt)
```

Resultado esperado: solo siguen abiertos 22 (desde la red del laboratorio) y, si procede, 80. Lo demás aparece `filtered` o desaparece.

Si todo funciona, **cancela el deshacer**: `sudo systemctl stop deshacer-fw.timer`. Si el acceso se pierde, a los 3 minutos el cortafuegos se detiene.

> [!TIP]
> Prueba una regla negativa: desde otra IP no incluida en `192.168.100.0/24` (por ejemplo, con una segunda VM en otra red) el puerto 22 debe aparecer filtrado. Anota qué diferencias ves entre `filtered` (el paquete se descarta) y `closed` (se rechaza con RST).

---

## 7. Práctica 5 · Cifrado de datos con LUKS

**Objetivo:** proteger datos en reposo y comprobar que sin la clave son ilegibles. Se usa un fichero como disco virtual: **no se toca ningún disco real**.

```bash
sudo truncate -s 200M /root/volumen.img
sudo cryptsetup luksFormat --type luks2 /root/volumen.img      # escribe YES (mayúsculas) y fija una frase de paso
sudo cryptsetup open /root/volumen.img seguro
sudo mkfs.ext4 -L SEGURO /dev/mapper/seguro
sudo mkdir -p /mnt/seguro && sudo mount /dev/mapper/seguro /mnt/seguro
echo "Informe confidencial de laboratorio" | sudo tee /mnt/seguro/informe.txt
df -h /mnt/seguro | tee ~/ud4-evidencias/05-luks-montado.txt
```

Cierre y comprobación de que el contenido no es legible:

```bash
sudo umount /mnt/seguro
sudo cryptsetup close seguro
sudo grep -c "confidencial" /root/volumen.img || true        # esperado: 0
sudo cryptsetup luksDump /root/volumen.img | head -25 | tee ~/ud4-evidencias/05-luks-dump.txt
```

Copia de seguridad de la cabecera y prueba de recuperación:

```bash
sudo cryptsetup luksHeaderBackup /root/volumen.img --header-backup-file /root/volumen.header
sudo chmod 600 /root/volumen.header
sudo cryptsetup open /root/volumen.img seguro && sudo mount /dev/mapper/seguro /mnt/seguro && cat /mnt/seguro/informe.txt
sudo umount /mnt/seguro && sudo cryptsetup close seguro
```

> [!CAUTION]
> `luksFormat` destruye el contenido del dispositivo indicado. Revisa **dos veces** la ruta; en este laboratorio solo debe ser `/root/volumen.img`.

**Preguntas para el informe:** ¿qué ocurre si olvidas la frase de paso? ¿Y si se corrompe la cabecera y no tienes copia? ¿Dónde guardarías la copia de la cabecera y por qué?

---

## 8. Práctica 6 · Control de acceso obligatorio

{{< tabs >}}
{{% tab "AlmaLinux / Rocky (SELinux)" %}}
**Objetivo:** diagnosticar y corregir una denegación de SELinux sin desactivarlo.

```bash
getenforce | tee ~/ud4-evidencias/06-selinux.txt           # debe ser Enforcing
sudo mkdir -p /srv/web
echo "<h1>Hola SELinux</h1>" | sudo tee /srv/web/index.html
sudo sed -i 's|^DocumentRoot.*|DocumentRoot "/srv/web"|' /etc/httpd/conf/httpd.conf
sudo tee /etc/httpd/conf.d/srvweb.conf >/dev/null <<'CONF'
<Directory "/srv/web">
    Require all granted
</Directory>
CONF
sudo httpd -t                                       # Syntax OK
sudo systemctl enable --now httpd
sudo firewall-cmd --add-service=http --permanent && sudo firewall-cmd --reload
curl -I http://localhost                            # 403 Forbidden
```

Diagnóstico:

```bash
ls -Zd /srv/web /srv/web/index.html                 # tipo var_t (incorrecto)
sudo ausearch -m avc -ts recent | tail -5           # denegación de httpd_t sobre var_t
```

Corrección permanente (sin `setenforce 0`):

```bash
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/web(/.*)?"
sudo restorecon -Rv /srv/web
curl -I http://localhost                            # 200 OK
```

Segundo ejercicio con un **booleano**: haz que Apache pueda conectar con otros servidores (por ejemplo, como proxy):

```bash
getsebool httpd_can_network_connect
sudo setsebool -P httpd_can_network_connect on
```
{{% /tab %}}
{{% tab "Debian / Ubuntu (AppArmor)" %}}
**Objetivo:** entender qué perfiles protegen el sistema y cómo cambiar su modo.

```bash
sudo aa-status | tee ~/ud4-evidencias/06-apparmor.txt      # perfiles en enforce / complain
```

Crea un perfil mínimo de prueba para un script propio:

```bash
sudo tee /usr/local/bin/leer-config.sh >/dev/null <<'SCRIPT'
#!/bin/bash
# Lee un fichero de configuración y, si puede, el de contraseñas (para demostrar el confinamiento)
cat /etc/hostname
cat /etc/shadow 2>&1 | head -1
SCRIPT
sudo chmod 755 /usr/local/bin/leer-config.sh
sudo tee /etc/apparmor.d/usr.local.bin.leer-config.sh >/dev/null <<'PERFIL'
#include <tunables/global>
/usr/local/bin/leer-config.sh {
  #include <abstractions/base>
  #include <abstractions/bash>
  /usr/local/bin/leer-config.sh r,
  /usr/bin/bash ix,
  /usr/bin/cat ix,
  /usr/bin/head ix,
  /etc/hostname r,
  deny /etc/shadow r,
}
PERFIL
sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.leer-config.sh      # carga el perfil
sudo aa-status | grep leer-config
sudo /usr/local/bin/leer-config.sh                      # /etc/shadow denegado aunque seas root
sudo journalctl -k --since "2 min ago" | grep -i 'apparmor="DENIED"' | tail -3
```

Prueba el modo *complain* (solo registra, no bloquea) y vuelve a *enforce*:

```bash
sudo aa-complain /usr/local/bin/leer-config.sh
sudo /usr/local/bin/leer-config.sh          # ahora se muestra la primera línea de /etc/shadow
sudo aa-enforce /usr/local/bin/leer-config.sh
```

> [!NOTE]
> Si algún acceso del script falla por rutas de tu sistema, el registro del kernel (`journalctl -k`) indica qué falta en el perfil. Es el mismo proceso de diagnóstico que con SELinux: **leer la denegación, ajustar la política**.
{{% /tab %}}
{{< /tabs >}}

---

## 9. Práctica 7 · Auditoría, integridad y antimalware

### 9.1. Registros persistentes

```bash
sudo mkdir -p /etc/systemd/journald.conf.d
sudo tee /etc/systemd/journald.conf.d/10-persistente.conf >/dev/null <<'EOF'
[Journal]
Storage=persistent
SystemMaxUse=500M
EOF
sudo systemctl restart systemd-journald
journalctl --disk-usage | tee ~/ud4-evidencias/07-journal.txt
ls /var/log/journal                         # existe el directorio: ya es persistente
```

### 9.2. auditd

```bash
sudo systemctl enable --now auditd
sudo tee /etc/audit/rules.d/50-hardening.rules >/dev/null <<'EOF'
-w /etc/passwd -p wa -k identidad
-w /etc/shadow -p wa -k identidad
-w /etc/sudoers.d/ -p wa -k sudoers
-w /etc/ssh/sshd_config.d/ -p wa -k ssh
EOF
sudo augenrules --load
sudo auditctl -l | tee ~/ud4-evidencias/07-audit-reglas.txt
```

Provoca eventos y búscalos:

```bash
sudo useradd temporal-audit
sudo touch /etc/ssh/sshd_config.d/99-prueba.conf
sudo ausearch -k identidad -i | tail -12
sudo ausearch -k ssh -i | tail -8 | tee ~/ud4-evidencias/07-audit-eventos.txt
sudo rm /etc/ssh/sshd_config.d/99-prueba.conf && sudo userdel -r temporal-audit
```

Anota para cada evento: **quién** (`auid`), **qué** (ruta, acción), **cuándo** y **con qué resultado**.

### 9.3. AIDE

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo aideinit
sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo aide --init
sudo mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz
```
{{% /tab %}}
{{< /tabs >}}

```bash
echo "# modificado" | sudo tee -a /etc/hosts >/dev/null          # cambio no autorizado simulado
sudo aide --check | tee ~/ud4-evidencias/07-aide.txt             # Debian: añade -c /etc/aide/aide.conf si lo pide
sudo sed -i '$d' /etc/hosts                                      # revertir el cambio
```

El informe de AIDE debe mostrar `/etc/hosts` en «Changed entries», con el hash anterior y el actual.

### 9.4. ClamAV con el fichero EICAR

```bash
sudo systemctl stop clamav-freshclam 2>/dev/null; sudo freshclam; sudo systemctl start clamav-freshclam 2>/dev/null
mkdir -p ~/prueba-av
echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > ~/prueba-av/eicar.txt
clamscan -r --infected ~/prueba-av | tee ~/ud4-evidencias/07-clamav.txt        # Eicar-Signature FOUND
rm ~/prueba-av/eicar.txt
clamscan -r --infected ~/prueba-av                                              # tras borrarlo: Infected files: 0
```

El fichero EICAR es una cadena de texto **inofensiva** reconocida por todos los antivirus como prueba. No utilices muestras de malware real.

---

## 10. Práctica 8 · Auditoría con Lynis (antes y después)

```bash
sudo lynis audit system --quiet | tee ~/ud4-evidencias/08-lynis-despues.txt >/dev/null
sudo grep -E '^hardening_index' /var/log/lynis-report.dat
sudo grep -E '^suggestion\[\]' /var/log/lynis-report.dat | head -20
```

Procedimiento:

1. Si dispones de la *snapshot* `ud4-inicio`, ejecuta Lynis también en ese estado inicial (o conserva el resultado de una auditoría hecha antes de empezar) y anota el **hardening index**.
2. Elige **3 sugerencias** de Lynis que no hayas aplicado ya, justifica el riesgo que reducen y aplícalas (por ejemplo, banner legal en SSH, parámetros `sysctl`, `umask`, desactivar un protocolo no usado).
3. Vuelve a ejecutar Lynis y compara el índice.
4. Elige 1 sugerencia que **decidas no aplicar** y razona por qué.

| Medida | Riesgo que reduce | Comando | Comprobación | Índice antes → después |
| --- | --- | --- | --- | --- |
| … | … | … | … | … |

---

## 11. Práctica 9 · Monitorización centralizada con Wazuh

**Objetivo:** ver el estado de seguridad de varias máquinas en un único panel.

> [!NOTE]
> Wazuh evoluciona con frecuencia. Sigue la **guía de instalación oficial** de la versión vigente (<https://documentation.wazuh.com>) y anota la versión usada. Si tu docente ya ofrece un servidor Wazuh, salta al apartado 11.2.

### 11.1. Servidor (máquina nueva `sad-wazuh`, Debian o Ubuntu compatible, 4 GB RAM, 2 vCPU, 50 GB)

1. Crea la VM en `SAD-NAT` con IP `192.168.100.40` y una *snapshot* inicial.
2. Descarga el instalador asistido desde la documentación oficial («Quickstart») y **revisa el script antes de ejecutarlo**:

```bash
curl -fsSLO <URL del instalador indicada en la documentación oficial>
less wazuh-install.sh                      # revisar antes de ejecutar
sudo bash wazuh-install.sh -a              # instalación todo en uno (servidor, indexador y panel)
```

3. Al terminar, el instalador muestra la contraseña del usuario `admin` del panel. **Guárdala** y accede a `https://192.168.100.40` desde el navegador (certificado autofirmado: es esperado en el laboratorio).

### 11.2. Agente en `sad-web`

1. En el panel: *Agents → Deploy new agent*; elige el sistema operativo, introduce la IP del servidor y el nombre `sad-web`. El asistente genera los comandos de instalación.
2. Ejecútalos en `sad-web` y comprueba:

```bash
sudo systemctl enable --now wazuh-agent
sudo systemctl status wazuh-agent --no-pager | tee ~/ud4-evidencias/09-wazuh-agente.txt
```

3. El agente debe aparecer como **Active** en el panel. Anota nombre, IP, versión del agente y hora de la última conexión.

> [!WARNING]
> Si usas el cortafuegos de la práctica 4, el agente necesita llegar al servidor (salida) y el servidor recibir en los puertos 1514/tcp y 1515/tcp. Revisa las reglas si el agente no se conecta.

### 11.3. Eventos y supervisión de integridad

1. **Intentos fallidos de SSH**: desde `sad-cli`, genera 3 intentos erróneos con un usuario inexistente (como en la práctica 3). Localiza en *Threat Hunting / Events* las alertas de autenticación fallida: anota regla, nivel, hora, usuario y host de origen.
2. **Integridad (FIM)**: en `sad-web` crea y modifica un fichero en un directorio supervisado por defecto (por ejemplo, `/etc`):

```bash
echo "prueba" | sudo tee /etc/prueba-wazuh.conf
echo "cambio" | sudo tee -a /etc/prueba-wazuh.conf
sudo rm /etc/prueba-wazuh.conf
```

   Comprueba que aparecen eventos de fichero creado, modificado y eliminado (puede tardar unos minutos: el análisis FIM es periódico por defecto).
3. **Configuración (SCA)**: abre el módulo de evaluación de configuración del agente, localiza **dos controles fallidos** y razona si aplicarías la medida y cómo.
4. Para cada alerta responde: ¿qué evidencia aporta?, ¿qué impacto podría tener?, ¿cuál sería la primera medida de contención?

---

## 12. Práctica 10 · Windows Server 2025 (opcional)

Con una máquina de evaluación y una *snapshot*:

```powershell
Get-MpComputerStatus | Select-Object AMServiceEnabled, AntivirusEnabled, AntivirusSignatureLastUpdated
Update-MpSignature
Get-NetFirewallProfile | Format-Table Name, Enabled, DefaultInboundAction
Set-SmbServerConfiguration -EnableSMB1Protocol $false -Force
net accounts /lockoutthreshold:5 /lockoutduration:15 /lockoutwindow:15 /minpwlen:12
auditpol /set /subcategory:"Logon" /success:enable /failure:enable
```

Comprueba cada medida (con el cmdlet `Get-` o la consola «Directiva de seguridad local») y haz un inicio de sesión fallido contra tu cuenta de laboratorio para localizar el evento **4625** en el *Visor de eventos* (Seguridad). Anota los campos *Cuenta*, *Tipo de inicio de sesión* y *Dirección de red de origen*.

---

## 13. Problemas habituales

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| Sin acceso SSH tras la práctica 3 | Error en `10-hardening.conf` o sin clave | Consola de VirtualBox: borra el fichero y `systemctl reload ssh` |
| `ssh-copy-id` falla | Ya desactivaste la contraseña | Restaura temporalmente `PasswordAuthentication yes` o usa la consola |
| UFW bloquea SSH | Regla mal escrita o `enable` sin regla | Consola: `sudo ufw disable`, corrige y vuelve a activar |
| Fail2ban no arranca | Error de sintaxis en `jail.local` | `sudo fail2ban-client -t` y `journalctl -u fail2ban` |
| `cryptsetup: device busy` | El volumen sigue montado | `umount /mnt/seguro` y después `cryptsetup close` |
| 403 persistente en SELinux | Contexto no aplicado | `ls -Zd /srv/web`, repite `restorecon -Rv` |
| `augenrules` sin efecto | Reglas inmutables (`-e 2`) o servicio parado | Reinicia el sistema; revisa `systemctl status auditd` |
| AIDE no encuentra la base | No se copió `aide.db.new` | Repite el paso de copia (Debian) o `mv` (AlmaLinux) |
| El agente Wazuh no conecta | Cortafuegos o IP del servidor incorrecta | Revisa 1514/1515 y `/var/ossec/etc/ossec.conf` |

---

## 14. Buenas prácticas de seguridad aplicadas

- Una medida cada vez, con su comprobación y su forma de revertirla.
- Copia (`.bak`) antes de editar; validación (`visudo -c`, `sshd -t`, `httpd -t`, `nft -c`) antes de aplicar.
- Segunda sesión abierta y *snapshot* antes de tocar SSH, PAM o el cortafuegos.
- Pruebas siempre sobre equipos propios y con intentos mínimos.
- Evidencias guardadas en `~/ud4-evidencias` con fecha, sin contraseñas ni claves privadas.

---

## 15. Autoevaluación

1. ¿Qué objetivo principal tiene el hardening y qué es la superficie de ataque?
2. ¿Qué principio establece que un usuario debe disponer solo de los permisos necesarios?
3. ¿Por qué se edita `sudoers` con `visudo`?
4. ¿Qué diferencia hay entre autenticación y autorización? Pon un ejemplo con SSH.
5. ¿Qué riesgo mitiga Secure Boot y cuál la contraseña de GRUB?
6. ¿Qué protege el cifrado de disco y qué **no** protege (por ejemplo, con el equipo encendido y la sesión abierta)?
7. ¿Por qué una clave privada SSH no debe compartirse y cómo se protege?
8. ¿Qué diferencia hay entre `reload` y `restart` al cambiar `sshd_config`?
9. ¿Qué diferencia hay entre un puerto `closed` y uno `filtered` en Nmap?
10. ¿Para qué sirve Lynis y por qué no basta con maximizar su puntuación?
11. ¿Qué detecta AIDE que no detecta un antivirus?
12. ¿Qué diferencia hay entre un IDS y un IPS? ¿Cuál es Fail2ban?
13. ¿Por qué no se debe desactivar SELinux para «arreglar» un error?
14. ¿Qué información proporciona un evento de `auditd` y en qué se diferencia de un mensaje de `journald`?
15. ¿Por qué un análisis de vulnerabilidades requiere autorización previa?

---

## 16. Tarea evaluable: fortificación de un servidor

**Escenario.** Eres administrador/a de sistemas en *Textiles del Ebro*. Recibes un servidor Debian 13 (o AlmaLinux 10) con un servidor web instalado y debes entregarlo fortificado y documentado.

**Entrega** (PDF o Markdown, con capturas y evidencias propias, redactado con tus palabras):

1. **Inventario inicial** (prácticas 1) y análisis de la superficie de ataque, con `nmap` antes.
2. **Análisis de riesgos**: al menos 8 hallazgos con amenaza, vulnerabilidad, impacto y prioridad.
3. **Medidas aplicadas**, cada una con: comando o configuración, explicación, comprobación y forma de revertirla. Deben incluir como mínimo: usuarios y `sudo` mínimos, política de contraseñas, SSH con claves y Fail2ban, cortafuegos con denegación por defecto, actualizaciones automáticas de seguridad, un volumen cifrado, SELinux/AppArmor activo y `auditd`.
4. **Resultados**: `nmap` después, hardening index de Lynis antes y después, y una captura de una alerta de Wazuh generada por una prueba controlada.
5. **Medidas no aplicadas** con justificación y **plan de mantenimiento** (actualizaciones, revisión de registros, copias, revisión de accesos).

| Criterio | Peso |
| --- | --- |
| Inventario y análisis de riesgos correctos | 20 % |
| Medidas bien configuradas y justificadas | 35 % |
| Comprobaciones y evidencias reproducibles | 25 % |
| Resultados y análisis (antes/después) | 10 % |
| Claridad, estructura y recuperación (rollback) | 10 % |

---

## 17. Resumen

Has partido de un servidor con configuración por defecto y lo has llevado a un estado verificable: mínimo privilegio, acceso remoto con claves y bloqueo de abusos, cortafuegos con denegación por defecto, datos cifrados, procesos confinados, cambios auditados y visibilidad centralizada. La clave del proceso es **medir antes, cambiar con red de seguridad, comprobar y documentar**.

---

## 18. Referencias

- OpenSSH, *sshd_config(5)*: <https://man.openbsd.org/sshd_config>
- Debian, *Securing Debian Manual*: <https://www.debian.org/doc/manuals/securing-debian-manual/>
- Red Hat, *Security hardening* (RHEL, aplicable a AlmaLinux): <https://docs.redhat.com>
- Fail2ban: <https://github.com/fail2ban/fail2ban>
- Cryptsetup / LUKS: <https://gitlab.com/cryptsetup/cryptsetup>
- Lynis: <https://cisofy.com/documentation/lynis/>
- Wazuh: <https://documentation.wazuh.com>
- CIS Benchmarks: <https://www.cisecurity.org/cis-benchmarks>
- CCN-STIC: <https://www.ccn-cert.cni.es/guias.html>
