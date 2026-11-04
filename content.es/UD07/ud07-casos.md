---
title: "UD07 · Casos de ataque y defensa"
weight: 3
bookToc: true
---

# UD07 · Casos de ataque y defensa

{{< ra "RA6:a,d,e,f,g,h,i" >}}

La alta disponibilidad suele pensarse frente a **averías**: se cae un disco, un servidor o un balanceador y otro toma el relevo. Pero muchas interrupciones las causa un **ataque** o un **error humano**, y frente a ellos la redundancia no siempre ayuda: un ataque de denegación de servicio satura **todos** los nodos a la vez, y un borrado o un cifrado se **replica** al instante. En esta página lo compruebas en el entorno de prácticas de la unidad.

| Caso | Ataque o incidente | Caso real | Tipo |
|---|---|---|---|
| [7.A](#caso-7a--inundación-http-contra-el-balanceador) | Inundación HTTP (DDoS de capa 7) | *HTTP/2 Rapid Reset* (2023) | Entorno de prácticas |
| [7.B](#caso-7b--la-réplica-también-se-borra) | Borrado o cifrado que se replica | GitLab (2017), Ahold Delhaize (2024-2026) | Entorno de prácticas |
| [7.C](#caso-7c--secuestro-de-la-ip-virtual) | Suplantación de VRRP para robar la IP virtual | Riesgo de diseño de los protocolos de redundancia | Análisis + comprobación |
| [Búsqueda](#búsqueda-de-vulnerabilidades-en-la-pila-de-alta-disponibilidad) | Vulnerabilidades de HAProxy, Keepalived, MariaDB, Proxmox | — | Autónoma |

> [!IMPORTANT]
> Las pruebas de carga se lanzan **solo** desde `sad-cli` contra tu entorno de prácticas y con un número de peticiones limitado. Recuerda las [normas del entorno de prácticas](/ud01/ud01-casos/#antes-de-empezar-ética-y-legalidad-del-entorno-de-prácticas). Estos casos **no se entregan**.

### Entorno de prácticas común

Es el entorno de prácticas de las prácticas 7.3 a 7.6:

| VM | IP | Función |
|---|---|---|
| `lb01` / `lb02` | 192.168.100.51 / .52 | HAProxy + Keepalived |
| IP virtual | **192.168.100.50** | Punto de entrada único |
| `web01` / `web02` | 192.168.100.61 / .62 | Apache + PHP |
| `db01` / `db02` | 192.168.100.70 / .71 | MariaDB primaria y réplica |
| `sad-cli` | 192.168.100.10 (y .11 como «cliente legítimo») | Pruebas |

Haz una **instantánea** de todas las VM antes de empezar.

---

## Caso 7.A · Inundación HTTP contra el balanceador

{{< practica etiqueta="Caso" num="7.A" tipo="Guiada" duracion="1.5 h · trabajo autónomo" nivel="2" ra="RA6:a,e,h" entorno="Debian 13 · HAProxy 3.0 · ApacheBench" entrega="limitación por IP en HAProxy y medidas antes y después" >}}

### El caso real

En **octubre de 2023** Google, Cloudflare y Amazon revelaron que habían sufrido los mayores ataques DDoS de capa 7 conocidos hasta entonces, con picos de **cientos de millones de peticiones por segundo**. Usaban una técnica nueva, ***HTTP/2 Rapid Reset*** (**CVE-2023-44487**): el atacante abre una petición HTTP/2 y la cancela inmediatamente, miles de veces por conexión. El servidor trabaja en cada petición, pero el atacante apenas gasta recursos. Afectó a la mayoría de servidores y *proxies* web con HTTP/2 (Nginx, Apache, IIS, Envoy…), que publicaron parches y límites nuevos; HAProxy, en cambio, ya limitaba este comportamiento y no se vio afectado.

Un ataque de capa 7 no satura el enlace, sino la **CPU, los procesos o la base de datos**. Si el balanceador reparte el ataque entre `web01` y `web02`, **ambos** caen: la redundancia no protege si no se **filtra** antes.

### Ciclo del caso

| Fase | Descripción |
|---|---|
| **Vulnerabilidad** | El balanceador acepta cualquier volumen de peticiones de un mismo cliente y lo reparte a los servidores |
| **Ataque** | `ab` lanza miles de peticiones concurrentes desde una IP contra la IP virtual |
| **Detección** | Tasa de peticiones por IP en la tabla de HAProxy; tiempos de respuesta y errores 5xx en la página de estadísticas |
| **Mitigación** | Limitar la tasa de peticiones por IP en el balanceador (respuesta **429 Too Many Requests**); *timeouts* y `maxconn` ajustados; protección aguas arriba para ataques grandes |
| **Comprobación** | Durante el ataque, un cliente legítimo sigue obteniendo **200** en tiempo razonable |

{{< figura src="ud07/haproxy-rate-limit.svg" alt="Limitación por IP en HAProxy" caption="HAProxy responde 429 al atacante sin molestar a los servidores web." >}}

### 1. Línea base (desde `sad-cli`)

```bash
sudo apt install -y apache2-utils           # proporciona ab (ApacheBench)
sudo ip addr add 192.168.100.11/24 dev enp0s3
curl -s -o /dev/null --interface 192.168.100.11 -w 'HTTP %{http_code} en %{time_total} s\n' http://192.168.100.50/
```

### 2. El ataque

```bash
ab -n 20000 -c 200 -s 10 http://192.168.100.50/ | grep -E 'Complete requests|Failed requests|Non-2xx|Requests per second|Time per request'
```

- `-n 20000`: número **total** de peticiones (el ataque termina solo).
- `-c 200`: peticiones **simultáneas**.
- `-s 10`: segundos máximos de espera por respuesta.

Mientras dura, mide desde otra terminal el cliente legítimo y observa la [página de estadísticas](http://192.168.100.51:8404/stats) de HAProxy (columnas *Cur*, *Max* y *Rate* de las sesiones, y errores).

{{% details title="🎯 Resultado esperado" open=false %}}
Con una aplicación sencilla quizá aguanten los dos servidores, pero verás subir el tiempo de respuesta del cliente legítimo y la carga de `web01` y `web02` (`uptime` o `top` en cada uno). Con una aplicación que consulte la base de datos (la de la práctica 7.3), la degradación es mucho mayor: el cuello de botella suele ser la BD, que **no** está replicada para escritura.
{{% /details %}}

### 3. Mitigación: limitar la tasa por IP en HAProxy

HAProxy permite guardar contadores por cliente en una **tabla de seguimiento** (*stick table*). Edita `/etc/haproxy/haproxy.cfg` en **`lb01` y `lb02`** (la configuración debe ser idéntica en ambos: si cambia la IP virtual de nodo, la protección debe seguir activa).

En la sección `global`, añade un *socket* de administración para consultar la tabla:

```text
    stats socket /run/haproxy/admin.sock mode 660 level admin
```

Y sustituye el `frontend fe_web` por:

```text
frontend fe_web
    bind *:80
    # Tabla: una entrada por IP origen, guarda su tasa de peticiones en los últimos 10 s
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    # Si una IP supera 100 peticiones en 10 s, se le responde 429 sin molestar a los servidores
    http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }
    default_backend be_web
```

- `stick-table type ip size 100k expire 30s store http_req_rate(10s)`: hasta 100 000 IP; cada entrada caduca a los 30 s de inactividad y guarda la tasa de peticiones en una ventana de 10 s.
- `http-request track-sc0 src`: asocia cada petición a la entrada de su IP origen (contador *sc0*).
- `http-request deny deny_status 429 if { … gt 100 }`: si la tasa supera 100, HAProxy responde **429** él mismo.

```bash
sudo cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.antes-ddos
sudo haproxy -c -f /etc/haproxy/haproxy.cfg && sudo systemctl reload haproxy
```

> [!TIP]
> El umbral (100 peticiones en 10 s) depende de la aplicación: una página con muchas imágenes genera decenas de peticiones por visita. Mide primero el tráfico normal y deja margen. Si muchos usuarios llegan detrás de la misma IP (un aula, una empresa), valora umbrales más altos o identificar al cliente por otra cabecera.

### 4. Detección y comprobación

Repite el ataque y, a la vez, la medida del cliente legítimo. Después:

```bash
# En lb01: la IP del atacante y su tasa
echo "show table fe_web" | sudo socat stdio /run/haproxy/admin.sock
# Número de respuestas 429 en el registro
sudo journalctl -u haproxy --since "10 min ago" | grep -c ' 429 '
```

(`socat` se instala con `sudo apt install -y socat`.)

| Medida | Sin limitación | Con limitación |
|---|---|---|
| `Non-2xx responses` en `ab` | | |
| Tiempo de respuesta del cliente legítimo | | |
| Carga de `web01` / `web02` durante el ataque | | |

{{% details title="🎯 Resultado esperado" open=false %}}
Con la limitación, `ab` muestra miles de `Non-2xx responses` (los 429), la entrada de 192.168.100.10 aparece en la tabla con `http_req_rate(10000)` muy por encima de 100 y la carga de los servidores web apenas sube. El cliente legítimo (192.168.100.11) sigue recibiendo `HTTP 200` con tiempos normales: el balanceador **absorbe** el ataque antes de que llegue a los nodos.
{{% /details %}}

**Prueba de fallo combinada**: con el ataque en marcha, detén HAProxy en `lb01` (`sudo systemctl stop haproxy`). Keepalived mueve la IP virtual a `lb02`. ¿Sigue limitado el atacante? Si no lo está, revisa que `lb02` tenga la misma configuración. Al terminar, vuelve a arrancar HAProxy en `lb01`.

### Variantes: Linux, Windows 11 y web

{{< tabs >}}
{{% tab "Linux" %}}
`ab -n 20000 -c 200 http://192.168.100.50/` y `stick-table` en HAProxy.
{{% /tab %}}
{{% tab "Windows 11" %}}
Abre **PowerShell** (`Win` + `X` → *Terminal*; para lo que pida administrador, *Terminal (administrador)*).

Con **PowerShell 7** (`winget install --id Microsoft.PowerShell`) puedes generar carga paralela **contra tu entorno de prácticas**, sin instalar nada más:

```powershell
# 2000 peticiones, 100 a la vez. SOLO contra la IP virtual del entorno de prácticas
1..2000 | ForEach-Object -Parallel {
    try { (Invoke-WebRequest -Uri http://192.168.100.50/ -SkipHttpErrorCheck -TimeoutSec 10).StatusCode } catch { 0 }
} -ThrottleLimit 100 | Group-Object | Select-Object Count, Name | Sort-Object Count -Descending
```

El resultado agrupa los códigos HTTP: con la limitación de HAProxy activa verás muchos `429`; sin ella, `200` o tiempos de espera (`0`). Mide el cliente legítimo con `Measure-Command { Invoke-WebRequest http://192.168.100.50/ }`.
{{% /tab %}}
{{% tab "Web" %}}
Si publicas un sitio detrás de un servicio como **Cloudflare**, la limitación de peticiones se configura sin tocar el servidor: *Seguridad → WAF → Reglas de limitación de velocidad* (por IP, por ruta, con acción de bloqueo o *challenge*). Es la misma idea que `http-request deny deny_status 429` de HAProxy, aplicada **aguas arriba**, que es donde se frenan los ataques grandes.
{{% /tab %}}
{{< /tabs >}}

---

## Caso 7.B · La réplica también se borra

{{< practica etiqueta="Caso" num="7.B" tipo="Guiada" duracion="1.5 h · trabajo autónomo" nivel="3" ra="RA6:a,d,f,i" entorno="Debian 13 · MariaDB 11 (réplica de la práctica 7.6)" entrega="réplica retardada y recuperación tras un borrado" >}}

### Los casos reales

- **GitLab (enero de 2017).** Durante una incidencia de rendimiento, un administrador ejecutó por error un borrado del directorio de datos en la base de datos **principal** en lugar de en la réplica. Se perdieron unos 300 GB. Al intentar recuperar, descubrieron que varios de sus mecanismos de copia **no funcionaban** desde hacía tiempo. Restauraron desde una instantánea de seis horas antes y lo contaron todo en un informe público, que hoy es un clásico.
- **Ahold Delhaize / Albert Heijn (2024 y 2026).** Ante un incidente de *ransomware*, el grupo **desconectó sistemas** de forma preventiva. Las tiendas siguieron abiertas y cobrando porque esos sistemas funcionan de forma **independiente** de los centrales: un ejemplo de **modo degradado** planificado.

La lección: **alta disponibilidad no es copia de seguridad**. La replicación copia los cambios… también los malos: un `DROP TABLE`, un `DELETE` sin `WHERE` o el cifrado de un *ransomware* llegan a la réplica en milisegundos.

### Ciclo del caso

| Fase | Descripción |
|---|---|
| **Vulnerabilidad** | Réplica síncrona o casi síncrona como única «protección» de los datos |
| **Ataque / incidente** | Un atacante con acceso a la aplicación (o un error humano) ejecuta `DROP TABLE` en `db01` |
| **Detección** | Errores de la aplicación; `Seconds_Behind_Master` y el registro binario muestran la sentencia |
| **Mitigación** | **Réplica retardada** (`MASTER_DELAY`) que da margen para reaccionar; copias de seguridad independientes; registro binario para recuperación a un punto en el tiempo |
| **Comprobación** | Recuperar la tabla desde la réplica retardada antes de que aplique el borrado |

{{< figura src="ud07/replica-retardada.svg" alt="Réplica retardada" caption="La réplica retardada deja una ventana para detener la réplica antes de aplicar el desastre." >}}

### 1. Comprobar el problema

Con la réplica de la práctica 7.6 funcionando:

```bash
# db01
sudo mariadb -e "SELECT * FROM tienda.visitas;"
sudo mariadb -e "DROP TABLE tienda.visitas;"           # el «ataque»
# db02 (inmediatamente)
sudo mariadb -e "SELECT * FROM tienda.visitas;"         # ERROR 1146: Table 'tienda.visitas' doesn't exist
```

La réplica ha hecho **exactamente su trabajo**: copiar el cambio. Restaura la tabla (vuelve a crearla como en la práctica 7.3, o restaura las instantáneas) antes de seguir.

### 2. Mitigación: réplica retardada

Una **réplica retardada** aplica los cambios con un retraso fijo. No sirve para el *failover* inmediato, pero da un margen para detener la réplica antes de que aplique un desastre. En producción se usa una **tercera** máquina para esto; en el entorno de prácticas la configuramos en `db02` (perderás temporalmente la réplica «al día»).

```bash
# db02
sudo mariadb <<'SQL'
STOP REPLICA;
CHANGE MASTER TO MASTER_DELAY = 600;      -- 10 minutos de retraso
START REPLICA;
SQL
sudo mariadb -e "SHOW REPLICA STATUS\G" | grep -E 'SQL_Delay|Slave_SQL_Running_State|Seconds_Behind_Master'
```

`SQL_Delay: 600` confirma el retraso. El hilo de E/S sigue **descargando** los cambios de `db01` (no se pierden), pero el hilo SQL espera 10 minutos antes de **aplicarlos**.

### 3. Repetir el incidente y recuperar

```bash
# db01
sudo mariadb -e "UPDATE tienda.visitas SET total = total + 1 WHERE id=1;"   # cambio legítimo
sudo mariadb -e "DROP TABLE tienda.visitas;"                                 # incidente
```

Tienes 10 minutos. En `db02`:

```bash
sudo mariadb -e "STOP REPLICA SQL_THREAD;"                       # 1. congela la réplica ANTES de que aplique el DROP
sudo mariadb -e "SELECT * FROM tienda.visitas;"                  # 2. la tabla sigue aquí
sudo mariadb-dump --single-transaction tienda visitas > /root/visitas-rescate.sql   # 3. rescátala
```

Copia el fichero a `db01` y restaura:

```bash
scp /root/visitas-rescate.sql usuario@192.168.100.70:/tmp/
# db01
sudo mariadb tienda < /tmp/visitas-rescate.sql
sudo mariadb -e "SELECT * FROM tienda.visitas;"
```

{{% details title="🎯 Resultado esperado y reflexión" open=false %}}
La tabla vuelve a `db01`, pero **sin** el último cambio legítimo (el `UPDATE` de justo antes del `DROP`), porque la réplica retardada aún no lo había aplicado. Recuperarlo exige reproducir el registro binario de `db01` hasta la posición anterior al `DROP` (recuperación a un punto en el tiempo, PITR), por ejemplo localizándolo con `sudo mariadb-binlog --base64-output=decode-rows -v /var/log/mysql/mariadb-bin.0000NN | grep -n -i "drop table"`.

Relación con los conceptos de la unidad: la réplica retardada mejora el **RPO** frente a errores lógicos (no pierdes la tabla), pero empeora el **RTO** de un *failover* (la réplica va 10 minutos por detrás). Por eso se usan **ambas**: una réplica al día para disponibilidad y otra retardada (o copias frecuentes) para recuperación.
{{% /details %}}

### 4. Vuelta a la normalidad

`db02` tiene ahora el `DROP` pendiente en su cola. Para devolverla a su papel normal, la forma más limpia es **reconstruirla** a partir de una copia consistente de `db01` (como en la nota de la práctica 7.6) y volver a configurarla con `MASTER_DELAY = 0`. O, más rápido, restaurar las instantáneas.

### Preguntas de análisis

1. Completa la frase: «La replicación protege frente a ______; la copia de seguridad protege frente a ______».
2. ¿Por qué el *ransomware* moderno intenta cifrar **también** los servidores de virtualización (como Proxmox o VMware ESXi) y no solo las máquinas virtuales? Relaciónalo con el [caso 2.A](/ud02/ud02-casos/#caso-2a--el-ransomware-que-borra-las-copias).
3. Diseña el **modo degradado** de la Librería Pilar: si la tienda *online* cae, ¿qué sigue funcionando y cómo?

### Variantes: Linux, Windows 11 y web

{{< tabs >}}
{{% tab "Linux" %}}
Réplica retardada con `MASTER_DELAY` en MariaDB, y `mariadb-binlog` para recuperar.
{{% /tab %}}
{{% tab "Windows 11" %}}
Abre **PowerShell** (`Win` + `X` → *Terminal*; para lo que pida administrador, *Terminal (administrador)*).

En Windows 11 Pro con **Hyper-V** (las VM del entorno de prácticas) tienes estas protecciones, que **no sustituyen a una copia de seguridad**:

```powershell
# Punto de control (instantánea) antes de una operación peligrosa
Checkpoint-VM -Name db01 -SnapshotName "antes-de-borrar"
Get-VMCheckpoint -VMName db01

# Réplica de Hyper-V con puntos de recuperación adicionales (hasta 24): permite volver atrás aunque la réplica ya haya copiado el borrado
Set-VMReplication -VMName db01 -RecoveryHistory 24
Get-VMReplication -VMName db01 | Select-Object VMName, State, RecoveryHistory   # (si la réplica está configurada)
```

El principio es el mismo que con `MASTER_DELAY`: tener **varios puntos en el tiempo** a los que volver, no solo la copia más reciente.
{{% /tab %}}
{{% tab "Web" %}}
Lee el **[informe público de GitLab (2017)](https://about.gitlab.com/blog/2017/02/10/postmortem-of-database-outage-of-january-31/)**: es un modelo de cómo documentar un incidente (cronología, causas, qué funcionó y qué no, acciones). Haz un resumen de una página con ese mismo esquema para el borrado del caso.
{{% /tab %}}
{{< /tabs >}}

---

## Caso 7.C · Secuestro de la IP virtual

{{< practica etiqueta="Caso" num="7.C" tipo="Reto" duracion="1 h · trabajo autónomo" nivel="3" ra="RA6:d,g" entorno="Debian 13 · Keepalived · tcpdump · nftables" entrega="análisis del riesgo y filtrado de VRRP" >}}

### El riesgo

Keepalived usa **VRRP** (*Virtual Router Redundancy Protocol*): el nodo maestro anuncia cada segundo «tengo la IP virtual, con prioridad 150». Si otro equipo anuncia una prioridad **mayor** para el mismo grupo (`virtual_router_id`), los demás le ceden la IP virtual. Un atacante en la misma red podría hacerlo y quedarse con todo el tráfico de los clientes: una **denegación de servicio** o un **ataque de intermediario** contra el servicio de alta disponibilidad.

La autenticación `auth_type PASS` de la práctica 7.5 **no lo impide**: en VRRP versión 2 la contraseña viaja **en claro** en cada anuncio, y la especificación de VRRP versión 3 (RFC 5798) eliminó la autenticación porque no aportaba seguridad real.

### 1. Comprobación: la contraseña viaja en claro (en `lb02`)

```bash
sudo tcpdump -i enp0s3 -n -c 3 -v 'ip proto 112'          # 112 = VRRP
```

{{% details title="🎯 Resultado esperado" open=false %}}
Cada línea muestra el anuncio de `lb01` con `vrid 51, prio 150, authtype simple, intvl 1s` y la contraseña `auth "Lab2627x"` legible. Cualquiera que vea este tráfico conoce la «clave».
{{% /details %}}

### 2. Mitigación

1. **Unidifusión entre pares conocidos** (ya configurada en la práctica 7.5 con `unicast_peer`): los anuncios no se difunden a toda la red.
2. **Filtrar VRRP en cada balanceador**: solo se acepta VRRP del otro nodo. En `lb01` (en `lb02`, con la IP de `lb01`), añade a la cadena `input` de su nftables:

```text
    ip protocol vrrp ip saddr != 192.168.100.52 counter drop      # VRRP solo desde lb02
```

3. **Red dedicada**: en producción, el tráfico VRRP y de *heartbeat* va por una **VLAN o enlace exclusivo** entre los balanceadores, donde no hay equipos de usuarios.
4. **Monitorizar** los cambios de estado de Keepalived (`journalctl -u keepalived | grep -E 'MASTER|BACKUP'`): una transición que no coincide con una avería es una alerta.

### 3. Reto (opcional, solo con instantáneas)

Con una tercera VM en la misma red, configura Keepalived con el mismo `virtual_router_id 51`, la misma contraseña y `priority 200`, **sin** `unicast_peer` y, después, con `unicast_peer` apuntando a `lb01`. Comprueba en cada caso si consigue la IP virtual (`ip -br a` y `journalctl -u keepalived` en los tres equipos) y repite con el filtro de nftables activo. Documenta qué medida lo impide.

---

## Búsqueda de vulnerabilidades en la pila de alta disponibilidad

{{< practica etiqueta="Búsqueda" num="7.D" tipo="Autónoma" duracion="1 h · trabajo autónomo" nivel="1" ra="RA6:h,i" entorno="Navegador · Debian 13" entrega="tabla de vulnerabilidades" >}}

1. Busca **CVE-2023-44487** (*HTTP/2 Rapid Reset*) en NVD y en INCIBE-CERT. ¿A qué productos afectaba? ¿Por qué HAProxy no se vio afectado? ¿Y el Nginx de la UD06 (comprueba qué versiones lo corrigieron y compáralo con `nginx -v`)?
2. Completa la tabla con la última vulnerabilidad relevante de cada componente:

| Componente | Versión (`orden`) | CVE | Tipo de impacto (C/I/D) | ¿Corregido en Debian 13? |
|---|---|---|---|---|
| HAProxy | `haproxy -v` | | | |
| Keepalived | `keepalived --version` | | | |
| MariaDB | `mariadb --version` | | | |
| Pacemaker / Corosync | `pacemakerd --version` | | | |
| Proxmox VE (si hiciste 7.9) | `pveversion` | | | |

3. Explica por qué una vulnerabilidad de **denegación de servicio** (impacto solo en disponibilidad, `A:H` en CVSS) es especialmente grave en un balanceador o en el gestor de un clúster.
4. Busca en el catálogo KEV vulnerabilidades de **VMware ESXi** usadas en campañas de *ransomware*. ¿Qué te dice sobre la importancia de proteger la capa de virtualización en una solución de alta disponibilidad?

---

## Qué debes saber explicar

- Por qué un DDoS de capa 7 afecta a todos los nodos de un clúster y cómo se limita en el balanceador (respuestas 429, tablas por IP).
- Por qué **alta disponibilidad no es copia de seguridad** y para qué sirve una réplica retardada (relación con RPO y RTO).
- Qué es el **modo degradado** de un servicio y por qué se planifica.
- Por qué VRRP debe aislarse o filtrarse y por qué su autenticación no es una medida de seguridad.

## Referencias

- HAProxy. [Configuration Manual: stick-table, track-sc, sc_http_req_rate](https://docs.haproxy.org/3.0/configuration.html) y [HAProxy and HTTP/2 Rapid Reset](https://www.haproxy.com/blog/haproxy-is-not-affected-by-the-http-2-rapid-reset-attack-cve-2023-44487).
- NVD. [CVE-2023-44487](https://nvd.nist.gov/vuln/detail/CVE-2023-44487).
- MariaDB. [Delayed Replication](https://mariadb.com/kb/en/delayed-replication/) y [mariadb-binlog](https://mariadb.com/kb/en/mariadb-binlog/).
- GitLab (2017). [Postmortem of database outage of January 31](https://about.gitlab.com/blog/2017/02/10/postmortem-of-database-outage-of-january-31/).
- IETF. [RFC 5798: Virtual Router Redundancy Protocol (VRRP) Version 3](https://www.rfc-editor.org/rfc/rfc5798).
- Keepalived. [Documentación oficial](https://keepalived.readthedocs.io/).
