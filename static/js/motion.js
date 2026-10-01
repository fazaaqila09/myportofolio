/* ============================================================
   MOTION.JS: tombol magnetik dan transisi halaman
   cadangan (untuk browser yang belum mendukung View Transitions).
   Efek magnetik hanya aktif di perangkat dengan mouse, dan semuanya
   menghormati pengaturan "kurangi gerakan". (Bentuk kursor kustom
   diatur lewat CSS di extras.css, bukan di sini.)
   ============================================================ */
(function () {
    'use strict';

    var root = document.documentElement;
    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    /* ======================================================
       1. TOMBOL MAGNETIK: tombol sedikit "tertarik" ke arah kursor
       ====================================================== */
    if (finePointer && !reduced) {
        var MAGNETIC = '.button, .nav-lang, .nav-account, .fab:not(.fab--top), .footer-cta, .footer-social a, .lb__btn';
        var PULL = 0.28;          // seberapa kuat tertarik (0-1)
        var LIMIT = 14;           // batas geser maksimum (px)
        var active = new Map();   // elemen -> {x, y, tx, ty}
        var loop = false;

        function clamp(v) { return Math.max(-LIMIT, Math.min(LIMIT, v)); }

        function tick() {
            var moving = false;
            active.forEach(function (s, el) {
                s.x += (s.tx - s.x) * 0.18;
                s.y += (s.ty - s.y) * 0.18;
                if (Math.abs(s.tx - s.x) < 0.05 && Math.abs(s.ty - s.y) < 0.05 && s.tx === 0 && s.ty === 0) {
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
            if (moving) requestAnimationFrame(tick); else loop = false;
        }
        function wake() { if (!loop) { loop = true; requestAnimationFrame(tick); } }

        var hovered = null;
        document.addEventListener('pointermove', function (e) {
            if (e.pointerType !== 'mouse') return;
            var el = e.target.closest ? e.target.closest(MAGNETIC) : null;
            if (el && (el.disabled || el.getAttribute('aria-disabled') === 'true')) el = null;

            if (hovered && hovered !== el) {          // keluar dari tombol: kembali ke tempat semula
                var old = active.get(hovered);
                if (old) { old.tx = 0; old.ty = 0; wake(); }
                hovered = null;
            }
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
            if (hovered) {
                var s = active.get(hovered);
                if (s) { s.tx = 0; s.ty = 0; wake(); }
                hovered = null;
            }
        });
    }

    /* ======================================================
       2. TRANSISI HALAMAN CADANGAN
       Browser yang mendukung View Transitions (Chrome, Edge, Safari baru)
       memakai CSS saja. Selain itu: halaman memudar keluar sebelum
       pindah, lalu memudar masuk di halaman berikutnya.
       ====================================================== */
    if (root.classList.contains('no-vt') && !reduced) {
        document.addEventListener('click', function (e) {
            if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
            var a = e.target.closest ? e.target.closest('a[href]') : null;
            if (!a || a.target === '_blank' || a.hasAttribute('download')) return;
            var url;
            try { url = new URL(a.href, location.href); } catch (err) { return; }
            if (url.origin !== location.origin) return;
            if (url.pathname === location.pathname && url.search === location.search) return;   // anchor di halaman yang sama
            e.preventDefault();
            root.classList.add('is-leaving');
            window.setTimeout(function () { location.href = url.href; }, 220);
        });
        // tombol "Kembali" browser: pulihkan halaman yang sempat memudar
        window.addEventListener('pageshow', function (e) {
            if (e.persisted) root.classList.remove('is-leaving');
        });
    }

    /* ======================================================
       3. EFEK SENTUH: HP tidak punya "hover", jadi chip Skills dan baris Education
       diberi kelas .is-lit saat disentuh (efeknya sama dengan hover di desktop),
       lalu dilepas sebentar setelah jari diangkat. Mouse tidak ikut: ia memakai :hover.
       ====================================================== */
    var LIT_TARGETS = [
        { selector: '.skill-chip', hold: 1000 },
        { selector: '.edu-item', hold: 1200 }
    ];
    var lit = new Map();    // elemen -> {hold, timer}

    function lightUp(el, hold) {
        var s = lit.get(el);
        if (s) clearTimeout(s.timer);
        lit.set(el, { hold: hold, timer: null });
        el.classList.add('is-lit');
    }
    function releaseAll(delayScale) {
        lit.forEach(function (s, el) {
            clearTimeout(s.timer);
            s.timer = setTimeout(function () { el.classList.remove('is-lit'); lit.delete(el); }, s.hold * delayScale);
        });
    }
    document.addEventListener('pointerdown', function (e) {
        if (e.pointerType === 'mouse' || !e.target.closest) return;
        LIT_TARGETS.forEach(function (t) {
            var el = e.target.closest(t.selector);
            if (el) lightUp(el, t.hold);
        });
    }, { passive: true });
    document.addEventListener('pointerup', function () { releaseAll(1); }, { passive: true });
    // jari menggeser halaman (scroll) = bukan ketukan: padamkan lebih cepat
    document.addEventListener('pointercancel', function () { releaseAll(0.25); }, { passive: true });
})();