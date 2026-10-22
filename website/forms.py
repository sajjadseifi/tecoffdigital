# website/forms.py
from django import forms
from presentation.widgets import TailwindFormMixin, PersianFileWidget
from .models import WebsiteSettings, LandingSection, SectionItem

# -------------------------------------------------------------
# اعمال Mixin روی فرم‌ها (حذف کلاس‌های بوت‌استرپ و نگه داشتن ساختار)
# -------------------------------------------------------------

class WebsiteSettingsForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = WebsiteSettings
        fields = ['custom_domain', 'meta_title', 'meta_description', 'favicon', 'primary_color', 'is_published']
        widgets = {
            'custom_domain': forms.TextInput(attrs={'dir': 'ltr', 'placeholder': 'www.example.com'}),
            'meta_description': forms.Textarea(attrs={'rows': 3}),
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            # فیلدهای دیگر به صورت خودکار توسط Mixin مدیریت می‌شوند
        }

class LandingSectionForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = LandingSection
        fields = ['section_type', 'title', 'subtitle', 'image', 'order', 'is_active', 'config']
        widgets = {
            'subtitle': forms.Textarea(attrs={'rows': 2}),
            # config به صورت JSON است، از فونت monospace استفاده می‌کنیم تا خواناتر باشد
            'config': forms.Textarea(attrs={'rows': 4, 'dir': 'ltr', 'class': 'font-mono text-sm', 'placeholder': '{"key": "value"}'}),
        }

class SectionItemForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = SectionItem
        fields = ['title', 'description', 'icon', 'image', 'url', 'value', 'order', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'icon': forms.TextInput(attrs={'dir': 'ltr', 'placeholder': 'fas fa-star'}),
            'url': forms.URLInput(attrs={'dir': 'ltr', 'placeholder': 'https://...'}),
        }
