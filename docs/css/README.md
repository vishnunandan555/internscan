# 🎨 Stylesheet Architecture (`docs/css/`)

This directory houses the design system tokens and styling rules for the InternScan web application.

---

## 1. File Map

```
docs/css/
├── style.css       # Master stylesheet & CSS variables (design system)
└── README.md       # Styling and layout architecture
```

---

## 2. Design System Tokens (`style.css`)

The web application follows strict vanilla CSS guidelines (no Tailwind, Sass, or preprocessors):

- **Color Tokens:**
  - `--brand`: Vibrant accent (`#f97316` brand orange).
  - `--brand-hover`: Darker orange interactive state.
  - `--bg`: Dark mode primary background (`#0b0f19`) / Light mode (`#f8fafc`).
  - `--surface`: Dark card surface (`#111827`) / Light card (`#ffffff`).
  - `--ink`: Primary typography color.
  - `--ink-dim`: Secondary text color.
- **Components:**
  - Glassmorphic panels with subtle backdrop filters.
  - Responsive job cards with hover animations.
  - High-contrast badge tags for job engineering categories and tech hubs.
  - Theme toggler supporting dark/light mode with smooth CSS transitions.
