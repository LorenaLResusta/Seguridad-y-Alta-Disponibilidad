º

# UD2 - Seguridad pasiva: almacenamiento

> Protección de la información, redundancia, copias de seguridad y recuperación.

| Datos de la unidad | Información |
| --- | --- |
| Módulo | Seguridad y Alta Disponibilidad |
| Curso | 2.º ASIR |
| Modalidad | Semipresencial |
| Duración | 12 horas |

## Índice

1. [Fundamentos y seguridad física](#1-fundamentos-y-seguridad-física)
2. [Almacenamiento y fallos](#2-almacenamiento-y-fallos)
3. [Redundancia y RAID](#3-redundancia-y-raid)
4. [Copias de seguridad y recuperación](#4-copias-de-seguridad-y-recuperación)
5. [Borrado seguro y ciclo de vida](#5-borrado-seguro-y-ciclo-de-vida)
6. [Resumen](#6-resumen)
7. [Recursos](#7-recursos)
8. [Relación con los resultados de aprendizaje](#8-relación-con-los-resultados-de-aprendizaje)

---

## 1. Fundamentos y seguridad física

### 1.1. Introducción

La seguridad de un sistema informático no consiste únicamente en impedir que un atacante acceda a él. También es necesario estar preparado para situaciones en las que se produzcan fallos.

Un servidor puede sufrir:

- La avería de un disco.
- Un fallo eléctrico.
- Un error humano.
- La eliminación accidental de archivos.
- La corrupción de un sistema de archivos.
- Un ataque de ransomware.
- Un incendio o una inundación.
- El robo del equipamiento.
- Una actualización defectuosa.
- Un fallo de software.

Por este motivo, las organizaciones necesitan mecanismos que permitan reducir el impacto de los incidentes y recuperar la información y los servicios.

Estos mecanismos forman parte de la seguridad pasiva.

En esta unidad estudiaremos especialmente los sistemas de almacenamiento, la redundancia mediante RAID, las copias de seguridad, los sistemas NAS, las snapshots y las estrategias de recuperación.

### 1.2. Objetivos

Al finalizar esta unidad, el alumnado será capaz de:

- Diferenciar seguridad activa y seguridad pasiva.
- Identificar los principales sistemas de almacenamiento.
- Diferenciar HDD, SSD y NVMe.
- Identificar los principales tipos de fallos de almacenamiento.
- Comprender el concepto de redundancia.
- Explicar el funcionamiento de RAID.
- Diferenciar RAID 0, RAID 1, RAID 5, RAID 6 y RAID 10.
- Seleccionar un nivel RAID en función de las necesidades.
- Comprender las limitaciones de RAID.
- Explicar qué es una copia de seguridad.
- Diferenciar copias completas, incrementales y diferenciales.
- Diseñar una estrategia básica de copias.
- Aplicar la regla 3-2-1.
- Comprender los conceptos RPO y RTO.
- Conocer sistemas NAS y snapshots.
- Realizar y comprobar copias de seguridad y recuperación.
- Diseñar una política de almacenamiento y backup.
### 1.3. Seguridad pasiva

La seguridad pasiva engloba las medidas destinadas principalmente a reducir las consecuencias de un incidente y facilitar la recuperación.

Por ejemplo, imaginemos un servidor que dispone de dos discos.

Si uno de ellos falla, una configuración redundante puede permitir que el sistema continúe funcionando.

Si además se dispone de copias de seguridad, será posible recuperar la información incluso ante problemas más graves.

Podemos representar el concepto de la siguiente forma:

                    SEGURIDAD
                       │
              ┌────────┴────────┐
              │                 │
            Activa            Pasiva
              │                 │
       Prevenir / detectar    Recuperar
       / bloquear             / continuar
**Ejemplos de seguridad activa:**

- Firewall.
- Antivirus.
- IDS/IPS.
- Control de acceso.
- Monitorización y sistemas de detección.

**Ejemplos de seguridad pasiva:**

- RAID y sistemas redundantes.
- Copias de seguridad y almacenamiento externo.
- SAI y replicación.
- Planes de recuperación.

### 1.4. Seguridad física y CPD

Un centro de procesamiento de datos (CPD) concentra servidores, redes y almacenamiento críticos. Centralizar los equipos facilita el control de accesos, la climatización, el mantenimiento y las comunicaciones, pero también exige planificar los riesgos físicos y ambientales. La ubicación debe evitar zonas con elevado riesgo de inundación, incendio, vibraciones o accesos no controlados, y la sala debe contar con procedimientos documentados para recuperar los servicios ante una incidencia.

Las medidas habituales incluyen control de acceso mediante credenciales o biometría, videovigilancia, detección y extinción de incendios, falso suelo para cableado y ventilación, y control de temperatura y humedad. En un CPD con racks, los pasillos fríos aportan aire a la parte frontal de los equipos y los pasillos calientes recogen el aire de salida; esta separación reduce el sobrecalentamiento y mejora la eficiencia energética.

La continuidad también requiere alimentación y comunicaciones redundantes. Un SAI proporciona tiempo para un apagado controlado durante un corte breve; un generador puede cubrir interrupciones prolongadas. Para servicios críticos, se pueden contratar enlaces de Internet con proveedores y rutas diferentes. Un centro de respaldo, ubicado a suficiente distancia del CPD principal, permite restaurar servicios si una catástrofe afecta a la ubicación primaria. Por ejemplo, una empresa puede replicar la base de datos y conservar copias verificadas en un segundo centro, probando periódicamente el procedimiento de conmutación.

## 2. Almacenamiento y fallos

### 2.1. Almacenamiento de la información

La información de una organización puede almacenarse en diferentes dispositivos y sistemas.

Entre los más habituales encontramos:

HDD.
SSD.
NVMe.
NAS.
SAN.
Cabinas de almacenamiento.
Sistemas distribuidos.

La elección depende de factores como:

Capacidad.
Rendimiento.
Coste.
Fiabilidad.
Disponibilidad.
Redundancia.
Tipo de información.

También importa la forma de acceso: un sistema de copias históricas puede utilizar cinta, que ofrece gran capacidad a bajo coste pero acceso secuencial; una base de datos necesita normalmente acceso aleatorio y baja latencia, por lo que puede requerir SSD o NVMe. Para compartir documentos entre varios equipos suele ser suficiente un NAS con acceso a nivel de archivo, mientras que un entorno de virtualización puede necesitar almacenamiento de bloques mediante SAN o una plataforma definida por software.

Por ejemplo, una pequeña empresa puede combinar SSD para las máquinas virtuales que ejecutan aplicaciones, HDD en un NAS para documentos compartidos y almacenamiento externo para una copia de seguridad. No existe una tecnología universalmente mejor: la solución adecuada responde a los requisitos de rendimiento, disponibilidad, presupuesto y protección de los datos.
### 2.2. Discos HDD

Los discos HDD utilizan platos magnéticos y cabezales mecánicos para almacenar y recuperar información.

Una representación simplificada sería:

       HDD
 ┌───────────────┐
 │   Plato       │
 │      ↓        │
 │  ──────────   │
 │      ↑        │
 │   Cabezal     │
 └───────────────┘
Ventajas
Gran capacidad.
Precio reducido por GB.
Adecuados para grandes volúmenes de información.
Interesantes para almacenamiento de backup.
Inconvenientes
Componentes mecánicos.
Mayor latencia.
Menor rendimiento que los SSD en determinados escenarios.
Sensibilidad a golpes y vibraciones.
### 2.3. Discos SSD

Los SSD almacenan la información en memoria flash.

No utilizan partes mecánicas móviles.

Ventajas
Alta velocidad.
Baja latencia.
Menor ruido.
Mayor resistencia frente a vibraciones.
Buen rendimiento para sistemas operativos y aplicaciones.
Inconvenientes
Precio por GB generalmente superior.
Desgaste de las celdas.
Recuperación de datos potencialmente compleja ante determinados fallos.

Los SSD son habituales en:

Servidores.
Ordenadores.
Máquinas virtuales.
Bases de datos.
Sistemas de alto rendimiento.
### 2.4. NVMe

NVMe es un protocolo diseñado específicamente para dispositivos de almacenamiento no volátil de alta velocidad.

Los dispositivos NVMe suelen utilizar PCI Express.

Comparados con dispositivos SATA tradicionales, pueden proporcionar:

Mayor ancho de banda.
Menor latencia.
Mayor número de operaciones de entrada/salida.

Son especialmente interesantes para:

Bases de datos.
Virtualización.
Servidores.
Aplicaciones con muchas operaciones de disco.
### 2.5. Fallos de almacenamiento

Los problemas de almacenamiento pueden tener diferentes orígenes.

#### 2.5.1. Fallo físico

Ejemplo:

El disco deja de funcionar.

Puede producirse por:

Desgaste.
Temperatura.
Fallo electrónico.
Fallo mecánico.
Daños físicos.
#### 2.5.2. Fallo lógico

El dispositivo continúa funcionando, pero la información o el sistema de archivos presenta problemas.

Ejemplos:

Corrupción del sistema de archivos.
Partición dañada.
Eliminación accidental.
Metadatos corruptos.
#### 2.5.3. Error humano

Un administrador puede ejecutar accidentalmente:

rm -rf

sobre el directorio equivocado.

También puede producirse:

Sobrescritura de archivos.
Eliminación de bases de datos.
Configuración incorrecta.
Formateo accidental.
#### 2.5.4. Malware

Un ransomware puede cifrar los archivos disponibles.

Por ejemplo:

documento1.docx
      ↓
documento1.docx.cifrado

Si el sistema de backup está conectado y accesible desde el mismo entorno, también podría verse afectado.

#### 2.5.5. Catástrofes físicas

Algunos riesgos son:

Incendio.
Inundación.
Robo.
Sobretensión.
Fallo de refrigeración.

Por ello es recomendable disponer de copias en una ubicación diferente.

### 2.6. Fiabilidad y monitorización del almacenamiento

Al seleccionar almacenamiento deben valorarse capacidad, rendimiento, coste, consumo, durabilidad y fiabilidad. El **MTBF** expresa una estimación estadística del tiempo medio entre fallos de una población de unidades, mientras que la **AFR** representa la tasa anualizada de fallos. Ninguna métrica predice el momento exacto en que fallará un disco concreto; por ello, las decisiones deben complementarse con redundancia, copias de seguridad y supervisión.

La tecnología SMART permite consultar indicadores de salud de HDD y SSD, como sectores reasignados, errores de lectura, temperatura y, en SSD, desgaste de las celdas. Una alerta SMART debe provocar la revisión y sustitución planificada de la unidad, pero su ausencia no garantiza que no vaya a fallar. Por ejemplo, si un servidor detecta sectores reasignados crecientes en un disco de un RAID 5, el administrador debe sustituirlo antes de que coincida con otro fallo durante la reconstrucción.

| Necesidad | Opción habitual | Ejemplo |
| --- | --- | --- |
| Gran capacidad a bajo coste | HDD o cinta para archivado. | Copias históricas mensuales. |
| Baja latencia y muchas operaciones de E/S | SSD NVMe. | Base de datos o máquinas virtuales. |
| Compartición de archivos | NAS con SMB/NFS. | Documentación de un departamento. |
| Acceso por bloques de alto rendimiento | SAN o almacenamiento definido por software. | Clúster de virtualización. |

## 3. Redundancia y RAID

### 3.1. Redundancia

La redundancia consiste en disponer de elementos adicionales que permitan mantener el servicio cuando uno de ellos falla.

Ejemplo:

Servidor
 ├── Disco 1
 └── Disco 2

Si ambos contienen información redundante y uno falla, el sistema puede continuar funcionando.

La redundancia puede aplicarse a:

Discos.
Fuentes de alimentación.
Servidores.
Redes.
Conexiones a Internet.
Sistemas de almacenamiento.
### 3.2. RAID

RAID — Redundant Array of Independent Disks

RAID permite combinar varios discos para conseguir diferentes objetivos:

Mayor rendimiento.
Redundancia.
Tolerancia a fallos.
Mayor capacidad útil.

Sin embargo, RAID no es un sistema de backup.

Esta diferencia debe quedar clara:

RAID
↓
Protección principalmente frente a fallos de discos

BACKUP
↓
Protección frente a pérdida, modificación o destrucción de información
### 3.3. RAID 0

RAID 0 distribuye los datos entre varios discos mediante una técnica denominada striping.

Ejemplo:

       RAID 0

Disco 1       Disco 2
--------      --------
Bloque A      Bloque B
Bloque C      Bloque D
Bloque E      Bloque F
Ventaja

Puede aumentar considerablemente el rendimiento.

Inconveniente

No existe redundancia.

Si falla uno de los discos:

Disco 1 → OK
Disco 2 → FALLA

se puede perder el conjunto completo de información.

Uso

Puede utilizarse cuando el rendimiento es prioritario y los datos pueden reconstruirse desde otra fuente.

### 3.4. RAID 1

RAID 1 utiliza mirroring, es decir, mantiene una copia de los datos en otro disco.

Disco 1       Disco 2

Datos A       Datos A
Datos B       Datos B
Datos C       Datos C

Si un disco falla:

Disco 1 → FALLA
Disco 2 → OK

la información continúa disponible.

Ventajas
Sencillo.
Buena tolerancia a fallos.
Recuperación relativamente sencilla.
Inconveniente

La capacidad útil es aproximadamente la de un único disco.

Por ejemplo:

2 × 2 TB

proporcionan aproximadamente:

2 TB útiles
### 3.5. RAID 5

RAID 5 combina distribución de datos y paridad.

Necesita al menos tres discos.

Una representación simplificada:

Disco 1   Disco 2   Disco 3

Datos     Datos     Paridad
Datos     Paridad   Datos
Paridad   Datos     Datos

La información de paridad permite reconstruir los datos cuando falla uno de los discos.

Ventajas
Tolerancia a un fallo.
Buen aprovechamiento de la capacidad.
Puede proporcionar un equilibrio entre rendimiento, capacidad y redundancia.
Inconvenientes
La reconstrucción puede ser lenta.
Durante la reconstrucción existe una situación de mayor riesgo.
Las operaciones de escritura tienen un coste adicional debido a la paridad.
### 3.6. RAID 6

RAID 6 utiliza doble paridad.

Necesita al menos cuatro discos y puede soportar el fallo simultáneo de dos unidades.

Disco 1   Disco 2   Disco 3   Disco 4
Datos     Datos     Paridad   Paridad
Datos     Paridad   Datos     Paridad
Paridad   Datos     Datos     Paridad

Es apropiado para sistemas con grandes cantidades de almacenamiento donde se desea una mayor tolerancia a fallos.

### 3.7. RAID 10

RAID 10 combina:

RAID 1 → redundancia.
RAID 0 → distribución.

Ejemplo:

          RAID 10

       ┌─────────────┐
       │             │
    RAID 1        RAID 1
    D1 + D2       D3 + D4
       │             │
       └──── RAID 0 ─┘

Proporciona:

Buen rendimiento.
Redundancia.
Buen comportamiento en sistemas con muchas operaciones de entrada/salida.

El número de discos necesarios es superior al de RAID 1.

### 3.8. Comparación de RAID

| Nivel | Discos mínimos | Redundancia | Tolerancia | Característica principal |
| --- | ---: | --- | --- | --- |
| RAID 0 | 2 | No | Ninguna | Rendimiento |
| RAID 1 | 2 | Sí | 1 disco | Simplicidad |
| RAID 5 | 3 | Sí | 1 disco | Capacidad + redundancia |
| RAID 6 | 4 | Sí | 2 discos | Mayor tolerancia |
| RAID 10 | 4 | Sí | Depende del patrón de fallos | Rendimiento + redundancia |

### 3.9. RAID no es backup

Este concepto es especialmente importante.

Supongamos que tenemos:

Servidor
   ↓
RAID 1
   ↓
Disco A + Disco B

Un usuario elimina accidentalmente:

clientes.xlsx

La eliminación se replica en ambos discos.

Por tanto:

Disco A → archivo eliminado
Disco B → archivo eliminado

RAID no permite recuperar automáticamente el archivo.

En cambio, un backup podría contener una versión anterior:

Backup
   ↓
clientes.xlsx
   ↓
Recuperación

Por ello:

RAID protege principalmente frente a determinados fallos de hardware; el backup protege la información frente a muchos tipos de pérdida o alteración.

## 4. Copias de seguridad y recuperación

### 4.1. Copias de seguridad

Una copia de seguridad es una copia de información almacenada en un medio alternativo que puede utilizarse para recuperar los datos originales tras una pérdida, daño, corrupción o incidente. Debe proteger datos, configuraciones y, cuando sea necesario, imágenes de sistemas completos. Una imagen facilita la restauración de un equipo tras un fallo grave; en cambio, una copia de archivos permite recuperar selectivamente un documento sin restaurar todo el sistema.

Una estrategia de backup debe definir:

Qué información copiar.
Cuándo copiarla.
Dónde almacenarla.
Cuánto tiempo conservarla.
Quién puede acceder.
Cómo protegerla.
Cómo restaurarla.
Cómo comprobar que funciona.

Las copias deben automatizarse siempre que sea posible, cifrarse cuando contienen información sensible y supervisarse mediante avisos de éxito o error. Una planificación habitual puede combinar una copia completa semanal, copias incrementales diarias y una retención diferenciada para versiones diarias, mensuales y anuales. La periodicidad debe responder al RPO: si una organización solo acepta perder hasta cuatro horas de trabajo, una copia diaria no será suficiente.

La restauración es la prueba definitiva de una estrategia. Por ejemplo, después de configurar una copia programada de una base de datos, el administrador debe restaurarla en un entorno de pruebas, comprobar que abre correctamente y medir el tiempo empleado. Esa evidencia permite confirmar si el procedimiento cumple el RTO establecido.
### 4.2. Backup completo

Una copia completa contiene toda la información seleccionada.

Ejemplo:

Domingo
Backup completo → 500 GB

Ventajas:

Restauración sencilla.
Independencia respecto de otras copias.

Inconvenientes:

Consume más almacenamiento.
Puede tardar más tiempo.
### 4.3. Backup incremental

Una copia incremental contiene los cambios realizados desde la última copia.

Ejemplo:

Domingo
Completa

Lunes
Cambios del lunes

Martes
Cambios del martes

Miércoles
Cambios del miércoles

Ventaja:

Menor consumo de espacio.

Inconveniente:

Para realizar una recuperación completa puede ser necesario disponer de:

Backup completo
+
Incremental lunes
+
Incremental martes
+
Incremental miércoles
### 4.4. Backup diferencial

La copia diferencial almacena los cambios realizados desde la última copia completa.

Ejemplo:

Domingo
Completa

Lunes
Cambios desde domingo

Martes
Cambios desde domingo + lunes

Miércoles
Cambios desde domingo + lunes + martes

Para recuperar el estado del miércoles normalmente necesitamos:

Backup completo
+
Backup diferencial del miércoles
### 4.5. Comparación de copias

| Tipo | Espacio | Velocidad de backup | Recuperación |
| --- | --- | --- | --- |
| Completa | Alto | Menor | Muy sencilla |
| Incremental | Bajo | Alta | Más compleja |
| Diferencial | Medio | Intermedia | Sencilla |

### 4.6. Regla 3-2-1

La regla 3-2-1 es una estrategia sencilla para mejorar la protección de los backups.

Consiste en mantener:

3 copias de la información

2 soportes diferentes

1 copia fuera de la ubicación principal

Ejemplo:

                 DATOS
                   │
          ┌────────┼────────┐
          │        │        │
       Original   NAS     Cloud
                         / ubicación externa

Esto permite reducir el riesgo de que un único incidente destruya todas las copias.

### 4.7. Backup y ransomware

Los sistemas de backup también deben protegerse.

Imaginemos:

Servidor
    ↓
Backup NAS

Si el atacante consigue privilegios suficientes sobre ambos sistemas, podría cifrar:

Servidor → cifrado
NAS      → cifrado

Por ello debemos aplicar medidas adicionales:

Separación de cuentas.
Contraseñas robustas.
MFA.
Permisos mínimos.
Segmentación de red.
Versionado.
Copias desconectadas cuando sea posible.
Almacenamiento inmutable.
Copias externas.
Pruebas de recuperación.
### 4.8. RPO

RPO — Recovery Point Objective

El RPO indica la cantidad máxima de información que una organización está dispuesta a perder.

Ejemplo:

RPO = 4 horas

Significa que la estrategia debe permitir recuperar información con una antigüedad máxima objetivo de unas cuatro horas.

Cuanto menor sea el RPO:

RPO pequeño
    ↓
Más frecuencia de copia/replicación
    ↓
Mayor coste y complejidad
### 4.9. RTO

RTO — Recovery Time Objective

El RTO indica cuánto tiempo puede tardar como máximo la recuperación de un servicio.

Ejemplo:

RTO = 8 horas

La organización debe disponer de procedimientos y recursos adecuados para intentar recuperar el servicio dentro de ese objetivo.

### 4.10. Diferencia entre RPO y RTO

| Concepto | Pregunta |
| --- | --- |
| RPO | ¿Cuánta información podemos perder? |
| RTO | ¿Cuánto tiempo podemos estar sin servicio? |

Ejemplo:

Una empresa establece:

RPO = 1 hora
RTO = 4 horas

Por tanto:

Se intenta limitar la pérdida de información a una hora.
Se intenta recuperar el servicio en cuatro horas.
### 4.11. NAS

Un NAS — Network Attached Storage es un dispositivo de almacenamiento conectado a una red.

Permite proporcionar almacenamiento centralizado a diferentes equipos.

             ┌──── PC 1
             │
Red ─────────┼──── PC 2
             │
             ├──── PC 3
             │
             └──── NAS

Un NAS puede proporcionar:

Carpetas compartidas.
Usuarios.
Permisos.
RAID.
Snapshots.
Copias de seguridad.
Replicación.
Servicios de red.
### 4.12. NAS frente a almacenamiento local
Almacenamiento local
PC
 ↓
Disco

Los datos están directamente en el equipo.

NAS
PC ───┐
PC ───┼── Red ── NAS
PC ───┘

Los datos se centralizan en un sistema de almacenamiento accesible mediante red.

Esto facilita:

Administración.
Compartición.
Backup.
Control de acceso.
### 4.13. TrueNAS

TrueNAS es una plataforma utilizada para implementar sistemas de almacenamiento en red.

Permite trabajar con:

Discos.
Pools de almacenamiento.
Sistemas de archivos.
Usuarios.
Permisos.
Comparticiones.
Snapshots.
Replicación.
Servicios de red.

En un entorno de pruebas de ASIR puede utilizarse para practicar:

RAID.
Almacenamiento.
Compartición de archivos.
Backup.
Snapshots.
Recuperación.
### 4.14. Snapshots

Una snapshot representa el estado de un sistema de archivos o almacenamiento en un momento determinado.

Ejemplo:

10:00 → Snapshot 1
12:00 → Snapshot 2
14:00 → Snapshot 3

Si un usuario modifica un archivo a las 14:30, puede ser posible recuperar una versión anterior mediante una snapshot.

Las snapshots son especialmente útiles para:

Errores humanos.
Recuperación rápida.
Versionado.
Protección frente a determinadas modificaciones.

Pero:

Una snapshot no sustituye necesariamente a una copia de seguridad.

Si todas las snapshots están almacenadas en el mismo dispositivo que los datos y este dispositivo se destruye, también pueden perderse las snapshots.

### 4.15. Recuperación de información

Una estrategia de backup debe incluir procedimientos de recuperación.

Proceso básico:

Incidente
   ↓
Identificar información afectada
   ↓
Seleccionar backup
   ↓
Restaurar
   ↓
Comprobar integridad
   ↓
Comprobar aplicación
   ↓
Poner servicio en producción
   ↓
Documentar
### 4.16. Pruebas de restauración

No basta con realizar copias.

Es necesario comprobar periódicamente que pueden restaurarse.

Una prueba puede consistir en:

Seleccionar una copia.
Restaurar algunos archivos.
Comprobar su contenido.
Restaurar una máquina virtual.
Comprobar una base de datos.
Medir el tiempo de recuperación.
Registrar los resultados.

Una copia que nunca ha sido probada supone un riesgo.

### 4.17. Política de backup

Una política de copias debería definir claramente:

Información protegida

Ejemplo:

Bases de datos.
Documentos.
Configuraciones.
Máquinas virtuales.
Servidores.
Frecuencia

Ejemplo:

Backup completo → semanal
Backup incremental → diario
Retención

Ejemplo:

Diarios → 30 días
Semanales → 3 meses
Mensuales → 1 año
Destinos
NAS.
Servidor de backup.
Cloud.
Ubicación externa.
### 4.18. Herramientas de backup

#### rsync

rsync permite sincronizar archivos y directorios.

Ejemplo:

rsync -av /datos/ /backup/datos/

Puede utilizarse para realizar sincronizaciones locales o remotas.

#### Clonezilla

Clonezilla permite trabajar con imágenes y clonaciones de discos y particiones.

Puede utilizarse para:

Clonar equipos.
Crear imágenes.
Restaurar sistemas.
Preparar despliegues.
#### Duplicati

Duplicati permite crear copias programadas y puede utilizar diferentes destinos de almacenamiento.

Entre sus características se encuentran:

Programación.
Versionado.
Cifrado.
Destinos locales y remotos.
## 5. Borrado seguro y ciclo de vida

### 5.1. Borrado seguro de información

Eliminar un archivo o formatear rápidamente una unidad no garantiza que los datos no puedan recuperarse. El método adecuado depende del medio, del nivel de confidencialidad y de la reutilización prevista. En HDD, la sobrescritura gestionada correctamente puede ser eficaz porque los sectores pueden escribirse de forma directa. En SSD, el *wear leveling* y el espacio reservado por el controlador impiden asegurar la sobrescritura de una ubicación concreta; se recomiendan los comandos de saneamiento del fabricante, como **ATA Secure Erase**, o el borrado criptográfico mediante destrucción de claves cuando la unidad se cifró desde el inicio.

La guía [NIST SP 800-88](https://csrc.nist.gov/pubs/sp/800/88/r1/final) diferencia tres niveles: **clear**, que elimina los datos de modo que no sean recuperables con técnicas habituales; **purge**, que aplica un saneamiento más profundo; y **destroy**, que inutiliza físicamente el soporte. La organización debe definir qué método emplea, quién lo autoriza y qué evidencia conserva. Por ejemplo, antes de reciclar un portátil que contenía información personal, se puede verificar que estaba cifrado, eliminar de forma segura sus claves, restablecerlo y registrar el número de serie, el responsable y el resultado del proceso.

En servicios cloud, el cliente no controla directamente el hardware y debe revisar las condiciones de eliminación, retención y copias del proveedor. El cifrado, una política de retención definida, contratos adecuados y el registro de las operaciones ayudan a cumplir las obligaciones de protección de datos. El borrado seguro también se aplica a dispositivos móviles: se deben eliminar las cuentas vinculadas, comprobar la sincronización en la nube y utilizar el restablecimiento de fábrica con el cifrado habilitado.

## 6. Resumen

En esta unidad hemos estudiado cómo proteger la información frente a fallos y pérdidas.

Los conceptos fundamentales son:

- Seguridad pasiva y protección física.
- Almacenamiento en HDD, SSD y NVMe.
- Redundancia y RAID.
- Backup, NAS, snapshots y recuperación.
- RPO, RTO y pruebas de restauración.
- Borrado seguro y ciclo de vida del soporte.

Los niveles RAID permiten mejorar la disponibilidad o el rendimiento, pero no sustituyen a las copias de seguridad.

Una estrategia profesional debe combinar diferentes mecanismos:

        INFORMACIÓN
             │
     ┌───────┴────────┐
     │                │
 Redundancia         Backup
     │                │
    RAID        3-2-1 / externo
     │                │
     └───────┬────────┘
             │
        RECUPERACIÓN

La idea fundamental de esta unidad es:

No debemos preguntarnos solamente cómo evitar que los datos se pierdan, sino también cómo recuperarlos cuando el fallo inevitablemente se produzca.

## 7. Recursos

- TrueNAS.
- Clonezilla.
- Duplicati.
- rsync.
- BorgBackup.
- Restic.
- [NIST SP 800-88: Guidelines for Media Sanitization](https://csrc.nist.gov/pubs/sp/800/88/r1/final)
- [INCIBE: borrado seguro de información](https://www.incibe.es/sites/default/files/contenidos/guias/doc/guia_ciberseguridad_borrado_seguro_metad_0.pdf)
- [Guía de seguridad en centros de datos de Google](https://www.google.com/about/datacenters/data-security/)

## 8. Relación con los resultados de aprendizaje

Esta unidad contribuye principalmente a:

### 8.1. RA1

Adopta prácticas seguras de utilización y trabajo con sistemas informáticos, reconociendo las vulnerabilidades y las necesidades de aseguramiento de los sistemas.

Especialmente mediante:

- Protección de la información y seguridad pasiva.
- Copias de seguridad y recuperación.

### 8.2. RA6

Implementa soluciones de alta disponibilidad mediante técnicas de virtualización y sistemas de almacenamiento redundante.

Especialmente mediante:

- RAID, redundancia y almacenamiento.
- NAS y recuperación.
- RPO, RTO y continuidad del servicio.