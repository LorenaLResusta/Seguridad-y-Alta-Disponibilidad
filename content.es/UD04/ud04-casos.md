---
title: "UD04 · Casos de ataque y defensa"
weight: 3
bookToc: true
---

# UD04 · Casos de ataque y defensa

{{< ra "RA2:a,b,c,d,e" "RA1:c" >}}

Fortificar un *host* no es solo cerrar puertos: las aplicaciones que se ejecutan en él también son superficie de ataque. En esta página atacas y defiendes una pequeña aplicación web en tu servidor Debian con las dos vulnerabilidades más clásicas de inyección (**SQL** y **órdenes del sistema**) y aprendes a buscar las vulnerabilidades conocidas de tus propios paquetes.

| Caso | Ataque | Caso real | Tipo |
|---|---|---|---|
| [4.A](#caso-4a--inyección-sql) | Inyección SQL | MOVEit Transfer (2023) | Laboratorio |
| [4.B](#caso-4b--inyección-de-órdenes-del-sistema) | Inyección de órdenes del sistema operativo | Controladores Danfoss de los supermercados (2025-2026) | Laboratorio |
| [4.C](#caso-4c--búsqueda-de-vulnerabilidades-en-tu-propio-servidor) | Búsqueda de vulnerabilidades en paquetes instalados | — | Laboratorio |
| [4.D](#búsqueda-de-vulnerabilidades-de-aplicaciones-web) | Vulnerabilidades de aplicaciones web en INCIBE-CERT | — | Autónoma |

> [!IMPORTANT]
> Las aplicaciones de esta página son **vulnerables a propósito**. Instálalas solo en una VM del laboratorio, sin acceso desde fuera de la red interna, y **bórralas al terminar**. Recuerda las [normas de laboratorio](/ud01/ud01-casos/#antes-de-empezar-ética-y-legalidad-del-laboratorio). Estos casos **no se entregan**.

### Laboratorio común

| Máquina | Función | IP (red `SAD-NAT`) |
|---|---|---|
| `sad-web` | Servidor Debian 13 con Apache, PHP y MariaDB | 192.168.100.30 |
| `sad-cli` | Máquina desde la que se prueban los ataques | 192.168.100.10 |

Haz una **instantánea** de `sad-web` (`ud04-casos-antes`) y prepara el servidor:

```bash
sudo apt update && sudo apt install -y apache2 php libapache2-mod-php php-mysql mariadb-server
php -v | head -n 1                         # Debian 13: PHP 8.4
sudo systemctl enable --now apache2 mariadb
```

---

## Caso 4.A · Inyección SQL

{{< practica etiqueta="Caso" num="4.A" tipo="Guiada" duracion="2 h · trabajo autónomo" nivel="2" ra="RA2:a,c,d" entorno="Debian 13 · Apache 2.4 · PHP 8.4 · MariaDB 11" entrega="ataque, detección, corrección y comprobación documentados" >}}

### Qué es

Una aplicación web construye consultas SQL con los datos que escribe el usuario. Si **pega** esos datos directamente dentro de la consulta, el usuario puede escribir **fragmentos de SQL** que cambian su significado. Eso es una **inyección SQL** (*SQL injection*, CWE-89). Con ella un atacante puede leer tablas que no debería ver, saltarse un inicio de sesión, modificar o borrar datos y, en algunos casos, ejecutar órdenes en el servidor.

OWASP la incluye dentro de la categoría **A03 Injection** de su *Top 10* de riesgos de aplicaciones web.

### El caso real: MOVEit Transfer (2023)

En **mayo de 2023** el grupo de extorsión **Cl0p** explotó una inyección SQL (**CVE-2023-34362**, CVSS 9.8) en **MOVEit Transfer**, un programa de transferencia de ficheros muy usado por empresas y administraciones. La vulnerabilidad permitía, sin credenciales, acceder a la base de datos de la aplicación e instalar una puerta trasera (*web shell*). Cl0p robó datos de **miles de organizaciones** (bancos, universidades, aseguradoras, administraciones) y después las extorsionó. CISA y el FBI publicaron un aviso conjunto (AA23-158A) y el fallo entró en el catálogo KEV.

INCIBE recuerda en su blog para empresas las medidas básicas: **filtrar y validar** lo que introduce el usuario, **no exponer** las bases de datos a Internet y **analizar** las aplicaciones antes de publicarlas.

### Ciclo del caso

| Fase | Descripción |
|---|---|
| **Vulnerabilidad** | Consulta construida concatenando texto del usuario; usuario de BD con más permisos de los necesarios; errores de SQL visibles |
| **Ataque** | `' OR 1=1 -- -` para ver todos los registros; `UNION SELECT` para leer otra tabla |
| **Detección** | Peticiones con comillas, `UNION`, `SELECT` o comentarios SQL en el registro de Apache; errores de sintaxis SQL en los registros |
| **Mitigación** | **Consultas preparadas**; mínimo privilegio en la BD; no mostrar errores; WAF como capa adicional |
| **Comprobación** | Repetir los ataques y verificar con `sqlmap` que el parámetro ya no es inyectable |

### 1. Base de datos y aplicación vulnerable (en `sad-web`)

```bash
sudo mariadb <<'SQL'
CREATE DATABASE clinica;
CREATE TABLE clinica.pacientes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50), telefono VARCHAR(15), diagnostico VARCHAR(100));
CREATE TABLE clinica.usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario VARCHAR(30), clave VARCHAR(255));
INSERT INTO clinica.pacientes (nombre, telefono, diagnostico) VALUES
  ('Ana Pérez','600111222','Caries'), ('Luis Gil','600333444','Ortodoncia'),
  ('Marta Ruiz','600555666','Implante');
INSERT INTO clinica.usuarios (usuario, clave) VALUES
  ('admin','$2y$10$EjemploDeHashBcryptNoRealParaElLaboratorio0000000000'),
  ('recepcion','$2y$10$OtroHashDeEjemploNoRealParaElLaboratorio000000000000');
-- ERROR DE DISEÑO A PROPÓSITO: la aplicación recibe todos los privilegios sobre la BD
CREATE USER 'webapp'@'localhost' IDENTIFIED BY 'ClaveWebLab1';
GRANT ALL PRIVILEGES ON clinica.* TO 'webapp'@'localhost';
SQL
```

Crea `/var/www/html/buscar.php`. La página busca pacientes por nombre y **muestra la consulta** para que veas qué ocurre:

```php
<?php
// APLICACIÓN VULNERABLE A PROPÓSITO: solo para el laboratorio
mysqli_report(MYSQLI_REPORT_OFF);              // muestra los errores en lugar de lanzar excepciones
$db = new mysqli('localhost', 'webapp', 'ClaveWebLab1', 'clinica');
$nombre = $_GET['nombre'] ?? '';

// ERROR: el texto del usuario se pega dentro de la consulta
$sql = "SELECT nombre, telefono FROM pacientes WHERE nombre LIKE '%$nombre%'";
echo "<p><code>" . htmlspecialchars($sql) . "</code></p>\n";

$res = $db->query($sql);
if (!$res) { die("Error de base de datos: " . htmlspecialchars($db->error)); }   // ERROR: revela detalles internos
while ($f = $res->fetch_assoc()) {
    echo htmlspecialchars($f['nombre']) . " - " . htmlspecialchars($f['telefono']) . "<br>\n";
}
```

```bash
sudo chown root:www-data /var/www/html/buscar.php && sudo chmod 640 /var/www/html/buscar.php
curl -s "http://localhost/buscar.php?nombre=Ana"     # uso normal: solo aparece Ana Pérez
```

### 2. El ataque (desde `sad-cli`)

`curl -G --data-urlencode` codifica correctamente los caracteres especiales en la URL (comillas, espacios), igual que haría un navegador.

**a) Mostrar todos los registros**

```bash
curl -sG http://192.168.100.30/buscar.php --data-urlencode "nombre=' OR 1=1 -- -"
```

La consulta resultante es `… WHERE nombre LIKE '%' OR 1=1 -- -%'`. La comilla **cierra** la cadena, `OR 1=1` hace la condición siempre verdadera y `-- -` convierte el resto en un **comentario**.

**b) Provocar un error para obtener información**

```bash
curl -sG http://192.168.100.30/buscar.php --data-urlencode "nombre='"
```

El mensaje de error revela que la base de datos es MariaDB y cómo está escrita la consulta: información muy útil para el atacante.

**c) Leer otra tabla con `UNION`**

`UNION` une el resultado de dos consultas. Si la segunda consulta devuelve el mismo número de columnas (aquí, dos), sus filas aparecen en la página:

```bash
curl -sG http://192.168.100.30/buscar.php --data-urlencode "nombre=' UNION SELECT @@version, current_user() -- -"
curl -sG http://192.168.100.30/buscar.php --data-urlencode "nombre=' UNION SELECT usuario, clave FROM usuarios -- -"
```

{{% details title="🎯 Resultado esperado" open=false %}}
- (a) aparecen **los tres pacientes**, aunque no se ha buscado ninguno.
- (b) aparece `Error de base de datos: You have an error in your SQL syntax…`.
- (c) la primera consulta muestra la versión de MariaDB y `webapp@localhost`; la segunda, los **usuarios y los *hashes* de sus contraseñas** de la tabla `usuarios`, que la página nunca debería mostrar.

Ese último resultado es exactamente lo que pasó en muchos robos de datos reales. Si los *hashes* fueran débiles, el atacante continuaría con el [caso 3.B](/ud03/ud03-casos/#caso-3b--robo-de-una-base-de-datos-de-contraseñas).
{{% /details %}}

**d) Ataque automatizado con `sqlmap`** (solo contra tu laboratorio)

`sqlmap` es una herramienta libre que detecta y explota inyecciones SQL de forma automática. Los atacantes la usan, y los auditores también, para **comprobar** si una corrección funciona.

```bash
sudo apt install -y sqlmap && mkdir -p ~/evidencias/ud04
sqlmap -u "http://192.168.100.30/buscar.php?nombre=Ana" -p nombre --batch --level=1 --risk=1 | tee ~/evidencias/ud04/sqlmap-antes.txt
```

- `-u`: URL que se analiza; `-p nombre`: parámetro que se prueba.
- `--batch`: responde automáticamente con la opción por defecto.
- `--level` y `--risk` en 1: pruebas mínimas y no destructivas.

Esperado: `Parameter: nombre (GET) … is vulnerable` y los tipos de inyección encontrados.

### 3. Detección (en `sad-web`)

Los ataques dejan huella en el registro de acceso de Apache, con los caracteres codificados en URL (`%27` es una comilla, `+` o `%20` un espacio):

```bash
sudo grep -iE "%27|union|select|sleep\(|--" /var/log/apache2/access.log | tail -n 10
sudo grep -c "sqlmap" /var/log/apache2/access.log     # sqlmap se identifica en el User-Agent por defecto
```

{{% details title="💡 Para pensar" open=false %}}
Un atacante real cambia el *User-Agent* (`--random-agent`) y espacia las peticiones. Por eso la detección por cadenas es útil pero limitada: hay que combinarla con un WAF (UD06), con la centralización de registros (Wazuh, práctica 4.9) y, sobre todo, con **código que no sea vulnerable**.
{{% /details %}}

### 4. Mitigación

**a) Mínimo privilegio en la base de datos** (contiene el daño aunque el código siga siendo vulnerable):

```bash
sudo mariadb <<'SQL'
REVOKE ALL PRIVILEGES ON clinica.* FROM 'webapp'@'localhost';
GRANT SELECT ON clinica.pacientes TO 'webapp'@'localhost';
SHOW GRANTS FOR 'webapp'@'localhost';
SQL
```

Repite desde `sad-cli` el ataque `UNION … FROM usuarios`: ahora falla con `SELECT command denied to user 'webapp'@'localhost' for table 'usuarios'`. El código sigue siendo vulnerable (el ataque `OR 1=1` sigue funcionando), pero el atacante **ya no puede salir** de la tabla `pacientes`.

**b) Consultas preparadas** (corrige la causa). Haz una copia y sustituye el contenido de `buscar.php`:

