# Interfaz de Configuración de Mosaicos - Robot Paletizador L16

## Descripción del Proyecto

Interfaz web para la configuración y ajuste de puntos de cogida y dejada de los patrones de mosaico del sistema de paletizado L16, eliminando la necesidad de modificar código directamente y simplificando los ajustes por parte del equipo técnico.

## Objetivos

### Objetivo Principal
Crear una herramienta visual e intuitiva que permita a técnicos sin conocimientos de programación ajustar los patrones de mosaico del robot paletizador.

### Objetivos Específicos
- ✅ Visualización 2D/3D de patrones de mosaico
- ✅ Edición visual de puntos de cogida y dejada
- ✅ Validación automática de límites del robot
- ✅ Guardado seguro con backup automático
- ✅ Preview antes de aplicar cambios
- ✅ Historial de modificaciones
- ✅ Interfaz accesible desde red local

## Stack Tecnológico

### Backend
- **Python 3.10+**
- **FastAPI** - Framework web moderno y rápido
- **Pydantic** - Validación de datos
- **uvicorn** - Servidor ASGI

### Frontend
- **Vue.js 3** - Framework JavaScript progresivo
- **Vite** - Build tool y dev server
- **Tailwind CSS** - Framework CSS utility-first
- **Konva.js / Fabric.js** - Canvas para visualización 2D
- **Three.js** (opcional) - Visualización 3D

### Herramientas
- **Git** - Control de versiones
- **pytest** - Testing backend
- **Vitest** - Testing frontend

## Arquitectura del Sistema

```
┌──────────────────────────────────────────────────────────┐
│                    PC Taller / Servidor                   │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │              Backend (FastAPI)                     │  │
│  │  ┌──────────────┐  ┌──────────────┐                │  │
│  │  │  Parser      │  │  Validator   │                │  │
│  │  │  .script     │  │  Límites     │                │  │
│  │  └──────────────┘  └──────────────┘                │  │
│  │  ┌──────────────┐  ┌──────────────┐                │  │
│  │  │  File        │  │  Backup      │                │  │
│  │  │  Manager     │  │  Manager     │                │  │
│  │  └──────────────┘  └──────────────┘                │  │
│  │                                                     │  │
│  │  API REST (http://localhost:8000)                  │  │
│  └────────────────────┬───────────────────────────────┘  │
│                       │                                   │
│  ┌────────────────────▼───────────────────────────────┐  │
│  │           Frontend (Vue.js + Vite)                 │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐     │  │
│  │  │ Editor   │  │ Viewer   │  │ Validation   │     │  │
│  │  │ Panel    │  │ 2D/3D    │  │ Feedback     │     │  │
│  │  └──────────┘  └──────────┘  └──────────────┘     │  │
│  │                                                     │  │
│  │  http://localhost:5173                             │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
           │
           │ Red Local (192.168.x.x)
           │
┌──────────▼──────────┐
│  Tablet / Otro PC   │
│  Navegador Web      │
└─────────────────────┘
```

## Fases de Desarrollo

### 📋 FASE 0: Preparación (ACTUAL)
**Tiempo estimado: 1 día**

- [x] Análisis de requisitos
- [x] Selección de stack tecnológico
- [x] Creación de documentación inicial
- [ ] Configuración del entorno de desarrollo
- [ ] Estructura de directorios del proyecto
- [ ] Inicialización de repositorio Git

**Entregables:**
- README del proyecto
- Archivo de seguimiento de progreso
- Estructura de carpetas

---

### 🔍 FASE 1: Análisis y Parser (MVP Básico)
**Tiempo estimado: 3-4 días**

#### 1.1 Análisis de Archivos .script
- [ ] Documentar estructura de archivos mosaico1-12.script
- [ ] Identificar patrón de puntos en archivos
- [ ] Identificar variables críticas (puntos de cogida/dejada)
- [ ] Crear especificación de formato de datos

