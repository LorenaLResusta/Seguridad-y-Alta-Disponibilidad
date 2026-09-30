---
title: "4. Fortificació de Hosts"
weight: 1
---

# UD4 - Fortificació de Hosts

> Mesures per a reduir la superfície d'atac, protegir sistemes operatius i detectar incidents.

| Dades de la unitat | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Duració | 14 hores |

## Índex

1. #1-fonaments-del-hardening
2. #2-identitats-permisos-i-accés-remot
3. #3-arrancada-segura-i-protecció-de-dades
4. #4-protecció-davant-del-malware
5. #5-actualitzacions-auditoria-i-vulnerabilitats
6. #6-monitorització-registres-i-resposta
7. #7-resum
8. #8-recursos
9. #9-relació-amb-els-resultats-daprenentatge

---

## 1. Fonaments del hardening

### 1.1. Introducció

La fortificació, o *hardening*, és el conjunt de mesures que reduïx la superfície d'atac d'un host i limita l'impacte d'un possible compromís. Afecta servidors, equips client, màquines virtuals i dispositius connectats. No consistix en una configuració única: requerix inventari, aplicació de controls, revisió i millora contínua.

Abans de modificar un sistema s'ha d'identificar què està exposat: usuaris i grups, serveis actius, ports oberts, aplicacions instal·lades, tasques programades, interfícies de xarxa, directoris compartits i versions de programari. L'objectiu és eliminar o deshabilitar allò que no aporta una funció necessària.

### 1.2. Objectius

En finalitzar la unitat, l'alumnat serà capaç de:

- Identificar la superfície d'atac d'un host.
- Aplicar controls d'accés, permisos i autenticació robusta.
- Protegir l'arrancada, l'emmagatzematge i les dades.
- Reconéixer mesures de prevenció davant del malware.
- Gestionar actualitzacions, auditories i vulnerabilitats.
- Interpretar registres, alertes i mecanismes de monitorització.

### 1.3. Principis de fortificació

El principi de mínim privilegi guia totes les decisions: cada usuari, servici i procés ha de disposar únicament dels permisos estrictament necessaris. Executar servicis amb privilegis administratius, compartir comptes o mantindre servicis innecessaris amplia el risc i dificulta la investigació posterior.

Una fortificació eficaç combina controls tècnics, polítiques documentades i formació. Les mesures han de ser proporcionades al risc, verificables i compatibles amb la continuïtat del servici.

## 2. Identitats, permisos i accés remot

La gestió d'identitats determina qui pot accedir a un sistema i a quins recursos. Els comptes han de ser individuals, tindre un responsable i revisar-se periòdicament. Els comptes abandonats, compartits o amb privilegis excessius són un risc freqüent.

En Linux, els permisos distingixen propietari, grup i resta d'usuaris, amb lectura, escriptura i execució. L'assignació de grups facilita aplicar permisos coherents a diversos usuaris. Configuracions àmplies com permisos universals d'escriptura o execució han d'evitar-se excepte per una necessitat concreta, documentada i controlada.

Les contrasenyes han de ser llargues, úniques i difícils de predir. Una política raonable contempla longitud mínima, protecció davant intents repetits, historial quan siga necessari i un procediment segur de recuperació. Forçar canvis periòdics sense indicis de compromís pot fomentar patrons predictibles; és preferible exigir el canvi davant la sospita d'exposició, recuperació del compte o canvi de risc. Els gestors de contrasenyes i l'autenticació multifactor reduïxen la dependència d'una única contrasenya.

L'autenticació multifactor combina factors de coneixement, possessió o inherència. Un codi temporal, una clau de seguretat o un token complementen la contrasenya i reduïxen l'impacte del seu robatori. Els mecanismes de recuperació del segon factor també han d'estar protegits.

SSH permet administrar hosts Linux de forma remota. Una configuració segura utilitza claus en lloc de dependre només de contrasenyes, restringix els usuaris autoritzats, limita els privilegis, manté el servici actualitzat i registra els accessos. La clau privada mai es compartix; la pública pot instal·lar-se en el servidor. Abans d'aplicar canvis s'ha de preveure una via de recuperació per a no perdre l'accés legítim.

## 3. Arrancada segura i protecció de dades

La protecció comença abans que arranque el sistema operatiu. UEFI, les contrasenyes del firmware, la restricció de l'arrancada externa i les actualitzacions del firmware reduïxen el risc de manipulació física. Secure Boot verifica que els components d'arrancada estiguen signats per una entitat de confiança. TPM pot mesurar elements de l'arrancada i col·laborar amb mecanismes de protecció com BitLocker.

El xifratge de disc protegix la confidencialitat de les dades en repòs quan es perd, es roba o es retira un dispositiu. BitLocker s'integra en Windows, FileVault en macOS i LUKS és l'estàndard habitual en Linux. El xifratge no substituïx els permisos, les còpies de seguretat ni la gestió de claus: si es perd la clau de recuperació, les dades poden quedar inaccessibles.

També es pot xifrar de manera més granular mitjançant volums o directoris, per exemple amb VeraCrypt o EFS en Windows. L'elecció depén de quines dades es protegixen, qui ha d'accedir-hi, on s'emmagatzemen les claus i com es realitzarà la recuperació.

Les dades en trànsit requerixen protocols autenticats i xifrats, com HTTPS, SSH, SFTP o una VPN. Les dades sensibles han de classificar-se, disposar de controls d'accés adequats i comptar amb còpies de seguretat xifrades i recuperables. La seguretat física, com el control d'accés a instal·lacions, ancoratges, armaris tancats o vigilància, complementa estos controls.

