"""
Validation tests for Cortex API compliance.

These tests verify that the models and fixtures correctly match
the Cortex API specification schemas.
"""

import unittest
from unittest.mock import MagicMock

import clearskies

from clearskies_cortex.models import (
    CortexCatalogEntity,
    CortexTeam,
)
from tests.fixtures.api_responses import (
    CatalogEntityResponseFactory,
    ScorecardResponseFactory,
    TeamResponseFactory,
)


class DummyCortexAuth:
    """Dummy auth for testing."""

    def __call__(self, r):
        return r

    def clear_credential_cache(self):
        pass


class TestCatalogEntityAPICompliance(unittest.TestCase):
    """Tests for CortexCatalogEntity API compliance."""

    def setUp(self):
        """Set up test fixtures."""
        self.requests = MagicMock()
        self.auth = DummyCortexAuth()

    def _mock_response(self, data: dict):
        """Create a mock response with the given data."""
        response = MagicMock()
        response.ok = True
        response.content = b"..."
        response.json.return_value = data
        self.requests.request = MagicMock(return_value=response)

    def _get_first_entity(self, response_data: dict):
        """Get first entity using clearskies context."""
        self._mock_response(response_data)

        def get_entity(cortex_entities: CortexCatalogEntity):
            for entity in cortex_entities:
                return entity
            return None

        _, result, _ = clearskies.contexts.Context(
            clearskies.endpoints.Callable(get_entity),
            classes=[CortexCatalogEntity],
            bindings={"requests": self.requests, "cortex_auth": self.auth},
        )()

        return result["data"]

    def _get_entities(self, response_data: dict, count: int = 3):
        """Get multiple entities using clearskies context."""
        self._mock_response(response_data)

        def get_entities(cortex_entities: CortexCatalogEntity):
            entities = []
            for entity in cortex_entities:
                entities.append(entity)
                if len(entities) >= count:
                    break
            return {"entities": entities}

        _, result, _ = clearskies.contexts.Context(
            clearskies.endpoints.Callable(get_entities),
            classes=[CortexCatalogEntity],
            bindings={"requests": self.requests, "cortex_auth": self.auth},
        )()

        return result["data"]["entities"]

    def test_list_entities_response_format(self):
        """Test that list entities response matches API spec."""
        response_data = CatalogEntityResponseFactory.list_entities(count=3)

        entities = self._get_entities(response_data, count=3)

        self.assertEqual(len(entities), 3)
        for entity in entities:
            # Verify required fields from API spec
            self.assertIsNotNone(entity.tag)
            self.assertIsNotNone(entity.name)
            self.assertIsNotNone(entity.type)
            self.assertIsNotNone(entity.id)

    def test_single_entity_response_format(self):
        """Test that single entity response matches API spec."""
        entity_data = CatalogEntityResponseFactory.single(
            tag="my-service",
            name="My Service",
            entity_type="service",
            description="A test service",
            groups=["team:platform", "env:production"],
            git_repository="org/my-service",
        )
        response_data = {
            "entities": [entity_data],
            "page": 0,
            "total": 1,
            "totalPages": 1,
        }

        entity = self._get_first_entity(response_data)

        # Verify all fields from DetailsResponse schema
        self.assertEqual(entity.tag, "my-service")
        self.assertEqual(entity.name, "My Service")
        self.assertEqual(entity.type, "service")
        self.assertEqual(entity.description, "A test service")
        self.assertEqual(entity.groups, ["team:platform", "env:production"])
        self.assertIsNotNone(entity.git)
        self.assertEqual(entity.git["provider"], "github")

    def test_entity_with_hierarchy(self):
        """Test entity with hierarchy matches API spec."""
        entity_data = CatalogEntityResponseFactory.with_hierarchy(
            tag="child-service",
            name="Child Service",
            parent_tag="parent-domain",
            parent_name="Parent Domain",
        )
        response_data = {
            "entities": [entity_data],
            "page": 0,
            "total": 1,
            "totalPages": 1,
        }

        entity = self._get_first_entity(response_data)

        # Verify hierarchy structure matches EntityHierarchyDetails schema
        self.assertIsNotNone(entity.hierarchy)
        self.assertIn("parents", entity.hierarchy)
        self.assertIn("children", entity.hierarchy)
        self.assertEqual(len(entity.hierarchy["parents"]), 1)
        self.assertEqual(entity.hierarchy["parents"][0]["tag"], "parent-domain")

    def test_entity_with_owners(self):
        """Test entity with owners matches API spec."""
        entity_data = CatalogEntityResponseFactory.with_owners(
            tag="owned-service",
            name="Owned Service",
            team_tag="platform-team",
            team_name="Platform Team",
            individual_email="owner@example.com",
        )
        response_data = {
            "entities": [entity_data],
            "page": 0,
            "total": 1,
            "totalPages": 1,
        }

        entity = self._get_first_entity(response_data)

        # Verify owners structure matches OwnersDetails schema
        self.assertIsNotNone(entity.owners)
        self.assertIn("teams", entity.owners)
        self.assertIn("individuals", entity.owners)
        self.assertEqual(len(entity.owners["teams"]), 1)
        self.assertEqual(entity.owners["teams"][0]["tag"], "platform-team")
        self.assertEqual(len(entity.owners["individuals"]), 1)
        self.assertEqual(entity.owners["individuals"][0]["email"], "owner@example.com")

    def test_service_entity_type(self):
        """Test service entity matches API spec."""
        entity_data = CatalogEntityResponseFactory.service(
            tag="my-service",
            name="My Service",
        )
        response_data = {
            "entities": [entity_data],
            "page": 0,
            "total": 1,
            "totalPages": 1,
        }

        entity = self._get_first_entity(response_data)

        self.assertEqual(entity.type, "service")
        self.assertIsNotNone(entity.git)

    def test_domain_entity_type(self):
        """Test domain entity matches API spec."""
        entity_data = CatalogEntityResponseFactory.domain(
            tag="my-domain",
            name="My Domain",
        )
        response_data = {
            "entities": [entity_data],
            "page": 0,
            "total": 1,
            "totalPages": 1,
        }

        entity = self._get_first_entity(response_data)

        self.assertEqual(entity.type, "domain")

    def test_team_entity_type(self):
        """Test team entity matches API spec."""
        entity_data = CatalogEntityResponseFactory.team(
            tag="my-team",
            name="My Team",
        )
        response_data = {
            "entities": [entity_data],
            "page": 0,
            "total": 1,
            "totalPages": 1,
        }

        entity = self._get_first_entity(response_data)

        self.assertEqual(entity.type, "team")


