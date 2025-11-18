# Interfaz de Configuración de Mosaicos - Robot Paletizador L16

**Repositorio:** https://github.com/edwtorr/mosaic-config-interface

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

## Compatibilidad y Detección de Proyectos UR

### Alcance de Compatibilidad

Este sistema está diseñado para trabajar con **proyectos de Universal Robots** que utilicen archivos `.script` y estructuras similares al proyecto L16. El sistema puede adaptarse automáticamente a diferentes proyectos UR.

### Robots Universal Robots Compatibles

El sistema soporta todos los modelos de la familia Universal Robots:

**Modelos Estándar:**
- UR3 / UR3e
- UR5 / UR5e
- UR10 / UR10e
- UR16e
- UR20
- UR30

**Variantes:**
- Generación estándar (CB3)
- Generación e-Series (Gen 5)
- Variantes DC (Direct Current)

### Detección Automática de Proyectos

El sistema incluirá capacidad de **detección automática** para identificar y adaptarse a diferentes estructuras de proyectos UR:

#### 1. Detección de Estructura del Proyecto

```
Análisis automático:
├── Identificar archivos .urp (programa principal)
├── Detectar archivos .script (scripts modulares)
├── Localizar archivos .installation (configuración)
├── Identificar archivos .variables (estado de variables)
└── Reconocer convenciones de nombres
```

#### 2. Identificación de Patrones

El sistema buscará automáticamente:

**Patrones de Mosaico:**
- Archivos con nombres como: `mosaico*.script`, `pattern*.script`, `layer*.script`
- Variables de puntos: `p[...]`, `pose_*`, `waypoint_*`
- Estructuras de movimiento: `movel()`, `movej()`, `movep()`

**Puntos de Operación:**
- Puntos de cogida: `pick_point`, `pickup_pos`, variables con "cog"
- Puntos de dejada: `place_point`, `drop_pos`, variables con "dej"
- Offsets y ajustes: variables con "offset", "adjust", "delta"

**Variables de Configuración:**
- Contadores de pallet: `pallet_count`, `layer_count`
- Estados de sistema: `step_code`, `state_machine`
- Configuraciones: variables numéricas y booleanas

#### 3. Detección de Modelo de Robot

El sistema extraerá automáticamente:

```python
# Desde archivos .installation o .urp
- Modelo de robot (UR3, UR5, UR10, UR16, UR20, UR30)
- Generación (CB3, e-Series)
- Límites de workspace específicos del modelo
- Configuración de payload máximo
- Versión de PolyScope
```

#### 4. Adaptación de Validaciones

Según el modelo detectado, el sistema ajustará:

| Modelo | Alcance | Payload | TCP Speed | Validaciones |
|--------|---------|---------|-----------|--------------|
| UR3/UR3e | 500mm | 3kg | 1 m/s | Workspace pequeño |
| UR5/UR5e | 850mm | 5kg | 1 m/s | Workspace medio |
| UR10/UR10e | 1300mm | 12.5kg | 1 m/s | Workspace grande |
| UR16e | 900mm | 16kg | 1 m/s | Payload alto |
| UR20 | 1750mm | 20kg | 1.5 m/s | Alcance extendido |
| UR30 | 1300mm | 30kg | 1.5 m/s | Payload muy alto |

### Tipos de Aplicaciones Compatibles

El sistema puede trabajar con diferentes tipos de aplicaciones UR:

**Paletizado (Principal):**
- ✅ Patrones de mosaico
- ✅ Apilado de cajas/productos
- ✅ Gestión de pallets multicapa
- ✅ Múltiples líneas de producción

**Pick & Place:**
- ✅ Recogida y colocación de piezas
- ✅ Patrones de ordenación
- ✅ Trayectorias optimizadas

**Machine Tending:**
- 🔄 Carga/descarga de máquinas
- 🔄 Secuencias de espera
- 🔄 Puntos de aproximación

**Ensamblaje:**
- 🔄 Secuencias de montaje
- 🔄 Puntos de inserción
- 🔄 Movimientos de precisión

✅ Totalmente compatible | 🔄 Compatible con adaptaciones menores

### Configuración de Proyectos

El sistema permitirá configurar:

**Detección Manual (cuando sea necesaria):**
```json
{
  "project_name": "L16_Paletizado",
  "robot_model": "UR16e",
  "project_type": "palletizing",
  "script_patterns": {
    "mosaic_files": "mosaico*.script",
    "pick_variable": "PosicionCogida",
    "place_variable": "PosicionDejada"
  },
  "workspace_limits": {
    "x": [-1300, 1300],
    "y": [-1300, 1300],
    "z": [0, 1000]
  }
}
```

**Detección Automática (preferida):**
- El sistema analizará el proyecto y generará esta configuración automáticamente
- El usuario podrá revisar y ajustar si es necesario
- Se guardará como perfil reutilizable

### Casos de Uso Multi-Proyecto

**Escenario 1: Múltiples líneas en la misma planta**
```
Planta A/
├── L16_Paletizado/        (UR16e)
├── L10_Paletizado/        (UR10e)
└── L05_PickPlace/         (UR5e)

→ El sistema detecta y trabaja con los 3 proyectos
→ Configuración específica por proyecto
→ Base de datos de configuraciones guardadas
```

**Escenario 2: Diferentes versiones del mismo proyecto**
```
L16_Paletizado/
├── Produccion/            (activo)
├── Testing/               (pruebas)
└── Backup_2024/           (histórico)

→ El sistema distingue entre versiones
→ Permite comparar configuraciones
→ Facilita rollback si es necesario
```

**Escenario 3: Diferentes fabricantes en la planta**
```
Robots/
├── UR16_Linea1/           ✅ Compatible
├── UR10_Linea2/           ✅ Compatible
├── ABB_Linea3/            ❌ No compatible (diferente fabricante)
└── KUKA_Linea4/           ❌ No compatible (diferente fabricante)

→ El sistema identifica automáticamente proyectos UR
→ Muestra advertencia para otros fabricantes
```

### Implementación (Fase 1 mejorada)

Durante la **FASE 1 - Análisis y Parser**, se implementará:

1. **Detector de proyectos UR:**
   - Escaneo de directorios
   - Identificación de archivos UR
   - Análisis de estructura

2. **Parser inteligente:**
   - Reconocimiento de convenciones
   - Extracción de variables relevantes
   - Adaptación a diferentes estilos de código

3. **Sistema de perfiles:**
   - Guardado de configuraciones detectadas
   - Reutilización para proyectos similares
   - Biblioteca de patrones comunes

4. **Validador adaptativo:**
   - Límites específicos por modelo
   - Reglas personalizables
   - Warnings según aplicación

### Beneficios de la Detección Automática

✅ **Flexibilidad:** Trabajar con cualquier proyecto UR sin configuración manual
✅ **Reutilización:** Mismo sistema para múltiples líneas/proyectos
✅ **Escalabilidad:** Fácil expansión a nuevos proyectos
✅ **Mantenimiento:** Un solo sistema para toda la planta
✅ **Seguridad:** Validaciones específicas por modelo de robot

### Limitaciones

⚠️ **No compatible con:**
- Robots de otros fabricantes (ABB, KUKA, Fanuc, etc.)
- Proyectos que no usen archivos .script
- Código compilado o binario sin acceso al source

⚠️ **Requiere adaptación manual para:**
- Convenciones de nombres muy diferentes
- Estructuras de datos custom muy específicas
- Proyectos con encriptación o protección

---

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
