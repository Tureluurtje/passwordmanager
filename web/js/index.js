import { handleAddPassword, handleGetPassword } from "./password.js";
import { setEncContext, retrieveEncKey } from "./password.js";

// Validate user session on page load
// Validate session (used before initial render to avoid starting work
// (like favicon fetches) when the user will immediately be redirected).
async function validateSession() {
  try {
    const res = await fetch("/validate-session");
    return res.status !== 401;
  } catch (e) {
    return false;
  }
}

// Password data
let passwordData = "";

async function retrieveVault() {
  const { user, encKey } = retrieveEncKey();
  const vaultData = await handleGetPassword({ user, encKey });
  return vaultData;
}

// State
let selectedCategory = "vaults";
let selectedPassword = "";
let searchTerm = "";
let showPassword = false;

// Helper functions
function getFirstLetter(str) {
  if (!str || typeof str !== "string") return "";
  return str.trim().charAt(0).toUpperCase();
}

function getIconColor(name) {
  if (!name) return "#888888"; // fallback gray

  // Simple hash function
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }

  // Convert hash to hex color
  let color = "#";
  for (let i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 0xff;
    // ensure not too dark (min 80) to avoid black
    const adjusted = Math.max(80, value);
    color += adjusted.toString(16).padStart(2, "0");
  }

  return color;
}

async function checkPassword(password) {
  try{
    // SHA-1 hash in browser
    const enc = new TextEncoder().encode(password);
    const buffer = await crypto.subtle.digest("SHA-1", enc);
    const hashArray = Array.from(new Uint8Array(buffer));
    const sha1 = hashArray.map(b => b.toString(16).padStart(2, "0")).join("").toUpperCase();

    const prefix = sha1.substring(0, 5);
    const suffix = sha1.substring(5);

    // Send only prefix + suffix, NOT password
    const response = await fetch("/check-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prefix, suffix }),
    });

    if (!response.ok) throw new Error("Server error: " + response.status);
    const result = await response.json();
    return result.breached;
  } catch (e) {
    return e
  }
}

// Fetch favicon with caching
async function getFavicon(domain) {
  const CACHE_KEY = `fav:${domain}`;
  const TTL_MS = 1000 * 60 * 60 * 24; // 24 hours

  try {
    // Try localStorage first
    try {
      const raw = localStorage.getItem(CACHE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && parsed.ts && Date.now() - parsed.ts < TTL_MS) {
          return parsed.url || null;
        }
      }
    } catch (e) {
      // localStorage might be disabled; ignore silently
    }

    const response = await fetch(
      `/favicon?domain=${encodeURIComponent(domain)}`
    );
    if (!response.ok) throw new Error("Server error");

    const data = await response.json();
    const faviconUrl = data.favicon || null;

    // Store in cache (best-effort)
    try {
      localStorage.setItem(
        CACHE_KEY,
        JSON.stringify({ url: faviconUrl, ts: Date.now() })
      );
    } catch (e) {
      // ignore
    }

    return faviconUrl;
  } catch (e) {
    // Ignore aborts (happen during navigation) and don't spam the console.
    if (e && e.name === "AbortError") return null;
    console.error("Error fetching favicon:", e);
    return null;
  }
}

function getStrengthClass(score) {
  if (score < 40) return "weak";
  if (score < 70) return "medium";
  return "strong";
}

function ratePassword(password) {
  if (!password || typeof password !== "string") return 1;

  let score = 0;

  const length = password.length;
  const hasLower = /[a-z]/.test(password);
  const hasUpper = /[A-Z]/.test(password);
  const hasDigit = /\d/.test(password);
  const hasSymbol = /[^A-Za-z0-9]/.test(password);

  // Base score: length (reduce multiplier for faster drop)
  score += Math.min(length * 2, 30); // up to 30 points

  // Character variety
  if (hasLower) score += 8;
  if (hasUpper) score += 8;
  if (hasDigit) score += 8;
  if (hasSymbol) score += 8;

  // Bonus: mix of letters, digits, symbols
  if ((hasLower || hasUpper) && hasDigit && hasSymbol) score += 8;

  // Penalty: only letters or only digits
  if (/^[a-zA-Z]+$/.test(password)) score -= 15;
  if (/^\d+$/.test(password)) score -= 15;

  // Penalty: repeated characters (increase penalty)
  const repeats = password.match(/(.)\1+/g);
  if (repeats) score -= repeats.reduce((sum, r) => sum + r.length * 2, 0);

  // Penalty: sequential letters (abc, def) or digits (123) (increase penalty)
  const sequences = [
    "abcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "0123456789",
  ];
  for (let seq of sequences) {
    for (let i = 0; i < seq.length - 2; i++) {
      const pattern = seq.slice(i, i + 3);
      if (password.includes(pattern)) score -= 8;
    }
  }

  // Clamp score 1–100
  score = Math.max(1, Math.min(100, score));

  return score;
}

