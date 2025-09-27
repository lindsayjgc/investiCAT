import os
from pathlib import Path
from dotenv import load_dotenv
import uuid
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

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
                    doc_id = doc.id if getattr(doc, 'id', None) else str(uuid.uuid4())
                    filename = getattr(doc, 'filename', None)
                    session.run(
                        """
                        MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})
                        CREATE (d:Document {id: $doc_id, filename: $filename})
                        CREATE (c)-[:HAS_DOCUMENT]->(d)
                        RETURN d
                        """,
                        user_id=user_id,
                        cat_id=cat_id,
                        doc_id=doc_id,
                        filename=filename,
                    )

            # Create events (and their locations/entities), if provided
            if getattr(cat_data, 'events', None):
                for ev in cat_data.events:
                    ev_id = ev.id if getattr(ev, 'id', None) else str(uuid.uuid4())
                    title = getattr(ev, 'title', None)
                    summary = getattr(ev, 'summary', None)
                    # convert datetime to ISO string if present
                    date_val = ev.date.isoformat() if getattr(ev, 'date', None) else None

                    # Create the event node and attach to cat
                    session.run(
                        """
                        MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})
                        CREATE (ev:Event {id: $ev_id, title: $title, summary: $summary, date: $date})
                        CREATE (c)-[:HAS_EVENT]->(ev)
                        RETURN ev
                        """,
                        user_id=user_id,
                        cat_id=cat_id,
                        ev_id=ev_id,
                        title=title,
                        summary=summary,
                        date=date_val,
                    )

                    # Location
                    if getattr(ev, 'location', None):
                        loc = ev.location
                        loc_id = loc.id if getattr(loc, 'id', None) else str(uuid.uuid4())
                        address = getattr(loc, 'address', None)
                        session.run(
                            """
                            MATCH (ev:Event {id: $ev_id})
                            CREATE (loc:Location {id: $loc_id, address: $address})
                            CREATE (ev)-[:OCCURS_AT]->(loc)
                            RETURN loc
                            """,
                            ev_id=ev_id,
                            loc_id=loc_id,
                            address=address,
                        )

                    # Entities: create and link to event and to cat
                    if getattr(ev, 'entities', None):
                        for ent in ev.entities:
                            ent_id = ent.id if getattr(ent, 'id', None) else str(uuid.uuid4())
                            name = getattr(ent, 'name', None)
                            # Use MERGE so entities with the same id are not duplicated
                            session.run(
                                """
                                MERGE (e:Entity {id: $ent_id})
                                SET e.name = $name
                                WITH e
                                MATCH (c:Cat {id: $cat_id}), (ev:Event {id: $ev_id})
                                MERGE (c)-[:HAS_ENTITY]->(e)
                                MERGE (e)-[:PARTICIPATES_IN]->(ev)
                                RETURN e
                                """,
                                ent_id=ent_id,
                                name=name,
                                cat_id=cat_id,
                                ev_id=ev_id,
                            )

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
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})
    SET c.title = $title
    RETURN c
    """
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, cat_id=cat_id, title=cat_data.title)
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


def create_document(user_id: str, cat_id: str, filename: str):
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
            if result.peek():
                return dict(result.single()['d'])
            return None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
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


def add_entity_to_event_db(user_id: str, cat_id: str, event_id: str, entity_id: str):
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
    Retrieves a specific cat for a specific user
    """
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Cat {id: $cat_id})
    RETURN c
    """
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, cat_id=cat_id)
            print(result.data())
            return dict(result.single()['c']) if result.peek() else None
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return None

def close_driver():
    """
    Close the Neo4j driver (call on shutdown)
    """
    driver.close()