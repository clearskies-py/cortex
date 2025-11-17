from typing import Self

from clearskies import Model
from clearskies.columns import String

from clearskies_cortex.backends import CortexBackend


class CortexCatalogEntityRelationship(Model):
    """Model for entities."""

    id_column_name: str = "tag"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "catalog/:tag/relationships/:relationship_type_tag/destinations"

    id = String()
    tag = String()
    description = String()
    name = String()
    type = String()
