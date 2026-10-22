from django.shortcuts import render
from dashboard.constants import get_template_by_key
from catalog.services.catalog_service import CatalogService
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin, messages
from django.shortcuts import render
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import IconLibs
from .forms import IconLibsForm
from django.core.files.base import ContentFile
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin, messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q,Count
from .models import IconLibs 
from catalog.reserved import  RESERVED_SLUGS,ALLOWED_CATALOG_PAGES
from django.contrib.auth.decorators import login_required
from catalog.models import Catalog
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Q
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import admin
from .models import IconLibs
from .forms import IconLibsForm


def error_404(request, exception):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)



def build_template(template_key,page_name):
    template = get_template_by_key(template_key)

    if template:
        template_path = f'apps/wallpares/{template_key}/{page_name}.html'
    else:
        template_path = f'apps/wallpares/404.html'
        
    return template,template_path

@login_required
def app_catalog_user(request):
    catalog = CatalogService.get_singleton_catalog(request.user)
    return redirect('app_catalog', catalog_slug=catalog.slug, page_name='menu')

from django.shortcuts import render
from django.urls import reverse
from .engine.template_engine import ThemeEngine 

def app_catalog(request, catalog_slug, page_name='website'): 
    catalog = None
    smimilar_catalogs = []
    is_404 = False

    # ۱. اعتبارسنجی نام صفحه
    if page_name not in ALLOWED_CATALOG_PAGES:
        page_name = 'website'

    # ۲. بررسی رزرو نبودن اسلاگ و دریافت کاتالوگ
    if str(catalog_slug) not in RESERVED_SLUGS:
        catalog = CatalogService.get_catalog_by_slug(catalog_slug)
        if not catalog:
            is_404 = True
            smimilar_catalogs = CatalogService.search_similar(catalog_slug)
    else:
        is_404 = True
        smimilar_catalogs = CatalogService.search_similar(catalog_slug)
    
        # =========================
    # REDIRECT / PROXY
    # =========================

    if catalog and catalog.redirect_url and catalog.redirect_url_active:
        if catalog.redirect_url_portal:
            return render(request, 'apps/wallpares/portxl.html', {'catalog':catalog})

        return redirect(catalog.redirect_url)

    # ۳. تعیین کلید تم
    theme_key = catalog.theme if catalog and hasattr(catalog, 'theme') and catalog.theme else ThemeEngine.DEFAULT_THEME

    # ۴. مسیریابی قالب با استفاده از موتور تم (ThemeEngine)
    if is_404:
        page_name = '404'
        final_template_path = ThemeEngine.get_error_page(404)
    else:
        final_template_path = ThemeEngine.resolve_template(theme_key, page_name)
        
        # اگر فایل‌های تم اصلا وجود نداشتند و انجین خروجی 404 داد
        if final_template_path == ThemeEngine.get_error_page(404):
            is_404 = True
            page_name = '404'

    # ۵. ساخت متغیرهای کانتکست
    base_url = reverse('app_catalog_base', kwargs={'catalog_slug': catalog_slug})

    context = {
        "catalog_slug": catalog_slug,
        "catalog": catalog,
        "theme_key": theme_key,  # کلید تم را برای استفاده در HTML می‌فرستیم
        "is_preview_mode": False,
        "current_page": page_name,
        "base_url": base_url,
        "smimilar_catalogs": smimilar_catalogs # دیکته متغیر مطابق کد خودتان حفظ شد
    }

    # ۶. رندر خروجی (ارسال کد 404 برای سئو بسیار مهم است)
    status_code = 404 if is_404 else 200
    return render(request, final_template_path, context, status=status_code)


def preview_template(request, catalog_id, template_key, page_name='website'): 
    if page_name not in ALLOWED_CATALOG_PAGES:
        page_name = 'website' 

    template,template_path = build_template(template_key,page_name)

    catalog = None
    is_preview_mode = False

    if str(catalog_id) not in ['0', 'dummy']:
        catalog = CatalogService.get_catalog_by_id(catalog_id)
    else:
        is_preview_mode = True

    base_url = reverse('preview_template_base', kwargs={ 'catalog_id': catalog_id, 'template_key': template_key })

    context = {
        "catalog": catalog,
        "template": template,
        "is_preview_mode": is_preview_mode,
        "current_page": page_name, 
        "base_url": base_url,      
    }

    return render(request, template_path, context)



