---
title: "Prácticas"
slug: "practicas"
weight: 2
---

# UD5. Prácticas: alta disponibilidad

> Cálculo de disponibilidad, RAID 1 con fallo de disco, servicio web de dos nodos con base de datos, balanceo con HAProxy, IP virtual con Keepalived, replicación de MariaDB, pruebas de carga y de fallo, y diseño de un clúster (Pacemaker y Proxmox).

| Datos de las prácticas | Información |
| --- | --- |
| Módulo | 0378. Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR |
| Duración estimada | 10 horas |
| Entorno | Red `SAD-NAT` (192.168.100.0/24) en VirtualBox, VMs Debian 13 (AlmaLinux 10 donde se indica) |
| Teoría asociada | [Teoría de la UD5](../teoria/) |

---

## 1. Objetivos

- Calcular la disponibilidad y el tiempo de parada de una arquitectura, y localizar sus SPOF.
- Montar un **RAID 1** y comprobar que sobrevive al fallo de un disco.
- Desplegar una aplicación web en dos nodos con una base de datos independiente.
- Configurar **HAProxy** con comprobaciones de salud y observar cómo retira un servidor caído.
- Duplicar el balanceador con **Keepalived** y una IP virtual, y probar la conmutación.
- Replicar una base de datos **MariaDB** y promocionar la réplica.
- Medir el efecto de un fallo bajo carga y registrar el tiempo de interrupción.
- Interpretar un clúster Pacemaker/Corosync y la HA de Proxmox VE.

> [!IMPORTANT]
> **Cada práctica termina con una prueba de fallo.** El objetivo no es que el servicio funcione, sino comprobar **qué ocurre cuando algo deja de funcionar** y cuánto tarda en recuperarse. Anota siempre la hora del fallo y de la recuperación.

---

## 2. Preparación del laboratorio

### 2.1. Máquinas y direcciones

Todas las máquinas están en la red `SAD-NAT`. Crea las que vayas a usar (puedes clonar una plantilla Debian 13 mínima con SSH). Cada una necesita 1 vCPU y 1 GiB de RAM (2 GiB para `db01`/`db02`).

| VM | Nombre | IP | Función |
| --- | --- | --- | --- |
| Balanceador 1 | `lb01` | 192.168.100.51 | HAProxy + Keepalived (MASTER) |
| Balanceador 2 | `lb02` | 192.168.100.52 | HAProxy + Keepalived (BACKUP) |
| IP virtual | — | **192.168.100.50** | Punto de entrada único |
| Web 1 | `web01` | 192.168.100.61 | Apache + PHP |
| Web 2 | `web02` | 192.168.100.62 | Apache + PHP |
| BD primaria | `db01` | 192.168.100.70 | MariaDB |
| BD réplica | `db02` | 192.168.100.71 | MariaDB (práctica 6) |
| Cliente | `sad-cli` | 192.168.100.10 | Pruebas |

Si dispones de poca RAM, empieza con `lb01`, `web01`, `web02` y `db01` (prácticas 3 y 4) y añade las demás después.

### 2.2. Configuración común (en todas las VM)

```bash
sudo hostnamectl set-hostname web01                 # el nombre que corresponda a cada VM
sudo tee -a /etc/hosts >/dev/null <<'EOF'
192.168.100.51 lb01
192.168.100.52 lb02
192.168.100.61 web01
192.168.100.62 web02
192.168.100.70 db01
192.168.100.71 db02
EOF
getent hosts web01 db01         # comprueba la resolución de nombres
ping -c 2 192.168.100.70        # y la conectividad entre máquinas
```

Instala las herramientas comunes y crea una *snapshot* `ud5-inicio` de cada VM:

```bash
sudo apt update && sudo apt install -y curl net-tools tcpdump       # AlmaLinux: sudo dnf install -y curl net-tools tcpdump
mkdir -p ~/ud5-evidencias && chmod 700 ~/ud5-evidencias
```

### 2.3. Puertos que deben estar abiertos

Si usas cortafuegos en las VM (UD4), abre solo lo necesario:

| Máquina | Puerto | Para qué |
| --- | --- | --- |
| `web01`, `web02` | 80/tcp desde `lb01`, `lb02` | HTTP desde los balanceadores |
| `db01`, `db02` | 3306/tcp desde `web01`, `web02` y desde `db02`/`db01` | MySQL y replicación |
| `lb01`, `lb02` | 80/tcp, 8404/tcp (solo admin), protocolo 112 entre ellos | Web, estadísticas, VRRP |

---

