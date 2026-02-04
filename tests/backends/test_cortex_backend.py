import unittest
from unittest.mock import MagicMock

import clearskies

from clearskies_cortex.backends import CortexBackend


class CortexEntity(clearskies.Model):
    """Test model for CortexBackend tests."""

    id_column_name = "tag"
    backend = CortexBackend()

    @classmethod
    def destination_name(cls) -> str:
        return "catalog/entities"

    tag = clearskies.columns.String()
    name = clearskies.columns.String()
    description = clearskies.columns.String()


class TestCortexBackendPagination(unittest.TestCase):
    """Tests for CortexBackend pagination functionality.

    The Cortex API uses 0-indexed pages:
    - page=0 is the first page
    - page=totalPages-1 is the last page
    - There are more pages if page + 1 < totalPages
    """

    def test_pagination_data_not_mutated_by_map_records_response(self):
        """Test that map_records_response doesn't mutate the response data.

        This is critical because get_next_page_data_from_response() is called
        after map_records_response() and needs access to the pagination fields.
        """
        response_data = {
            "entities": [
                {"tag": "entity-1", "name": "Entity 1"},
                {"tag": "entity-2", "name": "Entity 2"},
            ],
            "page": 0,
            "totalPages": 3,
            "total": 50,
        }

        query = MagicMock()
        query.model_class = CortexEntity
        query.conditions = []

        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        records = backend.map_records_response(response_data, query)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["tag"], "entity-1")
        self.assertEqual(records[1]["tag"], "entity-2")

        # Verify pagination data was NOT mutated
        self.assertIn("page", response_data, "page field was deleted from response_data")
        self.assertIn("totalPages", response_data, "totalPages field was deleted from response_data")
        self.assertIn("total", response_data, "total field was deleted from response_data")
        self.assertEqual(response_data["page"], 0)
        self.assertEqual(response_data["totalPages"], 3)
        self.assertEqual(response_data["total"], 50)

    def test_get_next_page_data_from_response_returns_next_page(self):
        """Test that get_next_page_data_from_response correctly extracts next page info.

        With 0-indexed pages: page=0, totalPages=3 means pages 0, 1, 2 exist.
        So next page should be 1.
        """
        response = MagicMock()
        response.content = b'{"entities": [], "page": 0, "totalPages": 3, "total": 50}'
        response.json.return_value = {
            "entities": [],
            "page": 0,
            "totalPages": 3,
            "total": 50,
        }

        query = MagicMock()

        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        next_page_data = backend.get_next_page_data_from_response(query, response)

        self.assertEqual(next_page_data["page"], 1)
        self.assertEqual(next_page_data["total_count"], 50)
        self.assertEqual(next_page_data["total_pages"], 3)

    def test_get_next_page_data_from_response_no_next_page_on_last_page(self):
        """Test that get_next_page_data_from_response returns empty when on last page.

        With 0-indexed pages: page=2, totalPages=3 means we're on the last page.
        (pages 0, 1, 2 exist, and we're on page 2)
        """
        response = MagicMock()
        response.content = b'{"entities": [], "page": 2, "totalPages": 3, "total": 50}'
        response.json.return_value = {
            "entities": [],
            "page": 2,
            "totalPages": 3,
            "total": 50,
        }

        query = MagicMock()

        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        next_page_data = backend.get_next_page_data_from_response(query, response)

        # No next page should be returned when on the last page
        self.assertNotIn("page", next_page_data)
        # But count info should still be present
        self.assertEqual(next_page_data["total_count"], 50)
        self.assertEqual(next_page_data["total_pages"], 3)

    def test_pagination_works_end_to_end(self):
        """Test that pagination works correctly in an end-to-end scenario.

        This simulates the actual flow where map_records_response is called first,
        then get_next_page_data_from_response is called on the same response.
        """
        response_data = {
            "entities": [
                {"tag": "entity-1", "name": "Entity 1"},
            ],
            "page": 0,
            "totalPages": 5,
            "total": 100,
        }

        response = MagicMock()
        response.content = b"..."
        response.json.return_value = response_data

        query = MagicMock()
        query.model_class = CortexEntity
        query.conditions = []

        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        # First call map_records_response (this is what happens in ApiBackend.records())
        records = backend.map_records_response(response.json(), query)

        # Then call get_next_page_data_from_response (this is called after map_records_response)
        next_page_data = backend.get_next_page_data_from_response(query, response)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["tag"], "entity-1")

        # Verify pagination still works after map_records_response was called
        self.assertEqual(next_page_data["page"], 1, "Next page should be 1 but pagination data was lost")
        self.assertEqual(next_page_data["total_count"], 100)
        self.assertEqual(next_page_data["total_pages"], 5)

    def test_pagination_with_multiple_pages_iteration(self):
        """Test that pagination works correctly when iterating through multiple pages.

        This simulates the scenario where we fetch page 0, then page 1, then page 2.
        """
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        # Page 0 (first page)
        page0_data = {
            "entities": [{"tag": "entity-1", "name": "Entity 1"}],
            "page": 0,
            "totalPages": 3,
            "total": 3,
        }
        response0 = MagicMock()
        response0.content = b"..."
        response0.json.return_value = page0_data

        query = MagicMock()
        query.model_class = CortexEntity
        query.conditions = []

        records0 = backend.map_records_response(response0.json(), query)
        next_page0 = backend.get_next_page_data_from_response(query, response0)

        self.assertEqual(len(records0), 1)
        self.assertEqual(records0[0]["tag"], "entity-1")
        self.assertEqual(next_page0["page"], 1)

        # Page 1 (middle page)
        page1_data = {
            "entities": [{"tag": "entity-2", "name": "Entity 2"}],
            "page": 1,
            "totalPages": 3,
            "total": 3,
        }
        response1 = MagicMock()
        response1.content = b"..."
        response1.json.return_value = page1_data

        records1 = backend.map_records_response(response1.json(), query)
        next_page1 = backend.get_next_page_data_from_response(query, response1)

        self.assertEqual(len(records1), 1)
        self.assertEqual(records1[0]["tag"], "entity-2")
        self.assertEqual(next_page1["page"], 2)

        # Page 2 (last page)
        page2_data = {
            "entities": [{"tag": "entity-3", "name": "Entity 3"}],
            "page": 2,
            "totalPages": 3,
            "total": 3,
        }
        response2 = MagicMock()
        response2.content = b"..."
        response2.json.return_value = page2_data

        records2 = backend.map_records_response(response2.json(), query)
        next_page2 = backend.get_next_page_data_from_response(query, response2)

        self.assertEqual(len(records2), 1)
        self.assertEqual(records2[0]["tag"], "entity-3")
        # No next page on last page (page 2 is last when totalPages=3)
        self.assertNotIn("page", next_page2)

    def test_pagination_with_empty_response(self):
        """Test pagination handling when response has no entities."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        response_data = {
            "entities": [],
            "page": 0,
            "totalPages": 0,
            "total": 0,
        }
        response = MagicMock()
        response.content = b"..."
        response.json.return_value = response_data

        query = MagicMock()
        query.model_class = CortexEntity
        query.conditions = []

        records = backend.map_records_response(response.json(), query)
        next_page = backend.get_next_page_data_from_response(query, response)

        self.assertEqual(len(records), 0)
        self.assertNotIn("page", next_page)
        self.assertEqual(next_page["total_count"], 0)
        self.assertEqual(next_page["total_pages"], 0)

    def test_pagination_with_single_page(self):
        """Test pagination when there's only one page of results.

        With 0-indexed pages: page=0, totalPages=1 means only page 0 exists.
        """
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        response_data = {
            "entities": [
                {"tag": "entity-1", "name": "Entity 1"},
                {"tag": "entity-2", "name": "Entity 2"},
            ],
            "page": 0,
            "totalPages": 1,
            "total": 2,
        }
        response = MagicMock()
        response.content = b"..."
        response.json.return_value = response_data

        query = MagicMock()
        query.model_class = CortexEntity
        query.conditions = []

        records = backend.map_records_response(response.json(), query)
        next_page = backend.get_next_page_data_from_response(query, response)

        self.assertEqual(len(records), 2)
        # No next page when page=0 and totalPages=1
        self.assertNotIn("page", next_page)
        self.assertEqual(next_page["total_count"], 2)
        self.assertEqual(next_page["total_pages"], 1)

    def test_pagination_with_empty_content(self):
        """Test pagination handling when response has empty content."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        response = MagicMock()
        response.content = b""

        query = MagicMock()

        next_page = backend.get_next_page_data_from_response(query, response)

        self.assertEqual(next_page, {})

    def test_pagination_with_missing_page_field(self):
        """Test pagination handling when page field is missing from response."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        response = MagicMock()
        response.content = b"..."
        response.json.return_value = {
            "entities": [],
            "totalPages": 3,
            "total": 50,
        }

        query = MagicMock()

        next_page = backend.get_next_page_data_from_response(query, response)

        # No next page should be returned when page field is missing
        self.assertNotIn("page", next_page)
        self.assertEqual(next_page["total_count"], 50)
        self.assertEqual(next_page["total_pages"], 3)

    def test_pagination_with_missing_total_pages_field(self):
        """Test pagination handling when totalPages field is missing from response."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        response = MagicMock()
        response.content = b"..."
        response.json.return_value = {
            "entities": [],
            "page": 0,
            "total": 50,
        }

        query = MagicMock()

        next_page = backend.get_next_page_data_from_response(query, response)

        # No next page should be returned when totalPages field is missing
        self.assertNotIn("page", next_page)
        self.assertEqual(next_page["total_count"], 50)

    def test_pagination_boundary_page_1_of_2(self):
        """Test pagination boundary: page 1 of 2 (last page)."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        response = MagicMock()
        response.content = b"..."
        response.json.return_value = {
            "entities": [],
            "page": 1,
            "totalPages": 2,
            "total": 20,
        }

        query = MagicMock()

        next_page = backend.get_next_page_data_from_response(query, response)

        # page=1, totalPages=2: 1+1 < 2 is False, so no next page
        self.assertNotIn("page", next_page)

    def test_pagination_boundary_page_0_of_2(self):
        """Test pagination boundary: page 0 of 2 (first page, has next)."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        response = MagicMock()
        response.content = b"..."
        response.json.return_value = {
            "entities": [],
            "page": 0,
            "totalPages": 2,
            "total": 20,
        }

        query = MagicMock()

        next_page = backend.get_next_page_data_from_response(query, response)

        # page=0, totalPages=2: 0+1 < 2 is True, so next page is 1
        self.assertEqual(next_page["page"], 1)

    def test_pagination_with_large_page_numbers(self):
        """Test pagination with large page numbers."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        response = MagicMock()
        response.content = b"..."
        response.json.return_value = {
            "entities": [],
            "page": 99,
            "totalPages": 100,
            "total": 10000,
        }

        query = MagicMock()

        next_page = backend.get_next_page_data_from_response(query, response)

        # page=99, totalPages=100: 99+1 < 100 is False, so no next page
        self.assertNotIn("page", next_page)
        self.assertEqual(next_page["total_count"], 10000)
        self.assertEqual(next_page["total_pages"], 100)

    def test_pagination_middle_of_large_result_set(self):
        """Test pagination in the middle of a large result set."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        response = MagicMock()
        response.content = b"..."
        response.json.return_value = {
            "entities": [],
            "page": 50,
            "totalPages": 100,
            "total": 10000,
        }

        query = MagicMock()

        next_page = backend.get_next_page_data_from_response(query, response)

        # page=50, totalPages=100: 50+1 < 100 is True, so next page is 51
        self.assertEqual(next_page["page"], 51)
        self.assertEqual(next_page["total_count"], 10000)
        self.assertEqual(next_page["total_pages"], 100)


