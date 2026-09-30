---
title: "1. Introducció a la seguretat. Pràctiques"
weight: 1
---
# UD01 - Introducció a la seguretat informàtica

> Conceptes fonamentals per a la protecció de sistemes i informació.

| Dades de la unitat | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Durada | 14 hores |

## Índex

1. [Fonaments i principis de seguretat](#1-fonaments-i-principis-de-seguretat)
2. [Actius, riscos i tipus de seguretat](#2-actius-riscos-i-tipus-de-seguretat)
3. [Amenaces i vulnerabilitats](#3-amenaces-i-vulnerabilitats)
4. [Mesures de protecció i polítiques](#4-mesures-de-protecció-i-polítiques)
5. [Gestió, resposta i compliment](#5-gestió-resposta-i-compliment)
6. [Resum](#6-resum)
7. [Recursos](#7-recursos)
8. [Relació amb els resultats d'aprenentatge](#8-relació-amb-els-resultats-daprenentatge)

---

## 1. Fonaments i principis de seguretat

### 1.1. Introducció

La informació constitueix un dels actius més importants de qualsevol organització. Empreses, administracions i usuaris particulars emmagatzemen i processen grans quantitats d'informació mitjançant ordinadors, servidors, dispositius mòbils, xarxes i serveis a Internet.

La dependència dels sistemes informàtics fa que una incidència de seguretat puga provocar conseqüències importants:

* Pèrdua d'informació.
* Robatori de dades.
* Interrupció de serveis.
* Danys econòmics.
* Pèrdua de confiança de clients i usuaris.
* Incompliment d'obligacions legals.
* Danys en la imatge de l'organització.

La seguretat informàtica comprén el conjunt de tècniques, procediments, eines i mesures destinades a protegir els sistemes d'informació enfront d'amenaces.

La seguretat s'ha de gestionar abans que ocorrega un incident. Una organització que depén de les seues aplicacions, comunicacions i dades necessita identificar quins actius són essencials, què pot fallar i quant de temps pot estar sense cada servei. El primer pas és realitzar una anàlisi de riscos que relacione actius, amenaces, vulnerabilitats, probabilitat i impacte; després s'apliquen controls proporcionats al valor de l'actiu i al risc acceptable.

La seguretat absoluta no existeix. Els sistemes incorporen programari, maquinari, xarxes, proveïdors i persones, tots ells subjectes a errors, canvis i noves amenaces. A més, reforçar un control pot tindre cost econòmic o dificultar l'ús d'un servei. Per aquest motiu, la seguretat es basa en la millora contínua: avaluar, protegir, comprovar els resultats i ajustar les mesures quan canvie l'organització o el seu entorn.

En aquesta unitat s'estudiaran els conceptes fonamentals que permetran comprendre la resta del mòdul.

---

![Panells i codis que representen l'operació de seguretat informàtica](images/ud1/security-operations.jpg)

*Figura 1. La seguretat protegeix informació, sistemes, xarxes i persones mitjançant controls coordinats.*

### 1.2. Objectius

En finalitzar aquesta unitat, l'alumnat haurà de ser capaç de:

* Identificar els principals conceptes relacionats amb la seguretat informàtica.
* Diferenciar actiu, amenaça, vulnerabilitat i risc.
* Comprendre els principis fonamentals de la seguretat de la informació.
* Identificar amenaces físiques i lògiques.
* Reconéixer diferents tipus d'atacs informàtics.
* Analitzar vulnerabilitats de sistemes i aplicacions.
* Identificar mesures de seguretat preventives i correctives.
* Comprendre la importància de les polítiques de seguretat.
* Analitzar riscos bàsics d'una infraestructura informàtica.
* Conéixer les fases generals d'actuació davant un incident.
* Introduir-se en les auditories i l'anàlisi forense.
* Valorar la importància de la seguretat des del punt de vista tècnic, organitzatiu i legal.

---

### 1.3. Conceptes fonamentals

#### 1.3.1. Seguretat informàtica

La seguretat informàtica és el conjunt de mesures destinades a protegir els sistemes informàtics, les xarxes, els dispositius, les aplicacions i la informació enfront d'accessos no autoritzats, alteracions, pèrdues o interrupcions.

La seguretat no consisteix únicament a instal·lar un antivirus o un tallafocs.

Una infraestructura segura requereix combinar:

* Mesures tècniques.
* Mesures físiques.
* Mesures organitzatives.
* Formació dels usuaris.
* Procediments d'actuació.
* Monitoratge.
* Còpies de seguretat.
* Actualitzacions.
* Polítiques de seguretat.

---

#### 1.3.2. Seguretat de la informació

La seguretat de la informació busca protegir la informació independentment del format en què es trobe.

Una informació pot estar:

* Emmagatzemada en un disc.
* En una base de dades.
* En un servidor.
* En un ordinador personal.
* En una còpia de seguretat.
* En paper.
* En un dispositiu mòbil.
* Transmetent-se per una xarxa.

Per tant, la protecció ha de cobrir tot el cicle de vida de la informació.

---

### 1.4. Principis bàsics de seguretat

![Infraestructura de servidors connectats en un centre de dades](images/ud1/server-infrastructure.jpg)

*Figura 2. La protecció ha d'abastar la infraestructura, els serveis i la informació que allotgen.*

Els tres principis clàssics de la seguretat informàtica formen l'anomenada **tríada CIA**:

* Confidentiality → Confidencialitat.
* Integrity → Integritat.
* Availability → Disponibilitat.

---

#### 1.4.1. Confidencialitat

La confidencialitat garanteix que la informació només puga ser consultada per les persones o sistemes autoritzats.

Exemple:

Un empleat del departament d'administració ha de poder consultar les nòmines, però un usuari del departament de manteniment no hauria de tindre accés a elles.

Algunes mesures relacionades amb la confidencialitat són:

* Contrasenyes.
* Control de permisos.
* Xifrat.
* Autenticació multifactor.
* Segmentació de xarxes.
* Control d'accés.

---

#### 1.4.2. Integritat

La integritat garanteix que la informació no haja sigut modificada de manera no autoritzada.

Per exemple, si una base de dades conté:

```text
Saldo = 1.500 €
un atacant no hauria de poder modificar-lo a:   
MD

Plaintext
Saldo = 15.000 €
sense que el sistema puga detectar la modificació.   
MD

Algunes tècniques relacionades amb la integritat són:   
MD

Hashes.   
MD

Signatures digitals.   
MD

Sistemes de control de versions.   
MD

Permisos.   
MD

Auditories.   
MD

Registres d'activitat.   
MD

1.4.3. Disponibilitat
La disponibilitat garanteix que els usuaris autoritzats puguen utilitzar la informació i els serveis quan els necessiten.   
MD

Un servidor pot ser molt segur des del punt de vista de la confidencialitat, però si roman apagat o inaccessible, no compleix adequadament la seua funció.   
MD

Mesures relacionades:   
MD

Redundància.   
MD

RAID.   
MD

Còpies de seguretat.   
MD

Alta disponibilitat.   
MD

Balancejadors.   
MD

Sistemes d'alimentació ininterrompuda.   
MD

Monitoratge.   
MD

Plans de recuperació.   
MD

1.4.4. Autenticitat
L'autenticitat permet comprovar que una persona, dispositiu o sistema és realment qui diu ser.   
MD

Exemples:   
MD

Usuari i contrasenya.   
MD

Certificats digitals.   
MD

Claus criptogràfiques.   
MD

Biometria.   
MD

Autenticació multifactor.   
MD

1.4.5. Traçabilitat
La traçabilitat permet conéixer quines accions s'han realitzat en un sistema i qui les ha realitzades.   
MD

Per exemple:   
MD

Plaintext
10/09/2026 08:43
Usuari: admin
Acció: modificació de configuració
Equip: servidor01
Els registres o logs són fonamentals per a aconseguir traçabilitat.   
MD

1.4.6. No repudi
El no repudi permet disposar d'evidències que dificulten que una persona puga negar posteriorment una acció realitzada.   
MD

Les signatures digitals són una de les principals tecnologies relacionades amb aquest concepte.   
MD

2. Actius, riscos i tipus de seguretat
2.1. Actius
   
MD

Figura 3. L'anàlisi de riscos permet prioritzar la protecció dels actius més importants.

   
MD

Un actiu és qualsevol element que tinga valor per a una organització i que haja de ser protegit.   
MD

Alguns exemples són:   
MD

Servidors.   
MD

Ordinadors.   
MD

Encaminadors (routers).   
MD

Bases de dades.   
MD

Aplicacions.   
MD

Sistemes operatius.   
MD

Informació de clients.   
MD

Contrasenyes.   
MD

Certificats.   
MD

Còpies de seguretat.   
MD

Instal·lacions.   
MD

Personal.   
MD

No tots els actius tenen el mateix valor.   
MD

Una base de dades amb informació de clients pot tindre una importància molt major que un ordinador utilitzat únicament per a tasques administratives.   
MD

2.2. Amenaces
Una amenaça és qualsevol circumstància que pot provocar un dany sobre un actiu.   
MD

Les amenaces poden ser accidentals o intencionades.   
MD

2.2.1. Amenaces accidentals
Fallada elèctrica.   
MD

Error humà.   
MD

Esborrat accidental.   
MD

Avaria de maquinari.   
MD

Incendi.   
MD

Inundació.   
MD

2.2.2. Amenaces intencionades
Robatori.   
MD

Programari maliciós (malware).   
MD

Atacs de xarxa.   
MD

Phishing.   
MD

Robatori de credencials.   
MD

Sabotatge.   
MD

Accés no autoritzat.   
MD

2.3. Vulnerabilitats
Una vulnerabilitat és una feblesa tècnica, física, organitzativa o humana que pot ser aprofitada per a provocar un dany. Pot estar present en el disseny d'una aplicació, en una configuració insegura, en un equip sense actualitzar o en un procediment que no defineix controls suficients. Per si sola no causa necessàriament un incident, però obri una possible via d'accés o d'alteració que s'ha d'identificar, valorar i tractar.   
MD
+ 2

Exemples:   
MD

Sistema operatiu sense actualitzar.   
MD

Contrasenya feble.   
MD

Port innecessari obert.   
MD

Servei vulnerable.   
MD

Permisos excessius.   
MD

Falta de còpies de seguretat.   
MD

Configuració incorrecta.   
MD

Aplicació vulnerable.   
MD

Una vulnerabilitat no implica necessàriament que existeixca un atac.   
MD

Per exemple:   
MD

Plaintext
Servidor Linux
     ↓
SSH exposat a Internet
     ↓
Contrasenya feble
     ↓
Vulnerabilitat
Si un atacant aprofita eixa feblesa per a accedir al servidor, estaríem davant una explotació de la vulnerabilitat.   
MD

2.3.1. Amenaça i exploit
Una amenaça és una persona, un procés, un esdeveniment o una circumstància amb capacitat de causar dany a un actiu. Pot ser intencionada, com un intent de robatori de credencials, o accidental, com una fallada elèctrica. Un exploit és la tècnica, procediment o eina que aprofita una vulnerabilitat concreta per a convertir eixa possibilitat en un atac real.   
MD
+ 2

Per tant, els tres conceptes es relacionen d'aquesta forma:   
MD

Plaintext
Vulnerabilitat: feblesa existent
   ↓
Amenaça: agent o circumstància que pot aprofitar-la
   ↓
Exploit: tècnica utilitzada per a explotar-la
   ↓
Incident: dany o accés no autoritzat
Per exemple, una aplicació web que no valida correctament les dades introduïdes presenta una vulnerabilitat. Un atacant constitueix l'amenaça i podria utilitzar una tècnica d'injecció com a exploit per a intentar accedir o alterar informació. La protecció no depén d'una única mesura: requereix desenvolupament segur, actualitzacions, configuracions adequades i supervisió dels registres.   
MD
+ 2

2.3.2. Classificació per tipus
Les vulnerabilitats es poden classificar per la naturalesa de la feblesa:   
MD

| Tipus | Descripció | Exemple | Mesura principal |
| --- | --- | --- | --- |
| Programari | Errors de disseny, programació o validació d'una aplicació. | Programari sense parchejar o validació d'entrades deficient. | Actualitzacions, desenvolupament segur i revisió de codi. |
| Configuració | Ajustos insegurs o serveis exposats sense necessitat. | Credencials per defecte o port d'administració accessible des d'Internet. | Hardening, mínim privilegi i revisió periòdica. |
| Física | Falta de protecció d'equips, instal·lacions o suports. | Accés no controlat a un servidor o robatori d'un portàtil. | Control d'accés, inventari i xifrat de dispositius. |
| Xarxa | Febleses en protocols, segmentació o configuració de comunicacions. | Wi-Fi mal protegit o tràfec sense xifrar. | Segmentació, xifrat i configuració segura. |
| Maquinari | Deficiències en components físics o firmware. | Vulnerabilitats conegudes de processadors o firmware desactualitzat. | Actualitzacions de firmware i mesures de mitigació del fabricant. |
| Humana | Errors, falta de formació o procediments inadequats. | Phishing, contrasenyes febles o enviament erroni d'informació. | Formació, MFA i procediments de verificació. |   
MD
+ 4

2.3.3. Classificació per origen
Inherents: procedeixen del disseny o desenvolupament original d'un sistema; per exemple, un mecanisme d'autenticació mal implementat.   
MD

Introduïdes: apareixen durant la instal·lació, configuració, operació o manteniment; per exemple, un servei innecessari habilitat o permisos excessius.   
MD

Derivades: surgeixen de la interacció entre components, versions o dependències; per exemple, una extensió incompatible amb l'aplicació principal.   
MD

De tercers: afecten proveïdors, biblioteques, serveis cloud o cadenes de subministrament. S'han de gestionar mitjançant avaluació de proveïdors, inventari de dependències i aplicació controlada d'actualitzacions.   
MD
+ 1

També convé diferenciar les vulnerabilitats conegudes amb pegat disponible, les conegudes sense correcció definitiva i les de tipus zero-day, que encara no han sigut reconegudes públicament o no disposen d'una solució del proveïdor. Davant aquestes últimes es recorre a controls compensatoris, com restringir l'exposició del servei, segmentar la xarxa i reforçar el monitoratge.   
MD
+ 1

2.4. Risc
El risc representa la possibilitat que una amenaça aprofite una vulnerabilitat i provoque un impacte sobre un actiu. Per a gestionar-lo no n'hi ha prou amb enumerar problemes: és necessari identificar quins actius són importants, quines amenaces els afecten, quines febleses existeixen i quines conseqüències tindria un incident. Aquesta valoració permet prioritzar recursos, ja que no tots els riscos requereixen la mateixa resposta.   
MD
+ 2

De forma simplificada:   
MD

Plaintext
AMENAÇA + VULNERABILITAT → INCIDENT → IMPACTE
Una forma senzilla de valorar el risc és:   
MD

Plaintext
Risc = Probabilitat × Impacte
Per exemple:   
MD

| Amenaça          | Probabilitat |  Impacte |   Risc |
| ---------------- | -----------: | -------: | -------: |
| Fallada de disc  |         Alta |    Mitjà |     Alt |
| Robatori de portàtil |        Mitjana |     Alt |     Alt |
| Incendi         |         Baixa | Molt alt |     Alt |
| Phishing         |         Alta |     Alt | Molt alt |   
MD
+ 4

Aquesta valoració permet establir prioritats. Una vegada valorat, el risc es pot reduir aplicant controls, transferir-se mitjançant una assegurança o un servei especialitzat, acceptar-se de forma justificada quan el seu cost siga desproporcionat o evitar-se eliminant l'activitat que l'origina. Les decisions s'han de documentar i revisar quan canvie la infraestructura, apareguen noves amenaces o es produïsca un incident.   
MD
+ 2

2.5. Tipus de seguretat
2.5.1. Seguretat física
Protegeix els elements físics de la infraestructura.   
MD

Exemples:   
MD

Panys.   
MD

Càmeres.   
MD

Control d'accés.   
MD

SAI.   
MD

Sistemes contra incendis.   
MD

Control de temperatura.   
MD

Sistemes de detecció de fum.   
MD

2.5.2. Seguretat lògica
Protegeix els sistemes mitjançant mecanismes relacionats amb programari i configuració.   
MD

Exemples:   
MD

Usuaris.   
MD

Contrasenyes.   
MD

Permisos.   
MD

Tallafocs.   
MD

Antivirus.   
MD

Xifrat.   
MD

Sistemes IDS/IPS.   
MD

2.5.3. Seguretat activa
Busca prevenir, detectar o detindre incidents.   
MD

Exemples:   
MD

Tallafocs.   
MD

IDS.   
MD

IPS.   
MD

Antivirus.   
MD

Sistemes de monitoratge.   
MD

Autenticació.   
MD

2.5.4. Seguretat passiva
El seu objectiu principal és reduir les conseqüències d'un incident.   
MD

Exemples:   
MD

Còpies de seguretat.   
MD

RAID.   
MD

SAI.   
MD

Sistemes redundants.   
MD

Plans de recuperació.   
MD

3. Amenaces i vulnerabilitats
3.1. Principals amenaces informàtiques
3.1.1. Malware
   
MD

Figura 4. La protecció enfront d'amenaces combina controls tècnics, actualització i vigilància.

   
MD

Malware és un terme general utilitzat per a referir-se a programari maliciós dissenyat per a alterar el funcionament d'un equip, obtindre informació o facilitar un accés no autoritzat. Pot arribar mitjançant adjunts de correu, descàrregues no verificades, suports extraïbles, pàgines compromeses o l'explotació de programes vulnerables. El seu impacte depén dels permisos obtinguts i de l'accés de l'equip a altres sistemes de l'organització.   
MD
+ 2

Entre els seus principals tipus trobem:   
MD

Virus
Programa capaç de propagar-se infectant altres arxius.   
MD

Cucs (Worms)
Programes capaços de propagar-se automàticament a través de xarxes.   
MD

Troians
Programes que aparenten realitzar una funció legítima però incorporen funcionalitats malicioses.   
MD

Ransomware
Malware que xifra o bloqueja informació per a exigir posteriorment un pagament.   
MD

Spyware
Programari dissenyat per a obtindre informació sobre les activitats de l'usuari.   
MD

Keylogger
Eina que registra les pulsacions del teclat.   
MD

La protecció enfront de malware combina mesures preventives i de detecció: mantindre el sistema operatiu i les aplicacions actualitzats, utilitzar protecció antimalware, limitar privilegis, filtrar el correu, mantindre còpies de seguretat verificades i analitzar alertes o comportaments anómals. Cap d'aquestes mesures és suficient de forma aïllada; la defensa millora en aplicar diverses capes.   
MD
+ 1

3.2. Enginyeria social
L'enginyeria social consisteix a manipular les persones per a aconseguir informació o provocar determinades accions. En lloc d'atacar directament un sistema, l'atacant explota la confiança, la urgència, la curiositat o la falta de procediments de verificació. Es pot presentar per correu electrònic, crida telefònica, missatgeria, xarxes socials o fins i tot mitjançant accés físic a instal·lacions.   
MD
+ 2

L'atacant pot intentar aconseguir:   
MD

Contrasenyes.   
MD

Informació personal.   
MD

Codis d'autenticació.   
MD

Accés físic.   
MD

Informació empresarial.   
MD

La principal característica d'aquests atacs és que aprofiten el comportament humà. Per a reduir el risc, el personal ha de verificar sol·licituds inusuals per un canal alternatiu, evitar compartir credencials o codis MFA, i comunicar immediatament qualsevol intent sospitós. Les polítiques clares i la formació periòdica són controls tan importants com les eines tècniques.   
MD
+ 2

3.3. Phishing
El phishing consisteix a intentar enganyar l'usuari utilitzant comunicacions fraudulentes que aparenten procedir d'una entitat coneguda. El seu objectiu pot ser robar credencials, induir una transferència, instal·lar malware o aconseguir informació personal. Encara que el correu electrònic és el canal més habitual, també es poden utilitzar missatges SMS, crides telefòniques o xarxes socials.   
MD
+ 2

Exemple:   
MD

Plaintext
AVÍS DE SEGURETAT

El seu compte serà bloquejat.

Accedisca al següent enllaç per a verificar les seues dades:
[https://ejemplo-falso.com](https://ejemplo-falso.com)
L'objectiu pot ser obtindre:   
MD

Usuari.   
MD

Contrasenya.   
MD

Dades bancàries.   
MD

Codis MFA.   
MD

Informació personal.   
MD

Per a reduir el risc és important comprovar:   
MD

Remitent.   
MD

Domini.   
MD

Enllaços.   
MD

Ortografia.   
MD

Context del missatge.   
MD

Sol·licituds urgents o inesperades.   
MD

A més, les organitzacions poden aplicar filtres de correu, autenticació de domini, MFA, bloqueig d'enllaços maliciosos i un procediment senzill per a informar de missatges sospitosos. Abans de facilitar informació o accedir a un enllaç, s'ha de verificar la petició a través de la web oficial o un contacte conegut, no mitjançant les dades incloses en el missatge.   
MD
+ 1

3.4. Atacs de força bruta
Un atac de força bruta consisteix a provar diferents combinacions fins a trobar una contrasenya vàlida. També pot reutilitzar contrasenyes filtrades prèviament en altres serveis, pràctica coneguda com a credential stuffing. Aquests atacs són més eficaços quan s'utilitzen contrasenyes curtes, predictibles o compartides entre diferents sistemes.   
MD
+ 2

Per exemple:   
MD

Plaintext
0000
0001
0002
0003
...
9999
La resistència es pot millorar mitjançant:   
MD

Contrasenyes llargues.   
MD

Bloqueig temporal.   
MD

Limitació d'intents.   
MD

MFA.   
MD

Polítiques de contrasenyes.   
MD

Monitoratge.   
MD

També és recomanable revisar els intents fallits d'inici de sessió, impedir l'ús de contrasenyes conegudes com a compromeses i separar els comptes d'administració dels comptes d'ús diari. La MFA redueix de forma significativa l'impacte d'una contrasenya robada, encara que no substitueix una bona gestió d'identitats.   
MD
+ 1

3.5. Denegació de servei
Un atac de denegació de servei busca impedir o dificultar que un servei puga ser utilitzat. L'atacant intenta esgotar recursos d'un servidor, una aplicació o una connexió de xarxa perquè els usuaris legítims no puguen utilitzar-lo. En un atac distribuït, denominat DDoS, el tràfec pot procedir de nombrosos dispositius, la qual cosa fa més difícil distingir les peticions legítimes de les malicioses.   
MD
+ 2

L'objectiu és consumir recursos com:   
MD

CPU.   
MD

Memòria.   
MD

Ample de banda.   
MD

Connexions.   
MD

Processos.   
MD

Les mesures de protecció inclouen filtratge i limitació de tràfec, monitoratge, serveis especialitzats de mitigació, redundància i distribució dels serveis. Un pla de resposta ha de definir qui rep les alertes, com s'escala l'incident i quins proveïdors poden intervindre quan l'atac supera la capacitat de la infraestructura pròpia.   
MD
+ 1

3.6. Vulnerabilitats de programari
Els programes poden contindre errors de programació, fallades de disseny o dependències insegures que permeten realitzar accions no previstes. Una actualització no aplicada, una biblioteca obsoleta o una validació insuficient de dades poden exposar aplicacions, serveis i sistemes operatius. Per això, la gestió de vulnerabilitats ha de formar part del manteniment ordinari i no limitar-se a actuar quan apareix un incident.   
MD
+ 2

Les vulnerabilitats es poden identificar mitjançant identificadors com els CVE.   
MD

La valoració d'una vulnerabilitat es pot complementar mitjançant sistemes com CVSS, que ajuda a estimar la seua gravetat tenint en compte factors com l'accés necessari, els privilegis requerits i l'impacte sobre confidencialitat, integritat i disponibilitat. L'identificador no substitueix l'anàlisi pròpia: una vulnerabilitat crítica pot tindre poca exposició en un sistema aïllat, mentre que una de gravetat mitjana pot ser prioritària en un servei exposat a Internet.   
MD
+ 1

Per això és important:   
MD

Mantindre actualitzat el sistema.   
MD

Aplicar pegats (parches).   
MD

Eliminar programari innecessari.   
MD

Monitorar vulnerabilitats.   
MD

Revisar configuracions.   
MD

El cicle de gestió ha d'incloure inventari d'actius i programari, consulta d'avisos del fabricant, avaluació de l'exposició, proves abans de desplegar pegats crítics i verificació posterior. Quan no existeix pegat, s'apliquen mesures temporals com deshabilitar el servei afectat, restringir l'accés de xarxa, limitar permisos o augmentar el monitoratge.   
MD
+ 1

4. Mesures de protecció i polítiques
4.1. Gestió d'usuaris i contrasenyes
   
MD

Figura 5. Les identitats, contrasenyes i factors addicionals d'autenticació controlen l'accés.

   
MD

Una política de seguretat ha d'establir criteris per als comptes d'usuari.   
MD

Algunes mesures:   
MD

Cada usuari ha de tindre el seu propi compte.   
MD

Evitar comptes compartits.   
MD

Aplicar el principi de mínim privilegi.   
MD

Utilitzar contrasenyes robustes.   
MD

Utilitzar MFA quan siga possible.   
MD

Bloquejar comptes inactius.   
MD

Revisar periòdicament els permisos.   
MD

4.2. Principi de mínim privilegi
Cada usuari o procés ha de disposar únicament dels permisos necessaris per a realitzar el seu treball.   
MD

Per exemple:   
MD

Plaintext
Usuari: alumne
Permisos:
- Llegir documents de classe
- Executar aplicacions

No hauria de disposar de:
- Administrar usuaris
- Modificar configuració del sistema
- Instal·lar programari sense autorització
Aquest principi redueix l'impacte d'un compte compromés.   
MD

4.3. Polítiques de seguretat
Una política de seguretat estableix les normes que han de seguir els usuaris i administradors.   
MD

Pot incloure:   
MD

Gestió de contrasenyes.   
MD

Ús de dispositius.   
MD

Accés remot.   
MD

Còpies de seguretat.   
MD

Actualitzacions.   
MD

Ús del correu electrònic.   
MD

Navegació web.   
MD

Gestió d'incidents.   
MD

Control d'accessos.   
MD

Protecció de dades.   
MD

Una política ha de ser coneguda pels usuaris i revisar-se periòdicament.   
MD

5. Gestió, resposta i compliment
5.1. Auditories de seguretat
   
MD

Figura 6. Les auditories, el monitoratge i la resposta documentada permeten millorar la seguretat de forma contínua.

   
MD

Una auditoria de seguretat és un procés sistemàtic que analitza una infraestructura, les seues polítiques i els seus controls per a comprovar el seu nivell de protecció. No busca únicament fallades tècniques: també revisa si existeixen procediments, si els permisos són adequats i si es compleixen els requisits legals i organitzatius.   
MD
+ 1

Pot revisar:   
MD

Usuaris.   
MD

Permisos.   
MD

Serveis.   
MD

Ports.   
MD

Actualitzacions.[cite: 6]

Configuració.[cite: 6]

Vulnerabilitats.[cite: 6]

Logs.[cite: 6]

Còpies de seguretat.[cite: 6]

Eines habituals en entorns ASIR inclouen:[cite: 6]

Lynis.[cite: 6]

OpenVAS/GVM.[cite: 6]

Nmap.[cite: 6]

Wazuh.[cite: 6]

Eines pròpies del sistema operatiu.[cite: 6]

El resultat ha de ser un informe prioritzat que descriga la troballa, l'actiu afectat, el risc, l'evidència obtinguda i una recomanació viable[cite: 6]. Per exemple, una auditoria pot detectar que un servidor conserva un compte administratiu sense ús: la mesura adequada seria validar que no és necessària, deshabilitar-la i comprovar després que el servei continua funcionant[cite: 6].

5.1.1. Equips de ciberseguretat
[cite: 6]
Les auditories i els exercicis de seguretat requereixen rols definits i autorització prèvia[cite: 6]. En una organització poden intervindre els següents equips:[cite: 6]

| Equip | Missió | Exemple d'activitat |[cite: 6]
| --- | --- | --- |
| Red Team | Simula tècniques d'un adversari per a comprovar la resistència de sistemes i processos. | Executar una prova autoritzada sobre una aplicació d'entorn de proves i informar de les febleses trobades. |[cite: 6]
| Blue Team | Protegeix, monitora, detecta i respon a incidents. | Analitzar alertes d'un SIEM, aplicar un pegat i millorar una regla de detecció. |[cite: 6]
| Purple Team | Coordina el Red Team i el Blue Team per a convertir les troballes en millores defensives. | Verificar que una tècnica simulada genera una alerta i ajustar la detecció si no ho fa. |[cite: 6]
| White Team | Defineix l'abast, les regles i la supervisió d'un exercici. | Establir quins sistemes poden analitzar-se, l'horari i els criteris de parada. |[cite: 6]
| Green Team | Implanta i manté les millores derivades dels exercicis. | Aplicar una configuració segura i documentar el canvi. |[cite: 6]

A l'aula, qualsevol pràctica ofensiva s'ha de realitzar només sobre màquines virtuals pròpies o sistemes autoritzats[cite: 6]. El valor d'un exercici no està a causar impacte, sinó a aprendre a detectar, documentar i corregir una feblesa[cite: 6].

5.2. Gestió d'incidents
[cite: 6]
Un incident de seguretat és un esdeveniment que pot afectar la confidencialitat, integritat o disponibilitat d'un sistema[cite: 6]. Es pot originar en un atac maliciós, una fallada tècnica o un error humà[cite: 6]. Una resposta ràpida, coordinada i documentada redueix l'impacte i permet aprendre del que ha ocorregut[cite: 6].

Exemples:[cite: 6]

Compte compromés.[cite: 6]

Infecció per malware.[cite: 6]

Robatori d'informació.[cite: 6]

Atac de ransomware.[cite: 6]

Accés no autoritzat.[cite: 6]

Caiguda provocada per un atac.[cite: 6]

Una actuació bàsica es pot dividir en:[cite: 6]

Plaintext
Detecció
   ↓
Anàlisi
   ↓
Contenció
   ↓
Erradicació
   ↓
Recuperació
   ↓
Lliçons apreses
Durant la detecció s'han de registrar la data, els sistemes afectats, els símptomes observats i les accions realitzades[cite: 6]. La contenció busca limitar la propagació sense destruir evidències; per exemple, aïllar una estació de treball compromesa de la xarxa pot ser preferible a apagar-la sense analitzar el seu estat[cite: 6]. Després de la recuperació es revisen les causes, els controls fallits i les millores necessàries[cite: 6].

A Espanya, les administracions públiques compten amb el suport del CCN-CERT, mentre que ciutadans i empreses poden recorrer a INCIBE-CERT[cite: 6]. Quan l'incident supera la capacitat interna de l'organització, la notificació ha d'incloure informació verificable i actualitzada, evitant compartir dades sensibles per canals no autoritzats[cite: 6].

5.3. Introducció a l'anàlisi forense
[cite: 6]
L'anàlisi forense informàtica busca obtindre i analitzar evidències relacionades amb un incident de manera que puguen ser revisades i, quan procedisca, tindre validesa en un procediment intern o judicial[cite: 6]. La prioritat és no alterar l'evidència original i mantindre una cadena de custòdia que documente qui accedeix a cada element, quan i per a què[cite: 6].

És important preservar la informació correctament per a evitar alterar les evidències[cite: 6].

Algunes fonts d'informació:[cite: 6]

Discos.[cite: 6]

Memòria RAM.[cite: 6]

Logs.[cite: 6]

Tràfec de xarxa.[cite: 6]

Registres d'aplicacions.[cite: 6]

Historials.[cite: 6]

Metadades.[cite: 6]

L'anàlisi forense requereix procediments rigorosos i documentació de les actuacions[cite: 6]. Les seues fases habituals són l'adquisició de còpies de treball, la preservació dels originals, l'anàlisi de registres i artefactes, la documentació d'eines i resultats, i la presentació d'un informe comprensible[cite: 6]. Per exemple, abans d'investigar una possible intrusió en un servidor, es pot crear una còpia forense, calcular el seu hash i analitzar la còpia, mantenint el suport original protegit[cite: 6].

5.3.1. CVE, CVSS i fonts d'informació
[cite: 6]
Una CVE (Common Vulnerabilities and Exposures) és un identificador públic per a una vulnerabilitat coneguda[cite: 6]. Facilita que fabricants, administradors i equips de seguretat parlen del mateix problema[cite: 6]. La puntuació CVSS ajuda a estimar la gravetat tècnica en una escala de 0 a 10, però la prioritat real també depén de l'exposició del sistema i dels controls ja existents[cite: 6].

Per exemple, una CVE crítica en un servei exposat a Internet s'ha de revisar amb urgència; la mateixa vulnerabilitat en una màquina d'entorn de proves aïllada pot tindre menor prioritat[cite: 6]. Les fonts habituals per a mantindre's informat són la NVD de NIST, els avisos de fabricants, INCIBE-CERT i CCN-CERT[cite: 6]. El procediment ha d'incloure inventari de versions, avaluació, pegat o mesura compensatòria i verificació posterior[cite: 6].

5.4. Compliment, normes i gestió del risc
[cite: 6]
El compliment legal forma part de la seguretat perquè obliga a protegir la informació, demostrar que s'apliquen controls adequats i respectar els drets de les persones[cite: 6]. Quan una organització tracta dades personals ha de considerar, entre altres normes, el RGPD i la LOPDGDD[cite: 6]. Les dades personals inclouen identificadors, dades de contacte, localització, informació econòmica o categories especials com a dades de salut o biomètriques[cite: 6].

El responsable del tractament determina per a què i com s'utilitzen les dades; l'encarregat les tracta per compte del responsable[cite: 6]. Algunes organitzacions han de designar un delegat de protecció de dades (DPO), que assessora i supervisa el compliment[cite: 6]. Les mesures tècniques i organitzatives, com el control d'accés, el xifrat, les còpies de seguretat i els registres, ajuden a aplicar aquests principis en la pràctica[cite: 6].

5.4.1. Marcs de referència
[cite: 6]
| Marc | Aplicació principal | Aportació |[cite: 6]
| --- | --- | --- |
| ISO 31000 | Gestió general del risc. | Proporciona principis per a identificar, valorar, tractar i revisar riscos. |[cite: 6]
| ISO/IEC 27001 | Sistemes de Gestió de Seguretat de la Informació (SGSI). | Defineix requisits certificables per a organitzar la seguretat de la informació. |[cite: 6]
| ISO/IEC 27002 | Controls de seguretat. | Ofereix bones pràctiques per a seleccionar i implantar controls. |[cite: 6]
| ENS | Administracions públiques espanyoles i proveïdors afectats. | Estableix principis i requisits de seguretat per a sistemes del sector públic. |[cite: 6]
| NIST Cybersecurity Framework | Gestió de ciberseguretat. | Organitza el treball en identificar, protegir, detectar, respondre i recuperar. |[cite: 6]

La gestió del risc és un cicle continu: identificar els actius i amenaces, analitzar probabilitat i impacte, decidir un tractament, implantar controls i revisar els resultats[cite: 6]. Un centre educatiu, per exemple, pot protegir les dades de l'alumnat mitjançant comptes individuals, permisos per rol, MFA per a comptes administratius, xifrat de portàtils, còpies verificades i un procediment de notificació d'incidències[cite: 6].

6. Resum
[cite: 6]
La seguretat informàtica combina persones, processos i tecnologia per a protegir els actius d'una organització[cite: 6]. L'anàlisi de riscos permet prioritzar controls; l'auditoria verifica la seua eficàcia; els equips de seguretat i la gestió d'incidents ajuden a detectar i millorar; i el compliment normatiu garanteix que la protecció respecte obligacions legals i drets de les persones[cite: 6].

Els conceptes d'actiu, amenaça, vulnerabilitat, exploit, risc i control serviran de base per a la resta del mòdul[cite: 6]. Una defensa eficaç no es basa en una única eina: aplica capes de protecció, supervisió constant i millora contínua[cite: 6].

7. Recursos
[cite: 6]
Nmap

[cite: 6]

Lynis

[cite: 6]

Wazuh

[cite: 6]

OWASP

[cite: 6]

MITRE ATT&CK

[cite: 6]

NIST Cybersecurity Framework

[cite: 6]

INCIBE

[cite: 6]

Material de suport: vulnerabilitats i amenaces

[cite: 6]

Guies per a empreses d'INCIBE

[cite: 6]

Guies CCN-STIC

[cite: 6]

8. Relació amb els resultats d'aprenentatge
[cite: 6]   
MD
+ 4
Aquesta unitat contribueix principalment al:[cite: 6]

RA1. Adopta pràctiques segures d'utilització i treball amb sistemes informàtics, reconeixent les vulnerabilitats i les necessitats d'assegurament dels sistemes.

[cite: 6]

També introdueix continguts relacionats amb:[cite: 6]

RA7. Reconeix la legislació i normativa sobre seguretat i protecció de dades.

[cite: 6]