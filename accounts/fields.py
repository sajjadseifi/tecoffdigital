import re
from django.core.exceptions import ValidationError
from django.db import models


def normalize_iran_phone(phone: str) -> str:
    phone = re.sub(r"\D", "", phone)

    if phone.startswith("0098"):
        phone = phone[4:]
    elif phone.startswith("098"):
        phone = phone[3:]
    elif phone.startswith("98"):
        phone = phone[2:]
    elif phone.startswith("0"):
        phone = phone[1:]

    if len(phone) != 10 or not phone.startswith("9"):
        raise ValidationError("Invalid Iranian phone number")

    return "+98" + phone


class PhoneField(models.CharField):

    description = "Iranian phone number"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 13
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value is None:
            return value
        return normalize_iran_phone(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return normalize_iran_phone(value)
