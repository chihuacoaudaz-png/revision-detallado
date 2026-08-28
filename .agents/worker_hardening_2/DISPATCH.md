## 2026-08-19T16:58:35Z

You are the Hardening Worker for the Rockdrill Group Detailed Reporting Pipeline project.

Working Directory: C:\Proyectos Python\Detallados\.agents\worker_hardening_2
Workspace Directory: C:\Proyectos Python\Detallados
Original Request Path: C:\Proyectos Python\Detallados\.agents\ORIGINAL_REQUEST.md
Scope Document Path: C:\Proyectos Python\Detallados\PROJECT.md
Challenger 1 Report Path: C:\Proyectos Python\Detallados\.agents\challenger_1\handoff.md

Tasks:
Remediate the 6 edge-case vulnerabilities identified by Challenger 1:
1. VULN-01 & VULN-03 & VULN-04 in `src/etl_control_interno.py`:
   - Wrap `CalamineWorkbook.from_path` in `try...except Exception as e:` logging a warning and returning an empty DataFrame with proper schema columns if the file is missing or corrupted.
   - In the date parsing loop (`sheet_name`), wrap `datetime(current_year, m_int, d_int)` in `try...except (ValueError, OverflowError):` skipping invalid calendar date sheets (e.g. `31.02`).
   - If `compiled_rows` is empty, return `pd.DataFrame(columns=["FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR", "METRAJE_CI", "SE_PERFORO", "ID_CLAVE_UNICA"])`.
2. VULN-02 in `src/export_star_schema.py`:
   - Fix column extraction for `"Nº BROCA"` and other optional fields so it handles missing columns safely without calling `.fillna()` on default strings (e.g., `df_metraje["Nº_BROCA"] = df_det["Nº BROCA"].fillna("ND").astype(str) if "Nº BROCA" in df_det.columns else "ND"`).
3. VULN-05 in `src/utils.py` (`clean_number_value`):
   - Enhance `clean_number_value` to correctly handle both US/standard formats (`1,234.56`, `1234.56`) and European formats (`1.234,56`, `1234,56`).
4. VULN-06 in `generar_pdf_propuesta.py`:
   - Import `from config import OUTPUT_PATH` and use `OUTPUT_PATH` as the default directory instead of relative `Path("output")`.
5. Verification:
   - Run `python tests/test_e2e_runner.py` (all tests must pass).
   - Run `python tests/test_adversarial_challenger.py` (all adversarial tests must pass).
   - Run `python ejecutar_pipeline.py --fecha-corte 2026-08-17 --export-star-schema --generar-pdf` and ensure complete clean execution.
6. Write your handoff report to `C:\Proyectos Python\Detallados\.agents\worker_hardening_2\handoff.md`.
7. Send a message to parent upon completion.
