/* ============================================================
   EFFECTS.JS: efek & animasi tambahan untuk seluruh halaman.
   Dimuat di akhir base.html. Semua bagian berdiri sendiri: kalau satu
   elemen target tidak ada di halaman, bagian itu dilewati begitu saja.
   Isi: 1. Helper animateNumber      2. Dark mode + tombol melayang
        3. Menu aktif (scrollspy)    4. Efek mengetik di hero
        5. Scroll reveal             6. Kartu tilt + spotlight
   ============================================================ */
(function () {
    'use strict';

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    var root = document.documentElement;

    /* ---------- 1. Helper: angka berhitung naik/turun ----------
       Dipakai halaman lain: animateNumber(elemen, angkaTujuan) */
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

    /* ---------- 2. Dark mode + tombol melayang (tema, kembali ke atas) ---------- */
    function currentTheme() { return root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'; }

    var fabs = document.createElement('div');
    fabs.className = 'fab-stack';
    fabs.innerHTML =
        '<button type="button" class="fab fab--theme" data-i18n-attr="aria-label:fab.theme" aria-label="' + I18N.t('fab.theme') + '"><i class="fa-solid fa-moon" aria-hidden="true"></i></button>' +
        '<button type="button" class="fab fab--top" data-i18n-attr="aria-label:fab.top;title:fab.top" aria-label="' + I18N.t('fab.top') + '" title="' + I18N.t('fab.top') + '">' +
            '<svg class="fab__ring" viewBox="0 0 48 48" aria-hidden="true">' +
                '<circle class="fab__ring-bg" cx="24" cy="24" r="21"/>' +
                '<circle class="fab__ring-bar" cx="24" cy="24" r="21"/>' +
            '</svg>' +
            '<i class="fa-solid fa-arrow-up" aria-hidden="true"></i>' +
        '</button>';
    document.body.appendChild(fabs);

    var themeBtn = fabs.querySelector('.fab--theme');
    var topBtn = fabs.querySelector('.fab--top');
    var ringBar = fabs.querySelector('.fab__ring-bar');

    function paintThemeButton() {
        var dark = currentTheme() === 'dark';
        themeBtn.querySelector('i').className = dark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        themeBtn.title = I18N.t(dark ? 'fab.toLight' : 'fab.toDark');
    }
    function applyTheme(theme, remember) {
        root.classList.add('theme-fade');
        root.setAttribute('data-theme', theme);
        if (remember) { try { localStorage.setItem('theme', theme); } catch (e) { /* abaikan */ } }
        paintThemeButton();
        setTimeout(function () { root.classList.remove('theme-fade'); }, 450);
    }
    paintThemeButton();
    document.addEventListener('langchange', paintThemeButton);   // judul tombol ikut bahasa
    themeBtn.addEventListener('click', function () {
        applyTheme(currentTheme() === 'dark' ? 'light' : 'dark', true);
    });
    // Ikuti pengaturan sistem selama pengunjung belum memilih sendiri
    try {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
            if (!localStorage.getItem('theme')) applyTheme(e.matches ? 'dark' : 'light', false);
        });
    } catch (e) { /* abaikan */ }

    // Tombol kembali ke atas + cincin progres scroll
    var RING = 131.95;   // keliling lingkaran r=21
    var ticking = false;
    function updateScrollUi() {
        var max = document.documentElement.scrollHeight - window.innerHeight;
        var progress = max > 0 ? Math.min(window.scrollY / max, 1) : 0;
        ringBar.style.strokeDashoffset = String(RING * (1 - progress));
        topBtn.classList.toggle('is-visible', window.scrollY > 300);
        ticking = false;
    }
    window.addEventListener('scroll', function () {
        if (!ticking) { ticking = true; requestAnimationFrame(updateScrollUi); }
    }, { passive: true });
    window.addEventListener('resize', updateScrollUi);
    updateScrollUi();
    topBtn.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });

    /* ---------- 3. Menu aktif di navbar (scrollspy) ---------- */
    var navLinks = Array.prototype.slice.call(document.querySelectorAll('.nav-menu a'));
    function setActive(link) {
        navLinks.forEach(function (l) {
            var on = l === link;
            l.classList.toggle('is-active', on);
            if (on) l.setAttribute('aria-current', 'page'); else l.removeAttribute('aria-current');
        });
    }
    function trimSlash(p) { return p.replace(/\/+$/, '') || '/'; }
    var here = trimSlash(location.pathname);

    if (here === '/') {
        // Halaman utama: sorot Home/About sesuai bagian yang sedang terlihat
        var spyMap = {};
        navLinks.forEach(function (a) {
            if (trimSlash(a.pathname) === '/' && a.hash) spyMap[a.hash.slice(1)] = a;
        });
        var spyIds = Object.keys(spyMap);
        if (spyIds.length && 'IntersectionObserver' in window) {
            setActive(spyMap[spyIds[0]]);
            var spy = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) setActive(spyMap[entry.target.id]);
                });
            }, { rootMargin: '-40% 0px -55% 0px' });
            spyIds.forEach(function (id) {
                var section = document.getElementById(id);
                if (section) spy.observe(section);
            });
        }
    } else {
        // Halaman lain: sorot menu yang sesuai alamat halaman
        var match = null;
        navLinks.forEach(function (a) {
            var p = trimSlash(a.pathname);
            if (p !== '/' && !a.hash && (here === p || here.indexOf(p + '/') === 0)) match = a;
        });
        if (match) setActive(match);
    }

    /* ---------- 4. Efek mengetik di hero ---------- */
    var heroName = document.querySelector('h1.name');
    if (heroName) {
        // Kata-kata yang diketik mengikuti bahasa aktif (kamus di i18n.js: 'hero.words')
        var words = function () { return I18N.get('hero.words') || ['Data Science']; };
        var line = document.createElement('p');
        line.className = 'role-line';
        line.innerHTML = '<span data-i18n="hero.exploring">' + I18N.t('hero.exploring') + '</span> <span class="role-typed"></span><span class="role-cursor" aria-hidden="true"></span>';
        heroName.insertAdjacentElement('afterend', line);
        var typed = line.querySelector('.role-typed');

        if (reduceMotion) {
            typed.textContent = words()[0];
            document.addEventListener('langchange', function () { typed.textContent = words()[0]; });
        } else {
            var wordIndex = 0, charIndex = 0, deleting = false;
            (function tick() {
                var list = words();
                var word = list[wordIndex % list.length];
                if (!document.hidden) {
                    charIndex += deleting ? -1 : 1;
                    typed.textContent = word.slice(0, charIndex);
                }
                var delay = deleting ? 35 : 75;
                if (!deleting && charIndex === word.length) { deleting = true; delay = 1500; }
                else if (deleting && charIndex === 0) { deleting = false; wordIndex = (wordIndex + 1) % words().length; delay = 350; }
                setTimeout(tick, delay);
            })();
        }
    }

    /* ---------- 5. Scroll reveal (bagian About & Education di halaman utama) ---------- */
    if ('IntersectionObserver' in window && !reduceMotion) {
        var groups = [
            ['.about-photo'],
            ['.about-title', '.about-bio', '.info-item', '.cv-button'],
            ['.skills-head', '.skill-row', '.skills-note'],
            ['.edu-intro'],
            ['.edu-item']
        ];
        var revealObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var el = entry.target;
                revealObserver.unobserve(el);
                el.classList.add('is-visible');
                // Setelah selesai, lepas class supaya transisi hover bawaan elemen kembali normal
                setTimeout(function () { el.classList.remove('reveal', 'is-visible'); }, 1400);
            });
        }, { threshold: 0.15 });

        groups.forEach(function (selectors) {
            var index = 0;
            selectors.forEach(function (selector) {
                document.querySelectorAll(selector).forEach(function (el) {
                    // Elemen yang sudah terlihat saat halaman dibuka tidak perlu dianimasikan
                    if (el.getBoundingClientRect().top < window.innerHeight * 0.9) return;
                    el.classList.add('reveal');
                    el.style.setProperty('--d', (index++ * 90) + 'ms');
                    revealObserver.observe(el);
                });
            });
        });
    }

    /* ---------- 6. Kartu: miring 3D + sorotan cahaya mengikuti kursor ---------- */
    if (finePointer && !reduceMotion) {
        var CARD_SELECTOR = '.proj-card';
        var activeCard = null;

        function resetCard(card) {
            card.classList.remove('is-tilting');
            card.style.removeProperty('--rx');
            card.style.removeProperty('--ry');
        }
        document.addEventListener('pointermove', function (e) {
            var card = e.target.closest ? e.target.closest(CARD_SELECTOR) : null;
            if (activeCard && activeCard !== card) resetCard(activeCard);
            activeCard = card;
            if (!card || card.classList.contains('skeleton-card')) return;
            var rect = card.getBoundingClientRect();
            var x = (e.clientX - rect.left) / rect.width;
            var y = (e.clientY - rect.top) / rect.height;
            card.style.setProperty('--mx', (x * 100).toFixed(1) + '%');
            card.style.setProperty('--my', (y * 100).toFixed(1) + '%');
            card.style.setProperty('--ry', ((x - 0.5) * 7).toFixed(2) + 'deg');
            card.style.setProperty('--rx', ((0.5 - y) * 5).toFixed(2) + 'deg');
            card.classList.add('is-tilting');
        }, { passive: true });
        root.addEventListener('mouseleave', function () {
            if (activeCard) { resetCard(activeCard); activeCard = null; }
        });
    }
})();