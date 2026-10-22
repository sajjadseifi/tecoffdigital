from django import forms
from django.core.validators import validate_unicode_slug
from .entities import Category, Item, Catalog
from presentation.widgets import *
from django.urls import path
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.crypto import get_random_string
from django import forms
from .models import Catalog
import json
from django import forms
from django.utils.crypto import get_random_string
from .models import Catalog, Category

class SetPriceForm(forms.Form):

    price = forms.DecimalField(
        label="قیمت جدید (ریال)",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "w-full rounded-xl border border-surface-200 bg-surface-50 px-4 py-3 focus:ring-1 focus:ring-accent-500 focus:border-accent-500 outline-none",
                "placeholder": "مثلا 120000",
            }
        ),
    )
class SetDiscountForm(forms.Form):

    discount_price = forms.DecimalField(
        label="قیمت تخفیفی (ریال)",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "w-full rounded-xl border border-surface-200 bg-surface-50 px-4 py-3 focus:ring-1 focus:ring-accent-500 focus:border-accent-500 outline-none",
                "placeholder": "مثلا 950000",
            }
        ),
    )


class QuickCatalogAdminForm(TailwindFormMixin, forms.ModelForm):

    class Meta:
        model = Catalog

        fields = [
            'title',
            'business_type',
            'description',

            'theme',

            'logo',
            'cover',

            'headline',
            'subheadline',
            'tagline',

            'is_active',
            'is_verified',
            'is_featured',
            'is_public',

            'phone',
            'address',

            # redirect
            'redirect_url_active',
            'redirect_url',
            'redirect_url_proxy',

            'facilities',
        ]

        widgets = {

            # فایل
            'logo': PersianFileWidget(),
            'cover': PersianFileWidget(),

            # json
            'working_hours': WorkingHoursWidget(),
            'facilities': FacilitiesWidget(),

            # text
            'title': forms.TextInput(attrs={
                'placeholder': 'مثلاً: فروشگاه لوازم خانگی امید'
            }),

            'business_type': forms.TextInput(attrs={
                'placeholder': 'مثلاً: رستوران، فروشگاه اینترنتی و...'
            }),

            'headline': forms.TextInput(attrs={
                'placeholder': 'تیتر اصلی کاتالوگ'
            }),

            'subheadline': forms.TextInput(attrs={
                'placeholder': 'زیرتیتر کاتالوگ'
            }),

            'tagline': forms.TextInput(attrs={
                'placeholder': 'شعار تبلیغاتی کسب‌وکار'
            }),

            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'توضیحات مختصر...'
            }),

            'address': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'آدرس کامل'
            }),

            'phone': forms.TextInput(attrs={
                'dir': 'ltr',
                'class': 'text-left',
                'placeholder': '02112345678'
            }),

            # redirect
            'redirect_url': forms.URLInput(attrs={
                'dir': 'ltr',
                'class': 'text-left',
                'placeholder': 'https://example.com'
            }),
        }

        labels = {

            'title': 'عنوان',
            'business_type': 'نوع کسب‌وکار',
            'description': 'توضیحات کوتاه',

            'logo': 'لوگو',
            'cover': 'تصویر کاور',

            'headline': 'تیتر اصلی',
            'subheadline': 'زیرتیتر',
            'tagline': 'شعار تبلیغاتی',

            'phone': 'تلفن',
            'address': 'آدرس',

            'working_hours': 'ساعات کاری',
            'facilities': 'امکانات',

            'is_active': 'فعال',
            'is_verified': 'تایید شده',
            'is_featured': 'ویژه',
            'is_public': 'عمومی',

            'theme': 'قالب',

            # redirect
            'redirect_url_active': 'فعال بودن ریدایرکت',
            'redirect_url': 'لینک مقصد',
            'redirect_url_proxy': 'نمایش به‌صورت پروکسی',
            'redirect_url_portal': 'نمایش به‌صورت پورتال',
        }

    # ===================================
    # VALIDATION
    # ===================================

    def clean(self):

        cleaned_data = super().clean()

        redirect_url_active = cleaned_data.get(
            'redirect_url_active'
        )

        redirect_url = cleaned_data.get(
            'redirect_url'
        )

        # اگر فعال بود باید لینک داشته باشد
        if redirect_url_active and not redirect_url:

            self.add_error(
                'redirect_url',
                'لینک مقصد الزامی است'
            )

        return cleaned_data

    # ===================================
    # SAVE
    # ===================================

    def save(self, commit=True, user=None):

        instance = super().save(commit=False)

        is_new = instance.pk is None

        # owner
        if is_new:

            if user and not instance.owner_id:
                instance.owner = user

        # defaults
        if is_new:

            if not instance.working_hours:
                instance.working_hours = {
                    "شنبه": ["08:00", "18:00"],
                    "یکشنبه": ["08:00", "18:00"],
                    "دوشنبه": ["08:00", "18:00"],
                    "سه‌شنبه": ["08:00", "18:00"],
                    "چهارشنبه": ["08:00", "18:00"],
                    "پنج‌شنبه": ["08:00", "18:00"],
                    "جمعه": ["09:00", "18:00"]
                }

            if not instance.facilities:
                instance.facilities = {
                    "کاتالوگ رایگان": "ساخت کاتالوگ بدون هزینه",
                    "هوش مصنوعی": "تولید محتوای هوشمند",
                    "قالب متنوع": "قالب‌های واکنش‌گرا",
                }

            if not instance.highlights:
                instance.highlights = [
                    "کیفیت بالا",
                    "پشتیبانی عالی"
                ]

        # logo copy
        if instance.logo:

            if not instance.logo_dark:
                instance.logo_dark = instance.logo

            if not instance.favicon:
                instance.favicon = instance.logo

        if commit:

            instance.save()

            # categories
            if is_new:

                default_categories = [
                    'منو',
                    'محصولات',
                    'فروشگاه',
                    'تخفیف'
                ]

                for index, cat_title in enumerate(default_categories):

                    Category.objects.create(
                        catalog=instance,
                        title=cat_title,
                        order=index
                    )

        return instance

class CatalogSettingForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Catalog
        fields = [
            'title', 'slug', 'business_type', 'description', 'about', 'services',
            'established_year', 'registration_number', 'tax_id',
            'logo', 'cover', 'banner', 'promo_video',
            'phone', 'mobile', 'email', 'website',
            'address', 'location',
            'instagram', 'telegram', 'whatsapp', 'linkedin', 'aparat', 'youtube', 'twitter',
            'working_hours', 'facilities',
            'meta_title', 'meta_description',
            'theme', 'is_active'
        ]
        
        widgets = {
            # ================= ویجت‌های اختصاصی فایل و JSON =================
            'logo': PersianFileWidget(),
            'cover': PersianFileWidget(),
            'banner': PersianFileWidget(),
            'working_hours': WorkingHoursWidget(), 
            'facilities': FacilitiesWidget(),
            'location': LocationWidget(),
            
            # ================= فیلدهای متنی ساده (راست‌چین) =================
            'title': forms.TextInput(attrs={'placeholder': 'مثلاً: فروشگاه لوازم خانگی امید'}),
            'business_type': forms.TextInput(attrs={'placeholder': 'مثلاً: رستوران، فروشگاه اینترنتی و...'}),
            'meta_title': forms.TextInput(attrs={'placeholder': 'عنوان مناسب برای نمایش در گوگل (حدود ۶۰ کاراکتر)'}),
            'theme': forms.Select(), # در صورت نیاز به انتخاب قالب تغییر دهید
            
            # ================= کنترل ارتفاع Textarea ها =================
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'توضیحات مختصری که زیر عنوان نمایش داده می‌شود...'}),
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'استان، شهر، خیابان، پلاک...'}),
            'about': forms.Textarea(attrs={'rows': 5, 'placeholder': 'تاریخچه و توضیحات کامل درباره کسب‌وکار شما...'}),
            'services': forms.Textarea(attrs={'rows': 4, 'placeholder': 'لیست خدمات یا محصولاتی که ارائه می‌دهید...'}),
            'meta_description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'توضیحات مناسب برای جستجوی گوگل (حدود ۱۶۰ کاراکتر)'}),
            
            # ================= فیلدهای انگلیسی و عددی (چپ‌چین و LTR) =================
            'slug': forms.TextInput(attrs={'dir': 'ltr', 'class': 'text-left font-sans', 'placeholder': 'my-business-name'}),
            'phone': forms.TextInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': '02112345678'}),
            'mobile': forms.TextInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': '09123456789'}),
            'email': forms.EmailInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': 'info@yourdomain.com'}),
            'website': forms.URLInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': 'https://www.yourdomain.com'}),
            
            # اطلاعات ثبتی
            'established_year': forms.NumberInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': '1398'}),
            'registration_number': forms.TextInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': '123456'}),
            'tax_id': forms.TextInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': '123456789012'}),
            
            # شبکه‌های اجتماعی
            'instagram': forms.TextInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': 'your_page_id'}),
            'telegram': forms.TextInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': '@your_channel'}),
            'whatsapp': forms.TextInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': '+989123456789'}),
            'linkedin': forms.URLInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': 'https://linkedin.com/in/username'}),
            'aparat': forms.URLInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': 'https://www.aparat.com/username'}),
            'youtube': forms.URLInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': 'https://youtube.com/@username'}),
            'twitter': forms.TextInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': '@username'}),
            'promo_video': forms.URLInput(attrs={'dir': 'ltr', 'class': 'text-left', 'placeholder': 'https://www.aparat.com/v/...'}),
        }
        
        labels = {
            'title': 'عنوان',
            'slug': 'شناسه URL (Slug)',
            'description': 'توضیحات کوتاه',
            'logo': 'لوگو',
            'cover': 'تصویر کاور',
            'phone': 'تلفن ثابت',
            'mobile': 'تلفن همراه',
            'email': 'ایمیل کسب‌وکار',
            'address': 'آدرس دقیق',
            'latitude': 'عرض جغرافیایی (Latitude)',
            'longitude': 'طول جغرافیایی (Longitude)',
            'website': 'وب‌سایت',
            'instagram': 'اینستاگرام',
            'telegram': 'تلگرام',
            'whatsapp': 'واتساپ',
            'linkedin': 'لینکدین',
            'aparat': 'آپارات',
            'youtube': 'یوتیوب',
            'twitter': 'ایکس (توییتر)',
            'business_type': 'نوع کسب‌وکار',
            'working_hours': 'ساعات کاری',
            'facilities': 'امکانات و ویژگی‌ها',
            'established_year': 'سال تاسیس',
            'registration_number': 'شماره ثبت',
            'tax_id': 'شناسه مالیاتی',
            'about': 'درباره کسب‌وکار',
            'services': 'خدمات ارائه شده',
            'banner': 'بنر معرفی',
            'promo_video': 'لینک ویدیو معرفی',
            'meta_title': 'عنوان سئو',
            'meta_description': 'توضیحات سئو',
            'theme': 'قالب نمایش',
            'is_active': 'فعال بودن کاتالوگ',
        }



class CategoryAdminForm(forms.ModelForm):
    slug = forms.SlugField(
        required=False,
        allow_unicode=True,
        validators=[validate_unicode_slug]
    )

    class Meta:
        model = Category
        fields = "__all__"


class ItemAdminForm(forms.ModelForm):
    slug = forms.SlugField(
        required=False,
        allow_unicode=True,
        validators=[validate_unicode_slug]
    )

    class Meta:
        model = Item
        fields = "__all__"
