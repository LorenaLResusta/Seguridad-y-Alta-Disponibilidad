---
title: "UD3. Criptografía y aplicaciones criptográficas"
weight: 30
---

# UD3 · Criptografía y aplicaciones criptográficas

La criptografía es la herramienta que sostiene casi todo lo demás en seguridad: protege los datos guardados en un disco, los que viajan por una red, las copias de seguridad, las contraseñas de las cuentas y la validez de un contrato firmado. En esta unidad aprendes **qué garantiza cada técnica** (confidencialidad, integridad, autenticidad y no repudio), **qué algoritmos son recomendables hoy y cuáles están obsoletos**, y cómo aplicarlas en un sistema real: cifrado simétrico y asimétrico, funciones *hash*, almacenamiento seguro de contraseñas, firma digital, certificados X.509, **infraestructura de clave pública (PKI)**, TLS y HTTPS, cifrado de volúmenes con **LUKS2** y firma electrónica de documentos.

Además, te asomas a las tendencias: la **criptografía post-cuántica** (ML-KEM, ML-DSA) que ya se está desplegando en TLS y SSH, y el cifrado homomórfico.

En el proyecto transversal [Mediterránea Dental](/guia/proyecto-clinica/) esta unidad entrega la **PKI interna y el cifrado**: una autoridad de certificación propia, HTTPS en la intranet, el volumen cifrado de los datos clínicos y la firma de los consentimientos de los pacientes.

{{< ra "RA1:g" "RA2:f" "RA3:c" >}}

| Página | Contenido |
|---|---|
| [Teoría](/ud03-criptografia/ud03-teoria/) | Conceptos, cifrado simétrico (AES, ChaCha20, AEAD), asimétrico (RSA, ECC, Diffie-Hellman), *hash*, HMAC, contraseñas, firma digital y marco legal (eIDAS 2, FNMT, DNIe), certificados y PKI, TLS 1.3, ACME, LUKS2, gestión de claves y criptografía post-cuántica |
| [Prácticas](/ud03-criptografia/ud03-practicas/) | Diez prácticas guiadas, autónomas y de reto (*hash*, cifrado, GnuPG, contraseñas, CA propia, HTTPS con Nginx, análisis TLS, revocación, LUKS2, firma de PDF) y la **Tarea del proyecto «PKI interna y HTTPS»** |

**Duración:** 18 horas (7 h teoría · 9 h prácticas · 2 h evaluación)

> [!NOTE]
> Esta unidad es la «caja de herramientas» del resto del módulo: el cifrado de disco y el acceso por clave SSH se refuerzan en la [UD4](/UD04/), las VPN y los certificados de cliente en la [UD6](/ud06-seguridad-perimetral/) y los certificados del *proxy* inverso y del balanceador en la [UD7](/ud07-alta-disponibilidad/).

## Cómo estudiar esta unidad

1. Lee la [teoría](/ud03-criptografia/ud03-teoria/) en orden: cada apartado se apoya en el anterior.
2. Reproduce los ejemplos en tu laboratorio a medida que aparecen.
3. Resuelve los ejercicios antes de abrir las soluciones.
4. Realiza las [prácticas](/ud03-criptografia/ud03-practicas/) y entrega la **Tarea del proyecto** dentro de [Mediterránea Dental](/guia/proyecto-clinica/).
