@echo off
title Rockdrill Group - Subir Detallados a GitHub
color 0A
set PATH=C:\Proyectos Python\Detallados\tools\git\cmd;%PATH%
cd /d "C:\Proyectos Python\Detallados"

echo ================================================================================
echo   ROCKDRILL GROUP - SUBIR PROYECTO DETALLADOS A GITHUB
echo ================================================================================
echo.
echo Repositorio: https://github.com/chihuacoaudaz-png/revision-detallado.git
echo Rama:        main
echo.
echo Subiendo commits y archivos...
echo.

git push origin main

echo.
echo ================================================================================
if %ERRORLEVEL% EQU 0 (
    echo   [EXITO] Repositorio subido correctamente a GitHub.
) else (
    echo   [AVISO] Si te pide autenticacion, ingresa tu cuenta de GitHub o tu Token.
)
echo ================================================================================
echo.
pause
