---
title: "Teoría"
slug: "teoria"
weight: 1
---

# UD7. Seguridad perimetral

> Cómo proteger el borde entre la red interna y las redes públicas: zonas de seguridad y DMZ, tipos de cortafuegos, filtrado con nftables, NAT y publicación de servicios, cortafuegos dedicados (OPNsense/pfSense), registros y diagnóstico, proxy directo con Squid, proxy inverso con Nginx, WAF y alta disponibilidad del perímetro.

| Datos de la unidad | Información |
| --- | --- |
| Módulo | 0378. Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR |
| Duración | 14 horas |
| Resultados de aprendizaje | RA1 (h) · RA3 (a, b) · RA4 (a–h) · RA5 (a–i) |
| Herramientas | nftables 1.x · OPNsense / pfSense CE · Squid 6 · Nginx · ModSecurity + OWASP CRS · Keepalived · conntrackd |

---

## 1. Introducción

Una empresa pequeña publica su web, da acceso a Internet a sus empleados y permite a un proveedor conectarse a un servidor. Si todo está en una única red plana con un router doméstico, **un solo fallo (un servidor web vulnerable) entrega al atacante toda la red interna**, incluidos los equipos de los empleados y los ficheros de contabilidad.

La **seguridad perimetral** define **dónde están los límites de la red**, qué zonas existen y **qué tráfico puede cruzar cada frontera**. El elemento central es el **cortafuegos** (*firewall*); a su alrededor se añaden **proxies**, sistemas de detección (UD6) y registros (UD4).

> [!NOTE]
> **Perímetro hoy.** El teletrabajo, la nube y las aplicaciones SaaS han difuminado el perímetro tradicional. Por eso el perímetro **no sustituye** a la defensa en profundidad ni al enfoque *Zero Trust* (UD6): es **una** capa, esencial, pero no la única. CE h de RA1: «reconocer la necesidad de un plan integral de protección perimetral».

## 2. Objetivos

- Describir las zonas de riesgo de un sistema y las arquitecturas de red perimetral (DMZ).
- Clasificar los cortafuegos y los niveles a los que filtran el tráfico.
- Planificar la instalación de cortafuegos y documentar las reglas con una matriz de flujos.
- Configurar un cortafuegos con **nftables** (filtrado con estado, NAT, registro).
- Publicar un servicio de la DMZ de forma segura (DNAT) y diagnosticar problemas de conectividad.
- Conocer cortafuegos dedicados (OPNsense, pfSense CE) y su administración.
- Instalar y configurar un **proxy directo** (Squid) con ACL, autenticación y modo transparente.
- Configurar un **proxy inverso** (Nginx) con TLS y valorar el papel de un WAF.
- Diseñar la **alta disponibilidad** del perímetro y la gestión de cambios.

---

## 3. Perímetro, zonas y arquitecturas

### 3.1. Zonas de seguridad

Una **zona** agrupa equipos con el mismo nivel de confianza y los mismos requisitos. Las zonas típicas:

| Zona | Contenido | Confianza | Quién puede entrar |
| --- | --- | --- | --- |
| **WAN / Internet** | Red pública | Ninguna | — |
| **DMZ** (*DeMilitarized Zone*) | Servidores publicados: web, correo, DNS público, VPN | Baja (expuesta) | Internet (solo servicios concretos) |
| **LAN** | Puestos de usuario, impresoras | Media | Solo desde dentro |
| **Servidores internos** | Bases de datos, ficheros, directorio | Alta | Solo la LAN y la DMZ, por puertos concretos |
| **Gestión** | Administración de equipos y cortafuegos | Muy alta | Solo administradores |
| **Invitados / IoT** | Equipos no gestionados | Nula | Solo Internet |

### 3.2. Arquitecturas clásicas

| Arquitectura | Descripción | Limitaciones |
| --- | --- | --- |
| **Router apantallado** (*screening router*) | Un router con ACL entre Internet y la red | Una sola barrera; sin DMZ |
| **Host bastión** | Un equipo muy fortificado que da servicios | Si cae, el atacante está dentro |
| **Doble interfaz** (*dual-homed*) | Equipo con dos tarjetas que separa dos redes | Mismo riesgo |
| **Subred apantallada con un cortafuegos** (*three-legged*) | Un cortafuegos con **tres interfaces**: WAN, LAN, DMZ | El cortafuegos es un SPOF y única barrera |
| **Subred apantallada con dos cortafuegos** | Cortafuegos externo → DMZ → cortafuegos interno (de **otro fabricante**, a ser posible) | Más caro; máxima defensa en profundidad |

```mermaid
flowchart LR
  I((Internet)) --- FW{{Cortafuegos<br/>tres patas}}
  FW --- D[DMZ<br/>web, correo, DNS<br/>172.16.0.0/24]
  FW --- L[LAN<br/>usuarios<br/>192.168.50.0/24]
```

```mermaid
flowchart LR
  I((Internet)) --- F1{{Cortafuegos<br/>externo}}
  F1 --- D[DMZ<br/>servidores publicados]
  D --- F2{{Cortafuegos<br/>interno}}
  F2 --- L[LAN y servidores<br/>internos]
```

**Reglas generales de la DMZ:**

1. Internet → DMZ: **solo** los puertos de los servicios publicados.
2. Internet → LAN: **nada** (salvo conexiones que la LAN haya iniciado).
3. LAN → DMZ: solo lo necesario (administración, web).
4. **DMZ → LAN: denegado**. Si se compromete un servidor expuesto, el atacante no debe poder avanzar hacia la red interna. Cualquier intento se **registra** como señal de compromiso.
5. DMZ → Internet: mínimo (actualizaciones, DNS, relé de correo).

### 3.3. Planificación: la matriz de flujos

Antes de escribir una sola regla se **planifica** (CE c de RA4) con una **matriz de flujos**: una tabla de qué zona puede hablar con cuál, por qué puerto y para qué.

| Origen | Destino | Servicio | Puerto | Acción | Justificación |
| --- | --- | --- | --- | --- | --- |
| Internet | `web-dmz` | HTTPS | 443/tcp | Permitir (DNAT) | Web corporativa |
| LAN | Internet | HTTP/HTTPS | 80, 443/tcp | Permitir | Navegación (vía proxy) |
| LAN | Internet | DNS, NTP | 53, 123/udp | Permitir | Resolución y hora |
| LAN | `web-dmz` | SSH | 22/tcp | Permitir (solo admins) | Administración |
| DMZ | LAN | Cualquiera | — | **Denegar y registrar** | Contención de compromisos |
| Cualquiera | Cualquiera | Cualquiera | — | **Denegar** | Política por defecto |

Esta tabla es, además, la **documentación** (CE h de RA4) y la base de las pruebas de aceptación: cada fila se comprueba con un test positivo y uno negativo.

---

## 4. Cortafuegos: tipos y niveles de filtrado

### 4.1. Qué es un cortafuegos

Un **cortafuegos** es un sistema (software o hardware) que **controla el tráfico entre redes** aplicando reglas. Su misión es permitir lo autorizado y descartar lo demás.

### 4.2. Niveles de filtrado

| Nivel | Capa OSI | Qué examina | Ejemplo de regla |
| --- | --- | --- | --- |
| **Filtrado de paquetes** (sin estado) | 3-4 | IP origen/destino, protocolo, puertos de **cada paquete** por separado | «Permitir TCP al puerto 80» |
| **Con estado** (*stateful*) | 3-4 | Lo anterior **más el estado de la conexión** (nueva, establecida, relacionada) | «Permitir respuestas a conexiones que yo inicié» |
| **De aplicación / proxy** | 7 | El contenido del protocolo (URL, métodos, comandos) | «Bloquear descargas `.exe`» |
| **NGFW** (*Next-Generation Firewall*) | 3-7 | Estado + identificación de aplicaciones, usuarios, IPS, filtrado TLS, antimalware | «Bloquear BitTorrent a los alumnos» |
| **WAF** (*Web Application Firewall*) | 7 (HTTP) | Peticiones web: detecta inyecciones, XSS… | «Bloquear una petición con `<script>`» |

