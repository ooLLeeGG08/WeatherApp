from flask import Flask, request, jsonify
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta

app = Flask(__name__)


class WeatherService:
    def __init__(self):
        self.api_key = "a346177658d2c23e6d305f654816e360"

    def get_weather(self, city):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}"

        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data["cod"] == 200:
                        return self.format_weather_data(data)
                    else:
                        return {"error": "City not found. Please check your input."}
                else:
                    return {"error": f"HTTP Error {response.status}. Please try again later."}

        except urllib.error.HTTPError as e:
            if 400 <= e.code <= 404:
                return {"error": "City not found. Please check your input."}
            elif e.code == 500:
                return {"error": "Internal Server Error. Please try again later."}
            elif e.code == 502:
                return {"error": "Bad Gateway. Please try again later."}
            elif e.code == 503:
                return {"error": "Service Unavailable. Please try again later."}
            else:
                return {"error": f"HTTP error {e.code}. Please try again later."}

        except urllib.error.URLError as e:
            return {"error": "Connection Error. Check your internet connection."}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    def get_forecast(self, city):
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.api_key}"

        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data["cod"] == "200":
                        return self.format_forecast_data(data)
                    else:
                        return {"error": "City not found. Please check your input."}
                else:
                    return {"error": f"HTTP Error {response.status}. Please try again later."}

        except urllib.error.HTTPError as e:
            if 400 <= e.code <= 404:
                return {"error": "City not found. Please check your input."}
            else:
                return {"error": f"HTTP error {e.code}. Please try again later."}

        except urllib.error.URLError as e:
            return {"error": "Connection Error. Check your internet connection."}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    def format_weather_data(self, data):
        temperature_k = data["main"]["temp"]
        temperature_c = temperature_k - 273.15
        temperature_f = temperature_c * 9 / 5 + 32
        weather_description = data["weather"][0]["description"]

        return {
            "temperature_celsius": f"{temperature_c:.0f}°C",
            "temperature_fahrenheit": f"{temperature_f:.0f}°F",
            "temperature_c_value": round(temperature_c),
            "temperature_f_value": round(temperature_f),
            "description": weather_description.title(),
            "city": data["name"],
            "country": data["sys"]["country"]
        }

    def format_forecast_data(self, data):
        forecasts = []
        daily_forecasts = {}

        # Group forecasts by day
        for item in data["list"]:
            date = datetime.fromtimestamp(item["dt"])
            day_key = date.strftime("%Y-%m-%d")

            if day_key not in daily_forecasts:
                daily_forecasts[day_key] = []

            daily_forecasts[day_key].append(item)

        # Process each day (limit to 7 days)
        for day_key in sorted(daily_forecasts.keys())[:7]:
            day_data = daily_forecasts[day_key]

            # Get temperatures for the day
            temps = [item["main"]["temp"] for item in day_data]
            max_temp_k = max(temps)
            min_temp_k = min(temps)

            # Convert to Celsius and Fahrenheit
            max_temp_c = max_temp_k - 273.15
            min_temp_c = min_temp_k - 273.15
            max_temp_f = max_temp_c * 9 / 5 + 32
            min_temp_f = min_temp_c * 9 / 5 + 32

            # Get most common weather description
            descriptions = [item["weather"][0]["description"] for item in day_data]
            most_common_desc = max(set(descriptions), key=descriptions.count)

            # Get weather icon
            icons = [item["weather"][0]["icon"] for item in day_data]
            most_common_icon = max(set(icons), key=icons.count)

            # Format date
            date_obj = datetime.strptime(day_key, "%Y-%m-%d")
            day_name = date_obj.strftime("%A")
            formatted_date = date_obj.strftime("%m/%d")

            forecasts.append({
                "date": formatted_date,
                "day": day_name,
                "max_temp_c": round(max_temp_c),
                "min_temp_c": round(min_temp_c),
                "max_temp_f": round(max_temp_f),
                "min_temp_f": round(min_temp_f),
                "description": most_common_desc.title(),
                "icon": most_common_icon
            })

        return {
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "forecasts": forecasts
        }


weather_service = WeatherService()


