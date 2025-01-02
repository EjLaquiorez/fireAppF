const CONFIG = {
    MAP: {
        DEFAULT_ZOOM: 13,
        MAX_ZOOM: 18,
        TILE_LAYER: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        DEFAULT_LOCATION: { lat: 9.7348, lng: 118.7384 },
        COORDINATE_PRECISION: 6
    },
    APIS: {
        WEATHER: '/api/weather/',
        GEOCODING: 'https://nominatim.openstreetmap.org/reverse',
        DEBOUNCE_DELAY: 500 // ms
    },
    VALIDATION: {
        LAT_MIN: -90,
        LAT_MAX: 90,
        LNG_MIN: -180,
        LNG_MAX: 180
    }
};

// Add utility functions
const debounce = (func, delay) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
};

class LocationWeatherMap {
    constructor() {
        try {
            this.initializeElements();
            this.initializeMap();
            this.setupEventListeners();
            this.initializeData();
        } catch (error) {
            console.error('Initialization Error:', error);
            this.handleInitializationError(error);
        }
    }

    initializeElements() {
        this.elements = {
            latitude: document.getElementById('latitude'),
            longitude: document.getElementById('longitude'),
            location: document.getElementById('location'),
            locationName: document.getElementById('location_name'),
            setLocationBtn: document.getElementById('set-location-btn'),
            weatherData: document.getElementById('weather-data'),
            locationData: document.getElementById('location-data')
        };

        // Validate all elements exist
        Object.entries(this.elements).forEach(([key, element]) => {
            if (!element) {
                throw new Error(`Required element not found: ${key}`);
            }
        });
    }

    // Add coordinate validation
    validateCoordinates(lat, lng) {
        const { LAT_MIN, LAT_MAX, LNG_MIN, LNG_MAX } = CONFIG.VALIDATION;
        
        if (isNaN(lat) || lat < LAT_MIN || lat > LAT_MAX) {
            throw new Error(`Invalid latitude: ${lat}`);
        }
        if (isNaN(lng) || lng < LNG_MIN || lng > LNG_MAX) {
            throw new Error(`Invalid longitude: ${lng}`);
        }
        return true;
    }

    initializeMap() {
        // Initialize coordinates
        const lat = parseFloat(this.elements.latitude.value) || CONFIG.MAP.DEFAULT_LOCATION.lat;
        const lng = parseFloat(this.elements.longitude.value) || CONFIG.MAP.DEFAULT_LOCATION.lng;

        // Setup map
        this.map = L.map('map').setView([lat, lng], CONFIG.MAP.DEFAULT_ZOOM);
        L.tileLayer(CONFIG.MAP.TILE_LAYER, { maxZoom: CONFIG.MAP.MAX_ZOOM }).addTo(this.map);
        
        // Setup marker
        this.marker = L.marker([lat, lng], { draggable: true }).addTo(this.map);
    }

    setupEventListeners() {
        // Marker movement
        this.marker.on('moveend', (e) => {
            const position = e.target.getLatLng();
            this.updateCoordinates(position.lat, position.lng);
        });

        // Set location button
        this.elements.setLocationBtn.addEventListener('click', () => {
            this.elements.location.value = this.elements.locationName.value;
        });

        // Manual coordinate update (if exists)
        const updateMapBtn = document.getElementById('update-map');
        if (updateMapBtn) {
            updateMapBtn.addEventListener('click', () => this.handleManualUpdate());
        }
    }

    async initializeData() {
        const position = this.marker.getLatLng();
        await Promise.all([
            this.fetchWeatherData(position.lat, position.lng),
            this.getLocationName(position.lat, position.lng)
        ]);
    }

    async getLocationName(lat, lng) {
        this.elements.locationData.innerHTML = '<p>Loading location data...</p>';

        try {
            const response = await fetch(
                `${CONFIG.APIS.GEOCODING}?format=json&lat=${lat}&lon=${lng}`
            );
            if (!response.ok) throw new Error('Failed to fetch location data');
            
            const data = await response.json();
            const locationName = data.display_name || 'Unnamed Location';
            
            this.elements.locationData.innerHTML = `<p>${locationName}</p>`;
            this.elements.locationName.value = locationName;
        } catch (error) {
            console.error('Location Data Error:', error);
            this.elements.locationData.innerHTML = 
                '<p class="text-danger">Unable to load location data</p>';
        }
    }

    async fetchWeatherData(lat, lng) {
        this.elements.weatherData.innerHTML = '<p>Loading weather data...</p>';

        try {
            const response = await fetch(
                `${CONFIG.APIS.WEATHER}?lat=${lat}&lon=${lng}`
            );
            if (!response.ok) throw new Error('Failed to fetch weather data');
            
            const data = await response.json();
            this.updateWeatherDisplay(data);
            this.updateWeatherFields(data);
        } catch (error) {
            console.error('Weather Data Error:', error);
            this.elements.weatherData.innerHTML = 
                '<p class="text-danger">Unable to load weather data. Please try again later.</p>';
        }
    }

    updateWeatherDisplay(data) {
        this.elements.weatherData.innerHTML = `
            <p><strong>Temperature:</strong> ${data.temperature}°C</p>
            <p><strong>Humidity:</strong> ${data.humidity}%</p>
            <p><strong>Wind Speed:</strong> ${data.wind_speed} m/s</p>
            <p><strong>Conditions:</strong> ${data.conditions}</p>
        `;
    }

    updateWeatherFields(data) {
        document.getElementById('temperature').value = data.temperature;
        document.getElementById('humidity').value = data.humidity;
        document.getElementById('wind_speed').value = data.wind_speed;
        document.getElementById('weather_conditions').value = data.conditions;
    }

    updateCoordinates(lat, lng) {
        try {
            this.validateCoordinates(lat, lng);
            this.elements.latitude.value = lat.toFixed(CONFIG.MAP.COORDINATE_PRECISION);
            this.elements.longitude.value = lng.toFixed(CONFIG.MAP.COORDINATE_PRECISION);
            
            // Debounce API calls
            this.debouncedFetchWeather(lat, lng);
            this.debouncedFetchLocation(lat, lng);
        } catch (error) {
            console.error('Coordinate Update Error:', error);
            this.showError('Invalid coordinates provided');
        }
    }

    handleManualUpdate() {
        const manualLat = parseFloat(document.getElementById('manual-lat').value);
        const manualLng = parseFloat(document.getElementById('manual-lng').value);

        if (!isNaN(manualLat) && !isNaN(manualLng)) {
            this.marker.setLatLng([manualLat, manualLng]);
            this.map.setView([manualLat, manualLng], CONFIG.MAP.DEFAULT_ZOOM);
            this.updateCoordinates(manualLat, manualLng);
        }
    }

    // Add error handling methods
    showError(message) {
        const errorHtml = `<p class="text-danger">${message}</p>`;
        this.elements.weatherData.innerHTML = errorHtml;
        this.elements.locationData.innerHTML = errorHtml;
    }

    handleInitializationError(error) {
        const mapContainer = document.getElementById('map');
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div class="alert alert-danger">
                    Failed to initialize map: ${error.message}
                </div>
            `;
        }
    }

    constructor() {
        this.debouncedFetchWeather = debounce(
            this.fetchWeatherData.bind(this),
            CONFIG.APIS.DEBOUNCE_DELAY
        );
        this.debouncedFetchLocation = debounce(
            this.getLocationName.bind(this),
            CONFIG.APIS.DEBOUNCE_DELAY
        );
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.locationWeatherMap = new LocationWeatherMap();
});
  