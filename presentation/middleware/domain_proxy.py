import httpx
import logging
from django.conf import settings
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.core.cache import cache

logger = logging.getLogger("domain_proxy")

# تنظیمات کش
CACHE_PREFIX = "domain_proxy"
CACHE_TTL = 60 * 10

# لیست مسیرها و پسوندهایی که نباید پروکسی شوند (Bypass)
BYPASS_PATHS = [
    "/media/",
    "/static/",
    "/api/",
    "/download/",
    "/files/",
    "/uploads/",
]

BYPASS_EXTENSIONS = (
    ".pdf", ".zip", ".rar", ".7z", ".mp4", ".mp3", 
    ".xlsx", ".csv", ".doc", ".docx", ".jpg", ".png"
)

# =========================================
# Model
# =========================================

class DomainRoute(models.Model):
    source = models.CharField(max_length=255, unique=True)
    destination = models.CharField(max_length=500)
    active = models.BooleanField(default=True)
    allow_forward = models.BooleanField(
        default=False,
        help_text="If enabled user may redirect to destination"
    )

    class Meta:
        db_table = "domain_routes"

    def __str__(self):
        return f"{self.source} -> {self.destination}"


# =========================================
# Manager
# =========================================

class DomainRouteManager:

    @staticmethod
    def normalize(host):
        if not host:
            return None
        return host.split(":")[0].lower()

    @staticmethod
    def cache_key(host):
        return f"{CACHE_PREFIX}:{host}"

    @classmethod
    def resolve(cls, host):
        host = cls.normalize(host)
        if not host:
            return None

        key = cls.cache_key(host)
        cached = cache.get(key)

        if cached is not None:
            return cached

        try:
            route = DomainRoute.objects.get(source=host, active=True)
            result = {
                "destination": route.destination,
                "allow_forward": route.allow_forward
            }
            cache.set(key, result, CACHE_TTL)
            return result
        except DomainRoute.DoesNotExist:
            cache.set(key, None, CACHE_TTL)
            return None


# =========================================
# Proxy Service
# =========================================

class DomainProxyService:

    # هدرهایی که نباید از مبدا به مقصد یا بالعکس منتقل شوند (Hop-by-hop headers)
    HOP_HEADERS = {
        "connection", "keep-alive", "proxy-authenticate", 
        "proxy-authorization", "te", "trailers", 
        "transfer-encoding", "upgrade", "host",
    }

    @staticmethod
    def build_target(destination, path):
        if destination.startswith("http"):
            base = destination.rstrip("/")
        else:
            base = "http://" + destination.rstrip("/")
        return base + path

    @staticmethod
    def should_bypass(path):
        """بررسی اینکه آیا این آدرس باید از سیستم پروکسی خارج شود یا خیر"""
        # چک کردن شروع مسیر
        for p in BYPASS_PATHS:
            if path.startswith(p):
                return True
        # چک کردن پسوند فایل
        if path.lower().endswith(BYPASS_EXTENSIONS):
            return True
        return False

    @staticmethod
    def proxy(request, destination):
        print("\n--- PROXYING REQUEST ---")
        
        url = DomainProxyService.build_target(destination, request.get_full_path())
        
        # آماده‌سازی هدرهای ارسالی به مقصد
        headers = {}
        EXCLUDED_REQUEST_HEADERS = {"host", "content-length", "connection"}
        
        for key, value in request.headers.items():
            if key.lower() not in EXCLUDED_REQUEST_HEADERS:
                headers[key] = value

        # ارسال درخواست به سرور مقصد
        try:
            # استفاده از stream=True برای جلوگیری از پر شدن رم در فایلهای بزرگ
            client = httpx.Client(follow_redirects=True, timeout=60.0)
            
            # در درخواستهای پروکسی، کل بدنه (body) باید منتقل شود
            proxied_response = client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=request.body if request.body else None,
            )

            # ساخت پاسخ به صورت Streaming برای پشتیبانی از دانلود
            django_response = StreamingHttpResponse(
                proxied_response.iter_bytes(),
                status=proxied_response.status_code
            )

            # کپی کردن هدرهای بازگشتی از مقصد به کاربر
            for k, v in proxied_response.headers.items():
                if k.lower() not in DomainProxyService.HOP_HEADERS:
                    django_response[k] = v

            print(f"[Proxy] Success: {url} ({proxied_response.status_code})")
            return django_response

        except Exception as e:
            logger.error(f"Proxy error: {str(e)}")
            return HttpResponse("Proxy Error", status=502)


# =========================================
# Middleware
# =========================================

class DomainProxyMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        print("[Middleware] DomainProxyMiddleware Loaded")

    def __call__(self, request):
        host = request.get_host()
        path = request.get_full_path()

        # 1. پیدا کردن مسیر بر اساس دامنه
        route = DomainRouteManager.resolve(host)

        # اگر دامنه در لیست ما نبود، درخواست عادی جنگو ادامه پیدا کند
        if not route:
            return self.get_response(request)

        # 2. بررسی سیستم Bypass (آیا فایل دانلودی است یا مسیر خاص؟)
        if DomainProxyService.should_bypass(path):
            print(f"[Middleware] Bypassing: {path}")
            return self.get_response(request)

        destination = route["destination"]
        allow_forward = route["allow_forward"]

        # 3. حالت Forward (اگر پارامتر forward=1 باشد و اجازه داشته باشیم)
        if allow_forward and request.GET.get("forward") == "1":
            target_url = DomainProxyService.build_target(destination, path)
            print(f"[Middleware] Forwarding to: {target_url}")
            return HttpResponseRedirect(target_url)

        # 4. حالت Proxy (پیش‌فرض)
        return DomainProxyService.proxy(request, destination)
