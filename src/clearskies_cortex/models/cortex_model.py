from clearskies import Model

from clearskies_cortex.backends import CortexBackend


class CortexModel(Model):
    """Base model for cortex."""

    backend = CortexBackend()
