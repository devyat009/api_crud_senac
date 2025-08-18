import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from app.models.models import Client
from app.models.ClientModel import ClientCreate, ClientUpdate
from app.utils.ErrorModel import create_error_response
from fastapi import HTTPException, status
from datetime import datetime

class ClientRepository:
    @staticmethod
    def get_all(db: Session):
        return db.query(Client).filter(Client.ativo == True).all()

    @staticmethod
    def get_by_id(db: Session, client_id: str):
        return db.query(Client).filter(Client.id_client == client_id, Client.ativo == True).first()

    @staticmethod
    def get_by_email_cpf_cnpj(db: Session, email: str = None, cpf: str = None, cnpj: str = None):
        return db.query(Client).filter(
            or_(Client.email == email, Client.cpf == cpf, Client.cnpj == cnpj),
            Client.ativo == True
        ).first()

    @staticmethod
    def create(db: Session, client_in: ClientCreate):
        # Verifica unicidade de email, cpf, cnpj
        if ClientRepository.get_by_email_cpf_cnpj(db, client_in.email, client_in.cpf, client_in.cnpj):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=create_error_response(
                    message="Email, CPF ou CNPJ já cadastrado.",
                    field="email/cpf/cnpj",
                    code="unique_violation"
                )
            )
        db_client = Client(
            id_client=str(uuid.uuid4()),
            nome=client_in.nome,
            cpf=client_in.cpf,
            cnpj=client_in.cnpj,
            email=client_in.email,
            endereco=client_in.endereco,
            telefone=client_in.telefone,
            data_nascimento=client_in.data_nascimento,
            perfil=client_in.perfil,
            ativo=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_client)
        try:
            db.commit()
            db.refresh(db_client)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=create_error_response(
                    message="Violação de unicidade ao criar cliente.",
                    field="email/cpf/cnpj",
                    code="unique_violation"
                )
            )
        return db_client

    @staticmethod
    def update(db: Session, client_id: str, client_in: ClientUpdate):
        db_client = ClientRepository.get_by_id(db, client_id)
        if not db_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    message="Cliente não encontrado.",
                    field="id_client",
                    code="not_found"
                )
            )
        # Verifica unicidade se email/cpf/cnpj mudaram
        if (client_in.email and client_in.email != db_client.email) or \
           (client_in.cpf and client_in.cpf != db_client.cpf) or \
           (client_in.cnpj and client_in.cnpj != db_client.cnpj):
            existing = ClientRepository.get_by_email_cpf_cnpj(db, client_in.email, client_in.cpf, client_in.cnpj)
            if existing and existing.id_client != client_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=create_error_response(
                        message="Email, CPF ou CNPJ já cadastrado.",
                        field="email/cpf/cnpj",
                        code="unique_violation"
                    )
                )
        for field, value in client_in.model_dump(exclude_unset=True).items():
            setattr(db_client, field, value)
        db_client.updated_at = datetime.utcnow()
        try:
            db.commit()
            db.refresh(db_client)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=create_error_response(
                    message="Violação de unicidade ao atualizar cliente.",
                    field="email/cpf/cnpj",
                    code="unique_violation"
                )
            )
        return db_client

    @staticmethod
    def delete(db: Session, client_id: str):
        db_client = ClientRepository.get_by_id(db, client_id)
        if not db_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    message="Cliente não encontrado.",
                    field="id_client",
                    code="not_found"
                )
            )
        db_client.ativo = False
        db_client.updated_at = datetime.utcnow()
        db.commit()
        return db_client
