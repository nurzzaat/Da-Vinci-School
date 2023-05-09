from flask import redirect, render_template, session , jsonify
from functools import wraps
from math import sin, cos, acos , radians
import requests


def apology(message, code):
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def lookup(name):

    try:
        api_url = 'https://api.api-ninjas.com/v1/city?name={}'.format(name)
        response = requests.get(api_url, headers={'X-Api-Key': 'XiovoJfX7wJisf/EUP/sYQ==unJr5BgvaVG2I8v1'})
        response.raise_for_status()
    except requests.RequestException:
        return None

    try:
        city = response.json()
        return {
            'latitude': city[0]['latitude'],
            'longitude': city[0]['longitude']
        }
    except (KeyError, TypeError, ValueError , IndexError):
        return None

# Function to calculate distance between two cities
def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert coordinates from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calculate distance using haversine formula
    distance = acos(sin(lat1)*sin(lat2) + cos(lat1)*cos(lat2)*cos(lon2-lon1)) * 6371
    return distance