@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Calibri', Arial, sans-serif;
            background: linear-gradient(135deg, #74b9ff, #0984e3);
            min-height: 200vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
            backdrop-filter: blur(10px);
        }

        h1 {
            font-size: 60px;
            color: #2d3436;
            margin-bottom: 30px;
            font-weight: bold;
        }

        .controls {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 30px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .input-group {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        label {
            font-size: 18px;
            color: #636e72;
            margin-bottom: 10px;
            font-weight: 500;
        }

        input[type="text"] {
            padding: 12px 20px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 10px;
            text-align: center;
            outline: none;
            transition: all 0.3s ease;
            font-family: 'Calibri', Arial, sans-serif;
            width: 250px;
        }

        input[type="text"]:focus {
            border-color: #74b9ff;
            box-shadow: 0 0 15px rgba(116, 185, 255, 0.3);
        }

        .temperature-toggle {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .toggle-label {
            font-size: 16px;
            color: #636e72;
            font-weight: 500;
        }

        .toggle-switch {
            position: relative;
            width: 60px;
            height: 30px;
            background: #ddd;
            border-radius: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .toggle-switch.active {
            background: #74b9ff;
        }

        .toggle-slider {
            position: absolute;
            top: 3px;
            left: 3px;
            width: 24px;
            height: 24px;
            background: white;
            border-radius: 50%;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .toggle-switch.active .toggle-slider {
            transform: translateX(30px);
        }

        .button-group {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }

        button {
            background: linear-gradient(135deg, #00b894, #00a085);
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Calibri', Arial, sans-serif;
            min-width: 120px;
        }

        button:hover {
            background: linear-gradient(135deg, #00a085, #00b894);
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 184, 148, 0.3);
        }

        button:active {
            transform: translateY(0);
        }

        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .weather-result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 15px;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .weather-success {
            background: linear-gradient(135deg, #00b894, #00cec9);
            color: white;
        }

        .weather-error {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
        }

        .current-weather {
            margin-bottom: 20px;
        }

        .temperature {
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .temperature:hover {
            transform: scale(1.05);
        }

        .description {
            font-size: 24px;
            font-style: italic;
            opacity: 0.9;
        }

        .city-info {
            font-size: 18px;
            margin-top: 10px;
            opacity: 0.8;
        }

        .forecast-section {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.3);
        }

        .forecast-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
            color: white;
        }

        .forecast-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 15px;
            max-width: 1000px;
            margin: 0 auto;
        }

        .forecast-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }

        .forecast-item:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }

        .forecast-day {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 8px;
            color: white;
        }

        .forecast-date {
            font-size: 12px;
            opacity: 0.8;
            margin-bottom: 10px;
            color: white;
        }

        .forecast-icon {
            width: 40px;
            height: 40px;
            margin: 0 auto 10px;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
        }

        .forecast-temps {
            font-size: 14px;
            color: white;
            margin-bottom: 5px;
        }

        .forecast-desc {
            font-size: 12px;
            opacity: 0.9;
            color: white;
        }

        .error-message {
            font-size: 20px;
            font-weight: 500;
        }

        .loading {
            color: #74b9ff;
            font-size: 18px;
            margin-top: 20px;
        }

        @media (max-width: 700px) {
            .container {
                padding: 20px;
            }

            h1 {
                font-size: 40px;
            }

            .controls {
                flex-direction: column;
                gap: 20px;
            }

            .button-group {
                flex-direction: column;
                align-items: center;
            }

            .temperature {
                font-size: 36px;
            }

            .forecast-container {
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Weather App</h1>

        <div class="controls">
            <div class="input-group">
                <label for="cityInput">Enter city name:</label>
                <input type="text" id="cityInput" placeholder="e.g., London, New York" />
            </div>

            <div class="temperature-toggle">
                <span class="toggle-label">°F</span>
                <div class="toggle-switch" id="tempToggle" onclick="toggleTemperatureUnit()">
                    <div class="toggle-slider"></div>
                </div>
                <span class="toggle-label">°C</span>
            </div>
        </div>

        <div class="button-group">
            <button id="getWeatherBtn" onclick="getWeather()">Current Weather</button>
            <button id="getForecastBtn" onclick="getForecast()">7-Day Forecast</button>
        </div>

        <div id="loadingMessage" class="loading" style="display: none;">
            Getting weather data...
        </div>

        <div id="weatherResult" class="weather-result" style="display: none;"></div>
    </div>

    <script>
        const cityInput = document.getElementById('cityInput');
        const getWeatherBtn = document.getElementById('getWeatherBtn');
        const getForecastBtn = document.getElementById('getForecastBtn');
        const loadingMessage = document.getElementById('loadingMessage');
        const weatherResult = document.getElementById('weatherResult');
        const tempToggle = document.getElementById('tempToggle');

        let currentWeatherData = null;
        let currentForecastData = null;
        let isCelsius = false;

        // Allow Enter key to trigger weather fetch
        cityInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                getWeather();
            }
        });

        function toggleTemperatureUnit() {
            isCelsius = !isCelsius;
            tempToggle.classList.toggle('active', isCelsius);

            // Update display if data is available
            if (currentWeatherData) {
                showWeather(currentWeatherData);
            }
            if (currentForecastData) {
                showForecast(currentForecastData);
            }
        }

        async function getWeather() {
            const city = cityInput.value.trim();

            if (!city) {
                showError('Please enter a city name.');
                return;
            }

            // Show loading state
            getWeatherBtn.disabled = true;
            getForecastBtn.disabled = true;
            loadingMessage.style.display = 'block';
            weatherResult.style.display = 'none';

            try {
                const response = await fetch('/weather', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ city: city })
                });

                const data = await response.json();

                if (data.error) {
                    showError(data.error);
                } else {
                    currentWeatherData = data;
                    currentForecastData = null;
                    showWeather(data);
                }
            } catch (error) {
                showError('Failed to fetch weather data. Please try again.');
                console.error('Error:', error);
            } finally {
                // Hide loading state
                getWeatherBtn.disabled = false;
                getForecastBtn.disabled = false;
                loadingMessage.style.display = 'none';
            }
        }

        async function getForecast() {
            const city = cityInput.value.trim();

            if (!city) {
                showError('Please enter a city name.');
                return;
            }

            // Show loading state
            getWeatherBtn.disabled = true;
            getForecastBtn.disabled = true;
            loadingMessage.style.display = 'block';
            weatherResult.style.display = 'none';

            try {
                const response = await fetch('/forecast', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ city: city })
                });

                const data = await response.json();

                if (data.error) {
                    showError(data.error);
                } else {
                    currentForecastData = data;
                    currentWeatherData = null;
                    showForecast(data);
                }
            } catch (error) {
                showError('Failed to fetch forecast data. Please try again.');
                console.error('Error:', error);
            } finally {
                // Hide loading state
                getWeatherBtn.disabled = false;
                getForecastBtn.disabled = false;
                loadingMessage.style.display = 'none';
            }
        }

        function showWeather(data) {
            const primaryTemp = isCelsius ? data.temperature_celsius : data.temperature_fahrenheit;

            weatherResult.className = 'weather-result weather-success';
            weatherResult.innerHTML = `
                <div class="current-weather">
                    <div class="temperature" onclick="toggleTemperatureUnit()">${primaryTemp}</div>
                    <div class="description">${data.description}</div>
                    <div class="city-info">${data.city}, ${data.country}</div>
                </div>
            `;
            weatherResult.style.display = 'block';
        }

        function showForecast(data) {
            const forecastItems = data.forecasts.map(forecast => {
                const maxTemp = isCelsius ? `${forecast.max_temp_c}°C` : `${forecast.max_temp_f}°F`;
                const minTemp = isCelsius ? `${forecast.min_temp_c}°C` : `${forecast.min_temp_f}°F`;

                return `
                    <div class="forecast-item">
                        <div class="forecast-day">${forecast.day}</div>
                        <div class="forecast-date">${forecast.date}</div>
                        <div class="forecast-icon" style="background-image: url('https://openweathermap.org/img/wn/${forecast.icon}@2x.png')"></div>
                        <div class="forecast-temps">${maxTemp} / ${minTemp}</div>
                        <div class="forecast-desc">${forecast.description}</div>
                    </div>
                `;
            }).join('');

            weatherResult.className = 'weather-result weather-success';
            weatherResult.innerHTML = `
                <div class="city-info" style="margin-bottom: 20px;">${data.city}, ${data.country}</div>
                <div class="forecast-section">
                    <div class="forecast-title">7-Day Forecast</div>
                    <div class="forecast-container">
                        ${forecastItems}
                    </div>
                </div>
            `;
            weatherResult.style.display = 'block';
        }

        function showError(message) {
            currentWeatherData = null;
            currentForecastData = null;
            weatherResult.className = 'weather-result weather-error';
            weatherResult.innerHTML = `
                <div class="error-message">${message}</div>
            `;
            weatherResult.style.display = 'block';
        }
    </script>
</body>
</html>
    '''


@app.route('/weather', methods=['POST'])
def get_weather():
    city = request.json.get('city', '').strip()
    print(city)
    city = urllib.parse.quote(city)
    print(city)

    if not city:
        return jsonify({"error": "Please enter a city name."})

    result = weather_service.get_weather(city)
    return jsonify(result)


@app.route('/forecast', methods=['POST'])
def get_forecast():
    city = request.json.get('city', '').strip()
    print(city)
    city = urllib.parse.quote(city)
    print(city)

    if not city:
        return jsonify({"error": "Please enter a city name."})

    result = weather_service.get_forecast(city)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
