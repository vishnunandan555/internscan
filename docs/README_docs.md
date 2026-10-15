# 🌐 Web Application & GitHub Pages Root (`docs/`)

The `docs/` directory contains the production web application hosted on **GitHub Pages** ([https://vishnunandan555.github.io/internscan/](https://vishnunandan555.github.io/internscan/)).

---

## Directory Architecture

```
docs/
├── index.html         # Global Gateway (Overview, regional navigation & auto-redirect)
├── in/index.html      # India Internship Tracker
├── us/index.html      # United States Tracker
├── ca/index.html      # Canada Tracker
├── uk/index.html      # United Kingdom Tracker
├── eu/index.html      # Europe Tracker
├── docs/index.html    # Dedicated Developer Platform & Integrations Hub
├── css/style.css      # Design system, dark/light theme tokens, animations
├── js/app.js          # Client-side state, fuzzy search, filters & bookmarks
├── api/               # Public REST API endpoints (active.json, latest.json)
├── feed.xml           # Standard RSS 2.0 feed
├── icon.png           # High-resolution official brand logo
├── favicon.ico        # Multi-resolution browser tab icon
├── apple-touch-icon.png # Mobile bookmark icon
├── og-image.png       # OpenGraph preview banner
├── sitemap.xml        # SEO sitemap across all portals
└── robots.txt         # Crawler indexing directives
```

---

## Frontend Technology Stack

1. **Vanilla HTML5 & CSS3:** No Tailwind, no React, no bulky runtime frameworks. Loads instantly in < 250ms worldwide.
2. **Design Tokens & Parity (`css/style.css`):**
   - Cohesive CSS custom properties (`--brand`, `--bg`, `--surface`, `--ink`, `--border`).
   - Dark mode and light mode parity toggled via `data-theme` attribute.
   - Symmetric glassmorphism, responsive micro-animations, and clean cards.
3. **Client-Side State (`js/app.js`):**
   - High-speed in-memory fuzzy search across titles, companies, categories, and locations.
   - Offline bookmarking powered by browser `localStorage`.
   - Real-time hub filtering and date pill formatting (`Posted 2d ago` vs `Found today`).
