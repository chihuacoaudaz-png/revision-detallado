# 🧠 Prompt Inicial para el Agente en Casa (Copiar y Pegar)

```markdown
Hola Antigravity / Asistente AI:

Estoy trabajando en el proyecto de Business Intelligence y Analítica de Perforación de Rockdrill Group en este repositorio (`Detallados`).

Por favor, lee de inmediato los siguientes archivos clave de arquitectura y parámetros antes de realizar cualquier acción:
1. `PARAMETROS_EJECUCION_CASA.txt` (Instrucciones y comandos oficiales de ejecución)
2. `docs/00_MASTER_INDEX.md` (Índice maestro de la documentación)
3. `docs/06_REGLA_DE_NEGOCIO_CONCILIACION_Y_AUDITORIA_SENTIDO_COMUN.md` (Axioma de conciliación 1-a-1)
4. `docs/07_RESUMEN_EJECUTIVO_Y_DECISIONES_ARQUITECTURA.md` (Bitácora de decisiones y contexto completo)

REGLAS FUNDAMENTALES QUE DEBES RESPETAR SIEMPRE:
- El foco exclusivo del negocio es HORAS Y METROS (no perforistas ni tablas accesorias para las consultas principales).
- Los metrajes deben coincidir al 100% para el MISMO DÍA, MISMA MÁQUINA y MISMO TURNO (ID_CLAVE_UNICA = YYYYMMDD-MAQUINA-TURNO) entre el Detallado y Control Interno.
- Toda diferencia real (ej. los 35m faltantes de Americana XRD50USS-001) se aísla en el reporte de anomalías, nunca se auto-repara.
- La arquitectura está separada en 2 Bloques:
  * Bloque 1 (Python): `ejecutar_pipeline.py --export-star-schema` y `src/auditor_sentido_comun.py`
  * Bloque 2 (Power Query M en Excel): `output/CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx` con parámetros y consultas M nativas.

Por favor, confirma que has leído la documentación y ejecuta el pipeline de verificación para validar el estado del proyecto.
```
