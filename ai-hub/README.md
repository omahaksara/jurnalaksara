# Jurnal Aksara — AI Hub

AI Hub adalah skrip Python sederhana untuk:
1. menerima prompt dari terminal;
2. meminta jawaban teks atau kode dari Google Gemini API (Google AI Studio);
3. membaca prompt visual yang disertakan Gemini;
4. mencoba membuat ilustrasi melalui Pollinations.ai; dan
5. menyimpan hasil teks serta gambar ke folder `output/`.

> **Catatan layanan gratis:** Google AI Studio menyediakan kuota gratis dengan batas penggunaan yang dapat berubah menurut model, wilayah, dan kebijakan Google. Pollinations.ai dapat digunakan tanpa API key pada endpoint publiknya, tetapi ketersediaan, batas pemakaian, dan ketentuan layanannya dapat berubah. Skrip tetap menyimpan jawaban teks jika layanan gambar sedang tidak tersedia.

## 1. Persiapan

- Python 3.10 atau lebih baru.
- API key Gemini dari [Google AI Studio](https://aistudio.google.com/app/apikey).
- Koneksi internet.

## 2. Instalasi

Masuk ke folder `ai-hub`:

```bash
cd ai-hub
python -m venv .venv
```

Aktifkan virtual environment:

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

Pasang dependensi:

```bash
python -m pip install -r requirements.txt
```

## 3. Pasang API Key

Buat file bernama `.env` di dalam folder `ai-hub/` (sejajar dengan `main.py`) dengan isi:

```dotenv
GEMINI_API_KEY=PASTE_API_KEY_ANDA_DI_SINI
# Opsional:
GEMINI_MODEL=gemini-2.5-flash
```

Jangan unggah atau commit file `.env`. File ini sudah dikecualikan oleh `.gitignore`.

## 4. Jalankan

Mode interaktif — program akan meminta prompt:

```bash
python main.py
```

Kirim prompt langsung:

```bash
python main.py --prompt "Buatkan artikel singkat tentang kebiasaan membaca."
```

Hanya hasil teks tanpa gambar:

```bash
python main.py --prompt "Buat fungsi Python untuk merapikan data CSV." --no-image
```

Atur ukuran gambar (256–2048 piksel):

```bash
python main.py --prompt "Ilustrasi suasana perpustakaan yang hangat" --width 1024 --height 768
```

## 5. Hasil

File hasil dibuat otomatis di:

```text
ai-hub/
└── output/
    ├── hasil_YYYYMMDD_HHMMSS.md
    └── hasil_YYYYMMDD_HHMMSS.png
```

Format gambar mengikuti tipe file yang dikirim Pollinations (PNG, JPG, atau WebP). Folder output diabaikan Git agar hasil pribadi tidak ikut terunggah.

## 6. Pemecahan masalah

- **GEMINI_API_KEY belum diatur:** pastikan file `.env` berada di folder yang sama dengan `main.py`.
- **401/403 dari Gemini:** periksa API key dan akses Google AI Studio.
- **429 dari Gemini:** kuota atau batas permintaan mungkin tercapai; tunggu lalu coba kembali.
- **Gambar gagal dibuat:** layanan Pollinations bisa sedang sibuk/tidak tersedia. Jawaban teks tetap disimpan; ulangi beberapa saat kemudian.
- **Model tidak tersedia:** ubah `GEMINI_MODEL` pada `.env` ke model Gemini yang tersedia untuk akun Anda.

## Keamanan

Jangan pernah menaruh API key di source code, prompt, tangkapan layar publik, atau commit Git. Jika API key terlanjur terunggah, cabut key tersebut di Google AI Studio dan buat yang baru.
