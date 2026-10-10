---
title: "Entorno de trabajo"
weight: 4
bookToc: true
---

# Entorno de trabajo

Todas las prácticas se realizan en **máquinas virtuales** sobre redes de laboratorio aisladas. Así puedes equivocarte, atacar tu propio sistema y recuperarte sin riesgo para equipos reales.

> [!CAUTION]
> Las técnicas de ataque y análisis de estos apuntes se ejecutan **exclusivamente** en las redes virtuales del laboratorio y sobre máquinas propias. Usarlas contra sistemas ajenos sin autorización puede ser delito (Código Penal, arts. 197 bis, 197 ter y 264 y siguientes).

## Requisitos del equipo anfitrión

| Recurso | Mínimo | Recomendado |
|---|---|---|
| Procesador | 4 núcleos con virtualización (VT-x / AMD-V) activada en la BIOS/UEFI | 8 núcleos |
| Memoria | 16 GB | 32 GB |
| Disco | 120 GB libres (preferiblemente SSD) | 250 GB |
| Sistema anfitrión | Windows 11, Linux o macOS | — |

## Software de referencia

| Función | Tecnología | Observaciones |
|---|---|---|
| Virtualización en tu equipo | VirtualBox 7.x o VMware Workstation | Hipervisor de tipo 2 |
| Virtualización en el servidor del aula | Proxmox VE 9.x | Hipervisor de tipo 1; necesario para la práctica de clúster de la UD07 |
| Servidores Linux | **Debian 13 «trixie»** | Distribución de referencia de todos los apuntes |
| Alternativas Linux | Ubuntu Server LTS, AlmaLinux | Cuando cambian rutas, paquetes u órdenes, se indica con pestañas |
| Servidores Windows | Windows Server 2025 (versión de evaluación) | Directivas de grupo, Active Directory, Defender |
| Clientes | Debian con escritorio y Windows 11 | |
| Cortafuegos dedicado | OPNsense o pfSense CE | UD06 |
| Contenedores | Docker Engine | Servicios auxiliares de prácticas concretas |
| Análisis y herramientas | Wireshark, Nmap, OpenSSH, OpenSSL, Lynis, Suricata, Wazuh | Se explican en la unidad donde se usan |

> [!NOTE]
> Cada práctica indica la versión exacta cuando importa para reproducirla. Descarga siempre las imágenes de la **web oficial** de cada proyecto y comprueba su suma de verificación (práctica de la UD01).

## Redes virtuales

| Red | Tipo en VirtualBox | Uso |
|---|---|---|
| `sad-nat` | Red NAT | Salida a Internet para instalar paquetes |
| `sad-lan` | Red interna | LAN de la clínica (192.168.10.0/24) |
| `sad-dmz` | Red interna | DMZ (172.16.10.0/24) |
| `sad-atk` | Red interna | Máquina atacante, aislada de Internet |

Primero instala paquetes con salida a Internet; después deja solo las redes internas que necesita cada práctica.

## Buenas costumbres de laboratorio

- **Instantánea antes de cada práctica** que modifique configuraciones críticas. Nómbrala con la unidad y la práctica (`ud04-p3-antes`).
- **Nombres coherentes**: `fw01`, `srv-gestion`, `web01`… (ver el [proyecto transversal](/guia/proyecto-clinica/)).
- **Carpeta de evidencias** en cada máquina (`~/evidencias/udNN/`) con las salidas de órdenes (para repasar y para la práctica integradora; las prácticas de unidad no se entregan).
- **Copia de la configuración** antes de tocar un fichero crítico, **comprobación de sintaxis** antes de aplicarlo y **verificación** después.
- Nunca reutilices contraseñas reales. Las del laboratorio son de prueba y no se escriben en ningún fichero que vayas a compartir.
