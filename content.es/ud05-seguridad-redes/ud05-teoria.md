---
title: "Seguridad en redes: monitorización, detección y respuesta - Teoría"
weight: 1
bookToc: true
---

# UD5 · Seguridad en redes: monitorización, detección y respuesta

Cómo proteger la red interna y vigilarla: amenazas por capas, protección de la LAN, segmentación con VLAN y ACL, seguridad Wi-Fi, protocolos seguros, detección de intrusiones y análisis de tráfico.

{{< ra "RA2:a,c,d,g,h,i" "RA3:c" >}}

> [!NOTE]
> SSH avanzado, redes privadas virtuales (VPN) y autenticación AAA/RADIUS se estudian en la [UD6. Seguridad perimetral](/ud06-seguridad-perimetral/ud06-teoria/).

| Bloque | Horas |
|---|--:|
| Teoría (este documento) | 7 h |
| [Prácticas](/ud05-seguridad-redes/ud05-practicas/) | 9 h |
| Evaluación | 2 h |
| **Total** | **18 h** |

## 1. Introducción

Una empresa tiene un servidor muy bien fortificado (UD4), pero está conectado a una red donde cualquiera con un cable puede escuchar el tráfico, donde los portátiles de los visitantes comparten segmento con la contabilidad y donde los empleados en teletrabajo acceden por Internet con una contraseña. **La seguridad de un host no basta si la red que lo une al resto es insegura.**

Esta unidad se ocupa de la **seguridad en la red**: qué puede ir mal en cada capa, cómo **segmentar** y **controlar** el acceso, cómo **cifrar** las comunicaciones y cómo **detectar** lo que no se ha podido prevenir.

> [!NOTE]
> **Contexto ético y legal.** Para proteger una red hay que entender cómo se ataca. En esta unidad cada ataque se estudia como **amenaza que hay que detectar y mitigar**, con el ciclo amenaza → vulnerabilidad → ataque → detección → mitigación → comprobación, siempre en un **laboratorio aislado** y propio. No se aplican estas técnicas contra redes ajenas: es delito (Código Penal, arts. 197 bis y 264 ss.).

## 2. Objetivos

- Clasificar las amenazas de red por capas y explicar cómo funcionan a nivel conceptual.
- Aplicar medidas de protección de la LAN: segmentación, *port security*, *DHCP snooping*, ARP dinámico, 802.1X.
- Configurar VLAN y reglas de filtrado entre segmentos (Linux).
- Evaluar la seguridad de los protocolos Wi-Fi y de los protocolos de red más habituales.
- Usar SSH avanzado: túneles, bastión (`ProxyJump`) y certificados SSH.
- Implantar una **VPN de acceso remoto** (WireGuard) y conocer la **VPN sitio a sitio** (IPsec/IKEv2).
- Integrar un servidor de autenticación **RADIUS** (FreeRADIUS).
- Describir los tipos de IDS/IPS y configurar **Suricata** con reglas propias.
- Capturar y analizar tráfico con **tcpdump** y **Wireshark**.

---

## 3. Amenazas de red por capas

El modelo OSI sirve para ordenar las amenazas: cada capa tiene sus propios puntos débiles. Una medida en la capa 7 no protege de un ataque en la capa 2.

| Capa | Protocolo típico | Amenaza | Idea del ataque | Medida principal |
| --- | --- | --- | --- | --- |
| 1 Física | Cable, Wi-Fi | Acceso físico, interferencias | Conectarse a una roca de red libre | Control físico, apagar puertos sin uso |
| 2 Enlace | Ethernet, ARP, VLAN | **ARP spoofing**, **MAC flooding**, VLAN hopping, STP falso | Falsear identidades de capa 2 | *Port security*, DAI, BPDU guard |
| 3 Red | IP, ICMP, DHCP | **DHCP falso**, IP spoofing, redirecciones ICMP | Dar una configuración de red maliciosa | DHCP snooping, filtrado *anti-spoofing* |
| 4 Transporte | TCP, UDP | **SYN flood**, escaneo de puertos | Agotar recursos o descubrir servicios | SYN cookies, cortafuegos, IDS |
| 7 Aplicación | HTTP, DNS, SMTP | Inyección, *envenenamiento* de DNS, fuerza bruta | Explotar el protocolo o la aplicación | Cifrado, WAF, DNSSEC, autenticación robusta |

### 3.1. Escucha de tráfico (*sniffing*) y hombre en el medio (MITM)

- **Sniffing**: capturar tráfico que pasa por la red. Es trivial si el medio es compartido (Wi-Fi abierto) o si el atacante consigue redirigir el tráfico. Todo protocolo **sin cifrar** (HTTP, FTP, Telnet, SNMPv1/2c, POP3/IMAP sin TLS) expone contraseñas y datos.
- **MITM** (*Man In The Middle*): el atacante se interpone entre dos partes y lee o modifica el tráfico sin que lo noten. Puede lograrse falseando ARP, DHCP, DNS o con un punto de acceso Wi-Fi falso.

**Defensa de fondo:** el cifrado extremo a extremo con **autenticación del servidor** (TLS con certificados válidos, SSH con huellas verificadas, VPN). Aunque alguien se interponga, no puede leer ni modificar sin ser detectado.

<!-- enr:u6a -->
> [!WARNING]
> **Solo en tu laboratorio.** Las técnicas de esta sección (ARP spoofing, DHCP falso, MAC flooding) son ataques reales que están penados en una red ajena. Aquí se estudian para aprender a **detectarlos y prevenirlos**; en las prácticas solo se simula el *efecto* sobre tu propia máquina virtual.

