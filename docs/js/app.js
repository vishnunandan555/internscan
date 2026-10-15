/**
 * InternScan India — Application Logic (v2.0.0)
 * Modular, clean, performant client-side state and UI renderer.
 */

const DATA_URLS = [
  "./jobs.json",
  "https://raw.githubusercontent.com/vishnunandan555/internscan/main/data/jobs.json",
  "../data/jobs.json"
];

let allJobs = [];
let savedKeys = JSON.parse(localStorage.getItem("saved_jobs_v2") || "[]");

const urlParams = new URLSearchParams(window.location.search);
const state = {
  query: urlParams.get("q") || "",
  hub: urlParams.get("hub") || "all",
  company: urlParams.get("company") || "all",
  category: urlParams.get("cat") || "all",
  sort: urlParams.get("sort") || "newest",
  view: localStorage.getItem("tracker_view") || "cards",
  newOnly: urlParams.get("new") === "true",
  savedOnly: false,
};

// Reusable SVG Icon Sprites
const ICONS = {
  pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>',
  briefcase: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>',
  clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
  link: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>',
  star: (saved, s = 15) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="${saved ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2.2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`,
  arrow: (s = 14) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>`
};

function syncUrlParams() {
  const p = new URLSearchParams();
  if (state.query) p.set("q", state.query);
  if (state.hub && state.hub !== "all") p.set("hub", state.hub);
  if (state.company && state.company !== "all") p.set("company", state.company);
  if (state.category && state.category !== "all") p.set("cat", state.category);
  if (state.sort && state.sort !== "newest") p.set("sort", state.sort);
  if (state.newOnly) p.set("new", "true");
  const qStr = p.toString();
  window.history.replaceState({}, "", window.location.pathname + (qStr ? "?" + qStr : "") + window.location.hash);
}

function injectJobSchema(jobs) {
  try {
    const old = document.getElementById("schema-job-postings");
    if (old) old.remove();

    const script = document.createElement("script");
    script.id = "schema-job-postings";
    script.type = "application/ld+json";
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "ItemList",
      "name": "Verified Tech & Software Internships India 2026-2027",
      "numberOfItems": jobs.length,
      "itemListElement": jobs.slice(0, 30).map((j, idx) => ({
        "@type": "ListItem",
        "position": idx + 1,
        "item": {
          "@type": "JobPosting",
          "title": j.title,
          "description": `Verified ${j.category || "Software"} internship at ${j.company} in ${(j.locations || []).join(", ") || "India"}.`,
          "datePosted": j.first_seen || new Date().toISOString().slice(0, 10),
          "employmentType": "INTERN",
          "hiringOrganization": { "@type": "Organization", "name": j.company },
          "jobLocation": {
            "@type": "Place",
            "address": { "@type": "PostalAddress", "addressLocality": j.city_tag || "Bengaluru", "addressCountry": "IN" }
          },
          "url": j.url
        }
      }))
    });
    document.head.appendChild(script);
  } catch (e) {
    console.warn("Schema injection error:", e);
  }
}

function formatRelativeDate(dateStr) {
  if (!dateStr) return "Recently";
  const days = Math.floor((new Date() - new Date(dateStr + "T00:00:00Z")) / 86400000);
  if (days <= 0) return "Today";
  if (days === 1) return "Yesterday";
  return `${days}d ago`;
}

function getAvatarLetters(company) {
  if (!company) return "CO";
  const parts = company.trim().split(" ");
  return parts.length > 1 ? (parts[0][0] + parts[1][0]).toUpperCase() : company.slice(0, 2).toUpperCase();
}

function getCompanySlug(company) {
  return (company || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

function getLogosBasePath() {
  const p = window.location.pathname;
  if (/\/(in|us|ca|uk|eu)(\/|$)/i.test(p)) {
    return "../logos/";
  }
  return "./logos/";
}

function renderAvatar(company, isCompact = false) {
  const slug = getCompanySlug(company);
  const letters = getAvatarLetters(company);
  const boxCls = isCompact ? "compact-avatar" : "company-avatar";
  const imgCls = isCompact ? "compact-logo-img" : "company-logo-img";
  const basePath = getLogosBasePath();
  return `<div class="${boxCls}" title="${company}">
    <img class="${imgCls}" src="${basePath}${slug}.png" alt="${company}" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='block';" loading="lazy">
    <span class="avatar-fallback" style="display:none;">${letters}</span>
  </div>`;
}

function showToast(msg) {
  const toast = document.getElementById("toast");
  document.getElementById("toast-text").innerText = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2400);
}

async function fetchJobsData() {
  for (const url of DATA_URLS) {
    try {
      const res = await fetch(url);
      if (res.ok) return await res.json();
    } catch (_) {}
  }
  throw new Error("Unable to load jobs data from any source.");
}

async function loadJobs() {
  try {
    const data = await fetchJobsData();
    const updated = data.updated_at ? new Date(data.updated_at) : new Date();
    const cutoff = new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10);

    allJobs = Object.keys(data.jobs || {}).map(k => {
      const j = data.jobs[k];
      j.uid = k;
      j.isNew = (j.first_seen || "") >= cutoff;
      return j;
    }).filter(j => j.active);

    // Update hero metrics
    document.getElementById("metric-jobs").textContent = allJobs.length;
    const uniqueCos = new Set(allJobs.map(j => j.company));
    document.getElementById("metric-companies").textContent = uniqueCos.size;
    document.getElementById("last-updated-text").textContent = `Last checked: ${updated.toLocaleDateString()} ${updated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;

    updateHubCounts();
    updateCategoryCounts();
    populateCompanies();
    restoreUIFromState();

    renderJobs();
    injectJobSchema(allJobs);
  } catch (err) {
    console.error(err);
    document.getElementById("jobs-wrapper").innerHTML = `<div class="empty-state"><h3>Unable to load jobs</h3><p>${err.message}</p></div>`;
  }
}

