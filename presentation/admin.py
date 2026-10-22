from django.contrib import admin
from django.utils.html import mark_safe, format_html
from django.urls import reverse
from .models import IconLibs


@admin.register(IconLibs)
class IconLibsAdmin(admin.ModelAdmin):

    list_display = (
        "icon_preview_small",
        "display_name",
        "name",
        "category_badge",
        "is_active",
        "quick_actions",
    )

    list_filter = ("is_active", "category")

    search_fields = ("name", "display_name", "category")

    list_editable = ("is_active",)

    readonly_fields = ("icon_preview_large", "created_at")

    fieldsets = (
        ("اطلاعات پایه", {
            "fields": ("name", "display_name", "category", "is_active", "created_at")
        }),

        ("فایل آیکون", {
            "fields": ("icon_file", "icon_preview_large"),
            "description": "فرمت‌های مجاز: SVG / PNG / JPG / WEBP"
        }),
    )

    # -----------------------
    # preview کوچک
    # -----------------------

    def icon_preview_small(self, obj):
        if not obj.icon_file:
            return "-"

        file_name = obj.icon_file.name.lower()

        if file_name.endswith(".svg"):
            try:
                with obj.icon_file.open("r") as f:
                    svg = f.read()

                svg = svg.replace(
                    "<svg",
                    '<svg style="width:24px;height:24px;color:#3b82f6"',
                    1
                )

                return mark_safe(svg)

            except Exception:
                return "-"

        return mark_safe(
            f'<img src="{obj.icon_file.url}" '
            'style="width:24px;height:24px;object-fit:contain;" />'
        )

    icon_preview_small.short_description = "آیکون"

    # -----------------------
    # preview بزرگ
    # -----------------------

    def icon_preview_large(self, obj):

        if not obj.icon_file:
            return "فایلی آپلود نشده"

        wrapper = """
        padding:18px;
        background:#f8fafc;
        border:1px dashed #cbd5e1;
        border-radius:12px;
        display:inline-flex;
        align-items:center;
        justify-content:center;
        min-width:120px;
        min-height:120px;
        """

        file_name = obj.icon_file.name.lower()

        if file_name.endswith(".svg"):

            try:
                with obj.icon_file.open("r") as f:
                    svg = f.read()

                svg = svg.replace(
                    "<svg",
                    '<svg style="width:90px;height:90px;color:#2563eb"',
                    1
                )

                return mark_safe(f'<div style="{wrapper}">{svg}</div>')

            except Exception:
                return "خطا در پردازش SVG"

        return mark_safe(
            f'<div style="{wrapper}">'
            f'<img src="{obj.icon_file.url}" style="max-width:90px;max-height:90px;object-fit:contain;" />'
            "</div>"
        )

    icon_preview_large.short_description = "پیش‌نمایش"

    # -----------------------
    # دسته بندی به شکل badge
    # -----------------------

    def category_badge(self, obj):

        if not obj.category:
            return "-"

        return format_html(
            """
            <span style="
                background:#e0f2fe;
                color:#0369a1;
                padding:3px 8px;
                border-radius:6px;
                font-size:11px;
                font-weight:600;
            ">
            {}
            </span>
            """,
            obj.category
        )

    category_badge.short_description = "دسته"

    # -----------------------
    # دکمه های عملیات
    # -----------------------

    def quick_actions(self, obj):

        edit_url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.id]
        )

        file_url = obj.icon_file.url if obj.icon_file else "#"

        return format_html(
            """
            <div style="display:flex;gap:6px">

                <a href="{}" target="_blank" style="
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
                    مشاهده
                </a>

                <a href="{}" download style="
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
                    دانلود
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
                    ویرایش
                </a>

            </div>
            """,
            file_url,
            file_url,
            edit_url,
        )

    quick_actions.short_description = "عملیات"

    # -----------------------
    # اکشن گروهی
    # -----------------------

    actions = ["activate_icons", "deactivate_icons"]

    def activate_icons(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} آیکون فعال شد")

    activate_icons.short_description = "فعال کردن آیکون‌ها"

    def deactivate_icons(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} آیکون غیرفعال شد")

    deactivate_icons.short_description = "غیرفعال کردن آیکون‌ها"



from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from presentation.middleware.domain_proxy import DomainRoute


@admin.register(DomainRoute)
class DomainTLDAdmin(admin.ModelAdmin):

    list_display = (
        "source",
        "destination",
        "active",
        "allow_forward",
    )

    list_filter = (
        "active",
        "allow_forward",
    )

    search_fields = (
        "source",
        "destination",
    )

    ordering = (
        "source",
    )

    list_editable = (
        "active",
    )

    fieldsets = (
        (_("Domain Mapping"), {
            "fields": (
                "source",
                "destination",
            )
        }),
        (_("Status"), {
            "fields": (
                "active",
                "allow_forward",
            )
        }),
    )
