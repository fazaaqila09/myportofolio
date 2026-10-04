Nama : Muhammad Faza Aqila

NPM : 2506613142

Kelas : PBP C

### Tugas 1

1. Ya, saya menerapkan elemen semantik HTML5 pada berkas index.html. Tag nav digunakan untuk mempermudah identifikasi blok navigasi utama bagi screen reader. Tag section untuk memisahkan area konten utama seperti About, Education, dan Experience, serta secara spesifik memakai tag article untuk membungkus setiap kartu riwayat organisasi karena informasinya bersifat mandiri. Selain membuat struktur kode jauh lebih terbaca dibandingkan tumpukan div generik, elemen ini memperjelas hierarki halaman. Saya juga menggunakan Description List (dl, dt, dd) di bagian About karena sangat tepat secara semantik untuk merelasikan pasangan data profil, seperti Nama dan Umur.

2. Tantangan tata letak terbesar saat menyusun style.css adalah menjaga proporsi elemen berdampingan agar tidak saling bertabrakan atau terpotong saat layar menyempit. Pada tampilan desktop, area Hero menggunakan tata letak flexbox horizontal dengan teks di kiri dan foto di kanan. Saat berpindah ke mobile, saya memprioritaskan keterbacaan teks dan proporsi foto. Solusinya adalah dengan mengubah alur menjadi vertikal (flex-direction: column-reverse) dan mengubah perataan teks menjadi menengah (text-align: center) supaya visual tetap terjaga.

3. Batasan paling utama dari static web murni adalah kekakuan dalam membuat interaksi dan animasi visual yang kompleks dan tidak ada interaksi dua arah. Setiap kali ada penambahan riwayat pengalaman atau pendidikan baru, saya harus mengubah hardcode di dalam HTML dan melakukan redeployment secara manual. Selain itu, *user* saat ini hanya bisa menghubungi melalui tautan eksternal mailto: karena web belum bisa memproses input pengguna secara mandiri. Pada proyek selanjutnya, fungsionalitas dinamis yang ingin dtambahkan adalah integrasi database menggunakan arsitektur MVT dan implementasi JavaScript untuk menghidupkan *user interface*. Dengan JavaScript, saya bisa memanfaatkan API Intersection Observer atau library animasi untuk merancang transisi web yang jauh lebih interaktif. Serta, ingin membuat panel admin untuk mengelola (CRUD) entri pengalaman secara dinamis.

### Disclosure AI

**Alat:** Claude.

**Link percakapan AI:** https://claude.ai/share/9c19c5fc-6c9d-4e80-b794-ba0a07ab0ec5

**Bagian yang dibantu:** Pembuatan boilerplate HTML, perhitungan koordinat matematis untuk bentuk SVG latar belakang gelombang kustom, dan penyusunan logika awal rentang @keyframes untuk animasi masuk berurutan.

**Keterbatasan AI dan Perbaikan Manual:**
Selama menggunakan AI sebagai teman berpikir, saya menemukan bahwa AI sangat payah dalam memahami rendering visual secara spasial di browser. AI hanya membaca teks dan memberikan logika yang secara sintaksis benar, tapi secara visual merusak layout. Ada beberapa edge-cases krusial yang gagal ditangani AI dan memaksa saya melakukan perombakan manual:

    1. Glitch Pemotongan Teks dan Bayangan: Saat membuat animasi teks reveal, AI memberikan instruksi clip-path: inset(0 0 0 0). ketika dirender, ekor huruf 'q' pada "Aqila" dan bayangan (box-shadow) pada foto profil terpotong paksa oleh garis batas clip-path. Debugging manual: Menyisipkan area bleed negatif menjadi inset(-20% -20% -20% -20%) pada teks. Untuk foto, membuang metode AI sepenuhnya dan menulis ulang animasinya murni menggunakan transform: translateY dan scale agar bayangan meluncur utuh.

    2. Gap Putih pada SVG Wave: Saya meminta AI menggerakkan latar belakang ombak agar seolah menukik ke bawah. AI menyarankan transform: translateY(35px). Akibatnya, seluruh kotak gelombang turun dan meninggalkan celah putih kosong yang jelek di atap layar. Debugging manual: Menggunakan peregangan elastis transform: scaleY(1.35) dengan titik tumpu transform-origin: top center. Ini menahan ujung atas ombak tetap menempel di atap, sementara bagian bawahnya memanjang realistis.

