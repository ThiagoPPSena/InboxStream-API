from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime

from src.database.base import get_db
from src.repositories.emails import EmailRepository
from src.services.emails import EmailService
from src.schemas.emails import Email as EmailSchema
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Emails"])

def get_email_repo(db: AsyncSession = Depends(get_db)) -> EmailRepository:
    return EmailRepository(db)

def get_email_service(repo: EmailRepository = Depends(get_email_repo)) -> EmailService:
    return EmailService(repo)

@router.post("/emails")
async def ingest_email(
    email_data: EmailSchema, 
    email_service: EmailService = Depends(get_email_service)
):
    """
    Recebe um novo e-mail do sistema externo, salva no DB e envia notificação.
    """
    new_email = await email_service.ingest_email(email_data.model_dump())

    return new_email

@router.get("/emails")
async def get_all_emails(
    category: Optional[str] = Query(None, description="Filtra e-mails por categoria."),
    initial_date: Optional[datetime] = Query(None, description="Filtra e-mails recebidos a partir desta data."),
    end_date: Optional[datetime] = Query(None, description="Filtra e-mails recebidos até esta data."),
    order: str = Query("desc", regex="^(asc|desc)$", description="Ordem de classificação por data: 'asc' (mais antigos) ou 'desc' (mais recentes)."),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    
    email_service: EmailService = Depends(get_email_service),
):
    """
    Retorna a lista de e-mails, com opções de filtro, ordenação e paginação.
    """
    return await email_service.get_all_emails(
        category=category,
        initial_date=initial_date,
        end_date=end_date,
        order=order,
        limit=limit,
        offset=offset,
    )

@router.get("/emails/{email_id}")
async def get_email_detail(
    email_id: str,
    email_service: EmailService = Depends(get_email_service),
):
    """
    Busca um e-mail específico pelo seu ID.
    """
    email = await email_service.get_email_detail(email_id)
    
    if email is None:
        raise HTTPException(status_code=404, detail="E-mail não encontrado.")
    
    return email