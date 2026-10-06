---
title: "Prácticas"
slug: "practicas"
weight: 2
---

# UD3. Prácticas: criptografía

> Hashes e integridad, cifrado simétrico y autenticado, claves asimétricas y firma con GnuPG, almacenamiento seguro de contraseñas, creación de una PKI propia, publicación de un servicio HTTPS y análisis de TLS.

| Datos de las prácticas | Información |
| --- | --- |
| Duración estimada | 8 horas |
| Entorno | 2 VM Linux (Debian 13 o AlmaLinux 10) en la red `SAD-NAT` |
| Criterios de evaluación | RA1 g · RA2 f · RA3 c · RA7 e |

## 1. Objetivos

- Verificar la integridad y la autenticidad de ficheros descargados.
- Cifrar y descifrar ficheros con algoritmos simétricos y comprobar el valor del cifrado autenticado.
- Gestionar pares de claves, cifrar y firmar con GnuPG, y verificar huellas.
- Comprobar cómo almacena Linux las contraseñas y por qué importan la sal y el coste del algoritmo.
- Crear una autoridad de certificación, emitir y revocar certificados.
- Publicar un servidor web HTTPS con TLS 1.2/1.3 y comprobar su configuración.

## 2. Preparación

### 2.1. Máquinas virtuales

| VM | Nombre | IP de ejemplo | Función |
| --- | --- | --- | --- |
| Cliente | `sad-cli` | `192.168.100.10` | Usuarios, GnuPG, CA, cliente HTTPS |
| Servidor web | `sad-web` | `192.168.100.30` | Nginx con HTTPS |

Puedes reutilizar las VM de la UD2 (clonando `sad-cli` como `sad-web`; cambia el nombre con `sudo hostnamectl set-hostname sad-web`). Añade en `/etc/hosts` de ambas:

```text
192.168.100.10  sad-cli
192.168.100.30  sad-web  sad-web.lab  www.sad-web.lab
```

### 2.2. Paquetes

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo apt install -y openssl gnupg age python3-cryptography whois libpwquality-tools curl nmap imagemagick
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo dnf install -y epel-release
sudo dnf install -y openssl gnupg2 age python3-cryptography libpwquality curl nmap ImageMagick
```
{{% /tab %}}
{{< /tabs >}}

```bash
openssl version        # anota la versión (OpenSSL 3.x)
gpg --version | head -1
mkdir -p ~/ud03 && cd ~/ud03
```

---

## 3. Práctica 1 - Funciones hash e integridad

### 3.1. Propiedades de un hash

```bash
printf 'hola'  | sha256sum
printf 'Hola'  | sha256sum
echo   'hola'  | sha256sum          # ¿por qué cambia respecto al primero?

# Longitud fija: el hash de 1 byte y el de 100 MB tienen la misma longitud
printf 'a' | sha256sum
head -c 100M /dev/urandom | sha256sum
```

**Preguntas**: ¿qué propiedad demuestra cada par de órdenes? ¿Cuántos caracteres hexadecimales tiene un SHA-256 y cuántos bits representa?

### 3.2. Comparar algoritmos

```bash
for alg in md5sum sha1sum sha256sum sha512sum b2sum; do
  printf '%-10s ' "$alg"; printf 'Seguridad' | $alg | cut -c1-64
done

# Tiempo de cálculo sobre un fichero de 500 MB
head -c 500M /dev/urandom > grande.bin
for alg in md5sum sha1sum sha256sum sha512sum b2sum; do
  echo "== $alg"; ( time $alg grande.bin >/dev/null ) 2>&1 | grep real
