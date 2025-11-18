@echo off
echo ========================================
echo Configuracion Inicial del Proyecto
echo Interfaz de Configuracion de Mosaicos L16
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "backend" (
    echo ERROR: No se encuentra el directorio backend
    echo Ejecuta este script desde la raiz del proyecto
    pause
    exit /b 1
)

echo [1/5] Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo Instala Python 3.10 o superior desde python.org
    pause
    exit /b 1
)
echo.

echo [2/5] Creando entorno virtual Python...
cd backend
if exist "venv" (
    echo Entorno virtual ya existe, omitiendo...
) else (
    python -m venv venv
    echo Entorno virtual creado
)
echo.

echo [3/5] Instalando dependencias Python...
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
echo.

cd ..

echo [4/5] Verificando Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js no esta instalado
    echo Instala Node.js 18+ desde nodejs.org
    pause
    exit /b 1
)
echo.

echo [5/5] Instalando dependencias Node.js...
cd frontend
if exist "package.json" (
    call npm install
    echo Dependencias instaladas
) else (
    echo ADVERTENCIA: package.json no encontrado
    echo El proyecto frontend aun no esta inicializado
)
cd ..

echo.
echo ========================================
echo Configuracion completada exitosamente!
echo.
echo Proximos pasos:
echo 1. Ejecuta 'scripts\start-dev.bat' para iniciar el desarrollo
echo 2. Revisa PROGRESS.md para ver el estado del proyecto
echo ========================================
pause
