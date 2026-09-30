---

## title: "2. Seguretat passiva."
weight: 1

# UD2 - Seguretat passiva: emmagatzematge

> Protecció de la informació, redundància, còpies de seguretat i recuperació.

| Dades de la unitat | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Durada | 12 hores |

## Índex

1. [Fonaments i seguretat física](https://www.google.com/search?q=%231-fonaments-i-seguretat-f%C3%ADsica)
2. [Emmagatzematge i fallades](https://www.google.com/search?q=%232-emmagatzematge-i-fallades)
3. [Redundància i RAID](https://www.google.com/search?q=%233-redund%C3%A0ncia-i-raid)
4. [Còpies de seguretat i recuperació](https://www.google.com/search?q=%234-c%C3%B2pies-de-seguretat-i-recuperaci%C3%B3)
5. [Esborrament segur i cicle de vida](https://www.google.com/search?q=%235-esborrament-segur-i-cicle-de-vida)
6. [Resum](https://www.google.com/search?q=%236-resum)
7. [Recursos](https://www.google.com/search?q=%237-recursos)
8. [Relació amb els resultats d'aprenentatge](https://www.google.com/search?q=%238-relaci%C3%B3-amb-els-resultats-daprenentatge)

---

## 1. Fonaments i seguretat física

### 1.1. Introducció

La seguretat d'un sistema informàtic no consisteix únicament a impedir que un atacant hi accedisca. També cal estar preparat per a situacions en què es produïsquen fallades.

Un servidor pot patir:

* L'avaria d'un disc.
* Una fallada elèctrica.
* Un error humà.
* L'eliminació accidental de fitxers.
* La corrupció d'un sistema de fitxers.
* Un atac de ransomware.
* Un incendi o una inundació.
* El robatori de l'equipament.
* Una actualització defectuosa.
* Una fallada de software.

Per aquest motiu, les organitzacions necessiten mecanismes que permeten reduir l'impacte dels incidents i recuperar la informació i els serveis.

Aquests mecanismes formen part de la seguretat passiva.

En aquesta unitat estudiarem especialment els sistemes d'emmagatzematge, la redundància mitjançant RAID, les còpies de seguretat, els sistemes NAS, les snapshots i les estratègies de recuperació.

### 1.2. Objectius

En finalitzar aquesta unitat, l'alumnat serà capaç de:

* Diferenciar seguretat activa i seguretat passiva.
* Identificar els principals sistemes d'emmagatzematge.
* Diferenciar HDD, SSD i NVMe.
* Identificar els principals tipus de fallades d'emmagatzematge.
* Comprendre el concepte de redundància.
* Explicar el funcionament de RAID.
* Diferenciar RAID 0, RAID 1, RAID 5, RAID 6 i RAID 10.
* Seleccionar un nivell RAID en funció de les necessitats.
* Comprendre les limitacions de RAID.
* Explicar què és una còpia de seguretat.
* Diferenciar còpies completes, incrementals i diferencials.
* Dissenyar una estratègia bàsica de còpies.
* Aplicar la regla 3-2-1.
* Comprendre els conceptes RPO i RTO.
* Conéixer sistemes NAS i snapshots.
* Realitzar i comprovar còpies de seguretat i recuperació.
* Dissenyar una política d'emmagatzematge i backup.

### 1.3. Seguretat passiva

La seguretat passiva engloba les mesures destinades principalment a reduir les conseqüències d'un incident i facilitar la recuperació.

Per exemple, imaginem un servidor que disposa de dos discs.

Si un d'ells falla, una configuració redundant pot permetre que el sistema continue funcionant.

Si a més es disposa de còpies de seguretat, serà possible recuperar la informació fins i tot davant de problemes més greus.

Podem representar el concepte de la forma següent:

```
                SEGURETAT
                   │
          ┌────────┴────────┐
          │                 │
        Activa            Passiva
          │                 │
   Prevenir / detectar    Recuperar
   / blocar               / continuar

```

**Exemples de seguretat activa:**

* Firewall.
* Antivirus.
* IDS/IPS.
* Control d'accés.
* Monitoratge i sistemes de detecció.

**Exemples de seguretat passiva:**

* RAID i sistemes redundants.
* Còpies de seguretat i emmagatzematge extern.
* SAI i replicació.
* Plans de recuperació.

### 1.4. Seguretat física i CPD

Un centre de processament de dades (CPD) concentra servidors, xarxes i emmagatzematge crítics. Centralitzar els equips facilita el control d'accessos, la climatització, el manteniment i les comunicacions, però també exigeix planificar els riscos físics i ambientals. La ubicació ha d'evitar zones amb elevat risc d'inundació, incendi, vibracions o accessos no controlats, i la sala ha de comptar amb procediments documentats per a recuperar els serveis davant d'una incidència.

Les mesures habituals inclouen control d'accés mitjançant credencials o biometria, videovigilància, detecció i extinció d'incendis, fals sòl per a cablejat i ventilació, i control de temperatura i humitat. En un CPD amb racks, els passadissos freds aporten aire a la part frontal dels equips i els passadissos calents arrepleguen l'aire d'eixida; aquesta separació redueix el sobreescalfament i millora l'eficiència energètica.

La continuïtat també requereix alimentació i comunicacions redundants. Un SAI proporciona temps per a una apagada meguidament controlada durant un tall breu; un generador pot cobrir interrupcions meguidament prolongades. Per a serveis crítics, es poden contractar enllaços d'Internet amb proveïdors i rutes diferents. Un centre de suport, ubicat a suficient distància del CPD principal, permet restaurar serveis si una catàstrofe afecta la ubicació primària. Per exemple, una empresa pot replicar la base de dades i conservar còpies verificades en un segon centre, provant periòdicament el procediment de commutació.

## 2. Emmagatzematge i fallades

### 2.1. Emmagatzematge de la informació

La informació d'una organització es pot emmagatzemar en diferents dispositius i sistemes.

Entre els més habituals trobem:

HDD.
SSD.
NVMe.
NAS.
SAN.
Cabines d'emmagatzematge.
Sistemes distribuïts.

La tria depén de factors com ara:

Capacitat.
Rendiment.
Cost.
Fiabilitat.
Disponibilitat.
Redundància.
Tipus de informació.

També importa la forma d'accés: un sistema de còpies històriques pot utilitzar cinta, que ofereix gran capacitat a baix cost però accés seqüencial; una base de dades necessita normalment accés aleatori i baixa latència, per la qual cosa pot requerir SSD o NVMe. Per a compartir documents entre diversos equips sol ser suficient un NAS amb accés a nivell de fitxer, mentre que un entorn de virtualització pot necessitar emmagatzematge de blocs mitjançant SAN o una plataforma definida per software.

Per exemple, una xicoteta empresa pot combinar SSD per a les màquines virtuals que executen aplicacions, HDD en un NAS per a documents compartits i emmagatzematge extern per a una còpia de seguretat. No existeix una tecnologia universalment millor: la solució adequada respon als requisits de rendiment, disponibilitat, pressupost i protecció de les dades.

### 2.2. Discs HDD

Els discs HDD utilitzen plats magnètics i capçals mecànics per a emmagatzemar i recuperar informació.

Una representació simplificada seria:

```
   HDD

```

┌───────────────┐
│   Plat        │
│      ↓        │
│  ──────────   │
│      ↑        │
│   Capçal      │
└───────────────┘

Avantatges
Gran capacitat.
Preu reduït per GB.
Adequats per a grans volums de informació.
Interessants per a emmagatzematge de backup.

Inconvenients
Components mecànics.
Major latència.
Menor rendiment que els SSD en determinats escenaris.
Sensibilitat a colps i vibracions.

### 2.3. Discs SSD

Els SSD emmagatzemen la informació en memòria flash.

No utilitzen parts mecàniques mòbils.

Avantatges
Alta velocitat.
Baixa latència.
Menys soroll.
Major resistència davant de vibracions.
Bon rendiment per a sistemes operatius i aplicacions.

Inconvenients
Preu per GB generalment superior.
Desgast de les cel·les.
Recuperació de dades potencialment complexa davant de determinades fallades.

Els SSD són habituals en:

Servidors.
Ordinadors.
Màquines virtuals.
Bases de dades.
Sistemes d'alt rendiment.

### 2.4. NVMe

NVMe és un protocol dissenyat específicament per a dispositius d'emmagatzematge no volàtil d'alta velocitat.

Els dispositius NVMe solen utilitzar PCI Express.

Comparats amb dispositius SATA tradicionals, poden proporcionar:

Major amplada de banda.
Menor latència.
Major nombre d'operacions d'entrada/eixida.

Són especialment interessants per a:

Bases de dades.
Virtualització.
Servidors.
Aplicacions amb moltes operacions de disc.

### 2.5. Fallades d'emmagatzematge

Els problemes d'emmagatzematge poden tindre diferents orígens.

#### 2.5.1. Fallada física

Exemple:

El disc deixa de funcionar.

Es pot produir per:

Desgast.
Temperatura.
Fallada electrònica.
Fallada mecànica.
Danys físics.

#### 2.5.2. Fallada lògica

El dispositiu continua funcionant, però la informació o el sistema de fitxers presenta problemes.

Exemples:

Corrupció del sistema de fitxers.
Partició danyada.
Eliminació accidental.
Metadades corruptes.

#### 2.5.3. Error humà

Un administrador pot executar accidentalment:

rm -rf

sobre el directori equivocat.

També es pot produir:

Sobreescriptura de fitxers.
Eliminació de bases de dades.
Configuració incorrecta.
Formatat accidental.

#### 2.5.4. Malware

Un ransomware pot xifrar els fitxers disponibles.

Per exemple:

document1.docx
↓
document1.docx.xifrat

Si el sistema de backup està connectat i accessible des del mateix entorn, també podria veure's afectat.

#### 2.5.5. Catàstrofes físiques

Alguns riscos són:

Incendi.
Inundació.
Robatori.
Sobretensió.
Fallada de refrigeració.

Per això és recomanable disposar de còpies en una ubicació diferent.

### 2.6. Fiabilitat i monitoratge de l'emmagatzematge

En seleccionar emmagatzematge s'han de valorar capacitat, rendiment, cost, consum, durabilitat i fiabilitat. El **MTBF** expressa una estimació estadística del temps mitjà entre fallades d'una població d'unitats, mentre que l'**AFR** representa la taxa anualitzada de fallades. Cap mètrica no prediu el moment exacte en què fallarà un disc concret; per això, les decisions s'han de complementar amb redundància, còpies de seguretat i supervisió.

La tecnologia SMART permet consultar indicadors de salut de HDD i SSD, com ara sectors reassignats, errors de lectura, temperatura i, en SSD, desgast de les cel·les. Una alerta SMART ha de provocar la revisió i substitució planificada de la unitat, però la seua absència no garanteix que no vaja a fallar. Per exemple, si un servidor detecta sectors reassignats creixents en un disc d'un RAID 5, l'administrador l'ha de substituir abans que coincidisca amb una altra fallada durant la reconstrucció.

| Necessitat | Opció habitual | Exemple |
| --- | --- | --- |
| Gran capacitat a baix cost | HDD o cinta per a arxivament. | Còpies històriques mensuals. |
| Baixa latència i moltes operacions d'E/E | SSD NVMe. | Base de dades o màquines virtuals. |
| Compartició de fitxers | NAS amb SMB/NFS. | Documentació d'un departament. |
| Accés per blocs d'alt rendiment | SAN o emmagatzematge definit per software. | Clúster de virtualització. |

## 3. Redundància i RAID

### 3.1. Redundància

La redundància consisteix a disposar d'elements addicionals que permeten mantindre el servei quan un d'ells falla.

Exemple:

Servidor
├── Disc 1
└── Disc 2

Si tots dos contenen informació redundant i un falla, el sistema pot continuar funcionant.

La redundància es pot aplicar a:

Discs.
Fonts d'alimentació.
Servidors.
Xarxes.
Connexions a Internet.
Sistemes d'emmagatzematge.

### 3.2. RAID

RAID — Redundant Array of Independent Disks

RAID permet combinar diversos discs per a aconseguir diferents objectius:

Major rendiment.
Redundància.
Tolerància a fallades.
Major capacitat útil.

Tanmateix, RAID no és un sistema de backup.

Aquesta diferència ha de quedar clara:

RAID
↓
Protecció principalment davant de fallades de discs

BACKUP
↓
Protecció davant de pèrdua, modificació o destrucció de informació

### 3.3. RAID 0

RAID 0 distribueix les dades entre diversos discs mitjançant una tècnica denominada striping.

Exemple:

```
   RAID 0

```

Disc 1       Disc 2

---

Bloc A        Bloc B
Bloc C        Bloc D
Bloc E        Bloc F

Avantatge

Pot augmentar considerablement el rendiment.

Inconvenient

No existeix redundància.

Si falla un dels discs:

Disc 1 → OK
Disc 2 → FALLA

es pot perdre el conjunt complet de la informació.

Ús

Es pot utilitzar quan el rendiment és prioritari i les dades es poden reconstruir des d'una altra font.

### 3.4. RAID 1

RAID 1 utilitza mirroring, és a dir, manté una còpia de les dades en un altre disc.

Disc 1       Disc 2

Dades A       Dades A
Dades B       Dades B
Dades C       Dades C

Si un disc falla:

Disc 1 → FALLA
Disc 2 → OK

la informació continua disponible.

Avantatges
Senzill.
Bona tolerància a fallades.
Recuperació relativament simple.

Inconvenient

La capacitat útil és aproximadament la d'un únic disc.

Per exemple:

2 × 2 TB

proporcionen aproximadament:

2 TB útils

### 3.5. RAID 5

RAID 5 combina distribució de dades i paritat.

Necessita almenys tres discs.

Una representació simplificada:

Disc 1   Disc 2   Disc 3

Dades     Dades     Paritat
Dades     Paridad   Dades
Paritat   Dades     Dades

La informació de paritat permet reconstruir les dades quan falla un dels discs.

Avantatges
Tolerància a una fallada.
Bon aprofitament de la capacitat.
Pot proporcionar un equilibri entre rendiment, capacitat i redundància.

Inconvenients
La reconstrucció pot ser lenta.
Durant la reconstrucció existeix una situació de major risc.
Les operacions d'escriptura tenen un cost addicional a causa de la paritat.

### 3.6. RAID 6

RAID 6 utilitza doble paritat.

Necessita almenys quatre discs i pot suportar la fallada simultània de dues unitats.

Disc 1   Disc 2   Disc 3   Disc 4
Dades     Dades     Paritat   Paritat
Dades     Paritat   Dades     Paritat
Paritat   Dades     Dades     Paritat

És apropiat per a sistemes amb grans quantitats d'emmagatzematge on es desitja una major tolerància a fallades.

### 3.7. RAID 10

RAID 10 combina:

RAID 1 → redundància.
RAID 0 → distribució.

Exemple:

```
      RAID 10

   ┌─────────────┐
   │             │
RAID 1        RAID 1
D1 + D2       D3 + D4
   │             │
   └──── RAID 0 ─┘

```

Proporciona:

Bon rendiment.
Redundància.
Bon comportament en sistemes amb moltes operacions d'entrada/eixida.

El nombre de discs necessaris és superior al de RAID 1.

### 3.8. Comparació de RAID

| Nivell | Discs mínims | Redundància | Tolerància | Característica principal |
| --- | --- | --- | --- | --- |
| RAID 0 | 2 | No | Cap | Rendiment |
| RAID 1 | 2 | Sí | 1 disc | Simplicitat |
| RAID 5 | 3 | Sí | 1 disc | Capacitat + redundància |
| RAID 6 | 4 | Sí | 2 discs | Major tolerància |
| RAID 10 | 4 | Sí | Depén del patró de fallades | Rendiment + redundància |

### 3.9. RAID no és backup

Aquest concepte és especialment important.

Suposem que tenim:

Servidor
↓
RAID 1
↓
Disc A + Disc B

Un usuari elimina accidentalment:

clients.xlsx

L'eliminació es replica en tots dos discs.

Per tant:

Disc A → fitxer eliminat
Disc B → fitxer eliminat

RAID no permet recuperar automàticament el fitxer.

En canvi, un backup podria contindre una versió anterior:

Backup
↓
clients.xlsx
↓
Recuperació

Per això:

RAID protegeix principalment davant de determinades fallades de hardware; el backup protegeix la informació davant de molts tipus de pèrdua o alteració.

## 4. Còpies de seguretat i recuperació

### 4.1. Còpies de seguretat

Una còpia de seguretat és una còpia d'informació emmagatzemada en un mitjà alternatiu que es pot utilitzar per a recuperar les dades originals després d'una pèrdua, dany, corrupció o incident. Ha de protegir dades, configuracions i, quan siga necessari, imatges de sistemes complets. Una imatge facilita la restauració d'un equip després d'una fallada greu; en canvi, una còpia de fitxers permet recuperar selectivament un document sense restaurar tot el sistema.

Una estratègia de backup ha de definir:

Quina informació copiar.
Quan copiar-la.
On emmagatzemar-la.
Quant de temps conservar-la.
Qui hi pot accedir.
Com protegir-la.
Com restaurar-la.
Com comprovar que funciona.

Les còpies s'han d'automatitzar sempre que siga possible, xifrar-se quan contenen informació sensible i supervisar-se mitjançant avisos d'èxit o error. Una planificació habitual pot combinar una còpia completa setmanal, còpies incrementals diàries i una retenció diferenciada per a versions diàries, mensuals i anuals. La periodicitat ha de respondre al RPO: si una organització només accepta perdre fins a quatre hores de treball, una còpia diària no serà suficient.

La restauració és la prova definitiva d'una estratègia. Per exemple, després de configurar una còpia programada d'una base de dades, l'administrador l'ha de restaurar en un entorn de proves, comprovar que obri correctament i mesurar el temps emprat. Aquesta evidència permet confirmar si el procediment compleix el RTO establit.

### 4.2. Backup complet

Una còpia completa conté tota la informació seleccionada.

Exemple:

Diumenge
Backup complet → 500 GB

Avantatges:

Restauració senzilla.
Independència respecte d'altres còpies.

Inconvenients:

Consumeix més emmagatzematge.
Pot tardar més temps.

### 4.3. Backup incremental

Una còpia incremental conté els canvis realitzats des de l'última còpia.

Exemple:

Diumenge
Completa

Dilluns
Canvis del dilluns

Dimarts
Canvis del dimarts

Dimecres
Canvis del dimecres

Avantatge:

Menor consum d'espai.

Inconvenient:

Per a realitzar una recuperació completa pot ser necessari disposar de:

Backup complet
+
Incremental dilluns
+
Incremental dimarts
+
Incremental dimecres

### 4.4. Backup diferencial

La còpia diferencial emmagatzema els canvis realitzats des de l'última còpia completa.

Exemple:

Diumenge
Completa

Dilluns
Canvis des de diumenge

Dimarts
Canvis des de diumenge + dilluns

Dimecres
Canvis des de diumenge + dilluns + dimarts

Per a recuperar l'estat del dimecres normalment necessitem:

Backup complet
+
Backup diferencial del dimecres

### 4.5. Comparació de còpies

| Tipus | Espai | Velocitat de backup | Recuperació |
| --- | --- | --- | --- |
| Completa | Alt | Menor | Molt senzilla |
| Incremental | Baix | Alta | Més complexa |
| Diferencial | Mitjà | Intermèdia | Senzilla |

### 4.6. Regla 3-2-1

La regla 3-2-1 és una estratègia senzilla per a millorar la protecció dels backups.

Consisteix a mantindre:

3 còpies de la informació

2 suports diferents

1 còpia fora de la ubicació principal

Exemple:

```
             DADES
               │
      ┌────────┼────────┐
      │        │        │
   Original   NAS     Cloud
                     / ubicació externa

```

Això permet reduir el risc que un únic incident destruïsca totes les còpies.

### 4.7. Backup i ransomware

Els sistemes de backup també s'han de protegir.

Imaginem:

Servidor
↓
Backup NAS

Si l'atacant aconsegueix privilegis suficients sobre tots dos sistemes, podria xifrar:

Servidor → xifrat
NAS      → xifrat

Per això hem d'aplicar mesures addicionals:

Separació de comptes.
Contrasenyes meguidament robustes.
MFA.
Permisos mínims.
Segmentació de xarxa.
Versionat.
Còpies desconnectades quan siga possible.
Emmagatzematge immutable.
Còpies externes.
Proves de recuperació.

### 4.8. RPO

RPO — Recovery Point Objective

El RPO indica la quantitat màxima de informació que una organització està disposada a perdre.

Exemple:

RPO = 4 hores

Significa que l'estratègia ha de permetre recuperar informació amb una antiguitat màxima objectiu d'unes quatre hores.

Com menor siga el RPO:

RPO xicotet
↓
Més freqüència de còpia/replicació
↓
Major cost i complexitat

### 4.9. RTO

RTO — Recovery Time Objective

El RTO indica quant de temps pot tardar com a màxim la recuperació d'un servei.

Exemple:

RTO = 8 hores

L'organització ha de disposar de procediments i recursos adequats per a intentar recuperar el servei dins d'aquest objectiu.

### 4.10. Diferència entre RPO i RTO

| Concepte | Pregunta |
| --- | --- |
| RPO | Quanta informació podem perdre? |
| RTO | Quant de temps podem estar sense servei? |

Exemple:

Una empresa estableix:

RPO = 1 hora
RTO = 4 hores

Per tant:

S'intenta limitar la pèrdua d'informació a una hora.
S'intenta recuperar el servei en quatre hores.

### 4.11. NAS

Un NAS — Network Attached Storage és un dispositiu d'emmagatzematge connectat a una xarxa.

Permet proporcionar emmagatzematge centralitzat a diferents equips.

```
         ┌──── PC 1
         │

```

Xarxa ───────┼──── PC 2
│
├──── PC 3
│
└──── NAS

Un NAS pot proporcionar:

Carpetes compartides.
Usuaris.
Permisos.
RAID.
Snapshots.
Còpies de seguretat.
Replicació.
Serveis de xarxa.

### 4.12. NAS davant d'emmagatzematge local

Emmagatzematge local
PC
↓
Disc

Les dades estan directament en l'equip.

NAS
PC ───┐
PC ───┼── Xarxa ── NAS
PC ───┘

Les dades es centralitzen en un sistema d'emmagatzematge accessible mitjançant xarxa.

Això facilita:

Administració.
Compartició.
Backup.
Control d'accés.

### 4.13. TrueNAS

TrueNAS és una plataforma utilitzada per a implementar sistemes d'emmagatzematge en xarxa.

Permet treballar amb:

Discs.
Pools d'emmagatzematge.
Sistemes de fitxers.
Usuaris.
Permisos.
Comparticions.
Snapshots.
Replicació.
Serveis de xarxa.

En un entorn de proves d'ASIR es pot utilitzar per a practicar:

RAID.
Emmagatzematge.
Compartició de fitxers.
Backup.
Snapshots.
Recuperació.

### 4.14. Snapshots

Una snapshot representa l'estat d'un sistema de fitxers o emmagatzematge en un moment determinat.

Exemple:

10:00 → Snapshot 1
12:00 → Snapshot 2
14:00 → Snapshot 3

Si un usuari modifica un fitxer a les 14:30, pot ser possible recuperar una versió anterior mitjançant una snapshot.

Les snapshots són especialment útils per a:

Errors humans.
Recuperació ràpida.
Versionat.
Protecció davant de determinades modificacions.

Però:

Una snapshot no substitueix necessàriament una còpia de seguretat.

Si totes les snapshots estan emmagatzemades en el mateix dispositiu que les dades i aquest dispositiu es destrueix, també es poden perdre les snapshots.

### 4.15. Recuperació de informació

Una estratègia de backup ha d'incloure procediments de recuperació.

Procés bàsic:

Incident
↓
Identificar informació afectada
↓
Seleccionar backup
↓
Restaurar
↓
Comprovar integritat
↓
Comprovar aplicació
↓
Posar servei en producció
↓
Documentar

### 4.16. Proves de restauració

No n'hi ha prou amb fer còpies.

Cal comprovar periòdicament que es poden restaurar.

Una prova pot consistir a:

Seleccionar una còpia.
Restaurar alguns fitxers.
Comprovar el seu contingut.
Restaurar una màquina virtual.
Comprovar una base de dades.
Mesurar el temps de recuperació.
Registrar els resultats.

Una còpia que mai no ha sigut provada suposa un risc.

### 4.17. Política de backup

Una política de còpies hauria de definir clarament:

Informació protegida

Exemple:

Bases de dades.
Documents.
Configuracions.
Màquines virtuals.
Servidors.

Freqüència

Exemple:

Backup complet → setmanal
Backup incremental → diari

Retenció

Exemple:

Diaris → 30 dies
Setmanals → 3 mesos
Mensuals → 1 any

Destins
NAS.
Servidor de backup.
Cloud.
Ubicació externa.

### 4.18. Eines de backup

#### rsync

rsync permet sincronitzar fitxers i directoris.

Exemple:

rsync -av /datos/ /backup/datos/

Es pot utilitzar per a realitzar sincronitzacions locals o remotes.

#### Clonezilla

Clonezilla permet treballar amb imatges i clonacions de discs i particions.

Es pot utilitzar per a:

Clonar equips.
Crear imatges.
Restaurar sistemes.
Preparar desplegaments.

#### Duplicati

Duplicati permet crear còpies programades i pot utilitzar diferents destins d'emmagatzematge.

Entre les seues característiques es troben:

Programació.
Versionat.
Xifrat.
Destins locals i remots.

## 5. Esborrament segur i cicle de vida

### 5.1. Esborrament segur de la informació

Eliminar un fitxer o formatar ràpidament una unitat no garanteix que les dades no es puguen recuperar. El mètode adequat depén del mitjà, del nivell de confidencialitat i de la reutilització prevista. En HDD, la sobreescriptura gestionada correctament pot ser eficaç perquè els sectors es poden escriure de forma directa. En SSD, el *wear leveling* i l'espai reservat pel controlador impedeixen assegurar la sobreescriptura d'una ubicació concreta; es recomanen les ordes de sanejament del fabricant, com ara **ATA Secure Erase**, o l'esborrament criptogràfic mitjançant destrucció de claus quan la unitat es va xifrar des de l'inici.

La guia [NIST SP 800-88](https://csrc.nist.gov/pubs/sp/800/88/r1/final) diferencia tres nivells: **clear**, que elimina les dades de manera que no siguen recuperables amb tècniques habituals; **purge**, que aplica un sanejament més profund; i **destroy**, que inutilitza físicament el suport. L'organització ha de definir quin mètode empra, qui l'autoritza i quina evidència conserva. Per exemple, abans de reciclar un portàtil que contenia informació personal, es pot verificar que estava xifrat, eliminar de forma segura les seues claus, restablir-lo i registrar el número de sèrie, el responsable i el resultat del procés.

En serveis cloud, el client no controla directament el hardware i ha de revisar les condicions d'eliminació, retenció i còpies del proveïdor. El xifrat, una política de retenció definida, contractes adequats i el registre de les operacions ajuden a complir les obligacions de protecció de dades. L'esborrament segur també s'aplica a dispositius mòbils: s'han d'eliminar els comptes vinculats, comprovar la sincronització en el núvol i utilitzar el restabliment de fàbrica amb el xifrat meguidament habilitat.

## 6. Resum

En aquesta unitat hem estudiat com protegir la informació davant de fallades i pèrdues.

Els conceptes fonamentals són:

* Seguretat passiva i protecció física.
* Emmagatzematge en HDD, SSD i NVMe.
* Redundància i RAID.
* Backup, NAS, snapshots i recuperació.
* RPO, RTO i proves de restauració.
* Esborrament segur i cicle de vida del suport.

Els nivells RAID permeten millorar la disponibilitat o el rendiment, però no substitueixen les còpies de seguretat.

Una estratègia professional ha de combinar diferents mecanismes:

```
    INFORMACIÓ
         │
 ┌───────┴────────┐
 │                │

```

Redundància         Backup
│                │
RAID        3-2-1 / extern
│                │
└───────┬────────┘
│
RECUPERACIÓ

La idea fonamental d'aquesta unitat és:

No ens hem de preguntar només com evitar que les dades es perden, sinó també com recuperar-les quan la fallada inevitablement es produïsca.

## 7. Recursos

* TrueNAS.
* Clonezilla.
* Duplicati.
* rsync.
* BorgBackup.
* Restic.
* [NIST SP 800-88: Guidelines for Media Sanitization](https://csrc.nist.gov/pubs/sp/800/88/r1/final)
* [INCIBE: esborrament segur de la informació](https://www.incibe.es/sites/default/files/contenidos/guias/doc/guia_ciberseguridad_borrado_seguro_metad_0.pdf)
* [Guia de seguretat en centres de dades de Google](https://www.google.com/about/datacenters/data-security/)

## 8. Relació amb els resultats d'aprenentatge

Aquesta unitat contribueix principalment a:

### 8.1. RA1

Adopta pràctiques segures d'utilització i treball amb sistemes informàtics, reconeixent les vulnerabilitats i les necessitats d'assegurament dels sistemes.

Especialment mitjançant:

* Protecció de la informació i seguretat passiva.
* Còpies de seguretat i recuperació.

### 8.2. RA6

Implementa solucions d'alta disponibilitat mitjançant tècniques de virtualització i sistemes d'emmagatzematge redundant.

Especialment mitjançant:

* RAID, redundància i emmagatzematge.
* NAS i recuperació.
* RPO, RTO i continuïtat del servei.