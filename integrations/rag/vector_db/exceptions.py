"""
Vector database exceptions.
"""


class VectorDBError(Exception):
    """Base exception for vector database errors."""
    pass


class ConnectionError(VectorDBError):
    """Connection to vector database failed."""
    pass


class CollectionNotFoundError(VectorDBError):
    """Collection does not exist."""
    pass


class CollectionAlreadyExistsError(VectorDBError):
    """Collection already exists."""
    pass


class InsertError(VectorDBError):
    """Failed to insert vectors."""
    pass


class SearchError(VectorDBError):
    """Search operation failed."""
    pass


class UpdateError(VectorDBError):
    """Update operation failed."""
    pass


class DeleteError(VectorDBError):
    """Delete operation failed."""
    pass


class InvalidDimensionError(VectorDBError):
    """Vector dimension mismatch."""
    pass


class InvalidMetricError(VectorDBError):
    """Invalid distance metric."""
    pass


class AuthenticationError(VectorDBError):
    """Authentication failed."""
    pass


class ConfigurationError(VectorDBError):
    """Invalid configuration."""
    pass
