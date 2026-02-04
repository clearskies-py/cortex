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

    def get_group_tags(self) -> list[str]:
        """Get groups as simple tags.

        Returns groups that don't have a key:value format.

        Returns:
            List of group names that are simple tags without key:value format.

        Example:
            >>> entity.groups = ["my-tag", "team:platform", "production"]
            >>> entity.get_group_tags()
            ["my-tag", "production"]
        """
        tags: list[str] = []
        if self.groups:
            for group in self.groups:
                if ":" not in group:
                    tags.append(group)
        return tags

    def get_group_value(self, key: str) -> str | None:
        """Get the value for a specific group key.

        Groups can be formatted as "key:value" pairs. This method extracts
        the value for a given key.

        Args:
            key: The group key to look up.

        Returns:
            The value associated with the key, or None if not found.

        Example:
            >>> entity.groups = ["team:platform", "env:production"]
            >>> entity.get_group_value("team")
            "platform"
        """
        if self.groups:
            for group in self.groups:
                if group.startswith(f"{key}:"):
                    return group.split(":", 1)[1]
        return None

    def get_git_repository_url(self) -> str | None:
        """Get the Git repository URL.

        Returns:
            The repository URL, or None if not configured.

        Example:
            >>> entity.git = {"repository": "https://github.com/org/repo"}
            >>> entity.get_git_repository_url()
            "https://github.com/org/repo"
        """
        if not self.git:
            return None
        return self.git.get("repository") or self.git.get("repositoryUrl")

    def get_git_provider(self) -> str | None:
        """Get the Git provider name.

        Returns:
            The provider name (e.g., "github", "gitlab", "bitbucket", "azure-devops"),
            or None if not configured.

        Example:
            >>> entity.git = {"provider": "github", "repository": "..."}
            >>> entity.get_git_provider()
            "github"
        """
        if not self.git:
            return None
        return self.git.get("provider")

    def get_git_project_id(self) -> str | None:
        """Extract the project/repository identifier from the Git configuration.

        Cortex supports multiple SCM providers (GitHub, GitLab, Bitbucket, Azure DevOps).
        This method extracts the project identifier in a provider-agnostic way.

        For GitLab, this returns the numeric project ID if available in the URL.
        For GitHub/Bitbucket, this returns the "owner/repo" format.
        For Azure DevOps, this returns the project/repo path.

        Returns:
            The project identifier as a string, or None if not found.

        Example:
            >>> entity.git = {"repository": "https://github.com/org/repo"}
            >>> entity.get_git_project_id()
            "org/repo"

            >>> entity.git = {"repository": "https://gitlab.com/projects/12345"}
            >>> entity.get_git_project_id()
            "12345"
        """
        if not self.git:
            return None

        repo_url = self.git.get("repository") or self.git.get("repositoryUrl") or ""

        # GitLab numeric project ID format: https://gitlab.com/projects/12345
        if "/projects/" in repo_url:
            try:
                project_id = repo_url.split("/projects/")[1].split("/")[0]
                return project_id
            except IndexError:
                pass

        # Standard URL format: https://provider.com/owner/repo or https://provider.com/owner/repo.git
        # Works for GitHub, GitLab (path format), Bitbucket
        for prefix in ["github.com/", "gitlab.com/", "bitbucket.org/"]:
            if prefix in repo_url:
                try:
                    path = repo_url.split(prefix)[1]
                    # Remove .git suffix if present
                    if path.endswith(".git"):
                        path = path[:-4]
                    # Remove trailing slashes
                    path = path.rstrip("/")
                    # Return owner/repo format
                    parts = path.split("/")
                    if len(parts) >= 2:
                        return f"{parts[0]}/{parts[1]}"
                except IndexError:
                    pass

        # Azure DevOps format: https://dev.azure.com/org/project/_git/repo
        if "dev.azure.com/" in repo_url:
            try:
                path = repo_url.split("dev.azure.com/")[1]
                parts = path.split("/")
                if len(parts) >= 4 and parts[2] == "_git":
                    return f"{parts[0]}/{parts[1]}/{parts[3]}"
            except IndexError:
                pass

        return None

    @property
    def is_cloud_resource(self) -> bool:
        """Check if entity represents a cloud resource.

        Cortex supports pulling in resources from AWS, Azure, and Google Cloud.
        This property checks if the entity type indicates a cloud resource.

        Returns:
            True if the entity type indicates a cloud resource.

        Example:
            >>> entity.type = "AWS::Lambda::Function"
            >>> entity.is_cloud_resource
            True
        """
        if not self.type:
            return False
        cloud_prefixes = ("AWS::", "Azure::", "Google::")
        return self.type.startswith(cloud_prefixes)
