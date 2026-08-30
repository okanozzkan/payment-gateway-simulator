from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_payment():
    response = client.post(
        "/payments",
        json={
            "customer_id": "C_TEST_001",
            "amount": 100.50,
            "currency": "TRY"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["customer_id"] == "C_TEST_001"
    assert data["amount"] == "100.5"
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