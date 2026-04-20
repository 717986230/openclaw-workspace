"""
Cypher Query Templates

Pre-defined templates for common graph operations.
"""

from typing import Dict, Any, List, Optional


class QueryTemplates:
    """Collection of pre-defined Cypher query templates"""
    
    # Node operations
    CREATE_NODE = """
    CREATE (n:$label $properties)
    RETURN n
    """
    
    MERGE_NODE = """
    MERGE (n:$label {$key_property: $key_value})
    SET n += $properties
    RETURN n
    """
    
    FIND_NODE_BY_ID = """
    MATCH (n:$label {$id_property: $id_value})
    RETURN n
    """
    
    FIND_NODES_BY_PROPERTIES = """
    MATCH (n:$label)
    WHERE $conditions
    RETURN n
    ORDER BY n.$sort_property $sort_order
    LIMIT $limit
    """
    
    UPDATE_NODE = """
    MATCH (n:$label {$id_property: $id_value})
    SET n += $properties
    RETURN n
    """
    
    DELETE_NODE = """
    MATCH (n:$label {$id_property: $id_value})
    DETACH DELETE n
    RETURN count(n) as deleted
    """
    
    # Relationship operations
    CREATE_RELATIONSHIP = """
    MATCH (a:$from_label {$from_id_property: $from_id_value})
    MATCH (b:$to_label {$to_id_property: $to_id_value})
    CREATE (a)-[r:$rel_type $properties]->(b)
    RETURN r
    """
    
    MERGE_RELATIONSHIP = """
    MATCH (a:$from_label {$from_id_property: $from_id_value})
    MATCH (b:$to_label {$to_id_property: $to_id_value})
    MERGE (a)-[r:$rel_type]->(b)
    SET r += $properties
    RETURN r
    """
    
    FIND_RELATIONSHIPS = """
    MATCH (a:$from_label {$from_id_property: $from_id_value})-[r:$rel_type]-(b:$to_label)
    RETURN a, r, b
    """
    
    DELETE_RELATIONSHIP = """
    MATCH (a:$from_label {$from_id_property: $from_id_value})-[r:$rel_type]-(b:$to_label)
    DELETE r
    RETURN count(r) as deleted
    """
    
    # Path operations
    SHORTEST_PATH = """
    MATCH p = shortestPath(
        (a:$from_label {$from_id_property: $from_id_value})
        -[*]-
        (b:$to_label {$to_id_property: $to_id_value})
    )
    RETURN p
    """
    
    ALL_PATHS = """
    MATCH p = (
        (a:$from_label {$from_id_property: $from_id_value})
        -[*1..$max_depth]-
        (b:$to_label {$to_id_property: $to_id_value})
    )
    RETURN p
    ORDER BY length(p)
    LIMIT $limit
    """
    
    # Graph operations
    NODE_COUNT = """
    MATCH (n:$label)
    RETURN count(n) as count
    """
    
    RELATIONSHIP_COUNT = """
    MATCH ()-[r:$rel_type]->()
    RETURN count(r) as count
    """
    
    NEIGHBORS = """
    MATCH (n:$label {$id_property: $id_value})-[:$rel_type]-(neighbor)
    RETURN neighbor
    """
    
    NEIGHBORS_DEEP = """
    MATCH (n:$label {$id_property: $id_value})-[:$rel_type*$min_depth..$max_depth]-(neighbor)
    RETURN DISTINCT neighbor
    """
    
    # Pattern matching
    PATTERN_MATCH = """
    MATCH $pattern
    WHERE $conditions
    RETURN $returns
    """
    
    # Aggregation
    DEGREE_CENTRALITY = """
    MATCH (n:$label)
    OPTIONAL MATCH (n)-[r]-()
    RETURN n, count(r) as degree
    ORDER BY degree DESC
    LIMIT $limit
    """
    
    NEIGHBOR_COUNT = """
    MATCH (n:$label {$id_property: $id_value})-[r]-()
    RETURN count(r) as neighbor_count
    """
    
    # Full-text search
    FULLTEXT_SEARCH = """
    CALL db.index.fulltext.queryNodes('$index_name', '$search_query')
    YIELD node, score
    RETURN node, score
    ORDER BY score DESC
    LIMIT $limit
    """
    
    # Batch operations
    BATCH_CREATE_NODES = """
    UNWIND $nodes AS node_data
    CREATE (n:$label)
    SET n = node_data
    RETURN count(n) as created
    """
    
    BATCH_CREATE_RELATIONSHIPS = """
    UNWIND $relationships AS rel_data
    MATCH (a:$from_label {$from_id_property: rel_data.from_id})
    MATCH (b:$to_label {$to_id_property: rel_data.to_id})
    CREATE (a)-[r:$rel_type]->(b)
    SET r = rel_data.properties
    RETURN count(r) as created
    """


