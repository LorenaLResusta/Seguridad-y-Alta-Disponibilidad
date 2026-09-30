---
title: "7. Seguretat perimetral. Pràctiques"
weight: 1
---

# UD7 - Seguretat perimetral

> Protecció de les fronteres de xarxa mitjançant tallafocs, segmentació, publicació segura i control del trànsit.

| Dades de la unitat | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Duració | 14 hores |

## Índex

- UD7 - Seguretat perimetral
  - 1. Fonaments de seguretat perimetral
    - 1.1. Introducció
    - 1.2. Objectius
    - 1.3. Zones i defensa en profunditat
  - 2. Tallafocs i plataformes de filtratge
    - 2.1. Tipus de tallafocs
    - 2.2. Netfilter, PF i solucions de codi obert
  - 3. Polítiques, regles i registre
    - 3.1. Disseny de regles
    - 3.2. Registres i monitorització
    - 3.3. Actualització i gestió de canvis
  - 4. NAT, publicació de serveis i DMZ
    - 4.1. NAT i redirecció de ports
    - 4.2. DMZ i segmentació avançada
  - 5. Proxis, proxy invers i WAF
    - 5.1. Proxy directe
    - 5.2. Proxy invers i WAF
  - 6. Disponibilitat i operació del perímetre
    - 6.1. Alta disponibilitat del tallafocs
    - 6.2. Operació i millora contínua
  - 7. Resum
  - 8. Recursos
  - 9. Relació amb els resultats d'aprenentatge

---

## 1. Fonaments de seguretat perimetral

### 1.1. Introducció

La seguretat perimetral protegix les zones de connexió entre xarxes amb diferent nivell de confiança, especialment el límit entre Internet, les xarxes internes, els serveis publicats i l'accés remot. El seu objectiu és reduir accessos no autoritzats, atacs, pèrdua de dades i l'impacte d'una intrusió.

Un tallafocs actua com a filtre entre xarxes: permet, bloqueja, registra o redirigix trànsit segons regles predefinides. Avalua criteris com ara interfícies, adreces IP, ports, protocols, estat de connexió i, en solucions avançades, aplicació o identitat. És un punt de control estratègic, però no substituïx les actualitzacions, l'autenticació robusta, la segmentació ni el *hardening* dels sistemes protegits.

### 1.2. Objectius

En finalitzar la unitat, l'alumnat serà capaç de:

- Explicar la funció i les limitacions de la seguretat perimetral.
- Diferenciar tallafocs de paquets, amb estat, d'aplicació i de nova generació.
- Dissenyar polítiques de filtratge basades en denegació per defecte i mínim privilegi.
- Configurar i justificar NAT, redirecció de ports i una DMZ.
- Interpretar registres i relacionar-los amb la detecció d'incidents.
- Distingir entre proxy directe, proxy invers i WAF.
- Valorar la disponibilitat, actualització i operació segura dels controls perimetrals.

### 1.3. Zones i defensa en profunditat

Una arquitectura senzilla separa Internet, LAN, DMZ, xarxa de gestió i accés VPN. Cada zona ha de tindre una finalitat definida i fluxos documentats. La segmentació limita el moviment lateral: comprometre un servidor publicat no ha de donar accés directe a tots els sistemes interns.

La defensa en profunditat combina controls: filtratge al perímetre, regles entre zones, protecció d'hosts, autenticació, monitorització, còpies de seguretat i resposta davant incidents. La seguretat perimetral es complementa amb la segmentació LAN/WLAN i les VPN vistes en la UD6.

## 2. Tallafocs i plataformes de filtratge

### 2.1. Tipus de tallafocs

Els tallafocs de filtratge de paquets inspeccionen principalment adreces IP, ports i protocols. Són ràpids i senzills, però no analitzen en profunditat el contingut. Els tallafocs *stateful* mantenen l'estat de les connexions TCP i d'altres fluxos, cosa que permet diferenciar trànsit associat a una sessió legítima de paquets no sol·licitats.

Els tallafocs d'aplicació o *next-generation firewall* poden identificar protocols i aplicacions, aplicar filtratge web, control de continguts, IDS/IPS o polítiques basades en identitat. Estes funcions amplien la visibilitat, però requerixen dimensionament, actualització i ajust per a no bloquejar trànsit legítim ni crear una falsa sensació de seguretat.

