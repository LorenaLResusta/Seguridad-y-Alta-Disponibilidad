---
title: "4. Fortificació de Hosts. Pràctiques"
weight: 2
---

# UD4 - Pràctiques: fortificació de hosts

> Configuració segura, xifratge, auditoria i monitorització d'una màquina virtual Linux.

| Dades de les pràctiques | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Duració estimada | 10 hores |
| Entorn | Màquina virtual Linux pròpia |

## 1. Objectius

En finalitzar l'itinerari, l'alumnat serà capaç de:

- Inventariar serveis, ports, usuaris i permisos d'un host Linux.
- Aplicar el principi de mínim privilegi a usuaris, grups i fitxers.
- Configurar l'accés SSH amb claus i restriccions bàsiques.
- Crear i utilitzar un volum LUKS exclusivament d'entorn de proves.
- Actualitzar el sistema i analitzar recomanacions de seguretat amb Lynis.
- Revisar registres i recursos locals, i interpretar alertes de monitorització.
- Documentar mesures de fortificació i justificar-ne l'aplicació.

## 2. Abast i preparació

Realitza totes les tasques en una màquina virtual pròpia i crea una *snapshot* inicial anomenada `ud4-inici`. No apliques comandaments de xifratge, esborrat, escaneig ni modificació d'SSH a equips aliens, sistemes de producció o discos amb dades personals.

1. Actualitza el sistema i instal·la les eines bàsiques:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf update -y
sudo dnf install openssh-server lynis cryptsetup htop -y

# Debian o Ubuntu
sudo apt update && sudo apt upgrade -y
sudo apt install openssh-server lynis cryptsetup htop -y

Crea un directori per a les evidències de text:
mkdir -p ~/ud4-evidencias
chmod 700 ~/ud4-evidencias

3. Pràctica 1 - Inventari, usuaris i permisos
3.1. Inventari inicial

Guarda un inventari bàsic de l'host abans de modificar-lo:

hostnamectl | tee ~/ud4-evidencias/hostname.txt
id | tee ~/ud4-evidencias/usuario-actual.txt
ss -tulnp | tee ~/ud4-evidencias/puertos.txt
systemctl list-units --type=service --state=running | tee ~/ud4-evidencias/servicios.txt


Identifica quin servei escolta en cada port i assenyala'n un que podria deshabilitar-se si no fora necessari per a la funció de l'equip.

3.2. Mínim privilegi
Crea un grup i dos usuaris d'entorn de proves:
sudo groupadd proyecto-ud4
sudo useradd -m -G proyecto-ud4 lorena
sudo useradd -m alumno-prueba

Crea un directori compartit només pel grup i verifica l'accés:
sudo mkdir -p /srv/proyecto-ud4
sudo chown root:proyecto-ud4 /srv/proyecto-ud4
sudo chmod 2770 /srv/proyecto-ud4
ls -ld /srv/proyecto-ud4

Explica el significat del bit especial 2 en 2770 i per què 777 no seria adequat. Comprova que l'usuari lorena pertany al grup i que alumno-prueba no pot crear fitxers en el directori.
4. Pràctica 2 - Fortificació de l'accés SSH
4.1. Claus i configuració

Utilitza una segona màquina virtual o una segona sessió per a mantindre l'accés al servidor mentre canvies la configuració.

Genera una clau en el client i copia només la clau pública al servidor:
ssh-keygen -t ed25519 -C "lorena-ud4"
ssh-copy-id lorena@IP_SERVIDOR
ssh lorena@IP_SERVIDOR

En el servidor, crea un fragment de configuració. Substituïx lorena per l'usuari autoritzat:
sudo tee /etc/ssh/sshd_config.d/ud4-hardening.conf > /dev/null <<'EOF'
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers lorena
MaxAuthTries 3
EOF
sudo sshd -t
sudo systemctl reload sshd


En Debian o Ubuntu, el servei pot anomenar-se ssh; adapta únicament l'últim comandament si fora necessari. Verifica la connexió amb clau des d'una altra sessió abans de tancar l'actual. Guarda una còpia del fragment de configuració i explica quin risc mitiga cada directiva.

4.2. Revisió d'accessos

Consulta intents d'accés i sessions actuals:

last -a | head -n 20
sudo journalctl -u sshd --since "today" || sudo journalctl -u ssh --since "today"


Indica quins esdeveniments revisaries davant de diversos errors consecutius d'inici de sessió.

5. Pràctica 3 - Xifratge LUKS d'un volum d'entorn de proves

Esta pràctica requerix un disc virtual addicional buit, per exemple /dev/sdb. Confirma'n el nom amb lsblk i no continues si el dispositiu conté particions o dades que necessites conservar.

Identifica el disc addicional:
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS

Xifra, obri i crea un sistema de fitxers en el disc d'entorn de proves:
sudo cryptsetup luksFormat /dev/sdb
sudo cryptsetup open /dev/sdb ud4-cifrado
sudo mkfs.ext4 /dev/mapper/ud4-cifrado
sudo mkdir -p /mnt/ud4-cifrado
sudo mount /dev/mapper/ud4-cifrado /mnt/ud4-cifrado
echo "Dato de prueba" | sudo tee /mnt/ud4-cifrado/evidencia.txt

