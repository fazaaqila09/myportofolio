/* ============================================================
   I18N.JS: toggle bahasa Indonesia (ID) / Inggris (EN).

   Cara kerja:
   - Teks yang bisa diterjemahkan diberi atribut di template:
       data-i18n="kunci"                  -> mengganti teks elemen
       data-i18n-html="kunci"             -> mengganti isi HTML elemen (hanya dari kamus ini)
       data-i18n-attr="placeholder:kunci;aria-label:kunci2"   -> mengganti atribut
       data-i18n-auto                     -> teks dari server/database dicari di daftar AUTO
   - Teks asli di HTML = bahasa Inggris (kecuali beberapa label yang memang
     sudah Indonesia). Kalau kunci tidak ada di kamus, teks aslinya dibiarkan.
   - Pilihan bahasa disimpan di localStorage ("lang"); kunjungan pertama
     mengikuti bahasa browser (id* -> ID, selain itu -> EN).
   - Dipakai skrip lain: window.I18N.t('kunci'), window.t('kunci'),
     window.I18N.auto('teks'), dan event "langchange" di document.

   Catatan: isi yang ditulis pemilik di database (deskripsi experience,
   nama/deskripsi project, jurusan) tidak ikut diterjemahkan otomatis.
   ============================================================ */
(function () {
    'use strict';

    var STORE_KEY = 'lang';

    /* ---------- Kamus ---------- */
    var DICT = {
        en: {
            'lang.switch': 'Switch language',

            'nav.home': 'Home', 'nav.about': 'About', 'nav.skills': 'Skills', 'nav.education': 'Education',
            'nav.experience': 'Experience', 'nav.projects': 'Projects', 'nav.contact': 'Contact',
            'nav.login': 'Login', 'nav.logout': 'Logout', 'nav.inbox': 'Inbox',

            'footer.tagline': 'Computer Science student at Universitas Indonesia, interested in Data Science and Web Development.',
            'footer.explore': 'Explore', 'footer.connect': 'Connect', 'footer.cta': 'Get in touch',
            'footer.copy': '© 2026 Muhammad Faza Aqila. Faculty of Computer Science, Universitas Indonesia.',

            'hero.greeting': 'Hello I am',
            'hero.connect': "LET'S CONNECT",
            'hero.exploring': 'Currently exploring',
            'hero.words': ['Data Science', 'Web Development', 'Django Projects', 'Clean UI Design'],

            'about.title': 'About Me',
            'about.name': 'Name', 'about.from': 'From', 'about.npm': 'ID Student',
            'about.lastlogin': 'Last Login Session',
            'about.cv': 'Download CV',

            'skills.title': 'Skills & Tech Stack',
            'skills.sub': 'Tools and technologies I use to build things',
            'skills.languages': 'Languages',
            'skills.frameworks': 'Frameworks & Libraries',
            'skills.tools': 'Tools & Platforms',
            'skills.note': 'Always curious, always picking up new tools along the way.',

            'edu.title': 'Education',
            'edu.sub': "Where I've studied, learned, and grown",
            'edu.empty': 'No education history has been added yet.',

            'common.present': 'Present',
            'common.search': 'Search',

            'exp.title': 'Experience',
            'exp.sub': "Where I've led, served, and contributed",
            'exp.add': 'Add Experience',
            'exp.search.ph': 'Search by organization/activity name',
            'exp.search.label': 'Search experience',
            'exp.ongoing': 'Ongoing', 'exp.completed': 'Completed',
            'exp.none.found': 'No experience found with that name.',
            'exp.none.yet': 'No experience added yet.',

            'star.star': 'Star', 'star.unstar': 'Unstar',

            'proj.title': 'Projects',
            'proj.sub': "Things I've built, filmed, and created",
            'proj.add': 'Add Project',
            'proj.search.ph': 'Search by title or description',
            'proj.search.label': 'Search projects',
            'proj.filter': 'Filter by category',
            'proj.showing.a': 'Showing', 'proj.showing.b': 'of', 'proj.showing.c': 'projects',
            'proj.error': 'Failed to load projects. Please try again.',
            'proj.more': 'Load more',
            'proj.view': 'View Project',
            'proj.all': 'All',
            'proj.confirm.delete': 'Are you sure you want to delete this project?',
            'proj.empty.search': 'No projects match your search.',
            'proj.empty.none': 'No projects added yet — click "Add Project" to add your first one.',
            'proj.empty.category': 'No projects in this category.',

            'toast.ok': 'Success',
            'toast.proj.added': 'New project added successfully!',
            'toast.proj.fail': 'Failed to add project',
            'toast.network': 'Could not reach the server. Please try again.',
            'toast.star.fail': 'Failed to change star',

            'fab.theme': 'Toggle light/dark theme',
            'fab.top': 'Back to top',
            'fab.toLight': 'Switch to light theme',
            'fab.toDark': 'Switch to dark theme',

            'contact.title': 'Contact',
            'contact.sub': 'Got a question, a project idea, or just want to say hi? Send me a message.',
            'contact.info.title': "Let's talk",
            'contact.info.text': 'I usually reply within a few days. You can also reach me through the channels below.',
            'contact.email': 'Email', 'contact.location': 'Location',
            'contact.f.name': 'Name', 'contact.f.email': 'Email',
            'contact.f.subject': 'Subject', 'contact.f.message': 'Message',
            'contact.ph.name': 'Your name',
            'contact.ph.subject': 'What is this about?',
            'contact.ph.message': 'Write your message here...',
            'contact.send': 'Send Message',
            'contact.sending': 'Sending...',
            // Inbox (khusus pemilik)
            'inbox.title': 'Inbox',
            'inbox.sub': 'Messages sent through the Contact form',
            'inbox.filter.all': 'All', 'inbox.filter.unread': 'Unread', 'inbox.filter.read': 'Read',
            'inbox.search.ph': 'Search name, email, or message',
            'inbox.search.label': 'Search messages',
            'inbox.markall': 'Mark all as read',
            'inbox.mark.read': 'Mark as read', 'inbox.mark.unread': 'Mark as unread',
            'inbox.reply': 'Reply by email',
            'inbox.delete': 'Delete',
            'inbox.delete.title': 'Delete message?',
            'inbox.delete.text': 'This message will be permanently deleted.',
            'inbox.delete.cancel': 'Cancel', 'inbox.delete.confirm': 'Yes, Delete',
            'inbox.empty': 'Your inbox is empty. Messages from the Contact form will show up here.',
            'inbox.empty.filter': 'No messages match.',
            'inbox.prev': 'Previous', 'inbox.next': 'Next',
            // Lightbox foto
            'lb.label': 'Photo viewer', 'lb.close': 'Close',
            'lb.prev': 'Previous photo', 'lb.next': 'Next photo',
            'lb.enlarge': 'Enlarge photo', 'lb.enlarge.short': 'Enlarge',
            'lb.hint.switch': 'switch photo', 'lb.hint.close': 'close'
        },

        id: {
            'lang.switch': 'Ganti bahasa',

            'nav.home': 'Beranda', 'nav.about': 'Tentang', 'nav.skills': 'Keahlian', 'nav.education': 'Pendidikan',
            'nav.experience': 'Pengalaman', 'nav.projects': 'Proyek', 'nav.contact': 'Kontak',
            'nav.login': 'Masuk', 'nav.logout': 'Keluar', 'nav.inbox': 'Kotak Masuk',

            'footer.tagline': 'Mahasiswa Computer Science di Universitas Indonesia, tertarik pada Data Science dan Web Development.',
            'footer.explore': 'Jelajahi', 'footer.connect': 'Terhubung', 'footer.cta': 'Hubungi saya',
            'footer.copy': '© 2026 Muhammad Faza Aqila. Fakultas Ilmu Komputer, Universitas Indonesia.',

            'hero.greeting': 'Halo, saya',
            'hero.subtitle': 'Mahasiswa Computer Science di Universitas Indonesia, tertarik pada Data Science dan Web Development',
            'hero.connect': 'MARI TERHUBUNG',
            'hero.exploring': 'Sedang mendalami',
            'hero.words': ['Data Science', 'Pengembangan Web', 'Proyek Django', 'Desain UI yang Rapi'],

            'about.title': 'Tentang Saya',
            'about.bio': 'Halo! Saya Muhammad Faza Aqila, mahasiswa S1 Ilmu Komputer di Universitas Indonesia. ' +
                'Minat utama saya berada di persimpangan antara Data Science dan Web Development modern. ' +
                'Saya antusias menggali wawasan bermakna dari data mentah yang kompleks untuk mendukung keputusan yang tepat, ' +
                'lalu menerjemahkan temuan tersebut menjadi aplikasi web yang intuitif dan ramah pengguna.',
            'about.name': 'Nama', 'about.from': 'Asal', 'about.npm': 'NPM',
            'about.lastlogin': 'Sesi Terakhir Login',
            'about.cv': 'Unduh CV',

            'skills.title': 'Keahlian & Tech Stack',
            'skills.sub': 'Alat dan teknologi yang saya pakai untuk membangun berbagai hal',
            'skills.languages': 'Bahasa Pemrograman',
            'skills.frameworks': 'Framework & Library',
            'skills.tools': 'Alat & Platform',
            'skills.note': 'Selalu penasaran dan terus belajar alat-alat baru.',

            'edu.title': 'Pendidikan',
            'edu.sub': 'Tempat saya belajar, memperdalam ilmu, dan berkembang',
            'edu.empty': 'Belum ada riwayat pendidikan yang ditambahkan.',

            'common.present': 'Sekarang',
            'common.search': 'Cari',

            'exp.title': 'Pengalaman',
            'exp.sub': 'Tempat saya memimpin, mengabdi, dan berkontribusi',
            'exp.add': 'Tambah Pengalaman',
            'exp.search.ph': 'Cari berdasarkan nama organisasi/kegiatan',
            'exp.search.label': 'Cari pengalaman',
            'exp.ongoing': 'Berlangsung', 'exp.completed': 'Selesai',
            'exp.none.found': 'Tidak ada pengalaman dengan nama tersebut.',
            'exp.none.yet': 'Belum ada pengalaman yang ditambahkan.',

            'star.star': 'Star', 'star.unstar': 'Batal Star',

            'proj.title': 'Proyek',
            'proj.sub': 'Hal-hal yang telah saya bangun, filmkan, dan ciptakan',
            'proj.add': 'Tambah Proyek',
            'proj.search.ph': 'Cari berdasarkan judul atau deskripsi',
            'proj.search.label': 'Cari proyek',
            'proj.filter': 'Filter kategori',
            'proj.showing.a': 'Menampilkan', 'proj.showing.b': 'dari', 'proj.showing.c': 'proyek',
            'proj.error': 'Gagal memuat proyek. Silakan coba lagi.',
            'proj.more': 'Muat lebih banyak',
            'proj.view': 'Lihat Proyek',
            'proj.all': 'Semua',
            'proj.confirm.delete': 'Yakin ingin menghapus project ini?',
            'proj.empty.search': 'Tidak ada proyek yang cocok dengan pencarian.',
            'proj.empty.none': 'Belum ada proyek — klik "Tambah Proyek" untuk menambahkan yang pertama.',
            'proj.empty.category': 'Tidak ada proyek di kategori ini.',

            'toast.ok': 'Berhasil',
            'toast.proj.added': 'Proyek baru berhasil ditambahkan!',
            'toast.proj.fail': 'Gagal menambahkan proyek',
            'toast.network': 'Tidak dapat terhubung ke server. Silakan coba lagi.',
            'toast.star.fail': 'Gagal mengubah star',

            'fab.theme': 'Ganti tema terang/gelap',
            'fab.top': 'Kembali ke atas',
            'fab.toLight': 'Beralih ke tema terang',
            'fab.toDark': 'Beralih ke tema gelap',

            'contact.title': 'Kontak',
            'contact.sub': 'Punya pertanyaan, ide proyek, atau sekadar ingin menyapa? Kirim pesan kepada saya.',
            'contact.info.title': 'Ayo ngobrol',
            'contact.info.text': 'Biasanya saya membalas dalam beberapa hari. Anda juga bisa menghubungi saya lewat kanal di bawah ini.',
            'contact.email': 'Email', 'contact.location': 'Lokasi',
            'contact.f.name': 'Nama', 'contact.f.email': 'Email',
            'contact.f.subject': 'Subjek', 'contact.f.message': 'Pesan',
            'contact.ph.name': 'Nama Anda',
            'contact.ph.subject': 'Tentang apa ini?',
            'contact.ph.message': 'Tulis pesan Anda di sini...',
            'contact.send': 'Kirim Pesan',
            'contact.sending': 'Mengirim...',
            // Inbox (khusus pemilik)
            'inbox.title': 'Kotak Masuk',
            'inbox.sub': 'Pesan yang dikirim lewat formulir Contact',
            'inbox.filter.all': 'Semua', 'inbox.filter.unread': 'Belum dibaca', 'inbox.filter.read': 'Sudah dibaca',
            'inbox.search.ph': 'Cari nama, email, atau pesan',
            'inbox.search.label': 'Cari pesan',
            'inbox.markall': 'Tandai semua dibaca',
            'inbox.mark.read': 'Tandai dibaca', 'inbox.mark.unread': 'Tandai belum dibaca',
            'inbox.reply': 'Balas lewat email',
            'inbox.delete': 'Hapus',
            'inbox.delete.title': 'Hapus pesan?',
            'inbox.delete.text': 'Pesan ini akan dihapus permanen.',
            'inbox.delete.cancel': 'Batal', 'inbox.delete.confirm': 'Ya, Hapus',
            'inbox.empty': 'Kotak masuk masih kosong. Pesan dari formulir Contact akan muncul di sini.',
            'inbox.empty.filter': 'Tidak ada pesan yang cocok.',
            'inbox.prev': 'Sebelumnya', 'inbox.next': 'Berikutnya',
            // Lightbox foto
            'lb.label': 'Penampil foto', 'lb.close': 'Tutup',
            'lb.prev': 'Foto sebelumnya', 'lb.next': 'Foto berikutnya',
            'lb.enlarge': 'Perbesar foto', 'lb.enlarge.short': 'Perbesar',
            'lb.hint.switch': 'pindah foto', 'lb.hint.close': 'tutup'
        }
    };

    /* ---------- Teks dari server/database: pasangan [Inggris, Indonesia] ----------
       Dipakai oleh elemen data-i18n-auto. Dua arah: teks asli boleh bahasa
       Inggris atau Indonesia, hasilnya selalu mengikuti bahasa yang aktif. */
    var AUTO_PAIRS = [
        // kategori Experience
        ['Organization', 'Organisasi'], ['Committee', 'Kepanitiaan'], ['Volunteer', 'Relawan'],
        ['Part-Time', 'Paruh Waktu'], ['Full-Time', 'Penuh Waktu'], ['Internship', 'Magang'],
        // kategori Project
        ['Film & Video', 'Film & Video'], ['Software / Web', 'Software / Web'], ['Design', 'Desain'],
        ['Writing', 'Tulisan'], ['Music / Audio', 'Musik / Audio'], ['Other', 'Lainnya'],
        // pesan dari server (django messages)
        ['New experience added successfully!', 'Pengalaman baru berhasil ditambahkan!'],
        ['Experience updated successfully!', 'Pengalaman berhasil diperbarui!'],
        ['Experience deleted successfully!', 'Pengalaman berhasil dihapus!'],
        ['New project added successfully!', 'Proyek baru berhasil ditambahkan!'],
        ['Project updated successfully!', 'Proyek berhasil diperbarui!'],
        ['Project deleted successfully!', 'Proyek berhasil dihapus!'],
        ['Account created. Please log in.', 'Akun berhasil dibuat. Silakan login.'],
        // Contact
        ['All messages marked as read.', 'Semua pesan ditandai sudah dibaca.'],
        ['Message deleted.', 'Pesan dihapus.'],
        ['Thank you! Your message has been sent.', 'Terima kasih! Pesan Anda sudah terkirim.'],
        ['Please wait a moment before sending another message.', 'Mohon tunggu sebentar sebelum mengirim pesan lagi.'],
        ['Please enter your name.', 'Silakan isi nama Anda.'],
        ['Please enter your email address.', 'Silakan isi alamat email Anda.'],
        ['Please enter a valid email address.', 'Masukkan alamat email yang valid.'],
        ['Please enter a subject.', 'Silakan isi subjek.'],
        ['Please write a message.', 'Silakan tulis pesan Anda.'],
        ['Your message is too short.', 'Pesan Anda terlalu pendek.'],
        ['This is too long.', 'Terlalu panjang.'],
        // About
        ['No login session yet / Cookie not found', 'Belum ada sesi login / Cookie tidak ditemukan']
    ];
    var TO_ID = {}, TO_EN = {};
    AUTO_PAIRS.forEach(function (pair) {
        TO_ID[pair[0]] = pair[1]; TO_ID[pair[1]] = pair[1];
        TO_EN[pair[1]] = pair[0]; TO_EN[pair[0]] = pair[0];
    });

    /* ---------- Bahasa aktif ---------- */
    function detect() {
        try {
            var saved = localStorage.getItem(STORE_KEY);
            if (saved === 'id' || saved === 'en') return saved;
        } catch (e) { /* abaikan */ }
        var nav = (navigator.language || 'en').toLowerCase();
        return nav.indexOf('id') === 0 ? 'id' : 'en';
    }
    var lang = detect();
    document.documentElement.setAttribute('lang', lang);

    function raw(key) {
        var v = DICT[lang][key];
        if (v === undefined) v = DICT.en[key];
        return v;
    }
    // t(kunci, cadangan): cadangan dipakai bila kunci tidak ada di kamus
    function t(key, fallback) {
        var v = raw(key);
        if (v !== undefined) return v;
        return fallback !== undefined ? fallback : key;
    }
    function auto(text) {
        var clean = String(text == null ? '' : text).trim();
        var map = lang === 'id' ? TO_ID : TO_EN;
        return map.hasOwnProperty(clean) ? map[clean] : text;
    }

    /* ---------- Menerapkan terjemahan ke halaman ---------- */
    function apply(scope) {
        var root = scope || document;

        root.querySelectorAll('[data-i18n]').forEach(function (el) {
            if (el.dataset.i18nOrig === undefined) el.dataset.i18nOrig = el.textContent;
            var v = DICT[lang][el.dataset.i18n];
            if (v === undefined) v = DICT.en[el.dataset.i18n];
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

        // Isi dari database: teks Inggris ada di elemen, terjemahan Indonesia di data-id-text.
        // Bila terjemahan kosong, teks Inggris tetap dipakai.
        root.querySelectorAll('[data-id-text]').forEach(function (el) {
            if (el.dataset.enText === undefined) el.dataset.enText = el.textContent;
            var idText = el.dataset.idText;
            el.textContent = (lang === 'id' && idText) ? idText : el.dataset.enText;
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

    // field(en, id): pilih teks sesuai bahasa untuk data dari database (id kosong -> en)
    function field(en, id) {
        return (lang === 'id' && id) ? id : en;
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