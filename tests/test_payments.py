from fastapi.testclient import TestClient

from app.main import app
from decimal import Decimal


client = TestClient(app)


def test_create_payment():
    response = client.post(
        "/payments",
        json={
            "customer_id": "C_TEST_001",
            "amount": 100.50,
            "currency": "TRY"
        },
        headers={
            "Idempotency-Key": "TEST-CREATE-001"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["customer_id"] == "C_TEST_001"
    assert Decimal(data["amount"]) == Decimal("100.50")
    assert data["currency"] == "TRY"
    assert data["status"] == "APPROVED"
    assert "transaction_id" in data


def test_negative_amount():
    response = client.post(
        "/payments",
        json={
            "customer_id": "C_TEST_002",
            "amount": -500,
            "currency": "TRY"
        }
    )

    assert response.status_code == 422


def test_zero_amount():
    response = client.post(
        "/payments",
        json={
            "customer_id": "C_TEST_003",
            "amount": 0,
            "currency": "TRY"
        }
    )

    assert response.status_code == 422


def test_invalid_currency():
    response = client.post(
        "/payments",
        json={
            "customer_id": "C_TEST_004",
            "amount": 100,
            "currency": "TGT"
        }
    )

    assert response.status_code == 422


def test_empty_customer_id():
    response = client.post(
        "/payments",
        json={
            "customer_id": "",
            "amount": 100,
            "currency": "TRY"
        }
    )

    assert response.status_code == 422


def test_get_existing_payment():
    create_response = client.post(
        "/payments",
        json={
            "customer_id": "C_GET_001",
            "amount": 250.75,
            "currency": "EUR"
        },
        headers={
            "Idempotency-Key": "TEST-GET-001"
        }
    )

    assert create_response.status_code == 201

    created_payment = create_response.json()
    transaction_id = created_payment["transaction_id"]

    get_response = client.get(
        f"/payments/{transaction_id}"
    )

    assert get_response.status_code == 200

    payment = get_response.json()

    assert payment["transaction_id"] == transaction_id
    assert payment["customer_id"] == "C_GET_001"
    assert payment["amount"] == "250.75"
    assert payment["currency"] == "EUR"
    assert payment["status"] == "APPROVED"


def test_get_non_existing_payment():
    response = client.get(
        "/payments/TX-DOES-NOT-EXIST"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Transaction not found"


def test_get_all_payments():
    create_response = client.post(
        "/payments",
        json={
            "customer_id": "C_LIST_001",
            "amount": 350.25,
            "currency": "USD"
        },
        headers={
            "Idempotency-Key": "TEST-LIST-001"
        }
    )

    assert create_response.status_code == 201

    created_payment = create_response.json()
    transaction_id = created_payment["transaction_id"]

    response = client.get("/payments")

    assert response.status_code == 200

    payments = response.json()

    assert isinstance(payments, list)

    matching_payments = [
        payment
        for payment in payments
        if payment["transaction_id"] == transaction_id
    ]

    assert len(matching_payments) == 1

    payment = matching_payments[0]

    assert payment["customer_id"] == "C_LIST_001"
    assert payment["amount"] == "350.25"
    assert payment["currency"] == "USD"
    assert payment["status"] == "APPROVED"


def test_idempotency():
    headers = {
        "Idempotency-Key": "IDEMPOTENCY-TEST-001"
    }

    payload = {
        "customer_id": "C_IDEMPOTENCY_001",
        "amount": 100.00,
        "currency": "TRY"
    }

    first_response = client.post(
        "/payments",
        json=payload,
        headers=headers
    )

    assert first_response.status_code == 201

    first_payment = first_response.json()

    second_response = client.post(
        "/payments",
        json=payload,
        headers=headers
    )

    assert second_response.status_code == 201

    second_payment = second_response.json()

    assert (
        second_payment["transaction_id"]
        == first_payment["transaction_id"]
    )

    assert second_payment["customer_id"] == first_payment["customer_id"]
    assert Decimal(second_payment["amount"]) == Decimal(first_payment["amount"])
    assert second_payment["currency"] == first_payment["currency"]
    assert second_payment["status"] == first_payment["status"]