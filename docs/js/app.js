/**
 * InternScan India — Application Logic (v2.0.0)
 * Modular, clean, performant client-side state and UI renderer.
 */

const DATA_URLS = [
  "./jobs.json",
  "../jobs.json",
  "./metrics.json",
  "../metrics.json",
  "https://raw.githubusercontent.com/vishnunandan555/internscan/main/data/jobs.json"
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

function formatJobDate(j) {
  const isOfficial = Boolean(j.posted);
  const dateStr = j.posted || j.first_seen;
  if (!dateStr) return { text: "Recently", isOfficial: false, fullDate: "" };

  const days = Math.floor((new Date() - new Date(dateStr + "T00:00:00Z")) / 86400000);
  const prefix = isOfficial ? "Posted" : "Found";

  let rel;
  if (days <= 0) rel = `${prefix} today`;
  else if (days === 1) rel = `${prefix} yesterday`;
  else if (days < 30) rel = `${prefix} ${days}d ago`;
  else {
    const mo = Math.floor(days / 30);
    rel = `${prefix} ${mo}mo ago`;
  }

  let formattedDate = dateStr;
  try {
    const d = new Date(dateStr + "T00:00:00Z");
    formattedDate = d.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric"
    });
  } catch (_) {}

  return { text: rel, isOfficial, fullDate: formattedDate };
}

function cleanDisplayTitle(title) {
  if (!title || !/stagiaire/i.test(title)) return title;
  const parts = title.split(/[;/]|,\s*(?=[A-Z])/);
  const eng = parts.filter(p => !/\b(stagiaire|d[ée]veloppement|recherche|apprentissage|logiciel)\b/i.test(p));
  if (eng.length) return eng.join(" – ").trim();
  const intern = parts.filter(p => /\bintern\b/i.test(p));
  if (intern.length) return intern[0].trim();
  return title;
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

function formatLocalDateTime(dateObj, includeRelative = false) {
  if (!dateObj || isNaN(dateObj.getTime())) return "";

  const formatter = new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short"
  });

  const formattedStr = formatter.format(dateObj);
  if (!includeRelative) return formattedStr;

  const diffMs = Date.now() - dateObj.getTime();
  const diffMins = Math.max(0, Math.floor(diffMs / 60000));
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  let rel = "";
  if (diffMins < 1) rel = "just now";
  else if (diffMins < 60) rel = `${diffMins}m ago`;
  else if (diffHours < 24) rel = `${diffHours}h ago`;
  else if (diffDays === 1) rel = "yesterday";
  else rel = `${diffDays}d ago`;

  return `${formattedStr} (${rel})`;
}

function getLocalScrapeSchedule() {
  const d = new Date();
  d.setUTCHours(21, 30, 0, 0); // Scraper cron is 03:00 AM IST = 21:30 UTC
  return d.toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short"
  });
}

