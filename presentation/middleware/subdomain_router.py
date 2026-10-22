import re
from django.conf import settings
# from django.shortcuts import redirect # اگر redirect لازم نیست، این را حذف کنید
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404 # اگر redirect لازم نیست، اینها را حذف کنید
# from django.middleware.common import CommonMiddleware # برای دسترسی به host parsing - این خط معمولا نیاز نیست

# --- مدل‌های لازم ---
try:
    # فرض می‌کنیم DomainToPath (یا DomainMapping) و Catalog در app 'catalog' قرار دارند
    # مسیر import را با توجه به ساختار پروژه خودتان تنظیم کنید
    from catalog.models import DomainToPath
except ImportError:
    Catalog = None
    DomainToPath = None
# --------------------

class SubdomainRouterMiddleware: # نام middleware تغییر یافت
    """
    این Middleware هاست را تشخیص داده و اطلاعات مربوط به catalog_slug و page_name را
    به request اضافه می‌کند. همچنین می‌تواند بر اساس نگاشت‌ها redirect کند.
    """

    # نگاشت ساب‌دامین‌ها به پیشوندهای URL و catalog_slug پیش‌فرض
    # key: ساب‌دامین, value: tuple (path_prefix, default_catalog_slug)
    SUBDOMAIN_CONFIG = {
        "qr": ("/tqrs/", "qr"),
        "app": ("/teapp/", "app"),
        "teapp": ("/teapp/", "app"),
        "grootapp": ("/teapp/", "app"),
        "api": ("/api/", "api"),
        "mamut": ("/", "mamut"), # صفحه اصلی
        "panel": ("/dashboard/", "panel"),
    }

    RESERVED_HOSTS = [] # getattr(settings, 'RESERVED_HOSTS', []) # اگر در settings تعریف شده

    def __init__(self, get_response):
        self.get_response = get_response

    def _is_ip_address(self, host):
        """چک می‌کند که آیا هاست یک آدرس IP است."""
        # این regex ساده است و ممکن است تمام IP های معتبر را پوشش ندهد، اما برای اکثر موارد کافی است.
        return re.match(r'^(\d{1,3}\.){3}\d{1,3}$', host)

    def _extract_host_parts(self, host):
        """
        استخراج ساب‌دامین، دامنه اصلی، و TLD از هاست.
        برمی‌گرداند: (subdomain, main_domain, tld)
        """
        host_without_port = host.split(":")[0] # حذف پورت اگر وجود داشت

        if self._is_ip_address(host_without_port):
            return None, host_without_port, None # subdomain, main_domain (IP), tld

        parts = host_without_port.split(".")

        # localhost case (e.g., qr.localhost)
        if len(parts) == 2 and parts[1] == "localhost":
            return parts[0], host_without_port, "localhost"

        # standard case (e.g., qr.tecof.digital) - حداقل 3 بخش (subdomain.domain.tld)
        if len(parts) >= 3:
            subdomain = parts[0]
            main_domain = ".".join(parts[1:]) # بقیه بخش‌ها دامنه اصلی + TLD
            return subdomain, main_domain, parts[-1] # TLD آخرین بخش است

        # case for root domain (e.g., tecof.digital) - فقط 2 بخش
        if len(parts) == 2:
            return None, host_without_port, parts[1] # subdomain نداریم

        # اگر فرمت ناشناخته بود
        return None, host_without_port, None

    def _resolve_catalog_info(self, host, subdomain, main_domain, tld):
        """
        منطق اصلی برای تعیین catalog_slug و page_name.
        اولویت: DomainToPath > SUBDOMAIN_CONFIG > دامنه اصلی / ساب‌دامین
        """
        catalog_slug = None
        page_name = None
        path_prefix = None

        # 1. بررسی نگاشت دامنه‌های سفارشی (DomainToPath)
        if DomainToPath:
            try:
                # فرض می‌کنیم مدل DomainToPath دارای فیلدهای: domain, is_active, catalog (ForeignKey to Catalog), path
                mapping = DomainToPath.objects.get(domain=host, is_active=True)
                # چک می‌کنیم که کاتالوگ مرتبط هم فعال باشد
                if mapping.catalog and mapping.catalog.is_active:
                    catalog_slug = mapping.catalog.slug
                    page_name = mapping.path # این می‌تواند خالی باشد (صفحه اصلی)
                    # اگر path خالی بود، page_name را None قرار می‌دهیم تا صفحه اصلی در نظر گرفته شود
                    if not page_name:
                        page_name = None
                    # نگاشت دامنه بالاترین اولویت را دارد، پس همینجا برمی‌گردانیم
                    return catalog_slug, page_name, None # path_prefix از DomainToPath نمی‌آید
            except DomainToPath.DoesNotExist:
                pass # اگر نگاشتی پیدا نشد، به مرحله بعد برو
            except Exception as e:
                # لاگ کردن خطا برای اشکال‌زدایی
                print(f"Error querying DomainToPath for {host}: {e}")

        # 2. بررسی ساب‌دامین‌ها از طریق SUBDOMAIN_CONFIG
        if subdomain and subdomain in self.SUBDOMAIN_CONFIG:
            path_prefix, default_catalog_slug = self.SUBDOMAIN_CONFIG[subdomain]
            # در اینجا، catalog_slug را از پیش‌تعریف شده در config می‌گیریم
            # اگر می‌خواهید خود ساب‌دامین، catalog_slug باشد، catalog_slug = subdomain را استفاده کنید
            catalog_slug = default_catalog_slug
            page_name = None # page_name در این حالت معمولا از مسیر اصلی درخواست استخراج می‌شود

            # اگر path_prefix خالی "/" باشد و catalog_slug هم "mamut" باشد (مثال شما)
            # یعنی این ساب‌دامین به صفحه اصلی مربوط است
            if path_prefix == "/" and catalog_slug == "mamut":
                page_name = None # اطمینان از اینکه صفحه اصلی است

            return catalog_slug, page_name, path_prefix

        # 3. اگر ساب‌دامین بود ولی در SUBDOMAIN_CONFIG نبود
        # به طور پیش‌فرض، از خود ساب‌دامین به عنوان catalog_slug استفاده می‌کنیم
        if not catalog_slug and subdomain:
            catalog_slug = subdomain
            page_name = None # صفحه اصلی
            path_prefix = None # پیشوند مسیر ندارد
            # return catalog_slug, page_name, path_prefix # اگر این رفتار را ترجیح می‌دهید، اینجا return کنید

        # 4. اگر ساب‌دامین نداشتیم (یا مرحله 3 را return نکردیم)، از دامنه اصلی استفاده کن
        # این قسمت برای زمانی است که فقط دامنه اصلی (مثلا example.com) یا IP را داریم
        elif not catalog_slug and main_domain and tld and not self._is_ip_address(main_domain):
            # اولین بخش دامنه اصلی را به عنوان potential_slug در نظر می‌گیریم
            potential_slug = main_domain.split('.')[0]

            # **تغییر مهم برای تست لوکال**:
            # اگر می‌خواهید بدون نیاز به وجود Catalog در دیتابیس، فقط نام دامنه را به عنوان slug استفاده کنید:
            if potential_slug:
                catalog_slug = potential_slug
                page_name = None
                path_prefix = None
                # return catalog_slug, page_name, path_prefix # اگر این رفتار را ترجیح می‌دهید، اینجا return کنید

            # **یا اگر همچنان می‌خواهید وجود Catalog فعال را چک کنید (کد قبلی شما):**
            # elif Catalog and potential_slug:
            #     try:
            #         catalog = Catalog.objects.get(slug=potential_slug, is_active=True)
            #         catalog_slug = catalog.slug
            #         page_name = None
            #         path_prefix = None
            #         # return catalog_slug, page_name, path_prefix
            #     except Catalog.DoesNotExist:
            #         pass # کاتالوگ فعال با این اسلاگ پیدا نشد
            #     except Exception as e:
            #         print(f"Error querying Catalog for slug {potential_slug}: {e}")

        # در نهایت، مقادیر نهایی را برمی‌گردانیم
        return catalog_slug, page_name, path_prefix

    def __call__(self, request):
        host = request.get_host()
        subdomain, main_domain, tld = self._extract_host_parts(host)

        # ذخیره اطلاعات هاست استخراج شده در request برای استفاده‌های بعدی
        request.original_host = host
        request.subdomain = subdomain
        request.main_domain = main_domain
        request.tld = tld
        request.catalog_slug = None # مقدار اولیه
        request.page_name = None    # مقدار اولیه
        request.path_prefix = None  # مقدار اولیه

        # اگر هاست جزو دامنه‌های رزرو شده بود (در حالت لوکال معمولا خالی است)
        # یا اگر IP بود، پردازش را متوقف کرده و به middleware بعدی می‌رویم.
        if host in self.RESERVED_HOSTS or (subdomain and subdomain in self.RESERVED_HOSTS) or self._is_ip_address(main_domain):
            # اگر IP بود، ممکن است بخواهیم مسیر را به صورت عادی پردازش کنیم
            # یا به یک صفحه خاص هدایت کنیم. فعلا فقط ادامه می‌دهیم.
            response = self.get_response(request)
            return response

        # استخراج اطلاعات کاتالوگ و مسیر با استفاده از تابع کمکی
        catalog_slug, page_name, path_prefix = self._resolve_catalog_info(host, subdomain, main_domain, tld)

        # تنظیم attribute های request با مقادیر استخراج شده
        request.catalog_slug = catalog_slug
        request.page_name = page_name
        request.path_prefix = path_prefix

        # ----- منطق تغییر مسیر (Path Resolution / Redirect) -----
        # این بخش برای تست لوکال می‌تواند فعال یا غیرفعال باشد.
        # اگر فقط می‌خواهید اطلاعات را استخراج کنید، این بخش را حذف کنید.
        # اگر می‌خواهید رفتار redirect را هم تست کنید، آن را نگه دارید.

        current_path = request.path

        # اگر catalog_slug پیدا شد
        if catalog_slug:
            target_url = None
            # ساخت URL هدف بر اساس catalog_slug و page_name
            if page_name: # اگر صفحه خاصی مشخص شده بود (مثلاً از DomainToPath)
                try:
                    # استفاده از reverse برای ساخت URL امن (نیاز به تعریف URL pattern ها)
                    # فرض می‌کنیم URL pattern شما 'app_catalog_q' نام دارد
                    target_url = reverse('app_catalog_q', args=[catalog_slug, page_name])
                except Exception:
                    # اگر نام URL pattern پیدا نشد، مسیر را دستی بساز
                    target_url = f"/q/{catalog_slug}/{page_name}/"
            else: # اگر page_name خالی بود، صفحه اصلی کاتالوگ
                try:
                    # فرض می‌کنیم URL pattern برای صفحه اصلی 'app_catalog_q_base' نام دارد
                    target_url = reverse('app_catalog_q_base', args=[catalog_slug])
                except Exception:
                    target_url = f"/q/{catalog_slug}/"

            # اگر URL هدف پیدا شد و با مسیر فعلی متفاوت بود، redirect کن
            if target_url and current_path != target_url:
                # در اینجا شما تصمیم می‌گیرید که آیا path_prefix را هم لحاظ کنید یا نه
                # معمولا اگر catalog_slug از DomainToPath آمده، path_prefix اهمیت کمتری دارد
                # و redirect به target_url کفایت می‌کند.
                return HttpResponseRedirect(target_url)

            # اگر catalog_slug پیدا شد ولی target_url ساخته نشد (خطا در reverse)
            elif catalog_slug and not target_url:
                print(f"Warning: Could not reverse URL for catalog '{catalog_slug}', page '{page_name}'.")
                # می‌توانید به یک صفحه خطا هدایت کنید یا مسیر را دستی بسازید

        # اگر path_prefix از ساب‌دامین آمده بود و catalog_slug پیدا نشد (یا اولویت با path_prefix بود)
        # و مسیر فعلی با path_prefix شروع نمی‌شود.
        # این بخش مسیر را اصلاح می‌کند تا view ها بتوانند آن را درست پردازش کنند.
        if path_prefix and not request.path.startswith(path_prefix):
            # اطمینان حاصل کنید که request.path همیشه با '/' شروع می‌شود
            current_path_cleaned = request.path if request.path.startswith('/') else '/' + request.path
            request.path = path_prefix + current_path_cleaned.lstrip('/')

        # اجرای middleware بعدی یا view
        response = self.get_response(request)
        return response
