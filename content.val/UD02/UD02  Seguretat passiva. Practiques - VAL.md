
# UD2 - Seguretat passiva: emmagatzematge[cite: 7]

> Protecció de la informació, redundància, còpies de seguretat i recuperació.[cite: 7]

| Dades de la unitat | Informació |[cite: 7]
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |[cite: 7]
| Curs | 2n ASIR |[cite: 7]
| Modalitat | Semipresencial |[cite: 7]
| Durada | 12 hores |[cite: 7]

## Índex[cite: 7]

1. [Fonaments i seguretat física](#1-fonaments-i-seguretat-física)[cite: 7]
2. [Emmagatzematge i fallades](#2-emmagatzematge-i-fallades)[cite: 7]
3. [Redundància i RAID](#3-redundància-i-raid)[cite: 7]
4. [Còpies de seguretat i recuperació](#4-còpies-de-seguretat-i-recuperació)[cite: 7]
5. [Esborrat segur i cicle de vida](#5-esborrat-segur-i-cicle-de-vida)[cite: 7]
6. [Resum](#6-resum)[cite: 7]
7. [Recursos](#7-recursos)[cite: 7]
8. [Relació amb els resultats d'aprenentatge](#8-relació-amb-els-resultats-daprenentatge)[cite: 7]

---

## 1. Fonaments i seguretat física[cite: 7]

### 1.1. Introducció[cite: 7]

La seguretat d'un sistema informàtic no consisteix únicament a impedir que un atacant hi accedisca[cite: 7]. També és necessari estar preparat per a situacions en què es produïsquen fallades[cite: 7].

Un servidor pot patir:[cite: 7]

- L'avaria d'un disc.[cite: 7]
- Una fallada elèctrica.[cite: 7]
- Un error humà.[cite: 7]
- L'eliminació accidental d'arxius.[cite: 7]
- La corrupció d'un sistema d'arxius.[cite: 7]
- Un atac de ransomware.[cite: 7]
- Un incendi o una inundació.[cite: 7]
- El robatori de l'equipament.[cite: 7]
- Una actualització defectuosa.[cite: 7]
- Una fallada de programari.[cite: 7]

Per aquest motiu, les organitzacions necessiten mecanismes que permeten reduir l'impacte dels incidents i recuperar la informació i els serveis[cite: 7].

Aquests mecanismes formen part de la seguretat passiva[cite: 7].

En aquesta unitat estudiarem especialment els sistemes d'emmagatzematge, la redundància mitjançant RAID, les còpies de seguretat, els sistemes NAS, les snapshots i les estratègies de recuperació[cite: 7].

### 1.2. Objectius[cite: 7]

En finalitzar aquesta unitat, l'alumnat serà capaç de:[cite: 7]

- Diferenciar seguretat activa i seguretat passiva.[cite: 7]
- Identificar els principals sistemes d'emmagatzematge.[cite: 7]
- Diferenciar HDD, SSD i NVMe.[cite: 7]
- Identificar els principals tipus de fallades d'emmagatzematge.[cite: 7]
- Comprendre el concepte de redundància.[cite: 7]
- Explicar el funcionament de RAID.[cite: 7]
- Diferenciar RAID 0, RAID 1, RAID 5, RAID 6 i RAID 10.[cite: 7]
- Seleccionar un nivell RAID en funció de les necessitats.[cite: 7]
- Comprendre les limitacions de RAID.[cite: 7]
- Explicar què és una còpia de seguretat.[cite: 7]
- Diferenciar còpies completes, incrementals i diferencials.[cite: 7]
- Dissenyar una estratègia bàsica de còpies.[cite: 7]
- Aplicar la regla 3-2-1.[cite: 7]
- Comprendre els conceptes RPO i RTO.[cite: 7]
- Conéixer sistemes NAS i snapshots.[cite: 7]
- Realitzar i comprovar còpies de seguretat i recuperació.[cite: 7]
- Dissenyar una política d'emmagatzematge i backup.[cite: 7]

### 1.3. Seguretat passiva[cite: 7]

La seguretat passiva engloba les mesures destinades principalment a reduir les conseqüències d'un incident i facilitar la recuperació[cite: 7].

Per exemple, imaginem un servidor que disposa de dos discos[cite: 7].

Si un d'ells falla, una configuració redundant pot permetre que el sistema continue funcionant[cite: 7].

Si a més es disposa de còpies de seguretat, serà possible recuperar la informació fins i tot davant problemes més greus[cite: 7].

Podem representar el concepte de la següent forma:[cite: 7]

                    SEGURETAT
                       │
              ┌────────┴────────┐
              │                 │
            Activa            Passiva
              │                 │
       Prevenir / detectar    Recuperar
       / bloquejar            / continuar

**Exemples de seguretat activa:**[cite: 7]

- Tallafocs.[cite: 7]
- Antivirus.[cite: 7]
- IDS/IPS.[cite: 7]
- Control d'accés.[cite: 7]
- Monitoratge i sistemes de detecció.[cite: 7]

**Exemples de seguretat passiva:**[cite: 7]

- RAID i sistemes redundants.[cite: 7]
- Còpies de seguretat i emmagatzematge extern.[cite: 7]
- SAI i replicació.[cite: 7]
- Plans de recuperació.[cite: 7]

### 1.4. Seguretat física i CPD[cite: 7]

Un centre de processament de dades (CPD) concentra servidors, xarxes i emmagatzematge crítics[cite: 7]. Centralitzar els equips facilita el control d'accessos, la climatització, el manteniment i les comunicacions, però també exigeix planificar els riscos físics i ambientals[cite: 7]. La ubicació ha d'evitar zones amb elevat risc d'inundació, incendi, vibracions o accessos no controlats, i la sala ha de comptar amb procediments documentats per a recuperar els serveis davant una incidència[cite: 7].

Les mesures habituals inclouen control d'accés mitjançant credencials o biometria, videovigilància, detecció i extinció d'incendis, fals sòl per a cablejat i ventilació, i control de temperatura i humitat[cite: 7]. En un CPD amb racks, els passadissos freds aporten aire a la part frontal dels equips i els passadissos calents arrepleguen l'aire d'eixida; aquesta separació redueix el sobreescalfament i millora l'eficiència energètica[cite: 7].

La continuïtat també requereix alimentació i comunicacions redundants[cite: 7]. Un SAI proporciona temps per a un apagat controlat durant un tall breu; un generador pot cobrir interrupcions prolongades[cite: 7]. Per a serveis crítics, es poden contractar enllaços d'Internet amb proveïdors i rutes diferents[cite: 7]. Un centre de suport, ubicat a suficient distància del CPD principal, permet restaurar serveis si una catàstrofe afecta la ubicació primària[cite: 7]. Per exemple, una empresa pot replicar la base de dades i conservar còpies verificades en un segon centre, provant periòdicament el procediment de commutació[cite: 7].

## 2. Emmagatzematge i fallades[cite: 7]

### 2.1. Emmagatzematge de la informació[cite: 7]

La informació d'una organització es pot emmagatzemar en diferents dispositius i sistemes[cite: 7].

Entre els més habituals trobem:[cite: 7]

HDD.[cite: 7]
SSD.[cite: 7]
NVMe.[cite: 7]
NAS.[cite: 7]
SAN.[cite: 7]
Cabines d'emmagatzematge.[cite: 7]
Sistemes distribuïts.[cite: 7]

La tria depén de factors com:[cite: 7]

Capacitat.[cite: 7]
Rendiment.[cite: 7]
Cost.[cite: 7]
Fiabilitat.[cite: 7]
Disponibilitat.[cite: 7]
Redundància.[cite: 7]
Tipus d'informació.[cite: 7]

També importa la forma d'accés: un sistema de còpies històriques pot utilitzar cinta, que ofereix gran capacitat a baix cost però accés seqüencial; una base de dades necessita normalment accés aleatori i baixa latència, per la qual cosa pot requerir SSD o NVMe[cite: 7]. Per a compartir documents entre diversos equips sol ser suficient un NAS amb accés a nivell d'arxiu, mentre que un entorn de virtualització pot necessitar emmagatzematge de blocs mitjançant SAN o una plataforma definida per programari[cite: 7].

Per exemple, una petita empresa pot combinar SSD per a les màquines virtuals que executen aplicacions, HDD en un NAS per a documents compartits i emmagatzematge extern per a una còpia de seguretat[cite: 7]. No existeix una tecnologia universalment millor: la solució adequada respon als requisits de rendiment, disponibilitat, pressupost i protecció de les dades[cite: 7].

### 2.2. Discos HDD[cite: 7]

Els discos HDD utilitzen plats magnètics i capçals mecànics per a emmagatzemar i recuperar informació[cite: 7].

Una representació simplificada seria:[cite: 7]

       HDD
 ┌───────────────┐
 │   Plat        │
 │      ↓        │
 │  ──────────   │
 │      ↑        │
 │   Capçal      │
 └───────────────┘

Avantatges[cite: 7]
Gran capacitat.[cite: 7]
Preu reduït per GB.[cite: 7]
Adequats per a grans volums d'informació.[cite: 7]
Interessants per a emmagatzematge de backup.[cite: 7]

Inconvenients[cite: 7]
Components mecànics.[cite: 7]
Major latència.[cite: 7]
Menor rendiment que els SSD en determinats escenaris.[cite: 7]
Sensibilitat a colps i vibracions.[cite: 7]

### 2.3. Discos SSD[cite: 7]

Els SSD emmagatzemen la informació en memòria flash[cite: 7].

No utilitzen parts mecàniques mòbils[cite: 7].

Avantatges[cite: 7]
Alta velocitat.[cite: 7]
Baixa latència.[cite: 7]
Menor soroll.[cite: 7]
Major resistència enfront de vibracions.[cite: 7]
Bon rendiment per a sistemes operatius i aplicacions.[cite: 7]

Inconvenients[cite: 7]
Preu per GB generalment superior.[cite: 7]
Desgast de les cel·les.[cite: 7]
Recuperació de dades potencialment complexa davant determinades fallades.[cite: 7]

Els SSD són habituals en:[cite: 7]

Servidors.[cite: 7]
Ordinadors.[cite: 7]
Màquines virtuals.[cite: 7]
Bases de dades.[cite: 7]
Sistemes d'alt rendiment.[cite: 7]

### 2.4. NVMe[cite: 7]

NVMe és un protocol dissenyat específicament per a dispositius d'emmagatzematge no volàtil d'alta velocitat[cite: 7].

Els dispositius NVMe solen utilitzar PCI Express[cite: 7].

Comparats amb dispositius SATA tradicionals, poden proporcionar:[cite: 7]

Major ample de banda.[cite: 7]
Menor latència.[cite: 7]
Major nombre d'operacions d'entrada/eixida.[cite: 7]

Són especialment interessants per a:[cite: 7]

Bases de dades.[cite: 7]
Virtualització.[cite: 7]
Servidors.[cite: 7]
Aplicacions amb moltes operacions de disc.[cite: 7]

### 2.5. Fallades d'emmagatzematge[cite: 7]

Els problemes d'emmagatzematge poden tindre diferents orígens[cite: 7].

#### 2.5.1. Fallada física[cite: 7]

Exemple:[cite: 7]

El disc deixa de funcionar[cite: 7].

Es pot produir per:[cite: 7]

Desgast.[cite: 7]
Temperatura.[cite: 7]
Fallada electrònica.[cite: 7]
Fallada mecànica.[cite: 7]
Danys físics.[cite: 7]

#### 2.5.2. Fallada lògica[cite: 7]

El dispositiu continua funcionant, però la informació o el sistema d'arxius presenta problemes[cite: 7].

Exemples:[cite: 7]

Corrupció del sistema d'arxius.[cite: 7]
Partició danyada.[cite: 7]
Eliminació accidental.[cite: 7]
Metadades corruptes.[cite: 7]

#### 2.5.3. Error humà[cite: 7]

Un administrador pot executar accidentalment:[cite: 7]

rm -rf

sobre el directori equivocat[cite: 7].

També es pot produir:[cite: 7]

Sobreescriptura d'arxius.[cite: 7]
Eliminació de bases de dades.[cite: 7]
Configuració incorrecta.[cite: 7]
Formatat accidental.[cite: 7]

#### 2.5.4. Malware[cite: 7]

Un ransomware pot xifrar els arxius disponibles[cite: 7].

Per exemple:[cite: 7]

documento1.docx
      ↓
documento1.docx.cifrado

Si el sistema de backup està connectat i accessible des del mateix entorn, també es podria veure afectat[cite: 7].

#### 2.5.5. Catàstrofes físiques[cite: 7]

Alguns riscos són:[cite: 7]

Incendi.[cite: 7]
Inundació.[cite: 7]
Robatori.[cite: 7]
Sobretensió.[cite: 7]
Fallada de refrigeració.[cite: 7]

Per això és recomanable disposar de còpies en una ubicació diferent[cite: 7].

### 2.6. Fiabilitat i monitoratge de l'emmagatzematge[cite: 7]

En seleccionar emmagatzematge s'han de valorar capacitat, rendiment, cost, consum, durabilitat i fiabilitat[cite: 7]. El **MTBF** expressa una estimació estadística del temps mitjà entre fallades d'una població d'unitats, mentre que l'**AFR** representa la taxa anualitzada de fallades[cite: 7]. Cap mètrica prediu el moment exacte en què fallarà un disc concret; per això, les decisions s'han de complementar amb redundància, còpies de seguretat i supervisió[cite: 7].

La tecnologia SMART permet consultar indicadors de salut d'HDD i SSD, com a sectors reassignats, errors de lectura, temperatura i, en SSD, desgast de les cel·les[cite: 7]. Una alerta SMART ha de provocar la revisió i substitució planificada de la unitat, però la seua absència no garanteix que no vaja a fallar[cite: 7]. Per exemple, si un servidor detecta sectors reassignats creixents en un disc d'un RAID 5, l'administrador ha de substituir-lo abans que coincidisca amb una altra fallada durant la reconstrucció[cite: 7].

| Necessitat | Opció habitual | Exemple |[cite: 7]
| --- | --- | --- |
| Gran capacitat a baix cost | HDD o cinta per a arxivament. | Còpies històriques mensuals. |[cite: 7]
| Baixa latència i moltes operacions d'E/E | SSD NVMe. | Base de dades o màquines virtuals. |[cite: 7]
| Compartició d'arxius | NAS amb SMB/NFS. | Documentació d'un departament. |[cite: 7]
| Accés per blocs d'alt rendiment | SAN o emmagatzematge definit per programari. | Clúster de virtualització. |[cite: 7]

## 3. Redundància i RAID[cite: 7]

### 3.1. Redundància[cite: 7]

La redundància consisteix a disposar d'elements addicionals que permeten mantindre el servei quan un d'ells falla[cite: 7].

Exemple:[cite: 7]

Servidor
 ├── Disc 1
 └── Disc 2

Si tots dos contenen informació redundant i un falla, el sistema pot continuar funcionant[cite: 7].

La redundància es pot aplicar a:[cite: 7]

Discos.[cite: 7]
Fonts d'alimentació.[cite: 7]
Servidors.[cite: 7]
Xarxes.[cite: 7]
Connexions a Internet.[cite: 7]
Sistemes d'emmagatzematge.[cite: 7]

### 3.2. RAID[cite: 7]

RAID — Redundant Array of Independent Disks[cite: 7]

RAID permet combinar diversos discos per a aconseguir diferents objectius:[cite: 7]

Major rendiment.[cite: 7]
Redundància.[cite: 7]
Tolerància a fallades.[cite: 7]
Major capacitat útil.[cite: 7]

No obstant això, RAID no és un sistema de backup[cite: 7].

Aquesta diferència ha de quedar clara:[cite: 7]

RAID
↓
Protecció principalment enfront de fallades de discos

BACKUP
↓
Protecció enfront de pèrdua, modificació o destrucció d'informació

### 3.3. RAID 0[cite: 7]

RAID 0 distribueix les dades entre diversos discos mitjançant una tècnica denominada striping[cite: 7].

Exemple:[cite: 7]

       RAID 0

Disc 1        Disc 2
--------      --------
Bloc A        Bloc B
Bloc C        Bloc D
Bloc E        Bloc F

Avantatge[cite: 7]

Pot augmentar considerablement el rendiment[cite: 7].

Inconvenient[cite: 7]

No existeix redundància[cite: 7].

Si falla un dels discos:[cite: 7]

Disc 1 → OK
Disc 2 → FALLA

es pot perdre el conjunt complet d'informació[cite: 7].

Ús[cite: 7]

Es pot utilitzar quan el rendiment és prioritari i les dades es poden reconstruir des d'una altra font[cite: 7].

### 3.4. RAID 1[cite: 7]

RAID 1 utilitza mirroring, és a dir, manté una còpia de les dades en un altre disc[cite: 7].

Disc 1        Disc 2

Dades A       Dades A
Dades B       Dades B
Dades C       Dades C

Si un disc falla:[cite: 7]

Disc 1 → FALLA
Disc 2 → OK

la informació continua disponible[cite: 7].

Avantatges[cite: 7]
Senzill.[cite: 7]
Bona tolerància a fallades.[cite: 7]
Recuperació relativament senzilla.[cite: 7]

Inconvenient[cite: 7]

La capacitat útil és aproximadament la d'un únic disc[cite: 7].

Per exemple:[cite: 7]

2 × 2 TB

proporcionen aproximadament:[cite: 7]

2 TB útils

### 3.5. RAID 5[cite: 7]

RAID 5 combina distribució de dades i paritat[cite: 7].

Necessita almenys tres discos[cite: 7].

Una representació simplificada:[cite: 7]

Disc 1   Disc 2   Disc 3

Dades    Dades    Paritat
Dades    Paritat  Dades
Paritat  Dades    Dades

La informació de paritat permet reconstruir les dades quan falla un dels discos[cite: 7].

Avantatges[cite: 7]
Tolerància a una fallada.[cite: 7]
Bon aprofitament de la capacitat.[cite: 7]
Pot proporcionar un equilibri entre rendiment, capacitat i redundància.[cite: 7]

Inconvenients[cite: 7]
La reconstrucció pot ser lenta.[cite: 7]
Durant la reconstrucció existeix una situació de major risc.[cite: 7]
Les operacions d'escriptura tenen un cost addicional a causa de la paritat.[cite: 7]

### 3.6. RAID 6[cite: 7]

RAID 6 utilitza doble paritat[cite: 7].

Necessita almenys quatre discos i pot suportar la fallada simultània de dos unitats[cite: 7].

Disc 1   Disc 2   Disc 3   Disc 4
Dades    Dades    Paritat  Paritat
Dades    Paritat  Dades    Paritat
Paritat  Dades    Dades    Paritat

És apropiat per a sistemes amb grans quantitats d'emmagatzematge on es desitja una major tolerància a fallades[cite: 7].

### 3.7. RAID 10[cite: 7]

RAID 10 combina:[cite: 7]

RAID 1 → redundància.[cite: 7]
RAID 0 → distribució.[cite: 7]

Exemple:[cite: 7]

          RAID 10

       ┌─────────────┐
       │             │
    RAID 1        RAID 1
    D1 + D2       D3 + D4
       │             │
       └──── RAID 0 ─┘

Proporciona:[cite: 7]

Bon rendiment.[cite: 7]
Redundància.[cite: 7]
Bon comportament en sistemes amb moltes operacions d'entrada/eixida.[cite: 7]

El nombre de discos necessaris és superior al de RAID 1[cite: 7].

### 3.8. Comparació de RAID[cite: 7]

| Nivell | Discos mínims | Redundància | Tolerància | Característica principal |[cite: 7]
| --- | ---: | --- | --- | --- |
| RAID 0 | 2 | No | Cap | Rendiment |[cite: 7]
| RAID 1 | 2 | Sí | 1 disc | Simplicitat |[cite: 7]
| RAID 5 | 3 | Sí | 1 disc | Capacitat + redundància |[cite: 7]
| RAID 6 | 4 | Sí | 2 discos | Major tolerància |[cite: 7]
| RAID 10 | 4 | Sí | Depén del patró de fallades | Rendiment + redundància |[cite: 7]

### 3.9. RAID no és backup[cite: 7]

Aquest concepte és especialment important[cite: 7].

Suposem que tenim:[cite: 7]

Servidor
   ↓
RAID 1
   ↓
Disc A + Disc B

Un usuari elimina accidentalment:[cite: 7]

clientes.xlsx

L'eliminació es replica en tots dos discos[cite: 7].

Per tant:[cite: 7]

Disc A → arxiu eliminat
Disc B → arxiu eliminat

RAID no permet recuperar automàticament l'arxiu[cite: 7].

En canvi, un backup podria contindre una versió anterior:[cite: 7]

Backup
   ↓
clientes.xlsx
   ↓
Recuperació

Per això:[cite: 7]

RAID protegeix principalment enfront de determinades fallades de maquinari; el backup protegeix la informació enfront de molts tipus de pèrdua o alteració[cite: 7].

## 4. Còpies de seguretat i recuperació[cite: 7]

### 4.1. Còpies de seguretat[cite: 7]

Una còpia de seguretat és una còpia d'informació emmagatzemada en un medi alternatiu que es pot utilitzar per a recuperar les dades originals després d'una pèrdua, dany, corrupció o incident[cite: 7]. Ha de protegir dades, configuracions i, quan siga necessari, imatges de sistemes complets[cite: 7]. Una imatge facilita la restauració d'un equip després d'una fallada greu; en canvi, una còpia d'arxius permet recuperar selectivament un document sense restaurar tot el sistema[cite: 7].

Una estratègia de backup ha de definir:[cite: 7]

Quina informació copiar.[cite: 7]
Quan copiar-la.[cite: 7]
On emmagatzemar-la.[cite: 7]
Quant de temps conservar-la.[cite: 7]
Qui hi pot accedir.[cite: 7]
Com protegir-la.[cite: 7]
Com restaurar-la.[cite: 7]
Com comprovar que funciona.[cite: 7]

Les còpies s'han d'automatitzar sempre que siga possible, xifrar-se quan contenen informació sensible i supervisar-se mitjançant avisos d'èxit o error[cite: 7]. Una planificació habitual pot combinar una còpia completa semanal, còpies incrementals diàries i una retenció diferenciada per a versions diàries, mensuals i anuals[cite: 7]. La periodicitat ha de respondre al RPO: si una organització només accepta perdre fins a quatre hores de treball, una còpia diària no serà suficient[cite: 7].

La restauració és la prova definitiva d'una estratègia[cite: 7]. Per exemple, després de configurar una còpia programada d'una base de dades, l'administrador ha de restaurar-la en un entorn de proves, comprovar que obri correctament i mesurar el temps emprat[cite: 7]. Eixa evidència permet confirmar si el procediment compleix el RTO establit[cite: 7].

### 4.2. Backup complet[cite: 7]

Una còpia completa conté tota la informació seleccionada[cite: 7].

Exemple:[cite: 7]

Diumenge
Backup complet → 500 GB

Avantatges:[cite: 7]

Restauració senzilla.[cite: 7]
Independència respecte d'altres còpies.[cite: 7]

Inconvenients:[cite: 7]

Consumeix més emmagatzematge.[cite: 7]
Pot tardar més temps.[cite: 7]

### 4.3. Backup incremental[cite: 7]

Una còpia incremental conté els canvis realitzats des de l'última còpia[cite: 7].

Exemple:[cite: 7]

Diumenge
Completa

Dilluns
Canvis del dilluns

Dimarts
Canvis del dimarts

Dimecres
Canvis del dimecres

Avantatge:[cite: 7]

Menor consum d'espai[cite: 7].

Inconvenient:[cite: 7]

Per a realitzar una recuperació completa pot ser necessari disposar de:[cite: 7]

Backup complet
+
Incremental dilluns
+
Incremental dimarts
+
Incremental dimecres

### 4.4. Backup diferencial[cite: 7]

La còpia diferencial emmagatzema els canvis realitzats des de l'última còpia completa[cite: 7].

Exemple:[cite: 7]

Diumenge
Completa

Dilluns
Canvis des del diumenge

Dimarts
Canvis des del diumenge + dilluns

Dimecres
Canvis des del diumenge + dilluns + dimarts

Per a recuperar l'estat del dimecres normalment necessitem:[cite: 7]

Backup complet
+
Backup diferencial del dimecres

### 4.5. Comparació de còpies[cite: 7]

| Tipus | Espai | Velocitat de backup | Recuperació |[cite: 7]
| --- | --- | --- | --- |
| Completa | Alt | Menor | Molt senzilla |[cite: 7]
| Incremental | Baix | Alta | Més complexa |[cite: 7]
| Diferencial | Mitjà | Intermèdia | Senzilla |[cite: 7]

### 4.6. Regla 3-2-1[cite: 7]

La regla 3-2-1 és una estratègia senzilla per a millorar la protecció dels backups[cite: 7].

Consisteix a mantindre:[cite: 7]

3 còpies de la informació[cite: 7]

2 suports diferents[cite: 7]

1 còpia fora de la ubicació principal[cite: 7]

Exemple:[cite: 7]

                 DADES
                   │
          ┌────────┼────────┐
          │        │        │
       Original   NAS     Cloud
                         / ubicació externa

Açò permet reduir el risc que un únic incident destruïsca totes les còpies[cite: 7].

### 4.7. Backup i ransomware[cite: 7]

Els sistemes de backup també s'han de protegir[cite: 7].

Imaginem:[cite: 7]

Servidor
    ↓
Backup NAS

Si l'atacant aconsegueix privilegis suficients sobre tots dos sistemes, podria xifrar:[cite: 7]

Servidor → xifrat
NAS      → xifrat

Per això hem d'aplicar mesures addicionals:[cite: 7]

Separació de comptes.[cite: 7]
Contrasenyes robustes.[cite: 7]
MFA.[cite: 7]
Permisos mínims.[cite: 7]
Segmentació de xarxa.[cite: 7]
Versionat.[cite: 7]
Còpies desconnectades quan siga possible.[cite: 7]
Emmagatzematge immutable.[cite: 7]
Còpies externes.[cite: 7]
Proves de recuperació.[cite: 7]

### 4.8. RPO[cite: 7]

RPO — Recovery Point Objective[cite: 7]

El RPO indica la quantitat màxima d'informació que una organització està disposada a perdre[cite: 7].

Exemple:[cite: 7]

RPO = 4 hores

Significa que l'estratègia ha de permetre recuperar informació amb una antiguitat màxima objectiu d'unes quatre hores[cite: 7].

Com menor siga el RPO:[cite: 7]

RPO petit
    ↓
Més freqüència de còpia/replicació
    ↓
Major cost i complexitat

### 4.9. RTO[cite: 7]

RTO — Recovery Time Objective[cite: 7]

El RTO indica quant de temps pot tardar com a màxim la recuperació d'un servei[cite: 7].

Exemple:[cite: 7]

RTO = 8 hores

L'organització ha de disposar de procediments i recursos adequats per a intentar recuperar el servei dins d'eixe objectiu[cite: 7].

### 4.10. Diferència entre RPO i RTO[cite: 7]

| Concepte | Pregunta |[cite: 7]
| --- | --- |
| RPO | Quanta informació podem perdre? |[cite: 7]
| RTO | Quant de temps podem estar sense servei? |[cite: 7]

Exemple:[cite: 7]

Una empresa estableix:[cite: 7]

RPO = 1 hora
RTO = 4 hores

Per tant:[cite: 7]

S'intenta limitar la pèrdua d'informació a una hora[cite: 7].
S'intenta recuperar el servei en quatre hores[cite: 7].

### 4.11. NAS[cite: 7]

Un NAS — Network Attached Storage és un dispositiu d'emmagatzematge connectat a una xarxa[cite: 7].

Permet proporcionar emmagatzematge centralitzat a diferents equips[cite: 7].

             ┌──── PC 1
             │
Xarxa ───────┼──── PC 2
             │
             ├──── PC 3
             │
             └──── NAS

Un NAS pot proporcionar:[cite: 7]

Carpetes compartides.[cite: 7]
Usuaris.[cite: 7]
Permisos.[cite: 7]
RAID.[cite: 7]
Snapshots.[cite: 7]
Còpies de seguretat.[cite: 7]
Replicació.[cite: 7]
Serveis de xarxa.[cite: 7]

### 4.12. NAS enfront d'emmagatzematge local[cite: 7]
Emmagatzematge local[cite: 7]
PC
 ↓
Disc

Les dades estan directament en l'equip[cite: 7].

NAS[cite: 7]
PC ───┐
PC ───┼── Xarxa ── NAS
PC ───┘

Les dades es centralitzen en un sistema d'emmagatzematge accessible mitjançant xarxa[cite: 7].

Això facilita:[cite: 7]

Administració.[cite: 7]
Compartició.[cite: 7]
Backup.[cite: 7]
Control d'accés.[cite: 7]

### 4.13. TrueNAS[cite: 7]

TrueNAS és una plataforma utilitzada per a implementar sistemes d'emmagatzematge en xarxa[cite: 7].

Permet treballar amb:[cite: 7]

Discos.[cite: 7]
Pools d'emmagatzematge.[cite: 7]
Sistemes d'arxius.[cite: 7]
Usuaris.[cite: 7]
Permisos.[cite: 7]
Comparticions.[cite: 7]
Snapshots.[cite: 7]
Replicació.[cite: 7]
Serveis de xarxa.[cite: 7]

En un entorn de proves d'ASIR es pot utilitzar per a practicar:[cite: 7]

RAID.[cite: 7]
Emmagatzematge.[cite: 7]
Compartició d'arxius.[cite: 7]
Backup.[cite: 7]
Snapshots.[cite: 7]
Recuperació.[cite: 7]

### 4.14. Snapshots[cite: 7]

Una snapshot representa l'estat d'un sistema d'arxius o emmagatzematge en un moment determinat[cite: 7].

Exemple:[cite: 7]

10:00 → Snapshot 1
12:00 → Snapshot 2
14:00 → Snapshot 3

Si un usuari modifica un arxiu a les 14:30, pot ser possible recuperar una versió anterior mitjançant una snapshot[cite: 7].

Les snapshots són especialment útils per a:[cite: 7]

Errors humans.[cite: 7]
Recuperació ràpida.[cite: 7]
Versionat.[cite: 7]
Protecció enfront de determinades modificacions.[cite: 7]

Però:[cite: 7]

Una snapshot no substitueix necessàriament una còpia de seguretat[cite: 7].

Si totes les snapshots estan emmagatzemades en el mateix dispositiu que les dades i aquest dispositiu es destrueix, també es poden perdre les snapshots[cite: 7].

### 4.15. Recuperació d'informació[cite: 7]

Una estratègia de backup ha d'incloure procediments de recuperació[cite: 7].

Procés bàsic:[cite: 7]

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

### 4.16. Proves de restauració[cite: 7]

No n'hi ha prou amb realitzar còpies[cite: 7].

És necessari comprovar periòdicament que es poden restaurar[cite: 7].

Una prova pot consistir a:[cite: 7]

Seleccionar una còpia.[cite: 7]
Restaurar alguns arxius.[cite: 7]
Comprovar el seu contingut.[cite: 7]
Restaurar una màquina virtual.[cite: 7]
Comprovar una base de dades.[cite: 7]
Mesurar el temps de recuperació.[cite: 7]
Registrar els resultats.[cite: 7]

Una còpia que mai ha sigut provada suposa un risc[cite: 7].

### 4.17. Política de backup[cite: 7]

Una política de còpies hauria de definir clarament:[cite: 7]

Informació protegida[cite: 7]

Exemple:[cite: 7]

Bases de dades.[cite: 7]
Documents.[cite: 7]
Configuracions.[cite: 7]
Màquines virtuals.[cite: 7]
Servidors.[cite: 7]

Freqüència[cite: 7]

Exemple:[cite: 7]

Backup complet → semanal
Backup incremental → diari

Retenció[cite: 7]

Exemple:[cite: 7]

Diaris → 30 dies
Semanals → 3 mesos
Mensuals → 1 any

Destins[cite: 7]
NAS.[cite: 7]
Servidor de backup.[cite: 7]
Cloud.[cite: 7]
Ubicació externa.[cite: 7]

### 4.18. Eines de backup[cite: 7]

#### rsync[cite: 7]

rsync permet sincronitzar arxius i directoris[cite: 7].

Exemple:[cite: 7]

rsync -av /datos/ /backup/datos/

Es pot utilitzar per a realitzar sincronitzacions locals o remotes[cite: 7].

#### Clonezilla[cite: 7]

Clonezilla permet treballar amb imatges i clonacions de discos i particions[cite: 7].

Es pot utilitzar per a:[cite: 7]

Clonar equips.[cite: 7]
Crear imatges.[cite: 7]
Restaurar sistemes.[cite: 7]
Preparar desplegaments.[cite: 7]

#### Duplicati[cite: 7]

Duplicati permet crear còpies programades i pot utilitzar diferents destins d'emmagatzematge[cite: 7].

Entre les seues característiques es troben:[cite: 7]

Programació.[cite: 7]
Versionat.[cite: 7]
Xifrat.[cite: 7]
Destins locals i remots.[cite: 7]

## 5. Esborrat segur i cicle de vida[cite: 7]

### 5.1. Esborrat segur d'informació[cite: 7]

Eliminar un arxiu o formatar ràpidament una unitat no garanteix que les dades no puguen recuperar-se[cite: 7]. El mètode adequat depén del medi, del nivell de confidencialitat i de la reutilització prevista[cite: 7]. En HDD, la sobreescriptura gestionada correctament pot ser eficaç perquè els sectors es poden escriure de forma directa[cite: 7]. En SSD, el *wear leveling* i l'espai reservat pel controlador impedeixen assegurar la sobreescriptura d'una ubicació concreta; es recomanen les ordes de sanejament del fabricant, com **ATA Secure Erase**, o l'esborrat criptogràfic mitjançant destrucció de claus quan la unitat es va xifrar des de l'inici[cite: 7].

La guia [NIST SP 800-88](https://csrc.nist.gov/pubs/sp/800/88/r1/final) diferencia tres nivells: **clear**, que elimina les dades de manera que no siguen recuperables amb tècniques habituals; **purge**, que aplica un sanejament més profund; i **destroy**, que inutilitza físicament el suport[cite: 7]. L'organització ha de definir quin mètode empra, qui l'autoritza i quina evidència conserva[cite: 7]. Per exemple, abans de reciclar un portàtil que contenia informació personal, es pot verificar que estava xifrat, eliminar de forma segura les seues claus, restablir-lo i registrar el número de sèrie, el responsable i el resultat del procés[cite: 7].

En serveis cloud, el client no controla directament el maquinari i ha de revisar les condicions d'eliminació, retenció i còpies del proveïdor[cite: 7]. El xifrat, una política de retenció definida, contractes adequats i el registre de les operacions ajuden a complir les obligacions de protecció de dades[cite: 7]. L'esborrat segur també s'aplica a dispositius mòbils: s'han d'eliminar els comptes vinculats, comprovar la sincronització en el núvol i utilitzar el restabliment de fàbrica amb el xifrat habilitat[cite: 7].

## 6. Resum[cite: 7]

En aquesta unitat hem estudiat com protegir la informació enfront de fallades i pèrdues[cite: 7].

Els conceptes fonamentals són:[cite: 7]

- Seguretat passiva i protecció física.[cite: 7]
- Emmagatzematge en HDD, SSD i NVMe.[cite: 7]
- Redundància i RAID.[cite: 7]
- Backup, NAS, snapshots i recuperació.[cite: 7]
- RPO, RTO i proves de restauració.[cite: 7]
- Esborrat segur i cicle de vida del suport.[cite: 7]

Els nivells RAID permeten millorar la disponibilitat o el rendiment, però no substitueixen les còpies de seguretat[cite: 7].

Una estratègia professional ha de combinar diferents mecanismes:[cite: 7]

        INFORMACIÓ
             │
     ┌───────┴────────┐
     │                │
 Redundància         Backup
     │                │
    RAID        3-2-1 / extern
     │                │
     └───────┬────────┘
             │
        RECUPERACIÓ

La idea fonamental d'aquesta unitat és:[cite: 7]

No hem de preguntar-nos solament com evitar que les dades es perden, sinó també com recuperar-les quan la fallada inevitablement es produïsca[cite: 7].

## 7. Recursos[cite: 7]

- TrueNAS.[cite: 7]
- Clonezilla.[cite: 7]
- Duplicati.[cite: 7]
- rsync.[cite: 7]
- BorgBackup.[cite: 7]
- Restic.[cite: 7]
- [NIST SP 800-88: Guidelines for Media Sanitization](https://csrc.nist.gov/pubs/sp/800/88/r1/final)[cite: 7]
- [INCIBE: borrado seguro de información](https://www.incibe.es/sites/default/files/contenidos/guias/doc/guia_ciberseguridad_borrado_seguro_metad_0.pdf)[cite: 7]
- [Guía de seguridad en centros de datos de Google](https://www.google.com/about/datacenters/data-security/)[cite: 7]

## 8. Relació amb els resultats d'aprenentatge[cite: 7]

Aquesta unitat contribueix principalment a:[cite: 7]

### 8.1. RA1[cite: 7]

Adopta pràctiques segures d'utilització i treball amb sistemes informàtics, reconeixent les vulnerabilitats i les necessitats d'assegurament dels sistemes[cite: 7].

Especialment mitjançant:[cite: 7]

- Protecció de la informació i seguretat passiva.[cite: 7]
- Còpies de seguretat i recuperació.[cite: 7]

### 8.2. RA6[cite: 7]

Implementa solucions d'alta disponibilitat mitjançant tècniques de virtualització i sistemes d'emmagatzematge redundant[cite: 7].

Especialment mitjançant:[cite: 7]

- RAID, redundància i emmagatzematge.[cite: 7]
- NAS i recuperació.[cite: 7]
- RPO, RTO i continuïtat del servei.[cite: 7]

```