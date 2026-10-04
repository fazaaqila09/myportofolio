// Layar sentuh tidak punya hover: chip Skills dan baris Education diberi kelas .is-lit saat
// disentuh (tampilannya sama dengan hover), lalu dilepas sebentar setelah jari diangkat.
(function () {
    'use strict';

    var TARGETS = [
        { selector: '.skill-chip', hold: 1000 },
        { selector: '.edu-item', hold: 1200 }
    ];
    var lit = new Map();   // elemen -> { hold, timer }

    function lightUp(el, hold) {
        var s = lit.get(el);
        if (s) clearTimeout(s.timer);
        lit.set(el, { hold: hold, timer: null });
        el.classList.add('is-lit');
    }
    function releaseAll(delayScale) {
        lit.forEach(function (s, el) {
            clearTimeout(s.timer);
            s.timer = setTimeout(function () {
                el.classList.remove('is-lit');
                lit.delete(el);
            }, s.hold * delayScale);
        });
    }

    document.addEventListener('pointerdown', function (e) {
        if (e.pointerType === 'mouse' || !e.target.closest) return;
        TARGETS.forEach(function (t) {
            var el = e.target.closest(t.selector);
            if (el) lightUp(el, t.hold);
        });
    }, { passive: true });
    document.addEventListener('pointerup', function () { releaseAll(1); }, { passive: true });
    // Jari menggeser halaman (scroll), bukan mengetuk: padamkan lebih cepat
    document.addEventListener('pointercancel', function () { releaseAll(0.25); }, { passive: true });
})();
