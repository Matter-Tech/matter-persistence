from matter_persistence.exceptions import MatterPersistenceError


class DatabaseNoEngineSetException(MatterPersistenceError):
    def __init__(self):
        super().__init__(
            "The DatabaseClient does not have an engine set. Have you executed DatabaseClient.start(db_config)?"
        )


class ConnectionInTransactionException(MatterPersistenceError):
    pass


class InvalidPoolStateException(MatterPersistenceError):
    pass


class InstanceNotFoundError(MatterPersistenceError):
    pass


class InvalidActionError(MatterPersistenceError):
    pass


class InvalidDatabaseConfigurationError(MatterPersistenceError):
    pass
