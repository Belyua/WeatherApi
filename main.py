import datetime
import argparse
import sqlite3
import requests
import csv

from config import api_key


conn = sqlite3.connect('weather.db')
cursor = conn.cursor()


def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_table (
            date text,
            location text,
            weather text,
            temperature real
        )
    ''')


def get_weather(date, location):
    init_db()
    # Connect to the database
    # Check if the weather information is in the database
    cursor.execute('''
        SELECT weather, temperature FROM weather_table
        WHERE date = ? AND location = ?
    ''', (str(date), location))
    result = cursor.fetchone()
    if result is not None:
        return result

    weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}'
    response = requests.get(weather_url)
    response.raise_for_status()
    weather = response.json()['weather'][0]['description']
    temperature = response.json()['main']['temp'] - 273.15

    # Store the weather information in the database
    cursor.execute('''
        INSERT INTO weather_table (date, location, weather, temperature)
        VALUES (?, ?, ?, ?)
    ''', (str(date), location, weather, int(temperature)))
    conn.commit()

    return temperature, weather


def main(date, location, output_file=None):
    weather, temperature = get_weather(date, location)

    if output_file is None:
        print(f'date: {date}\n'
              f'temperature: {temperature}°C\n'
              f'precipitation: {weather}\n'
              f'location: {location}')
    else:
        # im also can add 'a' instead of 'w' if the user wants to update an existing file
        with open(f'{output_file}.csv', 'w', encoding='utf-8') as f:
            # create the csv writer
            writer = csv.writer(f)

            # write a row to the csv file
            writer.writerow([date, location, int(temperature), weather])


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date', type=str, help='Date (YYYY-MM-DD)')
    parser.add_argument('-l', '--location', type=str, help='Location')
    parser.add_argument('-o', '--output', type=str, help='Output file')

    args = parser.parse_args()

    date = None
    if args.date is not None:
        date = datetime.datetime.strptime(args.date, '%Y-%m-%d').date()
    else:
        date = datetime.datetime.today().date()

    location = args.location or 'Wrocław'
    output_file = args.output

    main(date, location, output_file)



