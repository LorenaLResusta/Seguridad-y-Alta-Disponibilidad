---
title: "Prácticas integradoras obligatorias"
weight: 5
bookToc: true
---

# Prácticas integradoras obligatorias

En el módulo hay **una única práctica obligatoria por trimestre**. Es **integradora**: no repite una práctica de unidad, sino que reúne lo aprendido en varias unidades en un mismo sistema, el de la clínica [Mediterránea Dental](/guia/proyecto-clinica/). Las prácticas de cada unidad siguen siendo la preparación: te dan las piezas, y la integradora te pide **montarlas, justificarlas y demostrar que funcionan**.

| Trimestre | Práctica integradora | Unidades que integra | Entrega | RA |
|---|---|---|---|---|
| 1.º | [INT-1 · Cimientos seguros](#int-1--cimientos-seguros-de-mediterránea-dental) | UD01, UD02, UD03 | **viernes 27 de noviembre de 2026** | RA1, RA2, RA3, RA6, RA7 |
| 2.º | [INT-2 · Servidor fortificado y red segmentada](#int-2--servidor-fortificado-y-red-segmentada) | UD04, UD05, UD06 | lunes 22 de marzo de 2027 *(propuesta)* | RA1 a RA5 |
| 3.º | [INT-3 · Servicio crítico sin parada](#int-3--servicio-crítico-sin-parada) | UD07 y todo lo anterior | viernes 30 de abril de 2027 *(propuesta)* | RA1 a RA7 |

> [!NOTE]
> La fecha de **INT-1 es la fijada para el curso**. Las de INT-2 e INT-3 son una propuesta calculada sobre el [calendario](/guia/temporalizacion/) (INT-2 tras terminar la UD06 el 10 de marzo; INT-3 una semana después de terminar la UD07 el 22 de abril). Se pueden mover cambiando una línea en `tools/planificacion.py`.

> [!IMPORTANT]
> **Las tareas de proyecto de cada unidad ya no se entregan por separado.** Son **hitos** de la práctica integradora del trimestre: las haces en clase, las compruebas y las incorporas a tu informe. Así, cada trimestre entregas **un solo trabajo**, más completo.

## Reglas comunes

| Aspecto | Norma |
|---|---|
| Modalidad | Individual |
| Dedicación | Los hitos se hacen en las horas de prácticas de cada unidad. El resto, de 6 a 8 horas de trabajo autónomo repartidas en las semanas previas a la entrega |
| Laboratorio | Solo máquinas virtuales propias en la red `SAD-NAT`. Nada de datos ni credenciales reales |
| Datos personalizados | Cada persona usa **sus propios datos**: nombre de la CA (`CA-<apellido>`), direccionamiento y usuarios. Dos entregas con los mismos datos se consideran copia |
| Formato | Informe técnico en PDF o Markdown, más un repositorio con configuraciones y *scripts* (sin contraseñas ni claves privadas) |
| Defensa | Cinco minutos en clase: se pide repetir en directo una comprobación y modificar un parámetro |
| Retraso | Cada día lectivo de retraso resta un punto sobre diez, hasta un máximo de tres |

### Estructura del informe

1. **Resumen** y objetivos (una página).
2. **Esquema** de la infraestructura (diagrama con direcciones).
3. **Procedimiento** por fases: qué se hizo, con órdenes y ficheros de configuración relevantes.
4. **Evidencias**: salida real de cada comprobación de la tabla de la práctica.
5. **Análisis**: qué ocurrió en cada prueba de fallo y por qué.
6. **Problemas encontrados** y cómo se diagnosticaron.
7. **Riesgos residuales** y mejoras propuestas.
8. **Referencias** a la documentación oficial usada.

### Rúbrica común

| Nivel | Qué demuestra |
|---|---|
| Insuficiente (0 a 4) | No funciona o faltan fases enteras. Sin evidencias propias |
| Suficiente (5 a 6) | Funciona con errores. Pruebas solo positivas |
| Notable (7 a 8) | Funciona, está justificado y tiene pruebas positivas y negativas |
| Sobresaliente (9 a 10) | Además, hay prueba de fallo con tiempos medidos, análisis y mejoras razonadas |

---

## INT-1 · Cimientos seguros de Mediterránea Dental

{{< practica etiqueta="Práctica integradora" num="1" tipo="Proyecto" duracion="hitos en clase + 6-8 h autónomas" nivel="3" ra="RA1: a,b,c,e,g;RA2: f;RA3: c;RA6: b,f;RA7: f" entorno="Debian 13 · VirtualBox 7" entrega="viernes 27/11/2026 · informe + repositorio" >}}

#### Objetivo

Dejar los datos de la clínica **identificados, protegidos frente a pérdida y cifrados**: diagnosticas el riesgo (UD01), proteges el almacenamiento y demuestras la recuperación (UD02) y montas una PKI propia con servicio HTTPS (UD03).

#### Contexto

La clínica guarda historiales clínicos (datos de salud, categoría especial del RGPD) en un servidor de ficheros sin RAID, sin copias verificadas y accesible por HTTP. La dirección os pide un informe y un entorno de prueba que demuestre cómo quedaría bien hecho. Fija **RPO de 4 horas y RTO de 8 horas** para los ficheros clínicos.

#### Requisitos previos

Laboratorio de la UD01 (práctica 1.1), `srv-ficheros` con cuatro discos de 1 GB y `srv-copias` de la UD02, y las dos máquinas de la UD03. Haz una instantánea de cada máquina antes de empezar cada fase.

#### Fases y hitos

| Fase | Unidad | Qué haces | Hito en clase |
|---|---|---|---|
| A. Diagnóstico | UD01 | Inventario de activos de `srv-ficheros`. Matriz de riesgos con **al menos 8 riesgos** (probabilidad × impacto, tratamiento y riesgo residual). Registro de actividades de tratamiento y política de contraseñas | 1.8 Plan de gestión de riesgos |
| B. Protección | UD02 | RAID 5 con disco de reserva en `srv-ficheros`. **Fallo provocado** de un disco y reconstrucción. Copias cifradas con `restic` a `srv-copias` siguiendo 3-2-1. **Restauración tras un *ransomware* simulado**, con el tiempo medido | 2.7 Plan de almacenamiento y copias |
| C. Cifrado | UD03 | CA raíz propia, certificado de servidor, HTTPS con Nginx (TLS 1.2 y 1.3). Resumen SHA-256 y **firma GPG** del informe de riesgos. **Revocación** de un certificado y comprobación | Práctica 3.8 y tarea de la unidad |

> [!TIP]
> Trabaja por fases y haz una instantánea al terminar cada una. Si la fase C falla, no pierdes la B.

#### Comprobaciones obligatorias

Cada fila debe aparecer en el informe con la **salida real** de la orden y una frase que la interprete.

| # | Qué se comprueba | Orden de referencia | Resultado esperado |
|---|---|---|---|
| 1 | El inventario está completo | `ss -tulpn`, `lsblk`, `dpkg -l \| wc -l` | Servicios, puertos y paquetes listados y comentados |
| 2 | Estado del RAID | `cat /proc/mdstat` y `sudo mdadm --detail /dev/md0` | `[UUUU]` y estado *clean* con disco de reserva |
| 3 | El RAID sobrevive al fallo | `sudo mdadm /dev/md0 --fail /dev/sdb` | Estado *degraded*, datos accesibles, reconstrucción en marcha |
| 4 | La copia es íntegra | `restic -r <repositorio> check` | `no errors were found` |
| 5 | La restauración funciona | `restic restore latest --target /tmp/prueba` y `diff -r` | Sin diferencias; tiempo anotado y comparado con el RTO de 8 h |
| 6 | La CA firma bien | `openssl verify -CAfile ca.crt servidor.crt` | `servidor.crt: OK` |
| 7 | HTTPS con la cadena correcta | `openssl s_client -connect intranet:443 -tls1_3 -CAfile ca.crt` | `Verification: OK` y `TLSv1.3` |
| 8 | Los protocolos obsoletos están cerrados | `openssl s_client -connect intranet:443 -tls1_1` | Error de *handshake* |
| 9 | La firma detecta manipulación | `gpg --verify riesgos.pdf.sig riesgos.pdf`, modificar el PDF y repetir | `Good signature` y después `BAD signature` |
| 10 | La revocación surte efecto | `openssl verify -crl_check -CRLfile ca.crl -CAfile ca.crt servidor.crt` | `certificate revoked` |

#### Problemas habituales

- **El RAID no aparece tras reiniciar:** falta guardar la configuración con `mdadm --detail --scan` en `mdadm.conf` y regenerar el *initramfs*.
- **La restauración «funciona» porque restauras en el mismo directorio:** restaura siempre en una ruta distinta y compara con `diff -r`.
- **El navegador no confía en el certificado:** falta importar `ca.crt` en el almacén del cliente; no desactives la comprobación.
- **El nombre del certificado no coincide:** el `subjectAltName` debe incluir el nombre con el que accedes.

#### Consideraciones de seguridad

Las claves privadas de la CA y del servidor **no se entregan** ni se suben al repositorio. Las copias de datos de salud van cifradas y la contraseña del repositorio se custodia por separado. Usa solo datos ficticios.

#### Rúbrica

| Criterio | Peso |
|---|--:|
| A. Diagnóstico: inventario, matriz de riesgos justificada, RAT y política | 20 % |
| B. Protección: RAID, fallo provocado, copias 3-2-1 y restauración medida frente al RPO/RTO | 30 % |
| C. Cifrado: PKI, HTTPS, firma y revocación comprobadas | 30 % |
| Verificación: las 10 comprobaciones con salida real y análisis | 10 % |
| Documentación reproducible, datos propios y defensa | 10 % |

#### Ampliación

Añade una copia fuera de línea o inmutable y calcula si cumple el RPO de 4 horas con la frecuencia de copia elegida.

---

## INT-2 · Servidor fortificado y red segmentada

{{< practica etiqueta="Práctica integradora" num="2" tipo="Proyecto" duracion="hitos en clase + 6-8 h autónomas" nivel="3" ra="RA1: e,i;RA2: c,d,e,h,i;RA3: c,d,e;RA4: c,d;RA5: b,d" entorno="Debian 13 · VirtualBox 7" entrega="lunes 22/03/2027 (propuesta) · informe + repositorio" >}}

#### Objetivo

Convertir `srv-gestion` en un servidor **fortificado**, ponerlo en una red **segmentada** con cortafuegos de política restrictiva y permitir el **teletrabajo** con una VPN, comprobando cada medida con un ataque simulado en el laboratorio.

#### Contexto

Tras INT-1, la clínica quiere abrir la web de citas a Internet y permitir que dos personas trabajen desde casa. Hay que proteger el servidor de gestión, separar la DMZ de la LAN y detectar intentos de intrusión.

#### Fases y hitos

| Fase | Unidad | Qué haces | Hito en clase |
|---|---|---|---|
| A. Fortificación | UD04 | Puntuación de **Lynis antes y después** (mejora de al menos 10 puntos). SSH solo con clave y Fail2ban. Cortafuegos local. `auditd` y antimalware | 4.11 Fortificación de un servidor |
| B. Red | UD05 | VLAN y ACL entre LAN y DMZ. Suricata con una **regla propia** que detecte un escaneo desde `atacante` | 5.5 Red segura |
| C. Perímetro | UD06 | `fw01` con nftables (`drop` por defecto), NAT y publicación de la web en la DMZ. *Proxy* inverso con TLS. VPN WireGuard para teletrabajo | 6.13 Perímetro |

#### Comprobaciones obligatorias

| # | Qué se comprueba | Resultado esperado |
|---|---|---|
| 1 | Informe de Lynis antes y después | Mejora de al menos 10 puntos y lista de sugerencias abordadas |
| 2 | Intento de acceso SSH con contraseña y con usuario bloqueado | Rechazado; tras varios fallos, IP baneada por Fail2ban |
| 3 | Escaneo con `nmap` desde el exterior | Solo los puertos publicados (443) aparecen abiertos; el resto, filtrados |
| 4 | Matriz de flujos probada | Cada flujo permitido funciona y cada flujo no permitido falla, con registro en el cortafuegos |
| 5 | Alerta de Suricata | La regla propia genera una alerta al escanear desde `atacante` |
| 6 | VPN activa | `wg show` con *handshake* reciente y acceso a un único recurso interno |
| 7 | Prueba negativa de la VPN | Sin clave válida no hay túnel; con clave válida no se llega a recursos no permitidos |

#### Rúbrica

| Criterio | Peso |
|---|--:|
| Fortificación medida (Lynis, SSH, auditoría) | 25 % |
| Segmentación y detección (VLAN, ACL, Suricata) | 25 % |
| Perímetro (nftables, DMZ, *proxy* inverso, VPN) | 30 % |
| Pruebas positivas y negativas con evidencias | 10 % |
| Documentación reproducible y defensa | 10 % |

---

## INT-3 · Servicio crítico sin parada

{{< practica etiqueta="Práctica integradora" num="3" tipo="Proyecto" duracion="hitos en clase + 6-8 h autónomas" nivel="3" ra="RA1 a RA7" entorno="Debian 13 · VirtualBox 7" entrega="viernes 30/04/2027 (propuesta) · dossier final" >}}

#### Objetivo

Hacer que la **web de citas** siga funcionando cuando falla un componente, y reunir en un **dossier final** todo lo construido en el curso, con la prueba de fallo y la recuperación medidas.

#### Contexto

La clínica no puede dejar de dar citas. La dirección fija un **SLA del 99,9 %**, un **RTO de 5 minutos** para la web y un **RPO de 1 minuto** para la base de datos.

#### Fases y hitos

| Fase | Qué haces | Hito en clase |
|---|---|---|
| A. Análisis | Puntos únicos de fallo de la arquitectura de INT-2, disponibilidad calculada y justificación del diseño | 7.1 |
| B. Implantación | Dos servidores web, **HAProxy** con comprobaciones de salud, **Keepalived** con IP virtual y réplica de **MariaDB** | 7.3 a 7.6 |
| C. Fallo y recuperación | Parar un servidor web, el balanceador activo y la base de datos principal, midiendo cuánto tarda el servicio en recuperarse | 7.7 |
| D. Dossier | Arquitectura final, matriz de riesgos residuales, flujos del cortafuegos, política de copias y plan de mejora a 12 meses | 7.10 Arquitectura de alta disponibilidad |

#### Comprobaciones obligatorias

| # | Prueba de fallo | Medición exigida |
|---|---|---|
| 1 | Parada de un servidor web | Hora del fallo, hora de recuperación y peticiones perdidas |
| 2 | Parada del balanceador activo | Tiempo de conmutación de la IP virtual frente al RTO de 5 minutos |
| 3 | Parada de la base de datos principal y promoción de la réplica | Pérdida de datos medida frente al RPO de 1 minuto |
| 4 | Vuelta a la normalidad (*failback*) | Servicio estable sin intervención sobre los clientes |
| 5 | Restauración desde copia con la web en marcha | Datos recuperados e integridad verificada |

#### Rúbrica

| Criterio | Peso |
|---|--:|
| Análisis de puntos únicos de fallo y objetivos (SLA, RTO, RPO) | 15 % |
| Implantación correcta y reproducible | 30 % |
| Pruebas de fallo medidas y análisis de resultados | 30 % |
| Dossier final: coherencia con INT-1 e INT-2 y riesgos residuales | 15 % |
| Defensa oral y documentación | 10 % |

---

## Cómo contribuyen a la nota

> [!NOTE]
> La ponderación es una **propuesta** que debe concretar la programación didáctica del departamento. Se mantiene el reparto de la guía didáctica del módulo, en el que la práctica integradora ocupa el lugar de las prácticas en el aula.

| Instrumento | Peso orientativo |
|---|--:|
| Pruebas teórico-prácticas de unidad | 80 % |
| Práctica integradora del trimestre (la única obligatoria) | 15 % |
| Cuestionarios y autoevaluaciones en Aules | 5 % |

La práctica integradora de cada trimestre debe estar **entregada y aprobada** para superar el trimestre. Quien no la entregue en plazo la recupera con una versión reducida, definida por la persona responsable del módulo, antes de la evaluación.
