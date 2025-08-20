// Validate user session on page load
window.addEventListener('load', () => {
  fetch('/validate-session')  // Verify here because beacon can't redirect
    .then(res => {
      if (res.status === 401) {
        window.location.href = '/login';
      }
    })
    .catch(() => {
      window.location.href = '/login';
    });
});

// Password data
const passwordData = {
    google: {
        id: "google",
        name: "Google",
        username: "john.doe@gmail.com",
        password: "Str0ngP@ssw0rd2024!",
        website: "google.com",
        category: "Work",
        notes: "Primary work account used for Gmail, Drive, and other Google services",
        tags: ["work", "google", "email", "primary"],
        isFavorite: true,
        strength: "strong",
        strengthScore: 85,
        lastUsed: "2 hours ago",
        lastModified: "3 days ago",
        createdDate: "Jan 15, 2024",
        breachFound: false
    },
    facebook: {
        id: "facebook",
        name: "Facebook",
        username: "john.doe@gmail.com",
        password: "fb_P@ss123",
        website: "facebook.com",
        category: "Personal",
        notes: "Personal social media account",
        tags: ["personal", "social", "facebook"],
        isFavorite: false,
        strength: "medium",
        strengthScore: 65,
        lastUsed: "1 day ago",
        lastModified: "2 weeks ago",
        createdDate: "Dec 10, 2023",
        breachFound: false
    },
    netflix: {
        id: "netflix",
        name: "Netflix",
        username: "john.doe@gmail.com",
        password: "N3tfl1x_Str34m!ng",
        website: "netflix.com",
        category: "Entertainment",
        notes: "Family streaming account",
        tags: ["entertainment", "streaming", "netflix", "family"],
        isFavorite: true,
        strength: "strong",
        strengthScore: 90,
        lastUsed: "3 days ago",
        lastModified: "1 week ago",
        createdDate: "Nov 20, 2023",
        breachFound: false
    },
    twitter: {
        id: "twitter",
        name: "Twitter",
        username: "john.doe@gmail.com",
        password: "Tw1tt3r_S0c1@l",
        website: "twitter.com",
        category: "Social",
        notes: "Professional Twitter account for networking",
        tags: ["social", "twitter", "professional", "networking"],
        isFavorite: false,
        strength: "strong",
        strengthScore: 80,
        lastUsed: "5 hours ago",
        lastModified: "5 days ago",
        createdDate: "Oct 5, 2023",
        breachFound: false
    },
    dribbble: {
        id: "dribbble",
        name: "Dribbble",
        username: "john.doe@gmail.com",
        password: "Dr1bbl3_D3s1gn",
        website: "dribbble.com",
        category: "Work",
        notes: "Design portfolio and inspiration",
        tags: ["work", "design", "portfolio", "inspiration"],
        isFavorite: true,
        strength: "medium",
        strengthScore: 70,
        lastUsed: "1 week ago",
        lastModified: "2 weeks ago",
        createdDate: "Sep 12, 2023",
        breachFound: false
    },
    github: {
        id: "github",
        name: "GitHub",
        username: "john.doe@gmail.com",
        password: "G1tHub_C0d3_2024!",
        website: "github.com",
        category: "Work",
        notes: "Code repository and development projects",
        tags: ["work", "development", "code", "repository"],
        isFavorite: true,
        strength: "strong",
        strengthScore: 95,
        lastUsed: "30 minutes ago",
        lastModified: "1 day ago",
        createdDate: "Aug 1, 2023",
        breachFound: false
    },
    spotify: {
        id: "spotify",
        name: "Spotify",
        username: "john.doe@gmail.com",
        password: "Sp0t1fy_Mus1c",
        website: "spotify.com",
        category: "Entertainment",
        notes: "Music streaming service",
        tags: ["entertainment", "music", "streaming"],
        isFavorite: false,
        strength: "medium",
        strengthScore: 72,
        lastUsed: "2 days ago",
        lastModified: "1 month ago",
        createdDate: "Jul 18, 2023",
        breachFound: false
    },
    linkedin: {
        id: "linkedin",
        name: "LinkedIn",
        username: "john.doe@gmail.com",
        password: "L1nk3dIn_Pr0f3ss10n@l",
        website: "linkedin.com",
        category: "Work",
        notes: "Professional networking and career development",
        tags: ["work", "networking", "professional", "career"],
        isFavorite: true,
        strength: "strong",
        strengthScore: 88,
        lastUsed: "4 hours ago",
        lastModified: "6 days ago",
        createdDate: "Jun 25, 2023",
        breachFound: false
    },
    amazon: {
        id: "amazon",
        name: "Amazon",
        username: "john.doe@gmail.com",
        password: "amaz0n123",
        website: "amazon.com",
        category: "Shopping",
        notes: "Online shopping and Prime membership",
        tags: ["shopping", "ecommerce", "prime"],
        isFavorite: false,
        strength: "weak",
        strengthScore: 35,
        lastUsed: "1 day ago",
        lastModified: "6 months ago",
        createdDate: "May 10, 2023",
        breachFound: true
    },
    instagram: {
        id: "instagram",
        name: "Instagram",
        username: "john.doe@gmail.com",
        password: "Inst@gr@m_Ph0t0s",
        website: "instagram.com",
        category: "Social",
        notes: "Photo sharing and social networking",
        tags: ["social", "photos", "instagram"],
        isFavorite: false,
        strength: "medium",
        strengthScore: 68,
        lastUsed: "6 hours ago",
        lastModified: "3 weeks ago",
        createdDate: "Apr 2, 2023",
        breachFound: false
    }
};

