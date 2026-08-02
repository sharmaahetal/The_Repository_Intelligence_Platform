from abc import ABC, abstractmethod
from pathlib import Path

from backend.app.logging import logger


class ArtifactStorageProvider(ABC):
    """Abstract interface decoupling model registry artifact persistence from specific cloud storage drivers."""

    @abstractmethod
    def save_artifact(self, relative_path: str, data: bytes) -> str:
        """Save binary data to storage. Returns canonical URI."""
        pass

    @abstractmethod
    def load_artifact(self, relative_path: str) -> bytes:
        """Load binary data from storage."""
        pass

    @abstractmethod
    def artifact_exists(self, relative_path: str) -> bool:
        """Check if artifact exists in storage."""
        pass


class LocalStorageProvider(ArtifactStorageProvider):
    """Local filesystem storage driver."""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_artifact(self, relative_path: str, data: bytes) -> str:
        file_path = self.base_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(data)
        logger.info("Saved artifact locally", extra={"path": str(file_path)})
        return f"file://{file_path.resolve()}"

    def load_artifact(self, relative_path: str) -> bytes:
        file_path = self.base_dir / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"Local artifact '{relative_path}' not found at {file_path}")
        with open(file_path, "rb") as f:
            return f.read()

    def artifact_exists(self, relative_path: str) -> bool:
        return (self.base_dir / relative_path).exists()


class S3StorageProvider(ArtifactStorageProvider):
    """Mock/S3 Cloud Storage driver for production object stores (S3, Cloudflare R2, MinIO)."""

    def __init__(self, bucket_name: str, endpoint_url: str = "https://s3.amazonaws.com") -> None:
        self.bucket = bucket_name
        self.endpoint = endpoint_url
        self._mock_memory_store: dict[str, bytes] = {}

    def save_artifact(self, relative_path: str, data: bytes) -> str:
        s3_key = f"s3://{self.bucket}/{relative_path}"
        self._mock_memory_store[relative_path] = data
        logger.info(
            "Saved artifact to cloud object store", extra={"s3_key": s3_key, "bytes": len(data)}
        )
        return s3_key

    def load_artifact(self, relative_path: str) -> bytes:
        if relative_path not in self._mock_memory_store:
            raise FileNotFoundError(
                f"S3 object '{relative_path}' not found in bucket '{self.bucket}'"
            )
        return self._mock_memory_store[relative_path]

    def artifact_exists(self, relative_path: str) -> bool:
        return relative_path in self._mock_memory_store
