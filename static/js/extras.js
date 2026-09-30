/* ============================================================
   EXTRAS.JS: garis menu aktif selebar teks
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
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(measureUnderline);
        measureUnderline();
    }
})();