### Tugas 2
1. Prosesnya mulai waktu user memasukkan URL, misalnya /education/, di peramban. Request ini bakal ditangkap duluan sama urls.py bawaan project utama, yang tugasnya melempar rute itu ke urls.py level app (seperti aplikasi main) pakai fungsi include(). Di app urls.py, URL tadi dicocokkan lagi untuk mencari fungsi View mana yang pas untuk menangani request-nya. Setelah ketemu, View ini bakal bertugas sebagai otak yang mengambil data riwayat pendidikan dari database lewat bantuan Model. Terakhir, View membungkus data itu ke dalam context dan me- render Template (berkas HTML) supaya gabung menjadi halaman utuh yang akhirnya ditampilkan di browser.

2. Alasan utamanya supaya lebih gampang saat harus maintenance dan mengembangkan webnya ke depan. Kalau datanya di-hardcode di HTML, tiap kali kita mau menambah riwayat sekolah atau pengalaman baru, kita harus membongkar ulang berkas HTML-nya secara manual. Tapi kalau menggunakan Model, kode HTML murni cuma dijadikan cetakan presentasi visual (kerangka) saja. Kita bisa bebas menambah, mengedit, atau menghapus data riwayat kapan saja lewat database (misalnya lewat Django Admin atau shell) tanpa perlu takut merusak susunan tag codingan tampilan webnya.

3. Makemigrations itu ibarat menyuruh Django untuk membuat draf atau catatan tentang perubahan apa saja yang barusan dilakukan di berkas Python (seperti di models.py), tapi perintah ini belum mengubah isi database sama sekali. Nah, kalau migrate, itu tahap eksekusinya—dia akan membaca draf tadi dan benar-benar mengubah struktur tabel fisik di dalam database sungguhan.
Contoh: misalnya di model Education mau menambah kolom baru, seperti logo = models.URLField(). Maka wajib menjalankan makemigrations dulu biar Django mencatat rencana penambahan ini, baru setelah itu menjalankan migrate agar kolom logonya sungguhan dibuat di tabel database.

### Disclosure AI

**Alat:** Claude.

**Link percakapan AI:** https://claude.ai/share/9c19c5fc-6c9d-4e80-b794-ba0a07ab0ec5

**Bagian yang dibantu:** Mencari ide struktur MVT untuk model Education, membuat desain timeline vertikal menggunakan HTML/CSS, membuat skrip pengisian data otomatis (auto-populate), serta menyusun kerangka awal untuk unit test.

**Keterbatasan AI dan Perbaikan Manual:**
Sama seperti tugas sebelumnya, AI sangat efisien untuk membuat kerangka kode, tapi sering kali kurang paham dengan flow atau logika sistem secara keseluruhan. Pada tugas 2 ini, saya menemukan kode dari AI justru memicu error dan mengharuskan saya melakukan troubleshoot manual:

    1. Konteks Database Lokal (Broken Image): Saat mengganti logo dari ekstensi .jpg menjadi .png, AI menyarankan untuk sekadar mengubah teks rutenya di dalam skrip views.py. Secara sintaks itu benar, tapi saat dijalankan, gambar logonya tetap pecah (hilang). AI tidak menyadari bahwa data dengan format lama sudah terlanjur tersimpan di dalam database lokal db.sqlite3 milik saya, dan perubahan skrip AI tersebut tidak akan tereksekusi karena tabelnya tidak dalam keadaan kosong. Perbaikan manual: Saya menyadari masalah state ini, lalu menghapus sendiri berkas db.sqlite3 lokal saya dan melakukan migrate ulang dari nol agar skrip barunya bisa menyuntikkan path gambar yang benar.

