---
title: "6 - Seguretat en xarxes"
weight: 1
---

# UD6 - Seguretat en xarxes

> Protecció de les comunicacions, l'accés i els serveis de xarxa mitjançant segmentació, xifratge, detecció i controls perimetrals.

| Dades de la unitat | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Duració | 14 hores |

## Índex

1. #1-fonaments-i-amenaces-de-xarxa
2. #2-control-daccés-i-segmentació-lanwlan
3. #3-comunicacions-remotes-i-vpn
4. #4-seguretat-perimetral-firewalls-i-dmz
5. #5-detecció-monitorització-i-resposta
6. #6-proxies-waf-ddos-i-zero-trust
7. #7-resum
8. #8-recursos
9. #9-relació-amb-els-resultats-daprenentatge

---

## 1. Fonaments i amenaces de xarxa

### 1.1. Introducció

Les xarxes connecten usuaris, sistemes, serveis i seus, però també amplien la superfície d'atac. Els protocols fundacionals d'Internet i moltes tecnologies LAN es van dissenyar per a entorns reduïts i relativament confiables, sense incorporar autenticació o xifratge de manera generalitzada. La seguretat de xarxa aplica controls per a preservar la confidencialitat, integritat, disponibilitat, autenticitat i traçabilitat.

La protecció ha de plantejar-se en capes: infraestructura física, enllaç, xarxa, transport, hosts i aplicacions. Un control aïllat no és suficient; per exemple, un firewall no evita una contrasenya robada, i el xifratge no corregix una autorització excessiva.

### 1.2. Amenaces habituals

Entre les amenaces més comunes es troben l'escolta de trànsit, l'escaneig de ports, la suplantació d'adreces, el malware, l'accés no autoritzat, la denegació de servei i els errors de configuració. Un atacant pot obtindre informació durant la fase de reconeixement i aprofitar serveis exposats, credencials dèbils, equips sense actualitzar o xarxes insuficientment segmentades.

Els atacs d'intermediari, o MITM, busquen situar-se entre dos participants per a observar, modificar o interrompre la comunicació. En una LAN IPv4, l'enverinament ARP pot associar una IP legítima a la MAC de l'atacant. Les contramesures inclouen segmentació, inspecció ARP dinàmica en switches compatibles, entrades estàtiques en casos concrets, xifratge d'extrem a extrem i monitorització.

DNS i DHCP són serveis crítics. La manipulació de respostes DNS pot redirigir cap a serveis fraudulents; DNSSEC firma dades DNS per a protegir-ne l'autenticitat, encara que requerix una cadena de validació correcta. Un DHCP no autoritzat pot proporcionar passarel·les o DNS maliciosos; les funcions DHCP snooping i port security en switches gestionables ajuden a limitar este risc.

### 1.3. Principis de protecció

El mínim privilegi, la defensa en profunditat, la segmentació i l'actualització són principis centrals. S'ha d'inventariar quins sistemes, ports, protocols i fluxos són necessaris, permetre només eixos fluxos i registrar els esdeveniments rellevants. Les anàlisis, captures i proves es realitzen exclusivament sobre xarxes pròpies o expressament autoritzades.

## 2. Control d'accés i segmentació LAN/WLAN

### 2.1. Protecció de la LAN

La seguretat cablejada comença amb el control físic d'armaris, panells de connexió, switches i ports. L'etiquetatge, la documentació, la desactivació de ports no utilitzats i el control d'accés a les sales reduïxen connexions i manipulacions no autoritzades.

L'autenticació 802.1X controla l'accés a un port abans de permetre el trànsit. El client s'autentica davant un servidor RADIUS, que pot assignar una VLAN o aplicar una política. El filtratge MAC i port security poden complementar el control, però una MAC es pot suplantar i no constituïx una autenticació suficient per si sola. Les solucions NAC amplien esta validació comprovant la identitat i, segons el cas, l'estat de seguretat del dispositiu.

### 2.2. VLAN, ACL i segmentació

Una VLAN crea un domini de capa 2 lògic independent sobre infraestructura compartida. IEEE 802.1Q etiqueta les trames que travessen enllaços troncals; els ports d'accés connecten normalment equips finals a una única VLAN. La comunicació entre VLAN requerix encaminament mitjançant un router o switch de capa 3.

La segmentació reduïx dominis de difusió i limita el moviment lateral. Una organització pot separar usuaris, servidors, gestió, convidats, IoT i DMZ. Les ACL i les regles de firewall definixen explícitament quines comunicacions entre zones estan permeses. Un troncal ha de transportar únicament les VLAN necessàries, i la xarxa de gestió ha d'estar separada i restringida.

### 2.3. Seguretat WLAN

Una WLAN utilitza un medi radioelèctric compartit i pot ser accessible des de fora de l'edifici, per la qual cosa requerix controls específics. WEP i WPA amb TKIP estan obsolets. WPA2 amb AES/CCMP continua present quan es configura correctament, mentre que WPA3 introduïx millores, com SAE en mode personal i una major protecció davant atacs de diccionari fora de línia.