```bash
sudo cp /var/www/html/buscar.php /root/buscar.php.vulnerable
```

```php
<?php
// Versión corregida: consulta preparada, errores ocultos al usuario
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
try {
    $db = new mysqli('localhost', 'webapp', 'ClaveWebLab1', 'clinica');
    $nombre = $_GET['nombre'] ?? '';
    if (mb_strlen($nombre) > 50) { http_response_code(400); exit('Búsqueda demasiado larga'); }

    // 1. La consulta se envía al servidor con un hueco (?) en lugar del dato
    $stmt = $db->prepare("SELECT nombre, telefono FROM pacientes WHERE nombre LIKE ?");
    // 2. El dato se envía aparte: la BD lo trata SIEMPRE como texto, nunca como SQL
    $patron = "%" . $nombre . "%";
    $stmt->bind_param("s", $patron);
    $stmt->execute();
    $res = $stmt->get_result();
    while ($f = $res->fetch_assoc()) {
        echo htmlspecialchars($f['nombre']) . " - " . htmlspecialchars($f['telefono']) . "<br>\n";
    }
} catch (mysqli_sql_exception $e) {
    error_log("buscar.php: " . $e->getMessage());     // el detalle va al registro del servidor
    http_response_code(500);
    exit("Se ha producido un error. Inténtalo más tarde.");
}
```

