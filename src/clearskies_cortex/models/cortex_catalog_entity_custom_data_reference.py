from typing import Any


class CortexCatalogEntityCustomDataReference:
    """
    A lazy reference to the CortexCatalogEntityCustomData model to avoid circular imports.

    This class is used in relationship definitions where directly importing the CortexCatalogEntityCustomData
    model would cause circular import issues. The actual model class is only imported
    when `get_model_class()` is called.

    Example usage:

    ```python
    from clearskies.columns import HasMany
    from clearskies_cortex.models import cortex_catalog_entity_reference

    # Use in a column definition
    custom_data = HasMany(
        cortex_catalog_entity_custom_data_reference.CortexCatalogEntityCustomDataReference
    )
    ```
    """

    def get_model_class(self) -> Any:
        """
        Return the CortexCatalogEntityCustomData model class.

        Performs a lazy import of the CortexCatalogEntityCustomData model to avoid circular dependencies.
        This method is called by clearskies when it needs to resolve the relationship.
        """
        from clearskies_cortex.models import CortexCatalogEntityCustomData

        return CortexCatalogEntityCustomData
