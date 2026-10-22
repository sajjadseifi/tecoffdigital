import random
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from accounts.models import OTP
from accounts.services.sms_service import SMSService


class OTPService:

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))

    @staticmethod
    def check_rate_limit(phone):

        last_otp = OTP.objects.filter(phone=phone).first()

        if not last_otp:
            return True

        diff = (timezone.now() - last_otp.created_at).total_seconds()

        if diff < getattr(settings, "OTP_RATE_LIMIT", 60):
            return False

        return True

    @staticmethod
    def create_otp(phone):

        if not OTPService.check_rate_limit(phone):
            raise Exception("لطفا کمی صبر کنید")

        code = OTPService.generate_code()

        otp = OTP.objects.create(
            phone=phone,
            code=code,
            expires_at=timezone.now() + timedelta(
                minutes=getattr(settings, "OTP_EXPIRE_MINUTES", 2)
            )
        )

        SMSService.send_otp(phone, code)

        return otp

    @staticmethod
    def verify_otp(phone, code):

        otp = OTP.objects.filter(
            phone=phone,
            code=code,
            is_used=False
        ).first()

        if not otp:
            raise Exception("کد اشتباه است")

        if otp.is_expired():
            raise Exception("کد منقضی شده است")

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        return otp
