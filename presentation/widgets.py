from django import forms
from django.utils.safestring import mark_safe
import json


class LocationWidget(forms.Widget):
    template_name = 'presentation/widgets/location_widjet.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        
        # مقادیر پیش‌فرض (مثلاً مرکز تهران)
        lat = 35.6892
        lng = 51.3890
        
        if value:
            # اگر داده از دیتابیس بیاید (dict) یا از فرم (string)
            if isinstance(value, str):
                try:
                    val_dict = json.loads(value)
                    lat = val_dict.get('lat', lat)
                    lng = val_dict.get('lng', lng)
                except json.JSONDecodeError:
                    pass
            elif isinstance(value, dict):
                lat = value.get('lat', lat)
                lng = value.get('lng', lng)

        context['widget'].update({
            'lat_val': lat,
            'lng_val': lng,
        })
        return context

class WorkingHoursWidget(forms.Widget):
    template_name = 'presentation/widgets/working_hours_widget.html'

    def format_value(self, value):
        if isinstance(value, dict):
            return value
        if value:
            try:
                return json.loads(value)
            except Exception:
                return {}
        return {}

    def render(self, name, value, attrs=None, renderer=None):
        value = self.format_value(value)
        html = renderer.render(self.template_name, {'name': name, 'value': value})
        return mark_safe(html)


class FacilitiesWidget(forms.Widget):
    template_name = 'presentation/widgets/facilities_widget.html'
    
    def format_value(self, value):
        if isinstance(value, dict):
            return value
        if value:
            try:
                return json.loads(value)
            except Exception:
                return {}
        return {}

    def render(self, name, value, attrs=None, renderer=None):
        value = self.format_value(value)
        html = renderer.render(self.template_name, {'name': name, 'value': value})
        return mark_safe(html)

class PersianFileWidget(forms.ClearableFileInput):
    template_name = 'presentation/widgets/file_input.html'
    
    clear_checkbox_label = 'پاک کردن فایل'
    initial_text = 'فایل آپلود شده'
    input_text = 'آپلود فایل جدید'


class TailwindFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')

            if isinstance(field.widget, (forms.FileInput, forms.ClearableFileInput)):
                if not isinstance(field.widget, PersianFileWidget):
                    field.widget = PersianFileWidget(attrs=field.widget.attrs)
                field.widget.attrs['class'] = "hidden"
                continue

            elif isinstance(field.widget, forms.CheckboxInput):
                base_class = 'w-5 h-5 text-accent-600 bg-surface-50 border-surface-300 rounded focus:ring-accent-500 focus:ring-2 cursor-pointer transition-colors'

            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                base_class = 'w-full rounded-xl border border-surface-200 bg-surface-50 text-brand-900 focus:border-accent-500 focus:ring-1 focus:ring-accent-500 px-4 py-3 transition-colors cursor-pointer appearance-none'
            
            elif isinstance(field.widget, forms.Textarea):
                base_class = 'w-full rounded-xl border border-surface-200 bg-surface-50 text-brand-900 placeholder-brand-400 focus:border-accent-500 focus:ring-1 focus:ring-accent-500 px-4 py-3 transition-colors outline-none resize-y min-h-[60px]'
            
            elif getattr(field.widget, 'input_type', None) == 'color':
                base_class = 'h-14 w-full rounded-xl border border-surface-200 bg-surface-50 p-1 cursor-pointer focus:border-accent-500 focus:ring-1 focus:ring-accent-500 transition-colors'
            
            else:
                base_class = 'w-full rounded-xl border border-surface-200 bg-surface-50 text-brand-900 placeholder-brand-400 focus:border-accent-500 focus:ring-1 focus:ring-accent-500 px-4 py-3 transition-colors outline-none'
            
            field.widget.attrs['class'] = f"{base_class} {existing_classes}".strip()
            
            if not isinstance(field.widget, (forms.CheckboxInput, forms.Select, forms.SelectMultiple)):
                if getattr(field.widget, 'input_type', None) != 'color':
                    if not field.widget.attrs.get('placeholder'):
                        field.widget.attrs['placeholder'] = f"{field.label} را وارد کنید..."
