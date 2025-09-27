from typing import List, Union

from fastapi import FastAPI, Path, Query

from models import (
    CatDto,
    DocumentDto,
    EntityDto,
    EventDto,
    LocationDto,
    UserDto,
    UserUserIdCatCatIdEventEventIdEntityPostRequest,
    UserUserIdCatCatIdEventPostRequest,
)

app = FastAPI(
    title='Cat API',
    version='2.1.0',
    description='API for managing cats (timeline), their documents, events, and related entities.',
)


@app.post(
    '/user', response_model=None, responses={'201': {'model': UserDto}}, tags=['User']
)
def post_user(body: UserDto) -> Union[None, UserDto]:
    """
    Create a new user
    """
    pass


@app.get('/user', response_model=List[UserDto], tags=['User'])
def get_user() -> List[UserDto]:
    """
    Get all users
    """
    pass


@app.get('/user/{user_id}', response_model=UserDto, tags=['User'])
def get_user_user_id(user_id: str = Path(..., alias='userId')) -> UserDto:
    """
    Get a specific user
    """
    pass


@app.delete('/user/{user_id}', response_model=None, tags=['User'])
def delete_user_user_id(user_id: str = Path(..., alias='userId')) -> None:
    """
    Delete a user
    """
    pass


@app.post(
    '/user/{user_id}/cat',
    response_model=None,
    responses={'201': {'model': CatDto}},
    tags=['Cat'],
)
def post_user_user_id_cat(
    user_id: str = Path(..., alias='userId'), body: CatDto = ...
) -> Union[None, CatDto]:
    """
    Create a new cat (timeline)
    """
    pass


@app.get('/user/{user_id}/cat', response_model=List[CatDto], tags=['Cat'])
def get_user_user_id_cat(user_id: str = Path(..., alias='userId')) -> List[CatDto]:
    """
    Get all cats (timelines)
    """
    pass


@app.get('/user/{user_id}/cat/{cat_id}', response_model=CatDto, tags=['Cat'])
def get_user_user_id_cat_cat_id(
    user_id: str = Path(..., alias='userId'), cat_id: str = Path(..., alias='catId')
) -> CatDto:
    """
    Get a specific cat (timeline)
    """
    pass


@app.put('/user/{user_id}/cat/{cat_id}', response_model=CatDto, tags=['Cat'])
def put_user_user_id_cat_cat_id(
    user_id: str = Path(..., alias='userId'),
    cat_id: str = Path(..., alias='catId'),
    body: CatDto = ...,
) -> CatDto:
    """
    Update a cat (timeline)
    """
    pass


@app.delete('/user/{user_id}/cat/{cat_id}', response_model=None, tags=['Cat'])
def delete_user_user_id_cat_cat_id(
    user_id: str = Path(..., alias='userId'), cat_id: str = Path(..., alias='catId')
) -> None:
    """
    Delete a cat (timeline)
    """
    pass


@app.post(
    '/user/{user_id}/cat/{cat_id}/document',
    response_model=None,
    responses={'201': {'model': DocumentDto}},
    tags=['Document'],
)
def post_user_user_id_cat_cat_id_document(
    user_id: str = Path(..., alias='userId'), cat_id: str = Path(..., alias='catId')
) -> Union[None, DocumentDto]:
    """
    Upload a document for a cat (timeline)
    """
    pass


@app.get(
    '/user/{user_id}/cat/{cat_id}/document',
    response_model=List[DocumentDto],
    tags=['Document'],
)
def get_user_user_id_cat_cat_id_document(
    user_id: str = Path(..., alias='userId'), cat_id: str = Path(..., alias='catId')
) -> List[DocumentDto]:
    """
    Get all documents for a cat (timeline)
    """
    pass


@app.get(
    '/user/{user_id}/cat/{cat_id}/document/{document_id}',
    response_model=DocumentDto,
    tags=['Document'],
)
def get_user_user_id_cat_cat_id_document_document_id(
    user_id: str = Path(..., alias='userId'),
    cat_id: str = Path(..., alias='catId'),
    document_id: str = Path(..., alias='documentId'),
) -> DocumentDto:
    """
    Get a specific document
    """
    pass


