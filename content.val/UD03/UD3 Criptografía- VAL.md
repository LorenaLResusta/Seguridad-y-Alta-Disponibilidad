---
title: "3. Criptografia."
weight: 1
---
# UD3 - Criptografia

> Fonaments, xifratge, integritat, signatura digital i certificats per a protegir la informació i les comunicacions.

| Dades de la unitat | Informació |
| --- | --- |
| Mòdul | Seguretat i Alta Disponibilitat |
| Curs | 2n ASIR |
| Modalitat | Semipresencial |
| Duració | 14 hores |

## Índex

1. Fonaments i propietats de seguretat
2. Criptografia simètrica
3. Criptografia asimètrica
4. Funcions hash, signatures i protecció de contrasenyes
5. Certificats, PKI i TLS
6. Resum
7. Recursos
8. Relació amb els resultats d'aprenentatge

---

## 1. Fonaments i propietats de seguretat

### 1.1. Introducció

La criptografia constituïx una de les principals ferramentes per a protegir la informació i les comunicacions dels sistemes informàtics.

En esta unitat s'estudiaran els fonaments de la criptografia i els principals mecanismes utilitzats actualment per a protegir la informació: xifratge simètric, xifratge asimètric, funcions hash, signatures digitals i certificats digitals.

Es prestarà una atenció especial a la selecció del mecanisme adequat segons l'objectiu de seguretat i a l'ús responsable de claus, certificats i algoritmes normalitzats.

L'objectiu és que l'alumnat no sols conega els algoritmes criptogràfics, sinó que siga capaç d'identificar quin mecanisme ha d'utilitzar en cada situació i per què.

### 1.2. Objectius

En finalitzar la unitat, l'alumnat serà capaç de:

- Comprendre els fonaments de la criptografia.
- Identificar les propietats de seguretat que proporciona.
- Diferenciar xifratge, hash i signatura digital.
- Comprendre el funcionament de la criptografia simètrica.
- Conéixer els principals algoritmes simètrics.
- Comprendre el funcionament de la criptografia asimètrica.
- Diferenciar clau pública i clau privada.
- Conéixer algoritmes com RSA i ECC.
- Comprendre el funcionament de les funcions hash.
- Conéixer els mecanismes utilitzats per a protegir contrasenyes.
- Comprendre el concepte de signatura digital.
- Comprendre el funcionament dels certificats digitals.
- Conéixer el concepte de PKI.
- Comprendre el paper de les autoritats certificadores.
- Comprendre el funcionament bàsic d'HTTPS/TLS.
- Aplicar bones pràctiques en la gestió de claus.

### 1.3. Què és la criptografia?

La criptografia engloba tècniques matemàtiques utilitzades per a protegir informació.

Permet implementar mecanismes relacionats amb:

- Confidencialitat.
- Integritat.
- Autenticitat.
- No repudi.

En un sistema criptogràfic podem trobar:

- Informació original: dades que volem protegir.
- Algoritme criptogràfic: procediment utilitzat.
- Clau: informació que controla el procés criptogràfic.
- Text xifrat: resultat del xifratge.
- Desxifratge: procés per a recuperar la informació original.

Exemple:

```text
              CLAU
                │
                ▼
Text clar → XIFRATGE → Text xifrat
                            │
                            ▼
                       DESXIFRATGE
                            │
                            ▼
                        Text clar
```

### 1.4. Propietats de seguretat

#### 1.4.1. Confidencialitat

La informació només ha de poder ser consultada per usuaris autoritzats.

**Exemple:** una empresa emmagatzema les nòmines dels seus treballadors en un servidor. Si els arxius estan xifrats, obtindre físicament una còpia d'ells no hauria de permetre llegir-ne el contingut sense disposar de la clau adequada.

#### 1.4.2. Integritat

Permet detectar modificacions realitzades sobre la informació.

Per exemple, podem calcular un hash d'un fitxer:

```text
Fitxer
   │
   ▼
 SHA-256
   │
   ▼
 Hash
```

Si el fitxer canvia, el hash resultant també hauria de canviar.

