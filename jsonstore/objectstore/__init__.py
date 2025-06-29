"""Public API for the :mod:`jsonstore.objectstore` package."""

from .table import (
    create_object_table,
    insert_object,
    insert_object_auto_hash,
    insert_objects_auto_hash,
    retrieve_object,
    retrieve_all_objects,
)
from .view import create_property_concat_view
from .fts import create_property_concat_fts
from .store import ObjectStore

__all__ = [
    "create_object_table",
    "insert_object",
    "insert_object_auto_hash",
    "insert_objects_auto_hash",
    "retrieve_object",
    "retrieve_all_objects",
    "create_property_concat_view",
    "create_property_concat_fts",
    "ObjectStore",
]
