---
title: "Seguridad perimetral: cortafuegos, proxy, VPN y acceso remoto"
weight: 1
bookToc: true
---

# UD6 · Seguridad perimetral: cortafuegos, *proxy*, VPN y acceso remoto

## Resumen del tema

Una red conectada a Internet necesita **fronteras**: puntos donde se decide qué tráfico entra, qué tráfico sale y quién puede acceder desde fuera. En esta unidad recorremos esas fronteras de fuera hacia dentro:

1. **El perímetro**: qué zonas existen, qué es una DMZ y cómo se organizan los cortafuegos que las separan.
2. **El cortafuegos**: qué filtra, a qué nivel y con qué herramientas (`nftables` en Linux, OPNsense, el cortafuegos de Windows).
3. **Los *proxy***: intermediarios que controlan la navegación de los usuarios (*proxy* directo) o protegen los servidores publicados (*proxy* inverso).
4. **El acceso remoto**: VPN, servidores de salto y autenticación centralizada (RADIUS) para que el personal que teletrabaja entre **solo** a lo que necesita.

El hilo conductor es el proyecto transversal [Mediterránea Dental](/guia/proyecto-clinica/): una clínica con una sede, una delegación pequeña y dos personas en teletrabajo, que tiene que publicar su web de citas sin poner en peligro los historiales clínicos (datos de salud, categoría especial del RGPD).

{{< ra "RA1:h" "RA3:a,b,c,d,e,f,g" "RA4:a,b,c,d,e,f,g,h" "RA5:a,b,c,d,e,f,g,h,i" >}}

### Planificación de la unidad

| Bloque | Horas |
|---|---|
| Teoría | 9 h |
| [Prácticas](/ud06-seguridad-perimetral/ud06-practicas/) | 14 h |
| Evaluación (prueba escrita y entrega de la Tarea del proyecto) | 2 h |
| **Total** | **25 h** |

| Apartado de la teoría | Horas | CE |
|---|---|---|
| 1. Introducción: escenarios que exigen fortificar la red | 0,5 h | RA1.h, RA3.a |
| 2. Seguridad perimetral: zonas, DMZ, arquitecturas y *Zero Trust* | 1 h | RA3.b |
| 3. Cortafuegos: tipos, niveles de filtrado y planificación | 1 h | RA4.a, RA4.b, RA4.c |
| 4. `nftables` y NAT | 1,5 h | RA4.d |
| 5. Otras plataformas: `firewalld`, UFW, OPNsense y Windows | 0,5 h | RA4.f |
| 6. Registros, diagnóstico y pruebas | 0,5 h | RA4.e, RA4.g |
| 7. Servidores *proxy*: Squid, PAC/WPAD, modo transparente, Nginx y WAF | 1,5 h | RA5.a a RA5.h |
| 8. Redes privadas virtuales (VPN) | 1 h | RA3.c, RA3.d |
| 9. Acceso remoto seguro y AAA | 1 h | RA3.c, RA3.e, RA3.f, RA3.g |
| 10. Gestión, documentación, alta disponibilidad y ejemplo integrado | 0,5 h | RA4.h, RA5.i |
| **Total** | **9 h** | |

### Objetivos de aprendizaje

Al terminar esta unidad serás capaz de:

- Describir escenarios con conexión a redes públicas que exigen fortificar la red interna y justificar un plan integral de protección perimetral.
- Clasificar las zonas de riesgo y elegir una arquitectura perimetral (subred protegida débil o fuerte), explicando su relación con el modelo de confianza cero.
- Explicar las características, los tipos y los niveles de filtrado de un cortafuegos, y planificar su ubicación con una **matriz de flujos**.
- Configurar un cortafuegos con `nftables` (política por defecto, estado de las conexiones, NAT, registro) aplicando los cambios con copia previa, comprobación de sintaxis y reversión automática.
- Comparar implementaciones software y hardware (`firewalld`, UFW, OPNsense, pfSense, Windows) y valorar un NGFW.
- Revisar los registros del cortafuegos y diagnosticar problemas de conectividad con un método ordenado.
- Instalar y configurar un *proxy*-caché (Squid) con ACL, autenticación, configuración de clientes (manual, PAC, WPAD) y modo transparente, y un *proxy* inverso (Nginx) con TLS.
- Implantar una VPN de acceso remoto (WireGuard) y comprender la sitio a sitio (IPsec/IKEv2) y la VPN sobre TLS (OpenVPN).
- Usar SSH como pasarela y servidor de salto, con túneles y certificados.
- Instalar un servidor RADIUS (FreeRADIUS) e integrarlo en la pasarela de acceso.
- Verificar desde el exterior que solo se exponen los servicios previstos y documentar la instalación.

---

## 1. Introducción: escenarios que exigen fortificar la red

Una pequeña clínica tiene una única conexión de fibra con una IP pública, un *router* del operador y todos los equipos en la misma red: recepción, gabinetes, el servidor con los historiales y el servidor web de citas. Un atacante que encuentre un fallo en la web (o una contraseña débil en un acceso remoto) llega, **sin ninguna otra barrera**, a los historiales clínicos. Este es el escenario que la unidad enseña a evitar.

### 1.1 Escenarios típicos (RA3.a)

| Escenario | Qué se expone | Riesgo principal | Medida de esta unidad |
|---|---|---|---|
| Publicar una web o una aplicación | Un servidor accesible desde Internet | Que su compromiso dé acceso a la red interna | DMZ, DNAT con filtrado, *proxy* inverso, WAF |
| Dar Internet a los usuarios | Salida de decenas de equipos | *Malware*, fuga de datos, uso indebido | Cortafuegos con estado, *proxy* directo, registros |
| Teletrabajo | Acceso desde redes domésticas o públicas | Robo de credenciales, equipos no controlados | VPN, MFA, servidor de salto, RADIUS |
| Delegaciones y proveedores | Enlaces entre sedes y terceros | Confianza excesiva en el otro extremo | VPN sitio a sitio con filtrado, mínimo privilegio |
| Servicios en la nube | Datos y aplicaciones fuera de la sede | El perímetro «ya no está» donde estaba | Identidad fuerte, cifrado, enfoque *Zero Trust* |

### 1.2 La necesidad de un plan integral de protección perimetral (RA1.h)

Proteger el perímetro no es instalar «un cortafuegos». Un **plan integral** responde, por escrito, a estas preguntas:

1. **Qué hay que proteger** y qué zonas existen (inventario y análisis de riesgos de la [UD1](/ud01-seguridad-informatica/ud01-teoria/)).
2. **Qué tráfico debe poder cruzar cada frontera** (matriz de flujos).
3. **Con qué elementos** se controla: cortafuegos, *proxy*, VPN, IDS/IPS, registros.
4. **Cómo se detecta** un fallo o un ataque (registros, alertas, [UD5](/ud05-seguridad-redes/ud05-teoria/)).
5. **Cómo se cambia y se recupera** (gestión de cambios, copias, redundancia, [UD7](/ud07-alta-disponibilidad/ud07-teoria/)).
6. **Quién es responsable** y cómo se documenta.

> [!IMPORTANT]
> El perímetro es **una capa** de la defensa en profundidad, no la única. Lo que protege dentro de la LAN (bastionado de [UD4](/ud04-fortificacion-hosts/ud04-teoria/), segmentación de [UD5](/ud05-seguridad-redes/ud05-teoria/)) sigue siendo imprescindible: un perímetro perfecto no sirve si un portátil infectado entra por la puerta de delante.

### 1.3 Caso de estudio: Mediterránea Dental

Hoy la clínica tiene una red plana detrás de un *router* doméstico, con un puerto redirigido al servidor web. El encargo es **diseñar e implantar el perímetro**: separar la web de citas de la red interna, controlar la salida a Internet, permitir el teletrabajo con VPN y dejar todo documentado. Las prácticas de la unidad construyen ese perímetro pieza a pieza sobre el laboratorio del proyecto.

---

## 2. Seguridad perimetral: zonas, DMZ y arquitecturas

### 2.1 Elementos básicos del perímetro

| Elemento | Función | Dónde se estudia |
|---|---|---|
| ***Router* frontera** | Conecta con el proveedor; primer filtrado grueso (ACL, antifalsificación de origen) | Este apartado |
| **Cortafuegos** (*firewall*) | Decide qué tráfico cruza cada frontera según reglas | Apartados 3 a 6 |
| ***Proxy*** | Intermedia la navegación (directo) o la publicación (inverso) | Apartado 7 |
| **IDS/IPS** | Detecta (o bloquea) tráfico malicioso | [UD5](/ud05-seguridad-redes/ud05-teoria/) |
| **Pasarela VPN / de acceso remoto** | Termina túneles cifrados del personal remoto y de las delegaciones | Apartados 8 y 9 |
| **Servidor de registros / SIEM** | Centraliza y correlaciona los eventos | [UD5](/ud05-seguridad-redes/ud05-teoria/) |

En una organización pequeña, varias funciones comparten máquina (un único equipo hace de *router*, cortafuegos, VPN y *proxy*). En una grande se reparten en equipos y fabricantes distintos. El **papel** de cada elemento es el mismo.

### 2.2 Zonas de riesgo y perímetros de red (RA3.b)

Una **zona de seguridad** agrupa equipos con el mismo nivel de confianza y las mismas necesidades de comunicación. Clasificar las zonas es el primer paso del diseño:

| Zona | Contenido | Confianza | Quién puede iniciar conexiones hacia ella |
|---|---|---|---|
| **WAN / Internet** | Red pública | Ninguna | — |
| **DMZ** (*DeMilitarized Zone*) | Servidores publicados: web, correo, DNS público, pasarela VPN | Baja (expuesta) | Internet, solo a servicios concretos |
| **LAN de usuarios** | Puestos de trabajo, impresoras | Media | Solo desde dentro |
| **Servidores internos** | Gestión de pacientes, ficheros, directorio | Alta | La LAN y la DMZ, por puertos concretos |
| **Gestión** | Administración de equipos y del cortafuegos | Muy alta | Solo administradores |
| **Invitados / IoT** | Equipos no gestionados | Nula | Solo salida a Internet |

Una **DMZ** es una red intermedia que aloja los servicios que **deben** ser accesibles desde Internet. Si uno de ellos se compromete, el atacante queda atrapado en la DMZ en lugar de aterrizar en la LAN. La clave de su diseño son cuatro reglas de dirección de flujo:

1. **Internet → DMZ**: solo los puertos de los servicios publicados.
2. **Internet → LAN**: nada (salvo respuestas a conexiones que la LAN haya iniciado).
3. **LAN → DMZ**: solo lo necesario (administración, pruebas).
4. **DMZ → LAN: denegado y registrado.** Un intento de la DMZ hacia la LAN es, casi siempre, una señal de compromiso.

{{< figura src="ud06/dmz-tres-zonas.svg" alt="Cortafuegos de tres zonas con WAN, LAN y DMZ" caption="Figura 6.1. Arquitectura de tres zonas: lo publicado vive en la DMZ, que no puede iniciar conexiones hacia la LAN." >}}

### 2.3 Arquitecturas de red perimetral

Con los años han aparecido varios diseños, de menos a más defensa en profundidad:

| Arquitectura | Descripción | Limitaciones |
|---|---|---|
| ***Router* apantallado** (*screening router*) | Un *router* con ACL entre Internet y la red | Una sola barrera, sin DMZ |
| ***Host* bastión** | Un equipo muy fortificado que ofrece los servicios expuestos | Si cae, el atacante está dentro |
| **Doble interfaz** (*dual-homed host*) | Un equipo con dos tarjetas que separa dos redes sin reenviar | Mismo riesgo que el bastión |
| **Subred protegida débil** (*three-legged*) | **Un** cortafuegos con tres interfaces: WAN, LAN y DMZ | El cortafuegos es la única barrera y un punto único de fallo |
| **Subred protegida fuerte** (*screened subnet*) | **Dos** cortafuegos en serie: externo → DMZ → interno (idealmente de fabricantes distintos) | Más coste y gestión; máxima defensa en profundidad |

```mermaid
flowchart LR
  I((Internet)) --- FW{{"Cortafuegos<br/>tres patas"}}
  FW --- D["DMZ<br/>web de citas<br/>172.16.10.0/24"]
  FW --- L["LAN<br/>192.168.10.0/24"]
```

```mermaid
flowchart LR
  I((Internet)) --- F1{{"Cortafuegos<br/>externo"}}
  F1 --- D["DMZ<br/>servidores publicados"]
  D --- F2{{"Cortafuegos<br/>interno"}}
  F2 --- L["LAN y servidores<br/>internos"]
```

> [!NOTE]
> **Débil o fuerte no significa «mala» o «buena»**: es una cuestión de proporcionalidad. Para Mediterránea Dental, con un solo equipo de perímetro, la subred protegida débil (un cortafuegos de tres patas) es razonable **si** se vigila y se hace redundante ([UD7](/ud07-alta-disponibilidad/ud07-teoria/)). Dos cortafuegos de fabricantes distintos se justifican cuando un fallo de implementación de uno de ellos no debe dejar pasar el tráfico (infraestructuras críticas, ENS de categoría alta).

### 2.4 Del modelo perimetral al modelo de confianza cero (*Zero Trust*)

