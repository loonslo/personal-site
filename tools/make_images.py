"""生成 PNG 图标和分享图，输出到 static/。内容改动后手动运行一次，结果随仓库提交。

    py -3 tools/make_images.py [--serif 字体路径] [--sans 字体路径]

分享图里的中文用本机字体渲染成图片，不分发字体文件本身。默认使用 Windows 自带的华文宋体和微软雅黑；
如需换成开源的思源宋体 / 思源黑体，用 --serif / --sans 指定字体文件后重新生成。
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PAPER = (244, 239, 230)
INK = (29, 27, 24)
INK2 = (94, 90, 83)
CINNABAR = (181, 68, 44)
LINE = (214, 207, 196)


def seal(size: int, scale: int = 4) -> Image.Image:
    """朱砂方印（白文半月），先放大绘制再缩小，边缘更平滑。"""
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad, radius = s * 4 // 48, s * 4 // 48
    d.rounded_rectangle((pad, pad, s - pad, s - pad), radius=radius, fill=CINNABAR)
    r, c, w = s * 10.5 / 48, s / 2, max(2, round(s * 2.4 / 48))
    d.ellipse((c - r, c - r, c + r, c + r), outline=PAPER, width=w)
    d.pieslice((c - r, c - r, c + r, c + r), 90, 270, fill=PAPER)
    return img.resize((size, size), Image.LANCZOS)


def paper(width: int, height: int, seed: int = 7) -> Image.Image:
    """带细微颗粒的纸色底。"""
    rng = random.Random(seed)
    base = Image.new("RGB", (width, height), PAPER)
    noise = Image.new("L", (width, height))
    noise.putdata([rng.randint(0, 255) for _ in range(width * height)])
    noise = noise.filter(ImageFilter.GaussianBlur(0.6)).point(lambda v: max(0, v - 150) // 7)
    specks = Image.new("RGB", (width, height), INK)
    base.paste(specks, (0, 0), noise)
    return base


def vertical_text(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font, fill, gap: float) -> None:
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill, anchor="mt")
        y += int(font.size * (1 + gap))


def og_image(site: dict, serif_path: str, sans_path: str) -> Image.Image:
    w, h = 1200, 630
    img = paper(w, h)
    d = ImageDraw.Draw(img)
    d.ellipse((760, -260, 1400, 380), outline=LINE, width=2)

    serif_big = ImageFont.truetype(serif_path, 170)
    serif_line = ImageFont.truetype(serif_path, 30)
    serif_lead = ImageFont.truetype(serif_path, 46)
    sans = ImageFont.truetype(sans_path, 26)

    name_x = 1030
    vertical_text(d, name_x, 110, site["name"], serif_big, INK, 0.08)
    stamp = seal(56)
    img.paste(stamp, (name_x - 28, 110 + int(170 * 1.08) * len(site["name"]) + 10), stamp)

    parts = [p.strip("，。 ") for p in site["tagline"].split("，") if p.strip("，。 ")]
    for i, part in enumerate(parts):
        x = name_x - 150 - i * 70
        d.line((x + 35, 70, x + 35, 560), fill=LINE, width=1)
        vertical_text(d, x, 200 + i * 60, part, serif_line, INK2, 0.6)

    lead_lines = ["十年软件从业，测试出身，", "正在转 AI 应用开发。"]
    y = 230
    for line in lead_lines:
        d.text((90, y), line, font=serif_lead, fill=INK)
        y += 74
    d.text((92, y + 30), "所有项目都从这里进。", font=sans, fill=INK2)
    return img


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serif", default=r"C:/Windows/Fonts/STSONG.TTF")
    parser.add_argument("--sans", default=r"C:/Windows/Fonts/msyh.ttc")
    args = parser.parse_args()

    site = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
    static = ROOT / "static"

    icon = Image.new("RGB", (180, 180), CINNABAR)
    mark = seal(180)
    icon.paste(mark, (0, 0), mark)
    icon.save(static / "apple-touch-icon.png", optimize=True)

    og_image(site, args.serif, args.sans).convert("RGB").save(static / "og-image.png", optimize=True)
    print("已生成 static/apple-touch-icon.png、static/og-image.png")


if __name__ == "__main__":
    main()
