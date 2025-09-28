#!/usr/bin/env python3
"""
InvestiCAT Neo4j Database Loader

Loads processed document data from document_processor_neo4j.py into Neo4j database.
Handles the complete JSON schema with nodes and relationships for investigative journalism data.
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Warning: neo4j driver not installed. Run: pip install neo4j")

class InvestiCATNeo4jLoader:
    """
    Neo4j database loader for InvestiCAT processed document data.
    
    Loads JSON output from document_processor_neo4j.py into Neo4j database
    following the complete InvestiCAT schema.
    """
    
    def __init__(self, uri: str = "neo4j://localhost:7687", 
                 username: str = "neo4j", 
                 password: str = "qfn6NNfwEMRI6s0QuebFri3Pa5LS6-4pxLh3rJHfa74"):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j database URI
            username: Database username  
            password: Database password
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j driver required. Install with: pip install neo4j")
        
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            
            # Test connection with a simple query
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                
                if test_value == 1:
                    self.connected = True
                    print(f"Connected to Neo4j database at {self.uri}")
                    return True
                    
        except Exception as e:
            print(f"Failed to connect to Neo4j database: {e}")
            print(f"URI: {self.uri}")
            print(f"Username: {self.username}")
            print("Please check your Neo4j server is running and credentials are correct")
            return False
        
        return False
    
    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.connected = False
            print("Neo4j connection closed")
    
    def clear_database(self, confirm: bool = False) -> bool:
        """
        Clear all nodes and relationships from the database.
        
        Args:
            confirm: Must be True to actually clear the database
            
        Returns:
            bool: True if clearing succeeded
        """
        if not self.connected:
            print("Not connected to Neo4j database")
            return False
        
        if not confirm:
            print("Database clear requested but not confirmed. Use confirm=True to proceed.")
            return False
        
        try:
            with self.driver.session() as session:
                # Delete all relationships first
                session.run("MATCH ()-[r]-() DELETE r")
                
                # Then delete all nodes
                session.run("MATCH (n) DELETE n")
                
                print("Database cleared successfully")
                return True
                
        except Exception as e:
            print(f"Failed to clear database: {e}")
            return False
    
    def create_constraints(self):
        """Create uniqueness constraints and indexes for better performance."""
        if not self.connected:
            print("Not connected to Neo4j database")
            return False
        
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE", 
            "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (ent:Entity) REQUIRE ent.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Cat) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (dt:Date) REQUIRE dt.date IS UNIQUE"
        ]
        
        try:
            with self.driver.session() as session:
                for constraint in constraints:
                    session.run(constraint)
            print("Neo4j constraints created successfully")
            return True
            
        except Exception as e:
            print(f"Failed to create constraints: {e}")
            return False
    
    def load_document_data(self, json_data: Dict[str, Any]) -> bool:
        """
        Load processed document data into Neo4j database.
        
        Args:
            json_data: JSON structure from document_processor_neo4j.py
            
        Returns:
            bool: True if loading succeeded
        """
        if not self.connected:
            print("Not connected to Neo4j database")
            return False
        
        try:
            with self.driver.session() as session:
                # Load nodes first
                self._load_nodes(session, json_data.get("nodes", {}))
                
                # Then load relationships  
                self._load_relationships(session, json_data.get("relationships", []))
                
                print("Document data loaded successfully into Neo4j")
                return True
                
        except Exception as e:
            print(f"Failed to load document data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_nodes(self, session, nodes: Dict[str, List[Dict]]):
        """Load all node types into Neo4j."""
        
        # Load Document nodes
        for doc in nodes.get("documents", []):
            session.run(
                "MERGE (d:Document {id: $id}) SET d.filename = $filename",
                id=doc["id"], filename=doc["filename"]
            )
        
        # Load Event nodes
        for event in nodes.get("events", []):
            session.run(
                "MERGE (e:Event {id: $id}) SET e.title = $title, e.summary = $summary",
                id=event["id"], title=event["title"], summary=event["summary"]
            )
        
        # Load Date nodes (NO ID FIELD - use date as unique identifier)
        for date in nodes.get("dates", []):
            session.run(
                "MERGE (dt:Date {date: datetime($date)})",
                date=date["date"]
            )
        
        # Load Location nodes
        for location in nodes.get("locations", []):
            session.run(
                "MERGE (l:Location {id: $id}) SET l.address = $address",
                id=location["id"], address=location["address"]
            )
        
        # Load Entity nodes
        for entity in nodes.get("entities", []):
            session.run(
                "MERGE (ent:Entity {id: $id}) SET ent.name = $name",
                id=entity["id"], name=entity["name"]
            )
        
        # Load User nodes
        for user in nodes.get("users", []):
            session.run(
                """MERGE (u:User {id: $id}) 
                   SET u.email = $email, u.name = $name, u.password = $password""",
                id=user["id"], email=user["email"], 
                name=user["name"], password=user["password"]
            )
        
        print(f"Loaded nodes: {sum(len(node_list) for node_list in nodes.values())} total")
    
    def _load_relationships(self, session, relationships: List[Dict]):
        """Load all relationships into Neo4j."""
        
        for rel in relationships:
            from_node = rel["from_node"]
            to_node = rel["to_node"]
            rel_type = rel["type"]
            
            # Handle different relationship types with proper node matching
            if rel_type == "MENTIONS":
                # Document MENTIONS Event
                session.run(f"""
                    MATCH (from:Document {{id: $from_node}})
                    MATCH (to:Event {{id: $to_node}})
                    MERGE (from)-[:{rel_type}]->(to)
                """, from_node=from_node, to_node=to_node)
                
            elif rel_type == "OCCURRED_ON":
                # Event OCCURRED_ON Date  
                session.run(f"""
                    MATCH (from:Event {{id: $from_node}})
                    MATCH (to:Date {{date: datetime($to_node)}})
                    MERGE (from)-[:{rel_type}]->(to)
                """, from_node=from_node, to_node=to_node)
                
            elif rel_type == "OCCURRED_AT":
                # Event OCCURRED_AT Location
                session.run(f"""
                    MATCH (from:Event {{id: $from_node}})
                    MATCH (to:Location {{id: $to_node}})
                    MERGE (from)-[:{rel_type}]->(to)
                """, from_node=from_node, to_node=to_node)
                
            elif rel_type == "PARTICIPATES_IN":
                # Entity PARTICIPATES_IN Event
                session.run(f"""
                    MATCH (from:Entity {{id: $from_node}})
                    MATCH (to:Event {{id: $to_node}})
                    MERGE (from)-[:{rel_type}]->(to)
                """, from_node=from_node, to_node=to_node)
                
            elif rel_type == "OWNS":
                # User OWNS Cat (handled by frontend, but support if present)
                session.run(f"""
                    MATCH (from:User {{id: $from_node}})
                    MATCH (to:Cat {{id: $to_node}})
                    MERGE (from)-[:{rel_type}]->(to)
                """, from_node=from_node, to_node=to_node)
                
            elif rel_type == "HAS_DOCUMENT":
                # Cat HAS_DOCUMENT Document (handled by frontend, but support if present)
                session.run(f"""
                    MATCH (from:Cat {{id: $from_node}})
                    MATCH (to:Document {{id: $to_node}})
                    MERGE (from)-[:{rel_type}]->(to)
                """, from_node=from_node, to_node=to_node)
                
            elif rel_type == "HAS_EVENT":
                # Cat HAS_EVENT Event (handled by frontend, but support if present)
                session.run(f"""
                    MATCH (from:Cat {{id: $from_node}})
                    MATCH (to:Event {{id: $to_node}})
                    MERGE (from)-[:{rel_type}]->(to)
                """, from_node=from_node, to_node=to_node)
        
        print(f"Loaded relationships: {len(relationships)} total")
    
    def load_from_file(self, json_file_path: str) -> bool:
        """
        Load document data from JSON file.
        
        Args:
            json_file_path: Path to JSON file from document processor
            
        Returns:
            bool: True if loading succeeded
        """
        file_path = Path(json_file_path)
        
        if not file_path.exists():
            print(f"JSON file not found: {json_file_path}")
            return False
        
        try:
            with open(file_path, 'r') as f:
                json_data = json.load(f)
            
            print(f"Loading data from: {file_path.name}")
            return self.load_document_data(json_data)
            
        except json.JSONDecodeError as e:
            print(f"Invalid JSON file: {e}")
            return False
        except Exception as e:
            print(f"Failed to load from file: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, int]:
        """
        Get statistics about loaded data.
        
        Returns:
            dict: Node and relationship counts
        """
        if not self.connected:
            print("Not connected to Neo4j database")
            return {}
        
        stats = {}
        
        try:
            with self.driver.session() as session:
                # Count nodes by type
                node_types = ["Document", "Event", "Date", "Location", "Entity", "User", "Cat"]
                for node_type in node_types:
                    result = session.run(f"MATCH (n:{node_type}) RETURN count(n) as count")
                    stats[f"{node_type} nodes"] = result.single()["count"]
                
                # Count relationships by type  
                rel_result = session.run("""
                    MATCH ()-[r]->()
                    RETURN type(r) as rel_type, count(r) as count
                    ORDER BY rel_type
                """)
                
                for record in rel_result:
                    rel_type = record["rel_type"]
                    count = record["count"]
                    stats[f"{rel_type} relationships"] = count
                
                # Total counts
                total_nodes = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                total_rels = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                
                stats["Total nodes"] = total_nodes
                stats["Total relationships"] = total_rels
                
        except Exception as e:
            print(f"Failed to get database stats: {e}")
        
        return stats

def main():
    """Example usage and CLI for Neo4j loader."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="InvestiCAT Neo4j Database Loader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data.json                           # Load JSON file into Neo4j
  %(prog)s data.json --clear                  # Clear database first, then load
  %(prog)s --stats                            # Show database statistics
  %(prog)s --clear-confirm                    # Clear database only
  %(prog)s data.json --uri bolt://server:7687 # Custom Neo4j server