done
rm grande.bin
```

Completa una tabla con la longitud del resumen, el tiempo y si el algoritmo es recomendable.

### 3.3. Verificar la autenticidad de una descarga

Descarga los ficheros de comprobación de la imagen de Debian (no hace falta descargar la ISO):

```bash
URL=https://cdimage.debian.org/debian-cd/current/amd64/iso-cd
curl -sO $URL/SHA256SUMS
curl -sO $URL/SHA256SUMS.sign
head -3 SHA256SUMS
```

Verifica que el fichero de hashes está firmado por Debian:

```bash
gpg --keyserver keyring.debian.org --recv-keys DF9B9C49EAA9298432589D76DA87E80D6294BE9B
gpg --verify SHA256SUMS.sign SHA256SUMS
```

Resultado esperado:

```text
gpg: Firma correcta de "Debian CD signing key <debian-cd@lists.debian.org>" [desconocido]
gpg: ATENCIÓN: ¡Esta clave no está certificada por una firma de confianza!
Huellas dactilares de la clave primaria: DF9B 9C49 EAA9 2984 3258  9D76 DA87 E80D 6294 BE9B
```

> [!NOTE]
> El aviso «no está certificada» indica que **tú** no has confirmado personalmente esa clave. Comprueba que la huella coincide con la publicada en [debian.org/CD/verify](https://www.debian.org/CD/verify) por un canal distinto (HTTPS).

Simula una manipulación del fichero de hashes:

```bash
cp SHA256SUMS SHA256SUMS.original
sed -i '1s/^./0/' SHA256SUMS             # cambia el primer carácter
gpg --verify SHA256SUMS.sign SHA256SUMS  # Firma INCORRECTA
mv SHA256SUMS.original SHA256SUMS
```

**Pregunta**: explica por qué comprobar solo el hash de una ISO descargada de una web comprometida no es suficiente y cómo lo resuelve la firma.

### 3.4. HMAC: integridad con clave

```bash
echo '{"pedido": 1234, "importe": 59.90}' > pedido.json
CLAVE="ClaveCompartidaTienda2026"
openssl dgst -sha256 -hmac "$CLAVE" pedido.json

# Un atacante cambia el importe y recalcula el SHA-256 normal (puede hacerlo)…
sed -i 's/59.90/0.01/' pedido.json
sha256sum pedido.json
# …pero sin la clave no puede generar el HMAC correcto
openssl dgst -sha256 -hmac "$CLAVE" pedido.json      # distinto del original
```

---

## 4. Práctica 2 - Cifrado simétrico

### 4.1. Cifrado con contraseña: OpenSSL, GnuPG y age

```bash
echo "Plan de expansión 2027 - CONFIDENCIAL" > plan.txt

# OpenSSL (AES-256-CBC con derivación PBKDF2)
openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt -in plan.txt -out plan.txt.enc
xxd plan.txt.enc | head -3                 # comienza por "Salted__" seguido de la sal
openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 -in plan.txt.enc

# GnuPG
gpg --symmetric --cipher-algo AES256 plan.txt
gpg --list-packets plan.txt.gpg 2>/dev/null | head -5    # algoritmo y parámetros usados
gpg --decrypt plan.txt.gpg

# age
age -p -o plan.txt.age plan.txt
age -d plan.txt.age
```

- `xxd` muestra el contenido de un fichero en hexadecimal.
- `gpg --list-packets` describe la estructura del fichero OpenPGP sin descifrarlo.

**Pregunta**: introduce una contraseña incorrecta en cada herramienta. ¿Qué mensaje muestra cada una?

### 4.2. ¿Por qué no usar ECB?

Vamos a cifrar una imagen con AES en modo ECB y en modo CBC conservando la cabecera del fichero para poder visualizar el resultado.

```bash
# Imagen BMP sencilla con figuras de colores planos (ImageMagick 7 usa «magick», la 6 usa «convert»)
IM=$(command -v magick || command -v convert)
$IM -size 600x300 xc:white -fill black -draw "circle 150,150 150,40" \
    -fill red -draw "rectangle 330,60 560,240" -type truecolor logo.bmp

CLAVE=$(openssl rand -hex 16)
IV=$(openssl rand -hex 16)
head -c 54 logo.bmp > cabecera.bin                      # cabecera BMP (54 bytes)
tail -c +55 logo.bmp > pixeles.bin                      # datos de la imagen

openssl enc -aes-128-ecb -K "$CLAVE" -nosalt -in pixeles.bin -out ecb.bin
openssl enc -aes-128-cbc -K "$CLAVE" -iv "$IV" -nosalt -in pixeles.bin -out cbc.bin

cat cabecera.bin ecb.bin > logo_ecb.bmp
cat cabecera.bin cbc.bin > logo_cbc.bmp
```

Copia las tres imágenes a tu equipo (por ejemplo con `scp`) y ábrelas. En `logo_ecb.bmp` las formas siguen siendo reconocibles; en `logo_cbc.bmp` solo se ve ruido.

**Pregunta**: ¿qué información filtra ECB aunque el contenido esté cifrado?

### 4.3. Cifrado autenticado: detección de manipulaciones

Guarda el programa del apartado 4.4 de la teoría como `aes_gcm.py` y ejecútalo:

```bash
python3 aes_gcm.py
```

Compara con un cifrado **no autenticado** (CTR):

```bash
echo -n "PAGAR 0100 EUR" > orden.txt
K=$(openssl rand -hex 32); IV=$(openssl rand -hex 16)
openssl enc -aes-256-ctr -K $K -iv $IV -in orden.txt -out orden.ctr

