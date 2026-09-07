Nama : Muhammad Faza Aqila

NPM : 2506613142

Kelas : PBP C

### Tugas 1

1. Ya, saya menerapkan elemen semantik HTML5 pada berkas index.html. Tag <nav> digunakan untuk mempermudah identifikasi blok navigasi utama bagi screen reader. Tag <section> untuk memisahkan area konten utama seperti About, Education, dan Experience, serta secara spesifik memakai tag <article> untuk membungkus setiap kartu riwayat organisasi karena informasinya bersifat mandiri. Selain membuat struktur kode jauh lebih terbaca dibandingkan tumpukan <div> generik, elemen ini memperjelas hierarki halaman. Saya juga menggunakan Description List (<dl>, <dt>, <dd>) di bagian About karena sangat tepat secara semantik untuk merelasikan pasangan data profil, seperti Nama dan Umur.

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