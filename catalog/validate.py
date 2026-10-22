from django.core.exceptions import ValidationError
from .reserved import RESERVED_SLUGS

RESERVED_NORMALIZED = {r.lower().strip() for r in RESERVED_SLUGS}

def validate_reserved_slug(value):
    normalized = value.lower().strip()

    if normalized in RESERVED_NORMALIZED:
        raise ValidationError("This name is reserved and cannot be used.")