// Filter passwords based on category and search
function getFilteredPasswords() {
  const allPasswords = Object.values(passwordData);

  let filtered = allPasswords.filter((entry) => {
    const matchesSearch =
      entry.metadata.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.metadata.username.toLowerCase().includes(searchTerm.toLowerCase());

    if (selectedCategory === "vaults") return matchesSearch;
    if (selectedCategory === "favorites")
      return matchesSearch && entry.metadata.isFavorite;
    if (selectedCategory === "recent")
      return (
        matchesSearch &&
        [
          "google",
          "twitter",
          "github",
          "linkedin",
          "instagram",
          "amazon",
        ].includes(entry.id)
      );
    /*
    if (selectedCategory === "weak")
      return matchesSearch && entry.strength === "weak";
    */
    return matchesSearch && entry.category.toLowerCase() === selectedCategory;
  });

  return filtered;
}

// Render password list
function renderPasswordList() {
  const container = document.getElementById("passwordContainer");
  const filtered = getFilteredPasswords();

  const listTitle = document.getElementById("passwordListTitle");
  listTitle.textContent =
    selectedCategory === "recent" ? "RECENTLY USED" : "PASSWORDS";

  container.innerHTML = "";

  filtered.forEach((entry) => {
    // Use a div with role=button to prevent any accidental form submit
    // behavior while keeping styling. Make it keyboard accessible.
    const item = document.createElement("div");
    item.setAttribute("role", "button");
    item.setAttribute("tabindex", "0");
    item.className = `password-item ${
      selectedPassword === entry.id ? "active" : ""
    }`;
    item.addEventListener("click", (e) => {
      e.preventDefault();
      selectPassword(entry.id);
    });
    item.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        selectPassword(entry.id);
      }
    });

    getFavicon(entry.website).then((faviconUrl) => {
      if (faviconUrl) {
        item.innerHTML = `
            <div class="password-icon">
                <img class="password-favicon" src="${faviconUrl}" alt="${entry.metdata.name} favicon" />
            </div>
            <div class="password-details">
                <span class="password-name">${entry.name}</span>
                <span class="password-username">${entry.metadata.username}</span>
            </div>
            `;
      } else {
        item.innerHTML = `
            <div class="password-icon" style="background-color: ${getIconColor(
              entry.name
            )};">
                <span class="icon-default">${getFirstLetter(entry.metadata.name)}</span>
            </div>
            <div class="password-details">
                <span class="password-name">${entry.metadata.name}</span>
                <span class="password-username">${entry.metadata.username}</span>
            </div>
            `;
      }
      container.appendChild(item);
    });
  });
}

// Select password
function selectPassword(id) {
  selectedPassword = id;
  renderPasswordDetails();
}