El modelo clásico se resume en «dentro de la red, confianza; fuera, desconfianza». Falla cuando:

- el atacante **ya está dentro** (un portátil infectado, un correo de *phishing*);
- el personal trabaja **fuera** de la sede y los datos están en la nube;
- las aplicaciones se publican en Internet y no hay un «dentro» claro.

La **confianza cero** (*Zero Trust*, NIST SP 800-207) parte de «**nunca confíes, verifica siempre**». No es un producto, es un conjunto de principios:

| Principio | Qué significa en la práctica |
|---|---|
| Verificar explícitamente | Autenticar y autorizar **cada acceso** según identidad, dispositivo y contexto |
| Mínimo privilegio | Permitir solo el acceso necesario y durante el tiempo necesario |
| Asumir la brecha | Segmentar, cifrar y registrar como si el atacante ya estuviera dentro |
| Microsegmentación | Reglas entre cargas de trabajo, no solo en el borde |

El perímetro **sigue siendo útil**, pero se complementa: VPN con segundo factor (apartado 8), RADIUS (apartado 9), segmentación y ACL ([UD5](/ud05-seguridad-redes/ud05-teoria/)) y registros centralizados.

---

## 3. Cortafuegos: tipos, niveles y planificación

### 3.1 Características y funciones (RA4.a)

Un **cortafuegos** (*firewall*) es un sistema, software o hardware, que **controla el tráfico entre redes** aplicando un conjunto ordenado de reglas. Sus funciones principales son:

- **Filtrar**: permitir lo autorizado y descartar el resto.
- **Traducir direcciones** (NAT) para compartir IP y publicar servicios.
- **Registrar** qué se permite y qué se descarta, para auditar y detectar ataques.
- **Delimitar zonas**: es el punto donde se aplican las reglas entre WAN, LAN y DMZ.
- **Actuar de pasarela** de VPN, de *proxy* o de IDS/IPS, según el producto.

Un cortafuegos **no** protege frente a lo que no ve: tráfico cifrado que atraviesa un puerto permitido (por ejemplo, HTTPS con *malware*), ataques desde dentro o equipos infectados que llegan por un medio extraíble.

### 3.2 Niveles de filtrado del tráfico (RA4.b)

| Nivel | Capa OSI | Qué examina | Ejemplo de regla |
|---|---|---|---|
| **Filtrado de paquetes** (sin estado) | 3-4 | IP de origen y destino, protocolo, puertos, de **cada paquete** por separado | «Permitir TCP al puerto 80» |
| **Con estado** (*stateful*) | 3-4 | Lo anterior **más el estado de la conexión** (nueva, establecida, relacionada) | «Permitir respuestas a conexiones que yo inicié» |
| **De aplicación / *proxy*** | 7 | El contenido del protocolo (URL, métodos, comandos) | «Bloquear descargas `.exe`» |
| **NGFW** (*Next-Generation Firewall*) | 3-7 | Estado + identificación de aplicaciones y usuarios, IPS, inspección TLS, antimalware | «Bloquear BitTorrent a los alumnos» |
| **WAF** (*Web Application Firewall*) | 7 (HTTP) | Peticiones web: detecta inyecciones SQL, XSS... | «Bloquear una petición con `<script>`» |

**Por qué importa el estado.** Un filtro sin estado trata cada paquete aislado: para que funcionen las conexiones salientes, debe permitir **todo** el tráfico de respuesta hacia puertos altos (mayores de 1024), un agujero enorme. Un cortafuegos con estado **recuerda** las conexiones iniciadas desde dentro y solo deja entrar las respuestas que les corresponden. En Linux lo hace el módulo **conntrack**, que clasifica cada paquete:

| Estado (`ct state`) | Significado |
|---|---|
| `new` | Primer paquete de una conexión nueva |
| `established` | Conexión ya vista en los dos sentidos |
| `related` | Conexión nueva asociada a otra existente (un error ICMP, el canal de datos de FTP) |
| `invalid` | Paquete que no encaja con ninguna conexión: se descarta |

### 3.3 Cortafuegos software, hardware y de nueva generación (RA4.f)

| Tipo | Ejemplos | Ventajas | Inconvenientes |
|---|---|---|---|
| **Software en un sistema operativo** | `nftables`, `firewalld`, UFW (Linux); Microsoft Defender Firewall (Windows) | Gratis, flexible, automatizable | Requiere administración experta; comparte máquina con otros servicios |
| **Distribución dedicada** (software libre) | **OPNsense**, **pfSense CE** | Interfaz web, VPN, IDS, *proxy* y alta disponibilidad integrados | Hay que dimensionar el *hardware* y aprender la plataforma |
| ***Appliance* hardware** | Fortinet, Palo Alto, Cisco, Sophos, WatchGuard | Hardware especializado, soporte y NGFW completo | Coste y licencias |
| **Cortafuegos de la nube** | Grupos de seguridad de AWS o Azure | Escalables, integrados con la infraestructura | Específicos de cada proveedor |

Un **NGFW** (*Next-Generation Firewall*) no se limita a puertos y direcciones: identifica la **aplicación** aunque use un puerto inesperado, asocia el tráfico a **usuarios** (integración con el directorio), incorpora **prevención de intrusiones**, puede **inspeccionar TLS** y bloquea *malware* conocido. En software libre, OPNsense con Suricata o Zenarmor se acerca a ese modelo. La inspección TLS plantea las mismas implicaciones legales y de privacidad que se describen en el apartado 7.1.

### 3.4 Planificación y ubicación: política por defecto y matriz de flujos (RA4.c)

Un cortafuegos se **ubica** en cada frontera entre zonas de distinta confianza. Su política por defecto debe ser **«denegar todo»** y permitir solo lo que se haya justificado. Antes de escribir una sola regla se construye una **matriz de flujos**: una tabla con qué zona puede hablar con cuál, por qué puerto y para qué.

| # | Origen | Destino | Servicio | Acción | Justificación |
|---|---|---|---|---|---|
| 1 | Internet | `web01` (DMZ) | HTTPS 443/tcp (y 80/tcp para redirigir) | Permitir (DNAT) | Web de citas en línea |
| 2 | LAN | Internet | HTTP/HTTPS 80, 443/tcp | Permitir (vía *proxy*) | Navegación |
| 3 | LAN | Internet | DNS y NTP, 53 y 123/udp | Permitir | Resolución y hora |
| 4 | Puesto de administración | `fw01` | SSH 22/tcp | Permitir | Administración |
| 5 | LAN | DMZ | SSH, HTTP, HTTPS | Permitir | Administración y pruebas |
| 6 | DMZ | LAN | Cualquiera | **Denegar y registrar** | Contención de compromisos |
| 7 | DMZ | Internet | 80, 443/tcp, 53 y 123/udp | Permitir | Actualizaciones |
| 8 | Teletrabajo (VPN) | `srv-gestion` | HTTP/HTTPS, SSH | Permitir | Acceso a la aplicación |
| 9 | Cualquiera | Cualquiera | Cualquiera | **Denegar** | Política por defecto |

> [!TIP]
> Cada fila de la matriz se traduce en **una regla** y en **dos pruebas** (una positiva que debe funcionar y una negativa que debe fallar). La matriz es además la documentación del cortafuegos (RA4.h) y la base de las pruebas de aceptación.

---

## 4. Filtrado en Linux con `nftables` y NAT

> [!NOTE]
> **Sistema de referencia:** Debian 13 «trixie» con `nftables` 1.1.x. En Ubuntu Server LTS el paquete y el fichero `/etc/nftables.conf` son los mismos; en AlmaLinux 10 la configuración está en `/etc/sysconfig/nftables.conf` y el servicio gestor por defecto es `firewalld` (apartado 5.1).

### 4.1 Netfilter y `nftables`

**Netfilter** es el marco del núcleo de Linux que intercepta los paquetes en puntos concretos de su recorrido, llamados ***hooks***. **`nftables`** es la herramienta actual para definir reglas sobre esos *hooks*. **Sustituye a `iptables`, `ip6tables`, `arptables` y `ebtables`**, que se consideran heredadas: en las distribuciones modernas `iptables` suele ser una capa de compatibilidad que traduce a `nftables`.

```mermaid
flowchart LR
  E[Paquete entra] --> PRE["prerouting<br/>DNAT"]
  PRE --> R{"¿Destinado a<br/>este equipo?"}
  R -- sí --> IN[input]
  IN --> L[Proceso local]
  L --> OUT[output]
  OUT --> POST
  R -- "no: reenviar" --> FWD[forward]
  FWD --> POST["postrouting<br/>SNAT / masquerade"]
  POST --> S[Paquete sale]
```

| *Hook* | Cuándo se evalúa | Uso típico |
|---|---|---|
| `prerouting` | Nada más entrar, antes de decidir la ruta | **DNAT** (cambiar el destino), `redirect` |
| `input` | Paquetes **dirigidos al propio cortafuegos** | Proteger el equipo (SSH, ICMP, el servicio de *proxy*) |
| `forward` | Paquetes que el equipo **reenvía entre redes** | **Política entre zonas**: lo principal de un cortafuegos perimetral |
| `output` | Paquetes que genera el propio equipo | Limitar lo que el cortafuegos puede iniciar |
| `postrouting` | Justo antes de salir | **SNAT** y *masquerade* |

**Estructura de la configuración:** `tabla` → `cadena` → `regla`.

- **Tabla**: contenedor con una *familia* (`ip` = IPv4, `ip6`, `inet` = IPv4 e IPv6 a la vez, `bridge`, `arp`).
- **Cadena base**: lista de reglas enganchada a un *hook* (`type filter hook input priority filter; policy drop;`). La **prioridad** ordena las cadenas del mismo *hook*.
- **Regla**: condiciones más una acción (`accept`, `drop`, `reject`, `log`, `counter`, `dnat`, `masquerade`...).
- **Política** (`policy`): qué ocurre con lo que no coincide con ninguna regla. En un cortafuegos bien diseñado es **siempre `drop`**.

> [!NOTE]
> `drop` descarta el paquete **sin avisar** (el origen espera hasta agotar el tiempo); `reject` lo descarta y **responde** con un error (inmediato, pero revela que hay un filtro). Hacia Internet se usa `drop`; en la red interna, `reject` facilita el diagnóstico.

### 4.2 Comandos esenciales

`nft` es la orden que consulta y modifica el conjunto de reglas del núcleo. Casi todo lo que sigue necesita privilegios de administrador (`sudo`).

```bash
sudo nft list ruleset                  # muestra TODAS las reglas activas
sudo nft list table inet filtro        # muestra una tabla concreta
sudo nft -a list chain inet filtro reenvio    # -a añade el «handle» (identificador) de cada regla
sudo nft -c -f /etc/nftables.conf      # -c = check: COMPRUEBA la sintaxis sin aplicar nada
sudo nft -f /etc/nftables.conf         # -f = file: aplica el fichero
sudo nft delete rule inet filtro reenvio handle 12   # borra una regla concreta por su handle
sudo nft flush ruleset                 # borra TODAS las reglas: deja el equipo SIN filtrado
```

Para que las reglas se carguen en cada arranque, se usa el servicio `nftables` de **systemd**:

```bash
sudo systemctl enable --now nftables   # enable: arrancar siempre al iniciar; --now: además, arrancarlo ya
sudo systemctl status nftables --no-pager
```

> [!NOTE]
> **Qué es `systemctl`.** Es la orden que gestiona los servicios en sistemas con **systemd**. `enable` los marca para arrancar con el sistema, `start`/`stop` los arrancan o detienen ahora, `restart` los detiene y arranca (corta las conexiones activas) y `reload` les pide que relean su configuración sin cortar el servicio. Prefiere `reload` cuando el servicio lo admita.

Si heredas reglas de `iptables`, puedes traducirlas (revisa siempre el resultado):

```bash
iptables-translate -A INPUT -p tcp --dport 22 -j ACCEPT        # traduce una regla suelta
sudo iptables-save | sudo iptables-restore-translate            # traduce un conjunto completo
```

### 4.3 Cortafuegos de tres zonas: el *ruleset* de `fw01`

El laboratorio del proyecto tiene un cortafuegos `fw01` con tres interfaces:

| Zona | Interfaz | Red | Equipos |
|---|---|---|---|
| WAN | `enp0s3` | 10.0.2.0/24 (`fw01`: .10) | `atacante` (.50), `cli-remoto` (.60) |
| LAN | `enp0s8` | 192.168.10.0/24 (`fw01`: .1) | `srv-gestion` (.10), `srv-ficheros` (.11), `cli-recepcion` (.50) |
| DMZ | `enp0s9` | 172.16.10.0/24 (`fw01`: .1) | `web01` (.11), `web02` (.12) |

Este es el fichero `/etc/nftables.conf`, comprobado con `nft -c`. Implementa las filas 1 a 7 y 9 de la matriz del apartado 3.4:

