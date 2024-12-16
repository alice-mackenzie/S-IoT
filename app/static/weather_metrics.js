// static/weather_metrics.js

const WeatherMetrics = (function() {
    function init() {
        const container = document.getElementById('currentWeather');
        if (!container) return;

        loadLatestWeather();
        // Update every 5 minutes
        setInterval(loadLatestWeather, 5 * 60 * 1000);
    }

    function loadLatestWeather() {
        fetch('/api/weather/hourly')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success' && data.data.length > 0) {
                    updateWeatherDisplay(data.data[data.data.length - 1]);
                }
            })
            .catch(err => console.error('Error fetching weather data:', err));
    }

    function getTemperatureColor(temp) {
        // Scale temperature from -10 to 40 degrees to 0-255
        const normalized = Math.max(0, Math.min(255, ((temp + 10) / 50) * 255));
        const red = normalized;
        const blue = 255 - normalized;
        return `rgb(${red}, 0, ${blue})`;
    }

    function updateWeatherDisplay(weatherData) {
        const container = document.getElementById('currentWeather');
        if (!container) return;

        container.innerHTML = `
            <div class="weather-card">
                <h3>Current Weather Conditions</h3>
                <div class="weather-metrics">
                    <div class="metric">
                        <span class="label">Temperature:</span>
                        <span class="value">${weatherData.Temperature.toFixed(1)}°C</span>
                    </div>
                    <div class="metric">
                        <span class="label">Humidity:</span>
                        <span class="value">${weatherData.Humidity.toFixed(1)}%</span>
                    </div>
                    <div class="metric">
                        <span class="label">Cloud Cover:</span>
                        <span class="value">${weatherData.Cloud_Cover.toFixed(1)}%</span>
                    </div>
                    <div class="metric">
                        <span class="label">Rainfall:</span>
                        <span class="value">${weatherData.Rainfall.toFixed(2)} mm</span>
                    </div>
                    <div class="temperature-viz">
                        <div class="label">Temperature Visualization</div>
                        <div class="temp-bar" style="background-color: ${getTemperatureColor(weatherData.Temperature)}"></div>
                    </div>
                </div>
            </div>
        `;
    }

    return {
        init: init
    };
})();

console.log('weather_metrics.js loaded');
