# Guía de Inicio Rápido

## Para Desarrolladores

### Primera vez - Configuración Inicial

1. **Clonar/Abrir el proyecto**
   ```bash
   cd "C:\Users\V13_Sp2\Desktop\L16 - BACKUP\mosaic-config-interface"
   ```

2. **Ejecutar script de configuración**
   ```bash
   scripts\setup-dev.bat
   ```

   Este script:
   - Verifica Python y Node.js
   - Crea entorno virtual Python
   - Instala todas las dependencias
   - Configura el entorno de desarrollo

### Desarrollo Diario

**Iniciar servidores de desarrollo:**
```bash
scripts\start-dev.bat
```

Esto abrirá dos ventanas:
- Backend (FastAPI) en http://localhost:8000
- Frontend (Vue.js) en http://localhost:5173

**URLs importantes:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

### Comandos Manuales

Si prefieres iniciar manualmente:

**Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Para Continuar el Desarrollo

### Si interrumpiste el desarrollo:

1. **Abrir el archivo de progreso:**
   ```bash
   notepad PROGRESS.md
   ```

2. **Revisar última fase trabajada:**
   - Lee la sección "Tareas Completadas"
   - Lee la sección "Próximos Pasos"

3. **Continuar desde donde dejaste:**
   - Marca tareas completadas con [x]
   - Actualiza el progreso
   - Sigue con la siguiente tarea pendiente

### Estructura de archivos importantes:

```
mosaic-config-interface/
├── README.md          ← Plan completo del proyecto
├── PROGRESS.md        ← Estado actual y progreso
├── QUICKSTART.md      ← Este archivo
├── backend/           ← Código Python/FastAPI
├── frontend/          ← Código Vue.js
└── scripts/           ← Scripts de utilidad
```

## Flujo de Trabajo Recomendado

1. **Inicio de sesión:**
   - Abrir `PROGRESS.md`
   - Revisar "Próximos Pasos"
   - Identificar tarea actual

2. **Durante el desarrollo:**
   - Trabajar en la tarea
   - Hacer commits frecuentes
   - Actualizar `PROGRESS.md` conforme avanzas

3. **Al terminar sesión:**
   - Actualizar `PROGRESS.md` con:
     - Tareas completadas (marcar con [x])
     - Notas importantes
     - Próximos pasos claros
   - Hacer commit final

4. **Para retomar:**
   - Abrir `PROGRESS.md`
   - Leer "Próximos Pasos"
   - Continuar

## Testing

**Backend:**
```bash
cd backend
venv\Scripts\activate
pytest
```

**Frontend:**
```bash
cd frontend
npm run test
```

## Documentación Adicional

- **Plan completo:** Ver [README.md](README.md)
- **Progreso:** Ver [PROGRESS.md](PROGRESS.md)
- **Backend:** Ver [backend/README.md](backend/README.md)
- **Frontend:** Ver [frontend/README.md](frontend/README.md)

## Resolución de Problemas

### Error: Python no encontrado
Instala Python 3.10+ desde https://www.python.org/downloads/

### Error: Node.js no encontrado
Instala Node.js 18+ desde https://nodejs.org/

### Error: venv no existe
Ejecuta `scripts\setup-dev.bat`

### Error: Dependencias no instaladas
```bash
# Backend
cd backend
venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Puerto 8000 o 5173 ya en uso
Detén el proceso que esté usando ese puerto o modifica el puerto en la configuración.

## Próximos Pasos (Según Fase Actual)

Consulta `PROGRESS.md` sección "Próximos Pasos" para saber exactamente qué hacer a continuación.

---

**¿Listo para comenzar?** Ejecuta `scripts\setup-dev.bat` si es la primera vez, o `scripts\start-dev.bat` para desarrollo diario.
