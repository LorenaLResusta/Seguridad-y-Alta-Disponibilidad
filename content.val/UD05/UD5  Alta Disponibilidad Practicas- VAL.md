---
title: "5. Alta disponibilitat. Pràctiques"
weight: 2
---

# UD5 - Pràctiques: alta disponibilitat

> Disseny, desplegament i validació de serveis redundants en entorns de proves virtualitzats.

| Dades de les pràctiques | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Duració estimada | 8 hores |
| Entorn | Màquines virtuals i xarxes d'entorn de proves pròpies |

## 1. Objectius

- Identificar SPOF i definir objectius de disponibilitat, RPO i RTO.
- Desplegar WordPress en dos nodes web amb una base de dades independent.
- Configurar HAProxy amb comprovacions de salut i balanceig de càrrega.
- Configurar una IP virtual amb VRRP i Keepalived en una xarxa aïllada.
- Interpretar i validar recursos, quòrum i *fencing* en Pacemaker i Corosync.
- Dissenyar una plataforma virtualitzada disponible amb Proxmox i emmagatzematge distribuït.

## 2. Abast i preparació

Les pràctiques s'executen exclusivament en màquines virtuals, xarxes internes i adreces IP de l'entorn de proves. Abans de començar, crea una *snapshot* de cada VM. No utilitzes IP virtuals, rutes, regles de NAT, configuracions de clúster ni credencials en xarxes alienes o de producció.

L'itinerari principal requerix quatre VM AlmaLinux 9 connectades a una xarxa interna i amb accés temporal a Internet per a instal·lar paquets:

| VM | Hostname | Recursos mínims | Funció |
| --- | --- | --- | --- |
| Balancejador | `balancer01` | 1 vCPU, 1-2 GiB RAM | HAProxy. |
| Web 1 | `web01` | 1 vCPU, 2 GiB RAM | Apache, PHP i WordPress. |
| Web 2 | `web02` | 1 vCPU, 2 GiB RAM | Apache, PHP i WordPress. |
| Base de dades | `db01` | 1 vCPU, 2 GiB RAM | MariaDB. |

Assigna IP estàtiques pròpies de la teua xarxa. En els exemples s'utilitzen `IP_BALANCER`, `IP_WEB1`, `IP_WEB2`, `IP_DB` i `IP_VIRTUAL`; substituïx-les per valors reals. Afig les correspondències de noms i IP en `/etc/hosts` de les quatre màquines.

