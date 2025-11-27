from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import logging

from sqlalchemy import select, desc, asc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result

from src.database.models import Email

logger = logging.getLogger("inboxstream.repositories.emails")

class EmailRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_filtered_emails(
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
        Retorna (items, total) aplicando filtros:
         - category: aceita lista e valores separados por vírgula
         - initial_date / end_date
         - order: "asc" | "desc"
         - limit / offset para paginação
         - name: busca case-insensitive por substring em subject e body
        """
        stmt = select(Email)

        # categorias: suporta ?category=a&category=b e ?category=a,b
        cats: List[str] = []
        if category:
            for item in category:
                cats.extend([c.strip() for c in item.split(",") if c.strip()])
            if cats:
                lowered = [c.lower() for c in cats]
                stmt = stmt.where(func.lower(Email.category).in_(lowered))

        # datas
        if initial_date:
            stmt = stmt.where(Email.date >= initial_date)
        if end_date:
            stmt = stmt.where(Email.date <= end_date)

        # busca em subject e body
        if name:
            pattern = f"%{name.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Email.subject).like(pattern),
                    func.lower(Email.body).like(pattern),
                )
            )

        # ordenação e paginação
        stmt = stmt.order_by(desc(Email.date) if order == "desc" else asc(Email.date))
        stmt = stmt.limit(limit).offset(offset)

        result: Result = await self.db_session.execute(stmt)
        items: List[Email] = list(result.scalars().all())

        # contador com mesmos filtros (sem limit/offset)
        count_stmt = select(func.count()).select_from(Email)
        if cats:
            count_stmt = count_stmt.where(func.lower(Email.category).in_([c.lower() for c in cats]))
        if initial_date:
            count_stmt = count_stmt.where(Email.date >= initial_date)
        if end_date:
            count_stmt = count_stmt.where(Email.date <= end_date)
        if name:
            pattern = f"%{name.strip().lower()}%"
            count_stmt = count_stmt.where(
                or_(
                    func.lower(Email.subject).like(pattern),
                    func.lower(Email.body).like(pattern),
                )
            )

        count_result = await self.db_session.execute(count_stmt)
        total: int = int(count_result.scalar_one())

        logger.debug("get_filtered_emails: returned %d items (total=%d) [cats=%s name=%s]", len(items), total, cats, name)
        return items, total

    async def get_email_by_id(self, email_id: str) -> Optional[Email]:
        stmt = select(Email).where(Email.id == email_id)
        return await self.db_session.scalar(stmt)

    async def create_email(self, email_data: Dict[str, Any]) -> Email:
        new_email = Email(**email_data)
        self.db_session.add(new_email)
        await self.db_session.commit()
        await self.db_session.refresh(new_email)
        return new_email