from typing import Any, Self

from clearskies import Column
from clearskies.query import Condition, Query

from clearskies_cortex.models import cortex_catalog_entity


class CortexCatalogEntityDomain(cortex_catalog_entity.CortexCatalogEntity):
    """
    Model for Cortex domain entities.

    This model extends CortexCatalogEntity to specifically handle domain-type entities
    in the Cortex catalog. Domains represent logical groupings of services and can be
    organized hierarchically.

    The model automatically filters for domain entities and includes nested fields for
    team members, owners, metadata, and hierarchy groups.

    ```python
    from clearskies_cortex.models import CortexCatalogEntityDomain

    # Fetch all domains
    domains = CortexCatalogEntityDomain()
    for domain in domains.get_final_query():
        print(f"Domain: {domain.name}")

    # Get the top-level domain for a given domain
    domain = domains.find("tag=my-domain")
    top_level = domain.get_top_level_domain()
    print(f"Top-level domain: {top_level.name}")

    # Get the immediate parent domain
    parent = domain.get_parent()
    if parent.exists():
        print(f"Parent domain: {parent.name}")
    ```
    """

    def get_final_query(self) -> Query:
        return (
            self.get_query()
            .add_where(Condition("types=domain"))
            .add_where(Condition("include_nested_fields=team:members"))
            .add_where(Condition("include_owners=true"))
            .add_where(Condition("include_metadata=true"))
            .add_where(Condition("include_hierarchy_fields=groups"))
        )

    def get_top_level_domain(self: Self) -> Self:
        """Get the upper domain of this service if set."""
        hierarchy = self.parse_hierarchy()
        if hierarchy.parents:
            parent = hierarchy.parents[0]
            while parent.parents:
                parent = parent.parents[0]
            return self.as_query().find(f"tag={parent.tag}")
        return self.empty()

    def get_parent(self: Self) -> Self:
        """Get the first domain of this service if set."""
        hierarchy = self.parse_hierarchy()
        if hierarchy.parents:
            container = hierarchy.parents[0]
            return self.as_query().find(f"tag={container.tag}")
        return self.empty()
