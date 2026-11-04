#!/usr/bin/env python3
"""Generate a cloud AI video with Magic Hour and save it in ai-hub/output."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from magic_hour import Client

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Buat video AI online melalui Magic Hour (tanpa GPU lokal)."
    )
    parser.add_argument("--prompt", required=True, help="Deskripsi video yang ingin dibuat.")
    parser.add_argument("--name", default="Jurnal Aksara AI Video", help="Nama proyek.")
    parser.add_argument("--seconds", type=int, default=5, help="Durasi video (default 5 detik).")
    parser.add_argument("--aspect-ratio", choices=("9:16", "16:9", "1:1"), default="9:16")
    parser.add_argument("--resolution", choices=("480p", "720p", "1080p"), default="480p")
    parser.add_argument("--model", default=None, help="Model Magic Hour; default wan-2.2.")
    parser.add_argument(
        "--confirm-credit-use",
        action="store_true",
        help="Wajib disertakan karena setiap generasi menggunakan kredit akun Magic Hour.",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv(BASE_DIR / ".env")
    args = parse_args()
    api_key = os.getenv("MAGIC_HOUR_API_KEY", "").strip()
    if not api_key:
        print(
            "ERROR: MAGIC_HOUR_API_KEY belum diisi di ai-hub/.env. "
            "Buat key di https://magichour.ai/developer",
            file=sys.stderr,
        )
        return 2

    if not args.confirm_credit_use:
        print(
            "PERLU KONFIRMASI: permintaan video akan memakai kredit Magic Hour.\n"
            "Periksa saldo dan harga di dashboard, lalu jalankan ulang dengan "
            "--confirm-credit-use jika setuju.",
            file=sys.stderr,
        )
        return 2

    if not 3 <= args.seconds <= 15:
        print("Untuk preset Wan 2.2, durasi harus 3–15 detik.", file=sys.stderr)
        return 2
    if args.resolution != "480p":
        print(
            "Preset gratis/hemat AI Hub memakai 480p. Resolusi lebih tinggi mungkin "
            "memerlukan paket atau kredit lebih banyak. Periksa akun sebelum mengubahnya.",
            file=sys.stderr,
        )
        return 2

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model = args.model or os.getenv("MAGIC_HOUR_VIDEO_MODEL", "wan-2.2")
    try:
        client = Client(token=api_key)
        print(f"Mengirim permintaan ke Magic Hour: model={model}, {args.seconds}s, {args.resolution}")
        result = client.v1.text_to_video.generate(
            name=args.name,
            end_seconds=float(args.seconds),
            aspect_ratio=args.aspect_ratio,
            style={"prompt": args.prompt},
            model=model,
            resolution=args.resolution,
            wait_for_completion=True,
            download_outputs=True,
            download_directory=str(OUTPUT_DIR),
        )

        paths = getattr(result, "downloaded_paths", None) or []
        print(f"Status proyek: {getattr(result, 'status', 'selesai')}")
        print(f"ID proyek: {getattr(result, 'id', 'tidak tersedia')}")
        if paths:
            print("Video berhasil diunduh:")
            for path in paths:
                print(f" - {path}")
        else:
            print(
                "Job telah dikirim/diproses, tetapi SDK tidak mengembalikan path unduhan. "
                "Periksa proyek di https://magichour.ai/my-library"
            )
        return 0
    except Exception as exc:
        message = str(exc)
        print(f"ERROR saat membuat video: {message}", file=sys.stderr)
        print(
            "Jangan langsung mengulangi permintaan jika status job belum jelas; "
            "periksa https://magichour.ai/my-library agar tidak membuat job ganda.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
