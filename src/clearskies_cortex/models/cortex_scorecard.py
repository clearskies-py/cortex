from collections import OrderedDict
from typing import Any, Self

from clearskies import Model
from clearskies.columns import Boolean, Json, String

from clearskies_cortex.backends import CortexBackend


class CortexScorecard(Model):
    """Model for scorecards."""

    id_column_name: str = "scorecard_tag"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "scorecards"

    scorecard_tag = String()
    catalog_entity_tag = String()
    is_archived = Boolean()
    links = Json()
    metadata = Json()
    slack_channels = Json()
