from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime

from src.repositories.emails import EmailRepository
from src.database.models import Email
from src.services.websockets import manager


class EmailService:
    def __init__(self, repository: EmailRepository):
        self.repo = repository

    async def get_all_emails(
        self,
        category: Optional[List[str]],
        initial_date: Optional[datetime],
        end_date: Optional[datetime],
        order: str,
        limit: int,
        offset: int,
        name: Optional[str] = None,
    ) -> Tuple[List[Email], int]:
        """
        Encaminha filtros para o repositório e retorna (items, total).
        """
        emails, total = await self.repo.get_filtered_emails(
            category=category,
            initial_date=initial_date,
            end_date=end_date,
            order=order,
            limit=limit,
            offset=offset,
            name=name,
        )

        return emails, total

    async def get_email_detail(self, email_id: str) -> Optional[Email]:
        return await self.repo.get_email_by_id(email_id)

    async def ingest_email(self, email_data: Dict[str, Any]) -> Email:
        """
        email_data deve ser um dict com os campos do Email (ex.: result de model_dump()).
        """
        await manager.broadcast(email_data)
        new_email = await self.repo.create_email(email_data)
        return new_email