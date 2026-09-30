# UD6 - Seguridad en redes

> Protección de las comunicaciones, el acceso y los servicios de red mediante segmentación, cifrado, detección y controles perimetrales.

| Datos de la unidad | Información |
| --- | --- |
| Módulo | Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR |
| Modalidad | Semipresencial |
| Duración | 14 horas |

## Índice

1. [Fundamentos y amenazas de red](#1-fundamentos-y-amenazas-de-red)
2. [Control de acceso y segmentación LAN/WLAN](#2-control-de-acceso-y-segmentación-lanwlan)
3. [Comunicaciones remotas y VPN](#3-comunicaciones-remotas-y-vpn)
4. [Seguridad perimetral, firewalls y DMZ](#4-seguridad-perimetral-firewalls-y-dmz)
5. [Detección, monitorización y respuesta](#5-detección-monitorización-y-respuesta)
6. [Proxies, WAF, DDoS y Zero Trust](#6-proxies-waf-ddos-y-zero-trust)
7. [Resumen](#7-resumen)
8. [Recursos](#8-recursos)
9. [Relación con los resultados de aprendizaje](#9-relación-con-los-resultados-de-aprendizaje)

---

## 1. Fundamentos y amenazas de red

### 1.1. Introducción

Las redes conectan usuarios, sistemas, servicios y sedes, pero también amplían la superficie de ataque. Los protocolos fundacionales de Internet y muchas tecnologías LAN se diseñaron para entornos reducidos y relativamente confiables, sin incorporar autenticación o cifrado de forma generalizada. La seguridad de red aplica controles para preservar confidencialidad, integridad, disponibilidad, autenticidad y trazabilidad.

La protección debe plantearse en capas: infraestructura física, enlace, red, transporte, hosts y aplicaciones. Un control aislado no es suficiente; por ejemplo, un firewall no evita una contraseña robada, y el cifrado no corrige una autorización excesiva.

### 1.2. Amenazas habituales

Entre las amenazas más comunes se encuentran la escucha de tráfico, escaneo de puertos, suplantación de direcciones, malware, acceso no autorizado, denegación de servicio y errores de configuración. Un atacante puede obtener información durante la fase de reconocimiento y aprovechar servicios expuestos, credenciales débiles, equipos sin parchear o redes insuficientemente segmentadas.

Los ataques de intermediario, o MITM, buscan colocarse entre dos participantes para observar, modificar o interrumpir la comunicación. En una LAN IPv4, el envenenamiento ARP puede asociar una IP legítima a la MAC del atacante. Las contramedidas incluyen segmentación, inspección ARP dinámica en switches compatibles, entradas estáticas en casos concretos, cifrado de extremo a extremo y monitorización.

DNS y DHCP son servicios críticos. La manipulación de respuestas DNS puede redirigir a servicios fraudulentos; DNSSEC firma datos DNS para proteger su autenticidad, aunque requiere una cadena de validación correcta. Un DHCP no autorizado puede entregar puertas de enlace o DNS maliciosos; las funciones DHCP snooping y port security en switches gestionables ayudan a limitar este riesgo.

### 1.3. Principios de protección

El mínimo privilegio, la defensa en profundidad, la segmentación y la actualización son principios centrales. Se debe inventariar qué sistemas, puertos, protocolos y flujos son necesarios, permitir solo esos flujos y registrar los eventos relevantes. Los análisis, capturas y pruebas se realizan exclusivamente sobre redes propias o expresamente autorizadas.

## 2. Control de acceso y segmentación LAN/WLAN

### 2.1. Protección de la LAN

La seguridad cableada comienza con el control físico de armarios, paneles de parcheo, switches y puertos. El etiquetado, la documentación, la desactivación de puertos no utilizados y el control de acceso a las salas reducen conexiones y manipulaciones no autorizadas.

La autenticación 802.1X controla el acceso a un puerto antes de permitir el tráfico. El cliente se autentica ante un servidor RADIUS, que puede asignar una VLAN o aplicar una política. El filtrado MAC y port security pueden complementar el control, pero una MAC se puede suplantar y no constituyen una autenticación suficiente por sí solos. Las soluciones NAC amplían esta validación comprobando identidad y, según el caso, postura de seguridad del dispositivo.

### 2.2. VLAN, ACL y segmentación

Una VLAN crea un dominio de capa 2 lógico independiente sobre infraestructura compartida. IEEE 802.1Q etiqueta las tramas que atraviesan enlaces troncales; los puertos de acceso conectan normalmente equipos finales a una única VLAN. La comunicación entre VLAN requiere enrutamiento mediante un router o switch de capa 3.

La segmentación reduce dominios de difusión y limita el movimiento lateral. Una organización puede separar usuarios, servidores, gestión, invitados, IoT y DMZ. Las ACL y reglas de firewall definen explícitamente qué comunicaciones entre zonas están permitidas. Un troncal debe transportar únicamente las VLAN necesarias, y la red de gestión debe estar separada y restringida.

### 2.3. Seguridad WLAN

Una WLAN utiliza un medio radioeléctrico compartido y puede ser alcanzada fuera del edificio, por lo que requiere controles específicos. WEP y WPA con TKIP están obsoletos. WPA2 con AES/CCMP sigue presente cuando se configura correctamente, mientras que WPA3 introduce mejoras, como SAE en modo personal y mayor protección frente a ataques de diccionario sin conexión.

Las redes empresariales deben priorizar WPA2-Enterprise o WPA3-Enterprise con 802.1X y RADIUS, que permiten credenciales o certificados individuales y revocación por usuario. Un SSID de invitados debe aislarse de redes internas. También son relevantes la actualización de puntos de acceso, la detección de AP no autorizados, la desactivación de WPS, el aislamiento de clientes y la planificación de cobertura y potencia.

## 3. Comunicaciones remotas y VPN

### 3.1. Administración y cifrado de comunicaciones

Los servicios de administración y transferencia deben utilizar protocolos autenticados y cifrados. SSH reemplaza a Telnet para la administración remota; HTTPS y TLS protegen aplicaciones web; SFTP y SCP permiten transferencias seguras. La protección criptográfica, certificados y claves se estudian en UD3, y el endurecimiento de SSH en UD4.

### 3.2. Concepto y tipos de VPN

Una VPN crea un túnel protegido sobre una red no confiable. Puede proporcionar confidencialidad, integridad y autenticación, pero no concede acceso ilimitado por defecto. Las VPN de acceso remoto conectan usuarios individuales con una red o aplicación; las VPN site-to-site interconectan sedes o redes completas.

IPsec trabaja en la capa de red y es habitual en conexiones entre sedes. Las VPN basadas en TLS, como OpenVPN, suelen atravesar NAT con facilidad y son prácticas para acceso remoto. WireGuard ofrece una arquitectura más compacta y moderna. L2TP no aporta cifrado por sí solo y normalmente se combina con IPsec. PPTP no debe emplearse en diseños nuevos por sus debilidades conocidas.

### 3.3. Diseño seguro de acceso remoto

Una VPN segura aplica autenticación robusta, preferiblemente MFA, identidades individuales, cifrados actuales, revocación de accesos y registro de conexiones. El *split tunneling* envía por el túnel solo el tráfico corporativo; el *full tunneling* dirige todo el tráfico del cliente por la organización. La elección depende del riesgo, privacidad, capacidad y necesidades de inspección.

También se deben controlar las fugas de DNS, las rutas distribuidas al cliente, los permisos sobre recursos internos y el estado de los dispositivos. El acceso remoto debe limitarse a los servicios necesarios y revisarse de forma periódica.

## 4. Seguridad perimetral, firewalls y DMZ

### 4.1. Firewalls y políticas de filtrado

Un firewall filtra tráfico entre zonas según dirección, puerto, protocolo, estado de la conexión y, en soluciones avanzadas, aplicación o identidad. Los firewalls de filtrado de paquetes son simples y rápidos; los *stateful* mantienen el estado de las conexiones; los de nueva generación pueden incorporar control de aplicaciones, IDS/IPS, filtrado web y otras capacidades.

Una política segura parte de denegar por defecto y permitir de forma explícita solo los flujos necesarios. Las reglas deben documentar origen, destino, servicio, propósito, responsable y fecha de revisión. Las configuraciones, firmware y copias de seguridad del firewall requieren control de cambios y protección.

Netfilter es el marco de filtrado integrado en Linux, gestionable mediante nftables, iptables o firewalld. PF es un firewall usado en sistemas BSD y constituye la base de soluciones como pfSense y OPNsense. La herramienta no sustituye el diseño de una política clara ni la revisión de registros.

### 4.2. DMZ y zonas de seguridad

Una DMZ aloja servicios expuestos, como servidores web o de correo, en una zona separada de la LAN interna. El firewall perimetral controla el tráfico desde Internet hacia la DMZ, y reglas adicionales limitan estrictamente las comunicaciones desde la DMZ a la red interna. Un servidor web no debe acceder sin restricciones a una base de datos o a todos los sistemas corporativos.

Las VLAN, subredes, interfaces separadas y controles entre zonas permiten contener incidentes. La segmentación debe acompañarse de actualizaciones, hardening, monitorización y pruebas de las reglas, porque una DMZ mal configurada puede convertirse en una ruta directa hacia la red interna.

## 5. Detección, monitorización y respuesta

### 5.1. IDS e IPS

Un IDS detecta actividad sospechosa y genera alertas; un IPS además puede bloquear o modificar el tráfico. Los NIDS/NIPS inspeccionan tráfico en puntos de red, mientras que los HIDS/HIPS analizan sucesos de un host. Los sensores pueden recibir una copia de tráfico mediante un puerto SPAN o TAP; un IPS suele situarse en línea, por lo que una política incorrecta puede afectar a tráfico legítimo.

Los mecanismos de detección se basan en firmas, anomalías, políticas o combinaciones de ellos. Las firmas son eficaces frente a amenazas conocidas; las anomalías pueden encontrar comportamientos nuevos, pero producen más falsos positivos si no existe una línea base adecuada. Suricata y Snort son herramientas conocidas para análisis y detección en red.

### 5.2. Análisis de tráfico y registros

Wireshark y tcpdump ayudan a analizar protocolos, direcciones, puertos, sesiones y errores en un entorno autorizado. El análisis permite diagnosticar problemas, verificar cifrado, identificar configuraciones inseguras y estudiar una alerta. Capturar tráfico puede incluir datos personales o credenciales, por lo que las evidencias deben protegerse y conservarse solo el tiempo necesario.

Los registros de switches, routers, firewalls, VPN, IDS/IPS, proxies y servidores deben sincronizar su hora, centralizarse cuando sea posible y protegerse frente a alteración. Un SIEM correlaciona eventos de varias fuentes y facilita alertas e investigación. La respuesta ante un incidente sigue un ciclo de detección, análisis, contención, erradicación, recuperación y mejora.

### 5.3. Límites y mejora continua

Un IDS/IPS necesita ajuste continuo de reglas, actualización de firmas y revisión de falsos positivos y negativos. El cifrado puede impedir inspeccionar el contenido si no se termina o inspecciona de forma controlada; ello plantea requisitos técnicos, legales y de privacidad. Las pruebas de detección se planifican y ejecutan solo sobre entornos autorizados.

## 6. Proxies, WAF, DDoS y Zero Trust

### 6.1. Proxies y WAF

Un proxy directo representa a los clientes ante Internet y puede aplicar filtrado, autenticación, registro y caché. Un proxy inverso se sitúa delante de los servidores, oculta la infraestructura interna, termina TLS, distribuye carga y centraliza registros. Ninguno debe convertirse en un punto único de fallo sin una estrategia de disponibilidad, como se estudia en UD5.

Un WAF inspecciona solicitudes HTTP para detectar o bloquear patrones de ataques contra aplicaciones web, como inyecciones SQL o XSS. Complementa las validaciones de la aplicación, actualizaciones, autenticación y configuración TLS; no corrige por sí solo una aplicación vulnerable. Las reglas deben ajustarse para reducir bloqueos de tráfico legítimo y evitar una falsa sensación de seguridad.

### 6.2. Mitigación de DDoS

Los ataques DDoS buscan agotar ancho de banda, capacidad de red o recursos de aplicación. Pueden ser volumétricos, de amplificación o de capa 7. La mitigación combina limitación de tasa, filtrado, monitorización de picos, capacidad de escalado, CDN y servicios especializados de limpieza de tráfico.

Una organización debe disponer de contactos, umbrales de alerta, procedimientos de escalado y comunicación con proveedores. Las pruebas de resiliencia no consisten en generar tráfico contra sistemas ajenos: se realizan con alcance aprobado, herramientas controladas y medidas de parada.

### 6.3. Zero Trust

Zero Trust parte de que ninguna red, usuario o dispositivo es confiable por defecto. Verifica explícitamente la identidad y contexto de cada acceso, aplica mínimo privilegio y reduce el impacto de un compromiso mediante microsegmentación. MFA, NAC, gestión de dispositivos, políticas por identidad y monitorización continua son elementos habituales.

La implantación es gradual: inventario de activos y flujos, clasificación de recursos, definición de políticas, despliegue por fases y revisión de resultados. No equivale a adquirir un único producto; exige procesos, arquitectura y formación.

## 7. Resumen

La seguridad de red combina protección del acceso LAN y WLAN, segmentación, comunicaciones cifradas, control perimetral, detección y respuesta. Los controles deben ser coherentes con los activos y flujos que protegen, y aplicar el mínimo privilegio en cada capa.

VPN, firewalls, IDS/IPS, proxies, WAF y Zero Trust resuelven problemas distintos y complementarios. Su eficacia depende de una configuración mantenida, monitorización, evidencias protegidas y pruebas realizadas de forma autorizada.

## 8. Recursos

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Wi-Fi Alliance: WPA3](https://www.wi-fi.org/discover-wi-fi/security)
- [WireGuard](https://www.wireguard.com/)
- [OpenVPN](https://openvpn.net/community-resources/)
- [Suricata](https://suricata.io/)
- [Snort](https://www.snort.org/)
- [Wireshark](https://www.wireshark.org/docs/)
- [Netfilter](https://www.netfilter.org/)
- [OWASP: Web Application Firewall](https://owasp.org/www-community/Web_Application_Firewall)

## 9. Relación con los resultados de aprendizaje

Esta unidad contribuye principalmente al **RA2**, mediante la identificación de amenazas, la configuración de controles de red, la segmentación, la monitorización y la detección de intrusiones.

También se relaciona con el **RA3**, por el diseño de VPN y acceso remoto seguro, y con el **RA4**, por las políticas de firewall, DMZ, proxies y protección de servicios perimetrales.
