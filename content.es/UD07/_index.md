---
title: "UD7. Seguridad perimetral: cortafuegos y proxy"
weight: 7
bookCollapseSection: true
---

# UD7. Seguridad perimetral: cortafuegos y proxy

> Diseño e implantación del perímetro de una red: arquitecturas, DMZ, cortafuegos (nftables y OPNsense/pfSense), NAT, registro de sucesos, servidores proxy (directo, transparente, inverso), autenticación, filtrado de contenidos y WAF.

| Datos de la unidad | Información |
| --- | --- |
| Módulo | 0378. Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR · 2026/27 |
| Duración | 14 horas |
| Material | [Teoría](teoria/) · [Prácticas](practicas/) |

## Resultados de aprendizaje y criterios de evaluación

| RA | Criterio de evaluación |
| --- | --- |
| RA1 | h) Se ha reconocido la necesidad de establecer un plan integral de protección perimetral, especialmente en sistemas conectados a redes públicas. |
| RA3 | a) Se han descrito escenarios típicos de sistemas con conexión a redes públicas en los que se precisa fortificar la red interna. |
| RA3 | b) Se han clasificado las zonas de riesgo de un sistema, según criterios de seguridad perimetral. |
| RA4 | a) Se han descrito las características, tipos y funciones de los cortafuegos. |
| RA4 | b) Se han clasificado los niveles en los que se realiza el filtrado de tráfico. |
| RA4 | c) Se ha planificado la instalación de cortafuegos para limitar los accesos a determinadas zonas de la red. |
| RA4 | d) Se han configurado filtros en un cortafuegos a partir de un listado de reglas de filtrado. |
| RA4 | e) Se han revisado los registros de sucesos de cortafuegos, para verificar que las reglas se aplican correctamente. |
| RA4 | f) Se han probado distintas opciones para implementar cortafuegos, tanto software como hardware. |
| RA4 | g) Se han diagnosticado problemas de conectividad en los clientes provocados por los cortafuegos. |
| RA4 | h) Se ha elaborado documentación relativa a la instalación, configuración y uso de cortafuegos. |
| RA5 | a) Se han identificado los tipos de «proxy», sus características y funciones principales. |
| RA5 | b) Se ha instalado y configurado un servidor «proxy-cache». |
| RA5 | c) Se han configurado los métodos de autenticación en el «proxy». |
| RA5 | d) Se ha configurado un «proxy» en modo transparente. |
| RA5 | e) Se ha utilizado el servidor «proxy» para establecer restricciones de acceso Web. |
| RA5 | f) Se han solucionado problemas de acceso desde los clientes al «proxy». |
| RA5 | g) Se han realizado pruebas de funcionamiento del «proxy», monitorizando su actividad con herramientas gráficas. |
| RA5 | h) Se ha configurado un servidor «proxy» en modo inverso. |
| RA5 | i) Se ha elaborado documentación relativa a la instalación, configuración y uso de servidores «proxy». |

## Contenidos

- Perímetro, defensa en profundidad y zonas de seguridad.
- Arquitecturas: router apantallado, host bastión, subred apantallada, DMZ con uno o dos cortafuegos.
- Tipos de cortafuegos: filtrado de paquetes, con estado, de aplicación, NGFW. Software y hardware.
- Netfilter y nftables: tablas, cadenas, hooks, reglas, conjuntos y registro.
- NAT: SNAT, enmascaramiento y DNAT (publicación de servicios).
- Cortafuegos dedicados: OPNsense y pfSense.
- Registro y análisis de sucesos; diagnóstico de problemas de conectividad.
- Proxy directo y caché con Squid: ACL, autenticación, modo transparente, filtrado y monitorización.
- Proxy inverso con Nginx: TLS, cabeceras, limitación de peticiones, WAF.
- Alta disponibilidad del perímetro y gestión de cambios.

## Entorno de laboratorio

Una máquina Linux con tres interfaces actuando como cortafuegos (WAN, LAN y DMZ), un cliente en la LAN y un servidor en la DMZ. Opcional: OPNsense o pfSense CE.

> [!TIP]
> Antes de empezar las prácticas, crea una instantánea (*snapshot*) de cada máquina virtual. Si algo sale mal, podrás volver al estado inicial en segundos.

## Cómo estudiar esta unidad

1. Lee la [teoría](teoria/) en orden: cada apartado se apoya en el anterior.
2. Reproduce los ejemplos en tu laboratorio a medida que aparecen.
3. Resuelve los ejercicios de cada apartado antes de mirar las soluciones.
4. Realiza las [prácticas](practicas/) y entrega la tarea evaluable con las evidencias solicitadas.
