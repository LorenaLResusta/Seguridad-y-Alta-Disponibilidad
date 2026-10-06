---
title: "Seguridad y Alta Disponibilidad"
weight: 1
bookToC: false
---

# 0378. Seguridad y Alta Disponibilidad

> Apuntes y prácticas del módulo profesional **0378. Seguridad y Alta Disponibilidad** del **2.º curso del CFGS de Administración de Sistemas Informáticos en Red (ASIR)**. Curso **2026/27**.

Estos apuntes están pensados para usarse de dos formas:

- **Como material de referencia**: cada unidad empieza por los fundamentos y avanza hacia la configuración de servicios reales.
- **Como guía de laboratorio**: las prácticas se pueden reproducir paso a paso en máquinas virtuales, sin poner en riesgo ningún sistema real.

## Unidades didácticas

| UD | Unidad | Horas | Resultados de aprendizaje |
| --- | --- | ---: | --- |
| [UD1](ud01/) | Introducción a la seguridad informática | 14 h | RA1, RA7 |
| [UD2](ud02/) | Seguridad pasiva: almacenamiento y copias de seguridad | 12 h | RA1, RA6 |
| [UD3](ud03/) | Criptografía | 14 h | RA1, RA2, RA3, RA7 |
| [UD4](ud04/) | Fortificación de hosts (*hardening*) | 14 h | RA2 |
| [UD5](ud05/) | Alta disponibilidad | 14 h | RA6 |
| [UD6](ud06/) | Seguridad en redes y acceso remoto | 14 h | RA2, RA3, RA7 |
| [UD7](ud07/) | Seguridad perimetral: cortafuegos y proxy | 14 h | RA3, RA4, RA5, RA7 |
| | **Total** | **96 h** | |

Cada unidad contiene:

1. Una **presentación** con los resultados de aprendizaje (RA) y criterios de evaluación (CE) que trabaja, la temporalización y el entorno de laboratorio necesario.
2. La **teoría**, con explicaciones progresivas, ejemplos, comandos comentados y ejercicios.
3. Las **prácticas**, con procedimientos reproducibles, comprobaciones, problemas habituales y una tarea evaluable.

## Resultados de aprendizaje del módulo

| RA | Descripción |
| --- | --- |
| RA1 | Adopta pautas y prácticas de tratamiento seguro de la información, reconociendo las vulnerabilidades de un sistema informático y la necesidad de asegurarlo. |
| RA2 | Implanta mecanismos de seguridad activa, seleccionando y ejecutando contramedidas ante amenazas o ataques al sistema. |
| RA3 | Implanta técnicas seguras de acceso remoto a un sistema informático, interpretando y aplicando el plan de seguridad. |
| RA4 | Implanta cortafuegos para asegurar un sistema informático, analizando sus prestaciones y controlando el tráfico hacia la red interna. |
| RA5 | Implanta servidores *proxy*, aplicando criterios de configuración que garanticen el funcionamiento seguro del servicio. |
| RA6 | Implanta soluciones de alta disponibilidad empleando técnicas de virtualización y configurando los entornos de prueba. |
| RA7 | Reconoce la legislación y normativa sobre seguridad y protección de datos valorando su importancia. |

## Marco normativo

- **Real Decreto 1629/2009**, de 30 de octubre, por el que se establece el título de Técnico Superior en Administración de Sistemas Informáticos en Red y se fijan sus enseñanzas mínimas. Define los RA y CE del módulo 0378.
- **Real Decreto 500/2024**, de 21 de mayo, que modifica los reales decretos de los títulos de grado superior para adaptarlos a la nueva ordenación (incorpora, entre otros, los módulos de Digitalización aplicada, Sostenibilidad aplicada, Inglés profesional, Itinerario personal para la empleabilidad y el Proyecto intermodular). Los RA y CE del módulo 0378 se mantienen.
- **Ley Orgánica 3/2022**, de 31 de marzo, de ordenación e integración de la Formación Profesional, y **Real Decreto 659/2023**, de 18 de julio, que desarrolla la ordenación del Sistema de Formación Profesional.
- El currículo autonómico aplicable (en la Comunitat Valenciana, la orden de currículo del ciclo publicada en el DOGV y sus modificaciones).

## Normas de trabajo en el laboratorio

> [!CAUTION]
> Todas las prácticas de este módulo se realizan **exclusivamente** sobre máquinas virtuales propias y redes aisladas o autorizadas por el profesorado. Escanear, capturar tráfico o probar credenciales contra sistemas ajenos sin autorización es ilegal (artículos 197 bis y 264 del Código Penal) y contrario a la ética profesional.

- Haz una **instantánea (*snapshot*)** antes de cada cambio importante.
- No uses **credenciales reales** ni **datos personales reales**.
- **Documenta** cada cambio: qué has hecho, por qué y cómo se comprueba.
- Sigue siempre el ciclo **amenaza → vulnerabilidad → ataque → detección → mitigación → comprobación**.

## Convenciones de estos apuntes

| Elemento | Significado |
| --- | --- |
| `$ comando` | Comando que se ejecuta como usuario sin privilegios. |
| `# comando` o `sudo comando` | Comando que requiere privilegios de administración. |
| `MAYÚSCULAS` dentro de un comando | Valor que debes sustituir por el tuyo (por ejemplo, `IP_SERVIDOR`). |
| **Debian / Ubuntu** y **AlmaLinux / Rocky** | Cuando un comando cambia entre familias de distribuciones se indican ambas versiones. |

Distribuciones de referencia utilizadas en los ejemplos:

- **Debian 13 (*trixie*)** y **Ubuntu Server 24.04 LTS** o posterior (familia Debian, gestor de paquetes `apt`).
- **AlmaLinux 10** o **Rocky Linux 10** (familia Red Hat, gestor de paquetes `dnf`).
- **Windows Server 2025** y **Windows 11** cuando se trabaja con sistemas Microsoft.
- **VirtualBox 7.x** y **Proxmox VE 9** como plataformas de virtualización.
