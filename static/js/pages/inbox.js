// Halaman Inbox: buka/tutup pesan. Pesan yang belum dibaca otomatis ditandai dibaca saat dibuka,
// lalu lencana jumlah pesan baru di navbar diperbarui.
(function () {
    'use strict';

    function csrfToken() {
        var el = document.querySelector('[name=csrfmiddlewaretoken]');
        return el ? el.value : '';
    }
    function setBadges(count) {
        document.querySelectorAll('[data-inbox-badge]').forEach(function (badge) {
            badge.textContent = count;
            badge.hidden = !count;
        });
    }
    function markRead(item) {
        var body = new URLSearchParams({ set: 'read', csrfmiddlewaretoken: csrfToken() });
        fetch(item.dataset.readUrl, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            body: body
        }).then(function (r) { return r.ok ? r.json() : null; }).then(function (data) {
            if (!data) return;
            item.classList.remove('is-unread');
            var button = item.querySelector('.inbox-toggle-btn');
            if (button) {
                button.dataset.i18n = 'inbox.mark.unread';
                button.textContent = window.t('inbox.mark.unread', 'Mark as unread');
            }
            setBadges(data.unread);
        }).catch(function () { /* gagal diam-diam: status masih bisa diubah manual */ });
    }

    document.querySelectorAll('.inbox-item').forEach(function (item) {
        var head = item.querySelector('.inbox-item__head');
        head.addEventListener('click', function () {
            var open = head.getAttribute('aria-expanded') !== 'true';
            head.setAttribute('aria-expanded', open ? 'true' : 'false');
            item.classList.toggle('is-open', open);
            if (open && item.classList.contains('is-unread')) markRead(item);
        });
    });
})();
