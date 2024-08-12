from ..models.fast_crud import model_registry
from pyodmongo import AsyncDbEngine
from fastapi import FastAPI, APIRouter


def init_fast_crud(app: FastAPI, engine: AsyncDbEngine):
    global model_registry

    for model in model_registry:
        router = APIRouter(tags=[model.__name__])
        model.engine = engine
        model.register_routes(router)
        app.include_router(router)
