# Handoff Report — Survey Spec Miner 2
**Project:** Rockdrill Group Detailed Reporting Pipeline
**Agent:** `survey_specminer_2`
**Date:** 2026-08-19
**Status:** Task Complete (Hard Handoff)

---

## 1. Observation

Direct observations extracted from the authoritative codebase, documentation, and live execution:

1. **Contract Enumeration & Operational Scope**:
   - In `Estructura base/Rockdrill_Control_Operaciones`, exactly 18 CTR folders exist: `CTR_AMERICANA`, `CTR_ANDAYCHAGUA`, `CTR_CATALINA_HUANCA`, `CTR_CERRO`, `CTR_CHUNGAR`, `CTR_COBRIZA`, `CTR_COLQUISIRI`, `CTR_CONDESTABLE`, `CTR_CUCULI`, `CTR_INMACULADA`, `CTR_LA_ESTRELLA`, `CTR_MOROCOCHA`, `CTR_RAURA`, `CTR_SAN_CRISTOBAL`, `CTR_TAMBOJASA`, `CTR_TICLIO`, `CTR_YAULIYACU`, `CTR_YAURICOCHA` (`HANDOFF_KNOWLEDGE_BASE_OBSIDIAN.md:45-58`).
   - One excluded surface drilling contract is documented and configured: `CTRS_EXCLUIDOS = {"COLQUIJIRCA"}` (`config.py:47`).
   - Nominal shift hours vary by project: `CATALINA HUANCA` operates at 10.15 hrs/turno; `YAULIYACU` at 11.00 hrs/turno; all other 16 CTRs operate at standard 12.00 hrs/turno (`HANDOFF_KNOWLEDGE_BASE_OBSIDIAN.md:191-196`).

2. **Schema Definitions (135 vs 156 Columns)**:
   - The production schema contains exactly **135 columns** (`COLS_OFICIALES` in `src/etl_detallados.py:40-85`): 129 native form columns + 6 metadata columns appended at the end (`HOJA DE TRABAJO ORIGEN`, `ARCHIVO ORIGEN`, `TURNO_ESTANDAR`, `ID_CLAVE_UNICA`, `SONDAJE_PARALELO`, `Alerta_Comentarios`). Data types consist of 2 `int64`, 1 ISO date `str`, 88 `float64` (rounded to 2 decimals), and 44 `str`/text columns (`docs/02_diccionario_de_datos_135_columnas.md:27-35`).
   - The master standardization proposal contains **156 columns** organized into 13 functional blocks (`docs/10_propuesta_estandarizacion_detallado_f01.md:54-295`), designed for dynamic column hiding per CTR without breaking positional indexing.

3. **Shift Assignment Logic**:
   - `assign_daily_turnos_fast` in `src/etl_detallados.py:184-241` and `assign_daily_turnos_grid_smart` in `docs/03_algoritmo_turnos_y_casos_borde.md:49-105` implement hierarchical shift assignment on the raw daily grid:
     - 1-row days: `B/N/2 -> B`, else `A`.
     - 2-row days: `['B', 'A']` if row 0 is night, else `['A', 'B']`.
     - 3+ row days: Priority 1 = driller transition (`PERFORISTA`), Priority 2 = explicit shift codes (`TURNO / GRUPO`), Priority 3 = group change (`G1` vs `G2`), Priority 4 = 50/50 fallback split.

4. **Machine Normalization & SAP Exceptions**:
   - `Maestros_Maquinas.xlsx` contains 56 official SAP machines in sheet `NOMBRES_SAP` and 22 exception mapping entries in sheet `Exepciones`.
   - `KNOWN_FALLBACK_EXCEPTIONS` in `src/utils.py:89-107` encodes fallbacks for key aliases, including:
     - `ANDAYCHAGUA`: `XRD90U-017 -> XRD150U-001`, `LF90DST-002 -> LF90D ST-002`
     - `CATALINA HUANCA`: `XRD50-003 -> XRD50U-003`, `XRD100U-01 -> XRD100U-001`
     - `CHUNGAR`: `XRD90U-003 -> XRD90U-021`
     - `COBRIZA`: `XRD90U-008 -> XRD150U-008`
     - `INMACULADA`: `XRD150-004 -> XRD150USS-004`, `XRD250-001 -> XRD250U-001`, `XRD80U-008 -> XRD80USS-008`, `XRD90U-012 (XRD150) -> XRD90U-012`
     - `MOROCOCHA`: `XRD150USS -> XRD150USS-002`, `XRD90USS-002 -> XRD90USS-005`
     - `TAMBOJASA`: `DE710ST-002 -> DE710T-002`
     - `TICLIO`: `XRD150USS-001 / XRD150USS-007 -> XRD150U-007`
     - `YAULIYACU`: `XRD50USS-001 / XRD50USS-00T -> XDR50USS-00T`

