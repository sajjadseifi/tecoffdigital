WALLPAPERS_CONFIG = [
    {
        "key": "tecof",
        "name": "تکوف (پایه)",
        "description": "طراحی مینیمال، استاندارد و جامع مناسب برای انواع فروشگاه‌ها",
        "file_path": "wallpapers/tecof.html",
        "business_name": "تکوف شاپ",
        "business_logo": "🛍️",
        "items": ["هدفون بلوتوثی", "ساعت هوشمند پرو", "پاوربانک فست‌شارژ"]
    },
    {
        "key": "board",
        "name": "منوی تخته‌ای (کافه)",
        "description": "نمایش خطی و کلاسیک آیتم‌ها با خط‌چین (نام --- قیمت)، همراه با ۴ بافت مختلف (تخته سیاه، وایت‌برد، چوبی و سنگی)",
        "file_path": "wallpapers/board.html",
        "business_name": "کافه نوستالژی",
        "business_logo": "☕",
        "items": [
            "اسپرسو دبل", 
            "کاپوچینو", 
            "آیس لاته", 
            "کیک هویج و گردو", 
            "چای ماسالا", 
            "شیک نوتلا"
        ]
    },
    {
        "key": "horizontal",
        "name": "افقی (اسلایدی)",
        "description": "نمایش دسته‌بندی‌ها و محصولات به صورت اسکرول افقی با تمرکز بر تصاویر",
        "file_path": "wallpapers/horizontal.html",
        "business_name": "کافه باریستا",
        "business_logo": "☕", # مسیر فایل استاتیک هم قابل استفاده است: "/static/images/cafe.png"
        "items": ["قهوه‌های گرم", "نوشیدنی‌های سرد", "کیک و دسر", "اسموتی و شیک", "منوی صبحانه"]
    },
    {
        "key": "vertical",
        "name": "عمودی (لیستی)",
        "description": "نمایش کلاسیک و زیر هم آیتم‌ها، خوانا و مناسب برای منوی خدمات",
        "file_path": "wallpapers/vertical.html",
        "business_name": "خدمات کارواش درخشان",
        "business_logo": "🚗",
        "items": [
            "روشویی ساده با فوم", 
            "توشویی و جاروبرقی", 
            "موتورشویی با بخار", 
            "پولیش و واکس بدنه", 
            "صفرشویی کامل (VIP)"
        ]
    },
    {
        "key": "accordion",
        "name": "درختی (آکاردئون)",
        "description": "دسته‌بندی‌های بازشونده، مناسب برای فروشگاه‌های دارای زیرمجموعه",
        "file_path": "wallpapers/accordion.html",
        "business_name": "تکوف دیجیتال",
        "business_logo": "💻",
        "items": [
            {"name": "کالای دیجیتال", "sub_items": ["گوشی موبایل", "لپ‌تاپ و اولترابوک", "ساعت هوشمند"]},
            {"name": "لوازم جانبی", "sub_items": ["کاور و گلس", "هندزفری و هدفون", "پاوربانک"]},
            {"name": "قطعات کامپیوتر", "sub_items": ["کارت گرافیک", "مادربرد", "حافظه SSD"]}
        ]
    },
    {
        "key": "grid",
        "name": "شبکه‌ای (کارت‌های گرید)",
        "description": "نمایش شبکه‌ای محصولات، ایده‌آل برای رستوران‌ها و فست‌فودها",
        "file_path": "wallpapers/grid.html",
        "business_name": "فست‌فود برگرلند",
        "business_logo": "🍔",
        "items": ["چیزبرگر ویژه", "پیتزا پپرونی", "سیب‌زمینی پنیری", "سالاد سزار", "مرغ سوخاری", "نوشابه قوطی"]
    },
    {
        "key": "tabs",
        "name": "تب‌بندی (سربرگ‌دار)",
        "description": "جابجایی سریع بین دسته‌بندی‌های اصلی از طریق تب‌های بالای صفحه",
        "file_path": "wallpapers/tabs.html",
        "business_name": "بوتیک پوشاک شیک‌پوش",
        "business_logo": "👗",
        "tabs": [
            {"title": "مردانه", "content": ["پیراهن کلاسیک", "تی‌شرت اسپرت", "شلوار جین کتونی"]},
            {"title": "زنانه", "content": ["مانتو مجلسی", "شال و روسری نخی", "شومیز طرح‌دار"]},
            {"title": "بچه‌گانه", "content": ["ست نوزادی", "کفش بچه‌گانه"]}
        ]
    },
    {
        "key": "sidebar",
        "name": "سایدبار (منوی کناری)",
        "description": "دسترسی دائم به دسته‌بندی‌ها از طریق منوی ثابت در کناره‌ی تصویر",
        "file_path": "wallpapers/sidebar.html",
        "business_name": "سالن زیبایی گل‌رخ",
        "business_logo": "✂️",
        "menu_groups": [
            {"title": "خدمات مو", "items": ["کوتاهی و براشینگ", "رنگ و لایت", "کراتین و احیا"]},
            {"title": "خدمات ناخن", "items": ["کاشت پودر", "ترمیم و ژلیش", "مانیکور و پدیکور"]},
            {"title": "مراقبت پوست", "items": ["فیشیال تخصصی", "پاکسازی عمیق"]}
        ]
    }
]


def get_template_by_key(template_key):
    for item in WALLPAPERS_CONFIG:
        if item["key"] == template_key:
            return item

    return None