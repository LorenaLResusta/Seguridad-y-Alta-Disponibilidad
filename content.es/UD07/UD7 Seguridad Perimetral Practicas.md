---
title: "Prácticas"
slug: "practicas"
weight: 2
---

# UD7. Prácticas: seguridad perimetral

> Montaje de un perímetro con WAN, LAN y DMZ en un cortafuegos Linux (nftables): política por defecto, NAT y publicación, registro y diagnóstico, proxy Squid, proxy inverso Nginx con TLS y WAF, y alta disponibilidad y recuperación del cortafuegos.

| Datos de las prácticas | Información |
| --- | --- |
| Módulo | 0378. Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR |
| Duración estimada | 10 horas |
| Entorno | VirtualBox 7: red NAT `SAD-NAT` y redes internas `sad-lan7` y `sad-dmz` |
| Sistemas | Debian 13 (AlmaLinux 10 donde se indica); OPNsense como alternativa |
| Teoría asociada | [Teoría de la UD7](../teoria/) |

---

## 1. Objetivos

- Desplegar una arquitectura de subred apantallada (WAN, LAN, DMZ) con un cortafuegos de tres patas.
- Planificar las reglas con una **matriz de flujos** y aplicarlas con política de denegación por defecto.
- Publicar un servidor de la DMZ mediante **DNAT** y comprobar que la DMZ no puede alcanzar la LAN.
- Revisar los registros del cortafuegos, interpretarlos y **diagnosticar** fallos de conectividad.
- Instalar un proxy **Squid** con ACL, autenticación y modo transparente, y monitorizarlo.
- Configurar un proxy inverso **Nginx** con TLS, cabeceras de seguridad y limitación de peticiones; valorar un WAF.
- Diseñar y probar la alta disponibilidad y la restauración del cortafuegos.

> [!IMPORTANT]
> **Alcance.** Todo el laboratorio es virtual y aislado. Las pruebas de bloqueo se hacen **solo** contra tus máquinas. No uses herramientas de evasión ni de ataque contra destinos ajenos. Antes de tocar el cortafuegos crea una *snapshot* y deja siempre una consola de VirtualBox abierta como acceso de emergencia.

---

## 2. Preparación del laboratorio

### 2.1. Topología y direccionamiento

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

### 2.2. Primero, instalar paquetes (mientras hay salida a Internet)

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

### 2.3. Direccionamiento

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

---

## 3. Práctica 1 · Perímetro, zonas y matriz de flujos

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

---

## 4. Práctica 2 · Cortafuegos con nftables y política `drop`

**Objetivo:** implementar la matriz de flujos (RA4 d, f).

### 4.1. Preparación segura

```bash
# En fw
sudo cp /etc/nftables.conf /etc/nftables.conf.bak                  # copia del fichero original
sudo systemctl disable --now firewalld 2>/dev/null; sudo systemctl disable --now ufw 2>/dev/null
```

