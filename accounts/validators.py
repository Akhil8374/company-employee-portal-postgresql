import os
import re
import struct
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


# ─────────────────────────────────────────────────────────────────────────────
# Allowed / Blocked file type configuration
# ─────────────────────────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}

BLOCKED_EXTENSIONS = {
    ".exe", ".zip", ".js", ".bat", ".sh", ".cmd",
    ".msi", ".dll", ".py", ".php", ".ps1", ".vbs",
}

MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB


# ─────────────────────────────────────────────────────────────────────────────
# Magic-bytes MIME detection (no third-party dependency)
# ─────────────────────────────────────────────────────────────────────────────

# Map of file magic bytes → MIME type
_MAGIC_SIGNATURES = [
    (b"\xff\xd8\xff",               "image/jpeg"),  # JPEG
    (b"\x89PNG\r\n\x1a\n",         "image/png"),   # PNG
    (b"GIF87a",                    "image/gif"),
    (b"GIF89a",                    "image/gif"),
    (b"BM",                        "image/bmp"),
    (b"MZ",                        "application/x-msdownload"),  # EXE
    (b"PK\x03\x04",               "application/zip"),             # ZIP
    (b"\x7fELF",                   "application/x-elf"),
    (b"#!",                        "application/x-shellscript"),  # Shell
    (b"<?php",                     "application/x-php"),
]


def _detect_mime_from_bytes(header: bytes) -> str:
    """
    Detects MIME type by inspecting magic bytes at the start of the file.
    Returns the detected MIME type string or 'application/octet-stream'.
    """
    for signature, mime_type in _MAGIC_SIGNATURES:
        if header.startswith(signature):
            return mime_type
    return "application/octet-stream"


# ─────────────────────────────────────────────────────────────────────────────
# Secure Image Validator
# ─────────────────────────────────────────────────────────────────────────────

@deconstructible
class SecureImageValidator:
    """
    Validates employee profile image uploads with multi-layer security checks:

    1. File extension — only .jpg / .jpeg / .png allowed
    2. File size     — maximum 2 MB
    3. MIME type     — verified via magic-byte inspection of file contents

    Explicitly rejects dangerous file types (.exe, .zip, .js, .bat, etc.)
    even if they are renamed with an image extension.

    Usage in a serializer field:
        profile_image = serializers.ImageField(
            validators=[SecureImageValidator()]
        )
    """

    def __call__(self, file):
        self._validate_extension(file)
        self._validate_size(file)
        self._validate_mime_type(file)

    # ── Extension Validation ─────────────────────────────────────────────────

    def _validate_extension(self, file):
        filename = getattr(file, "name", "") or ""
        ext = os.path.splitext(filename)[1].lower()

        if ext in BLOCKED_EXTENSIONS:
            raise ValidationError(
                f"File type '{ext}' is explicitly blocked. "
                "Only JPG and PNG images are accepted."
            )

        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"Unsupported file extension '{ext}'. "
                "Allowed extensions: .jpg, .jpeg, .png"
            )

    # ── Size Validation ──────────────────────────────────────────────────────

    def _validate_size(self, file):
        size = getattr(file, "size", None)
        if size is not None and size > MAX_IMAGE_SIZE_BYTES:
            size_mb = size / (1024 * 1024)
            raise ValidationError(
                f"File size {size_mb:.2f} MB exceeds the 2 MB maximum allowed."
            )

    # ── MIME Type Validation via Magic Bytes ─────────────────────────────────

    def _validate_mime_type(self, file):
        """
        Reads the first 16 bytes to detect the true MIME type.
        Prevents disguised uploads (e.g., malware.exe renamed to photo.jpg).
        """
        try:
            if hasattr(file, "seek"):
                file.seek(0)

            header = file.read(16)

            if hasattr(file, "seek"):
                file.seek(0)

            # Try python-magic first if available
            try:
                import magic as python_magic
                mime_type = python_magic.from_buffer(header, mime=True)
            except ImportError:
                # Fallback: use our own magic-byte detection
                mime_type = _detect_mime_from_bytes(header)

            if mime_type not in ALLOWED_MIME_TYPES:
                raise ValidationError(
                    f"File content appears to be '{mime_type}', which is not allowed. "
                    "Only JPEG and PNG images are accepted."
                )

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                f"File validation failed. Could not verify file type: {str(e)}"
            )

    def __repr__(self):
        return "SecureImageValidator()"


# ─────────────────────────────────────────────────────────────────────────────
# Employee Field Validators (Module 9)
# ─────────────────────────────────────────────────────────────────────────────

def validate_employee_id(value):
    """
    Validates that the employee ID matches the format: EMP followed by 5 digits.
    Examples: EMP00001, EMP12345
    """
    pattern = r"^EMP\d{5}$"
    if not re.match(pattern, value):
        raise ValidationError(
            f"Invalid employee ID '{value}'. "
            "Format must be EMP followed by 5 digits (e.g., EMP00001)."
        )


def validate_phone_number(value):
    """
    Validates that the phone number contains exactly 10 digits.
    Non-digit characters (spaces, dashes) are stripped before counting.
    """
    digits_only = re.sub(r"\D", "", value)
    if len(digits_only) != 10:
        raise ValidationError(
            f"Phone number must contain exactly 10 digits. "
            f"Got {len(digits_only)} digit(s) in '{value}'."
        )


def validate_positive_salary(value):
    """
    Validates that the salary is a positive number greater than zero.
    """
    if value is not None and value <= 0:
        raise ValidationError(
            "Salary must be a positive number greater than zero."
        )


def validate_joining_date_not_future(value):
    """
    Validates that the joining date is not set to a future date.
    """
    from django.utils import timezone
    if value and value > timezone.now().date():
        raise ValidationError(
            "Joining date cannot be set to a future date."
        )
