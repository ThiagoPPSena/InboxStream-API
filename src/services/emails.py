from typing import Optional, List
from datetime import datetime
from src.repositories.emails import EmailRepository 
from src.database.models import Email
from src.services.websockets import manager
from src.schemas.emails import Email as EmailSchema


class EmailService:
    def __init__(self, repository: EmailRepository):
        self.repo = repository

    async def get_all_emails(
        self,
        category: Optional[str],
        initial_date: Optional[datetime],
        end_date: Optional[datetime],
        order: str,
        limit: int,
        offset: int,
    ) -> List[Email]:
        
        emails = await self.repo.get_filtered_emails(
            category=category,
            initial_date=initial_date,
            end_date=end_date,
            order=order,
            limit=limit,
            offset=offset,
        )
        
        return emails

    async def get_email_detail(self, email_id: int) -> Optional[Email]:
        return await self.repo.get_email_by_id(email_id)

    async def ingest_email(self, email_data: EmailSchema) -> Email:
        
        await manager.broadcast(email_data)

        new_email = await self.repo.create_email(email_data)
        
        return new_email