---
title: "1. Placas Base"
weight: 1
---
# 1. EQUIPS INFORMÀTICS

L'ordinador és una màquina electrònica que rep i processa dades per convertir-les en informació útil. Un ordinador està format, físicament, per nombrosos circuits integrats i molts altres components no tangibles. Per tant, podem dividir un ordinador en dos tipus de components:

- **Maquinari (Hardware)**: components físics i tangibles de l'ordinador. Està compost per tots els elements electrònics i electromecànics. Depenent de la seva ubicació, es poden classificar en dispositius interns (situats dins del xassís de l'ordinador) o externs.
- **Programari (Software)**: components lògics (programes) de l'ordinador que fan que el maquinari pugui funcionar. Els programes estan formats per una sèrie d'instruccions que indiquen a l'ordinador què ha de realitzar en cada moment. Per tant, són els que dirigeixen el funcionament de l'ordinador.

---

## 1.1. ARQUITECTURA D'UN ORDINADOR

Hi ha diversos components principals de l'arquitectura de l'ordinador:

- **CPU**: és la unitat central de processament o microprocessador. Aquesta part s'encarrega d'anar executant les diferents instruccions i les dades que el programari utilitza per a la seva execució. És a dir, és l'encarregada d'executar els programes informàtics, inclòs el sistema operatiu.
- **Bus**: es refereix als components que entrellacen parts de l'ordinador i poden ser de diversos tipus i característiques, com el bus de dades, el bus d'adreces i el bus de control.
- **Memòria principal**: és la memòria RAM, generalment, on es guarden els programes que s'executaran, és a dir, les dades i instruccions per a un procés i que seran reclamades per la CPU.
- **E/S (Entrada/Sortida)**: els ordinadors també necessiten un sistema d'entrada i sortida de la informació, és a dir, ports per on enviar i rebre dades. Això és fonamental per a l'usuari per interactuar amb l'ordinador.
- **Arquitectura Von Neumann**: L'arquitectura de Von Neumann és un model de disseny d'ordinadors proposat per John von Neumann el 1945, i és la base de la majoria dels ordinadors actuals.
- **Unitat de control**: Controla l'ordre d'execució de les instruccions, el flux de dades i les activitats dels perifèrics.
- **Unitat aritmètica i lògica (ALU)**: Processa les dades aritmètiques com sumes, restes, etc., i les operacions lògiques com les portes AND, NOT, XOR, etc.


{{< image src="images/1.png" alt="Description" title="Caption" loading="lazy" >}}

---

## 1.2. PLACA BASE

Una placa base és la plataforma de maquinari on es connecten tots els components interns d'un ordinador. Es tracta d'un complex circuit elèctric proveït de nombroses ranures per poder connectar des de targetes d'expansió com una targeta gràfica, fins a unitats d'emmagatzematge com són discs durs SATA mitjançant cable o SSD en ranures M.2.

El més important és que la placa base és el mitjà o la via per on totes les dades que circulen en un ordinador viatgen d'un punt a un altre.

### Mides disponibles i els seus principals usos de les plaques base:

{{< image src="images/2.png" alt="Description" title="Caption" loading="lazy" >}}


Al mercat podem trobar una sèrie de formats de mida de plaques base que determinaran en gran part la utilitat i la forma d'instal·lar aquestes. Seran els següents:

- **ATX**: serà el factor de forma més habitual en un PC d'escriptori, que en aquest cas s'introduirà en un xassís del mateix tipus ATX o anomenats **middle tower**. Aquesta placa mesura 305×244 mm i, per regla general, compta amb una capacitat per a 7 slots d'expansió.

- **E-ATX**: serà la placa base d'escriptori més gran disponible. Les seves mides són de 305 x 330 mm i pot comptar amb 7 o més ranures d'expansió. El seu ús generalitzat correspon als equips orientats a **Workstation** o escriptori de nivell entusiasta amb xipsets X399 i X299 per a AMD o Intel. Molts dels xassís ATX són compatibles amb aquest format.

- **Micro-ATX**: aquestes plaques són més petites que les ATX, mesurant 244 x 244 mm, sent completament quadrades. Actualment, el seu ús és bastant reduït, ja que no presenten un gran avantatge pel que fa a l'optimització de l'espai, atès que existeixen formats més petits. Tenen espai per a 4 slots d'expansió.

- **Mini-ITX**: aquest format ha anat desplaçant a l'anterior, ja que sí que és ideal per muntar petits ordinadors multimèdia i fins i tot per a *gaming*. Les plaques Mini-ITX mesuren només 170 x 170 mm i són les més esteses de la seva classe. Només tenen una ranura PCIe i dues ranures per a memòries RAM.

### Plataforma d'una placa base i principals fabricants:

La plataforma a la qual pertany una placa base es refereix al *socket* o sòcol que té aquesta. Es tracta del sòcol on es connecta la CPU, i pot ser de diferents tipus en funció de la generació del processador. Les dues plataformes actuals són **INTEL** i **AMD**:

Els sòcols actuals tenen un sistema de connexió anomenat **ZIF (Zero Insertion Force)**, que indica que no necessitem fer força per efectuar la connexió. Es classifiquen en tres tipus genèrics:

### Tipus de sòcols

- **PGA**: *Pin Grid Array* o matriu de reixetes de pins. La connexió s'efectua mitjançant una matriu de pins instal·lats directament a la CPU. Aquests pins han d'encajar en els forats del sòcol de la placa base. PGA és el tipus de sòcol que utilitza AMD (AM4, AM5).