### Tugas 3
1. Penggunaan ModelForm jauh lebih praktis karena Django otomatis membuatkan elemen input, label, dan aturan validasi langsung dari struktur model yang sudah ada. Hal ini menghemat waktu dan mencegah ketidaksinkronan antara form HTML dan database. Sementara itu, tag {% csrf_token %} wajib ditambahkan untuk mengamankan form POST dari serangan CSRF (Cross-Site Request Forgery). Token ini memastikan bahwa request yang masuk benar-benar berasal dari aksi pengguna sah di situs kita, bukan dari situs peretas.

2. JSON jauh lebih disukai dalam web modern karena strukturnya lebih ringkas dan ringan. Berbeda dengan XML yang boros karakter karena membutuhkan tag pembuka dan penutup untuk setiap data, JSON hanya menggunakan pasangan key-value. Selain itu, format JSON langsung sepadan dengan struktur dictionary di Python dan objek di JavaScript, sehingga datanya bisa langsung dibaca dan diolah tanpa perlu parser yang rumit.

3. Saat browser meminta data, URL akan meneruskannya ke fungsi view. View kemudian mengambil data dari database yang masih berbentuk objek Python / QuerySet. Karena protokol HTTP hanya bisa mengirim format teks atau byte, data objek ini tidak bisa dikirim mentah-mentah. Di sinilah proses serialisasi diperlukan untuk menerjemahkan objek Python tersebut, termasuk tipe data khusus seperti tanggal menjadi format string teks JSON standar. Setelah menjadi JSON, barulah data dibungkus menjadi response dan dikirim ke browser.

### Disclosure AI

**Alat:** Claude.

**Link percakapan AI:** https://claude.ai/share/a86a498f-a8be-4065-a790-dcebc10847f3

**Strategi Prompting:** Pengerjaan dilakukan secara iteratif dengan prompt pendek. Karena AI tidak bisa melihat hasil layar, screenshot browser selalu dilampirkan sebagai umpan balik. Jika ada keputusan desain, saran ditanyakan terlebih dahulu. Apabila kode dari AI terasa berlebihan atau rumit, instruksi untuk menyederhanakan dan mengembalikan ke kode awal langsung diberikan.

**Bagian yang dibantu:** Membangun section baru untuk "Projects" lengkap dengan fitur CRUD, serta merancang desain card yang memuat foto/logo, nama proyek, posisi, hingga deskripsinya.

**Keterbatasan AI dan Perbaikan Manual:** AI cepat untuk membuat kerangka kode, tetapi tidak bisa melihat browser maupun server saya, sehingga beberapa hasilnya baru ketahuan bermasalah setelah saya coba sendiri:

    1. Jarak ke Footer dan Cache CSS: Saat saya meminta konten halaman Add Project tidak menempel ke footer, AI menambahkan padding bawah lewat aturan .projects di style.css. Ketika dijalankan di browser saya, tampilannya tidak berubah karena browser masih memakai CSS lama, dan AI tidak bisa melihat hasil render untuk menyadarinya. Debugging manual: Memasang padding langsung di tag <section> pada halaman form "padding: 130px 0 80px; min-height: 100vh; box-sizing: border-box;" dan melakukan refresh supaya CSS terbaru terbaca.

    2. Pencarian Berdasarkan Kategori: Pencarian awal pada halaman Projects mencocokkan kata yang diketik dengan nilai yang tersimpan di database atau berdasarkan kategori, bukan label yang tampil di card (Film & Video), sehingga mengetik label yang terlihat tidak menemukan hasil. Debugging manual: Mengganti pencarian menjadi berdasarkan judul dan deskripsi "Q(title__icontains=...) | Q(description__icontains=...)", lalu mencobanya sendiri di browser.

### Tugas 4

Pada Tugas 4 tidak ada pertanyaan reflektif (dihilangkan untuk pekan ini), jadi bagian ini berisi ringkasan fitur dan cara menjalankan proyek.

