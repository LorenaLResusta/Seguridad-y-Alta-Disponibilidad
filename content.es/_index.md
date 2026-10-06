---
title: "Índice del módulo"
weight: 1
bookToc: true
---

# Seguridad y Alta Disponibilidad — Índice del módulo

**Módulo profesional:** 0378 Seguridad y Alta Disponibilidad (SAD)
**Ciclo:** CFGS Técnico Superior en Administración de Sistemas Informáticos en Red (ASIR) — 2.º curso
**Curso académico:** 2026/27
**Duración en la Comunitat Valenciana:** 133 horas (4 h/semana)
**Ámbito:** Comunitat Valenciana

---

## 1. Marco normativo

La organización de estos apuntes se ajusta a los **Resultados de Aprendizaje (RA)**, **Criterios de Evaluación (CE)** y **Contenidos Básicos** del módulo 0378, establecidos en la normativa vigente para el curso 2026/27:

| Ámbito | Norma | Qué regula |
|---|---|---|
| Estatal | Ley Orgánica 3/2022, de 31 de marzo, de ordenación e integración de la Formación Profesional | Nuevo Sistema de FP |
| Estatal | Real Decreto 659/2023, de 18 de julio | Ordenación del Sistema de FP |
| Estatal | Real Decreto 1629/2009, de 30 de octubre | Título de ASIR y enseñanzas mínimas (RA, CE y contenidos del módulo 0378) |
| Estatal | Real Decreto 500/2024, de 21 de mayo | Adapta el título de ASIR (y otros de grado superior) al nuevo Sistema de FP |
| Autonómica | Decreto 114/2025, de 29 de julio, del Consell (modificado por el Decreto 95/2026, de 19 de junio) | Currículos de los ciclos de grado medio y superior en la Comunitat Valenciana. Implantado en 2.º curso desde 2025/26 |

> **Nota.** La Orden 36/2012, de 22 de junio, que establecía anteriormente el currículo de ASIR en la Comunitat Valenciana, no debe utilizarse como referencia para el curso 2026/27: el currículo aplicable es el del Decreto 114/2025. Los RA y CE del módulo 0378 proceden del RD 1629/2009, que sigue vigente con las modificaciones del RD 500/2024.

---

## 2. Resultados de aprendizaje del módulo

| RA | Enunciado |
|---|---|
| **RA1** | Adopta pautas y prácticas de tratamiento seguro de la información, reconociendo las vulnerabilidades de un sistema informático y la necesidad de asegurarlo. |
| **RA2** | Implanta mecanismos de seguridad activa, seleccionando y ejecutando contramedidas ante amenazas o ataques al sistema. |
| **RA3** | Implanta técnicas seguras de acceso remoto a un sistema informático, interpretando y aplicando el plan de seguridad. |
| **RA4** | Implanta cortafuegos para asegurar un sistema informático, analizando sus prestaciones y controlando el tráfico hacia la red interna. |
| **RA5** | Implanta servidores *proxy*, aplicando criterios de configuración que garanticen el funcionamiento seguro del servicio. |
| **RA6** | Implanta soluciones de alta disponibilidad empleando técnicas de virtualización y configurando los entornos de prueba. |
| **RA7** | Reconoce la legislación y normativa sobre seguridad y protección de datos valorando su importancia. |

Los criterios de evaluación se citan en este índice con la notación **RAx.letra** (por ejemplo, **RA4.d** = «Se han configurado filtros en un cortafuegos a partir de un listado de reglas de filtrado»).

---

## 3. Visión general de las unidades

| UD | Título | RA principales | Horas orientativas |
|---|---|---|---|
| **UD1** | Introducción a la seguridad informática, gestión de riesgos y marco legal | RA1, RA7 | 14 h |
| **UD2** | Seguridad pasiva: seguridad física, almacenamiento y copias de seguridad | RA1, RA6 | 18 h |
| **UD3** | Criptografía y aplicaciones criptográficas | RA1, RA2, RA3 | 18 h |
| **UD4** | Fortificación de sistemas (*hardening*) y seguridad activa en el host | RA1, RA2 | 22 h |
| **UD5** | Seguridad en redes: monitorización, detección y respuesta | RA2, RA3 | 18 h |
| **UD6** | Seguridad perimetral: cortafuegos, *proxy*, VPN y acceso remoto | RA3, RA4, RA5 | 25 h |
| **UD7** | Alta disponibilidad, virtualización y continuidad de negocio | RA6 | 18 h |
| | **Total** | | **133 h** |

### Hilo conductor

Las unidades siguen una progresión que va **del concepto al servicio y del servicio a la infraestructura**:

1. **Qué proteger y por qué** (UD1): activos, riesgos, normativa.
2. **Proteger frente a la pérdida** (UD2): seguridad física, redundancia de almacenamiento, copias.
3. **La herramienta transversal** (UD3): criptografía, que se reutiliza en todas las unidades posteriores.
4. **Proteger el equipo** (UD4): *hardening*, control de acceso, actualizaciones, *malware*, registros.
5. **Proteger y vigilar la red** (UD5): análisis de tráfico, inventario de servicios, IDS/IPS, Wi-Fi.
6. **Proteger el perímetro** (UD6): DMZ, cortafuegos, *proxy*, VPN y pasarelas de acceso.
7. **Garantizar que el servicio no se detiene** (UD7): redundancia, *failover*, balanceo, *clusters* y recuperación.

En todas las prácticas de seguridad se aplica el ciclo:

**amenaza → vulnerabilidad → ataque → detección → mitigación → comprobación**

y en todas las prácticas de alta disponibilidad se incluye una **prueba explícita de fallo** y la **comprobación de la recuperación** del servicio.

### Correspondencia con la organización anterior de la web

