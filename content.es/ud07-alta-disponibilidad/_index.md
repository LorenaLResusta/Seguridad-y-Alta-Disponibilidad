---
title: "UD07. Alta disponibilidad, virtualización y continuidad de negocio"
weight: 70
---

# UD07 · Alta disponibilidad, virtualización y continuidad de negocio

Todo acaba fallando: discos, fuentes de alimentación, cables, actualizaciones, errores humanos e incluso el centro de datos completo. Lo que distingue a una infraestructura profesional no es que no falle, sino que **el servicio sobreviva al fallo** y que, si no puede hacerlo, la organización sepa cómo recuperarse. Esta unidad cierra el módulo: reutiliza el cortafuegos, el *proxy* inverso y la monitorización de las unidades anteriores para que la web de citas de *Mediterránea Dental* siga funcionando cuando se cae un componente.

Aprenderás a **medir** la disponibilidad (los «nueves», SLA, RTO y RPO), a **localizar y eliminar puntos únicos de fallo** con redundancia de hardware, virtualización, balanceo de carga (HAProxy), IP virtual (Keepalived), *clústeres* (Pacemaker, Corosync y Proxmox VE) y replicación de datos, a **vigilar** el servicio con alertas y a **planificar la continuidad de negocio** (BIA, BCP y DRP). Y, sobre todo, a **romper a propósito** cada pieza y comprobar cuánto tarda en recuperarse.

{{< ra "RA6" "RA5:h" >}}

| Página | Contenido |
|---|---|
| [Teoría](/ud07-alta-disponibilidad/ud07-teoria/) | Disponibilidad, SLA/SLO/SLI, SPOF, RTO/RPO, activo-pasivo y activo-activo, redundancia de hardware y de red, virtualización y Proxmox VE, VRRP y Keepalived, Pacemaker y Corosync (quórum y *fencing*), balanceo L4/L7 con HAProxy, almacenamiento compartido, DRBD, Ceph y replicación de bases de datos, escalabilidad y contenedores, monitorización, alta disponibilidad en la nube y continuidad de negocio (BCP, DRP, BIA) |
| [Prácticas](/ud07-alta-disponibilidad/ud07-practicas/) | Siete prácticas (disponibilidad y RAID, web de dos nodos con HAProxy, Keepalived, replicación MariaDB, Pacemaker, Proxmox VE, monitorización) y la **Tarea del proyecto**: web de citas en alta disponibilidad con prueba de fallo y dossier final del módulo |

Esta unidad enlaza con las anteriores: las copias de seguridad y el RAID de la [UD2](/ud02-seguridad-pasiva/ud02-teoria/), el cortafuegos y el *proxy* inverso de la [UD6](/ud06-seguridad-perimetral/ud06-teoria/) y el proyecto transversal [Mediterránea Dental](/guia/proyecto-clinica/).

**Duración:** 18 horas (7 h teoría · 9 h prácticas · 2 h evaluación)