def format_template(template: str, **kwargs) -> str:
    """
    Format a query template with provided values.
    
    Args:
        template: Query template string
        **kwargs: Values to substitute
    
    Returns:
        Formatted query string
    """
    # Replace $var with {var} for .format()
    def replace_dollar(match):
        var_name = match.group(1)
        return f"{{{var_name}}}"
    
    formatted = re.sub(r'\$(\w+)', replace_dollar, template)
    return formatted.format(**kwargs)


def build_find_query(
    label: str,
    conditions: Dict[str, Any],
    return_fields: List[str],
    order_by: Optional[str] = None,
    limit: Optional[int] = None
) -> tuple:
    """
    Build a parameterized find query.
    
    Args:
        label: Node label
        conditions: Property conditions {name: value}
        return_fields: Fields to return
        order_by: Order by field
        limit: Result limit
    
    Returns:
        Tuple of (query, parameters)
    """
    where_parts = []
    params = {}
    
    for key, value in conditions.items():
        where_parts.append(f"n.{key} = ${key}")
        params[key] = value
    
    where_clause = " AND ".join(where_parts) if where_parts else "true"
    return_clause = ", ".join(return_fields) if return_fields else "n"
    
    query = f"MATCH (n:{label}) WHERE {where_clause} RETURN {return_clause}"
    
    if order_by:
        query += f" ORDER BY {order_by}"
    
    if limit:
        query += f" LIMIT {limit}"
    
    return query, params


def build_create_query(
    label: str,
    properties: Dict[str, Any],
    unique_key: Optional[str] = None
) -> tuple:
    """
    Build a parameterized create query.
    
    Args:
        label: Node label
        properties: Node properties
        unique_key: Optional unique key for MERGE
    
    Returns:
        Tuple of (query, parameters)
    """
    params = {"properties": properties}
    
    if unique_key:
        params["key_value"] = properties.get(unique_key)
        query = f"""
        MERGE (n:{label} {{{unique_key}: $key_value}})
        SET n += $properties
        RETURN n
        """
    else:
        query = f"CREATE (n:{label} $properties) RETURN n"
    
    return query, params


def build_relationship_query(
    from_label: str,
    from_key: str,
    from_value: Any,
    to_label: str,
    to_key: str,
    to_value: Any,
    rel_type: str,
    properties: Optional[Dict[str, Any]] = None,
    merge: bool = False
) -> tuple:
    """
    Build a relationship creation query.
    
    Args:
        from_label: Source node label
        from_key: Source node property key
        from_value: Source node property value
        to_label: Target node label
        to_key: Target node property key
        to_value: Target node property value
        rel_type: Relationship type
        properties: Relationship properties
        merge: Use MERGE instead of CREATE
    
    Returns:
        Tuple of (query, parameters)
    """
    operation = "MERGE" if merge else "CREATE"
    params = {
        "from_value": from_value,
        "to_value": to_value,
    }
    
    if properties:
        params["properties"] = properties
        query = f"""
        MATCH (a:{from_label} {{{from_key}: $from_value}})
        MATCH (b:{to_label} {{{to_key}: $to_value}})
        {operation} (a)-[r:{rel_type} $properties]->(b)
        RETURN r
        """
    else:
        query = f"""
        MATCH (a:{from_label} {{{from_key}: $from_value}})
        MATCH (b:{to_label} {{{to_key}: $to_value}})
        {operation} (a)-[r:{rel_type}]->(b)
        RETURN r
        """
    
    return query, params


import re  # Import for regex substitution
