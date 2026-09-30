---
title: "2. Seguridad pasiva. Prácticas"
weight: 1
---

# UD2 - Prácticas: seguridad pasiva y almacenamiento

> Monitorización, redundancia, copias de seguridad, recuperación y borrado seguro en un entorno de pruebas Linux.

| Datos de las prácticas | Información |
| --- | --- |
| Módulo | Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR |
| Modalidad | Semipresencial |
| Duración estimada | 10 horas |
| Entorno | VirtualBox y una distribución Linux compatible |

## 1. Objetivos

Al finalizar este itinerario, el alumnado será capaz de:

- Identificar unidades de almacenamiento y consultar su estado.
- Crear y administrar un RAID 5 por software con `mdadm`.
- Simular un fallo controlado y reconstruir un RAID.
- Realizar una copia de seguridad remota con `rsync` y restaurar archivos.
- Diferenciar el borrado normal del borrado seguro y aplicarlo únicamente sobre datos de prueba.
- Documentar las evidencias y proponer una estrategia básica de protección de datos.

## 2. Alcance y normas 

Estas prácticas se realizan únicamente en máquinas virtuales propias. No ejecutes comandos de borrado, formateo, RAID ni recuperación en el equipo personal, en un disco físico o en sistemas ajenos. Antes de cada práctica, crea una snapshot de la máquina virtual para poder regresar a un estado conocido.

El itinerario omite la configuración de SAN, iSCSI, RAID en Windows, TrueNAS, Clonezilla por red y recuperación forense de archivos borrados. Son actividades útiles, pero requieren más máquinas, recursos o configuraciones específicas. Aquí se priorizan procedimientos que se pueden repetir y verificar con dos máquinas virtuales Linux.

## 3. Preparación común

### 3.1. Máquinas virtuales necesarias

Se necesitan dos máquinas Linux actualizadas:

| Máquina | Nombre de equipo | Función |
| --- | --- | --- |
| Cliente | `cliente-apellido` | Contiene los datos de trabajo y el RAID. |
| Servidor | `servidor-apellido` | Recibe las copias de seguridad mediante SSH. |

Puedes partir de la máquina Linux preparada en UD1 y clonarla desde VirtualBox. AlmaLinux es la opción recomendada para seguir los comandos principales de esta guía, pero también se pueden utilizar Debian, Ubuntu Server, Rocky Linux o Fedora. Al clonar, genera una nueva dirección MAC para evitar conflictos de red.

### 3.2. Red y nombres

1. Configura ambas máquinas con el adaptador de red en **NAT** para instalar paquetes.
2. Arranca cada máquina y cambia su nombre. Sustituye `apellido` por tu primer apellido sin espacios:

```bash
sudo hostnamectl set-hostname cliente-apellido
```

En la otra máquina:

```bash
sudo hostnamectl set-hostname servidor-apellido
```

3. Reinicia o abre una nueva sesión y verifica el nombre:

```bash
hostnamectl
```

4. Actualiza ambas máquinas:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf update -y

# Debian o Ubuntu
sudo apt update && sudo apt upgrade -y
```

5. Crea una snapshot de cada máquina con el nombre `ud2-inicio`.

### 3.3. Discos virtuales del cliente

1. Apaga la máquina `cliente-apellido`.
2. En VirtualBox, abre **Configuración > Almacenamiento**.
3. Añade tres discos virtuales nuevos de 4 GB cada uno. Nómbralos `raid-a`, `raid-b` y `raid-c`.
4. Añade un cuarto disco virtual de 4 GB llamado `raid-repuesto`, pero no lo uses todavía.
5. Inicia la máquina cliente y comprueba los discos:

```bash
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS
```

Anota los nombres asignados a los cuatro discos nuevos. En los ejemplos se utilizarán `/dev/sdb`, `/dev/sdc`, `/dev/sdd` y `/dev/sde`, pero debes sustituirlos por los que aparezcan en tu sistema.

## 4. Práctica 1 - Inventario y estado SMART

### 4.1. Identificar las unidades

1. Instala las herramientas de monitorización:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf install smartmontools -y

# Debian o Ubuntu
sudo apt install smartmontools -y
```