### 2.2. Netfilter, PF i solucions de codi obert

Netfilter és el marc de filtratge i manipulació de trànsit integrat en el nucli Linux. Permet filtratge, NAT, redirecció de ports, registre i seguiment de connexions. *nftables* és la interfície moderna per a definir regles; *iptables* continua present en molts entorns, encara que ha sigut substituït progressivament. *firewalld* oferix una capa de gestió dinàmica sobre estos mecanismes en diverses distribucions.

Packet Filter, o PF, és un sistema de filtratge i NAT utilitzat en sistemes BSD. Oferix regles per interfícies, seguiment d'estat, NAT, taules d'adreces i capacitats d'alta disponibilitat com CARP. pfSense i OPNsense són plataformes basades en FreeBSD i PF que integren tallafocs, NAT, VLAN, VPN, DHCP, DNS, monitorització i extensions com IDS/IPS o proxy.

L'elecció de la plataforma ha de considerar requisits, coneixements de l'equip, suport, actualitzacions, rendiment, còpies de configuració i capacitat d'auditoria. Cap eina reemplaça una política clara i ben mantinguda.

## 3. Polítiques, regles i registre

### 3.1. Disseny de regles

Una política segura comença amb denegació per defecte i afig únicament excepcions justificades. Cada regla ha de definir interfície, origen, destinació, protocol, port, acció, finalitat, responsable i data de revisió. L'orde és important: molts tallafocs processen les regles de dalt cap avall fins a trobar una coincidència.

El mínim privilegi implica limitar tant l'accés entrant com l'eixint. Per exemple, publicar HTTPS cap a un servidor web de la DMZ no implica permetre SSH des d'Internet ni concedir a eixe servidor accés lliure a la LAN. Les regles temporals, massa àmplies o sense responsable han de revisar-se i eliminar-se.

### 3.2. Registres i monitorització

Els registres del tallafocs documenten connexions permeses i bloquejades, amb origen, destinació, port, protocol i interfície. Permeten detectar escanejos, intents repetits, errors de regles, trànsit inesperat i possibles incidents. Els equips han de sincronitzar la seua hora i protegir els registres contra alteracions.

La centralització en un servidor de registres o SIEM facilita correlacionar esdeveniments de tallafocs, VPN, IDS/IPS, proxis i servidors. El volum de logs requerix criteris de retenció, accés autoritzat i alertes útils. Registrar-ho tot sense revisió no equival a monitoritzar.

### 3.3. Actualització i gestió de canvis

El firmware o programari del tallafocs ha de mantindre's actualitzat i els canvis han de provar-se, documentar-se i poder revertir-se. Les còpies de configuració han d'emmagatzemar-se protegides i comprovar-se periòdicament. Abans de modificar una regla crítica s'ha de disposar d'una via de recuperació per a evitar perdre l'accés administratiu legítim.

## 4. NAT, publicació de serveis i DMZ

### 4.1. NAT i redirecció de ports

NAT modifica adreces i, en alguns casos, ports durant el trànsit. Permet que xarxes privades compartisquen una adreça pública i pot ocultar l'estructura interna, però no és un mecanisme de seguretat complet. La traducció d'adreces ha d'acompanyar-se de regles de filtratge explícites.

El *port forwarding* publica un servei intern associant un port o adreça externa amb una destinació concreta. Només han d'exposar-se els serveis necessaris, preferiblement en una DMZ, i protegir-se amb actualitzacions, TLS, autenticació i monitorització. Publicar un port d'administració directament a Internet augmenta considerablement el risc.

### 4.2. DMZ i segmentació avançada

Una DMZ és una subxarxa destinada a serveis publicats, com ara servidors web, correu, DNS públic o proxy invers. Se separa de la LAN mitjançant interfícies, VLAN o dispositius diferents. El tallafocs controla Internet-DMZ, LAN-DMZ i, de manera especialment restrictiva, DMZ-LAN.

Un servidor web de DMZ pot requerir accés a un port concret de base de dades, però no a tota la xarxa interna. Un servidor de correu exposat pot necessitar entregar correu a un sistema intern, però no accés administratiu general. Minimitzar serveis, limitar fluxos, reforçar hosts i monitoritzar accessos reduïxen l'impacte d'una intrusió.

