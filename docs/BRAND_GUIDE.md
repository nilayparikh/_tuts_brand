# LocalM™ Tuts Brand Guide

This guide defines the canonical LocalM™ Tuts identity system.

## Source of Truth

- Master artwork board: `localm_tuts_brands.svg`
- Generator: `scripts/generate_localm_brand_assets.py`
- Generated assets: `dist/localm/`

## Logo Family

1. Primary horizontal (color)
2. Secondary vertical/stacked (color)
3. Mark/icon (gradient)
4. Monochrome light
5. Monochrome dark
6. Favicon lockup

## Color Tokens

| Token                 | Hex       | Usage             |
| --------------------- | --------- | ----------------- |
| `brand.cyan`          | `#00F5FF` | Highlight         |
| `brand.blue`          | `#2932FF` | Core gradient     |
| `brand.purple`        | `#A838FF` | Accent            |
| `brand.green`         | `#00FFB2` | Positive accent   |
| `brand.gold`          | `#FFB03A` | Warm gradient end |
| `brand.base`          | `#0B0B0F` | Primary dark base |
| `brand.textPrimary`   | `#FFFFFF` | Primary text      |
| `brand.textSecondary` | `#94A3B8` | Secondary text    |

## Typography

- Wordmark: Share Tech Mono
- Supporting type: Outfit
- Fallbacks:
  - Mono: `Consolas, Courier New, monospace`
  - Sans: `Segoe UI, Roboto, Arial, sans-serif`

## Transparency

All SVGs and PNGs are **transparent** — no background rectangle is baked in.
The only exception is `og-image-template` which has a solid `#07070A` fill
because social-card images do not support transparency.

Consumers choose the appropriate variant for their surface:

| Surface           | Variant to use     |
| ----------------- | ------------------ |
| Dark background   | `*-color` or `*-light` (white/gradient strokes are visible) |
| Light background  | `*-dark` (dark strokes are visible)                         |
| Social card / OG  | `og-image-template` (solid background)                      |

## Export Matrix

### SVG (14 files)

| File                         | Size      | Background  | Notes                        |
| ---------------------------- | --------- | ----------- | ---------------------------- |
| `icon-mark-gradient.svg`     | 200×200   | transparent | Primary gradient mark        |
| `icon-mark-white.svg`        | 200×200   | transparent | Monochrome white mark        |
| `icon-mark-dark.svg`         | 200×200   | transparent | Monochrome dark mark         |
| `favicon-full.svg`           | 200×200   | transparent | Mark + "localm" text         |
| `logo-horizontal-color.svg`  | 980×220   | transparent | Gradient mark + colored text |
| `logo-horizontal-light.svg`  | 980×220   | transparent | White mark + white text      |
| `logo-horizontal-dark.svg`   | 980×220   | transparent | Dark mark + dark text        |
| `logo-stacked-color.svg`     | 360×440   | transparent | Gradient mark, text below    |
| `logo-stacked-light.svg`     | 360×440   | transparent | White mark, text below       |
| `logo-stacked-dark.svg`      | 360×440   | transparent | Dark mark, text below        |
| `og-image-template.svg`      | 1200×630  | solid dark  | Social sharing card          |
| `brand-board.svg`            | 1400×1850 | solid dark  | Master presentation board    |

### PNG (transparent, high-density rasterised)

| Source SVG                   | Sizes (px)                                       |
| ---------------------------- | ------------------------------------------------ |
| `icon-mark-gradient`         | 32, 64, 128, 180, 192, 256, 512, 1024           |
| `icon-mark-white`            | 64, 128, 256, 512                                |
| `icon-mark-dark`             | 64, 128, 256, 512                                |
| `favicon-full`               | 16, 32, 48, 64                                   |
| `logo-horizontal-color`      | 490×110, 980×220, 1960×440                       |
| `logo-horizontal-light`      | 490×110, 980×220, 1960×440                       |
| `logo-horizontal-dark`       | 490×110, 980×220, 1960×440                       |
| `logo-stacked-color`         | 360×440, 720×880, 1080×1320                      |
| `logo-stacked-light`         | 360×440, 720×880                                 |
| `logo-stacked-dark`          | 360×440, 720×880                                 |
| `og-image-template`          | 1200×630                                         |

### Standard web icon mappings

| Web use               | Canonical file                    |
| ---------------------- | --------------------------------- |
| `favicon.ico`          | (copy from `icon-mark-gradient-32.png` or create ICO externally) |
| Apple touch icon       | `icon-mark-gradient-180.png`      |
| Android Chrome 192     | `icon-mark-gradient-192.png`      |
| Android Chrome 512     | `icon-mark-gradient-512.png`      |
| OG image               | `og-image-template-1200x630.png`  |

## Do / Don’t

### Do

- Use generated files from `dist/localm/` as canonical distribution assets.
- Prefer SVG in UI and PNG for metadata/favicon slots.
- Preserve aspect ratio and clear space.

### Don’t

- Distort, skew, or recolor logos.
- Add extra effects not present in canonical assets.
- Introduce ad-hoc brand colors.

## Consumer Pattern

Any project that uses `_brand` should:

1. Add `_brand` as submodule.
2. Copy **only the files actually referenced by the app** from `_brand/dist/localm/` into `public/brand/`.
3. Reference this guide for usage and allowed variants.

### `_tuts` consumer workflow

The `_tuts` site copies a minimal subset from `dist/localm/` directly into
`public/brand/` (flat, no `localm/` subfolder). Only files referenced by
`layout.tsx`, `manifest.webmanifest`, or `config/site.ts` are copied.

```powershell
# From _tuts root
cd _brand
python scripts/generate_localm_brand_assets.py
cd ..

# Copy only the files the app actually uses
$needed = @(
  'favicon-full-32.png',
  'icon-mark-gradient-64.png',
  'icon-mark-gradient-180.png',
  'icon-mark-gradient-192.png',
  'icon-mark-gradient-512.png',
  'og-image-template-1200x630.png'
)
foreach ($f in $needed) {
  Copy-Item "_brand\dist\localm\$f" "public\brand\$f" -Force
}
```

### Non-brand files in `public/brand/`

These are **not** generated by `_brand` — they are site-specific assets:

| File                 | Purpose            |
| -------------------- | ------------------ |
| `nilay_parikh.jpeg`  | Instructor photo   |
| `profile-pic-512.png`| Profile picture    |
| `logo-canvas.svg`    | Slide deck canvas  |
