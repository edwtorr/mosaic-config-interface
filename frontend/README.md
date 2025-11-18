# Frontend - Interfaz de Configuración de Mosaicos

Interfaz web desarrollada en Vue.js 3 para la configuración visual de patrones de mosaico del robot paletizador L16.

## Tecnologías

- Vue.js 3
- Vite
- Tailwind CSS
- Konva.js / Fabric.js (visualización 2D)
- Pinia (state management)
- Axios (HTTP client)

## Estructura

```
frontend/
├── src/
│   ├── main.js                    # Entry point
│   ├── App.vue                    # Componente raíz
│   ├── components/                # Componentes reutilizables
│   │   ├── MosaicSelector.vue    # Selector de mosaicos
│   │   ├── MosaicViewer2D.vue    # Visualización 2D
│   │   ├── MosaicEditor.vue      # Editor de configuración
│   │   └── PointEditor.vue       # Editor de puntos
│   ├── views/                     # Vistas/Páginas
│   │   └── MosaicConfigView.vue
│   ├── stores/                    # Pinia stores
│   │   └── mosaicStore.js
│   ├── services/                  # API calls
│   │   └── api.js
│   └── assets/                    # Recursos estáticos
│       ├── styles/
│       └── images/
├── public/                        # Archivos públicos
├── tests/                         # Tests
└── package.json
```

## Instalación

```bash
# Instalar dependencias
npm install
```

## Desarrollo

```bash
# Servidor de desarrollo
npm run dev

# Build para producción
npm run build

# Preview de build de producción
npm run preview

# Ejecutar tests
npm run test

# Linting
npm run lint
```

## Características Principales

### Fase 1 (MVP)
- ✅ Selector de mosaicos (1-12)
- ✅ Visualización 2D del patrón
- ✅ Editor de puntos de cogida/dejada
- ✅ Formularios de edición
- ✅ Validación en tiempo real
- ✅ Guardar configuración

### Fase 2 (Mejoras)
- 🔄 Visualización 2D interactiva (drag & drop)
- 🔄 Zoom y pan en canvas
- 🔄 Preview de cambios
- 🔄 Visualización 3D (opcional)

### Fase 3 (Avanzado)
- ⏳ Herramientas de edición (rotar, espejo, offset)
- ⏳ Sistema de plantillas
- ⏳ Historial de cambios
- ⏳ Multi-idioma

## Acceso

Una vez el servidor de desarrollo esté corriendo:
- **Local:** http://localhost:5173
- **Red local:** http://[IP-de-tu-PC]:5173

## Configuración del Backend

Por defecto, el frontend se conecta al backend en `http://localhost:8000`.
Para cambiar esto, edita el archivo `src/services/api.js`.

## Estado del Desarrollo

Ver [PROGRESS.md](../PROGRESS.md) para el estado actual del proyecto.

## Componentes Principales (Planificados)

### MosaicSelector
Selector dropdown para elegir entre los 12 mosaicos disponibles.

### MosaicViewer2D
Canvas 2D que muestra visualmente el patrón del mosaico con:
- Grid de referencia
- Puntos del patrón numerados
- Punto de cogida destacado
- Punto de dejada destacado
- Dimensiones y reglas

### MosaicEditor
Panel de edición con formularios para:
- Coordenadas X, Y, Z de cada punto
- Ajustes globales (offset)
- Validación de límites

### PointEditor
Editor individual de puntos con:
- Inputs numéricos
- Validación de rangos
- Feedback visual