Crea `/etc/nftables.conf` con el **ruleset de tres zonas** del apartado 5.3 de la [teoría](../teoria/#53-cortafuegos-de-tres-zonas-completo) (cópialo íntegro; ya incluye filtrado y NAT) y comprueba la sintaxis:

```bash
sudo nft -c -f /etc/nftables.conf && echo "SINTAXIS CORRECTA"
```

### 4.2. Aplicación con red de seguridad

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

### 4.3. Pruebas de aceptación (positivas y negativas)

Rellena la tabla con el resultado real:

| # | Prueba | Desde | Comando | Esperado | Resultado |
| --- | --- | --- | --- | --- | --- |
| 1+ | Web publicada | `sad-cli` | `curl -s -m 3 http://192.168.100.100/` | `<h1>web-dmz</h1>` (tras la práctica 3) | |
| 2− | SSH al `fw` desde fuera | `sad-cli` | `ssh -o ConnectTimeout=3 usuario@192.168.100.100` | Timeout | |
| 3+ | Navegar | `cli-lan` | `curl -s -m 5 -I https://example.org` | `HTTP/2 200` (o similar) | |
| 4+ | SSH a la DMZ | `cli-lan` | `ssh usuario@172.16.0.10` | Funciona | |
| 5− | **DMZ → LAN** | `web-dmz` | `ping -c 2 -W 1 192.168.50.10` | Sin respuesta | |
| 5− | **DMZ → LAN** (TCP) | `web-dmz` | `nc -zv -w 2 192.168.50.10 22` | *Timeout* | |
| 6+ | Actualizar | `web-dmz` | `sudo apt update` | Funciona | |
| 7+ | SSH al `fw` desde LAN | `cli-lan` | `ssh usuario@192.168.50.1` | Funciona | |
| 8− | LAN → puerto no permitido | `cli-lan` | `nc -zv -w 2 192.168.100.10 8080` | *Timeout* | |

Guarda `sudo nft list ruleset > ~/ud7-evidencias/02-ruleset.txt` y las salidas de las pruebas.

### 4.4. Contadores: ¿se aplican realmente las reglas?

```bash
sudo nft list chain inet filtro reenvio | grep -E 'counter|packets'     # paquetes por regla
sudo nft -a list chain inet filtro reenvio                               # con handle (para borrar/insertar)
```

Repite una prueba y observa qué contador aumenta. Explica qué regla ha atendido cada prueba de la tabla anterior.

> [!TIP]
> Si la prueba 1 aún no funciona, es normal: falta el servidor web en la DMZ o el DNAT (práctica 3) o el servicio no escucha. Si pierdes el acceso al `fw`: consola de VirtualBox → `sudo nft flush ruleset` → revisa el fichero.

---

## 5. Práctica 3 · NAT y publicación de un servicio en la DMZ

**Objetivo:** salir con masquerade, publicar con DNAT y verificar el camino completo (RA4 d, RA3 a).

### 5.1. Comprobar los cinco requisitos de la publicación

| Requisito | Dónde se comprueba |
| --- | --- |
| DNAT en `prerouting` | `sudo nft list table ip nat` |
| Regla `forward` hacia la DMZ | `sudo nft list chain inet filtro reenvio` |
| `ip_forward = 1` | `sysctl net.ipv4.ip_forward` |
| *Gateway* de `web-dmz` = 172.16.0.1 | `ip route` en `web-dmz` |
| Servicio escuchando | `ss -tlnp` en `web-dmz` |

### 5.2. Prueba y observación

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

### 5.3. Comprobar la contención de la DMZ

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

### 5.4. Prueba de fallo del servicio

1. En `web-dmz` para Apache (`sudo systemctl stop apache2`) y repite `curl` desde `sad-cli`: observa si el error es *timeout* o *connection refused* y explica **por qué** (el SYN llega y la DMZ responde con RST).
2. Arranca el servicio y verifica la recuperación.
3. **Pregunta:** ¿qué ocurriría si en `web-dmz` olvidases el *gateway*? Compruébalo temporalmente (`sudo ip route del default`) con una captura en el `fw`: ¿se ve el SYN-ACK de vuelta? Restáuralo después.

---

## 6. Práctica 4 · Endurecimiento TCP/IP, registro y diagnóstico

### 6.1. Parámetros del núcleo del cortafuegos

Crea `/etc/sysctl.d/90-perimetro.conf` según el apartado 7 de la teoría, aplica con `sudo sysctl --system` y verifica:

```bash
sysctl net.ipv4.ip_forward net.ipv4.conf.all.rp_filter net.ipv4.conf.all.accept_redirects net.ipv4.tcp_syncookies
```

> [!NOTE]
> Si `sysctl --system` avisa de que `net.netfilter.nf_conntrack_max` no existe, ejecuta `sudo modprobe nf_conntrack` y vuelve a aplicar. Comprueba la ocupación con `sudo conntrack -C`.

### 6.2. Análisis de registros

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

### 6.3. Diagnóstico guiado: tres averías

Pide a un compañero (o hazlo tú tras una *snapshot*) que provoque **una de estas averías** en `fw` sin decirte cuál, y diagnostica con el método del apartado 8.3 de la teoría:

| Avería | Cómo se provoca (en `fw`) | Síntoma |
| --- | --- | --- |
| A | `sudo sysctl -w net.ipv4.ip_forward=0` | Nada pasa entre zonas |
| B | `sudo nft delete rule inet filtro reenvio handle <N>` (la regla de navegación) | `cli-lan` no navega, pero sí llega a la DMZ |
| C | En `web-dmz`: `sudo ip route del default` | La web publicada no responde desde fuera |

Para cada avería documenta: **síntoma observado → hipótesis → prueba que la confirma (comando y salida) → solución → comprobación**. Restaura el estado inicial después de cada una.

---

## 7. Práctica 5 · Proxy directo con Squid

**Objetivo:** controlar y registrar la navegación de la LAN (RA5 a–g). Squid se instala en `fw` (ya en la práctica 2.2).

### 7.1. Configuración con ACL, horario y bloqueos

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

### 7.2. Pruebas desde `cli-lan`

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

### 7.3. Autenticación

1. Crea usuarios con `htpasswd` y configura el *helper* según el apartado 11.4 de la teoría (la ruta del helper cambia entre Debian y AlmaLinux).
2. Prueba **sin** credenciales (esperado: `407`), con credenciales **erróneas** (407) y **correctas** (200):

```bash
curl -sI -x http://192.168.50.1:3128 http://example.org/ | head -1
curl -sI -x http://ana:Mal@192.168.50.1:3128 http://example.org/ | head -1
curl -sI -x http://ana:ClaveAna1@192.168.50.1:3128 http://example.org/ | head -1
sudo tail -n 3 /var/log/squid/access.log            # ahora el log muestra el usuario
```

3. **Diagnóstico:** si recibes `407` con credenciales correctas, prueba el *helper* a mano: `echo "ana ClaveAna1" | /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd` (debe responder `OK`).

### 7.4. Modo transparente

1. Añade a `squid.conf`: `http_port 3129 intercept`; `sudo squid -k parse && sudo squid -k reconfigure`.
2. En `fw`, añade la redirección a la tabla NAT (**antes** de la regla DNAT de Internet→DMZ no es necesario: son interfaces distintas):

```bash
sudo nft add rule ip nat prerouting iifname "enp0s8" ip saddr 192.168.50.0/24 tcp dport 80 redirect to :3129
sudo nft add rule inet filtro entrada iifname "enp0s8" tcp dport 3129 accept
```

3. Desde `cli-lan` **sin** configurar proxy: `curl -sI http://example.org/ | head -1` y comprueba que la petición aparece en `access.log`. Prueba también `curl https://example.org/`: ¿pasa por el proxy? Explica por qué **no**.
4. Para **forzar** el uso del proxy, bloquea en el cortafuegos la salida directa de la LAN al puerto 80 (salvo la redirigida) y valora qué hacer con 443.

### 7.5. Monitorización gráfica

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

## 8. Práctica 6 · Proxy inverso con Nginx, TLS y WAF

**Objetivo:** publicar aplicaciones de forma segura con un proxy inverso (RA5 h).

### 8.1. Dos aplicaciones internas y el proxy

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

### 8.2. TLS y cabeceras de seguridad

Usa un certificado de la **PKI de la UD3** (o genera uno de laboratorio) y configura el servidor HTTPS del apartado 12.3 de la teoría. Comprueba:

```bash
sudo nginx -t && sudo systemctl reload nginx
curl -vk https://localhost/ 2>&1 | grep -E 'SSL connection|subject|issuer|HTTP/'
curl -skI https://localhost/ | grep -iE 'strict-transport|x-content|x-frame|server'
openssl s_client -connect localhost:443 -tls1_1 </dev/null 2>&1 | grep -iE 'alert|handshake failure|Protocol'   # TLS 1.1 debe rechazarse
sudo nmap --script ssl-enum-ciphers -p 443 localhost | head -30                                                # resumen de cifrados
```

Registra la versión de TLS negociada y los cifrados aceptados, y razona si algún protocolo antiguo sigue habilitado.

### 8.3. Limitación de peticiones

Aplica `limit_req` según el apartado 12.4. Genera carga **contra tu propio servidor**:

```bash
sudo apt install -y apache2-utils
ab -n 300 -c 30 http://localhost/app-a/ | grep -E 'Complete requests|Failed requests|Non-2xx|Requests per second'
sudo grep -c 'limiting requests' /var/log/nginx/error.log
```

Anota cuántas peticiones fueron rechazadas (`503`) y ajusta `rate` y `burst` hasta que una navegación normal no se vea afectada.

### 8.4. WAF en modo detección

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

---

## 9. Práctica 7 · Cortafuegos dedicado: OPNsense (opcional)

Repite la política mínima de la práctica 2 con **OPNsense** en lugar de nftables:

1. Crea la VM con los tres adaptadores (WAN `SAD-NAT`, LAN `sad-lan7`, OPT1 `sad-dmz`), instala desde la ISO (verifica su SHA-256) y cambia las credenciales por defecto.
2. Asigna interfaces e IP (LAN `192.168.50.1/24`, OPT1 `172.16.0.1/24`). Accede por `https://192.168.50.1` desde `cli-lan`.
3. Crea **alias** (`WEB_DMZ`, `PUERTOS_WEB`) y las reglas de la matriz de flujos: *LAN* (navegar, SSH a la DMZ), *OPT1/DMZ* (solo salida web y DNS; **bloquear DMZ → LAN con registro**), *WAN* (solo la publicación).
4. Configura la **publicación** en *Firewall → NAT → Port Forward* (WAN:80 → 172.16.0.10:80) y verifica con `sad-cli`.
5. Revisa *Firewall → Log Files → Live View* y localiza los eventos de las pruebas negativas.
6. Haz una **copia de configuración** (*System → Configuration → Backups*), descárgala y cífrala (`gpg --symmetric`).

**Entrega:** capturas de las reglas, del Live View con bloqueos y comparación breve **nftables frente a OPNsense** (administración, trazabilidad, rendimiento, curva de aprendizaje).

---

## 10. Práctica 8 · Alta disponibilidad y recuperación del perímetro

### 10.1. Diseño

Redacta la propuesta de **HA del cortafuegos**: dos cortafuegos, IP virtual en cada zona (VRRP o CARP), sincronización de reglas y de estado de conexiones, red de gestión, alimentación y enlaces redundantes, DNS y monitorización. Justifica **activo-pasivo** frente a **activo-activo**.

### 10.2. Implantación (si dispones de recursos)

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

### 10.3. Copia y restauración

```bash
sudo nft list ruleset | gpg --symmetric --cipher-algo AES256 -o ~/ud7-evidencias/fw-$(date +%F).nft.gpg
sudo cp -a /etc/nftables.conf /etc/sysctl.d/90-fw.conf /etc/squid/squid.conf ~/ud7-evidencias/ 2>/dev/null
```

Prueba la **restauración** en una VM de sustitución: instala nftables, descifra (`gpg -d`), aplica con `nft -f` y repite las pruebas de aceptación. Mide el **tiempo de restauración** (RTO) y anota qué faltaba (rutas, `sysctl`, interfaces, claves).

---

## 11. Problemas habituales

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

---

## 12. Buenas prácticas de seguridad aplicadas

- **Política `drop` por defecto**, reglas mínimas justificadas por la matriz de flujos.
- **DMZ → LAN denegado y registrado**; la DMZ solo sale a lo necesario.
- **Pruebas positivas y negativas** tras cada cambio, con evidencia.
- **Cambios con red de seguridad**: copia, `nft -c`, «deshacer» programado.
- Administración del cortafuegos **solo** desde la red de gestión.
- Registros con límite, hora sincronizada y centralizados; informes de Squid con acceso restringido.
- Proxy: informar a los usuarios y no inspeccionar HTTPS sin justificación legal.
- Copias de configuración **cifradas** y fuera del cortafuegos; restauración probada.

---

## 13. Autoevaluación

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

---

## 14. Tarea evaluable: seguridad perimetral del Colegio San Jorge

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

## 15. Resumen

Has construido un perímetro completo: tres zonas con política `drop`, publicación por DNAT, contención de la DMZ, registros útiles, proxies que controlan la salida y protegen la entrada, y un plan de continuidad con copias y alta disponibilidad. Lo importante: **planificar con una matriz de flujos, aplicar con red de seguridad, comprobar cada fila con pruebas positivas y negativas y documentar**.

---

## 16. Referencias

- nftables wiki: <https://wiki.nftables.org>
- OPNsense: <https://docs.opnsense.org> · pfSense CE: <https://docs.netgate.com/pfsense/en/latest/>
- Squid: <http://www.squid-cache.org/Doc/>
- Nginx: <https://nginx.org/en/docs/>
- OWASP CRS: <https://coreruleset.org>
- NIST SP 800-41 Rev. 1, *Guidelines on Firewalls and Firewall Policy*: <https://csrc.nist.gov/pubs/sp/800/41/r1/final>
- CCN-STIC: <https://www.ccn-cert.cni.es/guias.html>
