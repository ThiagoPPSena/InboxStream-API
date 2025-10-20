from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Email(BaseModel):
    """
    Schema de requisição usado para receber dados no POST /emails.
    """
    id: str = Field(..., description="ID único do e-mail fornecido pelo sistema externo.")
    subject: str = Field(..., description="Assunto principal do e-mail.")
    body: Optional[str] = Field(None, description="Corpo do e-mail.")
    category: str = Field("Geral", description="Categoria do e-mail.")
    date: datetime = Field(..., description="Timestamp de quando o e-mail foi enviado pelo remetente.")