# ==========================================
# 1. Page Render View (فقط لود کردن صفحه خالی HTML)
# ==========================================
@staff_member_required
@require_http_methods(["GET"])
def icons_gallery_page(request):
    """
    این ویو فقط قالب HTML صفحه را رندر می‌کند.
    داده‌ها بعداً توسط جاوااسکریپت از طریق API دریافت می‌شوند.
    """
    context = admin.site.each_context(request)
    context.update({'title': 'گالری آیکون‌ها'})
    return render(request, "admin/pages/icons_gallery.html", context)


# ==========================================
# 2. API: List & Search (لیست کردن و جستجو با صفحه‌بندی)
# ==========================================
@staff_member_required
@require_http_methods(["GET"])
def api_icons_list(request):
    search_query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)
    queryset = IconLibs.objects.all().order_by('-created_at')

    if search_query:
        queryset = queryset.filter(Q(name__icontains=search_query) | Q(display_name__icontains=search_query))
        
    paginator = Paginator(queryset, 30)
    page_obj = paginator.get_page(page_number)
    
    icons_data = []
    for icon in page_obj:
        content = ''
        is_svg = False
        if icon.icon_file and icon.icon_file.name.lower().endswith('.svg'):
            is_svg = True
            try:
                with icon.icon_file.open('r') as f:
                    content = f.read()
            except Exception:
                pass
                
        icons_data.append({
            'id': icon.id, 
            'name': icon.name, 
            'display_name': icon.display_name,
            'category': icon.category or '', 
            'is_active': icon.is_active,
            'url': icon.icon_file.url if icon.icon_file else '',
            'content': content, 
            'is_svg': is_svg,
        })

    return JsonResponse({
        'status': 'success',
        'data': icons_data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_items': paginator.count
        }
    })


# ==========================================
# 3. API: Create & Update (افزودن و ویرایش)
# ==========================================
@staff_member_required
@require_http_methods(["POST"])
def api_icon_save(request):
    # گرفتن کپی از داده‌ها
    data = request.POST.copy()
    files = request.FILES.copy()
    
    icon_id = data.get('icon_id')
    pasted_svg = data.get('svg_content', '').strip()
    name = data.get('name', 'icon')

    # هندل کردن کد SVG متنی
    if pasted_svg:
        if '<svg' in pasted_svg.lower() and '</svg>' in pasted_svg.lower():
            file_name = f"{name}.svg"
            files['icon_file'] = ContentFile(pasted_svg.encode('utf-8'), name=file_name)
        else:
            return JsonResponse({'status': 'error', 'message': 'کد وارد شده یک SVG معتبر نیست.'}, status=400)

    # تشخیص ویرایش یا افزودن
    if icon_id:  # حالت ویرایش
        instance = get_object_or_404(IconLibs, id=icon_id)
        if not files.get('icon_file'):
            files['icon_file'] = instance.icon_file
            
        form = IconLibsForm(data, files, instance=instance)
        msg_success = 'آیکون با موفقیت ویرایش شد.'
    else:  # حالت افزودن
        form = IconLibsForm(data, files)
        msg_success = 'آیکون جدید با موفقیت اضافه شد.'

    # ذخیره فرم
    if form.is_valid():
        form.save()
        return JsonResponse({'status': 'success', 'message': msg_success})
    else:
        # استخراج ارورهای فرم برای ارسال به فرانت‌اند
        errors = {field: error[0] for field, error in form.errors.items()}
        return JsonResponse({'status': 'error', 'message': 'خطا در اعتبارسنجی فرم', 'errors': errors}, status=400)