```text
IP_BALANCER balancer01
IP_WEB1     web01
IP_WEB2     web02
IP_DB       db01

3. Pràctica 1 - Diagnòstic de disponibilitat
Dibuixa les dependències d'una web amb un únic router, firewall, switch, servidor web, base de dades i emmagatzematge.
Identifica almenys cinc SPOF i proposa per a cadascun una mesura proporcionada: segon enllaç, font redundant, SAI, RAID, rèplica, còpia de seguretat, balancejador o monitorització.
Calcula la disponibilitat amb $MTBF = 8,760$ hores i $MTTR = 4$ hores:
D=MTBFMTBF+MTTRD = \frac{MTBF}{MTBF + MTTR}
Calcula el temps anual d'indisponibilitat de $99.9%$, $99.99%$ i $99.999%$. Indica quines mesures reduïxen MTTR i quines augmenten MTBF.
Defineix un RPO i un RTO realistes per a la web i justifica la decisió.
4. Pràctica 2 - WordPress balancejat amb HAProxy
4.1. Preparar les màquines

En totes les VM, actualitza el sistema, activa el firewall i configura el nom d'host corresponent:

sudo dnf update -y
sudo dnf install -y vim curl wget firewalld
sudo systemctl enable --now firewalld
sudo hostnamectl set-hostname NOMBRE_DE_LA_VM


Comprova la connectivitat entre les quatre màquines mitjançant ping, la resolució de noms mitjançant getent hosts web01 i l'estat de les interfícies mitjançant ip -br a.

4.2. Configurar MariaDB en db01

Instal·la i habilita MariaDB:

sudo dnf install -y mariadb-server
sudo systemctl enable --now mariadb
sudo firewall-cmd --permanent --add-service=mysql
sudo firewall-cmd --reload


Executa sudo mysql_secure_installation i aplica les mesures sol·licitades. Després, crea una base de dades i un usuari exclusius de l'entorn de proves. Substituïx CLAVE_PRUEBAS per una contrasenya diferent de qualsevol compte personal:

sudo mysql
CREATE DATABASE wordpress CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wpuser'@'IP_WEB1' IDENTIFIED BY 'CLAVE_PRUEBAS';
CREATE USER 'wpuser'@'IP_WEB2' IDENTIFIED BY 'CLAVE_PRUEBAS';
GRANT ALL PRIVILEGES ON wordpress.* TO 'wpuser'@'IP_WEB1';
GRANT ALL PRIVILEGES ON wordpress.* TO 'wpuser'@'IP_WEB2';
FLUSH PRIVILEGES;
EXIT;


Comprova que MariaDB escolta només en l'adreça interna necessària. No habilites l'accés remot de root ni exposes el port MySQL fora de la xarxa de l'entorn de proves.

4.3. Configurar web01 i web02

En tots dos nodes instal·la Apache i PHP:

sudo dnf install -y httpd php php-mysqlnd php-fpm php-gd php-xml php-mbstring tar
sudo systemctl enable --now httpd
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload


Descarrega WordPress en tots dos nodes i concedix la propietat a l'usuari d'Apache:

cd /tmp
wget https://wordpress.org/latest.tar.gz
tar xzf latest.tar.gz
sudo rm -rf /var/www/html/*
sudo cp -a wordpress/. /var/www/html/
sudo chown -R apache:apache /var/www/html
sudo cp /var/www/html/wp-config-sample.php /var/www/html/wp-config.php


Edita wp-config.php en cada node. Configura DB_NAME, DB_USER, DB_PASSWORD i DB_HOST amb la informació de db01. Completa la instal·lació inicial accedint primer a un dels nodes directament.

Els dos nodes compartixen la base de dades, però les pujades i els canvis d'arxius continuen sent un SPOF funcional si no s'utilitza emmagatzematge compartit o sincronització. No copies secrets ni arxius de producció en este entorn de proves.

4.4. Configurar HAProxy en balancer01

Instal·la HAProxy i permet HTTP:

sudo dnf install -y haproxy
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload


Guarda una còpia de /etc/haproxy/haproxy.cfg i afig al final una configuració mínima. Substituïx les IP d'exemple:

frontend wordpress_http
	bind *:80
	default_backend wordpress_nodes

backend wordpress_nodes
	balance roundrobin
	option httpchk GET /
	server web01 IP_WEB1:80 check
	server web02 IP_WEB2:80 check

listen stats
	bind *:8080
	stats enable
	stats uri /stats
	stats refresh 10s


Valida i activa el servei:

sudo haproxy -c -f /etc/haproxy/haproxy.cfg
sudo systemctl enable --now haproxy
curl -I http://localhost/


Accedix a http://IP_BALANCER/, revisa el panell http://IP_BALANCER:8080/stats des de la xarxa d'entorn de proves i documenta quins nodes apareixen actius. Detén temporalment httpd en un backend, comprova que HAProxy el retira i després restaura el servei. No confongues balanceig amb alta disponibilitat completa: el balancejador i la base de dades continuen sent dependències úniques.

5. Pràctica 3 - Gateway HA amb VRRP i Keepalived

Esta pràctica requerix dos gateways Linux i una màquina client en una xarxa interna aïllada. Cada gateway necessita una interfície WAN amb accés a Internet i una altra interfície LAN. Exemple de LAN:

Equip	IP LANgateway1	192.168.100.2/24
gateway2	192.168.100.3/24
IP virtual VRRP	192.168.100.1/24
Client	192.168.100.10/24, gateway 192.168.100.1
5.1. Activar encaminament i NAT

En tots dos gateways, habilita temporalment el reenviament IP i després fes-lo persistent en un fitxer de /etc/sysctl.d/:

sudo sysctl -w net.ipv4.ip_forward=1
echo 'net.ipv4.ip_forward = 1' | sudo tee /etc/sysctl.d/99-ha-routing.conf
sudo sysctl --system


Assigna la interfície WAN a la zona public i la LAN a internal, adaptant els noms reals. Habilita NAT únicament cap a la WAN:

sudo firewall-cmd --permanent --zone=public --change-interface=INTERFAZ_WAN
sudo firewall-cmd --permanent --zone=internal --change-interface=INTERFAZ_LAN
sudo firewall-cmd --permanent --zone=public --add-masquerade
sudo firewall-cmd --permanent --zone=internal --set-target=ACCEPT
sudo firewall-cmd --reload


Des del client, prova primer l'eixida utilitzant la IP real de cada gateway. Verifica les rutes amb ip route i, si està disponible, traceroute 8.8.8.8.

5.2. Configurar Keepalived

Instal·la Keepalived en tots dos gateways:

sudo dnf install -y keepalived


En gateway1, crea /etc/keepalived/keepalived.conf. Adapta la interfície LAN i utilitza una clau d'entorn de proves:

vrrp_instance VI_1 {
	state MASTER
	interface INTERFAZ_LAN
	virtual_router_id 51
	priority 120
	advert_int 1
	authentication {
		auth_type PASS
		auth_pass CLAVE_LAB
	}
	virtual_ipaddress {
		192.168.100.1/24
	}
}


En gateway2, utilitza el mateix virtual_router_id, interfície i adreça virtual, però configura state BACKUP i priority 100. Inicia el servei en tots dos nodes:

sudo systemctl enable --now keepalived
ip -br address


Configura el client perquè utilitze 192.168.100.1 com a gateway. Mantín un ping 8.8.8.8 actiu des del client, desconnecta únicament la interfície LAN del gateway principal en la configuració de la VM i verifica que la IP virtual apareix en el node de reserva. Restaura la interfície i anota el temps de commutació i els paquets perduts.

7. Pràctica 5 Avaluable - Màquines virtuals amb Proxmox

Esta pràctica necessita tres nodes Proxmox dedicats. La virtualització imbricada pot ser lenta i no substituïx la validació en maquinari compatible.

Instal·la tres nodes Proxmox amb IP estàtiques, connectivitat mútua i un segon disc lliure en cada node per a Ceph. Cada node ha de comptar amb almenys 2 GiB de RAM; augmenta els recursos quan l'equip amfitrió ho permeta.
Crea el clúster des del primer node mitjançant la interfície web en Datacenter > Cluster > Create Cluster i unix els altres mitjançant Join Cluster, o utilitza pvecm create NOMBRE_CLUSTER i pvecm add IP_NODO_PRINCIPAL.
Verifica l'estat amb pvecm status. Explica per què tres nodes faciliten mantindre el quòrum davant una caiguda.
Instal·la Ceph en els nodes des de Datacenter > Ceph, crea un OSD amb el disc secundari de cada node i un pool per a les VM. Comprova que l'estat siga HEALTH_OK abans de continuar.
Crea una VM Debian o Ubuntu Server amb el disc en el pool Ceph. Instal·la SSH per a comprovar la connectivitat i realitza una migració controlada des de la interfície de Proxmox.
Crea un grup HA, afig els tres nodes i registra la VM com a recurs HA. Simula la indisponibilitat d'un node segons el procediment del professorat; mesura la interrupció mitjançant ping i una sessió SSH des d'una altra màquina.
9. Autoavaluació
Què és un SPOF?
Què representen MTBF i MTTR?
Quina diferència hi ha entre RPO i RTO?
Per què RAID no substituïx una còpia de seguretat?
Què comprova option httpchk en HAProxy?
Quina funció té una IP virtual VRRP?
Quina diferència existix entre un balancejador i un proxy invers?
Quines funcions exercixen Corosync i Pacemaker?
Quin risc evita el quòrum?
Què és fencing?
Per què tres nodes són preferibles a dos per al quòrum de Proxmox?
Quines dependències s'han de comprovar abans d'afirmar que una VM està en alta disponibilitat?
11. Recursos
HAProxy
Keepalived
Pacemaker
Corosync
Proxmox VE
Ceph
OpenStack
WordPress amb HAProxy