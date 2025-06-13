from fastapi import FastAPI, Request
import traceback
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware  # 🔴 Importar CORS
from app.routers import users

app = FastAPI(title="API de Usuarios")

# 🔵 Añadir middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔵 Incluir las rutas del módulo de usuarios
app.include_router(users.router)

@app.get("/")
def root():
    return {"mensaje": "API de gestión de usuarios"}

# 🔴 Manejo de errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body},
    )

# 🔴 Manejo de errores generales
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print("🔴 Excepción no controlada:")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Error interno del servidor: {str(exc)}"},
    )
