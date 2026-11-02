---
title: "UD06 · Casos de ataque y defensa"
weight: 3
bookToc: true
---

# UD06 · Casos de ataque y defensa

{{< ra "RA3:a,b,d,e" "RA4:c,d,e,g" "RA5:h" >}}

El perímetro es la frontera entre la red interna e Internet, y por eso recibe dos tipos de ataque muy distintos: los que intentan **tumbar** los servicios publicados (denegación de servicio) y los que intentan **entrar** por lo que hemos dejado expuesto (interfaces de administración, VPN y cortafuegos sin actualizar). En esta página reproduces ambos en el laboratorio del cortafuegos `fw`.

| Caso | Ataque | Caso real | Tipo |
|---|---|---|---|
| [6.A](#caso-6a--inundación-syn-contra-un-servicio-publicado) | Denegación de servicio por inundación SYN | NoName057(16) contra webs españolas (2023-2025) | Laboratorio |
| [6.B](#caso-6b--interfaz-de-administración-expuesta-a-internet) | Interfaz de administración expuesta a Internet | Controladores de refrigeración de supermercados (2026) | Laboratorio |
| [6.C](#caso-6c--cuando-el-perímetro-es-el-objetivo) | Explotación de cortafuegos y VPN sin parchear | Vulnerabilidades en KEV de fabricantes de seguridad perimetral | Análisis |
| [Búsqueda](#búsqueda-de-vulnerabilidades-en-equipos-perimetrales) | Vulnerabilidades de cortafuegos, VPN y *proxies* | — | Autónoma |

> [!IMPORTANT]
> Las pruebas de inundación se lanzan **solo** desde `sad-cli` contra `fw` y `web-dmz`, dentro de las redes de VirtualBox. Lanzar tráfico de inundación contra un servicio ajeno es un delito de interrupción de sistemas (art. 264 bis del Código Penal), aunque dure segundos. Recuerda las [normas de laboratorio](/ud01/ud01-casos/#antes-de-empezar-ética-y-legalidad-del-laboratorio). Estos casos **no se entregan**.

### Laboratorio común

Es el laboratorio de las prácticas 6.2 y 6.3, con el *ruleset* de tres zonas cargado y la web de la DMZ publicada por DNAT:

| VM | IP | Papel en estos casos |
|---|---|---|
| `fw` | WAN 192.168.100.100 · LAN 192.168.50.1 · DMZ 172.16.0.1 | Cortafuegos con nftables |
| `web-dmz` | 172.16.0.10 | Servidor web publicado (Apache) |
| `sad-cli` | 192.168.100.10 (y 192.168.100.11 como «cliente legítimo») | «Internet»: atacante y cliente de pruebas |
| `cli-lan` | 192.168.50.10 | Puesto del administrador |

Haz una **instantánea** de `fw` y `web-dmz` antes de empezar.

---

## Caso 6.A · Inundación SYN contra un servicio publicado

{{< practica etiqueta="Caso" num="6.A" tipo="Guiada" duracion="2 h · trabajo autónomo" nivel="3" ra="RA4:d,e,g;RA3:a" entorno="Debian 13 · nftables · hping3 · conntrack" entrega="medidas antes y después de las contramedidas" >}}

### El caso real

**NoName057(16)** es un grupo hacktivista prorruso que desde 2022 coordina ataques de **denegación de servicio distribuida** (DDoS) contra webs de administraciones, bancos, transporte y empresas de países que apoyan a Ucrania. En España intentó tumbar, entre otros, el portal del **Ministerio del Interior** durante las elecciones generales de julio de 2023. Su método: reclutar «voluntarios» que instalaban una herramienta llamada **DDoSia** y lanzaban peticiones a la vez contra los objetivos del día. En **julio de 2025** la operación internacional **Eastwood**, coordinada por Europol y Eurojust con participación de la Guardia Civil, desmanteló más de 600 servidores del grupo, con registros en Madrid, Barcelona y Zaragoza.

El volumen de este tipo de ataques no deja de crecer: según Cloudflare, en el **primer semestre de 2026** se mitigaron 23,2 millones de ataques DDoS de capa de red, **935 de ellos por encima de 1 Tbps**, y más del 90 % duraron **menos de 10 minutos**: demasiado rápidos para que una persona reaccione a mano.

> [!TIP]
> **Caso real de INCIBE (Línea 017).** Una tienda *online* española sufrió un ataque contra su **pasarela de pagos**: más de 1 800 intentos de operación en pocas horas. Al cambiar de banco, el ataque se repitió contra el nuevo. INCIBE recomendó, entre otras medidas, credenciales robustas con doble factor en el gestor de contenidos, avisar al alojamiento y a la pasarela, recopilar evidencias, denunciar y, como prevención, separar entornos, valorar una **DMZ** y **monitorizar el tráfico**. [Lee el caso completo](https://www.incibe.es/linea-de-ayuda-en-ciberseguridad/casos-reales/e-commerce-bloqueado-por-un-ataque-ddos-su-pasarela-de-pagos).

{{< figura src="ud06/ddos-1tbps.svg" alt="Ataques DDoS de más de 1 Tbps por trimestre" caption="Los ataques hipervolumétricos se multiplicaron por seis en un trimestre (Cloudflare, 2026)." >}}

### Tipos de DDoS y dónde se defienden

| Tipo | Ejemplo | Qué agota | Dónde se mitiga |
|---|---|---|---|
| **Volumétrico** (capa 3) | Amplificación DNS, NTP, CLDAP | El ancho de banda del enlace | Proveedor de Internet o servicio *anti-DDoS* (CDN): **antes** de llegar a tu enlace |
| **De protocolo** (capa 4) | Inundación SYN | Tablas de conexiones del servidor y del cortafuegos | Cortafuegos y servidor (SYN *cookies*, límites) |
| **De aplicación** (capa 7) | Inundación HTTP | CPU, procesos o base de datos del servidor web | *Proxy* inverso / WAF / balanceador (práctica 6.6, UD07) |

> [!NOTE]
> Un cortafuegos propio **no puede** detener un ataque volumétrico de cientos de Gbps: el enlace se satura antes de que los paquetes lleguen a él. Para eso se contrata protección al proveedor o a una CDN. Lo que sí puede y debe hacer el perímetro es resistir ataques de protocolo y limitar abusos de clientes individuales.

{{< figura src="ud06/syn-flood.svg" alt="Saludo TCP normal e inundación SYN" caption="En la inundación SYN el atacante nunca completa el saludo y agota la cola del servidor." >}}

### Ciclo del caso

| Fase | Descripción |
|---|---|
| **Vulnerabilidad** | Servidor sin SYN *cookies*; cortafuegos sin límites por origen; tabla de seguimiento de conexiones (*conntrack*) del cortafuegos de tamaño limitado |
| **Ataque** | `hping3` envía miles de paquetes SYN por segundo al puerto 80 publicado, sin completar nunca la conexión |
| **Detección** | Muchas conexiones en estado `SYN-RECV`; aviso del núcleo *Possible SYN flooding*; contador de *conntrack* disparado; reglas `limit` que empiezan a descartar |
| **Mitigación** | SYN *cookies* en el servidor; límite de conexiones nuevas y de conexiones simultáneas **por IP** en el cortafuegos; protección aguas arriba para lo volumétrico |
| **Comprobación** | Durante el ataque, un cliente legítimo sigue cargando la web en un tiempo razonable |

### Qué es una inundación SYN

Una conexión TCP empieza con el **saludo en tres pasos**: el cliente envía `SYN`, el servidor responde `SYN-ACK` y **reserva memoria** para esa conexión a medias, y el cliente confirma con `ACK`. En una inundación SYN el atacante envía miles de `SYN` y **nunca** contesta: el servidor llena su cola de conexiones a medias y deja de aceptar clientes legítimos.

Las **SYN *cookies*** resuelven el problema en el servidor: cuando la cola se llena, el servidor no guarda nada y codifica la información de la conexión en el número de secuencia del `SYN-ACK`. Solo si llega el `ACK` correcto reconstruye la conexión.

### 1. Línea base

En `web-dmz`, desactiva **temporalmente** las SYN *cookies* para ver el efecto del ataque (en Debian vienen activadas):

```bash
sysctl net.ipv4.tcp_syncookies net.ipv4.tcp_max_syn_backlog
sudo sysctl -w net.ipv4.tcp_syncookies=0          # SOLO para el laboratorio
```

En `sad-cli`, añade una segunda IP que hará de **cliente legítimo** y mide el tiempo de carga normal:

```bash
sudo ip addr add 192.168.100.11/24 dev enp0s3
curl -s -o /dev/null --interface 192.168.100.11 -w 'HTTP %{http_code} en %{time_total} s\n' --max-time 10 http://192.168.100.100/
```

En `fw`, instala la herramienta para consultar la tabla de conexiones:

```bash
sudo apt install -y conntrack
sudo conntrack -C                                   # número de conexiones seguidas ahora
sysctl net.netfilter.nf_conntrack_max               # máximo antes de descartar conexiones nuevas
```

### 2. El ataque (en `sad-cli`)

`hping3` construye paquetes TCP a medida. Instálalo antes de aislar la máquina.

```bash
sudo apt install -y hping3
sudo timeout 60 hping3 -S -p 80 --flood -I enp0s3 -a 192.168.100.10 192.168.100.100
```

- `-S`: activa el indicador SYN; `-p 80`: puerto destino.
- `--flood`: envía tan rápido como puede, sin esperar respuestas.
- `-a 192.168.100.10`: IP origen (la propia; un atacante real la falsificaría con `--rand-source`).
- `timeout 60`: el ataque se detiene solo al cabo de 60 segundos. **No lo quites.**

Mientras dura, repite la medida del cliente legítimo desde otra terminal de `sad-cli`.

### 3. Detección

En `web-dmz`:

```bash
ss -tan state syn-recv | wc -l                                   # conexiones a medias
sudo journalctl -k --since "5 min ago" | grep -i "syn flooding"
nstat -az TcpExtListenOverflows TcpExtListenDrops TcpExtSyncookiesSent
```

En `fw`:

```bash
sudo conntrack -C
sudo conntrack -L -p tcp --state SYN_SENT 2>/dev/null | wc -l
```

{{% details title="🎯 Resultado esperado" open=false %}}
- Sin SYN *cookies*, `ss` muestra cientos de conexiones en `SYN-RECV`, `TcpExtListenDrops` crece y el cliente legítimo tarda segundos o falla por tiempo de espera (`HTTP 000`).
- En `fw`, el contador de `conntrack` sube muy deprisa: **el cortafuegos también es víctima**, porque cada SYN nuevo ocupa una entrada de su tabla. Si llega a `nf_conntrack_max`, el núcleo registra `nf_conntrack: table full, dropping packet` y empieza a descartar **cualquier** conexión nueva, incluida la de la LAN.
{{% /details %}}

### 4. Mitigación

**a) En el servidor: SYN *cookies*.**

```bash
sudo sysctl -w net.ipv4.tcp_syncookies=1
echo 'net.ipv4.tcp_syncookies = 1' | sudo tee /etc/sysctl.d/90-syncookies.conf
sudo sysctl --system | grep syncookies
```

**b) En el cortafuegos: límites por origen.** Añade a la tabla `inet filtro` de `/etc/nftables.conf` (copia antes el fichero) dos conjuntos dinámicos y una cadena auxiliar, **antes** de la cadena `reenvio`:

```text
  set limite_nuevas {                       # tasa de conexiones nuevas por IP
    type ipv4_addr
    flags dynamic,timeout
    timeout 1m
  }

  set limite_simultaneas {                  # conexiones abiertas a la vez por IP
    type ipv4_addr
    flags dynamic
    size 65535
  }

  chain inundacion {                        # registra (con moderación) y descarta
    limit rate 5/minute log prefix "FW-SYNFLOOD: "
    drop
  }
```

Y estas dos reglas al **principio** de la cadena `reenvio`, justo después de `ct state invalid drop` (deben ir antes de la regla que acepta el tráfico hacia la web publicada):

```text
    # Anti-inundación hacia la web publicada
    iifname $WAN ip daddr $WEB_PUB tcp flags & (syn|ack) == syn ct state new \
      add @limite_nuevas { ip saddr limit rate over 25/second burst 50 packets } \
      counter jump inundacion
    iifname $WAN ip daddr $WEB_PUB tcp dport { 80, 443 } ct state new \
      add @limite_simultaneas { ip saddr ct count over 60 } counter reject with tcp reset
```

- `add @limite_nuevas { ip saddr limit rate over 25/second … }` lleva **un contador por cada IP origen**. Mientras una IP no supere 25 conexiones nuevas por segundo (con ráfagas de 50), la regla no coincide; cuando la supera, sus paquetes saltan a la cadena `inundacion`. Las entradas caducan al minuto (`timeout 1m`).
- La cadena `inundacion` registra como máximo 5 líneas por minuto y **descarta siempre**. Si pusiéramos `limit rate 5/minute log … drop` en una sola regla, el `limit` afectaría también al `drop` y solo se descartarían 5 paquetes por minuto: un error típico.
- `ct count over 60` limita las **conexiones simultáneas** por IP y las rechaza con un *reset* TCP.

Estas reglas se han comprobado con `nft -c` (nftables 1.0.9 y posteriores).

```bash
sudo cp /etc/nftables.conf /etc/nftables.conf.antes-ddos
sudo nft -c -f /etc/nftables.conf && echo "SINTAXIS CORRECTA"
sudo systemd-run --on-active=180 --unit=deshacer-fw nft -f /etc/nftables.conf.antes-ddos   # red de seguridad
sudo nft -f /etc/nftables.conf
sudo systemctl stop deshacer-fw.timer                                                     # si todo va bien
```

> [!WARNING]
> Los límites por IP pueden bloquear a usuarios legítimos que comparten IP pública (una empresa entera detrás de un NAT, un aula, una red móvil). Ajusta los valores midiendo el tráfico normal y revisa los registros `FW-SYNFLOOD` después de activarlos.

### 5. Comprobación

1. Repite el ataque de 60 segundos y, a la vez, la medida del cliente legítimo (192.168.100.11).
2. Revisa los contadores y el registro:

```bash
sudo nft list set inet filtro limite_nuevas            # la IP del atacante aparece en el conjunto
sudo nft list chain inet filtro reenvio | grep -E 'inundacion|ct count'
sudo journalctl -k --since "5 min ago" | grep -c "FW-SYNFLOOD"
```

3. Completa la tabla:

| Medida | Sin contramedidas | Con SYN *cookies* | Con SYN *cookies* + límites nftables |
|---|---|---|---|
| Conexiones `SYN-RECV` en `web-dmz` | | | |
| Contador `conntrack` máximo en `fw` | | | |
| Tiempo de carga del cliente legítimo | | | |

4. **Prueba de los límites de la defensa**: repite el ataque con `--rand-source` (origen aleatorio). ¿Siguen funcionando los límites por IP? ¿Qué medida protege entonces al servidor? ¿Y al cortafuegos?

{{% details title="💡 Pista" open=false %}}
Con orígenes aleatorios cada paquete parece venir de una IP distinta: los límites **por IP** no se activan. El servidor resiste gracias a las SYN *cookies*, pero la tabla *conntrack* del cortafuegos se sigue llenando. En redes reales esto se aborda con filtrado anti-suplantación en los proveedores (BCP 38), protección *anti-DDoS* aguas arriba y, en el cortafuegos, con reglas en la cadena `raw`/`notrack` o SYN *proxy* (`synproxy` en nftables), que quedan fuera del alcance del módulo.
{{% /details %}}

### 6. Limpieza

```bash
# sad-cli
sudo ip addr del 192.168.100.11/24 dev enp0s3
# web-dmz: deja las SYN cookies activadas (valor por defecto y recomendado)
```

### Variantes: Linux, Windows 11 y web

{{< tabs >}}
{{% tab "Linux" %}}
`ss -tan state syn-recv | wc -l`, `conntrack -C`, límites con `nftables` y `tcp_syncookies`.
{{% /tab %}}
{{% tab "Windows 11" %}}
Abre **PowerShell** (`Win` + `X` → *Terminal*; para lo que pida administrador, *Terminal (administrador)*).

Windows 11 como equipo **que vigila** (o como servidor de pruebas):

```powershell
# Conexiones a medias: SynReceived (el equivalente de SYN-RECV)
(Get-NetTCPConnection -State SynReceived -ErrorAction SilentlyContinue).Count
netstat -an | findstr /C:"SYN_RECEIVED"

# La protección contra inundación SYN de Windows ya está activa por defecto desde Windows Vista;
# estos contadores muestran cuántas conexiones están a medias o han fallado
Get-Counter '\TCPv4\Connection Failures', '\TCPv4\Connections Established'
```

El **Monitor de rendimiento** (`perfmon`) permite ver en tiempo real el contador *TCPv4 → Connection Failures*. Windows protege a nivel de sistema (por defecto) y el filtrado por origen se hace en el cortafuegos o en el proxy inverso de delante, no en cada equipo.
{{% /tab %}}
{{% tab "Web" %}}
Observa ataques DDoS **reales y en directo**, sin lanzar ninguno:

- **[Cloudflare Radar](https://radar.cloudflare.com/)**: tráfico de Internet, ataques de capa 3/4 y 7 por país y sector, y cortes de servicio.
- **[Informe DDoS de Cloudflare, 1.er semestre de 2026](https://blog.cloudflare.com/ddos-threat-report-2026-h1/)**: la fuente de la gráfica de esta página.
- Si tu web está detrás de Cloudflare, en *Seguridad → WAF → Reglas de limitación de velocidad* puedes aplicar el mismo límite por IP que en HAProxy, sin tocar tu servidor.
{{% /tab %}}
{{< /tabs >}}

---

## Caso 6.B · Interfaz de administración expuesta a Internet

{{< practica etiqueta="Caso" num="6.B" tipo="Guiada" duracion="1 h · trabajo autónomo" nivel="2" ra="RA3:a,b,e;RA4:c,d" entorno="Debian 13 · nftables · WireGuard · Nmap" entrega="exposición antes y después" >}}

### El caso real

En el [ataque a los supermercados franceses](/ud01/ud01-casos/#caso-1b--supermercados-sin-frío-dispositivos-expuestos-a-internet) de octubre de 2026, el problema de fondo era de **arquitectura perimetral**: miles de paneles de control de refrigeración estaban **publicados en Internet**. La reacción de los operadores lo confirma: en tres días, el número de paneles expuestos en Francia cayó un 71 %. Los expertos lo resumen en una regla: las interfaces de administración de equipos industriales, NAS, cámaras o cortafuegos **nunca se publican directamente**; se accede a ellas desde la red interna o **a través de una VPN**.

### Simulación

En `web-dmz`, crea una «interfaz de administración» de prueba en el puerto 8080 (por ejemplo, la de un equipo de refrigeración):

```bash
sudo mkdir -p /srv/panel && echo "<h1>Panel de control de refrigeración</h1>" | sudo tee /srv/panel/index.html
cd /srv/panel && sudo python3 -m http.server 8080 --bind 172.16.0.10
```

**Error de configuración** en `fw`: alguien la publica para que el técnico externo pueda entrar desde casa. Añade a la cadena `prerouting` de la tabla `ip nat`:

```text
    iifname $WAN tcp dport 8080 dnat to $WEB_PUB:8080          # ERROR: panel publicado en Internet
```

y en `reenvio` la regla correspondiente (`tcp dport { 80, 443, 8080 } ct status dnat accept`). Aplica con el procedimiento seguro.

### Ataque: reconocimiento desde «Internet» (en `sad-cli`)

```bash
nmap -sV -p 22,80,443,8080 192.168.100.100
curl -s http://192.168.100.100:8080/
```

Así es como los buscadores de dispositivos (Shodan, Censys) encuentran estos paneles: recorren Internet probando puertos y guardan lo que responde.

### Mitigación

1. **Elimina** la publicación del puerto 8080 (regla DNAT y regla de reenvío) y vuelve a aplicar el *ruleset*.
2. **Acceso remoto por VPN**: el técnico externo se conecta con **WireGuard** a `fw` (o a la pasarela VPN de la práctica 6.10) y, una vez dentro, accede al panel por su IP interna. Añade en `reenvio` una regla que solo permita llegar al panel desde la red de la VPN:

```text
    iifname "wg0" oifname $DMZ ip saddr 10.99.0.0/24 ip daddr $WEB_PUB tcp dport 8080 counter accept
```

3. Opcional: limita también el origen a la IP del técnico (`ip saddr 10.99.0.5`) y registra cada acceso (`log prefix "PANEL-VPN: "`).

### Comprobación

```bash
# Desde sad-cli SIN VPN
nmap -Pn -p 8080 192.168.100.100                  # filtered (el cortafuegos descarta)
# Desde el cliente CON la VPN levantada
curl -s http://172.16.0.10:8080/                  # el panel responde
```

{{% details title="🎯 Resultado esperado" open=false %}}
Antes de la mitigación, `nmap` muestra `8080/tcp open http SimpleHTTPServer` y `curl` devuelve el panel. Después, desde Internet el puerto aparece como `filtered` y solo es accesible para quien está autenticado en la VPN. Has reducido la **superficie de ataque** del perímetro y has añadido **autenticación fuerte** (claves de WireGuard) y **trazabilidad** (registro de accesos).
{{% /details %}}

### Variantes: Linux, Windows 11 y web

{{< tabs >}}
{{% tab "Linux" %}}
Regla DNAT en `nftables` frente a acceso por VPN con WireGuard.
{{% /tab %}}
{{% tab "Windows 11" %}}
Abre **PowerShell** (`Win` + `X` → *Terminal*; para lo que pida administrador, *Terminal (administrador)*).

```powershell
# ¿Se ve el panel desde fuera? (equivalente al nmap del laboratorio)
Test-NetConnection -ComputerName 192.168.100.100 -Port 8080

# Cortafuegos de Windows: bloquear un puerto de administración desde fuera de la LAN (administrador)
New-NetFirewallRule -DisplayName "Bloquear panel 8080 desde Internet" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Block -Profile Public
New-NetFirewallRule -DisplayName "Permitir panel 8080 solo desde la LAN" -Direction Inbound -Protocol TCP -LocalPort 8080 -RemoteAddress 192.168.50.0/24 -Action Allow -Profile Domain,Private
Get-NetFirewallRule -DisplayName "*panel 8080*" | Format-Table DisplayName, Enabled, Action

# Cliente WireGuard para el acceso remoto seguro
winget install --id WireGuard.WireGuard
```

Importa el archivo de configuración del cliente en la aplicación *WireGuard* y activa el túnel antes de abrir `http://172.16.0.10:8080/`.
{{% /tab %}}
{{% tab "Web" %}}
Comprueba **tu exposición** con fuentes públicas: busca tu IP pública en [Shodan](https://www.shodan.io/) y [Censys](https://search.censys.io/), y compara con el ritmo del caso real: los operadores franceses retiraron del acceso público el **71 %** de los paneles en tres días. En INCIBE, el proyecto **+Ciberseguridad** notifica a las organizaciones españolas con servicios vulnerables expuestos.
{{% /tab %}}
{{< /tabs >}}

---

## Caso 6.C · Cuando el perímetro es el objetivo

{{< practica etiqueta="Caso" num="6.C" tipo="Autónoma" duracion="1 h · trabajo autónomo" nivel="2" ra="RA4:a,f;RA3:d" entorno="Navegador" entrega="análisis de vulnerabilidades perimetrales" >}}

Los cortafuegos, concentradores VPN y pasarelas de acceso remoto están **por definición expuestos a Internet**. Por eso son uno de los objetivos favoritos: una vulnerabilidad en ellos da acceso directo a la red interna, saltándose todas las defensas. En los últimos años se han explotado de forma masiva fallos de VPN y cortafuegos de casi todos los grandes fabricantes (Fortinet, Ivanti, Palo Alto Networks, Cisco, Citrix, SonicWall…), muchos de ellos **antes** de que existiera parche (vulnerabilidades de día cero).

### Actividad

1. En el [catálogo KEV](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) filtra por `Fortinet`, `Ivanti` o `Palo Alto`. ¿Cuántas vulnerabilidades hay? ¿Qué productos afectan (VPN SSL, cortafuegos, gestión)? ¿Cuántas están marcadas como usadas en campañas de *ransomware*?
2. Elige **una** de los últimos 12 meses y busca su aviso en INCIBE-CERT y en la web del fabricante. Anota: producto, versiones, si requería autenticación, si hubo explotación antes del parche y qué mitigación provisional se recomendaba.
3. Responde:
   - ¿Por qué la regla «la interfaz de administración del cortafuegos solo desde la LAN» (cadena `entrada` de `fw`) reduce el riesgo aunque exista una vulnerabilidad?
   - ¿Qué ventaja tiene WireGuard, con muy poco código y sin respuesta a paquetes no autenticados, frente a una VPN SSL con portal web?
   - ¿Qué harías si el fabricante tarda una semana en publicar el parche?

---

## Búsqueda de vulnerabilidades en equipos perimetrales

{{< practica etiqueta="Búsqueda" num="6.D" tipo="Autónoma" duracion="1 h · trabajo autónomo" nivel="1" ra="RA4:a;RA5:a" entorno="Navegador · Debian 13" entrega="tabla de vulnerabilidades del perímetro del laboratorio" >}}

Haz el inventario del software perimetral **de tu laboratorio** y busca una vulnerabilidad relevante (o el último aviso de seguridad) de cada uno:

| Componente | Versión instalada (orden) | Último CVE o aviso relevante | ¿Te afecta? |
|---|---|---|---|
| Núcleo Linux / nftables | `uname -r` · `nft --version` | | |
| OpenSSH | `ssh -V` | | |
| Squid | `squid -v \| head -n 1` | | |
| Nginx | `nginx -v` | | |
| WireGuard | `wg --version` | | |
| strongSwan (si hiciste 6.12) | `ipsec --version` | | |
| OPNsense (si hiciste 6.7) | Panel → *System → Firmware* | | |

Fuentes: Debian Security Tracker (`debsecan`, [caso 4.C](/ud04/ud04-casos/#caso-4c--búsqueda-de-vulnerabilidades-en-tu-propio-servidor)), avisos de INCIBE-CERT, avisos de seguridad de cada proyecto ([Squid](https://github.com/squid-cache/squid/security/advisories), [nginx](https://nginx.org/en/security_advisories.html), [OPNsense](https://opnsense.org/blog/)).

Pregunta final: ¿qué componente de tu perímetro tendría **más prioridad** de actualización y por qué? (Pista: expuesto a Internet + sin autenticación previa + explotación conocida).

---

## Qué debes saber explicar

- Los tipos de DDoS (volumétrico, de protocolo, de aplicación) y **dónde** se mitiga cada uno.
- Qué es una inundación SYN, cómo la frenan las SYN *cookies* y por qué la tabla *conntrack* del cortafuegos también puede saturarse.
- Cómo limitar en nftables la tasa de conexiones nuevas y las conexiones simultáneas por IP, y sus limitaciones (orígenes falsificados, NAT compartido).
- Por qué las interfaces de administración no se publican y cómo se sustituye esa publicación por una VPN.
- Por qué los equipos perimetrales (cortafuegos, VPN) deben actualizarse con máxima prioridad.

## Referencias

- nftables wiki. [Meters / dynamic sets](https://wiki.nftables.org/wiki-nftables/index.php/Meters) y [Connlimits](https://wiki.nftables.org/wiki-nftables/index.php/Connlimits).
- Documentación del núcleo Linux. [ip-sysctl: tcp_syncookies](https://docs.kernel.org/networking/ip-sysctl.html).
- IETF. [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987).
- Cloudflare (2026). [DDoS Threat Report H1 2026](https://blog.cloudflare.com/ddos-threat-report-2026-h1/).
- Euronews (2025). [Desarticulada la red de hackers prorrusos NoName057(16)](https://es.euronews.com/2025/07/17/desarticulada-la-red-de-hackers-prorrusos-noname-057-que-perpetro-ciberataques-en-espana-e).
- INCIBE. [Ataques DDoS: qué son y qué puedo hacer para proteger mi empresa](https://www.incibe.es/empresas/blog/ataques-ddos-que-son-y-que-puedo-hacer-para-proteger-mi-empresa).
- INCIBE, Línea 017. [Caso real: *e-commerce* bloqueado por un ataque DDoS a su pasarela de pagos](https://www.incibe.es/linea-de-ayuda-en-ciberseguridad/casos-reales/e-commerce-bloqueado-por-un-ataque-ddos-su-pasarela-de-pagos).
- CISA. [Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog).