#### 1.4.3. Autenticitat

Permet comprovar la identitat de l'origen d'una informació.

Per exemple, una signatura digital permet comprovar que un document ha sigut signat mitjançant una determinada clau privada.

#### 1.4.4. No repudi

Permet disposar de mecanismes que relacionen una determinada acció amb el seu autor.

Les signatures digitals poden contribuir al no repudi, encara que la seua validesa també depén del context legal i dels procediments utilitzats.

### 1.5. Principi de Kerckhoffs

La seguretat d'un sistema criptogràfic no ha de dependre de mantindre secret l'algoritme, sinó de protegir correctament la clau. Este principi permet que algoritmes com AES, RSA o les funcions SHA siguen públics, revisats per especialistes i utilitzats per moltes organitzacions.

Ocultar el funcionament d'un algoritme no és una mesura suficient: si es descobrix, el sistema no hauria de quedar exposat.

En la pràctica, una organització ha de seleccionar algoritmes normalitzats, aplicar implementacions mantingudes i centrar els seus controls en la generació, emmagatzematge, rotació i revocació de les claus.

### 1.6. Aplicacions de la criptografia

La criptografia s'aplica a dades en trànsit i en repòs.

- HTTPS protegix la comunicació entre un navegador i un servidor.
- El xifratge de disc reduïx l'impacte del robatori d'un portàtil.
- PGP i S/MIME poden protegir el correu electrònic.
- Les signatures digitals permeten comprovar la integritat i autoria de documents o programes.

La tecnologia adequada dependrà de l'objectiu:

| Necessitat | Mecanisme |
| --- | --- |
| Ocultar informació | Xifratge |
| Comprovar que no s'ha alterat | Hash |
| Demostrar l'origen | Signatura digital |
| Verificar la identitat d'un servidor | Certificat digital |

---

## 2. Criptografia simètrica

### 2.1. Xifratge

El xifratge transforma informació llegible en informació que no hauria de poder interpretar-se sense disposar de la clau corresponent.

```text
INFORMACIÓ ORIGINAL
        │
        │ Xifratge
        ▼
INFORMACIÓ XIFRADA
        │
        │ Desxifratge
        ▼
INFORMACIÓ ORIGINAL
```

### 2.2. Criptografia simètrica

La criptografia simètrica utilitza una mateixa clau secreta per a xifrar i desxifrar.

```text
                 CLAU
                   │
                   ▼
Missatge ───────► XIFRATGE
                   │
                   ▼
             Missatge xifrat
                   │
                   ▼
              DESXIFRATGE
                   │
                   ▼
                Missatge
```

El principal problema és com aconseguir que emissor i receptor compartisquen la clau de manera segura.

### 2.3. Avantatges i inconvenients

*Avantatges*

- És ràpida.
- Consumix pocs recursos.
- És adequada per a grans quantitats d'informació.
- S'utilitza habitualment per a xifrar dades i comunicacions.

*Inconvenients*

- L'intercanvi inicial de la clau pot ser un problema.
- Si un atacant aconseguix la clau secreta, podrà desxifrar la informació protegida amb ella.

### 2.4. Algoritmes simètrics

Alguns algoritmes coneguts són:

- AES
- ChaCha20
- 3DES
- DES

Actualment:

- AES és un estàndard àmpliament utilitzat.
- ChaCha20 també s'utilitza en sistemes moderns.
- DES es considera obsolet.
- 3DES està obsolet per a nous dissenys.

### 2.5. AES

AES (*Advanced Encryption Standard*) és un dels algoritmes de xifratge simètric més utilitzats.

Admet claus de:

- 128 bits
- 192 bits
- 256 bits

```text
                  AES
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
    AES-128     AES-192     AES-256
```

### 2.6. Modes d'operació i xifratge autenticat

AES és un xifrador de blocs i necessita un mode d'operació per a protegir missatges de longitud variable.

- **ECB** no ha d'utilitzar-se per a informació sensible.
- **AES-GCM** aporta confidencialitat i integritat.
- **ChaCha20-Poly1305** és una alternativa moderna molt utilitzada.

