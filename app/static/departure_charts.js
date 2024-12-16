// departure_charts.js

const departureCharts = (function () {
    let departureData = null;
    let currentView = 'time'; // 'time' or 'temperature'
    let togglesInitialized = false;
    
    function init() {
        console.log('Departure charts init called');
        if (!departureData) {
            loadDepartureData();
        } else {
            updateChart();
        }
        if (!togglesInitialized) {
            setupToggleControls();
            togglesInitialized = true;
        }
    }
    
function loadDepartureData() {
    // Show loading state
    const chartContainer = document.getElementById('departureChart');
    if (chartContainer) {
        chartContainer.innerHTML = '<div class="loading">Loading departure data...</div>';
    }

    fetch('/api/moths/departures')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(result => {
            if (result.status === 'success' && result.data) {
                departureData = result.data;
                createChart();
                updateStats();
            } else {
                throw new Error('Invalid data format received');
            }
        })
        .catch(error => {
            console.error('Error loading departure data:', error);
            if (chartContainer) {
                chartContainer.innerHTML = `
                    <div class="error-message">
                        <p>Error loading departure data. Please try again later.</p>
                        <button onclick="departureCharts.init()">Retry</button>
                    </div>
                `;
            }
        });
}
    
    function setupToggleControls() {
        const existingToggles = document.querySelector('.view-toggles');
        if (existingToggles) {
            existingToggles.remove();
        }
        
        const controlsContainer = document.createElement('div');
        controlsContainer.className = 'view-toggles';
        
        const views = [
            { id: 'time', label: 'Time Distribution' },
            { id: 'temperature', label: 'Temperature Analysis' }
        ];
        
        views.forEach(view => {
            const button = document.createElement('button');
            button.textContent = view.label;
            button.className = currentView === view.id ? 'active' : '';
            button.onclick = () => switchView(view.id);
            controlsContainer.appendChild(button);
        });
        
        const chartContainer = document.getElementById('departureChart');
        if (chartContainer) {
            chartContainer.parentElement.insertBefore(controlsContainer, chartContainer);
        }
    }
    
    function switchView(view) {
        currentView = view;
        document.querySelectorAll('.view-toggles button').forEach(btn => {
            btn.className = btn.textContent.toLowerCase().includes(view) ? 'active' : '';
        });
        updateChart();
    }
    
    function createTimeDistributionChart() {
        const data = departureData.time_distribution;
        const smoothedCounts = movingAverage(data.counts, 3);
        
        const trace = {
            x: data.times,
            y: smoothedCounts,
            type: 'scatter',
            mode: 'lines',
            fill: 'tozeroy',
            line: {
                color: 'rgb(75, 192, 192)',
                shape: 'spline',
                width: 2
            },
            name: 'Departure Distribution'
        };
        
        const layout = {
            title: 'Time to Departure Distribution',
            xaxis: {
                title: 'Minutes After Red Light Activation',
                tickmode: 'auto',
                nticks: 10
            },
            yaxis: {
                title: 'Number of Moths',
                rangemode: 'tozero'
            },
            showlegend: false
        };
        
        return Plotly.newPlot('departureChart', [trace], layout);
    }
    
    function createTemperatureChart() {
        const data = departureData.temperature_analysis;
        
        const trace = {
            x: data.ranges,
            y: data.avg_times,
            type: 'bar',
            marker: {
                color: data.avg_times,
                colorscale: 'Viridis'
            },
            text: data.counts.map(count => `${count} moths`),
            hovertemplate: 
                'Temperature: %{x}<br>' +
                'Average Departure Time: %{y:.1f} min<br>' +
                'Sample Size: %{text}<br>' +
                '<extra></extra>'
        };
        
        const layout = {
            title: 'Average Departure Time by Light Temperature',
            xaxis: {
                title: 'Temperature Range (°C)',
                tickangle: -45
            },
            yaxis: {
                title: 'Average Time to Departure (minutes)',
                rangemode: 'tozero'
            },
            showlegend: false
        };
        
        return Plotly.newPlot('departureChart', [trace], layout);
    }
    
    function movingAverage(arr, window) {
        const result = [];
        for (let i = 0; i < arr.length; i++) {
            let sum = 0;
            let count = 0;
            for (let j = Math.max(0, i - window); j <= Math.min(arr.length - 1, i + window); j++) {
                sum += arr[j];
                count++;
            }
            result.push(sum / count);
        }
        return result;
    }
    
    function updateStats() {
        const stats = departureData.stats;
        const statsContainer = document.createElement('div');
        statsContainer.className = 'departure-stats';
        statsContainer.innerHTML = `
            <h3>Summary Statistics</h3>
            <p>Total Moths: ${stats.total_moths}</p>
            <p>Average Departure Time: ${stats.avg_departure_time.toFixed(1)} minutes</p>
            <p>Temperature Correlation: ${stats.temp_correlation.toFixed(3)}</p>
        `;
        
        const chartContainer = document.getElementById('departureChart');
        if (chartContainer && chartContainer.parentElement) {
            const existingStats = document.querySelector('.departure-stats');
            if (existingStats) {
                existingStats.remove();
            }
            chartContainer.parentElement.appendChild(statsContainer);
        }
    }
    
    function updateChart() {
        if (!departureData) return;
        
        if (currentView === 'time') {
            createTimeDistributionChart();
        } else {
            createTemperatureChart();
        }
    }
    
    return {
        init: init
    };
})();

console.log('departure_charts.js loaded');
