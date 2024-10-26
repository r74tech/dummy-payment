from fastapi import FastAPI
from app.auth import router as auth_router
from app.payments import router as payments_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(payments_router, prefix="/payments")