| Unidad anterior | Unidad en esta organización | Cambio |
|---|---|---|
| UD1 Introducción | UD1 | Se incorpora la gestión de riesgos y el marco legal (RA7) |
| UD2 Seguridad pasiva | UD2 | Se amplía con RAID, copias 3-2-1 y RPO/RTO |
| UD3 Criptografía | UD3 | Sin cambio de posición |
| UD4 Fortificación de hosts | UD4 | Se incorpora control de acceso, *malware*, registros y análisis forense |
| UD6 Seguridad en redes | **UD5** | Adelanta su posición |
| UD7 Seguridad perimetral | **UD6** | Adelanta su posición e incluye *proxy* y VPN |
| UD5 Alta disponibilidad | **UD7** | Pasa al final, porque reutiliza cortafuegos, *proxy* inverso y monitorización |

---

## UD1. Introducción a la seguridad informática, gestión de riesgos y marco legal

**RA:** RA1, RA7 · **CE:** RA1.a, RA1.b, RA1.c, RA1.d, RA1.h · RA7.a, RA7.b, RA7.c, RA7.d, RA7.e, RA7.f, RA7.g · **Horas:** 14

### Teoría

1. Introducción: por qué la seguridad es una función del administrador de sistemas
2. Objetivos de la unidad
3. Conceptos fundamentales
   1. Información, activo, sistema de información
   2. Dimensiones de la seguridad: confidencialidad, integridad, disponibilidad (tríada CIA); autenticidad y trazabilidad
   3. Fiabilidad y no repudio
   4. Seguridad física y lógica; seguridad activa y pasiva
   5. Elementos vulnerables: *hardware*, *software*, datos y personas
4. Amenazas, vulnerabilidades y ataques
   1. Terminología: amenaza, vulnerabilidad, *exploit*, riesgo, impacto, salvaguarda
   2. Clasificación de amenazas: físicas y lógicas; internas y externas; intencionadas y accidentales
   3. Clasificación de vulnerabilidades por tipología y origen
   4. Bases de datos de vulnerabilidades: CVE, CVSS, CWE
   5. Ingeniería social y fraude: *phishing*, *vishing*, *smishing*, suplantación del CEO
5. Análisis y gestión de riesgos
   1. Proceso de análisis: activos → amenazas → vulnerabilidades → impacto → riesgo
   2. Metodologías: MAGERIT v3 (herramienta PILAR) e ISO/IEC 27005
   3. Tratamiento del riesgo: mitigar, transferir, aceptar, evitar
   4. Riesgo residual
6. Políticas y planes de seguridad
   1. Política de seguridad, normas, procedimientos e instrucciones técnicas
   2. Plan integral de seguridad y protección perimetral en sistemas conectados a redes públicas
   3. Concienciación y formación de usuarios
7. Legislación y normativa
   1. Protección de datos: Reglamento (UE) 2016/679 (RGPD) y LO 3/2018 (LOPDGDD)
   2. Figuras legales: responsable, encargado del tratamiento, delegado de protección de datos (DPD), interesado
   3. Derechos de las personas: acceso, rectificación, supresión, oposición, limitación y portabilidad
   4. Control de acceso a la información personal y medidas técnicas y organizativas
   5. Servicios de la sociedad de la información y comercio electrónico: Ley 34/2002 (LSSI)
   6. Esquema Nacional de Seguridad: RD 311/2022 (ENS)
   7. Normas de gestión de la seguridad: familia ISO/IEC 27000 (ISO/IEC 27001:2022, ISO/IEC 27002:2022)
   8. Ciberseguridad en la UE: Directiva (UE) 2022/2555 (NIS2) y su transposición
   9. Organismos de referencia: INCIBE, INCIBE-CERT, CCN-CERT, AEPD, ENISA
8. Resumen
9. Referencias

### Prácticas

- **P1.1** Preparación del laboratorio virtual del módulo (ver Anexo A) y documentación de la topología.
- **P1.2** Inventario de activos de una pyme ficticia y valoración en las dimensiones CIA.
- **P1.3** Análisis de riesgos simplificado con matriz probabilidad × impacto y propuesta de salvaguardas.
- **P1.4** Búsqueda e interpretación de vulnerabilidades reales en NVD y en los avisos de INCIBE-CERT (puntuación CVSS, vector de ataque, mitigación).
- **P1.5** Análisis de un correo de *phishing* (cabeceras, enlaces, remitente) sin interactuar con él.
- **P1.6** Elaboración de un registro de actividades de tratamiento (RAT) conforme al RGPD.

### Supuesto profesional

Una clínica dental con 12 equipos y una aplicación de gestión de pacientes solicita un diagnóstico de seguridad. Identificar activos, amenazas y obligaciones legales (datos de salud: categoría especial del RGPD) y redactar una política de seguridad básica.

---

## UD2. Seguridad pasiva: seguridad física, almacenamiento y copias de seguridad

**RA:** RA1, RA6 · **CE:** RA1.a, RA1.b · RA6.b, RA6.f · **Horas:** 18

### Teoría

1. Introducción: seguridad activa frente a seguridad pasiva
2. Objetivos de la unidad
3. Seguridad física y ambiental
   1. Ubicación y protección física de equipos y servidores
   2. El centro de proceso de datos (CPD): control de acceso, climatización, detección y extinción de incendios
   3. Niveles de disponibilidad de un CPD (TIA-942 / Uptime Institute Tier)
4. Sistemas de alimentación ininterrumpida (SAI/UPS)
   1. Tipos: *offline*, interactivo, *online* de doble conversión
   2. Dimensionado: potencia (VA/W) y autonomía
   3. Monitorización y apagado ordenado con NUT (*Network UPS Tools*)
5. Almacenamiento de la información
   1. Medios de almacenamiento: HDD, SSD, cinta LTO, almacenamiento en red (NAS, SAN) y en la nube
   2. Políticas de almacenamiento: ciclo de vida, clasificación y retención
   3. Almacenamiento redundante: RAID 0, 1, 5, 6 y 10; RAID por *software* con `mdadm`
   4. Sistemas de ficheros con integridad: ZFS y Btrfs (instantáneas y suma de verificación)
   5. Soluciones *hardware* para la continuidad: fuentes redundantes, discos *hot-swap*, controladoras RAID
