from sqlalchemy import Table, Column, Integer, String, Boolean
from config.db import meta_data, engine

users = Table('users', meta_data, 
    Column('id', Integer, primary_key=True),
    Column('name', String(255), nullable=False),
    Column('username', String(255), nullable=False),
    Column('password', String(255), nullable=False),
)

parametros = Table('parametros', meta_data, 
    Column('id', Integer, primary_key=True),
    Column('nombre', String(255), nullable=False),
    Column('descripcion', String(255), nullable=False),
    Column('estado', Boolean, nullable=False),
)

valor_parametro = Table('valor_parametro', meta_data, 
    Column('id', Integer, primary_key=True),
    Column('id_aux', String(255), nullable=False),
    Column('id_parametro', Integer, nullable=False),
    Column('valor', String(255), nullable=False),
    Column('valorx', String(255), nullable=False),
    Column('valory', String(255), nullable=False),
    Column('valorz', String(255), nullable=False),
    Column('valora', String(255), nullable=False),
    Column('estado', Boolean, nullable=False),
)
meta_data.create_all(engine)