#### 1.2 Parser de Archivos
- [ ] Implementar lectura de archivos .script
- [ ] Extraer puntos de mosaico
- [ ] Extraer puntos de cogida
- [ ] Extraer puntos de dejada
- [ ] Extraer configuración de capa (tipo 1/tipo 2)
- [ ] Convertir a formato JSON estructurado
- [ ] Crear tests unitarios para parser

#### 1.3 Escritor de Archivos
- [ ] Implementar generación de archivos .script
- [ ] Mantener formato original
- [ ] Preservar comentarios
- [ ] Validar sintaxis URScript
- [ ] Crear tests unitarios para escritor

**Entregables:**
- Parser funcional de archivos .script
- Conversor bidireccional .script ↔ JSON
- Tests unitarios
- Documentación de formato de datos

---

### 🚀 FASE 2: Backend API (MVP Básico)
**Tiempo estimado: 3-4 días**

#### 2.1 Configuración de FastAPI
- [ ] Setup de proyecto FastAPI
- [ ] Configuración de CORS
- [ ] Configuración de logging
- [ ] Manejo de errores centralizado
- [ ] Documentación automática (Swagger)

#### 2.2 Endpoints Básicos
- [ ] `GET /api/mosaics` - Listar mosaicos disponibles
- [ ] `GET /api/mosaic/{id}` - Obtener configuración de mosaico
- [ ] `PUT /api/mosaic/{id}` - Actualizar configuración
- [ ] `GET /api/health` - Health check

#### 2.3 Gestión de Archivos
- [ ] Lectura desde directorio del proyecto robot
- [ ] Escritura con backup automático
- [ ] Validación de permisos de archivo
- [ ] Sistema de rollback

#### 2.4 Validación de Datos
- [ ] Validación de límites del robot (workspace)
- [ ] Validación de formato de puntos
- [ ] Validación de colisiones básicas
- [ ] Mensajes de error descriptivos

**Entregables:**
- API REST funcional
- Documentación Swagger
- Sistema de backup automático
- Tests de integración

---

### 🎨 FASE 3: Frontend Básico (MVP Básico)
**Tiempo estimado: 4-5 días**

#### 3.1 Setup de Vue.js
- [ ] Inicializar proyecto Vite + Vue 3
- [ ] Configurar Tailwind CSS
- [ ] Estructura de componentes
- [ ] Router (si necesario)
- [ ] Estado global (Pinia)

#### 3.2 Componentes Básicos
- [ ] Selector de mosaicos
- [ ] Visor de configuración actual
- [ ] Formularios de edición de puntos
- [ ] Botones de acción (Guardar/Cancelar)
- [ ] Feedback de validación

#### 3.3 Visualización 2D
- [ ] Canvas 2D con Konva.js/Fabric.js
- [ ] Renderizado de patrón de mosaico
- [ ] Punto de cogida visual
- [ ] Punto de dejada visual
- [ ] Grid de referencia
- [ ] Regla/dimensiones

#### 3.4 Interacción Básica
- [ ] Cargar mosaico seleccionado
- [ ] Editar valores en formulario
- [ ] Preview en tiempo real
- [ ] Validación visual de límites
- [ ] Guardar cambios

**Entregables:**
- Interfaz web funcional
- Visualización 2D operativa
- Edición básica de puntos
- Integración con backend

---

### ✅ HITO: MVP FUNCIONAL
**Al completar Fase 3 tendremos un sistema básico operativo**
- Parser lee/escribe archivos .script
- API REST funcional con validación
- Interfaz web para editar puntos
- Visualización 2D de patrones
- Sistema de backup

---

### 🎯 FASE 4: Mejoras de Visualización
**Tiempo estimado: 3-4 días**

#### 4.1 Visualización 2D Avanzada
- [ ] Arrastrar y soltar puntos
- [ ] Zoom y pan en canvas
- [ ] Mostrar trayectorias entre puntos
- [ ] Numeración de puntos
- [ ] Colores por tipo de capa
- [ ] Highlight de punto seleccionado
- [ ] Tooltips informativos

