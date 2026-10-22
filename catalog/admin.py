from django.contrib import admin
from .models import Catalog, Category, Item
from .forms import ItemAdminForm,CategoryAdminForm
from .entities import CatalogQRCode  
from django.db import models
from django.forms import Textarea
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Count
from django.db import models
from django.forms import Textarea
from .models import Catalog, Category, Item
from .forms import ItemAdminForm, CategoryAdminForm
from .entities import CatalogQRCode
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Catalog

class CategoryInline(admin.TabularInline):
    model = Category
    form = CategoryAdminForm
    fk_name = 'catalog' 
    extra = 0

    fields = (
        "order",
        "image",
        "image_preview",
        "title",
        "slug",
        "description",
        "is_active",
        "is_featured",
        "is_important",
    )

    readonly_fields = ("image_preview",)

    prepopulated_fields = {"slug": ("title",)}
    show_change_link = True

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 2, 'cols': 40})
        }
    }

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;object-fit:cover;" />',
                obj.image.url
            )
        return "—"

    image_preview.short_description = "Preview"

class ItemInline(admin.TabularInline):
    model = Item
    form = ItemAdminForm
    extra = 0

    fields = (
        
        "order",
        "image_preview",
        "image",
        "title",
        "slug",
        "description",
        "price",
        "discount_price",
        "stock",
        "is_available",

        
    )

    readonly_fields = ("image_preview",)

    show_change_link = True

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 2, 'cols': 40})
        }
    }

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;object-fit:cover;" />',
                obj.image.url
            )
        return "—"

    image_preview.short_description = "Preview"

from .forms import QuickCatalogAdminForm
from django.template.response import TemplateResponse

