class AppError(Exception):
    pass


class AuthError(AppError):
    pass


class NotFoundError(AppError):
    pass
