---
title: "Temporalización y calendario"
weight: 2
bookToc: true
---

# Temporalización y calendario

## Horas oficiales del módulo

| Dato | Valor | Fuente |
|---|---|---|
| Módulo | 0378. Seguridad y alta disponibilidad | RD 1629/2009 |
| Curso | 2.º ASIR | Decreto 114/2025 |
| **Duración** | **133 horas** | Decreto 114/2025, de 29 de julio, del Consell (Anexo de distribución horaria) |
| **Carga semanal** | **4 horas** (oficial) · **5 horas** en esta planificación | Decreto 114/2025 · horario del grupo |
| Duración mínima estatal | 55 horas · 6 ECTS | RD 1629/2009 (enseñanzas mínimas) |

> [!WARNING]
> **No uses la Orden 36/2012.** La orden anterior fijaba 100 horas (5 semanales) en la Comunitat Valenciana. Para el curso 2026/27 el currículo vigente es el del **Decreto 114/2025**: 133 horas en total. Esta planificación reparte esas 133 horas a **5 horas semanales** (una hora cada día lectivo); el total oficial no cambia.

Estos apuntes cuentan **horas lectivas** (las del horario oficial del grupo). Cada unidad reparte sus horas en tres bloques: **teoría** (explicación y ejemplos), **prácticas** (laboratorio guiado y autónomo) y **evaluación** (prueba teórico-práctica y entrega de la tarea de la unidad).

## Distribución por unidades

| UD | Unidad | Teoría | Prácticas | Evaluación | Total | % | RA principales |
|---|---|--:|--:|--:|--:|--:|---|
| UD1 | [Introducción a la seguridad, riesgos y marco legal](/ud01/) | 7 h | 5 h | 2 h | **14 h** | 11 % | RA1, RA7 |
| UD2 | [Seguridad pasiva: almacenamiento y copias de seguridad](/ud02/) | 7 h | 9 h | 2 h | **18 h** | 14 % | RA1, RA6 |
| UD3 | [Criptografía y aplicaciones criptográficas](/ud03/) | 7 h | 9 h | 2 h | **18 h** | 14 % | RA1, RA2, RA3 |
| UD4 | [Fortificación de hosts y seguridad activa](/ud04/) | 8 h | 12 h | 2 h | **22 h** | 17 % | RA1, RA2 |
| UD5 | [Seguridad en redes: monitorización, detección y respuesta](/ud05/) | 7 h | 9 h | 2 h | **18 h** | 14 % | RA2 |
| UD6 | [Seguridad perimetral: cortafuegos, proxy, VPN y acceso remoto](/ud06/) | 9 h | 14 h | 2 h | **25 h** | 19 % | RA1, RA3, RA4, RA5 |
| UD7 | [Alta disponibilidad, virtualización y continuidad de negocio](/ud07/) | 7 h | 9 h | 2 h | **18 h** | 14 % | RA6 |
| | **Total** | **52 h** | **67 h** | **14 h** | **133 h** | 100 % | RA1 a RA7 |
> [!NOTE]
> El **50 %** de las horas son de laboratorio. Esa proporción es intencionada: en seguridad y alta disponibilidad se aprende configurando, atacando en un entorno aislado, comprobando y recuperando.

## Calendario escolar de referencia 2026/27

| Hito | Fecha |
|---|---|
| Inicio del curso | miércoles 9 de septiembre de 2026 |
| Vacaciones de Navidad | del 22 de diciembre de 2026 al 6 de enero de 2027 |
| Vacaciones de Pascua | del 25 de marzo al 5 de abril de 2027 |
| Fin del curso | viernes 18 de junio de 2027 |
| Días lectivos del curso | 179 |

Festivos y días no lectivos que afectan a la planificación (calendario **provisional** del IES San Vicente; los marcados «propuesta» deben ser aprobados por el Consejo Escolar Municipal):

| Fecha | Motivo |
|---|---|
| viernes 9 oct 2026 | Día de la Comunitat Valenciana |
| lunes 12 oct 2026 | Fiesta Nacional de España |
| lunes 7 dic 2026 | No lectivo (propuesta del Consejo Escolar Municipal) |
| martes 8 dic 2026 | Inmaculada Concepción |
| viernes 19 mar 2027 | San José |
| lunes 5 abr 2027 | Fiesta patronal de San Vicente |
| martes 6 abr 2027 | Fiesta patronal de San Vicente |
| miércoles 7 abr 2027 | No lectivo (propuesta del Consejo Escolar Municipal) |
| jueves 8 abr 2027 | No lectivo (propuesta del Consejo Escolar Municipal) |
| viernes 9 abr 2027 | No lectivo (propuesta del Consejo Escolar Municipal) |

> [!CAUTION]
> **Calendario provisional.** Comprueba las fechas con la versión definitiva que publique el centro. Si cambia algún festivo, vuelve a ejecutar `tools/gen_guia.py` para regenerar esta tabla.