## 3. Práctica 1 · Diagnóstico y cálculo de disponibilidad

**Objetivo:** localizar SPOF y cuantificar el efecto de la redundancia (RA6 a, i).

1. Dibuja la cadena de dependencias de una web: **cliente → router → firewall → switch → servidor web → base de datos → disco**. Identifica **al menos cinco SPOF** y propón para cada uno una medida proporcionada.
2. Guarda el script `disp.py` de la teoría y ejecútalo:

```bash
python3 disp.py | tee ~/ud5-evidencias/01-disponibilidad.txt
```

3. Modifica el script para calcular estos casos y anota los resultados:

| Caso | Disponibilidad | Parada anual |
| --- | --- | --- |
| Router 99,9 % + firewall 99,9 % + servidor 99,5 % en serie | | |
| Igual, con dos servidores en paralelo | | |
| Igual, con router y firewall también duplicados | | |
| MTBF = 8 760 h y MTTR = 4 h | | |
| El mismo, con conmutación automática (MTTR = 30 s) | | |

4. Define **RPO** y **RTO** realistas para una web de comercio electrónico pequeña y justifica la decisión.

**Comprobación:** ¿qué conclusión sacas sobre dónde invertir primero? (pista: el eslabón más débil de la cadena en serie).

---

## 4. Práctica 2 · RAID 1 y fallo de un disco

**Objetivo:** comprobar la tolerancia a fallos de disco y que RAID no es una copia de seguridad (RA6 b, f). En `web01` o en una VM aparte. Se usan ficheros como discos.

```bash
sudo apt install -y mdadm                           # AlmaLinux: sudo dnf install -y mdadm
cd /root
sudo truncate -s 200M disco1.img disco2.img disco3.img
D1=$(sudo losetup -f --show disco1.img); D2=$(sudo losetup -f --show disco2.img); D3=$(sudo losetup -f --show disco3.img)
echo "$D1 $D2 $D3"                                  # p. ej. /dev/loop0 /dev/loop1 /dev/loop2
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 --run $D1 $D2
cat /proc/mdstat | tee ~/ud5-evidencias/02-raid-inicial.txt    # [UU]
sudo mkfs.ext4 /dev/md0 && sudo mkdir -p /mnt/raid && sudo mount /dev/md0 /mnt/raid
echo "informe-$(date +%s)" | sudo tee /mnt/raid/dato.txt
```

**Prueba de fallo 1: se estropea un disco**

```bash
sudo mdadm /dev/md0 --fail $D2
cat /proc/mdstat                          # [U_] -> degradado
cat /mnt/raid/dato.txt                    # el servicio sigue: los datos siguen accesibles
sudo mdadm --detail /dev/md0 | tee ~/ud5-evidencias/02-raid-degradado.txt
sudo mdadm /dev/md0 --remove $D2
sudo mdadm /dev/md0 --add $D3             # disco de repuesto
watch -n1 cat /proc/mdstat                # observa la reconstrucción (Ctrl+C para salir) hasta [UU]
```

**Prueba de fallo 2: RAID NO protege de un borrado**

```bash
sudo rm /mnt/raid/dato.txt
ls /mnt/raid                              # el fichero ha desaparecido de AMBOS discos
```

**Preguntas para el informe:** ¿cuántos fallos de disco tolera RAID 1 con 2 discos? ¿Qué necesitarías para recuperar `dato.txt`? (Pista: UD2.) ¿Qué comando muestra que hay un disco degradado y cómo lo monitorizarías?

Limpieza:

```bash
sudo umount /mnt/raid && sudo mdadm --stop /dev/md0 && sudo losetup -D && sudo rm -f /root/disco?.img
```

---

## 5. Práctica 3 · Servicio web de dos nodos con base de datos

**Objetivo:** construir la aplicación que luego se hará redundante. La aplicación es una página PHP que muestra **qué servidor responde** y cuenta las visitas en la base de datos, de modo que se vea el estado compartido.

### 5.1. Base de datos en `db01`

```bash
sudo apt install -y mariadb-server                  # AlmaLinux: sudo dnf install -y mariadb-server
sudo systemctl enable --now mariadb
sudo mariadb-secure-installation                    # contraseña de root, sin usuarios anónimos ni acceso remoto de root
```

Configura la escucha en la IP interna (Debian: `/etc/mysql/mariadb.conf.d/60-red.cnf`; AlmaLinux: `/etc/my.cnf.d/60-red.cnf`):

```ini
[mysqld]
bind-address = 192.168.100.70
```

