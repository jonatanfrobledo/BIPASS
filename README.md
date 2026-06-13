# BIPASS - Sistema de Gestión de Eventos y Tickets

## 📌 Introducción

**BIPASS** es un sistema integral de gestión de eventos y venta de tickets desarrollado con **FastAPI**. Diseñado para proporcionar una solución completa y escalable, BIPASS facilita la gestión de eventos, venta de entradas, procesamiento de pagos y administración de usuarios, todo con un enfoque en la seguridad y la experiencia del usuario.

> 🔍 **Este proyecto fue desarrollado como parte de la materia _Gestión de Proyectos_ de la Tecnicatura Universitaria en Programación (Universidad Austral).**

>🤖 Uso de Inteligencia Artificial: Durante el desarrollo se utilizaron herramientas de asistencia como ChatGPT y GitHub Copilot para apoyo en tareas de documentación, validación de arquitectura, generación de ejemplos de código y resolución de problemas específicos.

Todas las decisiones de diseño, implementación e integración fueron comprendidas, revisadas y adaptadas al contexto del proyecto por el alumno y desarrollador.

---

## 🚀 Características Principales

- 🎫 **Gestión de Eventos**: Creación, modificación y eliminación de eventos con detalles completos.
- 💳 **Sistema de Pagos**: Integración con pasarelas de pago para transacciones seguras.
- 👥 **Gestión de Usuarios**: Sistema de roles y permisos para diferentes tipos de usuarios.
- 📊 **Panel Administrativo**: Interfaz intuitiva para la gestión del sistema.
- 📝 **Sistema de Reseñas**: Los usuarios pueden calificar y comentar eventos.
- 🏟️ **Gestión de Locaciones**: Administración completa de venues y sus capacidades.
- 📱 **API RESTful**: Endpoints bien definidos y documentados.
- 🛡️ **Seguridad**: Uso de JWT, encriptación y validaciones robustas.

## Arquitectura del Sistema

### Diagrama de Base de Datos
![Diagrama de Base de Datos](docs/Diagrama%20de%20Base%20de%20Datos.png)

El diagrama muestra la estructura de la base de datos con las siguientes entidades principales:
- **Users**: Gestión de usuarios y autenticación
- **Events**: Información detallada de eventos
- **Venues**: Datos de las locaciones
- **Orders**: Proceso de compra y gestión de órdenes
- **Tickets**: Control de entradas y disponibilidad
- **Payments**: Registro de transacciones
- **Reviews**: Sistema de calificaciones y comentarios

### Diagrama de Integración del Sistema
![Diagrama de Secuencia](docs/Diagrama%20de%20Secuencia.png)

El diagrama ilustra el flujo de una transacción completa:
1. **Autenticación**: Validación de usuarios y tokens
2. **Procesamiento**: Gestión de órdenes y disponibilidad
3. **Pagos**: Integración con pasarelas de pago
4. **Confirmación**: Generación de tickets y notificaciones

## Tecnologías Implementadas

### Backend
- **FastAPI**: Framework web moderno y de alto rendimiento
- **SQLModel**: ORM para gestión de base de datos
- **PostgreSQL**: Base de datos relacional robusta
- **Pydantic**: Validación y serialización de datos
- **Python-Jose**: Manejo seguro de JWT
- **Passlib**: Gestión de contraseñas
- **Alembic**: Control de versiones de base de datos

### Seguridad
- Autenticación JWT
- Encriptación de datos sensibles
- Validación de entrada de datos
- Protección contra ataques comunes
- Manejo seguro de sesiones

### Documentación
- **Swagger UI**: Documentación interactiva de la API
- **ReDoc**: Documentación alternativa de la API
- **Markdown**: Documentación técnica detallada

## Estructura del Proyecto
```
BIPASS/
├── app/
│   ├── api/           # Endpoints de la API
│   ├── core/          # Configuraciones centrales
│   ├── db/            # Configuración de base de datos
│   ├── models/        # Modelos de datos
│   ├── schemas/       # Esquemas Pydantic
│   ├── services/      # Lógica de negocio
│   └── utils/         # Utilidades
├── alembic/           # Migraciones de base de datos
├── docs/              # Documentación y diagramas
├── tests/             # Pruebas unitarias y de integración
└── scripts/           # Scripts de utilidad
```

## Características Técnicas Destacadas
- Arquitectura modular y escalable
- Diseño orientado a microservicios
- Implementación de patrones de diseño
- Manejo asíncrono de operaciones
- Sistema de caché para optimización
- Logging y monitoreo
- Manejo de errores robusto

## 🚧 Roadmap

- [x] Gestión de usuarios
- [x] Gestión de eventos
- [x] Sistema de tickets
- [x] Pagos
- [ ] Streaming en vivo
- [ ] Aplicación móvil
- [ ] Notificaciones push

      
## Contacto
Jonatan Frobledo - [@jonatanfrobledo](https://github.com/jonatanfrobledo)

Tel: + 54 9 (341) 6 212725 

Link del Proyecto: https://github.com/jonatanfrobledo/BIPASS

