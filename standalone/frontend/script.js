// Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// State
let currentFilter = 'all';
let allFlags = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupUpload();
    setupFilters();
});

// Setup upload functionality
function setupUpload() {
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('fileInput');

    // Drag and drop
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.classList.add('dragover');
    });

    uploadBox.addEventListener('dragleave', () => {
        uploadBox.classList.remove('dragover');
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // Click to upload
    uploadBox.addEventListener('click', () => {
        fileInput.click();
    });
}

// Handle file upload
async function handleFileUpload(file) {
    // Validate file
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Invalid file type. Please upload a PDF file.');
        return;
    }

    // Validate filename format
    const filename = file.name.replace('.pdf', '').replace('.PDF', '');
    const pattern = /^([A-Z0-9]+)_(\d{4})$/i;
    if (!pattern.test(filename)) {
        showError('Invalid filename format. Expected: SYMBOL_YEAR.pdf (e.g., RELIANCE_2025.pdf)');
        return;
    }

    // Show progress
    document.getElementById('uploadProgress').style.display = 'block';
    document.getElementById('uploadBox').style.display = 'none';
    updateProgress(10, 'Uploading PDF...');

    try {
        // Upload file
        const formData = new FormData();
        formData.append('file', file);

        updateProgress(30, 'Processing PDF...');

        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const result = await response.json();
        updateProgress(50, 'Analyzing with FinEdge API...');

        // Poll for results
        await pollAnalysis(result.analysis_id);

    } catch (error) {
        console.error('Upload error:', error);
        showError(error.message);
        resetUpload();
    }
}

// Poll for analysis results
async function pollAnalysis(analysisId) {
    const maxAttempts = 60; // 5 minutes max
    let attempts = 0;

    const poll = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch analysis results');
            }

            const data = await response.json();

            if (data.status === 'completed') {
                updateProgress(100, 'Analysis complete!');
                setTimeout(() => {
                    displayResults(data);
                }, 500);
                return;
            } else if (data.status === 'failed') {
                throw new Error(data.error || 'Analysis failed');
            } else {
                // Still processing
                attempts++;
                if (attempts > maxAttempts) {
                    throw new Error('Analysis timeout');
                }

                const progress = 50 + (attempts * 0.5);
                updateProgress(Math.min(progress, 95), 'Analyzing PDF with Gemini AI...');
                
                setTimeout(poll, 5000); // Poll every 5 seconds
            }
        } catch (error) {
            console.error('Polling error:', error);
            showError(error.message);
            resetUpload();
        }
    };

    poll();
}

// Update progress bar
function updateProgress(percentage, text) {
    document.getElementById('progressFill').style.width = `${percentage}%`;
    document.getElementById('progressText').textContent = text;
}

// Display analysis results
function displayResults(data) {
    // Hide upload section
    document.getElementById('uploadProgress').style.display = 'none';
    
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';

    // Update company info
    document.getElementById('symbol').textContent = data.symbol;
    document.getElementById('fiscalYear').textContent = data.fiscal_year;
    document.getElementById('statementType').textContent = data.statement_type || 'Unknown';

    // Update risk score gauge
    const riskScore = data.risk_score || {};
    updateRiskGauge(riskScore.risk_score || 0, riskScore.risk_level || 'LOW');
    document.getElementById('riskDescription').textContent = 
        riskScore.risk_description || 'Risk assessment completed';

    // Update category breakdown
    updateCategoryBreakdown(riskScore.category_breakdown || {}, riskScore.category_scores || {});

    // Store flags globally
    allFlags = data.flags || [];

    // Update flags summary
    updateFlagsSummary(allFlags);

    // Display flags table
    displayFlags(allFlags);
}

// Update risk gauge
function updateRiskGauge(score, level) {
    document.getElementById('riskScore').textContent = score.toFixed(1);
    document.getElementById('riskLevel').textContent = level;

    // Update gauge arc
    const arcLength = 251.2; // Approximate arc length
    const offset = arcLength - (arcLength * score / 100);
    
    const gaugeArc = document.getElementById('gaugeArc');
    gaugeArc.style.strokeDashoffset = offset;

    // Color based on level
    const colors = {
        'LOW': '#4CAF50',
        'MODERATE': '#8BC34A',
        'ELEVATED': '#FFC107',
        'HIGH': '#FF9800',
        'CRITICAL': '#F44336'
    };
    gaugeArc.style.stroke = colors[level] || '#4CAF50';
}