6. Copias de seguridad e imágenes de respaldo
   1. Tipos de copia: completa, incremental, diferencial
   2. Estrategia 3-2-1 (y 3-2-1-1-0) y copias inmutables frente a *ransomware*
   3. RPO y RTO: definición y relación con la política de copias
   4. Herramientas: `rsync`, BorgBackup, restic, Proxmox Backup Server
   5. Imágenes de sistema: Clonezilla
   6. Verificación y restauración: una copia no verificada no es una copia
7. Introducción a la continuidad de negocio: plan de contingencia y plan de recuperación
8. Resumen
9. Referencias

### Prácticas

- **P2.1** Configuración de un SAI virtual/simulado con NUT y apagado ordenado del servidor.
- **P2.2** Creación de un RAID 1 y un RAID 5 con `mdadm` en Debian. **Prueba de fallo:** marcar un disco como defectuoso, comprobar el estado degradado, sustituirlo y verificar la reconstrucción.
- **P2.3** Copias incrementales con BorgBackup o restic: cifrado del repositorio, retención, automatización con temporizadores de `systemd` y restauración de ficheros.
- **P2.4** Copia remota con `rsync` sobre SSH.
- **P2.5** Creación y restauración de una imagen de sistema con Clonezilla.
- **P2.6** Cálculo de RPO/RTO reales de la política diseñada y comparación con los objetivos.

### Supuesto profesional

Diseñar la política de copias de una asesoría que ha sufrido un ataque de *ransomware*: qué copiar, con qué frecuencia, dónde, cuánto tiempo conservarlo y cómo comprobar que se puede restaurar.

### Recursos de la unidad

- Vídeo: *El invento millonario que Volvo regaló* (`ud02/El_invento_millonario_que_Volvo_regaló.mp4`). Uso propuesto: introducción al concepto de seguridad pasiva mediante una analogía (el cinturón de seguridad no evita el accidente, pero reduce sus consecuencias).

---

## UD3. Criptografía y aplicaciones criptográficas

**RA:** RA1, RA2, RA3 · **CE:** RA1.g · RA2.f · RA3.c · **Horas:** 18

### Teoría

1. Introducción: la criptografía como herramienta transversal de la seguridad
2. Objetivos de la unidad
3. Conceptos fundamentales: criptografía, criptoanálisis, clave, algoritmo, principio de Kerckhoffs
4. Cifrado simétrico
   1. Cifrado en bloque y en flujo
   2. AES y ChaCha20; modos de operación (GCM frente a ECB)
   3. Cifrado autenticado (AEAD)
   4. Problema de la distribución de claves
5. Cifrado asimétrico
   1. Pares de claves pública/privada
   2. RSA y criptografía de curva elíptica (ECDSA, Ed25519, X25519)
   3. Intercambio de claves Diffie-Hellman
   4. Sistemas híbridos
6. Funciones *hash* y códigos de autenticación
   1. Propiedades de una función *hash*
   2. Algoritmos actuales (SHA-256, SHA-3, BLAKE2) y obsoletos (MD5, SHA-1)
   3. HMAC
   4. Almacenamiento seguro de contraseñas: Argon2, bcrypt, yescrypt
7. Firma digital y certificados
   1. Firma digital: integridad, autenticidad y no repudio
   2. Certificados X.509
   3. Infraestructura de clave pública (PKI): CA raíz e intermedia, cadena de confianza, revocación (CRL y OCSP)
   4. Certificados en España: DNIe, FNMT, Reglamento eIDAS 2 (UE) 2024/1183
   5. Certificación automática: protocolo ACME y Let's Encrypt
8. Aplicaciones criptográficas
   1. Cifrado de la información almacenada: LUKS2, BitLocker, VeraCrypt
   2. Cifrado y firma de ficheros y correo: GnuPG y S/MIME
   3. Protocolos seguros de comunicación: TLS 1.3, SSH, HTTPS, SFTP, IMAPS/SMTPS; protocolos obsoletos (SSL, TLS 1.0/1.1)
9. Tendencias
   1. Criptografía postcuántica: ML-KEM y ML-DSA (NIST FIPS 203/204) y su adopción en OpenSSH y TLS
   2. Cifrado homomórfico y *bootstrapping*
10. Resumen
11. Referencias

### Prácticas

- **P3.1** Cifrado y descifrado simétrico de ficheros con OpenSSL (`openssl enc` con AES-256 y derivación PBKDF2) y con `age`.
- **P3.2** Generación y comprobación de resúmenes *hash* (`sha256sum`) para verificar la integridad de una ISO descargada.
- **P3.3** GnuPG: creación de claves, intercambio, cifrado, firma y verificación de documentos.
- **P3.4** Creación de una CA propia con OpenSSL: CA raíz, CA intermedia, emisión y revocación de certificados de servidor.
- **P3.5** Publicación de un servidor web con TLS 1.3 (Nginx o Apache) usando la CA del laboratorio; análisis del *handshake* con Wireshark y `openssl s_client`; evaluación de la configuración con `testssl.sh`.
- **P3.6** Cifrado de un volumen con LUKS2 y montaje automático con fichero de claves.
- **P3.7** Firma electrónica de un PDF con un certificado y verificación de la firma.

### Supuesto profesional

Una empresa necesita intercambiar contratos firmados con sus clientes y publicar una intranet con HTTPS. Proponer la solución criptográfica (PKI interna o pública, tipo de certificados, algoritmos) y justificar la elección.

### Recursos de la unidad

- Vídeo: *Cómo el Bootstrapping limpia datos cifrados sin abrirlos* (`UD03/Cómo_el_Bootstrapping_Limpia_Datos_Cifrados_sin_Abrirlos.mp4`). Uso propuesto: apartado 9.2, tendencias en criptografía.

---

## UD4. Fortificación de sistemas (*hardening*) y seguridad activa en el host

**RA:** RA1, RA2 · **CE:** RA1.e, RA1.f, RA1.i · RA2.a, RA2.b, RA2.c, RA2.d, RA2.e, RA2.h · **Horas:** 22

### Teoría

