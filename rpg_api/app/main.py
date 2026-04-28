from fastapi import FastAPI
from app.db.database import Base, engine
from app.routers import personagens


# Inicia a aplicação FastAPI
app = FastAPI(
    title="API do Sistema de RPG",
    description="Motor de RPG de Mesa com simulação de batalhas em turnos.",
    version="1.0.0"
)

# Inclui as rotas que criamos
app.include_router(personagens.router)

@app.get("/")
def root():
    return {"mensagem": "Bem-vindo à API do Sistema de RPG! Acesse /docs para a documentação interativa."}