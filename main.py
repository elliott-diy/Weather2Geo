import csv
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from math import radians, sin, cos, sqrt, atan2
import typer
from rich import print
from rich.console import Console
from rich.panel import Panel

app = typer.Typer()
console = Console()

API_KEY = "UhJ4G66OjyLbn9mXARgajXLiLw6V75sHnfpU60aJBB"
WEATHER_API_URL = "https://api.msn.com/weather/overview"


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))


def cluster_locations(locations, max_distance_km=10):
    clusters = []
    for loc in locations:
        added = False
        for cluster in clusters:
            for member in cluster:
                d = haversine(loc['latitude'], loc['longitude'], member['latitude'], member['longitude'])
                if d <= max_distance_km:
                    cluster.append(loc)
                    added = True
                    break
            if added:
                break
        if not added:
            clusters.append([loc])
    return clusters


def fetch_weather(loc, desired_cap, desired_temp, temp_tolerance):
    try:
        params = {
            "apikey": API_KEY,
            "lat": loc['latitude'],
            "lon": loc['longitude'],
            "units": "C"
        }
        r = requests.get(WEATHER_API_URL, params=params, timeout=5)
        if r.status_code != 200:
            loc['status'] = f"Error {r.status_code}"
            return None
        data = r.json()
        current = data['value'][0]['responses'][0]['weather'][0]['current']
        cap = current.get('cap', '').strip().lower()
        temp = current.get('temp')
        loc['cap'] = cap
        loc['temp'] = temp
        loc['status'] = "OK"

        console.print(f"[cyan]Checking[/cyan] [bold]{loc['location']}[/bold] — [green]{cap}[/green], [yellow]{temp}°C[/yellow]")

        if cap == desired_cap and (desired_temp is None or abs(float(temp) - desired_temp) <= temp_tolerance):
            return loc
    except Exception as e:
        loc['status'] = f"Failed: {e}"
    return None


@app.command()
def run(
    time: str = typer.Option(..., help="Target date/time in format YYYY-MM-DD HH:MM (interpreted in your local timezone)"),
    condition: str = typer.Option(..., help="Desired weather condition (e.g. 'Mostly cloudy')"),
    temp: float = typer.Option(..., help="Target temperature in Celsius"),
    tolerance: float = typer.Option(1.0, help="Temperature tolerance (default: 1.0)"),
    cluster_distance: int = typer.Option(15, help="Clustering distance in KM (default: 25)"),
    cities_file: str = typer.Option("cities15000.txt", help="Path to cities data file")
):
    # Restore original behavior: assume user input is in local system time
    input_dt = datetime.strptime(time, "%Y-%m-%d %H:%M")

    desired_cap = condition.strip().lower()
    desired_temp = temp
    tf = TimezoneFinder()
    locations = []

    with open(cities_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        for i, row in enumerate(reader):
            if len(row) < 18:
                continue
            try:
                if row[6] != 'P':
                    continue
                location = row[1].strip()
                latitude = float(row[4].strip())
                longitude = float(row[5].strip())
                timezone_str = row[17].strip()

                tz = pytz.timezone(timezone_str)
                target_hour = input_dt.hour
                tz_now = datetime.now(tz)
                if tz_now.hour == target_hour:
                    locations.append({
                        'location': location,
                        'latitude': latitude,
                        'longitude': longitude,
                        'timezone': timezone_str,
                    })
            except Exception:
                continue

    console.print(Panel.fit(f"[bold]Checking {len(locations)} candidate locations...[/bold]", style="blue"))

    if len(locations) > 2000:
        console.print("[yellow]Warning: More than 2000 locations found. This may take a while and will use a lot of API calls.[/yellow]")
        input("Press Enter to continue or Ctrl+C to cancel...")

    matches = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(fetch_weather, loc, desired_cap, desired_temp, tolerance) for loc in locations]
        for future in as_completed(futures):
            result = future.result()
            if result:
                matches.append(result)

    console.print(Panel.fit(f"[bold green]\nFound {len(matches)} matching locations[/bold green]", style="green"))
    clusters = cluster_locations(matches, max_distance_km=cluster_distance)
    clusters = sorted(clusters, key=lambda c: len(c), reverse=True)

    for i, cluster in enumerate(clusters, start=1):
        console.print(f"\n[bold magenta]Cluster {i}[/bold magenta] — [cyan]{len(cluster)}[/cyan] locations:")
        for loc in cluster:
            console.print(f"[dim]-[/dim] [bold]{loc['location']}[/bold] — [yellow]{loc['temp']}°C[/yellow], [green]{loc['cap']}[/green]")


if __name__ == "__main__":
    console.print("[bold blue]OSINT-style Weather Matcher[/bold blue]")
    app()