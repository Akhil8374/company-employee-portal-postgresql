from django.core.exceptions import ValidationError
import os

def validate_file_size(file):
    max_size_mb = 5
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"File size cannot exceed {max_size_mb} MB.")

def validate_pdf(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError("Only PDF files are allowed.")

def validate_image(file):
    """
    Allow only JPG, JPEG and PNG images.
    """
    ext = os.path.splitext(file.name)[1].lower()

    allowed_extensions = [".jpg", ".jpeg", ".png"]

    if ext not in allowed_extensions:
        raise ValidationError(
            "Only JPG, JPEG and PNG images are allowed."
        )