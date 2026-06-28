class AppError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"
    message = "Internal server error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)


class UserNotFoundError(AppError):
    status_code = 404
    code = "USER_NOT_FOUND"
    message = "User not found"


class PostNotFoundError(AppError):
    status_code = 404
    code = "POST_NOT_FOUND"
    message = "Post not found"


class DuplicateEmailError(AppError):
    status_code = 409
    code = "DUPLICATE_EMAIL"
    message = "Email already exists"
