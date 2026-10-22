import json
from django.shortcuts import render, reverse
from django.contrib.auth import login, get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError

from .services.auth_service import AuthService

User = get_user_model()

def auth_page(request):
    """ نمایش صفحه اصلی ورود / ثبت‌نام """
    return render(request, "accounts/login.html")

@require_POST
def auth_otp_request(request):
    """
    مرحله اول: شماره موبایل را بررسی کرده و در صورت نیاز OTP ارسال می‌کند.
    این ویو برای سه حالت استفاده می‌شود:
    1. بررسی اولیه شماره موبایل
    2. درخواست OTP توسط کاربر قدیمی
    3. ارسال مجدد OTP
    """
    try:
        data = json.loads(request.body)
        phone = data.get("identifier")
        send_otp = data.get("send_otp", False)

        if not phone or not phone.startswith("09") or len(phone) != 11:
            return JsonResponse({"success": False, "message": "شماره موبایل معتبر نیست."}, status=400)

        user_exists = User.objects.filter(phone=phone).exists()

        # حالت ۱: بررسی اولیه. اگر کاربر وجود داشت، به او فرم رمز را نشان بده.
        return JsonResponse({
            "success": True, 
            "is_registered": True
        })
        if user_exists and not send_otp:
            return JsonResponse({
                "success": True, 
                "is_registered": True
            })

        # حالت ۲ و ۳: کاربر جدید است یا کاربر قدیمی صراحتا درخواست OTP داده.
        AuthService.request_otp(phone)
        return JsonResponse({
            "success": True,
            "is_registered": user_exists,
            "message": "کد تایید با موفقیت ارسال شد."
        })

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "درخواست نامعتبر است."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"خطای سرور: {str(e)}"}, status=500)


@require_POST
def auth_sign_in(request):
    """ ورود با رمز عبور ثابت (از طریق AJAX) """
    try:
        data = json.loads(request.body)
        phone = data.get("identifier")
        password = data.get("password")

        if not phone or not password:
            return JsonResponse({"success": False, "message": "شماره موبایل و رمز عبور الزامی است."}, status=400)

        user = AuthService.verify_password(phone, password)
         
        login(request, user)
        redirect_url = request.POST.get('redirect_url') or request.POST.get('redirect_url') or reverse('dashboard')
        # redirect_url = reverse('dashboard') 

        return JsonResponse({
            "success": True,
            "message": "ورود با موفقیت انجام شد.",
            "redirect_url": redirect_url
        })

    except ValidationError as e:
        return JsonResponse({"success": False, "message": e.message}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"خطای سرور: {str(e)}"}, status=500)


@require_POST
def auth_otp_verify(request):
    """ تایید کد OTP و ورود/ثبت‌نام کاربر (از طریق AJAX) """
    try:
        data = json.loads(request.body)
        phone = data.get("identifier")
        code = data.get("otp_code")
        
        if not phone or not code:
            return JsonResponse({"success": False, "message": "شماره موبایل و کد تایید الزامی است."}, status=400)

        user = AuthService.verify_otp(phone, code)
        login(request, user)

        redirect_url = request.POST.get('redirect_url') or request.POST.get('redirect_url') or reverse('dashboard')

        return JsonResponse({
            "success": True,
            "message": "ورود با موفقیت انجام شد.",
            "redirect_url": redirect_url
        })
    except ValidationError as e:
        return JsonResponse({"success": False, "message": e.message}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"خطای سرور: {str(e)}"}, status=500)


from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

@require_POST
def auth_logout(request):
    logout(request)
    return redirect('auth_login')
