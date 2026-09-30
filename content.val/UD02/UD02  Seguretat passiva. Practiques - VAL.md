---
title: "2.Seguretat passiva: emmagatzematge. Pràctiques"
weight: 2
---
# UD2 - Pràctiques: seguretat passiva i emmagatzematge

> Monitoratge, redundància, còpies de seguretat, recuperació i esborrament segur en un entorn de proves Linux.

| Dades de les pràctiques | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Durada estimada | 10 hores |
| Entorn | VirtualBox i una distribució Linux compatible |

## 1. Objectius

En finalitzar aquest itinerari, l'alumnat serà capaç de:

- Identificar unitats d'emmagatzematge i consultar el seu estat.
- Crear i administrar un RAID 5 per programari amb `mdadm`.
- Simular una fallada controlada i reconstruir un RAID.
- Realitzar una còpia de seguretat remota amb `rsync` i restaurar fitxers.
- Diferenciar l'esborrament normal de l'esborrament segur i aplicar-lo únicament sobre dades de prova.
- Documentar les evidències i proposar una estratègia bàsica de protecció de dades.

## 2. Abast i normes 

Aquestes pràctiques es realitzen únicament en màquines virtuals pròpies. No executes ordes d'esborrament, formatació, RAID ni recuperació en l'equip personal, en un disc físic o en sistemes aliens. Abans de cada pràctica, crea una instantània (*snapshot*) de la màquina virtual per a poder tornar a un estat conegut.

L'itinerari omet la configuració de SAN, iSCSI, RAID en Windows, TrueNAS, Clonezilla per xarxa i recuperació forense de fitxers esborrats. Són activitats útils, però requereixen més màquines, recursos o configuracions específiques. Ací es prioritzen procediments que es poden repetir i verificar amb dues màquines virtuals Linux.

## 3. Preparació comuna

### 3.1. Màquines virtuals necessàries

Es necessiten dues màquines Linux actualitzades:

| Màquina | Nom d'equip | Funció |
| --- | --- | --- |
| Client | `client-cognom` | Conté les dades de treball i el RAID. |
| Servidor | `servidor-cognom` | Rep les còpies de seguretat mitjançant SSH. |

Pots partir de la màquina Linux meua en la UD1 i clonar-la des de VirtualBox. AlmaLinux és l'opció recomanada per a seguir les ordes principals d'aquesta guia, però també es poden utilitzar Debian, Ubuntu Server, Rocky Linux o Fedora. En clonar, genera una nova adreça MAC per a evitar conflictes de xarxa.

### 3.2. Xarxa i noms

1. Configura totes dues màquines amb l'adaptador de xarxa en **NAT** per a instal·lar paquets.
2. Arranca cada màquina i canvia el seu nom. Substitueix `cognom` pel teu primer cognom sense espais:

```bash
sudo hostnamectl set-hostname client-cognom

```

En l'altra màquina:

```bash
sudo hostnamectl set-hostname servidor-cognom

```

3. Reinicia o obri una nova sessió i verifica el nom:

```bash
hostnamectl

```

4. Actualitza totes dues màquines:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf update -y

# Debian o Ubuntu
sudo apt update && sudo apt upgrade -y

```

5. Crea una instantània (*snapshot*) de cada màquina amb el nom `ud2-inici`.

### 3.3. Discs virtuals del client

1. Apaga la màquina `client-cognom`.
2. En VirtualBox, obri **Configuració > Emmagatzematge**.
3. Afig tres discs virtuals nous de 4 GB cadascun. Anomena'ls `raid-a`, `raid-b` i `raid-c`.
4. Afig un quart disc virtual de 4 GB anomenat `raid-recanvi`, però no l'utilitzes encara.
5. Inicia la màquina client i comprova els discs:

```bash
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS

```

Anota els noms assignats als quatre discs nous. En els exemples s'utilitzaran `/dev/sdb`, `/dev/sdc`, `/dev/sdd` i `/dev/sde`, però has de substituir-los pels que apareguen en el teu sistema.

## 4. Pràctica 1 - Inventari i estat SMART

### 4.1. Identificar les unitats

1. Instal·la les eines de monitoratge:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf install smartmontools -y

# Debian o Ubuntu
sudo apt install smartmontools -y

```

