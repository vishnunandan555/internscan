/* InternTrack India — App Logic
 * Auto-loaded by docs/index.html via <script src="js/app.js" defer>
 * Edit here; do NOT hand-edit inside index.html.
 */

var PRIMARY_DATA_URL = "./jobs.json";
var FALLBACK_DATA_URL = "https://raw.githubusercontent.com/vishnunandan555/interntrack-india/main/data/jobs.json";
var LOCAL_REL_URL = "../data/jobs.json";

var allJobs = [];
var savedKeys = JSON.parse(localStorage.getItem("saved_jobs_v2") || "[]");

var urlParams = new URLSearchParams(window.location.search);
var state = {
  query: urlParams.get("q") || "",
  hub: urlParams.get("hub") || "all",
  company: urlParams.get("company") || "all",
  category: urlParams.get("cat") || "all",
  sort: urlParams.get("sort") || "newest",
  view: localStorage.getItem("tracker_view") || "cards",
  newOnly: urlParams.get("new") === "true",
  savedOnly: false,
};

function syncUrlParams() {
  var p = new URLSearchParams();
  if (state.query) p.set("q", state.query);
  if (state.hub && state.hub !== "all") p.set("hub", state.hub);
  if (state.company && state.company !== "all") p.set("company", state.company);
  if (state.category && state.category !== "all") p.set("cat", state.category);
  if (state.sort && state.sort !== "newest") p.set("sort", state.sort);
  if (state.newOnly) p.set("new", "true");
  var qStr = p.toString();
  var newUrl = window.location.pathname + (qStr ? "?" + qStr : "") + window.location.hash;
  window.history.replaceState({}, "", newUrl);
}

function injectJobSchema(jobs) {
  try {
    var oldScript = document.getElementById("schema-job-postings");
    if (oldScript) oldScript.remove();

    var script = document.createElement("script");
    script.id = "schema-job-postings";
    script.type = "application/ld+json";

    var schemaData = {
      "@context": "https://schema.org",
      "@type": "ItemList",
      "name": "Verified Tech & Software Internships India 2026-2027",
      "description": "Daily verified directory of software engineering, AI/ML, data, and cloud internships across 55+ tech employers in India.",
      "numberOfItems": jobs.length,
      "itemListElement": jobs.slice(0, 30).map(function(j, idx) {
        var postDate = j.first_seen || new Date().toISOString().slice(0, 10);
        return {
          "@type": "ListItem",
          "position": idx + 1,
          "item": {
            "@type": "JobPosting",
            "title": j.title,
            "description": "Verified " + (j.category || "Software") + " internship role at " + j.company + " in " + (j.locations ? j.locations.join(", ") : "India") + ". Direct official portal listing on InternTrack India.",
            "datePosted": postDate,
            "employmentType": "INTERN",
            "hiringOrganization": {
              "@type": "Organization",
              "name": j.company
            },
            "jobLocation": {
              "@type": "Place",
              "address": {
                "@type": "PostalAddress",
                "addressLocality": j.city_tag || "Bengaluru",
                "addressCountry": "IN"
              }
            },
            "url": j.url
          }
        };
      })
    };
    script.textContent = JSON.stringify(schemaData);
    document.head.appendChild(script);
  } catch (e) {
    console.warn("Schema injection error:", e);
  }
}

function formatRelativeDate(dateStr) {
  if (!dateStr) return "Recently";
  var diffMs = new Date() - new Date(dateStr + "T00:00:00Z");
  var days = Math.floor(diffMs / 86400000);
  if (days <= 0) return "Today";
  if (days === 1) return "Yesterday";
  return days + "d ago";
}

function getAvatarLetters(company) {
  if (!company) return "CO";
  var parts = company.trim().split(" ");
  if (parts.length > 1) return (parts[0][0] + parts[1][0]).toUpperCase();
  return company.slice(0, 2).toUpperCase();
}

