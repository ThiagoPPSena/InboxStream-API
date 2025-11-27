from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_db
from src.repositories.emails import EmailRepository
from src.services.emails import EmailService
from src.schemas.emails import Email as EmailSchema

logger = logging.getLogger("inboxstream.routers.emails")
router = APIRouter(tags=["Emails"])


def get_email_repo(db: AsyncSession = Depends(get_db)) -> EmailRepository:
    return EmailRepository(db)


def get_email_service(repo: EmailRepository = Depends(get_email_repo)) -> EmailService:
    return EmailService(repo)


@router.post("/emails")
async def ingest_email(
    email_data: EmailSchema,
    email_service: EmailService = Depends(get_email_service),
):
    """
    Recebe um novo e-mail do sistema externo, salva no DB e envia notificação.
    """
    logger.info("ingest_email called")
    logger.debug("payload: %s", email_data.model_dump())

    new_email = await email_service.ingest_email(email_data.model_dump())

    logger.info("email ingested id=%s", getattr(new_email, "id", None))
    return new_email


@router.get("/emails")
async def get_all_emails(
    category: Optional[List[str]] = Query(
        None,
        description="Filtra e-mails por categoria. Pode repetir: ?category=a&category=b ou usar vírgula: ?category=a,b",
    ),
    initial_date: Optional[datetime] = Query(
        None, description="Filtra e-mails recebidos a partir desta data."
    ),
    end_date: Optional[datetime] = Query(
        None, description="Filtra e-mails recebidos até esta data."
    ),
    name: Optional[str] = Query(
        None, description="Busca por substring (case-insensitive) em subject e body."
    ),
    order: str = Query(
        "desc",
        regex="^(asc|desc)$",
        description="Ordem de classificação por data: 'asc' (mais antigos) ou 'desc' (mais recentes).",
    ),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    email_service: EmailService = Depends(get_email_service),
):
    """
    Retorna a lista de e-mails, com opções de filtro, ordenação e paginação.
    """
    logger.info("get_all_emails called")
    logger.debug(
        "filters: category=%s, initial_date=%s, end_date=%s, name=%s, order=%s, limit=%s, offset=%s",
        category,
        initial_date,
        end_date,
        name,
        order,
        limit,
        offset,
    )

    emails, total = await email_service.get_all_emails(
        category=category,
        initial_date=initial_date,
        end_date=end_date,
        order=order,
        limit=limit,
        offset=offset,
        name=name,
    )

    logger.info(
        "get_all_emails returning %d items (total=%d) [name=%s]",
        len(emails) if emails else 0,
        total,
        name,
    )

    return {"items": emails, "total": total} if not isinstance(emails, dict) else emails


@router.get("/emails/{email_id}")
async def get_email_detail(
    email_id: str, email_service: EmailService = Depends(get_email_service)
):
    """
    Busca um e-mail específico pelo seu ID.
    """
    logger.info("get_email_detail called id=%s", email_id)

    email = await email_service.get_email_detail(email_id)

    if email is None:
        logger.warning("E-mail não encontrado id=%s", email_id)
        raise HTTPException(status_code=404, detail="E-mail não encontrado.")

    logger.info("get_email_detail found id=%s", email_id)

    return email