from fastapi.testclient import TestClient
from fastapi import FastAPI
from pyodmongo import AsyncDbEngine
from fast_crud import init_fast_crud, FastCrud
from typing import ClassVar
import pytest

app = FastAPI()

engine = AsyncDbEngine(mongo_uri="mongodb://localhost:27017", db_name="TestDB")


class Product(FastCrud):
    name: str
    code: str
    quantity: int = 0
    _collection: ClassVar = "products"


init_fast_crud(app, engine)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as _client:
        yield _client


# @pytest_asyncio.fixture(scope="session", autouse=True)
# async def clear_db():
#     await engine._client.drop_database("TestDB")
#     yield
#     await engine._client.drop_database("TestDB")