// Hub Keyword Patterns for Intelligent Multi-City Matching
const HUB_PATTERNS = {
  // India Hubs
  "Bengaluru": /\b(bengaluru|bangalore|blr)\b/i,
  "Hyderabad": /\b(hyderabad|secunderabad|cyberabad|hyd)\b/i,
  "Pune": /\b(pune|pun)\b/i,
  "Delhi-NCR": /\b(delhi|gurugram|gurgaon|noida|ncr|ggn)\b/i,
  "Chennai": /\b(chennai|madras|maa)\b/i,
  "Mumbai": /\b(mumbai|bombay|bom|navi mumbai|thane)\b/i,
  // US Hubs
  "SF Bay Area": /\b(san francisco|sf|bay area|mountain view|sunnyvale|palo alto|san jose|santa clara|menlo park|cupertino|redwood city|san mateo|fremont)\b/i,
  "Seattle": /\b(seattle|redmond|bellevue|kirkland)\b/i,
  "New York": /\b(new york|nyc|manhattan|brooklyn)\b/i,
  "Austin": /\b(austin|round rock)\b/i,
  "Boston": /\b(boston|cambridge|waltham)\b/i,
  // Canada Hubs
  "Toronto": /\b(toronto|mississauga|markham)\b/i,
  "Waterloo": /\b(waterloo|kitchener)\b/i,
  "Vancouver": /\b(vancouver|burnaby|richmond)\b/i,
  "Montreal": /\b(montreal|montréal|laval)\b/i,
  // UK Hubs
  "London": /\b(london)\b/i,
  "Cambridge / Oxford": /\b(cambridge|oxford)\b/i,
  "Manchester": /\b(manchester)\b/i,
  "Edinburgh": /\b(edinburgh)\b/i,
  // Europe Hubs
  "Berlin": /\b(berlin)\b/i,
  "Munich": /\b(munich|münchen)\b/i,
  "Dublin": /\b(dublin)\b/i,
  "Amsterdam": /\b(amsterdam)\b/i,
  "Zurich": /\b(zurich|zürich)\b/i,
  "Paris": /\b(paris)\b/i,
  // Global & General
  "Remote": /\b(remote|work\s*from\s*home|wfh|anywhere)\b/i,
  "Other": /\b(multiple|other)\b/i,
};

function isJobRemote(j) {
  const locText = [j.city_tag || "", ...(j.locations || []), j.title || ""].join(" ");
  return (
    /remote/i.test(j.city_tag || "") ||
    HUB_PATTERNS["Remote"].test(locText) ||
    (/\bremote\b/i.test(locText) && !/\b(hybrid|on-?site|in-?office)\b/i.test(locText))
  );
}

function jobMatchesHub(j, hub) {
  if (!hub || hub === "all") return true;

  if (hub === "Remote" || hub.toLowerCase().includes("remote")) {
    return isJobRemote(j);
  }

  const locText = [j.city_tag || "", ...(j.locations || [])].join(" ");

  if (hub === "Other" || hub.toLowerCase().includes("other")) {
    return HUB_PATTERNS["Other"].test(locText) || (j.city_tag || "").toLowerCase().includes("other");
  }

  const pattern = HUB_PATTERNS[hub];
  if (pattern && pattern.test(locText)) {
    return true;
  }
  return j.city_tag === hub;
}

