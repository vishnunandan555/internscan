# 🛠️ Helper Scripts (`scripts/`)

The `scripts/` directory contains standalone automation utilities for managing media assets, logos, and preview banners.

---

## Script Map

### 1. `download_logos.py`
Downloads official company SVG/PNG logos from verified CDN sources (Clearbit, GitHub, SimpleIcons) and saves them into `docs/logos/<company-slug>.png`.
```bash
python3 scripts/download_logos.py
```

### 2. `generate_og_image.py`
Generates the modern 1200×630 OpenGraph preview card (`docs/og-image.png`) using Pillow. Renders custom typography, gradient highlights, and platform metrics for social sharing on Twitter, LinkedIn, and WhatsApp.
```bash
python3 scripts/generate_og_image.py
```