class TestTeamAPICompliance(unittest.TestCase):
    """Tests for CortexTeam API compliance."""

    def setUp(self):
        """Set up test fixtures."""
        self.requests = MagicMock()
        self.auth = DummyCortexAuth()

    def _mock_response(self, data: dict):
        """Create a mock response with the given data."""
        response = MagicMock()
        response.ok = True
        response.content = b"..."
        response.json.return_value = data
        self.requests.request = MagicMock(return_value=response)

    def _get_first_team(self, response_data: dict):
        """Get first team using clearskies context."""
        self._mock_response(response_data)

        def get_team(cortex_teams: CortexTeam):
            for team in cortex_teams:
                return team
            return None

        _, result, _ = clearskies.contexts.Context(
            clearskies.endpoints.Callable(get_team),
            classes=[CortexTeam],
            bindings={"requests": self.requests, "cortex_auth": self.auth},
        )()

        return result["data"]

    def _get_teams(self, response_data: dict, count: int = 3):
        """Get multiple teams using clearskies context."""
        self._mock_response(response_data)

        def get_teams(cortex_teams: CortexTeam):
            teams = []
            for team in cortex_teams:
                teams.append(team)
                if len(teams) >= count:
                    break
            return {"teams": teams}

        _, result, _ = clearskies.contexts.Context(
            clearskies.endpoints.Callable(get_teams),
            classes=[CortexTeam],
            bindings={"requests": self.requests, "cortex_auth": self.auth},
        )()

        return result["data"]["teams"]

    def test_list_teams_response_format(self):
        """Test that list teams response matches API spec."""
        response_data = TeamResponseFactory.list(count=3)

        teams = self._get_teams(response_data, count=3)

        self.assertEqual(len(teams), 3)
        for team in teams:
            # Verify required fields from TeamResponse schema
            self.assertIsNotNone(team.team_tag)
            self.assertIsNotNone(team.id)
            self.assertIsNotNone(team.type)

    def test_single_team_response_format(self):
        """Test that single team response matches API spec."""
        team_data = TeamResponseFactory.single(
            team_tag="my-team",
            name="My Team",
            team_type="CORTEX",
        )
        response_data = {"teams": [team_data]}

        team = self._get_first_team(response_data)

        # Verify all fields from TeamResponse schema
        self.assertEqual(team.team_tag, "my-team")
        self.assertEqual(team.type, "CORTEX")
        self.assertIsNotNone(team.metadata)
        self.assertEqual(team.get_name(), "My Team")

    def test_team_with_members(self):
        """Test team with members matches API spec."""
        team_data = TeamResponseFactory.with_members(
            team_tag="team-with-members",
            name="Team with Members",
            member_count=3,
        )
        response_data = {"teams": [team_data]}

        team = self._get_first_team(response_data)

        # Verify members structure matches CortexTeamDetails schema
        self.assertIsNotNone(team.members)
        self.assertEqual(len(team.members), 3)
        for member in team.members:
            self.assertIn("email", member)
            self.assertIn("name", member)

    def test_idp_backed_team(self):
        """Test IDP-backed team matches API spec."""
        team_data = TeamResponseFactory.idp_backed(
            team_tag="idp-team",
            name="IDP Team",
            provider="OKTA",
            group="okta-group",
        )
        response_data = {"teams": [team_data]}

        team = self._get_first_team(response_data)

        # Verify IDP group structure matches IdpGroupDetailsResponse schema
        self.assertEqual(team.type, "IDP")