```text
#!/usr/sbin/nft -f
# fw01 · Cortafuegos perimetral de Mediterránea Dental S. L. (Debian 13 · nftables)
# Zonas: WAN (enp0s3) · LAN (enp0s8) · DMZ (enp0s9)
flush ruleset

define WAN      = "enp0s3"
define LAN      = "enp0s8"
define DMZ      = "enp0s9"
define WEB_PUB  = 172.16.10.11                       # servidor publicado en la DMZ
define DMZ_SRV  = { 172.16.10.11, 172.16.10.12 }     # servidores de la DMZ alcanzables desde la LAN

table inet filtro {

  set admins {                                       # orígenes autorizados para administrar fw01
    type ipv4_addr
    flags interval
    elements = { 192.168.10.50 }
  }

  set bloqueados {                                   # IP bloqueadas con caducidad automática
    type ipv4_addr
    flags timeout
    timeout 1h
  }

  chain entrada {                                    # tráfico dirigido AL propio cortafuegos
    type filter hook input priority filter; policy drop;

    ip saddr @bloqueados drop
    ct state established,related accept
    ct state invalid drop
    iif "lo" accept

    iifname $LAN icmp type echo-request limit rate 10/second accept
    icmp type { destination-unreachable, time-exceeded } accept
    icmpv6 type { nd-neighbor-solicit, nd-neighbor-advert, nd-router-solicit, nd-router-advert } accept

    iifname $LAN ip saddr @admins tcp dport 22 accept            # SSH solo desde el puesto de administración

    limit rate 5/minute log prefix "FW-IN-DROP: " flags all counter
  }

  chain reenvio {                                    # tráfico ENTRE zonas
    type filter hook forward priority filter; policy drop;

    ct state established,related accept
    ct state invalid drop

    # Internet -> web publicada (solo lo que pasó por una regla DNAT)
    iifname $WAN oifname $DMZ ip daddr $WEB_PUB tcp dport { 80, 443 } ct status dnat counter accept

    # LAN -> DMZ: administración y pruebas
    iifname $LAN oifname $DMZ ip daddr $DMZ_SRV tcp dport { 22, 80, 443 } counter accept

    # LAN -> Internet: navegación, DNS y NTP
    iifname $LAN oifname $WAN tcp dport { 80, 443 } counter accept
    iifname $LAN oifname $WAN udp dport { 53, 123 } counter accept

    # DMZ -> Internet: actualizaciones, DNS y NTP
    iifname $DMZ oifname $WAN tcp dport { 80, 443 } counter accept
    iifname $DMZ oifname $WAN udp dport { 53, 123 } counter accept

    # DMZ -> LAN: PROHIBIDO; se registra porque indica un posible compromiso
    iifname $DMZ oifname $LAN limit rate 5/minute log prefix "DMZ-A-LAN: " flags all
    iifname $DMZ oifname $LAN counter drop

    limit rate 5/minute log prefix "FW-FWD-DROP: " flags all counter
  }

  chain salida {
    type filter hook output priority filter; policy accept;
  }
}

table ip nat {
  chain prerouting {
    type nat hook prerouting priority dstnat; policy accept;
    iifname $WAN tcp dport { 80, 443 } dnat to $WEB_PUB          # publica la web de la DMZ
  }
  chain postrouting {
    type nat hook postrouting priority srcnat; policy accept;
    oifname $WAN masquerade                                      # LAN y DMZ salen con la IP de la WAN
  }
}
```

**Cómo leerlo:**

- `define` crea **variables**: cambiar de interfaz o de servidor publicado es cambiar una línea.
- `set admins` es un **conjunto** con nombre: se amplía sin tocar las reglas (`sudo nft add element inet filtro admins { 192.168.10.51 }`).
- La cadena `entrada` protege **el propio cortafuegos**; la cadena `reenvio` aplica la política **entre zonas**. Las dos empiezan aceptando las respuestas de conexiones ya establecidas (`established,related`) y descartando lo inválido.
- `ct status dnat` exige que el paquete haya pasado por una regla DNAT: solo se acepta hacia la DMZ lo que se publicó **expresamente**.
- `counter` cuenta paquetes y bytes de cada regla: sirve para comprobar **qué regla atiende cada prueba**.
- Las reglas `log` van **al final** de cada cadena, con `limit rate`, para registrar lo descartado sin llenar el disco. `flags all` añade al mensaje las cabeceras IP y TCP.
- La tabla `nat` se evalúa **antes** del filtrado en `prerouting` (DNAT) y **después** en `postrouting` (SNAT).

### 4.4 Aplicación segura de cambios en un cortafuegos

Un cortafuegos con política `drop` mal aplicado **te deja sin acceso**, sobre todo si administras por SSH. Por eso todo cambio sigue un procedimiento fijo:

| Paso | Qué se hace | Por qué |
|---|---|---|
| 1 | **Copia** de la configuración y del estado actual | Poder volver atrás |
| 2 | **Comprobar la sintaxis** (`nft -c -f`) | Un error no debe dejar el cortafuegos a medio cargar |
| 3 | **Programar la reversión automática** («red de seguridad») | Si pierdes el acceso, el cambio se deshace solo |
| 4 | **Aplicar** el cambio | |
| 5 | **Probar** (positivas y negativas) | Comprobar que funciona lo permitido y falla lo prohibido |
| 6 | **Cancelar** la reversión y **hacerlo persistente** | Solo cuando todo es correcto |

```bash
# 1. Copia: del fichero y del estado actual del núcleo (con "flush ruleset" delante para poder reaplicarla tal cual)
sudo cp /etc/nftables.conf /etc/nftables.conf.bak
( echo "flush ruleset"; sudo nft list ruleset ) | sudo tee /root/fw-anterior.nft >/dev/null

# 2. Comprobación de sintaxis: no cambia nada, solo valida
sudo nft -c -f /etc/nftables.conf && echo "SINTAXIS CORRECTA"

# 3. Red de seguridad: dentro de 3 minutos se restaura el estado anterior
sudo systemd-run --on-active=3min --unit=deshacer-fw /usr/sbin/nft -f /root/fw-anterior.nft

# 4. Aplicar
sudo nft -f /etc/nftables.conf

# 5. ... realiza las pruebas de la matriz de flujos ...

# 6. Si todo es correcto: cancela la reversión y deja el cambio persistente
sudo systemctl stop deshacer-fw.timer
sudo systemctl enable --now nftables
```

**Explicación de las órdenes nuevas.** `systemd-run` crea una **unidad temporal** de systemd; `--on-active=3min` la programa para dentro de 3 minutos; `--unit=deshacer-fw` le da nombre (así luego se puede cancelar: se crea `deshacer-fw.timer` y `deshacer-fw.service`); lo que sigue es la orden que se ejecutará, aquí volver a cargar el estado anterior. Si todo sale bien, `systemctl stop deshacer-fw.timer` cancela la reversión.

> [!WARNING]
> Si olvidas cancelar la reversión, a los 3 minutos el cortafuegos **vuelve al estado anterior** (por ejemplo, a no filtrar nada). Es deliberado: es preferible un cortafuegos abierto un momento que una máquina inaccesible. Ten siempre abierta la **consola de la máquina virtual** como acceso de emergencia. Y **nunca** uses `nft flush ruleset` como solución permanente: deja el equipo sin ninguna protección.

> [!CAUTION]
> Elige **un solo gestor** de cortafuegos por equipo. Si usas `/etc/nftables.conf`, no tengas activos `firewalld` ni `ufw`: sus reglas se pisan y el comportamiento es impredecible.

### 4.5 Conjuntos, límites y bloqueos dinámicos

`nftables` permite reglas mucho más expresivas que una lista plana. Todos los ejemplos están comprobados con `nft -c`:

```text
table inet demo {
  set bloqueados {                 # direcciones bloqueadas con caducidad
    type ipv4_addr
    flags timeout
    timeout 1h
  }
  set ssh_ritmo {                  # medidor: lleva la cuenta de conexiones nuevas por origen
    type ipv4_addr
    flags dynamic,timeout
    timeout 1m
    size 65535
  }
  chain entrada {
    type filter hook input priority filter; policy drop;

    ip saddr @bloqueados drop                                     # descarta a los bloqueados
    fib saddr . iif oif missing drop                              # antifalsificación de origen (como rp_filter)
    tcp flags syn tcp dport 80 limit rate over 50/second burst 100 packets drop   # limita ráfagas de SYN

    # Más de 5 conexiones nuevas por minuto al SSH desde la misma IP: se bloquea esa IP 1 hora
    tcp dport 22 ct state new add @ssh_ritmo { ip saddr limit rate over 5/minute } add @bloqueados { ip saddr } drop
    tcp dport 22 ct state new accept
  }
}
```

```bash
sudo nft add element inet filtro bloqueados { 203.0.113.5 }         # bloquea una IP durante 1 hora (203.0.113.0/24 es una red de documentación)
sudo nft list set inet filtro bloqueados                              # ver el conjunto y los tiempos restantes
sudo nft delete element inet filtro bloqueados { 203.0.113.5 }        # desbloquear
```

Un **mapa** permite decidir por tabla; por ejemplo, publicar varios puertos externos hacia destinos distintos:

```text
table ip nat2 {
  map puertos_dnat {
    type inet_service : ipv4_addr . inet_service
    elements = { 8080 : 172.16.10.11 . 80, 8443 : 172.16.10.11 . 443 }
  }
  chain prerouting {
    type nat hook prerouting priority dstnat;
    dnat ip addr . port to tcp dport map @puertos_dnat
  }
}
```

### 4.6 NAT: traducción de direcciones

El **NAT** (*Network Address Translation*, RFC 3022) modifica las direcciones de los paquetes al cruzar el cortafuegos. **No es una medida de seguridad en sí** (la seguridad la da el filtrado con estado), pero oculta el direccionamiento interno y permite compartir una IP pública.

| Tipo | Qué cambia | Para qué | *Hook* |
|---|---|---|---|
| **SNAT** | IP **origen** (fija) | Salir con una IP pública conocida | `postrouting` |
| ***Masquerade*** | IP origen (la de la interfaz de salida, variable) | Salir con IP pública **dinámica** (DHCP) | `postrouting` |
| **DNAT** (*port forwarding*) | IP y/o puerto **destino** | **Publicar** un servicio interno | `prerouting` |
| ***Redirect*** | Destino = el propio equipo | Mandar tráfico a un servicio local (*proxy* transparente) | `prerouting` |

```mermaid
sequenceDiagram
  participant C as atacante 10.0.2.50
  participant F as fw01 WAN 10.0.2.10
  participant W as web01 172.16.10.11
  C->>F: SYN a 10.0.2.10:443
  Note over F: prerouting: DNAT a 172.16.10.11:443<br/>forward: ¿permitido? sí (ct status dnat)
  F->>W: SYN a 172.16.10.11:443
  W->>F: SYN-ACK (conntrack recuerda la traducción)
  F->>C: SYN-ACK desde 10.0.2.10:443
```

**Los cinco requisitos para que una publicación funcione** (y los motivos habituales de fallo):

1. Regla **DNAT** en `prerouting` (sin ella, el paquete llega al cortafuegos, no al servidor).
2. Regla de **`forward`** que permita el tráfico ya traducido (sin ella: *timeout*).
3. **`net.ipv4.ip_forward = 1`** (sin él, el equipo no reenvía).
4. El servidor de la DMZ tiene como **puerta de enlace** el cortafuegos (sin ello, llegan los SYN pero la respuesta no vuelve por `fw01`).
5. El servicio **escucha** en el puerto (si no, `Connection refused` inmediato).

> [!NOTE]
> **¿Y el *hairpin* NAT?** Se necesita cuando un cliente y el servidor publicado están en la **misma red** y el cliente accede por la IP pública: el servidor respondería directamente al cliente (sin pasar por el cortafuegos) y la conexión se rompería. En nuestra arquitectura la LAN y la DMZ son redes **distintas** y todo pasa por `fw01`: basta con una regla DNAT en `prerouting` también para la interfaz LAN (`iifname $LAN ip daddr 10.0.2.10 tcp dport { 80, 443 } dnat to $WEB_PUB`) y la regla de `forward` correspondiente.


### 4.7 Fortificación de la pila TCP/IP del cortafuegos

Un equipo que **reenvía** paquetes necesita ajustes de red distintos de los de un servidor normal (que viste en la [UD4](/ud04-fortificacion-hosts/ud04-teoria/): allí se desactivaba el reenvío; aquí se activa). Se hacen con `sysctl`, que lee y escribe parámetros del núcleo; el fichero va en `/etc/sysctl.d/`:

```bash
sudo tee /etc/sysctl.d/90-perimetro.conf >/dev/null <<'EOF'
# Es un router: reenvía paquetes entre zonas (¡solo con cortafuegos activo!)
net.ipv4.ip_forward = 1
# Descarta paquetes con un origen imposible por esa interfaz (antifalsificación)
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
# No acepta redirecciones ICMP ni enrutamiento de origen; tampoco las envía
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
# Registra paquetes con direcciones imposibles («marcianos»)
net.ipv4.conf.all.log_martians = 1
# Protección frente a inundación de SYN
net.ipv4.tcp_syncookies = 1
# No responde a ping dirigido a broadcast (evita amplificación)
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1
EOF
sudo sysctl --system            # recarga todos los ficheros de sysctl
sysctl net.ipv4.ip_forward net.ipv4.conf.all.rp_filter     # verifica
```

