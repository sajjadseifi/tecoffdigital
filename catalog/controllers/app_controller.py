from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from catalog.entities import Catalog, Category, Item

# ==========================================
# 1. رندر صفحه اصلی منو (HTML)
# ==========================================
def catalog_detail(request, catalog_slug):
    # دریافت کاتالوگ فعال
    catalog = get_object_or_404(Catalog, slug=catalog_slug, is_active=True)
    
    # آپدیت بازدیدها
    catalog.views += 1
    catalog.save(update_fields=['views'])
    
    # دریافت مسیر تمپلیت بر اساس انتخاب کاربر (مثلا apps/wallpares/tecof/template.html)
    template_path = f"apps/wallpares/{catalog.theme}/template.html"
    
    context = {
        'catalog': catalog,
    }
    return render(request, template_path, context)


# ==========================================
# 2. API: دریافت آیتم‌های یک دسته‌بندی
# ==========================================
def api_category_items(request, catalog_slug, category_slug):
    # فیلتر کردن آیتم‌های فعال که متعلق به کاتالوگ و دسته‌بندی مورد نظر هستند
    items = Item.objects.filter(
        category__catalog__slug=catalog_slug,
        category__slug=category_slug,
        is_available=True
    ).order_by('order', 'title')
    
    data = []
    for item in items:
        data.append({
            'id': item.id,
            'slug': item.slug,
            'title': item.title,
            'description': item.description,
            'price': float(item.price) if item.price else 0,
            'discount_price': float(item.discount_price) if item.discount_price else 0,
            'final_price': float(item.final_price) if item.final_price else 0,
            'discount_percent': item.discount_percent,
            'image': item.image.url if item.image else None,
            'is_featured': item.is_featured
        })
        
    return JsonResponse(data, safe=False)


# ==========================================
# 3. API: جستجو در منو (با ساختار دسته‌بندی شده)
# ==========================================
def api_catalog_search(request, catalog_slug):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse([], safe=False)
        
    # جستجو در عنوان و توضیحات آیتم‌های فعال این کاتالوگ
    items = Item.objects.select_related('category').filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query) | 
        Q(title__icontains=query) |
        Q(description__icontains=query),
        category__catalog__slug=catalog_slug,
        is_available=True
    ).order_by('category__order', 'order')
    
    # گروه‌بندی آیتم‌های پیدا شده بر اساس دسته‌بندی (برای نمایش درست در فرانت‌اند)
    grouped_results = {}
    for item in items:
        cat_slug = item.category.slug
        if cat_slug not in grouped_results:
            grouped_results[cat_slug] = {
                'slug': cat_slug,
                'title': item.category.title,
                'items': []
            }
            
        grouped_results[cat_slug]['items'].append({
            'id': item.id,
            'slug': item.slug,
            'title': item.title,
            'description': item.description,
            "price": float(item.price) if item.price else 0,
            "discount_price": float(item.discount_price or 0),
            "final_price": float(item.final_price),
            "discount_percent": item.discount_percent,
            'image': item.image.url if item.image else None,
        })
        
    # تبدیل مقادیر دیکشنری به لیست
    response_data = list(grouped_results.values())
    
    return JsonResponse(response_data, safe=False)


# ==========================================
# 4. API: اطلاعات یک دسته‌بندی (اختیاری)
# ==========================================
def api_category_detail(request, catalog_slug, category_slug):
    category = get_object_or_404(
        Category, 
        catalog__slug=catalog_slug, 
        slug=category_slug, 
        is_active=True
    )
    
    data = {
        'id': category.id,
        'slug': category.slug,
        'title': category.title,
        'description': category.description,
        'image': category.image.url if category.image else None,
        'total_items': category.total_items()
    }
    return JsonResponse(data)


# ==========================================
# 5. API: اطلاعات یک محصول (برای مودال/پاپ‌آپ)
# ==========================================
def api_item_detail(request, catalog_slug, item_slug):
    item = get_object_or_404(
        Item, 
        category__catalog__slug=catalog_slug, 
        slug=item_slug, 
        is_available=True
    )
    
    # آپدیت بازدید محصول
    item.views += 1
    item.save(update_fields=['views'])
    
    data = {
        'id': item.id,
        'slug': item.slug,
        'title': item.title,
        'description': item.description,
        'price': str(item.price) if item.price else "0",
        "price": float(item.price) if item.price else 0,
        "discount_price": float(item.discount_price or 0),
        "final_price": float(item.final_price),
        "discount_percent": item.discount_percent,
        'image': item.image.url if item.image else None,
        'sku': item.sku,
        'stock': item.stock,
        'is_featured': item.is_featured
    }
    return JsonResponse(data)



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.text import slugify
from ..models import Catalog

def admin_required(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(admin_required)
def catalog_create_quick(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

    title = request.POST.get("title", "").strip()
    headline = request.POST.get("headline", "").strip()
    subheadline = request.POST.get("subheadline", "").strip()
    loading_title = request.POST.get("loading_title", "").strip()
    theme = request.POST.get("theme", "tecof").strip() or "tecof"

    logo = request.FILES.get("logo")
    banner = request.FILES.get("banner")

    if not title:
        return JsonResponse({"success": False, "message": "نام الزامی است"}, status=400)

    catalog = Catalog.objects.create(
        owner=request.user,
        title=title,
        headline=headline,
        subheadline=subheadline,
        tagline=loading_title,   # موقتاً اینجا ذخیره می‌کنیم
        theme=theme,
        logo=logo,
        banner=banner,
    )

    return JsonResponse({
        "success": True,
        "id": catalog.id,
        "url": catalog.get_absolute_url(),
    })