class TestCortexBackendResponseMapping(unittest.TestCase):
    def test_map_records_response_with_different_entity_keys(self):
        """Test that map_records_response works with different entity key names.

        Cortex API returns different key names for different endpoints:
        - "entities" for catalog
        - "teams" for teams
        - "scorecards" for scorecards
        """
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        query = MagicMock()
        query.model_class = CortexEntity
        query.conditions = []

        # Test with "entities" key
        entities_response = {
            "entities": [{"tag": "entity-1", "name": "Entity 1"}],
            "page": 0,
            "totalPages": 1,
            "total": 1,
        }
        records = backend.map_records_response(entities_response, query)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["tag"], "entity-1")

        # Test with "teams" key
        teams_response = {
            "teams": [{"tag": "team-1", "name": "Team 1"}],
            "page": 0,
            "totalPages": 1,
            "total": 1,
        }
        records = backend.map_records_response(teams_response, query)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["tag"], "team-1")

        # Test with "scorecards" key
        scorecards_response = {
            "scorecards": [{"tag": "scorecard-1", "name": "Scorecard 1"}],
            "page": 0,
            "totalPages": 1,
            "total": 1,
        }
        records = backend.map_records_response(scorecards_response, query)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["tag"], "scorecard-1")

    def test_map_records_response_preserves_all_fields(self):
        """Test that map_records_response preserves all entity fields."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        query = MagicMock()
        query.model_class = CortexEntity
        query.conditions = []

        response_data = {
            "entities": [
                {
                    "tag": "my-service",
                    "name": "My Service",
                    "description": "A test service",
                    "type": "service",
                    "groups": ["team:platform", "env:production"],
                    "owners": {"teams": ["platform-team"]},
                    "metadata": {"custom_field": "value"},
                }
            ],
            "page": 0,
            "totalPages": 1,
            "total": 1,
        }

        records = backend.map_records_response(response_data, query)

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["tag"], "my-service")
        self.assertEqual(record["name"], "My Service")
        self.assertEqual(record["description"], "A test service")
        self.assertEqual(record["type"], "service")
        self.assertEqual(record["groups"], ["team:platform", "env:production"])
        self.assertEqual(record["owners"], {"teams": ["platform-team"]})
        self.assertEqual(record["metadata"], {"custom_field": "value"})

    def test_map_records_response_with_list_response(self):
        """Test map_records_response when response is a list (no wrapper)."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        query = MagicMock()
        query.model_class = CortexEntity
        query.conditions = []

        response_data = [
            {"tag": "entity-1", "name": "Entity 1"},
            {"tag": "entity-2", "name": "Entity 2"},
        ]

        records = backend.map_records_response(response_data, query)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["tag"], "entity-1")
        self.assertEqual(records[1]["tag"], "entity-2")

    def test_map_records_response_with_empty_dict(self):
        """Test map_records_response with empty dictionary raises ValueError.

        The parent ApiBackend raises an error when it can't find records in the response.
        """
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        query = MagicMock()
        query.model_class = CortexEntity
        query.conditions = []

        response_data = {}

        with self.assertRaises(ValueError):
            backend.map_records_response(response_data, query)

    def test_map_records_response_with_only_pagination_fields(self):
        """Test map_records_response when response only has pagination fields.

        When only pagination fields are present, the parent ApiBackend treats
        the response as a single record (since it's a dict with no list values).
        """
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        query = MagicMock()
        query.model_class = CortexEntity
        query.conditions = []

        response_data = {
            "page": 0,
            "totalPages": 0,
            "total": 0,
        }

        records = backend.map_records_response(response_data, query)

        # Parent ApiBackend treats this as a single record since it's a dict
        # with fields that could map to model columns
        self.assertEqual(len(records), 1)

    def test_map_records_response_with_non_list_value(self):
        """Test map_records_response when the first non-pagination value is not a list.

        The parent ApiBackend treats the dict as a single record when it contains
        fields that could map to model columns.
        """
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        query = MagicMock()
        query.model_class = CortexEntity
        query.conditions = []

        response_data = {
            "status": "ok",
            "page": 0,
            "totalPages": 1,
            "total": 0,
        }

        records = backend.map_records_response(response_data, query)

        # Parent ApiBackend treats this as a single record
        self.assertEqual(len(records), 1)


