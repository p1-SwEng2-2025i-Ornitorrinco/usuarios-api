**README.md**

# Usuarios API

API RESTful para la gestión de usuarios en una plataforma de intercambio de servicios, desarrollada con **FastAPI** y **MongoDB**.

## Características
- Registro de usuarios con contraseña encriptada (bcrypt)
- Actualización de datos personales (PUT)
- Eliminación de usuarios (DELETE)
- Consulta individual o general de usuarios (GET)
- MongoDB como base de datos principal (usando Motor)

## Instalación
1. Clona el repositorio:
```bash
git clone https://github.com/p1-SwEng2-2025i-Ornitorrinco/usuarios-api.git
cd usuarios-api
```

2. Crea y activa un entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate  # En Windows
# source venv/bin/activate  # En Linux/macOS
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecuta el servidor:
```bash
uvicorn app.main:app --reload --port 8001
```

## Documentación
- Visita `http://127.0.0.1:8001/docs` para Swagger UI.

## Estructura de carpetas
```
usuarios-api/
├── app/
│   ├── models/
│   │   └── user.py
│   ├── routers/
│   │   └── users.py
│   └── db/
│       └── mongo.py
├── main.py
├── requirements.txt
└── README.md
```

---

**requirements.txt**

```txt
fastapi==0.110.0
uvicorn==0.29.0
motor==3.3.2
pydantic==2.7.1
python-dotenv==1.0.1
passlib[bcrypt]==1.7.4
```
