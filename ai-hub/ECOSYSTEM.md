# Omah Aksara Ecosystem
## Independent but Connected

Dokumen ini menjadi panduan kerja ringan untuk repo-repo dalam ekosistem Omah Aksara. Tujuannya mempercepat pengembangan dan berbagi dukungan tanpa membuat satu proyek bergantung atau merusak proyek lain.

## Prinsip utama

- **Repo tetap mandiri.** Setiap aplikasi memiliki kode, rilis, konfigurasi, dan tanggung jawab sendiri.
- **Berbagi pengetahuan, bukan mencampur data.** AI Hub boleh membantu membaca dan mengembangkan repo lain, tetapi data operasional tidak otomatis dipindahkan atau digabung.
- **Perubahan proporsional.** Perubahan kecil cukup diperiksa pada bagian yang disentuh. Pemeriksaan menyeluruh hanya untuk perubahan yang berdampak luas atau berisiko.
- **Tidak ada sinkronisasi kode otomatis lintas repo.** Komponen atau pola bersama diadopsi secara sadar oleh repo yang membutuhkan.
- **Utamakan kelancaran pengguna.** Jangan menambah proses, persetujuan, atau pemeriksaan yang tidak memberi manfaat nyata.

## Peta repo

| Repo | Peran | Batas utama |
|---|---|---|
| `omahaksara/jurnalaksara` | Jurnal dan AI Hub / pusat alat bantu pengembangan | Menjadi alat bantu, bukan pemilik data aplikasi lain |
| `omahaksara/invitation` | Engine undangan, tema, data undangan, integrasi RSVP dan buku tamu | Data pelanggan dan layanan undangan harus tetap terisolasi |
| `omahaksara/omahaksara.github.io` | Katalog, demo, halaman publik, dan router URL pendek | Tidak menduplikasi engine atau backend invitation |
| `omahaksara/ruangkelas` | Workspace administrasi dan pembelajaran guru | Data siswa/sekolah tidak dibagikan ke repo publik atau AI Hub |

## Aturan khusus Invitation

Undangan yang sudah dibagikan kepada pasangan, keluarga, dan tamu adalah layanan produksi. Karena itu:

- Jangan mengubah isi, nama, tanggal, foto, musik, tema, slug, URL, RSVP, atau buku tamu pelanggan sebagai efek samping pengembangan ekosistem.
- Jangan menjalankan migrasi massal atau mengubah endpoint produksi hanya demi menyamakan struktur.
- Pengembangan fitur dan tema baru tetap boleh berjalan cepat. Jaga agar perubahan terlokalisasi dan kompatibel dengan kontrak data/tema yang berlaku.
- Untuk perubahan yang menyentuh alur pembukaan undangan, routing, data klien, RSVP, buku tamu, atau backend, lakukan uji terarah pada demo/test client terlebih dahulu.
- Jangan mengirim formulir uji ke spreadsheet pelanggan. Gunakan backend dan spreadsheet uji.
- Katalog boleh membaca registry tema yang disediakan invitation; katalog tidak boleh menjadi sumber kedua yang mengelola daftar tema secara terpisah.
- Perubahan konten atau tampilan pelanggan dilakukan hanya sebagai pekerjaan khusus pelanggan, bukan sebagai sinkronisasi umum.

## Cara kerja lintas repo

1. Tentukan repo pemilik fitur. Perubahan dikerjakan di repo tersebut.
2. Jika ada pola yang berguna bagi repo lain, dokumentasikan atau tawarkan sebagai opsi; jangan menyalin otomatis.
3. Gunakan branch untuk perubahan yang berpotensi memengaruhi layanan aktif. Perubahan dokumentasi atau perbaikan kecil yang terisolasi boleh lebih sederhana.
4. Jalankan pemeriksaan yang relevan dengan file dan alur yang berubah. Jangan mengulang seluruh suite tanpa alasan.
5. Catat perubahan yang berdampak lintas repo di dokumen ini atau README terkait.
6. Integrasi/deployment tetap mengikuti mekanisme repo masing-masing.

## Batas data dan rahasia

- API key, token, kredensial, dan konfigurasi privat disimpan di secret manager atau file lokal yang diabaikan Git; tidak di-commit.
- Data pelanggan undangan, data siswa, dan catatan pribadi tidak dimasukkan ke AI Hub, issue publik, atau repo publik.
- Gunakan data demo sintetis untuk pengembangan dan dokumentasi.
- Hasil AI bersifat bantuan kerja; pemilik proyek tetap memeriksa sebelum dipakai pada layanan pelanggan atau sekolah.

## Kapan perlu pemeriksaan ekstra?

Cukup lakukan pemeriksaan tambahan saat perubahan menyentuh:
- kontrak JSON atau migrasi data;
- URL/slug dan router;
- tema aktif dan registry tema;
- RSVP, buku tamu, Apps Script, atau spreadsheet;
- autentikasi, izin, dan data pribadi;
- dependensi bersama atau perubahan yang menjangkau lebih dari satu repo.

Untuk perubahan teks, dokumentasi, styling terisolasi, atau fitur yang tidak menyentuh alur sensitif, cukup lakukan uji ringan yang relevan.

## Status sinkronisasi

Sinkronisasi saat ini bersifat **koordinasi dan standar kerja**, bukan replikasi kode atau data otomatis. Integrasi teknis lintas repo ditambahkan hanya jika ada kebutuhan konkret dan manfaatnya jelas.

Dengan pola ini, semua proyek dapat saling mendukung sambil tetap bebas berkembang.