## Propuesta de calendario

**Horario supuesto:** 5 horas semanales, una hora cada día lectivo de lunes a viernes. Si el grupo tiene otro horario, edita `HORARIO` en `tools/calendario.py` y regenera con `python3 tools/planificacion.py` y `python3 tools/gen_guia.py`.

Hasta el 18 de junio hay **174 horas** posibles. Se necesitan 133: el plan termina el **2027-04-22** y quedan **41 horas de margen** para imprevistos, repasos, recuperaciones y la evaluación final.

> [!NOTE]
> El **calendario interactivo** (pulsa un día para ver qué toca) está en la [portada](/). La tabla resume el mismo plan por semanas.

| Semana | Del | Al | Horas | Unidad(es) | Horas acumuladas |
|--:|---|---|--:|---|---|
| 1 | mié 9 sep | vie 11 sep | 3 | UD1 | 1–3 |
| 2 | lun 14 sep | vie 18 sep | 5 | UD1 | 4–8 |
| 3 | lun 21 sep | vie 25 sep | 5 | UD1 | 9–13 |
| 4 | lun 28 sep | vie 2 oct | 5 | UD1 / UD2 | 14–18 |
| 5 | lun 5 oct | jue 8 oct | 4 | UD2 | 19–22 |
| 6 | mar 13 oct | vie 16 oct | 4 | UD2 | 23–26 |
| 7 | lun 19 oct | vie 23 oct | 5 | UD2 | 27–31 |
| 8 | lun 26 oct | vie 30 oct | 5 | UD2 / UD3 | 32–36 |
| 9 | lun 2 nov | vie 6 nov | 5 | UD3 | 37–41 |
| 10 | lun 9 nov | vie 13 nov | 5 | UD3 | 42–46 |
| 11 | lun 16 nov | vie 20 nov | 5 | UD3 / UD4 | 47–51 |
| 12 | lun 23 nov | vie 27 nov | 5 | UD4 | 52–56 |
| 13 | lun 30 nov | vie 4 dic | 5 | UD4 | 57–61 |
| 14 | mié 9 dic | vie 11 dic | 3 | UD4 | 62–64 |
| 15 | lun 14 dic | vie 18 dic | 5 | UD4 | 65–69 |
| 16 | lun 21 dic | lun 21 dic | 1 | UD4 | 70–70 |
| 17 | jue 7 ene | vie 8 ene | 2 | UD4 | 71–72 |
| 18 | lun 11 ene | vie 15 ene | 5 | UD5 | 73–77 |
| 19 | lun 18 ene | vie 22 ene | 5 | UD5 | 78–82 |
| 20 | lun 25 ene | vie 29 ene | 5 | UD5 | 83–87 |
| 21 | lun 1 feb | vie 5 feb | 5 | UD5 / UD6 | 88–92 |
| 22 | lun 8 feb | vie 12 feb | 5 | UD6 | 93–97 |
| 23 | lun 15 feb | vie 19 feb | 5 | UD6 | 98–102 |
| 24 | lun 22 feb | vie 26 feb | 5 | UD6 | 103–107 |
| 25 | lun 1 mar | vie 5 mar | 5 | UD6 | 108–112 |
| 26 | lun 8 mar | vie 12 mar | 5 | UD6 / UD7 | 113–117 |
| 27 | lun 15 mar | jue 18 mar | 4 | UD7 | 118–121 |
| 28 | lun 22 mar | mié 24 mar | 3 | UD7 | 122–124 |
| 29 | lun 12 abr | vie 16 abr | 5 | UD7 | 125–129 |
| 30 | lun 19 abr | jue 22 abr | 4 | UD7 | 130–133 |

## Cómo está pensado el ritmo de cada unidad

1. **Primeras sesiones: teoría y demostración.** Se presentan los conceptos con el ciclo *amenaza → vulnerabilidad → ataque → detección → mitigación → comprobación*.
2. **Sesiones centrales: prácticas guiadas.** Se reproduce el procedimiento paso a paso en el laboratorio y se anota qué ocurre en cada comprobación.
3. **Sesiones finales: práctica autónoma, tarea del proyecto y evaluación.** La última sesión de cada unidad es la prueba; la tarea del proyecto se entrega en esa semana.

> [!TIP]
> En las unidades de red, perímetro y alta disponibilidad conviene dejar las **instantáneas** de las máquinas virtuales preparadas al final de cada sesión: la siguiente práctica parte del estado en que terminó la anterior.


## Entregas obligatorias

| Práctica | Unidades | Fecha |
|---|---|---|
| INT-1 | UD1–UD3 | 27/11/2026 |
| INT-2 | UD4–UD6 | 22/03/2027 (propuesta) |
| INT-3 | UD7 | 30/04/2027 (propuesta) |

Detalle en [Prácticas integradoras](/guia/practicas-integradoras/).