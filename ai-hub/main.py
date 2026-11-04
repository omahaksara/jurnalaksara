#!/usr/bin/env python3
"""Generate a text response with Gemini and an optional image with Pollinations."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import google.generativeai as genai
import requests
from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
DEFAULT_MODEL = "gemini-2.5-flash"
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Buat jawaban teks/koding dengan Gemini dan gambar dengan Pollinations.ai."
    )
    parser.add_argument(
        "-p", "--prompt",
        help="Prompt yang akan dikirim ke Gemini. Jika kosong, Anda akan diminta mengetik.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
        help=f"Nama model Gemini (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument("--width", type=int, default=1024, help="Lebar gambar (default: 1024).")
    parser.add_argument("--height", type=int, default=1024, help="Tinggi gambar (default: 1024).")
    parser.add_argument(
        "--no-image",
        action="store_true",
        help="Hanya simpan jawaban teks, tanpa meminta gambar.",
    )
    return parser.parse_args()


def ask_gemini(prompt: str, api_key: str, model_name: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    instruction = f"""
Anda adalah asisten yang membantu membuat konten, tulisan, dan kode.
Jawab permintaan pengguna secara lengkap dalam Bahasa Indonesia, kecuali jika
bahasa lain diminta. Jika pengguna meminta kode, berikan kode yang dapat dipakai
beserta penjelasan singkat.

Setelah jawaban utama, tulis satu prompt visual berbahasa Inggris yang cocok
untuk membuat ilustrasi pendamping. Prompt visual harus aman, deskriptif,
dan tidak berisi teks/tipografi di dalam gambar. Jangan membuat prompt visual
jika permintaan memang tidak membutuhkan gambar; dalam kasus itu tulis NONE.

Gunakan format persis berikut:
===JAWABAN===
[Jawaban teks atau kode]
===PROMPT_VISUAL===
[Prompt visual berbahasa Inggris atau NONE]
===AKHIR_PROMPT_VISUAL===

Permintaan pengguna:
{prompt}
"""
    response = model.generate_content(instruction)
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError(
            "Gemini tidak mengembalikan teks. Periksa kuota, model, atau keamanan prompt."
        )
    return text.strip()


def split_response(response: str) -> tuple[str, str | None]:
    match = re.search(
        r"===JAWABAN===\s*(.*?)\s*===PROMPT_VISUAL===\s*(.*?)\s*===AKHIR_PROMPT_VISUAL===",
        response,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return response.strip(), None

    answer = match.group(1).strip()
    visual_prompt = match.group(2).strip()
    if not visual_prompt or visual_prompt.upper() == "NONE":
        return answer, None
    return answer, visual_prompt


def generate_image(prompt: str, width: int, height: int, destination: Path) -> Path:
    if not (256 <= width <= 2048 and 256 <= height <= 2048):
        raise ValueError("Ukuran gambar harus berada di antara 256 dan 2048 piksel.")

    url = POLLINATIONS_URL + quote(prompt, safe="")
    response = requests.get(
        url,
        params={"width": width, "height": height, "nologo": "true"},
        headers={"User-Agent": "JurnalAksara-AIHub/1.0"},
        timeout=(20, 240),
    )
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").split(";")[0].lower()
    extensions = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/webp": ".webp",
    }
    extension = extensions.get(content_type)
    if not extension or not response.content:
        preview = response.text[:300] if response.text else "(respons kosong)"
        raise RuntimeError(
            f"Pollinations tidak mengembalikan file gambar (Content-Type: {content_type}). "
            f"Respons: {preview}"
        )

    image_path = destination.with_suffix(extension)
    image_path.write_bytes(response.content)
    return image_path


def main() -> int:
    load_dotenv(BASE_DIR / ".env")
    args = parse_args()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("ERROR: GEMINI_API_KEY belum diatur. Buat file ai-hub/.env terlebih dahulu.")
        return 2

    prompt = (args.prompt or input("Masukkan prompt Anda: ")).strip()
    if not prompt:
        print("Prompt tidak boleh kosong.")
        return 2

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    base_name = f"hasil_{timestamp}"
    text_path = OUTPUT_DIR / f"{base_name}.md"

    try:
        print(f"Meminta jawaban dari Gemini ({args.model})...")
        raw_response = ask_gemini(prompt, api_key, args.model)
        answer, visual_prompt = split_response(raw_response)

        text_path.write_text(
            f"# Hasil AI Hub\n\n"
            f"**Waktu:** {datetime.now().astimezone().isoformat()}\n\n"
            f"## Prompt\n\n{prompt}\n\n"
            f"## Jawaban Gemini\n\n{answer}\n",
            encoding="utf-8",
        )
        print(f"Jawaban teks tersimpan: {text_path}")

        if args.no_image:
            print("Pembuatan gambar dilewati (--no-image).")
        elif visual_prompt:
            print("Membuat gambar melalui Pollinations.ai...")
            try:
                image_path = generate_image(
                    visual_prompt, args.width, args.height, OUTPUT_DIR / base_name
                )
                with text_path.open("a", encoding="utf-8") as output_file:
                    output_file.write(
                        f"\n## Prompt Visual\n\n{visual_prompt}\n\n"
                        f"**File gambar:** {image_path.name}\n"
                    )
                print(f"Gambar tersimpan: {image_path}")
            except requests.RequestException as exc:
                print(f"PERINGATAN: Permintaan gambar gagal: {exc}")
                print("Jawaban teks tetap tersimpan. Coba lagi beberapa saat kemudian.")
            except (RuntimeError, ValueError) as exc:
                print(f"PERINGATAN: Gambar tidak berhasil dibuat: {exc}")
                print("Jawaban teks tetap tersimpan.")
        else:
            print("Gemini tidak memberikan prompt visual; hanya hasil teks yang disimpan.")

        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
