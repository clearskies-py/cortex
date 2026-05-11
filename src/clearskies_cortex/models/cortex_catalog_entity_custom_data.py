from typing import Self

from clearskies import Model
from clearskies.columns import BelongsToId, BelongsToModel, Datetime, Integer, Json, Select, String

from clearskies_cortex.backends import CortexBackend
from clearskies_cortex.models import cortex_catalog_entity_reference


class CortexCatalogEntityCustomData(Model):
    """
    Model for Cortex entity type custom data.

    This model represents the custom data associated with entity types in the Cortex catalog. Custom data
    allows for extending the schema and structure of different kinds of entities (e.g., service, domain, team).

    The model connects to the Cortex API endpoint `catalog/definitions` to fetch
    entity type custom data.

    ```python
    from clearskies_cortex.models import CortexCatalogEntityType

    # Fetch all entity type custom data
    entity_custom_data = CortexCatalogEntityCustomData()
    for custom_data in entity_custom_data:
        print(f"Type: {custom_data.name}")
        print(f"Description: {custom_data.description}")
    ```
    """

    id_column_name: str = "key"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "catalog/:entity_tag/custom-data"

    """
    The id of the custom data entry, which is a unique identifier for this piece of custom data.
    """
    id = Integer()

    """
    A description of what this custom data represents.
    """
    description = String()

    """
    The key of the custom data, which identifies the specific piece of custom data for an entity type (e.g., "owner", "sla", "cost_center").
    """
    key = String()

    """
    The value of the custom data, which can be any JSON object depending on the entity type and key.
    """
    value = Json()

    """
    The source of the custom data (e.g., "YAML", "API", "INTEGRATION").
    """
    source = Select(allowed_values=["YAML", "API", "INTEGRATION"])

    """
    The date and time when this custom data was last updated.
    """
    date_updated = Datetime()

    """
    The tag identifier of the entity this custom data belongs to.
    """
    entity_tag = BelongsToId(
        cortex_catalog_entity_reference.CortexCatalogEntityReference,
        readable_parent_columns=["id", "name", "tag", "type"],
    )

    """
    Relationship to the parent entity this custom data belongs to, using the entity_tag as the foreign key.

    This allows for easy access to the parent entity's information when working with custom data entries.

    Example usage:
    ```python   from clearskies_cortex.models import CortexCatalogEntityCustomData
    # Fetch custom data for a specific entity
    custom_data_entries = CortexCatalogEntityCustomData().where("entity_tag=my-service")
    for entry in custom_data_entries:
        print(f"Custom Data Key: {entry.key}")
        print(f"Custom Data Value: {entry.value}")
        print(f"Belongs to Entity Name: {entry.entity.name}")
        print(f"Belongs to Entity Type: {entry.entity.type}")
    ```
    """
    entity = BelongsToModel("entity_tag")
