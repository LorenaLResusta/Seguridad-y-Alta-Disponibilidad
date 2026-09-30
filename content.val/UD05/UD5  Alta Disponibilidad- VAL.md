---
title: "5. Alta disponibilitat"
weight: 1
---

# UD5 - Alta disponibilitat

> Disseny de serveis redundants, tolerants a fallades i recuperables.

| Dades de la unitat | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Duració | 14 hores |

## Índex

1. #1-fonaments-dalta-disponibilitat
2. #2-redundància-dinfraestructura-i-xarxa
3. #3-clústers-i-failover-en-linux
4. #4-balanceig-ip-virtual-i-continuitat-de-xarxa
5. #5-virtualització-contenidors-i-disseny-ha
6. #6-resum
7. #7-recursos
8. #8-relació-amb-els-resultats-daprenentatge

---

## 1. Fonaments d'alta disponibilitat

### 1.1. Introducció

L'alta disponibilitat, o HA, busca que un servei romanga operatiu i accessible el màxim temps possible, reduint les interrupcions no planificades. És necessària quan una caiguda afecta de manera rellevant usuaris, ingressos, seguretat, obligacions legals o la continuïtat d'una organització.

HA no equival a eliminar totes les fallades. Combina prevenció, detecció, redundància, commutació automàtica i recuperació per a reduir el temps d'indisponibilitat. També es relaciona amb la continuïtat de negoci i la recuperació davant desastres: la primera manté les operacions i la segona permet recuperar-les després d'un incident greu.

### 1.2. Objectius

En finalitzar la unitat, l'alumnat serà capaç de:

- Diferenciar disponibilitat, redundància, tolerància a fallades i continuïtat.
- Identificar punts únics de fallada en una infraestructura.
- Interpretar MTBF, MTTR, RPO i RTO en un disseny HA.
- Seleccionar mecanismes de redundància de maquinari, emmagatzematge i xarxa.
- Explicar el funcionament de clústers, quòrum, *fencing* i *failover*.
- Dissenyar serveis amb balanceig de càrrega, IP virtual i comprovacions de salut.
- Valorar el paper de la virtualització, els contenidors i l'automatització.

### 1.3. Disponibilitat i punts únics de fallada

La disponibilitat expressa la proporció de temps en què un servei funciona correctament:

$$
D = \frac{MTBF}{MTBF + MTTR}
$$

El MTBF és el temps mitjà entre fallades i el MTTR el temps mitjà de reparació. Els anomenats "nous" traduïxen un percentatge anual en temps de caiguda aproximat: $99.9\%$ permet unes $8.76$ hores, $99.99\%$ uns $52.56$ minuts i $99.999\%$ uns $5.26$ minuts.

Un punt únic de fallada, o SPOF, és un component la caiguda del qual interromp un servei. Pot ser un firewall, un switch, una font d'alimentació, un host de virtualització, un enllaç o una base de dades. El primer pas d'un disseny HA és identificar-los i decidir quins s'han d'eliminar segons l'impacte i el cost.

### 1.4. Redundància, tolerància i objectius de recuperació

La redundància incorpora components addicionals; la tolerància a fallades permet mantindre el servei quan un element falla; el *failover* trasllada un recurs a un component disponible. Els models actiu-passiu mantenen un node de reserva, mentre que els actiu-actiu repartixen la càrrega entre diversos nodes.

L'RPO establix la pèrdua màxima de dades acceptable i l'RTO el temps objectiu de recuperació. Per exemple, un RPO de 15 minuts pot exigir còpies o replicació freqüents, mentre que un RTO d'una hora requerix procediments assajats i recursos preparats per a recuperar el servei. RAID i les còpies de seguretat s'estudien en la UD2: RAID millora la disponibilitat davant fallades de disc, però no substituïx les còpies ni la recuperació davant esborrats o ransomware.

## 2. Redundància d'infraestructura i xarxa

### 2.1. Maquinari, alimentació i emmagatzematge

