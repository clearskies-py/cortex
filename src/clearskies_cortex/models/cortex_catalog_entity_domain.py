from typing import Any, Self

from clearskies import Column

from clearskies_cortex.models import cortex_catalog_entity


class CortexCatalogEntityDomain(cortex_catalog_entity.CortexCatalogEntity):
    """Model for domain entities."""

    def where_for_request(
        self: Self,
        model: Self,
        input_output: Any,
        routing_data: dict[str, str],
        authorization_data: dict[str, Any],
        overrides: dict[str, Column] = {},
    ) -> Self:
        return (
            model.where("types=domain")
            .where("include_nested_fields=team:members")
            .where("include_owners=true")
            .where("include_metadata=true")
            .where("include_hierarchy_fields=groups")
        )
