from django.shortcuts import render
from django.http import Http404
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .services.catalog_service import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.text import slugify
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .entities import *

from .serializers import CategorySerializer,ItemSerializer
from .services.catalog_service import CatalogService

@login_required
def create_or_update_catalog_api(request):
    """
    API برای ایجاد یا ویرایش کاتالوگ کاربر.
    اگر کاتالوگ وجود نداشت: ساخته می‌شود.
    اگر وجود داشت: آپدیت می‌شود.
    """
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST method allowed."},
            status=405
        )

    title = request.POST.get("title")
    description = request.POST.get("description", "")

    if not title:
        return JsonResponse(
            {"error": "Title is required."},
            status=400
        )

    service = CatalogService(request.user)
    catalog = service.get_catalog()  # فقط واکشی، بدون ساختن خودکار

    if catalog is None:
        # ایجاد کاتالوگ
        catalog = Catalog.objects.create(
            owner=request.user,
            title=title,
            slug=slugify(title),
            description=description
        )
        created = True
    else:
        # آپدیت کاتالوگ
        catalog.title = title
        catalog.slug = slugify(title)
        catalog.description = description
        catalog.save()
        created = False

    return JsonResponse({
        "success": True,
        "created": created,
        "catalog": {
            "id": catalog.id,
            "title": catalog.title,
            "slug": catalog.slug,
            "description": catalog.description,
        }
    })

@login_required
def catalog_switch(request, catalog_id):

    member = CatalogMember.objects.filter(
        catalog_id=catalog_id,
        user=request.user
    ).first()

    if member:
        request.session["active_catalog"] = catalog_id

    return redirect(request.META.get("HTTP_REFERER", "/dashboard/"))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def category_create(request):
    catalog = CatalogService.get_singleton_catalog(request.user)
    referer_url = request.META.get('HTTP_REFERER', 'dashboard_categories_list')

    if not catalog:
        messages.error(request, "کاتالوگی یافت نشد.")
        return redirect(referer_url)

    data = request.data.copy()

    # مدیریت تصویر
    try:
        image_file = process_base64_image(data.get('cropped_image_base64'), prefix="category")
        if image_file:
            data['image'] = image_file
    except ValueError as e:
        messages.error(request, str(e))
        return redirect(referer_url)

    serializer = CategorySerializer(data=data)

    if serializer.is_valid():
        serializer.save(catalog=catalog)
        messages.success(request, "دسته‌بندی با موفقیت ایجاد شد.")
        return redirect(referer_url)

    for field, errors in serializer.errors.items():
        for error in errors:
            messages.error(request, f"خطا در {field}: {error}")

    return redirect(referer_url)


