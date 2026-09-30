---
title: "6 - Seguridad en redes. Prácticas"
weight: 2
---

# UD6 - Prácticas: seguridad en redes

> Segmentación, perímetro, WLAN, VPN y detección en entornos de pruebas controlados.

| Datos de las prácticas | Información |
| --- | --- |
| Módulo | Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR |
| Modalidad | Semipresencial |
| Duración estimada | 8 horas |
| Entorno | Máquinas virtuales, simulador y equipos autorizados |

## 1. Objetivos

- Diseñar redes segmentadas con VLAN, DMZ y reglas de mínimo privilegio.
- Configurar y comprobar un firewall perimetral en un entorno virtual.
- Evaluar una WLAN y aplicar autenticación empresarial cuando el entorno lo permita.
- Desplegar VPN de acceso remoto y site-to-site con rutas y reglas limitadas.
- Capturar tráfico propio y analizar alertas de un IDS/IPS.
- Configurar un proxy y documentar evidencias de pruebas de seguridad.

## 2. Alcance y preparación

Estas prácticas se realizan solo en máquinas virtuales, redes internas, switches, puntos de acceso y firewalls autorizados. No escanees, captures tráfico, pruebes credenciales, modifiques puntos de acceso ni generes tráfico de denegación de servicio fuera del entorno de pruebas.

Se recomienda crear una *snapshot* antes de cada práctica. Para los escenarios perimetrales se utilizarán un firewall pfSense u OPNsense, una VM cliente y una VM servidor. Para las VPN site-to-site se necesitarán dos firewalls y un cliente en cada LAN. Registra las IP, redes, interfaces y cambios realizados en una tabla de trabajo.

## 3. Práctica 1 - Firewall perimetral, VLAN y DMZ

### 3.1. Escenario

En VirtualBox, crea un firewall con tres interfaces y dos VM Linux:

| Interfaz o VM | Red | Función |
| --- | --- | --- |
| WAN | NAT o puente de entorno de pruebas | Salida a Internet simulada. |
| LAN | Solo-anfitrión o red interna | Cliente corporativo. |
| DMZ | Red interna independiente | Servidor web. |
| Cliente | LAN | Comprobación de políticas. |
| Servidor | DMZ | Servicio HTTP/HTTPS y SSH de entorno de pruebas. |

Instala pfSense u OPNsense, asigna correctamente las interfaces y configura subredes distintas para LAN y DMZ. El acceso a la interfaz de administración debe realizarse desde la LAN o red de gestión, nunca desde WAN.

### 3.2. Servicios y reglas

En el servidor de la DMZ instala Apache o Nginx y permite solo los puertos necesarios en su firewall local. Crea en el firewall perimetral una política de denegación por defecto y reglas que cumplan la siguiente matriz:

| Origen | Destino | Servicios permitidos |
| --- | --- | --- |
| LAN | DMZ | ICMP, HTTP, HTTPS y SSH. |
| WAN | DMZ | HTTPS publicado mediante NAT/port forwarding. |
| DMZ | LAN | Ninguno. |
| LAN | WAN | DNS, HTTP y HTTPS necesarios. |

Comprueba los flujos permitidos con `ping`, `curl` y SSH desde tus VM. Comprueba también que un servicio no autorizado de LAN a DMZ y cualquier conexión iniciada de DMZ a LAN quedan bloqueados. Incluye capturas de las interfaces, reglas, NAT y resultados de cada prueba.

### 3.3. Extensión de VLAN

Diseña VLAN de administración, usuarios, servidores, invitados, DMZ y gestión. Indica puertos de acceso, troncales 802.1Q y reglas inter-VLAN. Si dispones de switch gestionable o simulador, implementa al menos dos VLAN y comprueba aislamiento entre ellas. No habilites VLAN en un troncal si no es necesaria.

## 4. Práctica 2 - WLAN segura y autenticación RADIUS

### 4.1. Auditoría de WLAN

Revisa un AP propio, autorizado o simulado. Completa una ficha que indique estándar WPA configurado, autenticación, WPS, actualización de firmware, cuenta de administración, SSID de invitados, VLAN asignada, aislamiento de clientes y cobertura. Justifica por qué WEP, WPA y TKIP no deben utilizarse.

Compara WPA2/WPA3-Personal con WPA2/WPA3-Enterprise. Explica cómo se revoca el acceso de una persona en cada caso y por qué una clave PSK compartida no escala bien en una organización.

### 4.2. FreeRADIUS opcional

En una VM Debian o Ubuntu de entorno de pruebas, instala FreeRADIUS y sus utilidades:

```bash
sudo apt update
sudo apt install -y freeradius freeradius-utils
sudo systemctl enable --now freeradius
```

