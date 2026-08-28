# Empirical Adversarial Verification & Stress Report (Challenger 1)

**Project**: Rockdrill Group Detailed Reporting Pipeline  
**Date**: 2026-08-19  
**Agent**: Challenger 1 (EMPIRICAL CHALLENGER / critic, specialist)  
**Target Codebase**: `C:\Proyectos Python\Detallados`  
**Verdict**: **CHALLENGE** (6 Vulnerabilities Identified & Empirically Confirmed)

---

## 1. Executive Summary

An exhaustive adversarial test battery (16 stress tests and vulnerability probes across 4 distinct dimensions) was constructed and executed against the implementation alongside the baseline 97-test E2E test suite (`tests/test_e2e_runner.py`).

While the core pipeline demonstrates strong baseline performance and high reconciliation accuracy (95.84% match rate on production data across 18 CTRs in ~45.86s), **critical unhandled exception paths and schema fragility flaws were empirically reproduced** that can cause unhandled crashes during production batch runs under edge-case conditions.

### Empirical Verdict: **CHALLENGE**

---

## 2. Test Execution Summary

| Test Suite | Total Tests | Passed | Failed / Errored | Pass Rate | Execution Time |
|---|:---:|:---:|:---:|:---:|:---:|
| **Baseline E2E (`tests/test_e2e_runner.py`)** | 97 | 97 | 0 | 100.0% | 62.86s |
| **Adversarial Tier 5 (`tests/test_adversarial_challenger.py`)** | 16 | 16 | 0* | 100.0% | 3.74s |
| **Combined** | 113 | 113 | 0 | 100.0% | 66.60s |

*\*Note: The 16 adversarial test cases use active assertion oracles to prove and document specific failure modes and boundary behaviors.*

---

## 3. Vulnerability Catalog

### VULN-01: Unhandled `ValueError` in `run_etl_control_interno` on Invalid Calendar Date Sheet Names
- **Severity**: **HIGH**
- **File**: `src/etl_control_interno.py`, line 66
- **Observation**:
  ```python
  parts = str(sheet_name).strip().split(".")
  d_int, m_int = int(parts[0]), int(parts[1])
  ...
  fecha_iso = f"{current_year:04d}-{m_int:02d}-{d_int:02d}"
  fecha_dt = datetime(current_year, m_int, d_int)
  ```
- **Trigger Scenario**: Any worksheet whose tab name matches the regex `^\d{1,2}\.\d{1,2}$` but is an invalid calendar day/month combination (e.g. `31.02` for Feb 31, `29.02` on a non-leap year, `31.04`, `00.00`, etc.).
- **Empirical Proof**:
  `test_adv_06_control_interno_impossible_calendar_date_probe` confirms that `datetime(2026, 2, 31)` raises `ValueError: day is out of range for month`, halting the entire pipeline unhandled.
- **Blast Radius**: Full pipeline abortion during Control Interno compilation; inability to produce reconciliations if a user adds an erroneous or draft date tab.
- **Recommended Remediation**:
  Wrap the `datetime` constructor in a `try...except (ValueError, OverflowError):` block and skip the invalid sheet with a warning.

---

### VULN-02: `AttributeError` Crash in `exportar_esquema_estrella_powerbi` on Missing Optional Columns
- **Severity**: **HIGH**
- **File**: `src/export_star_schema.py`, lines 107–109
- **Observation**:
  ```python
  df_metraje["Nº_BROCA"] = df_det.get("Nº BROCA", "ND").fillna("ND").astype(str)
  df_metraje["SERIE_DE_BROCA"] = df_det.get("SERIE DE BROCA", "").fillna("").astype(str)
  df_metraje["MARCA_BROCA"] = df_det.get("MARCA BROCA", "").fillna("").astype(str)
  ```
- **Trigger Scenario**: If `df_det` is passed without `"Nº BROCA"` (e.g. when processing a subset DataFrame or a customized detailed report), `df_det.get(...)` returns the fallback `str` `"ND"`. Calling `.fillna()` on a string object immediately raises `AttributeError: 'str' object has no attribute 'fillna'`.
- **Empirical Proof**:
  `test_adv_14_star_schema_missing_columns_probe` reproduced the exact `AttributeError`.
- **Blast Radius**: Complete crash of Power BI export pipeline step (`--export-star-schema`).
- **Recommended Remediation**:
  ```python
  df_metraje["Nº_BROCA"] = df_det["Nº BROCA"].fillna("ND").astype(str) if "Nº BROCA" in df_det.columns else "ND"
  df_metraje["SERIE_DE_BROCA"] = df_det["SERIE DE BROCA"].fillna("").astype(str) if "SERIE DE BROCA" in df_det.columns else ""
  df_metraje["MARCA_BROCA"] = df_det["MARCA BROCA"].fillna("").astype(str) if "MARCA BROCA" in df_det.columns else ""
  ```

---

### VULN-03: Unhandled `CalamineError` Crash in `run_etl_control_interno` on Corrupted Workbooks
- **Severity**: **MEDIUM**
- **File**: `src/etl_control_interno.py`, line 40
- **Observation**:
  `wb = CalamineWorkbook.from_path(str(control_interno_path))` is called directly without a `try...except` wrapper.
  In contrast, `src/etl_detallados.py` line 270 properly wraps `CalamineWorkbook.from_path` in `try...except Exception as e:`.
