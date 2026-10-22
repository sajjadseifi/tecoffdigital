import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TQRCode(models.Model):
    """
    مدل اصلی کیوآرکد (موتور ترنسفر TQRS)
    شامل تنظیمات پیشرفته ظاهری و فنی
    """
    ERROR_CORRECTION_CHOICES = [
        ('L', 'Low (7%)'),
        ('M', 'Medium (15%)'),
        ('Q', 'Quartile (25%)'),
        ('H', 'High (30%) - مناسب برای لوگو دار'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qrcodes')
    
    # اطلاعات پایه
    title = models.CharField(max_length=255, verbose_name="عنوان")
    target_url = models.URLField(max_length=1000, verbose_name="لینک یا دیتای مقصد")
    short_code = models.CharField(max_length=20, unique=True, db_index=True, verbose_name="کد کوتاه مسیردهی")
    
    # تنظیمات پیشرفته طراحی (Design)
    template_id = models.CharField(max_length=50, default='default', verbose_name="قالب انتخاب شده")
    color_dark = models.CharField(max_length=7, default='#e6481b', verbose_name="رنگ اصلی")
    color_light = models.CharField(max_length=7, default='#fef2f2', verbose_name="رنگ پس‌زمینه")
    logo = models.ImageField(upload_to='qrs/logos/', null=True, blank=True, verbose_name="لوگو وسط QR")
    error_correction = models.CharField(max_length=1, choices=ERROR_CORRECTION_CHOICES, default='H', verbose_name="ضریب تصحیح خطا")
    
    # وضعیت
    is_active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.short_code})"

    class Meta:
        verbose_name = "TQR Code"
        verbose_name_plural = "TQR Codes"


class TQRAnalysitic(models.Model):
    """
    مدل آنالیز و سیستم هوشمند تشخیص خطا (Event-Based)
    """
    EVENT_TYPES = [
        ('scan_success', 'اسکن موفق'),
        ('scan_failed', 'خطا در اسکن/تخریب فیزیکی'),
        ('link_broken', 'لینک شکسته (404/500)'),
        ('timeout', 'تایم‌اوت در لود مقصد'),
    ]

    qr_code = models.OneToOneField(TQRCode, on_delete=models.CASCADE, related_name='analytics')
    
    # آمارهای کلی
    total_scans = models.PositiveIntegerField(default=0, verbose_name="کل اسکن‌ها")
    unique_visitors = models.PositiveIntegerField(default=0, verbose_name="بازدیدکنندگان یکتا")
    
    # سیستم تشخیص سلامت (Health Check)
    is_damaged = models.BooleanField(default=False, verbose_name="احتمال تخریب فیزیکی QR")
    target_status_code = models.IntegerField(null=True, blank=True, verbose_name="آخرین وضعیت HTTP مقصد")
    is_link_broken = models.BooleanField(default=False, verbose_name="آیا لینک خراب است؟")
    
    # محاسبه ضریب خطا
    # فرمول ریاضی: Error Rate = (Failed Events / Total Events) * 100
    error_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="ضریب خطا (%)")
    
    last_scanned_at = models.DateTimeField(null=True, blank=True, verbose_name="آخرین اسکن")
    last_error_detected_at = models.DateTimeField(null=True, blank=True, verbose_name="آخرین خطای شناسایی شده")

    def __str__(self):
        return f"Analytics for {self.qr_code.title}"

    def calculate_error_rate(self, total_failed, total_events):
        """
        محاسبه ضریب خطا
        $$Error\ Rate = \frac{Failed\ Events}{Total\ Events} \times 100$$
        """
        if total_events > 0:
            self.error_rate = (total_failed / total_events) * 100
            self.save()

    class Meta:
        verbose_name = "TQR Analytic"
        verbose_name_plural = "TQR Analytics"


class TQREventLog(models.Model):
    """
    ثبت لاگ هر رویداد برای ایجاد سیستم Event-Based دقیق
    """
    analytics = models.ForeignKey(TQRAnalysitic, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=TQRAnalysitic.EVENT_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True, verbose_name="جزئیات فنی رویداد")

    class Meta:
        ordering = ['-timestamp']
