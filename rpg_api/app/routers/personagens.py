from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models import personagens_db as models
from app.schemas import rpg_schemas as schemas

# Cria o roteador base para o prefixo /personagens
router = APIRouter(prefix="/api/v1", tags=["RPG Geral"])

# --- ENDPOINTS DE RAÇAS ---

@router.post("/racas/", response_model=schemas.RacaResponse)
def criar_raca(raca: schemas.RacaCreate, db: Session = Depends(get_db)):
    nova_raca = models.RacaDB(**raca.model_dump())
    db.add(nova_raca)
    db.commit()
    db.refresh(nova_raca)
    return nova_raca

@router.get("/racas/", response_model=List[schemas.RacaResponse])
def listar_racas(db: Session = Depends(get_db)):
    return db.query(models.RacaDB).all()

# --- ENDPOINTS DE PERSONAGENS ---

@router.post("/personagens/", response_model=schemas.PersonagemResponse)
def criar_personagem(personagem: schemas.PersonagemCreate, db: Session = Depends(get_db)):
    # Verifica se a Raça e Classe existem para não quebrar o banco
    raca = db.query(models.RacaDB).filter(models.RacaDB.id == personagem.raca_id).first()
    classe = db.query(models.ClasseRPGDB).filter(models.ClasseRPGDB.id == personagem.classe_id).first()
    
    if not raca or not classe:
        raise HTTPException(status_code=404, detail="Raça ou Classe não encontrada.")
        
    novo_personagem = models.PersonagemDB(**personagem.model_dump())
    db.add(novo_personagem)
    db.commit()
    db.refresh(novo_personagem)
    return novo_personagem

@router.get("/personagens/", response_model=List[schemas.PersonagemResponse])
def listar_personagens(db: Session = Depends(get_db)):
    return db.query(models.PersonagemDB).all()