"""Generate all brand assets from the master SVG artboard.

Reads ``localm_tuts_brands.svg`` and writes distributable SVG + PNG files
into ``dist/localm/``.  Every SVG that represents an icon, logo, or mark is
**transparent** (no background rectangle).  The *only* exception is the
``og-image-template`` which requires a solid background for social cards.

PNG conversion uses ImageMagick 7 (``magick``) with ``-background none``
*before* the input so that SVG transparency is preserved in the raster output.

Run::

    python scripts/generate_localm_brand_assets.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import TypeAlias

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
SOURCE_BOARD = ROOT / "localm_tuts_brands.svg"
DIST = ROOT / "dist" / "localm"

# ---------------------------------------------------------------------------
# Shared SVG <defs> block — injected into every generated SVG
# ---------------------------------------------------------------------------

COMMON_DEFS = """\
<defs>
  <style>
    .tech-text { font-family: 'Share Tech Mono', 'Consolas', 'Courier New', monospace; }
    .sans-text { font-family: 'Outfit', 'Segoe UI', Roboto, Arial, sans-serif; }
  </style>
  <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#00F5FF"/>
    <stop offset="35%" stop-color="#2932FF"/>
    <stop offset="70%" stop-color="#A838FF"/>
    <stop offset="100%" stop-color="#FF9A44"/>
  </linearGradient>
  <linearGradient id="left-grad" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#00E1FF"/>
    <stop offset="100%" stop-color="#FFB03A"/>
  </linearGradient>
  <linearGradient id="slash-grad" x1="0%" y1="100%" x2="0%" y2="0%">
    <stop offset="0%" stop-color="#A838FF"/>
    <stop offset="100%" stop-color="#4FACFE"/>
  </linearGradient>
  <linearGradient id="right-grad" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#00FFB2"/>
    <stop offset="100%" stop-color="#9D00FF"/>
  </linearGradient>
  <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="2.3" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <!-- gradient mark — dark-filled circle, neon strokes -->
  <g id="logo-mark">
    <circle cx="100" cy="100" r="96" fill="#0B0B0F" stroke="url(#border-grad)" stroke-width="4"/>
    <g stroke-width="9" stroke-linecap="round" stroke-linejoin="round" fill="none" filter="url(#neon-glow)">
      <path d="M 65 65 L 35 100 L 65 135" stroke="url(#left-grad)"/>
      <path d="M 112 63 L 82 137" stroke="url(#slash-grad)"/>
      <path d="M 135 65 L 165 100 L 135 135" stroke="url(#right-grad)"/>
    </g>
  </g>
  <!-- monochrome white — transparent fill, white strokes -->
  <g id="logo-mark-white">
    <circle cx="100" cy="100" r="96" fill="none" stroke="#FFFFFF" stroke-width="4"/>
    <g stroke-width="9" stroke-linecap="round" stroke-linejoin="round" fill="none" stroke="#FFFFFF">
      <path d="M 65 65 L 35 100 L 65 135"/>
      <path d="M 112 63 L 82 137"/>
      <path d="M 135 65 L 165 100 L 135 135"/>
    </g>
  </g>
  <!-- monochrome dark — transparent fill, dark strokes -->
  <g id="logo-mark-dark">
    <circle cx="100" cy="100" r="96" fill="none" stroke="#0F172A" stroke-width="4"/>
    <g stroke-width="9" stroke-linecap="round" stroke-linejoin="round" fill="none" stroke="#0F172A">
      <path d="M 65 65 L 35 100 L 65 135"/>
      <path d="M 112 63 L 82 137"/>
      <path d="M 135 65 L 165 100 L 135 135"/>
    </g>
  </g>
  <!-- favicon mark — shifted up to allow embedded text -->
  <g id="favicon-mark">
    <circle cx="100" cy="100" r="96" fill="#0B0B0F" stroke="url(#border-grad)" stroke-width="4"/>
    <g stroke-width="9" stroke-linecap="round" stroke-linejoin="round" fill="none" filter="url(#neon-glow)">
      <path d="M 65 50 L 35 85 L 65 120" stroke="url(#left-grad)"/>
      <path d="M 112 48 L 82 122" stroke="url(#slash-grad)"/>
      <path d="M 135 50 L 165 85 L 135 120" stroke="url(#right-grad)"/>
    </g>
  </g>
  <!-- favicon with embedded "localm" wordmark -->
  <g id="favicon-full">
    <use xlink:href="#favicon-mark" href="#favicon-mark"/>
    <text class="tech-text" x="100" y="162" fill="#F8FAFC" font-size="26"
          font-weight="bold" text-anchor="middle" letter-spacing="2">
      localm<tspan font-size="11" fill="#3B82F6" dy="-12"
                   font-family="Outfit, Arial, sans-serif">™</tspan>
    </text>
  </g>