# Sin conocer la clave, se modifica el byte 6 del texto cifrado
python3 - <<'EOF'
data = bytearray(open("orden.ctr", "rb").read())
data[6] ^= 0x30 ^ 0x39
open("orden.ctr", "wb").write(data)
EOF

openssl enc -d -aes-256-ctr -K $K -iv $IV -in orden.ctr
# PAGAR 9100 EUR      ← el contenido ha cambiado y nadie lo ha detectado
```

**Conclusión**: cifrar no garantiza la integridad. Explica con tus palabras por qué AES-GCM habría detectado el cambio.

---

## 5. Práctica 3 - Claves asimétricas, cifrado y firma con GnuPG

Trabajaremos con dos usuarios en `sad-cli`: **ana** y **bruno**.

```bash
sudo useradd -m -s /bin/bash ana   && sudo passwd ana
sudo useradd -m -s /bin/bash bruno && sudo passwd bruno
```

> [!TIP]
> Abre dos terminales y entra en cada una con `ssh ana@sad-cli` y `ssh bruno@sad-cli`. GnuPG necesita que la sesión sea del propio usuario para pedir la frase de paso.

### 5.1. Generar las claves

Como **ana**:

```bash
gpg --quick-generate-key "Ana García <ana@sad.lab>" default default 1y
gpg --list-secret-keys --keyid-format long
```

Resultado esperado:

```text
sec   ed25519/1A2B3C4D5E6F7A8B 2026-10-06 [SC] [caduca: 2027-10-06]
      9F8E7D6C5B4A39281716151413121110 1A2B3C4D5E6F7A8B
uid                 [  absoluta ] Ana García <ana@sad.lab>
ssb   cv25519/8B7A6F5E4D3C2B1A 2026-10-06 [E] [caduca: 2027-10-06]
```

- `sec ed25519 [SC]`: clave principal Ed25519 para firmar (**S**ign) y certificar (**C**ertify).
- `ssb cv25519 [E]`: subclave Curve25519 para cifrar (**E**ncrypt).

Genera también un **certificado de revocación** y guárdalo en lugar seguro:

```bash
gpg --output ~/revocacion_ana.asc --gen-revoke ana@sad.lab
```

Repite como **bruno**.

### 5.2. Intercambiar claves públicas y comprobar huellas

```bash
gpg --armor --export ana@sad.lab   > /tmp/ana.pub.asc     # como ana
gpg --armor --export bruno@sad.lab > /tmp/bruno.pub.asc   # como bruno
```

Cada uno importa la del otro:

```bash
gpg --import /tmp/bruno.pub.asc         # como ana
gpg --fingerprint bruno@sad.lab
```

> [!IMPORTANT]
> Antes de confiar en una clave, **comprueba la huella** con su dueño por un canal diferente (en persona, por teléfono). Si alguien sustituye el fichero `/tmp/bruno.pub.asc` por el suyo, Ana cifraría para la persona equivocada.

Si la huella coincide, firma la clave para certificar que la has comprobado:

```bash
gpg --sign-key bruno@sad.lab
```

### 5.3. Cifrar y firmar

Como **ana**:

```bash
echo "Bruno, la reunión con el proveedor se adelanta al jueves." > mensaje.txt
gpg --encrypt --sign --armor -r bruno@sad.lab -o /tmp/para_bruno.asc mensaje.txt
cat /tmp/para_bruno.asc
```

Como **bruno**:

```bash
gpg --decrypt /tmp/para_bruno.asc
```

Resultado esperado:

```text
gpg: cifrado con clave de 255 bits CV25519, ID 8B7A..., creada el 2026-10-06
      "Bruno Pérez <bruno@sad.lab>"
Bruno, la reunión con el proveedor se adelanta al jueves.
gpg: Firma correcta de "Ana García <ana@sad.lab>" [total]
```

¿Puede **ana** descifrar el fichero que ella misma ha cifrado para Bruno? Pruébalo y explica el resultado.

### 5.4. Firma separada y detección de manipulación

```bash
# ana firma un documento público (sin cifrarlo)
echo "Acta de la reunión del 6 de octubre" > acta.txt
gpg --armor --detach-sign acta.txt          # genera acta.txt.asc
cp acta.txt acta.txt.asc /tmp/

# bruno verifica
gpg --verify /tmp/acta.txt.asc /tmp/acta.txt