El vector d'inicialització o *nonce* no sol ser secret, però ha de gestionar-se correctament i no reutilitzar-se quan el mode utilitzat ho prohibisca.

---

## 3. Criptografia asimètrica

### 3.1. Criptografia asimètrica

La criptografia asimètrica utilitza un parell de claus:

- Clau pública.
- Clau privada.

```text
        PARELL DE CLAUS

   ┌─────────────────────┐
   │                     │
   ▼                     ▼
Clau pública       Clau privada
   │                     │
Pot distribuir-se   Ha de protegir-se
```

### 3.2. Clau pública

La clau pública pot distribuir-se a altres persones o sistemes.

Pot utilitzar-se per a:

- Xifrar informació.
- Verificar signatures.
- Participar en mecanismes d'establiment de claus.

### 3.3. Clau privada

La clau privada ha de mantindre's protegida.

Pot utilitzar-se per a:

- Desxifrar informació.
- Generar signatures digitals.
- Autenticar-se mitjançant certificats.

### 3.4. RSA

RSA és un dels algoritmes asimètrics més coneguts.

Pot utilitzar-se per a:

- Xifratge.
- Signatures digitals.
- Determinats mecanismes d'intercanvi de claus.

### 3.5. Criptografia de corba el·líptica

La criptografia basada en corbes el·líptiques (ECC) permet aconseguir nivells de seguretat comparables a RSA amb claus més menudes.

Alguns sistemes relacionats són:

- ECDSA
- ECDH
- EdDSA

### 3.6. Simètrica davant asimètrica

| Característica | Simètrica | Asimètrica |
| --- | --- | --- |
| Claus | Una clau secreta | Pública + privada |
| Velocitat | Alta | Menor |
| Grans quantitats de dades | Molt adequada | Menys adequada |
| Gestió de claus | Més complicada | Facilita l'intercanvi |
| Signatures digitals | No és l'objectiu principal | Sí |
| Exemples | AES, ChaCha20 | RSA, ECC |

En sistemes reals és habitual combinar ambdós tipus.

### 3.7. Diffie-Hellman i gestió de claus

Diffie-Hellman permet establir un secret compartit sense enviar-lo directament.

Les seues variants modernes, com ECDH, s'utilitzen per a crear claus de sessió.

Les claus privades han d'emmagatzemar-se amb permisos restrictius, xifratge, còpies de seguretat protegides i procediments de revocació.

---

## 4. Funcions hash, signatures i protecció de contrasenyes

### 4.1. Funcions hash

Una funció hash genera un resum de les dades d'entrada.

```text
Fitxer
   │
   ▼
Funció HASH
   │
   ▼
Resum
```

Alguns algoritmes coneguts:

- SHA-256
- SHA-384
- SHA-512

### 4.2. Característiques dels hash

Una funció hash criptogràfica ha de dificultar:

- Obtindre les dades originals a partir del hash.
- Trobar dos entrades amb el mateix hash.
- Manipular les dades sense que el canvi siga detectable.

Una propietat important és l'efecte allau.

### 4.3. Hash i contrasenyes

Per a emmagatzemar contrasenyes han d'utilitzar-se funcions específiques com:

- Argon2
- bcrypt
- scrypt
- PBKDF2

### 4.4. Salt

El *salt* és un valor addicional, normalment aleatori, que es combina amb la contrasenya abans d'aplicar la funció de derivació.

```text
Contrasenya + Salt
        │
        ▼
Funció de derivació
        │
        ▼
Resultat emmagatzemat
```

El *salt* no és una clau secreta i normalment s'emmagatzema junt amb el resultat derivat.

### 4.5. Signatura digital

Una signatura digital permet comprovar principalment:

- Integritat.
- Autenticitat.

```text
Document
    │
    ▼
   HASH
    │
    ▼
Signatura amb clau privada
    │
    ▼
Signatura digital
```

### 4.6. Xifratge davant signatura digital

