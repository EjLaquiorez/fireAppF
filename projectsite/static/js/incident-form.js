// Configuration
const CONFIG = {
    MAP: {
        DEFAULT_ZOOM: 13,
        MAX_ZOOM: 18,
        DEFAULT_LAT: 0,
        DEFAULT_LNG: 0,
        TILE_LAYER: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    },
    WEATHER_API: '/api/weather/',
    DECIMAL_PLACES: 6
};

class IncidentForm {
    constructor() {
        this.initializeForm();
        this.initializeMap();
        this.setupEventListeners();
    }

    initializeForm() {
        // Form validation
        const statusSelect = document.querySelector('select[name="status"]');
        if (statusSelect) {
            Array.from(statusSelect.options)
                .filter(option => !['Active', 'Resolve'].includes(option.value))
                .forEach(option => option.remove());
        }

        const descriptionField = document.querySelector('textarea[name="description"]');
        if (descriptionField) {
            descriptionField.maxLength = 1000;
            descriptionField.addEventListener('input', this.validateDescription.bind(this));
        }
    }

    initializeMap() {
        try {
            const latField = document.getElementById('latitude');
            const lngField = document.getElementById('longitude');
            const lat = parseFloat(latField.dataset.default) || CONFIG.MAP.DEFAULT_LAT;
            const lng = parseFloat(lngField.dataset.default) || CONFIG.MAP.DEFAULT_LNG;

            this.map = L.map('map').setView([lat, lng], CONFIG.MAP.DEFAULT_ZOOM);
            
            L.tileLayer(CONFIG.MAP.TILE_LAYER, {
                maxZoom: CONFIG.MAP.MAX_ZOOM,
            }).addTo(this.map);

            this.marker = L.marker([lat, lng], { draggable: true }).addTo(this.map);
            
            if (lat !== CONFIG.MAP.DEFAULT_LAT && lng !== CONFIG.MAP.DEFAULT_LNG) {
                this.fetchWeatherData(lat, lng);
            }
        } catch (error) {
            console.error('Map initialization failed:', error);
            document.getElementById('map').innerHTML = 
                '<div class="alert alert-danger">Failed to load map. Please refresh the page.</div>';
        }
    }

    async fetchWeatherData(lat, lng) {
        const weatherDataEl = document.getElementById('weather-data');
        weatherDataEl.innerHTML = `
            <div class="loading-spinner"></div>
            <p class="loading-text">Loading weather data...</p>
        `;

        try {
            const response = await fetch(
                `${CONFIG.WEATHER_API}?lat=${lat}&lon=${lng}`
            );
            if (!response.ok) throw new Error('Weather API request failed');
            
            const data = await response.json();
            this.updateWeatherDisplay(data);
            this.updateHiddenFields(data);
        } catch (error) {
            console.error('Weather Data Error:', error);
            weatherDataEl.innerHTML = `
                <div class="alert alert-danger">
                    Unable to load weather data. Please try again later.
                    <button type="button" class="btn btn-sm btn-outline-danger mt-2" 
                            onclick="window.incidentForm.retryWeatherFetch()">
                        Retry
                    </button>
                </div>
            `;
        }
    }

    // ... additional methods ...
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.incidentForm = new IncidentForm();
});