Les xarxes empresarials han de prioritzar WPA2-Enterprise o WPA3-Enterprise amb 802.1X i RADIUS, que permeten credencials o certificats individuals i revocació per usuari. Un SSID de convidats ha d'aïllar-se de les xarxes internes. També són rellevants l'actualització dels punts d'accés, la detecció d'AP no autoritzats, la desactivació de WPS, l'aïllament de clients i la planificació de cobertura i potència.

## 3. Comunicacions remotes i VPN

### 3.1. Administració i xifratge de comunicacions

Els serveis d'administració i transferència han d'utilitzar protocols autenticats i xifrats. SSH substituïx Telnet per a l'administració remota; HTTPS i TLS protegixen aplicacions web; SFTP i SCP permeten transferències segures. La protecció criptogràfica, certificats i claus s'estudien en la UD3, i l'enduriment d'SSH en la UD4.

### 3.2. Concepte i tipus de VPN

Una VPN crea un túnel protegit sobre una xarxa no confiable. Pot proporcionar confidencialitat, integritat i autenticació, però no concedix accés il·limitat per defecte. Les VPN d'accés remot connecten usuaris individuals amb una xarxa o aplicació; les VPN site-to-site interconnecten seus o xarxes completes.

IPsec treballa en la capa de xarxa i és habitual en connexions entre seus. Les VPN basades en TLS, com OpenVPN, solen travessar NAT amb facilitat i són pràctiques per a l'accés remot. WireGuard oferix una arquitectura més compacta i moderna. L2TP no aporta xifratge per si mateix i normalment es combina amb IPsec. PPTP no s'ha d'utilitzar en dissenys nous a causa de les seues debilitats conegudes.

### 3.3. Disseny segur d'accés remot

Una VPN segura aplica autenticació robusta, preferiblement MFA, identitats individuals, xifratges actuals, revocació d'accessos i registre de connexions. El *split tunneling* envia pel túnel només el trànsit corporatiu; el *full tunneling* dirigix tot el trànsit del client a través de l'organització. L'elecció depén del risc, la privacitat, la capacitat i les necessitats d'inspecció.

També s'han de controlar les fugues de DNS, les rutes distribuïdes al client, els permisos sobre recursos interns i l'estat dels dispositius. L'accés remot ha de limitar-se als serveis necessaris i revisar-se periòdicament.

## 4. Seguretat perimetral, firewalls i DMZ

### 4.1. Firewalls i polítiques de filtratge

Un firewall filtra trànsit entre zones segons l'adreça, el port, el protocol, l'estat de la connexió i, en solucions avançades, l'aplicació o la identitat. Els firewalls de filtratge de paquets són simples i ràpids; els *stateful* mantenen l'estat de les connexions; els de nova generació poden incorporar control d'aplicacions, IDS/IPS, filtratge web i altres capacitats.

Una política segura partix de denegar per defecte i permetre de manera explícita només els fluxos necessaris. Les regles han de documentar origen, destinació, servei, propòsit, responsable i data de revisió. Les configuracions, el firmware i les còpies de seguretat del firewall requerixen control de canvis i protecció.

Netfilter és el marc de filtratge integrat en Linux, gestionable mitjançant nftables, iptables o firewalld. PF és un firewall utilitzat en sistemes BSD i constituïx la base de solucions com pfSense i OPNsense. La ferramenta no substituïx el disseny d'una política clara ni la revisió de registres.

### 4.2. DMZ i zones de seguretat

Una DMZ allotja serveis exposats, com servidors web o de correu, en una zona separada de la LAN interna. El firewall perimetral controla el trànsit des d'Internet cap a la DMZ, i regles addicionals limiten estrictament les comunicacions des de la DMZ cap a la xarxa interna. Un servidor web no ha d'accedir sense restriccions a una base de dades o a tots els sistemes corporatius.

Les VLAN, subxarxes, interfícies separades i controls entre zones permeten contindre incidents. La segmentació ha d'acompanyar-se d'actualitzacions, hardening, monitorització i proves de les regles, perquè una DMZ mal configurada pot convertir-se en una ruta directa cap a la xarxa interna.

## 5. Detecció, monitorització i resposta

### 5.1. IDS i IPS

Un IDS detecta activitat sospitosa i genera alertes; un IPS, a més, pot bloquejar o modificar el trànsit. Els NIDS/NIPS inspeccionen trànsit en punts de xarxa, mentre que els HIDS/HIPS analitzen successos d'un host. Els sensors poden rebre una còpia del trànsit mitjançant un port SPAN o TAP; un IPS sol situar-se en línia, per la qual cosa una política incorrecta pot afectar trànsit legítim.

