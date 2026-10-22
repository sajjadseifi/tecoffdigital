/**
 * TECU MENU ENGINE
 * -----------------------------------------------
 * این ماژول اصلی سیستم منوی TECU است.
 *
 * TECU = Technology YOU
 * یعنی: «فناوری به سبک شما»
 *
 * هدف این فایل: مدیریت تمام رفتارهای منوی دیجیتال،
 * پویا، سفارشی، واکنش‌گرا، و قابل شخصی‌سازی برای هر کسب‌وکار.
 *
 * ساختار سیستم:
 *  - دریافت پیکربندی از Django Template (MENU_CONFIG)
 *  - مدیریت State بخش منو (دسته‌ها، آیتم‌ها، جستجو، سوایپ، لودینگ)
 *  - تعاملات UI بر پایه Alpine.js
 *  - بدون هیچ ارتباط HTML‌محور → 100% Reusable
 *
 * این فایل "هسته" (Core) موتور منوی TECU است.
 */

document.addEventListener('alpine:init', () => {

    Alpine.data('tecMenuApp', () => ({

        /* =====================================================
         * CONFIG (Injected from Django Template)
         * -----------------------------------------------------
         * MENU_CONFIG شامل:
         *  - لیست دسته‌ها (slug, title, image, count)
         *  - مسیر API جستجو
         *  - مسیر API دریافت آیتم‌های هر دسته
         *
         * این جدا‌سازی منطق از Backend یکی از اصول TECU است:
         *     «فرانت مستقل، بک‌اند انعطاف‌پذیر»
         * ===================================================== */
        config: window.MENU_CONFIG || {},


        /* =====================================================
         * STATE (وضعیت‌های فعال سیستم)
         * -----------------------------------------------------
         * در اینجا کل وضعیت UI مدیریت می‌شود.
         * هر تغییری در state، مستقیماً UI را به‌روزرسانی می‌کند.
         * این همان فلسفه reactive در TECU است.
         * ===================================================== */
        categories: [],         // دسته‌ها
        activeCategory: null,   // دسته باز شده فعلی
        items: [],              // آیتم‌های دسته انتخاب‌شده
        searchResults: [],      // نتایج جستجو
        searchQuery: '',        // متن جستجو
        isSearching: false,     // آیا در حالت جستجو هستیم؟
        isLoading: true,        // وضعیت لودینگ داده از API


        /* ----------------- Ripple Touch Effect ------------------
         * هدف: القای حس لمس واقعی موبایل، مانند اپلیکیشن‌های native
         * ------------------------------------------------------- */
        isRippling: false,
        rippleX: 0,
        rippleY: 0,
        rippleCatId: null,


        /* ----------------- Swipe Navigation ---------------------
         * این بخش امکان سوایپ بین دسته‌ها را فراهم می‌کند.
         * دقت سوایپ بسیار مهم است تا با اسکرول عمودی اشتباه نشود.
         * ------------------------------------------------------- */
        touchStartX: 0,
        touchStartY: 0,
        translateX: 0,
        isDragging: false,
        isSwipingX: null,
        hasSwiped: false,


        /* =====================================================
         * COMPUTED (مقادیر محاسباتی)
         * -----------------------------------------------------
         * همیشه بر اساس state محاسبه می‌شوند.
         * ===================================================== */
        get currentCategoryIndex() {
            return this.categories.findIndex(c => c.slug === this.activeCategory);
        },
        get hasNext() {
            return this.currentCategoryIndex < this.categories.length - 1;
        },
        get hasPrev() {
            return this.currentCategoryIndex > 0;
        },


        /* =====================================================
         * INIT (شروع موتور منوی TECU)
         * -----------------------------------------------------
         * با اولین load دسته اول را فعال می‌کنیم و آیتم‌هایش را می‌گیریم.
         * ===================================================== */
        init() {
            this.categories = this.config.categories || [];

            if (this.categories.length) {
                this.activeCategory = this.categories[0].slug;
                this.fetchItems(this.activeCategory);
            }
        },


        /* =====================================================
         * CATEGORY HANDLING (مدیریت دسته‌ها)
         * ===================================================== */
        selectCategory(slug) {
            // جلوگیری از درخواست بیهوده در صورت انتخاب دوباره
            if (this.activeCategory === slug && !this.isSearching) return;

            this.activeCategory = slug;
            this.fetchItems(slug);
            this.scrollToTop();
        },

        handleCatPress(e, slug) {
            // ثبت محل لمس برای ایجاد Ripple Effect
            const rect = e.target.getBoundingClientRect();
            const x = e.touches ? e.touches[0].clientX : e.clientX;
            const y = e.touches ? e.touches[0].clientY : e.clientY;

            this.rippleX = x - rect.left;
            this.rippleY = y - rect.top;
            this.rippleCatId = slug;

            // ریست انیمیشن و اجرا
            this.isRippling = false;
            this.$nextTick(() => this.isRippling = true);
        },


        /* =====================================================
         * SWIPE HANDLER (سوایپ بین دسته‌ها)
         * ===================================================== */
        onTouchStart(e) {
            if (this.isLoading) return;
            this.hasSwiped = true;

            this.touchStartX = e.touches[0].clientX;
            this.touchStartY = e.touches[0].clientY;
            this.isDragging = true;
            this.isSwipingX = null;
        },

        onTouchMove(e) {
            if (!this.isDragging) return;

            const dx = e.touches[0].clientX - this.touchStartX;
            const dy = e.touches[0].clientY - this.touchStartY;

            // تشخیص اینکه حرکت افقی است یا عمودی
            if (this.isSwipingX === null) {
                this.isSwipingX = Math.abs(dx) > Math.abs(dy);
            }

            if (!this.isSwipingX) return;

            e.preventDefault(); // جلوگیری از اسکرول عمودی
            this.translateX = dx * 0.9;
        },

        onTouchEnd() {
            if (!this.isDragging || !this.isSwipingX) {
                this.isDragging = false;
                return;
            }

            const threshold = window.innerWidth * 0.2;

            if (this.translateX > threshold && this.hasNext) {
                this.selectCategory(this.categories[this.currentCategoryIndex + 1].slug);
            }

            if (this.translateX < -threshold && this.hasPrev) {
                this.selectCategory(this.categories[this.currentCategoryIndex - 1].slug);
            }

            this.translateX = 0;
            this.isDragging = false;
        },


        /* =====================================================
         * DATA FETCHING (دریافت داده‌ها از API)
         * ===================================================== */

        async fetchItems(categorySlug) {
            this.isLoading = true;
            this.items = [];

            // تولید URL با slug دینامیکی دسته
            const url = this.config.itemsUrlTemplate.replace('__CAT__', categorySlug);

            try {
                const res = await fetch(url);
                this.items = await res.json();
            } catch (e) {
                console.error("TECU fetch error:", e);
            } finally {
                this.isLoading = false;
            }
        },

        async handleSearch() {
            const q = this.searchQuery.trim();

            if (!q) {
                // بازگشت از حالت جستجو
                this.isSearching = false;
                this.fetchItems(this.activeCategory);
                return;
            }

            this.isSearching = true;
            this.isLoading = true;

            try {
                const res = await fetch(`${this.config.searchUrl}?q=${encodeURIComponent(q)}`);
                this.searchResults = await res.json();
            } catch (e) {
                console.error("TECU search error:", e);
            } finally {
                this.isLoading = false;
            }
        },


        /* =====================================================
         * UTILITIES (ابزارهای کمکی)
         * ===================================================== */

        scrollToTop() {
            // اسکرول به ابتدای صفحه → تجربه اپلیکیشنی
            this.$root.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }));
});
