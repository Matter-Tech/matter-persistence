from matter_exceptions import DetailedException


class DatabaseError(DetailedException):
    TOPIC = "Database Error"


class DatabaseIntegrityError(DetailedException):
    TOPIC = "Database Integrity Error"


class DatabaseNoEngineSetError(DetailedException):
    TOPIC = "Database No Engine Set Error"


class DatabaseRecordNotFoundError(DetailedException):
    TOPIC = "Database Record Not Found Error"


class DatabaseInvalidSortFieldError(DetailedException):
    TOPIC = "Database Invalid Sort Field Error"
