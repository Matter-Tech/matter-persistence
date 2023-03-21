from matter_exceptions import DetailedException


class MatterPersistenceError(DetailedException):
    """Base class for Matter Persistence errors."""

    TOPIC = "Matter Persistence Error"