5. **Live Pipeline Execution Results**:
   - Execution command `venv\Scripts\python.exe ejecutar_pipeline.py` processed 18 CTRs, 56 machines, 2,951 detailed records, and 2,736 Control Interno records in **41.92 seconds** (under the 45.0-second performance requirement in `ORIGINAL_REQUEST.md:47`).
   - Evaluated 2,644 unique keys (`ID_CLAVE_UNICA = {YYYYMMDD}-{MAQUINA}-{TURNO}`) with **95.84% exact matching** (2,534 keys with 0.00m difference).

---

## 2. Logic Chain

1. **From Ingestion to Operational Consistency**:
   - Strict date search query `"{CTR} received:{fecha}"` eliminates false matches from previous dates (e.g. Andaychagua 14/08 vs 17/08). Multi-modal download handles direct files, ZIP archives, dropdown menus, and viewer preview buttons.
2. **From Raw Dual-Row Headers to Canonical Typing**:
   - Row 23 (Category) and Row 24 (Activity/Unit) combined with horizontal forward-fill (`ffill`) produce unique, predictable column names across all 18 CTRs.
   - Slicing to 200 rows per sheet bypasses corrupted 1M-row empty sheets in Rust Calamine, cutting runtime from >15 minutes in Power Query to <42 seconds in Python.
3. **From Shift Ambiguities to Deterministic Keys**:
   - Applying `assign_daily_turnos_fast` on the raw daily grid before dropping standby rows ensures night-only shifts retain Shift B identity, resolving multi-drill days in Catalina Huanca (4 rows on 29.06) and Condestable (01.07, 05.07).
4. **From Discrepancy Diagnostics to Operational Traceability**:
   - Cruces via `ID_CLAVE_UNICA` isolate all differences into verified operational categories:
     - Unbilled parallel drilling in Yauliyacu (`XRD125USS-001`: +125.40m over 11 keys in July).
     - 1-day cut date shifts in Chungar (`LM110U-001`: $\pm 1.50$m) and Ticlio (`XRD150U-007`: $\pm 1.30$m).
     - Supervisor shift split reallocations in Chungar (`XRD90U-021`: 29.80m daily total exact).
     - Cumulative depth fractional rounding in San Cristóbal (`XRD90U-023`: 0.04m).

---

## 3. Caveats

- **OWA Session Authentication**: In headless mode or CI/CD without active Edge SSO profiles, `descargar_detallados.py` requires initial interactive `--setup` to populate `.sesiones/`.
- **Open-Pit vs Underground Scope**: Surface operations (`COLQUIJIRCA`) remain excluded from the underground detailed reporting pipeline as mandated by business rules.
- **No further caveats**: All 18 CTRs, machine catalogs, schemas, and shift logic have been validated against live data files.

---

## 4. Conclusion

The specification mining mission is complete. The exact domain specifications for all 18 mining contracts, the 135-column production schema, the 156-column master proposal schema, the shift assignment hierarchy, the SAP machine normalization matrix, and all 12 operational edge cases are fully cataloged and documented in `analysis.md`.

---

## 5. Verification Method

To independently verify these domain specifications and execution metrics:

1. **Verify Full Pipeline Execution & Runtime (<45s)**:
   ```powershell
   cd "C:\Proyectos Python\Detallados"
   venv\Scripts\python.exe ejecutar_pipeline.py
   ```
   *Expected result:* Exit code 0, runtime $< 45$ seconds, 18 CTRs processed, $>95.8\%$ exact key matching.

2. **Verify Canonical 135-Column Output Schema**:
   ```powershell
   venv\Scripts\python.exe -c "import pandas as pd; df = pd.read_csv('output/detallados_consolidados.csv'); assert len(df.columns) == 135; print(f'Validated {len(df.columns)} columns across {len(df)} rows.')"
   ```

3. **Verify Machine Normalization & Visible Sheets**:
   ```powershell
   venv\Scripts\python.exe -c "from src.utils import load_machine_exceptions; from config import MAESTRO_PATH; ex = load_machine_exceptions(MAESTRO_PATH); assert len(ex) >= 17; print(f'Loaded {len(ex)} machine exceptions.')"
   ```

4. **Inspect Artifacts**:
   - Detailed analysis: `C:\Proyectos Python\Detallados\.agents\survey_specminer_2\analysis.md`
   - Generated reports: `C:\Proyectos Python\Detallados\output\detallados_consolidados.xlsx`, `C:\Proyectos Python\Detallados\output\matriz_comparativa_metrajes.xlsx`
