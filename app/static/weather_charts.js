const weatherCharts = (function () {
    let weatherChart = null;
    let weatherData = null;  // Store data to prevent multiple loads

    function init() {
        const ctx = document.getElementById('weatherChart');
        if (!ctx) {
            console.error('Weather chart container not found');
            return;
        }

        if (!weatherData) {
            loadWeatherData();
        } else {
            updateChart();
        }
    }

    function calculateRainfallRange(rainfallData) {
        const maxRainfall = Math.max(...rainfallData);
        return [0, Math.ceil(maxRainfall * 5) / 5 + 0.2];
    }

    function createChart(data) {
        const rainfallData = data.map(d => d.Rainfall);
        const rainfallRange = calculateRainfallRange(rainfallData);

        const traces = [
            {
                name: 'Temperature (°C)',
                x: data.map(d => new Date(d.Timestamp)),
                y: data.map(d => d.Temperature),
                type: 'scatter',
                mode: 'lines',
                line: { color: 'rgb(255, 99, 132)' },
                yaxis: 'y'
            },
            {
                name: 'Humidity (%)',
                x: data.map(d => new Date(d.Timestamp)),
                y: data.map(d => d.Humidity),
                type: 'scatter',
                mode: 'lines',
                line: { color: 'rgb(54, 162, 235)' },
                yaxis: 'y2'
            },
            {
                name: 'Cloud Cover (%)',
                x: data.map(d => new Date(d.Timestamp)),
                y: data.map(d => d.Cloud_Cover),
                type: 'scatter',
                mode: 'lines',
                line: { color: 'rgb(75, 192, 192)' },
                yaxis: 'y2'
            },
            {
                name: 'Rainfall (mm)',
                x: data.map(d => new Date(d.Timestamp)),
                y: rainfallData,
                type: 'scatter',
                mode: 'lines',
                line: { color: 'rgb(153, 102, 255)' },
                yaxis: 'y3'
            }
        ];

        const layout = {
            title: 'Weather Data',
            showlegend: true,
            width: null,
            height: 450,
            margin: {
                l: 50,
                r: 100,
                t: 30,
                b: 50
            },
            xaxis: {
                title: 'Time',
                type: 'date',
                showgrid: true,
                gridcolor: '#f0f0f0'
            },
            yaxis: {
                title: 'Temperature (°C)',
                range: [-1, 20],
                side: 'left',
                showgrid: true,
                gridcolor: 'rgba(255, 99, 132, 0.2)'
            },
            yaxis2: {
                title: 'Percentage (%)',
                range: [0, 100],
                side: 'right',
                overlaying: 'y',
                showgrid: false,
                zeroline: false
            },
            yaxis3: {
                title: 'Rainfall (mm)',
                range: rainfallRange,
                side: 'right',
                overlaying: 'y',
                showgrid: false,
                zeroline: false,
                anchor: 'free',
                position: 0.85
            },
            legend: {
                orientation: 'h',
                yanchor: 'bottom',
                y: -0.3,
                xanchor: 'center',
                x: 0.5
            }
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        return Plotly.newPlot('weatherChart', traces, layout, config);
    }

    function loadWeatherData() {
        fetch('/api/weather/hourly')
            .then(response => response.json())
            .then(result => {
                if (result.status === 'success' && result.data && result.data.length > 0) {
                    weatherData = result.data;  // Store the data
                    createChart(weatherData);
                    createMetricToggles();
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function updateChart() {
        if (weatherData) {
            createChart(weatherData);
            createMetricToggles();
        }
    }

    function createMetricToggles() {
        const existingToggles = document.querySelector('.metric-toggles');
        if (existingToggles) {
            existingToggles.remove();
        }

        const toggleContainer = document.createElement('div');
        toggleContainer.className = 'metric-toggles';

        const metrics = [
            { id: 'temp', label: 'Temperature', checked: true },
            { id: 'humidity', label: 'Humidity', checked: true },
            { id: 'clouds', label: 'Cloud Cover', checked: true },
            { id: 'rain', label: 'Rainfall', checked: true }
        ];

        metrics.forEach((metric, index) => {
            const label = document.createElement('label');
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = metric.id;
            checkbox.checked = metric.checked;
            checkbox.addEventListener('change', () => {
                const update = { visible: checkbox.checked };
                Plotly.restyle('weatherChart', update, [index]);
            });

            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(` ${metric.label}`));
            toggleContainer.appendChild(label);
        });

        const chartContainer = document.querySelector('.chart-container');
        if (chartContainer) {
            chartContainer.appendChild(toggleContainer);
        }
    }

    return {
        init: init
    };
})();

