---
title: "UD6 · Prácticas"
weight: 2
bookToc: true
---

# UD6 · Prácticas

{{< ra "RA1:h" "RA3" "RA4" "RA5" >}}

Perímetro con WAN, LAN y DMZ en un cortafuegos Linux (nftables), NAT y publicación, proxy directo e inverso, y acceso remoto seguro con SSH, WireGuard y RADIUS, con prueba de fallo del perímetro.

| Práctica | Tipo | Nivel | Horas | CE principales |
|---|---|---|--:|---|
| [6.1 Perímetro, zonas y matriz de flujos](#práctica-61--perímetro-zonas-y-matriz-de-flujos) | Guiada | ●○○ | 1 | RA1: h · RA3: a, b |
| [6.2 Cortafuegos con nftables y política `drop`](#práctica-62--cortafuegos-con-nftables-y-política-drop) | Guiada | ●●● | 2 | RA4: b, c, d |
| [6.3 NAT y publicación de un servicio en la DMZ](#práctica-63--nat-y-publicación-de-un-servicio-en-la-dmz) | Guiada | ●●○ | 1 | RA4: c, d |
| [6.4 Endurecimiento TCP/IP, registro y diagnóstico](#práctica-64--endurecimiento-tcpip-registro-y-diagnóstico) | Autónoma | ●●○ | — | RA4: e, g |
| [6.5 Proxy directo con Squid](#práctica-65--proxy-directo-con-squid) | Guiada | ●●○ | 2 | RA5: b, c, d, e, g |
| [6.6 Proxy inverso con Nginx, TLS y WAF](#práctica-66--proxy-inverso-con-nginx-tls-y-waf) | Guiada | ●●● | 1 | RA5: a, f |
| [6.7 Cortafuegos dedicado: OPNsense (opcional)](#práctica-67--cortafuegos-dedicado-opnsense-opcional) | Autónoma | ●●○ | — | RA4: f |
| [6.8 Alta disponibilidad y recuperación del perímetro](#práctica-68--alta-disponibilidad-y-recuperación-del-perímetro) | Guiada | ●●● | 1 | RA4: g |
| [6.9 Protocolos seguros y SSH avanzado](#práctica-69--protocolos-seguros-y-ssh-avanzado) | Guiada | ●●○ | 1 | RA3: c, f |
| [6.10 VPN de acceso remoto con WireGuard](#práctica-610--vpn-de-acceso-remoto-con-wireguard) | Guiada | ●●● | 2 | RA3: d, e |
| [6.11 Autenticación centralizada con FreeRADIUS](#práctica-611--autenticación-centralizada-con-freeradius) | Guiada | ●●● | 1 | RA3: f, g |
| [6.12 VPN sitio a sitio con IPsec (opcional)](#práctica-612--vpn-sitio-a-sitio-con-ipsec-opcional) | Autónoma | ●●● | — | RA3: d |
| [6.13 Seguridad perimetral del Colegio San Jorge](#tarea-del-proyecto--seguridad-perimetral-del-colegio-san-jorge) | Proyecto | ●●● | 2 | RA1: h · RA3 · RA4 · RA5 |
| **Total** | | | **14 h** | |

> [!NOTE]
> Las prácticas con **—** horas son **trabajo autónomo** (fuera del horario) u opcionales: amplían la unidad, pero no restan tiempo a las 14 h de prácticas oficiales de la unidad. El resto se realiza en el laboratorio, en las horas indicadas.

## Objetivos

- Desplegar una arquitectura de subred apantallada (WAN, LAN, DMZ) con un cortafuegos de tres patas.
- Planificar las reglas con una **matriz de flujos** y aplicarlas con política de denegación por defecto.
- Publicar un servidor de la DMZ mediante **DNAT** y comprobar que la DMZ no puede alcanzar la LAN.
- Revisar los registros del cortafuegos, interpretarlos y **diagnosticar** fallos de conectividad.
- Instalar un proxy **Squid** con ACL, autenticación y modo transparente, y monitorizarlo.
- Configurar un proxy inverso **Nginx** con TLS, cabeceras de seguridad y limitación de peticiones; valorar un WAF.
- Diseñar y probar la alta disponibilidad y la restauración del cortafuegos.
- Configurar acceso remoto seguro: SSH avanzado, VPN con WireGuard y autenticación centralizada con RADIUS.

> [!IMPORTANT]
> **Alcance.** Todo el laboratorio es virtual y aislado. Las pruebas de bloqueo se hacen **solo** contra tus máquinas. No uses herramientas de evasión ni de ataque contra destinos ajenos. Antes de tocar el cortafuegos crea una *snapshot* y deja siempre una consola de VirtualBox abierta como acceso de emergencia.

## Preparación del laboratorio

#### Topología y direccionamiento

```mermaid
flowchart LR
  subgraph WAN["WAN: SAD-NAT 192.168.100.0/24"]
    EXT[sad-cli<br/>192.168.100.10<br/>«Internet»]
  end
  FW{{fw<br/>WAN .100 · LAN .1 · DMZ .1}}
  subgraph LAN["LAN: sad-lan7 192.168.50.0/24"]
    CLI[cli-lan<br/>192.168.50.10]
  end
  subgraph DMZ["DMZ: sad-dmz 172.16.0.0/24"]
    WEB[web-dmz<br/>172.16.0.10]
  end
  EXT --- FW
  FW --- CLI
  FW --- WEB
```

| VM | Adaptadores de VirtualBox | IP | Puerta de enlace |
| --- | --- | --- | --- |
| `fw` | 1: `SAD-NAT` · 2: `sad-lan7` · 3: `sad-dmz` | WAN `enp0s3` 192.168.100.100/24 · LAN `enp0s8` 192.168.50.1/24 · DMZ `enp0s9` 172.16.0.1/24 | 192.168.100.1 (VirtualBox, da salida real a Internet) |
| `cli-lan` | `sad-lan7` | 192.168.50.10/24 | 192.168.50.1 |
| `web-dmz` | `sad-dmz` | 172.16.0.10/24 | 172.16.0.1 |
| `sad-cli` | `SAD-NAT` | 192.168.100.10/24 | 192.168.100.1 |

> [!NOTE]
> Los nombres de interfaz (`enp0s3`, `enp0s8`, `enp0s9`) son los habituales en VirtualBox, pero compruébalos con `ip -br a` y sustitúyelos si son distintos. Las direcciones configuradas con `ip addr` **se pierden al reiniciar**; para hacerlas persistentes usa la configuración de red de tu distribución (NetworkManager, `systemd-networkd` o `/etc/network/interfaces`).

#### Primero, instalar paquetes (mientras hay salida a Internet)

En `fw` (con la WAN todavía por DHCP o con la ruta por defecto funcionando):

```bash
sudo apt update && sudo apt install -y nftables squid apache2-utils nginx tcpdump conntrack nmap curl dnsutils sarg netcat-openbsd
# AlmaLinux: sudo dnf install -y nftables squid httpd-tools nginx tcpdump conntrack-tools nmap curl bind-utils
```

En `web-dmz`:

```bash
sudo apt update && sudo apt install -y apache2 openssh-server netcat-openbsd curl && echo "<h1>web-dmz</h1>" | sudo tee /var/www/html/index.html
```

En `cli-lan` y `sad-cli`: `sudo apt install -y curl nmap tcpdump netcat-openbsd` (AlmaLinux: `nmap-ncat`).

Crea la carpeta de evidencias en cada VM: `mkdir -p ~/ud7-evidencias && chmod 700 ~/ud7-evidencias`.

#### Direccionamiento

**`fw`:**

```bash
sudo ip addr add 192.168.100.100/24 dev enp0s3 2>/dev/null; sudo ip addr add 192.168.50.1/24 dev enp0s8
sudo ip addr add 172.16.0.1/24 dev enp0s9
sudo ip link set enp0s8 up && sudo ip link set enp0s9 up
sudo ip route replace default via 192.168.100.1
echo 'net.ipv4.ip_forward = 1' | sudo tee /etc/sysctl.d/90-fw.conf && sudo sysctl --system
```

**`cli-lan`:**

```bash
sudo ip addr add 192.168.50.10/24 dev enp0s3 && sudo ip link set enp0s3 up
sudo ip route replace default via 192.168.50.1
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf       # DNS provisional (el cortafuegos filtrará la salida)
```

**`web-dmz`:**

```bash
sudo ip addr add 172.16.0.10/24 dev enp0s3 && sudo ip link set enp0s3 up
sudo ip route replace default via 172.16.0.1
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf
```

**Comprobación de la conectividad base** (sin filtrado todavía):

```bash
# En cli-lan
ping -c 2 192.168.50.1 && ping -c 2 172.16.0.10 && ping -c 2 192.168.100.10
# En web-dmz
ping -c 2 172.16.0.1 && ping -c 2 192.168.50.10          # ¡alcanza la LAN! (esto es lo que vamos a corregir)
```

> [!WARNING]
> Con el reenvío activo y sin reglas, **todas las zonas se ven entre sí**: ese es el punto de partida «inseguro». Anota las pruebas que funcionan: son tu **estado inicial**.

Haz una *snapshot* `ud7-inicio` de las cuatro VM.

<!-- hint:h1 -->
{{% details title="🔧 Si algo falla" open=false %}}
Los nombres de las interfaces pueden variar (`enp0s3`, `enp0s8`, `enp0s9`). Compruébalo con `ip -br link` y ajusta las variables `WAN`, `LAN` y `DMZ` del fichero de reglas a lo que veas. Las direcciones configuradas con `ip addr add` **no son persistentes**: si reinicias, hay que volver a aplicarlas.
{{% /details %}}

> [!NOTE]
> Las prácticas **6.9 a 6.12** (SSH, WireGuard, RADIUS e IPsec) reutilizan las máquinas y redes de laboratorio de la [UD5](/ud05-seguridad-redes/ud05-practicas/#preparación-del-laboratorio). Si no las tienes, prepáralas primero.

---

## Práctica 6.1 · Perímetro, zonas y matriz de flujos

{{< practica num="6.1" tipo="Guiada" duracion="1 h" nivel="1" ra="RA1:h;RA3:a,b" entorno="Debian 13 · VirtualBox 7" entrega="esquema de zonas y matriz de flujos" >}}

**Objetivo:** planificar antes de configurar (RA1 h, RA3 b, RA4 c).

1. Dibuja el diagrama del laboratorio indicando zonas, interfaces, redes y nivel de confianza.
2. Rellena la **matriz de flujos** (usa la de la teoría como modelo). Debe cubrir, al menos:

| # | Origen | Destino | Servicio | Acción | Justificación |
| --- | --- | --- | --- | --- | --- |
| 1 | `sad-cli` (WAN) | `web-dmz` | HTTP 80, HTTPS 443 (vía IP del `fw`) | Permitir (DNAT) | Publicación de la web |
| 2 | `sad-cli` (WAN) | `fw`, LAN | Cualquiera | Denegar | Nada interno es público |
| 3 | `cli-lan` | Internet | HTTP, HTTPS, DNS, NTP | Permitir | Navegación |
| 4 | `cli-lan` | `web-dmz` | SSH 22, HTTP 80, HTTPS 443 | Permitir | Administración y pruebas |
| 5 | `web-dmz` | LAN | Cualquiera | **Denegar y registrar** | Contención de compromisos |
| 6 | `web-dmz` | Internet | HTTP, HTTPS, DNS | Permitir | Actualizaciones |
| 7 | LAN | `fw` | SSH 22 | Permitir (solo admin) | Administración del cortafuegos |
| 8 | Cualquiera | Cualquiera | — | Denegar | Política por defecto |

3. Define las **pruebas de aceptación**: para cada fila, un comando que **debe funcionar** y otro que **debe fallar**. Será tu plan de pruebas.

<!-- hint:h2 -->
{{% details title="💡 Pista" open=false %}}
Antes de escribir una regla, completa la matriz con tres columnas: **origen → destino → servicio → acción**. Si algo no figura en la matriz, la política por defecto (`drop`) lo bloquea. Las reglas son la traducción literal de esa tabla, y la tabla es lo que enseñarás al cliente o al auditor.
{{% /details %}}

---

## Práctica 6.2 · Cortafuegos con nftables y política `drop`

{{< practica num="6.2" tipo="Guiada" duracion="2 h" nivel="3" ra="RA4:b,c,d" entorno="Debian 13 · VirtualBox 7" entrega="conjunto de reglas nftables y pruebas" >}}

**Objetivo:** implementar la matriz de flujos (RA4 d, f).

#### Preparación segura

```bash
# En fw
sudo cp /etc/nftables.conf /etc/nftables.conf.bak                  # copia del fichero original
sudo systemctl disable --now firewalld 2>/dev/null; sudo systemctl disable --now ufw 2>/dev/null
```

Crea `/etc/nftables.conf` con el **ruleset de tres zonas** del apartado 5.3 de la [teoría](/ud06-seguridad-perimetral/ud06-teoria/) (cópialo íntegro; ya incluye filtrado y NAT) y comprueba la sintaxis:

```bash
sudo nft -c -f /etc/nftables.conf && echo "SINTAXIS CORRECTA"
```

<!-- hint:h3 -->
> [!WARNING]
> No mezcles cortafuegos: si dejas `firewalld` o `ufw` activos junto con `nftables`, las reglas se pisan y el comportamiento es impredecible. En este laboratorio el único gestor del cortafuegos es el fichero `/etc/nftables.conf`.

#### Aplicación con red de seguridad

```bash
sudo systemd-run --on-active=180 --unit=deshacer-fw nft flush ruleset    # a los 3 min se borran las reglas
sudo nft -f /etc/nftables.conf                                           # aplica
sudo nft list ruleset | head -40                                         # revisa lo aplicado
```

Comprueba que **sigues conectado** a `fw` y que las pruebas del apartado 4.3 se comportan según lo esperado. Si todo va bien:

```bash
sudo systemctl stop deshacer-fw.timer              # cancela el deshacer
sudo systemctl enable --now nftables               # persiste al reiniciar
```

<!-- hint:h4 -->
> [!TIP]
> Si todo va bien, **cancela el deshacer** con `sudo systemctl stop deshacer-fw.timer`. Si olvidas hacerlo, a los 3 minutos se borrará el conjunto de reglas y el cortafuegos quedará abierto. Esa es precisamente la red de seguridad: es preferible un cortafuegos abierto durante un momento que una máquina inaccesible.

#### Pruebas de aceptación (positivas y negativas)

Rellena la tabla con el resultado real:

| # | Prueba | Desde | Comando | Esperado | Resultado |
| --- | --- | --- | --- | --- | --- |
| 1+ | Web publicada | `sad-cli` | `curl -s -m 3 http://192.168.100.100/` | `<h1>web-dmz</h1>` (tras la práctica 6.3) | |
| 2− | SSH al `fw` desde fuera | `sad-cli` | `ssh -o ConnectTimeout=3 usuario@192.168.100.100` | Timeout | |
| 3+ | Navegar | `cli-lan` | `curl -s -m 5 -I https://example.org` | `HTTP/2 200` (o similar) | |
| 4+ | SSH a la DMZ | `cli-lan` | `ssh usuario@172.16.0.10` | Funciona | |
| 5− | **DMZ → LAN** | `web-dmz` | `ping -c 2 -W 1 192.168.50.10` | Sin respuesta | |
| 5− | **DMZ → LAN** (TCP) | `web-dmz` | `nc -zv -w 2 192.168.50.10 22` | *Timeout* | |
| 6+ | Actualizar | `web-dmz` | `sudo apt update` | Funciona | |
| 7+ | SSH al `fw` desde LAN | `cli-lan` | `ssh usuario@192.168.50.1` | Funciona | |
| 8− | LAN → puerto no permitido | `cli-lan` | `nc -zv -w 2 192.168.100.10 8080` | *Timeout* | |

Guarda `sudo nft list ruleset > ~/ud7-evidencias/02-ruleset.txt` y las salidas de las pruebas.

<!-- hint:h5 -->
{{% details title="💡 Pista" open=false %}}
Prueba siempre **ambos sentidos**: lo permitido debe funcionar (prueba positiva) y lo prohibido debe fallar (prueba negativa). Una regla de la que solo compruebas que «deja pasar» no está validada: puede que sea un `accept` demasiado amplio. Anota cada prueba y su resultado en la tabla de aceptación.
{{% /details %}}

#### Contadores: ¿se aplican realmente las reglas?

```bash
sudo nft list chain inet filtro reenvio | grep -E 'counter|packets'     # paquetes por regla
sudo nft -a list chain inet filtro reenvio                               # con handle (para borrar/insertar)
```

Repite una prueba y observa qué contador aumenta. Explica qué regla ha atendido cada prueba de la tabla anterior.

> [!TIP]
> Si la prueba 1 aún no funciona, es normal: falta el servidor web en la DMZ o el DNAT (práctica 6.3) o el servicio no escucha. Si pierdes el acceso al `fw`: consola de VirtualBox → `sudo nft flush ruleset` → revisa el fichero.

---

## Práctica 6.3 · NAT y publicación de un servicio en la DMZ

{{< practica num="6.3" tipo="Guiada" duracion="1 h" nivel="2" ra="RA4:c,d" entorno="Debian 13 · VirtualBox 7" entrega="servicio publicado y comprobación desde fuera" >}}

**Objetivo:** salir con masquerade, publicar con DNAT y verificar el camino completo (RA4 d, RA3 a).

#### Comprobar los cinco requisitos de la publicación

| Requisito | Dónde se comprueba |
| --- | --- |
| DNAT en `prerouting` | `sudo nft list table ip nat` |
| Regla `forward` hacia la DMZ | `sudo nft list chain inet filtro reenvio` |
| `ip_forward = 1` | `sysctl net.ipv4.ip_forward` |
| *Gateway* de `web-dmz` = 172.16.0.1 | `ip route` en `web-dmz` |
| Servicio escuchando | `ss -tlnp` en `web-dmz` |

#### Prueba y observación

```bash
# Desde sad-cli (Internet simulada)
curl -s http://192.168.100.100/                       # <h1>web-dmz</h1>
```

En paralelo, en `fw`, observa la **traducción** en los dos lados:

```bash
sudo tcpdump -ni enp0s3 'tcp port 80 and host 192.168.100.10' -c 4     # lado WAN: destino 192.168.100.100
sudo tcpdump -ni enp0s9 'tcp port 80 and host 192.168.100.10' -c 4     # lado DMZ: destino 172.16.0.10 (traducido)
sudo conntrack -L | grep 172.16.0.10                                    # la traducción recordada por conntrack
```

Anota qué direcciones ve cada captura y explica cómo regresa la respuesta con la IP original.

<!-- hint:h6 -->
{{% details title="🎯 Resultado esperado" open=false %}}
Captura en cada lado del cortafuegos: en `enp0s3` (WAN) el destino es `192.168.100.100`; en `enp0s9` (DMZ) el mismo tráfico llega ya con destino `172.16.0.10`. Eso es **DNAT** en acción: la dirección de destino se reescribe antes del reenvío.
{{% /details %}}

#### Comprobar la contención de la DMZ

Supón que el servidor de la DMZ ha sido comprometido. Desde `web-dmz` intenta alcanzar la LAN (como lo haría un atacante, pero con simples herramientas de prueba de conectividad):

```bash
nc -zv -w 2 192.168.50.10 22        # debe fallar
ping -c 2 -W 1 192.168.50.10        # debe fallar
```

En `fw`, localiza la alerta:

```bash
sudo journalctl -k --since "5 min ago" | grep 'DMZ-A-LAN' | tee ~/ud7-evidencias/03-dmz-lan.txt
sudo nft list chain inet filtro reenvio | grep -B1 'DMZ-A-LAN'          # el contador de la regla
```

#### Prueba de fallo del servicio

1. En `web-dmz` para Apache (`sudo systemctl stop apache2`) y repite `curl` desde `sad-cli`: observa si el error es *timeout* o *connection refused* y explica **por qué** (el SYN llega y la DMZ responde con RST).
2. Arranca el servicio y verifica la recuperación.
3. **Pregunta:** ¿qué ocurriría si en `web-dmz` olvidases el *gateway*? Compruébalo temporalmente (`sudo ip route del default`) con una captura en el `fw`: ¿se ve el SYN-ACK de vuelta? Restáuralo después.

<!-- hint:h7 -->
{{% details title="💡 Pista" open=false %}}
Para el servidor de la DMZ y observa qué ocurre desde Internet: la regla de NAT sigue existiendo, pero la conexión se rechaza o expira. Esto sirve para diferenciar **un fallo del servicio** de **un fallo del cortafuegos**: mira los contadores de las reglas y los registros.
{{% /details %}}

---

## Práctica 6.4 · Endurecimiento TCP/IP, registro y diagnóstico

{{< practica num="6.4" tipo="Autónoma" duracion="0 h · trabajo autónomo" nivel="2" ra="RA4:e,g" entorno="Debian 13 · VirtualBox 7" entrega="registro y diagnóstico" >}}

#### Parámetros del núcleo del cortafuegos

Crea `/etc/sysctl.d/90-perimetro.conf` según el apartado 7 de la teoría, aplica con `sudo sysctl --system` y verifica:

```bash
sysctl net.ipv4.ip_forward net.ipv4.conf.all.rp_filter net.ipv4.conf.all.accept_redirects net.ipv4.tcp_syncookies
```

> [!NOTE]
> Si `sysctl --system` avisa de que `net.netfilter.nf_conntrack_max` no existe, ejecuta `sudo modprobe nf_conntrack` y vuelve a aplicar. Comprueba la ocupación con `sudo conntrack -C`.

#### Análisis de registros

1. Genera **tres tipos de eventos de bloqueo** controlados:
   - Desde `sad-cli` a un puerto no publicado del `fw`: `nc -zv -w 2 192.168.100.100 8080`.
   - Desde `web-dmz` a la LAN (práctica 3.3).
   - Desde `cli-lan` a un servicio no permitido de la DMZ: `nc -zv -w 2 172.16.0.10 3306`.
2. Extrae los eventos y rellena:

```bash
sudo journalctl -k --since "10 min ago" | grep -E 'FW-IN-DROP|FW-FWD-DROP|DMZ-A-LAN' | tee ~/ud7-evidencias/04-eventos.txt
```

| Fecha y hora | Interfaz entrada → salida | Origen | Destino | Protocolo y puerto | Regla (prefijo) | Acción |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

3. Comprueba la **hora**: ¿están sincronizadas las cuatro VM? (`timedatectl`; instala `chrony` si no). Explica por qué es imprescindible para correlacionar eventos.
4. Indica **qué eventos enviarías a un servidor de registros o SIEM** (UD4: Wazuh): cambios de reglas, autenticaciones administrativas, bloqueos repetidos, DMZ → LAN, alertas de IDS.

#### Diagnóstico guiado: tres averías

Pide a un compañero (o hazlo tú tras una *snapshot*) que provoque **una de estas averías** en `fw` sin decirte cuál, y diagnostica con el método del apartado 8.3 de la teoría:

| Avería | Cómo se provoca (en `fw`) | Síntoma |
| --- | --- | --- |
| A | `sudo sysctl -w net.ipv4.ip_forward=0` | Nada pasa entre zonas |
| B | `sudo nft delete rule inet filtro reenvio handle <N>` (la regla de navegación) | `cli-lan` no navega, pero sí llega a la DMZ |
| C | En `web-dmz`: `sudo ip route del default` | La web publicada no responde desde fuera |

Para cada avería documenta: **síntoma observado → hipótesis → prueba que la confirma (comando y salida) → solución → comprobación**. Restaura el estado inicial después de cada una.

<!-- hint:h8 -->
{{% details title="💡 Pista" open=false %}}
Sigue siempre el mismo método, **capa por capa**: (1) enlace (`ip -br link`), (2) direccionamiento y rutas (`ip -br a`, `ip route`), (3) reenvío (`sysctl net.ipv4.ip_forward`), (4) reglas (`nft list ruleset`, contadores, `nft monitor trace`), (5) servicio de destino (`ss -tlnp`, `nc -zv`), (6) registros. Es más rápido que probar cosas al azar.
{{% /details %}}

---

## Práctica 6.5 · Proxy directo con Squid

{{< practica num="6.5" tipo="Guiada" duracion="2 h" nivel="2" ra="RA5:b,c,d,e,g" entorno="Debian 13 · VirtualBox 7" entrega="Squid con autenticación y restricciones" >}}

**Objetivo:** controlar y registrar la navegación de la LAN (RA5 a–g). Squid se instala en `fw` (ya en la práctica 2.2).

#### Configuración con ACL, horario y bloqueos

```bash
sudo systemctl stop squid
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.bak
sudoedit /etc/squid/squid.conf          # sustituye el contenido por el del apartado 11.2 de la teoría
printf '.malwaredomain.test\n.casino-lab.test\n' | sudo tee /etc/squid/bloqueados.txt
sudo squid -k parse                     # debe terminar sin ERROR (puede haber advertencias informativas)
sudo systemctl enable --now squid
sudo ss -tlnp | grep 3128
```

Permite el acceso al puerto 3128 desde la LAN en el cortafuegos (regla en la cadena `entrada`):

```bash
sudo nft add rule inet filtro entrada iifname "enp0s8" tcp dport 3128 accept
```

(Para hacerlo permanente, añade la regla a `/etc/nftables.conf`.)

<!-- hint:h9 -->
> [!TIP]
> Valida la sintaxis con `sudo squid -k parse` antes de reiniciar. **El orden de `http_access` importa:** Squid evalúa de arriba abajo y se detiene en la primera coincidencia; las reglas de bloqueo van antes que las de permiso, y la última siempre es `http_access deny all`.

#### Pruebas desde `cli-lan`

```bash
export http_proxy=http://192.168.50.1:3128 https_proxy=http://192.168.50.1:3128
curl -sI http://example.org/ | head -3                      # permitido
curl -sI http://www.casino-lab.test/ | head -3              # bloqueado: 403 de Squid
curl -sI https://example.org/ | head -3                     # HTTPS por CONNECT
unset http_proxy https_proxy
```

Revisa en `fw` el registro y rellena:

```bash
sudo tail -n 10 /var/log/squid/access.log | tee ~/ud7-evidencias/05-access.log
```

| Cliente | Método | URL | Resultado de caché / código | Interpretación |
| --- | --- | --- | --- | --- |
| | | | | |

**Prueba de caché:** descarga dos veces un fichero estático (`curl -x http://192.168.50.1:3128 -o /dev/null -s -w '%{time_total}\n' http://example.org/`). En el log, el segundo acceso debería aparecer como `TCP_MEM_HIT`/`TCP_HIT` si el contenido es *cacheable*; si no, razona por qué (cabeceras `Cache-Control`).

<!-- hint:h10 -->
{{% details title="🔧 Si algo falla" open=false %}}
- **`403 Forbidden` / `TCP_DENIED`:** el cliente no está en una ACL permitida o el sitio está en la lista de bloqueados. Mira `sudo tail -f /var/log/squid/access.log` mientras pruebas.
- **No hay respuesta:** comprueba que Squid escucha (`ss -tlnp | grep 3128`) y que el cortafuegos del `fw` permite el puerto 3128 desde la LAN.
- **El navegador salta el proxy:** `curl` usa `http_proxy` si lo exportas; los navegadores tienen su propia configuración.
{{% /details %}}

#### Autenticación

1. Crea usuarios con `htpasswd` y configura el *helper* según el apartado 11.4 de la teoría (la ruta del helper cambia entre Debian y AlmaLinux).
2. Prueba **sin** credenciales (esperado: `407`), con credenciales **erróneas** (407) y **correctas** (200):

```bash
curl -sI -x http://192.168.50.1:3128 http://example.org/ | head -1
curl -sI -x http://ana:Mal@192.168.50.1:3128 http://example.org/ | head -1
curl -sI -x http://ana:ClaveAna1@192.168.50.1:3128 http://example.org/ | head -1
sudo tail -n 3 /var/log/squid/access.log            # ahora el log muestra el usuario
```

3. **Diagnóstico:** si recibes `407` con credenciales correctas, prueba el *helper* a mano: `echo "ana ClaveAna1" | /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd` (debe responder `OK`).

<!-- hint:h11 -->
> [!WARNING]
> La autenticación **básica** transmite usuario y contraseña en Base64 (codificado, no cifrado). Cualquiera que capture el tráfico entre cliente y proxy puede leerla. En laboratorio es aceptable; en producción, usa Kerberos/NTLM/LDAP o limita el uso de la autenticación al segmento de confianza.

#### Modo transparente

1. Añade a `squid.conf`: `http_port 3129 intercept`; `sudo squid -k parse && sudo squid -k reconfigure`.
2. En `fw`, añade la redirección a la tabla NAT (**antes** de la regla DNAT de Internet→DMZ no es necesario: son interfaces distintas):

```bash
sudo nft add rule ip nat prerouting iifname "enp0s8" ip saddr 192.168.50.0/24 tcp dport 80 redirect to :3129
sudo nft add rule inet filtro entrada iifname "enp0s8" tcp dport 3129 accept
```

3. Desde `cli-lan` **sin** configurar proxy: `curl -sI http://example.org/ | head -1` y comprueba que la petición aparece en `access.log`. Prueba también `curl https://example.org/`: ¿pasa por el proxy? Explica por qué **no**.
4. Para **forzar** el uso del proxy, bloquea en el cortafuegos la salida directa de la LAN al puerto 80 (salvo la redirigida) y valora qué hacer con 443.

<!-- hint:h12 -->
> [!NOTE]
> El modo transparente funciona bien con **HTTP**. El HTTPS no se puede interceptar sin romper el cifrado extremo a extremo (haría falta que los clientes confíen en una CA propia, lo que tiene implicaciones legales y de privacidad). Para HTTPS se configura el proxy en los clientes o se filtra por nombre (SNI).

#### Monitorización gráfica

```bash
sudo mkdir -p /var/lib/sarg-reports
sudo sarg -l /var/log/squid/access.log -o /var/lib/sarg-reports
sudo systemctl disable --now apache2 2>/dev/null          # si sarg ha instalado Apache, libera el puerto 80 para Nginx
cd /var/lib/sarg-reports && sudo python3 -m http.server 8088 --bind 192.168.50.1 &     # servidor temporal solo para esta prueba
sudo nft add rule inet filtro entrada iifname "enp0s8" tcp dport 8088 accept
```

Abre `http://192.168.50.1:8088/` desde `cli-lan` y adjunta una captura con los sitios más visitados y bloqueados. Al terminar, detén el servidor temporal (`kill %1`) y elimina la regla (`sudo nft -a list chain inet filtro entrada` y `sudo nft delete rule inet filtro entrada handle N`).

**Reflexiona:** ¿qué datos personales trata este informe y cómo cumplirías el RGPD (información, minimización, acceso restringido, retención)?

---

## Práctica 6.6 · Proxy inverso con Nginx, TLS y WAF

{{< practica num="6.6" tipo="Guiada" duracion="1 h" nivel="3" ra="RA5:a,f" entorno="Debian 13 · VirtualBox 7" entrega="proxy inverso con TLS" >}}

**Objetivo:** publicar aplicaciones de forma segura con un proxy inverso (RA5 h).

#### Dos aplicaciones internas y el proxy

En `web-dmz` (o en `fw` para simplificar), levanta dos servicios que escuchan **solo en local**:

```bash
mkdir -p ~/app-a ~/app-b && echo "App A" > ~/app-a/index.html && echo "App B" > ~/app-b/index.html
(cd ~/app-a && python3 -m http.server 8081 --bind 127.0.0.1 >/dev/null 2>&1 &)
(cd ~/app-b && python3 -m http.server 8082 --bind 127.0.0.1 >/dev/null 2>&1 &)
```

Configura el proxy inverso como en el apartado 12.2 de la teoría y valida:

```bash
sudo nginx -t && sudo systemctl enable --now nginx && sudo systemctl reload nginx
curl -s http://localhost/app-a/ ; curl -s http://localhost/app-b/
```

**Comprobación de no exposición:** desde otra VM `curl -m 3 http://IP:8081/` debe fallar y `http://IP/app-a/` funcionar. Documenta con `ss -tlnp` qué escucha en cada interfaz.

#### TLS y cabeceras de seguridad

Usa un certificado de la **PKI de la UD3** (o genera uno de laboratorio) y configura el servidor HTTPS del apartado 12.3 de la teoría. Comprueba:

```bash
sudo nginx -t && sudo systemctl reload nginx
curl -vk https://localhost/ 2>&1 | grep -E 'SSL connection|subject|issuer|HTTP/'
curl -skI https://localhost/ | grep -iE 'strict-transport|x-content|x-frame|server'
openssl s_client -connect localhost:443 -tls1_1 </dev/null 2>&1 | grep -iE 'alert|handshake failure|Protocol'   # TLS 1.1 debe rechazarse
sudo nmap --script ssl-enum-ciphers -p 443 localhost | head -30                                                # resumen de cifrados
```

Registra la versión de TLS negociada y los cifrados aceptados, y razona si algún protocolo antiguo sigue habilitado.

#### Limitación de peticiones

Aplica `limit_req` según el apartado 12.4. Genera carga **contra tu propio servidor**:

```bash
sudo apt install -y apache2-utils
ab -n 300 -c 30 http://localhost/app-a/ | grep -E 'Complete requests|Failed requests|Non-2xx|Requests per second'
sudo grep -c 'limiting requests' /var/log/nginx/error.log
```

Anota cuántas peticiones fueron rechazadas (`503`) y ajusta `rate` y `burst` hasta que una navegación normal no se vea afectada.

<!-- hint:h13 -->
{{% details title="🎯 Resultado esperado" open=false %}}
Con `limit_req` activo, parte de las peticiones de `ab` devolverán **503** (`Non-2xx responses`) en cuanto se supera el ritmo permitido. Es la señal de que la limitación funciona. Ajusta `rate` y `burst` para encontrar un equilibrio entre proteger el servicio y no molestar a usuarios legítimos.
{{% /details %}}

#### WAF en modo detección

1. Comprueba si tu distribución ofrece el módulo (`apt search modsecurity`). Instálalo y actívalo con `SecRuleEngine DetectionOnly` y OWASP CRS, según la documentación del paquete.
2. Lanza las **pruebas inofensivas** del apartado 12.5 contra tu propio Nginx y revisa el registro de auditoría:

```bash
curl -s -o /dev/null -w '%{http_code}\n' "http://localhost/?q=<script>alert(1)</script>"
curl -s -o /dev/null -w '%{http_code}\n' "http://localhost/?file=../../etc/passwd"
sudo tail -n 20 /var/log/modsec_audit.log
```

3. Cambia a `SecRuleEngine On`, repite y comprueba que ahora devuelven `403`. Explica **por qué** se empieza en detección y qué harías con un falso positivo.

> [!NOTE]
> Si el paquete no está disponible en tu versión, realiza esta parte de forma documental: describe dónde situarías el WAF, qué peticiones inspeccionaría y el plan de implantación gradual (detección → ajuste → bloqueo).

<!-- hint:h14 -->
{{% details title="💡 Pista" open=false %}}
En `DetectionOnly` el WAF **registra** pero **no bloquea** (por eso las peticiones sospechosas siguen devolviendo `200`). Se empieza así a propósito, para descubrir falsos positivos sin romper la aplicación. Solo cuando las reglas están ajustadas se pasa a `SecRuleEngine On`, donde la petición devuelve `403`. Los eventos se leen en `/var/log/modsec_audit.log` (la ruta puede variar según el paquete).
{{% /details %}}

---

## Práctica 6.7 · Cortafuegos dedicado: OPNsense (opcional)

{{< practica num="6.7" tipo="Autónoma" duracion="0 h · trabajo autónomo" nivel="2" ra="RA4:f" entorno="Debian 13 · VirtualBox 7" entrega="informe comparativo de cortafuegos" >}}

Repite la política mínima de la práctica 6.2 con **OPNsense** en lugar de nftables:

1. Crea la VM con los tres adaptadores (WAN `SAD-NAT`, LAN `sad-lan7`, OPT1 `sad-dmz`), instala desde la ISO (verifica su SHA-256) y cambia las credenciales por defecto.
2. Asigna interfaces e IP (LAN `192.168.50.1/24`, OPT1 `172.16.0.1/24`). Accede por `https://192.168.50.1` desde `cli-lan`.
3. Crea **alias** (`WEB_DMZ`, `PUERTOS_WEB`) y las reglas de la matriz de flujos: *LAN* (navegar, SSH a la DMZ), *OPT1/DMZ* (solo salida web y DNS; **bloquear DMZ → LAN con registro**), *WAN* (solo la publicación).
4. Configura la **publicación** en *Firewall → NAT → Port Forward* (WAN:80 → 172.16.0.10:80) y verifica con `sad-cli`.
5. Revisa *Firewall → Log Files → Live View* y localiza los eventos de las pruebas negativas.
6. Haz una **copia de configuración** (*System → Configuration → Backups*), descárgala y cífrala (`gpg --symmetric`).

**Entrega:** capturas de las reglas, del Live View con bloqueos y comparación breve **nftables frente a OPNsense** (administración, trazabilidad, rendimiento, curva de aprendizaje).

---

## Práctica 6.8 · Alta disponibilidad y recuperación del perímetro

{{< practica num="6.8" tipo="Guiada" duracion="1 h" nivel="3" ra="RA4:g" entorno="Debian 13 · VirtualBox 7" entrega="prueba de fallo del perímetro" >}}

#### Diseño

Redacta la propuesta de **HA del cortafuegos**: dos cortafuegos, IP virtual en cada zona (VRRP o CARP), sincronización de reglas y de estado de conexiones, red de gestión, alimentación y enlaces redundantes, DNS y monitorización. Justifica **activo-pasivo** frente a **activo-activo**.

#### Implantación (si dispones de recursos)

1. Clona `fw` como `fw2`, con IP propias en cada zona: WAN `.101`, LAN `.2`, DMZ `.2`.
2. Instala Keepalived (ver UD5) en ambos, con una instancia VRRP por zona (VIP: WAN `192.168.100.100`, LAN `192.168.50.254`, DMZ `172.16.0.254`) agrupadas en un `vrrp_sync_group`. Los clientes pasan a usar la VIP como puerta de enlace (`cli-lan`: `192.168.50.254`).
3. Cambia las reglas de `fw`/`fw2` a las nuevas direcciones y comprueba con las pruebas de aceptación de la práctica 2.
4. **Prueba de fallo planificada:** con un `ping` continuo y una sesión SSH desde `cli-lan` hacia Internet, detén Keepalived en el principal:

```bash
sudo systemctl stop keepalived              # en fw
```

Registra: tiempo de interrupción, si la sesión SSH sobrevive (necesita `conntrackd`; si no lo has configurado, se cortará), registros generados en ambos nodos y comportamiento al **recuperar** el principal.

> [!NOTE]
> Si no dispones de recursos para dos cortafuegos, presenta el diseño completo, la secuencia de conmutación y el plan de pruebas **sin desplegar**, con los ficheros de configuración que usarías.

#### Copia y restauración

```bash
sudo nft list ruleset | gpg --symmetric --cipher-algo AES256 -o ~/ud7-evidencias/fw-$(date +%F).nft.gpg
sudo cp -a /etc/nftables.conf /etc/sysctl.d/90-fw.conf /etc/squid/squid.conf ~/ud7-evidencias/ 2>/dev/null
```

Prueba la **restauración** en una VM de sustitución: instala nftables, descifra (`gpg -d`), aplica con `nft -f` y repite las pruebas de aceptación. Mide el **tiempo de restauración** (RTO) y anota qué faltaba (rutas, `sysctl`, interfaces, claves).

<!-- hint:h15 -->
> [!WARNING]
> La configuración del cortafuegos contiene información sensible (topología, direcciones, a veces secretos). **Cífrala** (por eso el ejemplo usa `gpg --symmetric`) y guarda la copia fuera del propio equipo. Prueba la restauración: una configuración que nunca se ha restaurado no está respaldada de verdad.

---

## Práctica 6.9 · Protocolos seguros y SSH avanzado

{{< practica num="6.9" tipo="Guiada" duracion="1 h" nivel="2" ra="RA3:c,f" entorno="Debian 13 · VirtualBox 7" entrega="configuración SSH y pruebas" >}}

#### Lo que ve la red: protocolo en claro frente a cifrado

Sigue el apartado 6.1 de la [teoría](/ud06-seguridad-perimetral/ud06-teoria/): instala la zona con autenticación básica en `sad-web`, captura tu propia petición con `tcpdump` y decodifica la cabecera `Authorization`.

Entrega: captura de pantalla de la cabecera, el resultado de `base64 -d` y una explicación de por qué es inseguro. Después repite la petición con **HTTPS** (certificado de la UD3, práctica 6) y comprueba que ya no se ve el contenido:

```bash
sudo tcpdump -n -A -i enp0s3 'tcp port 443 and host 192.168.100.10' -c 20 | tee ~/ud6-evidencias/03-https.txt
```

#### Túnel SSH hacia la intranet

`gw-vpn` es el único acceso desde fuera. Desde `sad-cli` (permitido por SSH a `gw-vpn`, con clave: UD4):

```bash
ssh -N -L 8080:10.10.10.10:80 ana@192.168.100.90 &       # túnel local: localhost:8080 → srv-lan:80
curl -s http://localhost:8080/                           # "srv-lan interno"
kill %1                                                  # cierra el túnel
```

Comprueba que **sin** el túnel `sad-cli` no alcanza `10.10.10.10` (no hay ruta): `curl -m 3 http://10.10.10.10/`.

<!-- hint:h5 -->
{{% details title="💡 Pista" open=false %}}
`-N` indica que no se abra una shell (solo el túnel) y `-L 8080:10.10.10.10:80` reenvía el puerto local 8080 al puerto 80 del destino **visto desde el servidor SSH**. Para cerrar el túnel: `kill %1` (o `fg` y Ctrl+C). Los túneles son útiles, pero también una vía para saltarse el cortafuegos: en producción conviene controlarlos (`AllowTcpForwarding`).
{{% /details %}}

#### Bastión con `ProxyJump`

En `sad-cli`, `~/.ssh/config`:

```text
Host gw
    HostName 192.168.100.90
    User ana
Host srv-lan
    HostName 10.10.10.10
    User ana
    ProxyJump gw
```

```bash
ssh srv-lan 'hostname; echo conectado vía bastión'
```

Revisa en `gw-vpn` el registro de la conexión (`sudo journalctl -u ssh --since "5 min ago"`): el bastión **centraliza la auditoría**. Mejora de seguridad: en `srv-lan` permite SSH **solo** desde `10.10.10.1` (cortafuegos de la UD4).

#### Certificados SSH

1. En `gw-vpn` crea una CA SSH (en un directorio protegido):

```bash
mkdir -m 700 ~/ca-ssh && cd ~/ca-ssh
ssh-keygen -t ed25519 -f ssh_ca -C "CA SSH laboratorio"
```

2. Firma la clave pública de Ana (cópiala antes desde `sad-cli`: `scp ~/.ssh/id_ed25519.pub gw-vpn:~/ca-ssh/ana.pub`):

```bash
ssh-keygen -s ssh_ca -I ana-2026 -n ana -V +4w ana.pub        # certificado válido 4 semanas, solo para la cuenta "ana"
ssh-keygen -L -f ana-cert.pub                                  # inspecciona: Key ID, Valid, Principals
```

3. Devuelve `ana-cert.pub` a `sad-cli` como `~/.ssh/id_ed25519-cert.pub` (misma carpeta que la clave privada).
4. En `srv-lan`, confía en la CA y **quita** la clave pública de Ana de `authorized_keys`:

```bash
sudo cp ssh_ca.pub /etc/ssh/ssh_ca.pub                          # (copia la pública de la CA a srv-lan)
echo 'TrustedUserCAKeys /etc/ssh/ssh_ca.pub' | sudo tee /etc/ssh/sshd_config.d/20-ca.conf
sudo sshd -t && sudo systemctl reload ssh
```

5. Comprueba: `ssh -v ana@10.10.10.10 2>&1 | grep -i certificate` debe mostrar que se ofrece el certificado y entra **sin** `authorized_keys`. Prueba la caducidad: firma un certificado con `-V +1m`, espera un minuto y comprueba que se rechaza.

**Preguntas:** ¿qué ventajas ofrece un certificado SSH frente a distribuir claves en `authorized_keys`? ¿Cómo se **revoca** un certificado antes de que caduque? (pista: `RevokedKeys`).

<!-- hint:h6 -->
{{% details title="🔧 Si algo falla" open=false %}}
- **`Certificate invalid: name is not a listed principal`:** el usuario con el que entras no está en los *principals* del certificado (`ssh-keygen -L -f id_ed25519-cert.pub`).
- **El servidor sigue pidiendo clave:** ¿`TrustedUserCAKeys` apunta a la pública de la CA? ¿Se recargó `sshd`? Mira `ssh -vvv` en el cliente.
- **Certificado caducado:** los certificados SSH tienen vigencia; renuévalos antes de que expiren.
{{% /details %}}

---

## Práctica 6.10 · VPN de acceso remoto con WireGuard

{{< practica num="6.10" tipo="Guiada" duracion="2 h" nivel="3" ra="RA3:d,e" entorno="Debian 13 · VirtualBox 7" entrega="túnel WireGuard operativo" >}}

**Objetivo:** que `sad-cli` (fuera de la sede) acceda por un túnel cifrado al servidor interno `srv-lan` y **solo** a lo permitido (RA3 d, e).

#### Instalación y claves

En `gw-vpn` y `sad-cli`:

```bash
sudo apt install -y wireguard wireguard-tools                  # AlmaLinux: sudo dnf install -y wireguard-tools
umask 077
wg genkey | sudo tee /etc/wireguard/privada.key | wg pubkey | sudo tee /etc/wireguard/publica.key
sudo cat /etc/wireguard/publica.key                            # anota la pública de cada máquina
```

#### Configuración

**`gw-vpn`**, `/etc/wireguard/wg0.conf`:

```ini
[Interface]
Address    = 10.99.0.1/24
ListenPort = 51820
PrivateKey = <PRIVADA_DE_GW-VPN>

[Peer]
PublicKey  = <PUBLICA_DE_SAD-CLI>
AllowedIPs = 10.99.0.2/32
```

**`sad-cli`**, `/etc/wireguard/wg0.conf`:

```ini
[Interface]
Address    = 10.99.0.2/24
PrivateKey = <PRIVADA_DE_SAD-CLI>

[Peer]
PublicKey  = <PUBLICA_DE_GW-VPN>
Endpoint   = 192.168.100.90:51820
AllowedIPs = 10.99.0.0/24, 10.10.10.0/24
PersistentKeepalive = 25
```

Cortafuegos de `gw-vpn` (`/etc/nftables.d/vpn.nft`): VPN solo a la web y SSH de la LAN:

```text
table inet vpn {
  chain input {
    type filter hook input priority 0; policy accept;
    udp dport 51820 accept
  }
  chain forward {
    type filter hook forward priority 0; policy drop;
    ct state established,related accept
    iifname "wg0" ip daddr 10.10.10.0/24 tcp dport { 22, 80 } accept
    oifname "wg0" ip saddr 10.10.10.0/24 accept
  }
}
```

> [!WARNING]
> Si todavía tienes cargadas las reglas de la práctica 2 (`table inet vlans`) en `gw-vpn`, su cadena `forward` con política `drop` puede bloquear el tráfico de la VPN. Elimínalas con `sudo nft delete table inet vlans` o ejecuta esta práctica sobre una *snapshot* limpia.

```bash
sudo chmod 600 /etc/wireguard/wg0.conf                         # en ambas máquinas
sudo nft -c -f /etc/nftables.d/vpn.nft && sudo nft -f /etc/nftables.d/vpn.nft
sudo systemctl enable --now wg-quick@wg0                       # en ambas máquinas
```

`srv-lan` debe devolver el tráfico a `10.99.0.2` por `gw-vpn`: como su puerta de enlace ya es `10.10.10.1`, funciona sin más.

<!-- hint:h7 -->
> [!WARNING]
> Las claves **privadas** de WireGuard se crean con `umask 077` y el fichero `wg0.conf` con permisos `600`. No las pegues en chats ni las subas a Git. Solo se comparten las claves **públicas**. Si una clave privada se expone, hay que generar una nueva y sustituir la pública en el otro extremo.

#### Comprobaciones

```bash
sudo wg show | tee ~/ud6-evidencias/04-wg-show.txt             # "latest handshake" reciente y bytes en rx/tx
ping -c 3 10.99.0.1                                            # pasarela por el túnel
curl -s http://10.10.10.10/                                    # "srv-lan interno" (permitido)
ssh ana@10.10.10.10 hostname                                   # SSH (permitido)
curl -m 3 http://10.10.10.10:8080/                             # otro puerto: debe fallar (regla forward)
```

**Prueba de cifrado:** captura en la WAN de `gw-vpn` mientras haces `curl` por el túnel:

```bash
sudo tcpdump -ni enp0s3 udp port 51820 -c 6                    # solo se ve UDP 51820 ilegible
sudo tcpdump -ni wg0 -A -c 10 'tcp port 80'                    # dentro de la interfaz del túnel sí se ve la petición HTTP
```

**Prueba de fallo (disponibilidad y revocación):**

1. En `gw-vpn`, elimina el bloque `[Peer]` de `sad-cli` y recarga (`sudo wg syncconf wg0 <(sudo wg-quick strip wg0)`). Comprueba que `sad-cli` **pierde** el acceso: la **revocación** funciona.
2. Restaura el `[Peer]`. Detén y arranca `wg-quick@wg0` en `gw-vpn` y mide cuánto tarda el túnel en volver a funcionar (gracias a `PersistentKeepalive`).

**Preguntas:** ¿qué hace `AllowedIPs` en cada extremo? ¿Cómo cambiarías la configuración para enviar **todo** el tráfico del cliente por la VPN? ¿Qué riesgo corre la clave privada de `sad-cli` si le roban el portátil y cómo lo mitigarías?

<!-- hint:h8 -->
{{% details title="🔧 Si algo falla" open=false %}}
Si `wg show` no muestra `latest handshake`: (1) el puerto **UDP 51820** debe estar abierto en el servidor, (2) el `Endpoint` del cliente debe ser correcto, (3) las claves públicas deben estar **cruzadas** (la pública del cliente en el servidor y viceversa), (4) `AllowedIPs` debe incluir la IP del túnel del otro lado, (5) ambos relojes deben estar razonablemente sincronizados.

**Prueba de revocación:** `sudo wg set wg0 peer <clave_pública_cliente> remove` y comprueba que el cliente ya no puede comunicarse.
{{% /details %}}

---

## Práctica 6.11 · Autenticación centralizada con FreeRADIUS

{{< practica num="6.11" tipo="Guiada" duracion="1 h" nivel="3" ra="RA3:f,g" entorno="Debian 13 · VirtualBox 7" entrega="autenticación RADIUS comprobada" >}}

**Objetivo:** montar un servidor RADIUS y comprobar autenticaciones correctas e incorrectas (RA3 f, g).

En `gw-vpn`:

```bash
sudo apt install -y freeradius freeradius-utils                # AlmaLinux: sudo dnf install -y freeradius freeradius-utils
sudo systemctl stop freeradius
sudo cp /etc/freeradius/3.0/clients.conf /etc/freeradius/3.0/clients.conf.bak
sudo cp /etc/freeradius/3.0/mods-config/files/authorize /etc/freeradius/3.0/mods-config/files/authorize.bak
```

1. **Declara un cliente** (*NAS*) en `/etc/freeradius/3.0/clients.conf`:

```text
client lab-nas {
    ipaddr = 192.168.100.30
    secret = SecretoRadiusLab-CambiaMe-2026
}
```

2. **Añade usuarios** al principio de `/etc/freeradius/3.0/mods-config/files/authorize`:

```text
ana    Cleartext-Password := "ClavePruebaAna1"
       Reply-Message := "Hola Ana, acceso concedido"
luis   Cleartext-Password := "ClavePruebaLuis1"
       Reply-Message := "Hola Luis"
```

3. **Arranca en modo depuración** (verás cada decisión):

```bash
sudo freeradius -X
```

4. En `sad-web` (el «NAS» declarado), prueba con `radtest` (paquete `freeradius-utils`):

```bash
radtest ana ClavePruebaAna1 192.168.100.90 0 SecretoRadiusLab-CambiaMe-2026       # Access-Accept
radtest ana ClaveIncorrecta 192.168.100.90 0 SecretoRadiusLab-CambiaMe-2026       # Access-Reject
radtest ana ClavePruebaAna1 192.168.100.90 0 SecretoEquivocado                    # sin respuesta (secreto distinto)
```

Anota para cada caso la respuesta y qué ves en la salida de depuración del servidor.

5. **Pregunta de seguridad.** Sal de la depuración (`Ctrl+C`), activa el servicio (`sudo systemctl enable --now freeradius`) y comprueba con `sudo ss -ulnp | grep 1812` en qué interfaz escucha. Restringe el acceso a `1812/udp` y `1813/udp` desde la red de gestión con el cortafuegos.

**Ampliación (opcional):** configura el módulo **`pam_radius_auth`** en `sad-web` para que el inicio de sesión de un usuario de prueba se valide contra RADIUS (copia antes los ficheros de `/etc/pam.d/`, mantén una sesión de `root` abierta y revierte al terminar), o conecta un punto de acceso virtual con `hostapd` (WPA2/WPA3-Enterprise) al servidor.

<!-- hint:h9 -->
{{% details title="💡 Pista" open=false %}}
Arranca FreeRADIUS en primer plano y en modo depuración (`sudo freeradius -X`) para ver cada paso de la autenticación. Después prueba con `radtest`: debes recibir `Access-Accept` con credenciales correctas y `Access-Reject` con incorrectas. El secreto compartido entre cliente y servidor RADIUS debe ser largo y distinto en cada cliente.
{{% /details %}}

---

## Práctica 6.12 · VPN sitio a sitio con IPsec (opcional)

{{< practica num="6.12" tipo="Autónoma" duracion="0 h · trabajo autónomo" nivel="3" ra="RA3:d" entorno="Debian 13 · VirtualBox 7" entrega="túnel IPsec sitio a sitio" >}}

Requiere dos pasarelas (`gw-sede` y `gw-oficina`, cada una con una LAN interna). Sigue el apartado 8.4 de la [teoría](/ud06-seguridad-perimetral/ud06-teoria/) con **strongSwan**:

1. Instala `strongswan-swanctl` y `charon-systemd` en ambas.
2. Crea `/etc/swanctl/conf.d/sede-oficina.conf` en cada extremo (invirtiendo los valores `local_*` y `remote_*`), con propuestas modernas (`aes256gcm16-prfsha384-ecp384`).
3. Carga y comprueba: `sudo swanctl --load-all`, `sudo swanctl --list-sas` (IKE_SA y CHILD_SA en estado `ESTABLISHED/INSTALLED`) y `ping` entre equipos de las dos LAN.
4. **Prueba de fallo:** detén `strongswan` en un extremo y comprueba la pérdida de conectividad; arráncalo de nuevo y mide el tiempo de recuperación. Captura con `tcpdump` y verifica que solo se ven paquetes ESP/UDP 4500 cifrados.
5. **Mejora:** sustituye la clave precompartida por **certificados** firmados por la CA de la UD3 y justifica por qué es más seguro.

---

## Tarea del proyecto · Seguridad perimetral del Colegio San Jorge

> [!IMPORTANT]
> Esta tarea **no se entrega por separado**: es un **hito** de la práctica integradora obligatoria **INT-2** (entrega: 22/03/2027). Consulta [Prácticas integradoras](/guia/practicas-integradoras/).

{{< practica etiqueta="Tarea" num="6.13" tipo="Proyecto" duracion="2 h" nivel="3" ra="RA1:h;RA3;RA4;RA5" entorno="Debian 13 · VirtualBox 7" entrega="informe técnico del perímetro" >}}

**Entrega** (PDF o Markdown con capturas y ficheros de configuración sin secretos), basada en el supuesto de la teoría:

1. **Análisis y diseño**: zonas, diagrama, **matriz de flujos** y justificación de la arquitectura (un cortafuegos de tres patas frente a dos cortafuegos).
2. **Implantación** de las prácticas 2 y 3 (reglas nftables y NAT) con el fichero `nftables.conf` comentado.
3. **Plan de pruebas** ejecutado con la tabla positivas/negativas y los contadores de reglas.
4. **Registro y diagnóstico**: eventos analizados, procedimiento de respuesta inicial y la resolución de **una avería guiada** (síntoma → hipótesis → prueba → solución).
5. **Proxy**: Squid con ACL, autenticación y modo transparente; análisis de `access.log`; reflexión sobre HTTPS y privacidad.
6. **Proxy inverso**: Nginx con TLS, cabeceras y limitación; valoración del WAF.
7. **Continuidad**: diseño de HA, copia cifrada y **restauración probada** con su tiempo.
8. **Documentación** final del cortafuegos (diagrama, matriz, configuración, procedimiento de restauración y excepciones).

| Criterio | Peso |
| --- | --- |
| Análisis, zonas y matriz de flujos | 15 % |
| Reglas del cortafuegos y NAT (mínimo privilegio) | 25 % |
| Pruebas, registros y diagnóstico | 20 % |
| Proxy directo e inverso (Squid / Nginx) | 20 % |
| Alta disponibilidad, copias y restauración | 10 % |
| Documentación y claridad | 10 % |

---

## Problemas habituales

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| Pierdo el SSH al aplicar reglas | Falta la regla de administración en `entrada` | «Deshacer» programado; consola de VirtualBox; `nft flush ruleset` |
| La web publicada no responde | DNAT, `forward`, `ip_forward`, *gateway* o servicio | Método de diagnóstico del apartado 8.3 de la teoría |
| `nft -c` falla | Error de sintaxis (llaves, `;`, variable sin definir) | Lee el mensaje: indica línea y columna |
| Los registros `log` no aparecen | Una regla anterior acepta o descarta ya el paquete | Orden de reglas y contadores |
| `apt update` falla en `web-dmz` | La regla DMZ→Internet o el DNS | Revisa la regla de la DMZ y `resolv.conf` |
| Squid no arranca | Error en `squid.conf` o caché sin crear | `squid -k parse`; `journalctl -u squid`; `squid -z` |
| `407` con credenciales correctas | Ruta del *helper* incorrecta o permisos del fichero | Prueba el *helper* a mano; `chown root:proxy` |
| `502 Bad Gateway` en Nginx | Backend parado o SELinux (AlmaLinux) | `ss -tlnp`; `setsebool -P httpd_can_network_connect on` |
| Tras apagar el principal no hay conmutación | Prioridades, protocolo 112 bloqueado | `tcpdump -ni enp0s8 proto 112`; reglas de `entrada` |

## Buenas prácticas de seguridad aplicadas

- **Política `drop` por defecto**, reglas mínimas justificadas por la matriz de flujos.
- **DMZ → LAN denegado y registrado**; la DMZ solo sale a lo necesario.
- **Pruebas positivas y negativas** tras cada cambio, con evidencia.
- **Cambios con red de seguridad**: copia, `nft -c`, «deshacer» programado.
- Administración del cortafuegos **solo** desde la red de gestión.
- Registros con límite, hora sincronizada y centralizados; informes de Squid con acceso restringido.
- Proxy: informar a los usuarios y no inspeccionar HTTPS sin justificación legal.
- Copias de configuración **cifradas** y fuera del cortafuegos; restauración probada.

## Preguntas de autoevaluación

1. ¿Qué es una DMZ y por qué la DMZ no debe poder iniciar conexiones hacia la LAN?
2. ¿Qué diferencia hay entre un cortafuegos con estado y uno sin estado?
3. ¿En qué hook se aplica el DNAT y en cuál el masquerade? ¿Por qué?
4. ¿Qué diferencia hay entre `drop` y `reject`? ¿Cuándo usar cada uno?
5. ¿Qué cinco requisitos deben cumplirse para publicar un servicio de la DMZ?
6. ¿Para qué sirve `nft -c -f` y por qué conviene programar un «deshacer» antes de aplicar reglas por SSH?
7. ¿Qué datos mínimos debe contener un registro de cortafuegos para ser útil?
8. ¿Qué diferencia hay entre un proxy directo, uno transparente y uno inverso?
9. ¿Por qué el proxy transparente no intercepta HTTPS con facilidad y qué implicaciones legales tiene la inspección TLS?
10. ¿Qué ventajas aporta Nginx como proxy inverso frente a exponer los servidores directamente?
11. ¿Por qué un WAF debe empezar en modo detección?
12. ¿Qué aporta `conntrackd` en un par de cortafuegos redundantes?
13. ¿Qué incluirías en la documentación de un cortafuegos?

## Resumen

Has construido un perímetro completo: tres zonas con política `drop`, publicación por DNAT, contención de la DMZ, registros útiles, proxies que controlan la salida y protegen la entrada, y un plan de continuidad con copias y alta disponibilidad. Lo importante: **planificar con una matriz de flujos, aplicar con red de seguridad, comprobar cada fila con pruebas positivas y negativas y documentar**.

## Referencias y documentación oficial

- nftables wiki: <https://wiki.nftables.org>
- OPNsense: <https://docs.opnsense.org> · pfSense CE: <https://docs.netgate.com/pfsense/en/latest/>
- Squid: <http://www.squid-cache.org/Doc/>
- Nginx: <https://nginx.org/en/docs/>
- OWASP CRS: <https://coreruleset.org>
- NIST SP 800-41 Rev. 1, *Guidelines on Firewalls and Firewall Policy*: <https://csrc.nist.gov/pubs/sp/800/41/r1/final>
- CCN-STIC: <https://www.ccn-cert.cni.es/guias.html>
