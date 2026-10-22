# accounts/services.py

import random
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class AuthService:
    """
    سرویس مدیریت منطق احراز هویت (OTP و کاربر)
    """
    
    @staticmethod
    def request_otp(phone: str):
        """
        یک کد OTP تولید کرده، در کش ذخیره می‌کند و (مثلا) آن را ارسال می‌کند.
        """
        # تولید کد ۶ رقمی
        code = str(random.randint(100000, 999999))
        
        # کلید برای ذخیره در کش (مثلا: otp_09123456789)
        cache_key = f"otp_{phone}"
        
        # ذخیره کد در کش به مدت ۲ دقیقه (۱۲۰ ثانیه)
        cache.set(cache_key, code, timeout=120)
        
        # TODO: در اینجا باید کد را از طریق سرویس پیامک واقعی ارسال کنید
        # برای تست، کد را در کنسول نمایش می‌دهیم
        print(f"======> OTP for {phone} is: {code} <======")
        
        # return True
        return False

    @staticmethod
    def verify_otp(phone: str, code: str) :
        """
        کد OTP را بررسی کرده و در صورت صحت، کاربر را برمی‌گرداند.
        اگر کاربر وجود نداشته باشد، او را می‌سازد.
        """
        cache_key = f"otp_{phone}"
        stored_code = cache.get(cache_key)
        
        if not stored_code:
            raise ValidationError("کد تایید منقضی شده است. لطفا مجددا درخواست دهید.")
        
        if stored_code != code:
            raise ValidationError("کد وارد شده صحیح نیست.")
        
        # پس از تایید موفق، کد را از کش حذف می‌کنیم
        cache.delete(cache_key)
        
        # کاربر را پیدا کرده یا یک کاربر جدید می‌سازیم
        # استفاده از get_or_create تضمین می‌کند که کاربر تکراری ساخته نشود
        user, created = User.objects.get_or_create(phone=phone)
        
        return user

    @staticmethod
    def verify_password(phone: str, password: str) :
        """
        رمز عبور کاربر را بررسی کرده و در صورت صحت، او را برمی‌گرداند.
        """
        try:
            user = User.objects.get(phone=phone)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass # اگر کاربر وجود نداشت، چیزی برنمی‌گردانیم
        
        raise ValidationError("شماره موبایل یا رمز عبور اشتباه است.")
