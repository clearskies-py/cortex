import unittest
from unittest.mock import MagicMock

import clearskies

from clearskies_cortex import dataclasses
from clearskies_cortex.models import CortexCatalogEntity


class TestCortexCatalogEntity(unittest.TestCase):
    """Tests for the CortexCatalogEntity model."""

    def test_destination_name(self):
        """Test that destination_name returns the correct API endpoint."""
        self.assertEqual(CortexCatalogEntity.destination_name(), "catalog")

    def test_id_column_name(self):
        """Test that the ID column is set to 'tag'."""
        self.assertEqual(CortexCatalogEntity.id_column_name, "tag")


class TestCortexCatalogEntityMethods(unittest.TestCase):
    """Tests for CortexCatalogEntity instance methods using clearskies context."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock requests object
        self.requests = MagicMock()

        class DummyCortexAuth:
            def __call__(self, r):
                return r

            def clear_credential_cache(self):
                pass

        self.auth = DummyCortexAuth()

    def _create_entity_with_data(self, data):
        """Create an entity with specific data using clearskies context."""
        response_data = {
            "entities": [data],
            "page": 0,
            "totalPages": 1,
            "total": 1,
        }

        response = MagicMock()
        response.ok = True
        response.content = b"..."
        response.json.return_value = response_data

        self.requests.request = MagicMock(return_value=response)

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

    def test_parse_groups_with_key_value_pairs(self):
        """Test parsing groups with key:value format."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "groups": ["team:platform", "env:production", "tier:1"]}
        )

        result = entity.parse_groups()

        self.assertEqual(result, {"team": "platform", "env": "production", "tier": "1"})

    def test_parse_groups_with_simple_tags(self):
        """Test parsing groups that are simple tags without key:value format."""
        entity = self._create_entity_with_data({"tag": "test-entity", "groups": ["my-tag", "another-tag"]})

        result = entity.parse_groups()

        # Simple tags without colons are not included in the dict
        self.assertEqual(result, {})

    def test_parse_groups_with_mixed_formats(self):
        """Test parsing groups with both key:value and simple tag formats."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "groups": ["team:platform", "my-tag", "env:production"]}
        )

        result = entity.parse_groups()

        self.assertEqual(result, {"team": "platform", "env": "production"})

    def test_parse_groups_with_empty_groups(self):
        """Test parsing empty groups list."""
        entity = self._create_entity_with_data({"tag": "test-entity", "groups": []})

        result = entity.parse_groups()

        self.assertEqual(result, {})

    def test_parse_groups_with_none_groups(self):
        """Test parsing when groups is None."""
        entity = self._create_entity_with_data({"tag": "test-entity", "groups": None})

        result = entity.parse_groups()

        self.assertEqual(result, {})

    def test_get_group_tags(self):
        """Test getting simple tags from groups."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "groups": ["my-tag", "team:platform", "production", "env:staging"]}
        )

        result = entity.get_group_tags()

        self.assertEqual(result, ["my-tag", "production"])

    def test_get_group_tags_with_no_simple_tags(self):
        """Test get_group_tags when all groups are key:value pairs."""
        entity = self._create_entity_with_data({"tag": "test-entity", "groups": ["team:platform", "env:production"]})

        result = entity.get_group_tags()

        self.assertEqual(result, [])

    def test_get_group_value(self):
        """Test getting a specific group value by key."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "groups": ["team:platform", "env:production", "tier:1"]}
        )

        self.assertEqual(entity.get_group_value("team"), "platform")
        self.assertEqual(entity.get_group_value("env"), "production")
        self.assertEqual(entity.get_group_value("tier"), "1")

    def test_get_group_value_not_found(self):
        """Test get_group_value when key doesn't exist."""
        entity = self._create_entity_with_data({"tag": "test-entity", "groups": ["team:platform"]})

        result = entity.get_group_value("env")

        self.assertIsNone(result)

    def test_get_group_value_with_colon_in_value(self):
        """Test get_group_value when value contains a colon."""
        entity = self._create_entity_with_data({"tag": "test-entity", "groups": ["url:https://example.com:8080"]})

        result = entity.get_group_value("url")

        self.assertEqual(result, "https://example.com:8080")

    def test_get_git_repository_url(self):
        """Test getting Git repository URL."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "git": {"repository": "https://github.com/org/repo"}}
        )

        result = entity.get_git_repository_url()

        self.assertEqual(result, "https://github.com/org/repo")

    def test_get_git_repository_url_with_repository_url_key(self):
        """Test getting Git repository URL with repositoryUrl key."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "git": {"repositoryUrl": "https://github.com/org/repo"}}
        )

        result = entity.get_git_repository_url()

        self.assertEqual(result, "https://github.com/org/repo")

    def test_get_git_repository_url_with_no_git(self):
        """Test get_git_repository_url when git is None."""
        entity = self._create_entity_with_data({"tag": "test-entity", "git": None})

        result = entity.get_git_repository_url()

        self.assertIsNone(result)

    def test_get_git_provider(self):
        """Test getting Git provider."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "git": {"provider": "github", "repository": "https://github.com/org/repo"}}
        )

        result = entity.get_git_provider()

        self.assertEqual(result, "github")

    def test_get_git_provider_with_no_git(self):
        """Test get_git_provider when git is None."""
        entity = self._create_entity_with_data({"tag": "test-entity", "git": None})

        result = entity.get_git_provider()

        self.assertIsNone(result)

    def test_get_git_project_id_github(self):
        """Test extracting project ID from GitHub URL."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "git": {"repository": "https://github.com/myorg/myrepo"}}
        )

        result = entity.get_git_project_id()

        self.assertEqual(result, "myorg/myrepo")

    def test_get_git_project_id_github_with_git_suffix(self):
        """Test extracting project ID from GitHub URL with .git suffix."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "git": {"repository": "https://github.com/myorg/myrepo.git"}}
        )

        result = entity.get_git_project_id()

        self.assertEqual(result, "myorg/myrepo")

    def test_get_git_project_id_gitlab(self):
        """Test extracting project ID from GitLab URL."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "git": {"repository": "https://gitlab.com/myorg/myrepo"}}
        )

        result = entity.get_git_project_id()

        self.assertEqual(result, "myorg/myrepo")

    def test_get_git_project_id_gitlab_numeric(self):
        """Test extracting numeric project ID from GitLab URL."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "git": {"repository": "https://gitlab.com/projects/12345"}}
        )

        result = entity.get_git_project_id()

        self.assertEqual(result, "12345")

    def test_get_git_project_id_bitbucket(self):
        """Test extracting project ID from Bitbucket URL."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "git": {"repository": "https://bitbucket.org/myorg/myrepo"}}
        )

        result = entity.get_git_project_id()

        self.assertEqual(result, "myorg/myrepo")

    def test_get_git_project_id_azure_devops(self):
        """Test extracting project ID from Azure DevOps URL."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "git": {"repository": "https://dev.azure.com/myorg/myproject/_git/myrepo"}}
        )

        result = entity.get_git_project_id()

        self.assertEqual(result, "myorg/myproject/myrepo")

    def test_get_git_project_id_with_no_git(self):
        """Test get_git_project_id when git is None."""
        entity = self._create_entity_with_data({"tag": "test-entity", "git": None})

        result = entity.get_git_project_id()

        self.assertIsNone(result)

    def test_get_git_project_id_unknown_provider(self):
        """Test get_git_project_id with unknown provider URL."""
        entity = self._create_entity_with_data(
            {"tag": "test-entity", "git": {"repository": "https://unknown.com/org/repo"}}
        )

        result = entity.get_git_project_id()

        self.assertIsNone(result)

    def test_is_cloud_resource_aws(self):
        """Test is_cloud_resource for AWS resources."""
        entity = self._create_entity_with_data({"tag": "test-entity", "type": "AWS::Lambda::Function"})

        self.assertTrue(entity.is_cloud_resource)

    def test_is_cloud_resource_azure(self):
        """Test is_cloud_resource for Azure resources."""
        entity = self._create_entity_with_data({"tag": "test-entity", "type": "Azure::Functions::FunctionApp"})

        self.assertTrue(entity.is_cloud_resource)

    def test_is_cloud_resource_google(self):
        """Test is_cloud_resource for Google Cloud resources."""
        entity = self._create_entity_with_data({"tag": "test-entity", "type": "Google::CloudFunctions::Function"})

        self.assertTrue(entity.is_cloud_resource)

    def test_is_cloud_resource_service(self):
        """Test is_cloud_resource for regular service."""
        entity = self._create_entity_with_data({"tag": "test-entity", "type": "service"})

        self.assertFalse(entity.is_cloud_resource)

    def test_is_cloud_resource_domain(self):
        """Test is_cloud_resource for domain entity."""
        entity = self._create_entity_with_data({"tag": "test-entity", "type": "domain"})

        self.assertFalse(entity.is_cloud_resource)

    def test_is_cloud_resource_with_none_type(self):
        """Test is_cloud_resource when type is None."""
        entity = self._create_entity_with_data({"tag": "test-entity", "type": None})

        self.assertFalse(entity.is_cloud_resource)

    def test_parse_hierarchy_with_data(self):
        """Test parsing hierarchy data."""
        entity = self._create_entity_with_data(
            {
                "tag": "test-entity",
                "hierarchy": {
                    "parents": [
                        {
                            "tag": "parent-domain",
                            "type": "domain",
                            "name": "Parent Domain",
                            "description": "A parent domain",
                            "definition": None,
                            "parents": [],
                            "groups": ["team:platform"],
                        }
                    ],
                    "children": [
                        {
                            "tag": "child-service",
                            "type": "service",
                            "name": "Child Service",
                            "description": "A child service",
                            "definition": None,
                            "children": [],
                            "groups": None,
                        }
                    ],
                },
            }
        )

        result = entity.parse_hierarchy()

        self.assertIsInstance(result, dataclasses.ServiceEntityHierarchy)
        self.assertEqual(len(result.parents), 1)
        self.assertEqual(result.parents[0].tag, "parent-domain")
        self.assertEqual(result.parents[0].type, "domain")
        self.assertEqual(len(result.children), 1)
        self.assertEqual(result.children[0].tag, "child-service")

    def test_parse_hierarchy_with_none(self):
        """Test parsing hierarchy when it's None."""
        entity = self._create_entity_with_data({"tag": "test-entity", "hierarchy": None})

        result = entity.parse_hierarchy()

        self.assertIsInstance(result, dataclasses.ServiceEntityHierarchy)
        self.assertEqual(result.parents, [])
        self.assertEqual(result.children, [])

    def test_parse_owners_with_data(self):
        """Test parsing owners data."""
        entity = self._create_entity_with_data(
            {
                "tag": "test-entity",
                "owners": {
                    "teams": [
                        {
                            "tag": "platform-team",
                            "name": "Platform Team",
                            "description": "The platform team",
                            "inheritance": "direct",
                            "isArchived": False,
                            "provider": "cortex",
                        }
                    ],
                    "individuals": [{"email": "user@example.com", "description": "Team lead"}],
                },
            }
        )

        result = entity.parse_owners()

        self.assertIsInstance(result, dataclasses.EntityTeamOwner)
        self.assertEqual(len(result.teams), 1)
        self.assertEqual(result.teams[0].tag, "platform-team")
        self.assertEqual(len(result.individuals), 1)
        self.assertEqual(result.individuals[0].email, "user@example.com")

    def test_parse_owners_with_none(self):
        """Test parsing owners when it's None."""
        entity = self._create_entity_with_data({"tag": "test-entity", "owners": None})

        result = entity.parse_owners()

        self.assertIsInstance(result, dataclasses.EntityTeamOwner)
        self.assertEqual(result.teams, [])
        self.assertEqual(result.individuals, [])


