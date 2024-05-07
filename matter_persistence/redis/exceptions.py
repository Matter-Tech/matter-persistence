from matter_exceptions.detailed_exception import DetailedException


class CacheRecordNotFoundError(DetailedException):
    TOPIC = "Cache Record Not Found Error"


class CacheRecordNotSavedError(DetailedException):
    TOPIC = "Cache Record Not Saved Error"


class CacheServerError(DetailedException):
    TOPIC = "Cache Server Error"