// State
let selectedCategory = 'vaults';
let selectedPassword = 'google';
let searchTerm = '';
let showPassword = false;

// Helper functions
function getPasswordIcon(name) {
    const iconMap = {
        Google: "G", Facebook: "f", Netflix: "N", Twitter: "T", Dribbble: "D",
        GitHub: "G", Spotify: "S", LinkedIn: "L", Amazon: "A", Instagram: "I"
    };
    return iconMap[name] || name.charAt(0);
}

function getPasswordColorClass(name) {
    const colorMap = {
        Google: "icon-google", Facebook: "icon-facebook", Netflix: "icon-netflix",
        Twitter: "icon-twitter", Dribbble: "icon-dribbble", GitHub: "icon-github",
        Spotify: "icon-spotify", LinkedIn: "icon-linkedin", Amazon: "icon-amazon",
        Instagram: "icon-instagram"
    };
    return colorMap[name] || "icon-default";
}

function getStrengthClass(strength) {
    return `strength-${strength}`;
}

// Filter passwords based on category and search
function getFilteredPasswords() {
    const allPasswords = Object.values(passwordData);
    
    let filtered = allPasswords.filter(entry => {
        const matchesSearch = entry.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             entry.username.toLowerCase().includes(searchTerm.toLowerCase());
        
        if (selectedCategory === "vaults") return matchesSearch;
        if (selectedCategory === "favorites") return matchesSearch && entry.isFavorite;
        if (selectedCategory === "recent") return matchesSearch && ["google", "twitter", "github", "linkedin", "instagram", "amazon"].includes(entry.id);
        if (selectedCategory === "weak") return matchesSearch && entry.strength === "weak";
        return matchesSearch && entry.category.toLowerCase() === selectedCategory;
    });

    return filtered;
}

// Render password list
function renderPasswordList() {
    const container = document.getElementById('passwordContainer');
    const filtered = getFilteredPasswords();
    
    const listTitle = document.getElementById('passwordListTitle');
    listTitle.textContent = selectedCategory === 'recent' ? 'RECENTLY USED' : 'PASSWORDS';
    
    container.innerHTML = '';
    
    filtered.forEach(entry => {
        const item = document.createElement('button');
        item.className = `password-item ${selectedPassword === entry.id ? 'active' : ''}`;
        item.onclick = () => selectPassword(entry.id);
        
        item.innerHTML = `
            <div class="password-icon ${getPasswordColorClass(entry.name)}">
                ${getPasswordIcon(entry.name)}
            </div>
            <div class="password-info">
                <div class="password-name">
                    <p>${entry.name}</p>
                    <div class="strength-indicator ${getStrengthClass(entry.strength)}"></div>
                </div>
                <p class="password-username">${entry.username}</p>
                <p class="password-last-used">${entry.lastUsed}</p>
            </div>
        `;
        
        container.appendChild(item);
    });
}

