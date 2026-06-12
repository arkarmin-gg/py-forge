from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageConfig(BaseSettings):
    """S3 storage settings. Env vars are prefixed S3_ (e.g. S3_BUCKET).

    ENDPOINT_URL points the client at S3-compatible services (MinIO, Cloudflare R2,
    LocalStack); leave it unset for real AWS S3. PUBLIC_BASE_URL is the origin used to
    turn a stored object key into a public URL (a CDN domain or a public bucket origin).
    When unset, public_url() falls back to a virtual-hosted-style S3/endpoint URL — for
    private buckets, prefer presigned URLs (see storage.service.presigned_url).
    """

    model_config = SettingsConfigDict(env_prefix="S3_", env_file=".env", extra="ignore")

    # Optional so the app boots without S3 configured; storage operations raise
    # StorageNotConfigured if used while unset (see storage.client.get_s3_client).
    BUCKET: str = ""
    ACCESS_KEY_ID: str = ""
    SECRET_ACCESS_KEY: str = ""
    REGION: str = "us-east-1"
    ENDPOINT_URL: str | None = None
    PUBLIC_BASE_URL: str | None = None
    USE_SSL: bool = True
    PRESIGN_EXPIRY_SECONDS: int = 3600

    @property
    def is_configured(self) -> bool:
        return bool(self.BUCKET and self.ACCESS_KEY_ID and self.SECRET_ACCESS_KEY)


storage_settings = StorageConfig()
