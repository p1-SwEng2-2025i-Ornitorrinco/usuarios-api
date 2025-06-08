from fastapi import FastAPI, Request
import traceback
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.routers import users

app = FastAPI(title="API de Usuarios")

app.include_router(users.router)

@app.get("/")
def root():
    return {"mensaje": "API de gestión de usuarios"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body},
    )
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print("🔴 Excepción no controlada:")
    traceback.print_exc()  # Esto imprime el traceback completo en consola

    return JSONResponse(
        status_code=500,
        content={"detail": f"Error interno del servidor: {str(exc)}"},
    )