1. Introducción: superficie de ataque y principio de mínimo privilegio
2. Objetivos de la unidad
3. Identificación, autenticación y autorización (modelo AAA)
   1. Factores de autenticación: conocimiento, posesión, inherencia
   2. Políticas de contraseñas: longitud, complejidad, caducidad y bloqueo (recomendaciones NIST SP 800-63B)
   3. Autenticación multifactor (MFA): TOTP, FIDO2/WebAuthn, *passkeys*
   4. Sistemas biométricos: ventajas, limitaciones y tasas FAR/FRR
   5. PAM en Linux y directivas de cuenta en Windows
4. Control de acceso y gestión de permisos
   1. Modelos DAC, MAC y RBAC
   2. Permisos UNIX, ACL POSIX (`setfacl`/`getfacl`) y ACL de NTFS
   3. Elevación controlada de privilegios: `sudo` y UAC
   4. Control de acceso obligatorio: AppArmor y SELinux
5. Fortificación del sistema
   1. Guías de bastionado: CIS Benchmarks y guías CCN-STIC
   2. Seguridad del arranque: UEFI *Secure Boot* y contraseña del gestor de arranque
   3. Minimización de servicios y paquetes; inventario de servicios en ejecución
   4. Fortificación del acceso SSH
   5. Directivas de seguridad en Windows Server (GPO)
   6. Auditoría automatizada del bastionado: Lynis y OpenSCAP
6. Gestión de actualizaciones y vulnerabilidades
   1. Verificación del origen y autenticidad del *software* (firmas de repositorios, sumas de verificación)
   2. Actualizaciones automáticas: `unattended-upgrades` y Windows Update/WSUS
   3. Ciclo de gestión de vulnerabilidades
7. Amenazas lógicas y *software* malicioso
   1. Clasificación: virus, gusanos, troyanos, *ransomware*, *rootkits*, *spyware*, *botnets*
   2. Anatomía de un ataque: modelo *Cyber Kill Chain* y matriz MITRE ATT&CK
   3. Herramientas preventivas y paliativas: antivirus/EDR, ClamAV, Microsoft Defender
   4. Detección de *rootkits* e integridad de ficheros: `rkhunter`, AIDE
8. Registros (*logs*) y auditoría
   1. `journald`, `rsyslog` y el Visor de eventos de Windows
   2. Auditoría de accesos con `auditd`
   3. Protección automática frente a fuerza bruta: Fail2ban
9. Respuesta a incidentes y análisis forense
   1. Fases de gestión de un incidente
   2. Fases del análisis forense: adquisición, preservación, análisis, documentación
   3. Cadena de custodia y orden de volatilidad
   4. Herramientas: `dd`/`dcfldd`, Autopsy, Volatility
10. Resumen
11. Referencias

### Prácticas

- **P4.1** Política de contraseñas y bloqueo de cuentas con PAM (`pam_pwquality`, `pam_faillock`) en Debian y con GPO en Windows Server.
- **P4.2** Autenticación SSH por claves Ed25519 y segundo factor TOTP.
- **P4.3** Permisos y ACL en un servidor de ficheros departamental.
- **P4.4** Configuración de `sudo` con privilegios mínimos y registro de comandos.
- **P4.5** Auditoría de bastionado con Lynis: análisis del informe, aplicación de medidas y nueva medición.
- **P4.6** Ataque de fuerza bruta contra SSH en el laboratorio → detección en los registros → mitigación con Fail2ban → comprobación.
- **P4.7** Análisis de muestras de prueba (fichero EICAR) y escaneo con ClamAV en un entorno aislado.
- **P4.8** Monitorización de integridad con AIDE y detección de una modificación no autorizada.
- **P4.9** Adquisición forense de un disco virtual con verificación *hash* y análisis básico con Autopsy.

### Supuesto profesional

Recibimos un servidor Debian recién instalado que se va a publicar en Internet. Elaborar y ejecutar su plan de bastionado, documentando la puntuación de Lynis antes y después de aplicar las medidas.

---

## UD5. Seguridad en redes: monitorización, detección y respuesta

**RA:** RA2, RA3 · **CE:** RA2.c, RA2.d, RA2.g, RA2.h, RA2.i · RA3.c · **Horas:** 18

### Teoría

1. Introducción: la red como superficie de ataque
2. Objetivos de la unidad
3. Seguridad en la red corporativa
   1. Segmentación con VLAN y principio de defensa en profundidad
   2. Seguridad en la capa 2: seguridad de puertos, DHCP *snooping*, inspección ARP dinámica
   3. Control de acceso a la red: IEEE 802.1X y RADIUS
4. Ataques de red y contramedidas
   1. Reconocimiento y escaneo de puertos
   2. Suplantación: ARP *spoofing*, DNS *spoofing*, servidor DHCP falso
   3. Ataques intermediarios (*man-in-the-middle*)
   4. Denegación de servicio (DoS y DDoS)
5. Monitorización del tráfico
   1. Captura de tráfico: modo promiscuo, puerto espejo (SPAN), TAP
   2. Herramientas: Wireshark y `tcpdump`
   3. Inventario y control de servicios de red: Nmap y `ss`
   4. Riesgos potenciales de los servicios de red y protocolos inseguros (Telnet, FTP, HTTP, SNMPv1/v2c)
6. Seguridad en redes inalámbricas
   1. Evolución: WEP (obsoleto), WPA2, WPA3
   2. Modos Personal (PSK/SAE) y Enterprise (802.1X/EAP)
   3. Amenazas: puntos de acceso falsos, ataques de desautenticación, WPS
7. Sistemas de detección y prevención de intrusiones
   1. Tipos: NIDS/HIDS, IDS/IPS, por firmas y por anomalías
   2. Ubicación en la red
   3. Suricata: reglas, alertas y modo IPS
8. Gestión centralizada de eventos
   1. Centralización de registros
   2. SIEM y XDR: Wazuh
9. Pruebas de intrusión
   1. Concepto, fases y marco legal y ético
   2. Diferencia entre análisis de vulnerabilidades y prueba de intrusión
   3. Escáneres de vulnerabilidades: OpenVAS/Greenbone
