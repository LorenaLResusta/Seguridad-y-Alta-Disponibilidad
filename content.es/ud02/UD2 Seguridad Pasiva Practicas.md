---
title: "Prácticas"
slug: "practicas"
weight: 2
---

# UD2. Prácticas: seguridad pasiva y almacenamiento

> RAID por software, instantáneas LVM, copias de seguridad completas, incrementales y deduplicadas, automatización, restauración tras un ataque de *ransomware* simulado, SAI simulado y borrado seguro.

| Datos de las prácticas | Información |
| --- | --- |
| Duración estimada | 7 horas |
| Entorno | VirtualBox 7.x · 2 VM Debian 13 o AlmaLinux 10 |
| Criterios de evaluación | RA1 a, b · RA6 a, b, f, i |

## 1. Objetivos

- Crear, supervisar y reparar un RAID 5 por software con disco de reserva.
- Usar instantáneas LVM para obtener copias coherentes.
- Realizar copias completas e incrementales con `tar` y copias con historial con `rsync`.
- Implantar un sistema de copias cifradas y deduplicadas con `restic` en un servidor remoto.
- Automatizar las copias con temporizadores de systemd y verificar su ejecución.
- Recuperar los datos tras un ataque de *ransomware* simulado y medir el tiempo de recuperación.
- Configurar el apagado automático de un servidor ante un fallo eléctrico con NUT.
- Comparar el borrado normal con el borrado seguro.

## 2. Normas

> [!CAUTION]
> Las prácticas de RAID y borrado seguro **destruyen** datos de los discos indicados. Hazlas solo en los discos virtuales creados para ello y comprueba siempre el nombre del dispositivo con `lsblk` antes de ejecutar una orden.

Crea una instantánea de cada VM antes de empezar cada práctica.

---

## 3. Práctica 0 - Preparación del entorno

### 3.1. Máquinas virtuales

| VM | Nombre de equipo | Red | Recursos | Discos | Función |
| --- | --- | --- | --- | --- | --- |
| Cliente / servidor de datos | `sad-cli` | `SAD-NAT` | 2 GB RAM, 2 CPU | Disco del sistema + **4 discos de 1 GB** | RAID, LVM, origen de las copias |
| Servidor de copias | `sad-backup` | `SAD-NAT` | 1 GB RAM, 1 CPU | Disco del sistema de 20 GB | Destino de las copias |

Puedes clonar la VM de la UD1 (**Clonar → Clonación enlazada**, generando nuevas direcciones MAC) para ahorrar tiempo.

### 3.2. Añadir los discos al cliente

Con la VM **apagada**: **Configuración → Almacenamiento → Controlador SATA → Añadir disco duro → Crear** cuatro discos VDI de 1 GB llamados `raid1.vdi` a `raid4.vdi`.

Desde la línea de órdenes del anfitrión:

```bash
for i in 1 2 3 4; do
  VBoxManage createmedium disk --filename "raid$i.vdi" --size 1024
  VBoxManage storageattach sad-cli --storagectl "SATA" --port $i --device 0 --type hdd --medium "raid$i.vdi"
done
```

> [!NOTE]
> El nombre del controlador puede ser «SATA» o «Controlador SATA» según el idioma de VirtualBox. Compruébalo con `VBoxManage showvminfo sad-cli | grep -i storage`.

### 3.3. Nombres y direcciones

Arranca ambas VM, anota sus direcciones con `ip -br a` y añádelas a `/etc/hosts` en las **dos** máquinas:

```bash
echo "192.168.100.10  sad-cli"    | sudo tee -a /etc/hosts
echo "192.168.100.20  sad-backup" | sudo tee -a /etc/hosts
getent hosts sad-backup            # comprueba la resolución
ping -c 3 sad-backup
```

> [!TIP]
> Para que las direcciones no cambien entre arranques, configura IP estáticas dentro de la red `192.168.100.0/24` (puerta de enlace `192.168.100.1`): en Debian en `/etc/network/interfaces`; en AlmaLinux con `nmcli connection modify`.

### 3.4. Paquetes necesarios

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
# En sad-cli
sudo apt install -y mdadm lvm2 rsync restic smartmontools nut
# En sad-backup
sudo apt install -y rsync openssh-server
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
# En sad-cli (restic y nut están en EPEL)
sudo dnf install -y epel-release
sudo dnf install -y mdadm lvm2 rsync restic smartmontools nut
# En sad-backup
sudo dnf install -y rsync openssh-server
```
{{% /tab %}}
{{< /tabs >}}

Al instalar `mdadm` en Debian puede aparecer una pregunta sobre el envío de correo: acepta los valores por defecto.

---

## 4. Práctica 1 - Identificar el almacenamiento

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL
```

Salida esperada:

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

