from fastapi import APIRouter, HTTPException
from app.models.user import UserRegister, User, UserLogin, UserInDB
from typing import List,Optional
from app.utils.password import hash_password
from datetime import datetime
from app.db.mongo import users_collection
from app.models.user import UserUpdate
from bson import ObjectId
from passlib.context import CryptContext
from fastapi import UploadFile, File, Form
import os
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db_users: List[User] = []
user_id_counter = 1  # simulamos un autoincremento

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="ID inválido")

        user = await users_collection.find_one({"_id": ObjectId(user_id)})

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Convertir el ObjectId a string para poder retornarlo
        user["_id"] = str(user["_id"])

        return user

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")
    
@router.get("/users")
async def get_all_users():
    try:
        users = []
        cursor = users_collection.find({})
        async for user in cursor:
            user["_id"] = str(user["_id"])
            users.append(user)
        return users

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")

from fastapi import Form, UploadFile, File

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    nombres: Optional[str] = Form(None),
    apellidos: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
    direccion: Optional[str] = Form(None),
    descripcion_habilidades: Optional[str] = Form(None),
    foto: UploadFile = File(None),
    reputacion: Optional[float] = Form(None)
):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="ID inválido")

        update_data = {}

        if nombres is not None:
            update_data["nombres"] = nombres
        if apellidos is not None:
            update_data["apellidos"] = apellidos
        if telefono is not None:
            update_data["telefono"] = telefono
        if direccion is not None:
            update_data["direccion"] = direccion
        if descripcion_habilidades is not None:
            update_data["descripcion_habilidades"] = descripcion_habilidades
        if reputacion is not None:
            update_data["reputacion"] = reputacion

        # Guardar la nueva foto si se envía
        if foto:
            ruta_foto = f"app/static/perfiles/{user_id}_{foto.filename}"
            with open(ruta_foto, "wb") as f:
                contenido = await foto.read()
                f.write(contenido)
            update_data["foto_url"] = f"/static/perfiles/{user_id}_{foto.filename}"

        if not update_data:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")

        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {"message": "Usuario actualizado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/users/register")
async def register_user(
    nombres: str = Form(...),
    apellidos: str = Form(...),
    fecha_nacimiento: str = Form(...),
    correo: str = Form(...),
    codigo_barrio: str = Form(...),
    telefono: str = Form(...),
    direccion: str = Form(...),
    contrasena: str = Form(...),
    confirmar_contrasena: str = Form(...),
    descripcion_habilidades: str = Form(None),
    foto: UploadFile = File(None)
    
):
    if contrasena != confirmar_contrasena:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")

    existing_user = await users_collection.find_one({"correo": correo})
    if existing_user:
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    # Guardar la imagen si se envió
    if foto:
        ruta_foto = f"app/static/perfiles/{correo}_{foto.filename}"
        with open(ruta_foto, "wb") as f:
            contenido = await foto.read()
            f.write(contenido)
        foto_url = f"/static/perfiles/{correo}_{foto.filename}"
    else:
        foto_url = "https://cdn-icons-png.flaticon.com/512/847/847969.png"

    # Crear el usuario
    user_dict = {
        "nombres": nombres,
        "apellidos": apellidos,
        "fecha_nacimiento": fecha_nacimiento,
        "correo": correo,
        "codigo_barrio": codigo_barrio,
        "telefono": telefono,
        "direccion": direccion,
        "descripcion_habilidades": descripcion_habilidades,
        "foto_url": foto_url,
        "hashed_password": hash_password(contrasena),
        "created_at": datetime.today(),
        "reputacion": 0.0  # Nuevo campo
    }

    result = await users_collection.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    return {"message": "Usuario registrado correctamente", "id": user_dict["id"]}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="ID inválido")

        result = await users_collection.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {"message": "Usuario eliminado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")

@router.post("/login")
async def login_user(login_data: UserLogin):
    user = await users_collection.find_one({"correo": login_data.correo})
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if not pwd_context.verify(login_data.contrasena, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    return {"user_id": str(user["_id"])}

@router.get("/users/{user_id}/nombre_completo")
async def get_nombre_completo_usuario(user_id: str):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="ID inválido")

        user = await users_collection.find_one(
            {"_id": ObjectId(user_id)},
            {"nombres": 1, "apellidos": 1,"foto_url": 1}
        )

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        nombre_completo = f"{user['nombres']} {user['apellidos']}"
        return {
            "nombre_completo": nombre_completo,
            "foto_url": user.get("foto_url")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener nombre del usuario: {str(e)}")
    
@router.get("/users/{user_id}/perfil")
async def get_perfil_usuario(user_id: str):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="ID inválido")

        user = await users_collection.find_one(
            {"_id": ObjectId(user_id)},
            {
                "nombres": 1,
                "apellidos": 1,
                "foto_url": 1,
                "reputacion": 1,
                "telefono": 1,
                "correo": 1,
                "direccion": 1
            }
        )

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        user["_id"] = str(user["_id"])
        return {
            "nombre_completo": f"{user['nombres']} {user['apellidos']}",
            "foto_url": user.get("foto_url"),
            "reputacion": user.get("reputacion", 0.0),
            "telefono": user.get("telefono"),
            "correo": user.get("correo"),
            "direccion": user.get("direccion")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener perfil: {str(e)}")

@router.get("/users/{user_id}/publicaciones")
async def get_info_publicaciones(user_id: str):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="ID inválido")

        user = await users_collection.find_one(
            {"_id": ObjectId(user_id)},
            {
                "nombres": 1,
                "apellidos": 1,
                "reputacion": 1,
                "telefono": 1,
                "direccion": 1
            }
        )

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        user["_id"] = str(user["_id"])
        return {
            "nombre_completo": f"{user['nombres']} {user['apellidos']}",
            "reputacion": user.get("reputacion", 0.0),
            "telefono": user.get("telefono"),
            "direccion": user.get("direccion")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener información: {str(e)}")

@router.get("/users/{user_id}/reputacion")
async def get_reputacion_usuario(user_id: str):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="ID inválido")

        user = await users_collection.find_one(
            {"_id": ObjectId(user_id)},
            {
                "foto_url": 1,
                "reputacion": 1
            }
        )

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {
            "foto_url": user.get("foto_url"),
            "reputacion": user.get("reputacion", 0.0)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reputación: {str(e)}")