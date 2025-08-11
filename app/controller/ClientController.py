
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.repositories.ClientRepository import ClientRepository
from app.models.ClientModel import ClientCreate, ClientUpdate, ClientResponse, ClientPublic
from app.database import get_db
from datetime import datetime
from typing import List, Optional

router = APIRouter(tags=["clientes"])

def now_iso():
    return datetime.utcnow().isoformat()

@router.get("/", response_model=dict)
def listar_clientes(db: Session = Depends(get_db)):
    try:
        clientes = ClientRepository.get_all(db)
        data = [ClientPublic.model_validate(cliente) for cliente in clientes]
        return {
            "success": True,
            "message": f"Encontrados {len(data)} clientes",
            "data": data,
            "timestamp": now_iso()
        }
    except Exception:
        return {
            "success": False,
            "message": "Erro ao listar clientes",
            "code": "INTERNAL_ERROR",
            "timestamp": now_iso()
        }

@router.get("/{client_id}", response_model=dict)
def obter_cliente(client_id: str, db: Session = Depends(get_db)):
    try:
        cliente = ClientRepository.get_by_id(db, client_id)
        if not cliente:
            return {
                "success": False,
                "message": "Cliente não encontrado.",
                "code": "NOT_FOUND",
                "timestamp": now_iso()
            }
        return {
            "success": True,
            "message": "Cliente encontrado",
            "data": ClientPublic.model_validate(cliente),
            "timestamp": now_iso()
        }
    except Exception:
        return {
            "success": False,
            "message": "Erro ao buscar cliente",
            "code": "INTERNAL_ERROR",
            "timestamp": now_iso()
        }

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente_in: ClientCreate, db: Session = Depends(get_db)):
    try:
        cliente = ClientRepository.create(db, cliente_in)
        return {
            "success": True,
            "message": "Cliente criado com sucesso",
            "data": ClientPublic.model_validate(cliente),
            "timestamp": now_iso()
        }
    except Exception as e:
        msg = str(e)
        code = "DUPLICATE_ERROR" if "unique" in msg.lower() else "INTERNAL_ERROR"
        return {
            "success": False,
            "message": msg,
            "code": code,
            "timestamp": now_iso()
        }

@router.put("/{client_id}", response_model=dict)
def atualizar_cliente(client_id: str, cliente_in: ClientUpdate, db: Session = Depends(get_db)):
    try:
        cliente = ClientRepository.update(db, client_id, cliente_in)
        return {
            "success": True,
            "message": "Cliente atualizado com sucesso",
            "data": ClientPublic.model_validate(cliente),
            "timestamp": now_iso()
        }
    except Exception as e:
        msg = str(e)
        code = "DUPLICATE_ERROR" if "unique" in msg.lower() else "INTERNAL_ERROR"
        return {
            "success": False,
            "message": msg,
            "code": code,
            "timestamp": now_iso()
        }

@router.delete("/{client_id}", response_model=dict)
def deletar_cliente(client_id: str, db: Session = Depends(get_db)):
    try:
        cliente = ClientRepository.delete(db, client_id)
        return {
            "success": True,
            "message": "Cliente deletado com sucesso",
            "timestamp": now_iso()
        }
    except Exception:
        return {
            "success": False,
            "message": "Erro ao deletar cliente",
            "code": "INTERNAL_ERROR",
            "timestamp": now_iso()
        }
