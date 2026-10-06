---
title: "Prácticas"
slug: "practicas"
weight: 2
---

# UD6. Prácticas: seguridad en redes

> Observación y detección de amenazas de capa 2/3, VLAN y ACL con Linux, protocolos seguros frente a protocolos en claro, SSH avanzado, VPN con WireGuard, autenticación RADIUS, detección con Suricata y análisis de tráfico.

| Datos de las prácticas | Información |
| --- | --- |
| Módulo | 0378. Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR |
| Duración estimada | 10 horas |
| Entorno | VirtualBox 7: red `SAD-NAT` (192.168.100.0/24) y redes internas `sad-lan` y `sad-trunk` |
| Sistemas | Debian 13 (AlmaLinux 10 donde se indica) |
| Teoría asociada | [Teoría de la UD6](../teoria/) |

---

## 1. Objetivos

- Observar el funcionamiento normal de ARP y DHCP y detectar anomalías con herramientas defensivas.
- Segmentar con VLAN 802.1Q en Linux y aplicar ACL entre segmentos con nftables.
- Demostrar la diferencia entre protocolos en claro y cifrados con capturas de tráfico propias.
- Usar túneles SSH, un bastión (`ProxyJump`) y certificados SSH.
- Implantar una VPN de acceso remoto con WireGuard y verificarla.
- Instalar FreeRADIUS y comprobar autenticaciones correctas e incorrectas.
- Desplegar Suricata con reglas propias y comprobar sus alertas.
- Capturar y analizar tráfico con tcpdump y Wireshark.

> [!IMPORTANT]
> **Alcance ético y legal.** Estas prácticas se realizan **solo** en tu laboratorio virtual aislado. No se incluyen ni se piden herramientas de ataque: se **observan** los protocolos, se **simulan los efectos** de forma local y se practica la **detección y la mitigación**. Nunca captures ni analices tráfico de redes que no sean tuyas (secreto de las comunicaciones; arts. 197 y 197 bis del Código Penal).

---

## 2. Preparación del laboratorio

### 2.1. Topología

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

### 2.2. Preparación común

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

## 3. Práctica 1 · Observar ARP y DHCP, y detectar anomalías

**Objetivo:** entender qué hay que vigilar para detectar ARP spoofing y DHCP falso, **sin atacar a nadie**.

### 3.1. ARP en funcionamiento normal

En `sad-cli`:

```bash
ip neigh flush all                                   # vacía la caché ARP (se rehará sola)
sudo tcpdump -n -e -i enp0s3 arp -c 4 &              # observa el ARP (con las direcciones MAC)
ping -c 1 192.168.100.30
wait
ip neigh show | tee ~/ud6-evidencias/01-arp-normal.txt
```

Esperado: una petición `Request who-has 192.168.100.30 tell 192.168.100.10` y la respuesta `Reply 192.168.100.30 is-at <MAC>`. Anota la MAC de `sad-web` (y comprueba con `ip link show enp0s3` en `sad-web` que coincide).

### 3.2. Simular **el efecto** de una caché ARP envenenada (solo en tu VM)

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

### 3.3. Detección continua con arpwatch (en `sad-web`)

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

### 3.4. DHCP: observar el intercambio y localizar servidores

En `sad-cli` (con `dhclient` o `NetworkManager`), observa un intercambio DHCP **sin cambiar la configuración**:

```bash
sudo tcpdump -n -i enp0s3 'udp port 67 or udp port 68' -c 8 &
sudo nmap --script broadcast-dhcp-discover -e enp0s3        # pregunta quién ofrece DHCP en TU red de laboratorio
wait
```

Anota **qué servidores DHCP responden**. En una red real, si aparece más de uno donde solo debería haber uno, es un indicio de DHCP no autorizado.

**Entrega:** tabla con las amenazas de capa 2/3 vistas, cómo se detecta cada una en tu laboratorio y qué función de switch la mitiga (port security, DHCP snooping, DAI).

---

## 4. Práctica 2 · VLAN y ACL entre segmentos

**Objetivo:** segmentar con VLAN 802.1Q y permitir solo los flujos necesarios (RA3 a).

Escenario: `gw-vpn` hace de router entre dos VLAN sobre la red interna `sad-trunk`:

| VLAN | Red | Equipo |
| --- | --- | --- |
| 20 (empleados) | 10.10.20.0/24 | `sad-cli` (10.10.20.10), puerta de enlace 10.10.20.1 |
| 40 (servidores) | 10.10.40.0/24 | `srv-lan` (10.10.40.10), puerta de enlace 10.10.40.1 |

> [!NOTE]
> Las interfaces de la red `sad-trunk` pueden llamarse `enp0s9`, `enp0s10`… según la VM. Comprueba con `ip -br a` el nombre real y sustitúyelo en los comandos (`IFACE`).

### 4.1. Subinterfaces VLAN

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

### 4.2. Comprobación del aislamiento y del etiquetado

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

### 4.3. ACL entre VLAN con nftables

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

**Entrega:** tabla de flujos (origen → destino → servicio → permitido/denegado) con la evidencia de cada prueba y el volcado de `nft list ruleset`.

<!-- hint:h4 -->
> [!TIP]
> Comprueba la sintaxis **antes** de cargar (`sudo nft -c -f …`) y haz la prueba con una red de seguridad. Después valida las dos direcciones: lo permitido **funciona** y lo prohibido **falla** (pruebas positivas y negativas). Los contadores (`counter`) te dicen qué regla actuó.

