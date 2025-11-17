from collections import OrderedDict
from typing import Any, Self

from clearskies import Model
from clearskies.columns import Float, Integer, Json, String

from clearskies_cortex.backends import CortexBackend


class CortexCatalogEntityScorecard(Model):
    """Model for teams."""

    id_column_name: str = "scorecard_id"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "catalog/:entity_tag/scorecards"

    scorecard_id = Integer()
    entity_tag = String()
    ladder_levels = Json()
    score = Integer()
    score_percentage = Float()
    score_card_name = String()
    total_possible_score = Integer()

    def get_score_card_tag_name(self) -> str:
        """Transform the scorecardName to scorecard tag."""
        name: str = self.score_card_name
        return name