# alguien modifica el acta
echo "Se aprueba un nuevo punto no acordado" >> /tmp/acta.txt
gpg --verify /tmp/acta.txt.asc /tmp/acta.txt    # Firma INCORRECTA
```

### 5.5. Lo mismo con OpenSSL

Repite el cifrado y la firma con OpenSSL y claves RSA de 3072 bits (apartados 5.4 y 8.2 de la teoría). Comprueba que:

1. Un fichero cifrado con la clave pública solo se descifra con la privada.
2. Una firma generada con la clave privada se verifica con la pública.
3. Si cambias un byte del documento, la verificación falla.

### 5.6. Preguntas

1. Para **cifrar** un mensaje a Bruno y para **firmarlo** como Ana, ¿qué clave usa cada uno?
2. ¿Qué propiedades garantiza el mensaje cifrado y firmado?
3. ¿Para qué sirve el certificado de revocación? ¿Por qué se genera al crear la clave?

---

## 6. Práctica 4 - Almacenamiento seguro de contraseñas

**Objetivo**: comprobar cómo guarda Linux las contraseñas, por qué la sal y el coste del algoritmo protegen frente al robo del fichero de hashes, y cómo se valora la calidad de una contraseña antes de aceptarla.

### 6.1. Formato de `/etc/shadow`

```bash
sudo useradd -m prueba_ud03 && sudo passwd prueba_ud03
sudo grep '^prueba_ud03:' /etc/shadow
ls -l /etc/shadow            # ¿quién puede leerlo?
grep -E '^ENCRYPT_METHOD|^YESCRYPT_COST_FACTOR|^SHA_CRYPT' /etc/login.defs
```

Identifica en la línea de `/etc/shadow` el **algoritmo** (`$y$`, `$6$`…), los **parámetros de coste**, la **sal** y el **hash**. Indica qué algoritmo usa tu distribución.

### 6.2. El efecto de la sal

```bash
# Dos usuarios con la MISMA contraseña
sudo useradd -m prueba_ud03b
echo 'prueba_ud03:MismaClave2026'  | sudo chpasswd
echo 'prueba_ud03b:MismaClave2026' | sudo chpasswd
sudo grep -E '^prueba_ud03b?:' /etc/shadow | cut -d: -f1,2
```

Los hashes son distintos porque cada uno tiene su propia sal. **Pregunta**: ¿qué ventaja tendría un atacante si no hubiese sal?

### 6.3. El efecto del coste

Un hash de contraseñas debe ser **lento**. Mide cuánto tarda generar un hash con distintos algoritmos (`mkpasswd` está en el paquete `whois` de Debian; en AlmaLinux usa `openssl passwd`):

```bash
time (for i in $(seq 1 1000); do printf 'x' | sha256sum >/dev/null; done)   # hash rápido
time mkpasswd -m sha512crypt 'MismaClave2026' >/dev/null
time mkpasswd -m yescrypt 'MismaClave2026' >/dev/null
time mkpasswd -m yescrypt -R 9 'MismaClave2026' >/dev/null                   # mayor coste
```

Completa la tabla y extrae una conclusión: si un sistema tarda 100 veces más en calcular cada hash, ¿cuánto se ralentiza un intento masivo de adivinar contraseñas a partir de un fichero robado? ¿Y el inicio de sesión de un usuario legítimo?

| Algoritmo | Tiempo por hash | ¿Adecuado para contraseñas? |
| --- | --- | --- |
| SHA-256 simple | | |
| sha512crypt | | |
| yescrypt (coste por defecto) | | |
| yescrypt (coste 9) | | |

### 6.4. Calidad de las contraseñas

```bash
for p in "123456" "verano2026" "Barcelona1" "MismaClave2026" "tostada-azul-mochila-trueno"; do
  printf '%-30s ' "$p"; echo "$p" | pwscore 2>&1
done
```

Redacta qué contraseñas rechazarías y por qué, y relaciónalo con la política de contraseñas de la UD1.

### 6.5. Limpieza

```bash
sudo userdel -r prueba_ud03; sudo userdel -r prueba_ud03b
```

---

## 7. Práctica 5 - Autoridad de certificación propia

En el laboratorio no podemos usar Let's Encrypt porque no tenemos un dominio público. Crearemos una **CA raíz** propia con OpenSSL y la usaremos para emitir el certificado de `sad-web`. Este procedimiento es el mismo que usan muchas empresas para sus servicios internos.

### 7.1. Estructura de la CA

En `sad-cli`:

```bash
mkdir -p ~/ud03/ca/{certs,crl,newcerts,private,csr}
cd ~/ud03/ca
chmod 700 private
touch index.txt              # base de datos de certificados emitidos
echo 1000 > serial           # siguiente número de serie
echo 1000 > crlnumber        # siguiente número de CRL
```

Fichero `openssl.cnf`:

```ini
# Configuración mínima de la CA del laboratorio
[ ca ]
default_ca = CA_SAD

