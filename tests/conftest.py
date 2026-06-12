import os

# These run before any `src` import, so module-level Settings() construction succeeds
# without a real .env. Unit tests never open a DB connection (the engine is lazy).
os.environ.setdefault("ENVIRONMENT", "local")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("AUTH_JWT_SECRET", "test-secret-not-for-production-min-32-bytes")
os.environ.setdefault("S3_BUCKET", "test-bucket")
os.environ.setdefault("S3_ACCESS_KEY_ID", "test")
os.environ.setdefault("S3_SECRET_ACCESS_KEY", "test")
