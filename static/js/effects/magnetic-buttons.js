// Tombol sedikit "tertarik" ke arah kursor. Hanya perangkat dengan mouse, mati bila "kurangi gerakan".
// Posisi dikirim lewat --mag-x / --mag-y (lihat [data-magnetic] di animations.css).
(function () {
    'use strict';

    var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!finePointer || reduceMotion) return;

    var MAGNETIC = '.button, .nav-lang, .nav-account, .fab:not(.fab--top), .footer-cta, .footer-social a, .lb__btn';
    var PULL = 0.28;          // kekuatan tarikan (0-1)
    var LIMIT = 14;           // geseran maksimum (px)
    var active = new Map();   // elemen -> { x, y, tx, ty }
    var looping = false;
    var hovered = null;

    function clamp(v) { return Math.max(-LIMIT, Math.min(LIMIT, v)); }

    // Gerak halus menuju target; elemen yang sudah kembali ke posisi awal dilepas
    function tick() {
        var moving = false;
        active.forEach(function (s, el) {
            s.x += (s.tx - s.x) * 0.18;
            s.y += (s.ty - s.y) * 0.18;
            var settled = Math.abs(s.tx - s.x) < 0.05 && Math.abs(s.ty - s.y) < 0.05;
            if (settled && s.tx === 0 && s.ty === 0) {
                el.style.removeProperty('--mag-x');
                el.style.removeProperty('--mag-y');
                el.removeAttribute('data-magnetic');
                active.delete(el);
            } else {
                el.style.setProperty('--mag-x', s.x.toFixed(2) + 'px');
                el.style.setProperty('--mag-y', s.y.toFixed(2) + 'px');
                moving = true;
            }
        });
        if (moving) requestAnimationFrame(tick); else looping = false;
    }
    function wake() {
        if (!looping) { looping = true; requestAnimationFrame(tick); }
    }
    function release(el) {
        var s = active.get(el);
        if (s) { s.tx = 0; s.ty = 0; wake(); }
    }

    document.addEventListener('pointermove', function (e) {
        if (e.pointerType !== 'mouse') return;
        var el = e.target.closest ? e.target.closest(MAGNETIC) : null;
        if (el && (el.disabled || el.getAttribute('aria-disabled') === 'true')) el = null;

        if (hovered && hovered !== el) { release(hovered); hovered = null; }
        if (!el) return;

        var rect = el.getBoundingClientRect();
        var s = active.get(el);
        if (!s) {
            s = { x: 0, y: 0, tx: 0, ty: 0 };
            active.set(el, s);
            el.setAttribute('data-magnetic', '');
        }
        s.tx = clamp((e.clientX - (rect.left + rect.width / 2)) * PULL);
        s.ty = clamp((e.clientY - (rect.top + rect.height / 2)) * PULL);
        hovered = el;
        wake();
    }, { passive: true });

    document.addEventListener('mouseleave', function () {
        if (hovered) { release(hovered); hovered = null; }
    });
})();