```bash
sudo systemctl restart mariadb
sudo ss -tlnp | grep 3306                           # debe escuchar en 192.168.100.70:3306, NO en 0.0.0.0
```

Crea la base de datos y un usuario con **mínimos privilegios**, limitado a las IP de los servidores web:

```bash
sudo mariadb <<'SQL'
CREATE DATABASE tienda CHARACTER SET utf8mb4;
CREATE TABLE tienda.visitas (id INT PRIMARY KEY, total INT NOT NULL);
INSERT INTO tienda.visitas VALUES (1, 0);
CREATE USER 'appuser'@'192.168.100.61' IDENTIFIED BY 'ClaveAppLab1';
CREATE USER 'appuser'@'192.168.100.62' IDENTIFIED BY 'ClaveAppLab1';
GRANT SELECT, UPDATE ON tienda.visitas TO 'appuser'@'192.168.100.61';
GRANT SELECT, UPDATE ON tienda.visitas TO 'appuser'@'192.168.100.62';
SQL
sudo mariadb -e "SHOW GRANTS FOR 'appuser'@'192.168.100.61';"
```

> [!NOTE]
> La contraseña `ClaveAppLab1` es solo de laboratorio. En un entorno real se usan contraseñas únicas y se guardan en un gestor de secretos, nunca en el código.

### 5.2. Servidores web (`web01` y `web02`)

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo apt install -y apache2 php libapache2-mod-php php-mysql
sudo rm -f /var/www/html/index.html
sudo systemctl enable --now apache2
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo dnf install -y httpd php php-mysqlnd
sudo systemctl enable --now httpd
sudo setsebool -P httpd_can_network_connect_db on       # SELinux: permite a Apache conectar con la BD
```
{{% /tab %}}
{{< /tabs >}}

Crea `/var/www/html/index.php` (igual en ambos nodos):

```php
<?php
// Página de demostración: muestra el servidor que responde y cuenta visitas en la BD
mysqli_report(MYSQLI_REPORT_OFF);
$servidor = gethostname();
$db = @new mysqli('192.168.100.70', 'appuser', 'ClaveAppLab1', 'tienda');
if ($db->connect_errno) {
    http_response_code(500);
    echo "Servidor: $servidor - ERROR de base de datos\n";
    exit;
}
$db->query("UPDATE visitas SET total = total + 1 WHERE id = 1");
$fila = $db->query("SELECT total FROM visitas WHERE id = 1")->fetch_assoc();
echo "Servidor: $servidor - visitas: {$fila['total']}\n";
```

Y `/var/www/html/salud.php`, que el balanceador usará para saber si el nodo está **realmente** sano (servidor web + acceso a la base de datos):

```php
<?php
// Comprobación de salud: 200 si el servidor y la BD responden; 503 si no
mysqli_report(MYSQLI_REPORT_OFF);
$db = @new mysqli('192.168.100.70', 'appuser', 'ClaveAppLab1', 'tienda');
if ($db->connect_errno || !$db->query("SELECT 1")) {
    http_response_code(503);
    echo "KO\n";
    exit;
}
echo "OK\n";
```

### 5.3. Comprobación

```bash
curl -s http://192.168.100.61/            # Servidor: web01 - visitas: 1
curl -s http://192.168.100.62/            # Servidor: web02 - visitas: 2   (el contador es COMPARTIDO)
curl -s -o /dev/null -w '%{http_code}\n' http://192.168.100.61/salud.php    # 200
```

**Prueba de fallo (sin balanceador aún):** para MariaDB en `db01` (`sudo systemctl stop mariadb`) y repite las dos peticiones: debe aparecer el error 500/503 en **ambos** nodos. Arranca de nuevo la base de datos y comprueba que se recuperan. Esto demuestra que **`db01` es un SPOF**: duplicar los servidores web no lo elimina.

> [!TIP]
> Si falla la conexión a la BD: `sudo ss -tlnp | grep 3306` (escucha), `mariadb -h 192.168.100.70 -uappuser -pClaveAppLab1 tienda` desde el web (permiso/usuario/cortafuegos) y, en AlmaLinux, `sudo ausearch -m avc -ts recent` (SELinux).

---

## 6. Práctica 4 · Balanceo con HAProxy

**Objetivo:** repartir la carga entre `web01` y `web02` y retirar automáticamente el que falle (RA6 e).

### 6.1. Instalación y configuración en `lb01`

```bash
sudo apt install -y haproxy                         # AlmaLinux: sudo dnf install -y haproxy
sudo cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.bak
sudo nano /etc/haproxy/haproxy.cfg                  # sustituye el contenido por el siguiente
```

```text
global
    log /dev/log local0
    maxconn 2000
    user haproxy
    group haproxy
    daemon

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5s
    timeout client  30s
    timeout server  30s
    retries 3