async function loadJobs() {
  const footerScanEl = document.getElementById("footer-scan-time");
  try {
    const data = await fetchJobsData();
    const updated = data.updated_at ? new Date(data.updated_at) : new Date();

    if (footerScanEl) {
      footerScanEl.textContent = `Last Scanned on: ${formatLocalDateTime(updated)}`;
    }

    if (!document.getElementById("jobs-wrapper")) return;

    const cutoff = new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10);

    allJobs = Object.keys(data.jobs || {}).map(k => {
      const j = data.jobs[k];
      j.uid = k;
      j.isNew = (j.first_seen || "") >= cutoff;
      return j;
    }).filter(j => j.active);

    // Update hero metrics
    const metricJobsEl = document.getElementById("metric-jobs");
    if (metricJobsEl) metricJobsEl.textContent = allJobs.length;
    const uniqueCos = new Set(allJobs.map(j => j.company));
    const metricCosEl = document.getElementById("metric-companies");
    if (metricCosEl) metricCosEl.textContent = uniqueCos.size;
    const lastCheckedEl = document.getElementById("last-updated-text");
    if (lastCheckedEl) {
      lastCheckedEl.textContent = `Last checked: ${formatLocalDateTime(updated, true)}`;
    }

    // Hero cadence metric adaptation to local timezone
    const cadenceValEl = document.getElementById("metric-cadence-val");
    const cadenceSubEl = document.getElementById("metric-cadence-sub");
    const cadenceCardEl = document.getElementById("cadence-card");
    const scheduleTime = getLocalScrapeSchedule();

    if (cadenceValEl) {
      cadenceValEl.textContent = "Updated Daily";
    }
    if (cadenceSubEl) {
      const diffMs = Date.now() - updated.getTime();
      const diffMins = Math.max(0, Math.floor(diffMs / 60000));
      const diffHours = Math.floor(diffMins / 60);
      const rel = diffMins < 60 ? `${diffMins}m ago` : (diffHours < 24 ? `${diffHours}h ago` : `${Math.floor(diffHours / 24)}d ago`);
      const timeOnly = updated.toLocaleTimeString(undefined, {
        hour: "numeric",
        minute: "2-digit",
        timeZoneName: "short"
      });
      cadenceSubEl.textContent = `Last: ${rel} (${timeOnly})`;
    }
    if (cadenceCardEl) {
      cadenceCardEl.title = `Syncs daily at ~${scheduleTime} (03:00 AM IST). Last updated: ${formatLocalDateTime(updated, true)}.`;
    }

    initMobileSelects();
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

const US_STATE_MAP = {
  "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
  "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
  "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
  "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
  "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
  "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
  "new mexico": "NM", "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH",
  "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
  "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
  "virginia": "VA", "washington": "WA", "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
  "district of columbia": "DC"
};
const US_CODE_SET = new Set(Object.values(US_STATE_MAP));

const CA_PROVINCE_MAP = {
  "ontario": "ON", "quebec": "QC", "british columbia": "BC", "alberta": "AB",
  "manitoba": "MB", "saskatchewan": "SK", "nova scotia": "NS", "new brunswick": "NB",
  "newfoundland and labrador": "NL", "prince edward island": "PE"
};

const EU_COUNTRY_MAP = {
  "esp": "Spain", "fra": "France", "gbr": "UK", "deu": "Germany", "irl": "Ireland",
  "ita": "Italy", "pol": "Poland", "rou": "Romania", "che": "Switzerland", "nor": "Norway",
  "dnk": "Denmark", "swe": "Sweden", "nld": "Netherlands", "bel": "Belgium", "cze": "Czechia",
  "aut": "Austria", "prt": "Portugal", "fin": "Finland"
};

const KNOWN_COUNTRY_NAMES = new Set([
  "united states", "usa", "us", "u.s.a.", "u.s.", "canada", "united kingdom", "uk",
  "great britain", "england", "scotland", "wales", "ireland", "germany", "france",
  "poland", "spain", "italy", "switzerland", "netherlands", "sweden", "norway",
  "denmark", "czech republic", "czechia", "romania", "belgium", "austria", "portugal",
  "india"
]);

function toTitleCase(str) {
  if (!str) return "";
  return str.replace(/\b[a-z]/g, c => c.toUpperCase());
}

function cleanSingleLocation(rawLoc, country) {
  if (!rawLoc) return "";
  let s = String(rawLoc).trim();
  if (/^\d+\s+Locations?$/i.test(s)) return "";
  if (/\bmultiple locations?\b/i.test(s)) return "Multiple Locations";

  s = s.replace(/^(?:US|USA|UK|India)\s*[-–—, ]\s*/i, "");

  // State City Intel format: e.g. "Arizona Phoenix", "Oregon Hillsboro"
  for (const [stName, code] of Object.entries(US_STATE_MAP)) {
    const rx = new RegExp("^" + stName + "\\s+([A-Za-z\\s]+)$", "i");
    const mStCity = s.match(rx);
    if (mStCity) {
      return `${toTitleCase(mStCity[1].toLowerCase().trim())}, ${code}`;
    }
  }

  // Walmart: "(USA) ISD Office - DGTC AR BENTONVILLE Home Office"
  const mWm = s.match(/\b([A-Z]{2})\s+([A-Z\s]+?)\s+Home Office/i);
  if (mWm) {
    return `${toTitleCase(mWm[2].trim().toLowerCase())}, ${mWm[1].toUpperCase()}`;
  }

  // Micron: "Longmont MAX Office CO"
  const mMi = s.match(/^([A-Za-z]+).*?\b([A-Z]{2})\b$/);
  if (mMi && US_CODE_SET.has(mMi[2].toUpperCase())) {
    return `${toTitleCase(mMi[1].toLowerCase())}, ${mMi[2].toUpperCase()}`;
  }

  // Intel Europe: "Poland Gdansk", "Ireland Leixlip"
  const mIntelEu = s.match(/^(Poland|Ireland|Germany|UK|France|Spain|Italy|Sweden|Romania|Czech Republic)\s+([A-Za-z]+)$/i);
  if (mIntelEu) {
    return `${toTitleCase(mIntelEu[2].toLowerCase())}, ${toTitleCase(mIntelEu[1].toLowerCase())}`;
  }

  // Microsoft format: "United States, Virginia, Reston"
  const mMs = s.match(/^(?:United States|Czech Republic|Belgium|Netherlands|Poland|Germany|Ireland),\s*([^,]+),\s*([^,]+)$/i);
  if (mMs) {
    const p1 = mMs[1].trim();
    const p2 = mMs[2].trim();
    if (US_STATE_MAP[p1.toLowerCase()]) {
      return `${toTitleCase(p2.toLowerCase())}, ${US_STATE_MAP[p1.toLowerCase()]}`;
    }
    return `${toTitleCase(p2.toLowerCase())}, ${toTitleCase(p1.toLowerCase())}`;
  }

  const parts = s.split(",").map(p => p.trim()).filter(Boolean);
  const cleaned = [];
  for (const p of parts) {
    if (/^(?:\d{4,6}(?:-\d{4})?|[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}|H91\s*[A-Z0-9]+)$/i.test(p)) continue;
    if (/^(?:United States(?: of America)?|USA|U\.S\.A\.|US|Canada|CAN|United Kingdom|UK|Great Britain|ESP|FRA|DEU|India)$/i.test(p)) continue;
    if (/^(?:N\/A|NONE)$/i.test(p)) continue;
    cleaned.push(p);
  }

  if (cleaned.length === 0) return s;

  if (cleaned.length >= 2) {
    const part0 = toTitleCase(cleaned[0].replace(/_/g, " ").toLowerCase());
    const part1 = cleaned[1].trim();
    if (part0.toLowerCase() === "all") {
      return toTitleCase(part1.toLowerCase());
    }

    if (KNOWN_COUNTRY_NAMES.has(part0.toLowerCase()) && !KNOWN_COUNTRY_NAMES.has(part1.toLowerCase())) {
      return `${toTitleCase(part1.toLowerCase())}, ${part0}`;
    }

    if (US_STATE_MAP[part0.toLowerCase()] && !US_STATE_MAP[part1.toLowerCase()]) {
      return `${toTitleCase(part1.toLowerCase())}, ${US_STATE_MAP[part0.toLowerCase()]}`;
    }

    const city = part0;
    const stLower = part1.toLowerCase();
    if (US_STATE_MAP[stLower]) {
      return `${city}, ${US_STATE_MAP[stLower]}`;
    }
    if (CA_PROVINCE_MAP[stLower]) {
      return `${city}, ${CA_PROVINCE_MAP[stLower]}`;
    }
    if (US_CODE_SET.has(part1.toUpperCase())) {
      return `${city}, ${part1.toUpperCase()}`;
    }
    if (EU_COUNTRY_MAP[stLower]) {
      return `${city}, ${EU_COUNTRY_MAP[stLower]}`;
    }
    return `${city}, ${toTitleCase(stLower)}`;
  }

  if (cleaned.length === 1) {
    const c = toTitleCase(cleaned[0].replace(/_/g, " ").toLowerCase());
    if (US_CODE_SET.has(c.toUpperCase())) {
      return `${c.toUpperCase()}, US`;
    }
    if (US_STATE_MAP[c.toLowerCase()]) {
      return `${US_STATE_MAP[c.toLowerCase()]}, US`;
    }
    return c;
  }

  return s;
}

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
    if (HUB_PATTERNS["Other"].test(locText) || (j.city_tag || "").toLowerCase().includes("other")) {
      return true;
    }
    const pageHubs = Array.from(document.querySelectorAll(".hub-btn"))
      .map(b => b.dataset.hub)
      .filter(h => h && h !== "all" && h !== "Other" && !h.toLowerCase().includes("remote"));
    if (pageHubs.length > 0) {
      const matchesAnyPrimary = pageHubs.some(h => {
        const pat = HUB_PATTERNS[h];
        return (pat && pat.test(locText)) || j.city_tag === h;
      });
      if (!matchesAnyPrimary && !isJobRemote(j)) return true;
    }
    return false;
  }

  const pattern = HUB_PATTERNS[hub];
  if (pattern && pattern.test(locText)) {
    return true;
  }
  return j.city_tag === hub;
}

