// Tombol melayang di kiri bawah: ganti tema terang/gelap dan kembali ke atas.
(function () {
    'use strict';

    var root = document.documentElement;
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var RING = 131.95;   // keliling lingkaran progres (r = 21)

    var stack = document.createElement('div');
    stack.className = 'fab-stack';
    stack.innerHTML =
        '<button type="button" class="fab fab--theme" data-i18n-attr="aria-label:fab.theme" aria-label="' + I18N.t('fab.theme') + '"><i class="fa-solid fa-moon" aria-hidden="true"></i></button>' +
        '<button type="button" class="fab fab--top" data-i18n-attr="aria-label:fab.top;title:fab.top" aria-label="' + I18N.t('fab.top') + '" title="' + I18N.t('fab.top') + '">' +
            '<svg class="fab__ring" viewBox="0 0 48 48" aria-hidden="true">' +
                '<circle class="fab__ring-bg" cx="24" cy="24" r="21"/>' +
                '<circle class="fab__ring-bar" cx="24" cy="24" r="21"/>' +
            '</svg>' +
            '<i class="fa-solid fa-arrow-up" aria-hidden="true"></i>' +
        '</button>';
    document.body.appendChild(stack);

    var themeButton = stack.querySelector('.fab--theme');
    var topButton = stack.querySelector('.fab--top');
    var ringBar = stack.querySelector('.fab__ring-bar');

    // Tema
    function currentTheme() {
        return root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    }
    function paintThemeButton() {
        var dark = currentTheme() === 'dark';
        themeButton.querySelector('i').className = dark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        themeButton.title = I18N.t(dark ? 'fab.toLight' : 'fab.toDark');
    }
    function applyTheme(theme, remember) {
        root.classList.add('theme-fade');   // warna berganti halus
        root.setAttribute('data-theme', theme);
        if (remember) { try { localStorage.setItem('theme', theme); } catch (e) { /* abaikan */ } }
        paintThemeButton();
        setTimeout(function () { root.classList.remove('theme-fade'); }, 450);
    }

    paintThemeButton();
    document.addEventListener('langchange', paintThemeButton);
    themeButton.addEventListener('click', function () {
        applyTheme(currentTheme() === 'dark' ? 'light' : 'dark', true);
    });
    // Ikuti tema sistem selama pengunjung belum memilih sendiri
    try {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
            if (!localStorage.getItem('theme')) applyTheme(e.matches ? 'dark' : 'light', false);
        });
    } catch (e) { /* abaikan */ }

    // Kembali ke atas + cincin progres scroll
    var ticking = false;
    function updateScrollUi() {
        var max = document.documentElement.scrollHeight - window.innerHeight;
        var progress = max > 0 ? Math.min(window.scrollY / max, 1) : 0;
        ringBar.style.strokeDashoffset = String(RING * (1 - progress));
        topButton.classList.toggle('is-visible', window.scrollY > 300);
        ticking = false;
    }
    window.addEventListener('scroll', function () {
        if (!ticking) { ticking = true; requestAnimationFrame(updateScrollUi); }
    }, { passive: true });
    window.addEventListener('resize', updateScrollUi);
    updateScrollUi();
    topButton.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
})();