10. Resumen
11. Referencias

### Prácticas

- **P5.1** Captura y análisis con Wireshark de protocolos en claro (HTTP, FTP, Telnet) frente a cifrados (HTTPS, SSH): extracción de credenciales en el laboratorio y conclusiones.
- **P5.2** Inventario de la red y de los servicios expuestos con Nmap; comparación con la documentación de la red.
- **P5.3** Ataque ARP *spoofing* en el laboratorio → detección en Wireshark y en Suricata → mitigación (entradas ARP estáticas o inspección ARP dinámica) → comprobación.
- **P5.4** Instalación de Suricata como IDS, reglas personalizadas y paso a modo IPS.
- **P5.5** Despliegue de Wazuh: agentes Linux y Windows, correlación de eventos y alertas.
- **P5.6** Análisis de vulnerabilidades de la red del laboratorio con Greenbone y elaboración de un informe con prioridades de corrección.
- **P5.7** Red Wi-Fi WPA3-Enterprise con autenticación 802.1X contra FreeRADIUS (opcional, según el equipamiento del aula).

### Supuesto profesional

Una empresa detecta lentitud y conexiones salientes sospechosas en horario nocturno. Diseñar el procedimiento de investigación (captura, análisis, correlación de registros) y proponer las medidas de detección permanentes.

---

## UD6. Seguridad perimetral: cortafuegos, *proxy*, VPN y acceso remoto

**RA:** RA1, RA3, RA4, RA5 · **CE:** RA1.h · RA3.a, RA3.b, RA3.d, RA3.e, RA3.f, RA3.g · RA4.a–RA4.h · RA5.a–RA5.i · **Horas:** 25

### Teoría

1. Introducción: escenarios con conexión a redes públicas que requieren fortificar la red interna
2. Objetivos de la unidad
3. Seguridad perimetral
   1. Elementos básicos: *router* frontera, cortafuegos, *proxy*, IDS/IPS, pasarela VPN
   2. Zonas de riesgo y perímetros de red; zonas desmilitarizadas (DMZ)
   3. Arquitecturas: subred protegida débil (un cortafuegos) y fuerte (dos cortafuegos)
   4. Del modelo perimetral al modelo de confianza cero (*Zero Trust*)
4. Cortafuegos
   1. Características, tipos y funciones
   2. Niveles de filtrado: paquetes, estado de la conexión (*stateful*), aplicación (capa 7)
   3. Cortafuegos *software* y *hardware*; cortafuegos de nueva generación (NGFW)
   4. Planificación y ubicación; política por defecto (denegar todo)
   5. Filtrado en Linux con `nftables`: tablas, cadenas, reglas, conjuntos y NAT
   6. Interfaces de gestión: `firewalld` y UFW
   7. Cortafuegos perimetral dedicado: pfSense CE u OPNsense
   8. Cortafuegos de Windows Defender
   9. Registros de sucesos del cortafuegos y diagnóstico de problemas de conectividad
   10. Pruebas de funcionamiento y sondeo
5. Servidores *proxy*
   1. Tipos: directo, transparente e inverso; características y funciones
   2. *Proxy*-caché con Squid: almacenamiento en caché, ACL y filtros
   3. Métodos de autenticación en el *proxy*: básica, LDAP, Kerberos
   4. Configuración de los clientes: manual, PAC y WPAD
   5. *Proxy* en modo transparente
   6. *Proxy* inverso con Nginx o HAProxy y terminación TLS
   7. Monitorización de la actividad del *proxy*
6. Redes privadas virtuales (VPN)
   1. Beneficios e inconvenientes frente a las líneas dedicadas
   2. VPN de acceso remoto y VPN sitio a sitio
   3. VPN a nivel de red: IPsec (IKEv2) con strongSwan y WireGuard
   4. VPN sobre TLS: OpenVPN
   5. VPN a nivel de aplicación: túneles SSH
7. Acceso remoto seguro
   1. Servidor como pasarela de acceso a la red interna
   2. Servidores de salto (*bastion host*)
   3. Protocolos de autenticación: PAP, CHAP, EAP, Kerberos
   4. Servidores de autenticación remota: RADIUS (FreeRADIUS) y su integración con LDAP/Active Directory
   5. Configuración de parámetros de acceso
8. Resumen
9. Referencias

### Prácticas

- **P6.1** Diseño de la topología perimetral del laboratorio (LAN, DMZ, WAN) y de la matriz de flujos permitidos.
- **P6.2** Cortafuegos con `nftables` en Debian a partir de un listado de reglas dado: política por defecto, servicios permitidos, NAT y registro. Incluye copia previa de la configuración, comprobación de sintaxis (`nft -c -f`) y procedimiento de recuperación.
- **P6.3** Cortafuegos perimetral con pfSense CE u OPNsense: interfaces, reglas, NAT y publicación de un servicio en la DMZ.
- **P6.4** Diagnóstico de problemas de conectividad provocados por reglas erróneas utilizando los registros del cortafuegos.
- **P6.5** Squid como *proxy*-caché con autenticación y restricciones de acceso web; modo transparente; monitorización de la actividad.
- **P6.6** *Proxy* inverso con Nginx delante de un servidor web de la DMZ.
- **P6.7** VPN de acceso remoto con WireGuard y VPN sitio a sitio con IPsec/strongSwan.
- **P6.8** Pasarela de acceso remoto con autenticación contra FreeRADIUS.
- **P6.9** Comprobación del perímetro desde el exterior con Nmap y verificación de que solo se exponen los servicios previstos.

### Supuesto profesional

Una empresa con sede central, una delegación y personal en teletrabajo necesita publicar su web, proteger su red interna y permitir el acceso remoto. Diseñar la arquitectura perimetral, implantarla en el laboratorio y documentar la instalación, configuración y uso.

---

## UD7. Alta disponibilidad, virtualización y continuidad de negocio

**RA:** RA6 · **CE:** RA6.a, RA6.b, RA6.c, RA6.d, RA6.e, RA6.f, RA6.g, RA6.h, RA6.i · **Horas:** 18

