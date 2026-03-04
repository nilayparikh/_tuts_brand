# LocalM™ Brand Docs

This folder is the documentation source of truth for brand usage in any project that consumes the `_brand` submodule.

## Files

- `docs/BRAND_GUIDE.md` — full logo/color/type and export matrix
- `scripts/generate_localm_brand_assets.py` — generator for distributable brand artifacts
- `dist/localm/` — generated artifacts (canonical SVG/PNG + manifest)

## Workflow

1. Update source artwork in `localm_tuts_brands.svg`.
2. Run:

```powershell
python scripts/generate_localm_brand_assets.py
```

3. Validate outputs in `dist/localm/`.
4. Consumers (for example `_tuts`) copy required files from this submodule into their own `public/` folder.