2. Muestra el inventario de unidades:

```bash
lsblk -o NAME,MODEL,SIZE,TYPE,TRAN
```

3. Consulta el estado SMART de la unidad del sistema. Sustituye `/dev/sda` si tu disco principal tiene otro nombre:

```bash
sudo smartctl -H /dev/sda
```

4. Intenta obtener el informe detallado:

```bash
sudo smartctl -a /dev/sda
```

En muchas máquinas virtuales, VirtualBox no expone los atributos SMART del disco virtual. Si aparece un mensaje de que SMART no está disponible, incluye la salida como evidencia y explica la limitación: el sistema invitado ve un disco virtual, no el hardware físico real.

### 4.2. Analizar el resultado

1. Indica modelo, tamaño y tipo de conexión que muestra `lsblk`.
2. Explica qué significan, a nivel general, los atributos de sectores reasignados, sectores pendientes y errores no corregibles.
3. Justifica por qué una alerta SMART debe provocar una copia de seguridad y revisión de la unidad, pero no sustituye RAID ni copias de seguridad.

## 5. Práctica 2 - Creación y comprobación de RAID 5

### 5.1. Instalar y verificar `mdadm`

1. Instala la herramienta de RAID por software:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf install mdadm -y

# Debian o Ubuntu
sudo apt install mdadm -y
```

2. Comprueba de nuevo los discos y confirma que los tres discos de RAID no contienen datos importantes:

```bash
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS
```

3. Limpia exclusivamente las firmas de los tres discos virtuales que vas a utilizar. No ejecutes estos comandos sobre el disco del sistema:

```bash
sudo wipefs -a /dev/sdb
sudo wipefs -a /dev/sdc
sudo wipefs -a /dev/sdd
```

### 5.2. Crear el volumen RAID

1. Crea un RAID 5 con los tres discos de datos:

```bash
sudo mdadm --create --verbose /dev/md0 --level=5 --raid-devices=3 /dev/sdb /dev/sdc /dev/sdd
```

2. Confirma la creación cuando `mdadm` la solicite.
3. Consulta el progreso de sincronización. Pulsa `Ctrl+C` al terminar la comprobación:

```bash
watch -n 1 cat /proc/mdstat
```

4. Revisa los detalles del conjunto:

```bash
sudo mdadm --detail /dev/md0
```

### 5.3. Formatear y montar el RAID

1. Cuando la sincronización haya terminado, crea un sistema de archivos ext4:

```bash
sudo mkfs.ext4 /dev/md0
```

2. Crea el punto de montaje y monta el volumen:

```bash
sudo mkdir -p /mnt/raid5
sudo mount /dev/md0 /mnt/raid5
```

3. Comprueba capacidad y montaje:

```bash
df -h /mnt/raid5
```

4. Crea datos de prueba y verifica que se han guardado:

```bash
echo "Prueba RAID 5 - $(date)" | sudo tee /mnt/raid5/prueba-raid.txt
sudo cat /mnt/raid5/prueba-raid.txt
```

### 5.4. Simular un fallo y reconstruir

Esta simulación marca como fallido un disco virtual del conjunto, pero no borra datos. Aun así, verifica que utilizas el disco correcto.

1. Marca `/dev/sdb` como fallido y elimínalo del conjunto:

```bash
sudo mdadm /dev/md0 --fail /dev/sdb
sudo mdadm /dev/md0 --remove /dev/sdb
```

2. Consulta el estado degradado:

```bash
cat /proc/mdstat
sudo mdadm --detail /dev/md0
```

3. Comprueba que el archivo sigue disponible:

```bash
sudo cat /mnt/raid5/prueba-raid.txt
```

4. Añade el disco de repuesto, suponiendo que sea `/dev/sde`:

```bash
sudo wipefs -a /dev/sde
sudo mdadm /dev/md0 --add /dev/sde
```

5. Observa la reconstrucción:

```bash
watch -n 1 cat /proc/mdstat
```

6. Cuando termine, comprueba que el conjunto está activo y que el archivo continúa accesible:

```bash
sudo mdadm --detail /dev/md0
sudo cat /mnt/raid5/prueba-raid.txt
```

7. Explica qué habría ocurrido si hubiese fallado un segundo disco antes de completar la reconstrucción.

## 6. Práctica 3 - Copia remota y recuperación con `rsync`

### 6.1. Preparar el servidor de copias

En `servidor-apellido`:

1. Instala y activa el servidor SSH:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf install openssh-server rsync -y

# Debian o Ubuntu
sudo apt install openssh-server rsync -y
sudo systemctl enable --now sshd
```