**Por qué importa el estado.** Un filtro sin estado debe permitir **todo** el tráfico de respuesta por puertos altos (> 1024) para que funcionen las conexiones salientes: un agujero enorme. El cortafuegos con estado **recuerda** las conexiones iniciadas desde dentro y solo deja entrar las respuestas que corresponden a ellas. En Linux, esto lo gestiona **conntrack**:

| Estado `ct state` | Significado |
| --- | --- |
| `new` | Primer paquete de una conexión |
| `established` | Conexión ya vista en ambos sentidos |
| `related` | Conexión nueva asociada a una existente (p. ej. error ICMP, datos FTP) |
| `invalid` | Paquete que no encaja con ninguna conexión (se descarta) |

### 4.3. Software y hardware

| Tipo | Ejemplos | Ventajas | Inconvenientes |
| --- | --- | --- | --- |
| **Software en Linux** | nftables, firewalld, UFW | Gratis, muy flexible, automatizable | Requiere administración experta |
| **Distribución dedicada** (software libre) | **OPNsense**, **pfSense CE** | Interfaz web, VPN, IDS, proxy, HA integrados | Hay que dimensionar el hardware |
| **Appliance hardware** | Fortinet, Palo Alto, Cisco, Sophos, WatchGuard | Hardware especializado, soporte del fabricante, NGFW | Coste y licencias |
| **Cortafuegos de la nube** | Grupos de seguridad (AWS/Azure), Cloud Firewall | Escalables, integrados | Específicos de cada proveedor |

---

## 5. nftables: el cortafuegos de Linux

### 5.1. Netfilter y nftables

**Netfilter** es el marco del núcleo de Linux que intercepta los paquetes en puntos concretos de su recorrido (*hooks*). **nftables** es la herramienta moderna para definir reglas sobre esos *hooks*; **sustituye a iptables, ip6tables, arptables y ebtables**, que están **obsoletos** (iptables hoy suele ser una capa de compatibilidad sobre nftables).

```mermaid
flowchart LR
  E[Paquete entra] --> PRE[prerouting<br/>DNAT]
  PRE --> R{¿Para este equipo?}
  R -- sí --> IN[input]
  IN --> L[Proceso local]
  L --> OUT[output]
  OUT --> POST
  R -- no, reenviar --> FWD[forward]
  FWD --> POST[postrouting<br/>SNAT / masquerade]
  POST --> S[Paquete sale]
```

| Hook | Cuándo se evalúa | Uso típico |
| --- | --- | --- |
| `prerouting` | Nada más entrar, antes de decidir ruta | **DNAT** (cambiar destino) |
| `input` | Paquetes **dirigidos al propio cortafuegos** | Proteger el equipo (SSH, ICMP) |
| `forward` | Paquetes que el equipo **reenvía** entre redes | **Política entre zonas** (lo principal de un router) |
| `output` | Paquetes que genera el propio equipo | Limitar su salida |
| `postrouting` | Justo antes de salir | **SNAT / masquerade** |

**Estructura:** `tabla` → `cadena` → `regla`.

- **Tabla**: contenedor, con una *familia* (`ip`, `ip6`, `inet` = IPv4+IPv6, `bridge`, `arp`).
- **Cadena**: lista de reglas. Una **cadena base** se engancha a un *hook* (`type filter hook input priority filter; policy drop;`).
- **Regla**: condiciones + acción (`accept`, `drop`, `reject`, `log`, `counter`, `dnat`, `masquerade`…).
- **Política** (`policy`): qué se hace con lo que no coincide con ninguna regla. **Siempre `drop`** en un cortafuegos bien diseñado.

> [!NOTE]
> `drop` descarta sin avisar (el origen espera hasta agotar el tiempo); `reject` descarta y **responde** con un error (rápido, pero revela que hay un cortafuegos). Hacia Internet se suele usar `drop`; en la LAN, `reject` facilita el diagnóstico.

### 5.2. Comandos esenciales

```bash
sudo nft list ruleset                     # todas las reglas activas
sudo nft list table inet filtro           # una tabla concreta
sudo nft -c -f /etc/nftables.conf         # COMPRUEBA la sintaxis sin aplicar (-c = check)
sudo nft -f /etc/nftables.conf            # aplica el fichero
sudo nft flush ruleset                    # borra TODAS las reglas (¡y política abierta!)
sudo systemctl enable --now nftables      # carga /etc/nftables.conf al arrancar
sudo nft -a list ruleset                  # muestra el "handle" (identificador) de cada regla
sudo nft delete rule inet filtro entrada handle 12     # borra una regla concreta
```

Traducir reglas antiguas de iptables:

```bash
iptables-translate -A INPUT -p tcp --dport 22 -j ACCEPT
# nft 'add rule ip filter INPUT tcp dport 22 counter accept'
sudo iptables-save | sudo iptables-restore-translate   # traduce un conjunto completo (revisa el resultado)
```

### 5.3. Cortafuegos de tres zonas completo

Escenario del laboratorio (apartado 12 y prácticas): cortafuegos `fw` con tres interfaces.

| Zona | Interfaz | Red | Equipos |
| --- | --- | --- | --- |
| WAN | `enp0s3` | 192.168.100.0/24 (IP del `fw`: 192.168.100.100) | Cliente externo `sad-cli` (.10) |
| LAN | `enp0s8` | 192.168.50.0/24 (`fw`: .1) | `cli-lan` (.10) |
| DMZ | `enp0s9` | 172.16.0.0/24 (`fw`: .1) | `web-dmz` (172.16.0.10) |

Fichero `/etc/nftables.conf` (**haz copia antes**; validado con `nft -c`):

```text
#!/usr/sbin/nft -f
# Cortafuegos de tres zonas: WAN (enp0s3), LAN (enp0s8), DMZ (enp0s9)
flush ruleset

define WAN = "enp0s3"
define LAN = "enp0s8"
define DMZ = "enp0s9"
define WEB_DMZ = 172.16.0.10

table inet filtro {

  set admins {                         # conjunto de origen autorizado para administrar
    type ipv4_addr
    flags interval
    elements = { 192.168.50.0/24 }
  }

  chain entrada {                      # tráfico dirigido AL cortafuegos
    type filter hook input priority filter; policy drop;

    ct state established,related accept
    ct state invalid drop
    iif "lo" accept

    ip protocol icmp icmp type { echo-request, destination-unreachable, time-exceeded } limit rate 10/second accept
    ip6 nexthdr icmpv6 accept

    iifname $LAN ip saddr @admins tcp dport 22 accept       # SSH solo desde la LAN de administración
    iifname { $LAN, $DMZ } udp dport 53 accept              # DNS si el cortafuegos es resolutor

    limit rate 5/minute log prefix "FW-IN-DROP: " flags all
  }

  chain reenvio {                      # tráfico ENTRE zonas
    type filter hook forward priority filter; policy drop;

    ct state established,related accept
    ct state invalid drop

    # Internet → web de la DMZ (ya traducido por DNAT)
    iifname $WAN oifname $DMZ ip daddr $WEB_DMZ tcp dport { 80, 443 } ct status dnat accept

    # LAN → DMZ: solo web y SSH de administración
    iifname $LAN oifname $DMZ ip daddr $WEB_DMZ tcp dport { 22, 80, 443 } accept

    # LAN → Internet: navegación, DNS, NTP
    iifname $LAN oifname $WAN tcp dport { 80, 443 } accept
    iifname $LAN oifname $WAN udp dport { 53, 123 } accept

    # DMZ → Internet: solo actualizaciones y DNS
    iifname $DMZ oifname $WAN tcp dport { 80, 443 } accept
    iifname $DMZ oifname $WAN udp dport 53 accept

    # DMZ → LAN: PROHIBIDO; se registra porque indica un posible compromiso
    iifname $DMZ oifname $LAN limit rate 5/minute log prefix "DMZ-A-LAN: " flags all counter drop

    limit rate 5/minute log prefix "FW-FWD-DROP: " flags all
  }

  chain salida {
    type filter hook output priority filter; policy accept;
  }
}

table ip nat {
  chain prerouting {
    type nat hook prerouting priority dstnat; policy accept;
    iifname $WAN tcp dport { 80, 443 } dnat to $WEB_DMZ     # publica la web de la DMZ
  }
  chain postrouting {
    type nat hook postrouting priority srcnat; policy accept;
    oifname $WAN masquerade                                 # LAN y DMZ salen con la IP de la WAN
  }
}
```