[ CA_SAD ]
dir               = .
certs             = $dir/certs
crl_dir           = $dir/crl
new_certs_dir     = $dir/newcerts
database          = $dir/index.txt
serial            = $dir/serial
crlnumber         = $dir/crlnumber
private_key       = $dir/private/ca.key
certificate       = $dir/certs/ca.crt
crl               = $dir/crl/ca.crl
default_md        = sha256
default_days      = 200
default_crl_days  = 30
policy            = politica_sad
copy_extensions   = copy          # copia la extensión SAN de la solicitud
unique_subject    = no

[ politica_sad ]
countryName             = match
organizationName        = match
commonName              = supplied

[ req ]
default_md          = sha256
distinguished_name  = dn
prompt              = no

[ dn ]
C  = ES
O  = SAD Laboratorio
CN = SAD Laboratorio Root CA

[ v3_ca ]
basicConstraints       = critical, CA:true
keyUsage               = critical, keyCertSign, cRLSign
subjectKeyIdentifier   = hash

[ servidor ]
basicConstraints       = critical, CA:false
keyUsage               = critical, digitalSignature
extendedKeyUsage       = serverAuth
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid
crlDistributionPoints  = URI:http://sad-web.lab/ca.crl
```

| Sección | Para qué sirve |
| --- | --- |
| `[ CA_SAD ]` | Rutas, algoritmo de firma y validez por defecto (200 días, como los certificados públicos actuales) |
| `[ politica_sad ]` | Qué campos de la solicitud deben coincidir con los de la CA |
| `[ v3_ca ]` | Extensiones del certificado raíz: puede firmar certificados y CRL |
| `[ servidor ]` | Extensiones de los certificados de servidor: no es CA, solo autenticación de servidor TLS |

### 7.2. Crear la CA raíz

```bash
# Clave privada de la CA (curva P-384), protegida con frase de paso
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-384 -aes-256-cbc -out private/ca.key
chmod 400 private/ca.key

# Certificado raíz autofirmado, válido 10 años
openssl req -config openssl.cnf -new -x509 -key private/ca.key -days 3650 -extensions v3_ca -out certs/ca.crt
openssl x509 -in certs/ca.crt -noout -subject -issuer -dates -ext basicConstraints
```

Observa que en un certificado raíz el **sujeto** y el **emisor** coinciden.

> [!WARNING]
> La clave privada de la CA es el activo más crítico de una PKI: con ella se pueden emitir certificados válidos para cualquier nombre. En producción se guarda en un HSM o en un equipo desconectado.

### 7.3. Solicitud del servidor (CSR)

La clave del servidor se genera **en el servidor**: la clave privada no debe viajar. En `sad-web`:

```bash
sudo mkdir -p /etc/ssl/sad && cd /etc/ssl/sad
sudo openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out sad-web.key
sudo chmod 600 sad-web.key
sudo openssl req -new -key sad-web.key \
     -subj "/C=ES/O=SAD Laboratorio/CN=sad-web.lab" \
     -addext "subjectAltName=DNS:sad-web.lab,DNS:www.sad-web.lab,IP:192.168.100.30" \
     -out sad-web.csr
openssl req -in sad-web.csr -noout -text | grep -A1 "Alternative"
scp sad-web.csr USUARIO@sad-cli:~/ud03/ca/csr/
```

### 7.4. Emitir el certificado

En `sad-cli`, la CA revisa y firma la solicitud:

```bash
cd ~/ud03/ca
openssl req -in csr/sad-web.csr -noout -subject -verify      # comprobar la firma de la solicitud
openssl ca -config openssl.cnf -extensions servidor -in csr/sad-web.csr -out certs/sad-web.crt
```

`openssl ca` muestra los datos y pide confirmación dos veces (`Sign the certificate? [y/n]` y `commit? [y/n]`).

```bash
cat index.txt                                         # V = válido, número de serie y sujeto
openssl verify -CAfile certs/ca.crt certs/sad-web.crt # certs/sad-web.crt: OK
openssl x509 -in certs/sad-web.crt -noout -ext subjectAltName,extendedKeyUsage -dates
scp certs/sad-web.crt certs/ca.crt USUARIO@sad-web:/tmp/
```

---

## 8. Práctica 6 - Servidor HTTPS con Nginx

### 8.1. Instalar Nginx

En `sad-web`:

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo apt install -y nginx
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo dnf install -y nginx
sudo systemctl enable --now nginx
sudo firewall-cmd --permanent --add-service=http --add-service=https && sudo firewall-cmd --reload
```
{{% /tab %}}
{{< /tabs >}}

