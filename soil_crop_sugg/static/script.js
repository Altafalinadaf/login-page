document.addEventListener('DOMContentLoaded', function() {
    // Load soil types when page loads
    fetch('/get_soil_types')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('soilType');
            select.innerHTML = '<option value="">Select Soil Type</option>';
            data.forEach(soil => {
                const option = document.createElement('option');
                option.value = soil.id;
                option.textContent = soil.name;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading soil types:', error);
            document.getElementById('soilType').innerHTML = '<option value="">Error loading soil types</option>';
        });
    
    // Handle form submission
    document.getElementById('soilForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const soilTypeId = document.getElementById('soilType').value;
        const phLevel = document.getElementById('phLevel').value;
        const nitrogen = document.getElementById('nitrogen').value;
        const phosphorus = document.getElementById('phosphorus').value;
        const potassium = document.getElementById('potassium').value;
        
        // Validate inputs
        if (!soilTypeId || !phLevel || !nitrogen || !phosphorus || !potassium) {
            alert('Please fill all fields');
            return;
        }
        
        // Show loading state
        const submitBtn = document.querySelector('#soilForm button');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
        
        fetch('/get_crop_recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                soil_type_id: soilTypeId,
                ph: phLevel,
                nitrogen: nitrogen,
                phosphorus: phosphorus,
                potassium: potassium
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            displayRecommendations(data);
        })
        .catch(error => {
            console.error('Error getting recommendations:', error);
            alert('Error getting recommendations. Please try again.');
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Get Recommendations';
        });
    });
    
    function displayRecommendations(recommendations) {
        const container = document.getElementById('recommendations');
        container.innerHTML = '';
        
        if (!recommendations || recommendations.length === 0) {
            container.innerHTML = '<div class="crop-card"><p>No suitable crops found for the given soil properties.</p></div>';
        } else {
            recommendations.forEach((crop, index) => {
                const card = document.createElement('div');
                card.className = `crop-card ${index === 0 ? 'best-match' : ''}`;
                
                // Create status indicators
                const phStatusClass = crop.ph_compatibility === 'Good' ? 'good' : 'warning';
                const nitrogenStatusClass = getStatusClass(crop.nitrogen_status);
                const phosphorusStatusClass = getStatusClass(crop.phosphorus_status);
                const potassiumStatusClass = getStatusClass(crop.potassium_status);
                
                card.innerHTML = `
                    <h3>${crop.crop_name}</h3>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: ${crop.score}%">
                            <span class="progress-text">${Math.round(crop.score)}% Match</span>
                        </div>
                    </div>
                    <div class="crop-details">
                        <div class="detail-row">
                            <span class="detail-label">Optimal pH Range:</span>
                            <span class="detail-value">${crop.ph_range}</span>
                            <span class="detail-status ${phStatusClass}">${crop.ph_compatibility}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Nitrogen Needs:</span>
                            <span class="detail-value">${crop.nitrogen_needs}</span>
                            <span class="detail-status ${nitrogenStatusClass}">${crop.nitrogen_status}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Phosphorus Needs:</span>
                            <span class="detail-value">${crop.phosphorus_needs}</span>
                            <span class="detail-status ${phosphorusStatusClass}">${crop.phosphorus_status}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Potassium Needs:</span>
                            <span class="detail-value">${crop.potassium_needs}</span>
                            <span class="detail-status ${potassiumStatusClass}">${crop.potassium_status}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Water Requirements:</span>
                            <span class="detail-value">${crop.water_requirements}</span>
                            <span class="detail-status neutral">-</span>
                        </div>
                    </div>
                `;
                
                container.appendChild(card);
            });
        }
        
        document.getElementById('results').classList.remove('hidden');
        window.scrollTo({
            top: document.getElementById('results').offsetTop - 20,
            behavior: 'smooth'
        });
    }
    
    function getStatusClass(statusText) {
        if (statusText.includes('Ideal')) return 'good';
        if (statusText.includes('excessive') || statusText.includes('deficient')) return 'bad';
        if (statusText.includes('Adequate')) return 'neutral';
        return 'warning';
    }
});