{{< image src="images/3.png" alt="Description" title="Caption" loading="lazy" >}}

- **LGA**: *Land Grid Array* o matriu de contactes en reixeta. La connexió, en aquest cas, es tracta d'una matriu de pins instal·lats al *socket* i de contactes plans a la CPU. La CPU es col·loca sobre el *socket* i, amb un *bracket* que fa pressió sobre el dissipador tèrmic, es fixa el sistema. LGA és utilitzat per **INTEL** (LGA1200, LGA1700).

- **BGA**: *Ball Grid Array* o matriu de reixeta de boles. Bàsicament, és el sistema d'instal·lació de processadors en portàtils, fixant mitjançant soldadura la CPU al *socket* de forma permanent. Aquest tipus de sòcol el fan servir tant **INTEL** com **AMD**.

### Xipset (*Chipset*):

El *chipset* de la vostra placa base es compon de la lletra amb la qual comença i el número que el segueix. La lletra correspon a la gamma, mentre que el número correspon a la generació i, com hem esmentat abans, si és per a Intel o AMD.

#### Exemples de *Chipset*:

- **X570, X670** (sèries X): Aquest és el model més alt de la generació per a AMD. Les seves capacitats estan pensades per a *Gaming Hardcore* i *Overclocking* en processadors i memòries RAM. Multitud de connexions, components de la millor qualitat, jocs de llums múltiples, programes de control i monitorització dels ventiladors i molt més.

- **Z590, Z690, Z790** (sèries Z): Aquest és el model més alt de la generació per a Intel. Inclou millores d'àudio, components més resistents. Permet *Overclocking* tant de processadors com de memòries RAM i l'opció de *MultiGPU* (connexió de 2 targetes gràfiques en sèrie) mitjançant connexió SLI.

- **Intel H310, H410, H470, H510, H570, H610, H670** (sèries H): una opció una mica més cara que les B per a Intel. Són compatibles amb RAID, una mica més resistents, major quantitat de ports USB 3.1.

- **Intel B460, B560, B660, B760** o **AMD B350, B450, B550, B650** (sèries B): Direm d'elles que són les versions més òptimes equilibrant preu i característiques. No permeten el *Overclocking* en processador (per a això necessitaràs un processador desbloquejat o de la sèrie K).


{{< image src="images/5.png" alt="Description" title="Caption" loading="lazy" >}}


Les plaques base poden dur incorporat els receptors per rebre senyal WiFi. Si és el cas, es reflecteix al final del model de placa base. Igualment passa si aquesta placa només admet RAM de tipus DDR4, ja que actualment els models superiors utilitzen DDR5.


{{< image src="images/6.png" alt="Description" title="Caption" loading="lazy" >}}

Les especificacións es troben a les descripcions dels articles

{{< image src="images/7.png" alt="Description" title="Caption" loading="lazy" >}}

### Parts principals d'una placa base:

- **Sòcol del processador (CPU Socket)**: On s'instal·la el microprocessador. Pot ser PGA (AMD), LGA (Intel/AMD AM5) o BGA (soldat, en portàtils).

- **Xipset (*Chipset*)**: Controla la comunicació entre la CPU, la RAM, la GPU, l'emmagatzematge i els perifèrics. Es divideix en *northbridge* (ja integrat a la CPU en models moderns) i *southbridge* (entrada/sortida).

- **Ranures de memòria RAM (DIMM slots)**: Connectors per instal·lar mòduls de memòria (DDR3, DDR4, DDR5).

- **Ranures d'expansió (PCIe / PCI)**: Per instal·lar targetes gràfiques, de so, de xarxa, capturadores, etc.

- **Emmagatzematge**:
  - Ports SATA → discs durs i SSD de 2.5".
  - Ranures M.2 / NVMe → SSD d'alta velocitat.

- **ROM/BIOS/UEFI (firmware)**: Xip de memòria que emmagatzema el programa bàsic d'arrencada i configuració del maquinari.

- **Pila CMOS**: Manté la configuració de la BIOS/UEFI quan el PC està apagat.

- **Connectors d'alimentació**:
  - ATX de 24 pins → alimentació principal de la placa.
  - EPS de 4/8 pins → alimentació del processador.

- **VRM (*Voltage Regulator Module*)**: Reguladors de voltatge que subministren alimentació de forma estable al processador i a la RAM.

- **Xip d'àudio integrat**: Proporciona so (sortida d'altaveus, micròfon, auriculars).

- **Xip de xarxa integrat**: Controlador Ethernet i/o WiFi.

- **Ports posteriors d'E/S (*I/O Shield*)**:
  - USB (2.0, 3.0, 3.2, Type-C).
  - Connectors d'àudio (jack, S/PDIF).
  - Sortides de vídeo (HDMI, DisplayPort, DVI, VGA).
  - Xarxa (RJ-45 Ethernet, WiFi).

- **Connectors interns**:
  - *Headers* USB (2.0 / 3.0 / 3.2) per a ports frontals.
  - Connectors de ventiladors (*FAN*).
  - *Front panel* (botó d'encès, *reset*, LEDs).


{{< image src="images/8.png" alt="Description" title="Caption" loading="lazy" >}}

---
# ACTIVITAT

### ACTIVITAT 1: PLACA BASE

- Identifica les parts d'una placa base.
- Identifica els connectors que té una placa base.
- Omple les taules.
- Entrega la tasca a AULES.