```bash
sudo mv /tmp/sad-web.crt /tmp/ca.crt /etc/ssl/sad/
# Cadena completa: certificado del servidor + CA (el servidor debe enviar la cadena)
sudo sh -c 'cat /etc/ssl/sad/sad-web.crt /etc/ssl/sad/ca.crt > /etc/ssl/sad/fullchain.crt'
echo "<h1>sad-web: HTTPS funcionando</h1>" | sudo tee /var/www/html/index.html
```

En AlmaLinux la raíz de documentos por defecto es `/usr/share/nginx/html`.

### 8.2. Configuración del sitio

Fichero `/etc/nginx/conf.d/sad-web.conf`:

```nginx
# Redirigir todo el tráfico HTTP a HTTPS
server {
    listen 80;
    server_name sad-web.lab www.sad-web.lab;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name sad-web.lab www.sad-web.lab;

    ssl_certificate     /etc/ssl/sad/fullchain.crt;
    ssl_certificate_key /etc/ssl/sad/sad-web.key;

    # Solo versiones modernas de TLS
    ssl_protocols TLSv1.2 TLSv1.3;
    # Conjuntos de cifrado para TLS 1.2 (TLS 1.3 usa siempre AEAD)
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;

    # HSTS: el navegador usará solo HTTPS durante 1 año
    add_header Strict-Transport-Security "max-age=31536000" always;

    root /var/www/html;
    index index.html;
}
```

| Directiva | Función |
| --- | --- |
| `return 301` | Redirección permanente de HTTP a HTTPS |
| `ssl_certificate` / `ssl_certificate_key` | Cadena de certificados y clave privada del servidor |
| `ssl_protocols` | Versiones de TLS permitidas |
| `ssl_ciphers` | Algoritmos permitidos en TLS 1.2 (ECDHE + AEAD) |
| `add_header Strict-Transport-Security` | Activa HSTS |

En Debian, desactiva el sitio por defecto para evitar conflictos: `sudo rm /etc/nginx/sites-enabled/default`.

### 8.3. Comprobar y aplicar

```bash
sudo cp -a /etc/nginx /root/nginx.bak.$(date +%F)   # copia de la configuración
sudo nginx -t                                       # comprobar la sintaxis ANTES de recargar
sudo systemctl reload nginx                         # aplica sin cortar conexiones
sudo ss -tlnp | grep nginx                          # escucha en 80 y 443
```

> [!TIP]
> `reload` aplica la nueva configuración sin interrumpir las conexiones en curso; `restart` detiene y vuelve a arrancar el servicio. Si `nginx -t` da error, `reload` no se debe ejecutar.

### 8.4. Probar desde el cliente

En `sad-cli`:

```bash
curl -I http://sad-web.lab                      # 301 → https://sad-web.lab/
curl https://sad-web.lab                        # ERROR: certificado de una CA desconocida
curl --cacert ~/ud03/ca/certs/ca.crt https://sad-web.lab    # funciona
```

Añade la CA al almacén de confianza del sistema:

{{< tabs >}}
{{% tab "Debian / Ubuntu" %}}
```bash
sudo cp ~/ud03/ca/certs/ca.crt /usr/local/share/ca-certificates/sad-lab-ca.crt
sudo update-ca-certificates
```
{{% /tab %}}
{{% tab "AlmaLinux / Rocky" %}}
```bash
sudo cp ~/ud03/ca/certs/ca.crt /etc/pki/ca-trust/source/anchors/sad-lab-ca.crt
sudo update-ca-trust
```
{{% /tab %}}
{{< /tabs >}}

```bash
curl -v https://sad-web.lab 2>&1 | grep -E "SSL connection|subject|issuer|verify"
curl https://192.168.100.30          # funciona porque la IP está en el SAN
curl https://sad-web                 # falla: "sad-web" no está en el SAN
```

Para probarlo con un navegador del equipo anfitrión, añade `sad-web.lab` al fichero `hosts` del anfitrión (en Windows `C:\Windows\System32\drivers\etc\hosts`) e importa `ca.crt` en el almacén de certificados raíz de confianza **solo durante la práctica**. Elimínalo al terminar.

---

## 9. Práctica 7 - Análisis de la configuración TLS

### 9.1. Con OpenSSL

