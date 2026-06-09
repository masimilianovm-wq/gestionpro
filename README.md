# GestiónPro — Sistema de Administración Web

Sistema completo de stock y ventas. Funciona en PC, celular y tablet.

## Credenciales default
- Email: admin@gestionpro.com
- Contraseña: admin123

## Cómo subir a Railway (GRATIS, 5 minutos)

### Paso 1 — Subir el código a GitHub
1. Entrá a https://github.com y creá una cuenta (si no tenés)
2. Hacé click en "+" → "New repository"
3. Nombre: `gestionpro` → "Create repository"
4. Descargá GitHub Desktop: https://desktop.github.com
5. Cloná el repo y copiá todos estos archivos adentro
6. "Commit" y "Push"

### Paso 2 — Deploy en Railway
1. Entrá a https://railway.app
2. "Start a New Project" → "Deploy from GitHub repo"
3. Conectá tu cuenta de GitHub y elegí `gestionpro`
4. Railway detecta automáticamente el Procfile y despliega
5. En "Settings" → "Domains" → generá un dominio gratis
6. ¡Listo! El sistema queda online en una URL tipo `gestionpro-production.up.railway.app`

### Variables de entorno (en Railway → Variables)
```
SECRET_KEY=una-clave-secreta-larga-y-aleatoria
```

## Estructura del proyecto
```
gestionpro/
├── main.py          # API FastAPI (todos los endpoints)
├── models.py        # Base de datos SQLAlchemy
├── auth.py          # Login y JWT
├── pdf_gen.py       # Generación de PDFs
├── requirements.txt # Dependencias Python
├── Procfile         # Comando de inicio Railway
└── frontend/
    └── index.html   # Frontend completo (HTML/CSS/JS)
```

## Módulos incluidos
- Dashboard con stats en tiempo real
- Nueva Venta (carga rápida, múltiples productos, impuestos seleccionables)
- Comprobantes (Factura A/B/C, Remito, Presupuesto) con PDF descargable
- Clientes con condición IVA y lista de precios
- Stock / Productos con búsqueda, filtros y paginación
- Movimientos de stock (ingresos/egresos)
- Proveedores
- Órdenes de Compra editables (manual + autocompletado por stock bajo)
- Configuración de empresa, listas de precios, impuestos, familias
- Usuarios con roles (admin / vendedor)
- Importar productos desde Excel
- Exportar stock a CSV
- Responsive: funciona en celular y tablet

## Ejecutar localmente
```bash
pip install -r requirements.txt
python main.py
# Abrí http://localhost:8000
```
