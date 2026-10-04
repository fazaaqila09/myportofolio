// Angka berhitung naik/turun ke nilai baru. Dipakai halaman Projects: animateNumber(el, 12).
(function () {
    'use strict';

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    window.animateNumber = function (el, to, duration) {
        if (!el) return;
        var from = parseInt(el.dataset.value !== undefined ? el.dataset.value : el.textContent, 10) || 0;
        el.dataset.value = to;
        if (reduceMotion || from === to) { el.textContent = to; return; }

        var start = null;
        var total = duration || 600;
        function step(now) {
            if (start === null) start = now;
            var progress = Math.min((now - start) / total, 1);
            var eased = 1 - Math.pow(1 - progress, 3);   // melambat di akhir
            el.textContent = Math.round(from + (to - from) * eased);
            if (progress < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    };
})();