// Update category breakdown
function updateCategoryBreakdown(breakdown, scores) {
    const categoryList = document.getElementById('categoryList');
    categoryList.innerHTML = '';

    const categories = [
        'Auditor',
        'Cash Flow',
        'Related Party',
        'Promoter',
        'Governance',
        'Balance Sheet',
        'Revenue Quality',
        'Textual Analysis'
    ];

    categories.forEach(category => {
        const catData = breakdown[category] || {};
        const score = scores[category] || 0;

        const item = document.createElement('div');
        item.className = 'category-item';
        item.innerHTML = `
            <h4>
                ${category}
                <span class="category-score">${score.toFixed(1)}</span>
            </h4>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${score}%"></div>
            </div>
            <div class="category-details">
                ${catData.flags_triggered || 0} / ${catData.flags_total || 0} flags triggered
            </div>
        `;
        categoryList.appendChild(item);
    });
}

// Update flags summary
function updateFlagsSummary(flags) {
    const total = flags.length;
    const triggered = flags.filter(f => f.triggered).length;

    document.getElementById('totalFlags').textContent = total;
    document.getElementById('triggeredFlags').textContent = triggered;

    // Count by severity
    const counts = { critical: 0, high: 0, medium: 0, low: 0 };
    flags.forEach(flag => {
        if (flag.triggered) {
            const severity = flag.severity.toLowerCase();
            if (counts.hasOwnProperty(severity)) {
                counts[severity]++;
            }
        }
    });

    document.getElementById('criticalCount').textContent = counts.critical;
    document.getElementById('highCount').textContent = counts.high;
    document.getElementById('mediumCount').textContent = counts.medium;
    document.getElementById('lowCount').textContent = counts.low;
}

// Display flags table
function displayFlags(flags) {
    const flagsTable = document.getElementById('flagsTable');
    flagsTable.innerHTML = '';

    // Filter flags
    let filteredFlags = flags;
    if (currentFilter === 'triggered') {
        filteredFlags = flags.filter(f => f.triggered);
    } else if (currentFilter !== 'all') {
        filteredFlags = flags.filter(f => f.category === currentFilter);
    }

    // Sort by flag_id
    filteredFlags.sort((a, b) => (a.flag_id || 0) - (b.flag_id || 0));

    filteredFlags.forEach(flag => {
        const item = document.createElement('div');
        item.className = `flag-item ${flag.triggered ? 'triggered' : ''}`;

        const header = document.createElement('div');
        header.className = 'flag-header';
        header.innerHTML = `
            <div class="flag-id">#${flag.flag_id}</div>
            <div class="flag-name">${flag.flag_name}</div>
            <div class="flag-category">${flag.category}</div>
            <div class="severity-badge ${flag.severity.toLowerCase()}">${flag.severity}</div>
            <div class="flag-status ${flag.triggered ? 'triggered' : 'not-triggered'}">
                ${flag.triggered ? 'TRIGGERED' : 'OK'}
            </div>
            <div class="flag-confidence">${flag.confidence || 0}%</div>
        `;

        const details = document.createElement('div');
        details.className = 'flag-details';
        details.innerHTML = `
            <div class="flag-evidence">
                <h5>Evidence:</h5>
                <p>${flag.evidence || 'No evidence provided'}</p>
                ${flag.page_references && flag.page_references.length > 0 
                    ? `<p class="flag-pages">Pages: ${flag.page_references.join(', ')}</p>`
                    : ''}
            </div>
            ${flag.value ? `
                <div class="flag-evidence">
                    <h5>Details:</h5>
                    <pre>${JSON.stringify(flag.value, null, 2)}</pre>
                </div>
            ` : ''}
        `;

        header.addEventListener('click', () => {
            details.classList.toggle('show');
        });

        item.appendChild(header);
        item.appendChild(details);
        flagsTable.appendChild(item);
    });
}

// Setup filters
function setupFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update filter
            currentFilter = btn.dataset.filter;

            // Re-display flags
            displayFlags(allFlags);
        });
    });
}

// Show error
function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorSection').style.display = 'block';
    document.getElementById('uploadProgress').style.display = 'none';
}

// Reset upload
function resetUpload() {
    document.getElementById('uploadBox').style.display = 'block';
    document.getElementById('uploadProgress').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
    document.getElementById('fileInput').value = '';
    document.getElementById('progressFill').style.width = '0%';
}