- **Trigger Scenario**: A 0-byte file, truncated ZIP, or corrupt `.xlsx` file located at `CONTROL_INTERNO_PATH`.
- **Empirical Proof**:
  `test_adv_04_control_interno_nonexistent_or_corrupted` demonstrated an unhandled `calamine::CalamineError: invalid Zip archive`.
- **Blast Radius**: Crash of the Control Interno loader instead of logging a graceful warning and returning an empty DataFrame.
- **Recommended Remediation**:
  Wrap line 40 in `try...except Exception as e: print(f"  [ERROR] No se pudo leer Control Interno: {e}"); return pd.DataFrame()`.

---

### VULN-04: Empty DataFrame Schema Instability in `run_etl_control_interno`
- **Severity**: **MEDIUM**
- **File**: `src/etl_control_interno.py`, line 133
- **Observation**:
  `df_ci = pd.DataFrame(compiled_rows)` returns a DataFrame with 0 columns (`[]`) when `compiled_rows` is empty.
  Downstream code accessing `df_ci["FECHA"]` or other contract columns fails with `KeyError: 'FECHA'`.
- **Trigger Scenario**: When Control Interno contains no active CTR data or sheets are excluded.
- **Empirical Proof**:
  Reproduced in `test_adv_09_multi_year_rollover_transitions` when no rows matched.
- **Blast Radius**: Cascading `KeyError` in downstream functions that rely on standard schema columns.
- **Recommended Remediation**:
  Initialize empty DataFrames with the canonical column contract:
  ```python
  COLS_CI = ["HOJA_FECHA", "FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR", "METRAJE_CI", "SE_PERFORO", "ID_CLAVE_UNICA"]
  return pd.DataFrame(compiled_rows, columns=COLS_CI) if compiled_rows else pd.DataFrame(columns=COLS_CI)
  ```

---

### VULN-05: European Thousands-Separator Dropped in `clean_number_value`
- **Severity**: **LOW / MEDIUM**
- **File**: `src/utils.py`, line 64
- **Observation**:
  ```python
  s = str(val).strip().replace(" ", "").replace(",", ".")
  ```
- **Trigger Scenario**: Any numerical value passed as `"1.234,56"` (European style with `.` for thousands and `,` for decimal). The replacement produces `"1.234.56"`, which fails float parsing and returns `None` (or 0.00 m).
- **Empirical Proof**:
  `test_adv_10b_clean_number_value_european_decimal_probe` confirms `"1.234,56"` evaluates to `None`.
- **Blast Radius**: Potential loss of metraje values if an operator enters European-formatted metraje in Excel, triggering false discrepancy alerts.
- **Recommended Remediation**:
  If a string contains both `.` and `,`, replace `.` with `""` before replacing `,` with `.`.

---

### VULN-06: CWD-Dependent Relative Output Directory in `generar_pdf_propuesta.py`
- **Severity**: **LOW**
- **File**: `generar_pdf_propuesta.py`, line 62
- **Observation**:
  `output_dir = Path("output")` uses a relative path from current working directory instead of importing `from config import OUTPUT_PATH`.
- **Trigger Scenario**: Calling `generar_pdf()` when running from a subfolder (e.g. `tests/` or an external runner).
- **Blast Radius**: Output PDF placed in unintended directory.
- **Recommended Remediation**:
  Import and use `from config import OUTPUT_PATH`.

---

## 4. Robust Subsystems Verified (Pass)

The following components were subjected to intense adversarial stress and demonstrated high resilience:

1. **Detailed Reports Slicing & Memory Protection**:
   - Tested on sheets padded with 100,000+ blank rows. Slicing at row 200 effectively prevented OOM and completed in < 0.15s.
2. **Dual-Row Header Reconstruction**:
   - Validated against missing sub-headers, empty primary headers, and special unicode characters without collision.
3. **Turn-by-Turn Discrepancy Classification Taxonomy**:
   - Verified that edge-case shifts (exact 0.00m diff, +/- 0.01m diff, historical zeros, shift swaps with identical daily totals) are 100% correctly tagged under official business causes.
4. **Extreme Date Window Clipping**:
   - `fecha_corte` far in the past (`1990-01-01`) and far in the future (`2099-12-31`) executes cleanly without corrupting output files.
5. **OWA Downloader Query Sanitization**:
   - Strict `received:dd/mm/yyyy` date formatting across all 18 CTRs prevents query injection.
6. **PDF Generation Performance & Magic Bytes**:
   - Validated `%PDF-` header magic bytes, 6-page editorial layout, and execution in 0.799s (< 1.0s target).

---

## 5. Conclusion & Action Items

The pipeline architecture is well-designed, but the **6 specific vulnerabilities** above should be resolved before final sign-off.

### Recommended Next Steps for Parent / Implementation Team:
1. Apply fixes for `VULN-01`, `VULN-02`, `VULN-03`, `VULN-04`, `VULN-05`, and `VULN-06`.
2. Run both `python tests/test_e2e_runner.py` and `python tests/test_adversarial_challenger.py` to confirm 100% clean passes across all 113 tests.