function formatLocationDisplay(j) {
  if (isJobRemote(j)) {
    return j.city_tag && j.city_tag.includes("Remote") ? j.city_tag : "Remote";
  }

  const tag = (j.city_tag || "").trim();
  const isOtherOrGeneric = !tag || /other|multiple/i.test(tag);

  // If already tagged with a recognized non-generic hub, display it
  if (tag && !isOtherOrGeneric) {
    return tag;
  }

  // Extract clean place name(s) from j.locations
  const rawLocs = j.locations || [];
  const cleanedLocs = [];
  for (const raw of rawLocs) {
    const c = cleanSingleLocation(raw, j.country);
    if (c && !cleanedLocs.includes(c)) {
      cleanedLocs.push(c);
    }
  }

  if (cleanedLocs.length === 1) {
    return cleanedLocs[0];
  }
  if (cleanedLocs.length === 2) {
    return `${cleanedLocs[0]}, ${cleanedLocs[1]}`;
  }
  if (cleanedLocs.length > 2) {
    return `${cleanedLocs[0]}, ${cleanedLocs[1]} (+${cleanedLocs.length - 2})`;
  }

  if (/multiple/i.test(tag) || rawLocs.some(l => /multiple/i.test(l))) {
    return "Multiple Locations";
  }
  const defaultByCountry = {
    "us": "United States",
    "ca": "Canada",
    "uk": "United Kingdom",
    "eu": "Europe",
    "in": "India"
  };
  return defaultByCountry[j.country] || "Global";
}

