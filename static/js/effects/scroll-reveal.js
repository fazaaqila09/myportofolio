// Elemen di halaman utama muncul halus (naik + memudar) saat discroll ke layar.
(function () {
    'use strict';

    if (!('IntersectionObserver' in window)) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    // Tiap grup diberi jeda berurutan sendiri
    var groups = [
        ['.about-photo'],
        ['.about-title', '.about-bio', '.info-item', '.cv-button'],
        ['.skills-head', '.skill-row', '.skills-note'],
        ['.edu-intro'],
        ['.edu-item']
    ];

    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            var el = entry.target;
            observer.unobserve(el);
            el.classList.add('is-visible');
            // Lepas class setelah selesai supaya transisi hover elemen kembali normal
            setTimeout(function () { el.classList.remove('reveal', 'is-visible'); }, 1400);
        });
    }, { threshold: 0.15 });

    groups.forEach(function (selectors) {
        var index = 0;
        selectors.forEach(function (selector) {
            document.querySelectorAll(selector).forEach(function (el) {
                // Yang sudah terlihat saat halaman dibuka tidak dianimasikan
                if (el.getBoundingClientRect().top < window.innerHeight * 0.9) return;
                el.classList.add('reveal');
                el.style.setProperty('--d', (index++ * 90) + 'ms');
                observer.observe(el);
            });
        });
    });
})();