@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    # اضافه کردن تمپلیت اختصاصی برای نمایش دکمه در بالای لیست
    change_list_template = "admin/catalog/catalog/change_list_with_quick_create.html"

    # ================= LIST =================

    list_display = (
        "title",
        "logo_thumb",
        "admin_actions",
        "categories_count",
        "items_count",
        "is_active",
        "is_featured",
        "is_public",
        "owner",
        "created_at",
        
    )

    list_per_page = 25
    date_hierarchy = "created_at"

    # ================= FILTER =================

    list_filter = (
        "is_active",
        "is_verified",
        "is_featured",
        "is_public",
        "theme",
        "created_at",
    )

    # ================= SEARCH =================

    search_fields = (
        "title",
        "slug",
        "owner__username",
        "owner__email",
        "phone",
        "mobile",
        "instagram",
    )

    # ================= ORDER =================

    ordering = ("-created_at",)

    # ================= READONLY =================

    readonly_fields = (
        "views",
        "created_at",
        "updated_at",
        "logo_preview",
    )

    # ================= SLUG =================

    prepopulated_fields = {
        "slug": ("title",)
    }
    autocomplete_fields = ("owner",)

    # ================= INLINES =================

    inlines = [
        CategoryInline,
    ]

    # ================= FIELDSETS =================

    fieldsets = (

        ("اطلاعات اصلی", {
            "fields": (
                "owner",
                "title",
                "slug",
                "business_type",
            )
        }),
        ("مسیر کاتالوگ خام", {
            "fields": (
            'redirect_url_active',
            'redirect_url',
            'redirect_url_proxy',
            'redirect_url_portal'
            )
        }),
        ("برندینگ", {
            "fields": (
                "logo",
                "logo_preview",
                "logo_dark",
                "favicon",
                "primary_color",
                "secondary_color",
            )
        }),
        ("اطلاعات ثبتی", {
            "fields": (
                "established_year",
                "registration_number",
                "tax_id",
            )
        }),
        ("توضیحات", {
            "fields": (
                "description",
                "about",
                "services",
            )
        }),

        ("رسانه‌ها", {
            "fields": (
                "cover",
                "banner",
                "promo_video",
            )
        }),

        ("Hero Section", {
            "fields": (
                "headline",
                "subheadline",
                "tagline",
            )
        }),

        ("Call To Action", {
            "fields": (
                "cta_text",
                "cta_link",
                "booking_url",
                "order_url",
                "menu_pdf",
            )
        }),

        ("اطلاعات تماس", {
            "fields": (
                "phone",
                "mobile",
                "email",
                "website",
                "address",
                "location",
            )
        }),

        ("شبکه‌های اجتماعی", {
            "fields": (
                "instagram",
                "telegram",
                "whatsapp",
                "linkedin",
                "youtube",
                "aparat",
                "twitter",
            )
        }),

        ("امکانات و محتوا", {
            "fields": (
                "working_hours",
                "facilities",
                "highlights",
            )
        }),

        ("اعتمادسازی", {
            "fields": (
                "clients_count",
                "years_of_experience",
                "projects_count",
            )
        }),

        ("سئو", {
            "fields": (
                "meta_title",
                "meta_description",
                "schema_type",
            )
        }),

        ("وضعیت", {
            "fields": (
                "theme",
                "is_active",
                "is_verified",
                "is_featured",
                "is_public",
            )
        }),

        ("آمار", {
            "fields": (
                "views",
                "created_at",
                "updated_at",
            )
        }),

    )
    # ================= CUSTOM URLS & VIEWS =================

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('quick-create/', self.admin_site.admin_view(self.quick_create_view), name='catalog_quick_create'),
        ]
        return custom_urls + urls

    def quick_create_view(self, request):
        if request.method == 'POST':
            form = QuickCatalogAdminForm(request.POST, request.FILES)
            if form.is_valid():
                form.save(user=request.user)
                self.message_user(request, "کاتالوگ سریع با موفقیت ساخته شد.")
                return redirect('admin:catalog_catalog_changelist')
        else:
            form = QuickCatalogAdminForm()

        context = dict(
            self.admin_site.each_context(request),
            title="ایجاد کاتالوگ سریع",
            form=form,
        )
        return TemplateResponse(request, "admin/catalog/catalog/quick_create.html", context)
    # ---------- image preview ----------

    # ================= PERFORMANCE =================

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.select_related(
            "owner"
        ).annotate(
            _categories_count=Count("categories"),
            _items_count=Count("categories__items")
        )

    # ================= COLUMNS =================

    def logo_thumb(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="width:26px;height:26px;border-radius:6px;object-fit:cover;" />',
                obj.logo.url
            )
        return "—"

    logo_thumb.short_description = "لوگو"

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height:120px;border-radius:10px"/>',
                obj.logo.url
            )
        return "—"

    logo_preview.short_description = "پیش‌نمایش لوگو"

    def categories_count(self, obj):
        return obj._categories_count

    categories_count.short_description = "دسته‌ها"

    def items_count(self, obj):
        return obj._items_count

    items_count.short_description = "آیتم‌ها"

    # ================= STATUS BADGE =================

    def status_badge(self, obj):

        if obj.is_active:
            color = "#10b981"
            label = "فعال"
        else:
            color = "#ef4444"
            label = "غیرفعال"

        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:6px;font-size:11px">{}</span>',
            color,
            label
        )

    status_badge.short_description = "وضعیت"

    # ================= QUICK ACTIONS =================

    def admin_actions(self, obj):

        dashboard_url = reverse("dashboard")
        preview_url = reverse("preview_template_base", args=[obj.id, obj.theme])
        menu_url = reverse("app_catalog_q_base", args=[obj.slug])

        return format_html(
            """
            <div style="display:flex;gap:6px">

                <a href="{}" style="
                    padding:4px 8px;
                    border-radius:6px;
                    background:#2563eb;
                    color:white;
                    font-size:11px;
                    text-decoration:none;">
                    منو
                </a>

                <a href="{}" style="
                    padding:4px 8px;
                    border-radius:6px;
                    background:#059669;
                    color:white;
                    font-size:11px;
                    text-decoration:none;">
                    داشبورد
                </a>

                <a href="{}" target="_blank" style="
                    padding:4px 8px;
                    border-radius:6px;
                    background:#d97706;
                    color:white;
                    font-size:11px;
                    text-decoration:none;">
                    پیش‌نمایش
                </a>

            </div>
            """,
            menu_url,
            dashboard_url,
            preview_url,
        )


    admin_actions.short_description = "عملیات"

    # ================= BULK ACTIONS =================

    actions = [
        "make_active",
        "make_inactive",
        "mark_featured",
        'mark_un_featured',
        'mark_public',
        'mark_private' 
    ]

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "فعال کردن کاتالوگ‌ها"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "غیرفعال کردن کاتالوگ‌ها"

    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_featured.short_description = "ویژه کردن کاتالوگ‌ها"

    def mark_un_featured(self, request, queryset):
        queryset.update(is_featured=False)
    mark_un_featured.short_description = "لغو کاتالوگ ویژه"

    def mark_public(self, request, queryset):
        queryset.update(is_public=True)

    mark_public.short_description = "نمایش عمومی کاتالوگ"

    def mark_private(self, request, queryset):
        queryset.update(is_public=False)

    mark_private.short_description = "نمایش شخصی کاتالوگ"

