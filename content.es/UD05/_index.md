---
title: "UD5. Alta disponibilidad"
weight: 5
bookCollapseSection: true
cascade:
  build:
    render: never
    list: never
---

# UD5. Alta disponibilidad

> Diseño e implantación de servicios que siguen funcionando cuando falla un componente: disponibilidad, SLA, SPOF, redundancia, virtualización, balanceo de carga, IP virtual, clústeres, replicación y pruebas de fallo.

| Datos de la unidad | Información |
| --- | --- |
| Módulo | 0378. Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR · 2026/27 |
| Duración | 14 horas |
| Material | [Teoría](teoria/) · [Prácticas](practicas/) |

## Resultados de aprendizaje y criterios de evaluación

| RA | Criterio de evaluación |
| --- | --- |
| RA6 | a) Se han analizado supuestos y situaciones en las que se hace necesario implementar soluciones de alta disponibilidad. |
| RA6 | b) Se han identificado soluciones hardware para asegurar la continuidad en el funcionamiento de un sistema. |
| RA6 | c) Se han evaluado las posibilidades de la virtualización de sistemas para implementar soluciones de alta disponibilidad. |
| RA6 | d) Se ha implantado un servidor redundante que garantice la continuidad de servicios en casos de caída del servidor principal. |
| RA6 | e) Se ha implantado un balanceador de carga a la entrada de la red interna. |
| RA6 | f) Se han implantado sistemas de almacenamiento redundante sobre servidores y dispositivos específicos. |
| RA6 | g) Se ha evaluado la utilidad de los sistemas de «clusters» para aumentar la fiabilidad y productividad del sistema. |
| RA6 | h) Se han analizado soluciones de futuro para un sistema con demanda creciente. |
| RA6 | i) Se han esquematizado y documentado soluciones para diferentes supuestos con necesidades de alta disponibilidad. |

## Contenidos

- Disponibilidad, fiabilidad, MTBF, MTTR, SLA, SLO y «nueves».
- Punto único de fallo (SPOF), redundancia y tolerancia a fallos.
- RTO y RPO aplicados a servicios.
- Redundancia de hardware, alimentación y red (bonding).
- Virtualización: hipervisores, KVM, Proxmox VE, snapshots, migración en vivo y HA de máquinas virtuales.
- Balanceo de carga con HAProxy: algoritmos, comprobaciones de salud, persistencia.
- IP virtual con VRRP y Keepalived.
- Clústeres activo-pasivo con Pacemaker y Corosync: quórum y fencing.
- Replicación de bases de datos (MariaDB) y almacenamiento replicado.
- Escalabilidad vertical y horizontal, contenedores y pruebas de carga.
- Monitorización de la disponibilidad.

## Entorno de laboratorio

Entre cuatro y cinco máquinas virtuales Linux ligeras en una red interna (balanceadores, servidores web y base de datos). Opcional: Proxmox VE 9 con virtualización anidada.

> [!TIP]
> Antes de empezar las prácticas, crea una instantánea (*snapshot*) de cada máquina virtual. Si algo sale mal, podrás volver al estado inicial en segundos.

## Cómo estudiar esta unidad

1. Lee la [teoría](teoria/) en orden: cada apartado se apoya en el anterior.
2. Reproduce los ejemplos en tu laboratorio a medida que aparecen.
3. Resuelve los ejercicios de cada apartado antes de mirar las soluciones.
4. Realiza las [prácticas](practicas/) y entrega la tarea evaluable con las evidencias solicitadas.