// Render password details
function renderPasswordDetails() {
  const data = passwordData[selectedPassword];
  if (!data) {
    document.getElementById("emptyState").classList.remove("hidden");
    document.getElementById("passwordDetails").classList.add("hidden");
    return;
  }

  const strengthScore = ratePassword(data.password);
  const strength = getStrengthClass(strengthScore);

  document.getElementById("emptyState").classList.add("hidden");
  document.getElementById("passwordDetails").classList.remove("hidden");

  // Update header
  document.getElementById("passwordTitle").textContent = data.name;

  const starButton = document.getElementById("starButton");
  starButton.className = `star-button ${data.isFavorite ? "active" : ""}`;

  const breachBadge = document.getElementById("breachBadge");
  if (data.breachFound) {
    breachBadge.classList.remove("hidden");
  } else {
    breachBadge.classList.add("hidden");
  }

  // Update strength
  const strengthValue = document.getElementById("strengthValue");
  strengthValue.textContent = strength;
  strengthValue.className = `strength-value ${strength}`;

  const progressFill = document.getElementById("progressFill");
  progressFill.style.width = `${strengthScore}%`;
  progressFill.className = `progress-fill ${strength}`;

  document.getElementById(
    "strengthScore"
  ).textContent = `Score: ${strengthScore}/100`;
  document.getElementById(
    "lastChecked"
  ).textContent = `Last checked: ${data.lastModified}`;

  // Update fields
  document.getElementById("usernameValue").textContent = data.metadata.username;
  document.getElementById("passwordValue").textContent = showPassword
    ? data.password
    : "••••••••••••••••";
  document.getElementById("websiteValue").textContent = data.metadata.url;
  document.getElementById("categoryValue").textContent = data.metadata.category;
  document.getElementById("notesValue").textContent = data.metadata.notes;

  // Update activity
  document.getElementById("lastUsedValue").textContent = data.metadata.lastUsed;
  document.getElementById("lastModifiedValue").textContent = data.metadata.lastModified;
  document.getElementById("createdValue").textContent = data.metadata.createdDate;

  // Update security alert
  const securityAlert = document.getElementById("securityAlert");
  if (data.metadata.breachFound) {
    securityAlert.classList.remove("hidden");
  } else {
    securityAlert.classList.add("hidden");
  }
}

// Toggle password visibility
function togglePasswordVisibility() {
  showPassword = !showPassword;
  const passwordValue = document.getElementById("passwordValue");
  const eyeIcon = document.getElementById("eyeIcon");

  if (showPassword) {
    const data = passwordData[selectedPassword];
    passwordValue.textContent = data.password;
    eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
        `;
  } else {
    passwordValue.textContent = "••••••••••••••••";
    eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
        `;
  }
}

// Copy to clipboard
function copyToClipboard(elementId, isPassword = false) {
  let text;
  if (isPassword && !showPassword) {
    const data = passwordData[selectedPassword];
    text = data.password;
  } else {
    text = document.getElementById(elementId).textContent;
  }

  navigator.clipboard.writeText(text).then(() => {});
}

// Expose legacy/global handlers for inline `onclick` attributes in HTML.
// Modules don't export to the global scope, so attach these explicitly.
if (typeof window !== "undefined") {
  window.copyToClipboard = copyToClipboard;
  window.togglePasswordVisibility = togglePasswordVisibility;
  window.getStrengthClass = getStrengthClass;
}

// Modal functions
function openModal() {
  document.getElementById("addPasswordModal").classList.remove("hidden");
  document.body.style.overflow = "hidden";
}

function closeModal() {
  document.getElementById("addPasswordModal").classList.add("hidden");
  document.body.style.overflow = "auto";
  resetForm();
}

function resetForm() {
  document.getElementById("addPasswordForm").reset();
  showNewPassword = false;
  updateNewPasswordVisibility();
}

function generatePassword() {
  const lower = "abcdefghijklmnopqrstuvwxyz";
  const upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const digits = "0123456789";
  const allChars = lower + upper + digits;

  function randomChar(set) {
    return set[Math.floor(Math.random() * set.length)];
  }

  // Generate a segment of given length
  function generateSegment(length, ensureUpper = false, ensureDigit = false) {
    let segment = "";

    // If constraints: add one uppercase / digit first
    if (ensureUpper) segment += randomChar(upper);
    if (ensureDigit) segment += randomChar(digits);

    // Fill remaining with random chars
    while (segment.length < length) {
      segment += randomChar(allChars);
    }

    // Shuffle so uppercase/digit aren’t always at start
    return segment
      .split("")
      .sort(() => Math.random() - 0.5)
      .join("");
  }

  // Example: 3 segments of 5–6 chars
  const seg1 = generateSegment(6, false, true); // must contain a digit
  const seg2 = generateSegment(6); // no constraint
  const seg3 = generateSegment(6, true, false); // must contain uppercase

  return `${seg1}-${seg2}-${seg3}`;
}

// New password visibility toggle
let showNewPassword = false;

function toggleNewPasswordVisibility() {
  showNewPassword = !showNewPassword;
  updateNewPasswordVisibility();
}

