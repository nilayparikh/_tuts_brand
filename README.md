# \_tuts_brand

LocalM™ Tuts brand source repository.

## Purpose

This submodule stores the master vector source and brand documentation used to
generate all web-ready brand assets consumed by `_tuts` and related projects.

## Source Files

- `localm_tuts_brands.svg` — master board including six logo families:
  1.  Original favicon base
  2.  Primary horizontal lockup
  3.  Secondary vertical lockup
  4.  Animated lockup
  5.  Monochrome dark (for light backgrounds)
  6.  Monochrome light (for dark backgrounds)
- `docs/BRAND_GUIDE.md` — canonical usage guide
- `docs/README.md` — documentation index and workflow

## Downstream Generation

In this `_brand` repo, generated assets are built with:

- `scripts/generate_localm_brand_assets.py`

Outputs are written to:

- `dist/localm/` (canonical distributable assets)

Consumers (for example `_tuts`) copy required artifacts from `dist/localm/`.

## Brand System Highlights

- Primary gradient: cyan → blue → purple → copper/orange
- Core dark base: `#0B0B0F`
- Wordmark typography: Share Tech Mono
- Supporting typography: Outfit

## Maintenance

1. Edit `localm_tuts_brands.svg`
2. Run `python scripts/generate_localm_brand_assets.py`
3. Validate outputs under `dist/localm/`
4. Consumers sync and copy required artifacts
5. Update docs if color/type/logo matrix changed