### 3.2. ARP spoofing (envenenamiento ARP)

**ARP** (*Address Resolution Protocol*) traduce una IP en la MAC de la tarjeta de red de ese equipo dentro de la misma LAN. Funciona así:

```mermaid
sequenceDiagram
  participant A as PC-A 192.168.100.10
  participant S as Switch (difunde)
  participant G as Router 192.168.100.1
  A->>S: ARP request: ¿Quién tiene 192.168.100.1?
  S->>G: (difusión a todos)
  G->>A: ARP reply: 192.168.100.1 está en MAC aa:bb:cc:00:00:01
  Note over A: Guarda IP→MAC en su caché ARP
```

**La vulnerabilidad:** ARP **no tiene autenticación**. Un equipo malicioso de la LAN puede enviar respuestas ARP falsas diciendo «la IP del router soy yo»; las víctimas actualizan su caché y le envían el tráfico a él. Es la base de muchos MITM en LAN.

**Cómo se detecta** (en tu laboratorio, sin atacar a nadie):

```bash
ip neigh show                          # caché ARP/vecinos actual: IP, MAC, estado
ip neigh show | awk '{print $5}' | sort | uniq -d    # MAC repetidas para IP distintas: indicio sospechoso
sudo tcpdump -n -e -i enp0s3 arp       # observa el tráfico ARP: -e muestra las MAC
```

Señales de ARP spoofing: la **MAC del router cambia** en la caché; **dos IP diferentes con la misma MAC**; avalancha de respuestas ARP que nadie ha solicitado (*gratuitous ARP*). Herramientas de detección: **arpwatch** (avisa de cambios de pareja IP-MAC) y los IDS (Suricata).

```bash
sudo apt install -y arpwatch                          # Debian
sudo systemctl enable --now arpwatch                  # registra pares IP/MAC y alerta de cambios
sudo journalctl -u arpwatch --since "10 min ago"
```

**Cómo se mitiga:**

| Medida | Dónde | Efecto |
| --- | --- | --- |
| **DAI** (*Dynamic ARP Inspection*) | Switch gestionable | Descarta ARP que no coinciden con la tabla de DHCP snooping |
| *Port security* | Switch | Limita las MAC por puerto |
| Entradas ARP estáticas para el router en servidores críticos | Host | `sudo ip neigh replace 192.168.100.1 lladdr aa:bb:cc:00:00:01 dev enp0s3 nud permanent` |
| Segmentación (VLAN pequeñas) | Red | Reduce el alcance de un atacante |
| Cifrado de extremo a extremo | Aplicación | Aunque desvíen el tráfico, no lo pueden leer |

### 3.3. MAC flooding

Un switch aprende qué MAC hay en cada puerto en su **tabla CAM** (de tamaño finito). Un equipo que envíe miles de tramas con MAC falsas puede **llenar la tabla**; el switch, desbordado, pasa a **difundir por todos los puertos** (*fail-open*), y cualquier equipo puede escuchar tráfico ajeno.

**Mitigación:** *port security* (máximo de MAC por puerto) y alarma o apagado del puerto si se excede.

### 3.4. DHCP falso (*rogue DHCP*)

**DHCP** asigna IP, puerta de enlace y DNS automáticamente. Cualquier equipo que responda primero «gana»: un servidor DHCP falso puede entregar **una puerta de enlace o un DNS maliciosos** y redirigir a las víctimas. Por la misma razón, un router doméstico enchufado por error a la LAN corporativa causa caídas.

```bash
sudo tcpdump -n -i enp0s3 'udp port 67 or udp port 68'   # observa DISCOVER/OFFER/REQUEST/ACK
sudo nmap --script broadcast-dhcp-discover -e enp0s3     # (en LAB propio) lista qué servidores DHCP responden
```

**Mitigación:** **DHCP snooping** en el switch: solo se aceptan ofertas DHCP desde puertos «de confianza» (*trusted*) donde está el servidor legítimo.

### 3.5. VLAN hopping

Las VLAN separan redes lógicas. En **VLAN hopping** el atacante consigue acceso a otra VLAN: negociando un *trunk* (DTP) o enviando tramas con doble etiqueta 802.1Q. **Medidas:** deshabilitar la negociación de *trunk*, configurar los puertos de acceso como `access` fijo, no usar la VLAN 1 ni la VLAN nativa para datos, y apagar los puertos sin uso en una VLAN «agujero negro».

### 3.6. Denegación de servicio (DoS/DDoS)

El objetivo es **agotar** un recurso (ancho de banda, tabla de conexiones, CPU). Un ejemplo clásico es el **SYN flood**: inundar un servidor de peticiones TCP SYN sin completar el *handshake*, para saturar su cola de conexiones.

**Medidas en el host (ya vistas en UD4):**

```bash
sysctl net.ipv4.tcp_syncookies              # 1 = activo: mantiene el servicio ante SYN flood
sudo ss -s                                  # resumen de conexiones (muchas en SYN-RECV = sospechoso)
```

y limitación de tasa en el cortafuegos (UD7), CDN/anti-DDoS del proveedor, y balanceo/escalado (UD5).

---

## 4. Protección de la LAN

### 4.1. Medidas en conmutadores gestionables

