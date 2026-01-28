from collections.abc import Iterator
from typing import Any, Self

from clearskies import Model
from clearskies.columns import Boolean, Datetime, HasMany, Json, String
from clearskies.di import inject
from clearskies.query import Query
from dacite import from_dict

from clearskies_cortex import dataclasses
from clearskies_cortex.backends import CortexBackend
from clearskies_cortex.columns import StringList
from clearskies_cortex.models import (
    cortex_catalog_entity_group,
    cortex_catalog_entity_scorecard,
)


class CortexCatalogEntity(Model):
    """
    Model for Cortex catalog entities.

    This model represents entities in the Cortex catalog, which can include services, domains,
    teams, and other entity types. It provides access to entity metadata, ownership information,
    hierarchy data, and associated scorecards.

    The model connects to the Cortex catalog API endpoint and supports various search parameters
    for filtering entities.

    ```python
    from clearskies_cortex.models import CortexCatalogEntity

    # Fetch all entities
    entities = CortexCatalogEntity()
    for entity in entities:
        print(f"Entity: {entity.name} ({entity.type})")

    # Find a specific entity by tag
    entity = entities.find("tag=my-service")
    print(entity.description)

    # Access parsed hierarchy data
    hierarchy = entity.parse_hierarchy()
    if hierarchy.parents:
        print(f"Parent: {hierarchy.parents[0].tag}")
    ```
    """

    id_column_name: str = "tag"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "catalog"

    """
    The unique identifier for the entity.
    """
    id = String()

    """
    The unique tag identifier for the entity (e.g., "my-service").

    This is the primary identifier used to reference entities in the Cortex catalog.
    """
    tag = String()

    """
    List of groups the entity belongs to.

    Groups are key-value pairs formatted as "key:value" strings. Use `parse_groups()`
    to convert to a dictionary.
    """
    groups = StringList("groups")

    """
    JSON object containing owner information for the entity.

    Contains team and user ownership data. Use `parse_owners()` to convert to a typed dataclass.
    """
    owners = Json()

    """
    JSON object containing ownership configuration.
    """
    ownership = Json()

    """
    JSON object containing version 2 owner information.
    """
    owners_v2 = Json()

    """
    Human-readable description of the entity.
    """
    description = String()

    """
    JSON object containing Git repository information.

    Includes repository URLs, default branch, and other Git-related metadata.
    """
    git = Json()

    """
    JSON object containing hierarchy information.

    Contains parent and child relationships. Use `parse_hierarchy()` to convert to a typed dataclass.
    """
    hierarchy = Json()

    """
    Timestamp of when the entity was last updated.
    """
    last_updated = Datetime()

    """
    Whether the entity is archived.
    """
    is_archived = Boolean()

    """
    JSON object containing external links associated with the entity.
    """
    links = Json()

    """
    JSON object containing member information for team entities.
    """
    members = Json()

    """
    JSON object containing custom metadata for the entity.
    """
    metadata = Json()

    """
    JSON object containing Slack channel configurations.
    """
    slack_channels = Json()

    """
    Human-readable name of the entity.
    """
    name = String()

    """
    The type of entity (e.g., "service", "domain", "team").
    """
    type = String()

    """
    Related scorecards for this entity.

    HasMany relationship to CortexCatalogEntityScorecard.
    """
    scorecards = HasMany(
        cortex_catalog_entity_scorecard.CortexCatalogEntityScorecard,
        foreign_column_name="entity_tag",
    )

    """
    Related groups for this entity.

    HasMany relationship to CortexCatalogEntityGroup.
    """
    group_models = HasMany(
        cortex_catalog_entity_group.CortexCatalogEntityGroup,
        foreign_column_name="entity_tag",
    )

    # search columns

    """
    Search parameter: Filter by hierarchy depth level.
    """
    hierarchy_depth = String(is_searchable=True, is_temporary=True)

    """
    Search parameter: Filter by Git repository URLs.
    """
    git_repositories = StringList(is_searchable=True, is_temporary=True)

    """
    Search parameter: Filter by entity types (e.g., "service", "domain").
    """
    types = StringList(is_searchable=True, is_temporary=True)

    """
    Search parameter: Free-text search query.
    """
    query = String(is_searchable=True, is_temporary=True)

    """
    Search parameter: Include archived entities in results.
    """
    include_archived = Boolean(is_searchable=True, is_temporary=True)

    """
    Search parameter: Include metadata in response.
    """
    include_metadata = Boolean(is_searchable=True, is_temporary=True)

    """
    Search parameter: Include links in response.
    """
    include_links = Boolean(is_searchable=True, is_temporary=True)

    """
    Search parameter: Include owner information in response.
    """
    include_owners = Boolean(is_searchable=True)

    """
    Search parameter: Include nested fields in response (e.g., "team:members").
    """
    include_nested_fields = StringList(is_searchable=True, is_temporary=True)

    """
    Search parameter: Include hierarchy fields in response (e.g., "groups").
    """
    include_hierarchy_fields = StringList(is_searchable=True, is_temporary=True)

    def parse_hierarchy(self) -> dataclasses.ServiceEntityHierarchy:
        """Parse the hierarchy column into a dictionary."""
        return from_dict(dataclasses.ServiceEntityHierarchy, data=self.hierarchy)

    def parse_groups(self) -> dict[str, str]:
        """
        Parse the strings of groups.

        The groups is a list of string with key,value splitted by ':'.
        Return a dict with key value.
        """
        parsed: dict[str, str] = {}
        if self.groups:
            for entity in self.groups:
                splitted = entity.split(":")
                if len(splitted) > 1:
                    parsed[splitted[0]] = splitted[1]
        return parsed

    def parse_owners(self) -> dataclasses.EntityTeamOwner:
        """Parse the owners column into a dictionary."""
        return from_dict(dataclasses.EntityTeamOwner, data=self.owners)
