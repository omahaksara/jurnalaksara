# Jurnal Aksara — AI Hub

Pusat kerja AI berbasis Python untuk membantu penulisan, pendidikan, pemrograman, ilustrasi, dan produksi konten. Komponen yang tersedia:

- **Gemini** untuk tanya jawab, artikel, ide, naskah, kode, storyboard, dan prompt visual (free tier memiliki kuota/batas).
- **Pollinations** untuk membuat gambar dari prompt (API key diperlukan; kredit dan biaya mengikuti akun/model).
- **ComfyUI lokal** untuk menjalankan workflow gambar atau video open-source di komputer sendiri. Tidak ada biaya API, tetapi membutuhkan komputer/GPU dan model yang sesuai.

Hasil disimpan ke `ai-hub/output/` secara lokal dan tidak otomatis diunggah ke GitHub.

## Biaya dan batasan penting

Tidak ada janji penggunaan gratis tanpa batas. Gemini memiliki kuota gratis yang dapat berubah. Pollinations memerlukan API key dan ketersediaan kredit gratis bergantung akun. ComfyUI dapat digunakan tanpa biaya API jika dijalankan sendiri, tetapi perangkat, listrik, ruang penyimpanan, waktu render, dan model yang diunduh tetap menjadi tanggung jawab pengguna. Jangan memasukkan API key ke source code atau commit Git.

## 1. Persiapan

- Python 3.10+
- API key Gemini dari [Google AI Studio](https://aistudio.google.com/app/apikey)
- API key Pollinations dari [Pollinations](https://enter.pollinations.ai/) (opsional jika hanya memakai Gemini/ComfyUI)
- ComfyUI lokal untuk generasi gambar/video lokal: [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

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

## 2. Konfigurasi

Salin `.env.example` menjadi `.env`, kemudian isi key yang tersedia:

**Windows PowerShell**
```powershell
Copy-Item .env.example .env
```

**macOS/Linux**
```bash
cp .env.example .env
```

Contoh:

```dotenv
GEMINI_API_KEY=isi_key_google
POLLINATIONS_API_KEY=isi_key_pollinations
GEMINI_MODEL=gemini-2.5-flash
POLLINATIONS_MODEL=zimage
COMFYUI_URL=http://127.0.0.1:8188
```

Key yang tidak dipakai boleh dibiarkan kosong. File `.env` sudah dikecualikan dari Git.

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

## 4. Membuat gambar

Skrip utama dapat meminta Gemini menyusun jawaban dan prompt ilustrasi, lalu mengirim prompt gambar ke Pollinations:

```bash
python main.py --prompt "Buat konsep poster perpustakaan sekolah yang hangat."
```

Ukuran gambar dapat diatur:

```bash
python main.py --prompt "Ilustrasi ruang baca saat hujan" --width 1024 --height 768
```

Jika ingin generasi gambar lokal, gunakan ComfyUI dengan workflow API yang sesuai model gambar Anda; runner `video.py` juga dapat menjalankan workflow ComfyUI gambar maupun video.

## 5. Membuat video dengan ComfyUI lokal

### Persiapan ComfyUI

1. Pasang dan jalankan ComfyUI dari komputer yang memiliki GPU/komputasi memadai.
2. Pasang model video yang kompatibel (misalnya workflow berbasis Wan atau model video open-source lain). Perhatikan kebutuhan VRAM dan lisensi model.
3. Buka ComfyUI di browser, susun atau impor workflow video sampai berhasil dijalankan.
4. Aktifkan **Dev Mode** jika diperlukan, lalu ekspor workflow dalam format **API** (bukan workflow UI biasa) sebagai file JSON.
5. Pastikan server ComfyUI berjalan. Default URL: `http://127.0.0.1:8188`.

Jalankan workflow:

```bash
python video.py --workflow workflow_api.json
```

Workflow bisa berupa workflow video atau gambar. File media hasil dikenali dari output node dan diunduh ke `output/`.

Untuk mengganti prompt teks di salah satu node workflow:

```bash
python video.py --workflow workflow_api.json --prompt "A cinematic shot of a quiet library in the rain" --prompt-node-id 6
```

Ganti angka `6` dengan ID node prompt pada workflow API Anda. Runner hanya mengganti satu field bernama `text`, `prompt`, `positive`, atau `positive_prompt` yang dikenali secara tunggal. Jika workflow memiliki beberapa field prompt atau struktur berbeda, edit JSON workflow terlebih dahulu. Tiap model/custom node memiliki format dan kebutuhan berbeda; tidak ada satu workflow universal yang otomatis cocok untuk semua model.

Atur alamat server jika ComfyUI berjalan di komputer/server lain:

```dotenv
COMFYUI_URL=http://ALAMAT-KOMPUTER:8188
```

Jangan membuka port ComfyUI ke internet publik tanpa pengamanan jaringan dan autentikasi yang tepat.

## 6. Hasil

Semua hasil berada di `output/`:

- `.md` — jawaban teks Gemini
- `.png`, `.jpg`, `.webp` — gambar
- `.mp4`, `.webm`, `.gif` atau format media lain yang dihasilkan workflow ComfyUI

Output tidak masuk Git karena folder ini diabaikan, kecuali file placeholder.

## Troubleshooting

- **Gemini 401/403:** periksa API key dan status proyek.
- **Gemini 429:** kuota/rate limit tercapai; tunggu atau cek batas akun.
- **Pollinations 401/402:** key tidak valid atau kredit/anggaran tidak cukup.
- **ComfyUI connection refused:** pastikan ComfyUI aktif dan `COMFYUI_URL` benar.
- **ComfyUI node validation error:** workflow mungkin bukan format API atau custom nodes/model belum terpasang.
- **Video terlalu lambat / out of memory:** gunakan resolusi, durasi, batch, atau model yang lebih ringan; kebutuhan VRAM bergantung workflow.
- **Tidak ada file output:** pastikan workflow memiliki output node yang menghasilkan file media.

## Referensi

- [Gemini API](https://ai.google.dev/gemini-api/docs)
- [Pollinations API](https://gen.pollinations.ai/)
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI server API routes](https://github.com/Comfy-Org/docs/blob/main/development/comfyui-server/comms_routes.mdx)
