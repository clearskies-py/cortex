import unittest
from unittest.mock import MagicMock

import clearskies

from clearskies_cortex.models.cortex_team import CortexTeam


class TestCortexTeamRelationshipBackend(unittest.TestCase):
    def run_team_tree_test(self, archived=False):
        relationships = [
            {"childTeamTag": "Sub 1 of Root 1", "parentTeamTag": "Root 1"},
            {"childTeamTag": "Sub 2 of Root 1", "parentTeamTag": "Root 1"},
            {"childTeamTag": "Sub Sub", "parentTeamTag": "Sub 1 of Root 1"},
            {"childTeamTag": "Sub 1 of Root 2", "parentTeamTag": "Root 2"},
        ]
        teams = [
            {"teamTag": "Root 1", "isArchived": False, "metadata": {"name": "Root 1"}},
            {"teamTag": "Root 2", "isArchived": False, "metadata": {"name": "Root 2"}},
            {"teamTag": "Sub 1 of Root 1", "isArchived": archived, "metadata": {"name": "Sub 1 of Root 1"}},
            {"teamTag": "Sub 2 of Root 1", "isArchived": False, "metadata": {"name": "Sub 2 of Root 1"}},
            {"teamTag": "Sub Sub", "isArchived": False, "metadata": {"name": "Sub Sub"}},
            {"teamTag": "Sub 1 of Root 2", "isArchived": archived, "metadata": {"name": "Sub 1 of Root 2"}},
        ]

        relationships_response = MagicMock()
        relationships_response.json = MagicMock(return_value={"edges": relationships})
        relationships_response.ok = True

        teams_response = MagicMock()
        teams_response.json = MagicMock(return_value={"teams": teams})
        teams_response.ok = True

        def smart_response(*args, **kwargs):
            url = args[1] if len(args) > 1 else ""
            if "relationships" in url:
                return relationships_response
            return teams_response

        requests = MagicMock()
        requests.request = MagicMock(side_effect=smart_response)

        class DummyCortexAuth:
            def __call__(self, r):
                return r

            def clear_credential_cache(self):
                pass

        def fetch_cortex_team(cortex_teams: CortexTeam):
            root_1 = list(cortex_teams.where("team_tag='Root 1'"))[0]
            root_2 = list(cortex_teams.where("team_tag='Root 2'"))[0]
            sub_sub = list(cortex_teams.where("team_tag='Sub Sub'"))[0]
            return {
                "descendants_of_root_1": [t.team_tag for t in root_1.descendants],  # type: ignore[attr-defined]
                "children_of_root_1": [t.team_tag for t in root_1.children],  # type: ignore[attr-defined]
                "descendants_of_root_2": [t.team_tag for t in root_2.descendants],  # type: ignore[attr-defined]
                "ancestors_of_sub_sub": [t.team_tag for t in sub_sub.ancestors],  # type: ignore[attr-defined]
            }

        status_code, response, _ = clearskies.contexts.Context(
            clearskies.endpoints.Callable(fetch_cortex_team),
            classes=[CortexTeam],
            bindings={"requests": requests, "cortex_auth": DummyCortexAuth()},
        )()
        self.assertEqual(status_code, 200)
        self.assertEqual(
            set(response["data"]["descendants_of_root_1"]), {"Sub 1 of Root 1", "Sub 2 of Root 1", "Sub Sub"}
        )
        self.assertEqual(set(response["data"]["children_of_root_1"]), {"Sub 1 of Root 1", "Sub 2 of Root 1"})
        self.assertEqual(response["data"]["descendants_of_root_2"], ["Sub 1 of Root 2"])
        self.assertEqual(set(response["data"]["ancestors_of_sub_sub"]), {"Root 1", "Sub 1 of Root 1"})

    def test_cortex_team_category_tree(self):
        self.run_team_tree_test(archived=False)

    def test_cortex_team_category_tree_with_archived(self):
        self.run_team_tree_test(archived=True)
