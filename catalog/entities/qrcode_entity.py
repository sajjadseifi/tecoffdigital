from django.db import models
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from catalog.validate import validate_reserved_slug
from django.core.validators import validate_unicode_slug
import qrcode
from io import BytesIO
from django.core.files import File

class CatalogQRCode(models.Model):
    catalog = models.ForeignKey('catalog.Catalog', on_delete=models.CASCADE, related_name="qrcodes",db_index=True)
    
    # برای مواقعی که می‌خواهید برای یک کاتالوگ چند QR Code (مثلاً برای میزهای مختلف رستوران) بسازید
    title = models.CharField(
        max_length=255, 
        help_text="عنوان کیوآر کد (مثلاً: میز شماره ۱ یا ورودی اصلی)",
        blank=True
    )
    
    # لینک مقصدی که QR Code به آن اشاره می‌کند (معمولاً لینک کاتالوگ شماست)
    target_url = models.URLField(max_length=500)
    
    # تصویر تولید شده به صورت خودکار در این فیلد ذخیره می‌شود
    qr_image = models.ImageField(upload_to="catalog/qrcodes/", blank=True, null=True)
    
    # برای ردگیری تعداد اسکن‌ها (اختیاری)
    scans_count = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "کد کیو آر"
        verbose_name_plural = "کد های کیو آر"
        ordering = ["-created_at"]

    def __str__(self):
        return f"QR: {self.catalog.title} - {self.title or 'Default'}"

    def generate_qr_code(self):
        """متدی برای تولید تصویر کیوآر کد"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H, # خطایابی بالا برای خوانایی بهتر
            box_size=10,
            border=4,
        )
        qr.add_data(self.target_url)
        qr.make(fit=True)

        # تولید تصویر (می‌توانید رنگ‌ها را شخصی‌سازی کنید)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # ذخیره تصویر در مموری و سپس در فیلد مدل
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        
        # ایجاد یک نام یکتا برای فایل
        file_name = f"qr_{self.catalog.slug}_{self.pk or 'new'}.png"
        
        # ذخیره فایل در فیلد (بدون فراخوانی مجدد save)
        self.qr_image.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        # اگر لینک تغییر کرده بود یا تصویری وجود نداشت، QR Code جدید بساز
        # در اینجا برای سادگی، اگر تصویری نبود آن را می‌سازیم
        if not self.qr_image:
            self.generate_qr_code()
            
        super().save(*args, **kwargs)