@app.post(
    '/user/{user_id}/cat/{cat_id}/entity',
    response_model=None,
    responses={'201': {'model': EntityDto}},
    tags=['Entity'],
)
def post_user_user_id_cat_cat_id_entity(
    user_id: str = Path(..., alias='userId'),
    cat_id: str = Path(..., alias='catId'),
    body: EntityDto = ...,
) -> Union[None, EntityDto]:
    """
    Create an entity (person/animal) who participates in events
    """
    pass


@app.get(
    '/user/{user_id}/cat/{cat_id}/entity',
    response_model=List[EntityDto],
    tags=['Entity'],
)
def get_user_user_id_cat_cat_id_entity(
    user_id: str = Path(..., alias='userId'), cat_id: str = Path(..., alias='catId')
) -> List[EntityDto]:
    """
    Get all entities for a cat (timeline)
    """
    pass


@app.delete('/user/{user_id}/cat/{cat_id}/entity', response_model=None, tags=['Entity'])
def delete_user_user_id_cat_cat_id_entity(
    user_id: str = Path(..., alias='userId'),
    cat_id: str = Path(..., alias='catId'),
    entity_id: str = Query(..., alias='entityId'),
) -> None:
    """
    Delete a cat's entity
    """
    pass


@app.get(
    '/user/{user_id}/cat/{cat_id}/entity/{entity_id}',
    response_model=EntityDto,
    tags=['Entity'],
)
def get_user_user_id_cat_cat_id_entity_entity_id(
    user_id: str = Path(..., alias='userId'),
    cat_id: str = Path(..., alias='catId'),
    entity_id: str = Path(..., alias='entityId'),
) -> EntityDto:
    """
    Get a specific entity
    """
    pass


@app.get(
    '/user/{user_id}/cat/{cat_id}/event', response_model=List[EventDto], tags=['Event']
)
def get_user_user_id_cat_cat_id_event(
    user_id: str = Path(..., alias='userId'), cat_id: str = Path(..., alias='catId')
) -> List[EventDto]:
    """
    Get all events for a cat (timeline)
    """
    pass


@app.post('/user/{user_id}/cat/{cat_id}/event', response_model=None, tags=['Event'])
def post_user_user_id_cat_cat_id_event(
    user_id: str = Path(..., alias='userId'),
    cat_id: str = Path(..., alias='catId'),
    body: UserUserIdCatCatIdEventPostRequest = ...,
) -> None:
    """
    Associate an existing event with a cat (timeline)
    """
    pass


@app.delete('/user/{user_id}/cat/{cat_id}/event', response_model=None, tags=['Event'])
def delete_user_user_id_cat_cat_id_event(
    user_id: str = Path(..., alias='userId'),
    cat_id: str = Path(..., alias='catId'),
    event_id: str = Query(..., alias='eventId'),
) -> None:
    """
    Delete a cat's event
    """
    pass


@app.post(
    '/user/{user_id}/cat/{cat_id}/event/{event_id}/entity',
    response_model=None,
    tags=['Entity'],
)
def post_user_user_id_cat_cat_id_event_event_id_entity(
    user_id: str = Path(..., alias='userId'),
    cat_id: str = Path(..., alias='catId'),
    event_id: str = Path(..., alias='eventId'),
    body: UserUserIdCatCatIdEventEventIdEntityPostRequest = ...,
) -> None:
    """
    Add an entity to an event (PARTICIPATES_IN)
    """
    pass


@app.get(
    '/user/{user_id}/cat/{cat_id}/location',
    response_model=List[LocationDto],
    tags=['Location'],
)
def get_user_user_id_cat_cat_id_location(
    user_id: str = Path(..., alias='userId'), cat_id: str = Path(..., alias='catId')
) -> List[LocationDto]:
    """
    Get all locations for a cat (timeline)
    """
    pass
