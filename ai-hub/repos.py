#!/usr/bin/env python3
"""Read-only local workspace helper for Omah Aksara repositories."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "workspace.json"


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        config = json.load(handle)
    if config.get("version") != 1 or not isinstance(config.get("repositories"), list):
        raise ValueError("Format workspace.json tidak dikenali.")
    return config


def run_git(path: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), *args],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def inspect_repo(item: dict) -> dict:
    path = (BASE_DIR / item["path"]).resolve()
    exists = path.is_dir()
    git_root = run_git(path, "rev-parse", "--show-toplevel") if exists else None
    branch = run_git(path, "branch", "--show-current") if git_root else None
    status = run_git(path, "status", "--short") if git_root else None
    remote = run_git(path, "remote", "get-url", "origin") if git_root else None
    readme_path = path / item.get("readme", "README.md")
    readme = None
    if readme_path.is_file():
        try:
            readme = readme_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            pass
    return {
        "id": item["id"],
        "name": item["name"],
        "expected_remote": item.get("remote", ""),
        "role": item.get("role", ""),
        "path": str(path),
        "exists": exists,
        "is_git": bool(git_root),
        "branch": branch,
        "working_tree": "clean" if status == "" else ("changes" if status else "unknown"),
        "origin": remote,
        "origin_matches": bool(remote and item.get("remote", "").lower() in remote.lower()),
        "readme_available": readme is not None,
        "readme_preview": "\n".join(readme.splitlines()[:12]) if readme else None,
        "sensitive": bool(item.get("sensitive", False)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Periksa workspace repo Omah Aksara secara lokal (read-only)."
    )
    parser.add_argument("command", choices=("list", "status", "inspect"))
    parser.add_argument("repo", nargs="?", help="ID repo untuk perintah inspect.")
    args = parser.parse_args()

    try:
        repositories = [inspect_repo(item) for item in load_config()["repositories"]]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    if args.command == "list":
        for repo in repositories:
            print(f"- {repo['id']}: {repo['name']} — {repo['role']}")
        return 0

    if args.command == "inspect":
        selected = next((repo for repo in repositories if repo["id"] == args.repo), None)
        if not selected:
            parser.error(f"Repo tidak terdaftar: {args.repo}")
        repositories = [selected]

    print("Omah Aksara Workspace — pemeriksaan lokal, read-only")
    for repo in repositories:
        if args.command == "status":
            location = "tersedia" if repo["exists"] else "belum ditemukan"
            git = f"branch={repo['branch'] or '-'}; working-tree={repo['working_tree']}" if repo["is_git"] else "git=tidak terdeteksi"
            print(f"{repo['id']}: {location}; {git}")
            continue
        print(f"\n## {repo['name']} ({repo['id']})")
        print(f"Peran: {repo['role']}")
        print(f"Path: {repo['path']}")
        print(f"Folder tersedia: {'ya' if repo['exists'] else 'belum'}")
        print(f"Git: {'ya' if repo['is_git'] else 'tidak terdeteksi'}")
        print(f"Branch: {repo['branch'] or '-'}")
        print(f"Working tree: {repo['working_tree']}")
        print(f"Origin: {repo['origin'] or '-'}")
        print(f"Origin sesuai registry: {'ya' if repo['origin_matches'] else 'belum terverifikasi'}")
        if repo["readme_preview"]:
            print("\nRingkasan README:")
            print(repo["readme_preview"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
