const API_BASE = "http://127.0.0.1:8000";
let currentProvider = 'groq';

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const navItems = document.querySelectorAll('.nav-item');
const views = document.querySelectorAll('.view');
const districtDropdown = document.getElementById('district-dropdown');
const summaryData = document.getElementById('summary-data');

// --- View Switching ---
function switchView(viewId, btn) {
    document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
    const targetView = document.getElementById(viewId);
    if (targetView) targetView.classList.add('active');

    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    if (btn) btn.classList.add('active');

    if (viewId === 'dashboard-view') loadDistricts();
}

// --- Chat Logic ---
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage('user', { explanation: message });
    userInput.value = '';

    // Add loading indicator
    const loadingId = addLoadingIndicator();

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: message,
                provider: currentProvider
            })
        });
        const data = await response.json();
        console.log("Chat API Response:", data);

        removeLoadingIndicator(loadingId);
        appendMessage('assistant', data);
    } catch (err) {
        console.error("Chat API Error:", err);
        removeLoadingIndicator(loadingId);
        appendMessage('assistant', { explanation: "Error: Could not connect to the backend server. Make sure api.py is running!" });
    }
});

function appendMessage(role, data) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;

    // Fallback: Use explanation field, otherwise stringify the whole data object
    const text = (typeof data === 'string') ? data : (data.explanation || data.response || JSON.stringify(data));
    let contentHtml = `<div class="bubble">${text}</div>`;
    msgDiv.innerHTML = contentHtml;
    chatMessages.appendChild(msgDiv);

    if (role === 'assistant' && data.visuals && data.visuals.length > 0) {
        console.log("Assistant Visuals:", data.visuals);
        const explorer = document.getElementById('visuals-content');
        explorer.innerHTML = ''; // Clear for new response visuals

        const msgTime = Date.now();
        let visualsHtml = '';

        data.visuals.forEach((vis, idx) => {
            const visId = `vis-${msgTime}-${idx}`;
            let visHtml = `<div class="visual-container">
                                <h4 class="vis-title">${vis.title || ''}</h4>`;

            if (['bar', 'pie', 'line'].includes(vis.type)) {
                visHtml += `<div class="chart-container"><canvas id="${visId}"></canvas></div>`;
            } else if (vis.type === 'map') {
                visHtml += `<div id="${visId}" class="map-container"></div>`;
            } else if (vis.type === 'table') {
                visHtml += `<div class="table-wrapper"><table><thead><tr>`;
                vis.headers.forEach(h => visHtml += `<th>${h}</th>`);
                visHtml += `</tr></thead><tbody>`;
                vis.rows.forEach(row => {
                    visHtml += `<tr>`;
                    row.forEach(cell => visHtml += `<td>${cell}</td>`);
                    visHtml += `</tr>`;
                });
                visHtml += `</tbody></table></div>`;
            }

            visHtml += `</div>`;
            visualsHtml += visHtml;
        });

        // 2. Inject into DOM once
        explorer.innerHTML = visualsHtml;

        // 3. Initialize Charts & Maps after DOM injection
        data.visuals.forEach((vis, idx) => {
            const visId = `vis-${msgTime}-${idx}`;

            if (['bar', 'pie', 'line'].includes(vis.type)) {
                setTimeout(() => {
                    const canvas = document.getElementById(visId);
                    if (!canvas) {
                        console.error("Canvas not found:", visId);
                        return;
                    }
                    new Chart(canvas.getContext('2d'), {
                        type: vis.type,
                        data: {
                            labels: vis.labels,
                            datasets: vis.datasets.map(ds => ({
                                ...ds,
                                backgroundColor: vis.type === 'pie' ?
                                    ['#00d2ff', '#4ade80', '#fbbf24', '#f87171', '#a78bfa'] : '#00d2ff',
                                borderColor: '#00d2ff',
                                borderWidth: 1
                            }))
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { labels: { color: '#94a3b8', font: { family: 'Outfit', size: 10 } } }
                            },
                            scales: vis.type !== 'pie' ? {
                                y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } },
                                x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } }
                            } : {}
                        }
                    });
                }, 100);
            } else if (vis.type === 'map') {
                setTimeout(() => renderMap(visId, vis.location, vis.title), 150);
            }
        });
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
    setTimeout(() => {
        chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
    }, 100);
}


