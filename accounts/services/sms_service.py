import requests
from django.conf import settings


class SMSService:

    BASE_URL = "https://api.sms.ir/v1/send/verify"

    @staticmethod
    def send_otp(phone, code):

        headers = {
            "Accept": "application/json",
            "X-API-KEY": settings.SMSIR_API_KEY,
            "Content-Type": "application/json",
        }

        payload = {
            "mobile": str(phone),
            "templateId": settings.SMSIR_VERIFY_TEMPLATE,
            "parameters": [{ "name": "CODE", "value": code }]
        }

        response = requests.post(SMSService.BASE_URL, json=payload, headers=headers)
        print(response.json())
        if response.status_code != 200:
            raise Exception("SMS service error")

        data = response.json()

        if data.get("status") != 1:
            raise Exception(data.get("message", "SMS sending failed"))

        return True
