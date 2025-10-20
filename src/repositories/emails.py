from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from src.database.models import Email 

class EmailRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_filtered_emails(
        self,
        category: Optional[str],
        initial_date: Optional[datetime],
        end_date: Optional[datetime],
        order: str,
        limit: int,
        offset: int,
    ) -> List[Email]:
        
        emails = select(Email)
        
        if category:
            emails = emails.where(Email.category.ilike(category))
        
        if initial_date:
            emails = emails.where(Email.date >= initial_date)
            
        if end_date:
            emails = emails.where(Email.date <= end_date)
            
        if order == "desc":
            emails = emails.order_by(desc(Email.date))
        else:
            emails = emails.order_by(asc(Email.date))
            
        emails = emails.limit(limit).offset(offset)
        
        result: Result = await self.db_session.execute(emails)
        
        return list(result.scalars().all())

    async def get_email_by_id(self, email_id: str) -> Optional[Email]:
        email = select(Email).where(Email.id == email_id)
        
        return await self.db_session.scalar(email)
        
    async def create_email(self, email_data: Dict[str, Any]) -> Email:
        new_email = Email(**email_data)
        self.db_session.add(new_email)
        await self.db_session.commit()
        await self.db_session.refresh(new_email)
        return new_email