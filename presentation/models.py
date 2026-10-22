import os
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.files.storage import FileSystemStorage

static_storage = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static'),
    base_url=settings.STATIC_URL
)

class IconLibs(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150)
    category = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    icon_file = models.FileField(
        storage=static_storage,
        upload_to='icons/libs/', 
        validators=[FileExtensionValidator(allowed_extensions=['svg', 'png', 'jpg', 'jpeg', 'webp'])]
    )
    
    class Meta:
        verbose_name = "گالری ایکون"
        verbose_name_plural = "گالری ایکون ها"


    def __str__(self):
        return self.name

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


class DomainMapping(models.Model): # نام مدل را به DomainMapping تغییر دادم برای وضوح

    # مبدا: دامنه یا IP
    source_domain = models.CharField(
        max_length=255,
        verbose_name=_("دامنه مبدا"),
        help_text=_("دامنه کامل (مثلاً: example.com) یا آدرس IP.")
    )

    # مقصد: می‌تواند یک مسیر URL باشد یا به یک کاتالوگ ارجاع دهد
    # انتخاب بین این دو حالت بستگی به نیاز شما دارد:

    # حالت الف: نگاشت مستقیم به مسیر URL
    destination_path = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("مسیر مقصد"),
        help_text=_("مسیر URL مقصد (مثلاً: /products/category-a/). اگر خالی باشد، به صفحه اصلی هدایت می‌شود.")
    )



    is_active = models.BooleanField(
        default=True,
        verbose_name=_("فعال"),
        help_text=_("آیا این نگاشت فعال است؟")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ بروزرسانی"))

    class Meta:
        verbose_name = _("نگاشت مبدا به مقصد")
        verbose_name_plural = _("نگاشت‌های مبدا به مقصد")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["source_domain"]),
            # models.Index(fields=["catalog"]), # اگر از catalog استفاده می‌کنید
            models.Index(fields=["destination_path"]), # اگر از destination_path استفاده می‌کنید
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        # نمایش بسته به اینکه از کدام نوع مقصد استفاده می‌کنید
        if hasattr(self, 'destination_path'): # اگر destination_path وجود دارد
            path_str = self.destination_path if self.destination_path else '/'
            return f"{self.source_domain} -> {path_str}"
        # elif hasattr(self, 'catalog'): # اگر catalog وجود دارد
        #     catalog_slug = self.catalog.slug if self.catalog else 'N/A'
        #     path_str = self.path_in_catalog if self.path_in_catalog else '/'
        #     return f"{self.source_domain} -> {catalog_slug}/{path_str}"
        else:
            return self.source_domain # fallback

    def clean(self):
        """
        اعتبارسنجی‌های اضافی.
        """
        # اعتبارسنجی فرمت دامنه/IP برای مبدا
        domain_ip_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$' # Domain
            r'|' # OR
            r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$' # IPv4
        )
        if not domain_ip_pattern.match(self.source_domain) and self.source_domain not in ['localhost']:
             raise ValidationError(_("فرمت دامنه مبدا نامعتبر است. مثال: example.com یا 192.168.1.1"))

        # اگر فقط از destination_path استفاده می‌کنید:
        if self.destination_path:
            # می‌توانید اعتبارسنجی بیشتری روی مسیر مقصد انجام دهید
            pass

        # اگر از catalog و path_in_catalog استفاده می‌کنید:
        # if self.catalog:
        #     if not self.catalog.is_active:
        #         raise ValidationError(_("کاتالوگ مقصد غیرفعال است."))
        #     if self.path_in_catalog:
        #         # اعتبارسنجی path_in_catalog
        #         pass

        # جلوگیری از تداخل www و non-www (اختیاری)
        if self.source_domain.startswith("www."):
            domain_without_www = self.source_domain[4:]
            try:
                # بررسی کنید آیا نگاشت مشابهی برای دامنه بدون www فعال است
                existing_mapping = DomainMapping.objects.filter(
                    source_domain=domain_without_www,
                    is_active=True,
                    # شرط تطابق مقصد: اگر از catalog استفاده می‌کنید، اینجا هم چک کنید
                    # destination_path=self.destination_path, # اگر فقط مسیر را چک می‌کنید
                    # catalog=self.catalog, # اگر کاتالوگ را چک می‌کنید
                ).exclude(pk=self.pk).exists()

                if existing_mapping:
                    raise ValidationError(
                        _("نگاشت مشابهی برای '%(domain_www)s' و '%(domain_no_www)s' فعال است.") %
                        {'domain_www': self.source_domain, 'domain_no_www': domain_without_www}
                    )
            except DomainMapping.DoesNotExist:
                pass
