---
title: "7. Seguretat perimetral. Pràctiques"
weight: 2
---

# UD7 - Pràctiques: seguretat perimetral

> Configuració i validació de controls perimetrals mitjançant evidències tècniques reproduïbles.

| Dades de les pràctiques | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Duració estimada | 8 hores |
| Entorn | Màquines virtuals, xarxes i serveis d'entorn de proves |

## 1. Objectius

- Dissenyar un perímetre amb WAN, LAN, DMZ i xarxa de gestió.
- Aplicar polítiques de firewall amb denegació per defecte i mínim privilegi.
- Configurar NAT d'eixida i publicar serveis de manera controlada.
- Analitzar registres de firewall i comprovar regles permeses i denegades.
- Configurar proxy directe, proxy invers i controls d'aplicació.
- Valorar la disponibilitat i la recuperació dels serveis perimetrals.

## 2. Abast i preparació

Totes les accions es realitzen exclusivament sobre VM, adreces, xarxes i serveis autoritzats. No publiques serveis d'administració a Internet, no modifiques firewalls de producció i no generes trànsit de denegació de servei.

Abans de cada pràctica, crea una *snapshot* de les màquines afectades. Mantín una taula de treball amb interfícies, adreces, regles, canvis i resultat de cada prova. Les evidències consistiran en exportacions de configuració sense secrets, eixides de comandaments, extractes anonimitzats de logs i taules de resultats.

L'escenari base utilitza un firewall pfSense o OPNsense, una VM client en LAN i una VM servidor en DMZ. Per a les pràctiques de proxy i alta disponibilitat es pot afegir una o més VM Linux pròpies.

## 3. Pràctica 1 - Perímetre, zones i política base

### 3.1. Topologia i direccionament

Configura un firewall amb les següents zones:

| Zona | Xarxa d'exemple | Funció |
| --- | --- | --- |
| WAN | NAT o pont d'entorn de proves | Connexió externa simulada. |
| LAN | `192.168.20.0/24` | Equips corporatius. |
| DMZ | `192.168.30.0/24` | Serveis publicats. |
| Gestió | `192.168.99.0/24` | Administració restringida. |

Assigna al firewall la primera adreça útil de cada subxarxa. Configura client i servidor amb adreces coherents, passarel·la i DNS d'entorn de proves. Descriu quines interfícies o VLAN representen cada zona i quins actius han de residir-hi.

### 3.2. Política de mínim privilegi

Crea una matriu de filtratge inicial:

| Origen | Destinació | Servei | Acció | Motiu |
| --- | --- | --- | --- | --- |
| LAN | WAN | DNS, HTTP i HTTPS | Permetre | Accés corporatiu necessari. |
| LAN | DMZ | ICMP, HTTP, HTTPS i SSH | Permetre | Ús i administració controlats. |
| DMZ | LAN | Qualsevol | Denegar | Contenció d'un servidor publicat. |
| Gestió | Firewall i equips | HTTPS i SSH | Permetre | Administració restringida. |
| Qualsevol zona | Qualsevol destinació no definida | Qualsevol | Denegar | Política per defecte. |

Aplica les regles en l'orde adequat i comprova els fluxos des de les VM. Entrega la taula final de regles i una taula de resultats amb origen, destinació, servei, resultat esperat i resultat obtingut.

## 4. Pràctica 2 - NAT i publicació segura en DMZ

### 4.1. Servidor web d'entorn de proves

En la VM de DMZ instal·la un servidor web de prova i limita el seu firewall local als serveis necessaris:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf install -y httpd
sudo systemctl enable --now httpd
echo 'Servicio web de la DMZ' | sudo tee /var/www/html/index.html

# Debian o Ubuntu
sudo apt update && sudo apt install -y apache2
sudo systemctl enable --now apache2
echo 'Servicio web de la DMZ' | sudo tee /var/www/html/index.html


Comprova el servei des de LAN mitjançant curl i conserva l'eixida com a evidència. El servidor de la DMZ no ha d'incloure serveis o comptes que no siguen necessaris per a la pràctica.