class TestScorecardAPICompliance(unittest.TestCase):
    """Tests for CortexScorecard API compliance."""

    def test_scorecard_response_structure(self):
        """Test that scorecard response matches API spec."""
        scorecard_data = ScorecardResponseFactory.single(
            tag="production-readiness",
            name="Production Readiness",
            description="Checks for production readiness",
        )

        # Verify structure matches ScorecardDescriptorResponse schema
        self.assertIn("scorecard", scorecard_data)
        scorecard = scorecard_data["scorecard"]

        # Required fields
        self.assertIn("tag", scorecard)
        self.assertIn("name", scorecard)
        self.assertIn("isDraft", scorecard)
        self.assertIn("lastUpdated", scorecard)
        self.assertIn("rules", scorecard)
        self.assertIn("exemptions", scorecard)
        self.assertIn("notifications", scorecard)

        # Verify rules structure
        self.assertIsInstance(scorecard["rules"], list)
        for rule in scorecard["rules"]:
            self.assertIn("expression", rule)
            self.assertIn("identifier", rule)

        # Verify exemptions structure
        self.assertIn("enabled", scorecard["exemptions"])
        self.assertIn("autoApprove", scorecard["exemptions"])

        # Verify notifications structure
        self.assertIn("enabled", scorecard["notifications"])
        self.assertIn("scoreDropNotificationsEnabled", scorecard["notifications"])

    def test_scorecard_list_response_structure(self):
        """Test that scorecard list response matches API spec."""
        response_data = ScorecardResponseFactory.list(count=3)

        # Verify structure matches PaginatedScorecardsResponse schema
        self.assertIn("scorecards", response_data)
        self.assertIn("page", response_data)
        self.assertIn("total", response_data)
        self.assertIn("totalPages", response_data)

        self.assertEqual(len(response_data["scorecards"]), 3)
        self.assertEqual(response_data["total"], 3)

    def test_scorecard_scores_response_structure(self):
        """Test that scorecard scores response matches API spec."""
        response_data = ScorecardResponseFactory.scores(
            scorecard_tag="test-scorecard",
            scorecard_name="Test Scorecard",
            entity_count=3,
        )

        # Verify structure matches ScorecardServiceScore schema
        self.assertIn("scorecardId", response_data)
        self.assertIn("scorecardTag", response_data)
        self.assertIn("scorecardName", response_data)
        self.assertIn("serviceScores", response_data)

        self.assertEqual(len(response_data["serviceScores"]), 3)

        for score in response_data["serviceScores"]:
            # Verify ServiceScore structure
            self.assertIn("service", score)
            self.assertIn("score", score)
            self.assertIn("lastEvaluated", score)
            self.assertIn("ruleExemptions", score)

            # Verify service structure
            self.assertIn("id", score["service"])
            self.assertIn("tag", score["service"])
            self.assertIn("name", score["service"])

            # Verify score details structure
            self.assertIn("summary", score["score"])
            self.assertIn("rules", score["score"])
            self.assertIn("ladderLevels", score["score"])

    def test_scorecard_next_steps_response_structure(self):
        """Test that scorecard next steps response matches API spec."""
        response_data = ScorecardResponseFactory.next_steps(
            rules_to_complete=2,
            current_level="Bronze",
            next_level="Silver",
        )

        # Verify structure matches NextSteps1 schema
        self.assertIn("nextSteps", response_data)
        self.assertEqual(len(response_data["nextSteps"]), 1)

        next_step = response_data["nextSteps"][0]
        self.assertIn("currentLevel", next_step)
        self.assertIn("nextLevel", next_step)
        self.assertIn("rulesToComplete", next_step)

        # Verify level structure
        self.assertIn("level", next_step["currentLevel"])
        self.assertEqual(next_step["currentLevel"]["level"]["name"], "Bronze")

        # Verify rules to complete
        self.assertEqual(len(next_step["rulesToComplete"]), 2)
        for rule in next_step["rulesToComplete"]:
            self.assertIn("expression", rule)
            self.assertIn("title", rule)
            self.assertIn("identifier", rule)


