---
title: "7.  seguridad perimetral. Prácticas"
weight: 1
---
# UD7 - Seguridad perimetral

> Protección de las fronteras de red mediante firewalls, segmentación, publicación segura y control del tráfico.

| Datos de la unidad | Información |
| --- | --- |
| Módulo | Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR |
| Modalidad | Semipresencial |
| Duración | 14 horas |

## Índice

1. [Fundamentos de seguridad perimetral](#1-fundamentos-de-seguridad-perimetral)
2. [Firewalls y plataformas de filtrado](#2-firewalls-y-plataformas-de-filtrado)
3. [Políticas, reglas y registro](#3-políticas-reglas-y-registro)
4. [NAT, publicación de servicios y DMZ](#4-nat-publicación-de-servicios-y-dmz)
5. [Proxies, proxy inverso y WAF](#5-proxies-proxy-inverso-y-waf)
6. [Disponibilidad y operación del perímetro](#6-disponibilidad-y-operación-del-perímetro)
7. [Resumen](#7-resumen)
8. [Recursos](#8-recursos)
9. [Relación con los resultados de aprendizaje](#9-relación-con-los-resultados-de-aprendizaje)

---

## 1. Fundamentos de seguridad perimetral

### 1.1. Introducción

La seguridad perimetral protege las zonas de conexión entre redes con distinto nivel de confianza, especialmente el límite entre Internet, las redes internas, los servicios publicados y el acceso remoto. Su objetivo es reducir accesos no autorizados, ataques, pérdida de datos y el impacto de una intrusión.

Un firewall actúa como filtro entre redes: permite, bloquea, registra o redirige tráfico según reglas predefinidas. Evalúa criterios como interfaces, dirección IP, puertos, protocolos, estado de conexión y, en soluciones avanzadas, aplicación o identidad. Es un punto de control estratégico, pero no sustituye actualizaciones, autenticación robusta, segmentación ni hardening de los sistemas protegidos.

### 1.2. Objetivos

Al finalizar la unidad, el alumnado será capaz de:

- Explicar la función y limitaciones de la seguridad perimetral.
- Diferenciar firewalls de paquetes, con estado, de aplicación y de nueva generación.
- Diseñar políticas de filtrado basadas en denegación por defecto y mínimo privilegio.
- Configurar y justificar NAT, redirección de puertos y una DMZ.
- Interpretar registros y relacionarlos con la detección de incidentes.
- Distinguir proxy directo, proxy inverso y WAF.
- Valorar la disponibilidad, actualización y operación segura de los controles perimetrales.

### 1.3. Zonas y defensa en profundidad

Una arquitectura sencilla separa Internet, LAN, DMZ, red de gestión y acceso VPN. Cada zona debe tener una finalidad definida y flujos documentados. La segmentación limita el movimiento lateral: comprometer un servidor publicado no debe dar acceso directo a todos los sistemas internos.

La defensa en profundidad combina controles: filtrado en el perímetro, reglas entre zonas, protección de hosts, autenticación, monitorización, copias de seguridad y respuesta ante incidentes. La seguridad perimetral se complementa con la segmentación LAN/WLAN y las VPN vistas en UD6.

## 2. Firewalls y plataformas de filtrado

### 2.1. Tipos de firewall

Los firewalls de filtrado de paquetes inspeccionan principalmente direcciones IP, puertos y protocolos. Son rápidos y sencillos, pero no analizan en profundidad el contenido. Los firewalls *stateful* mantienen el estado de conexiones TCP y otros flujos, lo que permite diferenciar tráfico asociado a una sesión legítima de paquetes no solicitados.

Los firewalls de aplicación o *next-generation firewall* pueden identificar protocolos y aplicaciones, aplicar filtrado web, control de contenidos, IDS/IPS o políticas basadas en identidad. Estas funciones amplían la visibilidad, pero requieren dimensionamiento, actualización y ajuste para no bloquear tráfico legítimo ni crear una falsa sensación de seguridad.

### 2.2. Netfilter, PF y soluciones de código abierto

Netfilter es el marco de filtrado y manipulación de tráfico integrado en el kernel Linux. Permite filtrado, NAT, redirección de puertos, registro y seguimiento de conexiones. nftables es la interfaz moderna para definir reglas; iptables continúa presente en muchos entornos, aunque ha sido sustituido progresivamente. firewalld ofrece una capa de gestión dinámica sobre estos mecanismos en varias distribuciones.

Packet Filter, o PF, es un sistema de filtrado y NAT usado en sistemas BSD. Ofrece reglas por interfaces, seguimiento de estado, NAT, tablas de direcciones y capacidades de alta disponibilidad como CARP. pfSense y OPNsense son plataformas basadas en FreeBSD y PF que integran firewall, NAT, VLAN, VPN, DHCP, DNS, monitorización y extensiones como IDS/IPS o proxy.

La elección de plataforma debe considerar requisitos, conocimientos del equipo, soporte, actualizaciones, rendimiento, copias de configuración y capacidad de auditoría. Ninguna herramienta reemplaza una política clara y bien mantenida.

## 3. Políticas, reglas y registro

### 3.1. Diseño de reglas

Una política segura comienza con denegación por defecto y añade únicamente excepciones justificadas. Cada regla debe definir interfaz, origen, destino, protocolo, puerto, acción, finalidad, responsable y fecha de revisión. El orden es importante: muchos firewalls procesan reglas de arriba abajo hasta encontrar una coincidencia.

El mínimo privilegio implica limitar tanto el acceso entrante como el saliente. Por ejemplo, publicar HTTPS hacia un servidor web de la DMZ no implica permitir SSH desde Internet ni conceder a ese servidor acceso libre a la LAN. Las reglas temporales, demasiado amplias o sin responsable deben revisarse y retirarse.

### 3.2. Registros y monitorización

Los registros de firewall documentan conexiones permitidas y bloqueadas, con origen, destino, puerto, protocolo e interfaz. Permiten detectar escaneos, intentos repetidos, errores de reglas, tráfico inesperado y posibles incidentes. Los equipos deben sincronizar su hora y proteger los registros contra alteración.

La centralización en un servidor de logs o SIEM facilita correlacionar eventos de firewalls, VPN, IDS/IPS, proxies y servidores. El volumen de logs requiere criterios de retención, acceso autorizado y alertas útiles. Registrar todo sin revisión no equivale a monitorizar.

### 3.3. Actualización y gestión de cambios

El firmware o software del firewall debe mantenerse actualizado y sus cambios deben probarse, documentarse y poder revertirse. Las copias de configuración deben almacenarse protegidas y comprobarse periódicamente. Antes de modificar una regla crítica se debe disponer de una vía de recuperación para evitar perder acceso administrativo legítimo.

## 4. NAT, publicación de servicios y DMZ

### 4.1. NAT y redirección de puertos

NAT modifica direcciones y, en algunos casos, puertos durante el tránsito. Permite que redes privadas compartan una dirección pública y puede ocultar la estructura interna, pero no es un mecanismo de seguridad completo. La traducción de direcciones debe acompañarse de reglas de filtrado explícitas.

El *port forwarding* publica un servicio interno asociando un puerto o dirección externa con un destino concreto. Solo deben exponerse los servicios necesarios, preferiblemente en una DMZ, y protegerse con actualizaciones, TLS, autenticación y monitorización. Publicar un puerto de administración directamente en Internet aumenta considerablemente el riesgo.

### 4.2. DMZ y segmentación avanzada

Una DMZ es una subred destinada a servicios publicados, como servidores web, correo, DNS público o proxy inverso. Se separa de la LAN mediante interfaces, VLAN o dispositivos distintos. El firewall controla Internet-DMZ, LAN-DMZ y, de forma especialmente restrictiva, DMZ-LAN.

Un servidor web de DMZ puede requerir acceso a un puerto concreto de base de datos, pero no a toda la red interna. Un servidor de correo expuesto puede necesitar entregar correo a un sistema interno, pero no acceso administrativo general. Minimizar servicios, limitar flujos, endurecer hosts y monitorizar accesos reducen el impacto de una intrusión.

## 5. Proxies, proxy inverso y WAF

### 5.1. Proxy directo

Un proxy directo representa a los clientes ante Internet. Puede aplicar autenticación, filtrado por políticas, control de dominios, caché y registro de navegación. Squid es un ejemplo habitual de proxy HTTP/HTTPS. Las reglas de acceso se evalúan en orden y deben terminar en una denegación general después de permitir los clientes y servicios necesarios.

El filtrado de HTTPS tiene limitaciones: sin inspección TLS, el proxy no ve el contenido; con inspección se requieren certificados, información a los usuarios, controles de privacidad y una gestión rigurosa. Las políticas de navegación deben ser proporcionadas, transparentes y acordes con la normativa aplicable.

### 5.2. Proxy inverso y WAF

Un proxy inverso recibe peticiones externas y las reenvía a uno o varios servicios internos. Permite ocultar los backends, centralizar TLS, aplicar control de acceso, registrar solicitudes, ofrecer caché y distribuir carga. Nginx y HAProxy son herramientas habituales; su papel en el balanceo y la alta disponibilidad se relaciona con UD5.

Un WAF inspecciona peticiones web y puede detectar o bloquear patrones asociados a ataques como inyección SQL o XSS. Complementa, pero no sustituye, validación de entradas, autenticación, desarrollo seguro, actualizaciones y registros de la aplicación. Sus reglas requieren ajuste continuo para controlar falsos positivos y negativos.

## 6. Disponibilidad y operación del perímetro

### 6.1. Alta disponibilidad del firewall

Un firewall único puede ser un punto único de fallo. Los entornos con requisitos elevados pueden usar pares activo-pasivo o activo-activo, enlaces redundantes, fuentes de alimentación independientes y sincronización de estado. CARP permite compartir una dirección virtual en plataformas basadas en PF; las soluciones comerciales ofrecen mecanismos equivalentes.

La redundancia debe incluir sus dependencias: alimentación, red, DNS, acceso de gestión, enlaces del proveedor y monitorización. Un diseño HA se valida con pruebas controladas de conmutación, restauración y comportamiento de sesiones, como se estudia en UD5.

### 6.2. Operación y mejora continua

La operación del perímetro comprende inventario de activos, revisión de reglas, parcheo, copias de seguridad, gestión de certificados, análisis de registros y respuesta a incidentes. Las pruebas deben definir alcance, responsables, ventana de mantenimiento, criterios de parada y reversión.

El cumplimiento normativo y la privacidad afectan a la conservación de logs, inspección de tráfico y control de navegación. Las decisiones deben documentarse y revisarse ante cambios de servicios, personal, amenazas o requisitos legales.

## 7. Resumen

La seguridad perimetral separa zonas de confianza y controla sus comunicaciones mediante firewalls, NAT, DMZ y proxies. Una política eficaz parte de denegar por defecto, permite solo flujos justificados y registra los eventos relevantes.

Netfilter, PF, pfSense, OPNsense, Squid, Nginx y WAF son herramientas que deben integrarse en una arquitectura mantenida, monitorizada y preparada para recuperarse de fallos. La segmentación, el hardening y las aplicaciones seguras siguen siendo necesarios incluso detrás de un firewall.

## 8. Recursos

- [Netfilter](https://www.netfilter.org/)
- [nftables](https://wiki.nftables.org/)
- [Packet Filter](https://www.openbsd.org/faq/pf/)
- [pfSense](https://docs.netgate.com/pfsense/en/latest/)
- [OPNsense](https://docs.opnsense.org/)
- [Squid](https://www.squid-cache.org/Doc/)
- [Nginx: reverse proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [OWASP: Web Application Firewall](https://owasp.org/www-community/Web_Application_Firewall)

## 9. Relación con los resultados de aprendizaje

Esta unidad contribuye principalmente al **RA4**, mediante la planificación, configuración y documentación de firewalls, filtrado, NAT, DMZ, registros y resolución de incidencias perimetrales.

También se relaciona con el **RA5**, por la selección y configuración de proxies directos e inversos, y con el **RA3**, cuando el perímetro integra VPN y acceso remoto seguro.