Comprueba S.M.A.R.T. en un disco virtual:

```bash
sudo smartctl -i -H /dev/sdb
# SMART support is: Unavailable - device lacks SMART capability.
```

Como VirtualBox no emula S.M.A.R.T., repite la consulta en tu **equipo anfitrión**:

- **Linux**: `sudo smartctl -a /dev/sda` o `sudo nvme smart-log /dev/nvme0`.
- **Windows**: instala [smartmontools para Windows](https://www.smartmontools.org/wiki/Download) y ejecuta en una consola de administrador `smartctl --scan` y después `smartctl -a /dev/sda` (o el dispositivo que indique).

**Análisis**: anota modelo, horas de funcionamiento, temperatura y, según el tipo de disco, los atributos 5, 197 y 198 (HDD) o `percentage_used` y `media_errors` (NVMe). ¿Está sano el disco? ¿Qué atributo vigilarías?

---

## 5. Práctica 2 - RAID 5 con disco de reserva

**Ciclo**: *amenaza* (avería de un disco) → *vulnerabilidad* (los datos están en un único disco) → *incidente* (fallo simulado) → *detección* (`/proc/mdstat`, `mdadm --monitor`) → *mitigación* (RAID 5 + *hot spare*) → *comprobación* (los datos siguen accesibles y el RAID se reconstruye).

### 5.1. Crear el RAID

```bash
sudo mdadm --create /dev/md0 --level=5 --raid-devices=3 \
     /dev/sdb /dev/sdc /dev/sdd --spare-devices=1 /dev/sde
```

`mdadm` pide confirmación (`Continue creating array? y`). Sigue la sincronización inicial:

```bash
watch -n 1 cat /proc/mdstat      # Ctrl+C para salir
```

Cuando termine:

```bash
sudo mdadm --detail /dev/md0
```

Fíjate en estos campos:

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

    Number   Major   Minor   RaidDevice State
       0       8       16        0      active sync   /dev/sdb
       1       8       32        1      active sync   /dev/sdc
       4       8       48        2      active sync   /dev/sdd
       3       8       64        -      spare   /dev/sde
```

### 5.2. Sistema de ficheros y montaje permanente

```bash
sudo mkfs.ext4 -L DATOS /dev/md0
sudo mkdir -p /srv/datos
sudo mount /dev/md0 /srv/datos
df -h /srv/datos
```

Guarda la configuración y el montaje:

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf
sudo update-initramfs -u
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm.conf
sudo dracut -f
```
{{% /tab %}}
{{< /tabs >}}

```bash
# Copia de seguridad de fstab antes de modificarlo
sudo cp -a /etc/fstab /etc/fstab.bak

UUID=$(sudo blkid -s UUID -o value /dev/md0)
echo "UUID=$UUID  /srv/datos  ext4  defaults,nofail  0  2" | sudo tee -a /etc/fstab

# Verificar la sintaxis y probar el montaje sin reiniciar
sudo findmnt --verify
sudo umount /srv/datos && sudo mount -a && findmnt /srv/datos
```

> [!WARNING]
> Si `findmnt --verify` muestra errores, **no reinicies**: corrige `/etc/fstab` o restaura `/etc/fstab.bak`. Un `fstab` incorrecto puede dejar el sistema en modo de emergencia.

Reinicia y comprueba que el RAID se ensambla y se monta solo.

### 5.3. Datos de prueba con verificación de integridad

```bash
sudo mkdir -p /srv/datos/empresa
for i in $(seq 1 50); do
  head -c 200K /dev/urandom | sudo tee /srv/datos/empresa/documento_$i.bin >/dev/null
done
echo "Contrato confidencial" | sudo tee /srv/datos/empresa/contrato.txt
cd /srv/datos && sudo find empresa -type f -exec sha256sum {} + | sudo tee /root/hashes_datos.sha256 >/dev/null
```

### 5.4. Simular el fallo de un disco

```bash
sudo mdadm /dev/md0 --fail /dev/sdc
cat /proc/mdstat
```

Resultado esperado: `sdc` aparece con `(F)`, el estado es `[3/2] [U_U]` y `sde` empieza a reconstruirse (`recovery`).

```bash
sudo journalctl -k --since "-5min" | grep -i md
# md/raid:md0: Disk failure on sdc, disabling device.
# md: recovery of RAID array md0
```

Mientras se reconstruye, comprueba que los datos siguen accesibles **e íntegros**:

```bash
cd /srv/datos && sudo sha256sum -c --quiet /root/hashes_datos.sha256 && echo "Datos íntegros"
```

### 5.5. Sustituir el disco averiado

```bash
sudo mdadm /dev/md0 --remove /dev/sdc
sudo wipefs -a /dev/sdc                  # en la realidad sería un disco nuevo
sudo mdadm /dev/md0 --add /dev/sdc       # se añade como nueva reserva
sudo mdadm --detail /dev/md0 | grep -E "State|Devices|spare"
```

### 5.6. Fallo doble

1. Haz una instantánea de la VM.
2. Marca como fallidos **dos** discos activos seguidos, sin esperar a la reconstrucción.
3. ¿Qué ocurre con el RAID? ¿Y con los datos? Explica el resultado.
4. Restaura la instantánea.

### 5.7. Monitorización

```bash
# Prueba de alerta: genera un evento TestMessage por cada RAID
sudo mdadm --monitor --scan --oneshot --test
sudo journalctl --since "-2min" | grep -i mdadm
# Estado del servicio de vigilancia
systemctl status mdmonitor --no-pager
```

### 5.8. Preguntas

1. ¿Por qué la capacidad útil es de unos 2 GB con tres discos de 1 GB?
2. ¿Qué ventaja ha aportado el disco de reserva?
3. ¿Qué habría pasado sin él si fallase un segundo disco durante la sustitución?
4. Explica con un ejemplo por qué este RAID no sustituye a una copia de seguridad.

---

## 6. Práctica 3 - Instantáneas LVM para copias coherentes

Vamos a convertir el RAID en un volumen físico LVM para usar instantáneas.

> [!WARNING]
> Esta práctica **borra** el sistema de ficheros de `/dev/md0`. Haz antes una copia de los datos de prueba o repite la práctica 2.

```bash
sudo umount /srv/datos
sudo sed -i.bak '\#/srv/datos#d' /etc/fstab     # elimina la línea del montaje anterior (copia en fstab.bak)

sudo wipefs -a /dev/md0
sudo pvcreate /dev/md0
sudo vgcreate vg_datos /dev/md0
sudo lvcreate -L 1.2G -n lv_datos vg_datos      # deja espacio libre para instantáneas
sudo mkfs.ext4 /dev/vg_datos/lv_datos
sudo mount /dev/vg_datos/lv_datos /srv/datos
sudo vgs; sudo lvs
```

- `pvcreate` prepara el dispositivo como volumen físico.
- `vgcreate` crea un grupo de volúmenes con él.
- `lvcreate -L 1.2G` crea un volumen lógico de 1,2 GB; el resto del grupo queda libre.

Crea datos, haz una instantánea y modifica el original:

```bash
echo "versión 1" | sudo tee /srv/datos/informe.txt
sudo lvcreate --snapshot -L 200M -n snap_datos /dev/vg_datos/lv_datos
echo "versión 2 (modificada tras la instantánea)" | sudo tee /srv/datos/informe.txt

sudo mkdir -p /mnt/snap
sudo mount -o ro /dev/vg_datos/snap_datos /mnt/snap
cat /srv/datos/informe.txt     # versión 2
cat /mnt/snap/informe.txt      # versión 1: estado congelado

# Copia coherente desde la instantánea
sudo tar -czpf /root/datos_$(date +%F_%H%M).tar.gz -C /mnt/snap .
sudo lvs                       # observa el porcentaje de uso de la instantánea (Data%)

sudo umount /mnt/snap
sudo lvremove -y /dev/vg_datos/snap_datos
```

Para terminar:

1. Vuelve a añadir el montaje a `/etc/fstab` con el UUID del volumen lógico (`sudo blkid /dev/vg_datos/lv_datos`) y comprueba con `sudo findmnt --verify`.
2. Vuelve a generar los datos de prueba y su fichero de hashes ejecutando de nuevo los comandos del apartado 5.3: las prácticas siguientes los utilizan.

**Pregunta**: ¿qué ocurriría si durante la vida de la instantánea se modificasen más de 200 MB en el volumen original?

---

## 7. Práctica 4 - Copias completas e incrementales con `tar`

### 7.1. Preparación

```bash
sudo mkdir -p /backup/tar
sudo cp -r /etc/skel /srv/datos/proyecto 2>/dev/null; echo "inicio" | sudo tee /srv/datos/proyecto/notas.txt
```

### 7.2. Copia completa (nivel 0)

```bash
sudo tar --listed-incremental=/backup/tar/datos.snar \
         -czpf /backup/tar/datos_0_full.tar.gz -C /srv datos
```

### 7.3. Cambios y copias incrementales

```bash
# Lunes: se crea un fichero
echo "tarea lunes" | sudo tee /srv/datos/proyecto/lunes.txt
sudo tar --listed-incremental=/backup/tar/datos.snar -czpf /backup/tar/datos_1_inc.tar.gz -C /srv datos

# Martes: se modifica un fichero y se borra otro
echo "cambio martes" | sudo tee -a /srv/datos/proyecto/notas.txt
sudo rm /srv/datos/proyecto/lunes.txt
sudo tar --listed-incremental=/backup/tar/datos.snar -czpf /backup/tar/datos_2_inc.tar.gz -C /srv datos

ls -lh /backup/tar/
```

Compara los tamaños: la completa es mucho mayor que las incrementales.

```bash
tar -tzvf /backup/tar/datos_1_inc.tar.gz | grep -v '/$'    # solo ficheros nuevos o modificados
```

### 7.4. Restauración de la cadena

```bash
sudo mkdir -p /tmp/restaura_tar
for f in /backup/tar/datos_0_full.tar.gz /backup/tar/datos_1_inc.tar.gz /backup/tar/datos_2_inc.tar.gz; do
  sudo tar --listed-incremental=/dev/null -xzpf "$f" -C /tmp/restaura_tar
done
ls /tmp/restaura_tar/datos/proyecto/
cat /tmp/restaura_tar/datos/proyecto/notas.txt
```

**Comprobaciones**:

- `notas.txt` contiene el cambio del martes.
- `lunes.txt` **no** aparece: `tar` registra también los borrados y la restauración reproduce el estado del martes.
- Si quisieras recuperar `lunes.txt`, ¿qué copias restaurarías?

---

## 8. Práctica 5 - Copias remotas con historial usando `rsync`

### 8.1. Usuario de copias y autenticación por clave

En **sad-backup**:

```bash
sudo useradd -m -s /bin/bash copias
sudo mkdir -p /backups/sad-cli
sudo chown copias: /backups/sad-cli
sudo chmod 700 /backups/sad-cli
```

En **sad-cli**, como `root` (las copias se harán con privilegios para leer todos los ficheros):

```bash
sudo ssh-keygen -t ed25519 -f /root/.ssh/id_backup -N "" -C "backup@sad-cli"
sudo ssh-copy-id -i /root/.ssh/id_backup.pub copias@sad-backup   # pide la contraseña de «copias»
sudo ssh -i /root/.ssh/id_backup copias@sad-backup hostname      # debe responder sin contraseña
```

- `ssh-keygen -t ed25519` genera un par de claves de tipo Ed25519 (UD3). `-N ""` sin frase de paso, porque la usará un proceso automático.
- `ssh-copy-id` añade la clave pública al fichero `~/.ssh/authorized_keys` del usuario remoto.

> [!NOTE]
> Para limitar el daño si alguien roba esta clave, en un entorno real se restringe en `authorized_keys` con opciones como `restrict,from="192.168.100.10"` y, si es posible, con `rrsync` para que solo pueda ejecutar `rsync` sobre un directorio.

### 8.2. Copias diarias con enlaces duros

Script `/usr/local/sbin/backup-rsync.sh` en **sad-cli**:

```bash
#!/usr/bin/env bash
# Copia diaria con historial mediante rsync --link-dest
set -euo pipefail
ORIGEN="/srv/datos/"
DESTINO="copias@sad-backup:/backups/sad-cli"
SSH="ssh -i /root/.ssh/id_backup"
FECHA=$(date +%F_%H%M)

rsync -aAXH --delete -e "$SSH" \
      --link-dest=../ultima \
      "$ORIGEN" "$DESTINO/$FECHA/"

# Actualizar el enlace «ultima» en el servidor remoto
$SSH copias@sad-backup "ln -sfn $FECHA /backups/sad-cli/ultima"
logger -t backup-rsync "Copia $FECHA completada"
```

```bash
sudo install -m 750 backup-rsync.sh /usr/local/sbin/
sudo /usr/local/sbin/backup-rsync.sh
# Modifica algún fichero en /srv/datos y espera 1 minuto
sudo /usr/local/sbin/backup-rsync.sh
```

En **sad-backup** comprueba que hay dos copias que parecen completas, pero que comparten los ficheros no modificados:

```bash
ls -l /backups/sad-cli/
du -sh /backups/sad-cli/*                    # la segunda copia ocupa muy poco
ls -li /backups/sad-cli/*/empresa/documento_1.bin   # mismo número de inodo = mismo fichero
```

### 8.3. Restaurar un fichero borrado

```bash
# En sad-cli: borrado accidental
sudo rm /srv/datos/empresa/contrato.txt

# Restaurar desde la última copia
sudo rsync -av -e "ssh -i /root/.ssh/id_backup" \
     copias@sad-backup:/backups/sad-cli/ultima/empresa/contrato.txt /srv/datos/empresa/
cat /srv/datos/empresa/contrato.txt
```

---

## 9. Práctica 6 - Copias cifradas con `restic` y recuperación ante *ransomware*

**Ciclo**: *amenaza* (*ransomware*) → *vulnerabilidad* (los datos solo están en el servidor) → *ataque* (cifrado masivo simulado) → *detección* (ficheros ilegibles, extensión nueva, nota de rescate) → *mitigación* (restauración desde restic) → *comprobación* (hashes y tiempo de recuperación frente al RTO).

### 9.1. Inicializar el repositorio

En **sad-backup**:

```bash
sudo mkdir -p /backups/restic-sad-cli
sudo chown copias: /backups/restic-sad-cli
```

En **sad-cli**:

```bash
# Contraseña del repositorio en un fichero protegido
sudo sh -c 'openssl rand -base64 32 > /root/.restic-pass && chmod 600 /root/.restic-pass'

# Configuración SSH para que restic use la clave de copias
sudo tee -a /root/.ssh/config >/dev/null <<'EOF'
Host sad-backup
    User copias
    IdentityFile /root/.ssh/id_backup
EOF

sudo -i     # el resto de la práctica como root
export RESTIC_REPOSITORY="sftp:sad-backup:/backups/restic-sad-cli"
export RESTIC_PASSWORD_FILE="/root/.restic-pass"
restic init
```

Resultado esperado:

```text
created restic repository 7c2a1f0e3d at sftp:sad-backup:/backups/restic-sad-cli
Please note that knowledge of your password is required to access the repository.
Losing your password means that your data is irrecoverably lost.
```

> [!IMPORTANT]
> Guarda una copia de `/root/.restic-pass` fuera de la VM (en tu gestor de contraseñas). Sin ella el repositorio es irrecuperable.

### 9.2. Primera copia y comprobación del cifrado

```bash
restic backup /srv/datos /etc --tag manual
restic snapshots
restic stats --mode raw-data
```

En **sad-backup**, comprueba que los datos están cifrados:

```bash
sudo ls /backups/restic-sad-cli/
# config  data  index  keys  locks  snapshots
sudo grep -r "Contrato confidencial" /backups/restic-sad-cli/ || echo "No se encuentra el texto: los datos están cifrados"
```

### 9.3. Deduplicación

```bash
# Duplicamos 10 MB de datos ya existentes
cp -r /srv/datos/empresa /srv/datos/empresa_copia
restic backup /srv/datos --tag manual
```

Observa en la salida `Added to the repository:`: apenas se añade espacio, porque los fragmentos ya estaban en el repositorio.

### 9.4. Automatizar con systemd

Crea el script, el servicio y el temporizador de la teoría (apartado 9.4) adaptando las rutas. Para la práctica, programa el temporizador cada 15 minutos:

```ini
[Timer]
OnCalendar=*:0/15
Persistent=true
```

```bash
systemctl daemon-reload
systemctl enable --now backup-restic.timer
systemctl list-timers backup-restic.timer
systemctl start backup-restic.service
journalctl -u backup-restic.service -n 20 --no-pager
```

Resultado esperado al final del diario: `snapshot ... saved` y `no errors were found`.

### 9.5. Simular un ataque de *ransomware*

> [!CAUTION]
> Este script **cifra** los ficheros de `/srv/datos` con una clave aleatoria que **no se guarda**. Es una simulación didáctica para el laboratorio: ejecútala solo en `sad-cli` y después de comprobar que tienes una copia válida (`restic snapshots`).

```bash
cat > /root/simula_ransomware.sh <<'EOF'
#!/usr/bin/env bash
# SIMULACIÓN DIDÁCTICA: cifra los ficheros de /srv/datos con una clave que se descarta
set -euo pipefail
CLAVE=$(openssl rand -hex 32)
find /srv/datos -type f ! -name "*.cifrado" | while read -r f; do
  openssl enc -aes-256-cbc -pbkdf2 -salt -pass pass:"$CLAVE" -in "$f" -out "$f.cifrado" && rm -f "$f"
done
echo "Sus ficheros han sido cifrados. (Simulación de laboratorio)" > /srv/datos/LEEME_RESCATE.txt
unset CLAVE
EOF
chmod 700 /root/simula_ransomware.sh
date +%T > /root/hora_ataque.txt
/root/simula_ransomware.sh
```

### 9.6. Detección

```bash
ls /srv/datos/empresa | head
cat /srv/datos/LEEME_RESCATE.txt
find /srv/datos -name "*.cifrado" | wc -l
file /srv/datos/empresa/contrato.txt.cifrado    # «openssl enc'd data with salted password»
```

### 9.7. Contención y recuperación

```bash
# 1. Detener el temporizador para no hacer copias de los datos cifrados
systemctl stop backup-restic.timer

# 2. Identificar la última copia ANTERIOR al ataque
restic snapshots

# 3. Restaurar en un directorio temporal y verificar antes de sustituir
date +%T > /root/hora_inicio_restauracion.txt
restic restore <ID_SNAPSHOT> --target /tmp/restaura_restic --include /srv/datos
cd /tmp/restaura_restic/srv/datos && sha256sum -c --quiet /root/hashes_datos.sha256 && echo "Copia verificada"

# 4. Sustituir los datos cifrados por los restaurados
rsync -a --delete /tmp/restaura_restic/srv/datos/ /srv/datos/
date +%T > /root/hora_fin_restauracion.txt

# 5. Reactivar las copias
systemctl start backup-restic.timer
```

### 9.8. Análisis

1. ¿Cuánto tiempo ha pasado desde el ataque hasta la recuperación? ¿Cumpliría un RTO de 1 hora?
2. ¿Qué datos se han perdido? Relaciónalo con el RPO (frecuencia de las copias).
3. Si el *ransomware* hubiera obtenido la contraseña de `copias@sad-backup`, ¿podría haber borrado el repositorio? Propón dos medidas para evitarlo (por ejemplo: servidor REST de restic en modo `--append-only`, modelo *pull*, copia adicional inmutable).
4. Ejecuta `restic check` y `restic forget --keep-last 10 --prune --dry-run` y explica la salida.

---

## 10. Práctica 7 - SAI simulado y apagado ordenado con NUT

**Objetivo**: comprobar que un servidor se apaga de forma ordenada cuando el SAI informa de batería baja, sin necesidad de un SAI real.

El driver `dummy-ups` lee el estado del «SAI» de un fichero de texto, de modo que podemos simular un corte eléctrico editando ese fichero.

### 10.1. Configuración

Los ficheros están en `/etc/nut/` (Debian) o `/etc/ups/` (AlmaLinux). En el ejemplo se usa la ruta de Debian; ajústala si es necesario.

```bash
cd /etc/nut
sudo cp -a /etc/nut /etc/nut.bak       # copia de seguridad de la configuración

# Modo de funcionamiento
sudo sed -i 's/^MODE=.*/MODE=standalone/' nut.conf

# Estado inicial del SAI simulado: en línea y batería llena
sudo tee dummy.dev >/dev/null <<'EOF'
ups.status: OL
battery.charge: 100
battery.runtime: 1800
ups.load: 35
input.voltage: 230
EOF

# Definición del SAI
sudo tee -a ups.conf >/dev/null <<'EOF'

[saisim]
    driver = dummy-ups
    port = dummy.dev
    desc = "SAI simulado para el laboratorio"
EOF

# Usuario para upsmon
sudo tee -a upsd.users >/dev/null <<'EOF'

[monuser]
    password = LabNut2026
    upsmon primary
EOF

# Vigilancia. En lugar de apagar de verdad, registramos el evento (para poder repetir la prueba)
sudo tee -a upsmon.conf >/dev/null <<'EOF'

MONITOR saisim@localhost 1 monuser LabNut2026 primary
SHUTDOWNCMD "/usr/bin/logger -t NUT 'APAGADO ORDENADO: aquí se ejecutaría /sbin/shutdown -h +0'"
NOTIFYFLAG ONBATT SYSLOG+WALL
NOTIFYFLAG LOWBATT SYSLOG+WALL
NOTIFYFLAG ONLINE SYSLOG+WALL
EOF

sudo chown root:nut /etc/nut/*.conf /etc/nut/upsd.users /etc/nut/dummy.dev 2>/dev/null
sudo chmod 640 /etc/nut/upsd.users /etc/nut/upsmon.conf
```

Arranca los servicios:

```bash
sudo systemctl restart nut-driver-enumerator.service 2>/dev/null; sudo upsdrvctl start 2>/dev/null
sudo systemctl enable --now nut-server nut-monitor
upsc saisim@localhost ups.status
# OL
```

> [!NOTE]
> Los nombres de los servicios pueden variar según la versión: `nut-server` (upsd), `nut-monitor` (upsmon) y `nut-driver@saisim` o `nut-driver.target`. Usa `systemctl list-units 'nut*'` para verlos.

### 10.2. Simular el corte eléctrico

En una terminal, sigue el registro:

```bash
sudo journalctl -f -t upsmon -t NUT
```

En otra terminal, simula el paso a batería y, después, la batería baja:

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

Restaura el estado `OL` y reinicia `nut-monitor`.

### 10.3. Preguntas

1. ¿Qué significan los estados `OL`, `OB` y `LB`?
2. ¿Por qué no se apaga el servidor en cuanto el SAI pasa a batería?
3. ¿Cómo se apagarían otros servidores conectados al mismo SAI? (Pista: `upsmon` en modo `secondary` en esos equipos, conectando al `upsd` de este por el puerto 3493).
4. ¿Qué cambiarías en `SHUTDOWNCMD` para un servidor real?

---

## 11. Práctica 8 - Borrado normal frente a borrado seguro

Trabajaremos sobre un **fichero de imagen** para no tocar discos reales.

```bash
mkdir -p ~/ud02/borrado && cd ~/ud02/borrado
truncate -s 50M soporte.img
mkfs.ext4 -q soporte.img
sudo mkdir -p /mnt/soporte
sudo mount -o loop soporte.img /mnt/soporte
echo "NUMERO-DE-CUENTA-SECRETO-ES00-1234" | sudo tee /mnt/soporte/secreto.txt
sync
```

### 11.1. Borrado normal

```bash
sudo rm /mnt/soporte/secreto.txt
sync
sudo umount /mnt/soporte
grep -a -c "NUMERO-DE-CUENTA-SECRETO" soporte.img    # cuenta apariciones del texto en la imagen
strings soporte.img | grep "SECRETO"
```

El texto **sigue en la imagen**: `rm` solo ha liberado el espacio.

### 11.2. Borrado seguro del soporte completo

```bash
# Sobrescribir el soporte completo (aquí, el fichero de imagen) con datos aleatorios y luego ceros
shred -v -n 1 -z soporte.img
grep -a -c "NUMERO-DE-CUENTA-SECRETO" soporte.img || echo "No quedan restos del dato"
```

### 11.3. Borrado criptográfico

```bash
truncate -s 50M cifrado.img
sudo cryptsetup luksFormat --batch-mode cifrado.img <<< "ClaveLab2026"
sudo cryptsetup open cifrado.img vol_cifrado <<< "ClaveLab2026"
sudo mkfs.ext4 -q /dev/mapper/vol_cifrado
sudo mount /dev/mapper/vol_cifrado /mnt/soporte
echo "NUMERO-DE-CUENTA-SECRETO-ES00-1234" | sudo tee /mnt/soporte/secreto.txt
sudo umount /mnt/soporte && sudo cryptsetup close vol_cifrado

grep -a -c "NUMERO-DE-CUENTA-SECRETO" cifrado.img || echo "En el disco cifrado no aparece en claro"

# Borrado criptográfico: se destruyen las ranuras de clave
sudo cryptsetup erase --batch-mode cifrado.img
sudo cryptsetup open cifrado.img vol_cifrado <<< "ClaveLab2026"   # ya no es posible abrirlo
```

- `cryptsetup luksFormat` prepara un volumen cifrado con LUKS2 (se estudia en la UD4). `<<<` pasa la contraseña por la entrada estándar.
- `cryptsetup erase` destruye todas las ranuras de clave: sin ellas, el contenido es irrecuperable aunque se conozca la contraseña.

### 11.4. Preguntas

1. ¿Por qué el texto seguía visible tras `rm`?
2. ¿Por qué `shred` sobre un fichero dentro de un SSD o de un sistema de ficheros Btrfs no garantiza el borrado?
3. ¿Qué ventaja tiene cifrar un disco desde el principio de cara a su retirada?
4. Redacta un procedimiento de retirada de equipos para una empresa (inventario, método por tipo de soporte, certificado, registro).

---

## 12. Problemas habituales

| Problema | Causa | Solución |
| --- | --- | --- |
| `mdadm: cannot open /dev/sdb: Device or resource busy` | El disco tiene particiones o pertenece a otro RAID | `sudo wipefs -a /dev/sdb`; `sudo mdadm --stop /dev/md127` si se ensambló un RAID antiguo |
| Tras reiniciar el RAID aparece como `/dev/md127` | No se guardó `mdadm.conf` o no se regeneró el initramfs | Guardar la configuración y ejecutar `update-initramfs -u` o `dracut -f` |
| El sistema arranca en modo de emergencia | Error en `/etc/fstab` | Desde la consola de emergencia, corregir `fstab` o restaurar `fstab.bak`; usar `nofail` |
| `restic: Fatal: unable to open config file` | Variable `RESTIC_REPOSITORY` incorrecta o repositorio no inicializado | Revisar la variable; `restic init` |
| `restic` pide contraseña de SSH | No encuentra la clave | Revisar `/root/.ssh/config` y probar `ssh sad-backup` como root |
| El temporizador no se ejecuta | No está habilitado o hay un error en `OnCalendar` | `systemctl list-timers`; `systemd-analyze calendar "*:0/15"` |
| `upsc: Error: Driver not connected` | El driver `dummy-ups` no está arrancado o no encuentra `dummy.dev` | `sudo upsdrvctl -D start`; revisar permisos y ruta del fichero |
| `rsync` borra datos del destino inesperadamente | Barra final o `--delete` mal usados | Usar siempre `--dry-run` antes |

## 13. Actividades

1. Compara en una tabla RAID 1, RAID 5, RAID 6 y RAID 10 para un servidor de base de datos con 6 discos de 2 TB. Recomienda uno y justifícalo.
2. Diseña la política de copias de una clínica veterinaria (datos, frecuencia, tipo, retención, ubicaciones, cifrado, verificación, responsables). Aplica la regla 3-2-1-1-0.
3. Calcula el tiempo de restauración de 1 TB desde la nube con 300 Mbit/s y desde un NAS local con 1 Gbit/s. ¿Qué implica para el RTO?
4. Investiga qué es una copia **inmutable** en un servicio de almacenamiento de objetos (S3 Object Lock) y en qué se diferencia de una copia desconectada.
5. Investiga cómo se hace una copia de seguridad del estado del sistema en Windows Server con `wbadmin` y qué papel tiene VSS.

## 14. Autoevaluación

{{% details "1. ¿Qué diferencia hay entre una copia incremental y una diferencial?" %}}
La incremental copia lo cambiado desde la última copia de cualquier tipo; la diferencial, lo cambiado desde la última completa. La incremental ocupa menos pero restaurar requiere toda la cadena; la diferencial solo requiere la completa y la última diferencial.
{{% /details %}}

{{% details "2. ¿Cuántos discos puede perder un RAID 6?" %}}
Dos discos cualesquiera.
{{% /details %}}

{{% details "3. ¿Qué indica [U_U] en /proc/mdstat?" %}}
Que el RAID tiene tres posiciones y la segunda está ausente o fallida: el RAID funciona en modo degradado.
{{% /details %}}

{{% details "4. ¿Qué determina el RPO?" %}}
La cantidad máxima de datos (expresada en tiempo) que se puede perder; por tanto, la frecuencia mínima de las copias.
{{% /details %}}

{{% details "5. ¿Qué significa el último «0» de la regla 3-2-1-1-0?" %}}
Cero errores en la verificación de las copias: hay que comprobar que se pueden restaurar.
{{% /details %}}

{{% details "6. ¿Por qué una instantánea LVM no es una copia de seguridad?" %}}
Porque se almacena en el mismo grupo de volúmenes y discos que el original; si se pierden los discos, se pierden ambos.
{{% /details %}}

{{% details "7. ¿Qué tipo de SAI ofrece conmutación de 0 ms?" %}}
El SAI *on-line* de doble conversión.
{{% /details %}}

{{% details "8. ¿Cuál es el método recomendado para borrar un SSD?" %}}
Los comandos de borrado del propio firmware (*Sanitize* / *Secure Erase*) o el borrado criptográfico si el disco estaba cifrado; si no son posibles, la destrucción física.
{{% /details %}}

## 15. Tarea evaluable - Plan de almacenamiento, copias y recuperación

Diseña e implanta la solución para el siguiente supuesto:

> **Asesoría Levante S.L.** (15 empleados) tiene un servidor Linux con los expedientes de clientes (300 GB, crecimiento de 5 GB/mes) y una base de datos de facturación. La dirección establece un RPO de 4 horas y un RTO de 8 horas para los expedientes y de 1 hora / 4 horas para la facturación. El año pasado sufrió un corte de luz que corrompió el sistema de ficheros.

Entrega:

1. **Diseño** (RA6 a, b, i): esquema del almacenamiento (nivel RAID justificado), SAI dimensionado, ubicación de las copias y diagrama de la solución.
2. **Política de copias** completa (RA1 a): qué, cuándo, tipo, retención GFS, cifrado, ubicaciones según 3-2-1-1-0, verificación y responsables.
3. **Implantación en el laboratorio** (RA6 f) con evidencias: RAID funcionando, fallo y reconstrucción, copias automáticas con restic, NUT configurado.
4. **Prueba de recuperación**: restauración tras el *ransomware* simulado, con tiempos medidos y comparación con el RTO.
5. **Procedimiento de retirada segura** de los discos antiguos.

| Criterio | Peso |
| --- | :-: |
| Diseño justificado (RAID, SAI, ubicaciones) | 25 % |
| Política de copias coherente con RPO/RTO y 3-2-1-1-0 | 25 % |
| Implantación y evidencias técnicas | 30 % |
| Prueba de recuperación y análisis de tiempos | 15 % |
| Presentación y documentación | 5 % |

## 16. Recursos

- [mdadm (página de manual)](https://man7.org/linux/man-pages/man8/mdadm.8.html)
- [Debian Wiki: SoftwareRAID](https://wiki.debian.org/SoftwareRAID)
- [Red Hat: Managing RAID](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/managing_storage_devices/managing-raid_managing-storage-devices)
- [LVM: lvmthin y snapshots (página de manual)](https://man7.org/linux/man-pages/man7/lvmthin.7.html)
- [restic: documentación](https://restic.readthedocs.io/)
- [NUT: dummy-ups](https://networkupstools.org/docs/man/dummy-ups.html)
- [smartmontools](https://www.smartmontools.org/)