# ==========================================
# 4. API: Delete Single (حذف تکی)
# ==========================================
@staff_member_required
@require_http_methods(["POST", "DELETE"])
def api_icon_delete(request, icon_id):
    icon = get_object_or_404(IconLibs, id=icon_id)
    
    # اختیاری: پاک کردن فایل فیزیکی آیکون از روی سرور قبل از حذف دیتابیس
    if icon.icon_file:
        icon.icon_file.delete(save=False)
        
    icon.delete()
    return JsonResponse({'status': 'success', 'message': 'آیکون با موفقیت حذف شد.'})


# ==========================================
# 5. API: Bulk Delete (حذف گروهی - Select)
# ==========================================
@staff_member_required
@require_http_methods(["POST"])
def api_icon_bulk_delete(request):
    try:
        # چون دیتای این بخش معمولا به صورت JSON خام از فرانت ارسال می‌شود
        data = json.loads(request.body)
        icon_ids = data.get('ids', [])
        
        if not icon_ids:
            return JsonResponse({'status': 'error', 'message': 'هیچ آیکونی انتخاب نشده است.'}, status=400)

        # اختیاری: پاک کردن فایل‌های فیزیکی
        icons = IconLibs.objects.filter(id__in=icon_ids)
        for icon in icons:
            if icon.icon_file:
                icon.icon_file.delete(save=False)
                
        # حذف از دیتابیس
        icons.delete()
        
        return JsonResponse({'status': 'success', 'message': f'{len(icon_ids)} آیکون با موفقیت حذف شدند.'})
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'فرمت اطلاعات ارسالی نامعتبر است.'}, status=400)


import openpyxl
import json
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from .models import IconLibs

# ==========================================
# API: Preview Excel (فقط خواندن و ارسال به فرانت)
# ==========================================
@staff_member_required
@require_http_methods(["POST"])
def api_preview_excel(request):
    if 'excel_file' not in request.FILES:
        return JsonResponse({'status': 'error', 'message': 'فایلی ارسال نشده است.'}, status=400)

    excel_file = request.FILES['excel_file']
    if not excel_file.name.endswith('.xlsx'):
        return JsonResponse({'status': 'error', 'message': 'لطفا یک فایل اکسل (.xlsx) معتبر آپلود کنید.'}, status=400)

    try:
        wb = openpyxl.load_workbook(excel_file, data_only=True)
        sheet = wb.active
        
        preview_data = []
        # فرض بر این است که ردیف 1 هدر (ستون‌ها) است: 
        # A: Name, B: Display Name, C: Category, D: SVG Content
        for row in sheet.iter_rows(min_row=2, values_only=True):
            name = str(row[0]).strip() if row[0] else None
            svg_content = str(row[3]).strip() if row[3] else None
            
            # اگر نام یا کد SVG خالی بود، از آن ردیف رد شو
            if not name or not svg_content or name == 'None':
                continue
                
            preview_data.append({
                'name': name,
                'display_name': str(row[1]).strip() if row[1] else name,
                'category': str(row[2]).strip() if row[2] else '',
                'svg_content': svg_content
            })
            
        return JsonResponse({'status': 'success', 'data': preview_data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'خطا در پردازش اکسل: {str(e)}'}, status=400)


