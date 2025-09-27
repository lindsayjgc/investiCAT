import os
from pathlib import Path
from dotenv import load_dotenv
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

def create_user(user_id: str, name: str, email: str):
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
            result = session.run(query, user_id=user_id, name=name, email=email)
        return result
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
            return result.data()[0]['u'] if result.peek() else None
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
                list_of_users.append(user_data)
        return list_of_users
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return []
    
def remove_user(user_id: str):
    """
    Deletes a user node
    """
    query = "MATCH (u:User {id: $user_id}) DETACH DELETE u"
    try:
        with driver.session() as session:
            session.run(query, user_id=user_id)
        return True
    except Neo4jError as e:
        print(f"Neo4j error: {e}")
        return False

def close_driver():
    """
    Close the Neo4j driver (call on shutdown)
    """
    driver.close()


create_user("123", "Test User", "test@gmail.com")