from django.template.loader import select_template
from django.template.exceptions import TemplateDoesNotExist

class ThemeEngine:
    """
    موتور مدیریت و مسیریابی تم‌های کاتالوگ
    """
    BASE_DIR = 'apps/wallpares'
    DEFAULT_THEME = 'tecof'

    @classmethod
    def resolve_template(cls, theme_key: str, page_name: str) -> str:
        """
        مسیر تمپلیت را بر اساس نام تم و نام صفحه پیدا می‌کند.
        """
        # فرض می‌کنیم page_name مقداری مثل 'website' یا 'menu' است
        target_file = f"{page_name}.html"
        
        template_candidates = [
            f"{cls.BASE_DIR}/{theme_key}/{target_file}",       # اولویت اول: تم انتخابی کاربر
            f"{cls.BASE_DIR}/{theme_key}/template.html",
            f"{cls.BASE_DIR}/{cls.DEFAULT_THEME}/{target_file}",
        ]
        print(template_candidates)
        try:
            template = select_template(template_candidates)
            return template.template.name
        except TemplateDoesNotExist:
            return cls.get_error_page(404)

    @classmethod
    def get_error_page(cls, error_code: int = 404) -> str:
        return f"{cls.BASE_DIR}/{error_code}.html"
