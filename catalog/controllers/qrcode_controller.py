from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from ..entities import CatalogQRCode # حتما مدل را ایمپورت کنید
from ..serializers import CatalogQRCodeSerializer # حتما سریالایزر را ایمپورت کنید
from catalog.services.catalog_service import CatalogService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def qrcode_create(request):
    """اکشن ایجاد کیوآر کد جدید"""
    catalog = CatalogService.get_singleton_catalog(request.user)
    referer_url = request.META.get('HTTP_REFERER', 'dashboard_qrcodes_list') # مسیر پیش‌فرض را به لیست QRها تغییر دهید

    if not catalog:
        messages.error(request, "کاتالوگی یافت نشد.")
        return redirect(referer_url)

    data = request.data.copy()

    serializer = CatalogQRCodeSerializer(data=data)

    if serializer.is_valid():
        # متد save در مدل، خودش تصویر qr_image را می‌سازد
        serializer.save(catalog=catalog)
        messages.success(request, "کیوآر کد با موفقیت ایجاد شد.")
        return redirect(referer_url)

    for field, errors in serializer.errors.items():
        for error in errors:
            messages.error(request, f"خطا در {field}: {error}")

    return redirect(referer_url)


@api_view(['POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def qrcode_edit(request, qrcode_id):
    """اکشن ویرایش کیوآر کد"""
    catalog = CatalogService.get_singleton_catalog(request.user)
    referer_url = request.META.get('HTTP_REFERER', 'dashboard_qrcodes_list')
    
    qrcode_obj = get_object_or_404(CatalogQRCode, id=qrcode_id, catalog=catalog)

    data = request.data.copy()
    
    # بررسی می‌کنیم که آیا لینک تغییر کرده است یا خیر
    old_url = qrcode_obj.target_url

    serializer = CatalogQRCodeSerializer(qrcode_obj, data=data, partial=True)

    if serializer.is_valid():
        updated_qrcode = serializer.save()
        
        # اگر لینک مقصد تغییر کرد، باید تصویر QR قبلی حذف و تصویر جدید ساخته شود
        new_url = updated_qrcode.target_url
        if old_url != new_url:
            if updated_qrcode.qr_image:
                updated_qrcode.qr_image.delete(save=False) # حذف عکس قدیمی از هاست
            updated_qrcode.generate_qr_code() # متدی که در مدل نوشتیم
            updated_qrcode.save() # ذخیره مجدد با عکس جدید

        messages.success(request, "کیوآر کد با موفقیت بروزرسانی شد.")
        return redirect(referer_url)

    for field, errors in serializer.errors.items():
        for error in errors:
            messages.error(request, f"خطا در {field}: {error}")

    return redirect(referer_url)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def qrcode_delete(request, qrcode_id):
    """اکشن حذف کیوآر کد"""
    catalog = CatalogService.get_singleton_catalog(request.user)
    referer_url = request.META.get('HTTP_REFERER', 'dashboard_qrcodes_list')
    
    qrcode_obj = get_object_or_404(CatalogQRCode, id=qrcode_id, catalog=catalog)

    try:
        qr_title = qrcode_obj.title or "بدون عنوان"
        
        # حذف تصویر از روی هاست هنگام پاک کردن رکورد
        if qrcode_obj.qr_image:
            qrcode_obj.qr_image.delete(save=False)
            
        qrcode_obj.delete()
        messages.success(request, f"کیوآر کد '{qr_title}' با موفقیت حذف شد.")
    except Exception as e:
        messages.error(request, f"خطا در حذف کیوآر کد: {str(e)}")

    return redirect(referer_url)

import qrcode
from io import BytesIO
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes


@api_view(['POST'])
@permission_classes([AllowAny])
def qrcode_genarate_api(request):

    data = request.data
    link = data.get('text')

    if not link:
        return HttpResponse("text is required", status=400)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer, content_type="image/png")
