---
title: "Cómo se corrigen las integradoras"
weight: 6
bookToc: true
---

# Cómo se corrigen las prácticas integradoras

Las [prácticas integradoras](/guia/practicas-integradoras/) están diseñadas para corregirse en **unos cinco minutos por persona**, de forma transparente: el alumnado ve exactamente las mismas comprobaciones que aplica el profesorado.

## Qué se corrige

| Parte | Puntos | Cómo |
|---|--:|---|
| 16 comprobaciones automáticas | 8,0 | El *script* de verificación escribe `[OK]` o `[FALLA]` en cada una; cada `[OK]` vale 0,5 |
| 4 preguntas cortas (`respuestas.md`) | 2,0 | Cada una vale 0,5: completa, 0,5; parcial, 0,25; ausente o incorrecta, 0 |

## Procedimiento (5 minutos)

1. **Comprueba la firma** del fichero de evidencias. Si no coincide, el fichero se ha editado a mano y se repite la verificación en directo:

   ```bash
   # Calcula el hash del cuerpo (todas las líneas menos la última) y compáralo con la línea FIRMA
   head -n -1 evidencias-INT1-GARCIA.txt | sha256sum
   tail -n 1 evidencias-INT1-GARCIA.txt
   ```

2. **Lee la puntuación** (`PUNTOS_AUTO: 14/16`) y repasa las líneas `[FALLA]`: cada una indica qué comprobación no se cumplió y una pista.
3. **Corrige las cuatro preguntas** con los criterios de abajo.
4. **Anota la nota:** `puntos automáticos + puntos de las preguntas` sobre 10.

### Corregir una clase entera de golpe

Con todos los ficheros en una carpeta, esta orden resume la puntuación automática y la validez de la firma de cada persona (alumno, puntos y firma):

```bash
for f in evidencias-INT1-*.txt; do
  a=$(grep -m1 '^ALUMNO:' "$f" | awk '{print $2}')
  p=$(grep -m1 '^PUNTOS_AUTO:' "$f" | sed -E 's/^PUNTOS_AUTO: ([0-9]+)\/.*/\1/')
  if [ "$(head -n -1 "$f" | sha256sum | cut -d' ' -f1)" = "$(tail -n 1 "$f" | awk '{print $2}')" ]; then s=FIRMA_OK; else s=FIRMA_ROTA; fi
  echo "$a,$p,$s"
done
```

Para detectar copias, busca identificadores de máquina repetidos entre personas distintas: `grep -h '^ID-VM' evidencias-*.txt | sort | uniq -d`.

## Criterios de las preguntas cortas

Se valora que la respuesta sea **coherente con el sistema entregado** y use bien los conceptos, no que repita palabras exactas.

| Pregunta | Qué debe mostrar |
|---|---|
| INT-1 · P1 (UD01) | Identifica correctamente el riesgo más alto **de su propia matriz**, propone una salvaguarda adecuada y nombra bien el tipo de tratamiento |
| INT-1 · P2 (UD02) | Relaciona la frecuencia de copia con el **RPO** y el tiempo de restauración medido con el **RTO**, y concluye si se cumplen |
| INT-1 · P3 (UD03) | Entiende que el equipo debe **confiar en la CA** y que desactivar la comprobación anula la protección del certificado |
| INT-1 · P4 (UD04) | Une una medida concreta, la **amenaza** que reduce y una **comprobación real** |
| INT-2 · P1 (UD05) | Describe lo que detecta su regla y distingue **detectar** (IDS) de **bloquear** (IPS) |
| INT-2 · P2 (UD06) | Explica la política restrictiva (todo lo no permitido se descarta) y nombra el flujo que abrió |
| INT-2 · P3 (UD07) | Da un RTO medido coherente con su CSV y señala un **punto único de fallo** real que persiste |
| INT-2 · P4 (UD05-UD07) | Propone un riesgo residual verosímil y una mejora concreta |

> [!NOTE]
> Si una comprobación automática falla por un motivo ajeno al trabajo (por ejemplo, una versión distinta de una orden), se revisa la causa en la propia salida o se repite en directo, y se puntúa a mano.