La redundància pot aplicar-se a servidors, fonts d'alimentació, ventiladors, controladores, interfícies de xarxa i emmagatzematge. Els components redundants han de connectar-se, quan siga possible, a rutes elèctriques i de xarxa diferents; duplicar un equip que depén del mateix switch o SAI no elimina tots els riscos.

Un SAI proporciona autonomia limitada i temps per a un apagat controlat; un generador pot mantindre el servei durant talls prolongats. La potència, autonomia, prioritats i procediment d'apagat han de dimensionar-se i provar-se. NAS, SAN, replicació i sistemes distribuïts permeten reduir riscos d'emmagatzematge, però exigixen dissenyar la coherència de les dades i la recuperació.

### 2.2. Redundància de xarxa i agregació d'enllaços

Una xarxa resilient incorpora rutes i equips alternatius per a evitar que un únic enllaç, switch, router o firewall interrompa el servei. Les topologies de malla, anell o nucli-distribució-accés poden oferir diversos camins si es dissenyen i supervisen correctament.

L'agregació d'enllaços combina diverses interfícies físiques en un canal lògic. LACP, normalitzat en IEEE 802.3ad, permet augmentar la capacitat agregada i mantindre la connectivitat si falla un dels enllaços. Ha de configurar-se de manera compatible en tots dos extrems i no garantix que una única connexió utilitze tot l'ample de banda del grup.

Els enllaços redundants poden crear bucles. STP i les seues variants RSTP o MSTP bloquegen rutes segons la topologia i habiliten alternatives quan detecten una fallada. La segmentació, els protocols d'encaminament i la monitorització completen el disseny d'una xarxa disponible.

## 3. Clústers i failover en Linux

### 3.1. Components i models de clúster

Un clúster HA reunix diversos nodes per a oferir un servei de manera coordinada. Els seus components habituals són nodes, xarxa de comunicació, emmagatzematge compartit o replicat, recursos gestionats, comprovacions de salut i mecanismes per a evitar operacions simultànies no segures.

En un disseny actiu-passiu, un node executa el servei i un altre està preparat per a assumir-lo. En actiu-actiu, diversos nodes atenen peticions i normalment s'utilitza balanceig. L'elecció depén de si l'aplicació permet executar-se de forma concurrent, de com manté l'estat i de quina consistència requerixen les dades.

### 3.2. Corosync, Pacemaker, quòrum i fencing

Corosync proporciona comunicació entre nodes, detecció de pertinença i quòrum. Pacemaker utilitza esta informació per a gestionar recursos com serveis, sistemes de fitxers o adreces IP, i decidix on s'han d'executar segons les restriccions definides.

El quòrum evita que una part aïllada del clúster prenga decisions crítiques sense majoria suficient. El *split-brain* es produïx quan nodes o grups aïllats creuen poder gestionar el mateix recurs, amb risc de corrupció de dades. El *fencing* aïlla de manera fiable un node que no respon, per exemple apagant-lo o bloquejant-li l'accés a l'emmagatzematge, abans de moure un recurs crític a un altre node.

### 3.3. Dades, comprovacions i commutació

Un clúster necessita decidir on estan les dades i com preservar-ne la consistència. Pot utilitzar emmagatzematge compartit, replicació de bloc com DRBD, sistemes distribuïts com GlusterFS o mecanismes propis d'una base de dades. No existix una solució universal: cal valorar latència, integritat, comportament davant particions i recuperació.

Les comprovacions de salut han de verificar tant que el procés està actiu com que el servei respon correctament. Quan es detecta una fallada, el clúster aplica el procediment de *failover*: deté o aïlla el recurs si és necessari, activa el destí i confirma que el servei funciona abans d'anunciar-lo als clients.

## 4. Balanceig, IP virtual i continuïtat de xarxa

### 4.1. Balancejadors i proxy invers

Un balancejador de càrrega distribuïx peticions entre diversos servidors disponibles per a millorar la disponibilitat, el rendiment i l'escalabilitat. Els algoritmes habituals inclouen *round-robin*, menor nombre de connexions, repartiment ponderat i hash d'IP. Este últim pot aportar afinitat de sessió, però reduïx la flexibilitat si la distribució de clients és desigual.