```bash
php -l /var/www/html/buscar.php                       # comprueba la sintaxis: "No syntax errors detected"
```

- `prepare()` envía la **estructura** de la consulta con un marcador `?`.
- `bind_param("s", $patron)` envía el dato por separado indicando su tipo (`s` = *string*). Aunque contenga comillas o `UNION`, la base de datos lo busca **como texto literal**.
- `htmlspecialchars()` en la salida evita otra inyección distinta, el *cross-site scripting* (XSS).
- Los errores se escriben en el registro (`/var/log/apache2/error.log`) y el usuario solo ve un mensaje genérico.

**c) Capa adicional: WAF.** Un cortafuegos de aplicaciones web (ModSecurity con OWASP CRS) bloquea muchas cargas típicas de inyección antes de que lleguen a la aplicación. Lo configuras en la [práctica 6.6](/ud06/ud06-practicas/). Es una **defensa en profundidad**, no un sustituto de corregir el código.

### 5. Comprobación

```bash
curl -sG http://192.168.100.30/buscar.php --data-urlencode "nombre=' OR 1=1 -- -"                     # sin resultados
curl -sG http://192.168.100.30/buscar.php --data-urlencode "nombre=' UNION SELECT usuario, clave FROM usuarios -- -"   # sin resultados
curl -sG http://192.168.100.30/buscar.php --data-urlencode "nombre=Ana"                               # sigue funcionando
sqlmap -u "http://192.168.100.30/buscar.php?nombre=Ana" -p nombre --batch --level=1 --risk=1 --flush-session | tee ~/evidencias/ud04/sqlmap-despues.txt
```