frontend fe_web
    bind *:80
    default_backend be_web

backend be_web
    balance roundrobin
    option forwardfor
    option httpchk
    http-check send meth GET uri /salud.php ver HTTP/1.1 hdr Host localhost
    http-check expect status 200
    default-server inter 2s fall 3 rise 2
    server web01 192.168.100.61:80 check
    server web02 192.168.100.62:80 check

listen stats
    bind 192.168.100.51:8404
    stats enable
    stats uri /stats
    stats refresh 5s
    stats auth admin:ClaveStatsLab1
```

```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg         # "Configuration file is valid"
sudo systemctl enable --now haproxy
sudo systemctl status haproxy --no-pager
```

> [!NOTE]
> En AlmaLinux, si SELinux está activo, HAProxy puede necesitar `sudo setsebool -P haproxy_connect_any on` para conectar con los backends en puertos distintos del habitual. Con el puerto 80 no es necesario.

### 6.2. Comprobación del reparto

```bash
for i in $(seq 1 8); do curl -s http://192.168.100.51/ | cut -c1-30; done | tee ~/ud5-evidencias/04-reparto.txt
```

Esperado: se alternan `web01` y `web02`. Abre el panel `http://192.168.100.51:8404/stats` (usuario `admin`) y comprueba que los dos servidores están en verde (**UP**).

### 6.3. Pruebas de fallo

**Fallo 1: cae un servidor web.** En una terminal del cliente deja una petición continua:

```bash
while true; do printf '%s ' "$(date +%T)"; curl -s -m 2 -w ' [%{http_code}]\n' http://192.168.100.51/ | cut -c1-45; sleep 0.5; done
```

En `web01` detén Apache (`sudo systemctl stop apache2`; AlmaLinux: `httpd`). Observa:

- Durante unos 4-6 segundos puede aparecer algún error 503 (mientras HAProxy detecta el fallo: `inter 2s × fall 3`).
- Después **todas las respuestas vienen de `web02`** y el panel de estadísticas muestra `web01` en rojo (**DOWN**).

Arranca de nuevo Apache en `web01`: tras `rise 2` comprobaciones correctas vuelve a **UP** y el reparto se reanuda. Anota el tiempo de detección.

**Fallo 2: la aplicación falla pero el servidor web sigue vivo.** Para MariaDB en `db01`: ambos nodos devuelven 503 en `/salud.php`, HAProxy los marca **DOWN** y el cliente recibe `503 Service Unavailable`. Arranca MariaDB y comprueba la recuperación. *Pregunta:* ¿qué ventaja tiene el *health check* de aplicación frente a comprobar solo el puerto 80?

**Fallo 3: se detiene HAProxy.** `sudo systemctl stop haproxy` en `lb01`: el servicio queda inaccesible. Esto demuestra que el **balanceador es ahora el SPOF** → práctica 5.

### 6.4. Mantenimiento sin parada

Con el socket de administración de HAProxy (habilítalo añadiendo `stats socket /run/haproxy/admin.sock mode 660 level admin` en la sección `global`), saca `web01` ordenadamente para actualizarlo:

```bash
sudo apt install -y socat
echo "disable server be_web/web01" | sudo socat stdio /run/haproxy/admin.sock
echo "show servers state be_web"   | sudo socat stdio /run/haproxy/admin.sock
# ...actualizar web01 y reiniciarlo...
echo "enable server be_web/web01"  | sudo socat stdio /run/haproxy/admin.sock
```

El cliente no debe notar nada: es la ventaja de la redundancia para el **mantenimiento**.

---

## 7. Práctica 5 · IP virtual con Keepalived

**Objetivo:** eliminar el SPOF del balanceador con dos nodos y una IP virtual (RA6 d).

### 7.1. Segundo balanceador

En `lb02`, instala HAProxy y copia la **misma** configuración de `lb01`, pero cambiando la línea de `stats` por `bind 192.168.100.52:8404`. Valida con `haproxy -c` y arranca el servicio.

### 7.2. Keepalived en ambos

```bash
sudo apt install -y keepalived                      # AlmaLinux: sudo dnf install -y keepalived
ip -br a                                            # anota el nombre de tu interfaz (p. ej. enp0s3)
```

`/etc/keepalived/keepalived.conf` en **`lb01`** (ajusta `interface`):

