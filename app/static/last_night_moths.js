// last_night_moths.js
const lastNightMoths = (function() {
    let mothData = null;
    let weatherData = null;

    function init() {
        console.log('LastNightMoths: Initializing module');
        const container = document.getElementById('mothActivity');
        if (!container) {
            console.error('LastNightMoths: Container #mothActivity not found');
            return;
        }
        
        // Show loading state
        container.innerHTML = `
            <div class="p-4 bg-white rounded-lg shadow">
                <div class="animate-pulse grid grid-cols-2 gap-4">
                    <div>
                        <div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                        <div class="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
                    </div>
                    <div>
                        <div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                        <div class="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
                    </div>
                </div>
            </div>
        `;
        
        loadData();
    }

    function loadData() {
        console.log('LastNightMoths: Starting data fetch');
        
        Promise.all([
            fetch('/api/moths/daily')
                .then(res => res.json())
                .catch(error => {
                    console.error('LastNightMoths: Moths API error:', error);
                    return { status: 'error', error: 'Failed to load moth data' };
                }),
            fetch('/api/weather/hourly')
                .then(res => res.json())
                .catch(error => {
                    console.error('LastNightMoths: Weather API error:', error);
                    return { status: 'error', error: 'Failed to load weather data' };
                })
        ])
        .then(([mothResult, weatherResult]) => {
            if (mothResult.status !== 'success' || !mothResult.data || mothResult.data.length === 0) {
                throw new Error('No moth data available');
            }

            if (weatherResult.status !== 'success' || !weatherResult.data || weatherResult.data.length === 0) {
                throw new Error('No weather data available');
            }

            mothData = mothResult.data[mothResult.data.length - 1];
            weatherData = weatherResult.data[weatherResult.data.length - 1];
            
            if (!isValidMothData(mothData)) {
                throw new Error('Invalid moth data structure');
            }

            updateDisplay();
        })
        .catch(error => {
            console.error('LastNightMoths: Error:', error);
            showErrorState(error.message);
        });
    }

    function isValidMothData(data) {
        return data && 
               typeof data === 'object' &&
               data.morning && 
               data.afternoon &&
               typeof data.morning.mini !== 'undefined' &&
               typeof data.morning.medium !== 'undefined' &&
               typeof data.morning.large !== 'undefined' &&
               typeof data.afternoon.mini !== 'undefined' &&
               typeof data.afternoon.medium !== 'undefined' &&
               typeof data.afternoon.large !== 'undefined';
    }

    function getTemperatureColor(temp) {
        if (!temp || isNaN(temp)) return '#808080';
        if (temp <= 0) return '#00ffff';
        if (temp <= 10) return '#00bfff';
        if (temp <= 20) return '#ffa500';
        return '#ff4500';
    }

    function createTimeSection(title, data, tempColor) {
        const total = (data.mini || 0) + (data.medium || 0) + (data.large || 0);
        
        return `
            <div class="p-4">
                <h3 class="text-lg font-semibold mb-4">${title}</h3>
                <div class="space-y-4">
                    <div class="flex items-baseline gap-2">
                        <span class="text-base font-medium">Total:</span>
                        <span class="text-2xl font-bold" style="color: ${tempColor}">
                            ${total}
                        </span>
                    </div>

                    <div class="grid grid-cols-3 gap-2">
                        <div class="text-center p-2 bg-gray-50 rounded">
                            <div class="text-sm text-gray-600">Mini</div>
                            <div class="text-lg font-semibold">
                                ${data.mini || 0}
                            </div>
                        </div>
                        <div class="text-center p-2 bg-gray-50 rounded">
                            <div class="text-sm text-gray-600">Medium</div>
                            <div class="text-lg font-semibold">
                                ${data.medium || 0}
                            </div>
                        </div>
                        <div class="text-center p-2 bg-gray-50 rounded">
                            <div class="text-sm text-gray-600">Large</div>
                            <div class="text-lg font-semibold">
                                ${data.large || 0}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function showErrorState(message) {
        const container = document.getElementById('mothActivity');
        if (container) {
            container.innerHTML = `
                <div class="p-4 bg-white rounded-lg shadow">
                    <div class="text-center">
                        <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <h3 class="mt-2 text-lg font-medium text-gray-900">No Data Available</h3>
                        <p class="mt-1 text-sm text-gray-500">${message || 'Could not load moth activity data'}</p>
                        <button onclick="lastNightMoths.loadData()" class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                            Try Again
                        </button>
                    </div>
                </div>
            `;
        }
    }

    function updateDisplay() {
        const container = document.getElementById('mothActivity');
        if (!container || !mothData || !weatherData) {
            showErrorState();
            return;
        }

        const tempColor = getTemperatureColor(weatherData.Temperature);

        const html = `
            <div class="bg-white rounded-lg shadow">
                <div class="border-b border-gray-200 px-4 py-3">
                    <h2 class="text-xl font-semibold">Yesterday's Moths</h2>
                </div>
                <div class="grid grid-cols-2 divide-x">
                    ${createTimeSection('Dawn', mothData.morning, tempColor)}
                    ${createTimeSection('Dusk', mothData.afternoon, tempColor)}
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    return {
        init: init,
        loadData: loadData
    };
})();

console.log('last_night_moths.js loaded');
