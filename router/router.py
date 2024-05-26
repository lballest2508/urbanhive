from fastapi import APIRouter, Response, Depends, HTTPException, status
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from schema.user_schema import (
    PasswordSchema,
    UserSchema,
    UserLoginSchema,
    ParametroSchema,
    ValorParametroSchema,
    UserEditSchema,
)
from config.db import engine
from model.users import users, parametros, valor_parametro
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from config import SECRET_KEY, ALGORITHM
from jose import JWTError

user = APIRouter()
parametro = APIRouter()
valores_parametro = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/user/login")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=60
        )  # Token expira en 15 minutos
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalido")


@user.get("/")
def read_root(current_user: str = Depends(get_current_user)):
    return {"message": "Hello World"}


# endpoints del modulo de users
@user.get("/api/user", response_model=List[UserSchema])
def get_all_user(current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()
        columns = users.columns.keys()
        user_list = [dict(zip(columns, row)) for row in result]

        return user_list


@user.post("/api/user", status_code=HTTP_201_CREATED)
def create_user(data_user: UserSchema, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        new_user = data_user.model_dump()
        new_user["password"] = generate_password_hash(
            data_user.password, "pbkdf2:sha256:30", 20
        )
        conn.execute(users.insert().values(new_user))
        conn.commit()
        return Response(status_code=HTTP_201_CREATED)


@user.get("/api/user/{id}", response_model=UserSchema)
def get_user_by_id(id: int, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(users.select().where(users.c.id == id)).fetchone()
        columns = users.columns.keys()
        user = dict(zip(columns, result))
        return user


@user.put("/api/user/{id}", response_model=UserEditSchema)
def update_user(
    data_update: UserEditSchema, id: int, current_user: str = Depends(get_current_user)
):
    with engine.connect() as conn:

        conn.execute(
            users.update()
            .values(
                name=data_update.name,
                username=data_update.username,
            )
            .where(users.c.id == id)
        )
        conn.commit()

        result = conn.execute(users.select().where(users.c.id == id)).fetchone()
        columns = users.columns.keys()
        user = dict(zip(columns, result))
        return user


@user.put("/api/user/{id}/password", response_model=PasswordSchema)
def update_user(
    data_update: PasswordSchema, id: int, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        encrypted_password = generate_password_hash(data_update.password, "pbkdf2:sha256:30", 20)

        conn.execute(users.update().values(password=encrypted_password).where(users.c.id == id))
        conn.commit()

        result = conn.execute(users.select().where(users.c.id == id)).fetchone()
        columns = users.columns.keys()
        user = dict(zip(columns, result))
        return user


@user.delete("/api/user/{id}")
def delete_user(id: int, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        conn.execute(users.delete().where(users.c.id == id))
        conn.commit()
        return Response(status_code=HTTP_204_NO_CONTENT)


@user.post("/api/user/login")
# Esta linea se habilita solo para cuando se vayan hacer pruebas en la documentacion en el backend
# def login_user(data_login: OAuth2PasswordRequestForm = Depends()):
# Esta linea se habilita solo para cuando se vaya a utilizar el manejo de los datos desde el frontend
def login_user(data_login: UserLoginSchema):
    with engine.connect() as conn:
        result = conn.execute(
            users.select().where(users.c.username == data_login.username)
        ).fetchone()
        if result is None or not check_password_hash(
            result.password, data_login.password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        columns = users.columns.keys()
        user_data = dict(zip(columns, result))
        access_token_expires = timedelta(minutes=15)
        access_token = create_access_token(
            data={"sub": user_data["username"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "user": user_data}


# endpoints del modulo de parametros
@parametro.get("/api/parametros")
def get_parametros(current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(parametros.select()).fetchall()
        columns = parametros.columns.keys()
        parametros_list = [dict(zip(columns, row)) for row in result]

        return parametros_list


@parametro.get("/api/parametros/{id}")
def get_parametro_by_id(id: int, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(
            parametros.select().where(parametros.c.id == id)
        ).fetchone()
        columns = parametros.columns.keys()
        parametro = dict(zip(columns, result))
        return parametro


@parametro.post("/api/parametros")
def create_parametro(
    data_parametro: ParametroSchema, current_user: str = Depends(get_current_user)
):
    with engine.connect() as conn:
        new_parametro = data_parametro.model_dump()
        conn.execute(parametros.insert().values(new_parametro))
        conn.commit()
        return Response(status_code=HTTP_201_CREATED)


@parametro.put("/api/parametros/{id}")
def update_parametro(
    data_update: ParametroSchema, id: int, current_user: str = Depends(get_current_user)
):
    with engine.connect() as conn:
        conn.execute(
            parametros.update()
            .values(
                nombre=data_update.nombre,
                descripcion=data_update.descripcion,
                estado=data_update.estado,
            )
            .where(parametros.c.id == id)
        )
        conn.commit()

        result = conn.execute(
            parametros.select().where(parametros.c.id == id)
        ).fetchone()
        columns = parametros.columns.keys()
        parametro = dict(zip(columns, result))
        return parametro


@parametro.delete("/api/parametros/{id}")
def delete_parametro(id: int, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        conn.execute(parametros.delete().where(parametros.c.id == id))
        conn.commit()
        return Response(status_code=HTTP_204_NO_CONTENT)


# endpoints del modulo de valores_parametro
@valores_parametro.get("/api/valores_parametro")
def get_valores_parametro(current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(valor_parametro.select()).fetchall()
        columns = valor_parametro.columns.keys()
        valores_parametro_list = [dict(zip(columns, row)) for row in result]

        return valores_parametro_list


@valores_parametro.get("/api/valores_parametro/{id}")
def get_valor_parametro_by_id(id: int, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(
            valor_parametro.select().where(valor_parametro.c.id == id)
        ).fetchone()
        columns = valor_parametro.columns.keys()
        valor_parametro_data = dict(zip(columns, result))
        return valor_parametro_data


@valores_parametro.post("/api/valores_parametro")
def create_valor_parametro(
    data_valor_parametro: ValorParametroSchema,
    current_user: str = Depends(get_current_user),
):
    with engine.connect() as conn:
        new_valor_parametro = data_valor_parametro.model_dump()
        conn.execute(valor_parametro.insert().values(new_valor_parametro))
        conn.commit()
        return Response(status_code=HTTP_201_CREATED)


@valores_parametro.put("/api/valores_parametro/{id}")
def update_valor_parametro(
    data_update: ValorParametroSchema,
    id: int,
    current_user: str = Depends(get_current_user),
):
    with engine.connect() as conn:
        conn.execute(
            valor_parametro.update()
            .values(
                id_aux=data_update.id_aux,
                id_parametro=data_update.id_parametro,
                valor=data_update.valor,
                valorx=data_update.valorx,
                valory=data_update.valory,
                valorz=data_update.valorz,
                valora=data_update.valora,
                estado=data_update.estado,
            )
            .where(valor_parametro.c.id == id)
        )
        conn.commit()

        result = conn.execute(
            valor_parametro.select().where(valor_parametro.c.id == id)
        ).fetchone()
        columns = valor_parametro.columns.keys()
        valor_parametro_data = dict(zip(columns, result))
        return valor_parametro_data


@valores_parametro.delete("/api/valores_parametro/{id}")
def delete_valor_parametro(id: int, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        conn.execute(valor_parametro.delete().where(valor_parametro.c.id == id))
        conn.commit()
        return Response(status_code=HTTP_204_NO_CONTENT)


@valores_parametro.get("/api/valores_parametro/parametro/{id}")
def get_valor_parametro_by_parametro(
    id: int, current_user: str = Depends(get_current_user)
):
    with engine.connect() as conn:
        result = conn.execute(
            valor_parametro.select().where(valor_parametro.c.id_parametro == id)
        ).fetchall()
        columns = valor_parametro.columns.keys()
        valores_parametro_list = [dict(zip(columns, row)) for row in result]

        return valores_parametro_list
