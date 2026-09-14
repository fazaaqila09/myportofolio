Nama : Muhammad Faza Aqila

NPM : 2506613142

Kelas : PBP C

### Tugas 1

1. Ya, saya menerapkan elemen semantik HTML5 pada berkas index.html. Tag nav digunakan untuk mempermudah identifikasi blok navigasi utama bagi screen reader. Tag section untuk memisahkan area konten utama seperti About, Education, dan Experience, serta secara spesifik memakai tag article untuk membungkus setiap kartu riwayat organisasi karena informasinya bersifat mandiri. Selain membuat struktur kode jauh lebih terbaca dibandingkan tumpukan div generik, elemen ini memperjelas hierarki halaman. Saya juga menggunakan Description List (dl, dt, dd) di bagian About karena sangat tepat secara semantik untuk merelasikan pasangan data profil, seperti Nama dan Umur.

2. Tantangan tata letak terbesar saat menyusun style.css adalah menjaga proporsi elemen berdampingan agar tidak saling bertabrakan atau terpotong saat layar menyempit. Pada tampilan desktop, area Hero menggunakan tata letak flexbox horizontal dengan teks di kiri dan foto di kanan. Saat berpindah ke mobile, saya memprioritaskan keterbacaan teks dan proporsi foto. Solusinya adalah dengan mengubah alur menjadi vertikal (flex-direction: column-reverse) dan mengubah perataan teks menjadi menengah (text-align: center) supaya visual tetap terjaga.

3. Batasan paling utama dari static web murni adalah kekakuan dalam membuat interaksi dan animasi visual yang kompleks dan tidak ada interaksi dua arah. Setiap kali ada penambahan riwayat pengalaman atau pendidikan baru, saya harus mengubah hardcode di dalam HTML dan melakukan redeployment secara manual. Selain itu, *user* saat ini hanya bisa menghubungi melalui tautan eksternal mailto: karena web belum bisa memproses input pengguna secara mandiri. Pada proyek selanjutnya, fungsionalitas dinamis yang ingin dtambahkan adalah integrasi database menggunakan arsitektur MVT dan implementasi JavaScript untuk menghidupkan *user interface*. Dengan JavaScript, saya bisa memanfaatkan API Intersection Observer atau library animasi untuk merancang transisi web yang jauh lebih interaktif. Serta, ingin membuat panel admin untuk mengelola (CRUD) entri pengalaman secara dinamis.

### Disclosure AI

**Alat:** Claude.

**Link percakapan AI:** https://claude.ai/chat/8c5a667f-5d61-4073-8987-a81e0e555d3b

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

**Link percakapan AI:** https://claude.ai/chat/8c5a667f-5d61-4073-8987-a81e0e555d3b

**Bagian yang dibantu:** Mencari ide struktur MVT untuk model Education, membuat desain timeline vertikal menggunakan HTML/CSS, membuat skrip pengisian data otomatis (auto-populate), serta menyusun kerangka awal untuk unit test.

**Keterbatasan AI dan Perbaikan Manual:**
Sama seperti tugas sebelumnya, AI sangat efisien untuk membuat kerangka kode, tapi sering kali kurang paham dengan flow atau logika sistem secara keseluruhan. Pada tugas 2 ini, saya menemukan kode dari AI justru memicu error dan mengharuskan saya melakukan troubleshoot manual:

    1. Konteks Database Lokal (Broken Image): Saat mengganti logo dari ekstensi .jpg menjadi .png, AI menyarankan untuk sekadar mengubah teks rutenya di dalam skrip views.py. Secara sintaks itu benar, tapi saat dijalankan, gambar logonya tetap pecah (hilang). AI tidak menyadari bahwa data dengan format lama sudah terlanjur tersimpan di dalam database lokal db.sqlite3 milik saya, dan perubahan skrip AI tersebut tidak akan tereksekusi karena tabelnya tidak dalam keadaan kosong. Perbaikan manual: Saya menyadari masalah state ini, lalu menghapus sendiri berkas db.sqlite3 lokal saya dan melakukan migrate ulang dari nol agar skrip barunya bisa menyuntikkan path gambar yang benar.