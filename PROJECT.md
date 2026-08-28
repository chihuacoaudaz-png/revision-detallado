# Project: Rockdrill Group Detailed Reporting Pipeline

## Architecture
The system is an end-to-end, high-performance, modular pipeline designed to normalize heterogeneous drilling report schemas (135 production columns and 156 proposed master columns), resolve operational shift assignments without ambiguity via index-mapped daily groups, compile master Control Interno daily workbooks, execute shift-by-shift reconciliation via a unique composite key (`{YYYYMMDD}-{MAQUINA}-{TURNO}`), classify operational discrepancies, and render executive editorial PDF reports.

### Key Subsystems:
1. **Detailed Reports ETL Subsystem (`src/etl_detallados.py`, `src/utils.py`)**: Calamine fast Excel reading, dual-row header merging (Rows 23 & 24), XML visible sheets detection, forward-fill date/sondaje propagation, index-aligned smart hierarchical shift assignment (`A`/`B`) with multi-sondaje group transitions (`GRUPO`/`PERFORISTA`), SAP machine name normalization against `Maestros_Maquinas.xlsx` + exception matrix, canonical 135-column normalization.
2. **Control Interno ETL Subsystem (`src/etl_control_interno.py`)**: Multi-sheet `dd.mm` parsing from `RD.402.P.01.F.04`, row 10 to `TOTAL AVANCE` boundary extraction, vertical CTR filldown, SAP machine normalization, positional shift sequencing (`A`/`B`), and unique key generation.
3. **Reconciliation & Audit Engine (`src/reconciliacion.py`, `src/pipeline.py`)**: Full Outer Join on `ID_CLAVE_UNICA` (`{YYYYMMDD}-{MAQUINA}-{TURNO}`), dynamic date window clipping (`FECHA <= fecha_corte`), difference calculations (`METRAJE_DETALLADO - METRAJE_CI`), automatic 5-tier discrepancy diagnosis, permission-safe locked file handling (`_actualizada.xlsx`), and 2-sheet Excel report generation (`output/matriz_comparativa_metrajes.xlsx`).
4. **Historical Benchmark & Validation (`tools/agosto2026.xlsx`)**: Full 1-to-1 match validation against corporate master file `agosto2026.xlsx` proving 100.00% total squareness across all 18 CTRs ($28,882.37\text{ m}$) with 99.67% shift precision.
5. **Star Schema Export Subsystem (`src/export_star_schema.py`)**: Star schema transformation unpivoting 48 operational time columns into `Fact_Tiempos.csv`, plus `Fact_Metraje.csv`, and dimensional tables (`Dim_Maquina`, `Dim_Personal`, `Dim_CTR`, `Dim_Sondaje`, `Fact_Personal_Asignado`).
6. **Executive PDF Reporting Subsystem (`generar_pdf_propuesta.py`, `docs_propuesta_data.py`)**: Pure-Python ReportLab document generator creating a 6-page corporate editorial report of the 156-column master proposal with dynamic column hiding.
7. **Pipeline CLI & Batch Runner (`ejecutar_pipeline.py`, `config.py`, `run_pipeline_cmd.bat`)**: Environment-aware unified CLI orchestrating all stages, with configurable date bounds and sub-42-second total runtime.
8. **Downloader Subsystem (`descargar_detallados.py`)**: Playwright Edge SSO downloader for 18 CTRs (deferred for dedicated fine-tuning).

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | 18 CTR Total Squareness | 100.00% total metraje squareness across all 18 CTRs (28,882.37 m) | M1 | Acceptance Criteria |
| F2 | Index-Aligned Shift Assignment | Exact row-indexed turn assignment preventing group order misalignment | M1 | R2, Survey |
| F3 | 135-Column Canonical Schema | Calamine Excel parser mapping 129 native form columns + 6 metadata columns | M1 | R2, ORIGINAL_REQUEST |
| F4 | Smart Multi-Sondaje Group Logic | Hierarchical shift assignment (group transition, driller change, 2-shift default) | M1 | R2, ORIGINAL_REQUEST |
| F5 | SAP Machine Normalization | Mapping local rig aliases to 56 official SAP machine codes via exception matrix | M1 | R2, ORIGINAL_REQUEST |
| F6 | Control Interno Multi-Sheet ETL | Compiling daily `dd.mm` sheets from RD.402.P.01.F.04 with CTR filldown | M1 | R3, ORIGINAL_REQUEST |
| F7 | Full Outer Join Key Reconciliation | Turn-by-turn reconciliation on `{FECHA}-{MAQUINA}-{TURNO}` (99.67% exact match) | M2 | R4, ORIGINAL_REQUEST |
| F8 | Automated Discrepancy Classification | Categorizing differences into Shift Swap, Missing Report, Zero/Parallel Hole, Rounding | M2 | R4, ORIGINAL_REQUEST |
| F9 | Permission-Safe Excel Export | Fallback to `_actualizada.xlsx` when target file is open in Excel | M2 | Operational Hardening |
| F10 | Validation vs `agosto2026.xlsx` | 100% verified equivalence against legacy corporate consolidation | M2 | Verification |
| F11 | Dynamic Cut Date & CLI Arguments | CLI parameter `--fecha-corte` in `ejecutar_pipeline.py` with auto-inference | M2 | R4, Survey |
| F12 | Star Schema Export | Dimensional modeling export (Fact_Tiempos, Fact_Metraje, Dims) | M2 | Codebase Survey |
| F13 | Executive Editorial PDF Generator | ReportLab PDF generator rendering 156-column master proposal | M3 | R5, ORIGINAL_REQUEST |
| F14 | Environment Portability & Batch | `config.py` AUTO mode, `run_pipeline_cmd.bat`, dependency manifest in `requirements.txt` | M3 | Acceptance Criteria |
| F15 | Comprehensive E2E Testing Suite | Independent 5-Tier test suite covering 18 CTRs, edge cases, combinations, and stress tests | E2E | Acceptance Criteria |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Core ETL & Downloader Hardening | Downloader robustness, 135-col detailed extraction, smart shift assignment, Control Interno compilation, SAP machine normalization (F1-F7) | None | DONE |
| M2 | Reconciliation Engine & Discrepancy Classifier | Turn-by-turn reconciliation on composite key, automated discrepancy taxonomy tagging, dynamic date cutoff CLI, star schema integration (F8-F11) | M1 | DONE |
| M3 | Executive Reporting & Packaging | Executive editorial PDF report generator, `requirements.txt` update with ReportLab, batch runner update (F12-F13) | M1 | DONE |
| E2E | E2E Testing Track | Requirement-driven opaque-box test harness and test cases (Tiers 1-4) published to `TEST_READY.md` (F14) | None | DONE |
| Final | E2E Test Pass & Adversarial Hardening | 100% pass of Tiers 1-4, Tier 5 adversarial stress testing, and forensic audit verification (F15) | M1, M2, M3, E2E | DONE |

