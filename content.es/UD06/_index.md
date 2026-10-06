---
title: "UD6. Seguridad en redes y acceso remoto"
weight: 6
bookCollapseSection: true
---

# UD6. Seguridad en redes y acceso remoto

> Amenazas en redes locales e inalámbricas, segmentación con VLAN, protocolos seguros, acceso remoto con SSH y VPN (WireGuard e IPsec), autenticación centralizada con RADIUS, detección de intrusiones con Suricata y análisis de tráfico.

| Datos de la unidad | Información |
| --- | --- |
| Módulo | 0378. Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR · 2026/27 |
| Duración | 14 horas |
| Material | [Teoría](teoria/) · [Prácticas](practicas/) |

## Resultados de aprendizaje y criterios de evaluación

| RA | Criterio de evaluación |
| --- | --- |
| RA2 | c) Se han identificado la anatomía de los ataques más habituales, así como las medidas preventivas y paliativas disponibles. |
| RA2 | f) Se han utilizado técnicas de cifrado, firmas y certificados digitales en un entorno de trabajo basado en el uso de redes públicas. |
| RA2 | g) Se han evaluado las medidas de seguridad de los protocolos usados en redes inalámbricas. |
| RA2 | h) Se ha reconocido la necesidad de inventariar y controlar los servicios de red que se ejecutan en un sistema. |
| RA2 | i) Se han descrito los tipos y características de los sistemas de detección de intrusiones. |
| RA3 | a) Se han descrito escenarios típicos de sistemas con conexión a redes públicas en los que se precisa fortificar la red interna. |
| RA3 | c) Se han identificado los protocolos seguros de comunicación y sus ámbitos de utilización. |
| RA3 | d) Se han configurado redes privadas virtuales mediante protocolos seguros a distintos niveles. |
| RA3 | e) Se ha implantado un servidor como pasarela de acceso a la red interna desde ubicaciones remotas. |
| RA3 | f) Se han identificado y configurado los posibles métodos de autenticación en el acceso de usuarios remotos a través de la pasarela. |
| RA3 | g) Se ha instalado, configurado e integrado en la pasarela un servidor remoto de autenticación. |

## Contenidos

- Amenazas de red por capas: ARP spoofing, MAC flooding, DHCP falso, VLAN hopping, sniffing, MITM, DoS.
- Protección de la LAN: port security, DHCP snooping, DAI, 802.1X.
- Segmentación con VLAN y ACL. Zero Trust.
- Seguridad Wi-Fi: WPA2, WPA3-Personal (SAE), WPA3-Enterprise, OWE.
- Protocolos seguros y sus equivalentes inseguros: SSH, HTTPS, SFTP, DoT/DoH, SNMPv3...
- SSH avanzado: túneles, bastión (ProxyJump), certificados SSH.
- VPN: acceso remoto y sitio a sitio. WireGuard. IPsec/IKEv2 con strongSwan. OpenVPN.
- AAA y RADIUS: FreeRADIUS, EAP, integración con la pasarela.
- IDS/IPS: tipos, firmas y anomalías. Suricata.
- Análisis de tráfico con tcpdump y Wireshark.

## Entorno de laboratorio

Tres o cuatro máquinas virtuales Linux en dos redes internas (sede y «oficina remota» o cliente externo). Wireshark en el equipo anfitrión.

> [!TIP]
> Antes de empezar las prácticas, crea una instantánea (*snapshot*) de cada máquina virtual. Si algo sale mal, podrás volver al estado inicial en segundos.

## Cómo estudiar esta unidad

1. Lee la [teoría](teoria/) en orden: cada apartado se apoya en el anterior.
2. Reproduce los ejemplos en tu laboratorio a medida que aparecen.
3. Resuelve los ejercicios de cada apartado antes de mirar las soluciones.
4. Realiza las [prácticas](practicas/) y entrega la tarea evaluable con las evidencias solicitadas.