```text
global_defs {
    router_id LB01
    enable_script_security
    script_user root
}

vrrp_script chk_haproxy {
    script "/usr/bin/pgrep -x haproxy"
    interval 2
    timeout 2
    fall 2
    rise 2
    weight -60
}

vrrp_instance VI_WEB {
    state MASTER
    interface enp0s3
    virtual_router_id 51
    priority 150
    advert_int 1
    unicast_src_ip 192.168.100.51
    unicast_peer {
        192.168.100.52
    }
    authentication {
        auth_type PASS
        auth_pass Lab2627x
    }
    virtual_ipaddress {
        192.168.100.50/24 dev enp0s3
    }
    track_script {
        chk_haproxy
    }
}
```

En **`lb02`**: `router_id LB02`, `state BACKUP`, `priority 100`, `unicast_src_ip 192.168.100.52` y `unicast_peer { 192.168.100.51 }`; el resto, igual.

```bash
sudo keepalived -t -f /etc/keepalived/keepalived.conf    # comprueba la configuración
sudo systemctl enable --now keepalived
ip -br a show enp0s3                                     # solo lb01 debe tener 192.168.100.50
sudo journalctl -u keepalived -n 15 --no-pager           # "Entering MASTER STATE" en lb01
curl -s http://192.168.100.50/ | cut -c1-30              # el servicio responde por la IP virtual
```

> [!WARNING]
> Si tienes cortafuegos, permite el protocolo VRRP (IP 112) entre `lb01` y `lb02`, o ambos se creerán MASTER. Compruébalo con `sudo tcpdump -ni enp0s3 proto 112`: debes ver los anuncios cada segundo desde la IP del MASTER.

### 7.3. Pruebas de fallo (anota la hora y los segundos de interrupción)

En el cliente, lanza la petición continua **a la IP virtual**:

```bash
while true; do printf '%s ' "$(date +%T.%N | cut -c1-12)"; curl -s -m 1 -w ' [%{http_code}]\n' http://192.168.100.50/ | cut -c1-45 || true; sleep 0.5; done | tee ~/ud5-evidencias/05-failover.txt
```

| Prueba | Acción en `lb01` | Resultado esperado |
| --- | --- | --- |
| **A. Fallo del servicio** | `sudo systemctl stop haproxy` | `chk_haproxy` baja la prioridad (150 − 60 = 90 < 100); `lb02` asume la VIP en unos segundos |
| **B. Fallo del nodo** | Apagar bruscamente la VM (VirtualBox: *Apagar la máquina*) | `lb02` detecta la falta de anuncios (≈ 3 s) y asume la VIP |
| **C. Recuperación** | Arrancar de nuevo `lb01` / `systemctl start haproxy` | `lb01` recupera la VIP (preempción) |

Para cada prueba rellena:

| Prueba | Hora del fallo | Hora de recuperación | Interrupción (s) | Peticiones fallidas |
| --- | --- | --- | --- | --- |
| A | | | | |
| B | | | | |
| C | | | | |

**Ampliación:** añade `nopreempt` (con `state BACKUP` en ambos y prioridades distintas) y repite la prueba C. ¿Qué diferencia observas al volver `lb01`? ¿Por qué puede interesar evitar el «vaivén» de la VIP?

---

## 8. Práctica 6 · Replicación de MariaDB

**Objetivo:** eliminar (parcialmente) el SPOF de la base de datos (RA6 d, f). Requiere `db02` (Debian 13, MariaDB instalado como en 5.1).

### 8.1. Configuración

En `db01`, crea `/etc/mysql/mariadb.conf.d/61-replica.cnf` (AlmaLinux: `/etc/my.cnf.d/61-replica.cnf`):

```ini
[mysqld]
server_id     = 1
log_bin       = /var/log/mysql/mariadb-bin
binlog_format = ROW
```

```bash
sudo mkdir -p /var/log/mysql && sudo chown mysql:mysql /var/log/mysql
sudo systemctl restart mariadb
sudo mariadb <<'SQL'
CREATE USER 'repl'@'192.168.100.71' IDENTIFIED BY 'ClaveReplLab1';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'192.168.100.71';
SQL
```

> [!NOTE]
> Si `db01` ya contiene datos (la tabla `visitas` de la práctica 3), la réplica debe empezar con una **copia consistente** de esos datos. Hazla con `sudo mariadb-dump --all-databases --single-transaction --master-data=2 > /root/inicial.sql`, cópiala a `db02` (`scp`) e impórtala con `sudo mariadb < inicial.sql` **antes** del paso siguiente. Para un laboratorio nuevo, basta con crear la BD después de configurar la réplica.