## 4. Protecció davant del malware

El malware és programari dissenyat per a danyar, espiar, interrompre o accedir sense autorització a un sistema. Entre les seues formes més comunes es troben virus, cucs, troians, ransomware, spyware, adware, rootkits, *keyloggers*, malware sense arxiu i botnets. Poden entrar mitjançant phishing, aplicacions malicioses, vulnerabilitats sense corregir, xarxes insegures o atacs a la cadena de subministrament.

La defensa es basa en capes: actualització de sistemes, mínim privilegi, segmentació de xarxa, filtratge de correu, còpies de seguretat provades, autenticació multifactor, control d'aplicacions i formació d'usuaris. Un ransomware també pot afectar recursos compartits i còpies connectades, per la qual cosa les còpies han d'estar separades i comptar amb protecció davant modificacions no autoritzades.

Les solucions antimalware combinen signatures, heurística i anàlisi de comportament. Un antivirus protegix principalment davant amenaces conegudes; les solucions EDR recopilen i analitzen activitat dels endpoints per a detectar i respondre; XDR correlaciona senyals d'endpoints, xarxa, correu, núvol i altres orígens. Una *sandbox* permet analitzar fitxers sospitosos en un entorn aïllat, però mai justifica executar mostres en un equip de producció.

Els servicis públics d'anàlisi poden oferir indicadors útils, però pujar un arxiu revela el seu contingut a tercers. Els fitxers confidencials, dades personals, claus o documents interns no han d'enviar-se a servicis externs d'anàlisi sense autorització expressa.

## 5. Actualitzacions, auditoria i vulnerabilitats

Les actualitzacions corregixen vulnerabilitats, errors i problemes d'estabilitat. Una política de pegats ha d'inventariar actius i versions, avaluar actualitzacions, provar canvis quan el seu impacte siga rellevant, desplegar-los de manera controlada i verificar-ne el resultat. En entorns Windows, WSUS o Microsoft Endpoint Configuration Manager permeten centralitzar el desplegament; en Linux, els gestors de paquets i les eines d'automatització complixen esta funció.

La integritat i procedència del programari han de comprovar-se mitjançant repositoris oficials, signatures digitals, hashes i control de versions. Git registra canvis en el codi, mentre que les signatures de paquets o de codi ajuden a verificar autoria i integritat. Estes verificacions no substituïxen l'aplicació oportuna de pegats.

La gestió de vulnerabilitats és un cicle continu: identificació, anàlisi, priorització, correcció, verificació i seguiment. La prioritat no depén només d'una puntuació tècnica: també importen l'exposició de l'actiu, la seua criticitat, la facilitat d'explotació, l'impacte i els controls compensatoris disponibles.

Ferramentes com Lynis, OpenSCAP i GVM/OpenVAS ajuden a descobrir configuracions dèbils, incompliments o vulnerabilitats conegudes. Nessus, Qualys, Rapid7 InsightVM i Tripwire són alternatives comercials. Qualsevol escaneig s'ha de realitzar únicament sobre actius propis o autoritzats, amb un abast i horari definits per a evitar afectar els servicis.

## 6. Monitorització, registres i resposta

Els registres documenten esdeveniments de sistemes, aplicacions i dispositius. Permeten detectar activitat anòmala, investigar incidents, demostrar compliment normatiu i aprendre dels errors. Una estratègia de registres útil definix quins esdeveniments es conserven, durant quant de temps, qui pot consultar-los i com es protegix la seua integritat.

En un host s'han de vigilar, entre altres aspectes, autenticacions, canvis de privilegis, inicis i aturades de servicis, errors, connexions de xarxa, consum de recursos i canvis de configuració. La monitorització local aporta una primera visió, mentre que la centralització evita que les evidències es perden si un host és compromés.

Un IDS detecta indicis d'intrusió; un IPS pot, a més, bloquejar trànsit o accions segons la seua configuració. Snort i Suricata són exemples de motors de detecció en xarxa. Un SIEM recopila i correlaciona esdeveniments de múltiples fonts per a generar alertes, facilitar investigacions i produir informes de compliment. Wazuh combina agents, anàlisi de logs, detecció de canvis i integració amb gestió de vulnerabilitats; Elastic Stack i Graylog s'utilitzen amb freqüència per a centralitzar i visualitzar registres.

Les alertes necessiten un procediment de resposta: validar l'esdeveniment, classificar-ne la gravetat, contindre l'impacte, preservar evidències, erradicar la causa, recuperar el servici i documentar les lliçons apreses. La revisió contínua de regles, llindars i falsos positius manté útil el sistema de monitorització.

## 7. Resum

La fortificació de hosts reduïx la superfície d'atac mitjançant inventari, mínim privilegi, autenticació robusta, protecció de l'arrancada, xifratge, actualitzacions, defensa davant del malware i monitorització. La millora contínua requerix comprovar els canvis, prioritzar vulnerabilitats i documentar les decisions.

## 8. Recursos

- CIS Benchmarks
- Lynis
- Wazuh
- OpenSCAP
- CISA
- CCN-CERT

## 9. Relació amb els resultats d'aprenentatge

La unitat desenrotlla l'adopció de pràctiques segures, la protecció d'hosts i dades, el control d'accés, la detecció d'amenaces, l'actualització de sistemes i la monitorització de la seguretat.

<br aria-hidden="true">