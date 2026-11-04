#!/usr/bin/env python3
"""Run a local ComfyUI API workflow and download generated image/video outputs."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
MEDIA_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".webm", ".mov"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Jalankan workflow gambar/video ComfyUI lokal dan simpan hasilnya."
    )
    parser.add_argument("--workflow", required=True, help="File workflow ComfyUI format API (JSON).")
    parser.add_argument("--prompt", help="Teks prompt opsional untuk mengganti input prompt pada node.")
    parser.add_argument(
        "--prompt-node-id",
        help="ID node yang input teksnya akan diganti; harus cocok dengan workflow Anda.",
    )
    parser.add_argument("--timeout", type=int, default=1800, help="Batas tunggu dalam detik (default 1800).")
    parser.add_argument("--poll-interval", type=float, default=2.0)
    return parser.parse_args()


def patch_prompt(workflow: dict, node_id: str, prompt: str) -> None:
    node = workflow.get(str(node_id))
    if not isinstance(node, dict) or not isinstance(node.get("inputs"), dict):
        raise ValueError(f"Node {node_id!r} tidak ditemukan atau tidak memiliki inputs.")
    inputs = node["inputs"]
    candidates = [key for key in inputs if key.lower() in {"text", "prompt", "positive", "positive_prompt"}]
    if len(candidates) != 1:
        raise ValueError(
            f"Tidak bisa menentukan field prompt pada node {node_id}. "
            f"Field tersedia: {', '.join(inputs.keys())}. Edit workflow atau sesuaikan node."
        )
    inputs[candidates[0]] = prompt


def main() -> int:
    load_dotenv(BASE_DIR / ".env")
    args = parse_args()
    base_url = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
    workflow_path = Path(args.workflow).expanduser()
    if not workflow_path.is_absolute():
        workflow_path = (Path.cwd() / workflow_path).resolve()
    if not workflow_path.is_file():
        print(f"ERROR: Workflow tidak ditemukan: {workflow_path}", file=sys.stderr)
        return 2

    try:
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
        if not isinstance(workflow, dict) or not workflow:
            raise ValueError("Workflow harus berupa objek JSON ComfyUI API yang tidak kosong.")
        if args.prompt and not args.prompt_node_id:
            raise ValueError("Jika memakai --prompt, sertakan --prompt-node-id sesuai ID node workflow.")
        if args.prompt_node_id:
            if not args.prompt:
                raise ValueError("--prompt-node-id membutuhkan --prompt.")
            patch_prompt(workflow, args.prompt_node_id, args.prompt)

        client_id = str(uuid.uuid4())
        print(f"Mengirim workflow ke ComfyUI: {base_url}")
        response = requests.post(
            f"{base_url}/prompt",
            json={"prompt": workflow, "client_id": client_id},
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        prompt_id = payload.get("prompt_id")
        if not prompt_id:
            raise RuntimeError(f"ComfyUI tidak memberi prompt_id: {payload}")

        print(f"Job diterima: {prompt_id}. Menunggu hasil...")
        deadline = time.monotonic() + max(30, args.timeout)
        entry = None
        while time.monotonic() < deadline:
            history_response = requests.get(f"{base_url}/history/{prompt_id}", timeout=30)
            history_response.raise_for_status()
            history = history_response.json()
            entry = history.get(prompt_id)
            if entry and entry.get("outputs") and entry.get("status", {}).get("completed", True):
                break
            time.sleep(max(0.5, args.poll_interval))
        else:
            raise TimeoutError(
                f"ComfyUI belum selesai dalam {args.timeout} detik. Job {prompt_id} mungkin masih berjalan."
            )

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        saved = []
        for node_id, node_output in entry.get("outputs", {}).items():
            for kind in ("images", "gifs", "videos"):
                for item in node_output.get(kind, []):
                    filename = item.get("filename")
                    if not filename:
                        continue
                    params = {
                        "filename": filename,
                        "subfolder": item.get("subfolder", ""),
                        "type": item.get("type", "output"),
                    }
                    media = requests.get(f"{base_url}/view", params=params, timeout=(20, 600))
                    media.raise_for_status()
                    suffix = Path(filename).suffix.lower()
                    if suffix not in MEDIA_EXTENSIONS:
                        suffix = ".bin"
                    destination = OUTPUT_DIR / f"comfy_{prompt_id[:8]}_{node_id}_{len(saved)+1}{suffix}"
                    destination.write_bytes(media.content)
                    saved.append(destination)

        if not saved:
            raise RuntimeError(
                "Workflow selesai tetapi tidak ada file media yang dikenali. "
                "Pastikan workflow memiliki output node dan menghasilkan images/gifs/videos."
            )
        print("Berhasil. File tersimpan:")
        for path in saved:
            print(f" - {path}")
        return 0

    except (requests.RequestException, ValueError, RuntimeError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
