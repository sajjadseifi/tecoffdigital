from django.contrib.auth.decorators import login_required
from catalog.services.catalog_service import CatalogService
from django.core.paginator import Paginator
from django.db.models import Q
from catalog.models import Item
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import copy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
from .constants import WALLPAPERS_CONFIG
from django.urls import reverse
from catalog.forms import CatalogSettingForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from catalog.entities import CatalogMember, CatalogInvite
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from catalog.entities import Catalog, CatalogMember, CatalogInvite
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.contrib.auth import get_user_model
import jdatetime
from catalog.models import Catalog, Item, Category
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from catalog.entities import CatalogMember
from django.shortcuts import get_object_or_404, redirect
from catalog.entities import Catalog, CatalogMember
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.cache import cache

from catalog.entities import Catalog, CatalogMember


CACHE_TIMEOUT = 60  # seconds

User = get_user_model()

@login_required
def dashboard_workspace(request):
    user = request.user

    # ایجاد تاریخ شمسی واقعی (مثلا: ۱۴ فروردین ۱۴۰۵)
    today = jdatetime.date.today()
    persian_months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    current_date = f"{today.day} {persian_months[today.month - 1]} {today.year}"

    # ==========================================
    # 1. منطق داشبورد ادمین (Staff)
    # ==========================================
    if user.is_staff:
        # محاسبه آمار کل سیستم
        total_catalogs = Catalog.objects.count()
        all_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_items = Item.objects.count()
        total_views = Catalog.objects.aggregate(sum_views=Sum('views'))['sum_views'] or 0

        # دریافت آخرین داده‌ها برای جداول
        # استفاده از select_related برای بهینه سازی کوئری به دیتابیس
        recent_catalogs = Catalog.objects.select_related('owner').order_by('-created_at')[:6]
        recent_users = User.objects.order_by('-date_joined')[:5]
        # داخل view:
        recent_icons = IconLibs.objects.filter(is_active=True).order_by('-created_at')[:10]



        context = {
            'user_display_name': user.display_name,
            'current_date': current_date,
   
            'stats': {
                'total_catalogs': total_catalogs,
                'active_users': active_users,
                'all_users':all_users,
                'total_items': total_items,
                'total_views': total_views,
            },
            'recent_catalogs': recent_catalogs,
            'recent_users': recent_users,
            'recent_icons':recent_icons,
        }
        
        return render(request, "dashboard/admin/workspace.html", context)

    # ==========================================
    # 2. منطق داشبورد کاربر عادی (صاحب کسب‌وکار)
    # ==========================================
    # فقط کاتالوگ‌های مربوط به همین کاربر را می‌گیریم
    u_catalogs = Catalog.objects.filter(owner=user)
    
    # محاسبه آمار مربوط به شخص کاربر
    u_total_catalogs = u_catalogs.count()
    # تعداد کل آیتم‌هایی که در دسته‌بندی‌های کاتالوگ‌های این کاربر هستند
    u_total_categories = Category.objects.filter(catalog__owner=user).count()
    u_total_items = Item.objects.filter(category__catalog__owner=user).count()
    u_total_views = u_catalogs.aggregate(sum_views=Sum('views'))
    
    context ={ 
        'u_catalogs' : u_catalogs,
        'u_stats': {
            'total_categories': u_total_categories,
            'total_catalogs':   u_total_catalogs,
            'total_items':      u_total_items,
            'total_views':      u_total_views,
        }
    }
    return render(request, "dashboard/workspace.html", context)

@login_required
def dashboard_catalog_members(request):

    catalog = request.catalog

    if not catalog:
        messages.error(request,"هیچ مجموعه فعالی انتخاب نشده")
        return redirect("dashboard")

    is_owner = request.catalog_is_owner
    member = request.catalog_member

    if not is_owner and not member:
        messages.error(request,"دسترسی ندارید")
        return redirect("dashboard")

    members = CatalogMember.objects.filter(
        catalog=catalog,
        is_active=True
    ).select_related("user")

    return render(request,"dashboard/members/dashboard_catalog_members.html",{
        "catalog": catalog,
        "members": members,
        "member": member,
        "is_owner": is_owner,
        "can_manage_members": is_owner or (
            member and member.has_permission("catalog","manage_members")
        )
    })

