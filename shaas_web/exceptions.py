from fastapi import HTTPException


class BaseAPIError(HTTPException):
    detail = "Unknown error"
    status_code = 500

    def __init__(self):
        pass


class ForbiddenError(BaseAPIError):
    detail = "Permission denied"
    status_code = 403


class AlreadyRunningError(BaseAPIError):
    detail = "Already running"
    status_code = 409


class NotFoundError(BaseAPIError):
    detail = "Entity not found"
    status_code = 404