```bash
# Versión y algoritmo negociados
openssl s_client -connect sad-web.lab:443 -servername sad-web.lab </dev/null 2>/dev/null \
  | grep -E "Protocol|Cipher|Verify return"

# ¿Se aceptan versiones antiguas? (deben fallar)
openssl s_client -connect sad-web.lab:443 -tls1_1 </dev/null 2>&1 | grep -iE "alert|error|Protocol"
openssl s_client -connect sad-web.lab:443 -tls1_2 </dev/null 2>&1 | grep -E "Protocol|Cipher"
openssl s_client -connect sad-web.lab:443 -tls1_3 </dev/null 2>&1 | grep -E "Protocol|Cipher"

# Cabecera HSTS
curl -sI https://sad-web.lab | grep -i strict
```

### 9.2. Con Nmap

**Nmap** es un escáner de red; su *script* `ssl-enum-ciphers` enumera las versiones y algoritmos que acepta un servidor y les asigna una nota.

> [!CAUTION]
> Ejecuta Nmap **solo** contra tus máquinas del laboratorio.

```bash
nmap -p 443 --script ssl-enum-ciphers sad-web.lab
```

Resultado esperado (resumido):

```text
| ssl-enum-ciphers:
|   TLSv1.2:
|     ciphers:
|       TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 (secp256r1) - A
|       TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 (secp256r1) - A
|       TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256 (secp256r1) - A
|   TLSv1.3:
|     ciphers:
|       TLS_AKE_WITH_AES_128_GCM_SHA256 (ecdh_x25519) - A
|       ...
|_  least strength: A
```

### 9.3. Configuración insegura y corrección

1. Haz una copia de `sad-web.conf`, añade `TLSv1 TLSv1.1` a `ssl_protocols`, comprueba con `nginx -t` y recarga.
2. Repite el análisis con Nmap: ¿qué cambia en la nota y en los avisos?
3. Restaura la configuración segura, recarga y vuelve a comprobar.

### 9.4. Comparar con un servidor real

```bash
curl -vI https://www.boe.es 2>&1 | grep -E "SSL connection|expire date|issuer"
echo | openssl s_client -connect www.boe.es:443 -servername www.boe.es 2>/dev/null | openssl x509 -noout -dates -issuer
```