@login_required 
def dashboard_catalog_setting(request):
    # دریافت کاتالوگ متعلق به کاربر
    catalog = CatalogService.get_singleton_catalog(request.user)
    
    if request.method == 'POST':
        # پاس دادن request.FILES برای آپلود لوگو و کاور الزامی است
        form = CatalogSettingForm(request.POST, request.FILES, instance=catalog)
        if form.is_valid():
            form.save()
            messages.success(request, "تنظیمات کاتالوگ با موفقیت به‌روزرسانی شد.")
            # ریدایرکت به همین صفحه برای جلوگیری از submit مجدد با رفرش
            return redirect('dashboard_catalog_setting') 
        else:
            messages.error(request, "لطفاً خطاهای فرم را بررسی کنید.")
    else:
        form = CatalogSettingForm(instance=catalog)

    
    tabs = [
        {'key':'basic', 'label':'اطلاعات پایه', 'icon':"<svg class='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'></path></svg>", 'fields': ['title','slug','description','business_type']},
        {'key':'about', 'label':'درباره و خدمات', 'icon':"<svg class='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 21H5a2 2 0 01-2-2V7a2 2 0 012-2h2l2 3h7a2 2 0 012 2v9a2 2 0 01-2 2z'></path></svg>", 'fields': ['about','services','working_hours','facilities']},
        {'key':'registration', 'label':'اطلاعات ثبتی', 'icon':"<svg class='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M9 12h6m-3-3v6'></path></svg>", 'fields': ['established_year', 'registration_number', 'tax_id']},
        {'key':'branding', 'label':'برندینگ و رسانه', 'icon':"<svg class='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z'></path></svg>", 'fields': ['logo','cover','banner','promo_video','theme']},
        {'key':'contact', 'label':'تماس و شبکه‌ها', 'icon':"<svg class='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'></path></svg>", 'fields': ['phone','mobile','email','website','address','instagram','telegram','whatsapp','linkedin','aparat','youtube','twitter']},
        {'key':'location', 'label':'مکان‌نما', 'icon':"<svg class='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M12 11c1.104 0 2-.896 2-2s-.896-2-2-2-2 .896-2 2 .896 2 2 2zM12 22s8-4.5 8-10a8 8 0 10-16 0c0 5.5 8 10 8 10z'></path></svg>", 'fields': ['latitude','longitude']},
        {'key':'settings', 'label':'تنظیمات', 'icon':"<svg class='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M12 8v4l3 3'></path><circle cx='12' cy='12' r='10' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'></circle></svg>", 'fields': ['is_active']}
    ]
    context = { 
        'catalog': catalog, 
        'form': form,
        'tabs':tabs,
    }
    return render(request, "dashboard/catalog/dashboard_catalog_settings.html", context)

@login_required
def dashboard_categories_list(request):
    catalog = CatalogService.get_singleton_catalog(request.user)
    
    if catalog:
        categories_list = catalog.categories.order_by('order').all()
    else:
        categories_list = []

    # صفحه‌بندی: نمایش ۱۰ آیتم در هر صفحه
    paginator = Paginator(categories_list, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'catalog': catalog,
        'data': page_obj, # ارسال شیء صفحه‌بندی شده به قالب
    }
    return render(request, "dashboard/catalog/dashboard_categories_list.html", context)



@login_required
def dashboard_items_list(request):
    catalog = CatalogService.get_singleton_catalog(request.user)
    
    if catalog:
        # 1. دریافت کوئری پایه
        items_list = Item.objects.filter(category__catalog=catalog).select_related('category')
        categories = catalog.categories.order_by('order').all()
        
        # 2. دریافت پارامترهای GET از فرم فیلتر
        search_query = request.GET.get('search', '').strip()
        category_id = request.GET.get('category', '')
        status = request.GET.get('status', '')
        sort_by = request.GET.get('sort', '-created_at')

        # 3. اعمال جستجو (در عنوان، SKU و Slug)
        if search_query:
            items_list = items_list.filter(
                Q(title__icontains=search_query) | 
                Q(sku__icontains=search_query) |
                Q(slug__icontains=search_query)
            )

        # 4. اعمال فیلتر دسته‌بندی
        if category_id:
            items_list = items_list.filter(category_id=category_id)

        # 5. اعمال فیلتر وضعیت
        if status == 'active':
            items_list = items_list.filter(is_available=True)
        elif status == 'inactive':
            items_list = items_list.filter(is_available=False)

        # 6. اعمال مرتب‌سازی
        valid_sorts = ['-created_at', 'created_at', 'price', '-price']
        if sort_by in valid_sorts:
            items_list = items_list.order_by(sort_by)
        else:
            items_list = items_list.order_by('-created_at') # پیش‌فرض

    else:
        categories = []
        items_list = []
    
    # 7. صفحه‌بندی (پیشنهاد: برای هماهنگی با قالب، تعداد را 10 قرار دهید)
    paginator = Paginator(items_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'catalog': catalog,
        'data': page_obj,
        'categories': categories,
    }
    return render(request, "dashboard/catalog/dashboard_items_list.html", context)


