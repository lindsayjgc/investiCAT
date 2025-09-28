from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentDto(BaseModel):
    id: Optional[str] = None
    filename: Optional[str] = None


class LocationDto(BaseModel):
    id: Optional[str] = None
    address: Optional[str] = None


class UserDto(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class EntityDto(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None


class DocumentPostRequest(BaseModel):
    file: Optional[bytes] = None
    filename: Optional[str] = Field(
        None, description='The name of the file being uploaded'
    )


class EventPostRequest(BaseModel):
    eventId: Optional[str] = None


class EntityPostRequest(BaseModel):
    entityId: Optional[str] = None


class EventDto(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[LocationDto] = None
    entities: Optional[List[EntityDto]] = None


class CatDto(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    ownerId: Optional[str] = None
    documents: Optional[List[DocumentDto]] = None
    events: Optional[List[EventDto]] = None