function initMobileSelects() {
  const hubSelect = document.getElementById("hub-select");
  const catSelect = document.getElementById("category-select");

  if (hubSelect && hubSelect.options.length <= 1) {
    const hubBtns = document.querySelectorAll(".hub-btn");
    if (hubBtns.length > 0) {
      hubSelect.innerHTML = "";
      hubBtns.forEach(btn => {
        const hubVal = btn.dataset.hub;
        const clone = btn.cloneNode(true);
        const countSpan = clone.querySelector(".count, .badge");
        if (countSpan) countSpan.remove();
        const label = clone.textContent.trim() || hubVal;
        const opt = document.createElement("option");
        opt.value = hubVal;
        opt.textContent = label;
        opt.dataset.label = label;
        hubSelect.appendChild(opt);
      });
    }
  }

  if (catSelect && catSelect.options.length <= 1) {
    const catPills = document.querySelectorAll("#category-pills .filter-pill");
    if (catPills.length > 0) {
      catSelect.innerHTML = "";
      catPills.forEach(pill => {
        const catVal = pill.dataset.cat;
        const clone = pill.cloneNode(true);
        const countSpan = clone.querySelector(".cat-count, .pill-count");
        if (countSpan) countSpan.remove();
        const label = clone.textContent.trim() || catVal;
        const opt = document.createElement("option");
        opt.value = catVal;
        opt.textContent = label;
        opt.dataset.label = label;
        catSelect.appendChild(opt);
      });
    }
  }
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

  const hubSelect = document.getElementById("hub-select");
  if (hubSelect) {
    Array.from(hubSelect.options).forEach(opt => {
      const hub = opt.value;
      const baseLabel = opt.dataset.label || opt.text.replace(/\s*\(\d+\)$/, "");
      opt.dataset.label = baseLabel;
      if (hub === "all") {
        opt.text = `${baseLabel} (${allJobs.length})`;
      } else {
        const count = allJobs.filter(j => jobMatchesHub(j, hub)).length;
        opt.text = `${baseLabel} (${count})`;
      }
    });
  }
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

  const catSelect = document.getElementById("category-select");
  if (catSelect) {
    Array.from(catSelect.options).forEach(opt => {
      const cat = opt.value;
      const baseLabel = opt.dataset.label || opt.text.replace(/\s*\(\d+\)$/, "");
      opt.dataset.label = baseLabel;
      if (cat === "all") {
        opt.text = `${baseLabel} (${allJobs.length})`;
      } else {
        const count = counts[cat] || 0;
        opt.text = `${baseLabel} (${count})`;
      }
    });
  }
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
  const compSelect = document.getElementById("company-select");
  if (state.company !== "all" && compSelect) {
    compSelect.value = state.company;
    compSelect.classList.add("is-filtered");
  }
  const sortSelect = document.getElementById("sort-select");
  if (state.sort !== "newest" && sortSelect) {
    sortSelect.value = state.sort;
    sortSelect.classList.add("is-filtered");
  }
  if (state.hub !== "all") {
    document.querySelectorAll(".hub-btn").forEach(b => b.classList.toggle("active", b.dataset.hub === state.hub));
    const hubSelect = document.getElementById("hub-select");
    if (hubSelect) {
      hubSelect.value = state.hub;
      hubSelect.classList.add("is-filtered");
    }
  }
  if (state.category !== "all") {
    document.querySelectorAll("#category-pills .filter-pill").forEach(p => p.classList.toggle("active", p.dataset.cat === state.category));
    const catSelect = document.getElementById("category-select");
    if (catSelect) {
      catSelect.value = state.category;
      catSelect.classList.add("is-filtered");
    }
  }
  if (state.newOnly) document.getElementById("btn-new").classList.add("active");
  if (state.savedOnly) document.getElementById("btn-saved").classList.add("active");
}

