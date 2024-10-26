from pydantic import BaseModel

class PaymentRequest(BaseModel):
    order_id: str
    amount: float

class RefundRequest(BaseModel):
    amount: float

class Token(BaseModel):
    access_token: str
    token_type: str
