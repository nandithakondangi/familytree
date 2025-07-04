# familytree/exceptions.py (New File or in a shared module)


class FamilyTreeBaseError(Exception):
    """Base exception for all custom errors in the FamilyTree application."""

    def __init__(
        self, message: str, status_code: int = 500, operation: str | None = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.detail = message  # This will be the primary message for the HTTP response
        self.operation = operation  # Context: what was the app trying to do?


class OperationError(FamilyTreeBaseError):
    """Raised when a specific operation fails for a known reason."""

    def __init__(self, operation: str, reason: str, status_code: int = 500):
        message = f"Operation '{operation}' failed. Reason: {reason}"
        super().__init__(message, status_code=status_code, operation=operation)
        self.reason = reason


class MemberNotFoundError(FamilyTreeBaseError):
    """Raised when a family member cannot be found."""

    def __init__(self, member_id: str, operation: str):
        message = (
            f"Member with ID '{member_id}' not found during operation '{operation}'."
        )
        super().__init__(message, status_code=404, operation=operation)  # 404 Not Found
        self.member_id = member_id


class InvalidInputError(FamilyTreeBaseError):
    """Raised for business logic validation errors beyond simple parsing."""

    def __init__(self, operation: str, field: str | None, description: str):
        message = f"Invalid input for operation '{operation}'. Field: '{field if field else 'N/A'}'. Description: {description}"
        super().__init__(
            message, status_code=400, operation=operation
        )  # 400 Bad Request
        self.field = field
        self.description = description


class UnsupportedOperationError(FamilyTreeBaseError):
    """Raised when an unsupported operation or feature is requested."""

    def __init__(self, operation: str, feature: str, status_code: int = 501):
        message = f"Unsupported operation '{operation}'. Feature '{feature}' is not implemented."
        super().__init__(
            message, status_code=status_code, operation=operation
        )  # 501 Not Implemented
        self.feature = feature