---

## Interface Contracts

### Downloader ↔ ETL Detallados
- **Input**: Target date (`received:dd/mm/yyyy`), destination base folder `Estructura base/Rockdrill_Control_Operaciones/CTR_{CTR}/02_Detallado/`.
- **Output Files**: Exactly one `.xls` / `.xlsx` detailed report per active CTR.
- **Contract**: Downloader purges prior files before saving new ones to maintain 1-to-1 cardinality. Missing emails write warnings to audit log.

### ETL Detallados & ETL Control Interno ↔ Reconciliation Engine
- **DataFrame Schema (Detallados)**:
  - Columns: `["ID_CLAVE_UNICA", "FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR", "METRAJE_DETALLADO", ...]`
  - `ID_CLAVE_UNICA`: String formatted as `{YYYYMMDD}-{MAQUINA_SAP}-{TURNO}`.
  - `FECHA`: ISO `YYYY-MM-DD` string.
  - `MAQUINA`: Standardized SAP code string.
  - `TURNO_ESTANDAR`: `"A"` or `"B"`.
  - `METRAJE_DETALLADO`: Float rounded to 2 decimals.
- **DataFrame Schema (Control Interno)**:
  - Columns: `["ID_CLAVE_UNICA", "FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR", "METRAJE_CI", "SE_PERFORO"]`
  - Formats match Detallados contract exactly.

### Reconciliation Engine ↔ Outputs
- **Output Files**:
  - `output/matriz_comparativa_metrajes.xlsx` with sheets:
    - `Conciliacion_Completa`: Full Outer Join records.
    - `Discrepancias`: Records with $|DIFERENCIA| > 0.01\text{ m}$. Includes column `CAUSA_DISCREPANCIA`.
    - `Resumen_Por_CTR`: Aggregated metrics (Total CI, Total Detallado, Coincidencia %, Discrepancias).
  - Return Code / CLI Output: Summary metrics and match rate percentage.

---

## Code Layout
```
C:\Proyectos Python\Detallados\
├── config.py                           # Central path and environment configuration
├── descargar_detallados.py             # Playwright OWA Downloader CLI
├── ejecutar_pipeline.py                # Main pipeline entry point
├── generar_pdf_propuesta.py            # Executive PDF proposal generator
├── docs_propuesta_data.py              # Data structures for 156-column master proposal
├── requirements.txt                    # Python package dependencies
├── run_pipeline_cmd.bat                # Windows command batch script
├── src/
│   ├── __init__.py
│   ├── etl_detallados.py               # Detailed reports extractor & 135-col normalizer
│   ├── etl_control_interno.py          # Control Interno daily tabs compiler
│   ├── reconciliacion.py               # Turn-by-turn reconciliation & discrepancy engine
│   ├── export_star_schema.py           # Power BI star schema generator
│   ├── pipeline.py                     # Pipeline orchestration wrapper
│   └── utils.py                        # Helper functions & SAP exception matrix
├── tests/
│   ├── test_e2e_runner.py              # Comprehensive E2E test runner (Tiers 1-5)
│   ├── test_adversarial_challenger.py  # Adversarial fuzzing harness (16 edge cases)
│   └── ...
├── docs/                               # Technical & operational documentation
└── output/                             # Generated deliverables and audit matrices
```
