---
title: "UD6. Seguridad perimetral: cortafuegos, proxy, VPN y acceso remoto"
weight: 60
---

# UD6 · Seguridad perimetral: cortafuegos, *proxy*, VPN y acceso remoto

La red de una organización ya no termina en las paredes de la oficina: la web se publica en Internet, el personal teletrabaja y las delegaciones se conectan a la sede. En esta unidad aprendes a **decidir dónde están los límites de la red**, a controlar con un **cortafuegos** qué tráfico los cruza, a intermediar la navegación y la publicación de servicios con **servidores *proxy***, y a dar **acceso remoto seguro** al personal mediante **VPN**, servidores de salto y **autenticación centralizada**. Es la unidad más extensa del módulo y su práctica final es el **perímetro de Mediterránea Dental**.

{{< ra "RA1:h" "RA3:a,b,c,d,e,f,g" "RA4:a,b,c,d,e,f,g,h" "RA5:a,b,c,d,e,f,g,h,i" >}}

| Página | Contenido |
|---|---|
| [Teoría](/ud06-seguridad-perimetral/ud06-teoria/) | Perímetro, zonas y DMZ; cortafuegos y niveles de filtrado; `nftables`, NAT, `firewalld`, UFW, OPNsense y cortafuegos de Windows; registros y diagnóstico; Squid, PAC/WPAD, proxy transparente e inverso (Nginx) y WAF; VPN (WireGuard, IPsec, OpenVPN, túneles SSH); servidores de salto, PAP/CHAP/EAP/Kerberos y RADIUS |
| [Prácticas](/ud06-seguridad-perimetral/ud06-practicas/) | Diez prácticas guiadas, autónomas y de reto (diseño de zonas, cortafuegos con `nftables`, OPNsense, diagnóstico, Squid, proxy inverso, WireGuard, SSH avanzado, FreeRADIUS y comprobación con Nmap) y la Tarea del proyecto «Perímetro de Mediterránea Dental» con rúbrica |

> [!NOTE]
> Esta unidad se apoya en las anteriores: el cifrado y los certificados de la [UD3](/ud03-criptografia/ud03-teoria/), el bastionado de la [UD4](/ud04-fortificacion-hosts/ud04-teoria/) y la segmentación y la detección de la [UD5](/ud05-seguridad-redes/ud05-teoria/). La redundancia del propio cortafuegos se desarrolla en la [UD7](/ud07-alta-disponibilidad/ud07-teoria/).

**Duración:** 25 horas (9 h teoría · 14 h prácticas · 2 h evaluación)