Comprova l'estat, desmunta i tanca el volum:
sudo cryptsetup status ud4-cifrado
sudo umount /mnt/ud4-cifrado
sudo cryptsetup close ud4-cifrado


Documenta les fases de creació, obertura, muntatge, accés, desmuntatge i tancament. Explica com custodiaries una clau de recuperació i per què el xifratge no substituïx les còpies de seguretat.

6. Pràctica 4 - Actualització i auditoria amb Lynis
6.1. Actualització controlada

Registra les actualitzacions disponibles, aplica les corresponents i reinicia només si el sistema ho sol·licita:

# AlmaLinux, Rocky Linux o Fedora
sudo dnf check-update || true
sudo dnf update -y

# Debian o Ubuntu
sudo apt update
apt list --upgradable
sudo apt upgrade -y


Anota quines comprovacions realitzaries abans d'actualitzar un servidor crític: còpies, finestra de manteniment, dependències, pla de reversió i validació posterior.

6.2. Auditoria local
Executa Lynis en la màquina virtual:
sudo lynis audit system | tee ~/ud4-evidencias/lynis-inicial.txt


Selecciona cinc recomanacions. Per a cadascuna, indica el risc, la mesura proposada, si és aplicable a l'entorn i el resultat després de revisar-la. No apliques canvis que no comprengues ni que puguen impedir l'arrancada o l'accés a la màquina.

Repetix l'auditoria després d'aplicar únicament millores segures i documentades.

7. Pràctica 5 - Monitorització centralitzada amb Wazuh

Esta pràctica es realitza només amb un servidor Wazuh proporcionat pel professorat i una màquina virtual pròpia. No registres equips aliens ni modifiques regles globals de la plataforma.

7.1. Instal·lació i registre de l'agent
Obtín del professorat l'adreça del servidor Wazuh, el mètode de registre i el grup assignat a l'agent.
Instal·la l'agent seguint la documentació oficial de Wazuh per a la teua distribució.
Comprova que el servei està actiu i guarda'n l'evidència:
sudo systemctl status wazuh-agent --no-pager | tee ~/ud4-evidencias/wazuh-agente.txt
sudo journalctl -u wazuh-agent --since "today" --no-pager | tail -n 30 | tee ~/ud4-evidencias/wazuh-registro.txt

En el panell de Wazuh, verifica que l'agent apareix connectat. Registra el nom de l'host, l'adreça privada assignada, el grup i l'hora de l'última connexió.
7.2. Esdeveniments i supervisió d'integritat
Realitza un únic inici de sessió fallit contra el teu propi compte i localitza l'alerta corresponent en Wazuh. Anota la regla, el nivell, l'hora, l'usuari i l'host.
Crea un fitxer de prova en un directori supervisat per l'agent segons la configuració facilitada pel professorat. Comprova que Wazuh informa del canvi d'integritat i conserva una captura o exportació de l'alerta.
Per a cada alerta, explica quina evidència aporta, quin possible impacte té i quina seria la primera mesura de contenció.

Si no hi ha servidor Wazuh disponible, utilitza una demostració o un informe d'exemple proporcionat pel professorat. Identifica-hi l'agent, la regla, el nivell d'alerta, la font de l'esdeveniment i l'acció recomanada.

8. Pràctica 6 - Monitorització local i registres
8.1. Recursos i serveis

Observa l'estat de l'host i registra una evidència de cada comandament:

htop
df -h
free -h
systemctl --failed
ss -tulnp


Identifica un procés, un servei, una connexió o port en escolta, i l'ús de disc i memòria. Distingix entre un estat normal i una dada que requeriria investigació.

8.2. Logs i esdeveniments controlats

Consulta esdeveniments recents i els del servei SSH:

sudo journalctl -xe --no-pager | tail -n 50
sudo journalctl -u sshd --since "today" || sudo journalctl -u ssh --since "today"


Genera un únic error d'autenticació contra el teu propi compte d'entorn de proves i localitza l'esdeveniment corresponent. Documenta l'hora, el servei, l'usuari i el resultat; no realitzes atacs de força bruta.

10. Autoavaluació
Quin objectiu principal té el hardening?
Quin principi establix que un usuari ha de disposar únicament dels permisos necessaris?
Quina diferència existix entre autenticació i autorització?
Quin risc mitiga Secure Boot?
Què protegix principalment el xifratge de disc?
Per què una clau privada SSH no s'ha de compartir?
Per a què servix Lynis?
Quines etapes formen el cicle de gestió de vulnerabilitats?
Quina informació poden proporcionar els logs?
Quina funció pot realitzar Wazuh?
Quina diferència existix entre un IDS i un IPS?
Per què és important comprovar una actualització després de desplegar-la?
Quins riscos presenta un servei innecessari exposat a Internet?
Per què una anàlisi de vulnerabilitats requerix autorització prèvia?
11. Tasca avaluable única - Fortificació d'un servidor

Entrega un informe en PDF o Markdown amb captures pròpies i explicacions redactades amb les teues paraules de la pràctica de WAZUH.

12. Recursos
CIS Benchmarks
Documentació d'OpenSSH
Cryptsetup i LUKS
Lynis
Greenbone Community Edition
Wazuh
OpenSCAP
CISA: Secure by Design