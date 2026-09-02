@echo off
setlocal enabledelayedexpansion
title ROCKDRILL GROUP - PIPELINE DE BASE DE DATOS DIMENSIONAL

echo ===============================================================================
echo   [ROCKDRILL GROUP] GENERADOR DE BASE DE DATOS DIMENSIONAL (KIMBALL)
echo ===============================================================================
echo   Este proceso transforma los reportes detallados diarios de operaciones
echo   en las 11 tablas del Esquema Estrella (7 Dimensiones y 4 Tablas de Hechos)
echo   generando formatos CSV, Parquet y el libro Excel maestro.
echo ===============================================================================
echo.

:: 1. Verificar si Python esta instalado en el sistema
python --version >nul 2>&1
if %errorlevel% neq 0 goto usar_exe

echo [1/2] Entorno Python detectado. Ejecutando pipeline dimensional...
echo.
python "%~dp0generar_base_datos_dimensional.py"
set ESTADO_EJECUCION=%errorlevel%
goto evaluar_resultado

:usar_exe
echo [INFO] Python no se detecto en el PATH de este equipo.
echo [INFO] Iniciando ejecutable independiente compilado (EJECUTAR_BBDD.exe)...
echo.
if exist "%~dp0EJECUTAR_BBDD\EJECUTAR_BBDD.exe" (
    "%~dp0EJECUTAR_BBDD\EJECUTAR_BBDD.exe"
    set ESTADO_EJECUCION=!errorlevel!
) else (
    echo [ERROR] No se encontro Python ni el ejecutable 'EJECUTAR_BBDD.exe'.
    echo Por favor verifique la instalacion.
    pause
    exit /b 1
)

:evaluar_resultado
echo.
if %ESTADO_EJECUCION% neq 0 (
    echo ===============================================================================
    echo   [ERROR] OCURRIO UN ERROR DURANTE LA EJECUCION DEL PIPELINE
    echo ===============================================================================
    echo   Revise los mensajes de error mostrados arriba o verifique las rutas
    echo   configuradas en 'generar_base_datos_dimensional.py'.
    echo ===============================================================================
) else (
    echo ===============================================================================
    echo   [OK] PROCESO COMPLETADO SATISFACTORIAMENTE
    echo ===============================================================================
    echo   Las tablas normalizadas han sido generadas en la carpeta:
    echo   %~dp0output_star_schema
    echo ===============================================================================
)

echo.
echo Presione cualquier tecla para salir...
pause > nul
