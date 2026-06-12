"""Storage-domain constants: what may be uploaded and how large."""

# Image content types accepted for avatars/profile images, mapped to a file extension.
IMAGE_CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}

ALLOWED_IMAGE_CONTENT_TYPES = frozenset(IMAGE_CONTENT_TYPE_EXTENSIONS)

# Per-file ceiling for image uploads.
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MiB