HAProxy i Nginx poden actuar com a balancejadors i proxy invers. El proxy invers oculta els servidors interns, pot finalitzar TLS, aplicar filtratge i emmagatzemar contingut en memòria cau. El mateix balancejador també pot ser un SPOF, per la qual cosa els serveis crítics solen desplegar-lo de manera redundant.

### 4.2. IP virtual i VRRP

VRRP oferix una passarel·la o adreça IP virtual compartida per diversos routers o servidors. Un membre actua com a *master* i els altres com a *backup*; si els nodes de reserva deixen de rebre anuncis, un d'ells assumix la IP virtual. Els clients mantenen la mateixa passarel·la i no necessiten reconfigurar-se.

Keepalived implementa VRRP en Linux i pot associar la IP virtual a comprovacions de salut. S'utilitza tant per a redundància de gateways com per a mantindre disponible una IP de balanceig. HSRP i GLBP són alternatives propietàries habituals en dispositius Cisco.

### 4.3. Disseny i proves

La disponibilitat real es valida mitjançant proves controlades: caiguda d'un node, fallada d'un enllaç, indisponibilitat d'un backend, reinici planificat i restauració de dades. Les proves han de tindre abast, horari, criteris d'aturada i pla de reversió. Una solució HA no està completa fins que es comproven les seues alertes, temps de commutació i comportament durant la recuperació.

## 5. Virtualització, contenidors i disseny HA

### 5.1. Virtualització i contenidors

La virtualització facilita aïllar serveis, crear recursos ràpidament, migrar màquines i reiniciar càrregues en altres hosts. Plataformes com Proxmox, VMware o Hyper-V poden incorporar clústers i automatització de recuperació. Perquè una màquina virtual siga realment disponible, també s'han de considerar els hosts, les xarxes i l'emmagatzematge dels quals depén.

Els contenidors reduïxen la sobrecàrrega compartint el sistema operatiu de l'host. Orquestradors com Kubernetes gestionen rèpliques, comprovacions de salut, desplegaments i reprogramació de càrregues. Tot i això, la disponibilitat d'una aplicació depén de les seues dades, configuració, secrets, xarxa i disseny d'estat, no sols del nombre de rèpliques.

### 5.2. Planificació d'una arquitectura HA

Una proposta HA partix dels serveis crítics, els objectius RPO/RTO, les dependències i el pressupost. Ha d'identificar SPOF, triar controls proporcionats i definir qui respon a les alertes. Afegir tecnologia sense conéixer el servei pot incrementar el risc operatiu.

Un servei web d'exemple pot utilitzar dos servidors darrere d'un proxy invers, dos balancejadors amb una IP virtual, emmagatzematge o base de dades replicats, còpies de seguretat independents, monitorització centralitzada i procediments de recuperació documentats. L'arquitectura ha de poder créixer, mantindre's i provar-se sense interrompre innecessàriament el servei.

## 6. Resum

L'alta disponibilitat combina redundància, detecció, automatització i procediments de recuperació per a reduir indisponibilitats. El disseny ha d'eliminar SPOF rellevants, mantindre la consistència de les dades i validar el comportament davant fallades reals o simulades.

Clústers, balancejadors, VRRP, LACP, virtualització i emmagatzematge replicat són ferramentes, no objectius per si mateixos. El seu valor depén que responguen a requisits mesurables de disponibilitat, RPO i RTO.

## 7. Recursos

- Pacemaker
- Corosync
- Keepalived
- HAProxy
- Documentació de LACP
- Proxmox VE
- Kubernetes: high availability

## 8. Relació amb els resultats d'aprenentatge

Esta unitat contribuïx principalment al **RA6**, mitjançant el disseny i la implantació de solucions d'alta disponibilitat amb redundància, virtualització, emmagatzematge, clústers, balanceig i recuperació.

També es relaciona amb el **RA2**, per la monitorització i detecció de fallades, i amb el **RA4**, quan les solucions HA s'integren amb dispositius i controls perimetrals.

