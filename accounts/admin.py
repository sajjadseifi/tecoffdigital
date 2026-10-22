from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import format_html
from django.utils import timezone
from django.contrib.admin.utils import get_deleted_objects
from django.contrib import admin
from .models import User, OTP


# =========================
# OTP INLINE
# =========================

class OTPInline(admin.TabularInline):
    model = OTP
    extra = 0
    readonly_fields = ("code", "created_at", "expires_at", "is_used")
    can_delete = False


# =========================
# USER ADMIN
# =========================
from .forms import CustomUserAddForm
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserAddForm

    ordering = ["-date_joined"]

    inlines = [OTPInline]

    list_display = (
        "display_name",
        "avatar_preview",
        "phone",
        "email",
        "status_badge",
        "is_staff",
        "login_count",
        "date_joined",
        "quick_actions",
    )

    search_fields = (
        "phone",
        "email",
        "first_name",
        "last_name",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_phone_verified",
        "is_email_verified",
    )

    readonly_fields = (
        "avatar_preview",
        "login_count",
        "last_activity",
        "date_joined",
    )

    actions = [
        "activate_users",
        "deactivate_users",
        "verify_phone",
        "verify_email",
    ]
    add_fieldsets = (
        (
            "ایجاد کاربر جدید",
            {
                "classes": ("wide",),
                "fields": ("phone", "password", "first_name", "last_name", "is_active", "is_staff"),
            },
        ),
    )
    fieldsets = (

        ("اطلاعات کاربر", {
            "fields": (
                "avatar",
                "avatar_preview",
                "phone",
                "password",
            )
        }),

        ("اطلاعات شخصی", {
            "fields": (
                "first_name",
                "last_name",
                "email",
            )
        }),

        ("وضعیت تایید", {
            "fields": (
                "is_phone_verified",
                "is_email_verified",
            )
        }),

        ("دسترسی", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),

        ("آمار", {
            "fields": (
                "login_count",
                "last_activity",
                "date_joined",
            )
        }),

    )

    # =========================
    # PASSWORD CHANGE
    # =========================

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<int:user_id>/password/",
                self.admin_site.admin_view(self.user_change_password),
                name="accounts_user_password_change",
            ),
        ]

        return custom_urls + urls

    def user_change_password(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)

        if request.method == "POST":
            form = AdminPasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password updated successfully.")
                return redirect(
                    reverse(
                        f"admin:{user._meta.app_label}_{user._meta.model_name}_change",
                        args=[user.id],
                    )
                )
        else:
            form = AdminPasswordChangeForm(user)

        opts = self.model._meta   # <-- IMPORTANT

        context = {
            "title": "Change password",
            "form": form,
            "original": user,
            "opts": opts,                        # <-- REQUIRED
            "app_label": opts.app_label,         # <-- sometimes used by templates
            "has_permission": True,              # <-- avoids admin template crashes
            "is_popup": False,
            "save_as": False,
            "change": True,
        }

        return render(request, "admin/auth/user/change_password.html", context)

    # =========================
    # AVATAR
    # =========================

    def avatar_preview(self, obj):

        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;" />',
                obj.avatar.url
            )

        return "—"

    avatar_preview.short_description = "تصویر"

    # =========================
    # DISPLAY NAME
    # =========================

    def display_name(self, obj):

        name = f"{obj.first_name or ''} {obj.last_name or ''}".strip()

        return name or "بدون نام"

    display_name.short_description = "نام"

    # =========================
    # STATUS
    # =========================

    def status_badge(self, obj):

        if obj.is_active:
            color = "#10b981"
            text = "فعال"
        else:
            color = "#ef4444"
            text = "غیرفعال"

        return format_html(
            '<b style="color:{}">{}</b>',
            color,
            text
        )

    status_badge.short_description = "وضعیت"

    # =========================
    # QUICK ACTIONS
    # =========================

    def quick_actions(self, obj):

        edit_url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.id],
        )

        password_url = reverse(
            "admin:accounts_user_password_change",
            args=[obj.id],
        )

        return format_html(
            """
            <div style="display:flex; gap:6px">

                <a href="{}" style="
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
                        <path d="M6 22l2 4l4-2l12-12l-4-4z" fill="white"/>
                    </svg>
                    ویرایش
                </a>

                <a href="{}" style="
                    display:flex;
                    align-items:center;
                    gap:5px;
                    padding:4px 8px;
                    border-radius:6px;
                    background:linear-gradient(135deg,#a78bfa,#5b21b6);
                    color:white;
                    font-size:11px;
                    text-decoration:none;
                    box-shadow:0 2px 4px rgba(0,0,0,.15);
                ">
                    <svg width="13" viewBox="0 0 32 32">
                        <rect x="6" y="14" width="20" height="12" rx="3" fill="white"/>
                        <path d="M10 14V10a6 6 0 0112 0v4" stroke="white" stroke-width="2" fill="none"/>
                    </svg>
                    رمز
                </a>

            </div>
            """,
            edit_url,
            password_url
        )

    quick_actions.short_description = "عملیات"

    # =========================
    # ACTIONS
    # =========================

    def activate_users(self, request, queryset):

        updated = queryset.update(is_active=True)

        self.message_user(request, f"{updated} users activated.")

    activate_users.short_description = "فعال سازی کاربران"

    def deactivate_users(self, request, queryset):

        updated = queryset.update(is_active=False)

        self.message_user(request, f"{updated} users deactivated.")

    deactivate_users.short_description = "غیرفعال سازی کاربران"

    def verify_phone(self, request, queryset):

        updated = queryset.update(is_phone_verified=True)

        self.message_user(request, f"{updated} phones verified.")

    verify_phone.short_description = "تایید شماره موبایل"

    def verify_email(self, request, queryset):

        updated = queryset.update(is_email_verified=True)

        self.message_user(request, f"{updated} emails verified.")

    verify_email.short_description = "تایید ایمیل"