class TestCortexBackendExtractCount(unittest.TestCase):
    def test_extract_count_from_response_body(self):
        """Test that extract_count_from_response correctly extracts counts from response body."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        response_data = {
            "entities": [],
            "page": 0,
            "totalPages": 10,
            "total": 250,
        }

        total_count, total_pages = backend.extract_count_from_response(None, response_data)

        self.assertEqual(total_count, 250)
        self.assertEqual(total_pages, 10)

    def test_extract_count_from_response_with_missing_fields(self):
        """Test extract_count_from_response when some fields are missing."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        # Missing totalPages
        response_data = {
            "entities": [],
            "total": 100,
        }
        total_count, total_pages = backend.extract_count_from_response(None, response_data)
        self.assertEqual(total_count, 100)
        self.assertIsNone(total_pages)

        # Missing total
        response_data = {
            "entities": [],
            "totalPages": 5,
        }
        total_count, total_pages = backend.extract_count_from_response(None, response_data)
        self.assertIsNone(total_count)
        self.assertEqual(total_pages, 5)

        # Missing both
        response_data = {"entities": []}
        total_count, total_pages = backend.extract_count_from_response(None, response_data)
        self.assertIsNone(total_count)
        self.assertIsNone(total_pages)

    def test_extract_count_from_non_dict_response(self):
        """Test extract_count_from_response with non-dict response."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        # List response
        total_count, total_pages = backend.extract_count_from_response(None, [])
        self.assertIsNone(total_count)
        self.assertIsNone(total_pages)

        # None response
        total_count, total_pages = backend.extract_count_from_response(None, None)
        self.assertIsNone(total_count)
        self.assertIsNone(total_pages)

        # String response
        total_count, total_pages = backend.extract_count_from_response(None, "not a dict")
        self.assertIsNone(total_count)
        self.assertIsNone(total_pages)

    def test_extract_count_ignores_headers(self):
        """Test that extract_count_from_response ignores headers parameter."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        response_data = {
            "entities": [],
            "total": 100,
            "totalPages": 5,
        }

        # Headers should be ignored, only response_data is used
        total_count, total_pages = backend.extract_count_from_response(
            {"X-Total-Count": "999", "X-Total-Pages": "99"}, response_data
        )

        self.assertEqual(total_count, 100)
        self.assertEqual(total_pages, 5)


