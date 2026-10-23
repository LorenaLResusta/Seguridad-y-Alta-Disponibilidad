---
title: "Prácticas integradoras obligatorias"
weight: 5
bookToc: true
---

# Prácticas integradoras obligatorias

> [!IMPORTANT]
> **En este módulo las prácticas de cada unidad no se entregan.** Sirven para aprender haciendo, pero **los conceptos básicos y las órdenes principales de esas prácticas entran en la prueba teórico-práctica de cada unidad**. Lo único que se entrega son **dos prácticas integradoras**, una al final de cada trimestre.
## Qué entregas, cuándo y cómo

| | **INT-1 · Servidor seguro** (1.er trimestre) | **INT-2 · Perímetro y servicio sin parada** (2.º trimestre) |
|---|---|---|
| Unidades | UD01, UD02, UD03, UD04 | UD05, UD06, UD07 |
| Fecha (semipresencial) | **viernes 27/11/2026** | **miércoles 03/02/2027** *(revisión, propuesta)*; examen de la 2.ª evaluación el 10/02/2027 |
| Fecha (presencial) | viernes 15/01/2027 *(propuesta)* | viernes 30/04/2027 *(propuesta)* |
| Prácticas | **1** máquina virtual: `srv-clinica` | **3** máquinas virtuales: `fw01`, `web01`, `web02` |
| Dedicación orientativa | unas 8 h | unas 5 h |
| Script que ejecutas | `sudo ./verifica-int1.sh APELLIDO` (en `srv-clinica`) | `sudo ./verifica-int2.sh APELLIDO` (solo en `fw01`) |
| **Entregas (2 ficheros)** | `evidencias-INT1-APELLIDO.txt` + `respuestas.md` | `evidencias-INT2-APELLIDO.txt` + `respuestas.md` |
| Puntuación | 16 comprobaciones × 0,5 = **8,0** + 4 preguntas × 0,5 = **2,0** | 10 comprobaciones × 0,8 = **8,0** + 4 preguntas × 0,5 = **2,0** |

Nada más: **ni informes, ni capturas, ni copias de máquinas, ni claves**. El fichero de evidencias lo genera el script; `respuestas.md` lo escribes tú (cuatro respuestas de tres líneas como máximo).

{{< explora "int-entrega" >}}

> [!NOTE]
> Las fechas dependen de dónde termine cada bloque en el [calendario](/guia/temporalizacion/) (presencial) o en la [guía semipresencial](/guia/semipresencial/). La de INT-1 semipresencial (27/11/2026) es la fijada para el curso; el resto son propuestas.

## Cómo funcionan (y por qué son fáciles de evaluar)

Una práctica integradora no repite una práctica de unidad: **reúne en un mismo sistema lo aprendido** en varias unidades, el de la clínica [Mediterránea Dental](/guia/proyecto-clinica/). Para que su evaluación lleve minutos y no horas:

1. **Nombres, rutas y ficheros fijados** en el enunciado.
2. **Un script de verificación** que lees y ejecutas tú: comprueba el sistema con órdenes reales y genera el fichero de **evidencias**, con `[OK]` o `[FALLA]` en cada punto y una puntuación automática.
3. **Cuatro preguntas cortas** sobre los conceptos de las unidades.
4. **Se ejecuta tantas veces como quieras:** solo cuenta la última.

### Dos formas de entregar

- **En Aules:** subes `evidencias-….txt` y `respuestas.md`.
- **En la tutoría o en clase:** ejecutas el script **delante del profesorado**, en tu máquina, y se evalúa en el momento. Es la forma recomendada en la modalidad semipresencial.

### Reglas comunes

| Aspecto | Norma |
|---|---|
| Modalidad | Individual |
| Prácticas | Solo máquinas virtuales propias. Nada de datos personales ni credenciales reales |
| Datos propios | El nombre de la CA lleva **tu apellido** (`CA-<apellido>`) y las contraseñas y claves son tuyas |
| Qué no se entrega | Claves privadas, contraseñas ni copias de la máquina |
| Retraso | Cada día lectivo de retraso resta un punto sobre diez, hasta un máximo de tres |
| Recuperación | Quien no entregue o no alcance 5 puntos repite una versión reducida antes de la evaluación |
| Honestidad | El fichero incluye el nombre de la máquina, un identificador de la máquina y la fecha, y termina con una **firma** (una suma de comprobación del contenido). La firma detecta errores y ediciones descuidadas, **no** una manipulación deliberada: por eso el profesorado puede pedirte repetir la ejecución **en directo**, y dos entregas con el mismo identificador de máquina se revisan siempre así |