**Fitur yang ditambahkan**
- Registrasi, login, dan logout memakai sistem autentikasi bawaan Django (`UserCreationForm` dan `AuthenticationForm`), dengan username akun ditampilkan di navbar.
- Cookie `last_login` dibuat saat login dan dihapus saat logout, lalu ditampilkan di halaman profil sebagai "Sesi Terakhir Login".
- Empat peran dengan hak akses berikut. Peran Editor dibuat lewat Django Group bernama `Editor` di Django Admin.

| Peran | Lihat data | Star | Edit | Tambah / Hapus |
|---|---|---|---|---|
| Pengunjung (belum login) | Ya | Tidak (diarahkan ke login) | Tidak | Tidak |
| Pengguna biasa | Ya | Ya | Tidak | Tidak |
| Editor | Ya | Ya | Ya | Tidak |
| Pemilik (superuser) | Ya | Ya | Ya | Ya |

- Pemeriksaan hak akses dilakukan di sisi server dengan `@login_required` (pengunjung diarahkan ke halaman login) dan `PermissionDenied` (HTTP 403 untuk aksi yang tidak diizinkan). Tombol tambah, edit, dan hapus di template disembunyikan sesuai peran.
- Fitur star memakai `ManyToManyField` ke `User` pada model `Experience` dan `Project` (migrasi `0008` dan `0009`). View `toggle_star` dan `toggle_star_experience` hanya mengubah data lewat POST dengan `{% csrf_token %}`, dan maksimal satu star per pengguna. Jumlah star dan status pengguna ditampilkan pada tombol.
- Endpoint JSON `/api/experience/` dan `/api/projects/` tetap berfungsi. Field `starred_by` diserialisasi dengan `use_natural_foreign_keys=True` sehingga berisi username, bukan id database, dan tidak ada data sensitif yang ikut keluar.
- Sistem Access Code dari Tugas 3 dihapus karena sudah digantikan login dan peran.
- Test otomatis ditambahkan untuk hak akses tiap peran, visibilitas tombol, dan fitur star.

### Disclosure AI

**Alat:** Claude.

**Link percakapan AI:** https://claude.ai/share/dab33ecf-9da1-49d6-a18c-f6e53409dc3f

**Strategi Prompting:** Pengerjaan dilakukan secara iteratif. Saya mengunggah PDF tutorial dan tugas beserta ZIP project supaya AI bisa membaca kode saya, lalu meminta panduan langkah demi langkah dengan kode yang bisa langsung di-copy-paste. Ketika terjadi error, saya melampirkan screenshot atau output terminal (misalnya `NameError` dan hasil `python manage.py test`) supaya AI bisa menunjuk bagian yang salah, kemudian mengunggah project yang sudah saya perbarui untuk diperiksa ulang.

**Bagian yang dibantu:** Menyusun panduan Tutorial 04 (register, login, logout, cookie `last_login`, dan otorisasi), merancang peran Editor lewat Django Group, pembatasan hak akses di sisi server, fitur star pada Experience dan Projects, penyesuaian endpoint JSON, penulisan test untuk tiap peran, serta panduan Git dan penyusunan README ini.

**Keterbatasan AI dan Perbaikan Manual:** AI cepat menyusun kode dan langkah kerja, tetapi tidak bisa menjalankan proyek di laptop saya, sehingga beberapa masalah baru ketahuan setelah saya coba sendiri:

    1. Kode Contoh Tidak Cocok dengan Project: Kode di PDF menulis `datetime.datetime.now()` untuk cookie `last_login`, padahal `views.py` saya sudah memakai `from datetime import date, datetime`, sehingga kode itu akan error. CSS tombol star di PDF juga memakai variabel `--ink` dan `--accent` yang tidak ada di `style.css` saya. Perbaikan manual: memakai `datetime.now()` dan mengganti warna tombol dengan palet biru-kuning yang sudah dipakai di website.

    2. Access Code Bertabrakan dengan Login: Sistem Access Code dari Tugas 3 masih dipakai di form Experience, Projects, dan modal hapus, sehingga akan bertabrakan dengan pembatasan berbasis login dan peran. Perbaikan manual: menghapus input Access Code dari template, menghapus fungsi `is_authorized` dari `views.py`, dan menulis ulang `ExperienceEditTest` yang sebelumnya bergantung pada `secret_key` agar memakai login.

    3. Potongan Kode yang Terlewat: Karena panduan berupa potongan kode yang harus disisipkan ke beberapa file, ada bagian yang terlewat saat saya menyalin. `toggle_star` dan `toggle_star_experience` belum di-import di `main/urls.py` sehingga `runserver` gagal dengan `NameError`, dan konstanta `PASSWORD` tidak ikut tertempel di `tests.py` sehingga 14 test error. Keduanya ketahuan saat menjalankan `runserver` dan `python manage.py test`, lalu saya perbaiki manual.