</defs>"""


def _svg(view_box: str, body: str) -> str:
    """Return a complete SVG document with shared defs."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg"'
        ' xmlns:xlink="http://www.w3.org/1999/xlink"'
        f' viewBox="{view_box}">'
        f"{COMMON_DEFS}{body}</svg>"
    )


# ---------------------------------------------------------------------------
# SVG templates — ALL transparent except og-image-template
# ---------------------------------------------------------------------------

_USE = 'xlink:href="#{0}" href="#{0}"'

SVG_TEMPLATES: dict[str, str] = {
    # ── Icon marks (200×200, transparent) ──────────────────────────────
    "icon-mark-gradient.svg": _svg(
        "0 0 200 200",
        f'<use {_USE.format("logo-mark")}/>',
    ),
    "icon-mark-white.svg": _svg(
        "0 0 200 200",
        f'<use {_USE.format("logo-mark-white")}/>',
    ),
    "icon-mark-dark.svg": _svg(
        "0 0 200 200",
        f'<use {_USE.format("logo-mark-dark")}/>',
    ),
    # ── Favicon with text (200×200, transparent) ──────────────────────
    "favicon-full.svg": _svg(
        "0 0 200 200",
        f'<use {_USE.format("favicon-full")}/>',
    ),
    # ── Horizontal logos (980×220, transparent) ───────────────────────
    "logo-horizontal-color.svg": _svg(
        "0 0 980 220",
        f'<g transform="translate(20,10)"><use {_USE.format("logo-mark")}/></g>'
        '<text x="250" y="138">'
        '<tspan class="tech-text" font-size="96" font-weight="700" fill="#FFFFFF">localm</tspan>'
        '<tspan class="sans-text" font-size="40" font-weight="700" fill="#4FACFE" dy="-44" dx="3">™</tspan>'
        '<tspan class="sans-text" font-size="96" font-weight="300" fill="#94A3B8" dy="44" dx="24">TUTS</tspan>'
        "</text>",
    ),
    "logo-horizontal-light.svg": _svg(
        "0 0 980 220",
        f'<g transform="translate(20,10)"><use {_USE.format("logo-mark-white")}/></g>'
        '<text x="250" y="138">'
        '<tspan class="tech-text" font-size="96" font-weight="700" fill="#FFFFFF">localm</tspan>'
        '<tspan class="sans-text" font-size="40" font-weight="700" fill="#FFFFFF" dy="-44" dx="3">™</tspan>'
        '<tspan class="sans-text" font-size="96" font-weight="300" fill="#94A3B8" dy="44" dx="24">TUTS</tspan>'
        "</text>",
    ),
    "logo-horizontal-dark.svg": _svg(
        "0 0 980 220",
        f'<g transform="translate(20,10)"><use {_USE.format("logo-mark-dark")}/></g>'
        '<text x="250" y="138">'
        '<tspan class="tech-text" font-size="96" font-weight="700" fill="#0F172A">localm</tspan>'
        '<tspan class="sans-text" font-size="40" font-weight="700" fill="#0F172A" dy="-44" dx="3">™</tspan>'
        '<tspan class="sans-text" font-size="96" font-weight="300" fill="#475569" dy="44" dx="24">TUTS</tspan>'
        "</text>",
    ),
    # ── Wordmark-only logos (730×120, transparent, tight bbox) ───────
    "wordmark-horizontal-color.svg": _svg(
        "0 0 730 120",
        '<text x="0" y="60" dominant-baseline="middle">'
        '<tspan class="tech-text" font-size="96" font-weight="700" fill="#FFFFFF">localm</tspan>'
        '<tspan class="sans-text" font-size="40" font-weight="700" fill="#4FACFE" dy="-44" dx="3">™</tspan>'
        '<tspan class="sans-text" font-size="96" font-weight="300" fill="#94A3B8" dy="44" dx="24">TUTS</tspan>'
        "</text>",
    ),
    "wordmark-horizontal-light.svg": _svg(
        "0 0 730 120",
        '<text x="0" y="60" dominant-baseline="middle">'
        '<tspan class="tech-text" font-size="96" font-weight="700" fill="#FFFFFF">localm</tspan>'
        '<tspan class="sans-text" font-size="40" font-weight="700" fill="#FFFFFF" dy="-44" dx="3">™</tspan>'
        '<tspan class="sans-text" font-size="96" font-weight="300" fill="#94A3B8" dy="44" dx="24">TUTS</tspan>'
        "</text>",
    ),
    "wordmark-horizontal-dark.svg": _svg(
        "0 0 730 120",
        '<text x="0" y="60" dominant-baseline="middle">'
        '<tspan class="tech-text" font-size="96" font-weight="700" fill="#0F172A">localm</tspan>'
        '<tspan class="sans-text" font-size="40" font-weight="700" fill="#0F172A" dy="-44" dx="3">™</tspan>'
        '<tspan class="sans-text" font-size="96" font-weight="300" fill="#475569" dy="44" dx="24">TUTS</tspan>'
        "</text>",
    ),
    # ── Stacked logos (360×440, transparent) ──────────────────────────
    "logo-stacked-color.svg": _svg(
        "0 0 360 440",
        f'<g transform="translate(80,30)"><use {_USE.format("logo-mark")}/></g>'
        '<text class="tech-text" x="180" y="315" font-size="72" font-weight="700" fill="#FFFFFF" text-anchor="middle">'
        'localm<tspan class="sans-text" font-size="28" fill="#4FACFE" dy="-28" dx="2">™</tspan>'
        "</text>"
        '<text class="sans-text" x="180" y="385" font-size="60" font-weight="300" fill="#94A3B8" text-anchor="middle" letter-spacing="4">TUTS</text>',
    ),
    "logo-stacked-light.svg": _svg(
        "0 0 360 440",
        f'<g transform="translate(80,30)"><use {_USE.format("logo-mark-white")}/></g>'
        '<text class="tech-text" x="180" y="315" font-size="72" font-weight="700" fill="#FFFFFF" text-anchor="middle">'
        'localm<tspan class="sans-text" font-size="28" fill="#FFFFFF" dy="-28" dx="2">™</tspan>'
        "</text>"
        '<text class="sans-text" x="180" y="385" font-size="60" font-weight="300" fill="#94A3B8" text-anchor="middle" letter-spacing="4">TUTS</text>',
    ),
    "logo-stacked-dark.svg": _svg(
        "0 0 360 440",
        f'<g transform="translate(80,30)"><use {_USE.format("logo-mark-dark")}/></g>'
        '<text class="tech-text" x="180" y="315" font-size="72" font-weight="700" fill="#0F172A" text-anchor="middle">'
        'localm<tspan class="sans-text" font-size="28" fill="#0F172A" dy="-28" dx="2">™</tspan>'
        "</text>"
        '<text class="sans-text" x="180" y="385" font-size="60" font-weight="300" fill="#475569" text-anchor="middle" letter-spacing="4">TUTS</text>',
    ),
    # ── OG image template (1200×630, SOLID dark background) ──────────
    "og-image-template.svg": _svg(
        "0 0 1200 630",
        '<rect width="1200" height="630" fill="#07070A"/>'
        f'<g transform="translate(80,205)"><use {_USE.format("logo-mark")} transform="scale(1.1)"/></g>'
        '<text x="360" y="355">'
        '<tspan class="tech-text" font-size="120" font-weight="700" fill="#FFFFFF">localm</tspan>'
        '<tspan class="sans-text" font-size="50" font-weight="700" fill="#4FACFE" dy="-54" dx="3">™</tspan>'
        '<tspan class="sans-text" font-size="120" font-weight="300" fill="#94A3B8" dy="54" dx="24">TUTS</tspan>'
        "</text>",
    ),
}

