# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pillow",
#     "tomlkit",
# ]
# ///

"""
更新论坛表情包。

运行方法：uv run --script update_stickers.py
"""

import os
import hashlib
import tomllib
import shutil
from PIL import Image
from pathlib import Path
from typing import List, Dict, cast
import argparse
from tomlkit import aot, document, item as toml_item # type: ignore

SUPPORTED_INPUT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}
OUTPUT_WEBP_QUALITY = 80  # Quality for WebP conversion (0-100)
RESIZE_WIDTH = 150  # Resize width for WebP conversion
URL_PREFIX = "https://static.fduhole.com/stickers/"


def convert_to_webp(input_path: Path, output_path: Path, quality: int):
    img = Image.open(input_path)
    # Ensure the image is in RGB or RGBA mode for WebP saving
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    # Resize to maintain aspect ratio
    if img.width > RESIZE_WIDTH:
        ratio = RESIZE_WIDTH / img.width
        new_height = int(img.height * ratio)
        img = img.resize((RESIZE_WIDTH, new_height), Image.Resampling.LANCZOS)
    img.save(output_path, "webp", quality=quality)


def calc_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--toml",
        required=False,
        help="original toml file path. If provided, will only process images that are not in the toml file. (default: ../public/tmp_wait_for_json_editor.toml)",
        default="../public/tmp_wait_for_json_editor.toml",
    )
    parser.add_argument(
        "--sticker_folder",
        required=False,
        help="sticker folder path. (default: current folder)",
        default=".",
    )
    parser.add_argument(
        "--output",
        required=False,
        help="output directory for webp files. (default: ../public/stickers/)",
        default="../public/stickers/",
    )
    args = parser.parse_args()

    original_id2sha256: Dict[str, str] = {}
    if args.toml:
        with open(args.toml, "r") as f:
            toml_data = tomllib.loads(f.read())
        sticker_data = cast(List[Dict[str, str]], toml_data.get("sticker", []))
        existing_ids = {item["id"] for item in sticker_data}
        print(f"已存在的表情包 ID: {existing_ids}")
        for item in sticker_data:
            original_id2sha256[item["id"]] = item["sha256"]

    cwd = args.sticker_folder
    print(f"在 {cwd} 中扫描图片")

    output_data: List[Dict[str, str | Path]] = []
    for filename in os.listdir(cwd):
        filepath = Path(cwd) / filename
        if os.path.isfile(filepath):
            name, ext = os.path.splitext(filename)
            if ext.lower() in SUPPORTED_INPUT_EXTENSIONS:
                print(f"处理 {filename}")
                webp_filepath = filepath.with_suffix(".webp")
                convert_to_webp(
                    filepath, output_path=webp_filepath, quality=OUTPUT_WEBP_QUALITY
                )
                sha256 = calc_sha256(webp_filepath)
                output_data.append(
                    {"id": name, "sha256": sha256, "path": webp_filepath}
                )

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    for item in output_data:
        id = cast(str, item["id"])
        path = cast(Path, item.pop("path"))
        if original_id2sha256.get(id) == item["sha256"]:
            print(f"跳过 {id}，已存在且未修改")
            continue
        dest_path = output_dir / f"{id}.webp"
        print(f"复制 {path} -> {dest_path}")
        shutil.copy(path, dest_path)
        item["url"] = f"{URL_PREFIX}{id}.webp"
        print(f"完成，链接：{item['url']}")

    # Save the output data to a file
    doc = document()
    for item in cast(List[Dict[str, str]], output_data):
        a = aot()
        a.append(toml_item(item)) # type: ignore
        doc.append("sticker", a)
    toml_output = doc.as_string()
        
    print("\n--- TOML 输出，请复制到文件中 ---")
    print(toml_output)


if __name__ == "__main__":
    main()
