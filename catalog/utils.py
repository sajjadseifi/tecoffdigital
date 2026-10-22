import base64
import uuid
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from catalog.validate import validate_reserved_slug
from django.core.validators import validate_unicode_slug
from dashboard.constants import get_template_by_key
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.urls import reverse
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import datetime

def process_base64_image(base64_string, prefix="image"):
    """
    دریافت رشته Base64 و تبدیل آن به ContentFile جنگو.
    در صورت نامعتبر بودن یا خالی بودن، None برمی‌گرداند.
    """
    if not base64_string or ';base64,' not in base64_string:
        return None
        
    try:
        format_str, img_str = base64_string.split(';base64,') 
        ext = format_str.split('/')[-1]
        file_name = f"{prefix}_{uuid.uuid4().hex[:8]}.{ext}"
        
        return ContentFile(base64.b64decode(img_str), name=file_name)
    except Exception as e:
        raise ValueError(f"خطا در پردازش تصویر: {str(e)}")


def generate_unique_slug(instance, field_name="title", slug_field="slug", queryset=None):
    base_slug = slugify(getattr(instance, field_name), allow_unicode=True)
    slug = base_slug
    model = instance.__class__
    num = 1

    if queryset is None:
        queryset = model.objects.all()

    while queryset.filter(**{slug_field: slug}).exclude(id=instance.id).exists():
        slug = f"{base_slug}-{num}"
        num += 1

    return slug

