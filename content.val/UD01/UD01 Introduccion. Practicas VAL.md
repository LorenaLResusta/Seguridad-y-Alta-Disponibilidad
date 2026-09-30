---
title: "1. Introducció a la seguretat. Pràctiques"
weight: 2
---
# UD1 - Pràctiques: introducció a la seguretat

> Preparació d'un entorn de proves Linux i elaboració d'un pla bàsic de gestió de riscos.

| Dades de les pràctiques | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Durada estimada | 6 hores |
| Entorn | VirtualBox i una distribució Linux compatible |

## 1. Objectius

En finalitzar les pràctiques, l'alumnat serà capaç de:

- Preparar una màquina virtual aïllada per a pràctiques de seguretat.
- Identificar actius, amenaces, vulnerabilitats i riscos.
- Aplicar mesures bàsiques de protecció en un sistema Linux.
- Proposar controls tècnics, organitzatius i físics proporcionats.
- Documentar evidències i un pla de millora realista.

## 2. Abast i normes de l'entorn de proves

- Treballa únicament sobre la teua pròpia màquina virtual i els sistemes autoritzats pel professorat.
- No realitzes anàlisis, escanejos ni proves sobre equips, xarxes o serveis aliens.
- No utilitzes dades personals reals en captures, informes ni proves.
- Realitza una snapshot abans de canviar configuracions rellevants per a poder tornar a un estat conegut.

## 3. Preparació comuna

### 3.1. Material necessari

- Un equip amb virtualització habilitada.
- [VirtualBox](https://www.virtualbox.org/).
- Una ISO d'instal·lació mínima d'una distribució Linux compatible.
- Espai lliure en disc per a la màquina virtual.

AlmaLinux és la distribució recomanada per a mantindre la continuïtat amb la resta del mòdul, però no és obligatòria. També es poden utilitzar Debian, Ubuntu Server, Rocky Linux o Fedora. En aquest document, les ordes es mostren per a AlmaLinux i distribucions de la família RHEL; en Debian o Ubuntu s'ha d'utilitzar `apt` en lloc de `dnf`.

### 3.2. Crear la màquina virtual

1. Instal·la VirtualBox des del seu lloc oficial i obri'l.
2. Selecciona **Nova** i assigna el nom `linux-ud01`.
3. Selecciona la ISO descarregada. Si VirtualBox proposa una instal·lació desatesa, desmarca-la per a completar manualment les opcions d'instal·lació.
4. Assigna com a referència 2 GB de memòria RAM, 2 processadors i un disc virtual dinàmic de 25 GB. Ajusta aquests valors si l'equip amfitrió disposa de pocs recursos.
5. En la configuració de xarxa, selecciona **NAT**. Aquesta opció permet actualitzar el sistema sense exposar directament la màquina virtual a la xarxa local.
6. Inicia la màquina i segueix l'assistent d'instal·lació de la distribució triada.

### 3.3. Instal·lar i configurar el sistema

1. Tria l'idioma d'instal·lació.
2. En **Destí de la instal·lació**, selecciona el disc virtual creat i accepta la configuració automàtica de particions.
3. Activa la connexió de xarxa i estableix el nom d'equip `linux-ud01`.
4. Crea un compte d'usuari amb la inicial del teu nom seguida del teu primer cognom. Exemple: `fperez`.
5. Marca l'opció perquè l'usuari puga administrar el sistema i crea una contrasenya robusta per al compte administratiu.
6. Inicia la instal·lació. Quan acabe, reinicia la màquina i retira la ISO virtual si es sol·licita.
7. Inicia sessió amb l'usuari creat i obri una terminal.

### 3.4. Comprovacions inicials

Executa aquestes ordes i guarda una captura o còpia de la eixida de cadascuna:

```bash
hostnamectl
cat /etc/os-release
ip a
whoami