### Teoría

1. Introducción: el coste de la indisponibilidad
2. Objetivos de la unidad
3. Conceptos fundamentales
   1. Disponibilidad y fiabilidad; MTBF y MTTR
   2. Cálculo de la disponibilidad («los nueves»)
   3. Acuerdos de nivel de servicio (SLA)
   4. RPO y RTO
   5. Punto único de fallo (SPOF)
   6. Redundancia, tolerancia a fallos y funcionamiento ininterrumpido
4. Análisis de configuraciones de alta disponibilidad
   1. Activo-pasivo y activo-activo
   2. Escalado vertical y horizontal: soluciones para sistemas con demanda creciente
5. Virtualización de sistemas
   1. Hipervisores de tipo 1 y tipo 2
   2. Herramientas: Proxmox VE, KVM/QEMU, VirtualBox, VMware
   3. Contenedores: Docker y LXC
   4. Posibilidades de la virtualización para la alta disponibilidad: instantáneas, migración en caliente, plantillas, simulación de servicios
6. Servidores redundantes y *failover*
   1. IP virtual y protocolo VRRP con Keepalived
   2. Gestión de *clusters* con Pacemaker y Corosync: recursos, *quorum*, *fencing*/STONITH
7. Balanceo de carga
   1. Balanceo en capa 4 y en capa 7
   2. Algoritmos: *round robin*, menos conexiones, *hash* de origen
   3. Comprobaciones de salud (*health checks*) y persistencia de sesión
   4. HAProxy
8. Almacenamiento redundante y replicación
   1. Almacenamiento compartido: iSCSI y NFS
   2. Replicación de bloques: DRBD
   3. Almacenamiento distribuido: Ceph
   4. Replicación de bases de datos: MariaDB y PostgreSQL
   5. Integridad de datos y recuperación del servicio
9. *Clusters*
   1. Tipos: alta disponibilidad, alto rendimiento y balanceo de carga
   2. *Cluster* de Proxmox VE con alta disponibilidad de máquinas virtuales
10. Monitorización de la disponibilidad
    1. Zabbix o Prometheus + Grafana
    2. Alertas y umbrales
11. Alta disponibilidad en la nube: regiones, zonas de disponibilidad y servicios gestionados
12. Continuidad de negocio y recuperación ante desastres
    1. Plan de continuidad de negocio (BCP) y plan de recuperación ante desastres (DRP)
    2. Análisis de impacto en el negocio (BIA)
    3. CPD de respaldo: sitio caliente, templado y frío
    4. Pruebas y mantenimiento del plan
13. Resumen
14. Referencias

### Prácticas

En todas las prácticas se documentan tres momentos: **funcionamiento normal → provocación del fallo → comprobación de la recuperación**.

- **P7.1** Cálculo de la disponibilidad de una infraestructura e identificación de sus puntos únicos de fallo.
- **P7.2** Servidor web redundante con Keepalived (IP virtual). **Prueba de fallo:** detener el nodo maestro y comprobar la conmutación y la recuperación.
- **P7.3** Balanceador HAProxy delante de dos o tres servidores web con *health checks*. **Prueba de fallo:** detener un servidor y comprobar que el servicio continúa.
- **P7.4** Eliminación del SPOF del balanceador: dos HAProxy en alta disponibilidad con Keepalived.
- **P7.5** Replicación primario-réplica de MariaDB o PostgreSQL y promoción de la réplica ante la caída del primario.
- **P7.6** Almacenamiento replicado con DRBD y *cluster* activo-pasivo con Pacemaker.
- **P7.7** *Cluster* de Proxmox VE de tres nodos con alta disponibilidad de máquinas virtuales y migración en caliente (según los recursos del aula, puede realizarse con virtualización anidada).
- **P7.8** Monitorización de la infraestructura con Zabbix o Prometheus + Grafana y alertas ante caída de servicios.

### Supuesto profesional

Una tienda en línea sufre caídas en campañas de rebajas y exige un SLA del 99,9 %. Esquematizar y documentar una solución de alta disponibilidad (balanceo, redundancia de servidores, replicación de base de datos, copias y plan de recuperación), implantarla en el laboratorio y demostrar su comportamiento ante fallos.

---

## 4. Matriz de cobertura RA/CE por unidad

Cada criterio de evaluación queda asignado, al menos, a una unidad. **●** = tratamiento principal · **○** = tratamiento complementario.

