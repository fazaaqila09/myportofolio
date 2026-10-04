// Transisi halaman cadangan untuk browser tanpa View Transitions (kelas .no-vt dipasang di <head>):
// halaman memudar keluar sebelum pindah. Browser yang mendukung cukup memakai CSS.
(function () {
    'use strict';

    var root = document.documentElement;
    if (!root.classList.contains('no-vt')) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    document.addEventListener('click', function (e) {
        if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        var link = e.target.closest ? e.target.closest('a[href]') : null;
        if (!link || link.target === '_blank' || link.hasAttribute('download')) return;

        var url;
        try { url = new URL(link.href, location.href); } catch (err) { return; }
        if (url.origin !== location.origin) return;
        if (url.pathname === location.pathname && url.search === location.search) return;   // anchor di halaman sama

        e.preventDefault();
        root.classList.add('is-leaving');
        window.setTimeout(function () { location.href = url.href; }, 220);
    });

    // Tombol "Kembali": pulihkan halaman yang sempat memudar
    window.addEventListener('pageshow', function (e) {
        if (e.persisted) root.classList.remove('is-leaving');
    });
})();
