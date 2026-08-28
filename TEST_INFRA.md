# E2E Test Infra: Rockdrill Group Detailed Reporting Pipeline

## Test Philosophy
- Opaque-box, requirement-driven testing. Derived strictly from `ORIGINAL_REQUEST.md` (R1 to R5 and Acceptance Criteria).
- Methodology: Category-Partition + Boundary Value Analysis (BVA) + Pairwise Combinatorial Testing + Real-World Workload Testing.
- No dependence on internal implementation shortcuts; exercises CLI entry points and output contracts directly.

---

## Feature Inventory Mapping
| # | Feature | Source (Requirement) | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---------|---------------------|:------:|:------:|:------:|:------:|
| 1 | OWA Automated Download (F1-F3) | R1 | ≥5 | ≥5 | ✓ | ✓ |
| 2 | Detailed 135-Col Schema Extraction (F4) | R2 | ≥5 | ≥5 | ✓ | ✓ |
| 3 | Smart Shift Assignment (A/B) (F5) | R2 | ≥5 | ≥5 | ✓ | ✓ |
| 4 | SAP Machine Normalization (F6) | R2 | ≥5 | ≥5 | ✓ | ✓ |
| 5 | Control Interno Multi-Sheet Compilation (F7) | R3 | ≥5 | ≥5 | ✓ | ✓ |
| 6 | Turn-by-Turn Composite Key Reconciliation (F8) | R4 | ≥5 | ≥5 | ✓ | ✓ |
| 7 | Discrepancy Cause Categorization (F9) | R4 | ≥5 | ≥5 | ✓ | ✓ |
| 8 | Executive Editorial PDF Generation (F12) | R5 | ≥5 | ≥5 | ✓ | ✓ |
| 9 | Pipeline Performance & Portability (F10, F13) | Acceptance Criteria | ≥5 | ≥5 | ✓ | ✓ |

---

## Test Architecture
- **Test Runner**: `tests/test_e2e_runner.py` (executable via `python tests/test_e2e_runner.py` or `pytest tests/`).
- **Pass/Fail Semantics**: Exit code 0 if all tests pass; non-zero if any test fails. Output prints clear tabular summary of Tiers 1-4 results.
- **Coverage Tiers**:
  - **Tier 1 (Feature Coverage)**: Validates each feature in isolation against baseline inputs (18 CTR discovery, column schema length 135, shift A/B validity, machine name lookups, Control Interno row parsing, reconciliation join logic, PDF report creation).
  - **Tier 2 (Boundary & Corner Cases)**: Empty sheets, 1M blank rows, date rollovers, multi-drill days (4 rows/day in Catalina Huanca / Condestable), missing contract emails (Americana), zero metraje records (Yauliyacu), sub-centimeter rounding (San Cristóbal), and ZIP attachment extraction.
  - **Tier 3 (Cross-Feature Combinations)**: Full pipeline integration across multiple CTRs with mixed shift patterns, SAP exceptions, and date cutoffs.
  - **Tier 4 (Real-World Workloads)**: End-to-end operational runs on production dataset (July & August 2026 data), verifying $\ge 96\%$ key match, 100% squareness on available contracts, and total execution time $< 45$ seconds.

---

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Target Metric |
|---|----------|--------------------|---------------|
| 1 | Full August Operational Pipeline Run | F4, F5, F6, F7, F8, F9, F10, F13 | Complete $<45$s, $\ge 95.8\%$ key match |
| 2 | Complete July Operational Pipeline Run | F4, F5, F6, F7, F8, F9, F10, F13 | Complete $<45$s, $\ge 99.4\%$ key match |
| 3 | Contract Squareness Audit | F4, F6, F7, F8 | 100% squareness (0.00m diff) on all 12 available contracts |
| 4 | Discrepancy Taxonomy Classification Audit | F8, F9 | 100% of $|DIF| > 0.01$ tagged with valid operational cause |
| 5 | End-to-End PDF Report Generation | F12, F13 | Generates valid 6-page PDF with 156 cols in $<1$s |
