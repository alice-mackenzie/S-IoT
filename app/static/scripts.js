// scripts.js
console.log('scripts.js loaded');
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded - initializing charts');
    
    // Initialize weather charts
    if (typeof weatherCharts !== 'undefined') {
        console.log('Weather charts module found, initializing');
        weatherCharts.init();
    } else {
        console.error('Weather charts module not found');
    }

    // Initialize weather metrics
    if (typeof WeatherMetrics !== 'undefined') {
        WeatherMetrics.init();
    }

    
    // Initialize moth charts
    if (typeof mothCharts !== 'undefined') {
        console.log('Moth charts module found, initializing');
        mothCharts.init();
    } else {
        console.error('Moth charts module not found');
    }

    if (typeof lastNightMoths !== 'undefined') {
        console.log('Last night moths module found, initializing');
        lastNightMoths.init();
    } else {
        console.error('Last night moths module not found');
    }

    if (typeof departureCharts !== 'undefined') {
        console.log('Departure charts module found, initializing');
        departureCharts.init();
    } else {
        console.error('Departure charts module not found');
    }

    // Add light controls initialization
    if (typeof lightControls !== 'undefined') {
        console.log('Light controls module found, initializing');
        lightControls.init();
    }
});

// Function to update weather data
function updateWeatherData() {
    const weatherContainer = document.getElementById('currentWeather');
    if (weatherContainer && weatherData) {
        // Get the most recent weather reading
    }
}

// Function to update moth data
function updateMothData(data) {
    const mothContainer = document.getElementById('mothActivity');
    if (mothContainer && data) {
        // We'll add moth data display logic here
    }
}

// Function to update correlation analysis
function updateCorrelationData(weatherData, mothData) {
    const correlationContainer = document.getElementById('correlationData');
    if (correlationContainer && weatherData && mothData) {
        // We'll add correlation analysis logic here
    }
}

// Modular initialization for weather
function initializeWeatherChart() {
    if (typeof weatherCharts !== 'undefined') {
        weatherCharts.init();
    }
}

// Modular initialization for moths
function initializeMothChart() {
    if (typeof mothCharts !== 'undefined') {
        mothCharts.init();
    }
}


const lightControls = (function() {
    function init() {
        console.log('Light controls init called');
        setupEventListeners();
    }

    function setupEventListeners() {
        const warmLightBtn = document.getElementById('warmLightBtn');
        const turnOffLightBtn = document.getElementById('turnOffLightBtn');

        console.log('Warm light button found:', !!warmLightBtn);
        console.log('Turn off button found:', !!turnOffLightBtn);

        if (warmLightBtn) {
            warmLightBtn.addEventListener('click', async () => {
                console.log('Warm light button clicked');
                try {
                    await toggleLight('warm');
                } catch (error) {
                    console.error('Error in warm light click handler:', error);
                }
            });
        }

        if (turnOffLightBtn) {
            turnOffLightBtn.addEventListener('click', async () => {
                console.log('Turn off button clicked');
                try {
                    await toggleLight('off');
                } catch (error) {
                    console.error('Error in turn off click handler:', error);
                }
            });
        }
    }

    async function toggleLight(mode) {
        const button = mode === 'warm' ? 
            document.getElementById('warmLightBtn') : 
            document.getElementById('turnOffLightBtn');
        
        console.log(`Attempting to ${mode} light`);
        
        try {
            button.disabled = true;
            console.log(`Sending request to /api/lights/${mode}`);
            
            const response = await fetch(`/api/lights/${mode}`);
            console.log('Response received:', response.status);
            
            const data = await response.json();
            console.log('Response data:', data);
            
            if (data.status === 'error') {
                console.error(`Error controlling lights: ${data.message}`);
                alert(`Failed to control lights: ${data.message}`);
            } else {
                console.log(`Successfully ${mode === 'warm' ? 'turned on' : 'turned off'} lights`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert(`Failed to control lights: ${error.message}`);
        } finally {
            button.disabled = false;
        }
    }

    return {
        init: init
    };
})();