from django.urls import path
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    form = CategoryAdminForm

    list_display = (
        "title",
        "image_thumb",
        "catalog",
        "order",
        "total_items",
        "quick_actions",
        "is_active",
        "is_featured",
        "is_important",
    )

    list_filter = ("catalog", "is_active")
    search_fields = ("title", "slug", "catalog__title")
    ordering = ("catalog", "order")


    prepopulated_fields = {"slug": ("title",)}

    inlines = [ItemInline]

    actions = [
        "make_active",
        "make_inactive",
        "reset_order",
        "make_is_featured", 
        "make_un_featured", 
        "make_is_important", 
        "make_un_important",
    ]

    def image_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:34px;height:34px;border-radius:6px;object-fit:cover;" />',
                obj.image.url
            )
        return "—"

    image_thumb.short_description = "تصویر"

    def quick_actions(self, obj):

        menu_url = reverse("app_catalog_q_base", args=[obj.catalog.slug])

        edit_url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.id],
        )

        items_url = reverse(
            f"admin:{obj._meta.app_label}_item_changelist"
        ) + f"?category__id__exact={obj.id}"

        return format_html(
            """
            <div style="display:flex;gap:6px">

                <a href="{}#cat-{}" style="
                    display:flex;
                    align-items:center;
                    gap:5px;
                    padding:4px 8px;
                    border-radius:6px;
                    background:linear-gradient(135deg,#60a5fa,#1e40af);
                    color:white;
                    font-size:11px;
                    text-decoration:none;
                    box-shadow:0 2px 4px rgba(0,0,0,.15);
                ">
                    <svg width="13" viewBox="0 0 32 32">
                        <rect x="4" y="6" width="24" height="4" rx="2" fill="white"/>
                        <rect x="4" y="14" width="24" height="4" rx="2" fill="white"/>
                        <rect x="4" y="22" width="24" height="4" rx="2" fill="white"/>
                    </svg>
                    کاتالوگ
                </a>

                <a href="{}" style="
                    display:flex;
                    align-items:center;
                    gap:5px;
                    padding:4px 8px;
                    border-radius:6px;
                    background:linear-gradient(135deg,#34d399,#065f46);
                    color:white;
                    font-size:11px;
                    text-decoration:none;
                    box-shadow:0 2px 4px rgba(0,0,0,.15);
                ">
                    <svg width="13" viewBox="0 0 32 32">
                        <rect x="6" y="16" width="4" height="10" fill="white"/>
                        <rect x="14" y="10" width="4" height="16" fill="white"/>
                        <rect x="22" y="6" width="4" height="20" fill="white"/>
                    </svg>
                    آیتم‌ها
                </a>

                <a href="{}" style="
                    display:flex;
                    align-items:center;
                    gap:5px;
                    padding:4px 8px;
                    border-radius:6px;
                    background:linear-gradient(135deg,#fbbf24,#92400e);
                    color:white;
                    font-size:11px;
                    text-decoration:none;
                    box-shadow:0 2px 4px rgba(0,0,0,.15);
                ">
                    <svg width="13" viewBox="0 0 32 32">
                        <path d="M6 22l2 4l4-2l12-12l-4-4z" fill="white"/>
                    </svg>
                    ویرایش
                </a>

            </div>
            """,
            menu_url,
            obj.slug,
            items_url,
            edit_url,
        )

    quick_actions.short_description = "عملیات"


    # ---------- actions ----------

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} categories activated.")

    make_active.short_description = "فعال کردن دسته‌های انتخابی"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} categories deactivated.")

    make_inactive.short_description = "غیرفعال کردن دسته‌های انتخابی"

    def reset_order(self, request, queryset):
        for index, category in enumerate(queryset.order_by("catalog"), start=1):
            category.order = index
            category.save()

        self.message_user(request, "Order reset for selected categories.")

    reset_order.short_description = "ریست ترتیب دسته‌ها"

    def make_is_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} categories activated.")

    make_is_featured.short_description = " افزودن ویژه دسته های انتخابی"

    def make_un_featured(self, request, queryset): 
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} categories deactivated.")

    make_un_featured.short_description = "برداشتن ویژگی دسته‌های انتخابی"

    def make_is_important(self, request, queryset):
        updated = queryset.update(is_important=True)
        self.message_user(request, f"{updated} categories activated.")

    make_is_important.short_description = "اهمیت دسته‌های انتخابی"

    def make_un_important(self, request, queryset):
        updated = queryset.update(is_important=False)
        self.message_user(request, f"{updated} categories deactivated.")

    make_un_important.short_description = "عدم اهمیت دسته‌های انتخابی"



    class Media:
        js = ("admin/js/auto_slug.js",)

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SetPriceForm,SetDiscountForm
from .filters import CatalogFilter
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):

    form = ItemAdminForm

    list_display = (
        "title",
        "image_thumb",
        "category_with_image",
        "price",
        "discount_price",
        "stock",
        "is_available",
        "views",
        "quick_actions",
    )

    list_filter = ("is_available", "is_featured", CatalogFilter,"category")

    search_fields = ("title", "slug", "sku")

    ordering = ("category", "order")

    prepopulated_fields = {"slug": ("title",)}

    readonly_fields = ("views", "created_at", "updated_at")

    actions = [
        "make_available",
        "make_unavailable",
        "set_stock_one",
        "set_stock_zero",
        "set_price",
        'set_discount',
    ]
    def image_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:20px;height:20px;border-radius:6px;object-fit:cover;" />',
                obj.image.url
            )
        return "—"

    image_thumb.short_description = "تصویر"
    # ---------- image preview ----------
    def category_with_image(self, obj):
        if obj.category:
            image_html = ""

            if obj.category.image:
                image_html = f'<img src="{obj.category.image.url}" style="width:20px;height:20px;border-radius:6px;object-fit:cover;margin-left:6px;" />'

            return format_html(
                '<div style="display:flex;align-items:center;gap:6px;">{}<span>{}</span></div>',
                mark_safe(image_html),
                obj.category.title
            )

        return "—"

    category_with_image.short_description = "دسته‌بندی"




    def set_price(self, request, queryset):
            
            # برای تست
            print("🔥 ACTION CALLED!")

            if "apply" in request.POST:
                form = SetPriceForm(request.POST)
                if form.is_valid():
                    price = form.cleaned_data['price']

                    updated = queryset.update(price=price)

                    self.message_user(request, f"{updated} آیتم آپدیت شد.")
                    return redirect(request.get_full_path())
            else:
                form = SetPriceForm()

            print(form.errors)
            return render(
                request,
                "admin/set_price.html",
                {"form": form, "items": queryset}
            )

    set_price.short_description = "تنظیم قیمت گروهی"

    def set_discount(self, request, queryset):
        # برای تست
        print("🔥 DISCOUNT ACTION CALLED!")

        if "apply" in request.POST:
            form = SetDiscountForm(request.POST)
            if form.is_valid():
                discount_price = form.cleaned_data['discount_price']

                updated = queryset.update(discount_price=discount_price)

                self.message_user(request, f"{updated} آیتم تخفیف‌دار شد.")
                return redirect(request.get_full_path())
        else:
            form = SetDiscountForm()

        return render(
            request,
            "admin/set_discount.html",
            {"form": form, "items": queryset}
        )

    set_discount.short_description = "تنظیم قیمت تخفیفی گروهی"

    # ---------- action buttons ----------

    def quick_actions(self, obj):

        menu_url = reverse("app_catalog_q_base", args=[obj.category.catalog.slug])

        edit_url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.id],
        )

        category_url = reverse(
            f"admin:{obj._meta.app_label}_category_change",
            args=[obj.category.id],
        )

        return format_html(
            """
            <div style="display:flex;gap:6px">

                <a href="{}#item-{}" style="
                    display:flex;
                    align-items:center;
                    gap:5px;
                    padding:4px 8px;
                    border-radius:6px;
                    background:linear-gradient(135deg,#60a5fa,#1e40af);
                    color:white;
                    font-size:11px;
                    text-decoration:none;
                    box-shadow:0 2px 4px rgba(0,0,0,.15);
                ">
                    <svg width="13" viewBox="0 0 32 32">
                        <path d="M2 16c4-7 24-7 28 0c-4 7-24 7-28 0z" fill="white"/>
                        <circle cx="16" cy="16" r="4" fill="#1e40af"/>
                    </svg>
                    مشاهده
                </a>


                <a href="{}" style="
                    display:flex;
                    align-items:center;
                    gap:5px;
                    padding:4px 8px;
                    border-radius:6px;
                    background:linear-gradient(135deg,#34d399,#065f46);
                    color:white;
                    font-size:11px;
                    text-decoration:none;
                    box-shadow:0 2px 4px rgba(0,0,0,.15);
                ">
                    <svg width="13" viewBox="0 0 32 32">
                        <rect x="4" y="6" width="24" height="4" rx="2" fill="white"/>
                        <rect x="4" y="14" width="24" height="4" rx="2" fill="white"/>
                        <rect x="4" y="22" width="24" height="4" rx="2" fill="white"/>
                    </svg>
                    دسته
                </a>


                <a href="{}" style="
                    display:flex;
                    align-items:center;
                    gap:5px;
                    padding:4px 8px;
                    border-radius:6px;
                    background:linear-gradient(135deg,#fbbf24,#92400e);
                    color:white;
                    font-size:11px;
                    text-decoration:none;
                    box-shadow:0 2px 4px rgba(0,0,0,.15);
                ">
                    <svg width="13" viewBox="0 0 32 32">
                        <path d="M6 22l2 4l4-2l12-12l-4-4z" fill="white"/>
                    </svg>
                    ویرایش
                </a>

            </div>
            """,
            menu_url,
            obj.slug,
            category_url,
            edit_url,
        )

    quick_actions.short_description = "عملیات"

    # ---------- bulk actions ----------

    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f"{updated} items marked as available.")

    make_available.short_description = "فعال کردن آیتم‌ها"

    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f"{updated} items marked as unavailable.")

    make_unavailable.short_description = "غیرفعال کردن آیتم‌ها"

    def set_stock_one(self, request, queryset):
        updated = queryset.update(stock=1)
        self.message_user(request, f"Stock set to 1 for {updated} items.")

    set_stock_one.short_description = "تنظیم موجودی روی 1"

    def set_stock_zero(self, request, queryset):
        updated = queryset.update(stock=0)
        self.message_user(request, f"Stock set to 0 for {updated} items.")

    set_stock_zero.short_description = "اتمام موجودی"

    class Media:
        js = ("admin/js/auto_slug.js",)

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

