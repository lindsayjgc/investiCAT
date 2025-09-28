import os
from pathlib import Path
from dotenv import load_dotenv
import uuid
from models import DocumentDto
import tempfile
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))  # add repo root to path
from etl.document_processor_neo4j import InvestiCATProcessor
from etl.neo4j_loader import InvestiCATNeo4jLoader
from datetime import datetime

from document_processor import CAT, process_document

# Load .env
env_path = Path(__file__).resolve().parent.parent / "utilities" / ".env"
load_dotenv(dotenv_path=env_path)

# Neo4j driver singleton
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

def create_user(name: str, email: str):
    """
    Creates a user node
    """
    query = """
    MERGE (u:User {id: $user_id})
    ON CREATE SET u.name = $name, u.email = $email
    RETURN u
    """
    try:
        with driver.session() as session:
            user_id = str(uuid.uuid4())
            result = session.run(query, user_id=user_id, name=name, email=email)
            if result.peek():
                return dict(result.single()['u'])
            return None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None


def fetch_user(user_id: str):
    """
    Retrieves a user
    """
    query = "MATCH (u:User {id: $user_id}) RETURN u"
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id)
            if result.peek():
                return dict(result.single()['u'])
            return None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None
    
def fetch_users():
    """
    Retrieves all users
    """
    query = "MATCH (u:User) RETURN u"
    list_of_users = []
    try:
        with driver.session() as session:
            result = session.run(query)
            for record in result.data():
                user_data = record['u']
                list_of_users.append(dict(user_data))
        return list_of_users
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return []
    
def remove_user(user_id: str):
    """
    Deletes a user node
    """
    try:
        with driver.session() as session:
            # Delete documents attached to the user's cats
            session.run(
                """
                MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat)-[:HAS_DOCUMENT]->(d:Document)
                DETACH DELETE d
                """,
                user_id=user_id,
            )

            # Delete entities that participate only in events of this user's cats
            session.run(
                """
                MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat)-[:HAS_EVENT]->(ev:Event)<-[:PARTICIPATES_IN]-(e:Entity)
                DETACH DELETE e
                """,
                user_id=user_id,
            )

            # Delete events attached to the cats
            session.run(
                """
                MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat)-[:HAS_EVENT]->(ev:Event)
                DETACH DELETE ev
                """,
                user_id=user_id,
            )

            # Delete the cats themselves
            session.run(
                """
                MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat)
                DETACH DELETE c
                """,
                user_id=user_id,
            )

            # Finally delete the user
            session.run(
                "MATCH (u:User {id: $user_id}) DETACH DELETE u",
                user_id=user_id,
            )

            # Clean up orphaned events and locations (no remaining relationships)
            session.run("MATCH (ev:Event) WHERE NOT (ev)--() DELETE ev")
            session.run("MATCH (loc:Location) WHERE NOT (loc)--() DELETE loc")

        return True
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return False

def create_cat(user_id: str, cat_data):
    """
    Creates a cat node and associates it with a user
    """ 
    # Create the Cat and attach to the user. If the incoming payload includes
    # documents or events, create those nodes and relationships as well.
    create_cat_query = """
    MATCH (u:User {id: $user_id})
    CREATE (c:Cat {id: $cat_id, title: $cat_title})
    CREATE (u)-[:OWNS]->(c)
    RETURN c
    """
    try:
        with driver.session() as session:
            # Respect an incoming id if provided, otherwise generate one
            cat_id = cat_data.id if getattr(cat_data, 'id', None) else str(uuid.uuid4())
            result = session.run(
                create_cat_query, user_id=user_id, cat_id=cat_id, cat_title=cat_data.title
            )

            if not result.peek():
                return None

            # Create documents, if provided
            if getattr(cat_data, 'documents', None):
                for doc in cat_data.documents:
                    filename = getattr(doc, 'filename', None)
                    # create_document handles id generation and attaching to the cat
                    create_document(user_id, cat_id, filename)

            # Create events (and their locations/entities), if provided
            if getattr(cat_data, 'events', None):
                for ev in cat_data.events:
                    # create_event will create the event node and attach to the cat
                    created_ev = create_event(user_id, cat_id, ev)
                    if not created_ev:
                        continue
                    ev_id = created_ev.get('id')

                    # Location: create and attach if provided
                    if getattr(ev, 'location', None):
                        create_location(ev_id, ev.location)

                    # Entities: create/merge and attach to cat, then link to event
                    if getattr(ev, 'entities', None):
                        for ent in ev.entities:
                            created_ent = create_entity_and_attach(user_id, cat_id, ent)
                            ent_id = created_ent.get('id') if created_ent else None
                            if ent_id:
                                # link existing/created entity to the event
                                add_entity_to_event(user_id, cat_id, ev_id, ent_id)

            # Return the created cat node
            created = session.run("MATCH (c:Cat {id: $cat_id}) RETURN c", cat_id=cat_id)
            return dict(created.single()['c']) if created.peek() else None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None


