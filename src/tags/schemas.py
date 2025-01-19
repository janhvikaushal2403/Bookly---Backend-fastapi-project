from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TagModel(BaseModel):
    uid : int
    name: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class TagCreateModel(BaseModel):
    name: str

    class Config:
        from_attributes = True

class TagAddModel(BaseModel):
    tags: List[TagCreateModel]

    class Config:
        from_attributes = True