Cómo leerlo:

- `define` crea variables reutilizables (cambiar de interfaz = cambiar una línea).
- `set admins` es un **conjunto** nombrado: se puede ampliar sin tocar las reglas (`nft add element inet filtro admins { 192.168.50.20 }`).
- La cadena `entrada` protege **el propio cortafuegos**; la cadena `reenvio` aplica la política **entre zonas**.
- `ct status dnat` exige que el paquete haya pasado por una regla DNAT: solo se permite lo que se publicó **expresamente**.
- `flags all` en `log` añade al mensaje detalles (cabeceras IP/TCP, UID…) que facilitan el análisis.
- Las reglas `log` van **al final** de cada cadena, con `limit rate`, para registrar lo descartado sin inundar el disco.

Aplicación segura y pruebas:

```bash
sudo cp /etc/nftables.conf /etc/nftables.conf.bak                 # copia de seguridad
echo 'net.ipv4.ip_forward = 1' | sudo tee /etc/sysctl.d/90-fw.conf && sudo sysctl --system    # el cortafuegos reenvía
sudo nft -c -f /etc/nftables.conf && echo "SINTAXIS CORRECTA"      # nunca apliques sin comprobar
sudo systemd-run --on-active=180 --unit=deshacer-fw nft flush ruleset    # "deshacer" automático a los 3 min
sudo nft -f /etc/nftables.conf                                    # aplica
# ...comprueba que sigues conectado y que las pruebas funcionan...
sudo systemctl stop deshacer-fw.timer                             # cancela el deshacer
sudo systemctl enable --now nftables                              # persistente
```

### 5.4. Conjuntos, mapas, medidores y bloqueos dinámicos

nftables permite estructuras muy potentes (todas validadas con `nft -c`):

```text
table inet demo {
  set bloqueados {                     # lista de IP con caducidad automática
    type ipv4_addr
    flags timeout
    timeout 1h
  }
  chain entrada {
    type filter hook input priority filter; policy drop;

    ip saddr @bloqueados drop                              # descarta a los bloqueados

    fib saddr . iif oif missing drop                       # anti-spoofing (rp_filter en nftables)

    tcp flags syn tcp dport 80 limit rate over 50/second burst 100 packets drop   # limita SYN

    # Máximo 5 conexiones nuevas por minuto y por IP al SSH (medidor por origen)
    ct state new tcp dport 22 meter ssh-flood { ip saddr limit rate over 5/minute } drop
    ct state new tcp dport 22 counter accept
  }
}
```

```bash
sudo nft add element inet demo bloqueados { 203.0.113.5 }          # bloquea una IP durante 1 hora (203.0.113.0/24 es una red de documentación)
sudo nft list set inet demo bloqueados                              # ver el conjunto y los tiempos restantes
sudo nft delete element inet demo bloqueados { 203.0.113.5 }        # desbloquear
```

Un **mapa** permite decisiones por tabla, por ejemplo publicar varios puertos externos hacia distintos destinos:

```text
table ip nat {
  map puertos_dnat {
    type inet_service : ipv4_addr . inet_service
    elements = { 8080 : 172.16.0.10 . 80, 8443 : 172.16.0.10 . 443 }
  }
  chain prerouting {
    type nat hook prerouting priority dstnat;
    dnat ip addr . port to tcp dport map @puertos_dnat
  }
}
```

### 5.5. firewalld y UFW en un router

- **firewalld** (AlmaLinux) trabaja con **zonas**: `external` (WAN, con masquerade), `internal` (LAN) y `dmz`. Es muy cómodo y usa nftables por debajo:

```bash
sudo firewall-cmd --permanent --zone=external --change-interface=enp0s3
sudo firewall-cmd --permanent --zone=internal --change-interface=enp0s8
sudo firewall-cmd --permanent --zone=dmz --change-interface=enp0s9
sudo firewall-cmd --permanent --zone=external --add-forward-port=port=443:proto=tcp:toaddr=172.16.0.10   # publicar HTTPS
sudo firewall-cmd --reload
sudo firewall-cmd --list-all-zones | less
```

- **UFW** (Debian/Ubuntu) es sencillo para hosts; para un router de tres zonas se recomienda nftables directamente.

> [!WARNING]
> Elige **una sola** herramienta de cortafuegos (como se advirtió en la UD4). Si usas `nftables.conf` propio, no tengas `firewalld` ni `ufw` activos.

---

## 6. NAT: traducción de direcciones

El **NAT** (*Network Address Translation*) modifica las direcciones de los paquetes al cruzar el cortafuegos. No es una medida de seguridad en sí (la seguridad la da el filtrado con estado), pero **oculta** el direccionamiento interno y permite compartir una IP pública.

| Tipo | Qué cambia | Para qué | Dónde |
| --- | --- | --- | --- |
| **SNAT** | IP **origen** (fija) | Salir a Internet con una IP pública conocida | `postrouting` |
| **Masquerade** | IP origen (la de la interfaz de salida, dinámica) | Salir con IP pública **dinámica** (DHCP) | `postrouting` |
| **DNAT** (*port forwarding*) | IP/puerto **destino** | **Publicar** un servicio interno | `prerouting` |
| **Hairpin NAT** | Origen y destino | Que la LAN acceda a un servicio publicado usando la IP pública | ambos |

```mermaid
sequenceDiagram
  participant C as Cliente 192.168.100.10
  participant F as Cortafuegos WAN 192.168.100.100
  participant W as web-dmz 172.16.0.10
  C->>F: SYN a 192.168.100.100:443
  Note over F: prerouting: DNAT → 172.16.0.10:443<br/>forward: ¿permitido? sí (regla ct status dnat)
  F->>W: SYN a 172.16.0.10:443
  W->>F: SYN-ACK (conntrack recuerda la traducción)
  F->>C: SYN-ACK desde 192.168.100.100:443
```

Elementos imprescindibles para que la **publicación** funcione, y que son motivo habitual de fallos:

1. Regla **DNAT** en `prerouting`.
2. Regla **forward** que permita el tráfico traducido hacia la DMZ.
3. `net.ipv4.ip_forward = 1`.
4. El servidor de la DMZ tiene como **puerta de enlace** el cortafuegos (para que la respuesta vuelva por él).
5. El servicio escucha en el puerto y no hay un cortafuegos local que lo bloquee.

**Hairpin NAT** (que `cli-lan` acceda a la web con la IP pública del cortafuegos):

```text
table ip nat {
  chain prerouting {
    type nat hook prerouting priority dstnat;
    iifname "enp0s8" ip daddr 192.168.100.100 tcp dport { 80, 443 } dnat to 172.16.0.10
  }
  chain postrouting {
    type nat hook postrouting priority srcnat;
    ip saddr 192.168.50.0/24 ip daddr 172.16.0.10 masquerade
  }
}
```

---

## 7. Fortificación de la pila TCP/IP en el cortafuegos

Ajustes de `sysctl` para un **router/cortafuegos** (distintos de los de un servidor normal, como se vio en la UD4: aquí **sí** se reenvía):

```bash
sudo tee /etc/sysctl.d/90-perimetro.conf >/dev/null <<'EOF'
net.ipv4.ip_forward = 1                       # es un router
net.ipv4.conf.all.rp_filter = 1               # descarta paquetes con origen imposible (anti-spoofing)
net.ipv4.conf.all.accept_redirects = 0        # no acepta redirecciones ICMP
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0     # no acepta enrutamiento de origen
net.ipv4.conf.all.log_martians = 1            # registra paquetes con direcciones imposibles
net.ipv4.tcp_syncookies = 1                   # protección contra SYN flood
net.ipv4.icmp_echo_ignore_broadcasts = 1      # no responde a ping a broadcast (evita amplificación)
net.netfilter.nf_conntrack_max = 262144       # tamaño de la tabla de conexiones
EOF
sudo sysctl --system
```