<br aria-hidden="true">---
title: "5. Alta disponibilitat"
weight: 1
---

# UD5 - Alta disponibilitat

> Disseny de serveis redundants, tolerants a fallades i recuperables.

| Dades de la unitat | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Duració | 14 hores |

## Índex

1. #1-fonaments-dalta-disponibilitat
2. #2-redundància-dinfraestructura-i-xarxa
3. #3-clústers-i-failover-en-linux
4. #4-balanceig-ip-virtual-i-continuitat-de-xarxa
5. #5-virtualització-contenidors-i-disseny-ha
6. #6-resum
7. #7-recursos
8. #8-relació-amb-els-resultats-daprenentatge

---

## 1. Fonaments d'alta disponibilitat

### 1.1. Introducció

L'alta disponibilitat, o HA, busca que un servei romanga operatiu i accessible el màxim temps possible, reduint les interrupcions no planificades. És necessària quan una caiguda afecta de manera rellevant usuaris, ingressos, seguretat, obligacions legals o la continuïtat d'una organització.

HA no equival a eliminar totes les fallades. Combina prevenció, detecció, redundància, commutació automàtica i recuperació per a reduir el temps d'indisponibilitat. També es relaciona amb la continuïtat de negoci i la recuperació davant desastres: la primera manté les operacions i la segona permet recuperar-les després d'un incident greu.

### 1.2. Objectius

En finalitzar la unitat, l'alumnat serà capaç de:

- Diferenciar disponibilitat, redundància, tolerància a fallades i continuïtat.
- Identificar punts únics de fallada en una infraestructura.
- Interpretar MTBF, MTTR, RPO i RTO en un disseny HA.
- Seleccionar mecanismes de redundància de maquinari, emmagatzematge i xarxa.
- Explicar el funcionament de clústers, quòrum, *fencing* i *failover*.
- Dissenyar serveis amb balanceig de càrrega, IP virtual i comprovacions de salut.
- Valorar el paper de la virtualització, els contenidors i l'automatització.

### 1.3. Disponibilitat i punts únics de fallada

La disponibilitat expressa la proporció de temps en què un servei funciona correctament:

$$
D = \frac{MTBF}{MTBF + MTTR}
$$

El MTBF és el temps mitjà entre fallades i el MTTR el temps mitjà de reparació. Els anomenats "nous" traduïxen un percentatge anual en temps de caiguda aproximat: $99.9\%$ permet unes $8.76$ hores, $99.99\%$ uns $52.56$ minuts i $99.999\%$ uns $5.26$ minuts.

Un punt únic de fallada, o SPOF, és un component la caiguda del qual interromp un servei. Pot ser un firewall, un switch, una font d'alimentació, un host de virtualització, un enllaç o una base de dades. El primer pas d'un disseny HA és identificar-los i decidir quins s'han d'eliminar segons l'impacte i el cost.

### 1.4. Redundància, tolerància i objectius de recuperació

La redundància incorpora components addicionals; la tolerància a fallades permet mantindre el servei quan un element falla; el *failover* trasllada un recurs a un component disponible. Els models actiu-passiu mantenen un node de reserva, mentre que els actiu-actiu repartixen la càrrega entre diversos nodes.

L'RPO establix la pèrdua màxima de dades acceptable i l'RTO el temps objectiu de recuperació. Per exemple, un RPO de 15 minuts pot exigir còpies o replicació freqüents, mentre que un RTO d'una hora requerix procediments assajats i recursos preparats per a recuperar el servei. RAID i les còpies de seguretat s'estudien en la UD2: RAID millora la disponibilitat davant fallades de disc, però no substituïx les còpies ni la recuperació davant esborrats o ransomware.

## 2. Redundància d'infraestructura i xarxa

### 2.1. Maquinari, alimentació i emmagatzematge

