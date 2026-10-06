---
title: "UD3. Criptografía"
weight: 3
bookCollapseSection: true
---

# UD3. Criptografía

> Fundamentos y aplicaciones de la criptografía: cifrado simétrico y asimétrico, funciones hash, almacenamiento de contraseñas, firma digital, certificados, PKI y TLS, con OpenSSL y GnuPG.

| Datos de la unidad | Información |
| --- | --- |
| Módulo | 0378. Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR · 2026/27 |
| Duración | 14 horas |
| Material | [Teoría](teoria/) · [Prácticas](practicas/) |

## Resultados de aprendizaje y criterios de evaluación

| RA | Criterio de evaluación |
| --- | --- |
| RA1 | g) Se han aplicado técnicas criptográficas en el almacenamiento y transmisión de la información. |
| RA2 | f) Se han utilizado técnicas de cifrado, firmas y certificados digitales en un entorno de trabajo basado en el uso de redes públicas. |
| RA3 | c) Se han identificado los protocolos seguros de comunicación y sus ámbitos de utilización. |
| RA7 | e) Se ha descrito la legislación actual sobre los servicios de la sociedad de la información y comercio electrónico (firma electrónica y servicios de confianza). |

## Contenidos

- Conceptos: texto en claro, cifrado, clave, principio de Kerckhoffs.
- Criptografía simétrica: AES, ChaCha20, modos de operación y cifrado autenticado (GCM).
- Criptografía asimétrica: RSA, curvas elípticas (Ed25519, X25519), Diffie-Hellman.
- Funciones hash: SHA-2, SHA-3, BLAKE2. Integridad y HMAC.
- Almacenamiento de contraseñas: sal, yescrypt, Argon2.
- Firma digital y no repudio. GnuPG.
- Certificados X.509, autoridades de certificación, PKI, cadena de confianza y revocación.
- TLS 1.3 y HTTPS. Let's Encrypt y ACME.
- Criptografía post-cuántica (ML-KEM, ML-DSA).
- Firma electrónica y servicios de confianza (eIDAS, Ley 6/2020).

## Entorno de laboratorio

Una o dos máquinas virtuales Linux con OpenSSL 3, GnuPG 2.4 y un servidor web (Nginx o Apache).

> [!TIP]
> Antes de empezar las prácticas, crea una instantánea (*snapshot*) de cada máquina virtual. Si algo sale mal, podrás volver al estado inicial en segundos.

## Cómo estudiar esta unidad

1. Lee la [teoría](teoria/) en orden: cada apartado se apoya en el anterior.
2. Reproduce los ejemplos en tu laboratorio a medida que aparecen.
3. Resuelve los ejercicios de cada apartado antes de mirar las soluciones.
4. Realiza las [prácticas](practicas/) y entrega la tarea evaluable con las evidencias solicitadas.
