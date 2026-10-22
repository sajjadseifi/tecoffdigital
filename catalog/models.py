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
from catalog.utils import generate_unique_slug, get_template_by_key
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()

class Catalog(models.Model):

    # ==================== ارتباطات پایه ====================
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="catalogs",
        db_index=True,
        verbose_name=_("مالک")
    )

    # ==================== اطلاعات اصلی ====================
    title = models.CharField(max_length=255, verbose_name=_("نام کسب‌وکار"))
    slug = models.SlugField(unique=True,max_length=255,validators=[validate_reserved_slug],db_index=True,verbose_name=_("شناسه یکتا (slug)"))
    
    # ==================== ریدایرکت ====================
    redirect_url = models.URLField(blank=True,null=True,verbose_name=_("لینک مقصد"))
    redirect_url_active = models.BooleanField(default=False,verbose_name=_("فعال بودن ریدایرکت"))
    redirect_url_proxy = models.BooleanField(default=False,verbose_name=_("نمایش با پروکسی"))
    redirect_url_portal = models.BooleanField(default=False,verbose_name=_("نمایش با پورتال"))

    business_type = models.CharField(max_length=100, blank=True, verbose_name=_("نوع کسب‌وکار"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات کوتاه"))
    about = models.TextField(blank=True, verbose_name=_("درباره کسب‌وکار"))
    services = models.TextField(blank=True, verbose_name=_("خدمات/محصولات"))

    # اطلاعات ثبتی
    established_year = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("سال تاسیس"))
    registration_number = models.CharField(max_length=50, blank=True, verbose_name=_("شماره ثبت"))
    tax_id = models.CharField(max_length=50, blank=True, verbose_name=_("شناسه ملی/مالیاتی"))

    # ==================== برندینگ ====================
    logo = models.ImageField(upload_to="catalog/logo/", blank=True, null=True, verbose_name=_("لوگو"))
    logo_dark = models.ImageField(upload_to="catalog/logo/dark/", blank=True, null=True, verbose_name=_("لوگو نسخه تیره"))
    favicon = models.ImageField(upload_to="catalog/favicon/", blank=True, null=True, verbose_name=_("فاوآیکون"))

    primary_color = models.CharField(max_length=7, blank=True, verbose_name=_("رنگ اصلی"))
    secondary_color = models.CharField(max_length=7, blank=True, verbose_name=_("رنگ ثانویه"))

    # ==================== رسانه‌ها ====================
    cover = models.ImageField(upload_to="catalog/cover/", blank=True, null=True, verbose_name=_("تصویر کاور"))
    banner = models.ImageField(upload_to="catalog/banner/", blank=True, null=True, verbose_name=_("بنر معرفی"))
    promo_video = models.URLField(blank=True, verbose_name=_("ویدیو معرفی"))

    # ==================== Hero Section ====================
    headline = models.CharField(max_length=200, blank=True, verbose_name=_("عنوان اصلی"))
    subheadline = models.CharField(max_length=255, blank=True, verbose_name=_("عنوان دوم"))
    tagline = models.CharField(max_length=255, blank=True, verbose_name=_("توضیح کوتاه یک خطی"))

    # ==================== Call To Action ====================
    cta_text = models.CharField(max_length=100, blank=True, verbose_name=_("متن دکمه اصلی"))
    cta_link = models.URLField(blank=True, verbose_name=_("لینک دکمه"))

    # ==================== لینک‌های اپراتیوی ====================
    booking_url = models.URLField(blank=True, verbose_name=_("لینک رزرو"))
    order_url = models.URLField(blank=True, verbose_name=_("لینک سفارش"))
    menu_pdf = models.FileField(upload_to="catalog/menu/", blank=True, verbose_name=_("منو PDF"))

    # ==================== اطلاعات تماس ====================
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("تلفن ثابت"),
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_("شماره تلفن باید بین‌المللی باشد")
            )
        ]
    )
    mobile = models.CharField(max_length=20, blank=True, verbose_name=_("موبایل"))
    email = models.EmailField(blank=True, verbose_name=_("ایمیل"))
    website = models.URLField(blank=True, verbose_name=_("وبسایت"))

    # ==================== آدرس و موقعیت ====================
    address = models.CharField(max_length=500, blank=True, verbose_name=_("آدرس"))
    location = models.JSONField(blank=True, null=True, default=dict, verbose_name=_("موقعیت جغرافیایی"))

    # ==================== شبکه‌های اجتماعی ====================
    instagram = models.CharField(max_length=100, blank=True, verbose_name=_("اینستاگرام"))
    telegram = models.CharField(max_length=100, blank=True, verbose_name=_("تلگرام"))
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name=_("واتساپ"))
    linkedin = models.URLField(blank=True, verbose_name=_("لینکدین"))
    aparat = models.URLField(blank=True, verbose_name=_("آپارات"))
    youtube = models.URLField(blank=True, verbose_name=_("یوتیوب"))
    twitter = models.CharField(max_length=100, blank=True, verbose_name=_("ایکس (توییتر)"))

    # ==================== محتوا و امکانات ====================
    working_hours = models.JSONField(blank=True, default=dict, verbose_name=_("ساعات کاری"))
    facilities = models.JSONField(blank=True, default=dict, verbose_name=_("امکانات"))
    highlights = models.JSONField(blank=True, default=list, verbose_name=_("ویژگی‌های برجسته"))

    # ==================== اعتمادسازی ====================
    clients_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("تعداد مشتریان"))
    years_of_experience = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("سال تجربه"))
    projects_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("تعداد پروژه‌ها"))

    # ==================== سئو ====================
    meta_title = models.CharField(max_length=60, blank=True, verbose_name=_("Meta Title"))
    meta_description = models.CharField(max_length=160, blank=True, verbose_name=_("Meta Description"))
    schema_type = models.CharField(max_length=50, blank=True, default="LocalBusiness", verbose_name=_("Schema.org Type"))

    # ==================== وضعیت و آمار ====================
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    is_verified = models.BooleanField(default=False, verbose_name=_("تیک آبی"))
    is_featured = models.BooleanField(default=False, verbose_name=_("کسب‌وکار ویژه"))
    is_public = models.BooleanField(default=True, verbose_name=_("نمایش عمومی"))

    views = models.PositiveIntegerField(default=0, verbose_name=_("بازدید"))
    theme = models.CharField(max_length=100, blank=True, default='tecof', verbose_name=_("قالب"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("بروزرسانی"))

    # ==================== Meta ====================
    class Meta:
        verbose_name = _("کاتالوگ")
        verbose_name_plural = _("کاتالوگ‌ها")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["owner"]),
            models.Index(fields=["is_active", "is_verified"]),
        ]

    def __str__(self):
        return self.title

    # ==================== Properties ====================
    @property
    def theme_template(self):
        return get_template_by_key(self.theme)

    @property
    def theme_label(self):
        template = self.theme_template
        return template['name'] if template else self.theme

    @property
    def total_qrs(self):
        return self.qrcodes.count()

    @property
    def total_items(self):
        from catalog.models import Item
        return Item.objects.filter(category__catalog=self).count()

    @property
    def total_categories(self):
        return self.categories.count()

    @property
    def categories_first_level(self):
        qs = self.categories.all().prefetch_related('items')
        return qs if qs.exists() else []

    # ==================== URL و لینک‌ها ====================
    def get_absolute_url(self):
        return reverse("app_catalog_q_base", args=[self.slug])

    # ==================== URL و لینک‌ها ====================
    def get_menu_absolute_url(self):
        return reverse("app_catalog_q", args=[self.slug,'menu'])

    @property
    def whatsapp_link(self):
        if not self.whatsapp:
            return None
        num = self.whatsapp.replace("+", "").replace(" ", "")
        return f"https://wa.me/{num}"

    @property
    def phone_link(self):
        return f"tel:{self.phone}" if self.phone else None

    @property
    def email_link(self):
        return f"mailto:{self.email}" if self.email else None

    @property
    def instagram_url(self):
        if not self.instagram:
            return None
        return f"https://instagram.com/{self.instagram.replace('@', '')}"

    @property
    def google_maps_link(self):
        if not self.location:
            return None
        lat = self.location.get("lat")
        lng = self.location.get("lng")
        if lat and lng:
            return f"https://maps.google.com/?q={lat},{lng}"
        return None

    # ==================== لینک‌های شبکه اجتماعی ====================
    @property
    def social_links(self):
        out = []

        if self.instagram:
            out.append({"name": "instagram", "url": self.instagram_url})
        if self.telegram:
            out.append({"name": "telegram", "url": f"https://t.me/{self.telegram}"})
        if self.whatsapp:
            out.append({"name": "whatsapp", "url": self.whatsapp_link})
        if self.linkedin:
            out.append({"name": "linkedin", "url": self.linkedin})
        if self.youtube:
            out.append({"name": "youtube", "url": self.youtube})
        if self.aparat:
            out.append({"name": "aparat", "url": self.aparat})

        return out

    # ==================== Hero & CTA ====================
    @property
    def hero_title(self):
        return self.headline or self.title

    @property
    def short_description(self):
        return self.tagline or self.description

    @property
    def has_cta(self):
        return bool(self.cta_text and self.cta_link)

    # ==================== وضعیت کاری ====================
    @property
    def today_working_hours(self):
        if not self.working_hours:
            return None
        day = datetime.datetime.today().strftime("%A").lower()
        return self.working_hours.get(day)

    @property
    def is_open_now(self):
        return bool(self.today_working_hours)

    # ==================== موارد دیگر ====================
    @property
    def has_social(self):
        return any([
            self.instagram,
            self.telegram,
            self.whatsapp,
            self.linkedin,
            self.youtube,
            self.aparat,
        ])

    @property
    def logo_or_default(self):
        return self.logo.url if self.logo else "/static/img/default-business.png"

    @property
    def full_address(self):
        return self.address or "—"

    # ==================== Save ====================
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self)
        super().save(*args, **kwargs)


