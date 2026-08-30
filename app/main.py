from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app.database import get_connection


app = FastAPI(title="Payment Gateway Simulator")


class PaymentRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    amount: Decimal = Field(gt=0)
    currency: Literal["TRY", "USD", "EUR", "GBP"]


class PaymentResponse(BaseModel):
    transaction_id: str
    customer_id: str
    amount: Decimal
    currency: str
    status: str
    created_at: datetime


@app.get("/")
def root():
    return {
        "application": "Payment Gateway Simulator",
        "status": "running"
    }


@app.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_payment(payment: PaymentRequest):

    transaction_id = f"TX-{uuid4()}"
    created_at = datetime.now(timezone.utc)
    payment_status = "APPROVED"

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO payments (
                    transaction_id,
                    customer_id,
                    amount,
                    currency,
                    status,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    transaction_id,
                    payment.customer_id,
                    payment.amount,
                    payment.currency,
                    payment_status,
                    created_at
                )
            )

        connection.commit()

    return PaymentResponse(
        transaction_id=transaction_id,
        customer_id=payment.customer_id,
        amount=payment.amount,
        currency=payment.currency,
        status=payment_status,
        created_at=created_at
    )


@app.get("/payments/{transaction_id}", response_model=PaymentResponse)
def get_payment(transaction_id: str):

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    transaction_id,
                    customer_id,
                    amount,
                    currency,
                    status,
                    created_at
                FROM payments
                WHERE transaction_id = %s
                """,
                (transaction_id,)
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return PaymentResponse(
        transaction_id=row[0],
        customer_id=row[1],
        amount=row[2],
        currency=row[3],
        status=row[4],
        created_at=row[5]
    )