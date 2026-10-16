"""InputWeave: opt-in forwarding middleware for selected input libraries."""

__version__ = "0.0.3"

from inputweave.overrides import register_override, unregister_override

__all__ = ["register_override", "unregister_override"]