2. Mostra l'inventari d'unitats:

```bash
lsblk -o NAME,MODEL,SIZE,TYPE,TRAN

```

3. Consulta l'estat SMART de la unitat del sistema. Substitueix `/dev/sda` si el teu disc principal té un altre nom:

```bash
sudo smartctl -H /dev/sda

```

4. Intenta obtindre l'informe detallat:

```bash
sudo smartctl -a /dev/sda

```

En moltes màquines virtuals, VirtualBox no exposa els atributs SMART del disc virtual. Si apareix un missatge que SMART no està disponible, inclou la eixida com a evidència i explica la limitació: el sistema convidat veu un disc virtual, no el maquinari físic real.

### 4.2. Analitzar el resultat

1. Indica model, grandària i tipus de connexió que mostra `lsblk`.
2. Explica què signifiquen, a nivell general, els atributs de sectors reassignats, sectors pendents i errors no corregibles.
3. Justifica per què una alerta SMART ha de provocar una còpia de seguretat i revisió de la unitat, però no substitueix RAID ni còpies de seguretat.

## 5. Pràctica 2 - Creació i comprovació de RAID 5

### 5.1. Instal·lar i verificar `mdadm`

1. Instal·la l'eina de RAID per programari:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf install mdadm -y

# Debian o Ubuntu
sudo apt install mdadm -y

```

2. Comprova de nou els discs i confirma que els tres discs de RAID no contenen dades importants:

```bash
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS

```

3. Neteja exclusivament les signatures dels tres discs virtuals que utilitzaràs. No me n'executes d'aquestes ordes sobre el disc del sistema:

```bash
sudo wipefs -a /dev/sdb
sudo wipefs -a /dev/sdc
sudo wipefs -a /dev/sdd

```

### 5.2. Crear el volum RAID

1. Crea un RAID 5 amb els tres discs de dades:

```bash
sudo mdadm --create --verbose /dev/md0 --level=5 --raid-devices=3 /dev/sdb /dev/sdc /dev/sdd

```

2. Confirma la creació quan `mdadm` la sol·licite.
3. Consulta el progrés de sincronització. Prem `Ctrl+C` en acabar la comprovació:

```bash
watch -n 1 cat /proc/mdstat

```

4. Revisa els detalls del conjunt:

```bash
sudo mdadm --detail /dev/md0

```

### 5.3. Formatar i muntar el RAID

1. Quan la sincronització haja acabat, crea un sistema de fitxers ext4:

```bash
sudo mkfs.ext4 /dev/md0

```

2. Crea el punt de muntatge i munta el volum:

```bash
sudo mkdir -p /mnt/raid5
sudo mount /dev/md0 /mnt/raid5

```

3. Comprova capacitat i muntatge:

```bash
df -h /mnt/raid5

```

4. Crea dades de prova i verifica que s'han guardat:

```bash
echo "Prova RAID 5 - $(date)" | sudo tee /mnt/raid5/prova-raid.txt
sudo cat /mnt/raid5/prova-raid.txt

```

### 5.4. Simular una fallada i reconstruir

Aquesta simulació marca com a fallit un disc virtual del conjunt, però no esborra dades. Així i tot, verifica que utilitzes el disc correcte.

1. Marca `/dev/sdb` com a fallit i elimina'l del conjunt:

```bash
sudo mdadm /dev/md0 --fail /dev/sdb
sudo mdadm /dev/md0 --remove /dev/sdb

```

2. Consulta l'estat degradat:

```bash
cat /proc/mdstat
sudo mdadm --detail /dev/md0

```

3. Comprova que el fitxer continua disponible:

```bash
sudo cat /mnt/raid5/prova-raid.txt

```

4. Afig el disc de recanvi, suposant que siga `/dev/sde`:

```bash
sudo wipefs -a /dev/sde
sudo mdadm /dev/md0 --add /dev/sde

```

5. Observa la reconstrucció:

```bash
watch -n 1 cat /proc/mdstat