---

## 5. Práctica 3 · Protocolos seguros y SSH avanzado

### 5.1. Lo que ve la red: protocolo en claro frente a cifrado

Sigue el apartado 6.1 de la [teoría](../teoria/#61-comprobar-con-tus-propios-ojos-qué-se-ve-en-la-red): instala la zona con autenticación básica en `sad-web`, captura tu propia petición con `tcpdump` y decodifica la cabecera `Authorization`.

Entrega: captura de pantalla de la cabecera, el resultado de `base64 -d` y una explicación de por qué es inseguro. Después repite la petición con **HTTPS** (certificado de la UD3, práctica 6) y comprueba que ya no se ve el contenido:

```bash
sudo tcpdump -n -A -i enp0s3 'tcp port 443 and host 192.168.100.10' -c 20 | tee ~/ud6-evidencias/03-https.txt
```

### 5.2. Túnel SSH hacia la intranet

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

### 5.3. Bastión con `ProxyJump`

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

### 5.4. Certificados SSH

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

## 6. Práctica 4 · VPN de acceso remoto con WireGuard

**Objetivo:** que `sad-cli` (fuera de la sede) acceda por un túnel cifrado al servidor interno `srv-lan` y **solo** a lo permitido (RA3 d, e).

### 6.1. Instalación y claves

En `gw-vpn` y `sad-cli`:

```bash
sudo apt install -y wireguard wireguard-tools                  # AlmaLinux: sudo dnf install -y wireguard-tools
umask 077
wg genkey | sudo tee /etc/wireguard/privada.key | wg pubkey | sudo tee /etc/wireguard/publica.key
sudo cat /etc/wireguard/publica.key                            # anota la pública de cada máquina
```

### 6.2. Configuración

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

### 6.3. Comprobaciones

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

## 7. Práctica 5 · Autenticación centralizada con FreeRADIUS

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

## 8. Práctica 6 · Detección de intrusiones con Suricata

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

## 9. Práctica 7 · Captura y análisis de tráfico

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

## 10. Práctica 8 · VPN sitio a sitio con IPsec (opcional)

Requiere dos pasarelas (`gw-sede` y `gw-oficina`, cada una con una LAN interna). Sigue el apartado 8.4 de la [teoría](../teoria/) con **strongSwan**:

1. Instala `strongswan-swanctl` y `charon-systemd` en ambas.
2. Crea `/etc/swanctl/conf.d/sede-oficina.conf` en cada extremo (invirtiendo los valores `local_*` y `remote_*`), con propuestas modernas (`aes256gcm16-prfsha384-ecp384`).
3. Carga y comprueba: `sudo swanctl --load-all`, `sudo swanctl --list-sas` (IKE_SA y CHILD_SA en estado `ESTABLISHED/INSTALLED`) y `ping` entre equipos de las dos LAN.
4. **Prueba de fallo:** detén `strongswan` en un extremo y comprueba la pérdida de conectividad; arráncalo de nuevo y mide el tiempo de recuperación. Captura con `tcpdump` y verifica que solo se ven paquetes ESP/UDP 4500 cifrados.
5. **Mejora:** sustituye la clave precompartida por **certificados** firmados por la CA de la UD3 y justifica por qué es más seguro.

---

## 11. Problemas habituales

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

---

## 12. Buenas prácticas de seguridad aplicadas

- Laboratorio **aislado**; nada de capturas ni pruebas en redes ajenas.
- Entradas ARP estáticas solo para elementos críticos; la solución real es DAI en el switch.
- Reglas `forward` con política de **denegación por defecto** y registro limitado.
- VPN con **mínimo privilegio** (`AllowedIPs` y reglas por puerto) y revocación comprobada.
- Claves privadas con permisos `600`; la CA SSH, fuera de línea o muy protegida.
- RADIUS accesible solo desde la red de gestión; secretos largos y distintos por cliente.
- IDS en modo alerta antes de pasar a IPS; revisión periódica de falsos positivos.
- Evidencias sin contraseñas ni claves privadas.

---

## 13. Autoevaluación

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

---

## 14. Tarea evaluable: diseño y validación de una red segura

Para una empresa de 50 usuarios con una sede secundaria, teletrabajo, un servicio web publicado y Wi-Fi para invitados (ver supuesto de la teoría), entrega una memoria (PDF o Markdown) con:

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

## 15. Resumen

Has visto cómo se **comporta** la red cuando todo va bien (ARP, DHCP, TLS) y cómo se **nota** cuando algo va mal; has segmentado con VLAN y ACL, cifrado el acceso remoto con WireGuard, centralizado la autenticación con RADIUS y detectado tráfico sospechoso con Suricata. La constante: **comprobar cada medida con tráfico real** y documentarlo.

---

## 16. Referencias

- WireGuard: <https://www.wireguard.com/quickstart/>
- strongSwan: <https://docs.strongswan.org>
- FreeRADIUS: <https://www.freeradius.org/documentation/>
- Suricata: <https://docs.suricata.io>
- tcpdump / pcap-filter: <https://www.tcpdump.org/manpages/>
- Wireshark: <https://www.wireshark.org/docs/>
- OpenSSH `ssh-keygen(1)`: <https://man.openbsd.org/ssh-keygen>
- nftables wiki: <https://wiki.nftables.org>
- INCIBE: <https://www.incibe.es>
