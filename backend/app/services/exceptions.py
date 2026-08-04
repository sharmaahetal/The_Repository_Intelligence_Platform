"""Service layer custom business exceptions for Repository Intelligence Platform."""


class ServiceException(Exception):
    """Base exception for all service layer business rule failures."""


class RepositoryAlreadyExistsError(ServiceException):
    """Raised when attempting to create a repository that already exists by full_name or github_id."""


class RepositoryNotFoundError(ServiceException):
    """Raised when a requested repository entity cannot be found."""


class SnapshotNotFoundError(ServiceException):
    """Raised when a requested repository snapshot entity cannot be found."""


class DuplicateSnapshotError(ServiceException):
    """Raised when attempting to record a duplicate snapshot at the same timestamp."""


class PredictionNotFoundError(ServiceException):
    """Raised when a requested prediction entity cannot be found."""


class ModelNotFoundError(ServiceException):
    """Raised when a requested trained model version entity cannot be found."""


# Convenient Aliases
RepositoryAlreadyExists = RepositoryAlreadyExistsError
RepositoryNotFound = RepositoryNotFoundError
SnapshotNotFound = SnapshotNotFoundError
PredictionNotFound = PredictionNotFoundError
ModelNotFound = ModelNotFoundError

__all__ = [
    "ServiceException",
    "RepositoryAlreadyExistsError",
    "RepositoryNotFoundError",
    "SnapshotNotFoundError",
    "DuplicateSnapshotError",
    "PredictionNotFoundError",
    "ModelNotFoundError",
    "RepositoryAlreadyExists",
    "RepositoryNotFound",
    "SnapshotNotFound",
    "PredictionNotFound",
    "ModelNotFound",
]