#### 4.2 Visualización 3D (Opcional)
- [ ] Setup de Three.js
- [ ] Modelo 3D básico de pallet
- [ ] Modelo 3D de productos
- [ ] Renderizado de patrón en 3D
- [ ] Controles de cámara
- [ ] Vista de múltiples capas

#### 4.3 Preview de Cambios
- [ ] Vista antes/después
- [ ] Comparación lado a lado
- [ ] Resaltar diferencias
- [ ] Confirmación visual antes de guardar

**Entregables:**
- Visualización 2D interactiva
- Sistema de preview avanzado
- (Opcional) Visualización 3D

---

### 🔧 FASE 5: Funcionalidades Avanzadas
**Tiempo estimado: 4-5 días**

#### 5.1 Herramientas de Edición
- [ ] Aplicar offset global a todos los puntos
- [ ] Rotar patrón completo
- [ ] Espejo horizontal/vertical
- [ ] Duplicar configuración de mosaico
- [ ] Resetear a valores predeterminados
- [ ] Copiar/Pegar configuraciones

#### 5.2 Validación Avanzada
- [ ] Simulación de alcance del robot
- [ ] Detección de colisiones robot-pallet
- [ ] Validación de orientación de gripper
- [ ] Alertas de velocidad/aceleración
- [ ] Estimación de tiempo de ciclo

#### 5.3 Gestión de Configuraciones
- [ ] Guardar configuraciones como plantillas
- [ ] Importar/Exportar JSON
- [ ] Comparar configuraciones
- [ ] Búsqueda de configuraciones

**Entregables:**
- Herramientas avanzadas de edición
- Validación completa de seguridad
- Sistema de plantillas

---

### 📊 FASE 6: Historial y Trazabilidad
**Tiempo estimado: 2-3 días**

#### 6.1 Sistema de Historial
- [ ] Base de datos SQLite para historial
- [ ] Registro de cada cambio
- [ ] Timestamp y usuario
- [ ] Descripción de cambios

#### 6.2 Funcionalidades de Historial
- [ ] Ver historial de cambios
- [ ] Comparar versiones
- [ ] Restaurar versión anterior
- [ ] Exportar historial

#### 6.3 Backup Avanzado
- [ ] Backup automático antes de cambios
- [ ] Gestión de backups (límite de archivos)
- [ ] Restauración selectiva
- [ ] Validación de integridad

**Entregables:**
- Sistema completo de historial
- Gestión avanzada de backups
- Trazabilidad completa

---

### 🔐 FASE 7: Seguridad y Multi-usuario
**Tiempo estimado: 2-3 días**

#### 7.1 Autenticación Básica
- [ ] Sistema de login simple
- [ ] Usuarios: admin / técnico / visualización
- [ ] Gestión de sesiones
- [ ] Tokens de acceso

#### 7.2 Permisos
- [ ] Admin: todos los permisos
- [ ] Técnico: editar y guardar
- [ ] Visualización: solo lectura
- [ ] Registro de acciones por usuario

#### 7.3 Seguridad de Archivos
- [ ] Validación de paths (evitar path traversal)
- [ ] Checksum de archivos
- [ ] Validación de contenido .script
- [ ] Límites de tamaño de archivo

**Entregables:**
- Sistema de autenticación
- Control de permisos
- Auditoría de cambios

---

### 🚀 FASE 8: Optimización y Deployment
**Tiempo estimado: 2-3 días**

#### 8.1 Optimización Backend
- [ ] Caché de configuraciones
- [ ] Optimización de parser
- [ ] Compresión de respuestas
- [ ] Rate limiting

#### 8.2 Optimización Frontend
- [ ] Build de producción
- [ ] Lazy loading de componentes
- [ ] Optimización de bundle size
- [ ] PWA (opcional)

