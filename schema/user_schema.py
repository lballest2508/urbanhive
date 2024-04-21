from pydantic import BaseModel

class UserSchema(BaseModel):
    id: int | None = None
    name: str
    username: str
    password: str

class UserLoginSchema(BaseModel):
    username: str
    password: str

class ParametroSchema(BaseModel):
    id: int | None = None
    nombre: str
    descripcion: str
    estado: bool

class ValorParametroSchema(BaseModel):
    id: int | None = None
    id_aux: str
    id_parametro: int
    valor: str
    valorx: str
    valory: str
    valorz: str
    valora: str
    estado: bool