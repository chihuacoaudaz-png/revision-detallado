# Formal Handoff Report — Challenger 1 (Empirical Adversarial Verification)

**Author**: Challenger 1 (EMPIRICAL CHALLENGER / critic, specialist)  
**Date**: 2026-08-19  
**Target Project**: Rockdrill Group Detailed Reporting Pipeline  
**Type**: Hard Handoff  
**Verdict**: **CHALLENGE**

---

## 1. Observation

Direct empirical observations gathered during adversarial fuzzing and test execution:

1. **Baseline Test Suite Execution**:
   - Command: `& "C:\Proyectos Python\Detallados\venv\Scripts\python.exe" tests/test_e2e_runner.py`
   - Result: 97/97 tests passed in 62.86 seconds (Exit Code: 0).
   - Reconciliation Accuracy: 2,534 / 2,644 exact matches (95.84% match rate) up to cut date `2026-08-17`.

2. **Adversarial Test Suite Execution**:
   - Command: `& "C:\Proyectos Python\Detallados\venv\Scripts\python.exe" tests/test_adversarial_challenger.py`
   - Result: 16/16 adversarial test cases executed in 3.74 seconds.
   - Identified 6 specific edge-case vulnerabilities and exception paths.

3. **Verbatim Code & Error Observations**:
   - **Obs 1 (`src/etl_control_interno.py:66`)**:
     ```python
     parts = str(sheet_name).strip().split(".")
     d_int, m_int = int(parts[0]), int(parts[1])
     fecha_dt = datetime(current_year, m_int, d_int)
     ```
     *Verbatim Exception*: `ValueError: day is out of range for month` when sheet name is `31.02`.
   - **Obs 2 (`src/export_star_schema.py:107-109`)**:
     ```python
     df_metraje["Nº_BROCA"] = df_det.get("Nº BROCA", "ND").fillna("ND").astype(str)
     ```
     *Verbatim Exception*: `AttributeError: 'str' object has no attribute 'fillna'` when column `"Nº BROCA"` is not in `df_det`.
   - **Obs 3 (`src/etl_control_interno.py:40`)**:
     ```python
     wb = CalamineWorkbook.from_path(str(control_interno_path))
     ```
     *Verbatim Exception*: `calamine::CalamineError: invalid Zip archive: Could not find EOCD` on corrupt `.xlsx` files without `try...except`.
   - **Obs 4 (`src/etl_control_interno.py:133`)**:
     ```python
     df_ci = pd.DataFrame(compiled_rows)
     ```
     Returns empty columns `[]` when `compiled_rows` is empty, leading to `KeyError: 'FECHA'`.
   - **Obs 5 (`src/utils.py:64`)**:
     ```python
     s = str(val).strip().replace(" ", "").replace(",", ".")
     ```
     `clean_number_value("1.234,56")` yields `"1.234.56"` -> returns `None`.
   - **Obs 6 (`generar_pdf_propuesta.py:62`)**:
     ```python
     output_dir = Path("output")
     ```
     Uses relative path instead of `from config import OUTPUT_PATH`.

---

## 2. Logic Chain

1. **Premise 1**: A robust production ETL pipeline must handle unexpected, corrupted, or user-mutated workbooks without unhandled tracebacks or crashes.
2. **Step 1 (Control Interno Date Parsing)**: In `src/etl_control_interno.py:66`, worksheet tab names matching `\d{1,2}\.\d{1,2}` are directly passed to `datetime(current_year, m_int, d_int)`. If an operator leaves a sheet `31.02` or `29.02` in a non-leap year, Python raises `ValueError`. Because this is not caught in a try/except block, the entire pipeline crashes. *(References Obs 1)*.
3. **Step 2 (Star Schema Method Call on Default)**: In `src/export_star_schema.py:107`, `df_det.get("Nº BROCA", "ND")` returns a Python string `"ND"` when the column is absent. Calling `.fillna()` on a string triggers an `AttributeError`. *(References Obs 2)*.
4. **Step 3 (Corrupt File Handling Inconsistency)**: In `src/etl_detallados.py:270`, `CalamineWorkbook.from_path` is wrapped in `try...except Exception`, but in `src/etl_control_interno.py:40` it is called without protection. Corrupted CI workbooks crash the program instead of failing gracefully. *(References Obs 3)*.
5. **Step 4 (Empty Schema Invariants)**: When Control Interno is empty or filtered out, returning an un-columned DataFrame causes downstream consumers to raise `KeyError`. *(References Obs 4)*.
6. **Step 5 (European Format Truncation)**: Number parsing in `clean_number_value` mishandles strings with thousands-separators such as `"1.234,56"`, causing legitimate metraje values to become `None` (0.00m). *(References Obs 5)*.
7. **Step 6 (Portability)**: `generar_pdf_propuesta.py` relies on `Path("output")` relative to CWD instead of `config.OUTPUT_PATH`, causing files to be written outside the designated directory if invoked from a different CWD. *(References Obs 6)*.
8. **Conclusion**: While core business logic and performance are solid (97/97 E2E tests pass), the presence of these 6 unhandled exception points requires a **CHALLENGE** verdict to ensure production hardening.

---

## 3. Caveats

1. **OWA Live Network Testing**: Live network calls to Office 365 OWA with active credentials were not executed live due to headless CI security constraints; downloader resilience was verified via component unit tests, query builder validation, and mock attachment matching.
2. **Edge Session Persistence**: The persistent browser profile in `.sesiones/` depends on local Windows SSO session state.

---

## 4. Conclusion

- **Overall Verdict**: **CHALLENGE**
- **Summary**: The Rockdrill Detailed Reporting Pipeline successfully implements all core operational requirements (R1–R5) with high precision (95.84% match rate) and fast execution (<46s). However, 6 distinct exception handling and schema vulnerabilities have been empirically proven that must be patched to achieve Tier 5 production robustness.
- **Actionable Remediation**:
  1. Patch `src/etl_control_interno.py` with date validation and try/except around Calamine workbook loading.
  2. Patch `src/export_star_schema.py` column `.fillna()` calls.
  3. Patch `src/etl_control_interno.py` empty DataFrame schema definition.
  4. Patch `src/utils.py` European thousands parsing in `clean_number_value`.
  5. Patch `generar_pdf_propuesta.py` to import `OUTPUT_PATH`.

---

## 5. Verification Method

To independently reproduce and verify all findings:

1. **Run Baseline E2E Suite**:
   ```powershell
   & "C:\Proyectos Python\Detallados\venv\Scripts\python.exe" tests/test_e2e_runner.py
   ```
   *Expected*: 97 tests pass.

2. **Run Adversarial Challenger Suite**:
   ```powershell
   & "C:\Proyectos Python\Detallados\venv\Scripts\python.exe" tests/test_adversarial_challenger.py
   ```
   *Expected*: 16 adversarial tests pass, with exact assertions reproducing and validating the 6 vulnerability boundaries.

3. **Inspect Analysis Report**:
   - `C:\Proyectos Python\Detallados\.agents\challenger_1\analysis.md`
