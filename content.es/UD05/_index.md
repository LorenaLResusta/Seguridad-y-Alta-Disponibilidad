---
title: "UD05. Seguridad en redes: monitorización, detección y respuesta"
weight: 50
---

# UD05 · Seguridad en redes: monitorización, detección y respuesta

La seguridad de un servidor bien fortificado (UD04) no basta si la red que lo une con el resto de equipos permite que cualquiera escuche, suplante o desborde el tráfico. En esta unidad aprendes a **proteger la red interna** (segmentación con VLAN y ACL, medidas de capa 2, Wi-Fi seguro), a **vigilarla** (captura de tráfico, inventario de servicios, IDS/IPS con Suricata) y a **responder** (centralización de registros, SIEM/XDR con Wazuh y análisis de vulnerabilidades). Todo se practica en un laboratorio aislado, con el ciclo *amenaza → vulnerabilidad → ataque → detección → mitigación → comprobación*.

La unidad aporta al proyecto transversal [Mediterránea Dental](/guia/proyecto-clinica/) la tarea **Red segura**: VLAN y ACL, inventario de servicios, IDS, SIEM y detección de un ataque simulado.

{{< ra "RA2:a,c,d,g,h,i" "RA3:c,g" >}}

| Página | Contenido |
|---|---|
| [Teoría](/ud05/ud05-teoria/) | Amenazas de red por capas, protección de la LAN (VLAN, ACL, *port security*, DHCP *snooping*), Wi-Fi seguro, protocolos seguros, IDS/IPS con Suricata y análisis de tráfico con `tcpdump` y Wireshark |
| [Prácticas](/ud05/ud05-practicas/) | Cuatro prácticas (ARP y DHCP, VLAN y ACL, Suricata, captura de tráfico) y la **tarea del proyecto «Red segura»** |

Lo relativo a SSH avanzado, VPN (WireGuard, IPsec, OpenVPN) y autenticación AAA/RADIUS se estudia en la [UD06. Seguridad perimetral](/ud06/ud06-teoria/).

**Duración:** 18 horas (7 h teoría · 9 h prácticas · 2 h evaluación)

> [!NOTE]
> **Las prácticas de esta unidad no se entregan.** Los conceptos básicos y las órdenes principales que aparecen en ellas entran en la prueba teórico-práctica de la unidad: consulta [qué entra en la prueba](/ud05/ud05-practicas/#qué-entra-en-la-prueba-de-esta-unidad). Esta unidad contribuye a la práctica integradora **INT-2**, que sí se entrega ([cómo se entrega y se corrige](/guia/practicas-integradoras/)).
