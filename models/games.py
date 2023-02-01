from pydantic import BaseModel
from typing import Union

class Game(BaseModel):
    name: str
    status: Union[bool, None] = None
    price: float
    lowest: Union[float, None] = None
    img: Union[str, None] = None
    page: Union[str, None] = None
    genres: Union[str, None] = None