Revisa la configuración de clientes RADIUS y autoriza únicamente la IP del AP de entorno de pruebas con un secreto compartido de prácticas. Crea un usuario temporal en el fichero de usuarios de FreeRADIUS o mediante el método indicado por el docente. Ejecuta el servicio en modo de depuración solo durante la prueba:

```bash
sudo systemctl stop freeradius
sudo freeradius -X
```

Configura el AP para WPA2/WPA3-Enterprise y prueba la conexión con un cliente autorizado. No incluyas contraseñas ni secretos RADIUS en la memoria. Si no se dispone de AP compatible, documenta el flujo de autenticación 802.1X entre suplicante, AP y servidor RADIUS.

## 5. Práctica 3 - VPN de acceso remoto y site-to-site

### 5.1. Acceso remoto con WireGuard

Configura una VPN entre `vpn01` y `cliente01` en VM propias. Usa una subred de túnel, por ejemplo `10.20.30.0/24`, y claves generadas localmente:

```bash
sudo dnf install -y wireguard-tools
umask 077
wg genkey | tee privatekey | wg pubkey > publickey
```

En Debian o Ubuntu, instala `wireguard` mediante `apt`. En `vpn01` crea `/etc/wireguard/wg0.conf` con una dirección `10.20.30.1/24`, puerto UDP `51820`, su clave privada y un par autorizado con `AllowedIPs = 10.20.30.2/32`. Configura el cliente con `10.20.30.2/24`, la clave pública de `vpn01`, el endpoint de entorno de pruebas y solo las redes internas necesarias en `AllowedIPs`.

Permite UDP 51820 en el firewall únicamente desde el entorno de pruebas y activa ambos extremos con `sudo systemctl enable --now wg-quick@wg0`. Comprueba el estado con `sudo wg show`, verifica conectividad y documenta si usas *split tunneling* o *full tunneling*. Las claves privadas se ocultan en toda evidencia entregada.

### 5.2. Site-to-site con pfSense

Construye dos sedes en VirtualBox con dos pfSense, una WAN compartida de entorno de pruebas, dos LAN distintas y una VM cliente en cada LAN:

| Sede | LAN de ejemplo | Túnel WireGuard de ejemplo |
| --- | --- | --- |
| Principal | `192.168.23.0/24` | `10.69.69.1/30` |
| Secundaria | `192.168.17.0/24` | `10.69.69.2/30` |

En cada pfSense crea un túnel WireGuard, genera sus claves y crea el par con la clave pública del extremo opuesto. Configura como redes permitidas la red del túnel y la LAN remota; asigna la interfaz del túnel y crea reglas que permitan exclusivamente los servicios requeridos entre ambas LAN. En WAN, permite UDP al puerto del túnel solo desde la dirección WAN del par cuando sea posible.

Comprueba desde los clientes de ambas sedes que el tráfico autorizado cruza el túnel y que el no autorizado queda bloqueado. Como alternativa documentada, implementa el mismo escenario con OpenVPN o IPsec IKEv2 desde los asistentes de pfSense, usando cifrados actuales y reglas equivalentes. No utilices PPTP en ningún caso.

## 6. Práctica 4 - Captura de tráfico e IDS/IPS

### 6.1. Captura autorizada

Captura tráfico generado por tus propias VM mientras realizas una consulta DNS y conexiones HTTP y HTTPS a servicios de prueba:

```bash
sudo tcpdump -i INTERFAZ -nn -w ud6-pruebas.pcapng
```

Con Wireshark, identifica IP y puerto origen/destino, protocolo, establecimiento TCP y consulta/respuesta DNS. Compara qué contenido puede observarse en HTTP frente a HTTPS. Las capturas pueden contener datos sensibles; no compartas cookies, credenciales, claves ni tráfico de otras personas.

### 6.2. Suricata o Snort en pfSense

En el firewall de la práctica 1, instala Suricata o Snort desde `System > Package Manager`. Deshabilita las opciones de *hardware offloading* de la VM si el producto lo requiere. Activa inicialmente modo IDS, instala un conjunto gratuito de reglas, selecciona una interfaz de entorno de pruebas y actualiza las reglas.

Genera únicamente tráfico benigno y autorizado entre tus VM, como peticiones HTTP a la DMZ o conexiones repetidas a un servicio de prueba. Revisa alertas y registra fecha, origen, destino, regla, clasificación, gravedad y posible falso positivo. Después de validar el modo IDS, valora de forma razonada qué reglas podrían bloquearse en modo IPS y durante cuánto tiempo. No actives bloqueo generalizado sin una reversión preparada.

Explica la diferencia entre un sensor conectado a SPAN/TAP y un IPS en línea. Como ampliación, investiga cómo Security Onion centraliza Suricata, Zeek y registros de red para investigación, sin desplegarlo si los recursos del equipo no son suficientes.

## 7. Práctica 5 - Proxy directo e inverso

### 7.1. Proxy directo con Squid

