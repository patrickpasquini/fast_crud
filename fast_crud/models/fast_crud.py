from .main_filter import MainFilter
from pyodmongo import DbModel, AsyncDbEngine, DbResponse, ResponsePaginate, Id
from pyodmongo.queries import mount_query_filter, eq
from fastapi import APIRouter, HTTPException, status, Request, Depends
from typing import ClassVar, Optional

model_registry: list["FastCrud"] = []


class FastCrud(DbModel):
    engine: ClassVar[Optional[AsyncDbEngine]] = None
    _collection: ClassVar[str]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        model_registry.append(cls)

    @classmethod
    def register_routes(cls, router: APIRouter):
        model_name = cls.__name__.lower()

        @router.post(
            f"/{model_name}",
            status_code=status.HTTP_201_CREATED,
            response_model=DbResponse,
        )
        async def create(doc: cls):
            return await cls.engine.save(obj=doc)

        @router.get(f"/{model_name}", response_model=ResponsePaginate)
        async def get_many(request: Request, main_filter: MainFilter = Depends()):
            query, sort = mount_query_filter(
                Model=cls, items=request.query_params._dict
            )
            response = await cls.engine.find_many(
                Model=cls,
                query=query,
                current_page=main_filter.current_page,
                docs_per_page=main_filter.docs_per_page,
                paginate=True,
                sort=sort,
            )
            if response.docs != []:
                return response
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documents not found",
            )

        @router.get(f"/{model_name}/{{id}}", response_model=cls | None)
        async def get_one(id: Id):
            document = await cls.engine.find_one(Model=cls, query=eq(cls.id, id))
            if document:
                return document
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        @router.put(f"/{model_name}/{{id}}", response_model=DbResponse)
        async def update(id: Id, item: cls):
            item.id = id
            response = await cls.engine.save(item)
            if response.modified_count > 0:
                return response
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found or no changes applied",
            )

        @router.delete(f"/{model_name}/{{id}}", response_model=DbResponse)
        async def delete(id: Id):
            response = await cls.engine.delete(
                Model=cls, query=eq(cls.id, id), delete_one=True
            )
            if response.deleted_count > 0:
                return response
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
