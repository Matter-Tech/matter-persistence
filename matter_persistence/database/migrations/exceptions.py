from matter_exceptions import DetailedException


class InvalidProjectConfigurationError(DetailedException):
    pass


class NotSubclassDatabaseBaseModelError(DetailedException):
    pass