function filterAndSortJobs() {
  const q = state.query.toLowerCase();
  const filtered = allJobs.filter(j => {
    if (q) {
      const locDisplay = formatLocationDisplay(j);
      const hay = `${j.title} ${j.company} ${j.category || ""} ${j.city_tag || ""} ${locDisplay} ${(j.locations || []).join(" ")}`.toLowerCase();
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

  const container = document.getElementById("jobs-wrapper");
  if (!container) return;

  const countEl = document.getElementById("jobs-count");
  if (countEl) countEl.textContent = filtered.length;
  const savedCounterEl = document.getElementById("saved-counter");
  if (savedCounterEl) savedCounterEl.textContent = savedKeys.length;
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
    const dateInfo = formatJobDate(j);
    const catClass = j.category === "AI/ML" ? "cat-ai" : (j.category === "Hardware/Silicon" ? "cat-hw" : "");
    const dateTitle = dateInfo.isOfficial ? `Official posting date: ${dateInfo.fullDate}` : `First discovered by InternScan: ${dateInfo.fullDate} (employer hid post date)`;

    return `<div class="job-card">
      <div class="job-left">
        ${renderAvatar(j.company, false)}
        <div class="job-details">
          <div class="job-title-row">
            <span class="company-name">${j.company}</span>
            ${j.isNew ? '<span class="badge-status new">NEW</span>' : ''}
          </div>
          <div class="role-name">
            <a href="${j.url}" target="_blank" rel="noopener">${cleanDisplayTitle(j.title)}</a>
          </div>
          <div class="chips-row">
            <span class="chip hub">${ICONS.pin}${loc}</span>
            <span class="chip ${catClass}">${ICONS.briefcase}${j.category || "Software"}</span>
            <span class="chip chip-date" title="${dateTitle}">${ICONS.clock}${dateInfo.text}</span>
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
      const dateInfo = formatJobDate(j);
      const dateTitle = dateInfo.isOfficial ? `Official posting date: ${dateInfo.fullDate}` : `First discovered by InternScan: ${dateInfo.fullDate} (employer hid post date)`;

      return `<div class="compact-row">
        <div class="compact-role">
          ${renderAvatar(j.company, true)}
          <div class="compact-title-box">
            <div class="compact-title"><a href="${j.url}" target="_blank" rel="noopener">${cleanDisplayTitle(j.title)}</a></div>
            <div class="compact-sub">
              <span>${j.company}</span>
              ${j.isNew ? '<span class="badge-status new" style="font-size: 10px; padding: 1px 5px;">NEW</span>' : ''}
              <span class="compact-meta-inline" title="${dateTitle}"> · ${loc} · ${dateInfo.text}</span>
            </div>
          </div>
        </div>
        <div class="compact-col-loc"><span class="chip hub" style="font-size: 11px;">${loc}</span></div>
        <div class="compact-col-cat"><span class="chip" style="font-size: 11px;">${j.category || "Software"}</span></div>
        <div class="compact-col-date" style="font-size: 12.5px; color: var(--dim);" title="${dateTitle}">${dateInfo.text}</div>
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
  const compSelect = document.getElementById("company-select");
  if (compSelect) {
    compSelect.value = "all";
    compSelect.classList.remove("is-filtered");
  }
  const hubSelect = document.getElementById("hub-select");
  if (hubSelect) {
    hubSelect.value = "all";
    hubSelect.classList.remove("is-filtered");
  }
  const catSelect = document.getElementById("category-select");
  if (catSelect) {
    catSelect.value = "all";
    catSelect.classList.remove("is-filtered");
  }
  const sortSelect = document.getElementById("sort-select");
  if (sortSelect) {
    sortSelect.value = "newest";
    sortSelect.classList.remove("is-filtered");
  }
  document.querySelectorAll(".hub-btn").forEach(b => b.classList.toggle("active", b.dataset.hub === "all"));
  document.querySelectorAll("#category-pills .filter-pill").forEach(p => p.classList.toggle("active", p.dataset.cat === "all"));
  document.getElementById("btn-new").classList.remove("active");
  document.getElementById("btn-saved").classList.remove("active");

  renderJobs();
}

// Global Event Setup
const searchInput = document.getElementById("search-input");
const clearBtn = document.getElementById("clear-search");

if (searchInput) {
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
    if (clearBtn) clearBtn.style.display = state.query ? "flex" : "none";
    renderJobs();
  });
}

if (clearBtn) {
  clearBtn.addEventListener("click", () => {
    if (searchInput) {
      searchInput.value = "";
      searchInput.focus();
    }
    state.query = "";
    clearBtn.style.display = "none";
    renderJobs();
  });
}

document.querySelectorAll(".hub-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".hub-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    state.hub = btn.dataset.hub;
    const hs = document.getElementById("hub-select");
    if (hs) {
      hs.value = state.hub;
      hs.classList.toggle("is-filtered", state.hub !== "all");
    }
    renderJobs();
  });
});