function getCompanySlug(company) {
  if (!company) return "";
  return company.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

function renderAvatar(company, isCompact) {
  var slug = getCompanySlug(company);
  var letters = getAvatarLetters(company);
  var boxCls = isCompact ? "compact-avatar" : "company-avatar";
  var imgCls = isCompact ? "compact-logo-img" : "company-logo-img";
  return '<div class="' + boxCls + '" title="' + company + '">' +
    '<img class="' + imgCls + '" src="./logos/' + slug + '.png" alt="' + company + '" onerror="this.style.display=\'none\'; if(this.nextElementSibling) this.nextElementSibling.style.display=\'block\';" loading="lazy">' +
    '<span class="avatar-fallback" style="display:none;">' + letters + '</span>' +
  '</div>';
}

function showToast(msg) {
  var toast = document.getElementById("toast");
  document.getElementById("toast-text").innerText = msg;
  toast.classList.add("show");
  setTimeout(function() { toast.classList.remove("show"); }, 2400);
}

function loadJobs() {
  fetch(PRIMARY_DATA_URL)
    .then(function(r) {
      if (r.ok) return r.json();
      return fetch(FALLBACK_DATA_URL).then(function(r2) {
        if (r2.ok) return r2.json();
        return fetch(LOCAL_REL_URL).then(function(r3) { return r3.json(); });
      });
    })
    .then(function(data) {
      var updated = data.updated_at ? new Date(data.updated_at) : new Date();
      var cutoff = new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10);

      allJobs = Object.keys(data.jobs || {}).map(function(k) {
        var j = data.jobs[k];
        j.uid = k;
        j.isNew = (j.first_seen || "") >= cutoff;
        return j;
      }).filter(function(j) { return j.active; });

      document.getElementById("metric-jobs").innerText = allJobs.length;
      var companies = {};
      allJobs.forEach(function(j) { companies[j.company] = true; });
      document.getElementById("metric-companies").innerText = Object.keys(companies).length;

      document.getElementById("last-updated-text").innerText = "Last checked: " + updated.toLocaleDateString() + " " + updated.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

      updateHubCounts();
      updateCategoryCounts();
      populateCompanies();

      // Sync initial UI state from URL params
      if (state.query) {
        document.getElementById("search-input").value = state.query;
        document.getElementById("clear-search").style.display = "flex";
      }
      if (state.company !== "all") {
        document.getElementById("company-select").value = state.company;
      }
      if (state.sort !== "newest") {
        document.getElementById("sort-select").value = state.sort;
      }
      if (state.hub !== "all") {
        document.querySelectorAll(".hub-btn").forEach(function(b) {
          b.classList.toggle("active", b.dataset.hub === state.hub);
        });
      }
      if (state.category !== "all") {
        document.querySelectorAll("#category-pills .filter-pill").forEach(function(p) {
          p.classList.toggle("active", p.dataset.cat === state.category);
        });
      }
      if (state.newOnly) {
        document.getElementById("btn-new").classList.add("active");
      }

      renderJobs();
      injectJobSchema(allJobs);
    })
    .catch(function(err) {
      console.error(err);
      document.getElementById("jobs-wrapper").innerHTML = '<div class="empty-state"><h3>Unable to load data/jobs.json</h3><p>' + err.message + '</p></div>';
    });
}

function updateHubCounts() {
  var counts = { all: allJobs.length, blr: 0, hyd: 0, pune: 0, ncr: 0, chn: 0, bom: 0, rem: 0 };
  allJobs.forEach(function(j) {
    var h = j.city_tag || "";
    if (h === "Bengaluru") counts.blr++;
    else if (h === "Hyderabad") counts.hyd++;
    else if (h === "Pune") counts.pune++;
    else if (h === "Delhi-NCR") counts.ncr++;
    else if (h === "Chennai") counts.chn++;
    else if (h === "Mumbai") counts.bom++;
    else if (h === "Remote (India)") counts.rem++;
  });

  document.getElementById("count-all").innerText = counts.all;
  document.getElementById("count-blr").innerText = counts.blr;
  document.getElementById("count-hyd").innerText = counts.hyd;
  document.getElementById("count-pune").innerText = counts.pune;
  document.getElementById("count-ncr").innerText = counts.ncr;
  document.getElementById("count-chn").innerText = counts.chn;
  document.getElementById("count-bom").innerText = counts.bom;
  document.getElementById("count-rem").innerText = counts.rem;
}

