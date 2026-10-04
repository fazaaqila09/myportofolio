// Fungsi bantu untuk halaman yang memuat data lewat fetch(): token CSRF, escapeHtml (cegah XSS),
// debounce (tunda pencarian), dan format tanggal bulan-tahun sesuai bahasa.

// Nilai cookie berdasarkan namanya (dipakai untuk cookie csrftoken)
function getCookie(name) {
    if (!document.cookie) return null;
    const prefix = name + '=';
    for (const part of document.cookie.split(';')) {
        const cookie = part.trim();
        if (cookie.startsWith(prefix)) return decodeURIComponent(cookie.slice(prefix.length));
    }
    return null;
}

// Token CSRF: diambil dari input tersembunyi {% csrf_token %} di halaman,
// cadangannya dari cookie csrftoken. Dikirim lewat header X-CSRFToken.
function getCsrfToken() {
    const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return (input && input.value) || getCookie('csrftoken') || '';
}

// Mengubah karakter khusus HTML menjadi entity sehingga teks dari server
// selalu tampil sebagai teks biasa, tidak pernah dijalankan sebagai HTML/JS.
// Contoh: <img src=x onerror=alert(1)>  ->  &lt;img src=x onerror=alert(1)&gt;
function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

// Debouncing: fungsi baru benar-benar dipanggil setelah tidak ada panggilan
// lagi selama `delay` milidetik. Dipakai pada pencarian supaya permintaan
// ke server hanya dikirim saat pengguna berhenti mengetik.
function debounce(fn, delay) {
    let timer;
    const debounced = function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
    debounced.cancel = () => clearTimeout(timer);
    return debounced;
}

// Tanggal ISO (YYYY-MM-DD) menjadi "bulan tahun" sesuai bahasa aktif.
function formatMonthYear(isoDate) {
    if (!isoDate) return '';
    const lang = window.I18N ? window.I18N.lang : 'en';
    const date = new Date(isoDate + 'T00:00:00Z');
    if (Number.isNaN(date.getTime())) return '';
    return date.toLocaleDateString(lang === 'id' ? 'id-ID' : 'en-US', {
        month: 'short', year: 'numeric', timeZone: 'UTC',
    });
}