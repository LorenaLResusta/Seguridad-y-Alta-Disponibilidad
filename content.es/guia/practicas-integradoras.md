---
title: "Prácticas integradoras obligatorias"
weight: 5
bookToc: true
---

# Prácticas integradoras obligatorias

> [!IMPORTANT]
> **En este módulo las prácticas de cada unidad no se entregan.** Sirven para aprender haciendo en el laboratorio, pero **los conceptos básicos y las órdenes principales de esas prácticas entran en la prueba teórico-práctica de cada unidad**. Lo único que se entrega son **dos prácticas integradoras**, una al final de cada trimestre, diseñadas para corregirse en pocos minutos.

| Trimestre | Práctica integradora | Unidades | Fecha (semipresencial) | Fecha (presencial) | RA |
|---|---|---|---|---|---|
| 1.º | [INT-1 · Servidor seguro de la clínica](#int-1--servidor-seguro-de-la-clínica) | UD01, UD02, UD03, UD04 | **viernes 27/11/2026** | viernes 15/01/2027 *(propuesta)* | RA1, RA2, RA3, RA6, RA7 |
| 2.º | [INT-2 · Perímetro y servicio sin parada](#int-2--perímetro-y-servicio-sin-parada) | UD05, UD06, UD07 | miércoles 10/02/2027 *(propuesta)* | viernes 30/04/2027 *(propuesta)* | RA2 a RA6 |

> [!NOTE]
> Las fechas dependen de dónde termine cada bloque en el [calendario](/guia/temporalizacion/) (presencial) o en la [guía semipresencial](/guia/semipresencial/). La de INT-1 semipresencial (27/11/2026) es la fijada para el curso; el resto son propuestas.

## Cómo funcionan (y por qué son fáciles de corregir)

Una práctica integradora no repite una práctica de unidad: **reúne en un mismo sistema lo aprendido** en varias unidades, el de la clínica [Mediterránea Dental](/guia/proyecto-clinica/). Para que corregirla lleve minutos y no horas:

1. **Una sola máquina (INT-1) o un laboratorio mínimo (INT-2).** Nombres, rutas y ficheros fijados en el enunciado.
2. **Un script de verificación** que lees y ejecutas tú: comprueba el sistema con órdenes reales y genera un fichero de **evidencias** con `[OK]` o `[FALLA]` en cada punto y una puntuación automática.
3. **Cuatro preguntas cortas** (`respuestas.md`) sobre los conceptos de las unidades. Cada una, de tres líneas como máximo.
4. **Se entregan solo dos ficheros por práctica:** el fichero de evidencias y `respuestas.md`. Nada de informes largos ni capturas.

| Parte | Puntos | Quién la corrige |
|---|--:|---|
| 16 comprobaciones automáticas (0,5 cada una) | 8,0 | El script (se contrasta leyendo el fichero) |
| 4 preguntas cortas (0,5 cada una) | 2,0 | El profesorado, en unos minutos con la [guía de corrección](/guia/correccion-integradoras/) |
| **Total** | **10,0** | |

### Dos formas de entregar

- **En Aules:** subes `evidencias-….txt` y `respuestas.md`.
- **En la tutoría o en clase:** ejecutas el script **delante del profesorado**, en tu máquina, y se corrige en el momento. Es la forma recomendada en la modalidad semipresencial.

### Reglas comunes

| Aspecto | Norma |
|---|---|
| Modalidad | Individual |
| Laboratorio | Solo máquinas virtuales propias. Nada de datos personales ni credenciales reales |
| Datos propios | El nombre de la CA lleva **tu apellido** (`CA-<apellido>`) y las contraseñas y claves son tuyas |
| Qué no se entrega | Claves privadas, contraseñas ni copias de la máquina |
| Retraso | Cada día lectivo de retraso resta un punto sobre diez, hasta un máximo de tres |
| Recuperación | Quien no entregue o no alcance 5 puntos repite una versión reducida antes de la evaluación |
| Honestidad | El fichero incluye el nombre de la máquina, su identificador y la fecha, y termina con una **firma** que detecta ediciones manuales. Dos entregas con el mismo identificador de máquina se revisan en directo |

> [!TIP]
> Ejecuta el script **desde el primer día** que tengas algo montado. Las líneas `[FALLA]` te dicen qué te falta (cada una trae una pista) y es la mejor forma de saber cuánto te queda. Puedes ejecutarlo tantas veces como quieras; solo cuenta la última.

---

## INT-1 · Servidor seguro de la clínica

{{< practica etiqueta="Práctica integradora" num="1" tipo="Proyecto" duracion="8 h · trabajo autónomo" nivel="3" ra="RA1: a,c,e,g;RA2: c,d,f;RA3: c;RA6: b,f" entorno="Debian 13 · VirtualBox 7" entregable="si" entrega="evidencias-INT1-<apellido>.txt + respuestas.md" >}}

### Objetivo

Dejar **un servidor de la clínica** diagnosticado, protegido frente a la pérdida de datos, con cifrado y fortificado. Reúne UD01 (riesgos), UD02 (RAID y copias), UD03 (PKI y HTTPS) y UD04 (bastionado).

### Contexto

La clínica guarda historiales clínicos (datos de salud, categoría especial del RGPD) en un servidor sin RAID, sin copias verificadas y con una intranet en HTTP. La dirección fija un **RPO de 4 horas y un RTO de 8 horas** para los ficheros clínicos y pide demostrar cómo quedaría el servidor bien hecho.

### Laboratorio

Una única máquina virtual **`srv-clinica`** (Debian 13, 2 CPU, 2 GB de RAM, red NAT) con **cinco discos adicionales de 1 GB**: `sdb`, `sdc`, `sdd` y `sde` para el RAID, y `sdf` para las copias. Haz una instantánea antes de cada fase.

### Qué debe existir (el script lo comprueba)

| Fase | Requisito | Práctica de referencia | ID |
|---|---|---|---|
| **A · UD01 Diagnóstico** | `/srv/int1/matriz-riesgos.csv` con la cabecera `activo,amenaza,probabilidad,impacto,riesgo,tratamiento`, **al menos 8 filas**, valores de 1 a 5 y `riesgo = probabilidad × impacto` (sin comas dentro de los textos) | [1.8](/ud01/ud01-practicas/) | A1 |
| | Política de contraseñas: `minlen = 12` o más en `/etc/security/pwquality.conf` | [1.4](/ud01/ud01-practicas/) | A3 |
| | `/srv/int1/SHA256SUMS` con el *hash* de la matriz, que debe verificar con `sha256sum -c` | [1.3](/ud01/ud01-practicas/) | A4 |
| **B · UD02 Datos** | **RAID 5** `/dev/md0` con **3 discos activos y 1 de reserva** | [2.2](/ud02/ud02-practicas/) | B1 |
| | `md0` montado en `/srv/datos` (entrada en `/etc/fstab`) con **al menos 5 ficheros** de datos ficticios | [2.2](/ud02/ud02-practicas/), [2.3](/ud02/ud02-practicas/) | B2 |
| | Repositorio **restic** en `/backup/repo` (disco `sdf` montado en `/backup`), contraseña en `/root/.restic-pass`, que pase `restic check` | [2.5](/ud02/ud02-practicas/) | B3 |
| | Una copia **posterior al último cambio** de los datos, que se pueda restaurar en otra ruta y sea **idéntica** | [2.5](/ud02/ud02-practicas/) | B4 |
| **C · UD03 Cifrado** | CA propia en `/etc/ssl/clinica/ca.crt` con `CN=CA-<apellido>` | [3.5](/ud03/ud03-practicas/) | C1 |
| | `/etc/ssl/clinica/servidor.crt` firmado por esa CA, con `subjectAltName` `DNS:intranet.clinica.lan` | [3.5](/ud03/ud03-practicas/) | C2 |
| | Nginx sirve `intranet.clinica.lan` en el puerto 443 con TLS 1.3 y cadena verificable | [3.6](/ud03/ud03-practicas/) | C3 |
| | Nginx con `ssl_protocols TLSv1.2 TLSv1.3;` | [3.6](/ud03/ud03-practicas/) | C4 |
| **D · UD04 Bastionado** | SSH con `PasswordAuthentication no`, `PubkeyAuthentication yes` y `PermitRootLogin no` | [4.3](/ud04/ud04-practicas/) | D1 |
| | UFW activo, entrada denegada por defecto y solo **22 y 443** permitidos | [4.4](/ud04/ud04-practicas/) | D2 |
| | Fail2ban activo con la *jail* `sshd` | [4.3](/ud04/ud04-practicas/) | D3 |
| | `auditd` activo con una regla sobre `/etc/passwd` o `/etc/shadow` | [4.7](/ud04/ud04-practicas/) | D4 |
| | Lynis: `/srv/int1/lynis-antes.dat` y `/srv/int1/lynis-despues.dat` (copia de `/var/log/lynis-report.dat` antes y después de fortificar), con **al menos 10 puntos de mejora** en `hardening_index` | [4.8](/ud04/ud04-practicas/) | D5 |

> [!WARNING]
> Haz la **primera ejecución de Lynis antes de fortificar** (UD04) y copia el informe a `lynis-antes.dat`. Si fortificas primero, no podrás demostrar la mejora.

### Ejecutar la verificación

Descarga el script (también está en Aules), cópialo a `srv-clinica` y ejecútalo con tu apellido:

```bash
chmod +x verifica-int1.sh          # permiso de ejecución
sudo ./verifica-int1.sh GARCIA     # sustituye GARCIA por tu apellido, sin tildes
```

El script **no cambia nada**: solo lee el estado del sistema. Genera `evidencias-INT1-GARCIA.txt`, con un resultado así:

```text
--- UD02 Proteccion de los datos
[OK]     B1  RAID 5 con 3 discos activos + 1 de reserva (md0)
[FALLA]  B4  Restauracion en otra ruta identica a /srv/datos   -> haz una copia NUEVA tras el ultimo cambio

PUNTOS_AUTO: 14/16  (cada comprobacion = 0,5 -> 7.0 de 8,0 puntos)
FIRMA: 17aaa111a4b6df46…
```

{{< descarga "descargas/verifica-int1.sh" >}}

### Preguntas cortas (`respuestas.md`)

Crea el fichero con este formato y responde a cada pregunta en **tres líneas como máximo**, con tus palabras:

```markdown
# INT-1 · Respuestas · <apellido>

**P1 (UD01).** ¿Qué riesgo de tu matriz tiene el valor más alto, qué salvaguarda has elegido y qué tipo de tratamiento es (mitigar, transferir, evitar o aceptar)?

**P2 (UD02).** ¿Cada cuánto haces copia para cumplir el RPO de 4 horas y cuánto tardó tu restauración de prueba frente al RTO de 8 horas?

**P3 (UD03).** Si un navegador no confía en el certificado de la intranet, ¿qué falta en ese equipo y por qué no se debe desactivar la comprobación?

**P4 (UD04).** Describe una medida de fortificación que hayas aplicado, la amenaza que reduce y la orden con la que lo has comprobado.
```

### Problemas habituales

- **El RAID no aparece tras reiniciar (B1/B2):** guarda la configuración con `mdadm --detail --scan` en `/etc/mdadm/mdadm.conf` y ejecuta `update-initramfs -u`.
- **B4 falla aunque la copia existe:** has cambiado datos después de la última copia. Haz una copia nueva y vuelve a ejecutar.
- **C3 falla pero el navegador funciona:** el script exige que el nombre `intranet.clinica.lan` esté en el `subjectAltName`, no solo en el `CN`.
- **D5 no puede comparar:** faltan los dos ficheros `.dat` o tienen otro nombre.

### Consideraciones de seguridad

Las claves privadas (`ca.key`, `servidor.key`) y la contraseña de restic **no se entregan**. Usa solo datos ficticios y trabaja siempre en tus máquinas virtuales.

---

## INT-2 · Perímetro y servicio sin parada

{{< practica etiqueta="Práctica integradora" num="2" tipo="Proyecto" duracion="8 h · trabajo autónomo" nivel="3" ra="RA2: c,d,i;RA3: c,d;RA4: b,c,d;RA5: b;RA6: c,d,e,g" entorno="Debian 13 · VirtualBox 7" entregable="si" entrega="evidencias-INT2-fw-<apellido>.txt + evidencias-INT2-lb-<apellido>.txt + respuestas.md" >}}

### Objetivo

Proteger el perímetro de la clínica y conseguir que su **web de citas siga funcionando cuando falla un servidor**. Reúne UD05 (detección), UD06 (cortafuegos, publicación y VPN) y UD07 (balanceo y prueba de fallo).

### Contexto

La clínica quiere abrir la web de citas a Internet y que dos personas teletrabajen. Requisitos de la dirección: política restrictiva en el cortafuegos, detección de escaneos y una web que **se recupere en menos de 5 minutos (RTO)** si cae un servidor.

### Laboratorio

Cuatro máquinas Debian 13 (haz una instantánea de cada una antes de empezar):

| Máquina | Red | Función |
|---|---|---|
| `fw01` | NAT (WAN) y red interna `dmz` | Cortafuegos con nftables, Suricata y WireGuard |
| `lb01` | `dmz` | Balanceador HAProxy con TLS |
| `web01`, `web02` | `dmz` | Servidores web que muestran su propio nombre (`web01`, `web02`) |
| `cli` (opcional) | NAT (WAN) | Cliente externo: genera tráfico de prueba y se conecta a la VPN |

### Qué debe existir (el script lo comprueba)

**En `fw01` (`sudo ./verifica-int2.sh fw APELLIDO`)**

| Unidad | Requisito | Práctica de referencia | ID |
|---|---|---|---|
| UD05 | Regla propia de Suricata en `/var/lib/suricata/rules/local.rules` con `sid` entre 1000000 y 1999999 | [5.3](/ud05/ud05-practicas/) | S1 |
| | Suricata activo y `suricata -T` correcto | [5.3](/ud05/ud05-practicas/) | S2 |
| | Al menos una alerta de una regla propia en `/var/log/suricata/fast.log` (genera tráfico desde `cli`) | [5.3](/ud05/ud05-practicas/) | S3 |
| UD06 | Cadena `input` con `policy drop` | [6.2](/ud06/ud06-practicas/) | F1 |
| | Cadena `forward` con `policy drop` | [6.2](/ud06/ud06-practicas/) | F2 |
| | Publicación de la web con `dnat` hacia `lb01` | [6.3](/ud06/ud06-practicas/) | F3 |
| | Salida de la DMZ con `masquerade` (o `snat`) | [6.3](/ud06/ud06-practicas/) | F4 |
| | WireGuard con un par que ha hecho *handshake* | [6.10](/ud06/ud06-practicas/) | F5 |
| | `ip_forward = 1`, `tcp_syncookies = 1` y `rp_filter` distinto de 0 | [6.4](/ud06/ud06-practicas/) | F6 |
| | Alguna regla registra con `log` | [6.4](/ud06/ud06-practicas/) | F7 |

**En `lb01` (`sudo ./verifica-int2.sh lb APELLIDO`)**

| Unidad | Requisito | Práctica de referencia | ID |
|---|---|---|---|
| UD07 | HAProxy activo y `haproxy -c` correcto | [7.4](/ud07/ud07-practicas/) | H1 |
| | Al menos **dos** líneas `server … check` en el *backend* | [7.4](/ud07/ud07-practicas/) | H2 |
| | Los dos servidores en estado **UP** ahora (requiere `socat` y el *stats socket* `/run/haproxy/admin.sock`) | [7.4](/ud07/ud07-practicas/) | H3 |
| | `/srv/int2/prueba-fallo.csv` con **al menos 2 fallos** recuperados en **300 s o menos** | [7.7](/ud07/ud07-practicas/) | H4 |
| | En 20 peticiones a `http://127.0.0.1/` responden `web01` y `web02` (el puerto 80 **reparte**, no redirige) | [7.4](/ud07/ud07-practicas/) | H5 |
| | HAProxy sirve HTTPS en el puerto 443 (en la 6.6 lo haces con Nginx; aquí, con `bind :443 ssl crt …` en HAProxy) | [6.6](/ud06/ud06-practicas/) | H6 |

### La prueba de fallo

Crea `/srv/int2/prueba-fallo.csv` con esta cabecera y **una fila por fallo provocado** (por ejemplo, parar `web01`, volver a arrancarlo y parar `web02`):

```text
componente,hora_fallo,hora_recuperacion,segundos
web01,10:02:15,10:02:19,4
web02,10:09:40,10:09:43,3
```

Para medir, deja este bucle en otra terminal mientras paras el servidor. `hora_fallo` es el instante en que ves el primer error y `hora_recuperacion` el primero que vuelve a dar `200`:

```bash
# Pide la web dos veces por segundo y muestra la hora y el código HTTP (Ctrl+C para parar)
while true; do echo "$(date +%T) $(curl -s -o /dev/null -w '%{http_code}' --max-time 1 http://127.0.0.1/)"; sleep 0.5; done
```

> [!NOTE]
> Con comprobaciones de salud, el balanceador retira el servidor caído en pocos segundos. Si **nunca ves errores**, anota una fila con `segundos` igual a `1`: el valor debe ser mayor que 0 y no superior a 300.

### Ejecutar la verificación y preguntas cortas

```bash
sudo ./verifica-int2.sh fw GARCIA      # en fw01  -> evidencias-INT2-fw-GARCIA.txt
sudo ./verifica-int2.sh lb GARCIA      # en lb01  -> evidencias-INT2-lb-GARCIA.txt
```

{{< descarga "descargas/verifica-int2.sh" >}}

```markdown
# INT-2 · Respuestas · <apellido>

**P1 (UD05).** ¿Qué tráfico detecta tu regla propia de Suricata y por qué un IDS, por sí solo, no lo bloquea?

**P2 (UD06).** ¿Qué hace `policy drop` en las cadenas `input` y `forward` y qué flujo has permitido expresamente?

**P3 (UD07).** ¿Qué RTO mediste en tu peor fallo y qué componente sigue siendo un punto único de fallo en tu arquitectura?

**P4 (UD05-UD07).** Indica un riesgo residual de tu infraestructura y una mejora concreta para reducirlo.
```

### Problemas habituales

- **H3 no funciona:** instala `socat` y añade `stats socket /run/haproxy/admin.sock mode 660 level admin` en la sección `global` (viene así por defecto en Debian).
- **H5 falla:** cada servidor web debe devolver su nombre (`web01` o `web02`) en la página, y HAProxy debe escuchar en el puerto 80 sin redirigir.
- **F5 falla:** WireGuard registra el *handshake* solo cuando hay tráfico; haz un `ping` por el túnel y vuelve a ejecutar.
- **S3 falla:** genera tráfico que cumpla la regla (por ejemplo, un `ping` o una petición a la URL de la regla) desde `cli` hacia la interfaz que vigila Suricata.

### Consideraciones de seguridad

No publiques claves privadas de WireGuard ni del certificado. Los escaneos y la generación de tráfico se hacen **solo** entre tus máquinas virtuales.

---

## Cómo contribuyen a la nota

> [!NOTE]
> La ponderación es una **propuesta** que debe concretar la programación didáctica del departamento. Es la misma en las modalidades presencial y semipresencial.

| Instrumento | Peso orientativo |
|---|--:|
| Pruebas teórico-prácticas de unidad (incluyen preguntas sobre los conceptos básicos y las órdenes de las prácticas) | 80 % |
| Prácticas integradoras: INT-1 (10 %) e INT-2 (10 %) | 20 % |
| Autoevaluaciones y cuestionarios en Aules | formativas (sin peso) |

Las **prácticas de cada unidad no puntúan ni se entregan**, pero su contenido básico forma parte de las pruebas. Las dos integradoras deben estar **entregadas y aprobadas** para superar el módulo.
