---
title: "UD4. Fortificación de hosts (hardening)"
weight: 4
bookCollapseSection: true
---

# UD4. Fortificación de hosts (hardening)

> Técnicas para reducir la superficie de ataque de un equipo: mínimo privilegio, usuarios y permisos, contraseñas, SSH, actualizaciones, servicios, cortafuegos local, control de acceso obligatorio, antimalware, registros, auditoría y monitorización en Linux y Windows Server.

| Datos de la unidad | Información |
| --- | --- |
| Módulo | 0378. Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR · 2026/27 |
| Duración | 14 horas |
| Material | [Teoría](teoria/) · [Prácticas](practicas/) |

## Resultados de aprendizaje y criterios de evaluación

| RA | Criterio de evaluación |
| --- | --- |
| RA1 | e) Se han adoptado políticas de contraseñas. |
| RA2 | a) Se han clasificado los principales tipos de amenazas lógicas contra un sistema informático. |
| RA2 | b) Se ha verificado el origen y la autenticidad de las aplicaciones instaladas en un equipo, así como el estado de actualización del sistema operativo. |
| RA2 | c) Se han identificado la anatomía de los ataques más habituales, así como las medidas preventivas y paliativas disponibles. |
| RA2 | d) Se han analizado diversos tipos de amenazas, ataques y software malicioso, en entornos de ejecución controlados. |
| RA2 | e) Se han implantado aplicaciones específicas para la detección de amenazas y la eliminación de software malicioso. |
| RA2 | h) Se ha reconocido la necesidad de inventariar y controlar los servicios de red que se ejecutan en un sistema. |

## Contenidos

- Concepto de hardening, superficie de ataque y guías de referencia (CIS, CCN-STIC).
- Usuarios, grupos, sudo, permisos, ACL, umask y bits especiales.
- Políticas de contraseñas y bloqueo con PAM (pwquality, faillock).
- Arranque seguro: UEFI Secure Boot, contraseña de GRUB, cifrado de disco con LUKS.
- Gestión de paquetes, firmas de repositorios y actualizaciones automáticas.
- Servicios, puertos y procesos: systemd, ss, nmap.
- Cortafuegos local: firewalld, nftables y UFW.
- Acceso remoto seguro con OpenSSH y Fail2ban.
- Control de acceso obligatorio: SELinux y AppArmor.
- Antimalware (ClamAV), integridad de ficheros (AIDE).
- Registros (journald, rsyslog), auditoría (auditd), Lynis y Wazuh.
- Fortificación de Windows Server: directivas, Microsoft Defender, BitLocker, Windows LAPS.

## Entorno de laboratorio

Una máquina virtual Linux servidor, una máquina Linux cliente y, opcionalmente, Windows Server 2025 de evaluación.

> [!TIP]
> Antes de empezar las prácticas, crea una instantánea (*snapshot*) de cada máquina virtual. Si algo sale mal, podrás volver al estado inicial en segundos.

## Cómo estudiar esta unidad

1. Lee la [teoría](teoria/) en orden: cada apartado se apoya en el anterior.
2. Reproduce los ejemplos en tu laboratorio a medida que aparecen.
3. Resuelve los ejercicios de cada apartado antes de mirar las soluciones.
4. Realiza las [prácticas](practicas/) y entrega la tarea evaluable con las evidencias solicitadas.
