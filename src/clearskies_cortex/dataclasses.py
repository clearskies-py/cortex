from dataclasses import dataclass
from typing import Any


@dataclass
class ServiceEntityHierarchy:
    """Dataclass for parent in service hierarchy."""

    parents: list["ServiceEntityHierarchyParent"]
    children: list["ServiceEntityHierarchyChild"]


@dataclass
class ServiceEntityHierarchyParent:
    """Dataclass for parent in hierarchy."""

    tag: str
    type: str
    name: str
    description: str | None
    definition: None | dict[str, Any]
    parents: list["ServiceEntityHierarchyParent"]
    groups: list[str] | None


@dataclass
class ServiceEntityHierarchyChild:
    """Dataclass for child in hierarchy."""

    tag: str
    type: str
    name: str
    description: str | None
    definition: None | dict[str, Any]
    children: list["ServiceEntityHierarchyChild"]
    groups: list[str] | None


@dataclass
class TeamCategory:
    """Dataclass for Team Category Tree."""

    name: str
    level: int
    parent_name: str


@dataclass
class EntityTeam:
    """Dataclass for team in Catalog Entity."""

    description: str | None
    inheritance: str
    isArchived: bool  # noqa: N815
    name: str
    provider: str
    tag: str


@dataclass
class EntityIndividual:
    """Dataclass for individual in Catalog Entity."""

    description: str | None
    email: str


@dataclass
class EntityTeamOwner:
    """Dataclass for team owners in Catalog Entity."""

    teams: list[EntityTeam]
    individuals: list[EntityIndividual]
