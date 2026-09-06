Nama : Muhammad Faza Aqila

NPM : 2506613142

Kelas : PBP C

**Penggunaan AI (AI Disclosure) & Refleksi Kritis**

**Alat yang Digunakan:** Gemini dan Claude
**Strategi Prompting:** Memberikan spesifikasi teknologi, palet warna, dan deskripsi *layout* yang presisi.

**Bagian yang Dibantu AI:**
Saya memanfaatkan AI sebagai teman berfikir untuk logika matematis yang rumit, secara khusus dalam membuat koordinat bentuk SVG kustom untuk latar belakang gelombang, menyusun logika CSS `@keyframes` untuk animasi masuk berurutan dan efek glassmorphism beserta efek ketika kursor berada di tulisan pada navigasi bar.

**Keterbatasan AI & *Debugging* Manual:**
Meskipun AI sangat efisien dalam menghasilkan kode, saya menemukan bahwa AI tidak memiliki pemahaman spasial yang utuh terhadap hasil *render* visual di *browser*.

Sebagai contoh, saat membuat animasi *reveal* untuk teks profil dan foto, AI secara baku memberikan instruksi `clip-path: inset(0 0 0 0)`. Saat dieksekusi, kode dari AI ini menimbulkan *glitch* visual yang fatal, seperti ekor huruf yang menggantung ke bawah (huruf 'q' pada "Aqila") terpotong paksa.

Menyadari keterbatasan *output* generik AI ini, saya melakukan perbaikan dan restrukturisasi CSS secara manual:

**Perbaikan Teks:** Saya memodifikasi kode AI dengan memasukkan area *bleed* negatif pada parameter `clip-path` (menjadi `inset(-20% -20% -20% -20%)`) untuk memberikan ruang tambahan, sehingga ekor huruf 'q' tetap tampil utuh.

Hal ini menyadarkan saya bahwa AI sangat berguna sebagai asisten penyusun kerangka, namun intervensi dan pemahaman fundamental *developer* mutlak diperlukan untuk menyelesaikan *edge-cases* dan menyempurnakan elemen *User Interface* (UI).