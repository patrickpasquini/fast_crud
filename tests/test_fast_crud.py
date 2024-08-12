import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def product_data():
    return {"name": "Test Product", "code": "T001", "quantity": 10}


@pytest.fixture
def product_id(client: TestClient, product_data: dict):
    response = client.post("/product", json=product_data)
    return response.json().get("upserted_ids").get("0")


def test_create_route(client: TestClient, product_data: dict):
    response = client.post("/product", json=product_data)
    assert response.status_code == 201


def test_get_one_route(client: TestClient, product_id: str):
    response = client.get(f"/product/{product_id}")
    assert response.status_code == 200
    assert response.json().get("id") == product_id


def test_get_many_route(client: TestClient):
    response = client.get("/product")
    assert response.status_code == 200


def test_update_route(client: TestClient, product_id: str):
    updated_data = {
        "name": "Updated Product",
        "code": "T001",
        "quantity": 15,
        "margin": 7.0,
    }
    response = client.put(f"/product/{product_id}", json=updated_data)
    assert response.status_code == 200


def test_delete_route(client: TestClient, product_id: str):
    response = client.delete(f"/product/{product_id}")
    assert response.status_code == 200
    assert response.json().get("deleted_count") == 1
    response = client.get(f"/product/{product_id}")
    assert response.status_code == 404
