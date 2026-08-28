@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ===============================================================================
echo 🚀 ROCKDRILL GROUP - PIPELINE INTEGRAL DE OPERACIONES Y CONCILIACIÓN
echo ===============================================================================

:: Cambiar al directorio del script
cd /d "%~dp0"

:: 1. Detección automática del ejecutable Python (Virtualenv o Sistema)
set "PYTHON_EXE="
if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
) else if defined VIRTUAL_ENV (
    if exist "%VIRTUAL_ENV%\Scripts\python.exe" (
        set "PYTHON_EXE=%VIRTUAL_ENV%\Scripts\python.exe"
    )
)

if not defined PYTHON_EXE (
    where python >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_EXE=python"
    ) else (
        echo ❌ ERROR: No se encontró Python ni el entorno virtual 'venv'.
        echo Por favor instale Python 3.10+ o configure el entorno venv.
        pause
        exit /b 1
    )
)

echo [INFO] Utilizando intérprete Python: !PYTHON_EXE!
echo.

:: 2. Ejecutar Pipeline Integral
echo [1/1] Ejecutando Pipeline ETL y Conciliación Turno a Turno...
"!PYTHON_EXE!" ejecutar_pipeline.py %*
if !ERRORLEVEL! NEQ 0 (
    echo.
    echo ❌ ERROR: Ocurrió un fallo durante la ejecución del pipeline (Código !ERRORLEVEL!).
    pause
    exit /b !ERRORLEVEL!
)

echo.
echo ===============================================================================
echo ✅ PROCESO COMPLETADO EXITOSAMENTE
echo Entregables generados en:
echo   - Matriz Comparativa: output\matriz_comparativa_metrajes.xlsx
echo   - Detallados:         output\detallados_consolidados.xlsx
echo   - Control Interno:    output\control_interno\control_interno_compilado.xlsx
echo ===============================================================================

