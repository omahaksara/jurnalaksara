# Jurnal Aksara — AI Hub

Skrip terminal untuk membuat jawaban teks/kode memakai Gemini, mengambil prompt ilustrasi dari jawaban, lalu membuat gambar memakai Pollinations.ai. Semua hasil disimpan di `output/`.

## Prasyarat

- Python 3.10+
- Gemini API key dari [Google AI Studio](https://aistudio.google.com/app/apikey)
- Pollinations API key dari [Pollinations](https://enter.pollinations.ai/)
- Koneksi internet

**Tentang biaya/kuota:** Gemini API memiliki free tier dengan batas pemakaian yang bergantung model, wilayah, dan kebijakan Google. Pollinations saat ini meminta API key untuk permintaan generasi; ketersediaan kredit gratis/biaya mengikuti saldo, model, dan ketentuan akun Pollinations. Jadi jangan menganggap kedua layanan memiliki penggunaan gratis tanpa batas. Periksa halaman akun sebelum penggunaan rutin.

## Instalasi

Dari root repositori:

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

## Konfigurasi API key

Buat file `.env` di dalam folder `ai-hub/`, sejajar dengan `main.py`:

```dotenv
GEMINI_API_KEY=ISI_API_KEY_GOOGLE_AI_STUDIO
POLLINATIONS_API_KEY=ISI_SECRET_KEY_POLLINATIONS
# Opsional
GEMINI_MODEL=gemini-2.5-flash
POLLINATIONS_MODEL=zimage
```

Jangan masukkan key asli ke source code atau commit Git. File `.env` sudah dikecualikan oleh `.gitignore`. Gunakan secret key Pollinations hanya di komputer/server pribadi, jangan di aplikasi browser.

## Menjalankan

Mode interaktif:

```bash
python main.py
```

Prompt langsung:

```bash
python main.py --prompt "Buat artikel singkat tentang kebiasaan membaca."
```

Hanya teks/kode (tanpa gambar):

```bash
python main.py --prompt "Buat fungsi Python untuk membaca CSV." --no-image
```

Ukuran gambar:

```bash
python main.py --prompt "Ilustrasi perpustakaan hangat saat hujan" --width 1024 --height 768
```

Ukuran yang diterima: 256–2048 piksel.

## Hasil

`output/` dibuat otomatis dan berisi file Markdown jawaban serta gambar (PNG/JPG/WebP) jika pembuatan gambar berhasil. Hasil lokal tidak diunggah ke GitHub.

## Troubleshooting

- **Gemini 401/403:** cek key Google AI Studio.
- **Gemini 429:** kuota/batas permintaan tercapai; tunggu atau periksa penggunaan akun.
- **Pollinations 401:** key tidak ada atau tidak valid.
- **Pollinations 402:** saldo/kredit atau anggaran key tidak mencukupi.
- **Pollinations 429/5xx:** coba lagi nanti atau periksa status layanan.
- **Model tidak tersedia:** ubah `GEMINI_MODEL` atau `POLLINATIONS_MODEL` ke model yang tersedia di akun/dokumentasi.

Dokumentasi: [Gemini API](https://ai.google.dev/gemini-api/docs) · [Pollinations API](https://gen.pollinations.ai/)
