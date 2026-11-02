---
title: "UD02 · Casos de ataque y defensa"
weight: 3
bookToc: true
---

# UD02 · Casos de ataque y defensa

{{< ra "RA1:a,b" "RA2:c,d" "RA6:b,f" >}}

La seguridad pasiva entra en juego **cuando el ataque ya ha tenido éxito** (o cuando falla algo físico). Los grupos de *ransomware* lo saben: antes de cifrar los datos, **buscan y destruyen las copias de seguridad**, porque sin copias la víctima tiene que pagar. En esta página ves cómo se ataca la capacidad de recuperación y cómo se defiende.

| Caso | Ataque | Caso real | Tipo |
|---|---|---|---|
| [2.A](#caso-2a--el-ransomware-que-borra-las-copias) | *Ransomware* que borra las copias desde el equipo comprometido | Campañas contra servidores de copias (2024-2025) | Laboratorio |
| [2.B](#caso-2b--nas-expuesto-a-internet) | Cifrado masivo de NAS expuestos a Internet | DeadBolt contra QNAP (2022) | Análisis + comprobación |
| [2.C](#caso-2c--cuando-el-ataque-es-físico-continuidad-sin-sistemas) | Sabotaje que convierte un fallo físico en pérdidas | Supermercados franceses (2026) | Supuesto de continuidad |
| [Búsqueda](#búsqueda-de-vulnerabilidades-en-software-de-copias-y-almacenamiento) | Vulnerabilidades en software de copias y NAS | — | Autónoma |

> [!IMPORTANT]
> Recuerda las [normas de laboratorio](/ud01/ud01-casos/#antes-de-empezar-ética-y-legalidad-del-laboratorio): solo máquinas propias, en redes internas, con instantánea previa. Estos casos **no se entregan**.

---

## Caso 2.A · El *ransomware* que borra las copias

{{< practica etiqueta="Caso" num="2.A" tipo="Guiada" duracion="1.5 h · trabajo autónomo" nivel="2" ra="RA2:c,d;RA6:f" entorno="Debian 13 · restic · rest-server 0.13" entrega="copias en modo solo-añadir y restauración tras un ataque simulado" >}}

### Contexto real

Los informes de respuesta a incidentes repiten el mismo patrón: el atacante entra, obtiene privilegios de administrador y **lo primero que hace es atacar la copia de seguridad**. En 2024, por ejemplo, grupos de *ransomware* como Akira y Fog explotaron la vulnerabilidad **CVE-2024-40711** de Veeam Backup & Replication (una de las soluciones de copia más extendidas) para hacerse con los servidores de copias. En equipos Windows, otra técnica clásica es borrar las instantáneas con `vssadmin delete shadows`.

El problema de fondo es de **diseño**: si el equipo que se copia tiene permiso para **borrar** las copias, un atacante que controle ese equipo también lo tiene.

### Ciclo del caso

| Fase | Descripción |
|---|---|
| **Vulnerabilidad** | El servidor de ficheros envía copias a `srv-copias` con credenciales que permiten **escribir y borrar** (modelo de la práctica 2.5 con SFTP) |
| **Ataque** | El atacante, con `root` en el servidor, cifra los datos y ejecuta `restic forget --prune` para eliminar el historial |
| **Detección** | Cambio masivo de ficheros (extensiones nuevas, ficheros ilegibles), errores de la copia nocturna, peticiones de borrado rechazadas en el servidor de copias |
| **Mitigación** | Servidor de copias en modo **solo-añadir** (*append-only*): el cliente puede crear copias nuevas, pero **no borrar** las antiguas. Limpieza solo desde el propio servidor de copias |
| **Comprobación** | Repetir el ataque y verificar que el historial sobrevive y que se restaura una versión anterior al cifrado |

### Laboratorio

| Máquina | Función | IP (red `sad-lan`) |
|---|---|---|
| `srv-ficheros` | Servidor que se copia (será la «víctima») | 192.168.10.20 |
| `srv-copias` | Servidor de copias con `rest-server` | 192.168.10.30 |

Ambas con **Debian 13**. Haz una **instantánea** de las dos antes de empezar.

#### 1. Servidor de copias en modo solo-añadir (`srv-copias`)

`rest-server` es el servidor HTTP oficial del proyecto restic. Recibe las copias por HTTP y, con la opción `--append-only`, **rechaza cualquier petición de borrado** del cliente.

```bash
sudo apt update && sudo apt install -y restic-rest-server
sudo useradd --system --home /srv/restic --create-home --shell /usr/sbin/nologin restic
```

Comprueba dónde está el ejecutable (`command -v rest-server`; en Debian, `/usr/bin/rest-server`) y crea el servicio `/etc/systemd/system/rest-server.service`. Si el paquete ya instala una unidad propia, `systemctl cat rest-server` te la mostrará: la nuestra la sustituye.

```ini
[Unit]
Description=Servidor de copias restic en modo solo-añadir
After=network-online.target

[Service]
User=restic
Group=restic
ExecStart=/usr/bin/rest-server --path /srv/restic --listen 192.168.10.30:8000 --append-only --private-repos
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

- `--path`: carpeta donde se guardan los repositorios.
- `--listen`: dirección y puerto en los que escucha (solo en la LAN).
- `--append-only`: el cliente puede **añadir** datos, pero no borrar ni sobrescribir.
- `--private-repos`: cada usuario solo puede acceder al repositorio que lleva su nombre.

Crea un usuario para el cliente. `rest-server` usa un fichero `.htpasswd` con contraseñas cifradas con *bcrypt*:

```bash
sudo apt install -y apache2-utils              # proporciona htpasswd
sudo htpasswd -B -c /srv/restic/.htpasswd srv-ficheros
sudo chown restic:restic /srv/restic/.htpasswd && sudo chmod 600 /srv/restic/.htpasswd
sudo systemctl daemon-reload && sudo systemctl enable --now rest-server
sudo ss -tlnp | grep 8000                      # debe escuchar en 192.168.10.30:8000
```

> [!WARNING]
> En este laboratorio el tráfico va por HTTP en una red interna. En producción `rest-server` debe usar **TLS** (`--tls --tls-cert … --tls-key …`); lo aprenderás en la UD03. Los datos van cifrados por restic igualmente, pero la contraseña HTTP viajaría en claro.

#### 2. Primera copia desde el cliente (`srv-ficheros`)

```bash
sudo apt install -y restic
sudo mkdir -p /srv/datos && for i in $(seq 1 20); do echo "Historia clínica $i" | sudo tee /srv/datos/paciente$i.txt >/dev/null; done

# Variables del repositorio (como root, porque se copian datos del sistema)
sudo -i
export RESTIC_REPOSITORY="rest:http://srv-ficheros:CONTRASEÑA_HTTP@192.168.10.30:8000/srv-ficheros/"
echo 'ClaveRepoLab-2026' > /root/.restic-pass && chmod 600 /root/.restic-pass
export RESTIC_PASSWORD_FILE=/root/.restic-pass

restic init
restic backup /srv/datos
restic snapshots
```

Hay **dos contraseñas** distintas: la HTTP (quién puede hablar con el servidor) y la del repositorio (con la que restic **cifra** los datos).

#### 3. El ataque simulado (como `root` en `srv-ficheros`)

Simulamos lo que hace un *ransomware*: cifrar los ficheros con una clave que la víctima no tiene y borrar los originales. Usamos `openssl`, una herramienta legítima, igual que hacen muchos atacantes («vivir de la tierra»).

```bash
cd /srv/datos
CLAVE_ATACANTE=$(openssl rand -hex 32)       # la víctima nunca la conocerá
for f in *.txt; do
  openssl enc -aes-256-cbc -pbkdf2 -salt -in "$f" -out "$f.locked" -pass pass:"$CLAVE_ATACANTE" && rm -f "$f"
done
echo "Tus ficheros han sido cifrados" > LEEME_RESCATE.txt
unset CLAVE_ATACANTE
ls /srv/datos | head
```

A continuación el atacante intenta **destruir el historial** para que no haya vuelta atrás:

```bash
restic snapshots
restic forget --keep-last 1 --prune         # intenta dejar solo la última copia
```

{{% details title="🎯 Resultado esperado" open=false %}}
`restic forget` **falla** con un error de borrado rechazado por el servidor (HTTP **403 Forbidden**). El modo *append-only* impide eliminar instantáneas y datos. El atacante sí podría lanzar `restic backup` y crear una copia **nueva** con los ficheros cifrados, pero las anteriores siguen intactas.

Si repites la práctica sin `--append-only` (modifica el servicio, `daemon-reload` y `restart`), el `forget --prune` **sí** funciona y el historial desaparece: así se comprueba que la medida es la que protege.
{{% /details %}}

#### 4. Detección

En `srv-copias`, el registro del servicio muestra las peticiones rechazadas:

```bash
sudo journalctl -u rest-server --since "15 min ago" --no-pager | tail -n 20
```

En `srv-ficheros`, un indicador sencillo de cifrado masivo es la aparición de muchas extensiones nuevas en poco tiempo:

```bash
find /srv/datos -type f -mmin -10 | sed 's/.*\.//' | sort | uniq -c | sort -rn
```

En la UD04 verás herramientas que lo detectan de forma automática (AIDE, Wazuh).

#### 5. Recuperación y comprobación

La recuperación se hace **desde un equipo limpio** o tras reinstalar la víctima: un equipo comprometido no es de fiar.

```bash
restic snapshots                                   # localiza la copia ANTERIOR al ataque
restic restore <ID_SNAPSHOT_SANO> --target /srv/restaurado
ls /srv/restaurado/srv/datos | head               # deben aparecer los .txt originales, sin .locked
cat /srv/restaurado/srv/datos/paciente1.txt        # debe leerse en claro
restic check                                       # verifica la integridad del repositorio
```

#### 6. Mantenimiento seguro del repositorio

Con *append-only* el cliente no puede borrar, así que la limpieza de copias antiguas se hace **en el servidor de copias**, con acceso local al repositorio:

```bash
# En srv-copias (necesita la contraseña del repositorio)
sudo -u restic restic -r /srv/restic/srv-ficheros forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
```

> [!CAUTION]
> Un atacante que solo controla el cliente podría crear durante semanas copias «envenenadas» con datos ya cifrados. Si tu política de retención borra las copias antiguas automáticamente, acabarías **sin ninguna copia sana**. Por eso hay que **vigilar** las copias (tamaño, número de ficheros cambiados) y **restaurar periódicamente** para comprobarlas: el último **0** de la regla 3-2-1-1-0.

> [!TIP]
> **Caso real de INCIBE.** Lee el caso de la Línea 017 [«Una empresa se infecta de *ransomware* que se propaga al conectar dispositivos»](https://www.incibe.es/linea-de-ayuda-en-ciberseguridad/casos-reales/una-empresa-se-infecta-de-ransomware-que-se-propaga-al-conectar-dispositivos) y responde: ¿qué papel jugaron los soportes conectados?, ¿qué habría cambiado una copia desconectada o en modo solo-añadir?

### Preguntas de análisis

1. ¿Qué «1» de la regla 3-2-1-1-0 implementa el modo *append-only*? ¿Qué otras formas conoces de conseguirlo?
2. ¿Por qué se recomienda que el servidor de copias **no esté en el dominio** ni comparta credenciales con el resto de servidores?
3. Compara el modelo *push* (el cliente envía) y *pull* (el servidor de copias recoge). ¿Cuál resiste mejor a un cliente comprometido?

---

## Caso 2.B · NAS expuesto a Internet

{{< practica etiqueta="Caso" num="2.B" tipo="Autónoma" duracion="1 h · trabajo autónomo" nivel="1" ra="RA1:a;RA2:c;RA6:f" entorno="Debian 13 · Nmap" entrega="análisis del caso y comprobación de exposición" >}}

### El caso real

En **enero de 2022** el *ransomware* **DeadBolt** cifró miles de NAS de la marca QNAP **directamente accesibles desde Internet**, aprovechando una vulnerabilidad de su sistema operativo. No hizo falta engañar a nadie: el atacante encontraba los NAS con buscadores de dispositivos y los cifraba de forma automática. El fabricante tuvo que forzar una actualización a sus clientes. Synology, otro fabricante muy utilizado en pymes, ha sufrido campañas parecidas de fuerza bruta contra el acceso web de sus equipos.

Muchas pymes usan el NAS **a la vez como almacenamiento y como copia de seguridad**: si el NAS se cifra, se pierden los datos y la copia.

### Actividad

1. Identifica en el caso: activo, amenaza, vulnerabilidad y por qué el NAS **no** cumple la regla 3-2-1 si es la única copia.
2. Comprueba desde otra máquina del laboratorio qué servicios ofrece tu servidor de ficheros (o el `srv-copias` del caso anterior). Es lo que vería un atacante:

```bash
sudo apt install -y nmap
sudo nmap -sV -p- 192.168.10.30
```

- `-sV` intenta identificar el servicio y su versión en cada puerto abierto.
- `-p-` revisa los 65 535 puertos TCP, no solo los más comunes.

3. Para cada puerto abierto, decide si debe estar accesible y **desde dónde**. Aplica la regla: la interfaz de administración de un NAS **nunca** se publica en Internet; el acceso remoto, por VPN (UD06).

{{% details title="🎯 Resultado esperado" open=false %}}
En `srv-copias` deben aparecer solo SSH (22) y `rest-server` (8000). Si aparece algún otro servicio que no esperabas, investígalo con `sudo ss -tlnp` en el propio servidor. Esta comparación entre lo que **crees** que está abierto y lo que **realmente** está abierto es la base del inventario de servicios (RA2 h).
{{% /details %}}

---

## Caso 2.C · Cuando el ataque es físico: continuidad sin sistemas

{{< practica etiqueta="Caso" num="2.C" tipo="Proyecto" duracion="1 h · trabajo autónomo" nivel="2" ra="RA1:a,b;RA6:b" entorno="Documento" entrega="ficha de continuidad" >}}

En el [caso 1.B](/ud01/ud01-casos/#caso-1b--supermercados-sin-frío-dispositivos-expuestos-a-internet) viste cómo un ataque informático a los controladores de refrigeración se convirtió en un **daño físico**: alimentos estropeados y, en algunos casos, incendios. La seguridad pasiva pregunta: **si el sistema falla (por un ataque, una avería o un corte de luz), ¿cómo seguimos funcionando?**

### Actividad: ficha de continuidad

Elige un servicio crítico (la refrigeración de un supermercado, el servidor de citas de la clínica o el frigorífico de vacunas de un centro de salud) y completa:

| Pregunta | Respuesta |
|---|---|
| ¿Qué pasa si el sistema deja de funcionar 1 hora? ¿Y 6 horas? | |
| ¿Existe un **sensor o alarma independiente** del sistema principal? | |
| ¿Qué **procedimiento manual** permite seguir (termómetros, registro en papel, agenda impresa)? | |
| ¿Hay **alimentación** alternativa (SAI, grupo electrógeno) y cuánto aguanta? | |
| ¿Quién recibe la alarma fuera del horario laboral? | |
| RTO (tiempo máximo de parada aceptable) y RPO (pérdida máxima de datos aceptable) | |
| ¿Cómo se comprueba el plan? (simulacro, frecuencia) | |

> [!TIP]
> La cadena Picard no se vio afectada porque su refrigeración se gestiona **tienda a tienda**. Descentralizar o tener un mecanismo independiente es una decisión de **continuidad**, no solo de seguridad.

---

## Búsqueda de vulnerabilidades en software de copias y almacenamiento

{{< practica etiqueta="Búsqueda" num="2.D" tipo="Autónoma" duracion="1 h · trabajo autónomo" nivel="1" ra="RA1:c;RA2:b" entorno="Navegador" entrega="tabla de vulnerabilidades" >}}

Usa las fuentes de la [búsqueda de la UD01](/ud01/ud01-casos/#búsqueda-de-vulnerabilidades-cómo-se-investiga-un-cve) (INCIBE-CERT, NVD, KEV, EPSS) y completa la tabla con **una vulnerabilidad de los últimos 24 meses** para cada producto:

| Producto | CVE | CVSS | ¿En KEV? | ¿La usó algún *ransomware*? | Medida |
|---|---|---|---|---|---|
| Veeam Backup & Replication | | | | | |
| QNAP QTS / QuTS hero | | | | | |
| Synology DSM | | | | | |
| restic o rsync | | | | | |
| Firmware de un SAI con tarjeta de red (APC, Eaton…) | | | | | |

> [!TIP]
> En el catálogo **KEV** de CISA hay una columna *Known To Be Used in Ransomware Campaigns*. Filtra por fabricante (`Veeam`, `QNAP`) y fíjate en cuántas vulnerabilidades de software de copias aparecen marcadas: es la prueba de que los atacantes van **a por las copias**.

Pregunta final: ¿por qué un SAI con tarjeta de red o un NAS también deben entrar en el **inventario** y en la política de **actualizaciones**, igual que un servidor?

---

## Qué debes saber explicar

- Por qué los atacantes destruyen las copias **antes** de cifrar, y qué es una copia **inmutable** o en modo **solo-añadir**.
- Cómo se recupera tras un *ransomware*: desde una copia anterior al ataque y en un equipo limpio.
- Por qué un NAS no es una copia de seguridad si es el único lugar donde están los datos.
- Qué es un procedimiento manual de continuidad y por qué complementa a la tecnología.

## Referencias

- restic. [Documentación oficial](https://restic.readthedocs.io/) y [rest-server](https://github.com/restic/rest-server) (opción `--append-only`).
- CISA. [Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog).
- INCIBE. [Guías para empresas](https://www.incibe.es/empresas/guias) (incluye copias de seguridad y continuidad de negocio).
- INCIBE. [Ransomware: una guía de aproximación para el empresario](https://www.incibe.es/empresas/blog/ransomware-guia-aproximacion-el-empresario) y [servicio antiransomware](https://www.incibe.es/empresas/te-ayudamos/servicio-antiransomware).
- INCIBE, Línea 017. [Caso real: una empresa se infecta de *ransomware* que se propaga al conectar dispositivos](https://www.incibe.es/linea-de-ayuda-en-ciberseguridad/casos-reales/una-empresa-se-infecta-de-ransomware-que-se-propaga-al-conectar-dispositivos).
- QNAP. [Security Advisories](https://www.qnap.com/en/security-advisories).
- Veeam. [KB4649: CVE-2024-40711](https://www.veeam.com/kb4649).
