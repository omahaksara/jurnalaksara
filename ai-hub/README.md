# Jurnal Aksara — AI Hub

Pusat kerja AI online untuk membantu penulisan, pendidikan, pemrograman, ilustrasi, dan produksi konten. Tidak memerlukan GPU lokal.

## Layanan

- **Gemini API** — tanya jawab, artikel, ide konten, materi pendidikan, kode, naskah, dan storyboard. Kuota gratis mengikuti kebijakan Google.
- **Pollinations** — pembuatan gambar online. Memerlukan API key; kredit dan biaya mengikuti akun.
- **Magic Hour API** — pembuatan video online dari teks. Akun baru menawarkan kredit percobaan tanpa kartu kredit menurut halaman API, tetapi jumlah kredit, model yang dapat dipakai, resolusi, dan hak penggunaan dapat berubah. Setiap render memakai kredit. AI Hub meminta konfirmasi eksplisit sebelum mengirim job video.

Semua hasil yang berhasil diunduh disimpan di `ai-hub/output/` secara lokal dan tidak otomatis diunggah ke GitHub.

## Biaya dan keamanan

AI Hub tidak mengklaim layanan ini gratis tanpa batas. Gemini memiliki kuota sesuai model dan wilayah. Pollinations menggunakan API key dan saldo/kredit akun. Magic Hour menyediakan kredit percobaan untuk akun baru, tetapi render berikutnya atau model/resolusi tertentu dapat membutuhkan kredit tambahan atau paket berbayar. Periksa saldo dan biaya di dashboard sebelum membuat media.

Tidak ada API key yang ditanam dalam source code. Jangan pernah commit file `.env` atau membagikan key.

## 1. Persiapan

- Python 3.10+
- Gemini API key dari [Google AI Studio](https://aistudio.google.com/app/apikey)
- Pollinations API key dari [Pollinations](https://enter.pollinations.ai/) (opsional)
- Magic Hour API key dari [Developer Dashboard](https://magichour.ai/developer) (opsional, untuk video)

Dari root repository:

```bash
cd ai-hub
python -m venv .venv
```

Aktifkan lingkungan:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

Pasang dependensi:

```bash
python -m pip install -r requirements.txt
```

## 2. Konfigurasi API key

Salin `.env.example` menjadi `.env`.

**Windows PowerShell**
```powershell
Copy-Item .env.example .env
```

**macOS/Linux**
```bash
cp .env.example .env
```

Isi key yang diperlukan:

```dotenv
GEMINI_API_KEY=isi_key_google
POLLINATIONS_API_KEY=isi_key_pollinations
MAGIC_HOUR_API_KEY=isi_key_magic_hour
GEMINI_MODEL=gemini-2.5-flash
POLLINATIONS_MODEL=zimage
MAGIC_HOUR_VIDEO_MODEL=wan-2.2
```

Key untuk layanan yang tidak dipakai boleh dibiarkan kosong.

## 3. Tanya jawab, menulis, dan coding

Mode interaktif:

```bash
python main.py
```

Prompt langsung:

```bash
python main.py --prompt "Buat artikel edukasi tentang literasi digital."
```

Hanya teks/kode tanpa gambar:

```bash
python main.py --prompt "Buat fungsi Python untuk membaca CSV." --no-image
```

## 4. Membuat gambar online

Skrip utama meminta Gemini menyusun jawaban dan prompt ilustrasi, lalu mengirim prompt gambar ke Pollinations:

```bash
python main.py --prompt "Buat konsep poster perpustakaan sekolah yang hangat."
```

Ukuran gambar dapat diatur:

```bash
python main.py --prompt "Ilustrasi ruang baca saat hujan" --width 1024 --height 768
```

Pembuatan gambar memerlukan key dan kredit/akses yang aktif di akun Pollinations.

## 5. Membuat video online

AI Hub menggunakan Magic Hour cloud API. Komputasi video berjalan di server penyedia, bukan di laptop/HP Anda.

Contoh video vertikal:

```bash
python video.py --prompt "Cinematic vertical video of a cozy school library on a rainy afternoon, warm window light, slow camera push-in, realistic details" --seconds 5 --aspect-ratio 9:16 --resolution 480p --confirm-credit-use
```

Contoh video landscape:

```bash
python video.py --prompt "A cinematic aerial view of green rice fields at sunrise, gentle camera movement" --seconds 5 --aspect-ratio 16:9 --resolution 480p --confirm-credit-use
```

Pengaturan default:
- Model: `wan-2.2` (dapat diubah melalui `MAGIC_HOUR_VIDEO_MODEL`).
- Durasi: 5 detik.
- Rasio: 9:16 (vertikal).
- Resolusi: 480p untuk preset hemat.

**Penting:** setiap render memakai kredit. Opsi `--confirm-credit-use` wajib agar job tidak terkirim tanpa persetujuan sadar. Periksa saldo, model yang diizinkan pada akun, dan biaya aktual di [Magic Hour Developer Dashboard](https://magichour.ai/developer) sebelum menjalankan. Jangan mengulang job jika status sebelumnya belum jelas; periksa [My Library](https://magichour.ai/my-library) terlebih dahulu untuk menghindari render ganda.

## 6. Hasil

Semua file yang diunduh disimpan ke `output/`:
- `.md` — jawaban teks Gemini.
- `.png`, `.jpg`, `.webp` — gambar.
- `.mp4` atau format video hasil SDK — video Magic Hour.

Folder output diabaikan Git, sehingga hasil pribadi tidak otomatis masuk repository.

## Troubleshooting

- **Gemini 401/403:** periksa API key Google.
- **Gemini 429:** kuota/rate limit tercapai.
- **Pollinations 401/402:** key tidak valid atau kredit/anggaran tidak cukup.
- **Magic Hour 401:** API key salah atau tidak aktif.
- **Magic Hour 402:** kredit tidak cukup atau model/fitur memerlukan paket lain.
- **Video tidak muncul:** periksa status proyek di My Library; jangan mengirim job kedua sebelum status pertama diketahui.
- **Model/resolusi ditolak:** pilih model dan resolusi yang tersedia untuk akun Anda.

## Referensi resmi

- [Gemini API](https://ai.google.dev/gemini-api/docs)
- [Pollinations API](https://gen.pollinations.ai/)
- [Magic Hour API](https://docs.magichour.ai/)
- [Magic Hour Python SDK](https://github.com/magichourhq/magic-hour-python)
