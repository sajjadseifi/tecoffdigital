from .models import WebsiteSettings

def get_or_create_website_settings(catalog):
    """
    دریافت یا ایجاد تنظیمات وب‌سایت برای یک کاتالوگ مشخص
    """
    settings, created = WebsiteSettings.objects.get_or_create(catalog=catalog)
    return settings

def update_website_settings(settings_instance, data, files):
    """
    بروزرسانی تنظیمات وب‌سایت از طریق فرم
    """
    from .forms import WebsiteSettingsForm
    form = WebsiteSettingsForm(data, files, instance=settings_instance)
    if form.is_valid():
        return form.save(), None
    return None, form.errors

def get_website_sections(settings_instance):
    """
    دریافت تمام بخش‌های (Sections) مربوط به یک وب‌سایت
    """
    return settings_instance.sections.all()
