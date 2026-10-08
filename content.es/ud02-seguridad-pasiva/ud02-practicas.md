---
title: "UD2 · Prácticas"
weight: 2
bookToc: true
---

# UD2 · Prácticas

{{< ra "RA1:a,b,g" "RA6:b,f,i" >}}

En estas prácticas aplicas la [teoría de la UD2](/ud02-seguridad-pasiva/ud02-teoria/) en un laboratorio virtual aislado: provocas un **corte eléctrico**, un **disco averiado** y un ***ransomware*** simulado, y compruebas que sabes **recuperar** el servicio y los datos. Cada práctica de fallo incluye la prueba explícita del fallo y la verificación de la recuperación.

| Práctica | Tipo | Nivel | Horas | CE principales |
|---|---|---|--:|---|
| [2.1 Corte eléctrico: SAI simulado y apagado ordenado con NUT](#práctica-21--corte-eléctrico-sai-simulado-y-apagado-ordenado-con-nut) | Guiada | ●●○ | 1 h | RA6.b |
| [2.2 Disco averiado: diagnóstico y RAID 5 con disco de reserva](#práctica-22--disco-averiado-diagnóstico-y-raid-5-con-disco-de-reserva) | Guiada | ●●○ | 2 h | RA6.b, RA6.f |
| [2.3 Instantáneas LVM y copias incrementales con tar](#práctica-23--instantáneas-lvm-y-copias-incrementales-con-tar) | Guiada | ●●○ | 1 h | RA1.a, RA6.f |
| [2.4 Copias remotas con historial usando rsync](#práctica-24--copias-remotas-con-historial-usando-rsync) | Autónoma | ●●○ | 1 h | RA1.a |
| [2.5 Ransomware: copias cifradas con restic y recuperación](#práctica-25--ransomware-copias-cifradas-con-restic-y-recuperación) | Reto | ●●● | 2 h | RA1.a, RA1.g |
| [2.6 Borrado seguro de soportes](#práctica-26--borrado-seguro-de-soportes) | Guiada | ●○○ | 1 h | RA1.b, RA1.g |
| [2.7 Tarea del proyecto: plan de almacenamiento y copias](#tarea-del-proyecto) | Proyecto | ●●● | 1 h | RA1.b, RA6.b, RA6.f, RA6.i |
| **Total** | | | **9 h** | |

> [!CAUTION]
> Las prácticas de RAID, LVM y borrado seguro **destruyen** datos de los dispositivos indicados. Hazlas solo en los discos virtuales creados para ello y comprueba siempre el nombre del dispositivo con `lsblk` antes de ejecutar una orden. Haz una **instantánea** de cada máquina virtual antes de empezar cada práctica.

## Preparación del laboratorio

Todas las prácticas usan las mismas máquinas, que pertenecen a la infraestructura de [Mediterránea Dental](/guia/proyecto-clinica/). Prepáralas una sola vez.

| Máquina | Sistema | Red | Recursos | Discos | Función |
|---|---|---|---|---|---|
| `srv-ficheros` | {{< sw "Debian 13" >}} | LAN `192.168.10.11/24` | 2 GB RAM, 2 CPU | Disco del sistema + **4 discos de 1 GB** | RAID, LVM, NUT y origen de las copias |
| `srv-copias` | {{< sw "Debian 13" >}} | LAN `192.168.10.12/24` | 1 GB RAM, 1 CPU | Disco del sistema de 20 GB | Destino de las copias |

Las dos máquinas deben estar en una **red interna del hipervisor** (sin salida a Internet salvo para instalar paquetes). Puedes clonar la máquina base de la UD1 como **clon enlazado**, generando nuevas direcciones MAC, para ahorrar tiempo.

#### Añadir los discos de práctica

Con `srv-ficheros` **apagada**, añade cuatro discos VDI de 1 GB (`raid1.vdi` a `raid4.vdi`) en el controlador SATA. Con VirtualBox 7.x desde la línea de órdenes del anfitrión:

```bash
for i in 1 2 3 4; do
  VBoxManage createmedium disk --filename "raid$i.vdi" --size 1024
  VBoxManage storageattach srv-ficheros --storagectl "SATA" --port $i --device 0 --type hdd --medium "raid$i.vdi"
done
```

- `VBoxManage createmedium disk` crea un disco virtual de 1024 MB.
- `VBoxManage storageattach` lo conecta al puerto `$i` del controlador. El nombre del controlador puede ser «SATA» o «Controlador SATA» según el idioma: compruébalo con `VBoxManage showvminfo srv-ficheros | grep -i storage`.

#### Nombres y paquetes

En las **dos** máquinas, añade los nombres a `/etc/hosts` y comprueba la resolución:

```bash
echo "192.168.10.11  srv-ficheros" | sudo tee -a /etc/hosts   # añade (-a) la línea al final del fichero
echo "192.168.10.12  srv-copias"   | sudo tee -a /etc/hosts
getent hosts srv-copias            # comprueba que el nombre se resuelve
ping -c 3 srv-copias               # comprueba la conectividad
```

{{< tabs >}}
{{% tab "Debian 13" %}}
```bash
# En srv-ficheros
sudo apt install -y mdadm lvm2 rsync restic smartmontools nut cryptsetup
# En srv-copias
sudo apt install -y rsync openssh-server
```
Al instalar `mdadm` puede aparecer una pregunta sobre el envío de correo: acepta los valores por defecto.
{{% /tab %}}
{{% tab "AlmaLinux 10" %}}
```bash
# En srv-ficheros (restic y nut están en EPEL)
sudo dnf install -y epel-release
sudo dnf install -y mdadm lvm2 rsync restic smartmontools nut cryptsetup
# En srv-copias
sudo dnf install -y rsync openssh-server
```
Rutas distintas a Debian: `/etc/ups/` en lugar de `/etc/nut/`, `/etc/mdadm.conf` en lugar de `/etc/mdadm/mdadm.conf` y `dracut -f` en lugar de `update-initramfs -u`.
{{% /tab %}}
{{< /tabs >}}

> [!NOTE]
> Los ejemplos están escritos para {{< sw "Debian 13" >}}. Cuando una ruta o un comando difiera en otro sistema se indica expresamente.

---

## Práctica 2.1 · Corte eléctrico: SAI simulado y apagado ordenado con NUT

{{< practica num="2.1" tipo="Guiada" duracion="1 h" nivel="2" ra="RA6: b" entorno="Debian 13 · NUT 2.8" entrega="capturas del registro con los tres estados" >}}

#### Objetivo

Comprobar que un servidor se apaga de forma **ordenada** cuando el SAI informa de batería baja, sin necesidad de un SAI real, y reconocer los estados `OL`, `OB` y `LB`.

#### Contexto

Un corte de luz en mitad de una escritura puede corromper el sistema de ficheros (le ocurrió a la asesoría del supuesto de la teoría). El SAI da minutos de autonomía; **NUT** (*Network UPS Tools*) es el software que lee el estado del SAI y ordena al servidor apagarse antes de que se agote la batería. El *driver* `dummy-ups` lee el estado de un fichero de texto, de modo que el corte eléctrico se simula editando ese fichero. Ciclo: *amenaza* (corte) → *vulnerabilidad* (servidor sin apagado ordenado) → *fallo provocado* → *detección* (`upsmon`) → *mitigación* (apagado ordenado) → *comprobación* (registro).

#### Requisitos previos

- `srv-ficheros` con el paquete `nut` instalado (ver [Preparación](#preparación-del-laboratorio)).
- Ficheros de NUT en `/etc/nut/` ({{< sw "Debian 13" >}}); en AlmaLinux están en `/etc/ups/`.

#### Desarrollo

{{% steps %}}

1. **Copia de seguridad de la configuración** y modo de funcionamiento. `standalone` indica que el mismo equipo ejecuta el servidor y el monitor de NUT.

   ```bash
   cd /etc/nut
   sudo cp -a /etc/nut /etc/nut.bak                       # copia de seguridad para poder volver atrás
   sudo sed -i 's/^MODE=.*/MODE=standalone/' nut.conf     # sustituye la línea MODE por MODE=standalone
   ```

2. **Estado inicial del SAI simulado**: en línea (`OL`) y con la batería llena.

   ```bash
   sudo tee dummy.dev >/dev/null <<'EOT'
   ups.status: OL
   battery.charge: 100
   battery.runtime: 1800
   ups.load: 35
   input.voltage: 230
   EOT
   ```

3. **Definición del SAI** en `ups.conf`: nombre `saisim`, *driver* `dummy-ups` y el fichero de datos como «puerto».

   ```bash
   sudo tee -a ups.conf >/dev/null <<'EOT'

   [saisim]
       driver = dummy-ups
       port = dummy.dev
       desc = "SAI simulado para el laboratorio"
   EOT
   ```

4. **Usuario de `upsmon`** en `upsd.users`. La contraseña es solo de laboratorio.

   ```bash
   sudo tee -a upsd.users >/dev/null <<'EOT'

   [monuser]
       password = LabNut2026
       upsmon primary
   EOT
   ```

5. **Vigilancia** en `upsmon.conf`. En lugar de apagar de verdad, `SHUTDOWNCMD` registra el evento en el diario con `logger`, para poder repetir la prueba.

   ```bash
   sudo tee -a upsmon.conf >/dev/null <<'EOT'

   MONITOR saisim@localhost 1 monuser LabNut2026 primary
   SHUTDOWNCMD "/usr/bin/logger -t NUT 'APAGADO ORDENADO: aquí se ejecutaría /sbin/shutdown -h +0'"
   NOTIFYFLAG ONBATT SYSLOG+WALL
   NOTIFYFLAG LOWBATT SYSLOG+WALL
   NOTIFYFLAG ONLINE SYSLOG+WALL
   EOT

   sudo chown root:nut /etc/nut/*.conf /etc/nut/upsd.users /etc/nut/dummy.dev 2>/dev/null
   sudo chmod 640 /etc/nut/upsd.users /etc/nut/upsmon.conf    # contienen contraseñas: no legibles por todos
   ```

6. **Arranca los servicios** y comprueba el estado inicial. `systemctl` es el gestor de servicios de systemd; `enable --now` los activa en cada arranque y los inicia ya.

   ```bash
   sudo systemctl restart nut-driver-enumerator.service 2>/dev/null; sudo upsdrvctl start 2>/dev/null
   sudo systemctl enable --now nut-server nut-monitor
   upsc saisim@localhost ups.status        # upsc consulta una variable del SAI; debe responder: OL
   ```

7. **Fallo provocado: corte eléctrico.** En una terminal sigue el registro:

   ```bash
   sudo journalctl -f -t upsmon -t NUT
   ```

   En otra terminal, pasa el SAI a batería (`OB`) y, después, a batería baja (`OB LB`):

   ```bash
   # Corte de luz: el SAI pasa a batería
   sudo sed -i 's/^ups.status:.*/ups.status: OB/; s/^battery.charge:.*/battery.charge: 60/' /etc/nut/dummy.dev
   sleep 10; upsc saisim@localhost ups.status

   # La batería se agota
   sudo sed -i 's/^ups.status:.*/ups.status: OB LB/; s/^battery.charge:.*/battery.charge: 8/' /etc/nut/dummy.dev
   ```

   Resultado esperado en el registro:

   ```text
   upsmon[...]: UPS saisim@localhost on battery
   upsmon[...]: UPS saisim@localhost battery is low
   upsmon[...]: Executing automatic power-fail shutdown
   NUT[...]: APAGADO ORDENADO: aquí se ejecutaría /sbin/shutdown -h +0
   ```

8. **Recuperación.** Devuelve el SAI al estado `OL` y reinicia el monitor:

   ```bash
   sudo sed -i 's/^ups.status:.*/ups.status: OL/; s/^battery.charge:.*/battery.charge: 100/' /etc/nut/dummy.dev
   sudo systemctl restart nut-monitor
   upsc saisim@localhost ups.status        # OL
   ```

{{% /steps %}}

**Análisis.** Responde: (1) ¿qué significan `OL`, `OB` y `LB`? (2) ¿Por qué no se apaga el servidor en cuanto el SAI pasa a batería? (3) ¿Cómo se apagarían otros servidores conectados al mismo SAI? (4) ¿Qué cambiarías en `SHUTDOWNCMD` en un servidor real?

{{% details title="Pista" %}}
NUT espera a `LB` porque el objetivo es **aprovechar toda la autonomía** posible por si vuelve la luz. Para varios servidores, piensa en `upsmon` en modo `secondary` conectando al `upsd` del servidor principal por el puerto 3493.
{{% /details %}}

{{% details title="Solución" %}}
1. `OL` (*on line*): hay red eléctrica; `OB` (*on battery*): el SAI funciona con batería; `LB` (*low battery*): queda poca batería.
2. Porque un corte breve se resuelve solo; se apaga al llegar a `LB` para no perder autonomía útil.
3. Con `upsmon` en modo `secondary` en esos equipos, que consultan al `upsd` de este (puerto 3493) y se apagan al recibir `LB`.
4. Sustituirlo por `/sbin/shutdown -h +0` (apagado real), tras comprobar la cadena completa.
{{% /details %}}

#### Comprobación

- [ ] `upsc saisim@localhost ups.status` devuelve `OL` al empezar y al terminar.
- [ ] El diario muestra `on battery` y `battery is low` tras editar `dummy.dev`.
- [ ] Aparece el mensaje `APAGADO ORDENADO` generado por `SHUTDOWNCMD`.
- [ ] Los ficheros con contraseña (`upsd.users`, `upsmon.conf`) tienen permisos `640`.

#### Problemas habituales

| Problema | Causa | Solución |
|---|---|---|
| `upsc: Error: Driver not connected` | El *driver* no está arrancado o no encuentra `dummy.dev` | `sudo upsdrvctl -D start`; revisa permisos y ruta del fichero |
| El estado no cambia a `OB` | Se editó otro fichero o NUT no ha consultado aún | Edita `/etc/nut/dummy.dev` y espera unos segundos (NUT consulta periódicamente) |
| Los nombres de servicio no coinciden | Varían según la versión | `systemctl list-units 'nut*'` para verlos (`nut-server`, `nut-monitor`, `nut-driver@saisim`) |

#### Consideraciones de seguridad

`upsd` escucha por defecto solo en `localhost`; no lo expongas a la red sin restringir el acceso con el cortafuegos. Las contraseñas de `upsd.users` se guardan en claro: por eso el fichero es `640` y la contraseña debe ser distinta en producción. Un `SHUTDOWNCMD` mal probado puede apagar un servidor por error: prueba siempre primero con `logger`.

#### Ampliación

Configura un segundo servidor (`srv-copias`) como `secondary` de `srv-ficheros` y comprueba que también recibe el aviso `LB`. Calcula la autonomía necesaria de un SAI para `srv-ficheros` con una carga de 250 W y un apagado que tarda 3 minutos.

---

## Práctica 2.2 · Disco averiado: diagnóstico y RAID 5 con disco de reserva

{{< practica num="2.2" tipo="Guiada" duracion="2 h" nivel="2" ra="RA6: b, f" entorno="Debian 13 · mdadm" entrega="informe con salidas de /proc/mdstat antes, durante y después" >}}

#### Objetivo

Identificar los dispositivos de almacenamiento, consultar su estado de salud, y crear, supervisar y reparar un **RAID 5 por software con disco de reserva** (*hot spare*), demostrando que los datos sobreviven a la avería de un disco.

#### Contexto

Los discos se averían y, si los datos viven en uno solo, esa avería es una pérdida. RAID 5 reparte los datos y la paridad entre varios discos y tolera la pérdida de uno; el disco de reserva inicia la reconstrucción automáticamente. Ciclo: *amenaza* (avería de un disco) → *vulnerabilidad* (datos en un único disco) → *fallo provocado* (`--fail`) → *detección* (`/proc/mdstat`, `mdadm --monitor`) → *mitigación* (RAID 5 + reserva) → *comprobación* (datos íntegros y array reconstruido). Es el almacenamiento redundante de `srv-ficheros` que se amplía en la [UD7](/ud07-alta-disponibilidad/).

#### Requisitos previos

- `srv-ficheros` con los cuatro discos de 1 GB y los paquetes `mdadm` y `smartmontools`.
- Instantánea de la máquina antes de empezar.

#### Desarrollo

{{% steps %}}

1. **Identifica el almacenamiento.** `lsblk` lista los dispositivos de bloque; `-o` elige las columnas.

   ```bash
   lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL
   ```

   ```text
   NAME     SIZE TYPE FSTYPE MOUNTPOINTS MODEL
   sda       25G disk                    VBOX HARDDISK
   ├─sda1    24G part ext4   /
   └─sda2     1G part swap   [SWAP]
   sdb        1G disk                    VBOX HARDDISK
   sdc        1G disk                    VBOX HARDDISK
   sdd        1G disk                    VBOX HARDDISK
   sde        1G disk                    VBOX HARDDISK
   ```

   > [!WARNING]
   > Identifica **siempre** el disco del sistema antes de ejecutar comandos de formato o RAID. Aquí es `sda` (25 GB); los discos de práctica son los pequeños (`sdb` a `sde`). Un `mdadm --create` o `wipefs` sobre el disco equivocado destruye el sistema.

2. **Consulta S.M.A.R.T.** `smartctl` (paquete `smartmontools`) lee el diagnóstico interno del disco.

   ```bash
   sudo smartctl -i -H /dev/sdb
   # SMART support is: Unavailable - device lacks SMART capability.
   ```

   VirtualBox no emula S.M.A.R.T., así que repite la consulta en tu **equipo anfitrión**: en Linux `sudo smartctl -a /dev/sda` o `sudo nvme smart-log /dev/nvme0`; en Windows instala [smartmontools para Windows](https://www.smartmontools.org/wiki/Download) y ejecuta en una consola de administrador `smartctl --scan` y `smartctl -a /dev/sda`. Anota modelo, horas de funcionamiento, temperatura y, según el tipo de disco, los atributos 5, 197 y 198 (HDD) o `percentage_used` y `media_errors` (NVMe).

3. **Crea el RAID 5** con tres discos activos y uno de reserva. `--level=5` es el nivel RAID, `--raid-devices=3` los discos activos y `--spare-devices=1` la reserva.

   ```bash
   sudo mdadm --create /dev/md0 --level=5 --raid-devices=3 \
        /dev/sdb /dev/sdc /dev/sdd --spare-devices=1 /dev/sde
   ```

   `mdadm` pide confirmación (`Continue creating array? y`). Sigue la sincronización inicial (Ctrl+C para salir) y revisa el resultado:

   ```bash
   watch -n 1 cat /proc/mdstat
   sudo mdadm --detail /dev/md0
   ```

   Campos clave de la salida:

   ```text
           Raid Level : raid5
           Array Size : 2093056 (2044.00 MiB 2143.29 MB)     ← (3 - 1) × 1 GB
         Raid Devices : 3
        Total Devices : 4
                State : clean
       Active Devices : 3
      Working Devices : 4
       Failed Devices : 0
        Spare Devices : 1
   ```

4. **Sistema de ficheros y montaje.** `mkfs.ext4` formatea el array con una etiqueta y `mount` lo monta en `/srv/datos`.

   ```bash
   sudo mkfs.ext4 -L DATOS /dev/md0
   sudo mkdir -p /srv/datos
   sudo mount /dev/md0 /srv/datos
   df -h /srv/datos
   ```

5. **Guarda la configuración del array** para que se ensamble con el mismo nombre en cada arranque. Evita así que aparezca como `md127`.

   {{< sw "Debian 13" >}}

   ```bash
   sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf
   sudo update-initramfs -u
   ```

   {{< sw "AlmaLinux 10" >}}

   ```bash
   sudo mdadm --detail --scan | sudo tee -a /etc/mdadm.conf
   sudo dracut -f
   ```

6. **Montaje permanente por UUID.** Haz copia de `fstab`, verifica la sintaxis y prueba sin reiniciar. `nofail` permite que el sistema arranque aunque el RAID no esté disponible.

   ```bash
   sudo cp -a /etc/fstab /etc/fstab.bak
   UUID=$(sudo blkid -s UUID -o value /dev/md0)
   echo "UUID=$UUID  /srv/datos  ext4  defaults,nofail  0  2" | sudo tee -a /etc/fstab
   sudo findmnt --verify                                  # comprueba la sintaxis de fstab
   sudo umount /srv/datos && sudo mount -a && findmnt /srv/datos
   ```

   > [!WARNING]
   > Si `findmnt --verify` muestra errores, **no reinicies**: corrige `/etc/fstab` o restaura `/etc/fstab.bak`. Un `fstab` incorrecto puede dejar el sistema en modo de emergencia. Reinicia después y comprueba que el RAID se ensambla y se monta solo.

7. **Datos de prueba con sumas de verificación.** Se generan 50 ficheros aleatorios y un documento reconocible, y se guardan sus hashes SHA-256 para comprobar la integridad después.

   ```bash
   sudo mkdir -p /srv/datos/empresa
   for i in $(seq 1 50); do
     head -c 200K /dev/urandom | sudo tee /srv/datos/empresa/documento_$i.bin >/dev/null
   done
   echo "Contrato confidencial" | sudo tee /srv/datos/empresa/contrato.txt
   cd /srv/datos && sudo find empresa -type f -exec sha256sum {} + | sudo tee /root/hashes_datos.sha256 >/dev/null
   ```

8. **Fallo provocado: avería de un disco.** `--fail` marca el disco como averiado y simula su pérdida.

   ```bash
   sudo mdadm /dev/md0 --fail /dev/sdc
   cat /proc/mdstat
   sudo journalctl -k --since "-5min" | grep -i md
   ```

   Esperado: `sdc` aparece con `(F)`, el estado pasa de `[3/3] [UUU]` a `[3/2] [U_U]`, `sde` empieza a reconstruirse (`recovery = …%`) y el diario registra `Disk failure on sdc, disabling device`. Comprueba que los datos siguen accesibles **e íntegros** mientras reconstruye:

   ```bash
   cd /srv/datos && sudo sha256sum -c --quiet /root/hashes_datos.sha256 && echo "Datos íntegros"
   ```

9. **Sustituye el disco averiado.** Se retira del array, se limpia (en la realidad sería un disco nuevo) y se añade como nueva reserva.

   ```bash
   sudo mdadm /dev/md0 --remove /dev/sdc
   sudo wipefs -a /dev/sdc                  # borra las firmas del disco antiguo
   sudo mdadm /dev/md0 --add /dev/sdc
   sudo mdadm --detail /dev/md0 | grep -E "State|Devices|spare"
   ```

10. **Fallo doble (en una instantánea).** Haz una instantánea de la máquina, marca como fallidos **dos** discos activos seguidos sin esperar a la reconstrucción y observa qué ocurre con el array y con los datos. Después restaura la instantánea.

11. **Monitorización.** Genera un evento de prueba y comprueba el servicio de vigilancia.

    ```bash
    sudo mdadm --monitor --scan --oneshot --test      # genera un evento TestMessage por cada RAID
    sudo journalctl --since "-2min" | grep -i mdadm
    systemctl status mdmonitor --no-pager
    ```

{{% /steps %}}

**Análisis.** (1) ¿Por qué la capacidad útil es de unos 2 GB con tres discos de 1 GB? (2) ¿Qué ventaja ha aportado el disco de reserva? (3) ¿Qué habría pasado sin él si fallase un segundo disco durante la sustitución? (4) Explica con un ejemplo por qué este RAID no sustituye a una copia de seguridad.

{{% details title="Pista" %}}
Piensa en el *peor momento posible*: ¿qué pasaría si falla otro disco justo durante la reconstrucción? ¿Y si un *ransomware* cifra los datos? ¿Los protege el RAID? Relaciónalo con la regla 3-2-1-1-0.
{{% /details %}}

{{% details title="Solución" %}}
1. RAID 5 dedica la capacidad de un disco a la paridad: (3 − 1) × 1 GB.
2. La reconstrucción empieza sola, sin esperar a que una persona intervenga, y se reduce la ventana de riesgo.
3. Habría que sustituir el disco a mano y, si fallaba otro antes de terminar la reconstrucción, el array se perdería.
4. RAID replica también los errores: si alguien borra un fichero o un *ransomware* lo cifra, el cambio se propaga a todos los discos al instante.
{{% /details %}}

#### Comprobación

- [ ] `mdadm --detail /dev/md0` muestra `raid5`, 3 dispositivos activos y 1 de reserva.
- [ ] Tras el fallo, `/proc/mdstat` muestra `[3/2]`, `(F)` y la línea `recovery`.
- [ ] `sha256sum -c` devuelve «Datos íntegros» durante y después de la reconstrucción.
- [ ] El array vuelve a `[3/3] [UUU]` y se monta solo tras reiniciar.
- [ ] Has explicado qué ocurre en el fallo doble.

#### Problemas habituales

| Problema | Causa | Solución |
|---|---|---|
| `mdadm: Device or resource busy` | El disco tiene particiones o pertenece a otro RAID | `sudo wipefs -a /dev/sdX`; `sudo mdadm --stop /dev/md127` si se ensambló un RAID antiguo |
| Tras reiniciar aparece `/dev/md127` | No se guardó `mdadm.conf` o no se regeneró el *initramfs* | Guardar la configuración y ejecutar `update-initramfs -u` o `dracut -f` |
| El sistema arranca en modo de emergencia | Error en `/etc/fstab` | Corregir `fstab` o restaurar `fstab.bak`; usar `nofail` |
| No se ve avance de la sincronización | Es normal: tarda unos minutos | `watch -n 1 cat /proc/mdstat` |

#### Consideraciones de seguridad

Un `mdadm --create` o `wipefs` sobre el dispositivo equivocado destruye datos: verifica con `lsblk`. RAID protege frente a **fallos de hardware**, no frente a borrados, errores o *ransomware*; sin vigilancia (`mdmonitor`) un array degradado puede pasar meses sin que nadie lo note. Los discos de un mismo lote tienden a fallar juntos: en producción mezcla lotes o fabricantes.

#### Ampliación

Compara en una tabla RAID 1, RAID 5, RAID 6 y RAID 10 para un servidor de base de datos con 6 discos de 2 TB, recomienda uno y justifícalo. Repite la práctica con un RAID 1 de dos discos.

---

## Práctica 2.3 · Instantáneas LVM y copias incrementales con tar

{{< practica num="2.3" tipo="Guiada" duracion="1 h" nivel="2" ra="RA1: a; RA6: f" entorno="Debian 13 · LVM2 · GNU tar" entrega="salidas de lvs y de la restauración de la cadena" >}}

#### Objetivo

Usar **instantáneas LVM** para obtener copias coherentes de un volumen en uso y realizar copias **completas e incrementales** con `tar`, restaurando la cadena completa.

#### Contexto

Copiar ficheros mientras una aplicación los modifica puede producir una copia inconsistente. Una instantánea LVM congela el estado del volumen en un instante; `tar` con `--listed-incremental` copia solo lo que ha cambiado desde la última copia. Ninguna de las dos cosas protege ante la pérdida de los discos: la instantánea vive en el mismo grupo de volúmenes.

#### Requisitos previos

- Práctica 2.2 hecha: `/dev/md0` operativo y datos de prueba en `/srv/datos`.
- Paquetes `lvm2` y `cryptsetup` instalados. Instantánea previa de la máquina.

#### Desarrollo

{{% steps %}}

1. **Convierte el RAID en volumen físico LVM.** Esta operación **borra** el sistema de ficheros de `/dev/md0`: los datos se regeneran al final.

   > [!WARNING]
   > Haz antes una copia de los datos de prueba o vuelve a ejecutarlos después. Deja espacio libre en el grupo de volúmenes para las instantáneas.

   ```bash
   sudo umount /srv/datos
   sudo sed -i.bak '\#/srv/datos#d' /etc/fstab     # elimina la línea del montaje anterior (copia en fstab.bak)
   sudo wipefs -a /dev/md0
   sudo pvcreate /dev/md0                          # prepara el dispositivo como volumen físico
   sudo vgcreate vg_datos /dev/md0                 # crea el grupo de volúmenes
   sudo lvcreate -L 1.2G -n lv_datos vg_datos      # volumen lógico de 1,2 GB; el resto queda libre
   sudo mkfs.ext4 /dev/vg_datos/lv_datos
   sudo mount /dev/vg_datos/lv_datos /srv/datos
   sudo vgs; sudo lvs
   ```

2. **Instantánea y modificación del original.** `--snapshot -L 200M` reserva 200 MB para guardar los bloques que cambien.

   ```bash
   echo "versión 1" | sudo tee /srv/datos/informe.txt
   sudo lvcreate --snapshot -L 200M -n snap_datos /dev/vg_datos/lv_datos
   echo "versión 2 (modificada tras la instantánea)" | sudo tee /srv/datos/informe.txt

   sudo mkdir -p /mnt/snap
   sudo mount -o ro /dev/vg_datos/snap_datos /mnt/snap
   cat /srv/datos/informe.txt     # versión 2
   cat /mnt/snap/informe.txt      # versión 1: estado congelado
   ```

3. **Copia coherente desde la instantánea** y limpieza. Observa la columna `Data%` de la instantánea.

   ```bash
   sudo tar -czpf /root/datos_$(date +%F_%H%M).tar.gz -C /mnt/snap .
   sudo lvs
   sudo umount /mnt/snap
   sudo lvremove -y /dev/vg_datos/snap_datos
   ```

4. **Remonta de forma permanente** el volumen lógico por UUID y regenera los datos de prueba y su fichero de hashes (paso 7 de la práctica 2.2): las prácticas siguientes los usan.

   ```bash
   UUID=$(sudo blkid -s UUID -o value /dev/vg_datos/lv_datos)
   echo "UUID=$UUID  /srv/datos  ext4  defaults,nofail  0  2" | sudo tee -a /etc/fstab
   sudo findmnt --verify
   ```

5. **Copia completa (nivel 0) con `tar`.** El fichero `.snar` guarda el estado de la última copia; sin él, la siguiente copia sería completa. Guárdalo junto a las copias.

   ```bash
   sudo mkdir -p /backup/tar
   sudo mkdir -p /srv/datos/proyecto && echo "inicio" | sudo tee /srv/datos/proyecto/notas.txt
   sudo tar --listed-incremental=/backup/tar/datos.snar \
            -czpf /backup/tar/datos_0_full.tar.gz -C /srv datos
   ```

6. **Cambios y copias incrementales.**

   ```bash
   # Lunes: se crea un fichero
   echo "tarea lunes" | sudo tee /srv/datos/proyecto/lunes.txt
   sudo tar --listed-incremental=/backup/tar/datos.snar -czpf /backup/tar/datos_1_inc.tar.gz -C /srv datos

   # Martes: se modifica un fichero y se borra otro
   echo "cambio martes" | sudo tee -a /srv/datos/proyecto/notas.txt
   sudo rm /srv/datos/proyecto/lunes.txt
   sudo tar --listed-incremental=/backup/tar/datos.snar -czpf /backup/tar/datos_2_inc.tar.gz -C /srv datos

   ls -lh /backup/tar/                                        # la completa es mucho mayor que las incrementales
   tar -tzvf /backup/tar/datos_1_inc.tar.gz | grep -v '/$'    # solo ficheros nuevos o modificados
   ```

7. **Restaura la cadena en orden** (primero la completa, luego cada incremental). `--listed-incremental=/dev/null` hace que `tar` aplique también los borrados registrados.

   ```bash
   sudo mkdir -p /tmp/restaura_tar
   for f in /backup/tar/datos_0_full.tar.gz /backup/tar/datos_1_inc.tar.gz /backup/tar/datos_2_inc.tar.gz; do
     sudo tar --listed-incremental=/dev/null -xzpf "$f" -C /tmp/restaura_tar
   done
   ls /tmp/restaura_tar/datos/proyecto/
   cat /tmp/restaura_tar/datos/proyecto/notas.txt
   ```

{{% /steps %}}

**Análisis.** (1) ¿Qué ocurriría si durante la vida de la instantánea se modificasen más de 200 MB en el volumen original? (2) Si quisieras recuperar `lunes.txt`, ¿qué copias restaurarías?

{{% details title="Pista" %}}
Mira la columna `Data%` de `lvs`: mide cuánto de los 200 MB se ha consumido. Para la segunda pregunta, ¿en qué copia estaba `lunes.txt` y en cuál ya se había borrado?
{{% /details %}}

{{% details title="Solución" %}}
1. La instantánea se llena y se **invalida**: la copia hecha desde ella dejaría de ser fiable. Hay que dimensionarla según los cambios esperados.
2. Solo la completa y la incremental del lunes (`datos_0_full` y `datos_1_inc`), sin aplicar la del martes.
{{% /details %}}

#### Comprobación

- [ ] `informe.txt` muestra «versión 2» en el original y «versión 1» en la instantánea.
- [ ] `lvs` muestra el volumen `lv_datos` y, mientras existe, `snap_datos` con su `Data%`.
- [ ] `notas.txt` restaurado contiene el cambio del martes y `lunes.txt` **no** aparece.
- [ ] `findmnt --verify` no muestra errores y `/srv/datos` se monta tras reiniciar.

#### Problemas habituales

| Problema | Causa | Solución |
|---|---|---|
| `Insufficient free space` al crear la instantánea | El grupo no tiene extensiones libres | `sudo vgs` (columna `VFree`); reduce `-L` o amplía el grupo |
| La instantánea se invalida | Los cambios superan su tamaño | Mídela con `sudo lvs` (`Data%`) y reserva más espacio |
| Faltan ficheros o aparecen ficheros ya borrados | Cadena restaurada sin orden o con un eslabón omitido | Restaura en orden con `--listed-incremental=/dev/null` |

#### Consideraciones de seguridad

Una instantánea **no es una copia de seguridad**: comparte discos con el original. El fichero `.snar` y las copias contienen datos reales: protege `/backup` con permisos restrictivos y, en producción, almacénalas en otro equipo. Las copias hechas con `tar -p` conservan permisos; extráelas siempre como administrador y en un directorio temporal antes de sustituir datos.

#### Ampliación

Haz una copia **diferencial** (nuevo `.snar` copiado del nivel 0 antes de cada ejecución) y compara el espacio y el número de ficheros a restaurar con la incremental. Amplía el volumen lógico con `lvextend -r`.

---

## Práctica 2.4 · Copias remotas con historial usando rsync

{{< practica num="2.4" tipo="Autónoma" duracion="1 h" nivel="2" ra="RA1: a" entorno="Debian 13 · rsync · OpenSSH" entrega="script, salida de du/ls -li y restauración de un fichero" >}}

#### Objetivo

Implantar una copia diaria remota con **historial** mediante `rsync --link-dest` y restaurar un fichero borrado, con autenticación SSH por clave.

#### Contexto

`rsync` transfiere solo las diferencias. Con `--link-dest`, cada carpeta diaria parece una copia completa pero los ficheros sin cambios son **enlaces duros** al mismo dato, de modo que se conserva el historial ocupando poco espacio. Esta copia se hace a otro equipo (`srv-copias`), requisito de la regla 3-2-1-1-0.

#### Requisitos previos

- `srv-ficheros` con datos en `/srv/datos` y `srv-copias` con `openssh-server`.
- Conectividad entre ambas por nombre.

#### Desarrollo

{{% steps %}}

1. **Usuario de copias en `srv-copias`**, con un directorio accesible solo por él.

   ```bash
   sudo useradd -m -s /bin/bash copias
   sudo mkdir -p /backups/srv-ficheros
   sudo chown copias: /backups/srv-ficheros
   sudo chmod 700 /backups/srv-ficheros
   ```

2. **Clave SSH en `srv-ficheros`**, como `root` (para poder leer todos los ficheros). `-t ed25519` es el tipo de clave (UD3); `-N ""` la deja sin frase de paso porque la usará un proceso automático; `ssh-copy-id` instala la clave pública en `~/.ssh/authorized_keys` del usuario remoto.

   ```bash
   sudo ssh-keygen -t ed25519 -f /root/.ssh/id_backup -N "" -C "backup@srv-ficheros"
   sudo ssh-copy-id -i /root/.ssh/id_backup.pub copias@srv-copias    # pide la contraseña de «copias»
   sudo ssh -i /root/.ssh/id_backup copias@srv-copias hostname       # debe responder sin contraseña
   ```

3. **Script de copia** `/usr/local/sbin/backup-rsync.sh` en `srv-ficheros`. `-aAXH` conserva atributos, ACL, atributos extendidos y enlaces duros; `--delete` refleja los borrados en la nueva carpeta.

   ```bash
   #!/usr/bin/env bash
   # Copia diaria con historial mediante rsync --link-dest
   set -euo pipefail
   ORIGEN="/srv/datos/"
   DESTINO="copias@srv-copias:/backups/srv-ficheros"
   SSH="ssh -i /root/.ssh/id_backup"
   FECHA=$(date +%F_%H%M)

   rsync -aAXH --delete -e "$SSH" \
         --link-dest=../ultima \
         "$ORIGEN" "$DESTINO/$FECHA/"

   # Actualizar el enlace «ultima» en el servidor remoto
   $SSH copias@srv-copias "ln -sfn $FECHA /backups/srv-ficheros/ultima"
   logger -t backup-rsync "Copia $FECHA completada"
   ```

   ```bash
   sudo install -m 750 backup-rsync.sh /usr/local/sbin/
   sudo /usr/local/sbin/backup-rsync.sh
   # Modifica algún fichero en /srv/datos y espera 1 minuto
   sudo /usr/local/sbin/backup-rsync.sh
   ```

4. **Verifica el historial** en `srv-copias`: dos copias que parecen completas pero comparten los ficheros no modificados.

   ```bash
   ls -l /backups/srv-ficheros/
   du -sh /backups/srv-ficheros/*                                   # la segunda copia ocupa muy poco
   ls -li /backups/srv-ficheros/*/empresa/documento_1.bin           # mismo número de inodo = mismo fichero
   ```

5. **Fallo provocado y restauración.** Borra un fichero por error y recupéralo de la última copia.

   ```bash
   sudo rm /srv/datos/empresa/contrato.txt
   sudo rsync -av -e "ssh -i /root/.ssh/id_backup" \
        copias@srv-copias:/backups/srv-ficheros/ultima/empresa/contrato.txt /srv/datos/empresa/
   cat /srv/datos/empresa/contrato.txt
   ```

{{% /steps %}}

{{% details title="Pista" %}}
Cada carpeta diaria parece una copia completa, pero los ficheros sin cambios son **enlaces duros**. Compara `du -sh` de la primera carpeta con el de todas juntas: el total crece solo por lo que cambió.
{{% /details %}}

#### Comprobación

- [ ] `ssh -i /root/.ssh/id_backup copias@srv-copias hostname` funciona sin contraseña.
- [ ] Existen dos carpetas con fecha y el enlace `ultima` apunta a la más reciente.
- [ ] `ls -li` muestra el **mismo inodo** en ficheros sin cambios de ambas copias.
- [ ] `contrato.txt` se recupera con su contenido original.

#### Problemas habituales

| Problema | Causa | Solución |
|---|---|---|
| `rsync` borra datos del destino inesperadamente | Barra final o `--delete` mal usados | Usa siempre `--dry-run` (`-n`) antes de la primera ejecución |
| SSH pide contraseña | La clave no está instalada o los permisos de `~/.ssh` son incorrectos | Repite `ssh-copy-id`; `~/.ssh` debe ser `700` y `authorized_keys` `600` |
| La segunda copia ocupa lo mismo que la primera | Falta `--link-dest` o el enlace `ultima` no existe | Revisa la ruta relativa `../ultima` y el enlace remoto |

#### Consideraciones de seguridad

Quien robe `id_backup` podría escribir (y borrar) en `srv-copias`. En un entorno real se restringe la clave en `authorized_keys` con opciones como `restrict,from="192.168.10.11"` y, si es posible, con `rrsync` para que solo pueda ejecutar `rsync` sobre un directorio. El modelo *pull* (que sea el servidor de copias quien se conecte) evita dejar credenciales de escritura en el equipo a proteger.

#### Ampliación

Programa el script con un temporizador de systemd (como el de la práctica 2.5) y limita la clave con `rrsync`. Prueba una restauración completa de la carpeta `ultima` en un directorio temporal.

---

## Práctica 2.5 · Ransomware: copias cifradas con restic y recuperación

{{< practica num="2.5" tipo="Reto" duracion="2 h" nivel="3" ra="RA1: a, g" entorno="Debian 13 · restic 0.18" entrega="informe con tiempos medidos y comparación con el RTO" >}}

#### Objetivo

Implantar copias **cifradas y deduplicadas** con `restic`, automatizarlas, simular un *ransomware* en el laboratorio, **detectarlo y recuperar** los datos midiendo el tiempo frente al RTO.

#### Contexto

`restic` guarda copias cifradas (el servidor de copias no ve el contenido), con deduplicación e historial. Ciclo: *amenaza* (*ransomware*) → *vulnerabilidad* (datos solo en el servidor) → *ataque* (cifrado masivo simulado) → *detección* (ficheros ilegibles, extensión nueva, nota de rescate) → *mitigación* (restauración desde `restic`) → *comprobación* (hashes y tiempo de recuperación frente al RTO). Se espera que diseñes el orden de la respuesta; las pistas están al final.

#### Requisitos previos

- Prácticas 2.2 a 2.4 hechas: `/srv/datos` con datos y `/root/hashes_datos.sha256`, SSH por clave hacia `srv-copias`.
- `restic` instalado en `srv-ficheros`. Instantánea previa de ambas máquinas.

#### Desarrollo

{{% steps %}}

1. **Prepara el repositorio** en `srv-copias`.

   ```bash
   sudo mkdir -p /backups/restic-srv-ficheros
   sudo chown copias: /backups/restic-srv-ficheros
   ```

2. **Inicializa el repositorio** desde `srv-ficheros`. La contraseña va en un fichero protegido, y la configuración SSH hace que `restic` use la clave de copias.

   ```bash
   sudo sh -c 'openssl rand -base64 32 > /root/.restic-pass && chmod 600 /root/.restic-pass'
   sudo tee -a /root/.ssh/config >/dev/null <<'EOT'
   Host srv-copias
       User copias
       IdentityFile /root/.ssh/id_backup
   EOT

   sudo -i     # el resto de la práctica como root
   export RESTIC_REPOSITORY="sftp:srv-copias:/backups/restic-srv-ficheros"
   export RESTIC_PASSWORD_FILE="/root/.restic-pass"
   restic init
   ```

   Esperado: `created restic repository ... at sftp:srv-copias:/backups/restic-srv-ficheros`.

   > [!IMPORTANT]
   > Guarda una copia de `/root/.restic-pass` fuera de la máquina (en un gestor de contraseñas). Sin ella el repositorio es irrecuperable.

3. **Primera copia y comprobación del cifrado.**

   ```bash
   restic backup /srv/datos /etc --tag manual
   restic snapshots
   restic stats --mode raw-data
   ```

   En `srv-copias`, el texto de los ficheros no debe aparecer:

   ```bash
   sudo ls /backups/restic-srv-ficheros/      # config  data  index  keys  locks  snapshots
   sudo grep -r "Contrato confidencial" /backups/restic-srv-ficheros/ || echo "No se encuentra el texto: los datos están cifrados"
   ```

4. **Deduplicación.** Duplica los datos y observa en `Added to the repository:` que apenas se añade espacio.

   ```bash
   cp -r /srv/datos/empresa /srv/datos/empresa_copia
   restic backup /srv/datos --tag manual
   ```

5. **Automatiza con systemd.** Crea el script `/usr/local/sbin/backup-restic.sh`, el servicio y el temporizador del [apartado 8.8 de la teoría](/ud02-seguridad-pasiva/ud02-teoria/) cambiando `srv-copias` y la ruta del repositorio por las de esta práctica, y programa el temporizador cada 15 minutos para poder observarlo:

   ```ini
   [Timer]
   OnCalendar=*:0/15
   Persistent=true
   ```

   ```bash
   systemd-analyze calendar "*:0/15"                       # valida la expresión
   systemctl daemon-reload
   systemctl enable --now backup-restic.timer
   systemctl list-timers backup-restic.timer
   systemctl start backup-restic.service
   journalctl -u backup-restic.service -n 20 --no-pager
   ```

   Esperado al final del diario: `snapshot ... saved` y `no errors were found`.

6. **Simula el *ransomware*.** Este script **cifra** los ficheros de `/srv/datos` con una clave aleatoria que **no se guarda**. Ejecútalo solo en `srv-ficheros` y tras comprobar que hay una copia válida (`restic snapshots`).

   > [!CAUTION]
   > Es una simulación didáctica solo sobre los datos de práctica de tu máquina virtual. No la ejecutes en ningún otro equipo ni la adaptes para actuar sobre datos reales: el objetivo es entrenar la **detección y la recuperación**.

   ```bash
   cat > /root/simula_ransomware.sh <<'EOT'
   #!/usr/bin/env bash
   # SIMULACIÓN DIDÁCTICA: cifra los ficheros de /srv/datos con una clave que se descarta
   set -euo pipefail
   CLAVE=$(openssl rand -hex 32)
   find /srv/datos -type f ! -name "*.cifrado" | while read -r f; do
     openssl enc -aes-256-cbc -pbkdf2 -salt -pass pass:"$CLAVE" -in "$f" -out "$f.cifrado" && rm -f "$f"
   done
   echo "Sus ficheros han sido cifrados. (Simulación de laboratorio)" > /srv/datos/LEEME_RESCATE.txt
   unset CLAVE
   EOT
   chmod 700 /root/simula_ransomware.sh
   date +%T > /root/hora_ataque.txt
   /root/simula_ransomware.sh
   ```

7. **Detección.** Identifica los indicadores del ataque.

   ```bash
   ls /srv/datos/empresa | head
   cat /srv/datos/LEEME_RESCATE.txt
   find /srv/datos -name "*.cifrado" | wc -l
   file /srv/datos/empresa/contrato.txt.cifrado    # «openssl enc'd data with salted password»
   ```

8. **Contención y recuperación.** Aísla, identifica la última copia anterior al ataque, restaura en una carpeta aparte, verifica y solo entonces sustituye.

   ```bash
   systemctl stop backup-restic.timer              # 1. no hacer copias de datos cifrados
   restic snapshots                                # 2. localiza la última copia ANTERIOR al ataque

   date +%T > /root/hora_inicio_restauracion.txt   # 3. restaura aparte y verifica
   restic restore <ID_SNAPSHOT> --target /tmp/restaura_restic --include /srv/datos
   cd /tmp/restaura_restic/srv/datos && sha256sum -c --quiet /root/hashes_datos.sha256 && echo "Copia verificada"

   rsync -a --delete /tmp/restaura_restic/srv/datos/ /srv/datos/   # 4. sustituye los datos cifrados
   date +%T > /root/hora_fin_restauracion.txt

   systemctl start backup-restic.timer             # 5. reactiva las copias
   ```

   Sustituye `<ID_SNAPSHOT>` por el identificador real que muestra `restic snapshots`.

{{% /steps %}}

**Análisis.** (1) ¿Cuánto tiempo ha pasado desde el ataque hasta la recuperación? ¿Cumpliría un RTO de 1 hora? (2) ¿Qué datos se han perdido y cómo se relaciona con el RPO? (3) Si el *ransomware* hubiera obtenido la contraseña de `copias@srv-copias`, ¿podría haber borrado el repositorio? Propón dos medidas. (4) Ejecuta `restic check` y `restic forget --keep-last 10 --prune --dry-run` y explica la salida.

{{% details title="Pista" %}}
Orden recomendado: (1) **aislar** (parar el temporizador y desconectar la red si procede), (2) **identificar** la última copia anterior al ataque, (3) **restaurar en una carpeta aparte** y verificar, (4) volver los datos a su sitio, (5) analizar la causa. Anota hora de inicio y fin para calcular el **RTO real**.
{{% /details %}}

{{% details title="Solución" %}}
1. RTO real = `hora_fin_restauracion` − `hora_ataque` (o − hora de detección); en el laboratorio será de pocos minutos, pero con 300 GB y enlace de 300 Mbit/s sería mucho mayor: comprueba si el RTO se cumple con datos reales.
2. Se pierde lo escrito entre la última copia buena y el ataque: es el RPO efectivo, igual a la frecuencia de las copias en el peor caso.
3. Sí: con acceso de escritura al repositorio, sí. Medidas: servidor REST de `restic` en modo `--append-only`, modelo *pull* iniciado desde `srv-copias`, o una copia adicional inmutable o desconectada.
4. `restic check` verifica la estructura del repositorio; `forget --dry-run --prune` muestra qué instantáneas se eliminarían sin borrar nada.
{{% /details %}}

#### Comprobación

- [ ] `restic snapshots` lista al menos una copia anterior al ataque, y `restic check` no da errores.
- [ ] `grep` en `srv-copias` no encuentra el texto en claro (datos cifrados).
- [ ] `systemctl list-timers` muestra el temporizador y el diario `no errors were found`.
- [ ] Tras el ataque se ven los `*.cifrado` y `LEEME_RESCATE.txt`.
- [ ] Tras restaurar, `sha256sum -c` indica «Copia verificada» y los `*.cifrado` han desaparecido.
- [ ] Has calculado el tiempo de recuperación y lo has comparado con el RTO.

#### Problemas habituales

| Problema | Causa | Solución |
|---|---|---|
| `restic: Fatal: unable to open config file` | `RESTIC_REPOSITORY` incorrecta o repositorio sin inicializar | Revisa la variable; `restic init` |
| `restic` pide contraseña de SSH | No encuentra la clave | Revisa `/root/.ssh/config` y prueba `ssh srv-copias` como `root` |
| El temporizador no se ejecuta | No habilitado o error en `OnCalendar` | `systemctl list-timers`; `systemd-analyze calendar "*:0/15"` |
| El temporizador copió datos ya cifrados | No se detuvo antes de recuperar | Usa una instantánea anterior (`restic snapshots`) |

#### Consideraciones de seguridad

La contraseña del repositorio es el único modo de leer las copias: guárdala fuera del servidor y protege el fichero con permisos `600`. El equipo origen **no debe poder borrar** el histórico: valora `--append-only`, modelo *pull* o copias inmutables (regla 3-2-1-**1**-0). Una copia no restaurada nunca está comprobada: restaura en una carpeta temporal con regularidad.

#### Ampliación

Sustituye `restic` por BorgBackup y compara tiempos y tamaño (teoría 8.4). Calcula el tiempo de restauración de 1 TB desde la nube con 300 Mbit/s y desde un NAS local con 1 Gbit/s, e indica qué implica para el RTO. Investiga qué es una copia **inmutable** (S3 Object Lock) y en qué se diferencia de una copia desconectada. Investiga cómo se hace una copia del estado del sistema en Windows Server con `wbadmin` y qué papel tiene VSS.

---

## Práctica 2.6 · Borrado seguro de soportes

{{< practica num="2.6" tipo="Guiada" duracion="1 h" nivel="1" ra="RA1: b, g" entorno="Debian 13 · shred · cryptsetup (LUKS2)" entrega="resultados de las tres pruebas y procedimiento de retirada" >}}

#### Objetivo

Comparar el **borrado normal**, la **sobrescritura** y el **borrado criptográfico**, y redactar un procedimiento de retirada de equipos.

#### Contexto

Al borrar un fichero con `rm` solo se libera el espacio; los datos permanecen en el soporte hasta que se sobrescriben. Un disco retirado o devuelto con datos recuperables es una fuga de información. Se trabaja con ficheros de imagen para no tocar discos reales.

#### Requisitos previos

- `srv-ficheros` con `cryptsetup` instalado. Tener presente que LUKS se estudia a fondo en la UD4.

#### Desarrollo

{{% steps %}}

1. **Crea un soporte de prueba**: un fichero de 50 MB con sistema de ficheros, montado en bucle (`loop`), con un dato «secreto».

   ```bash
   mkdir -p ~/ud02/borrado && cd ~/ud02/borrado
   truncate -s 50M soporte.img
   mkfs.ext4 -q soporte.img
   sudo mkdir -p /mnt/soporte
   sudo mount -o loop soporte.img /mnt/soporte
   echo "NUMERO-DE-CUENTA-SECRETO-ES00-1234" | sudo tee /mnt/soporte/secreto.txt
   sync
   ```

2. **Borrado normal.** El texto sigue en la imagen: `rm` solo ha liberado el espacio.

   ```bash
   sudo rm /mnt/soporte/secreto.txt
   sync
   sudo umount /mnt/soporte
   grep -a -c "NUMERO-DE-CUENTA-SECRETO" soporte.img     # cuenta apariciones del texto en la imagen
   strings soporte.img | grep "SECRETO"
   ```

3. **Borrado seguro por sobrescritura.** `shred -v -n 1 -z` sobrescribe una vez con datos aleatorios y una pasada final de ceros.

   ```bash
   shred -v -n 1 -z soporte.img
   grep -a -c "NUMERO-DE-CUENTA-SECRETO" soporte.img || echo "No quedan restos del dato"
   ```

4. **Borrado criptográfico.** Con LUKS2 los datos se guardan cifrados; destruir las ranuras de clave los hace irrecuperables.

   ```bash
   truncate -s 50M cifrado.img
   sudo cryptsetup luksFormat --batch-mode cifrado.img <<< "ClaveLab2026"
   sudo cryptsetup open cifrado.img vol_cifrado <<< "ClaveLab2026"
   sudo mkfs.ext4 -q /dev/mapper/vol_cifrado
   sudo mount /dev/mapper/vol_cifrado /mnt/soporte
   echo "NUMERO-DE-CUENTA-SECRETO-ES00-1234" | sudo tee /mnt/soporte/secreto.txt
   sudo umount /mnt/soporte && sudo cryptsetup close vol_cifrado

   grep -a -c "NUMERO-DE-CUENTA-SECRETO" cifrado.img || echo "En el disco cifrado no aparece en claro"

   sudo cryptsetup erase --batch-mode cifrado.img                      # destruye las ranuras de clave
   sudo cryptsetup open cifrado.img vol_cifrado <<< "ClaveLab2026"    # ya no es posible abrirlo
   ```

   - `cryptsetup luksFormat` prepara un volumen cifrado con LUKS2; `<<<` pasa la contraseña por la entrada estándar (solo válido en laboratorio).
   - `cryptsetup erase` destruye todas las ranuras de clave: sin ellas el contenido es irrecuperable aunque se conozca la contraseña.

{{% /steps %}}

**Análisis.** (1) ¿Por qué el texto seguía visible tras `rm`? (2) ¿Por qué `shred` sobre un fichero dentro de un SSD o de Btrfs no garantiza el borrado? (3) ¿Qué ventaja tiene cifrar un disco desde el principio de cara a su retirada? (4) Redacta un procedimiento de retirada de equipos (inventario, método por tipo de soporte, certificado, registro).

{{% details title="Pista" %}}
Compara los tres resultados: ¿qué datos se recuperaban tras el borrado normal? ¿Y tras `shred`? ¿Y tras destruir la clave? Piensa también en **SSD y en la nube**, donde sobrescribir no garantiza nada.
{{% /details %}}

{{% details title="Solución" %}}
1. `rm` elimina la entrada del directorio y marca los bloques como libres, pero no los sobrescribe.
2. En SSD (nivelación de desgaste) y en sistemas con copia en escritura la sobrescritura puede ir a otros bloques y dejar los originales intactos.
3. Basta destruir la clave para inutilizar el contenido, de forma rápida y válida también en SSD y en la nube.
4. Inventario del soporte → método según tipo (HDD: sobrescritura; SSD: *Sanitize*/*Secure Erase* o borrado criptográfico; destrucción física si no es posible) → verificación → certificado → registro firmado.
{{% /details %}}

#### Comprobación

- [ ] Tras `rm` el texto sigue apareciendo en la imagen.
- [ ] Tras `shred` el recuento de apariciones es 0.
- [ ] En `cifrado.img` el texto no aparece en claro y tras `cryptsetup erase` no se puede abrir.
- [ ] Has redactado el procedimiento de retirada.

#### Problemas habituales

| Problema | Causa | Solución |
|---|---|---|
| `mount: failed to setup loop device` | Falta el módulo o el dispositivo `loop` ocupado | `sudo losetup -f`; libera con `sudo losetup -D` |
| `cryptsetup open` dice que el nombre ya existe | El mapeo anterior sigue abierto | `sudo cryptsetup close vol_cifrado` |

#### Consideraciones de seguridad

Verifica el nombre del dispositivo antes de `shred` o `cryptsetup erase`: se aplican sobre ficheros de imagen aquí, pero sobre un disco real son irreversibles. Pasar la contraseña por `<<<` la deja en el historial de la consola: no lo hagas con claves reales. Para SSD usa el borrado del firmware o criptográfico y, si no es posible, destruye el soporte.

#### Ampliación

Investiga `nvme format` y `hdparm --security-erase` para un borrado real de SSD y qué certificado de borrado exige tu organización.

---

## Tarea del proyecto

{{< practica etiqueta="Tarea" num="2.7" tipo="Proyecto" duracion="1 h" nivel="3" ra="RA1: b; RA6: b, f, i" entorno="Debian 13" entrega="informe técnico con evidencias" >}}

#### Objetivo

Entregar el **plan de almacenamiento y copias** de [Mediterránea Dental](/guia/proyecto-clinica/) para `srv-ficheros`, con la restauración demostrada.

#### Contexto

El servidor de ficheros guarda los historiales clínicos (datos de salud, categoría especial del RGPD), citas y facturación. La dirección fija un **RPO de 4 horas y un RTO de 8 horas** para los ficheros clínicos, y de **1 hora / 4 horas** para la base de datos de gestión. La clínica no tiene copias verificadas y ha motivado el encargo el *ransomware* sufrido por otra clínica del sector.

#### Requisitos previos

Prácticas 2.1 a 2.6 realizadas en el laboratorio.

#### Desarrollo

{{% steps %}}

1. **Diseño**: esquema del almacenamiento con el nivel RAID justificado, SAI dimensionado y ubicación de las copias, con un diagrama de la solución.
2. **Política de copias**: qué se copia, cuándo, tipo, retención, cifrado, ubicaciones según 3-2-1-1-0, verificación y responsables, coherente con los RPO/RTO.
3. **Implantación en el laboratorio** con evidencias: RAID funcionando, fallo y reconstrucción, copias automáticas con `restic` y NUT configurado.
4. **Prueba de recuperación**: restauración tras el *ransomware* simulado, con tiempos medidos y comparación con el RTO.
5. **Procedimiento de retirada segura** de los discos antiguos.

{{% /steps %}}

#### Comprobación

- [ ] El informe contiene objetivo, esquema, procedimiento, evidencias reales, análisis, problemas y conclusiones.
- [ ] Otra persona podría reproducir la implantación con el informe.
- [ ] Hay una prueba de fallo y la comprobación de la recuperación con tiempos.

#### Problemas habituales

Entregar una política sin restauración probada, no relacionar la frecuencia de copia con el RPO, o no incluir la copia fuera de línea o inmutable.

#### Consideraciones de seguridad

Usa solo datos ficticios. Las copias de datos de salud deben ir **cifradas** y con acceso restringido; indica quién custodia la contraseña del repositorio.

#### Ampliación

Añade una copia en la nube con inmutabilidad y calcula el tiempo de restauración real frente al RTO.

#### Rúbrica

| Criterio | Peso |
|---|--:|
| Diseño justificado (RAID, SAI, ubicaciones) | 25 % |
| Política de copias coherente con RPO/RTO y 3-2-1-1-0 | 25 % |
| Implantación y evidencias técnicas | 30 % |
| Prueba de recuperación y análisis de tiempos | 15 % |
| Presentación y documentación | 5 % |
