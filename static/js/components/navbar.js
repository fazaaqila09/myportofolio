// Navbar: menu aktif (scrollspy), garis kuning selebar teks menu aktif, dan menu dropdown akun.
(function () {
    'use strict';

    var menu = document.querySelector('.nav-menu');
    var links = Array.prototype.slice.call(document.querySelectorAll('.nav-menu a'));

    // Menu aktif
    function setActive(link) {
        links.forEach(function (l) {
            var on = l === link;
            l.classList.toggle('is-active', on);
            if (on) l.setAttribute('aria-current', 'page'); else l.removeAttribute('aria-current');
        });
    }
    function trimSlash(path) { return path.replace(/\/+$/, '') || '/'; }
    var here = trimSlash(location.pathname);

    if (here === '/') {
        // Halaman utama: sorot menu sesuai section yang sedang terlihat
        var spyMap = {};
        links.forEach(function (a) {
            if (trimSlash(a.pathname) === '/' && a.hash) spyMap[a.hash.slice(1)] = a;
        });
        var ids = Object.keys(spyMap);
        if (ids.length && 'IntersectionObserver' in window) {
            setActive(spyMap[ids[0]]);
            var spy = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) setActive(spyMap[entry.target.id]);
                });
            }, { rootMargin: '-40% 0px -55% 0px' });
            ids.forEach(function (id) {
                var section = document.getElementById(id);
                if (section) spy.observe(section);
            });
        }
    } else {
        // Halaman lain: sorot menu yang cocok dengan alamat halaman
        var match = null;
        links.forEach(function (a) {
            var p = trimSlash(a.pathname);
            if (p !== '/' && !a.hash && (here === p || here.indexOf(p + '/') === 0)) match = a;
        });
        if (match) setActive(match);
    }

    // Garis kuning menu aktif: posisi & lebarnya diukur dari teks (--u-left, --u-width)
    if (menu) {
        var measureUnderline = function () {
            var link = menu.querySelector('a.is-active');
            if (!link) return;
            var range = document.createRange();
            range.selectNodeContents(link);
            var text = range.getBoundingClientRect();
            var box = link.getBoundingClientRect();
            var spacing = parseFloat(getComputedStyle(link).letterSpacing) || 0;   // spasi setelah huruf terakhir
            link.style.setProperty('--u-left', (text.left - box.left).toFixed(1) + 'px');
            link.style.setProperty('--u-width', Math.max(text.width - spacing, 8).toFixed(1) + 'px');
        };
        new MutationObserver(measureUnderline).observe(menu, { subtree: true, attributes: true, attributeFilter: ['class'] });
        window.addEventListener('resize', measureUnderline);
        window.addEventListener('load', measureUnderline);
        document.addEventListener('langchange', function () { requestAnimationFrame(measureUnderline); });
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(measureUnderline);
        // Ukur ulang tiap kali lebar menu berubah (mis. teks diterjemahkan setelah halaman dimuat)
        if ('ResizeObserver' in window) {
            var watcher = new ResizeObserver(function () { requestAnimationFrame(measureUnderline); });
            links.forEach(function (link) { watcher.observe(link); });
        }
        measureUnderline();
    }

    // Menu akun: klik username -> menu (Inbox, Logout) muncul tepat di bawahnya
    var accountMenu = document.getElementById('profile-menu');
    var trigger = document.getElementById('account-trigger');
    if (accountMenu && trigger) {
        var wasOpen = false;
        var place = function () {
            var rect = trigger.getBoundingClientRect();
            accountMenu.style.top = (rect.bottom + 10) + 'px';
            accountMenu.style.right = (document.documentElement.clientWidth - rect.right) + 'px';
        };
        var toggle = function () {
            // Klik di luar sudah menutup menu; jangan langsung dibuka lagi
            if (wasOpen) { wasOpen = false; return; }
            place();
            accountMenu.showPopover();
        };
        accountMenu.addEventListener('beforetoggle', function (e) {
            trigger.setAttribute('aria-expanded', e.newState === 'open' ? 'true' : 'false');
        });
        trigger.addEventListener('pointerdown', function () { wasOpen = accountMenu.matches(':popover-open'); });
        trigger.addEventListener('click', function (e) { e.preventDefault(); toggle(); });
        trigger.addEventListener('keydown', function (e) {
            if (e.key === ' ') { e.preventDefault(); wasOpen = accountMenu.matches(':popover-open'); toggle(); }
        });
        window.addEventListener('resize', function () {
            if (accountMenu.matches(':popover-open')) place();
        });
    }
})();
