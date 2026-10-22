from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from ..entities import TQRCode, TQRAnalysitic, TQREventLog

def get_client_ip(request):
    """تابع کمکی برای گرفتن IP کاربر"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def tqrs_index(request):
    context = {'system_status': 'ONLINE', 'version': '1.0.0-beta'}
    return render(request, "engine/tqrs/tqrs_index.html", context, status=200)

def tqrs_root(request):
    context = {}
    return render(request, "engine/tqrs/tqrs_root.html", context, status=200)

def tqrs_about(request):
    context = {}
    return render(request, "engine/tqrs/tqrs_about.html", context, status=200)

def tqrs_contact(request):
    context = {}
    return render(request, "engine/tqrs/tqrs_contact.html", context, status=200)


# ==========================================
# 1. API بررسی وضعیت و هدایت (Protocol Check)
# ==========================================
@require_http_methods(["GET"])
def tqrs_protocol_check_api(request, hash_qrcode):
    """
    این API توسط PWA یا کلاینت برای گرفتن آدرس مقصد صدا زده می‌شود.
    ثبت اسکن موفق هم در اینجا یا در مرحله ریدایرکت انجام می‌شود.
    """
    try:
        # جستجو بر اساس short_code
        tqr = TQRCode.objects.get(short_code=hash_qrcode, is_active=True)
        
        # ثبت لاگ موفقیت آمیز به صورت اولیه (می‌توانید بهینه تر کنید یا به celery بسپارید)
        analytics, created = TQRAnalysitic.objects.get_or_create(qr_code=tqr)
        
        # آپدیت آمار
        analytics.total_scans += 1
        analytics.last_scanned_at = timezone.now()
        analytics.save()

        # ثبت رویداد
        TQREventLog.objects.create(
            analytics=analytics,
            event_type='scan_success',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'method': 'api_check'}
        )

        return JsonResponse({
            'status': 'success',
            'destination_url': tqr.target_url,
            'qr_title': tqr.title
        }, status=200)

    except TQRCode.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': f'کد اسکن شده ({hash_qrcode}) در سیستم یافت نشد، منقضی شده یا غیرفعال است.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'خطای داخلی سرور هنگام پردازش کد.'
        }, status=500)


# ==========================================
# 2. ریدایرکت مستقیم (برای اسکن مستقیم با دوربین گوشی)
# ==========================================
def tqrs_protocol(request, hash_qrcode):
    """
    این ویو زمانی صدا زده می‌شود که کاربر مستقیماً لینک TQRS را باز کند
    مثال: https://tecoff.com/tqrs/TECQR
    """
    try:
        tqr = TQRCode.objects.get(short_code=hash_qrcode, is_active=True)
        
        analytics, created = TQRAnalysitic.objects.get_or_create(qr_code=tqr)
        analytics.total_scans += 1
        analytics.last_scanned_at = timezone.now()
        analytics.save()

        TQREventLog.objects.create(
            analytics=analytics,
            event_type='scan_success',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'method': 'direct_redirect'}
        )

        # اگر صفحه واسط (پروتکل) دارید که با JS ریدایرکت میکند، رندر کنید:
        # context = {'hash_qrcode': hash_qrcode, 'target_url': tqr.target_url}
        # return render(request, "engine/tqrs/tqrs_protocol.html", context, status=200)

        # در غیر این صورت مستقیماً ریدایرکت کنید:
        return HttpResponseRedirect(tqr.target_url)

    except TQRCode.DoesNotExist:
        # رندر صفحه خطای یافت نشد
        context = {'hash_qrcode': hash_qrcode, 'error': 'QR Code Not Found'}
        return render(request, "engine/tqrs/tqrs_protocol.html", context, status=404)


# ==========================================
# 3. API دریافت گزارش خطای کلاینت (Event Based Endpoint)
# ==========================================
@csrf_exempt
@require_http_methods(["POST"])
def tqrs_report_error_api(request):
    """
    کلاینت (مثل اپلیکیشن اسکنر) اگر در شناسایی کد مشکل داشت 
    یا تایم‌اوت شد، به این API دیتا می‌فرستد.
    """
    try:
        data = json.loads(request.body)
        short_code = data.get('short_code')
        error_type = data.get('error_type') # scan_failed, timeout, etc.
        details = data.get('details', {})

        if not short_code or not error_type:
            return JsonResponse({'error': 'short_code and error_type are required'}, status=400)

        tqr = TQRCode.objects.filter(short_code=short_code).first()
        if not tqr:
            return JsonResponse({'error': 'QR Code not found'}, status=404)

        analytics, created = TQRAnalysitic.objects.get_or_create(qr_code=tqr)
        
        # ثبت رویداد خطا
        TQREventLog.objects.create(
            analytics=analytics,
            event_type=error_type,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details=details
        )

        # آپدیت وضعیت در Analysitic
        analytics.last_error_detected_at = timezone.now()
        if error_type == 'scan_failed':
            analytics.is_damaged = True
        
        # محاسبه مجدد ضریب خطا (به صورت ساده)
        total_events = TQREventLog.objects.filter(analytics=analytics).count()
        failed_events = TQREventLog.objects.filter(
            analytics=analytics, 
            event_type__in=['scan_failed', 'link_broken', 'timeout']
        ).count()
        
        analytics.calculate_error_rate(failed_events, total_events)
        analytics.save()

        return JsonResponse({'status': 'reported successfully'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def qrcode_genarate_api(request):
    pass