def update_cat(user_id: str, cat_id: str, cat_data):
    """
    Update a cat's properties
    """
    properties_to_update = []
    if getattr(cat_data, 'title', None) is not None:
        properties_to_update.append("SET c.title = $title")
    if getattr(cat_data, 'description', None) is not None:
        properties_to_update.append("SET c.description = $description")
    query = f"""
    MATCH (u:User {{id: $user_id}})-[:OWNS]->(c:Cat {{id: $cat_id}})
    {''.join(properties_to_update)}
    RETURN c
    """
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, cat_id=cat_id, title=cat_data.title, description=cat_data.description)
            if result.peek():
                return dict(result.single()['c'])
            return None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None


def remove_cat(user_id: str, cat_id: str):
    """
    Deletes a cat node owned by a user
    """
    query = "MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id}) DETACH DELETE c"
    try:
        with driver.session() as session:
            session.run(query, user_id=user_id, cat_id=cat_id)
        return True
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return False

def create_document(user_id: str, cat_id: str, filename: str, content: bytes):
    """
    Create a document node and attach to a cat
    """
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})
    CREATE (d:Document {id: $doc_id, filename: $filename})
    CREATE (c)-[:HAS_DOCUMENT]->(d)
    RETURN d
    """
    try:
        with driver.session() as session:
            doc_id = str(uuid.uuid4())
            result = session.run(query, user_id=user_id, cat_id=cat_id, doc_id=doc_id, filename=filename)
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
                result_cat = process_document(tmp_path)
                event_ids = add_events(user_id, cat_id, result_cat)
            if event_ids:
                for event_id in event_ids:
                    session.run(
                        """
                        MATCH (d:Document {id: $doc_id}), (ev:Event {id: $event_id})
                        MERGE (d)-[:MENTIONS]->(ev)
                        """,
                        doc_id=doc_id,
                        event_id=event_id,
                    )
            return DocumentDto(id=doc_id, filename=filename)
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None
    except Exception as e:
        print(f"ETL processing failed: {e}")
        return None


def fetch_documents(user_id: str, cat_id: str):
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})-[:HAS_DOCUMENT]->(d:Document)
    RETURN d
    """
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, cat_id=cat_id)
            docs = [dict(r['d']) for r in result.data()]
            return docs
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return []


