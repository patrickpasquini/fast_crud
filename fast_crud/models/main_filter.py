from pydantic import BaseModel


class MainFilter(BaseModel):
    current_page: int = 1
    docs_per_page: int = 10
