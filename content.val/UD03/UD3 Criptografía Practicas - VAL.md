---
title: "3. Criptografia. Pràctiques"
weight: 2
---

# UD3 - Pràctiques: criptografia

> Hashes, xifrat, signatures, certificats i PKI en un entorn Linux de proves.

| Dades de les pràctiques | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Duració estimada | 10 hores |
| Entorn | Màquina virtual Linux amb OpenSSL i GnuPG |

## 1. Objectius

En finalitzar l'itinerari, l'alumnat serà capaç de:

- Comprovar la integritat de fitxers mitjançant SHA-256.
- Generar i protegir parells de claus RSA en un entorn de proves.
- Crear sol·licituds de certificat, certificats autofirmats i una CA d'entorn de proves.
- Signar i verificar un certificat de servidor.
- Utilitzar GnuPG per a xifrar i signar dades de prova.
- Analitzar de manera autoritzada la fortalesa de contrasenyes de comptes de prova.
- Comprovar els elements principals d'una connexió TLS.
- Documentar les evidències sense divulgar claus privades.

## 2. Abast i preparació

Treballa únicament en una màquina virtual pròpia i amb dades de prova. Les claus i certificats generats en esta guia són exclusius de l'entorn de proves: no s'han d'utilitzar en producció ni per a protegir informació real. No publiques claus privades, fitxers `.key` ni contrasenyes.

1. Actualitza el sistema i instal·la les eines:

