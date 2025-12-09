from typing import Any, Self

from clearskies import Column
from clearskies.query import Condition, Query

from clearskies_cortex.models import cortex_catalog_entity


class CortexCatalogEntityDomain(cortex_catalog_entity.CortexCatalogEntity):
    """Model for domain entities."""

    def get_predefined_query(self) -> Query:
        return (
            self.get_query()
            .add_where(Condition("types=domain"))
            .add_where(Condition("include_nested_fields=team:members"))
            .add_where(Condition("include_owners=true"))
            .add_where(Condition("include_metadata=true"))
            .add_where(Condition("include_hierarchy_fields=groups"))
        )