document.querySelectorAll("#category-pills .filter-pill").forEach(pill => {
  pill.addEventListener("click", () => {
    document.querySelectorAll("#category-pills .filter-pill").forEach(p => p.classList.remove("active"));
    pill.classList.add("active");
    state.category = pill.dataset.cat;
    const cs = document.getElementById("category-select");
    if (cs) {
      cs.value = state.category;
      cs.classList.toggle("is-filtered", state.category !== "all");
    }
    renderJobs();
  });
});

const hubSelect = document.getElementById("hub-select");
if (hubSelect) {
  hubSelect.addEventListener("change", (e) => {
    state.hub = e.target.value;
    document.querySelectorAll(".hub-btn").forEach(b => b.classList.toggle("active", b.dataset.hub === state.hub));
    hubSelect.classList.toggle("is-filtered", state.hub !== "all");
    renderJobs();
  });
}

const categorySelect = document.getElementById("category-select");
if (categorySelect) {
  categorySelect.addEventListener("change", (e) => {
    state.category = e.target.value;
    document.querySelectorAll("#category-pills .filter-pill").forEach(p => p.classList.toggle("active", p.dataset.cat === state.category));
    categorySelect.classList.toggle("is-filtered", state.category !== "all");
    renderJobs();
  });
}

const btnNew = document.getElementById("btn-new");
if (btnNew) {
  btnNew.addEventListener("click", function() {
    state.newOnly = !state.newOnly;
    this.classList.toggle("active", state.newOnly);
    renderJobs();
  });
}