// --- AI Configuration ---
function setProvider(provider) {
    currentProvider = provider;

    // Update UI
    document.querySelectorAll('.ai-selector button').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`provider-${provider}`).classList.add('active');

    const status = document.getElementById('provider-status');
    if (provider === 'groq') {
        status.innerText = "Using high-speed cloud";
    } else {
        status.innerText = "Using local GPU/CPU";
    }

    console.log(`AI Provider switched to: ${currentProvider}`);
}

// Chart.js Default Config for dark mode
async function renderMap(containerId, locationName, title) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Default: Center of Maharashtra
    let lat = 19.7515;
    let lon = 75.7139;
    let zoom = 7;

    try {
        // Geocode using Nominatim (OSM)
        const searchQuery = `${locationName}, Maharashtra, India`;
        const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=1`);
        const results = await res.json();

        if (results && results.length > 0) {
            lat = parseFloat(results[0].lat);
            lon = parseFloat(results[0].lon);
            zoom = 11; // Zoom in for specific location
        }
    } catch (err) {
        console.warn("Geocoding failed, using default view.", err);
    }

    const map = L.map(containerId).setView([lat, lon], zoom);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    L.marker([lat, lon]).addTo(map)
        .bindPopup(`<b>${locationName}</b><br>${title || 'Location Reference'}`)
        .openPopup();
}

function addLoadingIndicator() {
    const id = 'loading-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message assistant loading';
    msgDiv.id = id;
    msgDiv.innerHTML = `<div class="bubble"><i class="fas fa-circle-notch fa-spin"></i> Analyzing data...</div>`;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function removeLoadingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

window.sendQuickQuery = (query) => {
    userInput.value = query;
    chatForm.dispatchEvent(new Event('submit'));
};

// --- Dashboard Logic ---
async function loadDistricts() {
    if (districtDropdown.options.length > 1) return; // Already loaded

    try {
        const res = await fetch(`${API_BASE}/districts`);
        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Database Error");
        }

        const districts = await res.json();

        if (!districts || districts.length === 0) {
            districtDropdown.innerHTML = '<option value="">No districts found</option>';
            return;
        }

        districtDropdown.innerHTML = '<option value="">Select District</option>';
        districts.forEach(d => {
            const opt = document.createElement('option');
            opt.value = d;
            opt.textContent = d;
            districtDropdown.appendChild(opt);
        });
    } catch (err) {
        console.error("Failed to load districts:", err);
        // Try to show specific message from API
        const errorMsg = err.message || "Backend unreachable";
        districtDropdown.innerHTML = `<option value="">${errorMsg}</option>`;
    }
}

districtDropdown.addEventListener('change', async () => {
    const district = districtDropdown.value;
    if (!district) return;

    summaryData.innerHTML = "Fetching stats...";

    try {
        const res = await fetch(`${API_BASE}/district-summary/${district}`);
        const data = await res.json();

        summaryData.innerHTML = `
            <div class="stats-result">
                <div class="stat-item"><span class="stat-label">Talukas</span><span class="stat-value">${data.talukas_analyzed}</span></div>
                <div class="stat-item"><span class="stat-label">Avg Rainfall</span><span class="stat-value">${data.avg_rainfall.toFixed(2)} mm</span></div>
                <div class="stat-item"><span class="stat-label">Total Recharge</span><span class="stat-value">${data.total_recharge.toFixed(2)} ham</span></div>
                <div class="stat-item"><span class="stat-label">Extraction Stage</span><span class="stat-value">${data.avg_stage_of_extraction.toFixed(2)}%</span></div>
            </div>
            <button onclick="sendQuickQuery('Give me a detailed report for ${district}')" style="margin-top: 20px; width: 100%; padding: 10px; border-radius: 8px; border: none; background: var(--accent); cursor: pointer; color: black; font-weight: bold;">Ask AI About This District</button>
        `;
    } catch (err) {
        summaryData.innerHTML = "Error fetching data for this district.";
    }
});