| CE | UD1 | UD2 | UD3 | UD4 | UD5 | UD6 | UD7 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **RA1.a** Privacidad, coherencia y disponibilidad | ● | ○ | | | | | |
| **RA1.b** Seguridad física y lógica | ● | ● | | | | | |
| **RA1.c** Clasificación de vulnerabilidades | ● | | | ○ | | | |
| **RA1.d** Ingeniería social y fraude | ● | | | | | | |
| **RA1.e** Políticas de contraseñas | | | | ● | | | |
| **RA1.f** Sistemas biométricos | | | | ● | | | |
| **RA1.g** Técnicas criptográficas | | | ● | | | | |
| **RA1.h** Plan integral de protección perimetral | ○ | | | | | ● | |
| **RA1.i** Fases del análisis forense | | | | ● | | | |
| **RA2.a** Amenazas lógicas | | | | ● | ○ | | |
| **RA2.b** Origen y actualización del *software* | | | | ● | | | |
| **RA2.c** Anatomía de ataques | | | | ● | ● | | |
| **RA2.d** Análisis de amenazas en entornos controlados | | | | ● | ● | | |
| **RA2.e** Detección y eliminación de *malware* | | | | ● | | | |
| **RA2.f** Cifrado, firmas y certificados en redes públicas | | | ● | | | | |
| **RA2.g** Seguridad en redes inalámbricas | | | | | ● | | |
| **RA2.h** Inventario y control de servicios de red | | | | ○ | ● | | |
| **RA2.i** Sistemas de detección de intrusiones | | | | | ● | | |
| **RA3.a** Escenarios con conexión a redes públicas | | | | | | ● | |
| **RA3.b** Zonas de riesgo y seguridad perimetral | | | | | | ● | |
| **RA3.c** Protocolos seguros de comunicación | | | ● | | ○ | ○ | |
| **RA3.d** VPN a distintos niveles | | | | | | ● | |
| **RA3.e** Pasarela de acceso remoto | | | | | | ● | |
| **RA3.f** Métodos de autenticación remota | | | | | | ● | |
| **RA3.g** Servidor remoto de autenticación | | | | | ○ | ● | |
| **RA4.a** Características, tipos y funciones de cortafuegos | | | | | | ● | |
| **RA4.b** Niveles de filtrado | | | | | | ● | |
| **RA4.c** Planificación del cortafuegos | | | | | | ● | |
| **RA4.d** Configuración de filtros | | | | | | ● | |
| **RA4.e** Registros de sucesos del cortafuegos | | | | | | ● | |
| **RA4.f** Cortafuegos *software* y *hardware* | | | | | | ● | |
| **RA4.g** Diagnóstico de conectividad | | | | | | ● | |
| **RA4.h** Documentación del cortafuegos | | | | | | ● | |
| **RA5.a** Tipos de *proxy* | | | | | | ● | |
| **RA5.b** *Proxy*-caché | | | | | | ● | |
| **RA5.c** Autenticación en el *proxy* | | | | | | ● | |
| **RA5.d** *Proxy* transparente | | | | | | ● | |
| **RA5.e** Restricciones de acceso web | | | | | | ● | |
| **RA5.f** Problemas de acceso al *proxy* | | | | | | ● | |
| **RA5.g** Monitorización del *proxy* | | | | | | ● | |
| **RA5.h** *Proxy* inverso | | | | | | ● | ○ |
| **RA5.i** Documentación del *proxy* | | | | | | ● | |
| **RA6.a** Supuestos que requieren alta disponibilidad | | | | | | | ● |
| **RA6.b** Soluciones *hardware* de continuidad | | ● | | | | | ○ |
| **RA6.c** Virtualización para alta disponibilidad | | | | | | | ● |
| **RA6.d** Servidor redundante | | | | | | | ● |
| **RA6.e** Balanceador de carga | | | | | | | ● |
| **RA6.f** Almacenamiento redundante | | ● | | | | | ● |
| **RA6.g** Sistemas de *clusters* | | | | | | | ● |
| **RA6.h** Soluciones para demanda creciente | | | | | | | ● |
| **RA6.i** Documentación de soluciones de alta disponibilidad | | | | | | | ● |
| **RA7.a** Legislación de protección de datos | ● | | | | | | |
| **RA7.b** Control de acceso a datos personales | ● | | | ○ | | | |
| **RA7.c** Figuras legales | ● | | | | | | |
| **RA7.d** Derechos de las personas sobre sus datos | ● | | | | | | |
| **RA7.e** LSSI y comercio electrónico | ● | | | | | | |
| **RA7.f** Normas de gestión de la seguridad | ● | | | | | | |
| **RA7.g** Respeto a la normativa legal | ● | ○ | ○ | ○ | ○ | ○ | ○ |

---

## 5. Estructura común de cada unidad

Cada unidad se publica en dos páginas: **teoría** (`udXX-tema.md`) y **prácticas** (`udXX-tema-practicas.md`). Siempre que el contenido lo permita, siguen esta estructura:

1. Introducción
2. Objetivos
3. Conceptos fundamentales
4. Arquitectura o funcionamiento
5. Tecnologías y herramientas
6. Configuración
7. Ejemplo práctico
8. Comprobación
9. Problemas habituales
10. Buenas prácticas de seguridad
11. Ejercicios
12. Actividad práctica o supuesto profesional
13. Resumen
14. Referencias y documentación oficial

Cada práctica indica: **requisitos previos, sistema operativo y versión, paquetes necesarios, procedimiento con explicación de cada comando, resultado esperado, comprobaciones, errores habituales, consideraciones de seguridad** y, cuando modifica configuraciones críticas, **copia de seguridad previa, comprobación de sintaxis y procedimiento de vuelta atrás**.

---

## Anexo A. Laboratorio virtual del módulo

### Plataforma de referencia

| Función | Tecnología | Observaciones |
|---|---|---|
| Virtualización en el puesto del alumnado | VirtualBox o VMware Workstation | Hipervisor de tipo 2 |
| Virtualización en servidor del aula | Proxmox VE | Hipervisor de tipo 1; necesario para UD7 |
| Servidores Linux | Debian 13 (*trixie*) | Distribución de referencia de los apuntes |
| Alternativa Linux | Ubuntu Server LTS | Se indicarán las diferencias de rutas y paquetes |
| Servidores Windows | Windows Server 2025 (evaluación) | Directivas de grupo, Active Directory, Defender |
| Clientes | Debian con escritorio y Windows 11 | |
| Cortafuegos perimetral | pfSense CE u OPNsense | |
| Contenedores | Docker Engine | Para servicios auxiliares de prácticas concretas |

> En cada práctica se indicará la versión exacta utilizada cuando sea relevante para reproducirla.

### Topología de referencia

```text
                    Internet (NAT del hipervisor)
                               │
                        ┌──────┴──────┐
                        │ Cortafuegos │  pfSense / OPNsense / nftables
                        └──┬───────┬──┘
                           │       │
        LAN 192.168.10.0/24│       │DMZ 172.16.10.0/24
       ┌───────────────────┴┐    ┌─┴──────────────────┐
       │ Clientes, servidor │    │ Web, proxy inverso,│
       │ de ficheros, AD,   │    │ balanceador        │
       │ monitorización     │    │                    │
       └────────────────────┘    └────────────────────┘
```

### Normas de uso del laboratorio

- Las técnicas de ataque se ejecutan **exclusivamente** en redes de laboratorio aisladas y sobre sistemas propios.
- Antes de cada práctica que modifique configuraciones críticas se crea una **instantánea** de la máquina virtual.
- No se utilizan credenciales reales ni datos personales reales en las prácticas.

