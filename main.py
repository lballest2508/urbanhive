from fastapi import FastAPI
from router.router import user, parametro, valores_parametro
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(user)
app.include_router(parametro)
app.include_router(valores_parametro)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Isaac bola de cacho de esta manera se integra con React
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)