> [!TIP]
> Ejecuta el script **desde el primer día** que tengas algo montado. Las líneas `[FALLA]` te dicen qué te falta (cada una trae una pista) y es la mejor forma de saber cuánto te queda.

---

## INT-1 · Servidor seguro de la clínica

{{< practica etiqueta="Práctica integradora" num="1" tipo="Proyecto" duracion="8 h · trabajo autónomo" nivel="3" ra="RA1: a,c,e,g;RA2: c,d,f;RA3: c;RA6: b,f;RA7: b" entorno="Debian 13 · VirtualBox 7" entregable="si" entrega="evidencias-INT1-<apellido>.txt + respuestas.md" >}}

### Objetivo

Dejar **un servidor de la clínica** diagnosticado, protegido frente a la pérdida de datos, con cifrado y fortificado. Reúne UD01 (riesgos), UD02 (RAID y copias), UD03 (PKI y HTTPS) y UD04 (bastionado). Es el mismo trabajo que hiciste en las prácticas de cada unidad, **juntado en una sola máquina** y con los nombres que fija este enunciado.

### Contexto

La clínica guarda historiales clínicos (datos de salud, categoría especial del RGPD) en un servidor sin RAID, sin copias verificadas y con una intranet en HTTP. La dirección fija un **RPO de 4 horas y un RTO de 8 horas** para los ficheros clínicos y pide demostrar cómo quedaría el servidor bien hecho.

### Prácticas

Una única máquina virtual **`srv-clinica`** (Debian 13, 2 CPU, 2 GB de RAM, red NAT) con **cinco discos adicionales de 1 GB**: `sdb`, `sdc`, `sdd` y `sde` para el RAID, y `sdf` para las copias. Haz una instantánea antes de cada fase.

### Qué debe existir (el script lo comprueba)

| Fase | Requisito | Práctica de referencia | ID |
|---|---|---|---|
| **A · UD01 Diagnóstico** | `/srv/int1/matriz-riesgos.csv` con la cabecera `activo,amenaza,probabilidad,impacto,riesgo,tratamiento`, **al menos 8 filas**, valores de 1 a 5 y `riesgo = probabilidad × impacto` (sin comas dentro de los textos) | [1.8](/ud01/ud01-practicas/) | A1 |
| | Política de contraseñas: `minlen = 12` o más en `/etc/security/pwquality.conf` (paquete `libpam-pwquality`) | [1.4](/ud01/ud01-practicas/) | A2 |
| | `/srv/int1/SHA256SUMS` con el *hash* de la matriz, que debe verificar con `sha256sum -c` | [1.3](/ud01/ud01-practicas/) | A3 |
| **B · UD02 Datos** | **RAID 5** `/dev/md0` con **3 discos activos y 1 de reserva** | [2.2](/ud02/ud02-practicas/) | B1 |
| | `md0` montado en `/srv/datos` (entrada en `/etc/fstab`) con **al menos 5 ficheros** de datos ficticios | [2.2](/ud02/ud02-practicas/), [2.3](/ud02/ud02-practicas/) | B2 |
| | Repositorio **restic** local en `/backup/repo` (disco `sdf` montado en `/backup`), contraseña en `/root/.restic-pass`, que pase `restic check` | [2.5](/ud02/ud02-practicas/) | B3 |
| | Una copia **posterior al último cambio** de los datos, que se pueda restaurar en otra ruta y sea **idéntica** | [2.5](/ud02/ud02-practicas/) | B4 |
| | Copias **programadas**: un temporizador de systemd (`.timer`) activo cuyo servicio ejecuta `restic`, con un intervalo máximo de **4 horas** (el RPO) | [2.5](/ud02/ud02-practicas/) | B5 |
| **C · UD03 Cifrado** | CA propia en `/etc/ssl/clinica/ca.crt` con `CN=CA-<apellido>` | [3.5](/ud03/ud03-practicas/) | C1 |
| | `/etc/ssl/clinica/servidor.crt` firmado por esa CA, con `subjectAltName` `DNS:intranet.clinica.lan` | [3.5](/ud03/ud03-practicas/) | C2 |
| | Nginx sirve `intranet.clinica.lan` en el puerto 443 con **TLS 1.3** y la cadena se verifica contra tu CA | [3.6](/ud03/ud03-practicas/) | C3 |
| **D · UD04 Bastionado** | SSH con `PasswordAuthentication no`, `PubkeyAuthentication yes` y `PermitRootLogin no` | [4.3](/ud04/ud04-practicas/) | D1 |
| | UFW activo, entrada denegada por defecto y **solo 22 y 443** permitidos | [4.4](/ud04/ud04-practicas/) | D2 |
| | Fail2ban activo con la *jail* `sshd` y `maxretry` de **3 o menos** | [4.3](/ud04/ud04-practicas/) | D3 |
| | `auditd` activo con una regla sobre `/etc/passwd` o `/etc/shadow` | [4.7](/ud04/ud04-practicas/) | D4 |
| | Lynis: `/srv/int1/lynis-antes.dat` y `/srv/int1/lynis-despues.dat` (copia de `/var/log/lynis-report.dat` antes y después de fortificar), con **al menos 10 puntos de mejora** en `hardening_index` | [4.8](/ud04/ud04-practicas/) | D5 |

