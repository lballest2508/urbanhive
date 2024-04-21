from fastapi import FastAPI
from router.router import user, parametro, valores_parametro

app = FastAPI()

app.include_router(user)
app.include_router(parametro)
app.include_router(valores_parametro)