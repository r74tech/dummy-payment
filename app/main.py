from fastapi import FastAPI
from app.auth import router as auth_router
from app.payments import router as payments_router
from app.webhooks import router as webhooks_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(payments_router, prefix="/payments")
app.include_router(webhooks_router, prefix="/webhook")