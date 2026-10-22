from django.db import models

class WebsiteSettings(models.Model):
    """
    تنظیمات کلی وب‌سایت و لندینگ پیج کاتالوگ
    """
    # نام اپلیکیشنی که مدل Catalog در آن است را جایگزین 'catalogs.Catalog' کنید
    catalog = models.OneToOneField(
        'catalog.Catalog', 
        on_delete=models.CASCADE,
        related_name='website_settings',
        verbose_name="کاتالوگ"
    )
    
    custom_domain = models.CharField(max_length=255, blank=True, null=True, help_text="مثال: www.mybusiness.com")
    meta_title = models.CharField(max_length=255, blank=True, verbose_name="عنوان سئو")
    meta_description = models.TextField(blank=True, verbose_name="توضیحات سئو")
    favicon = models.ImageField(upload_to="website/favicons/", blank=True, null=True)
    
    primary_color = models.CharField(max_length=7, default="#f97316", help_text="کد رنگ HEX (مثال: #f97316)")
    
    is_published = models.BooleanField(default=True, verbose_name="منتشر شده")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات وب‌سایت"
        verbose_name_plural = "تنظیمات وب‌سایت‌ها"

    def __str__(self):
        return f"وب‌سایت: {self.catalog.title}"


class LandingSection(models.Model):
    """
    بخش‌های مختلف (Section) لندینگ پیج
    """
    SECTION_TYPES = [
        ('HERO', 'بخش هیرو (Hero)'),
        ('ABOUT', 'درباره ما (About)'),
        ('FEATURES', 'ویژگی‌ها (Features)'),
        ('STATS', 'آمار و ارقام (Stats)'),
        ('FAQ', 'سوالات متداول (FAQ)'),
        ('CONTACT', 'تماس با ما (Contact)'),
        ('SOCIAL_PROOF', 'نظرات مشتریان (Social Proof)'),
        ('HTML', 'کد HTML دلخواه (Custom)'),
    ]

    website = models.ForeignKey(
        WebsiteSettings,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name="وب‌سایت"
    )
    
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, verbose_name="نوع بخش")
    title = models.CharField(max_length=255, blank=True, verbose_name="عنوان بخش")
    subtitle = models.TextField(blank=True, verbose_name="زیرنویس / توضیحات")
    
    image = models.ImageField(upload_to="website/sections/", blank=True, null=True, verbose_name="تصویر اصلی")
    
    # فیلد JSON برای تنظیمات بی‌نهایت و منعطف (مثل رنگ بک‌گراند اختصاصی این بخش، چیدمان و ...)
    config = models.JSONField(default=dict, blank=True, verbose_name="تنظیمات پیشرفته (JSON)")
    
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    @property 
    def get_layout_type_display(self):
        for st in self.SECTION_TYPES:
            if st[0] == self.section_type:
                return st[1]
            
        return None
    class Meta:
        verbose_name = "بخش لندینگ"
        verbose_name_plural = "بخش‌های لندینگ"
        ordering = ['order']

    def __str__(self):
        return f"{self.website.catalog.title} - {self.get_section_type_display()}"


class SectionItem(models.Model):
    """
    آیتم‌های زیرمجموعه یک بخش (مثل لیست سوالات FAQ یا کارت‌های ویژگی‌ها)
    """
    section = models.ForeignKey(
        LandingSection,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="بخش مربوطه"
    )
    
    title = models.CharField(max_length=255, verbose_name="عنوان آیتم")
    description = models.TextField(blank=True, verbose_name="توضیحات آیتم")
    icon = models.CharField(max_length=100, blank=True, help_text="کلاس آیکون (مثال: fas fa-star)")
    image = models.ImageField(upload_to="website/items/", blank=True, null=True)
    url = models.URLField(blank=True, verbose_name="لینک (اختیاری)")
    
    value = models.CharField(max_length=50, blank=True, help_text="برای بخش آمار (مثال: +500)")
    
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "آیتم بخش"
        verbose_name_plural = "آیتم‌های بخش"
        ordering = ['order']

    def __str__(self):
        return self.title