@login_required
def dashboard_qrcode_list(request):
    # دریافت کاتالوگ کاربر
    catalog = CatalogService.get_singleton_catalog(request.user)
    
    # --- آدرس‌های پیش‌فرض ---
    base_url = f"{request.scheme}://{request.get_host()}"
    default_target_url = f"{base_url}/q/{catalog.slug}/menu" 
    
    qrcodes_list = catalog.qrcodes.all() 
    
    # --- دریافت پارامترهای فیلتر از URL ---
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all')
    sort_by = request.GET.get('sort', '-created_at') # پیش‌فرض: جدیدترین
    
    # --- اعمال فیلترها ---
    # 1. جستجو در عنوان و لینک
    if search_query:
        qrcodes_list = qrcodes_list.filter(
            Q(title__icontains=search_query) | 
            Q(target_url__icontains=search_query)
        )
        
    # 2. فیلتر وضعیت (فعال/غیرفعال)
    if status_filter == 'active':
        qrcodes_list = qrcodes_list.filter(is_active=True)
    elif status_filter == 'inactive':
        qrcodes_list = qrcodes_list.filter(is_active=False)
        
    # 3. مرتب‌سازی
    valid_sorts = {
        '-created_at': '-created_at',   # جدیدترین
        'created_at': 'created_at',     # قدیمی‌ترین
        '-scans_count': '-scans_count', # بیشترین اسکن
        'scans_count': 'scans_count'    # کمترین اسکن
    }
    # جلوگیری از خطای امنیتی با بررسی معتبر بودن فیلد مرتب‌سازی
    if sort_by in valid_sorts:
        qrcodes_list = qrcodes_list.order_by(valid_sorts[sort_by])
    else:
        qrcodes_list = qrcodes_list.order_by('-created_at')

    # --- صفحه‌بندی (Pagination) ---
    # عدد 11 به این دلیل است که با 1 کارت "افزودن جدید"، مجموعاً در یک صفحه 12 کارت نمایش داده شود که برای گریدبندی عالی است.
    paginator = Paginator(qrcodes_list, 11) 
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        # اگر کاربر عدد صفحه‌ای خارج از محدوده زد، صفحه آخر را نشان بده
        page_obj = paginator.page(paginator.num_pages)
        
    context = {
        'catalog': catalog,
        'base_url': base_url,
        'default_target_url': default_target_url,
        
        # ارسال آبجکت صفحه‌بندی شده به جای کل لیست
        'data': page_obj, 
        
        # ارسال مقادیر فیلترها برای حفظ State در فرم‌های فرانت‌اند
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
    }
    
    return render(request, "dashboard/catalog/dashboard_qrcode_list.html", context)



def dashbaord_wallpare_list(request):
    # دریافت کاتالوگ کاربر
    catalog = CatalogService.get_singleton_catalog(request.user)
    
    # ---------------------------------------------------------
    # بخش POST: پردازش تغییر قالب
    # ---------------------------------------------------------
    if request.method == 'POST':
        selected_theme = request.POST.get('theme_key')
        
        # استخراج کلیدهای معتبر برای اعتبارسنجی
        valid_keys = [wp['key'] for wp in WALLPAPERS_CONFIG]
        
        if selected_theme in valid_keys:
            catalog.theme = selected_theme
            catalog.save()
            messages.success(request, "قالب منو با موفقیت تغییر یافت.")
        else:
            messages.error(request, "قالب انتخاب شده نامعتبر است.")
            
    # ---------------------------------------------------------
    # بخش GET: آماده‌سازی داده‌ها برای نمایش
    # ---------------------------------------------------------
    
    # ساخت یک کپی از تنظیمات برای جلوگیری از تغییر متغیر سراسری در رم سرور
    templates = copy.deepcopy(WALLPAPERS_CONFIG)
    
    # بررسی وجود فایل‌های قالب و تعیین قالب فعال
    for wp in templates:
        # تشخیص اینکه آیا این قالب، قالب فعال فعلی کاربر است یا خیر
        wp["is_active"] = (catalog.theme == wp["key"])
        
        try:
            get_template(wp["file_path"])
            wp["safe_template"] = wp["file_path"]
        except TemplateDoesNotExist:
            wp["safe_template"] = "wallpapers/empty.html" # مپ کردن به حالت خالی در صورت عدم وجود

    context = {
        'catalog': catalog,
        "templates": templates,
    }
    return render(request, "dashboard/catalog/dashboard_wallpares_list.html", context)

from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from presentation.models import IconLibs


def dashboard_palate_icons_list(request):
    """
    نمای خواندنی برای نمایش کتابخانه آیکون‌ها.
    - پشتیبانی از جستجو (name، display_name، category)
    - اگر request.is_ajax → خروجی JSON (برای API)
    - اگر GET ساده → نمایش قالب HTML
    """

    query = request.GET.get("q", "").strip()

    icons = IconLibs.objects.filter(is_active=True)

    if query:
        icons = icons.filter(
            Q(name__icontains=query) |
            Q(display_name__icontains=query) |
            Q(category__icontains=query)
        )

    # حالت API (برای Alpine سرچ زنده)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = []
        for i in icons:
            data.append({
                "id": i.id,
                "name": i.name,
                "display_name": i.display_name,
                "category": i.category,
                "url": i.icon_file.url if i.icon_file else None,
                "is_svg": True if (i.icon_file and i.icon_file.url.endswith(".svg")) else False,
            })
        return JsonResponse({"results": data})

    # حالت UI
    return render(request, "dashboard/palate/icons.html", {
        "icons": icons,
        "query": query,
    })
