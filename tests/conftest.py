import os

# Default environment variables for test executions
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("APP_ENVIRONMENT", "testing")