> [!WARNING]
> En `sysctl.d` **los comentarios van en su propia línea**: un `# comentario` detrás del valor pasa a formar parte del valor y el ajuste falla. Además, `rp_filter = 1` (modo estricto) descarta el tráfico con **rutas asimétricas**; si tu red las tiene (varios enlaces, algunos escenarios de VPN), usa el modo laxo `2`.

El tamaño de la tabla de conexiones (`net.netfilter.nf_conntrack_max`) solo existe cuando el módulo `nf_conntrack` está cargado (lo está en cuanto hay reglas con estado). Vigila su ocupación con `sudo conntrack -C` (conexiones actuales) frente a `sysctl net.netfilter.nf_conntrack_max`: si se llena, el cortafuegos descarta conexiones nuevas.

**Direcciones imposibles (*bogons*) desde Internet.** En una WAN real, nada que llegue de Internet puede tener como origen una IP privada (RFC 1918), de *loopback* o de enlace local: se descarta con `iifname $WAN ip saddr { 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8, 169.254.0.0/16 } drop`. **En nuestro laboratorio la WAN usa 10.0.2.0/24 (privada), por eso esa regla no se aplica.**

---

## 5. Otras plataformas de cortafuegos

### 5.1 `firewalld` y UFW: interfaces de gestión sobre el filtrado del núcleo

`nftables` es el **motor**; `firewalld` y UFW son **interfaces** que escriben las reglas por ti con un lenguaje más sencillo. No son cortafuegos distintos, son otra forma de configurar el mismo filtrado.

**`firewalld`** (AlmaLinux, Fedora, RHEL) trabaja con **zonas** (`external`, `internal`, `dmz`, `public`...) y **servicios**. Cada interfaz pertenece a una zona; la zona `external` activa *masquerade* por defecto. Usa `nftables` por debajo.

```bash
sudo firewall-cmd --permanent --zone=external --change-interface=enp0s3     # WAN
sudo firewall-cmd --permanent --zone=internal --change-interface=enp0s8     # LAN
sudo firewall-cmd --permanent --zone=dmz      --change-interface=enp0s9     # DMZ
sudo firewall-cmd --permanent --zone=external --add-forward-port=port=443:proto=tcp:toaddr=172.16.10.11   # publicar HTTPS
sudo firewall-cmd --reload                       # aplica la configuración permanente
sudo firewall-cmd --list-all-zones | less        # revisa el resultado
```

`--permanent` guarda la regla para los próximos arranques sin aplicarla ya; `--reload` la aplica sin cortar las conexiones. Sin `--permanent`, el cambio es temporal (se pierde al recargar).

**UFW** (*Uncomplicated Firewall*, Ubuntu y Debian) simplifica el filtrado de un **equipo** (no de un router). Está bien para proteger un servidor; para un cortafuegos de tres zonas es preferible `nftables` directamente.

```bash
sudo ufw default deny incoming                               # política por defecto: denegar la entrada
sudo ufw default allow outgoing
sudo ufw allow from 192.168.10.50 to any port 22 proto tcp   # SSH solo desde el puesto de administración
sudo ufw route allow in on enp0s8 out on enp0s9 proto tcp to 172.16.10.11 port 443   # reenvío LAN -> DMZ
sudo ufw enable                                              # ¡puede cortar tu SSH si no has permitido el puerto 22!
sudo ufw status verbose
```

> [!WARNING]
> `ufw enable` activa el cortafuegos **inmediatamente**. Si administras por SSH, permite antes el puerto 22. Para que UFW reenvíe paquetes hay que activar `net/ipv4/ip_forward=1` en `/etc/ufw/sysctl.conf`, y el NAT se añade editando `/etc/ufw/before.rules`: en un cortafuegos perimetral resulta más claro `nftables`.

### 5.2 Cortafuegos perimetral dedicado: OPNsense y pfSense CE

**OPNsense** y **pfSense CE** son distribuciones de cortafuegos y *router* basadas en **FreeBSD**, con **interfaz web** y funciones integradas: filtrado con estado (**`pf`**), NAT, VPN (WireGuard, IPsec, OpenVPN), IDS/IPS (Suricata), *proxy* (Squid), DNS, DHCP, alta disponibilidad (**CARP + pfsync**), informes y registros.

| | OPNsense | pfSense CE |
|---|---|---|
| Licencia | BSD (código abierto) | Apache 2.0 en la edición CE (Netgate ofrece también ediciones comerciales) |
| Interfaz | Moderna, con API | Clásica, muy extendida |
| Extensiones | Complementos (*plugins*) del proyecto | Paquetes propios |
| Uso | Pymes y centros educativos | Pymes y centros educativos |

Para este módulo son **equivalentes**: aprender uno permite manejar el otro. Se recomienda **OPNsense** por su mantenimiento activo y su documentación (consulta siempre la versión vigente en la web del proyecto).

Principios de las reglas en `pf` (distintos de `nftables`):

- Las reglas se aplican en la **interfaz de entrada** del tráfico (no hay cadenas `input`/`forward` separadas).
- El **orden** importa: en las reglas de interfaz se evalúa de arriba abajo y gana la **primera** coincidencia.
- En una interfaz nueva (la DMZ) **todo está denegado** por defecto. En la WAN se bloquea la entrada; en la LAN, el asistente crea una regla que permite todo: **sustitúyela** por una política de mínimo privilegio.
- Se activa el **registro** en las reglas de bloqueo importantes.

| Tarea | Ruta del menú (OPNsense) |
|---|---|
| Interfaces y direccionamiento | *Interfaces → Assignments* y *Interfaces → [LAN/OPT1]* |
| Alias (grupos de IP o puertos) | *Firewall → Aliases* |
| Reglas por interfaz | *Firewall → Rules → [WAN / LAN / DMZ]* |
| Publicación (DNAT) | *Firewall → NAT → Destination NAT* (*Port Forward* en versiones anteriores y en pfSense) |
| NAT de salida | *Firewall → NAT → Outbound* |
| Registros en vivo | *Firewall → Log Files → Live View* |
| Copia de la configuración | *System → Configuration → Backups* |

Ventajas frente a Linux «a mano»: gestión visual, actualizaciones del sistema, **copia de la configuración con un clic**, alta disponibilidad integrada, informes. Inconvenientes: hay que aprender la plataforma y su modelo de reglas, y la interfaz web de gestión es un **nuevo vector de ataque** que se debe proteger (red de gestión, contraseña fuerte, segundo factor).

### 5.3 Cortafuegos de Windows Defender (Microsoft Defender Firewall)

Los equipos Windows (Windows 11, Windows Server 2025) incluyen un cortafuegos **con estado, basado en el equipo** (*host*), que filtra entrada y salida por **programa, puerto y dirección**. Trabaja con tres **perfiles** que se activan según la red a la que se conecta el equipo:

| Perfil | Cuándo se aplica | Postura recomendada |
|---|---|---|
| **Dominio** | El equipo está en una red con controlador de dominio | Reglas de la organización (directiva de grupo) |
| **Privado** | Red de confianza (casa, oficina) | Más permisivo con lo local |
| **Público** | Redes no confiables (cafeterías, hoteles) | Más restrictivo: bloquear la entrada por defecto |

Por defecto bloquea el tráfico **entrante** no solicitado y permite el saliente. Se administra con la consola *Windows Defender Firewall con seguridad avanzada* (`wf.msc`), con directivas de grupo (en dominio) o con **PowerShell**, que es lo que se puede automatizar y documentar:

```powershell
# Ver el estado y la acción por defecto de cada perfil
Get-NetFirewallProfile | Format-Table Name, Enabled, DefaultInboundAction, DefaultOutboundAction

# Activar los tres perfiles y bloquear la entrada por defecto
Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled True -DefaultInboundAction Block

# Permitir HTTPS entrante solo desde la LAN y solo en el perfil de dominio
New-NetFirewallRule -DisplayName "Permitir HTTPS desde la LAN" -Direction Inbound `
    -Protocol TCP -LocalPort 443 -RemoteAddress 192.168.10.0/24 -Profile Domain -Action Allow

# Registrar los paquetes descartados
Set-NetFirewallProfile -Profile Domain -LogBlocked True -LogMaxSizeKilobytes 4096 `
    -LogFileName "%SystemRoot%\System32\LogFiles\Firewall\pfirewall.log"

# Copia de seguridad y restauración de toda la configuración
netsh advfirewall export "C:\copias\firewall.wfw"
netsh advfirewall import "C:\copias\firewall.wfw"
```

`Get-NetFirewallProfile` consulta los perfiles; `Set-NetFirewallProfile` los modifica; `New-NetFirewallRule` crea una regla (`-Direction` indica entrada o salida y `-Action` permitir o bloquear). El acento grave al final de línea continúa la orden en la siguiente.

> [!WARNING]
> Desactivar el cortafuegos de Windows «para que funcione una aplicación» es un error de manual. Crea una **regla concreta** (puerto, programa, origen) y **registra** lo que se bloquea para diagnosticar. El cortafuegos del equipo **complementa** al perimetral: protege cuando el portátil sale de la oficina.

### 5.4 Comparativa y criterios de elección (RA4.f)

| Criterio | `nftables` en Linux | OPNsense / pfSense | *Appliance* comercial (NGFW) | Windows Defender Firewall |
|---|---|---|---|---|
| Coste | Gratis | Gratis (CE) | Licencias y soporte | Incluido en Windows |
| Gestión | Ficheros y línea de órdenes | Interfaz web | Consola del fabricante | `wf.msc`, GPO, PowerShell |
| Funciones extra | Las que instales | VPN, IDS, *proxy*, HA | Todo integrado, identificación de aplicaciones | Solo filtrado del equipo |
| Mejor para | Automatizar y aprender | Pymes con perímetro dedicado | Grandes redes con soporte 24x7 | Proteger cada equipo Windows |

---

## 6. Registros, diagnóstico y pruebas

### 6.1 Dónde quedan los registros y cómo interpretarlos (RA4.e)

Las reglas con `log` escriben en el **registro del núcleo**, que `journald` recoge. En Debian 13 no hay `rsyslog` por defecto: se consultan con `journalctl`, la orden que lee el diario de systemd (`-k` limita a mensajes del núcleo, `--since` acota el tiempo y `-f` sigue el registro en directo).

```bash
sudo journalctl -k --since "10 min ago" | grep -E 'FW-|DMZ-A-LAN'        # registros del cortafuegos
sudo journalctl -k -f | grep --line-buffered 'DMZ-A-LAN'                 # en tiempo real
```

Un registro típico (una conexión de la DMZ hacia la LAN, que está prohibida):

```text
DMZ-A-LAN: IN=enp0s9 OUT=enp0s8 MAC=... SRC=172.16.10.11 DST=192.168.10.10 LEN=60 ... PROTO=TCP SPT=44512 DPT=445 SYN
```

Para que un registro sirva como evidencia debe recoger siempre: **fecha y hora**, **interfaz de entrada y de salida**, **origen y destino**, **protocolo y puerto**, **regla** (el prefijo) y **acción**. Sin la hora sincronizada (NTP, `chrony`) no se pueden correlacionar eventos entre equipos.

Los **contadores** (`counter`) indican si una regla se **aplica realmente** y el seguimiento de conexiones muestra las traducciones activas:

```bash
sudo nft list chain inet filtro reenvio          # cada regla con su contador de paquetes y bytes
sudo conntrack -L | head                         # conexiones en seguimiento (paquete conntrack-tools)
sudo conntrack -L | grep 172.16.10.11            # las de un servidor concreto, con la traducción NAT
```

Estos registros se envían a un servidor central o SIEM ([UD5](/ud05-seguridad-redes/ud05-teoria/)); como mínimo, los cambios de reglas, los accesos administrativos, los bloqueos repetidos, los intentos DMZ → LAN y las alertas del IDS.

### 6.2 Seguimiento de un paquete (`nftrace`)

Cuando no se sabe **qué regla** afecta a un paquete, se activa la traza solo para el tráfico que interesa y se observa su recorrido por las cadenas:

```bash
sudo nft add table inet traza
sudo nft add chain inet traza pre '{ type filter hook prerouting priority -300; }'
sudo nft add rule inet traza pre ip saddr 192.168.10.50 tcp dport 80 meta nftrace set 1
sudo nft monitor trace            # en otra terminal, haz la petición desde 192.168.10.50
sudo nft delete table inet traza  # limpieza al terminar (la traza consume recursos)
```

### 6.3 Diagnóstico de problemas de conectividad (RA4.g)

Se avanza de lo más simple a lo más profundo, comprobando una capa cada vez:

| Paso | Pregunta | Herramienta |
|---|---|---|
| 1 | ¿Hay conectividad IP básica? | `ping`, `ip -br a`, `ip route get IP` |
| 2 | ¿Se resuelven los nombres? | `dig nombre`, `getent hosts nombre` |
| 3 | ¿El servicio escucha en el destino? | `ss -tlnp` en el servidor (`ss` lista *sockets*; `-t` TCP, `-l` en escucha, `-n` numérico, `-p` proceso) |
| 4 | ¿Llega el paquete al cortafuegos? | `tcpdump -ni enp0s8 host IP and port P` |
| 5 | ¿Sale por la otra interfaz? | `tcpdump -ni enp0s9 ...` |
| 6 | ¿Vuelve la respuesta? | El mismo `tcpdump`; ruta de vuelta y puerta de enlace del servidor |
| 7 | ¿Qué regla lo descarta? | `journalctl -k`, contadores, `nft monitor trace` |
| 8 | ¿Interviene el NAT? | `conntrack -L`: ver las traducciones |