@admin.register(CatalogQRCode)
class CatalogQRCodeAdmin(admin.ModelAdmin):
    # نمایش تصویر کوچک، عنوان، تعداد اسکن و دکمه‌های عملیات
    list_display = (
        "qr_preview", 
        "title", 
        "catalog", 
        "scans_count_styled", 
        "is_active", 
        "quick_actions"
    )
    
    list_filter = ("is_active", "catalog", "created_at")
    search_fields = ("title", "catalog__title", "target_url")
    readonly_fields = ("qr_image_preview", "scans_count", "created_at")
    
    # مرتب‌سازی فیلدها در صفحه ویرایش
    fields = ("catalog", "title", "target_url", "qr_image_preview", "is_active", "scans_count")

    # ---------- نمایش تصویر QR در لیست ----------
    def qr_preview(self, obj):
        if obj.qr_image:
            return format_html(
                '<img src="{}" style="width:20px; height:20px; border-radius:4px; border:1px solid #ddd;" />',
                obj.qr_image.url
            )
        return "بدون تصویر"
    qr_preview.short_description = "کد QR"

    # ---------- نمایش پیش‌نمایش بزرگ در صفحه ویرایش ----------
    def qr_image_preview(self, obj):
        if obj.qr_image:
            return format_html(
                '<img src="{}" style="width:200px; height:200px; border:2px solid #eee; border-radius:10px;" />',
                obj.qr_image.url
            )
        return "هنوز تولید نشده است."
    qr_image_preview.short_description = "پیش‌نمایش"

    # ---------- استایل دادن به تعداد اسکن ----------
    def scans_count_styled(self, obj):
        color = "#10b981" if obj.scans_count > 0 else "#94a3b8"
        return format_html(
            '<b style="color:{}; font-size:14px;">{}</b> <small style="color:#94a3b8">اسکن</small>',
            color, obj.scans_count
        )
    scans_count_styled.short_description = "آمار"

    # ---------- دکمه‌های عملیات سریع ----------
    def quick_actions(self, obj):
        # لینک باز کردن مقصد
        target_url = obj.target_url
        
        # لینک دانلود مستقیم تصویر
        download_url = obj.qr_image.url if obj.qr_image else "#"
        
        # لینک ویرایش
        edit_url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.id],
        )

        return format_html(
            """
            <div style="display:flex; gap:6px;">
                <!-- مشاهده لینک -->
                <a href="{}" target="_blank" style="
                    display:flex; align-items:center; gap:5px; padding:4px 8px; border-radius:6px;
                    background:linear-gradient(135deg,#60a5fa,#1e40af); color:white;
                    font-size:11px; text-decoration:none; box-shadow:0 2px 4px rgba(0,0,0,.15);
                ">
                    <svg width="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/>
                    </svg>
                    باز کردن
                </a>

                <!-- دانلود تصویر -->
                <a href="{}" download style="
                    display:flex; align-items:center; gap:5px; padding:4px 8px; border-radius:6px;
                    background:linear-gradient(135deg,#34d399,#065f46); color:white;
                    font-size:11px; text-decoration:none; box-shadow:0 2px 4px rgba(0,0,0,.15);
                ">
                    <svg width="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
                    </svg>
                    دانلود
                </a>

                <!-- ویرایش -->
                <a href="{}" style="
                    display:flex; align-items:center; gap:5px; padding:4px 8px; border-radius:6px;
                    background:linear-gradient(135deg,#fbbf24,#92400e); color:white;
                    font-size:11px; text-decoration:none; box-shadow:0 2px 4px rgba(0,0,0,.15);
                ">
                    <svg width="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                    تنظیمات
                </a>
            </div>
            """,
            target_url,
            download_url,
            edit_url,
        )
    quick_actions.short_description = "عملیات"

    # اضافه کردن اکشن گروهی برای تولید مجدد QR Code ها
    actions = ["regenerate_qr_codes"]

    def regenerate_qr_codes(self, request, queryset):
        for obj in queryset:
            obj.generate_qr_code()
            obj.save()
        self.message_user(request, f"کدهای QR برای {queryset.count()} مورد دوباره تولید شد.")
    regenerate_qr_codes.short_description = "تولید مجدد کدهای QR انتخابی"
