from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import json
from datetime import datetime

# Simulação de um "banco de dados" na memória para testes
FAKE_DB = [
    {
        "id": "1",
        "assunto": "Fatura Atrasada",
        "categoria": "Financeiro",
        "data_recepcao": datetime(2025, 10, 15, 10, 0, 0) # Data mais antiga
    },
    {
        "id": "2",
        "assunto": "Reunião de Marketing",
        "categoria": "Marketing",
        "data_recepcao": datetime(2025, 10, 16, 14, 30, 0)
    },
    {
        "id": "3",
        "assunto": "Notícia Urgente",
        "categoria": "Geral",
        "data_recepcao": datetime(2025, 10, 18, 9, 0, 0) # Data mais recente
    },
]

router = APIRouter(tags=["Emails"])

@router.post("/emails")
async def ingest_email(email_data):
    """
    Recebe um novo e-mail do sistema externo, salva no DB e envia notificação.
    """
    # 1. Lógica de DB (substitua isso pela sua chamada ao MongoDB/PostgreSQL)
    new_id = len(FAKE_DB) + 1
    new_email = {"id": str(new_id), "email": email_data.model_dump()}
    FAKE_DB.append(new_email)

    return new_email

@router.get("/emails")
def get_all_emails(
    category: Optional[str] = Query(None, description="Filtra e-mails por categoria."),
    initial_date: Optional[datetime] = Query(None, description="Filtra e-mails recebidos a partir desta data."),
    end_date: Optional[datetime] = Query(None, description="Filtra e-mails recebidos até esta data."),
    order: str = Query("desc", regex="^(asc|desc)$", description="Ordem de classificação por data: 'asc' (mais antigos) ou 'desc' (mais recentes)."),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
):
    """
    Retorna a lista de e-mails, com opções de filtro, ordenação e paginação.
    """
    
    # 1. Aplicar Filtros
    filtered_emails = FAKE_DB
    
    # Filtro por Categoria
    if category:
        # Note que a categoria é case-insensitive
        filtered_emails = [
            e for e in filtered_emails 
            if e.get("categoria", "").lower() == category.lower()
        ]

    # Filtro por Data (Intervalo)
    if initial_date:
        filtered_emails = [
            e for e in filtered_emails 
            if e.get("data_recepcao") and e["data_recepcao"] >= initial_date
        ]

    if end_date:
        filtered_emails = [
            e for e in filtered_emails 
            if e.get("data_recepcao") and e["data_recepcao"] <= end_date
        ]
        
    # 2. Aplicar Ordenação
    # Usa 'data_recepcao' como chave e inverte a ordem se 'ordem' for 'desc'
    reverse_sort = (order == "desc")
    
    # Ordena: assume que 'data_recepcao' existe e é um datetime
    sorted_emails = sorted(
        filtered_emails,
        key=lambda x: x.get("data_recepcao", datetime.min), # Use datetime.min como fallback seguro
        reverse=reverse_sort
    )
    
    # 3. Aplicar Paginação
    start = offset
    end = offset + limit
    paginated_emails = sorted_emails[start:end]

    return paginated_emails

@router.get("/emails/{email_id}")
def get_email_detail(email_id: str):
    """
    Busca um e-mail específico pelo seu ID.
    """
    try:
        email = FAKE_DB[int(email_id) - 1]
        return email
    except IndexError:
        raise HTTPException(status_code=404, detail="E-mail não encontrado.")
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de e-mail inválido.")