En `db02`, `/etc/mysql/mariadb.conf.d/61-replica.cnf`:

```ini
[mysqld]
server_id  = 2
relay_log  = /var/log/mysql/relay-bin
read_only  = 1
bind-address = 192.168.100.71
```

```bash
sudo mkdir -p /var/log/mysql && sudo chown mysql:mysql /var/log/mysql
sudo systemctl restart mariadb
sudo mariadb <<'SQL'
CHANGE MASTER TO
  MASTER_HOST='192.168.100.70',
  MASTER_USER='repl',
  MASTER_PASSWORD='ClaveReplLab1',
  MASTER_USE_GTID=slave_pos;
START REPLICA;
SQL
sudo mariadb -e "SHOW REPLICA STATUS\G" | grep -E 'Slave_IO_Running|Slave_SQL_Running|Seconds_Behind_Master|Last_IO_Error|Last_SQL_Error' | tee ~/ud5-evidencias/06-replica.txt
```

Esperado: `Slave_IO_Running: Yes`, `Slave_SQL_Running: Yes`, `Seconds_Behind_Master: 0`.

### 8.2. Comprobación

```bash
# En db01
sudo mariadb -e "UPDATE tienda.visitas SET total = total + 100 WHERE id=1;"
# En db02
sudo mariadb -e "SELECT * FROM tienda.visitas;"          # debe reflejar el cambio
sudo mariadb -e "INSERT INTO tienda.visitas VALUES (2,0);"   # debe FALLAR por read_only (protege la réplica)
```

### 8.3. Prueba de fallo y promoción

1. Con la aplicación funcionando por la VIP (práctica 5), apaga `db01`. La aplicación devuelve errores: **tiempo de caída** hasta que actúes.
2. En `db02`, **promociona** la réplica:

```bash
sudo mariadb -e "STOP REPLICA; RESET REPLICA ALL; SET GLOBAL read_only = 0;"
```

3. Concede permisos al usuario de aplicación en `db02` (la réplica ya contiene el usuario `appuser` si se creó antes de replicar; compruébalo con `SHOW GRANTS`) y cambia en `web01` y `web02` la IP de conexión de `192.168.100.70` a `192.168.100.71` (o, mejor, define el nombre `db` en `/etc/hosts` y úsalo en la aplicación; así solo se cambia una línea).
4. Comprueba que la aplicación vuelve a funcionar y que **no se ha perdido el contador** (RPO ≈ 0).

**Preguntas para el informe:** ¿qué pasaría si `db01` volviera a arrancar y la aplicación siguiera escribiendo en él? ¿Qué tipo de herramientas automatizan esta promoción? ¿Por qué esta replicación **no** sustituye a una copia de seguridad? Demuéstralo ejecutando `DROP TABLE` en el primario y viendo qué ocurre en la réplica (hazlo sobre una tabla de prueba, no sobre `visitas`).

---

## 9. Práctica 7 · Fallo bajo carga

**Objetivo:** medir el efecto real de un fallo mientras hay tráfico.

En `sad-cli`:

```bash
sudo apt install -y apache2-utils                   # AlmaLinux: sudo dnf install -y httpd-tools
ab -n 5000 -c 20 -r http://192.168.100.50/index.php | tee ~/ud5-evidencias/07-carga-base.txt
```

Anota `Requests per second`, `Time per request` y `Failed requests` (**línea base**, sin fallos). Repite la prueba aumentando el número de peticiones (`-n 20000`) y **mientras corre**, provoca el fallo de un backend (`sudo systemctl stop apache2` en `web01`):

```bash
ab -n 20000 -c 20 -r http://192.168.100.50/index.php | tee ~/ud5-evidencias/07-carga-fallo.txt
```

Compara: peticiones fallidas (`Failed requests`, `Non-2xx responses`), caída del rendimiento y tiempo hasta estabilizarse. Responde: ¿qué parte de las peticiones se perdió y por qué? ¿Cómo la reducirías (valores `inter`/`fall`, reintentos `retries`, `option redispatch`)?

> [!CAUTION]
> Estas pruebas se realizan solo sobre tu laboratorio. Generar carga sobre servicios ajenos puede constituir un ataque de denegación de servicio.

---

## 10. Práctica 8 · Clúster Pacemaker/Corosync (activo-pasivo)

**Objetivo:** gestionar IP + servicio como un grupo con quórum (RA6 d, g). Dos VM nuevas `nodo1` (192.168.100.81) y `nodo2` (192.168.100.82) con Debian 13 o AlmaLinux 10.