> [!NOTE]
> El parámetro `nf_conntrack_max` solo existe cuando el módulo `nf_conntrack` está cargado (lo está en cuanto hay reglas con estado). Si `sysctl --system` avisa de que no lo encuentra, ejecuta antes `sudo modprobe nf_conntrack`. Vigila la ocupación con `sudo conntrack -C` y `sysctl net.netfilter.nf_conntrack_count`.

**Filtrado de direcciones imposibles** (*bogons*) en la interfaz WAN: nada que venga de Internet puede tener una IP privada o de loopback como origen:

```text
iifname $WAN ip saddr { 10.0.0.0/8, 172.16.0.0/12, 127.0.0.0/8, 169.254.0.0/16 } drop   # en forward/input
```

(En el laboratorio la WAN usa 192.168.100.0/24 —privada— y esa red **no** debe bloquearse, así que se omite.)

---

## 8. Registro, análisis y diagnóstico

### 8.1. Dónde quedan los registros

Las reglas con `log` escriben en el **registro del kernel**, que `journald` recoge:

```bash
sudo journalctl -k --since "10 min ago" | grep -E 'FW-|DMZ-A-LAN'        # registros del cortafuegos
sudo journalctl -k -f | grep --line-buffered 'DMZ-A-LAN'                 # en tiempo real
```

Un registro típico:

```text
DMZ-A-LAN: IN=enp0s9 OUT=enp0s8 MAC=... SRC=172.16.0.10 DST=192.168.50.10 LEN=60 ... PROTO=TCP SPT=44512 DPT=445 SYN
```

Campos a recoger siempre: **fecha y hora**, **interfaz de entrada y salida**, **origen y destino**, **protocolo**, **puerto**, **regla** (prefijo) y **acción** (CE e de RA4). Sin hora sincronizada (NTP/chrony) los registros no sirven para correlacionar.

Contadores para ver si una regla se **aplica**:

```bash
sudo nft list ruleset | grep -E 'counter|packets'          # paquetes y bytes por regla
sudo conntrack -L | head                                   # conexiones en seguimiento
sudo conntrack -L | grep 172.16.0.10                       # las de un servidor concreto
```

### 8.2. Seguimiento de un paquete (`nftrace`)

Para saber **qué regla** toca un paquete (ideal para diagnosticar), se activa la traza solo para el tráfico que interesa:

```bash
sudo nft add table inet traza
sudo nft add chain inet traza pre '{ type filter hook prerouting priority -300; }'
sudo nft add rule inet traza pre ip saddr 192.168.50.10 tcp dport 80 meta nftrace set 1
sudo nft monitor trace                                      # (otra terminal: haz la petición desde 192.168.50.10)
# Limpieza al terminar:
sudo nft delete table inet traza
```

### 8.3. Diagnóstico de problemas de conectividad con el cortafuegos (CE g)

Método ordenado, de lo más sencillo a lo más profundo:

| Paso | Pregunta | Herramienta |
| --- | --- | --- |
| 1 | ¿Hay conectividad IP básica? | `ping`, `ip route get IP`, `ip -br a` |
| 2 | ¿Resuelve nombres? | `dig nombre`, `getent hosts nombre` |
| 3 | ¿El servicio escucha en el destino? | `ss -tlnp` en el servidor |
| 4 | ¿Llega el paquete al cortafuegos? | `tcpdump -ni enp0s8 host IP and port P` |
| 5 | ¿Sale por la otra interfaz? | `tcpdump -ni enp0s9 …` |
| 6 | ¿Vuelve la respuesta? | Mismo `tcpdump`; ruta de vuelta y *gateway* del servidor |
| 7 | ¿Qué regla lo descarta? | Registro (`journalctl -k`), contadores, `nft monitor trace` |
| 8 | ¿Es NAT? | `conntrack -L`, ver traducciones |

**Casos típicos:**

| Síntoma | Causa | Solución |
| --- | --- | --- |
| Timeout al conectar (nada responde) | `drop` en el cortafuegos o servicio parado | Registros/contadores; `ss -tlnp` |
| «Connection refused» inmediato | El puerto no escucha (o regla `reject`) | Arranca el servicio |
| Llegan SYN al servidor pero no hay respuesta en el cliente | El servidor no tiene el cortafuegos como *gateway* | Corrige la ruta por defecto |
| Funciona por IP pero no por nombre | DNS bloqueado (UDP/TCP 53) | Permite DNS |
| Conexiones largas que se caen | Tiempo de espera de `conntrack` o NAT | Ajusta *keepalives*, `nf_conntrack_tcp_timeout_established` |
| Páginas que cargan a medias | Problema de MTU/fragmentación (ICMP bloqueado) | Permite ICMP `destination-unreachable` (frag-needed) |

---

## 9. Cortafuegos dedicados: OPNsense y pfSense

### 9.1. Qué son

**OPNsense** y **pfSense CE** son distribuciones de cortafuegos/router basadas en **FreeBSD**, con **interfaz web** y funciones integradas: filtrado con estado (**pf**), NAT, VPN (WireGuard, IPsec, OpenVPN), IDS/IPS (Suricata), proxy (Squid), DNS, DHCP, alta disponibilidad (**CARP + pfsync**), informes y registros.

| | OPNsense | pfSense CE |
| --- | --- | --- |
| Licencia | BSD (código abierto) | Apache 2.0, edición CE (Netgate también ofrece versión comercial) |
| Ciclo de versiones | Semestral, actualizaciones frecuentes | Más espaciado |
| Interfaz | Moderna, API | Clásica, muy extendida |
| Plugins | Repositorio propio (WireGuard, Zenarmor, etc.) | Paquetes propios |
| Uso | Pymes, centros educativos | Pymes, centros educativos |

Para nuestro módulo son equivalentes: aprender uno permite manejar el otro. Se recomienda **OPNsense** en el laboratorio por su mantenimiento activo y su documentación.

### 9.2. Despliegue en VirtualBox (resumen)

1. Descarga la ISO de la edición oficial (`dvd` o `nano`) desde el sitio del proyecto y **verifica su hash** SHA-256 (UD3).
2. Crea una VM FreeBSD de 64 bits: 2 vCPU, 2 GiB de RAM, 20 GiB de disco y **tres adaptadores**:
   - Adaptador 1: **Red NAT `SAD-NAT`** → WAN.
   - Adaptador 2: **Red interna `sad-lan7`** → LAN.
   - Adaptador 3: **Red interna `sad-dmz`** → DMZ (opcional: *OPT1*).
3. Arranca la ISO e inicia sesión con el usuario `installer` para instalar al disco. **Cambia las credenciales por defecto inmediatamente.**
4. En la consola, asigna interfaces (WAN, LAN, OPT1) y la IP de la LAN (`192.168.50.1/24`).
5. Desde `cli-lan` (192.168.50.10) abre `https://192.168.50.1` para la interfaz web.

### 9.3. Configuración básica de la política

En la interfaz web (OPNsense; en pfSense es análogo):

| Tarea | Ruta del menú |
| --- | --- |
| Interfaces y direccionamiento | *Interfaces → Assignments*, *Interfaces → [LAN/OPT1]* |
| Alias (grupos de IP o puertos) | *Firewall → Aliases* |
| Reglas por interfaz | *Firewall → Rules → [WAN / LAN / DMZ]* |
| NAT de salida | *Firewall → NAT → Outbound* |
| Publicación (DNAT) | *Firewall → NAT → Port Forward* |
| Registros en vivo | *Firewall → Log Files → Live View* |
| Copia de configuración | *System → Configuration → Backups* |

Principios de las reglas en `pf` (distintos de nftables):

- Las reglas se aplican en la **interfaz de entrada** del tráfico (no hay cadenas input/forward separadas).
- El **orden** importa: se evalúa de arriba abajo; por defecto en una interfaz nueva (la DMZ) **todo está denegado**.
- Por defecto la WAN bloquea la entrada; la LAN permite todo salvo que se cambie. **Crea explícitamente** una política de mínimo privilegio.
- Siempre se habilita el **registro** en las reglas de bloqueo importantes.

### 9.4. Qué aporta frente a Linux puro

Gestión visual, actualizaciones del sistema, **backups de configuración con un clic**, **HA con CARP**, integración de IDS/IPS y de proxy, informes de tráfico. A cambio, hay que aprender la plataforma y su modelo de reglas.

---