2. Consulta la dirección IP:

```bash
ip -br a
```

3. Anota la IP de la interfaz de red. En los comandos siguientes se representará como `IP_SERVIDOR`.

### 6.2. Crear datos y realizar una copia

En `cliente-apellido`:

1. Instala `rsync`:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf install rsync -y

# Debian o Ubuntu
sudo apt install rsync -y
```

2. Crea datos de prueba en el RAID:

```bash
sudo mkdir -p /mnt/raid5/datos
echo "Documento inicial" | sudo tee /mnt/raid5/datos/informe.txt
echo "Inventario de activos" | sudo tee /mnt/raid5/datos/inventario.txt
sudo chown -R "$USER":"$USER" /mnt/raid5/datos
```

3. Realiza una copia al directorio personal del mismo usuario en el servidor. Sustituye `usuario` e `IP_SERVIDOR`:

```bash
rsync -av /mnt/raid5/datos/ usuario@IP_SERVIDOR:~/copia-ud2/
```

4. Comprueba el contenido en el servidor:

```bash
ssh usuario@IP_SERVIDOR 'ls -l ~/copia-ud2'
```

La barra final en `datos/` indica que se copia el contenido del directorio. Sin esa barra, `rsync` crearía una carpeta `datos` dentro del destino.

### 6.3. Restaurar un archivo eliminado

1. En el cliente, elimina solo el archivo de prueba:

```bash
rm /mnt/raid5/datos/informe.txt
```

2. Comprueba que ya no existe:

```bash
ls -l /mnt/raid5/datos
```

3. Restaura el archivo desde el servidor:

```bash
rsync -av usuario@IP_SERVIDOR:~/copia-ud2/informe.txt /mnt/raid5/datos/
```

4. Verifica el contenido restaurado:

```bash
cat /mnt/raid5/datos/informe.txt
```

5. Explica por qué RAID no habría recuperado este archivo: RAID protege frente al fallo de un disco, pero replica o distribuye también el borrado accidental.

## 7. Práctica 4 - Borrado seguro y ciclo de vida

### 7.1. Comparar borrado normal y borrado seguro

Esta actividad se limita a un archivo de prueba en el RAID virtual. No intentes recuperar archivos ni ejecutes herramientas de borrado sobre unidades físicas.

1. Crea un archivo de prueba:

```bash
echo "Dato confidencial de prueba" > /mnt/raid5/datos/confidencial.txt
```

2. Realiza un borrado normal y verifica que el archivo ya no aparece en el directorio:

```bash
rm /mnt/raid5/datos/confidencial.txt
ls -l /mnt/raid5/datos
```

3. Vuelve a crear el archivo y realiza un borrado mediante sobrescritura:

```bash
echo "Dato confidencial de prueba" > /mnt/raid5/datos/confidencial.txt
shred -u -n 1 /mnt/raid5/datos/confidencial.txt
ls -l /mnt/raid5/datos
```

4. Explica la diferencia entre ambos métodos y por qué la sobrescritura puede ser adecuada para un HDD, pero no garantiza el saneamiento completo de un SSD debido al *wear leveling* y a las áreas gestionadas por el controlador.


## 8. Actividades

### 8.1. Fundamentos, RAID y copias

1. Explica la diferencia entre seguridad activa y seguridad pasiva. Incluye tres ejemplos de cada una.

2. Una empresa dispone de cuatro discos de 4 TB. Compara RAID 0, RAID 1, RAID 5 y RAID 10. Indica capacidad útil aproximada, tolerancia a fallos y características principales.

3. Explica por qué RAID no sustituye a un sistema de copias de seguridad.

4. Una empresa realiza las siguientes copias: domingo, completa; lunes, martes y miércoles, incrementales. Si el sistema falla el miércoles, indica qué copias serán necesarias para recuperar la información.

5. Diseña una estrategia 3-2-1 para una empresa pequeña.

6. Explica la diferencia práctica entre un RPO de una hora y un RTO de una hora.

### 8.2. Riesgos físicos y retirada de equipos

1. Una pequeña empresa quiere instalar un CPD en la planta baja, junto a un almacén con acceso público. Identifica al menos cinco riesgos físicos o ambientales y propone una medida proporcionada para cada uno.

2. Una organización va a retirar dos equipos: un PC con HDD que contenía documentos internos y un portátil con SSD cifrado que contenía datos personales. Propón un proceso de borrado o saneamiento para cada equipo e indica qué evidencias deben registrarse antes de reciclarlos.

## 9. Autoevaluación

Responde de forma breve y con vocabulario técnico. Puedes comprobar las respuestas en la unidad teórica una vez completadas.

### 9.1. Almacenamiento y redundancia

1. ¿Qué objetivo tiene la seguridad pasiva?
2. ¿Qué diferencia existe entre HDD y SSD?
3. ¿Qué característica principal proporciona RAID 1?
4. ¿Qué sucede si falla un disco en RAID 0?
5. ¿Cuántos discos necesita como mínimo RAID 5?
6. ¿Qué ventaja proporciona RAID 6 frente a RAID 5?
7. ¿Qué caracteriza a RAID 10?
8. ¿Qué información puede aportar SMART sobre una unidad de almacenamiento?

### 9.2. Copias y recuperación

1. ¿Qué diferencia existe entre una copia completa y una incremental?
2. ¿Qué establece la regla 3-2-1?
3. ¿Qué significa RPO?
4. ¿Qué significa RTO?
5. ¿Qué es un NAS?
6. ¿Para qué sirve una snapshot?
7. ¿Por qué es importante probar las copias?
8. ¿Qué herramienta de Linux permite sincronizar archivos y directorios?
9. ¿Por qué un SAI no sustituye a un generador ni a una estrategia de recuperación?

### 9.3. Saneamiento y ciclo de vida

1. ¿Qué método es más adecuado para sanear un SSD: sobrescribir sectores concretos o emplear un mecanismo de saneamiento del fabricante? ¿Por qué?
2. ¿Qué diferencia existe entre los niveles *clear*, *purge* y *destroy* del NIST SP 800-88?
3. ¿Qué precauciones adicionales deben considerarse al eliminar datos almacenados en la nube?

## 10. Tarea evaluable única - Informe de continuidad y recuperación

Entrega un único informe en PDF o Markdown que integre las cuatro prácticas. Debe incluir capturas propias y explicaciones redactadas con tus palabras.

### 10.1. Contenido obligatorio

1. Diagrama sencillo de las dos máquinas virtuales, los cuatro discos del cliente y la ruta de la copia remota.
2. Inventario de las unidades y resultado de la consulta SMART, incluyendo la limitación si VirtualBox no muestra atributos reales.
3. Evidencias de creación, estado normal, estado degradado y reconstrucción del RAID 5.
4. Cálculo de capacidad útil aproximada del RAID creado y número de fallos de disco que tolera.
5. Evidencias de la copia con `rsync`, el borrado accidental y la restauración correcta de `informe.txt`.
6. Comparación entre RAID, copia de seguridad y borrado seguro, indicando qué problema resuelve cada medida.



## 11. Recursos

- [Documentación de `mdadm`](https://man7.org/linux/man-pages/man8/mdadm.8.html)
- [Manual de `rsync`](https://man7.org/linux/man-pages/man1/rsync.1.html)
- [smartmontools](https://www.smartmontools.org/)
- [NIST SP 800-88: Guidelines for Media Sanitization](https://csrc.nist.gov/pubs/sp/800/88/r1/final)