function formatLocationDisplay(j) {
  if (isJobRemote(j)) return j.city_tag && j.city_tag.includes("Remote") ? j.city_tag : "Remote";
  const locs = j.locations || [];
  const text = (j.city_tag || "") + " " + locs.join(" ");
  if (/multiple/i.test(text) || (j.city_tag || "").includes("Multiple")) {
    return "Multiple Locations";
  }

  const detected = [];
  const checkHubs = [
    "Bengaluru", "Hyderabad", "Pune", "Delhi-NCR", "Chennai", "Mumbai",
    "SF Bay Area", "Seattle", "New York", "Austin", "Boston"
  ];
  for (const h of checkHubs) {
    if (HUB_PATTERNS[h] && HUB_PATTERNS[h].test(text)) detected.push(h);
  }

  if (detected.length > 0) {
    if (detected.length <= 2) return detected.join(", ");
    return `${detected[0]}, ${detected[1]} (+${detected.length - 2})`;
  }

  return j.city_tag || locs[0] || "Global";
}

function updateHubCounts() {
  document.querySelectorAll(".hub-btn").forEach(btn => {
    const hub = btn.dataset.hub;
    const badge = btn.querySelector(".count, .badge");
    if (!badge) return;
    if (hub === "all") {
      badge.textContent = allJobs.length;
    } else {
      badge.textContent = allJobs.filter(j => jobMatchesHub(j, hub)).length;
    }
  });
}

function updateCategoryCounts() {
  const counts = {};
  allJobs.forEach(j => {
    const cat = j.category || "Software";
    counts[cat] = (counts[cat] || 0) + 1;
  });

  document.querySelectorAll("#category-pills .filter-pill").forEach(pill => {
    const cat = pill.dataset.cat;
    const badge = pill.querySelector(".cat-count, .pill-count");
    if (badge && cat !== "all") {
      const num = counts[cat] || 0;
      badge.textContent = num > 0 ? num : "";
    }
  });
}

function populateCompanies() {
  const select = document.getElementById("company-select");
  const cos = {};
  allJobs.forEach(j => { cos[j.company] = (cos[j.company] || 0) + 1; });
  const sorted = Object.keys(cos).sort();

  select.innerHTML = `<option value="all">All Companies (${allJobs.length})</option>` +
    sorted.map(c => `<option value="${c}">${c} (${cos[c]})</option>`).join("");
}

function restoreUIFromState() {
  if (state.query) {
    document.getElementById("search-input").value = state.query;
    document.getElementById("clear-search").style.display = "flex";
  }
  if (state.company !== "all") document.getElementById("company-select").value = state.company;
  if (state.sort !== "newest") document.getElementById("sort-select").value = state.sort;
  if (state.hub !== "all") {
    document.querySelectorAll(".hub-btn").forEach(b => b.classList.toggle("active", b.dataset.hub === state.hub));
  }
  if (state.category !== "all") {
    document.querySelectorAll("#category-pills .filter-pill").forEach(p => p.classList.toggle("active", p.dataset.cat === state.category));
  }
  if (state.newOnly) document.getElementById("btn-new").classList.add("active");
}

