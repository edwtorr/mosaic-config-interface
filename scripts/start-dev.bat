@echo off
echo ========================================
echo Iniciando Entorno de Desarrollo
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

if not exist "frontend" (
    echo ERROR: No se encuentra el directorio frontend
    echo Ejecuta este script desde la raiz del proyecto
    pause
    exit /b 1
)

echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)
echo Python: OK

echo.
echo [2/4] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js no esta instalado o no esta en el PATH
    pause
    exit /b 1
)
echo Node.js: OK

echo.
echo [3/4] Iniciando Backend (FastAPI)...
start "Backend FastAPI" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

echo.
echo [4/4] Iniciando Frontend (Vue.js)...
timeout /t 2 /nobreak >nul
start "Frontend Vue.js" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Entorno de desarrollo iniciado!
echo.
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
echo Presiona Ctrl+C en cada ventana para detener
echo ========================================
pause