function updateCategoryCounts() {
  var cats = {};
  allJobs.forEach(function(j) {
    var c = j.category || "Software";
    cats[c] = (cats[c] || 0) + 1;
  });

  var map = {
    "Software": "Software",
    "AI/ML": "AIML",
    "Data": "Data",
    "Hardware/Silicon": "HardwareSilicon",
    "Backend/Infra": "BackendInfra",
    "Frontend": "Frontend",
    "Mobile": "Mobile",
    "QA": "QA",
    "Security": "Security"
  };

  Object.keys(map).forEach(function(cat) {
    var el = document.getElementById("cat-count-" + map[cat]);
    if (el) {
      var num = cats[cat] || 0;
      el.innerText = num > 0 ? num : "";
    }
  });
}

function populateCompanies() {
  var select = document.getElementById("company-select");
  var cos = {};
  allJobs.forEach(function(j) { cos[j.company] = (cos[j.company] || 0) + 1; });
  var sorted = Object.keys(cos).sort();

  select.innerHTML = '<option value="all">All Companies (' + allJobs.length + ')</option>';
  sorted.forEach(function(c) {
    var opt = document.createElement("option");
    opt.value = c;
    opt.innerText = c + " (" + cos[c] + ")";
    select.appendChild(opt);
  });
}

function renderJobs() {
  syncUrlParams();
  var filtered = allJobs.filter(function(j) {
    if (state.query) {
      var q = state.query.toLowerCase();
      var hay = (j.title + " " + j.company + " " + (j.category || "") + " " + (j.city_tag || "") + " " + (j.locations || []).join(" ")).toLowerCase();
      if (hay.indexOf(q) === -1) return false;
    }
    if (state.hub !== "all" && j.city_tag !== state.hub) return false;
    if (state.company !== "all" && j.company !== state.company) return false;
    if (state.category !== "all" && j.category !== state.category) return false;
    if (state.newOnly && !j.isNew) return false;
    if (state.savedOnly && savedKeys.indexOf(j.uid) === -1) return false;
    return true;
  });

  document.getElementById("jobs-count").innerText = filtered.length;
  document.getElementById("saved-counter").innerText = savedKeys.length;

  var container = document.getElementById("jobs-wrapper");
  if (!filtered.length) {
    container.innerHTML = '<div class="empty-state">' +
      '<svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>' +
      '<h3>No matching internships found</h3>' +
      '<p>Try adjusting your search query, location filter, or role category.</p>' +
      '<button class="btn-reset" onclick="resetFilters()">Reset All Filters</button>' +
    '</div>';
    return;
  }

  if (state.sort === "newest") {
    filtered.sort(function(a, b) {
      var da = a.posted || a.first_seen || "";
      var db = b.posted || b.first_seen || "";
      return db.localeCompare(da);
    });
  } else if (state.sort === "company") {
    filtered.sort(function(a, b) {
      return a.company.localeCompare(b.company);
    });
  } else if (state.sort === "title") {
    filtered.sort(function(a, b) {
      return a.title.localeCompare(b.title);
    });
  }

  if (state.view === "compact") {
    renderCompactView(filtered, container);
  } else {
    renderCardsView(filtered, container);
  }
}