function filterAndSortJobs() {
  const q = state.query.toLowerCase();
  const filtered = allJobs.filter(j => {
    if (q) {
      const hay = `${j.title} ${j.company} ${j.category || ""} ${j.city_tag || ""} ${(j.locations || []).join(" ")}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    if (state.hub && state.hub !== "all" && !jobMatchesHub(j, state.hub)) return false;
    if (state.company !== "all" && j.company !== state.company) return false;
    if (state.category !== "all" && j.category !== state.category) return false;
    if (state.newOnly && !j.isNew) return false;
    if (state.savedOnly && !savedKeys.includes(j.uid)) return false;
    return true;
  });

  if (state.sort === "newest") {
    filtered.sort((a, b) => (b.posted || b.first_seen || "").localeCompare(a.posted || a.first_seen || ""));
  } else if (state.sort === "company") {
    filtered.sort((a, b) => a.company.localeCompare(b.company));
  } else if (state.sort === "title") {
    filtered.sort((a, b) => a.title.localeCompare(b.title));
  }

  return filtered;
}

function renderJobs() {
  syncUrlParams();
  const filtered = filterAndSortJobs();

  document.getElementById("jobs-count").textContent = filtered.length;
  document.getElementById("saved-counter").textContent = savedKeys.length;

  const container = document.getElementById("jobs-wrapper");
  if (!filtered.length) {
    container.innerHTML = `<div class="empty-state">
      <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      <h3>No matching internships found</h3>
      <p>Try adjusting your search query, location filter, or role category.</p>
      <button class="btn-reset" onclick="resetFilters()">Reset All Filters</button>
    </div>`;
    return;
  }

  if (state.view === "compact") {
    renderCompactView(filtered, container);
  } else {
    renderCardsView(filtered, container);
  }
}

function renderCardsView(filtered, container) {
  container.innerHTML = `<div class="job-grid-cards">${filtered.map(j => {
    const isSaved = savedKeys.includes(j.uid);
    const loc = formatLocationDisplay(j);
    const date = formatRelativeDate(j.posted || j.first_seen);
    const catClass = j.category === "AI/ML" ? "cat-ai" : (j.category === "Hardware/Silicon" ? "cat-hw" : "");

    return `<div class="job-card">
      <div class="job-left">
        ${renderAvatar(j.company, false)}
        <div class="job-details">
          <div class="job-title-row">
            <span class="company-name">${j.company}</span>
            ${j.isNew ? '<span class="badge-status new">NEW</span>' : ''}
          </div>
          <div class="role-name">
            <a href="${j.url}" target="_blank" rel="noopener">${j.title}</a>
          </div>
          <div class="chips-row">
            <span class="chip hub">${ICONS.pin}${loc}</span>
            <span class="chip ${catClass}">${ICONS.briefcase}${j.category || "Software"}</span>
            <span class="chip">${ICONS.clock}${date}</span>
          </div>
        </div>
      </div>
      <div class="job-actions">
        <button class="action-icon-btn ${isSaved ? 'saved' : ''}" onclick="toggleSave('${j.uid}')" title="${isSaved ? 'Remove from bookmarks' : 'Bookmark role'}">
          ${ICONS.star(isSaved, 15)}
        </button>
        <button class="action-icon-btn" onclick="copyRoleLink('${j.url}')" title="Copy job link">
          ${ICONS.link}
        </button>
        <a href="${j.url}" target="_blank" rel="noopener" class="btn-apply">
          Apply ${ICONS.arrow(14)}
        </a>
      </div>
    </div>`;
  }).join("")}</div>`;
}

function renderCompactView(filtered, container) {
  container.innerHTML = `<div class="job-grid-compact">
    <div class="compact-header">
      <div>Role & Company</div>
      <div>Location</div>
      <div>Category</div>
      <div>Date</div>
      <div style="text-align: right;">Action</div>
    </div>
    ${filtered.map(j => {
      const isSaved = savedKeys.includes(j.uid);
      const loc = formatLocationDisplay(j);
      const date = formatRelativeDate(j.posted || j.first_seen);

      return `<div class="compact-row">
        <div class="compact-role">
          ${renderAvatar(j.company, true)}
          <div class="compact-title-box">
            <div class="compact-title"><a href="${j.url}" target="_blank" rel="noopener">${j.title}</a></div>
            <div class="compact-sub">
              <span>${j.company}</span>
              ${j.isNew ? '<span class="badge-status new" style="font-size: 10px; padding: 1px 5px;">NEW</span>' : ''}
              <span class="compact-meta-inline"> · ${loc} · ${date}</span>
            </div>
          </div>
        </div>
        <div class="compact-col-loc"><span class="chip hub" style="font-size: 11px;">${loc}</span></div>
        <div class="compact-col-cat"><span class="chip" style="font-size: 11px;">${j.category || "Software"}</span></div>
        <div class="compact-col-date" style="font-size: 12.5px; color: var(--dim);">${date}</div>
        <div class="compact-actions">
          <button class="action-icon-btn ${isSaved ? 'saved' : ''}" style="width: 32px; height: 32px;" onclick="toggleSave('${j.uid}')" title="Bookmark">
            ${ICONS.star(isSaved, 13)}
          </button>
          <a href="${j.url}" target="_blank" rel="noopener" class="compact-btn-apply">
            Apply ${ICONS.arrow(11)}
          </a>
        </div>
      </div>`;
    }).join("")}
  </div>`;
}

function toggleSave(uid) {
  const idx = savedKeys.indexOf(uid);
  if (idx === -1) {
    savedKeys.push(uid);
    showToast("Saved to your bookmarks");
  } else {
    savedKeys.splice(idx, 1);
    showToast("Removed from bookmarks");
  }
  localStorage.setItem("saved_jobs_v2", JSON.stringify(savedKeys));
  renderJobs();
}

function copyRoleLink(url) {
  navigator.clipboard.writeText(url)
    .then(() => showToast("Link copied to clipboard"))
    .catch(() => showToast("Could not copy link"));
}

function resetFilters() {
  state.query = "";
  state.hub = "all";
  state.company = "all";
  state.category = "all";
  state.newOnly = false;
  state.savedOnly = false;

  document.getElementById("search-input").value = "";
  document.getElementById("clear-search").style.display = "none";
  document.getElementById("company-select").value = "all";
  document.querySelectorAll(".hub-btn").forEach(b => b.classList.toggle("active", b.dataset.hub === "all"));
  document.querySelectorAll("#category-pills .filter-pill").forEach(p => p.classList.toggle("active", p.dataset.cat === "all"));
  document.getElementById("btn-new").classList.remove("active");
  document.getElementById("btn-saved").classList.remove("active");

  renderJobs();
}

// Global Event Setup
const searchInput = document.getElementById("search-input");
const clearBtn = document.getElementById("clear-search");

document.addEventListener("keydown", (e) => {
  if (e.key === "/" && document.activeElement !== searchInput) {
    e.preventDefault();
    searchInput.focus();
  } else if (e.key === "Escape" && document.activeElement === searchInput) {
    searchInput.blur();
  }
});

searchInput.addEventListener("input", (e) => {
  state.query = e.target.value.trim();
  clearBtn.style.display = state.query ? "flex" : "none";
  renderJobs();
});

clearBtn.addEventListener("click", () => {
  searchInput.value = "";
  state.query = "";
  clearBtn.style.display = "none";
  searchInput.focus();
  renderJobs();
});

document.querySelectorAll(".hub-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".hub-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    state.hub = btn.dataset.hub;
    renderJobs();
  });
});

document.querySelectorAll("#category-pills .filter-pill").forEach(pill => {
  pill.addEventListener("click", () => {
    document.querySelectorAll("#category-pills .filter-pill").forEach(p => p.classList.remove("active"));
    pill.classList.add("active");
    state.category = pill.dataset.cat;
    renderJobs();
  });
});

document.getElementById("btn-new").addEventListener("click", function() {
  state.newOnly = !state.newOnly;
  this.classList.toggle("active", state.newOnly);
  renderJobs();
});

document.getElementById("btn-saved").addEventListener("click", function() {
  state.savedOnly = !state.savedOnly;
  this.classList.toggle("active", state.savedOnly);
  renderJobs();
});

document.getElementById("company-select").addEventListener("change", (e) => {
  state.company = e.target.value;
  renderJobs();
});

document.getElementById("sort-select").addEventListener("change", (e) => {
  state.sort = e.target.value;
  renderJobs();
});

const btnCards = document.getElementById("btn-view-cards");
const btnCompact = document.getElementById("btn-view-compact");

function setViewMode(mode) {
  state.view = mode;
  localStorage.setItem("tracker_view", mode);
  btnCards.classList.toggle("active", mode === "cards");
  btnCompact.classList.toggle("active", mode === "compact");
  renderJobs();
}

btnCards.addEventListener("click", () => setViewMode("cards"));
btnCompact.addEventListener("click", () => setViewMode("compact"));
setViewMode(state.view);

// Theme Toggle
const themeBtn = document.getElementById("theme-btn");
const themeIcon = document.getElementById("theme-icon");
const currentTheme = localStorage.getItem("theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  themeIcon.innerHTML = theme === "dark"
    ? '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>'
    : '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
}

applyTheme(currentTheme);
themeBtn.addEventListener("click", () => {
  const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
  localStorage.setItem("theme", next);
  applyTheme(next);
});

// Documentation Section Tabs & Copy Handlers
document.querySelectorAll(".docs-tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const tabId = btn.getAttribute("data-tab");
    document.querySelectorAll(".docs-tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".docs-tab-panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    const panel = document.getElementById(tabId);
    if (panel) panel.classList.add("active");
  });
});

document.querySelectorAll(".api-copy-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const textToCopy = btn.getAttribute("data-copy");
    if (!textToCopy) return;
    navigator.clipboard.writeText(textToCopy).then(() => {
      showToast("API URL copied to clipboard!");
    }).catch(() => {
      showToast("Failed to copy URL");
    });
  });
});

// Country Dropdown Handler
const countryWrap = document.getElementById("countrySelectorWrap");
if (countryWrap) {
  const countryBtn = document.getElementById("countryMenuBtn");
  if (countryBtn) {
    countryBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      countryWrap.classList.toggle("open");
    });
  }
  document.addEventListener("click", (e) => {
    if (!countryWrap.contains(e.target)) {
      countryWrap.classList.remove("open");
    }
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") countryWrap.classList.remove("open");
  });
  countryWrap.querySelectorAll(".country-menu-item").forEach(item => {
    item.addEventListener("click", () => {
      countryWrap.classList.remove("open");
    });
  });
}

loadJobs();
