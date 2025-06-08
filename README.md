# usuarios-api

API REST para la gestión de usuarios del sistema de intercambio de servicios.

## Cómo usar

1. Clona el repositorio.
2. Crea y activa un entorno virtual.
3. Instala las dependencias con `pip install -r requirements.txt`
4. Ejecuta: `uvicorn app.main:app --reload`
5. Accede a `http://127.0.0.1:8000/docs` para la documentación interactiva.

## Endpoints principales

- `POST /users/register` → Registrar usuario
- `POST /users/login` → Iniciar sesión (JWT)
