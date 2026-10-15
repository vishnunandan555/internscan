# 🏢 Company Brand Assets (`docs/logos/`)

This directory caches high-resolution SVG and PNG logos for all tracked companies to ensure fast, consistent loading without depending on third-party CDNs.

---

## 1. Asset Guidelines

- **File Format:** High-resolution transparent PNG or vectorized SVG.
- **Naming Convention:** Matches company slug (e.g. `google.png`, `microsoft.png`, `nvidia.png`).
- **Generation & Fetching:**
  - Automated via `scripts/download_logos.py`.
  - Normalized to consistent aspect ratios for display in web app cards and list views.