# ---------------------------------------------------------------------------
# PNG export matrix — every raster size generated from the SVGs above
# ---------------------------------------------------------------------------

SizeSpec: TypeAlias = int | tuple[int, int]

PNG_EXPORTS: dict[str, list[SizeSpec]] = {
    # Icon marks — full range for favicon, apple-touch, android-chrome, etc.
    "icon-mark-gradient.svg": [32, 64, 128, 180, 192, 256, 512, 1024],
    "icon-mark-white.svg": [64, 128, 256, 512],
    "icon-mark-dark.svg": [64, 128, 256, 512],
    # Favicon with text — small sizes only (text is illegible above ~64 px)
    "favicon-full.svg": [16, 32, 48, 64],
    # Horizontal logos — 1×, 2×, 3× for each variant
    "logo-horizontal-color.svg": [(490, 110), (980, 220), (1960, 440)],
    "logo-horizontal-light.svg": [(490, 110), (980, 220), (1960, 440)],
    "logo-horizontal-dark.svg": [(490, 110), (980, 220), (1960, 440)],
    # Wordmark-only logos — tight raster sizes for split icon+text layout
    "wordmark-horizontal-color.svg": [(730, 120), (1460, 240)],
    "wordmark-horizontal-light.svg": [(730, 120), (1460, 240)],
    "wordmark-horizontal-dark.svg": [(730, 120), (1460, 240)],
    # Stacked logos — 1×, 2×, 3× for color; 1×, 2× for monochrome
    "logo-stacked-color.svg": [(360, 440), (720, 880), (1080, 1320)],
    "logo-stacked-light.svg": [(360, 440), (720, 880)],
    "logo-stacked-dark.svg": [(360, 440), (720, 880)],
    # OG image — standard social card size
    "og-image-template.svg": [(1200, 630)],
}

