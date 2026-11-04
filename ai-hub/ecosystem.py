#!/usr/bin/env python3
"""Read-only Omah Aksara project index for AI Hub.

Only public repository metadata and explicitly configured README files are read.
No client records, student records, secrets, or repository writes are accessed.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
REGISTRY_PATH = BASE_DIR / "ecosystem.json"
OUTPUT_DIR = BASE_DIR / "output"
API_ROOT = "https://api.github.com"


def load_registry() -> dict:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("repositories"), dict):
        raise ValueError("Format ecosystem.json tidak dikenal.")
    return data


def github_get(path: str) -> dict:
    response = requests.get(
        f"{API_ROOT}/{path.lstrip('/')}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "JurnalAksara-AIHub/1.0",
        },
        timeout=(10, 30),
    )
    response.raise_for_status()
    return response.json()


def inspect_repo(key: str, config: dict) -> str:
    full_name = config["full_name"]
    metadata = github_get(f"repos/{full_name}")
    readme_path = config.get("readme", "README.md")
    readme = github_get(f"repos/{full_name}/readme")
    import base64

    content = base64.b64decode(readme["content"]).decode("utf-8", errors="replace")
    lines = [
        f"# {config.get('name', full_name)}",
        "",
        f"- Repo: https://github.com/{full_name}",
        f"- Peran: {config.get('role', 'Belum ditentukan')}",
        f"- Branch utama: {metadata.get('default_branch', 'unknown')}",
        f"- Visibilitas: {metadata.get('visibility', 'unknown')}",
        f"- README: {readme_path}",
        f"- Akses: hanya baca README publik; tidak mengambil data operasional.",
        "",
        "## README",
        "",
        content.strip(),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lihat peta proyek Omah Aksara dan baca README publik (read-only)."
    )
    parser.add_argument("--list", action="store_true", help="Tampilkan semua proyek terdaftar.")
    parser.add_argument("--inspect", help="Nama kunci repo, misalnya invitation atau ruangkelas.")
    parser.add_argument("--snapshot", action="store_true", help="Simpan ringkasan README semua repo ke output/.")
    args = parser.parse_args()

    try:
        registry = load_registry()
        repos = registry["repositories"]
        if args.list or not (args.inspect or args.snapshot):
            for key, item in repos.items():
                print(f"{key:14} {item.get('name', item['full_name'])} — {item.get('role', '')}")
            return 0

        if args.inspect:
            if args.inspect not in repos:
                raise ValueError(f"Repo '{args.inspect}' tidak ada di ecosystem.json.")
            print(inspect_repo(args.inspect, repos[args.inspect]))
            return 0

        if args.snapshot:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
            target = OUTPUT_DIR / f"ecosystem_snapshot_{stamp}.md"
            sections = ["# Omah Aksara — Project Snapshot", "",
                        f"Generated: {datetime.now().astimezone().isoformat()}",
                        "", "> Snapshot read-only dari README publik. Bukan salinan data pelanggan/siswa.", ""]
            for key, item in repos.items():
                if not item.get("allow_readme_snapshot", False):
                    continue
                print(f"Membaca README: {item['full_name']}...")
                sections.append(inspect_repo(key, item))
                sections.append("---")
            target.write_text("\n".join(sections), encoding="utf-8")
            print(f"Snapshot tersimpan: {target}")
            return 0
    except (OSError, ValueError, requests.RequestException, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
