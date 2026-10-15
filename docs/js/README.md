# ⚡ Client Logic & State Architecture (`docs/js/`)

This directory houses the vanilla JavaScript client engine for the InternScan web application.

---

## 1. File Map

```
docs/js/
├── app.js          # Core client logic, state management, search, and filtering
└── README.md       # Client script architecture documentation
```

---

## 2. Responsibilities

- **Zero-Dependency Architecture:**
  - Written in modern, vanilla ECMAScript (ES6+).
  - No React, Vue, or Angular bundles — runs instantly with near-zero bundle overhead.
- **Client-Side State Engine:**
  - Fetches and parses `jobs.json` asynchronously with client caching.
  - Maintains state for active filters (Engineering Categories, Locations/Hubs, Status).
  - Real-time search with token matching and debounce.
  - Bookmark & Saved Jobs persistence using HTML5 `localStorage`.
  - Dark / Light theme synchronization with `prefers-color-scheme` support.