def fetch_document(user_id: str, cat_id: str, document_id: str):
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})-[:HAS_DOCUMENT]->(d:Document {id: $document_id})
    RETURN d
    """
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, cat_id=cat_id, document_id=document_id)
            if result.peek():
                return dict(result.single()['d'])
            return None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None


def create_entity(user_id: str, cat_id: str, entity_data):
    # Create an Entity node; do not attach directly to Cat in the data model.
    query = """
    CREATE (e:Entity {id: $entity_id, name: $name})
    RETURN e
    """
    try:
        with driver.session() as session:
            entity_id = str(uuid.uuid4())
            result = session.run(query, entity_id=entity_id, name=entity_data.name)
            if result.peek():
                return dict(result.single()['e'])
            return None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None


def create_entity_and_attach(user_id: str, cat_id: str, ent_data):
    """
    Ensure an Entity node exists (MERGE by id if provided, otherwise create new id),
    set its name, and attach it to the Cat via :HAS_ENTITY. Returns the entity dict.
    """
    try:
        with driver.session() as session:
            ent_id = ent_data.id if getattr(ent_data, 'id', None) else str(uuid.uuid4())
            name = getattr(ent_data, 'name', None)
            query = """
            MATCH (c:Cat {id: $cat_id})
            MERGE (e:Entity {id: $ent_id})
            SET e.name = $name
            MERGE (c)-[:HAS_ENTITY]->(e)
            RETURN e
            """
            result = session.run(query, cat_id=cat_id, ent_id=ent_id, name=name)
            if result.peek():
                return dict(result.single()['e'])
            return None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None


def create_event(user_id: str, cat_id: str, ev_data):
    """
    Create or update an Event node and attach it to the cat. Returns the event dict.
    """
    try:
        with driver.session() as session:
            ev_id = ev_data.id if getattr(ev_data, 'id', None) else str(uuid.uuid4())
            title = getattr(ev_data, 'title', None)
            summary = getattr(ev_data, 'summary', None)
            date_val = ev_data.date.isoformat() if getattr(ev_data, 'date', None) else None
            query = """
            MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})
            MERGE (ev:Event {id: $ev_id})
            SET ev.title = $title, ev.summary = $summary, ev.date = $date
            MERGE (c)-[:HAS_EVENT]->(ev)
            RETURN ev
            """
            result = session.run(
                query,
                user_id=user_id,
                cat_id=cat_id,
                ev_id=ev_id,
                title=title,
                summary=summary,
                date=date_val,
            )
            if result.peek():
                return dict(result.single()['ev'])
            return None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None


def create_location(ev_id: str, loc_data):
    """
    Create or update a Location node and attach it to the given Event.
    """
    try:
        with driver.session() as session:
            loc_id = loc_data.id if getattr(loc_data, 'id', None) else str(uuid.uuid4())
            address = getattr(loc_data, 'address', None)
            query = """
            MATCH (ev:Event {id: $ev_id})
            MERGE (loc:Location {id: $loc_id})
            SET loc.address = $address
            MERGE (ev)-[:OCCURS_AT]->(loc)
            RETURN loc
            """
            result = session.run(query, ev_id=ev_id, loc_id=loc_id, address=address)
            if result.peek():
                return dict(result.single()['loc'])
            return None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None


def fetch_entities(user_id: str, cat_id: str):
    # Fetch entities that are mentioned by documents or participate in events related to the cat
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})
    OPTIONAL MATCH (c)-[:HAS_EVENT]->(ev:Event)<-[:PARTICIPATES_IN]-(e:Entity)
    OPTIONAL MATCH (c)-[:HAS_DOCUMENT]->(d:Document)-[:MENTIONS]->(e2:Entity)
    WITH collect(DISTINCT e) + collect(DISTINCT e2) AS ents
    UNWIND ents AS ent
    RETURN DISTINCT ent
    """
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, cat_id=cat_id)
            return [dict(r['ent']) for r in result.data() if r['ent'] is not None]
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return []


def remove_entity(user_id: str, cat_id: str, entity_id: str):
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})-[:HAS_ENTITY]->(e:Entity {id: $entity_id})
    DETACH DELETE e
    """
    try:
        with driver.session() as session:
            session.run(query, user_id=user_id, cat_id=cat_id, entity_id=entity_id)
        return True
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return False


def fetch_entity(user_id: str, cat_id: str, entity_id: str):
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})-[:HAS_ENTITY]->(e:Entity {id: $entity_id})
    RETURN e
    """
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, cat_id=cat_id, entity_id=entity_id)
            if result.peek():
                return dict(result.single()['e'])
            return None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None