{{% details title="🎯 Resultado esperado" open=false %}}
Los dos ataques devuelven una página **vacía** (no hay pacientes cuyo nombre contenga literalmente `' OR 1=1 -- -`), la búsqueda legítima sigue funcionando y `sqlmap` termina con `all tested parameters do not appear to be injectable`. `--flush-session` obliga a `sqlmap` a repetir las pruebas en lugar de reutilizar el resultado anterior.
{{% /details %}}

### Problemas habituales

| Síntoma | Causa | Solución |
|---|---|---|
| La página PHP se descarga en lugar de ejecutarse | Falta `libapache2-mod-php` | Instálalo y `sudo systemctl restart apache2` |
| `Call to undefined method mysqli_stmt::get_result()` | PHP sin el controlador `mysqlnd` | En Debian, `php-mysql` ya lo usa; comprueba `php -m \| grep mysqlnd` |
| `Access denied for user 'webapp'` | Contraseña o usuario de BD incorrectos | Revisa `CREATE USER` y la cadena de conexión |
| Error 500 sin mensaje | Es lo esperado en la versión corregida | Mira el detalle en `/var/log/apache2/error.log` |

---

## Caso 4.B · Inyección de órdenes del sistema

{{< practica etiqueta="Caso" num="4.B" tipo="Guiada" duracion="1 h · trabajo autónomo" nivel="2" ra="RA2:a,c,d,e" entorno="Debian 13 · Apache 2.4 · PHP 8.4 · auditd" entrega="ataque, detección con auditd y corrección" >}}

