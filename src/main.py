from fastapi import FastAPI
from src.routers import emails as email_router

app = FastAPI(
    title="InboxStream API",
    version="v1",
    description="API para ingestão, categorização e notificação em tempo real de e-mails."
)

app.include_router(email_router.router, prefix="/api/v1")

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "InboxStream API is running!"}

# Para rodar: uvicorn src.main:app --reload