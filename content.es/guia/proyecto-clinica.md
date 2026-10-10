---
title: "Proyecto transversal: Mediterránea Dental"
weight: 3
bookToc: true
---

# Proyecto transversal: Mediterránea Dental

A lo largo del curso construyes, unidad a unidad, la seguridad de **una misma empresa ficticia**. Así cada práctica deja de ser un ejercicio aislado: lo que fortificas en la UD04 se vigila en la UD05, se protege con el perímetro de la UD06 y se hace redundante en la UD07.

> [!IMPORTANT]
> **Todo es ficticio.** Mediterránea Dental S. L., sus pacientes y sus datos no existen. Nunca uses datos personales reales ni credenciales reales en el laboratorio.

## La empresa

**Mediterránea Dental S. L.** es una clínica dental con una sede y una delegación pequeña.

| Dato | Descripción |
|---|---|
| Personal | 12 puestos de trabajo (recepción, gabinetes, administración) y 2 personas en teletrabajo |
| Aplicación crítica | Gestión de pacientes: historiales clínicos (**datos de salud, categoría especial del RGPD**), citas y facturación |
| Servicios | Servidor de gestión (aplicación + base de datos), servidor de ficheros, **web de citas en línea**, correo gestionado por un proveedor externo |
| Conexión | Fibra con IP pública única; sin cortafuegos dedicado ni copias verificadas |
| Problema | Un ataque de *ransomware* en otra clínica del sector ha motivado el encargo: **diagnosticar, proteger y garantizar la continuidad** |

Tú eres el técnico de sistemas contratado para hacerlo. En cada unidad montas una pieza de la clínica (**no se entrega**); esas piezas se reúnen en dos [prácticas integradoras](/guia/practicas-integradoras/) que sí se entregan.

## Infraestructura de laboratorio

Todas las máquinas son virtuales (ver [Entorno de trabajo](/guia/entorno/)). El direccionamiento es común a todas las unidades:

```text
                    Internet (NAT del hipervisor)
                               │
                        ┌──────┴──────┐
                        │ fw01        │  nftables (Debian 13) u OPNsense
                        └──┬───────┬──┘
                           │       │
        LAN 192.168.10.0/24│       │DMZ 172.16.10.0/24
       ┌───────────────────┴┐    ┌─┴──────────────────┐
       │ srv-gestion  .10   │    │ web01 .11  web02 .12│
       │ srv-ficheros .11   │    │ lb01  .21  lb02 .22 │
       │ mon01        .20   │    │ VIP   .20           │
       │ cli-recepcion .50  │    │ db01  .30 (réplica) │
       └────────────────────┘    └─────────────────────┘
```

| Máquina | Sistema | Red | Rol | Unidades |
|---|---|---|---|---|
| `fw01` | Debian 13 (nftables) u OPNsense | WAN, LAN, DMZ | Cortafuegos perimetral, NAT y pasarela VPN | UD06, UD07 |
| `srv-gestion` | Debian 13 | LAN `.10` | Aplicación y base de datos de pacientes | UD01 a UD05 |
| `srv-ficheros` | Debian 13 | LAN `.11` | Documentos, copias y NAS | UD02, UD04 |
| `mon01` | Debian 13 | LAN `.20` | Monitorización y SIEM (Wazuh, Zabbix o Prometheus) | UD04, UD05, UD07 |
| `cli-recepcion` | Debian con escritorio o Windows 11 | LAN `.50` | Puesto de recepción | UD01, UD04, UD05 |
| `web01`, `web02` | Debian 13 | DMZ `.11`, `.12` | Web de citas (dos nodos) | UD06, UD07 |
| `lb01`, `lb02` | Debian 13 | DMZ `.21`, `.22` (VIP `.20`) | Balanceo y alta disponibilidad | UD07 |
| `db01` | Debian 13 | DMZ `.30` | Base de datos con réplica | UD07 |
| `atacante` | Debian con herramientas de auditoría | Red aislada del laboratorio | Simula amenazas **solo en el laboratorio** | UD04 a UD06 |

> [!NOTE]
> No hace falta tener todas las máquinas encendidas a la vez. Cada práctica indica cuáles necesita; el resto permanece apagado y con su instantánea.

## Qué construyes en cada unidad

| UD | Tarea del proyecto (de repaso, no se entrega) | Qué debe quedar montado | Integradora | CE principales |
|---|---|---|---|---|
| **UD01** | **Diagnóstico inicial**: inventario de activos, análisis de riesgos (matriz probabilidad × impacto), registro de actividades de tratamiento (RAT) y política de seguridad | Matriz de riesgos, RAT y política | INT-1 | RA1.a-d, RA7.a-g |
| **UD02** | **Plan de almacenamiento y copias**: RAID en `srv-ficheros`, política 3-2-1, RPO/RTO objetivo y restauración demostrada | RAID, copias cifradas y restauración probada | INT-1 | RA1.b, RA6.b, RA6.f |
| **UD03** | **PKI interna y cifrado**: CA propia, HTTPS en la intranet, volumen de datos clínicos cifrado, firma de consentimientos | CA, certificado y HTTPS verificable | INT-1 | RA1.g, RA2.f, RA3.c |
| **UD04** | **Bastionado de `srv-gestion`**: puntuación de Lynis antes y después, SSH por clave con segundo factor, `auditd`, antimalware e integridad | Servidor fortificado y medido | INT-1 | RA1.e-f, RA1.i, RA2.a-e |
| **UD05** | **Red segura**: VLAN y ACL, inventario de servicios, IDS (Suricata), SIEM (Wazuh) y detección de un ataque simulado | Segmentación y detección con alerta | INT-2 | RA2.c-d, RA2.g-i |
| **UD06** | **Perímetro**: `fw01` con DMZ, NAT, *proxy* directo e inverso, VPN de teletrabajo y autenticación centralizada | Cortafuegos, publicación y VPN | INT-2 | RA1.h, RA3, RA4, RA5 |
| **UD07** | **Continuidad**: web de citas en alta disponibilidad (HAProxy + Keepalived), base de datos replicada, monitorización y **prueba de fallo** | Servicio que sobrevive a un fallo, con RTO medido | INT-2 | RA6.a-i |

### Las dos prácticas integradoras

Reúnen las piezas anteriores en un único sistema y **son lo único que se entrega**: INT-1 (UD01–UD04, un servidor seguro) e INT-2 (UD05–UD07, perímetro y servicio sin parada). Cada una se corrige con un script de verificación y cuatro preguntas cortas. Consulta [las condiciones y fechas](/guia/practicas-integradoras/).

## Qué se valora del proyecto

| Criterio | Qué se valora |
|---|---|
| Corrección técnica | La configuración funciona y se ha comprobado (capturas y salidas de órdenes reales) |
| Seguridad | Se aplican mínimo privilegio, defensa en profundidad y se justifican las decisiones |
| Verificación | Hay pruebas **positivas y negativas**; en alta disponibilidad, una prueba de fallo y la recuperación |
| Documentación | Otra persona podría reproducir el trabajo con tu informe |
| Cumplimiento | Se identifican las obligaciones legales aplicables (RGPD, LOPDGDD, ENS cuando proceda) |