## 5. Proxis, proxy invers i WAF

### 5.1. Proxy directe

Un proxy directe representa els clients davant Internet. Pot aplicar autenticació, filtratge per polítiques, control de dominis, memòria cau i registre de navegació. Squid és un exemple habitual de proxy HTTP/HTTPS. Les regles d'accés s'avaluen en orde i han d'acabar en una denegació general després de permetre els clients i serveis necessaris.

El filtratge d'HTTPS té limitacions: sense inspecció TLS, el proxy no veu el contingut; amb inspecció es requerixen certificats, informació als usuaris, controls de privacitat i una gestió rigorosa. Les polítiques de navegació han de ser proporcionades, transparents i d'acord amb la normativa aplicable.

### 5.2. Proxy invers i WAF

Un proxy invers rep peticions externes i les reenviа a un o diversos serveis interns. Permet ocultar els *backends*, centralitzar TLS, aplicar control d'accés, registrar sol·licituds, oferir memòria cau i distribuir càrrega. Nginx i HAProxy són eines habituals; el seu paper en el balanceig i l'alta disponibilitat es relaciona amb la UD5.

Un WAF inspecciona peticions web i pot detectar o bloquejar patrons associats a atacs com la injecció SQL o XSS. Complementa, però no substituïx, la validació d'entrades, l'autenticació, el desenvolupament segur, les actualitzacions i els registres de l'aplicació. Les seues regles requerixen ajust continu per a controlar falsos positius i negatius.

## 6. Disponibilitat i operació del perímetre

### 6.1. Alta disponibilitat del tallafocs

Un únic tallafocs pot representar un punt únic de fallada. Els entorns amb requisits elevats poden utilitzar parelles actiu-passiu o actiu-actiu, enllaços redundants, fonts d'alimentació independents i sincronització d'estat. CARP permet compartir una adreça virtual en plataformes basades en PF; les solucions comercials oferixen mecanismes equivalents.

La redundància ha d'incloure les seues dependències: alimentació, xarxa, DNS, accés de gestió, enllaços del proveïdor i monitorització. Un disseny HA es valida amb proves controlades de commutació, restauració i comportament de sessions, com s'estudia en la UD5.

### 6.2. Operació i millora contínua

L'operació del perímetre comprén inventari d'actius, revisió de regles, aplicació de pegats, còpies de seguretat, gestió de certificats, anàlisi de registres i resposta a incidents. Les proves han de definir abast, responsables, finestra de manteniment, criteris d'aturada i reversió.

El compliment normatiu i la privacitat afecten la conservació de logs, la inspecció de trànsit i el control de navegació. Les decisions han de documentar-se i revisar-se davant canvis de serveis, personal, amenaces o requisits legals.

## 7. Resum

La seguretat perimetral separa zones de confiança i controla les seues comunicacions mitjançant tallafocs, NAT, DMZ i proxis. Una política eficaç partix de denegar per defecte, permet només fluxos justificats i registra els esdeveniments rellevants.

Netfilter, PF, pfSense, OPNsense, Squid, Nginx i WAF són eines que han d'integrar-se en una arquitectura mantinguda, monitoritzada i preparada per a recuperar-se de fallades. La segmentació, el *hardening* i les aplicacions segures continuen sent necessaris fins i tot darrere d'un tallafocs.

## 8. Recursos

- Netfilter: https://www.netfilter.org/
- nftables: https://wiki.nftables.org/
- Packet Filter: https://www.openbsd.org/faq/pf/
- pfSense: https://docs.netgate.com/pfsense/en/latest/
- OPNsense: https://docs.opnsense.org/
- Squid: https://www.squid-cache.org/Doc/
- Nginx Reverse Proxy: https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
- OWASP Web Application Firewall: https://owasp.org/www-community/Web_Application_Firewall

## 9. Relació amb els resultats d'aprenentatge

Esta unitat contribuïx principalment al **RA4**, mitjançant la planificació, configuració i documentació de tallafocs, filtratge, NAT, DMZ, registres i resolució d'incidències perimetrals.

També es relaciona amb el **RA5**, per la selecció i configuració de proxis directes i inversos, i amb el **RA3**, quan el perímetre integra VPN i accés remot segur.