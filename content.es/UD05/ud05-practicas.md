---
title: "UD05 · Prácticas"
weight: 2
bookToc: true
---

# UD05 · Prácticas

{{< ra "RA2:c,d,h,i" >}}

Observación y detección de amenazas de capa 2 y 3, segmentación con VLAN y ACL, detección de intrusiones con Suricata y captura y análisis de tráfico en un laboratorio aislado.

| Práctica | Tipo | Nivel | Horas | CE principales |
|---|---|---|--:|---|
| [5.1 Observar ARP y DHCP, y detectar anomalías](#práctica-51--observar-arp-y-dhcp-y-detectar-anomalías) | Guiada | ●●○ | 2 | RA2: c, d |
| [5.2 VLAN y ACL entre segmentos](#práctica-52--vlan-y-acl-entre-segmentos) | Guiada | ●●● | 2 | RA2: c |
| [5.3 Detección de intrusiones con Suricata](#práctica-53--detección-de-intrusiones-con-suricata) | Guiada | ●●● | 2 | RA2: i, c |
| [5.4 Captura y análisis de tráfico](#práctica-54--captura-y-análisis-de-tráfico) | Autónoma | ●●○ | 1 | RA2: d, h |
| [5.5 Diseño y validación de una red segura](#tarea-del-proyecto--diseño-y-validación-de-una-red-segura) | Proyecto | ●●● | 2 | RA2: c, d, h, i |
| **Total** | | | **9 h** | |

> [!NOTE]
> Las prácticas con **—** horas son **trabajo autónomo** (fuera del horario) u opcionales: amplían la unidad, pero no restan tiempo a las 9 h de prácticas oficiales de la unidad. El resto se realiza en el laboratorio, en las horas indicadas.

> [!IMPORTANT]
> **Estas prácticas no se entregan.** Sirven para aprender haciendo en el laboratorio. Pero los **conceptos básicos y las órdenes principales** que aparecen en ellas **entran en la prueba teórico-práctica de la unidad**, así que conviene haberlas hecho. Lo único entregable del módulo son las [dos prácticas integradoras](/guia/practicas-integradoras/); esta unidad contribuye a **INT-2**.

## Qué entra en la prueba de esta unidad

Estos son los contenidos de las prácticas que se preguntan (no hace falta memorizar comandos largos, sí saber **qué hacen y cómo interpretar su resultado**):

- Amenazas de capa 2 y 3: **ARP spoofing** y **servidor DHCP falso**; cómo se detectan y qué función del *switch* las mitiga (*port security*, *DHCP snooping*, DAI) (5.1).
- Para qué sirve la **segmentación con VLAN y ACL** y cómo se escribe una **matriz de flujos** (origen → destino → servicio → permitido/denegado) (5.2).
- Diferencia entre **IDS e IPS**, y la estructura de una **regla de Suricata** (acción, protocolo, direcciones, opciones, `sid`) (5.3).
- Dónde se registran las alertas (`fast.log`, `eve.json`) y cómo se distingue un **verdadero** de un **falso positivo** (5.3).
- Capturar tráfico con `tcpdump` o Wireshark y aplicar **filtros** para aislar una conversación (5.4).

## Objetivos

- Observar el funcionamiento normal de ARP y DHCP y detectar anomalías con herramientas defensivas.
- Segmentar con VLAN 802.1Q en Linux y aplicar ACL entre segmentos con nftables.
- Desplegar Suricata con reglas propias y comprobar sus alertas.
- Capturar y analizar tráfico con `tcpdump` y Wireshark.

> [!IMPORTANT]
> **Alcance ético y legal.** Estas prácticas se realizan **solo** en tu laboratorio virtual aislado. No se incluyen ni se piden herramientas de ataque: se **observan** los protocolos, se **simulan los efectos** de forma local y se practica la **detección y la mitigación**. Nunca captures ni analices tráfico de redes que no sean tuyas (secreto de las comunicaciones; arts. 197 y 197 bis del Código Penal).

## Preparación del laboratorio

#### Topología

```mermaid
flowchart LR
  subgraph "SAD-NAT 192.168.100.0/24 (Internet simulada)"
    CLI[sad-cli<br/>192.168.100.10]
    GW[gw-vpn<br/>192.168.100.90]
    WEB[sad-web<br/>192.168.100.30]
  end
  subgraph "sad-lan 10.10.10.0/24 (LAN de la sede)"
    SRV[srv-lan<br/>10.10.10.10]
  end
  GW --- SRV
  CLI -. túnel WireGuard 10.99.0.0/24 .- GW
```

| VM | Interfaces | Función |
| --- | --- | --- |
| `sad-cli` | `SAD-NAT` (192.168.100.10) | Cliente / «teletrabajador» |
| `sad-web` | `SAD-NAT` (192.168.100.30) | Servidor web, sensor Suricata |
| `gw-vpn` | `SAD-NAT` (192.168.100.90) y `sad-lan` (10.10.10.1) | Pasarela VPN, router, bastión SSH, RADIUS |
| `srv-lan` | `sad-lan` (10.10.10.10, *gateway* 10.10.10.1) | Servidor interno (web + SSH) |

Para la práctica 2 (VLAN) añade una tercera red interna `sad-trunk` a `gw-vpn`, `sad-cli` y `srv-lan` (adaptador adicional en VirtualBox).

#### Preparación común

1. *Snapshot* `ud6-inicio` de cada VM.
2. Comprueba conectividad: `ping -c 2` entre `sad-cli`, `sad-web` y `gw-vpn`; `gw-vpn` ↔ `srv-lan`.
3. Instala las herramientas básicas en todas las VM:

```bash
sudo apt update && sudo apt install -y tcpdump nmap curl jq netcat-openbsd     # AlmaLinux: sudo dnf install -y tcpdump nmap curl jq nmap-ncat
mkdir -p ~/ud6-evidencias && chmod 700 ~/ud6-evidencias
```

4. En `srv-lan` instala un servidor web con una página identificable:

```bash
sudo apt install -y apache2 && echo "<h1>srv-lan interno</h1>" | sudo tee /var/www/html/index.html
```

5. En `gw-vpn` activa el reenvío de paquetes (es un router) y que `srv-lan` use `10.10.10.1` como puerta de enlace:

```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee /etc/sysctl.d/90-router.conf && sudo sysctl --system
```

---

## Práctica 5.1 · Observar ARP y DHCP, y detectar anomalías

{{< practica num="5.1" tipo="Guiada" duracion="2 h" nivel="2" ra="RA2:c,d" entorno="Debian 13 · VirtualBox 7" entrega="capturas de la anomalía ARP/DHCP" >}}

**Objetivo:** entender qué hay que vigilar para detectar ARP spoofing y DHCP falso, **sin atacar a nadie**.

#### ARP en funcionamiento normal

En `sad-cli`:

```bash
ip neigh flush all                                   # vacía la caché ARP (se rehará sola)
sudo tcpdump -n -e -i enp0s3 arp -c 4 &              # observa el ARP (con las direcciones MAC)
ping -c 1 192.168.100.30
wait
ip neigh show | tee ~/ud6-evidencias/01-arp-normal.txt
```

Esperado: una petición `Request who-has 192.168.100.30 tell 192.168.100.10` y la respuesta `Reply 192.168.100.30 is-at <MAC>`. Anota la MAC de `sad-web` (y comprueba con `ip link show enp0s3` en `sad-web` que coincide).

#### Simular **el efecto** de una caché ARP envenenada (solo en tu VM)

Un ARP spoofing consigue que la caché de la víctima contenga una MAC falsa. Puedes **reproducir ese efecto sin enviar ningún paquete a nadie**, escribiendo tú mismo una entrada falsa en la caché de tu propia máquina:

```bash
sudo ip neigh replace 192.168.100.30 lladdr 02:00:00:aa:bb:cc dev enp0s3 nud permanent
ip neigh show 192.168.100.30
ping -c 3 -W 1 192.168.100.30                        # falla: los paquetes van a una MAC que no existe
```

Esto es lo que vería una víctima real: **conectividad rota o tráfico desviado** hacia otro equipo. Observa qué detecta cada herramienta:

```bash
ip neigh show | tee ~/ud6-evidencias/01-arp-falsa.txt     # la MAC no coincide con la real
sudo tcpdump -n -e -i enp0s3 icmp -c 3                    # ¿a qué MAC se envían las tramas?
```

**Recuperación (mitigación del host):** elimina la entrada falsa y fija la correcta como entrada estática para el servidor crítico:

```bash
sudo ip neigh del 192.168.100.30 dev enp0s3
sudo ip neigh replace 192.168.100.30 lladdr <MAC_REAL_DE_SAD-WEB> dev enp0s3 nud permanent
ping -c 2 192.168.100.30                                  # vuelve a funcionar
sudo ip neigh del 192.168.100.30 dev enp0s3               # deja el laboratorio en su estado normal
```

**Para el informe:** ¿qué señales permiten a un administrador **detectar** una caché ARP alterada? ¿Por qué las entradas estáticas **no escalan** y qué medida de red (DAI) es la solución real?

<!-- hint:h1 -->
> [!WARNING]
> Esta práctica **simula el efecto** de una caché envenenada modificando solo la caché ARP de **tu propia VM**; no genera tráfico malicioso hacia la red. Está prohibido (y es delito) enviar respuestas ARP falsas en una red ajena. Al terminar, restaura la caché: `sudo ip neigh flush all`.

#### Detección continua con arpwatch (en `sad-web`)

```bash
sudo apt install -y arpwatch
sudo systemctl enable --now arpwatch
sudo journalctl -u arpwatch --since "10 min ago" --no-pager | tee ~/ud6-evidencias/01-arpwatch.txt
```

`arpwatch` guarda los pares IP–MAC que ve y avisa cuando **cambian** («changed ethernet address»). Genera un cambio **legítimo** para comprobarlo: cambia la MAC de una VM en VirtualBox y reiníciala, o asigna temporalmente la IP de otra VM, y localiza el aviso en el registro.

<!-- hint:h2 -->
{{% details title="🎯 Resultado esperado" open=false %}}
`arpwatch` registra los cambios de pareja IP-MAC. Mira `sudo journalctl -u arpwatch` o `/var/lib/arpwatch/` y busca mensajes como `changed ethernet address` o `flip flop`: son la señal de que una dirección IP ha empezado a ser anunciada por otra MAC.
{{% /details %}}

#### DHCP: observar el intercambio y localizar servidores

En `sad-cli` (con `dhclient` o `NetworkManager`), observa un intercambio DHCP **sin cambiar la configuración**:

```bash
sudo tcpdump -n -i enp0s3 'udp port 67 or udp port 68' -c 8 &
sudo nmap --script broadcast-dhcp-discover -e enp0s3        # pregunta quién ofrece DHCP en TU red de laboratorio
wait
```

Anota **qué servidores DHCP responden**. En una red real, si aparece más de uno donde solo debería haber uno, es un indicio de DHCP no autorizado.

**Resultado esperado:** tabla con las amenazas de capa 2/3 vistas, cómo se detecta cada una en tu laboratorio y qué función de switch la mitiga (port security, DHCP snooping, DAI).

---

## Práctica 5.2 · VLAN y ACL entre segmentos

{{< practica num="5.2" tipo="Guiada" duracion="2 h" nivel="3" ra="RA2:c" entorno="Debian 13 · VirtualBox 7" entrega="configuración VLAN/ACL y pruebas" >}}

> [!TIP]
> **Consejo.** Cuando dos máquinas de VLAN distintas no se ven, comprueba en este orden: **¿están en la VLAN correcta?** (etiqueta del puerto), **¿hay enlace troncal que permita esa VLAN?**, **¿tiene el encaminador una subinterfaz o ruta para ambas?** y, por último, **¿una ACL lo bloquea?** Descartar capa a capa evita ver fallos de red donde solo hay una regla bien aplicada.

**Objetivo:** segmentar con VLAN 802.1Q y permitir solo los flujos necesarios (RA3 a).

Escenario: `gw-vpn` hace de router entre dos VLAN sobre la red interna `sad-trunk`:

| VLAN | Red | Equipo |
| --- | --- | --- |
| 20 (empleados) | 10.10.20.0/24 | `sad-cli` (10.10.20.10), puerta de enlace 10.10.20.1 |
| 40 (servidores) | 10.10.40.0/24 | `srv-lan` (10.10.40.10), puerta de enlace 10.10.40.1 |

> [!NOTE]
> Las interfaces de la red `sad-trunk` pueden llamarse `enp0s9`, `enp0s10`… según la VM. Comprueba con `ip -br a` el nombre real y sustitúyelo en los comandos (`IFACE`).

#### Subinterfaces VLAN

En `gw-vpn`:

```bash
IFACE=enp0s9                                       # interfaz de sad-trunk (ajústala)
sudo ip link set $IFACE up
sudo ip link add link $IFACE name $IFACE.20 type vlan id 20
sudo ip link add link $IFACE name $IFACE.40 type vlan id 40
sudo ip addr add 10.10.20.1/24 dev $IFACE.20
sudo ip addr add 10.10.40.1/24 dev $IFACE.40
sudo ip link set $IFACE.20 up && sudo ip link set $IFACE.40 up
ip -d link show $IFACE.20 | grep -i vlan           # "vlan protocol 802.1Q id 20"
```

En `sad-cli` (VLAN 20):

```bash
IFACE=enp0s9
sudo ip link set $IFACE up
sudo ip link add link $IFACE name $IFACE.20 type vlan id 20
sudo ip addr add 10.10.20.10/24 dev $IFACE.20 && sudo ip link set $IFACE.20 up
sudo ip route add 10.10.40.0/24 via 10.10.20.1
```

En `srv-lan` (VLAN 40):

```bash
IFACE=enp0s9
sudo ip link set $IFACE up
sudo ip link add link $IFACE name $IFACE.40 type vlan id 40
sudo ip addr add 10.10.40.10/24 dev $IFACE.40 && sudo ip link set $IFACE.40 up
sudo ip route add 10.10.20.0/24 via 10.10.40.1
```

<!-- hint:h3 -->
{{% details title="💡 Pista" open=false %}}
Para comprobar que la subinterfaz es una VLAN 802.1Q: `ip -d link show enp0s3.20` (debe aparecer `vlan protocol 802.1Q id 20`). Las subinterfaces se pierden al reiniciar si no las haces persistentes: para el laboratorio basta con recrearlas.
{{% /details %}}

#### Comprobación del aislamiento y del etiquetado

```bash
# Desde sad-cli
ping -c 2 10.10.20.1                               # alcanza el router de su VLAN
ping -c 2 10.10.40.10                              # alcanza el servidor a través del router (aún sin ACL)
```

Captura el etiquetado en `gw-vpn`:

```bash
sudo tcpdump -n -e -i $IFACE vlan -c 6             # cada trama lleva "vlan 20" o "vlan 40"
```

Prueba de aislamiento: en `srv-lan` quita la VLAN y comprueba que ya **no** hay comunicación:

```bash
sudo ip link del $IFACE.40                         # (en srv-lan) y desde sad-cli: ping 10.10.40.10 → sin respuesta
# Restáuralo con los tres comandos del paso anterior antes de continuar
```

> [!TIP]
> Si las VLAN no se comunican y tu red virtual descarta las tramas etiquetadas, comprueba que usas **«Red interna»** de VirtualBox (no NAT) y que todas las VM están en la **misma** red interna `sad-trunk`.

#### ACL entre VLAN con nftables

En `gw-vpn`, crea `/etc/nftables.d/vlans.nft` (la carpeta puede no existir: `sudo mkdir -p /etc/nftables.d`):

```text
table inet vlans {
  chain forward {
    type filter hook forward priority 0; policy drop;
    ct state established,related accept
    ip saddr 10.10.20.0/24 ip daddr 10.10.40.0/24 tcp dport { 80, 443 } accept   # empleados → web de servidores
    ip saddr 10.10.20.0/24 ip daddr 10.10.40.0/24 icmp type echo-request accept    # ping de diagnóstico
    limit rate 5/minute log prefix "VLAN-drop: "
  }
}
```

```bash
sudo nft -c -f /etc/nftables.d/vlans.nft           # comprueba la sintaxis
sudo nft -f /etc/nftables.d/vlans.nft              # aplica
sudo nft list ruleset | head -20
```

Pruebas desde `sad-cli`:

| Prueba | Comando | Resultado esperado |
| --- | --- | --- |
| Web permitida | `curl -s -m 3 http://10.10.40.10/` | Responde |
| SSH no permitido | `ssh -o ConnectTimeout=3 ana@10.10.40.10` | *Timeout*: descartado |
| Ping permitido | `ping -c 2 10.10.40.10` | Responde |
| Sentido inverso | desde `srv-lan`: `curl -m 3 http://10.10.20.10/` | Descartado |

Mira el registro de lo bloqueado en `gw-vpn`: `sudo journalctl -k --since "5 min ago" | grep VLAN-drop`.

**Resultado esperado:** tabla de flujos (origen → destino → servicio → permitido/denegado) con la evidencia de cada prueba y el volcado de `nft list ruleset`.

<!-- hint:h4 -->
> [!TIP]
> Comprueba la sintaxis **antes** de cargar (`sudo nft -c -f …`) y haz la prueba con una red de seguridad. Después valida las dos direcciones: lo permitido **funciona** y lo prohibido **falla** (pruebas positivas y negativas). Los contadores (`counter`) te dicen qué regla actuó.

---

## Práctica 5.3 · Detección de intrusiones con Suricata

{{< practica num="5.3" tipo="Guiada" duracion="2 h" nivel="3" ra="RA2:i,c" entorno="Debian 13 · VirtualBox 7" entrega="regla propia y alerta de Suricata" >}}

> [!TIP]
> **Consejo.** Antes de arrancar Suricata comprueba la configuración con `sudo suricata -T -c /etc/suricata/suricata.yaml` y, tras lanzar el ataque de prueba, consulta las alertas con `sudo tail -f /var/log/suricata/fast.log`. Si no aparece nada, comprueba primero que escucha en la **interfaz correcta** y que `HOME_NET` coincide con tu red de laboratorio.

**Objetivo:** desplegar un NIDS, escribir reglas propias y comprobar que alerta (RA2 i).

En `sad-web` (sensor, ve el tráfico dirigido a él):

```bash
sudo apt install -y suricata jq
sudo cp /etc/suricata/suricata.yaml /etc/suricata/suricata.yaml.bak
suricata --build-info | head -3 | tee ~/ud6-evidencias/06-suricata-version.txt
sudo suricata-update                                           # descarga las reglas Emerging Threats Open
```

1. **Edita `/etc/suricata/suricata.yaml`**: `HOME_NET: "[192.168.100.0/24]"` y, en `af-packet`, la interfaz `enp0s3`. Añade `- local.rules` bajo `rule-files:`.
2. **Crea reglas propias** en `/var/lib/suricata/rules/local.rules`:

```text
alert http any any -> $HOME_NET any (msg:"LAB acceso a /admin"; http.uri; content:"/admin"; nocase; sid:1000001; rev:1;)
alert icmp any any -> $HOME_NET any (msg:"LAB ping detectado"; itype:8; sid:1000002; rev:1;)
alert tcp any any -> $HOME_NET 22 (msg:"LAB posible fuerza bruta SSH"; flow:to_server; flags:S; threshold:type both, track by_src, count 5, seconds 30; sid:1000003; rev:1;)
```

3. **Valida y arranca:**

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml -v             # "Configuration provided was successfully loaded"
sudo systemctl enable --now suricata
sudo tail -n 5 /var/log/suricata/suricata.log                  # espera "engine started"
```

4. **Genera tráfico de prueba** desde `sad-cli`, contra **tu** `sad-web`:

```bash
ping -c 2 192.168.100.30
curl -s http://192.168.100.30/admin -o /dev/null
for i in 1 2 3 4 5 6; do nc -z -w1 192.168.100.30 22; done    # varias conexiones a SSH en pocos segundos (tráfico de prueba, sin credenciales)
```

5. **Revisa las alertas** en `sad-web`:

```bash
sudo tail -n 10 /var/log/suricata/fast.log
sudo jq -c 'select(.event_type=="alert") | {hora:.timestamp, regla:.alert.signature, origen:.src_ip, destino:.dest_ip}' /var/log/suricata/eve.json | tail -10 | tee ~/ud6-evidencias/06-alertas.txt
```

**Análisis:** para cada alerta indica si es un verdadero positivo y qué haría el administrador. Escribe **una regla nueva** que detecte accesos a `/phpmyadmin` y pruébala.

**Ampliación (IPS):** en `gw-vpn` o `sad-web` (con reenvío), dirige el tráfico a `nfqueue` y ejecuta Suricata con `-q 0`, siguiendo el apartado 10.2 de la teoría; cambia una regla de prueba a `drop` y comprueba que corta la petición. **Haz una *snapshot* antes**: un fallo puede dejar la máquina sin red.

<!-- hint:h10 -->
{{% details title="🔧 Si algo falla" open=false %}}
- **Validar la configuración y las reglas antes de arrancar:** `sudo suricata -T -c /etc/suricata/suricata.yaml -v`.
- **No genera alertas:** comprueba que escucha en la interfaz correcta (`af-packet`), que la regla está cargada (`rule-files`) y que generas tráfico que la cumple.
- Las alertas están en `/var/log/suricata/fast.log` y, con más detalle, en `eve.json` (consúltalo con `jq`).
{{% /details %}}

---

## Práctica 5.4 · Captura y análisis de tráfico

{{< practica num="5.4" tipo="Autónoma" duracion="1 h" nivel="2" ra="RA2:d,h" entorno="Debian 13 · VirtualBox 7" entrega="captura filtrada y análisis" >}}

> [!NOTE]
> **Comentario.** El análisis de tráfico es una forma de ver lo que dicen los protocolos «en voz alta». Un protocolo seguro (SSH, HTTPS) se ve como una conversación sin contenido legible; uno inseguro (Telnet, HTTP, FTP) enseña usuario y contraseña. Lo que cambia al pasar de uno a otro es lo que justifica la medida de protección y, a la vez, lo que debes poder explicar en la prueba.

**Objetivo:** leer el tráfico para diagnosticar y para verificar medidas de seguridad.

1. En `sad-web` captura 40 paquetes mientras haces desde `sad-cli` una petición web y una consulta DNS:

```bash
sudo tcpdump -ni enp0s3 -w ~/ud6-evidencias/07-captura.pcap 'host 192.168.100.10' -c 40 &
curl -s http://192.168.100.30/ >/dev/null; nslookup debian.org >/dev/null
wait
```

2. Copia la captura a tu equipo (`scp`) y ábrela en **Wireshark**. Responde con capturas de pantalla:
   - Localiza el **3-way handshake** TCP (`tcp.flags.syn == 1`). ¿Qué números de secuencia usa cada extremo?
   - Con `http.request`, ¿qué versión de HTTP y qué cabeceras `User-Agent` y `Host` se envían?
   - Haz *Follow → TCP Stream*: ¿se ve el contenido en claro?
   - Con `dns`, ¿qué tipo de registros se consultan? ¿Viajan cifrados?
3. Repite con una petición **HTTPS** y localiza el `Client Hello` (`tls.handshake.type == 1`): ¿qué versión de TLS se negocia? ¿Qué información sigue siendo visible (SNI)? ¿Qué ya no lo es?
4. **Diagnóstico:** provoca un fallo (por ejemplo, un puerto cerrado con `curl http://192.168.100.30:8081`) y busca en la captura el paquete `RST`. Compáralo con un puerto **filtrado** (regla `drop` en el cortafuegos): ¿qué diferencia se ve?

<!-- hint:h11 -->
{{% details title="💡 Pista" open=false %}}
Filtros de visualización muy útiles en Wireshark: `dns`, `http`, `tcp.flags.syn==1 && tcp.flags.ack==0` (inicios de conexión), `ip.addr==192.168.100.30`, `tls.handshake.type==1` (ClientHello). Con *Seguir flujo TCP* (clic derecho) verás la conversación completa: en HTTP, en claro; en HTTPS, cifrada.
{{% /details %}}

---

## Tarea de repaso del proyecto (no se entrega) · Diseño y validación de una red segura

> [!IMPORTANT]
> Esta tarea **no se entrega ni se puntúa**. Es el ensayo de la parte de esta unidad en la práctica integradora obligatoria **INT-2** ([qué se entrega y cómo se corrige](/guia/practicas-integradoras/)). Hazla para llegar a INT-2 con las piezas montadas; sus conceptos básicos también entran en la prueba de la unidad.

{{< practica etiqueta="Tarea de repaso" num="5.5" tipo="Proyecto" duracion="2 h" nivel="3" ra="RA2:c,d,h,i" entorno="Debian 13 · VirtualBox 7" entrega="informe de red segura" >}}

Para una empresa de 50 usuarios con una sede secundaria, teletrabajo, un servicio web publicado y Wi-Fi para invitados (ver supuesto de la teoría), redacta una memoria (PDF o Markdown, no se entrega) con:

1. **Diagrama lógico**: VLAN, subredes, DMZ, WLAN, sedes, VPN y puntos de control.
2. **Inventario de activos, amenazas y controles**, usando el ciclo amenaza → vulnerabilidad → ataque → detección → mitigación → comprobación.
3. **Tabla de VLAN, direccionamiento y matriz de flujos** (denegación por defecto) con las reglas nftables equivalentes.
4. **Diseño Wi-Fi**: WPA3/Enterprise, invitados aislados, control de acceso.
5. **VPN de acceso remoto** (WireGuard) con rutas, DNS, autenticación fuerte y revocación; **sitio a sitio** (IPsec) justificada.
6. **Detección y registros**: ubicación de Suricata y qué alertas priorizas; qué registros se centralizan.
7. **Evidencias** de las prácticas (capturas, `wg show`, `radtest`, alertas de Suricata, `nft list ruleset`) y **plan de pruebas** con reversión.

| Criterio | Peso |
| --- | --- |
| Amenazas, activos y segmentación | 20 % |
| Reglas de cortafuegos y mínimo privilegio | 20 % |
| Seguridad Wi-Fi y control de acceso | 15 % |
| VPN y acceso remoto seguro | 15 % |
| Detección, registros y respuesta | 15 % |
| Evidencias reproducibles y análisis | 10 % |
| Claridad y justificación técnica | 5 % |

---

## Problemas habituales

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| Las VLAN no se ven | Red NAT en lugar de Red interna, nombre de interfaz erróneo | `ip -br a`; usa `sad-trunk` en las tres VM |
| `nft -c` da error | Sintaxis o carpeta inexistente | Lee el mensaje (indica línea y columna) |
| WireGuard sin *handshake* | Claves intercambiadas, `Endpoint` o UDP 51820 bloqueado | `sudo wg show`; compara claves públicas; revisa cortafuegos |
| Conecta el túnel pero no llega a `srv-lan` | `ip_forward`, regla `forward` o ruta de vuelta | `sysctl net.ipv4.ip_forward`; `nft list ruleset`; ruta de `srv-lan` |
| `radtest` sin respuesta | Secreto o IP del NAS no coinciden con `clients.conf` | `freeradius -X` y revisa el cliente |
| Suricata arranca pero no alerta | Interfaz o `HOME_NET` incorrectos; reglas no cargadas | `suricata -T`; revisa `af-packet`; `suricata-update` |
| Muchas alertas irrelevantes | Reglas genéricas | Ajusta `HOME_NET`; desactiva reglas concretas en `suricata-update` |
| `tcpdump` no captura | Interfaz equivocada o falta `sudo` | `tcpdump -D`; `sudo` |
| `ssh` con certificado no entra | Principal distinto del usuario o certificado caducado | `ssh-keygen -L -f …-cert.pub`; `journalctl -u ssh` |

## Buenas prácticas de seguridad aplicadas

- Laboratorio **aislado**; nada de capturas ni pruebas en redes ajenas.
- Entradas ARP estáticas solo para elementos críticos; la solución real es DAI en el switch.
- Reglas `forward` con política de **denegación por defecto** y registro limitado.
- VPN con **mínimo privilegio** (`AllowedIPs` y reglas por puerto) y revocación comprobada.
- Claves privadas con permisos `600`; la CA SSH, fuera de línea o muy protegida.
- RADIUS accesible solo desde la red de gestión; secretos largos y distintos por cliente.
- IDS en modo alerta antes de pasar a IPS; revisión periódica de falsos positivos.
- Evidencias sin contraseñas ni claves privadas.

## Preguntas de autoevaluación

1. ¿Qué es una DMZ y en qué se diferencia de una VLAN de empleados?
2. ¿Qué diferencia hay entre una VLAN y una subred? ¿Pueden coincidir?
3. ¿Qué controla 802.1X y qué papel tiene RADIUS en él?
4. ¿Por qué WEP y TKIP son inseguros? ¿Qué aporta SAE en WPA3?
5. ¿Qué diferencia hay entre una VPN de acceso remoto y una sitio a sitio?
6. ¿Qué función tiene `AllowedIPs` en WireGuard?
7. ¿Qué es una política de denegación por defecto y por qué se prefiere?
8. ¿Qué diferencia hay entre un IDS y un IPS, entre un NIDS y un HIDS?
9. ¿Qué puede revelar una captura de HTTP que HTTPS bien configurado no muestra?
10. ¿Cómo se detecta un cambio sospechoso en la caché ARP y cómo se previene en un switch?
11. ¿Cuándo es útil un túnel SSH `-L`? ¿Qué riesgo supone `-R`?
12. ¿Qué ventajas tienen los certificados SSH frente a las claves en `authorized_keys`?
13. ¿Qué principios aplica Zero Trust?

## Resumen

Has visto cómo se **comporta** la red cuando todo va bien (ARP, DHCP, TLS) y cómo se **nota** cuando algo va mal; has segmentado con VLAN y ACL, cifrado el acceso remoto con WireGuard, centralizado la autenticación con RADIUS y detectado tráfico sospechoso con Suricata. La constante: **comprobar cada medida con tráfico real** y documentarlo.

## Referencias y documentación oficial

- WireGuard: <https://www.wireguard.com/quickstart/>
- strongSwan: <https://docs.strongswan.org>
- FreeRADIUS: <https://www.freeradius.org/documentation/>
- Suricata: <https://docs.suricata.io>
- tcpdump / pcap-filter: <https://www.tcpdump.org/manpages/>
- Wireshark: <https://www.wireshark.org/docs/>
- OpenSSH `ssh-keygen(1)`: <https://man.openbsd.org/ssh-keygen>
- nftables wiki: <https://wiki.nftables.org>
- INCIBE: <https://www.incibe.es>
