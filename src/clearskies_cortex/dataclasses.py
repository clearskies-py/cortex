from dataclasses import dataclass
from typing import Any


@dataclass
class ServiceEntityHierarchy:
    """
    Dataclass representing the hierarchy structure of a service entity.

    This dataclass is used to parse the hierarchy JSON data from Cortex catalog entities.
    It contains both parent and child relationships for navigating the entity hierarchy.

    ```python
    from clearskies_cortex.models import CortexCatalogEntity

    entity = CortexCatalogEntity().find("tag=my-service")
    hierarchy = entity.parse_hierarchy()

    # Access parents
    for parent in hierarchy.parents:
        print(f"Parent: {parent.name} ({parent.type})")

    # Access children
    for child in hierarchy.children:
        print(f"Child: {child.name} ({child.type})")
    ```
    """

    """
    List of parent entities in the hierarchy (from immediate parent to root).
    """
    parents: list["ServiceEntityHierarchyParent"]

    """
    List of child entities in the hierarchy.
    """
    children: list["ServiceEntityHierarchyChild"]


@dataclass
class ServiceEntityHierarchyParent:
    """
    Dataclass representing a parent entity in the hierarchy.

    Contains information about a parent entity including its tag, type, name,
    and recursively its own parents for traversing up the hierarchy tree.
    """

    """
    The unique tag identifier of the parent entity.
    """
    tag: str

    """
    The type of the parent entity (e.g., "domain", "team").
    """
    type: str

    """
    The human-readable name of the parent entity.
    """
    name: str

    """
    Optional description of the parent entity.
    """
    description: str | None

    """
    Optional definition data for the parent entity.
    """
    definition: None | dict[str, Any]

    """
    List of grandparent entities (recursive parent structure).
    """
    parents: list["ServiceEntityHierarchyParent"]

    """
    Optional list of groups the parent entity belongs to.
    """
    groups: list[str] | None


@dataclass
class ServiceEntityHierarchyChild:
    """
    Dataclass representing a child entity in the hierarchy.

    Contains information about a child entity including its tag, type, name,
    and recursively its own children for traversing down the hierarchy tree.
    """

    """
    The unique tag identifier of the child entity.
    """
    tag: str

    """
    The type of the child entity (e.g., "service", "domain").
    """
    type: str

    """
    The human-readable name of the child entity.
    """
    name: str

    """
    Optional description of the child entity.
    """
    description: str | None

    """
    Optional definition data for the child entity.
    """
    definition: None | dict[str, Any]

    """
    List of grandchild entities (recursive child structure).
    """
    children: list["ServiceEntityHierarchyChild"]

    """
    Optional list of groups the child entity belongs to.
    """
    groups: list[str] | None


@dataclass
class TeamCategory:
    """
    Dataclass representing a team category in the category tree.

    Used for organizing teams into hierarchical categories with parent-child relationships.
    """

    """
    The name of the category.
    """
    name: str

    """
    The depth level in the category hierarchy (0 for root).
    """
    level: int

    """
    The name of the parent category.
    """
    parent_name: str


@dataclass
class EntityTeam:
    """
    Dataclass representing a team associated with a catalog entity.

    Contains team information including ownership inheritance and provider details.
    """

    """
    Optional description of the team.
    """
    description: str | None

    """
    The inheritance type for ownership (e.g., "direct", "inherited").
    """
    inheritance: str

    """
    Whether the team is archived.
    """
    isArchived: bool  # noqa: N815

    """
    The human-readable name of the team.
    """
    name: str

    """
    The provider of the team data (e.g., "cortex", "external").
    """
    provider: str

    """
    The unique tag identifier of the team.
    """
    tag: str


@dataclass
class EntityIndividual:
    """
    Dataclass representing an individual owner of a catalog entity.

    Contains information about individual (non-team) owners.
    """

    """
    Optional description of the individual.
    """
    description: str | None

    """
    The email address of the individual.
    """
    email: str


@dataclass
class EntityTeamOwner:
    """
    Dataclass representing the ownership information for a catalog entity.

    Contains both team and individual owners. Used by `CortexCatalogEntity.parse_owners()`.

    ```python
    from clearskies_cortex.models import CortexCatalogEntity

    entity = CortexCatalogEntity().find("tag=my-service")
    owners = entity.parse_owners()

    # Access team owners
    for team in owners.teams:
        print(f"Team owner: {team.name} ({team.tag})")

    # Access individual owners
    for individual in owners.individuals:
        print(f"Individual owner: {individual.email}")
    ```
    """

    """
    List of teams that own the entity.
    """
    teams: list[EntityTeam]

    """
    List of individuals that own the entity.
    """
    individuals: list[EntityIndividual]