> [!WARNING]
> Haz la **primera ejecución de Lynis antes de fortificar** (UD04) y copia el informe a `lynis-antes.dat`. Si fortificas primero, no podrás demostrar la mejora.

### Qué cambia respecto a las prácticas de cada unidad

Los nombres de la integradora son **fijos**; si has hecho las prácticas con otros, adáptalos:

| Aspecto | En la integradora |
|---|---|
| Nombre de la intranet | `intranet.clinica.lan` (en `/etc/hosts` de la máquina: `127.0.0.1 intranet.clinica.lan`) |
| Certificados | En `/etc/ssl/clinica/` (`ca.crt`, `servidor.crt`) |
| Copias | Repositorio restic **local** en `/backup/repo` (no uses repositorios remotos) |
| UFW | Debe permitir el **443** además del 22 (la intranet va por HTTPS) |
| Fail2ban | `maxretry = 3` en `/etc/fail2ban/jail.local` (el valor por defecto es 5) |
| Contraseñas | Instala `libpam-pwquality` antes de editar `pwquality.conf` |

### Prepara tu matriz de riesgos

Es la única parte que empieza «de cero». Usa este generador, copia el resultado a `/srv/int1/matriz-riesgos.csv` y calcula después su huella:

{{< explora "int1-matriz" >}}

### Ejecutar la verificación

Descarga el script (también está en Aules), cópialo a `srv-clinica` y ejecútalo con tu apellido:

```bash
chmod +x verifica-int1.sh          # permiso de ejecución
sudo ./verifica-int1.sh GARCIA     # sustituye GARCIA por tu apellido, sin tildes
```

El script **no cambia nada**: solo lee el estado del sistema (para la restauración de prueba crea una carpeta temporal en `/var/tmp` y la borra al terminar). Genera `evidencias-INT1-GARCIA.txt`, con un resultado así:

```text
--- UD02 Proteccion de los datos
[OK]     B1  RAID 5 con 3 discos activos + 1 de reserva (md0)
[FALLA]  B4  Restauracion en otra ruta identica a /srv/datos   -> haz una copia NUEVA tras el ultimo cambio

PUNTOS_AUTO: 15/16  (cada comprobacion = 0,5 -> 7.5 de 8,0 puntos)
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

Para entender la relación entre frecuencia de copia, RPO y RTO (pregunta P2), juega con este ejemplo:

{{< explora "rpo" >}}

### Problemas habituales

- **A1 falla con una matriz que parece correcta:** si la guardaste desde Excel, comprueba que el separador es la **coma** (no el punto y coma) y que no hay comas dentro de los textos. El script tolera el formato de Windows (BOM y saltos `CRLF`), pero avisa si ve `;`.
- **El RAID no aparece tras reiniciar (B1/B2):** guarda la configuración con `mdadm --detail --scan` en `/etc/mdadm/mdadm.conf` y ejecuta `update-initramfs -u`.
- **B4 falla aunque la copia existe:** has cambiado datos después de la última copia. Haz una copia nueva y vuelve a ejecutar.
- **B5 falla:** comprueba con `systemctl list-timers` que el temporizador está activo y que el servicio asociado ejecuta `restic backup`. Con `systemd-analyze calendar --iterations=6 "<tu OnCalendar>"` ves cuándo se dispararía.
- **C3 falla pero el navegador funciona:** el script exige que el nombre `intranet.clinica.lan` esté en el `subjectAltName`, no solo en el `CN`, y que la cadena verifique con tu `ca.crt`.
- **D2 falla:** si abriste más puertos de la cuenta (por ejemplo, el 80), ciérralos: la comprobación exige **solo** el 22 y el 443.
- **D5 no puede comparar:** faltan los dos ficheros `.dat` o tienen otro nombre.

### Consideraciones de seguridad

Las claves privadas (`ca.key`, `servidor.key`) y la contraseña de restic **no se entregan**. Usa solo datos ficticios y trabaja siempre en tus máquinas virtuales.

---

## INT-2 · Perímetro y servicio sin parada

{{< practica etiqueta="Práctica integradora" num="2" tipo="Proyecto" duracion="5 h · trabajo autónomo" nivel="3" ra="RA2: c,i;RA4: c,d;RA6: c,d,e,g" entorno="Debian 13 · VirtualBox 7" entregable="si" entrega="evidencias-INT2-<apellido>.txt + respuestas.md" >}}

### Objetivo

Proteger el perímetro de la clínica y comprobar que su **web de citas sigue funcionando cuando falla un servidor**. Una sola máquina, `fw01`, hace de cortafuegos, de sistema de detección y de balanceador; detrás hay dos servidores web. Reúne UD05 (detección), UD06 (cortafuegos y publicación) y UD07 (balanceo y prueba de fallo).

### Contexto

La clínica quiere abrir la web de citas a Internet. Requisitos de la dirección: **política restrictiva** en el cortafuegos, **detección** de tráfico sospechoso y una web que **se recupere en menos de 5 minutos (RTO)** si cae un servidor.

### Prácticas

Tres máquinas Debian 13. Es un entorno de prácticas **reducido** respecto a las prácticas de unidad (aquí `fw01` también hace de balanceador y no hay `lb01`). Haz una instantánea de cada una antes de empezar:

| Máquina | RAM | Red | Dirección | Función |
|---|--:|---|---|---|
| `fw01` | 2 GB | Adaptador 1: **Red NAT** `wan` (salida) · Adaptador 2: **red interna** `dmz` | WAN por DHCP · DMZ `172.16.0.1/24` | nftables, Suricata y HAProxy |
| `web01` | 512 MB | red interna `dmz` | `172.16.0.11/24` (puerta de enlace `172.16.0.1`) | Nginx con una página que dice `web01` |
| `web02` | 512 MB | red interna `dmz` | `172.16.0.12/24` (puerta de enlace `172.16.0.1`) | Nginx con una página que dice `web02` |

> [!NOTE]
> Con el tipo «NAT» de VirtualBox las máquinas **no se ven entre sí**; por eso la WAN de `fw01` es una *Red NAT* (se crea en *Herramientas → Redes → Redes NAT*) y la DMZ, una *red interna*. Los nombres de interfaz (`enp0s3` para la WAN y `enp0s8` para la DMZ en este ejemplo) los ves con `ip -br a`; si los tuyos son otros, cámbialos en los ficheros de abajo. **Instala los paquetes antes de aislar** `web01` y `web02` en la DMZ (o hazlo después, cuando `fw01` ya enmascare la salida).

Prepara las páginas de los servidores web (en cada uno, con su propio nombre):

```bash
sudo apt install -y nginx                          # servidor web
echo "web01" | sudo tee /var/www/html/index.html   # en web02, escribe web02
```

### Qué debe existir (el script lo comprueba)

Todo se comprueba **en `fw01`**, con un solo script y un solo fichero de evidencias.

| Unidad | Requisito | Práctica de referencia | ID |
|---|---|---|---|
| UD05 | Regla propia de Suricata en `/var/lib/suricata/rules/local.rules` (`sid` entre 1000000 y 1999999) y `local.rules` cargado en `suricata.yaml` | [5.3](/ud05/ud05-practicas/) | S1 |
| | Suricata activo y con **una alerta de tu regla** en `/var/log/suricata/fast.log` | [5.3](/ud05/ud05-practicas/) | S2 |
| UD06 | Cadena `input` con `policy drop` | [6.2](/ud06/ud06-practicas/) | F1 |
| | Cadena `forward` con `policy drop` | [6.2](/ud06/ud06-practicas/) | F2 |
| | Publicación de la web con `dnat` (o `redirect`) | [6.3](/ud06/ud06-practicas/) | F3 |
| | Salida de la DMZ con `masquerade` (o `snat`) | [6.3](/ud06/ud06-practicas/) | F4 |
| UD07 | HAProxy activo, `haproxy -c` correcto y **dos** líneas `server … check` | [7.4](/ud07/ud07-practicas/) | H1 |
| | Los dos servidores en estado **UP** ahora | [7.4](/ud07/ud07-practicas/) | H2 |
| | En 20 peticiones a `http://127.0.0.1/` responden `web01` **y** `web02` (reparto real) | [7.4](/ud07/ud07-practicas/) | H3 |
| | `/srv/int2/prueba-fallo.csv` con la caída de **`web01` y de `web02`**, cada una recuperada en **300 s o menos**, y HAProxy ha visto caer a los dos | [7.7](/ud07/ud07-practicas/) | H4 |

