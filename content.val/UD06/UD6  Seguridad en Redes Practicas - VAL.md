---
title: "6 - Seguretat en xarxes. Pràctiques"
weight: 2
---

# UD6 - Pràctiques: seguretat en xarxes

> Segmentació, perímetre, WLAN, VPN i detecció en entorns de proves controlats.

| Dades de les pràctiques | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Duració estimada | 8 hores |
| Entorn | Màquines virtuals, simulador i equips autoritzats |

## 1. Objectius

- Dissenyar xarxes segmentades amb VLAN, DMZ i regles de mínim privilegi.
- Configurar i comprovar un firewall perimetral en un entorn virtual.
- Avaluar una WLAN i aplicar autenticació empresarial quan l'entorn ho permeta.
- Desplegar VPN d'accés remot i site-to-site amb rutes i regles limitades.
- Capturar trànsit propi i analitzar alertes d'un IDS/IPS.
- Configurar un proxy i documentar evidències de proves de seguretat.

## 2. Abast i preparació

Estes pràctiques es realitzen només en màquines virtuals, xarxes internes, switches, punts d'accés i firewalls autoritzats. No escaneges, captures trànsit, proves credencials, modifiques punts d'accés ni generes trànsit de denegació de servei fora de l'entorn de proves.

Es recomana crear una *snapshot* abans de cada pràctica. Per als escenaris perimetrals s'utilitzaran un firewall pfSense o OPNsense, una VM client i una VM servidor. Per a les VPN site-to-site es necessitaran dos firewalls i un client en cada LAN. Registra les IP, xarxes, interfícies i canvis realitzats en una taula de treball.

## 3. Pràctica 1 - Firewall perimetral, VLAN i DMZ

### 3.1. Escenari

En VirtualBox, crea un firewall amb tres interfícies i dos VM Linux:

| Interfície o VM | Xarxa | Funció |
| --- | --- | --- |
| WAN | NAT o pont d'entorn de proves | Eixida a Internet simulada. |
| LAN | Només-amfitrió o xarxa interna | Client corporatiu. |
| DMZ | Xarxa interna independent | Servidor web. |
| Client | LAN | Comprovació de polítiques. |
| Servidor | DMZ | Servei HTTP/HTTPS i SSH d'entorn de proves. |

Instal·la pfSense o OPNsense, assigna correctament les interfícies i configura subxarxes diferents per a LAN i DMZ. L'accés a la interfície d'administració s'ha de realitzar des de la LAN o xarxa de gestió, mai des de WAN.

### 3.2. Serveis i regles

En el servidor de la DMZ instal·la Apache o Nginx i permet només els ports necessaris en el seu firewall local. Crea en el firewall perimetral una política de denegació per defecte i regles que complisquen la següent matriu:

| Origen | Destinació | Servicis permesos |
| --- | --- | --- |
| LAN | DMZ | ICMP, HTTP, HTTPS i SSH |
| WAN | DMZ | HTTPS publicat mitjançant NAT/port forwarding |
| DMZ | LAN | Cap |
| LAN | WAN | DNS, HTTP i HTTPS necessaris |

Comprova els fluxos permesos amb `ping`, `curl` i SSH des de les teues VM. Comprova també que un servici no autoritzat de LAN a DMZ i qualsevol connexió iniciada des de DMZ a LAN queden bloquejats. Inclou captures de les interfícies, regles, NAT i resultats de cada prova.

### 3.3. Extensió de VLAN

Dissenya VLAN d'administració, usuaris, servidors, convidats, DMZ i gestió. Indica ports d'accés, troncals 802.1Q i regles inter-VLAN. Si disposes de switch gestionable o simulador, implementa almenys dos VLAN i comprova l'aïllament entre elles. No habilites VLAN en un troncal si no és necessària.

## 4. Pràctica 2 - WLAN segura i autenticació RADIUS

### 4.1. Auditoria de WLAN

Revisa un AP propi, autoritzat o simulat. Completa una fitxa que indique estàndard WPA configurat, autenticació, WPS, actualització de firmware, compte d'administració, SSID de convidats, VLAN assignada, aïllament de clients i cobertura. Justifica per què WEP, WPA i TKIP no s'han d'utilitzar.

Compara WPA2/WPA3-Personal amb WPA2/WPA3-Enterprise. Explica com es revoca l'accés d'una persona en cada cas i per què una clau PSK compartida no escala bé en una organització.

### 4.2. FreeRADIUS opcional

En una VM Debian o Ubuntu d'entorn de proves, instal·la FreeRADIUS i les seues utilitats:

```bash
sudo apt update
sudo apt install -y freeradius freeradius-utils
sudo systemctl enable --now freeradius


Revisa la configuració de clients RADIUS i autoritza únicament la IP de l'AP d'entorn de proves amb un secret compartit de pràctiques. Crea un usuari temporal en el fitxer d'usuaris de FreeRADIUS o mitjançant el mètode indicat pel professorat. Executa el servici en mode de depuració només durant la prova:

sudo systemctl stop freeradius
sudo freeradius -X


Configura l'AP per a WPA2/WPA3-Enterprise i prova la connexió amb un client autoritzat. No inclogues contrasenyes ni secrets RADIUS en la memòria. Si no es disposa d'un AP compatible, documenta el flux d'autenticació 802.1X entre suplicant, AP i servidor RADIUS.

5. Pràctica 3 - VPN d'accés remot i site-to-site
5.1. Accés remot amb WireGuard

Configura una VPN entre vpn01 i cliente01 en VM pròpies. Utilitza una subxarxa de túnel, per exemple 10.20.30.0/24, i claus generades localment:

sudo dnf install -y wireguard-tools
umask 077
wg genkey | tee privatekey | wg pubkey > publickey


En Debian o Ubuntu, instal·la wireguard mitjançant apt. En vpn01 crea /etc/wireguard/wg0.conf amb una adreça 10.20.30.1/24, port UDP 51820, la seua clau privada i un parell autoritzat amb AllowedIPs = 10.20.30.2/32. Configura el client amb 10.20.30.2/24, la clau pública de vpn01, l'endpoint d'entorn de proves i només les xarxes internes necessàries en AllowedIPs.

Permet UDP 51820 en el firewall únicament des de l'entorn de proves i activa els dos extrems amb sudo systemctl enable --now wg-quick@wg0. Comprova l'estat amb sudo wg show, verifica la connectivitat i documenta si utilitzes split tunneling o full tunneling. Les claus privades s'han d'ocultar en qualsevol evidència entregada.

5.2. Site-to-site amb pfSense

Construïx dos seus en VirtualBox amb dos pfSense, una WAN compartida d'entorn de proves, dos LAN diferents i una VM client en cada LAN:

Seu	LAN d'exemple	Túnel WireGuard d'exemplePrincipal	192.168.23.0/24	10.69.69.1/30
Secundària	192.168.17.0/24	10.69.69.2/30

En cada pfSense crea un túnel WireGuard, genera les seues claus i crea el parell amb la clau pública de l'extrem oposat. Configura com a xarxes permeses la xarxa del túnel i la LAN remota; assigna la interfície del túnel i crea regles que permeten exclusivament els servicis requerits entre les dos LAN. En WAN, permet UDP al port del túnel només des de l'adreça WAN del parell quan siga possible.

Comprova des dels clients de les dos seus que el trànsit autoritzat travessa el túnel i que el no autoritzat queda bloquejat. Com a alternativa documentada, implementa el mateix escenari amb OpenVPN o IPsec IKEv2 des dels assistents de pfSense, utilitzant xifratges actuals i regles equivalents. No utilitzes PPTP en cap cas.

6. Pràctica 4 - Captura de trànsit i IDS/IPS
6.1. Captura autoritzada

Captura trànsit generat per les teues pròpies VM mentre realitzes una consulta DNS i connexions HTTP i HTTPS a servicis de prova:

sudo tcpdump -i INTERFAZ -nn -w ud6-pruebas.pcapng


Amb Wireshark, identifica IP i port origen/destinació, protocol, establiment TCP i consulta/resposta DNS. Compara quin contingut pot observar-se en HTTP davant HTTPS. Les captures poden contindre dades sensibles; no compartisques cookies, credencials, claus ni trànsit d'altres persones.

6.2. Suricata o Snort en pfSense

En el firewall de la pràctica 1, instal·la Suricata o Snort des de System > Package Manager. Deshabilita les opcions de hardware offloading de la VM si el producte ho requerix. Activa inicialment el mode IDS, instal·la un conjunt gratuït de regles, selecciona una interfície d'entorn de proves i actualitza les regles.

Genera únicament trànsit benigne i autoritzat entre les teues VM, com peticions HTTP a la DMZ o connexions repetides a un servici de prova. Revisa alertes i registra data, origen, destinació, regla, classificació, gravetat i possible fals positiu. Després de validar el mode IDS, valora de manera raonada quines regles podrien bloquejar-se en mode IPS i durant quant de temps. No actives bloqueig generalitzat sense una reversió preparada.

Explica la diferència entre un sensor connectat a SPAN/TAP i un IPS en línia. Com a ampliació, investiga com Security Onion centralitza Suricata, Zeek i registres de xarxa per a investigació, sense desplegar-lo si els recursos de l'equip no són suficients.

7. Pràctica 5 - Proxy directe i invers
7.1. Proxy directe amb Squid

En una VM AlmaLinux 9 instal·la Squid i permet el port només des de la subxarxa d'entorn de proves:

sudo dnf install -y squid
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.bak


Definix una ACL per a la xarxa de pràctiques i revisa que les regles s'avaluen en orde. La configuració ha de permetre només els clients autoritzats i acabar amb una denegació general. Configura el navegador d'una VM client perquè utilitze el proxy i revisa /var/log/squid/access.log.

Implementa una llista de bloqueig exclusivament amb dominis de prova o ficticis. Documenta per què el filtratge HTTPS sense una arquitectura d'inspecció i certificats gestionats té limitacions de privacitat i compatibilitat.

7.2. Proxy invers amb Nginx

En una VM Linux crea dos servicis HTTP de prova en ports diferents i configura Nginx com a proxy invers. Verifica que s'accedix a cada servici mitjançant rutes distintes, sense exposar directament els ports interns. Com a ampliació, utilitza un bloc upstream per a repartir sol·licituds entre dos backends propis i comprova el comportament quan un deixa de respondre.

Explica quina protecció afig un WAF davant d'una aplicació i quins controls continuen sent responsabilitat de la pròpia aplicació: validació d'entrades, autenticació, actualitzacions i registres.

8. Activitats
Dissenya una taula de VLAN i una matriu de fluxos per a usuaris, administració, convidats, IoT, servidors i DMZ.
Explica quins controls limiten ARP spoofing, DHCP no autoritzat i DNS manipulable.
Compara una VPN d'accés remot amb una VPN site-to-site, incloent identitat, rutes i regles.
Proposa una política de regles de firewall amb denegació per defecte per a una aplicació web en DMZ.
Diferencia IDS, IPS, NIDS i HIDS, i explica l'impacte dels falsos positius.
Identifica quins registres s'haurien d'enviar a un SIEM des de firewall, VPN, proxy i IDS/IPS.
Dissenya mesures proporcionades per a respondre a un increment anòmal de peticions HTTP sense bloquejar usuaris legítims.
9. Autoavaluació
Què és una DMZ?
Quina diferència existix entre VLAN i subxarxa?
Què controla 802.1X?
Per què WEP i TKIP són insegurs?
Quina diferència existix entre una VPN site-to-site i una d'accés remot?
Quina funció té AllowedIPs en WireGuard?
Què és una política de denegació per defecte?
Quina diferència hi ha entre un IDS i un IPS?
Què pot revelar una captura HTTP que HTTPS ben configurat no mostra?
Quina funció té un proxy invers?
Quins riscos de disponibilitat o privacitat planteja un proxy?
Quins principis aplica Zero Trust?
10. Tasca avaluable única - Disseny d'una xarxa segura

Entrega una memòria en PDF o Markdown per a una empresa de 50 usuaris, una seu secundària, teletreball, servicis web publicats i WLAN per a convidats. Inclou:

Diagrama lògic amb VLAN, subxarxes, DMZ, WLAN, seus, VPN i controls.
Inventari d'actius, amenaces i punts de control.
Taula de VLAN, direccionament i regles de firewall amb denegació per defecte.
Disseny WLAN amb autenticació, convidats i control d'accés.
Proposta de VPN d'accés remot o site-to-site amb rutes, DNS, MFA i revocació.
Ubicació i funció de firewall, IDS/IPS, proxy, WAF, registres i monitorització.
Mesures de mitigació DDoS i aplicació gradual de Zero Trust.
Pla de proves amb evidències esperades, reversió i justificació tècnica.
Criteri	PesAmenaces, actius i segmentació	20 %
Firewall, DMZ i regles de mínim privilegi	20 %
Seguretat WLAN i control d'accés	15 %
VPN i accés remot segur	15 %
Detecció, registres i resposta	15 %
Proxy, WAF, DDoS i Zero Trust	5 %
Diagrama, evidències i justificació	10 %
Total	100 %
11. Recursos
Documentació de pfSense
OPNsense
WireGuard
OpenVPN
FreeRADIUS
Suricata
Snort
Squid
Security Onion
NIST: Zero Trust Architecture