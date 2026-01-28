from collections import OrderedDict
from typing import Any, Self

from clearskies import Model
from clearskies.columns import Boolean, Json, String

from clearskies_cortex.backends import CortexBackend


class CortexScorecard(Model):
    """
    Model for Cortex scorecards.

    This model represents scorecard definitions in Cortex. Scorecards define rules and
    criteria for measuring entity compliance, quality, and maturity levels.

    The model connects to the Cortex API endpoint `scorecards` to fetch scorecard definitions.

    ```python
    from clearskies_cortex.models import CortexScorecard

    # Fetch all scorecards
    scorecards = CortexScorecard()
    for scorecard in scorecards:
        print(f"Scorecard: {scorecard.scorecard_tag}")
        if not scorecard.is_archived:
            print("  Status: Active")
    ```
    """

    id_column_name: str = "scorecard_tag"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "scorecards"

    """
    The unique tag identifier for the scorecard.
    """
    scorecard_tag = String()

    """
    The tag of the catalog entity associated with this scorecard.
    """
    catalog_entity_tag = String()

    """
    Whether the scorecard is archived.
    """
    is_archived = Boolean()

    """
    JSON object containing external links associated with the scorecard.
    """
    links = Json()

    """
    JSON object containing custom metadata for the scorecard.
    """
    metadata = Json()

    """
    JSON object containing Slack channel configurations for notifications.
    """
    slack_channels = Json()