Sigue el procedimiento del apartado 8.3 de la [teoría](../teoria/#83-ejemplo-con-pcs-ip-virtual--servicio-web-activo-pasivo) completo (instalación, `hacluster`, `pcs cluster setup`, recursos `vip` y `web`, restricciones). Después:

1. Guarda `sudo pcs status` y `sudo pcs config` como evidencia.
2. **Fallo ordenado:** `sudo pcs node standby nodo1`; verifica que `vip` y `web` pasan a `nodo2` y que `curl http://192.168.100.80/` sigue respondiendo. Después, `sudo pcs node unstandby nodo1`.
3. **Fallo brusco:** apaga la VM de `nodo2` (o `sudo systemctl stop corosync` en él). En `nodo1`, `sudo pcs status` debe mostrar a `nodo2` *OFFLINE* y los recursos arrancados en `nodo1`. Anota el tiempo.
4. **Análisis de quórum:** ejecuta `sudo pcs quorum status` y explica por qué un clúster de **2 nodos** es frágil. ¿Qué añadirías (*QDevice*, tercer nodo)?
5. **Fencing:** explica, sin ejecutarlo, qué riesgo corres con `stonith-enabled=false` si los nodos compartieran un disco, y cómo lo resolverías en un entorno real (IPMI/iLO, conmutador de energía).

---

## 11. Práctica 9 · Proxmox VE: alta disponibilidad de máquinas virtuales (evaluable)

Requiere tres nodos Proxmox VE 9 (VM con **virtualización anidada** habilitada) o hardware dedicado, con al menos 4 GiB de RAM por nodo y un segundo disco para Ceph. En VirtualBox la virtualización anidada puede ser lenta: es válida para aprender, no para medir rendimiento.

1. Instala tres nodos (`pve1`, `pve2`, `pve3`) con IP estáticas en `SAD-NAT` y comprueba la conectividad entre ellos (nombres en `/etc/hosts`).
2. Crea el clúster en `pve1` (`pvecm create labsad`) y une los otros dos (`pvecm add 192.168.100.101`). Comprueba `pvecm status` y explica el **quórum** (3 votos, mayoría = 2).
3. Instala y configura **Ceph** desde la interfaz (*Datacenter → Ceph*): un monitor y un OSD por nodo (segundo disco) y un *pool* para las VM. Comprueba que el estado es `HEALTH_OK`.
4. Crea una VM Debian con el disco en el *pool* Ceph y verifica que arranca.
5. **Migración en vivo:** `qm migrate <id> pve2 --online` con un `ping` continuo hacia la VM; anota los paquetes perdidos.
6. Registra la VM como recurso HA (`ha-manager add vm:<id> --state started`).
7. **Fallo:** apaga bruscamente el nodo donde se ejecuta la VM. Mide con `ping` el tiempo hasta que la VM responde otra vez y anota en qué nodo reinició. Ese tiempo es tu **RTO real**.
8. Reincorpora el nodo caído y comprueba el estado con `ha-manager status` y `ceph -s`.

> [!NOTE]
> Si no tienes recursos para tres nodos, realiza esta práctica **de forma teórica y documental**: describe cada paso, qué comprobarías y qué resultado esperas, y analiza el vídeo o la demostración que te facilite el docente.

---

## 12. Problemas habituales

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| HAProxy no arranca | Error de sintaxis o puerto en uso | `haproxy -c -f …`; `ss -tlnp` (busca el puerto 80) |
| Todos los backends `DOWN` | `/salud.php` falla (BD, permisos) | `curl -v http://IP_WEB/salud.php` desde `lb01` |
| Las dos máquinas tienen la VIP | Anuncios VRRP bloqueados | Abre el protocolo 112, `unicast_peer` correcto, `tcpdump proto 112` |
| La VIP no cambia al parar HAProxy | Falta `track_script`, o `weight` demasiado pequeño | Debe cumplirse `150 + weight < 100` |
| La VIP no responde tras migrar | ARP/NAT de VirtualBox | Prueba una **Red interna** en vez de NAT Network; `arping -c 3 -A -I enp0s3 192.168.100.50` |
| `appuser` no puede conectar | `bind-address`, usuario por IP, SELinux | `ss -tlnp`, `SHOW GRANTS`, `setsebool -P httpd_can_network_connect_db on` |
| Réplica sin `Yes` en IO/SQL | Credenciales, cortafuegos o datos distintos | `Last_IO_Error` / `Last_SQL_Error`; recarga una copia inicial |
| `pcs cluster setup` falla | Configuración previa de Corosync | `sudo pcs cluster destroy` y repetir |
| `partition WITHOUT quorum` | Se ha perdido la mayoría | Revisa la red; con 2 nodos, QDevice o tercer nodo |

---

## 13. Buenas prácticas de seguridad aplicadas

- Panel de estadísticas de HAProxy accesible **solo** desde la red interna y con credenciales.
- Usuarios de BD con **mínimos privilegios** y limitados por IP de origen.
- La base de datos escucha solo en la **IP interna**, nunca en `0.0.0.0`.
- Segmento de red dedicado para VRRP, replicación y Corosync (UD6: VLAN).
- Contraseñas de laboratorio **sustituidas** por secretos únicos en cualquier entorno real.
- STONITH activo y quórum correcto en clústeres reales.
- Copias de seguridad **además** de la replicación.

---

## 14. Autoevaluación

1. ¿Qué es un SPOF? Pon un ejemplo en cada capa (energía, red, servidor, datos).
2. ¿Qué miden MTBF y MTTR y cómo se combinan para obtener la disponibilidad?
3. ¿Qué diferencia hay entre RPO y RTO?
4. ¿Por qué RAID no sustituye a una copia de seguridad?
5. ¿Qué comprueba `option httpchk` en HAProxy y qué ventaja tiene frente a un *check* de puerto?
6. ¿Qué parámetros determinan el tiempo que HAProxy tarda en detectar un servidor caído?
7. ¿Qué papel cumple la IP virtual VRRP y qué hace `track_script`?
8. ¿Qué diferencia hay entre un balanceador y un proxy inverso?
9. ¿Qué funciones desempeñan Corosync y Pacemaker?
10. ¿Qué riesgo evita el quórum? ¿Y el *fencing*?
11. ¿Por qué tres nodos son preferibles a dos en un clúster Proxmox?
12. ¿Qué diferencia hay entre replicación síncrona y asíncrona en términos de RPO?
13. ¿Qué dependencias debes comprobar antes de afirmar que una máquina virtual está «en alta disponibilidad»?

---

## 15. Tarea evaluable: arquitectura de alta disponibilidad para *Librería Pilar*

**Entrega** (PDF o Markdown con capturas y evidencias propias, redactado con tus palabras):

1. **Análisis**: SPOF, impacto económico y propuesta de SLO, RTO y RPO justificados (práctica 1 y el supuesto de la teoría).
2. **Diseño**: diagrama de la arquitectura y tabla de componentes (qué SPOF elimina cada uno y cuál queda).
3. **Implantación** de las prácticas 3, 4, 5 y 6 con ficheros de configuración (sin contraseñas reales) y comprobaciones.
4. **Tabla de pruebas de fallo** con hora de fallo, hora de recuperación, interrupción medida y peticiones perdidas, para: backend web, balanceador (servicio y nodo), base de datos.
5. **Prueba de carga** con y sin fallo (práctica 7) y análisis.
6. **Riesgos residuales** y propuesta de evolución a futuro (CE h): escalado horizontal, segundo CPD, automatización de la promoción de BD, monitorización.

| Criterio | Peso |
| --- | --- |
| Análisis de SPOF y objetivos (RTO/RPO/SLO) | 15 % |
| Configuración correcta y reproducible | 30 % |
| Pruebas de fallo bien diseñadas y medidas | 30 % |
| Análisis de resultados y riesgos residuales | 15 % |
| Documentación clara y coherente | 10 % |

---

## 16. Resumen

Has construido, paso a paso, una arquitectura sin SPOF en la capa web y balanceadora, y has visto sus límites en la capa de datos. Lo esencial: **medir** (disponibilidad, RTO, RPO), **eliminar SPOF con proporcionalidad**, **comprobar la aplicación y no solo el puerto**, y **romper a propósito** cada componente para verificar que la recuperación es la esperada y cuánto tarda.

---

## 17. Referencias

- HAProxy, *Configuration Manual*: <https://docs.haproxy.org>
- Keepalived: <https://www.keepalived.org/manpage.html>
- RFC 5798, VRRP v3: <https://www.rfc-editor.org/rfc/rfc5798>
- ClusterLabs, *Clusters from Scratch*: <https://clusterlabs.org/pacemaker/doc/>
- Proxmox VE, *Administration Guide*: <https://pve.proxmox.com/pve-docs/>
- MariaDB, *Replication*: <https://mariadb.com/kb/en/replication-overview/>
- Linux RAID wiki: <https://raid.wiki.kernel.org>
- Ceph: <https://docs.ceph.com>