### Plan de trabajo y kit de ficheros

La práctica se puede hacer **por partes, sin esperar a la teoría de HAProxy**: esta guía trae la configuración completa. Plan sugerido para la modalidad semipresencial (la revisión es el miércoles 3 de febrero):

| Cuándo | Qué haces | Tiempo |
|---|---|--:|
| Semanas 18-19 (11-22 ene, UD6) | Prácticas (3 VM) y pasos 1 y 2: Suricata y nftables | 2 h |
| Semana 20 (25-29 ene, inicio de UD7) | Pasos 3 y 4: HAProxy y prueba de fallo | 2 h |
| Semana 21 (1-2 feb) | Ejecutas el script, resuelves los avisos `[FALLA]` y escribes `respuestas.md` | 1 h |
| **Miércoles 3 feb** | **Revisión** con el profesorado (o entrega en Aules) | |

Para no perder tiempo copiando texto, descarga los **tres ficheros ya preparados** (los mismos que ves en los pasos; cambia solo los nombres de interfaz si los tuyos son distintos y comprueba siempre la sintaxis antes de aplicar):

{{< descarga "descargas/int2-nftables.conf" >}}

{{< descarga "descargas/int2-haproxy.cfg" >}}

{{< descarga "descargas/int2-local.rules" >}}

### Paso 1 · Detección con Suricata (S1, S2)

Suricata vigila la **interfaz de la DMZ**. Instala, indica la interfaz y carga tus reglas propias:

```bash
sudo apt install -y suricata
sudo cp /etc/suricata/suricata.yaml /etc/suricata/suricata.yaml.bak     # copia de seguridad
ip -br a                                                                # confirma el nombre de la interfaz DMZ
```

En `/etc/suricata/suricata.yaml` ajusta (busca cada sección):

```yaml
af-packet:
  - interface: enp0s8          # la interfaz de la DMZ

rule-files:
  - suricata.rules
  - local.rules                # tus reglas propias
```

Crea tu regla (detecta cualquier ping; `sid` propio, sin comillas en el número):

```bash
echo 'alert icmp any any -> any any (msg:"INT2 ping detectado"; itype:8; sid:1000001; rev:1;)' \
  | sudo tee /var/lib/suricata/rules/local.rules
sudo suricata -T -c /etc/suricata/suricata.yaml    # -T: solo comprueba la configuración, no arranca
sudo systemctl restart suricata                    # reinicia el servicio para cargar los cambios
```

Prueba: desde `web01`, `ping -c 3 172.16.0.1` y, en `fw01`, `sudo tail /var/log/suricata/fast.log`. Debe aparecer una línea con `[1:1000001:1]`.

> [!NOTE]
> Suricata funciona aquí como **IDS**: avisa, pero no bloquea. Quien bloquea es nftables (paso 2).

### Paso 2 · Cortafuegos con nftables (F1–F4)

`fw01` reenvía tráfico entre la DMZ y la WAN, así que activa el reenvío IP de forma permanente:

```bash
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-forward.conf
sudo sysctl --system                               # aplica la configuración
```

Escribe `/etc/nftables.conf` (guarda antes la copia: `sudo cp /etc/nftables.conf /etc/nftables.conf.bak`):

