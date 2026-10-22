from django import forms
from .models import IconLibs

class IconLibsForm(forms.ModelForm):
    class Meta:
        model = IconLibs
        fields = ['name', 'display_name', 'icon_file', 'category', 'is_active']