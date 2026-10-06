---
title: "UD2. Seguridad pasiva: almacenamiento y copias de seguridad"
weight: 2
bookCollapseSection: true
---

# UD2. Seguridad pasiva: almacenamiento y copias de seguridad

> Medidas que reducen las consecuencias de un incidente: seguridad física y del CPD, alimentación eléctrica y SAI, almacenamiento, RAID, NAS/SAN, copias de seguridad, RPO/RTO, recuperación y borrado seguro.

| Datos de la unidad | Información |
| --- | --- |
| Módulo | 0378. Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR · 2026/27 |
| Duración | 12 horas |
| Material | [Teoría](teoria/) · [Prácticas](practicas/) |

## Resultados de aprendizaje y criterios de evaluación

| RA | Criterio de evaluación |
| --- | --- |
| RA1 | a) Se ha valorado la importancia de asegurar la privacidad, coherencia y disponibilidad de la información en los sistemas informáticos. |
| RA1 | b) Se han descrito las diferencias entre seguridad física y lógica. |
| RA6 | a) Se han analizado supuestos y situaciones en las que se hace necesario implementar soluciones de alta disponibilidad. |
| RA6 | b) Se han identificado soluciones hardware para asegurar la continuidad en el funcionamiento de un sistema. |
| RA6 | f) Se han implantado sistemas de almacenamiento redundante sobre servidores y dispositivos específicos. |
| RA6 | i) Se han esquematizado y documentado soluciones para diferentes supuestos con necesidades de alta disponibilidad. |

## Contenidos

- Seguridad pasiva y física. Centros de proceso de datos (CPD): ubicación, control de acceso, climatización, incendios.
- Alimentación eléctrica: SAI/UPS, tipos, dimensionado y monitorización con NUT.
- Almacenamiento: HDD, SSD, NVMe. Fallos y monitorización SMART.
- Redundancia y RAID 0, 1, 5, 6 y 10. RAID software con mdadm. LVM.
- Almacenamiento en red: DAS, NAS y SAN. Snapshots.
- Copias de seguridad: completa, incremental y diferencial. Regla 3-2-1-1-0.
- RPO, RTO y política de copias. Herramientas: rsync, tar, restic.
- Automatización con temporizadores systemd y pruebas de restauración.
- Borrado seguro y ciclo de vida de los soportes.

## Entorno de laboratorio

Dos máquinas virtuales Linux (cliente con 4 discos virtuales adicionales y servidor de copias) en una red NAT de VirtualBox.

> [!TIP]
> Antes de empezar las prácticas, crea una instantánea (*snapshot*) de cada máquina virtual. Si algo sale mal, podrás volver al estado inicial en segundos.

## Cómo estudiar esta unidad

1. Lee la [teoría](teoria/) en orden: cada apartado se apoya en el anterior.
2. Reproduce los ejemplos en tu laboratorio a medida que aparecen.
3. Resuelve los ejercicios de cada apartado antes de mirar las soluciones.
4. Realiza las [prácticas](practicas/) y entrega la tarea evaluable con las evidencias solicitadas.
