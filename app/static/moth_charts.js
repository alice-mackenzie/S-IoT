const mothCharts = (function () {
    let mothData = null;
    let moonData = null;
    let weatherData = null;
    let visibilitySettings = {
        moon: true,
        temperature: false,
        humidity: false,
        cloudCover: false
    };

    function init() {
        if (!mothData || !moonData || !weatherData) {
            loadAllData();
        } else {
            updateChart();
        }
        setupToggleControls();
    }

    function loadAllData() {
        Promise.all([
            fetch('/api/moths/daily').then(response => response.json()),
            fetch('/api/moon/monthly').then(response => response.json()),
            fetch('/api/weather/hourly').then(response => response.json())
        ])
        .then(([mothResult, moonResult, weatherResult]) => {
            if (mothResult.status === 'success' && 
                moonResult.status === 'success' && 
                weatherResult.status === 'success') {
                
                mothData = mothResult.data;
                moonData = moonResult.data;
                weatherData = processWeatherData(weatherResult.data);
                createChart();
            }
        })
        .catch(error => console.error('Error loading data:', error));
    }

    function processWeatherData(rawData) {
        const dailyData = {};
        
        rawData.forEach(record => {
            const date = record.Timestamp.split(' ')[0];
            if (!dailyData[date]) {
                dailyData[date] = {
                    temperature: [],
                    humidity: [],
                    cloudCover: []
                };
            }
            
            dailyData[date].temperature.push(record.Temperature);
            dailyData[date].humidity.push(record.Humidity);
            dailyData[date].cloudCover.push(record.Cloud_Cover);
        });

        Object.keys(dailyData).forEach(date => {
            dailyData[date] = {
                temperature: calculateAverage(dailyData[date].temperature),
                humidity: calculateAverage(dailyData[date].humidity),
                cloudCover: calculateAverage(dailyData[date].cloudCover)
            };
        });

        return dailyData;
    }

    function calculateAverage(arr) {
        return arr.reduce((a, b) => a + b, 0) / arr.length;
    }

    function setupToggleControls() {
        const controlsContainer = document.createElement('div');
        controlsContainer.className = 'metric-toggles';

        const toggles = [
            { id: 'moon', label: 'Moon Phase' },
            { id: 'temperature', label: 'Temperature' },
            { id: 'humidity', label: 'Humidity' },
            { id: 'cloudCover', label: 'Cloud Cover' }
        ];

        toggles.forEach(toggle => {
            const label = document.createElement('label');
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `toggle-${toggle.id}`;
            checkbox.checked = visibilitySettings[toggle.id];
            checkbox.addEventListener('change', (e) => {
                visibilitySettings[toggle.id] = e.target.checked;
                updateChart();
            });

            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(` ${toggle.label}`));
            controlsContainer.appendChild(label);
        });

        const chartContainer = document.getElementById('mothsChart');
        if (chartContainer) {
            chartContainer.parentElement.appendChild(controlsContainer);
        }
    }

function createChart() {
    const dates = mothData.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric'
        });
    });

    const traces = [];

    dates.forEach((date, i) => {
        // Dawn Bars - all share same offsetgroup 'dawn' but unique stackgroup per date
        traces.push({
            name: 'Dawn - Mini',
            x: [date],
            y: [mothData[i].morning.mini],
            type: 'bar',
            marker: { color: 'rgba(255, 205, 86, 1)' },
            showlegend: i === 0,
            legendgroup: 'Dawn Mini',
            offsetgroup: 'dawn',
            stackgroup: `dawn-${date}`, // Unique stack group per date
            width: 0.4
        });

        traces.push({
            name: 'Dawn - Medium',
            x: [date],
            y: [mothData[i].morning.medium],
            type: 'bar',
            marker: { color: 'rgba(255, 159, 64, 1)' },
            showlegend: i === 0,
            legendgroup: 'Dawn Medium',
            offsetgroup: 'dawn',
            stackgroup: `dawn-${date}`, // Same stack group as dawn mini for this date
            width: 0.4
        });

        traces.push({
            name: 'Dawn - Large',
            x: [date],
            y: [mothData[i].morning.large],
            type: 'bar',
            marker: { color: 'rgba(255, 99, 132, 1)' },
            showlegend: i === 0,
            legendgroup: 'Dawn Large',
            offsetgroup: 'dawn',
            stackgroup: `dawn-${date}`, // Same stack group as other dawn bars for this date
            width: 0.4
        });

        // Dusk Bars - all share same offsetgroup 'dusk' but unique stackgroup per date
        traces.push({
            name: 'Dusk - Mini',
            x: [date],
            y: [mothData[i].afternoon.mini],
            type: 'bar',
            marker: { color: 'rgba(153, 102, 255, 1)' },
            showlegend: i === 0,
            legendgroup: 'Dusk Mini',
            offsetgroup: 'dusk',
            stackgroup: `dusk-${date}`, // Unique stack group per date
            width: 0.4
        });

        traces.push({
            name: 'Dusk - Medium',
            x: [date],
            y: [mothData[i].afternoon.medium],
            type: 'bar',
            marker: { color: 'rgba(54, 162, 235, 1)' },
            showlegend: i === 0,
            legendgroup: 'Dusk Medium',
            offsetgroup: 'dusk',
            stackgroup: `dusk-${date}`, // Same stack group as dusk mini for this date
            width: 0.4
        });

        traces.push({
            name: 'Dusk - Large',
            x: [date],
            y: [mothData[i].afternoon.large],
            type: 'bar',
            marker: { color: 'rgba(75, 192, 192, 1)' },
            showlegend: i === 0,
            legendgroup: 'Dusk Large',
            offsetgroup: 'dusk',
            stackgroup: `dusk-${date}`, // Same stack group as other dusk bars for this date
            width: 0.4
        });
    });
    // Add weather and moon overlays if enabled
    if (visibilitySettings.moon) {
        traces.push({
            name: 'Moon Phase',
            x: dates,
            y: moonData.map(d => d['Moon Phase (%)']),
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: 'rgba(255, 206, 86, 1)', width: 2 },
            marker: { size: 6 },
            yaxis: 'y2'
        });
    }

    // Add other weather metrics if enabled
    if (visibilitySettings.temperature || visibilitySettings.humidity || visibilitySettings.cloudCover) {
        const weatherMetrics = [];
        if (visibilitySettings.temperature) {
            weatherMetrics.push({
                name: 'Temperature (°C)',
                color: 'rgba(255, 99, 132, 1)',
                values: dates.map(date => weatherData[date]?.temperature)
            });
        }
        if (visibilitySettings.humidity) {
            weatherMetrics.push({
                name: 'Humidity (%)',
                color: 'rgba(54, 162, 235, 1)',
                values: dates.map(date => weatherData[date]?.humidity)
            });
        }
        if (visibilitySettings.cloudCover) {
            weatherMetrics.push({
                name: 'Cloud Cover (%)',
                color: 'rgba(75, 192, 192, 1)',
                values: dates.map(date => weatherData[date]?.cloudCover)
            });
        }

        weatherMetrics.forEach(metric => {
            traces.push({
                name: metric.name,
                x: dates,
                y: metric.values,
                type: 'scatter',
                mode: 'lines',
                line: { color: metric.color },
                yaxis: 'y3'
            });
        });
    }

    const layout = {
        title: 'Moth Activity at Dawn and Dusk',
        xaxis: {
            title: 'Date',
            tickangle: -45
        },
        yaxis: {
            title: 'Number of Moths',
            side: 'left'
        },
        yaxis2: {
            title: 'Moon Phase (%)',
            side: 'right',
            overlaying: 'y',
            range: [0, 100],
            tickfont: {color: 'rgba(255, 206, 86, 1)'},
            titlefont: {color: 'rgba(255, 206, 86, 1)'}
        },
        yaxis3: {
            title: 'Weather Metrics',
            side: 'right',
            overlaying: 'y',
            position: 0.85,
            tickfont: {color: 'rgba(75, 192, 192, 1)'},
            titlefont: {color: 'rgba(75, 192, 192, 1)'}
        },
        legend: {
            orientation: 'h',
            y: -0.2,
            x: 0.5,
            xanchor: 'center'
        },
        margin: {
            l: 50,
            r: 50,
            t: 50,
            b: 100
        },
        showlegend: true,
        hovermode: 'closest',
        bargap: 0.2,
        bargroupgap: 0.1
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
        Plotly.newPlot('mothsChart', traces, layout, config);
    }

    function updateChart() {
        if (mothData && moonData && weatherData) {
            createChart();
        }
    }

    return {
        init: init
    };
})();

console.log('moth_charts.js loaded');
