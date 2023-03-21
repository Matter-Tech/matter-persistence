from matter_persistence.exceptions import MatterPersistenceError


class InvalidProjectConfigurationError(MatterPersistenceError):
    pass


class NotSubclassDatabaseBaseModelError(MatterPersistenceError):
    pass
