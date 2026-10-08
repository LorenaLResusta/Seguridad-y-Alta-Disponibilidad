---
title: "UD2. Seguridad pasiva: almacenamiento y copias de seguridad"
weight: 20
---

# UD2 · Seguridad pasiva: seguridad física, almacenamiento y copias de seguridad

Ninguna medida de prevención es infalible: los discos se averían, alguien borra una carpeta por error, el *ransomware* consigue entrar o se va la luz en mitad de una escritura. La **seguridad pasiva** parte de una idea realista (el incidente va a ocurrir) y se ocupa de que sus consecuencias sean mínimas y de que la recuperación sea rápida y demostrable.

En esta unidad recorres la cadena completa de protección de los datos: la **seguridad física** y el centro de proceso de datos (CPD), la **alimentación eléctrica** con SAI, el **almacenamiento redundante** (RAID y LVM), el almacenamiento en red (NAS/SAN), las **copias de seguridad** (`tar`, `rsync`, `restic`, BorgBackup, Proxmox Backup Server y Clonezilla), la política **3-2-1-1-0**, los objetivos **RPO/RTO**, los planes de contingencia y el **borrado seguro** de los soportes. Todo se practica en un laboratorio virtual con **pruebas de fallo** reales: un disco que se avería, un corte eléctrico y un *ransomware* simulado.

{{< ra "RA1:a,b" "RA6:b,f" >}}

| Página | Contenido |
|---|---|
| [Teoría](/ud02-seguridad-pasiva/ud02-teoria/) | Seguridad física y CPD, SAI y NUT, almacenamiento y S.M.A.R.T., RAID, LVM, ZFS/Btrfs, NAS/SAN, copias, RPO/RTO, herramientas, continuidad y borrado seguro |
| [Prácticas](/ud02-seguridad-pasiva/ud02-practicas/) | Nueve prácticas: SAI simulado, RAID con fallo de disco, instantáneas LVM, `rsync`, `restic`, recuperación ante *ransomware*, Clonezilla, borrado seguro y la **Tarea del proyecto «Plan de almacenamiento y copias»** |

**Duración:** 18 horas (7 h teoría · 9 h prácticas · 2 h evaluación)

> [!NOTE]
> La implantación de **almacenamiento redundante** que se inicia aquí (RAID, LVM, copias) se vuelve a trabajar en la [UD7](/ud07-alta-disponibilidad/), donde se combina con replicación, *clústeres* y conmutación automática.

## Cómo estudiar esta unidad

1. Lee la [teoría](/ud02-seguridad-pasiva/ud02-teoria/) en orden: cada apartado se apoya en el anterior.
2. Reproduce los ejemplos en tu laboratorio a medida que aparecen.
3. Resuelve los ejercicios antes de abrir las soluciones.
4. Realiza las [prácticas](/ud02-seguridad-pasiva/ud02-practicas/) y entrega la **Tarea del proyecto** dentro de [Mediterránea Dental](/guia/proyecto-clinica/).