### Tugas 5

1. Debouncing adalah teknik menunda pemanggilan sebuah fungsi sampai pengguna berhenti melakukan aksi selama jeda tertentu. Pada pencarian Experience, setiap ketikan me-reset timer 300 ms, dan permintaan `fetch()` ke `/api/experience/?title=...` baru dikirim setelah 300 ms tanpa ketikan. Tanpa debouncing, mengetik kata "compfest" akan mengirim delapan permintaan berturut-turut (satu per huruf), padahal hanya hasil terakhir yang dibutuhkan. Hal ini membebani server dan database, memboroskan kuota pengguna, dan bisa membuat hasil yang tampil salah karena respons permintaan lama bisa datang lebih lambat dari respons terbaru (*race condition*). Untuk mengatasi kemungkinan terakhir itu, saya juga membatalkan permintaan lama dengan `AbortController` setiap kali pencarian baru dikirim.

2. `fetch()` bersifat asinkron: ia langsung mengembalikan sebuah *Promise*, bukan data. `await` membuat fungsi `async` menunggu sampai Promise itu selesai lalu mengambil hasilnya (objek `Response`), dan `await response.json()` menunggu isi respons selesai dibaca dan diubah menjadi objek JavaScript. Selama menunggu, browser tetap responsif karena yang berhenti hanya fungsi tersebut, bukan seluruh halaman. Jika `await` tidak dipakai, variabel akan berisi Promise yang masih tertunda, sehingga kode berikutnya berjalan sebelum data datang. Akibatnya, misalnya `response.ok` bernilai `undefined` atau kode mencoba melakukan `forEach` pada Promise sehingga terjadi error, dan error dari jaringan tidak tertangkap oleh blok `try...catch` karena terjadinya belakangan.

3. XSS (*Cross-Site Scripting*) adalah serangan ketika penyerang berhasil menyisipkan kode (biasanya JavaScript) ke halaman web, lalu kode itu dijalankan di browser pengunjung lain. Contohnya data berisi `<img src="x" onerror="alert('XSS!')">`: jika ditampilkan sebagai HTML, `onerror` akan berjalan dan bisa dipakai untuk mencuri cookie sesi atau melakukan aksi atas nama korban. Template Django melakukan *auto-escaping*: setiap `{{ variabel }}` otomatis diubah menjadi `&lt;img ...&gt;` sehingga tampil sebagai teks. Saat data ditampilkan lewat JavaScript, perlindungan otomatis itu tidak ada. Jika data dari JSON dimasukkan ke `innerHTML` dengan *template literal*, browser akan menafsirkannya sebagai HTML sungguhan. Karena itu, pada Experience saya melindunginya di dua sisi: setiap teks dari server dilewatkan `escapeHtml()` (atau `textContent`) sebelum disisipkan ke HTML, dan input teks dibersihkan di server dengan `strip_tags` pada `clean_<field>` di `ExperienceForm`.

**Bagian yang dikerjakan:** Pola Tutorial 05 diterapkan pada halaman **Experience** (bagian yang saya kerjakan di Tugas 3 dan Tugas 4: CRUD Experience, peran, dan star), bukan halaman Projects yang dipakai di tutorial.

