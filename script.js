document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const urlInput = document.getElementById('youtube-url');
    const loadingSection = document.getElementById('loading');
    const resultsSection = document.getElementById('results');
    const ingredientList = document.getElementById('ingredient-list');
    const summaryText = document.getElementById('summary-text');
    const langDetected = document.getElementById('lang-detected');

    analyzeBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        if (!url) {
            alert('Please enter a YouTube URL');
            return;
        }

        // Show loading, hide results
        loadingSection.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            // Populate data
            ingredientList.innerHTML = '';
            data.ingredients.forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `<span class="ingredient-name">${item.name}</span> <span class="ingredient-quantity">${item.quantity}</span>`;
                ingredientList.appendChild(li);
            });

            const transcriptText = document.getElementById('transcript-text');
            summaryText.textContent = data.summary;
            transcriptText.textContent = data.transcript || "No spoken audio found during extraction.";
            langDetected.textContent = data.language_detected.toUpperCase();

            // Show results
            loadingSection.classList.add('hidden');
            resultsSection.classList.remove('hidden');

        } catch (error) {
            console.error('Error analyzing video:', error);
            alert('Failed to analyze video. Please check if the backend is running.');
            loadingSection.classList.add('hidden');
        }
    });
});