| Síntoma | Causa probable | Solución |
|---|---|---|
| *Timeout* al conectar | `drop` en el cortafuegos o servicio parado | Registros y contadores; `ss -tlnp` |
| `Connection refused` inmediato | El puerto no escucha (o regla `reject`) | Arrancar el servicio |
| Llegan SYN al servidor pero el cliente no recibe respuesta | El servidor no tiene el cortafuegos como puerta de enlace | Corregir la ruta por defecto |
| Funciona por IP pero no por nombre | DNS bloqueado (UDP y TCP 53) | Permitir el DNS |
| Las conexiones largas se caen | Tiempos de `conntrack` o NAT | Ajustar *keepalives* y `nf_conntrack_tcp_timeout_established` |
| Las páginas cargan a medias | Problema de MTU (ICMP «fragmentación necesaria» bloqueado) | Permitir `destination-unreachable` |

### 6.4 Pruebas de funcionamiento y sondeo

Una regla no está validada hasta que se prueba en **los dos sentidos**:

- **Prueba positiva**: lo permitido funciona (`curl` a la web publicada, `ssh` desde el puesto de administración).
- **Prueba negativa**: lo prohibido falla (SSH al cortafuegos desde Internet, cualquier conexión DMZ → LAN).

Para sondear puertos se usan `nc` (*netcat*: `-z` solo comprueba si está abierto, `-v` detalla, `-w 2` espera 2 s) y **Nmap**, que clasifica cada puerto:

| Estado de Nmap | Significado | Causa típica |
|---|---|---|
| `open` | Un servicio responde | Puerto publicado |
| `closed` | El equipo responde que no hay servicio (RST o ICMP) | Sin servicio y sin filtrado, o regla `reject` |
| `filtered` | No hay respuesta | Regla `drop`: el cortafuegos funciona |

```bash
# SOLO contra tus propias máquinas del laboratorio, desde la zona WAN (máquina "atacante")
sudo nmap -sS -p- -T4 10.0.2.10        # -sS: sondeo SYN (el paquete SYN sin completar la conexión); -p-: los 65535 puertos
sudo nmap -sV -p 80,443 10.0.2.10      # -sV: intenta identificar el servicio y su versión
sudo nmap -sU --top-ports 20 10.0.2.10 # -sU: UDP, los 20 puertos más comunes (es lento: UDP no responde si está filtrado)
```

Resultado esperado de un perímetro bien cerrado (solo la web publicada):

```text
Not shown: 65533 filtered tcp ports (no-response)
PORT    STATE SERVICE
80/tcp  open  http
443/tcp open  https
```

> [!WARNING]
> Sondea **solo** equipos propios del laboratorio. Escanear redes ajenas sin autorización puede constituir delito (Código Penal, arts. 197 bis y siguientes). Un sondeo contra la propia infraestructura, con permiso por escrito, es una **verificación** profesional; en el laboratorio, tú das el permiso.

---

## 7. Servidores *proxy*

### 7.1 Tipos y funciones (RA5.a)

Un ***proxy*** es un **intermediario**: recibe las peticiones de un cliente y las reenvía a un servidor (o al revés), pudiendo controlarlas, registrarlas, guardarlas en caché o modificarlas.

| Tipo | Quién lo conoce | Para qué | Ejemplo |
|---|---|---|---|
| ***Proxy* directo** (*forward*) | Los **clientes** (navegador configurado) | Controlar y registrar la **salida** a Internet; caché; filtrado | Squid en la clínica |
| ***Proxy* transparente** (*intercept*) | Nadie: el cortafuegos redirige el tráfico | Lo mismo, sin configurar clientes | Squid con redirección del puerto 80 |
| ***Proxy* inverso** (*reverse*) | Los clientes de Internet creen hablar con el servidor | Proteger y publicar **servidores**: TLS, caché, balanceo, WAF | Nginx delante de la web de citas |
| ***Proxy*-caché** | — | Ahorrar ancho de banda guardando contenido | Squid con `cache_dir` |
| ***Proxy* con autenticación** | — | Exigir usuario antes de navegar | Squid con `basic_ncsa_auth` |
| ***Proxy* SOCKS** | Aplicaciones | Túnel genérico TCP | `ssh -D` (apartado 8.6) |

{{< figura src="ud06/proxy-directo-inverso.svg" alt="Comparativa entre proxy directo y proxy inverso" caption="Figura 6.2. El proxy directo controla a los clientes que salen; el proxy inverso protege a los servidores que se publican." >}}

**Funciones:** control de acceso, filtrado por dominio u horario, autenticación y trazabilidad (quién visitó qué), caché, antimalware (con ICAP), ocultación de la red interna, balanceo y terminación TLS (inverso).

> [!WARNING]
> Un *proxy* ve la navegación de los usuarios: hay implicaciones de **privacidad** (RGPD, LOPDGDD, derechos de los trabajadores). Debe estar **informado** en la política de uso aceptable, registrar solo lo necesario y proteger los registros. La **inspección de HTTPS** (descifrar y volver a cifrar) exige una CA propia instalada en los clientes, justificación legal y proporcionalidad; sin ella, el *proxy* solo ve el nombre del servidor (método `CONNECT`), no el contenido.

### 7.2 *Proxy*-caché con Squid (RA5.b, RA5.e)

**Squid** es el *proxy*-caché libre más veterano y utilizado. Escucha por defecto en el puerto **3128/tcp**. Versión de referencia: **Squid 6.x** (Debian 13, AlmaLinux 10).

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo apt install -y squid apache2-utils          # apache2-utils aporta htpasswd
squid -v | head -1                               # versión instalada
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.bak      # copia de la configuración original
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo dnf install -y squid httpd-tools            # httpd-tools aporta htpasswd
squid -v | head -1
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.bak
```
{{% /tab %}}
{{< /tabs >}}

La lógica de Squid es: se **definen ACL** (`acl`, listas con nombre de orígenes, destinos, horas, métodos...) y se **combinan en reglas** (`http_access allow|deny`). Las reglas se evalúan **en orden** y gana la primera que coincide; por eso las **denegaciones específicas** van primero y `http_access deny all` al final.

Sustituye `/etc/squid/squid.conf` por esta versión mínima y comentada (la que usa `fw01`):

```text
# ---------- Redes, puertos y métodos ----------
acl lan src 192.168.10.0/24                  # clientes autorizados
acl Safe_ports port 80 443                   # solo se navega por estos puertos de destino
acl SSL_ports port 443                       # CONNECT (túnel HTTPS) solo hacia el 443
acl CONNECT method CONNECT

# ---------- Restricciones de acceso web ----------
acl dominios_bloqueados dstdomain "/etc/squid/bloqueados.txt"   # lista de dominios en un fichero
acl horario_laboral time MTWHF 08:00-20:00                      # lunes a viernes de 8 a 20 h
acl redes_sociales dstdomain .facebook.com .instagram.com .tiktok.com
acl ejecutables urlpath_regex -i \.(exe|msi|scr)$               # descargas de ejecutables (solo HTTP)

# ---------- Reglas de acceso (el orden importa) ----------
http_access deny !Safe_ports
http_access deny CONNECT !SSL_ports
http_access deny dominios_bloqueados
http_access deny redes_sociales horario_laboral
http_access deny ejecutables
http_access allow lan
http_access deny all                         # política por defecto

# ---------- Puerto y caché ----------
http_port 3128
cache_dir ufs /var/spool/squid 500 16 256    # 500 MB de caché en disco
cache_mem 128 MB
maximum_object_size 50 MB
refresh_pattern . 0 20% 4320
coredump_dir /var/spool/squid

# ---------- Registro y privacidad ----------
access_log stdio:/var/log/squid/access.log
visible_hostname fw01.mediterraneadental.lab
forwarded_for delete                         # no revela la IP interna del cliente
via off
```

```bash
printf '.malwaredomain.test\n.casino-lab.test\n' | sudo tee /etc/squid/bloqueados.txt   # dominios de prueba; el punto inicial incluye subdominios
sudo squid -k parse                          # comprueba sintaxis y lógica: indica errores y advertencias
sudo squid -z                                # crea la estructura de la caché (solo si es la primera vez o squid se queja)
sudo systemctl enable --now squid            # arranca Squid y lo activa en el arranque
sudo ss -tlnp | grep 3128                    # comprueba que escucha en el 3128
sudo squid -k reconfigure                    # tras cada cambio: recarga la configuración sin cortar clientes
```

> [!NOTE]
> Hay que **abrir el puerto 3128 a la LAN en la cadena `entrada`** de `fw01` (el cliente habla con el *proxy*, que es el propio cortafuegos): `iifname $LAN tcp dport 3128 accept`. Y para que no se eluda el *proxy*, en un entorno real se **retira** la regla que permite a la LAN navegar directamente por 80 y 443 (apartado 7.5).

**Pruebas desde un cliente de la LAN:**

```bash
curl -x http://192.168.10.1:3128 -I http://example.org/              # permitido: 200 OK (con cabeceras X-Cache)
curl -x http://192.168.10.1:3128 -I http://prueba.casino-lab.test/   # denegado: 403 Forbidden (página de error de Squid)
curl -x http://192.168.10.1:3128 -I https://example.org/             # HTTPS por CONNECT: el túnel no se inspecciona
sudo tail -f /var/log/squid/access.log                               # en fw01, en directo
```

Formato del `access.log` de Squid (por defecto):

```text
1760000000.123    214 192.168.10.50 TCP_MISS/200 1256 GET http://example.org/ - HIER_DIRECT/93.184.216.34 text/html
```

| Campo | Significado |
|---|---|
| `1760000000.123` | Hora en formato Unix (`date -d @1760000000` la convierte) |
| `214` | Duración en milisegundos |
| `192.168.10.50` | Cliente |
| `TCP_MISS/200` | Resultado de caché y código HTTP (`HIT`: servido de caché; `MISS`: obtenido de Internet; `DENIED`: bloqueado por una ACL) |
| `GET http://...` | Método y URL |
| `HIER_DIRECT/IP` | Cómo se obtuvo el contenido |

### 7.3 Autenticación en el *proxy* (RA5.c)

Para saber **quién** navega se exige usuario y contraseña mediante un **ayudante** (*helper*), un programa que Squid consulta. Los métodos más habituales:

| Método | Cómo funciona | Cuándo |
|---|---|---|
| **Básica** (`basic_ncsa_auth`) | Fichero `htpasswd`; el navegador envía usuario y contraseña en Base64 (**no cifrados**) | Laboratorio o LAN de confianza |
| **LDAP / Active Directory** (`basic_ldap_auth`) | Valida contra el directorio de la organización | Empresas con directorio |
| **Kerberos / NTLM** (`negotiate_kerberos_auth`) | Inicio de sesión único (SSO), sin contraseña en la red | Dominio de Active Directory |

Configuración con ficheros `htpasswd`:

```bash
sudo htpasswd -c /etc/squid/passwd ana          # -c crea el fichero (solo la primera vez); pide la contraseña
sudo htpasswd /etc/squid/passwd luis
sudo chown root:proxy /etc/squid/passwd && sudo chmod 640 /etc/squid/passwd    # Debian: grupo "proxy"; AlmaLinux: grupo "squid"
```

Añade a `squid.conf` **antes** de las reglas de `http_access`:

```text
auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd     # AlmaLinux: /usr/lib64/squid/basic_ncsa_auth
auth_param basic realm Proxy de Mediterranea Dental
auth_param basic credentialsttl 2 hours
acl autenticados proxy_auth REQUIRED
```

y cambia `http_access allow lan` por `http_access allow lan autenticados`. Comprueba:

```bash
sudo squid -k parse && sudo squid -k reconfigure
curl -sI -x http://192.168.10.1:3128 http://example.org/ | head -1                    # 407 Proxy Authentication Required
curl -sI -x http://ana:ClaveAna1@192.168.10.1:3128 http://example.org/ | head -1      # 200 OK; el log ya muestra el usuario
```

> [!WARNING]
> La autenticación **básica** viaja en Base64 (codificada, no cifrada): cualquiera que capture el tráfico entre el cliente y el *proxy* puede leerla. En producción se integra con LDAP/Kerberos y se protege el segmento del *proxy*. Con el modo transparente (apartado 7.5) **no hay autenticación** por usuario.

### 7.4 Configuración de los clientes: manual, PAC y WPAD

Un *proxy* directo solo sirve si los clientes lo usan. Hay tres formas de configurarlos:

| Método | Cómo | Ventaja | Inconveniente |
|---|---|---|---|
| **Manual** | Ajustes del navegador o del sistema: servidor `192.168.10.1`, puerto `3128`. En Linux, variables `http_proxy` y `https_proxy`; APT: `Acquire::http::Proxy` | Sencillo | Hay que repetirlo en cada equipo |
| **PAC** (*Proxy Auto-Configuration*) | El navegador descarga un fichero JavaScript que **decide por URL** si usar el *proxy* o ir directo | Un solo sitio de gestión; excepciones por destino | Hay que publicar el fichero |
| **WPAD** (*Web Proxy Auto-Discovery*) | El navegador **busca solo** el PAC (DNS `wpad.dominio` o DHCP opción 252) | Sin configuración en los clientes | Riesgo: quien responda a `wpad` controla el tráfico |

