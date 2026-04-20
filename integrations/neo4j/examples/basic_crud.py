"""
Basic CRUD Operations Example

Demonstrates basic create, read, update, and delete operations.
"""

from integrations.neo4j.database import Neo4jConnection, Neo4jConfig


def main():
    """Run basic CRUD examples"""
    
    # Create connection
    config = Neo4jConfig(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="your_password"
    )
    
    with Neo4jConnection(config) as conn:
        
        # CREATE - Create a person node
        print("Creating person nodes...")
        
        person1 = conn.create_node(
            label="Person",
            properties={
                "id": "p1",
                "name": "Alice",
                "age": 30,
                "email": "alice@example.com"
            },
            unique_key="id"
        )
        print(f"Created: {person1}")
        
        person2 = conn.create_node(
            label="Person",
            properties={
                "id": "p2",
                "name": "Bob",
                "age": 25,
                "email": "bob@example.com"
            },
            unique_key="id"
        )
        print(f"Created: {person2}")
        
        # CREATE - Create a relationship
        print("\nCreating relationship...")
        
        rel = conn.create_relationship(
            from_label="Person",
            from_key="id",
            from_value="p1",
            to_label="Person",
            to_key="id",
            to_value="p2",
            relationship_type="KNOWS",
            properties={
                "since": "2020",
                "weight": 0.8
            }
        )
        print(f"Created relationship: {rel}")
        
        # READ - Find a node
        print("\nReading node...")
        
        found_person = conn.find_node("Person", {"id": "p1"})
        print(f"Found person: {found_person}")
        
        # READ - Execute custom query
        print("\nExecuting custom query...")
        
        query = """
        MATCH (p:Person)
        WHERE p.age > $min_age
        RETURN p.name, p.age
        ORDER BY p.age DESC
        """
        results = conn.execute(query, {"min_age": 20})
        print(f"People over 20: {results}")
        
        # UPDATE - Update a node
        print("\nUpdating node...")
        
        update_query = """
        MATCH (p:Person {id: $id})
        SET p.age = $new_age, p.updated_at = timestamp()
        RETURN p
        """
        updated = conn.execute(update_query, {"id": "p1", "new_age": 31})
        print(f"Updated: {updated}")
        
        # DELETE - Delete a relationship
        print("\nDeleting relationship...")
        
        delete_rel_query = """
        MATCH (a:Person {id: 'p1'})-[r:KNOWS]-(b:Person {id: 'p2'})
        DELETE r
        RETURN count(r) as deleted
        """
        conn.execute(delete_rel_query)
        print("Relationship deleted")
        
        # DELETE - Delete nodes
        print("\nDeleting nodes...")
        
        conn.delete_node("Person", "id", "p1", force=True)
        conn.delete_node("Person", "id", "p2", force=True)
        print("Nodes deleted")


if __name__ == "__main__":
    main()
