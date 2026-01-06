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

    def get_top_level_team(self: Self) -> cortex_team.CortexTeam:
        """Find the top level team based on the team ownership."""
        team = self.get_team()
        if team:
            return team.find_top_level_team()

        return team

    def get_team(self: Self) -> cortex_team.CortexTeam:
        """Find the team based on the team ownership."""
        team = self.teams.empty()
        self.logger.debug(f"EntityService: owners {self.owners}")
        if not self.owners:
            return team
        owners = self.parse_owners()
        self.logger.debug(f"Parsed owners: {owners}")
        if not owners.teams:
            return team

        entity_team = owners.teams[0]
        self.logger.debug(f"Found entity team: {entity_team}")

        return self.teams.find(f"team_tag={entity_team.tag}")

    def get_top_level_domain(self: Self) -> cortex_catalog_entity_domain.CortexCatalogEntityDomain:
        """Get the upper domain of this service if set."""
        hierarchy = self.parse_hierarchy()
        if hierarchy.parents:
            parent = hierarchy.parents[0]
            while parent.parents:
                parent = parent.parents[0]
            return self.entity_domains.find(f"tag={parent.tag}")
        return self.entity_domains.empty()

    def get_parent_domain(self: Self) -> cortex_catalog_entity_domain.CortexCatalogEntityDomain:
        """Get the first domain of this service if set."""
        hierarchy = self.parse_hierarchy()
        if hierarchy.parents:
            container = hierarchy.parents[0]
            return self.entity_domains.find(f"tag={container.tag}")
        return self.entity_domains.empty()
