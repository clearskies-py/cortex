import logging
from typing import Any, Self, cast

from clearskies import Column
from clearskies.di import inject
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

    def where_for_request(
        self: Self,
        model: Self,
        input_output: Any,
        routing_data: dict[str, str],
        authorization_data: dict[str, Any],
        overrides: dict[str, Column] = {},
    ) -> Self:
        """Return iterable models."""
        return (
            model.where("types=service")
            .where("include_nested_fields=team:members")
            .where("include_owners=true")
            .where("include_metadata=true")
            .where("include_hierarchy_fields=groups")
        )

    def get_software_product(self: Self) -> cortex_catalog_entity_domain.CortexCatalogEntityDomain:
        """
        Get the upper domain of this service if set.

        The top level domain in this software hierarchy should be a MCP Product.
        """
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
        """
        Get the first domain of this service if set.

        Any other “Domains” in the hierarchy below the top layer (Products) can largely be used at your Team’s discretion.
        """
        hierarchy = from_dict(dataclasses.ServiceEntityHierarchy, data=self.hierarchy)
        if hierarchy.parents:
            container = hierarchy.parents[0]
            return cast(
                cortex_catalog_entity_domain.CortexCatalogEntityDomain,
                self.entity_domains.find(f"tag={container.tag}"),
            )
        return cast(cortex_catalog_entity_domain.CortexCatalogEntityDomain, self.entity_domains.empty())

    def get_domain(self: Self) -> cortex_team.CortexTeam:
        """Find the domain based on the team ownership."""
        domain = cast(cortex_team.CortexTeam, self.teams.empty())

        if not self.ownersV2:
            return domain

        owners = from_dict(dataclasses.EntityTeamOwner, data=self.ownersV2)

        if not owners.teams:
            return domain

        logger.debug(f"EntityService: teams {owners.teams}")
        entity_team = owners.teams[0]
        logger.debug(f"Found entity team: {entity_team}")
        team = self.teams.find(f"team_tag={entity_team.tag}")

        if team.exists:
            return cast(cortex_team.CortexTeam, team.find_domain())

        return domain

    def get_squad(self: Self) -> cortex_team.CortexTeam:
        """Find the domain based on the team ownership."""
        squad = cast(cortex_team.CortexTeam, self.teams.empty())
        if not self.ownersV2:
            return squad

        logger.debug(f"EntityService: ownersV2 {self.ownersV2}")
        owners = from_dict(dataclasses.EntityTeamOwner, data=self.ownersV2)

        if not owners.teams:
            return squad

        entity_team = owners.teams[0]
        logger.debug(f"Found entity team: {entity_team}")

        team = self.teams.find(f"teamTag={entity_team.tag}")
        if team.exists:
            return cast(cortex_team.CortexTeam, team)

        return squad
