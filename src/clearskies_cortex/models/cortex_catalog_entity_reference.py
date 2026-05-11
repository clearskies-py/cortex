from typing import Any


class CortexCatalogEntityReference:
    """
    A lazy reference to the CortexCatalogEntity model to avoid circular imports.

    This class is used in relationship definitions where directly importing the CortexCatalogEntity
    model would cause circular import issues. The actual model class is only imported
    when `get_model_class()` is called.

    Example usage:

    ```python
    from clearskies.columns import BelongsToId, BelongsToModel
    from clearskies_cortex.models import cortex_catalog_entity_reference

    # Use in a column definition
    entity_tag = BelongsToId(cortex_catalog_entity_reference.CortexCatalogEntityReference)
    entity = BelongsToModel("entity_tag")
    ```
    """

    def get_model_class(self) -> Any:
        """
        Return the CortexCatalogEntity model class.

        Performs a lazy import of the CortexCatalogEntity model to avoid circular dependencies.
        This method is called by clearskies when it needs to resolve the relationship.
        """
        from clearskies_cortex.models import CortexCatalogEntity

        return CortexCatalogEntity
