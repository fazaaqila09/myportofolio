// Efek mengetik di bawah nama pada hero. Kata-katanya dari kamus 'hero.words' (ikut bahasa).
(function () {
    'use strict';

    var heroName = document.querySelector('h1.name');
    if (!heroName) return;

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var words = function () { return I18N.get('hero.words') || ['Data Science']; };

    var line = document.createElement('p');
    line.className = 'role-line';
    line.innerHTML = '<span data-i18n="hero.exploring">' + I18N.t('hero.exploring') + '</span> <span class="role-typed"></span><span class="role-cursor" aria-hidden="true"></span>';
    heroName.insertAdjacentElement('afterend', line);
    var typed = line.querySelector('.role-typed');

    if (reduceMotion) {
        typed.textContent = words()[0];
        document.addEventListener('langchange', function () { typed.textContent = words()[0]; });
        return;
    }

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
})();
