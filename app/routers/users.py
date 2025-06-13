from fastapi import APIRouter, HTTPException
from app.models.user import UserRegister, User, UserLogin, UserInDB
from typing import List
from app.utils.password import hash_password
from datetime import datetime
from app.db.mongo import users_collection
from app.models.user import UserUpdate
from bson import ObjectId
from passlib.context import CryptContext
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

@router.put("/users/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate):
    try:
        # Validar que el ID sea válido
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="ID inválido")

        # Convertir el body en un diccionario y eliminar campos nulos
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")

        result =await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        print("Resultado update_one:", result.raw_result)
        return {"message": "Usuario actualizado correctamente"}
    except Exception as e:
        print(f" ERROR AL ACTUALIZAR USUARIO: {e}") 
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/users/register", response_model=User)
async def register_user(new_user: UserRegister):
    # Validar que las contraseñas coincidan
    if new_user.contrasena != new_user.confirmar_contrasena:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")

    # Verificar si ya existe el correo en la base de datos
    existing_user = await users_collection.find_one({"correo": new_user.correo})
    if existing_user:
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    # Crear el nuevo usuario
    user_dict = {
        "nombres": new_user.nombres,
        "apellidos": new_user.apellidos,
        "fecha_nacimiento": new_user.fecha_nacimiento,
        "correo": new_user.correo,
        "codigo_barrio": new_user.codigo_barrio,
        "telefono": new_user.telefono,
        "direccion": new_user.direccion,
        "descripcion_habilidades": new_user.descripcion_habilidades,
        "hashed_password": hash_password(new_user.contrasena),
        "created_at": datetime.today()
    }

    # Insertar en la base de datos
    result = await users_collection.insert_one(user_dict)

    # Retornar los datos del nuevo usuario (sin la contraseña)
    user_dict["id"] = str(result.inserted_id)
    return User(**user_dict)

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
            {"nombres": 1, "apellidos": 1}
        )

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        nombre_completo = f"{user['nombres']} {user['apellidos']}"
        return {
            "nombre_completo": nombre_completo
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener nombre del usuario: {str(e)}")