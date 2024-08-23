class VectorDBException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(VectorDBException):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)

class ValidationError(VectorDBException):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)