from typing import List, Union
from fastapi import HTTPException
from fastapi import FastAPI, Path, Query

from models import (
    CatDto,
    DocumentDto,
    EntityDto,
    EventDto,
    LocationDto,
    UserDto,
    EntityPostRequest,
    EventPostRequest,
)

from db import (
    create_user,
    fetch_user,
    fetch_users,
    remove_user,
    create_cat,
    fetch_cats,
    fetch_cat,
    update_cat,
    remove_cat,
    create_document,
    fetch_documents,
    fetch_document,
    create_entity,
    fetch_entities,
    remove_entity,
    fetch_entity,
    fetch_events,
    associate_event_with_cat,
    remove_event,
    add_entity_to_event_db,
    fetch_locations,
)

app = FastAPI(
    title='Cat API',
    version='2.1.0',
    description='API for managing cats (timeline), their documents, events, and related entities.',
)

# ------------------------
# User Endpoints
# ------------------------

@app.post(
    '/user', response_model=None, responses={'201': {'model': UserDto}}, tags=['User']
)
def post_user(body: UserDto) -> Union[None, UserDto]:
    """
    Create a new user
    """
    user_node = create_user(body.name, body.email)
    if not user_node:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return {"message": "User created", "user": user_node}

@app.get('/user', response_model=List[UserDto], tags=['User'])
def get_users() -> List[UserDto]:
    """
    Get all users
    """
    list_of_users = fetch_users()
    if not list_of_users:
        return []
    return list_of_users
    


@app.get('/user/{user_id}', response_model=UserDto, tags=['User'])
def get_user(user_id: str = Path(...)) -> UserDto:
    """
    Get a specific user
    """
    user_node = fetch_user(user_id)
    if not user_node:
        raise HTTPException(status_code=404, detail="User not found")
    return user_node


