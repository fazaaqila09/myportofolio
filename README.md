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