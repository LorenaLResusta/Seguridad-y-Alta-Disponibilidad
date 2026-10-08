---
title: "UD1 · Prácticas"
weight: 2
bookToc: true
---

# UD1 · Prácticas

{{< ra "RA1:a,b,c,d,e,g,i" "RA2:b,h" "RA7:f" >}}

Preparación del laboratorio, revisión básica de un sistema Linux, detección de amenazas habituales, análisis de vulnerabilidades, iniciación al análisis forense y elaboración de un plan de gestión de riesgos.

| Práctica | Tipo | Nivel | Horas | CE principales |
|---|---|---|--:|---|
| [1.1 Preparación del laboratorio](#práctica-11--preparación-del-laboratorio) | Guiada | ●○○ | 1 | RA1: a, b |
| [1.2 Inventario y revisión básica de seguridad](#práctica-12--inventario-y-revisión-básica-de-seguridad) | Guiada | ●○○ | 1 | RA1: c · RA2: h |
| [1.3 Integridad y trazabilidad](#práctica-13--integridad-y-trazabilidad) | Guiada | ●●○ | 1 | RA1: a, g |
| [1.4 Contraseñas y detección de fuerza bruta](#práctica-14--contraseñas-y-detección-de-fuerza-bruta) | Guiada | ●●○ | 1 | RA1: e |
| [1.5 Análisis de un correo de phishing](#práctica-15--análisis-de-un-correo-de-phishing) | Autónoma | ●○○ | — | RA1: d |
| [1.6 Vulnerabilidades conocidas del sistema](#práctica-16--vulnerabilidades-conocidas-del-sistema) | Autónoma | ●●○ | — | RA1: c · RA2: b |
| [1.7 Iniciación al análisis forense](#práctica-17--iniciación-al-análisis-forense) | Reto | ●●● | — | RA1: i |
| [1.8 Plan de gestión de riesgos](#práctica-18--plan-de-gestión-de-riesgos) | Proyecto | ●●● | 1 | RA1: a, c · RA7: f |
| **Total** | | | **5 h** | |

> [!NOTE]
> Las prácticas con **—** horas son **trabajo autónomo** (fuera del horario) u opcionales: amplían la unidad, pero no restan tiempo a las 5 h de prácticas oficiales de la unidad. El resto se realiza en el laboratorio, en las horas indicadas.

## Objetivos

- Preparar una máquina virtual aislada y recuperable para las prácticas del módulo.
- Inventariar un sistema: identidad, red, usuarios, servicios y puertos.
- Comprobar la integridad de ficheros y la trazabilidad de las acciones.
- Detectar intentos fallidos de autenticación y valorar una política de contraseñas.
- Analizar un correo de *phishing* a partir de sus cabeceras.
- Identificar vulnerabilidades del sistema relacionadas con CVE.
- Adquirir y analizar una evidencia digital respetando su integridad.
- Elaborar un plan de gestión de riesgos y un procedimiento de respuesta a incidentes.

## Normas del laboratorio

> [!CAUTION]
> - Trabaja únicamente sobre **tu propia máquina virtual** y los sistemas que autorice el profesorado.
> - No escanees ni pruebes credenciales contra equipos, redes o servicios ajenos.
> - No uses datos personales reales en capturas, informes ni pruebas.
> - Crea una **instantánea** antes de cada práctica para poder volver a un estado conocido.

**Entrega de evidencias**: para cada práctica guarda las salidas de los comandos (copiando el texto o con capturas) y responde a las preguntas de análisis. Todas las evidencias se guardarán en `~/ud01/evidencias`.

---

## Práctica 1.1 · Preparación del laboratorio

{{< practica num="1.1" tipo="Guiada" duracion="1 h" nivel="1" ra="RA1:a,b" entorno="Debian 13 · VirtualBox 7" entrega="capturas del laboratorio operativo" >}}

#### ¿Por qué máquinas virtuales?

Una **máquina virtual (VM)** es un ordenador simulado por software (el **hipervisor**, en nuestro caso VirtualBox) que se ejecuta dentro del equipo real (el **anfitrión**). Para practicar seguridad tiene tres ventajas:

1. **Aislamiento**: lo que ocurra en la VM no afecta al anfitrión ni a la red del centro.
2. **Recuperación**: las **instantáneas** (*snapshots*) permiten volver atrás en segundos.
3. **Reproducibilidad**: todo el grupo trabaja con el mismo entorno.

#### Material

- Un equipo con la virtualización activada en la UEFI/BIOS (Intel VT-x o AMD-V).
- [VirtualBox 7.x](https://www.virtualbox.org/wiki/Downloads).
- Una ISO de **Debian 13** (*netinst*) o de **AlmaLinux 10** (*minimal* o *boot*).
- Unos 30 GB libres en disco.

> [!NOTE]
> En este módulo los ejemplos indican siempre los comandos de las dos familias de distribuciones cuando son diferentes. Elige una y úsala durante todo el curso.

#### Crear una red NAT para el módulo

Con el modo **NAT** simple de VirtualBox cada VM está sola en su red. Con una **Red NAT** varias VM se ven entre sí y salen a Internet, pero no son accesibles desde la red del centro. Esta será la red de trabajo de las primeras unidades.

1. En VirtualBox: **Archivo → Herramientas → Administrador de red → Redes NAT → Crear**.
2. Nombre: `SAD-NAT`. Prefijo IPv4: `192.168.100.0/24`. DHCP activado.

También puede crearse desde la línea de órdenes del anfitrión con `VBoxManage`, la herramienta de administración de VirtualBox:

```bash
VBoxManage natnetwork add --netname SAD-NAT --network "192.168.100.0/24" --enable --dhcp on
VBoxManage natnetwork list
```

<!-- hint:h1 -->
{{% details title="💡 Pista" open=false %}}
En VirtualBox existen dos modos distintos: **NAT** (cada VM queda aislada, con salida a Internet pero sin ver a las demás) y **Red NAT** (*NAT Network*, las VM comparten una red y se ven entre sí). Para este módulo necesitas **Red NAT**, con el nombre `SAD-NAT`. Si dos VM no se hacen ping, revisa primero esto.
{{% /details %}}

#### Crear e instalar la máquina virtual

1. **Nueva** → Nombre `sad-linux01`. Selecciona la ISO. Desmarca la **instalación desatendida**.
2. Memoria: 2048 MB. CPU: 2. Disco: 25 GB dinámico.
3. **Configuración → Red → Adaptador 1**: conectado a **Red NAT** → `SAD-NAT`.
4. Inicia la VM y realiza una instalación mínima:

| Opción | Debian 13 | AlmaLinux 10 |
| --- | --- | --- |
| Nombre del equipo | `sad-linux01` | `sad-linux01` |
| Usuario | inicial + primer apellido (ej. `fperez`) | igual, marcando **Hacer administrador** |
| Contraseña de `root` | **Déjala en blanco**: así el usuario se añade al grupo `sudo` | Deja la cuenta `root` bloqueada |
| Software | Solo **servidor SSH** y **utilidades estándar** | Instalación **mínima** |

> [!TIP]
> Dejar la cuenta `root` sin contraseña y administrar con `sudo` es una buena práctica: cada acción administrativa queda registrada con el nombre de la persona que la ejecutó (trazabilidad).

#### Comprobaciones iniciales

Inicia sesión y comprueba el sistema:

```bash
hostnamectl                 # nombre del equipo, sistema operativo y núcleo
cat /etc/os-release         # distribución y versión exactas
ip -br address              # interfaces y direcciones IP en formato breve
ip route                    # puerta de enlace por defecto
id                          # usuario, UID y grupos a los que pertenece
sudo -l                     # qué puede ejecutar con sudo
timedatectl                 # hora del sistema y sincronización NTP
```

Resultado esperado (Debian):

```text
$ ip -br address
lo               UNKNOWN        127.0.0.1/8 ::1/128
enp0s3           UP             192.168.100.4/24 fe80::a00:27ff:fe4e:66a1/64

$ id
uid=1000(fperez) gid=1000(fperez) grupos=1000(fperez),24(cdrom),27(sudo),...

$ timedatectl
...
System clock synchronized: yes
              NTP service: active
```

Actualiza el sistema:

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo apt update          # descarga la lista de paquetes disponibles
sudo apt full-upgrade -y # instala todas las actualizaciones
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo dnf upgrade -y      # descarga e instala todas las actualizaciones
```
{{% /tab %}}
{{< /tabs >}}

Si se ha actualizado el núcleo, reinicia con `sudo systemctl reboot`.

<!-- hint:h2 -->
{{% details title="🔧 Si algo falla" open=false %}}
- **`ip -br address` no muestra dirección IP:** comprueba en VirtualBox que el adaptador está conectado a `SAD-NAT` y que *Cable conectado* está marcado.
- **El nombre de la interfaz no es `enp0s3`:** puede llamarse `ens3`, `enp0s8`, etc. Usa el que muestre tu salida en todos los comandos.
- **No hay Internet pero sí IP:** prueba `ping -c 2 1.1.1.1` (red) y luego `ping -c 2 debian.org` (DNS). Si falla solo el segundo, es un problema de DNS.
{{% /details %}}

#### Crear la instantánea base

1. Apaga la VM: `sudo systemctl poweroff`.
2. En VirtualBox, selecciona la VM → **Instantáneas** → **Tomar**.
3. Nombre: `00-instalacion-actualizada`. Descripción: fecha y «sistema recién instalado y actualizado».

```bash
# Equivalente desde la línea de órdenes del anfitrión
VBoxManage snapshot sad-linux01 take "00-instalacion-actualizada" --description "Sistema base actualizado"
VBoxManage snapshot sad-linux01 list
```

> [!IMPORTANT]
> Una instantánea **no es una copia de seguridad**: se guarda en el mismo disco que la VM. Si ese disco falla, se pierden ambas. Lo estudiaremos en la UD2.

<!-- hint:h3 -->
> [!TIP]
> **Toma una instantánea antes de cada práctica que modifique el sistema** y ponle un nombre con la fecha (por ejemplo, `antes-UD1-P2-2026-10-06`). Si algo sale mal, vuelves al punto anterior en segundos. Es el equivalente de laboratorio a una copia de seguridad.

---

## Práctica 1.2 · Inventario y revisión básica de seguridad

{{< practica num="1.2" tipo="Guiada" duracion="1 h" nivel="1" ra="RA1:c;RA2:h" entorno="Debian 13 · VirtualBox 7" entrega="inventario en la carpeta de evidencias" >}}

**Objetivo**: conocer el estado del sistema antes de protegerlo. *No se puede proteger lo que no se conoce.*

#### Preparar la carpeta de evidencias

```bash
mkdir -p ~/ud01/evidencias
cd ~/ud01/evidencias
```

#### Inventario del sistema

```bash
{
  echo "=== SISTEMA ===";   hostnamectl
  echo "=== RED ===";       ip -br address; ip route
  echo "=== DISCOS ===";    lsblk -f
  echo "=== MEMORIA ===";   free -h
} > inventario.txt
less inventario.txt
```

- Las llaves `{ ... }` agrupan varias órdenes para redirigir la salida de todas a un único fichero.
- `lsblk -f` muestra los dispositivos de bloque (discos y particiones) con su sistema de ficheros.
- `free -h` muestra la memoria en unidades legibles (*human readable*).

#### Usuarios del sistema

Cada línea de `/etc/passwd` describe una cuenta: `usuario:x:UID:GID:descripción:directorio:shell`.

```bash
# Cuentas con UID >= 1000: son las cuentas de personas
awk -F: '$3 >= 1000 && $3 < 65534 {print $1, $3, $7}' /etc/passwd

# Cuentas que pueden iniciar sesión (tienen una shell válida)
grep -Ev '(nologin|false)$' /etc/passwd

# Miembros de los grupos de administración
getent group sudo wheel
```

- `awk -F:` separa cada línea por los dos puntos; `$3` es el tercer campo (UID) y `$7` la *shell*.
- Las cuentas de servicio (como `www-data` o `sshd`) tienen UID bajos y *shell* `nologin`: no pueden iniciar sesión interactiva.

**Pregunta**: ¿hay alguna cuenta, además de la tuya y de `root`, que pueda iniciar sesión? ¿Quién puede administrar el sistema?

#### Servicios y puertos en escucha

Un servicio que escucha en un puerto de red es una posible puerta de entrada. Hay que conocerlos todos y justificar cada uno.

```bash
# Servicios en ejecución
systemctl list-units --type=service --state=running --no-pager

# Puertos TCP y UDP en escucha y el proceso que los abre
sudo ss -tulpn
```

Salida esperada en una instalación mínima:

```text
Netid State  Local Address:Port  Process
udp   UNCONN 0.0.0.0:68          users:(("dhclient",pid=512,fd=7))
tcp   LISTEN 0.0.0.0:22          users:(("sshd",pid=640,fd=3))
tcp   LISTEN [::]:22             users:(("sshd",pid=640,fd=4))
```

- `0.0.0.0:22` significa que SSH escucha en **todas** las interfaces IPv4.
- Un servicio que escucha en `127.0.0.1` solo es accesible desde el propio equipo.

**Pregunta**: completa la tabla para cada puerto en escucha.

| Puerto | Protocolo | Servicio | ¿Necesario? | Accesible desde | Riesgo |
| --- | --- | --- | --- | --- | --- |
| 22 | TCP | OpenSSH | Sí, administración | Todas las interfaces | Fuerza bruta si hay contraseñas débiles |

<!-- hint:h4 -->
{{% details title="💡 Pista" open=false %}}
Fíjate en la **dirección de escucha** de cada puerto: `0.0.0.0` o `[::]` significa «accesible desde cualquier red»; `127.0.0.1` significa «solo desde esta máquina». Un servicio de uso interno (una base de datos, por ejemplo) que escuche en `0.0.0.0` es un candidato claro a corregir.
{{% /details %}}

#### Actualizaciones pendientes

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo apt update
apt list --upgradable
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo dnf check-update            # devuelve código 100 si hay actualizaciones
sudo dnf updateinfo list --security   # solo actualizaciones de seguridad
```
{{% /tab %}}
{{< /tabs >}}

#### Análisis

Redacta en `analisis_p1.md`:

1. Tres **activos** de tu VM, su valor y la propiedad (C, I, D) más importante de cada uno.
2. Dos **vulnerabilidades** potenciales detectadas (o que podrían aparecer) y su clasificación por tipología y origen.
3. Una medida de seguridad **física** y una **lógica** aplicables a tu VM y a tu equipo anfitrión.

---

## Práctica 1.3 · Integridad y trazabilidad

{{< practica num="1.3" tipo="Guiada" duracion="1 h" nivel="2" ra="RA1:a,g" entorno="Debian 13 · VirtualBox 7" entrega="línea base y registro de la detección" >}}

**Ciclo de trabajo**: *amenaza* (un intruso o un error modifica ficheros de configuración) → *vulnerabilidad* (nadie vigila los cambios) → *ataque* (se modifica `/etc/hosts`) → *detección* (comparación de hashes y registros) → *mitigación* (restaurar y proteger) → *comprobación*.

#### Crear una línea base de integridad

Una **línea base** (*baseline*) es una fotografía del estado correcto del sistema con la que comparar después.

```bash
cd ~/ud01/evidencias

# Huellas SHA-256 de ficheros críticos de configuración
sudo sha256sum /etc/passwd /etc/group /etc/hosts /etc/ssh/sshd_config > linea_base.sha256
cat linea_base.sha256

# Protegemos la línea base frente a modificaciones accidentales
chmod 400 linea_base.sha256
```

#### Simular una modificación maliciosa

Muchos *malware* modifican `/etc/hosts` para redirigir dominios legítimos a servidores del atacante.

```bash
# Copia de seguridad de la configuración antes de tocarla
sudo cp -a /etc/hosts /etc/hosts.bak

# «Ataque» simulado: redirigimos un dominio
echo "203.0.113.66   www.mibanco.es" | sudo tee -a /etc/hosts
```

- `tee -a` añade (*append*) el texto al final del fichero. Se usa con `sudo tee` porque una redirección `>>` no hereda los privilegios de `sudo`.
- `203.0.113.0/24` es un rango reservado para documentación: no pertenece a nadie.

#### Detectar la modificación

```bash
sudo sha256sum -c linea_base.sha256
```

Resultado esperado:

```text
/etc/passwd: La suma coincide
/etc/group: La suma coincide
/etc/hosts: FALLÓ
/etc/ssh/sshd_config: La suma coincide
sha256sum: AVISO: 1 suma de verificación calculada NO coincide
```

Para ver **qué** ha cambiado:

```bash
diff /etc/hosts.bak /etc/hosts
# > 203.0.113.66   www.mibanco.es

getent hosts www.mibanco.es
# 203.0.113.66    www.mibanco.es
```

<!-- hint:h5 -->
{{% details title="🎯 Resultado esperado" open=false %}}
La comprobación debe señalar el fichero alterado y el resumen final (según el idioma del sistema):

```text
/etc/hosts: FALLIDO            (en inglés: FAILED)
sha256sum: AVISO: 1 suma calculada NO coincide
```

El resto de ficheros aparecen como `HECHO` (`OK`). Si **todos** salen bien, no has modificado `/etc/hosts` o la línea base se creó después del cambio.
{{% /details %}}

#### Trazabilidad: ¿quién ha sido?

```bash
sudo journalctl _COMM=sudo --since today --no-pager | grep hosts
```

Resultado esperado:

```text
oct 06 11:02:15 sad-linux01 sudo[1873]: fperez : TTY=pts/0 ; PWD=/home/fperez/ud01/evidencias ;
  USER=root ; COMMAND=/usr/bin/tee -a /etc/hosts
```

El registro identifica **usuario**, **terminal**, **directorio**, **hora** y **orden**: trazabilidad completa.

<!-- hint:h6 -->
{{% details title="🔧 Si algo falla" open=false %}}
- **No aparece nada en el registro:** la traza de `sudo` solo existe si ejecutaste el comando con `sudo`. Lo que se ve es *quién usó sudo*, no el contenido del cambio.
- **En AlmaLinux** los mensajes de `sudo` y `su` pueden estar en `/var/log/secure`: `sudo grep sudo /var/log/secure | tail`.
- Si la VM acaba de reiniciarse, usa `journalctl --since today` o añade `-b` (arranque actual).
{{% /details %}}

#### Mitigar y comprobar

```bash
sudo cp -a /etc/hosts.bak /etc/hosts     # restauramos el original
sudo sha256sum -c linea_base.sha256      # todas las sumas deben coincidir
getent hosts www.mibanco.es              # ya no devuelve la IP falsa
sudo rm /etc/hosts.bak
```

#### Automatizar la vigilancia

Este script compara la línea base y escribe un aviso en el diario del sistema si algo ha cambiado:

```bash
#!/usr/bin/env bash
# /usr/local/sbin/comprobar_integridad.sh
# Compara los ficheros críticos con su línea base y registra el resultado.
BASE="/home/fperez/ud01/evidencias/linea_base.sha256"   # adapta la ruta

if sha256sum --quiet -c "$BASE" 2>/dev/null; then
    logger -t integridad "OK: los ficheros críticos no han cambiado"
else
    logger -p auth.warning -t integridad "ALERTA: cambios detectados respecto a la línea base"
    exit 1
fi
```

```bash
sudo install -m 750 comprobar_integridad.sh /usr/local/sbin/
sudo /usr/local/sbin/comprobar_integridad.sh
journalctl -t integridad -n 5 --no-pager
```

- `logger` escribe mensajes en el registro del sistema; `-t` asigna una etiqueta y `-p` la prioridad.
- `install -m 750` copia el fichero asignando permisos en un solo paso.

> [!NOTE]
> Herramientas como **AIDE** o el módulo de integridad de **Wazuh** hacen esto mismo de forma profesional y para miles de ficheros. Las veremos en la UD4.

**Preguntas**: ¿qué principio protege la comparación de hashes? ¿Qué principio protege el registro de `sudo`? ¿Por qué la línea base debería guardarse fuera del propio servidor?

---

## Práctica 1.4 · Contraseñas y detección de fuerza bruta

{{< practica num="1.4" tipo="Guiada" duracion="1 h" nivel="2" ra="RA1:e" entorno="Debian 13 · VirtualBox 7" entrega="política de contraseñas y registro del ataque" >}}

**Ciclo**: *amenaza* (bot que prueba contraseñas) → *vulnerabilidad* (contraseña débil, sin límite de intentos) → *ataque* (intentos fallidos simulados) → *detección* (registros) → *mitigación* (política de contraseñas, bloqueo y MFA) → *comprobación*.

#### Crear un usuario de pruebas

```bash
sudo useradd -m -s /bin/bash prueba_ud01   # -m crea el directorio personal, -s asigna la shell
sudo passwd prueba_ud01                     # asigna una contraseña: usa "Prueba2026!"
```

#### Valorar la calidad de las contraseñas

Instala las utilidades de `libpwquality`, la biblioteca que usa PAM para valorar contraseñas:

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo apt install -y libpwquality-tools
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo dnf install -y libpwquality
```
{{% /tab %}}
{{< /tabs >}}

```bash
for p in "123456" "Prueba2026!" "empresa2026" "tostada-azul-mochila-trueno"; do
    printf '%-30s ' "$p"; echo "$p" | pwscore 2>&1
done
```

Resultado aproximado:

```text
123456                         Password quality check failed: The password is shorter than 8 characters
Prueba2026!                    41
empresa2026                    Password quality check failed: The password fails the dictionary check
tostada-azul-mochila-trueno    100
```

`pwscore` devuelve una puntuación de 0 a 100 o el motivo del rechazo.

#### Simular un ataque de fuerza bruta local

Simulamos varios intentos fallidos de inicio de sesión con `su` desde **otra terminal** (Ctrl+Alt+F2 en la consola de la VM o una segunda sesión SSH):

```bash
# Introduce contraseñas incorrectas cuando las pida (repite 5 veces)
su - prueba_ud01
```

<!-- hint:h7 -->
> [!WARNING]
> **Solo contra el usuario de pruebas `prueba_ud01`**, dentro de tu máquina virtual y con el fin de ver cómo queda registrado. No pruebes contraseñas en cuentas reales ni en equipos ajenos. El objetivo es comprender la **huella en los registros** y la mitigación, no el ataque.

#### Detectar los intentos fallidos

```bash
# Mensajes de autenticación fallida en la última hora
sudo journalctl --since "-1h" --no-pager | grep -Ei "authentication failure|FAILED SU"

# Contar intentos fallidos por usuario objetivo
sudo journalctl --since "-1h" --no-pager | grep -oP "authentication failure.*user=\K\S+" | sort | uniq -c
```

Resultado esperado:

```text
oct 06 11:20:01 sad-linux01 su[2011]: pam_unix(su-l:auth): authentication failure; logname=fperez uid=1000 euid=0 tty=pts/1 ruser=fperez rhost=  user=prueba_ud01
...
      5 prueba_ud01
```

- `grep -oP ... \K\S+` usa una expresión regular de Perl: `\K` descarta lo anterior y se queda solo con el nombre de usuario.
- `sort | uniq -c` agrupa y cuenta las repeticiones.

En un servidor real con SSH expuesto verías cientos de intentos diarios contra `root`, `admin`, `test`… desde IP de todo el mundo.

<!-- hint:h8 -->
{{% details title="💡 Pista" open=false %}}
Fíjate en los campos `user=`, `rhost=` y la hora de cada línea. Muchos fallos seguidos, del mismo origen y en pocos segundos, son la firma típica de un ataque automatizado; un fallo suelto es lo normal (un despiste al teclear).
{{% /details %}}

#### Mitigación

1. Revisa la caducidad y estado de la cuenta:

    ```bash
    sudo chage -l prueba_ud01
    sudo passwd -S prueba_ud01      # estado: P (contraseña válida), L (bloqueada)
    ```

2. Bloquea temporalmente la cuenta comprometida y comprueba que no puede iniciar sesión:

    ```bash
    sudo passwd -l prueba_ud01      # -l (lock) bloquea la contraseña
    sudo passwd -S prueba_ud01
    su - prueba_ud01                 # debe fallar aunque la contraseña sea correcta
    ```

3. Redacta en `politica_contrasenas.md` una política de contraseñas para tu laboratorio siguiendo las recomendaciones de la teoría (longitud, listas de contraseñas filtradas, bloqueo tras intentos, MFA, cuentas separadas).

> [!NOTE]
> El bloqueo **automático** tras varios intentos (`pam_faillock`), las reglas de calidad (`pam_pwquality`) y la protección de SSH con Fail2ban se configuran en la **UD4**.

#### Limpieza

```bash
sudo userdel -r prueba_ud01      # -r elimina también su directorio personal
```

---

## Práctica 1.5 · Análisis de un correo de phishing

{{< practica num="1.5" tipo="Autónoma" duracion="0 h · trabajo autónomo" nivel="1" ra="RA1:d" entorno="Debian 13 · VirtualBox 7" entrega="informe de análisis del correo" >}}

**Objetivo**: reconocer indicadores técnicos y no técnicos de un correo fraudulento (RA1.d).

#### Material

Guarda el siguiente mensaje en `~/ud01/evidencias/sospechoso.eml`. Es un ejemplo **ficticio** con direcciones de documentación.

```text
Return-Path: <notificaciones@correos-envios-es.top>
Received: from mail.envios-rapidos.top (mail.envios-rapidos.top [198.51.100.23])
        by mx.ejemplo.es (Postfix) with ESMTPS id 4XyZ1
        for <alumno@ejemplo.es>; Tue, 6 Oct 2026 07:41:12 +0200 (CEST)
Authentication-Results: mx.ejemplo.es;
        spf=fail (mx.ejemplo.es: domain of correos-envios-es.top does not designate 198.51.100.23 as permitted sender) smtp.mailfrom=correos-envios-es.top;
        dkim=none;
        dmarc=fail (p=NONE) header.from=correos-envios-es.top
From: "Correos" <notificaciones@correos-envios-es.top>
Reply-To: soporte.pagos@protonmail.example
To: alumno@ejemplo.es
Subject: Su paquete esta retenido - accion requerida
Date: Tue, 6 Oct 2026 07:41:09 +0200
Content-Type: text/html; charset="UTF-8"

<p>Estimado cliente,</p>
<p>Su envio no ha podido ser entregado por falta de pago de las tasas de aduana (1,79 EUR).</p>
<p>Si no realiza el pago en las proximas <b>12 horas</b> el paquete sera devuelto.</p>
<p><a href="https://correos-envios-es.top/pago?id=88731">Pagar ahora en Correos.es</a></p>
```

#### Análisis técnico

Extrae los campos importantes con `grep`:

```bash
cd ~/ud01/evidencias
grep -E "^(From|Reply-To|Return-Path|Subject|Received):" sospechoso.eml
grep -A3 "^Authentication-Results" sospechoso.eml
grep -oE 'href="[^"]+"' sospechoso.eml
```

<!-- hint:h9 -->
{{% details title="💡 Pista" open=false %}}
Compara tres cosas: el dominio de `From`, el de `Return-Path` y el de `Reply-To`. Si no coinciden entre sí ni con la empresa que dice ser, es una señal fuerte de suplantación. Después mira `Authentication-Results`: `spf=fail`, `dkim=fail` o `dmarc=fail` indican que el servidor remitente **no está autorizado** a enviar en nombre de ese dominio.

**No abras enlaces ni adjuntos:** analiza solo el texto del fichero `.eml`.
{{% /details %}}

#### Preguntas

1. ¿Coincide el dominio del remitente con el dominio oficial de la empresa suplantada?
2. ¿Qué significan los resultados `spf=fail`, `dkim=none` y `dmarc=fail`?
3. ¿Por qué es sospechoso que `Reply-To` sea distinto de `From`?
4. ¿A qué dominio apunta realmente el enlace? ¿Coincide con el texto que se muestra?
5. Enumera al menos **seis** indicadores de *phishing*, técnicos y no técnicos.
6. ¿Qué técnica de ingeniería social utiliza (urgencia, autoridad, miedo, curiosidad…)?
7. Redacta el procedimiento que debería seguir un empleado que recibe este correo.

{{% details "Pistas para la corrección" %}}
- Dominio `.top` que imita a la empresa (*typosquatting*), sin firma DKIM y con SPF y DMARC fallidos.
- `Reply-To` a un servicio de correo gratuito: las respuestas irían al atacante.
- El texto del enlace dice «Correos.es» pero el `href` lleva a `correos-envios-es.top`.
- Urgencia (12 horas), importe pequeño para no levantar sospechas, saludo genérico, faltas de ortografía (sin tildes).
- Procedimiento: no pulsar, no responder, notificar al responsable de seguridad (o reenviar como adjunto al buzón de incidentes), borrar; si se pulsó o se introdujeron datos, avisar inmediatamente y cambiar credenciales/bloquear tarjeta.
{{% /details %}}

---

## Práctica 1.6 · Vulnerabilidades conocidas del sistema

{{< practica num="1.6" tipo="Autónoma" duracion="0 h · trabajo autónomo" nivel="2" ra="RA1:c;RA2:b" entorno="Debian 13 · VirtualBox 7" entrega="informe de vulnerabilidades" >}}

**Objetivo**: relacionar el software instalado con vulnerabilidades públicas (CVE) y priorizar su corrección (RA1.c).

#### Listar vulnerabilidades del sistema

{{< tabs >}}
{{% tab "Debian" %}}
`debsecan` compara los paquetes instalados con el rastreador de seguridad de Debian.

```bash
sudo apt install -y debsecan
# Vulnerabilidades que YA tienen corrección disponible en trixie
debsecan --suite trixie --only-fixed
# Formato detallado
debsecan --suite trixie --format detail | less
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
`dnf updateinfo` consulta los avisos de seguridad publicados por la distribución.

```bash
# Resumen de avisos pendientes por gravedad
sudo dnf updateinfo summary
# Avisos de seguridad pendientes con su CVE
sudo dnf updateinfo list --security --with-cve
# Información de un aviso concreto
sudo dnf updateinfo info ALSA-2026:XXXX
```
{{% /tab %}}
{{< /tabs >}}

> [!NOTE]
> Si acabas de actualizar, puede que no aparezca ninguna vulnerabilidad con corrección pendiente. Restaura temporalmente la instantánea anterior a la actualización o consulta una versión concreta de un paquete para hacer el ejercicio.

#### Investigar una CVE

Elige una CVE de la lista (o usa `CVE-2024-6387`) y consulta su ficha:

```bash
CVE=CVE-2024-6387
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=$CVE" \
  | jq -r '.vulnerabilities[0].cve | .id, .published, .descriptions[0].value,
           (.metrics.cvssMetricV31[0].cvssData | "CVSS \(.baseScore) \(.baseSeverity) \(.vectorString)"),
           (.weaknesses[0].description[0].value)'
```

Comprueba la versión instalada del software afectado:

```bash
ssh -V                                   # versión del cliente OpenSSH
dpkg -l openssh-server 2>/dev/null | tail -1 || rpm -q openssh-server
```

<!-- hint:h10 -->
{{% details title="🔧 Si algo falla" open=false %}}
- **La consulta devuelve error 403 o 429:** la API pública de la NVD limita las peticiones sin clave (unas 5 cada 30 segundos). Espera medio minuto y reintenta.
- **Sin salida de red desde la VM:** puedes consultar la CVE en el navegador de tu equipo (`https://nvd.nist.gov/vuln/detail/CVE-XXXX-XXXX`) y copiar los datos a la tabla.
{{% /details %}}

#### Tabla de análisis

| CVE | Software | CVSS | ¿Explotada activamente (KEV)? | ¿Expuesta? | Prioridad | Acción |
| --- | --- | --- | --- | --- | --- | --- |
| CVE-2024-6387 | OpenSSH | 8,1 Alta | Consultar catálogo KEV | Sí, puerto 22 | Alta | Actualizar `openssh-server` |

#### Mitigar y comprobar

Aplica las actualizaciones de seguridad y vuelve a ejecutar `debsecan` o `dnf updateinfo`. La lista debe haber disminuido.

---

## Práctica 1.7 · Iniciación al análisis forense

{{< practica num="1.7" tipo="Reto" duracion="0 h · trabajo autónomo" nivel="3" ra="RA1:i" entorno="Debian 13 · VirtualBox 7" entrega="informe forense con cadena de custodia" >}}

**Objetivo**: adquirir una evidencia preservando su integridad, mantener una cadena de custodia y recuperar un fichero borrado (RA1.i).

**Escenario**: un empleado ha entregado una memoria USB que contenía un documento confidencial. Sospechamos que lo borró antes de entregarla. Simularemos la memoria con un **fichero de imagen** de 64 MB, de modo que no se necesita ningún disco adicional.

#### Preparar la «memoria USB»

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo apt install -y dosfstools sleuthkit
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo dnf install -y epel-release
sudo dnf install -y dosfstools sleuthkit
```
{{% /tab %}}
{{< /tabs >}}

- `dosfstools` permite crear sistemas de ficheros FAT (los habituales en memorias USB).
- **The Sleuth Kit** es un conjunto de herramientas forenses libres para analizar sistemas de ficheros.

```bash
mkdir -p ~/ud01/forense && cd ~/ud01/forense

# Creamos un fichero vacío de 64 MB y le damos formato FAT32
truncate -s 64M usb.img
mkfs.vfat -F 32 -n USB_EMPLEADO usb.img

# Lo montamos como si fuera un dispositivo y copiamos ficheros
sudo mkdir -p /mnt/usb
sudo mount -o loop,uid=$(id -u) usb.img /mnt/usb
echo "Planos del nuevo producto - CONFIDENCIAL" > /mnt/usb/confidencial.txt
echo "Lista de la compra" > /mnt/usb/compra.txt
sync

# El «empleado» borra el documento confidencial
rm /mnt/usb/confidencial.txt
ls -l /mnt/usb
sudo umount /mnt/usb
```

#### Adquisición y preservación

```bash
# 1. Hash del ORIGINAL
sha256sum usb.img | tee hash_original.txt

# 2. Copia de trabajo bit a bit
dd if=usb.img of=evidencia_caso01.img bs=4M status=progress

# 3. Hash de la COPIA: debe ser idéntico
sha256sum evidencia_caso01.img | tee hash_copia.txt

# 4. Protegemos el original contra escritura
chmod 444 usb.img
```

Rellena el **registro de cadena de custodia**:

| Fecha y hora | Evidencia | Acción | Responsable | Hash SHA-256 | Observaciones |
| --- | --- | --- | --- | --- | --- |
| 06/10/2026 11:45 | usb.img (USB_EMPLEADO) | Recepción | (tu nombre) | (hash) | Entregada por RR. HH. |
| 06/10/2026 11:50 | evidencia_caso01.img | Copia bit a bit con `dd` | (tu nombre) | (hash) | Coincide con el original |

#### Análisis de la copia

```bash
# Información del sistema de ficheros
fsstat evidencia_caso01.img | head -20

# Listado de ficheros, incluidos los BORRADOS (-d muestra solo los borrados)
fls -r evidencia_caso01.img
fls -r -d evidencia_caso01.img
```

Salida esperada (los números de entrada pueden variar):

```text
r/r 4:  USB_EMPLEADO (Volume Label Entry)
r/r * 6:        confidencial.txt
r/r 8:  compra.txt
```

El asterisco `*` indica un fichero **borrado**. El número (`6`) es su dirección (inodo) en el sistema de ficheros. En FAT el borrado solo marca la entrada como libre: el contenido sigue en el disco hasta que se sobrescribe.

```bash
# Recuperar el contenido a partir de su dirección
icat evidencia_caso01.img 6 > recuperado_confidencial.txt
cat recuperado_confidencial.txt
# Planos del nuevo producto - CONFIDENCIAL

# Línea temporal (fechas de acceso, modificación y creación)
fls -r -m / evidencia_caso01.img > bodyfile.txt
mactime -b bodyfile.txt -d | column -s, -t
```

<!-- hint:h11 -->
{{% details title="💡 Pista" open=false %}}
`fls -r` lista los ficheros del sistema de ficheros y `fls -r -d` solo los **borrados** (aparecen marcados con `*`). Con el número de inodo que muestra `fls` puedes recuperar el contenido: `icat evidencia_caso01.img <inodo>`. Trabaja siempre sobre la **copia**, nunca sobre el original.
{{% /details %}}

#### Comprobación de integridad final

```bash
sha256sum usb.img evidencia_caso01.img
```

Los hashes deben seguir coincidiendo con los iniciales: el análisis **no ha alterado** las evidencias.

<!-- hint:h12 -->
{{% details title="🔧 Si algo falla" open=false %}}
Si los *hashes* del original y de la copia **no coinciden** al final, la evidencia queda invalidada. Lo más probable: se montó o modificó el original, o se analizó sin proteger contra escritura. Repite la adquisición desde el principio y protege el original (`chmod 444`, o monta con `-o ro`).
{{% /details %}}

#### Preguntas

1. ¿Por qué se trabaja sobre una copia y no sobre el original?
2. ¿Qué demuestra que los dos hashes coincidan antes y después del análisis?
3. ¿Por qué ha sido posible recuperar el fichero borrado? ¿Cómo se podría haber borrado de forma segura? (Lo veremos en la UD2).
4. Redacta un breve informe pericial (media página) con: objeto, evidencias recibidas, metodología, herramientas y versiones (`fls -V`), resultados y conclusión.

---

## Práctica 1.8 · Plan de gestión de riesgos

{{< practica num="1.8" tipo="Proyecto" duracion="1 h" nivel="3" ra="RA1:a,c;RA7:f" entorno="Debian 13 · VirtualBox 7" entrega="plan de gestión de riesgos" >}}

#### Escenarios

Elige uno de estos escenarios para el informe:

| Escenario | Organización | Situación |
| --- | --- | --- |
| A | TechSolutions S.L. (25 empleados) | Migración a la nube, CMS para la web, accesos sospechosos a documentación técnica. |
| B | PetCare S.L. (clínica veterinaria) | Historiales digitalizados, servidor en un despacho, datos corruptos tras un corte de luz. |
| C | GourmetExpress (comida a domicilio) | Pedidos y pagos en línea, servidor en el almacén, caídas del servicio en horas punta. |
| D | CulturaUrbana (asociación cultural) | Plataforma de eventos, redes sociales comprometidas, contraseñas compartidas. |
| E | Academia Venus | Notas y datos de menores, portátiles del profesorado sin cifrar, Wi-Fi compartida con el alumnado. |

#### Paso 1: inventario y valoración de activos

Identifica al menos **ocho** activos de tipos distintos (información, servicios, software, hardware, comunicaciones, personas, instalaciones) y valóralos de 0 a 10 en cada dimensión.

| Activo | Tipo (MAGERIT) | C | I | D | Justificación |
| --- | --- | :-: | :-: | :-: | --- |
| Base de datos de clientes | Información | 9 | 8 | 7 | Datos personales; necesarios para el servicio diario |

#### Paso 2: amenazas y vulnerabilidades

Para al menos **seis** activos, identifica amenaza y vulnerabilidad. Incluye amenazas naturales, industriales, accidentales e intencionadas.

| Activo | Amenaza | Vulnerabilidad | Tipología / origen de la vulnerabilidad | Incidente posible |
| --- | --- | --- | --- | --- |
| Servidor web | Ciberdelincuente | CMS sin actualizar | Software / terceros | Desfiguración o robo de datos |

#### Paso 3: valoración del riesgo

Valora probabilidad e impacto (1-3), calcula el riesgo y ordénalo. Puedes usar el script `matriz_riesgos.py` de la teoría. Justifica los tres riesgos más altos.

<!-- hint:h13 -->
{{% details title="💡 Pista" open=false %}}
**Riesgo = probabilidad × impacto.** Usa una escala del 1 al 5 para cada factor y ordena la tabla de mayor a menor riesgo. Los de valor 15 o más se tratan primero; después decide para cada uno si lo **mitigas, transfieres, evitas o aceptas**, y justifícalo.
{{% /details %}}

#### Paso 4: tratamiento y plan de mejora

Propón al menos **ocho** salvaguardas que combinen controles físicos, técnicos y organizativos, e indica la estrategia de tratamiento.

| Riesgo | Estrategia | Salvaguarda | Tipo de control | Responsable | Prioridad | Coste estimado | Evidencia de implantación |
| --- | --- | --- | --- | --- | --- | --- | --- |
| *Phishing* | Mitigar | MFA + formación trimestral | Técnico + organizativo | Sistemas / RR. HH. | Alta | Bajo | Captura de MFA activo, registro de asistencia |

Estima el **riesgo residual** tras aplicar las salvaguardas.

#### Paso 5: procedimiento de respuesta

Redacta un procedimiento (una página) para uno de los riesgos más altos siguiendo las fases: preparación, detección y análisis, contención, erradicación, recuperación y lecciones aprendidas. Indica a quién se notificaría (INCIBE-CERT, AEPD, Policía) y en qué plazos.

#### Paso 6: cumplimiento legal

1. Indica qué tratamientos de datos personales realiza la organización y su base legal.
2. Identifica responsable, encargados (proveedores) y si necesita DPD.
3. Describe cómo atendería una solicitud de **derecho de acceso** de un cliente (plazo, verificación de identidad, formato de respuesta).
4. Indica si le afecta la LSSI-CE (web, *cookies*, comunicaciones comerciales) y qué debe cumplir.
5. Indica qué norma (ISO 27001, ENS, NIST CSF) le recomendarías como marco de mejora y por qué.

---

## Problemas habituales

| Problema | Causa probable | Solución |
| --- | --- | --- |
| La VM no arranca: «VT-x is not available» | Virtualización desactivada en la UEFI/BIOS o Hyper-V activo en Windows | Activar VT-x/AMD-V; desactivar Hyper-V / «Plataforma de máquina virtual» |
| La VM no tiene red | Adaptador no conectado a `SAD-NAT` o DHCP de la red NAT desactivado | Revisar la configuración del adaptador; `ip -br a` |
| `usuario is not in the sudoers file` | Se asignó contraseña a `root` en la instalación de Debian | Como root: `usermod -aG sudo usuario` y volver a iniciar sesión |
| `journalctl` no muestra mensajes antiguos | El diario no es persistente | Comprobar que existe `/var/log/journal` (persistente por defecto en Debian 13 y AlmaLinux 10) |
| `fls` no muestra el fichero borrado | La imagen se montó y escribió tras el borrado, sobrescribiendo la entrada | Repetir la preparación sin copiar más ficheros tras el borrado |
| `mount: wrong fs type` | Falta `dosfstools` o la imagen está corrupta | Instalar `dosfstools`; volver a crear la imagen |

## Actividades

1. Explica la diferencia entre amenaza, vulnerabilidad, riesgo, ataque e incidente con ejemplos de tu laboratorio.
2. Clasifica como física/lógica y activa/pasiva: RAID, cortafuegos, SAI, antivirus, copia de seguridad, control de acceso al CPD, IDS, cifrado de disco.
3. Analiza la contraseña `empresa2026` con `pwscore` y calcula su espacio de búsqueda. Propón una alternativa.
4. Busca un caso real de *ransomware* en España en los últimos dos años (por ejemplo en noticias de INCIBE o de la AEPD). Identifica vector de entrada, impacto y medidas que lo habrían evitado.
5. Prepara un ejercicio para un servicio web del laboratorio: describe una actividad autorizada de Red Team, las evidencias que revisaría el Blue Team, una mejora de Purple Team y dos reglas de alcance del White Team.
6. Compara MAGERIT, ISO 27005 y NIST SP 800-30 en una tabla (ámbito, fases, herramientas).

## Preguntas de autoevaluación

{{% details "1. ¿Qué tres propiedades forman la tríada CIA?" %}}
Confidencialidad, integridad y disponibilidad.
{{% /details %}}

{{% details "2. ¿Qué diferencia hay entre amenaza y vulnerabilidad?" %}}
La amenaza es el agente o evento que puede causar daño (un atacante, un incendio); la vulnerabilidad es la debilidad que permite que ese daño se produzca (contraseña débil, CPD sin extinción).
{{% /details %}}

{{% details "3. ¿Qué mecanismo permite comprobar la integridad de un fichero?" %}}
Una función hash (por ejemplo SHA-256). Si el hash calculado no coincide con el original, el fichero ha cambiado.
{{% /details %}}

{{% details "4. ¿Por qué una instantánea de VirtualBox no es una copia de seguridad?" %}}
Porque se almacena en el mismo disco que la máquina virtual. Si se pierde ese disco, se pierden la VM y sus instantáneas.
{{% /details %}}

{{% details "5. ¿Qué significan CVE y CVSS?" %}}
CVE es el identificador público de una vulnerabilidad concreta. CVSS es el sistema de puntuación de 0 a 10 que estima su gravedad técnica.
{{% /details %}}

{{% details "6. ¿Qué es el orden de volatilidad?" %}}
El criterio de recogida de evidencias que empieza por las más volátiles (memoria, conexiones de red) y termina por las persistentes (disco, copias).
{{% /details %}}

{{% details "7. ¿En qué plazo hay que notificar a la AEPD una brecha de datos personales?" %}}
Sin dilación indebida y, como máximo, en 72 horas desde que se tiene conocimiento (art. 33 RGPD), salvo que sea improbable que suponga un riesgo para los derechos de las personas.
{{% /details %}}

{{% details "8. ¿Qué norma define requisitos certificables para un SGSI?" %}}
ISO/IEC 27001 (versión vigente de 2022).
{{% /details %}}

{{% details "9. ¿Qué es más resistente: una contraseña de 8 caracteres con símbolos o una frase de 5 palabras aleatorias?" %}}
La frase de 5 palabras aleatorias (unos 64 bits frente a unos 52), y además es más fácil de recordar.
{{% /details %}}

{{% details "10. ¿Qué diferencia hay entre Blue Team y Purple Team?" %}}
El Blue Team defiende, monitoriza y responde. El Purple Team coordina a los equipos rojo y azul para convertir las técnicas de ataque simuladas en mejoras de detección y defensa.
{{% /details %}}

## Tarea evaluable de la unidad

> [!IMPORTANT]
> Esta tarea **no se entrega por separado**: es un **hito** de la práctica integradora obligatoria **INT-1** (entrega: 27/11/2026). Consulta [Prácticas integradoras](/guia/practicas-integradoras/).

Entrega un informe en PDF o Markdown que incluya:

1. **Evidencias de las prácticas 1 a 6** (inventario, línea base e incidente simulado, detección de fuerza bruta, análisis de *phishing*, tabla de CVE, informe forense con cadena de custodia).
2. **Plan de gestión de riesgos** completo de la práctica 7 (activos, amenazas, vulnerabilidades, matriz de riesgos, salvaguardas, riesgo residual).
3. **Política de contraseñas** y **política de copias de seguridad** básicas para el escenario elegido.
4. **Procedimiento de respuesta** a un incidente y análisis de **cumplimiento legal**.
5. **Conclusión** con las tres medidas más urgentes y su justificación.

#### Rúbrica

| Criterio | Peso | Excelente (100 %) | Adecuado (60 %) | Insuficiente (0-30 %) |
| --- | :-: | --- | --- | --- |
| Evidencias técnicas (RA1 b, c, e, i) | 30 % | Completas, explicadas e interpretadas | Completas pero poco explicadas | Faltan o no se interpretan |
| Análisis de riesgos (RA1 a, c) | 25 % | Activos, amenazas y vulnerabilidades coherentes; riesgos justificados | Coherente con errores menores | Confunde conceptos |
| Salvaguardas y respuesta (RA1 d, h) | 20 % | Proporcionadas, priorizadas y verificables | Adecuadas pero genéricas | Poco realistas |
| Cumplimiento legal (RA7) | 15 % | Identifica figuras, derechos, plazos y normas | Identifica lo básico | Ausente o incorrecto |
| Presentación y redacción técnica | 10 % | Clara, ordenada, sin errores | Algún error | Desordenada |

## Referencias y documentación oficial

- [VirtualBox: manual de usuario](https://www.virtualbox.org/manual/)
- [Debian: manual de seguridad (*Securing Debian Manual*)](https://www.debian.org/doc/manuals/securing-debian-manual/)
- [AlmaLinux: documentación](https://wiki.almalinux.org/)
- [The Sleuth Kit](https://www.sleuthkit.org/sleuthkit/)
- [Rastreador de seguridad de Debian](https://security-tracker.debian.org/tracker/)
- [INCIBE: Plan Director de Seguridad](https://www.incibe.es/empresas/que-te-interesa/plan-director-seguridad)
- [INCIBE: Guía de gestión de riesgos para empresas](https://www.incibe.es/empresas/guias)
- [MAGERIT v3](https://administracionelectronica.gob.es/pae_Home/pae_Documentacion/pae_Metodolog/pae_Magerit.html)
- [AEPD: Guía para la notificación de brechas de datos personales](https://www.aepd.es/guias/guia-brechas-seguridad.pdf)
