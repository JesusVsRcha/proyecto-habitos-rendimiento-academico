@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
title Habitos academicos - Streamlit

set "APP=app.py"
set "REQ=requirements.txt"
set "DATA=data\raw\student_lifestyle_dataset.csv"
set "VENV=.venv"
set "VPY=%VENV%\Scripts\python.exe"
set "PORT=8501"

cls
echo ============================================================
echo   HABITOS ACADEMICOS - INICIO AUTOMATICO DE STREAMLIT
echo ============================================================
echo.
echo Carpeta del proyecto:
echo %CD%
echo.

rem ------------------------------------------------------------
rem 1) Verificar archivos esenciales
rem ------------------------------------------------------------
echo [1/6] Verificando archivos del proyecto...
if not exist "%APP%" goto :missing_app
if not exist "%REQ%" goto :missing_req
if not exist "%DATA%" goto :missing_data
echo       OK - Archivos esenciales encontrados.

rem ------------------------------------------------------------
rem 2) Encontrar una instalacion valida de Python del sistema
rem    Se usa solo para crear/recrear el entorno virtual.
rem ------------------------------------------------------------
echo [2/6] Buscando Python instalado...
set "PYMODE="

where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
    if not errorlevel 1 set "PYMODE=PY"
)

if not defined PYMODE (
    where python >nul 2>&1
    if not errorlevel 1 (
        python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
        if not errorlevel 1 set "PYMODE=PYTHON"
    )
)

if not defined PYMODE goto :python_missing

if "%PYMODE%"=="PY" (
    for /f "delims=" %%V in ('py -3 -c "import sys; print(sys.version.split()[0])"') do set "PYVER=%%V"
) else (
    for /f "delims=" %%V in ('python -c "import sys; print(sys.version.split()[0])"') do set "PYVER=%%V"
)
echo       OK - Python !PYVER! encontrado.

rem ------------------------------------------------------------
rem 3) Verificar/recrear .venv. Esto corrige automaticamente
rem    entornos copiados desde otro computador o usuario.
rem ------------------------------------------------------------
echo [3/6] Verificando entorno virtual...
set "VENV_OK=0"
if exist "%VPY%" (
    "%VPY%" -c "import sys; print(sys.executable)" >nul 2>&1
    if not errorlevel 1 set "VENV_OK=1"
)

if "!VENV_OK!"=="0" (
    if exist "%VENV%" (
        echo       El entorno .venv existente no es valido para este PC.
        echo       Se eliminara y recreara automaticamente...
        rmdir /s /q "%VENV%" >nul 2>&1
        if exist "%VENV%" goto :venv_delete_error
    )

    echo       Creando nuevo entorno virtual...
    if "%PYMODE%"=="PY" (
        py -3 -m venv "%VENV%"
    ) else (
        python -m venv "%VENV%"
    )
    if errorlevel 1 goto :venv_create_error
)

"%VPY%" -c "import sys; print(sys.version)" >nul 2>&1
if errorlevel 1 goto :venv_create_error
echo       OK - Entorno virtual listo.

rem ------------------------------------------------------------
rem 4) Instalar/verificar dependencias.
rem    pip descarga solo lo que falte o no coincida con requirements.
rem ------------------------------------------------------------
echo [4/6] Verificando librerias necesarias...
"%VPY%" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo       Reparando pip...
    "%VPY%" -m ensurepip --upgrade
    if errorlevel 1 goto :pip_error
)

"%VPY%" -m pip install --disable-pip-version-check -r "%REQ%"
if errorlevel 1 goto :requirements_error
echo       OK - Dependencias verificadas.

rem ------------------------------------------------------------
rem 5) Ejecutar verificaciones del proyecto si existe verificar.py
rem ------------------------------------------------------------
echo [5/6] Verificando funcionamiento del proyecto...
if exist "tests\verificar.py" (
    "%VPY%" tests\verificar.py
    if errorlevel 1 goto :verify_error
    echo       OK - Verificacion completa superada.
) else (
    "%VPY%" -c "import pandas, numpy, plotly, streamlit; import app" >nul 2>&1
    if errorlevel 1 goto :verify_error
    echo       OK - Importaciones principales correctas.
)

rem ------------------------------------------------------------
rem 6) Buscar un puerto libre, abrir navegador y ejecutar Streamlit
rem ------------------------------------------------------------
echo [6/6] Iniciando Streamlit...
for /f "usebackq delims=" %%P in (`powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=8501; while($p -le 8599 -and (Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction SilentlyContinue)){ $p++ }; Write-Output $p"`) do set "PORT=%%P"
if not defined PORT set "PORT=8501"

set "URL=http://localhost:!PORT!"
echo.
echo ============================================================
echo   TODO LISTO
echo   Abriendo: !URL!
echo   Para cerrar la aplicacion, vuelve aqui y presiona Ctrl+C.
echo ============================================================
echo.

start "" powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process '!URL!'"
"%VPY%" -m streamlit run "%APP%" --server.port !PORT! --server.headless true

set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
    echo.
    echo Streamlit finalizo con codigo %EXITCODE%.
    pause
)
exit /b %EXITCODE%

:missing_app
echo.
echo ERROR: No se encontro "%APP%".
echo Coloca este archivo .bat en la misma carpeta que app.py.
goto :fatal

:missing_req
echo.
echo ERROR: No se encontro "%REQ%".
echo El proyecto necesita requirements.txt para instalar sus librerias.
goto :fatal

:missing_data
echo.
echo ERROR: No se encontro "%DATA%".
echo Debe estar en la misma carpeta del proyecto.
goto :fatal

:python_missing
echo.
echo ERROR: No se encontro Python 3.10 o superior.
echo Instala Python desde https://www.python.org/downloads/
echo Durante la instalacion marca "Add Python to PATH".
goto :fatal

:venv_delete_error
echo.
echo ERROR: No se pudo eliminar la carpeta .venv.
echo Cierra VS Code, Python o Streamlit si estan usando esa carpeta y vuelve a ejecutar.
goto :fatal

:venv_create_error
echo.
echo ERROR: No se pudo crear un entorno virtual valido.
goto :fatal

:pip_error
echo.
echo ERROR: No se pudo preparar pip dentro del entorno virtual.
goto :fatal

:requirements_error
echo.
echo ERROR: No se pudieron instalar/verificar las dependencias.
echo Revisa tu conexion a Internet y el contenido de requirements.txt.
goto :fatal

:verify_error
echo.
echo ERROR: La verificacion del proyecto fallo.
echo Revisa el mensaje mostrado arriba antes de iniciar Streamlit.
goto :fatal

:fatal
echo.
echo La aplicacion NO se inicio.
pause
exit /b 1
