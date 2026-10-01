/* ============================================================
   EXTRAS.JS: garis menu aktif selebar teks (diukur ulang otomatis saat teks menu berubah)
   ============================================================ */
(function () {
    'use strict';

    var root = document.documentElement;

    /* Garis menu aktif = selebar teks */
    var menu = document.querySelector('.nav-menu');
    if (menu) {
        var measureUnderline = function () {
            var link = menu.querySelector('a.is-active');
            if (!link) return;
            var range = document.createRange();
            range.selectNodeContents(link);
            var text = range.getBoundingClientRect();
            var box = link.getBoundingClientRect();
            var spacing = parseFloat(getComputedStyle(link).letterSpacing) || 0;   // spasi huruf terakhir
            link.style.setProperty('--u-left', (text.left - box.left).toFixed(1) + 'px');
            link.style.setProperty('--u-width', Math.max(text.width - spacing, 8).toFixed(1) + 'px');
        };
        new MutationObserver(measureUnderline).observe(menu, { subtree: true, attributes: true, attributeFilter: ['class'] });
        window.addEventListener('resize', measureUnderline);
        window.addEventListener('load', measureUnderline);
        document.addEventListener('langchange', function () { requestAnimationFrame(measureUnderline); });   // teks menu berubah lebar
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(measureUnderline);

        // Kunci perbaikannya: ukur ulang setiap kali LEBAR menu berubah, apa pun penyebabnya
        // (teks diterjemahkan ke Indonesia setelah halaman dimuat, font web selesai dimuat, dll).
        // Tanpa ini garis tetap selebar kata bahasa Inggris saat halaman dibuka dalam bahasa ID.
        if ('ResizeObserver' in window) {
            var resizeWatcher = new ResizeObserver(function () { requestAnimationFrame(measureUnderline); });
            menu.querySelectorAll('a').forEach(function (link) { resizeWatcher.observe(link); });
        }
        measureUnderline();
    }
})();