```nft
#!/usr/sbin/nft -f
flush ruleset

define WAN = "enp0s3"
define DMZ = "enp0s8"

table inet filtro {
  chain entrada {
    type filter hook input priority filter; policy drop;
    ct state established,related accept          # respuestas de conexiones ya permitidas
    ct state invalid drop                        # paquetes que no encajan en ninguna conexión
    iif "lo" accept                              # tráfico local (imprescindible: el script usa 127.0.0.1)
    iifname $DMZ ip protocol icmp accept         # ping desde la DMZ
    tcp dport 22 accept                          # SSH (si lo quitas, pierdes el acceso)
    ct status dnat tcp dport 80 accept           # web publicada con DNAT
    iifname $DMZ tcp dport 80 accept             # HAProxy desde la DMZ
    log prefix "fw01-drop-in: " limit rate 5/minute
  }
  chain reenvio {
    type filter hook forward priority filter; policy drop;
    ct state established,related accept
    iifname $DMZ oifname $WAN tcp dport { 80, 443 } accept   # la DMZ solo sale por web
    iifname $DMZ oifname $WAN udp dport 53 accept             # y DNS
  }
}

table ip nat {
  chain prerouting {
    type nat hook prerouting priority dstnat; policy accept;
    iifname $WAN tcp dport 8080 dnat to 172.16.0.1:80        # puerto 8080 de la WAN -> HAProxy
  }
  chain postrouting {
    type nat hook postrouting priority srcnat; policy accept;
    oifname $WAN masquerade                                   # la DMZ sale con la IP de la WAN
  }
}
```

```bash
sudo nft -c -f /etc/nftables.conf        # -c: comprueba la sintaxis SIN aplicar
sudo nft -f /etc/nftables.conf           # aplica las reglas
sudo systemctl enable --now nftables     # las carga en cada arranque
sudo nft list ruleset                    # comprueba lo aplicado
```

> [!WARNING]
> Con `policy drop` y sin la regla del puerto 22 te quedas **sin acceso** a la máquina. Haz la instantánea antes y, si te equivocas, recupera el fichero con `sudo cp /etc/nftables.conf.bak /etc/nftables.conf`.

Prueba el flujo (para entender qué hace el cortafuegos con cada paquete, usa el simulador):

{{< explora "int2-paquete" >}}

### Paso 3 · Balanceo con HAProxy (H1–H3)

HAProxy reparte las peticiones entre `web01` y `web02` y **retira** del reparto el que no responde a la comprobación de salud (*health check*):

```bash
sudo apt install -y haproxy socat
sudo cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.bak
```

Sustituye el contenido de `/etc/haproxy/haproxy.cfg`:

```text
global
    log /dev/log local0
    stats socket /run/haproxy/admin.sock mode 660 level admin   # lo usa el script (socat)
    user haproxy
    group haproxy
    daemon

defaults
    mode http
    log global
    option httplog
    timeout connect 3s
    timeout client  30s
    timeout server  30s

frontend web
    bind :80
    default_backend webs

backend webs
    balance roundrobin                       # reparto por turnos
    option httpchk GET /                     # comprobación de salud: pide la página
    http-check expect status 200
    server web01 172.16.0.11:80 check inter 2s fall 3 rise 2
    server web02 172.16.0.12:80 check inter 2s fall 3 rise 2
```

`inter 2s fall 3 rise 2` significa: comprueba cada 2 s, marca el servidor como caído tras 3 fallos seguidos y como activo tras 2 aciertos. Por tanto, **la detección tarda como máximo `inter × fall` = 6 s**.

```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg   # comprueba la sintaxis
sudo systemctl restart haproxy
for i in 1 2 3 4; do curl -s http://127.0.0.1/; done    # debe alternar web01 y web02
```

### Paso 4 · La prueba de fallo (H4)

Esta es la parte central: **romper algo a propósito y medir cuánto tarda en recuperarse el servicio**. Juega primero con el simulador para ver qué ocurre y cómo se rellena el CSV:

{{< explora "int2-fallo" >}}

Ahora hazlo de verdad. En `fw01`, deja este bucle en una terminal (pide la web dos veces por segundo y muestra la hora y el código HTTP; `Ctrl+C` para parar):