Un fichero PAC (`proxy.pac`) mínimo:

```javascript
// Se evalúa en el navegador para cada URL: devuelve DIRECT o el proxy a usar
function FindProxyForURL(url, host) {
    // Nombres cortos, dominio interno y redes internas: sin proxy
    if (isPlainHostName(host) ||
        dnsDomainIs(host, ".mediterraneadental.lab") ||
        isInNet(dnsResolve(host), "192.168.10.0", "255.255.255.0") ||
        isInNet(dnsResolve(host), "172.16.10.0", "255.255.255.0"))
        return "DIRECT";
    // El resto: por Squid; si el proxy no responde, salir directo
    return "PROXY 192.168.10.1:3128; DIRECT";
}
```

Se sirve por HTTP con el tipo MIME `application/x-ns-proxy-autoconfig` y el navegador se configura con «URL de configuración automática del proxy». Para WPAD el fichero se llama `wpad.dat` y se publica en `http://wpad.<dominio>/wpad.dat`.

> [!WARNING]
> **WPAD es un vector de ataque conocido**: si un equipo malicioso responde a la consulta `wpad` (DNS, LLMNR, NetBIOS), puede redirigir todo el tráfico web. Mitigaciones: **desactivar el autodescubrimiento** y fijar la URL del PAC por directiva de grupo o gestión de dispositivos; registrar `wpad` en el DNS interno apuntando a un servidor propio o a un nombre inexistente; y desactivar LLMNR y NetBIOS.

### 7.5 *Proxy* en modo transparente (RA5.d)

En el **modo transparente** (`intercept`) el cortafuegos **redirige** el tráfico web de la LAN al *proxy*: los navegadores no necesitan configuración y no pueden saltárselo. Squid necesita un puerto especial:

```text
http_port 3128
http_port 3129 intercept               # puerto para tráfico interceptado
```

Y el cortafuegos (aquí el propio `fw01`, que tiene Squid instalado) redirige el HTTP de la LAN con `redirect`, que cambia el destino al propio equipo y al puerto indicado:

```text
table ip nat {
  chain prerouting {
    type nat hook prerouting priority dstnat; policy accept;
    iifname "enp0s8" ip saddr 192.168.10.0/24 tcp dport 80 redirect to :3129
  }
}
```

(Se **añade** a la cadena `prerouting` ya existente; no se duplica la tabla.) Además hay que permitir en `entrada` el puerto `3129` desde la LAN.

Limitaciones del modo transparente:

- Intercepta con facilidad solo **HTTP**. El **HTTPS** exigiría inspección TLS (`ssl_bump`), una CA propia en todos los clientes y tiene implicaciones legales y de privacidad. Alternativa: dejar pasar HTTPS y filtrar por **nombre de dominio** (SNI) o por DNS.
- Sin autenticación por usuario: el navegador no sabe que existe un *proxy*.
- Para que no se eluda, se **retira** en el cortafuegos la salida directa de la LAN por 80 (la redirigida llega a Squid por `input`, no por `forward`) y se decide qué hacer con 443.

### 7.6 Monitorización de la actividad y problemas frecuentes (RA5.f, RA5.g)

Con **SARG** (*Squid Analysis Report Generator*) se generan informes HTML a partir de `access.log`: sitios más visitados, usuarios, volumen, bloqueos. Alternativas: **GoAccess** (informes en terminal y HTML), Grafana con Loki o Prometheus, Zabbix, o los informes de OPNsense y pfSense.

```bash
sudo apt install -y sarg                                       # Debian; en AlmaLinux está en EPEL
sudo sarg -l /var/log/squid/access.log -o /var/lib/sarg-reports   # genera los informes HTML
```

> [!WARNING]
> Los informes contienen la navegación de personas identificadas: **datos personales**. Protege el acceso, informa a los usuarios, conserva los registros solo el tiempo necesario y cumple el RGPD (minimización, limitación de la finalidad).

| Síntoma | Causa | Solución |
|---|---|---|
| `403 Forbidden` (página de Squid) | Regla `http_access` o ACL | Revisar el orden; `access.log` muestra `TCP_DENIED` |
| `407` en bucle | Credenciales erróneas o *helper* mal configurado | Probar el *helper* a mano: `echo "ana ClaveAna1" \| /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd` debe responder `OK` |
| `Connection refused` al *proxy* | Squid parado o puerto cerrado en el cortafuegos | `systemctl status squid`, `ss -tlnp`, regla de `entrada` |
| Webs HTTPS lentas o que fallan | DNS o `CONNECT` bloqueado | `SSL_ports`, DNS del *proxy* |
| `Host header forgery` en el modo transparente | El cliente y Squid resuelven distinto el nombre | Usar el mismo DNS en los clientes y en Squid |
| Squid no arranca | Error de configuración o permisos de la caché | `squid -k parse`; `journalctl -u squid`; `squid -z` |
| Los servidores no actualizan paquetes | No tienen salida por el *proxy* | `Acquire::http::Proxy` en APT; `proxy=` en `dnf.conf` |

### 7.7 *Proxy* inverso con Nginx (RA5.h)

Un **proxy inverso** se sitúa **delante de los servidores web**: los clientes de Internet hablan con él y él, internamente, con los servidores reales. Aporta:

- **Un único punto de entrada**: los servidores internos no se exponen.
- **Terminación TLS**: gestiona los certificados ([UD3](/ud03-criptografia/ud03-teoria/)) en un solo sitio; los *backends* pueden hablar HTTP interno.
- **Publicación de varias aplicaciones** bajo un mismo dominio y puerto (por ruta o por nombre).
- **Balanceo** entre servidores y comprobaciones de salud ([UD7](/ud07-alta-disponibilidad/ud07-teoria/)).
- **Protección**: limitación de peticiones, cabeceras de seguridad, filtrado (WAF), ocultación de versiones.
- **Caché** de contenido estático.

En el laboratorio, el *proxy* inverso es **`web02`** (`172.16.10.12`, actúa de `rp01`) y el servidor real es **`web01`** (`172.16.10.11`). El cortafuegos publica el *proxy*, no el servidor real. En producción, el *proxy* inverso es un equipo propio de la DMZ (o HAProxy en la [UD7](/ud07-alta-disponibilidad/ud07-teoria/)).

```bash
sudo apt install -y nginx                      # AlmaLinux: sudo dnf install -y nginx
nginx -v                                       # Nginx 1.26 en Debian 13
```

Certificado de laboratorio (en la unidad de proyecto se usa el de la PKI de la [UD3](/ud03-criptografia/ud03-teoria/)): `openssl req -x509` crea un certificado autofirmado; `-newkey ec -pkeyopt ec_paramgen_curve:prime256v1` genera una clave de curva elíptica P-256; `-nodes` la deja sin contraseña (para que Nginx arranque solo; protégela con permisos `600`); `-addext` añade el nombre alternativo (SAN) que exigen los navegadores.

```bash
sudo mkdir -p /etc/ssl/lab && cd /etc/ssl/lab
sudo openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -days 90 \
    -keyout citas.key -out citas.crt -subj "/CN=citas.mediterraneadental.lab" \
    -addext "subjectAltName=DNS:citas.mediterraneadental.lab"
sudo chmod 600 citas.key
```

Configuración en `/etc/nginx/conf.d/citas.conf`:

```nginx
# Límites de peticiones (contexto http): 10 por segundo y por IP; 20 conexiones simultáneas por IP
limit_req_zone  $binary_remote_addr zone=por_ip:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=conex_ip:10m;

upstream citas_backend {
    server 172.16.10.11:80 max_fails=3 fail_timeout=10s;     # web01 (el servidor real)
}

server {                                          # HTTP: solo redirige a HTTPS
    listen 80 default_server;
    server_name citas.mediterraneadental.lab;
    server_tokens off;                            # oculta la versión de Nginx
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name citas.mediterraneadental.lab;
    server_tokens off;

    ssl_certificate     /etc/ssl/lab/citas.crt;
    ssl_certificate_key /etc/ssl/lab/citas.key;
    ssl_protocols       TLSv1.2 TLSv1.3;          # sin TLS 1.0 ni 1.1
    ssl_prefer_server_ciphers off;

    # Cabeceras de seguridad (HSTS corto en el laboratorio; en producción, max-age=31536000)
    add_header Strict-Transport-Security "max-age=300" always;
    add_header X-Content-Type-Options    "nosniff" always;
    add_header X-Frame-Options           "DENY" always;
    add_header Referrer-Policy           "no-referrer" always;

    location / {
        limit_req  zone=por_ip burst=20 nodelay;  # absorbe ráfagas de 20 y rechaza el exceso con 503
        limit_conn conex_ip 20;
        proxy_pass http://citas_backend;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo rm -f /etc/nginx/sites-enabled/default      # Debian: quita el sitio por defecto, que ocupa el puerto 80
sudo nginx -t                                    # comprueba la sintaxis: «syntax is ok / test is successful»
sudo systemctl enable --now nginx && sudo systemctl reload nginx
curl -skI --resolve citas.mediterraneadental.lab:443:127.0.0.1 https://citas.mediterraneadental.lab/ | head -3    # respuesta HTTPS del proxy
curl -skI --resolve citas.mediterraneadental.lab:443:127.0.0.1 https://citas.mediterraneadental.lab/ | grep -iE 'strict-transport|x-content|x-frame|server'   # cabeceras de seguridad
```

**Aislar el *backend*.** Que el *proxy* inverso exista no basta: `web01` debe **aceptar el puerto 80 solo desde `web02`**, de modo que nadie salte el *proxy* y llegue directamente al servidor real. Dentro de la misma red (la DMZ) el cortafuegos perimetral no ve ese tráfico, así que se hace con el filtrado local de `web01` (mismo método `nftables`, tabla propia). En AlmaLinux, si SELinux impide que Nginx se conecte al *backend* (error `502`), se habilita con `sudo setsebool -P httpd_can_network_connect on`.

### 7.8 WAF: cortafuegos de aplicación web

Un **WAF** inspecciona las **peticiones HTTP/HTTPS** y bloquea patrones de ataque: inyección SQL, XSS, recorrido de rutas (*path traversal*)... Se coloca **delante** de la aplicación, normalmente integrado en el *proxy* inverso.

| Elemento | Descripción |
|---|---|
| **ModSecurity** | Motor WAF libre (mantenido hoy por OWASP); la versión 3 es una biblioteca con conector para Nginx |
| **OWASP CRS** (*Core Rule Set*) | Conjunto de reglas genéricas mantenido por OWASP |
| **Coraza** | Motor WAF moderno escrito en Go, compatible con CRS |
| **Modos** | `DetectionOnly` (registra, no bloquea) y `On` (bloquea) |

**Flujo recomendado:** instalar en **modo detección** → revisar el registro durante días (falsos positivos) → ajustar exclusiones → pasar a **bloqueo**. En Debian el conector está en el paquete `libnginx-mod-http-modsecurity` y las reglas en `modsecurity-crs` (comprueba que existen en tu versión con `apt search modsecurity`; las rutas de configuración dependen del paquete: consulta su documentación).

```nginx
modsecurity on;
modsecurity_rules_file /etc/nginx/modsec/main.conf;    # incluye SecRuleEngine DetectionOnly y las reglas CRS
```

Prueba defensiva **solo contra tu propio servidor**, con cadenas inofensivas que las reglas reconocen como patrones de ataque:

```bash
curl -sk -o /dev/null -w '%{http_code}\n' "https://localhost/?q=<script>alert(1)</script>"       # XSS de prueba
curl -sk -o /dev/null -w '%{http_code}\n' "https://localhost/?file=../../etc/passwd"            # recorrido de rutas de prueba
```

En modo detección ambas devuelven `200` y quedan en el registro de auditoría; con `SecRuleEngine On` devolverían `403`. Un WAF **complementa**, no sustituye, al código seguro y a las actualizaciones de la aplicación.

---

## 8. Redes privadas virtuales (VPN)

### 8.1 Qué es una VPN y para qué sirve

Una **VPN** (*Virtual Private Network*) crea un **túnel cifrado** sobre una red no confiable (Internet) y hace que los equipos parezcan estar en la misma red privada. Aporta **confidencialidad** (nadie lee el tráfico), **integridad** (nadie lo modifica) y **autenticación** (se sabe quién está al otro lado).

**Beneficios frente a una línea dedicada:** coste mucho menor (se aprovecha Internet), despliegue rápido, flexibilidad (cualquier ubicación) y escalabilidad. **Inconvenientes:** depende de la calidad y la disponibilidad de Internet (sin garantías de ancho de banda ni de latencia), añade carga de cifrado, y su seguridad depende de **la configuración y de la gestión de credenciales**: una VPN mal configurada es una puerta abierta.

