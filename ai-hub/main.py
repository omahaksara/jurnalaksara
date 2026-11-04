#!/usr/bin/env python3
"""Jurnal Aksara AI Hub: Gemini text/code + Pollinations image generation."""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
DEFAULT_MODEL = "gemini-2.5-flash"
POLLINATIONS_URL = "https://gen.pollinations.ai/image/"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Buat teks/kode dengan Gemini dan ilustrasi dengan Pollinations.ai."
    )
    parser.add_argument("-p", "--prompt", help="Prompt; jika kosong, input diminta di terminal.")
    parser.add_argument("--model", default=None, help="Model Gemini (default dari .env atau bawaan).")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--no-image", action="store_true", help="Lewati pembuatan gambar.")
    return parser.parse_args()


def ask_gemini(prompt: str, api_key: str, model_name: str) -> str:
    client = genai.Client(api_key=api_key)
    instruction = f"""
Anda adalah asisten kreatif dan teknis untuk Jurnal Aksara.
Jawab permintaan pengguna dengan jelas, berguna, dan dalam Bahasa Indonesia
(kecuali diminta bahasa lain). Jika diminta membuat kode, berikan kode lengkap
yang dapat dijalankan serta petunjuk singkat bila diperlukan.

Setelah jawaban, buat satu prompt ilustrasi berbahasa Inggris yang relevan.
Jangan meminta gambar untuk tugas yang murni teknis atau tidak membutuhkan
visual. Jangan masukkan tulisan, watermark, atau tipografi ke dalam gambar.

Gunakan format persis:
===JAWABAN===
[jawaban lengkap]
===PROMPT_VISUAL===
[prompt visual atau NONE]
===AKHIR_PROMPT_VISUAL===

Permintaan pengguna:
{prompt}
"""
    response = client.models.generate_content(
        model=model_name,
        contents=instruction,
        config=types.GenerateContentConfig(temperature=0.7),
    )
    answer = response.text
    if not answer:
        raise RuntimeError("Gemini tidak mengembalikan teks. Periksa API key, kuota, dan nama model.")
    return answer.strip()


def split_response(response: str) -> tuple[str, str | None]:
    match = re.search(
        r"===JAWABAN===\s*(.*?)\s*===PROMPT_VISUAL===\s*(.*?)\s*===AKHIR_PROMPT_VISUAL===",
        response,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return response.strip(), None
    answer, visual = match.group(1).strip(), match.group(2).strip()
    return answer, None if not visual or visual.upper() == "NONE" else visual


def generate_image(
    prompt: str, api_key: str, width: int, height: int, destination: Path
) -> Path:
    if not (256 <= width <= 2048 and 256 <= height <= 2048):
        raise ValueError("Ukuran gambar harus antara 256 dan 2048 piksel.")
    if not api_key:
        raise RuntimeError(
            "POLLINATIONS_API_KEY belum diatur. Buat key di https://enter.pollinations.ai/ "
            "dan simpan sebagai POLLINATIONS_API_KEY di file .env."
        )

    url = POLLINATIONS_URL + quote(prompt, safe="")
    response = requests.get(
        url,
        params={"model": os.getenv("POLLINATIONS_MODEL", "zimage"),
                "width": width, "height": height},
        headers={"Authorization": f"Bearer {api_key}",
                 "User-Agent": "JurnalAksara-AIHub/1.1"},
        timeout=(20, 300),
    )
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "").split(";")[0].lower()
    extensions = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
    extension = extensions.get(content_type)
    if not extension or not response.content:
        detail = response.text[:300] if response.text else "(respons kosong)"
        raise RuntimeError(f"Respons Pollinations bukan gambar ({content_type}): {detail}")
    image_path = destination.with_suffix(extension)
    image_path.write_bytes(response.content)
    return image_path


def main() -> int:
    load_dotenv(BASE_DIR / ".env")
    args = parse_args()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    pollinations_key = os.getenv("POLLINATIONS_API_KEY", "").strip()
    model_name = args.model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    if not gemini_key:
        print("ERROR: GEMINI_API_KEY belum diatur di file ai-hub/.env.")
        return 2
    prompt = (args.prompt or input("Masukkan prompt Anda: ")).strip()
    if not prompt:
        print("Prompt tidak boleh kosong.")
        return 2

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    base = OUTPUT_DIR / f"hasil_{stamp}"
    text_path = base.with_suffix(".md")

    try:
        print(f"Meminta jawaban dari Gemini ({model_name})...")
        raw = ask_gemini(prompt, gemini_key, model_name)
        answer, visual_prompt = split_response(raw)
        text_path.write_text(
            f"# Hasil AI Hub\n\n**Waktu:** {datetime.now().astimezone().isoformat()}\n\n"
            f"## Prompt\n\n{prompt}\n\n## Jawaban Gemini\n\n{answer}\n",
            encoding="utf-8",
        )
        print(f"Teks tersimpan: {text_path}")

        if args.no_image:
            print("Gambar dilewati (--no-image).")
        elif visual_prompt:
            print("Membuat ilustrasi melalui Pollinations.ai...")
            try:
                image_path = generate_image(
                    visual_prompt, pollinations_key, args.width, args.height, base
                )
                with text_path.open("a", encoding="utf-8") as output:
                    output.write(
                        f"\n## Prompt Visual\n\n{visual_prompt}\n\n"
                        f"**File gambar:** {image_path.name}\n"
                    )
                print(f"Gambar tersimpan: {image_path}")
            except (requests.RequestException, RuntimeError, ValueError) as exc:
                print(f"PERINGATAN: Gambar gagal dibuat: {exc}")
                print("Jawaban teks tetap tersimpan.")
        else:
            print("Tidak ada prompt visual; hanya hasil teks yang disimpan.")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
