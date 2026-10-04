// Halaman Contact: penghitung karakter pesan dan tombol "Sending..." saat form dikirim.
(function () {
    'use strict';

    var form = document.getElementById('contact-form');
    if (!form) return;
    var area = form.querySelector('textarea');
    var counter = document.getElementById('contact-counter');

    function count() {
        counter.textContent = area.value.length + ' / ' + (area.maxLength > 0 ? area.maxLength : 2000);
    }
    area.addEventListener('input', count);
    count();

    form.addEventListener('submit', function () {
        var button = document.getElementById('contact-submit');
        button.disabled = true;
        var label = button.querySelector('span');
        label.setAttribute('data-i18n', 'contact.sending');
        label.textContent = window.I18N ? I18N.t('contact.sending') : 'Sending...';
    });
})();
