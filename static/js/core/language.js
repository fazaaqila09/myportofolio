// Ganti bahasa ID/EN. Kamusnya ada di translations.js (harus dimuat lebih dulu).
//
// Atribut di template:
//   data-i18n="kunci"                         ganti teks elemen
//   data-i18n-html="kunci"                    ganti isi HTML (hanya dari kamus sendiri)
//   data-i18n-attr="placeholder:kunci;..."    ganti atribut
//   data-i18n-auto                            teks dari server, dicari di serverText
//   data-id-text="teks Indonesia"             isi database; teks Inggris ada di elemen
//
// Dipakai skrip lain: I18N.t(), t(), I18N.auto(), I18N.field(), event "langchange".
// Pilihan disimpan di localStorage ("lang"); kunjungan pertama mengikuti bahasa browser.
(function () {
    'use strict';

    var STORE_KEY = 'lang';
    var WORDS = { en: window.TRANSLATIONS.en, id: window.TRANSLATIONS.id };

    // Peta dua arah untuk teks dari server: hasilnya selalu mengikuti bahasa aktif
    var TO_ID = {}, TO_EN = {};
    window.TRANSLATIONS.serverText.forEach(function (pair) {
        TO_ID[pair[0]] = pair[1]; TO_ID[pair[1]] = pair[1];
        TO_EN[pair[1]] = pair[0]; TO_EN[pair[0]] = pair[0];
    });

    function detect() {
        try {
            var saved = localStorage.getItem(STORE_KEY);
            if (saved === 'id' || saved === 'en') return saved;
        } catch (e) { /* abaikan */ }
        var browser = (navigator.language || 'en').toLowerCase();
        return browser.indexOf('id') === 0 ? 'id' : 'en';
    }
    var lang = detect();
    document.documentElement.setAttribute('lang', lang);   // sebelum halaman tampil, agar tidak berkedip

    // Isi kamus untuk kunci; bila tidak ada di bahasa aktif, pakai bahasa Inggris
    function raw(key) {
        var v = WORDS[lang][key];
        if (v === undefined) v = WORDS.en[key];
        return v;
    }
    // t(kunci, cadangan): cadangan dipakai bila kunci tidak ada di kamus
    function t(key, fallback) {
        var v = raw(key);
        if (v !== undefined) return v;
        return fallback !== undefined ? fallback : key;
    }
    // Terjemahan teks dari server (pesan, kategori); teks yang tidak dikenal dibiarkan
    function auto(text) {
        var clean = String(text == null ? '' : text).trim();
        var map = lang === 'id' ? TO_ID : TO_EN;
        return map.hasOwnProperty(clean) ? map[clean] : text;
    }
    // Data dari database: pakai versi Indonesia bila ada
    function field(en, id) {
        return (lang === 'id' && id) ? id : en;
    }

    function apply(scope) {
        var root = scope || document;

        root.querySelectorAll('[data-i18n]').forEach(function (el) {
            if (el.dataset.i18nOrig === undefined) el.dataset.i18nOrig = el.textContent;
            var v = raw(el.dataset.i18n);
            el.textContent = v === undefined ? el.dataset.i18nOrig : v;
        });

        root.querySelectorAll('[data-i18n-html]').forEach(function (el) {
            if (el.dataset.i18nOrig === undefined) el.dataset.i18nOrig = el.innerHTML;
            var v = raw(el.dataset.i18nHtml);
            el.innerHTML = v === undefined ? el.dataset.i18nOrig : v;
        });

        root.querySelectorAll('[data-i18n-auto]').forEach(function (el) {
            if (el.dataset.i18nOrig === undefined) el.dataset.i18nOrig = el.textContent;
            el.textContent = auto(el.dataset.i18nOrig);
        });

        root.querySelectorAll('[data-id-text]').forEach(function (el) {
            if (el.dataset.enText === undefined) el.dataset.enText = el.textContent;
            el.textContent = field(el.dataset.enText, el.dataset.idText);
        });

        root.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
            el.dataset.i18nAttr.split(';').forEach(function (pair) {
                var parts = pair.split(':');
                if (parts.length !== 2) return;
                var v = raw(parts[1].trim());
                if (v !== undefined) el.setAttribute(parts[0].trim(), v);
            });
        });

        var toggle = document.querySelector('[data-lang-toggle]');
        if (toggle) toggle.setAttribute('data-lang', lang);
    }

    function setLang(next, remember) {
        if (next !== 'id' && next !== 'en') return;
        lang = next;
        document.documentElement.setAttribute('lang', lang);
        if (remember !== false) { try { localStorage.setItem(STORE_KEY, lang); } catch (e) { /* abaikan */ } }
        apply();
        document.dispatchEvent(new CustomEvent('langchange', { detail: { lang: lang } }));
    }

    window.I18N = {
        t: t,
        field: field,
        get: raw,
        auto: auto,
        apply: apply,
        set: setLang,
        get lang() { return lang; }
    };
    window.t = t;

    function init() {
        var toggle = document.querySelector('[data-lang-toggle]');
        if (toggle) {
            toggle.addEventListener('click', function () { setLang(lang === 'id' ? 'en' : 'id'); });
        }
        apply();
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
