from matter_exceptions import DetailedException


class DatabaseNoEngineSetException(DetailedException):
    def __init__(self):
        super().__init__(
            "The DatabaseClient does not have an engine set. " "Have you executed DatabaseClient.start(db_config)?"
        )


class ConnectionInTransactionException(DetailedException):
    pass


class InvalidPoolStateException(DetailedException):
    pass


class InstanceNotFoundError(DetailedException):
    pass


class InvalidActionError(DetailedException):
    pass
