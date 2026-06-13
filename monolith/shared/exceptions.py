class TennisException(Exception):
    pass


class ValidationError(TennisException):
    pass


class PermissionDeniedError(TennisException):
    pass


class NotFoundError(TennisException):
    pass


class InvalidStateError(TennisException):
    pass


class ScoreConflictError(TennisException):
    pass


class DisputeError(TennisException):
    pass
