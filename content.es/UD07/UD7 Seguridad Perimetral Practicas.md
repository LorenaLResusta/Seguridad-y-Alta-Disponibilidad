# UD7 - Prácticas: seguridad perimetral

> Configuración y validación de controles perimetrales mediante evidencias técnicas reproducibles.

| Datos de las prácticas | Información |
| --- | --- |
| Módulo | Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR |
| Modalidad | Semipresencial |
| Duración estimada | 8 horas |
| Entorno | Máquinas virtuales, redes y servicios de entorno de pruebas |

## 1. Objetivos

- Diseñar un perímetro con WAN, LAN, DMZ y red de gestión.
- Aplicar políticas de firewall con denegación por defecto y mínimo privilegio.
- Configurar NAT de salida y publicar servicios de forma controlada.
- Analizar registros de firewall y comprobar reglas permitidas y denegadas.
- Configurar proxy directo, proxy inverso y controles de aplicación.
- Valorar la disponibilidad y la recuperación de los servicios perimetrales.

## 2. Alcance y preparación

Todas las acciones se realizan exclusivamente sobre VM, direcciones, redes y servicios autorizados. No publiques servicios de administración en Internet, no modifiques firewalls de producción y no generes tráfico de denegación de servicio.

Antes de cada práctica, crea una *snapshot* de las máquinas afectadas. Mantén una tabla de trabajo con interfaces, direcciones, reglas, cambios y resultado de cada prueba. Las evidencias consistirán en exportaciones de configuración sin secretos, salidas de comandos, extractos anonimizados de logs y tablas de resultados.

El escenario base usa un firewall pfSense u OPNsense, una VM cliente en LAN y una VM servidor en DMZ. Para las prácticas de proxy y alta disponibilidad se puede añadir una o más VM Linux propias.

## 3. Práctica 1 - Perímetro, zonas y política base

### 3.1. Topología y direccionamiento

Configura un firewall con las siguientes zonas:

| Zona | Red de ejemplo | Función |
| --- | --- | --- |
| WAN | NAT o puente de entorno de pruebas | Conexión externa simulada. |
| LAN | `192.168.20.0/24` | Equipos corporativos. |
| DMZ | `192.168.30.0/24` | Servicios publicados. |
| Gestión | `192.168.99.0/24` | Administración restringida. |

Asigna al firewall la primera dirección útil de cada subred. Configura cliente y servidor con direcciones coherentes, puerta de enlace y DNS de entorno de pruebas. Describe qué interfaces o VLAN representan cada zona y qué activos deben residir en ella.

### 3.2. Política de mínimo privilegio

Crea una matriz de filtrado inicial:

| Origen | Destino | Servicio | Acción | Motivo |
| --- | --- | --- | --- | --- |
| LAN | WAN | DNS, HTTP y HTTPS | Permitir | Acceso corporativo necesario. |
| LAN | DMZ | ICMP, HTTP, HTTPS y SSH | Permitir | Uso y administración controlados. |
| DMZ | LAN | Cualquiera | Denegar | Contención de un servidor publicado. |
| Gestión | Firewall y equipos | HTTPS y SSH | Permitir | Administración restringida. |
| Cualquier zona | Cualquier destino no definido | Cualquiera | Denegar | Política por defecto. |

Aplica las reglas en el orden adecuado y comprueba los flujos desde las VM. Entrega la tabla final de reglas y una tabla de resultados con origen, destino, servicio, resultado esperado y resultado obtenido.

## 4. Práctica 2 - NAT y publicación segura en DMZ

### 4.1. Servidor web de entorno de pruebas

En la VM de DMZ instala un servidor web de prueba y limita su firewall local a los servicios necesarios:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf install -y httpd
sudo systemctl enable --now httpd
echo 'Servicio web de la DMZ' | sudo tee /var/www/html/index.html