# ---------------------------------------------------------------------------
# PNG conversion
# ---------------------------------------------------------------------------


def svg_to_png(svg_path: Path, out_path: Path, width: int, height: int) -> None:
    """Rasterise *svg_path* to *out_path* at the requested pixel dimensions.

    ``-density 300`` gives ImageMagick enough resolution to rasterise the SVG
    sharply at large sizes.  ``-background none`` is placed **before** the
    input file so that SVG transparency is respected.
    """
    command = [
        "magick",
        "-density",
        "300",
        "-background",
        "none",
        str(svg_path),
        "-resize",
        f"{width}x{height}!",
        str(out_path),
    ]
    subprocess.run(command, check=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if not SOURCE_BOARD.exists():
        raise SystemExit("Missing source board: localm_tuts_brands.svg")

    # Wipe previous dist to avoid stale artefacts
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # 1. Write SVGs
    for name, content in SVG_TEMPLATES.items():
        (DIST / name).write_text(content, encoding="utf-8")

    # 2. Copy master board as-is
    (DIST / "brand-board.svg").write_text(
        SOURCE_BOARD.read_text(encoding="utf-8"), encoding="utf-8"
    )

    # 3. Rasterise PNGs
    for svg_name, sizes in PNG_EXPORTS.items():
        svg_path = DIST / svg_name
        for size in sizes:
            if isinstance(size, tuple):
                w, h = size
                out_name = f"{svg_path.stem}-{w}x{h}.png"
            else:
                w = h = size
                out_name = f"{svg_path.stem}-{size}.png"
            svg_to_png(svg_path, DIST / out_name, w, h)

    # 4. Write asset manifest
    manifest = {
        "name": "LocalM™ Tuts",
        "short_name": "LocalM Tuts",
        "description": "Brand assets generated from localm_tuts_brands.svg",
        "source": "localm_tuts_brands.svg",
        "assetsDir": "dist/localm",
        "assets": sorted(p.name for p in DIST.iterdir() if p.is_file()),
    }
    (DIST / "brand-assets.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    print(f"✓ Generated {len(list(DIST.iterdir()))} files in {DIST}")


if __name__ == "__main__":
    main()