## 10. Proxy: tipos y funciones

Un **proxy** es un intermediario: recibe peticiones de un cliente y las reenvía a un servidor, o al revés.

| Tipo | Quién lo conoce | Para qué | Ejemplo |
| --- | --- | --- | --- |
| **Proxy directo** (*forward*) | Los **clientes** (navegador configurado) | Controlar y registrar la salida a Internet; caché; filtrado | Squid en una empresa |
| **Proxy transparente** (*intercept*) | Nadie: el cortafuegos redirige el tráfico | Lo mismo, sin configurar clientes | Squid con DNAT del puerto 80 |
| **Proxy inverso** (*reverse*) | Los clientes de Internet creen hablar con el servidor | Proteger y publicar servidores: TLS, caché, balanceo, WAF | Nginx delante de una app |
| **Proxy de caché** | — | Ahorrar ancho de banda guardando contenido | Squid con `cache_dir` |
| **Proxy de autenticación** | — | Exigir usuario antes de navegar | Squid con `basic_ncsa_auth` |
| **Proxy SOCKS** | Aplicaciones | Túnel genérico TCP | `ssh -D` (UD6) |

```mermaid
flowchart LR
  subgraph "Proxy directo"
    U1[Usuarios LAN] --> P1[Squid]
    P1 --> I1((Internet))
  end
  subgraph "Proxy inverso"
    I2((Internet)) --> P2[Nginx<br/>TLS + WAF]
    P2 --> S1[App 1]
    P2 --> S2[App 2]
  end
```

**Funciones:** control de acceso, filtrado por dominio/horario, autenticación y trazabilidad (quién visitó qué), caché, antimalware (con ICAP), ocultación de la red interna, balanceo y terminación TLS (inverso).

> [!WARNING]
> Un proxy ve el tráfico de navegación de los usuarios: hay implicaciones de **privacidad** (RGPD, LOPDGDD, derechos de los trabajadores). Debe estar **informado** en la política de uso aceptable, registrar solo lo necesario y proteger los registros. La **inspección de HTTPS** (descifrar y volver a cifrar) requiere una CA propia instalada en los clientes y justificación legal y proporcionalidad; sin ella, el proxy solo ve los dominios (`CONNECT`), no el contenido.

---

## 11. Squid: proxy directo y de caché

**Squid** es el proxy de caché libre más veterano y usado. Escucha por defecto en el puerto **3128/tcp**. Versión de referencia: Squid 6.x (Debian 13, AlmaLinux 10).

### 11.1. Instalación

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo apt install -y squid apache2-utils          # apache2-utils aporta htpasswd
squid -v | head -1
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.bak
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo dnf install -y squid httpd-tools
squid -v | head -1
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.bak
```
{{% /tab %}}
{{< /tabs >}}

### 11.2. Configuración básica con ACL

La lógica de Squid: se **definen ACL** (`acl`) y luego se **combinan en reglas** (`http_access allow/deny`). Se evalúan **en orden** y gana la primera que coincide; por eso las **denegaciones específicas** van primero y `http_access deny all` al final.

Sustituye `/etc/squid/squid.conf` por esta versión mínima y comentada:

```text
# ---------- Redes y puertos ----------
acl lan src 192.168.50.0/24                 # clientes autorizados
acl Safe_ports port 80 443 21 70 210 1025-65535
acl SSL_ports port 443
acl CONNECT method CONNECT

# ---------- Restricciones de acceso ----------
acl dominios_bloqueados dstdomain "/etc/squid/bloqueados.txt"     # lista externa de dominios
acl horario_laboral time MTWHF 08:00-18:00                        # lunes a viernes, 8-18 h
acl redes_sociales dstdomain .facebook.com .instagram.com .tiktok.com

# ---------- Reglas (el orden importa) ----------
http_access deny !Safe_ports
http_access deny CONNECT !SSL_ports
http_access deny dominios_bloqueados
http_access deny redes_sociales horario_laboral            # bloqueadas SOLO en horario laboral
http_access allow lan
http_access deny all                                       # política por defecto

# ---------- Puerto y caché ----------
http_port 3128
cache_dir ufs /var/spool/squid 500 16 256      # 500 MB de caché en disco
cache_mem 128 MB
maximum_object_size 50 MB

# ---------- Registro y privacidad ----------
access_log stdio:/var/log/squid/access.log
visible_hostname proxy.lab.local
forwarded_for delete                           # no revela la IP interna del cliente
via off
```

Crea la lista de dominios bloqueados:

```bash
printf '.malwaredomain.test\n.casino-lab.test\n' | sudo tee /etc/squid/bloqueados.txt
```

(El punto inicial `.dominio` incluye los subdominios. Usa dominios ficticios o de prueba.)

Valida, inicializa la caché y arranca:

```bash
sudo squid -k parse                                    # comprueba sintaxis y lógica; indica errores y advertencias
sudo squid -z                                          # (solo si squid -k parse no dice que ya existe) crea la estructura de la caché
sudo systemctl enable --now squid
sudo systemctl status squid --no-pager
sudo ss -tlnp | grep 3128                              # escucha en 3128
sudo squid -k reconfigure                              # tras cada cambio: recarga sin cortar
```

### 11.3. Pruebas desde un cliente

```bash
curl -x http://192.168.50.1:3128 -I http://example.org/             # permitido: HTTP/1.1 200 OK (cabecera Via/X-Cache)
curl -x http://192.168.50.1:3128 -I http://prueba.casino-lab.test/   # denegado: 403 Forbidden (página de error de Squid)
curl -x http://192.168.50.1:3128 -I https://example.org/             # HTTPS por CONNECT (túnel, no se inspecciona)
sudo tail -f /var/log/squid/access.log                               # en el servidor
```

Formato de `access.log` (por defecto):

```text
1760000000.123    214 192.168.50.10 TCP_MISS/200 1256 GET http://example.org/ - HIER_DIRECT/93.184.216.34 text/html
```

| Campo | Significado |
| --- | --- |
| `1760000000.123` | Hora (formato Unix; `date -d @1760000000` la convierte) |
| `214` | Duración (ms) |
| `192.168.50.10` | Cliente |
| `TCP_MISS/200` | Resultado de caché (`HIT` = servido de caché, `MISS` = obtenido de Internet, `DENIED` = bloqueado) / código HTTP |
| `GET http://…` | Método y URL |
| `HIER_DIRECT/IP` | Cómo se obtuvo |

Estadísticas de caché: `sudo grep -c TCP_HIT /var/log/squid/access.log` y la utilidad `squidclient mgr:info` (si está instalada).

### 11.4. Autenticación de usuarios

Para saber **quién** navega, se exige usuario y contraseña mediante un **ayudante** (*helper*). Con fichero de contraseñas `htpasswd`:

```bash
sudo htpasswd -c /etc/squid/passwd ana                 # -c solo la primera vez (crea el fichero)
sudo htpasswd /etc/squid/passwd luis
sudo chown root:proxy /etc/squid/passwd && sudo chmod 640 /etc/squid/passwd      # Debian: grupo "proxy"; AlmaLinux: grupo "squid"
```

Añade a `squid.conf` (**antes** de las reglas `http_access allow lan`):

```text
auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd     # AlmaLinux: /usr/lib64/squid/basic_ncsa_auth
auth_param basic realm Proxy de la empresa
auth_param basic credentialsttl 2 hours
acl autenticados proxy_auth REQUIRED
```

Y cambia la regla de acceso:

```text
http_access allow lan autenticados          # en lugar de "http_access allow lan"
```

```bash
sudo squid -k parse && sudo squid -k reconfigure
curl -x http://192.168.50.1:3128 -I http://example.org/                              # 407 Proxy Authentication Required
curl -x http://ana:ClaveAna1@192.168.50.1:3128 -I http://example.org/                # 200 OK, y el log muestra el usuario
```

> [!NOTE]
> La autenticación **básica** viaja en Base64 (UD6): en entornos reales se integra con **LDAP/Active Directory** (helper `basic_ldap_auth`) o Kerberos/NTLM (`negotiate_kerberos_auth`), y se protege el segmento del proxy.

### 11.5. Proxy transparente

