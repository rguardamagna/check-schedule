# Cheques App — SDD Complete

## Resumen del SDD

Se completó el ciclo completo de Spec-Driven Development para la aplicación de gestión de cheques.

### Fases completadas

1. **EXPLORE** — Relevamiento de requerimientos (columnas XLSX, modalidad local→pública, stack Flask+Alpine.js, lógica 30 días, feriados configurables)
2. **PROPOSE** — Arquitectura de alto nivel: Flask + SQLite + Alpine.js + Bootstrap 5, Flask-Login multi-rol, feriados.json
3. **SPEC** — 8 endpoints API, algoritmo de informe con feriados, modelo de datos Cheque, 10 criterios de éxito
4. **DESIGN** — 17 archivos diseñados (modelos, servicios, rutas, templates HTML + Alpine.js)
5. **TASKS** — 11 tareas secuenciadas (~2.5h estimado)
6. **APPLY** — Implementación completa + 14/14 smoke tests pasando

### Stack

- **Backend**: Flask + SQLAlchemy + Flask-Login
- **Base de datos**: SQLite (migrable a PostgreSQL)
- **Frontend**: Bootstrap 5 (dark) + Alpine.js 3.x
- **Autenticación**: Flask-Login con 3 roles (admin, contador, visualizador)
- **Archivos**: openpyxl para parseo XLSX, pdfkit para PDF

### Funcionalidades

- Carga de XLSX con detección automática de columnas
- Dashboard con resumen de pendientes/pagados/vencidos/próximos
- Informe diario por fecha específica
- Vista semanal (7 días)
- Botón "Pagar" y "Reabrir" en cada cheque
- Lógica de deslizamiento: si no se paga, pasa al día siguiente hasta 30 días
- Luego de 30 días, el cheque expira (no se paga)
- Feriados configurables en `feriados.json`
- Días inhábiles (feriados/fin de semana) no muestran cheques
- PDF exportable del informe diario

### Ubicación

- Código: `/opt/data/cheques-app/`
- Servidor: http://localhost:5000
- Usuarios dev: admin/admin, contador/contador
