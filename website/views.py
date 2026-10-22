from django.shortcuts import render
from django.urls import reverse
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from website.models import LandingSection, SectionItem
from website.forms import WebsiteSettingsForm, LandingSectionForm, SectionItemForm
from website.services import get_or_create_website_settings, update_website_settings
from catalog.services.catalog_service import CatalogService 
from django.contrib.auth.decorators import login_required
from catalog.services.catalog_service import CatalogService
# ==========================================
# توابع کمکی (Helper Functions)
# ==========================================

def get_user_website_settings(user):
    """تابع کمکی برای دریافت تنظیمات وب‌سایت کاربر جاری"""
    catalog = CatalogService.get_singleton_catalog(user)
    if not catalog:
        return None
    return get_or_create_website_settings(catalog)

def get_settings_or_404(user):
    """
    جلوگیری از باگ امنیتی:
    اگر کاربر کاتالوگ نداشت، اجازه دسترسی به ویرایش/حذف را نمی‌دهد.
    """
    settings = get_user_website_settings(user)
    if not settings:
        raise Http404("شما هنوز تنظیمات وب‌سایت ندارید.")
    return settings

# ==========================================
# مدیریت اصلی وب‌سایت
# ==========================================

@login_required
def dashboard_website(request):
    """صفحه اصلی تنظیمات و لیست بخش‌ها"""
    website_settings = get_user_website_settings(request.user)
    
    if not website_settings:
        messages.error(request, "شما هنوز کاتالوگی ایجاد نکرده‌اید.")
        return redirect('dashboard_home') # نام ویوی داشبورد اصلی خود را جایگزین کنید

    if request.method == 'POST':
        updated_settings, errors = update_website_settings(website_settings, request.POST, request.FILES)
        if updated_settings:
            messages.success(request, "تنظیمات وب‌سایت با موفقیت بروزرسانی شد.")
            # اگر می‌خواهید بعد از ذخیره تنظیمات روی تب تنظیمات بماند
            return redirect(f"{reverse('dashboard_website')}?tab=settings")
        else:
            messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")
            form = WebsiteSettingsForm(request.POST, request.FILES, instance=website_settings)
    else:
        form = WebsiteSettingsForm(instance=website_settings)

    sections = website_settings.sections.all().order_by('order')

    context = {
        'form': form,
        'website_settings': website_settings,
        'sections': sections,
    }
    return render(request, 'dashboard/website/dashboard_website.html', context)


# ==========================================
# مدیریت بخش‌ها (Sections)
# ==========================================

@login_required
def dashboard_section_create(request):
    website_settings = get_settings_or_404(request.user)
    
    if request.method == 'POST':
        form = LandingSectionForm(request.POST, request.FILES)
        if form.is_valid():
            section = form.save(commit=False)
            section.website = website_settings
            section.save()
            messages.success(request, "بخش جدید با موفقیت اضافه شد.")
            return redirect(f"{reverse('dashboard_website')}?tab=sections")
    else:
        form = LandingSectionForm()

    return render(request, 'dashboard/website/dashboard_section_form.html', {'form': form, 'section': None})

@login_required
def dashboard_section_edit(request, pk):
    website_settings = get_settings_or_404(request.user)
    section = get_object_or_404(LandingSection, pk=pk, website=website_settings)

    if request.method == 'POST':
        form = LandingSectionForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "بخش با موفقیت ویرایش شد.")
            return redirect('dashboard_section_edit', pk=pk)
    else:
        form = LandingSectionForm(instance=section)

    return render(request, 'dashboard/website/dashboard_section_form.html', {'form': form, 'section': section})

@login_required
def dashboard_section_delete(request, pk):
    website_settings = get_settings_or_404(request.user)
    section = get_object_or_404(LandingSection, pk=pk, website=website_settings)
    
    section.delete()
    messages.success(request, "بخش مورد نظر حذف شد.")
    return redirect(f"{reverse('dashboard_website')}?tab=sections")

@login_required
def dashboard_section_toggle(request, pk):
    """تغییر وضعیت فعال/غیرفعال بودن یک بخش"""
    website_settings = get_settings_or_404(request.user)
    section = get_object_or_404(LandingSection, pk=pk, website=website_settings)
    
    section.is_active = not section.is_active
    section.save()
    
    status = "فعال" if section.is_active else "غیرفعال"
    messages.success(request, f'وضعیت بخش "{section.title}" به {status} تغییر یافت.')
    
    return redirect(f"{reverse('dashboard_website')}?tab=sections")


# ==========================================
# مدیریت آیتم‌ها (Items)
# ==========================================

@login_required
def dashboard_item_create(request, section_id):
    website_settings = get_settings_or_404(request.user)
    section = get_object_or_404(LandingSection, pk=section_id, website=website_settings)

    if request.method == 'POST':
        form = SectionItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.section = section
            item.save()
            messages.success(request, "آیتم جدید با موفقیت اضافه شد.")
            return redirect('dashboard_section_edit', pk=section.id)
    else:
        form = SectionItemForm()

    return render(request, 'dashboard/website/dashboard_item_form.html', {
        'form': form, 
        'item': None, 
        'section_id': section.id
    })

@login_required
def dashboard_item_edit(request, pk):
    website_settings = get_settings_or_404(request.user)
    # دسترسی به آیتمی که بخشِ آن متعلق به وب‌سایت این کاربر است
    item = get_object_or_404(SectionItem, pk=pk, section__website=website_settings)

    if request.method == 'POST':
        form = SectionItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "آیتم با موفقیت ویرایش شد.")
            return redirect('dashboard_section_edit', pk=item.section.id)
    else:
        form = SectionItemForm(instance=item)

    return render(request, 'dashboard/website/dashboard_item_form.html', {
        'form': form, 
        'item': item, 
        'section_id': item.section.id
    })

@login_required
def dashboard_item_delete(request, pk):
    website_settings = get_settings_or_404(request.user)
    item = get_object_or_404(SectionItem, pk=pk, section__website=website_settings)
    
    section_id = item.section.id
    item.delete()
    messages.success(request, "آیتم مورد نظر حذف شد.")
    
    return redirect('dashboard_section_edit', pk=section_id)
