// Kartu Projects miring 3D dan disorot cahaya mengikuti kursor (hanya perangkat dengan mouse).
(function () {
    'use strict';

    var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!finePointer || reduceMotion) return;

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

    document.documentElement.addEventListener('mouseleave', function () {
        if (activeCard) { resetCard(activeCard); activeCard = null; }
    });
})();