def fetch_events(user_id: str, cat_id: str):
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})-[:HAS_EVENT]->(ev:Event)
    OPTIONAL MATCH (ev)-[:OCCURS_AT]->(loc:Location)
    OPTIONAL MATCH (ev)-[:HAS_PARTICIPANT]->(ent:Entity)
    RETURN ev, collect(DISTINCT loc) AS locs, collect(DISTINCT ent) AS ents
    """
    events = []
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, cat_id=cat_id)
            for r in result.data():
                ev = dict(r['ev'])
                locs = [dict(l) for l in r['locs'] if l is not None]
                ents = [dict(e) for e in r['ents'] if e is not None]
                ev['location'] = locs[0] if len(locs) else None
                ev['entities'] = ents
                events.append(ev)
        return events
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return []


def associate_event_with_cat(user_id: str, cat_id: str, event_id: str):
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id}), (ev:Event {id: $event_id})
    MERGE (c)-[:HAS_EVENT]->(ev)
    RETURN ev
    """
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, cat_id=cat_id, event_id=event_id)
            if result.peek():
                return dict(result.single()['ev'])
            return None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None


def remove_event(user_id: str, cat_id: str, event_id: str):
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})-[rel:HAS_EVENT]->(ev:Event {id: $event_id})
    DELETE rel
    """
    try:
        with driver.session() as session:
            session.run(query, user_id=user_id, cat_id=cat_id, event_id=event_id)
        return True
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return False


def add_entity_to_event(user_id: str, cat_id: str, event_id: str, entity_id: str):
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})-[:HAS_EVENT]->(ev:Event {id: $event_id}),
          (c)-[:HAS_ENTITY]->(ent:Entity {id: $entity_id})
    MERGE (ent)-[:PARTICIPATES_IN]->(ev)
    RETURN ent, ev
    """
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, cat_id=cat_id, event_id=event_id, entity_id=entity_id)
            if result.peek():
                row = result.single()
                return {'entity': dict(row['ent']), 'event': dict(row['ev'])}
            return None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None


def fetch_locations(user_id: str, cat_id: str):
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})-[:HAS_EVENT]->(ev:Event)-[:OCCURS_AT]->(loc:Location)
    RETURN DISTINCT loc
    """
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, cat_id=cat_id)
            return [dict(r['loc']) for r in result.data()]
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return []
    
def fetch_cats(user_id: str):
    """
    Retrieves all cats for a specific user
    """
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat)
    RETURN c
    """
    list_of_cats = []
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id)
            for record in result.data():
                cat_data = record['c']
                list_of_cats.append(cat_data)
        return list_of_cats
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return []

def fetch_cat(user_id: str, cat_id: str):
    """
    Retrieves a specific cat for a specific user and returns related nodes:
    documents, events (with per-event location and entities), locations, entities
    """
    try:
        with driver.session() as session:
            # Cat node
            cat_res = session.run(
                "MATCH (u:User {id:$user_id})-[:OWNS]->(c:Cat {id:$cat_id}) RETURN c",
                user_id=user_id,
                cat_id=cat_id,
            )
            if not cat_res.peek():
                return None
            cat = dict(cat_res.single()['c'])

            # Documents
            docs_res = session.run(
                "MATCH (u:User {id:$user_id})-[:OWNS]->(c:Cat {id:$cat_id})-[:HAS_DOCUMENT]->(d:Document) RETURN d",
                user_id=user_id,
                cat_id=cat_id,
            )
            documents = [dict(r['d']) for r in docs_res.data() if r.get('d') is not None]

            # Events with per-event locations and entities
            ev_query = """
            MATCH (u:User {id:$user_id})-[:OWNS]->(c:Cat {id:$cat_id})-[:HAS_EVENT]->(ev:Event)
            OPTIONAL MATCH (ev)-[:OCCURS_AT]->(loc:Location)
            OPTIONAL MATCH (ev)<-[:PARTICIPATES_IN]-(ent:Entity)
            RETURN ev, collect(DISTINCT loc) AS locs, collect(DISTINCT ent) AS ents
            """
            events = []
            all_event_locs = []
            all_event_ents = []
            for r in session.run(ev_query, user_id=user_id, cat_id=cat_id).data():
                ev = dict(r['ev']) if r.get('ev') is not None else None
                locs = [dict(l) for l in (r.get('locs') or []) if l is not None]
                ents = [dict(e) for e in (r.get('ents') or []) if e is not None]
                if ev is None:
                    continue
                ev['location'] = locs[0] if len(locs) else None
                ev['entities'] = ents
                events.append(ev)
                all_event_locs.extend(locs)
                all_event_ents.extend(ents)

            # Cat-level entities (HAS_ENTITY)
            cat_ent_res = session.run(
                "MATCH (u:User {id:$user_id})-[:OWNS]->(c:Cat {id:$cat_id})-[:HAS_ENTITY]->(e:Entity) RETURN e",
                user_id=user_id,
                cat_id=cat_id,
            )
            cat_entities = [dict(r['e']) for r in cat_ent_res.data() if r.get('e') is not None]

            # Deduplicate entities by id (merge event entities + cat-level entities)
            entities_map = {}
            for e in (all_event_ents + cat_entities):
                if not e:
                    continue
                eid = e.get('id')
                if eid:
                    entities_map[eid] = e
            entities = list(entities_map.values())

            # Deduplicate locations by id (from events)
            loc_map = {}
            for l in all_event_locs:
                if not l:
                    continue
                lid = l.get('id')
                if lid:
                    loc_map[lid] = l
            locations = list(loc_map.values())

            return {
                'cat': cat,
                'documents': documents,
                'events': events,
                'locations': locations,
                'entities': entities,
            }
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return
    