```

6. Quan acabe, comprova que el conjunt està actiu i que el fitxer continua accessible:

```bash
sudo mdadm --detail /dev/md0
sudo cat /mnt/raid5/prova-raid.txt

```

7. Explica què hauria hagut si haguera fallat un segon disc abans de completar la reconstrucció.

## 6. Pràctica 3 - Còpia remota i recuperació amb `rsync`

### 6.1. Preparar el servidor de còpies

En `servidor-cognom`:

1. Instal·la i activa el servidor SSH:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf install openssh-server rsync -y

# Debian o Ubuntu
sudo apt install openssh-server rsync -y
sudo systemctl enable --now sshd

```

2. Consulta l'adreça IP:

```bash
ip -br a

```

3. Anota la IP de la interfície de xarxa. En les ordes següents es representarà com a `IP_SERVIDOR`.

### 6.2. Crear dades i realitzar una còpia

En `client-cognom`:

1. Instal·la `rsync`:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf install rsync -y

# Debian o Ubuntu
sudo apt install rsync -y

```

2. Crea dades de prova en el RAID:

```bash
sudo mkdir -p /mnt/raid5/datos
echo "Document inicial" | sudo tee /mnt/raid5/datos/informe.txt
echo "Inventari d'actius" | sudo tee /mnt/raid5/datos/inventario.txt
sudo chown -R "$USER":"$USER" /mnt/raid5/datos

```

3. Realitza una còpia al directori personal del mateix usuari en el servidor. Substitueix `usuari` i `IP_SERVIDOR`:

```bash
rsync -av /mnt/raid5/datos/ usuari@IP_SERVIDOR:~/copia-ud2/

```

4. Comprova el contingut en el servidor:

```bash
ssh usuari@IP_SERVIDOR 'ls -l ~/copia-ud2'

```

La barra final en `datos/` indica que es copia el contingut del directori. Sense eixa barra, `rsync` crearia una carpeta `datos` dins de la destinació.

### 6.3. Restaurar un fitxer eliminat

1. En el client, elimina només el fitxer de prova:

```bash
rm /mnt/raid5/datos/informe.txt

```

2. Comprova que ja no existeix:

```bash
ls -l /mnt/raid5/datos

```

3. Restaura el fitxer des del servidor:

```bash
rsync -av usuari@IP_SERVIDOR:~/copia-ud2/informe.txt /mnt/raid5/datos/

```

4. Verifica el contingut restaurat:

```bash
cat /mnt/raid5/datos/informe.txt

```

5. Explica per què RAID no hauria recuperat aquest fitxer: RAID protegeix davant la fallada d'un disc, però replica o distribueix també l'esborrament accidental.

## 7. Pràctica 4 - Esborrament segur i cicle de vida

### 7.1. Comparar esborrament normal i esborrament segur

Aquesta activitat es limita a un fitxer de prova en el RAID virtual. No intentes recuperar fitxers ni me n'executes d'eines d'esborrament sobre unitats físiques.

1. Crea un fitxer de prova:

```bash
echo "Dada confidencial de prova" > /mnt/raid5/datos/confidencial.txt

```

2. Realitza un esborrament normal i verifica que el fitxer ja no apareix en el directori:

```bash
rm /mnt/raid5/datos/confidencial.txt
ls -l /mnt/raid5/datos

```

3. Torna a crear el fitxer i realitza un esborrament mitjançant sobreescriptura:

```bash
echo "Dada confidencial de prova" > /mnt/raid5/datos/confidencial.txt
shred -u -n 1 /mnt/raid5/datos/confidencial.txt
ls -l /mnt/raid5/datos

