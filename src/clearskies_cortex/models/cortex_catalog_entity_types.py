from typing import Self

from clearskies import Model
from clearskies.columns import Json, String

from clearskies_cortex.backends import CortexBackend


class CortexCatalogEntityType(Model):
    """
    Model for Cortex entity type definitions.

    This model represents the available entity types in the Cortex catalog. Entity types
    define the schema and structure for different kinds of entities (e.g., service, domain, team).

    The model connects to the Cortex API endpoint `catalog/definitions` to fetch
    entity type definitions.

    ```python
    from clearskies_cortex.models import CortexCatalogEntityType

    # Fetch all entity type definitions
    entity_types = CortexCatalogEntityType()
    for entity_type in entity_types:
        print(f"Type: {entity_type.name}")
        print(f"Description: {entity_type.description}")
    ```
    """

    id_column_name: str = "type"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "catalog/definitions"

    """
    The human-readable name of the entity type.
    """
    name = String()

    """
    A description of what this entity type represents.
    """
    description = String()

    """
    JSON object containing the schema definition for this entity type.
    """
    schema = Json()

    """
    The source of the entity type definition (e.g., "builtin", "custom").
    """
    source = String()

    """
    The unique type identifier (e.g., "service", "domain", "team").
    """
    type = String()