El **modo transparente** (`intercept`) evita configurar cada navegador: el cortafuegos **redirige** el puerto 80 de la LAN al proxy. Squid necesita un puerto especial para este modo:

```text
http_port 3128
http_port 3129 intercept               # puerto para tráfico interceptado
```

Y el cortafuegos (aquí el mismo `fw`, con Squid instalado en él) redirige el HTTP de la LAN, pero **no** el del propio proxy:

```text
table ip nat {
  chain prerouting {
    type nat hook prerouting priority dstnat; policy accept;
    iifname "enp0s8" ip saddr 192.168.50.0/24 tcp dport 80 redirect to :3129
  }
}
```

(`redirect` cambia el destino al propio equipo y al puerto indicado; añádelo a la tabla `ip nat` ya existente, sin duplicar la cadena `prerouting`).

Limitaciones del modo transparente:

- Solo intercepta **HTTP** con facilidad. El tráfico **HTTPS** exigiría inspección TLS (`ssl_bump`), una CA propia en todos los clientes y tiene implicaciones legales y de privacidad. Alternativa: dejar HTTPS pasar y **filtrar por nombre de dominio (SNI)** o por DNS.
- Con el modo transparente no hay autenticación por usuario (el navegador no sabe que existe un proxy).
- Para que no se eludan los controles, se **bloquea** en el cortafuegos la salida directa de la LAN por 80/443 y se permite solo la del proxy.

### 11.6. Monitorización con herramientas gráficas (CE g)

Con **SARG** (*Squid Analysis Report Generator*) se generan informes HTML a partir de `access.log`:

```bash
sudo apt install -y sarg apache2                       # Debian; en AlmaLinux está en EPEL
sudo sarg -l /var/log/squid/access.log -o /var/www/html/squid-reports
# Abre http://IP_DEL_PROXY/squid-reports/ : sitios más visitados, usuarios, volumen, bloqueados
```

Alternativas: **GoAccess** (informes en terminal y HTML), **Grafana + Loki/Prometheus**, **Zabbix** o el módulo de informes de OPNsense/pfSense. Protege el acceso a los informes (contienen la navegación de los usuarios).

### 11.7. Problemas frecuentes con clientes del proxy (CE f)

| Síntoma | Causa | Solución |
| --- | --- | --- |
| `403 Forbidden` (página de Squid) | Regla `http_access` o ACL | Revisa el orden de reglas; `access.log` muestra `TCP_DENIED` |
| `407 Proxy Authentication Required` en bucle | Credenciales erróneas o helper mal configurado | Prueba el helper a mano: `echo "ana ClaveAna1" \| /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd` → `OK` |
| `Connection refused` al proxy | Squid parado o puerto/cortafuegos | `systemctl status squid`, `ss -tlnp`, reglas de `input` |
| Webs HTTPS lentas o fallan | DNS o `CONNECT` bloqueado | `SSL_ports`, DNS del proxy |
| Squid no arranca | Error de configuración o permisos de la caché | `squid -k parse`; `journalctl -u squid`; `squid -z` |
| Actualizaciones de paquetes fallan en los servidores | Sin salida por proxy | Configura `Acquire::http::Proxy` en APT o `proxy=` en `dnf.conf` |

---

## 12. Proxy inverso con Nginx

### 12.1. Qué problema resuelve

Un **proxy inverso** se sitúa **delante de los servidores web**: los clientes de Internet hablan con él y él, internamente, con los servidores reales. Aporta:

- **Un único punto de entrada**: los servidores internos no se exponen (solo escucha el proxy).
- **Terminación TLS**: gestiona los certificados (UD3) en un solo lugar; los backends pueden hablar HTTP interno.
- **Publicar varias aplicaciones** bajo un mismo dominio y puerto (por ruta o nombre de host).
- **Balanceo** entre varios servidores (UD5) y comprobaciones de salud.
- **Protección**: limitación de peticiones, cabeceras de seguridad, filtrado (WAF), ocultar versiones.
- **Caché** de contenido estático.

### 12.2. Instalación y configuración básica

```bash
sudo apt install -y nginx                        # AlmaLinux: sudo dnf install -y nginx
nginx -v
```

Dos aplicaciones de prueba internas (en Python, solo para laboratorio) que escuchan **solo** en el equipo local:

```bash
mkdir -p ~/app-a ~/app-b && echo "App A" > ~/app-a/index.html && echo "App B" > ~/app-b/index.html
(cd ~/app-a && python3 -m http.server 8081 --bind 127.0.0.1 >/dev/null 2>&1 &)
(cd ~/app-b && python3 -m http.server 8082 --bind 127.0.0.1 >/dev/null 2>&1 &)
```

Proxy inverso en `/etc/nginx/conf.d/proxy.conf`:

```nginx
server {
    listen 80 default_server;
    server_name _;
    server_tokens off;                              # oculta la versión de Nginx

    location /app-a/ {
        proxy_pass http://127.0.0.1:8081/;          # la barra final sustituye el prefijo /app-a/
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /app-b/ {
        proxy_pass http://127.0.0.1:8082/;
        proxy_set_header Host              $host;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo rm -f /etc/nginx/sites-enabled/default      # Debian: quita el sitio por defecto que ocupa el puerto 80
sudo nginx -t                                     # comprueba sintaxis: "syntax is ok / test is successful"
sudo systemctl enable --now nginx && sudo systemctl reload nginx
curl -s http://localhost/app-a/                   # App A
curl -s http://localhost/app-b/                   # App B
```

**Comprobación de que los backends no se exponen:** desde **otra máquina**, `curl -m 3 http://IP_PROXY:8081/` debe fallar (están en `127.0.0.1`), pero `http://IP_PROXY/app-a/` funciona. En AlmaLinux, si SELinux bloquea la conexión: `sudo setsebool -P httpd_can_network_connect on`.

### 12.3. TLS en el proxy inverso