```

4. Explica la diferència entre tots dos mètodes i per què la sobreescriptura pot ser adequada per a un HDD, però no garanteix el sanejament complet d'un SSD a causa del *wear leveling* i a les àrees gestionades pel controlador.

## 8. Activitats

### 8.1. Fonaments, RAID i còpies

1. Explica la diferència entre seguretat activa i seguretat passiva. Inclou tres exemples de cadascuna.
2. Una empresa disposa de quatre discs de 4 TB. Compara RAID 0, RAID 1, RAID 5 i RAID 10. Indica capacitat útil aproximada, tolerància a fallades i característiques principals.
3. Explica per què RAID no substitueix a un sistema de còpies de seguretat.
4. Una empresa realitza les següents còpies: diumenge, completa; dilluns, dimarts i dimecres, incrementals. Si el sistema falla dimecres, indica quines còpies seran necessàries per a recuperar la informació.
5. Dissenya una estratègia 3-2-1 per a una empresa petita.
6. Explica la diferència pràctica entre un RPO d'una hora i un RTO d'una hora.

### 8.2. Riscos físics i retirada d'equips

1. Una petita empresa vol instal·lar un CPD en la planta baixa, al costat d'un magatzem amb accés públic. Identifica almenys cinc riscos físics o ambientals i proposa una mesura proporcionada per a cadascun.
2. Una organització retirarà dos equips: un PC amb HDD que contenia documents interns i un portàtil amb SSD xifrat que contenia dades personals. Proposa un procés d'esborrament o sanejament per a cada equip i indica quines evidències han de registrar-se abans de reciclar-los.

## 9. Autoavaluació

Respon de manera breu i amb vocabulari tècnic. Pots comprovar les respostes en la unitat teòrica una vegada completades.

### 9.1. Emmagatzematge i redundància

1. Quin objectiu té la seguretat passiva?
2. Quina diferència existeix entre HDD i SSD?
3. Quina característica principal proporciona RAID 1?
4. Què passa si falla un disc en RAID 0?
5. Quants discs necessita com a mínim RAID 5?
6. Quin avantatge proporciona RAID 6 enfront de RAID 5?
7. Què caracteritza a RAID 10?
8. Quina informació pot aportar SMART sobre una unitat d'emmagatzematge?

### 9.2. Còpies i recuperació

1. Quina diferència existeix entre una còpia completa i una incremental?
2. Què estableix la regla 3-2-1?
3. Què significa RPO?
4. Què significa RTO?
5. Què és un NAS?
6. Per a què serveix una instantània (*snapshot*)?
7. Per què és important provar les còpies?
8. Quina eina de Linux permet sincronitzar fitxers i directoris?
9. Per què un SAI no substitueix a un generador ni a una estratègia de recuperació?

### 9.3. Sanejament i cicle de vida

1. Quin mètode és més adequat per a sanejar un SSD: sobreescriure sectors concrets o emprar un mecanisme de sanejament del fabricant? Per què?
2. Quina diferència existeix entre els nivells *clear*, *purge* i *destroy* del NIST SP 800-88?
3. Quines precaucions addicionals han de considerar-se en eliminar dades emmagatzemades en el núvol?

## 10. Tasca avaluable única - Informe de continuïtat i recuperació

Lliura un únic informe en PDF o Markdown que integre les quatre pràctiques. Ha d'incloure captures pròpies i explicacions redactades amb les teues paraules.

### 10.1. Contingut obligatori

1. Diagrama senzill de les dues màquines virtuals, els quatre discs del client i la ruta de la còpia remota.
2. Inventari de les unitats i resultat de la consulta SMART, incloent-hi la limitació si VirtualBox no mostra atributs reals.
3. Evidències de creació, estat normal, estat degradat i reconstrucció del RAID 5.
4. Càlcul de capacitat útil aproximada del RAID creat i nombre de fallades de disc que tolera.
5. Evidències de la còpia amb `rsync`, l'esborrament accidental i la restauració correcta d'`informe.txt`.
6. Comparació entre RAID, còpia de seguretat i esborrament segur, indicant quin problema resol cada mesura.

## 11. Recursos

* [Documentació de `mdadm](https://man7.org/linux/man-pages/man8/mdadm.8.html)`
* [Manual de `rsync](https://man7.org/linux/man-pages/man1/rsync.1.html)`
* [smartmontools](https://www.smartmontools.org/)
* [NIST SP 800-88: Guidelines for Media Sanitization](https://csrc.nist.gov/pubs/sp/800/88/r1/final)

```

```