Database Connection:
  Default URI: neo4j://localhost:7687
  Default credentials: neo4j/qfn6NNfwEMRI6s0QuebFri3Pa5LS6-4pxLh3rJHfa74
        """
    )
    
    parser.add_argument(
        'json_file',
        nargs='?',
        help='JSON file from document processor to load'
    )
    
    parser.add_argument(
        '--uri',
        default="neo4j://localhost:7687",
        help='Neo4j database URI (default: neo4j://localhost:7687)'
    )
    
    parser.add_argument(
        '--username',
        default="neo4j", 
        help='Neo4j username (default: neo4j)'
    )
    
    parser.add_argument(
        '--password',
        default="qfn6NNfwEMRI6s0QuebFri3Pa5LS6-4pxLh3rJHfa74",
        help='Neo4j password'
    )
    
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear database before loading'
    )
    
    parser.add_argument(
        '--clear-confirm',
        action='store_true', 
        help='Clear database only (no loading)'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )
    
    parser.add_argument(
        '--create-constraints',
        action='store_true',
        help='Create database constraints and indexes'
    )
    
    args = parser.parse_args()
    
    # Initialize loader
    loader = InvestiCATNeo4jLoader(uri=args.uri, username=args.username, password=args.password)
    
    # Connect to database
    if not loader.connect():
        sys.exit(1)
    
    try:
        # Create constraints if requested
        if args.create_constraints:
            loader.create_constraints()
        
        # Clear database if requested
        if args.clear or args.clear_confirm:
            loader.clear_database(confirm=True)
            
            if args.clear_confirm:
                print("Database cleared successfully")
                return
        
        # Load data if JSON file provided
        if args.json_file:
            success = loader.load_from_file(args.json_file)
            if success:
                print("Data loaded successfully")
            else:
                print("Failed to load data")
                sys.exit(1)
        
        # Show statistics if requested or after loading
        if args.stats or args.json_file:
            print("\n" + "="*40)
            print("DATABASE STATISTICS")
            print("="*40)
            
            stats = loader.get_database_stats()
            for key, value in stats.items():
                print(f"{key}: {value}")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        loader.close()

if __name__ == "__main__":
    main()