class TestCortexBackendConfiguration(unittest.TestCase):
    """Tests for CortexBackend configuration options."""

    def test_default_configuration(self):
        """Test default configuration values."""
        backend = CortexBackend()
        backend.finalize_and_validate_configuration()

        self.assertEqual(backend.base_url, "https://api.getcortexapp.com/api/v1/")
        self.assertEqual(backend.api_casing, "camelCase")
        self.assertEqual(backend.pagination_parameter_name, "page")
        self.assertEqual(backend.limit_parameter_name, "pageSize")
        self.assertFalse(backend.can_count)

    def test_custom_base_url(self):
        """Test custom base URL configuration."""
        backend = CortexBackend(base_url="https://custom.cortex.io/api/v2/")
        backend.finalize_and_validate_configuration()

        self.assertEqual(backend.base_url, "https://custom.cortex.io/api/v2/")

    def test_custom_pagination_parameter_name(self):
        """Test custom pagination parameter name."""
        backend = CortexBackend(pagination_parameter_name="pageNumber")
        backend.finalize_and_validate_configuration()

        self.assertEqual(backend.pagination_parameter_name, "pageNumber")

        # Verify it's used in get_next_page_data_from_response
        response = MagicMock()
        response.content = b"..."
        response.json.return_value = {
            "entities": [],
            "page": 0,
            "totalPages": 3,
            "total": 50,
        }

        query = MagicMock()
        next_page = backend.get_next_page_data_from_response(query, response)

        self.assertEqual(next_page["pageNumber"], 1)
        self.assertNotIn("page", next_page)

    def test_custom_limit_parameter_name(self):
        """Test custom limit parameter name."""
        backend = CortexBackend(limit_parameter_name="limit")
        backend.finalize_and_validate_configuration()

        self.assertEqual(backend.limit_parameter_name, "limit")