function renderCardsView(filtered, container) {
  var html = '<div class="job-grid-cards">' + filtered.map(function(j) {
    var isSaved = savedKeys.indexOf(j.uid) !== -1;
    var locDisplay = j.city_tag || (j.locations && j.locations[0]) || "India";
    var dateDisplay = formatRelativeDate(j.posted || j.first_seen);
    var catClass = (j.category === "AI/ML") ? "cat-ai" : (j.category === "Hardware/Silicon" ? "cat-hw" : "");

    return '<div class="job-card">' +
      '<div class="job-left">' +
        renderAvatar(j.company, false) +
        '<div class="job-details">' +
          '<div class="job-title-row">' +
            '<span class="company-name">' + j.company + '</span>' +
            (j.isNew ? '<span class="badge-status new">NEW</span>' : '') +
          '</div>' +
          '<div class="role-name">' +
            '<a href="' + j.url + '" target="_blank" rel="noopener">' + j.title + '</a>' +
          '</div>' +
          '<div class="chips-row">' +
            '<span class="chip hub">' +
              '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>' +
              locDisplay +
            '</span>' +
            '<span class="chip ' + catClass + '">' +
              '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>' +
              (j.category || "Software") +
            '</span>' +
            '<span class="chip">' +
              '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>' +
              dateDisplay +
            '</span>' +
          '</div>' +
        '</div>' +
      '</div>' +
      '<div class="job-actions">' +
        '<button class="action-icon-btn ' + (isSaved ? 'saved' : '') + '" onclick="toggleSave(\'' + j.uid + '\')" title="' + (isSaved ? 'Remove from bookmarks' : 'Bookmark role') + '">' +
          '<svg width="15" height="15" viewBox="0 0 24 24" fill="' + (isSaved ? 'currentColor' : 'none') + '" stroke="currentColor" stroke-width="2.2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>' +
        '</button>' +
        '<button class="action-icon-btn" onclick="copyRoleLink(\'' + j.url + '\')" title="Copy job link">' +
          '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>' +
        '</button>' +
        '<a href="' + j.url + '" target="_blank" rel="noopener" class="btn-apply">' +
          'Apply' +
          '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>' +
        '</a>' +
      '</div>' +
    '</div>';
  }).join("") + '</div>';

  container.innerHTML = html;
}

function renderCompactView(filtered, container) {
  var html = '<div class="job-grid-compact">' +
    '<div class="compact-header">' +
      '<div>Role & Company</div>' +
      '<div>Location</div>' +
      '<div>Category</div>' +
      '<div>Date</div>' +
      '<div style="text-align: right;">Action</div>' +
    '</div>' +
    filtered.map(function(j) {
      var isSaved = savedKeys.indexOf(j.uid) !== -1;
      var locDisplay = j.city_tag || (j.locations && j.locations[0]) || "India";
      var dateDisplay = formatRelativeDate(j.posted || j.first_seen);

      return '<div class="compact-row">' +
        '<div class="compact-role">' +
          renderAvatar(j.company, true) +
          '<div class="compact-title-box">' +
            '<div class="compact-title"><a href="' + j.url + '" target="_blank" rel="noopener">' + j.title + '</a></div>' +
            '<div class="compact-sub">' +
              '<span>' + j.company + '</span>' +
              (j.isNew ? '<span class="badge-status new" style="font-size: 10px; padding: 1px 5px;">NEW</span>' : '') +
              '<span class="compact-meta-inline"> · ' + locDisplay + ' · ' + dateDisplay + '</span>' +
            '</div>' +
          '</div>' +
        '</div>' +
        '<div class="compact-col-loc"><span class="chip hub" style="font-size: 11px;">' + locDisplay + '</span></div>' +
        '<div class="compact-col-cat"><span class="chip" style="font-size: 11px;">' + (j.category || "Software") + '</span></div>' +
        '<div class="compact-col-date" style="font-size: 12.5px; color: var(--dim);">' + dateDisplay + '</div>' +
        '<div class="compact-actions">' +
          '<button class="action-icon-btn ' + (isSaved ? 'saved' : '') + '" style="width: 32px; height: 32px;" onclick="toggleSave(\'' + j.uid + '\')" title="Bookmark">' +
            '<svg width="13" height="13" viewBox="0 0 24 24" fill="' + (isSaved ? 'currentColor' : 'none') + '" stroke="currentColor" stroke-width="2.2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>' +
          '</button>' +
          '<a href="' + j.url + '" target="_blank" rel="noopener" class="compact-btn-apply">' +
            'Apply' +
            '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>' +
          '</a>' +
        '</div>' +
      '</div>';
    }).join("") +
  '</div>';

  container.innerHTML = html;
}