Els mecanismes de detecció es basen en signatures, anomalies, polítiques o combinacions d'estes. Les signatures són eficaces davant amenaces conegudes; les anomalies poden trobar comportaments nous, però produïxen més falsos positius si no existix una línia base adequada. Suricata i Snort són eines conegudes per a anàlisi i detecció en xarxa.

### 5.2. Anàlisi de trànsit i registres

Wireshark i tcpdump ajuden a analitzar protocols, adreces, ports, sessions i errors en un entorn autoritzat. L'anàlisi permet diagnosticar problemes, verificar el xifratge, identificar configuracions insegures i estudiar una alerta. Capturar trànsit pot incloure dades personals o credencials, per la qual cosa les evidències han de protegir-se i conservar-se només el temps necessari.

Els registres de switches, routers, firewalls, VPN, IDS/IPS, proxies i servidors han de sincronitzar l'hora, centralitzar-se quan siga possible i protegir-se davant alteracions. Un SIEM correlaciona esdeveniments de diverses fonts i facilita alertes i investigació. La resposta davant un incident seguix un cicle de detecció, anàlisi, contenció, erradicació, recuperació i millora.

### 5.3. Límits i millora contínua

Un IDS/IPS necessita ajust continu de regles, actualització de signatures i revisió de falsos positius i negatius. El xifratge pot impedir inspeccionar el contingut si no es finalitza o inspecciona de manera controlada; això planteja requisits tècnics, legals i de privacitat. Les proves de detecció es planifiquen i executen només sobre entorns autoritzats.

## 6. Proxies, WAF, DDoS i Zero Trust

### 6.1. Proxies i WAF

Un proxy directe representa els clients davant Internet i pot aplicar filtratge, autenticació, registre i memòria cau. Un proxy invers se situa davant dels servidors, oculta la infraestructura interna, finalitza TLS, distribuïx càrrega i centralitza registres. Cap dels dos ha de convertir-se en un punt únic de fallada sense una estratègia de disponibilitat, com s'estudia en la UD5.

Un WAF inspecciona sol·licituds HTTP per a detectar o bloquejar patrons d'atacs contra aplicacions web, com injeccions SQL o XSS. Complementa les validacions de l'aplicació, actualitzacions, autenticació i configuració TLS; no corregix per si mateix una aplicació vulnerable. Les regles han d'ajustar-se per a reduir bloquejos de trànsit legítim i evitar una falsa sensació de seguretat.

### 6.2. Mitigació de DDoS

Els atacs DDoS busquen esgotar ample de banda, capacitat de xarxa o recursos de l'aplicació. Poden ser volumètrics, d'amplificació o de capa 7. La mitigació combina limitació de taxa, filtratge, monitorització de pics, capacitat d'escalat, CDN i serveis especialitzats de neteja de trànsit.

Una organització ha de disposar de contactes, llindars d'alerta, procediments d'escalada i comunicació amb proveïdors. Les proves de resiliència no consistixen a generar trànsit contra sistemes aliens: es realitzen amb abast aprovat, eines controlades i mesures d'aturada.

### 6.3. Zero Trust

Zero Trust partix de la idea que cap xarxa, usuari o dispositiu és confiable per defecte. Verifica explícitament la identitat i el context de cada accés, aplica mínim privilegi i reduïx l'impacte d'un compromís mitjançant microsegmentació. MFA, NAC, gestió de dispositius, polítiques per identitat i monitorització contínua són elements habituals.

La implantació és gradual: inventari d'actius i fluxos, classificació de recursos, definició de polítiques, desplegament per fases i revisió de resultats. No equival a adquirir un únic producte; exigix processos, arquitectura i formació.

## 7. Resum

La seguretat de xarxa combina la protecció de l'accés LAN i WLAN, la segmentació, les comunicacions xifrades, el control perimetral, la detecció i la resposta. Els controls han de ser coherents amb els actius i fluxos que protegixen, i aplicar el mínim privilegi en cada capa.

VPN, firewalls, IDS/IPS, proxies, WAF i Zero Trust resolen problemes diferents i complementaris. La seua eficàcia depén d'una configuració mantinguda, monitorització, evidències protegides i proves realitzades de manera autoritzada.

## 8. Recursos

- NIST Cybersecurity Framework
- Wi‑Fi Alliance: WPA3
- WireGuard
- OpenVPN
- Suricata
- Snort
- Wireshark
- Netfilter
- OWASP: Web Application Firewall

## 9. Relació amb els resultats d'aprenentatge

Esta unitat contribuïx principalment al **RA2**, mitjançant la identificació d'amenaces, la configuració de controls de xarxa, la segmentació, la monitorització i la detecció d'intrusions.

També es relaciona amb el **RA3**, pel disseny de VPN i accés remot segur, i amb el **RA4**, per les polítiques de firewall, DMZ, proxies i protecció de serveis perimetrals.

<br aria-hidden="true">