class TestCortexBackendIntegration(unittest.TestCase):
    def test_full_pagination_flow_with_clearskies_context(self):
        """Test pagination through a full clearskies context.

        This test simulates how pagination would work when using the CortexBackend
        through clearskies endpoints.
        """
        # Create mock responses for 3 pages (0-indexed)
        page_responses = [
            {
                "entities": [{"tag": f"entity-{i}", "name": f"Entity {i}"} for i in range(1, 4)],
                "page": 0,
                "totalPages": 3,
                "total": 9,
            },
            {
                "entities": [{"tag": f"entity-{i}", "name": f"Entity {i}"} for i in range(4, 7)],
                "page": 1,
                "totalPages": 3,
                "total": 9,
            },
            {
                "entities": [{"tag": f"entity-{i}", "name": f"Entity {i}"} for i in range(7, 10)],
                "page": 2,
                "totalPages": 3,
                "total": 9,
            },
        ]

        current_page = [0]  # Use list to allow mutation in closure

        def mock_request(*args, **kwargs):
            response = MagicMock()
            response.ok = True
            response.content = b"..."
            response.json.return_value = page_responses[current_page[0]]
            current_page[0] = min(current_page[0] + 1, 2)  # Advance page, max at 2
            return response

        requests = MagicMock()
        requests.request = MagicMock(side_effect=mock_request)

        class DummyCortexAuth:
            def __call__(self, r):
                return r

            def clear_credential_cache(self):
                pass

        def fetch_entities(cortex_entities: CortexEntity):
            # Fetch first page - use iteration instead of list() to avoid count()
            entities = []
            for entity in cortex_entities.limit(3):
                entities.append(entity.tag)
                if len(entities) >= 3:
                    break
            return {"entities": entities}

        status_code, response, _ = clearskies.contexts.Context(
            clearskies.endpoints.Callable(fetch_entities),
            classes=[CortexEntity],
            bindings={"requests": requests, "cortex_auth": DummyCortexAuth()},
        )()

        self.assertEqual(status_code, 200)
        # Should have fetched entities from first page
        self.assertEqual(len(response["data"]["entities"]), 3)
        self.assertEqual(response["data"]["entities"], ["entity-1", "entity-2", "entity-3"])


if __name__ == "__main__":
    unittest.main()