La redundància pot aplicar-se a servidors, fonts d'alimentació, ventiladors, controladores, interfícies de xarxa i emmagatzematge. Els components redundants han de connectar-se, quan siga possible, a rutes elèctriques i de xarxa diferents; duplicar un equip que depén del mateix switch o SAI no elimina tots els riscos.

Un SAI proporciona autonomia limitada i temps per a un apagat controlat; un generador pot mantindre el servei durant talls prolongats. La potència, autonomia, prioritats i procediment d'apagat han de dimensionar-se i provar-se. NAS, SAN, replicació i sistemes distribuïts permeten reduir riscos d'emmagatzematge, però exigixen dissenyar la coherència de les dades i la recuperació.

### 2.2. Redundància de xarxa i agregació d'enllaços

Una xarxa resilient incorpora rutes i equips alternatius per a evitar que un únic enllaç, switch, router o firewall interrompa el servei. Les topologies de malla, anell o nucli-distribució-accés poden oferir diversos camins si es dissenyen i supervisen correctament.

L'agregació d'enllaços combina diverses interfícies físiques en un canal lògic. LACP, normalitzat en IEEE 802.3ad, permet augmentar la capacitat agregada i mantindre la connectivitat si falla un dels enllaços. Ha de configurar-se de manera compatible en tots dos extrems i no garantix que una única connexió utilitze tot l'ample de banda del grup.

Els enllaços redundants poden crear bucles. STP i les seues variants RSTP o MSTP bloquegen rutes segons la topologia i habiliten alternatives quan detecten una fallada. La segmentació, els protocols d'encaminament i la monitorització completen el disseny d'una xarxa disponible.

## 3. Clústers i failover en Linux

### 3.1. Components i models de clúster

Un clúster HA reunix diversos nodes per a oferir un servei de manera coordinada. Els seus components habituals són nodes, xarxa de comunicació, emmagatzematge compartit o replicat, recursos gestionats, comprovacions de salut i mecanismes per a evitar operacions simultànies no segures.

En un disseny actiu-passiu, un node executa el servei i un altre està preparat per a assumir-lo. En actiu-actiu, diversos nodes atenen peticions i normalment s'utilitza balanceig. L'elecció depén de si l'aplicació permet executar-se de forma concurrent, de com manté l'estat i de quina consistència requerixen les dades.

### 3.2. Corosync, Pacemaker, quòrum i fencing

Corosync proporciona comunicació entre nodes, detecció de pertinença i quòrum. Pacemaker utilitza esta informació per a gestionar recursos com serveis, sistemes de fitxers o adreces IP, i decidix on s'han d'executar segons les restriccions definides.

El quòrum evita que una part aïllada del clúster prenga decisions crítiques sense majoria suficient. El *split-brain* es produïx quan nodes o grups aïllats creuen poder gestionar el mateix recurs, amb risc de corrupció de dades. El *fencing* aïlla de manera fiable un node que no respon, per exemple apagant-lo o bloquejant-li l'accés a l'emmagatzematge, abans de moure un recurs crític a un altre node.

### 3.3. Dades, comprovacions i commutació

Un clúster necessita decidir on estan les dades i com preservar-ne la consistència. Pot utilitzar emmagatzematge compartit, replicació de bloc com DRBD, sistemes distribuïts com GlusterFS o mecanismes propis d'una base de dades. No existix una solució universal: cal valorar latència, integritat, comportament davant particions i recuperació.

Les comprovacions de salut han de verificar tant que el procés està actiu com que el servei respon correctament. Quan es detecta una fallada, el clúster aplica el procediment de *failover*: deté o aïlla el recurs si és necessari, activa el destí i confirma que el servei funciona abans d'anunciar-lo als clients.

## 4. Balanceig, IP virtual i continuïtat de xarxa

### 4.1. Balancejadors i proxy invers

Un balancejador de càrrega distribuïx peticions entre diversos servidors disponibles per a millorar la disponibilitat, el rendiment i l'escalabilitat. Els algoritmes habituals inclouen *round-robin*, menor nombre de connexions, repartiment ponderat i hash d'IP. Este últim pot aportar afinitat de sessió, però reduïx la flexibilitat si la distribució de clients és desigual.