class TestFixtureSchemaCompliance(unittest.TestCase):
    """Tests for fixture schema compliance with API spec."""

    def test_entity_id_format(self):
        """Test that entity IDs follow the Cortex format."""
        entity = CatalogEntityResponseFactory.single()

        # Cortex entity IDs start with 'en' followed by 16 hex characters
        self.assertTrue(entity["id"].startswith("en"))
        self.assertEqual(len(entity["id"]), 18)

    def test_timestamp_format(self):
        """Test that timestamps follow ISO 8601 format."""
        entity = CatalogEntityResponseFactory.single()

        # Should be ISO 8601 format with Z suffix
        self.assertTrue(entity["lastUpdated"].endswith("Z"))
        self.assertIn("T", entity["lastUpdated"])

    def test_hierarchy_structure(self):
        """Test that hierarchy structure matches API spec."""
        entity = CatalogEntityResponseFactory.single(include_hierarchy=True)

        hierarchy = entity["hierarchy"]
        self.assertIn("parents", hierarchy)
        self.assertIn("children", hierarchy)
        self.assertIsInstance(hierarchy["parents"], list)
        self.assertIsInstance(hierarchy["children"], list)

    def test_owners_structure(self):
        """Test that owners structure matches API spec."""
        entity = CatalogEntityResponseFactory.with_owners(
            team_tag="test-team",
            team_name="Test Team",
            individual_email="test@example.com",
        )

        owners = entity["owners"]
        self.assertIn("teams", owners)
        self.assertIn("individuals", owners)

        # Verify team owner structure
        team = owners["teams"][0]
        self.assertIn("id", team)
        self.assertIn("tag", team)
        self.assertIn("name", team)
        self.assertIn("isArchived", team)

        # Verify individual owner structure
        individual = owners["individuals"][0]
        self.assertIn("email", individual)

    def test_git_details_structure(self):
        """Test that git details structure matches API spec."""
        entity = CatalogEntityResponseFactory.service(
            git_repository="org/repo",
        )

        git = entity["git"]
        self.assertIn("repository", git)
        self.assertIn("provider", git)
        self.assertIn("repositoryUrl", git)

    def test_link_structure(self):
        """Test that link structure matches API spec."""
        entity = CatalogEntityResponseFactory.single(include_links=True)

        links = entity["links"]
        self.assertIsInstance(links, list)
        if links:
            link = links[0]
            self.assertIn("name", link)
            self.assertIn("url", link)
            self.assertIn("type", link)

    def test_metadata_structure(self):
        """Test that metadata structure matches API spec."""
        entity = CatalogEntityResponseFactory.single(include_metadata=True)

        metadata = entity["metadata"]
        self.assertIsInstance(metadata, list)
        if metadata:
            item = metadata[0]
            self.assertIn("key", item)
            self.assertIn("value", item)

    def test_slack_channel_structure(self):
        """Test that slack channel structure matches API spec."""
        entity = CatalogEntityResponseFactory.single()

        slack_channels = entity["slackChannels"]
        self.assertIsInstance(slack_channels, list)

    def test_team_member_structure(self):
        """Test that team member structure matches API spec."""
        team = TeamResponseFactory.with_members(member_count=1)

        members = team["cortexTeam"]["members"]
        self.assertEqual(len(members), 1)

        member = members[0]
        self.assertIn("email", member)
        self.assertIn("name", member)
        self.assertIn("roles", member)


if __name__ == "__main__":
    unittest.main()