| Medida | Qué hace | Amenaza que frena |
| --- | --- | --- |
| **Port security** | Limita MAC por puerto y reacciona (avisa, bloquea) | MAC flooding, equipos no autorizados |
| **DHCP snooping** | Marca puertos *trusted* para ofertas DHCP y construye una tabla IP-MAC-puerto | DHCP falso |
| **DAI** | Valida ARP contra la tabla de snooping | ARP spoofing |
| **IP Source Guard** | Descarta IP de origen falseadas | IP spoofing |
| **BPDU Guard / Root Guard** | Impide que un puerto de acceso altere el árbol de STP | STP falso |
| **Apagar puertos sin uso** | Quita puntos de entrada | Acceso físico |
| **802.1X** | Autentica el equipo/usuario antes de dar acceso al puerto | Equipos no autorizados |

Ejemplo de **sintaxis típica de un switch Cisco** (es solo ilustrativo; otras marcas usan comandos equivalentes):

```text
! Port security en un puerto de acceso
interface GigabitEthernet0/5
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 spanning-tree portfast
 spanning-tree bpduguard enable
!
! DHCP snooping y DAI para la VLAN 10
ip dhcp snooping
ip dhcp snooping vlan 10
ip arp inspection vlan 10
interface GigabitEthernet0/1
 description Enlace al servidor DHCP / router
 ip dhcp snooping trust
 ip arp inspection trust
```

En un laboratorio con máquinas virtuales no hay switch gestionable, pero un **puente Linux** (`bridge`) con filtrado permite reproducir parte de estas medidas (ver prácticas).

<!-- enr:u6b -->
![Segmentación con VLAN y ACL](/images/ud05/segmentacion-vlan.svg)
*Figura 6.1. Dos VLAN separadas por el router: todo el tráfico entre ellas pasa por el cortafuegos y puede filtrarse.*

> [!NOTE]
> Las VLAN **segmentan**, pero por sí solas **no protegen**: si el router permite todo entre VLAN, no se ha ganado nada. La seguridad la dan las ACL aplicadas en el punto de unión.

### 4.2. Segmentación con VLAN

Una **VLAN** (*Virtual LAN*, IEEE 802.1Q) divide un switch físico en redes lógicas aisladas. Cada trama lleva una **etiqueta** con el identificador de la VLAN (1-4094). Entre switches o hacia un router se usa un puerto **trunk** que transporta varias VLAN.

```mermaid
flowchart TB
  R[Router / cortafuegos<br/>routing entre VLAN + ACL]
  SW[Switch gestionable<br/>trunk 802.1Q]
  R --- SW
  SW --- A[VLAN 10 Administración<br/>10.10.10.0/24]
  SW --- B[VLAN 20 Empleados<br/>10.10.20.0/24]
  SW --- C[VLAN 30 Invitados Wi-Fi<br/>10.10.30.0/24]
  SW --- D[VLAN 40 Servidores<br/>10.10.40.0/24]
```

Beneficios: **limita el alcance** de un atacante, reduce el tráfico de difusión y permite aplicar **políticas distintas** a cada grupo (los invitados solo salen a Internet; los empleados no acceden a la administración).

**VLAN en Linux** (paquete `vlan` no es necesario con el kernel actual; `iproute2` basta):

```bash
sudo ip link add link enp0s3 name enp0s3.10 type vlan id 10     # subinterfaz VLAN 10 sobre enp0s3
sudo ip addr add 10.10.10.1/24 dev enp0s3.10
sudo ip link set enp0s3.10 up
ip -d link show enp0s3.10                                       # muestra "vlan protocol 802.1Q id 10"
```

Persistente con **systemd-networkd** (`/etc/systemd/network/`):

```ini
# 10-vlan10.netdev
[NetDev]
Name=enp0s3.10
Kind=vlan

[VLAN]
Id=10
```

```ini
# 20-vlan10.network
[Match]
Name=enp0s3.10

[Network]
Address=10.10.10.1/24
```

(Y en la interfaz física, `VLAN=enp0s3.10` en su `.network`.) Para eliminarla: `sudo ip link del enp0s3.10`.

### 4.3. ACL: controlar qué se comunica con qué

Una **ACL** (*Access Control List*) es una lista ordenada de reglas permitir/denegar. Entre VLAN, el router aplica ACL; en Linux se hace con **nftables** (que verás a fondo en la UD7). Ejemplo: un router Linux que une VLAN 20 (empleados), 30 (invitados) y 40 (servidores):

```text
# /etc/nftables.d/vlans.nft  (el cortafuegos del router)
table inet vlans {
  chain forward {
    type filter hook forward priority 0; policy drop;       # por defecto, nada pasa

    ct state established,related accept

    iifname "enp0s3.20" oifname "enp0s3.40" tcp dport { 80, 443, 445 } accept   # empleados → servidores
    iifname "enp0s3.30" oifname "enp0s9"    accept                              # invitados → solo Internet (WAN)
    iifname "enp0s3.10" accept                                                  # administración → todo
    log prefix "VLAN-drop: " limit rate 5/minute
  }
}
```

```bash
sudo nft -c -f /etc/nftables.d/vlans.nft       # comprobar sintaxis
sudo nft -f /etc/nftables.d/vlans.nft          # aplicar
sudo sysctl -w net.ipv4.ip_forward=1           # el router debe reenviar paquetes
```

### 4.4. Zero Trust

El modelo clásico («perímetro»: dentro de la red de confianza, fuera no) falla cuando un atacante ya está dentro o cuando hay teletrabajo y nube. **Zero Trust** («nunca confíes, verifica siempre») propone: autenticar y autorizar **cada petición**, mínimo privilegio, microsegmentación y monitorización continua. Las VLAN, ACL, 802.1X, VPN con MFA y registros de esta unidad son sus piezas.

### 4.5. 802.1X: control de acceso a la red

**IEEE 802.1X** autentica un dispositivo **antes** de darle conectividad. Tres roles:

```mermaid
flowchart LR
  S[Suplicante<br/>portátil] -- EAP sobre LAN --> A[Autenticador<br/>switch / punto de acceso]
  A -- RADIUS --> R[Servidor de autenticación<br/>FreeRADIUS]
  R -.->|Acceso concedido: VLAN 20| A
```

El suplicante envía credenciales (usuario/contraseña, certificado) con **EAP**; el autenticador las reenvía por **RADIUS** al servidor, que decide y puede indicar en qué **VLAN** colocar al equipo. Es la base de la **autenticación de puertos** y de **WPA2/WPA3-Enterprise** (apartado 5).

---

## 5. Seguridad Wi-Fi

Una red inalámbrica no tiene «cable»: **cualquiera en el alcance** puede captar las señales. Por eso el cifrado y la autenticación son críticos.

### 5.1. Evolución de los protocolos

| Protocolo | Estado | Observaciones |
| --- | --- | --- |
| **WEP** | **Roto** (obsoleto desde 2004) | Nunca se debe usar |
| **WPA** (TKIP) | **Obsoleto** | No usar |
| **WPA2-Personal** (PSK, AES-CCMP) | Aceptable con clave robusta | Vulnerable a ataques de diccionario *offline* si la clave es débil |
| **WPA2-Enterprise** (802.1X) | Seguro si se valida el certificado del servidor | Credenciales individuales |
| **WPA3-Personal** (SAE) | **Recomendado** | Sustituye el PSK por SAE (*Dragonfly*): resiste el diccionario *offline* y da secreto hacia delante |
| **WPA3-Enterprise** | **Recomendado** en empresa | Suites de 192 bits opcionales, PMF obligatorio |
| **OWE** (*Enhanced Open*) | Para redes abiertas | Cifra el tráfico entre cliente y AP sin contraseña |

**Elementos clave:**

- **PMF** (*Protected Management Frames*, 802.11w): protege las tramas de gestión (impide expulsar clientes con falsas desautenticaciones). Obligatorio en WPA3.
- **WPS**: método de emparejamiento por PIN con debilidades conocidas: **desactívalo**.
- **SSID oculto**: no es una medida de seguridad (el SSID se descubre al conectarse un cliente).
- **Aislamiento de clientes** (*client isolation*) en redes de invitados: los clientes no se ven entre sí.

### 5.2. Buenas prácticas de diseño Wi-Fi

- Redes separadas por VLAN: **corporativa** (WPA3-Enterprise), **invitados** (aislada, solo Internet) e **IoT**.
- Clave Wi-Fi larga (frase de 16+ caracteres) si usas PSK; cámbiala cuando se marche personal.
- Actualiza el *firmware* del punto de acceso y desactiva la administración desde la Wi-Fi.
- Servidor RADIUS con certificado válido y clientes configurados para **validar** ese certificado (si no, un AP falso puede robar credenciales).

### 5.3. Revisar tu propia Wi-Fi

Comprueba qué seguridad anuncia **tu** red (en tu portátil Linux):

```bash
nmcli -f SSID,SECURITY,SIGNAL dev wifi list       # redes visibles y su seguridad (WPA2, WPA3, ...)
nmcli -f 802-11-wireless-security connection show "MiWiFi"    # parámetros de tu conexión guardada
iw dev wlp2s0 link                                # frecuencia, señal, bitrate de la conexión actual
```

Ejemplo de configuración de un AP **WPA3-Personal** con `hostapd` (laboratorio con adaptador compatible):

```text
# /etc/hostapd/lab-wpa3.conf
interface=wlan0
ssid=LAB-SAD
hw_mode=g
channel=6
ieee80211w=2                 # PMF obligatorio
wpa=2
wpa_key_mgmt=SAE             # WPA3-Personal
sae_password=FraseLargaDeLaboratorio2026
rsn_pairwise=CCMP
sae_pwe=2
```

---

## 6. Protocolos seguros

Cada protocolo antiguo tiene un sustituto cifrado. Usar el inseguro es dejar los datos «en una postal».

| Función | Inseguro | Seguro | Puerto |
| --- | --- | --- | --- |
| Acceso remoto a consola | Telnet (23), rlogin | **SSH** | 22 |
| Web | HTTP | **HTTPS** (TLS 1.2/1.3) | 443 |
| Transferencia de ficheros | FTP (21) | **SFTP** (sobre SSH), FTPS | 22 |
| Correo | POP3 (110), IMAP (143), SMTP (25) | POP3S 995, IMAPS 993, SMTP+STARTTLS/SMTPS | 993, 995, 587 |
| Resolución de nombres | DNS (53) | **DoT** (853), **DoH** (443); DNSSEC para integridad | 853 |
| Monitorización | SNMP v1/v2c | **SNMPv3** (autenticación y cifrado) | 161 |
| Directorio | LDAP (389) | **LDAPS** (636) / LDAP+StartTLS | 636 |
| Escritorio remoto | VNC sin cifrar | RDP con NLA, VNC sobre SSH/VPN | 3389 |
| Registros | Syslog UDP | Syslog sobre TLS | 6514 |

### 6.1. Comprobar con tus propios ojos qué se ve en la red

Para entender **por qué** importa el cifrado, observa tu propio tráfico en el laboratorio. En `sad-web` instala un servidor web con una carpeta protegida con autenticación básica HTTP y captura tu propia petición:

```bash
sudo apt install -y apache2 apache2-utils tcpdump
sudo htpasswd -bc /etc/apache2/.htpasswd demo ClaveDemo1       # usuario demo / clave de laboratorio
sudo mkdir -p /var/www/html/privado && echo "zona privada" | sudo tee /var/www/html/privado/index.html
sudo tee /etc/apache2/conf-available/privado.conf >/dev/null <<'EOF'
<Directory /var/www/html/privado>
    AuthType Basic
    AuthName "Zona privada"
    AuthUserFile /etc/apache2/.htpasswd
    Require valid-user
</Directory>
EOF
sudo a2enconf privado && sudo apache2ctl configtest && sudo systemctl reload apache2
```

En una terminal de `sad-web`, captura en la interfaz de la red:

```bash
sudo tcpdump -n -A -i enp0s3 'tcp port 80 and host 192.168.100.10' | grep -i authorization
```

Desde `sad-cli`, haz la petición:

```bash
curl -u demo:ClaveDemo1 http://192.168.100.30/privado/
```

Verás `Authorization: Basic ZGVtbzpDbGF2ZURlbW8x`. Eso es solo **Base64** (no cifrado): `echo ZGVtbzpDbGF2ZURlbW8x | base64 -d` devuelve `demo:ClaveDemo1`. **Cualquiera con acceso al medio la lee.** Repite con HTTPS (UD3, práctica 6): la cabecera ya no es legible. Ese es el valor del cifrado en tránsito.

---

## 7. Detección de intrusiones: IDS e IPS

### 7.1. Conceptos

Un **IDS** (*Intrusion Detection System*) **observa** el tráfico o el sistema y **alerta** de actividad sospechosa. Un **IPS** (*Intrusion Prevention System*) además **bloquea** lo que detecta, porque está «en línea» (por donde pasa el tráfico).

| Criterio | Tipos |
| --- | --- |
| **Ubicación** | **NIDS** (en la red, analiza tráfico: Suricata, Snort, Zeek) · **HIDS** (en el equipo, analiza ficheros, registros y procesos: Wazuh, OSSEC, AIDE) |
| **Método de detección** | **Por firmas** (compara con patrones conocidos: fiable pero no ve lo nuevo) · **Por anomalías** (detecta desviaciones de lo normal: puede detectar lo nuevo, pero genera más falsos positivos) · **Híbrido** |
| **Reacción** | **Pasivo** (IDS: solo alerta, copia del tráfico desde un puerto espejo o *tap*) · **Activo** (IPS: bloquea, en línea) |

| Resultado | Significado |
| --- | --- |
| **Verdadero positivo** | Alerta de un ataque real |
| **Falso positivo** | Alerta de algo legítimo (genera cansancio de alertas) |
| **Falso negativo** | Ataque real **no detectado** (el más peligroso) |
| **Verdadero negativo** | Tráfico normal sin alerta |

<!-- enr:u6d -->
> [!TIP]
> Un IDS genera **falsos positivos**. Antes de pasar a modo IPS (que bloquea), ejecuta Suricata en modo *detección* varios días, ajusta las reglas ruidosas y valora el impacto de bloquear algo legítimo.

### 7.2. Suricata

**Suricata** es un motor libre de **NIDS/IPS** y monitorización de seguridad de red (OISF). Analiza el tráfico en tiempo real, decodifica protocolos (HTTP, DNS, TLS, SMB…), aplica **reglas** y genera registros estructurados (`eve.json`).

```bash
sudo apt install -y suricata jq                        # AlmaLinux: sudo dnf install -y epel-release && sudo dnf install -y suricata jq
suricata --build-info | head -3                        # versión
```

Configuración principal: `/etc/suricata/suricata.yaml`. Lo mínimo para empezar:

```bash
sudo cp /etc/suricata/suricata.yaml /etc/suricata/suricata.yaml.bak
ip -br a                                               # identifica tu interfaz (p. ej. enp0s3)
sudo nano /etc/suricata/suricata.yaml
```

Comprueba estos valores:

```yaml
vars:
  address-groups:
    HOME_NET: "[192.168.100.0/24]"      # tu red interna
af-packet:
  - interface: enp0s3                   # interfaz en la que escucha (la de tu laboratorio)
```

**Reglas.** El conjunto de reglas libre **Emerging Threats Open** se actualiza con `suricata-update`:

```bash
sudo suricata-update                                   # descarga y compila las reglas en /var/lib/suricata/rules/suricata.rules
sudo suricata-update list-sources | head               # otras fuentes disponibles
```

**Anatomía de una regla:**

```text
alert http any any -> $HOME_NET any (msg:"LAB acceso a /admin"; http.uri; content:"/admin"; nocase; sid:1000001; rev:1;)
```

| Parte | Significado |
| --- | --- |
| `alert` | **Acción**: `alert` (avisa), `drop` (bloquea, en modo IPS), `pass`, `reject` |
| `http` | Protocolo |
| `any any -> $HOME_NET any` | Origen (IP, puerto) → destino |
| `msg` | Texto de la alerta |
| `http.uri; content:"/admin"` | Condición: la URI HTTP contiene `/admin` |
| `sid` / `rev` | Identificador único y revisión (usa `sid` > 1 000 000 para reglas propias) |

Añade tus reglas propias en un fichero y activa su lectura:

```bash
sudo tee /var/lib/suricata/rules/local.rules >/dev/null <<'EOF'
alert http any any -> $HOME_NET any (msg:"LAB acceso a /admin"; http.uri; content:"/admin"; nocase; sid:1000001; rev:1;)
alert icmp any any -> $HOME_NET any (msg:"LAB ping detectado"; itype:8; sid:1000002; rev:1;)
EOF
```