# =========================
# OTP ADMIN
# =========================

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):

    list_display = (
        "code_badge",
        "phone",
        "status_badge",
        "remaining_time",
        "created_at",
        'quick_actions',
    )

    list_filter = (
        "is_used",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "phone",
        "code",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "phone",
        "code",
        "created_at",
        "expires_at",
        "is_used",
    )

    list_per_page = 30

    actions = [
        "mark_as_used",
        "mark_as_unused",
        "delete_expired",
    ]
    
    
    # =========================
    # Actions
    # =========================
    def quick_actions(self, obj):

        return format_html(
            """
            <div style="display:flex; gap:6px">

                <a href="#" style="
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
                        <path d="M16 4v6l6-6-6-6v6C7 4 2 9 2 16s5 12 12 12s12-5 12-12h-4c0 6-4 8-8 8s-8-2-8-8s4-8 8-8z" fill="white"/>
                    </svg>
                    ارسال مجدد
                </a>

            </div>
            """
        )

    quick_actions.short_description = "عملیات"

    # =========================
    # CODE
    # =========================

    def code_badge(self, obj):

        return format_html(
            '<span style="font-weight:bold;font-size:13px;background:#0f172a;color:white;padding:3px 8px;border-radius:6px;">{}</span>',
            obj.code
        )

    code_badge.short_description = "کد"

    # =========================
    # STATUS
    # =========================

    def status_badge(self, obj):

        if obj.is_used:
            color = "#94a3b8"
            text = "مصرف شده"

        elif obj.expires_at < timezone.now():
            color = "#ef4444"
            text = "منقضی"

        else:
            color = "#10b981"
            text = "فعال"

        return format_html(
            '<b style="color:{}">{}</b>',
            color,
            text
        )

    status_badge.short_description = "وضعیت"

    # =========================
    # REMAINING TIME
    # =========================

    def remaining_time(self, obj):

        if obj.expires_at < timezone.now():
            return format_html('<span style="color:#ef4444;">0s</span>')

        diff = obj.expires_at - timezone.now()

        seconds = int(diff.total_seconds())

        return format_html(
            '<span style="color:#10b981;">{}s</span>',
            seconds
        )

    remaining_time.short_description = "زمان باقی‌مانده"

    # =========================
    # ACTIONS
    # =========================

    def mark_as_used(self, request, queryset):

        updated = queryset.update(is_used=True)

        self.message_user(request, f"{updated} OTP marked as used.")

    mark_as_used.short_description = "علامت گذاری به عنوان مصرف شده"

    def mark_as_unused(self, request, queryset):

        updated = queryset.update(is_used=False)

        self.message_user(request, f"{updated} OTP restored.")

    mark_as_unused.short_description = "بازگردانی OTP"

    def delete_expired(self, request, queryset):

        expired = queryset.filter(expires_at__lt=timezone.now())

        count = expired.count()

        expired.delete()

        self.message_user(request, f"{count} expired OTP deleted.")

    delete_expired.short_description = "حذف OTP های منقضی"