class TestCortexCatalogEntityColumns(unittest.TestCase):
    """Tests for CortexCatalogEntity column definitions."""

    def test_has_required_columns(self):
        """Test that the model has all required columns."""
        columns = CortexCatalogEntity.get_columns()
        column_names = list(columns.keys())

        required_columns = [
            "id",
            "tag",
            "groups",
            "owners",
            "ownership",
            "owners_v2",
            "description",
            "git",
            "hierarchy",
            "last_updated",
            "is_archived",
            "links",
            "members",
            "metadata",
            "slack_channels",
            "name",
            "type",
        ]

        for col in required_columns:
            self.assertIn(col, column_names, f"Missing column: {col}")

    def test_has_search_columns(self):
        """Test that the model has searchable columns."""
        columns = CortexCatalogEntity.get_columns()

        searchable_columns = [
            "hierarchy_depth",
            "git_repositories",
            "types",
            "query",
            "include_archived",
            "include_metadata",
            "include_links",
            "include_owners",
            "include_nested_fields",
            "include_hierarchy_fields",
        ]

        for col in searchable_columns:
            self.assertIn(col, columns, f"Missing searchable column: {col}")
            self.assertTrue(columns[col].is_searchable, f"Column {col} should be searchable")


if __name__ == "__main__":
    unittest.main()