**Ringkasan implementasi**
- **Data lewat AJAX:** `show_experience` sekarang hanya merender kerangka halaman. `static/js/experience.js` mengambil data dari `/api/experience/` dengan `fetch()`. Endpoint `get_experience_json` menyusun JSON secara manual dengan `JsonResponse`, termasuk info star dari Tugas 4 (`star_count`, `is_starred` untuk pengguna yang sedang login, dan `starred_by` yang hanya berisi username).
- **State halaman:** *skeleton loading* saat data dimuat, pesan kosong (berbeda untuk "belum ada data" dan "pencarian tidak ditemukan"), dan pesan error dengan tombol "Coba lagi".
- **Pencarian dengan debouncing:** berdasarkan nama kegiatan dan peran (Inggris/Indonesia), 300 ms setelah berhenti mengetik, tanpa reload. Parameter `?title=` di URL ikut diperbarui.
- **Tambah data lewat modal:** form `ExperienceForm` ditampilkan di modal pada halaman daftar. View `create_experience_ajax` (POST) memvalidasi dengan ModelForm dan membalas JSON dengan status **201** (berhasil), **400** (input tidak valid, beserta pesan dan label tiap field), atau **403** (bukan pemilik). Hak akses diperiksa di dalam view, bukan hanya dengan menyembunyikan tombol. Token CSRF dikirim lewat header `X-CSRFToken` (juga ikut di `FormData` sebagai `csrfmiddlewaretoken`). Setelah berhasil, daftar dimuat ulang tanpa reload dan kartu baru diberi sorotan.
- **Toast:** muncul saat berhasil, saat validasi gagal (berisi pesan dari server), saat ditolak (403), dan saat jaringan bermasalah. Pesan validasi juga ditampilkan di bawah field yang salah.
- **Perlindungan XSS:** `escapeHtml()` dipakai untuk setiap teks yang disisipkan lewat JavaScript, dan `clean_title`, `clean_role`, `clean_role_indo`, `clean_description`, `clean_description_indo` memakai `strip_tags`. Nama kegiatan yang isinya hanya tag HTML ditolak dengan status 400. Diuji dengan `<img src="x" onerror="alert('XSS!')">`: input lewat form dibersihkan, dan data mentah yang sengaja dimasukkan langsung ke database tetap tampil sebagai teks tanpa memunculkan alert.
- **Struktur kode:** `getCookie`, `getCsrfToken`, `escapeHtml`, `debounce`, dan `formatMonthYear` dipindah ke `static/js/ajax-utils.js`. Konfigurasi (endpoint, URL, hak akses) dikirim dari template lewat atribut `data-*`, sehingga tidak ada logika Django di dalam berkas JavaScript. Lightbox foto memakai *event delegation* agar tetap berfungsi pada kartu yang dibuat oleh JavaScript.
- **Test:** `ExperienceAjaxTest` menguji kerangka halaman, isi JSON dan info star, pencarian, status 201/400/403/405, kewajiban token CSRF, dan pembersihan XSS. Test lama yang memeriksa HTML hasil render server disesuaikan agar memeriksa JSON. Total 103 test lulus.


### Disclosure AI

**Alat:** Claude.

# Log Prompting AI: Tugas 5 dan Fitur Tambahan Pekan Ini

**Alat:** Claude (mode Cowork di aplikasi desktop, model Opus).
**Alasan memakai log:** sesi Cowork tidak menyediakan tombol share link, sehingga percakapan dicatat di sini sebagai log prompting.

**Cara kerja:** folder proyek dihubungkan ke Claude dengan akses baca saja. AI mengerjakan perubahan di salinan proyek terpisah, menjalankan `python manage.py test` dan uji browser otomatis (Playwright), lalu mengirim berkas lengkap dalam file Markdown. Saya menyalin berkas tersebut ke proyek, mencobanya di laptop dan PWS, lalu melakukan commit sendiri.

Prompt ditulis apa adanya (bahasa santai). Kolom "Hasil / koreksi" mencatat apa yang dikerjakan AI dan bagian yang harus saya luruskan.

---


