(function () {

    function wait() {
        if (typeof django === "undefined" || !django.jQuery) {
            return setTimeout(wait, 50);
        }

        const $ = django.jQuery;

        function slugify(text) {
            return text.toString().toLowerCase()
                .trim()
                .replace(/\s+/g, "-")
                .replace(/[^\p{Letter}\p{Number}\-]+/gu, "")
                .replace(/\-\-+/g, "-")
                .replace(/^-+/, "")
                .replace(/-+$/, "");
        }

        // وقتی کاربر slug را خودش تغییر داد
        $(document).on("input", 'input[name$="-slug"]', function () {
            $(this).data("manual-edit", true);
        });

        // وقتی title تغییر می‌کند
        $(document).on("input", 'input[name$="-title"]', function () {

            const titleInput = $(this);
            const row = titleInput.closest("tr");
            const slugInput = row.find('input[name$="-slug"]');

            // اگر کاربر slug را ویرایش نکرده باشد
            if (!slugInput.data("manual-edit")) {
                slugInput.val(slugify(titleInput.val()));
            }

        });

    }

    wait();

})();