function toggleSave(uid) {
  var idx = savedKeys.indexOf(uid);
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
  navigator.clipboard.writeText(url).then(function() {
    showToast("Link copied to clipboard");
  }).catch(function() {
    showToast("Could not copy link");
  });
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
  document.querySelectorAll(".hub-btn").forEach(function(b) {
    b.classList.toggle("active", b.dataset.hub === "all");
  });
  document.querySelectorAll("#category-pills .filter-pill").forEach(function(p) {
    p.classList.toggle("active", p.dataset.cat === "all");
  });
  document.getElementById("btn-new").classList.remove("active");
  document.getElementById("btn-saved").classList.remove("active");
  renderJobs();
}

// Keyboard shortcut: Press "/" to focus search
document.addEventListener("keydown", function(e) {
  if (e.key === "/" && document.activeElement !== searchInput) {
    e.preventDefault();
    searchInput.focus();
  } else if (e.key === "Escape" && document.activeElement === searchInput) {
    searchInput.blur();
  }
});

// Event Listeners
var searchInput = document.getElementById("search-input");
var clearBtn = document.getElementById("clear-search");

searchInput.addEventListener("input", function(e) {
  state.query = e.target.value.trim();
  clearBtn.style.display = state.query ? "flex" : "none";
  renderJobs();
});

clearBtn.addEventListener("click", function() {
  searchInput.value = "";
  state.query = "";
  clearBtn.style.display = "none";
  searchInput.focus();
  renderJobs();
});

// Hub filter buttons
document.querySelectorAll(".hub-btn").forEach(function(btn) {
  btn.addEventListener("click", function() {
    document.querySelectorAll(".hub-btn").forEach(function(b) { b.classList.remove("active"); });
    btn.classList.add("active");
    state.hub = btn.dataset.hub;
    renderJobs();
  });
});

// Category filter pills
document.querySelectorAll("#category-pills .filter-pill").forEach(function(pill) {
  pill.addEventListener("click", function() {
    document.querySelectorAll("#category-pills .filter-pill").forEach(function(p) { p.classList.remove("active"); });
    pill.classList.add("active");
    state.category = pill.dataset.cat;
    renderJobs();
  });
});

// Quick Toggles
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

document.getElementById("company-select").addEventListener("change", function(e) {
  state.company = e.target.value;
  renderJobs();
});

document.getElementById("sort-select").addEventListener("change", function(e) {
  state.sort = e.target.value;
  renderJobs();
});

// View Switcher (Cards vs Compact)
var btnCards = document.getElementById("btn-view-cards");
var btnCompact = document.getElementById("btn-view-compact");

function setViewMode(mode) {
  state.view = mode;
  localStorage.setItem("tracker_view", mode);
  btnCards.classList.toggle("active", mode === "cards");
  btnCompact.classList.toggle("active", mode === "compact");
  renderJobs();
}

btnCards.addEventListener("click", function() { setViewMode("cards"); });
btnCompact.addEventListener("click", function() { setViewMode("compact"); });
setViewMode(state.view);

// Dark/Light Theme with SVG Icon update
var themeBtn = document.getElementById("theme-btn");
var themeIcon = document.getElementById("theme-icon");
var currentTheme = localStorage.getItem("theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  if (theme === "dark") {
    themeIcon.innerHTML = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
  } else {
    themeIcon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
  }
}

applyTheme(currentTheme);

themeBtn.addEventListener("click", function() {
  var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
  localStorage.setItem("theme", next);
  applyTheme(next);
});

loadJobs();