| # | Prompt saya | Hasil / koreksi |
|---|---|---|
| 11 | "sekarang tugas 5" + PDF soal Tugas 5 | AI membaca PDF dan folder proyek, lalu memilih halaman **Experience** (bagian Tugas 3 dan 4, bukan Projects dari tutorial). Hasilnya: endpoint JSON manual dengan info star, `show_experience` yang hanya merender kerangka, `create_experience_ajax` (201/400/403), modal tambah, pencarian dengan debounce dan `AbortController`, state loading/kosong/error, toast, `escapeHtml` dan `strip_tags`, serta `ajax-utils.js`. Lightbox diubah memakai *event delegation*, ditambah 13 test baru (total 103), dan draf README. Saat uji browser, AI menemukan toast error menutupi tombol Submit di modal, lalu memindahkan toast ke atas saat modal terbuka. Perubahan dibagi menjadi 6 langkah dengan conventional commit. |
| 12 | "yang 4b saya salah commit lagi saya udah commit di langkah 4 sebelum ubah css yang di 4b" | CSS dijadikan commit terpisah (`style(experience): ...`), tanpa membatalkan commit sebelumnya. |
| 13 | "gimana cara share chat ini, kok ga ada opsi sharenya" | Sesi Cowork tidak menampilkan tombol share, jadi dibuat log prompting ini sebagai gantinya. |

## C. Yang saya periksa sendiri

- Menjalankan `python manage.py test` di laptop setelah menyalin berkas.
- Mencoba halaman Experience sebagai pengunjung, user biasa, dan pemilik (pencarian, tambah lewat modal, star).
- Menguji XSS dengan `<img src="x" onerror="alert('XSS!')">`. Input dibersihkan oleh server dan alert tidak muncul.
- Mengecek ulang isi README dan bagian disclosure ini sebelum commit.

**Strategi Prompting:** Saya mengunggah PDF Tugas 5 dan menghubungkan folder proyek supaya AI bisa membaca kode saya (hanya membaca, tanpa mengubah folder). AI diminta mengerjakan di salinan terpisah, menguji dengan `python manage.py test` dan browser otomatis untuk setiap peran, lalu mengirim berkas lengkap yang siap saya salin. Setiap hasil saya cek di browser saya sendiri, dan jika tidak sesuai saya kirim screenshot sebagai umpan balik.

**Bagian yang dibantu:** Endpoint JSON manual `get_experience_json`, view `create_experience_ajax`, `static/js/experience.js` dan `static/js/ajax-utils.js`, modal tambah Experience, pembersihan `strip_tags` di `ExperienceForm`, penyesuaian lightbox agar memakai *event delegation*, test `ExperienceAjaxTest`, serta draf README ini.

**Keterbatasan AI dan Perbaikan Manual:**

    1. Salah Paham Fitur Lightbox: Saya meminta foto Experience bisa diklik dan dipindah dengan tombol panah. AI membuat panah yang berpindah ke foto Experience lain, padahal maksud saya adalah berpindah antar beberapa foto di dalam satu Experience yang sama. Perbaikan: saya jelaskan ulang maksudnya, lalu ditambahkan kolom foto tambahan (satu URL per baris) dan lightbox dibatasi hanya pada foto milik kartu yang diklik.

    2. Kesimpulan yang Keliru soal PWS: Login dengan akun superuser berhasil di lokal tetapi gagal di PWS karena database lokal (SQLite) dan database PWS (PostgreSQL) terpisah. AI awalnya menyuruh `createsuperuser` dari laptop memakai `.env.prod`, yang gagal dengan *connection timed out* karena database PWS memakai IP internal kampus. AI lalu menyimpulkan PWS tidak punya terminal dan membuat jalan memutar lewat environment variable. Perbaikan manual: saya menunjukkan screenshot dashboard PWS yang ternyata punya tab Terminal, lalu menjalankan `python manage.py createsuperuser` langsung di sana.

    3. Migrasi Data yang Harus Ditulis Manual: Untuk terjemahan isi database, AI awalnya menyertakan file migrasi data yang harus saya buat sendiri. Saya tidak mau menulis file migrasi secara manual, sehingga pendekatannya diganti: kolom baru cukup dibuat dengan `makemigrations`, dan terjemahan data lama diisi otomatis oleh aplikasi ketika halaman dibuka.