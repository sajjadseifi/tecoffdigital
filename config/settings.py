from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# 1. CORE SETTINGS
# ==========================================
# در حالت DEBUG=False، فقط همین آدرس‌ها اجازه دسترسی دارند
DEBUG = True
 # در زمان توسعه روی سیستم خودتان این را True کنید
SECRET_KEY = "django-insecure-b1(#(h5&icxeet^%59tbdi2jd5pl)i3t!9b9-w1#og#+clzuj1"

# ==========================================
# 4. SECURITY & CSRF
# ==========================================
SESSION_COOKIE_SECURE = False # اگر دامنه شما کاملا HTTPS است، این را True کنید
CSRF_COOKIE_SECURE = False    # اگر دامنه شما کاملا HTTPS است، این را True کنید

# ==========================================
# 2. PROXY & DOMAIN SETTINGS (بسیار مهم برای رفع مشکل دامنه)
# ==========================================
# وقتی سایت روی IIS یا Nginx است، این تنظیمات به جنگو می‌فهماند 
# که دامنه اصلی چیست و لینک‌های استاتیک و مدیا را با دامنه بسازد، نه با IP داخلی
# USE_X_FORWARDED_HOST = False
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ["*"]


CSRF_TRUSTED_ORIGINS = [
    "http://*",
    "https://*",
]

# ==========================================
# 3. APPS & MIDDLEWARE
# ==========================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic", # توصیه می‌شود برای وایت‌نویز اضافه شود
    "django.contrib.staticfiles",
    "phonenumber_field",
    "accounts",
    "website",
    "catalog",
    "dashboard",
    "game",
    'presentation'
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    'presentation.middleware.domain_proxy.DomainProxyMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    'catalog.middlewares.catalog_middleware.ActiveCatalogMiddleware',
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]




# ==========================================
# 5. TEMPLATES & URLS & DB
# ==========================================
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
ALLOW_UNICODE_SLUGS = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'catalog.contexts.context_processors.user_catalog_context',
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ==========================================
# 6. INTERNATIONALIZATION (I18N)
# ==========================================
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# ==========================================
# 7. STATIC & MEDIA FILES
# ==========================================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "assets"]
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ==========================================
# 8. THIRD-PARTY & CUSTOM SETTINGS
# ==========================================
PHONENUMBER_DEFAULT_REGION = "IR"
PHONENUMBER_DB_FORMAT = "E164"

SMSIR_API_KEY = "e8xDOAOGzs0UPWfr83oK6ImbixjexdhDgdUsaHWM7qIOefP1"
SMSIR_BASE_URL = "https://api.sms.ir/v1"
SMSIR_LINE_NUMBER = "30002108019523"
SMSIR_VERIFY_TEMPLATE = 893549
OTP_EXPIRE_SECONDS = 120
OTP_RATE_LIMIT = 60

# settings.py

AUTH_PASSWORD_VALIDATORS = [
    {
        # فقط بررسی می‌کند که رمز عبور حداقل چند کاراکتر باشد
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4, # مثلا حداقل 4 کاراکتر
        }
    },
]
