class ScrapingStatus:
    status_ok = "ok"
    status_failed = "failed"

    failed_reason_unknown = "failReasonUnknown"

class WorkerExceptions(Exception):
    class ScrapingFailed(Exception):
        pass