Con el certificado generado en la UD3 (CA propia) o con un certificado autofirmado de laboratorio:

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name web.lab.local;
    server_tokens off;

    ssl_certificate     /etc/ssl/lab/web.crt;
    ssl_certificate_key /etc/ssl/lab/web.key;
    ssl_protocols       TLSv1.2 TLSv1.3;                 # sin TLS 1.0/1.1
    ssl_prefer_server_ciphers off;

    add_header Strict-Transport-Security "max-age=31536000" always;   # HSTS: el navegador exige HTTPS
    add_header X-Content-Type-Options    "nosniff" always;
    add_header X-Frame-Options           "DENY" always;
    add_header Referrer-Policy           "no-referrer" always;

    location / {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host              $host;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {                                                  # redirige HTTP → HTTPS
    listen 80;
    server_name web.lab.local;
    return 301 https://$host$request_uri;
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
curl -vk https://localhost/ 2>&1 | grep -E 'SSL connection|subject|HTTP/'        # protocolo TLS y certificado
curl -sI https://localhost/ -k | grep -i strict-transport                           # cabecera HSTS
```

### 12.4. Balanceo y limitación de peticiones

El proxy inverso puede repartir entre varios servidores (UD5) y limitar abusos:

```nginx
# En el contexto http { } (por ejemplo, /etc/nginx/conf.d/limites.conf)
limit_req_zone  $binary_remote_addr zone=por_ip:10m rate=10r/s;     # 10 peticiones/s por IP
limit_conn_zone $binary_remote_addr zone=conex_ip:10m;

upstream app_servers {
    least_conn;
    server 172.16.0.11:80 max_fails=3 fail_timeout=10s;
    server 172.16.0.12:80 max_fails=3 fail_timeout=10s;
    server 172.16.0.13:80 backup;                      # solo si caen los demás
}

server {
    listen 80;
    location / {
        limit_req  zone=por_ip burst=20 nodelay;       # absorbe ráfagas de 20 y rechaza el exceso (503)
        limit_conn conex_ip 20;                        # máximo 20 conexiones simultáneas por IP
        proxy_pass http://app_servers;
    }
}
```

Prueba (solo contra tu servidor): `ab -n 200 -c 20 http://localhost/` y observa `Non-2xx responses`. Las peticiones rechazadas aparecen en `/var/log/nginx/error.log` como `limiting requests`.

### 12.5. WAF: cortafuegos de aplicación web

Un **WAF** inspecciona las **peticiones HTTP/HTTPS** y bloquea patrones de ataque: inyección SQL, XSS, *path traversal*, etc. Se coloca **delante** de la aplicación, normalmente integrado en el proxy inverso.

| Elemento | Descripción |
| --- | --- |
| **ModSecurity** | Motor de reglas WAF libre (hoy bajo OWASP), versión 3 como librería para Nginx |
| **OWASP CRS** (*Core Rule Set*) | Conjunto de reglas genéricas mantenido por OWASP |
| **Coraza** | Motor WAF moderno compatible con CRS, escrito en Go (módulos para Caddy, Nginx, etc.) |
| **Modos** | `DetectionOnly` (registra, no bloquea) y `On` (bloquea) |

**Flujo recomendado:** instalar en modo **detección** → revisar el registro durante días (falsos positivos) → ajustar exclusiones → pasar a **bloqueo**.

Ejemplo de uso con paquetes de Debian (comprueba que existen en tu versión: `apt search modsecurity`):

```bash
sudo apt install -y libnginx-mod-http-modsecurity modsecurity-crs
```

Se activa en el servidor (rutas orientativas; revisa la documentación del paquete):

```nginx
modsecurity on;
modsecurity_rules_file /etc/nginx/modsecurity/main.conf;
```

con `main.conf` que incluye `SecRuleEngine DetectionOnly` y las reglas de CRS. Prueba defensiva **solo contra tu propio servidor**, con cadenas inofensivas que las reglas reconocen como patrones:

```bash
curl -s -o /dev/null -w '%{http_code}\n' "http://localhost/?q=<script>alert(1)</script>"      # XSS de prueba
curl -s -o /dev/null -w '%{http_code}\n' "http://localhost/?file=../../etc/passwd"           # recorrido de rutas de prueba
sudo tail -n 20 /var/log/modsec_audit.log                                                   # eventos detectados
```

En modo detección ambas devuelven `200` y quedan en el registro de auditoría; con `SecRuleEngine On`, devolverían `403`. Un WAF **complementa**, no sustituye, al código seguro y a las actualizaciones de la aplicación.

---

## 13. Alta disponibilidad y gestión del perímetro

### 13.1. El cortafuegos como SPOF

Si el cortafuegos cae, **toda la organización pierde conectividad**. Se duplica con (UD5):

```mermaid
flowchart LR
  I((Internet)) --- FA{{fw-a<br/>MASTER}}
  I --- FB{{fw-b<br/>BACKUP}}
  FA --- L[LAN<br/>192.168.50.254 VIP]
  FB --- L
  FA <-->|sincronización de estado<br/>conntrackd| FB
```

- **IP virtual** con VRRP (Keepalived) en cada zona: WAN, LAN, DMZ. Los equipos usan la **VIP** como puerta de enlace.
- **Sincronización de reglas**: un repositorio (Git) y despliegue automatizado a ambos nodos, o la sincronización integrada de OPNsense/pfSense.
- **Sincronización de estado de conexiones** con **conntrackd**: al conmutar, las conexiones TCP establecidas **no se cortan** (si no, todos los usuarios reconectarían).
- En OPNsense/pfSense: **CARP** (IP virtual) + **pfsync** (estado) + **XMLRPC** (configuración).

Ejemplo mínimo con Keepalived en el cortafuegos de Linux (resumen; ver UD5 para el detalle):

```text
vrrp_instance FW_LAN {
    state MASTER
    interface enp0s8
    virtual_router_id 61
    priority 150
    advert_int 1
    unicast_src_ip 192.168.50.2
    unicast_peer { 192.168.50.3 }
    virtual_ipaddress { 192.168.50.254/24 dev enp0s8 }
}
```

Y una instancia análoga para la WAN y la DMZ, agrupadas con `vrrp_sync_group` para que **todas conmuten a la vez** (si solo cambia una pata, el tráfico se rompe).

**Prueba de fallo:** `sudo systemctl stop keepalived` en el principal mientras hay un `ping`/`ssh` continuo desde la LAN a Internet; mide la interrupción y comprueba si la conexión SSH sobrevive (con `conntrackd`, sí).

### 13.2. Gestión de cambios y copias de la configuración

Un perímetro se rompe más por **cambios mal hechos** que por ataques. Buenas prácticas:

1. **Copia** de la configuración antes de cada cambio y **versionado**: `sudo nft list ruleset > fw-$(date +%F).nft` y guardarlo en Git (sin secretos).
2. **Comprobar sintaxis** antes de aplicar (`nft -c -f`).
3. **Red de seguridad**: «deshacer» programado (`systemd-run --on-active`) o `at`.
4. **Ventana de cambios** y aprobación: quién, por qué, cuándo y cómo revertir.
5. **Pruebas positivas y negativas** tras cada cambio (la matriz de flujos).
6. **Revisión periódica de reglas**: eliminar las obsoletas, comprobar con contadores cuáles no se usan.
7. **Copias cifradas y fuera del equipo** de la configuración (contiene información sensible):

```bash
sudo nft list ruleset | gpg --symmetric --cipher-algo AES256 -o fw-$(date +%F).nft.gpg     # copia cifrada (UD3)
```

### 13.3. Documentación (CE h)

La documentación del cortafuegos debe incluir: **diagrama** de zonas, **matriz de flujos** (aprobada), **ficheros de configuración** versionados, **procedimiento de instalación y restauración**, **pruebas de aceptación** realizadas, **inventario** de excepciones y su caducidad, y **contactos** y escalado.

---

## 14. Ejemplo integrado: ciclo defensivo del perímetro

| Fase | Contenido |
| --- | --- |
| **Amenaza** | Un atacante en Internet busca servidores web vulnerables |
| **Vulnerabilidad** | La web de la DMZ tiene un componente desactualizado |
| **Ataque** | El atacante consigue ejecutar código en el servidor de la DMZ y trata de alcanzar la LAN |
| **Detección** | Regla `DMZ-A-LAN` registra y **cuenta** los intentos; el WAF registra las peticiones anómalas; Suricata (UD6) alerta; Wazuh (UD4) detecta cambios de ficheros |
| **Mitigación** | La política **DMZ → LAN = denegado** contiene el compromiso; se aísla el servidor, se restaura desde copia (UD2) y se corrige la vulnerabilidad |
| **Comprobación** | Se repite la prueba negativa (DMZ → LAN falla), se verifica el parche y se actualiza la matriz de flujos |

---

## 15. Problemas habituales (resumen)

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| La web de la DMZ no es accesible desde Internet | Falta `ip_forward`, DNAT o regla `forward`; *gateway* del servidor | Seguir el método de diagnóstico del apartado 8.3 |
| El cortafuegos bloquea su propio SSH | Cadena `input` sin regla de administración | Consola de la VM; `nft flush ruleset`; «deshacer» programado |
| Los registros no aparecen | `log` no alcanzado (regla anterior acepta) o `limit` | Orden de las reglas; `nft list ruleset` con contadores |
| Squid devuelve 403 a todos | `acl lan` no coincide con la red real | `squid -k parse`; mira la IP origen en `access.log` |
| Nginx: `502 Bad Gateway` | Backend parado o SELinux | `ss -tlnp`; `error.log`; `setsebool -P httpd_can_network_connect on` |
| Tras cambiar reglas se pierden conexiones | `flush ruleset` borra el estado/reglas | Aplica con `nft -f` completo; usa «deshacer» |
| Fallos intermitentes con dos cortafuegos | Las tres patas no conmutan a la vez | `vrrp_sync_group` y `conntrackd` |

---

## 16. Buenas prácticas

- **Política por defecto: denegar.** Todo lo permitido, documentado y justificado.
- **Matriz de flujos** antes de las reglas; pruebas positivas y negativas tras ellas.
- **DMZ → LAN denegado y registrado.**
- **Mínimo de servicios en el cortafuegos**: solo administración desde la red de gestión.
- **Registrar con límite**; sincronizar la hora; centralizar los registros.
- **Un solo gestor de cortafuegos** por equipo; versionar la configuración.
- **Cambios con red de seguridad**: copia, `nft -c`, «deshacer» programado.
- **Proxy**: informar a los usuarios, minimizar y proteger los registros, y no inspeccionar TLS sin justificación.
- **WAF**: primero detección; no confiar solo en él.
- **Perímetro redundado** con sincronización de estado, y pruebas de conmutación periódicas.

---

## 17. Ejercicios

1. Explica la diferencia entre un cortafuegos con estado y uno sin estado. ¿Qué agujero obligaría a abrir un filtro sin estado para permitir navegar?
2. Dibuja la matriz de flujos de una empresa con LAN, DMZ (web y correo), Internet y una VLAN de invitados.
3. En la configuración de tres zonas del apartado 5.3, ¿qué ocurre si cambias la política de `reenvio` a `accept`? ¿Y si eliminas `ct state established,related accept`?
4. ¿Qué cinco elementos deben cumplirse para que la publicación de un servidor de la DMZ funcione? Indica qué síntoma produce cada fallo.
5. Escribe las reglas nftables que bloqueen 1 h las IP que superen 5 conexiones nuevas por minuto al SSH.
6. Un cliente recibe «407» continuamente tras configurar autenticación en Squid. Describe cómo diagnosticarlo.
7. Redacta el bloque `acl` y `http_access` de Squid que permita a los profesores navegar siempre y a los alumnos solo entre las 8:00 y las 15:00, y bloquee `.juegos-lab.test` para todos.
8. ¿Qué diferencia hay entre un proxy directo, uno transparente y uno inverso? Pon un caso de uso de cada uno.
9. ¿Por qué un WAF debe iniciarse en modo detección?
10. Diseña la secuencia de pasos para sustituir el cortafuegos principal por otro con una ventana de 10 minutos, minimizando el riesgo.

{{% details "Soluciones orientativas" %}}
1. El filtro sin estado trata cada paquete por separado: para que las respuestas a conexiones salientes entren, hay que permitir todo el tráfico entrante a puertos altos (> 1024) desde cualquier origen. El cortafuegos con estado (conntrack) solo permite las respuestas de conexiones iniciadas desde dentro.
2. Respuesta abierta: LAN→Internet (80/443/53/123), Internet→DMZ (80/443 web, 25 correo), LAN→DMZ (solo administración y webmail), DMZ→LAN denegado, Invitados→Internet únicamente, Invitados→LAN/DMZ denegado.
3. Con `accept` por defecto en `reenvio`, el cortafuegos deja pasar todo lo no prohibido: se pierde la protección (la DMZ podría llegar a la LAN). Sin `established,related` fallan las respuestas: las conexiones salientes no vuelven y los servicios publicados no responden.
4. (1) DNAT en `prerouting` (sin él: el paquete llega al cortafuegos y no al servidor); (2) regla `forward` (sin ella: timeout); (3) `ip_forward=1` (sin él: no se reenvía); (4) *gateway* del servidor = cortafuegos (llegan SYN pero no vuelve el SYN-ACK al cliente); (5) servicio escuchando (rechazo inmediato `Connection refused`).
5. `set bloqueados { type ipv4_addr; flags timeout; timeout 1h; }` + `ip saddr @bloqueados drop` + `ct state new tcp dport 22 meter flood { ip saddr limit rate over 5/minute } add @bloqueados { ip saddr } drop`, seguidas de `ct state new tcp dport 22 accept` (validado con `nft -c` en nftables 1.0.9).
6. Probar el *helper* a mano (`echo "ana clave" | /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd` → `OK`), revisar la ruta del ayudante y los permisos del fichero de contraseñas, `squid -k parse`, y el log (`access.log`/`cache.log`).
7. `acl profesores src 192.168.50.0/26`, `acl alumnos src 192.168.50.64/26`, `acl horario_alumnos time 08:00-15:00`, `acl juegos dstdomain .juegos-lab.test`; reglas: `http_access deny juegos`, `http_access allow profesores`, `http_access allow alumnos horario_alumnos`, `http_access deny all`.
8. Directo: los clientes lo configuran, controla la salida a Internet; transparente: el cortafuegos redirige el HTTP, sin configurar clientes; inverso: delante de servidores para publicar con TLS, balanceo y WAF.
9. Porque las reglas genéricas generan falsos positivos que bloquearían usuarios legítimos; en detección se registran y se ajustan las exclusiones antes de activar el bloqueo.
10. Copia de la configuración y de las reglas; aprovisionar el nuevo con la misma configuración y probarlo aislado; comunicar la ventana; «deshacer» preparado; cambio de cables/rutas o VIP; pruebas positivas y negativas de la matriz de flujos; monitorización reforzada; plan de vuelta atrás.
{{% /details %}}

---

## 18. Actividad práctica: supuesto profesional

> [!IMPORTANT]
> **Supuesto.** *Colegio San Jorge* tiene una LAN de administración (30 equipos), una LAN de aulas (200 equipos), un servidor web con la intranet y la web pública, y un servidor de correo. Hoy todo está detrás de un router del operador, con puertos abiertos hacia el servidor web y el correo directamente conectados a la red de administración.

Entrega:

1. **Análisis de riesgos** y zonas propuestas, con diagrama de la nueva arquitectura (DMZ, LAN administración, LAN aulas, Wi-Fi invitados).
2. **Matriz de flujos** completa y reglas nftables (o capturas de OPNsense) que la implementan, con política por defecto `drop`.
3. **Proxy** para las aulas: Squid con ACL por horario, filtrado por dominios y registro; justificación de la decisión sobre HTTPS y privacidad.
4. **Publicación segura** de la web con Nginx como proxy inverso (TLS, cabeceras, limitación) y valoración de un WAF.
5. **Registros y pruebas**: qué se registra, dónde y quién lo revisa; pruebas positivas y negativas con evidencias.
6. **Continuidad**: propuesta de alta disponibilidad del cortafuegos y procedimiento de restauración desde copia.

Las prácticas guiadas están en [Prácticas](../practicas/).

---

## 19. Resumen

- El **perímetro** separa zonas de confianza; la **DMZ** aloja lo expuesto y no debe poder alcanzar la LAN.
- Los cortafuegos filtran en capas 3-4 (con estado) o 7 (aplicación, WAF, NGFW); en Linux, **nftables** sustituye a iptables.
- Se **planifica** con una matriz de flujos, se aplica con **política `drop`**, se **registra** con límite y se **comprueba** con pruebas positivas y negativas.
- **NAT**: SNAT/masquerade para salir, **DNAT** para publicar (con `forward`, `ip_forward` y *gateway* correctos).
- **OPNsense/pfSense** ofrecen todo esto con interfaz web, VPN, IDS y HA (CARP + pfsync).
- **Squid** controla y registra la navegación (ACL, autenticación, transparente, informes); **Nginx** como **proxy inverso** protege y publica (TLS, límites) y un **WAF** inspecciona las peticiones web.
- El perímetro también debe ser **redundante** y **gestionarse con control de cambios**: copias, sintaxis, «deshacer», pruebas y documentación.

---

## 20. Referencias y documentación oficial

- Netfilter / nftables. *nftables wiki*. <https://wiki.nftables.org>
- Netfilter. *nft(8)*. <https://www.netfilter.org/projects/nftables/manpage.html>
- OPNsense. *Documentation*. <https://docs.opnsense.org>
- Netgate. *pfSense CE Documentation*. <https://docs.netgate.com/pfsense/en/latest/>
- Squid. *Documentación y configuración*. <http://www.squid-cache.org/Doc/>
- Nginx. *Documentation (Reverse Proxy, ngx_http_limit_req_module)*. <https://nginx.org/en/docs/>
- OWASP. *ModSecurity Core Rule Set (CRS)*. <https://coreruleset.org>
- OWASP. *Coraza WAF*. <https://coraza.io>
- Keepalived y conntrack-tools. <https://www.keepalived.org> · <https://conntrack-tools.netfilter.org>
- NIST. *SP 800-41 Rev. 1: Guidelines on Firewalls and Firewall Policy*. <https://csrc.nist.gov/pubs/sp/800/41/r1/final>
- CCN-STIC. *Guías de seguridad de cortafuegos y perímetro*. <https://www.ccn-cert.cni.es/guias.html>
- INCIBE. *Guías de ciberseguridad*. <https://www.incibe.es>