HAProxy i Nginx poden actuar com a balancejadors i proxy invers. El proxy invers oculta els servidors interns, pot finalitzar TLS, aplicar filtratge i emmagatzemar contingut en memòria cau. El mateix balancejador també pot ser un SPOF, per la qual cosa els serveis crítics solen desplegar-lo de manera redundant.

### 4.2. IP virtual i VRRP

VRRP oferix una passarel·la o adreça IP virtual compartida per diversos routers o servidors. Un membre actua com a *master* i els altres com a *backup*; si els nodes de reserva deixen de rebre anuncis, un d'ells assumix la IP virtual. Els clients mantenen la mateixa passarel·la i no necessiten reconfigurar-se.

Keepalived implementa VRRP en Linux i pot associar la IP virtual a comprovacions de salut. S'utilitza tant per a redundància de gateways com per a mantindre disponible una IP de balanceig. HSRP i GLBP són alternatives propietàries habituals en dispositius Cisco.

### 4.3. Disseny i proves

La disponibilitat real es valida mitjançant proves controlades: caiguda d'un node, fallada d'un enllaç, indisponibilitat d'un backend, reinici planificat i restauració de dades. Les proves han de tindre abast, horari, criteris d'aturada i pla de reversió. Una solució HA no està completa fins que es comproven les seues alertes, temps de commutació i comportament durant la recuperació.

## 5. Virtualització, contenidors i disseny HA

### 5.1. Virtualització i contenidors

La virtualització facilita aïllar serveis, crear recursos ràpidament, migrar màquines i reiniciar càrregues en altres hosts. Plataformes com Proxmox, VMware o Hyper-V poden incorporar clústers i automatització de recuperació. Perquè una màquina virtual siga realment disponible, també s'han de considerar els hosts, les xarxes i l'emmagatzematge dels quals depén.

Els contenidors reduïxen la sobrecàrrega compartint el sistema operatiu de l'host. Orquestradors com Kubernetes gestionen rèpliques, comprovacions de salut, desplegaments i reprogramació de càrregues. Tot i això, la disponibilitat d'una aplicació depén de les seues dades, configuració, secrets, xarxa i disseny d'estat, no sols del nombre de rèpliques.

### 5.2. Planificació d'una arquitectura HA

Una proposta HA partix dels serveis crítics, els objectius RPO/RTO, les dependències i el pressupost. Ha d'identificar SPOF, triar controls proporcionats i definir qui respon a les alertes. Afegir tecnologia sense conéixer el servei pot incrementar el risc operatiu.

Un servei web d'exemple pot utilitzar dos servidors darrere d'un proxy invers, dos balancejadors amb una IP virtual, emmagatzematge o base de dades replicats, còpies de seguretat independents, monitorització centralitzada i procediments de recuperació documentats. L'arquitectura ha de poder créixer, mantindre's i provar-se sense interrompre innecessàriament el servei.

## 6. Resum

L'alta disponibilitat combina redundància, detecció, automatització i procediments de recuperació per a reduir indisponibilitats. El disseny ha d'eliminar SPOF rellevants, mantindre la consistència de les dades i validar el comportament davant fallades reals o simulades.

Clústers, balancejadors, VRRP, LACP, virtualització i emmagatzematge replicat són ferramentes, no objectius per si mateixos. El seu valor depén que responguen a requisits mesurables de disponibilitat, RPO i RTO.

## 7. Recursos

- Pacemaker
- Corosync
- Keepalived
- HAProxy
- Documentació de LACP
- Proxmox VE
- Kubernetes: high availability

## 8. Relació amb els resultats d'aprenentatge

Esta unitat contribuïx principalment al **RA6**, mitjançant el disseny i la implantació de solucions d'alta disponibilitat amb redundància, virtualització, emmagatzematge, clústers, balanceig i recuperació.

També es relaciona amb el **RA2**, per la monitorització i detecció de fallades, i amb el **RA4**, quan les solucions HA s'integren amb dispositius i controls perimetrals.

