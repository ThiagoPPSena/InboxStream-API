from fastapi import FastAPI
from src.routers import emails as email_router
from src.routers import websockets as websocket_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="InboxStream API",
    version="v1",
    description="API para ingestão, categorização e notificação em tempo real de e-mails."
)


origins = [
    "http://localhost:5173",   
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,
    allow_methods=["*"],            
    allow_headers=["*"],            
)


app.include_router(email_router.router, prefix="/api/v1")
app.include_router(websocket_router.router, prefix="/api/v1")

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "InboxStream API is running!"}

# Para rodar: uvicorn src.main:app --reload