| Tipo | Escenario | Ejemplo |
|---|---|---|
| **Acceso remoto** (*road warrior*) | Una persona se conecta desde casa a la red de la empresa | Portátil de la doctora → `fw01` |
| **Sitio a sitio** (*site-to-site*) | Dos redes se unen de forma permanente | Delegación ↔ sede |

Según el **nivel** al que operan, las VPN se clasifican (RA3.d):

| Nivel | Tecnologías | Característica |
|---|---|---|
| **Red** (capa 3) | **WireGuard**, **IPsec/IKEv2** | Transportan paquetes IP; transparentes para las aplicaciones |
| **Transporte / sesión** (TLS) | **OpenVPN** | Usa TLS ([UD3](/ud03-criptografia/ud03-teoria/)); atraviesa casi cualquier cortafuegos |
| **Aplicación** | **Túneles SSH** (`-L`, `-R`, `-D`) | Protegen un único servicio o puerto |

### 8.2 Comparativa de tecnologías

| | **WireGuard** | **IPsec / IKEv2** | **OpenVPN** |
|---|---|---|---|
| Implementación | En el núcleo de Linux | Estándar IETF; núcleo + demonio IKE | Espacio de usuario |
| Complejidad | **Muy baja** (pocas líneas) | Alta (muchos parámetros) | Media |
| Autenticación | Claves públicas | PSK, certificados, EAP/RADIUS | Certificados, usuario y contraseña, RADIUS |
| Rendimiento | Excelente | Muy bueno (aceleración por hardware) | Bueno |
| Interoperabilidad | Buena y creciente | **La mayor** (cortafuegos, móviles) | Muy buena |
| Uso típico | Acceso remoto; sitio a sitio entre Linux | Sitio a sitio entre fabricantes distintos | Acceso remoto con clientes heterogéneos |

> [!NOTE]
> **Tecnologías obsoletas que no debes usar:** PPTP y L2TP sin IPsec, IKEv1 con «modo agresivo», claves precompartidas débiles, y cifrados 3DES, RC4 o SHA-1. Usa los modos modernos (AES-GCM, ChaCha20-Poly1305, curvas elípticas).

### 8.3 WireGuard: VPN de acceso remoto paso a paso (RA3.d, RA3.e)

**WireGuard** está integrado en el núcleo de Linux. Cada extremo (*peer*) tiene un **par de claves** (privada y pública) y declara qué direcciones aceptará de los demás (`AllowedIPs`). No hay negociación compleja: es fácil de configurar y de auditar.

{{< figura src="ud06/wireguard-tunel.svg" alt="Esquema de VPN WireGuard de acceso remoto" caption="Figura 6.3. WireGuard enruta por el túnel solo las redes indicadas en AllowedIPs y autentica a los pares con claves públicas." >}}

Escenario: el teletrabajador `cli-remoto` (10.0.2.60) accede por el túnel `10.99.0.0/24` a `srv-gestion` (192.168.10.10) a través de la pasarela `fw01` (WAN 10.0.2.10).

**1. Instalación** (Debian 13; en AlmaLinux 10, `sudo dnf install -y wireguard-tools`):

```bash
sudo apt install -y wireguard wireguard-tools
```

**2. Claves** (en cada extremo; la clave **privada no sale nunca** de su máquina). `umask 077` hace que los ficheros nuevos solo los pueda leer su propietario; `wg genkey` genera la clave privada y `wg pubkey` calcula la pública a partir de ella:

```bash
umask 077
wg genkey | sudo tee /etc/wireguard/privada.key | wg pubkey | sudo tee /etc/wireguard/publica.key
sudo cat /etc/wireguard/publica.key        # esta SÍ se comparte con el otro extremo
```

**3. Configuración de la pasarela `fw01`** (`/etc/wireguard/wg0.conf`, permisos `600`):

```ini
[Interface]
Address    = 10.99.0.1/24                  # IP del túnel de la pasarela
ListenPort = 51820
PrivateKey = <CLAVE_PRIVADA_DE_FW01>

[Peer]                                     # portátil de la doctora (cli-remoto)
PublicKey  = <CLAVE_PUBLICA_DEL_CLIENTE>
AllowedIPs = 10.99.0.2/32                  # solo puede usar esta IP dentro del túnel
```

**4. Configuración del cliente** (`/etc/wireguard/wg0.conf`):

```ini
[Interface]
Address    = 10.99.0.2/24
PrivateKey = <CLAVE_PRIVADA_DEL_CLIENTE>

[Peer]                                     # la pasarela
PublicKey  = <CLAVE_PUBLICA_DE_FW01>
Endpoint   = 10.0.2.10:51820               # dirección pública de la pasarela
AllowedIPs = 10.99.0.0/24, 192.168.10.0/24 # tráfico que se envía por el túnel (split tunneling)
PersistentKeepalive = 25                   # mantiene abierto el NAT del cliente
```

> [!IMPORTANT]
> `AllowedIPs` hace **dos cosas**: **enruta** hacia el túnel el tráfico de esas redes y **filtra** qué direcciones de origen se aceptan de ese par. Con `0.0.0.0/0` todo el tráfico del cliente pasa por la VPN (*full tunnel*, obliga a configurar NAT y DNS en la pasarela); con redes concretas solo ese tráfico va por el túnel (*split tunneling*).

**5. El cortafuegos de `fw01`** debe abrir el puerto UDP de WireGuard y permitir por la VPN **solo** lo necesario. **Se añaden a las cadenas existentes de `/etc/nftables.conf`** (no en una tabla aparte: dos cadenas `forward` con política `drop` deben aceptar *ambas* el paquete):

```text
# En la cadena "entrada", antes de las reglas finales de registro:
    iifname $WAN udp dport 51820 accept                          # WireGuard

# En la cadena "reenvio", antes del registro final:
    iifname "wg0" oifname $LAN ip daddr 192.168.10.10 tcp dport { 22, 80, 443 } counter accept   # la VPN solo llega a srv-gestion
```

Se aplican con el procedimiento del apartado 4.4. `srv-gestion` devuelve el tráfico a `10.99.0.2` por `fw01` porque es su puerta de enlace.

**6. Arrancar y comprobar:**

```bash
sudo chmod 600 /etc/wireguard/wg0.conf
sudo systemctl enable --now wg-quick@wg0     # wg-quick crea la interfaz wg0 y las rutas; la unidad lo hace en cada arranque
sudo wg show                                 # "latest handshake" reciente y bytes transferidos
ping -c 3 10.99.0.1                          # desde el cliente: la pasarela por el túnel
curl -s http://192.168.10.10/                # un servidor de la LAN interna (permitido)
```

Con `tcpdump` en la WAN solo se ve tráfico UDP/51820 **ilegible** (el cifrado funciona); dentro de `wg0` sí se ve el tráfico en claro:

```bash
sudo tcpdump -ni enp0s3 udp port 51820 -c 5    # fuera del túnel: solo UDP cifrado
sudo tcpdump -ni wg0 -c 5 icmp                 # dentro del túnel: el ping se ve en claro
```

**Revocar un cliente** (un portátil robado): se elimina su bloque `[Peer]` y se recarga la configuración sin cortar a los demás: `sudo wg syncconf wg0 <(sudo wg-quick strip wg0)`.

> [!IMPORTANT]
> Las claves **privadas** no se comparten, no se pegan en chats ni se suben a Git; solo se intercambian las **públicas**. Si una privada se expone, se genera una nueva y se sustituye la pública en el otro extremo. WireGuard solo autentica **equipos** (claves): para autenticar a la **persona** se añade un segundo factor en otra capa (apartado 9.3).

### 8.4 IPsec/IKEv2 con strongSwan (sitio a sitio)

**IPsec** es el estándar para unir redes entre fabricantes distintos. Funciona en dos fases: **IKEv2** (RFC 7296) autentica a los extremos y negocia las claves (UDP 500 y 4500) y **ESP** (RFC 4303) cifra el tráfico. Por cada túnel se crea una **SA** (*Security Association*) que indica qué redes protege (*selectores de tráfico*).

Ejemplo con **strongSwan 6.x** y su interfaz moderna `swanctl` (el antiguo `ipsec.conf` está en desuso): unión de la sede (`192.168.10.0/24`, `fw01` en 10.0.2.10) y la delegación (`192.168.20.0/24`, `fw-deleg` en 10.0.2.20). La clave precompartida (PSK) es **solo para laboratorio**: en producción se usan **certificados** de la PKI de la [UD3](/ud03-criptografia/ud03-teoria/).

```bash
sudo apt install -y strongswan-swanctl charon-systemd   # AlmaLinux: sudo dnf install -y strongswan (EPEL)
```

`/etc/swanctl/conf.d/sede-delegacion.conf` en la **sede** (en la delegación, el mismo fichero invirtiendo `local_*`, `remote_*`, `id` y `*_ts`):

```text
connections {
  sede-delegacion {
    version = 2                                  # IKEv2
    local_addrs  = 10.0.2.10
    remote_addrs = 10.0.2.20
    proposals = aes256gcm16-prfsha384-ecp384     # cifrado moderno: AES-GCM + curva P-384
    local  { auth = psk; id = sede }
    remote { auth = psk; id = delegacion }
    children {
      lan {
        local_ts  = 192.168.10.0/24
        remote_ts = 192.168.20.0/24
        esp_proposals = aes256gcm16-ecp384
        start_action = start                     # levanta el túnel al arrancar
      }
    }
  }
}
secrets {
  ike-sede-delegacion {
    id-1 = sede
    id-2 = delegacion
    secret = "CambiaEstaPSKDeLaboratorio-UnaFraseLargaYAleatoria"
  }
}
```

```bash
sudo chmod 600 /etc/swanctl/conf.d/sede-delegacion.conf     # contiene la PSK
sudo systemctl enable --now strongswan       # el servicio se llama strongswan (con charon-systemd)
sudo swanctl --load-all                      # carga configuración y secretos
sudo swanctl --list-sas                      # IKE_SA y CHILD_SA establecidas
ping -c 3 192.168.20.10                      # desde un equipo de la sede, a uno de la delegación
sudo ip xfrm state | head                    # asociaciones de seguridad en el núcleo
```

Notas de cortafuegos: hay que permitir en `entrada` el **UDP 500 y 4500** y el protocolo **ESP** (`iifname $WAN udp dport { 500, 4500 } accept` y `iifname $WAN ip protocol esp accept`), y **excluir del NAT** el tráfico hacia la otra red (`oifname $WAN ip daddr 192.168.20.0/24 accept` antes de `masquerade`), porque si se enmascara, los selectores dejan de coincidir. Para acceso remoto con usuarios, strongSwan admite `auth = eap-radius` y delega la autenticación en FreeRADIUS (apartado 9.5).

### 8.5 VPN sobre TLS: OpenVPN

**OpenVPN** utiliza TLS ([UD3](/ud03-criptografia/ud03-teoria/)) para autenticar con **certificados**, se ejecuta en espacio de usuario y atraviesa casi cualquier cortafuegos (UDP o TCP/443). Requiere una **PKI** (por ejemplo, con `easy-rsa`) y un servidor con su fichero de configuración. Su ventaja es la flexibilidad (usuario, contraseña y certificado a la vez; integración con RADIUS y LDAP); su inconveniente, más complejidad y menor rendimiento que WireGuard. Para instalarlo, consulta la documentación oficial de OpenVPN y usa siempre `tls-crypt` y cifrados AEAD.

### 8.6 VPN a nivel de aplicación: túneles SSH

SSH puede transportar **otros protocolos** dentro de su canal cifrado:

```mermaid
flowchart LR
  subgraph Cliente
    A["Navegador<br/>localhost:8080"]
  end
  subgraph "Servidor SSH (pasarela)"
    B[sshd]
  end
  subgraph "Red interna"
    C["srv-gestion<br/>192.168.10.10:80"]
  end
  A == "túnel cifrado SSH" ==> B --> C
```

| Opción | Tipo | Ejemplo | Para qué |
|---|---|---|---|
| `-L` | Reenvío **local** | `ssh -L 8080:192.168.10.10:80 ana@10.0.2.10` | Acceder desde tu equipo a un servicio interno |
| `-R` | Reenvío **remoto** | `ssh -R 9000:localhost:3000 ana@10.0.2.10` | Exponer un servicio local en el servidor |
| `-D` | *Proxy* **dinámico** SOCKS | `ssh -D 1080 ana@10.0.2.10` | Navegar a través del servidor |

```bash
ssh -N -L 8080:192.168.10.10:80 ana@10.0.2.10 &    # -N: no abre shell, solo el túnel; & lo deja en segundo plano
curl -s http://localhost:8080/                      # llega a la intranet por el túnel
kill %1                                             # cierra el túnel
```

> [!WARNING]
> Los túneles **pueden saltarse el cortafuegos**: un empleado podría exponer un servicio interno a Internet con `-R`. Por eso en los servidores se deja `AllowTcpForwarding no` ([UD4](/ud04-fortificacion-hosts/ud04-teoria/)) y se habilita solo para quien lo necesita (apartado 9.2).

---

## 9. Acceso remoto seguro y AAA

### 9.1 El servidor como pasarela de acceso a la red interna (RA3.e)

