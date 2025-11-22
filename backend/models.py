from typing import List, Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import String, JSON
from datetime import datetime


class LinkBase(SQLModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    resource_type: str = "article"


class Link(LinkBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tags: Optional[List[str]] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    read: bool = Field(default=False, nullable=False)


class LinkCreate(LinkBase):
    pass


class LinkRead(LinkBase):
    id: int
    tags: Optional[List[str]] = None
    created_at: datetime
    read: bool