4.2. NAT i regles associades

Configura NAT d'eixida per a LAN i, només si està justificat, per a DMZ. Publica HTTPS des d'una IP o port WAN d'entorn de proves cap al servidor de DMZ. Com a exercici addicional, utilitza un port extern no estàndard per a una administració SSH temporal, limitada a una IP d'origen d'entorn de proves i documenta per què esta mesura no substituïx una VPN.

Verifica que el servei web publicat respon des d'una VM externa de proves i que altres ports no publicats continuen sent inaccessibles. Revisa els registres del firewall i redacta una taula amb la traducció configurada, la regla associada i el resultat de la prova.

5. Pràctica 3 - Firewall Linux i fortificació TCP/IP

En una VM Linux d'entorn de proves, identifica el sistema de filtratge actiu:

sudo firewall-cmd --list-all
sudo nft list ruleset


Crea regles que permeten el servei web només des de la subxarxa LAN de la pràctica. Valida des d'una VM permesa i una altra situada en una xarxa no autoritzada. Abans de modificar paràmetres del nucli, revisa el seu valor actual:

sysctl net.ipv4.ip_forward
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.log_martians


En un host que no siga router, guarda esta configuració en /etc/sysctl.d/99-perimetro.conf:

net.ipv4.ip_forward = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.log_martians = 1


Aplica els canvis amb sudo sysctl --system, verifica els valors i explica per què no s'han d'aplicar sense adaptació en un gateway, un firewall o un servidor VPN.

6. Pràctica 4 - Registre, alertes i resposta inicial

Activa el registre de les regles de bloqueig rellevants en el firewall de l'entorn de proves. Genera de manera controlada un intent de connexió no permés des de LAN a DMZ i un altre des de DMZ a LAN. No utilitzes tècniques d'evasió ni eines contra destinacions alienes.

Per a cada esdeveniment, arreplega data i hora, interfície, IP d'origen i destinació, protocol, port, regla aplicada i acció. Sincronitza l'hora de les VM i proposa quins esdeveniments s'haurien d'enviar a un servidor de logs o SIEM: canvis de regles, autenticacions administratives, bloquejos repetits, errors VPN i alertes IDS/IPS.

Elabora un procediment breu de resposta: validació de l'alerta, contenció, conservació d'evidències, comunicació, correcció i revisió posterior. Distingix una alerta que requerix investigació d'un fals positiu documentat.

7. Pràctica 5 - Proxy directe amb Squid

Instal·la Squid en una VM AlmaLinux 9 i crea una còpia de seguretat de la configuració:

sudo dnf install -y squid
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.bak


Definix una ACL per a la subxarxa LAN de pràctiques. Ordena les directives per a aplicar primer bloquejos específics, després autorització de clients permesos i finalment http_access deny all. Valida la sintaxi i activa el servici:

sudo squid -k parse
sudo systemctl enable --now squid


Configura una VM client perquè utilitze el proxy en IP_SQUID:3128. Prova una destinació d'entorn de proves permesa i una entrada de bloqueig basada en un domini de proves o fictici. Analitza /var/log/squid/access.log i identifica client, destinació, mètode HTTP i resultat. Explica les limitacions de filtrar HTTPS sense una arquitectura d'inspecció TLS, certificats gestionats i requisits de privacitat.

8. Pràctica 6 - Proxy invers, TLS i WAF

En una VM Linux executa dos serveis HTTP de prova propis en els ports 8081 i 8082. Instal·la Nginx i configura un proxy invers que publique els dos serveis sota rutes diferents:

server {
    listen 80;
    server_name _;

    location /app-a/ {
        proxy_pass http://127.0.0.1:8081/;
    }

    location /app-b/ {
        proxy_pass http://127.0.0.1:8082/;
    }
}


Valida amb sudo nginx -t, activa el servici i prova les rutes amb curl. Demostra que els ports interns no s'exposen a les altres VM. Afig TLS amb un certificat d'entorn de proves i comprova el protocol i certificat utilitzat amb:

