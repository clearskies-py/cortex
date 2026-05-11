"""
Factory functions for creating mock API responses.

This module provides factory classes for generating realistic mock responses
for each Cortex API resource type. These factories are used in tests to create
consistent, valid test data that matches the Cortex API specification.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from tests.fixtures.schemas import (
    make_cortex_response,
    make_entity_resource,
    make_git_details,
    make_hierarchy_node,
    make_individual_owner,
    make_link,
    make_metadata,
    make_owner_details,
    make_slack_channel,
    make_team_member,
    make_team_owner,
)


def _uuid() -> str:
    """Generate a random UUID string."""
    return str(uuid4())


def _entity_id() -> str:
    """Generate a Cortex entity ID (18-character format)."""
    return f"en{uuid4().hex[:16]}"


def _timestamp() -> str:
    """Generate an ISO 8601 timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class CatalogEntityResponseFactory:
    """Factory for catalog entity API responses."""

    @staticmethod
    def single(
        tag: str | None = None,
        name: str = "Test Service",
        entity_type: str = "service",
        id: str | None = None,
        description: str | None = None,
        groups: list[str] | None = None,
        is_archived: bool = False,
        git_repository: str | None = None,
        git_provider: str = "github",
        include_hierarchy: bool = True,
        include_owners: bool = True,
        include_links: bool = False,
        include_metadata: bool = False,
    ) -> dict[str, Any]:
        """
        Create a single catalog entity response (DetailsResponse format).

        Args:
            tag: Entity tag (auto-generated if not provided)
            name: Entity name
            entity_type: Type of entity (service, domain, team, etc.)
            id: Entity ID (auto-generated if not provided)
            description: Entity description
            groups: List of groups
            is_archived: Whether entity is archived
            git_repository: Git repository (e.g., "org/repo")
            git_provider: Git provider name
            include_hierarchy: Include hierarchy data
            include_owners: Include owner data
            include_links: Include links data
            include_metadata: Include metadata

        Returns:
            Cortex API formatted single entity response
        """
        tag = tag or f"test-{entity_type}-{_uuid()[:8]}"

        git = None
        if git_repository:
            git = make_git_details(git_repository, git_provider)

        hierarchy = None
        if include_hierarchy:
            hierarchy = {"parents": [], "children": []}

        owners = None
        if include_owners:
            owners = make_owner_details()

        links = None
        if include_links:
            links = [make_link("Documentation", "https://docs.example.com")]

        metadata = None
        if include_metadata:
            metadata = [make_metadata("environment", "production")]

        return make_entity_resource(
            tag=tag,
            name=name,
            entity_type=entity_type,
            id=id,
            description=description,
            groups=groups or [],
            is_archived=is_archived,
            git=git,
            hierarchy=hierarchy,
            owners=owners,
            links=links,
            metadata=metadata,
        )

    @staticmethod
    def list_entities(
        count: int = 3,
        entity_type: str = "service",
        groups: list[str] | None = None,
        page: int = 0,
        page_size: int = 250,
    ) -> dict[str, Any]:
        """
        Create a list of catalog entities response (ListCatalogEntities format).

        Args:
            count: Number of entities to generate
            entity_type: Type of entities
            groups: Common groups for all entities
            page: Current page number
            page_size: Page size

        Returns:
            Cortex API formatted list response with pagination
        """
        entities = [
            make_entity_resource(
                tag=f"test-{entity_type}-{i}",
                name=f"Test {entity_type.title()} {i}",
                entity_type=entity_type,
                groups=groups or [],
            )
            for i in range(count)
        ]

        total_pages = (count + page_size - 1) // page_size if count > 0 else 1

        return make_cortex_response(
            data=entities,
            data_key="entities",
            page=page,
            total=count,
            total_pages=total_pages,
        )

    @staticmethod
    def service(
        tag: str | None = None,
        name: str = "Test Service",
        git_repository: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a service entity response."""
        return CatalogEntityResponseFactory.single(
            tag=tag,
            name=name,
            entity_type="service",
            git_repository=git_repository or "org/test-service",
            **kwargs,
        )

    @staticmethod
    def domain(
        tag: str | None = None,
        name: str = "Test Domain",
        children: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a domain entity response."""
        entity = CatalogEntityResponseFactory.single(
            tag=tag,
            name=name,
            entity_type="domain",
            **kwargs,
        )

        if children:
            entity["hierarchy"]["children"] = children

        return entity

    @staticmethod
    def team(
        tag: str | None = None,
        name: str = "Test Team",
        members: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a team entity response."""
        entity = CatalogEntityResponseFactory.single(
            tag=tag,
            name=name,
            entity_type="team",
            **kwargs,
        )

        if members:
            entity["members"] = members

        return entity

    @staticmethod
    def with_hierarchy(
        tag: str = "child-service",
        name: str = "Child Service",
        entity_type: str = "service",
        parent_tag: str = "parent-domain",
        parent_name: str = "Parent Domain",
        parent_type: str = "domain",
    ) -> dict[str, Any]:
        """Create an entity with parent hierarchy."""
        entity = CatalogEntityResponseFactory.single(
            tag=tag,
            name=name,
            entity_type=entity_type,
        )

        entity["hierarchy"]["parents"] = [
            make_hierarchy_node(
                tag=parent_tag,
                name=parent_name,
                node_type=parent_type,
                parents=[],
            )
        ]

        return entity

    @staticmethod
    def with_owners(
        tag: str | None = None,
        name: str = "Owned Service",
        team_tag: str = "platform-team",
        team_name: str = "Platform Team",
        individual_email: str | None = None,
    ) -> dict[str, Any]:
        """Create an entity with owner information."""
        entity = CatalogEntityResponseFactory.single(
            tag=tag,
            name=name,
            include_owners=True,
        )

        teams = [make_team_owner(tag=team_tag, name=team_name)]
        individuals = []
        if individual_email:
            individuals = [make_individual_owner(email=individual_email)]

        entity["owners"] = make_owner_details(teams=teams, individuals=individuals)

        return entity


class TeamResponseFactory:
    """Factory for team API responses."""

    @staticmethod
    def single(
        team_tag: str | None = None,
        name: str = "Test Team",
        id: str | None = None,
        is_archived: bool = False,
        team_type: str = "CORTEX",
        members: list[dict[str, Any]] | None = None,
        links: list[dict[str, Any]] | None = None,
        slack_channels: list[dict[str, Any]] | None = None,
        parent_team_tag: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a single team response (TeamResponse format).

        Args:
            team_tag: Team tag (auto-generated if not provided)
            name: Team name
            id: Team ID (auto-generated if not provided)
            is_archived: Whether team is archived
            team_type: Team type (CORTEX or IDP)
            members: List of team members
            links: List of links
            slack_channels: List of Slack channels
            parent_team_tag: Parent team tag for hierarchy

        Returns:
            Cortex API formatted team response
        """
        team_tag = team_tag or f"test-team-{_uuid()[:8]}"

        response: dict[str, Any] = {
            "id": id or _entity_id(),
            "teamTag": team_tag,
            "catalogEntityTag": team_tag,
            "isArchived": is_archived,
            "type": team_type,
            "links": links or [],
            "slackChannels": slack_channels or [],
            "metadata": {
                "name": name,
                "description": f"Description for {name}",
            },
        }

        if team_type == "CORTEX":
            response["cortexTeam"] = {
                "members": members
                or [
                    {
                        "email": "member@example.com",
                        "name": "Team Member",
                        "notificationsEnabled": True,
                        "roles": [],
                    }
                ]
            }
        elif team_type == "IDP":
            response["idpGroup"] = {
                "group": "idp-group-name",
                "provider": "OKTA",
                "members": members or [],
            }

        if parent_team_tag:
            response["parentTeamTag"] = parent_team_tag

        return response

    @staticmethod
    def list(
        count: int = 3,
        team_type: str = "CORTEX",
    ) -> dict[str, Any]:
        """
        Create a list of teams response (AllTeamsResponse format).

        Args:
            count: Number of teams to generate
            team_type: Type of teams

        Returns:
            Cortex API formatted list response
        """
        teams = [
            TeamResponseFactory.single(
                team_tag=f"test-team-{i}",
                name=f"Test Team {i}",
                team_type=team_type,
            )
            for i in range(count)
        ]

        return {"teams": teams}

    @staticmethod
    def with_members(
        team_tag: str | None = None,
        name: str = "Team with Members",
        member_count: int = 3,
    ) -> dict[str, Any]:
        """Create a team with multiple members."""
        members = [
            {
                "email": f"member{i}@example.com",
                "name": f"Member {i}",
                "notificationsEnabled": True,
                "roles": [{"name": "Developer", "tag": "developer", "type": "TEAM_ROLE"}],
            }
            for i in range(member_count)
        ]

        return TeamResponseFactory.single(
            team_tag=team_tag,
            name=name,
            members=members,
        )

    @staticmethod
    def with_hierarchy(
        team_tag: str = "child-team",
        name: str = "Child Team",
        parent_team_tag: str = "parent-team",
    ) -> dict[str, Any]:
        """Create a team with parent hierarchy."""
        return TeamResponseFactory.single(
            team_tag=team_tag,
            name=name,
            parent_team_tag=parent_team_tag,
        )

    @staticmethod
    def idp_backed(
        team_tag: str | None = None,
        name: str = "IDP Team",
        provider: str = "OKTA",
        group: str = "okta-group",
    ) -> dict[str, Any]:
        """Create an IDP-backed team response."""
        team = TeamResponseFactory.single(
            team_tag=team_tag,
            name=name,
            team_type="IDP",
        )

        team["idpGroup"] = {
            "group": group,
            "provider": provider,
            "members": [],
        }

        return team


class ScorecardResponseFactory:
    """Factory for scorecard API responses."""

    @staticmethod
    def single(
        tag: str | None = None,
        name: str = "Test Scorecard",
        description: str | None = None,
        is_draft: bool = False,
        rules: list[dict[str, Any]] | None = None,
        levels: list[dict[str, Any]] | None = None,
        filter_query: str | None = None,
        filter_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a single scorecard response (ScorecardDescriptorResponse format).

        Args:
            tag: Scorecard tag (auto-generated if not provided)
            name: Scorecard name
            description: Scorecard description
            is_draft: Whether scorecard is a draft
            rules: List of scorecard rules
            levels: List of ladder levels
            filter_query: CQL filter query
            filter_types: Entity types to include

        Returns:
            Cortex API formatted scorecard response
        """
        tag = tag or f"test-scorecard-{_uuid()[:8]}"

        default_rules = rules or [
            {
                "expression": 'custom("key") = "value"',
                "title": "Has required custom data",
                "description": "Entity must have the required custom data key",
                "identifier": _uuid(),
                "weight": 1,
            },
            {
                "expression": "git != null",
                "title": "Has Git repository",
                "description": "Entity must have a Git repository configured",
                "identifier": _uuid(),
                "weight": 1,
            },
        ]

        default_levels = levels or [
            {"level": {"name": "Bronze", "number": 3}},
            {"level": {"name": "Silver", "number": 2}},
            {"level": {"name": "Gold", "number": 1}},
        ]

        filter_config: dict[str, Any] = {}
        if filter_query:
            filter_config["query"] = filter_query
        if filter_types:
            filter_config["types"] = {"include": filter_types}

        scorecard: dict[str, Any] = {
            "tag": tag,
            "name": name,
            "isDraft": is_draft,
            "lastUpdated": _timestamp(),
            "rules": default_rules,
            "levels": default_levels,
            "exemptions": {
                "enabled": True,
                "autoApprove": False,
            },
            "notifications": {
                "enabled": True,
                "scoreDropNotificationsEnabled": False,
            },
        }

        if description:
            scorecard["description"] = description

        if filter_config:
            scorecard["filter"] = filter_config

        return {"scorecard": scorecard}

    @staticmethod
    def list(
        count: int = 3,
        page: int = 0,
        page_size: int = 250,
    ) -> dict[str, Any]:
        """
        Create a list of scorecards response (PaginatedScorecardsResponse format).

        Args:
            count: Number of scorecards to generate
            page: Current page number
            page_size: Page size

        Returns:
            Cortex API formatted list response with pagination
        """
        scorecards = [
            ScorecardResponseFactory.single(
                tag=f"test-scorecard-{i}",
                name=f"Test Scorecard {i}",
            )["scorecard"]
            for i in range(count)
        ]

        total_pages = (count + page_size - 1) // page_size if count > 0 else 1

        return {
            "scorecards": scorecards,
            "page": page,
            "total": count,
            "totalPages": total_pages,
        }

    @staticmethod
    def scores(
        scorecard_tag: str = "test-scorecard",
        scorecard_name: str = "Test Scorecard",
        entity_count: int = 3,
        page: int = 0,
    ) -> dict[str, Any]:
        """
        Create a scorecard scores response (ScorecardServiceScore format).

        Args:
            scorecard_tag: Scorecard tag
            scorecard_name: Scorecard name
            entity_count: Number of entity scores to generate
            page: Current page number

        Returns:
            Cortex API formatted scores response
        """
        service_scores = [
            {
                "service": {
                    "id": _entity_id(),
                    "tag": f"test-service-{i}",
                    "name": f"Test Service {i}",
                    "groups": [],
                    "owners": {"groups": [], "individuals": []},
                },
                "score": {
                    "summary": {
                        "score": 75.0 + i * 5,
                        "totalPossibleScore": 100.0,
                        "percentage": 0.75 + i * 0.05,
                    },
                    "rules": [
                        {"expression": 'custom("key") = "value"', "score": 1, "identifier": _uuid()},
                        {"expression": "git != null", "score": 1, "identifier": _uuid()},
                    ],
                    "ladderLevels": [{"level": {"name": "Silver", "number": 2}}],
                },
                "lastEvaluated": _timestamp(),
                "ruleExemptions": [],
            }
            for i in range(entity_count)
        ]

        return {
            "scorecardId": 12345,
            "scorecardTag": scorecard_tag,
            "scorecardName": scorecard_name,
            "serviceScores": service_scores,
        }

    @staticmethod
    def next_steps(
        rules_to_complete: int = 2,
        current_level: str = "Bronze",
        next_level: str = "Silver",
    ) -> dict[str, Any]:
        """
        Create a next steps response (NextSteps1 format).

        Args:
            rules_to_complete: Number of rules remaining
            current_level: Current level name
            next_level: Next level name

        Returns:
            Cortex API formatted next steps response
        """
        rules = [
            {
                "expression": f'custom("requirement{i}") = true',
                "title": f"Requirement {i}",
                "description": f"Complete requirement {i} to advance",
                "identifier": _uuid(),
            }
            for i in range(rules_to_complete)
        ]

        return {
            "nextSteps": [
                {
                    "currentLevel": {"level": {"name": current_level, "number": 3}},
                    "nextLevel": {"level": {"name": next_level, "number": 2}},
                    "rulesToComplete": rules,
                }
            ]
        }


class EntityRelationshipResponseFactory:
    """Factory for entity relationship API responses."""

    @staticmethod
    def single(
        source_tag: str | None = None,
        target_tag: str | None = None,
        relationship_type: str = "DEPENDS_ON",
        id: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a single entity relationship response.

        Args:
            source_tag: Source entity tag
            target_tag: Target entity tag
            relationship_type: Type of relationship
            id: Relationship ID
            description: Relationship description

        Returns:
            Cortex API formatted relationship response
        """
        return {
            "id": id or _uuid(),
            "sourceEntityTag": source_tag or f"source-{_uuid()[:8]}",
            "targetEntityTag": target_tag or f"target-{_uuid()[:8]}",
            "type": relationship_type,
            "description": description,
        }

    @staticmethod
    def list(
        count: int = 3,
        source_tag: str | None = None,
        relationship_type: str = "DEPENDS_ON",
    ) -> dict[str, Any]:
        """
        Create a list of entity relationships response.

        Args:
            count: Number of relationships to generate
            source_tag: Common source entity tag
            relationship_type: Type of relationships

        Returns:
            Cortex API formatted list response
        """
        relationships = [
            EntityRelationshipResponseFactory.single(
                source_tag=source_tag or f"source-{i}",
                target_tag=f"target-{i}",
                relationship_type=relationship_type,
            )
            for i in range(count)
        ]

        return {
            "relationships": relationships,
            "page": 0,
            "total": count,
            "totalPages": 1,
        }


class DependencyResponseFactory:
    """Factory for dependency API responses."""

    @staticmethod
    def single(
        tag: str | None = None,
        method: str = "USES",
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a single dependency response.

        Args:
            tag: Dependency entity tag
            method: Dependency method (USES, CALLS, etc.)
            description: Dependency description
            metadata: Additional metadata

        Returns:
            Cortex API formatted dependency response
        """
        return {
            "tag": tag or f"dependency-{_uuid()[:8]}",
            "method": method,
            "description": description,
            "metadata": metadata or {},
        }

    @staticmethod
    def list(
        count: int = 3,
        method: str = "USES",
    ) -> dict[str, Any]:
        """
        Create a list of dependencies response.

        Args:
            count: Number of dependencies to generate
            method: Dependency method

        Returns:
            Cortex API formatted list response
        """
        dependencies = [
            DependencyResponseFactory.single(
                tag=f"dependency-{i}",
                method=method,
            )
            for i in range(count)
        ]

        return {
            "dependencies": dependencies,
        }


class CustomDataResponseFactory:
    """Factory for custom data API responses."""

    @staticmethod
    def single(
        key: str = "test-key",
        value: Any = "test-value",
    ) -> dict[str, Any]:
        """
        Create a single custom data response.

        Args:
            key: Custom data key
            value: Custom data value

        Returns:
            Cortex API formatted custom data response
        """
        return {
            "key": key,
            "value": value,
        }

    @staticmethod
    def list(
        count: int = 3,
    ) -> dict[str, Any]:
        """
        Create a list of custom data response.

        Args:
            count: Number of custom data entries to generate

        Returns:
            Cortex API formatted list response
        """
        values = [
            CustomDataResponseFactory.single(
                key=f"key-{i}",
                value=f"value-{i}",
            )
            for i in range(count)
        ]

        return {
            "values": values,
        }


class GroupResponseFactory:
    """Factory for group API responses."""

    @staticmethod
    def single(
        tag: str | None = None,
        name: str = "Test Group",
        description: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a single group response.

        Args:
            tag: Group tag
            name: Group name
            description: Group description

        Returns:
            Cortex API formatted group response
        """
        return {
            "tag": tag or f"test-group-{_uuid()[:8]}",
            "name": name,
            "description": description,
        }

    @staticmethod
    def list(
        count: int = 3,
    ) -> dict[str, Any]:
        """
        Create a list of groups response.

        Args:
            count: Number of groups to generate

        Returns:
            Cortex API formatted list response
        """
        groups = [
            GroupResponseFactory.single(
                tag=f"test-group-{i}",
                name=f"Test Group {i}",
            )
            for i in range(count)
        ]

        return {
            "groups": groups,
        }
