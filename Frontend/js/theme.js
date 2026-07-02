/* ==========================================================================
   ArmWork Theme Script
   Կառավարում է կայքի Light/Dark mode-ը բոլոր էջերում։
   Ֆայլը միացված է <head>-ում, որպեսզի dark mode-ը կիրառվի էջի բացման սկզբում։
   ========================================================================== */

(function () {
    const THEME_KEY = "theme";
    const DARK_CLASS = "dark-theme";
    const htmlEl = document.documentElement;

    function systemPrefersDark() {
        return window.matchMedia("(prefers-color-scheme: dark)").matches;
    }

    function applyInitialTheme() {
        const savedTheme = localStorage.getItem(THEME_KEY);

        if (savedTheme === "dark" || (!savedTheme && systemPrefersDark())) {
            htmlEl.classList.add(DARK_CLASS);
        }
    }

    function setTheme(theme) {
        if (theme === "dark") {
            htmlEl.classList.add(DARK_CLASS);
            localStorage.setItem(THEME_KEY, "dark");
            return;
        }

        htmlEl.classList.remove(DARK_CLASS);
        localStorage.setItem(THEME_KEY, "light");
    }

    function toggleTheme() {
        const nextTheme = htmlEl.classList.contains(DARK_CLASS) ? "light" : "dark";
        setTheme(nextTheme);
    }

    applyInitialTheme();

    document.addEventListener("DOMContentLoaded", function () {
        const themeBtn = document.getElementById("theme-btn");

        // Որոշ էջերում դեռ theme կոճակ չկա, դրա համար այստեղ անվտանգ դուրս ենք գալիս։
        if (!themeBtn) return;

        themeBtn.addEventListener("click", toggleTheme);
    });
})();
