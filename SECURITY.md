# 🔒 Security Policy

Security and data integrity are fundamental to **InternScan**. Because our platform syncs directly from enterprise ATS APIs and serves public REST endpoints, we treat crawler safety, rate-limiting compliance, data immutability, and dependency hygiene with high rigor.

---

## Supported Versions

| Version | Supported |
| :--- | :--- |
| `2.0.x` | ✅ Yes |
| `< 2.0.0` | ❌ End of Life |

---

## Reporting a Vulnerability

If you discover a security vulnerability or exploit within InternScan, please report it privately:

1. **Email:** Send details directly to `vishnunandan555@gmail.com` with the subject line `[SECURITY] InternScan Vulnerability Report`.
2. **Details to Include:**
   - Detailed description of the issue.
   - Steps or proof-of-concept scripts to reproduce.
   - Affected components (`bot/`, `scraper/`, `docs/`, or API endpoints).
   - Your name or handle for credit in our security advisories.

We kindly request that you do not open public GitHub issues for sensitive security vulnerabilities until we have verified and patched the issue.

---

## Crawler & Scraper Ethics

InternScan strictly adheres to ethical automated data fetching:
- **Zero Heavy Web Drivers:** We do not use headless browser farms or spam career portals. All crawling is done via lightweight standard library HTTP requests.
- **Backoff & Rate Limiting:** All scrapers implement exponential backoff with jitter when encountering rate limits (HTTP 429) or transient server errors (HTTP 5xx).
- **Public Data Only:** We only index publicly listed job openings intended for applicant discovery. We never attempt to bypass authentication walls or access private data.
- **Descriptive Identity:** All requests carry a descriptive `User-Agent` header referencing our open-source project.
- **POSIX Atomic Persistence:** All database and state updates write to temporary files first before atomic renaming via `os.replace`, protecting database integrity against sudden process termination.
