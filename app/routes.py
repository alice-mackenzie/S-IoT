from flask import Blueprint, render_template, jsonify
import pandas as pd
from datetime import datetime, timedelta
import os
import subprocess

# Define the blueprint
main = Blueprint("main", __name__)

# Helper function to get the full path to data files
def get_data_file_path(filename):
    """Helper function to construct path to data files"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'data', filename)

# Define the main index route
@main.route("/")
def index():
    # Load weather data
    weather_file = get_data_file_path('weather_data_log.csv')  # Adjusted path
    df = pd.read_csv(weather_file)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Get the last 7 days of data
    week_ago = datetime.now() - timedelta(days=7)
    df = df[df['Timestamp'] >= week_ago]

    # Prepare data for the template
    weather_data = df.to_dict('records')
    for record in weather_data:
        record['Timestamp'] = record['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')

    # Render the index.html template
    return render_template("index.html", weather_data=weather_data)

# Define the API route for hourly weather data
@main.route("/api/weather/hourly")
def api_weather_hourly():
    # Load weather data
    weather_file = get_data_file_path('weather_data_log.csv')  # Adjusted path
    df = pd.read_csv(weather_file)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Get the last 7 days of data
    week_ago = datetime.now() - timedelta(days=7)
    df = df[df['Timestamp'] >= week_ago]

    # Return the data as JSON
    return jsonify({
        "status": "success",
        "data": df.to_dict('records')
    })

@main.route("/api/moths/monthly")
def api_moths_monthly():
    # Load moth data
    moth_file = get_data_file_path('moth_measurements.csv')
    df = pd.read_csv(moth_file)
    df['date'] = pd.to_datetime(df['date'])  # Convert date column to datetime

    # Filter data for the past month
    one_month_ago = datetime.now() - timedelta(days=30)
    df = df[df['date'] >= one_month_ago]

    # Group by day and calculate size categories
    grouped = df.groupby(df['date'].dt.date).agg(
        mini_moths=('length_mm', lambda x: (x < 25).sum()),
        medium_moths=('length_mm', lambda x: ((x >= 25) & (x <= 45)).sum()),
        large_moths=('length_mm', lambda x: (x > 45).sum())
    ).reset_index()

    # Return JSON data
    return {
        "status": "success",
        "data": grouped.to_dict(orient='records')
    }

@main.route("/api/moon/monthly")
def api_moon_monthly():
    # Load moon data
    moon_file = get_data_file_path('day-moon-light.csv')
    df = pd.read_csv(moon_file)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter data for the past month
    one_month_ago = datetime.now() - timedelta(days=30)
    df = df[df['Date'] >= one_month_ago]
    
    # Keep only the date and moon phase columns
    result = df[['Date', 'Moon Phase (%)']].copy()
    result['Date'] = result['Date'].dt.date
    
    # Remove duplicates keeping the first entry for each date
    result = result.drop_duplicates(subset=['Date'], keep='first')
    
    return jsonify({
        "status": "success",
        "data": result.to_dict(orient='records')
    })


@main.route("/api/moths/daily")
def api_moths_daily():
    # Load moth measurement data only
    measurements_file = get_data_file_path('moth_measurements.csv')
    df = pd.read_csv(measurements_file)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    
    # Add time of day classification (morning = before noon)
    df['is_morning'] = df['timestamp'].dt.hour < 12
    
    # Calculate size categories based on length_mm
    df['size_category'] = pd.cut(
        df['length_mm'],
        bins=[0, 25, 45, float('inf')],
        labels=['mini', 'medium', 'large']
    )
    
    # Group by date and time of day, count moths in each size category
    result = []
    for date, group in df.groupby('date'):
        # Get morning counts
        morning_group = group[group['is_morning']]
        morning_counts = morning_group['size_category'].value_counts()
        
        # Get afternoon counts
        afternoon_group = group[~group['is_morning']]
        afternoon_counts = afternoon_group['size_category'].value_counts()
        
        entry = {
            'date': date.strftime('%Y-%m-%d'),
            'morning': {
                'mini': int(morning_counts.get('mini', 0)),
                'medium': int(morning_counts.get('medium', 0)),
                'large': int(morning_counts.get('large', 0))
            },
            'afternoon': {
                'mini': int(afternoon_counts.get('mini', 0)),
                'medium': int(afternoon_counts.get('medium', 0)),
                'large': int(afternoon_counts.get('large', 0))
            }
        }
        result.append(entry)
    
    # Sort by date
    result.sort(key=lambda x: x['date'])
    
    return jsonify({
        "status": "success",
        "data": result
    })


@main.route("/api/weather/daily")
def api_weather_daily():
    weather_file = get_data_file_path('weather_data_log.csv')
    df = pd.read_csv(weather_file)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Calculate daily averages
    daily = df.groupby(df['Timestamp'].dt.date).agg({
        'Temperature': 'mean',
        'Humidity': 'mean',
        'Cloud_Cover': 'mean'
    }).round(2)
    
    # Convert to records
    result = []
    for date, row in daily.iterrows():
        result.append({
            'date': date.strftime('%Y-%m-%d'),
            'temperature': float(row['Temperature']),
            'humidity': float(row['Humidity']),
            'cloudCover': float(row['Cloud_Cover'])
        })
    
    return jsonify({
        "status": "success",
        "data": result
    })




@main.route("/api/moths/departures")
def api_moths_departures():
    # Load departure data and weather data
    departures_file = get_data_file_path('moth_departures.csv')
    weather_file = get_data_file_path('weather_data_log.csv')
    
    df_departures = pd.read_csv(departures_file)
    df_weather = pd.read_csv(weather_file)
    
    # Fix datetime parsing by handling 24-hour format correctly
    def parse_datetime(row):
        try:
            # Extract hour and minute from image filename
            time_parts = row['image_name'].split('.')[0].split('-')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            # Adjust hour for PM times (after 12)
            if hour > 23:  # For times like 15:55, convert to 03:55 PM
                hour = hour - 12
                
            # Create datetime with the adjusted hour
            return pd.to_datetime(f"{row['date']} {hour:02d}:{minute:02d}:00")
        except Exception as e:
            print(f"Error parsing datetime for row: {row}, Error: {e}")
            return pd.NaT
    
    # Apply the datetime parsing
    df_departures['datetime'] = df_departures.apply(parse_datetime, axis=1)
    
    # Remove rows with invalid datetimes
    df_departures = df_departures.dropna(subset=['datetime'])
    
    # Convert weather timestamps
    df_weather['Timestamp'] = pd.to_datetime(df_weather['Timestamp'])
    
    # Function to find closest temperature reading
    def get_closest_temp(departure_time):
        if pd.isna(departure_time):
            return None
        time_diff = abs(df_weather['Timestamp'] - departure_time)
        closest_idx = time_diff.idxmin()
        return df_weather.loc[closest_idx, 'Temperature']
    
    # Add temperature data to departures
    df_departures['temperature'] = df_departures['datetime'].apply(get_closest_temp)
    
    # Create time-based distribution
    time_dist = df_departures.groupby('time_since_red_minutes')['moths_departed'].sum().reset_index()
    
    # Temperature analysis with error handling
    try:
        # Create temperature bins
        temp_min = df_departures['temperature'].min()
        temp_max = df_departures['temperature'].max()
        bins = np.linspace(temp_min, temp_max, num=11)  # 10 bins
        labels = [f"{bins[i]:.1f}-{bins[i+1]:.1f}°C" for i in range(len(bins)-1)]
        
        df_departures['temp_bin'] = pd.cut(df_departures['temperature'], 
                                         bins=bins, 
                                         labels=labels, 
                                         include_lowest=True)
        
        # Aggregate by temperature bins
        temp_analysis = (df_departures.groupby('temp_bin', observed=True)
                        .agg({
                            'time_since_red_minutes': lambda x: np.average(x, weights=df_departures.loc[x.index, 'moths_departed']),
                            'moths_departed': 'sum'
                        })
                        .reset_index()
                        .dropna())
        
    except Exception as e:
        print(f"Error in temperature analysis: {e}")
        # Provide simplified temperature analysis if the detailed one fails
        temp_analysis = pd.DataFrame({
            'temp_bin': ['All'],
            'time_since_red_minutes': [df_departures['time_since_red_minutes'].mean()],
            'moths_departed': [df_departures['moths_departed'].sum()]
        })
    
    # Calculate summary statistics
    stats = {
        'total_moths': int(df_departures['moths_departed'].sum()),
        'avg_departure_time': float(np.average(
            df_departures['time_since_red_minutes'],
            weights=df_departures['moths_departed']
        )),
        'temp_correlation': float(df_departures['time_since_red_minutes'].corr(
            df_departures['temperature'],
            method='spearman'
        ))
    }
    
    return jsonify({
        "status": "success",
        "data": {
            "time_distribution": {
                "times": time_dist['time_since_red_minutes'].tolist(),
                "counts": time_dist['moths_departed'].tolist()
            },
            "temperature_analysis": {
                "ranges": temp_analysis['temp_bin'].tolist(),
                "avg_times": temp_analysis['time_since_red_minutes'].tolist(),
                "counts": temp_analysis['moths_departed'].tolist()
            },
            "stats": stats
        }
    })

@main.route("/api/lights/warm")
def warm_light():
    try:
        # Use sudo to run the script
        result = subprocess.run(
            ['sudo', 'python3', os.path.join('light', 'warm_white.py')],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return jsonify({"status": "success", "message": "Warm light activated"})
        else:
            return jsonify({"status": "error", "message": f"Error: {result.stderr}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@main.route("/api/lights/off")
def turn_off_light():
    try:
        result = subprocess.run(
            ['sudo', 'python3', os.path.join('light', 'turn_off.py')],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return jsonify({"status": "success", "message": "Lights turned off"})
        else:
            return jsonify({"status": "error", "message": f"Error: {result.stderr}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