const btnSaved = document.getElementById("btn-saved");
if (btnSaved) {
  btnSaved.addEventListener("click", function() {
    state.savedOnly = !state.savedOnly;
    this.classList.toggle("active", state.savedOnly);
    renderJobs();
  });
}

const companySelect = document.getElementById("company-select");
if (companySelect) {
  companySelect.addEventListener("change", (e) => {
    state.company = e.target.value;
    companySelect.classList.toggle("is-filtered", state.company !== "all");
    renderJobs();
  });
}

const sortSelect = document.getElementById("sort-select");
if (sortSelect) {
  sortSelect.addEventListener("change", (e) => {
    state.sort = e.target.value;
    sortSelect.classList.toggle("is-filtered", state.sort !== "newest");
    renderJobs();
  });
}

const btnCards = document.getElementById("btn-view-cards");
const btnCompact = document.getElementById("btn-view-compact");

function setViewMode(mode) {
  state.view = mode;
  localStorage.setItem("tracker_view", mode);
  if (btnCards) btnCards.classList.toggle("active", mode === "cards");
  if (btnCompact) btnCompact.classList.toggle("active", mode === "compact");
  renderJobs();
}

if (btnCards && btnCompact) {
  btnCards.addEventListener("click", () => setViewMode("cards"));
  btnCompact.addEventListener("click", () => setViewMode("compact"));
  setViewMode(state.view);
}

// Theme Toggle
const themeBtn = document.getElementById("theme-btn");
const themeIcon = document.getElementById("theme-icon");
const currentTheme = localStorage.getItem("theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const metaTheme = document.querySelector('meta[name="theme-color"]');
  if (metaTheme) metaTheme.setAttribute("content", theme === "dark" ? "#07090e" : "#f8fafc");
  if (themeIcon) {
    themeIcon.innerHTML = theme === "dark"
      ? '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>'
      : '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
  }
}

applyTheme(currentTheme);
if (themeBtn) {
  themeBtn.addEventListener("click", () => {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    localStorage.setItem("theme", next);
    applyTheme(next);
  });
}

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
