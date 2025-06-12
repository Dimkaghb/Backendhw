from pydantic import BaseModel

class ToDo(BaseModel):
    id: int | None = None
    name: str
    is_completed: bool