En una VM AlmaLinux 9 instala Squid y permite el puerto solo desde la subred de entorno de pruebas:

```bash
sudo dnf install -y squid
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.bak
```

Define una ACL para la red de prácticas y revisa que las reglas se evalúan en orden. La configuración debe permitir solo los clientes autorizados y terminar con una denegación general. Configura el navegador de una VM cliente para utilizar el proxy y revisa `/var/log/squid/access.log`.

Implementa una lista de bloqueo exclusivamente con dominios de prueba o ficticios. Documenta por qué el filtrado HTTPS sin una arquitectura de inspección y certificados gestionados tiene limitaciones de privacidad y compatibilidad.

### 7.2. Proxy inverso con Nginx

En una VM Linux crea dos servicios HTTP de prueba en puertos diferentes y configura Nginx como proxy inverso. Verifica que se accede a cada servicio mediante rutas distintas, sin exponer los puertos internos directamente. Como ampliación, usa un bloque `upstream` para repartir solicitudes entre dos backends propios y comprueba el comportamiento cuando uno deja de responder.

Explica qué protección añade un WAF delante de una aplicación y qué controles siguen siendo responsabilidad de la propia aplicación: validación de entradas, autenticación, actualizaciones y registros.

## 8. Actividades

1. Diseña una tabla de VLAN y una matriz de flujos para usuarios, administración, invitados, IoT, servidores y DMZ.
2. Explica qué controles limitan ARP spoofing, DHCP no autorizado y DNS manipulable.
3. Compara una VPN de acceso remoto con una VPN site-to-site, incluyendo identidad, rutas y reglas.
4. Propón una política de reglas de firewall con denegación por defecto para una aplicación web en DMZ.
5. Diferencia IDS, IPS, NIDS y HIDS, y explica el impacto de los falsos positivos.
6. Identifica qué registros deberían enviarse a un SIEM desde firewall, VPN, proxy e IDS/IPS.
7. Diseña medidas proporcionadas para responder a un incremento anómalo de peticiones HTTP sin bloquear usuarios legítimos.

## 9. Autoevaluación

1. ¿Qué es una DMZ?
2. ¿Qué diferencia existe entre VLAN y subred?
3. ¿Qué controla 802.1X?
4. ¿Por qué WEP y TKIP son inseguros?
5. ¿Qué diferencia existe entre una VPN site-to-site y una de acceso remoto?
6. ¿Qué función tiene `AllowedIPs` en WireGuard?
7. ¿Qué es una política de denegación por defecto?
8. ¿Qué diferencia hay entre un IDS y un IPS?
9. ¿Qué puede revelar una captura HTTP que HTTPS bien configurado no muestra?
10. ¿Qué función tiene un proxy inverso?
11. ¿Qué riesgos de disponibilidad o privacidad plantea un proxy?
12. ¿Qué principios aplica Zero Trust?

## 10. Tarea evaluable única - Diseño de una red segura

Entrega una memoria en PDF o Markdown para una empresa de 50 usuarios, una sede secundaria, teletrabajo, servicios web publicados y WLAN para invitados. Incluye:

1. Diagrama lógico con VLAN, subredes, DMZ, WLAN, sedes, VPN y controles.
2. Inventario de activos, amenazas y puntos de control.
3. Tabla de VLAN, direccionamiento y reglas de firewall con denegación por defecto.
4. Diseño WLAN con autenticación, invitados y control de acceso.
5. Propuesta de VPN de acceso remoto o site-to-site con rutas, DNS, MFA y revocación.
6. Ubicación y función de firewall, IDS/IPS, proxy, WAF, registros y monitorización.
7. Medidas de mitigación DDoS y aplicación gradual de Zero Trust.
8. Plan de pruebas con evidencias esperadas, reversión y justificación técnica.

| Criterio | Peso |
| --- | ---: |
| Amenazas, activos y segmentación | 20 % |
| Firewall, DMZ y reglas de mínimo privilegio | 20 % |
| Seguridad WLAN y control de acceso | 15 % |
| VPN y acceso remoto seguro | 15 % |
| Detección, registros y respuesta | 15 % |
| Proxy, WAF, DDoS y Zero Trust | 5 % |
| Diagrama, evidencias y justificación | 10 % |
| **Total** | **100 %** |

## 11. Recursos

- [Documentación de pfSense](https://docs.netgate.com/pfsense/en/latest/)
- [OPNsense](https://docs.opnsense.org/)
- [WireGuard](https://www.wireguard.com/quickstart/)
- [OpenVPN](https://openvpn.net/community-resources/)
- [FreeRADIUS](https://www.freeradius.org/documentation/)
- [Suricata](https://docs.suricata.io/)
- [Snort](https://www.snort.org/documents)
- [Squid](https://www.squid-cache.org/Doc/)
- [Security Onion](https://securityonionsolutions.com/)
- [NIST: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