def add_events(user_id: str, cat_id: str, parsed_cat: CAT) -> list[str]:
    """
    Add events from a CAT object to a cat, associating with the user and document.
    """
    event_ids: list[str] = []
    try:
        with driver.session() as session:
            for ev in parsed_cat.events:
                ev_id: str = str(uuid.uuid4())
                title: str = getattr(ev, 'title', None)
                summary: str = getattr(ev, 'summary', None)
                date_val: str = ev.date if getattr(ev, 'date', None) else None
                location: str = getattr(ev, 'location', None)
                entities: list[str] = getattr(ev, 'entities', None)
                print(f"Adding event: {title}, {summary}, {date_val}, loc={location}, ents={entities}")

                event_ids.append(ev_id)

                # Create or update Event node and attach to Cat
                event_query = """
                MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})
                MERGE (ev:Event {id: $ev_id, date: $date_val})
                SET ev.title = $title, ev.summary = $summary
                MERGE (c)-[:HAS_EVENT]->(ev)
                RETURN ev
                """
                result = session.run(
                    event_query,
                    user_id=user_id,
                    cat_id=cat_id,
                    ev_id=ev_id,
                    title=title,
                    date_val=datetime.strptime(date_val, "%Y-%m-%d").isoformat(),
                    summary=summary,
                )
                if not result.peek():
                    continue
                created_ev = dict(result.single()['ev'])
                ev_id = created_ev.get('id')

                # Location: create and attach if provided
                if location:
                    loc_id: str = location
                    address = location
                    loc_query = """
                    MATCH (ev:Event {id: $ev_id})
                    MERGE (loc:Location {id: $loc_id})
                    SET loc.address = $address
                    MERGE (ev)-[:OCCURS_AT]->(loc)
                    RETURN loc
                    """
                    session.run(loc_query, ev_id=ev_id, loc_id=loc_id, address=address)

                # Entities: create/merge and attach to cat, then link to event
                if entities:
                    for ent in entities:
                        ent_id = ent
                        name = ent
                        ent_query = """
                        MATCH (c:Cat {id: $cat_id}), (ev:Event {id: $ev_id})
                        MERGE (en:Entity {id: $ent_id})
                        SET en.name = $name
                        MERGE (en)-[:PARTICIPATES_IN]->(ev)
                        RETURN en
                        """
                        session.run(ent_query, cat_id=cat_id, ev_id=ev_id, ent_id=ent_id, name=name)

            return event_ids
    except Exception as e:
        print(f"Neo4j error: {e}")
        return []
    return event_ids

def close_driver():
    """
    Close the Neo4j driver (call on shutdown)
    """
    driver.close()