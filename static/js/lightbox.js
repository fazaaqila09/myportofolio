/* ============================================================
   LIGHTBOX FOTO EXPERIENCE
   Klik foto kegiatan -> terbuka besar. Pindah foto dengan tombol
   panah, tombol keyboard (← →), atau geser jari di HP. Esc / klik
   latar / tombol X untuk menutup. Teks mengikuti bahasa (ID/EN).
   ============================================================ */
(function () {
    'use strict';

    var cards = Array.prototype.slice.call(document.querySelectorAll('.exp-card'))
        .filter(function (card) { return card.querySelector('.exp-photo img'); });
    if (!cards.length) return;

    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function tr(key, fallback) { return window.t ? window.t(key, fallback) : fallback; }
    function text(card, selector) {
        var el = card.querySelector(selector);
        return el ? el.textContent.replace(/\s+/g, ' ').trim() : '';
    }

    /* ---------- Bangun lightbox ---------- */
    var box = document.createElement('div');
    box.className = 'lb';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.hidden = true;
    box.innerHTML =
        '<button type="button" class="lb__btn lb__close">&times;</button>' +
        '<button type="button" class="lb__btn lb__prev" aria-hidden="false">&#8249;</button>' +
        '<button type="button" class="lb__btn lb__next">&#8250;</button>' +
        '<div class="lb__stage">' +
            '<img class="lb__img" alt="" draggable="false">' +
            '<div class="lb__cap"><div><h4 class="lb__title"></h4><p class="lb__sub"></p></div><span class="lb__count"></span></div>' +
        '</div>' +
        '<div class="lb__hint"><kbd>&larr;</kbd> <kbd>&rarr;</kbd> <span class="lb__hint-switch"></span> &nbsp;&middot;&nbsp; <kbd>Esc</kbd> <span class="lb__hint-close"></span></div>';
    document.body.appendChild(box);

    var img = box.querySelector('.lb__img');
    var titleEl = box.querySelector('.lb__title');
    var subEl = box.querySelector('.lb__sub');
    var countEl = box.querySelector('.lb__count');
    var prevBtn = box.querySelector('.lb__prev');
    var nextBtn = box.querySelector('.lb__next');
    var closeBtn = box.querySelector('.lb__close');
    var single = cards.length < 2;
    if (single) { prevBtn.hidden = true; nextBtn.hidden = true; }

    var current = 0;
    var opener = null;

    function labels() {
        box.setAttribute('aria-label', tr('lb.label', 'Photo viewer'));
        closeBtn.setAttribute('aria-label', tr('lb.close', 'Close'));
        prevBtn.setAttribute('aria-label', tr('lb.prev', 'Previous photo'));
        nextBtn.setAttribute('aria-label', tr('lb.next', 'Next photo'));
        box.querySelector('.lb__hint-switch').textContent = tr('lb.hint.switch', 'switch photo');
        box.querySelector('.lb__hint-close').textContent = tr('lb.hint.close', 'close');
        cards.forEach(function (card) {
            var photo = card.querySelector('.exp-photo');
            photo.setAttribute('aria-label', tr('lb.enlarge', 'Enlarge photo') + ': ' + text(card, '.exp-org'));
        });
    }

    function fill(index) {
        var card = cards[current = (index + cards.length) % cards.length];
        var photo = card.querySelector('.exp-photo img');
        img.src = photo.currentSrc || photo.src;
        img.alt = text(card, '.exp-org');
        titleEl.textContent = text(card, '.exp-org');
        subEl.textContent = [text(card, '.exp-role'), text(card, '.exp-period')].filter(Boolean).join(' · ');
        countEl.textContent = (current + 1) + ' / ' + cards.length;
        // muat foto tetangga lebih dulu supaya perpindahan terasa instan
        [current + 1, current - 1].forEach(function (i) {
            var n = cards[(i + cards.length) % cards.length].querySelector('.exp-photo img');
            if (n) (new Image()).src = n.currentSrc || n.src;
        });
    }

    function go(step) {
        if (single) return;
        if (reduced) { fill(current + step); return; }
        var out = step > 0 ? 'lb-out-left' : 'lb-out-right';
        var inn = step > 0 ? 'lb-in-right' : 'lb-in-left';
        img.classList.add(out);
        window.setTimeout(function () {
            fill(current + step);
            img.classList.remove(out);
            img.classList.add(inn);
            void img.offsetWidth;                       // mulai ulang animasi
            img.classList.remove(inn);
        }, 140);
    }

    function open(index, trigger) {
        opener = trigger || null;
        labels();
        fill(index);
        box.hidden = false;
        document.documentElement.classList.add('lb-lock');
        void box.offsetWidth;
        box.classList.add('is-open');
        closeBtn.focus({ preventScroll: true });
    }

    function close() {
        if (box.hidden) return;
        box.classList.remove('is-open');
        document.documentElement.classList.remove('lb-lock');
        window.setTimeout(function () { box.hidden = true; }, reduced ? 0 : 220);
        if (opener) opener.focus({ preventScroll: true });
    }

    /* ---------- Pemicu: klik / Enter / Spasi pada foto ---------- */
    cards.forEach(function (card, i) {
        var photo = card.querySelector('.exp-photo');
        photo.setAttribute('role', 'button');
        photo.setAttribute('tabindex', '0');
        if (!photo.querySelector('.exp-photo__zoom')) {
            var zoom = document.createElement('span');
            zoom.className = 'exp-photo__zoom';
            zoom.setAttribute('aria-hidden', 'true');
            zoom.innerHTML = '<i class="fa-solid fa-magnifying-glass-plus"></i> <span data-i18n="lb.enlarge.short">Enlarge</span>';
            photo.appendChild(zoom);
        }
        photo.addEventListener('click', function () { open(i, photo); });
        photo.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(i, photo); }
        });
    });
    if (window.I18N) window.I18N.apply(document);
    labels();

    /* ---------- Kontrol ---------- */
    prevBtn.addEventListener('click', function () { go(-1); });
    nextBtn.addEventListener('click', function () { go(1); });
    closeBtn.addEventListener('click', close);
    box.addEventListener('click', function (e) {
        if (e.target === box || e.target.classList.contains('lb__stage')) close();
    });

    document.addEventListener('keydown', function (e) {
        if (box.hidden) return;
        if (e.key === 'Escape') { e.preventDefault(); close(); }
        else if (e.key === 'ArrowRight') { e.preventDefault(); go(1); }
        else if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1); }
        else if (e.key === 'Tab') {
            // fokus tidak boleh keluar dari lightbox
            var focusable = [closeBtn, prevBtn, nextBtn].filter(function (b) { return !b.hidden; });
            var first = focusable[0], last = focusable[focusable.length - 1];
            if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
            else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        }
    });

    /* ---------- Geser jari (HP) ---------- */
    var startX = null, startY = null;
    box.addEventListener('touchstart', function (e) {
        if (e.touches.length !== 1) return;
        startX = e.touches[0].clientX; startY = e.touches[0].clientY;
    }, { passive: true });
    box.addEventListener('touchend', function (e) {
        if (startX === null) return;
        var dx = e.changedTouches[0].clientX - startX;
        var dy = e.changedTouches[0].clientY - startY;
        startX = startY = null;
        if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.4) go(dx < 0 ? 1 : -1);
    }, { passive: true });

    // ganti bahasa: perbarui label & keterangan foto yang sedang terbuka
    document.addEventListener('langchange', function () {
        labels();
        if (!box.hidden) fill(current);
    });
})();