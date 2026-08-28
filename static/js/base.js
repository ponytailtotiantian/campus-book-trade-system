document.addEventListener("DOMContentLoaded", function () {
    const navCollapse = document.getElementById("mainNav");
    if (navCollapse && window.bootstrap) {
        navCollapse.addEventListener("click", function (event) {
            const target = event.target.closest("a.nav-link, a.btn");
            if (!target) {
                return;
            }
            const collapse = window.bootstrap.Collapse.getInstance(navCollapse);
            if (collapse && navCollapse.classList.contains("show")) {
                collapse.hide();
            }
        });
    }

    document.querySelectorAll("[data-auto-submit]").forEach(function (select) {
        select.addEventListener("change", function () {
            if (select.form && typeof select.form.requestSubmit === "function") {
                select.form.requestSubmit();
            }
        });
    });
});