@api_view(['POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def category_edit(request, category_id):
    catalog = CatalogService.get_singleton_catalog(request.user)
    referer_url = request.META.get('HTTP_REFERER', 'dashboard_categories_list')
    
    category = get_object_or_404(Category, id=category_id, catalog=catalog)

    data = request.data.copy()

    # مدیریت تصویر
    try:
        image_file = process_base64_image(data.get('cropped_image_base64'), prefix="category")
        if image_file:
            data['image'] = image_file
    except ValueError as e:
        messages.error(request, str(e))
        return redirect(referer_url)

    serializer = CategorySerializer(category, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        messages.success(request, "دسته‌بندی با موفقیت بروزرسانی شد.")
        return redirect(referer_url)

    for field, errors in serializer.errors.items():
        for error in errors:
            messages.error(request, f"خطا در {field}: {error}")

    return redirect(referer_url)


@api_view(['POST', 'DELETE']) # اضافه شدن POST برای پشتیبانی از فرم‌های ساده HTML
@permission_classes([IsAuthenticated])
def category_delete(request, category_id):
    catalog = CatalogService.get_singleton_catalog(request.user)
    referer_url = request.META.get('HTTP_REFERER', 'dashboard_categories_list')
    
    category = get_object_or_404(Category, id=category_id, catalog=catalog)

    try:
        category_title = category.title
        category.delete()
        messages.success(request, f"دسته‌بندی '{category_title}' با موفقیت حذف شد.")
    except Exception as e:
        # حالت غیر عادی (مثلاً خطای دیتابیس در هنگام حذف)
        messages.error(request, f"خطا در حذف دسته‌بندی: {str(e)}")

    return redirect(referer_url)

from .utils import process_base64_image

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def item_create(request):
    catalog = CatalogService.get_singleton_catalog(request.user)
    referer_url = request.META.get('HTTP_REFERER', 'dashboard_items_list')

    if not catalog:
        messages.error(request, "کاتالوگی یافت نشد.")
        return redirect(referer_url)

    category_id = request.data.get('category')
    if category_id and not Category.objects.filter(id=category_id, catalog=catalog).exists():
        messages.error(request, "دسته‌بندی نامعتبر است یا به شما تعلق ندارد.")
        return redirect(referer_url)

    data = request.data.copy()
    
    # ------------------ مدیریت تصویر با استفاده از utils ------------------
    try:
        image_file = process_base64_image(data.get('cropped_image_base64'), prefix="item")
        if image_file:
            data['image'] = image_file
    except ValueError as e:
        messages.error(request, str(e))
        return redirect(referer_url)
    # ----------------------------------------------------------------------

    serializer = ItemSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save()
        messages.success(request, "آیتم با موفقیت ایجاد شد.")
    else:
        for field, errors in serializer.errors.items():
            for error in errors:
                messages.error(request, f"خطا در {field}: {error}")
                
    return redirect(referer_url)


@api_view(['POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def item_edit(request, item_id):
    catalog = CatalogService.get_singleton_catalog(request.user)
    referer_url = request.META.get('HTTP_REFERER', 'dashboard_items_list')
    
    item = get_object_or_404(Item, id=item_id, category__catalog=catalog)

    new_category_id = request.data.get('category')
    if new_category_id and str(new_category_id) != str(item.category.id):
        if not Category.objects.filter(id=new_category_id, catalog=catalog).exists():
            messages.error(request, "دسته‌بندی جدید نامعتبر است.")
            return redirect(referer_url)

    data = request.data.copy()

    # ------------------ مدیریت تصویر با استفاده از utils ------------------
    try:
        image_file = process_base64_image(data.get('cropped_image_base64'), prefix="item")
        if image_file:
            data['image'] = image_file
    except ValueError as e:
        messages.error(request, str(e))
        return redirect(referer_url)
    # ----------------------------------------------------------------------

    serializer = ItemSerializer(item, data=data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        messages.success(request, "آیتم با موفقیت بروزرسانی شد.")
    else:
        for field, errors in serializer.errors.items():
            for error in errors:
                messages.error(request, f"خطا در {field}: {error}")
                
    return redirect(referer_url)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def item_delete(request, item_id):
    catalog = CatalogService.get_singleton_catalog(request.user)
    referer_url = request.META.get('HTTP_REFERER', 'dashboard_items_list')
    
    # پیدا کردن آیتم با شرط اینکه دسته‌بندی آن متعلق به کاتالوگ کاربر باشد
    item = get_object_or_404(Item, id=item_id, category__catalog=catalog)

    try:
        item_title = item.title
        item.delete()
        messages.success(request, f"آیتم '{item_title}' با موفقیت حذف شد.")
    except Exception as e:
        messages.error(request, f"خطا در حذف آیتم: {str(e)}")

    return redirect(referer_url)


def quick_catalog_create(request):
    if request.method == "POST":
        form = QuickCatalogForm(request.POST)
        if form.is_valid():
            catalog = form.save(commit=False)
            catalog.owner = request.user  # اختصاص مالک کاتالوگ
            # catalog.theme = 'tecof' # تم پیش‌فرض اعمال می‌شود
            catalog.save()
            return redirect('app_catalog_q_base', slug=catalog.slug)
    else:
        form = QuickCatalogForm()

    return render(request, 'your_template_path/quick_create.html', {'form': form})