# Debian o Ubuntu
sudo apt update && sudo apt install -y apache2
sudo systemctl enable --now apache2
echo 'Servicio web de la DMZ' | sudo tee /var/www/html/index.html
```

Comprueba el servicio desde LAN mediante `curl` y conserva la salida como evidencia. El servidor de la DMZ no debe incluir servicios o cuentas que no sean necesarios para la práctica.

### 4.2. NAT y reglas asociadas

Configura NAT de salida para LAN y, solo si está justificado, para DMZ. Publica HTTPS desde una IP o puerto WAN de entorno de pruebas hacia el servidor de DMZ. Como ejercicio adicional, usa un puerto externo no estándar para una administración SSH temporal, limitada a una IP de origen de entorno de pruebas y documenta por qué esta medida no sustituye una VPN.

Verifica que el servicio web publicado responde desde una VM externa de pruebas y que otros puertos no publicados permanecen inaccesibles. Revisa los registros del firewall y redacta una tabla con la traducción configurada, regla asociada y resultado de la prueba.

## 5. Práctica 3 - Firewall Linux y fortificación TCP/IP

En una VM Linux de entorno de pruebas, identifica el sistema de filtrado activo:

```bash
sudo firewall-cmd --list-all
sudo nft list ruleset
```

Crea reglas que permitan el servicio web solo desde la subred LAN de la práctica. Valida desde una VM permitida y otra ubicada en una red no autorizada. Antes de modificar parámetros del núcleo, revisa su valor actual:

```bash
sysctl net.ipv4.ip_forward
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.log_martians
```

En un host que no sea router, guarda esta configuración en `/etc/sysctl.d/99-perimetro.conf`:

```text
net.ipv4.ip_forward = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.log_martians = 1
```

Aplica los cambios con `sudo sysctl --system`, verifica los valores y explica por qué no se deben aplicar sin adaptación en un gateway, un firewall o un servidor VPN.

## 6. Práctica 4 - Registro, alertas y respuesta inicial

Activa el registro de las reglas de bloqueo relevantes en el firewall del entorno de pruebas. Genera de forma controlada un intento de conexión no permitido desde LAN a DMZ y otro desde DMZ a LAN. No uses técnicas de evasión ni herramientas contra destinos ajenos.

Para cada evento, recoge fecha y hora, interfaz, IP de origen y destino, protocolo, puerto, regla aplicada y acción. Sincroniza la hora de las VM y propone qué eventos deberían enviarse a un servidor de logs o SIEM: cambios de reglas, autenticaciones administrativas, bloqueos repetidos, fallos VPN y alertas IDS/IPS.

Elabora un procedimiento breve de respuesta: validación de la alerta, contención, conservación de evidencias, comunicación, corrección y revisión posterior. Distingue una alerta que requiere investigación de un falso positivo documentado.

## 7. Práctica 5 - Proxy directo con Squid

Instala Squid en una VM AlmaLinux 9 y crea una copia de seguridad de la configuración:

```bash
sudo dnf install -y squid
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.bak
```

Define una ACL para la subred LAN de prácticas. Ordena las directivas para aplicar primero bloqueos específicos, después autorización de clientes permitidos y finalmente `http_access deny all`. Valida la sintaxis y activa el servicio:

```bash
sudo squid -k parse
sudo systemctl enable --now squid
```

Configura una VM cliente para usar el proxy en `IP_SQUID:3128`. Prueba un destino de entorno de pruebas permitido y una entrada de bloqueo basada en un dominio de pruebas o ficticio. Analiza `/var/log/squid/access.log` e identifica cliente, destino, método HTTP y resultado. Explica las limitaciones de filtrar HTTPS sin una arquitectura de inspección TLS, certificados gestionados y requisitos de privacidad.

## 8. Práctica 6 - Proxy inverso, TLS y WAF

En una VM Linux ejecuta dos servicios HTTP de prueba propios en los puertos `8081` y `8082`. Instala Nginx y configura un proxy inverso que publique ambos servicios bajo rutas diferentes:

```nginx
server {
    listen 80;
    server_name _;

    location /app-a/ {
        proxy_pass http://127.0.0.1:8081/;
    }

    location /app-b/ {
        proxy_pass http://127.0.0.1:8082/;
    }
}
```

Valida con `sudo nginx -t`, activa el servicio y prueba las rutas con `curl`. Demuestra que los puertos internos no se exponen a las otras VM. Añade TLS con un certificado de entorno de pruebas y comprueba el protocolo y certificado utilizado con `curl -vk https://HOST_DE_PRUEBAS/`.

Investiga un WAF compatible con el entorno, como ModSecurity con el conjunto de reglas OWASP CRS. Explica dónde se situaría, qué tipos de solicitudes puede inspeccionar y por qué debe iniciarse en modo de detección antes de habilitar bloqueos. No generes cargas de ataque contra aplicaciones ajenas.