@app.delete('/user/{user_id}', response_model=None, tags=['User'])
def delete_user(user_id: str = Path(...)) -> None:
    """
    Delete a user
    """
    ok = remove_user(user_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to delete user")
    return {"message": "User deleted"}

# ------------------------
# Cat Endpoints
# ------------------------

@app.post(
    '/user/{user_id}/cat',
    response_model=None,
    responses={'201': {'model': CatDto}},
    tags=['Cat'],
)
def post_cat(
    user_id: str = Path(...), body: CatDto = ...
) -> Union[None, CatDto]:
    """
    Create a new cat (timeline)
    """
    user_node = fetch_user(user_id)
    if not user_node:
        raise HTTPException(status_code=404, detail="User not found")

    new_cat_data = create_cat(user_id, body)
    if not new_cat_data:
        raise HTTPException(status_code=500, detail="Failed to create cat timeline")

    return new_cat_data


@app.get('/user/{user_id}/cat', response_model=List[CatDto], tags=['Cat'])
def get_cats(user_id: str = Path(...)) -> List[CatDto]:
    """
    Get all cats (timelines) for a specific user.
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    list_of_cats = fetch_cats(user_id)
    return list_of_cats if list_of_cats else []


@app.get('/user/{user_id}/cat/{cat_id}', response_model=CatDto, tags=['Cat'])
def get_cat(
    user_id: str = Path(...), cat_id: str = Path(...)
) -> CatDto:
    """
    Get a specific cat (timeline)
    """
    cat_data = fetch_cat(user_id, cat_id)
    if not cat_data:
        raise HTTPException(status_code=404, detail="Cat not found for this user")
    
    return cat_data


@app.put('/user/{user_id}/cat/{cat_id}', response_model=CatDto, tags=['Cat'])
def put_cat(
    user_id: str = Path(...),
    cat_id: str = Path(...),
    body: CatDto = ...,
) -> CatDto:
    """
    Update a cat (timeline)
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    updated = update_cat(user_id, cat_id, body)
    if not updated:
        raise HTTPException(status_code=404, detail="Cat not found for this user")
    return updated


@app.delete('/user/{user_id}/cat/{cat_id}', response_model=None, tags=['Cat'])
def delete_cat(
    user_id: str = Path(...), cat_id: str = Path(...)
) -> None:
    """
    Delete a cat (timeline)
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    ok = remove_cat(user_id, cat_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to delete cat")
    return {"message": "Cat deleted"}


# ------------------------
# Document Endpoints
# ------------------------

@app.post(
    '/user/{user_id}/cat/{cat_id}/document',
    response_model=None,
    responses={'201': {'model': DocumentDto}},
    tags=['Document'],
)
def post_document(
    user_id: str = Path(...), cat_id: str = Path(...)
) -> Union[None, DocumentDto]:
    """
    Upload a document for a cat (timeline)
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    # In this simplified implementation we accept a filename in a query/body in future; for now use a placeholder
    filename = "uploaded_document"
    doc = create_document(user_id, cat_id, filename)
    if not doc:
        raise HTTPException(status_code=500, detail="Failed to create document")
    return doc


@app.get(
    '/user/{user_id}/cat/{cat_id}/document',
    response_model=List[DocumentDto],
    tags=['Document'],
)
def get_documents(
    user_id: str = Path(...), cat_id: str = Path(...)
) -> List[DocumentDto]:
    """
    Get all documents for a cat (timeline)
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    docs = fetch_documents(user_id, cat_id)
    return docs if docs else []


@app.get(
    '/user/{user_id}/cat/{cat_id}/document/{document_id}',
    response_model=DocumentDto,
    tags=['Document'],
)
def get_document(
    user_id: str = Path(...),
    cat_id: str = Path(...),
    document_id: str = Path(...),
) -> DocumentDto:
    """
    Get a specific document
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    doc = fetch_document(user_id, cat_id, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

# ------------------------
# Entity Endpoints
# ------------------------
@app.post(
    '/user/{user_id}/cat/{cat_id}/entity',
    response_model=None,
    responses={'201': {'model': EntityDto}},
    tags=['Entity'],
)
def post_entity(
    user_id: str = Path(...),
    cat_id: str = Path(...),
    body: EntityDto = ...,
) -> Union[None, EntityDto]:
    """
    Create an entity (person/organization) who participates in events
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    ent = create_entity(user_id, cat_id, body)
    if not ent:
        raise HTTPException(status_code=500, detail="Failed to create entity")
    return ent


@app.get(
    '/user/{user_id}/cat/{cat_id}/entity',
    response_model=List[EntityDto],
    tags=['Entity'],
)
def get_entities(
    user_id: str = Path(...), cat_id: str = Path(...)
) -> List[EntityDto]:
    """
    Get all entities for a cat (timeline)
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    ents = fetch_entities(user_id, cat_id)
    return ents if ents else []


@app.delete('/user/{user_id}/cat/{cat_id}/entity', response_model=None, tags=['Entity'])
def delete_entity(
    user_id: str = Path(...),
    cat_id: str = Path(...),
    entity_id: str = Query(...),
) -> None:
    """
    Delete a cat's entity
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    ok = remove_entity(user_id, cat_id, entity_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to delete entity")
    return {"message": "Entity deleted"}


@app.get(
    '/user/{user_id}/cat/{cat_id}/entity/{entity_id}',
    response_model=EntityDto,
    tags=['Entity'],
)
def get_entity(
    user_id: str = Path(...),
    cat_id: str = Path(...),
    entity_id: str = Path(...),
) -> EntityDto:
    """
    Get a specific entity
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    ent = fetch_entity(user_id, cat_id, entity_id)
    if not ent:
        raise HTTPException(status_code=404, detail="Entity not found")
    return ent

# ------------------------
# Event Endpoints
# ------------------------

@app.get(
    '/user/{user_id}/cat/{cat_id}/event', response_model=List[EventDto], tags=['Event']
)
def get_events(
    user_id: str = Path(...), cat_id: str = Path(...)
) -> List[EventDto]:
    """
    Get all events for a cat (timeline)
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    events = fetch_events(user_id, cat_id)
    return events if events else []


@app.post('/user/{user_id}/cat/{cat_id}/event', response_model=None, tags=['Event'])
def post_event(
    user_id: str = Path(...),
    cat_id: str = Path(...),
    body: EventPostRequest = ...,
) -> None:
    """
    Associate an existing event with a cat (timeline)
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    ev = associate_event_with_cat(user_id, cat_id, body.eventId)
    if not ev:
        raise HTTPException(status_code=500, detail="Failed to associate event")
    return {"message": "Event associated", "event": ev}


@app.delete('/user/{user_id}/cat/{cat_id}/event', response_model=None, tags=['Event'])
def delete_event(
    user_id: str = Path(...),
    cat_id: str = Path(...),
    event_id: str = Query(...),
) -> None:
    """
    Delete a cat's event
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    ok = remove_event(user_id, cat_id, event_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to remove event")
    return {"message": "Event removed"}

@app.post(
    '/user/{user_id}/cat/{cat_id}/event/{event_id}/entity',
    response_model=None,
    tags=['Entity'],
)
def add_entity_to_event(
    user_id: str = Path(...),
    cat_id: str = Path(...),
    event_id: str = Path(...),
    body: EntityPostRequest = ...,
) -> None:
    """
    Add an entity to an event (PARTICIPATES_IN)
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    res = add_entity_to_event_db(user_id, cat_id, event_id, body.entityId)
    if not res:
        raise HTTPException(status_code=500, detail="Failed to add entity to event")
    return {"message": "Entity added to event", "result": res}


@app.get(
    '/user/{user_id}/cat/{cat_id}/location',
    response_model=List[LocationDto],
    tags=['Location'],
)
def get_locations(
    user_id: str = Path(...), cat_id: str = Path(...)
) -> List[LocationDto]:
    """
    Get all locations for a cat (timeline)
    """
    if not fetch_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    locs = fetch_locations(user_id, cat_id)
    return locs if locs else []