### Qué es y caso real

Una **inyección de órdenes** (*OS command injection*, CWE-78) ocurre cuando una aplicación ejecuta una orden del sistema operativo con texto del usuario dentro. En la consola de Linux el carácter `;` separa órdenes, así que si el usuario escribe `8.8.8.8; cat /etc/passwd`, el servidor ejecuta **las dos**.

Es exactamente el tipo de fallo **CVE-2025-41451** de los controladores de refrigeración Danfoss AK-SM 800A, implicados en el [ataque a los supermercados franceses](/ud01/ud01-casos/#caso-1b--supermercados-sin-frío-dispositivos-expuestos-a-internet): un campo del formulario de configuración del correo no se filtraba y permitía ejecutar órdenes en el equipo. Encadenado con el fallo de autenticación CVE-2025-41450, daba control total del controlador. Muchos *routers*, cámaras y dispositivos IoT tienen páginas de diagnóstico («hacer ping») con este mismo error.

### 1. Aplicación vulnerable (en `sad-web`)

`/var/www/html/ping.php`:

```php
<?php
// APLICACIÓN VULNERABLE A PROPÓSITO: herramienta de diagnóstico "ping"
$ip = $_GET['ip'] ?? '127.0.0.1';
echo "<pre>" . htmlspecialchars(shell_exec("ping -c 1 " . $ip)) . "</pre>";   // ERROR: concatena texto del usuario en una orden
```

### 2. Detección preparada antes del ataque: `auditd`

`auditd` (práctica 4.7) registra llamadas al sistema. Esta regla anota **cada programa que ejecute el usuario `www-data`** (UID 33 en Debian), es decir, todo lo que lance el servidor web:

```bash
sudo apt install -y auditd
sudo auditctl -a always,exit -F arch=b64 -S execve -F uid=33 -k web_exec
sudo auditctl -l                                    # lista las reglas activas
```

### 3. El ataque (desde `sad-cli`)

```bash
curl -sG http://192.168.100.30/ping.php --data-urlencode "ip=127.0.0.1"                 # uso normal
curl -sG http://192.168.100.30/ping.php --data-urlencode "ip=127.0.0.1; id; uname -a"
curl -sG http://192.168.100.30/ping.php --data-urlencode "ip=127.0.0.1; cat /etc/passwd | head -n 3"
```

{{% details title="🎯 Resultado esperado" open=false %}}
Tras la respuesta del `ping` aparecen `uid=33(www-data) gid=33(www-data)…`, la versión del núcleo y las primeras líneas de `/etc/passwd`. El atacante ejecuta lo que quiere **con los permisos del servidor web**. Con eso podría descargar una puerta trasera o intentar una escalada de privilegios.
{{% /details %}}

### 4. Detección

```bash
sudo ausearch -k web_exec -i | grep -E "proctitle|exe=" | tail -n 15
```

Un servidor web que ejecuta `id`, `uname` o `cat` es una **anomalía clarísima**: en producción, estos eventos deberían generar una alerta en el SIEM (Wazuh).

### 5. Mitigación

1. **No usar la consola** si no hace falta. Si hace falta, **validar** el dato con una lista blanca y **escapar** el argumento:

```php
<?php
$ip = $_GET['ip'] ?? '127.0.0.1';
// 1. Validación estricta: solo se acepta una dirección IPv4 o IPv6 válida
if (filter_var($ip, FILTER_VALIDATE_IP) === false) {
    http_response_code(400);
    exit("Dirección IP no válida");
}
// 2. escapeshellarg() encierra el dato entre comillas simples: la consola lo trata como UN argumento
echo "<pre>" . htmlspecialchars(shell_exec("ping -c 1 " . escapeshellarg($ip))) . "</pre>";
```

2. **Mínimo privilegio del proceso**: el servidor web nunca debe ejecutarse como `root`. Con AppArmor (práctica 4.6) se puede limitar qué programas puede lanzar.
3. **Desactivar funciones peligrosas** si la aplicación no las necesita, en `/etc/php/8.4/apache2/php.ini`:

```ini
disable_functions = exec,passthru,shell_exec,system,proc_open,popen
```

```bash
sudo cp /etc/php/8.4/apache2/php.ini /etc/php/8.4/apache2/php.ini.bak
sudo systemctl restart apache2
```

> [!WARNING]
> `disable_functions` rompe las aplicaciones que usen esas funciones legítimamente. Pruébalo primero en un entorno de pruebas. Además, desactiva también nuestra herramienta corregida: es una decisión de diseño (¿necesita la web hacer *ping*?).

### 6. Comprobación

```bash
curl -sG http://192.168.100.30/ping.php --data-urlencode "ip=127.0.0.1; id"    # "Dirección IP no válida"
curl -sG http://192.168.100.30/ping.php --data-urlencode "ip=127.0.0.1"        # ping normal (si no desactivaste shell_exec)
sudo ausearch -k web_exec -i --start recent | grep -c "exe=/usr/bin/id"       # 0 eventos nuevos
```

### 7. Limpieza

```bash
sudo auditctl -d always,exit -F arch=b64 -S execve -F uid=33 -k web_exec
sudo rm -f /var/www/html/buscar.php /var/www/html/ping.php
sudo mariadb -e "DROP DATABASE clinica; DROP USER 'webapp'@'localhost';"
```

O, más sencillo, restaura la instantánea `ud04-casos-antes`.

---

## Caso 4.C · Búsqueda de vulnerabilidades en tu propio servidor

{{< practica etiqueta="Caso" num="4.C" tipo="Guiada" duracion="1 h · trabajo autónomo" nivel="1" ra="RA2:b;RA1:c" entorno="Debian 13 · debsecan · Lynis" entrega="lista de CVE pendientes y plan de actualización" >}}

Un administrador no espera a leer la noticia: **pregunta a su sistema** qué vulnerabilidades conocidas le afectan.

### 1. `debsecan`: CVE de los paquetes instalados (Debian)

`debsecan` compara los paquetes instalados con la base de datos del **Debian Security Tracker** y lista los CVE que les afectan.

```bash
sudo apt install -y debsecan && mkdir -p ~/evidencias/ud04
debsecan --suite trixie --only-fixed | tee ~/evidencias/ud04/debsecan.txt | head -n 20
debsecan --suite trixie --only-fixed --format packages        # solo los paquetes a actualizar
debsecan --suite trixie --format summary | wc -l               # total, incluidos los que aún no tienen parche
```

- `--suite trixie`: versión de Debian (Debian 13).
- `--only-fixed`: solo los CVE para los que **ya existe** una versión corregida (los que puedes resolver hoy).

> [!NOTE]
> En Ubuntu usa `sudo pro security-status` y en AlmaLinux `sudo dnf updateinfo list --security`. Las herramientas cambian; la idea es la misma.

### 2. Actualizar y comprobar

```bash
sudo apt update && apt list --upgradable
sudo apt upgrade -y
sudo apt install -y needrestart && sudo needrestart -r l      # servicios que siguen usando bibliotecas antiguas
debsecan --suite trixie --only-fixed | wc -l                  # debe bajar (idealmente, 0)
```

`needrestart` es importante: actualizar una biblioteca (por ejemplo OpenSSL) no protege a los servicios que ya estaban en marcha hasta que **se reinician**.

### 3. Investigar un CVE concreto

Elige un CVE de la salida de `debsecan` y búscalo en:

1. El [Debian Security Tracker](https://security-tracker.debian.org/tracker/) (estado en *trixie* y aviso DSA).
2. El [catálogo de vulnerabilidades de INCIBE-CERT](https://www.incibe.es/incibe-cert/alerta-temprana/vulnerabilidades) (descripción en castellano).
3. El [catálogo KEV](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) (¿se está explotando?).

Decide la **prioridad**: ¿el servicio afectado está expuesto en red? ¿se explota activamente? Relaciónalo con el ciclo de gestión de vulnerabilidades de la [teoría](/ud04/ud04-teoria/).

### 4. Complemento: imágenes de contenedores (opcional)

Si usas Docker (por ejemplo, con n8n), las **imágenes** también tienen paquetes vulnerables. [Trivy](https://trivy.dev/) es un escáner libre que las analiza:

```bash
trivy image --severity HIGH,CRITICAL php:8.4-apache
```

---

## Búsqueda de vulnerabilidades de aplicaciones web

{{< practica etiqueta="Búsqueda" num="4.D" tipo="Autónoma" duracion="1 h · trabajo autónomo" nivel="1" ra="RA2:a,c" entorno="Navegador" entrega="tabla de avisos" >}}

1. En los [avisos de INCIBE-CERT](https://www.incibe.es/incibe-cert/alerta-temprana/avisos), busca «**inyección SQL**» y elige **tres avisos** de los últimos 12 meses (procura que uno afecte a un producto de un fabricante español).
2. Completa:

| Aviso (fecha) | Producto | CVE | CVSS | ¿Requiere autenticación? | Solución |
|---|---|---|---|---|---|
| | | | | | |

3. Repite la búsqueda con «**inyección de comandos**» o «*command injection*». ¿Qué tipo de productos aparecen más (aplicaciones web, *routers*, dispositivos industriales)?
4. Lee el artículo de INCIBE [«Ataques de inyección SQL: una amenaza para tu web»](https://www.incibe.es/empresas/blog/ataques-inyeccion-sql-amenaza-tu-web) y relaciona cada recomendación con una medida del caso 4.A.
5. Lee el caso real de la Línea 017 [«Un empleado introduce código malicioso y roba un millón de euros»](https://www.incibe.es/linea-de-ayuda-en-ciberseguridad/casos-reales/un-empleado-introduce-codigo-malicioso-y-roba-un-millon-de-euros) (modificación de la pasarela de pagos de una web). ¿Qué controles de esta unidad habrían detectado antes el cambio (integridad de ficheros con AIDE, auditoría, mínimo privilegio, revisión de copias)?
6. Consulta la ficha de la categoría *Injection* del [OWASP Top 10](https://owasp.org/Top10/) y anota tres ejemplos de inyección distintos de SQL.

---

## Qué debes saber explicar

- Por qué concatenar datos del usuario en una consulta SQL o en una orden del sistema es una vulnerabilidad.
- Qué hace una **consulta preparada** y por qué es la solución, frente a «filtrar caracteres».
- Cómo el **mínimo privilegio** (usuario de BD, usuario del servidor web) limita el daño aunque haya una vulnerabilidad.
- Cómo se **detecta** un ataque en los registros de Apache y con `auditd`.
- Cómo buscar los CVE que afectan a tus paquetes (`debsecan`) y priorizarlos.

## Referencias

- OWASP. [SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) y [OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html).
- PHP. [Sentencias preparadas con mysqli](https://www.php.net/manual/es/mysqli.quickstart.prepared-statements.php) y [`escapeshellarg`](https://www.php.net/manual/es/function.escapeshellarg.php).
- INCIBE. [Ataques de inyección SQL: una amenaza para tu web](https://www.incibe.es/empresas/blog/ataques-inyeccion-sql-amenaza-tu-web).
- CISA. [AA23-158A: CL0P Ransomware Gang Exploits CVE-2023-34362 MOVEit Vulnerability](https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-158a).
- TechRadar (2026). [Hidden daily passwords and command injection flaws in Danfoss supermarket systems](https://techradar.com/pro/a-nightmare-scenario-for-supermarkets-hidden-daily-passwords-and-command-injection-flaws-leave-thousands-of-danfoss-supermarket-systems-open-to-remote-takeover).
- Debian. [debsecan](https://wiki.debian.org/DebianSecurity/debsecan) y [Security Tracker](https://security-tracker.debian.org/tracker/).
- [sqlmap](https://sqlmap.org/).
- INCIBE, Línea 017. [Caso real: un empleado introduce código malicioso y roba un millón de euros](https://www.incibe.es/linea-de-ayuda-en-ciberseguridad/casos-reales/un-empleado-introduce-codigo-malicioso-y-roba-un-millon-de-euros).
