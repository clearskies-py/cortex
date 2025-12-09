import logging
from typing import Any, Iterator, Self, cast

from clearskies import Column
from clearskies.di import inject
from clearskies.query import Condition, Query
from dacite import from_dict

from clearskies_cortex import dataclasses
from clearskies_cortex.backends import CortexBackend
from clearskies_cortex.models import (
    cortex_catalog_entity,
    cortex_catalog_entity_domain,
    cortex_team,
)

logger = logging.getLogger(__name__)


class CortexCatalogEntityService(cortex_catalog_entity.CortexCatalogEntity):
    """Model for domain entities."""

    backend = CortexBackend()

    teams = inject.ByClass(cortex_team.CortexTeam)
    entity_domains = inject.ByClass(cortex_catalog_entity_domain.CortexCatalogEntityDomain)

    def get_final_query(self) -> Query:
        return (
            self.get_query()
            .add_where(Condition("types=service"))
            .add_where(Condition("include_nested_fields=team:members"))
            .add_where(Condition("include_owners=true"))
            .add_where(Condition("include_metadata=true"))
            .add_where(Condition("include_hierarchy_fields=groups"))
        )

    def get_software_domain(self: Self) -> cortex_catalog_entity_domain.CortexCatalogEntityDomain:
        """Get the upper domain of this service if set."""
        hierarchy = from_dict(dataclasses.ServiceEntityHierarchy, data=self.hierarchy)
        if hierarchy.parents:
            parent = hierarchy.parents[0]
            while parent.parents:
                parent = parent.parents[0]
            return cast(
                cortex_catalog_entity_domain.CortexCatalogEntityDomain,
                self.entity_domains.find(f"tag={parent.tag}"),
            )
        return cast(cortex_catalog_entity_domain.CortexCatalogEntityDomain, self.entity_domains.empty())

    def get_software_container(self: Self) -> cortex_catalog_entity_domain.CortexCatalogEntityDomain:
        """Get the first domain of this service if set."""
        hierarchy = from_dict(dataclasses.ServiceEntityHierarchy, data=self.hierarchy)
        if hierarchy.parents:
            container = hierarchy.parents[0]
            return cast(
                cortex_catalog_entity_domain.CortexCatalogEntityDomain,
                self.entity_domains.find(f"tag={container.tag}"),
            )
        return cast(cortex_catalog_entity_domain.CortexCatalogEntityDomain, self.entity_domains.empty())

    def get_top_level_team(self: Self) -> cortex_team.CortexTeam:
        """Find the top level team based on the team ownership."""
        team = self.get_team()

        if team:
            return team.find_top_level_team()

        return team

    def get_team(self: Self) -> cortex_team.CortexTeam:
        """Find the team based on the team ownership."""
        team = cast(cortex_team.CortexTeam, self.teams.empty())
        if not self.ownersV2:
            return team

        logger.debug(f"EntityService: ownersV2 {self.ownersV2}")
        owners = from_dict(dataclasses.EntityTeamOwner, data=self.ownersV2)

        if not owners.teams:
            return team

        entity_team = owners.teams[0]
        logger.debug(f"Found entity team: {entity_team}")

        return self.teams.find(f"team_tag={entity_team.tag}")