```bash
# AlmaLinux, Rocky Linux o Fedora
sudo dnf install openssl gnupg2 -y

# Debian o Ubuntu
sudo apt update
sudo apt install openssl gnupg -y

Crea el directori de treball i restringix-ne l'accés:
mkdir -p ~/ud3-criptografia/{ca,servidor,dades}
chmod 700 ~/ud3-criptografia
cd ~/ud3-criptografia


En els exemples d'esta guia s'utilitzarà la identitat fictícia Lorena L Resusta <lorena.resusta@exemple.com>. Substituïx les dades d'exemple per les teues quan una activitat ho sol·licite.

3. Pràctica 1 - Integritat amb funcions hash
3.1. Calcular i comprovar un hash
Crea un fitxer de prova i calcula'n el resum:
echo "Missatge de prova" > dades/missatge.txt
sha256sum dades/missatge.txt | tee dades/missatge.txt.sha256

Comprova el resum emmagatzemat:
sha256sum -c dades/missatge.txt.sha256

Modifica el fitxer i torna a comprovar-lo:
echo "Missatge modificat" > dades/missatge.txt
sha256sum -c dades/missatge.txt.sha256


Explica per què la segona comprovació falla i per què un hash permet detectar canvis, però no recuperar el contingut original.

3.2. Verificar una imatge ISO

Descarrega una imatge ISO i el seu fitxer oficial de sumes de comprovació, per exemple, des d'AlmaLinux o Debian. Calcula el SHA-256 del fitxer i compara'l amb el valor publicat pel projecte.

# Linux
sha256sum nom-de-la-imatge.iso

# Windows PowerShell
Get-FileHash .\nom-de-la-imatge.iso -Algorithm SHA256


Inclou el nom de la ISO, l'algorisme utilitzat, el valor publicat i el valor calculat. No descarregues imatges des de fonts no oficials.

4. Pràctica 2 - Claus RSA, xifrat i signatura amb GnuPG
4.1. Generar i protegir una clau RSA
Genera una clau privada RSA d'entorn de proves i limita'n els permisos:
cd ~/ud3-criptografia/servidor
openssl genrsa -out servidor.key 2048
chmod 600 servidor.key

Examina la clau sense copiar-ne el contingut en l'entrega:
openssl rsa -in servidor.key -check -noout

Obtín la clau pública associada:
openssl rsa -in servidor.key -pubout -out servidor.pub
openssl pkey -pubin -in servidor.pub -text -noout


Anota quin fitxer es pot distribuir i quin ha de romandre protegit.

4.2. Xifrat simètric amb GnuPG
Crea un fitxer confidencial de prova i xifra'l amb una frase de pas que recordes:
cd ~/ud3-criptografia
echo "Document confidencial de Lorena L Resusta" > dades/confidencial.txt
gpg --symmetric dades/confidencial.txt
file dades/confidencial.txt.gpg

Elimina l'original de prova i recupera'n una còpia:
rm dades/confidencial.txt
gpg --output dades/confidencial-recuperat.txt --decrypt dades/confidencial.txt.gpg
cat dades/confidencial-recuperat.txt


Explica què ocorreria si s'oblidara la frase de pas i per què no s'ha d'enviar juntament amb el fitxer xifrat.

4.3. Xifrat asimètric i signatura amb GnuPG
Genera un parell de claus d'entorn de proves. Utilitza les dades d'exemple Lorena L Resusta <lorena.resusta@exemple.com>, una caducitat d'un any i una contrasenya segura:
gpg --full-generate-key
gpg --list-keys
gpg --list-secret-keys

Exporta únicament la teua clau pública i importa la clau pública del professor, subministrada com fperez.asc:
gpg --output dades/lorena-l-resusta-publica.asc --armor --export "Lorena L Resusta"
gpg --import fperez.asc
gpg --list-keys
gpg --fingerprint


Verifica l'empremta digital de la clau importada per un canal fiable abans d'utilitzar-la. Substituïx ID_PROFESSOR per l'identificador o correu que mostre gpg --list-keys.

Crea un missatge amb el teu nom i la data, xifra'l per al professor i signa'l amb la teua clau:
printf 'Missatge creat per Lorena L Resusta el %s\n' "$(date +%F)" > dades/missatge-lorena.txt
gpg --armor --output dades/missatge-lorena.asc --encrypt --sign \
	--local-user "Lorena L Resusta" --recipient ID_PROFESSOR dades/missatge-lorena.txt


Com a entrega d'esta activitat, utilitza missatge-lorena.asc i lorena-l-resusta-publica.asc. No inclogues la clau privada ni la seua contrasenya. Descriu la diferència entre xifrar, signar i xifrar juntament amb signar.

5. Pràctica 3 - Auditoria controlada de contrasenyes

Esta pràctica només està autoritzada sobre comptes creats expressament en la màquina virtual pròpia. No copies, analyses ni entregues hashes de comptes reals o d'altres sistemes.

5.1. Comptes i emmagatzematge de credencials
Crea dos comptes de prova amb contrasenyes dèbils conegudes exclusivament per a l'entorn de proves:
sudo useradd -m lorena_lab
sudo passwd lorena_lab
sudo useradd -m pedro_lab
sudo passwd pedro_lab

Comprova on s'emmagatzemen la informació pública dels usuaris i els hashes de contrasenya, així com els seus permisos:
getent passwd lorena_lab pedro_lab
sudo ls -l /etc/passwd /etc/shadow
sudo grep -E '^(lorena_lab|pedro_lab):' /etc/shadow


Explica la funció de /etc/passwd i /etc/shadow, el significat general dels camps separats per : i per què els hashes de dos usuaris amb la mateixa contrasenya poden ser diferents.

5.2. Auditoria amb John the Ripper

Instal·la John the Ripper des dels repositoris disponibles en la teua distribució o utilitza la instal·lació proporcionada pel docent:

# Debian o Ubuntu
sudo apt install john -y

# AlmaLinux, Rocky Linux o Fedora amb EPEL disponible
sudo dnf install epel-release -y
sudo dnf install john -y


Genera un fitxer temporal limitat als dos comptes de prova i analitza únicament eixe fitxer:

sudo unshadow /etc/passwd /etc/shadow > /tmp/ud3-comptes-complets.txt
sudo grep -E '^(lorena_lab|pedro_lab):' /tmp/ud3-comptes-complets.txt > ~/ud3-criptografia/dades/hashes-prova.txt
john ~/ud3-criptografia/dades/hashes-prova.txt
john --show ~/ud3-criptografia/dades/hashes-prova.txt
rm -f /tmp/ud3-comptes-complets.txt ~/ud3-criptografia/dades/hashes-prova.txt


Documenta el resultat sense incloure el fitxer de hashes ni les contrasenyes en l'entrega. Relaciona la prova amb l'ús de funcions de derivació com Argon2, bcrypt, scrypt o PBKDF2, amb salt únic i amb polítiques de contrasenyes robustes.

6. Pràctica 4 - CSR i certificat autofirmat
6.1. Crear una sol·licitud de certificat
Genera una CSR a partir de la clau del servidor. Quan OpenSSL sol·licite el nom comú, utilitza servidor.lan:
cd ~/ud3-criptografia/servidor
openssl req -new -key servidor.key -out servidor.csr

Consulta'n el contingut:
openssl req -in servidor.csr -text -noout


Explica per què una CSR conté una clau pública, però no ha de contindre la clau privada.

6.2. Crear un certificat autofirmat
Genera un certificat vàlid durant 365 dies per a proves:
openssl req -x509 -new -key servidor.key -out servidor-autofirmat.crt -days 365

Examina emissor, subjecte, validesa i clau pública:
openssl x509 -in servidor-autofirmat.crt -text -noout


Indica per què este certificat és apropiat per a un entorn de proves, però no genera confiança automàtica en els navegadors.

7. Pràctica 5 - CA i certificat de servidor
7.1. Crear una CA d'entorn de proves
Genera la clau i el certificat arrel de la CA:
cd ~/ud3-criptografia/ca
openssl genrsa -out ca.key 4096
chmod 600 ca.key
openssl req -x509 -new -key ca.key -sha256 -days 3650 -out ca.crt

Mostra només la informació pública del certificat:
openssl x509 -in ca.crt -subject -issuer -dates -noout

7.2. Signar i verificar el certificat del servidor
Signa la CSR creada en la pràctica anterior:
cd ~/ud3-criptografia
openssl x509 -req -in servidor/servidor.csr -CA ca/ca.crt -CAkey ca/ca.key \
	-CAcreateserial -out servidor/servidor.crt -days 365 -sha256

Comprova la cadena de confiança:
openssl verify -CAfile ca/ca.crt servidor/servidor.crt
openssl x509 -in servidor/servidor.crt -subject -issuer -dates -noout


El resultat de la verificació ha de ser servidor/servidor.crt: OK. Conserva captures de la creació de la CA, la CSR, el certificat signat i la verificació.

7.3. Certificat amb noms alternatius i Apache

Per a un certificat de servidor, els noms vàlids han de figurar en l'extensió SAN. Crea el fitxer servidor/san.cnf, substituint el cognom si utilitzes dominis propis:

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = www.servidorresusta.test
DNS.2 = cursresusta.test
DNS.3 = www.cursresusta.test


Firma de nou la CSR incloent-hi l'extensió i comprova els SAN:

openssl x509 -req -in servidor/servidor.csr -CA ca/ca.crt -CAkey ca/ca.key \
	-CAcreateserial -out servidor/servidor-san.crt -days 365 -sha256 \
	-extfile servidor/san.cnf -extensions v3_req
openssl x509 -in servidor/servidor-san.crt -noout -ext subjectAltName


Per a configurar-lo en Apache, instal·la el servidor i el mòdul TLS. Utilitza només una de les alternatives segons la distribució:

# AlmaLinux, Rocky Linux o Fedora
sudo dnf install httpd mod_ssl -y
sudo install -m 600 -o root -g root servidor/servidor.key /etc/pki/tls/private/servidor-resusta.key
sudo install -m 644 servidor/servidor-san.crt /etc/pki/tls/certs/servidor-resusta.crt

# Debian o Ubuntu
sudo apt install apache2 -y
sudo a2enmod ssl
sudo install -m 600 -o root -g root servidor/servidor.key /etc/ssl/private/servidor-resusta.key
sudo install -m 644 servidor/servidor-san.crt /etc/ssl/certs/servidor-resusta.crt


Configura un lloc HTTPS amb SSLEngine on, SSLCertificateFile i SSLCertificateKeyFile apuntant als fitxers instal·lats. Afig els noms de prova a /etc/hosts per a resoldre'ls localment:

127.0.0.1 www.servidorresusta.test cursresusta.test www.cursresusta.test


Prova un nom inclòs i un altre que no estiga en SAN. Importar ca/ca.crt com a autoritat de confiança en el navegador és opcional i només s'ha de fer en el perfil de proves.

7.4. Alternativa gràfica amb XCA

Com a alternativa a les ordres anteriors, es pot utilitzar XCA per a crear una base de dades protegida, una CA arrel i una CSR de servidor. Selecciona les plantilles de CA i servidor HTTPS, utilitza SHA-256, genera una clau RSA de 4096 bits per a la CA i afig els noms DNS en SAN. Exporta el certificat públic de la CA i el certificat del servidor en PEM. La clau privada del servidor només s'exportarà per a instal·lar-la en el servidor d'entorn de proves amb permisos 600.

8. Pràctica 6 - Comprovació de TLS
8.1. Consultar un certificat públic
Consulta el certificat que presenta un lloc web públic. Substituïx el domini si és necessari:
openssl s_client -connect www.example.com:443 -servername www.example.com </dev/null 2>/dev/null \
	| openssl x509 -noout -subject -issuer -dates


Identifica el subjecte, emissor i període de validesa. Explica per què el nom sol·licitat mitjançant -servername és rellevant per a servidors que allotgen diversos llocs HTTPS.

Relaciona el certificat observat amb la cadena de confiança, TLS i la protecció de la clau privada del servidor.

8.2. Anàlisi passiva amb SSL Labs

Accedix a https://www.ssllabs.com/ssltest/ i analitza quatre llocs HTTPS públics. Limita l'activitat a l'anàlisi oferida pel web, sense realitzar proves intrusives. Per a cada lloc, anota la qualificació, versions TLS, suites criptogràfiques, cadena de certificats i avisos rellevants.

Compara, a més, el tipus de validació i l'adequació per al servei dels llocs de BBVA, Banco Santander, El País i El Mundo. Les etiquetes DV, OV o EV no substituïxen l'anàlisi de la configuració TLS ni garantixen la seguretat global del lloc.

9. Activitats
9.1. Conceptes i mecanismes
Explica la diferència entre xifrat, hash i signatura digital.
Compara criptografia simètrica i asimètrica: claus, rendiment, casos d'ús i principal limitació.
Completa la taula:
Algorisme o mecanisme	Tipus	Ús principal	CaracterísticaAES			
RSA			
SHA-256			
Argon2			
10. Autoavaluació
Quin mecanisme proporciona principalment confidencialitat: hash, xifrat o signatura digital?
Quina clau ha de mantindre's protegida en un sistema asimètric?
Quin d'estos és una funció hash: RSA, AES, SHA-256 o ECDSA?
Per a què s'utilitza principalment una signatura digital?
Quin element relaciona una identitat amb una clau pública?
Quin protocol protegix les comunicacions HTTPS?
Per què no s'ha d'utilitzar ECB per a dades sensibles?
Què aporta un salt a l'emmagatzematge de contrasenyes?
Quina funció complix una CSR?
Quina diferència existix entre una CA arrel i una CA intermèdia?
Quins mecanismes permeten comprovar la revocació de certificats?
Per què un certificat autofirmat no és adequat per a un servei públic?
Quin risc suposa reutilitzar un nonce amb el mateix algorisme i clau quan el mode ho prohibix?
Quina amenaça representa l'algorisme de Shor per a RSA i ECC?
11. Tasca avaluable única - Implementació d'una PKI

Entrega un informe en PDF o Markdown amb captures pròpies i explicacions redactades amb les teues paraules. No inclogues claus privades reals, contrasenyes ni el contingut de fitxers .key.

11.1. Situació

Una empresa disposa de serveis interns i necessita protegir les seues comunicacions. Com a administrador de sistemes, has de dissenyar i implementar una PKI mínima d'entorn de proves.

11.2. Contingut obligatori
Diagrama de la CA, el servidor, la clau privada, la CSR, el certificat signat i el client.
Evidències del càlcul i comprovació d'un hash abans i després de modificar un fitxer.
Creació i protecció de la clau del servidor, sense mostrar-ne el material privat.
Explicació de l'auditoria realitzada només sobre comptes de prova i de les mesures que dificulten atacs contra contrasenyes.
Creació de la CA, CSR i certificat de servidor signat per la CA.
Verificació de la cadena mitjançant openssl verify i identificació de subjecte, emissor, validesa i noms SAN.
Evidències de xifrat simètric i d'un missatge xifrat i signat amb GnuPG, sense claus privades.
12. Recursos
Manual d'OpenSSL: https://docs.openssl.org/
Documentació de GnuPG: https://www.gnupg.org/documentation/
NIST: estàndards de criptografia postquàntica: https://csrc.nist.gov/projects/post-quantum-cryptography
Let's Encrypt: documentació sobre certificats: https://letsencrypt.org/docs/
John the Ripper: https://www.openwall.com/john/
XCA: https://hohnstaedt.de/xca/
SSL Labs: https://www.ssllabs.com/ssltest/