En `suricata.yaml`, bajo `rule-files:` añade `- local.rules` (junto a `suricata.rules`). Valida y arranca:

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml -v     # -T: prueba la configuración y las reglas
sudo systemctl enable --now suricata
sudo tail -f /var/log/suricata/suricata.log            # espera "engine started"
```

**Prueba de detección** (desde `sad-cli` contra `sad-web`, en tu laboratorio):

```bash
ping -c 2 192.168.100.30
curl -s http://192.168.100.30/admin >/dev/null
```

Y en el sensor:

```bash
sudo tail -n 5 /var/log/suricata/fast.log              # alertas en formato corto
sudo jq -c 'select(.event_type=="alert") | {t:.timestamp, sig:.alert.signature, src:.src_ip, dst:.dest_ip}' /var/log/suricata/eve.json | tail -5
```

**Modo IPS (en línea).** Para bloquear, Suricata debe ver el tráfico **antes** de reenviarlo, normalmente con `nfqueue`: el cortafuegos manda el tráfico a Suricata y este devuelve un veredicto (aceptar/descartar).

```text
# En nftables del router/pasarela
table inet ips {
  chain forward {
    type filter hook forward priority 0; policy accept;
    queue num 0 bypass                                   # envía a Suricata; "bypass" deja pasar si Suricata no está
  }
}
```

```bash
sudo suricata -c /etc/suricata/suricata.yaml -q 0       # modo nfqueue; las reglas con "drop" bloquean
```

> [!WARNING]
> Un IPS mal ajustado **corta tráfico legítimo** (falsos positivos). Empieza siempre en modo IDS (`alert`), revisa las alertas durante días y solo después pasa a `drop` las reglas de alta confianza. En un punto crítico, valora `bypass` para que un fallo del IPS no pare la red (disponibilidad frente a seguridad: UD5).

---

## 8. Análisis de tráfico: tcpdump y Wireshark

### 8.1. Por qué analizar tráfico

Capturar y leer paquetes permite **diagnosticar** problemas de red, **comprobar** que el cifrado funciona, **verificar** reglas del cortafuegos y **investigar** incidentes. Es la herramienta de «ver lo que realmente ocurre».

> [!CAUTION]
> Captura **solo en tu red de laboratorio o con autorización**. El tráfico de otros puede contener datos personales (RGPD, LOPDGDD) y las comunicaciones están protegidas por el secreto de las comunicaciones.

### 8.2. tcpdump (línea de comandos)

`tcpdump` captura paquetes con filtros **BPF**. Necesita privilegios de `root`.

```bash
sudo tcpdump -D                                       # lista interfaces disponibles
sudo tcpdump -i enp0s3 -c 20                          # 20 paquetes de la interfaz
sudo tcpdump -ni enp0s3 'host 192.168.100.30'         # -n no resuelve nombres; solo tráfico con ese equipo
sudo tcpdump -ni enp0s3 'tcp port 22'                 # solo SSH
sudo tcpdump -ni enp0s3 'icmp'                        # ping
sudo tcpdump -ni enp0s3 'tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack == 0'   # solo SYN iniciales
sudo tcpdump -ni enp0s3 -w captura.pcap 'port 80'     # guarda en fichero .pcap (para Wireshark)
sudo tcpdump -nr captura.pcap | head                  # leer una captura
```

Cómo leer una línea típica:

```text
10:15:32.123456 IP 192.168.100.10.54321 > 192.168.100.30.80: Flags [S], seq 1000, win 64240, length 0
```

`Flags [S]` = SYN, `[S.]` = SYN-ACK, `[.]` = ACK, `[P.]` = datos, `[F.]` = cierre, `[R]` = reinicio. El *handshake* de tres vías es `[S]` → `[S.]` → `[.]`.

### 8.3. Wireshark (análisis gráfico)

**Wireshark** es el analizador gráfico libre estándar. Abre capturas `.pcap` y permite filtrar, seguir conversaciones y descifrar si dispones de las claves.

**Flujo de trabajo recomendado**: capturar con `tcpdump` en el servidor (que no tiene entorno gráfico), copiar el `.pcap` a tu equipo (`scp`) y analizarlo con Wireshark.

Filtros de visualización útiles:

| Filtro | Qué muestra |
| --- | --- |
| `ip.addr == 192.168.100.30` | Tráfico de/hacia esa IP |
| `tcp.port == 80` | Tráfico TCP del puerto 80 |
| `http.request` | Peticiones HTTP |
| `dns` | Consultas y respuestas DNS |
| `tls.handshake.type == 1` | `Client Hello` de TLS (muestra el SNI y los cifrados ofrecidos) |
| `tcp.flags.syn == 1 && tcp.flags.ack == 0` | Intentos de conexión TCP |
| `arp` | Tráfico ARP |
| `tcp.analysis.retransmission` | Retransmisiones (problemas de red) |

Funciones imprescindibles: *Follow → TCP Stream* (reconstruye una conversación), *Statistics → Conversations* (quién habla con quién) y *Statistics → Protocol Hierarchy*.

---

<!-- enr:u6e -->
> [!NOTE]
> **Wireshark y tcpdump:** capturar tráfico de otras personas sin autorización puede vulnerar el secreto de las comunicaciones. En el aula, captura solo el tráfico de tus VM del laboratorio.

## 9. Ejemplo integrado: ciclo defensivo completo

Para integrar todo, un caso con el ciclo **amenaza → vulnerabilidad → ataque → detección → mitigación → comprobación**:

| Fase | Contenido |
| --- | --- |
| **Amenaza** | Un empleado conecta un router doméstico a la LAN para tener Wi-Fi propio |
| **Vulnerabilidad** | La red no tiene DHCP snooping ni control de puertos: el router reparte direcciones y rutas propias (*rogue DHCP*) |
| **Ataque (efecto)** | Algunos equipos reciben una puerta de enlace distinta: se pierde el servicio y el tráfico pasa por un equipo no controlado |
| **Detección** | `tcpdump 'udp port 67 or udp port 68'` muestra dos servidores DHCP respondiendo; Suricata/arpwatch alertan; los usuarios notan la caída |
| **Mitigación** | DHCP snooping, *port security*, 802.1X en los puertos y VLAN por usuario; política escrita que prohíbe equipos no autorizados |
| **Comprobación** | Se conecta un DHCP de prueba en un puerto no confiable y se verifica que el switch lo descarta y registra |

---

## 10. Problemas habituales

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| VLAN no se comunica | El trunk no transporta esa VLAN o no hay etiquetas | `ip -d link`; revisa el modo del puerto (trunk/access) |
| WireGuard sin *handshake* | Clave pública cambiada, puerto bloqueado o `Endpoint` incorrecto | `wg show`; UDP 51820 abierto; compara claves |
| WireGuard conecta pero no llega a la LAN | Falta `ip_forward` o la LAN no conoce la ruta de vuelta | `sysctl net.ipv4.ip_forward`; ruta de retorno o `masquerade` |
| Ping responde por el túnel pero no hay web | Regla `forward` demasiado restrictiva | `nft list ruleset`; `nft monitor trace` |
| IPsec no levanta (`NO_PROPOSAL_CHOSEN`) | Propuestas de cifrado diferentes en los extremos | Iguala `proposals`/`esp_proposals`; `journalctl -u strongswan` |
| `radtest` sin respuesta | Secreto o IP del cliente incorrectos | `freeradius -X` y comprueba el cliente en `clients.conf` |
| Suricata no genera alertas | Interfaz equivocada o reglas no cargadas | `suricata -T`, `af-packet.interface`, `HOME_NET`, `sudo suricata-update` |
| Suricata con muchos falsos positivos | Reglas genéricas sin ajustar | Ajusta `HOME_NET`, desactiva reglas con `disable.conf` de `suricata-update` |
| `tcpdump: permission denied` | Falta de privilegios | Usa `sudo` |
| No veo tráfico ajeno en la captura | Switch (cada puerto solo ve lo suyo) | Puerto espejo (SPAN) o captura en el propio equipo |

---

## 11. Buenas prácticas

- **Segmenta**: separa invitados, empleados, servidores y gestión; filtra entre segmentos con política de denegación por defecto.
- **Cifra siempre**: sustituye protocolos en claro por sus equivalentes seguros y verifica los certificados.
- **Autentica a quién y qué se conecta**: 802.1X, VPN con certificados + MFA.
- **Mínimo privilegio en la VPN**: el cliente accede solo a lo que necesita (`AllowedIPs` y reglas `forward`).
- **Wi-Fi**: WPA3 o WPA2-Enterprise, PMF, WPS desactivado, invitados aislados.
- **Detecta**: IDS en los puntos de paso y registros centralizados (UD4: Wazuh).
- **Gestiona los secretos**: claves privadas con permisos `600`, rotación de PSK, revocación de claves y certificados.
- **Documenta** el diseño de red y la matriz de flujos permitidos (quién → qué → por qué).
- **Prueba** cada medida (captura de tráfico, intento de acceso no permitido) y conserva la evidencia.

---

## 12. Ejercicios

1. Ordena por capa OSI estas amenazas y asocia una medida a cada una: ARP spoofing, SYN flood, DHCP falso, SQL injection, MAC flooding.
2. ¿Qué dos observaciones de `ip neigh` te harían sospechar de un ARP spoofing en tu LAN? ¿Qué medida de **host** y qué medida de **switch** aplicarías?
3. Diseña un esquema de VLAN para un instituto: aulas, profesorado, administración, servidores, Wi-Fi de invitados. Indica rangos IP y las reglas de filtrado entre ellas (tabla origen → destino → permitido).
4. Diferencia `-L`, `-R` y `-D` en SSH con un ejemplo de uso legítimo de cada uno y un riesgo asociado.
5. En WireGuard, ¿qué ocurre si cambias `AllowedIPs` del cliente de `10.99.0.0/24, 10.10.10.0/24` a `0.0.0.0/0`? ¿Qué ventajas e inconvenientes tiene?
6. Explica por qué WPA3-Personal (SAE) protege mejor que WPA2-PSK frente a un diccionario *offline*.
7. Escribe una regla de Suricata que alerte cuando alguien acceda por HTTP a `/phpmyadmin` en tu red. ¿Cómo la probarías sin causar daño?
8. Clasifica estos casos como verdadero/falso positivo/negativo: (a) alerta por un escaneo de puertos real; (b) alerta por la copia de seguridad nocturna; (c) un ataque real sin alerta; (d) tráfico normal sin alerta. ¿Cuál es más peligroso?
9. ¿Qué diferencia hay entre un IDS y un IPS? ¿Qué riesgo introduce un IPS en línea y cómo se mitiga?
10. Describe qué ve un atacante que capture el tráfico entre un cliente y un servidor HTTP con autenticación básica, y entre cliente y servidor HTTPS.

{{% details "Soluciones orientativas" %}}
1. ARP spoofing y MAC flooding: capa 2 (DAI/port security); DHCP falso: capa 3 (DHCP snooping); SYN flood: capa 4 (SYN cookies, límites); SQL injection: capa 7 (consultas parametrizadas, WAF).
2. Dos IP con la misma MAC, o que la MAC del router cambie. Host: ARP estático para el router (`nud permanent`). Switch: DAI con DHCP snooping.
3. Ejemplo: VLAN 10 administración, 20 profesorado, 30 aulas, 40 servidores, 50 invitados. Aulas → servidores: solo HTTP/HTTPS; invitados → solo Internet; administración → todas; profesorado → servidores (SMB/HTTP).
4. `-L` acceder a una intranet desde casa (riesgo: saltarse controles); `-R` exponer un servicio de desarrollo temporalmente (riesgo: puerta trasera desde fuera); `-D` navegar a través de un servidor de confianza (riesgo: eludir el filtrado).
5. Todo el tráfico del cliente pasa por la VPN (*full tunnel*): ventaja, protección en redes no fiables y control corporativo; inconvenientes, más carga en la pasarela, latencia y que la pasarela necesita NAT y DNS adecuados.
6. SAE exige una interacción con el AP por cada intento de adivinar la clave; no se puede capturar un *handshake* y probar claves sin conexión; además da secreto hacia delante.
7. `alert http any any -> $HOME_NET any (msg:"LAB phpmyadmin"; http.uri; content:"/phpmyadmin"; nocase; sid:1000010; rev:1;)`; probarla con `curl http://servidor-propio/phpmyadmin`.
8. (a) verdadero positivo; (b) falso positivo; (c) falso negativo (el más peligroso); (d) verdadero negativo.
9. El IDS observa y alerta; el IPS está en línea y bloquea. Riesgo: falsos positivos que cortan tráfico legítimo y punto único de fallo; mitigación: empezar en modo alerta, `bypass`, ajuste de reglas y redundancia.
10. En HTTP con auth. básica: cabecera `Authorization: Basic …` en Base64 (reversible) y todo el contenido. En HTTPS: solo IP, puerto, tamaños y el SNI; el contenido y las credenciales no son legibles.
{{% /details %}}