| Xifratge | Signatura |
| --- | --- |
| Protegix confidencialitat | Protegix integritat i autenticitat |
| Oculta informació | Permet verificar l'origen |
| Impedix la lectura | Detecta modificacions |

Una informació pot estar:

- Xifrada.
- Signada.
- Xifrada i signada.
- Ni xifrada ni signada.

---

## 5. Certificats, PKI i TLS

### 5.1. Certificats digitals

Un certificat digital permet associar una identitat amb una clau pública.

Pot contindre:

- Identitat del titular.
- Clau pública.
- Emissor.
- Número de sèrie.
- Període de validesa.
- Algoritmes utilitzats.
- Signatura de l'autoritat certificadora.

### 5.2. Autoritat de certificació

Una CA (*Certificate Authority*) és una entitat que emet i firma certificats digitals.

La seua funció principal és establir una relació de confiança entre:

```text
Identitat ←── Certificat ──→ Clau pública
```

### 5.3. PKI

Una PKI (*Public Key Infrastructure*) és una infraestructura destinada a gestionar claus públiques i certificats digitals.

Pot incloure:

- Autoritats certificadores.
- Autoritats de registre.
- Autoritats de validació.
- Certificats.
- Claus.
- Polítiques de certificació.
- Mecanismes de revocació.

### 5.4. Cadena de confiança

```text
CA arrel
   │
   ▼
CA intermèdia
   │
   ▼
Certificat servidor
   │
   ▼
www.empresa.es
```

### 5.5. Revocació de certificats

Un certificat pot deixar de ser vàlid abans de caducar.

Per exemple:

- Compromís de la clau privada.
- Error en l'emissió.
- Canvi d'identitat associada.

Mecanismes habituals:

- CRL
- OCSP

### 5.6. TLS i HTTPS

HTTPS utilitza TLS per a protegir les comunicacions.

```text
Client
   │
   │ Connexió TLS
   ▼
Servidor
   │
   ├── Certificat
   ├── Autenticació
   └── Negociació criptogràfica
             │
             ▼
      Comunicació segura
```

Durant la connexió, el client valida el certificat, la seua validesa temporal i la cadena de confiança.

### 5.7. Tipus i formats de certificats

Tipus habituals:

- Certificats de servidor.
- Certificats personals.
- Certificats de firma de codi.
- Certificats de CA.

Nivells de validació:

- DV (*Domain Validation*)
- OV (*Organization Validation*)
- EV (*Extended Validation*)

Formats habituals:

- X.509
- PEM
- DER
- PKCS#12 (PFX)
- PKCS#7

### 5.8. Criptografia quàntica i postquàntica

La distribució quàntica de claus aprofita propietats físiques per a detectar interceptacions durant l'intercanvi de claus.

Els ordinadors quàntics a gran escala podrien afectar:

- RSA
- Diffie-Hellman
- ECC

La criptografia postquàntica busca algoritmes resistents tant a atacs clàssics com quàntics.

Alguns estàndards recents inclouen:

- ML-KEM
- ML-DSA
- SLH-DSA

Les organitzacions han de preparar-se per a poder substituir algoritmes i certificats quan siga necessari.

---

## 6. Resum

La criptografia protegix informació i comunicacions mitjançant mecanismes amb finalitats diferents:

- El xifratge aporta confidencialitat.
- Els hash permeten comprovar integritat.
- Les signatures aporten integritat i autenticitat.
- Els certificats vinculen una identitat amb una clau pública.

Els sistemes actuals combinen criptografia simètrica i asimètrica, i la seua seguretat depén tant dels algoritmes utilitzats com d'una correcta gestió de claus, certificats i procediments de revocació.

## 7. Recursos

- NIST: Cryptographic Standards and Guidelines
- NIST: criptografia postquàntica
- Documentació d'OpenSSL
- Documentació de GnuPG
- Let's Encrypt

## 8. Relació amb els resultats d'aprenentatge

Esta unitat contribuïx a l'adopció de pràctiques segures, la protecció de la informació, l'autenticació de sistemes i usuaris, i l'aplicació de mecanismes criptogràfics en comunicacions i servicis.