---

## Anexo B. Criterios técnicos de los apuntes

Para evitar tecnologías obsoletas (*deprecated*), los apuntes utilizan:

| Se utiliza | En lugar de | Motivo |
|---|---|---|
| `nftables` | `iptables` heredado | Marco de filtrado actual del núcleo Linux |
| `ip`, `ss` | `ifconfig`, `netstat` (`net-tools`) | `net-tools` está obsoleto |
| `systemctl`, `journalctl` | Scripts de `/etc/init.d` | `systemd` es el sistema de inicio de Debian y Ubuntu |
| Temporizadores de `systemd` o `cron` | — | Automatización de tareas |
| Claves de repositorio en `/etc/apt/keyrings` | `apt-key` | `apt-key` está retirado |
| TLS 1.2/1.3 | SSL, TLS 1.0/1.1 | TLS 1.0 y 1.1 están retirados (RFC 8996) |
| SHA-256/SHA-3, Argon2/yescrypt | MD5, SHA-1 para integridad o contraseñas | Algoritmos rotos o débiles |
| Claves SSH Ed25519 | Claves DSA | OpenSSH ya no admite DSA |
| WPA3 / WPA2-AES | WEP, WPA-TKIP | Protocolos inseguros |
| strongSwan con `swanctl` | Configuración `ipsec.conf` (*stroke*) | Interfaz heredada |
| WireGuard / IKEv2 | PPTP | PPTP es inseguro |

---

## Anexo C. Referencias normativas y técnicas

### Normativa educativa

- [Ley Orgánica 3/2022, de 31 de marzo, de ordenación e integración de la Formación Profesional](https://www.boe.es/eli/es/lo/2022/03/31/3)
- [Real Decreto 659/2023, de 18 de julio, por el que se desarrolla la ordenación del Sistema de Formación Profesional](https://www.boe.es/eli/es/rd/2023/07/18/659)
- [Real Decreto 1629/2009, de 30 de octubre, título de Técnico Superior en ASIR](https://www.boe.es/eli/es/rd/2009/10/30/1629)
- [Real Decreto 500/2024, de 21 de mayo, que modifica determinados títulos de FP de grado superior](https://www.boe.es/eli/es/rd/2024/05/21/500)
- [Decreto 114/2025, de 29 de julio, del Consell, currículos de ciclos de grado medio y superior (DOGV)](https://dogv.gva.es/datos/2025/08/04/pdf/2025_29742_es.pdf)
- [Conselleria de Educación: normativa de ordenación de la FP](https://ceice.gva.es/es/web/formacion-profesional/normativa-sobre-ordenacion-y-organizacion-academica-de-los-ciclos-formativos)
- [TodoFP: Técnico Superior en ASIR](https://www.todofp.es/que-estudiar/familias-profesionales/informatica-comunicaciones/admin-sist-informaticos-red.html)

### Legislación y normas de seguridad

- [Reglamento (UE) 2016/679 (RGPD)](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- [Ley Orgánica 3/2018 (LOPDGDD)](https://www.boe.es/eli/es/lo/2018/12/05/3)
- [Ley 34/2002 (LSSI)](https://www.boe.es/eli/es/l/2002/07/11/34)
- [Real Decreto 311/2022, Esquema Nacional de Seguridad](https://www.boe.es/eli/es/rd/2022/05/03/311)
- [Directiva (UE) 2022/2555 (NIS2)](https://eur-lex.europa.eu/eli/dir/2022/2555/oj)
- [Agencia Española de Protección de Datos](https://www.aepd.es/)
- [INCIBE](https://www.incibe.es/) · [CCN-CERT](https://www.ccn-cert.cni.es/) · [ENISA](https://www.enisa.europa.eu/)
- [MAGERIT v3 (PAe)](https://administracionelectronica.gob.es/pae_Home/pae_Documentacion/pae_Metodolog/pae_Magerit.html)

### Documentación técnica

- [Debian Administrator's Handbook](https://debian-handbook.info/) · [Debian Security](https://www.debian.org/security/)
- [NIST SP 800-63B: Digital Identity Guidelines](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [NIST SP 800-34: Contingency Planning Guide](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)
- [NIST FIPS 203: ML-KEM](https://csrc.nist.gov/pubs/fips/203/final)
- [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446) · [RFC 8996: retirada de TLS 1.0 y 1.1](https://www.rfc-editor.org/rfc/rfc8996) · [RFC 5798: VRRPv3](https://www.rfc-editor.org/rfc/rfc5798)
- [MITRE ATT&CK](https://attack.mitre.org/) · [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [OpenSSL](https://docs.openssl.org/) · [OpenSSH](https://www.openssh.com/manual.html) · [GnuPG](https://gnupg.org/documentation/)
- [nftables wiki](https://wiki.nftables.org/) · [pfSense](https://docs.netgate.com/pfsense/en/latest/) · [OPNsense](https://docs.opnsense.org/)
- [Squid](https://wiki.squid-cache.org/) · [Nginx](https://nginx.org/en/docs/) · [HAProxy](https://docs.haproxy.org/)
- [WireGuard](https://www.wireguard.com/) · [strongSwan](https://docs.strongswan.org/) · [FreeRADIUS](https://www.freeradius.org/documentation/)
- [Suricata](https://docs.suricata.io/) · [Wazuh](https://documentation.wazuh.com/) · [Greenbone](https://greenbone.github.io/docs/) · [Wireshark](https://www.wireshark.org/docs/) · [Nmap](https://nmap.org/book/)
- [Keepalived](https://keepalived.readthedocs.io/) · [ClusterLabs (Pacemaker/Corosync)](https://clusterlabs.org/) · [DRBD](https://linbit.com/drbd-user-guide/) · [Proxmox VE](https://pve.proxmox.com/pve-docs/)
- [BorgBackup](https://borgbackup.readthedocs.io/) · [restic](https://restic.readthedocs.io/) · [Zabbix](https://www.zabbix.com/documentation/current/) · [Prometheus](https://prometheus.io/docs/)