---

## 13. Actividad práctica: supuesto profesional

> [!IMPORTANT]
> **Supuesto.** *Gestoría Moncayo* tiene 25 empleados en una oficina en Zaragoza y 4 en teletrabajo. Una sola red plana para todo (empleados, servidores, impresoras, Wi-Fi de visitas). Los teletrabajadores acceden por escritorio remoto abierto a Internet. Hace un mes detectaron que un invitado accedió a la carpeta de clientes.

Entrega un documento con:

1. **Análisis de riesgos de red**: amenazas, vulnerabilidades y activos afectados.
2. **Diseño de red segura**: diagrama con VLAN (rangos IP), Wi-Fi corporativa/invitados, matriz de flujos entre VLAN y DMZ si procede.
3. **Acceso remoto**: sustitución del escritorio remoto expuesto por una VPN WireGuard con acceso restringido a los recursos necesarios y justificación del método de autenticación (MFA).
4. **Detección**: dónde colocarías Suricata y qué reglas/alertas priorizarías.
5. **Plan de comprobación**: pruebas (capturas, intentos denegados) que demuestren cada medida.

Las prácticas guiadas de la unidad están en [Prácticas](/ud05-seguridad-redes/ud05-practicas/).

---

## 14. Resumen

- Cada capa OSI tiene sus amenazas; en la LAN destacan **ARP spoofing**, **MAC flooding**, **DHCP falso** y **VLAN hopping**, que se mitigan con *port security*, DHCP snooping, DAI y VLAN bien configuradas.
- **Segmenta** con VLAN y controla los flujos entre ellas con **ACL/cortafuegos** (denegación por defecto). **Zero Trust**: verificar siempre.
- **Wi-Fi**: WPA3 o WPA2-Enterprise con PMF; nunca WEP/WPA; WPS desactivado.
- Sustituye los protocolos en claro por sus equivalentes cifrados y **comprueba con tcpdump** qué se ve realmente.
- **SSH avanzado**: túneles, bastión con `ProxyJump` y certificados SSH.
- **VPN**: acceso remoto (WireGuard) y sitio a sitio (IPsec/IKEv2); autenticación fuerte (certificados + MFA).
- **RADIUS** centraliza AAA para VPN, Wi-Fi y 802.1X.
- **IDS/IPS**: Suricata con reglas propias; empezar en modo alerta; gestionar falsos positivos.
- **tcpdump** y **Wireshark** permiten verificar, diagnosticar e investigar.

---

## 15. Referencias y documentación oficial

- Wireguard. *Quick Start y documentación*. <https://www.wireguard.com/quickstart/>
- strongSwan. *Documentation (swanctl)*. <https://docs.strongswan.org>
- OpenVPN. *Community Resources*. <https://openvpn.net/community-resources/>
- FreeRADIUS. *Documentation*. <https://www.freeradius.org/documentation/>
- IETF. *RFC 2865: RADIUS*; *RFC 7296: IKEv2*; *RFC 4301: Arquitectura IPsec*. <https://www.rfc-editor.org>
- OISF. *Suricata Documentation*. <https://docs.suricata.io>
- tcpdump. *Manual y filtros pcap-filter(7)*. <https://www.tcpdump.org/manpages/>
- Wireshark. *User's Guide*. <https://www.wireshark.org/docs/>
- OpenSSH. *ssh-keygen(1)* (certificados) y *ssh_config(5)*. <https://man.openbsd.org>
- Wi-Fi Alliance. *WPA3 Specification*. <https://www.wi-fi.org/discover-wi-fi/security>
- INCIBE. *Guías de ciberseguridad*. <https://www.incibe.es>
- CCN-CERT. *Guías CCN-STIC*. <https://www.ccn-cert.cni.es/guias.html>
