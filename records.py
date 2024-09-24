from pydantic import BaseModel


class Station(BaseModel):
    id: int
    name: str
    address: str
    num_bikes_available: int | None = None
