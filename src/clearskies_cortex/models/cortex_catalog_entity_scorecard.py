from collections import OrderedDict
from typing import Any, Self

from clearskies import Model
from clearskies.columns import Float, Integer, Json, String

from clearskies_cortex.backends import CortexBackend


class CortexCatalogEntityScorecard(Model):
    """
    Model for Cortex entity scorecards.

    This model represents scorecard data associated with a specific catalog entity in Cortex.
    Scorecards track compliance, quality, and other metrics for entities based on defined rules.

    The model connects to the Cortex API endpoint `catalog/:entity_tag/scorecards` to fetch
    scorecard scores and ladder level information for a specific entity.

    ```python
    from clearskies_cortex.models import CortexCatalogEntityScorecard

    # Fetch scorecards for a specific entity
    scorecards = CortexCatalogEntityScorecard()
    entity_scorecards = scorecards.where("entity_tag=my-service")
    for scorecard in entity_scorecards:
        print(f"Scorecard: {scorecard.score_card_name}")
        print(f"Score: {scorecard.score}/{scorecard.total_possible_score}")
        print(f"Percentage: {scorecard.score_percentage}%")
    ```
    """

    id_column_name: str = "scorecard_id"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "catalog/:entity_tag/scorecards"

    """
    The unique identifier for the scorecard.
    """
    scorecard_id = Integer()

    """
    The tag identifier of the entity this scorecard belongs to.
    """
    entity_tag = String()

    """
    JSON object containing ladder level information.

    Ladder levels define maturity stages for the scorecard (e.g., Bronze, Silver, Gold).
    """
    ladder_levels = Json()

    """
    The current score achieved by the entity for this scorecard.
    """
    score = Integer()

    """
    The score as a percentage of the total possible score.
    """
    score_percentage = Float()

    """
    The human-readable name of the scorecard.
    """
    score_card_name = String()

    """
    The maximum possible score for this scorecard.
    """
    total_possible_score = Integer()

    def get_score_card_tag_name(self) -> str:
        """Transform the scorecardName to scorecard tag."""
        name: str = self.score_card_name
        return name
