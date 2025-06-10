from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: str
    nombres: str
    apellidos: str
    fecha_nacimiento: datetime
    correo: EmailStr
    codigo_barrio: str
    telefono: str
    direccion: str
    descripcion_habilidades: Optional[str] = None
    

class UserLogin(BaseModel):
    correo: EmailStr
    contrasena: str

class UserRegister(BaseModel):
    nombres: str
    apellidos: str
    fecha_nacimiento: datetime
    correo: EmailStr
    codigo_barrio: str
    telefono: str
    direccion: str
    contrasena: str
    confirmar_contrasena: str
    descripcion_habilidades: Optional[str] = None
    

class UserOut(BaseModel):
    nombre: str
    correo: EmailStr

#  Modelo interno (no se expone al cliente)
class UserInDB(User):
    hashed_password: str

class UserUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    correo: Optional[EmailStr] = None
    codigo_barrio: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    contrasena: Optional[str] = None
    confirmar_contrasena: Optional[str] = None
    descripcion_habilidades: Optional[str] = None