Una **pasarela de acceso remoto** es el servidor (o conjunto de servicios) que **termina** las conexiones externas y decide a qué recursos internos puede llegar cada persona. Debe cumplir tres funciones, las tres de **AAA**:

| Función | Pregunta | En nuestra pasarela |
|---|---|---|
| **Autenticación** | ¿Quién eres? | Clave de WireGuard (equipo) + clave SSH o RADIUS (persona) + segundo factor |
| **Autorización** | ¿Qué puedes hacer? | `AllowedIPs`, reglas `forward` por origen y destino, `PermitOpen` en SSH |
| **Auditoría** (*accounting*) | ¿Qué has hecho? | Registros de `wg`, de `sshd`, del cortafuegos y de RADIUS (1813/udp) |

```mermaid
flowchart LR
  T["Teletrabajo<br/>10.0.2.60"] -- "WireGuard 51820/udp" --> G["fw01<br/>pasarela"]
  T -- "SSH 22/tcp con clave + RADIUS" --> G
  G -- "forward filtrado" --> S["srv-gestion<br/>192.168.10.10"]
  G -. "RADIUS 1812/udp" .-> R["srv-ficheros<br/>FreeRADIUS"]
```

### 9.2 Servidores de salto (*bastion host*) y SSH avanzado

Un **servidor de salto** o **bastión** es el **único** servidor SSH accesible desde fuera; para llegar a los servidores internos hay que pasar por él. Reduce la exposición y **centraliza los registros**. Se usa con `ProxyJump` (`-J`), que abre una conexión SSH al bastión y, a través de ella, otra al destino; **la clave privada nunca viaja al bastión**.

```bash
ssh -J ana@10.0.2.10 ana@192.168.10.10          # salta por el bastión hasta el servidor interno
```

Configuración permanente en `~/.ssh/config` del cliente:

```text
Host bastion
    HostName 10.0.2.10
    User ana
    IdentityFile ~/.ssh/id_ed25519

Host srv-gestion
    HostName 192.168.10.10
    User ana
    ProxyJump bastion
```

```bash
ssh srv-gestion         # conecta con el servidor interno pasando por el bastión
```

**En el bastión** se limita lo que los usuarios de salto pueden hacer (`/etc/ssh/sshd_config.d/30-bastion.conf`; compruébalo con `sudo sshd -t` y recarga con `sudo systemctl reload ssh`):

```text
Match Group saltadores
    AllowTcpForwarding yes                         # necesario para ProxyJump
    PermitOpen 192.168.10.10:22 192.168.10.11:22   # solo puede saltar a estos destinos
    PermitTTY no                                   # sin intérprete de órdenes en el bastión
    X11Forwarding no
    AllowAgentForwarding no
```

**Certificados SSH.** Con claves públicas, cada servidor debe tener las `authorized_keys` de cada usuario: no escala. Los **certificados SSH** usan una **autoridad certificadora (CA) de SSH**, mucho más sencilla que la PKI de la UD3: la CA **firma** las claves de los usuarios (y de los servidores) con una validez limitada.

```bash
# En la máquina de la CA (protegida)
ssh-keygen -t ed25519 -f ssh_ca -C "CA SSH laboratorio"                  # clave de la CA
ssh-keygen -s ssh_ca -I ana-2026 -n ana,admin -V +12w ana.pub            # firma: identidad (-I), cuentas permitidas (-n), caducidad (-V)
ssh-keygen -L -f ana-cert.pub                                            # inspecciona el certificado
```

En el **servidor** basta una línea para confiar en la CA, sin `authorized_keys` por usuario:

```bash
sudo cp ssh_ca.pub /etc/ssh/ssh_ca.pub
echo 'TrustedUserCAKeys /etc/ssh/ssh_ca.pub' | sudo tee /etc/ssh/sshd_config.d/20-ca.conf
sudo sshd -t && sudo systemctl reload ssh
```

Ventajas: caducan solos (`-V +12w`), llevan una identidad (`-I`) útil en la auditoría y se pueden restringir (`-n`, `-O force-command=...`). Para **revocar** antes de que caduquen, se usa un fichero `RevokedKeys` en `sshd_config`.

### 9.3 Protocolos de autenticación y métodos para el acceso remoto (RA3.f)

| Protocolo | Qué es | Seguridad | Dónde se usa |
|---|---|---|---|
| **PAP** (*Password Authentication Protocol*) | Envía usuario y contraseña **en claro** | Baja: solo aceptable dentro de un túnel cifrado | Acceso a la red, PPP; el más sencillo de RADIUS |
| **CHAP** (RFC 1994) | Desafío-respuesta con *hash*: la contraseña no viaja | Media: exige que el servidor conozca la contraseña en claro | PPP, RADIUS |
| **EAP** (RFC 3748) | **Marco** extensible con distintos métodos | Depende del método: **EAP-TLS** (certificados de cliente y servidor, RFC 5216) es el más seguro; PEAP y EAP-TTLS (usuario y contraseña dentro de un túnel TLS) | Wi-Fi WPA2/WPA3-Enterprise, 802.1X, IPsec |
| **Kerberos** (RFC 4120) | **Tickets** emitidos por un centro de distribución de claves; inicio de sesión único | Alta: la contraseña no viaja y los tickets caducan | Active Directory, SSH y Squid con SSO |

Para el **acceso remoto** de personas se combinan métodos:

| Método | Cómo | Nivel |
|---|---|---|
| Clave precompartida | Un secreto común a todos | Bajo (solo laboratorio) |
| Clave pública (WireGuard, SSH) | Un par de claves por equipo o persona | Alto |
| Certificado de cliente | Emitido por la PKI ([UD3](/ud03-criptografia/ud03-teoria/)) | Alto |
| Usuario y contraseña (EAP o RADIUS) | Contra un servidor RADIUS o LDAP | Medio |
| Clave + contraseña | Dos elementos | Alto |
| **MFA** (TOTP, FIDO2) | Segundo factor independiente | **Recomendado** |

### 9.4 AAA y RADIUS: servidores de autenticación remota (RA3.g)

**RADIUS** (*Remote Authentication Dial-In User Service*, RFC 2865) es el protocolo estándar para centralizar AAA: la pasarela VPN, el punto de acceso Wi-Fi o el *switch* (**NAS**, *Network Access Server*) preguntan al servidor RADIUS si la persona puede entrar. Usa **UDP 1812** (autenticación) y **1813** (*accounting*) y protege con un **secreto compartido** entre el NAS y el servidor.

```mermaid
sequenceDiagram
  participant U as Usuario
  participant N as NAS (fw01 / AP / switch)
  participant R as Servidor RADIUS
  participant D as Base de usuarios (ficheros, LDAP, AD)
  U->>N: Credenciales
  N->>R: Access-Request (UDP 1812)
  R->>D: Verifica el usuario
  D-->>R: OK
  R-->>N: Access-Accept (+ atributos: VLAN, tiempo máximo)
  N-->>U: Acceso concedido
```

**FreeRADIUS** (3.2.x) es el servidor RADIUS libre más utilizado. Se instala en `srv-ficheros` (192.168.10.11) y `fw01` es su cliente (NAS):

```bash
sudo apt install -y freeradius freeradius-utils     # AlmaLinux: sudo dnf install -y freeradius freeradius-utils
sudo systemctl stop freeradius                      # se para para probarlo en modo depuración
```

Los ficheros están en `/etc/freeradius/3.0/` (AlmaLinux: `/etc/raddb/`):

| Fichero | Función |
|---|---|
| `clients.conf` | Qué NAS pueden consultar al servidor y su **secreto compartido** |
| `mods-config/files/authorize` | Usuarios de prueba (modo ficheros) |
| `radiusd.conf`, `sites-enabled/` | Configuración general y «sitios» virtuales |
| `mods-enabled/` | Módulos activos (`eap`, `ldap`, `pap`...) |

Declara la pasarela como cliente (**copia antes** los ficheros que vas a tocar):

```bash
sudo cp /etc/freeradius/3.0/clients.conf /etc/freeradius/3.0/clients.conf.bak
sudo cp /etc/freeradius/3.0/mods-config/files/authorize /etc/freeradius/3.0/mods-config/files/authorize.bak
sudo tee -a /etc/freeradius/3.0/clients.conf >/dev/null <<'EOF'

client fw01 {
    ipaddr = 192.168.10.1
    secret = SecretoRadiusLab-CambiaMe-2026
}
EOF
```

Crea un usuario de prueba al principio de `mods-config/files/authorize` (contraseña en claro: **solo laboratorio**):

```text
ana  Cleartext-Password := "ClavePruebaAna1"
     Reply-Message := "Hola Ana"
```

Arranca en **modo depuración** (muestra cada paso: ideal para aprender y diagnosticar) y prueba desde otra terminal. `radtest` envía una petición como lo haría un NAS: usuario, contraseña, servidor, número de puerto del NAS y secreto del cliente:

```bash
sudo freeradius -X                                                  # depuración en primer plano; Ctrl+C para salir
radtest ana ClavePruebaAna1 localhost 0 testing123                  # desde el propio servidor (cliente «localhost»)
radtest ana ClavePruebaAna1 192.168.10.11 0 SecretoRadiusLab-CambiaMe-2026    # desde fw01
```

La salida debe incluir `Received Access-Accept`; con una clave errónea, `Access-Reject`; si el **secreto** no coincide, el servidor **descarta en silencio** la petición (aparece en el registro de depuración). Cuando funcione: `sudo systemctl enable --now freeradius`.

> [!WARNING]
> Las contraseñas en claro del fichero `authorize` son **solo para laboratorio**. En producción RADIUS se integra con **LDAP o Active Directory** (módulo `ldap`; para AD con contraseñas NT, `ntlm_auth`/Winbind) o usa *hashes*, y mejor aún EAP-TLS con certificados. Protege `clients.conf` (permisos `640`, propietario `root:freerad`), usa secretos largos y **distintos por cliente**, y no expongas RADIUS fuera de la red de gestión: el protocolo cifra solo la contraseña con el secreto. Entre redes distintas se usa **RadSec** (RADIUS sobre TLS, RFC 6614).

### 9.5 Integración de RADIUS con la pasarela

| Servicio | Cómo se integra |
|---|---|
| **SSH (PAM)** | El módulo `pam_radius_auth` hace que `sshd` valide la contraseña contra RADIUS; con `AuthenticationMethods publickey,keyboard-interactive` se exige **clave pública + contraseña RADIUS** (dos factores) |
| **strongSwan** (IPsec) | El método `auth = eap-radius` envía la autenticación EAP del usuario a FreeRADIUS |
| **OpenVPN** | Complemento de RADIUS o PAM |
| **Wi-Fi WPA2/WPA3-Enterprise** | El punto de acceso (`hostapd`) apunta a RADIUS (`auth_server_addr`, `auth_server_port=1812`, `auth_server_shared_secret`); con **EAP-TLS** se autentican los equipos con certificado |
| **Switches (802.1X)** | El *switch* es el NAS y RADIUS puede devolver la **VLAN** del usuario |
| **Directorio** (LDAP/AD) | FreeRADIUS consulta el directorio: un solo usuario para todos los servicios |

Ejemplo de la pasarela SSH de `fw01` con RADIUS (Debian 13; **mantén una sesión de `root` abierta** mientras pruebas y haz copia antes de tocar PAM):

```bash
sudo apt install -y libpam-radius-auth
sudo cp /etc/pam.d/sshd /etc/pam.d/sshd.bak
echo '192.168.10.11:1812 SecretoRadiusLab-CambiaMe-2026 3' | sudo tee /etc/pam_radius_auth.conf   # servidor:puerto  secreto  tiempo de espera
sudo chmod 600 /etc/pam_radius_auth.conf
```

En `/etc/pam.d/sshd`, **comenta** la línea `@include common-auth` y añade `auth required pam_radius_auth.so`. En `/etc/ssh/sshd_config.d/40-radius.conf`:

```text
UsePAM yes
KbdInteractiveAuthentication yes
AuthenticationMethods publickey,keyboard-interactive:pam
```

```bash
sudo sshd -t && sudo systemctl reload ssh      # comprueba y recarga SIN cerrar la sesión actual
```

La persona debe tener además una **cuenta local** (`ana`): PAM autentica, pero no crea cuentas.

### 9.6 Configuración de los parámetros de acceso

| Parámetro | Dónde | Efecto |
|---|---|---|
| `MaxAuthTries`, `LoginGraceTime` | `sshd_config` | Limitan intentos y tiempo para autenticarse |
| `AllowUsers` / `AllowGroups` | `sshd_config` | Solo entran las cuentas autorizadas |
| `PermitOpen`, `AllowTcpForwarding` | `sshd_config` | Qué destinos puede alcanzar un túnel |
| `AllowedIPs`, reglas `forward` | WireGuard y `nftables` | A qué redes y puertos llega cada par |
| `Session-Timeout`, VLAN | Atributos de RADIUS | Duración de la sesión y segmento asignado |
| Caducidad de certificados (`-V`) | CA SSH y PKI | Vigencia limitada de los accesos |
| Revocación | Eliminar el `[Peer]`, `RevokedKeys`, CRL | Retirada inmediata de un acceso |
| Registros y *accounting* | `journald`, RADIUS 1813 | Trazabilidad de quién entró y cuándo |

---

