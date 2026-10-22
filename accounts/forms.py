from django import forms
from django.contrib import admin
from .models import User
# 1. فرم سفارشی برای ایجاد کاربر جدید
class CustomUserAddForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")

    class Meta:
        model = User
        fields = ("phone", "password", "first_name", "last_name", "is_active", "is_staff")

    def save(self, commit=True):
        # این متد رمز عبور را پیش از ذخیره در دیتابیس به درستی هش می‌کند
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