#### 8.3 Deployment
- [ ] Script de instalación para Windows
- [ ] Configuración como servicio Windows
- [ ] Auto-start en arranque del sistema
- [ ] Guía de instalación

#### 8.4 Documentación
- [ ] Manual de usuario (español)
- [ ] Guía de instalación
- [ ] Troubleshooting
- [ ] Video tutoriales

**Entregables:**
- Aplicación optimizada
- Instalador Windows
- Documentación completa

---

### 🎁 FASE 9: Extras (Opcional)
**Tiempo estimado: variable**

- [ ] Generador automático de patrones
- [ ] Importar patrones desde Excel
- [ ] Integración con ERP/MES
- [ ] Dashboard de estadísticas
- [ ] Modo oscuro
- [ ] Múltiples idiomas
- [ ] Simulador de robot virtual
- [ ] Integración directa con controlador UR
- [ ] Mobile responsive

---

## Requisitos del Sistema

### Desarrollo
- Python 3.10 o superior
- Node.js 18 o superior
- Git
- Editor de código (VS Code recomendado)

### Producción
- Windows 10/11
- Python 3.10+ instalado
- Red local configurada
- Acceso al directorio del proyecto L16

## Estructura del Proyecto

```
mosaic-config-interface/
├── README.md                          # Este archivo
├── PROGRESS.md                        # Seguimiento de progreso
├── .gitignore
│
├── backend/                           # Backend Python/FastAPI
│   ├── app/
│   │   ├── main.py                   # Entry point FastAPI
│   │   ├── config.py                 # Configuración
│   │   ├── models/                   # Modelos Pydantic
│   │   ├── routers/                  # Endpoints API
│   │   ├── services/                 # Lógica de negocio
│   │   │   ├── parser.py            # Parser .script
│   │   │   ├── writer.py            # Escritor .script
│   │   │   ├── validator.py         # Validaciones
│   │   │   └── backup.py            # Sistema backup
│   │   └── utils/                    # Utilidades
│   ├── tests/                        # Tests
│   ├── requirements.txt              # Dependencias Python
│   └── README.md
│
├── frontend/                          # Frontend Vue.js
│   ├── src/
│   │   ├── main.js                   # Entry point Vue
│   │   ├── App.vue                   # Componente raíz
│   │   ├── components/               # Componentes Vue
│   │   │   ├── MosaicSelector.vue
│   │   │   ├── MosaicViewer2D.vue
│   │   │   ├── MosaicEditor.vue
│   │   │   └── PointEditor.vue
│   │   ├── views/                    # Vistas/Páginas
│   │   ├── stores/                   # Pinia stores
│   │   ├── services/                 # API calls
│   │   └── assets/                   # Recursos estáticos
│   ├── public/
│   ├── tests/                        # Tests frontend
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
│
├── docs/                              # Documentación
│   ├── user-manual.md
│   ├── installation.md
│   ├── api-documentation.md
│   └── architecture.md
│
└── scripts/                           # Scripts de utilidad
    ├── install.bat                   # Instalador Windows
    ├── start-dev.bat                 # Iniciar desarrollo
    └── build-production.bat          # Build producción
```

## Instalación (Cuando esté listo)

### Modo Desarrollo

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (otra terminal)
cd frontend
npm install
npm run dev
```

### Modo Producción

```bash
# Ejecutar instalador
scripts\install.bat
```

## Uso (Cuando esté listo)

1. Abrir navegador en `http://localhost:5173`
2. Seleccionar mosaico a editar
3. Visualizar patrón actual
4. Modificar puntos
5. Validar cambios
6. Guardar configuración

## Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

## Contribución

Este es un proyecto interno para el sistema L16.

## Licencia

Uso interno - Sistema de Paletizado L16

## Contacto y Soporte

Equipo técnico L16

---

**Última actualización:** 2025-01-18
**Versión:** 0.1.0 - Fase 0 (Preparación)
**Estado:** En desarrollo inicial
