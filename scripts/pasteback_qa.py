#!/usr/bin/env python3
"""Generate local paste-back QA crops for an ai2psd-struct package.

The script is intentionally conservative: it creates comparison images from
screen-map assetUsages, but it does not auto-approve them. A reviewer must
inspect the output before writing localPastebackStatus="passed".
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_box(obj: dict[str, Any] | None) -> tuple[float, float, float, float] | None:
    if not isinstance(obj, dict):
        return None
    try:
        x = float(obj.get("x", 0))
        y = float(obj.get("y", 0))
        width = float(obj.get("width", 0))
        height = float(obj.get("height", 0))
    except (TypeError, ValueError):
        return None
    if width <= 0 or height <= 0:
        return None
    return x, y, width, height


def content_bbox(asset: dict[str, Any]) -> tuple[float, float, float, float] | None:
    bbox = read_box(asset.get("contentBBox"))
    if bbox:
        return bbox
    validation = asset.get("validation") if isinstance(asset.get("validation"), dict) else {}
    return read_box(validation.get("contentBBox"))


def asset_usage_screen(screen: Image.Image, asset_image: Image.Image, bbox: tuple[float, float, float, float], placement: tuple[float, float, float, float]) -> Image.Image:
    canvas = Image.new("RGBA", screen.size, (255, 255, 255, 0))
    bbox_x, bbox_y, bbox_w, bbox_h = bbox
    target_x, target_y, target_w, target_h = placement
    scale_x = target_w / bbox_w
    scale_y = target_h / bbox_h
    scale = (scale_x + scale_y) / 2.0
    new_size = (max(1, round(asset_image.width * scale)), max(1, round(asset_image.height * scale)))
    resized = asset_image.resize(new_size, Image.LANCZOS)
    paste_x = round(target_x - bbox_x * scale)
    paste_y = round(target_y - bbox_y * scale)
    canvas.alpha_composite(resized, (paste_x, paste_y))
    return canvas


def padded_crop_box(placement: tuple[float, float, float, float], screen_size: tuple[int, int], pad: int = 32) -> tuple[int, int, int, int]:
    x, y, w, h = placement
    left = max(0, int(x) - pad)
    top = max(0, int(y) - pad)
    right = min(screen_size[0], int(x + w) + pad)
    bottom = min(screen_size[1], int(y + h) + pad)
    return left, top, right, bottom


def checker(size: tuple[int, int]) -> Image.Image:
    out = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(out)
    step = 12
    for y in range(0, size[1], step):
        for x in range(0, size[0], step):
            fill = (236, 240, 243, 255) if ((x // step + y // step) % 2 == 0) else (255, 255, 255, 255)
            draw.rectangle((x, y, min(x + step - 1, size[0] - 1), min(y + step - 1, size[1] - 1)), fill=fill)
    return out


def make_sheet(source_crop: Image.Image, paste_crop: Image.Image) -> Image.Image:
    source = source_crop.convert("RGBA")
    paste = paste_crop.convert("RGBA")
    paste_bg = checker(paste.size)
    paste_bg.alpha_composite(paste)
    width = source.width + paste.width
    height = max(source.height, paste.height) + 28
    sheet = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    sheet.alpha_composite(source, (0, 28))
    sheet.alpha_composite(paste_bg, (source.width, 28))
    draw = ImageDraw.Draw(sheet)
    draw.text((8, 8), "source crop", fill=(31, 41, 55, 255))
    draw.text((source.width + 8, 8), "asset at targetPlacement", fill=(31, 41, 55, 255))
    return sheet.convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_root")
    parser.add_argument("--screen", help="Limit to one screen id, such as P01")
    parser.add_argument("--out-dir", default="99-working-sources/pasteback-qa")
    args = parser.parse_args()

    root = Path(args.package_root)
    screen_map = load_json(root / "04-manifest" / "screen-map.json")
    asset_map = load_json(root / "04-manifest" / "asset-map.json")
    assets = {asset.get("id"): asset for asset in asset_map.get("assets", []) if asset.get("id")}
    out_root = root / args.out_dir
    made = 0
    skipped = 0

    for screen in screen_map.get("screens", []):
        sid = str(screen.get("id", ""))
        if args.screen and sid != args.screen:
            continue
        screen_file = screen.get("filename")
        if not screen_file:
            skipped += 1
            continue
        screen_path = root / screen_file
        if not screen_path.exists():
            skipped += 1
            continue
        source_screen = Image.open(screen_path).convert("RGBA")
        for usage in screen.get("assetUsages") or []:
            if not isinstance(usage, dict):
                continue
            asset_id = usage.get("assetId")
            asset = assets.get(asset_id)
            placement = read_box(usage.get("targetPlacement"))
            bbox = content_bbox(asset) if asset else None
            if not asset or not placement or not bbox:
                skipped += 1
                continue
            asset_path = root / str(asset.get("filename", ""))
            if not asset_path.exists():
                skipped += 1
                continue
            asset_image = Image.open(asset_path).convert("RGBA")
            paste_canvas = asset_usage_screen(source_screen, asset_image, bbox, placement)
            crop_box = padded_crop_box(placement, source_screen.size)
            source_crop = source_screen.crop(crop_box)
            paste_crop = paste_canvas.crop(crop_box)
            page_out = out_root / sid
            page_out.mkdir(parents=True, exist_ok=True)
            safe_id = str(asset_id).replace(".", "-").replace("/", "-")
            out_path = page_out / f"{sid}-{safe_id}-pasteback.png"
            make_sheet(source_crop, paste_crop).save(out_path)
            made += 1

    print(f"pasteback QA sheets: {made}")
    print(f"skipped usages: {skipped}")
    print(f"output: {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
