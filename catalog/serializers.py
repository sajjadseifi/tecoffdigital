from rest_framework import serializers
from .models import Category
from .models import Item
from .entities.qrcode_entity import CatalogQRCode

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'order', 'is_active','is_featured','is_important', 'image']
        read_only_fields = ['id']

from rest_framework import serializers
from django.core.exceptions import ValidationError

class ItemSerializer(serializers.ModelSerializer):
    # ورودی‌ها (قابل ویرایش)
    stock = serializers.IntegerField(required=False, min_value=0)
    price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, min_value=0)
    discount_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, min_value=0)

    # خروجی‌های محاسبه‌شده (فقط خواندنی)
    has_discount = serializers.BooleanField(read_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Item
        fields = [
            'id',
            'category',
            'title',
            'slug',
            'sku',
            'image',
            'price',
            'discount_price',
            'stock',
            'is_available',
            'is_featured',
            'order',
            'description',

            # فیلدهای محاسبه‌شده
            'has_discount',
            'discount_amount',
            'discount_percent',
            'final_price',
        ]

    def validate(self, data):
        price = data.get('price')
        discount_price = data.get('discount_price')
        stock = data.get('stock')

        errors = {}

        # چک عدم ثبت discount_price بدون price
        if discount_price is not None and price is None:
            errors['price'] = "برای تعیین قیمت تخفیفی، وارد کردن قیمت اصلی الزامی است."

        # چک معتبر بودن تخفیف
        if price is not None and discount_price is not None:
            if discount_price > price:
                errors['discount_price'] = "قیمت با تخفیف نمی‌تواند از قیمت اصلی بیشتر باشد."

        # چک منفی نبودن موجودی
        if stock is not None and stock < 0:
            errors['stock'] = "موجودی نمی‌تواند کمتر از صفر باشد."

        if errors:
            raise serializers.ValidationError(errors)

        return data


class CatalogQRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogQRCode
        fields = ['id', 'title', 'target_url', 'is_active']
        read_only_fields = ['qr_image', 'scans_count', 'created_at']
