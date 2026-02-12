// Gemini Pipeline Test App - Frontend Logic

document.addEventListener('DOMContentLoaded', function () {
    // File input handlers
    const fileInputs = [
        { input: document.getElementById('year1'), display: document.getElementById('file1Name') },
        { input: document.getElementById('year2'), display: document.getElementById('file2Name') },
        { input: document.getElementById('year3'), display: document.getElementById('file3Name') }
    ];

    fileInputs.forEach(({ input, display }) => {
        input.addEventListener('change', function () {
            display.textContent = this.files[0] ? this.files[0].name : 'No file chosen';
        });
    });

    // Form submission
    const form = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const progressSection = document.getElementById('progressSection');
    const errorSection = document.getElementById('errorSection');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Validate files are selected
        const file1 = document.getElementById('year1').files[0];
        const file2 = document.getElementById('year2').files[0];
        const file3 = document.getElementById('year3').files[0];

        if (!file1 || !file2 || !file3) {
            showError('Please select all 3 PDF files');
            return;
        }

        // Hide previous messages
        errorSection.style.display = 'none';
        progressSection.style.display = 'block';

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Processing...';

        try {
            // Create FormData
            const formData = new FormData(form);

            // Update progress
            updateProgress(10, 'Uploading PDFs to server...');

            // Send to backend
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            updateProgress(30, 'PDFs uploaded. Starting analysis...');

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Upload failed');
            }

            const result = await response.json();
            const jobId = result.job_id;

            // Poll for status (simplified - backend completes synchronously)
            updateProgress(100, 'Analysis complete! Redirecting...');

            // Redirect to results
            setTimeout(() => {
                window.location.href = `/results.html?job_id=${jobId}`;
            }, 1000);

        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'An error occurred during upload');
            submitBtn.disabled = false;
            submitBtn.textContent = '🚀 Analyze with Gemini';
            progressSection.style.display = 'none';
        }
    });
});

function updateProgress(percent, message) {
    const progressFill = document.getElementById('progressFill');
    const progressMessage = document.getElementById('progressMessage');

    progressFill.style.width = percent + '%';
    progressMessage.textContent = message;
}

function showError(message) {
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');

    errorMessage.textContent = message;
    errorSection.style.display = 'block';
}