```bash
while true; do echo "$(date +%T) $(curl -s -o /dev/null -w '%{http_code}' --max-time 1 http://127.0.0.1/)"; sleep 0.5; done
```

En otra terminal, **para el servidor** (en `web01`: `sudo systemctl stop nginx`) y observa. Con reparto por turnos verás errores `503` **intermitentes** hasta que HAProxy retira el servidor; después, todo `200`. Anota:

- `hora_fallo`: la hora del **primer error** (código distinto de 200).
- `hora_recuperacion`: la hora del **primer 200 a partir de la cual ya no hay más errores**.
- `segundos`: la diferencia (debe ser mayor que 0 y no superior a 300; si nunca ves errores, anota `1`).

Vuelve a arrancar el servidor (`sudo systemctl start nginx`), espera a que vuelva a estar **UP** y repite con el otro. Crea `/srv/int2/prueba-fallo.csv` (`sudo mkdir -p /srv/int2`) con **una fila por servidor**:

```text
componente,hora_fallo,hora_recuperacion,segundos
web01,10:02:15,10:02:21,6
web02,10:09:40,10:09:45,5
```

> [!WARNING]
> **No reinicies ni recargues HAProxy después de la prueba.** El script comprueba en el contador de HAProxy (`chkdown`, visible con `echo "show stat" | sudo socat stdio /run/haproxy/admin.sock`) que de verdad vio caer a los dos servidores; al reiniciar, el contador vuelve a cero. Deja además **los dos servidores arrancados** (H2 exige que estén UP).

### Ejecutar la verificación

```bash
chmod +x verifica-int2.sh
sudo ./verifica-int2.sh GARCIA      # en fw01 -> evidencias-INT2-GARCIA.txt
```

El fichero incluye además el dato `RTO_PEOR_MEDIDO`, que necesitarás para la pregunta P3.

{{< descarga "descargas/verifica-int2.sh" >}}

### Preguntas cortas (`respuestas.md`)

```markdown
# INT-2 · Respuestas · <apellido>

**P1 (UD05).** ¿Qué tráfico detecta tu regla de Suricata y por qué un IDS, por sí solo, no lo bloquea? ¿Qué cambiaría para que lo bloquease (IPS)?

**P2 (UD06).** ¿Qué hace `policy drop` en `input` y `forward` y qué flujo has permitido expresamente (y por qué ese y no otros)?

**P3 (UD07).** ¿Qué RTO mediste en tu peor fallo (`RTO_PEOR_MEDIDO`) y qué componente sigue siendo un punto único de fallo en tu arquitectura?

**P4 (UD05-UD07).** Indica un riesgo residual de tu infraestructura y una mejora concreta para reducirlo.
```

> [!TIP]
> Pista para P3: en estas prácticas hay dos servidores web, pero **un solo `fw01`** que hace de cortafuegos y de balanceador. ¿Qué pasa si cae?

### Problemas habituales

- **H2 o H4 no funcionan:** instala `socat` (`sudo apt install socat`) y comprueba que existe `/run/haproxy/admin.sock`; la línea `stats socket …` va en la sección `global`.
- **H3 falla:** cada servidor debe devolver su nombre (`web01` o `web02`) y HAProxy debe escuchar en el puerto 80 sin redirigir. Prueba cada uno con `curl http://172.16.0.11/`.
- **H4 falla con un CSV correcto:** has reiniciado HAProxy tras la prueba (el contador `chkdown` se ha puesto a cero). Repite la prueba de fallo y no lo toques.
- **S2 falla:** genera tráfico que cumpla la regla (un `ping` desde `web01` a `172.16.0.1`) y comprueba que la `interface` de `af-packet` es la de la DMZ. Si `fast.log` está vacío, `sudo systemctl status suricata` te dirá si arrancó.
- **F3 falla:** en una tabla `inet`, `nft` escribe `dnat ip to …`; el script lo acepta. Si pusiste la regla en otra tabla, revisa `nft list ruleset`.
- **Te quedas sin SSH:** falta `tcp dport 22 accept` en `input`. Entra por la consola de VirtualBox y restaura `/etc/nftables.conf.bak`.

### Consideraciones de seguridad

Genera tráfico y haz pruebas **solo** entre tus máquinas virtuales. La política restrictiva tiene un coste: todo lo que no abres deja de funcionar, así que abre solo lo necesario y verifica cada flujo.

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