## 9. Práctica 7 - Alta disponibilidad y recuperación del perímetro

Diseña una propuesta para evitar que el firewall sea un SPOF. Incluye dos firewalls, enlaces redundantes, alimentación, red de gestión, DNS, sincronización de configuración o estado, dirección virtual y monitorización. Indica qué modelo usarías, activo-pasivo o activo-activo, y por qué.

En un entorno de pruebas que disponga de recursos, configura un par de firewalls con una dirección virtual mediante CARP o una alternativa equivalente. Realiza una conmutación planificada y registra tiempo de interrupción, comportamiento de las conexiones existentes, registros generados y recuperación del nodo original. Si el entorno de pruebas no dispone de dos firewalls, presenta el diseño, la secuencia de conmutación y el plan de pruebas sin realizar el despliegue.

Realiza una copia de la configuración, guárdala cifrada en una ubicación de entorno de pruebas separada y describe el procedimiento para restaurarla en una VM de sustitución.

## 10. Actividades

1. Compara firewall de paquetes, *stateful*, de aplicación y NGFW según visibilidad y limitaciones.
2. Diseña la matriz de comunicaciones para Internet, LAN, DMZ, VPN y gestión.
3. Explica por qué NAT no sustituye el filtrado de firewall.
4. Propón controles para un servidor web en DMZ que necesita una base de datos interna.
5. Analiza cinco eventos de firewall y prioriza cuáles investigarías.
6. Compara proxy directo, proxy inverso y WAF según los activos que protegen.
7. Identifica los SPOF de una arquitectura con firewall, enlace WAN, DNS y proxy únicos.

## 11. Autoevaluación

1. ¿Qué función cumple un firewall?
2. ¿Qué diferencia existe entre filtrado de paquetes y *stateful*?
3. ¿Qué significa denegar por defecto?
4. ¿Qué es NAT y qué no protege por sí solo?
5. ¿Qué es una DMZ?
6. ¿Por qué DMZ-LAN debe ser especialmente restrictivo?
7. ¿Qué información aporta un registro de firewall?
8. ¿Qué diferencia existe entre proxy directo e inverso?
9. ¿Qué limita el filtrado de HTTPS sin inspección TLS?
10. ¿Qué función puede realizar un WAF?
11. ¿Por qué un firewall puede ser un SPOF?
12. ¿Qué debe incluir una prueba de conmutación?

## 12. Tarea evaluable única - Diseño de seguridad perimetral

Entrega una memoria en PDF o Markdown para una empresa de 40 usuarios con una sede, servicios internos, una aplicación web pública, WLAN corporativa e invitados, acceso remoto y necesidad de controlar navegación.

La memoria debe incluir:

1. Diagrama lógico con WAN, LAN, DMZ, VPN, gestión, firewall, proxy y controles de monitorización.
2. Inventario de activos, amenazas y puntos únicos de fallo.
3. Tabla de redes y matriz de reglas de firewall con denegación por defecto.
4. Diseño de NAT, publicación del servicio web y controles DMZ-LAN.
5. Propuesta de proxy directo, proxy inverso y WAF cuando proceda.
6. Registros, alertas y procedimiento básico de respuesta.
7. Medidas de disponibilidad, actualizaciones, copia de configuración y recuperación.
8. Plan de pruebas con resultados esperados, reversión y justificación técnica.

| Criterio | Peso |
| --- | ---: |
| Arquitectura, activos y amenazas | 15 % |
| Firewall, reglas y segmentación | 25 % |
| NAT, DMZ y publicación segura | 15 % |
| Registros, respuesta y firewall Linux | 10 % |
| Proxies, TLS y WAF | 15 % |
| Disponibilidad y recuperación del perímetro | 10 % |
| Evidencias técnicas y justificación | 10 % |
| **Total** | **100 %** |

## 13. Recursos

- [Documentación de pfSense](https://docs.netgate.com/pfsense/en/latest/)
- [OPNsense](https://docs.opnsense.org/)
- [Netfilter](https://www.netfilter.org/)
- [nftables](https://wiki.nftables.org/)
- [Squid](https://www.squid-cache.org/Doc/)
- [Nginx: reverse proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [OWASP ModSecurity Core Rule Set](https://coreruleset.org/)
- [CARP en pfSense](https://docs.netgate.com/pfsense/en/latest/highavailability/index.html)