function updateNewPasswordVisibility() {
  const passwordInput = document.getElementById("password");
  const eyeIcon = document.getElementById("newPasswordEyeIcon");

  if (showNewPassword) {
    passwordInput.type = "text";
    eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
        `;
  } else {
    passwordInput.type = "password";
    eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
        `;
  }
}

// Handle form submission
async function handleFormSubmission(event) {
  event.preventDefault();

  // Get form data
  let siteName = document.getElementById("siteName").value;
  let username = document.getElementById("username").value;
  let password = document.getElementById("password").value;
  let url = document.getElementById("website").value;
  let category = document.getElementById("category").value;
  let notes = document.getElementById("notes").value;

  let datetime = new Date().toISOString(); // Format: 2025-07-20T12:00:00Z

  let isFavorite = false;
  let isBreached = await checkPassword(password);

  try {
    // retrieveEncKey returns { user, encKey } which matches handleAddPassword's first param
    const ctx = retrieveEncKey();
    await handleAddPassword(
      ctx,
      siteName,
      url,
      username,
      password,
      notes,
      category,
      isFavorite,
      isBreached,
      datetime
    );
    alert("Password added successfully!");
    closeModal();
  } catch (err) {
    console.error("Failed to add password:", err);
    alert("Failed to add password. See console for details.");
  }
}

// Event listeners
document.addEventListener("DOMContentLoaded", async function () {
  // Ensure session is valid before doing expensive/async rendering.
  const ok = await validateSession();
  if (!ok) {
    window.location.href = "/login";
    return;
  }
  // Attempt to retrieve encryption context (may return {user, encKey})
  try {
    // Only attempt to retrieve the encryption context when document.name is set.
    // On a reload document.name can be empty and password.js may log "no token received".
    if (typeof document !== "undefined" && document.name) {
      const ctx = await retrieveEncKey();
      if (ctx && ctx.encKey) {
        encKey = ctx.encKey;
        if (ctx.user) setEncContext(ctx.user, ctx.encKey);
      }
    }
  } catch (e) {
    // ignore; missing key will be handled when adding passwords
  }
  // Category buttons
  document.querySelectorAll(".category-item").forEach((button) => {
    button.addEventListener("click", function () {
      document
        .querySelectorAll(".category-item")
        .forEach((b) => b.classList.remove("active"));
      this.classList.add("active");
      selectedCategory = this.dataset.category;
      renderPasswordList();
    });
  });

  // Search input
  document
    .getElementById("searchInput")
    .addEventListener("input", function (e) {
      searchTerm = e.target.value;
      renderPasswordList();
    });

  // Star button
  document.getElementById("starButton").addEventListener("click", function () {
    const data = passwordData[selectedPassword];
    if (data) {
      data.isFavorite = !data.isFavorite;
      this.classList.toggle("active");
    }
  });

  // Modal event listeners
  document
    .getElementById("addPasswordBtn")
    .addEventListener("click", openModal);
  document
    .getElementById("closeModalBtn")
    .addEventListener("click", closeModal);
  document.getElementById("cancelBtn").addEventListener("click", closeModal);

  // Close modal when clicking outside
  document
    .getElementById("addPasswordModal")
    .addEventListener("click", function (e) {
      if (e.target === this) {
        closeModal();
      }
    });

  // Form submission
  document
    .getElementById("addPasswordForm")
    .addEventListener("submit", handleFormSubmission);

  // Password visibility toggle
  document
    .getElementById("toggleNewPassword")
    .addEventListener("click", toggleNewPasswordVisibility);

  // Generate password button
  document
    .getElementById("generatePasswordBtn")
    .addEventListener("click", function () {
      const generatedPassword = generatePassword();
      document.getElementById("password").value = generatedPassword;
    });

  // ESC key to close modal
  document.addEventListener("keydown", function (e) {
    if (
      e.key === "Escape" &&
      !document.getElementById("addPasswordModal").classList.contains("hidden")
    ) {
      closeModal();
    }
  });

  passwordData = await retrieveVault();
  console.log(passwordData);
  renderPasswordList();
  renderPasswordDetails();

  window.addEventListener("pagehide", (event) => {
    navigator.sendBeacon("/logout");
  });
});