// Select password
function selectPassword(id) {
    selectedPassword = id;
    renderPasswordList();
    renderPasswordDetails();
}

// Render password details
function renderPasswordDetails() {
    const data = passwordData[selectedPassword];
    if (!data) {
        document.getElementById('emptyState').classList.remove('hidden');
        document.getElementById('passwordDetails').classList.add('hidden');
        return;
    }

    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('passwordDetails').classList.remove('hidden');

    // Update header
    document.getElementById('passwordTitle').textContent = data.name;
    
    const starButton = document.getElementById('starButton');
    starButton.className = `star-button ${data.isFavorite ? 'active' : ''}`;
    
    const breachBadge = document.getElementById('breachBadge');
    if (data.breachFound) {
        breachBadge.classList.remove('hidden');
    } else {
        breachBadge.classList.add('hidden');
    }

    // Update strength
    const strengthValue = document.getElementById('strengthValue');
    strengthValue.textContent = data.strength;
    strengthValue.className = `strength-value ${data.strength}`;
    
    const progressFill = document.getElementById('progressFill');
    progressFill.style.width = `${data.strengthScore}%`;
    progressFill.className = `progress-fill ${data.strength}`;
    
    document.getElementById('strengthScore').textContent = `Score: ${data.strengthScore}/100`;
    document.getElementById('lastChecked').textContent = `Last checked: ${data.lastModified}`;

    // Update fields
    document.getElementById('usernameValue').textContent = data.username;
    document.getElementById('passwordValue').textContent = showPassword ? data.password : '••••••••••••••••';
    document.getElementById('websiteValue').textContent = data.website;
    document.getElementById('categoryValue').textContent = data.category;
    document.getElementById('notesValue').textContent = data.notes;
    
    // Update tags
    const tagsContainer = document.getElementById('tagsContainer');
    tagsContainer.innerHTML = '';
    data.tags.forEach(tag => {
        const tagEl = document.createElement('span');
        tagEl.className = 'tag';
        tagEl.textContent = tag;
        tagsContainer.appendChild(tagEl);
    });

    // Update activity
    document.getElementById('lastUsedValue').textContent = data.lastUsed;
    document.getElementById('lastModifiedValue').textContent = data.lastModified;
    document.getElementById('createdValue').textContent = data.createdDate;

    // Update security alert
    const securityAlert = document.getElementById('securityAlert');
    if (data.breachFound) {
        securityAlert.classList.remove('hidden');
    } else {
        securityAlert.classList.add('hidden');
    }
}

// Toggle password visibility
function togglePasswordVisibility() {
    showPassword = !showPassword;
    const passwordValue = document.getElementById('passwordValue');
    const eyeIcon = document.getElementById('eyeIcon');
    
    if (showPassword) {
        const data = passwordData[selectedPassword];
        passwordValue.textContent = data.password;
        eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
        `;
    } else {
        passwordValue.textContent = '••••••••••••••••';
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
    
    navigator.clipboard.writeText(text).then(() => {
        // Could add a toast notification here
        console.log('Copied to clipboard:', text);
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Category buttons
    document.querySelectorAll('.category-item').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.category-item').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            selectedCategory = this.dataset.category;
            renderPasswordList();
        });
    });

    // Search input
    document.getElementById('searchInput').addEventListener('input', function(e) {
        searchTerm = e.target.value;
        renderPasswordList();
    });

    // Star button
    document.getElementById('starButton').addEventListener('click', function() {
        const data = passwordData[selectedPassword];
        if (data) {
            data.isFavorite = !data.isFavorite;
            this.classList.toggle('active');
        }
    });

    // Initial render
    renderPasswordList();
    renderPasswordDetails();

    window.addEventListener('pagehide', (event) => {
        navigator.sendBeacon('/logout');
    });
});