# ==========================================
# API: Bulk Save from JSON (ذخیره نهایی)
# ==========================================
@staff_member_required
@require_http_methods(["POST"])
def api_bulk_save_excel(request):
    try:
        data = json.loads(request.body)
        icons_list = data.get('icons', [])
        
        if not icons_list:
            return JsonResponse({'status': 'error', 'message': 'لیست آیکون‌ها خالی است.'}, status=400)

        saved_count = 0
        skipped_count = 0

        for item in icons_list:
            name = item.get('name')
            svg_content = item.get('svg_content')
            
            if not name or not svg_content:
                continue
                
            # جلوگیری از خطای تکراری بودن نام (unique=True)
            if IconLibs.objects.filter(name=name).exists():
                skipped_count += 1
                continue

            file_name = f"{name}.svg"
            
            IconLibs.objects.create(
                name=name,
                display_name=item.get('display_name', name),
                category=item.get('category', ''),
                is_active=True,
                icon_file=ContentFile(svg_content.encode('utf-8'), name=file_name)
            )
            saved_count += 1
            
        return JsonResponse({
            'status': 'success', 
            'message': f'{saved_count} آیکون ذخیره شد. {skipped_count} آیکون تکراری نادیده گرفته شد.'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# ==========================================
# API: Bulk Save from JSON (ارسال مستقیم از تکست‌باکس)
# ==========================================
@staff_member_required
@require_http_methods(["POST"])
def api_bulk_save_json(request):
    try:
        data = json.loads(request.body)
        icons_list = data.get('icons', [])
        
        if not icons_list:
            return JsonResponse({'status': 'error', 'message': 'لیست آیکون‌ها خالی است یا فرمت اشتباه است.'}, status=400)

        saved_count = 0
        skipped_count = 0

        for item in icons_list:
            name = item.get('name')
            svg_content = item.get('svg_content', item.get('content', '')) # پشتیبانی از هر دو کلید
            
            if not name or not svg_content:
                continue
                
            # جلوگیری از خطای تکراری بودن نام
            if IconLibs.objects.filter(name=name).exists():
                skipped_count += 1
                continue

            file_name = f"{name}.svg" if '<svg' in svg_content.lower() else f"{name}.png"
            
            IconLibs.objects.create(
                name=name,
                display_name=item.get('display_name', name),
                category=item.get('category', 'بدون دسته'),
                is_active=True,
                icon_file=ContentFile(svg_content.encode('utf-8'), name=file_name)
            )
            saved_count += 1
            
        return JsonResponse({
            'status': 'success', 
            'message': f'{saved_count} آیکون با موفقیت ثبت شد. {skipped_count} آیکون تکراری نادیده گرفته شد.'
        })
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'فرمت JSON نامعتبر است.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)




def catalogs(request):

    business_types = (
        Catalog.objects
        .filter(is_active=True, is_public=True)
        .exclude(business_type="")
        .values("business_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )[:50]

    sections = []

    for bt in business_types:

        catalogs = Catalog.objects.filter(
            business_type=bt["business_type"],
            is_active=True,
            is_public=True
        )[:8]
        if catalogs and len(catalogs):
            sections.append({
                "type": bt["business_type"],
                "catalogs": catalogs
            })

    return render(request, "apps/catalogs/app.html", {
        "sections": sections
    })

def category_catalogs_detail(request, business_type):
    catalogs = Catalog.objects.filter(
        business_type=business_type, 
        is_public=True,  # فقط عمومی‌ها
        is_active=True   # فقط فعال‌ها
    )

    context = {
        'category_name': business_type,
        'catalogs': catalogs,
    }
    
    # آدرس فایل HTML که فرستادید را اینجا وارد کنید
    return render(request, 'apps/catalogs/app_catalog.html', context)

# لود بیشتر دسته‌ها (infinite scroll)
def catalog_load_more(request):

    offset = int(request.GET.get("offset", 0))

    business_types = (
        Catalog.objects
        .filter(is_active=True, is_public=True)
        .exclude(business_type="")
        .values("business_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )[offset:offset + 10]

    data = []

    for bt in business_types:

        catalogs = Catalog.objects.filter(
            business_type=bt["business_type"],
            is_active=True,
            is_public=True
        )[:8]

        data.append({
            "type": bt["business_type"],
            "catalogs": [
                {
                    "title": c.title,
                    "logo": c.logo_or_default,
                    "url": c.get_absolute_url(),
                    "description": c.short_description
                }
                for c in catalogs
            ]
        })

    return JsonResponse(data, safe=False)


# API جستجو
def search_catalogs(request):

    q = request.GET.get("q", "").strip()

    catalogs = Catalog.objects.filter(
        Q(title__icontains=q) |
        Q(description__icontains=q) |
        Q(business_type__icontains=q),
        is_active=True,
        is_public=True
    ).order_by("-views")[:20]

    results = []

    for c in catalogs:
        results.append({
            "title": c.title,
            "url": c.get_absolute_url(),
            "logo": c.logo_or_default,
            "business_type": c.business_type,
            "description": c.short_description
        })

    return JsonResponse({
        "results": results
    })

# views.py

def tec_team_land(request):

    teams = [
        {
            "team_key": "TEC Boy BNUT",
            "display": "پسران تک نیت",
            "members": [
                {"label": "Soul", "persian": "روح", "role": "ایده‌پرداز و معماری سیستم"},
                {"label": "CoreX", "persian": "کورکس", "role": "هسته پردازش و توسعه عمیق"},
            ]
        },
        {
            "team_key": "TEC Girls BNUT",
            "display": "دختران تک نیت",
            "members": [
                {"label": "Devx", "persian": "دویکس", "role": "توسعه‌دهنده مرکزی و صاحب هسته"},
                {"label": "Vision", "persian": "ویژن", "role": "خلق ایده و طراحی تجربه کاربری"},
            ]
        },
        {
            "team_key": "TEC Secure BNUT",
            "display": "سکیور تک نیت",
            "members": [
                {"label": "Shadow", "persian": "شدو", "role": "امنیت سایبری و نفوذ"},
                {"label": "GhostLine", "persian": "گوست‌لاین", "role": "تحلیل امنیت و فورنسیک"},
            ]
        },

    ]

    return render(request, "apps/public/tec_team_land.html", {"teams": teams})

dream_lands = [
    { 
        'title': 'هوش مصنوعی', 
        'url_name': 'tecland_dream',
        'icon': '''<svg class="w-10 h-10 text-sky-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L3 7L12 12L21 7L12 2Z" fill="currentColor" fill-opacity="1.0"/>
            <path d="M3 7V13L12 18L21 13V7L12 12L3 7Z" fill="currentColor" fill-opacity="0.4"/>
            <path d="M12 12V22L21 17V7L12 12Z" fill="currentColor" fill-opacity="0.7"/>
            <path d="M12 12V22L3 17V7L12 12Z" fill="currentColor" fill-opacity="0.2"/>
        </svg>'''
    },
    { 
        'title': 'کتابخانه دیجیتال', 
        'url_name': 'tecland_book',
        'icon': '''<svg class="w-10 h-10 text-indigo-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 4L2 9L12 14L22 9L12 4Z" fill="currentColor" fill-opacity="0.9"/>
            <path d="M2 9V12L12 17L22 12V9L12 14L2 9Z" fill="currentColor" fill-opacity="0.5"/>
            <path d="M2 13V16L12 21L22 16V13L12 18L2 13Z" fill="currentColor" fill-opacity="0.3"/>
        </svg>'''
    },
    { 
        'title': 'مستندات جامع', 
        'url_name': 'tecland_doc',
        'icon': '''<svg class="w-10 h-10 text-emerald-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2L4 7V17L14 12V2Z" fill="currentColor" fill-opacity="1.0"/>
            <path d="M4 7L14 12L22 8L12 3L4 7Z" fill="currentColor" fill-opacity="0.5"/>
            <path d="M14 12V22L22 18V8L14 12Z" fill="currentColor" fill-opacity="0.8"/>
            <path d="M8 8.5L12 10.5V12.5L8 10.5V8.5Z" fill="#1e293b" fill-opacity="0.5"/>
        </svg>'''
    },
    { 
        'title': 'ابزار توسعه', 
        'url_name': 'tecland_dev',
        'icon': '''<svg class="w-10 h-10 text-blue-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 4L2 7V17L8 20V4Z" fill="currentColor" fill-opacity="0.4"/>
            <path d="M16 4L22 7V17L16 20V4Z" fill="currentColor" fill-opacity="0.8"/>
            <path d="M8 4L16 4L22 7L16 20L8 20L2 7L8 4Z" fill="currentColor" fill-opacity="0.1"/>
            <path d="M8 4L16 4V20L8 20V4Z" fill="currentColor" fill-opacity="1.0"/>
        </svg>'''
    },
    { 
        'title': 'فضای کاری', 
        'url_name': 'tecland_team',
        'icon': '''<svg class="w-10 h-10 text-purple-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L5 6L12 10L19 6L12 2Z" fill="currentColor" fill-opacity="1.0"/>
            <path d="M5 6V11L12 15V10L5 6Z" fill="currentColor" fill-opacity="0.6"/>
            <path d="M19 6V11L12 15V10L19 6Z" fill="currentColor" fill-opacity="0.3"/>
            <path d="M12 12L5 16L12 20L19 16L12 12Z" fill="currentColor" fill-opacity="0.8"/>
            <path d="M19 16V21L12 25V20L19 16Z" fill="currentColor" fill-opacity="0.2"/>
            <path d="M5 16V21L12 25V20L5 16Z" fill="currentColor" fill-opacity="0.5"/>
        </svg>'''
    },
    { 
        'title': 'زیرساخت', 
        'url_name': 'tecland_devops',
        'icon': '''<svg class="w-10 h-10 text-cyan-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L4 6V9L12 13L20 9V6L12 2Z" fill="currentColor" fill-opacity="0.9"/>
            <path d="M4 11V14L12 18L20 14V11L12 15L4 11Z" fill="currentColor" fill-opacity="0.6"/>
            <path d="M4 16V19L12 23L20 19V16L12 20L4 16Z" fill="currentColor" fill-opacity="0.3"/>
        </svg>'''
    },
    { 
        'title': 'گیمینگ', 
        'url_name': 'tecland_game',
        'icon': '''<svg class="w-10 h-10 text-pink-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 4L3 8.5L12 13L21 8.5L12 4Z" fill="currentColor" fill-opacity="1.0"/>
            <path d="M3 8.5V14.5L12 19V13L3 8.5Z" fill="currentColor" fill-opacity="0.4"/>
            <path d="M21 8.5V14.5L12 19V13L21 8.5Z" fill="currentColor" fill-opacity="0.8"/>
            <circle cx="16.5" cy="11.5" r="1" fill="#1e293b" fill-opacity="0.7"/>
            <circle cx="18.5" cy="10.5" r="1" fill="#1e293b" fill-opacity="0.7"/>
        </svg>'''
    },
    { 
        'title': 'بازار کار', 
        'url_name': 'tecland_job',
        'icon': '''<svg class="w-10 h-10 text-yellow-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 5L4 9L12 13L20 9L12 5Z" fill="currentColor" fill-opacity="0.3"/>
            <path d="M4 9V17L12 21V13L4 9Z" fill="currentColor" fill-opacity="1.0"/>
            <path d="M20 9V17L12 21V13L20 9Z" fill="currentColor" fill-opacity="0.6"/>
            <path d="M10 2L8 4V8L10 6V2Z" fill="currentColor" fill-opacity="0.8"/>
            <path d="M14 2L16 4V8L14 6V2Z" fill="currentColor" fill-opacity="0.4"/>
            <path d="M10 2L14 2L16 4L12 4L10 2Z" fill="currentColor" fill-opacity="1.0"/>
        </svg>'''
    }
]


def landing_page(request):
    return render(request, "apps/landing.html",{'dream_lands': dream_lands})

def tecland(request):
    template = "apps/tecland/tecland.html"
    context = {}
    return render(request, template,context)

def tecland_dream(request):
    template = "apps/tecland/tecland_dream.html"
    context = { 'dream_lands': dream_lands }
    return render(request, template,context)
    
def tecland_dev(request):
    template = "apps/tecland/tecland_dev.html"
    context = {}
    return render(request, template,context)

def tecland_book(request):
    template = "apps/tecland/tecland_book.html"
    context = {}
    return render(request, template,context)

def tecland_ketabche(request):
    template = "apps/tecland/tecland_ketabche.html"
    context = {}
    return render(request, template,context)

def tecland_doc(request):
    template = "apps/tecland/tecland_doc.html"
    context = {}
    return render(request, template,context)

def tecland_team(request):
    template = "apps/tecland/tecland_team.html"
    context = {}
    return render(request, template,context)

def tecland_game(request):
    template = "apps/tecland/tecland_game.html"
    context = {}
    return render(request, template,context)

def tecland_work(request):
    template = "apps/tecland/tecland_work.html"
    context = {}
    return render(request, template,context)

def tecland_job(request):
    template = "apps/tecland/tecland_job.html"
    context = {}
    return render(request, template,context)

def tecland_devops(request):
    template = "apps/tecland/tecland_devops.html"
    context = {}
    return render(request, template,context)

