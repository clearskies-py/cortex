from typing import Self

from clearskies import Model
from clearskies.columns import String

from clearskies_cortex.backends import CortexBackend


class CortexCatalogEntityRelationship(Model):
    """
    Model for Cortex entity relationships.

    This model represents relationships between entities in the Cortex catalog.
    Relationships define connections between entities such as dependencies,
    ownership, or custom relationship types.

    The model connects to the Cortex API endpoint
    `catalog/:tag/relationships/:relationship_type_tag/destinations` to fetch
    relationship destination entities.

    ```python
    from clearskies_cortex.models import CortexCatalogEntityRelationship

    # Fetch relationship destinations for an entity
    relationships = CortexCatalogEntityRelationship()
    destinations = relationships.where("tag=my-service").where("relationship_type_tag=depends-on")
    for dest in destinations:
        print(f"Depends on: {dest.name} ({dest.type})")
    ```
    """

    id_column_name: str = "tag"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "catalog/:tag/relationships/:relationship_type_tag/destinations"

    """
    The unique identifier for the relationship destination entity.
    """
    id = String()

    """
    The tag identifier of the relationship destination entity.
    """
    tag = String()

    """
    A description of the relationship destination entity.
    """
    description = String()

    """
    The human-readable name of the relationship destination entity.
    """
    name = String()

    """
    The type of the relationship destination entity (e.g., "service", "domain").
    """
    type = String()