curl -vk https://HOST_DE_PRUEBAS/


Investiga un WAF compatible amb l'entorn, com ModSecurity amb el conjunt de regles OWASP CRS. Explica on se situaria, quins tipus de sol·licituds pot inspeccionar i per què ha d'iniciar-se en mode de detecció abans d'habilitar bloquejos. No generes càrregues d'atac contra aplicacions alienes.

9. Pràctica 7 - Alta disponibilitat i recuperació del perímetre

Dissenya una proposta per a evitar que el firewall siga un SPOF. Inclou dos firewalls, enllaços redundants, alimentació, xarxa de gestió, DNS, sincronització de configuració o estat, adreça virtual i monitorització. Indica quin model utilitzaries, actiu-passiu o actiu-actiu, i per què.

En un entorn de proves que dispose de recursos, configura un parell de firewalls amb una adreça virtual mitjançant CARP o una alternativa equivalent. Realitza una commutació planificada i registra temps d'interrupció, comportament de les connexions existents, registres generats i recuperació del node original. Si l'entorn de proves no disposa de dos firewalls, presenta el disseny, la seqüència de commutació i el pla de proves sense realitzar el desplegament.

Realitza una còpia de la configuració, guarda-la xifrada en una ubicació d'entorn de proves separada i descriu el procediment per a restaurar-la en una VM de substitució.

10. Activitats
Compara firewall de paquets, stateful, d'aplicació i NGFW segons visibilitat i limitacions.
Dissenya la matriu de comunicacions per a Internet, LAN, DMZ, VPN i gestió.
Explica per què NAT no substituïx el filtratge de firewall.
Proposa controls per a un servidor web en DMZ que necessita una base de dades interna.
Analitza cinc esdeveniments de firewall i prioritza quins investigaries.
Compara proxy directe, proxy invers i WAF segons els actius que protegixen.
Identifica els SPOF d'una arquitectura amb firewall, enllaç WAN, DNS i proxy únics.
11. Autoavaluació
Quina funció complix un firewall?
Quina diferència existix entre filtratge de paquets i stateful?
Què significa denegar per defecte?
Què és NAT i què no protegix per si mateix?
Què és una DMZ?
Per què DMZ-LAN ha de ser especialment restrictiu?
Quina informació aporta un registre de firewall?
Quina diferència existix entre proxy directe i invers?
Què limita el filtratge d'HTTPS sense inspecció TLS?
Quina funció pot realitzar un WAF?
Per què un firewall pot ser un SPOF?
Què ha d'incloure una prova de commutació?
12. Tasca avaluable única - Disseny de seguretat perimetral

Entrega una memòria en PDF o Markdown per a una empresa de 40 usuaris amb una seu, serveis interns, una aplicació web pública, WLAN corporativa i de convidats, accés remot i necessitat de controlar la navegació.

La memòria ha d'incloure:

Diagrama lògic amb WAN, LAN, DMZ, VPN, gestió, firewall, proxy i controls de monitorització.
Inventari d'actius, amenaces i punts únics de fallada.
Taula de xarxes i matriu de regles de firewall amb denegació per defecte.
Disseny de NAT, publicació del servici web i controls DMZ-LAN.
Proposta de proxy directe, proxy invers i WAF quan siga procedent.
Registres, alertes i procediment bàsic de resposta.
Mesures de disponibilitat, actualitzacions, còpia de configuració i recuperació.
Pla de proves amb resultats esperats, reversió i justificació tècnica.
Criteri	PesArquitectura, actius i amenaces	15 %
Firewall, regles i segmentació	25 %
NAT, DMZ i publicació segura	15 %
Registres, resposta i firewall Linux	10 %
Proxies, TLS i WAF	15 %
Disponibilitat i recuperació del perímetre	10 %
Evidències tècniques i justificació	10 %
Total	100 %
13. Recursos
Documentació de pfSense
OPNsense
Netfilter
nftables
Squid
Nginx: reverse proxy
OWASP ModSecurity Core Rule Set
CARP en pfSense

 ```