class Category(models.Model):

    catalog = models.ForeignKey(Catalog,on_delete=models.CASCADE,related_name="categories",db_index=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, db_index=True, blank=True,allow_unicode=True,validators=[validate_unicode_slug])
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="category/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=True)
    is_important = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    category_link_catalog = models.ForeignKey(
        Catalog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',  # 👈 این باعث می‌شود Catalog هیچ ربطی نداشته باشد
        verbose_name="کاتالوگ مرتبط",
        db_index=True,
    )
    class Meta:
        verbose_name = "دسته بندی ها"
        verbose_name_plural = "دسته بندی ها"

        ordering = ["order", "title"]

        constraints = [
            models.UniqueConstraint(
                fields=["catalog", "slug"],
                name="unique_category_slug_per_catalog"
            )
        ]

        indexes = [
            models.Index(fields=["catalog", "order"]),
        ]

    def __str__(self):
        return f"{self.catalog.title} / {self.title}"

    def total_items(self):
        return self.items.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            qs = Category.objects.filter(catalog=self.catalog)
            self.slug = generate_unique_slug(self, queryset=qs)
        super().save(*args, **kwargs)

class Item(models.Model):
    item_link_catalog = models.ForeignKey(
        Catalog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',  # 👈 این باعث می‌شود Catalog هیچ ربطی نداشته باشد
        verbose_name="کاتالوگ مرتبط",
        db_index=True,
    )
    class PriceType(models.TextChoices):
        NUMBER = "number", "عدد"
        KILOGRAM = "kg", "کیلو"
        GRAM = "g", "گرم"
        LITER = "l", "لیتر"
        METER = "m", "متر"

    class CurrencyType(models.TextChoices):
        RIAL = "rial", "ریال"
        TOMAN = "toman", "تومان"
        USD = "usd", "دلار"
        YEN = "yen", "ین"
        EURO = "eur", "یورو"

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True
    )

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=200,
        db_index=True,
        blank=True,
        allow_unicode=True,
        validators=[validate_unicode_slug]
    )

    description = models.TextField(blank=True)

    image = models.ImageField(upload_to="items/", blank=True, null=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )

    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )

    # نوع قیمت
    price_type = models.CharField(
        max_length=10,
        choices=PriceType.choices,
        default=PriceType.NUMBER
    )

    # واحد پول
    currency = models.CharField(
        max_length=10,
        choices=CurrencyType.choices,
        default=CurrencyType.RIAL
    )

    # نمایش نوع و واحد
    show_price_meta = models.BooleanField(default=True)

    # نمایش یا مخفی کردن قیمت
    show_price = models.BooleanField(default=True)

    sku = models.CharField(max_length=100, blank=True)

    stock = models.PositiveIntegerField(default=0)

    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    views = models.PositiveIntegerField(default=0)

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "آیتم ها"
        verbose_name_plural = "آیتم ها"

        ordering = ["order", "title"]

        constraints = [
            models.UniqueConstraint(
                fields=["category", "slug"],
                name="unique_item_slug_per_category"
            )
        ]

        indexes = [
            models.Index(fields=["category", "order"]),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        if self.price and self.discount_price:
            if self.discount_price > self.price:
                raise ValidationError({
                    "discount_price": "قیمت با تخفیف نمی‌تواند از قیمت اصلی بیشتر باشد."
                })

    @property
    def has_discount(self):
        return (
            self.price is not None and
            self.discount_price is not None and
            self.discount_price > 0
        )

    @property
    def final_price(self):
        if self.has_discount:
            return self.price - self.discount_price
        return self.price

    @property
    def discount_amount(self):
        if not self.has_discount:
            return Decimal("0")
        return self.discount_price

    @property
    def discount_percent(self):
        if not self.has_discount or self.price == 0:
            return 0
        return round((self.discount_price / self.price) * 100)
    def save(self, *args, **kwargs):
        if not self.slug:
            qs = Item.objects.filter(category=self.category)
            self.slug = generate_unique_slug(self, queryset=qs)

        self.clean()

        super().save(*args, **kwargs)