Puedes analizar de forma pasiva un dominio público con [SSL Labs](https://www.ssllabs.com/ssltest/) (marca la opción para no publicar el resultado).

---

## 10. Práctica 8 - Revocación de un certificado

**Escenario**: la clave privada de `sad-web` se ha copiado por error en un repositorio público. Hay que revocar el certificado y emitir uno nuevo.

```bash
cd ~/ud03/ca
openssl ca -config openssl.cnf -revoke certs/sad-web.crt -crl_reason keyCompromise
openssl ca -config openssl.cnf -gencrl -out crl/ca.crl
openssl crl -in crl/ca.crl -noout -text | grep -A3 "Revoked Certificates"
cat index.txt                  # el certificado aparece con estado R (revocado)

# Verificar teniendo en cuenta la CRL
openssl verify -crl_check -CAfile certs/ca.crt -CRLfile crl/ca.crl certs/sad-web.crt
# error 23 at 0 depth lookup: certificate revoked
```

Publica la CRL en el servidor web (la URL figura en la extensión `crlDistributionPoints` del certificado) y repite las prácticas 7.3 y 7.4 con una **clave nueva** para emitir un certificado sustituto.

**Preguntas**:

1. ¿Por qué no basta con emitir un certificado nuevo con la misma clave?
2. ¿Qué diferencias hay entre CRL y OCSP?
3. ¿Qué ventaja tienen los certificados de corta duración frente a la revocación?

---

## 11. Problemas habituales

| Problema | Causa | Solución |
| --- | --- | --- |
| `gpg: signing failed: Inappropriate ioctl for device` | GnuPG no puede pedir la frase de paso en esa terminal | `export GPG_TTY=$(tty)` |
| `bad decrypt` en `openssl enc` | Contraseña o parámetros (`-pbkdf2`, `-iter`) distintos al cifrar y al descifrar | Usar exactamente las mismas opciones |
| `nginx: [emerg] cannot load certificate key` | Ruta o permisos de la clave | Comprobar la ruta y que el fichero es legible por root |
| `key values mismatch` | La clave no corresponde al certificado | Comparar `openssl x509 -noout -pubkey -in cert` con `openssl pkey -pubout -in key` |
| `SSL certificate problem: unable to get local issuer certificate` | El cliente no confía en la CA o falta la cadena | Instalar la CA en el cliente; usar `fullchain.crt` en el servidor |
| `no alternative certificate subject name matches` | El nombre usado no está en el SAN | Acceder con un nombre incluido o reemitir el certificado |
| `openssl ca: ... TXT_DB error number 2` | Ya existe un certificado válido con ese sujeto | `unique_subject = no` en la configuración o revocar el anterior |

## 12. Actividades

1. Compara en una tabla OpenSSL `enc`, GnuPG y age: algoritmos, cifrado autenticado, facilidad de uso.
2. Investiga qué es un HSM y un TPM y en qué casos usarías cada uno.
3. Firma un PDF con AutoFirma usando un certificado de pruebas y verifica la firma en VALIDe. Explica qué tipo de firma electrónica (simple, avanzada o cualificada) has generado.
4. Investiga cómo obtiene una empresa un certificado TLS público con Certbot y el desafío DNS-01.
5. Comprueba si tu cliente OpenSSH usa un intercambio de claves post-cuántico (`ssh -Q kex`, `ssh -v`) y explica qué significa.

## 13. Autoevaluación

{{% details "1. ¿Por qué es peligroso el modo ECB?" %}}
Porque bloques de texto en claro iguales producen bloques cifrados iguales, lo que revela patrones del contenido.
{{% /details %}}

{{% details "2. ¿Con qué clave se cifra un mensaje para Bruno? ¿Y con cuál lo firma Ana?" %}}
Se cifra con la clave pública de Bruno. Ana firma con su propia clave privada.
{{% /details %}}

{{% details "3. ¿Qué aporta la sal en el almacenamiento de contraseñas?" %}}
Que contraseñas iguales tengan hashes distintos e impide usar tablas precalculadas.
{{% /details %}}

{{% details "4. ¿Qué extensión del certificado comprueba el navegador para el nombre del servidor?" %}}
La extensión SAN (*Subject Alternative Name*).
{{% /details %}}

{{% details "5. ¿Qué diferencia hay entre `nginx -s reload` / `systemctl reload` y `restart`?" %}}
`reload` aplica la nueva configuración sin cortar las conexiones activas; `restart` detiene y vuelve a iniciar el servicio.
{{% /details %}}

{{% details "6. ¿Por qué la clave privada del servidor se genera en el propio servidor?" %}}
Para que nunca tenga que viajar por la red ni salir del equipo que la usa. A la CA solo se envía la CSR, que contiene la clave pública.
{{% /details %}}

## 14. Tarea evaluable - PKI y servicio HTTPS para una empresa

**Supuesto**: la empresa *Construcciones Mediterráneo* necesita publicar internamente su intranet (`intranet.cmed.lab`) y su aplicación de fichajes (`fichajes.cmed.lab`) con HTTPS, y que la dirección pueda enviar documentos firmados y cifrados al departamento jurídico.

Entrega un informe con:

1. **Diseño de la PKI**: jerarquía (raíz e intermedia, opcional), algoritmos, validez, custodia de la clave raíz y procedimiento de revocación.
2. **Implantación**: CA, certificados con SAN para ambos servicios, Nginx con TLS 1.2/1.3, redirección y HSTS. Evidencias de `nginx -t`, `curl -v` y Nmap.
3. **Revocación**: revocación de un certificado comprometido, CRL publicada y comprobación con `openssl verify -crl_check`.
4. **Correo seguro**: procedimiento con GnuPG para que la dirección firme y cifre documentos para jurídico, incluida la verificación de huellas.
5. **Contraseñas**: algoritmo de hash usado por los servidores y recomendaciones de política.
6. **Marco legal**: diferencias entre firma simple, avanzada y cualificada y cuál necesitaría la empresa para firmar contratos con clientes.

| Criterio | Peso |
| --- | :-: |
| Diseño de la PKI justificado | 20 % |
| Servicio HTTPS correcto y verificado | 30 % |
| Revocación y CRL | 15 % |
| Cifrado y firma con GnuPG | 15 % |
| Contraseñas y marco legal | 10 % |
| Documentación | 10 % |

## 15. Recursos

- [OpenSSL: `openssl-ca`](https://docs.openssl.org/master/man1/openssl-ca/) · [`openssl-req`](https://docs.openssl.org/master/man1/openssl-req/) · [`openssl-s_client`](https://docs.openssl.org/master/man1/openssl-s_client/)
- [GnuPG: manual de usuario](https://www.gnupg.org/gph/es/manual.html)
- [age](https://github.com/FiloSottile/age)
- [Nginx: configuring HTTPS servers](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Nmap: ssl-enum-ciphers](https://nmap.org/nsedoc/scripts/ssl-enum-ciphers.html)
- [AutoFirma (Portal de Administración Electrónica)](https://firmaelectronica.gob.es/Home/Descargas.html) · [VALIDe](https://valide.redsara.es/)
